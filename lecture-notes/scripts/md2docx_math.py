"""md2docx (lecture-notes skill) + LaTeX 수식 → Word 수식(OMML).

- 인라인 $...$ → 문장 안 Word 수식, 한 줄 전체가 $$...$$ → 가운데 정렬 별도 수식 문단(분수가 크게 보임)
- 통화 표기 \\$ 는 글자 $ 로 바꾼다.
- 수식 글자 크기: 인라인 10pt, 별도 줄 11pt (본문 9pt보다 크게)

Usage: python md2docx_math.py 입력.md 출력.docx
"""
import copy
import os
import re
import sys

SKILL = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL)
import md2docx as base  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.shared import Cm  # noqa: E402
from lxml import etree  # noqa: E402
from latex2mathml.converter import convert as tex2mml  # noqa: E402

# 수식 변환기: ① Windows의 Office XSL(MathML → OMML)  ② 없으면 pandoc(pip install pypandoc_binary, 어느 OS든)
XSL_CANDIDATES = [r"C:/Program Files/Microsoft Office/root/Office16/MML2OMML.XSL",
                  r"C:/Program Files (x86)/Microsoft Office/root/Office16/MML2OMML.XSL",
                  r"C:/Program Files/Microsoft Office/Office16/MML2OMML.XSL"]
_xslt = None
if not os.environ.get("LN_FORCE_PANDOC"):
    for _p in XSL_CANDIDATES:
        if os.path.exists(_p):
            _xslt = etree.XSLT(etree.parse(_p))
            break
_PANDOC = {}  # 전처리한 tex → m:oMath (pandoc 경로)
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
INLINE_PT, DISPLAY_PT, FRAC_PT = 10, 11, 13

MATH_RE = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$|(?<!\\)\$(.+?)(?<!\\)\$")


def _prep(tex):
    # Word 변환이 \underbrace의 괄호를 잃으므로 "식 (아래 글자)"로, 아래 화살표는 옆 화살표로 바꾼다
    tex = re.sub(r"\\underbrace\{((?:[^{}]|\{[^{}]*\})*)\}_\{((?:[^{}]|\{[^{}]*\})*)\}",
                 r"\1\\ (\2)", tex)
    tex = re.sub(r"\\underset\{(\\(?:downarrow|uparrow))\}\{((?:[^{}]|\{[^{}]*\})*)\}", r"\2\1", tex)
    # Word 변환(XSL)이 mspace를 버리므로 간격 명령은 공백 글자로 바꾼다
    tex = (tex.replace("\\qquad", "\\ \\ \\ \\ ").replace("\\quad", "\\ \\ ")
           .replace("\\;", "\\ ").replace("\\:", "\\ "))
    return tex.strip()


def pandoc_batch(texs):
    """Office XSL이 없을 때: 수식 묶음을 pandoc으로 한 번에 docx로 만들어 m:oMath를 순서대로 꺼낸다."""
    import tempfile
    import zipfile
    import pypandoc
    todo = [t for t in dict.fromkeys(_prep(x) for x in texs) if t and t not in _PANDOC]
    if not todo:
        return
    d = tempfile.mkdtemp()
    src, out = os.path.join(d, "m.md"), os.path.join(d, "m.docx")
    open(src, "w", encoding="utf-8").write("\n\n".join(f"${t}$" for t in todo))
    pypandoc.convert_file(src, "docx", format="markdown", outputfile=out)
    doc = etree.fromstring(zipfile.ZipFile(out).read("word/document.xml"))
    paras = [p for p in doc.iter("{%s}p" % W_NS)]
    for t, p in zip(todo, paras):
        om = p.find(".//{%s}oMath" % M_NS)
        _PANDOC[t] = om


def _plain(tex):
    """변환 실패 시: 수식 글자를 그대로 넣는다(깨진 수식 대신 원문이 보이게)."""
    om = etree.Element("{%s}oMath" % M_NS)
    r = etree.SubElement(om, "{%s}r" % M_NS)
    etree.SubElement(r, "{%s}t" % M_NS).text = tex
    return om


def omml(tex, size_pt, display=False):
    tex = _prep(tex)
    if _xslt is not None:
        mml = tex2mml(tex, display="block" if display else "inline")
        tree = etree.fromstring(mml.encode("utf-8"))
        om = _xslt(tree).getroot()
    else:
        if tex not in _PANDOC:
            try:
                pandoc_batch([tex])
            except Exception as e:  # noqa: BLE001
                print("pandoc 수식 변환 실패:", e, file=sys.stderr)
        src = _PANDOC.get(tex)
        om = copy.deepcopy(src) if src is not None else _plain(tex)
    # 글자 크기·글꼴
    for r in om.iter("{%s}r" % M_NS):
        rpr = r.find("{%s}rPr" % W_NS)
        if rpr is None:
            rpr = etree.SubElement(r, "{%s}rPr" % W_NS)
            # w:rPr 는 m:rPr 다음, m:t 앞에 와야 한다
            r.remove(rpr)
            t = r.find("{%s}t" % M_NS)
            r.insert(list(r).index(t) if t is not None else len(r), rpr)
        fonts = etree.SubElement(rpr, "{%s}rFonts" % W_NS)
        for a in ("ascii", "hAnsi", "eastAsia", "cs"):
            fonts.set("{%s}%s" % (W_NS, a), "Cambria Math" if a != "eastAsia" else "맑은 고딕")
        # 문장 속 분수는 Word가 작게 줄이므로 분자·분모 글자를 키워 본문 크기에 맞춘다
        in_frac = not display and any(a.tag == "{%s}f" % M_NS for a in r.iterancestors())
        for tag in ("sz", "szCs"):
            e = etree.SubElement(rpr, "{%s}%s" % (W_NS, tag))
            e.set("{%s}val" % W_NS, str((FRAC_PT if in_frac else size_pt) * 2))
    # 수식 영역의 기준 글자 크기: 분수로 시작하는 수식도 본문 크기를 기준으로 삼게 한다
    for pr in om.iter("{%s}fPr" % M_NS):
        ctrl = etree.SubElement(pr, "{%s}ctrlPr" % M_NS)
        rpr = etree.SubElement(ctrl, "{%s}rPr" % W_NS)
        etree.SubElement(rpr, "{%s}rFonts" % W_NS).set("{%s}ascii" % W_NS, "Cambria Math")
        for tag in ("sz", "szCs"):
            etree.SubElement(rpr, "{%s}%s" % (W_NS, tag)).set("{%s}val" % W_NS, str(size_pt * 2))
    return om


_orig_add_inline = base.add_inline


PH = re.compile("(\\d+)")


def style_math(om, bold, color, hl):
    """수식 글자에도 문단의 굵게·색·형광펜을 입힌다."""
    for rpr in om.iter("{%s}rPr" % W_NS):
        # 스키마 순서: rFonts, b, color, sz, szCs, highlight, shd
        sz = rpr.find("{%s}sz" % W_NS)
        at = list(rpr).index(sz) if sz is not None else len(rpr)
        if color is not None:
            c = etree.Element("{%s}color" % W_NS)
            c.set("{%s}val" % W_NS, str(color))
            rpr.insert(at, c)
        if bold:
            rpr.insert(at, etree.Element("{%s}b" % W_NS))
        if hl == "노랑":
            etree.SubElement(rpr, "{%s}highlight" % W_NS).set("{%s}val" % W_NS, "yellow")
        elif hl in base.SHADE:
            s = etree.SubElement(rpr, "{%s}shd" % W_NS)
            s.set("{%s}val" % W_NS, "clear")
            s.set("{%s}fill" % W_NS, base.SHADE[hl])
    if bold:
        for r in om.iter("{%s}r" % M_NS):
            mrpr = r.find("{%s}rPr" % M_NS)
            if mrpr is None:
                mrpr = etree.Element("{%s}rPr" % M_NS)
                r.insert(0, mrpr)
            etree.SubElement(mrpr, "{%s}sty" % M_NS).set("{%s}val" % M_NS, "bi")


def add_inline(par, text, bold_all=False, color=None):
    """수식은 자리표시로 바꿔 두고 굵게·형광펜 구간을 전체 글 기준으로 나눈 뒤, 수식 자리에 OMML을 넣는다."""
    maths = []

    def keep(m):
        maths.append(m.group(1) if m.group(1) is not None else m.group(2))
        return "%d" % (len(maths) - 1)
    body = MATH_RE.sub(keep, text)
    if not maths:
        return _orig_add_inline(par, text.replace("\\$", "$"), bold_all, color)
    body = base.LINK_RE.sub(lambda m: m.group(1), body).replace("`", "")
    pcolor, pbold = base.para_style(text)
    color = color or pcolor
    for s, bold, hl in base.segments(body):
        pos = 0
        for m in PH.finditer(s):
            chunk = s[pos:m.start()].replace("\\$", "$")
            if chunk:
                r = par.add_run(chunk)
                r.bold = True if (bold or bold_all or pbold) else None
                r.font.color.rgb = color
                if hl == "노랑":
                    r.font.highlight_color = base.WD_COLOR_INDEX.YELLOW
                elif hl in base.SHADE:
                    base.shade(r, base.SHADE[hl])
            om = copy.deepcopy(omml(maths[int(m.group(1))], INLINE_PT))
            style_math(om, bold or bold_all or pbold, color, hl)
            par._p.append(om)
            pos = m.end()
        chunk = s[pos:].replace("\\$", "$")
        if chunk:
            r = par.add_run(chunk)
            r.bold = True if (bold or bold_all or pbold) else None
            r.font.color.rgb = color
            if hl == "노랑":
                r.font.highlight_color = base.WD_COLOR_INDEX.YELLOW
            elif hl in base.SHADE:
                base.shade(r, base.SHADE[hl])


base.add_inline = add_inline

_orig_convert = base.convert


def add_display(doc, tex, level=0):
    par = doc.add_paragraph()
    base.compact(par.paragraph_format, before=2, after=2)
    if level:
        par.paragraph_format.left_indent = Cm(0.4 * level)
    om = omml(tex, DISPLAY_PT, display=True)
    para = etree.SubElement(etree.Element("dummy"), "{%s}oMathPara" % M_NS)
    para.append(om)
    par._p.append(para)


def convert(md_path, out_path):
    """$$...$$ 만 있는 줄(불릿 포함)은 별도 수식 문단으로 바꿔 넣는다."""
    base_dir = os.path.dirname(os.path.abspath(md_path))
    lines = open(md_path, encoding="utf-8").read().splitlines()
    if _xslt is None:  # Office가 없으면 모든 수식을 pandoc으로 한 번에 변환해 둔다
        try:
            pandoc_batch([m.group(1) or m.group(2) for ln in lines for m in MATH_RE.finditer(ln)])
        except Exception as e:  # noqa: BLE001
            print("pandoc을 쓸 수 없어 수식을 글자로 넣습니다 (pip install pypandoc_binary):", e, file=sys.stderr)
    tmp = []
    marks = {}
    for ln in lines:
        m = re.match(r"^(\s*)(?:[-*+]\s+)?\$\$(.+)\$\$\s*$", ln)
        # 앞에 글이 있는 줄: "- 설명: $$수식$$" → 설명 문단 + 아래 별도 수식 문단
        m2 = None if m else re.match(r"^(\s*)([-*+]\s+)(.*?)\s*(?<!\\)\$\$(.+)\$\$\s*$", ln)
        if m:
            key = f"@@DISPLAY{len(marks)}@@"
            marks[key] = (m.group(2), base.indent_level(m.group(1)) if ln.lstrip()[:1] in "-*+" else 0)
            tmp.append(key)
        elif m2 and "$$" not in m2.group(3):
            tmp.append(m2.group(1) + m2.group(2) + m2.group(3))
            key = f"@@DISPLAY{len(marks)}@@"
            marks[key] = (m2.group(4), base.indent_level(m2.group(1)) + 1)
            tmp.append(key)
        else:
            tmp.append(ln)
    tmp_md = os.path.join(base_dir, "~math_tmp.md")
    open(tmp_md, "w", encoding="utf-8").write("\n".join(tmp))
    orig_paragraph = base.Document

    def patched_document(*a, **k):
        d = orig_paragraph(*a, **k)
        orig_add_par = d.add_paragraph

        def add_paragraph(text="", style=None):
            if isinstance(text, str) and text in marks:
                tex, lvl = marks[text]
                add_display(d, tex, lvl)
                return d.paragraphs[-1]
            return orig_add_par(text, style)
        d.add_paragraph = add_paragraph
        return d

    base.Document = patched_document
    # 표시 줄은 일반 문단으로 처리되므로 add_inline 경유가 아니라 add_paragraph(s) 경로를 타게 한다
    orig_inline = base.add_inline

    def inline_hook(par, text, bold_all=False, color=None):
        if text.strip() in marks:
            tex, lvl = marks[text.strip()]
            par._p.getparent().remove(par._p)
            add_display(par_doc[0], tex, lvl)
            return
        orig_inline(par, text, bold_all, color)
    par_doc = [None]
    orig_setup = base.setup

    def setup_hook(doc):
        par_doc[0] = doc
        orig_setup(doc)
    base.setup = setup_hook
    base.add_inline = inline_hook
    try:
        _orig_convert(tmp_md, out_path)
    finally:
        base.add_inline = orig_inline
        base.Document = orig_paragraph
        base.setup = orig_setup
        os.remove(tmp_md)


if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
    print("saved", sys.argv[2])
