# Roda a medicao inteira do layout juntado (14/10/2026), uma rodada por vez:
# aquecimento rapido nas duas copias e depois antes/depois alternados, 3 de cada.
# Para na primeira rodada que falhar (memoria, python ja rodando, erro do teste).
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$rodadas = @(
    @('antes', 'aquecimento-antes', $true),
    @('depois', 'aquecimento-depois', $true),
    @('antes', 'antes-1', $false), @('depois', 'depois-1', $false),
    @('antes', 'antes-2', $false), @('depois', 'depois-2', $false),
    @('antes', 'antes-3', $false), @('depois', 'depois-3', $false)
)
foreach ($r in $rodadas) {
    Write-Output "=== $($r[1]) ($(Get-Date -Format 'HH:mm:ss'))"
    if ($r[2]) { & "$aqui\rodar_uma.ps1" -braco $r[0] -nome $r[1] -rapido }
    else { & "$aqui\rodar_uma.ps1" -braco $r[0] -nome $r[1] }
    if ($LASTEXITCODE -ne 0) { Write-Output "Rodada $($r[1]) saiu com codigo ${LASTEXITCODE}: parei."; exit $LASTEXITCODE }
}
Write-Output "=== fim ($(Get-Date -Format 'HH:mm:ss'))"
