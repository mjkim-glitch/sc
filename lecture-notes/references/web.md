# 웹 페이지 묶음 · 아티팩트 · 프린트 PDF

.md 미리보기에서는 색·형광펜이 안 보이고, 마인드맵 그림·모의고사 정답 가리기도 불편하다. 그래서 세트를 웹 페이지 묶음으로 만든다(휴대폰에서도 봄). 사용자가 원하거나 "보기 편하게", "색이 안 보인다", "html/아티팩트"라고 하면 만든다.

## 만들기

과목 폴더(claude.ai에서는 작업 폴더)에서:

```bash
python -I <skill>/scripts/web/build_web.py --dir . --prefix "{강의명}_{범위}_" \
  --title "{강의명} 중간고사" --scope "범위: … (n~m주차)" \
  --concepts tools/concepts_vN.py --mindmap-md "{강의명}_{범위}_마인드맵_vN.md" [--single-file]
python -I <skill>/scripts/browser.py pdf web/mindmap_print.html web/mindmap_print.pdf
```

- 결과(web/): `index.html`(첫 화면), `guide.html`, `exam.html`, `mindmap.html`, `mindmap_print.html`, `note.html`, `images/`. 있는 .md만 페이지가 된다.
- `--single-file`: 그림을 data URI로 넣은 한 파일짜리 페이지를 `web/single/`에 더 만든다. 파일 하나만 열어도 그림이 보이므로 claude.ai·휴대폰으로 넘길 때 쓴다(파일이 커진다: 그림이 많은 노트는 수 MB).
- 프린트 PDF는 과목 폴더(결과 폴더)에도 `{…}_마인드맵_vN_프린트_A3.pdf`로 복사해 둔다(바로 인쇄용). 브라우저가 없어 PDF를 못 만들면 `mindmap_print.html`을 넘기고 "브라우저에서 열어 인쇄(A3·가로·여백 없음·100%)"라고 안내한다.
- .md를 고치면 위 명령을 다시 실행한다. 이 명령을 과목 메모에 적어 둔다.

## 페이지가 하는 일

- 공통: 상단 메뉴, 목차, MathJax(cdnjs, SVG)로 수식, 노트 색 규칙(회색 강의·빨강 중요·파랑 자료에 없음·초록 풀이, [필기]·[판서] 태그, 형광펜 3색), `(→ 2.3.1)`은 note.html의 그 절 링크, 밝은·어두운 화면 모두 대응.
- 가이드: 체크리스트 칸을 누르면 이 브라우저에 기억.
- 모의고사: 문제마다 [정답] [풀이] [관련 설명] [채점 포인트] [노트 원문 x.y]를 하나씩 펼침. 유형 거르기(대제목 글자로 자동), 중요만, 틀린 것만, 모두 펼치기, 스스로 채점(브라우저에 기억).
- 마인드맵: 구조도 + 라벨 수식 + 상자를 누르면 노트 원문 + 왼쪽 아래 **프린트용 내려받기**(PDF·HTML).

## 넘기기

### PC의 Claude Code — 아티팩트 서버(claude-artifacts)

1. 처음 올리기 전에 서버의 `guide`(pages, design)를 읽는다.
2. `publish_files`로 여러 파일을 한 번에: `index.html`·각 페이지·`mindmap_print.html`·`mindmap_print.pdf`·`images/*.png`를 각자 `as` 경로로(그림은 파일, 상대 경로). 제목·아이콘을 준다.
3. **내려받기 버튼**: `declare_capabilities`로 `{"downloads": true}`를 먼저 선언하고(새 아티팩트면 올린 뒤) 올린다. 버튼은 `window.claude.use('downloads')`가 null이면 숨고, 아티팩트 밖에서는 일반 링크가 보인다.
4. 다시 올릴 때는 바뀐 파일만 `slug`·`base_version`과 함께. 주소·slug는 과목 CLAUDE.md에.
5. 이렇게 올린 아티팩트는 claude.ai 주소라서 휴대폰 앱에서도 열린다.

### claude.ai (웹·모바일 앱)

- `--single-file` 결과(web/single/의 HTML)와 프린트 PDF·Word 파일을 결과 폴더에 두고 사용자에게 넘긴다. 휴대폰에서는 파일을 눌러 미리 보거나 내려받아 브라우저로 연다.
- 대화 안 아티팩트로 보여 줄 때는 한 파일짜리여야 한다(외부 스크립트는 cdnjs만 — MathJax는 이미 cdnjs). 그림이 많은 노트 페이지는 너무 커서 아티팩트로 다시 쓰기 어렵다 → 가이드·모의고사처럼 작은 페이지만 아티팩트로, 노트는 파일로.

## 확인 (넘기기 전에 한 번)

- 스크린샷: `python -I <skill>/scripts/browser.py shot web/guide.html <png> --size 1400,2400`. 주소에 `#앵커`를 붙이면 빈 화면이 나오므로 붙이지 않는다.
- 수식이 글자(`\(…\)`)로 보이면 MathJax 스크립트가 안 들어간 것이다(구조도 템플릿은 `</head>`·`</body>`를 생략하므로 빌드가 `</title>` 뒤와 문서 끝에 넣는다).
- 모든 수식: `python -I <skill>/scripts/mathcheck.py *.md` (ERRORS 0).
- 프린트 PDF: `pymupdf`로 쪽 수·크기를 확인하고 2~3쪽을 그려 본다(칸 넘침, 끊긴 가지, 수식 크기).
