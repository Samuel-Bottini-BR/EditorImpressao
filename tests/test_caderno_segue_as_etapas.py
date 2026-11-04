"""Teste de reversão da D-603 (CLAUDE.md §4.7): as folhas do caderno da etapa 7 seguem o
"Dividir" marcado na janela do Automático, antes do "Rodar".

Bug (print do Samuel `relatorios/testes-guiados/2026-10-29-automatico/
a-49-dividir-marcado-caderno-sem-divisao.png`, 03/11/2026: etapa 1 "Dividir" marcada, etapa 7
aberta, o caderno com os scans inteiros): "eu fui lá e apertei o botão de dividir e nos cadernos
ainda aparece a folha sem divisão, era para ser com divisão, já que eu cliquei lá em cima, mesmo
que eu não tenha processado ainda, pois é o preview." -> D-603: "pode ser assim nos cadernos".

Causa: ui/widgets/folhas_do_caderno contava e distribuía as páginas do livro COMO ESTÁ
(Projeto.paginas_ativas): com o Dividir marcado num livro sem dividir, uma página por folha do
scan, e cada lugar do caderno recebia as duas metades coladas (a folha aberta).

No código antigo (`016ec37a`) este teste falha: "Folha 1 de 2" (6 folhas do scan) no lugar de
"Folha 1 de 3" (12 páginas), e cada metade da folha do caderno traz duas páginas.

Livro sintético: 6 folhas deitadas, cada uma com duas páginas lado a lado; a página k (0 a 11)
tem uma faixa preta numa altura só dela, para ler qual página caiu em cada metade.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from tests.test_decisoes_automatico import _pdf  # noqa: E402

LIMITE_S = 180
FOLHAS = 6
ALTURA, LARGURA = 840, 600        # uma página; a folha do scan tem duas lado a lado


def _pagina(k: int) -> np.ndarray:
    img = np.full((ALTURA, LARGURA, 3), 245, np.uint8)
    y = 30 + k * 60
    img[y:y + 40, 100:LARGURA - 100] = 20
    return img


def livro_de_folhas_abertas(tmp_path: Path) -> str:
    """6 folhas do scan, cada uma com as páginas 2i e 2i+1 lado a lado (deitadas)."""
    caminho = tmp_path / "abertas.pdf"
    if not caminho.exists():
        _pdf(caminho, [np.concatenate([_pagina(2 * i), _pagina(2 * i + 1)], axis=1)
                       for i in range(FOLHAS)])
    return str(caminho)


def paginas_na_metade(metade: np.ndarray) -> list[int]:
    """As páginas (1, 2, ...) cujas faixas estão nesta metade da folha do caderno."""
    cinza = metade if metade.ndim == 2 else metade.mean(axis=2)
    escuras = (cinza < 100).mean(axis=1) > 0.15
    achadas, y = [], 0
    while y < len(escuras):
        if escuras[y]:
            inicio = y
            while y < len(escuras) and escuras[y]:
                y += 1
            meio = (inicio + y) / 2 / cinza.shape[0] * ALTURA
            achadas.append(int(round((meio - 50) / 60)) + 1)
        y += 1
    return achadas


def paginas_do_lado(face: np.ndarray) -> tuple:
    meio = face.shape[1] // 2
    return paginas_na_metade(face[:, :meio]), paginas_na_metade(face[:, meio:])


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def janela(app, tmp_path, monkeypatch):
    import projetos
    from ui.automatico import _guardiao
    from ui.janela_principal import JanelaPrincipal

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    yield janela
    janela._fechar_a_janela_do_automatico()
    for tarefa in list(_guardiao().tarefas):
        tarefa.wait(60000)
    assentar(app)
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


def assentar(app, vezes: int = 5) -> None:
    for _ in range(vezes):
        app.processEvents()


def esperar(app, painel) -> None:
    fim = time.monotonic() + LIMITE_S
    while time.monotonic() < fim:
        app.processEvents()
        if not painel.calculando():
            assentar(app)
            if not painel.calculando():
                return
        time.sleep(0.02)
    raise AssertionError("a folha do caderno não terminou")


def test_d603_dividir_marcado_o_caderno_mostra_as_paginas_divididas(janela, app, tmp_path):
    """D-603 (print a-49): livro sem dividir, "Dividir" e "Montar cadernos" marcados, etapa 7
    aberta, sem Rodar: 12 páginas em cadernos de 8 -> 3 folhas; folha 1: frente páginas 8 e 1,
    verso 2 e 7, UMA página em cada metade (antes: as duas metades da folha do scan coladas)."""
    janela.abrir_livro(livro_de_folhas_abertas(tmp_path))
    assentar(app)
    estado = janela.estado_do_automatico
    estado.marcadas = {A.DIVIDIR, A.CADERNOS}
    estado.opcoes["paginas_por_caderno"] = 8
    grande = janela.abrir_o_automatico(A.CADERNOS)
    assentar(app)
    folhas = grande.folhas_do_caderno
    esperar(app, folhas)
    assert folhas.rotulos["frente"].text() == "Folha 1 de 3 — frente"
    frente, verso = folhas.faces()
    assert paginas_do_lado(frente) == ([8], [1])
    assert paginas_do_lado(verso) == ([2], [7])
    # o livro não mudou (só mostra, D-577): continua com uma página por folha do scan
    assert len(janela.projeto.paginas_ativas) == FOLHAS
