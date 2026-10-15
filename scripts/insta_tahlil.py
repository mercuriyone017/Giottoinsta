#!/usr/bin/env python3
"""Instagram post/reel ni tahlilga tayyorlaydi.

Natija papkasida:
  meta.json          - muallif, sana, ko'rishlar, like, izohlar, davomiylik
  caption.txt        - post matni
  kadrlar/           - asosiy kadrlar (birinchi 3 soniya zichroq, hook uchun)
  kadrlar_jadval.jpg - barcha kadrlar bitta rasmda (tez ko'rish uchun)
  transkript.txt     - nutq matni vaqt belgilari bilan (agar ovoz bo'lsa)
  rasmlar/           - karusel/rasmli post bo'lsa, rasmlar

Ishlatish:
  python3 scripts/insta_tahlil.py <instagram-link>
  python3 scripts/insta_tahlil.py --fayl video.mp4      # telefondan yuklangan video
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XOM = os.path.join(ROOT, "goyalar", "_xom")
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "medium")


def log(msg):
    print(f"[insta] {msg}", file=sys.stderr, flush=True)


def ensure(module, package=None):
    try:
        __import__(module)
    except ImportError:
        log(f"{package or module} o'rnatilmoqda...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", package or module],
            check=True,
        )


def post_id(url):
    m = re.search(r"instagram\.com/(?:[^/]+/)?(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else re.sub(r"\W+", "_", url)[-40:]


def cookies_file():
    """INSTAGRAM_COOKIES muhit o'zgaruvchisi: cookies.txt mazmuni yoki fayl yo'li."""
    val = os.environ.get("INSTAGRAM_COOKIES", "").strip()
    if not val:
        return None
    if os.path.isfile(val):
        return val
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    f.write(val if val.startswith("# Netscape") else "# Netscape HTTP Cookie File\n" + val)
    f.close()
    return f.name


def ytdlp_download(url, out):
    ensure("yt_dlp", "yt-dlp")
    cmd = [
        sys.executable, "-m", "yt_dlp", url,
        "-o", os.path.join(out, "video.%(ext)s"),
        "--write-info-json", "--no-playlist", "--no-progress",
        "-f", "best[ext=mp4]/best",
    ]
    ck = cookies_file()
    if ck:
        cmd += ["--cookies", ck]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return False, r.stderr.strip()[-1500:]
    return True, ""


def gallerydl_download(url, out):
    """Rasmli/karusel postlar uchun zaxira yo'l."""
    ensure("gallery_dl", "gallery-dl")
    rasmlar = os.path.join(out, "rasmlar")
    os.makedirs(rasmlar, exist_ok=True)
    cmd = [sys.executable, "-m", "gallery_dl", "-D", rasmlar, "--write-metadata", url]
    ck = cookies_file()
    if ck:
        cmd += ["--cookies", ck]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.listdir(rasmlar):
        return False, r.stderr.strip()[-1500:]
    # gallery-dl metadata dan caption ni olamiz
    for mf in sorted(glob.glob(os.path.join(rasmlar, "*.json"))):
        with open(mf) as fh:
            d = json.load(fh)
        write_meta(out, {
            "uploader": d.get("username") or d.get("owner", {}).get("username"),
            "description": d.get("description"),
            "upload_date": str(d.get("date", ""))[:10],
            "like_count": d.get("likes"),
            "webpage_url": url,
        })
        break
    return True, ""


def write_meta(out, info):
    keep = ["title", "description", "uploader", "uploader_id", "channel", "upload_date",
            "duration", "view_count", "like_count", "comment_count", "webpage_url"]
    meta = {k: info.get(k) for k in keep if info.get(k) is not None}
    with open(os.path.join(out, "meta.json"), "w") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(out, "caption.txt"), "w") as fh:
        fh.write(meta.get("description") or "")
    return meta


def probe(video):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
         "-of", "json", video], capture_output=True, text=True)
    d = json.loads(r.stdout or "{}")
    dur = float(d.get("format", {}).get("duration") or 0)
    has_audio = any(s.get("codec_type") == "audio" for s in d.get("streams", []))
    return dur, has_audio


def extract_frames(video, out, dur):
    kd = os.path.join(out, "kadrlar")
    os.makedirs(kd, exist_ok=True)
    # Hook uchun birinchi 3 soniya har soniyada, keyin videoning qolgan qismidan ~10 ta kadr
    times = [t for t in (0.3, 1, 2, 3) if t < dur]
    if dur > 4:
        step = max(1.0, (dur - 4) / 10)
        t = 4.0
        while t < dur - 0.3:
            times.append(round(t, 1))
            t += step
    paths = []
    for t in times:
        p = os.path.join(kd, f"kadr_{int(t // 60):02d}m{t % 60:04.1f}s.jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", video,
                        "-frames:v", "1", "-vf", "scale=540:-2", "-q:v", "4", p], check=False)
        if os.path.exists(p):
            paths.append(p)
    if paths:
        cols = 4
        rows = (len(paths) + cols - 1) // cols
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i",
                        os.path.join(kd, "kadr_*.jpg"), "-vf",
                        f"scale=270:-2,tile={cols}x{rows}:padding=4:color=white",
                        "-frames:v", "1", os.path.join(out, "kadrlar_jadval.jpg")], check=False)
    return paths


def transcribe(video, out):
    wav = os.path.join(out, "audio.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-ac", "1", "-ar", "16000", wav], check=True)
    try:
        ensure("faster_whisper", "faster-whisper")
        from faster_whisper import WhisperModel
        model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        segments, info = model.transcribe(wav, vad_filter=True)
        lines = [f"# til: {info.language} ({info.language_probability:.0%})"]
        for s in segments:
            lines.append(f"[{int(s.start // 60):02d}:{int(s.start % 60):02d}] {s.text.strip()}")
        text = "\n".join(lines)
    except Exception as e:  # model yuklanmasa ham qolgan tahlil davom etadi
        text = f"# transkript olinmadi: {type(e).__name__}: {str(e)[:300]}"
    finally:
        if os.path.exists(wav):
            os.remove(wav)
    with open(os.path.join(out, "transkript.txt"), "w") as fh:
        fh.write(text + "\n")
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?")
    ap.add_argument("--fayl", help="Lokal video fayl (link o'rniga)")
    a = ap.parse_args()
    if not a.url and not a.fayl:
        ap.error("link yoki --fayl kerak")

    pid = post_id(a.url) if a.url else os.path.splitext(os.path.basename(a.fayl))[0]
    out = os.path.join(XOM, pid)
    os.makedirs(out, exist_ok=True)
    natija = {"papka": out, "id": pid}

    if a.fayl:
        video = os.path.join(out, "video" + os.path.splitext(a.fayl)[1])
        shutil.copy(a.fayl, video)
        write_meta(out, {"title": os.path.basename(a.fayl)})
    else:
        ok, err = ytdlp_download(a.url, out)
        if not ok:
            log("yt-dlp video topmadi, rasmli post sifatida urinib ko'rilmoqda...")
            ok2, err2 = gallerydl_download(a.url, out)
            if not ok2:
                shutil.rmtree(out, ignore_errors=True)
                natija["xato"] = err or err2
                print(json.dumps(natija, ensure_ascii=False, indent=2))
                sys.exit(2)
        infos = glob.glob(os.path.join(out, "video*.info.json"))
        if infos:
            with open(infos[0]) as fh:
                write_meta(out, json.load(fh))
            os.remove(infos[0])
        videos = [v for v in glob.glob(os.path.join(out, "video.*")) if not v.endswith(".json")]
        video = videos[0] if videos else None

    if video:
        dur, has_audio = probe(video)
        natija["davomiylik_s"] = round(dur, 1)
        natija["kadrlar"] = len(extract_frames(video, out, dur))
        if has_audio:
            log(f"nutq matnga o'girilmoqda (model: {WHISPER_MODEL})...")
            natija["transkript_boshi"] = transcribe(video, out)[:300]
        os.remove(video)  # video katta, repoga kerak emas
    natija["fayllar"] = sorted(os.listdir(out))
    print(json.dumps(natija, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
