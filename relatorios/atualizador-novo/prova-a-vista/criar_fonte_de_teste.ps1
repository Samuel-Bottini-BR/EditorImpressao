# Cria o arquivo que aponta o programa instalado para as versoes de prova (prova a vista do atualizador novo,
# 25/11/2026). NAO e parte do programa do Kaique.
#
# QUEM RODA E QUANDO: a gerente, no comeco da prova (passo 0), com UMA pergunta do Windows (o Samuel clica "Sim"):
#   Start-Process powershell.exe -Verb RunAs -Wait -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','<este arquivo>'
# POR QUE COM LICENCA: o programa so aceita este arquivo se o dono for o grupo Administradores ou o sistema
# (atualizacao.fonte_de_teste, DONOS_ACEITOS); uma conta comum consegue criar arquivo no ProgramData, mas fica ela de
# dona, e o programa ignora (o notebook do Kaique nunca tem este arquivo: la as versoes vem do GitHub).
#
# O QUE FAZ: cria SO a pasta C:\ProgramData\EditorImpressao (se faltar) e o arquivo fonte-de-teste.txt, com uma linha: a
# pasta da fonte da prova. NAO cria a subpasta atualizacao\ (o programa cria, na conta do Samuel, e precisa ser o dono
# dela para gravar o registro). Depois le de volta o que ficou e o dono, e escreve num registro ao lado da prova.
# -Destino e so para o ensaio (uma pasta de ensaio, sem licenca).
param(
    [string]$Destino = "C:\ProgramData\EditorImpressao",
    [string]$Fonte = "C:\EditorImpressaoProva\prova-a-vista-25-11\fonte",
    [string]$Registro = "C:\EditorImpressaoProva\prova-a-vista-25-11\registros\criar_fonte_de_teste.txt"
)
$ErrorActionPreference = "Stop"
$linhas = @()
try {
    if (-not (Test-Path -LiteralPath $Fonte -PathType Container)) { throw "a pasta da fonte nao existe: $Fonte" }
    New-Item -ItemType Directory -Force -Path $Destino | Out-Null
    $arquivo = Join-Path $Destino "fonte-de-teste.txt"
    [System.IO.File]::WriteAllText($arquivo, $Fonte + "`r`n", (New-Object System.Text.UTF8Encoding($false)))
    $lido = [System.IO.File]::ReadAllText($arquivo).Trim()
    $dono = (Get-Acl -LiteralPath $arquivo).GetOwner([System.Security.Principal.SecurityIdentifier]).Value
    $linhas += "$(Get-Date -Format 'dd/MM/yyyy HH:mm:ss') criado $arquivo"
    $linhas += "  diz: $lido"
    $linhas += "  dono: $dono (o programa aceita S-1-5-32-544 ou S-1-5-18)"
    $linhas += "  confere: $(($lido -eq $Fonte) -and (@('S-1-5-32-544','S-1-5-18') -contains $dono))"
} catch {
    $linhas += "$(Get-Date -Format 'dd/MM/yyyy HH:mm:ss') NAO CRIADO: $($_.Exception.Message)"
}
$linhas | ForEach-Object { Write-Output $_ }
New-Item -ItemType Directory -Force -Path (Split-Path $Registro) | Out-Null
Add-Content -LiteralPath $Registro -Value $linhas -Encoding UTF8
