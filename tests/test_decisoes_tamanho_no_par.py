"""D-612, pedido do Samuel depois de testar o Mover nos pares (04/11/2026): "ele funciona mas eu não
gostei do tamanho que aparece a pagina quando começa a mover ela, ela deveria continuar o preview das
duas do mesmo tamanho." Vale também para Cortar, Endireitar e marcar nos pares.

O defeito (ressalva 1 da entrega do Mover, `472e410c`/`07c051fb`): nos pares, a página da ferramenta
ficava 8 pontos menor que a outra do par e, com o conteúdo passando da beirada, menor ainda (a vista
encolhia para caber a página inteira). Agora a página da ferramenta tem o tamanho da prévia: a área
branca do Mover é o lugar da página no par; a parte de fora e os cantos azuis aparecem em volta.

O que se mede: o retângulo em que a ferramenta desenha a página (Visualizador._area, a área branca
no Mover; EditorSelecao._calcular_area na de marcar), levado para as coordenadas do desenho dos
pares, contra o lugar da página da vez e a altura da outra página do par. Em `07c051fb` os testes
de reversão falham.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint, QRect  # noqa: E402

from tests.test_decisoes_mover import _assentar, _esperar, _pdf, app, janela, pasta  # noqa: E402,F401
from tests.test_decisoes_mover_lado import _alvo, _arrastar_na_tela, _lugar_da_vez  # noqa: E402
from ui.widgets.paginas_rolando import DUAS  # noqa: E402


def _nos_pares(janela, tmp_path, ferramenta: str, pagina: int = 1):
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf"))
    janela.show()
    tela = janela.tela_conferir
    tela.ir_para_pagina(pagina)
    tela.escolher_ferramenta(ferramenta)
    tela.botoes_mostrar[DUAS].click()
    _assentar(10)
    return tela


def _lugares(tela):
    """(o lugar da página da vez, o da outra página do par), nas coordenadas do desenho dos pares."""
    pares = tela.lado_a_lado
    pares.grab()
    da_vez = next(r for i, r in pares.retangulos() if i == pares.atual)
    linha = pares._linha_de(pares.atual)
    outra = next(r for i, r in pares.retangulos() if i != pares.atual and pares._linha_de(i) == linha)
    return da_vez, outra


def _na_tela_dos_pares(tela, peca, ret: QRect) -> QRect:
    """`ret` (coordenadas da peça) nas coordenadas do desenho dos pares."""
    canto = peca.mapTo(tela.lado_a_lado.folhas, ret.topLeft())
    return QRect(canto, ret.size())


def _perto(a: QRect, b: QRect, folga: int = 2) -> bool:
    return all(abs(x - y) <= folga for x, y in ((a.left(), b.left()), (a.top(), b.top()),
                                                 (a.right(), b.right()), (a.bottom(), b.bottom())))


# --- Mover --------------------------------------------------------------------------------

def test_reversao_d612_mover_do_tamanho_da_previa_antes_e_depois_de_mexer(janela, tmp_path):
    """Mover nos pares: a área branca da página da vez tem exatamente o lugar dela no par (o tamanho
    da prévia) e a mesma altura da outra página; depois de arrastar para fora da beirada e de puxar
    o canto, continua do mesmo tamanho. A parte de fora fica à vista em volta, e os cantos azuis
    também (a mão os pega)."""
    tela = _nos_pares(janela, tmp_path, "mover")
    vis = tela.visualizadores["mover"]
    assert _esperar(lambda: vis._pixmap is not None)
    da_vez, outra = _lugares(tela)
    vis.grab()
    assert _perto(_na_tela_dos_pares(tela, vis, vis._area), da_vez), (vis._area, da_vez)
    assert abs(da_vez.height() - outra.height()) <= 1

    # arrastar para fora (a página da vez é a da esquerda: para a esquerda, a margem de fora)
    _arrastar_na_tela(tela, _lugar_da_vez(tela).center(), -int(da_vez.width() * 0.3))
    pagina = janela.projeto.paginas[1]
    assert pagina.conteudo_deslocamento[0] < -0.2
    _assentar(5)
    da_vez, outra = _lugares(tela)
    vis.grab()
    assert _perto(_na_tela_dos_pares(tela, vis, vis._area), da_vez), "a página encolheu ao mover"
    # a parte de fora fica à vista (a peça a mostra, ela não está debaixo de outra página)
    conteudo = _na_tela_dos_pares(tela, vis, vis._area_do_conteudo())
    assert conteudo.left() < da_vez.left() - 10
    fora = QPoint(da_vez.left() - 5, da_vez.center().y())
    assert vis.mask().contains(vis.mapFrom(tela.lado_a_lado.folhas, fora))

    # puxar um canto: continua do tamanho da prévia, e o canto está à vista para a mão
    canto = vis._alcas(vis._area_do_conteudo())["no"]
    vista = tela.vista_da_pagina.currentWidget()
    assert _alvo(tela, vis.mapTo(vista, canto))[0] is vis
    _arrastar_na_tela(tela, vis.mapTo(vista, canto), -20, -20)
    assert pagina.conteudo_escala > 1.02
    da_vez, _outra = _lugares(tela)
    vis.grab()
    assert _perto(_na_tela_dos_pares(tela, vis, vis._area), da_vez)


# --- Cortar, Endireitar, marcar ------------------------------------------------------------

@pytest.mark.parametrize("ferramenta,aba", [("cortar", "bordas"), ("endireitar", "angulo")])
def test_reversao_d612_cortar_e_endireitar_na_altura_da_previa(janela, tmp_path, ferramenta, aba):
    """Cortar e Endireitar nos pares: a página da ferramenta tem a altura da prévia (a mesma da outra
    página do par), no meio do lugar dela."""
    tela = _nos_pares(janela, tmp_path, ferramenta)
    vis = tela.visualizadores[aba]
    assert _esperar(lambda: vis._pixmap is not None)
    da_vez, outra = _lugares(tela)
    vis.grab()
    area = _na_tela_dos_pares(tela, vis, vis._area)
    assert abs(area.height() - da_vez.height()) <= 2, (area, da_vez)
    assert abs(area.top() - da_vez.top()) <= 2
    assert abs(area.center().x() - da_vez.center().x()) <= 2
    assert abs(da_vez.height() - outra.height()) <= 1


def test_reversao_d612_marcar_na_altura_da_previa(janela, tmp_path):
    """Retângulo (marcar) nos pares: a página do editor tem a altura da prévia, no meio do lugar."""
    tela = _nos_pares(janela, tmp_path, "retangulo")
    editor = tela.editor_selecao
    assert _esperar(lambda: editor._pixmap is not None)
    tela._acertar_a_vista_da_pagina()
    da_vez, _outra = _lugares(tela)
    editor.grab()
    area = _na_tela_dos_pares(tela, editor, editor._calcular_area())
    assert abs(area.height() - da_vez.height()) <= 2, (area, da_vez)
    assert abs(area.center().x() - da_vez.center().x()) <= 2


def test_d612_a_outra_pagina_continua_por_cima_e_clicavel(janela, tmp_path):
    """D-605: a outra página do par continua à vista inteira (a peça não a cobre) e o clique nela
    continua escolhendo ela."""
    tela = _nos_pares(janela, tmp_path, "mover")
    vis = tela.visualizadores["mover"]
    assert _esperar(lambda: vis._pixmap is not None)
    _da_vez, outra = _lugares(tela)
    vista = tela.vista_da_pagina.currentWidget()
    centro = tela.lado_a_lado.folhas.mapTo(vista, outra.center())
    assert _alvo(tela, centro)[0] is not vis
    _arrastar_na_tela(tela, centro, 0)
    assert tela.indice_pagina == 2
