$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

python -m pip install -r requirements.txt
python src/acquire_data.py --as-of 2026-10-16
python src/analyze.py
python tests/test_outputs.py

