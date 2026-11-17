"""정리 자료 세트(.md) → 웹 페이지 묶음(web/): index · guide · exam · mindmap(+프린트용) · note + images/.

Usage (과목 폴더에서):
  python -I build_web.py --dir . --prefix "{강의명}_{범위}_" --title "{강의명} 중간고사" --scope "범위 한 줄 설명" \
      [--concepts tools/concepts.py --mindmap-md "{강의명}_{범위}_마인드맵.md"]

- 있는 파일만 페이지로 만든다: {prefix}study note.md / {prefix}스터디가이드.md / {prefix}모의고사.md
- --concepts를 주면 마인드맵 웹 페이지·.md·프린트용(A3, web/mindmap_print.html)을 함께 만든다.
  프린트용 PDF는 scripts/print_pdf.ps1로 만들고 web/mindmap_print.pdf로 둔다 (페이지의 내려받기 버튼이 이 파일을 쓴다).
- 아티팩트로 올릴 때 내려받기 버튼을 쓰려면 downloads 기능을 먼저 선언한다 (references/web.md).
"""
import argparse
import html
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(os.path.dirname(HERE), "structure")
sys.path.insert(0, HERE)
import webmd  # noqa: E402

# main()에서 채움
ROOT = WEB = NOTE = GUIDE = EXAM = CONCEPTS = MINDMAP_MD = ""
TITLE = COURSE = SCOPE = ""
HAVE = {}


MATHJAX = """<script>
window.MathJax = {
  tex: { inlineMath: [['\\\\(', '\\\\)']], displayMath: [['\\\\[', '\\\\]']], processEscapes: false },
  svg: { fontCache: 'global' },
  options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'template'] }
};
</script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.min.js"></script>"""

FONTS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">"""

CSS = r"""
:root {
  /* 장부(ledger) 느낌: 옅은 종이색 + 국채 초록 강조, 노트 색 규칙(회색 강의·빨강 중요·파랑 자료에 없음)을 그대로 */
  --paper: #f6f7f4; --card: #ffffff; --ink: #1c2321; --muted: #5b6662; --line: #d8ded9;
  --accent: #1d6a55; --accent-soft: #e2efe9;
  --lec: #636a6e; --imp: #b3261e; --ext: #0b57d0; --sol: #2e7d32; --hw: #7a4f00;
  --hl: #fff09a; --pink: #fbdade; --blue: #d5e7fa;
  --font-body: "IBM Plex Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
  --font-num: "IBM Plex Mono", Consolas, monospace;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #111614; --card: #181f1c; --ink: #e5ebe8; --muted: #9ba7a2; --line: #2b3531;
    --accent: #63c3a3; --accent-soft: #1d2d27;
    --lec: #a9b0b3; --imp: #ff8b7f; --ext: #8db6f7; --sol: #86cf95; --hw: #e0b45c;
    --hl: rgba(255, 226, 80, .32); --pink: rgba(250, 150, 170, .26); --blue: rgba(120, 175, 240, .26);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --paper: #111614; --card: #181f1c; --ink: #e5ebe8; --muted: #9ba7a2; --line: #2b3531;
  --accent: #63c3a3; --accent-soft: #1d2d27;
  --lec: #a9b0b3; --imp: #ff8b7f; --ext: #8db6f7; --sol: #86cf95; --hw: #e0b45c;
  --hl: rgba(255, 226, 80, .32); --pink: rgba(250, 150, 170, .26); --blue: rgba(120, 175, 240, .26);
  color-scheme: dark;
}
* { box-sizing: border-box; }
html { scroll-padding-top: 64px; }
body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--font-body); font-size: 16px; line-height: 1.7; }
a { color: var(--accent); }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.top { position: sticky; top: 0; z-index: 5; background: var(--paper); border-bottom: 1px solid var(--line); }
.top nav { max-width: 1180px; margin: 0 auto; padding: 10px 16px; display: flex; gap: 6px 18px; flex-wrap: wrap; align-items: baseline; }
.top .brand { font-weight: 700; margin-right: 8px; color: var(--ink); text-decoration: none; }
.top nav a.pg { text-decoration: none; color: var(--muted); font-weight: 500; }
.top nav a.pg[aria-current="page"] { color: var(--accent); border-bottom: 2px solid var(--accent); }
.wrap { max-width: 1180px; margin: 0 auto; padding: 24px 16px 80px; display: grid; grid-template-columns: 250px minmax(0, 1fr); gap: 36px; }
.wrap.single { grid-template-columns: minmax(0, 1fr); max-width: 860px; }
.toc { position: sticky; top: 64px; align-self: start; max-height: calc(100vh - 80px); overflow-y: auto; font-size: 14px; line-height: 1.45; padding-right: 6px; }
.toc a { display: block; color: var(--muted); text-decoration: none; padding: 3px 0; }
.toc a:hover { color: var(--accent); }
.toc .l1 { font-weight: 700; color: var(--ink); margin-top: 10px; }
.toc .l3 { padding-left: 12px; font-size: 13px; }
.toc .l4 { padding-left: 24px; font-size: 12.5px; }
main { min-width: 0; }
main > .body { max-width: 780px; }
h1 { font-size: 1.75rem; line-height: 1.3; margin: 0 0 12px; text-wrap: balance; }
h2 { font-size: 1.35rem; margin: 40px 0 10px; padding-top: 10px; border-top: 2px solid var(--ink); text-wrap: balance; }
h3 { font-size: 1.12rem; margin: 28px 0 8px; color: var(--accent); text-wrap: balance; }
h4 { font-size: 1rem; margin: 20px 0 6px; }
ul { padding-left: 1.25em; margin: 6px 0; }
li { margin: 3px 0; }
p { margin: 8px 0; }
hr { border: 0; border-top: 1px solid var(--line); margin: 28px 0; }
mark { background: var(--hl); color: inherit; padding: 0 2px; border-radius: 2px; }
mark.pink { background: var(--pink); }
mark.blue { background: var(--blue); }
code { font-family: var(--font-num); font-size: .9em; background: var(--accent-soft); padding: 0 4px; border-radius: 3px; }
li.lec, p.lec { color: var(--lec); }
li.lec.key, p.lec.key { color: var(--imp); font-weight: 700; }
li.lec.extra, li.extra, p.extra { color: var(--ext); }
li.sol, p.sol { color: var(--sol); }
.tag { display: inline-block; font-size: .72em; font-weight: 700; line-height: 1.5; padding: 0 6px; margin-right: 4px; border-radius: 999px; border: 1px solid currentColor; vertical-align: .12em; }
.tag.lec { color: var(--lec); }
.tag.imp { color: #fff; background: var(--imp); border-color: var(--imp); }
.tag.hw { color: var(--hw); }
.tag.board { color: var(--hw); }
.tag.sol { color: var(--sol); }
.tag.ext { color: var(--ext); }
.chk { color: var(--muted); font-size: .9em; }
.ref { font-size: .82em; color: var(--muted); white-space: nowrap; }
.ref a { font-family: var(--font-num); }
.disp { display: block; margin: 6px 0; overflow-x: auto; overflow-y: hidden; }
mjx-container[display="true"] { margin: .4em 0 !important; }
mjx-container { max-width: 100%; }
.tbl { overflow-x: auto; margin: 10px 0; }
table { border-collapse: collapse; font-size: .92em; font-variant-numeric: tabular-nums; }
th, td { border: 1px solid var(--line); padding: 5px 9px; text-align: left; vertical-align: top; }
th { background: var(--accent-soft); }
td { background: var(--card); }
img { max-width: 100%; height: auto; border: 1px solid var(--line); border-radius: 4px; background: #fff; }
figure { margin: 12px 0; }
pre.tree { font-family: var(--font-num); font-size: 13px; line-height: 1.5; background: var(--card); border: 1px solid var(--line); padding: 12px; overflow-x: auto; }
li.check { list-style: none; margin-left: -1.2em; }
li.check input { accent-color: var(--accent); margin-right: 6px; }
.legend { display: flex; flex-wrap: wrap; gap: 8px 16px; font-size: 14px; padding: 10px 12px; border: 1px solid var(--line); background: var(--card); border-radius: 6px; margin: 12px 0 20px; }
@media (max-width: 860px) {
  .wrap { grid-template-columns: minmax(0, 1fr); }
  .toc { position: static; max-height: none; border: 1px solid var(--line); padding: 10px 12px; background: var(--card); border-radius: 6px; }
  .toc details summary { cursor: pointer; font-weight: 700; }
}
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; transition: none !important; } }
/* 모의고사 */
.bar { position: sticky; top: 49px; z-index: 4; background: var(--paper); padding: 10px 0; border-bottom: 1px solid var(--line); display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.btn { font: inherit; font-size: 14px; padding: 5px 12px; border: 1px solid var(--line); background: var(--card); color: var(--ink); border-radius: 999px; cursor: pointer; }
.btn[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: #fff; }
.btn:hover { border-color: var(--accent); }
.score { margin-left: auto; font-family: var(--font-num); font-size: 14px; color: var(--muted); }
.grp { margin-top: 34px; }
.q { background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--line); border-radius: 6px; padding: 14px 16px; margin: 14px 0; }
.q.imp { border-left-color: var(--imp); }
.q.right { border-left-color: var(--sol); }
.q.wrong { border-left-color: #c77700; }
.q header { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 6px; }
.qn { font-family: var(--font-num); font-weight: 500; font-size: 15px; color: var(--accent); }
.kind { font-size: 12px; color: var(--muted); border: 1px solid var(--line); border-radius: 999px; padding: 0 8px; }
.qtext { font-weight: 500; }
.acts { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.acts details { border: 1px solid var(--line); border-radius: 6px; background: var(--paper); }
.acts details[open] { flex-basis: 100%; }
.acts summary { cursor: pointer; padding: 4px 12px; font-size: 14px; font-weight: 700; list-style: none; }
.acts summary::-webkit-details-marker { display: none; }
.acts summary::before { content: "▸ "; color: var(--muted); }
.acts details[open] summary::before { content: "▾ "; }
.acts details > div { padding: 2px 14px 10px; }
.acts .f-ans summary { color: var(--accent); }
.acts .f-sol summary { color: var(--sol); }
.acts .f-exp summary { color: var(--ext); }
.acts .f-pts summary { color: var(--hw); }
.acts .f-note summary { color: var(--muted); }
.note-body { border-top: 1px dashed var(--line); margin-top: 6px; padding-top: 6px; font-size: 15px; }
.self { display: flex; gap: 8px; margin-top: 10px; font-size: 13px; color: var(--muted); align-items: center; }
.self .btn { font-size: 13px; padding: 2px 10px; }
/* 첫 화면 */
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin: 20px 0; }
.card { display: block; background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 16px; text-decoration: none; color: var(--ink); }
.card:hover { border-color: var(--accent); }
.card b { display: block; font-size: 1.1rem; color: var(--accent); margin-bottom: 4px; }
.card span { color: var(--muted); font-size: 14px; }
.facts { font-variant-numeric: tabular-nums; }
"""


def page(title, cur, body, extra_head="", toc_html="", single=False, extra_js="", mathjax=None, body_class=""):
    nav = [("index.html", "처음")] + [(h, lab) for h, lab in
           [("guide.html", "스터디 가이드"), ("exam.html", "모의고사"), ("mindmap.html", "마인드맵"), ("note.html", "정리 노트")]
           if HAVE.get(h)]
    links = "".join(f'<a class="pg" href="{h}"{" aria-current=\"page\"" if h == cur else ""}>{t}</a>' for h, t in nav)
    layout = f'<div class="wrap{" single" if single else ""}">{toc_html}<main>{body}</main></div>'
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
{FONTS}
<style>{CSS}</style>
{MATHJAX if mathjax is None else mathjax}
{extra_head}
</head>
<body{f' class="{body_class}"' if body_class else ""}>
<header class="top"><nav><a class="brand" href="index.html">{html.escape(TITLE)}</a>{links}</nav></header>
{layout}
{extra_js}
</body>
</html>
"""


def toc_block(toc, levels=(1, 2, 3)):
    items = []
    for lv, hid, title in toc:
        if lv in levels:
            items.append(f'<a class="l{lv}" href="#{hid}">{html.escape(title)}</a>')
    inner = "".join(items)
    return f'<nav class="toc" aria-label="목차"><details open><summary>목차</summary>{inner}</details></nav>'


def read_lines(p):
    return open(p, encoding="utf-8").read().replace("\r\n", "\n").split("\n")


NOTE_ALL = False  # --note-all: 예전처럼 한 페이지에 전부


def split_chapters(lines):
    """노트 본문(제목 줄 뺀 것) → (머리말 줄, [(대분류 제목, 줄 목록), …]). 대분류(`# `) 하나 = 강의자료 하나."""
    pre, chaps = [], []
    for l in lines:
        if re.match(r"^# \S", l):
            chaps.append((l[2:].strip(), [l]))
        elif chaps:
            chaps[-1][1].append(l)
        else:
            pre.append(l)
    for _, ls in chaps:  # 대분류 사이 구분선(---)은 과 나누기로 대신한다
        while ls and ls[-1].strip() in ("", "---"):
            ls.pop()
    return pre, chaps


NOTE_LEGEND = ('<div class="legend"><span>검정 = 강의자료</span><span class="tag hw">필기</span><span class="tag board">판서</span>'
               '<span style="color:var(--lec)">회색 = 강의 녹음</span><span style="color:var(--imp);font-weight:700">빨강 = 교수 강조</span>'
               '<span style="color:var(--ext)">파랑 = 자료에 없음</span><mark>핵심</mark><mark class="pink">헷갈림</mark><mark class="blue">반대편</mark></div>')

# 노트 페이지는 과를 열 때 그 과만 수식을 그린다(숨긴 과는 크기를 잴 수 없고, 휴대폰에서 첫 화면이 느려지므로)
NOTE_MATHJAX = MATHJAX.replace("options: {", "startup: { typeset: false },\n  options: {")

NOTE_CSS = r"""
<style>
/* 정리 노트: 과(강의자료) 단위 보기 · 목차 이동 · 휴대폰 읽기 */
body.note { font-size: calc(16px * var(--fs, 1)); }
.chapbar { position: sticky; top: var(--toph, 49px); z-index: 4; background: var(--paper); border-bottom: 1px solid var(--line); }
.chapbar .in { max-width: 1180px; margin: 0 auto; padding: 6px 16px; display: flex; gap: 8px; align-items: center; }
.chapbar select { flex: 1; min-width: 0; font: inherit; font-size: 15px; padding: 6px 8px; border: 1px solid var(--line); border-radius: 6px; background: var(--card); color: var(--ink); }
.chapbar .btn { flex: none; min-height: 36px; }
.chapbar .pos { flex: none; font-family: var(--font-num); font-size: 13px; color: var(--muted); }
.prog { height: 3px; background: transparent; }
.prog i { display: block; height: 100%; width: 0; background: var(--accent); }
.chap[hidden] { display: none; }
.chap > h1:first-child { margin-top: 8px; }
.chapnav { display: flex; gap: 10px; justify-content: space-between; margin: 40px 0 0; padding-top: 16px; border-top: 1px solid var(--line); }
.chapnav a { flex: 1; display: block; padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--card); text-decoration: none; color: var(--ink); font-size: 14px; min-height: 44px; }
.chapnav a small { display: block; color: var(--muted); font-size: 12px; }
.chapnav a.nx { text-align: right; }
.chapnav a:hover { border-color: var(--accent); }
.toc .ch { display: block; }
.toc .ch > a.l1 { padding: 6px 0; }
.toc .ch.on > a.l1 { color: var(--accent); }
.toc .ch:not(.on) .subs { display: none; }
.toc a.here { color: var(--accent); font-weight: 700; }
.toc .tools { display: flex; gap: 6px; margin: 4px 0 8px; }
.toc .tools .btn { font-size: 13px; padding: 2px 10px; }
.fab { display: none; }
.scrim { display: none; }
@media (min-width: 861px) {
  body.note .toc { top: calc(var(--toph, 49px) + var(--barh, 52px) + 12px); max-height: calc(100vh - var(--toph, 49px) - var(--barh, 52px) - 24px); }
}
@media (max-width: 860px) {
  body.note { line-height: 1.75; }
  .wrap { padding: 12px 14px 96px; gap: 0; }
  .chap > h1 { font-size: 1.35rem; }
  h2 { font-size: 1.2rem; margin-top: 30px; }
  h3 { font-size: 1.06rem; }
  ul { padding-left: 1.05em; }
  /* 목차는 서랍으로 */
  .toc { position: fixed; top: 0; bottom: 0; left: 0; width: min(86vw, 340px); max-height: none; z-index: 20; margin: 0;
         border: 0; border-right: 1px solid var(--line); border-radius: 0; padding: 14px 14px 40px; background: var(--card);
         transform: translateX(-105%); transition: transform .2s ease; overflow-y: auto; font-size: 15px; }
  .toc a { padding: 7px 0; }
  .toc .l3 { font-size: 14px; }
  body.drawer .toc { transform: none; box-shadow: 0 0 24px rgba(0,0,0,.25); }
  body.drawer .scrim { display: block; position: fixed; inset: 0; z-index: 19; background: rgba(0,0,0,.35); }
  .toc details > summary { pointer-events: none; list-style: none; font-size: 16px; }
  .toc details > summary::-webkit-details-marker { display: none; }
  .fab { display: flex; position: fixed; right: 16px; bottom: calc(16px + env(safe-area-inset-bottom)); z-index: 18; gap: 8px; }
  .fab .btn { min-height: 46px; min-width: 46px; padding: 0 16px; font-size: 15px; font-weight: 700; box-shadow: 0 2px 10px rgba(0,0,0,.18); }
  .fab .btn.main { background: var(--accent); border-color: var(--accent); color: #fff; }
  .chapbar .pos { display: none; }
  .chapnav { flex-direction: column; }
  .chapnav a.nx { text-align: left; }
  .top nav { padding: 8px 14px; gap: 4px 14px; font-size: 14px; }
}
@media print { .chapbar, .fab, .toc, .chapnav, .top { display: none !important; } .chap[hidden] { display: block !important; } .wrap { display: block; } }
</style>"""

NOTE_JS = r"""
<script>
(() => {
  const chaps = [...document.querySelectorAll('section.chap')];
  const sel = document.getElementById('chapSel'), pos = document.getElementById('chapPos');
  const tocChs = [...document.querySelectorAll('.toc .ch')];
  const bar = document.querySelector('.prog i');
  const store = (() => { try { const k = '__t'; localStorage.setItem(k, k); localStorage.removeItem(k); return localStorage; } catch (e) { return null; } })();
  const KEY = 'note:' + document.title;
  const done = new Set();
  let cur = -1;

  const setTop = () => {
    const r = document.documentElement.style;
    r.setProperty('--toph', document.querySelector('.top').offsetHeight + 'px');
    r.setProperty('--barh', document.querySelector('.chapbar').offsetHeight + 'px');
  };
  setTop(); addEventListener('resize', setTop);
  const offset = () => document.querySelector('.top').offsetHeight + document.querySelector('.chapbar').offsetHeight + 8;
  document.documentElement.style.scrollPaddingTop = '0px';

  function typeset(i) {
    if (done.has(i)) return Promise.resolve();
    done.add(i);
    const go = () => window.MathJax.typesetPromise([chaps[i]]).catch(() => {});
    if (window.MathJax && window.MathJax.typesetPromise) return go();
    return new Promise(res => {
      const t = setInterval(() => { if (window.MathJax && window.MathJax.typesetPromise) { clearInterval(t); go().then(res); } }, 100);
      setTimeout(() => { clearInterval(t); res(); }, 15000);
    });
  }
  function scrollToEl(el) {
    const y = el ? el.getBoundingClientRect().top + scrollY - offset() : 0;
    scrollTo({ top: Math.max(0, y) });
  }
  function show(i, targetId, push) {
    i = Math.max(0, Math.min(chaps.length - 1, i));
    if (i !== cur) {
      chaps.forEach((c, k) => { c.hidden = k !== i; });
      tocChs.forEach((c, k) => c.classList.toggle('on', k === i));
      sel.value = String(i);
      pos.textContent = (i + 1) + ' / ' + chaps.length;
      cur = i;
      if (store) store.setItem(KEY, String(i));
    }
    const target = targetId ? document.getElementById(targetId) : null;
    scrollToEl(target);
    typeset(i).then(() => { if (target) scrollToEl(target); spy(); });
    if (push) history.replaceState(null, '', '#' + (targetId || chaps[i].id));
  }
  function chapOf(id) {
    const el = id && document.getElementById(id);
    const c = el && el.closest('section.chap');
    return c ? chaps.indexOf(c) : -1;
  }
  function fromHash() {
    const id = decodeURIComponent(location.hash.slice(1));
    const k = chapOf(id);
    if (k >= 0) { show(k, chaps[k].id === id ? null : id); return true; }
    return false;
  }

  sel.addEventListener('change', () => show(+sel.value, null, true));
  document.querySelectorAll('[data-go]').forEach(b => b.addEventListener('click', e => {
    e.preventDefault(); show(cur + (+b.dataset.go), null, true);
  }));
  // 페이지 안의 모든 #링크(목차·(→ 2.3.1)·다른 과로 가는 링크)를 과 전환으로
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href]');
    if (!a) return;
    const h = a.getAttribute('href');
    const m = h.match(/^(?:note\.html)?#(.+)$/);
    if (!m) return;
    const k = chapOf(decodeURIComponent(m[1]));
    if (k < 0) return;
    e.preventDefault();
    document.body.classList.remove('drawer');
    show(k, chaps[k].id === m[1] ? null : m[1], true);
  });
  addEventListener('hashchange', fromHash);

  // 목차 서랍(휴대폰)
  const toggle = open => document.body.classList.toggle('drawer', open);
  document.getElementById('tocBtn').addEventListener('click', () => {
    toggle(!document.body.classList.contains('drawer'));
    const here = document.querySelector('.toc a.here') || document.querySelector('.toc .ch.on > a');
    if (here) here.scrollIntoView({ block: 'center' });
  });
  document.querySelector('.scrim').addEventListener('click', () => toggle(false));
  addEventListener('keydown', e => { if (e.key === 'Escape') toggle(false); });
  document.getElementById('topBtn').addEventListener('click', () => scrollTo({ top: 0 }));

  // 글자 크기
  let fs = store ? parseFloat(store.getItem('note:fs')) || 1 : 1;
  const applyFs = () => { document.body.style.setProperty('--fs', fs); if (store) store.setItem('note:fs', fs); };
  document.querySelectorAll('[data-fs]').forEach(b => b.addEventListener('click', () => {
    fs = Math.max(.85, Math.min(1.4, +(fs + (+b.dataset.fs)).toFixed(2))); applyFs();
  }));
  applyFs();

  // 지금 읽는 절을 목차에 표시 + 진행 막대
  const links = new Map([...document.querySelectorAll('.toc a[href^="#"]')].map(a => [a.getAttribute('href').slice(1), a]));
  function spy() {
    if (cur < 0) return;
    const hs = chaps[cur].querySelectorAll('h1[id], h2[id], h3[id]');
    let best = null;
    for (const h of hs) { if (h.getBoundingClientRect().top - offset() <= 4) best = h; else break; }
    document.querySelectorAll('.toc a.here').forEach(a => a.classList.remove('here'));
    const a = best && links.get(best.id);
    if (a) a.classList.add('here');
    const r = chaps[cur].getBoundingClientRect(), total = r.height - innerHeight + offset();
    bar.style.width = (total > 0 ? Math.min(100, Math.max(0, (-r.top + offset()) / total * 100)) : 100) + '%';
  }
  let tick = false;
  addEventListener('scroll', () => { if (!tick) { tick = true; requestAnimationFrame(() => { tick = false; spy(); }); } }, { passive: true });

  // 휴대폰에서 옆으로 밀어 이전·다음 과
  let sx = 0, sy = 0, st = 0;
  addEventListener('touchstart', e => { const t = e.touches[0]; sx = t.clientX; sy = t.clientY; st = Date.now(); }, { passive: true });
  addEventListener('touchend', e => {
    if (document.body.classList.contains('drawer')) return;
    if (e.target.closest('.tbl, .disp, pre, mjx-container, .toc')) return;
    const t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
    if (Date.now() - st < 600 && Math.abs(dx) > 90 && Math.abs(dy) < 40) show(cur + (dx < 0 ? 1 : -1), null, true);
  }, { passive: true });

  if (!fromHash()) {
    const last = store ? parseInt(store.getItem(KEY), 10) : NaN;
    show(Number.isFinite(last) ? last : 0);
  }
})();
</script>"""


def chap_plain(t):
    """대분류 제목 → 목차·고르기 칸에 쓸 글자 (꾸밈 표시 뺌)."""
    return html.unescape(re.sub(r"<[^>]+>", "", webmd.inline(t, "note.html"))).replace("\\(", "").replace("\\)", "")


def build_note():
    lines = read_lines(NOTE)
    title = lines[0].lstrip("# ").strip()
    pre, chaps = split_chapters(lines[1:])
    if NOTE_ALL or len(chaps) < 2:
        toc = []
        body = webmd.render(lines[1:], note_page="note.html", toc=toc, shift=0)
        body = f'<div class="body"><h1>{html.escape(title)}</h1>{NOTE_LEGEND}{body}</div>'
        open(os.path.join(WEB, "note.html"), "w", encoding="utf-8").write(
            page(f"{COURSE} 정리 노트", "note.html", body, toc_html=toc_block(toc, (1, 2))))
        return

    secs, toc_parts, opts = [], [], []
    for k, (ctitle, clines) in enumerate(chaps):
        toc = []
        inner = webmd.render(clines, note_page="note.html", toc=toc, shift=0)
        plain = chap_plain(ctitle)
        prev_a = (f'<a class="pv" href="#" data-go="-1"><small>← 이전 과</small>{html.escape(chap_plain(chaps[k - 1][0]))}</a>'
                  if k > 0 else '<span></span>')
        next_a = (f'<a class="nx" href="#" data-go="1"><small>다음 과 →</small>{html.escape(chap_plain(chaps[k + 1][0]))}</a>'
                  if k + 1 < len(chaps) else '<span></span>')
        secs.append(f'<section class="chap" id="chap-{k + 1}" data-title="{html.escape(plain)}"{" hidden" if k else ""}>'
                    f'{inner}<nav class="chapnav" aria-label="과 이동">{prev_a}{next_a}</nav></section>')
        subs = "".join(f'<a class="l{lv}" href="#{hid}">{html.escape(t)}</a>' for lv, hid, t in toc if lv in (2, 3))
        toc_parts.append(f'<div class="ch"><a class="l1" href="#chap-{k + 1}">{html.escape(plain)}</a><div class="subs">{subs}</div></div>')
        opts.append(f'<option value="{k}">{k + 1}. {html.escape(plain)}</option>' if not re.match(r"^\d", plain)
                    else f'<option value="{k}">{html.escape(plain)}</option>')

    head = webmd.render(pre, note_page="note.html") if any(l.strip() and l.strip() != "---" for l in pre) else ""
    head_html = (f'<details class="intro"><summary>노트 머리말 · 색 표시</summary>{head}{NOTE_LEGEND}</details>'
                 if head else f'<details class="intro"><summary>색 표시</summary>{NOTE_LEGEND}</details>')
    body = (f'<div class="body"><h1 style="font-size:1.3rem">{html.escape(title)}</h1>{head_html}{"".join(secs)}</div>')
    toc_html = ('<nav class="toc" aria-label="목차"><details open><summary>목차 · 강의자료별</summary>'
                '<div class="tools"><button class="btn" type="button" data-fs="-0.1" aria-label="글자 작게">가−</button>'
                '<button class="btn" type="button" data-fs="0.1" aria-label="글자 크게">가+</button></div>'
                + "".join(toc_parts) + '</details></nav>')
    chapbar = ('<div class="chapbar"><div class="in">'
               '<button class="btn" type="button" data-go="-1" aria-label="이전 과">‹</button>'
               f'<select id="chapSel" aria-label="과 고르기">{"".join(opts)}</select>'
               '<button class="btn" type="button" data-go="1" aria-label="다음 과">›</button>'
               '<span class="pos" id="chapPos"></span></div><div class="prog"><i></i></div></div>')
    extras = ('<div class="scrim"></div><div class="fab"><button class="btn" id="topBtn" type="button" aria-label="맨 위로">↑</button>'
              '<button class="btn main" id="tocBtn" type="button" aria-label="목차 열기">목차</button></div>')
    out = page(f"{COURSE} 정리 노트", "note.html", body, extra_head=NOTE_CSS, toc_html=toc_html,
               extra_js=extras + NOTE_JS, mathjax=NOTE_MATHJAX, body_class="note")
    out = out.replace("</header>\n", "</header>\n" + chapbar + "\n", 1)
    open(os.path.join(WEB, "note.html"), "w", encoding="utf-8").write(out)


def build_guide():
    lines = read_lines(GUIDE)
    toc = []
    body = webmd.render(lines[1:], note_page="note.html", toc=toc, heading_ids=False)
    title = lines[0].lstrip("# ").strip()
    body = f'<div class="body"><h1>{html.escape(title)}</h1>{body}</div>'
    js = """<script>
document.querySelectorAll('li.check input').forEach((c, i) => {
  const k = 'guide-check-' + i;
  try { c.checked = localStorage.getItem(k) === '1'; } catch (e) {}
  c.addEventListener('change', () => { try { localStorage.setItem(k, c.checked ? '1' : '0'); } catch (e) {} });
});
</script>"""
    open(os.path.join(WEB, "guide.html"), "w", encoding="utf-8").write(
        page(f"{COURSE} 스터디 가이드", "guide.html", body, toc_html=toc_block(toc, (2, 3)), extra_js=js))


FIELDS = {"정답": "ans", "풀이": "sol", "관련 설명": "exp", "채점 포인트": "pts", "노트": "note"}
FIELD_LABEL = {"ans": "정답", "sol": "풀이", "exp": "관련 설명", "pts": "채점 포인트", "note": "노트 원문"}
KINDS = [("OX", "ox", "OX"), ("객관식", "mc", "객관식"), ("단답", "short", "단답"), ("빈칸", "blank", "빈칸"),
         ("계산", "calc", "계산"), ("그래프", "graph", "그래프"), ("서술", "essay", "서술"), ("논술", "essay", "서술")]


def kind_of(title):
    """'## Ⅲ. 계산 (16문항)' 같은 대제목 → (키, 이름). 맞는 낱말이 없으면 대제목 자체를 이름으로."""
    for word, key, label in KINDS:
        if word in title:
            return key, label
    name = re.sub(r"^[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ\d]+[.)]\s*", "", title).split("(")[0].strip()
    return "k" + str(abs(hash(name)) % 10000), name


def parse_exam(lines):
    head, groups, cur_group, q = [], [], None, None
    for l in lines[1:]:
        m = re.match(r"^## (.*)$", l)
        if m:
            cur_group = {"title": m.group(1), "kind": kind_of(m.group(1))[0], "label": kind_of(m.group(1))[1], "items": []}
            groups.append(cur_group)
            q = None
            continue
        m = re.match(r"^### (.*)$", l)
        if m and cur_group is not None:
            cur_group["items"].append(("sub", m.group(1)))
            q = None
            continue
        m = re.match(r"^\*\*(\d+)\.\*\* (.*)$", l)
        if m and cur_group is not None:
            q = {"n": int(m.group(1)), "text": m.group(2), "fields": [], "kind": cur_group["kind"]}
            cur_group["items"].append(("q", q))
            continue
        if q is not None:
            m = re.match(r"^- (정답|풀이|관련 설명|채점 포인트|노트):?\s*(.*)$", l)
            if m:
                q["fields"].append([FIELDS[m.group(1)], [m.group(2)] if m.group(2) else []])
                continue
            if l.startswith("  ") and q["fields"]:
                q["fields"][-1][1].append(l[2:])
                continue
            continue
        if cur_group is None and l.strip():
            head.append(l)
    return head, groups


def refs_of(text):
    m = re.search(r"\(→ ([^)]*)\)", text)
    if not m:
        return []
    out = []
    for part in re.split(r",\s*", m.group(1)):
        part = part.strip()
        r = re.match(r"^(\d\.\d+(?:\.\d+)*)~(\d\.\d+(?:\.\d+)*)$", part)
        if r:
            out.append(("range", r.group(1), r.group(2)))
        elif re.match(r"^\d\.\d+(?:\.\d+)*$", part):
            out.append(("one", part, part))
    return out


def build_exam():
    lines = read_lines(EXAM)
    secs = webmd.note_sections(read_lines(NOTE))
    order = list(secs.keys())
    head, groups = parse_exam(lines)
    templates = {}

    def want(num):
        if num in secs and num not in templates:
            templates[num] = webmd.render(secs[num], note_page="note.html", shift=1)

    cards, nq = [], 0
    for g in groups:
        cards.append(f'<section class="grp" data-kind="{g["kind"]}"><h2 id="g-{g["kind"]}">{webmd.inline(g["title"])}</h2>')
        for typ, it in g["items"]:
            if typ == "sub":
                cards.append(f'<h3>{webmd.inline(it)}</h3>')
                continue
            q = it
            nq += 1
            imp = "(중요)" in q["text"]
            kind_label = g["label"]
            chips = f'<span class="kind">{kind_label}</span>'
            if "[응용 계산]" in q["text"]:
                chips += '<span class="kind">응용 계산</span>'
            qtext = q["text"].replace("[응용 계산] ", "").replace("(중요) ", "(중요)")
            acts = []
            for key, flines in q["fields"]:
                if key == "note":
                    refs = refs_of(" ".join(flines))
                    nums = []
                    for kind_, a, b in refs:
                        if kind_ == "one":
                            nums.append(a)
                        else:
                            ia = order.index(a) if a in order else -1
                            ib = order.index(b) if b in order else -1
                            if ia >= 0 and ib >= ia:
                                depth = a.count(".")
                                nums.extend([x for x in order[ia:ib + 1] if x.count(".") == depth])
                    nums = [x for x in nums if x in secs]
                    for x in nums:
                        want(x)
                    if nums:
                        lab = " · ".join(nums)
                        acts.append(f'<details class="f-note" data-refs="{",".join(nums)}"><summary>노트 원문 {lab}</summary>'
                                    f'<div class="note-body"></div></details>')
                    continue
                first, rest = (flines[0], flines[1:]) if flines else ("", [])
                md = ([f"- {first}"] if first else []) + rest
                inner = webmd.render(md, note_page="note.html")
                if first and not rest:
                    inner = f"<p>{webmd.inline(first, 'note.html')}</p>"
                acts.append(f'<details class="f-{key}"><summary>{FIELD_LABEL[key]}</summary><div>{inner}</div></details>')
            cards.append(
                f'<article class="q{" imp" if imp else ""}" id="q{q["n"]}" data-kind="{g["kind"]}" data-imp="{1 if imp else 0}">'
                f'<header><span class="qn">{q["n"]}</span>{chips}</header>'
                f'<div class="qtext">{webmd.inline(qtext, "note.html")}</div>'
                f'<div class="acts">{"".join(acts)}</div>'
                f'<div class="self">스스로 채점 <button type="button" class="btn ok" data-q="{q["n"]}">맞음</button>'
                f'<button type="button" class="btn ng" data-q="{q["n"]}">틀림</button></div></article>')
        cards.append("</section>")
    tpl = "".join(f'<template id="tpl-{k.replace(".", "-")}">{v}</template>' for k, v in templates.items())
    intro = webmd.render(head, note_page="note.html")
    kinds = []
    for g in groups:
        if (g["kind"], g["label"]) not in kinds:
            kinds.append((g["kind"], g["label"]))
    bar = ('<div class="bar" role="toolbar" aria-label="문제 거르기">'
           '<button type="button" class="btn flt" data-f="all" aria-pressed="true">전체</button>'
           + "".join(f'<button type="button" class="btn flt" data-f="{k}" aria-pressed="false">{html.escape(lab)}</button>' for k, lab in kinds) +
           '<button type="button" class="btn" id="impOnly" aria-pressed="false">중요만</button>'
           '<button type="button" class="btn" id="wrongOnly" aria-pressed="false">틀린 것만</button>'
           '<button type="button" class="btn" id="openAll">정답·풀이 모두 펼치기</button>'
           '<button type="button" class="btn" id="closeAll">모두 접기</button>'
           f'<span class="score" id="score">맞음 0 · 틀림 0 / {nq}</span></div>')
    body = (f'<div class="body"><h1>{webmd.inline(lines[0].lstrip("# ").strip())}</h1>{intro}{bar}'
            + "".join(cards) + f"</div>{tpl}")
    js = """<script>
(function () {
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  const qs = [...document.querySelectorAll('article.q')];
  let kind = 'all', impOnly = false, wrongOnly = false;
  function mark(n, v) {
    const a = document.getElementById('q' + n);
    a.classList.toggle('right', v === 'ok');
    a.classList.toggle('wrong', v === 'ng');
    a.querySelector('.ok').setAttribute('aria-pressed', v === 'ok');
    a.querySelector('.ng').setAttribute('aria-pressed', v === 'ng');
  }
  function score() {
    let ok = 0, ng = 0;
    qs.forEach(a => { const v = store.get('exam-' + a.id); if (v === 'ok') ok++; if (v === 'ng') ng++; });
    document.getElementById('score').textContent = `맞음 ${ok} · 틀림 ${ng} / ${qs.length}`;
  }
  function apply() {
    qs.forEach(a => {
      const v = store.get('exam-' + a.id);
      const show = (kind === 'all' || a.dataset.kind === kind) && (!impOnly || a.dataset.imp === '1') && (!wrongOnly || v === 'ng');
      a.hidden = !show;
    });
    document.querySelectorAll('section.grp').forEach(s => { s.hidden = ![...s.querySelectorAll('article.q')].some(a => !a.hidden); });
  }
  qs.forEach(a => { const v = store.get('exam-' + a.id); if (v) mark(a.id.slice(1), v); });
  score();
  document.querySelectorAll('.self .btn').forEach(b => b.addEventListener('click', () => {
    const n = b.dataset.q, key = 'exam-q' + n, v = b.classList.contains('ok') ? 'ok' : 'ng';
    const nv = store.get(key) === v ? '' : v;
    store.set(key, nv); mark(n, nv); score(); if (wrongOnly) apply();
  }));
  document.querySelectorAll('.flt').forEach(b => b.addEventListener('click', () => {
    kind = b.dataset.f;
    document.querySelectorAll('.flt').forEach(x => x.setAttribute('aria-pressed', x === b));
    apply();
  }));
  const tog = (id, fn) => { const b = document.getElementById(id); b.addEventListener('click', () => { const on = b.getAttribute('aria-pressed') !== 'true'; b.setAttribute('aria-pressed', on); fn(on); apply(); }); };
  tog('impOnly', on => impOnly = on);
  tog('wrongOnly', on => wrongOnly = on);
  document.getElementById('openAll').addEventListener('click', () => {
    qs.forEach(a => { if (!a.hidden) a.querySelectorAll('details.f-ans, details.f-sol').forEach(d => d.open = true); });
  });
  document.getElementById('closeAll').addEventListener('click', () => document.querySelectorAll('.acts details').forEach(d => d.open = false));
  document.querySelectorAll('details.f-note').forEach(d => d.addEventListener('toggle', () => {
    const box = d.querySelector('.note-body');
    if (!d.open || box.dataset.filled) return;
    d.dataset.refs.split(',').forEach(r => {
      const t = document.getElementById('tpl-' + r.replace(/\\./g, '-'));
      if (t) box.appendChild(t.content.cloneNode(true));
    });
    box.dataset.filled = '1';
    if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([box]).catch(() => {});
  }));
})();
</script>"""
    open(os.path.join(WEB, "exam.html"), "w", encoding="utf-8").write(
        page(f"{COURSE} 모의고사", "exam.html", body, single=True, extra_js=js))
    return nq


def build_mindmap():
    """스킬의 구조도 빌더를 쓰되, 노트 원문 렌더링을 webmd로 바꿔 수식·그림·색이 보이게 한다."""
    sys.path.insert(0, SKILL)
    import notedata
    notedata.inline = lambda s: webmd.inline(s, "note.html")
    notedata.block_html = lambda body: webmd.render(body, note_page="note.html", heading_ids=False, shift=2)
    import mindmap_build
    out_html = os.path.join(WEB, "mindmap.html")
    mindmap_build.build(NOTE, CONCEPTS, out_html, MINDMAP_MD,
                        os.path.join(WEB, "mindmap_print.html"), os.path.join(ROOT, "tools", "_gen"))
    h = open(out_html, encoding="utf-8").read()
    extra_css = ("<style>.mm-nav{position:fixed;right:12px;bottom:12px;z-index:50;display:flex;gap:6px;flex-wrap:wrap}"
                 ".mm-nav a{font:14px/1.4 'IBM Plex Sans KR',sans-serif;padding:5px 12px;border-radius:999px;"
                 "background:#1d6a55;color:#fff;text-decoration:none}"
                 "li.lec{color:#636a6e}li.lec.key{color:#b3261e;font-weight:700}li.extra,li.lec.extra{color:#0b57d0}"
                 "mark.pink{background:#fbdade}mark.blue{background:#d5e7fa}.disp{display:block;overflow-x:auto}"
                 "img{max-width:100%;height:auto}.tag{font-size:.72em;font-weight:700;padding:0 6px;margin-right:4px;"
                 "border:1px solid currentColor;border-radius:999px}.tag.imp{background:#b3261e;color:#fff;border-color:#b3261e}</style>")
    observer = """<script>
(function () {
  let t = null;
  const run = () => { if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([document.body]).catch(() => {}); };
  new MutationObserver(() => { clearTimeout(t); t = setTimeout(run, 120); }).observe(document.body, { childList: true, subtree: true });
})();
</script>"""
    nav = ('<nav class="mm-nav" aria-label="다른 페이지"><a href="index.html">처음</a><a href="guide.html">스터디 가이드</a>'
           '<a href="exam.html">모의고사</a><a href="note.html">정리 노트</a></nav>')
    # 프린트용 내려받기: 아티팩트에서는 downloads 기능으로, 그 밖(파일로 열었을 때)에서는 링크로
    dl_css = ("<style>.mm-dl{position:fixed;left:12px;bottom:12px;z-index:50;display:flex;gap:6px;flex-wrap:wrap;align-items:center;"
              "font:14px/1.4 'IBM Plex Sans KR',sans-serif;background:#fff;border:1px solid #c9d3ce;border-radius:10px;padding:8px 10px;"
              "box-shadow:0 1px 4px rgba(0,0,0,.12)}.mm-dl b{color:#1d6a55}.mm-dl button,.mm-dl a{font:inherit;padding:5px 12px;"
              "border-radius:999px;border:1px solid #1d6a55;background:#1d6a55;color:#fff;cursor:pointer;text-decoration:none}"
              ".mm-dl .alt{background:#fff;color:#1d6a55}.mm-dl small{color:#5b6662}</style>")
    dl = ('<div class="mm-dl" role="group" aria-label="프린트용 내려받기"><b>프린트용</b>'
          '<small>A3 가로 · 내용|빈칸|내용|빈칸 · 결론 상자·예시 제외</small>'
          '<button type="button" id="dlPdf" hidden>PDF 내려받기</button>'
          '<button type="button" id="dlHtml" class="alt" hidden>인쇄용 HTML 내려받기</button>'
          '<a id="lnPdf" href="mindmap_print.pdf">PDF 열기</a>'
          '<a id="lnHtml" class="alt" href="mindmap_print.html">인쇄용 화면 열기</a>'
          '<small id="dlMsg" aria-live="polite"></small></div>')
    dl_js = """<script>
(async function () {
  const msg = t => { document.getElementById('dlMsg').textContent = t; };
  const c = window.claude;
  if (!c || !c.use) return;
  let downloads = null;
  try { downloads = await c.use('downloads'); } catch (e) { downloads = null; }
  if (!downloads) return;
  document.getElementById('lnPdf').hidden = true;
  document.getElementById('lnHtml').hidden = true;
  const save = async (url, filename) => {
    msg('준비 중…');
    try {
      const r = await fetch(url);
      if (!r.ok) throw new Error('파일을 읽지 못했습니다');
      const blob = await r.blob();
      await downloads.save({ filename, data: blob });
      msg('저장했습니다');
    } catch (e) {
      msg(e && e.code === 'declined' ? '취소했습니다' : '내려받지 못했습니다: ' + ((e && (e.message || e.code)) || ''));
    }
  };
  const bp = document.getElementById('dlPdf'), bh = document.getElementById('dlHtml');
  bp.hidden = false; bh.hidden = false;
  bp.addEventListener('click', () => save('mindmap_print.pdf', '" + COURSE + "_마인드맵_프린트_A3.pdf'));
  bh.addEventListener('click', () => save('mindmap_print.html', '" + COURSE + "_마인드맵_프린트_A3.html'));
})();
</script>"""
    # 구조도 템플릿은 </head>·</body>를 생략하므로 <title> 뒤와 문서 끝에 붙인다
    head_add = MATHJAX + extra_css + dl_css
    if "</head>" in h:
        h = h.replace("</head>", head_add + "</head>", 1)
    else:
        h = re.sub(r"(</title>)", lambda m: m.group(1) + head_add, h, count=1)
    body_add = nav + dl + observer + dl_js
    h = h.replace("</body>", body_add + "</body>", 1) if "</body>" in h else h.rstrip() + body_add + "\n"
    assert "tex-svg" in h and "mm-dl" in h
    open(out_html, "w", encoding="utf-8").write(h)


def build_index(nq):
    cards = []
    if HAVE.get("guide.html"):
        cards.append('<a class="card" href="guide.html"><b>스터디 가이드</b><span>장별 교재 핵심 → 교수 강조 → 함정, 공식·숫자 모음, 시험 직전 체크리스트</span></a>')
    if HAVE.get("exam.html"):
        cards.append(f'<a class="card" href="exam.html"><b>모의고사 {nq}문항</b><span>정답 · 풀이 · 관련 설명 · 노트 원문을 하나씩 펼쳐 보기, 스스로 채점</span></a>')
    if HAVE.get("mindmap.html"):
        cards.append('<a class="card" href="mindmap.html"><b>마인드맵</b><span>개념 상하관계를 왼쪽 → 오른쪽으로 펼친 키워드 구조도, 프린트용 내려받기</span></a>')
    if HAVE.get("note.html"):
        cards.append('<a class="card" href="note.html"><b>정리 노트</b><span>강의자료·필기·판서·녹음을 모두 담은 원본 노트, 그래프 그림 포함</span></a>')
    body = f"""<div class="body">
<h1>{html.escape(TITLE)} 공부 세트</h1>
<p class="facts">{html.escape(SCOPE)}</p>
<div class="cards">{"".join(cards)}</div>
<h2 id="how">추천 순서</h2>
<ul>
<li>마인드맵으로 전체 구조를 훑기 → 스터디 가이드로 장별 핵심과 교수 강조 확인 → 모의고사를 풀고 틀린 문제의 '노트 원문'으로 복습</li>
<li>모의고사의 스스로 채점 결과는 이 브라우저에만 기억됩니다 (다른 기기에는 넘어가지 않음)</li>
</ul>
<h2 id="legend">색 표시</h2>
<div class="legend"><span>검정 = 강의자료</span><span class="tag hw">필기</span><span class="tag board">판서</span>
<span style="color:var(--lec)">회색 = 강의 녹음</span><span style="color:var(--imp);font-weight:700">빨강 = 교수 강조</span>
<span style="color:var(--ext)">파랑 = 자료에 없음</span><span style="color:var(--sol)">초록 = 풀이</span>
<mark>핵심</mark><mark class="pink">헷갈림</mark><mark class="blue">반대편</mark></div>
</div>"""
    open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(
        page(f"{TITLE} 공부 세트", "index.html", body, single=True))


def main():
    global ROOT, WEB, NOTE, GUIDE, EXAM, CONCEPTS, MINDMAP_MD, TITLE, COURSE, SCOPE, NOTE_ALL
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".", help="과목 폴더")
    ap.add_argument("--prefix", required=True, help='파일 이름 앞부분, 예: "화폐금융론_1강~8강_"')
    ap.add_argument("--title", required=True, help='사이트 제목, 예: "화폐금융론 중간고사"')
    ap.add_argument("--course", default="", help="과목 이름 (기본: prefix의 첫 낱말)")
    ap.add_argument("--scope", default="", help="첫 화면에 쓸 범위 설명 한 줄")
    ap.add_argument("--concepts", default="", help="마인드맵 데이터 파일(tools/concepts*.py)")
    ap.add_argument("--mindmap-md", default="", help="마인드맵 .md 출력 경로")
    ap.add_argument("--single-file", action="store_true", help="그림을 넣은 한 파일짜리 페이지도 만든다 (claude.ai·휴대폰용)")
    ap.add_argument("--out-dir", default="", help="--single-file 결과 폴더 (기본: web/single)")
    ap.add_argument("--note-all", action="store_true", help="정리 노트를 과(강의자료)별로 나누지 않고 한 페이지에 전부")
    a = ap.parse_args()
    ROOT = os.path.abspath(a.dir)
    WEB = os.path.join(ROOT, "web")
    NOTE = os.path.join(ROOT, a.prefix + "study note.md")
    GUIDE = os.path.join(ROOT, a.prefix + "스터디가이드.md")
    EXAM = os.path.join(ROOT, a.prefix + "모의고사.md")
    CONCEPTS = os.path.abspath(a.concepts) if a.concepts else ""
    MINDMAP_MD = os.path.abspath(a.mindmap_md) if a.mindmap_md else os.path.join(ROOT, a.prefix + "마인드맵.md")
    TITLE, SCOPE = a.title, a.scope
    NOTE_ALL = a.note_all
    COURSE = a.course or a.prefix.split("_")[0]
    if not os.path.exists(NOTE):
        raise SystemExit("study note가 없습니다: " + NOTE)
    HAVE.update({"note.html": True, "guide.html": os.path.exists(GUIDE), "exam.html": os.path.exists(EXAM),
                 "mindmap.html": bool(CONCEPTS)})
    os.makedirs(WEB, exist_ok=True)
    img_src, img_dst = os.path.join(ROOT, "images"), os.path.join(WEB, "images")
    if os.path.isdir(img_dst):
        shutil.rmtree(img_dst)
    if os.path.isdir(img_src):
        shutil.copytree(img_src, img_dst)
    build_note()
    if HAVE["guide.html"]:
        build_guide()
    nq = build_exam() if HAVE["exam.html"] else 0
    if HAVE["mindmap.html"]:
        build_mindmap()
    build_index(nq)
    if a.single_file:
        make_single_files(a.out_dir or os.path.join(WEB, "single"))
    for f in sorted(os.listdir(WEB)):
        p = os.path.join(WEB, f)
        if os.path.isfile(p):
            print(f, os.path.getsize(p))


def make_single_files(out_dir):
    """그림을 data URI로 넣은 한 파일짜리 페이지들 (claude.ai·휴대폰에서 파일 하나만 열어도 그림이 보이게).
    페이지끼리의 링크(guide.html 등)는 같은 폴더에 함께 두면 그대로 작동한다."""
    import base64
    import mimetypes
    os.makedirs(out_dir, exist_ok=True)
    cache = {}

    def data_uri(m):
        rel = m.group(2)
        p = os.path.join(WEB, rel)
        if rel not in cache and os.path.exists(p):
            mime = mimetypes.guess_type(p)[0] or "image/png"
            cache[rel] = f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()
        return m.group(1) + cache.get(rel, rel) + m.group(3)

    for f in os.listdir(WEB):
        if f.endswith(".html"):
            h = open(os.path.join(WEB, f), encoding="utf-8").read()
            h = re.sub(r'(src=")(images/[^"]+)(")', data_uri, h)
            # 마인드맵 노트 원문은 JSON 안에 들어 있어 따옴표가 \" 로 escape됨
            h = re.sub(r'(src=\\")(images/[^"\\]+)(\\")', data_uri, h)
            open(os.path.join(out_dir, f), "w", encoding="utf-8").write(h)
    pdf = os.path.join(WEB, "mindmap_print.pdf")
    if os.path.exists(pdf):
        shutil.copy(pdf, out_dir)
    print("single-file pages →", out_dir)


if __name__ == "__main__":
    main()
