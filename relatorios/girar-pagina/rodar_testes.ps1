# Roda os testes que tocam o girar, o Dividir, o PDF e os cadernos, UM arquivo por vez
# (regra de 19/10/2026), e anota o resumo de cada um em resultado-testes.txt.
param([string[]]$Arquivos)
$raiz = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $raiz
New-Item -ItemType Directory -Force _tmp | Out-Null
$env:QT_QPA_PLATFORM = "offscreen"
$saida = Join-Path $PSScriptRoot "resultado-testes.txt"
$lista = $Arquivos | ForEach-Object { $_ -split "," } | Where-Object { $_ }
foreach ($a in $lista) {
    $linhas = & D:\programas\EditorImpressao\.venv\Scripts\python.exe -m pytest "tests\$a" -q --basetemp=_tmp\bt -p no:cacheprovider 2>&1
    $resumo = ($linhas | Select-String "passed|failed|error|no tests ran" | Select-Object -Last 1).Line
    $falhas = ($linhas | Select-String "^FAILED|^ERROR") | ForEach-Object { "    " + $_.Line }
    "$a :: $resumo" | Out-File -Append -Encoding utf8 $saida
    $falhas | Out-File -Append -Encoding utf8 $saida
}
"FIM" | Out-File -Append -Encoding utf8 $saida
