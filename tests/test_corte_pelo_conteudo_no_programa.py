"""O corte que segue o conteúdo LIGADO ao programa (item 2.5): core/pipeline.py.

Decisões: G8 (a) e G9 (05/10/2026: opção desligada de fábrica; "Todas as
páginas do tamanho da maior: Sim"); g8-moldura-tinta-fora e
g9-pagina-muito-maior (13/10/2026). Regra da Fase 2 (13/10): quando muda a
imagem, vem desligado e o livro já começado sai igual.

Testes de máquina:
- o campo: desligado de fábrica; projeto sem o campo abre desligado; vai e
  volta do arquivo; o campo novo da página (alinhar_com_as_outras) também;
- DESLIGADO NADA MUDA: a conta do ScanTailor não é chamada nem na prévia nem
  ao gerar o PDF, nas duas ordens, e o corte é o de sempre;
- ligado (com a medida do ScanTailor trocada por uma fixa, sem DLL): o corte
  é a caixa + 1 mm; do tamanho do livro com as outras páginas; a muito maior
  fica de fora e avisa; o "pôr de volta"; o aviso de tinta de fora e o corte
  alargado; desligar tira os avisos; o corte à mão vale como está;
- com a DLL (pula sem ela): um livro de mentira de 4 páginas gerado em PDF
  sai com as 3 páginas comuns do MESMO tamanho e a muito maior no dela.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import analise  # noqa: E402
from core import caixas_scantailor as cs  # noqa: E402
from core import corte_pelo_conteudo as cc  # noqa: E402
from core import endireitar_scantailor as es  # noqa: E402
from core import pipeline  # noqa: E402
from core import st_ferramentas  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402
from core.recortar import detectar_bordas  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402

DPI = 200
LARGURA, ALTURA = 1165, 1654          # A5 a 200 DPI


@pytest.fixture(autouse=True)
def _limpo():
    for guardados in (pipeline._GEOMETRIAS, pipeline._ANGULOS_MEDIDOS,
                      pipeline._CONTEUDOS, pipeline._TAMANHOS):
        guardados.clear()
    yield
    for guardados in (pipeline._GEOMETRIAS, pipeline._ANGULOS_MEDIDOS,
                      pipeline._CONTEUDOS, pipeline._TAMANHOS):
        guardados.clear()


def _folha_de_texto(bloco, numero_no_pe=False):
    """Uma folha A5 a 200 DPI com um bloco de "texto" (x0, y0, x1, y1)."""
    img = np.full((ALTURA, LARGURA, 3), 255, np.uint8)
    x0, y0, x1, y1 = bloco
    for y in range(y0, y1 - 14, 34):
        for x in range(x0, x1 - 38, 52):
            cv2.rectangle(img, (x, y), (x + 38, y + 14), (0, 0, 0), -1)
    if numero_no_pe:
        cv2.rectangle(img, (LARGURA // 2 - 12, y1 + 120), (LARGURA // 2 + 12, y1 + 150), (0, 0, 0), -1)
    return img


def _pdf(pasta: Path, blocos, nome="livro") -> str:
    caminho = pasta / f"{nome}.pdf"
    doc = fitz.open()
    for i, bloco in enumerate(blocos):
        png = pasta / f"{nome}-{i}.png"
        cv2.imwrite(str(png), _folha_de_texto(bloco))
        pagina = doc.new_page(width=LARGURA * 72 / DPI, height=ALTURA * 72 / DPI)
        pagina.insert_image(pagina.rect, filename=str(png))
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _projeto(caminho: str, n: int, **campos) -> Projeto:
    campos.setdefault("endireitar", False)
    p = Projeto(caminho_entrada=caminho, qualidade_dpi=DPI, filtro_padrao=ORIGINAL,
                detectar_regioes=False, limpar=False, **campos)
    p.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(n)]
    p.paginas = [ConfigPagina(indice=i, folha=i, filtro=ORIGINAL) for i in range(n)]
    return p


def _desenhar(caminho: str, indice: int = 0) -> np.ndarray:
    doc = abrir_pdf(caminho)
    try:
        return pagina_para_array(doc, indice, dpi=DPI)
    finally:
        doc.close()


MM = 25.4 / DPI


def _medida_fixa(caixas: dict):
    """Troca corte_pelo_conteudo.medir por uma medida fixa por página (pela
    soma dos pontos da imagem, que muda de página para página): o teste não
    depende da DLL."""
    def medir(img, dpi=None, dpi_do_scan=None, **_k):
        cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        tinta = np.argwhere(cinza < 128)
        if tinta.size == 0:
            return cc.MedidaDoConteudo(img.shape[1], img.shape[0], None, None, (MM, MM), "vazia")
        (y0, x0), (y1, x1) = tinta.min(0), tinta.max(0) + 1
        caixa = caixas.get("forcada") or (float(x0), float(y0), float(x1), float(y1))
        return cc.MedidaDoConteudo(img.shape[1], img.shape[0], caixa,
                                   ((caixa[2] - caixa[0]) * MM, (caixa[3] - caixa[1]) * MM), (MM, MM))
    return medir


# ---------------------------------------------------------------- o campo

def test_desligado_de_fabrica_e_projeto_antigo_abre_desligado():
    assert Projeto(caminho_entrada="x.pdf").cortar_pelo_conteudo is False
    dados = Projeto(caminho_entrada="x.pdf").para_dicionario()
    dados.pop("cortar_pelo_conteudo")
    assert Projeto.de_dicionario(dados).cortar_pelo_conteudo is False
    assert ConfigPagina(indice=0, folha=0).alinhar_com_as_outras is None


def test_os_campos_vao_e_voltam_do_arquivo():
    p = Projeto(caminho_entrada="x.pdf", cortar_pelo_conteudo=True)
    p.folhas = [ConfigFolha(indice=0)]
    p.paginas = [ConfigPagina(indice=0, folha=0, alinhar_com_as_outras=True)]
    volta = Projeto.de_dicionario(p.para_dicionario())
    assert volta.cortar_pelo_conteudo is True
    assert volta.paginas[0].alinhar_com_as_outras is True


# ------------------------------------------------------- desligado nada muda

@pytest.mark.parametrize("ordem", ["endireitar_antes", "cortar_antes"])
def test_desligado_nao_chama_o_scantailor_e_o_corte_e_o_de_sempre(tmp_path, monkeypatch, ordem):
    """Regra da Fase 2: desligado de fábrica, o livro sai igual. Nem a prévia
    nem o PDF chamam a conta da caixa do conteúdo."""
    def proibido(*_a, **_k):
        raise AssertionError("a caixa do conteúdo foi chamada com a opção desligada")

    monkeypatch.setattr(cs, "achar", proibido)
    monkeypatch.setattr(cc, "medir", proibido)
    caminho = _pdf(tmp_path, [(150, 200, 1000, 1400), (300, 400, 800, 1100)])
    projeto = _projeto(caminho, 2, ordem_do_preparo=ordem, endireitar=False)
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    img = _desenhar(caminho)
    folha, pagina = projeto.folhas[0], projeto.paginas[0]
    saida, desenho = pipeline.preparar_metade_e_geometria(img, folha, pagina, projeto, dpi=DPI)
    assert tuple(desenho["recorte"]) == pytest.approx(detectar_bordas(img, dpi=DPI).tupla)
    pipeline.processar(projeto)
    assert Path(projeto.caminho_saida).exists()
    # com o endireitar ligado, também nada é chamado (prévia e PDF)
    projeto.endireitar, projeto.endireitar_como = True, es.JEITO_PROGRAMA
    pipeline.preparar_metade_e_geometria(img, folha, pagina, projeto, dpi=DPI)
    pipeline.processar(projeto)
    assert not pipeline._CONTEUDOS and not pipeline._TAMANHOS


# ------------------------------------------------------------ ligado, sem DLL

def test_ligado_o_corte_e_a_caixa_mais_1_mm(tmp_path, monkeypatch):
    monkeypatch.setattr(cc, "medir", _medida_fixa({}))
    caminho = _pdf(tmp_path, [(150, 200, 1000, 1400)])
    projeto = _projeto(caminho, 1, cortar_pelo_conteudo=True)
    img = _desenhar(caminho)
    pipeline._guardar_geometria(projeto.folhas[0], projeto.paginas[0], projeto, img)
    saida, desenho = pipeline.preparar_metade_e_geometria(img, projeto.folhas[0], projeto.paginas[0],
                                                          projeto, dpi=DPI)
    x, y, w, h = desenho["recorte"]
    um_mm = 1 / MM
    assert x * LARGURA == pytest.approx(150 - um_mm, abs=1.5)
    assert y * ALTURA == pytest.approx(200 - um_mm, abs=1.5)
    assert (x + w) * LARGURA == pytest.approx(1000 - 14 + um_mm, abs=40)   # o último bloco da linha
    assert saida.shape[0] == pytest.approx(h * ALTURA, abs=2)


def _livro_medido(tmp_path, monkeypatch, blocos, **campos):
    monkeypatch.setattr(cc, "medir", _medida_fixa({}))
    caminho = _pdf(tmp_path, blocos)
    projeto = _projeto(caminho, len(blocos), cortar_pelo_conteudo=True, **campos)
    assert pipeline.medir_conteudo_do_livro(projeto) == len(blocos)
    return caminho, projeto


def _corte(projeto, caminho, i):
    img = _desenhar(caminho, i)
    folha, pagina = projeto.folhas[i], projeto.paginas[i]
    pipeline._guardar_geometria(folha, pagina, projeto, img)
    saida, desenho = pipeline.preparar_metade_e_geometria(img, folha, pagina, projeto, dpi=DPI)
    return saida, desenho


BLOCOS = [(150, 200, 950, 1400), (200, 300, 950, 1300), (250, 350, 900, 1250),
          (40, 40, 1130, 1620)]                       # a última: muito maior


def test_g9_todas_do_tamanho_da_maior_e_a_muito_maior_fica_de_fora(tmp_path, monkeypatch):
    """G9 ("Todas as páginas do tamanho da maior: Sim") e g9-pagina-muito-maior
    ("O programa deixa essa folha de fora sozinho, e avisa")."""
    caminho, projeto = _livro_medido(tmp_path, monkeypatch, BLOCOS)
    livro = pipeline.tamanho_do_livro(projeto)
    assert livro.muito_maiores == frozenset({3})
    tamanhos = [_corte(projeto, caminho, i)[0].shape[:2] for i in range(4)]
    assert tamanhos[0] == pytest.approx(tamanhos[1], abs=2)
    assert tamanhos[0] == pytest.approx(tamanhos[2], abs=2)
    assert tamanhos[3][0] > tamanhos[0][0] + 100              # a muito maior, no tamanho dela
    assert analise.PAGINA_MUITO_MAIOR in projeto.paginas[3].alertas
    assert all(analise.PAGINA_MUITO_MAIOR not in p.alertas for p in projeto.paginas[:3])


def test_g9_pagina_posta_de_volta_entra_na_conta(tmp_path, monkeypatch):
    caminho, projeto = _livro_medido(tmp_path, monkeypatch, BLOCOS)
    projeto.paginas[3].alinhar_com_as_outras = True
    assert pipeline.tamanho_do_livro(projeto).muito_maiores == frozenset()
    _corte(projeto, caminho, 3)
    assert analise.PAGINA_MUITO_MAIOR not in projeto.paginas[3].alertas


def test_corte_a_mao_vale_como_esta(tmp_path, monkeypatch):
    caminho, projeto = _livro_medido(tmp_path, monkeypatch, BLOCOS[:3])
    projeto.paginas[1].recorte = (0.1, 0.1, 0.5, 0.5)
    _saida, desenho = _corte(projeto, caminho, 1)
    assert tuple(desenho["recorte"]) == pytest.approx((0.1, 0.1, 0.5, 0.5))


def test_g8_avisa_o_que_ficou_de_fora_e_da_o_corte_alargado(tmp_path, monkeypatch):
    """g8-moldura-tinta-fora: "Só avisa" + "ele avisa e da opção e de mudar o
    corte e mostrar ele alargado com o que foi tirado". A caixa (forçada)
    deixa de fora a parte de baixo do texto: aviso; o corte alargado pega."""
    monkeypatch.setattr(cc, "medir", _medida_fixa({"forcada": (150.0, 200.0, 1000.0, 700.0)}))
    caminho = _pdf(tmp_path, [(150, 200, 1000, 1400)])
    projeto = _projeto(caminho, 1, cortar_pelo_conteudo=True)
    _corte(projeto, caminho, 0)
    pagina = projeto.paginas[0]
    assert analise.CORTE_DEIXOU_TINTA_FORA in pagina.alertas
    x, y, w, h = pipeline.corte_alargado(projeto, pagina)
    assert (y + h) * ALTURA > 1370                              # o texto vai até 1370
    # aceitar o alargado = corte à mão: o aviso sai
    pagina.recorte = (x, y, w, h)
    _corte(projeto, caminho, 0)
    assert analise.CORTE_DEIXOU_TINTA_FORA not in pagina.alertas
    assert pipeline.corte_alargado(projeto, pagina) is None


def test_desligar_tira_os_avisos(tmp_path, monkeypatch):
    caminho, projeto = _livro_medido(tmp_path, monkeypatch, BLOCOS)
    _corte(projeto, caminho, 3)
    assert analise.PAGINA_MUITO_MAIOR in projeto.paginas[3].alertas
    projeto.cortar_pelo_conteudo = False
    pipeline.acertar_avisos_do_corte(projeto)
    assert analise.PAGINA_MUITO_MAIOR not in projeto.paginas[3].alertas


def test_sem_a_dll_fica_o_corte_comum(tmp_path, monkeypatch):
    """Sem a DLL (ou página sem conteúdo) o corte é o comum, sem aviso."""
    monkeypatch.setattr(cc, "medir", lambda img, *_a, **_k: cc.MedidaDoConteudo(
        img.shape[1], img.shape[0], None, None, None, "sem DLL"))
    caminho = _pdf(tmp_path, [(150, 200, 1000, 1400)])
    projeto = _projeto(caminho, 1, cortar_pelo_conteudo=True)
    img = _desenhar(caminho)
    _saida, desenho = _corte(projeto, caminho, 0)
    assert tuple(desenho["recorte"]) == pytest.approx(detectar_bordas(img, dpi=DPI).tupla)
    assert not projeto.paginas[0].alertas


def test_ordem_antiga_ligada_tambem_corta_pelo_conteudo(tmp_path, monkeypatch):
    monkeypatch.setattr(cc, "medir", _medida_fixa({}))
    caminho = _pdf(tmp_path, [(150, 200, 950, 1400)])
    projeto = _projeto(caminho, 1, cortar_pelo_conteudo=True, ordem_do_preparo="cortar_antes")
    _saida, desenho = _corte(projeto, caminho, 0)
    x, y, _w, _h = desenho["recorte"]
    assert x * LARGURA == pytest.approx(150 - 1 / MM, abs=1.5)


# -------------------------------------------------------------- com a DLL

precisa_da_dll = pytest.mark.skipif(
    st_ferramentas.padrao().funcao("st_ferramentas_caixas") is None,
    reason="sem a DLL do ScanTailor (st_ferramentas)")


@precisa_da_dll
def test_pdf_de_verdade_paginas_do_mesmo_tamanho(tmp_path):
    """O objetivo do G9, no PDF gerado: com a opção ligada, as três páginas
    comuns saem do mesmo tamanho e a muito maior sai no dela, com o aviso;
    desligada, cada uma sai do tamanho do seu corte."""
    caminho = _pdf(tmp_path, BLOCOS)
    tamanhos = {}
    for ligado in (True, False):
        projeto = _projeto(caminho, 4, cortar_pelo_conteudo=ligado)
        projeto.caminho_saida = str(tmp_path / f"saida-{ligado}.pdf")
        pipeline.processar(projeto)
        with fitz.open(projeto.caminho_saida) as doc:
            tamanhos[ligado] = [(round(p.rect.width, 1), round(p.rect.height, 1)) for p in doc]
        if ligado:
            assert analise.PAGINA_MUITO_MAIOR in projeto.paginas[3].alertas
    com = tamanhos[True]
    assert com[0] == pytest.approx(com[1], abs=1.0) and com[0] == pytest.approx(com[2], abs=1.0)
    assert com[3][1] > com[0][1] + 20
    sem = tamanhos[False]
    assert abs(sem[0][1] - sem[2][1]) > 20                  # desligado: tamanhos diferentes


def test_faxina_dos_avisos_tira_os_do_corte_pelo_conteudo(tmp_path, monkeypatch):
    """acertar_alertas_do_fundo (que a tela chama ao abrir e a cada
    atualização) tira os avisos do 2.5 das páginas onde não valem mais."""
    caminho, projeto = _livro_medido(tmp_path, monkeypatch, BLOCOS)
    _corte(projeto, caminho, 3)
    projeto.paginas[3].recorte = (0.0, 0.0, 1.0, 1.0)            # virou corte à mão
    pipeline.acertar_alertas_do_fundo(projeto)
    assert analise.PAGINA_MUITO_MAIOR not in projeto.paginas[3].alertas
