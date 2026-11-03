"""As margens iguais no "depois" do Automático (defeito de 02/11/2026).

O DEFEITO (Samuel, 02/11/2026): "coloquei margem e ela não apareceu no preview." No Automático do
Gradus Primus, etapa "Margens iguais" marcada com 10 / 5 / 10 / 5 mm: o lado "depois" de "A
página, antes e depois" não mostrava as margens. Causa: a prévia só media a folha da página da
vez, e a conta das margens precisa do tamanho de TODAS as páginas
(core/pipeline.conta_das_margens_para_a_tela devolvia None).

AS DECISÕES (Livro, docs/plano/DECISOES.md):
  D-577: o "depois" é como a página vai sair com as etapas e opções marcadas e muda a cada opção
      trocada ("o antes é sem filtro e sem cortar sem nada, o depois na tela de atualizar que
      aplica os filtros de endireitar cortar ou fazer qualquer outra coisa para ver como iria
      ficar."); vale na janela, na tela cheia e nos dois lados do "comparar".
  D-329: "Sim, a tela mostra igual ao que sai (recomendado)".
  D-311: "Todas as páginas do tamanho da maior: Sim".
  D-075: as margens do ScanTailor (10/5 mm), alteráveis.

Testes de reversão (CLAUDE.md §4.7): no código de antes (110976f) o depois sai do tamanho da
página sem margem e falham. Medida: o tamanho do depois (em pontos da prévia) contra o da página
como a tela de conferir a mostra depois do "Rodar" e contra a proporção da página do PDF.
Livro sintético das provas do Automático (tests/test_decisoes_automatico._livro: uma folha
dupla, uma torta, uma reta).
"""

from __future__ import annotations

import copy

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from tests.test_decisoes_automatico_ver_como_fica import (  # noqa: E402, F401 - fixtures
    _abrir,
    _assentar,
    _esperar,
    _imagens,
    _marcar,
    app,
    janela,
    pasta,
)

MM = 180 / 25.4                       # pontos por milímetro na resolução da prévia (DPI_DA_PREVIA)


def _como_a_tela_mostra(projeto, indice: int):
    """A página `indice` como a tela de conferir a mostra (e o PDF a grava) depois do "Rodar":
    medida para as margens (a primeira passada do PDF), desenhada na resolução da prévia e
    composta com as margens (core/automatico.como_sai_na_tela, a conta de _com_as_margens)."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import medir_o_livro_para_as_margens, renderizar_pagina
    from ui.automatico import DPI_DA_PREVIA

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        copia = A.copia_para_a_previa(projeto)
        medir_o_livro_para_as_margens(copia, doc, copia.paginas_ativas)
        img, _ = renderizar_pagina(doc, copia, copia.paginas[indice], dpi=DPI_DA_PREVIA)
        return A.como_sai_na_tela(img, copia, copia.paginas[indice], DPI_DA_PREVIA)
    finally:
        doc.close()


def _tamanhos_do_pdf(projeto, tmp_path) -> list[tuple[float, float]]:
    """(largura, altura) em pontos de cada página do PDF gravado pelo processar."""
    from core.pipeline import processar

    gravar = copy.copy(projeto)
    gravar.caminho_saida = str(tmp_path / "saida.pdf")
    with fitz.open(processar(gravar)) as doc:
        return [(p.rect.width, p.rect.height) for p in doc]


def test_margens_iguais_marcadas_aparecem_no_depois_como_no_pdf(janela, app, tmp_path):
    """Defeito de 02/11/2026 ("coloquei margem e ela não apareceu no preview."). Na página reta,
    com "Cortar" e "Margens iguais" marcadas (10/5/10/5 mm de fábrica): o depois fica maior que
    sem as margens, é ponto por ponto a página que a tela mostra depois do "Rodar" (D-329: a tela
    mostra igual ao que sai) e tem a proporção da página do PDF, em que todas as páginas saem do
    tamanho da maior (D-311). Teste de reversão: no código de antes o depois sai sem margem."""
    grande = _abrir(janela, app, tmp_path, pagina=2)
    painel = grande.antes_e_depois
    _marcar(grande, {A.CORTAR})
    _esperar(app, painel)
    sem_margens = _imagens(painel)[1]
    _marcar(grande, {A.CORTAR, A.MARGENS})
    _esperar(app, painel)
    com_margens = _imagens(painel)[1]
    assert com_margens is not None
    assert com_margens.shape[1] > sem_margens.shape[1] + 15 * MM \
        and com_margens.shape[0] > sem_margens.shape[0] + 7 * MM, \
        f"o depois não mostra as margens: {sem_margens.shape} sem, {com_margens.shape} com"
    janela._fechar_a_janela_do_automatico()
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    assert janela.projeto.margens_iguais is True
    na_tela = _como_a_tela_mostra(janela.projeto, 2)
    assert com_margens.shape == na_tela.shape, (com_margens.shape, na_tela.shape)
    assert np.array_equal(com_margens, na_tela), "o depois não é a página como a tela mostra"
    tamanhos = _tamanhos_do_pdf(janela.projeto, tmp_path)
    # D-311: a torta e a reta saem do mesmo tamanho (a folha dupla, sem dividir, é muito maior:
    # fica fora da conta e ganha o aviso, g9-pagina-muito-maior, Samuel 14/10/2026)
    assert [round(v) for v in tamanhos[1]] == [round(v) for v in tamanhos[2]], tamanhos
    largura, altura = tamanhos[-1]
    proporcao = com_margens.shape[1] / com_margens.shape[0]
    assert abs(proporcao - largura / altura) < 0.01 * (largura / altura), \
        f"o depois ({proporcao:.4f}) não tem a proporção da página do PDF ({largura / altura:.4f})"


def test_mudar_um_numero_da_margem_muda_o_depois(janela, app, tmp_path):
    """D-577: o depois "muda a cada opção trocada"; D-075: as margens são alteráveis. A margem
    da esquerda de 10 para 30 mm alarga o depois em 20 mm (a 180 DPI, 142 pontos), e a de baixo
    de 5 para 15 mm o alonga em 10 mm. Teste de reversão: no código de antes nada muda."""
    grande = _abrir(janela, app, tmp_path, pagina=2)
    painel = grande.antes_e_depois
    _marcar(grande, {A.MARGENS})
    _esperar(app, painel)
    antes = _imagens(painel)[1].shape
    grande.margens_mm["esquerda"].setValue(30.0)
    _esperar(app, painel)
    largo = _imagens(painel)[1].shape
    assert abs((largo[1] - antes[1]) - 20 * MM) <= 3, (antes, largo)
    assert largo[0] == antes[0]
    grande.margens_mm["baixo"].setValue(15.0)
    _esperar(app, painel)
    alto = _imagens(painel)[1].shape
    assert abs((alto[0] - largo[0]) - 10 * MM) <= 3, (largo, alto)


def test_margens_na_tela_cheia_e_nos_dois_lados_do_comparar(janela, app, tmp_path):
    """D-577: a tela cheia mostra o MESMO depois (com as margens); no "comparar", o lado direito
    que acompanha a janela também; cada lado mexido calcula o dele com as margens do lado (a
    esquerda marca "Margens iguais"; a direita põe 30 mm à esquerda). Teste de reversão: no
    código de antes os lados mexidos saem sem margem."""
    from PySide6.QtCore import Qt

    grande = _abrir(janela, app, tmp_path, pagina=2)
    painel = grande.antes_e_depois
    sem_margens = _imagens(painel)[1].shape
    _marcar(grande, {A.MARGENS})
    _esperar(app, painel)
    depois = _imagens(painel)[1]
    assert depois.shape[1] > sem_margens[1] + 15 * MM
    painel.botao_tela_cheia.click()
    _assentar(app)
    tela = painel.tela_cheia
    assert tela.visor._crus[1] is depois, "a tela cheia não mostra o depois da janela"
    tela.botao_comparar.click()
    _esperar(app, painel)
    _assentar(app)
    assert tela.vista_b._pixmap is not None
    assert (tela.vista_b._pixmap.height(), tela.vista_b._pixmap.width()) == depois.shape[:2]
    # a esquerda (o livro como está, sem margens) passa a ter "Margens iguais" marcada
    tela.lado_a.painel.lista.item_da_etapa(A.MARGENS).setCheckState(Qt.Checked)
    _assentar(app)
    _esperar(app, tela.lado_a.motor)
    img_a = tela.lado_a.imagem_e_rotulo()[0]
    assert img_a is not None and img_a.shape == depois.shape, (img_a is None or img_a.shape, depois.shape)
    # a direita: 30 mm à esquerda, só neste lado
    tela.lado_b.painel.margens_mm["esquerda"].setValue(30.0)
    _assentar(app)
    _esperar(app, tela.lado_b.motor)
    img_b = tela.lado_b.imagem_e_rotulo()[0]
    assert img_b is not None and abs((img_b.shape[1] - depois.shape[1]) - 20 * MM) <= 3
    _assentar(app)
    assert (tela.vista_b._pixmap.height(), tela.vista_b._pixmap.width()) == img_b.shape[:2]
    assert _imagens(painel)[1].shape == depois.shape, "o lado do comparar mudou a janela"
    tela.accept()
    _assentar(app)


def test_como_esta_no_livro_com_as_margens_ligadas_sai_com_elas(janela, app, tmp_path):
    """O lado esquerdo do "comparar" mostra a página como está no livro
    (core/automatico.pagina_como_esta). Com as margens iguais já ligadas no livro, ela sai com
    elas, como a tela e o PDF (D-329), mesmo sem ninguém ter medido o livro antes. Teste de
    reversão: no código de antes ela sai sem margem."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import _TAMANHOS_PRONTOS
    from ui.automatico import DPI_DA_PREVIA

    janela.abrir_livro(__import__("tests.test_decisoes_automatico", fromlist=["_livro"])._livro(tmp_path))
    _assentar(app)
    projeto = janela.projeto
    projeto.margens_iguais = True
    _TAMANHOS_PRONTOS.clear()                 # ninguém mediu: como ao abrir o programa
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img = A.pagina_como_esta(doc, A.copia_para_a_previa(projeto), 2, DPI_DA_PREVIA)
    finally:
        doc.close()
    na_tela = _como_a_tela_mostra(projeto, 2)
    assert img.shape == na_tela.shape and np.array_equal(img, na_tela), (img.shape, na_tela.shape)
