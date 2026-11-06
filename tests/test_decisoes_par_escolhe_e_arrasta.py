"""D-612 (a), resposta do Samuel (04/11/2026) à pergunta "O mesmo clique na outra página do par já
escolhe e arrasta?": "ok". Vale para o Mover, o Cortar e as ferramentas de marcar.

Antes (entrega de 04/11), o aperto na outra página do par só a escolhia; o arrasto valia do aperto
seguinte. Agora o mesmo aperto escolhe a página e o arrasto já mexe nela. No Endireitar (fora da
resposta) continua só escolhendo.

O que se mede: a mão aperta na outra página do par (no que está à vista) e arrasta; a página da
vez passa a ser ela e o que a ferramenta faz chega ao projeto dela. Em `d2567fab` os testes de
reversão falham (a página muda, mas nada se mexe).
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint  # noqa: E402

from tests.test_decisoes_mover import _assentar, _esperar, _pdf, app, janela, pasta  # noqa: E402,F401
from tests.test_decisoes_mover_lado import _arrastar_na_tela  # noqa: E402
from ui.widgets.paginas_rolando import DUAS  # noqa: E402


def _nos_pares(janela, tmp_path, ferramenta: str):
    """Página 2 (a da esquerda do par 2-3) da vez, a ferramenta e "Duas lado a lado"."""
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf"))
    janela.show()
    tela = janela.tela_conferir
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta(ferramenta)
    tela.botoes_mostrar[DUAS].click()
    _assentar(10)
    # a página 3 (a outra do par) já tem a prévia: a ferramenta pega o aperto nela
    assert _esperar(lambda: tela.previas.ja_pronta(2, tela._dpi_atual) is not None, 30)
    return tela


def _na_outra(tela, fx: float, fy: float) -> QPoint:
    """O ponto (fx, fy) da página 3 (a outra do par), na vista da página."""
    pares = tela.lado_a_lado
    pares.grab()
    ret = next(r for p, r in pares.retangulos() if pares.indices[p] == 2)
    vista = tela.vista_da_pagina.currentWidget()
    return pares.folhas.mapTo(vista, QPoint(ret.left() + int(fx * ret.width()),
                                            ret.top() + int(fy * ret.height())))


def test_reversao_d612_a_mover_o_mesmo_aperto_escolhe_e_arrasta(janela, tmp_path):
    tela = _nos_pares(janela, tmp_path, "mover")
    _arrastar_na_tela(tela, _na_outra(tela, 0.5, 0.4), 50)
    assert tela.indice_pagina == 2
    assert janela.projeto.paginas[2].conteudo_deslocamento[0] > 0.04, "o arrasto não começou"
    assert tuple(janela.projeto.paginas[1].conteudo_deslocamento) == (0.0, 0.0)


def test_reversao_d612_b_cortar_o_mesmo_aperto_escolhe_e_puxa_a_beirada(janela, tmp_path):
    tela = _nos_pares(janela, tmp_path, "cortar")
    vis = tela.visualizadores["bordas"]
    # o Cortar mostra a página sem cortar (outra prévia): a da página 3 já desenhada
    tela.ir_para_pagina(2)
    assert _esperar(lambda: vis._pixmap is not None and not vis.carregando, 30)
    tela.ir_para_pagina(1)
    assert _esperar(lambda: vis._pixmap is not None and not vis.carregando, 30)
    antes = tuple(janela.projeto.paginas[2].recorte or (0.0, 0.0, 1.0, 1.0))
    # a beirada da direita da página 3, no meio da altura: a alça do corte
    _arrastar_na_tela(tela, _na_outra(tela, 1.0, 0.5) - QPoint(2, 0), -40)
    assert tela.indice_pagina == 2
    depois = tuple(janela.projeto.paginas[2].recorte or (0.0, 0.0, 1.0, 1.0))
    assert depois[2] < antes[2] - 0.02, (antes, depois, vis.retangulos_das_pegas())


def test_reversao_d612_c_retangulo_o_mesmo_aperto_escolhe_e_marca(janela, tmp_path):
    tela = _nos_pares(janela, tmp_path, "retangulo")
    editor = tela.editor_selecao
    _arrastar_na_tela(tela, _na_outra(tela, 0.3, 0.3), 50, 50)
    assert tela.indice_pagina == 2
    assert len(editor.selecao.regioes) == 1, "o retângulo não foi marcado no mesmo aperto"
    assert janela.projeto.paginas[2].selecao is not None


def test_d612_endireitar_na_outra_pagina_so_escolhe(janela, tmp_path):
    """Guarda: no Endireitar (fora da resposta) o aperto na outra página só a escolhe."""
    tela = _nos_pares(janela, tmp_path, "endireitar")
    _arrastar_na_tela(tela, _na_outra(tela, 0.2, 0.5), 80, -6)
    assert tela.indice_pagina == 2
    assert janela.projeto.paginas[2].angulo_manual is None
