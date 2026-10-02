r"""Monta as imagens do formulario relatorios/conferir-aqui-6.html (sexta conferencia, 01/10/2026).

Os consertos que o Samuel pediu na conferencia 5 (respostas em
relatorios/conferencia-samuel-2026-10-01.md), cada um com ORIGINAL · ANTES · AGORA e o detalhe.

Uso (no .venv do programa; nao muda o programa, nao processa pagina nenhuma, so desenha):
    .venv\Scripts\python.exe relatorios\conferencia-6-2026-10-01\scripts\montar_imagens.py

Le (somente leitura), so imagens prontas:
- ANTES = a rodada da conferencia 5: relatorios/conferir/pb-mp-decoracao-2026-10-01/depois-pb e
  depois-mp (o programa antes destes consertos);
- AGORA = a rodada dos consertos: relatorios/conferir/conferencia-5-consertos-2026-10-01/depois-pb
  e depois-mp;
- ORIGINAL = gabarito/paginas/<id>.png;
- as beiradas do corte de 1 mm: relatorios/corte-folga-1mm-2026-10-01/bordas/ (so ganham um
  rotulo grande em cima; o titulo pequeno de dentro, que saia cortado, e trocado).

O corte das bordas mudou um pouco entre ANTES e AGORA (folga de 1 mm), entao ORIGINAL e ANTES sao
redesenhados no enquadramento do AGORA pelos pontos em comum (ORB + ECC, alinhar.py da
conferencia 4): o mesmo recorte vale para as tres partes.

Regra do desenho (igual as conferencias 4 e 5): retangulo de destaque com folga, POR FORA do lugar
ampliado; nada desenhado em cima dos detalhes; rotulos em faixas acima de cada parte.

Seguro mudar: recortes, textos, tamanhos. Arriscado: nada (so leitura e desenho).
"""

from __future__ import annotations

import glob
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
SAIDA = AQUI.parent
sys.path.insert(0, str(RAIZ / "relatorios" / "conferencia-4-2026-10-01" / "scripts"))

import montar_imagens as M4  # noqa: E402  (pecas de desenho da conferencia 4)

U, A = M4.U, M4.A
CONF = RAIZ / "relatorios" / "conferir"
PASTA_ANTES = CONF / "pb-mp-decoracao-2026-10-01"
PASTA_AGORA = CONF / "conferencia-5-consertos-2026-10-01"
BORDAS = RAIZ / "relatorios" / "corte-folga-1mm-2026-10-01" / "bordas"
LARGURA = M4.LARGURA
COR = M4.COR_DETALHE
NOME = {"pb": "Preto e branco", "mp": "Mágico pro"}
CINZA_ORIG, MARROM, VERDE = (90, 90, 90), (150, 60, 30), (0, 115, 0)


def _res(pasta: Path, filtro: str, pagina: str) -> np.ndarray:
    return A.ler_rgb(Path(glob.glob(str(pasta / f"depois-{filtro}" / "*" / "resultado" / f"{pagina}.png"))[0]))


_CACHE: dict = {}


def tres(pagina: str, filtro: str) -> list:
    """[(imagem, ROTULO, sub, cor)] de ORIGINAL, ANTES e AGORA, todas no enquadramento do AGORA."""
    chave = (pagina, filtro)
    if chave not in _CACHE:
        agora = _res(PASTA_AGORA, filtro, pagina)
        agora_mp = _res(PASTA_AGORA, "mp", pagina)
        orig = A.original_no_quadro_do_resultado(A.ler_rgb(RAIZ / "gabarito" / "paginas" / f"{pagina}.png"),
                                                 agora_mp, f"{pagina} original")
        antes = A.original_no_quadro_do_resultado(_res(PASTA_ANTES, filtro, pagina), agora, f"{pagina} antes-{filtro}")
        _CACHE[chave] = [(orig, "ORIGINAL", "a página como veio do livro", CINZA_ORIG),
                         (antes, "ANTES", f"{NOME[filtro]}, conferência 5", MARROM),
                         (agora, "AGORA", f"{NOME[filtro]}, com os consertos", VERDE)]
    return _CACHE[chave]


def cartao(nome: str, titulo: str, colunas: list, detalhes: list, alt: int = 880) -> Path:
    """Pagina inteira (com o lugar de cada detalhe marcado por fora) e, embaixo, cada detalhe."""
    n = len(colunas)
    topo = U.lado_a_lado([U.rotulo(M4.pagina_com_folga_marcada(im, detalhes, alt), r, fundo=f, sub=s, tam=38)
                          for im, r, s, f in colunas], por_baixo=True)
    legenda = " · ".join(f"retângulo {M4.NOME_COR[k]} = detalhe {k + 1}" for k in range(len(detalhes)))
    partes = [U.rotulo(topo, titulo, fundo=(30, 42, 54), tam=40,
                       sub=f"Página inteira: {legenda} (o retângulo fica com folga, por fora do lugar ampliado; "
                           "os detalhes não têm nada desenhado por cima)")]
    todos = [[M4.recorte(im, ret) for im, *_ in colunas] for ret in detalhes]
    aspectos = [c[-1].shape[1] / c[-1].shape[0] for c in todos]
    # dois detalhes largos: um ao lado do outro, cada um com as partes empilhadas;
    # um detalhe so: partes empilhadas so se for bem largo (senao, lado a lado)
    em_colunas = len(detalhes) == 2 and all(x >= 1.75 for x in aspectos)
    largos = [x >= (1.75 if em_colunas else 2.2) for x in aspectos]
    larg_bloco = (LARGURA - 24) // 2 if em_colunas else LARGURA
    blocos = []
    for k, crs in enumerate(todos):
        if largos[k]:
            corpo = U.um_embaixo_do_outro([U.rotulo(U.na_largura(c, larg_bloco - 10), r, fundo=f, tam=34)
                                           for c, (_i, r, _s, f) in zip(crs, colunas)], espaco=14)
        else:
            larg = (larg_bloco - 18 * (n - 1)) // n
            corpo = U.lado_a_lado([U.rotulo(U.na_largura(c, larg), r, fundo=f, tam=34)
                                   for c, (_i, r, _s, f) in zip(crs, colunas)], por_baixo=True)
        texto = f"DETALHE {k + 1} (retângulo {M4.NOME_COR[k]}), ampliado" + ("" if em_colunas else ", sem nada desenhado por cima")
        blocos.append(U.rotulo(corpo, texto, fundo=COR[k], tam=32))
    partes += [U.lado_a_lado(blocos, espaco=24)] if em_colunas else blocos
    return U.gravar(U.um_embaixo_do_outro(partes, espaco=26), SAIDA / "cartoes" / f"{nome}.jpg",
                    qualidade=88, largura_max=LARGURA)


# (nome, pagina, filtro, [detalhes em fracao da pagina AGORA], titulo)
CARTOES = [
    ("a2-horas11-mp", "horas_p011", "mp", [(0.36, 0.37, 0.66, 0.48)], "Horas 11 no Mágico pro: o papel dentro e em volta das letras douradas"),
    ("a2-horas11-pb", "horas_p011", "pb", [(0.36, 0.37, 0.66, 0.48)], "Horas 11 no Preto e branco: o papel dentro e em volta das letras douradas"),
    ("p4-horas11-pb", "horas_p011", "pb", [(0.33, 0.33, 0.67, 0.58)], "Horas 11 no Preto e branco: o título dentro do oval"),
    ("m2-horas26-pb", "horas_p026", "pb", [(0.03, 0.08, 0.75, 0.28)], "Horas 26 no Preto e branco: 'NOVEMBRE.' e a coluna de letrinhas"),
    ("a1-horas47-pb", "horas_p047", "pb", [(0.15, 0.23, 0.50, 0.345), (0.15, 0.48, 0.50, 0.56)],
     "Horas 47 no Preto e branco: os 'JESUS' e o 'C' dourados"),
    ("m1-horas13-mp", "horas_p013", "mp", [(0.40, 0.76, 0.88, 0.88)], "Horas 13 no Mágico pro: a barra de baixo da moldura, perto de 'pag. 54'"),
    ("m1-horas13-pb", "horas_p013", "pb", [(0.40, 0.76, 0.88, 0.88)], "Horas 13 no Preto e branco: a barra de baixo da moldura, perto de 'pag. 54'"),
    ("m3-horas27-mp", "horas_p027", "mp", [(0.05, 0.08, 0.45, 0.17)], "Horas 27 no Mágico pro: a barra de cima da moldura, perto do canto esquerdo"),
    ("m3-horas27-pb", "horas_p027", "pb", [(0.05, 0.08, 0.45, 0.17)], "Horas 27 no Preto e branco: a barra de cima da moldura, perto do canto esquerdo"),
    ("f1-opus20-pb", "opusmajus_p020", "pb", [(0.06, 0.04, 0.62, 0.50)], "Opus Majus 20 no Preto e branco (forma 'livre'): o rosto da estátua"),
    ("n1-palatino5-pb", "palatino_p005", "pb", [(0.15, 0.10, 0.85, 0.55)], "Palatino 5 no Preto e branco: nada pode ter piorado"),
    ("n1-palatino5-mp", "palatino_p005", "mp", [(0.15, 0.10, 0.85, 0.55)], "Palatino 5 no Mágico pro: nada pode ter piorado"),
    ("n2-escola35-pb", "escola_p035", "pb", [(0.10, 0.0, 0.55, 0.42)], "Escola 35 no Preto e branco: nada pode ter piorado"),
    ("n2-escola35-mp", "escola_p035", "mp", [(0.10, 0.0, 0.55, 0.42)], "Escola 35 no Mágico pro: nada pode ter piorado"),
    ("n3-graduale222-pb", "graduale_p222", "pb", [(0.30, 0.08, 0.85, 0.34)], "Graduale 222 no Preto e branco: nada pode ter piorado"),
    ("n3-graduale222-mp", "graduale_p222", "mp", [(0.30, 0.08, 0.85, 0.34)], "Graduale 222 no Mágico pro: nada pode ter piorado"),
    ("x1-horas11-ponto-azul", "horas_p011", "pb", [(0.42, 0.665, 0.76, 0.715)], "Horas 11 no Preto e branco: 'M. DC.LXXXVIII.' encostado na moldura do oval"),
    ("x2-opus20-mp", "opusmajus_p020", "mp", [(0.06, 0.04, 0.62, 0.50)], "Opus Majus 20 no Mágico pro (forma 'livre'): o rosto ainda lavado"),
]


def borda(pagina: str, nome: str) -> Path:
    """A folha de beiradas do corte de 1 mm, com um rotulo grande em cima (o titulo pequeno sai)."""
    im = A.ler_rgb(BORDAS / f"bordas-{pagina}.jpg")
    im = im[44:]                                  # tira o titulo pequeno de dentro (saia cortado)
    if im.shape[1] < 900:                         # amplia as folhas estreitas, para ler
        im = U.na_largura(im, 900)
    img = U.rotulo(im, f"{nome}: a beirada da página pronta, ampliada", fundo=(30, 42, 54), tam=34,
                   sub="em cada linha: ANTES à esquerda, DEPOIS (com 1 mm, o programa de agora) à direita, com quanto papel sobra depois da "
                       "última tinta; a régua vermelha de 1 mm fica embaixo, fora da página; nada desenhado em cima")
    return U.gravar(img, SAIDA / "corte" / f"corte-{pagina}.jpg", qualidade=90, largura_max=LARGURA)


def main() -> None:
    feitos = [cartao(nome, titulo, tres(p, f), det) for nome, p, f, det, titulo in CARTOES]
    for p, nome in (("escola_p007", "Escola 7 ('CRISTÃ')"), ("escola_p035", "Escola 35"),
                    ("palatino_p067", "Palatino 67"), ("rhetorica_p073", "Rhetorica 73")):
        feitos.append(borda(p, nome))
    for f in feitos:
        print("  gravado", f.relative_to(SAIDA))
    print(f"{len(feitos)} imagens em {SAIDA}")


if __name__ == "__main__":
    main()
