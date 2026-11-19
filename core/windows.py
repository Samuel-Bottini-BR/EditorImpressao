"""A peça única do Windows (plano da parte do Windows, versão 3: peças 1 e 2).

O QUE É
    O único lugar do programa que conversa com o Windows: pedir a licença de administrador, lançar um processo solto,
    rodar e esperar uma ferramenta do Windows ou um script do PowerShell, criar/apagar/rodar/ler tarefas do
    Agendador, a pasta de troca, a pasta segura, ler licenças de pasta e marcas. O porteiro (`regras_dos_agentes`,
    conferência K01) só deixa essa conversa acontecer aqui. Nenhum chamador do programa usa esta peça ainda: eles
    mudam nos passos 3 a 5 do plano; hoje só o `main.py` (a entrada do trabalho de administrador), a janela de prova e
    os testes a usam.

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
      função própria na peça (`PROGRAMAS_COM_FUNCAO_PROPRIA`: as tarefas, as licenças de pasta, o PowerShell, o pedido
      de licença, o registro, os serviços, o firewall, o instalador...). Quem precisa de um deles chama a função da
      peça (`ler_tarefa`, `rodar_tarefa`, `rodar_powershell`, `pedir_licenca`...), ou a peça ganha uma função nova
      para isso, com teste.

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
                  "apagar_tarefa", "apagar_pasta_de_tarefas", "script")

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

# Os programas do Windows que têm função própria na peça (ver "A PEÇA É FECHADA" no topo). O rodar e o lançar
# genéricos recusam qualquer um destes, pelo nome do arquivo, venha com o caminho inteiro ou não. O cmd entra porque
# roda qualquer outro. Acrescentar é seguro; tirar abre a porta.
PROGRAMAS_COM_FUNCAO_PROPRIA = frozenset({
    "schtasks", "powershell", "pwsh", "powershell_ise", "cmd", "runas", "icacls", "cacls", "takeown", "reg", "regedit",
    "sc", "net", "net1", "netsh", "msiexec", "wmic", "wevtutil", "bcdedit", "rundll32", "mshta", "wscript", "cscript",
    "taskkill", "shutdown", "dism", "update",
})

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
        linhas = [f"dono: {self.dono_nome or self.dono}"]
        if self.sem_lista:
            linhas.append("SEM LISTA DE LICENÇAS: todos podem tudo")
        linhas += [f"{li.nome or li.sid}: {li.direitos()}" + (" (herdada)" if li.herdada else "")
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
        if cabeca.AceType in (_ACE_PERMITE, _ACE_NEGA):
            psid = ace.value + 8
            linhas.append(Licenca(_sid_em_texto(psid), _nome_da_conta(psid),
                                  "permite" if cabeca.AceType == _ACE_PERMITE else "nega", cabeca.Mask, herdada,
                                  so_dentro))
        else:
            linhas.append(Licenca("", "", "outra", cabeca.Mask, herdada, so_dentro))
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
            problemas.append(f"{li.nome or li.sid} não ficou com os direitos pedidos na tarefa")
    pode_mudar = {SID_SISTEMA, SID_ADMINISTRADORES, SID_INSTALADOR_CONFIAVEL}
    pode_mudar |= {li.sid for li in pedidas if _direitos(li.mascara) & _ESCRITA}
    for e in efetivas:
        if _direitos(e.mascara) & _ESCRITA and e.sid not in pode_mudar:
            problemas.append(f"{e.nome or e.sid} pode mudar a tarefa")
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
        problemas.append(f"o dono da pasta é {licencas.dono_nome or licencas.dono}, não a conta que pediu")
    aceitos = {sid_da_conta, SID_SISTEMA, SID_ADMINISTRADORES, SID_PROPRIETARIO_CRIADOR, SID_DIREITOS_DO_DONO}
    for quem in sorted(licencas.quem_grava() - aceitos):
        problemas.append(f"outra conta pode gravar na pasta: {quem}")
    for quem in sorted(licencas.quem_le() - aceitos):
        problemas.append(f"outra conta pode ler a pasta: {quem}")
    return problemas


def problemas_da_pasta_segura(licencas: Licencas) -> list[str]:
    """A pasta segura tem só as licenças de fábrica de Arquivos de Programas? O dono é o sistema, os administradores
    ou o Instalador Confiável; só eles (e o "Proprietário Criador", que vira o dono) podem gravar; as contas comuns
    leem."""
    problemas = []
    donos = (SID_SISTEMA, SID_ADMINISTRADORES, SID_INSTALADOR_CONFIAVEL)
    if licencas.dono not in donos:
        problemas.append(f"o dono da pasta é {licencas.dono_nome or licencas.dono} (deveria ser o sistema ou os "
                         "administradores)")
    aceitos = {SID_SISTEMA, SID_ADMINISTRADORES, SID_INSTALADOR_CONFIAVEL, SID_PROPRIETARIO_CRIADOR}
    for quem in sorted(licencas.quem_grava() - aceitos):
        problemas.append(f"uma conta que não é administradora pode gravar na pasta: {quem}")
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


def _gravar_por_inteiro(caminho: Path, conteudo: bytes) -> None:
    """Grava o arquivo inteiro de uma vez (num arquivo ao lado e depois troca o nome): quem lê nunca vê pela metade."""
    provisorio = caminho.with_name(caminho.name + ".gravando")
    provisorio.write_bytes(conteudo)
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

def _programa_com_funcao_propria(programa: str) -> bool:
    """O programa (pelo nome do arquivo, com ou sem caminho e ".exe") é um dos que têm função própria na peça?"""
    nome = Path(str(programa).strip().strip('"')).name.lower()
    return nome.removesuffix(".exe") in PROGRAMAS_COM_FUNCAO_PROPRIA


def _recusa_de_programa(programa: str) -> Resposta:
    """A resposta para quem pede ao rodar ou lançar genérico um programa que tem função própria na peça."""
    return _falhou("este programa do Windows tem função própria na peça: use a função dela",
                   f"{programa} recusado pelo rodar genérico (ver \"A PEÇA É FECHADA\" em core/windows.py)")


def rodar_e_esperar(comando: list, limite_s: float = 120, entrada: bytes | None = None,
                    letras: str = "oem") -> Resposta:
    """Roda um programa sem janela, espera ele terminar (com limite) e lê a resposta. RECUSA os programas que têm
    função própria na peça (`PROGRAMAS_COM_FUNCAO_PROPRIA`; ver "A PEÇA É FECHADA" no topo).

    `letras`: a tabela de letras da resposta. Os programas de console do Windows escrevem na tabela OEM do console
    ("oem"); o Python escreve em UTF-8 ("utf-8"). Deu certo = código de saída 0.
    `dados`: `codigo`, `saida` (o que o programa escreveu como resposta) e `erros` (o que escreveu como erro), separados
    e já com as letras certas."""
    if not comando or _programa_com_funcao_propria(str(comando[0])):
        return _recusa_de_programa(str(comando[0]) if comando else "(nada)")
    return _rodar(comando, limite_s, entrada, letras)


def _rodar(comando: list, limite_s: float = 120, entrada: bytes | None = None, letras: str = "oem") -> Resposta:
    """O rodar sem filtro, só de dentro da peça (as funções próprias de cada ferramenta usam este)."""
    comando = [str(c) for c in comando]
    extra = {"input": entrada} if entrada is not None else {"stdin": subprocess.DEVNULL}
    try:
        feito = subprocess.run(comando, capture_output=True, timeout=limite_s, creationflags=CREATE_NO_WINDOW,
                               **extra)
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
    return _falhou(f"o Windows respondeu com erro (código {feito.returncode})", (erros + "\n" + saida).strip(),
                   codigo=feito.returncode, saida=saida, erros=erros)


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
        return _rodar(_comando_do_powershell(script), limite_s, entrada, "utf-8-sig")
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
    if not comando or _programa_com_funcao_propria(str(comando[0])):
        return _recusa_de_programa(str(comando[0]) if comando else "(nada)")
    return _lancar_solto(comando, sinal, espera_s)


def _lancar_solto(comando: list, sinal: Path, espera_s: float) -> Resposta:
    """O lançar solto sem filtro, só de dentro da peça (`lancar_powershell_solto` usa este)."""
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
                                    stderr=subprocess.DEVNULL, close_fds=True, creationflags=bandeiras)
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
    return _falhou(f"o processo lançado saiu sem começar (código {processo.returncode})", comando[0], grupo=grupo)


def lancar_powershell_solto(texto: str, espera_s: float = 30) -> Resposta:
    """Lança solto um script do PowerShell (em arquivo com a marca de UTF-8, numa pasta de troca) e espera o sinal de
    vida. O script dá o sinal na primeira linha e apaga a própria pasta de troca no fim, deu certo ou não."""
    try:
        pasta = criar_pasta_de_troca()
    except OSError as erro:
        return _falhou("não consegui preparar o script (o disco está cheio ou sem licença?)", repr(erro))
    sinal = pasta / "comecei.txt"
    script = pasta / "solto.ps1"
    try:
        _gravar_script(script, _CABECA_DO_SCRIPT
                       + f"[System.IO.File]::WriteAllText({aspas_do_powershell(sinal)}, 'comecei')\n"
                       + "try {\n" + texto + "\n} finally {\n"
                       + f"  Remove-Item -LiteralPath {aspas_do_powershell(pasta)} -Recurse -Force -ErrorAction SilentlyContinue\n"
                       + "}\n")
    except (OSError, ValueError) as erro:
        apagar_pasta_de_troca(pasta)
        return _falhou("não consegui preparar o script", repr(erro))
    resposta = _lancar_solto(_comando_do_powershell(script), sinal, espera_s)
    if not resposta.deu_certo:
        apagar_pasta_de_troca(pasta)
    return resposta


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
    return Tarefa(nome, None, motivo=f"o Windows respondeu 0x{codigo:08X}")


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
    """Pergunta ao Agendador pela pasta do programa (`PASTA_DAS_TAREFAS`): "ler" ou "apagar" (só se vazia). Devolve
    (o número da resposta do Windows, 0 = deu certo; None = não deu para perguntar, o técnico)."""
    comando = (f"$s.GetFolder('\\').DeleteFolder({aspas_do_powershell(PASTA_DAS_TAREFAS)}, 0)" if acao == "apagar"
               else f"$null = $s.GetFolder({aspas_do_powershell(chr(92) + PASTA_DAS_TAREFAS)})")
    resposta = rodar_powershell(
        "$s = New-Object -ComObject Schedule.Service\n$s.Connect()\n"
        f"try {{ {comando}; [Console]::Out.Write('0') }}\n"
        "catch { $h = $_.Exception.HResult; if ($_.Exception.InnerException) { $h = $_.Exception.InnerException.HResult }\n"
        "  [Console]::Out.Write([string]$h) }\n", limite_s)
    if not resposta.deu_certo:
        return None, f"{resposta.motivo} {resposta.detalhe}"
    try:
        return int(resposta.dados["saida"]) & 0xFFFFFFFF, resposta.dados["saida"]
    except (ValueError, KeyError):
        return None, f"resposta que não deu para ler: {resposta.dados.get('saida')!r}"


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
    if d["com_segredo"] and segredo is None:
        return _falhou("o script precisa do segredo e ele não veio")
    return rodar_powershell(d["texto"], d["limite_s"], segredo if d["com_segredo"] else None)


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
        return _falhou(f"o programa com licença terminou com o código {codigo}", "relatório sem falha, código não 0",
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
        erro, f"o Windows não abriu o programa (código {erro})")


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


def _abrir_com_licenca(programa: list[str], argumentos: list[str], janela: int | None, limite_s: float,
                       pasta: Path) -> tuple[str, int | None, str]:
    """Abre o programa com a licença de administrador (a pergunta do Windows) e espera ele terminar.

    Devolve (o que houve, código de saída, técnico): `o_que_houve_ao_abrir` (o Windows não abriu, ou a pessoa disse
    Não), "tempo" (passou do limite), "sem_acompanhar" (a espera do Windows falhou), "terminou". Se o Windows não
    devolver o processo (a documentação diz que pode acontecer), espera o relatório dizer que terminou. Nunca no fio da
    tela: a pergunta segura esta chamada até a resposta."""
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
        fim = time.monotonic() + limite_s
        if not info.hProcess:
            while time.monotonic() < fim:
                if (_ler_relatorio(pasta) or {}).get("terminou"):
                    return "terminou", None, "o Windows não devolveu o processo; acompanhado pelo relatório"
                time.sleep(0.5)
            return "tempo", None, f"passou de {limite_s} s (sem o processo para acompanhar)"
        try:
            while True:
                espera = w.kernel32.WaitForSingleObject(info.hProcess, 250)
                if espera == 0:                                                 # WAIT_OBJECT_0
                    break
                if espera == 0xFFFFFFFF:                                        # WAIT_FAILED
                    return "sem_acompanhar", None, f"WaitForSingleObject falhou (erro {_ler_erro()})"
                if time.monotonic() > fim:
                    return "tempo", None, f"passou de {limite_s} s"
            codigo = wintypes.DWORD()
            if not w.kernel32.GetExitCodeProcess(info.hProcess, ctypes.byref(codigo)):
                return "terminou", None, f"código de saída não lido (erro {_ler_erro()})"
            return "terminou", int(codigo.value), ""
        finally:
            w.kernel32.CloseHandle(info.hProcess)
    finally:
        if comeco_com in (0, 1):                        # S_OK, S_FALSE: este fio iniciou o COM, este fio fecha
            w.ole32.CoUninitialize()


def pedir_licenca(passos: list[Passo], *, segredo: str | None = None, janela: int | None = None,
                  programa: list[str] | None = None, limite_s: float = 1800, ate_o_fim: bool = False) -> Resposta:
    """A pergunta do Windows ("Deseja permitir...?"): abre o próprio programa com a licença de administrador para
    fazer os `passos`, espera e lê o relatório.

    `janela`: a janela do programa (o número dela no Windows), que vira a dona da pergunta e é trazida para a frente
    antes. `segredo`: vai cifrado num arquivo da pasta de troca, nunca pela linha de comando. `programa`: o programa a
    abrir (padrão: este mesmo). `ate_o_fim`: para desfazer: um passo que falha não impede os seguintes. Chamar FORA
    do fio da tela: a pergunta segura a chamada até a pessoa responder.

    Desfechos (decididos em `resposta_do_pedido`): DISSE_NAO (a pessoa disse Não; nada mudou), FALHOU (com o passo e o
    motivo), DEU_CERTO (todos os passos feitos e conferidos). `dados`: `passos` (o relatório de cada passo),
    `janela_na_frente`, `codigo`. Se o trabalho com licença passou do limite, a pasta de troca fica (ele ainda pode
    estar usando; a limpeza das velhas a apaga depois de um dia)."""
    pedidos = [asdict(p) for p in passos]
    problemas = [p for passo in pedidos for p in problemas_do_passo(passo)] or ([] if pedidos else ["sem passos"])
    if problemas:
        return _falhou("o pedido ao Windows está errado", "; ".join(problemas))
    programa = [str(p) for p in (programa or programa_deste_processo())]
    if not Path(programa[0]).is_file():
        return _falhou("não achei o programa a abrir com a licença", programa[0])
    try:
        sid = sid_desta_conta()
        pasta = criar_pasta_de_troca()
    except OSError as erro:
        return _falhou("não consegui preparar o pedido (o disco está cheio ou sem licença?)", repr(erro))
    manter_a_pasta = False
    try:
        problemas = problemas_da_pasta_de_troca(ler_licencas(pasta), sid) + \
            problemas_da_pasta_de_troca(ler_licencas(pasta.parent), sid)
        if problemas:
            return _falhou("a pasta do pedido não é só desta conta: " + "; ".join(problemas), str(pasta))
        if segredo is not None:
            _gravar_por_inteiro(pasta / NOME_DO_SEGREDO, cifrar_segredo(segredo))
        aviso = {"formato": FORMATO_DO_AVISO, "pedido_por": sid, "criado_em": datetime.now().isoformat(timespec="seconds"),
                 "com_segredo": segredo is not None, "ate_o_fim": ate_o_fim, "passos": pedidos}
        _gravar_por_inteiro(pasta / NOME_DO_AVISO, json.dumps(aviso, ensure_ascii=False).encode("utf-8"))
        na_frente = trazer_para_a_frente(janela)
        houve, codigo, tecnico = _abrir_com_licenca(programa, [ARG_TRABALHO_DE_ADMINISTRADOR, str(pasta)], janela,
                                                    limite_s, pasta)
        manter_a_pasta = houve in ("tempo", "sem_acompanhar")
        resposta = resposta_do_pedido(houve, codigo, tecnico, _ler_relatorio(pasta) if houve == "terminou" else None,
                                      pedidos, limite_s)
        return Resposta(resposta.desfecho, resposta.motivo, resposta.detalhe,
                        {**resposta.dados, "janela_na_frente": na_frente})
    except Exception as erro:  # noqa: BLE001 - nunca derruba quem chamou
        return _falhou("o pedido ao Windows teve um problema inesperado", repr(erro))
    finally:
        try:
            (pasta / NOME_DO_SEGREDO).unlink(missing_ok=True)
        except OSError:
            pass
        if not manter_a_pasta:
            apagar_pasta_de_troca(pasta)
