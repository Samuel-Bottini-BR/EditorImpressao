"""Quadrados na capa (13/11/2026): o Preto e branco de fabrica de UMA versao do programa na pagina
inteira (sem marcacao nenhuma: e o que a pagina recebe com "Respeitar as gravuras achadas"
desmarcada, D-586), para achar a versao em que os retangulos brancos comecaram (13-01).

    python pb_da_versao.py <raiz da versao> <livro.pdf> <pagina 1-based> <saida.png> [dpi]

Grava a imagem e escreve uma linha JSON: preto na capa (metade da direita) e "quadros" (a fracao
da capa em quadradinhos brancos: blocos de pelo menos 1/40 do lado da pagina, todos brancos,
DENTRO da capa azul, onde o original nao e papel claro)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
SAIDA = Path(sys.argv[4]).resolve()
DADOS = Path(__file__).resolve().parents[1] / "_trabalho" / "dados" / "pb_versao"
(DADOS / "temp").mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(DADOS)
os.environ["TEMP"] = os.environ["TMP"] = str(DADOS / "temp")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)
try:
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:  # noqa: BLE001
    pass

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import filtros as F  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402


def main() -> None:
    pdf, numero = sys.argv[2], int(sys.argv[3])
    dpi = int(sys.argv[5]) if len(sys.argv) > 5 else 300
    doc = abrir_pdf(pdf)
    try:
        img = pagina_para_array(doc, numero - 1, dpi=dpi)
    finally:
        doc.close()
    saida = F.filtro_preto_e_branco(img)
    if saida.ndim == 3:
        saida = saida[:, :, 0]
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(SAIDA), saida)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    h, w = cinza.shape
    nao_papel = cinza < 0.8 * float(np.percentile(cinza, 95))     # a capa azul, nao o papel
    branco = saida >= 128
    # branco "liso" onde o original nao e papel: abertura com um quadrado de 1/40 do lado
    lado = max(3, min(h, w) // 40)
    liso = cv2.morphologyEx(branco.astype(np.uint8), cv2.MORPH_OPEN,
                            np.ones((lado, lado), np.uint8)) > 0
    capa = np.zeros_like(branco)
    capa[:, w // 2 + w // 50: w - w // 30] = True
    alvo = capa & nao_papel
    print(json.dumps({"raiz": RAIZ.name, "preto_na_capa": round(float((~branco)[capa].mean()), 4),
                      "branco_liso_na_capa_azul": round(float(liso[alvo].mean()), 4)}), flush=True)


if __name__ == "__main__":
    main()
