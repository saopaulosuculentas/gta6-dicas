# Confere, monta e envia o site para o ar.
# Uso:  powershell -ExecutionPolicy Bypass -File publicar.ps1 "o que mudou"
param([string]$Mensagem = "Atualiza dicas")

Set-Location $PSScriptRoot

python agente\validar.py
if ($LASTEXITCODE -ne 0) { Write-Host "PAREI: a conferencia das dicas achou erro."; exit 1 }

npm run build
if ($LASTEXITCODE -ne 0) { Write-Host "PAREI: o site nao montou."; exit 1 }

# trava de seguranca: dica de exemplo nunca vai ao ar
$exemplo = Get-ChildItem dist -Recurse -Filter *.html | Select-String -Pattern '\[Exemplo\]' -List
if ($exemplo) { Write-Host "PAREI: tem dica de exemplo no site montado."; exit 1 }

# 1) guarda o conteudo (branch main)
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { git commit -q -m $Mensagem -m "Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>" }
git push -q origin main
if ($LASTEXITCODE -ne 0) { Start-Sleep -Seconds 8; git push -q origin main }
if ($LASTEXITCODE -ne 0) { Write-Host "PAREI: nao consegui enviar para o GitHub (tentei duas vezes)."; exit 1 }

# 2) envia o site montado (branch gh-pages, que e o que aparece na internet)
$remoto = git remote get-url origin
$pages = Join-Path $PSScriptRoot ".pages"
if (-not (Test-Path (Join-Path $pages ".git"))) {
  git clone -q --branch gh-pages --single-branch $remoto $pages
  if ($LASTEXITCODE -ne 0) { Write-Host "PAREI: a branch gh-pages ainda nao existe."; exit 1 }
  git -C $pages config user.name (git config user.name)
  git -C $pages config user.email (git config user.email)
}
git -C $pages config core.autocrlf false
git -C $pages config core.safecrlf false
git -C $pages pull -q
robocopy dist $pages /MIR /XD .git /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { Write-Host "PAREI: erro ao copiar o site."; exit 1 }
Set-Content -Path (Join-Path $pages ".nojekyll") -Value "" -Encoding ascii
$cname = Join-Path $PSScriptRoot "CNAME"
if (Test-Path $cname) { Copy-Item $cname (Join-Path $pages "CNAME") -Force }
git -C $pages add -A
git -C $pages diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
  git -C $pages commit -q -m $Mensagem
  git -C $pages push -q origin gh-pages
  if ($LASTEXITCODE -ne 0) { Start-Sleep -Seconds 8; git -C $pages push -q origin gh-pages }
  if ($LASTEXITCODE -ne 0) { Write-Host "PAREI: nao consegui enviar o site (tentei duas vezes)."; exit 1 }
  Write-Host "NO AR: site atualizado."
  Start-Sleep -Seconds 40   # tempo para o GitHub Pages publicar antes de avisar os buscadores
  python agente\indexnow.py
} else {
  Write-Host "NO AR: nada mudou no site desde a ultima vez."
}
