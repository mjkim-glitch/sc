# Word로 .docx를 PDF로 내보낸다 (레이아웃 확인용).
# Usage: powershell -File docx2pdf.ps1 -In 입력.docx -Out 출력.pdf
param([Parameter(Mandatory)][string]$In, [Parameter(Mandatory)][string]$Out)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open((Resolve-Path $In).Path, $false, $true)
    $doc.ExportAsFixedFormat([IO.Path]::GetFullPath($Out), 17)  # 17 = PDF
    $doc.Close($false)
} finally {
    $word.Quit()
}
Write-Output "saved $Out"
