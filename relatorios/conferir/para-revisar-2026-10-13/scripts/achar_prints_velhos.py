"""Acha prints da janela principal que sairam VELHOS (o Windows devolveu a imagem antiga da
janela: aparece a tela inicial e uma faixa preta a direita)."""
from pathlib import Path
import numpy as np
from PIL import Image
PR = Path(__file__).resolve().parent.parent / "trabalho" / "prints"
velhos, bons = [], []
for p in sorted(PR.glob("*.png")):
    im = np.asarray(Image.open(p).convert("L"))
    if im.shape[1] < 1500 or "perto" in p.name:
        continue
    faixa = im[60:-10, im.shape[1] - 60:]
    (velhos if faixa.max() < 12 else bons).append(p.name)
print("VELHOS (%d):" % len(velhos)); [print("  ", n) for n in velhos]
print("bons:", len(bons))
