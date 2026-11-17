"""PDF 몇 쪽을 PNG로 렌더링한다 (레이아웃·색 가독성 확인용).

Usage: python render_pages.py 입력.pdf 출력폴더 [쪽번호 ...]   (쪽번호는 1부터, 생략하면 1쪽과 가운데 쪽)
"""
import os
import sys

import pymupdf


def main():
    pdf, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    doc = pymupdf.open(pdf)
    pages = [int(p) for p in sys.argv[3:]] or sorted({1, max(1, doc.page_count // 2)})
    for p in pages:
        if 1 <= p <= doc.page_count:
            out = os.path.join(outdir, f"page_{p}.png")
            doc[p - 1].get_pixmap(dpi=110).save(out)
            print(out)
    print(f"total pages: {doc.page_count}")


if __name__ == "__main__":
    main()
