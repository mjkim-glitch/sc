"""note.html 목차 서랍(휴대폰) 스크롤 고침: 서랍이 열린 동안 본문 스크롤을 잠그고, 서랍만 스크롤되게 한다."""
import sys
CSS = """
@media (max-width: 860px) {
  .toc { height: 100vh; height: 100dvh; bottom: auto; overscroll-behavior: contain; -webkit-overflow-scrolling: touch; touch-action: pan-y; }
  body.drawer { overflow: hidden; }
  body.drawer .scrim { touch-action: none; }
}
</style>
</head>"""
JS_OLD = "const toggle = open => document.body.classList.toggle('drawer', open);"
JS_NEW = """let lockY = 0;
  function setDrawer(open) {
    const b = document.body, on = b.classList.contains('drawer');
    if (open === on) return;
    if (open) {
      lockY = scrollY;
      b.style.position = 'fixed'; b.style.top = -lockY + 'px'; b.style.left = '0'; b.style.right = '0';
      b.classList.add('drawer');
    } else {
      b.classList.remove('drawer');
      b.style.position = b.style.top = b.style.left = b.style.right = '';
      scrollTo(0, lockY);
    }
  }
  const toggle = open => setDrawer(open);"""
for f in sys.argv[1:]:
    h = open(f, encoding='utf-8').read()
    if 'setDrawer' in h:
        continue
    assert h.count('</style>\n</head>') == 1 and h.count(JS_OLD) == 1
    h = h.replace('</style>\n</head>', CSS, 1)
    h = h.replace(JS_OLD, JS_NEW, 1)
    n = h.count("document.body.classList.remove('drawer');")
    h = h.replace("document.body.classList.remove('drawer');", "setDrawer(false);")
    # setDrawer는 아래에서 정의되므로(함수 선언 호이스팅) 위쪽 호출도 동작한다
    open(f, 'w', encoding='utf-8').write(h)
    print(f, 'patched; remove calls replaced:', n)
