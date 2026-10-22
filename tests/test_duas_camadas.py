"""Itens 2.10 e 1.6: o PDF de saída em duas camadas, como opção (core/duas_camadas.py).

Testes de máquina:
- desmarcado de fábrica (livro novo e projeto antigo) e, desmarcado, o PDF sai
  com uma imagem por página, como sempre;
- marcado, a página colorida sai com duas imagens (o fundo pequeno embaixo, a
  de cima com máscara), do mesmo tamanho, parecida com a de uma camada e menor;
- a página de 1 bit sai como sempre;
- a máscara pega letra e cor e deixa o papel embaixo.
"""

from __future__ import annotations

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import duas_camadas
from core.pdf_io import EscritorPDF


def _pagina_colorida():
    """Papel creme com ruído (escaneado), letras pretas e uma iluminura vermelha."""
    gerador = np.random.default_rng(3)
    img = np.clip(np.full((900, 650, 3), (225, 238, 245), np.float32)
                  + gerador.normal(0, 6, (900, 650, 3)), 0, 255).astype(np.uint8)
    for y in range(120, 820, 40):
        img[y:y + 14, 80:570] = (25, 25, 25)
    img[60:100, 80:140] = (30, 30, 200)
    return img


def test_desmarcado_de_fabrica_e_projeto_antigo():
    from modelos import Projeto

    assert Projeto(caminho_entrada="x").pdf_em_duas_camadas is False
    dados = Projeto(caminho_entrada="x").para_dicionario()
    dados.pop("pdf_em_duas_camadas")
    assert Projeto.de_dicionario(dados).pdf_em_duas_camadas is False


def test_mascara_pega_a_tinta_e_a_cor_e_deixa_o_papel():
    img = _pagina_colorida()
    mascara = duas_camadas.mascara_de_cima(img)
    assert mascara[125, 300] and mascara[80, 100]           # letra e iluminura
    assert not mascara[500, 20]                               # papel da margem
    assert mascara.mean() < 0.6


def test_duas_camadas_menor_e_parecida(tmp_path):
    img = _pagina_colorida()
    with EscritorPDF(tmp_path / "uma.pdf") as e:
        e.escrever_imagem(img, dpi=150)
    with EscritorPDF(tmp_path / "duas.pdf") as e:
        e.escrever_em_duas_camadas(img, dpi=150)
    uma, duas = fitz.open(str(tmp_path / "uma.pdf")), fitz.open(str(tmp_path / "duas.pdf"))
    try:
        assert duas[0].rect == uma[0].rect
        assert len(duas[0].get_images()) == 2
        assert (tmp_path / "duas.pdf").stat().st_size < (tmp_path / "uma.pdf").stat().st_size * 0.6
        a = np.frombuffer(uma[0].get_pixmap(dpi=150).samples, np.uint8).astype(int)
        b = np.frombuffer(duas[0].get_pixmap(dpi=150).samples, np.uint8).astype(int)
        assert np.abs(a - b).mean() < 8
    finally:
        uma.close()
        duas.close()


def test_no_processar_a_caixinha_vale_e_o_1_bit_sai_como_sempre(tmp_path):
    import cv2

    from core.filtros import MELHORAR, PRETO_E_BRANCO
    from core.pipeline import processar
    from modelos import ConfigFolha, ConfigPagina, Projeto

    doc = fitz.open()
    for _ in range(2):
        ok, buf = cv2.imencode(".png", _pagina_colorida())
        pagina = doc.new_page(width=650 * 72 / 150, height=900 * 72 / 150)
        pagina.insert_image(pagina.rect, stream=buf.tobytes())
    doc.save(str(tmp_path / "l.pdf"))
    doc.close()

    def gerar(nome, duas):
        projeto = Projeto(caminho_entrada=str(tmp_path / "l.pdf"), caminho_saida=str(tmp_path / nome),
                          dividir_folhas=False, endireitar=False, cortar_bordas=False,
                          detectar_regioes=False, qualidade_dpi=150, pdf_em_duas_camadas=duas)
        projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(2)]
        projeto.paginas = [ConfigPagina(indice=0, folha=0, filtro=MELHORAR),
                           ConfigPagina(indice=1, folha=1, filtro=PRETO_E_BRANCO)]
        processar(projeto)
        with fitz.open(str(tmp_path / nome)) as saida:
            return [len(p.get_images()) for p in saida]

    assert gerar("de-sempre.pdf", False) == [1, 1]
    assert gerar("camadas.pdf", True) == [2, 1]               # o 1 bit sai como sempre
