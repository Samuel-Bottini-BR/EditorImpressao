"""O "Para revisar" na tela de conferir, depois das decisoes do Samuel
(rodadas 4 e 5 do "Para revisar", 07 a 09/10/2026). Testes de maquina: a tela
de verdade (TelaConferir) e montada sem aparecer, e os botoes sao clicados
com .click().

O que se cobra:
    - um aviso para cada coisa, cada um com os dois botoes: "Deixar em
      branco" e "Tirar do livro" (`rv5-em-branco`: "Fica assim");
    - o conserto rapido e um botao do proprio aviso: "Trazer de volta nesta
      página" (`rv5-erro-1-desenho`, `rv5-erro-6-so-texto`), com o lugar onde
      sumiu marcado; "Desfazer" na forca do preto escurecida;
    - "está bom" num motivo de uma pagina, em todas as paginas de um motivo e
      em tudo (`rv4-aviso-so-texto`), sempre com Ctrl+Z;
    - a janela "Antes de processar" lista as paginas e os motivos, com "ver"
      e "continuar assim mesmo" (`rv5-aviso-so-texto`).
A aparencia nao e cobrada aqui (fica com o agente de layout).
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QPushButton  # noqa: E402

from core import analise, avisos, misto  # noqa: E402
from core.filtros import PRETO_E_BRANCO  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import _pdf, app, pasta  # noqa: F401, E402 - fixtures
from tests.test_misto_consertos import _projeto_com_cor, leitor_rapido  # noqa: F401, E402

CAIXA = (0.10, 0.20, 0.30, 0.40)


@pytest.fixture
def tela(app, pasta):  # noqa: F811 - fixtures importadas
    """A tela de conferir de um livro de 4 paginas em Preto e branco com "So
    as letras" de fabrica (e ali que os avisos novos valem), na aba Filtro.
    O leitor de texto e trocado por um que nao acha nada (leitor_rapido): as
    previas de fundo nao medem a regra, e os avisos postos a mao ficam."""
    from historico_acoes import HistoricoAcoes
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    projeto = _projeto_com_cor()
    projeto.caminho_entrada = str(_pdf(pasta, folhas=4))
    projeto.paginas[0].tem_cor = False
    projeto.paginas[0].alertas = []
    projeto.misto_so_as_letras = True
    conferir = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, conferir)
    conferir.carregar(projeto, HistoricoAcoes(), previas)
    conferir.barra_abas.setCurrentIndex(conferir._abas_ativas.index("filtro"))
    conferir.ir_para_pagina(0)
    yield conferir
    previas.parar()


def _botoes(tela):
    return tela.botoes_de_sugestao["filtro"], tela.botoes_de_sugestao_2["filtro"]


def _por_aviso(tela, indice: int, codigos: list[str]):
    pagina = tela.projeto.paginas[indice]
    pagina.alertas = list(codigos)
    pagina.revisada = False
    tela.ir_para_pagina(indice)
    return pagina


# --- um aviso para cada coisa, com os dois botoes -------------------------------

@pytest.mark.parametrize("codigo", [analise.EM_BRANCO, analise.PAGINA_SEM_CONTEUDO])
def test_deixar_em_branco_pelo_botao_do_aviso(tela, codigo):
    pagina = _por_aviso(tela, 1, [codigo])
    primeiro, segundo = _botoes(tela)
    assert tela.texto_faixa.text() == analise.descrever(codigo).mensagem
    assert not primeiro.isHidden() and primeiro.text() == "Deixar em branco"
    assert not segundo.isHidden() and segundo.text() == "Tirar do livro"
    terceiro = tela.botoes_de_sugestao_3["filtro"]
    assert not terceiro.isHidden() and terceiro.text() == "está bom assim"

    primeiro.click()
    assert terceiro.isHidden()
    assert pagina.em_branco is True and pagina.apagada is False and pagina.revisada is True
    assert tela.botao_alertas.text() == "tudo certo"
    # a pagina fica no livro (a encadernacao nao muda)
    assert pagina in tela.projeto.paginas_ativas
    # a faixa diz o que vai acontecer e deixa voltar atras
    assert "em branco" in tela.texto_faixa.text()
    assert primeiro.text() == "voltar a página" and segundo.isHidden()
    primeiro.click()
    assert pagina.em_branco is False
    tela.desfazer()
    assert pagina.em_branco is True
    tela.desfazer()
    assert pagina.em_branco is False and pagina.revisada is False
    assert not primeiro.isHidden() and primeiro.text() == "Deixar em branco"


@pytest.mark.parametrize("codigo", [analise.EM_BRANCO, analise.PAGINA_SEM_CONTEUDO])
def test_tirar_do_livro_pelo_botao_do_aviso(tela, codigo):
    pagina = _por_aviso(tela, 2, [codigo])
    _botoes(tela)[1].click()
    assert pagina.apagada is True and pagina.em_branco is False
    assert pagina not in tela.projeto.paginas_ativas
    tela.desfazer()
    assert pagina.apagada is False


@pytest.mark.parametrize("codigo", [analise.EM_BRANCO, analise.PAGINA_SEM_CONTEUDO])
def test_esta_bom_assim_no_aviso_de_pagina_em_branco(tela, codigo):
    """O "Parece em branco" erra (Gladstone 18, que tem titulo): tem de dar para
    dizer "está bom" sem deixar em branco nem tirar do livro (verificador, 13/10)."""
    pagina = _por_aviso(tela, 1, [codigo])
    tela.botoes_de_sugestao_3["filtro"].click()
    assert pagina.alertas_pendentes == [] and tela.botao_alertas.text() == "tudo certo"
    assert pagina.em_branco is False and pagina.apagada is False, "a pagina nao muda"
    assert all(b.isHidden() for b in (*_botoes(tela), tela.botoes_de_sugestao_3["filtro"]))
    tela.desfazer()
    assert pagina.alertas_pendentes == [codigo]


def test_os_botoes_do_aviso_nao_ficam_com_o_teclado(tela):
    """Verificador, 13/10: depois de clicar num botao do aviso o foco ficava
    nele - a seta para a direita pulava de botao em vez de trocar de pagina e a
    barra de espaco apertava o botao (ate escondido)."""
    from PySide6.QtCore import Qt

    assert tela.botoes_de_sugestao and "filtro" in tela.botoes_de_sugestao
    assert set(tela.botoes_de_sugestao) == set(tela.botoes_de_sugestao_2) == set(
        tela.botoes_de_sugestao_3)
    for botoes in (tela.botoes_de_sugestao, tela.botoes_de_sugestao_2, tela.botoes_de_sugestao_3):
        for aba, botao in botoes.items():
            assert botao.focusPolicy() == Qt.NoFocus, aba


def test_dois_cliques_no_cartao_do_filtro_nao_dao_a_pagina_por_conferida(tela):
    """Verificador, 13/10: dois cliques no cartao (o jeito de abrir o "Ver de
    perto") gravavam "Preto e branco para Preto e branco", a pagina ficava
    conferida e o aviso sumia."""
    from core.filtros import MELHORAR

    pagina = _por_aviso(tela, 0, [analise.DESENHO_APAGADO])
    feitas = len(tela.acoes.feitas)
    tela._escolher_filtro(PRETO_E_BRANCO)              # o filtro que ja esta (o clique no cartao)
    tela._escolher_filtro(PRETO_E_BRANCO)
    assert len(tela.acoes.feitas) == feitas, "nenhuma acao gravada"
    assert pagina.revisada is False and pagina.alertas_pendentes == [analise.DESENHO_APAGADO]
    assert "1 página" in tela.botao_alertas.text()
    # trocar de verdade continua gravando (e dando a pagina por conferida, como sempre)
    tela._escolher_filtro(MELHORAR)
    assert len(tela.acoes.feitas) == feitas + 1 and pagina.filtro == MELHORAR and pagina.revisada


def test_usar_mais_escuro_nao_aparece_com_a_forca_ja_no_mais_escuro(tela):
    """Verificador, 13/10 (Egenloff 3): o aviso "Texto falhado" oferecia "usar
    mais escuro" com a forca ja em 85."""
    from core.pipeline import FORCA_DO_REFORCO

    pagina = tela.projeto.paginas[0]
    pagina.forca_preto = FORCA_DO_REFORCO
    pagina.reforco_desfeito = True
    _por_aviso(tela, 0, [analise.TEXTO_FALHADO])
    primeiro, segundo = _botoes(tela)
    assert primeiro.text() == "está bom assim" and not primeiro.isHidden()
    assert segundo.isHidden()
    primeiro.click()                                   # o botao que aparece e o que age
    assert pagina.alertas_pendentes == [] and pagina.forca_preto == FORCA_DO_REFORCO


# --- o conserto rapido e um botao do aviso ---------------------------------------

def test_trazer_de_volta_quando_o_jeito_de_fabrica_apagou_um_desenho(tela):
    pagina = _por_aviso(tela, 0, [analise.DESENHO_APAGADO])
    primeiro, segundo = _botoes(tela)
    assert primeiro.text() == "Trazer de volta nesta página" and not primeiro.isHidden()
    assert segundo.text() == "está bom assim" and not segundo.isHidden()
    primeiro.click()
    assert pagina.misto_fora_do_texto == misto.FORA_TUDO, "so esta pagina passa a guardar tudo"
    assert tela.projeto.misto_fora_do_texto == misto.FORA_REDE, "o livro nao muda"
    assert all(p.misto_fora_do_texto is None for p in tela.projeto.paginas[1:])
    # no "Guardar tudo" nada some: o aviso sai sozinho
    assert analise.DESENHO_APAGADO not in pagina.alertas
    assert primeiro.isHidden() and tela.botao_alertas.text() == "tudo certo"
    tela.desfazer()
    assert pagina.misto_fora_do_texto is None


def test_trazer_de_volta_quando_o_guardar_so_o_texto_apagou(tela):
    tela.projeto.misto_fora_do_texto = misto.FORA_APAGAR
    pagina = _por_aviso(tela, 0, [analise.SO_O_TEXTO_APAGOU])
    primeiro, _segundo = _botoes(tela)
    assert primeiro.text() == "Trazer de volta nesta página"
    primeiro.click()
    assert pagina.misto_fora_do_texto == misto.FORA_REDE, "esta pagina passa a guardar a tinta forte"
    assert tela.projeto.misto_fora_do_texto == misto.FORA_APAGAR, "as outras continuam so com o texto"


def test_o_lugar_onde_sumiu_aparece_marcado(tela):
    pagina = _por_aviso(tela, 0, [analise.DESENHO_APAGADO])
    setattr(pagina, "_marcas_do_aviso", {analise.DESENHO_APAGADO: [CAIXA]})   # o que o desenho guarda
    tela.atualizar()
    assert tela.cartoes[PRETO_E_BRANCO].amostra._marcas == [CAIXA]
    if "marcar" in tela._abas_ativas:
        assert tela.editor_selecao._marcas_do_aviso == [CAIXA], "a aba Marcar mostra o mesmo lugar"
    # pagina dada como boa: a marca some
    tela._marcar_revisada()
    assert tela.cartoes[PRETO_E_BRANCO].amostra._marcas == []
    # outra pagina, sem aviso: sem marca
    tela.desfazer()
    assert tela.cartoes[PRETO_E_BRANCO].amostra._marcas == [CAIXA]
    tela.ir_para_pagina(1)
    assert tela.cartoes[PRETO_E_BRANCO].amostra._marcas == []


def test_forca_do_preto_escurecida_tem_o_desfazer(tela):
    from core.pipeline import FORCA_DO_REFORCO

    pagina = tela.projeto.paginas[0]
    pagina.forca_preto, pagina.forca_antes_do_reforco = FORCA_DO_REFORCO, 50   # o que o desenho faz
    tela.atualizar()
    assert pagina.alertas_pendentes == [analise.FORCA_REFORCADA]
    primeiro, segundo = _botoes(tela)
    assert primeiro.text() == "Desfazer" and segundo.text() == "está bom assim"
    assert tela.texto_faixa.text() == analise.descrever(analise.FORCA_REFORCADA).mensagem
    primeiro.click()
    assert pagina.forca_preto == 50 and pagina.forca_antes_do_reforco is None
    assert pagina.reforco_desfeito is True
    assert analise.FORCA_REFORCADA not in pagina.alertas
    # o Ctrl+Z do "Desfazer" traz o reforco (e o aviso) de volta
    tela.desfazer()
    assert pagina.forca_preto == FORCA_DO_REFORCO and pagina.forca_antes_do_reforco == 50
    assert pagina.alertas_pendentes == [analise.FORCA_REFORCADA]


def test_usar_mais_escuro_do_texto_falhado_funciona(tela):
    """Ate 12/10/2026 os botoes "usar mais escuro" / "usar mais fraco" caiam em
    "Não consegui fazer isso agora" (o metodo que eles chamavam nao existia)."""
    from core.pipeline import FORCA_DO_REFORCO

    pagina = _por_aviso(tela, 0, [analise.TEXTO_FALHADO])
    pagina.reforco_desfeito = True                     # a pessoa ja tinha desfeito o reforco
    avisou = []
    tela._avisar_problema = lambda: avisou.append(1)
    primeiro, _segundo = _botoes(tela)
    assert primeiro.text() == "usar mais escuro"
    primeiro.click()
    assert avisou == [], "o botao nao pode cair no aviso de problema"
    assert pagina.forca_preto == FORCA_DO_REFORCO
    tela.desfazer()
    assert pagina.forca_preto == 50


# --- "está bom" em cada nivel ------------------------------------------------------

def test_esta_bom_num_motivo_mostra_o_proximo_motivo_da_pagina(tela):
    pagina = _por_aviso(tela, 0, [analise.DESENHO_APAGADO, analise.FIGURA_ALEM_DA_GRAVURA])
    _primeiro, segundo = _botoes(tela)
    assert analise.descrever(analise.DESENHO_APAGADO).mensagem in tela.texto_faixa.text()
    assert "aviso 1 de 2" in tela.texto_faixa.text()
    segundo.click()                                     # "está bom assim" so no desenho apagado
    assert pagina.alertas_aceitos == [analise.DESENHO_APAGADO] and not pagina.revisada
    assert tela.texto_faixa.text() == analise.descrever(analise.FIGURA_ALEM_DA_GRAVURA).mensagem
    assert "1 página" in tela.botao_alertas.text(), "a pagina continua na lista pelo outro motivo"
    primeiro, _ = _botoes(tela)
    assert primeiro.text() == "está bom assim"
    primeiro.click()
    assert pagina.alertas_pendentes == [] and tela.botao_alertas.text() == "tudo certo"
    tela.desfazer()
    assert pagina.alertas_pendentes == [analise.FIGURA_ALEM_DA_GRAVURA]
    tela.desfazer()
    assert pagina.alertas_pendentes == [analise.DESENHO_APAGADO, analise.FIGURA_ALEM_DA_GRAVURA]


def _botao_do_painel(tela, comeco: str, qual: int = 0) -> QPushButton:
    achados = [b for b in tela.paineis.para_revisar.findChildren(QPushButton)
               if getattr(b, "_texto_completo", b.text()).startswith(comeco)]
    assert len(achados) > qual, (comeco, [getattr(b, "_texto_completo", "") for b in
                                          tela.paineis.para_revisar.findChildren(QPushButton)])
    return achados[qual]


def test_esta_bom_em_todas_as_paginas_de_um_motivo_pelo_painel(tela):
    for i in (0, 1, 3):
        tela.projeto.paginas[i].alertas = [analise.FAIXA_NA_BEIRADA]
    tela.projeto.paginas[2].alertas = [analise.DESENHO_APAGADO, analise.FAIXA_NA_BEIRADA]
    tela.atualizar()
    assert "4 páginas" in tela.botao_alertas.text()
    # o primeiro motivo do painel e o de mais paginas: a faixa (4)
    _botao_do_painel(tela, "está bom: todas").click()
    assert all(analise.FAIXA_NA_BEIRADA in p.alertas_aceitos for p in tela.projeto.paginas)
    assert "1 página" in tela.botao_alertas.text(), "sobra a pagina 3, pelo desenho apagado"
    assert tela.projeto.paginas[2].alertas_pendentes == [analise.DESENHO_APAGADO]
    tela.desfazer()                                     # uma acao so
    assert "4 páginas" in tela.botao_alertas.text()


def test_esta_bom_em_tudo_pelo_painel(tela):
    for i in range(4):
        tela.projeto.paginas[i].alertas = [analise.FAIXA_NA_BEIRADA, analise.FIGURA_ALEM_DA_GRAVURA]
    tela.atualizar()
    _botao_do_painel(tela, "está bom em tudo").click()
    assert tela.botao_alertas.text() == "tudo certo"
    assert avisos.pendentes_do_livro(tela.projeto) == []
    assert all(len(p.alertas) == 2 for p in tela.projeto.paginas), "as paginas nao mudam"
    tela.desfazer()
    assert "4 páginas" in tela.botao_alertas.text()


def test_o_esta_certo_da_aba_continua_valendo_para_a_pagina_inteira(tela):
    pagina = _por_aviso(tela, 0, [analise.DESENHO_APAGADO, analise.FIGURA_ALEM_DA_GRAVURA])
    tela._marcar_revisada()
    assert pagina.revisada and pagina.alertas_pendentes == []
    assert tela.botao_alertas.text() == "tudo certo"


# --- a lista grande e a janela "Antes de processar" --------------------------------

def _lista(tela):
    for i in (0, 2):
        tela.projeto.paginas[i].alertas = [analise.FAIXA_NA_BEIRADA]
    tela.projeto.paginas[1].alertas = [analise.DESENHO_APAGADO, analise.FAIXA_NA_BEIRADA]
    tela.atualizar()
    return avisos.pendentes_do_livro(tela.projeto)


def test_a_janela_lista_as_paginas_e_os_motivos(tela):
    from ui.janela_dos_avisos import ACEITAR, CONTINUAR, FECHAR, VER, JanelaDosAvisos

    lista = _lista(tela)
    janela = JanelaDosAvisos(lista, antes_de_processar=True)
    assert janela.windowTitle() == "Antes de processar"
    assert janela.linhas() == [
        "Página 1  -  Faixa escura na beirada",
        "Página 2  -  Desenho apagado",
        "Página 2  -  Faixa escura na beirada",
        "Página 3  -  Faixa escura na beirada",
    ]
    assert "3 páginas" in janela.rotulo.text()
    assert janela.botao_ver.text() == "ver"
    assert janela.botao_continuar.text() == "continuar assim mesmo"
    assert (janela.botao_todas.text(), janela.botao_nenhuma.text()) == ("Selecionar todas", "Nenhuma")

    # "está bom nas marcadas" sem nada marcado nao faz nada
    janela.botao_aceitar.click()
    assert janela.escolha == FECHAR and janela.marcados == []
    janela.botao_todas.click()
    assert len(janela.avisos_marcados()) == 4
    janela.botao_nenhuma.click()
    assert janela.avisos_marcados() == []

    # so as paginas de um motivo ("todas as paginas com aquele problema")
    janela.combo_motivo.setCurrentIndex(janela.combo_motivo.findData(analise.FAIXA_NA_BEIRADA))
    assert len(janela.linhas()) == 3 and all("Faixa" in t for t in janela.linhas())
    janela.botao_todas.click()
    janela.botao_aceitar.click()
    assert janela.escolha == ACEITAR
    assert [(a.indice, a.codigo) for a in janela.marcados] == [
        (0, analise.FAIXA_NA_BEIRADA), (1, analise.FAIXA_NA_BEIRADA), (2, analise.FAIXA_NA_BEIRADA)]

    outra = JanelaDosAvisos(lista, antes_de_processar=True)
    outra.lista.setCurrentRow(3)
    outra.botao_ver.click()
    assert outra.escolha == VER and outra.aviso_para_ver.indice == 2
    terceira = JanelaDosAvisos(lista, antes_de_processar=True)
    terceira.botao_continuar.click()
    assert terceira.escolha == CONTINUAR
    # no seletor do painel o ultimo botao so fecha
    seletor = JanelaDosAvisos(lista)
    assert seletor.windowTitle() == "Para revisar" and seletor.botao_continuar.text() == "fechar"
    seletor.botao_continuar.click()
    assert seletor.escolha == FECHAR


def test_antes_de_processar_menor_e_em_duas_filas(tela):
    """Samuel, 21/10/2026 (`pr-antes-de-processar`): "ficou meio embolado, deve
    ficar mais claro e não tão grande." A janela abre menor que os 560 x 520 de
    antes e cabe no notebook do Kaique (1280 x 657); a frase de cima em duas
    linhas; os botões em duas filas (a de cima da lista e a de baixo) em vez
    de três; nenhum controle sumiu."""
    from PySide6.QtWidgets import QApplication

    from ui.janela_dos_avisos import TAMANHO_DA_JANELA, JanelaDosAvisos

    janela = JanelaDosAvisos(_lista(tela), antes_de_processar=True)
    janela.show()
    QApplication.processEvents()
    # a largura de verdade depende das letras do Windows (522 pontos na janela de verdade,
    # relatorios/layout-antes-de-processar); aqui, sem as letras do Windows, so a altura
    assert TAMANHO_DA_JANELA[0] * TAMANHO_DA_JANELA[1] < 560 * 520 * 0.8
    assert janela.height() <= 657 * 0.65
    assert "3 páginas" in janela.rotulo.text()
    assert janela.pergunta.text() == "Quer ver antes ou continuar assim mesmo?"
    assert janela.rotulo.y() < janela.pergunta.y() < janela.combo_motivo.y()
    botoes = [b for b in janela.findChildren(QPushButton) if b.isVisible()]
    assert {b.text() for b in botoes} == {"Selecionar todas", "Nenhuma", "está bom nas marcadas",
                                         "ver", "continuar assim mesmo"}
    cima = {b.text() for b in botoes if b.y() < janela.lista.y()}
    baixo = {b.text() for b in botoes if b.y() > janela.lista.y() + janela.lista.height()}
    assert cima == {"Selecionar todas", "Nenhuma"}
    assert baixo == {"está bom nas marcadas", "ver", "continuar assim mesmo"}
    meios = [b.y() + b.height() / 2 for b in botoes if b.text() in baixo]
    assert max(meios) - min(meios) <= 3, "uma fila só embaixo"
    janela.close()


@pytest.fixture
def janela_dos_avisos(monkeypatch):
    """Troca o exec() da lista grande por um roteiro: cada vez que ela abre,
    roda a proxima funcao de `roteiro` (que recebe a janela) em vez de esperar
    a pessoa. Guarda as janelas abertas em `abertas`."""
    from ui.janela_dos_avisos import JanelaDosAvisos

    estado = {"roteiro": [], "abertas": []}

    def falso(self):
        estado["abertas"].append(self)
        assert estado["roteiro"], "a janela abriu mais vezes do que o teste esperava"
        estado["roteiro"].pop(0)(self)
        return 0

    monkeypatch.setattr(JanelaDosAvisos, "exec", falso)
    return estado


def test_processar_com_avisos_para_e_mostra_a_lista(tela, janela_dos_avisos):
    _lista(tela)
    pediu = []
    tela.processar.connect(lambda: pediu.append(1))

    # "ver": vai para a pagina e NAO processa
    def ver_a_pagina_3(janela):
        assert janela.antes_de_processar and len(janela.linhas()) == 4
        janela.lista.setCurrentRow(3)
        janela.botao_ver.click()

    janela_dos_avisos["roteiro"] = [ver_a_pagina_3]
    tela._pedir_processamento()
    assert pediu == [] and tela.indice_pagina == 2

    # fechar no X: nao processa
    janela_dos_avisos["roteiro"] = [lambda janela: janela.reject()]
    tela._pedir_processamento()
    assert pediu == []

    # "continuar assim mesmo": processa, e os avisos ficam como estavam
    janela_dos_avisos["roteiro"] = [lambda janela: janela.botao_continuar.click()]
    tela._pedir_processamento()
    assert pediu == [1]
    assert len(avisos.pendentes_do_livro(tela.projeto)) == 4


def test_esta_bom_nas_marcadas_dentro_da_janela_e_ela_mostra_o_que_sobrou(tela, janela_dos_avisos):
    _lista(tela)
    pediu = []
    tela.processar.connect(lambda: pediu.append(1))

    def aceitar_as_faixas(janela):
        janela.combo_motivo.setCurrentIndex(janela.combo_motivo.findData(analise.FAIXA_NA_BEIRADA))
        janela.botao_todas.click()
        janela.botao_aceitar.click()

    def conferir_o_resto_e_fechar(janela):
        assert janela.linhas() == ["Página 2  -  Desenho apagado"]
        janela.reject()

    janela_dos_avisos["roteiro"] = [aceitar_as_faixas, conferir_o_resto_e_fechar]
    tela._pedir_processamento()
    assert pediu == [] and len(janela_dos_avisos["abertas"]) == 2
    assert "1 página" in tela.botao_alertas.text()
    tela.desfazer()
    assert "3 páginas" in tela.botao_alertas.text()


def test_sem_aviso_nenhum_processa_direto(tela, janela_dos_avisos):
    pediu = []
    tela.processar.connect(lambda: pediu.append(1))
    tela._pedir_processamento()                      # roteiro vazio: a janela nao pode abrir
    assert pediu == [1] and janela_dos_avisos["abertas"] == []


def test_ver_a_lista_pelo_painel(tela, janela_dos_avisos):
    _lista(tela)

    def ver_a_segunda(janela):
        assert not janela.antes_de_processar
        janela.lista.setCurrentRow(1)
        janela.botao_ver.click()

    janela_dos_avisos["roteiro"] = [ver_a_segunda]
    _botao_do_painel(tela, "ver a lista").click()
    assert tela.indice_pagina == 1


# --- a medida por tras, na resolucao do PDF ----------------------------------------

def test_a_tela_pede_a_medida_da_pagina_da_vez_na_resolucao_do_pdf(tela):
    """A regra so vale na resolucao do PDF (a 110 DPI, a previa, 13 das 89
    paginas do estudo decidem diferente): a previa nao mede, e a tela pede por
    tras a medida da pagina que esta na frente - so dela, e so uma vez por
    estado da pagina. Desde 13/10/2026 so DEPOIS de a previa dela aparecer: e
    a previa que guarda a marcacao provisoria, que o desenho de tras troca
    pela do tamanho do PDF (tests/test_marcacao_por_tras.py)."""
    import time

    from PySide6.QtCore import QCoreApplication

    from ui.tarefas import MARCA_DA_MEDIDA

    def esperar(condicao, segundos=30.0):
        fim = time.monotonic() + segundos
        while time.monotonic() < fim and not condicao():
            QCoreApplication.processEvents()
            time.sleep(0.01)
        return condicao()

    previas = tela.previas
    chave = previas.chave_da_medida(0)
    assert chave.startswith(f"0{MARCA_DA_MEDIDA}") and f":{tela.projeto.qualidade_dpi}:" in chave
    # ao abrir, so a previa e pedida; a medida espera a previa aparecer
    assert chave not in previas._pedidas and chave not in previas._cache
    assert esperar(lambda: chave in previas._pedidas or chave in previas._cache), \
        "a prévia chegou e a tela não pediu a medida"
    # pedir de novo nao repete
    assert previas.pedir_medida(0) is False
    # as vizinhas nao sao medidas sozinhas (so quando a pessoa chega nelas)
    chave_3 = previas.chave_da_medida(3)
    assert chave_3 not in previas._pedidas and chave_3 not in previas._cache
    tela.ir_para_pagina(3)
    assert esperar(lambda: chave_3 in previas._pedidas or chave_3 in previas._cache)
    # pagina fora do "So as letras" (aqui: "Guardar tudo") nao tem o que medir
    tela.projeto.paginas[2].misto_fora_do_texto = misto.FORA_TUDO
    assert previas.pedir_medida(2) is False
    assert previas.pedir_medida(99) is False
    # mudou a forca do preto: e outro estado, mede de novo
    antes = previas.chave_da_medida(1)
    tela.projeto.paginas[1].forca_preto = 70
    assert previas.chave_da_medida(1) != antes
    assert previas.pedir_medida(1) is True and previas.pedir_medida(1) is False


# --- o botao de ligar e desligar a forca sozinha (regra 8 do plano) ----------------

def test_o_automatico_liga_e_desliga_a_forca_sozinha(app):  # noqa: F811
    """D-186/D-277: a caixinha "força sozinha" saiu da tela "O que fazer" e mora no
    Automático, etapa "Limpar a folha" (etapa 3 da obra, 26/10/2026); rodar grava."""
    from core import automatico as A
    from core.filtros import PRETO_E_BRANCO
    from ui.automatico import EstadoDoAutomatico, JanelaDoAutomatico

    projeto = _projeto_com_cor()
    projeto.misto_so_as_letras = True
    projeto.filtro_padrao = PRETO_E_BRANCO
    estado = EstadoDoAutomatico()
    estado.do_projeto(projeto)
    janela = JanelaDoAutomatico(estado)
    caixa = janela.cx_forca_sozinha
    assert caixa.isChecked() and projeto.reforcar_texto_falhado is True
    assert "força do preto" in caixa.text()
    caixa.setChecked(False)
    assert estado.opcoes["reforcar_texto_falhado"] is False
    A.aplicar(projeto, A.Pedido(etapas=[A.LIMPAR], opcoes=estado.opcoes))
    assert projeto.reforcar_texto_falhado is False
    # projeto que veio desligado (o salvo antes de 12/10) abre desmarcado
    antigo = _projeto_com_cor()
    antigo.reforcar_texto_falhado = False
    estado.do_projeto(antigo)
    assert not janela.cx_forca_sozinha.isChecked() and antigo.reforcar_texto_falhado is False
    janela.done(0)
