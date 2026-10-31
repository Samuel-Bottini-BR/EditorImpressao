"""As provas da D-594 e da parte da D-577 que faltava (o "comparar" com as opções nos dois
lados e o "usar este"). CLAUDE.md §11, regra 4; Livro de decisões, docs/plano/DECISOES.md.

  D-594 (31/10/2026): "Outra coisa, no automatico não tem opções que encontramos nos filtros da
      aba da area de trabalho." · print do "Mais ajustes": "os tipos de preto." · "mas isso era
      uma coisa obvia que deveria ter". No Livro: a etapa "Limpar a folha" do Automático tem
      todas as opções do painel Filtro da área de trabalho, com os mesmos nomes. Prova pedida:
      "Abrir o Automático, etapa "Limpar a folha" → cada opção do "Mais ajustes" do painel
      Filtro aparece, e rodar com ela dá o mesmo resultado que escolhê-la no painel".
  D-577 (3º teste, 30/10): "seria bom se pudessemos ver as opções e mudar simutaneamente nesse
      comparar, tivesse uma aba de cada lado que abrisse e fechasse para mudar as opções no
      comparar" · "não, eu quero poder mudar dos dois lados, todas as opções." · "usar este" em
      cada lado → "ok, não gostei do nome, mas vamos ficar com esse por enquanto." No Livro:
      "cada lado com uma aba que abre e fecha com todas as opções do Automático, mudando à
      parte; cada lado com "usar este" (nome provisório), que passa as opções daquele lado para
      a janela; o "Rodar" usa as da janela."

O que se mede: os nomes dos controles do painel Filtro (lidos da tela de verdade) contra os da
janela do Automático; os campos da página e a página desenhada depois de escolher no painel e
depois de rodar o Automático (dois livros iguais); o "depois" da prévia; a receita; e, no
"comparar", o estado de cada lado e o da janela. Livro sintético do tests/test_decisoes_automatico.py.
"""

from __future__ import annotations

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtCore import Qt  # noqa: E402

from core import automatico as A  # noqa: E402
from core import perfis  # noqa: E402
from core import preto_e_branco_scantailor as PBST  # noqa: E402
from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from tests.test_decisoes_automatico import _livro  # noqa: E402
from tests.test_decisoes_automatico_ver_como_fica import (  # noqa: E402,F401 - fixtures
    _abrir, _assentar, _esperar, _imagens, app, janela, pasta)

PAGINA = 2          # a folha reta do livro sintético


def _textos(widget) -> set[str]:
    """Os textos de todas as caixinhas, rótulos e listas dentro de `widget`."""
    from PySide6.QtWidgets import QAbstractButton, QComboBox, QLabel

    textos = set()
    for filho in widget.findChildren(QAbstractButton) + widget.findChildren(QLabel):
        textos.add(filho.text().strip())
    for combo in widget.findChildren(QComboBox):
        textos.update(combo.itemText(i) for i in range(combo.count()))
    return textos


def _itens(combo) -> list:
    return [(combo.itemText(i), combo.itemData(i)) for i in range(combo.count())]


# --- D-594: os nomes ------------------------------------------------------------------

def test_d594_cada_opcao_do_painel_filtro_esta_no_limpar_a_folha_com_o_mesmo_nome(janela, app, tmp_path):
    """Abrir o Automático, etapa "Limpar a folha": cada opção do painel "Filtro da página" da
    área de trabalho aparece, com o mesmo nome (lido da tela de conferir de verdade), e só na
    página do "Limpar a folha"."""
    grande = _abrir(janela, app, tmp_path, pagina=PAGINA)
    tc = janela.tela_conferir
    limpar = grande.paginas_das_etapas[A.LIMPAR]
    nomes_do_painel = [tc.caixa_claro_no_escuro.text(), tc.caixa_letras_com_a_cor.text(),
                       tc.caixa_reduzir_cores.text(), tc.caixa_luz_igualar.text(),
                       tc.caixa_luz_suavizar.text(), tc.rotulo_luz_chuvisco.text(),
                       tc.caixa_respeitar_gravuras.text(), tc.rotulo_algoritmo_pb.text(),
                       "Ajuste", "Mais ajustes"]
    textos = _textos(limpar)
    for nome in nomes_do_painel:
        assert nome in textos, f"\"{nome}\" (painel Filtro) não está no \"Limpar a folha\" do Automático"
    # os jeitos do preto e branco ("os tipos de preto"): os mesmos, na mesma ordem
    assert _itens(grande.combo_algoritmo_pb) == _itens(tc.seletor_algoritmo_pb)
    assert any(PBST.NOMES_NA_TELA[c] in textos for c in PBST.CODIGOS)
    # "Limpar a sujeira" (já estava): as mesmas escolhas
    assert [d for _t, d in _itens(grande.combo_pontinhos)] == [d for _t, d in _itens(tc.seletor_pontinhos)]
    # a barra do "Ajuste" com o nome do painel em cada filtro
    from ui.tela_conferir import ROTULOS_DO_AJUSTE

    for filtro, (rotulo, esquerda, direita) in ROTULOS_DO_AJUSTE.items():
        grande.estado.definir_opcao("filtro_padrao", filtro)
        assert not grande.bloco_ajuste.isHidden()
        assert (grande.medidor.rotulo.text(), grande.medidor.ponta_esquerda.text(),
                grande.medidor.ponta_direita.text()) == (rotulo, esquerda, direita)
    # cada controle mora na página do "Limpar a folha" e muda o estado
    for campo in A.CAMPOS_DA_PAGINA:
        assert campo in A.OPCOES[A.LIMPAR] and campo in A.todas_as_opcoes()
        assert limpar.isAncestorOf(grande.controles[campo]), campo
        assert campo in grande.estado.opcoes, f"{campo} sem valor na janela"


def test_d594_aparecem_como_no_painel_conforme_o_filtro(janela, app, tmp_path):
    """As mesmas regras de aparecer do painel Filtro: o jeito do preto e branco, "Letras com a
    cor delas" e "Suavizar as letras" só no Preto e branco; o "Ajuste" e o "Mais ajustes" nos
    filtros com ajuste; "Respeitar as gravuras achadas" em todos, cinza com "Só as letras"
    (D-587)."""
    grande = _abrir(janela, app, tmp_path, pagina=PAGINA)
    e = grande.estado
    so_pb = ("letras_com_a_cor", "luz_suavizar")
    for filtro in (PRETO_E_BRANCO, MELHORAR, MAGICO_PRO, ORIGINAL):
        e.definir_opcao("filtro_padrao", filtro)
        com_ajuste = filtro != ORIGINAL
        assert grande.bloco_mais.isHidden() is not com_ajuste, filtro
        assert grande.bloco_ajuste.isHidden() is not com_ajuste, filtro
        assert grande.combo_algoritmo_pb.isHidden() is (filtro != PRETO_E_BRANCO), filtro
        for campo in so_pb:
            assert grande.controles[campo].isHidden() is (filtro != PRETO_E_BRANCO), (campo, filtro)
        assert not grande.cx_respeitar_gravuras.isHidden(), filtro
    e.definir_opcao("filtro_padrao", PRETO_E_BRANCO)
    e.definir_opcao("misto_so_as_letras", True)
    assert not grande.cx_respeitar_gravuras.isEnabled()
    e.definir_opcao("misto_so_as_letras", False)
    assert grande.cx_respeitar_gravuras.isEnabled()


# --- D-594: o mesmo resultado que o painel --------------------------------------------

def _no_painel(tc, filtro, campo, valor) -> None:
    """Escolhe no painel Filtro da página da vez, pelos mesmos métodos que os controles chamam."""
    tc._escolher_filtro(filtro)
    if campo in ("forca_preto", "clareza_melhorar", "intensidade_magico"):
        tc._medidor_pegou()
        tc.medidor.barra.setValue(valor)
        tc._medidor_soltou(valor)
    elif campo == "algoritmo_preto_branco":
        tc._mudar_algoritmo_pb(tc.seletor_algoritmo_pb.findData(valor))
    elif campo == "claro_no_escuro":
        tc._mudar_claro_no_escuro(valor)
    elif campo in ("letras_com_a_cor", "reduzir_cores"):
        tc._mudar_cores(campo, valor)
    elif campo in ("luz_igualar", "luz_suavizar", "luz_chuvisco"):
        tc._mudar_luz(campo, valor)
    elif campo == "respeitar_gravuras_achadas":
        tc._mudar_respeitar_gravuras(valor)


def _na_janela(grande, filtro, campo, valor) -> None:
    """Escolhe na janela do Automático, pelos controles dela."""
    grande.radios_de_filtro[filtro].setChecked(True)
    controle = grande.controles[campo]
    if campo in ("forca_preto", "clareza_melhorar", "intensidade_magico"):
        controle.barra.setValue(valor)
    elif campo == "algoritmo_preto_branco":
        controle.setCurrentIndex(controle.findData(valor))
    elif campo == "luz_chuvisco":
        controle.setValue(valor)
    else:
        controle.setChecked(valor)
    assert grande.estado.opcoes[campo] == valor, campo


def _desenho(projeto, indice):
    """A página desenhada (core/pipeline, o desenho do PDF), numa cópia em que a marcação
    achada sozinha é feita de novo na hora: a tela de conferir guarda a marcação provisória
    quando mostra a página, e isso acontece em momentos diferentes nos dois caminhos (não é
    o que se compara aqui)."""
    import copy

    from core.pipeline import renderizar_pagina

    copia = copy.deepcopy(projeto)
    pagina = copia.paginas[indice]
    pagina.selecao, pagina.gravura_feita_com, pagina.marcacao_provisoria = [], "", False
    with fitz.open(copia.caminho_entrada) as doc:
        img, _ = renderizar_pagina(doc, copia, pagina, dpi=90)
    return np.asarray(img)


CASOS = [
    (PRETO_E_BRANCO, "forca_preto", 80),
    (MELHORAR, "clareza_melhorar", 85),
    (MAGICO_PRO, "intensidade_magico", 20),
    (PRETO_E_BRANCO, "algoritmo_preto_branco", PBST.CODIGOS[0]),
    (PRETO_E_BRANCO, "claro_no_escuro", True),
    (PRETO_E_BRANCO, "letras_com_a_cor", True),
    (MELHORAR, "reduzir_cores", True),
    (MAGICO_PRO, "luz_igualar", True),
    (PRETO_E_BRANCO, "luz_suavizar", True),
    (PRETO_E_BRANCO, "luz_chuvisco", 30),
    (PRETO_E_BRANCO, "respeitar_gravuras_achadas", False),
]


@pytest.mark.parametrize("filtro,campo,valor", CASOS, ids=[c[1] for c in CASOS])
def test_d594_rodar_com_a_opcao_da_o_mesmo_que_escolher_no_painel(janela, app, tmp_path, filtro, campo, valor):
    """No mesmo livro e na mesma página: (1) a opção é escolhida na janela do Automático, que
    roda o "Limpar a folha" com o filtro só nessa página; o Ctrl+Z desfaz o Automático inteiro
    (a página volta a ser a de fábrica); (2) o Automático roda de novo com o mesmo filtro e a
    opção como numa página nova, e a opção é escolhida no painel Filtro. Os campos da página
    (os do painel) e a página desenhada saem iguais nos dois. (O Automático roda nos dois para a
    página ficar com o mesmo "Limpar a folha" ligado nela: com ele, a página ganha a marcação
    achada sozinha, que muda o desenho; não é o que se compara aqui. Dois livros com o mesmo
    PDF não servem: o programa reconhece o mesmo livro e abre o mesmo projeto.)"""
    from ui.automatico import NA_PAGINA

    campos = ("filtro",) + A.CAMPOS_DA_PAGINA
    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    tc = janela.tela_conferir
    tc.ir_para_pagina(PAGINA)
    de_fabrica = {c: getattr(janela.projeto.paginas[PAGINA], c) for c in campos}
    assert de_fabrica[campo] != valor

    # 1) no Automático
    grande = janela.abrir_o_automatico()
    e = grande.estado
    e.marcadas = {A.LIMPAR}
    e.definir_alcance(NA_PAGINA)
    _na_janela(grande, filtro, campo, valor)
    janela._fechar_a_janela_do_automatico()
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    pagina = janela.projeto.paginas[PAGINA]
    assert getattr(pagina, campo) == valor, "o Automático não gravou a opção na página"
    do_automatico = {c: getattr(pagina, c) for c in campos}
    desenho_do_automatico = _desenho(janela.projeto, PAGINA)

    # o Ctrl+Z desfaz o Automático inteiro, com a opção junto
    tc.desfazer()
    _assentar(app)
    assert {c: getattr(janela.projeto.paginas[PAGINA], c) for c in campos} == de_fabrica

    # 2) o Automático só com o filtro, e a opção no painel Filtro
    grande = janela.abrir_o_automatico()
    e = grande.estado
    e.marcadas = {A.LIMPAR}
    e.definir_alcance(NA_PAGINA)
    grande.radios_de_filtro[filtro].setChecked(True)
    assert e.opcoes[campo] == de_fabrica[campo]
    janela._fechar_a_janela_do_automatico()
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    assert getattr(janela.projeto.paginas[PAGINA], campo) == de_fabrica[campo]
    tc.ir_para_pagina(PAGINA)
    _no_painel(tc, filtro, campo, valor)
    pagina = janela.projeto.paginas[PAGINA]
    assert getattr(pagina, campo) == valor, "o painel não gravou (a prova não valeria)"
    assert {c: getattr(pagina, c) for c in campos} == do_automatico
    assert np.array_equal(_desenho(janela.projeto, PAGINA), desenho_do_automatico),         "a página desenhada saiu diferente da escolhida no painel"


def test_d594_a_previa_mostra_a_mudanca_da_opcao(janela, app, tmp_path):
    """D-577 + D-594: na janela, mudar "Tirar o chuvisco" muda o "depois" da página da direita;
    voltar ao 0 volta ao de antes."""
    grande = _abrir(janela, app, tmp_path, pagina=PAGINA)
    painel = grande.antes_e_depois
    e = grande.estado
    e.marcar(A.LIMPAR, True)
    e.definir_opcao("filtro_padrao", MAGICO_PRO)
    _esperar(app, painel)
    _antes, sem = _imagens(painel)
    grande.seletor_luz_chuvisco.setValue(60)
    _esperar(app, painel)
    _antes, com = _imagens(painel)
    assert sem is not None and com is not None
    assert not np.array_equal(sem, com), "o depois não mudou com \"Tirar o chuvisco\""
    grande.seletor_luz_chuvisco.setValue(0)
    _esperar(app, painel)
    assert np.array_equal(_imagens(painel)[1], sem)


def test_d594_a_receita_leva_as_opcoes_novas_e_a_antiga_continua_valendo(janela, app, tmp_path, monkeypatch):
    """A receita guarda as opções novas como as outras; posta, elas voltam. Receita guardada
    antes (sem as chaves novas) continua valendo: as opções novas ficam como estavam. A caixa
    da receita diz o que vai dentro (D-071)."""
    from ui.automatico import EstadoDoAutomatico, texto_das_opcoes

    guardado = {}
    monkeypatch.setattr(perfis, "_ler", lambda chave, padrao: guardado.get(chave, padrao))
    monkeypatch.setattr(perfis, "_escrever", lambda chave, valor: guardado.__setitem__(chave, valor))
    e = EstadoDoAutomatico()
    e.opcoes = {**A.de_fabrica_da_pagina(), "filtro_padrao": PRETO_E_BRANCO,
                "luz_chuvisco": 30, "algoritmo_preto_branco": PBST.CODIGOS[0]}
    nome = perfis.guardar_receita("Com chuvisco", e.opcoes, [A.LIMPAR])
    dados = perfis.ler(nome)
    assert dados["luz_chuvisco"] == 30 and dados["algoritmo_preto_branco"] == PBST.CODIGOS[0]
    assert "Tirar o chuvisco: 30" in texto_das_opcoes(A.LIMPAR, e.opcoes)
    outro = EstadoDoAutomatico()
    outro.opcoes = dict(A.de_fabrica_da_pagina())
    assert outro.por_receita(nome)
    assert outro.opcoes["luz_chuvisco"] == 30
    # receita antiga, sem as chaves novas
    guardado["perfis"]["Antiga"] = {"limpar": True, "filtro_padrao": MELHORAR}
    outro.opcoes["luz_chuvisco"] = 10
    assert outro.por_receita("Antiga")
    assert outro.opcoes["filtro_padrao"] == MELHORAR and outro.opcoes["luz_chuvisco"] == 10
    # "De fábrica" devolve as de uma página nova
    assert outro.por_receita(perfis.NOME_DE_FABRICA)
    assert outro.opcoes["luz_chuvisco"] == 0 and outro.opcoes["respeitar_gravuras_achadas"] is True


# --- D-577: o "comparar" com as opções nos dois lados ----------------------------------

def _comparar(grande, app):
    from PySide6.QtWidgets import QPushButton  # noqa: F401

    painel = grande.antes_e_depois
    painel.abrir_em_tela_cheia()
    tela = painel.tela_cheia
    tela.botao_comparar.click()
    _assentar(app)
    _esperar(app, painel)
    return painel, tela


def _esperar_lado(app, painel, lado):
    _esperar(app, painel)
    if lado.motor is not None:
        _esperar(app, lado.motor)
    _assentar(app)


def test_d577_cada_lado_do_comparar_tem_a_aba_com_todas_as_opcoes_e_o_usar_este(janela, app, tmp_path):
    """Cada lado do "comparar" tem a aba que abre e fecha com o MESMO painel de opções da
    janela (a mesma classe, com as etapas e as opções de todas elas, também as da D-594) e o
    "usar este"."""
    from ui.automatico import PainelDeOpcoes

    grande = _abrir(janela, app, tmp_path, pagina=PAGINA)
    _painel, tela = _comparar(grande, app)
    for lado in (tela.lado_a, tela.lado_b):
        assert isinstance(lado.painel, PainelDeOpcoes) and type(lado.painel) is type(grande.painel_de_opcoes)
        assert lado.botao_usar.text() == "usar este"
        assert lado.aba.isHidden()
        lado.botao_opcoes.click()
        assert not lado.aba.isHidden(), "a aba das opções não abriu"
        assert set(lado.painel.controles) == set(grande.controles)
        assert set(lado.painel.paginas_das_etapas) == set(A.ETAPAS)
        assert lado.painel.lista.count() == len(A.ETAPAS)
        lado.botao_opcoes.click()
        assert lado.aba.isHidden(), "a aba das opções não fechou"
        assert lado.estado is not grande.estado
    # começam como era: a esquerda, o livro como está; a direita, as opções da janela
    assert tela.rotulo_a.text().startswith("como está no livro")
    assert tela.lado_b.estado.opcoes == grande.estado.opcoes


def test_d577_mudar_um_lado_nao_muda_a_janela_e_usar_este_passa_para_ela(janela, app, tmp_path):
    """Mudar as opções do lado direito muda o que ele mostra, não a janela nem o outro lado;
    "usar este" passa as opções dele para a janela (e o "Rodar" usa as da janela). O mesmo do
    lado esquerdo. Nada muda no livro."""
    import dataclasses
    import json

    import time

    grande = _abrir(janela, app, tmp_path, pagina=PAGINA)
    # a medida do livro por trás (D-284) põe os avisos sozinha logo depois de abrir: espera
    # ela acabar antes de fotografar o livro (como na prova da D-577 "mexer e fechar")
    fim = time.monotonic() + 180
    while getattr(janela, "medida_ao_abrir", None) is not None and time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.02)
    _assentar(app)
    livro_antes = json.dumps(dataclasses.asdict(janela.projeto), sort_keys=True, default=str)
    feitas = len(janela.acoes.feitas)
    e = grande.estado
    e.marcar(A.LIMPAR, True)
    e.definir_opcao("filtro_padrao", PRETO_E_BRANCO)
    painel, tela = _comparar(grande, app)
    depois_da_janela = painel.visor._crus[1].copy()

    # o lado direito: Mágico pro com "Tirar o chuvisco"
    b = tela.lado_b
    b.botao_opcoes.click()
    b.painel.radios_de_filtro[MAGICO_PRO].setChecked(True)
    b.painel.seletor_luz_chuvisco.setValue(30)
    _esperar_lado(app, painel, b)
    assert e.opcoes["filtro_padrao"] == PRETO_E_BRANCO, "mudar o lado mudou a janela"
    assert b.mexido and tela.rotulo_b.text() == "depois: Mágico pro"
    img_b = b.imagem_e_rotulo()[0]
    assert img_b is not None and not np.array_equal(np.asarray(img_b), depois_da_janela)
    assert tela.lado_a.estado.opcoes.get("filtro_padrao") != MAGICO_PRO
    b.botao_usar.click()
    _assentar(app)
    assert e.opcoes["filtro_padrao"] == MAGICO_PRO and e.opcoes["luz_chuvisco"] == 30
    assert e.marcadas == b.estado.marcadas
    pedido = e.pedido()                              # o que o "Rodar" usa
    assert pedido.opcoes["filtro_padrao"] == MAGICO_PRO and pedido.opcoes["luz_chuvisco"] == 30

    # o lado esquerdo: Melhorar
    a = tela.lado_a
    a.botao_opcoes.click()
    a.painel.lista.item_da_etapa(A.LIMPAR).setCheckState(Qt.Checked)
    a.painel.radios_de_filtro[MELHORAR].setChecked(True)
    _esperar_lado(app, painel, a)
    assert a.mexido and tela.rotulo_a.text() == "depois: Melhorar"
    assert e.opcoes["filtro_padrao"] == MAGICO_PRO
    a.botao_usar.click()
    _assentar(app)
    assert e.opcoes["filtro_padrao"] == MELHORAR and A.LIMPAR in e.marcadas
    # o lado direito já mexido não acompanha a janela
    assert b.estado.opcoes["filtro_padrao"] == MAGICO_PRO
    tela.accept()
    _assentar(app)
    assert json.dumps(dataclasses.asdict(janela.projeto), sort_keys=True, default=str) == livro_antes
    assert len(janela.acoes.feitas) == feitas, "o comparar entrou no desfazer"


def test_d577_lado_direito_nao_mexido_acompanha_a_janela(janela, app, tmp_path):
    """O lado direito, enquanto não é mexido, mostra o "depois" da janela e acompanha as opções
    dela (o "usar este" da esquerda muda os dois)."""
    grande = _abrir(janela, app, tmp_path, pagina=PAGINA)
    e = grande.estado
    e.marcar(A.LIMPAR, True)
    e.definir_opcao("filtro_padrao", PRETO_E_BRANCO)
    painel, tela = _comparar(grande, app)
    a, b = tela.lado_a, tela.lado_b
    a.painel.radios_de_filtro[MAGICO_PRO].setChecked(True)
    a.painel.lista.item_da_etapa(A.LIMPAR).setCheckState(Qt.Checked)
    a.botao_usar.click()
    _esperar_lado(app, painel, a)
    assert not b.mexido and b.estado.opcoes["filtro_padrao"] == MAGICO_PRO
    assert tela.rotulo_b.text() == "depois: Mágico pro"
