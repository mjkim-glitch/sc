"""개념 구조도 데이터 작성용 헬퍼.

concepts 파일에서 `from structure_model import N` 으로 쓴다.
N(라벨, 설명, [근거 절], key=교수 강조, kids=[...], z=결론, g=묶음 이름, a=보조 태그)
- g가 있는 노드: 자식 중 a가 없는 것이 핵심 구성원 → 1, 2, 3… 번호 (빌드 때 자동)
- a가 있는 노드: 핵심이 아닌 보조 항목(도구·근거·관측·공식·점검 등), 번호 없이 뒤로
- z: 끝 노드의 결론("그래서 무엇"). 없으면 설명이 결론 노드로 쓰임
"""


def N(label, desc="", refs=(), key=False, kids=(), z="", g="", a=""):
    return {"t": label, "d": desc, "r": list(refs), "k": key, "c": list(kids), "z": z, "g": g, "a": a}
