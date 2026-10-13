# Roda um dos scripts desta pasta com os cuidados combinados para o PC (12/10/2026):
#   - TEMP e TMP dentro da worktree (saida_teste\geometria-perguntas\tmp);
#   - espera ter 3 GB de memoria livre antes de comecar (ate 10 minutos);
#   - o Python e o da .venv da pasta principal; a pasta de trabalho e a raiz da worktree.
# Uso (de qualquer pasta):  powershell -File rodar.ps1 passo2_imagens.py g7 g8m
param([Parameter(Mandatory = $true)][string]$script, [Parameter(ValueFromRemainingArguments = $true)][string[]]$resto)
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$raiz = (Resolve-Path "$aqui\..\..\..\..").Path
$tmp = "$raiz\saida_teste\geometria-perguntas\tmp"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TEMP = $tmp; $env:TMP = $tmp; $env:PYTHONIOENCODING = 'utf-8'
$livre = 0
for ($i = 0; $i -lt 40; $i++) {
    $livre = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 2)
    if ($livre -ge 3) { break }
    Start-Sleep -Seconds 15
}
Write-Output "memoria livre: $livre GB"
if ($livre -lt 3) { Write-Output 'Menos de 3 GB livres depois de 10 minutos: parei.'; exit 3 }
Set-Location $raiz
& 'D:\programas\EditorImpressao\.venv\Scripts\python.exe' "$aqui\$script" @resto
exit $LASTEXITCODE
