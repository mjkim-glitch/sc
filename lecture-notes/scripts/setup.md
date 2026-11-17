# 실행 환경 준비

`<skill>`은 이 skill 폴더(SKILL.md가 있는 곳)다. 스크립트는 `python -I <skill>/scripts/…`로 부른다.

## PC의 Claude Code (Windows) — 처음 한 번

```bash
"C:/Users/Kimminji/AppData/Local/Programs/Python/Python314/python.exe" -m venv "C:/Users/Kimminji/AppData/Local/lecture-notes/venv"
V="C:/Users/Kimminji/AppData/Local/lecture-notes/venv/Scripts/python.exe"
"$V" -m pip install -r "<skill>/scripts/requirements.txt" faster-whisper av
"$V" -c "import docx, pymupdf, PIL, lxml, latex2mathml, pypandoc; print('ok')"
```

- 위 경로의 파이썬이 없으면 Python 3 설치를 안내한다. `python` 명령은 Microsoft Store 별칭이라 멈출 수 있으니 쓰지 않는다.
- Word가 있으면 수식은 Office의 `MML2OMML.XSL`로, Word → PDF는 Word로 바꾼다. 브라우저는 Edge를 쓴다.
- PowerShell 5.1은 BOM 없는 UTF-8 .ps1의 한글을 깨뜨린다. .ps1에는 한글을 넣지 않는다.

## claude.ai (웹·데스크톱·모바일 앱)

```bash
pip install -r <skill>/scripts/requirements.txt  # 막히면 --break-system-packages 를 붙인다
python3 -c "import docx, pymupdf, PIL, lxml, latex2mathml, pypandoc; print('ok')"
```

- 설치가 안 되면(네트워크 막힘) 사용자에게 claude.ai 설정의 코드 실행·네트워크 허용을 안내하고, 되는 범위(.md 결과물)만 먼저 만든다.
- Word 수식은 pandoc(`pypandoc_binary`에 들어 있음)으로 바뀐다.
- 브라우저(Chrome/Chromium)가 없으면: 수식 확인은 문법 검사만, 프린트 PDF·스크린샷은 건너뛰고 인쇄용 HTML을 넘긴다(휴대폰·PC 브라우저에서 열어 인쇄 → PDF로 저장 가능). `pip install playwright && python -m playwright install chromium`이 되면 그 Chromium을 자동으로 쓴다.
- LibreOffice(`soffice`)가 있으면 Word → PDF 확인에 쓴다.
- whisper 받아쓰기는 하지 않는다(모델 3GB, 시간 제한). 전사문을 받는다.

## 스크립트 목록

| 스크립트 | 하는 일 | Windows | claude.ai |
| --- | --- | --- | --- |
| extract_pdf.py | PDF → 쪽별 텍스트·쪽 이미지 | O | O |
| transcribe.py | 녹음 받아쓰기(faster-whisper) | O | X (전사문 사용) |
| md2docx.py / md2docx_math.py | .md → .docx (색·형광펜 / + LaTeX → Word 수식) | O (Office) | O (pandoc) |
| docx2pdf.py (+ docx2pdf.ps1) | Word → PDF (눈으로 확인) | O (Word) | LibreOffice 있을 때 |
| render_pages.py | PDF → 쪽 그림 | O | O |
| mathcheck.py | .md의 모든 수식 오류 찾기 | O (MathJax) | 브라우저 없으면 문법만 |
| browser.py | HTML → PDF(@page 크기대로) / 스크린샷 / DOM | O (Edge) | 브라우저 있을 때 |
| structure/build_structure.py | 개념 구조도 .md + 웹 페이지 (기본) | O | O |
| structure/mindmap_build.py | 라벨 LaTeX 구조도 + 프린트용 A3 (build_web.py가 부름) | O | O |
| web/build_web.py, web/webmd.py | 세트 → 웹 페이지 묶음(`--single-file`: 그림까지 한 파일) | O | O |
