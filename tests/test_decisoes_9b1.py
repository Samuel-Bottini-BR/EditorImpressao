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
