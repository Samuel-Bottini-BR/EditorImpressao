"""Item 2.6: o arquivo para impressão (core/impressao.py) e a impressora (core/impressora.py).

Testes de máquina sobre um livro sintético: cada página do livro é pintada
INTEIRA de uma cor só, diferente em cada página (página n = cinza 8*n), para
dar para saber, olhando a folha montada, qual página caiu em cada metade e
onde ela começa e termina. As decisões testadas estão no cabeçalho de
core/impressao.py (g11, g12, imp-1 a imp-6, g9-folha-maior-impressao).
"""

from __future__ import annotations

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import impressao as imp
from tests.test_mesmo_livro_outro_caminho import app  # noqa: F401, E402 - fixture

MM = 72 / 25.4


def _livro(caminho, n, largura_mm=146.0, altura_mm=235.0, deitadas=()):
    doc = fitz.open()
    for i in range(1, n + 1):
        l, a = (altura_mm, largura_mm) if i in deitadas else (largura_mm, altura_mm)
        pagina = doc.new_page(width=l * MM, height=a * MM)
        cor = (8 * i) / 255
        pagina.draw_rect(pagina.rect, color=(cor, cor, cor), fill=(cor, cor, cor))
    doc.save(str(caminho))
    doc.close()
    return caminho


def _imagem(doc, i, dpi=36):
    pix = doc[i].get_pixmap(dpi=dpi, colorspace=fitz.csGRAY, alpha=False)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width].copy()


def _pagina_na_metade(img, esquerda: bool):
    """(número da página, caixa em mm) do que está pintado numa metade."""
    meio = img.shape[1] // 2
    metade = img[:, :meio] if esquerda else img[:, meio:]
    pintado = metade < 250
    if not pintado.any():
        return None, None
    ys, xs = np.nonzero(pintado)
    valor = int(np.median(metade[pintado]))
    numero = round(valor / 8)
    deslocamento = 0 if esquerda else meio
    passo = 25.4 / 36
    return numero, ((xs.min() + deslocamento) * passo, ys.min() * passo,
                    (xs.max() + 1 + deslocamento) * passo, (ys.max() + 1) * passo)


def _opcoes(**campos):
    opcoes = imp.OpcoesDeImpressao(como_imagem=False)
    for k, v in campos.items():
        setattr(opcoes, k, v)
    return opcoes


# --------------------------------------------------------------- livreto

def test_livreto_a4_deitada_na_ordem_da_dobra(tmp_path):
    entrada = _livro(tmp_path / "l.pdf", 8)
    resultado = imp.montar_para_impressao(entrada, tmp_path / "s.pdf",
                                          _opcoes(paginas_por_caderno=8))
    with fitz.open(str(tmp_path / "s.pdf")) as doc:
        assert doc.page_count == 4
        assert doc[0].rect.width == pytest.approx(297 * MM, abs=0.5)
        assert doc[0].rect.height == pytest.approx(210 * MM, abs=0.5)
        ordem = [(_pagina_na_metade(_imagem(doc, i), True)[0],
                  _pagina_na_metade(_imagem(doc, i), False)[0]) for i in range(4)]
    assert ordem == [(8, 1), (2, 7), (6, 3), (4, 5)]
    assert resultado.folhas_de_papel == 2
    assert resultado.conferencia[0] is True
    assert resultado.avisos == []


def test_ajustar_ja_entra_dentro_das_margens(tmp_path):
    """imp-2 "Já entra dentro das margens" e g11: 1,3 cm da beirada do papel
    (em cima, embaixo, fora) e 1 cm da dobra."""
    entrada = _livro(tmp_path / "l.pdf", 4)
    imp.montar_para_impressao(entrada, tmp_path / "s.pdf", _opcoes(paginas_por_caderno=4))
    with fitz.open(str(tmp_path / "s.pdf")) as doc:
        img = _imagem(doc, 0)
    for esquerda in (True, False):
        _n, (x0, y0, x1, y1) = _pagina_na_metade(img, esquerda)
        assert y0 >= 13 - 1.0 and 210 - y1 >= 13 - 1.0
        if esquerda:
            assert x0 >= 13 - 1.0 and 148.5 - x1 >= 10 - 1.0
        else:
            assert 297 - x1 >= 13 - 1.0 and x0 - 148.5 >= 10 - 1.0
        # e encosta em cima e embaixo (a página comum é mais alta que larga)
        assert y0 == pytest.approx(13, abs=1.5) and 210 - y1 == pytest.approx(13, abs=1.5)


def test_pagina_diminuida_fica_no_meio_da_sua_metade(tmp_path):
    """imp-3 "No meio da sua metade" e g12 (só o lado esquerdo)."""
    entrada = _livro(tmp_path / "l.pdf", 4)
    imp.montar_para_impressao(entrada, tmp_path / "s.pdf",
                              _opcoes(paginas_por_caderno=4, escala_esquerda=70.0))
    with fitz.open(str(tmp_path / "s.pdf")) as doc:
        img = _imagem(doc, 0)
    _n, (x0, y0, x1, y1) = _pagina_na_metade(img, True)
    assert (x0 + x1) / 2 == pytest.approx(148.5 / 2, abs=1.5)
    assert (y0 + y1) / 2 == pytest.approx(105, abs=1.5)
    _n, (dx0, dy0, dx1, dy1) = _pagina_na_metade(img, False)
    assert (dy1 - dy0) > (y1 - y0) * 1.3          # a da direita não diminuiu


def test_excecao_de_uma_pagina_so(tmp_path):
    """imp-1 "Uma página só": a exceção diminui só a página escolhida, não a
    folha A4 inteira."""
    entrada = _livro(tmp_path / "l.pdf", 4)
    imp.montar_para_impressao(entrada, tmp_path / "s.pdf",
                              _opcoes(paginas_por_caderno=4, excecoes={1: 60.0}))
    with fitz.open(str(tmp_path / "s.pdf")) as doc:
        img = _imagem(doc, 0)                         # frente: 4 | 1
    n_esq, caixa_esq = _pagina_na_metade(img, True)
    n_dir, caixa_dir = _pagina_na_metade(img, False)
    assert (n_esq, n_dir) == (4, 1)
    assert (caixa_dir[3] - caixa_dir[1]) == pytest.approx(0.6 * (caixa_esq[3] - caixa_esq[1]), rel=0.06)


def test_aumentar_avisa_a_margem_e_nao_cobre_a_vizinha(tmp_path):
    """"Mas eu ainda vou poder aumentar né?": sim; passou da margem, avisa. A
    página aumentada não pode cobrir a metade da outra."""
    entrada = _livro(tmp_path / "l.pdf", 4)
    resultado = imp.montar_para_impressao(entrada, tmp_path / "s.pdf",
                                          _opcoes(paginas_por_caderno=4, escala_direita=125.0))
    assert resultado.avisos
    assert all(a.pagina % 2 == 1 for a in resultado.avisos)    # só as da direita (ímpares)
    assert any("abaixo de 1 cm" in a.texto for a in resultado.avisos)
    with fitz.open(str(tmp_path / "s.pdf")) as doc:
        img = _imagem(doc, 0)
    numero, _caixa = _pagina_na_metade(img, True)
    assert numero == 4                                # a da esquerda segue a dela


def test_ultimo_caderno_menor_no_livreto(tmp_path):
    entrada = _livro(tmp_path / "l.pdf", 23)
    resultado = imp.montar_para_impressao(entrada, tmp_path / "s.pdf", _opcoes())
    assert resultado.paginas_do_arquivo == 12       # 5 folhas + 1 folha, frente e verso
    assert resultado.cadernos == 2
    assert "o último grupo tem 1 folha" in resultado.instrucoes[1]


def test_pagina_deitada_gira_de_pe_e_avisa(tmp_path):
    """g9-folha-maior-impressao: "gira de pé e reduz até caber na página A5" +
    "Quero que o programa avise"."""
    entrada = _livro(tmp_path / "l.pdf", 4, deitadas=(3,))
    resultado = imp.montar_para_impressao(entrada, tmp_path / "s.pdf", _opcoes(paginas_por_caderno=4))
    assert [a.pagina for a in resultado.avisos if "girada" in a.texto] == [3]
    with fitz.open(str(tmp_path / "s.pdf")) as doc:
        img = _imagem(doc, 1)                         # verso: 2 | 3
    numero, (x0, y0, x1, y1) = _pagina_na_metade(img, False)
    assert numero == 3
    assert (y1 - y0) > (x1 - x0)                      # ficou de pé
    assert x0 - 148.5 >= 9 and 297 - x1 >= 12        # dentro das margens


def test_so_frente_folhas_de_ate_e_reverter(tmp_path):
    entrada = _livro(tmp_path / "l.pdf", 8)
    for campos, esperado in (
        (dict(lados=imp.SO_FRENTE), [(8, 1), (6, 3)]),
        (dict(lados=imp.SO_VERSO), [(2, 7), (4, 5)]),
        (dict(folhas_de=2, folhas_ate=2), [(6, 3), (4, 5)]),
        (dict(reverter=True), [(6, 3), (4, 5), (8, 1), (2, 7)]),
        (dict(encadernacao=imp.DIREITA), [(1, 8), (7, 2), (3, 6), (5, 4)]),
    ):
        imp.montar_para_impressao(entrada, tmp_path / "s.pdf", _opcoes(paginas_por_caderno=8, **campos))
        with fitz.open(str(tmp_path / "s.pdf")) as doc:
            ordem = [(_pagina_na_metade(_imagem(doc, i), True)[0],
                      _pagina_na_metade(_imagem(doc, i), False)[0]) for i in range(doc.page_count)]
        assert ordem == esperado, campos


def test_intervalo_que_comeca_em_pagina_par_guarda_a_costura(tmp_path):
    """A página par fica sempre à esquerda (a costura à direita): o intervalo
    que começa na 2 ganha uma branca antes."""
    entrada = _livro(tmp_path / "l.pdf", 8)
    imp.montar_para_impressao(entrada, tmp_path / "s.pdf",
                              _opcoes(paginas_por_caderno=4, paginas_de=2, paginas_ate=4))
    with fitz.open(str(tmp_path / "s.pdf")) as doc:
        frente = _imagem(doc, 0)
        verso = _imagem(doc, 1)
    assert _pagina_na_metade(frente, True)[0] == 4     # 4 | (branca)
    assert _pagina_na_metade(frente, False)[0] is None
    assert (_pagina_na_metade(verso, True)[0], _pagina_na_metade(verso, False)[0]) == (2, 3)


# --------------------------------------------------------------- os outros formatos

def test_pagina_inteira_a4_em_pe(tmp_path):
    entrada = _livro(tmp_path / "l.pdf", 3)
    resultado = imp.montar_para_impressao(entrada, tmp_path / "s.pdf",
                                          _opcoes(formato=imp.PAGINA_INTEIRA))
    with fitz.open(str(tmp_path / "s.pdf")) as doc:
        assert doc.page_count == 3
        assert doc[0].rect.width == pytest.approx(210 * MM, abs=0.5)
        assert doc[0].rect.height == pytest.approx(297 * MM, abs=0.5)
    assert resultado.avisos == []


def test_escalas_da_aba_tamanho(tmp_path):
    area = fitz.Rect(0, 0, 100, 100)
    assert imp.fator_base(50, 50, area, _opcoes(escala=imp.AJUSTAR)) == pytest.approx(2.0)
    assert imp.fator_base(50, 50, area, _opcoes(escala=imp.TAMANHO_REAL)) == 1.0
    assert imp.fator_base(50, 50, area, _opcoes(escala=imp.REDUZIR_GRANDES)) == 1.0
    assert imp.fator_base(200, 200, area, _opcoes(escala=imp.REDUZIR_GRANDES)) == pytest.approx(0.5)
    assert imp.fator_base(50, 50, area, _opcoes(escala=imp.PERSONALIZADA,
                                                escala_percentual=75)) == pytest.approx(0.75)


def test_multiplo_quatro_por_folha(tmp_path):
    entrada = _livro(tmp_path / "l.pdf", 9)
    resultado = imp.montar_para_impressao(entrada, tmp_path / "s.pdf",
                                          _opcoes(formato=imp.MULTIPLO, multiplo_por_folha=4))
    assert resultado.paginas_do_arquivo == 3


def test_poster_divide_a_pagina_grande(tmp_path):
    entrada = _livro(tmp_path / "l.pdf", 1, largura_mm=420, altura_mm=594)    # A2
    resultado = imp.montar_para_impressao(entrada, tmp_path / "s.pdf",
                                          _opcoes(formato=imp.POSTER, orientacao=imp.RETRATO))
    assert resultado.paginas_do_arquivo >= 4
    # pequena e "só páginas grandes": sai inteira numa folha
    entrada = _livro(tmp_path / "p.pdf", 1)
    resultado = imp.montar_para_impressao(entrada, tmp_path / "s2.pdf", _opcoes(formato=imp.POSTER))
    assert resultado.paginas_do_arquivo == 1


def test_como_imagem_de_fabrica_e_cinza(tmp_path):
    """imp-6: "Imprimir como imagem" ligado de fábrica: cada folha é UMA imagem."""
    assert imp.OpcoesDeImpressao().como_imagem is True
    entrada = _livro(tmp_path / "l.pdf", 4)
    opcoes = imp.OpcoesDeImpressao(paginas_por_caderno=4, dpi_da_imagem=72, cinza=True)
    imp.montar_para_impressao(entrada, tmp_path / "s.pdf", opcoes)
    with fitz.open(str(tmp_path / "s.pdf")) as doc:
        for pagina in doc:
            imagens = pagina.get_images(full=True)
            assert len(imagens) == 1
            assert fitz.Pixmap(doc, imagens[0][0]).n == 1      # cinza


def test_opcoes_vao_e_voltam_do_configuracoes_json():
    opcoes = imp.OpcoesDeImpressao(escala_direita=90.0, excecoes={7: 80.0}, formato=imp.MULTIPLO)
    volta = imp.OpcoesDeImpressao.de_dicionario(opcoes.para_dicionario())
    assert volta == opcoes
    assert imp.OpcoesDeImpressao.de_dicionario({"formato": "nada", "papel": 3}) == imp.OpcoesDeImpressao()
    assert imp.OpcoesDeImpressao.de_dicionario(None) == imp.OpcoesDeImpressao()


def test_cancelar_nao_deixa_arquivo(tmp_path):
    entrada = _livro(tmp_path / "l.pdf", 8)
    with pytest.raises(imp.Cancelou):
        imp.montar_para_impressao(entrada, tmp_path / "s.pdf", _opcoes(), cancelado=lambda: True)
    assert not (tmp_path / "s.pdf").exists()
    assert not list(tmp_path.glob("~*"))


# --------------------------------------------------------------- a impressora

def test_imprimir_direto_manda_cada_folha(tmp_path, app):
    """imp-5: a impressora (aqui gravando num PDF, sem gastar papel)."""
    from core import impressora

    entrada = _livro(tmp_path / "l.pdf", 8)
    folhas, resultado = imp.montar_em_memoria(entrada, _opcoes(paginas_por_caderno=8))
    try:
        mandadas = impressora.imprimir(folhas, arquivo_pdf=str(tmp_path / "impresso.pdf"),
                                       copias=1, frente_e_verso=impressora.BORDA_CURTA)
    finally:
        folhas.close()
    assert mandadas == 4
    with fitz.open(str(tmp_path / "impresso.pdf")) as doc:
        assert doc.page_count == 4
        assert doc[0].rect.width > doc[0].rect.height       # A4 deitada
    assert isinstance(impressora.listar_impressoras(), list)
