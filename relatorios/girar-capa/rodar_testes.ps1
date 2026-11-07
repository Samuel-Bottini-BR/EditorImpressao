# Roda os testes do girar, das decisoes, da tira, do Dividir, do PDF e o teste novo, UM arquivo
# por vez (regra de 19/10/2026), sem janela na tela (offscreen) e com LOCALAPPDATA numa pasta
# so deste trabalho; anota o resumo de cada um em resultado-testes.txt.
param([string]$Titulo = "rodada")
$raiz = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $raiz
$tmp = Join-Path $env:TEMP "girar-capa-testes"
New-Item -ItemType Directory -Force $tmp | Out-Null
$env:QT_QPA_PLATFORM = "offscreen"
$env:LOCALAPPDATA = Join-Path $tmp "localappdata"
New-Item -ItemType Directory -Force $env:LOCALAPPDATA | Out-Null
$saida = Join-Path $PSScriptRoot "resultado-testes.txt"
$fixos = @("test_decisoes_girar_capa.py", "test_girar.py", "test_girar_na_tela.py",
  "test_girar_cartoes_e_previas.py", "test_ajustar_pedaco_na_folha_girada.py",
  "test_recomeco_limpa_o_historico.py", "test_paineis_na_tela.py", "test_pipeline_folha.py",
  "test_corte_previa_igual_pdf.py", "test_zonas_na_folha.py", "test_camadas.py",
  "test_impressao.py", "test_borda_preta.py", "test_dividir_na_tela.py",
  "test_dividir_no_programa.py", "test_cartoes_e_previas.py", "test_historico_depois_de_reabrir.py",
  "test_cadernos.py", "test_caderno_segue_as_etapas.py")
$decisoes = Get-ChildItem tests\test_decisoes*.py | ForEach-Object { $_.Name } |
  Where-Object { $fixos -notcontains $_ }
"== $Titulo ($(Get-Date -Format 'dd/MM/yyyy HH:mm')), commit $(git rev-parse --short HEAD) ==" |
  Out-File -Append -Encoding utf8 $saida
foreach ($a in ($fixos + $decisoes)) {
    $linhas = & D:\programas\EditorImpressao\.venv\Scripts\python.exe -m pytest "tests\$a" -q --basetemp="$tmp\bt" -p no:cacheprovider 2>&1
    $resumo = ($linhas | Select-String "passed|failed|error|no tests ran" | Select-Object -Last 1).Line
    $falhas = ($linhas | Select-String "^FAILED|^ERROR") | ForEach-Object { "    " + $_.Line }
    "$a :: $resumo" | Out-File -Append -Encoding utf8 $saida
    $falhas | Out-File -Append -Encoding utf8 $saida
}
"FIM" | Out-File -Append -Encoding utf8 $saida
