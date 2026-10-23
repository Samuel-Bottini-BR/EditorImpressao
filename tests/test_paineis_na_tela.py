"""A coluna de ícones, os painéis e o Propriedades na janela (layout, etapa 3).

Decisões do Samuel conferidas aqui (página "Layout do Editor de Impressão";
as palavras dele estão no "Plano de layout (rascunho).md"):
  - rodada 7, 203 D: ícones na borda, tudo fechado de fábrica;
  - rodada 9, 401 A: "Empurra a página" (o painel aberto fica ao lado dela);
  - rodada 9, 402 C: Propriedades "Muda conforme a ferramenta";
  - rodada 12, 701 A: "Fazer logo o painel Propriedades do Cortar" (a fila de
    botões embaixo da página não cabia em 1280 x 657);
  - rodada 12, 702 C: a linha dos menus mostra só o nome da ferramenta;
  - rodada 12, 706 B: o Propriedades tem duas partes, "Só nesta página" e
    "Para o livro todo";
  - rodada 12, 709 B: as listas "aplicar em" dizem folha (girar) ou página
    (endireitar);
  - rodada 12, 710 B: "deixar como veio", "usar o ângulo do programa" e "usar
    o corte do programa".

Testes de máquina (sem janela na tela, tests/conftest.py). Não provam que o
texto cabe com as letras de verdade nem o arrasto: isso é dos prints da
janela real (relatorios/layout-impl/etapa3).
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from PySide6.QtCore import QEvent, Qt  # noqa: E402
from PySide6.QtGui import QKeyEvent  # noqa: E402
from PySide6.QtWidgets import QApplication, QCheckBox, QLabel, QPushButton  # noqa: E402

from core import girar  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _pdf,
    app,
    janela,
    pasta,
)
from ui.widgets.paineis import LARGURA, LARGURA_DA_SETA, LARGURA_DOS_ICONES  # noqa: E402
from ui.widgets.trilha_agrupada import (  # noqa: E402
    FERRAMENTA_CORTAR,
    FERRAMENTA_DIVIDIR,
    FERRAMENTA_ENDIREITAR,
    USOS,
)


def _aberta(janela, pasta, tamanho=(1280, 657)):
    """Um livro de 5 folhas com Dividir, Cortar e Endireitar ligados."""
    janela.abrir_livro(str(_pdf(pasta, folhas=5)))
    opcoes = janela.tela_opcoes
    opcoes.cx_dividir.setChecked(True)
    opcoes.cx_cortar.setChecked(True)
    opcoes.cx_endireitar.setChecked(True)
    _analisar(janela)
    janela.resize(*tamanho)
    janela.show()
    _assentar()
    return janela.tela_conferir


def _assentar() -> None:
    for _ in range(5):
        QApplication.processEvents()


def _botoes(widget) -> dict[str, QPushButton]:
    return {b.text(): b for b in widget.findChildren(QPushButton)}


def _direita_na_tela(tela, widget) -> int:
    return widget.mapTo(tela, widget.rect().topRight()).x()


# --- a coluna de ícones e o painel que empurra a página -----------------------


def test_de_fabrica_tudo_fechado_e_os_icones_na_borda(janela, pasta):
    tela = _aberta(janela, pasta)
    assert tela.paineis.aberto is None
    assert not tela.paineis.area.isVisible()
    assert tela.paineis.icones.isVisible()
    assert tela.paineis.width() == LARGURA_DOS_ICONES
    # a coluna de ícones encosta na borda direita da tela de trabalho
    assert _direita_na_tela(tela, tela.paineis.icones) == tela.width() - 1


def test_o_painel_aberto_empurra_a_pagina(janela, pasta):
    """Rodada 9, 401 A: o painel nunca fica por cima da página."""
    tela = _aberta(janela, pasta)
    fechado = tela.area_imagem.width()
    tela.paineis.abrir("revisar")
    _assentar()
    assert tela.paineis.area.isVisible()
    assert tela.area_imagem.width() == fechado - LARGURA
    painel = tela.paineis.para_revisar
    esquerda_do_painel = painel.mapTo(tela, painel.rect().topLeft()).x()
    assert _direita_na_tela(tela, tela.area_imagem) < esquerda_do_painel
    assert _direita_na_tela(tela, tela.faixa) < esquerda_do_painel, "nem por cima da faixa"
    assert _direita_na_tela(tela, tela.paineis.icones) == tela.width() - 1
    tela.paineis.fechar()
    _assentar()
    assert tela.area_imagem.width() == fechado


def test_a_seta_esconde_os_icones_e_a_pagina_ganha_o_lugar(janela, pasta):
    tela = _aberta(janela, pasta)
    com_icones = tela.area_imagem.width()
    tela.paineis.alternar_os_icones()
    _assentar()
    assert tela.paineis.width() == LARGURA_DA_SETA
    assert tela.area_imagem.width() == com_icones + LARGURA_DOS_ICONES - LARGURA_DA_SETA
    tela.paineis.alternar_os_icones()
    _assentar()
    assert tela.area_imagem.width() == com_icones


@pytest.mark.parametrize("tamanho", [(1280, 657), (1000, 600)])
def test_com_o_painel_aberto_nada_sai_da_janela(janela, pasta, tamanho):
    """Na janela do notebook do Kaique e na mínima, com um painel aberto, a
    coluna de ícones continua inteira dentro da janela, em todas as ferramentas."""
    tela = _aberta(janela, pasta, tamanho)
    for painel in ("revisar", "automatico", "props", "filtro", "historico"):
        tela.paineis.abrir(painel)
        for indice in range(len(tela._abas_ativas)):
            tela.barra_abas.setCurrentIndex(indice)
            _assentar()
            assert _direita_na_tela(tela, tela.paineis.icones) <= tela.width() - 1, (
                painel, tela.aba_atual)
            assert tela.area_imagem.width() > 200, (painel, tela.aba_atual)


def test_para_revisar_leva_a_pagina_clicada(janela, pasta):
    from core import analise

    tela = _aberta(janela, pasta)
    for indice in (1, 3):
        janela.projeto.paginas[indice].alertas = [analise.COR]
        janela.projeto.paginas[indice].revisada = False
    tela.atualizar()
    painel = tela.paineis.para_revisar
    assert tela.paineis.icones.contagem == painel.lista.count() >= 2
    tela.paineis.abrir("revisar")
    indices = [painel.lista.item(i).data(Qt.UserRole) for i in range(painel.lista.count())]
    assert 3 in indices
    painel.lista.itemClicked.emit(painel.lista.item(indices.index(3)))
    assert tela.indice_pagina == 3
    assert painel.lista.currentRow() == indices.index(3), "a página da vez fica destacada"


def test_o_automatico_volta_para_o_que_fazer(janela, pasta):
    from ui.janela_principal import OPCOES

    tela = _aberta(janela, pasta)
    tela.paineis.abrir("automatico")
    painel = tela.paineis.automatico
    ligadas = {nome: ligada for ligada, nome, _f, _e in painel.linhas}
    assert ligadas["Dividir folhas ao meio"] and ligadas["Cortar as bordas"]
    painel.botao_mudar.click()
    assert janela.telas.currentIndex() == OPCOES


def test_o_historico_do_painel_desfaz_e_refaz(janela, pasta):
    tela = _aberta(janela, pasta)
    tela.trilha.escolher(FERRAMENTA_CORTAR)
    tela._sem_recorte()
    painel = tela.paineis.historico
    feitas = len(janela.acoes.feitas)
    assert feitas >= 1 and len(painel.itens) == min(feitas, 40)
    assert painel.botao_desfazer.isEnabled()
    painel.botao_desfazer.click()
    assert len(janela.acoes.feitas) == feitas - 1
    assert painel.itens_desfeitos, "a desfeita continua na lista, apagada"
    painel.botao_refazer.click()
    assert len(janela.acoes.feitas) == feitas
    # clicar na ação desfeita refaz até ela
    tela.desfazer()
    tela.paineis.historico.itens_desfeitos[-1].click()
    assert len(janela.acoes.feitas) == feitas


# --- a faixa do conferir com os três botões ------------------------------------


def test_a_faixa_tem_esta_certo_e_proxima_duvida(janela, pasta):
    from core import analise

    tela = _aberta(janela, pasta)
    tela.trilha.escolher(FERRAMENTA_CORTAR)
    for botao in (tela.botao_esta_certo, tela.botao_proxima_duvida):
        assert botao.parentWidget() is tela.faixa
        assert botao.isVisible()
    for pagina in janela.projeto.paginas:
        pagina.alertas, pagina.revisada = [], False
    janela.projeto.paginas[3].alertas = [analise.COR]
    tela.ir_para_pagina(0)
    assert tela.botao_proxima_duvida.isEnabled()
    assert tela.botao_sugestao.isHidden(), "página sem aviso: sem botão laranja"
    tela.botao_proxima_duvida.click()
    assert tela.indice_pagina == 3
    assert not tela.botao_sugestao.isHidden()
    assert tela.botao_sugestao.text() == analise.descrever(analise.COR).acao
    # as palavras da rodada 12 (710 B) e da 13 (805 C) tambem nos avisos
    assert analise.descrever(analise.ANGULO_SUSPEITO_).acao == "deixar como veio"
    contas = analise.descrever(analise.CONTAS_DO_ENDIREITAR_DISCORDAM).mensagem
    assert "a do Editor" in contas and "ferramenta Endireitar" in contas
    assert "aba " not in contas and "programa" not in contas
    assert tela.botoes_de_sugestao["bordas"] is tela.botao_sugestao
    tela.botao_esta_certo.click()
    assert janela.projeto.paginas[3].revisada


# --- o painel Propriedades do Cortar (701 A) -----------------------------------


def test_os_botoes_do_cortar_sairam_da_fila_e_moram_no_propriedades(janela, pasta):
    tela = _aberta(janela, pasta)
    tela.trilha.escolher(FERRAMENTA_CORTAR)
    _assentar()
    assert tela.barra_botoes.height() == 0, "a fila embaixo da página ficou vazia"
    assert not tela.barra_botoes.currentWidget().findChildren(QPushButton)
    conteudo = tela.propriedades_das_abas["bordas"]
    botoes = _botoes(conteudo)
    for nome in ("não cortar esta", "usar o corte do programa", "usar em todas", "tamanho..."):
        assert nome in botoes, nome
    assert "voltar ao automático" not in botoes, "o nome mudou (rodada 12, 710 B)"
    assert "está certo" not in botoes, "o 'está certo' é o da faixa"

    assert tela.paineis.aberto == "props", "escolher o Cortar abre o Propriedades (802 A)"
    painel = tela.paineis.propriedades
    assert painel.conteudo == "bordas"
    assert painel.cabecalho.subtitulo.text() == "Cortar as bordas"
    for botao in botoes.values():
        assert botao.isVisible(), botao.text()
        assert painel.isAncestorOf(botao)
    # (se cabem nos 300 px com as letras de verdade, quem confere são os prints
    # da janela real: sem janela na tela a letra de mentira é larga demais)
    # as duas partes (rodada 12, 706 B)
    partes = [r.text() for r in conteudo.findChildren(QLabel)]
    assert "SÓ NESTA PÁGINA" in partes and "PARA O LIVRO TODO" in partes
    assert any(t.startswith("Cortar a beirada da folha vizinha:") for t in partes)


def test_os_botoes_do_cortar_fazem_o_mesmo_de_antes(janela, pasta, monkeypatch):
    """Item 2.13 (20/10/2026): o "usar em todas" passou a abrir a janela "Em
    quais páginas?" (as exceções vêm desmarcadas); aqui ela responde com as
    páginas de fábrica, que neste livro são todas (nenhuma tem corte próprio)."""
    from ui import dialogo_escolher_paginas as dep

    tela = _aberta(janela, pasta)
    monkeypatch.setattr(type(tela), "_escolher_paginas_do_corte",
                        lambda self: dep.paginas_de_fabrica(self.projeto, self.indice_pagina))
    tela.trilha.escolher(FERRAMENTA_CORTAR)
    tela.paineis.abrir("props")
    botoes = _botoes(tela.propriedades_das_abas["bordas"])
    pagina = janela.projeto.paginas[tela.indice_pagina]
    botoes["não cortar esta"].click()
    assert list(pagina.recorte) == [0.0, 0.0, 1.0, 1.0]
    botoes["usar o corte do programa"].click()
    assert pagina.recorte is None
    tela._mover_recorte((0.1, 0.1, 0.8, 0.8))
    botoes["usar em todas"].click()
    assert all(list(p.recorte) == [0.1, 0.1, 0.8, 0.8] for p in janela.projeto.paginas)


def test_espelhado_e_proporcao_travada_sao_caixinhas_e_as_teclas_valem(janela, pasta):
    tela = _aberta(janela, pasta)
    tela.trilha.escolher(FERRAMENTA_CORTAR)
    for caixinha in (tela.botao_espelhado, tela.botao_proporcao_travada,
                     tela.botao_mover_conteudo):
        assert isinstance(caixinha, QCheckBox)
        assert tela.paineis.propriedades.isAncestorOf(caixinha)
    assert "tecla M" in tela.botao_espelhado.text()
    assert "tecla T" in tela.botao_proporcao_travada.text()
    assert not tela.botao_mover_conteudo.isEnabled(), "só com um tamanho de folha"
    # as teclas valem também com o painel fechado
    tela.paineis.fechar()
    assert tela.paineis.aberto is None
    assert tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, Qt.Key_M, Qt.NoModifier, "m"))
    assert tela.botao_espelhado.isChecked()
    assert tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, Qt.Key_T, Qt.NoModifier, "t"))
    assert tela.botao_proporcao_travada.isChecked() and not tela.botao_espelhado.isChecked()


def test_escolher_cortar_endireitar_ou_dividir_abre_o_propriedades(janela, pasta):
    """Rodada 13, 802 A ("Abre sozinho"). Só ao ESCOLHER a ferramenta: abrir o
    livro não abre nada, e quem fecha o painel o encontra fechado até
    escolher outra dessas três."""
    tela = _aberta(janela, pasta)
    assert tela.paineis.aberto is None, "abrir o livro não abre painel (203 D)"
    for ferramenta in (FERRAMENTA_CORTAR, FERRAMENTA_ENDIREITAR, FERRAMENTA_DIVIDIR):
        tela.paineis.fechar()
        tela.trilha.escolher(ferramenta)
        assert tela.paineis.aberto == "props", ferramenta
    # fechou: continua fechado ao trocar de página e ao mexer na página
    tela.paineis.fechar()
    tela.ir_para_pagina(2)
    tela._marcar_revisada()
    assert tela.paineis.aberto is None
    # com outro painel aberto, escolher a ferramenta troca pelo Propriedades
    tela.paineis.abrir("revisar")
    tela.trilha.escolher(FERRAMENTA_CORTAR)
    assert tela.paineis.aberto == "props"
    # o ponto único de troca (teclas, menus) vale igual ao clique na trilha
    tela.paineis.fechar()
    tela.escolher_ferramenta(FERRAMENTA_ENDIREITAR)
    assert tela.paineis.aberto == "props"


def test_o_bloco_girar_a_folha_fica_no_alto_do_propriedades(janela, pasta):
    """Rodada 12, 703 B: em todas as ferramentas, acima do que é da ferramenta."""
    tela = _aberta(janela, pasta)
    painel = tela.paineis.propriedades
    assert painel.dentro.itemAt(0).widget() is tela.barra_girar
    for ferramenta in (FERRAMENTA_CORTAR, FERRAMENTA_ENDIREITAR, FERRAMENTA_DIVIDIR):
        tela.trilha.escolher(ferramenta)
        _assentar()
        assert tela.barra_girar.isVisible(), ferramenta
        conteudo = tela.propriedades_das_abas[tela.aba_atual]
        assert tela.barra_girar.geometry().bottom() < conteudo.geometry().top()
        assert all(b.isVisible() for b in tela.barra_girar.botoes_de_giro.values())
        assert tela.barra_girar.combo_alcance.isVisible()


def test_os_textos_da_rodada_13(janela, pasta):
    """805 C: a conta antiga chama-se "Editor" na linha dos ângulos. 806 B:
    "daqui em diante" em todos (o botão do Filtro dizia "só nas próximas")."""
    from ui.tela_conferir import texto_dos_angulos_medidos

    assert texto_dos_angulos_medidos(
        {"programa": -0.2, "scantailor": 0.0, "discordam": False}) ==         "ScanTailor +0,0° · Editor -0,2°"
    tela = _aberta(janela, pasta)
    if "filtro" not in tela._abas_ativas:
        pytest.skip("este livro abriu sem os filtros")
    # etapa 4 do layout: o "Aplicar em" mora no pé do painel Filtro
    botoes = _botoes(tela.paineis.filtro_da_pagina.pe)
    assert "daqui em diante" in botoes and "só nas próximas" not in botoes


# --- o Propriedades do Endireitar e do Dividir ---------------------------------


def test_o_propriedades_do_endireitar_tem_os_nomes_novos(janela, pasta):
    tela = _aberta(janela, pasta)
    tela.trilha.escolher(FERRAMENTA_ENDIREITAR)
    _assentar()
    assert tela.barra_botoes.height() == 0
    conteudo = tela.propriedades_das_abas["angulo"]
    botoes = _botoes(conteudo)
    assert "deixar como veio" in botoes and "usar o ângulo do programa" in botoes
    assert "não endireitar esta" not in botoes and "voltar ao automático" not in botoes
    # as mesmas ações de antes
    pagina = janela.projeto.paginas[tela.indice_pagina]
    botoes["deixar como veio"].click()
    assert pagina.angulo_manual == 0.0
    botoes["usar o ângulo do programa"].click()
    assert pagina.angulo_manual is None
    partes = [r.text() for r in conteudo.findChildren(QLabel)]
    assert "SÓ NESTA PÁGINA" in partes and "PARA O LIVRO TODO" in partes
    assert any(t.startswith("Conta do endireitar:") for t in partes)
    # a mesma conta com uma palavra so no painel (805 C: "Editor")
    lista = tela.combo_conta_do_endireitar
    assert [lista.itemText(i) for i in range(lista.count())] == ["a do ScanTailor", "a do Editor"]
    from core import endireitar_scantailor as es
    assert [lista.itemData(i) for i in range(lista.count())] == list(es.JEITOS), "os codigos nao mudam"
    tela.paineis.abrir("props")
    _assentar()
    assert tela.paineis.propriedades.cabecalho.subtitulo.text() == "Endireitar"
    for botao in botoes.values():
        assert botao.isVisible(), botao.text()


def test_as_duas_listas_aplicar_em_dizem_folha_ou_pagina(janela, pasta):
    """Rodada 12, 709 B. Só o texto muda: os códigos são os de core/girar."""
    tela = _aberta(janela, pasta)

    def itens(combo) -> list[str]:
        return [combo.itemText(i) for i in range(combo.count())]

    def codigos(combo) -> list[str]:
        return [combo.itemData(i) for i in range(combo.count())]

    do_girar, do_endireitar = tela.barra_girar.combo_alcance, tela.combo_alcance_do_angulo
    assert itens(do_girar)[:2] == ["só esta folha", "todas as folhas"]
    assert itens(do_endireitar)[:2] == ["só esta página", "todas as páginas"]
    assert itens(do_girar)[2:] == itens(do_endireitar)[2:] == [
        "daqui em diante", "só as pares", "só as ímpares"]
    assert codigos(do_girar) == codigos(do_endireitar) == list(girar.ALCANCES)
    # o menu Página usa as mesmas palavras da lista do girar
    assert janela.menu.acoes["giro_em_esta"].text() == "só esta folha"
    assert janela.menu.acoes["giro_em_todas"].text() == "todas as folhas"


def test_o_propriedades_do_dividir(janela, pasta):
    tela = _aberta(janela, pasta)
    tela.trilha.escolher(FERRAMENTA_DIVIDIR)
    _assentar()
    assert tela.barra_botoes.height() == 0
    conteudo = tela.propriedades_das_abas["corte"]
    botoes = _botoes(conteudo)
    assert "usar em todas" in botoes
    assert "girar" not in botoes, "o girar e um so: o bloco no alto do painel"
    assert tela.botao_nao_dividir in botoes.values()
    assert conteudo.isAncestorOf(tela.combo_jeito_da_folha)
    partes = [r.text() for r in conteudo.findChildren(QLabel)]
    assert "SÓ NESTA FOLHA" in partes and "PARA O LIVRO TODO" in partes
    assert any(t.startswith("Jeito de dividir:") for t in partes)
    tela.paineis.abrir("props")
    assert tela.paineis.propriedades.cabecalho.subtitulo.text() == "Dividir a folha"


def test_o_propriedades_segue_a_ferramenta(janela, pasta):
    """Rodada 9, 402 C: trocar de ferramenta troca o conteúdo do painel."""
    tela = _aberta(janela, pasta)
    tela.paineis.abrir("props")
    painel = tela.paineis.propriedades
    for ferramenta, aba in ((FERRAMENTA_CORTAR, "bordas"), (FERRAMENTA_ENDIREITAR, "angulo"),
                            (FERRAMENTA_DIVIDIR, "corte")):
        tela.trilha.escolher(ferramenta)
        _assentar()
        assert painel.conteudo == aba
        assert tela.propriedades_das_abas[aba].isVisible()
        outras = [w for chave, w in tela.propriedades_das_abas.items() if chave != aba]
        assert not any(w.isVisible() for w in outras)


def test_com_as_ferramentas_de_marcar_o_propriedades_mostra_o_marcar_como(janela, pasta):
    from core import pipeline

    janela.abrir_livro(str(_pdf(pasta, folhas=3)))
    janela._analise_pronta(pipeline.analisar_projeto(janela.projeto))   # com o Marcar
    tela = janela.tela_conferir
    if "marcar" not in tela._abas_ativas:
        pytest.skip("este livro abriu sem as ferramentas de marcar")
    janela.resize(1280, 657)
    janela.show()
    tela.escolher_ferramenta("laco")
    painel = tela.paineis.propriedades
    tela.paineis.abrir("props")
    _assentar()
    assert painel.conteudo == painel.CONTEUDO_DE_MARCAR
    assert painel.marcar_como.isVisible()
    assert painel.cabecalho.subtitulo.text() == "Laço"
    tela.escolher_ferramenta("zoom")
    assert painel.conteudo == painel.SEM_PROPRIEDADES
    assert "Zoom" in painel.sem_propriedades.text()


# --- a linha dos menus só com o nome (702 C) -----------------------------------


def test_a_linha_dos_menus_mostra_so_o_nome_da_ferramenta(janela, pasta):
    tela = _aberta(janela, pasta)
    for ferramenta, nome in ((FERRAMENTA_CORTAR, "Cortar as bordas"),
                             (FERRAMENTA_ENDIREITAR, "Endireitar"),
                             (FERRAMENTA_DIVIDIR, "Dividir a folha")):
        tela.trilha.escolher(ferramenta)
        assert tela.barra_opcoes.rotulo.text() == nome
        assert tela.barra_opcoes.dica.text() == ""
        assert not tela.barra_opcoes.dica.isVisible()
        # a frase do que fazer continua existindo: no balão da ferramenta, na trilha
        from ui.widgets.trilha_agrupada import grupo_de
        assert USOS[ferramenta] in tela.trilha.texto_da_dica(grupo_de(ferramenta))


def test_trocar_de_livro_refaz_o_propriedades(janela, pasta):
    """Abrir outro livro joga fora os botões do anterior e monta os novos."""
    tela = _aberta(janela, pasta)
    antigo = tela.propriedades_das_abas["bordas"]
    tela.paineis.abrir("props")
    _analisar(janela)                       # a conferência de novo: a tela recarrega
    _assentar()
    novo = tela.propriedades_das_abas["bordas"]
    assert novo is not antigo
    assert tela.paineis.propriedades.tem_conteudo("bordas")
    tela.trilha.escolher(FERRAMENTA_CORTAR)
    _assentar()
    assert novo.isVisible()
    assert tela.paineis.aberto == "props", "o painel continua como a pessoa deixou"
