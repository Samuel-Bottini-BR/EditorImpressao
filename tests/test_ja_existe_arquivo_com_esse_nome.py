"""A caixa "Ja existe um arquivo com esse nome" nao pode perder o PDF.

Bug da Lista de bugs do plano (02/10/2026), confirmado pela gerente no
codigo: na caixa que aparece quando o PDF de saida ja existe, o botao
"salvar como ... (2).pdf" chamava `self.tela_conferir.destino.definir(...)`,
mas a tela Conferir nao tem mais o seletor de destino (ele mudou para a
janela "Antes de processar", ui/janela_confirmar.py). Resultado: "Aconteceu
um problema inesperado" e o PDF NAO era gerado - o Kaique perdia o PDF.

O que se cobra aqui (teste de maquina), com o processamento DE VERDADE (a
TarefaProcessar em QThread, nao uma de mentira):

    - "salvar como (2)": gera `nome (2).pdf` com todas as paginas, e o arquivo
      antigo fica intacto, byte a byte;
    - se o `(2)` tambem ja existe, o nome oferecido e gerado e o `(3)` (o
      comportamento de escolher o proximo nome livre continua);
    - "substituir o antigo": grava por cima do antigo, no mesmo nome;
    - "cancelar": nada e processado e nada no disco muda.

A janela "Antes de processar" e trocada por uma resposta fixa (o caminho que
ja existe), e a caixa "Ja existe..." e respondida clicando o botao pelo
texto, como o Kaique clicaria - nada aparece na tela (tests/conftest.py).
Pasta de dados propria em saida_teste\\ (fixtures de
tests/test_mesmo_livro_outro_caminho.py), apagada no fim.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _pdf,
    app,
    janela,
    pasta,
)

TITULO_DA_CAIXA = "Já existe um arquivo com esse nome"


def _pdf_antigo(caminho: Path, texto: str) -> bytes:
    """Um PDF de uma pagina so, que faz o papel do que ja estava na pasta."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    doc.new_page().insert_text((40, 60), texto)
    doc.save(str(caminho))
    doc.close()
    return caminho.read_bytes()


def _livro_conferido(janela, pasta: Path) -> None:
    janela.abrir_livro(str(_pdf(pasta)))
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    _analisar(janela)
    assert len(janela.projeto.paginas) == 4


def _escolher_na_caixa(monkeypatch, comeco_do_botao: str, vistas: list) -> None:
    """Responde a caixa "Ja existe..." clicando o botao cujo texto comeca com
    `comeco_do_botao`. As outras caixas nao sao tocadas (o vigia do conftest
    reprova o teste se alguma ficar sem resposta)."""
    exec_de_antes = QMessageBox.exec

    def _clicar(caixa) -> None:
        vistas.append((caixa.text(), [b.text() for b in caixa.buttons()]))
        botao = next(b for b in caixa.buttons() if b.text().startswith(comeco_do_botao))
        botao.click()

    def _exec(caixa):
        if caixa.windowTitle() == TITULO_DA_CAIXA:
            QTimer.singleShot(0, lambda: _clicar(caixa))
        return exec_de_antes(caixa)

    monkeypatch.setattr(QMessageBox, "exec", _exec)


def _destino_ja_escolhido(monkeypatch, caminho: Path) -> None:
    """A janela "Antes de processar" devolve `caminho` (como se o Kaique
    tivesse confirmado esse nome)."""
    import ui.janela_confirmar as confirmar

    monkeypatch.setattr(confirmar, "pedir_confirmacao", lambda *_a, **_k: caminho)


def _esperar_o_fim(janela, segundos: float = 180) -> None:
    from ui.janela_principal import CONFERIR, FINAL, PROGRESSO

    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        QApplication.processEvents()
        if janela.telas.currentIndex() == FINAL:
            return
        if janela.telas.currentIndex() == CONFERIR and janela.avisos:
            pytest.fail(f"o processamento falhou: {janela.avisos}")
        time.sleep(0.02)
    pytest.fail(f"o processamento nao terminou (tela {janela.telas.currentIndex()}, "
                f"PROGRESSO={PROGRESSO})")


def _paginas(caminho: Path) -> int:
    with fitz.open(str(caminho)) as doc:
        return doc.page_count


def test_salvar_como_2_gera_o_pdf_novo_e_nao_toca_no_antigo(janela, pasta, monkeypatch):
    _livro_conferido(janela, pasta)
    antigo = pasta / "saida" / "pronto.pdf"
    bytes_do_antigo = _pdf_antigo(antigo, "o antigo")
    _destino_ja_escolhido(monkeypatch, antigo)
    vistas: list = []
    _escolher_na_caixa(monkeypatch, "salvar como", vistas)

    janela.processar()
    _esperar_o_fim(janela)

    novo = pasta / "saida" / "pronto (2).pdf"
    assert vistas, "a caixa 'Ja existe...' nao apareceu"
    texto, botoes = vistas[0]
    assert "pronto.pdf" in texto
    # a ordem na tela e o Qt que decide (pelo papel do botao); aqui so os textos
    assert sorted(botoes) == sorted(
        ["substituir o antigo", "salvar como pronto (2).pdf", "cancelar"])
    assert novo.exists(), "o PDF novo nao foi gerado"
    assert _paginas(novo) == 4
    assert antigo.read_bytes() == bytes_do_antigo, "o arquivo antigo foi mexido"
    assert Path(janela.projeto.caminho_saida) == novo
    assert not janela.avisos, janela.avisos


def test_com_o_2_tambem_ocupado_salva_como_3(janela, pasta, monkeypatch):
    _livro_conferido(janela, pasta)
    antigo = pasta / "saida" / "pronto.pdf"
    ocupado = pasta / "saida" / "pronto (2).pdf"
    bytes_do_antigo = _pdf_antigo(antigo, "o antigo")
    bytes_do_ocupado = _pdf_antigo(ocupado, "o (2) que ja existia")
    _destino_ja_escolhido(monkeypatch, antigo)
    vistas: list = []
    _escolher_na_caixa(monkeypatch, "salvar como", vistas)

    janela.processar()
    _esperar_o_fim(janela)

    novo = pasta / "saida" / "pronto (3).pdf"
    assert "salvar como pronto (3).pdf" in vistas[0][1]
    assert novo.exists(), "o PDF novo nao foi gerado"
    assert _paginas(novo) == 4
    assert antigo.read_bytes() == bytes_do_antigo
    assert ocupado.read_bytes() == bytes_do_ocupado
    assert Path(janela.projeto.caminho_saida) == novo


def test_substituir_grava_por_cima_do_antigo(janela, pasta, monkeypatch):
    _livro_conferido(janela, pasta)
    antigo = pasta / "saida" / "pronto.pdf"
    _pdf_antigo(antigo, "o antigo")
    _destino_ja_escolhido(monkeypatch, antigo)
    _escolher_na_caixa(monkeypatch, "substituir o antigo", [])

    janela.processar()
    _esperar_o_fim(janela)

    assert _paginas(antigo) == 4, "nao substituiu o antigo"
    assert not (pasta / "saida" / "pronto (2).pdf").exists()
    assert Path(janela.projeto.caminho_saida) == antigo


def test_cancelar_nao_processa_nem_mexe_no_disco(janela, pasta, monkeypatch):
    from ui.janela_principal import CONFERIR

    _livro_conferido(janela, pasta)
    antigo = pasta / "saida" / "pronto.pdf"
    bytes_do_antigo = _pdf_antigo(antigo, "o antigo")
    _destino_ja_escolhido(monkeypatch, antigo)
    vistas: list = []
    _escolher_na_caixa(monkeypatch, "cancelar", vistas)
    tela_antes = janela.telas.currentIndex()

    janela.processar()

    assert vistas, "a caixa 'Ja existe...' nao apareceu"
    assert janela.telas.currentIndex() == tela_antes == CONFERIR
    assert antigo.read_bytes() == bytes_do_antigo
    assert sorted(p.name for p in antigo.parent.iterdir()) == ["pronto.pdf"]
