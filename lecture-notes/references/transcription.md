# 녹음 받아쓰기

## 먼저: 이미 있는 전사문 확인

- 녹음 폴더 안팎에 전사문(클로바노트 .txt, 다른 앱의 받아쓰기)이 있는지 먼저 본다. 사용자가 나중에 넣어 줄 수도 있으니, 넣었다고 하면 바로 확인한다.
- 쓸 수 있는지 확인: 녹음마다 짝이 되는 전사문이 있는지, **전사문의 길이(머리말의 "n분 n초"·마지막 문단 시각)가 녹음 길이와 맞는지** 파일별 표로 확인해 사용자에게 보여 준다. 녹음 길이는 `av`(PyAV)로 읽는다.
- 맞으면 그 전사문을 쓰고 whisper 변환은 하지 않는다(진행 중이면 멈추고 부분 결과는 `transcripts/_중단_<모델>/`로 옮긴다). 전사문 출처를 과목 CLAUDE.md에 적는다.
- 클로바노트는 문단 시작 시각(분:초)만 있다 → 노트·보고에서 "파일 분:초"로 적는다.

## whisper 규칙

- 녹음 파일을 한국어로, 구간별 타임스탬프 `[HH:MM:SS - HH:MM:SS]`를 붙여 `transcripts/원본파일명.txt`로 저장한다.
- 품질을 속도보다 우선한다. 기본은 faster-whisper `large-v3`, language="ko", beam_size=5, vad_filter. 빠른 모델은 사용자 동의가 있을 때만.
- 실제 모델·설정은 스크립트가 `transcripts/_설정.txt`에 남긴다. 같은 과목은 같은 설정으로.
- 처음에는 첫 5분만 변환해 품질을 확인받은 뒤 전체를 진행한다.
- 파일 하나가 끝날 때마다 진행 상황과 예상 남은 시간(끝날 시각)을 보고하고, 사용자 응답이 없어도 계속 진행한다.
- 노트북 절전·화면 꺼짐이면 변환이 멈춘다. 오래 걸리면 절전 해제를 안내한다.
- 용어 힌트(`--prompt`)는 본문에 끼어들 수 있다. 끼어든 문구는 노트에서 빼고 보고한다. 힌트는 과목 CLAUDE.md에 적고 같은 과목에서 같은 힌트를 쓴다.
- 기존 받아쓰기를 다시 변환할 때는 덮어쓰기 전에 `transcripts/_이전_<모델>/`로 옮긴다.

## 명령 (PC의 Claude Code에서만 — claude.ai에서는 받아쓰기를 하지 않고 전사문을 받는다)

```bash
PY=C:/Users/Kimminji/AppData/Local/lecture-notes/venv/Scripts/python.exe   # Windows 가상환경
SK=<skill>/scripts
# 5분 품질 확인 (결과는 scratchpad에)
PYTHONIOENCODING=utf-8 "$PY" -I "$SK/transcribe.py" "녹음/파일.m4a" --outdir "<scratchpad>/sample" --max-seconds 300
# 전체 (백그라운드로 실행)
PYTHONIOENCODING=utf-8 "$PY" -I "$SK/transcribe.py" 녹음/*.m4a --outdir transcripts --skip-existing --prompt "과목명 강의. 용어1, 용어2"
```

- 속도 참고: CPU 16스레드에서 large-v3가 실시간의 약 1.7배(50분 녹음 ≈ 30분). 첫 실행은 모델 다운로드(약 3GB) 추가.
- 진행 로그의 `ETA`로 남은 시간을 보고한다.
