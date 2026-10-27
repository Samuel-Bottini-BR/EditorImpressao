"""Os painéis da direita e a coluna de ícones que os abre (layout, etapa 3).

Decisões do Samuel conferidas aqui (página "Layout do Editor de Impressão"):
  - rodada 7, 203 D: ícones na borda, tudo fechado, com a seta que esconde e
    mostra os ícones;
  - rodada 9, 401 A: o painel aberto fica ao lado da página (um por vez);
  - rodada 9, 402 C: o Propriedades muda conforme a ferramenta;
  - rodada 9, 405 C: o Histórico tem os botões de desfazer e refazer e a lista;
  - rodadas 10 (504 A) e 11 (602 A): "Para revisar" com as abas "Por página |
    Por motivo", abrindo sempre em "Por página".

E o que já se cobrava dos painéis antes: que nada tenha se perdido no caminho,
que "Para revisar" saiba juntar **por tipo** de alerta, e que o Histórico use
o arquivo de desfazer que já existe - e não um segundo mecanismo ao lado.

Testes de máquina (as peças sozinhas, sem janela).
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QEvent, Qt  # noqa: E402
from PySide6.QtGui import QMouseEvent  # noqa: E402
from PySide6.QtWidgets import QApplication, QLabel, QPushButton  # noqa: E402

from core import analise  # noqa: E402
from core.selecao import GRAVURA, LETRA, PAPEL  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402
from ui.widgets.paineis import (  # noqa: E402
    ABA_POR_MOTIVO,
    ABA_POR_PAGINA,
    LARGURA,
    LARGURA_DA_SETA,
    LARGURA_DOS_ICONES,
    ORDEM_DOS_PAINEIS,
    ColunaDeIcones,
    ColunaDePaineis,
    PainelAutomatico,
    PainelFiltroDaPagina,
    PainelHistorico,
    PainelMarcarComo,
    PainelParaRevisar,
    PainelPropriedades,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _projeto(paginas: int = 10) -> Projeto:
    p = Projeto(caminho_entrada="x.pdf", nome="x")
    p.folhas = [ConfigFolha(indice=i) for i in range(paginas)]
    p.paginas = [ConfigPagina(indice=i, folha=i) for i in range(paginas)]
    return p


def _textos(botoes) -> list[str]:
    return [b.text() for b in botoes]


def _clicar_no_icone(icones: ColunaDeIcones, item: str) -> None:
    """Aperta e solta o botão do mouse em cima de um ícone (ou da seta)."""
    centro = icones.retangulos()[item].center()
    for tipo in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
        icones.event(QMouseEvent(tipo, centro, icones.mapToGlobal(centro), Qt.LeftButton,
                                 Qt.LeftButton, Qt.NoModifier))


# --- a coluna de ícones e o painel que abre ----------------------------------


def test_os_cinco_paineis_na_ordem_do_desenho(app):
    coluna = ColunaDePaineis()
    assert list(coluna.paineis) == ["revisar", "automatico", "props", "filtro", "historico"]
    assert tuple(coluna.paineis) == ORDEM_DOS_PAINEIS
    assert LARGURA == 300 and LARGURA_DOS_ICONES == 44
    assert all(p.width() == LARGURA for p in coluna.paineis.values())


def test_de_fabrica_os_icones_a_vista_e_nenhum_painel_aberto(app):
    """Rodada 7, 203 D: "Ícones na borda, tudo fechado"."""
    coluna = ColunaDePaineis()
    assert coluna.aberto is None
    assert coluna.icones_a_vista
    assert not coluna.area.isVisibleTo(coluna)
    assert coluna.icones.isVisibleTo(coluna)
    assert coluna.largura_ocupada() == LARGURA_DOS_ICONES
    assert set(coluna.icones.retangulos()) == {"seta", *ORDEM_DOS_PAINEIS}


def test_clicar_no_icone_abre_e_clicar_de_novo_fecha(app):
    coluna = ColunaDePaineis()
    avisos = []
    coluna.abriu.connect(avisos.append)
    _clicar_no_icone(coluna.icones, "historico")
    assert coluna.aberto == "historico"
    assert coluna.area.isVisibleTo(coluna)
    assert coluna.area.currentWidget() is coluna.historico
    assert coluna.icones.aberto == "historico"
    assert coluna.largura_ocupada() == LARGURA + LARGURA_DOS_ICONES
    _clicar_no_icone(coluna.icones, "historico")
    assert coluna.aberto is None
    assert not coluna.area.isVisibleTo(coluna)
    assert avisos == ["historico", ""]


def test_um_painel_por_vez(app):
    """Rodada 9, 401 A (a opção de dois painéis juntos não foi a escolhida)."""
    coluna = ColunaDePaineis()
    _clicar_no_icone(coluna.icones, "revisar")
    _clicar_no_icone(coluna.icones, "automatico")
    assert coluna.aberto == "automatico"
    assert coluna.area.currentWidget() is coluna.automatico
    assert coluna.largura_ocupada() == LARGURA + LARGURA_DOS_ICONES


def test_o_x_do_painel_fecha(app):
    coluna = ColunaDePaineis()
    coluna.abrir("props")
    coluna.propriedades.cabecalho.botao_fechar.click()
    assert coluna.aberto is None
    assert not coluna.area.isVisibleTo(coluna)


def test_a_seta_esconde_e_mostra_os_icones(app):
    """O comentário do Samuel na 203: "uma seta de dropdown que eu abro ou
    fecho". Escondidos, sobra a faixa fina com a seta; o painel que estava
    aberto some junto e volta com os ícones."""
    coluna = ColunaDePaineis()
    coluna.abrir("filtro")
    _clicar_no_icone(coluna.icones, "seta")
    assert not coluna.icones_a_vista
    assert coluna.icones.recolhida and coluna.icones.width() == LARGURA_DA_SETA
    assert not coluna.area.isVisibleTo(coluna)
    assert coluna.largura_ocupada() == LARGURA_DA_SETA
    assert set(coluna.icones.retangulos()) == {"seta"}, "só a seta fica de clicar"
    _clicar_no_icone(coluna.icones, "seta")
    assert coluna.icones_a_vista and coluna.icones.width() == LARGURA_DOS_ICONES
    assert coluna.aberto == "filtro" and coluna.area.isVisibleTo(coluna)


def test_cada_icone_tem_o_nome_no_balao(app):
    icones = ColunaDeIcones()
    assert icones.texto_da_dica("revisar") == "Para revisar"
    assert icones.texto_da_dica("automatico") == "Automático"
    assert icones.texto_da_dica("props") == "Propriedades"
    assert icones.texto_da_dica("filtro") == "Filtro da página"
    assert icones.texto_da_dica("historico") == "Histórico"
    assert "esconder" in icones.texto_da_dica("seta")
    icones.definir_contagem(3)
    assert "3 páginas com dúvida" in icones.texto_da_dica("revisar")
    icones.definir_recolhida(True)
    assert "mostrar" in icones.texto_da_dica("seta")


def test_a_coluna_de_icones_se_pinta_nos_tres_estados(app):
    """Nenhum estado do desenho à mão levanta exceção (fechada, com um painel
    aberto e a contagem, e com os ícones escondidos)."""
    icones = ColunaDeIcones()
    icones.resize(icones.width(), 500)
    assert not icones.grab().isNull()
    icones.definir_aberto("revisar")
    icones.definir_contagem(128)
    assert not icones.grab().isNull()
    icones.definir_recolhida(True)
    assert not icones.grab().isNull()


def test_o_nome_antigo_do_menu_ver_ainda_abre_e_fecha(app):
    coluna = ColunaDePaineis()
    coluna.mostrar_painel("historico", True)
    assert coluna.aberto == "historico"
    coluna.mostrar_painel("historico", False)
    assert coluna.aberto is None
    coluna.mostrar_painel("marcar", True)          # o "Marcar como" mora no Propriedades
    assert coluna.aberto == "props"


# --- Para revisar: por página e por motivo -----------------------------------


def test_para_revisar_abre_sempre_em_por_pagina(app):
    """Rodada 11, 602 A: "Sempre 'Por página'" (não lembra a última)."""
    coluna = ColunaDePaineis()
    painel = coluna.para_revisar
    assert painel.aba == ABA_POR_PAGINA
    coluna.abrir("revisar")
    painel.botoes_de_aba[ABA_POR_MOTIVO].click()
    assert painel.aba == ABA_POR_MOTIVO
    assert painel.botoes_de_aba[ABA_POR_MOTIVO].isChecked()
    assert not painel.botoes_de_aba[ABA_POR_PAGINA].isChecked()
    coluna.fechar()
    coluna.abrir("revisar")
    assert painel.aba == ABA_POR_PAGINA, "abriu na aba que tinha ficado"
    assert _textos(painel.botoes_de_aba.values()) == ["Por página", "Por motivo"]


def test_por_pagina_uma_linha_por_pagina_na_ordem_do_livro(app):
    projeto = _projeto(20)
    projeto.paginas[11].alertas = [analise.COR]
    for indice in (7, 2):
        projeto.paginas[indice].alertas = [analise.ANGULO_SUSPEITO_]

    painel = PainelParaRevisar()
    painel.atualizar(projeto)

    linhas = [painel.lista.item(i) for i in range(painel.lista.count())]
    assert [item.text() for item in linhas] == ["Página 3", "Página 8", "Página 12"]
    assert [item.data(Qt.UserRole) for item in linhas] == [2, 7, 11]
    # cada linha leva o nome e a frase do aviso (de core/analise.descrever)
    cor = analise.descrever(analise.COR)
    assert cor.titulo in linhas[2].toolTip() and cor.mensagem in linhas[2].toolTip()
    assert painel.cabecalho.contagem.text() == "3"
    assert "3 páginas" in painel.frase.text()


def test_clicar_numa_linha_leva_a_pagina(app):
    projeto = _projeto(20)
    for indice in (6, 13):
        projeto.paginas[indice].alertas = [analise.COR]
    painel = PainelParaRevisar()
    painel.atualizar(projeto)
    destinos = []
    painel.ir_para.connect(destinos.append)
    painel.lista.itemClicked.emit(painel.lista.item(1))
    assert destinos == [13]


def test_a_pagina_da_vez_fica_destacada_sem_ir_a_lugar_nenhum(app):
    projeto = _projeto(20)
    for indice in (6, 13):
        projeto.paginas[indice].alertas = [analise.COR]
    painel = PainelParaRevisar()
    painel.atualizar(projeto)
    destinos = []
    painel.ir_para.connect(destinos.append)
    painel.definir_pagina_atual(13)
    assert painel.lista.currentRow() == 1
    painel.definir_pagina_atual(4)                 # página sem dúvida: nenhuma destacada
    assert painel.lista.currentRow() == -1
    assert destinos == [], "só mostrar não é ir"


def test_a_lista_por_pagina_se_desenha(app):
    projeto = _projeto(6)
    projeto.paginas[1].alertas = [analise.COR, analise.ANGULO_SUSPEITO_]
    painel = PainelParaRevisar()
    painel.resize(LARGURA, 500)
    painel.atualizar(projeto)
    painel.definir_pagina_atual(1)
    assert not painel.grab().isNull()


def test_por_motivo_agrupa_por_tipo_e_nao_lista_paginas(app):
    """Uma lista de "página 3, 17, 40" não diz o que há de errado com elas."""
    projeto = _projeto(20)
    for indice in (2, 7):
        projeto.paginas[indice].alertas = [analise.ANGULO_SUSPEITO_]
    projeto.paginas[11].alertas = [analise.COR]

    painel = PainelParaRevisar()
    painel.atualizar(projeto)

    textos = _textos(painel.itens)
    assert any("(2)" in t for t in textos), "não agrupou os dois de ângulo"
    assert any("(1)" in t for t in textos)
    assert painel.cabecalho.text().startswith("Para revisar")
    assert painel.cabecalho.text() != "Para revisar", "o cabeçalho leva o número"


def test_para_revisar_mostra_o_titulo_do_alerta_e_nao_o_objeto(app):
    """descrever() devolve um Alerta; sem o .titulo saía "Alerta(codigo=..."."""
    projeto = _projeto(3)
    projeto.paginas[0].alertas = [analise.COR]

    painel = PainelParaRevisar()
    painel.atualizar(projeto)

    textos = " ".join(_textos(painel.itens))
    assert "Alerta(" not in textos, "o painel mostrou a repr do objeto"
    assert analise.descrever(analise.COR).titulo in textos


def test_para_revisar_ignora_o_que_ja_foi_conferido(app):
    projeto = _projeto(5)
    projeto.paginas[0].alertas = [analise.COR]
    projeto.paginas[0].revisada = True
    projeto.paginas[1].alertas = [analise.COR]
    projeto.paginas[1].apagada = True

    painel = PainelParaRevisar()
    painel.atualizar(projeto)
    assert not painel.itens, "contou página já conferida ou apagada"
    assert painel.lista.count() == 0
    assert painel.cabecalho.text() == "Para revisar"
    assert painel.frase.text() == "nada pendente"


def test_clicar_no_motivo_leva_a_primeira_do_tipo(app):
    projeto = _projeto(20)
    for indice in (6, 13):
        projeto.paginas[indice].alertas = [analise.COR]

    painel = PainelParaRevisar()
    painel.atualizar(projeto)

    destinos = []
    painel.ir_para.connect(destinos.append)
    painel.itens[0].click()
    assert destinos == [6]


def test_a_contagem_avisa_a_coluna_de_icones(app):
    coluna = ColunaDePaineis()
    projeto = _projeto(8)
    for indice in (1, 3, 5):
        projeto.paginas[indice].alertas = [analise.COR]
    coluna.para_revisar.atualizar(projeto)
    assert coluna.icones.contagem == 3
    projeto.paginas[1].revisada = True
    coluna.para_revisar.atualizar(projeto)
    assert coluna.icones.contagem == 2


# --- Automático (etapa 3 da obra, 26/10/2026: o painel de verdade) ----------


def test_o_automatico_mostra_as_etapas_do_livro(app):
    """O painel mostra as etapas do livro, na ordem, e onde cada uma está
    ligada (antes: a lista só de leitura da tela "O que fazer")."""
    from core import automatico as A

    projeto = _projeto(3)
    projeto.dividir_folhas = True
    projeto.endireitar = False
    painel = PainelAutomatico()
    painel.atualizar(projeto)
    lista = painel.lista
    etapas = [lista.item(i).data(Qt.UserRole) for i in range(lista.count())]
    assert etapas == A.ordem(projeto)
    assert [A.NOMES[e] for e in etapas][:4] == ["Dividir folhas ao meio", "Endireitar folhas tortas",
                                                "Cortar as bordas", "Limpar a folha"]
    textos = {e: lista.item_da_etapa(e).text() for e in etapas}
    assert "Dividir folhas ao meio" in textos[A.DIVIDIR] and "ligada no livro todo" in textos[A.DIVIDIR]
    assert "desligada" in textos[A.ENDIREITAR]


def test_o_automatico_leva_as_opcoes_do_livro(app):
    """Mudar uma etapa é no Automático: "abrir em janela grande" e "ajustar a
    etapa escolhida ›" pedem a janela grande (antes: "Voltar para as opções")."""
    from core import automatico as A

    painel = PainelAutomatico()
    painel.atualizar(_projeto(2))
    pedidos = []
    painel.janela_pedida.connect(pedidos.append)
    painel.botao_janela.click()
    painel.lista.escolher(A.LIMPAR)
    painel.botao_ajustar.click()
    assert pedidos == ["", A.LIMPAR]


# --- Propriedades: muda conforme a ferramenta --------------------------------


def test_marcar_como_tem_os_tres_um_embaixo_do_outro(app):
    """Desde o item 2.18 (P11 (a) e TINTA3 do Samuel, 05/10/2026) são seis
    tipos - os três de sempre e os três "por cima" - e o botão da cor de
    pintar, um embaixo do outro."""
    from core.selecao import PINTAR, TINTA_COR, TINTA_PRETA

    painel = PainelMarcarComo()
    assert set(painel.botoes) == {GRAVURA, LETRA, PAPEL, PINTAR, TINTA_COR, TINTA_PRETA}
    assert painel.dentro.count() == 7
    assert all(not b.icon().isNull() for b in painel.botoes.values()), "a cor de cada um"


def test_marcar_como_avisa_quem_escolheu(app):
    painel = PainelMarcarComo()
    escolhas = []
    painel.escolheu.connect(escolhas.append)
    painel.definir_tipo(LETRA)
    assert escolhas == [LETRA]
    assert painel.tipo == LETRA


def test_o_propriedades_mostra_so_o_da_ferramenta_da_vez(app):
    """Rodada 9, 402 C: "Muda conforme a ferramenta (como no Photoshop)"."""
    painel = PainelPropriedades()
    do_cortar, do_endireitar = QLabel("botões do cortar"), QLabel("botões do endireitar")
    painel.definir_conteudo("bordas", do_cortar)
    painel.definir_conteudo("angulo", do_endireitar)

    painel.mostrar("bordas", "Cortar as bordas")
    assert do_cortar.isVisibleTo(painel) and not do_endireitar.isVisibleTo(painel)
    assert not painel.marcar_como.isVisibleTo(painel)
    assert painel.cabecalho.subtitulo.text() == "Cortar as bordas"

    painel.mostrar(painel.CONTEUDO_DE_MARCAR, "Laço")
    assert painel.marcar_como.isVisibleTo(painel)
    assert not do_cortar.isVisibleTo(painel)

    painel.mostrar("ferramenta que nao existe", "Zoom", "Zoom não tem propriedades.")
    assert painel.sem_propriedades.isVisibleTo(painel)
    assert painel.sem_propriedades.text() == "Zoom não tem propriedades."
    assert not painel.marcar_como.isVisibleTo(painel)

    painel.tirar_conteudos()
    assert not painel.tem_conteudo("bordas")
    assert painel.tem_conteudo(painel.CONTEUDO_DE_MARCAR), "os fixos ficam"


# --- Filtro da página -------------------------------------------------------


def _clicar(widget) -> None:
    """Aperta e solta o botão esquerdo do mouse no meio do widget."""
    centro = widget.rect().center()
    for tipo in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
        widget.event(QMouseEvent(tipo, centro, widget.mapToGlobal(centro), Qt.LeftButton,
                                 Qt.LeftButton, Qt.NoModifier))


def _painel_de_filtro_montado():
    """O painel Filtro com as peças que a tela entregaria (aqui, de mentira)."""
    from PySide6.QtWidgets import QWidget

    from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO

    painel = PainelFiltroDaPagina()
    pecas = {nome: QWidget() for nome in ("ajuste", "letras", "limpar", "mais", "aplicar")}
    pecas["apagar"] = QPushButton("apagar página")
    painel.montar([(ORIGINAL, "Original", "1"), (PRETO_E_BRANCO, "Preto e branco", "2"),
                   (MELHORAR, "Melhorar", "3"), (MAGICO_PRO, "Mágico pro", "4")], pecas)
    return painel


def test_o_painel_de_filtro_mostra_a_fila_com_as_teclas(app):
    """Etapa 4 do layout (rodada 9, 403 B): a fila dos filtros, cada um com a
    tecla, e o da página aceso."""
    from core.filtros import MAGICO_PRO

    painel = _painel_de_filtro_montado()
    painel.atualizar(ConfigPagina(indice=0, folha=0, filtro=MAGICO_PRO))
    textos = " ".join(r.text() for r in painel.findChildren(QLabel))
    for esperado in ("Original", "Preto e branco", "Melhorar", "Mágico pro",
                     "tecla 1", "tecla 4"):
        assert esperado in textos
    assert painel.cartoes[MAGICO_PRO].selecionado
    assert sum(c.selecionado for c in painel.cartoes.values()) == 1
    assert painel.cabecalho.subtitulo.text() == "página 1"


def test_clicar_na_fila_escolhe_o_filtro(app):
    from core.filtros import MELHORAR

    painel = _painel_de_filtro_montado()
    escolhidos = []
    painel.filtro_escolhido.connect(escolhidos.append)
    _clicar(painel.cartoes[MELHORAR])
    assert escolhidos == [MELHORAR]


def test_o_so_neste_pedaco_sem_o_botao_de_cima(app):
    """Rodada 14b do layout, 909 (Samuel, 20/10/2026: "B — Sem o botão de
    cima, nenhum aceso"): os quatro filtros, nenhum aceso de começo; clicar
    num acende, clicar de novo no aceso volta a nenhum."""
    from core.filtros import PRETO_E_BRANCO

    painel = _painel_de_filtro_montado()
    painel.atualizar(ConfigPagina(indice=0, folha=0, filtro=PRETO_E_BRANCO))
    textos = _textos(painel.botoes_do_pedaco.values())
    assert textos == ["Original", "Preto e branco", "Melhorar", "Mágico pro"]
    assert "o mesmo da página" not in _textos(painel.corpo.findChildren(QPushButton))
    assert painel.filtro_pedaco == ""
    assert painel.partes["pedaco"].cabeca.resumo.text() == "nenhum"
    escolhidos = []
    painel.filtro_do_pedaco.connect(escolhidos.append)
    painel.botoes_do_pedaco[PRETO_E_BRANCO].click()
    assert painel.partes["pedaco"].cabeca.resumo.text() == "Preto e branco"
    painel.botoes_do_pedaco[PRETO_E_BRANCO].click()
    assert escolhidos == [PRETO_E_BRANCO, ""]
    assert painel.partes["pedaco"].cabeca.resumo.text() == "nenhum"


def test_as_partes_abrem_fecham_e_lembram(app):
    """Rodada 9, 403 B: partes que abrem e fecham; a escolha vale para a
    próxima página (e para o próximo painel montado, no mesmo programa)."""
    from ui.widgets.paineis import ParteQueAbre

    ParteQueAbre.ABERTAS.clear()
    painel = _painel_de_filtro_montado()
    parte = painel.partes["limpar"]
    assert not parte.aberta and parte.caixa_do_corpo.isHidden()
    _clicar(parte.cabeca)
    assert parte.aberta and not parte.caixa_do_corpo.isHidden()
    outro = _painel_de_filtro_montado()
    assert outro.partes["limpar"].aberta, "não lembrou que estava aberta"
    painel.definir_parte("limpar", False, "Sem limpeza")
    assert parte.isHidden() and parte.cabeca.resumo.text() == "Sem limpeza"
    ParteQueAbre.ABERTAS.clear()


def test_sem_os_filtros_o_painel_diz_por_que(app):
    painel = PainelFiltroDaPagina()
    assert not painel.sem_filtro.isHidden()
    assert "Limpar a folha" in painel.sem_filtro.text()
    montado = _painel_de_filtro_montado()
    assert montado.sem_filtro.isHidden() and not montado.pe.isHidden()
    montado.desmontar()
    assert not montado.sem_filtro.isHidden() and not montado.cartoes


# --- Histórico --------------------------------------------------------------


def _acoes(tmp_path, quantas: int = 3):
    from historico_acoes import HistoricoAcoes
    from modelos import Acao

    acoes = HistoricoAcoes(tmp_path)
    for numero in range(quantas):
        acoes.registrar(Acao.nova("filtro", "pagina", [numero],
                                  {"filtro": "a"}, {"filtro": "b"},
                                  f"trocou o filtro da página {numero + 1}"))
    return acoes


def test_o_historico_usa_o_arquivo_de_desfazer_que_ja_existe(app, tmp_path):
    """Um segundo mecanismo seria duas verdades sobre o mesmo trabalho."""
    painel = PainelHistorico()
    painel.atualizar(_acoes(tmp_path))

    textos = _textos(painel.itens)
    assert len(textos) == 3
    assert "página 1" in textos[0]
    assert "página 3" in textos[-1], "a mais recente não ficou embaixo"


def test_clicar_no_historico_pede_para_voltar_ate_ali(app, tmp_path):
    painel = PainelHistorico()
    painel.atualizar(_acoes(tmp_path))

    posicoes = []
    painel.voltar_para.connect(posicoes.append)
    painel.itens[0].click()
    assert posicoes == [1], "clicar na primeira ação não voltou até ela"


def test_historico_vazio_diz_que_esta_vazio(app, tmp_path):
    from historico_acoes import HistoricoAcoes

    painel = PainelHistorico()
    painel.atualizar(HistoricoAcoes(tmp_path))
    textos = " ".join(r.text() for r in painel.findChildren(QLabel))
    assert "nada ainda" in textos
    assert not painel.botao_desfazer.isEnabled() and not painel.botao_refazer.isEnabled()


def test_o_historico_tem_desfazer_e_refazer_a_mao(app, tmp_path):
    """Rodada 9, 405 C ("Os dois"): os botões e a lista."""
    acoes = _acoes(tmp_path)
    painel = PainelHistorico()
    painel.atualizar(acoes)
    pedidos = []
    painel.desfazer_pedido.connect(lambda: pedidos.append("desfazer"))
    painel.refazer_pedido.connect(lambda: pedidos.append("refazer"))
    assert painel.botao_desfazer.isEnabled() and not painel.botao_refazer.isEnabled()
    assert "página 3" in painel.botao_desfazer.toolTip()
    painel.botao_desfazer.click()
    assert pedidos == ["desfazer"]

    acoes.desfazer(_projeto(4))
    painel.atualizar(acoes)
    assert painel.botao_refazer.isEnabled()
    painel.botao_refazer.click()
    assert pedidos == ["desfazer", "refazer"]


def test_a_acao_desfeita_fica_na_lista_e_clicar_refaz_ate_ela(app, tmp_path):
    acoes = _acoes(tmp_path)
    projeto = _projeto(4)
    acoes.desfazer(projeto)
    acoes.desfazer(projeto)
    painel = PainelHistorico()
    painel.atualizar(acoes)

    assert len(painel.itens) == 1 and len(painel.itens_desfeitos) == 2
    assert "página 2" in painel.itens_desfeitos[0].text()
    assert "(desfeita)" in painel.itens_desfeitos[0].text()
    posicoes = []
    painel.voltar_para.connect(posicoes.append)
    painel.itens_desfeitos[1].click()
    assert posicoes == [3], "clicar na última desfeita refaz as três"
