"""Um livro tirado da lista nunca volta para a lista (R-B do verificador-3,
06/10/2026).

O defeito: "Tirar da lista" o livro que esta aberto (a pessoa volta a tela
inicial e tira o cartao dele) e depois FECHAR o programa recriava a pasta do
projeto, e o cartao voltava na proxima abertura. Com a conversao das zonas
rodando, a pasta voltava sozinha quando ela terminava (Siebmacher: 69,6 s
depois). A janela continuava com o livro tirado em self.resumo, e o fechar
(closeEvent -> _salvar_agora), o relogio de salvar (_salvar_por_tras, que a
conversao chama ao terminar) e o parar da conversao ao trocar de livro
gravavam de novo - e a gravacao fazia mkdir da pasta.

O conserto tem duas camadas:
  - a janela solta o livro no momento do "Tirar da lista" (TelaInicio emite
    vai_tirar_da_lista ANTES de apagar; a janela para o relogio e a conversao
    das zonas, sem gravar, e fica sem livro aberto);
  - o gravador (projetos) nao grava numa pasta de projeto que nao existe
    mais, e nunca a recria.

Um teste por caminho (cada um falhava antes do conserto): fechar, relogio,
conversao terminando, gravacao na fila, trocar de livro; e o caso que ja
estava anotado (conversao termina com a pessoa na tela inicial e ela tira o
projeto da lista dentro de 0,6 s).

Pasta de dados propria em saida_teste\\ (fixtures de
tests/test_mesmo_livro_outro_caminho.py, com LOCALAPPDATA apontando para
ela): nada na pasta de dados real - nem as copias guardadas pelo "Tirar da
lista".
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

import projetos  # noqa: E402
from core import pipeline  # noqa: E402
from tests.test_converter_zonas_ao_abrir import (  # noqa: E402
    _abrir_projeto_antigo,
    _gravar_pdf,
)
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    app,
    janela,
    pasta,
)
from tests.test_trocar_de_livro_grava import (  # noqa: E402
    _abrir_e_conferir,
    _livro,
    _mudar_sem_esperar_o_relogio,
)
from ui.janela_principal import INICIO  # noqa: E402


@pytest.fixture
def sim_na_pergunta(monkeypatch):
    """A pergunta "Tirar da lista?" respondida com "Tirar da lista" (a caixa
    de verdade pararia o teste)."""
    from ui import perguntas

    monkeypatch.setattr(perguntas, "perguntar", lambda *a, **k: True)


def _tirar_da_lista(janela, resumo: projetos.Resumo) -> None:
    """O que o Kaique faz: tela inicial, clique direito no cartao, "remover
    da lista", "Tirar da lista" - pelo caminho de verdade da TelaInicio."""
    janela.telas.setCurrentIndex(INICIO)
    janela.tela_inicio.pedir_para_remover(projetos.ler_resumo(resumo.pasta))
    assert not Path(resumo.pasta).exists(), "o Tirar da lista nao apagou a pasta"


def _rodar_eventos(segundos: float = 1.2) -> None:
    """Deixa o laco de eventos andar (o relogio de salvar dispara em 0,6 s) e
    espera o fio de gravar esvaziar."""
    fim = time.perf_counter() + segundos
    while time.perf_counter() < fim:
        QApplication.processEvents()
        time.sleep(0.01)
    projetos.esperar_gravacoes(30)


def _esperar(condicao, limite_s: float = 60.0) -> None:
    fim = time.perf_counter() + limite_s
    while not condicao() and time.perf_counter() < fim:
        QApplication.processEvents()
        time.sleep(0.005)
    assert condicao(), "o teste esperou demais"


def _nao_voltou(pasta_do_projeto: str) -> None:
    assert not Path(pasta_do_projeto).exists(), "a pasta do projeto tirado da lista voltou"
    assert all(not projetos.mesmo_arquivo(r.pasta, pasta_do_projeto)
               for r in projetos.listar()), "o cartao voltou para a lista"


# --- o livro de teste com zonas no formato antigo (a conversao roda) -------

@pytest.fixture
def livro_antigo(pasta, monkeypatch):
    """Um PDF com zonas no formato antigo: abri-lo pela janela liga a
    conversao das zonas por tras. As previas devolvem uma folha branca sem
    desenhar (como em tests/test_converter_zonas_ao_abrir.py), para so a
    tarefa de fundo converter."""
    from ui import tarefas

    monkeypatch.setattr(tarefas, "renderizar_pagina",
                        lambda doc, projeto, pagina, dpi=0: (np.full((90, 64, 3), 255, np.uint8), False))
    (pasta / "livros").mkdir(exist_ok=True)
    caminho = pasta / "livros" / "antigo.pdf"
    _gravar_pdf(caminho)
    pipeline._GEOMETRIAS.clear()
    return caminho


@pytest.fixture
def conversao_devagar(monkeypatch):
    """Cada folha da conversao demora 0,3 s a mais: da tempo de tirar o
    livro da lista com ela no meio."""
    original = pipeline._guardar_geometria

    def devagar(*args, **kwargs):
        time.sleep(0.3)
        return original(*args, **kwargs)

    monkeypatch.setattr(pipeline, "_guardar_geometria", devagar)


# --- os caminhos -----------------------------------------------------------

def test_tirar_o_livro_aberto_e_fechar_o_programa_nao_traz_de_volta(janela, pasta,
                                                                    sim_na_pergunta):
    """O caso do verificador-3: tirar o livro aberto da lista e fechar."""
    resumo = _abrir_e_conferir(janela, _livro(pasta, "Primeiro"))
    janela._sair_da_conferencia()
    _tirar_da_lista(janela, resumo)
    janela.close()
    projetos.esperar_gravacoes(30)
    _nao_voltou(resumo.pasta)


def test_a_janela_solta_o_livro_tirado_da_lista(janela, pasta, sim_na_pergunta):
    """A janela fica sem livro aberto (como no "comecar de novo" do proprio
    livro), e o relogio de salvar para."""
    resumo = _abrir_e_conferir(janela, _livro(pasta, "Primeiro"))
    _mudar_sem_esperar_o_relogio(janela)
    _tirar_da_lista(janela, resumo)
    assert janela.resumo is None
    assert not janela.trabalho_carregado
    assert not janela._relogio_de_salvar.isActive()


def test_tirar_OUTRO_livro_nao_solta_o_aberto(janela, pasta, sim_na_pergunta):
    """Tirar da lista um livro que NAO esta aberto nao mexe no aberto: a
    mudanca dele continua indo para o disco."""
    outro = _abrir_e_conferir(janela, _livro(pasta, "Outro"))
    aberto = _abrir_e_conferir(janela, _livro(pasta, "Aberto"))
    _mudar_sem_esperar_o_relogio(janela)
    janela.tela_inicio.pedir_para_remover(projetos.ler_resumo(outro.pasta))
    assert not Path(outro.pasta).exists()
    assert janela.resumo is not None and janela.resumo.pasta == aberto.pasta
    assert janela._relogio_de_salvar.isActive()
    _rodar_eventos()
    from tests.test_trocar_de_livro_grava import _filtro_no_disco
    from core.filtros import MAGICO_PRO

    assert _filtro_no_disco(aberto) == MAGICO_PRO
    _nao_voltou(outro.pasta)


def test_tirar_com_o_relogio_contando_nao_traz_de_volta(janela, pasta, sim_na_pergunta):
    """O relogio de salvar ainda contando (mudanca de menos de 0,6 s, ou a
    conversao que acabou de terminar) quando o livro sai da lista: quando ele
    dispara, nao pode recriar a pasta."""
    resumo = _abrir_e_conferir(janela, _livro(pasta, "Primeiro"))
    _mudar_sem_esperar_o_relogio(janela)
    _tirar_da_lista(janela, resumo)
    _rodar_eventos()
    _nao_voltou(resumo.pasta)
    janela.close()
    _nao_voltou(resumo.pasta)


def test_tirar_com_a_conversao_rodando_nao_traz_de_volta_quando_ela_termina(
        janela, pasta, livro_antigo, conversao_devagar, sim_na_pergunta):
    """O caso do Siebmacher: tirar da lista com a conversao das zonas no meio.
    A conversao para (sem gravar), e nada recria a pasta - nem o fim dela,
    nem o relogio, nem o fechar."""
    _abrir_projeto_antigo(janela, livro_antigo)
    resumo = janela.resumo
    tarefa = janela.conversao_das_zonas
    assert tarefa is not None, "a conversao nao comecou"
    _esperar(lambda: tarefa.feitas >= 1, limite_s=30)
    janela._sair_da_conferencia()
    _tirar_da_lista(janela, resumo)
    _esperar(lambda: not tarefa.isRunning(), limite_s=30)
    _rodar_eventos()
    _nao_voltou(resumo.pasta)
    janela.close()
    _nao_voltou(resumo.pasta)
    # e a conversao do livro tirado parou ali, sem ir ate o fim
    assert tarefa.foi_cancelada, "a conversao do livro tirado nao parou"


def test_conversao_termina_na_tela_inicial_e_tirar_logo_depois(
        janela, pasta, livro_antigo, sim_na_pergunta):
    """O caso que ja estava anotado na Lista de bugs (06/10): a conversao
    termina com a pessoa na tela inicial (o relogio de salvar comeca a
    contar), e ela tira o projeto da lista dentro de 0,6 s."""
    _abrir_projeto_antigo(janela, livro_antigo)
    resumo = janela.resumo
    tarefa = janela.conversao_das_zonas
    assert tarefa is not None, "a conversao nao comecou"
    janela._sair_da_conferencia()
    janela.telas.setCurrentIndex(INICIO)
    _esperar(lambda: janela.conversao_das_zonas is None and not tarefa.isRunning())
    assert janela._relogio_de_salvar.isActive(), "o fim da conversao nao ligou o relogio"
    _tirar_da_lista(janela, resumo)
    _rodar_eventos()
    _nao_voltou(resumo.pasta)
    janela.close()
    _nao_voltou(resumo.pasta)


def test_tirar_com_a_conversao_rodando_e_abrir_outro_livro(
        janela, pasta, livro_antigo, conversao_devagar, sim_na_pergunta):
    """Trocar de livro depois de tirar da lista o que estava convertendo: o
    abrir_livro para a conversao do livro de antes gravando o que ela fez -
    mas nao a do livro tirado."""
    _abrir_projeto_antigo(janela, livro_antigo)
    resumo = janela.resumo
    tarefa = janela.conversao_das_zonas
    assert tarefa is not None, "a conversao nao comecou"
    _esperar(lambda: tarefa.feitas >= 1, limite_s=30)
    janela._sair_da_conferencia()
    _tirar_da_lista(janela, resumo)
    janela.abrir_livro(str(_livro(pasta, "Segundo")))
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    _esperar(lambda: not tarefa.isRunning(), limite_s=30)
    _rodar_eventos()
    _nao_voltou(resumo.pasta)
    assert [r.nome for r in projetos.listar()] == ["Segundo"]


# --- o gravador: nunca recria a pasta de um projeto -------------------------

def _projeto_gravado(pasta) -> tuple[projetos.Resumo, object]:
    from modelos import Projeto

    livro = _livro(pasta, "Gravado")
    projeto = Projeto(caminho_entrada=str(livro), nome="Gravado")
    resumo = projetos.criar(projeto, 4)
    projetos.salvar_estado(resumo, projeto)
    return resumo, projeto


def test_gravacao_na_fila_nao_recria_a_pasta_apagada(pasta):
    """Uma gravacao por tras que chega ao fio de gravar depois de a pasta ir
    embora (o relogio de salvar, a conversao terminando) nao a recria."""
    resumo, projeto = _projeto_gravado(pasta)
    projetos.remover_da_lista(resumo)
    assert not Path(resumo.pasta).exists()
    projetos.salvar_estado_por_tras(resumo, projeto)
    projetos.atualizar(resumo, projeto, pagina_atual=2, por_tras=True)
    projetos.esperar_gravacoes(30)
    _nao_voltou(resumo.pasta)


def test_gravacao_na_hora_nao_recria_a_pasta_apagada(pasta):
    """Nem a gravacao na hora (fechar, trocar de livro, processar)."""
    resumo, projeto = _projeto_gravado(pasta)
    projetos.remover_da_lista(resumo)
    projetos.salvar_estado(resumo, projeto)
    projetos.atualizar(resumo, projeto, pagina_atual=2)
    projetos.gravar_resumo(resumo)
    _nao_voltou(resumo.pasta)


def test_gravacao_normal_continua_gravando(pasta):
    """Com a pasta no lugar, tudo grava como antes."""
    resumo, projeto = _projeto_gravado(pasta)
    projeto.nome = "Mudado"
    projetos.salvar_estado_por_tras(resumo, projeto)
    projetos.atualizar(resumo, projeto, pagina_atual=3, por_tras=True)
    projetos.esperar_gravacoes(30)
    assert projetos.carregar_estado(resumo).nome == "Mudado"
    assert projetos.ler_resumo(resumo.pasta).pagina_atual == 3
