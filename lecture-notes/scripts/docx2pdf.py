"""Word 파일(.docx) → PDF (눈으로 확인용). Windows는 Word(docx2pdf.ps1), 그 밖은 LibreOffice(soffice).

Usage: python -I docx2pdf.py in.docx out.pdf
둘 다 없으면 알리고 끝낸다(이때는 .docx만 넘기고, 확인을 못 했다고 사용자에게 말한다).
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def convert(src, out):
    src, out = os.path.abspath(src), os.path.abspath(out)
    if os.name == "nt" and os.path.exists(os.path.join(HERE, "docx2pdf.ps1")):
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                            os.path.join(HERE, "docx2pdf.ps1"), "-In", src, "-Out", out])
        if r.returncode == 0 and os.path.exists(out):
            return True
    office = shutil.which("soffice") or shutil.which("libreoffice")
    if office:
        d = tempfile.mkdtemp()
        subprocess.run([office, "--headless", "--convert-to", "pdf", "--outdir", d, src], capture_output=True)
        made = os.path.join(d, os.path.splitext(os.path.basename(src))[0] + ".pdf")
        if os.path.exists(made):
            shutil.move(made, out)
            return True
    return False


if __name__ == "__main__":
    ok = convert(sys.argv[1], sys.argv[2])
    print(("saved " + sys.argv[2]) if ok else "Word·LibreOffice가 없어 PDF로 바꾸지 못함 (.docx는 그대로 사용 가능)")
