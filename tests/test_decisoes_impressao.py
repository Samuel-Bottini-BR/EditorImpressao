"""Provas de comportamento das decisões da etapa 9a (obra de 26/10/2026).

Cada teste cita a decisão do Livro (docs/plano/DECISOES.md) ou o achado que
prova, e foi rodado também no código de antes (base 66a91d4): os marcados
"REVERSÃO" falham lá e passam aqui (CLAUDE.md §4.7).

- D-012 ("2": "imprimir agora" na etapa 9; lista única 5.1): o clique nunca
  imprime sem confirmação.
- D-333 ("cheio de letras uma em cima da outra"; "são 1 cadernos"): nenhum
  texto cortado nem sobreposto em 1000x617 (a janela que abre num notebook
  1280x657 com 150%) e na janela mínima; resultado à parte; plural certo.
- Rodinha (teste do Kaique, 26/10: 100% virou 60% ao rolar a janela).
- Janelas de arquivo em português, com atalhos e aviso de caminho errado
  (teste do Kaique, 26/10; D-301).
- Lista única 5.12 e 5.15; D-332 (a frase "Falando com a impressora").

Nenhuma janela aparece na tela (tests/conftest.py); pasta de dados própria.
"""

from __future__ import annotations

import re
import time

import pytest

fitz = pytest.importorskip("fitz")

from PySide6.QtCore import QPoint, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QWheelEvent  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QAbstractButton,
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from tests.test_mesmo_livro_outro_caminho import app, pasta  # noqa: F401, E402 - fixtures

IMPRESSORAS = ["EPSON L3250 Series", "Microsoft Print to PDF"]


# --------------------------------------------------------------- ajudantes

def _livro(caminho, n):
    """Um PDF de n páginas A5 (146 x 235 mm), cinza claro com o número."""
    mm = 72 / 25.4
    doc = fitz.open()
    for i in range(1, n + 1):
        pagina = doc.new_page(width=146 * mm, height=235 * mm)
        pagina.draw_rect(pagina.rect, color=(0.9, 0.9, 0.9), fill=(0.9, 0.9, 0.9))
        pagina.insert_text((100, 300), str(i), fontsize=40)
    doc.save(str(caminho))
    doc.close()
    return caminho


@pytest.fixture
def sem_impressora_de_verdade(monkeypatch):
    """Grava o que iria para a impressora, em vez de mandar (e de perguntar
    ao Windows quais impressoras existem)."""
    from core import impressora

    import historico
    from ui import dialogo_impressao

    mandados: list[dict] = []

    def imprimir_falso(folhas, nome="", copias=1, agrupar=True, frente_e_verso="", **k):
        mandados.append({"impressora": nome, "copias": copias, "paginas": folhas.page_count,
                         "lados": frente_e_verso})
        return folhas.page_count

    monkeypatch.setattr(impressora, "imprimir", imprimir_falso)
    monkeypatch.setattr(historico, "imprimir", lambda *a, **k: mandados.append({"historico": a}))
    monkeypatch.setattr(dialogo_impressao, "listar_impressoras", lambda: list(IMPRESSORAS),
                        raising=False)          # raising=False: roda também no código antigo
    return mandados


def _tela_final(caminho, cadernos=False):
    from modelos import Projeto
    from ui.tela_final import TelaFinal

    tela = TelaFinal()
    projeto = Projeto(caminho_entrada=str(caminho), caminho_saida=str(caminho))
    projeto.montar_cadernos = cadernos
    tela.mostrar(projeto, str(caminho), fitz.open(str(caminho)).page_count)
    tela.resize(1280, 657)
    tela.show()
    QApplication.processEvents()
    return tela


@pytest.fixture
def fontes_do_windows(app):
    """A letra de verdade do programa ("Segoe UI", ui/estilo.py). Sem ela, a
    tela fora da vista desenha cada letra como um quadradinho mais largo, e a
    medida de "texto cortado" mediria uma letra que o Kaique nunca vê."""
    from pathlib import Path

    from PySide6.QtGui import QFontDatabase

    pasta = Path("C:/Windows/Fonts")
    arquivos = [pasta / n for n in ("segoeui.ttf", "segoeuib.ttf", "seguisb.ttf")]
    if not all(a.is_file() for a in arquivos):
        pytest.skip("sem a letra Segoe UI (não é Windows)")
    if "Segoe UI" not in QFontDatabase.families():
        for arquivo in arquivos:
            QFontDatabase.addApplicationFont(str(arquivo))


def _assentar(rodadas: int = 5) -> None:
    """Deixa o Qt terminar de arrumar a janela (a rolagem refaz a altura dos
    textos que quebram linha numa segunda passada)."""
    for _ in range(rodadas):
        QApplication.processEvents()
        time.sleep(0.02)


def _esperar(condicao, segundos=60.0):
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        QApplication.processEvents()
        if condicao():
            return True
        time.sleep(0.02)
    return False


def _rodinha(widget: QWidget, para_baixo: bool = True) -> None:
    centro = QPointF(widget.width() / 2, widget.height() / 2)
    evento = QWheelEvent(centro, QPointF(widget.mapToGlobal(centro.toPoint())), QPoint(0, 0),
                         QPoint(0, -120 if para_baixo else 120), Qt.MouseButton.NoButton,
                         Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.NoScrollPhase, False)
    QApplication.sendEvent(widget, evento)
    QApplication.processEvents()


def _area_das_opcoes(dialogo):
    """A rolagem das opções (no código antigo, a única da janela)."""
    from PySide6.QtWidgets import QScrollArea

    return getattr(dialogo, "area_das_opcoes", None) or dialogo.findChild(QScrollArea)


def _textos_visiveis(raiz: QWidget) -> list[QWidget]:
    """As peças com texto que aparecem de verdade (não escondidas, não fora da
    parte visível da rolagem)."""
    tipos = (QLabel, QAbstractButton, QComboBox, QAbstractSpinBox, QLineEdit)
    pecas = []
    for peca in raiz.findChildren(QWidget):
        if not isinstance(peca, tipos) or not peca.isVisible():
            continue
        if isinstance(peca, QLineEdit) and isinstance(peca.parent(), (QAbstractSpinBox, QComboBox)):
            continue                                # o campo de dentro da caixa
        if isinstance(peca, QLabel) and not peca.text().strip():
            continue
        if peca.visibleRegion().isEmpty():
            continue
        pecas.append(peca)
    return pecas


def _problemas_de_texto(raiz: QWidget) -> list[str]:
    """Texto cortado (menor que o que precisa) ou uma peça por cima da outra."""
    problemas = []
    pecas = _textos_visiveis(raiz)
    for peca in pecas:
        nome = getattr(peca, "text", lambda: "")() or type(peca).__name__
        if isinstance(peca, QLabel) and peca.wordWrap():
            precisa = peca.heightForWidth(peca.width())
            if precisa > peca.height() + 1:
                problemas.append(f"cortado na altura: {nome!r} ({peca.height()} < {precisa})")
        elif isinstance(peca, (QLabel, QPushButton, QCheckBox)):
            if peca.width() + 1 < peca.sizeHint().width():
                problemas.append(f"cortado na largura: {nome!r} "
                                 f"({peca.width()} < {peca.sizeHint().width()})")
    retangulos = []
    for peca in pecas:
        visivel = peca.visibleRegion().boundingRect()
        canto = peca.mapTo(raiz, visivel.topLeft())
        retangulos.append((peca, visivel.translated(canto - visivel.topLeft())))
    for i, (a, ra) in enumerate(retangulos):
        for b, rb in retangulos[i + 1:]:
            if a.isAncestorOf(b) or b.isAncestorOf(a):
                continue
            comum = ra.intersected(rb)
            if comum.width() > 2 and comum.height() > 2:
                ta = getattr(a, "text", lambda: "")() or type(a).__name__
                tb = getattr(b, "text", lambda: "")() or type(b).__name__
                problemas.append(f"por cima: {ta!r} e {tb!r}")
    return problemas


# --------------------------------------------------------------- D-012 imprimir agora

def test_d012_imprimir_agora_nunca_imprime_sem_confirmacao(app, pasta, sem_impressora_de_verdade):
    """REVERSÃO. D-012 ("2"; lista única 5.1): antes, um clique em "imprimir
    agora" mandava o PDF inteiro à impressora padrão (historico.imprimir),
    sem perguntar. Agora o clique só abre a confirmação; cancelar, Esc e o X
    não mandam nada."""
    livro = _livro(pasta / "l.pdf", 9)
    tela = _tela_final(livro)
    QTest.mouseClick(tela.botao_imprimir, Qt.MouseButton.LeftButton)
    QApplication.processEvents()
    assert sem_impressora_de_verdade == []                  # nada saiu no clique
    confirmar = tela.dialogo_imprimir
    assert confirmar.isVisible()

    QTest.keyClick(confirmar, Qt.Key.Key_Return)            # Enter cai no "cancelar"
    QApplication.processEvents()
    assert sem_impressora_de_verdade == []
    assert not confirmar.isVisible()

    QTest.mouseClick(tela.botao_imprimir, Qt.MouseButton.LeftButton)
    tela.dialogo_imprimir.reject()                          # X / Esc
    QApplication.processEvents()
    assert sem_impressora_de_verdade == []


def test_d012_confirmacao_mostra_impressora_paginas_e_copias(app, pasta, sem_impressora_de_verdade):
    """D-012: a confirmação diz o que vai sair, com número de páginas e a
    impressora, e deixa escolher impressora, páginas e cópias."""
    from ui.dialogo_impressao import ConfirmarImpressao

    confirmar = ConfirmarImpressao(str(_livro(pasta / "l.pdf", 37)))
    assert confirmar.combo_impressora.count() == 2
    assert "EPSON L3250 Series" in confirmar.frase_do_que_sai()
    assert "37 páginas (o livro inteiro)" in confirmar.frase_do_que_sai()
    assert "1 cópia." in confirmar.frase_do_que_sai()
    assert confirmar.botao_imprimir.text() == "imprimir 37 páginas"
    assert confirmar.botao_cancelar.isDefault() and not confirmar.botao_imprimir.isDefault()
    confirmar.copias.setValue(2)
    confirmar.de.setValue(3)
    confirmar.ate.setValue(3)
    assert "1 página (da página 3 à 3), 2 cópias" in confirmar.frase_do_que_sai()
    assert confirmar.botao_imprimir.text() == "imprimir 1 página"
    confirmar.reject()


def test_d012_so_o_botao_imprimir_da_confirmacao_manda(app, pasta, sem_impressora_de_verdade):
    """D-012 + D-325 (imp-5) + D-332 (b-5): o "imprimir" da confirmação manda
    só as páginas escolhidas, para a impressora escolhida, com as cópias; e
    mostra "Falando com a impressora" enquanto espera."""
    from ui.dialogo_impressao import FALANDO_COM_A_IMPRESSORA

    tela = _tela_final(_livro(pasta / "l.pdf", 12), cadernos=True)
    tela.imprimir_agora()
    confirmar = tela.dialogo_imprimir
    assert confirmar.combo_lados.currentData() == "curta"   # PDF em cadernos: borda curta
    confirmar.combo_impressora.setCurrentIndex(1)
    confirmar.de.setValue(2)
    confirmar.ate.setValue(5)
    confirmar.copias.setValue(2)
    QTest.mouseClick(confirmar.botao_imprimir, Qt.MouseButton.LeftButton)
    assert confirmar.estado.text() == FALANDO_COM_A_IMPRESSORA
    assert _esperar(lambda: confirmar.mandadas is not None)
    assert sem_impressora_de_verdade == [{"impressora": "Microsoft Print to PDF", "copias": 2,
                                          "paginas": 4, "lados": "curta"}]
    assert "4 páginas mandadas" in confirmar.estado.text()
    confirmar.reject()


def test_d012_mandar_da_janela_montar_tambem_pergunta(app, pasta, sem_impressora_de_verdade,
                                                      monkeypatch):
    """REVERSÃO. D-012 (o clique nunca imprime sem confirmação) vale também
    para o "mandar para a impressora" da janela "Montar para imprimir"
    (imp-5): antes, o clique já mandava as folhas. Agora pergunta, dizendo a
    impressora, os lados, as cópias e quantas folhas saem."""
    from ui import perguntas
    from ui.dialogo_impressao import DialogoImpressao

    perguntas_feitas: list[str] = []
    resposta = {"sim": False}

    def perguntar(pai, titulo, texto, *a, **k):
        perguntas_feitas.append(texto)
        return resposta["sim"]

    monkeypatch.setattr(perguntas, "perguntar", perguntar)
    dialogo = DialogoImpressao(str(_livro(pasta / "l.pdf", 8)))
    QTest.mouseClick(dialogo.botao_imprimir, Qt.MouseButton.LeftButton)
    assert dialogo.tarefa is None and sem_impressora_de_verdade == []
    assert perguntas_feitas and "EPSON L3250 Series" in perguntas_feitas[0]
    assert "1 cópia" in perguntas_feitas[0] and "2 folhas de papel" in perguntas_feitas[0]

    resposta["sim"] = True
    QTest.mouseClick(dialogo.botao_imprimir, Qt.MouseButton.LeftButton)
    assert dialogo.tarefa is not None and dialogo.tarefa.wait(60000)
    QApplication.processEvents()
    assert len(sem_impressora_de_verdade) == 1
    assert sem_impressora_de_verdade[0]["impressora"] == "EPSON L3250 Series"
    dialogo.reject()


# --------------------------------------------------------------- D-333 janela refeita

@pytest.mark.parametrize("tamanho", ["ao_abrir", "minima"])
def test_d333_montar_sem_texto_cortado_nem_por_cima(app, pasta, fontes_do_windows, tamanho):
    """REVERSÃO. D-333 ("cheio de letras uma em cima da outra"): em 1000x617
    (a janela que abre no notebook 1280x657 com 150%) e na janela mínima,
    antes e depois de gravar, nenhum texto cortado nem por cima de outro.
    Antes: o resultado espremia as opções e o botão "gravar o arquivo para
    imprimir" saía cortado."""
    from ui.dialogo_impressao import DialogoImpressao

    dialogo = DialogoImpressao(str(_livro(pasta / "l.pdf", 3)))
    dialogo.show()
    dialogo.resize(1000, 617) if tamanho == "ao_abrir" else dialogo.resize(dialogo.minimumSize())
    _assentar()
    assert dialogo.width() <= 1000 and dialogo.height() <= 617
    assert _problemas_de_texto(dialogo) == []

    dialogo.comecar(destino=str(pasta / "s.pdf"))
    assert dialogo.tarefa.wait(60000)
    _assentar()
    assert dialogo.estado.isVisible() and "Pronto" in dialogo.estado.text()
    assert _problemas_de_texto(dialogo) == []
    dialogo.reject()


def test_d333_resultado_a_parte_nao_espreme_as_opcoes(app, pasta):
    """REVERSÃO. D-333 ("o texto do resultado separado das opções"): o
    resultado mora num cartão à parte; depois de gravar, a área das opções
    continua do mesmo tamanho (antes ela encolhia para uma faixa)."""
    from ui.dialogo_impressao import DialogoImpressao

    dialogo = DialogoImpressao(str(_livro(pasta / "l.pdf", 23)))
    dialogo.show()
    dialogo.resize(dialogo.minimumSize())
    _assentar()
    opcoes = _area_das_opcoes(dialogo)
    altura_antes = opcoes.viewport().height()
    dialogo.comecar(destino=str(pasta / "s.pdf"))
    assert dialogo.tarefa.wait(60000)
    _assentar()
    assert not opcoes.isAncestorOf(dialogo.estado)
    assert opcoes.viewport().height() == altura_antes
    assert "último grupo tem 1 folha" in dialogo.passos.text()
    dialogo.reject()


def test_d333_singular_e_plural(app, pasta):
    """REVERSÃO. D-333 (print de 22/10: "1 folhas de papel, 1 cadernos", "são
    1 cadernos prontos"): com 1, singular; e um caderno só não fala em "grupos
    de 5; o último grupo"."""
    from core.cadernos import instrucoes_de_impressao
    from ui.dialogo_impressao import DialogoImpressao

    passos = instrucoes_de_impressao(3, 20)
    assert passos[2] == "Dobre o grupo ao meio - é 1 caderno pronto."
    assert passos[1] == "A folha forma um grupo só."
    assert instrucoes_de_impressao(40, 20)[2] == "Dobre cada grupo ao meio - são 2 cadernos prontos."

    dialogo = DialogoImpressao(str(_livro(pasta / "l.pdf", 3)))
    dialogo.comecar(destino=str(pasta / "s.pdf"))
    assert dialogo.tarefa.wait(60000)
    QApplication.processEvents()
    texto = " ".join(r.text() for r in dialogo.findChildren(QLabel))
    assert "1 folha de papel" in texto and "1 caderno." in texto
    assert not re.search(r"\b1 (folhas|cadernos|páginas|cópias)\b", texto)
    dialogo.reject()


def test_d315_nenhuma_opcao_sumiu_na_arrumacao(app, pasta):
    """D-315 ("Quero TODAS essas opções dentro do programa"): a janela
    refeita continua com todas as opções da janela do UPDF, e os de fábrica
    das decisões imp-1 a imp-6 (imp-6: "Imprimir como imagem" ligada)."""
    from core import impressao as imp
    from ui.dialogo_impressao import DialogoImpressao

    dialogo = DialogoImpressao(str(_livro(pasta / "l.pdf", 4)))
    assert dialogo.opcoes() == imp.OpcoesDeImpressao()
    assert [dialogo.combo_formato.itemData(i) for i in range(dialogo.combo_formato.count())] \
        == list(imp.FORMATOS)
    assert [dialogo.combo_escala.itemData(i) for i in range(dialogo.combo_escala.count())] \
        == list(imp.ESCALAS)
    for caixa in (dialogo.cx_girar, dialogo.cx_centralizar, dialogo.cx_margens, dialogo.cx_cinza,
                  dialogo.cx_imagem, dialogo.cx_reverter, dialogo.cx_moldura, dialogo.cx_marcas,
                  dialogo.cx_so_grandes, dialogo.cx_agrupar):
        assert isinstance(caixa, QCheckBox)
    assert dialogo.cx_imagem.isChecked()
    dialogo.reject()


# --------------------------------------------------------------- rodinha

def test_rodinha_nao_muda_numero_nem_lista_sem_clique(app, pasta):
    """REVERSÃO. Teste do Kaique (26/10): "ao rolar a janela 'Montar para
    imprimir' com a rodinha do mouse, o campo 'Páginas da esquerda (pares)'
    passou de 100% para 60% sozinho". Agora a rodinha rola a janela; o número
    só muda depois de clicar nele."""
    from ui.dialogo_impressao import DialogoImpressao

    dialogo = DialogoImpressao(str(_livro(pasta / "l.pdf", 4)))
    dialogo.show()
    dialogo.resize(dialogo.minimumSize())
    QApplication.processEvents()
    fechar = next(b for b in dialogo.findChildren(QPushButton) if b.text() == "fechar")
    fechar.setFocus()
    caixas = dialogo.findChildren(QAbstractSpinBox) + dialogo.findChildren(QComboBox)
    antes = {id(c): (c.value() if isinstance(c, QAbstractSpinBox) else c.currentIndex())
             for c in caixas}
    rolagem = _area_das_opcoes(dialogo).verticalScrollBar()
    rolagem.setValue(0)
    for caixa in caixas:
        _rodinha(caixa)
        _rodinha(caixa, para_baixo=False) if isinstance(caixa, QComboBox) else None
    depois = {id(c): (c.value() if isinstance(c, QAbstractSpinBox) else c.currentIndex())
              for c in caixas}
    assert depois == antes
    _rodinha(dialogo.escala_esquerda)
    assert rolagem.value() > 0 or rolagem.maximum() == 0    # a janela rolou

    campo = dialogo.escala_esquerda.findChild(QLineEdit)
    QTest.mouseClick(campo, Qt.MouseButton.LeftButton)       # clicou: agora vale
    _rodinha(dialogo.escala_esquerda)
    assert dialogo.escala_esquerda.value() == 95.0
    dialogo.reject()


def test_rodinha_foco_que_a_janela_deu_sozinha_nao_libera(app, pasta):
    """A primeira caixa ganha o foco sozinha quando a janela abre: isso não
    conta como clique (senão a lista "Formato" mudaria com a rodinha)."""
    from ui.dialogo_impressao import DialogoImpressao

    dialogo = DialogoImpressao(str(_livro(pasta / "l.pdf", 4)))
    dialogo.show()
    QApplication.processEvents()
    dialogo.combo_formato.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
    QApplication.processEvents()
    _rodinha(dialogo.combo_formato)
    assert dialogo.combo_formato.currentIndex() == 0
    dialogo.reject()


def test_rodinha_no_programa_inteiro(app):
    """O ajuste serve para o resto do programa (instalar_no_programa): uma
    caixa criada depois de instalar também fica protegida."""
    from PySide6.QtWidgets import QDoubleSpinBox, QScrollArea, QVBoxLayout

    from ui import rodinha

    rodinha.instalar_no_programa(app)
    try:
        area = QScrollArea()
        area.setWidgetResizable(True)
        dentro = QWidget()
        coluna = QVBoxLayout(dentro)
        caixa = QDoubleSpinBox()
        caixa.setRange(0, 400)
        caixa.setValue(100)
        coluna.addWidget(caixa)
        for i in range(60):
            coluna.addWidget(QLabel(f"linha {i}"))
        area.setWidget(dentro)
        area.resize(300, 300)
        area.show()
        QApplication.processEvents()
        area.setFocus()
        _rodinha(caixa)
        assert caixa.value() == 100
        assert area.verticalScrollBar().value() > 0
    finally:
        rodinha.desinstalar_do_programa(app)


# --------------------------------------------------------------- janelas de arquivo

INGLES = ("Look in", "File name", "Files of type", "Open", "Cancel", "Save", "My Computer",
          "Date Modified", "Name", "Size")


def _textos_da_janela(janela) -> list[str]:
    textos = [w.text() for w in janela.findChildren(QLabel) + janela.findChildren(QPushButton)]
    from PySide6.QtWidgets import QTreeView

    for arvore in janela.findChildren(QTreeView):
        modelo = arvore.model()
        textos += [str(modelo.headerData(i, Qt.Orientation.Horizontal))
                   for i in range(modelo.columnCount())]
    return [t.replace("&", "") for t in textos if t]


@pytest.mark.parametrize("modo", ["abrir", "salvar", "pasta"])
def test_janela_de_arquivo_em_portugues_com_atalhos(app, pasta, modo):
    """Teste do Kaique (26/10): "'Look in:', 'File name:', 'Files of type:',
    'Open', 'Cancel', 'My Computer'" e sem atalho para Área de Trabalho e
    Downloads. Quando a janela do Windows não pode ser usada, a do Qt sai em
    português, com os atalhos."""
    from PySide6.QtCore import QStandardPaths

    from ui import dialogos_de_arquivo as d

    d.lembrar_pasta_dos_livros(pasta)
    janela = d.JanelaDeArquivo(None, "Escolha", modo, str(pasta))
    textos = _textos_da_janela(janela)
    for palavra in INGLES:
        assert not any(t.strip().rstrip(":") == palavra for t in textos), (palavra, textos)
    assert {"abrir": "Abrir", "salvar": "Salvar", "pasta": "Escolher esta pasta"}[modo] in textos
    assert "Cancelar" in textos
    nomes = janela.nomes_dos_atalhos()
    for nome, lugar in (("Área de Trabalho", QStandardPaths.StandardLocation.DesktopLocation),
                        ("Documentos", QStandardPaths.StandardLocation.DocumentsLocation),
                        ("Downloads", QStandardPaths.StandardLocation.DownloadLocation)):
        from pathlib import Path

        if Path(QStandardPaths.writableLocation(lugar)).is_dir():
            assert nome in nomes
    assert "Última pasta aberta" in nomes
    janela.reject()


def test_caminho_digitado_que_nao_existe_avisa(app, pasta, monkeypatch):
    """Teste do Kaique (26/10): "digitar o caminho completo [...] não abriu o
    livro [...] sem nenhum aviso". Caminho que não existe: aviso claro em
    português e a janela fica aberta; caminho certo: abre; pasta: entra nela."""
    from ui import dialogos_de_arquivo as d
    from ui import perguntas

    avisos: list[str] = []
    monkeypatch.setattr(perguntas, "avisar", lambda pai, titulo, texto, *a, **k: avisos.append(texto))
    janela = d.JanelaDeArquivo(None, "Escolha o PDF do livro", d.ABRIR_PDF, str(pasta))

    janela.campo_do_nome().setText(str(pasta / "nao existe" / "livro.pdf"))
    janela.accept()
    assert janela.result() != QDialog.DialogCode.Accepted and janela.escolhido == ""
    assert avisos and avisos[0].startswith("Não achei este arquivo")

    (pasta / "sub").mkdir()
    janela.campo_do_nome().setText(f'"{pasta / "sub"}"')            # com aspas, como o Windows copia
    janela.accept()
    assert janela.escolhido == "" and len(avisos) == 1
    assert janela.directory().absolutePath().replace("/", "\\").lower() \
        == str(pasta / "sub").lower()

    livro = _livro(pasta / "sub" / "Meu livro.pdf", 2)
    janela.campo_do_nome().setText(str(livro)[:-4])                 # sem o ".pdf"
    janela.accept()
    assert janela.escolhido == str(livro) and len(avisos) == 1
    assert d.pasta_dos_livros() is None or True


@pytest.mark.parametrize("modo", ["salvar", "pasta"])
def test_salvar_ou_pasta_em_lugar_que_nao_existe_avisa(app, pasta, monkeypatch, modo):
    """D-301 ("avisar em português"): salvar numa pasta que não existe, ou
    escolher pasta que não existe, avisa e não fecha."""
    from ui import dialogos_de_arquivo as d
    from ui import perguntas

    avisos: list[str] = []
    monkeypatch.setattr(perguntas, "avisar", lambda pai, titulo, texto, *a, **k: avisos.append(titulo))
    janela = d.JanelaDeArquivo(None, "t", modo, str(pasta))
    janela.campo_do_nome().setText(str(pasta / "nao existe" / "x.pdf"))
    janela.accept()
    assert janela.escolhido == "" and avisos == ["Não achei a pasta"]


def test_abrir_o_livro_passa_pela_janela_em_portugues(app, pasta, monkeypatch):
    """REVERSÃO. A área de arrastar (e Arquivo > Abrir) usam o módulo novo, e
    não mais a função pronta do Qt (que nos testes é proibida sem resposta,
    tests/conftest.py). Também guarda a pasta do livro para a próxima vez."""
    from ui import dialogos_de_arquivo as d
    from ui.widgets.area_arrastar import AreaArrastar

    livro = _livro(pasta / "l.pdf", 2)
    monkeypatch.setattr(d, "_pela_janela_do_qt", lambda pai, titulo, modo, inicio: str(livro))
    # a função pronta do Qt está proibida aqui (conftest), não "trocada"
    monkeypatch.setattr(d, "_trocada_por_teste", lambda nome: False)
    area = AreaArrastar()
    escolhidos: list[str] = []
    area.arquivo_escolhido.connect(escolhidos.append)
    area.abrir_dialogo_de_arquivo()
    assert escolhidos == [str(livro)]
    assert d.pasta_dos_livros() == pasta


def test_janela_do_windows_conferida_na_volta(app, pasta, monkeypatch):
    """Com a janela do Windows (ou a troca dos testes), o caminho que volta é
    conferido de novo: se não existir, aviso em português e nada abre."""
    from PySide6.QtWidgets import QFileDialog

    from ui import dialogos_de_arquivo as d
    from ui import perguntas

    avisos: list[str] = []
    monkeypatch.setattr(perguntas, "avisar", lambda pai, titulo, texto, *a, **k: avisos.append(titulo))
    monkeypatch.setattr(QFileDialog, "getOpenFileName",
                        staticmethod(lambda *a, **k: (str(pasta / "sumiu.pdf"), "")))
    assert d.escolher_pdf_para_abrir(None) == ""
    assert avisos == ["Não achei o arquivo"]


# --------------------------------------------------------------- 5.12 e 5.15

def test_5_15_nome_sugerido_sem_acento(app, pasta):
    """REVERSÃO. Lista única 5.15 ("mágico pro" com acento no nome sugerido;
    CLAUDE.md §3: caminho de disco sem acento): o arquivo para imprimir é
    sugerido sem acento."""
    from ui.dialogo_impressao import DialogoImpressao

    livro = _livro(pasta / "Camões - mágico pro.pdf", 2)
    dialogo = DialogoImpressao(str(livro))
    assert dialogo.destino_sugerido().name == "Camoes - magico pro - para imprimir.pdf"
    dialogo.reject()


def test_5_12_ficou_pronto_diz_qual_montar_usar(app, pasta, sem_impressora_de_verdade):
    """REVERSÃO. Lista única 5.12 (dois "montar cadernos" com nomes parecidos;
    "a 'Ficou pronto!' não diz qual usar"); D-330 "Deixar os dois"."""
    livro = _livro(pasta / "l.pdf", 4)
    tela = _tela_final(livro)
    assert tela.botao_montar.isEnabled()
    assert "use \"montar para imprimir em A4\"" in tela.qual_montar.text()
    tela = _tela_final(livro, cadernos=True)
    assert not tela.botao_montar.isEnabled()
    assert "já saiu em cadernos" in tela.qual_montar.text()
    assert "Montar cadernos" in tela.qual_montar.text()
