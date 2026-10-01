r"""Monta as imagens do formulario relatorios/conferir-aqui-5.html (quinta conferencia, 01/10/2026).

Pedido do Samuel: "faz um novo relatório com mais fotos por favor, tem uns que estão faltando
foto, para que eu possa responder, deixe todas as questões bem explicadas e com fotos".

Uso (no .venv do programa; nao muda o programa, nao processa pagina nenhuma, so desenha):
    .venv\Scripts\python.exe relatorios\conferencia-5-2026-10-01\scripts\montar_imagens.py
O print da tela "O que fazer" vem de relatorios\conferencia-4-2026-10-01\scripts\print_tela.py
(copiado para conferencia-5-2026-10-01\tela\ antes de rodar este).

O que faz:
1. Refaz TODOS os cartoes da conferencia 4 (usa o script da conferencia 4, com a saida
   trocada para esta pasta): cartoes/, tela/, corte/.
2. Faz os cartoes novos (cartoes/ com nomes novos), so com imagens prontas:
   - da rodada relatorios/conferir/pb-mp-decoracao-2026-10-01/ (antes/depois, PB e MP);
   - do verificador dessa rodada (verificador/imagens/ampliados/a5 e a6: rodadas dele pelo
     caminho do programa, com "Este livro tem fotos" e com a caixinha marcada; e o print p05
     da janela). As partes dessas imagens sao separadas pelas faixas cor-de-rosa que ele
     desenhou entre elas.

Regra do desenho (igual a conferencia 4): o retangulo de destaque fica com folga, POR FORA do
lugar ampliado; nada e desenhado em cima dos detalhes; rotulos em faixas acima de cada parte;
setas (Opus 256) numa faixa branca ao lado, nunca em cima da imagem.

Seguro mudar: recortes, textos, tamanhos. Arriscado: nada (so leitura e desenho).
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
SAIDA = AQUI.parent
sys.path.insert(0, str(RAIZ / "relatorios" / "conferencia-4-2026-10-01" / "scripts"))

import montar_imagens as M4  # noqa: E402  (cartoes da conferencia 4 e as pecas de desenho)

U, A = M4.U, M4.A
M4.SAIDA = SAIDA                       # tudo o que o script da conferencia 4 grava vem para ca
VERIF = M4.RODADA / "verificador"
LARGURA = M4.LARGURA
COR = M4.COR_DETALHE
CINZA_ORIG = (90, 90, 90)
VERDE, MARROM, AZUL, ROXO = (0, 115, 0), (150, 60, 30), (21, 101, 192), (110, 40, 140)


def partes_do_verificador(arquivo: Path) -> list[np.ndarray]:
    """Separa uma imagem do verificador nas partes, pelas faixas cor-de-rosa verticais."""
    im = A.ler_rgb(arquivo)
    r, g, b = (im[:, :, k].astype(int) for k in range(3))
    faixa = ((r > 200) & (b > 200) & (g < 80)).mean(axis=0) > 0.8
    partes, x0 = [], 0
    for x in range(im.shape[1] + 1):
        if x == im.shape[1] or faixa[x]:
            if x - x0 > 50:
                partes.append(im[:, x0:x])
            x0 = x + 1
    return partes


def setas_ao_lado(img: np.ndarray, ys: list[float], cor=COR[0], larg: int = 70) -> np.ndarray:
    """Faixa branca a direita com setas apontando para a imagem (nada em cima da imagem)."""
    h = img.shape[0]
    faixa = np.full((h, larg, 3), 255, np.uint8)
    for y in ys:
        yy = int(y * h)
        cv2.arrowedLine(faixa, (larg - 6, yy), (6, yy), cor, 6, cv2.LINE_AA, tipLength=0.45)
    return np.hstack([img, faixa])


def cartao_geral(nome: str, titulo: str, colunas: list, detalhes: list, alt: int = 880,
                 setas: dict | None = None, sub_titulo: str = "") -> Path:
    """Como M4.cartao, com colunas livres: colunas = [(imagem, ROTULO, sub, cor_da_faixa)].

    Todas as imagens das colunas tem de estar no MESMO enquadramento (mesmo recorte vale para
    todas). detalhes = fracoes da pagina; setas = {indice do detalhe: [y em fracao do detalhe]}.
    """
    setas = setas or {}
    n = len(colunas)
    topo = U.lado_a_lado([U.rotulo(M4.pagina_com_folga_marcada(im, detalhes, alt), r, fundo=f, sub=s, tam=38)
                          for im, r, s, f in colunas], por_baixo=True)
    legenda = " · ".join(f"retângulo {M4.NOME_COR[k]} = detalhe {k + 1}" for k in range(len(detalhes)))
    partes = [U.rotulo(topo, titulo, fundo=(30, 42, 54), tam=40,
                       sub=(sub_titulo + " " if sub_titulo else "") + f"Página inteira: {legenda} (o retângulo fica com "
                       "folga, por fora do lugar ampliado; os detalhes não têm nada desenhado por cima)")]
    for k, ret in enumerate(detalhes):
        crs = [M4.recorte(im, ret) for im, *_ in colunas]
        largo = crs[-1].shape[1] / crs[-1].shape[0] >= 2.2
        extra = 70 if k in setas else 0
        if largo:
            linhas = []
            for c, (_im, r, s, f) in zip(crs, colunas):
                c = U.na_largura(c, LARGURA - 10 - extra)
                if k in setas:
                    c = setas_ao_lado(c, setas[k], COR[k])
                linhas.append(U.rotulo(c, r, fundo=f, tam=34))
            corpo = U.um_embaixo_do_outro(linhas, espaco=14)
        else:
            larg = (LARGURA - 18 * (n - 1)) // n - extra
            quadros = []
            for c, (_im, r, s, f) in zip(crs, colunas):
                c = U.na_largura(c, larg)
                if k in setas:
                    c = setas_ao_lado(c, setas[k], COR[k])
                quadros.append(U.rotulo(c, r, fundo=f, tam=34))
            corpo = U.lado_a_lado(quadros, por_baixo=True)
        partes.append(U.rotulo(corpo, f"DETALHE {k + 1} (retângulo {M4.NOME_COR[k]}), ampliado, sem nada desenhado por cima"
                               + (" · setas = os números que somem" if k in setas else ""), fundo=COR[k], tam=34))
    img = U.um_embaixo_do_outro(partes, espaco=26)
    return U.gravar(img, SAIDA / "cartoes" / f"{nome}.jpg", qualidade=88, largura_max=LARGURA)


def orig(p):
    return (M4.original_alinhado(p), "ORIGINAL", "a página como veio do livro", CINZA_ORIG)


def res(pasta, p, rotulo, sub, cor):
    return (M4.resultado(pasta, p), rotulo, sub, cor)


# --------------------------------------------------------------------------- A. fotos que faltavam
def p1_iluminura() -> list[Path]:
    """P1: a iluminura no Preto e branco, mantendo a cor (hoje) ou em traco (como sai com a caixinha)."""
    feitos = []
    for p, nome, det in (("horas_p011", "Horas 11", (0.0, 0.60, 0.50, 0.86)),
                         ("horas_p047", "Horas 47", (0.0, 0.38, 0.42, 0.63))):
        feitos.append(cartao_geral(
            f"q1-{p.replace('_p', '')}-cor-ou-traco", f"{nome} no Preto e branco: as duas escolhas da pergunta P1",
            [orig(p),
             res("depois-pb", p, "MANTÉM A COR", "Preto e branco de hoje (caixinha desmarcada)", VERDE),
             res("antes-pb", p, "EM PRETO E BRANCO", "a iluminura em traço preto (como sai com a caixinha marcada)", MARROM)],
            [det]))
    return feitos


def x1_opus256() -> Path:
    p = "opusmajus_p256"
    # setas: os blocos da ultima coluna (40/12/0, 48/20/8, 40/28/16, 48/36/24, 56/44/32)
    return cartao_geral(
        "x1-opus256-ultima-coluna", "Opus Majus 256: os números fracos da última coluna",
        [orig(p), res("depois-pb", p, "PRETO E BRANCO", "programa de hoje", VERDE),
         res("depois-mp", p, "MÁGICO PRO", "programa de hoje", AZUL)],
        [(0.70, 0.62, 0.975, 0.98)], alt=560, setas={0: [0.155, 0.33, 0.49, 0.66, 0.82]})


def x2_graduale221() -> Path:
    p = "graduale_p221"
    return cartao_geral(
        "x2-graduale221-letras-raspadas", "Graduale 221: as letras raspadas entre 'ſu' e 'mus'",
        [orig(p), res("depois-pb", p, "PRETO E BRANCO", "programa de hoje", VERDE),
         res("depois-mp", p, "MÁGICO PRO", "programa de hoje", AZUL)],
        [(0.10, 0.455, 0.32, 0.525)])


# --------------------------------------------------------------------------- B. perguntas novas
def pdf_peso() -> Path:
    """A mesma pagina nas duas versoes, com o tamanho do PDF em cima (medidas do verificador)."""
    a6 = partes_do_verificador(VERIF / "imagens" / "ampliados" / "a6-minha-rodada-horas11-cor-e-traco.jpg")
    h11_cor, h11_traco, h13_traco = a6[1], a6[2], a6[3]
    h13_cor = M4.resultado("depois-pb", "horas_p013")
    alt = 760
    linha = []
    for cor_img, traco_img, nome, mb_cor, mb_traco, seg in (
            (h11_cor, h11_traco, "Horas 11 (iluminura)", "25,6 MB", "0,4 MB", "14,2 s contra 9,8 s"),
            (h13_cor, h13_traco, "Horas 13 (moldura)", "2,8 MB", "0,11 MB", "7,3 s contra 3,1 s")):
        a = U.rotulo(U.na_altura(cor_img, alt), f"MANTÉM A COR: {mb_cor}", fundo=VERDE, tam=40,
                     sub="por página no PDF (de fábrica hoje)")
        b = U.rotulo(U.na_altura(traco_img, alt), f"TRAÇO PRETO: {mb_traco}", fundo=MARROM, tam=40,
                     sub="por página no PDF (caixinha marcada)")
        linha.append(U.rotulo(U.lado_a_lado([a, b], por_baixo=True), nome, fundo=(30, 42, 54), tam=36,
                              sub=f"processar esta página: {seg}"))
    img = U.um_embaixo_do_outro([U.lado_a_lado(linha, espaco=40)], espaco=10)
    img = U.rotulo(img, "O peso do PDF no Preto e branco", fundo=(30, 42, 54), tam=40,
                   sub="medidas do verificador (rodadas dele pelo caminho do programa, PDF gravado); imagens: a6 do "
                       "verificador e a rodada de 01/10")
    return U.gravar(img, SAIDA / "cartoes" / "q2-pdf-pesado.jpg", qualidade=88, largura_max=LARGURA)


def titulos() -> list[Path]:
    feitos = []
    for p, nome, det in (("horas_p011", "Horas 11: o título dentro do oval", (0.33, 0.33, 0.67, 0.58)),
                         ("horas_p026", "Horas 26: 'NOVEMBRE.' e a coluna de letrinhas", (0.03, 0.08, 0.75, 0.28))):
        feitos.append(cartao_geral(
            f"q3-{p.replace('_p', '')}-titulo", f"{nome} no Preto e branco",
            [orig(p),
             res("depois-pb", p, "FICAM NA COR", "como está hoje", VERDE),
             res("antes-pb", p, "SAEM PRETOS", "como saíam antes (olhe só as letras)", MARROM)],
            [det]))
    return feitos


# --------------------------------------------------------------------------- B. achados do verificador
def achados() -> list[Path]:
    feitos = []
    feitos.append(cartao_geral(
        "a1-horas47-jesus-dourado", "Horas 47 no Preto e branco: o 'JESUS' e o 'C' dourados",
        [orig("horas_p047"), res("antes-pb", "horas_p047", "ANTES", "Preto e branco, antes de 01/10", MARROM),
         res("depois-pb", "horas_p047", "AGORA", "Preto e branco, programa de hoje", VERDE)],
        [(0.17, 0.235, 0.47, 0.345)]))
    feitos.append(cartao_geral(
        "a2-horas11-miolo-creme", "Horas 11: o papel dentro das letras douradas",
        [orig("horas_p011"), res("depois-mp", "horas_p011", "MÁGICO PRO", "programa de hoje", AZUL),
         res("depois-pb", "horas_p011", "PRETO E BRANCO", "programa de hoje", VERDE)],
        [(0.36, 0.37, 0.66, 0.48)]))
    # Opus 20: forma "livre" (de fabrica, rodada de 01/10) x "Este livro tem fotos" (rodada do verificador, a5)
    a5 = partes_do_verificador(VERIF / "imagens" / "ampliados" / "a5-opus20-rodada-minha-livre-e-retangular.jpg")
    livre = M4.resultado("depois-pb", "opusmajus_p020")
    tem_fotos = cv2.resize(a5[2], (livre.shape[1], livre.shape[0]), interpolation=cv2.INTER_CUBIC)
    feitos.append(cartao_geral(
        "a3-opus20-livre-ou-tem-fotos", "Opus Majus 20 no Preto e branco: forma 'livre' × 'Este livro tem fotos'",
        [orig("opusmajus_p020"),
         (livre, "LIVRE (de fábrica)", "Preto e branco de hoje, rodada de 01/10", VERDE),
         (tem_fotos, "ESTE LIVRO TEM FOTOS", "Preto e branco de hoje, rodada do verificador", AZUL)],
        [(0.06, 0.04, 0.62, 0.50)]))
    feitos.append(cartao_geral(
        "a4-horas13-barra-de-baixo", "Horas 13: o retângulo na barra de baixo da moldura",
        [orig("horas_p013"), res("depois-pb", "horas_p013", "PRETO E BRANCO", "programa de hoje", VERDE),
         res("depois-mp", "horas_p013", "MÁGICO PRO", "programa de hoje", AZUL)],
        [(0.40, 0.80, 0.85, 0.88)]))
    feitos.append(cartao_geral(
        "a5-horas27-barra-de-cima", "Horas 27: o buraco na barra de cima da moldura",
        [orig("horas_p027"), res("depois-pb", "horas_p027", "PRETO E BRANCO", "programa de hoje", VERDE),
         res("depois-mp", "horas_p027", "MÁGICO PRO", "programa de hoje", AZUL)],
        [(0.06, 0.08, 0.40, 0.17)]))
    return feitos


def aviso_falso() -> Path:
    """Print p05 do verificador: o aviso e o cartao do Preto e branco marcados POR FORA, e ampliados."""
    im = A.ler_rgb(VERIF / "reproducoes" / "prints" / "p05-aba-filtro-pb-caixinha-desmarcada.png")
    marcado = im.copy()
    aviso, cartao_pb = (36, 672, 1564, 720), (437, 240, 712, 660)
    for (x0, y0, x1, y1), cor in ((aviso, COR[0]), (cartao_pb, COR[1])):
        cv2.rectangle(marcado, (x0 - 8, y0 - 8), (x1 + 8, y1 + 8), cor, 4)
    z_aviso = U.na_largura(im[aviso[1] - 4:aviso[3] + 4, aviso[0] - 4:aviso[2] + 4], LARGURA - 20)
    z_cartao = U.na_altura(im[cartao_pb[1]:cartao_pb[3], cartao_pb[0]:cartao_pb[2]], 700)
    partes = [U.rotulo(U.na_largura(marcado, LARGURA - 20), "A tela de conferir, aba Filtro (Horas 11, caixinha desmarcada)",
                       fundo=(30, 42, 54), tam=36,
                       sub="print do verificador (p05) · retângulo rosa = o aviso · retângulo azul = o cartão do "
                           "Preto e branco (os retângulos ficam com folga, por fora)"),
              U.rotulo(z_aviso, "O AVISO, ampliado: diz que vai perder a ilustração", fundo=COR[0], tam=34),
              U.rotulo(z_cartao, "O CARTÃO DO PRETO E BRANCO, ampliado", fundo=COR[1], tam=30,
                       sub="a iluminura continua colorida: não perde nada")]
    return U.gravar(U.um_embaixo_do_outro(partes, espaco=24), SAIDA / "cartoes" / "x3-aviso-falso.jpg",
                    qualidade=90, largura_max=LARGURA)


def conferir_traco_igual_caixinha() -> None:
    """Confere se o ANTES do Preto e branco (traco) e parecido com o que a caixinha marcada da
    (parte 3 da a6 do verificador), para poder usar o ANTES na pergunta P1. So imprime."""
    a6 = partes_do_verificador(VERIF / "imagens" / "ampliados" / "a6-minha-rodada-horas11-cor-e-traco.jpg")
    caixinha = cv2.cvtColor(a6[2], cv2.COLOR_RGB2GRAY)
    antes = cv2.cvtColor(cv2.resize(M4.resultado("antes-pb", "horas_p011"), (caixinha.shape[1], caixinha.shape[0]),
                                    interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    hoje = cv2.cvtColor(cv2.resize(M4.resultado("depois-pb", "horas_p011"), (caixinha.shape[1], caixinha.shape[0]),
                                   interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    print(f"  Horas 11, diferenca media contra a caixinha marcada (0-255): ANTES {np.abs(antes.astype(int) - caixinha).mean():.1f}"
          f", HOJE (cor) {np.abs(hoje.astype(int) - caixinha).mean():.1f}")


def main() -> None:
    feitos = []
    for nome, pagina, filtro, detalhes, titulo, cont in M4.CARTOES:
        feitos.append(M4.cartao(nome, pagina, filtro, detalhes, titulo, cont))
    feitos.append(M4.tela())
    feitos.append(M4.corte_crista())
    feitos += p1_iluminura()
    feitos += [x1_opus256(), x2_graduale221(), pdf_peso()]
    feitos += titulos()
    feitos += achados()
    feitos.append(aviso_falso())
    conferir_traco_igual_caixinha()
    for f in feitos:
        print("  gravado", f.relative_to(SAIDA))
    print(f"{len(feitos)} imagens em {SAIDA}")


if __name__ == "__main__":
    main()
