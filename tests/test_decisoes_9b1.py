"""As provas de comportamento da etapa 9b-1 da obra de 26/10/2026: menus, impressão, janelas e
lado direito (CLAUDE.md §11, regra 4; Livro de decisões, docs/plano/DECISOES.md).

Regra 7 (Samuel, 27/10/2026): "é só para fazer o que eu já tinha mandado, fazer as ferramentas que
colocamos no programa funcionem como deveriam e como eu tinha escolhido."

Cada teste diz a decisão e as palavras dele, e mede o comportamento (o que fica marcado, o que
abre, o que é gravado), não a aparência. Os marcados REVERSÃO falham no código de antes da etapa
(`27b4c52`); o resultado da rodada no código antigo está no ONDE-PAREI da etapa
(relatorios/obra-etapa9b1/).

  D-555 (27/10): Central `ac-nome-sem-acento`: "Voltar com acento (recomendo)".
  D-492 / P-085 (27/10): o tique do menu Filtro acompanha o filtro da página aberta.
  D-274 / P-127 (08/10): "quando alguém tentar imprimir sem ver os alertas o programa para e mostra
      os alertas e a pessoa diz se quer ver ou continuar" - também pelo menu Arquivo e Ctrl+Return.
  D-020 / P-125 (18/07): o Desfazer do menu apagado sem nada para desfazer.
  D-309 (05/10) / Lista de bugs 332: o cartão continuava "pronto, PDF gerado" depois de mudar.
  D-342 (05/10): projeto.json ilegível -> aviso na tela (a etapa 3 já cobria; prova de que cobre).
  D-057 (20/10): os "Painel: …" do menu Ver viraram o menu Painéis; cada item abre o painel.

Nada aparece na tela (tests/conftest.py). Pasta de dados própria (fixture `pasta`).
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")
pytest.importorskip("cv2")

from tests.promessas import ajudantes as aj  # noqa: E402
from tests.test_promessas import app, janela, livro, pasta, tela  # noqa: E402,F401 - fixtures


# --- D-555: o nome sugerido com acento ------------------------------------------------------

def test_d555_nome_do_pdf_pronto_e_do_para_imprimir_com_acento(app, pasta):  # noqa: F811
    """REVERSÃO. D-555 (Samuel, 27/10/2026, `ac-nome-sem-acento`: "Voltar com acento
    (recomendo)"): o nome sugerido do PDF pronto e o do "para imprimir" voltam a ter o acento do
    livro e do filtro, como no `fase-1`; o sem acento das etapas 9a/9c saiu."""
    from core.filtros import MAGICO_PRO
    from modelos import Projeto, nome_de_saida_sugerido
    from ui.dialogo_impressao import DialogoImpressao

    projeto = Projeto(caminho_entrada="x.pdf", caminho_saida="", nome="Ofício da Imaculada Conceição")
    projeto.limpar, projeto.filtro_padrao, projeto.montar_cadernos = True, MAGICO_PRO, False
    assert nome_de_saida_sugerido(projeto) == "Ofício da Imaculada Conceição - mágico pro.pdf"

    livro_com_acento = aj.criar_livro(pasta, folhas=2, nome="Ofício da Imaculada Conceição")
    dialogo = DialogoImpressao(str(livro_com_acento))
    try:
        assert dialogo.destino_sugerido().name == f"{livro_com_acento.stem} - para imprimir.pdf"
        assert "í" in dialogo.destino_sugerido().name and "ç" in dialogo.destino_sugerido().name
    finally:
        dialogo.reject()


# --- D-492 / P-085: o tique do menu Filtro ------------------------------------------------

def _marcados_no_menu_filtro(janela):  # noqa: F811
    return [chave for chave, item in janela.menu.acoes.items()
            if chave.startswith("filtro_") and item.isChecked()]


def test_d492_tique_do_menu_filtro_acompanha_a_pagina(janela, tela):  # noqa: F811
    """REVERSÃO. D-492 (27/10/2026; P-085): o menu Filtro mostra marcado o filtro da página
    aberta. Escolhido Preto e branco pelo cartão (não pelo menu) -> marca em "Preto e branco";
    outra página em Original -> marca em "Original" e só nele; volta -> "Preto e branco"."""
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    assert _marcados_no_menu_filtro(janela) == [f"filtro_{ORIGINAL}"], "livro aberto sem a marca"
    tela.ir_para_pagina(1)
    tela._escolher_filtro(PRETO_E_BRANCO)
    aj.assentar()
    assert _marcados_no_menu_filtro(janela) == [f"filtro_{PRETO_E_BRANCO}"]
    tela.ir_para_pagina(0)
    aj.assentar()
    assert _marcados_no_menu_filtro(janela) == [f"filtro_{ORIGINAL}"]
    tela.ir_para_pagina(1)
    aj.assentar()
    assert _marcados_no_menu_filtro(janela) == [f"filtro_{PRETO_E_BRANCO}"]


def test_d492_clicar_no_filtro_que_ja_esta_nao_tira_a_marca(janela, tela):  # noqa: F811
    """REVERSÃO. D-492: o item do menu é de marcar e o Qt alterna a marca no clique; clicar no
    filtro que a página já tem não muda nada na página, e a marca tem de continuar nele. Clicar
    num outro troca o filtro da página e a marca vai junto (uma marca só)."""
    from core.filtros import MAGICO_PRO, ORIGINAL

    janela.menu.acoes[f"filtro_{ORIGINAL}"].trigger()
    aj.assentar()
    assert _marcados_no_menu_filtro(janela) == [f"filtro_{ORIGINAL}"]
    janela.menu.acoes[f"filtro_{MAGICO_PRO}"].trigger()
    aj.assentar()
    assert tela.projeto.paginas[tela.indice_pagina].filtro == MAGICO_PRO
    assert _marcados_no_menu_filtro(janela) == [f"filtro_{MAGICO_PRO}"]


# --- D-274 / P-127: o menu e o Ctrl+Return passam pela "Antes de processar" ------------------

@pytest.mark.parametrize("como", ["menu", "tecla"])
def test_d274_menu_e_ctrl_return_mostram_antes_de_processar(janela, tela, monkeypatch, pasta, como):  # noqa: F811
    """REVERSÃO. D-274 (08/10/2026): "quando alguém tentar imprimir sem ver os alertas o programa
    para e mostra os alertas e a pessoa diz se quer ver ou continuar". Pelo menu Arquivo >
    "Confirmar e processar" e pela tecla Ctrl+Return, com um aviso pendente, a janela "Antes de
    processar" aparece; "ver" leva à página do aviso e NÃO processa (nenhum PDF)."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    import ui.janela_confirmar as confirmar
    from core import analise
    from ui.janela_dos_avisos import JanelaDosAvisos
    from ui.janela_principal import CONFERIR

    tela.projeto.paginas[2].alertas = [analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
    pedidos = []
    monkeypatch.setattr(confirmar, "pedir_confirmacao", lambda *a, **k: pedidos.append(1))
    vistas = []
    aj.responder_caixa(monkeypatch, JanelaDosAvisos, "ver", registro=vistas)
    if como == "menu":
        janela.menu.acoes["processar"].trigger()
    else:
        janela.activateWindow()
        QTest.keyClick(janela, Qt.Key_Return, Qt.ControlModifier)
    aj.assentar()
    assert vistas, "a janela 'Antes de processar' não apareceu"
    assert not pedidos, "'ver' foi para a janela de salvar"
    assert janela.telas.currentIndex() == CONFERIR and tela.indice_pagina == 2


def test_d274_sem_aviso_o_menu_vai_direto_para_salvar(janela, tela, monkeypatch):  # noqa: F811
    """D-274 (o outro lado): sem aviso pendente, o menu vai direto à janela de salvar, como o
    botão (a "Antes de processar" só aparece com aviso)."""
    import ui.janela_confirmar as confirmar
    from ui.janela_dos_avisos import JanelaDosAvisos

    for pagina in tela.projeto.paginas:
        pagina.alertas = []
    for folha in tela.projeto.folhas:
        if hasattr(folha, "alertas"):
            folha.alertas = []
    pedidos = []
    monkeypatch.setattr(confirmar, "pedir_confirmacao", lambda *a, **k: pedidos.append(1))
    monkeypatch.setattr(JanelaDosAvisos, "exec", lambda *_a, **_k: pytest.fail("abriu sem aviso"))
    janela.menu.acoes["processar"].trigger()
    aj.assentar()
    assert pedidos == [1]


# --- D-020 / P-125: Desfazer apagado sem nada -------------------------------------------------

def test_p125_desfazer_do_menu_acompanha_o_que_ha_para_desfazer(janela, tela):  # noqa: F811
    """REVERSÃO. P-125 (D-020, "Desfazer ligado sem nada"): livro recém-aberto -> Desfazer e
    Refazer do menu Editar apagados; uma ação -> Desfazer aceso; desfeita -> Desfazer apagado e
    Refazer aceso; refeita -> o contrário."""
    from core.filtros import PRETO_E_BRANCO

    desfazer, refazer = janela.menu.acoes["desfazer"], janela.menu.acoes["refazer"]
    assert not desfazer.isEnabled() and not refazer.isEnabled()
    tela._escolher_filtro(PRETO_E_BRANCO)
    aj.assentar()
    assert desfazer.isEnabled() and not refazer.isEnabled()
    desfazer.trigger()
    aj.assentar()
    assert not desfazer.isEnabled() and refazer.isEnabled()
    refazer.trigger()
    aj.assentar()
    assert desfazer.isEnabled() and not refazer.isEnabled()


# --- D-309 / bug 332: o cartão "PDF gerado" ------------------------------------------------------

def _resumo_em_disco(janela):  # noqa: F811
    import projetos

    janela._salvar_agora()
    projetos.esperar_gravacoes()
    return projetos.ler_resumo(janela.resumo.pasta)


def test_d309_cartao_deixa_de_dizer_pronto_quando_o_trabalho_muda(janela, tela, monkeypatch, pasta):  # noqa: F811
    """REVERSÃO. D-309 (05/10/2026, "pode mandar concertar"; o cartão só diz "PDF gerado" depois
    de gravar) e Lista de bugs 332 (05/10: "o cartão continua 'pronto, PDF gerado' depois de mudar
    páginas sem gerar de novo"). PDF gerado -> cartão pronto; folhear não muda; trocar o filtro
    de uma página -> o cartão volta a "N de M conferidas" (gravado no disco); gerar de novo ->
    pronto outra vez."""
    from core.filtros import PRETO_E_BRANCO
    from ui.janela_principal import CONFERIR

    aj.gerar_pdf(janela, monkeypatch, pasta / "saida" / "um.pdf")
    assert _resumo_em_disco(janela).pdf_gerado
    janela.telas.setCurrentIndex(CONFERIR)
    tela.ir_para_pagina(2)
    tela.ir_para_pagina(0)
    aj.assentar()
    assert _resumo_em_disco(janela).pdf_gerado, "folhear tirou o 'PDF gerado'"
    tela._escolher_filtro(PRETO_E_BRANCO)
    aj.assentar()
    resumo = _resumo_em_disco(janela)
    assert not resumo.pdf_gerado, "o cartão continua 'PDF gerado' depois de mudar a página"
    assert resumo.frase_do_progresso != "pronto, PDF gerado"
    aj.gerar_pdf(janela, monkeypatch, pasta / "saida" / "dois.pdf")
    assert _resumo_em_disco(janela).pdf_gerado


def test_d309_marcacao_mexida_tambem_tira_o_pronto(janela, tela, monkeypatch, pasta):  # noqa: F811
    """REVERSÃO. D-309 / bug 332: a marcação feita à mão não passa pela pilha do desfazer, mas
    muda o PDF: mexida depois do PDF pronto, o cartão também deixa de dizer pronto."""
    from ui.janela_principal import CONFERIR

    aj.gerar_pdf(janela, monkeypatch, pasta / "saida" / "um.pdf")
    janela.telas.setCurrentIndex(CONFERIR)
    tela.escolher_ferramenta("retangulo")
    aj.assentar()
    editor = tela.editor_selecao
    editor.selecao_mudou.emit()            # o editor avisa: a marcação mudou à mão
    aj.assentar()
    assert not _resumo_em_disco(janela).pdf_gerado


# --- D-342: projeto.json ilegível avisa (a etapa 3 já cobria) ------------------------------------

def test_d342_projeto_ilegivel_mostra_o_aviso(janela, tela, livro):  # noqa: F811
    """D-342 (05/10/2026): "o programa quando estiver pronto, ele vai ter que ser capaz de abrir
    arquivos de versões anteriores." Com o projeto.json estragado, abrir o livro de novo mostra o
    aviso na tela ("Comecei a conferência deste livro de novo: o trabalho salvo não pôde ser
    lido", com a cópia guardada) e guarda a cópia do arquivo estragado. Já era assim desde a
    etapa 3 (a 9c pôs a cópia do estragado): esta prova só confere que continua."""
    import projetos
    from core.filtros import PRETO_E_BRANCO

    tela._escolher_filtro(PRETO_E_BRANCO)
    pasta_do_projeto = aj.pasta_do_projeto(janela)
    janela._sair_da_conferencia()
    projetos.esperar_gravacoes()
    (pasta_do_projeto / "projeto.json").write_text("{ isto não é um projeto", encoding="utf-8")
    janela.avisos.clear()
    aj.abrir_livro_para_teste(janela, livro)
    assert any("não pôde ser lido" in aviso for aviso in janela.avisos), janela.avisos
    assert list(pasta_do_projeto.glob(f"{projetos.PREFIXO_DA_COPIA_ESTRAGADA}*.json")), \
        "a cópia do projeto estragado não foi guardada"


# --- D-057: os "Painel: …" viraram o menu Painéis ------------------------------------------------

def test_d057_menu_paineis_abre_cada_painel_e_o_ver_nao_tem_painel(janela, tela):  # noqa: F811
    """D-057 (20/10, `r14-menu-paineis`: "B — Um menu novo, “Painéis”"; o defeito antigo "Ver >
    'Painel: …' sem efeito"): o menu Ver não tem mais item "Painel: …"; cada item do menu
    Painéis abre o painel dele (e a marca fica nele); "Fechar o painel" fecha."""
    ver = janela.menu.menus["Ver"]
    assert not [a.text() for a in ver.actions() if a.text().startswith("Painel")]
    for chave, painel, _texto in janela.menu.PAINEIS_DO_MENU:
        janela.menu.acoes[chave].trigger()
        aj.assentar()
        assert tela.paineis.aberto == painel, chave
        assert janela.menu.acoes[chave].isChecked()
    janela.menu.acoes["painel_fechar"].trigger()
    aj.assentar()
    assert tela.paineis.aberto is None


# --- auditoria C3: os nomes da "Montar para imprimir" voltam aos do fase-1 ------------------------

def _textos_da_janela(janela_de_imprimir) -> set[str]:
    """Todos os textos à vista da janela: rótulos, caixinhas, botões e os itens das listas."""
    from PySide6.QtWidgets import QAbstractButton, QComboBox, QLabel

    textos = set()
    for rotulo in janela_de_imprimir.findChildren(QLabel):
        textos.add(rotulo.text())
    for botao in janela_de_imprimir.findChildren(QAbstractButton):
        textos.add(botao.text())
    for lista in janela_de_imprimir.findChildren(QComboBox):
        textos.update(lista.itemText(i) for i in range(lista.count()))
    return {t.strip().upper() if t.isupper() else t.strip() for t in textos if t}


def test_c3_nomes_da_montar_para_imprimir_sao_os_do_fase_1(app, pasta):  # noqa: F811
    """REVERSÃO. Auditoria das escolhas (27/10/2026), C3: a etapa 9a trocou os nomes das opções
    da "Montar para imprimir"; o Samuel tinha pedido só "melhorar esse layout" (fr-26, D-333) e
    as opções "que aparecem nos prints do PDF que mandei" (D-315); nome novo só pela revisão de
    nomes (D-374). Voltam os do `fase-1`; os da 9a saíram. A disposição em duas colunas fica
    (o cartão "O que vai sair" continua)."""
    from ui.dialogo_impressao import DialogoImpressao

    livro_de_teste = aj.criar_livro(pasta, folhas=2)
    dialogo = DialogoImpressao(str(livro_de_teste))
    try:
        textos = _textos_da_janela(dialogo)
        rotulos_do_form = set()
        from PySide6.QtWidgets import QFormLayout, QLabel

        for form in dialogo.findChildren(QFormLayout):
            for linha in range(form.rowCount()):
                item = form.itemAt(linha, QFormLayout.LabelRole)
                if item is not None and isinstance(item.widget(), QLabel):
                    rotulos_do_form.add(item.widget().text())
        textos |= rotulos_do_form
        do_fase_1 = ["Ordem de páginas:", "Páginas por caderno:", "Rotação automática",
                     "Centralizar automático", "Reverter páginas", "Agrupar", "Esquerda", "Direita",
                     "cancelar", "Escala personalizada:", "em pé (retrato)", "deitada (paisagem)",
                     "Frente e verso", "Horizontal", "Vertical", "Só uma página:",
                     "Imprimir em escala de cinza", "Folhas de (0 = todas):",
                     "Páginas do livro de (0 = todas):", "(a de sempre do Windows)"]
        faltam = [t for t in do_fase_1 if t not in textos]
        assert not faltam, f"nomes do fase-1 que não voltaram: {faltam}"
        da_9a = ["Imprimir:", "Cada caderno:", "Girar sozinho a página deitada", "Centralizar sozinho",
                 "Ordem invertida", "Agrupar as cópias", "costura à esquerda", "costura à direita",
                 "parar", "Escala:", "Uma página só:", "Imprimir em tons de cinza", "Folhas de papel:"]
        sobraram = [t for t in da_9a if t in textos]
        assert not sobraram, f"nomes da etapa 9a que ficaram: {sobraram}"
        assert "O QUE VAI SAIR" in textos, "a disposição nova (cartão 'O que vai sair') saiu"
    finally:
        dialogo.reject()


# --- D-283: a "Antes de processar" aprovada (lm22) e o "Mostrar" inteiro ---------------------------

def test_d283_antes_de_processar_aprovada_e_o_mostrar_nao_corta(app):  # noqa: F811
    """REVERSÃO. D-283 (21/10, `pr-antes-de-processar`: "ficou meio embolado, deve ficar mais
    claro e não tão grande"; 22/10 `lm22` "Aprovado", com o "Mostrar" cortado a consertar): a
    janela do commit `138e425` (frase em duas linhas, uma fila de botões embaixo, menor que os
    560 x 520 de antes, cabe a 1280 x 657 em 61% da altura) e o "Mostrar" com o motivo inteiro:
    "Endireitar: as contas discordam (12)", com o "(12)"."""
    from PySide6.QtWidgets import QApplication

    from core import analise
    from core import avisos as avisos_do_livro
    from ui.janela_dos_avisos import JanelaDosAvisos

    avisos = [avisos_do_livro.Aviso(avisos_do_livro.PAGINA, i, analise.CONTAS_DO_ENDIREITAR_DISCORDAM)
              for i in range(12)]
    janela_dos_avisos = JanelaDosAvisos(avisos, antes_de_processar=True)
    janela_dos_avisos.show()
    QApplication.processEvents()
    try:
        assert janela_dos_avisos.pergunta.text() == "Quer ver antes ou continuar assim mesmo?"
        assert janela_dos_avisos.height() <= 657 * 0.61
        combo = janela_dos_avisos.combo_motivo
        combo.setCurrentIndex(1)
        QApplication.processEvents()
        texto = combo.currentText()
        assert texto == "Endireitar: as contas discordam (12)"
        from PySide6.QtWidgets import QStyle, QStyleOptionComboBox

        opcao = QStyleOptionComboBox()
        combo.initStyleOption(opcao)
        cabe = combo.style().subControlRect(QStyle.CC_ComboBox, opcao,
                                            QStyle.SC_ComboBoxEditField, combo).width()
        assert combo.fontMetrics().horizontalAdvance(texto) <= cabe, \
            f"o 'Mostrar' corta o motivo: {combo.width()} pontos para {texto!r}"
        assert janela_dos_avisos.width() <= 1280
    finally:
        janela_dos_avisos.close()


# --- D-250: o "Pintar por cima" que cobre letras pergunta antes -----------------------------------

@pytest.fixture
def editor_no_marial_7(app):  # noqa: F811
    """A ferramenta de marcar com o Marial 7 do gabarito (a página do teste do Samuel), no
    "Pintar por cima" e no Retângulo."""
    import cv2

    from core.selecao import PINTAR
    from ui.widgets.editor_selecao import FERRAMENTA_RETANGULO, EditorSelecao

    img = cv2.imread(str(aj.RAIZ / "gabarito" / "paginas" / "marial_p007.png"))
    if img is None:
        pytest.skip("gabarito/paginas/marial_p007.png não está nesta cópia")
    editor = EditorSelecao()
    editor.resize(600, 800)
    editor.definir_imagem(img)
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    editor.definir_tipo(PINTAR)
    editor.show()
    aj.assentar()
    yield editor
    editor.close()


def _arrastar(editor, x0, y0, x1, y1):
    from tests.test_editor_selecao import arrastar

    arrastar(editor, x0, y0, x1, y1)
    aj.assentar()


@pytest.mark.parametrize("resposta", ["Pintar assim mesmo", "Voltar"])
def test_d250_pintar_por_cima_das_letras_pergunta_antes(editor_no_marial_7, monkeypatch, resposta):
    """REVERSÃO. D-250 (Samuel, 22/10/2026, `fr-218-aviso`: "A — Avisar (recomendo)"; no chat:
    "1- sim"): o retângulo de "Pintar por cima" desenhado sobre o começo das linhas do Marial 7
    (o caso do teste dele) pergunta antes, com "Este retângulo cobre letras; elas vão ser
    pintadas também." e os botões "Pintar assim mesmo" e "Voltar". "Voltar" não pinta nada (a
    marcação continua vazia); "Pintar assim mesmo" pinta."""
    from ui import perguntas

    editor = editor_no_marial_7
    perguntadas = []

    def responder(_pai, titulo, texto, sim="Sim", nao="Não", padrao_sim=False):
        perguntadas.append((titulo, texto, sim, nao))
        return resposta == sim

    monkeypatch.setattr(perguntas, "perguntar", responder)
    _arrastar(editor, 0.05, 0.15, 0.20, 0.45)
    assert perguntadas == [("Pintar por cima", "Este retângulo cobre letras; elas vão ser pintadas também.",
                            "Pintar assim mesmo", "Voltar")]
    if resposta == "Voltar":
        assert len(editor.selecao) == 0, "'Voltar' pintou"
    else:
        assert len(editor.selecao) == 1


def test_d250_sem_letras_pinta_sem_perguntar(editor_no_marial_7, monkeypatch):
    """D-250 (o outro lado): na margem branca de baixo e na sombra da lombada (sem letras) o
    retângulo pinta direto, sem pergunta."""
    from ui import perguntas

    editor = editor_no_marial_7
    monkeypatch.setattr(perguntas, "perguntar", lambda *a, **k: pytest.fail("perguntou sem letras"))
    _arrastar(editor, 0.10, 0.955, 0.60, 0.995)
    _arrastar(editor, 0.0, 0.2, 0.03, 0.8)
    assert len(editor.selecao) == 2


# --- o foco preso na lista do Automático (achado das etapas 5 e 6) --------------------------------

def _clicar_na_pagina(janela, tela):  # noqa: F811
    """Clica (mouse do Qt) no meio da página, como o Kaique antes de usar as teclas; devolve quem
    ficou com o teclado."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    janela.activateWindow()
    pagina = tela.area_imagem.currentWidget()
    QTest.mouseClick(pagina, Qt.LeftButton, Qt.NoModifier, pagina.rect().center())
    aj.assentar()
    return QApplication.focusWidget()


def _clicar_na_lista_do_automatico(janela, tela):  # noqa: F811
    """Abre o painel Automático e clica (mouse de verdade do Qt) na primeira etapa da lista."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from ui.widgets.paineis import PAINEL_AUTOMATICO

    tela.paineis.abrir(PAINEL_AUTOMATICO)
    aj.assentar()
    lista = tela.paineis.automatico.lista
    retangulo = lista.visualItemRect(lista.item(0))
    QTest.mouseClick(lista.viewport(), Qt.LeftButton, Qt.NoModifier, retangulo.center())
    aj.assentar()
    return lista


def _apertar_e_conferir(janela, tela, tecla):  # noqa: F811
    """Aperta a tecla em quem está com o teclado e confere que ela chegou à página."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from core.filtros import PRETO_E_BRANCO

    alvo = QApplication.focusWidget() or janela
    antes = tela.indice_atual
    if tecla == "D":
        QTest.keyClick(alvo, Qt.Key_D)
        aj.assentar()
        assert tela.trilha.ferramenta == "dividir", "a letra D não chegou à página"
    elif tecla == "PageDown":
        QTest.keyClick(alvo, Qt.Key_PageDown)
        aj.assentar()
        assert tela.indice_atual > antes, "Page Down não chegou à página"   # anda 10 (D-021)
    else:
        QTest.keyClick(alvo, Qt.Key_2)
        aj.assentar()
        assert tela.projeto.paginas[tela.indice_pagina].filtro == PRETO_E_BRANCO,             "a tecla 2 não chegou à página"


@pytest.mark.parametrize("tecla", ["D", "PageDown", "2"])
def test_teclas_chegam_a_pagina_depois_de_clicar_na_lista_do_automatico(janela, tela, tecla):  # noqa: F811
    """REVERSÃO. Achado das etapas 5 e 6 (ONDE-PAREI, ressalvas 2 e 3): depois de clicar na
    lista do painel Automático, as teclas (D, X, I, F, 1-4, Page Down) iam para a lista (e o
    Page Down para a rolagem do painel) e não chegavam à página até um clique na página. Agora:
    clique na página, clique na lista (ela escolhe a etapa, como antes), e o teclado continua
    com a página. As teclas não mudam (D-561: "Manter"): D leva ao Dividir, Page Down anda 10
    páginas (D-021), 2 põe o Preto e branco na página."""
    from PySide6.QtWidgets import QApplication

    _clicar_na_pagina(janela, tela)
    lista = _clicar_na_lista_do_automatico(janela, tela)
    assert lista.currentRow() == 0, "o clique na lista não escolheu a etapa"
    dono = QApplication.focusWidget()
    while dono is not None and dono is not tela.paineis:
        dono = dono.parentWidget()
    assert dono is None, f"o teclado ficou no painel ({type(QApplication.focusWidget()).__name__})"
    _apertar_e_conferir(janela, tela, tecla)


@pytest.mark.parametrize("tecla", ["PageDown"])
def test_page_down_chega_a_pagina_depois_de_clicar_numa_miniatura(janela, tela, tecla):  # noqa: F811
    """REVERSÃO. O mesmo foco preso, na tira de miniaturas (achado ao provar o de cima): a rolagem
    da tira ficava com o teclado (ao abrir o livro e depois de clicar numa miniatura), e o Page
    Down rolava a tira em vez de andar as páginas (D-021: "Page Up/Down, Home/End"). O clique na
    miniatura continua levando à página dela."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    janela.activateWindow()
    quadro = tela.tira._miniaturas[1]
    QTest.mouseClick(quadro, Qt.LeftButton, Qt.NoModifier, quadro.rect().center())
    aj.assentar()
    assert tela.indice_atual == 1, "o clique na miniatura não levou à página"
    _apertar_e_conferir(janela, tela, tecla)


# --- o contador da barra de baixo cabe (ressalva 1 da etapa 7) ------------------------------------

def test_contador_da_barra_de_baixo_em_duas_linhas_quando_nao_cabe_em_uma(app):  # noqa: F811
    """REVERSÃO. Etapa 7, ressalva 1: "o contador do rodapé ainda sai cortado com um painel aberto
    a 1280 ('3 de 36…')". Quando a conta não cabe numa linha, ela vai em duas ("N de M
    conferidas" / "K com dúvida"), inteira, em letra um ponto menor; o texto inteiro (com o nome
    do livro) continua no balão. Mede com as letras desta máquina: a largura dada é a que cabe
    em duas linhas e não cabe em uma."""
    from PySide6.QtGui import QFont, QFontMetrics

    from ui.tela_conferir import _RotuloDoLivro

    rotulo = _RotuloDoLivro()
    conta = "0 de 360 conferidas · 18 com dúvida"
    pequena = QFont(rotulo.font())
    pequena.setPixelSize(getattr(_RotuloDoLivro, "LETRA_EM_DUAS_LINHAS", 11))
    largura = max(QFontMetrics(pequena).horizontalAdvance(t) for t in conta.split(" · ")) + 12
    if QFontMetrics(rotulo.font()).horizontalAdvance(conta) <= largura - 4:
        pytest.skip("nesta máquina a conta cabe numa linha nessa largura")
    rotulo.resize(largura, 30)
    rotulo.show()
    aj.assentar()
    rotulo.definir("La vida eterna", conta)
    aj.assentar()
    assert rotulo.text() == "0 de 360 conferidas\n18 com dúvida", repr(rotulo.text())
    assert rotulo.toolTip() == "La vida eterna · " + conta
    rotulo.resize(2000, 30)          # cabe tudo numa linha: volta ao de sempre
    aj.assentar()
    assert rotulo.text() == "La vida eterna · " + conta
    rotulo.close()


def test_barra_de_baixo_nada_saiu(janela, tela):  # noqa: F811
    """O conserto do contador não tira nada da barra de baixo (o pedido: "faça caber sem tirar
    nada"): as setas, "página N de M", desfazer, refazer, Histórico, a conta, "Uma página",
    "Duas lado a lado", "antes / depois", o zoom e "ajustar à tela" continuam à vista, com um
    painel aberto."""
    tela.paineis.abrir("revisar")
    aj.assentar()
    for peca in (tela.botao_anterior, tela.rotulo_da_pagina, tela.botao_proxima,
                 tela.botao_desfazer_embaixo, tela.botao_refazer_embaixo, tela.botao_historico_embaixo,
                 tela.rotulo_do_livro, tela.botoes_mostrar["uma"] if "uma" in tela.botoes_mostrar
                 else list(tela.botoes_mostrar.values())[0], list(tela.botoes_mostrar.values())[1],
                 tela.botao_antes_depois, tela.botao_menos_zoom, tela.rotulo_do_zoom,
                 tela.botao_mais_zoom, tela.botao_ajustar_a_tela):
        assert peca.isVisible(), peca


# --- D-033: os quatro jeitos do lado direito ------------------------------------------------------

def _clicar_na_fila(fila, painel):  # noqa: F811
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    QTest.mouseClick(fila, Qt.LeftButton, Qt.NoModifier, fila.retangulos()[painel].center())
    aj.assentar()


def test_d033_os_quatro_jeitos_no_menu_ver_e_nas_configuracoes(janela, tela):  # noqa: F811
    """REVERSÃO. D-033 (05/10/2026): "Quer os quatro jeitos no app, escolhendo dentro dele:
    sanfona (o primeiro), abas no alto, ícones na borda, painel flutuante" · R14 902: "C — Nos
    dois lugares" (menu Ver e Configurações). A etapa 2 só fez dois (auditoria C2). Os quatro,
    com os nomes da pergunta 902, nos dois lugares, e o mesmo caminho: escolher num marca no
    outro."""
    from ui.tela_configuracoes import TelaConfiguracoes
    from ui.widgets.paineis import jeito_guardado

    nomes = {"icones": "Ícones na borda (de fábrica)", "sanfona": "Sanfona (a área de trabalho 1)",
             "abas": "Abas no alto", "solto": "Painel solto"}
    submenu = janela.menu.menu_do_lado_direito
    assert [a.text() for a in submenu.actions()] == list(nomes.values())
    configuracoes = TelaConfiguracoes(janela)
    try:
        assert {j: b.text() for j, b in configuracoes.botoes_lado.items()} == nomes
        for jeito in ("abas", "solto", "sanfona", "icones"):
            configuracoes.botoes_lado[jeito].setChecked(True)
            aj.assentar()
            assert tela.paineis.jeito == jeito and jeito_guardado() == jeito
            assert janela.menu.acoes[f"lado_{jeito}"].isChecked(), "o menu Ver não acompanhou"
    finally:
        configuracoes.close()


def test_d033_abas_no_alto(janela, tela):  # noqa: F811
    """REVERSÃO. D-033, "abas no alto" (o desenho `13-rodada7-padrao-c-abas`, "aberto em
    Revisar"): Ver > Lado direito > "Abas no alto" -> a coluna dos painéis com as cinco abas no
    alto e o "Para revisar" aberto embaixo delas; o clique numa aba abre o painel dela (o mouse
    do Qt na aba); o clique na aba aberta não fecha; a página fica ao lado (não por baixo)."""
    from PySide6.QtCore import QPoint

    janela.menu.acoes["lado_abas"].trigger()
    aj.assentar()
    paineis = tela.paineis
    assert paineis.jeito == "abas" and paineis.abas.isVisible()
    assert not paineis.icones.isVisible() and not paineis.sanfona.isVisible()
    assert paineis.aberto == "revisar" and paineis.para_revisar.isVisible()
    fila = paineis.fila_de_abas
    assert paineis.para_revisar.mapTo(paineis.abas, QPoint(0, 0)).y() >= fila.height(), \
        "o painel não está embaixo das abas"
    for painel in ("filtro", "historico", "automatico", "props"):
        _clicar_na_fila(fila, painel)
        assert paineis.aberto == painel and paineis.paineis[painel].isVisible(), painel
    _clicar_na_fila(fila, "props")
    assert paineis.aberto == "props", "o clique na aba aberta fechou o painel"
    pagina = tela.vista_da_pagina
    canto = pagina.mapTo(tela, QPoint(pagina.width(), 0)).x()
    assert canto <= paineis.abas.mapTo(tela, QPoint(0, 0)).x(), "as abas ficaram por cima da página"


def test_d033_painel_solto(janela, tela):  # noqa: F811
    """REVERSÃO. D-033, "painel flutuante" (o "Painel solto" da pergunta 902; o desenho
    `13-rodada7-padrao-e-flutuante`): os botões dos painéis na linha de cima (a dos menus), o
    painel aberto POR CIMA da página, no canto de cima à direita; a página não encolhe; o
    clique no botão do aberto fecha. Fora da tela de trabalho os botões somem."""
    from PySide6.QtCore import QPoint

    from ui.janela_principal import CONFERIR, INICIO

    pagina = tela.vista_da_pagina
    janela.menu.acoes["lado_solto"].trigger()
    aj.assentar()
    paineis = tela.paineis
    botoes = paineis.botoes_do_alto
    assert paineis.jeito == "solto" and botoes.isVisible()
    assert janela.linha_dos_menus.isAncestorOf(botoes), "os botões não estão na linha de cima"
    assert not paineis.icones.isVisible()
    largura_da_pagina = pagina.width()
    _clicar_na_fila(botoes, "historico")
    assert paineis.aberto == "historico" and paineis.historico.isVisible()
    moldura = paineis.moldura_do_solto
    assert moldura is not None and moldura.isVisible()
    assert pagina.width() == largura_da_pagina, "a página encolheu (o painel solto fica por cima)"
    canto_da_pagina = pagina.mapTo(tela, QPoint(0, 0))
    canto_da_moldura = moldura.mapTo(tela, QPoint(0, 0))
    assert canto_da_pagina.x() < canto_da_moldura.x() < canto_da_pagina.x() + pagina.width()
    assert canto_da_moldura.x() + moldura.width() <= canto_da_pagina.x() + pagina.width()
    assert canto_da_pagina.y() <= canto_da_moldura.y() < canto_da_pagina.y() + 40
    _clicar_na_fila(botoes, "historico")
    assert paineis.aberto is None and not moldura.isVisible()
    janela.telas.setCurrentIndex(INICIO)
    aj.assentar()
    assert not botoes.isVisible(), "os botões do painel solto ficaram fora da tela de trabalho"
    janela.telas.setCurrentIndex(CONFERIR)
    aj.assentar()
    assert botoes.isVisible()
