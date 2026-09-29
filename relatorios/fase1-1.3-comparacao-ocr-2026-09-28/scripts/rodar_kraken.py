"""Kraken no item 1.3: segmentador de linhas de base (blla), no WSL (Ubuntu).

O Kraken nao roda no Windows nem no Python 3.14: roda no WSL, num ambiente
proprio com Python 3.13 (/root/ocr-kraken/.venv, montado com o uv). Uso:

    wsl -d Ubuntu -u root -- bash -c "cd /mnt/d/programas/EditorImpressao/relatorios/fase1-1.3-comparacao-ocr-2026-09-28/scripts && /root/ocr-kraken/.venv/bin/python rodar_kraken.py [pagina ...]"

- K1  kraken.blla.segment com o modelo padrao blla.mlmodel (vem no pacote,
      Apache-2.0), no PROCESSADOR (device='cpu'): o notebook do Kaique nao tem
      placa de video NVIDIA, entao a placa do PC do Samuel nao entra na conta.

Cada linha sai com o contorno (boundary) que o Kraken calcula em volta da
linha de base. Mesmo formato de saida dos outros detectores (comum.gravar_linhas),
mas este script nao importa o comum.py, porque o ambiente do WSL nao tem as
mesmas bibliotecas; as pastas sao as mesmas, vistas por /mnt/d.

Tempo: RODADAS rodadas por pagina (padrao 3), mediana, com o modelo ja carregado.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from kraken import blla
from kraken.lib import vgsl

# No WSL a pasta e vista por /mnt/d; no Windows (medicao extra K1w, Python 3.12
# separado do pesquisador) passa-se OCR13_TRABALHO e OCR13_DETECTOR=K1w.
TRABALHO = Path(os.environ.get("OCR13_TRABALHO", "/mnt/d/programas/EditorImpressao/saida_teste/ocr-1.3"))
DETECTOR = os.environ.get("OCR13_DETECTOR", "K1")
PAGINAS = [
    "palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010",
    "escola_p007", "horas_p011", "horas_p013", "horas_p047",
    "opusmajus_p011", "opusmajus_p003", "opusmajus_p020", "opusmajus_p165",
    "opusmajus_p256", "horas_p026", "horas_p027", "escola_p035",
    "rhetorica_p018", "siebmacher_p009", "palatino_p057",
    "graduale_p221", "graduale_p222", "graduale_p223",
]
RODADAS = int(os.environ.get("RODADAS", "3"))


def main(paginas: list[str]) -> None:
    import kraken
    caminho_modelo = Path(kraken.__file__).parent / "blla.mlmodel"
    t0 = time.perf_counter()
    modelo = vgsl.TorchVGSLModel.load_model(str(caminho_modelo))
    carga = time.perf_counter() - t0
    print("threads do torch:", torch.get_num_threads(), "carga do modelo:", round(carga, 2), "s", flush=True)
    pasta = TRABALHO / "linhas" / DETECTOR
    pasta.mkdir(parents=True, exist_ok=True)
    for pagina in paginas:
        im = Image.open(TRABALHO / "imagens" / f"{pagina}.png").convert("RGB")
        tempos = []
        seg = None
        for _ in range(RODADAS):
            t0 = time.perf_counter()
            seg = blla.segment(im, model=modelo, device="cpu")
            tempos.append(time.perf_counter() - t0)
        linhas = []
        for ln in seg.lines:
            contorno = ln.boundary or []
            if len(contorno) >= 3:
                linhas.append({"poligono": [[float(x), float(y)] for x, y in contorno],
                               "linha_de_base": [[float(x), float(y)] for x, y in (ln.baseline or [])]})
        regioes = {k: len(v) for k, v in (seg.regions or {}).items()}
        dados = {"detector": DETECTOR, "sistema": sys.platform, "pagina": pagina, "linhas": linhas, "tempos_s": tempos,
                 "tempo_mediana_s": float(np.median(tempos)), "modelo": "blla.mlmodel (kraken 7.1.1)",
                 "carga_modelo_s": carga, "threads": torch.get_num_threads(), "regioes": regioes,
                 "linhas_sem_contorno": len(seg.lines) - len(linhas)}  # o Kraken nao conseguiu o contorno (Polygonizer failed)
        (pasta / f"{pagina}.json").write_text(json.dumps(dados), encoding="utf-8")
        print(f"{DETECTOR} {pagina:16s} {len(linhas):4d} linhas {np.median(tempos):7.2f} s  regioes {regioes}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or PAGINAS)
