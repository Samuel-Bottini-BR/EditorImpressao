"""Testes de reversão dos achados do verificador clicando de 03/11/2026 no Dividir e na janela
do Automático (relatório: .claude/worktrees/verif-03-11/relatorios/verif-03-11/relatorio.md,
ressalvas dos testes 1 e 2), consertados no ramo `dividir-ajustes-2026-11-03`.

D-605 (Samuel, 03/11/2026): "A partir de agora, nenhuma função nova, ou nova escolha dentro do
programa pode alterar o que já está escolhido e testado, coisas novas não podem criar novos
problemas". Cada conserto aqui desfaz um problema que o conserto de 03/11 (D-602) deixou, sem
mudar o que já estava escolhido.

- Seta → depois da lista "motor de corte" (ressalva 5 do teste 1).
- A tira de miniaturas depois do Ctrl+Z (ressalva 4 do teste 1, print t1-22).
- A coluna do meio da etapa 6 cortada em 1536 x 824 (ressalva 3 do teste 2, print t2m-02).

Os itens D-606 e D-607 têm a prova nos arquivos de decisões (tests/test_decisoes_dividir.py e
tests/test_decisoes_automatico.py). Todos falham no código de antes (75ed04af).
"""

from __future__ import annotations

import time

import numpy as np
import pytest

pytest.importorskip("fitz")
pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixtures app, pasta, janela)
    _pagina,
    _pdf,
    app,
    janela,
    pasta,
)


def _assentar(vezes: int = 5) -> None:
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


def _aberto() -> np.ndarray:
    return np.concatenate([_pagina(600), _pagina(760)], axis=1)


def _no_dividir(janela, tmp_path, folhas: int):
    from ui.tela_conferir import ABA_CORTE

    janela.show()
    janela.activateWindow()
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", [_aberto() for _ in range(folhas)]))
    tela = janela.tela_conferir
    tela.escolher_ferramenta("dividir")
    tela._ir_para(0)
    assert tela.aba_atual == ABA_CORTE
    _assentar()
    return tela


# --- seta → depois da lista "motor de corte" -------------------------------------------------

def test_reversao_seta_troca_de_folha_depois_de_escolher_o_motor(janela, tmp_path):
    """Achado do verificador clicando (03/11/2026, ressalva 5 do teste 1): "Depois de usar a
    lista "motor de corte", a seta do teclado (→) não trocou de folha. O teclado ficou com a
    lista." Agora a lista não pega o teclado (como as outras listas da área de trabalho, D-021
    e etapa 9b-1: "o teclado fica com a página"): abrir a lista com o mouse, escolher o outro
    motor, e a seta → vai à folha seguinte, como antes de usar a lista.
    No código de antes (75ed04af) o clique dava o teclado à lista: este teste falha lá."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    tela = _no_dividir(janela, tmp_path, 3)
    # como o verificador: o teclado com a janela (clicar nas miniaturas e na página não
    # dá o teclado a nenhum botão); antes de usar a lista, a seta anda
    if QApplication.focusWidget() is not None:
        QApplication.focusWidget().clearFocus()
    _assentar()
    QTest.keyClick(QApplication.focusWidget() or janela, Qt.Key_Right)
    _assentar()
    assert tela.indice_folha == 1, "antes de usar a lista, a seta → anda"
    QTest.keyClick(QApplication.focusWidget() or janela, Qt.Key_Left)
    _assentar()
    assert tela.indice_folha == 0
    combo = tela.combo_jeito_da_folha
    antes = combo.currentData()
    QTest.mouseClick(combo, Qt.LeftButton)              # abre a lista
    _assentar()
    vista = combo.view()
    outro = next(i for i in range(combo.count()) if combo.itemData(i) != antes)
    QTest.mouseClick(vista.viewport(), Qt.LeftButton, Qt.NoModifier,
                     vista.visualRect(vista.model().index(outro, 0)).center())
    _assentar()
    if vista.window().isVisible():                     # o offscreen às vezes não fecha
        combo.hidePopup()
        combo.setCurrentIndex(outro)
    _assentar()
    assert combo.currentData() != antes, "o motor foi trocado"
    # o teclado de volta na janela grande (a lista aberta é outra janela): quem fica com ele é
    # o "foco" da janela (no offscreen o foco da aplicação fica na lista escondida)
    assert janela.focusWidget() is not combo, "a lista não fica com o teclado"
    QTest.keyClick(janela.focusWidget() or janela, Qt.Key_Right)
    _assentar()
    assert tela.indice_folha == 1, "a seta → foi à folha seguinte"
    QTest.keyClick(janela.focusWidget() or janela, Qt.Key_Left)
    _assentar()
    assert tela.indice_folha == 0, "e a ← volta"


# --- a tira mostra a folha da vez depois do Ctrl+Z ---------------------------------------------

def _a_vista_na_tira(tela) -> bool:
    """A miniatura escolhida (borda grossa) está dentro da parte visível da tira?"""
    tira = tela.tira
    escolhidas = [m for m in tira._miniaturas if m.selecionada]
    assert len(escolhidas) == 1
    mini = escolhidas[0]
    vista = tira.rolagem.viewport()
    canto = mini.mapTo(vista, mini.rect().topLeft())
    return (0 <= canto.x() and canto.x() + mini.width() <= vista.width()
            and 0 <= canto.y() and canto.y() + mini.height() <= vista.height())


def test_reversao_tira_mostra_a_folha_da_vez_depois_do_ctrl_z(janela, tmp_path):
    """Achado do verificador clicando (03/11/2026, ressalva 4 do teste 1, print t1-22): "Depois
    do Ctrl+Z a tira voltou para o começo (folhas 1 a 16), mas a folha da vez era a 60: a
    miniatura escolhida ficou fora da vista." CAUSA: o desfazer remonta a tira (a lista de
    páginas mudou) e logo depois pede para rolar até a escolhida, mas os quadros novos ainda
    não estão no lugar (posição 0): a tira rolava para o começo. Agora, depois de remontar, a
    tira rola até a escolhida quando os quadros já estão no lugar. Vale para o desfazer e o
    refazer. No código de antes (75ed04af) falha (no programa de teste, o desfazer às vezes é
    acertado por um redesenho que chega depois - na janela do verificador não foi -; o refazer
    falha sempre)."""
    tela = _no_dividir(janela, tmp_path, 40)
    janela.resize(1536, 824)
    _assentar()
    projeto = janela.projeto
    tela.botao_dividir_todas.click()
    _esperar(lambda: all(f.dividir for f in projeto.folhas), 120, "dividir todas")
    _assentar(10)
    tela._ir_para(19)                                    # a folha 20, longe do começo
    _assentar(10)
    assert _a_vista_na_tira(tela), "antes do Ctrl+Z a escolhida está à vista"
    tela.desfazer()                                       # Ctrl+Z do "dividir todas"
    _assentar(10)
    assert not any(f.dividir for f in projeto.folhas)
    assert tela.indice_folha == 19
    assert _a_vista_na_tira(tela), "depois do Ctrl+Z a tira mostra a folha da vez"
    assert tela.tira.rolagem.horizontalScrollBar().value() > 0
    tela.refazer()                                        # e o refazer também
    _assentar(10)
    assert all(f.dividir for f in projeto.folhas) and tela.indice_folha == 19
    assert _a_vista_na_tira(tela), "depois do refazer a tira mostra a folha da vez"


# --- a etapa 6 inteira na janela do Automático da tela do Samuel ----------------------------------

def test_reversao_margens_iguais_inteira_na_janela_do_automatico_1536x824(app):
    """Achado do verificador clicando (03/11/2026, ressalva 3 do teste 2, print t2m-02; o print
    a-51 do Samuel mostra o mesmo): "Na janela grande do Automático, na etapa 6, a coluna do meio
    fica cortada à direita nesse tamanho de janela: "5,0 mm" e "no meio" aparecem pela metade,
    com barra de rolagem". A janela principal do tamanho da dele (1536 x 824) abre a do
    Automático com 92% (1413 x 758): na janela de verdade a coluna do meio tem 674 pontos e a
    linha "página menor, de cima a baixo: [no meio] de um lado ao outro: [no meio]" pedia 732.
    Agora a linha dobra em duas quando não cabe; textos, controles e a ordem são os mesmos.
    O teste não depende das letras da máquina: a coluna é posta numa largura em que as duas
    linhas das margens cabem e a linha do alinhamento inteira não (como na janela dele), medida
    pelo próprio Qt. No código de antes (75ed04af) aparece a rolagem de lado: falha lá."""
    from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QLabel

    from core import automatico as A
    from ui.automatico import EstadoDoAutomatico, PainelDeOpcoes

    painel = PainelDeOpcoes(EstadoDoAutomatico())
    rolagem = painel.paginas_das_etapas[A.MARGENS]
    dentro = rolagem.widget()
    rotulos = {r.text(): r for r in dentro.findChildren(QLabel)}
    larg = lambda w: w.minimumSizeHint().width()          # noqa: E731
    espaco, margens = 6, 36
    caixas = [painel.margens_mm[k] for k in ("esquerda", "cima", "direita", "baixo")]
    duas_linhas = max(larg(rotulos["margem esquerda:"]) + larg(caixas[0])
                      + larg(rotulos["margem em cima:"]) + larg(caixas[1]),
                      larg(rotulos["margem direita:"]) + larg(caixas[2])
                      + larg(rotulos["margem embaixo:"]) + larg(caixas[3])) + 3 * espaco
    alinhamento = (larg(rotulos["página menor, de cima a baixo:"]) + larg(painel.combo_vertical)
                   + larg(rotulos["de um lado ao outro:"]) + larg(painel.combo_horizontal)
                   + 3 * espaco)
    largura = margens + max(duas_linhas, alinhamento - 80)      # na janela dele faltavam 58
    assert largura < margens + alinhamento, "a largura da janela dele: o alinhamento não cabe"
    # a coluna do meio da janela grande (a pilha das etapas), aberta na etapa 6
    painel.mostrar_etapa(A.MARGENS)
    painel.pilha.resize(largura + rolagem.verticalScrollBar().sizeHint().width(), 900)
    painel.pilha.show()
    _assentar(10)
    assert rolagem.horizontalScrollBar().maximum() == 0, "a coluna do meio cabe sem rolar de lado"
    vista = rolagem.viewport()
    textos = []
    for w in dentro.findChildren(QLabel) + dentro.findChildren(QComboBox)             + dentro.findChildren(QDoubleSpinBox):
        if not w.isVisibleTo(painel.pilha):
            continue
        canto = w.mapTo(vista, w.rect().topLeft())
        assert canto.x() >= 0 and canto.x() + w.width() <= vista.width(), w
        assert w.width() >= w.minimumSizeHint().width(), w
        if isinstance(w, QLabel) and w.text().endswith(":"):
            textos.append((canto.y(), canto.x(), w.text()))
    # os mesmos textos de sempre, na mesma ordem de leitura
    assert [t for _y, _x, t in sorted(textos)] == [
        "margem esquerda:", "margem em cima:", "margem direita:", "margem embaixo:",
        "página menor, de cima a baixo:", "de um lado ao outro:"]
    painel.pilha.close()


def test_margens_iguais_onde_cabe_fica_numa_linha_como_era(app):
    """D-605 ("nenhuma [...] nova escolha [...] pode alterar o que já está escolhido e
    testado"): onde a linha do alinhamento cabe (a janela maior), ela fica como era, numa
    linha só: "página menor, de cima a baixo:" e "de um lado ao outro:" lado a lado."""
    from PySide6.QtWidgets import QLabel

    from core import automatico as A
    from ui.automatico import EstadoDoAutomatico, PainelDeOpcoes

    painel = PainelDeOpcoes(EstadoDoAutomatico())
    painel.mostrar_etapa(A.MARGENS)
    linha = painel.linha_do_alinhamento
    painel.pilha.resize(36 + linha.largura_numa_linha() + 80, 900)
    painel.pilha.show()
    _assentar(10)
    rotulos = {r.text(): r for r in linha.findChildren(QLabel)}
    a, b = rotulos["página menor, de cima a baixo:"], rotulos["de um lado ao outro:"]
    assert not linha.dobrada
    assert a.mapTo(linha, a.rect().topLeft()).y() == b.mapTo(linha, b.rect().topLeft()).y()
    assert b.mapTo(linha, b.rect().topLeft()).x() > painel.combo_vertical.mapTo(
        linha, painel.combo_vertical.rect().topLeft()).x(), "a ordem de sempre"
    painel.pilha.close()


# --- o refazer devolve os "Parece em branco" (D-497, D-605) ---------------------------------------

def _branca_e_escrita() -> np.ndarray:
    """Livro aberto com a página da esquerda em branco (o verso de uma folha de rosto, como
    as folhas 2, 3, 7, 8, 62, 63 e 69 do Gradus Primus) e a da direita escrita."""
    branca = np.full_like(_pagina(600), 235)
    return np.concatenate([branca, _pagina(600)], axis=1)


def _em_branco_medido(tela) -> None:
    """Espera a medida do "Parece em branco", que roda por trás."""
    _assentar(5)
    tarefa = getattr(tela, "_tarefa_do_em_branco", None)
    if tarefa is not None:
        tarefa.wait(60000)
    _assentar(10)


def _avisos_das_paginas(projeto) -> list:
    return [(p.folha, p.metade, sorted(p.alertas)) for p in projeto.paginas]


@pytest.mark.parametrize("como", ["dividir todas", "dividir esta"])
def test_reversao_refazer_devolve_o_parece_em_branco(janela, tmp_path, como):
    """Defeito anotado na entrega de 03/11/2026 (Gradus Primus): "dividir todas" → 7 "Parece em
    branco" (folhas 2, 3, 7, 8, 62, 63, 69); Ctrl+Z; Ctrl+Y (refazer) → 0 com dúvida. Samuel:
    "ele burlou a regra, colocou um defeito novo, concerta isso ai". Provado: já acontecia em
    75ed04af (antes destes ajustes) e também com "dividir esta" - vem da etapa 7 (27/10), quando a
    medida do em branco entrou: a ação guarda as páginas de ANTES da medida por trás, e o
    refazer as devolvia sem medir. Agora o refazer mede como o _registrar (D-497) e as páginas
    e os avisos ficam exatamente como depois da ação; o Ctrl+Z continua como estava; Ctrl+Z e
    Ctrl+Y de novo, também. No código de antes (75ed04af e abd8cd0a) falha."""
    from core import analise
    from core import avisos

    janela.show()
    janela.abrir_livro(_pdf(tmp_path / "branca.pdf", [_aberto(), _branca_e_escrita()]))
    tela = janela.tela_conferir
    projeto = janela.projeto
    tela.escolher_ferramenta("dividir")
    tela._ir_para(1)
    _assentar()
    ao_abrir = _avisos_das_paginas(projeto)
    if como == "dividir todas":
        tela.botao_dividir_todas.click()
        _esperar(lambda: all(f.dividir for f in projeto.folhas), 60, "dividir todas")
    else:
        tela.botao_nao_dividir.click()                     # "dividir esta" na folha 2
        assert projeto.folhas[1].dividir
    _em_branco_medido(tela)
    depois = _avisos_das_paginas(projeto)
    esquerda = next(p for p in projeto.paginas if p.folha == 1 and p.metade == "esquerda")
    assert analise.EM_BRANCO in esquerda.alertas, "a metade branca ganha o aviso (D-497)"
    duvidas = avisos.quantas_com_duvida(projeto)
    assert duvidas >= 1
    for _ in range(2):                                      # Ctrl+Z e Ctrl+Y, duas vezes
        tela.desfazer()
        _em_branco_medido(tela)
        assert _avisos_das_paginas(projeto) == ao_abrir, "o Ctrl+Z continua como estava"
        tela.refazer()
        _em_branco_medido(tela)
        assert _avisos_das_paginas(projeto) == depois, "o refazer devolve os avisos"
        assert avisos.quantas_com_duvida(projeto) == duvidas


# --- D-608: depois de clicar num botão do painel, as setas continuam passando de página ------------

def _botao_do_painel(tela, aba: str, texto: str):
    from PySide6.QtWidgets import QPushButton

    painel = tela.propriedades_das_abas[aba]
    return next(b for b in painel.findChildren(QPushButton) if b.text() == texto)


def _tecla_onde_o_teclado_esta(janela, tecla) -> None:
    """A tecla vai a quem tem o teclado na janela (o "foco" dela), como no Windows."""
    from PySide6.QtTest import QTest

    QTest.keyClick(janela.focusWidget() or janela, tecla)
    _assentar()


def test_reversao_d608_seta_depois_de_clicar_dividir_esta(janela, tmp_path):
    """D-608 (03/11/2026). Pergunta: "Quer que, depois de clicar num botão do painel, as setas
    continuem passando de página, em todas as ferramentas? As caixas de número continuam como
    estão." → "ok". Achado (entrega de 03/11, ressalva do item 3): depois de clicar em "dividir
    esta", o botão ficava com o teclado e a seta → passava de um botão a outro em vez de
    trocar de folha. Agora: clicar "dividir esta" (o botão funciona: divide) e a seta → vai à
    folha seguinte; ← volta; Page Down, Home e End também (D-021). No código de antes
    (75ed04af) falha."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QAbstractButton

    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir(janela, tmp_path, 12)
    _esperar(lambda: not tela.visualizadores[ABA_CORTE].lendo_a_linha, motivo="a linha")
    botao = tela.botao_nao_dividir
    assert botao.text() == "dividir esta"
    QTest.mouseClick(botao, Qt.LeftButton)
    _assentar()
    assert janela.projeto.folhas[0].dividir, "o botão funciona"
    assert isinstance(janela.focusWidget(), QAbstractButton), "o clique deu o teclado ao botão"
    _tecla_onde_o_teclado_esta(janela, Qt.Key_Right)
    assert tela.indice_pagina == 1 and tela.indice_folha == 0, "→ anda (metade direita, D-601)"
    _tecla_onde_o_teclado_esta(janela, Qt.Key_Right)
    assert tela.indice_folha == 1, "→ foi à folha seguinte"
    _tecla_onde_o_teclado_esta(janela, Qt.Key_Left)
    assert tela.indice_folha == 0
    _tecla_onde_o_teclado_esta(janela, Qt.Key_End)
    assert tela.indice_folha == 11, "End: a última"
    _tecla_onde_o_teclado_esta(janela, Qt.Key_Home)
    assert tela.indice_folha == 0, "Home: a primeira"
    _tecla_onde_o_teclado_esta(janela, Qt.Key_PageDown)
    assert tela.indice_atual > 0, "Page Down anda (D-021)"


def test_reversao_d608_seta_depois_de_clicar_nao_cortar_esta(janela, tmp_path):
    """D-608 "em todas as ferramentas": no Cortar, depois de clicar "não cortar esta", a seta
    → passa à página seguinte. No código de antes (75ed04af) falha."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from ui.tela_conferir import ABA_BORDAS, FERRAMENTA_CORTAR

    janela.show()
    janela.activateWindow()
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", [_pagina() for _ in range(4)]))
    tela = janela.tela_conferir
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    tela.ir_para_pagina(0)
    _assentar()
    botao = _botao_do_painel(tela, ABA_BORDAS, "não cortar esta")
    QTest.mouseClick(botao, Qt.LeftButton)
    _assentar()
    _tecla_onde_o_teclado_esta(janela, Qt.Key_Right)
    assert tela.indice_pagina == 1, "→ foi à página seguinte"
    _tecla_onde_o_teclado_esta(janela, Qt.Key_Left)
    assert tela.indice_pagina == 0


def test_d608_caixa_de_numero_do_angulo_continua_com_as_setas(janela, tmp_path):
    """D-608 ("As caixas de número continuam como estão") e D-083 (ângulo em número, setas de
    0,1°): com o teclado na caixa do ângulo do Endireitar, a seta ↑ sobe 0,1° e a página não
    muda; os botões de 0,1° continuam girando."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from ui.tela_conferir import FERRAMENTA_ENDIREITAR

    janela.show()
    janela.activateWindow()
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", [_pagina() for _ in range(3)]))
    tela = janela.tela_conferir
    tela.escolher_ferramenta(FERRAMENTA_ENDIREITAR)
    tela.ir_para_pagina(0)
    tela._angulo_zero()
    _assentar()
    campo = tela.campo_angulo
    antes = campo.value()
    QTest.mouseClick(campo.lineEdit(), Qt.LeftButton)
    _assentar()
    assert janela.focusWidget() is campo or campo.isAncestorOf(janela.focusWidget())
    QTest.keyClick(janela.focusWidget(), Qt.Key_Up)
    _assentar()
    assert campo.value() == pytest.approx(antes + 0.1), "a seta ↑ sobe 0,1°"
    QTest.keyClick(janela.focusWidget(), Qt.Key_Left)    # anda o cursor no número
    _assentar()
    assert tela.indice_pagina == 0, "a seta na caixa de número não troca de página"
    QTest.mouseClick(tela.botao_angulo_anti_horario, Qt.LeftButton)
    _assentar()
    assert tela.visualizadores["angulo"].angulo == pytest.approx(antes + 0.2), "o botão de 0,1° gira"
