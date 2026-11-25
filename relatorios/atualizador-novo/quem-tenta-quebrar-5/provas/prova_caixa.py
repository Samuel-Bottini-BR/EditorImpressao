"""Quem tenta quebrar 5 (25/11/2026): a caixa do Windows DE VERDADE (`core.windows.mostrar_caixa_do_windows`, que chama
`MessageBoxW`), nos casos que o escritor não rodou. EXECUTADO neste Windows, numa área de trabalho separada criada pela
prova (`CreateDesktopW`, "EditorProvaQtq5"), que ninguém vê: nada aparece na tela do Samuel.

Casos (cada abertura num processo à parte, como o programa; as aberturas do mesmo grupo dividem a instalação, o
bilhete e a conta):
- FUNDO: a frase (2) chega POR TRÁS (a procura num fio de verdade) antes de a janela abrir; a janela "abre" (o
  executor recebe `ligar_a_tela`) enquanto a caixa está na tela. A frase aparece uma vez só, na caixa, e não vai para a
  janela? A janela abriu sem esperar o OK?
- MATAR: a versão reprovada; a caixa na tela; o processo é morto à força (TerminateProcess, como desligar ou o
  Gerenciador de Tarefas) antes do OK. A abertura seguinte mostra a caixa de novo? E a outra, depois do OK?
- FECHAR_X: a caixa fechada pelo X (WM_CLOSE), não pelo OK. Conta como vista?
- ESPERA: o OK só chega 6 s depois: a abertura fica esperando (o programa só tenta abrir depois do OK)?

De verdade: a caixa (pela peça), a regra, o executor, o disco, o fio por trás (FUNDO). De mentira: a borda que não é a
caixa (Velopack e lista de processos, do `tests/ajudante_do_atualizador.py`), o teste rápido (MATAR, FECHAR_X, ESPERA:
"não passou"), a janela do programa (FUNDO: uma lista que anota o que a janela receberia).
O PROGRAMDATA e o LOCALAPPDATA trocados DENTRO do Python do filho e conferidos com assert antes de tudo.
Uso: python prova_caixa.py
"""
from __future__ import annotations

import ctypes
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from ctypes import wintypes
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
BASE = RAMO / "saida_teste" / "qtq5" / "caixa"
PY = sys.executable
NOME_DA_AREA = "EditorProvaQtq5"
GENERIC_ALL = 0x10000000

u32 = ctypes.WinDLL("user32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
ENUM = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
u32.CreateDesktopW.restype = wintypes.HANDLE
u32.CreateDesktopW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                               ctypes.c_void_p]
u32.OpenDesktopW.restype = wintypes.HANDLE
u32.OpenDesktopW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
u32.SetThreadDesktop.argtypes = [wintypes.HANDLE]
u32.CloseDesktop.argtypes = [wintypes.HANDLE]
u32.EnumDesktopWindows.argtypes = [wintypes.HANDLE, ENUM, wintypes.LPARAM]
u32.EnumChildWindows.argtypes = [wintypes.HWND, ENUM, wintypes.LPARAM]
u32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
u32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
u32.GetDlgCtrlID.argtypes = [wintypes.HWND]
u32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
k32.OpenProcess.restype = wintypes.HANDLE
k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
k32.CloseHandle.argtypes = [wintypes.HANDLE]


def _texto(hwnd, funcao) -> str:
    b = ctypes.create_unicode_buffer(1024)
    funcao(hwnd, b, 1024)
    return b.value


def _vigia(area, acao: str, achadas: list, parar: threading.Event) -> None:
    """Dentro da área de trabalho separada: acha cada caixa, lê o título e o texto da própria caixa e faz a `acao`."""
    if not u32.SetThreadDesktop(area):
        achadas.append({"erro": f"SetThreadDesktop falhou ({ctypes.get_last_error()})"})
        return
    vistas: set = set()
    while not parar.is_set():
        caixas: list = []

        def cada(hwnd, _):
            if _texto(hwnd, u32.GetClassNameW) == "#32770" and hwnd not in vistas:
                caixas.append(hwnd)
            return True

        u32.EnumDesktopWindows(area, ENUM(cada), 0)
        for hwnd in caixas:
            time.sleep(0.4)
            filhos: list = []
            u32.EnumChildWindows(hwnd, ENUM(lambda h, _: filhos.append(h) or True), 0)
            estaticos = [_texto(h, u32.GetWindowTextW) for h in filhos if _texto(h, u32.GetClassNameW) == "Static"]
            botoes = [h for h in filhos if _texto(h, u32.GetClassNameW) == "Button"]
            achada = {"apareceu": round(time.time(), 3), "titulo": _texto(hwnd, u32.GetWindowTextW),
                      "texto": [t for t in estaticos if t], "botoes": [_texto(h, u32.GetWindowTextW) for h in botoes]}
            if acao == "espera":
                time.sleep(6)
            if acao == "matar":
                dono = wintypes.DWORD()
                u32.GetWindowThreadProcessId(hwnd, ctypes.byref(dono))
                h = k32.OpenProcess(0x0001, False, dono.value)          # PROCESS_TERMINATE
                achada["fez"] = f"matou o processo {dono.value}: {bool(h and k32.TerminateProcess(h, 9))}"
                if h:
                    k32.CloseHandle(h)
            elif acao == "fechar_x":
                u32.PostMessageW(hwnd, 0x0010, 0, 0)                     # WM_CLOSE (o X)
                achada["fez"] = "fechou pelo X (WM_CLOSE)"
            elif botoes:
                ident = u32.GetDlgCtrlID(botoes[0])
                u32.PostMessageW(hwnd, 0x0111, ident & 0xFFFF, botoes[0])
                achada["fez"] = f"clicou o botão {ident} ({_texto(botoes[0], u32.GetWindowTextW)})"
            achada["quando"] = round(time.time(), 3)
            vistas.add(hwnd)
            achadas.append(achada)
        time.sleep(0.2)


def filho(caso: str, pasta: Path) -> None:
    """O "programa": entra na área de trabalho de prova antes de qualquer janela e abre como o programa instalado."""
    tempo: list = []
    marca = lambda o_que: tempo.append((round(time.time(), 3), o_que))  # noqa: E731
    area = u32.OpenDesktopW(NOME_DA_AREA, 0, False, GENERIC_ALL)
    assert area and u32.SetThreadDesktop(area), ctypes.get_last_error()
    grupo = pasta.parent
    os.environ["PROGRAMDATA"] = str(grupo / "ProgramData")
    os.environ["LOCALAPPDATA"] = str(grupo / "LocalAppData")
    os.environ["USERNAME"] = "Kaique"
    sys.path.insert(0, str(RAMO))
    import atualizacao
    import historico
    import versao
    from core import fases_da_atualizacao as fases
    from core import windows
    from tests import ajudante_do_atualizador as aj

    assert str(atualizacao.pasta_do_estado()).startswith(str(BASE)), atualizacao.pasta_do_estado()
    assert str(historico.pasta_de_dados()).startswith(str(BASE)), historico.pasta_de_dados()

    def caixa_de_verdade(titulo, texto):
        marca(f"a caixa vai aparecer (fio {threading.current_thread().name})")
        r = windows.mostrar_caixa_do_windows(titulo, texto)
        marca(f"a caixa voltou: {r.desfecho} {r.motivo}".strip())
        return r

    janela: list = []
    if caso == "fundo":
        versao.VERSAO = aj.ANTERIOR
        outra = aj.assinatura.nova_chave_privada()
        p = aj.Prova(pasta, chave_da_nova=outra, caixa_de_verdade=True)      # a nova sem a assinatura do Samuel
        p.win.mostrar_caixa_do_windows = caixa_de_verdade
        fio: list = []

        def por_tras(trabalho):
            t = threading.Thread(target=trabalho, name="atualizacao", daemon=True)
            fio.append(t)
            t.start()

        p.atual._por_tras = por_tras
        marca("abrir")
        p.abrir()
        time.sleep(1.0)                                    # a caixa já está na tela (o fio por trás espera o OK)
        marca("a janela abre (ligar_a_tela)")
        p.atual.ligar_a_tela(lambda ef: (janela.append(type(ef).__name__), marca(f"a janela recebeu {type(ef).__name__}")))
        marca("ligar_a_tela voltou (a janela não esperou o OK)")
        for t in fio:
            t.join(30)
    else:
        versao.VERSAO = aj.NOVA
        p = aj.Prova(pasta, teste=(False, "de prova"), ultima_boa=aj.ANTERIOR, publicar_nova=False,
                     caixa_de_verdade=True)
        p.pacote_em_packages(aj.NOVA)
        p.win.mostrar_caixa_do_windows = caixa_de_verdade
        marca("abrir")
        saida = p.abrir(*([atualizacao.ARG_CONFERIR_NOVA, aj.ANTERIOR, aj.NOVA] if pasta.name == "a1" else []))
        marca(f"a abertura voltou {saida!r}: SÓ AGORA o programa tentaria abrir a janela")
    print("RESULTADO " + json.dumps({
        "caso": caso, "abertura": pasta.name, "tempo": tempo, "a janela recebeu": janela,
        "vistos": sorted(atualizacao.ler_vistos()), "bilhete": atualizacao.ler_estado()}, ensure_ascii=False))


def rodar(caso: str, acao: str, pasta: Path, area) -> dict:
    p = subprocess.Popen([PY, "-I", str(Path(__file__)), "filho", caso, str(pasta)], cwd=str(RAMO),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    achadas: list = []
    parar = threading.Event()
    v = threading.Thread(target=_vigia, args=(area, acao, achadas, parar), daemon=True)
    v.start()
    try:
        saida, erro = p.communicate(timeout=90)
    except subprocess.TimeoutExpired:
        p.kill()
        saida, erro = p.communicate()
        erro = "PASSOU DE 90 s\n" + erro
    parar.set()
    v.join(10)
    linhas = [l for l in saida.splitlines() if l.startswith("RESULTADO ")]
    r = json.loads(linhas[-1][10:]) if linhas else {"caso": caso, "abertura": pasta.name,
                                                      "sem resultado (o processo morreu?)": erro[-1500:],
                                                      "código de saída": p.returncode}
    r["a vigia (a caixa lida do Windows)"] = achadas
    return r


def main() -> None:
    if BASE.exists():
        shutil.rmtree(BASE)
    area = u32.CreateDesktopW(NOME_DA_AREA, None, None, 0, GENERIC_ALL, None)
    assert area, ctypes.get_last_error()
    roteiro = [("fundo", "ok", "FUNDO", "a1"),
               ("reprovada", "matar", "MATAR", "a1"), ("reprovada", "ok", "MATAR", "a2"),
               ("reprovada", "ok", "MATAR", "a3"),
               ("reprovada", "fechar_x", "FECHAR_X", "a1"), ("reprovada", "ok", "FECHAR_X", "a2"),
               ("reprovada", "espera", "ESPERA", "a1")]
    res = []
    try:
        for caso, acao, grupo, abertura in roteiro:
            pasta = BASE / grupo / abertura
            for sub in ("ProgramData", "LocalAppData"):
                (BASE / grupo / sub).mkdir(parents=True, exist_ok=True)
            res.append({"grupo": grupo, "ação da vigia": acao, **rodar(caso, acao, pasta, area)})
    finally:
        u32.CloseDesktop(area)
    texto = json.dumps(res, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_caixa-resultado.txt").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) == 4 and sys.argv[1] == "filho":
        filho(sys.argv[2], Path(sys.argv[3]))
    else:
        main()
