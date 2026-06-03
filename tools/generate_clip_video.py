#!/usr/bin/env python3
"""LE BUZZER — Génère un clip vertical 1080x1920 à partir d'un segment.

Pipeline: TTS (OpenAI 'ash') -> Whisper word-level -> sous-titres karaoke .ass
-> ffmpeg (fond marque + waveform jaune + logo LE BUZZER + sous-titres + outro CTA).

Usage: python tools/generate_clip_video.py <YYYY-MM-DD> <rank>
Env  : OPENAI_API_KEY (via BUZZER_ENV / .env). Fallback sous-titres par chunk si Whisper échoue.
"""
import os, sys, re, json, subprocess, urllib.request, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RED="0xE63946"; YELLOW="0xFFD60A"; CREAM="0xF1FAEE"; BLACK="0x0D0D0D"
FONT="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
ANTON=os.path.join(ROOT,"tools","assets","Anton.ttf")
if not os.path.exists(ANTON): ANTON=FONT
OSWALD=os.path.join(ROOT,"tools","assets","Oswald.ttf")
W,H=1080,1920

def load_env():
    if os.environ.get("OPENAI_API_KEY"): return
    for c in [os.environ.get("BUZZER_ENV",""), os.path.join(ROOT,".env"), os.path.join(ROOT,"..","Podcast",".env")]:
        if c and os.path.isfile(c):
            for line in open(c,encoding="utf-8"):
                line=line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k,_,v=line.partition("="); v=v.strip().strip('"').strip("'")
                    if k.strip() and k.strip() not in os.environ: os.environ[k.strip()]=v
            if os.environ.get("OPENAI_API_KEY"): return

def tts(text, out_mp3):
    body=json.dumps({"model":"gpt-4o-mini-tts","voice":"ash","input":text,"response_format":"mp3"}).encode()
    req=urllib.request.Request("https://api.openai.com/v1/audio/speech", data=body, headers={
        "Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=180) as r, open(out_mp3,"wb") as f:
        f.write(r.read())
    print(f"[tts] {out_mp3} ({os.path.getsize(out_mp3)} bytes)")

def whisper_words(mp3):
    boundary="----lebuzzer"+os.urandom(8).hex()
    parts=[]
    def field(name,val):
        parts.append(("--"+boundary+"\r\nContent-Disposition: form-data; name=\""+name+"\"\r\n\r\n"+val+"\r\n").encode())
    field("model","whisper-1"); field("response_format","verbose_json"); field("language","fr")
    field("timestamp_granularities[]","word")
    data=open(mp3,"rb").read()
    parts.append(("--"+boundary+"\r\nContent-Disposition: form-data; name=\"file\"; filename=\"clip.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n").encode())
    parts.append(data); parts.append(("\r\n--"+boundary+"--\r\n").encode())
    payload=b"".join(parts)
    req=urllib.request.Request("https://api.openai.com/v1/audio/transcriptions", data=payload, headers={
        "Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],
        "Content-Type":"multipart/form-data; boundary="+boundary})
    with urllib.request.urlopen(req,timeout=180) as r:
        j=json.loads(r.read())
    return j.get("words",[]), j.get("duration")

def dur_of(mp3):
    out=subprocess.check_output(["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",mp3])
    return float(out.strip())

def ass_time(t):
    h=int(t//3600); m=int((t%3600)//60); s=t%60
    return f"{h:d}:{m:02d}:{s:05.2f}"

def esc(s): return s.replace("\\","\\\\").replace("{","(").replace("}",")")

def build_ass(words, total, path):
    # style: gros, centré bas-milieu, contour épais. Mot actif en jaune.
    head=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,Poppins,96,&H00F1FAEE,&H00141414,&H64000000,1,1,7,3,5,90,90,0,1

[Events]
Format: Layer, Start, End, Style, MarginL, MarginR, MarginV, Effect, Text
"""
    lines=[head]
    YEL="&H000AD6FF"  # #FFD60A en BBGGRR
    WHT="&H00F1FAEE"
    if words:
        # groupe en lignes de <=5 mots
        groups=[]; cur=[]
        for w in words:
            cur.append(w)
            if len(cur)>=5: groups.append(cur); cur=[]
        if cur: groups.append(cur)
        for g in groups:
            for i,w in enumerate(g):
                st=float(w["start"]); en=float(w["end"])
                txt=""
                for j,ww in enumerate(g):
                    word=esc(ww["word"]).strip()
                    if j==i: txt+="{\\c"+YEL+"\\fscx112\\fscy112}"+word+"{\\c"+WHT+"\\fscx100\\fscy100} "
                    else: txt+="{\\c"+WHT+"}"+word+" "
                lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Base,,0,0,0,,{txt.strip()}")
    else:
        # fallback: aucun timing -> rien (les sous-titres seront omis)
        pass
    open(path,"w",encoding="utf-8").write("\n".join(lines))
    return path

def main():
    load_env()
    if not os.environ.get("OPENAI_API_KEY"): sys.exit("OPENAI_API_KEY manquante.")
    date=sys.argv[1]; rank=int(sys.argv[2])
    clips=json.load(open(os.path.join(ROOT,"output","clips",date+"_clips.json"),encoding="utf-8"))["clips"]
    clip=next(c for c in clips if int(c.get("rank"))==rank)
    seg=clip["segment_text"]; hook=clip.get("hook_text","")
    base=os.path.join(ROOT,"output","clips",f"{date}_clip_{rank}")
    mp3=base+".mp3"; ass=base+".ass"; mp4=base+".mp4"

    if os.path.exists(mp3) and os.path.getsize(mp3)>1000:
        print('[tts] cache:', mp3)
    else:
        tts(seg, mp3)
    wcache=base+"_words.json"
    if os.path.exists(wcache):
        words=json.load(open(wcache,encoding="utf-8")); print(f"[whisper] cache {len(words)} mots")
    else:
        try:
            words,wdur=whisper_words(mp3); print(f"[whisper] {len(words)} mots")
            json.dump(words, open(wcache,"w",encoding="utf-8"), ensure_ascii=False)
        except Exception as e:
            print("[whisper] échec, fallback sans karaoke:", e); words=[]
    total=dur_of(mp3); print(f"[dur] {total:.1f}s")
    build_ass(words, total, ass)

    logo="LE BUZZER"
    outro="lebuzzer.com"
    barY=360
    # filtres
    vf=(
        f"[1:a]showwaves=s=1000x420:mode=cline:colors={YELLOW}:draw=full:rate=25,format=yuva420p,colorkey=0x000000:0.01:0.0[wv];"
        f"[0:v][wv]overlay=(W-w)/2:(H-h)/2-40[bg];"
        # barre jaune sous logo
        f"[bg]drawbox=x=(iw-360)/2:y={barY}:w=360:h=14:color={YELLOW}:t=fill[bx];"
        # logo
        f"[bx]drawtext=fontfile={ANTON}:text='{logo}':fontcolor={CREAM}:fontsize=104:x=(w-text_w)/2:y=235[lg];"
        # bandeau thème en haut
        f"[lg]drawtext=fontfile={ANTON}:text='{esc(clip.get('theme','SPORT')).upper()} • LE BRIEF':fontcolor={YELLOW}:fontsize=40:x=(w-text_w)/2:y=160[hd];"
        # outro CTA derniers 3s
        f"[hd]drawbox=x=0:y=ih-360:w=iw:h=200:color={RED}:t=fill:enable='gte(t,{max(0,total-3):.2f})'[ob];"
        f"[ob]drawtext=fontfile={FONT}:text='{outro}':fontcolor={CREAM}:fontsize=84:x=(w-text_w)/2:y=h-300:enable='gte(t,{max(0,total-3):.2f})'[oc];"
        f"[oc]subtitles={ass}:fontsdir=/usr/share/fonts[v]"
    )
    cmd=["ffmpeg","-y",
         "-f","lavfi","-i",f"color=c={BLACK}:s={W}x{H}:d={total:.2f}:r=25",
         "-i",mp3,
         "-filter_complex",vf,
         "-map","[v]","-map","1:a",
         "-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast","-crf","20",
         "-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart", mp4]
    print("[ffmpeg] composing...")
    r=subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode!=0:
        print(r.stderr[-3000:]); sys.exit("ffmpeg a échoué")
    print(f"[done] {mp4} ({os.path.getsize(mp4)} bytes)")

if __name__=="__main__":
    main()
