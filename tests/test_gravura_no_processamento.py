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
    """As opções de fábrica são as do ScanTailor; o livro manda; a página só
    troca a forma (e não quando o livro está em "não procurar")."""
    from core.pipeline import escolha_da_gravura
    from modelos import ConfigPagina, Projeto

    projeto = Projeto(caminho_entrada="")
    detector, opcoes = escolha_da_gravura(projeto)
    assert detector == dr.GRAVURA_SCANTAILOR
    assert opcoes == dr.OpcoesDaGravura("livre", 100, False, True)

    projeto.gravura_forma = "retangular"
    projeto.gravura_sensibilidade = 70
    projeto.gravura_mais_sensivel = True
    projeto.gravura_normalizar = False
    assert escolha_da_gravura(projeto)[1] == dr.OpcoesDaGravura("retangular", 70, True, False)

    pagina = ConfigPagina(indice=0, folha=0)
    assert escolha_da_gravura(projeto, pagina)[1].forma == "retangular"   # segue o livro
    pagina.gravura_forma = "livre"
    assert escolha_da_gravura(projeto, pagina)[1].forma == "livre"        # só esta página
    projeto.gravura_forma = "desligada"
    assert escolha_da_gravura(projeto, pagina)[1].forma == "desligada"    # o livro desligou

    # valor estragado no arquivo vale o padrão (ou fica dentro da faixa)
    projeto.gravura_forma = "redonda"
    projeto.gravura_sensibilidade = 500
    pagina.gravura_forma = "oval"
    opcoes = escolha_da_gravura(projeto, pagina)[1]
    assert opcoes.forma == "livre" and opcoes.sensibilidade == 100


def test_projeto_antigo_abre_com_as_opcoes_de_fabrica():
    from modelos import Projeto

    antigo = {"caminho_entrada": "x.pdf", "filtro_padrao": "magico_pro",
              "paginas": [{"indice": 0, "folha": 0, "metade": "inteira", "selecao": []}],
              "folhas": [{"indice": 0}]}
    projeto = Projeto.de_dicionario(antigo)
    assert (projeto.gravura_forma, projeto.gravura_sensibilidade,
            projeto.gravura_mais_sensivel, projeto.gravura_normalizar) == ("livre", 100, False, True)
    assert projeto.paginas[0].gravura_forma is None
    assert projeto.paginas[0].gravura_feita_com == ""
    # e ida e volta pelo dicionário guarda tudo
    projeto.gravura_forma = "retangular"
    projeto.paginas[0].gravura_forma = "livre"
    de_novo = Projeto.de_dicionario(projeto.para_dicionario())
    assert de_novo.gravura_forma == "retangular" and de_novo.paginas[0].gravura_forma == "livre"


def test_assinatura_muda_so_com_o_que_muda_a_gravura():
    a = dr.assinatura_da_gravura
    livre = dr.OpcoesDaGravura("livre", 100)
    assert a(dr.GRAVURA_SCANTAILOR, livre) == a(dr.GRAVURA_SCANTAILOR, dr.OpcoesDaGravura("livre", 40))
    assert a(dr.GRAVURA_SCANTAILOR, livre) != a(dr.GRAVURA_SCANTAILOR, dr.OpcoesDaGravura("retangular"))
    ret_100 = a(dr.GRAVURA_SCANTAILOR, dr.OpcoesDaGravura("retangular", 100))
    assert ret_100 != a(dr.GRAVURA_SCANTAILOR, dr.OpcoesDaGravura("retangular", 70))
    assert a(dr.GRAVURA_SCANTAILOR, livre) != a(dr.GRAVURA_SCANTAILOR, dr.OpcoesDaGravura(mais_sensivel=True))
    assert a(dr.GRAVURA_SCANTAILOR, livre) != a(dr.GRAVURA_SCANTAILOR, dr.OpcoesDaGravura(normalizar=False))


def test_forma_desligada_nao_chama_a_dll(monkeypatch):
    chamadas = []
    monkeypatch.setattr(gs, "detectar_gravura", lambda *a, **k: chamadas.append(1))
    img, gravura, escrita = pagina_com_gravura()
    selecao = dr.detectar(img, usar_layout=False, detector_de_gravura=dr.GRAVURA_SCANTAILOR,
                          opcoes_da_gravura=dr.OpcoesDaGravura("desligada"), dpi=150)
    achada, letra = _mascaras(selecao, img)
    assert chamadas == []
    assert selecao.gravura_por == dr.GRAVURA_NENHUMA and selecao.aviso_gravura is None
    assert not achada.any()


@precisa_da_dll
def test_as_opcoes_chegam_a_dll(monkeypatch):
    pedidos = []
    original = gs.detectar_gravura

    def espiao(img, dpi, **k):
        pedidos.append(k)
        return original(img, dpi, **k)

    monkeypatch.setattr(gs, "detectar_gravura", espiao)
    img, _g, _e = pagina_com_gravura()
    dr.detectar(img, usar_layout=False, detector_de_gravura=dr.GRAVURA_SCANTAILOR,
                opcoes_da_gravura=dr.OpcoesDaGravura("retangular", 40, True, False), dpi=150)
    assert pedidos == [{"forma": "retangular", "sensibilidade": 40, "mais_sensivel": True,
                        "normalizar_iluminacao": False}]


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
    assert pedidos[0]["opcoes_da_gravura"] == dr.OpcoesDaGravura()
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


# ------------------------------------------------------------- refazer a gravura quando as opções mudam

def _garantir(projeto, pagina, img):
    """garantir_selecao numa imagem a 150 DPI, escaneada a 150."""
    from core import pipeline

    return pipeline.garantir_selecao(projeto, pagina, img, 150, 150)


def test_opcao_mudada_refaz_so_o_que_a_maquina_marcou(monkeypatch):
    """Mudou a forma (no livro ou na página): a parte automática é refeita, a
    marcação à mão (com o filtro por pedaço) volta por cima, na ordem."""
    from core.selecao import MAO, SUBTRAIR, Regiao, retangulo
    from modelos import ConfigPagina, Projeto

    feitas = []
    original = dr.detectar

    def espiao(img, *a, **k):
        feitas.append(k["opcoes_da_gravura"].forma)
        return original(img, *a, **{**k, "usar_layout": False})

    monkeypatch.setattr(dr, "detectar", espiao)
    img, _g, _e = pagina_com_gravura()
    projeto = Projeto(caminho_entrada="")
    pagina = ConfigPagina(indice=0, folha=0)

    primeira = _garantir(projeto, pagina, img)
    assert feitas == ["livre"] and pagina.gravura_feita_com.startswith("scantailor|livre")
    a_mao = retangulo(0.1, 0.1, 0.3, 0.2, origem=MAO, filtro="original")
    tirar = Regiao(tipo="gravura", forma="retangulo", pontos=[(0.2, 0.5), (0.3, 0.6)],
                   operacao=SUBTRAIR, origem=MAO)
    primeira.acrescentar(a_mao)
    primeira.acrescentar(tirar)
    pagina.guardar_selecao(primeira)

    _garantir(projeto, pagina, img)                       # nada mudou: não refaz
    assert feitas == ["livre"]

    pagina.gravura_forma = "retangular"                   # "Esta página tem foto"
    nova = _garantir(projeto, pagina, img)
    assert feitas == ["livre", "retangular"]
    assert pagina.gravura_feita_com.startswith("scantailor|retangular")
    a_mao_depois = [r for r in nova.regioes if r.origem == MAO]
    assert [r.para_dicionario() for r in a_mao_depois] == [a_mao.para_dicionario(),
                                                           tirar.para_dicionario()]
    assert nova.regioes[-2:] == a_mao_depois, "a marcação à mão tem de vir por cima"

    pagina.gravura_forma = None                           # desfazer: volta a seguir o livro
    _garantir(projeto, pagina, img)
    assert feitas[-1] == "livre"


def test_marcacao_de_projeto_antigo_nao_e_refeita_sozinha(monkeypatch):
    """Página marcada antes deste campo existir (assinatura vazia): fica como está."""
    from core.selecao import Selecao, retangulo
    from modelos import ConfigPagina, Projeto

    chamadas = []
    monkeypatch.setattr(dr, "detectar", lambda *a, **k: chamadas.append(k))
    projeto = Projeto(caminho_entrada="")
    projeto.gravura_forma = "retangular"
    pagina = ConfigPagina(indice=0, folha=0)
    antiga = Selecao()
    antiga.acrescentar(retangulo(0.1, 0.1, 0.5, 0.5, origem="rede"))
    pagina.guardar_selecao(antiga)
    img, _g, _e = pagina_com_gravura()
    assert _garantir(projeto, pagina, img).para_lista() == antiga.para_lista()
    assert chamadas == []


def test_deteccao_que_falha_ao_refazer_nao_perde_a_marcacao(monkeypatch):
    from core.selecao import MAO, Selecao, retangulo
    from modelos import ConfigPagina, Projeto

    projeto = Projeto(caminho_entrada="")
    pagina = ConfigPagina(indice=0, folha=0)
    marcada = Selecao()
    marcada.acrescentar(retangulo(0.1, 0.1, 0.5, 0.5, origem="rede"))
    marcada.acrescentar(retangulo(0.6, 0.6, 0.7, 0.7, origem=MAO))
    pagina.guardar_selecao(marcada)
    pagina.gravura_feita_com = "scantailor|livre|-|0|1"
    projeto.gravura_forma = "retangular"

    def explode(*_a, **_k):
        raise RuntimeError("de mentira")

    monkeypatch.setattr(dr, "detectar", explode)
    img, _g, _e = pagina_com_gravura()
    assert _garantir(projeto, pagina, img).para_lista() == marcada.para_lista()
    assert pagina.selecao == marcada.para_lista()


# ------------------------------------------------------------- o aviso quando a DLL falta (bug de 30/09)

@pytest.fixture(autouse=True)
def avisos_limpos(monkeypatch):
    """Os avisos de falha da gravura ficam só neste arquivo (são uma vez por
    sessão): sem isto, uma falha de mentira daqui deixava a frase pendente, e
    a primeira janela de outro teste abria a caixa "Gravuras e fotos"."""
    monkeypatch.setattr(dr, "_JA_AVISADOS", set())
    monkeypatch.setattr(dr, "_AVISO_DA_TELA", {"pendente": None, "ja_mostrado": False})


def test_dll_ausente_vai_para_o_erros_log_e_para_a_tela_uma_vez(monkeypatch, tmp_path,
                                                                 avisos_limpos):
    from registro import caminho_do_log

    monkeypatch.setattr(gs, "_padrao", gs.DetectorGravuraScanTailor(tmp_path / "nao_existe.dll"))
    log = caminho_do_log()
    antes = log.read_text(encoding="utf-8") if log.exists() else ""
    img, _g, _e = pagina_com_gravura()
    for _vez in range(3):
        dr.detectar(img, usar_layout=False, detector_de_gravura=dr.GRAVURA_SCANTAILOR, dpi=150)

    novo = log.read_text(encoding="utf-8")[len(antes):]
    assert novo.count("| detector de gravura (item 1.2) =====") == 1, "no erros.log, uma vez"
    assert "nao_existe.dll" in novo, "o detalhe técnico vai para o log"
    frase = dr.aviso_da_gravura_para_a_tela()
    assert frase == dr.AVISO_DA_GRAVURA_NA_TELA
    assert "não pôde ser usado" in frase and "Traceback" not in frase and ".dll" not in frase
    assert dr.aviso_da_gravura_para_a_tela() is None, "na tela, uma vez só"


def test_sem_falha_nao_ha_aviso(avisos_limpos):
    img, _g, _e = pagina_com_gravura()
    dr.detectar(img, usar_layout=False)
    assert dr.aviso_da_gravura_para_a_tela() is None


def test_a_janela_mostra_o_aviso_da_gravura_uma_vez(monkeypatch, avisos_limpos):
    from PySide6.QtWidgets import QApplication

    QApplication.instance() or QApplication([])
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    try:
        vistos = []
        monkeypatch.setattr(janela, "avisar", lambda frase, titulo="": vistos.append(frase))
        dr._avisar_uma_vez("motivo de teste", "detalhe de teste")
        janela._avisar_da_gravura()
        janela._avisar_da_gravura()
        assert vistos == [dr.AVISO_DA_GRAVURA_NA_TELA]
    finally:
        janela.tela_opcoes.folhear.fechar()
        janela.close()


# ------------------------------------------------------------- consertos do detector (Graduale 222, Horas 13)

def test_a_gravura_cresce_pela_moldura_e_para_no_papel():
    """Horas 13: o ScanTailor pega só a beirada de dentro da moldura; a
    gravura cresce pela faixa (não é papel) e para no papel em volta."""
    altura, largura = 1000, 800
    img = np.full((altura, largura, 3), (205, 225, 235), np.uint8)       # papel creme
    faixa = np.zeros((altura, largura), bool)
    faixa[100:900, 100:700] = True
    faixa[115:885, 115:685] = False                                     # moldura de 15 pontos (1,9%)
    img[faixa] = (40, 140, 170)                                         # dourado
    so_a_beirada = np.zeros_like(faixa)
    so_a_beirada[110:890, 110:690] = True
    so_a_beirada[115:885, 115:685] = False                              # 5 pontos de dentro
    crescida = dr._crescer_pela_moldura(so_a_beirada, img)
    assert crescida[faixa].mean() > 0.98, "a faixa inteira tem de entrar"
    assert not crescida[50, 400] and not crescida[500, 400], "o papel não entra"
    assert (crescida | so_a_beirada).sum() == crescida.sum(), "nunca encolhe"


def test_barra_fina_na_beirada_sai_mesmo_presa_a_gravura():
    altura, largura = 1000, 800
    m = np.zeros((altura, largura), bool)
    m[300:600, 200:500] = True                 # gravura de verdade
    m[:, largura - 25:] = True                 # faixa escura da beirada direita
    m[400:420, 500:largura] = True             # ligando as duas
    limpa = dr._sem_barras_na_beirada(m)
    assert limpa[450, 350] and not limpa[100, largura - 5]
    foto = np.zeros((altura, largura), bool)
    foto[:, :] = True                          # foto que vai até a beirada: grossa, fica
    assert dr._sem_barras_na_beirada(foto).all()


def test_figura_julgada_escrita_tira_a_gravura_do_scantailor(monkeypatch):
    """Graduale 222: a caixa "figure" do modelo em volta da partitura é
    julgada escrita; ali a gravura do ScanTailor sai (e a peça que era quase
    toda de dentro da caixa sai inteira)."""
    img, gravura, escrita = pagina_com_gravura()
    altura, largura = img.shape[:2]
    faixa = np.zeros((altura, largura), bool)
    faixa[100:700, 50:1050] = True             # "pauta" marcada pelo ScanTailor
    faixa[60:100, 50:1050] = True              # um pouco para fora da caixa
    monkeypatch.setattr(dr, "_gravura_pelo_scantailor", lambda *a, **k: (faixa.copy(), None))
    caixa = dr.Achado("figure", 0.9, (50 / largura, 100 / altura, 1050 / largura, 700 / altura))
    monkeypatch.setattr(dr._detector, "achar", lambda img: [caixa])
    selecao = dr.detectar(img, detector_de_gravura=dr.GRAVURA_SCANTAILOR, dpi=150)
    achada, _l = _mascaras(selecao, img)
    assert not achada[faixa].any(), "a pauta (e o pedaço fora da caixa) não pode ser gravura"
