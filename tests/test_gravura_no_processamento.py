"""O detector de gravura do ScanTailor ligado ao processamento (item 1.2, segunda etapa).

Testes de máquina (29/09/2026):
- com a DLL, a zona gravura vem do ScanTailor e a letra continua saindo do
  detector de hoje, em volta dela;
- sem o DPI, sem a DLL, com a DLL falhando: cai no detector antigo, com o
  motivo em português, sem exceção;
- o caminho antigo (detector_de_gravura="antigo") é o mesmo de antes;
- a limpeza da gravura do ScanTailor tira respingo e faixa do scanner, e
  deixa gravura e moldura de verdade;
- o DPI que vai à DLL nunca passa o do escaneamento nem 300;
- o processamento (core/pipeline.py) passa à detecção o DPI de verdade da
  imagem e o do escaneamento, na prévia e no PDF;
- a escolha (detector e forma) vem do projeto quando houver o campo, senão
  dos padrões de fábrica.

Páginas sintéticas: rodam em qualquer máquina (os que precisam da DLL são
pulados sem ela). Pasta de dados própria, em saida_teste\\.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from core import detectar_regioes as dr
from core import gravura_scantailor as gs
from core.selecao import GRAVURA, LETRA

RAIZ = Path(__file__).resolve().parent.parent

precisa_da_dll = pytest.mark.skipif(not gs.disponivel(), reason="DLL do ScanTailor não compilada")


@pytest.fixture(autouse=True)
def pasta_de_dados_propria(monkeypatch):
    """LOCALAPPDATA numa pasta deste arquivo de teste, dentro de saida_teste\\."""
    pasta = RAIZ / "saida_teste" / "localappdata_test_gravura_no_processamento"
    pasta.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("LOCALAPPDATA", str(pasta))
    yield pasta


def pagina_com_gravura(dpi: int = 150) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Página branca com linhas de "letras" em cima e uma gravura de meio-tom
    embaixo (a mesma de tests/test_gravura_scantailor.py). Devolve (BGR, onde
    está a gravura, onde está a escrita)."""
    escala = dpi / 150
    # 7,3 x 9 polegadas: cabe no teto de trabalho da DLL
    # (dr.PONTOS_MAXIMOS_DA_GRAVURA), e a DLL a ve no DPI de verdade
    altura, largura = int(1350 * escala), int(1100 * escala)
    img = np.full((altura, largura, 3), 236, np.uint8)
    gravura = np.zeros((altura, largura), bool)
    escrita = np.zeros((altura, largura), bool)
    y0, y1, x0, x1 = int(700 * escala), int(1250 * escala), int(250 * escala), int(1000 * escala)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    tom = 110 + 40 * np.sin(xx / (3.0 * escala)) * np.cos(yy / (5.0 * escala))
    img[y0:y1, x0:x1] = tom.astype(np.uint8)[..., None]
    gravura[y0:y1, x0:x1] = True
    for linha in range(12):
        y = int((150 + linha * 40) * escala)
        for letra in range(36):
            x = int((150 + letra * 24) * escala)
            img[y:y + int(18 * escala), x:x + int(12 * escala)] = 20
            escrita[y:y + int(18 * escala), x:x + int(12 * escala)] = True
    return img, gravura, escrita


def _mascaras(selecao, img):
    altura, largura = img.shape[:2]
    return selecao.mascara(altura, largura, GRAVURA), selecao.mascara(altura, largura, LETRA)


# ------------------------------------------------------------- com a DLL

@precisa_da_dll
def test_gravura_vem_do_scantailor_e_a_letra_continua():
    img, gravura, escrita = pagina_com_gravura()
    selecao = dr.detectar(img, usar_layout=False, detector_de_gravura=dr.GRAVURA_SCANTAILOR,
                          dpi=150)

    assert selecao.gravura_por == dr.GRAVURA_SCANTAILOR
    assert selecao.aviso_gravura is None
    achada, letra = _mascaras(selecao, img)
    assert achada[gravura].mean() > 0.9, "a gravura de meio-tom não virou gravura"
    assert achada[escrita].mean() < 0.05, "a letra virou gravura"
    assert letra[escrita].mean() > 0.9, "a letra não ficou como letra"
    assert not (achada & letra).any(), "gravura e letra não podem se cruzar"


@precisa_da_dll
def test_mesma_gravura_na_previa_e_no_pdf():
    """A prévia (110 DPI) e o PDF (300 DPI) vão à DLL no DPI do escaneamento
    (aqui 100): a gravura sai praticamente igual nos dois."""
    base, _g, _e = pagina_com_gravura(dpi=100)
    altura, largura = base.shape[:2]
    mascaras = []
    for dpi in (110, 300):
        img = cv2.resize(base, (round(largura * dpi / 100), round(altura * dpi / 100)),
                         interpolation=cv2.INTER_LINEAR)
        selecao = dr.detectar(img, usar_layout=False, detector_de_gravura=dr.GRAVURA_SCANTAILOR,
                              dpi=dpi, dpi_do_scan=100)
        m = selecao.mascara(180, 147, GRAVURA)     # as duas no mesmo tamanho
        mascaras.append(m)
    comum = (mascaras[0] & mascaras[1]).sum() / max(1, (mascaras[0] | mascaras[1]).sum())
    assert comum > 0.95


@precisa_da_dll
def test_forma_retangular_tambem_funciona():
    img, gravura, _e = pagina_com_gravura()
    selecao = dr.detectar(img, usar_layout=False, detector_de_gravura=dr.GRAVURA_SCANTAILOR,
                          forma_da_gravura="retangular", dpi=150)
    achada, _l = _mascaras(selecao, img)
    assert selecao.gravura_por == dr.GRAVURA_SCANTAILOR
    assert achada[gravura].mean() > 0.9


# ------------------------------------------------------------- quando não dá

def test_sem_dpi_cai_no_detector_antigo():
    img, _g, _e = pagina_com_gravura()
    selecao = dr.detectar(img, usar_layout=False, detector_de_gravura=dr.GRAVURA_SCANTAILOR)
    assert selecao.gravura_por == dr.GRAVURA_ANTIGA
    assert "resolução" in selecao.aviso_gravura


def test_sem_a_dll_cai_no_detector_antigo_sem_excecao(monkeypatch, tmp_path):
    monkeypatch.setattr(gs, "_padrao", gs.DetectorGravuraScanTailor(tmp_path / "nao_existe.dll"))
    img, _g, _e = pagina_com_gravura()
    selecao = dr.detectar(img, usar_layout=False, detector_de_gravura=dr.GRAVURA_SCANTAILOR,
                          dpi=150)
    antiga = dr.detectar(img, usar_layout=False)

    assert selecao.gravura_por == dr.GRAVURA_ANTIGA
    assert "não foi encontrado" in selecao.aviso_gravura
    assert "detector antigo" in selecao.aviso_gravura
    assert selecao.para_lista() == antiga.para_lista()


def test_dll_que_levanta_excecao_nao_derruba(monkeypatch):
    def explode(*_a, **_k):
        raise RuntimeError("falha de mentira")

    monkeypatch.setattr(gs, "detectar_gravura", explode)
    img, _g, _e = pagina_com_gravura()
    selecao = dr.detectar(img, usar_layout=False, detector_de_gravura=dr.GRAVURA_SCANTAILOR,
                          dpi=150)
    assert selecao.gravura_por == dr.GRAVURA_ANTIGA
    assert "falhou" in selecao.aviso_gravura


def test_dpi_absurdo_nao_chega_a_dll(monkeypatch):
    """A trava do core/gravura_scantailor.py continua valendo pelo caminho novo."""
    chamadas = []

    class _Falsa:
        def st_gravura_detectar(self, *argumentos):
            chamadas.append(argumentos)
            return 0

    detector = gs.DetectorGravuraScanTailor(Path("nao_importa.dll"))
    monkeypatch.setattr(detector, "_carregar", lambda: _Falsa())
    monkeypatch.setattr(gs, "_padrao", detector)
    img, _g, _e = pagina_com_gravura()
    # 300.000 DPI: a página vai à DLL a 300 DPI (o teto), reduzida a menos de
    # 2 pontos de lado - a trava recusa antes da DLL
    selecao = dr.detectar(img, usar_layout=False, detector_de_gravura=dr.GRAVURA_SCANTAILOR,
                          dpi=300_000)
    assert chamadas == []
    assert selecao.gravura_por == dr.GRAVURA_ANTIGA
    assert "pequena demais" in selecao.aviso_gravura


def test_o_caminho_antigo_e_o_de_sempre():
    """detector_de_gravura="antigo" (o padrão de detectar()) = o detector de antes do 1.2."""
    img, _g, _e = pagina_com_gravura()
    sem_nada = dr.detectar(img, usar_layout=False)
    antigo = dr.detectar(img, usar_layout=False, detector_de_gravura=dr.GRAVURA_ANTIGA, dpi=150)
    assert sem_nada.para_lista() == antigo.para_lista()
    assert sem_nada.gravura_por == dr.GRAVURA_ANTIGA and sem_nada.aviso_gravura is None


def test_detector_desconhecido_usa_o_antigo():
    img, _g, _e = pagina_com_gravura()
    selecao = dr.detectar(img, usar_layout=False, detector_de_gravura="nao_existe", dpi=150)
    assert selecao.gravura_por == dr.GRAVURA_ANTIGA


# ------------------------------------------------------------- a limpeza da gravura do ScanTailor

def test_limpeza_tira_respingo_e_faixa_do_scanner():
    altura, largura = 1000, 800
    m = np.zeros((altura, largura), bool)
    m[400:700, 200:600] = True             # gravura de verdade, no meio: fica
    m[100:120, 100:130] = True             # respingo (0,075% da página): sai
    m[:8, :] = m[-8:, :] = True            # moldura do scanner colada na beirada: sai
    m[:, :8] = m[:, -8:] = True
    limpa = dr._limpar_gravura_do_scantailor(m)
    assert limpa[500, 400]
    assert not limpa[110, 115]
    assert not limpa[2, 400] and not limpa[500, 2]


def test_limpeza_tira_a_sombra_da_lombada_e_deixa_a_moldura():
    altura, largura = 1000, 800
    tira = np.zeros((altura, largura), bool)
    tira[50:950, 0:40] = True              # sombra da lombada: tira na beirada esquerda
    tira[400:700, 200:600] = True          # e uma gravura no meio
    limpa = dr._limpar_gravura_do_scantailor(tira)
    assert not limpa[500, 20] and limpa[500, 400]
    anel = np.zeros((altura, largura), bool)
    anel[80:920, 80:720] = True            # moldura dourada dentro da margem: fica
    anel[130:870, 130:670] = False
    assert (dr._limpar_gravura_do_scantailor(anel) == anel).all()


def test_limpeza_de_mascara_vazia():
    vazia = np.zeros((50, 40), bool)
    assert not dr._limpar_gravura_do_scantailor(vazia).any()


def test_teto_de_trabalho_da_dll():
    """Pagina que a 300 DPI passa do teto e dita a DLL num DPI maior, na medida
    para caber; a que cabe vai no DPI de verdade."""
    assert dr._dpi_declarado_a_dll(1100, 1350, 150) == 150        # 5,9 milhoes a 300 DPI
    grande = dr._dpi_declarado_a_dll(1024, 1446, 72)              # Livro de Horas: 25,7 milhoes
    assert grande > 72
    assert (1024 * 300 / grande) * (1446 * 300 / grande) == pytest.approx(
        dr.PONTOS_MAXIMOS_DA_GRAVURA, rel=1e-6)


@pytest.mark.parametrize("dpi, scan, esperado", [
    (110, 72, 72), (300, 72, 72), (110, 400, 110), (300, 400, 300), (600, None, 300),
    (110, 0, 110), (400, 350, 300),
])
def test_dpi_que_vai_a_dll(dpi, scan, esperado):
    assert dr._dpi_para_a_gravura(dpi, scan) == esperado


@precisa_da_dll
def test_mascara_volta_no_tamanho_da_pagina():
    img, _g, _e = pagina_com_gravura(dpi=300)
    mascara, motivo = dr._gravura_pelo_scantailor(img, 300, 150, "livre")
    assert motivo is None
    assert mascara.shape == img.shape[:2] and mascara.dtype == bool


# ------------------------------------------------------------- no processamento (core/pipeline.py)

def test_escolha_da_gravura_de_fabrica_e_do_projeto():
    from core.pipeline import escolha_da_gravura
    from modelos import Projeto

    projeto = Projeto(caminho_entrada="")
    assert escolha_da_gravura(projeto) == (dr.DETECTOR_DE_GRAVURA_PADRAO, dr.FORMA_DA_GRAVURA_PADRAO)
    assert dr.DETECTOR_DE_GRAVURA_PADRAO == dr.GRAVURA_SCANTAILOR
    assert dr.FORMA_DA_GRAVURA_PADRAO == "livre"
    # o campo que ainda não existe em modelos.Projeto: quando existir, manda
    projeto.detector_de_gravura = dr.GRAVURA_ANTIGA
    projeto.forma_da_gravura = "retangular"
    assert escolha_da_gravura(projeto) == (dr.GRAVURA_ANTIGA, "retangular")
    projeto.detector_de_gravura = "qualquer coisa"
    projeto.forma_da_gravura = "redonda"
    assert escolha_da_gravura(projeto) == (dr.DETECTOR_DE_GRAVURA_PADRAO, dr.FORMA_DA_GRAVURA_PADRAO)


def _pdf_com_imagem(caminho: Path, dpi_do_scan: int = 150) -> Path:
    """PDF de uma página A5 (420 x 595 pt) com a página inteira numa imagem
    escaneada a dpi_do_scan."""
    import fitz

    img, _g, _e = pagina_com_gravura(dpi=100)
    largura_pt, altura_pt = 420, 595
    px = cv2.resize(img, (round(largura_pt / 72 * dpi_do_scan), round(altura_pt / 72 * dpi_do_scan)))
    ok, png = cv2.imencode(".png", px)
    assert ok
    doc = fitz.open()
    pagina = doc.new_page(width=largura_pt, height=altura_pt)
    pagina.insert_image(pagina.rect, stream=png.tobytes())
    doc.save(caminho)
    doc.close()
    return caminho


def _projeto_do_pdf(pdf: Path, filtro: str):
    from core import pipeline
    from modelos import Projeto

    projeto = pipeline.analisar_projeto(Projeto(caminho_entrada=str(pdf)))
    for pagina in projeto.paginas:
        pagina.filtro = filtro
    return projeto


@pytest.mark.parametrize("filtro", ["magico_pro", "original"])
def test_previa_passa_o_dpi_de_verdade_para_a_deteccao(tmp_path, monkeypatch, filtro):
    """No Original a detecção também roda (e fica guardada para quando trocar
    de filtro): o DPI tem de ir junto, senão a marcação guardada seria a do
    detector antigo."""
    from core import pipeline
    from core.pdf_io import abrir_pdf

    pdf = _pdf_com_imagem(tmp_path / "livro.pdf", dpi_do_scan=150)
    projeto = _projeto_do_pdf(pdf, filtro)
    pedidos = []
    original = dr.detectar

    def espiao(img, *a, **k):
        pedidos.append(k)
        return original(img, *a, **{**k, "usar_layout": False})

    monkeypatch.setattr(dr, "detectar", espiao)
    doc = abrir_pdf(str(pdf))
    try:
        pipeline.renderizar_pagina(doc, projeto, projeto.paginas[0], dpi=110)
    finally:
        doc.close()

    assert len(pedidos) == 1
    assert pedidos[0]["detector_de_gravura"] == dr.DETECTOR_DE_GRAVURA_PADRAO
    assert pedidos[0]["forma_da_gravura"] == dr.FORMA_DA_GRAVURA_PADRAO
    assert pedidos[0]["dpi"] == pytest.approx(110, abs=1)
    assert pedidos[0]["dpi_do_scan"] == pytest.approx(150, abs=1)
    assert projeto.paginas[0].selecao, "a marcação não ficou guardada na página"


def test_processar_passa_o_dpi_de_verdade_para_a_deteccao(tmp_path, monkeypatch):
    from core import pipeline

    pdf = _pdf_com_imagem(tmp_path / "livro.pdf", dpi_do_scan=150)
    projeto = _projeto_do_pdf(pdf, "preto_e_branco")
    projeto.qualidade_dpi = 200
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pedidos = []
    original = dr.detectar

    def espiao(img, *a, **k):
        pedidos.append(k)
        return original(img, *a, **{**k, "usar_layout": False})

    monkeypatch.setattr(dr, "detectar", espiao)
    pipeline.processar(projeto)

    assert len(pedidos) == 1
    assert pedidos[0]["dpi"] == pytest.approx(200, abs=1)
    assert pedidos[0]["dpi_do_scan"] == pytest.approx(150, abs=1)
    assert Path(projeto.caminho_saida).is_file()


def test_marcacao_ja_feita_nao_e_refeita(tmp_path, monkeypatch):
    """A marcação guardada (inclusive a feita à mão na aba Marcar) vale como
    está: a detecção nova não roda por cima dela."""
    from core import pipeline
    from core.pdf_io import abrir_pdf
    from core.selecao import MAO, Selecao, retangulo

    pdf = _pdf_com_imagem(tmp_path / "livro.pdf")
    projeto = _projeto_do_pdf(pdf, "magico_pro")
    a_mao = Selecao()
    a_mao.acrescentar(retangulo(0.1, 0.1, 0.4, 0.4, tipo=GRAVURA, origem=MAO))
    projeto.paginas[0].guardar_selecao(a_mao)
    chamadas = []
    monkeypatch.setattr(dr, "detectar", lambda *a, **k: chamadas.append(k))
    doc = abrir_pdf(str(pdf))
    try:
        pipeline.renderizar_pagina(doc, projeto, projeto.paginas[0], dpi=110)
    finally:
        doc.close()
    assert chamadas == []
    assert projeto.paginas[0].selecao == a_mao.para_lista()


def test_dpi_do_scan_le_a_lista_de_imagens(tmp_path):
    from core import pipeline
    from core.pdf_io import abrir_pdf, dpi_real_da_pagina

    pdf = _pdf_com_imagem(tmp_path / "livro.pdf", dpi_do_scan=180)
    projeto = _projeto_do_pdf(pdf, "magico_pro")
    doc = abrir_pdf(str(pdf))
    try:
        assert pipeline._dpi_do_scan(doc, projeto.folhas[0]) == pytest.approx(
            dpi_real_da_pagina(doc, 0), abs=0.01)
    finally:
        doc.close()


def test_pdf_sem_imagem_nao_tem_dpi_do_scan(tmp_path):
    import fitz

    from core import pipeline
    from core.pdf_io import abrir_pdf

    caminho = tmp_path / "texto.pdf"
    doc = fitz.open()
    doc.new_page().insert_text((72, 72), "texto")
    doc.save(caminho)
    doc.close()
    projeto = _projeto_do_pdf(caminho, "magico_pro")
    doc = abrir_pdf(str(caminho))
    try:
        assert pipeline._dpi_do_scan(doc, projeto.folhas[0]) is None
    finally:
        doc.close()


# ------------------------------------------------------------- a conferência do programa empacotado

def test_conferir_gravura_do_diagnostico(tmp_path):
    """EditorImpressao.exe --conferir-ocr também diz se a DLL da gravura abre
    (core/ocr_diagnostico.conferir_gravura); nunca levanta exceção."""
    from core.ocr_diagnostico import conferir_gravura

    img, _g, _e = pagina_com_gravura()
    caminho = tmp_path / "pagina.png"
    cv2.imwrite(str(caminho), img)
    info = conferir_gravura(caminho, 150)
    assert info["dll_existe"] == gs.CAMINHO_DLL.is_file()
    if gs.disponivel():
        assert info["leu"] and info["gravura_fracao"] > 0.1
    sem_imagem = conferir_gravura(tmp_path / "nao_existe.png", 150)
    assert "erro" in sem_imagem and not sem_imagem.get("leu", False)
