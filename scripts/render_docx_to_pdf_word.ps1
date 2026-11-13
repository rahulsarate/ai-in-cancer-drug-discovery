param(
    [string]$DocxPath = "docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report.docx",
    [string]$PdfPath = "docs/pan_cancer_emt_state_atlas/clinician_pan_cancer_emt_state_atlas_report_word_rendered.pdf"
)

$ErrorActionPreference = "Stop"
$docx = (Resolve-Path -LiteralPath $DocxPath).Path
$pdf = Join-Path (Resolve-Path -LiteralPath (Split-Path -Parent $PdfPath)).Path (Split-Path -Leaf $PdfPath)

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$document = $null
try {
    $document = $word.Documents.Open($docx, $false, $true)
    $document.ExportAsFixedFormat($pdf, 17)
    Write-Output "Wrote $pdf"
}
finally {
    if ($document -ne $null) {
        $document.Close($false)
    }
    $word.Quit()
}
