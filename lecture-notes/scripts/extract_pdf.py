"""강의자료 PDF를 쪽 단위 텍스트(.md)와 쪽 이미지(.png)로 뽑는다.

텍스트는 extracted/<파일명>.md 에 "## p.N" 머리로 쪽마다 나눠 저장한다.
쪽 이미지는 extracted/<파일명>/p_NNN.png 로 저장한다. 이미지 속 글자, 도식, 잘린 글자는
이 이미지를 직접 보고 확인한다 (텍스트 추출만 믿지 않는다).

Usage: python extract_pdf.py 강의자료/*.pdf --outdir extracted [--dpi 130]
"""
import argparse
import os

import pymupdf
import pymupdf4llm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--outdir", default="extracted")
    ap.add_argument("--dpi", type=int, default=130)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    for path in a.inputs:
        name = os.path.splitext(os.path.basename(path))[0]
        chunks = pymupdf4llm.to_markdown(path, page_chunks=True)
        with open(os.path.join(a.outdir, name + ".md"), "w", encoding="utf-8") as f:
            for n, c in enumerate(chunks, 1):
                f.write(f"## p.{n}\n\n{c['text'].strip()}\n\n")
        imgdir = os.path.join(a.outdir, name)
        os.makedirs(imgdir, exist_ok=True)
        doc = pymupdf.open(path)
        for n, page in enumerate(doc, 1):
            page.get_pixmap(dpi=a.dpi).save(os.path.join(imgdir, f"p_{n:03d}.png"))
        print(f"{name}: {doc.page_count} pages")


if __name__ == "__main__":
    main()
