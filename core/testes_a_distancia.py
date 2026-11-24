"""Liga e desliga os testes a distancia no notebook do Kaique.

De onde vem (frente do notebook do Kaique, 16/11/2026; decisoes no Livro
docs/plano/DECISOES.md):
  D-705  testes a distancia pelo comando de longe do Windows (Servidor
         OpenSSH), SO pela rede do Tailscale, SEM porta de API dentro do
         programa; uma opcao nas Configuracoes liga e desliga.
  D-711  liga sozinho com o Windows; entra com SENHA, nao com chave.
  D-712  a opcao vem LIGADA DE FABRICA; o instalador nao pergunta nada.
  D-717  conta do Windows SO para os testes, SEM administrador, ESCONDIDA da
         tela de entrada; os projetos de teste nunca se misturam com os do
         Kaique.
  D-721  na primeira abertura, uma janela pede a senha; sem senha, os testes
         ficam desligados; da para por a senha depois nas Configuracoes.
  D-722  testar no PC do Samuel e, no fim, DESFAZER tudo (etapa 5).
  D-731  desinstalar o programa tira junto o que os testes a distancia
         puseram (o OpenSSH, se foi o programa que instalou; a regra do
         firewall; a conta de testes e o perfil dela). Os projetos do Kaique
         (%LOCALAPPDATA%\\EditorImpressao) nunca sao tocados.
  D-733  alternativa B do plano-d732.md: o `ligar` cria uma tarefa do Windows
         "desfazer" que roda como o sistema e que a conta comum pode mandar
         rodar; o gancho de desinstalar (sem administrador, 30 s) so manda.
  D-731, pergunta (a) do relatorio da construcao (pedido da gerente,
         17/11/2026): a tarefa "desfazer" existe SEMPRE, e nao so quando os
         testes foram ligados. A pergunta do Windows da primeira abertura
         (D-733/D-735; o antigo --preparar-o-computador, que saiu com o
         atualizador novo em 23/11/2026: hoje ninguem a cria na primeira
         abertura, e ela so nasce quando os testes sao ligados) a criava com o
         plano curto (`plano_de_desfazer(testes_ligados=False)`: so as nossas
         tarefas); o `ligar` a refaz com o plano inteiro. Nos dois, o desfazer
         apaga tambem a tarefa da atualizacao ("Procurar versao nova") e a si
         mesmo: o gancho de desinstalar nao consegue (roda sem administrador).

O CADERNINHO DO ANTES (D-731, 17/11/2026). O primeiro passo do `ligar`, ja
como administrador, anota em C:\\ProgramData\\EditorImpressao\\testes-a-distancia
\\antes.json o que o computador ja tinha (o OpenSSH, o servico, a regra larga,
uma conta com o nosso nome, a pasta ssh). So na primeira vez: um desligar e
ligar de novo nao faz o programa achar que o OpenSSH "ja estava la". A pasta
fica so de leitura para as contas comuns. Desligar e desfazer leem o
caderninho para tirar SO o que foi nosso; sem caderninho, o OpenSSH nunca e
tirado.

A REGRA NUM LUGAR SO (CLAUDE.md 11.12, sem gambiarra). Este arquivo e o unico
lugar que sabe QUAIS comandos ligam, desligam e desfazem os testes a distancia.
Todos os caminhos da tela (a janela da senha na primeira abertura, a caixinha
das Configuracoes, o botao "Por a senha") chamam `ligar`/`desligar` daqui -
nenhum monta comando por conta propria. O desfazer tambem e um so
(`plano_de_desfazer`): a tarefa "desfazer" roda exatamente esse plano, montado
por `montar_script`, e a etapa 5 (D-722) usa o mesmo. Tirar as nossas linhas do
sshd_config e uma funcao so (`_comando_tirar_o_bloco`), e "foi nosso?" tambem
(`_so_se_o_openssh_foi_nosso`, `_so_se_a_conta_foi_nossa`).

A PECA QUE FALA COM O WINDOWS esta isolada em `Executor`. `ExecutorWindows` e
a de verdade (uma pergunta de administrador so, para todos os passos). Os
testes trocam o executor por um de mentira que anota os comandos que SERIAM
dados, sem tocar o Windows. Por isso nada aqui muda o computador por si: quem
muda e o `ExecutorWindows`, e so na producao.

A SENHA nunca aparece na linha de comando (outros programas enxergariam a
linha de comando). Nos passos ela e a variavel `$SenhaDosTestes`; o
`ExecutorWindows` a entrega por dentro, cifrada pelo proprio Windows (DPAPI da
conta do usuario), e nao a guarda em lugar nenhum alem da conta criada com ela.

Este arquivo NAO importa nada de ui/ (core/__init__.py). Importa `configuracoes`
(raiz, nao ui/) so para lembrar o estado da opcao, como fazem outros assuntos.
"""

from __future__ import annotations

import base64
import os
import sys
from dataclasses import dataclass, field

import configuracoes

# --- nomes fixos (caminho em disco / Windows, SEM acento) --------------------
# Mudar qualquer um destes muda a conta, a regra do firewall ou a chave do
# registro que o programa cria no Windows. Nao mudar sem o Samuel.
NOME_DA_CONTA = "EditorTestes"            # a conta so dos testes (D-717)
NOME_DA_REGRA = "EditorImpressao-Testes"  # a regra do firewall que abre so o Tailscale (D-705)
REGRA_LARGA_DO_OPENSSH = "OpenSSH-Server-In-TCP"  # a que a instalacao cria e libera a porta a todos
CAPACIDADE_OPENSSH = "OpenSSH.Server~~~~0.0.1.0"   # o recurso do Windows a instalar
SID_USUARIOS = "S-1-5-32-545"             # o grupo "Usuarios" (sem administrador), igual em qualquer idioma
PORTA_SSH = 22
# A faixa de enderecos do Tailscale (IPv4 100.64.0.0/10 e IPv6; tailscale.com/kb/1015).
# SO estes entram; o Wi-Fi da casa (ex.: 192.168.x) nao (D-705).
FAIXAS_DO_TAILSCALE = "100.64.0.0/10,fd7a:115c:a1e0::/48"
PLACA_DO_TAILSCALE = "Tailscale"          # prende a regra a placa do Tailscale
SSHD_CONFIG = r"C:\ProgramData\ssh\sshd_config"
CHAVE_USERLIST = (r"HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion"
                  r"\Winlogon\SpecialAccounts\UserList")
VARIAVEL_DA_SENHA = "$SenhaDosTestes"     # o lugar da senha nos passos (NUNCA o texto dela)
# A descricao que o ligar da a conta: e por ela (e pelo caderninho) que o
# desfazer sabe que a conta EditorTestes e nossa. Mudar faz o desfazer deixar
# para tras as contas criadas pelas versoes de antes.
DESCRICAO_DA_CONTA = "Conta so para os testes a distancia"
SID_SISTEMA = "S-1-5-18"
SID_ADMINISTRADORES = "S-1-5-32-544"

# --- D-731 (17/11/2026): o caderninho do antes e a tarefa "desfazer" ----------
# Tudo numa pasta do ProgramData que so o sistema e os administradores gravam
# (o `ligar` protege a pasta). Os testes trocam estes caminhos por pastas
# temporarias; as funcoes abaixo os leem na hora.
PASTA_SSH = r"C:\ProgramData\ssh"
PASTA_DOS_TESTES = r"C:\ProgramData\EditorImpressao\testes-a-distancia"
PASTA_DAS_TAREFAS = "EditorImpressao"     # a mesma pasta da tarefa da atualizacao
NOME_DA_TAREFA_DO_DESFAZER = "Desfazer testes a distancia"
# As linhas que o ligar poe no sshd_config ficam entre estas duas marcas: o
# desfazer tira so o que esta entre elas (a linha de fabrica
# "#PasswordAuthentication yes" e as linhas do dono ficam). Mudar as marcas
# faz o desfazer nao achar as linhas postas pelas versoes de antes.
MARCA_DO_INICIO = "# --- Editor de Impressao: inicio ---"
MARCA_DO_FIM = "# --- Editor de Impressao: fim ---"
LINHAS_DO_SSHD = (f"AllowUsers {NOME_DA_CONTA}", "PasswordAuthentication yes", "MaxAuthTries 3")
# O gancho de desinstalar do Velopack e morto depois de 30 s: mandar rodar a
# tarefa tem de voltar bem antes disso.
TEMPO_MAXIMO_NO_GANCHO = 20


def caminho_do_antes() -> str:
    """O caderninho do antes (D-731): o que o computador ja tinha antes do 1o ligar."""
    return PASTA_DOS_TESTES + r"\antes.json"


def caminho_do_script_do_desfazer() -> str:
    """O script que a tarefa "desfazer" roda (gravado pelo ligar)."""
    return PASTA_DOS_TESTES + r"\desfazer.ps1"


def caminho_do_registro_do_desfazer() -> str:
    """A lista do que o desfazer fez, passo a passo (a gerente le pelo comando de longe; D-722)."""
    return PASTA_DOS_TESTES + r"\o-que-foi-desfeito.txt"


def nome_da_tarefa_do_desfazer() -> str:
    """O nome completo da tarefa, como o schtasks o recebe."""
    return f"{PASTA_DAS_TAREFAS}\\{NOME_DA_TAREFA_DO_DESFAZER}"

# Chaves das Configuracoes (configuracoes.PADROES tem os valores de fabrica).
CHAVE_LIGADO = "testes_a_distancia_ligado"              # intencao do Kaique (de fabrica True, D-712)
CHAVE_PRONTO = "testes_a_distancia_pronto"              # o lado do Windows ja foi montado?
CHAVE_SENHA_PERGUNTADA = "testes_a_distancia_senha_perguntada"  # a janela da 1a vez ja apareceu?


@dataclass
class Passo:
    """Um passo do plano: o que ele faz (em portugues) e o comando do Windows.

    `precisa_senha` marca o passo que usa `$SenhaDosTestes` - a prova confere
    que a senha nunca vira texto no comando.
    `so_se_tudo_certo` marca o passo que so roda se nenhum anterior falhou
    (o fim do desfazer: apagar a tarefa e o caderninho so quando tudo saiu).

    O nome e o comando ficam em ASCII: o PowerShell do Windows le o script
    sem marca de UTF-8 como ANSI.
    """

    nome: str
    comando: str
    precisa_senha: bool = False
    so_se_tudo_certo: bool = False


@dataclass
class Resultado:
    """O que o executor devolve.

    ok          deu certo (todos os passos aplicados).
    cancelado   a pessoa disse "Nao" a pergunta do Windows (erro 1223): nada
                foi instalado (D-705/estudo 2.3).
    mensagem    frase em portugues para a tela, quando nao deu certo (regra 3.3:
                nunca rastro de erro na tela).
    passos      o que foi (ou seria) feito, para o registro "o que o teste fez".
    """

    ok: bool
    cancelado: bool = False
    mensagem: str = ""
    passos: list[Passo] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pedacos de comando usados por mais de um plano (um lugar so, CLAUDE.md 11.12)
# ---------------------------------------------------------------------------

def _ler_o_antes() -> str:
    """Le o caderninho do antes para `$antes` (ou `$null`, se nao ha caderninho)."""
    arquivo = caminho_do_antes()
    return (f"$antes = $null; if (Test-Path -LiteralPath '{arquivo}')"
            f" {{ $antes = Get-Content -Raw -LiteralPath '{arquivo}' | ConvertFrom-Json }}")


def _so_se_o_openssh_foi_nosso(comando: str) -> str:
    """Roda `comando` so se o caderninho diz que o OpenSSH NAO existia antes do 1o ligar.

    Sem caderninho, nunca (D-731: "se foi o programa que instalou"). Dentro de
    `comando`, `$antes` ja esta lido.
    """
    return (f"{_ler_o_antes()}; if ($antes -and -not $antes.openssh_ja_existia) {{ {comando} }}"
            f" else {{ Anotar 'FICA | o Servidor OpenSSH ja existia antes (ou nao ha caderninho)' }}")


def _conta_e_nossa() -> str:
    """Expressao do PowerShell: a conta EditorTestes existe e tem a descricao que o ligar da?"""
    return (f"((Get-LocalUser -Name {NOME_DA_CONTA} -ErrorAction SilentlyContinue).Description"
            f" -eq '{DESCRICAO_DA_CONTA}')")


def _so_se_a_conta_foi_nossa(comando: str) -> str:
    """Roda `comando` so se a conta EditorTestes e a nossa: a descricao e a nossa e o caderninho nao
    anotou uma conta de outro com esse nome. Sem caderninho, vale so a descricao (plano.md, secao 5)."""
    return (f"{_ler_o_antes()}; if ({_conta_e_nossa()} -and -not ($antes -and $antes.conta_de_outro_existia))"
            f" {{ {comando} }} else {{ Anotar 'FICA | a conta {NOME_DA_CONTA} nao e do programa (ou nao existe)' }}")


# A expressao regular que acha o nosso bloco no sshd_config: da marca do
# inicio ate a marca do fim, linhas inteiras, com o fim de linha que o arquivo
# tiver (\n ou \r\n).
_BLOCO_DO_SSHD = (r"(?m)^" + MARCA_DO_INICIO + r"\r?\n(?:.*\r?\n)*?" + MARCA_DO_FIM + r"(?:\r?\n|$)")


def _comando_tirar_o_bloco(caminho: str) -> str:
    """Tira do arquivo SO o que esta entre as nossas marcas; o resto fica igual, letra por letra.

    Usado ao ligar de novo (nao repetir as linhas, B3), ao desligar um OpenSSH
    que ja era do dono (B4) e ao desfazer (D-731).
    """
    return (f"if (Test-Path -LiteralPath '{caminho}') {{ $t = [IO.File]::ReadAllText('{caminho}');"
            f" $t = [regex]::Replace($t, '{_BLOCO_DO_SSHD}', ''); [IO.File]::WriteAllText('{caminho}', $t) }}")


def _comando_por_o_bloco(caminho: str) -> str:
    """Poe as nossas linhas entre as marcas ANTES do primeiro "Match" do arquivo (B2).

    No sshd_config, o que vem depois de um "Match" vale so para quem o Match
    escolhe: o arquivo de fabrica do Windows termina com "Match Group
    administrators", e as linhas no fim valeriam so para os administradores.
    Sem "Match", vao no fim. Tira antes um bloco antigo (B3: nao repete).
    """
    bloco = " + $nl + ".join(f"'{linha}'" for linha in (MARCA_DO_INICIO, *LINHAS_DO_SSHD, MARCA_DO_FIM))
    return (f"{_comando_tirar_o_bloco(caminho)}; $t = '';"
            f" if (Test-Path -LiteralPath '{caminho}') {{ $t = [IO.File]::ReadAllText('{caminho}') }};"
            f" $nl = \"`n\"; if ($t.Contains(\"`r`n\")) {{ $nl = \"`r`n\" }};"
            f" $bloco = {bloco} + $nl;"
            f" $m = [regex]::Match($t, '(?im)^[ \\t]*Match[ \\t]');"
            f" if ($m.Success) {{ $t = $t.Insert($m.Index, $bloco) }}"
            f" else {{ if ($t.Length -gt 0 -and -not $t.EndsWith(\"`n\")) {{ $t = $t + $nl }}; $t = $t + $bloco }};"
            f" [IO.File]::WriteAllText('{caminho}', $t)")


def _comando_anotar_o_antes() -> str:
    """O 1o passo do ligar (D-731): grava o caderninho, SO se ainda nao ha um valido, e protege a pasta.

    Um caderninho cujo dono nao e o sistema nem os administradores foi posto
    por uma conta comum: nao vale e e gravado de novo. Depois, a pasta fica com
    dono "administradores" e so de leitura para os usuarios comuns.
    """
    pasta = PASTA_DOS_TESTES
    arquivo = caminho_do_antes()
    campos = "; ".join([
        "openssh_ja_existia = (([string]$cap.State -eq 'Installed') -or [bool]$svc)",
        "sshd_inicio = $(if ($svc) { [string]$svc.StartType } else { '' })",
        "sshd_rodando = [bool]($svc -and ([string]$svc.Status -eq 'Running'))",
        "regra_larga_existia = [bool]$regra",
        "regra_larga_ligada = [bool]($regra -and ([string]$regra.Enabled -eq 'True'))",
        f"conta_de_outro_existia = [bool]($conta -and ($conta.Description -ne '{DESCRICAO_DA_CONTA}'))",
        f"userlist_existia = [bool](Test-Path -Path '{CHAVE_USERLIST}')",
        f"pasta_ssh_existia = [bool](Test-Path -LiteralPath '{PASTA_SSH}')",
        "pasta_ssh_itens = $itens",
        "quando = (Get-Date -Format s)",
    ])
    return (f"$pasta = '{pasta}'; $arq = '{arquivo}';"
            f" if (-not (Test-Path -LiteralPath $pasta)) {{ New-Item -ItemType Directory -Path $pasta -Force | Out-Null }};"
            f" $vale = $false;"
            f" if (Test-Path -LiteralPath $arq) {{ $dono = (Get-Acl -LiteralPath $arq).GetOwner("
            f"[System.Security.Principal.SecurityIdentifier]).Value;"
            f" $vale = ($dono -eq '{SID_SISTEMA}' -or $dono -eq '{SID_ADMINISTRADORES}') }};"
            f" if (-not $vale) {{"
            f" $cap = Get-WindowsCapability -Online -Name {CAPACIDADE_OPENSSH};"
            f" $svc = Get-Service -Name sshd -ErrorAction SilentlyContinue;"
            f" $regra = Get-NetFirewallRule -Name {REGRA_LARGA_DO_OPENSSH} -ErrorAction SilentlyContinue;"
            f" $conta = Get-LocalUser -Name {NOME_DA_CONTA} -ErrorAction SilentlyContinue;"
            f" $itens = @(); if (Test-Path -LiteralPath '{PASTA_SSH}')"
            f" {{ $itens = @(Get-ChildItem -LiteralPath '{PASTA_SSH}' -Recurse -Force -Name) }};"
            f" $novo = [ordered]@{{ {campos} }};"
            f" $novo | ConvertTo-Json | Set-Content -LiteralPath $arq -Encoding UTF8 }};"
            f" {_comando_proteger_a_pasta()}")


def xml_da_tarefa_do_desfazer() -> str:
    """O XML da tarefa "desfazer" (D-731/D-733): sem gatilho (so roda quando mandam), como o proprio
    sistema (S-1-5-18), escondida, sem janela; roda o script gravado pelo ligar. Uma linha so, em ASCII."""
    script = caminho_do_script_do_desfazer()
    return ('<?xml version="1.0" encoding="UTF-16"?>'
            '<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">'
            '<RegistrationInfo><Description>Editor de Impressao: desfaz o que os testes a distancia puseram'
            ' no computador. Chamada ao desinstalar o programa.</Description></RegistrationInfo>'
            f'<Principals><Principal id="Sistema"><UserId>{SID_SISTEMA}</UserId>'
            '<RunLevel>HighestAvailable</RunLevel></Principal></Principals>'
            '<Settings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>'
            '<DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>'
            '<StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>'
            '<AllowStartOnDemand>true</AllowStartOnDemand><Enabled>true</Enabled><Hidden>true</Hidden>'
            '<ExecutionTimeLimit>PT1H</ExecutionTimeLimit></Settings>'
            '<Actions Context="Sistema"><Exec><Command>powershell.exe</Command>'
            '<Arguments>-NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden'
            f' -File "{script}"</Arguments></Exec></Actions></Task>')


# A licenca da tarefa "desfazer" (SDDL): a conta de testes e NEGADA primeiro
# (D-717: um teste nao pode mudar o Windows); o sistema e os administradores
# mandam em tudo; quem entrou no Windows (AU) pode ler e mandar rodar - e
# assim que o gancho de desinstalar, na conta do Kaique e sem administrador,
# consegue dispara-la. A tarefa so roda o nosso script, numa pasta que so o
# administrador grava.
# Sem a conta de testes (a primeira abertura, antes de qualquer ligar), so
# falta a negacao; o `ligar` refaz a tarefa ja com ela.
_LICENCA_SEM_A_CONTA = "D:(A;;FA;;;SY)(A;;FA;;;BA)(A;;GRGX;;;AU)"
_LICENCA_DA_TAREFA = "D:(D;;FA;;;$sid)" + _LICENCA_SEM_A_CONTA[2:]


def _comando_preparar_o_desfazer(testes_ligados: bool = True) -> str:
    """Grava o script do desfazer e cria (ou refaz) a tarefa que o roda (D-731/D-733).

    O UNICO jeito de criar a tarefa "desfazer" (CLAUDE.md 11.12). Dois caminhos:
      - o ultimo passo do `ligar` (testes_ligados=True): o plano inteiro;
      - a pergunta do Windows da primeira abertura (`plano_de_preparar_o_desfazer`,
        testes_ligados=False): o plano curto, so as nossas tarefas.
    O script e `montar_script(plano_de_desfazer(...), ...)`, o mesmo da etapa 5,
    levado em base64 (um texto so, sem aspas para escapar). Cada ligar grava de
    novo: a tarefa sempre roda o desfazer da versao que ligou por ultimo.
    A licenca nega a conta de testes quando ela existe (D-717); na primeira
    abertura ela ainda nao existe.
    Arriscado: gravar o plano curto por cima do inteiro (a conta e o OpenSSH
    ficariam para tras ao desinstalar): por isso o plano curto so entra pela
    porta de `plano_de_preparar_o_desfazer`, que confere o caderninho antes.
    """
    script = montar_script(plano_de_desfazer(testes_ligados), caminho_do_registro_do_desfazer(),
                           continuar_depois_de_erro=True)
    codificado = base64.b64encode(script.encode("utf-8")).decode("ascii")
    return (f"[IO.File]::WriteAllText('{caminho_do_script_do_desfazer()}',"
            f" [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{codificado}')),"
            f" (New-Object System.Text.UTF8Encoding $true));"
            f" Register-ScheduledTask -Xml '{xml_da_tarefa_do_desfazer()}' -TaskName '{NOME_DA_TAREFA_DO_DESFAZER}'"
            f" -TaskPath '\\{PASTA_DAS_TAREFAS}\\' -Force | Out-Null;"
            f" $u = Get-LocalUser -Name {NOME_DA_CONTA} -ErrorAction SilentlyContinue;"
            f" if ($u) {{ $sid = $u.SID.Value; $licenca = \"{_LICENCA_DA_TAREFA}\" }}"
            f" else {{ $licenca = '{_LICENCA_SEM_A_CONTA}' }};"
            f" $agenda = New-Object -ComObject Schedule.Service; $agenda.Connect();"
            f" $agenda.GetFolder('\\{PASTA_DAS_TAREFAS}').GetTask('{NOME_DA_TAREFA_DO_DESFAZER}')"
            f".SetSecurityDescriptor($licenca, 0)")


def _comando_criar_e_proteger_a_pasta() -> str:
    """Cria a pasta dos testes a distancia (se falta) e a deixa com dono "administradores", so de leitura
    para as contas comuns. Usado pelo 1o passo do ligar (`_comando_anotar_o_antes`) e pela primeira
    abertura (`plano_de_preparar_o_desfazer`): o script do desfazer, que roda como o sistema, mora nela,
    e uma conta comum nunca pode troca-lo. Arriscado: afrouxar a licenca (uma conta comum que grava ali
    roda o que quiser como o sistema)."""
    return (f"$pasta = '{PASTA_DOS_TESTES}';"
            f" if (-not (Test-Path -LiteralPath $pasta)) {{ New-Item -ItemType Directory -Path $pasta -Force | Out-Null }};"
            f" {_comando_proteger_a_pasta()}")


def _comando_proteger_a_pasta() -> str:
    """O pedaco do icacls (a pasta ja esta em `$pasta`): dono "administradores"; sistema e administradores
    tudo; o grupo Usuarios so le."""
    return (f"$global:LASTEXITCODE = 0;"
            f" icacls $pasta /setowner '*{SID_ADMINISTRADORES}' /T /C /Q | Out-Null;"
            f" icacls $pasta /inheritance:r /grant:r '*{SID_SISTEMA}:(OI)(CI)F' '*{SID_ADMINISTRADORES}:(OI)(CI)F'"
            f" '*{SID_USUARIOS}:(OI)(CI)RX' /T /C /Q | Out-Null;"
            f" if ($LASTEXITCODE) {{ throw 'nao consegui proteger a pasta dos testes a distancia' }}")


def plano_de_preparar_o_desfazer() -> list[Passo]:
    """O que a pergunta do Windows da primeira abertura faz pelo desfazer (D-731, pergunta (a)).

    Cria a tarefa "desfazer" SEMPRE, com ou sem os testes a distancia, para
    que desinstalar apague tambem a tarefa da atualizacao. Com o plano curto
    (`plano_de_desfazer(testes_ligados=False)`), e so se os testes nunca foram
    ligados: havendo o caderninho do antes (o 1o passo do `ligar` o grava; o
    desfazer inteiro o apaga), a tarefa ja tem o plano inteiro e fica como
    esta. Assim, a pergunta da primeira abertura que volta depois de um "Nao"
    (D-741), com os testes ja ligados pelas Configuracoes, nao estraga o desfazer.
    Quem chama: `preparar_o_desfazer` (era o --preparar-o-computador do
    atualizador antigo, que saiu em 23/11/2026; hoje ninguem do programa chama).
    """
    return [
        Passo("Criar e proteger a pasta do desfazer", _comando_criar_e_proteger_a_pasta()),
        Passo("Preparar o desfazer para quando o programa for desinstalado (as tarefas do programa)",
              f"if (Test-Path -LiteralPath '{caminho_do_antes()}')"
              f" {{ Anotar 'FICA | os testes a distancia ja foram ligados: o desfazer inteiro ja esta pronto' }}"
              f" else {{ {_comando_preparar_o_desfazer(testes_ligados=False)} }}"),
    ]


# ---------------------------------------------------------------------------
# A REGRA: os tres planos de comandos (um lugar so)
# ---------------------------------------------------------------------------

def plano_de_ligar() -> list[Passo]:
    """Os passos para ligar os testes a distancia, na ordem (estudo 2.2).

    Tudo com o que o proprio Windows traz, igual no Home e no Pro. A senha
    entra como `$SenhaDosTestes` (o executor a fornece por dentro).
    Ligar de novo (depois de desligar, ou para trocar a senha) da certo e nao
    repete nada (B3, 17/11/2026).
    """
    return [
        # D-731: antes de tudo, anotar o que o computador ja tinha (so na 1a vez).
        Passo("Anotar o que o computador ja tinha antes (D-731)", _comando_anotar_o_antes()),
        Passo("Instalar o Servidor OpenSSH do Windows",
              f"Add-WindowsCapability -Online -Name {CAPACIDADE_OPENSSH}"),
        Passo("Deixar o Servidor OpenSSH ligando sozinho com o Windows (D-711)",
              "Set-Service -Name sshd -StartupType Automatic; Start-Service -Name sshd"),
        # Firewall so para o Tailscale (D-705): fecha a regra larga que a
        # instalacao cria (libera a porta a todos) e abre uma nossa so para a
        # faixa do Tailscale, presa a placa do Tailscale. O Wi-Fi da casa nao entra.
        Passo("Fechar a porta para todo mundo (regra larga do OpenSSH)",
              f"Disable-NetFirewallRule -Name {REGRA_LARGA_DO_OPENSSH}"),
        # B3: a regra nossa e apagada antes (ligar de novo nao para no "ja existe").
        Passo("Abrir a porta so para a rede do Tailscale (D-705)",
              f"Remove-NetFirewallRule -Name {NOME_DA_REGRA} -ErrorAction SilentlyContinue;"
              f" New-NetFirewallRule -Name {NOME_DA_REGRA}"
              f" -DisplayName 'Editor de Impressao - testes a distancia'"
              f" -Direction Inbound -Protocol TCP -LocalPort {PORTA_SSH}"
              f" -RemoteAddress {FAIXAS_DO_TAILSCALE}"
              f" -InterfaceAlias {PLACA_DO_TAILSCALE} -Action Allow"),
        # A conta so dos testes (D-717): sem administrador (New-LocalUser nao
        # poe em nenhum grupo; acrescentamos SO ao grupo Usuarios pelo SID, que
        # e igual em qualquer idioma do Windows). A senha e $SenhaDosTestes.
        # B3: se a conta nossa ja existe (desligar so a desativa), ela e
        # reativada com a senha dada; uma conta com o nosso nome que nao e nossa
        # faz o ligar parar sem mexer nela.
        Passo("Criar a conta so dos testes, sem poder de administrador (D-717)",
              f"$u = Get-LocalUser -Name {NOME_DA_CONTA} -ErrorAction SilentlyContinue;"
              f" if ($u) {{ if ($u.Description -ne '{DESCRICAO_DA_CONTA}')"
              f" {{ throw 'Ja existe uma conta {NOME_DA_CONTA} que nao foi criada pelo programa: nada mudou nela.' }};"
              f" Set-LocalUser -Name {NOME_DA_CONTA} -Password {VARIAVEL_DA_SENHA}"
              f" -AccountNeverExpires -PasswordNeverExpires $true;"
              f" Enable-LocalUser -Name {NOME_DA_CONTA} }}"
              f" else {{ New-LocalUser -Name {NOME_DA_CONTA} -Password {VARIAVEL_DA_SENHA}"
              f" -FullName 'Testes do Editor de Impressao'"
              f" -Description '{DESCRICAO_DA_CONTA}'"
              f" -AccountNeverExpires -PasswordNeverExpires;"
              f" Add-LocalGroupMember -SID {SID_USUARIOS} -Member {NOME_DA_CONTA} }}",
              precisa_senha=True),
        # Esconder da tela de entrada (D-717): valor 0 (DWORD) no UserList.
        # B5 (17/11/2026): a chave so e criada se nao existe; o New-Item -Force
        # numa chave que ja existe pode recria-la e apagar as outras contas
        # escondidas do dono. O New-ItemProperty -Force so mexe no nosso valor.
        Passo("Esconder a conta de testes da tela de entrada (D-717)",
              f"if (-not (Test-Path -Path '{CHAVE_USERLIST}'))"
              f" {{ New-Item -Path '{CHAVE_USERLIST}' -Force | Out-Null }};"
              f" New-ItemProperty -Path '{CHAVE_USERLIST}' -Name {NOME_DA_CONTA}"
              f" -Value 0 -PropertyType DWord -Force | Out-Null"),
        # So a conta de testes entra pelo comando de longe (nem a conta do
        # Kaique); entra com senha, nao chave (D-711). As linhas vao entre as
        # marcas e ANTES do primeiro "Match" (B2), sem repetir (B3).
        Passo("Deixar entrar pelo comando de longe so a conta de testes (D-711)",
              f"{_comando_por_o_bloco(SSHD_CONFIG)}; Restart-Service -Name sshd"),
        # D-731/D-733: a tarefa "desfazer", que o gancho de desinstalar manda
        # rodar. Depois da conta (a licenca nega a conta de testes pelo SID).
        Passo("Preparar o desfazer para quando o programa for desinstalado (D-731)",
              _comando_preparar_o_desfazer()),
    ]


def plano_de_desligar() -> list[Passo]:
    """Os passos para desligar: para o servico e fecha a entrada (estudo 2.4).

    A conta e os projetos de teste ficam guardados (a conta so e desativada).
    B4 (17/11/2026): se o OpenSSH ja era do dono antes do 1o ligar (caderninho),
    ele nao e desativado: o servico e a regra larga voltam como estavam e as
    nossas linhas saem do sshd_config. Sem caderninho, para como sempre parou.
    """
    return [
        Passo("Parar o Servidor OpenSSH e tira-lo do arranque do Windows (ou devolver o do dono como estava)",
              f"{_ler_o_antes()}; if ($antes -and $antes.openssh_ja_existia) {{"
              f" {_comando_tirar_o_bloco(SSHD_CONFIG)};"
              f" if ($antes.sshd_inicio) {{ Set-Service -Name sshd -StartupType $antes.sshd_inicio }};"
              f" if ($antes.sshd_rodando) {{ Restart-Service -Name sshd }}"
              f" else {{ Stop-Service -Name sshd -ErrorAction SilentlyContinue }};"
              f" if ($antes.regra_larga_ligada) {{ Enable-NetFirewallRule -Name {REGRA_LARGA_DO_OPENSSH} }};"
              f" Anotar 'FICA | o Servidor OpenSSH ja era do dono: voltou como estava' }}"
              f" else {{ Stop-Service -Name sshd -ErrorAction SilentlyContinue;"
              f" Set-Service -Name sshd -StartupType Disabled }}"),
        Passo("Fechar a porta do Tailscale (apagar a regra do firewall)",
              f"Remove-NetFirewallRule -Name {NOME_DA_REGRA} -ErrorAction SilentlyContinue"),
        Passo("Desativar a conta de testes (os projetos de teste ficam guardados)",
              f"Disable-LocalUser -Name {NOME_DA_CONTA} -ErrorAction SilentlyContinue"),
    ]


def plano_de_desfazer(testes_ligados: bool = True) -> list[Passo]:
    """Os passos para desfazer TUDO o que o programa pos no Windows, e SO isso (D-722, D-731).

    Dois caminhos, o mesmo plano (CLAUDE.md 11.12):
      - desinstalar o programa: o gancho manda rodar a tarefa "desfazer"
        (`mandar_desfazer`), que roda este plano gravado pelo ligar ou pela
        primeira abertura (`_comando_preparar_o_desfazer`);
      - a etapa 5, no PC do Samuel: a mesma tarefa, ou este plano pelo executor.
    `testes_ligados=False` (a primeira abertura, antes de qualquer ligar): so
    os passos das nossas tarefas. Sem os testes ligados, os passos dos testes
    mexeriam no que nao e nosso (o desligar para um OpenSSH do dono quando nao
    ha caderninho). Os dois terminam igual (`_passos_das_nossas_tarefas`):
    apagar a tarefa da atualizacao e, se tudo deu certo, a propria tarefa.
    Cada passo que poderia atingir algo do dono confere antes o caderninho e a
    descricao da conta. Na tarefa, um passo que falha nao para os outros, e a
    tarefa e o caderninho so se apagam se tudo deu certo. Os projetos do Kaique
    nunca sao citados; o perfil da conta de testes e achado pelo SID dela.
    """
    passos = _passos_dos_testes_a_distancia() if testes_ligados else []
    return passos + _passos_das_nossas_tarefas()


def _passos_das_nossas_tarefas() -> list[Passo]:
    """O fim de todo desfazer: as tarefas do Windows que o programa criou, e so elas.

    1. a tarefa da atualizacao (atualizacao.NOME_DA_TAREFA, o ajudante da
       D-733): o gancho de desinstalar tenta apaga-la, mas roda sem
       administrador e nao consegue (pergunta (a) do relatorio da D-731);
       aqui roda como o sistema. Sempre, mesmo se um passo antes falhou;
    2. o caderninho, o script e a propria tarefa do desfazer, so se tudo deu
       certo (para dar para rodar de novo).
    O nome da tarefa da atualizacao vem do atualizacao.py (um lugar so); e
    importado aqui dentro porque o atualizacao.py importa este arquivo.
    """
    from atualizacao import NOME_DA_TAREFA

    pasta, nome = NOME_DA_TAREFA.rsplit("\\", 1)
    return [
        Passo("Apagar a tarefa da atualizacao do programa (Procurar versao nova)",
              f"Unregister-ScheduledTask -TaskName '{nome}' -TaskPath '\\{pasta}\\'"
              f" -Confirm:$false -ErrorAction SilentlyContinue"),
        Passo("Apagar o caderninho, o script e a tarefa do desfazer (so se tudo deu certo)",
              f"Remove-Item -LiteralPath '{caminho_do_antes()}' -Force -ErrorAction SilentlyContinue;"
              f" Remove-Item -LiteralPath '{caminho_do_script_do_desfazer()}' -Force -ErrorAction SilentlyContinue;"
              f" Anotar 'OK   | a tarefa do desfazer sai agora';"
              f" Unregister-ScheduledTask -TaskName '{NOME_DA_TAREFA_DO_DESFAZER}'"
              f" -TaskPath '\\{PASTA_DAS_TAREFAS}\\' -Confirm:$false -ErrorAction SilentlyContinue;"
              f" {_comando_apagar_a_pasta_das_tarefas_se_vazia()}",
              so_se_tudo_certo=True),
    ]


def _comando_apagar_a_pasta_das_tarefas_se_vazia() -> str:
    """D-731 ("o notebook fica como era antes de instalar"), 17/11/2026: a pasta
    PASTA_DAS_TAREFAS do Agendador do Windows sai no fim do desfazer, SO se
    ficou vazia (nenhuma tarefa, nem escondida, e nenhuma subpasta).

    O Agendador so apaga pasta pelo servico dele (Schedule.Service); os
    cmdlets ScheduledTasks nao tem esse comando. Se alguem (o dono do
    computador, outro programa) pos algo na pasta, ela fica e o registro diz.
    Roda como a ultima coisa do ultimo passo, depois de a tarefa do desfazer
    se apagar (antes disso a pasta nunca esta vazia).
    """
    return (f"$agenda = New-Object -ComObject Schedule.Service; $agenda.Connect(); $pasta = $null;"
            f" try {{ $pasta = $agenda.GetFolder('\\{PASTA_DAS_TAREFAS}') }} catch {{ }};"
            f" if ($pasta -and $pasta.GetTasks(1).Count -eq 0 -and $pasta.GetFolders(0).Count -eq 0)"
            f" {{ $agenda.GetFolder('\\').DeleteFolder('{PASTA_DAS_TAREFAS}', 0);"
            f" Anotar 'OK   | a pasta {PASTA_DAS_TAREFAS} saiu do Agendador (estava vazia)' }}"
            f" elseif ($pasta) {{ Anotar 'FICA | a pasta {PASTA_DAS_TAREFAS} do Agendador nao esta vazia' }}")


def _passos_dos_testes_a_distancia() -> list[Passo]:
    """Os passos que desfazem o que o `ligar` pos (o plano de desfazer de 17/11, sem o fim das tarefas)."""
    # Primeiro o desligar (para o sshd: nenhum teste novo entra), depois fechar
    # o que a conta de testes ainda estiver rodando, e so entao apagar.
    passos = list(plano_de_desligar())
    passos += [
        Passo("Fechar o que a conta de testes estiver rodando (um teste de longe no meio)",
              _so_se_a_conta_foi_nossa(
                  f"Get-Process -IncludeUserName | Where-Object {{ $_.UserName -like '*\\{NOME_DA_CONTA}' }}"
                  f" | Stop-Process -Force -ErrorAction SilentlyContinue")),
        # O perfil antes da conta: o SID e lido da conta, que ainda existe.
        Passo("Apagar o perfil da conta de testes (achado pelo SID da conta)",
              _so_se_a_conta_foi_nossa(
                  f"$sid = (Get-LocalUser -Name {NOME_DA_CONTA}).SID.Value;"
                  f" Get-CimInstance -ClassName Win32_UserProfile | Where-Object {{ $_.SID -eq $sid }}"
                  f" | Remove-CimInstance")),
        Passo("Tirar a conta de testes do registro (UserList)",
              _so_se_a_conta_foi_nossa(
                  f"Remove-ItemProperty -Path '{CHAVE_USERLIST}' -Name {NOME_DA_CONTA}"
                  f" -ErrorAction SilentlyContinue;"
                  f" if ($antes -and -not $antes.userlist_existia -and (Test-Path -Path '{CHAVE_USERLIST}')"
                  f" -and -not (Get-Item -Path '{CHAVE_USERLIST}').Property)"
                  f" {{ Remove-Item -Path '{CHAVE_USERLIST}' }}")),
        Passo("Apagar a conta de testes",
              _so_se_a_conta_foi_nossa(f"Remove-LocalUser -Name {NOME_DA_CONTA}")),
        Passo("Devolver o sshd_config (tirar so o que esta entre as marcas)",
              _comando_tirar_o_bloco(SSHD_CONFIG)),
        Passo("Apagar a regra larga do OpenSSH, se veio com o OpenSSH que o programa pos",
              _so_se_o_openssh_foi_nosso(
                  f"if (-not $antes.regra_larga_existia)"
                  f" {{ Remove-NetFirewallRule -Name {REGRA_LARGA_DO_OPENSSH} -ErrorAction SilentlyContinue }}")),
        Passo("Tirar o Servidor OpenSSH do Windows (so se foi o programa que instalou)",
              _so_se_o_openssh_foi_nosso(f"Remove-WindowsCapability -Online -Name {CAPACIDADE_OPENSSH}")),
        Passo("Apagar da pasta ssh so o que nasceu depois (e a pasta, se ela nao existia)",
              _so_se_o_openssh_foi_nosso(
                  f"$p = '{PASTA_SSH}'; if (Test-Path -LiteralPath $p) {{"
                  f" if (-not $antes.pasta_ssh_existia) {{ Remove-Item -LiteralPath $p -Recurse -Force }}"
                  f" else {{ $ja = @($antes.pasta_ssh_itens);"
                  f" Get-ChildItem -LiteralPath $p -Recurse -Force -Name | Where-Object {{ $ja -notcontains $_ }}"
                  f" | Sort-Object -Property Length -Descending"
                  f" | ForEach-Object {{ Remove-Item -LiteralPath (Join-Path $p $_) -Recurse -Force"
                  f" -ErrorAction SilentlyContinue }} }} }}")),
    ]
    return passos


def montar_script(passos: list[Passo], registro: str, blob: str | None = None,
                  continuar_depois_de_erro: bool = False) -> str:
    """O texto do script PowerShell que roda os passos (o unico montador).

    - Cada passo vai num try; o registro ganha "OK", "ERRO" ou "PULADO" com o
      nome do passo (a lista do que foi feito, D-722).
    - `blob`: o arquivo da senha cifrada, SO quando um passo precisa da senha
      (achado de 17/11/2026: antes o script lia o arquivo sempre e, sem ele,
      parava na primeira linha - o desligar e o desfazer nunca rodariam).
    - `continuar_depois_de_erro`: so o desfazer usa. Um passo que falha nao
      para os outros; o passo `so_se_tudo_certo` e pulado se algum falhou; o
      script sai com codigo 1 se algum falhou. Sem isto (o ligar), para no
      primeiro erro, como sempre.
    """
    linhas = ["$ErrorActionPreference = 'Stop'"]
    if blob is not None:
        linhas += [
            f"$blob = Get-Content -Raw '{blob}'",
            # $SenhaDosTestes (o nome que os passos usam) vem da DPAPI, so na memoria.
            f"{VARIAVEL_DA_SENHA} = ConvertTo-SecureString $blob",
            f"Remove-Item -Path '{blob}' -Force -ErrorAction SilentlyContinue",
        ]
    linhas += [
        f"function Anotar($t) {{ Add-Content -LiteralPath '{registro}' -Value $t }}",
        "$HouveErro = $false",
        "Anotar ('--- ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))",
    ]
    for passo in passos:
        nome = passo.nome.replace("'", "''")
        tentar = ["try {",
                  f"  {passo.comando}",
                  f"  Anotar 'OK   | {nome}'",
                  "} catch {",
                  f"  Anotar ('ERRO | {nome} | ' + $_.Exception.Message)",
                  "  $HouveErro = $true" if continuar_depois_de_erro else "  throw",
                  "}"]
        if passo.so_se_tudo_certo:
            linhas += ["if ($HouveErro) {", f"  Anotar 'PULADO | {nome} (um passo antes falhou)'", "} else {",
                       *tentar, "}"]
        else:
            linhas += tentar
    if continuar_depois_de_erro:
        linhas.append("if ($HouveErro) { exit 1 }")
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# A PECA QUE FALA COM O WINDOWS (isolada; os testes a trocam)
# ---------------------------------------------------------------------------

class Executor:
    """A peca que aplica os passos no Windows.

    `aplicar` recebe os passos e a senha, aplica TODOS numa pergunta de
    administrador so, e devolve um Resultado. Os testes implementam uma de
    mentira que so anota os comandos.
    """

    def aplicar(self, passos: list[Passo], senha: str) -> Resultado:  # pragma: no cover
        raise NotImplementedError

    def rodar_a_tarefa(self, nome: str) -> Resultado:  # pragma: no cover
        """Manda rodar uma tarefa do Windows ja criada e volta logo, SEM esperar
        ela terminar e SEM pedir licenca de administrador (D-731: o gancho de
        desinstalar roda sem administrador e tem 30 s)."""
        raise NotImplementedError

    def aplicar_ja_como_administrador(self, passos: list[Passo]) -> Resultado:  # pragma: no cover
        """Aplica os passos SEM pergunta nenhuma, porque quem chama ja roda como
        administrador (a primeira abertura: --preparar-o-computador, dentro da
        pergunta do Windows da D-733). Espera terminar. Sem senha."""
        raise NotImplementedError


class ExecutorWindows(Executor):
    """A de verdade: uma pergunta de administrador so para todos os passos.

    ATENCAO: so roda na producao. Sob o pytest (PYTEST_CURRENT_TEST no
    ambiente) ela se RECUSA a rodar, para nenhum teste tocar o Windows por
    engano - alem de os testes ja trocarem o executor por um de mentira.

    A etapa 5 (no PC do Samuel, D-722) e quem prova isto de verdade; a ligacao
    com o runas e a passagem da senha por dentro (DPAPI) estao marcadas como
    ressalva no relatorio.
    """

    def aplicar(self, passos: list[Passo], senha: str) -> Resultado:
        if "PYTEST_CURRENT_TEST" in os.environ:
            raise RuntimeError(
                "ExecutorWindows nao roda sob o pytest: troque por um de mentira.")
        if sys.platform != "win32":
            return Resultado(False, mensagem="Os testes a distancia so funcionam no Windows.")
        from core._testes_a_distancia_windows import aplicar_no_windows

        return aplicar_no_windows(passos, senha)

    def rodar_a_tarefa(self, nome: str) -> Resultado:
        if "PYTEST_CURRENT_TEST" in os.environ:
            raise RuntimeError(
                "ExecutorWindows nao roda sob o pytest: troque por um de mentira.")
        if sys.platform != "win32":
            return Resultado(False, mensagem="Os testes a distancia so funcionam no Windows.")
        from core._testes_a_distancia_windows import rodar_a_tarefa_no_windows

        return rodar_a_tarefa_no_windows(nome, TEMPO_MAXIMO_NO_GANCHO)

    def aplicar_ja_como_administrador(self, passos: list[Passo]) -> Resultado:
        if "PYTEST_CURRENT_TEST" in os.environ:
            raise RuntimeError(
                "ExecutorWindows nao roda sob o pytest: troque por um de mentira.")
        if sys.platform != "win32":
            return Resultado(False, mensagem="Os testes a distancia so funcionam no Windows.")
        from core._testes_a_distancia_windows import aplicar_ja_como_administrador_no_windows

        return aplicar_ja_como_administrador_no_windows(passos)


# O executor de hoje. Troca-se com `definir_executor` (os testes poem um de
# mentira; a producao usa o ExecutorWindows).
_executor: Executor = ExecutorWindows()


def definir_executor(executor: Executor) -> None:
    """Troca a peca que fala com o Windows (os testes poem a de mentira)."""
    global _executor
    _executor = executor


def executor_atual() -> Executor:
    """A peca que fala com o Windows agora."""
    return _executor


# ---------------------------------------------------------------------------
# O ESTADO (nas Configuracoes)
# ---------------------------------------------------------------------------

def esta_ligado() -> bool:
    """A opcao esta marcada? De fabrica True (D-712)."""
    return bool(configuracoes.ler(CHAVE_LIGADO))


def esta_pronto() -> bool:
    """O lado do Windows ja foi montado (a conta existe, o OpenSSH liga)?"""
    return bool(configuracoes.ler(CHAVE_PRONTO))


def senha_ja_perguntada() -> bool:
    """A janela da senha da primeira vez ja apareceu?"""
    return bool(configuracoes.ler(CHAVE_SENHA_PERGUNTADA))


def marcar_senha_perguntada() -> None:
    """Lembra que a janela da primeira vez ja apareceu (D-721)."""
    configuracoes.escrever(CHAVE_SENHA_PERGUNTADA, True)


# ---------------------------------------------------------------------------
# A PORTA UNICA que a tela usa (ligar / desligar)
# ---------------------------------------------------------------------------

def ligar(senha: str) -> Resultado:
    """Liga os testes a distancia com a senha dada (D-705, D-711, D-712, D-717).

    Monta o plano (um lugar so), manda o executor aplicar numa pergunta de
    administrador so, e guarda o estado. Sem senha, nao faz nada (D-721).
    Todos os caminhos da tela chamam esta funcao.
    """
    if not senha:
        # Sem senha os testes ficam desligados (D-721): nada e instalado.
        configuracoes.escrever(CHAVE_PRONTO, False)
        return Resultado(False, mensagem="Sem a senha, os testes à distância ficam desligados. "
                                         "Você pode pôr a senha depois nas Configurações.")
    passos = plano_de_ligar()
    resultado = executor_atual().aplicar(passos, senha)
    if resultado.ok:
        configuracoes.escrever(CHAVE_LIGADO, True)
        configuracoes.escrever(CHAVE_PRONTO, True)
    elif resultado.cancelado:
        # Disse "Nao" a pergunta do Windows: nada foi instalado, a opcao fica
        # DESLIGADA, com um aviso em portugues (pedido do Samuel; estudo 2.3).
        configuracoes.escrever(CHAVE_LIGADO, False)
        configuracoes.escrever(CHAVE_PRONTO, False)
        if not resultado.mensagem:
            resultado.mensagem = ("Nada foi instalado. Os testes à distância continuam desligados. "
                                  "Você pode ligar depois nas Configurações.")
    return resultado


def desligar() -> Resultado:
    """Desliga os testes a distancia: para o servico e fecha a entrada (D-705).

    A conta e os projetos de teste ficam guardados (estudo 2.4).
    """
    resultado = executor_atual().aplicar(plano_de_desligar(), senha="")
    configuracoes.escrever(CHAVE_LIGADO, False)
    return resultado


def mandar_desfazer() -> Resultado:
    """Manda rodar a tarefa "desfazer" (D-731/D-733) e volta logo. Nunca levanta.

    Quem chama: o gancho de desinstalar (atualizacao.ao_desinstalar), na conta
    do Kaique e sem administrador; e a etapa 5 (D-722), para desfazer no PC do
    Samuel com o mesmo plano. A tarefa (criada pelo ligar) roda como o sistema
    o `plano_de_desfazer` e anota cada passo em `caminho_do_registro_do_desfazer`.
    Se os testes nunca foram ligados, a tarefa nao existe: volta "nao deu certo"
    com a mensagem do Windows, e nada mais acontece.
    """
    try:
        return executor_atual().rodar_a_tarefa(nome_da_tarefa_do_desfazer())
    except Exception as erro:  # noqa: BLE001 - o gancho de desinstalar nunca pode quebrar
        return Resultado(False, mensagem=f"{type(erro).__name__}: {erro}")


def preparar_o_desfazer() -> Resultado:
    """Cria a tarefa "desfazer" na primeira abertura, mesmo sem os testes ligados (D-731, pergunta (a)).

    Quem chamava: o --preparar-o-computador do atualizador antigo, que rodava
    como administrador dentro da pergunta do Windows da primeira abertura
    (D-733/D-735). Saiu com o atualizador novo (23/11/2026): hoje ninguem do
    programa chama; fica para a entrega dos testes a distancia decidir. Os passos sao
    `plano_de_preparar_o_desfazer` (um lugar so). Nunca levanta.
    """
    try:
        return executor_atual().aplicar_ja_como_administrador(plano_de_preparar_o_desfazer())
    except Exception as erro:  # noqa: BLE001 - o preparo do computador continua
        return Resultado(False, mensagem=f"{type(erro).__name__}: {erro}")
