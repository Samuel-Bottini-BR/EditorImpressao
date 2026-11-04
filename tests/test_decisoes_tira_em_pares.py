"""Prova de comportamento da D-611 (04/11/2026): com a vista "Duas lado a lado" escolhida, a tira de
miniaturas mostra as páginas de duas em duas, juntas como no livro aberto.

Samuel, testando a lista de 04/11, item 7 (print `relatorios/testes-guiados/2026-10-29-automatico/
a-56-dividir-folha-1-duas-lado-a-lado-7-com-duvida.png`): "funciou, mas quando estiver duas lado a
lado escolhido os icones embaixo tem que estar em duas folhas;." · pergunta: "Quer dizer que, com
'Duas lado a lado' escolhido, as miniaturas embaixo também aparecem de duas em duas, juntas como no
livro aberto?" → "Sim". Livro de decisões: "Com a vista "Duas lado a lado" escolhida, a tira de
miniaturas embaixo mostra as páginas de duas em duas, juntas como no livro aberto (a 1 sozinha, à
direita), como a vista grande. Em "Uma página", a tira fica como está."

O que já estava escolhido e testado e continua (D-605): o "Ver em pares" do menu da tira (etapa 5
do layout, guardado para o próximo livro: tests/test_miniaturas_novas.py) não muda nem é gravado
por isto; a tira do Dividir (D-601: folha dividida = duas miniaturas, não dividida = uma dupla); a
miniatura da vez e a tira rolada até ela (conserto de 03/11, tests/test_dividir_ajustes_03_11.py).

O que se mede: o lugar de cada miniatura na grade da tira (TiraMiniaturas.posicao e a posição na
grade de verdade), a escolhida, o clique numa miniatura e o "Ver em pares" guardado. O ANTIGO SAIU:
no código de antes (e17410fe) a tira ficava uma a uma em "Duas lado a lado"; o teste de reversão
falha lá.
"""

from __future__ import annotations

import time

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixtures app, pasta, janela)
    _pagina,
    _pdf,
    app,
    janela,
    pasta,
)

LIVRO_ABERTO = [(0, 1), (0, 3), (0, 4), (0, 6), (0, 7), (0, 9)]   # 1 sozinha à direita; 2-3; 4-5
UMA_A_UMA = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]
# D-611 atualizada (04/11/2026, só no Dividir): as duas metades de cada folha juntas, 1-2, 3-4, 5-6
PELA_FOLHA = [(0, 0), (0, 1), (0, 3), (0, 4), (0, 6), (0, 7)]


def _aberto() -> np.ndarray:
    return np.concatenate([_pagina(600), _pagina(760)], axis=1)


def _assentar(vezes: int = 5) -> None:
    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        QApplication.processEvents()


def _esperar(condicao, segundos: float = 40.0, motivo: str = "") -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar(2)
        if condicao():
            return
        time.sleep(0.02)
    raise AssertionError(f"não aconteceu a tempo: {motivo}")


def _na_grade(tira) -> list[tuple[int, int]]:
    """Onde cada miniatura está DE VERDADE na grade da tira (linha, coluna)."""
    saida = []
    for mini in tira._miniaturas:
        i = tira.linha.indexOf(mini)
        linha, coluna, _a, _b = tira.linha.getItemPosition(i)
        saida.append((linha, coluna))
    return saida


def _aberto_no(janela, tmp_path, folhas: int = 3, ferramenta: str | None = None):
    janela.resize(1400, 900)
    janela.show()
    janela.activateWindow()
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", [_aberto() for _ in range(folhas)]))
    tela = janela.tela_conferir
    if ferramenta:
        tela.escolher_ferramenta(ferramenta)
    _assentar()
    return tela


def test_reversao_d611_tira_em_pares_no_dividir_em_duas_lado_a_lado(janela, tmp_path):
    """D-611 (a-56): no Dividir, Gradus dividido (aqui 3 folhas duplas: 6 páginas), "Duas lado a
    lado" → a tira em pares (desde a D-611 atualizada de 04/11, no Dividir pela folha: 1-2; 3-4;
    5-6; antes, como no livro aberto: a 1 sozinha à direita; 2-3; 4-5; 6);
    "Uma página" → a tira volta a ficar uma a uma, como está. No código de antes (e17410fe) a
    tira ficava uma a uma nas duas: falha lá."""
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _aberto_no(janela, tmp_path, 3, "dividir")
    projeto = janela.projeto
    tela.botao_dividir_todas.click()
    _esperar(lambda: all(f.dividir for f in projeto.folhas), motivo="dividir todas")
    _assentar()
    tira = tela.tira
    assert len(tira._miniaturas) == 6 and tela.mostrar == UMA
    assert _na_grade(tira) == UMA_A_UMA, "Uma página: uma a uma, como está"
    tela.botoes_mostrar[DUAS].click()
    _assentar()
    # D-611 atualizada (04/11/2026), só no Dividir: a pergunta "Quer que a tira junte igual à
    # tela grande, a 11 com a 12?" → "SIm, mas tem que verificar se vai ficar assim em todo os
    # lugares né? a miniatura corresponder com o numero real". No Dividir a tira junta pela
    # FOLHA (as duas metades de cada folha: 1-2, 3-4, 5-6), como a tela grande; antes era como no
    # livro aberto (LIVRO_ABERTO). Fora do Dividir continua LIVRO_ABERTO (teste de baixo).
    # Mudança autorizada pela gerente em 04/11.
    assert _na_grade(tira) == PELA_FOLHA, "Duas lado a lado no Dividir: em pares, pela folha"
    assert [tira.posicao(i) for i in range(6)] == PELA_FOLHA
    tela.botoes_mostrar[UMA].click()
    _assentar()
    assert _na_grade(tira) == UMA_A_UMA


def test_reversao_d611_tira_em_pares_nas_outras_ferramentas(janela, tmp_path):
    """D-611 vale com "Duas lado a lado" escolhida, em qualquer ferramenta (a vista grande mostra
    os pares do livro aberto): no Cortar, 6 páginas → a tira em pares; "Uma página" → uma a
    uma."""
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _aberto_no(janela, tmp_path, 3)
    projeto = janela.projeto
    if len(projeto.paginas) != 6:                       # o livro abre dividido pelo Automático?
        tela.escolher_ferramenta("dividir")
        tela.botao_dividir_todas.click()
        _esperar(lambda: all(f.dividir for f in projeto.folhas), motivo="dividir todas")
    tela.escolher_ferramenta("cortar")
    _assentar()
    tira = tela.tira
    assert len(tira._miniaturas) == 6
    tela.botoes_mostrar[DUAS].click()
    _assentar()
    assert _na_grade(tira) == LIVRO_ABERTO
    tela.botoes_mostrar[UMA].click()
    _assentar()
    assert _na_grade(tira) == UMA_A_UMA


def test_d611_nao_mexe_no_ver_em_pares_guardado(janela, tmp_path, monkeypatch):
    """O "Ver em pares" do menu da tira (escolha da pessoa, guardada para o próximo livro) não
    muda nem é gravado por escolher "Duas lado a lado"; ligado, a tira fica em pares também em
    "Uma página", como antes."""
    import configuracoes
    from ui.widgets.paginas_rolando import DUAS, UMA

    gravados = []
    real = configuracoes.escrever
    monkeypatch.setattr(configuracoes, "escrever",
                        lambda chave, valor: (gravados.append(chave), real(chave, valor))[1])
    tela = _aberto_no(janela, tmp_path, 3, "dividir")
    m = tela.miniaturas
    assert not m.em_pares and not m.acao_em_pares.isChecked()
    tela.botoes_mostrar[DUAS].click()
    _assentar()
    assert not m.em_pares and not m.acao_em_pares.isChecked(), "a escolha do menu não muda"
    assert "miniaturas" not in gravados, "nada é gravado"
    tela.botoes_mostrar[UMA].click()
    m.acao_em_pares.setChecked(True)                    # a pessoa liga o "Ver em pares"
    _assentar()
    assert tela.tira.posicao(0) == (0, 1), "ligado no menu: em pares também em Uma página"


def test_d611_escolhida_e_clique_continuam(janela, tmp_path):
    """Em "Duas lado a lado", a miniatura da vez continua marcada e à vista na tira (o conserto de
    03/11), e clicar numa miniatura do par vai para ela."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from ui.widgets.paginas_rolando import DUAS

    tela = _aberto_no(janela, tmp_path, 12, "dividir")
    projeto = janela.projeto
    tela.botao_dividir_todas.click()
    _esperar(lambda: all(f.dividir for f in projeto.folhas), motivo="dividir todas")
    tela.botoes_mostrar[DUAS].click()
    _assentar()
    tira = tela.tira
    tela._ir_para_o_quadro_da_tira(20)
    _assentar(10)
    escolhidas = [i for i, m in enumerate(tira._miniaturas) if m.selecionada]
    assert escolhidas == [20]
    vista = tira.rolagem.viewport()
    mini = tira._miniaturas[20]
    canto = mini.mapTo(vista, mini.rect().topLeft())
    assert 0 <= canto.x() and canto.x() + mini.width() <= vista.width(), "a da vez à vista"
    alvo = tira._miniaturas[18]
    tira.rolagem.ensureWidgetVisible(alvo)
    _assentar()
    QTest.mouseClick(alvo, Qt.LeftButton)
    _assentar(5)
    assert [i for i, m in enumerate(tira._miniaturas) if m.selecionada] == [18]
    assert tela.indice_folha == projeto.paginas[tela.indice_pagina].folha == 9
    _esperar_o_que_anda_por_tras(tela)


def _esperar_o_que_anda_por_tras(tela) -> None:
    """A medida do "Parece em branco" e as miniaturas rodam por trás: o teste espera elas
    acabarem (um fio de fundo vivo no fim do pytest derruba o processo)."""
    tarefa = getattr(tela, "_tarefa_do_em_branco", None)
    if tarefa is not None:
        tarefa.wait(60000)
    tela.tira._pool.waitForDone(30000)
    _assentar(10)
