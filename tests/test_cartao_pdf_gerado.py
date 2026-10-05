"""O cartao do livro na tela inicial mostra "pronto, PDF gerado" depois de gerar.

Bug da Lista de bugs do plano (02/10/2026, achado na janela real; o Samuel
autorizou consertar em 05/10): o cartao nunca mostrava "pronto, PDF gerado"
nem o botao "abrir a pasta". O campo `pdf_gerado` do resumo do projeto
(projetos.Resumo, lido em ui/tela_inicio.py) nunca virava verdadeiro: so o
"comecar de novo" (JanelaPrincipal._recomecar_projeto) o punha em falso.

O que se cobra aqui, com o processamento DE VERDADE (TarefaProcessar em
QThread) e a pasta de dados do teste:

    - PDF gravado com sucesso: o resumo em disco fica com pdf_gerado e o
      caminho do PDF, e o cartao mostra "pronto, PDF gerado" e "abrir a pasta";
    - processamento cancelado: nao conta (o cartao segue "X de Y conferidas",
      com "continuar");
    - processamento com erro: nao conta;
    - livro ja gerado que e processado de novo e da erro: deixa de contar (o
      destino estava sendo regravado; o cartao nao promete um PDF que pode
      nao estar la). Ver JanelaPrincipal.processar.

Nada aparece na tela (tests/conftest.py).
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

import projetos  # noqa: E402
from tests.test_ja_existe_arquivo_com_esse_nome import (  # noqa: E402
    _destino_ja_escolhido,
    _esperar_o_fim,
    _livro_conferido,
)
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    app,
    janela,
    pasta,
)
from tests.test_tela_inicio import _todos_os_textos  # noqa: E402


def _resumo_em_disco(janela) -> projetos.Resumo:
    resumo = projetos.ler_resumo(janela.resumo.pasta)
    assert resumo is not None
    return resumo


def _textos_do_cartao(janela, resumo) -> list[str]:
    from ui.tela_inicio import CartaoDeProjeto

    cartao = CartaoDeProjeto(resumo, janela.tela_inicio)
    try:
        return _todos_os_textos(cartao)
    finally:
        cartao.close()


def _esperar_voltar_para_conferir(janela, segundos: float = 60) -> None:
    from ui.janela_principal import CONFERIR, PROGRESSO

    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        QApplication.processEvents()
        tarefa = janela.tarefa
        if (janela.telas.currentIndex() == CONFERIR
                and (tarefa is None or not tarefa.isRunning())):
            QApplication.processEvents()
            return
        time.sleep(0.02)
    pytest.fail(f"nao voltou para Conferir (tela {janela.telas.currentIndex()}, "
                f"PROGRESSO={PROGRESSO})")


def _processamento_que(monkeypatch, erro: Exception) -> None:
    """O processamento (core.pipeline.processar, como a TarefaProcessar o
    chama) termina com `erro` - Cancelou para o "cancelar", outro para erro."""
    import ui.tarefas as tarefas

    def _processar(*_a, **_k):
        raise erro

    monkeypatch.setattr(tarefas, "processar", _processar)


def test_pdf_gravado_marca_o_cartao_como_pronto(janela, pasta, monkeypatch):
    _livro_conferido(janela, pasta)
    pronto = pasta / "saida" / "pronto.pdf"
    _destino_ja_escolhido(monkeypatch, pronto)
    assert not _resumo_em_disco(janela).pdf_gerado

    janela.processar()
    _esperar_o_fim(janela)

    resumo = _resumo_em_disco(janela)
    assert resumo.pdf_gerado, "o resumo nao anotou que o PDF foi gerado"
    assert Path(resumo.caminho_saida) == pronto
    textos = _textos_do_cartao(janela, resumo)
    assert any("pronto, PDF gerado" in t for t in textos), textos
    assert any("abrir a pasta" in t for t in textos), textos


def test_cancelar_nao_marca_o_pdf_como_gerado(janela, pasta, monkeypatch):
    from core.pipeline import Cancelou

    _livro_conferido(janela, pasta)
    _destino_ja_escolhido(monkeypatch, pasta / "saida" / "pronto.pdf")
    _processamento_que(monkeypatch, Cancelou())

    janela.processar()
    _esperar_voltar_para_conferir(janela)

    resumo = _resumo_em_disco(janela)
    assert not resumo.pdf_gerado
    textos = _textos_do_cartao(janela, resumo)
    assert not any("PDF gerado" in t for t in textos), textos
    assert any("continuar" in t for t in textos), textos


def test_erro_nao_marca_o_pdf_como_gerado(janela, pasta, monkeypatch):
    from core.pdf_io import ErroPDF

    _livro_conferido(janela, pasta)
    _destino_ja_escolhido(monkeypatch, pasta / "saida" / "pronto.pdf")
    _processamento_que(monkeypatch, ErroPDF("disco cheio, de mentira"))

    janela.processar()
    _esperar_voltar_para_conferir(janela)

    assert janela.avisos, "o erro nao foi avisado"
    assert not _resumo_em_disco(janela).pdf_gerado


def test_gerar_de_novo_com_erro_deixa_de_contar(janela, pasta, monkeypatch):
    from core.pdf_io import ErroPDF

    _livro_conferido(janela, pasta)
    pronto = pasta / "saida" / "pronto.pdf"
    _destino_ja_escolhido(monkeypatch, pasta / "saida" / "outro.pdf")
    janela.processar()
    _esperar_o_fim(janela)
    assert _resumo_em_disco(janela).pdf_gerado

    # de novo, para outro nome, e da erro
    _destino_ja_escolhido(monkeypatch, pronto)
    _processamento_que(monkeypatch, ErroPDF("pendrive tirado, de mentira"))
    janela.processar()
    _esperar_voltar_para_conferir(janela)

    resumo = _resumo_em_disco(janela)
    assert not resumo.pdf_gerado, \
        "o cartao continua dizendo 'PDF gerado' para um PDF que nao foi gravado"
