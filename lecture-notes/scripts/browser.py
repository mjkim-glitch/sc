"""헤드리스 브라우저(Edge·Chrome·Chromium) 찾기 + HTML → PDF 인쇄 / DOM 덤프 / 스크린샷.

Windows(이 PC)·macOS·Linux(claude.ai 실행 환경) 모두에서 쓴다. 브라우저가 없으면 None을 돌려주고,
부르는 쪽은 "이 환경에서는 확인·인쇄를 못 함"을 사용자에게 알리고 HTML만 넘긴다.

Usage:
  python -I browser.py pdf  in.html out.pdf [--wait 40000]   # @page CSS 크기대로 인쇄
  python -I browser.py shot in.html out.png [--size 1400,2400]
  python -I browser.py dom  in.html                          # 스크립트 실행 뒤 DOM을 출력
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
NAMES = ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "microsoft-edge", "msedge", "chrome"]


def find_browser():
    for p in CANDIDATES:
        if os.path.exists(p):
            return p
    for n in NAMES:
        p = shutil.which(n)
        if p:
            return p
    # playwright가 설치해 둔 chromium
    for base in [Path.home() / ".cache" / "ms-playwright", Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"]:
        if base.is_dir():
            for exe in list(base.glob("chromium-*/chrome-linux/chrome")) + list(base.glob("chromium-*/chrome-win/chrome.exe")):
                return str(exe)
    return None


def _run(args):
    b = find_browser()
    if not b:
        return None
    prof = os.path.join(tempfile.gettempdir(), "lecture_notes_browser_profile")
    base = [b, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}"]
    if os.name != "nt":  # 컨테이너(root)에서는 샌드박스를 끄지 않으면 Chromium이 뜨지 않는다
        base.append("--no-sandbox")
    return subprocess.run(base + args, capture_output=True, text=True, encoding="utf-8", errors="replace")


def uri(path):
    return Path(path).resolve().as_uri()


def print_pdf(html_path, pdf_path, wait_ms=40000):
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    r = _run([f"--virtual-time-budget={wait_ms}", "--run-all-compositor-stages-before-draw", "--no-pdf-header-footer",
              f"--print-to-pdf={os.path.abspath(pdf_path)}", uri(html_path)])
    return r is not None and os.path.exists(pdf_path)


def screenshot(html_path, png_path, size="1400,2400", wait_ms=20000):
    r = _run([f"--virtual-time-budget={wait_ms}", "--hide-scrollbars", f"--window-size={size}",
              f"--screenshot={os.path.abspath(png_path)}", uri(html_path)])
    return r is not None and os.path.exists(png_path)


def dump_dom(html_path, wait_ms=60000):
    r = _run([f"--virtual-time-budget={wait_ms}", "--dump-dom", uri(html_path)])
    return None if r is None else r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["pdf", "shot", "dom"])
    ap.add_argument("src")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--wait", type=int, default=40000)
    ap.add_argument("--size", default="1400,2400")
    a = ap.parse_args()
    if not find_browser():
        sys.exit("헤드리스 브라우저(Edge/Chrome/Chromium)가 없어 실행하지 못함")
    if a.cmd == "pdf":
        ok = print_pdf(a.src, a.out, a.wait)
    elif a.cmd == "shot":
        ok = screenshot(a.src, a.out, a.size, a.wait)
    else:
        sys.stdout.write(dump_dom(a.src, a.wait) or "")
        return
    print(("saved " + a.out) if ok else "실패")


if __name__ == "__main__":
    main()
