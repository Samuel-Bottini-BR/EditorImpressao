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

def tamanho_da_folha_cabe(
    tamanho_folha_cm: tuple[float, float] | None,
    tamanho_recorte_cm: tuple[float, float],
    tolerancia_cm: float = 1e-3,
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
    """
    if tamanho_folha_cm is None or conteudo is None or conteudo.size == 0:
        return conteudo
    if dpi <= 0:
        return conteudo

    altura_conteudo, largura_conteudo = conteudo.shape[:2]
    largura_escalada = largura_conteudo * escala
    altura_escalada = altura_conteudo * escala

    largura_folha_px, altura_folha_px = _para_pixels(tamanho_folha_cm, dpi)
    if largura_folha_px <= 0 or altura_folha_px <= 0:
        return conteudo

    # rede de seguranca: nao cabe -> devolve o conteudo original, intacto
    if largura_escalada > largura_folha_px or altura_escalada > altura_folha_px:
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
# Conversao escala+deslocamento <-> retangulo (preparacao para o item 4:
# arrastar o conteudo com guias/ima, fora desta entrega - ver o plano)
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
    entendem. Ainda não é chamada por nenhuma tela - é o terreno preparado
    para o item 4 do plano (arrastar o conteúdo), implementado depois."""
    largura_folha_px, altura_folha_px = _para_pixels(tamanho_folha_cm, dpi)
    if largura_folha_px <= 0 or altura_folha_px <= 0:
        return (0.0, 0.0, 1.0, 1.0)

    largura_conteudo_px, altura_conteudo_px = tamanho_conteudo_px
    w = (largura_conteudo_px * escala) / largura_folha_px
    h = (altura_conteudo_px * escala) / altura_folha_px
    dx, dy = deslocamento
    x = 0.5 - w / 2 + dx
    y = 0.5 - h / 2 + dy
    return (x, y, w, h)


def deslocamento_do_retangulo(
    retangulo: tuple[float, float, float, float],
    tamanho_folha_cm: tuple[float, float],
    tamanho_conteudo_px: tuple[int, int],
    dpi: float,
) -> tuple[float, tuple[float, float]]:
    """O inverso de `conteudo_como_retangulo`: devolve (escala, deslocamento)
    a partir de um retângulo em fração da folha."""
    x, y, w, h = retangulo
    largura_folha_px, altura_folha_px = _para_pixels(tamanho_folha_cm, dpi)
    largura_conteudo_px, altura_conteudo_px = tamanho_conteudo_px

    if (largura_folha_px <= 0 or altura_folha_px <= 0
            or largura_conteudo_px <= 0 or altura_conteudo_px <= 0):
        return (1.0, (0.0, 0.0))

    escala_w = (w * largura_folha_px) / largura_conteudo_px
    escala_h = (h * altura_folha_px) / altura_conteudo_px
    # os dois eixos escalam junto (mesma proporcao) quando o retangulo vem de
    # conteudo_como_retangulo; a media absorve qualquer arredondamento de px.
    escala = (escala_w + escala_h) / 2
    dx = (x + w / 2) - 0.5
    dy = (y + h / 2) - 0.5
    return (escala, (dx, dy))
