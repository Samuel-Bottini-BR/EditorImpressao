"""Texto claro em fundo escuro (item 2.9 da Fase 2, 20/10/2026).

O PEDIDO
    Samuel, conferência 10 (05/10/2026), P9: "(a) Uma caixinha por página,
    'Letra clara em fundo escuro', que o Kaique marca à mão (recomendado)".
    Regra da Fase 2 (13/10/2026): igual ao ScanTailor, desligado de fábrica.

COMO O SCANTAILOR FAZ (OutputGenerator.cpp, v1.2.1)
    A página marcada "claro no escuro" (o contrário de "black on white") é
    INVERTIDA na entrada - a cinza e a colorida, initFilterData(), linhas
    1245-1249 -, passa por toda a saída como se fosse uma página comum
    (achar gravura, igualar a luz, preto e branco, pontinhos) e é invertida DE
    NOVO no fim (linhas 1344-1346 no preto e branco, 1370-1372 nas cores,
    1497-1499 no Misto e na cor). Ou seja: a página sai como entrou - letra
    clara em fundo escuro -, só que limpa: no preto e branco, letra branca em
    fundo preto puro. Ele também tem uma detecção automática
    (BlackOnWhiteEstimator); pela decisão P9 ela NÃO vem: só a caixinha, à mão.

O QUE FAZ AQUI
    ligado(pagina): a caixinha da página (ConfigPagina.claro_no_escuro).
    inverter(img): o invertPixels() do ScanTailor (255 - cada ponto, em cada
    canal). core.pipeline._filtrar usa os dois: inverte a página preparada,
    passa pelo caminho de sempre (marcação de gravura, filtro, "Só as letras")
    e inverte o resultado. Original e "Tirar o fundo" não passam por aqui
    (inverter duas vezes daria a mesma página).

    SUFIXO_DA_GRAVURA: a marcação automática de gravura é feita na página
    invertida (como no ScanTailor). Ligar ou desligar a caixinha muda a
    imagem que o detector vê, então a assinatura da marcação ganha este
    sufixo quando a caixinha está ligada: a parte automática é refeita, e a
    marcação feita à mão fica (core.pipeline.garantir_selecao). Com a
    caixinha desligada a assinatura é a de sempre: nenhum livro já começado
    refaz nada.

O QUE É SEGURO MUDAR
    Os textos da tela (ROTULO_NA_TELA, EXPLICACAO_NA_TELA, FRASE_DO_DESFAZER).

O QUE É ARRISCADO
    - Inverter só na entrada (a página sairia com as cores trocadas: fundo
      branco e letra preta, o contrário do livro).
    - Pôr o sufixo na assinatura com a caixinha desligada (toda página de todo
      livro já começado refaria a marcação de gravura).
"""

from __future__ import annotations

import cv2
import numpy as np

ROTULO_NA_TELA = "Letra clara em fundo escuro"
EXPLICACAO_NA_TELA = (
    "Marque nas páginas em que a letra é clara e o fundo é escuro (por exemplo, "
    "letra branca numa faixa preta). O programa trata a página como se fosse "
    "letra escura em papel claro e, no fim, devolve as cores como no livro: a "
    "letra continua clara e o fundo escuro, só que limpos.")
FRASE_DO_DESFAZER = "Letra clara em fundo escuro na página {pagina}: {estado}"

SUFIXO_DA_GRAVURA = "|claro_no_escuro"


def ligado(pagina) -> bool:
    """A caixinha "Letra clara em fundo escuro" desta página está marcada?
    Objeto sem o campo (projeto em memória de antes do item 2.9): não."""
    return bool(getattr(pagina, "claro_no_escuro", False))


def inverter(img: np.ndarray) -> np.ndarray:
    """O invertPixels() do ScanTailor: 255 menos cada ponto, em cada canal.
    Devolve uma imagem nova (não mexe na de entrada)."""
    return cv2.bitwise_not(img)
