"""여러 .md 파일의 LaTeX 수식($...$, $$...$$)을 브라우저(MathJax)로 그려 보고 오류가 난 것을 찾는다.

Usage: python -I mathcheck.py "a.md" "b.md" ... [--out <scratchpad>/mathcheck.html]
- 결과: "ERRORS n" 과 함께 "파일:줄 | 오류 내용" 목록을 출력한다.
- 헤드리스 브라우저(browser.py)와 인터넷(MathJax CDN)이 있으면 실제로 그려서 확인하고,
  없으면 latex2mathml로 문법만 확인한다(느슨함).
- 통화 \\$ 는 수식으로 보지 않는다.
"""
import argparse
import html
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MATH = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$|(?<!\\)\$(.+?)(?<!\\)\$")
MATHJAX_URL = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.min.js"
JS = r"""
window.MathJax = {tex: {inlineMath: [['\\(', '\\)']]}, svg: {fontCache: 'global'},
  startup: {pageReady: () => MathJax.startup.defaultPageReady().then(() => {
    const bad = [...document.querySelectorAll('div.e')].filter(d => d.querySelector('[data-mjx-error]'));
    document.getElementById('out').textContent = 'ERRORS ' + bad.length + '\n' +
      bad.map(d => d.dataset.k + ' | ' + d.querySelector('[data-mjx-error]').getAttribute('data-mjx-error')).join('\n');
  })}};
"""


def collect(files):
    exprs = []
    for f in files:
        for i, line in enumerate(open(f, encoding="utf-8"), 1):
            for m in MATH.finditer(line):
                exprs.append((f"{os.path.basename(f)}:{i}", m.group(1) or m.group(2)))
    return exprs


def syntax_only(exprs):
    from latex2mathml.converter import convert as tex2mml
    bad = []
    for k, t in exprs:
        try:
            tex2mml(t)
        except Exception as e:  # noqa: BLE001
            bad.append(f"{k} | {e}")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default=os.path.join(tempfile.gettempdir(), "mathcheck.html"))
    a = ap.parse_args()
    exprs = collect(a.files)
    body = "".join(f'<div class="e" data-k="{html.escape(k)}">\\({html.escape(t)}\\)</div>' for k, t in exprs)
    page = ('<!DOCTYPE html><html><head><meta charset="utf-8"><script>' + JS +
            f'</script><script src="{MATHJAX_URL}"></script></head>'
            '<body><pre id="out">PENDING</pre>' + body + '</body></html>')
    open(a.out, "w", encoding="utf-8").write(page)
    import browser
    dom = browser.dump_dom(a.out)
    m = re.search(r'<pre id="out">([\s\S]*?)</pre>', dom or "")
    if m and not m.group(1).startswith("PENDING"):
        print(f"{len(exprs)} formulas (MathJax로 확인)")
        print(html.unescape(m.group(1)))
        return
    bad = syntax_only(exprs)
    print(f"{len(exprs)} formulas (브라우저·MathJax를 쓸 수 없어 문법만 확인)")
    print("ERRORS", len(bad), *bad, sep="\n")


if __name__ == "__main__":
    main()
