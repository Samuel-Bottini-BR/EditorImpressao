# Roda UMA execucao do teste de velocidade numa das duas copias do programa.
# Uso:  rodar_uma.ps1 -braco antes|depois -nome <nome da pasta> [-rapido]
#   antes  = worktree velocidade-antes (origin/fase-1, 9c51801)
#   depois = worktree endireitar       (fase2-endireitar-2, 44cbf21)
# Nao grava nada na pasta principal: so LE o livro e usa o Python da .venv dela.
# TEMP e TMP ficam dentro da propria worktree (saida_teste\tmp-velocidade).
# Antes de rodar: espera ter 3 GB de memoria livre e anota hora, memoria e uso do processador.
param(
    [Parameter(Mandatory = $true)][ValidateSet('antes', 'depois')][string]$braco,
    [Parameter(Mandatory = $true)][string]$nome,
    [switch]$rapido
)
$ErrorActionPreference = 'Stop'
$raiz = 'D:\programas\EditorImpressao'
$copias = @{
    antes  = "$raiz\.claude\worktrees\velocidade-antes"
    depois = "$raiz\.claude\worktrees\endireitar"
}
$copia = $copias[$braco]
$python = "$raiz\.venv\Scripts\python.exe"
$livro = "$raiz\gabarito\velocidade\marial_300.pdf"
$saida = "$raiz\.claude\worktrees\endireitar\relatorios\velocidade-g6-2026-10-12\rodadas\$nome"
$temp = "$copia\saida_teste\tmp-velocidade"

if (Test-Path $saida) { Write-Output "A pasta $saida ja existe: parei para nao misturar rodadas."; exit 4 }
if (Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $python }) {
    Write-Output 'Ja ha um python da .venv do projeto rodando: parei (uma rodada por vez).'; exit 5
}
New-Item -ItemType Directory -Force -Path $saida | Out-Null
New-Item -ItemType Directory -Force -Path $temp | Out-Null

# memoria: espera ate 20 minutos por 3 GB livres
$livre = 0
for ($i = 0; $i -lt 40; $i++) {
    $livre = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 2)
    if ($livre -ge 3) { break }
    Start-Sleep -Seconds 30
}
if ($livre -lt 3) { Write-Output "Memoria livre $livre GB (menos de 3 GB) depois de 20 minutos: parei."; exit 3 }

# uso do processador nos 5 segundos antes de comecar (media de 5 leituras)
$cargas = 1..5 | ForEach-Object {
    (Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average
    Start-Sleep -Seconds 1
}
$carga = [math]::Round(($cargas | Measure-Object -Average).Average, 0)
$commit = (git -C $copia rev-parse --short HEAD)
$sujo = @(git -C $copia status --porcelain).Count
$inicio = Get-Date

$env:TEMP = $temp
$env:TMP = $temp
$env:PYTHONUNBUFFERED = '1'
$env:PYTHONIOENCODING = 'utf-8'
$argumentos = @('teste_velocidade.py', "`"$livro`"", '--saida', "`"$saida`"")
if ($rapido) { $argumentos += '--rapido' }
$processo = Start-Process -FilePath $python -ArgumentList $argumentos -WorkingDirectory $copia `
    -RedirectStandardOutput "$saida\terminal.txt" -RedirectStandardError "$saida\terminal-erros.txt" `
    -NoNewWindow -Wait -PassThru
$fim = Get-Date
$livreDepois = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 2)

$anotacao = [ordered]@{
    braco                  = $braco
    nome                   = $nome
    rapido                 = [bool]$rapido
    copia                  = $copia
    commit                 = $commit
    arquivos_mexidos       = $sujo
    inicio                 = $inicio.ToString('yyyy-MM-dd HH:mm:ss')
    fim                    = $fim.ToString('yyyy-MM-dd HH:mm:ss')
    minutos                = [math]::Round(($fim - $inicio).TotalMinutes, 1)
    memoria_livre_antes_gb = $livre
    memoria_livre_depois_gb = $livreDepois
    processador_antes_pct  = $carga
    codigo_de_saida        = $processo.ExitCode
}
$anotacao | ConvertTo-Json | Out-File -FilePath "$saida\anotacao.json" -Encoding utf8
$anotacao | ConvertTo-Json
Get-Content "$saida\terminal.txt" -Encoding UTF8 | Where-Object { $_ -notmatch '\|' } | Select-Object -Last 30
exit $processo.ExitCode
