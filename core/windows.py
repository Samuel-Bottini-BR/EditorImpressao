"""A peça única do Windows (plano da parte do Windows, versão 3: peças 1 e 2).

O QUE É
    O único lugar do programa que conversa com o Windows: pedir a licença de administrador, lançar um processo solto,
    rodar e esperar uma ferramenta do Windows ou um script do PowerShell, criar/apagar/rodar/ler tarefas do
    Agendador, a pasta de troca, a pasta segura, ler licenças de pasta e marcas, e ler a assinatura digital de um
    arquivo (`ler_assinatura_digital`, desde o passo 2, para o publicar), e abrir um programa num grupo do Windows que
    fecha junto tudo o que ele abrir (`abrir_em_grupo`, passo 2, para a vigia do espaço do publicar), com o laço único
    de rodar, olhar a vigia e fechar (`rodar_em_grupo`, passo 2, volta 4: o vpk e o gh), e pedir ao Windows que grave
    um arquivo no disco (`gravar_no_disco`, passo 2, volta 4). O porteiro (`regras_dos_agentes`,
    conferência K01) só deixa essa conversa acontecer aqui. Quem usa hoje: o `main.py` (a entrada do trabalho de
    administrador), a janela de prova, os testes e, desde o passo 2, o `empacotar.py` (o vpk pelo laço único, a
    assinatura digital do Visual C++ e a gravação no disco) e o `publicar_versao_kaique.py` (o gh pelo laço único). O
    programa do Kaique ainda não a usa: ele muda nos passos 3 a 5.

AS TRÊS RESPOSTAS
    Toda função que pede algo ao Windows devolve uma `Resposta` com um de três desfechos: `DEU_CERTO`, `DISSE_NAO` (a
    pessoa clicou "Não" na pergunta do Windows) ou `FALHOU` (com o motivo em português em `motivo` e o técnico em
    `detalhe`, que vai para o registro). Nenhuma dessas funções levanta exceção: o erro vira `FALHOU`.
    "Deu certo" só sai depois de conferir o resultado de verdade (a pasta existe e tem as licenças certas, a tarefa
    existe e aponta para o lugar certo, o arquivo gravado foi lido de volta), nunca só pelo código de saída.

PEDIR A LICENÇA (decisão do Samuel de 18/11: a pergunta mostra o programa do Editor, não o PowerShell)
    `pedir_licenca(passos)` grava um aviso de trabalho (`trabalho.json`) numa pasta de troca e abre **o próprio
    programa** com a licença de administrador e o argumento `ARG_TRABALHO_DE_ADMINISTRADOR`. O programa aberto assim
    não mostra janela nem brasão (`main.py` atende esse argumento antes de tudo): `atender_trabalho_de_administrador`
    confere a pasta de troca, faz só os passos do aviso (de uma lista fechada de tipos), escreve o relatório
    (`relatorio.json`) e sai. Quem pediu lê o relatório e decide pelo relatório, não pelo código de saída.
    Desde o atualizador novo (23/11/2026) o pedido tem duas metades, da mesma conta: `comecar_pedido_de_licenca` faz a
    pergunta e volta logo depois da resposta (a pergunta vem antes da janela do programa, D-806, D-834), e
    `PedidoDeLicenca.esperar()` espera o trabalho e lê o relatório (por trás, com a janela aberta). `pedir_licenca` é
    as duas juntas. Os passos do preparo do computador (o Visual C++, tirar o Inno antigo e dar a Usuários a licença de
    Modificar na pasta do programa, `dar_licenca_aos_usuarios`, a ÚNICA mudança de licença de pasta do programa, D-837)
    não aceitam dado nenhum no aviso: o lado com licença calcula tudo a partir do próprio programa (`raiz_da_instalacao`).

A PASTA DE TROCA
    Nasce em `<pasta de dados do programa>\\troca\\troca-<data>-<sorteio>`, com `os.mkdir` comum, herdando as licenças
    da pasta da conta. NUNCA com `tempfile.mkdtemp`: no Python 3.13+ ele cria a pasta com licença só para o dono, e o
    arquivo que o programa com licença cria lá dentro tem outro dono (os Administradores), que a conta comum não lê
    (defeito 13 da etapa 5). Outra conta comum não grava na pasta da conta, então não consegue trocar o aviso; o lado
    com licença confere isso antes de ler (`problemas_da_pasta_de_troca`).

A PASTA SEGURA (peça 2)
    Uma pasta própria em Arquivos de Programas, ao lado da pasta do programa (nunca dentro: o Velopack troca e apaga a
    dele), com as licenças de fábrica que o Windows dá ali: o sistema e os administradores mudam, as contas comuns só
    leem. Nenhum comando de licença à mão: a pasta é criada pelo programa com licença e herda as licenças de
    Arquivos de Programas; `conferir_pasta_segura` lê e confere (é pasta de verdade, não um atalho; quem pode gravar).

O QUE É SEGURO E O QUE É ARRISCADO MUDAR
    Seguro: as frases de `motivo`; acrescentar um tipo de passo NOVO (com a validação dele em `problemas_do_passo` e
    um teste). Arriscado: `_ler_erro`/`use_last_error` (sem eles o "Não" vira "deu certo", defeito 2 da etapa 5);
    `_criar_pasta_comum` (voltar ao `mkdtemp` reabre o defeito 13); a marca de UTF-8 dos scripts (`_gravar_script`,
    sem ela o PowerShell 5.1 lê o script como ANSI e o texto com acento chega trocado ou o script nem roda); a tabela
    de letras `oem` na leitura das ferramentas do Windows (o "ÒXITO" da etapa 5); as listas fechadas
    (`TIPOS_DE_PASSO`, `PASTAS_SEGURAS_ACEITAS`, `_NOME_DE_TAREFA`): abri-las deixa o aviso mandar o programa com
    licença fazer outra coisa; as regras de quem pode gravar e ler (`problemas_da_pasta_de_troca`,
    `problemas_da_pasta_segura`). NUNCA usar a bandeira de lançar processo sem console (o porteiro barra, K02): o
    PowerShell lançado assim sai sem rodar (defeito 1 da etapa 5).

A PEÇA É FECHADA (escolha técnica da gerente, 19/11, achado 12 de quem tentou quebrar)
    Por quê: o porteiro só deixa a conversa com o Windows acontecer aqui. Se a peça entregasse a biblioteca crua do
    Windows ou um "rode qualquer ferramenta" a qualquer arquivo, cada chamador dos passos 3 a 5 voltaria a falar com o
    Windows do seu jeito, só que por dentro da peça, e o porteiro não veria (foi a causa dos defeitos da etapa 5).
    Então:
    - tudo o que tem "_" no nome é de dentro da peça e não é usado fora de `core/windows.py` (as bibliotecas cruas
      `_win()`, os caminhos das ferramentas, o comando do PowerShell, o rodar sem filtro `_rodar`);
    - o rodar genérico (`rodar_e_esperar`) e o lançar solto genérico (`lancar_solto`) RECUSAM os programas que já têm
      função própria na peça: TODO programa da pasta do Windows (é lá que ficam as ferramentas de tarefas, de licença
      de pasta, o PowerShell, o pedido de licença, o cmd, o registro, os serviços, o firewall, o instalador...) e os
      de fora dela listados em `PROGRAMAS_COM_FUNCAO_PROPRIA` (o PowerShell 7, o atualizador do Velopack). A regra é
      pela pasta, e não por uma lista de nomes, porque escrever aqui o nome das ferramentas de licença de pasta faria
      o porteiro (K03, que vale também nesta peça) acusar a própria recusa; e a pasta pega também as que ninguém
      lembrou de pôr na lista. Quem precisa de um deles chama a função da peça (`ler_tarefa`, `rodar_tarefa`,
      `rodar_powershell`, `pedir_licenca`...), ou a peça ganha uma função nova para isso, com teste. O caminho é
      normalizado num lugar só antes de comparar (`_caminho_do_programa`): o prefixo de caminho longo e o de
      dispositivo (duas barras com interrogação ou com ponto) saem, o caminho de rede (duas barras e o nome de um
      computador, que pode apontar para a pasta do Windows deste por outro nome) é recusado, e o nome é completado como
      o Windows o completa, com os pontos e espaços do fim tirados (passo 2, volta 4: `pwsh.exe.` e `whoami.exe.`
      passavam); a regra inteira, com uma frase para cada motivo, é `_por_que_recusa`.
    - Programa de fora do Windows (ex.: o do Tailscale, no passo 4) passa pelo rodar genérico neste passo. CADA passo
      que usar um programa de fora decide, no pedido dele, se o programa ganha função própria na peça (e entra em
      `PROGRAMAS_COM_FUNCAO_PROPRIA`).

Fontes lidas antes de escrever (CLAUDE.md §11.12, ponto 6): estão no ONDE-PAREI do passo 1
(`relatorios/passo1-peca-unica-windows/ONDE-PAREI.md`, seção "O que li da peça de fora e onde").
"""

from __future__ import annotations

import ctypes
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
import time
import uuid
from ctypes import wintypes
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Callable

# ---------------------------------------------------------------------------------------------------------------------
# Constantes (lugar único)
# ---------------------------------------------------------------------------------------------------------------------

ARG_TRABALHO_DE_ADMINISTRADOR = "--trabalho-de-administrador"   # o main.py atende antes de qualquer janela

DEU_CERTO = "deu certo"
DISSE_NAO = "disse Não"
FALHOU = "falhou"

NOME_DO_AVISO = "trabalho.json"
NOME_DO_RELATORIO = "relatorio.json"
NOME_DO_SEGREDO = "segredo.bin"
NOME_DA_PASTA_MAE_DA_TROCA = "troca"
PREFIXO_DA_TROCA = "troca-"
FORMATO_DO_AVISO = 1
TAMANHO_MAXIMO_DO_AVISO = 5_000_000          # bytes: um aviso maior que isso não é nosso
DIAS_ATE_LIMPAR_TROCA_VELHA = 1

# A pasta segura (peça 2): nomes técnicos, sem acento, que não lembram a pasta dos projetos. Lista FECHADA: o
# programa com licença só cria, grava ou apaga pasta segura com um destes nomes.
NOME_DA_PASTA_SEGURA = "EditorImpressaoAjudante"
NOME_DA_PASTA_SEGURA_DE_PROVA = "EditorImpressaoProvaPastaSegura"
PASTAS_SEGURAS_ACEITAS = (NOME_DA_PASTA_SEGURA, NOME_DA_PASTA_SEGURA_DE_PROVA)

# As tarefas do programa moram na pasta "EditorImpressao" do Agendador (a mesma do ajudante de hoje).
PASTA_DAS_TAREFAS = "EditorImpressao"
_NOME_DE_TAREFA = re.compile(r"^EditorImpressao\\[A-Za-z0-9 ._-]{1,100}$")
_NOME_DE_ARQUIVO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")
_SID = re.compile(r"^S-1-\d+(-\d+)+$")

# Quem é quem no Windows (os números fixos das contas e grupos de fábrica).
SID_SISTEMA = "S-1-5-18"
SID_ADMINISTRADORES = "S-1-5-32-544"
SID_USUARIOS = "S-1-5-32-545"
SID_AUTENTICADOS = "S-1-5-11"
SID_INSTALADOR_CONFIAVEL = "S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464"
SID_PROPRIETARIO_CRIADOR = "S-1-3-0"
SID_DIREITOS_DO_DONO = "S-1-3-4"

# Os tipos de passo que o programa com licença sabe fazer. Lista FECHADA (ver o topo).
TIPOS_DE_PASSO = ("criar_pasta_segura", "apagar_pasta_segura", "gravar_na_pasta_segura", "criar_tarefa",
                  "apagar_tarefa", "apagar_pasta_de_tarefas", "script",
                  # O preparo do computador do atualizador novo (23/11/2026): o lado com licença calcula tudo sozinho a
                  # partir do próprio programa; o aviso não leva dado nenhum (`_PASSOS_SEM_DADOS`).
                  "instalar_visual_c", "tirar_instalacao_do_inno", "dar_licenca_aos_usuarios")
_PASSOS_SEM_DADOS = ("instalar_visual_c", "tirar_instalacao_do_inno", "dar_licenca_aos_usuarios")

# Códigos de saída do programa com licença (o relatório decide; o código só explica quando não há relatório).
SAIDA_TUDO_CERTO = 0
SAIDA_UM_PASSO_FALHOU = 1
SAIDA_ARGUMENTOS_ERRADOS = 2
SAIDA_PASTA_RECUSADA = 3
SAIDA_SEM_LICENCA = 4
SAIDA_AVISO_RECUSADO = 5
SAIDA_ERRO_INESPERADO = 6
_MOTIVO_DA_SAIDA = {
    SAIDA_ARGUMENTOS_ERRADOS: "o programa com licença foi aberto sem o pedido certo",
    SAIDA_PASTA_RECUSADA: "o programa com licença recusou o pedido: a pasta do pedido não é só desta conta",
    SAIDA_SEM_LICENCA: "o programa abriu sem a licença de administrador",
    SAIDA_AVISO_RECUSADO: "o programa com licença recusou o pedido: o pedido está errado",
    SAIDA_ERRO_INESPERADO: "o programa com licença teve um problema inesperado",
}

# Os programas de FORA da pasta do Windows que também têm função própria na peça (os da pasta do Windows são todos
# recusados pela pasta; ver "A PEÇA É FECHADA" no topo). Pelo nome do arquivo, sem ".exe". Acrescentar é seguro;
# tirar abre a porta.
PROGRAMAS_COM_FUNCAO_PROPRIA = frozenset({"pwsh", "update"})

# Bandeiras de lançar processo (process-creation-flags, Microsoft Learn).
CREATE_NO_WINDOW = 0x08000000
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000

# Erros do Windows que a peça lê pelo número.
ERRO_ARQUIVO_NAO_ACHADO = 2
ERRO_CAMINHO_NAO_ACHADO = 3
ERRO_ACESSO_NEGADO = 5
ERRO_CANCELADO = 1223                      # a pessoa disse "Não" (ou fechou a pergunta)
ERRO_SEM_ASSOCIACAO = 1155
HRESULT_NAO_EXISTE = (0x80070002, 0x80070003)
HRESULT_ACESSO_NEGADO = 0x80070005

# Direitos de arquivo que deixam mudar alguma coisa (ESCRITA) e que deixam ler (LEITURA).
_ESCRITA = (0x2 | 0x4 | 0x10 | 0x40 | 0x100 | 0x10000 | 0x40000 | 0x80000 | 0x10000000 | 0x40000000)
_LEITURA = 0x1 | 0x80000000 | 0x10000000
_ACE_PERMITE, _ACE_NEGA = 0, 1
_ACE_SO_PARA_DENTRO = 0x08                 # INHERIT_ONLY_ACE: não vale para a própria pasta, só para o que nasce nela
_ACE_HERDADA = 0x10                        # INHERITED_ACE
_DACL_PROTEGIDA = 0x1000                   # SE_DACL_PROTECTED

# O que todo script da peça recebe na frente. `Confere-Comando 'o que era'` é a ajuda para conferir, logo depois de
# um programa de fora, se ele deu certo (o PowerShell não para sozinho quando um programa de fora falha: achado 10 de
# quem tentou quebrar). E o fim de todo script confere o último programa de fora (`_PE_DO_SCRIPT`).
_CABECA_DO_SCRIPT = (
    "$ErrorActionPreference = 'Stop'\n"
    "$__utf8 = New-Object System.Text.UTF8Encoding $false\n"
    "[Console]::InputEncoding = $__utf8\n"
    "[Console]::OutputEncoding = $__utf8\n"
    "$global:LASTEXITCODE = 0\n"
    "function Confere-Comando([string]$oque) { if ($LASTEXITCODE -ne 0) { "
    "throw ($oque + ' falhou (código ' + $LASTEXITCODE + ')') } }\n"
)
_PE_DO_SCRIPT = ("\nif ($LASTEXITCODE -ne 0) { [Console]::Error.WriteLine('um programa de fora falhou (código ' + "
                 "$LASTEXITCODE + ')'); exit $LASTEXITCODE }\n")


# ---------------------------------------------------------------------------------------------------------------------
# A resposta
# ---------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Resposta:
    """O que o Windows respondeu: `desfecho` (DEU_CERTO, DISSE_NAO ou FALHOU), a frase para a tela (`motivo`), o
    técnico para o registro (`detalhe`) e o que mais a função leu (`dados`)."""

    desfecho: str
    motivo: str = ""
    detalhe: str = ""
    dados: dict = field(default_factory=dict)

    @property
    def deu_certo(self) -> bool:
        """True só quando o desfecho é DEU_CERTO (nunca para DISSE_NAO nem FALHOU)."""
        return self.desfecho == DEU_CERTO


def _certo(motivo: str = "", **dados) -> Resposta:
    """Uma resposta "deu certo"."""
    return Resposta(DEU_CERTO, motivo, "", dados)


def _falhou(motivo: str, detalhe: str = "", **dados) -> Resposta:
    """Uma resposta "falhou", com a frase em português e o técnico."""
    return Resposta(FALHOU, motivo, detalhe, dados)


def _registrar(origem: str, detalhe: str) -> None:
    """Anota o técnico no erros.log do programa (nunca levanta)."""
    try:
        from registro import registrar_erro

        registrar_erro(f"windows: {origem}", detalhe)
    except Exception:  # noqa: BLE001 - o registro nunca derruba nada
        pass


# ---------------------------------------------------------------------------------------------------------------------
# As bibliotecas do Windows (carregadas uma vez, sempre guardando o último erro de cada chamada)
# ---------------------------------------------------------------------------------------------------------------------

class _GUID(ctypes.Structure):
    """O GUID do Windows (para as pastas conhecidas)."""

    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD),
                ("Data4", ctypes.c_ubyte * 8)]


class _SHELLEXECUTEINFOW(ctypes.Structure):
    """SHELLEXECUTEINFOW (shellapi.h): o pedido de abrir um programa, aqui com o verbo de licença."""

    _fields_ = [
        ("cbSize", wintypes.DWORD), ("fMask", ctypes.c_ulong), ("hwnd", wintypes.HWND),
        ("lpVerb", wintypes.LPCWSTR), ("lpFile", wintypes.LPCWSTR), ("lpParameters", wintypes.LPCWSTR),
        ("lpDirectory", wintypes.LPCWSTR), ("nShow", ctypes.c_int), ("hInstApp", wintypes.HINSTANCE),
        ("lpIDList", ctypes.c_void_p), ("lpClass", wintypes.LPCWSTR), ("hkeyClass", wintypes.HKEY),
        ("dwHotKey", wintypes.DWORD), ("hIconOrMonitor", wintypes.HANDLE), ("hProcess", wintypes.HANDLE),
    ]


class _ACL(ctypes.Structure):
    """O cabeçalho de uma lista de licenças (ACL)."""

    _fields_ = [("AclRevision", ctypes.c_ubyte), ("Sbz1", ctypes.c_ubyte), ("AclSize", wintypes.WORD),
                ("AceCount", wintypes.WORD), ("Sbz2", wintypes.WORD)]


class _ACE(ctypes.Structure):
    """Uma licença de permitir ou negar: cabeçalho, direitos e, logo depois, o SID."""

    _fields_ = [("AceType", ctypes.c_ubyte), ("AceFlags", ctypes.c_ubyte), ("AceSize", wintypes.WORD),
                ("Mask", wintypes.DWORD)]


class _DATA_BLOB(ctypes.Structure):
    """O pacote de bytes da cifra do Windows."""

    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


class _IO_COUNTERS(ctypes.Structure):
    """Parte da informação do grupo de processos (job)."""

    _fields_ = [(n, ctypes.c_ulonglong) for n in ("ReadOp", "WriteOp", "OtherOp", "ReadT", "WriteT", "OtherT")]


class _JOB_BASIC(ctypes.Structure):
    """JOBOBJECT_BASIC_LIMIT_INFORMATION."""

    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]


class _JOB_EXTENDED(ctypes.Structure):
    """JOBOBJECT_EXTENDED_LIMIT_INFORMATION (classe 9 do QueryInformationJobObject)."""

    _fields_ = [("BasicLimitInformation", _JOB_BASIC), ("IoInfo", _IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]


class _JOB_CONTAS(ctypes.Structure):
    """JOBOBJECT_BASIC_ACCOUNTING_INFORMATION (classe 1 do QueryInformationJobObject): quantos processos o grupo tem
    vivos agora (ActiveProcesses)."""

    _fields_ = [("TotalUserTime", ctypes.c_longlong), ("TotalKernelTime", ctypes.c_longlong),
                ("ThisPeriodTotalUserTime", ctypes.c_longlong), ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
                ("TotalPageFaultCount", wintypes.DWORD), ("TotalProcesses", wintypes.DWORD),
                ("ActiveProcesses", wintypes.DWORD), ("TotalTerminatedProcesses", wintypes.DWORD)]


class _THREADENTRY32(ctypes.Structure):
    """THREADENTRY32 (Toolhelp32): uma linha de execução (thread) de um processo, para achar a linha principal do
    programa aberto parado (`abrir_em_grupo`)."""

    _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ThreadID", wintypes.DWORD),
                ("th32OwnerProcessID", wintypes.DWORD), ("tpBasePri", wintypes.LONG), ("tpDeltaPri", wintypes.LONG),
                ("dwFlags", wintypes.DWORD)]


class _PROCESSENTRY32W(ctypes.Structure):
    """PROCESSENTRY32W (Toolhelp32): um processo da lista do Windows, com o número, o número de quem o abriu e o nome
    do programa (sem o caminho), lidos sem abrir o processo (`programas_rodando_de`; vinda da volta 4 do atualizador,
    22/11/2026, com o número de quem abriu, para deixar de fora os processos filhos deste)."""

    _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD), ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", wintypes.LONG), ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR * 260)]


class _Bibliotecas:
    """As funções do Windows que a peça usa, com os tipos certos e `use_last_error=True` (o erro de cada chamada
    fica guardado e é lido por `_ler_erro`, nunca um erro velho de outra chamada)."""

    def __init__(self) -> None:
        """Carrega as bibliotecas e declara os tipos de cada função usada (handles de 64 bits nunca cortados)."""
        P = ctypes.c_void_p
        k = self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        a = self.advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
        s = self.shell32 = ctypes.WinDLL("shell32", use_last_error=True)
        u = self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        o = self.ole32 = ctypes.WinDLL("ole32", use_last_error=True)
        c = self.crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
        declarar = [
            (k.WaitForSingleObject, [wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
            (k.GetExitCodeProcess, [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
            (k.CloseHandle, [wintypes.HANDLE], wintypes.BOOL),
            (k.LocalFree, [P], P),
            (k.GetCurrentProcess, [], wintypes.HANDLE),
            (k.GetSystemDirectoryW, [wintypes.LPWSTR, wintypes.UINT], wintypes.UINT),
            (k.OpenMutexW, [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR], wintypes.HANDLE),
            (k.IsProcessInJob, [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)], wintypes.BOOL),
            (k.QueryInformationJobObject, [wintypes.HANDLE, ctypes.c_int, P, wintypes.DWORD,
                                           ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
            (k.CreateJobObjectW, [P, wintypes.LPCWSTR], wintypes.HANDLE),
            (k.SetInformationJobObject, [wintypes.HANDLE, ctypes.c_int, P, wintypes.DWORD], wintypes.BOOL),
            (k.AssignProcessToJobObject, [wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
            (k.TerminateJobObject, [wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            (k.OpenProcess, [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            (k.OpenThread, [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            (k.ResumeThread, [wintypes.HANDLE], wintypes.DWORD),
            (k.CreateToolhelp32Snapshot, [wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
            (k.Thread32First, [wintypes.HANDLE, ctypes.POINTER(_THREADENTRY32)], wintypes.BOOL),
            (k.Thread32Next, [wintypes.HANDLE, ctypes.POINTER(_THREADENTRY32)], wintypes.BOOL),
            (k.Process32FirstW, [wintypes.HANDLE, ctypes.POINTER(_PROCESSENTRY32W)], wintypes.BOOL),
            (k.Process32NextW, [wintypes.HANDLE, ctypes.POINTER(_PROCESSENTRY32W)], wintypes.BOOL),
            (k.QueryFullProcessImageNameW, [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                            ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
            (k.GetCurrentProcessId, [], wintypes.DWORD),
            (a.GetNamedSecurityInfoW, [wintypes.LPCWSTR, ctypes.c_int, wintypes.DWORD, ctypes.POINTER(P),
                                       ctypes.POINTER(P), ctypes.POINTER(P), ctypes.POINTER(P), ctypes.POINTER(P)],
             wintypes.DWORD),
            (a.GetSecurityDescriptorControl, [P, ctypes.POINTER(wintypes.WORD), ctypes.POINTER(wintypes.DWORD)],
             wintypes.BOOL),
            (a.GetAce, [P, wintypes.DWORD, ctypes.POINTER(P)], wintypes.BOOL),
            (a.ConvertSidToStringSidW, [P, ctypes.POINTER(wintypes.LPWSTR)], wintypes.BOOL),
            (a.ConvertStringSidToSidW, [wintypes.LPCWSTR, ctypes.POINTER(P)], wintypes.BOOL),
            (a.LookupAccountSidW, [wintypes.LPCWSTR, P, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD),
                                   wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(ctypes.c_int)],
             wintypes.BOOL),
            (a.OpenProcessToken, [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)], wintypes.BOOL),
            (a.GetTokenInformation, [wintypes.HANDLE, ctypes.c_int, P, wintypes.DWORD,
                                     ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
            (a.CheckTokenMembership, [wintypes.HANDLE, P, ctypes.POINTER(wintypes.BOOL)], wintypes.BOOL),
            (a.ConvertStringSecurityDescriptorToSecurityDescriptorW, [wintypes.LPCWSTR, wintypes.DWORD,
                                                                      ctypes.POINTER(P), ctypes.POINTER(wintypes.DWORD)],
             wintypes.BOOL),
            (a.GetSecurityDescriptorDacl, [P, ctypes.POINTER(wintypes.BOOL), ctypes.POINTER(P),
                                           ctypes.POINTER(wintypes.BOOL)], wintypes.BOOL),
            (a.GetSecurityDescriptorOwner, [P, ctypes.POINTER(P), ctypes.POINTER(wintypes.BOOL)], wintypes.BOOL),
            (s.ShellExecuteExW, [ctypes.POINTER(_SHELLEXECUTEINFOW)], wintypes.BOOL),
            (s.SHGetKnownFolderPath, [ctypes.POINTER(_GUID), wintypes.DWORD, wintypes.HANDLE,
                                      ctypes.POINTER(wintypes.LPWSTR)], ctypes.c_long),
            (u.IsWindow, [wintypes.HWND], wintypes.BOOL),
            (u.IsIconic, [wintypes.HWND], wintypes.BOOL),
            (u.ShowWindow, [wintypes.HWND, ctypes.c_int], wintypes.BOOL),
            (u.SetForegroundWindow, [wintypes.HWND], wintypes.BOOL),
            (u.GetForegroundWindow, [], wintypes.HWND),
            (o.CoInitializeEx, [P, wintypes.DWORD], ctypes.c_long),
            (o.CoUninitialize, [], None),
            (o.CoTaskMemFree, [P], None),
            (c.CryptProtectData, [ctypes.POINTER(_DATA_BLOB), wintypes.LPCWSTR, P, P, P, wintypes.DWORD,
                                  ctypes.POINTER(_DATA_BLOB)], wintypes.BOOL),
            (c.CryptUnprotectData, [ctypes.POINTER(_DATA_BLOB), P, P, P, P, wintypes.DWORD,
                                    ctypes.POINTER(_DATA_BLOB)], wintypes.BOOL),
        ]
        for funcao, argumentos, volta in declarar:
            funcao.argtypes = argumentos
            funcao.restype = volta


@lru_cache(maxsize=1)
def _win() -> _Bibliotecas:
    """As bibliotecas do Windows, carregadas uma vez (fora do Windows, levanta OSError)."""
    if sys.platform != "win32":
        raise OSError("esta peça só funciona no Windows")
    return _Bibliotecas()


def bibliotecas_guardam_o_erro() -> dict[str, bool]:
    """Para cada biblioteca do Windows da peça, se ela guarda o erro de cada chamada (`use_last_error`). Tem de ser
    True em todas, em especial na `shell32`, que lê o "Não" da pergunta do Windows (defeito 2 da etapa 5: lido sem
    isso, o "Não" virava "deu certo"). Só leitura; para os testes conferirem sem tocar no que é de dentro."""
    w = _win()
    guarda = getattr(ctypes, "_FUNCFLAG_USE_LASTERROR", 0x10)
    return {nome: bool(getattr(w, nome)._FuncPtr._flags_ & guarda)
            for nome in ("kernel32", "advapi32", "shell32", "user32", "ole32", "crypt32")}


def _ler_erro() -> int:
    """O erro do Windows da última chamada feita por estas bibliotecas, NESTE fio (guardado pelo ctypes logo depois
    da chamada; `use_last_error=True`). Ler o erro de outro jeito pega um valor velho: foi assim que o "Não" virou
    "deu certo" na etapa 5."""
    return ctypes.get_last_error()


# ---------------------------------------------------------------------------------------------------------------------
# Onde ficam as coisas do Windows
# ---------------------------------------------------------------------------------------------------------------------

_PASTA_DE_PROGRAMAS = "905e63b6-c1bf-494e-b29c-65b732d3d21a"   # FOLDERID_ProgramFiles


def pasta_de_programas() -> Path:
    """Arquivos de Programas, perguntado ao Windows (não às variáveis de ambiente, que a conta pode mudar)."""
    w = _win()
    guid = _GUID.from_buffer_copy(uuid.UUID(_PASTA_DE_PROGRAMAS).bytes_le)
    saida = wintypes.LPWSTR()
    resultado = w.shell32.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(saida))
    try:
        if resultado != 0 or not saida.value:
            raise OSError(f"o Windows não disse onde fica Arquivos de Programas (0x{resultado & 0xFFFFFFFF:08X})")
        return Path(saida.value)
    finally:
        w.ole32.CoTaskMemFree(ctypes.cast(saida, ctypes.c_void_p))


def pasta_do_sistema() -> Path:
    """A pasta do sistema (System32), perguntada ao Windows."""
    buffer = ctypes.create_unicode_buffer(600)
    tamanho = _win().kernel32.GetSystemDirectoryW(buffer, len(buffer))
    if tamanho == 0 or tamanho >= len(buffer):
        raise OSError(f"o Windows não disse onde fica a pasta do sistema (erro {_ler_erro()})")
    return Path(buffer.value)


def _caminho_do_powershell() -> Path:
    """O PowerShell do Windows pelo caminho inteiro (nunca só pelo nome: defeito 5 do plano)."""
    return pasta_do_sistema() / "WindowsPowerShell" / "v1.0" / "powershell.exe"


def _comando_do_powershell(script: Path) -> list[str]:
    """O comando que roda um script do PowerShell (lugar único: rodar e esperar, lançar solto e as tarefas usam este):
    o caminho inteiro, sem o perfil da conta, sem perguntar nada, liberado para rodar o script (salvo política do
    computador, que vence este pedido) e pelo arquivo (nunca texto codificado na linha de comando)."""
    return [str(_caminho_do_powershell()), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File",
            str(script)]


def _ambiente_do_powershell() -> dict[str, str]:
    """O ambiente com que a peça abre o PowerShell do Windows (lugar único, ao lado de `_comando_do_powershell`; o
    rodar e esperar e o lançar solto usam este): o deste processo SEM a lista de pastas de módulos (PSModulePath).

    Por quê (bug de 19/11/2026, achado no GitHub no passo 2): quando o programa roda dentro de um PowerShell 7 (o
    Windows do GitHub; um terminal do pwsh), a lista herdada tem os módulos do PowerShell 7 na frente, e o PowerShell
    do Windows tenta carregá-los e falha ("CouldNotAutoloadMatchingModule": o Get-AuthenticodeSignature, o
    Remove-Item...). Lido na Microsoft (about_PSModulePath, Windows PowerShell 5.1): "If PSModulePath doesn't exist,
    combine CurrentUser, AllUsers, and the $PSHOME modules paths", e a nota "Inherited PowerShell 7 module paths
    precede the Windows PowerShell system module path [...] This breaks module autoloading". Sem a variável, ele
    monta a lista de fábrica. Arriscado: devolver a lista herdada (o defeito volta); tirar outras variáveis."""
    return {nome: valor for nome, valor in os.environ.items() if nome.upper() != "PSMODULEPATH"}


def _argumentos_do_powershell(script: Path) -> str:
    """Os argumentos de `_comando_do_powershell` numa linha só (para o campo de argumentos de uma tarefa)."""
    return subprocess.list2cmdline(_comando_do_powershell(script)[1:])


def _caminho_do_schtasks() -> Path:
    """A ferramenta de tarefas do Windows pelo caminho inteiro."""
    return pasta_do_sistema() / "schtasks.exe"


# ---------------------------------------------------------------------------------------------------------------------
# Quem sou eu
# ---------------------------------------------------------------------------------------------------------------------

def _sid_em_texto(psid: int) -> str:
    """O SID (ponteiro) em texto ("S-1-5-...")."""
    w = _win()
    texto = wintypes.LPWSTR()
    if not w.advapi32.ConvertSidToStringSidW(psid, ctypes.byref(texto)):
        raise OSError(f"não deu para ler um SID (erro {_ler_erro()})")
    try:
        return texto.value or ""
    finally:
        w.kernel32.LocalFree(ctypes.cast(texto, ctypes.c_void_p))


def sid_desta_conta() -> str:
    """O SID da conta que roda este processo (ex.: "S-1-5-21-...-1001")."""
    w = _win()
    token = wintypes.HANDLE()
    if not w.advapi32.OpenProcessToken(w.kernel32.GetCurrentProcess(), 0x0008, ctypes.byref(token)):  # TOKEN_QUERY
        raise OSError(f"não deu para ler a conta (erro {_ler_erro()})")
    try:
        tamanho = wintypes.DWORD()
        w.advapi32.GetTokenInformation(token, 1, None, 0, ctypes.byref(tamanho))      # TokenUser
        buffer = ctypes.create_string_buffer(tamanho.value)
        if not w.advapi32.GetTokenInformation(token, 1, buffer, tamanho, ctypes.byref(tamanho)):
            raise OSError(f"não deu para ler a conta (erro {_ler_erro()})")
        psid = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p))[0]                # TOKEN_USER.User.Sid
        return _sid_em_texto(psid)
    finally:
        w.kernel32.CloseHandle(token)


def tem_licenca_de_administrador() -> bool:
    """Este processo roda com a licença de administrador de verdade (o grupo Administradores ligado no token)?

    Conta comum, ou administrador sem a licença pedida (o grupo fica só "para negar"): False. Programa aberto pelo
    "Sim" da pergunta do Windows, ou como o sistema: True."""
    w = _win()
    psid = ctypes.c_void_p()
    if not w.advapi32.ConvertStringSidToSidW(SID_ADMINISTRADORES, ctypes.byref(psid)):
        return False
    try:
        dentro = wintypes.BOOL()
        if not w.advapi32.CheckTokenMembership(None, psid, ctypes.byref(dentro)):
            return False
        return bool(dentro.value)
    finally:
        w.kernel32.LocalFree(psid)


# ---------------------------------------------------------------------------------------------------------------------
# Licenças de pasta (só leitura) e as regras de quem pode gravar
# ---------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Licenca:
    """Uma linha da lista de licenças de uma pasta: quem (`sid`, `nome`), permite ou nega, os direitos (`mascara`),
    se veio da pasta de cima (`herdada`) e se só vale para o que nasce dentro (`so_para_dentro`)."""

    sid: str
    nome: str
    tipo: str              # "permite" | "nega" | "outra"
    mascara: int
    herdada: bool
    so_para_dentro: bool
    para_objetos: bool = False      # OBJECT_INHERIT_ACE: passa para os arquivos (ou as tarefas) que nascem dentro
    para_pastas: bool = False       # CONTAINER_INHERIT_ACE: passa para as pastas que nascem dentro (atualizador novo)

    @property
    def grava(self) -> bool:
        """Esta linha deixa mudar alguma coisa (gravar, apagar, mudar licença ou dono)?"""
        return self.tipo != "nega" and bool(self.mascara & _ESCRITA)

    @property
    def le(self) -> bool:
        """Esta linha deixa ler?"""
        return self.tipo == "permite" and bool(self.mascara & _LEITURA)

    def direitos(self) -> str:
        """Os direitos em português curto (para a janela de prova e o registro)."""
        m = self.mascara
        if m & 0x10000000 or m & 0x1F01FF == 0x1F01FF:
            texto = "controle total"
        elif m & 0x1301BF == 0x1301BF:
            texto = "modificar"
        elif self.grava:
            texto = "gravar"
        elif m & 0x1200A9 == 0x1200A9 or m & 0xA0000000 == 0xA0000000:
            texto = "ler e executar"
        elif self.le:
            texto = "ler"
        else:
            texto = f"direitos 0x{m:08X}"
        if self.tipo == "nega":
            texto = "NEGA " + texto
        if self.so_para_dentro:
            texto += " (só para o que nasce dentro)"
        return texto


@dataclass(frozen=True)
class Licencas:
    """As licenças de uma pasta: o dono, se a lista está protegida (não herda de cima), se não tem lista nenhuma (aí
    todos podem tudo) e as linhas."""

    caminho: str
    dono: str
    dono_nome: str
    protegida: bool
    sem_lista: bool
    lista: tuple[Licenca, ...]

    def quem_grava(self) -> set[str]:
        """Os SIDs que podem mudar alguma coisa; "todos" se não há lista; "desconhecida" se há linha que a peça não
        sabe ler (conta como gravar, por segurança)."""
        if self.sem_lista:
            return {"todos"}
        grava = {li.sid for li in self.lista if li.grava}
        if any(li.tipo == "outra" for li in self.lista):
            grava.add("desconhecida")
        return grava

    def quem_le(self) -> set[str]:
        """Os SIDs que podem ler; "todos" se não há lista; "desconhecida" se há linha que a peça não sabe ler."""
        if self.sem_lista:
            return {"todos"}
        le = {li.sid for li in self.lista if li.le}
        if any(li.tipo == "outra" for li in self.lista):
            le.add("desconhecida")
        return le

    def para_mostrar(self) -> list[str]:
        """Uma frase por linha, para a janela de prova ("BUILTIN\\Usuários: ler e executar")."""
        linhas = [f"dono: {nome_para_mostrar(self.dono, self.dono_nome)}"]
        if self.sem_lista:
            linhas.append("SEM LISTA DE LICENÇAS: todos podem tudo")
        linhas += [f"{nome_para_mostrar(li.sid, li.nome)}: {li.direitos()}" + (" (herdada)" if li.herdada else "")
                   for li in self.lista]
        return linhas


def _nome_da_conta(psid: int) -> str:
    """O nome da conta ou grupo ("BUILTIN\\Administradores"), ou "" se o Windows não souber."""
    w = _win()
    nome = ctypes.create_unicode_buffer(256)
    dominio = ctypes.create_unicode_buffer(256)
    n, d, uso = wintypes.DWORD(256), wintypes.DWORD(256), ctypes.c_int()
    if not w.advapi32.LookupAccountSidW(None, psid, nome, ctypes.byref(n), dominio, ctypes.byref(d),
                                        ctypes.byref(uso)):
        return ""
    return f"{dominio.value}\\{nome.value}" if dominio.value else nome.value


# As contas e grupos de fábrica do Windows, ditos em português pela peça (o Windows traduz o nome deles conforme a
# língua dele: "Todos" aqui, "Everyone" num Windows em inglês). Lugar único: toda frase da peça que cita uma conta
# passa por `nome_para_mostrar`.
_NOMES_DE_FABRICA = {
    "S-1-1-0": "Todos",
    SID_USUARIOS: "Usuários",
    SID_AUTENTICADOS: "Usuários autenticados",
    SID_SISTEMA: "o sistema",
    SID_ADMINISTRADORES: "Administradores",
    SID_INSTALADOR_CONFIAVEL: "o Instalador Confiável do Windows",
    SID_PROPRIETARIO_CRIADOR: "quem cria (Proprietário Criador)",
    SID_DIREITOS_DO_DONO: "o dono",
    "S-1-5-19": "o serviço local",
    "S-1-5-20": "o serviço de rede",
    "S-1-5-4": "quem usa este computador (Interativo)",
    "S-1-15-2-1": "os aplicativos da loja",
    "S-1-15-2-2": "os aplicativos da loja restritos",
    "S-1-5-32-546": "Convidados",
    "S-1-5-32-547": "Usuários avançados",
    "S-1-5-32-551": "Operadores de cópia",
    "S-1-5-32-555": "Usuários da área de trabalho remota",
    "S-1-5-32-556": "Operadores de configuração de rede",
    "S-1-5-32-558": "Usuários do monitor de desempenho",
    "S-1-5-32-559": "Usuários do log de desempenho",
    "S-1-5-32-562": "Usuários do COM distribuído",
    "S-1-5-32-568": "Usuários do servidor de páginas (IIS)",
    "S-1-5-32-569": "Operadores criptográficos",
    "S-1-5-32-573": "Leitores do registro de eventos",
    "S-1-5-32-578": "Administradores do Hyper-V",
    "S-1-5-32-579": "Operadores de assistência de controle de acesso",
    "S-1-5-32-580": "Usuários de gerenciamento remoto",
    "S-1-5-1": "quem entra por discagem",
    "S-1-5-2": "quem entra pela rede (Rede)",
    "S-1-5-3": "os trabalhos em lote",
    "S-1-5-6": "os serviços",
    "S-1-5-7": "quem entra sem conta (Anônimo)",
    "S-1-5-9": "os controladores de domínio",
    "S-1-5-10": "a própria conta (Self)",
    "S-1-5-12": "o código restrito",
    "S-1-5-13": "os usuários do terminal remoto",
    "S-1-5-14": "quem entra de longe (Logon interativo remoto)",
    "S-1-5-15": "esta organização",
    "S-1-5-17": "o usuário do servidor de páginas (IIS)",
    "S-1-5-33": "o código de escrita restrita",
    "S-1-5-64-10": "a autenticação NTLM",
    "S-1-5-113": "as contas locais",
    "S-1-5-114": "as contas locais administradoras",
    "S-1-2-0": "quem entra neste computador (Local)",
    "S-1-2-1": "quem entra pelo console",
    "S-1-3-1": "o grupo de quem cria (Grupo Criador)",
    "S-1-16-4096": "o nível baixo",
    "S-1-16-8192": "o nível médio",
    "S-1-16-12288": "o nível alto",
    "S-1-16-16384": "o nível do sistema",
    "todos": "todas as contas (a pasta não tem lista de licenças)",
    "desconhecida": "uma licença que a peça não sabe ler",
}


def _nome_do_sid_pelo_windows(sid: str) -> str:
    """O nome que o Windows dá à conta deste SID, ou "" se ele não souber (ou o SID não for válido)."""
    if not _SID.match(sid):
        return ""
    w = _win()
    psid = ctypes.c_void_p()
    if not w.advapi32.ConvertStringSidToSidW(sid, ctypes.byref(psid)):
        return ""
    try:
        return _nome_da_conta(psid.value)
    finally:
        w.kernel32.LocalFree(psid)


# As contas de fábrica que são grupos ou várias (o verbo vai no plural: "Todos podem", "Administradores podem").
_NOMES_NO_PLURAL = {sid for sid, nome in _NOMES_DE_FABRICA.items()
                    if sid.startswith("S-1-5-32-") or sid in ("S-1-1-0", SID_AUTENTICADOS, "S-1-5-6", "S-1-5-113",
                                                              "S-1-5-114", "S-1-15-2-1", "S-1-15-2-2", "S-1-5-9",
                                                              "S-1-5-13")}


def nome_para_mostrar(sid: str, nome_do_windows: str = "") -> str:
    """Como a peça diz uma conta numa frase (em português, sem código). Lugar único:
    - as de fábrica pelo nome em português (`_NOMES_DE_FABRICA`), nunca pelo que o Windows traduz;
    - as dos serviços do Windows ("NT SERVICE\\..."), "um serviço do Windows"; as permissões dos aplicativos da loja,
      "uma permissão de aplicativo da loja"; o administrador e o convidado embutidos, por esse nome;
    - as outras pelo nome que o Windows dá, SEM o nome do computador (ou do domínio) na frente;
    - sem nome, "outra conta deste computador". Nunca o SID cru."""
    if sid in _NOMES_DE_FABRICA:
        return _NOMES_DE_FABRICA[sid]
    if sid.startswith("S-1-5-80-"):
        return "um serviço do Windows"
    if sid.startswith("S-1-15-3-"):
        return "uma permissão de aplicativo da loja"
    if re.match(r"^S-1-5-21-\d+-\d+-\d+-500$", sid):
        return "o administrador embutido do Windows"
    if re.match(r"^S-1-5-21-\d+-\d+-\d+-501$", sid):
        return "o convidado embutido do Windows"
    nome = nome_do_windows or (_nome_do_sid_pelo_windows(sid) if sid else "")
    nome = nome.rsplit("\\", 1)[-1].strip()
    return nome or "outra conta deste computador"


def frase_da_conta(sid: str, nome_do_windows: str, singular: str, plural: str) -> str:
    """A conta e o verbo concordando: "Todos podem mexer...", "fotog pode mexer..." (`singular` e `plural` são o resto
    da frase, começando pelo verbo)."""
    return f"{nome_para_mostrar(sid, nome_do_windows)} {plural if sid in _NOMES_NO_PLURAL else singular}"


def ler_licencas(caminho: Path | str) -> Licencas:
    """Lê o dono e a lista de licenças de uma pasta ou arquivo (só lê; nunca muda nada). Levanta OSError (com o
    número do erro do Windows) se não der para ler."""
    w = _win()
    dono, grupo, lista, sacl, descritor = (ctypes.c_void_p() for _ in range(5))
    erro = w.advapi32.GetNamedSecurityInfoW(str(caminho), 1, 0x1 | 0x4,          # SE_FILE_OBJECT; dono e lista
                                            ctypes.byref(dono), ctypes.byref(grupo), ctypes.byref(lista),
                                            ctypes.byref(sacl), ctypes.byref(descritor))
    if erro != 0:
        raise OSError(erro, f"não deu para ler as licenças de {caminho} (erro {erro})")
    try:
        controle, revisao = wintypes.WORD(), wintypes.DWORD()
        w.advapi32.GetSecurityDescriptorControl(descritor, ctypes.byref(controle), ctypes.byref(revisao))
        return Licencas(str(caminho), _sid_em_texto(dono.value) if dono.value else "",
                        _nome_da_conta(dono.value) if dono.value else "", bool(controle.value & _DACL_PROTEGIDA),
                        not lista.value, tuple(_linhas_da_lista(lista, str(caminho))))
    finally:
        w.kernel32.LocalFree(descritor)


def _linhas_da_lista(lista: ctypes.c_void_p, de_onde: str) -> list[Licenca]:
    """As linhas de uma lista de licenças do Windows (lugar único: a pasta e a tarefa usam este)."""
    w = _win()
    linhas: list[Licenca] = []
    if not lista.value:
        return linhas
    for i in range(ctypes.cast(lista, ctypes.POINTER(_ACL)).contents.AceCount):
        ace = ctypes.c_void_p()
        if not w.advapi32.GetAce(lista, i, ctypes.byref(ace)):
            raise OSError(f"não deu para ler a licença {i} de {de_onde} (erro {_ler_erro()})")
        cabeca = ctypes.cast(ace, ctypes.POINTER(_ACE)).contents
        herdada, so_dentro = bool(cabeca.AceFlags & _ACE_HERDADA), bool(cabeca.AceFlags & _ACE_SO_PARA_DENTRO)
        objetos = bool(cabeca.AceFlags & 0x01)                                     # OBJECT_INHERIT_ACE
        pastas = bool(cabeca.AceFlags & 0x02)                                      # CONTAINER_INHERIT_ACE
        if cabeca.AceType in (_ACE_PERMITE, _ACE_NEGA):
            psid = ace.value + 8
            linhas.append(Licenca(_sid_em_texto(psid), _nome_da_conta(psid),
                                  "permite" if cabeca.AceType == _ACE_PERMITE else "nega", cabeca.Mask, herdada,
                                  so_dentro, objetos, pastas))
        else:
            linhas.append(Licenca("", "", "outra", cabeca.Mask, herdada, so_dentro, objetos, pastas))
    return linhas


def licencas_do_texto(sddl: str) -> list[Licenca]:
    """As linhas de uma licença escrita em texto do Windows ("D:(A;;FA;;;BA)..."), lidas pelo próprio Windows (o
    mesmo leitor das pastas). Levanta OSError se o Windows não aceitar o texto."""
    w = _win()
    descritor, tamanho = ctypes.c_void_p(), wintypes.DWORD()
    if not w.advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, ctypes.byref(descritor),
                                                                         ctypes.byref(tamanho)):
        raise OSError(f"o Windows não aceitou a licença {sddl!r} (erro {_ler_erro()})")
    try:
        presente, padrao, lista = wintypes.BOOL(), wintypes.BOOL(), ctypes.c_void_p()
        if not w.advapi32.GetSecurityDescriptorDacl(descritor, ctypes.byref(presente), ctypes.byref(lista),
                                                    ctypes.byref(padrao)):
            raise OSError(f"não deu para ler a licença {sddl!r} (erro {_ler_erro()})")
        return _linhas_da_lista(lista, sddl) if presente.value else []
    finally:
        w.kernel32.LocalFree(descritor)


def dono_do_texto(sddl: str) -> str:
    """O dono escrito numa licença em texto ("O:BA...", "O:S-1-5-21-..."), em SID, lido pelo próprio Windows; "" se
    não há dono no texto. Levanta OSError se o Windows não aceitar o texto."""
    w = _win()
    descritor, tamanho = ctypes.c_void_p(), wintypes.DWORD()
    if not w.advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, ctypes.byref(descritor),
                                                                         ctypes.byref(tamanho)):
        raise OSError(f"o Windows não aceitou a licença {sddl!r} (erro {_ler_erro()})")
    try:
        dono, padrao = ctypes.c_void_p(), wintypes.BOOL()
        if not w.advapi32.GetSecurityDescriptorOwner(descritor, ctypes.byref(dono), ctypes.byref(padrao)):
            raise OSError(f"não deu para ler o dono de {sddl!r} (erro {_ler_erro()})")
        return _sid_em_texto(dono.value) if dono.value else ""
    finally:
        w.kernel32.LocalFree(descritor)


# Direitos numa pasta do Agendador que deixam mexer no que já existe nela: mudar a licença ou o dono, apagar, apagar o
# que está dentro, tudo. O "gravar" de fábrica que o Windows dá às contas comuns (criar tarefas DELAS na pasta, com
# a licença "FW", só para a pasta e as de dentro) não entra: com ele ninguém mexe nas tarefas do programa.
_MEXER_NA_PASTA_DE_TAREFAS = 0x40000 | 0x80000 | 0x10000 | 0x40 | 0x10000000


def problemas_da_pasta_de_tarefas(sddl: str) -> list[str]:
    """A pasta do programa no Agendador (`\\EditorImpressao`) é segura para o ajudante? O dono é o sistema ou os
    Administradores; nenhuma conta comum pode mexer no que já está nela (mudar licença ou dono, apagar); e nenhuma
    licença que passa para as tarefas deixa conta comum gravar nelas. A licença de fábrica que o Windows dá a uma pasta
    nova criada por administrador passa (lida em 19/11 nas pastas do Windows); uma pasta criada antes por uma conta
    comum (dona) ou que dá controle total a "Todos" não passa. Levanta OSError se o Windows não aceitar o texto."""
    problemas = []
    dono = dono_do_texto(sddl)
    if dono not in (SID_SISTEMA, SID_ADMINISTRADORES, SID_INSTALADOR_CONFIAVEL):
        problemas.append(f"o dono da pasta do programa no Agendador é {nome_para_mostrar(dono)}, não o sistema nem os "
                         "Administradores")
    admins = {SID_SISTEMA, SID_ADMINISTRADORES, SID_INSTALADOR_CONFIAVEL, SID_PROPRIETARIO_CRIADOR}
    for li in licencas_do_texto(sddl):
        if li.tipo == "nega" or li.sid in admins:
            continue
        if li.tipo == "outra":
            problemas.append("a pasta do programa no Agendador tem uma licença que a peça não sabe ler")
        elif _direitos(li.mascara) & _MEXER_NA_PASTA_DE_TAREFAS:
            problemas.append(frase_da_conta(li.sid, li.nome, "pode mexer na pasta do programa no Agendador",
                                            "podem mexer na pasta do programa no Agendador"))
        elif li.para_objetos and _direitos(li.mascara) & _ESCRITA:
            problemas.append(frase_da_conta(li.sid, li.nome,
                                            "poderia mudar as tarefas da pasta do programa no Agendador",
                                            "poderiam mudar as tarefas da pasta do programa no Agendador"))
    return problemas


# Os direitos "genéricos" escritos do jeito dos arquivos (o Agendador devolve "FRFX" como 0x1200a9, lido em 19/11).
_GENERICOS = {0x80000000: 0x120089, 0x40000000: 0x120116, 0x20000000: 0x1200A0, 0x10000000: 0x1F01FF}


def _direitos(mascara: int) -> int:
    """Os direitos com os "genéricos" trocados pelos de arquivo (para comparar o pedido com o que o Windows devolve)."""
    for generico, especifico in _GENERICOS.items():
        if mascara & generico:
            mascara = (mascara & ~generico) | especifico
    return mascara


def problemas_da_licenca_da_tarefa(pedida: str, efetiva: str) -> list[str]:
    """A licença que o Windows diz que a tarefa tem (`efetiva`, lida com `GetSecurityDescriptor`) cumpre a pedida?

    Pelo sentido, não pelo texto (o Agendador acrescenta as licenças herdadas da pasta e reescreve os direitos): cada
    conta da pedida tem na efetiva pelo menos os direitos pedidos; e ninguém que não seja o sistema, os administradores
    ou quem a pedida deixa mudar pode mudar a tarefa. Levanta OSError se o Windows não aceitar um dos textos."""
    pedidas = [li for li in licencas_do_texto(pedida) if li.tipo == "permite"]
    efetivas = [li for li in licencas_do_texto(efetiva) if li.tipo == "permite"]
    problemas = []
    for li in pedidas:
        tem = 0
        for e in efetivas:
            if e.sid == li.sid:
                tem |= _direitos(e.mascara)
        if _direitos(li.mascara) & ~tem:
            problemas.append(frase_da_conta(li.sid, li.nome, "não ficou com os direitos pedidos na tarefa",
                                            "não ficaram com os direitos pedidos na tarefa"))
    pode_mudar = {SID_SISTEMA, SID_ADMINISTRADORES, SID_INSTALADOR_CONFIAVEL}
    pode_mudar |= {li.sid for li in pedidas if _direitos(li.mascara) & _ESCRITA}
    for e in efetivas:
        if _direitos(e.mascara) & _ESCRITA and e.sid not in pode_mudar:
            problemas.append(frase_da_conta(e.sid, e.nome, "pode mudar a tarefa", "podem mudar a tarefa"))
    return problemas


def e_atalho(caminho: Path) -> bool:
    """O caminho é um atalho do sistema de arquivos (junção ou link simbólico) para outro lugar?"""
    try:
        info = os.lstat(caminho)
    except OSError:
        return False
    return bool(getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT) or stat.S_ISLNK(
        info.st_mode)


def problemas_da_pasta_de_troca(licencas: Licencas, sid_da_conta: str) -> list[str]:
    """A pasta de troca é só da conta que pediu? Só ela, o sistema e os administradores podem gravar E ler (o segredo
    vai ali, cifrado para o computador: quem lê o arquivo abre o segredo, achado 8 de quem tentou quebrar); o dono é
    ela, o sistema ou os Administradores (quem já roda com a licença ligada cria com dono Administradores).

    Lugar único da regra: o lado que pede confere logo depois de criar, e o lado com licença confere antes de ler."""
    problemas = []
    if licencas.dono not in (sid_da_conta, SID_SISTEMA, SID_ADMINISTRADORES):
        problemas.append(f"o dono da pasta é {nome_para_mostrar(licencas.dono, licencas.dono_nome)}, não a conta que "
                         "pediu")
    aceitos = {sid_da_conta, SID_SISTEMA, SID_ADMINISTRADORES, SID_PROPRIETARIO_CRIADOR, SID_DIREITOS_DO_DONO}
    for quem in sorted(licencas.quem_grava() - aceitos):
        problemas.append(f"outra conta pode gravar na pasta: {nome_para_mostrar(quem)}")
    for quem in sorted(licencas.quem_le() - aceitos):
        problemas.append(f"outra conta pode ler a pasta: {nome_para_mostrar(quem)}")
    return problemas


def problemas_da_pasta_segura(licencas: Licencas) -> list[str]:
    """A pasta segura tem só as licenças de fábrica de Arquivos de Programas? O dono é o sistema, os administradores
    ou o Instalador Confiável; só eles (e o "Proprietário Criador", que vira o dono) podem gravar; as contas comuns
    leem."""
    problemas = []
    donos = (SID_SISTEMA, SID_ADMINISTRADORES, SID_INSTALADOR_CONFIAVEL)
    if licencas.dono not in donos:
        problemas.append(f"o dono da pasta é {nome_para_mostrar(licencas.dono, licencas.dono_nome)} (deveria ser o "
                         "sistema ou os "
                         "administradores)")
    aceitos = {SID_SISTEMA, SID_ADMINISTRADORES, SID_INSTALADOR_CONFIAVEL, SID_PROPRIETARIO_CRIADOR}
    for quem in sorted(licencas.quem_grava() - aceitos):
        problemas.append(f"uma conta que não é administradora pode gravar na pasta: {nome_para_mostrar(quem)}")
    if not any(li.le and not li.so_para_dentro and li.sid in (SID_USUARIOS, SID_AUTENTICADOS)
               for li in licencas.lista):
        problemas.append("as contas comuns não conseguem ler a pasta")
    return problemas


# ---------------------------------------------------------------------------------------------------------------------
# A pasta de troca
# ---------------------------------------------------------------------------------------------------------------------

def _pasta_mae_da_troca() -> Path:
    """`<pasta de dados do programa>\\troca` (a pasta de dados vem do lugar único dela, `historico.pasta_de_dados`;
    importada só aqui porque puxa o processamento e custa ~1 s)."""
    from historico import pasta_de_dados

    return pasta_de_dados() / NOME_DA_PASTA_MAE_DA_TROCA


def _criar_pasta_comum(caminho: Path) -> None:
    """Cria a pasta com `os.mkdir` comum, herdando as licenças da pasta de cima. NUNCA com o modo 0o700 nem com o
    `tempfile.mkdtemp` (ver o topo: o defeito 13 da etapa 5)."""
    os.mkdir(caminho)


def _limpar_trocas_velhas(mae: Path) -> None:
    """Apaga as pastas de troca que sobraram de pedidos antigos (mais de um dia), quando dá; nunca levanta."""
    limite = time.time() - DIAS_ATE_LIMPAR_TROCA_VELHA * 86400
    try:
        for pasta in mae.iterdir():
            if pasta.name.startswith(PREFIXO_DA_TROCA) and not e_atalho(pasta) and pasta.stat().st_mtime < limite:
                shutil.rmtree(pasta, ignore_errors=True)
    except OSError:
        pass


def criar_pasta_de_troca() -> Path:
    """Cria uma pasta de troca nova (nome sorteado) e devolve o caminho. Levanta OSError se não deu (disco cheio,
    pasta de dados sem licença)."""
    mae = _pasta_mae_da_troca()
    if not mae.is_dir():
        _criar_pasta_comum(mae)
    if e_atalho(mae):
        raise OSError(f"a pasta {mae} é um atalho para outro lugar")
    _limpar_trocas_velhas(mae)
    pasta = mae / f"{PREFIXO_DA_TROCA}{datetime.now():%Y%m%d-%H%M%S}-{secrets.token_hex(4)}"
    _criar_pasta_comum(pasta)
    return pasta


def apagar_pasta_de_troca(pasta: Path) -> bool:
    """Apaga a pasta de troca com tudo dentro e confere que sumiu. Só apaga uma pasta de troca de verdade (nome e
    lugar certos, não um atalho). True = não existe mais."""
    pasta = Path(pasta)
    if not pasta.name.startswith(PREFIXO_DA_TROCA) or pasta.parent.name != NOME_DA_PASTA_MAE_DA_TROCA:
        return False
    if e_atalho(pasta):
        return False
    shutil.rmtree(pasta, ignore_errors=True)
    if pasta.exists():
        _registrar("apagar a pasta de troca", f"sobrou {pasta}: {sorted(p.name for p in pasta.iterdir())}")
        return False
    return True


def gravar_no_disco(arquivo) -> None:
    """Pede ao Windows que grave no disco, agora, o que ele ainda guarda na memória para este arquivo (aberto para
    ESCREVER). O LUGAR ÚNICO dessa conversa. Quem passa por ela hoje, antes de conferir e de trocar o nome provisório
    pelo nome certo: `_gravar_por_inteiro` (aqui: o aviso, os scripts, a tarefa, o segredo, a pasta segura, o
    relatório), `empacotar.copiar_inteiro` e `empacotar.zipar_motor`. Quem grava num nome provisório e NÃO passa por ela
    (passo 2, volta 5, achado 6 do relatório 4; fora deste passo, a ideia de estender está na Lista de espera): a ficha
    do motor (`montar_motor_kraken.py`), o PDF de saída (`core/pipeline.py`) e os projetos (`projetos.py`). Passo 2, volta 4, achado 11 do relatório 3 de quem tentou quebrar: a cópia dizia "lida
    de volta do disco" sem pedir isso, e se a luz caísse logo depois da troca do nome, o nome certo podia ficar com o
    conteúdo pela metade.

    Lido (D-813): Python, `os.fsync` (com um arquivo do Python, primeiro `flush()`, depois `os.fsync(fileno())`; no
    Windows ele chama o `_commit` da biblioteca C); Microsoft Learn, `_commit`: "Flushes a file directly to disk",
    devolve -1 no erro (vira OSError); FlushFileBuffers: "The file handle must have the GENERIC_WRITE access right"
    (por isso o arquivo tem de estar aberto para escrever). O que NÃO faz: a leitura de volta continua vindo do que o
    Windows guarda na memória; e o nome trocado (a pasta) não é gravado à parte. Levanta OSError (quem chama trata como
    erro do disco). Arriscado: tirar (a troca do nome volta a poder chegar antes do conteúdo)."""
    arquivo.flush()
    os.fsync(arquivo.fileno())


def _gravar_por_inteiro(caminho: Path, conteudo: bytes) -> None:
    """Grava o arquivo inteiro de uma vez (num arquivo ao lado, gravado no disco, e depois troca o nome): quem lê nunca
    vê pela metade, e a troca do nome não chega antes do conteúdo (`gravar_no_disco`)."""
    provisorio = caminho.with_name(caminho.name + ".gravando")
    with open(provisorio, "wb") as arquivo:
        arquivo.write(conteudo)
        gravar_no_disco(arquivo)
    os.replace(provisorio, caminho)


def _gravar_script(caminho: Path, texto: str) -> None:
    """Grava um script do PowerShell em UTF-8 COM a marca (BOM): sem ela o PowerShell 5.1 lê o script como ANSI."""
    _gravar_por_inteiro(caminho, texto.encode("utf-8-sig"))


def aspas_do_powershell(texto: object) -> str:
    """Texto entre aspas simples do PowerShell (a aspa simples dobra). Só para valores de uma linha."""
    texto = str(texto)
    if "\n" in texto or "\r" in texto:
        raise ValueError("valor com quebra de linha não vai para o script")
    return "'" + texto.replace("'", "''") + "'"


# ---------------------------------------------------------------------------------------------------------------------
# Rodar e esperar
# ---------------------------------------------------------------------------------------------------------------------

def _como_o_windows_completa(texto: str) -> str:
    """O nome do programa como o Windows o completa antes de abrir (passo 2, volta 4, achado 2 do relatório 3 de quem
    tentou quebrar: a lista de nomes com função própria comparava o texto cru, e `pwsh.exe.` passava; o nome sozinho
    `whoami.exe.` rodava o whoami da pasta do Windows).

    Lido (D-813): Microsoft Learn, "File path formats on Windows systems", "Path normalization": "Almost all paths passed
    to Windows APIs are normalized" (pelo GetFullPathName); "Trim characters": "If the path doesn't end in a separator,
    all trailing periods and spaces (U+0020) are removed". O `os.path.abspath` do Python, no Windows, é o
    GetFullPathNameW. Rodado no PC (20/11): com pasta, `x.exe.` e `x.exe .` rodam o x.exe; o nome sozinho achado pelo
    PATH também (`x.exe.`, `x.exe..`, `x.exe. ` rodaram; `x.` não), e o `shutil.which` não acha nenhum deles.
    Com pasta (ou letra de disco): o caminho inteiro pelo GetFullPathNameW. Só o nome: o mesmo corte do fim (pontos e
    espaços), sem pôr a pasta atual (o Windows procura o nome sozinho em outros lugares). Levanta ValueError/OSError
    para o que o Windows não entende (quem chama recusa). Arriscado: comparar qualquer coisa pelo texto de antes."""
    if os.path.dirname(texto) or re.match(r"^[A-Za-z]:", texto):
        return os.path.abspath(texto)
    return texto.rstrip(". ")


def _caminho_do_programa(programa: str) -> Path | None:
    """O caminho do programa, normalizado num lugar só para comparar, UMA VEZ, e todas as conferências da regra única
    (`_por_que_recusa`) usam este: sem aspas; o que vem com o prefixo de caminho
    longo ou de dispositivo (duas barras com interrogação ou com ponto, que o Windows aceita para o mesmo arquivo) é
    resolvido inteiro pelo Windows e só então perde o prefixo (assim o "raiz global" e o "volume por número" viram a
    letra de disco de verdade); e, no fim, como o Windows o completa (`_como_o_windows_completa`: os pontos e espaços do
    fim saem). None para
    caminho de rede (duas barras e o nome de um computador, inclusive pelo prefixo longo com UNC): ele pode apontar
    para a pasta do Windows deste computador por outro nome (ex.: o "C$" ou o "ADMIN$" do "localhost"), e o rodar
    genérico não o aceita; e None para o que o Windows não consegue completar."""
    texto = str(programa).strip().strip('"').replace("/", "\\")
    for prefixo in ("\\\\?\\UNC\\", "\\\\.\\UNC\\"):
        if texto.upper().startswith(prefixo.upper()):
            return None
    prefixos = ("\\\\?\\", "\\\\.\\", "\\??\\")
    if texto.startswith(prefixos):
        # O caminho INTEIRO é resolvido pelo Windows antes de tirar o prefixo (achado T1 da terceira volta): o "raiz
        # global" e o "volume por número" só viram uma letra de disco assim. Depois de resolver, só vale caminho com
        # letra de disco; o que não virou letra (rede, dispositivo desconhecido) é recusado.
        try:
            texto = os.path.realpath(texto)
        except (OSError, ValueError):
            return None
        for prefixo in prefixos:
            if texto.startswith(prefixo):
                texto = texto[len(prefixo):]
                break
        if not re.match(r"^[A-Za-z]:\\", texto):
            return None
    if texto.startswith("\\\\"):
        return None
    try:
        texto = _como_o_windows_completa(texto)
    except (OSError, ValueError):
        return None
    if texto.startswith("\\\\"):
        return None
    return Path(texto)


# Os arquivos que o Windows NÃO roda como programa e entrega ao cmd.exe (que é da pasta do Windows e tem função própria
# na peça). Passo 2, volta 3: achado 3 do relatório 2 de quem tentou quebrar (19/11/2026, família F2: um `x.bat` fora
# da pasta do Windows passava pela recusa, e o Windows o rodava pelo C:\Windows\System32\cmd.exe).
# Lido (D-813, "tudo o que a peça aceita como entrada"):
# - Microsoft Learn, CreateProcessW, lpApplicationName: o módulo é "a Windows-based application" ou, "if the appropriate
#   subsystem is available", "some other type of module (for example, MS-DOS or OS/2)"; "To run a batch file, you must
#   start the command interpreter" (o cmd.exe); sem extensão, ".exe is appended"; sem pasta, a busca é: a pasta do
#   programa que chama, a pasta atual, System32, System, Windows, o PATH.
# - Python 3.14, subprocess, "Security Considerations": "On Windows, batch files (*.bat or *.cmd) may be launched by the
#   operating system in a system shell regardless of the arguments passed to this library". Ou seja: o próprio
#   CreateProcess, chamado pelo subprocess sem shell, abre o cmd.exe para um .bat ou .cmd.
# - Rodado no PC (Windows 11, 20/11/2026, subprocess sem shell, um lote que escreve a variável COMSPEC): "x.bat", "X.BAT"
#   e "x.bat " (com espaço no fim) rodaram pelo cmd.exe; "x.bat." e o prefixo de caminho longo abriram algo que saiu com
#   código 1; "x.bat::$DATA" deu o erro 193 e um lote com nome de .exe, o erro 216 (não rodaram). Um lote que começa
#   com "MZ" também dá o erro 216: o Windows só entrega ao cmd.exe o que NÃO começa com "MZ". O os.path.abspath (o
#   GetFullPathNameW do Windows) tira o ponto e o espaço do fim ("x.bat." e "x.bat " viram o x.bat).
# Por isso a recusa olha a COISA DE VERDADE em dois jeitos (`_por_que_nao_e_programa`): a extensão do caminho já
# completado pelo Windows, e o começo do arquivo (todo programa do Windows começa com as letras "MZ"; o que não
# começa ou é lote, que vai ao cmd.exe, ou é de um subsistema que este Windows de 64 bits não tem). Arriscado: tirar
# uma das duas (a extensão pega o lote que não se acha pelo nome; o começo pega o nome escrito de outro jeito).
_EXTENSOES_DE_LOTE = (".bat", ".cmd")
_COMECO_DE_PROGRAMA = b"MZ"


# As frases da recusa (passo 2, volta 4, achado 6 do relatório 3: o "não consegui ler" saía com a frase do "tem função
# própria", que manda usar uma função que não existe). Uma frase para cada motivo; seguro mexer no texto.
FRASE_TEM_FUNCAO_PROPRIA = "este programa do Windows tem função própria na peça: use a função dela"
FRASE_NAO_LI_O_PROGRAMA = "não consegui ler o programa para saber se é um programa do Windows"
FRASE_SEM_A_PASTA_DO_WINDOWS = "não consegui saber onde fica a pasta do Windows para conferir o programa"
FRASE_FLUXO_ESCONDIDO = ("o programa pedido é um fluxo escondido dentro de outro arquivo (o caminho tem \":\" depois "
                         "da letra do disco): a peça não roda")
# Passo 2, volta 6, achado 3 do relatório 5 (F7): o caminho de rede, e o que o Windows não completa com uma letra de
# disco, saíam com a frase do "tem função própria ... use a função dela" (uma função que não existe). O motivo de
# verdade: por esse caminho a peça não consegue saber se o programa é um do Windows (que tem função própria na peça:
# o "C$" do "localhost" é a pasta do Windows deste computador por outro nome), e por isso não roda.
FRASE_CAMINHO_DE_REDE = ("o programa pedido está num caminho de rede, ou num caminho que o Windows não completa com a "
                         "letra de um disco: por ele, a peça não consegue saber se é um programa do Windows (que tem "
                         "função própria na peça) e não roda; peça o programa pelo caminho com a letra do disco deste "
                         "computador")


def _por_que_nao_e_programa(caminho: Path) -> str | None:
    """O arquivo é algo que o Windows não roda como programa e entregaria a outro (o cmd.exe)? Devolve o motivo da
    recusa, ou None. Recusa (FRASE_TEM_FUNCAO_PROPRIA) se o nome, depois de o Windows completar o caminho (tira pontos e
    espaços do fim), acaba em .bat ou .cmd, ou se o arquivo existe e não começa com "MZ". Recusa com
    FRASE_NAO_LI_O_PROGRAMA se ele existe e não deu para ler o começo (na dúvida, recusa; achado 6 do relatório 3: os
    atalhos da Loja, em %LOCALAPPDATA%\\Microsoft\\WindowsApps, existem para o `isfile` e dão o erro 22 ao abrir, rodado
    no PC em 20/11). Arquivo que não existe: None (o Windows não acha e o rodar devolve "não achei o programa")."""
    try:
        completo = os.path.abspath(str(caminho))            # GetFullPathNameW: "x.bat. " vira "x.bat"
    except (OSError, ValueError):
        return FRASE_NAO_LI_O_PROGRAMA
    if completo.rstrip(". ").lower().endswith(_EXTENSOES_DE_LOTE):
        return FRASE_TEM_FUNCAO_PROPRIA
    try:
        if not os.path.isfile(completo):
            return None
        with open(completo, "rb") as arquivo:
            comeco = arquivo.read(len(_COMECO_DE_PROGRAMA))
    except OSError:
        return FRASE_NAO_LI_O_PROGRAMA
    return None if comeco == _COMECO_DE_PROGRAMA else FRASE_TEM_FUNCAO_PROPRIA


def _e_fluxo_escondido(caminho: Path) -> bool:
    """O caminho (já completado como o Windows o completa) aponta para um FLUXO de um arquivo, e não para o arquivo?
    Sim se tem ":" depois da letra do disco. Lido (D-813): Microsoft Learn, "File Streams (Local File Systems)": o nome
    completo de um fluxo é "filename:stream name:stream type" ("myfile.dat:stream1:$DATA"), e "filename::$DATA" é o
    próprio arquivo; "Naming Files, Paths, and Namespaces": o ":" está entre os caracteres reservados de um nome, e
    "C:tmp.txt" é relativo à pasta atual do disco C (o ":" da letra do disco). Então, fora do "C:" do começo, um ":"
    só pode ser de fluxo. Rodado (quem tentou quebrar, volta 4, e o teste da volta 5): o Windows roda
    "nada.txt:pwsh.exe". Na dúvida, recusa (o "::$DATA" do próprio arquivo também, que o Windows nem roda)."""
    texto = str(caminho)
    resto = texto[2:] if re.match(r"^[A-Za-z]:", texto) else texto
    return ":" in resto


def _por_que_recusa(programa: str) -> str | None:
    """A REGRA ÚNICA do rodar genérico, do lançar solto genérico e do grupo (`abrir_em_grupo`, e por ele o
    `rodar_em_grupo`): o motivo de recusar o programa (a frase para a tela), ou None (pode rodar).

    O nome é lido UMA VEZ, como o Windows o completa (`_caminho_do_programa`; passo 2, volta 4, achado 2 do relatório 3:
    antes a lista de nomes e o nome sozinho eram comparados pelo texto cru, e `pwsh.exe.` e `whoami.exe.` passavam), e
    todas as conferências abaixo usam esse mesmo nome. Recusa (com a frase de cada motivo):
    - caminho de rede, ou que o Windows não completa (`_caminho_do_programa` devolve None), com a frase própria
      (`FRASE_CAMINHO_DE_REDE`; passo 2, volta 6, achado 3 do relatório 5: antes, a do "tem função própria");
    - o nome de `PROGRAMAS_COM_FUNCAO_PROPRIA` (o PowerShell 7, o atualizador do Velopack);
    - o que não é programa do Windows de verdade (um .bat ou .cmd, que o Windows roda pelo cmd.exe) ou que não deu
      para ler (`_por_que_nao_e_programa`);
    - um fluxo escondido de outro arquivo (`_e_fluxo_escondido`: "nada.txt:pwsh.exe"; passo 2, volta 5, achado 5 do
      relatório 4); vem depois do lote para o "x.bat::$DATA" continuar com a frase do lote;
    - o que está na pasta do Windows (ou, dado só pelo nome, é achado lá: o Windows procura na pasta do sistema antes
      do PATH); na dúvida (não deu para saber onde fica a pasta do Windows), recusa;
    - de novo depois de achar o arquivo de verdade (o nome sozinho pode virar um .BAT pelo PATHEXT do `which`, ou o
      caminho passar por um atalho).
    Limite conhecido (achado 5 do relatório 3, escolha da gerente no passo 1: "a regra é pela pasta"): uma CÓPIA de um
    programa do Windows fora da pasta do Windows, com outro nome, passa. Arriscado: comparar pelo texto de antes de
    completar; tirar uma das conferências (cada uma tem o seu teste em tests/test_windows_peca.py)."""
    caminho = _caminho_do_programa(programa)
    if caminho is None:
        return FRASE_CAMINHO_DE_REDE
    nome = caminho.name.lower()
    if nome.removesuffix(".exe") in PROGRAMAS_COM_FUNCAO_PROPRIA:
        return FRASE_TEM_FUNCAO_PROPRIA
    motivo = _por_que_nao_e_programa(caminho)
    if motivo:
        return motivo
    if _e_fluxo_escondido(caminho):
        return FRASE_FLUXO_ESCONDIDO
    try:
        sistema = pasta_do_sistema()
    except OSError:
        return FRASE_SEM_A_PASTA_DO_WINDOWS
    pasta_do_windows = sistema.parent
    if len(caminho.parts) == 1:                                 # só o nome: onde o Windows o acharia
        com_exe = nome if nome.endswith(".exe") else nome + ".exe"
        if any((pasta / com_exe).exists() for pasta in (sistema, pasta_do_windows)):
            return FRASE_TEM_FUNCAO_PROPRIA
        achado = shutil.which(str(caminho))
        if not achado:
            return None
        caminho = Path(achado)
    try:
        caminho = caminho.resolve()
        pasta_do_windows = pasta_do_windows.resolve()
    except OSError:
        return FRASE_NAO_LI_O_PROGRAMA
    if caminho.is_relative_to(pasta_do_windows):
        return FRASE_TEM_FUNCAO_PROPRIA
    return _por_que_nao_e_programa(caminho)


def _programa_com_funcao_propria(programa: str) -> bool:
    """A regra única (`_por_que_recusa`) em sim ou não: o programa é recusado pelo rodar genérico, pelo lançar solto e
    pelo grupo? (O nome ficou por causa de quem já o chama: os testes e as conferências de quem tenta quebrar.)"""
    return _por_que_recusa(programa) is not None


def _recusa_de_programa(programa: str, motivo: str | None = None) -> Resposta:
    """A resposta para quem pede ao rodar, ao lançar ou ao grupo um programa que a regra única recusa, com a frase do
    motivo (de fábrica, a de "tem função própria", para o pedido vazio)."""
    return _falhou(motivo or FRASE_TEM_FUNCAO_PROPRIA,
                   f"{programa} recusado pelo rodar genérico (ver \"A PEÇA É FECHADA\" em core/windows.py)")


def rodar_e_esperar(comando: list, limite_s: float = 120, entrada: bytes | None = None,
                    letras: str = "oem") -> Resposta:
    """Roda um programa sem janela, espera ele terminar (com limite) e lê a resposta. RECUSA os programas que têm
    função própria na peça (`PROGRAMAS_COM_FUNCAO_PROPRIA`; ver "A PEÇA É FECHADA" no topo).

    `letras`: a tabela de letras da resposta. Os programas de console do Windows escrevem na tabela OEM do console
    ("oem"); o Python escreve em UTF-8 ("utf-8"). Deu certo = código de saída 0.
    `dados`: `codigo`, `saida` (o que o programa escreveu como resposta) e `erros` (o que escreveu como erro), separados
    e já com as letras certas."""
    motivo = _por_que_recusa(str(comando[0])) if comando else FRASE_TEM_FUNCAO_PROPRIA
    if motivo:
        return _recusa_de_programa(str(comando[0]) if comando else "(nada)", motivo)
    return _rodar(comando, limite_s, entrada, letras)


def _rodar(comando: list, limite_s: float = 120, entrada: bytes | None = None, letras: str = "oem",
           ambiente: dict[str, str] | None = None) -> Resposta:
    """O rodar sem filtro, só de dentro da peça (as funções próprias de cada ferramenta usam este). `ambiente`: o do
    PowerShell (`_ambiente_do_powershell`) quando o programa é ele; None = o deste processo."""
    comando = [str(c) for c in comando]
    extra = {"input": entrada} if entrada is not None else {"stdin": subprocess.DEVNULL}
    try:
        feito = subprocess.run(comando, capture_output=True, timeout=limite_s, creationflags=CREATE_NO_WINDOW,
                               env=ambiente, **extra)
    except subprocess.TimeoutExpired:
        return _falhou(f"o Windows não terminou em {int(limite_s)} segundos", f"tempo esgotado: {comando[0]}")
    except FileNotFoundError as erro:
        return _falhou("não achei o programa a rodar", f"{comando[0]}: {erro}")
    except OSError as erro:
        return _falhou("o Windows não deixou rodar o programa", f"{comando[0]}: {erro!r}")
    saida = feito.stdout.decode(letras, "replace").strip()
    erros = feito.stderr.decode(letras, "replace").strip()
    if feito.returncode == 0:
        return _certo(codigo=0, saida=saida, erros=erros)
    return _falhou("o Windows respondeu com erro", (f"código {feito.returncode}\n" + erros + "\n" + saida).strip(),
                   codigo=feito.returncode, saida=saida, erros=erros)


# ---------------------------------------------------------------------------------------------------------------------
# Rodar um programa num grupo do Windows (job): fechar ele fecha também o que ele abriu (passo 2, achado 2 de quem
# tentou quebrar: a vigia do espaço fechava o vpk e deixava o cmd.exe e o wix.exe que ele abre escrevendo no C:)
# ---------------------------------------------------------------------------------------------------------------------

_JOB_LIMITES_ESTENDIDOS = 9                 # JobObjectExtendedLimitInformation
_JOB_CONTAS_BASICAS = 1                     # JobObjectBasicAccountingInformation
_JOB_FECHA_TUDO_AO_FECHAR = 0x2000          # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
# PROCESS_SET_QUOTA | PROCESS_TERMINATE | SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION (este, para o IsProcessInJob
# conferir que ele entrou: sem ele, o Windows responde "acesso negado", erro 5)
_PODE_POR_NO_GRUPO_E_FECHAR = 0x0100 | 0x0001 | 0x00100000 | 0x1000
_ABRIR_PARADO = 0x00000004                  # CREATE_SUSPENDED (process-creation-flags)
_PODE_SOLTAR_A_LINHA = 0x0002               # THREAD_SUSPEND_RESUME
_FOTO_DAS_LINHAS = 0x00000004               # TH32CS_SNAPTHREAD (CreateToolhelp32Snapshot)
_ALCA_INVALIDA = ctypes.c_void_p(-1).value  # INVALID_HANDLE_VALUE
_RESUME_FALHOU = 0xFFFFFFFF                 # (DWORD)-1, o ResumeThread que falhou


class ProgramaEmGrupo:
    """Um programa aberto por `abrir_em_grupo`, num grupo do Windows só dele, junto com tudo o que ele abrir.

    Lido na Microsoft (Learn, "Job Objects" e "AssignProcessToJobObject"): depois que um processo entra num grupo, os
    processos que ele cria entram no mesmo grupo; `TerminateJobObject` fecha todos os processos do grupo; com
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, fechar a última alça do grupo fecha todos (assim, se este programa cair, o
    grupo não fica rodando sozinho); grupos dentro de grupos valem desde o Windows 8 (o Python dos testes do GitHub já
    roda num grupo).
    O programa nasce PARADO e só é solto depois de estar no grupo (`abrir_em_grupo`; passo 2, volta 3, achado 4 do
    relatório 2 de quem tentou quebrar: antes, no instante entre abrir e pôr no grupo, um filho escapava, e o
    `fechar_tudo` dizia "conferido" com ele vivo). Assim nada do que ele abre pelo CreateProcess fica fora do grupo. O
    que fica fora, pela documentação ("Job Objects"): o que se cria pelo Win32_Process.Create (o WMI), que o vpk não
    usa; e quem sair do grupo com a bandeira de sair, que este grupo não permite (o pedido falha).
    Usar sempre com `with` (ou `soltar()` no fim). Seguro mexer: as frases. Arriscado: tirar o fechar-ao-fechar; abrir
    sem ser parado (o instante volta)."""

    def __init__(self, processo: subprocess.Popen, grupo: int):
        """Guarda o processo e a alça do grupo (quem cria é `abrir_em_grupo`). `saida` e `erros`: o que o programa
        escreveu, quando aberto com a saída guardada (`capturar`), lido por `esperar` (bytes)."""
        self.processo = processo
        self._grupo = grupo
        self.saida = b""
        self.erros = b""

    @property
    def pid(self) -> int:
        """O número do processo principal."""
        return self.processo.pid

    def esperar(self, limite_s: float) -> int | None:
        """Espera o programa principal terminar, no máximo `limite_s`: o código de saída, ou None se ainda roda. Com a
        saída guardada, espera lendo (o `communicate` do Python: "Catching this exception and retrying communication
        will not lose any output"; esperar sem ler pode travar quando o programa escreve muito) e guarda o lido."""
        try:
            if self.processo.stdout is not None:
                saida, erros = self.processo.communicate(timeout=limite_s)
                self.saida, self.erros = saida or b"", erros or b""
                return self.processo.returncode
            return self.processo.wait(timeout=limite_s)
        except subprocess.TimeoutExpired:
            return None

    def vivos(self) -> int | None:
        """Quantos processos do grupo estão vivos agora, lido do Windows (None se não deu para ler)."""
        contas = _JOB_CONTAS()
        if not self._grupo or not _win().kernel32.QueryInformationJobObject(
                self._grupo, _JOB_CONTAS_BASICAS, ctypes.byref(contas), ctypes.sizeof(contas), None):
            return None
        return int(contas.ActiveProcesses)

    def fechar_tudo(self, espera_s: float = 15) -> Resposta:
        """Fecha o programa e tudo o que ele abriu, e CONFERE no Windows que nada do grupo ficou vivo.

        A frase "conferido" só sai quando a leitura do grupo diz 0 vivos (lido do Windows, `vivos`), nunca pelo pedido
        de fechar. Sem leitura do grupo (o Windows não respondeu), a frase diz "não deu para conferir", nunca "algum
        continua rodando" (achado 9 do relatório 2). Antes de soltar o grupo: quem chama decide com esta resposta."""
        w = _win()
        if not self._grupo:
            return _falhou("não deu para conferir se o programa e o que ele abriu fecharam: o grupo já foi solto")
        if not w.kernel32.TerminateJobObject(self._grupo, 1):
            erro = _ler_erro()
            self.processo.kill()
            return _falhou("não consegui fechar os programas do grupo (fechei só o programa principal; não deu para "
                           "conferir o resto)", f"TerminateJobObject: erro {erro}")
        try:
            self.processo.wait(timeout=espera_s)
        except subprocess.TimeoutExpired:
            pass
        fim = time.monotonic() + espera_s
        lido = self.vivos()
        while lido != 0 and time.monotonic() < fim:
            time.sleep(0.2)
            lido = self.vivos()
        if lido == 0:
            return _certo("fechados o programa e tudo o que ele abriu (conferido no Windows: nenhum vivo no grupo)")
        if lido is None:
            return _falhou("pedi para fechar o programa e o que ele abriu, e não deu para conferir (o Windows não "
                           "respondeu à leitura do grupo)", f"QueryInformationJobObject: erro {_ler_erro()}")
        return _falhou(f"pedi para fechar o programa e o que ele abriu, e {lido} continua(m) rodando",
                       f"vivos no grupo: {lido}")

    def soltar(self) -> None:
        """Fecha a alça do grupo (o que ainda estiver vivo nele é fechado pelo Windows: fechar-ao-fechar)."""
        if self._grupo:
            _win().kernel32.CloseHandle(self._grupo)
            self._grupo = 0

    def __enter__(self) -> "ProgramaEmGrupo":
        """Para usar com `with`."""
        return self

    def __exit__(self, *_erro) -> None:
        """No fim do `with`, solta o grupo (o que ficou vivo nele é fechado)."""
        self.soltar()


def _soltar_o_programa_parado(pid: int) -> tuple[bool, str]:
    """Solta (ResumeThread) a linha principal de um programa aberto PARADO. Devolve (soltou?, o técnico).

    O subprocess do Python fecha a alça da linha principal logo depois de abrir (Lib/subprocess.py, `_execute_child`:
    `_winapi.CloseHandle(ht)`) e não guarda o número dela; então ela é achada pela foto das linhas do Windows
    (CreateToolhelp32Snapshot com TH32CS_SNAPTHREAD, Thread32First/Next: as linhas com th32OwnerProcessID = pid). Um
    programa aberto parado só tem a linha principal (as outras nascem quando ele roda). Soltou = o ResumeThread de
    cada linha achada devolveu 1 ou mais (estava parada e agora roda). Lido na Microsoft: CreateProcess, flag
    CREATE_SUSPENDED: "The primary thread of the new process is created in a suspended state, and does not run until
    the ResumeThread function is called"; ResumeThread devolve a contagem de parada anterior, ou (DWORD)-1 se falhou."""
    k = _win().kernel32
    foto = k.CreateToolhelp32Snapshot(_FOTO_DAS_LINHAS, 0)
    if not foto or foto == _ALCA_INVALIDA:
        return False, f"CreateToolhelp32Snapshot: erro {_ler_erro()}"
    linhas: list[int] = []
    try:
        linha = _THREADENTRY32()
        linha.dwSize = ctypes.sizeof(linha)
        existe = k.Thread32First(foto, ctypes.byref(linha))
        while existe:
            if linha.th32OwnerProcessID == pid:
                linhas.append(int(linha.th32ThreadID))
            existe = k.Thread32Next(foto, ctypes.byref(linha))
    finally:
        k.CloseHandle(foto)
    if not linhas:
        return False, f"nenhuma linha do processo {pid} na foto do Windows"
    for numero in linhas:
        alca = k.OpenThread(_PODE_SOLTAR_A_LINHA, False, numero)
        if not alca:
            return False, f"OpenThread {numero}: erro {_ler_erro()}"
        try:
            antes = k.ResumeThread(alca)
            erro = _ler_erro()
        finally:
            k.CloseHandle(alca)
        if antes == _RESUME_FALHOU or antes < 1:
            return False, f"ResumeThread {numero}: devolveu {antes} (erro {erro})"
    return True, f"{len(linhas)} linha(s) soltas"


def abrir_em_grupo(comando: list, pasta: Path | str | None = None,
                   ambiente: dict[str, str] | None = None,
                   capturar: bool = False) -> tuple[ProgramaEmGrupo | None, Resposta]:
    """Abre um programa (com a janela de console de quem chama, para a saída dele aparecer) num grupo do Windows só
    dele. Devolve (o programa, DEU_CERTO) ou (None, FALHOU com o motivo). RECUSA os programas que têm função própria
    na peça (como o rodar genérico, pela mesma regra: `_por_que_recusa`). Quem usa: `rodar_em_grupo` (o laço único,
    que o `empacotar.rodar_vpk` e o gh do publicar usam). `capturar`: a saída e os erros do programa são guardados (lidos
    por `ProgramaEmGrupo.esperar`) em vez de aparecerem no console.

    Em ordem: cria o grupo (fechar-ao-fechar); abre o programa PARADO (CREATE_SUSPENDED); põe no grupo; CONFERE no
    Windows que ele está no grupo (IsProcessInJob); e só então o solta. Qualquer passo que falha fecha o que abriu e
    devolve FALHOU (nada fica rodando fora do grupo). Passo 2, volta 3 (achado 4 do relatório 2): antes ele nascia
    rodando e era posto no grupo depois; um filho aberto nesse instante ficava de fora.
    Observação para o passo 3 (achado 10 do relatório 2): o programa herda o console de quem chama. Chamado do programa
    do Kaique (sem console), o Windows criaria uma janela preta nova para um programa de console. Ver o ONDE-PAREI do
    passo 2."""
    motivo = _por_que_recusa(str(comando[0])) if comando else FRASE_TEM_FUNCAO_PROPRIA
    if motivo:
        return None, _recusa_de_programa(str(comando[0]) if comando else "(nada)", motivo)
    w = _win()
    grupo = w.kernel32.CreateJobObjectW(None, None)
    if not grupo:
        return None, _falhou("o Windows não deixou criar o grupo do programa", f"CreateJobObjectW: erro {_ler_erro()}")
    info = _JOB_EXTENDED()
    info.BasicLimitInformation.LimitFlags = _JOB_FECHA_TUDO_AO_FECHAR
    if not w.kernel32.SetInformationJobObject(grupo, _JOB_LIMITES_ESTENDIDOS, ctypes.byref(info), ctypes.sizeof(info)):
        erro = _ler_erro()
        w.kernel32.CloseHandle(grupo)
        return None, _falhou("o Windows não deixou preparar o grupo do programa", f"SetInformationJobObject: {erro}")
    try:
        guardar = subprocess.PIPE if capturar else None
        processo = subprocess.Popen([str(c) for c in comando], cwd=str(pasta) if pasta else None, env=ambiente,
                                    stdout=guardar, stderr=guardar, creationflags=_ABRIR_PARADO)
    except OSError as erro:
        w.kernel32.CloseHandle(grupo)
        return None, _falhou("não consegui abrir o programa", f"{comando[0]}: {erro!r}")

    def desistir(motivo: str, tecnico: str) -> tuple[None, Resposta]:
        """Fecha o programa (parado ou já no grupo) e o grupo, e devolve FALHOU."""
        w.kernel32.TerminateJobObject(grupo, 1)
        processo.kill()
        try:
            processo.wait(timeout=15)
        except subprocess.TimeoutExpired:
            tecnico += "; o programa não fechou em 15 s"
        w.kernel32.CloseHandle(grupo)
        return None, _falhou(motivo, tecnico)

    alca = w.kernel32.OpenProcess(_PODE_POR_NO_GRUPO_E_FECHAR, False, processo.pid)
    posto = bool(alca) and bool(w.kernel32.AssignProcessToJobObject(grupo, alca))
    erro = _ler_erro()
    dentro = wintypes.BOOL()
    conferido = posto and bool(w.kernel32.IsProcessInJob(alca, grupo, ctypes.byref(dentro))) and bool(dentro.value)
    erro_da_conferencia = _ler_erro()
    if alca:
        w.kernel32.CloseHandle(alca)
    if not posto:
        return desistir("o Windows não deixou pôr o programa no grupo (ele foi fechado antes de começar)",
                        f"AssignProcessToJobObject: erro {erro}")
    if not conferido:
        return desistir("o Windows não confirmou o programa no grupo (ele foi fechado antes de começar)",
                        f"IsProcessInJob: erro {erro_da_conferencia}")
    soltou, tecnico = _soltar_o_programa_parado(processo.pid)
    if not soltou:
        return desistir("não consegui soltar o programa depois de pô-lo no grupo (ele foi fechado)", tecnico)
    return ProgramaEmGrupo(processo, grupo), _certo()


def rodar_em_grupo(comando: list, *, pasta: Path | str | None = None, ambiente: dict[str, str] | None = None,
                   vigia: Callable[[], str | None] | None = None, limite_s: float | None = None,
                   intervalo_s: float = 2.0, capturar: bool = False, letras: str = "utf-8") -> Resposta:
    """O LAÇO ÚNICO de "rodar um programa de fora, olhar a vigia e fechar" (passo 2, volta 4, achado 8 do relatório 3 de
    quem tentou quebrar, §11.12, ponto 1: o vpk rodava por um laço na peça, num grupo, e o gh do publicar por outro, com
    o subprocess direto, sem grupo, fechando só o gh). Quem usa: `empacotar.rodar_vpk` e
    `publicar_versao_kaique.DestinoGitHub._gh`.

    Abre pelo `abrir_em_grupo` (a mesma recusa; o programa nasce parado e só roda dentro do grupo); a cada
    `intervalo_s`, se o programa não terminou, pergunta à `vigia` (None = continue; senão o motivo de parar) e olha o
    `limite_s`; se é para parar, fecha o grupo inteiro (o programa e tudo o que ele abriu) e CONFERE no Windows que nada
    ficou vivo (`ProgramaEmGrupo.fechar_tudo`). Ctrl+C (ou qualquer erro) no meio: fecha o grupo inteiro e repassa.
    Deu certo = o programa terminou sozinho com o código 0. `dados`:
    - `abriu` (False quando foi recusado ou não abriu: nada rodou);
    - `codigo` (o código de saída; None quando foi fechado);
    - `parou` (o motivo de ter fechado: a vigia ou o tempo; None quando terminou sozinho);
    - `fechado` (só quando fechou: True = conferido que nada ficou vivo) e `fechou` (a frase do fechar);
    - `saida` e `erros` (com `capturar`, já com as `letras`, sem os espaços das pontas; senão vazios).
    Arriscado: esperar sem ler com a saída guardada (o programa trava escrevendo); fechar só o programa principal."""
    programa, aberto = abrir_em_grupo(comando, pasta, ambiente, capturar=capturar)
    if programa is None:
        return _falhou(aberto.motivo, aberto.detalhe, abriu=False, codigo=None, parou=None, fechado=None, fechou="",
                       saida="", erros="")
    fim = None if limite_s is None else time.monotonic() + limite_s

    def lido() -> dict:
        """O que o programa escreveu, com as letras."""
        return {"saida": programa.saida.decode(letras, "replace").strip(),
                "erros": programa.erros.decode(letras, "replace").strip()}

    with programa:
        try:
            while True:
                codigo = programa.esperar(intervalo_s)
                if codigo is not None:
                    break
                motivo = vigia() if vigia is not None else None
                if not motivo and fim is not None and time.monotonic() > fim:
                    motivo = f"o programa não terminou em {int(limite_s)} segundos"
                if motivo:
                    fechado = programa.fechar_tudo()
                    if capturar:
                        programa.esperar(5)                      # junta o que ele escreveu antes de fechar
                    return _falhou(motivo, f"{comando[0]}: {fechado.motivo}", abriu=True, codigo=None, parou=motivo,
                                   fechado=fechado.deu_certo, fechou=fechado.motivo, **lido())
        except BaseException:
            programa.fechar_tudo()
            raise
    if codigo == 0:
        return _certo(abriu=True, codigo=0, parou=None, fechado=None, fechou="", **lido())
    return _falhou(f"o programa saiu com o código {codigo}", f"{comando[0]}: código {codigo}", abriu=True,
                   codigo=codigo, parou=None, fechado=None, fechou="", **lido())


def rodar_powershell(texto: str, limite_s: float = 600, segredo: str | None = None) -> Resposta:
    """Roda um script do PowerShell (pelo caminho inteiro, em arquivo com a marca de UTF-8, numa pasta de troca que é
    apagada no fim) e espera.

    O script recebe na frente: parar no primeiro erro e ler/escrever em UTF-8. Se `segredo` vier, ele chega pela
    entrada do script (nunca pela linha de comando, que outros programas veem), em UTF-8, numa linha: o script lê com
    `[Console]::In.ReadLine()`. A resposta (`dados["saida"]`) é só o que o script escreveu como resposta; o que ele
    escreveu como erro fica em `dados["erros"]`. Programa de fora que o script chama e falha não para o PowerShell
    sozinho: o script confere com `Confere-Comando 'o que era'` logo depois dele, e o fim de todo script dá "falhou"
    se o último programa de fora falhou."""
    try:
        pasta = criar_pasta_de_troca()
    except OSError as erro:
        return _falhou("não consegui preparar o script (o disco está cheio ou sem licença?)", repr(erro))
    try:
        script = pasta / "script.ps1"
        _gravar_script(script, _CABECA_DO_SCRIPT + texto + _PE_DO_SCRIPT)
        entrada = (segredo + "\n").encode("utf-8") if segredo is not None else None
        return _rodar(_comando_do_powershell(script), limite_s, entrada, "utf-8-sig", _ambiente_do_powershell())
    except (OSError, ValueError) as erro:
        return _falhou("não consegui rodar o script", repr(erro))
    finally:
        apagar_pasta_de_troca(pasta)


# ---------------------------------------------------------------------------------------------------------------------
# Lançar solto (o processo que continua depois de quem lançou fechar)
# ---------------------------------------------------------------------------------------------------------------------

def _situacao_do_grupo() -> str:
    """Este processo está preso a um grupo de processos (job) do Windows, e o que acontece com um filho?

    "fora" (não está), "solta_sozinho" (o grupo já solta os filhos), "pode_soltar" (o grupo deixa soltar com a
    bandeira), "fica_e_vive" (o filho fica no grupo, mas o grupo não mata ninguém ao fechar), "morre_junto" (o filho
    ficaria preso e morreria quando o grupo fechasse) ou "nao_sei" (o Windows não deixou ler o grupo)."""
    w = _win()
    dentro = wintypes.BOOL()
    if not w.kernel32.IsProcessInJob(w.kernel32.GetCurrentProcess(), None, ctypes.byref(dentro)):
        return "nao_sei"
    if not dentro.value:
        return "fora"
    info = _JOB_EXTENDED()
    if not w.kernel32.QueryInformationJobObject(None, 9, ctypes.byref(info), ctypes.sizeof(info), None):
        return "nao_sei"
    bandeiras = info.BasicLimitInformation.LimitFlags
    if bandeiras & 0x1000:          # JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK
        return "solta_sozinho"
    if bandeiras & 0x800:           # JOB_OBJECT_LIMIT_BREAKAWAY_OK
        return "pode_soltar"
    if bandeiras & 0x2000:          # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        return "morre_junto"
    return "fica_e_vive"


def lancar_solto(comando: list, sinal: Path, espera_s: float = 30) -> Resposta:
    """Lança um processo que continua rodando depois que este fecha, e espera o sinal de vida dele.

    O processo lançado tem de criar o arquivo `sinal` logo que começa. Sem o sinal em `espera_s` segundos, a peça
    fecha o lançado e diz "falhou" (nada fica rodando pela metade). Sem console e num grupo novo; NUNCA com a bandeira
    de processo sem console (o porteiro barra: o PowerShell lançado assim saía sem rodar). Se este processo estiver
    preso a um grupo que mataria o lançado ao fechar, não lança e diz "falhou". RECUSA os programas que têm função
    própria na peça (o PowerShell vai por `lancar_powershell_solto`; ver "A PEÇA É FECHADA" no topo).
    `dados`: `pid` e `grupo` (a situação do grupo)."""
    motivo = _por_que_recusa(str(comando[0])) if comando else FRASE_TEM_FUNCAO_PROPRIA
    if motivo:
        return _recusa_de_programa(str(comando[0]) if comando else "(nada)", motivo)
    return _lancar_solto(comando, sinal, espera_s)


def _lancar_solto(comando: list, sinal: Path, espera_s: float, ambiente: dict[str, str] | None = None) -> Resposta:
    """O lançar solto sem filtro, só de dentro da peça (`lancar_powershell_solto` usa este). `ambiente`: como em
    `_rodar`."""
    comando = [str(c) for c in comando]
    try:
        grupo = _situacao_do_grupo()
    except OSError as erro:
        return _falhou("não deu para lançar o processo", repr(erro))
    if grupo == "morre_junto":
        return _falhou("não deu para soltar o processo: ele fecharia junto com este", "grupo do Windows (job) "
                       "fecha os filhos e não deixa soltar", grupo=grupo)
    bandeiras = CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
    if grupo in ("pode_soltar", "nao_sei"):
        bandeiras |= CREATE_BREAKAWAY_FROM_JOB
    try:
        processo = subprocess.Popen(comando, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, close_fds=True, creationflags=bandeiras, env=ambiente)
    except OSError as erro:
        return _falhou("o Windows não deixou lançar o processo", f"{comando[0]}: {erro!r} (grupo: {grupo})",
                       grupo=grupo)
    fim = time.monotonic() + espera_s
    while time.monotonic() < fim:
        if Path(sinal).exists():
            return _certo(pid=processo.pid, grupo=grupo)
        if processo.poll() is not None:
            break
        time.sleep(0.1)
    if Path(sinal).exists():
        return _certo(pid=processo.pid, grupo=grupo)
    if processo.poll() is None:
        processo.kill()
        try:
            processo.wait(5)
        except subprocess.TimeoutExpired:
            pass
        return _falhou(f"o processo lançado não deu sinal de vida em {int(espera_s)} segundos (foi fechado)",
                       comando[0], grupo=grupo)
    return _falhou("o processo lançado saiu sem começar", f"{comando[0]}: código {processo.returncode}", grupo=grupo,
                   codigo=processo.returncode)


# O apagar do fim do script lançado solto (D-809, Samuel 19/11: "ok"; conferência K25 do porteiro). Cada item é
# conferido antes: atalho (junção ou link) sai SÓ ele (DirectoryInfo/FileInfo.Delete chama o RemoveDirectory/DeleteFile
# do Windows, que tira a junção sem tocar no que está do outro lado: Microsoft Learn, RemoveDirectoryW, "RemoveDirectory
# removes a directory junction, even if the contents of the target are not empty"); pasta comum, primeiro o que tem
# dentro, um por um; arquivo, apagado. Nunca o apagar recursivo do PowerShell (a Microsoft avisa do "known issue" do
# -Recurse no Remove-Item; e foi um apagar que passou por uma junção que esvaziou a pasta modelos/ em 18/11).
# Arriscado: trocar por um apagar recursivo; tirar a conferência do atalho.
_APAGAR_SEM_SEGUIR_ATALHO = (
    "function Apagar-SemSeguirAtalho([string]$caminho) {\n"
    "  $item = Get-Item -LiteralPath $caminho -Force -ErrorAction SilentlyContinue\n"
    "  if ($null -eq $item) { return }\n"
    "  if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) { $item.Delete(); return }\n"
    "  if ($item.PSIsContainer) {\n"
    "    foreach ($filho in @(Get-ChildItem -LiteralPath $caminho -Force -ErrorAction SilentlyContinue)) {\n"
    "      Apagar-SemSeguirAtalho $filho.FullName\n"
    "    }\n"
    "  }\n"
    "  $item.Delete()\n"
    "}\n"
)


def lancar_powershell_solto(texto: str, espera_s: float = 30) -> Resposta:
    """Lança solto um script do PowerShell (em arquivo com a marca de UTF-8, numa pasta de troca) e espera o sinal de
    vida. O script dá o sinal na primeira linha e apaga a própria pasta de troca no fim, deu certo ou não, sem seguir
    atalho (`_APAGAR_SEM_SEGUIR_ATALHO`, D-809).

    O sinal de vida fica numa SEGUNDA pasta de troca, que o script não apaga: só a peça, depois de ver o sinal (ou de
    desistir). Antes ele ficava na pasta que o script apaga no fim, e um script curto apagava o sinal antes de a peça
    olhar: "saiu sem começar" de uma coisa que rodou (bug de 19/11, 12 de 20 vezes com um script vazio). Se este
    processo cair antes, a pasta do sinal é limpa pela limpeza das trocas velhas (`_limpar_trocas_velhas`).
    Se a segunda pasta não nasce, a primeira é apagada na hora (volta 3, achado 9 do relatório 2: antes ficava para a
    limpeza do dia seguinte)."""
    try:
        pasta = criar_pasta_de_troca()
    except OSError as erro:
        return _falhou("não consegui preparar o script (o disco está cheio ou sem licença?)", repr(erro))
    try:
        pasta_do_sinal = criar_pasta_de_troca()
    except OSError as erro:
        apagar_pasta_de_troca(pasta)
        return _falhou("não consegui preparar o script (o disco está cheio ou sem licença?)", repr(erro))
    sinal = pasta_do_sinal / "comecei.txt"
    script = pasta / "solto.ps1"
    try:
        try:
            _gravar_script(script, _CABECA_DO_SCRIPT + _APAGAR_SEM_SEGUIR_ATALHO
                           + f"[System.IO.File]::WriteAllText({aspas_do_powershell(sinal)}, 'comecei')\n"
                           + "try {\n" + texto + "\n} finally {\n"
                           + f"  try {{ Apagar-SemSeguirAtalho {aspas_do_powershell(pasta)} }} catch {{ }}\n"
                           + "}\n")
        except (OSError, ValueError) as erro:
            apagar_pasta_de_troca(pasta)
            return _falhou("não consegui preparar o script", repr(erro))
        resposta = _lancar_solto(_comando_do_powershell(script), sinal, espera_s, _ambiente_do_powershell())
        if not resposta.deu_certo:
            apagar_pasta_de_troca(pasta)
        return resposta
    finally:
        apagar_pasta_de_troca(pasta_do_sinal)


# ---------------------------------------------------------------------------------------------------------------------
# A assinatura digital de um arquivo: só ler (passo 2 do plano; antes o empacotar abria o PowerShell por conta própria)
# ---------------------------------------------------------------------------------------------------------------------

_SCRIPT_DA_ASSINATURA = (
    "$arquivo = {arquivo}\n"
    "$s = Get-AuthenticodeSignature -LiteralPath $arquivo\n"
    "$v = (Get-Item -LiteralPath $arquivo).VersionInfo\n"
    "[Console]::Out.Write(([pscustomobject]@{{status=[string]$s.Status; "
    "assinante=[string]$s.SignerCertificate.Subject; produto=[string]$v.ProductName; "
    "versao=[string]$v.FileVersion}} | ConvertTo-Json -Compress))\n"
)


def ler_assinatura_digital(arquivo: Path | str, limite_s: float = 120) -> Resposta:
    """A assinatura digital (Authenticode) de um arquivo, lida pelo próprio Windows, sem licença e sem pergunta.

    DEU_CERTO quer dizer só que o Windows LEU: `dados` traz `status` (o estado do Windows: "Valid", "NotSigned",
    "HashMismatch", "NotTrusted", "UnknownError", "NotSupportedFileFormat" ou "Incompatible"; Microsoft Learn,
    SignatureStatus), `assinante` (o certificado de quem assinou, vazio sem assinatura), `produto` e `versao` (do
    arquivo). "Valid" não diz quem assinou: quem chama confere o assinante (ex.: `empacotar.vc_redist_confere`).
    FALHOU quando o Windows não conseguiu ler (o arquivo não existe, sem licença de leitura, o PowerShell não terminou):
    nunca um estado inventado.

    Roda pelo `rodar_powershell` da peça (o caminho inteiro do PowerShell do Windows, o script em arquivo com a marca
    de UTF-8). O caminho vai entre aspas do PowerShell, numa linha (`aspas_do_powershell` recusa quebra de linha).
    Seguro mexer: as frases. Arriscado: tirar o `-LiteralPath` (colchetes no nome viram curinga)."""
    try:
        texto = _SCRIPT_DA_ASSINATURA.format(arquivo=aspas_do_powershell(str(arquivo)))
    except ValueError as erro:
        return _falhou("o nome do arquivo não serve para ler a assinatura", repr(erro))
    r = rodar_powershell(texto, limite_s=limite_s)
    if not r.deu_certo:
        return _falhou("o Windows não conseguiu ler a assinatura digital do arquivo", f"{arquivo}: {r.detalhe}")
    try:
        lido = json.loads(r.dados.get("saida") or "")
    except ValueError as erro:
        return _falhou("o Windows respondeu algo que o programa não entendeu", f"{arquivo}: {erro!r}: {r.dados}")
    if not isinstance(lido, dict) or not isinstance(lido.get("status"), str):
        return _falhou("o Windows respondeu algo que o programa não entendeu", f"{arquivo}: {lido!r}")
    return _certo(status=lido["status"], assinante=str(lido.get("assinante") or ""),
                  produto=str(lido.get("produto") or ""), versao=str(lido.get("versao") or ""))


# ---------------------------------------------------------------------------------------------------------------------
# Marcas (os "mutex" do Windows): só ler
# ---------------------------------------------------------------------------------------------------------------------

def marca_existe(nome: str) -> bool | None:
    """A marca `nome` existe agora (algum processo a segura)? True, False, ou None (não deu para saber).

    "Acesso negado" quer dizer que ela EXISTE (de outra conta ou com licença maior), nunca que não existe."""
    w = _win()
    alca = w.kernel32.OpenMutexW(0x00100000, False, nome)          # SYNCHRONIZE
    if alca:
        w.kernel32.CloseHandle(alca)
        return True
    erro = _ler_erro()
    if erro == ERRO_ACESSO_NEGADO:
        return True
    if erro == ERRO_ARQUIVO_NAO_ACHADO:
        return False
    return None


# ---------------------------------------------------------------------------------------------------------------------
# Os programas que rodam de dentro de uma pasta: só ler (volta 4 do atualizador, 22/11/2026; atualizador novo, 23/11)
# ---------------------------------------------------------------------------------------------------------------------

_TODOS_OS_PROCESSOS = 0x00000002                # TH32CS_SNAPPROCESS
_SO_PERGUNTAR_O_CAMINHO = 0x1000                # PROCESS_QUERY_LIMITED_INFORMATION
_A_LISTA_ACABOU = 18                            # ERROR_NO_MORE_FILES


def _dentro_de(caminho: str, pastas: tuple[str, ...]) -> bool:
    """O arquivo `caminho` está dentro de uma das `pastas` (já normalizadas por `os.path.normcase(normpath)`)?"""
    c = os.path.normcase(os.path.normpath(caminho))
    return any(c.startswith(p + os.sep) for p in pastas)


def familia_de(pid: int, pais: dict[int, int]) -> set[int]:
    """`pid` e todos os processos que ele abriu, e os que esses abriram (pela tabela processo -> quem o abriu, como o
    Windows a dá). Lugar único da conta. Um número de quem abriu que já não existe não liga nada a ninguém."""
    familia, mudou = {int(pid)}, True
    while mudou:
        mudou = False
        for filho, pai in pais.items():
            if pai in familia and filho not in familia and filho != pai:
                familia.add(filho)
                mudou = True
    return familia


def programas_rodando_de(pasta: Path | str, menos_a_familia_de: int | None = None) -> list[tuple[int, str]] | None:
    """Os processos cujo programa está dentro de `pasta` (em qualquer conta), lidos agora no Windows: [(número,
    caminho)], [] se nenhum, None se o Windows não deu a lista. `menos_a_familia_de`: deixa de fora esse processo e os
    que ele abriu (o servidor de páginas, o brasão): para o atualizador saber se há OUTRA janela do programa aberta.

    É a mesma pergunta que o Velopack faz antes de fechar à força o que roda na pasta dele (util_windows.rs,
    `get_processes_running_in_directory`: o caminho de cada processo pelo `QueryFullProcessImageNameW`), feita ANTES,
    para o atualizador não pedir a troca com outra janela do programa aberta (o Velopack a fecharia à força, com o que
    estivesse nela). Como: a lista do Windows (`CreateToolhelp32Snapshot`) dá o número, o número de quem o abriu e o
    nome de cada processo sem abri-lo; o caminho vem de `OpenProcess` só para perguntar
    (`PROCESS_QUERY_LIMITED_INFORMATION`) e `QueryFullProcessImageNameW`. Um processo cujo caminho não deu para ler
    (outra conta sem licença, um processo protegido do Windows) conta como de dentro se o NOME dele é o de um programa
    (.exe) que está na pasta: nunca se dá como fechado o que não deu para conferir. Só lê; não fecha nada.
    Seguro mexer: as frases. Arriscado: comparar só pelo nome (outro programa com o mesmo nome contaria) ou só pelo
    caminho (o processo que não deixa ler o caminho sumiria da conta)."""
    w = _win()
    pastas = tuple({os.path.normcase(os.path.normpath(str(pasta))),
                    os.path.normcase(os.path.normpath(os.path.realpath(str(pasta))))})
    try:
        nomes = {p.name.lower() for p in Path(pasta).rglob("*.exe")}
    except OSError:
        nomes = set()
    lista = w.kernel32.CreateToolhelp32Snapshot(_TODOS_OS_PROCESSOS, 0)
    if not lista or lista == _ALCA_INVALIDA:
        return None
    lidos: list[tuple[int, int, str]] = []
    try:
        linha = _PROCESSENTRY32W()
        linha.dwSize = ctypes.sizeof(linha)
        if not w.kernel32.Process32FirstW(lista, ctypes.byref(linha)):
            return None
        while True:
            lidos.append((int(linha.th32ProcessID), int(linha.th32ParentProcessID), str(linha.szExeFile)))
            if not w.kernel32.Process32NextW(lista, ctypes.byref(linha)):
                if _ler_erro() != _A_LISTA_ACABOU:      # outro erro: a lista veio cortada
                    return None
                break
    finally:
        w.kernel32.CloseHandle(lista)
    fora = familia_de(menos_a_familia_de, {pid: pai for pid, pai, _ in lidos}) if menos_a_familia_de else set()
    achados: list[tuple[int, str]] = []
    for pid, _pai, nome in lidos:
        if not pid or pid in fora:
            continue
        caminho = None
        alca = w.kernel32.OpenProcess(_SO_PERGUNTAR_O_CAMINHO, False, pid)
        if alca:
            try:
                buffer = ctypes.create_unicode_buffer(32768)
                tamanho = wintypes.DWORD(len(buffer))
                if w.kernel32.QueryFullProcessImageNameW(alca, 0, buffer, ctypes.byref(tamanho)):
                    caminho = buffer.value
            finally:
                w.kernel32.CloseHandle(alca)
        if caminho is not None:
            if _dentro_de(caminho, pastas):
                achados.append((pid, caminho))
        elif nome.lower() in nomes:
            achados.append((pid, f"{nome} (o caminho não deu para ler)"))
    return achados


def numero_deste_processo() -> int:
    """O número deste processo no Windows."""
    return int(_win().kernel32.GetCurrentProcessId())


# ---------------------------------------------------------------------------------------------------------------------
# O dono de um arquivo, o Visual C++ e a instalação antiga do Inno: só ler (atualizador novo, 23/11/2026; antes eram
# escritos no atualizacao.py, cada um com o seu ctypes e o seu winreg)
# ---------------------------------------------------------------------------------------------------------------------

def dono_do_arquivo(caminho: Path | str) -> str | None:
    """O SID do dono do arquivo ("S-1-5-32-544"...), lido pelo Windows (`ler_licencas`), ou None se não deu para ler."""
    try:
        return ler_licencas(caminho).dono or None
    except OSError:
        return None


# A chave do Visual C++ 2015-2022 x64 (a mesma do instalador.iss, seção [Code], que a Microsoft documenta) e a da
# instalação antiga do Inno Setup (o AppId fixo do instalador.iss; o Windows a guarda em ...\Uninstall\{AppId}_is1).
CHAVE_DO_VISUAL_C = "SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64"
APPID_DO_INNO = "{7C4E1B92-3A5D-4F18-9B6C-2E8A5D0F3C71}"
CHAVE_DO_INNO = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APPID_DO_INNO}_is1"


def ler_versao_do_visual_c() -> tuple[int, int, int] | None:
    """A maior versão do Visual C++ 2015-2022 x64 instalada (as duas vistas do registro), ou None. Só lê."""
    import winreg

    achadas = []
    for vista in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, CHAVE_DO_VISUAL_C, 0, winreg.KEY_READ | vista) as chave:
                if winreg.QueryValueEx(chave, "Installed")[0] != 1:
                    continue
                achadas.append(tuple(int(winreg.QueryValueEx(chave, nome)[0]) for nome in ("Major", "Minor", "Bld")))
        except (OSError, ValueError, TypeError):
            continue
    return max(achadas) if achadas else None


def ler_instalacao_do_inno() -> dict | None:
    """A instalação antiga do Inno Setup (a de 28/10 do Kaique): {"UninstallString", "InstallLocation"} lidos do
    registro, ou None se não há. Só lê."""
    import winreg

    for vista in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, CHAVE_DO_INNO, 0, winreg.KEY_READ | vista) as chave:
                return {nome: winreg.QueryValueEx(chave, nome)[0] for nome in ("UninstallString", "InstallLocation")}
        except OSError:
            continue
    return None


# ---------------------------------------------------------------------------------------------------------------------
# Trazer a janela para a frente
# ---------------------------------------------------------------------------------------------------------------------

def trazer_para_a_frente(janela: int | None) -> bool:
    """Pede ao Windows para trazer a janela para a frente e devolve se ela ESTÁ na frente agora (conferido).

    O Windows não deixa um programa tomar a frente enquanto a pessoa usa outra janela: aí ele pisca o botão na barra
    de tarefas, e esta função devolve False (quem chama diz isso na resposta, não finge)."""
    if not janela:
        return False
    u = _win().user32
    if not u.IsWindow(janela):
        return False
    if u.IsIconic(janela):
        u.ShowWindow(janela, 9)                                        # SW_RESTORE
    u.SetForegroundWindow(janela)
    return u.GetForegroundWindow() == janela


# ---------------------------------------------------------------------------------------------------------------------
# O segredo (ex.: a senha dos testes à distância), numa codificação só dos dois lados
# ---------------------------------------------------------------------------------------------------------------------

def cifrar_segredo(texto: str) -> bytes:
    """Cifra o texto (em UTF-8) pelo próprio Windows, para ESTE computador: qualquer conta deste computador decifra,
    então a proteção de verdade é o arquivo ficar na pasta de troca (só a conta e os administradores leem) e ser
    apagado no fim. Assim abre também quando quem diz "Sim" é outro administrador. Levanta OSError."""
    w = _win()
    dados = texto.encode("utf-8")
    memoria = ctypes.create_string_buffer(dados, len(dados))        # fica viva até o fim da chamada
    origem = _DATA_BLOB(len(dados), ctypes.cast(memoria, ctypes.POINTER(ctypes.c_ubyte)))
    saida = _DATA_BLOB()
    if not w.crypt32.CryptProtectData(ctypes.byref(origem), "Editor de Impressão", None, None, None,
                                      0x1 | 0x4, ctypes.byref(saida)):          # UI_FORBIDDEN | LOCAL_MACHINE
        raise OSError(f"o Windows não cifrou o segredo (erro {_ler_erro()})")
    try:
        return ctypes.string_at(saida.pbData, saida.cbData)
    finally:
        w.kernel32.LocalFree(ctypes.cast(saida.pbData, ctypes.c_void_p))


def decifrar_segredo(cifrado: bytes) -> str:
    """Decifra o que `cifrar_segredo` cifrou e devolve o texto (UTF-8). Levanta OSError."""
    w = _win()
    memoria = ctypes.create_string_buffer(cifrado, len(cifrado))    # fica viva até o fim da chamada
    origem = _DATA_BLOB(len(cifrado), ctypes.cast(memoria, ctypes.POINTER(ctypes.c_ubyte)))
    saida = _DATA_BLOB()
    if not w.crypt32.CryptUnprotectData(ctypes.byref(origem), None, None, None, None, 0x1, ctypes.byref(saida)):
        raise OSError(f"o Windows não decifrou o segredo (erro {_ler_erro()})")
    try:
        return ctypes.string_at(saida.pbData, saida.cbData).decode("utf-8")
    finally:
        w.kernel32.LocalFree(ctypes.cast(saida.pbData, ctypes.c_void_p))


# ---------------------------------------------------------------------------------------------------------------------
# Tarefas do Agendador do Windows
# ---------------------------------------------------------------------------------------------------------------------

_NS_DA_TAREFA = "{http://schemas.microsoft.com/windows/2004/02/mit/task}"


@dataclass(frozen=True)
class Tarefa:
    """O que o Windows diz de uma tarefa: `existe` (True, False ou None = não deu para saber), `lida` (deu para ler
    o conteúdo; "acesso negado" é existe=True e lida=False), o comando, os argumentos, quem roda (`usuario`, o SID)
    e quem pode mandar rodar: `quem_pode` é o que o desenho (XML) declara; `licenca` é o que o Windows diz que vale
    de verdade (lido com `GetSecurityDescriptor`, já com as licenças herdadas da pasta do Agendador)."""

    nome: str
    existe: bool | None
    lida: bool = False
    comando: str = ""
    argumentos: str = ""
    usuario: str = ""
    quem_pode: str = ""
    motivo: str = ""
    licenca: str = ""


def xml_da_tarefa_do_sistema(comando: str, argumentos: str, descricao: str, quem_pode_mandar_rodar: str,
                             limite: str = "PT2H", prioridade: int = 7) -> str:
    """O XML de uma tarefa que roda como o próprio sistema (S-1-5-18), sem hora marcada (só quando alguém manda
    rodar), sem janela, com quem pode mandar rodar dado por `quem_pode_mandar_rodar` (descritor de segurança em texto).

    É o mesmo desenho do ajudante de hoje (`atualizacao.xml_da_tarefa`, que passa a usar esta no passo 3)."""
    from xml.sax.saxutils import escape

    return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>{escape(descricao)}</Description>
    <SecurityDescriptor>{escape(quem_pode_mandar_rodar)}</SecurityDescriptor>
  </RegistrationInfo>
  <Principals>
    <Principal id="Sistema">
      <UserId>{SID_SISTEMA}</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <ExecutionTimeLimit>{escape(limite)}</ExecutionTimeLimit>
    <Priority>{int(prioridade)}</Priority>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Sistema">
    <Exec>
      <Command>{escape(comando)}</Command>
      <Arguments>{escape(argumentos)}</Arguments>
    </Exec>
  </Actions>
</Task>
"""


def xml_da_tarefa_de_script(script: Path, descricao: str, quem_pode_mandar_rodar: str, limite: str = "PT2H") -> str:
    """O desenho de uma tarefa que roda como o sistema um script do PowerShell que está em `script` (com o mesmo
    comando do PowerShell que a peça usa em todo lugar). O script tem de estar numa pasta que só o administrador grava
    (a pasta segura)."""
    return xml_da_tarefa_do_sistema(str(_caminho_do_powershell()), _argumentos_do_powershell(script), descricao,
                                    quem_pode_mandar_rodar, limite)


def ler_xml_da_tarefa(xml: str) -> dict:
    """Do XML de uma tarefa: o comando, os argumentos, quem roda e quem pode mandar rodar (o mesmo leitor para o que
    a peça escreve e para o que o Windows devolve)."""
    import xml.etree.ElementTree as ET

    raiz = ET.fromstring(xml.encode("utf-16"))

    def texto(caminho: str) -> str:
        """O texto do primeiro elemento no caminho, ou ""."""
        achado = raiz.find(_caminho_ns(caminho))
        return (achado.text or "").strip() if achado is not None else ""

    return {"comando": texto("Actions/Exec/Command"), "argumentos": texto("Actions/Exec/Arguments"),
            "usuario": texto("Principals/Principal/UserId"),
            "quem_pode": texto("RegistrationInfo/SecurityDescriptor")}


def _caminho_ns(caminho: str) -> str:
    """'A/B' → '{ns}A/{ns}B' (o XML das tarefas tem um espaço de nomes)."""
    return "/".join(_NS_DA_TAREFA + parte for parte in caminho.split("/"))


def ler_tarefa(nome: str, limite_s: float = 60) -> Tarefa:
    """Pergunta ao Windows (sem licença) se a tarefa existe e o que ela faz. Lê pelo COM do Agendador, que responde
    por número: não existe (0x80070002/3), acesso negado (0x80070005: existe, mas esta conta não lê)."""
    if not _NOME_DE_TAREFA.match(nome):
        return Tarefa(nome, None, motivo="nome de tarefa fora da pasta do programa")
    pasta, _, folha = nome.rpartition("\\")
    resposta = rodar_powershell(
        "$s = New-Object -ComObject Schedule.Service\n$s.Connect()\n"
        f"try {{ $t = $s.GetFolder({aspas_do_powershell(chr(92) + pasta)}).GetTask({aspas_do_powershell(folha)})\n"
        "  $l = ''; try { $l = $t.GetSecurityDescriptor(4) } catch { }\n"
        "  [Console]::Out.Write((@{ codigo = 0; xml = $t.Xml; licenca = $l } | ConvertTo-Json -Compress)) }\n"
        "catch { $h = $_.Exception.HResult; if ($_.Exception.InnerException) { $h = $_.Exception.InnerException.HResult }\n"
        "  [Console]::Out.Write((@{ codigo = $h; xml = '' } | ConvertTo-Json -Compress)) }\n", limite_s)
    if not resposta.deu_certo:
        return Tarefa(nome, None, motivo=resposta.motivo)
    try:
        lido = json.loads(resposta.dados["saida"])
        codigo = int(lido["codigo"]) & 0xFFFFFFFF
    except (ValueError, KeyError, TypeError) as erro:
        return Tarefa(nome, None, motivo=f"resposta do Windows que não deu para ler ({erro})")
    if codigo == 0:
        try:
            campos = ler_xml_da_tarefa(lido["xml"])
        except Exception as erro:  # noqa: BLE001 - XML estranho vira "não deu para ler"
            return Tarefa(nome, True, False, motivo=f"a tarefa existe, mas o conteúdo não deu para ler ({erro!r})")
        return Tarefa(nome, True, True, licenca=str(lido.get("licenca") or ""), **campos)
    if codigo in HRESULT_NAO_EXISTE:
        return Tarefa(nome, False)
    if codigo == HRESULT_ACESSO_NEGADO:
        return Tarefa(nome, True, False, motivo="a tarefa existe, mas esta conta não tem licença para ler")
    _registrar("ler a tarefa", f"{nome}: o Windows respondeu 0x{codigo:08X}")
    return Tarefa(nome, None, motivo="o Windows deu uma resposta que a peça não conhece (anotada no registro)")


def problemas_da_tarefa_criada(pedido: str, lida: Tarefa) -> list[str]:
    """A tarefa lida no Windows é a que foi pedida? Existe e foi lida; o comando, os argumentos e quem roda batem com
    o desenho pedido; e a licença que o Windows diz que vale cumpre a pedida (`problemas_da_licenca_da_tarefa`)."""
    if not lida.existe or not lida.lida:
        return [f"a tarefa não foi achada depois de criada ({lida.motivo or 'não existe'})"]
    esperado = ler_xml_da_tarefa(pedido)
    problemas = [f"{campo} ficou {getattr(lida, campo)!r}, e o pedido era {esperado[campo]!r}"
                 for campo in ("comando", "argumentos", "usuario") if getattr(lida, campo) != esperado[campo]]
    if esperado["quem_pode"]:
        if not lida.licenca:
            problemas.append("não deu para ler a licença da tarefa no Windows")
        else:
            try:
                problemas += problemas_da_licenca_da_tarefa(esperado["quem_pode"], lida.licenca)
            except OSError as erro:
                problemas.append(f"a licença da tarefa não deu para comparar ({erro})")
    return problemas


def criar_tarefa(nome: str, xml: str) -> Resposta:
    """Cria (ou refaz) a tarefa a partir do XML e CONFERE lendo de volta (`problemas_da_tarefa_criada`). Se não
    conferir, apaga a tarefa de novo e confere que sumiu (nada fica pela metade; a resposta diz o que ficou). Precisa da
    licença de administrador (roda dentro do trabalho com licença ou como o sistema)."""
    if not _NOME_DE_TAREFA.match(nome):
        return _falhou("nome de tarefa fora da pasta do programa", nome)
    try:
        ler_xml_da_tarefa(xml)
    except Exception as erro:  # noqa: BLE001
        return _falhou("o desenho da tarefa está errado", repr(erro))
    # A pasta do programa no Agendador: se já existe, tem de ser segura ANTES de pôr a tarefa nela (qualquer conta
    # pode criá-la antes com as licenças que quiser; achado N3 de quem tentou quebrar). Se não existe, o Windows a
    # cria junto com a tarefa, e ela é conferida depois.
    existia = pasta_de_tarefas_existe()
    if existia is not False:
        antes = conferir_pasta_de_tarefas()
        if not antes.deu_certo:
            return _falhou(antes.motivo + " (a tarefa não foi criada)", antes.detalhe)
    try:
        pasta = criar_pasta_de_troca()
    except OSError as erro:
        return _falhou("não consegui preparar a tarefa (o disco está cheio?)", repr(erro))
    try:
        arquivo = pasta / "tarefa.xml"
        _gravar_por_inteiro(arquivo, xml.encode("utf-16"))
        feito = _rodar([_caminho_do_schtasks(), "/Create", "/TN", nome, "/XML", arquivo, "/F"])
    finally:
        apagar_pasta_de_troca(pasta)
    lida = ler_tarefa(nome)
    problemas = problemas_da_tarefa_criada(xml, lida)
    if lida.existe:
        depois = conferir_pasta_de_tarefas()
        if not depois.deu_certo:
            problemas.append(depois.motivo)
    if not problemas:
        return _certo(saida=feito.dados.get("saida", ""))
    tecnico = f"schtasks: {feito.desfecho} {feito.detalhe} {feito.dados.get('saida', '')}; lida: {lida}"
    if lida.existe is False:
        return _falhou("a tarefa não foi criada: " + "; ".join(problemas), tecnico)
    apagada = apagar_tarefa(nome)
    if apagada.deu_certo:
        return _falhou("a tarefa não ficou como pedido e foi apagada de novo: " + "; ".join(problemas), tecnico)
    return _falhou("a tarefa não ficou como pedido e NÃO deu para apagar: ela ficou no Windows: "
                   + "; ".join(problemas), tecnico + f"; apagar: {apagada.motivo} {apagada.detalhe}")


def apagar_tarefa(nome: str) -> Resposta:
    """Apaga a tarefa e CONFERE que ela não existe mais (se já não existia, deu certo). Precisa de administrador."""
    if not _NOME_DE_TAREFA.match(nome):
        return _falhou("nome de tarefa fora da pasta do programa", nome)
    antes = ler_tarefa(nome)
    if antes.existe is False:
        return _certo("a tarefa já não existia")
    feito = _rodar([_caminho_do_schtasks(), "/Delete", "/TN", nome, "/F"])
    depois = ler_tarefa(nome)
    if depois.existe is False:
        return _certo(saida=feito.dados.get("saida", ""))
    return _falhou("a tarefa não foi apagada", f"schtasks: {feito.detalhe} {feito.dados.get('saida', '')}; "
                   f"lida: {depois}")


def rodar_tarefa(nome: str, limite_s: float = 60) -> Resposta:
    """Manda a tarefa começar agora (não espera ela terminar). Sem licença, se a tarefa deixa a conta comum mandar
    rodar. `dados["saida"]` é a resposta do Windows, lida na tabela de letras certa ("ÊXITO: ...")."""
    if not _NOME_DE_TAREFA.match(nome):
        return _falhou("nome de tarefa fora da pasta do programa", nome)
    return _rodar([_caminho_do_schtasks(), "/Run", "/TN", nome], limite_s)


def _pasta_de_tarefas_pelo_windows(acao: str, limite_s: float = 60) -> tuple[int | None, str]:
    """Pergunta ao Agendador pela pasta do programa (`PASTA_DAS_TAREFAS`): "ler" (existe?), "licenca" (o dono e a
    licença, em texto) ou "apagar" (só se vazia). Devolve (o número da resposta do Windows, 0 = deu certo; None = não
    deu para perguntar, o texto: a licença em "licenca", senão o técnico)."""
    pasta = aspas_do_powershell(chr(92) + PASTA_DAS_TAREFAS)
    comando = {"apagar": f"$s.GetFolder('\\').DeleteFolder({aspas_do_powershell(PASTA_DAS_TAREFAS)}, 0); $t = ''",
               "licenca": f"$t = $s.GetFolder({pasta}).GetSecurityDescriptor(5)",
               "ler": f"$null = $s.GetFolder({pasta}); $t = ''"}[acao]
    resposta = rodar_powershell(
        "$s = New-Object -ComObject Schedule.Service\n$s.Connect()\n"
        f"try {{ {comando}; [Console]::Out.Write('0|' + $t) }}\n"
        "catch { $h = $_.Exception.HResult; if ($_.Exception.InnerException) { $h = $_.Exception.InnerException.HResult }\n"
        "  [Console]::Out.Write([string]$h + '|') }\n", limite_s)
    if not resposta.deu_certo:
        return None, f"{resposta.motivo} {resposta.detalhe}"
    codigo, _, texto = str(resposta.dados.get("saida", "")).partition("|")
    try:
        return int(codigo) & 0xFFFFFFFF, texto
    except ValueError:
        return None, f"resposta que não deu para ler: {resposta.dados.get('saida')!r}"


def conferir_pasta_de_tarefas() -> Resposta:
    """Lê (sem licença, se a conta pode ler) o dono e a licença da pasta do programa no Agendador e confere com
    `problemas_da_pasta_de_tarefas`. Não existe: "falhou" com `existe=False`. `dados`: `existe`, `licenca`,
    `problemas`."""
    codigo, texto = _pasta_de_tarefas_pelo_windows("licenca")
    if codigo in HRESULT_NAO_EXISTE:
        return _falhou("a pasta do programa no Agendador não existe", texto, existe=False)
    if codigo != 0:
        return _falhou("não deu para ler a licença da pasta do programa no Agendador",
                       f"0x{(codigo or 0):08X} {texto}", existe=None)
    try:
        problemas = problemas_da_pasta_de_tarefas(texto)
    except OSError as erro:
        return _falhou("a licença da pasta do programa no Agendador não deu para ler", repr(erro), existe=True)
    if problemas:
        return _falhou("a pasta do programa no Agendador não é segura: " + "; ".join(problemas), texto, existe=True,
                       licenca=texto, problemas=problemas)
    return _certo(existe=True, licenca=texto, problemas=[])


def pasta_de_tarefas_existe() -> bool | None:
    """A pasta do programa (`\\EditorImpressao`) existe no Agendador? True, False ou None (não deu para saber).
    "Acesso negado" quer dizer que existe."""
    codigo, _ = _pasta_de_tarefas_pelo_windows("ler")
    if codigo == 0 or codigo == HRESULT_ACESSO_NEGADO:
        return True
    if codigo in HRESULT_NAO_EXISTE:
        return False
    return None


def apagar_pasta_de_tarefas() -> Resposta:
    """Apaga a pasta do programa no Agendador, SÓ se estiver vazia, e confere que sumiu (se já não existia, deu
    certo). Para deixar o Agendador como estava quando foi o programa que a criou. Precisa de administrador."""
    if pasta_de_tarefas_existe() is False:
        return _certo("a pasta do Agendador já não existia")
    codigo, tecnico = _pasta_de_tarefas_pelo_windows("apagar")
    if pasta_de_tarefas_existe() is False:
        return _certo()
    if codigo == 0x80070091:                                    # ERROR_DIR_NOT_EMPTY
        return _falhou("a pasta do programa no Agendador tem outras tarefas: não apago", tecnico)
    return _falhou("a pasta do programa no Agendador não foi apagada", f"0x{(codigo or 0):08X} {tecnico}")


# ---------------------------------------------------------------------------------------------------------------------
# A pasta segura (peça 2)
# ---------------------------------------------------------------------------------------------------------------------

def pasta_segura(nome: str = NOME_DA_PASTA_SEGURA) -> Path:
    """Onde fica a pasta segura: em Arquivos de Programas, ao lado da pasta do programa. Só nomes da lista fechada."""
    if nome not in PASTAS_SEGURAS_ACEITAS:
        raise ValueError(f"pasta segura desconhecida: {nome}")
    return pasta_de_programas() / nome


def conferir_pasta_segura(nome: str = NOME_DA_PASTA_SEGURA) -> Resposta:
    """Lê (sem licença) se a pasta segura existe, é pasta de verdade (não um atalho) e tem só as licenças de
    fábrica. `dados`: `caminho`, `existe`, `licencas` (frases) e `problemas`."""
    try:
        caminho = pasta_segura(nome)
    except (ValueError, OSError) as erro:
        return _falhou("não deu para saber onde fica a pasta segura", repr(erro), existe=None)
    if not caminho.exists() and not e_atalho(caminho):
        return _falhou("a pasta segura não existe", str(caminho), caminho=str(caminho), existe=False)
    if e_atalho(caminho):
        return _falhou("a pasta segura é um atalho para outro lugar", str(caminho), caminho=str(caminho),
                       existe=True, problemas=["é um atalho"])
    if not caminho.is_dir():
        return _falhou("no lugar da pasta segura há um arquivo", str(caminho), caminho=str(caminho), existe=True,
                       problemas=["é um arquivo"])
    try:
        licencas = ler_licencas(caminho)
    except OSError as erro:
        return _falhou("não deu para ler as licenças da pasta segura", repr(erro), caminho=str(caminho), existe=True)
    problemas = problemas_da_pasta_segura(licencas)
    dados = {"caminho": str(caminho), "existe": True, "licencas": licencas.para_mostrar(), "problemas": problemas}
    if problemas:
        return _falhou("a pasta segura não confere: " + "; ".join(problemas), str(caminho), **dados)
    return _certo(**dados)


def criar_pasta_segura(nome: str = NOME_DA_PASTA_SEGURA) -> Resposta:
    """Cria a pasta segura herdando as licenças de fábrica de Arquivos de Programas (nenhuma licença à mão) e confere.
    Se ela já existe e confere, deu certo. Se a pasta que esta chamada criou não conferir, ela é apagada de novo
    (nada fica pela metade). Precisa de administrador."""
    try:
        caminho = pasta_segura(nome)
    except (ValueError, OSError) as erro:
        return _falhou("não deu para saber onde fica a pasta segura", repr(erro))
    if caminho.exists() or e_atalho(caminho):
        return conferir_pasta_segura(nome)
    try:
        _criar_pasta_comum(caminho)
    except OSError as erro:
        return _falhou("o Windows não deixou criar a pasta segura", repr(erro))
    conferida = conferir_pasta_segura(nome)
    if not conferida.deu_certo:
        shutil.rmtree(caminho, ignore_errors=True)
        sobrou = caminho.exists() or e_atalho(caminho)
        return _falhou(conferida.motivo + (" (a pasta criada agora NÃO deu para apagar: ela ficou)" if sobrou
                                           else " (a pasta criada agora foi apagada de novo)"),
                       conferida.detalhe, **{**conferida.dados, "sobrou": sobrou})
    return conferida


def apagar_pasta_segura(nome: str) -> Resposta:
    """Apaga a pasta segura (só nomes da lista fechada; nunca um atalho) e confere que sumiu. Precisa de
    administrador."""
    try:
        caminho = pasta_segura(nome)
    except (ValueError, OSError) as erro:
        return _falhou("não deu para saber onde fica a pasta segura", repr(erro))
    if e_atalho(caminho):
        return _falhou("a pasta segura é um atalho para outro lugar: não apago", str(caminho))
    if not caminho.exists():
        return _certo("a pasta segura já não existia")
    shutil.rmtree(caminho, ignore_errors=True)
    if caminho.exists():
        return _falhou("a pasta segura não foi apagada inteira (algum arquivo preso?)", str(caminho))
    return _certo()


def gravar_na_pasta_segura(nome: str, arquivo: str, texto: str) -> Resposta:
    """Grava um arquivo na pasta segura (que tem de existir e conferir) e lê de volta para conferir. Script do
    PowerShell (.ps1) vai com a marca de UTF-8. Precisa de administrador."""
    if not _NOME_DE_ARQUIVO.match(arquivo) or ".." in arquivo:
        return _falhou("nome de arquivo não aceito", arquivo)
    conferida = conferir_pasta_segura(nome)
    if not conferida.deu_certo:
        return conferida
    destino = Path(conferida.dados["caminho"]) / arquivo
    conteudo = texto.encode("utf-8-sig" if arquivo.lower().endswith(".ps1") else "utf-8")
    try:
        _gravar_por_inteiro(destino, conteudo)
        if destino.read_bytes() != conteudo:
            return _falhou("o arquivo gravado não confere", str(destino))
    except OSError as erro:
        return _falhou("não deu para gravar na pasta segura", repr(erro))
    return _certo(caminho=str(destino))


# ---------------------------------------------------------------------------------------------------------------------
# Os passos de um trabalho de administrador
# ---------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Passo:
    """Um passo do trabalho com licença: o tipo (da lista fechada `TIPOS_DE_PASSO`), a frase do que ele faz (para a
    tela e o registro, sem número de decisão) e os dados dele."""

    tipo: str
    descricao: str
    dados: dict = field(default_factory=dict)


def passo_criar_pasta_segura(nome: str = NOME_DA_PASTA_SEGURA) -> Passo:
    """Passo: criar (e conferir) a pasta segura."""
    return Passo("criar_pasta_segura", "criar a pasta segura", {"nome": nome})


def passo_apagar_pasta_segura(nome: str) -> Passo:
    """Passo: apagar a pasta segura."""
    return Passo("apagar_pasta_segura", "apagar a pasta segura", {"nome": nome})


def passo_gravar_na_pasta_segura(nome: str, arquivo: str, texto: str) -> Passo:
    """Passo: gravar um arquivo na pasta segura."""
    return Passo("gravar_na_pasta_segura", f"gravar {arquivo} na pasta segura",
                 {"nome": nome, "arquivo": arquivo, "texto": texto})


def passo_criar_tarefa(nome: str, xml: str) -> Passo:
    """Passo: criar (e conferir) uma tarefa do Windows."""
    return Passo("criar_tarefa", "criar a tarefa do Windows", {"nome": nome, "xml": xml})


def passo_apagar_tarefa(nome: str) -> Passo:
    """Passo: apagar uma tarefa do Windows."""
    return Passo("apagar_tarefa", "apagar a tarefa do Windows", {"nome": nome})


def passo_apagar_pasta_de_tarefas() -> Passo:
    """Passo: apagar a pasta do programa no Agendador, só se estiver vazia."""
    return Passo("apagar_pasta_de_tarefas", "apagar a pasta do programa no Agendador", {})


def passo_script(descricao: str, texto: str, com_segredo: bool = False, limite_s: float = 600) -> Passo:
    """Passo: rodar um script do PowerShell com licença (com o segredo pela entrada, se `com_segredo`)."""
    return Passo("script", descricao, {"texto": texto, "com_segredo": com_segredo, "limite_s": limite_s})


def passo_instalar_visual_c() -> Passo:
    """Passo (atualizador novo): instalar o Visual C++ que vem dentro do programa, só se faltar (D-727)."""
    return Passo("instalar_visual_c", "instalar o Visual C++ que vem com o programa, se faltar", {})


def passo_tirar_instalacao_do_inno() -> Passo:
    """Passo (atualizador novo): tirar a instalação antiga do programa (o instalador de antes), se houver (D-723)."""
    return Passo("tirar_instalacao_do_inno", "tirar a instalação antiga do programa, se houver", {})


def passo_dar_licenca_aos_usuarios() -> Passo:
    """Passo (atualizador novo, D-837): ACRESCENTAR "Usuários podem modificar" na pasta do programa."""
    return Passo("dar_licenca_aos_usuarios", "deixar as contas do computador atualizarem a pasta do programa", {})


def problemas_do_passo(passo: dict) -> list[str]:
    """O que está errado num passo do aviso (lugar único: o lado que pede confere antes de pedir, e o lado com
    licença confere antes de fazer). Lista vazia = o passo é aceito."""
    if not isinstance(passo, dict):
        return ["passo que não é um registro"]
    tipo, dados, descricao = passo.get("tipo"), passo.get("dados"), passo.get("descricao")
    if tipo not in TIPOS_DE_PASSO:
        return [f"tipo de passo desconhecido: {tipo!r}"]
    if not isinstance(descricao, str) or len(descricao) > 200 or not isinstance(dados, dict):
        return [f"passo {tipo} sem descrição ou sem dados"]
    if tipo in ("criar_pasta_segura", "apagar_pasta_segura", "gravar_na_pasta_segura"):
        if dados.get("nome") not in PASTAS_SEGURAS_ACEITAS:
            return [f"pasta segura desconhecida: {dados.get('nome')!r}"]
    if tipo == "gravar_na_pasta_segura":
        arquivo = dados.get("arquivo")
        if not isinstance(arquivo, str) or not _NOME_DE_ARQUIVO.match(arquivo) or ".." in arquivo:
            return [f"nome de arquivo não aceito: {arquivo!r}"]
        if not isinstance(dados.get("texto"), str):
            return ["arquivo sem texto"]
    if tipo in ("criar_tarefa", "apagar_tarefa"):
        if not isinstance(dados.get("nome"), str) or not _NOME_DE_TAREFA.match(dados["nome"]):
            return [f"nome de tarefa fora da pasta do programa: {dados.get('nome')!r}"]
    if tipo == "criar_tarefa" and not isinstance(dados.get("xml"), str):
        return ["tarefa sem desenho (XML)"]
    if tipo in _PASSOS_SEM_DADOS and dados:
        return [f"o passo {tipo} não aceita dados no pedido (o lado com licença calcula tudo sozinho)"]
    if tipo == "script":
        limite = dados.get("limite_s")
        if not isinstance(dados.get("texto"), str) or not isinstance(dados.get("com_segredo"), bool):
            return ["script sem texto"]
        if not isinstance(limite, (int, float)) or not 1 <= limite <= 7200:
            return [f"limite de tempo do script fora do aceito: {limite!r}"]
    return []


def _fazer_passo(passo: dict, segredo: str | None) -> Resposta:
    """Faz UM passo já conferido (o lado com licença). Cada tipo chama a função da peça que confere o resultado."""
    tipo, d = passo["tipo"], passo["dados"]
    if tipo == "criar_pasta_segura":
        return criar_pasta_segura(d["nome"])
    if tipo == "apagar_pasta_segura":
        return apagar_pasta_segura(d["nome"])
    if tipo == "gravar_na_pasta_segura":
        return gravar_na_pasta_segura(d["nome"], d["arquivo"], d["texto"])
    if tipo == "criar_tarefa":
        return criar_tarefa(d["nome"], d["xml"])
    if tipo == "apagar_tarefa":
        return apagar_tarefa(d["nome"])
    if tipo == "apagar_pasta_de_tarefas":
        return apagar_pasta_de_tarefas()
    if tipo in _PASSOS_SEM_DADOS:
        try:
            raiz = raiz_da_instalacao()
        except OSError as erro:
            return _falhou("este passo só roda no programa instalado", repr(erro))
        if tipo == "instalar_visual_c":
            return instalar_visual_c_do_programa(raiz / NOME_DA_PASTA_TROCADA)
        if tipo == "tirar_instalacao_do_inno":
            return tirar_instalacao_do_inno(raiz)
        return dar_licenca_aos_usuarios(raiz)
    if d["com_segredo"] and segredo is None:
        return _falhou("o script precisa do segredo e ele não veio")
    return rodar_powershell(d["texto"], d["limite_s"], segredo if d["com_segredo"] else None)


# ---------------------------------------------------------------------------------------------------------------------
# O preparo do computador do atualizador novo (23/11/2026): os três passos, feitos pelo lado com licença
# ---------------------------------------------------------------------------------------------------------------------
# Por que o lado com licença calcula tudo sozinho: o aviso de trabalho vem da pasta de troca da conta que pediu; se ele
# dissesse QUAL pasta liberar ou QUAL instalador rodar, um aviso trocado mandaria o programa com licença liberar outra
# pasta ou rodar outro programa. Por isso os três passos não aceitam dado nenhum (`_PASSOS_SEM_DADOS`) e partem do
# próprio programa com licença (`raiz_da_instalacao`).

NOME_DA_PASTA_TROCADA = "current"       # a pasta que o Velopack troca a cada versão (locator.rs: root_dir.join("current"))
NOME_DO_MANIFESTO = "sq.version"        # o manifesto dela (locator.rs: ManifestPath = current\sq.version)
DIREITOS_DE_MODIFICAR = 0x1301BF        # "Modificar" (M): ler, gravar, executar e apagar
LIMITE_DA_LICENCA_DA_PASTA_S = 1800
LIMITE_DO_INNO_S = 900
ESPERA_DO_INNO_S = 300                  # o desinstalador do Inno continua numa cópia dele depois de sair


def raiz_da_instalacao(exe: Path | str | None = None) -> Path:
    """A raiz da instalação do Velopack deste programa (a pasta acima de `current`), conferida: o programa é o
    empacotado (não roda pelo código), mora em `<raiz>\\current` com o manifesto do Velopack, nenhuma das duas é atalho
    e a raiz está dentro de Arquivos de Programas (perguntado ao Windows). Levanta OSError com o motivo.
    `exe` só muda nos testes."""
    if exe is None:
        if not getattr(sys, "frozen", False):
            raise OSError("o programa roda pelo código, não está instalado")
        exe = sys.executable
    programa = Path(exe).resolve()
    atual, raiz = programa.parent, programa.parent.parent
    if atual.name.lower() != NOME_DA_PASTA_TROCADA or not (atual / NOME_DO_MANIFESTO).is_file():
        raise OSError(f"o programa não está numa instalação do Velopack ({programa})")
    if e_atalho(raiz) or e_atalho(atual):
        raise OSError(f"a pasta do programa é um atalho para outro lugar ({raiz})")
    programas = pasta_de_programas().resolve()
    if raiz == programas or not raiz.is_relative_to(programas):
        raise OSError(f"a pasta do programa não está em Arquivos de Programas ({raiz})")
    return raiz


def instalar_visual_c_do_programa(pasta: Path) -> Resposta:
    """O Visual C++ oficial que vem dentro do programa (`<pasta>\\instalar\\vc_redist.x64.exe`, D-727), em silêncio, só
    se faltar. A regra (precisa? qual versão o pacote traz? ficou instalado?) é a única do programa,
    `atualizacao.instalar_visual_c_se_faltar`; aqui só entram a leitura do registro (`ler_versao_do_visual_c`) e o
    rodar, com uma conferência antes: o instalador e a pasta dele só podem ser mudados pelo sistema e pelos
    administradores (a regra da pasta segura, `problemas_da_pasta_segura`). Este passo roda com a licença de
    administrador, e um arquivo que uma conta comum pudesse trocar seria rodado com essa licença. (A régua da
    assinatura da Microsoft mora no `empacotar.py`, que o programa não importa: ver o ONDE-PAREI do atualizador novo.)"""
    import atualizacao

    def rodar(comando: list[str], limite_s: int) -> tuple[int, str]:
        """Confere quem pode mudar o instalador e roda; (código, o que disse)."""
        exe = Path(comando[0])
        try:
            problemas = problemas_da_pasta_segura(ler_licencas(exe)) + problemas_da_pasta_segura(ler_licencas(exe.parent))
        except OSError as erro:
            return -1, f"não deu para conferir quem pode mudar o instalador ({erro})"
        if problemas:
            return -1, "o instalador pode ser trocado por quem não é administrador, e não foi rodado: " + "; ".join(problemas)
        feito = _rodar(comando, limite_s)
        codigo = feito.dados.get("codigo")
        return (codigo if isinstance(codigo, int) else -1), f"{feito.motivo} {feito.detalhe}".strip()

    if atualizacao.instalar_visual_c_se_faltar(Path(pasta), ler=ler_versao_do_visual_c, rodar=rodar):
        return _certo("o Visual C++ está instalado")
    return _falhou("o Visual C++ não ficou instalado (o registro da atualização diz por quê)")


def tirar_instalacao_do_inno(raiz: Path, ler: Callable[[], dict | None] | None = None,
                             esperar_s: float = ESPERA_DO_INNO_S) -> Resposta:
    """Tira a instalação antiga do Inno Setup (a de 28/10), se existir (D-723), e CONFERE que a chave dela sumiu do
    registro. O caminho e o comando seguem a regra única (`atualizacao.achar_instalacao_do_inno`,
    `atualizacao.comando_para_tirar_o_inno`: só um `unins*.exe` dentro da pasta que a chave diz, nunca a pasta do
    programa novo nem a dos projetos). Quando o caminho não parece seguro, NÃO tira de propósito e dá certo (perguntar
    de novo a cada abertura não mudaria nada; fica no registro). O desinstalador do Inno continua numa cópia dele depois
    de sair: por isso a conferência espera a chave sumir até `esperar_s`. `ler` só muda nos testes."""
    import atualizacao

    ler = ler or ler_instalacao_do_inno
    antiga = atualizacao.achar_instalacao_do_inno(ler)
    if antiga is None:
        return _certo("não há instalação antiga")
    comando = atualizacao.comando_para_tirar_o_inno(antiga, Path(raiz))
    if comando is None:
        return _certo(f"instalação antiga em {antiga['pasta']}: não tirada de propósito (o caminho não parece seguro)")
    feito = _rodar(comando, LIMITE_DO_INNO_S)
    fim = time.monotonic() + esperar_s
    while ler() is not None:
        if time.monotonic() > fim:
            return _falhou("a instalação antiga não saiu", f"{antiga['pasta']}: {feito.motivo} {feito.detalhe}")
        time.sleep(1)
    return _certo(f"instalação antiga em {antiga['pasta']} tirada")


def problemas_da_licenca_dos_usuarios(antes: Licencas, depois: Licencas) -> list[str]:
    """A licença da pasta depois do passo é a de antes MAIS "Usuários podem modificar", e nada mais mudou? (D-837:
    "só para acrescentar"; o defeito de 18/11 foi uma tranca que cortou a herança.) Lista vazia = sim. Confere:
    - o dono e a herança (a lista não ficou protegida se não era) são os mesmos;
    - cada linha de antes continua (ou ficou maior, quando o Windows junta a linha nova a uma igual que já havia);
    - há uma linha própria (não herdada) de Usuários que permite Modificar, vale para a própria pasta e passa para os
      arquivos e as pastas de dentro."""
    problemas = []
    if depois.dono != antes.dono:
        problemas.append(f"o dono da pasta mudou ({antes.dono} -> {depois.dono})")
    if depois.protegida != antes.protegida:
        problemas.append("a herança da pasta mudou")
    if depois.sem_lista != antes.sem_lista:
        problemas.append("a pasta ficou sem lista de licenças")

    def cobre(velha: Licenca) -> bool:
        return any(n.sid == velha.sid and n.tipo == velha.tipo and n.herdada == velha.herdada
                   and n.so_para_dentro == velha.so_para_dentro and n.para_objetos == velha.para_objetos
                   and n.para_pastas == velha.para_pastas and (n.mascara & velha.mascara) == velha.mascara
                   for n in depois.lista)

    for velha in antes.lista:
        if not cobre(velha):
            problemas.append(f"sumiu a licença de {nome_para_mostrar(velha.sid, velha.nome)}: {velha.direitos()}")
    if not any(li.sid == SID_USUARIOS and li.tipo == "permite" and not li.herdada and not li.so_para_dentro
               and li.para_objetos and li.para_pastas and (li.mascara & DIREITOS_DE_MODIFICAR) == DIREITOS_DE_MODIFICAR
               for li in depois.lista):
        problemas.append("a pasta não ficou com \"Usuários podem modificar\" passando para dentro")
    return problemas


def _usuarios_modificam(licencas: Licencas) -> bool:
    """Alguma linha que permite a Usuários Modificar (própria ou herdada) neste arquivo ou pasta?"""
    return any(li.sid == SID_USUARIOS and li.tipo == "permite" and not li.so_para_dentro
               and (li.mascara & DIREITOS_DE_MODIFICAR) == DIREITOS_DE_MODIFICAR for li in licencas.lista)


def dar_licenca_aos_usuarios(raiz: Path) -> Resposta:
    """A ÚNICA mudança de licença de pasta do programa (D-837; o porteiro, K03, só deixa esta função): ACRESCENTA a
    Usuários (`S-1-5-32-545`) a licença de Modificar na `raiz`, passando para todos os arquivos e pastas de dentro, e
    CONFERE lendo de volta. É o jeito provado no experimento de 23/11/2026 (com ele, a conta comum trocou a versão sem
    pergunta do Windows): o `icacls "<raiz>" /grant "*S-1-5-32-545:(OI)(CI)M" /T`, pelo caminho inteiro da pasta do
    sistema. Nunca tira herança, nunca troca dono, nunca apaga nem nega linha (o porteiro barra `/inheritance`,
    `/setowner`, `/remove`, `/deny` até aqui dentro).

    O que a ferramenta faz (Microsoft Learn, icacls): "/grant[:r] <sid>:<perm>" acrescenta (sem o ":r", "permissions
    are added to any previously granted explicit permissions"); "(OI)" passa para os arquivos, "(CI)" para as pastas;
    "M" é Modificar; "/t" faz o mesmo em todos os arquivos e pastas de dentro; sem "/c" para no primeiro erro (o código
    de saída diz). O código de saída não decide: decide a leitura de volta (a raiz, pela regra
    `problemas_da_licenca_dos_usuarios`, e o manifesto de `current`, que tem de deixar Usuários modificar), e quem pediu
    ainda testa de verdade se a pasta aceita gravação (`atualizacao.pasta_aceita_gravacao`). Se a leitura não confere,
    FALHOU, e o que já foi acrescentado fica (tirar licença aqui é proibido); a pergunta volta na próxima abertura."""
    raiz = Path(raiz)
    if not raiz.is_dir() or e_atalho(raiz):
        return _falhou("a pasta do programa não existe ou é um atalho", str(raiz))
    try:
        antes = ler_licencas(raiz)
    except OSError as erro:
        return _falhou("não deu para ler a licença da pasta do programa", repr(erro))
    try:
        ferramenta = pasta_do_sistema() / "icacls.exe"
    except OSError as erro:
        return _falhou("não deu para achar a ferramenta do Windows", repr(erro))
    feito = _rodar([ferramenta, raiz, "/grant", f"*{SID_USUARIOS}:(OI)(CI)M", "/T"], LIMITE_DA_LICENCA_DA_PASTA_S)
    try:
        depois = ler_licencas(raiz)
    except OSError as erro:
        return _falhou("não deu para ler a licença da pasta do programa depois de mudar", repr(erro))
    problemas = problemas_da_licenca_dos_usuarios(antes, depois)
    manifesto = raiz / NOME_DA_PASTA_TROCADA / NOME_DO_MANIFESTO
    if manifesto.is_file():
        try:
            if not _usuarios_modificam(ler_licencas(manifesto)):
                problemas.append(f"o arquivo {manifesto.name} de dentro não ficou com a licença")
        except OSError as erro:
            problemas.append(f"não deu para ler a licença de {manifesto.name} ({erro})")
    if problemas:
        return _falhou("a licença da pasta do programa não ficou como pedido: " + "; ".join(problemas),
                       f"{feito.desfecho}: {feito.detalhe} {feito.dados.get('saida', '')}"[-4000:])
    return _certo("as contas do computador podem atualizar a pasta do programa", saida=feito.dados.get("saida", ""))


# ---------------------------------------------------------------------------------------------------------------------
# O lado com licença: o programa aberto pelo "Sim" (main.py chama antes de qualquer janela)
# ---------------------------------------------------------------------------------------------------------------------

def _ler_arquivo_da_troca(caminho: Path, limite: int) -> bytes:
    """Lê um arquivo da pasta de troca só se ele for um arquivo comum dela (nem atalho, nem ligação para outro
    arquivo) e pequeno. Levanta OSError com o motivo."""
    info = os.lstat(caminho)
    if not stat.S_ISREG(info.st_mode) or e_atalho(caminho):
        raise OSError(f"{caminho.name} não é um arquivo comum")
    if info.st_nlink != 1:
        raise OSError(f"{caminho.name} é ligado a outro arquivo")
    if info.st_size > limite:
        raise OSError(f"{caminho.name} é grande demais")
    return caminho.read_bytes()


def _conferir_a_troca(pasta: Path) -> tuple[dict | None, str]:
    """O lado com licença confere a pasta de troca e lê o aviso. Devolve (aviso, "") ou (None, o motivo).

    Recusa: caminho que não é de uma pasta de troca, atalho, aviso que não é um arquivo comum, conta que pediu
    inválida, ou a pasta (ou a de cima) onde outra conta pode gravar."""
    if not pasta.is_absolute() or not pasta.name.startswith(PREFIXO_DA_TROCA) \
            or pasta.parent.name != NOME_DA_PASTA_MAE_DA_TROCA:
        return None, "o caminho não é de uma pasta de troca"
    if not pasta.is_dir() or e_atalho(pasta) or e_atalho(pasta.parent):
        return None, "a pasta de troca não existe ou é um atalho"
    try:
        aviso = json.loads(_ler_arquivo_da_troca(pasta / NOME_DO_AVISO, TAMANHO_MAXIMO_DO_AVISO).decode("utf-8"))
    except (OSError, ValueError) as erro:
        return None, f"o aviso de trabalho não deu para ler: {erro}"
    if not isinstance(aviso, dict) or aviso.get("formato") != FORMATO_DO_AVISO:
        return None, "o aviso de trabalho não é deste programa"
    sid = aviso.get("pedido_por")
    if not isinstance(sid, str) or not _SID.match(sid):
        return None, "o aviso não diz qual conta pediu"
    for lugar in (pasta, pasta.parent):
        try:
            problemas = problemas_da_pasta_de_troca(ler_licencas(lugar), sid)
        except OSError as erro:
            return None, f"não deu para ler as licenças de {lugar.name}: {erro}"
        if problemas:
            return None, f"{lugar.name}: " + "; ".join(problemas)
    return aviso, ""


class _Relatorio:
    """O relatório que o lado com licença escreve na pasta de troca, inteiro a cada passo (se o computador desligar
    no meio, o que ficou diz até onde foi)."""

    def __init__(self, pasta: Path, passos: list[dict]):
        """Começa o relatório com todos os passos "não tentado"."""
        self.caminho = pasta / NOME_DO_RELATORIO
        self.dados = {"formato": FORMATO_DO_AVISO, "comecou_em": datetime.now().isoformat(timespec="seconds"),
                      "terminou": False, "recusado": "",
                      "passos": [{"tipo": p.get("tipo") if isinstance(p, dict) else "?",
                                  "descricao": p.get("descricao", "") if isinstance(p, dict) else "",
                                  "resultado": "não tentado", "motivo": "", "detalhe": "", "saida": ""}
                                 for p in passos]}
        self.gravar()

    def gravar(self) -> None:
        """Grava o relatório inteiro de uma vez."""
        _gravar_por_inteiro(self.caminho, json.dumps(self.dados, ensure_ascii=False, indent=1).encode("utf-8"))

    def recusar(self, motivo: str) -> None:
        """Anota que o trabalho foi recusado (nada foi feito) e fecha."""
        self.dados["recusado"] = motivo
        self.fechar()

    def anotar(self, i: int, resposta: Resposta) -> None:
        """Anota o resultado do passo `i` e grava."""
        self.dados["passos"][i].update(resultado=resposta.desfecho, motivo=resposta.motivo,
                                       detalhe=resposta.detalhe[-4000:],
                                       saida=str(resposta.dados.get("saida", ""))[-4000:])
        self.gravar()

    def fechar(self) -> None:
        """Marca o fim do trabalho e grava."""
        self.dados["terminou"] = True
        self.dados["terminou_em"] = datetime.now().isoformat(timespec="seconds")
        self.gravar()


def atender_trabalho_de_administrador(argumentos: list[str]) -> int:
    """O programa aberto com a licença de administrador: confere a pasta de troca, faz só os passos do aviso, escreve
    o relatório e devolve o código de saída. `argumentos` = o que veio depois de `ARG_TRABALHO_DE_ADMINISTRADOR`
    (só o caminho da pasta de troca). Nunca abre janela e nunca levanta.

    Se a pasta de troca não confere, não escreve nada nela (não é confiável) e só devolve o código."""
    if len(argumentos) != 1:
        return SAIDA_ARGUMENTOS_ERRADOS
    pasta = Path(argumentos[0])
    try:
        aviso, motivo = _conferir_a_troca(pasta)
        if aviso is None:
            return SAIDA_PASTA_RECUSADA
        passos = aviso.get("passos")
        if not isinstance(passos, list) or not passos:
            relatorio = _Relatorio(pasta, [])
            relatorio.recusar("o aviso não tem passos")
            return SAIDA_AVISO_RECUSADO
        relatorio = _Relatorio(pasta, passos)
        if not tem_licenca_de_administrador():
            relatorio.recusar("este trabalho precisa da licença de administrador, e o programa abriu sem ela")
            return SAIDA_SEM_LICENCA
        problemas = [p for passo in passos for p in problemas_do_passo(passo)]
        if problemas:
            relatorio.recusar("o pedido está errado: " + "; ".join(problemas))
            return SAIDA_AVISO_RECUSADO
        segredo = None
        if aviso.get("com_segredo"):
            try:
                segredo = decifrar_segredo(_ler_arquivo_da_troca(pasta / NOME_DO_SEGREDO, 100_000))
            except OSError as erro:
                relatorio.recusar(f"o segredo não deu para abrir: {erro}")
                return SAIDA_AVISO_RECUSADO
        # "ate_o_fim" (o desfazer): um passo que falha não impede os seguintes, para deixar o mínimo para trás; o
        # relatório diz cada um. Sem ele, para no primeiro que falha (os seguintes dependem dos anteriores).
        ate_o_fim = aviso.get("ate_o_fim") is True
        algum_falhou = False
        for i, passo in enumerate(passos):
            try:
                resposta = _fazer_passo(passo, segredo)
            except Exception as erro:  # noqa: BLE001 - um passo que quebra vira "falhou", nunca derruba o relatório
                resposta = _falhou("o passo teve um problema inesperado", repr(erro))
            relatorio.anotar(i, resposta)
            if not resposta.deu_certo:
                algum_falhou = True
                if not ate_o_fim:
                    break
        relatorio.fechar()
        return SAIDA_UM_PASSO_FALHOU if algum_falhou else SAIDA_TUDO_CERTO
    except Exception:  # noqa: BLE001 - o programa com licença nunca mostra erro na tela
        return SAIDA_ERRO_INESPERADO


# ---------------------------------------------------------------------------------------------------------------------
# O lado que pede: pedir a licença
# ---------------------------------------------------------------------------------------------------------------------

def programa_deste_processo() -> list[str]:
    """Como abrir o próprio programa: empacotado, o .exe; pelo código, o pythonw (sem console) com o main.py."""
    if getattr(sys, "frozen", False):
        return [sys.executable]
    executavel = Path(sys.executable)
    sem_console = executavel.with_name("pythonw.exe")
    return [str(sem_console if sem_console.is_file() else executavel),
            str(Path(__file__).resolve().parent.parent / "main.py")]


def desfecho_do_trabalho(codigo: int | None, relatorio: dict | None, pedidos: list[dict] | None = None) -> Resposta:
    """Decide o desfecho do trabalho com licença PELO RELATÓRIO (o código de saída só explica quando não há
    relatório). "Deu certo" só com o relatório completo, os mesmos passos do pedido (`pedidos`, na mesma ordem, com o
    mesmo tipo e a mesma frase), todos "deu certo" e o código 0."""
    if relatorio is None:
        motivo = _MOTIVO_DA_SAIDA.get(codigo, "o trabalho com licença não deixou relatório")
        return _falhou(motivo, f"código de saída {codigo}, sem relatório", codigo=codigo, passos=[])
    passos = relatorio.get("passos") if isinstance(relatorio.get("passos"), list) else []
    if relatorio.get("recusado"):
        return _falhou(str(relatorio["recusado"]), f"código {codigo}", codigo=codigo, passos=passos)
    if pedidos is not None and [(p.get("tipo"), p.get("descricao")) for p in passos] != \
            [(p.get("tipo"), p.get("descricao")) for p in pedidos]:
        return _falhou("o relatório do trabalho com licença não bate com o pedido",
                       f"pedidos {len(pedidos)} passos, relatório {len(passos)}", codigo=codigo, passos=passos)
    if not relatorio.get("terminou"):
        feitos = [p.get("descricao") for p in passos if p.get("resultado") == DEU_CERTO]
        return _falhou("o trabalho com licença não terminou", f"feitos até parar: {feitos}; código {codigo}",
                       codigo=codigo, passos=passos)
    for p in passos:
        if p.get("resultado") != DEU_CERTO:
            return _falhou(f"{p.get('descricao')}: {p.get('motivo') or p.get('resultado')}",
                           str(p.get("detalhe", "")), codigo=codigo, passos=passos)
    if not passos or codigo != SAIDA_TUDO_CERTO:
        return _falhou("o programa com licença terminou com um erro", f"relatório sem falha, código {codigo}",
                       codigo=codigo, passos=passos)
    return _certo(codigo=codigo, passos=passos)


def o_que_houve_ao_abrir(erro: int) -> str:
    """O erro do Windows ao pedir a licença: "nao" SÓ para o cancelado (a pessoa disse Não ou fechou a pergunta);
    qualquer outro é "erro:<n>" (nunca vira "Não", e nunca vira "deu certo")."""
    return "nao" if erro == ERRO_CANCELADO else f"erro:{erro}"


def _motivo_do_erro_ao_abrir(erro: int) -> str:
    """A frase em português para o erro do Windows ao abrir o programa com licença."""
    return {ERRO_ARQUIVO_NAO_ACHADO: "não achei o programa a abrir",
            ERRO_CAMINHO_NAO_ACHADO: "não achei a pasta do programa a abrir",
            ERRO_ACESSO_NEGADO: "o Windows não deixou abrir o programa",
            ERRO_SEM_ASSOCIACAO: "o Windows não sabe pedir licença para esse arquivo"}.get(
        erro, "o Windows não abriu o programa")


def manter_a_pasta_de_troca(houve: str) -> bool:
    """A pasta de troca fica depois do pedido? Sim quando o trabalho com licença pode estar ainda usando (passou do
    tempo, ou não deu para acompanhar); a limpeza das velhas a apaga depois de um dia. Senão, apaga."""
    return houve in ("tempo", "sem_acompanhar")


def resposta_do_pedido(houve: str, codigo: int | None, tecnico: str, relatorio: dict | None, pedidos: list[dict],
                       limite_s: float) -> Resposta:
    """O desfecho de um pedido de licença, a partir do que houve ao abrir (`o_que_houve_ao_abrir` ou "tempo",
    "sem_acompanhar", "terminou") e do relatório. Lugar único da decisão (o `pedir_licenca` só junta as peças)."""
    if houve == "nao":
        return Resposta(DISSE_NAO, "você disse Não; nada mudou", tecnico)
    if houve.startswith("erro:"):
        return _falhou(_motivo_do_erro_ao_abrir(int(houve[5:])), tecnico)
    if houve == "tempo":
        return _falhou(f"o trabalho com licença não terminou em {int(limite_s // 60)} minutos; ele pode continuar e "
                       "mudar o computador depois: confira de novo como o Windows está", tecnico)
    if houve == "sem_acompanhar":
        return _falhou("o Windows abriu o trabalho com licença, mas não deu para acompanhar até o fim; ele pode "
                       "continuar e mudar o computador depois: confira de novo como o Windows está", tecnico)
    resposta = desfecho_do_trabalho(codigo, relatorio, pedidos)
    return Resposta(resposta.desfecho, resposta.motivo, (resposta.detalhe + " " + tecnico).strip(), resposta.dados)


def _ler_relatorio(pasta: Path) -> dict | None:
    """O relatório que o lado com licença escreveu, ou None se não há (ou não deu para ler)."""
    try:
        relatorio = json.loads((pasta / NOME_DO_RELATORIO).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return relatorio if isinstance(relatorio, dict) else None


def _abrir_o_pedido(programa: list[str], argumentos: list[str], janela: int | None) -> tuple[str, int | None, str]:
    """A primeira metade do pedido: abre o programa com a licença de administrador (a pergunta do Windows) e volta
    logo depois da resposta. Devolve (o que houve, a alça do processo aberto, técnico): "comecou" (a pessoa disse
    Sim e o Windows abriu o trabalho; a alça pode ser None, a documentação diz que pode acontecer) ou
    `o_que_houve_ao_abrir` (disse Não, ou o Windows não abriu). O COM do Windows é ligado e desligado aqui, no mesmo
    fio (é a regra dele); a espera (`_esperar_o_pedido`) não precisa dele e pode rodar em outro fio.
    Nunca no fio da tela: a pergunta segura esta chamada até a resposta."""
    w = _win()
    comeco_com = w.ole32.CoInitializeEx(None, 0x2 | 0x4)       # COINIT_APARTMENTTHREADED | COINIT_DISABLE_OLE1DDE
    try:
        info = _SHELLEXECUTEINFOW()
        info.cbSize = ctypes.sizeof(info)
        info.fMask = 0x40 | 0x400 | 0x100 | 0x4000      # NOCLOSEPROCESS | FLAG_NO_UI | NOASYNC | UNICODE
        info.hwnd = janela or None
        info.lpVerb = "runas"
        info.lpFile = programa[0]
        info.lpParameters = subprocess.list2cmdline(programa[1:] + argumentos)
        info.lpDirectory = str(Path(programa[0]).parent)
        info.nShow = 0                                  # SW_HIDE: o trabalho com licença não mostra janela
        if not w.shell32.ShellExecuteExW(ctypes.byref(info)):
            erro = _ler_erro()
            return o_que_houve_ao_abrir(erro), None, f"ShellExecuteExW erro {erro}"
        return "comecou", info.hProcess or None, ""
    finally:
        if comeco_com in (0, 1):                        # S_OK, S_FALSE: este fio iniciou o COM, este fio fecha
            w.ole32.CoUninitialize()


def _esperar_o_pedido(processo: int | None, limite_s: float, pasta: Path) -> tuple[str, int | None, str]:
    """A segunda metade do pedido: espera o trabalho com licença terminar (com limite). Devolve (o que houve, código
    de saída, técnico): "tempo" (passou do limite), "sem_acompanhar" (a espera do Windows falhou), "terminou". Sem a
    alça do processo, espera o relatório dizer que terminou. Fecha a alça."""
    w = _win()
    fim = time.monotonic() + limite_s
    if not processo:
        while time.monotonic() < fim:
            if (_ler_relatorio(pasta) or {}).get("terminou"):
                return "terminou", None, "o Windows não devolveu o processo; acompanhado pelo relatório"
            time.sleep(0.5)
        return "tempo", None, f"passou de {limite_s} s (sem o processo para acompanhar)"
    try:
        while True:
            espera = w.kernel32.WaitForSingleObject(processo, 250)
            if espera == 0:                                                 # WAIT_OBJECT_0
                break
            if espera == 0xFFFFFFFF:                                        # WAIT_FAILED
                return "sem_acompanhar", None, f"WaitForSingleObject falhou (erro {_ler_erro()})"
            if time.monotonic() > fim:
                return "tempo", None, f"passou de {limite_s} s"
        codigo = wintypes.DWORD()
        if not w.kernel32.GetExitCodeProcess(processo, ctypes.byref(codigo)):
            return "terminou", None, f"código de saída não lido (erro {_ler_erro()})"
        return "terminou", int(codigo.value), ""
    finally:
        w.kernel32.CloseHandle(processo)


class PedidoDeLicenca:
    """Um pedido de licença já perguntado ao Windows (`comecar_pedido_de_licenca`; atualizador novo, 23/11/2026).

    Dois casos:
    - a resposta já veio na pergunta (`comecou` False): a pessoa disse Não, o Windows não abriu o trabalho, ou o pedido
      estava errado; `esperar()` devolve essa resposta na hora;
    - a pessoa disse Sim e o trabalho com licença começou (`comecou` True): `esperar()` espera ele terminar (com o
      limite), lê o relatório, decide pelo relatório (`resposta_do_pedido`, o lugar único da decisão) e apaga a pasta de
      troca (menos quando o trabalho pode estar ainda rodando: ver `manter_a_pasta_de_troca`).
    `esperar()` pode rodar em outro fio (a espera não usa o COM) e só espera uma vez: as chamadas seguintes devolvem a
    mesma resposta. Arriscado: esperar no fio da tela (a janela congela enquanto o Visual C++ instala)."""

    def __init__(self, resposta: Resposta | None = None, *, processo: int | None = None, pasta: Path | None = None,
                 pedidos: list[dict] | None = None, limite_s: float = 1800, na_frente: bool = False) -> None:
        """Só `comecar_pedido_de_licenca` cria (e os testes)."""
        self._resposta = resposta
        self._processo, self._pasta, self._pedidos = processo, pasta, list(pedidos or [])
        self._limite_s, self._na_frente = limite_s, na_frente

    @property
    def comecou(self) -> bool:
        """A pessoa disse Sim e o trabalho com licença começou (ainda falta `esperar`)."""
        return self._resposta is None

    @property
    def resposta_da_pergunta(self) -> Resposta | None:
        """A resposta que já veio na pergunta (None quando o trabalho começou)."""
        return self._resposta

    def esperar(self) -> Resposta:
        """Espera o trabalho com licença terminar e devolve o desfecho (ver a classe). Nunca levanta."""
        if self._resposta is not None:
            return self._resposta
        manter = False
        try:
            houve, codigo, tecnico = _esperar_o_pedido(self._processo, self._limite_s, self._pasta)
            manter = manter_a_pasta_de_troca(houve)
            r = resposta_do_pedido(houve, codigo, tecnico, _ler_relatorio(self._pasta) if houve == "terminou" else None,
                                   self._pedidos, self._limite_s)
            self._resposta = Resposta(r.desfecho, r.motivo, r.detalhe, {**r.dados, "janela_na_frente": self._na_frente})
        except Exception as erro:  # noqa: BLE001 - nunca derruba quem esperava
            self._resposta = _falhou("o pedido ao Windows teve um problema inesperado", repr(erro))
        finally:
            _fechar_a_pasta_do_pedido(self._pasta, manter)
        return self._resposta


def _fechar_a_pasta_do_pedido(pasta: Path | None, manter: bool) -> None:
    """Apaga o segredo do pedido e, se não for para manter, a pasta de troca inteira (nunca levanta)."""
    if pasta is None:
        return
    try:
        (pasta / NOME_DO_SEGREDO).unlink(missing_ok=True)
    except OSError:
        pass
    if not manter:
        apagar_pasta_de_troca(pasta)


def comecar_pedido_de_licenca(passos: list[Passo], *, segredo: str | None = None, janela: int | None = None,
                              programa: list[str] | None = None, limite_s: float = 1800,
                              ate_o_fim: bool = False) -> PedidoDeLicenca:
    """A pergunta do Windows ("Deseja permitir...?") para fazer os `passos` com a licença de administrador, e VOLTA
    LOGO DEPOIS DA RESPOSTA (atualizador novo, 23/11/2026: a pergunta vem antes da janela do programa, D-806, D-834, e
    a espera roda por trás, com a janela já aberta). Grava o aviso de trabalho numa pasta de troca e abre o próprio
    programa com a licença e `ARG_TRABALHO_DE_ADMINISTRADOR` (o mesmo de sempre). Os argumentos são os de
    `pedir_licenca`. Nunca levanta: o que der errado antes do trabalho começar vem como a resposta do pedido
    (`PedidoDeLicenca.comecou` False)."""
    pedidos = [asdict(p) for p in passos]
    problemas = [p for passo in pedidos for p in problemas_do_passo(passo)] or ([] if pedidos else ["sem passos"])
    if problemas:
        return PedidoDeLicenca(_falhou("o pedido ao Windows está errado", "; ".join(problemas)))
    programa = [str(p) for p in (programa or programa_deste_processo())]
    if not Path(programa[0]).is_file():
        return PedidoDeLicenca(_falhou("não achei o programa a abrir com a licença", programa[0]))
    try:
        sid = sid_desta_conta()
        pasta = criar_pasta_de_troca()
    except OSError as erro:
        return PedidoDeLicenca(_falhou("não consegui preparar o pedido (o disco está cheio ou sem licença?)",
                                       repr(erro)))
    try:
        problemas = problemas_da_pasta_de_troca(ler_licencas(pasta), sid) + \
            problemas_da_pasta_de_troca(ler_licencas(pasta.parent), sid)
        if problemas:
            _fechar_a_pasta_do_pedido(pasta, False)
            return PedidoDeLicenca(_falhou("a pasta do pedido não é só desta conta: " + "; ".join(problemas),
                                           str(pasta)))
        if segredo is not None:
            _gravar_por_inteiro(pasta / NOME_DO_SEGREDO, cifrar_segredo(segredo))
        aviso = {"formato": FORMATO_DO_AVISO, "pedido_por": sid, "criado_em": datetime.now().isoformat(timespec="seconds"),
                 "com_segredo": segredo is not None, "ate_o_fim": ate_o_fim, "passos": pedidos}
        _gravar_por_inteiro(pasta / NOME_DO_AVISO, json.dumps(aviso, ensure_ascii=False).encode("utf-8"))
        na_frente = trazer_para_a_frente(janela)
        houve, processo, tecnico = _abrir_o_pedido(programa, [ARG_TRABALHO_DE_ADMINISTRADOR, str(pasta)], janela)
    except Exception as erro:  # noqa: BLE001 - nunca derruba quem chamou
        _fechar_a_pasta_do_pedido(pasta, False)
        return PedidoDeLicenca(_falhou("o pedido ao Windows teve um problema inesperado", repr(erro)))
    if houve != "comecou":
        _fechar_a_pasta_do_pedido(pasta, False)
        r = resposta_do_pedido(houve, None, tecnico, None, pedidos, limite_s)
        return PedidoDeLicenca(Resposta(r.desfecho, r.motivo, r.detalhe, {**r.dados, "janela_na_frente": na_frente}))
    return PedidoDeLicenca(processo=processo, pasta=pasta, pedidos=pedidos, limite_s=limite_s, na_frente=na_frente)


def pedir_licenca(passos: list[Passo], *, segredo: str | None = None, janela: int | None = None,
                  programa: list[str] | None = None, limite_s: float = 1800, ate_o_fim: bool = False) -> Resposta:
    """A pergunta do Windows ("Deseja permitir...?"): abre o próprio programa com a licença de administrador para
    fazer os `passos`, espera e lê o relatório. É `comecar_pedido_de_licenca(...).esperar()` (uma conta só; desde o
    atualizador novo, 23/11/2026, as duas metades ficaram separadas para a espera poder rodar por trás).

    `janela`: a janela do programa (o número dela no Windows), que vira a dona da pergunta e é trazida para a frente
    antes. `segredo`: vai cifrado num arquivo da pasta de troca, nunca pela linha de comando. `programa`: o programa a
    abrir (padrão: este mesmo). `ate_o_fim`: para desfazer: um passo que falha não impede os seguintes. Chamar FORA
    do fio da tela: a pergunta segura a chamada até a pessoa responder.

    Desfechos (decididos em `resposta_do_pedido`): DISSE_NAO (a pessoa disse Não; nada mudou), FALHOU (com o passo e o
    motivo), DEU_CERTO (todos os passos feitos e conferidos). `dados`: `passos` (o relatório de cada passo),
    `janela_na_frente`, `codigo`. Se o trabalho com licença passou do limite, a pasta de troca fica (ele ainda pode
    estar usando; a limpeza das velhas a apaga depois de um dia)."""
    return comecar_pedido_de_licenca(passos, segredo=segredo, janela=janela, programa=programa, limite_s=limite_s,
                                     ate_o_fim=ate_o_fim).esperar()
