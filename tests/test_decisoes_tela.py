"""Provas de comportamento das decisões do Samuel que tocam a TELA (etapa 2 da obra de 26/10/2026).

Regra 4 do Livro de decisões (CLAUDE.md §11, docs/plano/DECISOES.md): "Cada decisão tem uma prova
de comportamento [...]. Quando a decisão substitui um comportamento antigo, a prova confere também
que o antigo saiu. Aparência não conta como prova." As provas das decisões do processamento ficam em
tests/test_decisoes.py (etapa 1, outro agente); estas são as da tela.

Cada teste diz a decisão, com as palavras dele:

  D-001 (25/09/2026): "Estrutura: Photoshop puro, sem abas. Uma única tela com todas as
        ferramentas." -> abrir um livro com QUALQUER combinação de caixinhas, inclusive nenhuma, e
        todas as ferramentas estão na trilha, funcionam, e todos os menus ficam acesos. O antigo
        (regra de julho: cada ferramenta só com a caixinha dela) saiu.
  R7 203 D + R14 902 C (05, 06 e 20/10): "D — Ícones na borda, tudo fechado" + "Mas eu também
        quero ter a opção da area de trabalho 1" + "C — Nos dois lugares" -> de fábrica os ícones,
        tudo fechado; a área de trabalho 1 (sanfona) escolhida no menu Ver e nas Configurações.
  R9 403 B (09/10): "B — Filtros numa fila + partes que abrem e fecham" -> o botão provisório
        "Os quatro filtros" saiu da trilha.
  07 e 09/10 (Registro, PLANO-DEFINITIVO l.473 e l.599-600): "Deixar em branco" (tecla Delete;
        página branca no lugar, encadernação não muda) e "Tirar do livro"; "Essa opção de tirar do
        livro ou deixar folha em branco eu quero ter em outras paginas" -> os dois botões em
        qualquer página, e a Delete deixa em branco (antes apagava).
  Teste do Kaique (26/10) + R8 302 C: "nenhum menu tem Endireitar, Cortar ou Dividir"; "quando eu
        passar em cima da agrupada tem que mostrar a letra dela de atalho" -> menu Ferramentas e o
        balão com nome e letra.
  Lista única 1.12 e 2.2 (23/10): menus cinza na tela das caixinhas; caixinha marcada sem quadrado.

Testes de máquina, sem janela na tela (tests/conftest.py). O print da janela de verdade, sem
caixinhas, fica em relatorios/obra-etapa2/prints/ (roteiro/print_sem_caixinhas.py).
"""

from __future__ import annotations

from tests.ajudante_do_automatico import rodar_como_o_conferir  # etapa 3 da obra

import itertools

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from PySide6.QtCore import QEvent, QPoint, Qt  # noqa: E402
from PySide6.QtGui import QColor, QHelpEvent, QKeyEvent  # noqa: E402
from PySide6.QtWidgets import QApplication, QCheckBox, QToolTip  # noqa: E402

from core import pipeline  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _pdf,
    app,
    janela,
    pasta,
)
from ui.widgets.trilha_agrupada import (  # noqa: E402
    FERRAMENTA_CORTAR,
    FERRAMENTA_DIVIDIR,
    FERRAMENTA_ENDIREITAR,
    FERRAMENTA_FILTROS,
    GRUPOS,
    NOMES,
    grupo_de,
    tecla_de,
)

CAIXINHAS = ("cx_dividir", "cx_cortar", "cx_endireitar", "cx_limpar")
# etapa 5 da obra: a ferramenta Mover ("mover") nasce em todo livro também (D-008, D-001)
TODAS_AS_ABAS = ["corte", "bordas", "angulo", "mover", "marcar", "filtro"]
# todas as ferramentas da trilha (as de página e as de marcar e de olhar)
TODAS_AS_FERRAMENTAS = [f for g in GRUPOS if g != "-" for f in g]


def _assentar() -> None:
    for _ in range(5):
        QApplication.processEvents()


# as caixinhas de antes e o campo do livro que cada uma ligava (desde a etapa 3 da obra
# elas são as etapas do Automático)
CAMPO_DA_CAIXINHA = {"cx_dividir": "dividir_folhas", "cx_cortar": "cortar_bordas",
                     "cx_endireitar": "endireitar", "cx_limpar": "limpar"}


def _abrir(janela, pasta, marcadas=(), folhas=3):
    """Abre um livro como o Kaique e roda o Automático SÓ com as etapas pedidas (as outras
    desligadas, inclusive as que vinham marcadas de fábrica). Etapa 3 da obra: antes era a
    tela "O que fazer" com as caixinhas e o "Conferir"."""
    janela.abrir_livro(str(_pdf(pasta, folhas=folhas)))
    rodar_como_o_conferir(janela, sempre=True, detectar_regioes=False,
                          **{campo: nome in marcadas for nome, campo in CAMPO_DA_CAIXINHA.items()})
    janela.resize(1280, 657)
    janela.show()
    _assentar()
    return janela.tela_conferir


# --- D-001: todas as ferramentas, com qualquer caixinha ---------------------------------------


def test_d001_sem_nenhuma_caixinha_todas_as_ferramentas_estao_na_trilha(janela, pasta):
    """D-001, o caso que o Samuel achou na sessão 1 (26/10): abrir sem marcar nada. Antes só
    existia "Os quatro filtros" (a regra de julho); agora as cinco "abas" de dentro e todos os
    botões da trilha."""
    tela = _abrir(janela, pasta, marcadas=())
    p = janela.projeto
    assert not (p.dividir_folhas or p.cortar_bordas or p.endireitar or p.limpar)
    assert tela._abas_ativas == TODAS_AS_ABAS, "o antigo (só as das caixinhas) voltou"
    grupos_a_vista = set(tela.trilha.retangulos())
    for ferramenta in TODAS_AS_FERRAMENTAS:
        assert tela.trilha.disponivel(ferramenta), ferramenta
        assert grupo_de(ferramenta) in grupos_a_vista, f"{NOMES[ferramenta]} não está na trilha"
    assert tela.trilha.isVisible()


@pytest.mark.parametrize("marcadas", [c for n in range(len(CAIXINHAS) + 1)
                                      for c in itertools.combinations(CAIXINHAS, n)],
                         ids=lambda c: "+".join(x[3:] for x in c) or "nenhuma")
def test_d001_qualquer_combinacao_de_caixinhas_tem_as_mesmas_ferramentas(janela, pasta, marcadas):
    """D-001: as 16 combinações das quatro caixinhas da tela "O que fazer" (Dividir, Cortar,
    Endireitar, Limpar) abrem com as MESMAS ferramentas, e cada ferramenta da trilha leva a tela
    para ela."""
    tela = _abrir(janela, pasta, marcadas=marcadas)
    assert tela._abas_ativas == TODAS_AS_ABAS
    assert set(tela.trilha.retangulos()) == {i for i, g in enumerate(GRUPOS) if g != "-"}
    for ferramenta, aba in ((FERRAMENTA_DIVIDIR, "corte"), (FERRAMENTA_CORTAR, "bordas"),
                            (FERRAMENTA_ENDIREITAR, "angulo"), ("retangulo", "marcar"),
                            ("zoom", "marcar"), ("mao", "marcar")):
        tela.trilha.escolher(ferramenta)
        assert tela.aba_atual == aba, (ferramenta, marcadas)
        assert tela.trilha.ferramenta == ferramenta


def test_d001_sem_caixinhas_marcar_zoom_mao_e_filtro_funcionam(janela, pasta):
    """D-001 de verdade, não só na aparência: sem nenhuma caixinha, o Retângulo marca a página,
    o Zoom aproxima, a Mão é escolhida, e o painel Filtro troca o filtro da página."""
    from core.filtros import PRETO_E_BRANCO
    from core.selecao import GRAVURA

    tela = _abrir(janela, pasta, marcadas=())
    pagina = janela.projeto.paginas[0]
    tela.ir_para_pagina(0)
    # Marcar: o Retângulo desenha uma área na página (o editor existe sem a caixinha)
    tela.escolher_ferramenta("retangulo")
    assert tela.aba_atual == "marcar"
    editor = tela.editor_selecao
    assert editor.ferramenta == "retangulo"
    img = np.full((400, 300, 3), 235, np.uint8)
    editor.definir_imagem(img)
    editor.resize(300, 400)
    editor._area = editor._calcular_area()
    from tests.test_editor_selecao import arrastar

    editor.definir_tipo(GRAVURA)
    arrastar(editor, 0.2, 0.2, 0.7, 0.7)
    assert len(editor.selecao) == 1, "o Retângulo não marcou nada"
    assert pagina.selecao, "a marcação não foi para a página"
    # Zoom e Mão
    tela.escolher_ferramenta("zoom")
    antes = editor.zoom
    tela.mudar_o_zoom(tela.PASSO_DO_ZOOM)
    assert editor.zoom > antes
    tela.escolher_ferramenta("mao")
    assert editor.ferramenta == "mao" and tela.barra_opcoes.ferramenta == "mao"
    # Filtro: o painel "Filtro da página" está montado e troca o filtro
    assert tela.paineis.filtro_da_pagina.montado
    tela.paineis.abrir("filtro")
    tela.paineis.filtro_da_pagina.filtro_escolhido.emit(PRETO_E_BRANCO)
    assert pagina.filtro == PRETO_E_BRANCO


def test_d001_sem_nada_marcado_o_livro_abre_na_area_de_trabalho(janela, pasta):
    """D-001 e D-009 (26/10: "eu deveria conseguir abrir o livro sem escolher nenhuma opção para
    fazer tudo manualmente"). Na etapa 2 o "Conferir" da tela "O que fazer" passou a ficar aceso
    sem caixinha; desde a etapa 3 (D-002) não há mais tela no meio: o livro abre direto na área
    de trabalho, sem nada ligado, com todas as ferramentas."""
    from ui.janela_principal import CONFERIR

    janela.abrir_livro(str(_pdf(pasta, folhas=2)))
    assert janela.telas.currentIndex() == CONFERIR
    assert not janela.projeto.alguma_funcao_marcada
    assert janela.tela_conferir._abas_ativas == TODAS_AS_ABAS


def test_d001_sem_caixinhas_todos_os_menus_acesos(janela, pasta):
    """D-001 ("todos os menus ativos") e lista única 1.12: na tela de trabalho e na tela das
    caixinhas, com um livro aberto, nenhum menu fica cinza."""
    from ui.janela_principal import CONFERIR

    janela.abrir_livro(str(_pdf(pasta, folhas=3)))
    _assentar()
    assert janela.telas.currentIndex() == CONFERIR   # etapa 3: direto na área de trabalho
    apagados = [t for t, m in janela.menu.menus.items() if not m.menuAction().isEnabled()]
    assert apagados == [], f"menus cinza na tela de trabalho: {apagados}"
    # na tela inicial, sem livro à vista, continua como no desenho
    janela._sair_da_conferencia()
    ativos = [t for t, m in janela.menu.menus.items() if m.menuAction().isEnabled()]
    assert ativos == ["Arquivo", "Ver", "Ajuda"]


def test_o_menu_mexe_so_no_livro_aberto_e_nao_no_de_antes(janela, pasta):
    """O que a etapa 2 protegia (o menu não mexer no trabalho do livro de antes), pelo caminho
    novo (etapa 3): o outro livro abre direto na área de trabalho, e o menu mexe nele, nunca no
    projeto do livro anterior."""
    _abrir(janela, pasta, marcadas=())
    primeiro = janela.projeto
    antes = [p.em_branco for p in primeiro.paginas]
    outro = pasta / "outro"
    outro.mkdir()
    janela.abrir_livro(str(_pdf(outro, folhas=2)))
    _assentar()
    assert janela.projeto is not primeiro
    janela.menu.acoes["deixar_em_branco"].trigger()
    assert [p.em_branco for p in primeiro.paginas] == antes
    assert janela.projeto.paginas[janela.tela_conferir.indice_pagina].em_branco


# --- Os quatro filtros fora da trilha (R9 403 B) -----------------------------------------------


def test_os_quatro_filtros_sairam_da_trilha_e_o_painel_filtro_faz_o_mesmo(janela, pasta):
    tela = _abrir(janela, pasta, marcadas=("cx_limpar",))
    assert grupo_de(FERRAMENTA_FILTROS) == -1
    assert all(FERRAMENTA_FILTROS not in g for g in GRUPOS if g != "-")
    textos = [a.text() for a in janela.menu.menus["Ferramentas"].actions()]
    assert not any("quatro filtros" in t.lower() for t in textos)
    # o painel Filtro tem a fila com os filtros (o que o botão fazia)
    assert len(tela.paineis.filtro_da_pagina.cartoes) >= 4


# --- Delete deixa em branco; os dois botões em qualquer página (07 e 09/10) --------------------


def test_delete_deixa_em_branco_e_nao_tira_do_livro(janela, pasta):
    """Samuel, 07/10: "Deixar em branco" (tecla Delete; página branca no lugar, encadernação não
    muda). Antes a Delete apagava a página (tirava do livro)."""
    tela = _abrir(janela, pasta, marcadas=())
    tela.ir_para_pagina(1)
    pagina = janela.projeto.paginas[1]
    assert not pagina.em_branco and not pagina.apagada
    tecla = QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
    assert tela.tratar_tecla(tecla)
    assert pagina.em_branco, "a Delete não deixou em branco"
    assert not pagina.apagada, "a Delete tirou a página do livro (o comportamento antigo)"
    # o menu: o item com a Delete é o "Deixar esta página em branco"
    item = janela.menu.acoes["deixar_em_branco"]
    assert item.shortcut().toString() == "Del"
    assert "em branco" in item.text()
    assert "apagar" not in janela.menu.acoes, "o \"Apagar esta página\" com a Delete voltou"
    item.trigger()                                   # de novo: a página volta
    assert not pagina.em_branco
    janela.menu.acoes["tirar_do_livro"].trigger()
    assert pagina.apagada


def test_com_uma_area_escolhida_a_delete_apaga_a_area_e_nao_a_pagina(janela, pasta):
    """A Delete é da janela (deixar em branco), MENOS quando a ferramenta "Mover e mudar o
    tamanho da área" tem uma área escolhida: aí ela apaga a área (item 2.18). O editor pega a
    tecla antes do atalho da janela (ShortcutOverride)."""
    from core.selecao import GRAVURA, Selecao, retangulo

    tela = _abrir(janela, pasta, marcadas=())
    tela.escolher_ferramenta("ajustar")
    editor = tela.editor_selecao
    selecao = Selecao()
    selecao.acrescentar(retangulo(0.2, 0.2, 0.5, 0.5, tipo=GRAVURA))
    editor.definir_selecao(selecao)
    sobreposicao = QKeyEvent(QEvent.ShortcutOverride, Qt.Key_Delete, Qt.NoModifier)
    QApplication.sendEvent(editor, sobreposicao)
    assert not sobreposicao.isAccepted(), "sem área escolhida a Delete é da janela"
    editor.escolhida = 0
    sobreposicao = QKeyEvent(QEvent.ShortcutOverride, Qt.Key_Delete, Qt.NoModifier)
    QApplication.sendEvent(editor, sobreposicao)
    assert sobreposicao.isAccepted(), "com a área escolhida a Delete é do editor"
    editor.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier))
    assert len(editor.selecao) == 0, "a área não foi apagada"
    assert not janela.projeto.paginas[tela.indice_pagina].em_branco


@pytest.mark.parametrize("ferramenta", [FERRAMENTA_CORTAR, FERRAMENTA_ENDIREITAR, "retangulo",
                                        "mao"])
def test_os_dois_botoes_em_qualquer_pagina(janela, pasta, ferramenta):
    """Samuel, 09/10: "Essa opção de tirar do livro ou deixar folha em branco eu quero ter em
    outras paginas". Os dois botões ficam no alto do painel Propriedades, em toda ferramenta e em
    toda página (não só na que tem o aviso "Página sem conteúdo"), e fazem o que dizem."""
    tela = _abrir(janela, pasta, marcadas=(), folhas=3)
    tela.trilha.escolher(ferramenta)
    tela.paineis.abrir("props")
    _assentar()
    for indice in range(len(janela.projeto.paginas)):
        tela.ir_para_pagina(indice)
        _assentar()
        pagina = janela.projeto.paginas[indice]
        assert not pagina.alertas_pendentes            # nenhuma tem aviso
        branco, tirar = tela.botao_em_branco, tela.botao_tirar_do_livro
        assert branco.isVisible() and tirar.isVisible(), (ferramenta, indice)
        assert branco.isEnabled() and tirar.isEnabled()
        assert branco.text() == "deixar em branco" and tirar.text() == "tirar do livro"
    tela.ir_para_pagina(2)
    tela.botao_em_branco.click()
    assert janela.projeto.paginas[2].em_branco and not janela.projeto.paginas[2].apagada
    assert tela.botao_em_branco.text() == "voltar a página"
    tela.botao_tirar_do_livro.click()
    assert janela.projeto.paginas[2].apagada


# --- Ferramentas no menu e o balão com nome e letra (teste do Kaique; R8 302 C) ----------------


def test_o_menu_ferramentas_tem_dividir_cortar_endireitar_e_troca_a_ferramenta(janela, pasta):
    tela = _abrir(janela, pasta, marcadas=())
    menu = janela.menu.menus["Ferramentas"]
    textos = [a.text().split("\t")[0] for a in menu.actions() if not a.isSeparator()]
    for ferramenta in TODAS_AS_FERRAMENTAS:
        assert NOMES[ferramenta] in textos, NOMES[ferramenta]
    # a letra do atalho aparece ao lado do nome (coluna da direita do menu)
    assert janela.menu.acoes["usar_retangulo"].text() == "Retângulo\tR"
    for ferramenta, aba in ((FERRAMENTA_ENDIREITAR, "angulo"), (FERRAMENTA_DIVIDIR, "corte"),
                            (FERRAMENTA_CORTAR, "bordas"), ("laco", "marcar")):
        janela.menu.acoes[f"usar_{ferramenta}"].trigger()
        assert tela.aba_atual == aba
        assert tela.trilha.ferramenta == ferramenta
        assert janela.menu.acoes[f"usar_{ferramenta}"].isChecked(), "a marca do menu não acompanhou"
    tela.trilha.escolher("zoom")                      # pela trilha: o menu acompanha
    assert janela.menu.acoes["usar_zoom"].isChecked()


def test_o_balao_da_trilha_aparece_com_o_nome_e_a_letra(janela, pasta):
    """R8 302 C: ao parar o mouse em cima, o balão mostra o nome e a letra (e as outras do mesmo
    botão). O evento de balão do Qt chega à trilha e o QToolTip aparece com o texto."""
    tela = _abrir(janela, pasta, marcadas=())
    trilha = tela.trilha
    for indice, ret in trilha.retangulos().items():
        ferramenta = trilha.a_vista(indice)
        evento = QHelpEvent(QEvent.ToolTip, ret.center(), trilha.mapToGlobal(ret.center()))
        QApplication.sendEvent(trilha, evento)
        texto = QToolTip.text()
        assert QToolTip.isVisible(), NOMES[ferramenta]
        assert NOMES[ferramenta] in texto
        letra = tecla_de(ferramenta)
        if letra:
            assert f"[{letra}]" in texto, (NOMES[ferramenta], texto)
    QToolTip.hideText()


# --- A área de trabalho 1 (R7 203 D + R14 902 C) -----------------------------------------------


def test_de_fabrica_icones_na_borda_tudo_fechado(janela, pasta):
    tela = _abrir(janela, pasta, marcadas=())
    paineis = tela.paineis
    assert paineis.jeito == "icones"
    assert paineis.aberto is None and paineis.icones.isVisible() and not paineis.sanfona.isVisible()
    assert janela.menu.acoes["lado_icones"].isChecked()


def test_area_de_trabalho_1_pelo_menu_ver(janela, pasta):
    """R14 902 C: no menu Ver. A sanfona: os painéis empilhados, o Automático aberto, os outros
    com a linha de título; clicar numa linha abre aquele painel ali; a escolha fica guardada."""
    from ui.widgets.paineis import jeito_guardado

    tela = _abrir(janela, pasta, marcadas=())
    paineis = tela.paineis
    ver = janela.menu.menus["Ver"]
    assert any(a.text() == "Lado direito" for a in ver.actions())
    janela.menu.acoes["lado_sanfona"].trigger()
    _assentar()
    assert paineis.jeito == "sanfona" and jeito_guardado() == "sanfona"
    assert paineis.sanfona.isVisible() and not paineis.icones.isVisible()
    assert paineis.aberto == "automatico" and paineis.automatico.isVisible()
    linhas = paineis.linhas_da_sanfona
    assert not linhas["automatico"].isVisible()      # o aberto mostra o cabeçalho dele
    assert all(linhas[c].isVisible() for c in ("revisar", "props", "filtro", "historico"))
    # a página não fica por baixo: a coluna empurra a página
    assert tela.area_imagem.mapTo(tela, tela.area_imagem.rect().topRight()).x() < \
        paineis.sanfona.mapTo(tela, QPoint(0, 0)).x()
    linhas["historico"].clicada.emit("historico")
    _assentar()
    assert paineis.aberto == "historico" and paineis.historico.isVisible()
    assert linhas["automatico"].isVisible() and not linhas["historico"].isVisible()
    assert janela.menu.acoes["lado_sanfona"].isChecked()
    janela.menu.acoes["lado_icones"].trigger()
    _assentar()
    assert paineis.jeito == "icones" and paineis.icones.isVisible() and not paineis.sanfona.isVisible()
    assert jeito_guardado() == "icones"


def test_area_de_trabalho_1_nas_configuracoes(janela, pasta):
    """R14 902 C: nas Configurações (Aparência), pelo mesmo caminho do menu."""
    from ui.tela_configuracoes import TelaConfiguracoes

    tela = _abrir(janela, pasta, marcadas=())
    configuracoes = TelaConfiguracoes(janela)
    botoes = configuracoes.botoes_lado
    assert set(botoes) == {"icones", "sanfona"} and botoes["icones"].isChecked()
    assert "área de trabalho 1" in botoes["sanfona"].text()
    botoes["sanfona"].setChecked(True)
    _assentar()
    assert tela.paineis.jeito == "sanfona"
    assert janela.menu.acoes["lado_sanfona"].isChecked(), "o menu Ver não acompanhou"
    botoes["icones"].setChecked(True)
    assert tela.paineis.jeito == "icones"
    configuracoes.close()


def test_a_area_de_trabalho_1_volta_no_proximo_programa(janela, pasta):
    """A escolha vale para a próxima vez que o programa abrir (como o tema)."""
    from ui.janela_principal import JanelaPrincipal

    janela._trocar_lado_direito("sanfona")
    outra = JanelaPrincipal()
    try:
        assert outra.tela_conferir.paineis.jeito == "sanfona"
        assert outra.menu.acoes["lado_sanfona"].isChecked()
    finally:
        outra.close()
        janela._trocar_lado_direito("icones")


# --- Caixinha com quadrado (lista única 2.2) ---------------------------------------------------


def _cores_do_quadrado(caixa: QCheckBox) -> set[tuple[int, int, int]]:
    """As cores dos pixels do quadradinho da caixinha (o canto esquerdo dela)."""
    caixa.resize(caixa.sizeHint())
    imagem = caixa.grab().toImage()
    altura = imagem.height()
    cores = set()
    for x in range(0, min(24, imagem.width())):
        for y in range(altura):
            c = QColor(imagem.pixel(x, y))
            cores.add((c.red(), c.green(), c.blue()))
    return cores


def test_caixinha_marcada_tem_quadrado_azul_e_desmarcada_tem_quadrado(janela, pasta):
    """Lista única 2.2 (23/10): "Caixinha marcada aparece só como um tique, sem quadrado: fácil
    desmarcar sem querer". Agora, em todas as caixinhas do programa (a folha do tema), a marcada é
    um quadrado azul cheio com o tique branco e a desmarcada um quadrado com borda."""
    from ui import estilo

    folha = estilo.folha()
    assert "QCheckBox::indicator:checked" in folha and "border-radius: 4px" in folha
    janela.abrir_livro(str(_pdf(pasta, folhas=2)))
    janela.resize(1280, 657)
    janela.show()
    _assentar()
    azul = QColor(estilo.cor("azul"))
    # uma das caixinhas do Automático (era a tela "O que fazer" até a etapa 3)
    caixa = janela.abrir_o_automatico("cortar").controles["cortar_sobra"]
    _assentar()
    caixa.setChecked(True)
    marcada = _cores_do_quadrado(caixa)
    perto = [c for c in marcada if abs(c[0] - azul.red()) + abs(c[1] - azul.green())
             + abs(c[2] - azul.blue()) < 30]
    assert perto, "a caixinha marcada não tem o quadrado azul"
    assert any(min(c) > 230 for c in marcada), "falta o tique branco"
    caixa.setChecked(False)
    desmarcada = _cores_do_quadrado(caixa)
    borda = QColor(estilo.cor("fraco"))
    assert any(abs(c[0] - borda.red()) + abs(c[1] - borda.green()) + abs(c[2] - borda.blue()) < 40
               for c in desmarcada), "a caixinha desmarcada não tem o quadrado"
