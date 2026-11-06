"""Prova de comportamento da D-591: o aviso de falta de memória ao processar.

D-591 (31/10/2026, Central, quadro 2-12, "Este livro ficou grande demais para
a memória do computador": o que o aviso deve dizer e fazer?). O Samuel
escolheu "Frase certa + botão "tentar de novo" (recomendo)":

    "Faltou memória no computador: outros programas abertos estão usando quase
    toda a memória. Feche o que não estiver usando. Nada do seu trabalho no
    livro se perdeu." com "tentar de novo" (processa de novo, com o mesmo nome
    e lugar) e "entendi".

O que se cobra (CLAUDE.md §11.4: a prova confere também que o antigo saiu):

    - a frase é exatamente a escolhida, para MemoryError e para as faltas de
      memória que chegam de outro jeito (numpy, OpenCV, MuPDF);
    - a frase antiga ("grande demais", "qualidade normal") não aparece mais;
    - outros erros continuam com o aviso de sempre, sem "tentar de novo";
    - na janela de verdade (processamento em QThread): faltou memória no meio
      -> o aviso com "tentar de novo" e "entendi"; "tentar de novo" processa
      de novo para o MESMO arquivo, sem perguntar o destino de novo, e chega a
      "Ficou pronto!"; "entendi" fica na área de trabalho e não processa;
    - nos dois casos o trabalho no livro fica como estava, e o PDF antigo de
      mesmo nome nunca some por causa da falha (bug de 05/10/2026).
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from core import pipeline  # noqa: E402
from core.pdf_io import ErroPDF  # noqa: E402
from tests.test_ja_existe_arquivo_com_esse_nome import (  # noqa: E402
    _esperar_o_fim,
    _livro_conferido,
    _paginas,
    _pdf_antigo,
)
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    app,
    janela,
    pasta,
)

FRASE = ("Faltou memória no computador: outros programas abertos estão usando quase "
         "toda a memória. Feche o que não estiver usando. Nada do seu trabalho no "
         "livro se perdeu.")


# --- a frase ------------------------------------------------------------------------

def _erros_de_memoria() -> list[BaseException]:
    import cv2
    import numpy as np

    erros: list[BaseException] = [MemoryError(), MemoryError("de mentira")]
    try:                                     # a do numpy (filha de MemoryError)
        np.empty((1 << 62,), np.uint8)
    except MemoryError as erro:
        erros.append(erro)
    erros.append(cv2.error("OpenCV(4.12.0) (-4:Insufficient memory) Failed to allocate 3611738 bytes"))
    erros.append(RuntimeError("code=2: malloc (27648000 bytes) failed"))
    try:                                     # embrulhada noutra ("raise ... from")
        try:
            raise MemoryError()
        except MemoryError as dentro:
            raise ErroPDF("Não consegui gravar o arquivo final.") from dentro
    except ErroPDF as erro:
        erros.append(erro)
    return erros


@pytest.mark.parametrize("erro", _erros_de_memoria(), ids=lambda e: type(e).__name__)
def test_d591_a_frase_e_a_escolhida(erro):
    from ui.tarefas import _mensagem_amigavel, faltou_memoria

    assert faltou_memoria(erro)
    assert _mensagem_amigavel(erro) == FRASE


def test_d591_a_frase_antiga_saiu():
    from ui.tarefas import FRASE_FALTOU_MEMORIA, _mensagem_amigavel

    assert FRASE_FALTOU_MEMORIA == FRASE
    texto = _mensagem_amigavel(MemoryError())
    assert "grande demais" not in texto and "qualidade normal" not in texto


@pytest.mark.parametrize("erro", [ValueError("x"), PermissionError("x"), OSError("disco"),
                                  ErroPDF("Esse PDF está protegido por senha. Não consigo abrir.")],
                         ids=lambda e: type(e).__name__)
def test_d591_outros_erros_continuam_como_sempre(erro):
    from ui.tarefas import _mensagem_amigavel, faltou_memoria

    assert not faltou_memoria(erro)
    assert _mensagem_amigavel(erro) != FRASE


def test_d591_a_tarefa_de_processar_diz_que_faltou_memoria(monkeypatch):
    """A TarefaProcessar anota a falta de memória ANTES de avisar a janela."""
    import ui.tarefas as tarefas
    from modelos import Projeto

    for erro, faltou in ((MemoryError(), True), (ValueError("outro"), False)):
        def processar(*_a, erro=erro, **_k):
            raise erro

        monkeypatch.setattr(tarefas, "processar", processar)
        tarefa = tarefas.TarefaProcessar(Projeto(caminho_entrada="x.pdf", nome="x"))
        vistas = []
        tarefa.falhou.connect(lambda mensagem, t=tarefa: vistas.append((mensagem, t.faltou_memoria)))
        tarefa.run()
        assert vistas and vistas[0][1] is faltou
        assert (vistas[0][0] == FRASE) is faltou


# --- na janela de verdade --------------------------------------------------------------

TITULO = "Um momento"


def _responder_o_aviso(monkeypatch, botao: str, vistas: list) -> None:
    """Responde a caixa "Um momento" clicando `botao`, e anota o texto e os
    botões dela."""
    exec_de_antes = QMessageBox.exec

    def _clicar(caixa) -> None:
        vistas.append((caixa.text(), [b.text() for b in caixa.buttons()]))
        next(b for b in caixa.buttons() if b.text() == botao).click()

    def _exec(caixa):
        if caixa.windowTitle() == TITULO:
            QTimer.singleShot(0, lambda: _clicar(caixa))
        return exec_de_antes(caixa)

    monkeypatch.setattr(QMessageBox, "exec", _exec)


def _falta_memoria_uma_vez(monkeypatch) -> None:
    """A terceira página da PRIMEIRA vez falha por falta de memória (como no
    Rhetorica); da segunda vez em diante, tudo passa."""
    original = pipeline.compor_na_folha
    vezes = {"n": 0}

    def compor(*a, **k):
        vezes["n"] += 1
        if vezes["n"] == 3:
            raise MemoryError("de mentira")
        return original(*a, **k)

    monkeypatch.setattr(pipeline, "compor_na_folha", compor)


def _destino_contado(monkeypatch, caminho: Path) -> list:
    """A janela "Antes de processar" devolve `caminho`; a lista conta quantas
    vezes ela foi aberta."""
    import ui.janela_confirmar as confirmar

    vezes: list = []

    def pedir(*_a, **_k):
        vezes.append(1)
        return caminho

    monkeypatch.setattr(confirmar, "pedir_confirmacao", pedir)
    return vezes


def _esperar_voltar_para_conferir(janela, vistas: list, segundos: float = 180) -> None:
    from ui.janela_principal import CONFERIR

    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        QApplication.processEvents()
        if janela.telas.currentIndex() == CONFERIR and vistas and not janela.tarefa.isRunning():
            return
        time.sleep(0.02)
    pytest.fail("o aviso de falta de memória não apareceu")


def _retrato_do_trabalho(janela) -> list:
    return [(p.indice, p.filtro, p.apagada, p.recorte) for p in janela.projeto.paginas]


def test_d591_tentar_de_novo_processa_para_o_mesmo_arquivo(janela, pasta, monkeypatch):
    from ui.janela_principal import FINAL

    _livro_conferido(janela, pasta)
    saida = pasta / "saida" / "pronto.pdf"
    vezes_do_destino = _destino_contado(monkeypatch, saida)
    vistas: list = []
    _responder_o_aviso(monkeypatch, "tentar de novo", vistas)
    _falta_memoria_uma_vez(monkeypatch)
    trabalho = _retrato_do_trabalho(janela)

    janela.processar()
    _esperar_o_fim(janela)

    assert vistas == [(FRASE, ["tentar de novo", "entendi"])], vistas
    assert not janela.avisos, janela.avisos
    assert janela.telas.currentIndex() == FINAL
    assert len(vezes_do_destino) == 1, "o tentar de novo perguntou o destino outra vez"
    assert Path(janela.projeto.caminho_saida) == saida
    assert _paginas(saida) == 4
    assert _retrato_do_trabalho(janela) == trabalho
    assert sorted(p.name for p in saida.parent.iterdir()) == ["pronto.pdf"]


def test_d591_entendi_fica_no_livro_e_o_antigo_fica_inteiro(janela, pasta, monkeypatch):
    from ui.janela_principal import CONFERIR

    _livro_conferido(janela, pasta)
    saida = pasta / "saida" / "pronto.pdf"
    bytes_do_antigo = _pdf_antigo(saida, "o antigo")
    _destino_contado(monkeypatch, saida)
    # "Já existe um arquivo com esse nome" -> "substituir o antigo"
    from tests.test_ja_existe_arquivo_com_esse_nome import _escolher_na_caixa

    _escolher_na_caixa(monkeypatch, "substituir o antigo", [])
    vistas: list = []
    _responder_o_aviso(monkeypatch, "entendi", vistas)
    _falta_memoria_uma_vez(monkeypatch)
    trabalho = _retrato_do_trabalho(janela)

    janela.processar()
    _esperar_voltar_para_conferir(janela, vistas)
    for _ in range(20):                      # nada mais pode começar depois
        QApplication.processEvents()
        time.sleep(0.02)

    assert vistas == [(FRASE, ["tentar de novo", "entendi"])], vistas
    assert janela.telas.currentIndex() == CONFERIR
    assert not janela.tarefa.isRunning()
    assert saida.read_bytes() == bytes_do_antigo, "o PDF antigo mudou ou sumiu"
    assert sorted(p.name for p in saida.parent.iterdir()) == ["pronto.pdf"]
    assert _retrato_do_trabalho(janela) == trabalho


def test_d591_outro_erro_ao_processar_continua_so_com_entendi(janela, pasta, monkeypatch):
    """Erro que não é de memória: o aviso de sempre (janela.avisar), sem
    "tentar de novo"."""
    _livro_conferido(janela, pasta)
    saida = pasta / "saida" / "pronto.pdf"
    _destino_contado(monkeypatch, saida)
    vistas: list = []
    _responder_o_aviso(monkeypatch, "tentar de novo", vistas)

    def quebra(*_a, **_k):
        raise ValueError("outro erro")

    monkeypatch.setattr(pipeline, "compor_na_folha", quebra)
    janela.processar()
    fim = time.monotonic() + 120
    while time.monotonic() < fim and not janela.avisos:
        QApplication.processEvents()
        time.sleep(0.02)
    assert janela.avisos and janela.avisos[0] != FRASE
    assert vistas == []
