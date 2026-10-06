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
