"""Prova de comportamento da D-601 (02/11/2026): no Dividir, "Uma página" mostra só a metade.

Samuel, testando o Dividir no Gradus Primus: "eu dividi a pagina não era para ela virar só uma na
hora que eu dividi, como funciona no scantailor?" · "ele não cortou, porque como pode ver as duas
paginas ainda estão juntas, deveria então aparecer só metdade da pagina que era dupla, e eu pode
mudar a opção lá embaixo de uma pagina, para pagina dupla." · pergunta: ""Uma página" (de fábrica):
depois de dividir, aparece só a metade, uma página de cada vez, e as setas andam pelas páginas.
"Duas lado a lado": aparece a folha inteira, com a linha azul para arrastar, como hoje. Pode ser
assim?" → "ok, pode botar um agente para fazer isso".
Livro de decisões: "Na ferramenta Dividir, com "Uma página" (de fábrica), a folha dividida mostra
só uma metade (uma página por vez, as setas andam pelas páginas); com "Duas lado a lado", a folha
inteira com a linha azul para arrastar. Muda a D-007 só dentro do Dividir."

O que se mede: a imagem que a vista do Dividir recebeu (comparada, pixel a pixel, com a folha que
o programa leu do PDF e com as duas metades dela partidas na linha), se a linha azul está lá e se
arrastá-la muda a divisão, e a página e a folha da vez depois das setas, da roda e do teclado.
O ANTIGO SAIU: no código de antes (110976f) o Dividir mostrava sempre a folha inteira com a
linha, e as setas andavam de folha em folha.

Livro sintético de 3 folhas com o livro aberto; a página da esquerda tem um quadrado preto no
alto à esquerda, a da direita não (para saber qual metade está na tela).
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QKeyEvent, QWheelEvent  # noqa: E402

from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixtures app, pasta, janela)
    _pagina,
    _pdf,
    app,
    janela,
    pasta,
    precisa_da_dll,
)


def _aberto_com_marca() -> np.ndarray:
    """O livro aberto, com um quadrado preto no alto da página da ESQUERDA."""
    esquerda, direita = _pagina(), _pagina()
    esquerda[30:110, 30:110] = 0
    return np.concatenate([esquerda, direita], axis=1)


def _livro(tmp_path: Path) -> str:
    return _pdf(tmp_path / "aberto.pdf", [_aberto_com_marca() for _ in range(3)])


def _assentar(vezes: int = 3) -> None:
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


def _pixmap_bgr(pix) -> np.ndarray:
    imagem = pix.toImage().convertToFormat(pix.toImage().Format.Format_RGB888)
    w, h = imagem.width(), imagem.height()
    dados = np.frombuffer(imagem.constBits(), np.uint8).reshape(h, imagem.bytesPerLine())
    return dados[:, : w * 3].reshape(h, w, 3)[..., ::-1].copy()


def _na_tela(tela) -> np.ndarray:
    """O que a vista do Dividir mostra agora (espera a folha chegar do PDF)."""
    from ui.tela_conferir import ABA_CORTE, DPI_PREVIA

    vista = tela.visualizadores[ABA_CORTE]
    _esperar(lambda: tela.previas.pegar_folha(tela.indice_folha, DPI_PREVIA) is not None,
             motivo="a folha")
    tela.atualizar()
    assert vista._pixmap is not None
    return _pixmap_bgr(vista._pixmap)


def _partes(tela) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A folha da vez como o programa a leu, e as duas metades dela partidas na linha."""
    from core.dividir import dividir_imagem
    from ui.tela_conferir import DPI_PREVIA

    _esperar(lambda: tela.previas.pegar_folha(tela.indice_folha, DPI_PREVIA) is not None,
             motivo="a folha")
    folha = tela.previas.pegar_folha(tela.indice_folha, DPI_PREVIA)
    esquerda, direita = dividir_imagem(folha, tela.projeto.folhas[tela.indice_folha].posicao_corte)
    return folha, esquerda, direita


def _tem_o_quadrado(img: np.ndarray) -> bool:
    """O quadrado preto do alto da página da esquerda (30 a 110 de 600 x 840 pontos)."""
    h, w = img.shape[:2]
    return float(img[int(0.05 * h):int(0.12 * h), int(0.07 * w):int(0.16 * w)].mean()) < 40


def _igual(a: np.ndarray, b: np.ndarray) -> bool:
    return a.shape == b.shape and float(np.abs(a.astype(int) - b.astype(int)).mean()) < 1.0


def _roda(vista, passos: int) -> None:
    """Uma volta da roda do mouse em cima da página (para baixo: passos negativos)."""
    from PySide6.QtWidgets import QApplication

    centro = QPointF(vista.width() / 2, vista.height() / 2)
    evento = QWheelEvent(centro, vista.mapToGlobal(centro), QPoint(0, 0), QPoint(0, 120 * passos),
                         Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
    QApplication.sendEvent(vista, evento)


def _no_dividir_dividida(janela, tmp_path):
    """O caminho do Samuel no Gradus Primus: abrir o livro (sem Dividir), escolher a
    ferramenta Dividir na folha 1 e clicar "dividir esta"."""
    from ui.tela_conferir import ABA_CORTE

    janela.show()
    janela.abrir_livro(_livro(tmp_path))
    tela = janela.tela_conferir
    tela.escolher_ferramenta("dividir")
    tela._ir_para(0)
    assert tela.aba_atual == ABA_CORTE and tela.trabalha_com_folhas
    return tela


@precisa_da_dll
def test_d601_uma_pagina_mostra_so_a_metade_e_as_setas_andam_pelas_paginas(janela, tmp_path):
    """D-601: folha NÃO dividida → a folha inteira, como antes. "dividir esta" com "Uma
    página" (de fábrica) → só a metade da esquerda, sem a linha; a seta → a metade da
    direita (a mesma folha); a seta → a próxima folha (não dividida: inteira); a seta para
    trás → a direita da folha 1; a roda e o teclado andam igual. O rótulo continua "folha N
    de M" e a tira continua de folhas (o Dividir confere a folha)."""
    from ui.tela_conferir import ABA_CORTE
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _no_dividir_dividida(janela, tmp_path)
    projeto, vista = janela.projeto, tela.visualizadores[ABA_CORTE]
    assert tela.mostrar == UMA

    # folha não dividida: a folha inteira, como hoje
    assert not projeto.folhas[0].dividir
    folha, _e, _d = _partes(tela)
    assert _igual(_na_tela(tela), folha) and not vista.corte_visivel

    tela.botao_nao_dividir.click()                     # "dividir esta"
    assert projeto.folhas[0].dividir
    folha, esquerda, direita = _partes(tela)
    na_tela = _na_tela(tela)
    assert _igual(na_tela, esquerda), "depois de dividir aparece só a metade (a da esquerda)"
    assert not _igual(na_tela, folha) and not vista.corte_visivel
    assert _tem_o_quadrado(na_tela)                     # o quadrado da página da esquerda
    assert not _tem_o_quadrado(direita)
    assert tela.rotulo_da_pagina.text() == "folha 1 de 3"
    assert tela.botoes_mostrar[UMA].isEnabled() and tela.botoes_mostrar[DUAS].isEnabled()

    tela._navegar(1)                                   # a seta: a página da direita
    assert tela.indice_folha == 0 and projeto.paginas[tela.indice_pagina].metade == "direita"
    assert _igual(_na_tela(tela), direita)
    assert tela.rotulo_da_pagina.text() == "folha 1 de 3"
    assert tela.botao_anterior.isEnabled() and tela.botao_proxima.isEnabled()

    tela.botao_proxima.click()                         # a seta da barra de baixo: a folha 2
    assert tela.indice_folha == 1
    folha2, _e, _d = _partes(tela)
    assert _igual(_na_tela(tela), folha2)               # não dividida: inteira

    janela.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Left, Qt.NoModifier))
    assert tela.indice_folha == 0 and projeto.paginas[tela.indice_pagina].metade == "direita"
    _roda(vista, 1)                                    # a roda para cima: a da esquerda
    assert tela.indice_folha == 0 and projeto.paginas[tela.indice_pagina].metade == "esquerda"
    assert not tela.botao_anterior.isEnabled()
    _roda(vista, -1)                                   # a roda para baixo: a da direita
    assert tela.indice_folha == 0 and projeto.paginas[tela.indice_pagina].metade == "direita"


@precisa_da_dll
def test_d601_duas_lado_a_lado_mostra_a_folha_inteira_com_a_linha(janela, tmp_path):
    """D-601: no Dividir, "Duas lado a lado" → a folha inteira com a linha azul, que se
    arrasta (muda a divisão), e as setas andam de folha em folha, como antes. Voltar para
    "Uma página" → a metade da página da vez de novo. Fora do Dividir, o "Duas lado a lado"
    continua sendo os pares (D-015)."""
    from ui.tela_conferir import ABA_CORTE
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _no_dividir_dividida(janela, tmp_path)
    projeto, vista = janela.projeto, tela.visualizadores[ABA_CORTE]
    tela.botao_nao_dividir.click()                     # "dividir esta"
    tela._navegar(1)                                   # a página da direita
    assert projeto.paginas[tela.indice_pagina].metade == "direita"

    tela.botoes_mostrar[DUAS].click()
    assert tela.mostrar == DUAS and janela.menu.acoes["lado_a_lado"].isChecked()
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem   # a ferramenta, não os pares
    folha, _e, direita = _partes(tela)
    assert _igual(_na_tela(tela), folha) and vista.corte_visivel
    antes = projeto.folhas[0].posicao_corte
    vista.corte_movido.emit(0.45)                      # arrastar a linha
    assert projeto.folhas[0].posicao_corte == pytest.approx(0.45) != antes

    tela.botoes_mostrar[UMA].click()                   # de volta: a metade da página da vez
    _folha, _e, direita = _partes(tela)
    assert _igual(_na_tela(tela), direita) and not vista.corte_visivel

    tela.botoes_mostrar[DUAS].click()
    tela._navegar(1)                                   # no "Duas lado a lado", de folha em folha
    assert tela.indice_folha == 1
    tela._navegar(-1)
    assert tela.indice_folha == 0

    tela.escolher_ferramenta("mao")                    # fora do Dividir: os pares
    assert tela.vista_da_pagina.currentWidget() is tela.lado_a_lado


@precisa_da_dll
def test_d601_nao_dividir_esta_volta_a_folha_inteira(janela, tmp_path):
    """D-601 com a D-498: na metade da direita, "não dividir esta" → a folha volta a ser uma
    página só e aparece inteira; a seta vai à folha 2 (um passo só por folha não dividida)."""
    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir_dividida(janela, tmp_path)
    projeto, vista = janela.projeto, tela.visualizadores[ABA_CORTE]
    tela.botao_nao_dividir.click()                     # "dividir esta"
    tela._navegar(1)
    tela.botao_nao_dividir.click()                     # "não dividir esta"
    assert not projeto.folhas[0].dividir and tela.indice_folha == 0
    folha, _e, _d = _partes(tela)
    assert _igual(_na_tela(tela), folha) and not vista.corte_visivel
    tela._navegar(1)
    assert tela.indice_folha == 1


# --- o acréscimo de 02/11: a tira de baixo do Dividir ----------------------------------------------
# Samuel: "quando cortar as paginas lá embaxio que foram cortadas vão aparecer como uma só e nas
# paginas que não foram cortadas ainda vão aparecer duplas ainda, mas para ver as paginas que foram
# cortadas vão ter que apertar uma folha só ali embaixo no aplicativo." · gerente: "Na tira de
# baixo do Dividir: a folha 1 foi cortada, então na tira ela aparece como duas miniaturas separadas
# (a contracapa e a capa); as folhas 2 a 70 ainda não foram cortadas, então continuam como uma
# miniatura dupla cada; [...] É isso?" → "isso".

def _imagens_da_tira(tela) -> list[np.ndarray]:
    """O que cada miniatura da tira mostra (espera as folhas chegarem do PDF)."""
    tira = tela.tira
    _esperar(lambda: all(m._pixmap is not None for m in tira._miniaturas), motivo="as miniaturas")
    return [_pixmap_bgr(m._pixmap) for m in tira._miniaturas]


@precisa_da_dll
def test_d601_tira_do_dividir_folha_dividida_vira_duas_miniaturas(janela, tmp_path):
    """Acréscimo da D-601: antes de dividir, a tira do Dividir tem uma miniatura dupla por
    folha (3). "dividir esta" na folha 1 → 4 miniaturas: a da esquerda (com o quadrado) e a da
    direita, cada uma mais estreita que a folha dupla, e as folhas 2 e 3 duplas, como antes.
    Clicar na miniatura da direita da folha 1 → a tela vai a essa página (no "Uma página",
    só a metade da direita); clicar na da folha 2 → a folha 2 inteira. A miniatura escolhida
    é a da página da vez. O ANTIGO SAIU: a tira do Dividir tinha sempre uma miniatura por folha."""
    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir_dividida(janela, tmp_path)
    projeto, tira = janela.projeto, tela.tira
    antes = _imagens_da_tira(tela)
    assert len(antes) == 3
    dupla = antes[0].shape[1]

    tela.botao_nao_dividir.click()                     # "dividir esta" na folha 1
    _assentar(10)
    depois = _imagens_da_tira(tela)
    assert len(depois) == 4, "a folha dividida vira duas miniaturas"
    esquerda, direita, folha2, folha3 = depois
    assert esquerda.shape[1] < 0.7 * dupla and direita.shape[1] < 0.7 * dupla
    assert folha2.shape[1] == dupla and folha3.shape[1] == dupla    # as não divididas: duplas
    assert _tem_o_quadrado(esquerda) and not _tem_o_quadrado(direita)
    assert tira._miniaturas[0].selecionada                         # a página da vez: a esquerda

    tira.selecionada.emit(1)                           # clicar na miniatura da direita
    assert tela.indice_folha == 0 and projeto.paginas[tela.indice_pagina].metade == "direita"
    assert tira._miniaturas[1].selecionada and not tira._miniaturas[0].selecionada
    _f, _e, metade_direita = _partes(tela)
    assert _igual(_na_tela(tela), metade_direita)
    tira.selecionada.emit(2)                           # a folha 2 (não dividida)
    assert tela.indice_folha == 1
    folha, _e, _d = _partes(tela)
    assert _igual(_na_tela(tela), folha) and not tela.visualizadores[ABA_CORTE].corte_visivel

    tela._navegar(-1)                                  # a seta acompanha a tira
    assert tira._miniaturas[1].selecionada


@precisa_da_dll
def test_d601_tira_do_dividir_acompanha_a_linha_e_o_juntar(janela, tmp_path):
    """Acréscimo da D-601: no "Duas lado a lado", arrastar a linha da folha 1 para 30% → a
    miniatura da esquerda fica mais estreita que a da direita (sem ler o livro de novo);
    "não dividir esta" → a folha 1 volta a ser uma miniatura dupla (3 ao todo)."""
    from ui.tela_conferir import ABA_CORTE
    from ui.widgets.paginas_rolando import DUAS

    tela = _no_dividir_dividida(janela, tmp_path)
    tela.botao_nao_dividir.click()                     # "dividir esta"
    _imagens_da_tira(tela)
    tela.botoes_mostrar[DUAS].click()
    tela.visualizadores[ABA_CORTE].corte_movido.emit(0.3)
    esquerda, direita = _imagens_da_tira(tela)[:2]
    assert esquerda.shape[1] < 0.6 * direita.shape[1]
    assert len(tela.tira._miniaturas) == 4

    tela.botao_nao_dividir.click()                     # "não dividir esta"
    _assentar(10)
    imagens = _imagens_da_tira(tela)
    assert len(imagens) == 3 and imagens[0].shape[1] == imagens[1].shape[1]
