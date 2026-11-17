"""Korean lecture transcription with faster-whisper.

Writes one <name>.txt per input with lines "[HH:MM:SS - HH:MM:SS] text".
Default model is large-v3 (accuracy first). Faster models need the user's consent.

Usage:
  python transcribe.py 녹음파일/*.m4a --outdir transcripts
  python transcribe.py a.m4a --outdir sample --max-seconds 300      # 5-minute check
  python transcribe.py ... --prompt "과목명. 용어1, 용어2"           # optional term hint
"""
import argparse
import os
import sys
import time

from faster_whisper import WhisperModel, decode_audio


def ts(sec):
    sec = int(sec)
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--prompt", default=None, help="initial_prompt term hint (may leak into text)")
    ap.add_argument("--max-seconds", type=float, default=0)
    ap.add_argument("--suffix", default="")
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--threads", type=int, default=os.cpu_count() or 8)
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    # Keep the PC awake while this process runs (released automatically on exit).
    if os.name == "nt":
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    model = WhisperModel(a.model, device="cpu", compute_type="int8", cpu_threads=a.threads)

    with open(os.path.join(a.outdir, "_설정.txt"), "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M')} model={a.model} language=ko beam_size=5 "
                f"vad_filter=True condition_on_previous_text=False prompt={a.prompt!r} "
                f"max_seconds={a.max_seconds or 'full'}\n")

    import av
    durs = {}
    for p in a.inputs:
        with av.open(p) as c:
            durs[p] = c.duration / 1e6
            if a.max_seconds:
                durs[p] = min(durs[p], a.max_seconds)
    left = sum(durs.values())
    done_audio = done_time = 0.0

    for i, path in enumerate(a.inputs, 1):
        name = os.path.splitext(os.path.basename(path))[0]
        out = os.path.join(a.outdir, name + a.suffix + ".txt")
        if a.skip_existing and os.path.exists(out):
            left -= durs[path]
            print(f"skip [{i}/{len(a.inputs)}] {name}", flush=True)
            continue
        audio = decode_audio(path, sampling_rate=16000)
        if a.max_seconds:
            audio = audio[: int(a.max_seconds * 16000)]
        dur = len(audio) / 16000
        t0 = time.time()
        segments, _ = model.transcribe(
            audio, language="ko", beam_size=5, vad_filter=True,
            condition_on_previous_text=False, initial_prompt=a.prompt,
        )
        tmp = out + ".part"
        with open(tmp, "w", encoding="utf-8") as f:
            for s in segments:
                f.write(f"[{ts(s.start)} - {ts(s.end)}] {s.text.strip()}\n")
                f.flush()
        os.replace(tmp, out)
        el = time.time() - t0
        left -= durs[path]
        done_audio += dur
        done_time += el
        eta = left / (done_audio / done_time) / 60
        print(f"done [{i}/{len(a.inputs)}] {name}: audio {dur/60:.1f} min, took {el/60:.1f} min "
              f"(x{dur/el:.2f} realtime) | remaining audio {left/60:.0f} min, ETA {eta:.0f} min", flush=True)


if __name__ == "__main__":
    sys.exit(main())
