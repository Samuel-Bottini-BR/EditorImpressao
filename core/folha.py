"""Tamanho da folha final e composição do recorte dentro dela.

Contexto (seção 3a do plano "corrigir bugs do teste do Boécio"): o programa
sempre confundiu duas coisas que o usuário decide separadamente:

  - RECORTE: qual pedaço da imagem ORIGINAL vira conteúdo (já existia,
    `ConfigPagina.recorte`, sempre em `core/recortar.py`/`core/pipeline.py`).
  - FOLHA: o tamanho FÍSICO da página impressa final (`ConfigPagina.
    tamanho_folha_cm`, novo). Quando a folha é maior que o recorte, sobra
    margem branca ao redor - o recorte não é esticado nem recentralizado.

Este módulo é PURO DE PROPÓSITO (nenhum import de PySide6/`ui`): `core/`
nunca pode depender de `ui/` (regra do projeto). As primeiras funções deste
arquivo (`TAMANHOS_DE_PAPEL_CM` até `recorte_cabe_na_pagina`) só mudaram de
lugar - vieram de `ui/widgets/visualizador.py`, onde moravam fora de lugar
por serem puramente aritméticas. `visualizador.py` reexporta os mesmos nomes
(`from core.folha import ...`), então nada que já importava de lá quebra.

Quem for mexer aqui: as funções de composição (`compor_na_folha` e a dupla
`conteudo_como_retangulo`/`deslocamento_do_retangulo`) têm uma regra de ouro -
NUNCA cortar conteúdo escondido. Se a folha escolhida não couber o conteúdo,
a composição é abortada e o conteúdo original volta sem alteração (rede de
segurança da decisão 2 do plano); quem avisa que a folha ficou pequena demais
é a tela (`ui/tela_conferir.py`), não este módulo.
"""

from __future__ import annotations

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover - cv2 sempre presente no projeto
    cv2 = None


# ---------------------------------------------------------------------------
# Medidas do recorte em cm (movido de ui/widgets/visualizador.py)
# ---------------------------------------------------------------------------

def medidas_do_recorte_em_cm(
    recorte: tuple[float, float, float, float],
    largura_px: int, altura_px: int, dpi: float,
) -> dict[str, float]:
    """Quanto cada lado do recorte corta, e o tamanho final, em cm.

    `largura_px`/`altura_px` são o tamanho em pixels da imagem MOSTRADA na
    tela (a prévia) e `dpi` é a resolução com que ELA foi renderizada - a
    conta pixel/dpi = polegada dá o tamanho físico real da página
    independente de qual "qualidade de prévia" está ativa (ver
    `ui/tela_conferir.py::_mudar_qualidade_da_previa`), porque o número de
    pixels e o dpi usado para gerá-los mudam juntos.
    """
    x, y, w, h = recorte
    if dpi <= 0 or largura_px <= 0 or altura_px <= 0:
        return {"esquerda": 0.0, "direita": 0.0, "cima": 0.0, "baixo": 0.0,
                "largura_final": 0.0, "altura_final": 0.0}
    largura_pol = largura_px / dpi
    altura_pol = altura_px / dpi
    return {
        "esquerda": x * largura_pol * 2.54,
        "direita": (1.0 - x - w) * largura_pol * 2.54,
        "cima": y * altura_pol * 2.54,
        "baixo": (1.0 - y - h) * altura_pol * 2.54,
        "largura_final": w * largura_pol * 2.54,
        "altura_final": h * altura_pol * 2.54,
    }


# Tamanhos de papel comuns, em cm (largura x altura), para o botão de atalho
# do diálogo "Tamanho da folha" - ver `ui/dialogo_tamanho_da_folha.py`.
TAMANHOS_DE_PAPEL_CM = {
    "A4": (21.0, 29.7),
    "A5": (14.8, 21.0),
    "Carta": (21.59, 27.94),
}


def recorte_para_tamanho_cm(
    largura_cm: float, altura_cm: float,
    largura_px: int, altura_px: int, dpi: float,
    centro: tuple[float, float] = (0.5, 0.5),
) -> tuple[float, float, float, float]:
    """A fração de recorte (x, y, w, h) que resulta nesse tamanho final.

    Fica centralizada em `centro` (fração 0-1 da página; o padrão é o meio).
    Não estica nada: se o tamanho pedido não couber na página, a fração
    resultante extrapola 0-1 de propósito - `recorte_cabe_na_pagina` avisa
    disso antes de aplicar.
    """
    if dpi <= 0 or largura_px <= 0 or altura_px <= 0:
        return (0.0, 0.0, 1.0, 1.0)
    largura_pol_pagina = largura_px / dpi
    altura_pol_pagina = altura_px / dpi
    w = (largura_cm / 2.54) / largura_pol_pagina
    h = (altura_cm / 2.54) / altura_pol_pagina
    cx, cy = centro
    return (cx - w / 2, cy - h / 2, w, h)


def recorte_cabe_na_pagina(recorte: tuple[float, float, float, float]) -> bool:
    x, y, w, h = recorte
    return x >= -1e-6 and y >= -1e-6 and x + w <= 1.0 + 1e-6 and y + h <= 1.0 + 1e-6


# ---------------------------------------------------------------------------
# Tamanho da FOLHA vs. tamanho do RECORTE (novo, item 2/4 do plano)
# ---------------------------------------------------------------------------

def _folga_do_arredondamento_cm() -> float:
    """Meio passo do campo mais grosso da janela "Tamanho da folha", em cm
    (core.unidades.CASAS: 0,01 pol = 0,0254 cm -> 0,0127 cm), mais um fio."""
    from core import unidades

    return max(0.5 * 10 ** -unidades.CASAS[u] / unidades._POR_CM[u]
               for u in unidades.UNIDADES) + 1e-6


# Etapa 9c da obra (26/10/2026; Lista de bugs de 02/10, "'Tamanho da folha' abre
# com o aviso 'menor que o corte' mesmo com tamanho igual ao corte"): a janela
# abre com os campos no tamanho do corte ARREDONDADO às casas da unidade
# (13,944 cm vira 13,94), e a folga de 0,001 cm fazia o arredondamento para
# baixo virar "menor que o corte", com os dois números iguais na tela. A folga
# agora é a do arredondamento (~0,13 mm, invisível na impressão; o corte nunca
# é cortado escondido: core/folha.compor_na_folha). Arriscado: folga maior que
# o passo dos campos (uma folha menor de verdade deixaria de avisar).
FOLGA_DO_ARREDONDAMENTO_CM = _folga_do_arredondamento_cm()


def tamanho_da_folha_cabe(
    tamanho_folha_cm: tuple[float, float] | None,
    tamanho_recorte_cm: tuple[float, float],
    tolerancia_cm: float = FOLGA_DO_ARREDONDAMENTO_CM,
) -> bool:
    """A folha escolhida é grande o bastante para conter o recorte atual?

    Usada tanto pelo diálogo "tamanho..." (ao digitar um valor) quanto pela
    tela (se o recorte crescer depois de já haver uma folha escolhida) -
    decisões 1 e 2 do plano: NUNCA trava, só avisa. `tamanho_folha_cm=None`
    quer dizer "a folha É do tamanho do recorte" (comportamento de sempre),
    então sempre cabe por definição.
    """
    if tamanho_folha_cm is None:
        return True
    largura_folha, altura_folha = tamanho_folha_cm
    largura_recorte, altura_recorte = tamanho_recorte_cm
    return (largura_folha + tolerancia_cm >= largura_recorte
            and altura_folha + tolerancia_cm >= altura_recorte)


def _para_pixels(tamanho_cm: tuple[float, float], dpi: float) -> tuple[int, int]:
    largura_cm, altura_cm = tamanho_cm
    return (round(largura_cm / 2.54 * dpi), round(altura_cm / 2.54 * dpi))


def compor_na_folha(
    conteudo: np.ndarray,
    tamanho_folha_cm: tuple[float, float] | None,
    dpi: float,
    escala: float = 1.0,
    deslocamento: tuple[float, float] = (0.0, 0.0),
    mexido_a_mao: bool = False,
) -> np.ndarray:
    """Cola `conteudo` (o recorte já pronto) num canvas branco do tamanho de
    `tamanho_folha_cm`, na resolução `dpi` - a etapa que faltava no pipeline
    (achado da investigação técnica do plano): "folha maior que o recorte,
    com sobra branca" não existia em NENHUM lugar antes desta função.

    `escala`/`deslocamento` são `ConfigPagina.conteudo_escala`/
    `conteudo_deslocamento` - hoje sempre 1.0/(0,0) (mover o conteúdo pela
    tela é o item 4, fora desta entrega), mas a função já os aplica de
    verdade: `deslocamento` é a fração de `tamanho_folha_cm` a partir do
    CENTRO (mesmo referencial de `guias_ativas`/`encaixar_no_ima`).

    Regra de ouro (decisão 2 do plano, rede de segurança): nunca corta nada
    escondido. `tamanho_folha_cm=None`, ou o conteúdo (já escalado) não
    caber na folha, ou `dpi<=0` -> devolve `conteudo` sem nenhuma alteração,
    do tamanho que sempre teve.

    mexido_a_mao (obra de 26/10/2026, etapa 1; decisão D-008 do Samuel:
    "quero conseguir redimensionar o conteudo tambem", "a ferramenta de mover
    não deveria estar vinculada ao corte de bordas"): True quando a PESSOA
    moveu ou redimensionou o conteúdo desta página e isso vale
    (core.etapas.conteudo_mexido). Aí o mover nunca é jogado fora:
      - sem tamanho de folha, a folha é a PRÓPRIA página (o tamanho de
        `conteudo`): o conteúdo anda dentro dela e o que sair pela beirada
        fica de fora (a página não muda de tamanho - escolha da gerente
        D-017; o aviso do que passou da beirada é analise.IMPRESSO_DE_FORA,
        medido por parte_impressa_de_fora, etapa 5 da obra);
      - com a folha escolhida um pouco menor que o conteúdo (a janela
        "tamanho..." mostra o corte arredondado a 0,01 cm: 21,01 cm a 300 DPI
        são 2481 pontos, e o conteúdo tinha 2482 - era o "Mover conteúdo"
        que não chegava ao PDF no teste do Kaique, 26/10/2026), a conta não
        desiste: cola e corta só o que passa da folha.
    False (o de sempre, e o projeto antigo sem a marca): a conta de antes,
    linha por linha. Arriscado: passar True sem a pessoa ter mexido (a rede
    de segurança deixaria de valer para quem nunca moveu nada).
    """
    if conteudo is None or conteudo.size == 0 or dpi <= 0:
        return conteudo
    if tamanho_folha_cm is None and not mexido_a_mao:
        return conteudo

    altura_conteudo, largura_conteudo = conteudo.shape[:2]
    largura_escalada = largura_conteudo * escala
    altura_escalada = altura_conteudo * escala

    if tamanho_folha_cm is None:
        # D-008: sem folha escolhida, a folha e a propria pagina
        largura_folha_px, altura_folha_px = largura_conteudo, altura_conteudo
    else:
        largura_folha_px, altura_folha_px = _para_pixels(tamanho_folha_cm, dpi)
    if largura_folha_px <= 0 or altura_folha_px <= 0:
        return conteudo

    # rede de seguranca: nao cabe -> devolve o conteudo original, intacto
    # (so quando a pessoa NAO mexeu no conteudo; ver mexido_a_mao)
    if not mexido_a_mao and (largura_escalada > largura_folha_px
                             or altura_escalada > altura_folha_px):
        return conteudo

    if abs(escala - 1.0) > 1e-9 and cv2 is not None:
        nova_largura = max(1, round(largura_escalada))
        nova_altura = max(1, round(altura_escalada))
        redimensionado = cv2.resize(
            conteudo, (nova_largura, nova_altura), interpolation=cv2.INTER_AREA)
    else:
        redimensionado = conteudo

    if redimensionado.ndim == 2:
        canvas = np.full((altura_folha_px, largura_folha_px), 255, dtype=conteudo.dtype)
    else:
        canvas = np.full(
            (altura_folha_px, largura_folha_px, redimensionado.shape[2]),
            255, dtype=conteudo.dtype)

    h_c, w_c = redimensionado.shape[:2]
    dx_px = round(deslocamento[0] * largura_folha_px)
    dy_px = round(deslocamento[1] * altura_folha_px)
    x0 = round((largura_folha_px - w_c) / 2) + dx_px
    y0 = round((altura_folha_px - h_c) / 2) + dy_px

    # Recorta so o que sobrar fora do CANVAS (deslocamento extremo empurrando
    # para fora) - nao e a rede de seguranca acima, e so a colagem nao poder
    # escrever fora dos limites do array.
    destino_x0, destino_x1 = max(0, x0), min(largura_folha_px, x0 + w_c)
    destino_y0, destino_y1 = max(0, y0), min(altura_folha_px, y0 + h_c)
    origem_x0, origem_x1 = destino_x0 - x0, destino_x1 - x0
    origem_y0, origem_y1 = destino_y0 - y0, destino_y1 - y0

    if destino_x1 > destino_x0 and destino_y1 > destino_y0:
        canvas[destino_y0:destino_y1, destino_x0:destino_x1] = (
            redimensionado[origem_y0:origem_y1, origem_x0:origem_x1])

    return canvas


# ---------------------------------------------------------------------------
# Conversao escala+deslocamento <-> retangulo (a ferramenta "Mover e
# redimensionar" da tela e o PDF usam a mesma conta; etapa 5 da obra)
# ---------------------------------------------------------------------------

def conteudo_como_retangulo(
    escala: float,
    deslocamento: tuple[float, float],
    tamanho_folha_cm: tuple[float, float],
    tamanho_conteudo_px: tuple[int, int],
    dpi: float,
) -> tuple[float, float, float, float]:
    """Converte (escala, deslocamento) - o formato salvo em `ConfigPagina` -
    para um retângulo (x, y, w, h) em fração da folha, o formato que
    `guias_ativas`/`encaixar_no_ima` (em `ui/widgets/visualizador.py`)
    entendem. A conta é a de `retangulo_na_folha` (etapa 5 da obra), com a
    folha dada em cm."""
    return retangulo_na_folha(escala, deslocamento, _para_pixels(tamanho_folha_cm, dpi),
                              tamanho_conteudo_px)


def deslocamento_do_retangulo(
    retangulo: tuple[float, float, float, float],
    tamanho_folha_cm: tuple[float, float],
    tamanho_conteudo_px: tuple[int, int],
    dpi: float,
) -> tuple[float, tuple[float, float]]:
    """O inverso de `conteudo_como_retangulo`: devolve (escala, deslocamento)
    a partir de um retângulo em fração da folha."""
    return escala_e_deslocamento(retangulo, _para_pixels(tamanho_folha_cm, dpi),
                                 tamanho_conteudo_px)


# ---------------------------------------------------------------------------
# Etapa 5 da obra de 26/10/2026: a ferramenta "Mover e redimensionar"
# ---------------------------------------------------------------------------
#
# Decisões do Samuel que estas contas seguem (docs/plano/DECISOES.md):
#   D-008 (22/09 e 26/10/2026): "quero conseguir redimensionar o conteudo
#       tambem" e "a ferramenta de mover não deveria estar vinculada ao corte
#       de bordas" - mover e aumentar sem escolher tamanho de folha. Sem folha,
#       a ÁREA BRANCA é a própria página (o tamanho do conteúdo): o conteúdo
#       anda dentro dela, como em compor_na_folha com mexido_a_mao.
#   D-017 (escolha da gerente sobre o G10 de 05/10: "Avisar e não reduzir -
#       avisar para eu reduzir manualmente"): o que passa da beirada fica de
#       fora, nada é diminuído sozinho, e a página ganha o aviso
#       analise.IMPRESSO_DE_FORA quando parte do que está IMPRESSO (não o papel
#       em branco da margem) sai da área branca. A medida é
#       `parte_impressa_de_fora`.
#   D-303 (12/09/2026): "precisamos centralizar" - `deslocamento_para_centralizar`
#       põe o IMPRESSO (não o retângulo da página, que tem margens diferentes
#       dos dois lados: era o 15 x 53 do teste do Kaique) no meio da área branca.
#   D-473: a tela e o PDF usam estas mesmas contas (a tela desenha a página no
#       retângulo de `retangulo_na_folha`; o PDF cola com compor_na_folha).
#
# Seguro mudar: LADO_DA_CONTA, FRACAO_DO_PAPEL, MENOR_PECA_PX,
# PARTE_DE_FORA_QUE_AVISA (só mudam a sensibilidade da medida e do aviso).
# Arriscado: o referencial (deslocamento = fração da ÁREA BRANCA a partir do
# CENTRO): é o mesmo de ConfigPagina.conteudo_deslocamento e de
# compor_na_folha; projeto salvo mudaria de lugar.

# Lado maior, em pontos, da cópia reduzida em que o impresso é medido. A
# medida é em fração, então o tamanho só muda o tempo (~5 ms nesta medida).
LADO_DA_CONTA = 1200
# Ponto mais escuro que esta fração do nível do papel conta como impresso.
FRACAO_DO_PAPEL = 0.75
# Pecinha de tinta menor que isto (pontos da cópia reduzida) é poeira.
MENOR_PECA_PX = 6
# Aviso do D-017: a partir desta fração do impresso fora da área branca
# (0,05%: um pedaço de letra numa página de texto). Abaixo disso é o
# arredondamento da beirada.
PARTE_DE_FORA_QUE_AVISA = 0.0005
# A caixa do "Centralizar" (caixa_do_impresso): letras a menos de 2% do lado
# maior da página umas das outras são o mesmo bloco; bloco com menos de 2% do
# impresso (marca-d'água, resto de cabeçalho cortado) não entra na caixa.
BLOCO_DO_IMPRESSO = 0.02
MENOR_BLOCO = 0.02


def tamanho_da_folha_px(
    tamanho_folha_cm: tuple[float, float] | None,
    dpi: float,
    tamanho_conteudo_px: tuple[int, int],
) -> tuple[int, int]:
    """A ÁREA BRANCA em pontos: a folha escolhida (na resolução `dpi`) ou,
    sem folha escolhida, a própria página - o tamanho do conteúdo (D-008).
    É a mesma área que compor_na_folha usa como canvas."""
    if tamanho_folha_cm is None:
        return (int(tamanho_conteudo_px[0]), int(tamanho_conteudo_px[1]))
    return _para_pixels(tamanho_folha_cm, dpi)


def area_branca_que_vale(
    conteudo_px: tuple[int, int],
    tamanho_folha_cm: tuple[float, float] | None,
    dpi: float,
    escala: float = 1.0,
    mexido_a_mao: bool = False,
) -> tuple[tuple[int, int], bool]:
    """A área branca que compor_na_folha vai usar DE VERDADE, em pontos, e se
    o mover/tamanho vale nela: (área, vale). `vale` False quando
    compor_na_folha devolve o conteúdo como está - sem folha escolhida e sem a
    marca de mexido (o de sempre), ou o conteúdo que não cabe na folha sem a
    marca (a rede de segurança): aí a área é o próprio conteúdo e ele fica
    onde está. É o que a ferramenta Mover mostra (D-473: a tela igual ao PDF)
    e o que parte_impressa_de_fora mede. Arriscado: mudar sem mudar
    compor_na_folha junto (a tela deixaria de mostrar o que sai)."""
    largura, altura = int(conteudo_px[0]), int(conteudo_px[1])
    if dpi <= 0 or largura <= 0 or altura <= 0:
        return ((largura, altura), False)
    if tamanho_folha_cm is None and not mexido_a_mao:
        return ((largura, altura), False)
    folha_px = tamanho_da_folha_px(tamanho_folha_cm, dpi, (largura, altura))
    if folha_px[0] <= 0 or folha_px[1] <= 0:
        return ((largura, altura), False)
    if not mexido_a_mao and (largura * escala > folha_px[0] or altura * escala > folha_px[1]):
        return ((largura, altura), False)
    return (folha_px, True)


def retangulo_na_folha(
    escala: float,
    deslocamento: tuple[float, float],
    folha_px: tuple[int, int],
    conteudo_px: tuple[int, int],
) -> tuple[float, float, float, float]:
    """Onde o conteúdo fica na área branca: (x, y, w, h) em fração dela,
    podendo passar de 0-1 (o conteúdo que passou da beirada, D-017). A conta
    é a de compor_na_folha: o conteúdo escalado, centrado, mais o
    deslocamento (fração da área branca a partir do centro)."""
    largura_folha, altura_folha = folha_px
    largura_conteudo, altura_conteudo = conteudo_px
    if largura_folha <= 0 or altura_folha <= 0:
        return (0.0, 0.0, 1.0, 1.0)
    w = (largura_conteudo * float(escala)) / largura_folha
    h = (altura_conteudo * float(escala)) / altura_folha
    dx, dy = (tuple(deslocamento) + (0.0, 0.0))[:2]
    return (0.5 - w / 2 + float(dx), 0.5 - h / 2 + float(dy), w, h)


def escala_e_deslocamento(
    retangulo: tuple[float, float, float, float],
    folha_px: tuple[int, int],
    conteudo_px: tuple[int, int],
) -> tuple[float, tuple[float, float]]:
    """O inverso de `retangulo_na_folha`: (escala, deslocamento) do
    retângulo (x, y, w, h) em fração da área branca."""
    x, y, w, h = retangulo
    largura_folha, altura_folha = folha_px
    largura_conteudo, altura_conteudo = conteudo_px
    if (largura_folha <= 0 or altura_folha <= 0
            or largura_conteudo <= 0 or altura_conteudo <= 0):
        return (1.0, (0.0, 0.0))
    escala_w = (w * largura_folha) / largura_conteudo
    escala_h = (h * altura_folha) / altura_conteudo
    # os dois eixos escalam junto (mesma proporcao) quando o retangulo vem de
    # retangulo_na_folha; a media absorve qualquer arredondamento de px.
    escala = (escala_w + escala_h) / 2
    return (escala, ((x + w / 2) - 0.5, (y + h / 2) - 0.5))


def _cinza_reduzido(img: np.ndarray) -> np.ndarray:
    """A página em cinza, reduzida a LADO_DA_CONTA no lado maior."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img[..., :3], cv2.COLOR_BGR2GRAY)
    lado = max(cinza.shape[:2])
    if lado > LADO_DA_CONTA:
        fator = LADO_DA_CONTA / lado
        cinza = cv2.resize(cinza, (max(1, round(cinza.shape[1] * fator)),
                                   max(1, round(cinza.shape[0] * fator))),
                           interpolation=cv2.INTER_AREA)
    return cinza


def mascara_do_impresso(img: np.ndarray, sem_o_que_encosta: bool = True) -> np.ndarray | None:
    """O que está IMPRESSO na página (texto, desenho, número), numa cópia
    reduzida: True onde há tinta. O papel em branco da margem fica de fora,
    e também o fundo do scanner - a peça escura que encosta na beirada da
    página e é comprida (um quarto do lado) ou grande (um décimo da página),
    como a faixa preta do scanner e a sombra da lombada: não é o que se
    imprime. Poeira (peça menor que MENOR_PECA_PX) também sai.
    sem_o_que_encosta=True (o de fábrica): sai também QUALQUER peça que
    encosta na beirada da página - achado nos prints da etapa 5 no "La vida
    eterna": a marca-d'água do site cortada na beirada puxava o meio do
    "Centralizar" para o lado, e os restos escuros do scanner colados na
    beirada davam o aviso do D-017 sem nada impresso sair. Ressalva: a letra
    que JÁ estava cortada na beirada da página também fica de fora da conta.
    False: só o fundo grande do scanner sai (o jeito do primeiro rascunho).
    None: sem imagem, ou sem cv2."""
    if img is None or getattr(img, "size", 0) == 0 or cv2 is None:
        return None
    cinza = _cinza_reduzido(img)
    altura, largura = cinza.shape[:2]
    papel = float(np.percentile(cinza, 90))
    tinta = (cinza < papel * FRACAO_DO_PAPEL).astype(np.uint8)
    if not tinta.any():
        return tinta.astype(bool)
    quantas, rotulos, medidas, _centros = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    x, y, w, h, area = (medidas[:, i] for i in range(5))
    encosta = (x == 0) | (y == 0) | (x + w >= largura) | (y + h >= altura)
    fundo = encosta & ((w >= 0.25 * largura) | (h >= 0.25 * altura) | (area >= 0.10 * largura * altura)
                       | bool(sem_o_que_encosta))
    fica = ~fundo & (area >= MENOR_PECA_PX)
    fica[0] = False                                   # o rótulo 0 é o papel
    return fica[rotulos]


def caixa_do_impresso(img: np.ndarray) -> tuple[float, float, float, float] | None:
    """A caixa do que está impresso, (x0, y0, x1, y1) em fração da página
    (0 = beirada de cima/esquerda). None quando a página não tem impresso
    (em branco) ou não dá para medir. É a base do "Centralizar" e do ímã
    das linhas de apoio, como no Photoshop (a camada gruda pelos pontos que
    têm desenho, não pela moldura transparente).

    Só os BLOCOS do impresso entram (achado nos prints da etapa 5, "La vida
    eterna" página 7): as letras próximas são juntadas em blocos (uma
    dilatação de BLOCO_DO_IMPRESSO do lado maior da página) e fica de fora o
    bloco com menos de MENOR_BLOCO do impresso - as letrinhas soltas da
    marca-d'água do site no pé da página, o resto do cabeçalho cortado na
    beirada, poeira grande. O texto, o desenho, a nota de rodapé e o título
    ficam. Seguro mudar: os dois números (mais ou menos rigor)."""
    mascara = mascara_do_impresso(img)
    if mascara is None or not mascara.any():
        return None
    altura, largura = mascara.shape[:2]
    lado = max(3, round(BLOCO_DO_IMPRESSO * max(altura, largura)) | 1)
    juntos = cv2.dilate(mascara.astype(np.uint8),
                        cv2.getStructuringElement(cv2.MORPH_RECT, (lado, lado)))
    _quantos, blocos = cv2.connectedComponents(juntos, connectivity=8)
    tinta_por_bloco = np.bincount(blocos[mascara], minlength=_quantos)
    fica = tinta_por_bloco >= max(1, MENOR_BLOCO * tinta_por_bloco.sum())
    fica[0] = False
    if not fica.any():
        fica[int(np.argmax(tinta_por_bloco))] = True
    principal = mascara & fica[blocos]
    colunas = np.flatnonzero(principal.any(axis=0))
    linhas = np.flatnonzero(principal.any(axis=1))
    return (float(colunas[0] / largura), float(linhas[0] / altura),
            float((colunas[-1] + 1) / largura), float((linhas[-1] + 1) / altura))


def deslocamento_para_centralizar(
    caixa_do_impresso_: tuple[float, float, float, float] | None,
    escala: float,
    folha_px: tuple[int, int],
    conteudo_px: tuple[int, int],
) -> tuple[float, float]:
    """O deslocamento (o formato de ConfigPagina.conteudo_deslocamento) que
    põe o meio do IMPRESSO no meio da área branca, nas duas direções, com o
    tamanho `escala` de agora (D-303: "precisamos centralizar"). Página sem
    impresso: o meio da página no meio da área branca (0, 0)."""
    if caixa_do_impresso_ is None:
        return (0.0, 0.0)
    _x, _y, w, h = retangulo_na_folha(escala, (0.0, 0.0), folha_px, conteudo_px)
    x0, y0, x1, y1 = caixa_do_impresso_
    return (float(w * (0.5 - (x0 + x1) / 2)), float(h * (0.5 - (y0 + y1) / 2)))


def parte_impressa_de_fora(
    conteudo: np.ndarray,
    tamanho_folha_cm: tuple[float, float] | None,
    dpi: float,
    escala: float = 1.0,
    deslocamento: tuple[float, float] = (0.0, 0.0),
    mexido_a_mao: bool = False,
) -> float:
    """Que parte do que está impresso fica FORA da área branca quando o
    conteúdo é colado por compor_na_folha com estes mesmos números (0 a 1;
    D-017). Segue as mesmas saídas de compor_na_folha: sem folha e sem a
    marca de mexido, ou o conteúdo que não cabe numa folha sem a marca (a
    rede de segurança devolve o conteúdo inteiro), nada fica de fora.
    Conteúdo que fica inteiro dentro da área branca: 0 sem medir nada (é o
    caso de quase toda página: a medida não custa nada nelas)."""
    if conteudo is None or getattr(conteudo, "size", 0) == 0 or dpi <= 0:
        return 0.0
    conteudo_px = (conteudo.shape[1], conteudo.shape[0])
    folha_px, vale = area_branca_que_vale(conteudo_px, tamanho_folha_cm, dpi, escala,
                                          mexido_a_mao)
    if not vale:
        return 0.0
    x, y, w, h = retangulo_na_folha(escala, deslocamento, folha_px, conteudo_px)
    # meio ponto da área branca de folga: o arredondamento da colagem
    folga_x, folga_y = 0.5 / folha_px[0], 0.5 / folha_px[1]
    if x >= -folga_x and y >= -folga_y and x + w <= 1 + folga_x and y + h <= 1 + folga_y:
        return 0.0
    mascara = mascara_do_impresso(conteudo)
    if mascara is None or not mascara.any():
        return 0.0
    linhas, colunas = np.nonzero(mascara)
    altura, largura = mascara.shape[:2]
    na_folha_x = x + (colunas + 0.5) / largura * w
    na_folha_y = y + (linhas + 0.5) / altura * h
    fora = ((na_folha_x < -folga_x) | (na_folha_x > 1 + folga_x)
            | (na_folha_y < -folga_y) | (na_folha_y > 1 + folga_y))
    return float(fora.mean())


def impresso_fica_de_fora(fracao: float) -> bool:
    """A medida de `parte_impressa_de_fora` pede o aviso do D-017?"""
    return fracao > PARTE_DE_FORA_QUE_AVISA
