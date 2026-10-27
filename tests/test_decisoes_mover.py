"""As provas de comportamento da etapa 5 da obra de 26/10/2026: a ferramenta "Mover e
redimensionar" (CLAUDE.md §11, regra 4; Livro de decisões, docs/plano/DECISOES.md).

Cada teste diz a decisão e as palavras do Samuel. Aparência não conta: o que se mede aqui é
a ferramenta em que a tela está, o projeto (o que vai para o projeto.json), o Histórico, o
que a tela DESENHA (os pontos pintados pelo visualizador) e o PDF que o programa gera
(core.pipeline.processar, o mesmo do "Confirmar e processar"), medido: onde o impresso caiu
na página do PDF e de que tamanho ficou.

  Pedido da etapa 5 (sessão 1, 26/10, 1-7 e 1-9): "essa folha eu não precisava endireitar
      ela, eu precisava conseguir mover ela dentro da area branca e redimensionar." ·
      "mover deveria se poder fazer sem ter que ir em cortar bordas e poder ser feito como é
      no photoshope, que você arrasta a hora que quiser e aumenta a hora que quiser. a
      ferramenta de mover não deveria estar vinculada ao corte de bordas, deveriam ser duas
      coisas independentes" (D-008).
  Teste do Kaique (26/10, tarefa 5): "O texto dessa página está deslocado; quero mover ele
      para o meio da folha e aumentar um pouco." - não conseguiu: o "Mover conteúdo" não
      chegou ao PDF (margens 15 x 53), "o retângulo não passa da borda da folha e o texto
      não aumenta", e não há botão "centralizar".
  D-473: "Tela e PDF saem da mesma conta [...] Tela e PDF diferentes é defeito".
  D-017 (G10: "Avisar e não reduzir - avisar para eu reduzir manualmente"): aumentar além
      da beirada não corta nada escondido: a parte de fora aparece marcada e a página ganha
      aviso no "Para revisar".
  D-303: "precisamos centralizar".
  D-056 (g8-guias): "As duas" + "Mas ele vai poder tirar a automatica a hora que ele quiser."
  G10 + D-090/D-091: "ter uma opção para passar isso para todas as folhas"; as exceções vêm
      desmarcadas.
  D-004/D-009: a marca "mexida à mão" e o feito à mão vale no PDF com tudo desligado.

Páginas sintéticas de propósito (a medida é de lugar e de tamanho, no caminho inteiro do
processar): papel amarelado com um bloco de "texto" deslocado para a direita e para baixo,
como a página 7 do "La vida eterna" do teste do Kaique.
"""

from __future__ import annotations

import copy
import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QKeyEvent, QMouseEvent  # noqa: E402
from PySide6.QtWidgets import QApplication, QCheckBox, QPushButton  # noqa: E402

from core import analise, etapas  # noqa: E402
from core.pipeline import processar  # noqa: E402

DPI = 150
LARGURA, ALTURA = 600, 840          # 10,16 x 14,22 cm a 150 DPI
AMARELADO = (170, 215, 235)         # BGR: papel velho
# o "texto": linhas pretas num bloco deslocado para a direita e para baixo
TEXTO_X0, TEXTO_X1 = 200, 520       # margem esquerda 200, direita 80 (como o 15 x 53)
TEXTO_Y0, TEXTO_Y1 = 260, 760


# --- o livro e as medidas ---------------------------------------------------------

def _pagina() -> np.ndarray:
    img = np.full((ALTURA, LARGURA, 3), AMARELADO, np.uint8)
    for y in range(TEXTO_Y0, TEXTO_Y1, 30):
        img[y:y + 12, TEXTO_X0:TEXTO_X1] = 25
    return img


def _pdf(caminho: Path, paginas: int = 3) -> str:
    doc = fitz.open()
    for _ in range(paginas):
        ok, buffer = cv2.imencode(".png", _pagina())
        assert ok
        largura_pt, altura_pt = LARGURA / DPI * 72, ALTURA / DPI * 72
        pagina = doc.new_page(width=largura_pt, height=altura_pt)
        pagina.insert_image(fitz.Rect(0, 0, largura_pt, altura_pt), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _paginas_do_pdf(caminho: str) -> list[np.ndarray]:
    with fitz.open(caminho) as doc:
        saida = []
        for pagina in doc:
            pix = pagina.get_pixmap(dpi=DPI, colorspace=fitz.csRGB)
            saida.append(np.frombuffer(pix.samples, np.uint8).reshape(
                pix.height, pix.width, pix.n)[..., :3].copy())
        return saida


def _gerar(janela, tmp_path: Path, nome: str) -> list[np.ndarray]:
    """O PDF do livro aberto, como o "Confirmar e processar" grava."""
    projeto = copy.copy(janela.projeto)
    projeto.caminho_saida = str(tmp_path / f"{nome}.pdf")
    return _paginas_do_pdf(processar(projeto))


def _caixa_da_tinta(img: np.ndarray) -> tuple[float, float, float, float]:
    """(x0, y0, x1, y1) do preto da página do PDF, em fração dela."""
    cinza = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ys, xs = np.nonzero(cinza < 100)
    assert xs.size, "a página do PDF saiu sem texto"
    altura, largura = cinza.shape
    return (xs.min() / largura, ys.min() / altura, (xs.max() + 1) / largura,
            (ys.max() + 1) / altura)


def _assentar(vezes: int = 5) -> None:
    for _ in range(vezes):
        QApplication.processEvents()


def _esperar(condicao, limite: float = 15.0) -> bool:
    fim = time.perf_counter() + limite
    while time.perf_counter() < fim:
        QApplication.processEvents()
        if condicao():
            return True
        time.sleep(0.01)
    return condicao()


# --- a janela ---------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    import projetos

    projetos_dir = tmp_path / "projetos"
    projetos_dir.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: projetos_dir)
    return tmp_path


@pytest.fixture
def janela(app, pasta):
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    yield janela
    tarefa = getattr(janela.tela_conferir, "_tarefa_do_impresso", None)
    if tarefa is not None:
        tarefa.cancelar()
        tarefa.wait(5000)
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    if janela.previas is not None:
        janela.previas.parar()
    janela.close()


def _no_mover(janela, tmp_path: Path, pagina: int = 0):
    """Abre o livro SEM marcar nada (D-009) e escolhe a ferramenta Mover pela tecla F,
    como o Kaique. Espera a página chegar e a tela ser desenhada."""
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf"))
    janela.show()
    tela = janela.tela_conferir
    tela.ir_para_pagina(pagina)
    assert tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, Qt.Key_F, Qt.NoModifier, "f"))
    assert tela.aba_atual == "mover"
    vis = tela.visualizadores["mover"]
    assert _esperar(lambda: vis._pixmap is not None and getattr(tela, "_mover_da_vez", None))
    vis.grab()                                            # desenha: a geometria da tela
    return tela, vis


def _evento(tipo, ponto, botao, botoes):
    return QMouseEvent(tipo, QPointF(ponto), QPointF(ponto), botao, botoes, Qt.NoModifier)


def _arrastar(vis, de: QPoint, ate: QPoint) -> None:
    """Arrasta com o mouse no visualizador (apertar, mover em passos, soltar)."""
    vis.mousePressEvent(_evento(QEvent.MouseButtonPress, de, Qt.LeftButton, Qt.LeftButton))
    for i in range(1, 6):
        meio = QPoint(de.x() + (ate.x() - de.x()) * i // 5, de.y() + (ate.y() - de.y()) * i // 5)
        vis.mouseMoveEvent(_evento(QEvent.MouseMove, meio, Qt.NoButton, Qt.LeftButton))
    vis.mouseReleaseEvent(_evento(QEvent.MouseButtonRelease, ate, Qt.LeftButton, Qt.NoButton))
    _assentar()
    vis.grab()


def _impresso_na_tela(vis) -> tuple[float, float, float, float]:
    """Onde a TELA diz que o impresso está, em fração da área branca (x0, y0, x1, y1):
    o retângulo do conteúdo e a caixa do impresso que o visualizador usa."""
    x, y, w, h = vis._retangulo_conteudo
    c0, d0, c1, d1 = vis._caixa_do_impresso
    return (x + c0 * w, y + d0 * h, x + c1 * w, y + d1 * h)


# --- D-008: a ferramenta própria, sempre à mão -----------------------------------------

def test_d008_ferramenta_mover_propria_na_trilha_no_menu_e_na_letra(janela, tmp_path):
    """D-008 ("a ferramenta de mover não deveria estar vinculada ao corte de bordas,
    deveriam ser duas coisas independentes"). Livro aberto sem nada marcado: a ferramenta
    está na trilha (com o nome e a letra no balão), no menu Ferramentas e na tecla F; o
    painel Propriedades abre com os botões dela. E o antigo saiu: nas Bordas não há mais
    "Mover conteúdo" (nem "(só depois de escolher um tamanho de folha)")."""
    from ui.widgets.trilha_agrupada import FERRAMENTA_MOVER, GRUPOS, NOMES, tecla_de

    tela, _vis = _no_mover(janela, tmp_path)
    assert (FERRAMENTA_MOVER,) in GRUPOS
    assert NOMES[FERRAMENTA_MOVER] == "Mover e redimensionar"
    assert tecla_de(FERRAMENTA_MOVER) == "F"
    assert janela.menu.acoes["usar_mover"].text().endswith("	F")
    assert tela.paineis.aberto == "props"
    assert tela.paineis.propriedades.conteudo == "mover"
    botoes = {b.text() for b in tela.propriedades_das_abas["mover"].findChildren(QPushButton)}
    assert {"Centralizar", "voltar como veio", "usar em todas...", "tamanho da folha..."} <= botoes
    # o menu Ferramentas leva para ela também
    tela.escolher_ferramenta("retangulo")
    assert tela.aba_atual == "marcar"
    janela.menu.acoes["usar_mover"].trigger()
    assert tela.aba_atual == "mover"
    # o antigo saiu das Bordas
    assert not hasattr(tela, "botao_mover_conteudo")
    caixinhas = [c.text() for c in tela.propriedades_das_abas["bordas"].findChildren(QCheckBox)]
    assert "Mover conteúdo" not in caixinhas
    assert tela.visualizadores["bordas"].receivers("2conteudo_movido(QVariant)") == 0 \
        if hasattr(tela.visualizadores["bordas"], "receivers") else True


def test_d008_sem_tamanho_de_folha_a_area_branca_e_a_propria_pagina(janela, tmp_path):
    """D-008: sem escolher tamanho de folha a ferramenta funciona (antes ficava cinza até
    escolher um): a área branca é a própria página, e o painel diz isso."""
    tela, vis = _no_mover(janela, tmp_path)
    pagina = janela.projeto.paginas[0]
    assert pagina.tamanho_folha_cm is None
    assert vis._folha_do_mover == vis.tamanho_da_pagina_px()
    assert vis._retangulo_conteudo == pytest.approx((0.0, 0.0, 1.0, 1.0))
    assert tela.rotulo_area_branca.text().startswith("A própria página")


# --- D-008 + teste do Kaique: arrastar e aumentar chegam ao PDF -------------------------

def test_d008_arrastar_com_o_mouse_sai_no_pdf_no_mesmo_lugar_da_tela(janela, tmp_path):
    """D-008 ("você arrasta a hora que quiser") e D-473 (tela = PDF). Arrastar a página
    com o mouse para a esquerda e para cima, sem tamanho de folha: o impresso anda no PDF
    exatamente o que andou na tela (medido em fração da página, até 1%), a página do PDF
    fica do mesmo tamanho, a página ganha a marca "mexida à mão" e é UMA ação do desfazer."""
    tela, vis = _no_mover(janela, tmp_path)
    antes_pdf = _gerar(janela, tmp_path, "antes")[0]
    feitas = len(janela.acoes.feitas)
    centro = vis._area.center()
    _arrastar(vis, centro, QPoint(centro.x() - int(vis._area.width() * 0.12),
                                  centro.y() - int(vis._area.height() * 0.08)))
    pagina = janela.projeto.paginas[0]
    assert pagina.conteudo_deslocamento[0] < -0.08 and pagina.conteudo_deslocamento[1] < -0.04
    assert etapas.MOVER in pagina.mexida_a_mao
    assert len(janela.acoes.feitas) == feitas + 1
    tela_diz = _impresso_na_tela(vis)

    depois_pdf = _gerar(janela, tmp_path, "depois")[0]
    assert depois_pdf.shape == antes_pdf.shape
    pdf_diz = _caixa_da_tinta(depois_pdf)
    assert pdf_diz == pytest.approx(tela_diz, abs=0.01), (pdf_diz, tela_diz)
    assert pdf_diz[0] < _caixa_da_tinta(antes_pdf)[0] - 0.08

    tela.desfazer()                                       # Ctrl+Z volta como veio
    assert tuple(janela.projeto.paginas[0].conteudo_deslocamento) == (0.0, 0.0)


def test_d008_puxar_o_canto_aumenta_o_texto_no_pdf(janela, tmp_path):
    """D-008 ("aumenta a hora que quiser") e o teste do Kaique ("o texto não aumenta").
    Puxar o canto de baixo à direita para fora: o conteúdo aumenta além da página (antes
    parava na beirada) e o texto sai maior no PDF, na proporção que a tela mostra."""
    tela, vis = _no_mover(janela, tmp_path)
    antes = _caixa_da_tinta(_gerar(janela, tmp_path, "antes")[0])
    canto = vis._alcas(vis._area_do_conteudo())["se"]
    _arrastar(vis, canto, QPoint(canto.x() + int(vis._area.width() * 0.06),
                                 canto.y() + int(vis._area.height() * 0.06)))
    escala = janela.projeto.paginas[0].conteudo_escala
    assert escala > 1.08, "o texto não aumentou (o antigo parava na beirada)"
    depois = _caixa_da_tinta(_gerar(janela, tmp_path, "depois")[0])
    largura_antes, largura_depois = antes[2] - antes[0], depois[2] - depois[0]
    assert largura_depois / largura_antes == pytest.approx(escala, rel=0.02)
    assert depois == pytest.approx(_impresso_na_tela(vis), abs=0.01)


def test_kaique_folha_do_tamanho_do_corte_arrastar_chega_ao_pdf(janela, tmp_path):
    """O caso exato do teste do Kaique (26/10/2026, tarefa 5): corte à mão, depois a
    folha escolhida do tamanho do corte (a janela "tamanho..." arredonda), e o texto
    arrastado. No programa de antes, com a folha do tamanho do corte, o conteúdo ficava
    preso (não havia folga) e o PDF saía como antes (margens 15 x 53). Agora o arrasto
    chega ao PDF, no lugar que a tela mostra."""
    tela, vis = _no_mover(janela, tmp_path)
    tela.escolher_ferramenta("cortar")
    tela._mover_recorte((0.04, 0.04, 0.92, 0.92))
    largura_cm = round(LARGURA * 0.92 / DPI * 2.54, 2)
    altura_cm = round(ALTURA * 0.92 / DPI * 2.54, 2)
    tela._mudar_tamanho_da_folha((largura_cm, altura_cm))
    tela.escolher_ferramenta("mover")
    assert _esperar(lambda: vis._pixmap is not None)
    vis.grab()
    antes = _caixa_da_tinta(_gerar(janela, tmp_path, "antes")[0])
    centro = vis._area.center()
    _arrastar(vis, centro, QPoint(centro.x() - int(vis._area.width() * 0.10), centro.y()))
    depois = _caixa_da_tinta(_gerar(janela, tmp_path, "depois")[0])
    assert depois[0] < antes[0] - 0.07, "o mover não chegou ao PDF"
    assert depois == pytest.approx(_impresso_na_tela(vis), abs=0.012)


# --- D-303: Centralizar -------------------------------------------------------------------

def test_d303_centralizar_poe_o_impresso_no_meio_no_pdf(janela, tmp_path):
    """D-303 ("precisamos centralizar") e o teste do Kaique ("mover ele para o meio da
    folha"; no PDF as margens do texto ficaram 15 x 53). O texto está à direita e embaixo;
    "Centralizar" põe o IMPRESSO no meio da página nas duas direções: no PDF as margens da
    esquerda e da direita ficam iguais, e as de cima e de baixo também (até 1%)."""
    tela, _vis = _no_mover(janela, tmp_path)
    tela.botao_centralizar.click()
    x0, y0, x1, y1 = _caixa_da_tinta(_gerar(janela, tmp_path, "meio")[0])
    assert abs(x0 - (1 - x1)) <= 0.01, (x0, 1 - x1)
    assert abs(y0 - (1 - y1)) <= 0.01, (y0, 1 - y1)
    assert etapas.MOVER in janela.projeto.paginas[0].mexida_a_mao


def test_tamanho_em_porcento_e_voltar_como_veio(janela, tmp_path):
    """O número "Tamanho do conteúdo" aumenta em volta do meio (o lugar não muda) e
    "voltar como veio" desfaz o mover e o tamanho; o PDF volta a ser o de antes."""
    tela, _vis = _no_mover(janela, tmp_path)
    antes = _gerar(janela, tmp_path, "antes")[0]
    tela.campo_tamanho_do_conteudo.setValue(110)
    assert janela.projeto.paginas[0].conteudo_escala == pytest.approx(1.10)
    tela.botao_centralizar.click()
    botoes = {b.text(): b for b in tela.propriedades_das_abas["mover"].findChildren(QPushButton)}
    botoes["voltar como veio"].click()
    pagina = janela.projeto.paginas[0]
    assert pagina.conteudo_escala == 1.0 and tuple(pagina.conteudo_deslocamento) == (0.0, 0.0)
    assert np.array_equal(_gerar(janela, tmp_path, "como_veio")[0], antes)


# --- D-017: o que passa da beirada fica de fora, marcado e avisado ------------------------

def test_d017_aumentar_alem_da_beirada_avisa_e_marca_a_parte_de_fora(janela, tmp_path):
    """D-017 (G10: "Avisar e não reduzir - avisar para eu reduzir manualmente"): 160%
    numa página com o texto perto da beirada da direita. A página fica do mesmo tamanho
    no PDF, o programa NÃO diminui sozinho (a escala continua 160%), a página ganha o
    aviso "Parte do impresso fica de fora" no "Para revisar", a frase vermelha aparece no
    painel e a parte de fora aparece pintada de vermelho na tela."""
    tela, vis = _no_mover(janela, tmp_path)
    tamanho_antes = _gerar(janela, tmp_path, "antes")[0].shape
    tela.campo_tamanho_do_conteudo.setValue(160)
    _assentar()
    pagina = janela.projeto.paginas[0]
    assert pagina.conteudo_escala == pytest.approx(1.6)
    assert analise.IMPRESSO_DE_FORA in pagina.alertas_pendentes
    assert janela.tela_conferir.aviso_de_fora.isVisible()
    assert analise.descrever(analise.IMPRESSO_DE_FORA).titulo == "Parte do impresso fica de fora"
    # a tela mostra a parte de fora (fora da área branca, dentro da página aumentada)
    # puxada para o vermelho; a área branca não
    imagem = vis.grab().toImage()
    branca, conteudo = vis._area, vis._area_do_conteudo()

    def vermelho(x, y):
        cor = imagem.pixelColor(x, y)
        return cor.red() > cor.green() + 40 and cor.red() > cor.blue() + 40

    fora = [vermelho(x, y) for x in range(conteudo.left() + 1, conteudo.right())
            for y in range(conteudo.top() + 1, conteudo.bottom())
            if not branca.adjusted(-1, -1, 1, 1).contains(x, y)]
    dentro = [vermelho(x, y) for x in range(branca.left() + 2, branca.right() - 1)
              for y in range(branca.top() + 2, branca.bottom() - 1)]
    assert fora and sum(fora) / len(fora) > 0.5, "a parte de fora não aparece marcada"
    assert sum(dentro) / len(dentro) < 0.02, "a área branca ficou vermelha"
    # no PDF: do mesmo tamanho, e nada foi diminuído
    depois = _gerar(janela, tmp_path, "depois")[0]
    assert depois.shape == tamanho_antes
    assert janela.projeto.paginas[0].conteudo_escala == pytest.approx(1.6)
    # "ver no Mover" do aviso leva à ferramenta; diminuir tira o aviso
    tela.escolher_ferramenta("retangulo")
    tela._aplicar_correcao(analise.IMPRESSO_DE_FORA, "ver_no_mover")
    assert tela.aba_atual == "mover"
    tela.campo_tamanho_do_conteudo.setValue(100)
    _assentar()
    assert analise.IMPRESSO_DE_FORA not in janela.projeto.paginas[0].alertas


def test_d017_so_o_papel_da_margem_saindo_nao_avisa(janela, tmp_path):
    """D-017 fala do que está IMPRESSO: aumentar 105% numa página de margem larga tira
    só papel em branco da beirada - sem aviso."""
    tela, _vis = _no_mover(janela, tmp_path)
    tela.campo_tamanho_do_conteudo.setValue(105)
    _assentar()
    assert analise.IMPRESSO_DE_FORA not in janela.projeto.paginas[0].alertas


def test_d017_o_pdf_tambem_poe_o_aviso(tmp_path):
    """D-473/D-017: o PDF faz a mesma conta e põe o aviso (a página mexida que ninguém
    abriu na ferramenta Mover também fica marcada para revisar)."""
    from modelos import ConfigFolha, ConfigPagina, Projeto

    entrada = _pdf(tmp_path / "livro.pdf", paginas=1)
    projeto = Projeto(caminho_entrada=entrada, caminho_saida=str(tmp_path / "saida.pdf"),
                      nome="x")
    projeto.dividir_folhas = projeto.cortar_bordas = projeto.endireitar = False
    projeto.limpar = projeto.detectar_regioes = False
    projeto.folhas = [ConfigFolha(indice=0)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0, conteudo_escala=2.0)]
    processar(projeto)
    assert analise.IMPRESSO_DE_FORA in projeto.paginas[0].alertas


# --- D-056 (g8-guias): as linhas de apoio na ferramenta Mover -----------------------------

def test_d056_linhas_de_apoio_na_ferramenta_mover_sem_tamanho_de_folha(janela, tmp_path):
    """D-056 (`g8-guias`: "As duas" + "Mas ele vai poder tirar a automatica a hora que ele
    quiser.") e D-025 ("a Etapa 5 leva as guias à ferramenta Mover"). Na ferramenta Mover,
    sem tamanho de folha: pôr uma linha pelo botão direito grava no livro (antes, sem folha,
    nada acontecia), ela aparece na página, e o ímã do meio gruda pelo IMPRESSO; a caixinha
    desliga as automáticas para o livro todo."""
    from core import guias

    tela, vis = _no_mover(janela, tmp_path)
    assert tela.paineis.propriedades.isAncestorOf(tela.botao_linhas_automaticas) or \
        tela.propriedades_das_abas["mover"].isAncestorOf(tela.botao_linhas_automaticas)
    vis.guias_mudaram.emit([(guias.DE_PE, 0.25)])
    _assentar()
    assert len(janela.projeto.guias) == 1
    assert vis.guias_do_livro and vis.guias_do_livro[0][1] == pytest.approx(0.25, abs=1e-3)
    # o ímã: arrastar quase até o meio gruda o meio do IMPRESSO no meio da página
    impresso = _impresso_na_tela(vis)
    falta = 0.5 - (impresso[0] + impresso[2]) / 2
    centro = vis._area.center()
    _arrastar(vis, centro, QPoint(centro.x() + round((falta + 0.004) * vis._area.width()),
                                  centro.y()))
    impresso = _impresso_na_tela(vis)
    assert (impresso[0] + impresso[2]) / 2 == pytest.approx(0.5, abs=0.002)
    # desligar as automáticas: vale no livro, e o Ctrl+Z desfaz
    tela.botao_linhas_automaticas.click()
    assert janela.projeto.guias_automaticas is False
    assert vis.guias_automaticas is False


# --- G10 + D-090: usar em todas, com as exceções desmarcadas, e a conferência por trás ----

def test_g10_usar_em_todas_nas_escolhidas_e_avisa_por_tras(janela, tmp_path, monkeypatch):
    """G10 ("ter uma opção para passar isso para todas as folhas"), D-090 ("usar em todas"
    nunca apaga exceção) e D-017. A página 3 já tem o seu tamanho; "usar em todas..." abre
    a lista com ela desmarcada; com a escolha de fábrica, as páginas 1 e 2 ficam com 170%
    numa ação do desfazer, a 3 fica com o dela; e a conferência por trás põe o aviso nas
    que ficaram com parte do impresso de fora (sem abrir cada uma)."""
    from ui import dialogo_escolher_paginas as dep

    tela, _vis = _no_mover(janela, tmp_path)
    projeto = janela.projeto
    tela.ir_para_pagina(2)
    tela.campo_tamanho_do_conteudo.setValue(90)
    tela.ir_para_pagina(0)
    _esperar(lambda: tela._mover_da_vez is not None)
    tela.campo_tamanho_do_conteudo.setValue(170)
    de_fabrica = dep.paginas_de_fabrica(projeto, 0, etapas.conteudo_fora_do_padrao)
    assert de_fabrica == [0, 1], "a página com tamanho próprio veio marcada"
    monkeypatch.setattr(type(tela), "_escolher_paginas_do_mover", lambda self: de_fabrica)
    projeto.paginas[1].alertas = []
    feitas = len(janela.acoes.feitas)
    botoes = {b.text(): b for b in tela.propriedades_das_abas["mover"].findChildren(QPushButton)}
    botoes["usar em todas..."].click()
    assert [p.conteudo_escala for p in projeto.paginas] == pytest.approx([1.7, 1.7, 0.9])
    assert len(janela.acoes.feitas) == feitas + 1
    assert _esperar(lambda: analise.IMPRESSO_DE_FORA in projeto.paginas[1].alertas, 30)
    assert etapas.MOVER in projeto.paginas[1].mexida_a_mao
