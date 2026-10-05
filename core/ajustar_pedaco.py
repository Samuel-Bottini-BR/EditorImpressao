"""Ajustar o pedaço à figura, e medir quanto papel o pedaço pegou em volta dela.

Pedido do Samuel (conferência 13, S3, 05/10/2026): "(b) e (c) juntas - Mas
caso ele não queira mudar, fica do jeito que está."

O problema: desde o conserto do "só neste pedaço" (60d8c58), a área marcada
obedece INTEIRA ao filtro escolhido para ela - inclusive o papel que o Kaique
pegou junto ao desenhar o retângulo em volta da figura. Numa página em Preto e
branco com a pintura em Original, esse papel sai creme ao lado do branco do
resto: uma faixa (Escola de Jesus 7). Quanto mais folga no retângulo, mais
larga a faixa.

    (b) o aviso: medir_folga / avaliar_os_pedacos dizem que fração do
        retângulo é papel liso na borda, e se isso é "muito" (PAPEL_DEMAIS);
    (c) o botão: caixa_justa / ajustar_os_pedacos encolhem o retângulo até a
        figura.

Os dois só SUGEREM: nada aqui muda a marcação sozinho. Quem chama (a aba
Marcar, ui/tela_conferir.py) mostra o aviso e, se o Kaique clicar no botão,
grava a marcação nova como uma ação do desfazer.

Como se acha "a figura" dentro do retângulo, em palavras simples: o papel é a
cor das partes claras da página FORA do retângulo (lá é quase só papel); dentro
dele, o que tem cor bem diferente do papel é tinta; pontinhos soltos de
sujeira são ignorados; a tinta que está perto uma da outra forma um grupo; a
figura é o maior grupo (e os que forem quase do tamanho dele); legenda e linha
de texto soltas, bem menores, ficam de fora. O retângulo justo é o menor que
contém a figura, mais uma margenzinha. O ajuste só encolhe: nunca cresce e
nunca anda. Pode errar para os dois lados, e por isso só sugere: um pedaço de
verdade da figura longe do resto e pequeno (mais longe que JUNTAR, menor que
GRUPO_SOLTO) ficaria de fora do retângulo - o Kaique vê na hora e desfaz; uma
mancha grande colada na figura segura o ajuste (ele encolhe menos).

Só retângulos: o pedaço desenhado com o oval, o laço, o polígono ou o pincel
fica como está (ajustar mudaria a forma que a pessoa escolheu).

Não importa nada de ui/ (regra de arquitetura). As frações são as mesmas da
core.selecao (0 a 1, relativas à página), então a imagem pode estar em
qualquer resolução - a da prévia (150 DPI) basta e é rápida.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass

import cv2
import numpy as np

from core.selecao import RETANGULO, SOMAR, Selecao

# Quanto a cor de um ponto precisa se afastar da cor do papel para contar como
# figura (distância de cor no espaço Lab, a "Delta E" das gráficas: ~2 é o
# mínimo que o olho nota lado a lado; ~10 já é outra cor). 14 foi calibrado na
# Escola de Jesus 7 e na Opus Majus 20: o céu claro da pintura e a parede clara
# da foto ficam acima; o grão do papel e a sombra fraca da borda ficam abaixo.
# Seguro mudar um pouco (10 a 18). Mais baixo: o ajuste encolhe menos (o
# amarelado do papel conta como figura). Mais alto: partes muito claras da
# figura podem ficar de fora - aí o ajuste cortaria a beira da figura.
LIMIAR_DO_PAPEL = 14.0

# Pedaço de "figura" menor que isto (fração da área da PÁGINA, com um mínimo
# de 9 pontos) é sujeira solta no papel e não segura o ajuste. 0,002% de uma
# página a 150 DPI são ~30 pontos (um pontinho de ~1 mm). Traço fino e comprido
# (a moldura de uma gravura) é um pedaço grande: não some.
SUJEIRA_MAXIMA = 0.00002

# O que esta perto da figura faz parte dela: pedacos a menos disto um do outro
# (fracao do lado menor da pagina; 1% ~ 1,5 mm num livro de 15 cm) sao
# juntados num grupo so. E o que mantem inteiros os tracos soltos da beira de
# uma gravura (capim, assinatura) e separa a legenda e a linha de texto, que
# ficam mais longe. Seguro mudar um pouco (0,5% a 2%). Mais alto: legenda
# encostada na figura passa a contar como figura (o ajuste encolhe menos).
JUNTAR = 0.01

# Grupo pequeno perto do maior (a area do retangulo em volta dele, em fracao
# da do maior grupo) nao e a figura: e legenda, linha de texto, mancha. Nao
# segura o ajuste. Na Escola 7 a linha de texto em cima da pintura e ~2% dela
# e a legenda ~1%. Dois desenhos lado a lado (cada um com mais de 25% do
# maior) ficam os dois. Arriscado: subir muito (pedacos de verdade da figura,
# mais longe que JUNTAR, comecariam a ser cortados).
GRUPO_SOLTO = 0.25

# A margenzinha deixada em volta da figura, em fração do lado menor da página
# (0,2% ~ 0,3 mm num livro de 15 cm). Serve para não cortar a beira suave da
# figura. Seguro mudar; zero deixaria o retângulo colado na figura.
MARGEM = 0.002

# O "muito" do aviso: a fração do retângulo que é papel liso em volta da
# figura (1 - área do retângulo justo / área do retângulo desenhado). Medido em
# 05/10/2026 na prévia (150 DPI) e no PDF (300 DPI), com os mesmos números
# (relatorios/conferir/pedaco-em-original-2026-10-05/calibracao.json):
#   - Opus Majus 20, o retângulo da conferência 13 em volta da foto: 0,6% -
#     a foto ocupa quase tudo; não avisa;
#   - Escola de Jesus 7, o retângulo da conferência 13: 2,2% - uma faixa de
#     ~1,5 mm em cima e à esquerda ("É pequena, mas se vê", verificador); não
#     avisa, mas o botão funciona e tira a faixa;
#   - Escola 7, retângulo com folga larga (pegando a linha de texto de cima e
#     a legenda): 17,8%; avisa.
# 5% é, numa figura do tamanho da da Escola 7, uma faixa de ~2 mm em volta
# toda. Figura pequena avisa com faixa mais fina (a faixa pesa mais nela).
# Seguro mudar: mais alto avisa menos vezes; 0,02 avisaria também o retângulo
# da conferência 13 (e quase todo retângulo desenhado à mão).
PAPEL_DEMAIS = 0.05

# Fora do retângulo precisa haver pelo menos isto da página para estimar a cor
# do papel ali; senão, vale a página inteira.
MINIMO_DE_FORA = 0.02


@dataclass
class Folga:
    """Quanto papel um pedaço pegou em volta da figura.

    caixa: o retângulo como está (x0, y0, x1, y1 em frações);
    justa: o retângulo ajustado à figura;
    fracao_de_papel: 0 a 1, a parte do retângulo que é papel na borda;
    muito: fracao_de_papel >= PAPEL_DEMAIS (é quando a aba Marcar avisa).
    """

    caixa: tuple[float, float, float, float]
    justa: tuple[float, float, float, float]
    fracao_de_papel: float
    muito: bool

    @property
    def muda(self) -> bool:
        """O ajuste muda alguma coisa?"""
        return self.justa != self.caixa


def _lab(img: np.ndarray) -> np.ndarray:
    """A imagem em Lab de verdade (L de 0 a 100; a e b em torno de 0), float32."""
    bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img[..., :3]
    lab = cv2.cvtColor(np.ascontiguousarray(bgr), cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[..., 0] *= 100.0 / 255.0
    lab[..., 1:] -= 128.0
    return lab


def _em_pontos(caixa, altura: int, largura: int) -> tuple[int, int, int, int]:
    """Frações -> pontos, em ordem e dentro da página."""
    xa, ya, xb, yb = caixa
    x0, x1 = sorted((xa, xb))
    y0, y1 = sorted((ya, yb))
    return (max(0, min(largura, int(round(x0 * largura)))),
            max(0, min(altura, int(round(y0 * altura)))),
            max(0, min(largura, int(round(x1 * largura)))),
            max(0, min(altura, int(round(y1 * altura)))))


def _cor_do_papel(lab: np.ndarray, x0: int, y0: int, x1: int, y1: int) -> np.ndarray:
    """A cor do papel: a mediana do quarto mais claro da página FORA do
    retângulo (lá é quase só papel e texto; o claro é o papel). Se sobra
    pouca página fora (o retângulo pega quase tudo), a página inteira."""
    altura, largura = lab.shape[:2]
    fora = np.ones((altura, largura), bool)
    fora[y0:y1, x0:x1] = False
    pontos = lab[fora] if fora.mean() >= MINIMO_DE_FORA else lab.reshape(-1, 3)
    claro = pontos[:, 0] >= np.percentile(pontos[:, 0], 75)
    return np.median(pontos[claro], axis=0)


def _caixa_justa_em_pontos(lab: np.ndarray, x0: int, y0: int, x1: int, y1: int
                           ) -> tuple[int, int, int, int] | None:
    """O retângulo justo, em pontos, ou None se dentro só há papel."""
    altura, largura = lab.shape[:2]
    papel = _cor_do_papel(lab, x0, y0, x1, y1)
    distancia = np.linalg.norm(lab[y0:y1, x0:x1] - papel, axis=-1)
    figura = (distancia > LIMIAR_DO_PAPEL).astype(np.uint8)
    if not figura.any():
        return None
    # 1. sujeira solta: pedaços pequenos demais saem (ver SUJEIRA_MAXIMA)
    quantos, rotulos, medidas, _ = cv2.connectedComponentsWithStats(figura, connectivity=8)
    minimo = max(9, int(SUJEIRA_MAXIMA * altura * largura))
    pequenos = medidas[:, cv2.CC_STAT_AREA] < minimo
    pequenos[0] = True                                   # o fundo
    figura[pequenos[rotulos]] = 0
    if not figura.any():
        return None
    # 2. o que esta perto vira um grupo so (ver JUNTAR)...
    lado = max(3, int(round(JUNTAR * min(altura, largura))) | 1)
    juntos = cv2.dilate(figura, cv2.getStructuringElement(cv2.MORPH_RECT, (lado, lado)))
    quantos, rotulos_dos_grupos, grupos, _ = cv2.connectedComponentsWithStats(juntos, connectivity=8)
    # ...e o dilatar nao pode alargar a caixa: cada grupo vale o que tem de
    # figura de verdade dentro dele (a caixa da figura, sem o dilatado)
    caixas = []
    for g in range(1, quantos):
        gx, gy, gl, ga = (int(v) for v in grupos[g, :4])
        dentro = figura[gy:gy + ga, gx:gx + gl] & (rotulos_dos_grupos[gy:gy + ga, gx:gx + gl] == g)
        ys, xs = np.nonzero(dentro)
        if xs.size:
            caixas.append((gx + xs.min(), gy + ys.min(), gx + xs.max() + 1, gy + ys.max() + 1))
    if not caixas:
        return None
    # 3. a figura e o maior grupo e os que nao sao muito menores que ele (ver
    #    GRUPO_SOLTO); legenda e linha de texto soltas ficam de fora
    areas = [(c[2] - c[0]) * (c[3] - c[1]) for c in caixas]
    maior = max(areas)
    da_figura = [c for c, a in zip(caixas, areas) if a >= GRUPO_SOLTO * maior]
    ex0 = min(c[0] for c in da_figura)
    ey0 = min(c[1] for c in da_figura)
    ex1 = max(c[2] for c in da_figura)
    ey1 = max(c[3] for c in da_figura)
    margem = int(np.ceil(MARGEM * min(altura, largura)))
    # so encolhe: nunca passa do retangulo desenhado
    return (max(x0, x0 + ex0 - margem), max(y0, y0 + ey0 - margem),
            min(x1, x0 + ex1 + margem), min(y1, y0 + ey1 + margem))


def _justa_e_fracao(lab: np.ndarray, caixa) -> tuple[tuple, float] | None:
    """(retângulo justo em frações, fração de papel) ou None (só papel ou
    retângulo vazio). Quando o ajuste não muda nenhum ponto, devolve a
    PRÓPRIA caixa (as mesmas frações, sem arredondar)."""
    altura, largura = lab.shape[:2]
    x0, y0, x1, y1 = _em_pontos(caixa, altura, largura)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None
    justa = _caixa_justa_em_pontos(lab, x0, y0, x1, y1)
    if justa is None:
        return None
    if justa == (x0, y0, x1, y1):
        return tuple(float(v) for v in caixa), 0.0
    jx0, jy0, jx1, jy1 = justa
    fracao = 1.0 - ((jx1 - jx0) * (jy1 - jy0)) / float((x1 - x0) * (y1 - y0))
    return (float(jx0 / largura), float(jy0 / altura), float(jx1 / largura),
            float(jy1 / altura)), float(fracao)


def caixa_justa(img: np.ndarray, caixa) -> tuple[float, float, float, float] | None:
    """O retângulo `caixa` (x0, y0, x1, y1, em frações) encolhido até a figura
    que está dentro dele, em frações. None se dentro só há papel.

    `img` é a página SEM filtro (o Original, já dividida, cortada e
    endireitada como o PDF vai sair), em qualquer resolução. Com a página já
    filtrada a conta erra: o papel de fora sai branco e o de dentro, creme.
    """
    resultado = _justa_e_fracao(_lab(img), caixa)
    return None if resultado is None else resultado[0]


def medir_folga(img: np.ndarray, caixa) -> Folga | None:
    """Quanto do retângulo é papel em volta da figura (a medida do aviso).
    None se dentro só há papel (não há figura para ajustar). Mesma `img` de
    caixa_justa."""
    resultado = _justa_e_fracao(_lab(img), caixa)
    if resultado is None:
        return None
    justa, fracao = resultado
    return Folga(tuple(float(v) for v in caixa), justa, fracao, bool(fracao >= PAPEL_DEMAIS))


def pedacos_com_outro_filtro(selecao: Selecao, filtro_da_pagina: str) -> list[int]:
    """Os índices (na lista da seleção) dos pedaços que o ajuste trata:
    retângulos de SOMAR, com "só neste pedaço" num filtro diferente do da
    página. A marcação da máquina (sem filtro próprio), o "tirar" e as outras
    formas ficam de fora."""
    return [i for i, r in enumerate(selecao.regioes)
            if r.forma == RETANGULO and r.operacao == SOMAR and r.valida()
            and r.filtro and r.filtro != filtro_da_pagina]


def _caixa_da_regiao(regiao) -> tuple[float, float, float, float]:
    (xa, ya), (xb, yb) = regiao.pontos[:2]
    return (min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb))


def avaliar_os_pedacos(img: np.ndarray, selecao: Selecao,
                       filtro_da_pagina: str) -> dict[int, Folga]:
    """A folga de cada pedaço com outro filtro ({índice: Folga}); os que só
    têm papel dentro ficam de fora. É o que a aba Marcar usa para decidir o
    aviso (algum .muito) e se o botão faz alguma coisa (algum .muda)."""
    indices = pedacos_com_outro_filtro(selecao, filtro_da_pagina)
    if not indices:
        return {}
    lab = _lab(img)
    folgas: dict[int, Folga] = {}
    for i in indices:
        caixa = _caixa_da_regiao(selecao.regioes[i])
        resultado = _justa_e_fracao(lab, caixa)
        if resultado is not None:
            justa, fracao = resultado
            folgas[i] = Folga(caixa, justa, fracao, bool(fracao >= PAPEL_DEMAIS))
    return folgas


def ajustar_os_pedacos(img: np.ndarray, selecao: Selecao,
                       filtro_da_pagina: str) -> tuple[Selecao, int]:
    """Uma CÓPIA da seleção com cada pedaço com outro filtro encolhido até a
    figura, e quantos mudaram. A seleção de entrada não é tocada (quem chama
    guarda a de antes para o desfazer). O resto - ordem, tipo, filtro,
    origem - fica igual; só os dois cantos do retângulo mudam."""
    nova = copy.deepcopy(selecao)
    mudaram = 0
    for i, folga in avaliar_os_pedacos(img, selecao, filtro_da_pagina).items():
        if not folga.muda:
            continue
        x0, y0, x1, y1 = folga.justa
        nova.regioes[i].pontos = [(x0, y0), (x1, y1)]
        mudaram += 1
    return nova, mudaram
