"""D-583 e D-586 (Samuel, 29/10/2026): a caixinha "Respeitar as gravuras achadas".

Palavras dele:
  - D-583: "Precisamos da opção de jogar o filtro em cima de outro filtro ou só substituir o
    filtro que está colocado em cima." → depois da investigação (o que fica "por cima" é a
    marcação do Automático): "c" — "C — As duas, com uma escolha no painel do Filtro. Por
    exemplo, uma caixinha que diz se o filtro respeita ou não as gravuras achadas."
  - D-586 ("A"): "A — Uma caixinha no painel "Filtro da página", logo abaixo das figurinhas dos
    filtros: "Respeitar as gravuras achadas". De início vem ligada, que é como funciona hoje.
    Desligada, o filtro vale na página inteira: no Preto e branco, a capa sairia toda em preto e
    branco, como na fileira de baixo da primeira imagem que te mostrei. Vale com o "Aplicar em:
    só nesta / todas / daqui em diante" que já existe no painel."
  - Prova pedida no Livro: "capa do *Na escola de Jesus* depois do Automático, Preto e branco:
    caixinha ligada → pintura com cor; desligada → página toda em preto e branco; "todas" leva
    às outras páginas; Ctrl+Z desfaz; tela = PDF".

O que estas provas guardam:
  1. ligada (de fábrica) → a gravura que a máquina achou sai com a cor no Preto e branco;
     desligada → a página sai toda em preto e branco; ligada de novo → igual à primeira, byte
     a byte; a tela mostra o desenho de cada vez (D-473);
  2. o "antes / depois" e a tela cheia seguem a caixinha;
  3. ligada, a conta é exatamente a de antes da caixinha (byte a byte);
  4. o pedaço feito À MÃO ("Só neste pedaço") continua valendo com ela desligada (D-199/D-224);
  5. "todas" e "daqui em diante" levam a caixinha às outras páginas, sem apagar a exceção (o
     pedaço à mão de outra página fica: D-090/D-545);
  6. Ctrl+Z desfaz e Ctrl+Shift+Z refaz (D-020);
  7. projeto gravado antes da caixinha abre com ela ligada e sai idêntico;
  8. PDF = tela (D-066/D-473);
  9. no Original nada muda; no Melhorar e no Mágico pro, desligada = a página sem a marcação da
     máquina; com "Só as letras" (D-148) nada muda;
 10. D-587 (29/10): com "Só as letras" valendo (na página ou herdado do livro), a caixinha fica
     cinza e não dá para clicar, como a das molduras (D-168); ao desligar, volta com o valor de
     antes.

Livro sintético: papel amarelado, uma iluminura grande e colorida em cima (dourado, vermelho e
azul com hachura, o tipo "enfeite colorido" que fica com a cor no Preto e branco: D-144/D-127) e
linhas de "texto" embaixo. Caminho inteiro (§4.10): o Automático roda com Endireitar, Cortar as
bordas e Limpar a folha (de fábrica); a marcação que o "Gravuras e fotos" deixa é posta direto na
página (a iluminura como gravura e o texto como letra, origem "rede", como no livro dele), sem
rodar o detector, que é lento e não é o assunto aqui. Reversão (§4.7): no `2db002e` (antes da
caixinha) estas provas falham (relatorios/automatico-respeitar/reversao-no-2db002e.txt).
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

from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402

DPI = 150
AMARELADO = (170, 215, 235)            # BGR: papel velho
DOURADO, VERMELHO, AZUL = (70, 175, 215), (50, 50, 200), (190, 110, 40)
ILUMINURA = (60, 60, 540, 560)         # x0, y0, x1, y1 na página de 600 x 840
LARGURA, ALTURA = 600, 840


# --- o livro de teste -------------------------------------------------------------

def _pagina() -> np.ndarray:
    """Papel amarelado; em cima uma iluminura grande (fundo dourado, um quadro vermelho e um
    azul, com hachura marrom fina, como as das Horas); embaixo linhas de "texto"."""
    img = np.full((ALTURA, LARGURA, 3), AMARELADO, np.uint8)
    x0, y0, x1, y1 = ILUMINURA
    img[y0:y1, x0:x1] = DOURADO
    cv2.rectangle(img, (x0 + 60, y0 + 60), (x1 - 60, y0 + 220), VERMELHO, -1)
    cv2.rectangle(img, (x0 + 60, y0 + 260), (x1 - 60, y1 - 60), AZUL, -1)
    for y in range(y0, y1, 10):
        cv2.line(img, (x0, y), (x1, y), (30, 50, 90), 2)
    for y in range(600, ALTURA - 60, 36):
        img[y:y + 11, 110:LARGURA - 110] = 25
    return img


def _pdf(caminho: Path, folhas: int = 3) -> str:
    """Um livro de `folhas` folhas de uma página só (sem dividir)."""
    doc = fitz.open()
    for _ in range(folhas):
        img = _pagina()
        ok, buffer = cv2.imencode(".png", img)
        assert ok
        largura, altura = img.shape[1] / DPI * 72, img.shape[0] / DPI * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


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


def _esperar(condicao, segundos: float = 60.0, motivo: str = "") -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar(2)
        if condicao():
            return
        time.sleep(0.02)
    raise AssertionError(f"não aconteceu a tempo: {motivo}")


def _marcacao_da_maquina():
    """A marcação que o "Gravuras e fotos" do Automático deixa: a iluminura como gravura e o
    texto como letra (origem "rede", como no livro dele)."""
    from core.selecao import GRAVURA, LETRA, REDE, RETANGULO, Regiao, Selecao

    x0, y0, x1, y1 = ILUMINURA
    marcacao = Selecao()
    marcacao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, origem=REDE,
                                pontos=[(x0 / LARGURA, y0 / ALTURA), (x1 / LARGURA, y1 / ALTURA)]))
    marcacao.acrescentar(Regiao(tipo=LETRA, forma=RETANGULO, origem=REDE,
                                pontos=[(100 / LARGURA, 590 / ALTURA), (500 / LARGURA, 790 / ALTURA)]))
    return marcacao


def _depois_do_automatico(janela, tmp_path: Path, folhas: int = 3):
    """O caminho do Kaique: abrir o livro, rodar o Automático (Endireitar, Cortar as bordas,
    Limpar a folha: o de fábrica), e em todas as páginas a marcação do "Gravuras e fotos"
    (definitiva). Devolve a tela, na página 1, com o Zoom (a página limpa: D-580) e o painel
    "Filtro da página" aberto."""
    from tests.ajudante_do_automatico import rodar_como_o_conferir
    from ui.tela_conferir import PAINEL_FILTRO

    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", folhas))
    assert rodar_como_o_conferir(janela, limpar=True)
    projeto = janela.projeto
    assert projeto.limpar and projeto.passou_pelo_automatico
    projeto.detectar_regioes = True                # o "Gravuras e fotos" ligado no livro
    for pagina in projeto.paginas:
        pagina.guardar_selecao(_marcacao_da_maquina(), provisoria=False)
        pagina.gravura_feita_com = ""              # a marcação vale como está (não procura de novo)
    tela = janela.tela_conferir
    tela.previas.invalidar()
    tela.escolher_ferramenta("zoom")
    tela.ir_para_pagina(0)
    tela.paineis.abrir(PAINEL_FILTRO)
    _assentar()
    # o primeiro desenho de cada página depois do Automático guarda as medidas dela (a
    # geometria); os seguintes saem iguais entre si. As comparações byte a byte começam depois
    # (ver "Ressalvas" no ONDE-PAREI: isso acontece também no 2db002e e no Original).
    _esperar(lambda: tela.previas.ja_pronta(0, tela._dpi_atual) is not None, motivo="a prévia")
    for pagina in projeto.paginas:
        _desenho(projeto, pagina, 110)
    return tela


def _caixa(tela):
    return tela.caixa_respeitar_gravuras


def _escolher(tela, filtro: str) -> None:
    """O clique no filtro do painel "Filtro da página" (o mesmo sinal das figurinhas)."""
    tela.paineis.filtro_da_pagina.filtro_escolhido.emit(filtro)
    _assentar()


def _desenho(projeto, pagina, dpi: int) -> np.ndarray:
    """A página desenhada do scan, numa cópia (core.pipeline.renderizar_pagina, o mesmo
    desenho da prévia e do PDF), em 3 canais (BGR)."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img, _ = renderizar_pagina(doc, copy.deepcopy(projeto), copy.deepcopy(pagina), dpi=dpi)
    finally:
        doc.close()
    return _bgr(img)


def _bgr(img: np.ndarray) -> np.ndarray:
    return np.repeat(img[..., None], 3, axis=2) if img.ndim == 2 else img


def _colorido(img: np.ndarray) -> float:
    """Fração dos pontos com cor (saturação acima de 60 em 255)."""
    hsv = cv2.cvtColor(_bgr(img), cv2.COLOR_BGR2HSV)
    return float((hsv[:, :, 1] > 60).mean())


def _miolo_da_iluminura(img: np.ndarray) -> np.ndarray:
    """O meio da iluminura (a página pode ter sido cortada pelo Automático: pega pela fração,
    bem para dentro)."""
    h, w = img.shape[:2]
    return img[int(h * 0.2):int(h * 0.55), int(w * 0.25):int(w * 0.75)]


def _diferenca(a: np.ndarray, b: np.ndarray) -> float:
    assert a.shape == b.shape, f"tamanhos diferentes: {a.shape} e {b.shape}"
    return float(np.abs(a.astype(np.int16) - b.astype(np.int16)).mean())


def _pixmap_bgr(pix) -> np.ndarray:
    imagem = pix.toImage().convertToFormat(pix.toImage().Format.Format_RGB888)
    w, h = imagem.width(), imagem.height()
    dados = np.frombuffer(imagem.constBits(), np.uint8).reshape(h, imagem.bytesPerLine())
    return dados[:, : w * 3].reshape(h, w, 3)[..., ::-1].copy()


def _paginas_do_pdf(caminho: str, dpi: int) -> list[np.ndarray]:
    with fitz.open(caminho) as doc:
        saida = []
        for pagina in doc:
            pix = pagina.get_pixmap(dpi=dpi, colorspace=fitz.csRGB)
            saida.append(np.frombuffer(pix.samples, np.uint8).reshape(
                pix.height, pix.width, pix.n)[..., :3][..., ::-1].copy())
        return saida


def _gerar(projeto, tmp_path: Path, nome: str, dpi: int) -> list[np.ndarray]:
    """O PDF do livro, como o "Confirmar e processar" grava (core.pipeline.processar)."""
    from core.pipeline import processar

    copia = copy.deepcopy(projeto)
    copia.caminho_saida = str(tmp_path / f"{nome}.pdf")
    return _paginas_do_pdf(processar(copia), dpi)


# --- 1. ligada / desligada / ligada de novo, na tela ---------------------------------

def test_d586_ligada_guarda_a_cor_desligada_toda_em_preto_e_branco_religada_igual(janela, tmp_path):
    """D-586: "De início vem ligada, que é como funciona hoje. Desligada, o filtro vale na página
    inteira: no Preto e branco, a capa sairia toda em preto e branco". Página em Preto e branco
    depois do Automático, com a iluminura achada pela máquina:
      - a caixinha está no painel, logo abaixo das figurinhas, ligada;
      - ligada → a iluminura sai com a cor (pontos coloridos);
      - desligada (clique de verdade) → a página toda em preto e branco (nenhum ponto colorido),
        e a tela mostra esse desenho (D-473);
      - ligada de novo → o desenho é o da primeira vez, byte a byte."""
    from PySide6.QtWidgets import QCheckBox

    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    painel = tela.paineis.filtro_da_pagina
    caixa = _caixa(tela)
    assert caixa.text() == "Respeitar as gravuras achadas"
    assert caixa.toolTip()
    assert isinstance(caixa, QCheckBox) and caixa.isVisibleTo(tela)
    # "logo abaixo das figurinhas dos filtros": o primeiro item do painel depois da fila
    itens = [painel.dentro.itemAt(i).widget() for i in range(painel.dentro.count())]
    assert itens.index(caixa) == itens.index(painel._fila) + 1
    assert caixa.isChecked() and pagina.respeitar_gravuras_achadas is True

    _escolher(tela, PRETO_E_BRANCO)
    dpi = tela._dpi_atual
    editor = tela.editor_selecao
    _esperar(lambda: editor._img is not None and editor._img is tela.previas.ja_pronta(0, dpi),
             motivo="a prévia em Preto e branco")
    ligada = _desenho(projeto, pagina, dpi)
    assert _colorido(_miolo_da_iluminura(ligada)) > 0.5, "ligada, a iluminura perdeu a cor"
    assert _diferenca(_bgr(editor._img), ligada) < 0.5

    caixa.click()
    _assentar()
    assert pagina.respeitar_gravuras_achadas is False and not caixa.isChecked()
    _esperar(lambda: editor._img is not None and editor._img is tela.previas.ja_pronta(0, dpi),
             motivo="a prévia com a caixinha desligada")
    desligada = _desenho(projeto, pagina, dpi)
    assert _colorido(desligada) == 0.0, "desligada, sobrou cor na página"
    assert _colorido(_bgr(editor._img)) == 0.0, "a tela ainda mostra cor"
    assert _diferenca(_bgr(editor._img), desligada) < 0.5
    assert pagina.obter_selecao().regioes, "a marcação da máquina continua guardada na página"

    caixa.click()
    _assentar()
    assert pagina.respeitar_gravuras_achadas is True
    assert np.array_equal(_desenho(projeto, pagina, dpi), ligada), "religada não é igual à primeira"
    _esperar(lambda: editor._img is not None and editor._img is tela.previas.ja_pronta(0, dpi),
             motivo="a prévia religada")
    assert _diferenca(_bgr(editor._img), ligada) < 0.5
    assert all(p.respeitar_gravuras_achadas for p in projeto.paginas[1:]), "mudou outra página"


# --- 2. "antes / depois" e tela cheia --------------------------------------------------

def test_d586_antes_depois_e_tela_cheia_seguem_a_caixinha(janela, tmp_path):
    """D-473/D-066 ("precisamos que o pdf saia que nem está na tela"): com a caixinha desligada,
    o lado "depois" do "antes / depois" e a página da tela cheia dos filtros (Preto e branco)
    saem todos em preto e branco; ligada, com a cor."""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    vista = tela.vista_antes_depois
    tela.botao_antes_depois.click()
    dpi = tela._dpi_atual
    for ligada in (True, False):
        if _caixa(tela).isChecked() != ligada:
            _caixa(tela).click()
        _esperar(lambda: tela.previas.ja_pronta(0, dpi) is not None and vista.depois is not None
                 and vista.antes is not None, motivo="o antes e o depois")
        _assentar()
        depois = _pixmap_bgr(vista.depois)
        assert _diferenca(depois, _desenho(projeto, pagina, dpi)) < 0.5
        cor = _colorido(_miolo_da_iluminura(depois))
        assert (cor > 0.5) if ligada else (_colorido(depois) == 0.0), (ligada, cor)
        cheia = None
        _esperar(lambda: tela.previas.pegar_com_filtro(0, dpi, PRETO_E_BRANCO) is not None,
                 motivo="a página da tela cheia")
        cheia = tela.previas.pegar_com_filtro(0, dpi, PRETO_E_BRANCO)
        assert ((_colorido(_miolo_da_iluminura(cheia)) > 0.5) if ligada
                else (_colorido(cheia) == 0.0)), f"a tela cheia não segue a caixinha ({ligada})"


# --- 3. ligada = a conta de antes, byte a byte ------------------------------------------

@pytest.mark.parametrize("filtro", [ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO])
def test_d586_ligada_e_a_conta_de_antes_byte_a_byte(janela, tmp_path, monkeypatch, filtro):
    """D-586 ("De início vem ligada, que é como funciona hoje"): ligada, a página sai igual ponto
    por ponto ao desenho sem a caixinha (a função que escolhe a marcação trocada pela de antes,
    que devolve a marcação inteira), nos quatro filtros. A prova entre commits (o `2db002e`
    contra este) está em relatorios/automatico-respeitar/identica-ao-2db002e.txt."""
    from core import pipeline

    _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    pagina.filtro = filtro
    agora = _desenho(projeto, pagina, 110)
    monkeypatch.setattr(pipeline, "marcacao_que_o_filtro_usa", lambda projeto, pagina, s: s)
    assert np.array_equal(agora, _desenho(projeto, pagina, 110))


# --- 4. o pedaço feito à mão continua valendo -------------------------------------------

def test_d586_o_pedaco_a_mao_continua_valendo_com_a_caixinha_desligada(janela, tmp_path):
    """D-199/D-224 ("espero ter a escolha de conseguir deixar a foto em original"): a caixinha
    fala das gravuras ACHADAS. Com ela desligada, um pedaço marcado À MÃO na iluminura com
    "Só neste pedaço: Original" continua saindo como o scan (com a cor), e o resto da página
    sai em preto e branco."""
    from core.selecao import MAO, GRAVURA, RETANGULO, Regiao

    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    marcacao = pagina.obter_selecao()
    marcacao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, origem=MAO, filtro=ORIGINAL,
                                pontos=[(0.3, 0.2), (0.7, 0.45)]))
    pagina.guardar_selecao(marcacao, provisoria=False)
    _escolher(tela, PRETO_E_BRANCO)
    _caixa(tela).click()
    _assentar()
    assert pagina.respeitar_gravuras_achadas is False
    img = _desenho(projeto, pagina, 110)
    h, w = img.shape[:2]
    pedaco = img[int(h * 0.24):int(h * 0.41), int(w * 0.34):int(w * 0.66)]
    assert _colorido(pedaco) > 0.5, "o pedaço à mão perdeu a cor"
    fora = img[int(h * 0.75):, :]                  # o texto, embaixo: preto e branco
    assert _colorido(fora) == 0.0
    resto_da_iluminura = img[int(h * 0.5):int(h * 0.6), int(w * 0.2):int(w * 0.8)]
    assert _colorido(resto_da_iluminura) == 0.0, "o que a máquina achou ainda guarda a cor"


# --- 5. "Aplicar em" -------------------------------------------------------------------

@pytest.mark.parametrize("alcance", ["todas", "daqui em diante"])
def test_d586_aplicar_em_leva_a_caixinha_sem_apagar_excecao(janela, tmp_path, alcance):
    """D-586 ("Vale com o "Aplicar em: só nesta / todas / daqui em diante""), D-090/D-545
    (nunca apaga exceção): na página 2, desligar a caixinha e apertar "todas" (ou "daqui em
    diante") → as páginas alcançadas ficam com ela desligada (as de antes, no "daqui em diante",
    não); o pedaço feito à mão da página 3 fica onde estava, e continua valendo."""
    from PySide6.QtWidgets import QPushButton

    from core.selecao import MAO, GRAVURA, RETANGULO, Regiao

    tela = _depois_do_automatico(janela, tmp_path)
    projeto = janela.projeto
    terceira = projeto.paginas[2]
    marcacao = terceira.obter_selecao()
    marcacao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, origem=MAO, filtro=ORIGINAL,
                                pontos=[(0.3, 0.2), (0.7, 0.45)]))
    terceira.guardar_selecao(marcacao, provisoria=False)
    selecao_antes = copy.deepcopy(terceira.selecao)
    tela.ir_para_pagina(1)
    _assentar()
    _escolher(tela, PRETO_E_BRANCO)
    _caixa(tela).click()
    _assentar()
    assert projeto.paginas[1].respeitar_gravuras_achadas is False
    botao = next(b for b in tela.paineis.filtro_da_pagina.findChildren(QPushButton)
                 if b.text() == alcance)
    botao.click()
    _assentar()
    esperado = {"todas": [False, False, False], "daqui em diante": [True, False, False]}[alcance]
    assert [p.respeitar_gravuras_achadas for p in projeto.paginas] == esperado
    assert terceira.selecao == selecao_antes, "o 'Aplicar em' mexeu no pedaço à mão"
    img = _desenho(projeto, terceira, 110)
    h, w = img.shape[:2]
    assert _colorido(img[int(h * 0.24):int(h * 0.41), int(w * 0.34):int(w * 0.66)]) > 0.5
    assert _colorido(img[int(h * 0.5):int(h * 0.6), int(w * 0.2):int(w * 0.8)]) == 0.0


# --- 6. Ctrl+Z / Ctrl+Shift+Z ---------------------------------------------------------

def test_d586_ctrl_z_desfaz_e_ctrl_shift_z_refaz(janela, tmp_path):
    """D-020 ("Ctrl+Z desfaz qualquer alteração, sem limite de quantidade, e Ctrl+Shift+Z
    refaz"): desligar a caixinha é uma ação do Histórico; as teclas a desfazem e a refazem, e a
    caixinha na tela acompanha."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    tela = _depois_do_automatico(janela, tmp_path)
    pagina = janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    _caixa(tela).click()
    _assentar()
    assert pagina.respeitar_gravuras_achadas is False
    assert "Respeitar as gravuras achadas" in janela.acoes.feitas[-1].descricao
    janela.show()
    janela.move(-3000, -3000)
    janela.activateWindow()
    _assentar()
    QTest.keyClick(janela, Qt.Key_Z, Qt.ControlModifier)
    _assentar()
    assert pagina.respeitar_gravuras_achadas is True and _caixa(tela).isChecked()
    QTest.keyClick(janela, Qt.Key_Z, Qt.ControlModifier | Qt.ShiftModifier)
    _assentar()
    assert pagina.respeitar_gravuras_achadas is False and not _caixa(tela).isChecked()


# --- 7. projeto antigo -------------------------------------------------------------------

def test_d586_projeto_antigo_abre_ligado_e_sai_identico(janela, tmp_path):
    """D-586 ("De início vem ligada"): o projeto.json gravado antes da caixinha (sem a chave
    "respeitar_gravuras_achadas") abre com ela ligada em todas as páginas, e a página sai igual
    ponto por ponto à do projeto de agora; o projeto novo grava a chave."""
    from modelos import Projeto

    _depois_do_automatico(janela, tmp_path)
    projeto = janela.projeto
    projeto.paginas[0].filtro = PRETO_E_BRANCO
    dados = projeto.para_dicionario()
    assert all(p["respeitar_gravuras_achadas"] is True for p in dados["paginas"])
    for p in dados["paginas"]:
        del p["respeitar_gravuras_achadas"]           # o projeto gravado antes da caixinha
    antigo = Projeto.de_dicionario(copy.deepcopy(dados))
    assert all(p.respeitar_gravuras_achadas is True for p in antigo.paginas)
    assert np.array_equal(_desenho(antigo, antigo.paginas[0], 110),
                          _desenho(projeto, projeto.paginas[0], 110))


# --- 8. PDF = tela ------------------------------------------------------------------------

def test_d586_o_pdf_sai_como_a_tela(janela, tmp_path):
    """D-066 ("precisamos que o pdf saia que nem está na tela") e D-473 ("Tela e PDF saem da
    mesma conta"): página 1 em Preto e branco com a caixinha desligada e página 2 em Preto e
    branco com ela ligada → no PDF gerado, a 1 sai toda em preto e branco e a 2 com a iluminura
    colorida; e cada página do PDF é o desenho do tamanho do PDF (a imagem que a tela mostra
    reduzida)."""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto = janela.projeto
    _escolher(tela, PRETO_E_BRANCO)
    _caixa(tela).click()
    _assentar()
    tela.ir_para_pagina(1)
    _assentar()
    _escolher(tela, PRETO_E_BRANCO)
    assert [p.respeitar_gravuras_achadas for p in projeto.paginas[:2]] == [False, True]
    dpi = int(projeto.qualidade_dpi)
    paginas = _gerar(projeto, tmp_path, "saida", dpi)
    assert _colorido(paginas[0]) < 0.001, "no PDF a página 1 ainda tem cor"
    assert _colorido(_miolo_da_iluminura(paginas[1])) > 0.5, "no PDF a página 2 perdeu a cor"
    for k in (0, 1):
        desenho = _desenho(projeto, projeto.paginas[k], dpi)
        no_pdf = paginas[k]
        if no_pdf.shape != desenho.shape:
            no_pdf = cv2.resize(no_pdf, (desenho.shape[1], desenho.shape[0]),
                                interpolation=cv2.INTER_AREA)
        assert _diferenca(no_pdf, desenho) < 3.0, f"a página {k + 1} do PDF não é a da tela"


# --- 9. Original, Melhorar / Mágico pro, "Só as letras" -----------------------------------

def test_d586_no_original_nada_muda(janela, tmp_path):
    """"No Original não muda nada": desligada ou ligada, o mesmo desenho, byte a byte."""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    assert pagina.filtro == ORIGINAL
    ligada = _desenho(projeto, pagina, 110)
    _caixa(tela).click()
    _assentar()
    assert pagina.respeitar_gravuras_achadas is False
    assert np.array_equal(_desenho(projeto, pagina, 110), ligada)


@pytest.mark.parametrize("filtro", [MELHORAR, MAGICO_PRO])
def test_d586_melhorar_e_magico_pro_desligada_e_a_pagina_sem_a_marcacao(janela, tmp_path, filtro):
    """D-586 ("Desligada, o filtro vale na página inteira"): no Melhorar e no Mágico pro, com a
    caixinha desligada, a página sai exatamente como sairia sem a marcação da máquina (a
    "fileira de baixo" da imagem que ele viu), e diferente de quando ligada."""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    _escolher(tela, filtro)
    ligada = _desenho(projeto, pagina, 110)
    _caixa(tela).click()
    _assentar()
    desligada = _desenho(projeto, pagina, 110)
    sem_marcacao = copy.deepcopy(pagina)
    sem_marcacao.respeitar_gravuras_achadas = True
    projeto_sem = copy.deepcopy(projeto)
    projeto_sem.detectar_regioes = False           # nada achado: a página inteira igual
    assert np.array_equal(desligada, _desenho(projeto_sem, sem_marcacao, 110))
    assert not np.array_equal(desligada, ligada)


def test_d586_com_so_as_letras_a_caixinha_nao_muda_a_pagina(janela, tmp_path):
    """D-148 ("Só as letras": só as letras viram preto e branco; gravura, foto, moldura e
    iluminura ficam como no original). O "Só as letras" depende das gravuras achadas para
    guardar a cor. D-587 (29/10, "sim" à opção C): o "Só as letras" manda — com ele ligado, a
    caixinha não muda a página (a iluminura continua com a cor) e fica cinza (provas
    test_d587_*)."""
    from PySide6.QtWidgets import QCheckBox

    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    so_as_letras = next(c for c in tela.paineis.filtro_da_pagina.findChildren(QCheckBox)
                        if c.text() == "Só as letras" and c.isVisibleTo(tela))
    so_as_letras.click()
    _assentar()
    assert pagina.misto_so_as_letras is True
    projeto.misto_fora_do_texto = "tudo"           # sem o leitor de texto (lento, não é o assunto)
    pagina.misto_fora_do_texto = "tudo"
    ligada = _desenho(projeto, pagina, 110)
    assert _colorido(_miolo_da_iluminura(ligada)) > 0.5
    # desde a D-587 a caixinha fica cinza com "Só as letras" (não dá para clicar); a página
    # pode ter ficado desligada de antes: o valor guardado desligado também não muda a página
    pagina.respeitar_gravuras_achadas = False
    assert np.array_equal(_desenho(projeto, pagina, 110), ligada)


# --- 10. D-587: com "Só as letras", a caixinha fica cinza (como a D-168) -------------------

def _caixa_so_as_letras(tela):
    from PySide6.QtWidgets import QCheckBox

    return next(c for c in tela.paineis.filtro_da_pagina.findChildren(QCheckBox)
                if c.text() == "Só as letras" and c.isVisibleTo(tela))


@pytest.mark.parametrize("valor_antes", [True, False])
def test_d587_com_so_as_letras_na_pagina_a_caixinha_fica_cinza_e_volta(janela, tmp_path, valor_antes):
    """D-587 (Samuel, 29/10/2026, "sim" a: "enquanto a "Só as letras" estiver marcada, a caixinha
    nova fica cinza e não dá para clicar. É assim que já funciona com a caixinha das molduras.");
    o jeito da D-168 ("Fica apagada (cinza) enquanto 'Só as letras' estiver marcada, e volta como
    estava ao desligar"). Página em Preto e branco: ligar "Só as letras" → a caixinha fica cinza
    e o valor guardado não muda (clicar nela não faz nada); desligar → volta clicável, com o
    valor de antes (ligada ou desligada)."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    tela = _depois_do_automatico(janela, tmp_path)
    pagina = janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    caixa = _caixa(tela)
    assert caixa.isEnabled()
    if not valor_antes:
        caixa.click()
        _assentar()
    assert pagina.respeitar_gravuras_achadas is valor_antes
    _caixa_so_as_letras(tela).click()
    _assentar()
    assert pagina.misto_so_as_letras is True
    assert not caixa.isEnabled(), "com 'Só as letras' a caixinha não ficou cinza"
    QTest.mouseClick(caixa, Qt.LeftButton)                 # não dá para clicar
    _assentar()
    assert pagina.respeitar_gravuras_achadas is valor_antes and caixa.isChecked() is valor_antes
    _caixa_so_as_letras(tela).click()
    _assentar()
    assert pagina.misto_so_as_letras is False
    assert caixa.isEnabled(), "ao desligar 'Só as letras' a caixinha não voltou"
    assert caixa.isChecked() is valor_antes and pagina.respeitar_gravuras_achadas is valor_antes


def test_d587_so_as_letras_herdado_do_livro_tambem_deixa_cinza(janela, tmp_path):
    """D-587, com o "Só as letras" do LIVRO (o da janela do Automático; a página segue o livro):
    em Preto e branco a caixinha fica cinza; no Melhorar (onde o "Só as letras" não vale) e com o
    livro desligado, volta clicável. O valor guardado não muda."""
    tela = _depois_do_automatico(janela, tmp_path)
    projeto, pagina = janela.projeto, janela.projeto.paginas[0]
    _escolher(tela, PRETO_E_BRANCO)
    assert pagina.misto_so_as_letras is None               # a página segue o livro
    projeto.misto_so_as_letras = True
    tela.atualizar()
    _assentar()
    caixa = _caixa(tela)
    assert not caixa.isEnabled(), "com 'Só as letras' do livro a caixinha não ficou cinza"
    assert pagina.respeitar_gravuras_achadas is True and caixa.isChecked()
    _escolher(tela, MELHORAR)
    assert caixa.isEnabled(), "no Melhorar o 'Só as letras' não vale: a caixinha volta"
    _escolher(tela, PRETO_E_BRANCO)
    assert not caixa.isEnabled()
    projeto.misto_so_as_letras = False
    tela.atualizar()
    _assentar()
    assert caixa.isEnabled() and caixa.isChecked() and pagina.respeitar_gravuras_achadas is True
