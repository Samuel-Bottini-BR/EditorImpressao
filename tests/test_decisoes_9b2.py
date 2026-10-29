"""As provas de comportamento da etapa 9b-2 da obra de 26/10/2026: a área de trabalho
(CLAUDE.md §11, regra 4; Livro de decisões, docs/plano/DECISOES.md).

Cada teste diz a decisão e as palavras do Samuel. Aparência não conta: o que se mede é o projeto
gravado, a imagem que sai (no PDF ou na tela), a página da vez e o desfazer. Os que provam um
conserto de defeito (CLAUDE.md §4.7) falham no código antigo (`obra-2026-10-26` = 27b4c52): o
resultado está em relatorios/obra-etapa9b2/reversao-no-codigo-antigo.txt.

  D-558 (27/10, `ac-grade-inserir`): "quando falei dividir é dividir a pagina, usando a
      funcionalidade do scantailor que colocamos no aplicativo, é isso que deveria ser feito."
  D-559 (27/10, `ac-tampa`): "Como eu decidi: sumir em todo o livro, e o Kaique escolhe por livro
      cortar ou pintar de branco" (D-097 "É para sumir totalmente."; D-092 "O Kaique escolhe por
      livro").
  D-547 / D-473 / D-066 / D-064: a tela mostra a página como sai no PDF ("precisamos que o pdf saia
      que nem está na tela"; "é só colocar uma bolinha de carregamento, pode ter uma pro livro
      inteiro e outra para a pagina que estamos").
  D-568 (`v-roda`): "sem zoom troca de página; Ctrl + roda dá zoom" + com zoom anda pela página.
  D-570 (`v-zoom-pares`): "Sim, zoom também no lado a lado".  D-571 (`v-100`): "A página inteira
      cabendo na tela".
  D-554 (`ac-margens-iguais`): "Também na tela do corte".
  D-563 (`ac-desentortar-texto`): "Tirar, voltar como era antes".  D-564 (`ac-gravura-cinza`):
      "Não fazer: gravura continua em preto e branco".
  D-020: "Ctrl+Z desfaz qualquer alteração" (lista única 1.3, 1.6, 1.7, 1.9, 4.6; promessa P-129).
  D-090 / D-091 (P-061): "usar em todas" com as exceções desmarcadas, que nunca apaga exceção.
"""

from __future__ import annotations

import copy
import inspect
import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402

DPI = 100
AMARELADO = (170, 215, 235)            # BGR: papel velho


# --- os livros de teste -----------------------------------------------------------

def _pagina(largura: int = 600, altura: int = 840, marca: int = 0) -> np.ndarray:
    """Papel amarelado com margem larga, linhas de "texto" pretas e, no alto, `marca`
    quadradinhos (para saber qual página é qual)."""
    img = np.full((altura, largura, 3), AMARELADO, np.uint8)
    for y in range(140, altura - 160, 40):
        img[y:y + 12, 110:largura - 110] = 25
    for k in range(marca % 12):
        img[60:80, 110 + k * 24:126 + k * 24] = 0
    return img


def _aberto(marca: int = 0) -> np.ndarray:
    """Um livro aberto: duas páginas lado a lado (a dobra no meio)."""
    return np.concatenate([_pagina(marca=2 * marca), _pagina(marca=2 * marca + 1)], axis=1)


def _pdf(caminho: Path, imagens) -> str:
    doc = fitz.open()
    for img in imagens:
        ok, buffer = cv2.imencode(".png", img)
        assert ok
        largura, altura = img.shape[1] / DPI * 72, img.shape[0] / DPI * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
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
    """O PDF do livro aberto, como o "Confirmar e processar" grava: as páginas desenhadas."""
    from core.pipeline import processar

    projeto = copy.copy(janela.projeto)
    projeto.caminho_saida = str(tmp_path / f"{nome}.pdf")
    return _paginas_do_pdf(processar(projeto))


# --- a janela ---------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    import projetos

    projetos_dir = tmp_path / "projetos"
    projetos_dir.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: projetos_dir)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "dados"))
    return tmp_path


@pytest.fixture
def janela(app, pasta):
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    yield janela
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    if janela.previas is not None:
        janela.previas.parar()
    janela.close()


def _assentar(vezes: int = 6) -> None:
    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        QApplication.processEvents()


def _esperar(condicao, segundos: float = 40.0, motivo: str = "") -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar(2)
        if condicao():
            return
        time.sleep(0.02)
    raise AssertionError(f"não aconteceu a tempo: {motivo}")


# --- D-563 e D-564: as contas que ele mandou tirar saíram -----------------------------------

def test_d563_a_conta_desentortar_so_o_bloco_do_texto_saiu():
    """D-563 (27/10/2026, Central `ac-desentortar-texto`: "Tirar, voltar como era antes
    (recomendo)"). A conta "desentortar seguindo só o bloco do texto" (D-493/D-530, etapa 10b,
    pronta e não ligada) saiu: a caixa do conteúdo do desentortar não tem mais o jeito "só o
    bloco" nem a conta das notas da margem. Falha no código antigo (a conta estava lá)."""
    from core import desentortar_scantailor as ds

    assert "so_o_bloco" not in inspect.signature(ds.caixa_do_conteudo).parameters
    assert not hasattr(ds, "_so_o_bloco_do_texto")
    assert not hasattr(ds, "BLOCO_PERCENTIL")


def test_d563_a_caixa_do_conteudo_continua_a_de_sempre():
    """D-563 ("voltar como era antes"): a caixa do conteúdo que vai ao desentortar é a de
    sempre, com o texto e as notas da margem dentro (nada ficou de fora)."""
    from core import desentortar_scantailor as ds

    img = np.full((1400, 1200, 3), 225, np.uint8)
    for y in range(160, 1260, 36):
        for x in range(260, 940, 22):
            img[y:y + 16, x:x + 14] = 30
    for y in (300, 336, 900):                           # notas da esquerda
        img[y:y + 12, 120:200] = 40
    x, _y, largura, _a = ds.caixa_do_conteudo(img, (0, 0, 1200, 1400), 300)
    assert x <= 125 and x + largura >= 930


def test_d564_a_chave_da_gravura_escura_em_cinza_saiu():
    """D-564 (27/10/2026, Central `ac-gravura-cinza`: "Não fazer: gravura continua em preto e
    branco (recomendo)"). A chave `GRAVURA_ESCURA_EM_CINZA` (D-532, etapa 9d, desligada) e a
    conta dela saíram. Falha no código antigo. A prova de que a gravura de fundo escuro do
    Palatino 74 sai em 1 bit pelo caminho inteiro é
    tests/test_decisoes_nucleo2.py::test_d564_palatino_74_continua_em_1_bit."""
    from core import filtros

    assert not hasattr(filtros, "GRAVURA_ESCURA_EM_CINZA")
    assert not hasattr(filtros, "_e_gravura_escura_ou_reticula")


# --- D-554: "Margens iguais" também na tela do Cortar ----------------------------------------

def test_d554_margens_iguais_na_tela_do_cortar_e_o_mesmo_valor_do_automatico(janela, tmp_path):
    """D-554 (27/10/2026, Central `ac-margens-iguais`: "Também na tela do corte"; confirma a
    D-494; D-075: "Mas eu vou conseguir alterar isso né?"). Na ferramenta Cortar há a caixinha
    "Margens iguais", desmarcada de fábrica; marcar liga as margens iguais DO LIVRO (o mesmo
    valor da etapa do Automático, que passa a mostrá-la marcada), numa ação do desfazer; o PDF
    sai com todas as páginas do mesmo tamanho. Falha no código antigo (não havia a caixinha)."""
    from ui.widgets.trilha_agrupada import FERRAMENTA_CORTAR

    imagens = [_pagina(600, 840), _pagina(520, 760), _pagina(640, 800)]
    janela.abrir_livro(_pdf(tmp_path / "tamanhos.pdf", imagens))
    tela = janela.tela_conferir
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    _assentar()
    caixa = tela.caixa_margens_iguais
    assert caixa.text() == "Margens iguais" and not caixa.isHidden()
    assert caixa.isChecked() is False and janela.projeto.margens_iguais is False

    caixa.click()
    _assentar()
    assert janela.projeto.margens_iguais is True
    assert A.MARGENS in tela.paineis.automatico.estado.marcadas      # o Automático mostra
    assert "Margens iguais" in janela.acoes.feitas[-1].descricao

    tela.desfazer()
    _assentar()
    assert janela.projeto.margens_iguais is False and not caixa.isChecked()
    tela.refazer()
    _assentar()
    assert janela.projeto.margens_iguais is True and caixa.isChecked()

    paginas = _gerar(janela, tmp_path, "margens")
    tamanhos = {p.shape[:2] for p in paginas}
    assert len(paginas) == 3 and len(tamanhos) == 1, tamanhos


# --- D-568, D-570, D-571: a roda e o zoom --------------------------------------------------

def _dividido(janela, tmp_path: Path, folhas: int = 5):
    """O caminho do Kaique: abrir o livro aberto e rodar o Automático só com "Dividir"."""
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", [_aberto(f) for f in range(folhas)]))
    estado = janela.estado_do_automatico
    estado.marcadas = {A.DIVIDIR}
    estado.alcance = "livro"
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    assert len(janela.projeto.paginas) == 2 * folhas
    return janela.tela_conferir


def _roda(vista, passos: int, ctrl: bool = False, shift: bool = False) -> None:
    """Uma volta da roda do mouse em cima da página (como o Windows manda)."""
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtGui import QWheelEvent
    from PySide6.QtWidgets import QApplication

    teclas = Qt.NoModifier
    if ctrl:
        teclas |= Qt.ControlModifier
    if shift:
        teclas |= Qt.ShiftModifier
    centro = QPointF(vista.width() / 2, vista.height() / 2)
    evento = QWheelEvent(centro, vista.mapToGlobal(centro), QPoint(0, 0), QPoint(0, 120 * passos),
                         Qt.NoButton, teclas, Qt.NoScrollPhase, False)
    QApplication.sendEvent(vista, evento)


@pytest.mark.parametrize("ferramenta", ["mao", "endireitar"])
def test_d568_com_zoom_a_roda_anda_pela_pagina(janela, tmp_path, ferramenta):
    """D-568 (27/10/2026, Central `v-roda`: "Como ficou: sem zoom troca de página; Ctrl + roda
    dá zoom"; com zoom anda pela página). Com zoom, a roda para baixo mostra a parte de baixo
    da página (o deslocamento sobe), não troca de página e não muda o zoom; para cima volta;
    a página não sai da tela (para na beirada). Na Mão (o editor de marcar) e numa ferramenta
    de página (Endireitar). Falha no código antigo (com zoom a roda dava zoom)."""
    tela = _dividido(janela, tmp_path)
    tela.escolher_ferramenta(ferramenta)
    tela.ir_para_pagina(4)
    janela.show()
    janela.move(-3000, -3000)
    _assentar()
    vista = tela.editor_selecao if ferramenta == "mao" else tela.visualizadores["angulo"]
    _esperar(lambda: getattr(vista, "_pixmap", None) is not None, motivo="a prévia")
    tela.mudar_o_zoom(2.0)
    zoom = vista.zoom
    assert zoom > 1.9
    antes = vista.deslocamento.y()
    _roda(vista, -1)
    assert tela.indice_pagina == 4 and vista.zoom == zoom
    assert vista.deslocamento.y() < antes                 # andou para baixo na página
    for _ in range(60):                                   # muito: para na beirada
        _roda(vista, -1)
    fundo = vista.deslocamento.y()
    _roda(vista, -1)
    assert vista.deslocamento.y() == fundo and tela.indice_pagina == 4
    _roda(vista, 1)
    assert vista.deslocamento.y() > fundo                 # volta para cima
    _roda(vista, 1, ctrl=True)                            # Ctrl+roda: zoom
    assert vista.zoom > zoom
    tela.mudar_o_zoom(2.0)                                # bem perto: a página passa dos lados
    de_lado = vista.deslocamento.x()
    _roda(vista, -1, shift=True)                          # Shift: para os lados
    assert vista.deslocamento.x() < de_lado and tela.indice_pagina == 4
    tela.mudar_o_zoom(None)                               # sem zoom: troca de página
    _roda(vista, -1)
    assert tela.indice_pagina == 5


def test_d570_zoom_tambem_no_lado_a_lado(janela, tmp_path):
    """D-570 (27/10/2026, Central `v-zoom-pares`: "Sim, zoom também no lado a lado"). No "Duas
    lado a lado" o "+" da barra de baixo aumenta as páginas dos pares (a altura de cada página
    na tela cresce na mesma conta), o número mostra o zoom, Ctrl+roda também dá zoom, e
    "ajustar à tela" volta o par inteiro à tela (100%). A página da vez continua a mesma.
    Falha no código antigo (no lado a lado os botões do zoom ficavam apagados e nada mudava)."""
    from ui.widgets.paginas_rolando import DUAS

    tela = _dividido(janela, tmp_path)
    tela.ir_para_pagina(4)
    tela.definir_mostrar(DUAS)
    _assentar()
    pares = tela.lado_a_lado
    assert tela.botao_mais_zoom.isEnabled() and tela.rotulo_do_zoom.text() == "100%"
    alturas = dict(pares.altura_das_paginas())
    tela.botao_mais_zoom.click()
    _assentar()
    assert tela.rotulo_do_zoom.text() == "125%" and abs(pares.zoom - 1.25) < 1e-6
    depois = dict(pares.altura_das_paginas())
    assert all(abs(depois[i] - 1.25 * alturas[i]) < 2 for i in alturas)
    assert tela.indice_pagina == 4
    _roda(pares.viewport(), 1, ctrl=True)
    _assentar()
    assert pares.zoom > 1.5 and tela.rotulo_do_zoom.text() == f"{round(pares.zoom * 100)}%"
    tela.botao_ajustar_a_tela.click()
    _assentar()
    assert pares.zoom == 1.0 and tela.rotulo_do_zoom.text() == "100%"
    assert dict(pares.altura_das_paginas()) == alturas


def test_d571_100_por_cento_e_a_pagina_inteira_cabendo_na_tela(janela, tmp_path):
    """D-571 (27/10/2026, Central `v-100`: "A página inteira cabendo na tela (recomendo)"). A
    conferir: com "100%" na barra de baixo, a página desenhada cabe inteira na área da página
    (e encosta nela na largura ou na altura: não é menor que a tela); "ajustar à tela" leva a
    100%. Vale na Mão e numa ferramenta de página."""
    tela = _dividido(janela, tmp_path)
    tela.escolher_ferramenta("endireitar")
    janela.show()
    janela.move(-3000, -3000)
    _assentar()
    vista = tela.visualizadores["angulo"]
    _esperar(lambda: getattr(vista, "_pixmap", None) is not None, motivo="a prévia")
    tela.mudar_o_zoom(1.6)
    tela.botao_ajustar_a_tela.click()
    _assentar()
    vista.repaint()
    assert tela.rotulo_do_zoom.text() == "100%"
    from ui.widgets.visualizador import PADDING_MOLDURA

    area = vista._area
    assert area.left() >= 0 and area.top() >= 0
    assert area.right() <= vista.width() and area.bottom() <= vista.height()
    folga = 2 * PADDING_MOLDURA + 2                       # a moldura em volta da página
    assert (area.width() >= vista.width() - folga) or (area.height() >= vista.height() - folga)


# --- D-558: "dividir" na grade "Todas as páginas" --------------------------------------------

def test_d558_dividir_na_grade_nas_folhas_escolhidas_com_a_conta_do_dividir_esta(janela, tmp_path):
    """D-558 (27/10/2026, Central `ac-grade-inserir`: "quando falei dividir é dividir a pagina,
    usando a funcionalidade do scantailor que colocamos no aplicativo, é isso que deveria ser
    feito."; D-334). Livro aberto de 4 folhas, sem "Dividir": na grade "Todas as páginas",
    escolher as folhas 2 e 3 e clicar "dividir" → por trás, com andamento, as duas viram duas
    páginas cada, na lombada (a mesma conta do "dividir esta", o jeito do ScanTailor de
    fábrica); as outras ficam inteiras; numa ação só do desfazer (o Ctrl+Z junta as duas de
    novo); o PDF sai com 6 páginas, as divididas com metade da largura. Falha no código antigo
    (não havia o "dividir" na grade)."""
    from core import dividir_a_mao

    folha_aberta = np.concatenate([_pagina(), _pagina()], axis=1)
    janela.abrir_livro(_pdf(tmp_path / "aberto.pdf", [folha_aberta] * 4))
    tela = janela.tela_conferir
    assert len(janela.projeto.paginas) == 4
    medidas = []
    original = dividir_a_mao.medir_para_dividir

    def contar(projeto, folha, jeito):
        lombada, tampa = original(projeto, folha, jeito)
        medidas.append((folha, jeito, lombada.posicao))
        return lombada, tampa

    dividir_a_mao.medir_para_dividir = contar
    try:
        tela.abrir_todas_as_paginas()
        tela.todas.comecar_a_escolher([1, 2])
        _assentar()
        botao = tela.todas.botoes_da_escolha["dividir"]
        assert botao.isEnabled() and botao.text() == "dividir"
        historico = len(janela.acoes.feitas)
        botao.click()
        assert getattr(tela, "_tarefa_de_dividir", None) is not None       # por trás
        _esperar(lambda: len(janela.projeto.paginas) == 6, motivo="dividir as escolhidas")
    finally:
        dividir_a_mao.medir_para_dividir = original
    projeto = janela.projeto
    assert sorted(f for f, _j, _p in medidas) == [1, 2]
    assert all(j == "scantailor" for _f, j, _p in medidas)                 # o do ScanTailor
    assert [f.dividir for f in projeto.folhas] == [False, True, True, False]
    for f, _j, posicao in medidas:                                       # a linha medida
        assert projeto.folhas[f].posicao_corte == round(posicao, 4)
        assert abs(posicao - 0.5) < 0.05                                 # na lombada
        assert "dividir" in projeto.folhas[f].mexida_a_mao
    assert len(janela.acoes.feitas) == historico + 1                     # uma ação só
    paginas = _gerar(janela, tmp_path, "dividido")
    larguras = [p.shape[1] for p in paginas]
    assert len(paginas) == 6
    assert abs(larguras[1] - larguras[0] / 2) < larguras[0] * 0.08
    tela.desfazer()
    _assentar()
    assert len(projeto.paginas) == 4 and not any(f.dividir for f in projeto.folhas)


# --- D-559: a faixa da tampa do scanner some em todo o livro, também no Automático ----------

def _righetti_sintetico() -> np.ndarray:
    """A folha do Righetti como ela fica depois de girada (medida no livro de verdade, folha 96
    a 150 DPI; a mesma de tests/test_decisoes_dividir.py): uma tira clara da tampa em cima, a
    faixa preta de ~2 cm atravessando a folha, o fundo preto do scanner à esquerda e o livro
    aberto."""
    altura, largura = 1275, 1650
    img = np.full((altura, largura, 3), 240, np.uint8)
    img[:, :270] = 12
    img[105:235, :] = 12
    img[:105, :] = 236
    for y in range(300, 1200, 24):
        img[y:y + 8, 330:900] = 30
        img[y:y + 8, 1010:1580] = 30
    return img


def _com_moldura_impressa() -> np.ndarray:
    """Livro aberto com moldura impressa PRETA e grossa (4,5 mm) em cada página: tem de sobrar
    inteira (D-495; a regra da tampa não pode pegá-la)."""
    altura, largura = 1275, 1650
    img = np.full((altura, largura, 3), 240, np.uint8)
    for x0, x1 in ((60, 780), (870, 1590)):
        cv2.rectangle(img, (x0, 60), (x1, altura - 60), (15, 15, 15), 27)
        for y in range(160, altura - 160, 24):
            img[y:y + 8, x0 + 80:x1 - 80] = 30
    return img


def _faixa_em_cima(img: np.ndarray, parte: float = 0.2, cheia: float = 0.9) -> int:
    """Quantas linhas, no alto da página, são pretas de ponta a ponta (a faixa da tampa)."""
    cinza = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    alto = cinza[: int(cinza.shape[0] * parte)]
    return int(((alto < 60).mean(axis=1) > cheia).sum())


def _rodar(janela, etapas_, alcance="livro", opcoes=None) -> bool:
    """O que o Kaique faz no painel Automático: marca as etapas e roda (no mesmo fio)."""
    estado = janela.estado_do_automatico
    estado.marcadas = set(etapas_)
    estado.opcoes.update(opcoes or {})
    estado.alcance = alcance
    return janela.rodar_o_automatico(esperar=True, perguntar=False)


def test_d559_a_tampa_some_em_todo_o_livro_pelo_automatico_e_o_livro_escolhe_cortar_ou_pintar(
        janela, tmp_path):
    """D-559 (27/10/2026, Central `ac-tampa`: "Como eu decidi: sumir em todo o livro, e o Kaique
    escolhe por livro cortar ou pintar de branco"; D-097: "É para sumir totalmente." / "tem que
    ficar rente a folha de papel, não pode ter preto ali."; D-092: "O Kaique escolhe por
    livro"). Substitui a D-495/D-499 (só ao dividir à mão). Livro de 3 folhas como o Righetti
    (já de pé), o Automático só com "Endireitar" (nenhum dividir à mão): a tampa é achada nas
    três; no PDF nenhuma página tem a faixa preta em cima. Com o livro em "cortar fora" (o de
    fábrica) a página fica mais baixa que a folha (cortada na beirada da tampa); em "pintar de
    branco", do tamanho da folha, com o lugar da faixa branco. O Ctrl+Z do Automático devolve a
    folha sem a tampa. Falha no código antigo (o Automático nunca tirava a tampa)."""
    janela.abrir_livro(_pdf(tmp_path / "tampa.pdf", [_righetti_sintetico()] * 3))
    projeto = janela.projeto
    assert projeto.borda_preta_fazer == "cortar"                       # de fábrica
    _rodar(janela, [A.ENDIREITAR])
    assert all(f.tampa_do_scanner and len(f.tampa_do_scanner) == 5 for f in projeto.folhas)
    cortadas = _gerar(janela, tmp_path, "cortar")
    assert len(cortadas) == 3
    assert all(_faixa_em_cima(p) == 0 for p in cortadas)
    folha_alta = 1275                                                  # a folha, no PDF a 100 DPI
    assert all(p.shape[0] < 0.88 * folha_alta for p in cortadas)       # cortada na tampa

    projeto.borda_preta_fazer = "pintar"
    pintadas = _gerar(janela, tmp_path, "pintar")
    assert all(_faixa_em_cima(p) == 0 for p in pintadas)
    assert all(p.shape[0] > 0.97 * folha_alta for p in pintadas)       # do tamanho da folha
    cinza = cv2.cvtColor(pintadas[0], cv2.COLOR_RGB2GRAY)
    faixa = cinza[int(0.10 * cinza.shape[0]): int(0.17 * cinza.shape[0]), int(0.3 * cinza.shape[1]):]
    assert float(faixa.mean()) > 200                                   # o lugar da faixa: branco

    janela.tela_conferir.desfazer()
    _assentar()
    assert all(f.tampa_do_scanner is None for f in projeto.folhas)


def test_d559_a_moldura_impressa_preta_nao_some_pelo_automatico(janela, tmp_path):
    """D-559 com o cuidado da D-495 ("livro com moldura impressa preta não perde a moldura"):
    o Automático procura a tampa no livro aberto com moldura preta grossa e não acha nada
    (tampa_do_scanner = [giro]: procurada, nada); a moldura sai inteira no PDF. A regra é a
    da etapa 4, passada nas 2.903 folhas do acervo sem pegar moldura nenhuma
    (relatorios/obra-etapa4/varrer-tampa-acervo.json)."""
    janela.abrir_livro(_pdf(tmp_path / "moldura.pdf", [_com_moldura_impressa()] * 2))
    projeto = janela.projeto
    _rodar(janela, [A.ENDIREITAR])
    assert all(f.tampa_do_scanner == [0] for f in projeto.folhas)
    paginas = _gerar(janela, tmp_path, "moldura")
    assert all(_faixa_em_cima(p, 0.12, 0.6) >= 10 for p in paginas)    # a linha de cima da moldura


def test_d559_a_escolha_cortar_ou_pintar_fica_a_vista_no_automatico(janela, tmp_path):
    """D-559 ("o Kaique escolhe por livro cortar ou pintar de branco") + D-092: a escolha "O que
    fica fora da página" (cortar fora / pintar de branco) do Automático vale também para a
    tampa e fica à vista com a borda preta desmarcada (antes só aparecia com ela marcada)."""
    janela.abrir_livro(_pdf(tmp_path / "tampa.pdf", [_righetti_sintetico()]))
    janela.estado_do_automatico.opcoes["borda_preta"] = False
    grande = janela.abrir_o_automatico(A.CORTAR)
    try:
        _assentar()
        assert not grande.linhas["borda_preta_fazer"].isHidden()
        assert grande.linhas["borda_preta_ate"].isHidden()                # o "até onde": só com ela
        assert "tampa do scanner" in grande.controles["borda_preta_fazer"].toolTip()
    finally:
        janela._fechar_a_janela_do_automatico()


# --- D-547 e a troca da 10b (D-473 / D-064): a tela como sai no PDF ---------------------------

def _caixa_da_tinta(img: np.ndarray, rgb: bool = True) -> tuple[float, float, float, float]:
    """(x0, y0, x1, y1) do preto da página, em fração dela."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_RGB2GRAY if rgb
                                                  else cv2.COLOR_BGR2GRAY)
    ys, xs = np.nonzero(cinza < 100)
    assert xs.size, "a página saiu sem texto"
    altura, largura = cinza.shape
    return (xs.min() / largura, ys.min() / altura, (xs.max() + 1) / largura,
            (ys.max() + 1) / altura)


def _perto(a, b, folga: float = 0.03) -> bool:
    return all(abs(x - y) <= folga for x, y in zip(a, b))


def test_d547_a_pagina_movida_aparece_como_sai_no_pdf_no_lado_a_lado_antes_depois_e_miniatura(
        janela, tmp_path):
    """D-547 (27/10/2026, escolha da gerente apoiada em D-473/D-066: "precisamos que o pdf saia
    que nem está na tela"; prova do Livro: "Mover uma página → a miniatura, a tela cheia e o
    lado a lado mostram igual ao PDF"). Página 2 com o conteúdo diminuído a 60% (ferramenta
    Mover): o lugar do texto (a caixa do preto) no lado a lado, no "antes / depois", na
    miniatura e nos cartões do painel Filtro é o mesmo do PDF (até 3% da página). Falha no
    código antigo (as outras telas mostravam a página sem o mover, D-546)."""
    from ui.widgets.paginas_rolando import DUAS

    janela.abrir_livro(_pdf(tmp_path / "mover.pdf", [_pagina(marca=k) for k in range(3)]))
    tela = janela.tela_conferir
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta("mover")
    _esperar(lambda: tela.previas.ja_pronta(1, tela._dpi_atual) is not None, motivo="a prévia")
    tela._mudar_tamanho_do_conteudo(60)
    _assentar()
    pdf = _gerar(janela, tmp_path, "movida")
    no_pdf = _caixa_da_tinta(pdf[1])
    assert no_pdf[2] - no_pdf[0] < 0.55                       # o texto diminuiu no PDF

    img, _chave = tela._previa_do_lado_a_lado(1, True)        # o lado a lado
    _esperar(lambda: tela._previa_do_lado_a_lado(1, True)[0] is not None, motivo="lado a lado")
    img, _chave = tela._previa_do_lado_a_lado(1, True)
    assert _perto(_caixa_da_tinta(img, rgb=False), no_pdf), (_caixa_da_tinta(img, False), no_pdf)

    tela.escolher_ferramenta("filtros")                       # os cartões do painel Filtro
    tela.definir_mostrar(DUAS)
    tela.definir_mostrar("uma")
    tela.botao_antes_depois.setChecked(True)                  # o "antes / depois"
    tela._alternar_antes_depois()
    _assentar()
    depois = tela._como_sai_no_pdf(tela.previas.ja_pronta(1, tela._dpi_atual), 1)
    assert _perto(_caixa_da_tinta(depois, rgb=False), no_pdf)

    tela._acertar_as_miniaturas_movidas()                    # a miniatura
    _chave, mini = tela.tira._como_sai[1]
    assert _perto(_caixa_da_tinta(mini, rgb=False), no_pdf, 0.05)
    assert 0 not in tela.tira._como_sai and 2 not in tela.tira._como_sai   # as outras: cruas


def test_d473_d064_a_tela_troca_pela_imagem_do_pdf_e_a_bolinha_da_pagina(janela, tmp_path,
                                                                      monkeypatch):
    """D-473 (escolha da gerente apoiada em D-066: "precisamos que o pdf saia que nem está na
    tela") + D-064 (22/10: "é só colocar uma bolinha de carregamento, pode ter uma pro livro
    inteiro e outra para a pagina que estamos"); a troca que a etapa 10b deixou para a tela
    (relatorios/obra-etapa10b/ONDE-PAREI.md). Na página em que a tela pede, por trás, o desenho
    do tamanho do PDF (a regra do "Para revisar" do "Só as letras"): enquanto ele não chega, a
    bolinha da página gira e diz "preparando a imagem igual ao PDF"; quando chega, a prévia da
    tela passa a ser a imagem do PDF REDUZIDA (a marca que só o desenho do PDF tem aparece na
    tela) e a bolinha para. Falha no código antigo (a imagem do PDF era jogada fora; não havia
    bolinha)."""
    import threading

    import ui.tarefas as T

    janela.abrir_livro(_pdf(tmp_path / "pdf.pdf", [_pagina(marca=k) for k in range(2)]))
    tela = janela.tela_conferir
    janela.show()                                  # as bolinhas só andam com a tela à vista
    janela.move(-3000, -3000)
    _esperar(lambda: tela.previas.ja_pronta(0, tela._dpi_atual) is not None, motivo="a prévia")
    solta = threading.Event()

    def acerto(doc, projeto, pagina, com_a_imagem=False):
        """O desenho do tamanho do PDF de mentira: a página com um quadrado preto no meio
        (a "diferença" que só o PDF tem); espera o teste soltar."""
        solta.wait(20)
        grande = np.full((int(840 * projeto.qualidade_dpi / DPI), int(600 * projeto.qualidade_dpi / DPI),
                          3), 255, np.uint8)
        h, w = grande.shape[:2]
        grande[h // 3: 2 * h // 3, w // 3: 2 * w // 3] = 0
        return (False, grande) if com_a_imagem else False

    monkeypatch.setattr(T, "acertar_no_tamanho_do_pdf", acerto)
    monkeypatch.setattr(T, "precisa_do_desenho_do_pdf", lambda projeto, pagina: True)
    assert tela.previas.pedir_medida(0)
    _esperar(lambda: tela.previas.medida_pendente(0), motivo="pedida")
    tela._acertar_as_bolinhas()
    assert tela.bolinha_da_pagina.carregando
    assert "igual ao PDF" in tela.bolinha_da_pagina.toolTip()
    solta.set()
    _esperar(lambda: tela.previas.igual_ao_pdf(0), motivo="a imagem do PDF na tela")
    previa = tela.previas.ja_pronta(0, tela._dpi_atual)
    h, w = previa.shape[:2]
    assert previa[h // 2, w // 2].max() < 30                   # o quadrado do "PDF" está na tela
    tela._acertar_as_bolinhas()
    assert not tela.bolinha_da_pagina.carregando


def test_d547_a_tela_cheia_dos_filtros_mostra_a_pagina_movida_como_no_pdf(janela, tmp_path):
    """D-547 (prova do Livro: "Mover uma página → [...] a tela cheia [...] mostra igual ao
    PDF"): a página grande da tela cheia dos filtros sai com o conteúdo no lugar e no tamanho do
    PDF (a caixa do preto até 3% da página). Falha no código antigo."""
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

    janela.abrir_livro(_pdf(tmp_path / "mover.pdf", [_pagina(marca=k) for k in range(2)]))
    tela = janela.tela_conferir
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta("mover")
    _esperar(lambda: tela.previas.ja_pronta(1, tela._dpi_atual) is not None, motivo="a prévia")
    tela._mudar_tamanho_do_conteudo(60)
    _assentar()
    no_pdf = _caixa_da_tinta(_gerar(janela, tmp_path, "movida")[1])
    vistas = []
    cheia = FiltrosEmTelaCheia(tela, parent=janela)
    original = cheia.vista.definir
    cheia.vista.definir = lambda antes, depois, *a, **k: (vistas.append(depois),
                                                          original(antes, depois, *a, **k))
    try:
        _esperar(lambda: (cheia.atualizar() or True) and any(v is not None for v in vistas),
                 motivo="a página grande da tela cheia")
        grande = next(v for v in vistas if v is not None)
        assert _perto(_caixa_da_tinta(grande, rgb=False), no_pdf)
    finally:
        cheia.done(0)


# --- D-020 / P-129: o desfazer e o Retângulo (lista única 1.3, 1.6, 1.7, 1.9, 4.6) -----------

def _regiao_pintar(x0=0.15, y0=0.15, x1=0.85, y1=0.5):
    """Um retângulo "Pintar por cima" (branco) feito à mão sobre o texto."""
    from core.selecao import MAO, PINTAR, RETANGULO, Regiao

    regiao = Regiao(tipo=PINTAR, forma=RETANGULO, pontos=[(x0, y0), (x1, y1)], origem=MAO)
    regiao.cor = "#ffffff"
    return regiao


def _tinta_no_alto(img: np.ndarray) -> float:
    """A parte do alto da página (onde o retângulo pinta) que é preta."""
    cinza = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    h, w = cinza.shape
    return float((cinza[int(0.2 * h): int(0.45 * h), int(0.25 * w): int(0.75 * w)] < 100).mean())


def test_p129_o_desfazer_tira_o_retangulo_e_ele_nao_sai_impresso(janela, tmp_path):
    """D-020 (18/07: "Ctrl+Z desfaz qualquer alteração, sem limite de quantidade") + promessa
    P-129 + lista única 23/10: 1.3 ("Marco um retângulo com a ferramenta Retângulo, clico no
    desfazer de baixo, e a marcação continua lá", nos 11 livros), 4.6 (a marca que o desfazer
    não tirou sai impressa) e 1.7 (o desfazer desfez a coisa de ANTES: o giro das 135 folhas).
    Livro de 2 páginas: girar as folhas, marcar um retângulo "Pintar por cima" branco sobre o
    texto → no PDF o texto some ali; o desfazer da barra de baixo tira o RETÂNGULO (o giro
    fica) e o PDF sai com o texto; "Limpar tudo" + desfazer traz a marcação de volta. REVERSÃO:
    no código antigo o desfazer desfazia o giro e o retângulo saía impresso."""
    janela.abrir_livro(_pdf(tmp_path / "ret.pdf", [_pagina(), _pagina()]))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._acao_nas_escolhidas("girar_direita", [0])
    tela._acao_nas_escolhidas("girar_esquerda", [0])          # volta de pé: duas ações
    giros = len(janela.acoes.feitas)
    tela.pilha_da_tela.setCurrentWidget(tela.trabalho)
    tela.escolher_ferramenta("retangulo")
    tela.ir_para_pagina(0)
    _assentar()
    tela.editor_selecao._acrescentar(_regiao_pintar())
    _assentar()
    assert len(projeto.paginas[0].selecao) == 1
    assert len(janela.acoes.feitas) == giros + 1               # a marcação é uma ação
    assert _tinta_no_alto(_gerar(janela, tmp_path, "com")[0]) < 0.01      # pintado de branco

    tela.botao_desfazer_embaixo.click()                       # o desfazer de baixo
    _assentar()
    assert projeto.paginas[0].selecao == []                   # o retângulo saiu
    assert len(janela.acoes.feitas) == giros                  # o giro ficou
    assert tela.editor_selecao.selecao.vazia                  # e a tela mostra
    assert _tinta_no_alto(_gerar(janela, tmp_path, "sem")[0]) > 0.1       # o texto volta

    tela.refazer()
    _assentar()
    assert len(projeto.paginas[0].selecao) == 1
    tela._limpar_marcacao()                                    # "Limpar tudo"
    assert projeto.paginas[0].selecao == []
    tela.desfazer()                                            # traz a marcação de antes
    _assentar()
    assert len(projeto.paginas[0].selecao) == 1


def test_lista_1_6_o_desfazer_devolve_os_avisos_da_pagina(janela, tmp_path):
    """Lista única 23/10, 1.6: "Mexo numa página que tinha aviso e desfaço: a página volta, mas
    o aviso some e a dúvida sai da lista sem eu ter resolvido nada" (Boécio p. 2 no
    Endireitar; Pesel p. 1 no "usar mais escuro"), "e no caminho contrário [...] trouxe um
    aviso a mais". D-020. Página com o aviso "Ficou escura": girar à mão 1,5° (a página é
    desenhada e medida de novo e o aviso sai), desfazer → o aviso volta, e só ele. REVERSÃO:
    no código antigo o aviso não voltava."""
    from core import analise

    janela.abrir_livro(_pdf(tmp_path / "aviso.pdf", [_pagina(), _pagina()]))
    tela, projeto = janela.tela_conferir, janela.projeto
    pagina = projeto.paginas[0]
    pagina.alertas = [analise.ESCURA_DEMAIS]
    tela._gravar_angulo(0, 1.5)
    pagina.alertas = []                         # a medida da página nova tirou o aviso
    tela.desfazer()
    _assentar()
    assert pagina.angulo_manual is None
    assert pagina.alertas == [analise.ESCURA_DEMAIS]


def test_lista_1_9_o_retangulo_feito_a_mao_aparece_dentro_da_area_da_maquina(app):
    """Lista única 23/10, 1.9: "Numa página que o programa já marcou quase inteira como gravura
    (em salmão), o retângulo que eu marco some dentro do salmão". Agora a área feita à mão tem
    o contorno cheio na cor do tipo dela: na beirada do retângulo há pontos da cor da gravura
    (vermelho-alaranjado puro), que a área da máquina sozinha não tem. Falha no código antigo
    (lá só o colorido transparente, igual dentro e fora)."""
    from PySide6.QtGui import QImage

    from core.selecao import AUTOMATICO, GRAVURA, MAO, RETANGULO, Regiao, Selecao
    from ui.widgets.editor_selecao import EditorSelecao

    editor = EditorSelecao()
    editor.resize(400, 560)
    editor.definir_imagem(np.full((560, 400, 3), 230, np.uint8))
    selecao = Selecao()
    selecao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.02, 0.02), (0.98, 0.98)],
                               origem=AUTOMATICO))
    selecao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.3, 0.3), (0.7, 0.6)],
                               origem=MAO))
    editor.definir_selecao(selecao)
    # D-580 (29/10/2026): as cores e o contorno das feitas à mão só aparecem com o botão
    # "marcações" ligado (de fábrica escondidos); a 1.9 vale com ele ligado
    editor.definir_mostrar_marcacao(True)
    imagem = editor.grab().toImage().convertToFormat(QImage.Format_RGB888)
    largura, altura = imagem.width(), imagem.height()
    dados = np.frombuffer(imagem.constBits(), np.uint8).reshape(altura, imagem.bytesPerLine())
    rgb = dados[:, :largura * 3].reshape(altura, largura, 3)
    area = editor._area
    x = area.left() + int(0.3 * area.width())
    meio_y = area.top() + int(0.45 * area.height())
    borda = rgb[meio_y, max(0, x - 2): x + 3]
    assert any(abs(int(p[0]) - 255) < 40 and int(p[1]) < 110 and int(p[2]) < 60 for p in borda), borda
    dentro = rgb[meio_y, x + 20]
    assert not (int(dentro[1]) < 110 and int(dentro[2]) < 60)          # dentro: só o colorido


# --- D-090 / D-091 (P-061, P-065): "usar em todas" nunca apaga exceção ------------------------

def test_d090_usar_em_todas_do_dividir_abre_as_folhas_e_nao_apaga_a_linha_propria(
        janela, tmp_path, monkeypatch):
    """D-090 (08/10/2026: "fazer um corte e mandar para todas as paginas e alterar em algumas
    paginas só o corte quando cortamos alguma, assim quando mudar de um não muda de todas, eu
    devo conseguir abrir uma aba para selecionar as que eu quero ( as paginas) ou também
    simplismente apertar num botão e selecionar todas."), D-091 ("'Selecionar todas' e
    'Nenhuma'"), promessa P-061. Livro de 4 folhas dividido: a linha da folha 3 acertada à mão
    (exceção); na folha 1, mover a linha e "usar em todas" → abre "Em quais páginas?" com as
    FOLHAS, a 3 desmarcada; aplicar → as folhas 2 e 4 ganham a linha da 1, a 3 fica com a dela.
    REVERSÃO: no código antigo a linha ia para todas, sem lista, e a da folha 3 se perdia."""
    from ui.dialogo_escolher_paginas import DialogoEscolherPaginas

    tela = _dividido(janela, tmp_path, folhas=4)
    projeto = janela.projeto
    tela.escolher_ferramenta("dividir")
    tela._ir_para(2)
    tela._mover_corte(0.44)                                   # a exceção, à mão
    tela._ir_para(0)
    tela._mover_corte(0.53)
    vistas = []

    def aplicar(dialogo):
        textos = [dialogo.lista.item(i).text() for i in range(dialogo.lista.count())]
        marcadas = dialogo.escolhidas()
        vistas.append((textos, marcadas, dialogo.botao_todas.text(), dialogo.botao_nenhuma.text()))
        return DialogoEscolherPaginas.Accepted

    monkeypatch.setattr(DialogoEscolherPaginas, "exec", aplicar)
    tela._corte_em_todas()
    assert vistas, "não abriu a lista (D-090)"
    textos, marcadas, todas, nenhuma = vistas[0]
    assert textos[0].startswith("Folha 1") and len(textos) == 4
    assert "linha própria" in textos[2] and 2 not in marcadas      # a exceção desmarcada
    assert marcadas == [0, 1, 3]
    assert (todas, nenhuma) == ("Selecionar todas", "Nenhuma")
    linhas = [round(f.posicao_corte, 2) for f in projeto.folhas]
    assert linhas == [0.53, 0.53, 0.44, 0.53]

    monkeypatch.setattr(DialogoEscolherPaginas, "exec", lambda self: 0)      # cancelar
    tela._mover_corte(0.6)
    tela._corte_em_todas()
    assert [round(f.posicao_corte, 2) for f in projeto.folhas] == [0.6, 0.53, 0.44, 0.53]


def test_d090_usar_em_todas_do_cortar_nao_apaga_a_excecao(janela, tmp_path, monkeypatch):
    """D-090 no Cortar (Lista de bugs, 08/10: "O 'usar em todas' da aba Bordas apaga as exceções
    por página"; consertado no item 2.13, conferido aqui na etapa 9b-2): a página com corte
    próprio vem desmarcada e fica com o dela."""
    from ui.dialogo_escolher_paginas import DialogoEscolherPaginas

    janela.abrir_livro(_pdf(tmp_path / "bordas.pdf", [_pagina() for _ in range(3)]))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._registrar("recortar", "pagina", [2], {"recorte": [0.1, 0.1, 0.5, 0.5]}, "exceção")
    tela.ir_para_pagina(0)
    tela._registrar("recortar", "pagina", [0], {"recorte": [0.0, 0.0, 0.8, 0.8]}, "corte")
    monkeypatch.setattr(DialogoEscolherPaginas, "exec", lambda self: DialogoEscolherPaginas.Accepted)
    tela._recorte_em_todas()
    assert tuple(projeto.paginas[1].recorte) == (0.0, 0.0, 0.8, 0.8)
    assert tuple(projeto.paginas[2].recorte) == (0.1, 0.1, 0.5, 0.5)


# --- D-156: "só neste pedaço" (no Preto e branco e sem "Limpar a folha") --------------------

def _pagina_com_foto() -> np.ndarray:
    """Papel amarelado com texto e uma "foto" colorida (azul e vermelho) no meio."""
    img = _pagina()
    img[330:520, 160:440] = (200, 80, 40)                 # BGR: azul
    img[330:520, 300:440] = (40, 60, 210)                 # vermelho
    return img


def _pedaco(filtro: str):
    from core.selecao import GRAVURA, MAO, RETANGULO, Regiao

    regiao = Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.25, 0.38), (0.75, 0.63)], origem=MAO)
    regiao.filtro = filtro
    return regiao


def _saturacao_no_meio(img: np.ndarray) -> float:
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    h, w = hsv.shape[:2]
    return float(hsv[int(0.42 * h): int(0.6 * h), int(0.3 * w): int(0.7 * w), 1].mean())


@pytest.mark.parametrize("com_limpar", [True, False])
def test_d156_so_neste_pedaco_vale_no_preto_e_branco_e_sem_limpar(janela, tmp_path, com_limpar):
    """D-156 (01/10/2026: "espero ter a escolha de conseguir deixar a foto em original, caso
    precise."; Lista de bugs 05/10: "No Preto e branco, o 'só neste pedaço' da aba Marcar é
    ignorado"; o pedido da etapa 9b-2: "'Só neste pedaço' ignorado sem 'Limpar a folha'").
    Página em Preto e branco, a foto marcada "só neste pedaço: Original" → no PDF a foto sai
    colorida e o resto em preto e branco; com o "Limpar a folha" do livro ligado (Automático) e
    desligado (o filtro escolhido à mão na página, D-009). Conferido na etapa 9b-2: já vinha
    consertado (60d8c58 e etapa 1); este teste guarda."""
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    janela.abrir_livro(_pdf(tmp_path / "foto.pdf", [_pagina_com_foto()]))
    tela, projeto = janela.tela_conferir, janela.projeto
    if com_limpar:
        _rodar(janela, [A.LIMPAR], opcoes={"filtro_padrao": PRETO_E_BRANCO})
    else:
        tela._escolher_filtro(PRETO_E_BRANCO)
    assert projeto.limpar is com_limpar
    tela.escolher_ferramenta("retangulo")
    tela.ir_para_pagina(0)
    _assentar()
    sem_pedaco = _gerar(janela, tmp_path, "sem")[0]
    assert _saturacao_no_meio(sem_pedaco) < 10                   # em preto e branco
    tela._escolher_filtro_da_regiao(ORIGINAL)                  # "só neste pedaço: Original"
    tela.editor_selecao._acrescentar(_pedaco(ORIGINAL))
    _assentar()
    assert projeto.paginas[0].selecao[-1]["filtro"] == ORIGINAL
    com_pedaco = _gerar(janela, tmp_path, "com")[0]
    assert _saturacao_no_meio(com_pedaco) > 100                  # a foto em Original
    cinza = cv2.cvtColor(com_pedaco, cv2.COLOR_RGB2GRAY)
    assert float(((cinza > 20) & (cinza < 235))[:120].mean()) < 0.02   # o resto: preto e branco


# --- Lista de bugs 12/10: "letra e traço" marcado à mão protege a tinta do "Só as letras" -----

@pytest.mark.parametrize("modo", ["apagar", "rede"])
def test_bug_12_10_letra_e_traco_a_mao_protege_a_tinta_do_so_as_letras(modo):
    """Lista de bugs de 12/10/2026: "Marcar uma área como 'letra e traço' à mão não protege a
    tinta do apagar do 'Só as letras' (core/misto.py, _fora_do_texto). Na rodada 5 o Samuel viu,
    em simulação, que a tinta voltava." (D-281: o aviso manda marcar "letra e traço" quando é
    escrita.) Página com linhas de texto e uma nota fina (cinza claro, fora das linhas): o "Só
    as letras" ("Guardar só o texto" e a rede de segurança) apaga a nota; marcada à mão como
    "letra e traço", a nota fica inteira. REVERSÃO: no código antigo a nota sumia igual."""
    from core import misto
    from core.selecao import LETRA, MAO, RETANGULO, Regiao, Selecao

    img = np.full((800, 600), 225, np.uint8)
    linhas = np.zeros((800, 600), bool)
    for y in range(100, 500, 40):
        img[y:y + 14, 80:520] = 20
        linhas[y - 4:y + 18, 70:530] = True
    for x in range(100, 500, 12):                         # a nota: traços finos, claros
        img[640:650, x:x + 6] = 120
    selecao = Selecao()
    sem, _ = misto.aplicar_misto(img, selecao, fora_do_texto=modo, linhas=linhas,
                                 altura_linha=14.0)
    assert float((sem[640:650, 100:500] == 0).mean()) < 0.05          # apagada
    selecao.acrescentar(Regiao(tipo=LETRA, forma=RETANGULO, pontos=[(0.1, 0.78), (0.9, 0.84)],
                               origem=MAO))
    com, _ = misto.aplicar_misto(img, selecao, fora_do_texto=modo, linhas=linhas,
                                 altura_linha=14.0)
    assert float((com[640:650, 100:500] == 0).mean()) > 0.3            # protegida
    assert np.array_equal(com[:600], sem[:600])                        # o resto não muda


# --- Lista de bugs 22/10: botões que aparecem por um instante como janelinhas soltas -------

class _VigiaDeJanelas:
    """Anota todo botão que aparece como JANELA solta (sem pai) - a "janelinha" que pisca."""

    def __init__(self):
        from PySide6.QtCore import QObject

        vigia = self

        class _Filtro(QObject):
            def eventFilter(self, obj, evento):  # noqa: N802 - nome do Qt
                from PySide6.QtCore import QEvent
                from PySide6.QtWidgets import QAbstractButton

                if (evento.type() == QEvent.Show and isinstance(obj, QAbstractButton)
                        and obj.isWindow()):
                    vigia.soltas.append(obj.text() or obj.toolTip())
                return False

        self.soltas: list[str] = []
        self.filtro = _Filtro()


@pytest.mark.parametrize("qual", ["escolhas_do_misto", "miniaturas"])
def test_bug_22_10_nenhum_botao_pisca_como_janela_solta(app, qual):
    """Lista de bugs de 22/10/2026: "Quatro botões aparecem por um instante como janelinhas
    soltas ao abrir o programa ('Guardar a tinta forte', 'Guardar tudo', 'Guardar só o texto' e
    'ver todas') [...] o verificador da tinta viu o mesmo ao escolher um tipo no 'Marcar como'"
    (ui/widgets/escolhas_do_misto.py e ui/widgets/miniaturas.py). Montar as duas peças não
    mostra nenhum botão como janela solta. REVERSÃO: no código antigo os três botões do "Só as
    letras" e o "ver todas" eram mostrados antes de ter pai."""
    vigia = _VigiaDeJanelas()
    app.installEventFilter(vigia.filtro)
    try:
        if qual == "escolhas_do_misto":
            from ui.widgets.escolhas_do_misto import EscolhasDoMisto

            peca = EscolhasDoMisto()
            EscolhasDoMisto(compacto=True)
        else:
            from ui.widgets.miniaturas import PainelDeMiniaturas

            peca = PainelDeMiniaturas()
        _assentar()
    finally:
        app.removeEventFilter(vigia.filtro)
    assert vigia.soltas == [], vigia.soltas
    assert peca is not None


# --- Lista única: 1.2 e 5.9, 1.10, 1.11, 5.3 ------------------------------------------------

def test_lista_1_2_e_5_9_o_aviso_da_forca_do_preto_so_em_pagina_de_preto_e_branco(janela, tmp_path):
    """Lista única 23/10, 1.2 ("O aviso oferece 'usar mais fraco', e o botão não faz nada" -
    Escola p. 1 em Mágico pro, Horas p. 4 em Melhorar) e 5.9 ("O aviso fala de 'força do preto'
    em página feita com Mágico pro ou Melhorar, onde isso não existe"). D-114: cada filtro tem o
    seu medidor ("Força do preto" só no Preto e branco). O aviso "Ficou escura" (medido no
    cartão Preto e branco) só fica na página que sai em Preto e branco; ali o "usar mais fraco"
    muda a força do preto da página. REVERSÃO: no código antigo a página em Mágico pro ganhava
    o aviso (e o botão não mudava nada nela)."""
    from core import analise
    from core.filtros import MAGICO_PRO, ORIGINAL, PRETO_E_BRANCO

    janela.abrir_livro(_pdf(tmp_path / "escura.pdf", [_pagina(), _pagina()]))
    tela, projeto = janela.tela_conferir, janela.projeto
    pagina = projeto.paginas[0]
    original = cv2.cvtColor(_pagina(), cv2.COLOR_BGR2GRAY)
    preta = np.zeros_like(original)                         # o Preto e branco "todo preto"
    tela._escolher_filtro(MAGICO_PRO)
    tela._conferir_qualidade_do_preto_e_branco(pagina, {ORIGINAL: original, PRETO_E_BRANCO: preta})
    assert analise.ESCURA_DEMAIS not in pagina.alertas      # Mágico pro: sem o aviso
    tela._escolher_filtro(PRETO_E_BRANCO)
    tela._conferir_qualidade_do_preto_e_branco(pagina, {ORIGINAL: original, PRETO_E_BRANCO: preta})
    assert analise.ESCURA_DEMAIS in pagina.alertas          # Preto e branco: o aviso
    antes = pagina.forca_preto
    tela._escolher_forca("mais_fraco")                      # o botão do aviso
    assert pagina.forca_preto < antes
    pagina.alertas.append(analise.ESCURA_DEMAIS)
    tela._escolher_filtro(MAGICO_PRO)                       # trocou de filtro: o aviso sai
    tela._conferir_qualidade_do_preto_e_branco(pagina, {ORIGINAL: original, PRETO_E_BRANCO: preta})
    assert analise.ESCURA_DEMAIS not in pagina.alertas


def test_lista_1_10_a_tab_vai_a_proxima_duvida_mesmo_com_o_foco_num_botao(janela, tmp_path):
    """Lista única 23/10, 1.10: "A tecla Tab ('Ir para a próxima dúvida') não andou no teste do
    mapa (ficou na folha 2). Pode ser o lugar do foco". Com o foco num botão da área de
    trabalho (o "próxima dúvida"), a Tab vai à próxima página com dúvida em vez de só passar o
    foco. REVERSÃO: no código antigo o Qt usava a Tab para mudar o foco e a página não mudava."""
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    from core import analise

    janela.abrir_livro(_pdf(tmp_path / "tab.pdf", [_pagina() for _ in range(4)]))
    tela, projeto = janela.tela_conferir, janela.projeto
    projeto.paginas[2].alertas = [analise.ESCURA_DEMAIS]
    tela.escolher_ferramenta("mao")
    tela.ir_para_pagina(0)
    janela.show()
    janela.move(-3000, -3000)
    _assentar()
    botao = tela.botao_proxima_duvida
    botao.setFocusPolicy(Qt.StrongFocus)
    botao.setFocus()
    _assentar()
    assert QApplication.focusWidget() is botao
    QApplication.sendEvent(botao, QKeyEvent(QEvent.KeyPress, Qt.Key_Tab, Qt.NoModifier))
    _assentar()
    assert tela.indice_pagina == 2


def test_lista_1_11_esc_fecha_o_ver_todas(janela, tmp_path):
    """Lista única 23/10, 1.11: "Na grade 'ver todas' da tela de conferir, o Esc não volta; só o
    botão 'voltar ao trabalho'". Com a grade à vista, o Esc volta à área de trabalho (como o
    botão). REVERSÃO: no código antigo o Esc não fazia nada."""
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent

    janela.abrir_livro(_pdf(tmp_path / "esc.pdf", [_pagina() for _ in range(3)]))
    tela = janela.tela_conferir
    tela.abrir_todas_as_paginas()
    _assentar()
    assert tela.pilha_da_tela.currentWidget() is tela.todas
    janela.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier))
    _assentar()
    assert tela.pilha_da_tela.currentWidget() is tela.trabalho


def test_lista_5_3_a_caixinha_da_forca_sozinha_nao_fica_cinza_e_marcada(janela, tmp_path):
    """Lista única 23/10, 5.3 (Samuel, 0-2: "Essa opção não dá para desativar"): no Automático,
    com o Preto e branco, a caixinha "Escurecer sozinho a força do preto quando o texto sair
    falhado" aparecia MARCADA e CINZA sem o "Só as letras". Agora ela fica acesa: dá para
    desmarcar e marcar (regra 8 do plano: toda função automática liga e desliga). REVERSÃO: no
    código antigo ela ficava cinza."""
    from core.filtros import PRETO_E_BRANCO

    janela.abrir_livro(_pdf(tmp_path / "forca.pdf", [_pagina()]))
    estado = janela.estado_do_automatico
    estado.opcoes.update({"filtro_padrao": PRETO_E_BRANCO, "misto_so_as_letras": False,
                          "reforcar_texto_falhado": True})
    grande = janela.abrir_o_automatico(A.LIMPAR)
    try:
        grande._mostrar_opcoes()
        _assentar()
        caixa = grande.cx_forca_sozinha
        assert not caixa.isHidden() and caixa.isChecked() and caixa.isEnabled()
        caixa.click()
        assert estado.opcoes["reforcar_texto_falhado"] is False
    finally:
        janela._fechar_a_janela_do_automatico()
