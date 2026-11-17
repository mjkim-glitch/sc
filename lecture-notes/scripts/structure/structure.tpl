<title>{{TITLE}}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap">
<style>
  /* Layout: 머리말 → 탭 → [왼쪽 개념 위계 트리 | 오른쪽 상세(설명·하위 개념·노트 원문)] — 좁은 화면에선 위아래 */
  :root {
    --bg: #f5f7f6; --surface: #ffffff; --ink: #17211f; --muted: #55625f;
    --line: #d9e1de; --wire: #9fb3ae;
    --accent: #0f6e6a; --accent-soft: #e2f0ee; --on-accent: #ffffff;
    --star: #a6510a; --star-soft: #fbeedd;
    --core: #5b4bc4; --core-soft: #ece9fb; --on-core: #ffffff;
    --lec: #5b6663; --lec-extra: #1d5fbf; --lec-key: #b3261e;
    --mark: #fff1a8; --mark-pink: #fadadd; --mark-blue: #d6e8fa;
    --font-body: "IBM Plex Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    --font-mono: "IBM Plex Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #101716; --surface: #172120; --ink: #e6eeec; --muted: #9db0ac; --line: #2a3936; --wire: #4d6460;
      --accent: #5cc8bf; --accent-soft: #1d3432; --on-accent: #0b1514; --star: #f0b25a; --star-soft: #3a2a14; --core: #a99bff; --core-soft: #262245; --on-core: #14112b;
      --lec: #a9b8b4; --lec-extra: #7fb2ff; --lec-key: #ff8a80;
      --mark: #5a4d12; --mark-pink: #5a2a33; --mark-blue: #1f3a57;
      color-scheme: dark;
    }
  }
  :root[data-theme="dark"] {
    --bg: #101716; --surface: #172120; --ink: #e6eeec; --muted: #9db0ac; --line: #2a3936; --wire: #4d6460;
    --accent: #5cc8bf; --accent-soft: #1d3432; --on-accent: #0b1514; --star: #f0b25a; --star-soft: #3a2a14; --core: #a99bff; --core-soft: #262245; --on-core: #14112b;
    --lec: #a9b8b4; --lec-extra: #7fb2ff; --lec-key: #ff8a80;
    --mark: #5a4d12; --mark-pink: #5a2a33; --mark-blue: #1f3a57;
    color-scheme: dark;
  }

  body {
    background: var(--bg); color: var(--ink);
    font-family: var(--font-body); font-size: 15px; line-height: 1.55;
    padding-left: max(16px, env(safe-area-inset-left, 0px));
    padding-right: max(16px, env(safe-area-inset-right, 0px));
  }
  body::before { content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--bg); }
  .wrap { max-width: 1360px; margin: 0 auto; padding-block: 24px 48px; display: grid; gap: 16px; }

  header { display: grid; gap: 8px; }
  .eyebrow { font-family: var(--font-mono); font-size: 12px; letter-spacing: .08em; color: var(--accent); text-transform: uppercase; }
  h1 { margin: 0; font-size: clamp(24px, 3.6vw, 32px); line-height: 1.2; text-wrap: balance; }
  .lede { margin: 0; color: var(--muted); max-width: 72ch; font-size: 14px; }
  .lede a { color: var(--accent); }
  .legend { display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: 12.5px; color: var(--muted); align-items: center; }
  .legend > span { display: inline-flex; align-items: center; gap: 6px; }
  .sw { display: inline-block; width: 10px; height: 10px; border-radius: 2px; }

  .tabs {
    position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg);
    display: flex; gap: 6px; overflow-x: auto; padding-block: 8px; border-bottom: 1px solid var(--line);
  }
  .tabs button {
    flex: none; font: inherit; font-size: 13.5px; font-weight: 500; cursor: pointer;
    color: var(--ink); background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 6px 14px;
  }
  .tabs button[aria-selected="true"] { background: var(--accent); color: var(--on-accent); border-color: var(--accent); }
  .tabs button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

  .view { display: grid; gap: 16px; grid-template-columns: minmax(0, 1fr) minmax(0, 470px); align-items: start; }
  .view.single { grid-template-columns: minmax(0, 1fr); }
  @media (max-width: 1000px) { .view { grid-template-columns: minmax(0, 1fr); } }
  .figure { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; overflow-x: auto; padding: 16px 18px; min-width: 0; }
  .hint { margin: 0 0 10px; font-size: 12.5px; color: var(--muted); }

  ul.tree, ul.tree ul { list-style: none; margin: 0; padding: 0; }
  ul.tree { display: inline-block; }
  ul.tree li { display: flex; align-items: center; position: relative; }
  ul.tree ul { display: flex; flex-direction: column; justify-content: center; position: relative; padding-left: 20px; }
  ul.tree ul::before { content: ""; position: absolute; left: 0; top: 50%; width: 20px; border-top: 1.5px solid var(--wire); }
  ul.tree ul > li { padding: 3px 0 3px 20px; }
  ul.tree ul > li::before { content: ""; position: absolute; left: 0; top: 50%; width: 20px; border-top: 1.5px solid var(--wire); }
  ul.tree ul > li::after { content: ""; position: absolute; left: 0; top: 0; bottom: 0; border-left: 1.5px solid var(--wire); }
  ul.tree ul > li:first-child::after { top: 50%; }
  ul.tree ul > li:last-child::after { bottom: 50%; }
  ul.tree ul > li:only-child::after { display: none; }

  .node {
    font: inherit; text-align: left; cursor: pointer; color: var(--ink);
    display: inline-flex; align-items: baseline; gap: 6px; max-width: 230px;
    border-radius: 6px; padding: 5px 10px; line-height: 1.35; border: 1.5px solid transparent;
  }
  .node .t { min-width: 0; }
  .node.d0 { background: var(--accent); color: var(--on-accent); font-weight: 700; font-size: 15.5px; padding: 8px 14px; }
  .node.d1 { background: var(--surface); border-color: var(--accent); font-weight: 700; font-size: 14.5px; }
  .node.d2 { background: var(--accent-soft); font-weight: 500; font-size: 14px; }
  .node.d3, .node.d4 { background: transparent; border-color: var(--line); font-size: 13.5px; color: var(--ink); }
  .node.key { border-color: var(--star); }
  .node.d2.key, .node.d3.key, .node.d4.key { background: var(--star-soft); }
  .node[aria-pressed="true"] { outline: 3px solid var(--star); outline-offset: 1px; }
  .node:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .star { color: var(--star); font-weight: 700; }
  .node.d0 .star { color: var(--on-accent); }
  .node.core { border-color: var(--core); background: var(--core-soft); }
  .node.d1.core { background: var(--surface); border-width: 2px; }
  .nb {
    flex: none; align-self: center; display: inline-grid; place-items: center; width: 19px; height: 19px; border-radius: 50%;
    background: var(--core); color: var(--on-core); font-size: 11px; font-weight: 700; font-family: var(--font-mono);
  }
  .node.aside { background: transparent; border: 1px dashed var(--wire); color: var(--ink); font-weight: 500; }
  .atag {
    flex: none; font-size: 10.5px; font-weight: 700; color: var(--muted); border: 1px solid var(--line);
    background: var(--surface); border-radius: 3px; padding: 0 4px; white-space: nowrap;
  }
  .gchip {
    flex: none; font-size: 11px; font-weight: 700; color: var(--core); background: var(--core-soft);
    border-radius: 999px; padding: 0 7px; white-space: nowrap;
  }
  .node.d0 .gchip { background: var(--surface); }
  .concl {
    display: inline-block; max-width: 300px; font-size: 12.5px; line-height: 1.4; color: var(--muted);
    border: 1px dashed var(--wire); border-radius: 6px; padding: 4px 8px; background: var(--bg);
  }
  .concl b { color: var(--accent); font-weight: 700; margin-right: 2px; }
  .toggle {
    flex: none; margin-left: auto; display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: var(--muted);
    padding: 0 4px; white-space: nowrap; cursor: pointer;
  }
  .toggle input { width: 16px; height: 16px; accent-color: var(--accent); }
  h2.ovh { margin: 6px 0 8px; font-size: 16px; color: var(--accent); position: sticky; left: 0; }

  .panel {
    background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 16px 18px;
    position: sticky; top: calc(58px + env(safe-area-inset-top, 0px));
    max-height: calc(100vh - 80px - env(safe-area-inset-top, 0px)); overflow: auto; min-width: 0;
  }
  @media (max-width: 1000px) { .panel { position: static; max-height: none; } }
  .crumb { font-size: 12.5px; color: var(--muted); display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
  .crumb button { font: inherit; color: var(--accent); background: none; border: 0; padding: 0; cursor: pointer; }
  .panel h2 { margin: 4px 0 6px; font-size: 19px; line-height: 1.35; text-wrap: balance; }
  .desc { margin: 0 0 10px; font-size: 14.5px; }
  .sub { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 12px; }
  .sub button {
    font: inherit; font-size: 13px; cursor: pointer; color: var(--ink);
    background: var(--accent-soft); border: 1px solid transparent; border-radius: 999px; padding: 3px 10px;
  }
  .sub button.key { background: var(--star-soft); border-color: var(--star); }
  .label { font-size: 12px; font-weight: 700; color: var(--muted); letter-spacing: .04em; margin: 12px 0 6px; }
  details { border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; margin-bottom: 8px; }
  details[open] { padding-bottom: 8px; }
  summary { cursor: pointer; padding: 8px 0; font-weight: 600; font-size: 14px; }
  summary .num { font-family: var(--font-mono); font-size: 12px; color: var(--accent); margin-right: 6px; }
  .content { font-size: 14px; overflow-wrap: anywhere; }
  .content h4 { margin: 12px 0 4px; font-size: 14px; color: var(--accent); }
  .content p { margin: 4px 0; }
  .content ul { margin: 4px 0; padding-left: 18px; }
  .content li { margin: 3px 0; }
  .content li.lec { color: var(--lec); }
  .content li.lec.extra { color: var(--lec-extra); }
  .content li.lec.key { color: var(--lec-key); font-weight: 700; }
  .content .tag { font-size: 11px; font-weight: 700; border: 1px solid currentColor; border-radius: 3px; padding: 0 4px; margin-right: 2px; }
  .content .chk { font-size: 12px; opacity: .8; }
  .content mark { background: var(--mark); color: inherit; padding: 0 2px; }
  .content mark.pink { background: var(--mark-pink); }
  .content mark.blue { background: var(--mark-blue); }
  .content code { font-family: var(--font-mono); font-size: 12.5px; }
  .tbl { overflow-x: auto; margin: 6px 0; }
  .tbl table { border-collapse: collapse; font-size: 13px; min-width: 100%; }
  .tbl th, .tbl td { border: 1px solid var(--line); padding: 4px 6px; vertical-align: top; text-align: left; font-variant-numeric: tabular-nums; }
  .tbl th { background: var(--accent-soft); }

  .links { display: grid; gap: 12px; }
  .link {
    background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px;
    display: grid; grid-template-columns: minmax(0, 1fr) minmax(120px, 0.8fr) minmax(0, 1fr); gap: 10px; align-items: center;
  }
  .link .node { max-width: none; width: 100%; background: var(--accent-soft); }
  .lbox { display: grid; gap: 4px; min-width: 0; }
  .lmeta { font-family: var(--font-mono); font-size: 11.5px; color: var(--muted); }
  .arrow { display: grid; gap: 4px; justify-items: center; text-align: center; font-size: 12.5px; color: var(--muted); }
  .arrow svg { width: 100%; height: 14px; display: block; }
  .arrow svg line { stroke: var(--accent); }
  .arrow svg path { fill: var(--accent); }
  @media (max-width: 640px) {
    .link { grid-template-columns: minmax(0, 1fr); }
    .arrow svg { transform: rotate(90deg); width: 40px; height: 40px; margin: 0 auto; }
  }

  footer { font-size: 12px; color: var(--muted); }
</style>

<div class="wrap">
  <header>
    <div class="eyebrow">{{EYEBROW}}</div>
    <h1>{{H1}}</h1>
    <p class="lede">노트 목차 순서가 아니라 개념의 상하관계로 짠 구조도입니다. 상자를 누르면 설명, 하위 개념, 근거가 된 노트 원문이 펼쳐집니다.{{LEDE_EXTRA}}</p>
    <div class="legend">
      <span><span class="gchip">3요소</span> 묶음 · <span class="nb">1</span> 핵심 구성원</span>
      <span><span class="atag">도구</span> 보조 항목(번호 없음)</span>
      <span><span class="star">★</span> 교수 강조 개념</span>
      <span><span class="sw" style="background:var(--lec)"></span> 강의 설명</span>
      <span><span class="sw" style="background:var(--lec-extra)"></span> 강의에서만 언급</span>
      <span><span class="sw" style="background:var(--lec-key)"></span> 교수 강조 (중요)</span>
    </div>
  </header>

  <nav class="tabs" role="tablist" aria-label="장 선택" id="tabs"></nav>
  <main id="main"></main>
  <footer>출처: {{NOTE_NAME}} · 설명은 노트 문장을 줄인 것, 원문은 각 상자의 '노트 원문'에서 확인</footer>
</div>

<script>
const P = /*DATA*/null;
const NOTES = P.notes;
const TITLES = P.titles;          // 장 id -> 표시 이름
const TABS = [{ id: "overview", label: "전체 개요" }, ...P.tabs.map(t => ({ id: t.id, label: t.label }))]
  .concat(P.links.length ? [{ id: "links", label: "강의 간 연결" }] : []);
const TAB_ROOTS = Object.fromEntries(P.tabs.map(t => [t.id, t.roots]));
const LINKS = P.links;            // [A, "n강 · 절", B, "n강 · 절", 관계]

const C = {};          // id -> node
const PARENT = {};     // id -> parent id
const CHAP = {};       // chapter id -> tree
P.chapters.forEach(({ id, tree }) => {
  CHAP[id] = tree;
  (function idx(n, par) { C[n.id] = n; if (par) PARENT[n.id] = par; n.c.forEach(k => idx(k, n.id)); })(tree, null);
});

const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const main = document.getElementById("main");
const tabsEl = document.getElementById("tabs");
let curTab = null;

const star = n => n.k ? '<span class="star" aria-label="교수 강조">★</span>' : "";
function nodeBtn(n, extra = "") {
  const cls = `node d${Math.min(n.depth, 4)}${n.k ? " key" : ""}${n.n ? " core" : ""}${n.a ? " aside" : ""}`;
  const nb = n.n ? `<span class="nb">${n.n}</span>` : "";
  const at = n.a ? `<span class="atag">${esc(n.a)}</span>` : "";
  const gc = n.g ? `<span class="gchip">${esc(n.g)}</span>` : "";
  return `<button type="button" class="${cls}" data-id="${n.id}" aria-pressed="false" title="${esc(n.d || "")}">${nb}${at}${star(n)}<span class="t">${esc(n.t)}</span>${gc}${extra}</button>`;
}
let showConcl = true;
try { showConcl = localStorage.getItem("v2-concl") !== "off"; } catch (e) {}
function treeHtml(n) {
  let kids = "";
  if (n.c.length) kids = `<ul>${n.c.map(k => `<li>${treeHtml(k)}</li>`).join("")}</ul>`;
  else if (showConcl && (n.z || n.d)) kids = `<ul><li><span class="concl"><b>→</b>${esc(n.z || n.d)}</span></li></ul>`;
  return nodeBtn(n) + kids;
}

function noteBlock(ref, open) {
  const s = NOTES[ref];
  if (!s) return "";
  let body = s.html || "";
  const addKids = id => NOTES[id].kids.forEach(k => { body += `<h4>${k} ${esc(NOTES[k].title)}</h4>${NOTES[k].html}`; addKids(k); });
  addKids(ref);
  const num = s.level === 1 ? ref + "장" : ref;
  return `<details${open ? " open" : ""}><summary><span class="num">${num}</span>${esc(s.title)}</summary><div class="content">${body}</div></details>`;
}

function panelHtml(id) {
  const n = C[id];
  const path = []; for (let p = id; p; p = PARENT[p]) path.unshift(p);
  const crumb = path.map(p => p === id ? `<span>${esc(C[p].t)}</span>` : `<button type="button" data-goto="${p}">${esc(C[p].t)}</button>`).join(" › ");
  const par = PARENT[id] ? C[PARENT[id]] : null;
  let role = "";
  if (n.n && par && par.g) role = `<span class="gchip">${esc(par.g)} 중 ${n.n}</span>`;
  else if (n.a) role = `<span class="atag">${esc(n.a)}</span>`;
  let h = `<div class="crumb">${crumb}</div><h2>${star(n)} ${esc(n.t)} ${role}</h2>`;
  if (n.d) h += `<p class="desc">${esc(n.d)}</p>`;
  if (n.z && !n.c.length) h += `<p class="desc"><b style="color:var(--accent)">→</b> ${esc(n.z)}</p>`;
  if (n.c.length) {
    const subLabel = n.g ? `핵심 구성 <span class="gchip">${esc(n.g)}</span>` : "하위 개념";
    h += `<div class="label">${subLabel}</div><div class="sub">${n.c.map(k => {
      const pre = k.n ? `<span class="nb">${k.n}</span> ` : (k.a ? `<span class="atag">${esc(k.a)}</span> ` : "");
      return `<button type="button" class="${k.k ? "key" : ""}" data-goto="${k.id}">${pre}${k.k ? "★ " : ""}${esc(k.t)}</button>`;
    }).join("")}</div>`;
  }
  h += `<div class="label">노트 원문</div>` + n.r.map((r, i) => noteBlock(r, i === 0)).join("");
  return h;
}

function select(id) {
  document.querySelectorAll(".node[data-id]").forEach(b => b.setAttribute("aria-pressed", b.dataset.id === id ? "true" : "false"));
  const panel = document.getElementById("panel");
  if (panel) { panel.innerHTML = panelHtml(id); panel.scrollTop = 0; }
}
const tabOf = id => { const c = id.slice(1).split(".")[0]; return (P.tabs.find(t => t.roots.includes(c)) || P.tabs[0]).id; };

function render(tab, sel) {
  curTab = tab;
  tabsEl.querySelectorAll("button").forEach(b => b.setAttribute("aria-selected", b.dataset.tab === tab ? "true" : "false"));
  if (tab === "overview") {
    const trees = P.order.map(cid =>
      `<h2 class="ovh">${esc(TITLES[cid])}</h2><ul class="tree" style="display:block;margin-bottom:18px"><li>${treeHtml(CHAP[cid])}</li></ul>`).join("");
    main.innerHTML = `<div class="view single"><div class="figure"><p class="hint">모든 장의 개념 구조도를 한 번에 펼친 화면입니다. 상자를 누르면 해당 장 탭에서 설명과 노트 원문이 열립니다.</p>${trees}</div></div>`;
  } else if (tab === "links") {
    const arrow = `<svg viewBox="0 0 100 14" preserveAspectRatio="none" aria-hidden="true"><line x1="0" y1="7" x2="90" y2="7" stroke-width="2"/><path d="M88 1 L100 7 L88 13 Z"/></svg>`;
    main.innerHTML = `<div class="view single"><div class="links">${LINKS.map(([a, am, b, bm, why]) => {
      const ga = conceptFor(am.split(" · ")[1]), gb = conceptFor(bm.split(" · ")[1]);
      return `<div class="link"><div class="lbox"><button type="button" class="node" data-goto="${ga}"><span class="t">${esc(a)}</span></button><span class="lmeta">${esc(am)}</span></div><div class="arrow">${arrow}<span>${esc(why)}</span></div><div class="lbox"><button type="button" class="node" data-goto="${gb}"><span class="t">${esc(b)}</span></button><span class="lmeta">${esc(bm)}</span></div></div>`;
    }).join("")}</div></div>`;
  } else {
    const roots = TAB_ROOTS[tab];
    const trees = roots.map(r => `<ul class="tree" style="display:block;margin-bottom:14px"><li>${treeHtml(CHAP[r])}</li></ul>`).join("");
    main.innerHTML = `<div class="view"><div class="figure"><p class="hint">상자를 누르면 설명과 노트 원문이 펼쳐집니다.</p>${trees}</div><aside class="panel" id="panel" aria-live="polite"></aside></div>`;
    const target = sel || CHAP[roots[0]].id;
    select(target);
    if (sel) { const b = main.querySelector(`.node[data-id="${CSS.escape(sel)}"]`); if (b) b.scrollIntoView({ block: "nearest", inline: "center" }); }
  }
}

function conceptFor(ref) {
  let best = null, bestDepth = 99;
  for (const id in C) {
    const n = C[id];
    if (n.r.includes(ref) && n.depth < bestDepth) { best = id; bestDepth = n.depth; }
  }
  if (best) return best;
  for (const id in C) if (C[id].r.some(r => ref.startsWith(r + ".") || r.startsWith(ref + "."))) return id;
  return "c" + ref.split(".")[0];
}

function goTo(id) {
  const tab = tabOf(id);
  if (curTab !== tab) render(tab, id); else select(id);
  if (window.matchMedia("(max-width: 1000px)").matches) { const p = document.getElementById("panel"); if (p) p.scrollIntoView({ block: "start" }); }
}

tabsEl.innerHTML = TABS.map(t => `<button type="button" role="tab" data-tab="${t.id}" aria-selected="false">${t.label}</button>`).join("")
  + `<label class="toggle"><input type="checkbox" id="concl-toggle"${showConcl ? " checked" : ""}>결론 노드 표시</label>`;
tabsEl.addEventListener("click", e => { const b = e.target.closest("button[data-tab]"); if (b) render(b.dataset.tab); });
document.getElementById("concl-toggle").addEventListener("change", e => {
  showConcl = e.target.checked;
  try { localStorage.setItem("v2-concl", showConcl ? "on" : "off"); } catch (err) {}
  const pressed = main.querySelector('.node[aria-pressed="true"]');
  render(curTab, pressed ? pressed.dataset.id : undefined);
});
main.addEventListener("click", e => {
  const g = e.target.closest("[data-goto]"); if (g) { goTo(g.dataset.goto); return; }
  const n = e.target.closest(".node[data-id]");
  if (n) { if (curTab === "overview") goTo(n.dataset.id); else select(n.dataset.id); }
});
const start = (location.hash || "").slice(1);
render(TABS.some(t => t.id === start) ? start : "overview");
</script>
