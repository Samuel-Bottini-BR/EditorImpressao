"""Prova de comportamento da D-611 refeita (04/11/2026): com "Duas lado a lado" escolhida, as duas
miniaturas de cada par ficam JUNTAS na tira, como as duas páginas do livro aberto - medido nos
desenhos que aparecem na tela, não só na coluna da grade.

O defeito (Samuel, 04/11, testando a D-611: "4- não está ok coloquei no primeiro print"; print
`relatorios/testes-guiados/2026-10-29-automatico/a-57-dividir-duas-lado-a-lado-tira-sem-pares.png`:
Dividir, Gradus, "Duas lado a lado", a tira com as miniaturas uma a uma, separadas). A grade já punha
1 | 2-3 | 4-5, mas com as folhas divididas cada miniatura é uma página em pé, estreita, no meio de um
quadro de largura fixa: o vão entre os dois desenhos do par era o mesmo de "Uma página" (22 pontos)
e entre um par e outro só 10 pontos a mais. A olho, uma a uma. Os testes de antes
(tests/test_decisoes_tira_em_pares.py) só conferiam a coluna de cada quadro na grade.

Decisão: D-611 ("quando estiver duas lado a lado escolhido os icones embaixo tem que estar em duas
folhas" → "Sim" a "as miniaturas embaixo também aparecem de duas em duas, juntas como no livro
aberto?"). O que continua como está (D-605): "Uma página" (uma a uma, o mesmo vão) e o "Ver em pares"
do menu dos três pontinhos (D-032, ly-pares "Está bom": o vão de antes dentro do par).

Como se mede: a tira é desenhada numa imagem (grab) e cada coluna de pontos claros (o papel da
página) conta como desenho; os desenhos são os trechos seguidos de colunas claras. O teste de
reversão falha no código de antes (5cf4aaed): dentro do par o vão era 22 pontos.
"""

from __future__ import annotations

import time

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixtures app, pasta, janela)
    _aberto,
    _pdf,
    app,
    janela,
    pasta,
)

FOLHAS = 4                     # 8 páginas depois de dividir: 1 | 2-3 | 4-5 | 6-7 | 8


def _assentar(vezes: int = 5) -> None:
    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        QApplication.processEvents()


def _esperar(condicao, segundos: float = 60.0, motivo: str = "") -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar(2)
        if condicao():
            return
        time.sleep(0.02)
    raise AssertionError(f"não aconteceu a tempo: {motivo}")


def _desenhos(tira) -> list[tuple[int, int]]:
    """Os desenhos das páginas na tira, da esquerda para a direita: (primeira coluna, última
    coluna) de cada trecho seguido de colunas claras (o papel), na faixa da altura dos desenhos.
    Medido na imagem da tira, como aparece na tela."""
    from PySide6.QtGui import QImage

    from ui.widgets.tira_miniaturas import ALTURA_MINIATURA

    dentro = tira.rolagem.widget()
    imagem = dentro.grab().toImage().convertToFormat(QImage.Format_RGB888)
    largura, altura = imagem.width(), imagem.height()
    linha_bytes = imagem.bytesPerLine()
    cru = np.frombuffer(imagem.constBits(), np.uint8, count=linha_bytes * altura)
    rgb = cru.reshape(altura, linha_bytes)[:, : largura * 3].reshape(altura, largura, 3)
    primeira = tira._miniaturas[0]
    topo = primeira.mapTo(dentro, primeira.rect().topLeft()).y()
    faixa = rgb[topo + 6: topo + ALTURA_MINIATURA - 6].astype(int).mean(axis=2)
    clara = (faixa > 170).mean(axis=0) > 0.5
    trechos, comeco = [], None
    for x, c in enumerate(clara):
        if c and comeco is None:
            comeco = x
        elif not c and comeco is not None:
            trechos.append((comeco, x - 1))
            comeco = None
    if comeco is not None:
        trechos.append((comeco, len(clara) - 1))
    return [t for t in trechos if t[1] - t[0] >= 8]           # tira restos de borda


def _vaos(tira) -> list[int]:
    d = _desenhos(tira)
    assert len(d) == FOLHAS * 2, f"esperava {FOLHAS * 2} desenhos na tira, achei {d}"
    return [d[k + 1][0] - d[k][1] - 1 for k in range(len(d) - 1)]


def _no_dividir_tudo_dividido(janela, tmp_path):
    """O caminho do a-57: livro de folhas duplas, ferramenta Dividir, "dividir todas" (as
    miniaturas viram páginas em pé, estreitas), miniaturas prontas."""
    janela.resize(1400, 900)
    janela.show()
    janela.activateWindow()
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", [_aberto() for _ in range(FOLHAS)]))
    tela = janela.tela_conferir
    tela.escolher_ferramenta("dividir")
    _assentar()
    projeto = janela.projeto
    if not all(f.dividir for f in projeto.folhas):
        tela.botao_dividir_todas.click()
        _esperar(lambda: all(f.dividir for f in projeto.folhas), motivo="dividir todas")
    tira = tela.tira
    _esperar(lambda: len(tira._miniaturas) == FOLHAS * 2
             and all(m._pixmap is not None for m in tira._miniaturas), motivo="as miniaturas")
    _assentar(10)
    return tela


def _esperar_o_que_anda_por_tras(tela) -> None:
    """A medida do "Parece em branco" e as miniaturas rodam por trás: espera acabarem."""
    tarefa = getattr(tela, "_tarefa_do_em_branco", None)
    if tarefa is not None:
        tarefa.wait(60000)
    tela.tira._pool.waitForDone(30000)
    _assentar(10)


def test_reversao_d611_par_junto_no_dividir_em_duas_lado_a_lado(janela, tmp_path):
    """D-611, o defeito do a-57 (04/11/2026): no Dividir, folhas divididas, "Duas lado a lado" →
    os dois desenhos de cada par (2-3, 4-5, 6-7) ficam encostados, e entre um par e outro fica um
    vão bem maior. No código de antes o vão dentro do par era 22 pontos (o mesmo de "Uma
    página"): falha lá."""
    from ui.widgets.paginas_rolando import DUAS

    tela = _no_dividir_tudo_dividido(janela, tmp_path)
    tela.botoes_mostrar[DUAS].click()
    _assentar(10)
    assert tela.mostrar == DUAS and tela.tira.pares_pela_vista
    vaos = _vaos(tela.tira)
    dentro = [vaos[1], vaos[3], vaos[5]]            # 2-3, 4-5, 6-7
    entre = [vaos[0], vaos[2], vaos[4], vaos[6]]     # 1|2, 3|4, 5|6, 7|8
    assert max(dentro) <= 6, f"as duas páginas do par juntas, como no livro aberto: vãos {vaos}"
    assert min(entre) >= 20 and min(entre) >= 4 * max(dentro, default=1), \
        f"entre um par e outro, um vão que se vê: vãos {vaos}"
    _esperar_o_que_anda_por_tras(tela)


def test_d611_uma_pagina_continua_uma_a_uma_com_o_mesmo_vao(janela, tmp_path):
    """Em "Uma página" a tira fica como está (D-611): todos os vãos iguais, nenhum par encostado;
    e voltar de "Duas lado a lado" devolve o mesmo vão de antes."""
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _no_dividir_tudo_dividido(janela, tmp_path)
    assert tela.mostrar == UMA
    antes = _vaos(tela.tira)
    assert max(antes) - min(antes) <= 1 and min(antes) >= 15, f"uma a uma: vãos {antes}"
    tela.botoes_mostrar[DUAS].click()
    _assentar(10)
    tela.botoes_mostrar[UMA].click()
    _assentar(10)
    assert _vaos(tela.tira) == antes, "voltar para Uma página: a tira como estava"
    _esperar_o_que_anda_por_tras(tela)


def test_d611_ver_em_pares_do_menu_continua_com_o_jeito_aprovado(janela, tmp_path):
    """O "Ver em pares" do menu (D-032, ly-pares "Está bom") em "Uma página" continua com o jeito
    de antes: o vão dentro do par é o mesmo de uma a uma e entre pares um pouco maior. Só a
    D-611 ("Duas lado a lado") encosta o par."""
    from ui.widgets.paginas_rolando import UMA

    tela = _no_dividir_tudo_dividido(janela, tmp_path)
    assert tela.mostrar == UMA
    uma_a_uma = _vaos(tela.tira)[0]
    tela.miniaturas.acao_em_pares.setChecked(True)
    _assentar(10)
    assert tela.tira.em_pares and not tela.tira.pares_pela_vista
    vaos = _vaos(tela.tira)
    assert all(abs(v - uma_a_uma) <= 1 for v in (vaos[1], vaos[3], vaos[5])), \
        f"dentro do par, o vão de antes: {vaos} (uma a uma: {uma_a_uma})"
    assert all(v > uma_a_uma + 5 for v in (vaos[0], vaos[2], vaos[4], vaos[6])), vaos
    tela.miniaturas.acao_em_pares.setChecked(False)
    _assentar()
    _esperar_o_que_anda_por_tras(tela)
