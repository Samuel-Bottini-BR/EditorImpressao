"""Monta as fotos da conferência da etapa 9d (antes | agora, lado a lado, com
o título de cada lado), a partir das imagens que os scripts gravaram:
  - item 4: folha_em_branco_sem_fundo.py (--saida _tmp/item4/antes e .../depois);
  - D-532: gravura_escura.py (--saida _tmp/d532).
USO (da pasta da worktree): python relatorios/obra-etapa9d/scripts/fazer_imagens.py
Grava relatorios/obra-etapa9d/conferencia/img/*.jpg (até ~300 KB cada).
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parents[3]
TMP = RAIZ / "_tmp"
IMG = RAIZ / "relatorios" / "obra-etapa9d" / "conferencia" / "img"


def _titulo(img: np.ndarray, texto: str) -> np.ndarray:
    faixa = np.full((44, img.shape[1], 3), 255, np.uint8)
    cv2.putText(faixa, texto, (10, 31), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
    return np.vstack([faixa, img])


def lado_a_lado(a: Path, b: Path, ta: str, tb: str, destino: Path, altura: int = 900) -> None:
    ia, ib = cv2.imread(str(a)), cv2.imread(str(b))
    if ia is None or ib is None:
        print("faltou", a, b)
        return
    f = altura / ia.shape[0]
    ia = cv2.resize(ia, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    ib = cv2.resize(ib, (ia.shape[1], ia.shape[0]), interpolation=cv2.INTER_AREA)
    juntas = np.hstack([_titulo(ia, ta), np.full((ia.shape[0] + 44, 12, 3), 128, np.uint8),
                        _titulo(ib, tb)])
    destino.parent.mkdir(parents=True, exist_ok=True)
    for q in (88, 80, 72, 64, 56, 48):
        cv2.imwrite(str(destino), juntas, [cv2.IMWRITE_JPEG_QUALITY, q])
        if destino.stat().st_size <= 300_000:
            break
    print(destino.name, destino.stat().st_size // 1000, "KB")


def main() -> None:
    for pid in ("opusmajus_p011", "opusmajus_p003", "palatino_p005"):
        for nome in ("folha-em-branco", "pintar"):
            lado_a_lado(TMP / "item4" / "antes" / f"{pid}-{nome}.png",
                        TMP / "item4" / "depois" / f"{pid}-{nome}.png",
                        "ANTES (programa de hoje)", "AGORA (etapa 9d)",
                        IMG / f"item4-{pid}-{nome}.jpg")
    for nome in ("palatino74", "palatino70", "righetti62", "righetti64",
                 "palatino5", "valades41", "palatino69", "pesel51"):
        lado_a_lado(TMP / "d532" / f"{nome}-inteira-hoje.png",
                    TMP / "d532" / f"{nome}-inteira-ligada.png",
                    "HOJE (conta desligada, de fabrica)", "COM A CONTA LIGADA",
                    IMG / f"d532-{nome}.jpg", altura=760)


if __name__ == "__main__":
    main()
