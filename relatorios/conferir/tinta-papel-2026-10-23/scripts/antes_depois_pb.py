"""Verificador tp23, ajuste da resposta 10 (23/10/2026): a letra de perto no Preto e branco,
ANTES (3e95076) x AGORA (d4c820b), em fotos com três colunas.

Usa os PDFs que o `papel.py somas-papel` gravou (mesmas páginas, mesmo caminho, mesmas áreas):
    %TEMP%/vtp23_localappdata/somaspapel-somas-papel-antes-3e95076/<pid>-preto_e_branco-<jeito>.pdf
    %TEMP%/vtp23_localappdata/somaspapel-somas-papel-novo-d4c820b/<pid>-preto_e_branco-<jeito>.pdf
Uso: python antes_depois_pb.py <pasta de saída>
"""
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[3] / "relatorios" / "fase2-novas" / "scripts"))
import antes_depois as ad  # noqa: E402
import papel  # noqa: E402

DADOS = Path(tempfile.gettempdir()) / "vtp23_localappdata"
ANTES = DADOS / "somaspapel-somas-papel-antes-3e95076"
AGORA = DADOS / "somaspapel-somas-papel-novo-d4c820b"
CAMINHO = ("Caminho: livro novo, ajustes de fábrica (girar 0, dividir não, endireitar sim, cortar as bordas sim), "
           "filtro Preto e branco, e a área \"manter a cor da tinta\" marcada à mão")
LARG = 620


def img(pasta, pid, jeito):
    return papel._guardada(pasta / f"{pid}-preto_e_branco-{jeito}.pdf")[0]


def main():
    saida = Path(sys.argv[1])
    saida.mkdir(parents=True, exist_ok=True)
    areas = papel._areas()
    for pid, nome in papel.PAGINAS.items():
        area = areas[pid]
        Ab = img(AGORA, pid, "Ab")
        h, w = Ab.shape[:2]
        x0, y0, x1, y1 = int(area[0] * w), int(area[1] * h), int(area[2] * w), int(area[3] * h)
        ys, xs = np.nonzero(np.any(Ab[y0:y1, x0:x1] != 255, axis=2))
        cx, cy = (int(np.median(xs)) + x0, int(np.median(ys)) + y0) if len(xs) else ((x0 + x1) // 2, (y0 + y1) // 2)
        # um pedaço pequeno (160 x 110 pontos da imagem) em volta do meio da letra, ampliado ~4 vezes
        pa = slice(max(0, cy - 55), cy + 55), slice(max(0, cx - 80), cx + 80)
        linhas = []
        for letra, cor in (("A", "\"cor como no livro\""), ("B", "\"cor escurecida\"")):
            ant_p, ago_p, ago_b = img(ANTES, pid, letra + "p"), img(AGORA, pid, letra + "p"), img(AGORA, pid, letra + "b")
            ant_b = img(ANTES, pid, letra + "b")
            iguais = np.array_equal(ago_p, ago_b)
            branco_igual = np.array_equal(ant_b, ago_b)
            cols = []
            for titulo, im in ((f"1. ANTES: {letra} + papel como o resto da página", ant_p),
                               (f"2. AGORA: {letra} + papel como o resto da página", ago_p),
                               (f"3. {letra} + papel branco (o de fábrica)", ago_b)):
                ped = im[pa]
                f = LARG / ped.shape[1]
                ped = cv2.resize(ped, (LARG, int(ped.shape[0] * f)), interpolation=cv2.INTER_NEAREST)
                cols.append(ad._faixa(ped, [titulo]))
            alt = max(c.shape[0] for c in cols)
            cols = [cv2.copyMakeBorder(c, 0, alt - c.shape[0], 0, 16, cv2.BORDER_CONSTANT, value=(255, 255, 255)) for c in cols]
            linha = np.hstack(cols)
            linhas.append(ad._faixa(linha, [f"Cor da tinta {cor} ({letra}). Coluna 2 igual à coluna 3 ponto por ponto: "
                                            f"{'sim' if iguais else 'NÃO'}. Coluna 3 igual à de antes: {'sim' if branco_igual else 'NÃO'}."]))
        corpo = np.vstack([cv2.copyMakeBorder(x, 0, 24, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255)) for x in linhas])
        lg = corpo.shape[1]
        cab = [f"{nome}, Preto e branco: a letra de perto (ampliada {LARG / (pa[1].stop - pa[1].start):.1f} vezes), antes e agora",
               "Coluna 1: como era antes do ajuste (código 3e95076), com \"papel como o resto da página\": o contorno preto em volta da letra.",
               "Coluna 2: como fica agora (código d4c820b), com \"papel como o resto da página\": sem o contorno.",
               "Coluna 3: \"papel branco\", o de fábrica, que não mudou. Pela sua resposta 10, a coluna 2 tem de sair igual à 3."]
        cab += ad._quebrar(CAMINHO + f" em {tuple(round(v, 2) for v in area)}.", lg)
        final = ad._faixa(corpo, cab)
        destino = saida / f"d4c_{pid}-pb-letra-antes-e-agora.jpg"
        cv2.imwrite(str(destino), final, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(destino.name, final.shape, flush=True)


if __name__ == "__main__":
    main()
