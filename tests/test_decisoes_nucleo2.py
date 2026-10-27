"""Obra de 26/10/2026, etapa 9d: consertos de núcleo que sobraram (provas das
decisões e testes de reversão; CLAUDE.md §4.7 e §11).

Cada teste diz a decisão ou o defeito (com a fonte) e uma MEDIDA que o pega.
Os de reversão falham no código de antes (`ad8df2b`, worktree
`obra-etapa9d-antes`) e passam no novo; a conta de cada um está no
`relatorios/obra-etapa9d/ONDE-PAREI.md`.

Dois tipos, como na etapa 10b:
  - páginas de verdade do acervo, pelo caminho inteiro do programa (livro NOVO
    de fábrica: core.pipeline.analisar_projeto e o mesmo corpo do processar,
    core.pipeline._pagina_pronta; regra de 21/10): só no PC do Samuel (o acervo
    fica fora do git; sem ele, pulam);
  - páginas e livros sintéticos, que rodam em qualquer lugar (GitHub).
Regra de 21/10: nenhuma página é lombada nem capa de couro.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
LIVROS = {
    "antiphon": "Antiphon_25.pdf",
    "horas": "Livro de Horas - Luís XIV.pdf",
    "ljs47": "ljs47.pdf",
    "palatino": "Giovambattista Palatino cittadino romano.pdf",
    "righetti": "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf",
    "escola": "Na escola de Jesus - Catecismo explicado com imagens..pdf",
    "boecio": "Sobre a Consolação da Filosofia - Severino Boécio.pdf",
}


# --- ajudantes ----------------------------------------------------------------

def _precisa(caminho: Path) -> None:
    if not caminho.exists():
        pytest.skip(f"sem {caminho} (só no PC do Samuel)")


def _pdf_sintetico(caminho: Path, paginas: list[np.ndarray], dpi: float = 150.0) -> Path:
    """Um PDF com uma imagem por página (cinza ou BGR), como um livro escaneado."""
    doc = fitz.open()
    for img in paginas:
        altura, largura = img.shape[:2]
        pagina = doc.new_page(width=largura / dpi * 72.0, height=altura / dpi * 72.0)
        ok, png = cv2.imencode(".png", img)
        assert ok
        pagina.insert_image(pagina.rect, stream=png.tobytes())
    doc.save(str(caminho))
    doc.close()
    return caminho


# =============================================================================
# Item 5 - o aviso de margem da impressão com número negativo
# =============================================================================

def test_reversao_aviso_de_margem_nunca_diz_numero_negativo(tmp_path):
    """Ressalva da etapa 10a (27/10/2026, "Bugs para a Lista de bugs"): "aviso
    de margem da impressão com número negativo ('em cima -2,2 cm (precisa de
    1,3 cm)') quando a página passa da folha: confuso" (core/impressao.py,
    _avisos_de_margem). Decisão do aviso (g11, 14/10): "o programa precisa
    avisar quando o corte deixar qualquer margem abaixo de 1 cm".

    Livreto em A4 com as duas páginas a 140% (o mesmo caso da 10a, numa página
    sintética com tinta até perto da beirada): o aviso de margem continua, sem
    nenhum número negativo, e diz que o impresso passa da beirada; o aviso
    "CORTADO" (D-017) continua dizendo quanto."""
    from core import impressao

    pagina = np.full((1500, 1000), 255, np.uint8)
    pagina[60:1440, 50:950] = 30                       # tinta quase até a beirada
    livro = _pdf_sintetico(tmp_path / "livro.pdf", [pagina] * 4)
    opcoes = impressao.OpcoesDeImpressao()
    opcoes.escala_esquerda = opcoes.escala_direita = 140.0
    r = impressao.montar_para_impressao(livro, tmp_path / "imprimir.pdf", opcoes)
    margem = [a.texto for a in r.avisos if "margem ficou abaixo" in a.texto]
    assert margem, [a.texto for a in r.avisos]
    textos = " ".join(margem)
    assert not re.search(r"-\s?\d", textos.replace(" - ", " ")), textos
    assert "nenhuma (o impresso passa da beirada do papel)" in textos, textos
    assert any("CORTADO" in a.texto for a in r.avisos)


def test_aviso_de_margem_pequena_continua_com_o_numero(tmp_path):
    """Guarda: a margem pequena mas positiva continua dita em cm (a 115%, o
    impresso não passa do papel, mas fica a menos de 1,3 cm da beirada)."""
    from core import impressao

    pagina = np.full((1500, 1000), 255, np.uint8)
    pagina[60:1440, 50:950] = 30
    livro = _pdf_sintetico(tmp_path / "livro.pdf", [pagina] * 4)
    opcoes = impressao.OpcoesDeImpressao()
    opcoes.escala_esquerda = opcoes.escala_direita = 115.0
    r = impressao.montar_para_impressao(livro, tmp_path / "imprimir.pdf", opcoes)
    textos = " ".join(a.texto for a in r.avisos if "margem ficou abaixo" in a.texto)
    assert re.search(r"\d,\d cm \(precisa de", textos), textos
    assert "nenhuma" not in textos, textos


# =============================================================================
# Item 4 - "Deixar a folha em branco" na página "Tirar o fundo" sem o fundo
# =============================================================================

@pytest.fixture
def _sem_figuras(monkeypatch):
    """O detector de figuras do core/camadas.py não acha nada (rápido, sem o
    modelo), como em tests/test_tirar_fundo_no_programa.py."""
    from core import camadas
    from tests.test_camadas import sem_figuras

    monkeypatch.setattr(camadas, "DETECTOR_DE_FIGURAS", sem_figuras)


def _livro_sem_o_fundo(tmp_path, detectar: bool):
    """Livro de uma página com camadas (como os do Internet Archive), no
    filtro "Tirar o fundo", e a página de verdade sem o fundo (core/camadas)."""
    from core import pipeline
    from core.filtros import TIRAR_FUNDO
    from modelos import Projeto
    from tests.test_camadas import pdf_com_camadas

    doc = pdf_com_camadas()
    caminho = tmp_path / "camadas.pdf"
    doc.save(str(caminho))
    doc.close()
    projeto = Projeto(caminho_entrada=str(caminho), nome="teste",
                      caminho_saida=str(tmp_path / "saida.pdf"))
    projeto.filtro_padrao = TIRAR_FUNDO
    projeto.detectar_regioes = detectar
    projeto.cortar_bordas = False
    projeto.endireitar = False
    projeto.montar_cadernos = False
    projeto.qualidade_dpi = 100
    projeto = pipeline.analisar_projeto(projeto)
    assert projeto.paginas[0].filtro == TIRAR_FUNDO
    return projeto


def _marcar_papel(pagina, x0, y0, x1, y1, origem=None):
    from core.selecao import MAO, PAPEL, RETANGULO, Regiao, Selecao

    selecao = Selecao()
    selecao.acrescentar(Regiao(tipo=PAPEL, forma=RETANGULO, pontos=[(x0, y0), (x1, y1)],
                               origem=origem or MAO))
    pagina.guardar_selecao(selecao)


def _pagina_do_pdf(caminho) -> np.ndarray:
    with fitz.open(str(caminho)) as doc:
        assert len(doc) == 1, "a página tem de continuar no livro (mesmo lugar)"
        pix = doc[0].get_pixmap(dpi=100, colorspace=fitz.csGRAY)
        return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width].copy()


@pytest.mark.parametrize("detectar", [True, False], ids=["procurar_gravura", "sem_procurar"])
def test_reversao_folha_em_branco_no_tirar_o_fundo_sem_o_fundo_sai_branca(tmp_path, _sem_figuras,
                                                                          detectar):
    """Bug achado na etapa 9c (27/10/2026, "Bugs para a Lista de bugs"):
    "'Deixar a folha em branco' numa página 'Tirar o fundo' de que o fundo FOI
    tirado: essa página vai por pipeline._pedacos_na_pagina_sem_fundo, que não
    passa pelo conserto do item 1; a tinta continua." Decisão D-027 (30/09):
    "essa é uma página que eu poderia simplesmente escolher a opção para virar
    uma folha branca". Medida: no PDF, a página inteira sai branca (antes, as
    letras pretas da camada de cima continuavam) - e a prévia igual."""
    from core import pipeline

    projeto = _livro_sem_o_fundo(tmp_path, detectar)
    pipeline.processar(projeto)
    antes = _pagina_do_pdf(projeto.caminho_saida)
    assert antes.min() < 80, "o livro de teste devia ter letra preta sem o fundo"
    _marcar_papel(projeto.paginas[0], 0.0, 0.0, 1.0, 1.0)      # "Deixar a folha em branco"
    pipeline.processar(projeto)
    img = _pagina_do_pdf(projeto.caminho_saida)
    assert img.min() >= 250, f"a folha devia sair toda branca no PDF (mínimo {img.min()})"
    doc = fitz.open(projeto.caminho_entrada)
    try:
        previa, _ = pipeline.renderizar_pagina(doc, projeto, projeto.paginas[0], dpi=100)
    finally:
        doc.close()
    assert previa.min() >= 250, "a prévia também (tela = PDF, D-473)"


def test_pintar_de_branco_no_tirar_o_fundo_so_na_area(tmp_path, _sem_figuras):
    """D-227 ("pintar de branco" → no PDF sai branca) na página sem o fundo:
    só a área marcada vai a branco; a letra de fora continua."""
    from core import pipeline

    projeto = _livro_sem_o_fundo(tmp_path, True)
    pipeline.processar(projeto)
    antes = _pagina_do_pdf(projeto.caminho_saida)
    altura, largura = antes.shape
    tinta = np.argwhere(antes < 80)
    meio = float(np.median(tinta[:, 0])) / altura          # onde está a letra (altura)
    _marcar_papel(projeto.paginas[0], 0.0, 0.0, 1.0, meio)  # a metade de cima da tinta
    pipeline.processar(projeto)
    img = _pagina_do_pdf(projeto.caminho_saida)
    corte = int(meio * altura)
    assert img[:max(1, corte - 2)].min() >= 250, "a área pintada não saiu branca"
    assert (img[corte + 2:] < 80).sum() > 0.3 * (antes[corte + 2:] < 80).sum(), \
        "a letra fora da área sumiu"


def test_papel_da_maquina_nao_branqueia_a_pagina_sem_o_fundo(tmp_path, _sem_figuras):
    """Guarda (D-134): o papel que a MÁQUINA marcou não muda a página sem o
    fundo; só o marcado à mão."""
    from core import pipeline
    from core.selecao import AUTOMATICO

    projeto = _livro_sem_o_fundo(tmp_path, True)
    _marcar_papel(projeto.paginas[0], 0.0, 0.0, 1.0, 1.0, origem=AUTOMATICO)
    pipeline.processar(projeto)
    assert _pagina_do_pdf(projeto.caminho_saida).min() < 80
