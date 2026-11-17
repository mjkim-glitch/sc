"""스터디 가이드 .md → 합본 페이지용 HTML (목차 + 본문).
절 번호 표시 (→ 3.3, 3.7.3)의 각 번호는 구조도로 이동하는 버튼(data-ref)이 된다.
"""
import html
import re


def _refs(m):
    inner = m.group(1)
    inner = re.sub(r"(?<![\d.])(\d+(?:\.\d+)*)(?![\d.])",
                   lambda x: f'<button type="button" class="gref" data-ref="{x.group(1)}">{x.group(1)}</button>', inner)
    return f'<span class="ref">→ {inner}</span>'


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"==분홍:(.+?)==", r'<mark class="pink">\1</mark>', s)
    s = re.sub(r"==파랑:(.+?)==", r'<mark class="blue">\1</mark>', s)
    s = re.sub(r"==(.+?)==", r"<mark>\1</mark>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\(→ ([^)]*)\)", _refs, s)
    s = s.replace("(중요)", '<span class="imp">중요</span>')
    return s


def convert(md_path):
    lines = open(md_path, encoding="utf-8").read().replace("\r\n", "\n").split("\n")
    out, toc, stack = [], [], []
    state = {"card": False, "n": 0, "checks": 0}

    def close_lists(level=-1):
        while stack and stack[-1] > level:
            out.append("</li></ul>")
            stack.pop()

    def close_card():
        if state["card"]:
            out.append("</section>")
            state["card"] = False

    i = 0
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1
            continue
        if l.startswith("# "):
            close_lists()
            i += 1
            continue
        m2 = re.match(r"^## (.*)$", l)
        m3 = re.match(r"^### (.*)$", l)
        if m2 or m3:
            close_lists()
            close_card()
            state["n"] += 1
            hid = f"g{state['n']}"
            if m2:
                title = m2.group(1)
                out.append(f'<h2 class="gh2" id="{hid}">{inline(title)}</h2>')
                toc.append([hid, re.sub(r"^\d+\.\s*", "", title), 2])
            else:
                title = m3.group(1)
                short = re.sub(r"^카드 ([A-Z])\. ", r"\1 ", title)
                short = re.sub(r"\s*\(.*?\)\s*→.*$", "", short)
                out.append(f'<section class="gcard" id="{hid}"><h3>{inline(title)}</h3>')
                state["card"] = True
                toc.append([hid, short, 3])
            i += 1
            continue
        if l.lstrip().startswith("```"):
            ind = len(l) - len(l.lstrip())
            i += 1
            code = []
            while i < len(lines) and not lines[i].lstrip().startswith("```"):
                code.append(lines[i][ind:] if lines[i][:ind].strip() == "" else lines[i])
                i += 1
            i += 1
            out.append(f'<pre class="gtree">{html.escape(chr(10).join(code))}</pre>')
            continue
        if l.lstrip().startswith("|"):
            close_lists()
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows if not re.match(r"^\|[\s\-|]+\|$", r)]
            t = ['<div class="tbl gtbl"><table>']
            for k, r in enumerate(cells):
                tag = "th" if k == 0 else "td"
                t.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in r) + "</tr>")
            t.append("</table></div>")
            out.append("".join(t))
            continue
        m = re.match(r"^( *)- (.*)$", l)
        if m:
            ind, text = len(m.group(1)), m.group(2)
            if not stack or ind > stack[-1]:
                out.append("<ul>")
                stack.append(ind)
            else:
                close_lists(ind)
                out.append("</li>")
            cb = re.match(r"^\[ \] (.*)$", text)
            if cb:
                state["checks"] += 1
                c = state["checks"]
                out.append(f'<li class="check"><label><input type="checkbox" id="c{c}" data-key="c{c}"><span>{inline(cb.group(1))}</span></label>')
            else:
                out.append(f"<li>{inline(text)}")
            i += 1
            continue
        close_lists()
        out.append(f"<p>{inline(l.strip())}</p>")
        i += 1
    close_lists()
    close_card()
    return {"toc": toc, "body": "\n".join(out), "checks": state["checks"]}
