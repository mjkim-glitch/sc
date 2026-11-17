"""마인드맵(개념 구조도) 빌드: 웹 페이지(수식 = MathJax), .md(수식 = 유니코드 글자), 프린트용(A3 가로, 세로 4칸 = 내용|빈칸|내용|빈칸, 장은 새 쪽에서 시작).

concepts 파일 라벨의 $...$ 는 LaTeX. 통화는 \\$.
프린트용에서는 회색 결론 상자(z)와 예시 노드(a="예", 그 아래 가지 포함)를 뺀다.
"""
import copy
import html
import importlib.util
import os
import re
import runpy
import sys

SKILL = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL)
MATH = re.compile(r"(?<!\\)\$(.+?)(?<!\\)\$")


def load_concepts(path):
    spec = importlib.util.spec_from_file_location("concepts_src", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------- LaTeX → 유니코드 (.md·Mermaid용) ----------
SUB = dict(zip("0123456789+-=()aehijklmnoprstuvx", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ"))
SUP = dict(zip("0123456789+-=()abdeghijklmnoprstuvwxyz*", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ᵃᵇᵈᵉᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ*"))
CMD = {"pi": "π", "theta": "θ", "beta": "β", "rho": "ρ", "sigma": "σ", "varepsilon": "ε", "infty": "∞",
       "times": "×", "div": "÷", "approx": "≈", "Rightarrow": "⇒", "neq": "≠", "cdots": "⋯", "log": "log",
       "Pr": "Pr", "le": "≤", "ge": "≥", "to": "→", "cdot": "·", "%": "%"}


def _group(s, i):
    """s[i] 위치의 {…} 또는 한 글자(\\명령 포함)를 읽어 (내용, 다음 위치)."""
    if i >= len(s):
        return "", i
    if s[i] == "{":
        depth, j = 0, i
        while j < len(s):
            if s[j] == "{":
                depth += 1
            elif s[j] == "}":
                depth -= 1
                if depth == 0:
                    return s[i + 1:j], j + 1
            j += 1
        return s[i + 1:], len(s)
    if s[i] == "\\":
        m = re.match(r"\\([A-Za-z]+|.)", s[i:])
        return m.group(0), i + len(m.group(0))
    return s[i], i + 1


def _script(text, table, mark):
    t = tex2uni(text)
    if t and all(ch in table for ch in t):
        return "".join(table[ch] for ch in t)
    return f"{mark}({t})" if len(t) > 1 else f"{mark}{t}"


def tex2uni(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", s[i:])
            name = m.group(1)
            i += len(m.group(0))
            if name in ("frac", "dfrac", "tfrac"):
                a, i = _group(s, i)
                b, i = _group(s, i)
                a, b = tex2uni(a), tex2uni(b)
                def wrap(x):
                    if re.fullmatch(r"\([^()]*\)\S*", x) and not re.search(r"[ +\-−×·]", re.sub(r"^\([^()]*\)", "", x)):
                        return x
                    return f"({x})" if re.search(r"[ +\-−×·]", x) else x
                out.append(f"{wrap(a)}/{wrap(b)}")
            elif name == "text":
                a, i = _group(s, i)
                out.append(a)
            elif name == "sum":
                out.append("Σ")
            elif name in (",", ";", " ", "quad", "qquad"):
                out.append(" ")
            elif name in ("!", "left", "right"):
                pass
            elif name in CMD:
                out.append(CMD[name])
            else:
                out.append(name)
        elif c in "_^":
            g, i = _group(s, i + 1)
            out.append(_script(g, SUB if c == "_" else SUP, c))
        elif c == "{":
            g, i = _group(s, i)
            out.append(tex2uni(g).replace(",", ",") if g != "," else ",")
        elif c == "-":
            out.append("−")
            i += 1
        else:
            out.append(c)
            i += 1
    return re.sub(r" {2,}", " ", "".join(out))


# ---------- 변환 ----------
def map_strings(tree, fn):
    t = copy.deepcopy(tree)

    def walk(n):
        for k in ("t", "d", "z"):
            n[k] = fn(n[k])
        for c in n["c"]:
            walk(c)
    walk(t)
    return t


def to_html_str(s):
    s = MATH.sub(lambda m: "\\(" + m.group(1) + "\\)", s)
    return s.replace("\\$", "$")


def to_md_str(s):
    return MATH.sub(lambda m: tex2uni(m.group(1)), s)


def write_variant(m, chapters, path):
    lines = ["from structure_model import N  # noqa", "# 자동 생성 파일 (tools/mindmap_build.py) — 직접 고치지 말 것"]
    for name in ("COURSE", "RANGE", "LEDE_EXTRA", "LINKS", "TITLES", "TABS", "ORDER"):
        if hasattr(m, name):
            lines.append(f"{name} = {getattr(m, name)!r}")
    lines.append(f"CHAPTERS = {chapters!r}")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def run_structure(note, concepts, out_html, out_md):
    argv = sys.argv
    sys.argv = ["build_structure.py", "--note", note, "--concepts", concepts, "--html", out_html, "--md", out_md]
    try:
        runpy.run_path(os.path.join(SKILL, "build_structure.py"), run_name="__main__")
    finally:
        sys.argv = argv


# ---------- 프린트용 ----------
PRINT_CSS = r"""
/* A3 가로 한 쪽을 세로 4칸으로: 내용 | 빈칸 | 내용 | 빈칸 (칸마다 105mm) */
@page { size: A3 landscape; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; }
body { font-family: "IBM Plex Sans KR", "Malgun Gothic", sans-serif; line-height: 1.3; color: #111; }
.screen-tip { font-size: 14px; background: #fff7d6; border: 1px solid #e3cf7a; padding: 10px 14px; margin: 12px; border-radius: 6px; max-width: 900px; line-height: 1.6; }
.page { width: 420mm; height: 297mm; display: flex; overflow: hidden; break-after: page; page-break-after: always; background: #fff; }
.page:last-child { break-after: auto; page-break-after: auto; }
.col { width: 105mm; height: 297mm; padding: 10mm 4mm 10mm 8mm; overflow: hidden; font-size: 9.6pt; }
.blank { width: 105mm; height: 297mm; }
@media screen { body { background: #e9ece9; } .page { margin: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.25); } .blank { border-left: 1px dashed #d5dcd8; border-right: 1px dashed #d5dcd8; } }
@media print { .screen-tip { display: none; } }
#src { position: absolute; left: -2000mm; top: 0; width: 93mm; visibility: hidden; font-size: 9.6pt; }
.chead { font-size: 11.5pt; font-weight: 700; color: #1d6a55; border-bottom: 1.2pt solid #1d6a55; padding-bottom: 1mm; margin-bottom: 2.2mm; }
.chead.cont { font-size: 9.5pt; border-bottom-width: 0.6pt; }
.chead small { display: block; font-size: 6.8pt; font-weight: 400; color: #666; margin-top: 0.5mm; }
ul.tree, ul.tree ul { list-style: none; margin: 0; padding: 0; }
ul.tree ul { margin-left: 0.36em; padding-left: 0.95em; border-left: 0.6pt solid #9aa5a0; }
ul.tree li { position: relative; margin: calc(0.16em + var(--g, 0px)) 0 0; }
ul.tree ul > li::before { content: ""; position: absolute; left: -0.95em; top: 0.66em; width: 0.75em; border-top: 0.6pt solid #9aa5a0; }
.lab { display: inline; }
.d1 > .lab { font-weight: 700; font-size: 1.1em; }
.d2 > .lab { font-weight: 700; }
.key > .lab { color: #9b1c14; }
.nb { font-weight: 700; color: #1d6a55; margin-right: 0.25em; }
.star { color: #b7791f; margin-right: 0.1em; }
.chip { font-size: 0.8em; color: #1d6a55; border: 0.5pt solid #1d6a55; border-radius: 3pt; padding: 0 0.3em; margin-left: 0.3em; }
.atag { font-size: 0.8em; color: #555; border: 0.5pt dashed #777; border-radius: 3pt; padding: 0 0.3em; margin-right: 0.3em; }
.cont { font-size: 0.8em; color: #777; font-weight: 400; }
mjx-container { font-size: 105% !important; }
"""

MATHJAX = """<script>
window.MathJax = { tex: { inlineMath: [['\\\\(', '\\\\)']] }, svg: { fontCache: 'local' } };
</script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.min.js"></script>"""

# 배치: 가지(부모 + 아래 노드 전체)를 한 단에 통째로 넣고, 안 들어가면 다음 단으로.
# 한 단보다 큰 가지만 나누며, 다음 단 위에 부모 이름을 "(계속)"으로 다시 적는다. 장(대제목)은 새 쪽에서 시작.
# 다 넣은 뒤 단마다 남는 높이를 노드 사이 간격으로 나눠 채운다.
PACK_JS = """<script>
window.addEventListener('load', async () => {
  try { if (document.fonts && document.fonts.ready) await document.fonts.ready; } catch (e) {}
  try { if (window.MathJax && MathJax.startup && MathJax.startup.promise) await MathJax.startup.promise; } catch (e) {}
  const src = document.getElementById('src'), out = document.getElementById('out');
  const META = src.dataset.meta;
  let page = null, slot = 1, col = null;
  const parse = li => ({ li, kids: [...((li.querySelector(':scope > ul') || {}).children || [])].map(parse), started: false });
  const fits = () => col.scrollHeight <= col.clientHeight + 0.5;
  function newPage() {
    page = document.createElement('section'); page.className = 'page';
    for (let i = 0; i < 2; i++) {
      const c = document.createElement('div'); c.className = 'col';
      const b = document.createElement('div'); b.className = 'blank';
      page.append(c, b);
    }
    out.appendChild(page); slot = -1;
  }
  function nextCol(title, cont, forcePage) {
    slot++;
    if (!page || slot > 1 || forcePage) { newPage(); slot = 0; }
    col = page.querySelectorAll('.col')[slot];
    const h = document.createElement('div');
    h.className = cont ? 'chead cont' : 'chead';
    h.textContent = title + (cont ? ' (계속)' : '');
    if (!cont) { const s = document.createElement('small'); s.textContent = META; h.appendChild(s); }
    const ul = document.createElement('ul'); ul.className = 'tree';
    col.append(h, ul);
    col._chain = []; col._root = ul; col._has = false;
  }
  function labelOnly(n, cont) {
    const li = document.createElement('li');
    li.className = n.li.className.replace(/\\bleaf\\b/, '').trim();
    for (const ch of n.li.childNodes) if (ch.nodeName !== 'UL') li.appendChild(ch.cloneNode(true));
    if (cont) { const s = document.createElement('span'); s.className = 'cont'; s.textContent = ' (계속)'; li.appendChild(s); }
    return li;
  }
  function full(n) {
    const li = labelOnly(n, false);
    if (n.kids.length) { const ul = document.createElement('ul'); n.kids.forEach(k => ul.appendChild(full(k))); li.appendChild(ul); }
    return li;
  }
  function ensure(path, made) {
    const ch = col._chain;
    let i = 0;
    while (i < ch.length && i < path.length && ch[i].n === path[i]) i++;
    ch.length = i;
    let ul = i ? ch[i - 1].ul : col._root;
    for (; i < path.length; i++) {
      const n = path[i];
      const li = labelOnly(n, n.started);
      const sub = document.createElement('ul');
      li.appendChild(sub); ul.appendChild(li);
      made.push({ li, n, prev: n.started });
      n.started = true;
      ch.push({ n, ul: sub });
      ul = sub;
    }
    return ul;
  }
  function rollback(made) {
    for (let k = made.length - 1; k >= 0; k--) { made[k].li.remove(); made[k].n.started = made[k].prev; }
    col._chain.length = Math.max(0, col._chain.length - made.length);
  }
  function place(n, path, title) {
    let made = [], ul = ensure(path, made);
    const li = full(n);
    ul.appendChild(li);
    if (fits()) { col._has = true; return; }
    li.remove(); rollback(made);
    if (col._has) {
      nextCol(title, true);
      made = []; ul = ensure(path, made); ul.appendChild(li);
      if (fits()) { col._has = true; return; }
      li.remove(); rollback(made);
    }
    if (!n.kids.length) { ensure(path, []).appendChild(li); col._has = true; return; }
    made = []; ensure(path.concat([n]), made);
    if (!fits()) { rollback(made); nextCol(title, true); ensure(path.concat([n]), []); }
    col._has = true;
    n.kids.forEach(k => place(k, path.concat([n]), title));
  }
  for (const chap of src.querySelectorAll(':scope > .chap')) {
    const title = chap.dataset.title;
    nextCol(title, false, true);
    const root = parse(chap.querySelector(':scope > ul > li'));
    place(root, [], title);
  }
  // 남는 높이를 노드 사이 간격으로
  document.querySelectorAll('#out .col').forEach(c => {
    if (!c.querySelector('li')) return;
    col = c;
    let lo = 0, hi = 90;
    for (let k = 0; k < 14; k++) {
      const mid = (lo + hi) / 2;
      c.style.setProperty('--g', mid + 'px');
      if (fits()) lo = mid; else hi = mid;
    }
    c.style.setProperty('--g', lo.toFixed(2) + 'px');
    c.dataset.gap = lo.toFixed(1);
  });
  src.remove();
  document.body.dataset.fit = 'done';
});
</script>"""


def numbered(n):
    """g(묶음)가 있는 노드의 자식 중 보조(a) 아닌 것에 1, 2, 3 번호."""
    if n["g"]:
        k = 0
        for c in n["c"]:
            if not c["a"]:
                k += 1
                c["_n"] = k
    for c in n["c"]:
        numbered(c)


def print_html(chapters, titles, course, rng):
    def node(n, depth):
        if n["a"] == "예":
            return ""
        lab = html.escape(n["t"], quote=False)
        pre = ""
        if n.get("_n"):
            pre += f'<span class="nb">{n["_n"]})</span>'
        if n["a"]:
            pre += f'<span class="atag">{html.escape(n["a"])}</span>'
        if n["k"]:
            pre += '<span class="star">★</span>'
        chip = f'<span class="chip">{html.escape(n["g"])}</span>' if n["g"] else ""
        kids = "".join(node(c, depth + 1) for c in n["c"])
        kids = f"<ul>{kids}</ul>" if kids else ""
        cls = f'd{min(depth, 3)}{" key" if n["k"] else ""}{"" if kids else " leaf"}'
        return f'<li class="{cls}">{pre}<span class="lab">{lab}</span>{chip}{kids}</li>'

    meta = f"{course} {rng} 마인드맵 · 결론 상자·예시 제외 · ★ 교수 강조 · 1) 2) 핵심 구성원"
    chaps = []
    for cid, tree in chapters:
        t = copy.deepcopy(tree)
        numbered(t)
        chaps.append(f'<div class="chap" data-title="{html.escape(titles.get(cid, cid))}"><ul class="tree">{node(t, 1)}</ul></div>')
    tip = ('<div class="screen-tip"><b>인쇄 방법</b>: Ctrl+P → 용지 <b>A3</b>, 레이아웃 <b>가로</b>, 여백 <b>없음</b>(또는 기본값), '
           '배율 <b>100%(실제 크기)</b> → 인쇄. 쪽마다 세로 4칸이 <b>내용 | 빈칸 | 내용 | 빈칸</b>이고, 장(대제목)은 새 쪽에서 시작합니다. '
           '부모 노드와 그 아래 가지는 같은 칸에 두고, 한 칸보다 큰 가지만 다음 칸으로 이어 "(계속)"을 붙입니다. (이 안내문은 인쇄되지 않습니다)</div>')
    fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;700&display=swap" rel="stylesheet">')
    return (f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{html.escape(course)} 마인드맵 프린트용 (A3)</title>{fonts}<style>{PRINT_CSS}</style>{MATHJAX}{PACK_JS}</head>'
            f'<body>{tip}<div id="src" data-meta="{html.escape(meta)}">{"".join(chaps)}</div><div id="out"></div></body></html>')


def chapter_titles(note):
    titles = {}
    for l in open(note, encoding="utf-8"):
        m = re.match(r"^# (\d)\. (.*)$", l)
        if m:
            titles[m.group(1)] = f"{m.group(1)}. {m.group(2).strip()}"
    return titles


def build(note, concepts_src, out_html, out_md, out_print, tmp_dir):
    m = load_concepts(concepts_src)
    html_ch = [(cid, map_strings(t, to_html_str)) for cid, t in m.CHAPTERS]
    md_ch = [(cid, map_strings(t, to_md_str)) for cid, t in m.CHAPTERS]
    os.makedirs(tmp_dir, exist_ok=True)
    c_html = os.path.join(tmp_dir, "_concepts_html.py")
    c_md = os.path.join(tmp_dir, "_concepts_md.py")
    write_variant(m, html_ch, c_html)
    write_variant(m, md_ch, c_md)
    run_structure(note, c_html, out_html, os.path.join(tmp_dir, "_discard.md"))
    run_structure(note, c_md, os.path.join(tmp_dir, "_discard.html"), out_md)
    titles = chapter_titles(note)
    open(out_print, "w", encoding="utf-8").write(
        print_html(html_ch, titles, getattr(m, "COURSE", ""), getattr(m, "RANGE", "")))
