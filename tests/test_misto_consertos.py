"""Consertos do modo Misto pedidos pelo parecer do verificador (05/10/2026).

Parecer: relatorios/conferir/misto-no-programa-2026-10-05/verificador/
parecer-verificador-misto-no-programa.md. Um bloco por conserto:

1. Alerta "Tem cor" falso com "So as letras" ligada (bug Misto 1, print 14):
   com o Misto, a ilustracao sai em cor, entao o alerta "o preto e branco vai
   perder a ilustracao" (e o botao "usar Magico pro nesta") nao vale. Volta
   quando "So as letras" e desligada. O "Para revisar" acompanha.

Testes de maquina, sem janela na tela (tests/conftest.py).
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from core import analise, misto, pipeline  # noqa: E402
from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _pdf,
    app,
    janela,
    pasta,
)


@pytest.fixture(autouse=True)
def leitor_rapido(monkeypatch):
    """As previas de fundo nao chamam o leitor de texto de verdade."""
    monkeypatch.setattr(pipeline.linhas_do_texto, "linhas_da_pagina", lambda *a, **k: [])
    monkeypatch.setattr(pipeline.linhas_do_texto, "aquecer_em_segundo_plano", lambda: None)


def _pdf_com_cor(pasta, folhas: int = 4, coloridas=(0,)):
    """PDF de `folhas` folhas com texto; as de `coloridas` com um bloco
    vermelho grande (a "ilustracao")."""
    (pasta / "livros").mkdir(exist_ok=True)
    caminho = pasta / "livros" / "Livro com cor.pdf"
    doc = fitz.open()
    for i in range(folhas):
        pagina = doc.new_page(width=400, height=560)
        for linha in range(12):
            pagina.insert_text((40, 60 + 30 * linha), f"folha {i} linha {linha} texto",
                               fontsize=14)
        if i in coloridas:
            pagina.draw_rect(fitz.Rect(60, 200, 340, 420), color=(0.8, 0.1, 0.1),
                             fill=(0.85, 0.15, 0.1))
    doc.save(str(caminho))
    doc.close()
    return caminho


def _projeto_com_cor(n: int = 4) -> Projeto:
    """Projeto em memoria: livro em Preto e branco, a pagina 0 com cor e o
    alerta "Tem cor" posto pela analise."""
    projeto = Projeto(caminho_entrada="nao-existe.pdf", filtro_padrao=PRETO_E_BRANCO,
                      dividir_folhas=False, detectar_regioes=False)
    projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(n)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i, filtro=PRETO_E_BRANCO) for i in range(n)]
    projeto.paginas[0].tem_cor = True
    projeto.paginas[0].alertas = [analise.COR]
    return projeto


# --- 1. o alerta "Tem cor" segue o "So as letras" ------------------------------

def test_so_as_letras_do_livro_tira_o_alerta_de_cor_e_desligar_devolve():
    projeto = _projeto_com_cor()
    pagina = projeto.paginas[0]
    assert projeto.pendentes_de_revisao() == 1

    projeto.misto_so_as_letras = True
    pipeline.acertar_alertas_de_cor(projeto)
    assert analise.COR not in pagina.alertas
    assert projeto.pendentes_de_revisao() == 0

    projeto.misto_so_as_letras = False
    pipeline.acertar_alertas_de_cor(projeto)
    assert pagina.alertas == [analise.COR]
    assert projeto.pendentes_de_revisao() == 1


def test_so_as_letras_so_na_pagina():
    projeto = _projeto_com_cor()
    pagina = projeto.paginas[0]
    pagina.misto_so_as_letras = True
    pipeline.acertar_alertas_de_cor(projeto)
    assert analise.COR not in pagina.alertas
    # o livro ligado e a pagina desligada so nela: o alerta volta
    projeto.misto_so_as_letras = True
    pagina.misto_so_as_letras = False
    pipeline.acertar_alertas_de_cor(projeto)
    assert analise.COR in pagina.alertas


def test_sem_limpar_a_folha_o_misto_nao_vale_e_o_alerta_fica():
    """A mesma conta de core.pipeline._filtrar: sem "Limpar a folha" nada de
    Misto, e a pagina sai como veio - o alerta fica como a analise pos."""
    projeto = _projeto_com_cor()
    projeto.limpar = False
    projeto.misto_so_as_letras = True
    pipeline.acertar_alertas_de_cor(projeto)
    assert projeto.paginas[0].alertas == [analise.COR]


def test_pagina_sem_o_misto_nao_muda():
    """Sem "So as letras", nada muda em pagina nenhuma: nem o alerta que ja
    estava, nem pagina sem alerta (outro filtro, livro em outro filtro)."""
    projeto = _projeto_com_cor()
    projeto.paginas[1].tem_cor = True
    projeto.paginas[1].filtro = MAGICO_PRO               # escolheu outro filtro
    projeto.paginas[2].tem_cor = True
    projeto.paginas[2].alertas = [analise.COR]
    projeto.paginas[2].filtro = MELHORAR                 # "usar Magico pro" etc.
    antes = [list(p.alertas) for p in projeto.paginas]
    pipeline.acertar_alertas_de_cor(projeto)
    assert [p.alertas for p in projeto.paginas] == antes

    outro = _projeto_com_cor()
    outro.filtro_padrao = MELHORAR
    outro.paginas[0].alertas = []          # a analise nao poe o alerta fora do P&B
    pipeline.acertar_alertas_de_cor(outro)
    assert outro.paginas[0].alertas == []


def test_livro_inteiro_colorido_nao_volta_para_as_paginas():
    """Quando o "Tem cor" virou observacao do livro, desligar o Misto nao
    devolve o alerta a cada pagina (seria o contador afogado de novo)."""
    projeto = _projeto_com_cor()
    for p in projeto.paginas:
        p.tem_cor = True
        p.alertas = []
    projeto.observacoes = [analise.OBSERVACOES[analise.COR]]
    projeto.misto_so_as_letras = True
    pipeline.acertar_alertas_de_cor(projeto)
    projeto.misto_so_as_letras = False
    pipeline.acertar_alertas_de_cor(projeto)
    assert all(p.alertas == [] for p in projeto.paginas)


def test_pagina_em_branco_nao_ganha_o_alerta_de_cor():
    projeto = _projeto_com_cor()
    projeto.paginas[1].tem_cor = True
    projeto.paginas[1].alertas = [analise.EM_BRANCO]
    projeto.misto_so_as_letras = True
    pipeline.acertar_alertas_de_cor(projeto)
    projeto.misto_so_as_letras = False
    pipeline.acertar_alertas_de_cor(projeto)
    assert projeto.paginas[1].alertas == [analise.EM_BRANCO]


def test_desligar_nao_mexe_no_conferida():
    """O alerta volta como estava: pagina ja conferida continua conferida."""
    projeto = _projeto_com_cor()
    pagina = projeto.paginas[0]
    pagina.revisada = True
    projeto.misto_so_as_letras = True
    pipeline.acertar_alertas_de_cor(projeto)
    projeto.misto_so_as_letras = False
    pipeline.acertar_alertas_de_cor(projeto)
    assert pagina.alertas == [analise.COR] and pagina.revisada is True


@pytest.mark.parametrize("so_as_letras", [False, True])
def test_a_analise_ja_sai_sem_o_alerta_com_o_misto_ligado(pasta, so_as_letras):
    caminho = _pdf_com_cor(pasta)
    projeto = Projeto(caminho_entrada=str(caminho), filtro_padrao=PRETO_E_BRANCO,
                      dividir_folhas=False, detectar_regioes=False,
                      misto_so_as_letras=so_as_letras)
    pipeline.analisar_projeto(projeto)
    pagina = projeto.paginas[0]
    assert pagina.tem_cor, "o PDF de teste tinha de ter cor na folha 0"
    assert (analise.COR in pagina.alertas) is (not so_as_letras)
    assert all(analise.COR not in p.alertas for p in projeto.paginas[1:])


# --- 1. na tela de conferir ----------------------------------------------------

@pytest.fixture
def conferir_cor(app, pasta):
    """Tela de conferir na aba Filtro com 4 paginas em Preto e branco, a
    primeira com cor e o alerta "Tem cor"."""
    from historico_acoes import HistoricoAcoes
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    caminho = _pdf(pasta, folhas=4)
    projeto = _projeto_com_cor()
    projeto.caminho_entrada = str(caminho)
    tela = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("filtro"))
    tela.ir_para_pagina(0)
    yield tela
    previas.parar()


def _mensagem_de_cor() -> str:
    return analise.descrever(analise.COR).mensagem


def test_na_tela_o_alerta_some_com_so_as_letras_e_volta_ao_desligar(conferir_cor):
    tela = conferir_cor
    projeto = tela.projeto
    sugestao = tela.botoes_de_sugestao["filtro"]
    assert tela.texto_faixa.text() == _mensagem_de_cor()
    assert not sugestao.isHidden() and sugestao.text() == "usar Mágico pro nesta"
    assert "1 página" in tela.botao_alertas.text()
    assert "Tem cor" in tela.paineis.para_revisar.cabecalho.text() or \
        "1" in tela.paineis.para_revisar.cabecalho.text()

    # "So as letras" so nesta pagina, pela caixinha da aba Filtro
    tela.escolhas_misto.caixa.setChecked(True)
    assert analise.COR not in projeto.paginas[0].alertas
    assert tela.texto_faixa.text() != _mensagem_de_cor()
    assert sugestao.isHidden()
    assert tela.botao_alertas.text() == "tudo certo"
    assert tela.paineis.para_revisar.cabecalho.text() == "Para revisar"

    # desligar: o alerta volta, com o botao e a contagem
    tela.escolhas_misto.caixa.setChecked(False)
    assert tela.texto_faixa.text() == _mensagem_de_cor()
    assert not sugestao.isHidden()
    assert "1 página" in tela.botao_alertas.text()

    # o desfazer (volta para "ligado") e o refazer acompanham
    tela.desfazer()
    assert tela.texto_faixa.text() != _mensagem_de_cor()
    tela.desfazer()
    assert tela.texto_faixa.text() == _mensagem_de_cor()


def test_na_tela_o_livro_inteiro_e_o_todas_acertam_todas_as_paginas(conferir_cor):
    """Com "So as letras" no livro (tela "O que fazer") ou levada a todas as
    paginas ("todas"), o contador e o "Para revisar" contam todas as paginas,
    e nao so a da vez."""
    tela = conferir_cor
    projeto = tela.projeto
    projeto.paginas[2].tem_cor = True
    projeto.paginas[2].alertas = [analise.COR]
    tela.atualizar()
    assert "2 páginas" in tela.botao_alertas.text()

    projeto.misto_so_as_letras = True          # como a tela "O que fazer" grava
    tela.atualizar()
    assert tela.botao_alertas.text() == "tudo certo"
    assert all(analise.COR not in p.alertas for p in projeto.paginas)

    projeto.misto_so_as_letras = False
    tela.atualizar()
    assert "2 páginas" in tela.botao_alertas.text()

    tela.escolhas_misto.caixa.setChecked(True)  # so na pagina 0
    assert "1 página" in tela.botao_alertas.text()
    tela._filtro_em_todas()                     # leva a todas
    assert tela.botao_alertas.text() == "tudo certo"
    tela.desfazer()
    assert "1 página" in tela.botao_alertas.text()


def test_misto_desligado_a_tela_mostra_o_alerta_como_antes(conferir_cor):
    tela = conferir_cor
    tela.ir_para_pagina(1)
    tela.ir_para_pagina(0)
    assert tela.texto_faixa.text() == _mensagem_de_cor()
    assert tela.projeto.paginas[0].alertas == [analise.COR]
    assert misto.opcoes_da_pagina(tela.projeto, tela.projeto.paginas[0]) is None


# --- 2. o cartao "Preto e branco" da aba Filtro mostra o Misto -----------------
#
# Bug Misto 2 do verificador (05/10, prints 09 e 10): numa pagina Original, o
# cartao "Preto e branco" mostrava a gravura em preto e branco (o filtro puro
# na amostra, ui/tarefas._TarefaCartoes) e, escolhido, a pagina saia com ela
# em cor (o Misto). Agora o cartao e a pagina desenhada pelo programa com o
# Misto (core.pipeline.renderizar_com_filtro), numa tarefa de previa.

@pytest.fixture
def conferir_original(app, pasta):
    """Aba Filtro com 3 paginas no Original; o livro em Preto e branco."""
    from historico_acoes import HistoricoAcoes
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    caminho = _pdf(pasta, folhas=3)
    projeto = Projeto(caminho_entrada=str(caminho), filtro_padrao=PRETO_E_BRANCO,
                      dividir_folhas=False, detectar_regioes=False)
    projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(3)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i, filtro=ORIGINAL) for i in range(3)]
    tela = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("filtro"))
    tela.ir_para_pagina(0)
    yield tela
    previas.parar()


def _espiar_o_cartao(tela, chave=PRETO_E_BRANCO):
    """Anota cada imagem posta no cartao (a ultima e a que ele mostra)."""
    postas: list = []
    cartao = tela.cartoes[chave]
    original = cartao.definir_amostra

    def definir(img):
        postas.append(img)
        original(img)

    cartao.definir_amostra = definir
    return postas


def _esperar(condicao, segundos: float = 30.0) -> bool:
    import time

    from PySide6.QtWidgets import QApplication

    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        QApplication.processEvents()
        if condicao():
            return True
        time.sleep(0.02)
    return False


def test_cartao_pb_com_so_as_letras_vem_do_programa(conferir_original, monkeypatch):
    import numpy as np

    from ui.tela_conferir import DPI_CARTAO_DO_MISTO

    tela = conferir_original
    pedidos: list = []
    do_programa = np.full((40, 30, 3), 7, np.uint8)

    def pegar_com_filtro(indice, dpi, filtro):
        pedidos.append((indice, dpi, filtro))
        return do_programa

    monkeypatch.setattr(tela.previas, "pegar_com_filtro", pegar_com_filtro)
    # a previa da pagina ja chegou (o cartao e pedido depois dela, como o
    # "Tirar o fundo": para nao disputar a maquina com ela)
    monkeypatch.setattr(tela.previas, "pegar",
                        lambda i, d: np.full((40, 30, 3), 128, np.uint8))
    postas = _espiar_o_cartao(tela)
    tela.projeto.misto_so_as_letras = True
    tela.atualizar()
    assert (0, DPI_CARTAO_DO_MISTO, PRETO_E_BRANCO) in pedidos
    assert postas and postas[-1] is not None and int(postas[-1].max()) == 7

    # a amostra pura que chega depois (_TarefaCartoes) nao passa por cima
    puro = np.full((40, 30, 3), 200, np.uint8)
    tela._cartoes_prontos(0, {PRETO_E_BRANCO: puro, ORIGINAL: puro, MELHORAR: puro})
    assert int(postas[-1].max()) == 7, "o filtro puro apagou o Misto no cartao"


def test_cartao_pb_sem_so_as_letras_continua_o_filtro_puro(conferir_original, monkeypatch):
    import numpy as np

    tela = conferir_original
    pedidos: list = []
    monkeypatch.setattr(tela.previas, "pegar_com_filtro",
                        lambda i, d, f: pedidos.append(f) or None)
    monkeypatch.setattr(tela.previas, "pegar",
                        lambda i, d: __import__("numpy").full((40, 30, 3), 128, "uint8"))
    postas = _espiar_o_cartao(tela)
    tela.atualizar()
    assert PRETO_E_BRANCO not in pedidos
    puro = np.full((40, 30, 3), 200, np.uint8)
    tela._cartoes_prontos(0, {PRETO_E_BRANCO: puro})
    assert postas[-1] is puro


def test_cartao_pb_com_a_pagina_ja_no_preto_e_branco_e_a_previa(conferir_original, monkeypatch):
    """No Preto e branco, o cartao dele e a propria previa (que ja passa pelo
    Misto): nada de desenhar a pagina duas vezes."""
    tela = conferir_original
    pedidos: list = []
    monkeypatch.setattr(tela.previas, "pegar_com_filtro",
                        lambda i, d, f: pedidos.append(f) or None)
    monkeypatch.setattr(tela.previas, "pegar",
                        lambda i, d: __import__("numpy").full((40, 30, 3), 128, "uint8"))
    tela.projeto.misto_so_as_letras = True
    tela.projeto.paginas[0].filtro = PRETO_E_BRANCO
    tela.atualizar()
    assert PRETO_E_BRANCO not in pedidos


def test_cartao_pb_do_misto_chega_de_uma_tarefa_de_fundo(conferir_original):
    """De ponta a ponta, com o GerenciadorPrevias de verdade: o pedido nao
    trava a tela (volta na hora, sem imagem) e a imagem chega pelo sinal;
    e e a mesma que core.pipeline.renderizar_com_filtro da com o Misto."""
    import time

    from core.pdf_io import abrir_pdf, limitar_altura
    from ui.tela_conferir import DPI_CARTAO_DO_MISTO

    tela = conferir_original
    projeto = tela.projeto
    projeto.misto_so_as_letras = True
    projeto.misto_fora_do_texto = misto.FORA_TUDO       # sem o leitor de texto
    postas = _espiar_o_cartao(tela)
    inicio = time.monotonic()
    tela.atualizar()
    assert time.monotonic() - inicio < 2.0
    assert _esperar(lambda: postas and postas[-1] is not None), "o cartao nao chegou"

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        esperado, _ = pipeline.renderizar_com_filtro(doc, projeto, projeto.paginas[0],
                                                     PRETO_E_BRANCO, dpi=DPI_CARTAO_DO_MISTO)
    finally:
        doc.close()
    import numpy as np

    assert np.array_equal(postas[-1], limitar_altura(esperado, 260))
    assert projeto.paginas[0].filtro == ORIGINAL, "o cartao nao pode mudar a pagina"


# --- 3. o bloco AJUSTE nao fica espremido ---------------------------------------
#
# Ressalva 1 do verificador (05/10, prints 10, 11 e 17; antigo, tambem no
# ace15b2): na aba Filtro de uma pagina Original, escolher o cartao "Preto e
# branco" fazia o bloco AJUSTE (com o "So as letras" e os tres botoes) virar
# uma faixa vazia e os botoes "Aplicar em" ficarem sem texto, ate trocar de
# aba. A barra de botoes tem a altura FIXA medida na troca de aba
# (_encolher_a_barra_de_botoes); o bloco aparece depois. O mesmo conserto do
# 50b9319 (aba Marcar): medir de novo quando os controles mudam.

def _nada_espremido(tela):
    from PySide6.QtWidgets import QPushButton

    from ui.tela_conferir import ABA_FILTRO

    painel = tela.linhas_de_botoes[ABA_FILTRO]
    assert tela.barra_botoes.height() >= painel.sizeHint().height(), \
        f"barra {tela.barra_botoes.height()} < {painel.sizeHint().height()}"
    botoes = [b for b in painel.findChildren(QPushButton) if b.isVisible()]
    assert botoes
    for botao in botoes:
        assert botao.height() >= botao.sizeHint().height(), \
            f"{botao.text()!r}: {botao.height()} de altura, precisa de {botao.sizeHint().height()}"


@pytest.mark.parametrize("tamanho", [(1280, 657), (1920, 1040)])
@pytest.mark.parametrize("so_as_letras", [False, True])
def test_escolher_preto_e_branco_numa_pagina_original_nao_espreme(
        conferir_original, tamanho, so_as_letras):
    from PySide6.QtWidgets import QApplication

    tela = conferir_original
    tela.projeto.misto_so_as_letras = so_as_letras
    tela.resize(*tamanho)
    tela.show()
    QApplication.processEvents()
    assert tela.bloco_ajuste.isHidden(), "no Original o bloco AJUSTE some"
    altura_sem = tela.barra_botoes.height()

    tela._escolher_filtro(PRETO_E_BRANCO)
    for _ in range(3):
        QApplication.processEvents()
    assert not tela.bloco_ajuste.isHidden()
    assert tela.barra_botoes.height() > altura_sem, "a barra nao cresceu com o bloco"
    _nada_espremido(tela)
    if so_as_letras:
        e = tela.escolhas_misto
        assert e.caixa.isChecked() and e.botoes[misto.FORA_REDE].isVisible()

    # e ao voltar para o Original, a barra encolhe de novo (a pagina ganha a
    # altura de volta)
    tela._escolher_filtro(ORIGINAL)
    QApplication.processEvents()
    assert tela.barra_botoes.height() < altura_sem + 1
    tela.hide()


def test_ligar_so_as_letras_na_pagina_nao_espreme(conferir_original):
    """Os tres botoes aparecem ao marcar "So as letras": a barra cresce."""
    from PySide6.QtWidgets import QApplication

    tela = conferir_original
    tela.projeto.paginas[0].filtro = PRETO_E_BRANCO
    tela.resize(1280, 657)
    tela.show()
    tela.atualizar()
    QApplication.processEvents()
    tela.escolhas_misto.caixa.setChecked(True)
    for _ in range(3):
        QApplication.processEvents()
    _nada_espremido(tela)
    tela.escolhas_misto.botao_mais.click()
    for _ in range(3):
        QApplication.processEvents()
    _nada_espremido(tela)
    tela.hide()


# --- 4. "So as letras" so com o Preto e branco; o resumo diz o que acontece -----
#
# Ressalvas 3 e 4 do verificador (05/10): na tela "O que fazer", "So as
# letras" aparecia mesmo com o Original escolhido, e o resumo dizia "deixar
# tudo em preto e branco" com ela marcada.

def _escolher_no_livro(tela, filtro):
    tela.radios_de_filtro[filtro].setChecked(True)
    tela._mudou()


def test_so_as_letras_so_aparece_com_o_preto_e_branco_no_livro(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = janela.tela_opcoes, janela.projeto
    e = tela.escolhas_misto
    _escolher_no_livro(tela, PRETO_E_BRANCO)
    assert not e.isHidden()
    e.caixa.setChecked(True)
    assert not tela.cx_decoracao_pb.isEnabled()
    for filtro in (ORIGINAL, MELHORAR, MAGICO_PRO):
        _escolher_no_livro(tela, filtro)
        assert e.isHidden(), f"'So as letras' a vista com {filtro}"
        # a caixinha das molduras volta a valer (o Misto nao vale fora do P&B)
        assert tela.cx_decoracao_pb.isEnabled()
        assert projeto.misto_so_as_letras is True, "esconder nao esquece a escolha"
    _escolher_no_livro(tela, PRETO_E_BRANCO)
    assert not e.isHidden() and e.caixa.isChecked() and not e.painel.isHidden()
    assert not tela.cx_decoracao_pb.isEnabled()


def test_o_resumo_da_tela_diz_o_que_o_so_as_letras_faz(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela = janela.tela_opcoes
    _escolher_no_livro(tela, PRETO_E_BRANCO)
    assert "deixar tudo em preto e branco" in tela.resumo.text()
    tela.escolhas_misto.caixa.setChecked(True)
    texto = tela.resumo.text()
    assert "deixar tudo em preto e branco" not in texto
    assert "só as letras em preto e branco" in texto
    assert "gravuras, fotos, molduras e iluminuras ficam como no original" in texto
    tela.escolhas_misto.caixa.setChecked(False)
    assert "deixar tudo em preto e branco" in tela.resumo.text()


def _resumo(**campos) -> str:
    projeto = Projeto(caminho_entrada="x.pdf", filtro_padrao=PRETO_E_BRANCO,
                      dividir_folhas=False, endireitar=False, cortar_bordas=False,
                      montar_cadernos=False, **campos)
    return pipeline.resumo_em_portugues(projeto, 10)


def test_resumo_em_portugues_com_so_as_letras():
    sem = _resumo()
    assert sem == "Vou deixar tudo em preto e branco e separar as gravuras do texto."
    a = _resumo(misto_so_as_letras=True)
    assert a == ("Vou deixar só as letras em preto e branco (gravuras, fotos, molduras "
                 "e iluminuras ficam como no original; fora do texto, só fica a tinta "
                 "escura).")
    b = _resumo(misto_so_as_letras=True, misto_fora_do_texto=misto.FORA_TUDO)
    assert b.startswith("Vou deixar tudo em preto e branco menos gravuras, fotos")
    c = _resumo(misto_so_as_letras=True, misto_fora_do_texto=misto.FORA_APAGAR)
    assert "só o texto que eu achar" in c and "o resto vai a branco" in c
    sem_gravuras = _resumo(misto_so_as_letras=True, gravura_forma="desligada")
    assert "as gravuras que você marcar à mão ficam como no original" in sem_gravuras
    assert "não procurar gravuras e fotos" in sem_gravuras
    for frase in (a, b, c, sem_gravuras):
        for jargao in ("ocr", "misto", "máscara", "binari", "docTR"):
            assert jargao not in frase.lower(), jargao


def test_resumo_fora_do_preto_e_branco_nao_fala_das_letras():
    projeto = Projeto(caminho_entrada="x.pdf", filtro_padrao=MELHORAR,
                      misto_so_as_letras=True, dividir_folhas=False, endireitar=False,
                      cortar_bordas=False, montar_cadernos=False)
    assert pipeline.resumo_em_portugues(projeto, 10) == (
        "Vou deixar tudo em melhorar e separar as gravuras do texto.")
