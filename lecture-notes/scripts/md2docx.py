"""정리 노트 .md -> .docx (A4 세로, 2단, 여백 1.5cm, 맑은 고딕, 본문 9pt, 제목 10pt 굵게).

색 규칙 (문단 단위, 우선순위 빨강 > 파랑 > 회색 > 검정):
  [강의] … (중요)        -> 빨강 #C00000 굵게
  [강의] … (자료에 없음) -> 파랑 #0B57D0
  [강의]                 -> 회색 #595959
  [풀이]                 -> 초록 #2E7D32
  그 밖                  -> 검정
형광펜 (키워드 단위, 표시 문자는 지움):
  ==키워드==        -> 노랑 형광펜
  ==분홍:키워드==   -> 연한 분홍 음영 #FADADD
  ==파랑:키워드==   -> 연한 파랑 음영 #D6E8FA
불릿: 1단계 ▪, 2단계 ◦, 3단계 -

Usage: python md2docx.py 입력.md 출력.docx
"""
import os
import re
import sys
from urllib.parse import unquote

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_COLOR_INDEX
from docx.image.image import Image as DocxImage
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BODY_PT = 9
HEAD_PT = 10
FONT = "맑은 고딕"
MONO = "Consolas"
MARGIN_CM = 1.5
COL_GAP_CM = 0.6
COL_W_CM = (21.0 - 2 * MARGIN_CM - COL_GAP_CM) / 2

RED = RGBColor(0xC0, 0x00, 0x00)
BLUE = RGBColor(0x0B, 0x57, 0xD0)
GRAY = RGBColor(0x59, 0x59, 0x59)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
BLACK = RGBColor(0, 0, 0)
SHADE = {"분홍": "FADADD", "파랑": "D6E8FA"}
BULLETS = ["▪", "◦", "-"]

IMG_RE = re.compile(r"!\[[^\]]*\]\((<[^>]+>|[^)]+)\)")
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]*)\)")
TOKEN_RE = re.compile(r"\*\*|==")


def set_font(style_or_run, size, bold=None, name=FONT):
    f = style_or_run.font
    f.name = name
    f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    rpr = style_or_run.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name if attr != "w:eastAsia" else FONT)


def compact(pf, before=0, after=1):
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = 1.1


def setup(doc):
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Cm(MARGIN_CM))
    cols = sec._sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols")
        sec._sectPr.append(cols)
    cols.set(qn("w:num"), "2")
    cols.set(qn("w:space"), str(int(COL_GAP_CM / 2.54 * 1440)))

    styles = doc.styles
    for name in ("Normal", "Table Grid"):
        set_font(styles[name], BODY_PT)
    compact(styles["Normal"].paragraph_format)
    for name, before in (("Title", 0), ("Heading 1", 8), ("Heading 2", 6), ("Heading 3", 4)):
        st = styles[name]
        set_font(st, HEAD_PT, bold=True)
        st.font.italic = False
        st.font.color.rgb = BLACK
        compact(st.paragraph_format, before=before, after=2)
        st.paragraph_format.keep_with_next = True
    ppr = styles["Title"].element.find(qn("w:pPr"))
    if ppr is not None:
        bdr = ppr.find(qn("w:pBdr"))
        if bdr is not None:
            ppr.remove(bdr)


def para_style(text):
    """문단 표시를 보고 (색, 전체 굵게)를 정한다."""
    if "(중요)" in text and "[강의]" in text:
        return RED, True
    if "(자료에 없음)" in text:
        return BLUE, False
    if "[강의]" in text:
        return GRAY, False
    if "[풀이]" in text:
        return GREEN, False
    return BLACK, False


def shade(run, fill):
    rpr = run._r.get_or_add_rPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    rpr.append(shd)


def segments(text):
    """**굵게** / ==형광펜== 토큰을 (글자, 굵게, 형광펜 종류) 조각으로 나눈다."""
    out, bold, hl, pos = [], False, None, 0
    for m in TOKEN_RE.finditer(text):
        if m.group() == "**":
            # 짝이 없는 ** 는 글자로 둔다
            if not bold and "**" not in text[m.end():]:
                continue
            out.append((text[pos:m.start()], bold, hl))
            bold = not bold
            pos = m.end()
        else:
            if hl is None:
                if "==" not in text[m.end():]:
                    continue
                out.append((text[pos:m.start()], bold, hl))
                rest = text[m.end():]
                kind = next((k for k in SHADE if rest.startswith(k + ":")), None)
                hl = kind or "노랑"
                pos = m.end() + (len(kind) + 1 if kind else 0)
            else:
                out.append((text[pos:m.start()], bold, hl))
                hl = None
                pos = m.end()
    out.append((text[pos:], bold, hl))
    return [s for s in out if s[0]]


def add_inline(par, text, bold_all=False, color=None):
    text = LINK_RE.sub(lambda m: m.group(1), text)
    text = text.replace("`", "")
    pcolor, pbold = para_style(text)
    color = color or pcolor
    for s, bold, hl in segments(text):
        r = par.add_run(s)
        r.bold = True if (bold or bold_all or pbold) else None
        r.font.color.rgb = color
        if hl == "노랑":
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        elif hl in SHADE:
            shade(r, SHADE[hl])


def img_path(raw, base):
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1]
    return os.path.join(base, unquote(raw))


def add_images(doc, line, base):
    srcs = IMG_RE.findall(line)
    caption = IMG_RE.sub("", line).strip()
    par = doc.add_paragraph()
    compact(par.paragraph_format, before=2, after=0)
    max_w = COL_W_CM if len(srcs) == 1 else (COL_W_CM - 0.3) / 2
    for i, raw in enumerate(srcs):
        p = img_path(raw, base)
        if not os.path.exists(p):
            par.add_run(f"[이미지 없음: {os.path.basename(p)}] ")
            continue
        im = DocxImage.from_file(p)
        w_cm = min(im.px_width / 96 * 2.54, max_w)
        par.add_run().add_picture(p, width=Cm(w_cm))
        # 한 줄에 2장씩
        if i % 2 == 1 and i < len(srcs) - 1:
            par.add_run().add_break()
        elif i < len(srcs) - 1:
            par.add_run(" ")
    if caption:
        cp = doc.add_paragraph()
        compact(cp.paragraph_format, before=0, after=3)
        add_inline(cp, caption)


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def add_table(doc, rows):
    header = rows[0]
    body = rows[2:] if len(rows) > 1 and re.fullmatch(r"[\s|:\-]+", rows[1]) else rows[1:]
    cells = [split_row(header)] + [split_row(r) for r in body]
    ncol = max(len(r) for r in cells)
    t = doc.add_table(rows=len(cells), cols=ncol)
    t.style = doc.styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblpr = t._tbl.tblPr
    tblw = tblpr.find(qn("w:tblW"))
    if tblw is None:
        tblw = OxmlElement("w:tblW")
        tblpr.append(tblw)
    tblw.set(qn("w:type"), "pct")
    tblw.set(qn("w:w"), "5000")
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "autofit")
    tblpr.append(layout)
    for gc in t._tbl.tblGrid.findall(qn("w:gridCol")):
        gc.attrib.pop(qn("w:w"), None)
    for tc in t._tbl.iter(qn("w:tc")):
        tcpr = tc.find(qn("w:tcPr"))
        if tcpr is not None:
            tcw = tcpr.find(qn("w:tcW"))
            if tcw is not None:
                tcw.set(qn("w:type"), "auto")
                tcw.set(qn("w:w"), "0")
    for ri, row in enumerate(cells):
        for ci in range(ncol):
            txt = row[ci] if ci < len(row) else ""
            par = t.cell(ri, ci).paragraphs[0]
            compact(par.paragraph_format, after=0)
            add_inline(par, txt, bold_all=(ri == 0))
    sp = doc.add_paragraph()
    compact(sp.paragraph_format, after=0)


def add_bullet(doc, body, level):
    level = min(level, 3)
    par = doc.add_paragraph()
    pf = par.paragraph_format
    compact(pf)
    pf.left_indent = Cm(0.4 * level)
    pf.first_line_indent = Cm(-0.3)
    r = par.add_run(BULLETS[level - 1] + " ")
    add_inline(par, body)
    r.font.color.rgb = par.runs[1].font.color.rgb if len(par.runs) > 1 else BLACK


def add_code(doc, block, lang):
    if lang.strip().lower() == "mermaid":
        par = doc.add_paragraph()
        add_inline(par, "[도식: .md 파일에서 확인]")
        return
    for line in block:
        par = doc.add_paragraph()
        compact(par.paragraph_format, after=0)
        r = par.add_run(line)
        set_font(r, BODY_PT - 1, name=MONO)


def indent_level(spaces):
    n = len(spaces.expandtabs(4))
    return 1 if n < 2 else 2 if n < 4 else 3


def convert(md_path, out_path):
    base = os.path.dirname(os.path.abspath(md_path))
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    doc = Document()
    setup(doc)
    i, first = 0, True
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s or s == "---":
            i += 1
            continue
        if s.startswith("```"):
            lang = s[3:]
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            add_code(doc, block, lang)
            i += 1
            continue
        if first and s.startswith("**") and s.endswith("**"):
            doc.add_paragraph(s.strip("*"), style="Title")
            first = False
            i += 1
            continue
        first = False
        if s.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            add_table(doc, block)
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            h = doc.add_heading(level=min(len(m.group(1)), 3))
            add_inline(h, m.group(2), color=BLACK)
            i += 1
            continue
        bm = re.match(r"^(\s*)[-*+]\s+(.*)$", line)
        body = bm.group(2) if bm else s
        if body.startswith("!["):
            add_images(doc, body, base)
        elif bm:
            add_bullet(doc, body, indent_level(bm.group(1)))
        else:
            par = doc.add_paragraph()
            add_inline(par, s)
        i += 1
    doc.save(out_path)


if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
    print("saved", sys.argv[2])
