"""Mede o pico de memória das caixas do ScanTailor, uma página por processo.

O QUE FAZ
    Para cada (página, DPI) da lista, abre um processo filho que carrega a
    página, chama core.caixas_scantailor.achar() uma vez e diz o pico de
    memória do processo (PeakWorkingSetSize do Windows) antes e depois da
    chamada. A diferença é o que a conta do ScanTailor pediu a mais.
    Serve para escolher a trava PONTOS_MAXIMOS_A_150 de
    core/caixas_scantailor.py. Grava
    relatorios/caixa-conteudo-impl/dados/memoria.json.

    Um processo por vez. Não muda o programa nem as páginas.

COMO RODAR (da raiz da worktree, com a .venv da pasta principal)
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\caixa-conteudo-impl\\scripts\\medir_memoria.py

SEGURO MUDAR: a lista CASOS. ARRISCADO: pôr um caso muito acima de 16 milhões
de pontos a 150 DPI com o PC ocupado (é o que a trava existe para impedir).
"""

from __future__ import annotations

import ctypes
import json
import subprocess
import sys
from ctypes import wintypes
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# (página do arquivo do pesquisador, DPI dito à DLL). O DPI menor que o de
# verdade amplia a página: é assim que se chega perto da trava.
CASOS = [
    ("palatino_p005", 400),      # página comum, 0,8 milhão de pontos a 150 DPI
    ("escola_p035", 200),        # 1,8 milhão
    ("egenloff_p047", 150),      # 5,7 milhões
    ("horas_p014", 72),          # 6,7 milhões (ampliada 2 vezes)
    ("antiphon_p088", 150),      # 10,3 milhões (a maior medida pelo pesquisador)
    ("antiphon_p088", 125),      # 14,8 milhões (perto da trava)
]


class _Contadores(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


def _pico_em_mb() -> tuple[float, float]:
    """(pico da memória em uso, pico da memória reservada) deste processo, em MB."""
    c = _Contadores()
    c.cb = ctypes.sizeof(c)
    kernel32 = ctypes.WinDLL("kernel32")
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL("psapi")
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(_Contadores), wintypes.DWORD]
    psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(), ctypes.byref(c), c.cb)
    return c.PeakWorkingSetSize / 2**20, c.PeakPagefileUsage / 2**20


def filho(nome: str, dpi: int) -> None:
    from medir import DADOS_DO_PESQUISADOR, carregar

    from core import caixas_scantailor as cs

    esperado = json.loads(DADOS_DO_PESQUISADOR.read_text(encoding="utf-8"))["paginas"][nome]
    img = carregar(esperado["fonte"])
    if img is None:
        print(json.dumps({"faltou": True}))
        return
    # Abre a DLL (e o Qt) antes de medir, com uma folha pequena.
    import numpy as np

    cs.achar(np.full((200, 200), 235, np.uint8), 150)
    antes, reservada_antes = _pico_em_mb()
    r = cs.achar(img, dpi, claro_no_escuro=False)
    depois, reservada_depois = _pico_em_mb()
    altura, largura = img.shape[:2]
    print(json.dumps({
        "disponivel": r.disponivel, "motivo": r.motivo,
        "megapontos_a_150": round(cs.pontos_a_150(largura, altura, dpi, dpi) / 1e6, 2),
        "megapontos_da_imagem": round(largura * altura / 1e6, 2),
        "pico_antes_mb": round(antes), "pico_depois_mb": round(depois),
        "a_mais_mb": round(depois - antes),
        "reservada_a_mais_mb": round(reservada_depois - reservada_antes),
        "segundos": round(r.segundos, 2)}))


def main() -> None:
    if len(sys.argv) == 4 and sys.argv[1] == "--filho":
        filho(sys.argv[2], int(sys.argv[3]))
        return
    medidas = []
    for nome, dpi in CASOS:
        saida = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--filho", nome, str(dpi)],
                               capture_output=True, text=True, cwd=str(RAIZ), timeout=900)
        linhas = [linha for linha in saida.stdout.strip().splitlines() if linha.startswith("{")]
        m = json.loads(linhas[-1]) if linhas else {"erro": saida.stderr[-400:]}
        medidas.append({"pagina": nome, "dpi": dpi, **m})
        print(nome, dpi, m, flush=True)
    destino = PASTA / "dados" / "memoria.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(medidas, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("gravou", destino, flush=True)


if __name__ == "__main__":
    main()
