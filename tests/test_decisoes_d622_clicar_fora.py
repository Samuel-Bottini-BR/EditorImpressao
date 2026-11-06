"""D-622 (Samuel, 04/11/2026, print a-74, Mover em "Duas lado a lado"): "quando eu clicar fora da
folha ele desseleciona o que está selecionado, para eu selecionar de novo tenho que clicar de novo
na coisa selecionada como no photoshop." Livro: "Clicar fora da folha (no cinza) tira a seleção
(cantos azuis, página escolhida); para escolher de novo, clica-se na página, como no Photoshop."
Vale nos pares e em "Uma página".

O que se mede: com a mão, o clique no cinza apaga os cantos azuis e o contorno do Mover (o que o
visualizador DESENHA: os pontos azuis dos cantos) e, nos pares, o quadro da página da vez; clicar
na página escolhe de novo (cantos de volta) e o arrasto continua movendo. Em `d2567fab` os testes de
reversão falham (os cantos não somem).
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint  # noqa: E402

from tests.test_decisoes_mover import _assentar, _esperar, _no_mover, app, janela, pasta  # noqa: E402,F401
from tests.test_decisoes_mover_lado import _alvo, _arrastar_na_tela, _lugar_da_vez  # noqa: E402
from ui.widgets.paginas_rolando import DUAS  # noqa: E402


def _cantos_a_vista(vis) -> bool:
    """Os quatro cantos azuis estão desenhados? (a cor do meio de cada canto, no desenho)"""
    imagem = vis.grab().toImage()
    escala = imagem.width() / max(1, vis.width())
    azuis = 0
    for nome in ("no", "ne", "so", "se"):
        p = vis._alcas(vis._area_do_conteudo())[nome]
        x, y = int(p.x() * escala), int(p.y() * escala)
        if not (0 <= x < imagem.width() and 0 <= y < imagem.height()):
            continue
        cor = imagem.pixelColor(x, y)
        azuis += cor.blue() > 150 and cor.red() < 120
    return azuis >= 3


def test_reversao_d622_uma_pagina_clicar_fora_larga_e_na_pagina_escolhe(janela, tmp_path):
    """"Uma página": clicar no cinza em volta da página → os cantos somem; clicar (e arrastar) na
    página → os cantos voltam e a página anda (D-541 continua)."""
    tela, vis = _no_mover(janela, tmp_path, 1)
    assert _cantos_a_vista(vis)
    vista = tela.vista_da_pagina.currentWidget()
    area = vis._area
    fora = vis.mapTo(vista, QPoint(max(2, area.left() // 2), area.center().y()))
    assert _alvo(tela, fora)[0] is vis
    _arrastar_na_tela(tela, fora, 0)
    assert not _cantos_a_vista(vis), "os cantos não sumiram com o clique fora"
    pagina = janela.projeto.paginas[1]
    _arrastar_na_tela(tela, vis.mapTo(vista, area.center()), -30)
    assert _cantos_a_vista(vis)
    assert pagina.conteudo_deslocamento[0] < -0.01


def test_reversao_d622_nos_pares_clicar_no_cinza_larga_e_na_pagina_escolhe(janela, tmp_path):
    """"Duas lado a lado": clicar no cinza abaixo do par → somem os cantos e o quadro azul da página
    da vez; clicar na página da vez → voltam."""
    tela, vis = _no_mover(janela, tmp_path, 1)
    tela.botoes_mostrar[DUAS].click()
    _assentar(10)
    pares = tela.lado_a_lado
    lugar = _lugar_da_vez(tela)
    vis.grab()
    assert _cantos_a_vista(vis) and not pares.sem_escolha
    # o cinza: na altura da página, longe dela para o lado de fora (a da vez é a da esquerda)
    fora = QPoint(max(2, lugar.left() // 2), lugar.center().y())
    _arrastar_na_tela(tela, fora, 0)
    assert pares.sem_escolha, "o quadro azul da página da vez continua"
    assert not _cantos_a_vista(vis), "os cantos não sumiram"
    assert tela.indice_pagina == 1                       # a página da vez não muda
    _arrastar_na_tela(tela, lugar.center(), 0)
    assert not pares.sem_escolha and _cantos_a_vista(vis)


def test_d622_outra_ferramenta_nos_pares_como_antes(janela, tmp_path):
    """Guarda (D-605): fora do Mover (Mão), o clique no cinza dos pares não apaga o quadro."""
    tela, _vis = _no_mover(janela, tmp_path, 1)
    tela.escolher_ferramenta("mao")
    tela.botoes_mostrar[DUAS].click()
    _assentar(10)
    lugar = _lugar_da_vez(tela)
    _arrastar_na_tela(tela, QPoint(max(2, lugar.left() // 2), lugar.center().y()), 0)
    assert not tela.lado_a_lado.sem_escolha
