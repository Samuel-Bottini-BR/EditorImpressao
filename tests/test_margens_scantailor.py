"""Item 2.4: margens iguais em todas as páginas, igual ao ScanTailor.

Duas partes:
- as contas de core/margens_scantailor.py contra a conta do ScanTailor
  (page_layout/Utils.cpp calcSoftMarginsMM e Settings.cpp, casos feitos à mão
  com os números do próprio código C++);
- o processar de verdade (PDF sintético de páginas de tamanhos diferentes):
  desligado sai igual ao de sempre; ligado, todas as páginas saem do mesmo
  tamanho, com o conteúdo no lugar do alinhamento, e a página muito maior fica
  fora da conta com o aviso (g9-pagina-muito-maior).
"""

from __future__ import annotations

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import analise
from core import margens_scantailor as ms
from core.filtros import ORIGINAL
from core.pipeline import processar
from modelos import ConfigFolha, ConfigPagina, Projeto


# --------------------------------------------------------------- as contas

def test_margens_de_fabrica_sao_as_do_scantailor():
    """DefaultParams::PageLayoutParams(): m_hardMargins(10, 5, 10, 5);
    Alignment(): VCENTER, HCENTER."""
    assert ms.MARGENS_DE_FABRICA == ms.Margens(10, 5, 10, 5)
    assert ms.ALINHAMENTO_DE_FABRICA == (ms.MEIO, ms.MEIO)
    assert Projeto(caminho_entrada="x").margens_iguais is False
    assert Projeto(caminho_entrada="x").margens_mm == [10.0, 5.0, 10.0, 5.0]


def test_tamanho_duro_e_conteudo_mais_margens():
    assert ms.tamanho_duro_mm((100, 150), ms.Margens(10, 5, 10, 5)) == (120, 160)


def test_tamanho_do_livro_e_o_maior_e_ignora_quem_nao_acompanha():
    assert ms.tamanho_do_livro_mm([(120, 160), (130, 150), None, (110, 170)]) == (130, 170)
    assert ms.tamanho_do_livro_mm([]) == (0.0, 0.0)


@pytest.mark.parametrize("horizontal,esperado", [
    (ms.ESQUERDA, (0.0, 20.0)),     # LEFT: right = deltaWidth
    (ms.MEIO, (10.0, 10.0)),        # HCENTER: metade e metade
    (ms.DIREITA, (20.0, 0.0)),      # RIGHT: left = deltaWidth
])
def test_alinhamento_horizontal(horizontal, esperado):
    suaves = ms.margens_suaves_mm((100, 200), (120, 200), (ms.MEIO, horizontal))
    assert (suaves.esquerda, suaves.direita) == esperado
    assert (suaves.cima, suaves.baixo) == (0.0, 0.0)


@pytest.mark.parametrize("vertical,esperado", [
    (ms.CIMA, (0.0, 30.0)), (ms.MEIO, (15.0, 15.0)), (ms.BAIXO, (30.0, 0.0)),
])
def test_alinhamento_vertical(vertical, esperado):
    suaves = ms.margens_suaves_mm((100, 170), (100, 200), (vertical, ms.MEIO))
    assert (suaves.cima, suaves.baixo) == esperado


def test_pagina_que_nao_acompanha_nao_ganha_margem_suave():
    assert ms.margens_suaves_mm((100, 100), (200, 200), None) == ms.Margens()


def test_original_segue_onde_o_conteudo_estava():
    """HORIGINAL: aggLeftBorder = cx * agg_w - hard_w / 2, limitado a [0, delta].
    Conteúdo com centro a 30% da largura: 0,3 * 200 - 100/2 = 10."""
    suaves = ms.margens_suaves_mm((100, 100), (200, 100), (ms.MEIO, ms.ORIGINAL), (0.3, 0.5))
    assert suaves.esquerda == pytest.approx(10.0)
    assert suaves.direita == pytest.approx(90.0)
    # encostado à esquerda demais: o qBound segura em zero
    suaves = ms.margens_suaves_mm((100, 100), (200, 100), (ms.MEIO, ms.ORIGINAL), (0.1, 0.5))
    assert suaves.esquerda == 0.0 and suaves.direita == pytest.approx(100.0)


def test_automatico_escolhe_como_o_scantailor():
    """HAUTO: 3*esq < dir -> LEFT; 3*dir < esq -> RIGHT; senão HCENTER."""
    # esquerda 10, direita 90: 30 < 90 -> LEFT (right = delta)
    s = ms.margens_suaves_mm((100, 100), (200, 100), (ms.MEIO, ms.AUTOMATICO), (0.3, 0.5))
    assert (s.esquerda, s.direita) == (0.0, 100.0)
    # centro no meio: agg 50/50 -> HCENTER
    s = ms.margens_suaves_mm((100, 100), (200, 100), (ms.MEIO, ms.AUTOMATICO), (0.5, 0.5))
    assert (s.esquerda, s.direita) == (50.0, 50.0)
    # sem saber onde estava: agg = (0, delta) -> 0 < delta -> LEFT
    s = ms.margens_suaves_mm((100, 100), (200, 100), (ms.MEIO, ms.AUTOMATICO), None)
    assert (s.esquerda, s.direita) == (0.0, 100.0)


def test_pagina_muito_maior_fica_fora_da_conta():
    duros = [(146, 235)] * 6 + [(208, 176)]       # a tabela do Opus Majus
    assert ms.paginas_muito_maiores(duros) == {6}
    assert ms.paginas_muito_maiores([(146, 235), (150, 240), (148, 236)]) == set()
    assert ms.paginas_muito_maiores([(146, 235), (300, 400)]) == set()   # poucas


def test_compor_poe_o_conteudo_no_lugar_e_o_resto_branco():
    img = np.zeros((100, 50, 3), np.uint8)
    dpi = 25.4                                    # 1 ponto = 1 mm
    folha = ms.compor_com_margens(img, dpi, ms.Margens(10, 5, 10, 5),
                                  ms.Margens(4, 3, 6, 7), (80, 120))
    assert folha.shape == (120, 80, 3)
    assert (folha[8:108, 14:64] == 0).all()
    assert folha[:8].min() == 255 and folha[108:].min() == 255
    assert folha[:, :14].min() == 255 and folha[:, 64:].min() == 255


def test_margens_vindas_do_arquivo_estranho_voltam_as_de_fabrica():
    assert ms.Margens.de(None) == ms.MARGENS_DE_FABRICA
    assert ms.Margens.de([1, 2, 3, 4]) == ms.Margens(1, 2, 3, 4)
    assert ms.alinhamento_valido(["qualquer", "coisa"]) == ms.ALINHAMENTO_DE_FABRICA


# --------------------------------------------------------------- o processar

DPI = 100


def _pdf(caminho, tamanhos_cm):
    """Um PDF com uma página por tamanho, cada uma com um retângulo preto no
    meio (o "conteúdo") e papel branco em volta."""
    import cv2

    doc = fitz.open()
    for largura_cm, altura_cm in tamanhos_cm:
        l_px, a_px = round(largura_cm / 2.54 * DPI), round(altura_cm / 2.54 * DPI)
        arte = np.full((a_px, l_px, 3), 255, np.uint8)
        arte[a_px // 4: 3 * a_px // 4, l_px // 4: 3 * l_px // 4] = 0
        ok, buf = cv2.imencode(".png", arte)
        assert ok
        pagina = doc.new_page(width=largura_cm / 2.54 * 72, height=altura_cm / 2.54 * 72)
        pagina.insert_image(pagina.rect, stream=buf.tobytes())
    doc.save(str(caminho))
    doc.close()


def _projeto(entrada, saida, n):
    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(saida), nome="x")
    projeto.dividir_folhas = False
    projeto.endireitar = False
    projeto.cortar_bordas = False
    projeto.limpar = False
    projeto.detectar_regioes = False
    projeto.qualidade_dpi = DPI
    projeto.filtro_padrao = ORIGINAL
    projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(n)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i, filtro=ORIGINAL) for i in range(n)]
    return projeto


def _tamanhos_pt(caminho):
    doc = fitz.open(str(caminho))
    try:
        return [(round(p.rect.width, 1), round(p.rect.height, 1)) for p in doc]
    finally:
        doc.close()


TAMANHOS = [(10, 15), (12, 14), (11, 16)]


def test_desligado_sai_cada_pagina_do_tamanho_dela(tmp_path):
    _pdf(tmp_path / "e.pdf", TAMANHOS)
    projeto = _projeto(tmp_path / "e.pdf", tmp_path / "s.pdf", 3)
    processar(projeto)
    tamanhos = _tamanhos_pt(tmp_path / "s.pdf")
    assert len(set(tamanhos)) == 3


def test_ligado_todas_saem_do_tamanho_da_maior_mais_margens(tmp_path):
    _pdf(tmp_path / "e.pdf", TAMANHOS)
    projeto = _projeto(tmp_path / "e.pdf", tmp_path / "s.pdf", 3)
    projeto.margens_iguais = True
    processar(projeto)
    tamanhos = _tamanhos_pt(tmp_path / "s.pdf")
    assert len(set(tamanhos)) == 1
    largura_pt, altura_pt = tamanhos[0]
    # a maior largura (12 cm) + 2 x 10 mm; a maior altura (16 cm) + 2 x 5 mm
    assert largura_pt == pytest.approx((120 + 20) / 25.4 * 72, abs=1.0)
    assert altura_pt == pytest.approx((160 + 10) / 25.4 * 72, abs=1.0)


def test_ligado_no_meio_o_conteudo_fica_centralizado(tmp_path):
    _pdf(tmp_path / "e.pdf", [(10, 10), (14, 14), (12, 12)])
    projeto = _projeto(tmp_path / "e.pdf", tmp_path / "s.pdf", 3)
    projeto.margens_iguais = True
    processar(projeto)
    doc = fitz.open(str(tmp_path / "s.pdf"))
    try:
        pix = doc[0].get_pixmap(dpi=DPI)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
    finally:
        doc.close()
    preto = np.argwhere(img[..., 0] < 128)
    (y0, x0), (y1, x1) = preto.min(0), preto.max(0)
    assert abs((x0 + x1) / 2 - img.shape[1] / 2) <= 3
    assert abs((y0 + y1) / 2 - img.shape[0] / 2) <= 3


def test_pagina_muito_maior_sai_do_tamanho_dela_e_ganha_o_aviso(tmp_path):
    _pdf(tmp_path / "e.pdf", [(10, 15), (10, 15), (10, 15), (20, 15)])
    projeto = _projeto(tmp_path / "e.pdf", tmp_path / "s.pdf", 4)
    projeto.margens_iguais = True
    processar(projeto)
    tamanhos = _tamanhos_pt(tmp_path / "s.pdf")
    assert tamanhos[0] == tamanhos[1] == tamanhos[2] != tamanhos[3]
    assert analise.FOLHA_MAIOR_FORA_DAS_MARGENS in projeto.paginas[3].alertas
    assert analise.FOLHA_MAIOR_FORA_DAS_MARGENS not in projeto.paginas[0].alertas
    assert analise.FOLHA_MAIOR_FORA_DAS_MARGENS in analise.ALERTAS


def test_ligado_nao_usa_o_caminho_rapido_dos_cadernos():
    projeto = Projeto(caminho_entrada="x", dividir_folhas=False, limpar=False, endireitar=False,
                      cortar_bordas=False, montar_cadernos=True)
    assert projeto.so_cadernos
    projeto.margens_iguais = True
    assert not projeto.so_cadernos


def test_projeto_antigo_sem_os_campos_abre_desligado():
    dados = Projeto(caminho_entrada="x").para_dicionario()
    for campo in ("margens_iguais", "margens_mm", "margens_alinhamento"):
        dados.pop(campo)
    projeto = Projeto.de_dicionario(dados)
    assert projeto.margens_iguais is False
    assert projeto.margens_mm == [10.0, 5.0, 10.0, 5.0]


def test_a_tela_mostra_as_margens_como_no_pdf(tmp_path):
    """Decisão do Samuel (22/10/2026): "Sim, a tela mostra igual ao que sai".
    Medidas as páginas, a página da tela (em outra resolução) ganha as mesmas
    margens: a proporção dela é a da página do PDF."""
    from core import pipeline
    from core.pdf_io import abrir_pdf, pagina_para_array

    _pdf(tmp_path / "e.pdf", TAMANHOS)
    projeto = _projeto(tmp_path / "e.pdf", tmp_path / "s.pdf", 3)
    projeto.margens_iguais = True
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        pipeline.medir_o_livro_para_as_margens(projeto, doc, projeto.paginas_ativas)
        conta = pipeline.conta_das_margens_para_a_tela(projeto)
        assert conta is not None
        pagina = projeto.paginas[0]
        tela = pagina_para_array(doc, 0, dpi=50)               # a "prévia", em 50 DPI
    finally:
        doc.close()
    com = pipeline.margens_na_tela(tela, projeto, pagina, conta)
    processar(projeto)
    largura_pt, altura_pt = _tamanhos_pt(tmp_path / "s.pdf")[0]
    assert com.shape[1] / com.shape[0] == pytest.approx(largura_pt / altura_pt, rel=0.02)
    projeto.margens_iguais = False
    assert pipeline.conta_das_margens_para_a_tela(projeto) is None
