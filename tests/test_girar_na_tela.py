"""Girar a folha na tela (item 2.3; provisório até o layout).

Pedido do Samuel (conferência 14, G1): "(c) Os dois" - botões numa barra em
cima da página, com o "aplicar em", e também no menu Página com teclas. A
aparência fica para o agente de layout com ele.

Testes de máquina (sem janela na tela, tests/conftest.py):
    - a barrinha existe, na linha das abas, sem emoji, e cabe na janela de
      1280 x 657 e na mínima de 1000 px (aí só os ícones);
    - cada botão gira as folhas do "aplicar em", numa ação só do desfazer;
    - o menu Página tem os três giros e o "Aplicar o giro em", que anda junto
      com a lista da barrinha;
    - Ctrl+Esquerda e Ctrl+Direita não brigam com nenhuma outra tecla, e a
      tecla R ficou só para o Retângulo;
    - o botão "girar" de sempre (aba Onde cortar) continua girando 1/4 à direita.
"""

from __future__ import annotations

from tests.ajudante_do_automatico import rodar_como_o_conferir  # etapa 3 da obra

import pytest

fitz = pytest.importorskip("fitz")

from PySide6.QtCore import QEvent, Qt  # noqa: E402
from PySide6.QtGui import QKeyEvent, QKeySequence  # noqa: E402

import atalhos  # noqa: E402
from core import girar, pipeline  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _pdf,
    app,
    janela,
    pasta,
)


def _aberta(janela, pasta, folhas=5, dividir=False):
    janela.abrir_livro(str(_pdf(pasta, folhas=folhas)))
    # etapa 3 da obra: o antigo "Conferir" (com "Dividir" marcado, se pedido;
    # desde o item 2.1 o livro novo nao divide sozinho) roda pelo Automatico
    from tests.ajudante_do_automatico import rodar_como_o_conferir

    rodar_como_o_conferir(janela, sempre=True, dividir_folhas=dividir)
    tela = janela.tela_conferir
    janela.resize(1280, 657)
    janela.show()
    return tela


def _rotacoes(janela):
    return [f.rotacao for f in janela.projeto.folhas]


def test_o_girar_mora_no_propriedades_e_no_canto_da_pagina_sem_emoji(janela, pasta):
    """Rodada 12 do layout, 703 ("Quero a opção B e D"): o bloco "Girar a
    folha" no alto do painel Propriedades e botoes pequenos no canto de cima
    da area da pagina. Na etapa 2 a barrinha ficava na linha dos menus."""
    tela = _aberta(janela, pasta)
    barra, canto = tela.barra_girar, tela.girar_do_canto
    assert tela.paineis.propriedades.isAncestorOf(barra)
    assert not janela.linha_dos_menus.isAncestorOf(barra), "saiu da linha dos menus"
    assert canto.parentWidget() is tela.area_imagem
    assert not tela.barra_abas.isVisible(), "sem abas na tela"
    # o nome de cada botao
    textos = [barra._textos[g] for g in barra.botoes_de_giro]
    assert textos == ["¼ à esquerda", "¼ à direita", "meia volta"]
    assert [b.text() for b in barra.botoes_de_giro.values()] == textos
    itens = [barra.combo_alcance.itemText(i) for i in range(barra.combo_alcance.count())]
    # rodada 12 do layout, 709 B: as palavras da lista do girar dizem "folha"
    # (a do endireitar diz "página"); os codigos de dentro nao mudaram
    assert itens == ["só esta folha", "todas as folhas", "daqui em diante", "só as pares",
                     "só as ímpares"]
    dados = [barra.combo_alcance.itemData(i) for i in range(barra.combo_alcance.count())]
    assert dados == list(girar.ALCANCES)
    assert barra.alcance() == girar.ALCANCE_ESTA, "começa no mais seguro"
    for texto in textos + itens + [barra.rotulo.text(), barra.rotulo_alcance.text()]:
        assert all(ord(c) < 0x2000 for c in texto), texto
    for botao in list(barra.botoes_de_giro.values()) + list(canto.botoes_de_giro.values()):
        assert not botao.icon().isNull(), "pista visual: a seta desenhada"
    assert all(b.text() == "" for b in canto.botoes_de_giro.values()), "no canto, so o icone"
    assert all("só esta folha" in b.toolTip() for b in canto.botoes_de_giro.values())


@pytest.mark.parametrize("largura, altura", [(1280, 657), (1000, 680)])
def test_os_botoes_do_canto_ficam_dentro_da_area_da_pagina(janela, pasta, app, largura, altura):
    """Os tres botoes pequenos ficam no canto direito de cima da area da
    pagina, inteiros dentro dela, com o painel fechado ou aberto (a area
    encolhe e eles acompanham)."""
    tela = _aberta(janela, pasta)
    janela.resize(largura, altura)
    canto, area = tela.girar_do_canto, tela.area_imagem
    for painel in (None, "props"):
        if painel:
            tela.paineis.abrir(painel)
        for _ in range(5):
            app.processEvents()
        assert canto.isVisible()
        assert canto.geometry().right() <= area.width() - 1
        assert area.width() - canto.geometry().right() <= 16, "encostado no canto direito"
        assert 0 <= canto.geometry().top() <= 12
        assert menus_inteiros(janela)


def menus_inteiros(janela) -> bool:
    """Os menus nunca sao espremidos (o Qt os esconderia atras de um "...")."""
    return janela.menu.width() >= janela.menu.sizeHint().width()


def test_os_botoes_do_canto_giram_so_esta_folha(janela, pasta):
    """Rodada 13 do layout, 803 B ("Só no painel"): a lista "aplicar em" fica
    so no painel; os botoes do canto giram sempre so a folha da vez, mesmo
    com "todas as folhas" escolhido no painel."""
    tela = _aberta(janela, pasta)
    tela.ir_para_pagina(2)
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    feitas = len(janela.acoes.feitas)
    tela.girar_do_canto.botoes_de_giro[girar.GIRO_DIREITA].click()
    assert _rotacoes(janela) == [0, 0, 90, 0, 0]
    assert len(janela.acoes.feitas) == feitas + 1
    tela.girar_do_canto.botoes_de_giro[girar.GIRO_MEIA_VOLTA].click()
    assert _rotacoes(janela) == [0, 0, 270, 0, 0]
    # o do painel continua obedecendo ao "aplicar em"
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    assert _rotacoes(janela) == [180] * 5


@pytest.mark.parametrize("alcance, giro, atual, esperado", [
    (girar.ALCANCE_ESTA, girar.GIRO_DIREITA, 2, [0, 0, 90, 0, 0]),
    (girar.ALCANCE_TODAS, girar.GIRO_ESQUERDA, 2, [270, 270, 270, 270, 270]),
    (girar.ALCANCE_DAQUI, girar.GIRO_MEIA_VOLTA, 2, [0, 0, 180, 180, 180]),
    # "so as pares" de uma folha par (folha 4): na impar ela avisa (abaixo)
    (girar.ALCANCE_PARES, girar.GIRO_DIREITA, 3, [0, 90, 0, 90, 0]),
    (girar.ALCANCE_IMPARES, girar.GIRO_DIREITA, 2, [90, 0, 90, 0, 90]),
])
def test_cada_botao_gira_as_folhas_do_aplicar_em(janela, pasta, alcance, giro, atual, esperado):
    tela = _aberta(janela, pasta)
    tela.ir_para_pagina(atual)
    assert tela.indice_folha == atual
    tela.barra_girar.definir_alcance(alcance)
    feitas = len(janela.acoes.feitas)
    tela.barra_girar.botoes_de_giro[giro].click()
    assert _rotacoes(janela) == esperado
    assert len(janela.acoes.feitas) == feitas + 1, "uma ação só do desfazer"
    assert janela.acoes.feitas[-1].descricao.startswith("Girar ")
    tela.desfazer()
    assert _rotacoes(janela) == [0, 0, 0, 0, 0]
    tela.refazer()
    assert _rotacoes(janela) == esperado


def test_o_menu_pagina_tem_os_tres_giros_e_o_aplicar_em(janela, pasta):
    tela = _aberta(janela, pasta)
    acoes = janela.menu.acoes
    assert acoes["girar_esquerda"].text() == "Girar ¼ à esquerda"
    assert acoes["girar"].text() == "Girar ¼ à direita"
    assert acoes["girar_meia_volta"].text() == "Girar meia volta"
    for chave in ("girar", "girar_esquerda", "girar_meia_volta",
                  *(f"giro_em_{a}" for a in girar.ALCANCES)):
        assert chave in janela.menu.ligadas, chave

    acoes["giro_em_todas"].trigger()
    assert tela.barra_girar.alcance() == girar.ALCANCE_TODAS, "o menu muda a barrinha"
    acoes["girar_esquerda"].trigger()
    assert _rotacoes(janela) == [270] * 5
    acoes["girar_meia_volta"].trigger()
    assert _rotacoes(janela) == [90] * 5
    tela.barra_girar.definir_alcance(girar.ALCANCE_PARES)
    assert acoes["giro_em_pares"].isChecked(), "a barrinha muda o menu"
    assert not acoes["giro_em_todas"].isChecked()
    tela.ir_para_pagina(1)                     # folha 2: "so as pares" vale daqui
    acoes["girar"].trigger()
    assert _rotacoes(janela) == [90, 180, 90, 180, 90]


def test_as_teclas_do_giro_nao_brigam_com_nenhuma_outra(janela):
    assert atalhos.tecla_atual("girar_esquerda") == "Ctrl+Left"
    assert atalhos.tecla_atual("girar") == "Ctrl+Right"
    usadas = [a.atual for a in atalhos.todas() if a.atual]
    repetidas = {t for t in usadas if usadas.count(t) > 1}
    assert not repetidas, repetidas
    atalhos_do_menu = [a.shortcut().toString() for a in janela.menu.acoes.values()
                       if not a.shortcut().isEmpty()]
    assert len(atalhos_do_menu) == len(set(atalhos_do_menu))
    assert janela.menu.acoes["girar"].shortcut() == QKeySequence("Ctrl+Right")
    # o balao dos botoes mostra a tecla, em portugues
    dica = janela.tela_conferir.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].toolTip()
    assert "Ctrl+seta para a direita" in dica


def test_a_tecla_do_menu_gira_de_verdade(janela, pasta, app):
    """Ctrl+Direita pelo caminho do Qt (atalho do menu), com a janela ativa."""
    tela = _aberta(janela, pasta)
    from PySide6.QtTest import QTest

    janela.raise_()
    janela.activateWindow()
    if not QTest.qWaitForWindowActive(janela, 2000):
        import warnings

        with warnings.catch_warnings():    # offscreen, depois de outras janelas
            warnings.simplefilter("ignore", DeprecationWarning)
            app.setActiveWindow(janela)
    app.processEvents()
    assert app.activeWindow() is janela

    QTest.keyClick(janela, Qt.Key_Right, Qt.ControlModifier)
    app.processEvents()
    assert _rotacoes(janela) == [90, 0, 0, 0, 0]
    assert tela.indice_folha == 0, "Ctrl+Direita não troca de página"
    QTest.keyClick(janela, Qt.Key_Left, Qt.ControlModifier)
    app.processEvents()
    assert _rotacoes(janela) == [0, 0, 0, 0, 0]


def test_a_tecla_r_ficou_so_para_o_retangulo(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta, folhas=5)))
    rodar_como_o_conferir(janela, sempre=True, detectar_regioes=True)  # com a aba Marcar
    tela = janela.tela_conferir
    assert "marcar" in tela._abas_ativas
    tela.escolher_ferramenta("elipse")
    evento = QKeyEvent(QEvent.KeyPress, Qt.Key_R, Qt.NoModifier, "r")
    assert tela.tratar_tecla(evento)
    assert tela.trilha.ferramenta == "retangulo"
    assert _rotacoes(janela) == [0, 0, 0, 0, 0]
    # nem com o Retangulo trocado para outra letra a R gira (antes girava)
    atalhos.redefinir("ferramenta_retangulo", "Q")
    try:
        tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, Qt.Key_R, Qt.NoModifier, "r"))
        assert _rotacoes(janela) == [0, 0, 0, 0, 0]
    finally:
        atalhos.restaurar_padrao("ferramenta_retangulo")


def test_no_dividir_ha_um_girar_so(janela, pasta):
    """O botao "girar" de sempre do Dividir fazia o mesmo que o "¼ à direita"
    do bloco "Girar a folha" (os dois: um quarto de volta a direita, com o
    "aplicar em"). Com o bloco no alto do painel Propriedades, o repetido saiu
    (13/10/2026); o giro de sempre continua, no bloco."""
    tela = _aberta(janela, pasta, dividir=True)
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("corte"))
    linha = tela.linhas_de_botoes["corte"]
    from PySide6.QtWidgets import QPushButton

    assert not [b for b in linha.findChildren(QPushButton) if b.text() == "girar"]
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    assert _rotacoes(janela) == [90, 0, 0, 0, 0]


def test_girar_grava_no_projeto(janela, pasta):
    """Fechar e abrir de novo: o giro continua (campo de sempre, rotacao)."""
    import json

    import projetos

    tela = _aberta(janela, pasta)
    tela.barra_girar.definir_alcance(girar.ALCANCE_IMPARES)
    tela.barra_girar.botoes_de_giro[girar.GIRO_MEIA_VOLTA].click()
    janela._salvar_agora()
    arquivos = list(projetos.pasta_dos_projetos().rglob("projeto.json"))
    assert arquivos
    dados = json.loads(arquivos[0].read_text(encoding="utf-8"))
    assert [f["rotacao"] for f in dados["folhas"]] == [180, 0, 180, 0, 180]


def test_com_zonas_ainda_no_formato_antigo_o_giro_espera(janela, pasta, monkeypatch):
    """Projeto de antes de 05/10 com a conversao das zonas ainda andando: girar
    antes de a pagina ser convertida levaria a zona para o lugar errado do
    papel. O giro espera, avisa, e pede a conversao; convertida, gira."""
    from core import zonas_na_folha as zf
    from core.selecao import GRAVURA, MAO, RETANGULO, Regiao

    # a previa (outro fio) nao converte a pagina no meio do teste
    monkeypatch.setattr(zf, "acompanhar", lambda pagina, geometria: False)
    tela = _aberta(janela, pasta)
    pagina = janela.projeto.paginas[0]
    pagina.selecao = [Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.1, 0.1), (0.4, 0.3)],
                             origem=MAO).para_dicionario()]
    pagina.geometria_das_zonas = None              # formato antigo
    pedidos = []
    monkeypatch.setattr(janela, "_comecar_a_converter_as_zonas", lambda: pedidos.append(1))
    tela.ir_para_pagina(0)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    assert _rotacoes(janela) == [0, 0, 0, 0, 0]
    assert janela.avisos and "preparando as marcações" in janela.avisos[-1]
    assert pedidos == [1]

    # outra folha (sem zonas antigas) gira normalmente
    tela.ir_para_pagina(3)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    assert _rotacoes(janela) == [0, 0, 0, 90, 0]

    # convertida (a geometria anotada), a folha 1 gira
    pagina.geometria_das_zonas = zf.geometria_do_desenho(400 / 560, 0, None, "inteira", None, 0.0)
    tela.ir_para_pagina(0)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    assert _rotacoes(janela) == [90, 0, 0, 90, 0]


@pytest.mark.parametrize("alcance, esperado", [
    (girar.ALCANCE_TODAS, [270, 270, 270, 270, 270]),
    (girar.ALCANCE_DAQUI, [0, 90, 270, 270, 270]),
    (girar.ALCANCE_IMPARES, [270, 90, 270, 270, 270]),
])
def test_aplicar_em_deixa_as_folhas_viradas_como_a_folha_da_vez(janela, pasta, alcance, esperado):
    """Decisao do Samuel (06/10/2026): "Todas ficam viradas como a folha da
    vez" (como o ScanTailor). Folhas com giros diferentes antes (feitos com
    "so esta"); na folha 3 (de cabeca para baixo), 1/4 a direita com o
    "aplicar em": a folha 3 vai a 270 e as escolhidas terminam em 270. Um
    Ctrl+Z devolve cada folha ao giro que ela tinha."""
    tela = _aberta(janela, pasta)
    barra = tela.barra_girar
    barra.definir_alcance(girar.ALCANCE_ESTA)
    for folha, giro in ((1, girar.GIRO_DIREITA), (2, girar.GIRO_MEIA_VOLTA),
                        (3, girar.GIRO_ESQUERDA)):
        tela.ir_para_pagina(folha)
        barra.botoes_de_giro[giro].click()
    antes = [0, 90, 180, 270, 0]
    assert _rotacoes(janela) == antes

    tela.ir_para_pagina(2)
    barra.definir_alcance(alcance)
    feitas = len(janela.acoes.feitas)
    barra.botoes_de_giro[girar.GIRO_DIREITA].click()
    assert _rotacoes(janela) == esperado
    assert len(janela.acoes.feitas) == feitas + 1, "uma ação só do desfazer"
    assert "viradas como a folha 3" in janela.acoes.feitas[-1].descricao
    tela.desfazer()
    assert _rotacoes(janela) == antes, "o desfazer devolve o giro de cada folha"
    tela.refazer()
    assert _rotacoes(janela) == esperado


def _com_giros_diferentes(janela, pasta):
    """Folhas 2, 3 e 4 ja giradas com "so esta": [0, 90, 180, 270, 0]."""
    tela = _aberta(janela, pasta)
    barra = tela.barra_girar
    barra.definir_alcance(girar.ALCANCE_ESTA)
    for folha, giro in ((1, girar.GIRO_DIREITA), (2, girar.GIRO_MEIA_VOLTA),
                        (3, girar.GIRO_ESQUERDA)):
        tela.ir_para_pagina(folha)
        barra.botoes_de_giro[giro].click()
    assert _rotacoes(janela) == [0, 90, 180, 270, 0]
    return tela


def test_so_as_pares_de_uma_folha_par_copia_o_giro_dela(janela, pasta):
    """Na folha 2 (a 90), 1/4 a direita com "so as pares": a folha 2 vai a
    180 e a outra par (folha 4) tambem; as impares nao mudam."""
    tela = _com_giros_diferentes(janela, pasta)
    tela.ir_para_pagina(1)
    tela.barra_girar.definir_alcance(girar.ALCANCE_PARES)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    assert _rotacoes(janela) == [0, 180, 180, 180, 0]
    assert "viradas como a folha 2" in janela.acoes.feitas[-1].descricao
    assert not janela.avisos


@pytest.mark.parametrize("alcance, folha, frase", [
    (girar.ALCANCE_PARES, 2, "Você está numa folha ímpar. Para girar só as pares, "
                             "vá a uma folha par e gire de lá."),
    (girar.ALCANCE_IMPARES, 1, "Você está numa folha par. Para girar só as ímpares, "
                              "vá a uma folha ímpar e gire de lá."),
], ids=["pares_na_impar", "impares_na_par"])
def test_folha_fora_do_aplicar_em_avisa_e_nao_gira(janela, pasta, alcance, folha, frase):
    """Decisao do Samuel (06/10/2026): "O programa avisa: 'va a uma folha
    par'". Nada muda no livro e nada entra no historico - pelo botao, pelo
    menu Pagina e pela tecla (os tres passam por _girar_folhas)."""
    tela = _com_giros_diferentes(janela, pasta)
    tela.ir_para_pagina(folha)
    tela.barra_girar.definir_alcance(alcance)
    feitas = len(janela.acoes.feitas)
    descricao = janela.acoes.descricao_desfazer()

    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    janela.menu.acoes["girar_meia_volta"].trigger()
    tela._girar_esquerda()

    assert _rotacoes(janela) == [0, 90, 180, 270, 0], "nada mudou no livro"
    assert len(janela.acoes.feitas) == feitas, "nada entrou no historico"
    assert janela.acoes.descricao_desfazer() == descricao
    assert janela.avisos == [frase] * 3
