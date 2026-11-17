"""개념 구조도(v2 방식) 생성: 웹 페이지 HTML + 마인드맵 .md

Usage:
  python -I build_structure.py --note "{강의명}_{범위}_study note.md" --concepts concepts.py \
      --html out.html --md "{강의명}_{범위}_마인드맵.md"

concepts.py 에 정의할 것 (structure_model.N 으로 노드 작성):
  CHAPTERS = [("1", 트리), ("2", 트리), ...]      # 필수. id는 노트의 대분류 번호("# 1. …")
  COURSE   = "과목명"                              # 선택 (기본: 노트 제목에서)
  RANGE    = "1강~6강"                             # 선택
  TITLES   = {"1": "1. 자산배분", ...}             # 선택 (기본: 노트 대분류 제목)
  TABS     = [("1", "1. 자산배분", ["1"]), ("05", "0·5. 원칙·여담", ["0", "5"])]  # 선택 (기본: 장마다 탭 하나)
  ORDER    = ["1", "2", "0"]                       # 선택: 전체 개요 순서 (기본: CHAPTERS 순서)
  LINKS    = [("A 개념", "2강 · 1.9.4", "B 개념", "1·3강 · 2.3", "관계"), ...]  # 선택: 강의 간 연결
  LEDE_EXTRA = " 이전 버전은 <a href=…>여기</a>"   # 선택: 머리말 뒤에 붙일 HTML
"""
import argparse
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import notedata  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--note", required=True)
ap.add_argument("--concepts", required=True)
ap.add_argument("--html", required=True)
ap.add_argument("--md", required=True)
ap.add_argument("--tpl", default=os.path.join(HERE, "structure.tpl"))
args = ap.parse_args()

sys.path.insert(0, os.path.dirname(os.path.abspath(args.concepts)))
spec = importlib.util.spec_from_file_location("concepts", args.concepts)
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)

D = notedata.load(args.note)
CHAPTERS = cm.CHAPTERS
note_title = ""
for l in open(args.note, encoding="utf-8"):
    if l.startswith("# ") and not re.match(r"^# \d", l):
        note_title = l[2:].strip()
        break
COURSE = getattr(cm, "COURSE", note_title.split(" ")[0] if note_title else "강의")
RANGE = getattr(cm, "RANGE", "")
TITLES = getattr(cm, "TITLES", {cid: f"{cid}. {D[cid]['title']}" if cid in D else cid for cid, _ in CHAPTERS})
TABS = getattr(cm, "TABS", [(cid, TITLES[cid], [cid]) for cid, _ in CHAPTERS])
ORDER = getattr(cm, "ORDER", [cid for cid, _ in CHAPTERS])
LINKS = getattr(cm, "LINKS", [])
LEDE_EXTRA = getattr(cm, "LEDE_EXTRA", "")

missing = []


def assign(node, nid, depth):
    node["id"], node["depth"] = nid, depth
    node.setdefault("n", 0)
    for r in node["r"]:
        if r not in D:
            missing.append((node["t"], r))
    if node.get("g"):
        core = [k for k in node["c"] if not k.get("a")]
        aside = [k for k in node["c"] if k.get("a")]
        for i, k in enumerate(core, 1):
            k["n"] = i
        node["c"] = core + aside
    for i, k in enumerate(node["c"], 1):
        assign(k, f"{nid}.{i}", depth + 1)


for cid, tree in CHAPTERS:
    assign(tree, "c" + cid, 0)
if missing:
    sys.exit(f"노트에 없는 근거 절: {missing}")

payload = {
    "notes": D,
    "chapters": [{"id": cid, "tree": t} for cid, t in CHAPTERS],
    "titles": TITLES,
    "tabs": [{"id": i, "label": l, "roots": r} for i, l, r in TABS],
    "order": ORDER,
    "links": [list(x) for x in LINKS],
}
data = json.dumps(payload, ensure_ascii=False)
if "</script" in data:
    sys.exit("노트 내용에 </script 가 있어 페이지에 넣을 수 없음")

title = f"{COURSE} 구조도"
page = open(args.tpl, encoding="utf-8").read()
for k, v in {
    "{{TITLE}}": title, "{{H1}}": title,
    "{{EYEBROW}}": " · ".join(x for x in [COURSE, RANGE, "개념 구조도"] if x),
    "{{LEDE_EXTRA}}": LEDE_EXTRA, "{{NOTE_NAME}}": os.path.basename(args.note),
}.items():
    page = page.replace(k, v)
page = page.replace("/*DATA*/null", data)
open(args.html, "w", encoding="utf-8").write(page)


# ---------- 마인드맵 .md ----------
def lab(n):
    s = ("★" if n["k"] else "") + n["t"]
    if n.get("n"):
        s = f'{n["n"]}) ' + s
    if n.get("a"):
        s = f'[{n["a"]}] ' + s
    if n.get("g"):
        s += f' 〔{n["g"]}〕'
    return s.replace('"', "'")


def mid(n):
    return n["id"].replace(".", "_")


def mermaid(tree):
    out = ["```mermaid", "flowchart LR", f'  {mid(tree)}["{lab(tree)}"]']

    def walk(n):
        for k in n["c"]:
            out.append(f'  {mid(n)} --> {mid(k)}["{lab(k)}"]')
            walk(k)
    walk(tree)
    out.append("```")
    return "\n".join(out)


def text_tree(tree):
    out = [f'{lab(tree)} — {tree["d"]}  (→ {", ".join(tree["r"])})']

    def walk(n, prefix):
        for i, k in enumerate(n["c"]):
            last = i == len(n["c"]) - 1
            name = f"**{lab(k)}**" if k["k"] else lab(k)
            desc = f' — {k["d"]}' if k["d"] else ""
            if k.get("z") and not k["c"]:
                desc += f' ⇒ {k["z"]}'
            out.append(f'{prefix}{"└─" if last else "├─"} {name}{desc}  (→ {", ".join(k["r"])})')
            walk(k, prefix + ("   " if last else "│  "))
    walk(tree, "")
    return out


md = [f"# {COURSE} {RANGE} 마인드맵 — 개념 구조도".replace("  ", " "), "",
      "- 노트 절 번호 순서가 아니라 개념의 상하관계로 짠 구조도 (왼쪽 상위 → 오른쪽 하위)",
      "- 설명은 study note 문장을 줄인 것, `⇒`는 끝 노드의 결론, `(→ 3.3.2)`는 근거 절 번호",
      "- ★ / **굵게** = 교수가 강조한 개념",
      "- `〔3요소〕` = 묶음, `1) 2) 3)` = 묶음의 핵심 구성원, `[도구]` `[근거]` 등 = 번호 없는 보조 항목", ""]
ov = ["```mermaid", "flowchart LR", f'  root["{COURSE} {RANGE}"]']
trees = dict(CHAPTERS)
for cid in ORDER:
    t = trees[cid]
    ov.append(f'  root --> {mid(t)}["{TITLES[cid]}"]')
    for k in t["c"]:
        ov.append(f'  {mid(t)} --> {mid(k)}["{lab(k)}"]')
ov.append("```")
md += ["## 전체 개요", "", "\n".join(ov), ""]
for cid in ORDER:
    md += [f"## {TITLES[cid]}", "", mermaid(trees[cid]), "", "```", *text_tree(trees[cid]), "```", ""]
if LINKS:
    md += ["## 강의를 넘나드는 연결", "", "```mermaid", "flowchart LR"]
    for i, (a, am, b, bm, why) in enumerate(LINKS, 1):
        md.append(f'  L{i}a["{a} ({am})"] -->|"{why}"| L{i}b["{b} ({bm})"]')
    md += ["```", ""]
    for a, am, b, bm, why in LINKS:
        md.append(f"- {a} ({am}) ⟶ {b} ({bm}): {why}")
    md.append("")
open(args.md, "w", encoding="utf-8").write("\n".join(md))

nodes = len(re.findall(r'"t":', json.dumps(payload["chapters"], ensure_ascii=False)))
print(f"nodes {nodes} → {args.html}, {args.md}")
