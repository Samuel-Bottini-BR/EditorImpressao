"""Separa as tres perguntas de core.filtros._limpar_o_papel_de_verdade dentro da gravura
da pagina 13 (original no tamanho do PDF): 'longe da letra', 'nao escuro', 'cor de papel'.
Diz quanto da gravura cada uma deixa passar e se a borda dela cai na grade do JPEG."""
import sys
from pathlib import Path

sys.path.insert(0, r"D:\programas\EditorImpressao\.claude\worktrees\obra-juncao")
import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import filtros as F  # noqa: E402

orig = cv2.imread(sys.argv[1])
caixa = [float(v) for v in sys.argv[2].split(",")]
grade = int(sys.argv[3])
h, w = orig.shape[:2]
x0, y0, x1, y1 = int(caixa[0] * w), int(caixa[1] * h), int(caixa[2] * w), int(caixa[3] * h)

capturado = {}
_pintar = F._pintar_de_branco


def espiar(img, mascara):
    capturado["papel_limpo"] = mascara.copy()
    return _pintar(img, mascara)


F._pintar_de_branco = espiar
F._limpar_o_papel_de_verdade(orig, orig.copy())
papel = capturado["papel_limpo"]

cinza = F._para_cinza(orig)
escuro = cinza < F._percentil(cinza, F.BRANCO_PERCENTIL) * F.ESCURO_DEMAIS_PARA_SER_MANCHA
hsv = cv2.cvtColor(orig, cv2.COLOR_BGR2HSV)
matiz = hsv[:, :, 0].astype(np.float32)
cor = (hsv[:, :, 1] <= F.SATURACAO_DE_GRAO) | ((matiz >= F.MATIZ_DE_PAPEL_MIN) & (
    matiz <= F.MATIZ_DE_PAPEL_MAX) & (hsv[:, :, 1] < F.SATURACAO_DE_RUBRICA))


def na_grade(m):
    m = m[y0:y1, x0:x1].astype(np.int8)
    c = np.nonzero(np.diff(m, axis=1))[1] + 1 + x0
    l = np.nonzero(np.diff(m, axis=0))[0] + 1 + y0
    f = lambda v: float((((v % grade) <= 1) | ((v % grade) >= grade - 1)).mean()) if v.size else 0
    return round(100 * (f(c) + f(l)) / 2, 1)


def pct(m):
    return round(100 * float(m[y0:y1, x0:x1].mean()), 1)


print("vai a branco (papel_limpo):", pct(papel), "% da gravura; bordas na grade", na_grade(papel), "%")
print("nao escuro:", pct(~escuro), "%; bordas na grade", na_grade(~escuro), "%")
print("cor de papel:", pct(cor), "%; bordas na grade", na_grade(cor), "%")
print("ao acaso:", round(100 * 3 / grade, 1), "%")
# a saturacao dentro de cada bloco de 'grade' pontos: quanto varia dentro x entre blocos
s = hsv[y0:y1, x0:x1, 1].astype(np.float32)
hh, ww = (s.shape[0] // grade) * grade, (s.shape[1] // grade) * grade
b = s[:hh, :ww].reshape(hh // grade, grade, ww // grade, grade)
dentro = float(b.std(axis=(1, 3)).mean())
entre = float(b.mean(axis=(1, 3)).std())
print(f"saturacao: desvio dentro do bloco {dentro:.1f}, entre blocos {entre:.1f}")
# mesmo com a grade deslocada meio bloco (controle)
m = grade // 2
b2 = s[m:m + hh - grade, m:m + ww - grade].reshape((hh - grade) // grade, grade, (ww - grade) // grade, grade)
print(f"controle (grade deslocada): dentro {float(b2.std(axis=(1, 3)).mean()):.1f}")
cv2.imwrite(str(Path(sys.argv[1]).with_name("mascara_papel_limpo.png")), (papel * 255).astype(np.uint8))
cv2.imwrite(str(Path(sys.argv[1]).with_name("mascara_cor_de_papel.png")), (cor * 255).astype(np.uint8))
