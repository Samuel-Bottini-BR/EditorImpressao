"""D3, segunda parte: QUEM ACERTOU o angulo, onde o nosso e o ScanTailor discordam.

Uma terceira medida, que nao e nem a do nosso (perfil de projecao da pagina
inteira) nem a do ScanTailor (perfil de projecao com cisalhamento): as linhas
de texto, uma a uma. Cada linha de texto da pagina (as letras emendadas na
horizontal) vira uma "faixa" comprida; a inclinacao de cada faixa e medida
pela reta que passa pelo meio da tinta de cada coluna dela; vale a mediana das
faixas (pesada pelo comprimento). Medida na folha COMO VEIO, ela diz quanto a
pagina esta torta de verdade; o angulo certo para endireitar e esse, com o
sinal trocado. Medida na pagina ja endireitada, ela diz quanto ficou torto.

Tambem grava, para cada pagina, a "faixa esticada": um pedaco do texto da
pagina endireitada por cada programa, esticado 5 vezes na altura. Esticar so
na altura aumenta a inclinacao 5 vezes: meio grau vira dois graus e meio, e da
para ver a olho, contra as linhas-guia.

Rodar da raiz do projeto, depois do comparar_d3.py:

    .venv\\Scripts\\python.exe relatorios\\fase2-geometria-d3-2026-10-05\\scripts\\medir_torto.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comparar_d3 as c  # noqa: E402

# Paginas em que os dois discordam em 0,2 grau ou mais (do medidas.json), mais
# duas em que concordam, de controle.
PAGINAS = ["horas_p011", "horas_p047", "horas_p027", "horas_p014", "opusmajus_p020",
           "palatino_p057", "siebmacher_p009", "escola_p007", "graduale_p221", "escola_p035"]


def inclinacao_das_linhas(img: np.ndarray) -> tuple[float | None, int]:
    """Graus (sentido do OpenCV: positivo = a linha sobe para a direita na
    tela... ver o sinal abaixo) e quantas linhas de texto foram usadas.

    Devolve o angulo que a pagina TEM. Para endireitar, gira-se o contrario.
    """
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = cinza.shape
    escala = 1600.0 / max(h, w)
    if escala < 1:
        cinza = cv2.resize(cinza, (int(w * escala), int(h * escala)), interpolation=cv2.INTER_AREA)
        h, w = cinza.shape
    tinta = cv2.adaptiveThreshold(cinza, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,
                                  31, 18)
    # emendar as letras de uma linha, sem emendar uma linha na outra
    nucleo = cv2.getStructuringElement(cv2.MORPH_RECT, (max(9, w // 60), 1))
    linhas = cv2.morphologyEx(tinta, cv2.MORPH_CLOSE, nucleo)
    n, rotulos, caixas, _ = cv2.connectedComponentsWithStats(linhas, 8)
    angulos, pesos = [], []
    for i in range(1, n):
        x, y, cw, ch, area = caixas[i]
        if cw < 0.12 * w or ch > 0.06 * h or ch < 4 or cw < 6 * ch:
            continue
        sub = (rotulos[y:y + ch, x:x + cw] == i) & (tinta[y:y + ch, x:x + cw] > 0)
        colunas = np.flatnonzero(sub.any(axis=0))
        if len(colunas) < 0.5 * cw:
            continue
        ys = np.array([np.mean(np.flatnonzero(sub[:, k])) for k in colunas])
        inclinacao = np.polyfit(colunas.astype(float), ys, 1)[0]
        angulos.append(np.degrees(np.arctan(inclinacao)))
        pesos.append(cw)
    if len(angulos) < 3:
        return None, len(angulos)
    ordem = np.argsort(angulos)
    a, p = np.asarray(angulos)[ordem], np.asarray(pesos, float)[ordem]
    acumulado = np.cumsum(p)
    mediana = float(a[np.searchsorted(acumulado, acumulado[-1] / 2.0)])
    # y cresce para baixo: inclinacao positiva = a linha DESCE para a direita,
    # que e uma pagina girada no sentido horario; o OpenCV endireita com +.
    return mediana, len(angulos)


def faixa_esticada(img: np.ndarray, largura: int = 1100, vezes: int = 5) -> np.ndarray:
    """O miolo de texto da pagina (40% a 60% da altura), esticado na altura."""
    h, w = img.shape[:2]
    faixa = img[int(h * 0.40):int(h * 0.60)]
    faixa = cv2.resize(faixa, (largura, int(faixa.shape[0] * largura / faixa.shape[1])),
                       interpolation=cv2.INTER_AREA)
    faixa = cv2.resize(faixa, (largura, min(900, faixa.shape[0] * vezes)), interpolation=cv2.INTER_CUBIC)
    if faixa.ndim == 2:
        faixa = cv2.cvtColor(faixa, cv2.COLOR_GRAY2BGR)
    for k in range(1, 12):
        y = int(k * faixa.shape[0] / 12)
        cv2.line(faixa, (0, y), (largura - 1, y), (200, 170, 0), 2, cv2.LINE_AA)
    return faixa


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    fator, _ = c.fator_do_sentido()
    medidas = json.loads((c.PASTA / "dados" / "medidas.json").read_text(encoding="utf-8"))
    lista = json.loads((c.RAIZ / "gabarito" / "lista.json").read_text(encoding="utf-8"))
    saida = {}
    for nome in PAGINAS:
        print("...", nome, flush=True)
        nosso = c.nossa_geometria(nome, lista["paginas"][nome])
        st = c.scantailor(nosso["img"], nome, fator)
        # a folha como veio, na mesma area: a primeira pagina de cada um
        original, n0 = inclinacao_das_linhas(nosso["img"] if not nosso["dividir"]
                                             else nosso["paginas"][0]["final"])
        r_nosso, n1 = inclinacao_das_linhas(nosso["paginas"][0]["final"])
        r_st, n2 = inclinacao_das_linhas(st["subs"][0]["final"])
        linha = {
            "torto_no_original": None if original is None else round(original, 2),
            "angulo_certo_estimado": None if original is None else round(original, 2),
            "nosso_angulo": medidas["paginas"][nome]["nosso_angulos"][0],
            "st_angulo": medidas["paginas"][nome]["st_angulos"][0],
            "sobra_torta_nosso": None if r_nosso is None else round(r_nosso, 2),
            "sobra_torta_st": None if r_st is None else round(r_st, 2),
            "linhas_usadas": [n0, n1, n2],
        }
        saida[nome] = linha
        print("   ", json.dumps(linha), flush=True)
        cima = c._titulo(faixa_esticada(nosso["paginas"][0]["final"]),
                         f"NOSSO ({linha['nosso_angulo']:+.2f} graus): ficou torto {linha['sobra_torta_nosso']}",
                         c.AZUL)
        baixo = c._titulo(faixa_esticada(st["subs"][0]["final"]),
                          f"SCANTAILOR ({linha['st_angulo']:+.2f} graus): ficou torto {linha['sobra_torta_st']}",
                          c.VERMELHO)
        cv2.imwrite(str(c.IMAGENS / f"esticada_{nome}.jpg"), c._empilhar([cima, baixo], 16),
                    [cv2.IMWRITE_JPEG_QUALITY, 85])
        del nosso, st
    (c.PASTA / "dados" / "torto.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1),
                                                  encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
