"""정리 노트용 마크다운 → HTML (웹 페이지 판).

- 수식: $...$ → \\(...\\), $$...$$ → \\[...\\] (MathJax가 그림), 통화 \\$ → $
- 색: [강의] 회색 / [강의] (중요) 빨강 굵게 / (자료에 없음) 파랑 / [풀이] 초록 / [필기]·[판서] 표시
- ==노랑== / ==분홍:…== / ==파랑:…== 형광펜, **굵게**, 그림 ![](images/…), 표, 목록 들여쓰기
- (→ 2.3.1) 절 번호는 note.html의 해당 절로 가는 링크
"""
import html
import re

MATH = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$|(?<!\\)\$(.+?)(?<!\\)\$")
NOTE_PAGE = "note.html"


def sec_id(num):
    return "s" + num.strip(".").replace(".", "-")


def _ref(m, note_page):
    inner = m.group(1)

    def one(x):
        n = x.group(1)
        return f'<a class="ref-n" href="{note_page}#{sec_id(n)}">{n}</a>'
    inner = re.sub(r"(?<![\w.])(\d\.\d+(?:\.\d+)*)(?![\d.])", one, inner)
    return f'<span class="ref">→ {inner}</span>'


def inline(s, note_page=NOTE_PAGE):
    maths = []

    def keep(m):
        tex = m.group(1) if m.group(1) is not None else m.group(2)
        disp = m.group(1) is not None
        maths.append((tex, disp))
        return f"\x00{len(maths) - 1}\x01"
    s = MATH.sub(keep, s)
    s = s.replace("\\$", "$")
    s = html.escape(s, quote=False)
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
               lambda m: f'<img src="{m.group(2)}" alt="{m.group(1) or "그림"}" loading="lazy">', s)
    s = re.sub(r"(?<!!)\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"==분홍:(.+?)==", r'<mark class="pink">\1</mark>', s)
    s = re.sub(r"==파랑:(.+?)==", r'<mark class="blue">\1</mark>', s)
    s = re.sub(r"==(.+?)==", r"<mark>\1</mark>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[(확인 필요[^\]]*|원문 확인[^\]]*|필기 그대로[^\]]*)\]", r'<span class="chk">[\1]</span>', s)
    s = s.replace("[강의] (중요)", '<span class="tag lec">강의</span><span class="tag imp">중요</span>')
    s = s.replace("[강의]", '<span class="tag lec">강의</span>')
    s = s.replace("[필기]", '<span class="tag hw">필기</span>')
    s = s.replace("[판서]", '<span class="tag board">판서</span>')
    s = s.replace("[풀이]", '<span class="tag sol">풀이</span>')
    s = s.replace("(자료에 없음)", '<span class="tag ext">자료에 없음</span>')
    s = s.replace("(중요)", '<span class="tag imp">중요</span>')
    s = re.sub(r"\(→ ([^)]*)\)", lambda m: _ref(m, note_page), s)

    def back(m):
        tex, disp = maths[int(m.group(1))]
        tex = html.escape(tex, quote=False)
        return f'<span class="disp">\\[{tex}\\]</span>' if disp else f"\\({tex}\\)"
    return re.sub("\x00(\\d+)\x01", back, s)


def line_class(raw):
    if "[강의]" in raw:
        if "(중요)" in raw:
            return "lec key"
        if "(자료에 없음)" in raw:
            return "lec extra"
        return "lec"
    if "(자료에 없음)" in raw:
        return "extra"
    if "[풀이]" in raw:
        return "sol"
    if "[필기]" in raw:
        return "hw"
    if "[판서]" in raw:
        return "board"
    return ""


def render(lines, note_page=NOTE_PAGE, heading_ids=True, toc=None, shift=0):
    """마크다운 줄 목록 → HTML. toc 리스트를 주면 (수준, id, 제목)을 채운다."""
    out, stack = [], []

    def close_to(level):
        while stack and stack[-1] > level:
            out.append("</li></ul>")
            stack.pop()

    i, n_auto = 0, 0
    while i < len(lines):
        l = lines[i].rstrip()
        if not l.strip():
            i += 1
            continue
        if l.strip() == "---":
            close_to(-1)
            out.append("<hr>")
            i += 1
            continue
        if l.startswith("```"):
            close_to(-1)
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].startswith("```"):
                buf.append(lines[j])
                j += 1
            out.append('<pre class="tree">' + html.escape("\n".join(buf).replace("\\$", "$")) + "</pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{1,4}) (.*)$", l)
        if m:
            close_to(-1)
            lv = len(m.group(1))
            title = m.group(2).strip()
            num = re.match(r"^(\d+(?:\.\d+)*)\.?\s", title)
            if num and heading_ids:
                hid = sec_id(num.group(1))
            else:
                n_auto += 1
                hid = f"h{n_auto}"
            hl = min(6, lv + shift)
            out.append(f'<h{hl} id="{hid}">{inline(title, note_page)}</h{hl}>')
            if toc is not None:
                toc.append((lv, hid, re.sub(r"<[^>]+>", "", inline(title, note_page))))
            i += 1
            continue
        if l.lstrip().startswith("|"):
            close_to(-1)
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            cells = [[c.strip() for c in re.split(r"(?<!\\)\|", r.strip("|"))]
                     for r in rows if not re.match(r"^\|[\s\-:|]+\|$", r)]
            t = ['<div class="tbl"><table>']
            for k, r in enumerate(cells):
                tag = "th" if k == 0 else "td"
                t.append("<tr>" + "".join(f"<{tag}>{inline(c, note_page)}</{tag}>" for c in r) + "</tr>")
            t.append("</table></div>")
            out.append("".join(t))
            continue
        m = re.match(r"^( *)[-*] (.*)$", l)
        if m:
            ind, text = len(m.group(1)), m.group(2)
            chk = text.startswith("[ ] ")
            if chk:
                text = text[4:]
            cls = line_class(text)
            if chk:
                cls = (cls + " check").strip()
            if not stack or ind > stack[-1]:
                out.append("<ul>")
                stack.append(ind)
            else:
                close_to(ind)
                out.append("</li>")
            out.append(f'<li class="{cls}">' if cls else "<li>")
            if chk:
                out.append('<input type="checkbox" aria-label="확인"> ')
            out.append(inline(text, note_page))
            i += 1
            continue
        close_to(-1)
        if l.lstrip().startswith("![") and l.rstrip().endswith(")"):
            out.append(f'<figure>{inline(l.strip(), note_page)}</figure>')
        else:
            cls = line_class(l)
            out.append(f'<p class="{cls}">{inline(l.strip(), note_page)}</p>' if cls else f"<p>{inline(l.strip(), note_page)}</p>")
        i += 1
    close_to(-1)
    return "".join(out)


def note_sections(note_lines):
    """노트 절 번호 → 그 절(하위 절 포함)의 줄 목록."""
    heads = []
    for k, l in enumerate(note_lines):
        m = re.match(r"^(#{1,3}) (\d+(?:\.\d+)*)\.?\s", l)
        if m:
            heads.append((k, len(m.group(1)), m.group(2)))
    secs = {}
    for idx, (k, lv, num) in enumerate(heads):
        end = len(note_lines)
        for k2, lv2, _ in heads[idx + 1:]:
            if lv2 <= lv:
                end = k2
                break
        secs[num] = note_lines[k:end]
    return secs
