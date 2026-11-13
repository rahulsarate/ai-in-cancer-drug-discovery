$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}
$projectPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
& $projectPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& $projectPython make_demo.py
if ($LASTEXITCODE -ne 0) { throw 'Demo generation failed.' }
& $projectPython pipeline.py train --manifest data/demo/manifest.csv --out outputs
if ($LASTEXITCODE -ne 0) { throw 'Training failed.' }
& $projectPython -m streamlit run app.py --server.address 127.0.0.1
