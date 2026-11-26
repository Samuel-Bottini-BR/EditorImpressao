"""Volta 5 (25/11/2026), D-868: a versão reprovada mostra a caixa do Windows DE VERDADE e depois o programa abre.
EXECUTADO no Windows, numa área de trabalho separada (nada na tela do Samuel).

Pergunta: a versão nova não passa no teste rápido. Aparece a caixa do próprio Windows (`MessageBoxW`, pela peça
`core.windows.mostrar_caixa_do_windows`) com "A versão nova não funcionou. Não desinstale nada. Avise o Samuel.", e só
DEPOIS do OK o programa tenta abrir? Com a janela da versão que nem abre (o G1 do quarto) e com a que abre. E a
abertura seguinte? E se não houver área de trabalho à vista?

Como (cada abertura num processo à parte, como o programa):
- o processo da prova cria uma área de trabalho só dela (`CreateDesktopW`, "EditorProvaVolta5"), que ninguém vê;
- o processo filho (o "programa") entra nela logo ao começar (`SetThreadDesktop`, antes de qualquer janela) e roda o
  executor de verdade (`atualizacao.Atualizacao`, a regra, o disco), a peça do Windows de verdade para a caixa, e o
  `main.main()` de verdade com o Qt fora da tela (`offscreen`: o Qt não é o que se prova aqui);
- um fio da prova, também dentro da área de trabalho separada, procura a caixa do processo filho, lê o título e o
  texto da própria caixa (as palavras que o Windows mostrou), tira um print dela (`PrintWindow`) e clica OK
  (`WM_COMMAND` com o botão da caixa).
De mentira: o teste rápido (devolve "não passou"), a peça do Velopack (só anota: nada é pedido), a lista de processos;
no caso A, a janela principal quebrada de propósito (o import dela falha, como numa versão que perdeu uma peça); a caixa
de sempre do programa ("Um momento") é anotada em vez de mostrada (é do Qt, fora da tela).
O PROGRAMDATA e o LOCALAPPDATA trocados DENTRO do Python do filho e conferidos com `assert` antes de tudo.

Casos: A (a janela da versão não abre) e a abertura seguinte; B (a janela abre); C (sem área de trabalho à vista: o
filho cria uma estação de janelas própria, que não tem tela, e a abertura seguinte, na área de trabalho de prova).
Uso: python prova_caixa_de_verdade.py
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

RAMO = Path(__file__).resolve().parents[3]
BASE = RAMO / "saida_teste" / "v5" / "caixa"
AQUI = Path(__file__).resolve().parent
PY = sys.executable
NOME_DA_AREA = "EditorProvaVolta5"
GENERIC_ALL = 0x10000000

u32 = ctypes.WinDLL("user32", use_last_error=True)
g32 = ctypes.WinDLL("gdi32", use_last_error=True)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
ENUM = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
u32.CreateDesktopW.restype = wintypes.HANDLE
u32.CreateDesktopW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                               ctypes.c_void_p]
u32.OpenDesktopW.restype = wintypes.HANDLE
u32.OpenDesktopW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
u32.SetThreadDesktop.argtypes = [wintypes.HANDLE]
u32.SetThreadDesktop.restype = wintypes.BOOL
u32.CloseDesktop.argtypes = [wintypes.HANDLE]
u32.EnumDesktopWindows.argtypes = [wintypes.HANDLE, ENUM, wintypes.LPARAM]
u32.EnumChildWindows.argtypes = [wintypes.HWND, ENUM, wintypes.LPARAM]
u32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
u32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
u32.GetDlgCtrlID.argtypes = [wintypes.HWND]
u32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
u32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
u32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
u32.GetDC.argtypes = [wintypes.HWND]
u32.GetDC.restype = wintypes.HDC
u32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
u32.CreateWindowStationW.restype = wintypes.HANDLE
u32.CreateWindowStationW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p]
u32.SetProcessWindowStation.argtypes = [wintypes.HANDLE]
g32.CreateCompatibleDC.argtypes = [wintypes.HDC]
g32.CreateCompatibleDC.restype = wintypes.HDC
g32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
g32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
g32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
g32.SelectObject.restype = wintypes.HGDIOBJ
g32.GetDIBits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT, ctypes.c_void_p,
                          ctypes.c_void_p, wintypes.UINT]
g32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
g32.DeleteDC.argtypes = [wintypes.HDC]


def _texto(hwnd, funcao) -> str:
    b = ctypes.create_unicode_buffer(1024)
    funcao(hwnd, b, 1024)
    return b.value


def _print(hwnd, destino: Path) -> str:
    """Tira o print da caixa (PrintWindow manda a própria caixa se desenhar num quadro nosso) e grava em PNG."""
    from PIL import Image

    r = wintypes.RECT()
    u32.GetWindowRect(hwnd, ctypes.byref(r))
    w, h = r.right - r.left, r.bottom - r.top
    tela = u32.GetDC(None)
    dc = g32.CreateCompatibleDC(tela)
    bmp = g32.CreateCompatibleBitmap(tela, w, h)
    velho = g32.SelectObject(dc, bmp)
    ok = u32.PrintWindow(hwnd, dc, 0)

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
                    ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                    ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG),
                    ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD),
                    ("biClrImportant", wintypes.DWORD)]

    cab = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
    dados = ctypes.create_string_buffer(w * h * 4)
    g32.GetDIBits(dc, bmp, 0, h, dados, ctypes.byref(cab), 0)
    g32.SelectObject(dc, velho)
    g32.DeleteObject(bmp)
    g32.DeleteDC(dc)
    u32.ReleaseDC(None, tela)
    Image.frombuffer("RGBA", (w, h), dados, "raw", "BGRA", 0, 1).convert("RGB").save(destino)
    return f"{destino.name} ({w}x{h}, PrintWindow={'ok' if ok else 'falhou'})"


def _vigia(area, pid: int, achadas: list, parar: threading.Event, prefixo: str) -> None:
    """Dentro da área de trabalho separada: acha cada caixa do processo `pid`, lê, tira o print e clica OK."""
    if not u32.SetThreadDesktop(area):
        achadas.append({"erro": f"SetThreadDesktop falhou ({ctypes.get_last_error()})"})
        return
    vistas: set = set()
    while not parar.is_set():
        caixas: list = []

        def cada(hwnd, _):
            dono = wintypes.DWORD()
            u32.GetWindowThreadProcessId(hwnd, ctypes.byref(dono))
            # Qualquer caixa nesta área de trabalho é do programa da prova (só ele roda aqui). Pelo número do processo
            # não dá: o python.exe da .venv abre o Python de verdade num processo filho, com outro número.
            if _texto(hwnd, u32.GetClassNameW) == "#32770" and hwnd not in vistas:
                caixas.append(hwnd)
            return True

        u32.EnumDesktopWindows(area, ENUM(cada), 0)
        for hwnd in caixas:
            time.sleep(0.4)                                   # a caixa termina de se desenhar
            filhos: list = []
            u32.EnumChildWindows(hwnd, ENUM(lambda h, _: filhos.append(h) or True), 0)
            estaticos = [_texto(h, u32.GetWindowTextW) for h in filhos if _texto(h, u32.GetClassNameW) == "Static"]
            botoes = [h for h in filhos if _texto(h, u32.GetClassNameW) == "Button"]
            achada = {"quando": time.time(), "titulo": _texto(hwnd, u32.GetWindowTextW),
                      "texto": [t for t in estaticos if t], "botoes": [_texto(h, u32.GetWindowTextW) for h in botoes]}
            try:
                achada["print"] = _print(hwnd, AQUI / f"{prefixo}-caixa-{len(achadas) + 1}.png")
            except Exception as erro:  # noqa: BLE001
                achada["print"] = f"não deu: {erro}"
            if botoes:
                ident = u32.GetDlgCtrlID(botoes[0])
                u32.PostMessageW(hwnd, 0x0111, ident & 0xFFFF, botoes[0])     # WM_COMMAND, BN_CLICKED do botão
                achada["clicou"] = f"o botão {ident}"
            achada["clicado_em"] = time.time()
            vistas.add(hwnd)
            achadas.append(achada)
        time.sleep(0.2)


def um_caso(caso: str, pasta: Path) -> None:
    """O "programa" (no processo filho): entra na área de trabalho de prova, abre como o programa instalado e conta."""
    linha_do_tempo: list = []
    marca = lambda o_que: linha_do_tempo.append((round(time.time(), 3), o_que))  # noqa: E731
    if caso == "C":
        # Uma estação de janelas própria, sem tela (como um processo de serviço ou de uma conexão de longe).
        estacao = u32.CreateWindowStationW(None, 0, 0x37F, None)  # sem nome; WINSTA_ALL_ACCESS
        assert estacao and u32.SetProcessWindowStation(estacao), ctypes.get_last_error()
        area = u32.CreateDesktopW("Prova", None, None, 0, GENERIC_ALL, None)
    else:
        area = u32.OpenDesktopW(NOME_DA_AREA, 0, False, GENERIC_ALL)
    assert area and u32.SetThreadDesktop(area), ctypes.get_last_error()
    grupo = pasta.parent                       # as aberturas do mesmo grupo dividem a instalação, o estado e a conta
    os.environ["PROGRAMDATA"] = str(grupo / "ProgramData")
    os.environ["LOCALAPPDATA"] = str(grupo / "LocalAppData")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["USERNAME"] = "Kaique"
    sys.path.insert(0, str(RAMO))
    import atualizacao
    import historico
    import versao
    from core import windows
    from tests.ajudante_do_atualizador import PUBLICA, VelopackFalso, WindowsFalso

    assert str(atualizacao.pasta_do_estado()).startswith(str(BASE)), atualizacao.pasta_do_estado()
    assert str(historico.pasta_de_dados()).startswith(str(BASE)), historico.pasta_de_dados()
    versao.VERSAO = "1.2.0"
    raiz = grupo / "raiz"
    (raiz / "current").mkdir(parents=True, exist_ok=True)
    (raiz / "Update.exe").write_bytes(b"MZ")
    (raiz / "packages").mkdir(exist_ok=True)
    (raiz / "packages" / atualizacao.nome_do_pacote("1.2.0")).write_bytes(b"o pacote da 1.2.0 (chegou pela troca)")

    class WindowsDaProva(WindowsFalso):
        """A caixa do Windows de VERDADE (a peça); o resto, de mentira."""

        def mostrar_caixa_do_windows(self, titulo, texto):
            marca("a caixa do Windows vai aparecer")
            r = windows.mostrar_caixa_do_windows(titulo, texto)
            marca(f"a caixa do Windows voltou: {r.desfecho} {r.motivo}".strip())
            return r

    testes: list = []
    vp = VelopackFalso(raiz, None, "sem internet", {})
    a = atualizacao.Atualizacao(windows=WindowsDaProva(), velopack=vp, raiz=raiz,
                                fonte=atualizacao.Fonte(str(pasta / "sem-fonte")), por_tras=lambda t: t(),
                                pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                motor_no_lugar=lambda m=None: True,
                                teste=lambda: testes.append(1) or (False, "erro ao abrir: ImportError (de prova)"),
                                chave_publica=PUBLICA)
    marca("o programa abriu (antes da janela)")
    saida = a.abrir(["--conferir-a-versao-nova", "1.1.0", "1.2.0"] if pasta.name == "primeira" else [])
    marca(f"a atualização terminou a abertura: {saida!r} (None = o programa abre a janela)")
    atualizacao._DESTA_ABERTURA = a
    import core.aquecimento
    import core.paginas_em_outro_processo
    import ui.perguntas
    import ui.tela_de_carregamento

    core.aquecimento.aquecer_em_segundo_plano = lambda: None
    core.paginas_em_outro_processo.iniciar_em_segundo_plano = lambda: None
    ui.tela_de_carregamento.abrir_o_brasao = lambda: type("B", (), {"fechar": lambda self: None})()
    caixas_do_programa: list = []
    ui.perguntas.avisar = lambda janela, titulo, texto, **kw: caixas_do_programa.append(f"[{titulo}] {texto}")
    if caso == "A":
        sys.modules["ui.janela_principal"] = None              # a janela desta versão não abre
    else:
        import ui.aviso_de_atualizacao
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication

        original = ui.aviso_de_atualizacao.ligar_na_janela

        def ligar(janela, atual=None):
            marca(f"a janela do programa abriu: {type(janela).__name__}")
            QTimer.singleShot(500, QApplication.instance().quit)
            return original(janela, atual)

        ui.aviso_de_atualizacao.ligar_na_janela = ligar
    import main

    erro = ""
    if saida is None:
        marca("main.main() começa (o programa tenta abrir)")
        try:
            main.main()
        except BaseException:  # noqa: BLE001 - o que o Python faz no topo: chama o excepthook
            tipo, valor, rastro = sys.exc_info()
            erro = f"{tipo.__name__}: {valor}"
            sys.excepthook(tipo, valor, rastro)
    marca("o processo do programa termina")
    print("RESULTADO " + json.dumps({
        "caso": caso, "grupo": pasta.parent.name, "abertura": pasta.name, "testes rápidos rodados": len(testes), "pedidos ao Velopack": vp.nomes(),
        "área de trabalho à vista (a peça leu)": windows.area_de_trabalho_a_vista(),
        "linha do tempo": linha_do_tempo, "o main.main() parou com": erro,
        "caixas do programa (Qt, anotadas)": caixas_do_programa,
        "frases vistas nesta conta": sorted(atualizacao.ler_vistos()),
        "bilhete": atualizacao.ler_estado()}, ensure_ascii=False))


def rodar(caso: str, pasta: Path, area) -> dict:
    """Abre o "programa" num processo à parte e, com ele aberto, a vigia das caixas na área de trabalho de prova."""
    filho = subprocess.Popen([PY, "-I", str(Path(__file__)), "filho", caso, str(pasta)], cwd=str(RAMO),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                             errors="replace")
    achadas: list = []
    parar = threading.Event()
    vigia = threading.Thread(target=_vigia, args=(area, filho.pid, achadas, parar, f"{pasta.parent.name}-{pasta.name}"),
                             daemon=True)
    vigia.start()
    try:
        saida, erro = filho.communicate(timeout=120)
    except subprocess.TimeoutExpired:
        filho.kill()
        saida, erro = filho.communicate()
        erro = "PASSOU DE 120 s (o processo do programa ficou parado)\n" + erro
    parar.set()
    vigia.join(5)
    linhas = [l for l in saida.splitlines() if l.startswith("RESULTADO ")]
    r = json.loads(linhas[-1][10:]) if linhas else {"caso": caso, "falhou": erro[-3000:]}
    r["caixas do Windows achadas na área de trabalho de prova (lidas da própria caixa)"] = achadas
    return r


def main_da_prova() -> None:
    """Os grupos (cada um uma instalação e uma conta de prova) e as aberturas de cada um, na ordem."""
    if BASE.exists():
        shutil.rmtree(BASE)
    area = u32.CreateDesktopW(NOME_DA_AREA, None, None, 0, GENERIC_ALL, None)
    assert area, f"CreateDesktopW falhou ({ctypes.get_last_error()})"
    roteiro = [("A", "A", "primeira"), ("A", "A", "seguinte"),       # a janela da versão não abre
               ("B", "B", "primeira"),                                 # a janela abre
               ("C", "C", "primeira"), ("B", "C", "seguinte")]         # sem área de trabalho à vista; depois, com
    resultado = []
    try:
        for caso, grupo, abertura in roteiro:
            pasta = BASE / grupo / abertura
            for sub in ("ProgramData", "LocalAppData"):
                (BASE / grupo / sub).mkdir(parents=True, exist_ok=True)
            pasta.mkdir(parents=True, exist_ok=True)
            resultado.append(rodar(caso, pasta, area))
    finally:
        u32.CloseDesktop(area)
    texto = json.dumps(resultado, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_caixa_de_verdade-resultado.txt").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) == 4 and sys.argv[1] == "filho":
        um_caso(sys.argv[2], Path(sys.argv[3]))
    else:
        main_da_prova()
