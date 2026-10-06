"""Girar a folha (item 2.3): o que a tela mostra depois do giro.

Consertos pedidos pela gerente em 06/10/2026, a partir do parecer do
verificador (relatorios/conferir/girar-2026-10-06/verificador/):

    D1 - os cartoes da aba Filtro (Preto e branco, Melhorar, Magico pro)
         mostravam a folha girada DUAS vezes (a folha crua ja vinha girada
         do GerenciadorPrevias e o preparar_metade girava de novo), e nao
         mudavam quando se girava com a aba aberta (a chave do cache dos
         cartoes nao levava o giro). Cada cartao tem de estar no mesmo giro
         da previa, nos quatro giros.

Testes de maquina, sem janela na tela (tests/conftest.py). O livro de teste
tem um bloco preto no canto de cima, a esquerda: o canto em que a tinta cai
diz o giro da imagem (0: em cima a esquerda; 90: em cima a direita; 180: em
baixo a direita; 270: em baixo a esquerda).
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from PySide6.QtWidgets import QApplication  # noqa: E402

from core import girar, pipeline  # noqa: E402
from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    app,
    janela,
    pasta,
)

# o canto em que cai o bloco preto, para cada giro da folha
CANTO_DO_GIRO = {0: "cima-esquerda", 90: "cima-direita",
                 180: "baixo-direita", 270: "baixo-esquerda"}


def _pdf_com_canto(pasta: Path, folhas: int = 3) -> Path:
    """Folhas em pe, com um bloco preto grande no canto de cima, a esquerda."""
    (pasta / "livros").mkdir(exist_ok=True)
    caminho = pasta / "livros" / "Livro do canto.pdf"
    doc = fitz.open()
    for i in range(folhas):
        pagina = doc.new_page(width=400, height=560)
        pagina.draw_rect(fitz.Rect(30, 30, 170, 150), color=(0, 0, 0), fill=(0, 0, 0))
        pagina.insert_text((60, 300), f"folha {i}", fontsize=14)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _canto(img: np.ndarray) -> str:
    """Em que canto esta o centro da tinta escura (o bloco preto)."""
    cinza = img if img.ndim == 2 else img.mean(axis=2)
    ys, xs = np.nonzero(cinza < 100)
    assert len(xs), "imagem sem tinta"
    altura, largura = cinza.shape
    vertical = "cima" if ys.mean() < altura / 2 else "baixo"
    horizontal = "esquerda" if xs.mean() < largura / 2 else "direita"
    return f"{vertical}-{horizontal}"


def _bombear_ate(app, condicao, segundos: float = 15.0) -> bool:
    """Deixa as tarefas de fundo (previas, cartoes) chegarem."""
    limite = time.monotonic() + segundos
    while time.monotonic() < limite:
        app.processEvents()
        if condicao():
            return True
        time.sleep(0.02)
    app.processEvents()
    return condicao()


def _aberta_na_aba_filtro(janela, pasta, folhas: int = 3):
    """O livro do canto aberto, sem dividir, sem cortar e sem endireitar (a
    previa e a folha inteira, so girada), na aba Filtro."""
    janela.abrir_livro(str(_pdf_com_canto(pasta, folhas)))
    projeto = janela.projeto
    projeto.dividir_folhas = False
    projeto.cortar_bordas = False
    projeto.endireitar = False
    projeto.detectar_regioes = False
    janela._analise_pronta(pipeline.analisar_projeto(projeto))
    tela = janela.tela_conferir
    janela.resize(1280, 657)
    janela.show()
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("filtro"))
    return tela


def _espiar_cartoes(tela) -> dict:
    """Anota a ultima imagem posta em cada cartao."""
    postas: dict = {}
    for chave, cartao in tela.cartoes.items():
        original = cartao.definir_amostra

        def definir(img, _c=chave, _o=original):
            postas[_c] = img
            _o(img)

        cartao.definir_amostra = definir
    return postas


@pytest.mark.parametrize("filtro_da_pagina", [ORIGINAL, MELHORAR])
def test_d1_os_cartoes_ficam_no_giro_da_previa_girando_com_a_aba_aberta(
        janela, pasta, app, filtro_da_pagina):
    """D1: gira 1/4 a direita quatro vezes com a aba Filtro aberta; depois de
    cada giro, os cartoes dos outros filtros chegam no MESMO giro da previa
    (e nao no dobro, nem no de antes)."""
    tela = _aberta_na_aba_filtro(janela, pasta)
    projeto = janela.projeto
    projeto.paginas[0].filtro = filtro_da_pagina
    tela.ir_para_pagina(0)
    postas = _espiar_cartoes(tela)
    outros = [c for c in (ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO)
              if c != filtro_da_pagina and c in tela.cartoes]
    assert len(outros) == 3

    for giro_esperado in (90, 180, 270, 0):
        tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
        assert projeto.folhas[0].rotacao == giro_esperado
        canto = CANTO_DO_GIRO[giro_esperado]

        # a previa (a imagem grande) chega no giro certo
        assert _bombear_ate(app, lambda: tela.previas.pegar(0, tela._dpi_atual) is not None)
        previa = tela.previas.pegar(0, tela._dpi_atual)
        assert _canto(previa) == canto

        def todos_no_giro():
            return all(postas.get(c) is not None and _canto(postas[c]) == canto
                       for c in outros)

        chegou = _bombear_ate(app, todos_no_giro)
        vistos = {c: (None if postas.get(c) is None else _canto(postas[c])) for c in outros}
        assert chegou, f"giro {giro_esperado}: cartoes {vistos}, previa {canto}"
        # e a mesma proporcao da previa (em pe / deitada)
        for c in outros:
            img = postas[c]
            assert (img.shape[0] > img.shape[1]) == (previa.shape[0] > previa.shape[1]), c


def test_d1_a_amostra_dos_cartoes_e_a_previa_em_cada_giro(janela, pasta, app):
    """A base dos cartoes (_imagem_sem_filtro) e a mesma imagem da previa,
    so menor, em cada giro: girada uma vez so."""
    tela = _aberta_na_aba_filtro(janela, pasta)
    projeto = janela.projeto
    for giro in (90, 180, 270):
        projeto.folhas[1].rotacao = giro
        tela.ir_para_pagina(1)
        assert _bombear_ate(app, lambda: tela._imagem_sem_filtro() is not None)
        base = tela._imagem_sem_filtro()
        assert _canto(base) == CANTO_DO_GIRO[giro], giro
        doc = fitz.open(projeto.caminho_entrada)
        try:
            previa, _ = pipeline.renderizar_pagina(doc, projeto, projeto.paginas[1], dpi=70)
        finally:
            doc.close()
        assert base.shape[:2] == previa.shape[:2]
        assert float(np.abs(base.astype(int) - previa.astype(int)).mean()) < 2.0


def test_d1_o_comparar_da_tela_ampliada_tambem_gira_uma_vez(janela, pasta, app):
    """O "comparar" da tela ampliada tinha o mesmo defeito (folha crua ja
    girada passada ao preparar_metade)."""
    tela = _aberta_na_aba_filtro(janela, pasta)
    projeto = janela.projeto
    projeto.folhas[0].rotacao = 90
    tela.ir_para_pagina(0)
    from ui.tela_ampliada import MODO_FILTRO, TelaAmpliada

    ampliada = TelaAmpliada(tela, modo=MODO_FILTRO, parent=janela)   # sem o exec (modal)
    indice = ampliada.combo_comparar.findData(PRETO_E_BRANCO)
    ampliada.combo_comparar.setCurrentIndex(indice)
    assert _bombear_ate(app, lambda: ampliada._imagem_do_outro_filtro() is not None)
    assert _canto(ampliada._imagem_do_outro_filtro()) == CANTO_DO_GIRO[90]
    ampliada.close()
