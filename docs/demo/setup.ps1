# Hidden setup for the tapes: run qrbar from this checkout in a scratch copy of examples/.
# Record from the repo root: vhs docs/demo/<name>.tape
$env:PYTHONIOENCODING = "utf-8"
$global:repo = (Resolve-Path "$PSScriptRoot/../..").Path
$demo = "$env:TEMP/qrbar-demo"
Remove-Item -Recurse -Force -ErrorAction Ignore $demo
Copy-Item -Recurse "$repo/examples" $demo
Set-Location $demo
function global:qrbar { uv run -q --project $repo qrbar @args }
function global:prompt { "> " }
