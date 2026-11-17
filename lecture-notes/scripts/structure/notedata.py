"""study note.md → 절별 데이터(제목·부모·자식·HTML·강조 여부)."""
import html
import re


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"==분홍:(.+?)==", r'<mark class="pink">\1</mark>', s)
    s = re.sub(r"==파랑:(.+?)==", r'<mark class="blue">\1</mark>', s)
    s = re.sub(r"==(.+?)==", r"<mark>\1</mark>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[(확인 필요[^\]]*|원문 확인)\]", r'<span class="chk">[\1]</span>', s)
    s = s.replace("[강의]", '<span class="tag">강의</span>')
    return s


def line_class(raw):
    if "[강의]" not in raw:
        return ""
    if "(중요)" in raw:
        return "lec key"
    if "(자료에 없음)" in raw:
        return "lec extra"
    return "lec"


def block_html(body_lines):
    out, stack = [], []

    def close_to(level):
        while stack and stack[-1] > level:
            out.append("</li></ul>")
            stack.pop()

    i = 0
    while i < len(body_lines):
        l = body_lines[i]
        if not l.strip() or l.strip() == "---":
            i += 1
            continue
        if l.lstrip().startswith("|"):
            close_to(-1)
            rows = []
            while i < len(body_lines) and body_lines[i].lstrip().startswith("|"):
                rows.append(body_lines[i].strip())
                i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows if not re.match(r"^\|[\s\-|]+\|$", r)]
            t = ['<div class="tbl"><table>']
            for k, r in enumerate(cells):
                tag = "th" if k == 0 else "td"
                t.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in r) + "</tr>")
            t.append("</table></div>")
            out.append("".join(t))
            continue
        m = re.match(r"^( *)- (.*)$", l)
        if m:
            ind, text = len(m.group(1)), m.group(2)
            cls = line_class(text)
            if not stack or ind > stack[-1]:
                out.append("<ul>")
                stack.append(ind)
            else:
                close_to(ind)
                out.append("</li>")
            out.append(f'<li class="{cls}">' if cls else "<li>")
            out.append(inline(text))
            i += 1
            continue
        close_to(-1)
        out.append(f"<p>{inline(l.strip())}</p>")
        i += 1
    close_to(-1)
    return "".join(out)


def load(note_path):
    lines = open(note_path, encoding="utf-8").read().replace("\r\n", "\n").split("\n")
    nodes, order, cur = {}, [], None
    for l in lines:
        m1 = re.match(r"^# (\d)\. (.*)$", l)
        m2 = re.match(r"^## (\d+\.\d+) (.*)$", l)
        m3 = re.match(r"^### (\d+\.\d+\.\d+) (.*)$", l)
        if m1:
            nid = m1.group(1)
            cur = {"id": nid, "title": m1.group(2), "level": 1, "parent": None, "body": [], "kids": []}
        elif m2:
            nid = m2.group(1)
            cur = {"id": nid, "title": m2.group(2), "level": 2, "parent": nid.split(".")[0], "body": [], "kids": []}
        elif m3:
            nid = m3.group(1)
            cur = {"id": nid, "title": m3.group(2), "level": 3, "parent": ".".join(nid.split(".")[:2]), "body": [], "kids": []}
        elif l.startswith("# "):
            cur = None
            continue
        else:
            if cur is not None:
                cur["body"].append(l)
            continue
        nodes[nid] = cur
        order.append(nid)
        if cur["parent"]:
            nodes[cur["parent"]]["kids"].append(nid)

    def full_text(nid):
        n = nodes[nid]
        return "\n".join(n["body"]) + "".join(full_text(k) for k in n["kids"])

    data = {}
    for nid in order:
        n = nodes[nid]
        data[nid] = {"id": nid, "title": n["title"], "level": n["level"], "parent": n["parent"],
                     "kids": n["kids"], "html": block_html(n["body"]), "key": "[강의] (중요)" in full_text(nid)}
    return data
