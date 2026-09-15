"""Os cartões de filtro não podem esperar a fila de prévias.

Achado ao vivo em 12/09/2026 (sessão de retomada, livro Boécio): navegar
rápido pelas páginas enche a fila de prévias, e como os cartões usavam o
MESMO pool de threads, um cartão podia ficar "preparando..." por muito mais
tempo do que o razoável - travamento percebido, mesmo sem exceção nenhuma no
log. Reproduzido com `py-spy` (zero threads ativas, cartão parado havia mais
de 70 segundos) e confirmado pelo Samuel ("testei e ainda trava").
"""

from __future__ import annotations

import time

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def livro(tmp_path):
    caminho = tmp_path / "livro.pdf"
    doc = fitz.open()
    for i in range(8):
        pagina = doc.new_page(width=400, height=560)
        pagina.insert_text((40, 60), f"folha {i}", fontsize=14)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _projeto(caminho, paginas: int = 8) -> Projeto:
    p = Projeto(caminho_entrada=str(caminho), nome=caminho.stem)
    p.folhas = [ConfigFolha(indice=i) for i in range(paginas)]
    p.paginas = [ConfigPagina(indice=i, folha=i) for i in range(paginas)]
    return p


def _bombear_ate(condicao, segundos: float) -> bool:
    """Processa eventos até a condição virar verdadeira ou o tempo acabar."""
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        QCoreApplication.processEvents()
        if condicao():
            return True
        time.sleep(0.01)
    return condicao()


def test_tarefa_que_termina_depois_do_dono_morrer_nao_quebra(app, livro):
    """Se a tela fecha (ou troca de livro) enquanto uma prévia ainda está
    calculando, a tarefa não pode explodir quando tenta avisar - o objeto que
    receberia o aviso já foi destruído.

    Achado no log de produção em 08/09/2026: 8+ ocorrências de
    'RuntimeError: Signal source has been deleted' em ui/tarefas.py:178,
    sempre na mesma linha (o emit do sinal 'pronta').
    """
    import shiboken6

    from ui.tarefas import _SinaisPrevia, _TarefaPrevia
    from modelos import ConfigFolha, ConfigPagina, Projeto as _Projeto

    projeto = _Projeto(caminho_entrada=str(livro), nome="x")
    projeto.folhas = [ConfigFolha(indice=0)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0)]

    sinais = _SinaisPrevia()
    tarefa = _TarefaPrevia("0:150", str(livro), projeto, 0, 150, sinais)

    # simula a tela sendo destruida ANTES da tarefa terminar
    shiboken6.delete(sinais)

    tarefa.run()  # nao pode levantar excecao aqui


def test_cartao_nao_espera_a_fila_de_previas_lenta(app, monkeypatch, tmp_path, livro):
    """Enche a fila de prévias (lenta de propósito) e pede os cartões: eles
    têm que responder rápido mesmo assim, porque não competem pelo mesmo pool.
    """
    from ui import tarefas as mod_tarefas

    def _abrir_lento(_caminho):
        time.sleep(0.4)
        return fitz.open(str(livro))

    def _renderizar_lento(doc, projeto, pagina, dpi):
        time.sleep(0.4)
        return np.zeros((100, 80, 3), dtype=np.uint8), 1.0

    monkeypatch.setattr(mod_tarefas, "abrir_pdf", _abrir_lento)
    monkeypatch.setattr(mod_tarefas, "renderizar_pagina", _renderizar_lento)

    projeto = _projeto(livro)
    previas = mod_tarefas.GerenciadorPrevias(str(livro), projeto, None)

    # enche o pool de prévias com bem mais pedidos do que threads disponíveis
    for indice in range(8):
        previas.pedir(indice, 150)

    chegou = {}

    def _guardar_cartoes(indice, resultados):
        chegou["indice"] = indice
        chegou["resultados"] = resultados

    previas.cartoes_prontos.connect(_guardar_cartoes)

    base = np.full((100, 80, 3), 200, dtype=np.uint8)
    inicio = time.monotonic()
    previas.pedir_cartoes(0, base, ["preto_e_branco", "melhorar"], 50, 50, 50)

    _bombear_ate(lambda: "resultados" in chegou, segundos=1.5)
    duracao = time.monotonic() - inicio

    previas.parar()

    assert "resultados" in chegou, "o cartão nunca respondeu"
    assert duracao < 1.2, (
        f"o cartão esperou {duracao:.2f}s atrás da fila de prévias - "
        "eles não podem competir pelo mesmo pool"
    )
