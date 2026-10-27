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
