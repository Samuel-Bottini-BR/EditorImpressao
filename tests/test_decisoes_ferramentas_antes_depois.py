"""D-612, terceira parte (04/11/2026): com o "antes / depois" ligado, Mover, Cortar, Endireitar e as
ferramentas de marcar agem no "depois"; o "antes" fica sÃ³ para olhar.

Perguntas ao Samuel: "O Cortar, o Endireitar e o marcar tambÃ©m tÃªm que funcionar em 'Duas lado a
lado' e em 'antes / depois', como o Mover?" â†’ "1- sim"; "Com 'antes / depois' ligado, as
ferramentas mexem na imagem do 'depois', e o 'antes' fica sÃ³ para olhar? Sugiro que sim." â†’
"1- ok".

O "antes / depois" da Ã¡rea de trabalho (D-577) Ã© UMA pÃ¡gina com a linha azul que se arrasta: Ã 
esquerda da linha o "depois" (como vai sair), Ã  direita o "antes" (o Original). O defeito (achado do
agente mover-parou, print p3): com ele ligado, o arrasto de qualquer ferramenta caÃ­a no "antes /
depois", que sÃ³ sabe arrastar a linha. Em `bcae6968` os testes de reversÃ£o falham.

O que se mede: a mÃ£o aperta no que estÃ¡ Ã  vista embaixo do ponto (como em
test_decisoes_mover_lado.py): Ã  esquerda da linha (o "depois") a ferramenta age; Ã  direita (o
"antes") nada muda; a linha continua se arrastando.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint  # noqa: E402

from tests.test_decisoes_mover import (  # noqa: E402,F401 - as mesmas peÃ§as das provas do Mover
    _assentar,
    _esperar,
    _pdf,
    app,
    janela,
    pasta,
)
from tests.test_decisoes_mover_lado import _alvo, _arrastar_na_tela  # noqa: E402


def _no_antes_depois(janela, tmp_path, ferramenta: str, filtro: str = "preto_e_branco"):
    """Livro aberto, pÃ¡gina 2 com um filtro (o "antes / depois" sÃ³ compara com filtro), a
    ferramenta escolhida e o botÃ£o "antes / depois" clicado na barra de baixo."""
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf"))
    janela.show()
    tela = janela.tela_conferir
    tela.ir_para_pagina(1)
    tela._escolher_filtro(filtro)          # como os cartÃµes do painel Filtro
    tela.escolher_ferramenta(ferramenta)
    tela.botao_antes_depois.click()
    _assentar()
    vista = tela.vista_antes_depois
    assert tela.comparando and tela.vista_da_pagina.currentWidget() is vista
    # as duas prÃ©vias (o filtro e o Original) chegam por trÃ¡s; cada chegada redesenha
    assert _esperar(lambda: (tela._acertar_a_vista_da_pagina() or True)
                    and vista.depois is not None and vista.antes is not None, 30)
    _assentar(5)
    return tela, vista


def _ponto(vista, fx: float, fy: float = 0.5) -> QPoint:
    """O ponto (fx, fy) da pÃ¡gina no "antes / depois" (fraÃ§Ã£o da pÃ¡gina desenhada)."""
    area = vista._area(vista.depois)
    return QPoint(int(area.left() + fx * area.width()), int(area.top() + fy * area.height()))


def _peca(tela, aba):
    return tela.editor_selecao if aba == "marcar" else tela.visualizadores[aba]


# --- as ferramentas agem no "depois" ---------------------------------------------------------

def test_reversao_d612_mover_arrasta_no_depois(janela, tmp_path):
    """Mover com "antes / depois": a mÃ£o aperta no "depois" (Ã  esquerda da linha) e arrasta; o
    conteÃºdo anda (uma aÃ§Ã£o), o "antes / depois" continua ligado."""
    tela, vista = _no_antes_depois(janela, tmp_path, "mover")
    pagina = janela.projeto.paginas[1]
    feitas = len(janela.acoes.feitas)
    de = _ponto(vista, 0.25)
    _arrastar_na_tela(tela, de, -40)
    assert pagina.conteudo_deslocamento[0] < -0.03, (
        f"nÃ£o andou: embaixo da mÃ£o estava {type(_alvo(tela, de)[0]).__name__}")
    assert len(janela.acoes.feitas) == feitas + 1
    assert tela.comparando and tela.vista_da_pagina.currentWidget() is vista


def test_reversao_d612_cortar_puxa_a_beirada_no_depois(janela, tmp_path):
    """Cortar com "antes / depois": a mÃ£o puxa a beirada da esquerda do corte (no "depois")
    para dentro; o corte muda."""
    tela, vista = _no_antes_depois(janela, tmp_path, "cortar")
    vis = tela.visualizadores["bordas"]
    pagina = janela.projeto.paginas[1]
    antes = tuple(pagina.recorte or (0.0, 0.0, 1.0, 1.0))
    if vista.isAncestorOf(vis):
        vis.grab()
        de = vis.mapTo(vista, vis._alcas(vis._retangulo_recorte())["o"])
    else:
        de = _ponto(vista, 0.0)
    _arrastar_na_tela(tela, de, 40)
    depois = tuple(pagina.recorte or (0.0, 0.0, 1.0, 1.0))
    assert depois[0] > antes[0] + 0.02, (
        f"o corte nÃ£o mudou: embaixo da mÃ£o estava {type(_alvo(tela, de)[0]).__name__}")


def test_reversao_d612_endireitar_linha_no_depois(janela, tmp_path):
    """Endireitar com "antes / depois": a linha torta desenhada no "depois" gira a pÃ¡gina."""
    tela, vista = _no_antes_depois(janela, tmp_path, "endireitar")
    vis = tela.visualizadores["angulo"]
    assert _esperar(lambda: vis.angulo_conhecido)
    pagina = janela.projeto.paginas[1]
    de = _ponto(vista, 0.05)
    largura = int(vista._area(vista.depois).width() * 0.4)
    _arrastar_na_tela(tela, de, largura, -int(largura * 0.06))
    assert pagina.angulo_manual is not None, (
        f"nÃ£o girou: embaixo da mÃ£o estava {type(_alvo(tela, de)[0]).__name__}")


def test_reversao_d612_retangulo_marca_no_depois(janela, tmp_path):
    """RetÃ¢ngulo com "antes / depois": o retÃ¢ngulo desenhado no "depois" vira uma regiÃ£o."""
    tela, vista = _no_antes_depois(janela, tmp_path, "retangulo")
    editor = tela.editor_selecao
    antes = len(editor.selecao.regioes)
    de = _ponto(vista, 0.1, 0.3)
    _arrastar_na_tela(tela, de, 50, 50)
    assert len(editor.selecao.regioes) == antes + 1, (
        f"nada marcado: embaixo da mÃ£o estava {type(_alvo(tela, de)[0]).__name__}")


# --- o "antes" sÃ³ para olhar; a linha continua; o resto como antes (D-605) -------------------

@pytest.mark.parametrize("ferramenta,aba", [("mover", "mover"), ("retangulo", "marcar")])
def test_d612_no_antes_nada_muda_e_a_linha_se_arrasta(janela, tmp_path, ferramenta, aba):
    """"o 'antes' fica sÃ³ para olhar": apertar e arrastar Ã  direita da linha nÃ£o mexe em nada; a
    linha azul continua se arrastando (D-577), e a ferramenta acompanha o lado novo."""
    tela, vista = _no_antes_depois(janela, tmp_path, ferramenta)
    pagina = janela.projeto.paginas[1]
    feitas = len(janela.acoes.feitas)
    de = _ponto(vista, 0.75)
    alvo, _p = _alvo(tela, de)
    peca = _peca(tela, aba)
    assert alvo is vista
    _arrastar_na_tela(tela, de, -40, 30)
    assert len(janela.acoes.feitas) == feitas
    assert tuple(pagina.conteudo_deslocamento) == (0.0, 0.0)
    # a linha (no meio) se arrasta para a direita: o "depois" cresce
    _arrastar_na_tela(tela, _ponto(vista, 0.5), int(vista._area(vista.depois).width() * 0.3))
    assert vista.posicao > 0.7
    assert _alvo(tela, _ponto(vista, 0.65))[0] in (peca, *peca.findChildren(type(peca)))


@pytest.mark.parametrize("ferramenta,aba", [("mover", "mover"), ("cortar", "bordas"),
                                            ("endireitar", "angulo"), ("retangulo", "marcar")])
def test_d612_desligar_o_antes_depois_devolve_a_peca(janela, tmp_path, ferramenta, aba):
    """D-605: desligar o "antes / depois" volta a "Uma pÃ¡gina" de sempre, com a peÃ§a da
    ferramenta no lugar dela, inteira (sem recorte de lado)."""
    tela, vista = _no_antes_depois(janela, tmp_path, ferramenta)
    tela.botao_antes_depois.click()
    _assentar()
    peca = _peca(tela, aba)
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem
    assert tela.paginas_de_imagem[aba].isAncestorOf(peca) and peca.isVisible()
    assert peca.mask().isEmpty()


def test_d612_mao_no_antes_depois_como_antes(janela, tmp_path):
    """Guarda: a MÃ£o sÃ³ olha; no "antes / depois" ela continua como era (sem o editor por cima)."""
    tela, vista = _no_antes_depois(janela, tmp_path, "mao")
    assert not vista.isAncestorOf(tela.editor_selecao)
    assert _alvo(tela, _ponto(vista, 0.25))[0] is vista


def test_d612_os_rotulos_e_a_linha_continuam_a_vista(janela, tmp_path):
    """D-605/D-577: com a peça da ferramenta no "depois", as caixinhas dos rótulos ("antes:
    Original", "depois: ...") e a pega da linha continuam desta vista (não ficam por baixo)."""
    tela, vista = _no_antes_depois(janela, tmp_path, "mover")
    for caixa in vista._caixas_dos_rotulos(vista._area(vista.depois)):
        assert _alvo(tela, caixa.center().toPoint())[0] is vista
    assert _alvo(tela, _ponto(vista, vista.posicao))[0] is vista
