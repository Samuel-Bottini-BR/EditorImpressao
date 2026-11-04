"""Prova de comportamento da D-609 (04/11/2026): no Dividir, a linha azul se arrasta já na folha
dupla ainda inteira, e o "dividir esta" corta onde ela ficou.

Samuel, no Gradus Primus, folha 2 ainda inteira, "Uma página", linha azul tracejada na lombada
(print `relatorios/testes-guiados/2026-10-29-automatico/a-54-dividir-folha-2-inteira-linha-nao-
arrasta.png`): "não consigo mover a linha azul manualmente." · pergunta: "Quer poder arrastar a
linha já na folha inteira, antes de dividir, e o "dividir esta" cortar onde você deixou?" → "Sim".
Livro de decisões: "Na folha dupla ainda inteira, a linha azul pode ser arrastada com o mouse (em
"Uma página" e em "Duas lado a lado"); "dividir esta" corta onde a linha ficou." Responde a
pergunta `d602-arrastar` da Central.

O que já estava escolhido e testado e continua (D-605): sem arrastar, "dividir esta" corta na linha
do motor (D-602); a folha de uma página só fica sem linha (D-602); "usar em todas" copia a linha
desta folha (D-090); trocar o motor refaz a conta (D-606); depois de mexer, as setas passam de
folha (D-608); a folha juntada volta como estava (D-498).

O que se mede: o arrasto feito com o mouse na vista do Dividir (apertar, mover, soltar, como na
janela de verdade), o projeto (folhas divididas, onde, as páginas), o Histórico (desfazer e
refazer devolvem tudo igual: páginas, linha, avisos, "com dúvida"). O ANTIGO SAIU: no código de
antes (e17410fe) a linha da folha inteira era só para ver (corte_arrastavel False) e o arrasto não
mudava nada; os testes de reversão falham lá.

Livros sintéticos: o livro aberto com a dobra FORA do meio (a 44% da largura, como em
test_decisoes_dividir_linha.py) e uma folha em pé (uma página só).
"""

from __future__ import annotations

import json
import dataclasses
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

DOBRA = 600 / (600 + 760)            # onde o motor acha a dobra do livro aberto sintético (0,441)
ARRASTADA = 0.36                     # para onde a pessoa arrasta a linha (longe da dobra)


def _aberto_torto() -> np.ndarray:
    return np.concatenate([_pagina(600), _pagina(760)], axis=1)


def _em_pe() -> np.ndarray:
    return _pagina(600, 840)


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


def _no_dividir(janela, tmp_path, folhas, mostrar=None):
    """Abrir o livro (nada dividido), escolher o Dividir (de fábrica "Uma página"), folha 1."""
    from ui.tela_conferir import ABA_CORTE

    janela.resize(1400, 900)
    janela.show()
    janela.activateWindow()
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", folhas))
    tela = janela.tela_conferir
    tela.escolher_ferramenta("dividir")
    tela._ir_para(0)
    if mostrar is not None:
        tela.botoes_mostrar[mostrar].click()
    assert tela.aba_atual == ABA_CORTE
    assert not any(f.dividir for f in janela.projeto.folhas), "ao abrir, nada dividido"
    _linha_lida(tela)
    return tela


def _linha_lida(tela) -> None:
    """Espera a conta do motor na folha da vez (roda por trás) e a imagem na vista."""
    from ui.tela_conferir import ABA_CORTE

    vista = tela.visualizadores[ABA_CORTE]
    _assentar(5)
    _esperar(lambda: not getattr(vista, "lendo_a_linha", False), motivo="a conta do motor")
    tela.atualizar()
    _esperar(lambda: vista._pixmap is not None and not vista.carregando
             and vista._area.width() > 50, motivo="a folha na vista")
    _assentar(3)


def _arrastar_com_o_mouse(tela, para: float) -> None:
    """O que a pessoa faz: aperta o botão esquerdo em cima da linha azul, leva o mouse até
    `para` (fração da largura da folha) e solta."""
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest

    from ui.tela_conferir import ABA_CORTE

    vista = tela.visualizadores[ABA_CORTE]
    area = vista._area
    y = int(area.center().y())
    x0 = int(area.left() + area.width() * vista.posicao_corte)
    x1 = int(area.left() + area.width() * para)
    QTest.mousePress(vista, Qt.LeftButton, Qt.NoModifier, QPoint(x0, y))
    meio = (x0 + x1) // 2
    QTest.mouseMove(vista, QPoint(meio, y))
    QTest.mouseMove(vista, QPoint(x1, y))
    QTest.mouseRelease(vista, Qt.LeftButton, Qt.NoModifier, QPoint(x1, y))
    _assentar(5)


def _paginas_da_folha(projeto, f: int) -> list:
    return [p.metade for p in projeto.paginas if p.folha == f]


def _foto(tela) -> dict:
    """Tudo o que o desfazer/refazer tem de devolver igual: as páginas (inteiras), as folhas,
    a linha que a vista mostra (onde, se aparece, se arrasta), os avisos e o "com dúvida"."""
    from core import avisos
    from ui.tela_conferir import ABA_CORTE

    projeto = tela.projeto
    vista = tela.visualizadores[ABA_CORTE]
    return {
        # json ida e volta: a tupla e a lista do mesmo valor contam iguais (o desfazer devolve
        # as páginas do jeito que o projeto.json as grava)
        "paginas": json.loads(json.dumps([dataclasses.asdict(p) for p in projeto.paginas])),
        "folhas": json.loads(json.dumps([dataclasses.asdict(f) for f in projeto.folhas])),
        "linha": (round(vista.posicao_corte, 3), vista.corte_visivel, vista.corte_arrastavel),
        "com_duvida": avisos.quantas_com_duvida(projeto),
        "botao": tela.botao_nao_dividir.text(),
    }


def _diferencas(a, b, caminho: str = "") -> list[str]:
    """Onde duas fotos (_foto) diferem, campo por campo (vazio = iguais)."""
    if isinstance(a, dict) and isinstance(b, dict):
        saida = []
        for k in sorted(set(a) | set(b), key=str):
            saida += _diferencas(a.get(k), b.get(k), f"{caminho}.{k}")
        return saida
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        saida = []
        for i, (x, y) in enumerate(zip(a, b)):
            saida += _diferencas(x, y, f"{caminho}[{i}]")
        return saida
    return [] if a == b else [f"{caminho}: {a!r} != {b!r}"]


def _em_branco_medido(tela) -> None:
    _assentar(5)
    tarefa = getattr(tela, "_tarefa_do_em_branco", None)
    if tarefa is not None:
        tarefa.wait(60000)
    _assentar(10)


def _desfazer(tela) -> None:
    tela.desfazer()
    _em_branco_medido(tela)
    _linha_lida(tela)


def _refazer(tela) -> None:
    tela.refazer()
    _em_branco_medido(tela)
    _linha_lida(tela)


# --- 1. a linha se arrasta na folha inteira (o pedido do a-54) ---------------------------------

@pytest.mark.parametrize("mostrar", ["uma", "duas"])
def test_reversao_d609_linha_se_arrasta_na_folha_dupla_inteira(janela, tmp_path, mostrar):
    """D-609, print a-54 ("não consigo mover a linha azul manualmente."): folha dupla ainda
    inteira, em "Uma página" e em "Duas lado a lado" → a linha azul tem a pega "arraste" e,
    arrastada com o mouse, fica onde a pessoa soltou; nada é cortado (a folha continua uma
    página só) e o arrasto é UMA ação do desfazer. No código de antes (e17410fe) a linha era
    só para ver (corte_arrastavel False) e o arrasto não mudava nada: este teste falha lá."""
    from ui.tela_conferir import ABA_CORTE
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()],
                       mostrar=UMA if mostrar == "uma" else DUAS)
    projeto, vista = janela.projeto, tela.visualizadores[ABA_CORTE]
    assert vista.corte_visivel and vista.posicao_corte == pytest.approx(DOBRA, abs=0.03)
    assert vista.corte_arrastavel, "a linha da folha inteira tem a pega e se arrasta (D-609)"
    _arrastar_com_o_mouse(tela, ARRASTADA)
    assert vista.posicao_corte == pytest.approx(ARRASTADA, abs=0.01), "a linha ficou onde soltou"
    assert vista.corte_visivel and vista.corte_arrastavel
    assert projeto.folhas[0].posicao_corte == pytest.approx(ARRASTADA, abs=0.01)
    assert not projeto.folhas[0].dividir and _paginas_da_folha(projeto, 0) == ["inteira"], \
        "arrastar não corta"
    assert len(janela.acoes.feitas) == 1, "o arrasto é uma ação do desfazer"
    # a linha arrastada fica ao passar de folha e voltar
    tela._navegar(1)
    _linha_lida(tela)
    assert vista.posicao_corte == pytest.approx(DOBRA, abs=0.03), "a outra folha: a do motor"
    tela._navegar(-1)
    _linha_lida(tela)
    assert vista.posicao_corte == pytest.approx(ARRASTADA, abs=0.01)


# --- 2. "dividir esta" corta onde a linha ficou; sem arrastar, na do motor --------------------

def test_reversao_d609_dividir_esta_corta_onde_a_linha_ficou(janela, tmp_path):
    """D-609 ("e o "dividir esta" cortar onde você deixou?" → "Sim"): depois de arrastar, o
    "dividir esta" corta na linha arrastada; a outra folha, sem arrastar, continua cortando na
    linha do motor (D-602). No código de antes o arrasto não mexia e o corte ia para a dobra."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()])
    projeto = janela.projeto
    _arrastar_com_o_mouse(tela, ARRASTADA)
    tela.botao_nao_dividir.click()                         # "dividir esta"
    f = projeto.folhas[0]
    assert f.dividir and f.posicao_corte == pytest.approx(ARRASTADA, abs=0.01)
    assert _paginas_da_folha(projeto, 0) == ["esquerda", "direita"]
    tela._ir_para(1)
    _linha_lida(tela)
    tela.botao_nao_dividir.click()                         # a outra, sem arrastar: a do motor
    assert projeto.folhas[1].dividir
    assert projeto.folhas[1].posicao_corte == pytest.approx(DOBRA, abs=0.03)


def test_d609_folha_juntada_arrastada_volta_como_estava_na_linha_nova(janela, tmp_path):
    """D-498 com a D-609: a folha juntada ("não dividir esta") mostra a linha de antes, que agora
    se arrasta; "dividir esta" devolve as duas páginas como estavam (o "tirar do livro" da
    direita continua) e corta onde a linha ficou."""
    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir(janela, tmp_path, [_aberto_torto()])
    projeto, vista = janela.projeto, tela.visualizadores[ABA_CORTE]
    tela.botao_nao_dividir.click()                         # dividir esta
    direita = next(p for p in projeto.paginas if p.folha == 0 and p.metade == "direita")
    projeto.paginas[direita.indice].apagada = True        # "tirar do livro" na da direita
    tela.botao_nao_dividir.click()                         # não dividir esta
    _linha_lida(tela)
    assert not projeto.folhas[0].dividir
    assert vista.corte_visivel and vista.corte_arrastavel
    _arrastar_com_o_mouse(tela, ARRASTADA)
    tela.botao_nao_dividir.click()                         # dividir esta
    f = projeto.folhas[0]
    assert f.dividir and f.posicao_corte == pytest.approx(ARRASTADA, abs=0.01)
    pags = [p for p in projeto.paginas if p.folha == 0]
    assert [p.metade for p in pags] == ["esquerda", "direita"]
    assert pags[1].apagada, "as páginas voltam como estavam (D-498)"


# --- 3. o arrasto entra no desfazer: Ctrl+Z e Ctrl+Y devolvem tudo igual ----------------------

def test_d609_desfazer_e_refazer_o_arrasto_e_o_corte_devolvem_tudo_igual(janela, tmp_path):
    """Arrastar e "dividir esta" na folha inteira; Ctrl+Z, Ctrl+Y duas vezes: as páginas, as
    folhas, a linha da vista, os avisos e o "com dúvida" voltam exatamente como eram em cada
    passo (o defeito do Ctrl+Y de 03/11 mostrou que isso escapa)."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()])
    _em_branco_medido(tela)
    ao_abrir = _foto(tela)
    _arrastar_com_o_mouse(tela, ARRASTADA)
    _em_branco_medido(tela)
    _linha_lida(tela)
    arrastada = _foto(tela)
    assert arrastada["linha"][0] == pytest.approx(ARRASTADA, abs=0.01)
    tela.botao_nao_dividir.click()
    _em_branco_medido(tela)
    _linha_lida(tela)
    cortada = _foto(tela)
    for _ in range(2):
        _desfazer(tela)
        assert not _diferencas(_foto(tela), arrastada), "Ctrl+Z do corte: a folha inteira, a linha arrastada"
        _desfazer(tela)
        assert not _diferencas(_foto(tela), ao_abrir), "Ctrl+Z do arrasto: a linha do motor"
        assert not janela.acoes.pode_desfazer
        _refazer(tela)
        assert not _diferencas(_foto(tela), arrastada)
        _refazer(tela)
        assert not _diferencas(_foto(tela), cortada)


def test_d609_ctrl_z_do_teclado_volta_a_linha(janela, tmp_path):
    """O Ctrl+Z do teclado (o atalho da janela, como o Samuel faz) depois do arrasto: a linha
    volta para a do motor; Ctrl+Y a leva de novo para onde foi arrastada."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir(janela, tmp_path, [_aberto_torto()])
    vista = tela.visualizadores[ABA_CORTE]
    _arrastar_com_o_mouse(tela, ARRASTADA)
    QTest.keyClick(janela.focusWidget() or janela, Qt.Key_Z, Qt.ControlModifier)
    _linha_lida(tela)
    assert vista.posicao_corte == pytest.approx(DOBRA, abs=0.03)
    QTest.keyClick(janela.focusWidget() or janela, Qt.Key_Y, Qt.ControlModifier)
    _linha_lida(tela)
    assert vista.posicao_corte == pytest.approx(ARRASTADA, abs=0.01)


# --- 4. trocar o motor depois de arrastar refaz a conta (D-606) -------------------------------

def test_d609_trocar_o_motor_depois_de_arrastar_refaz_a_conta(janela, tmp_path):
    """D-606 ("Ele deve fazer a conta novamente com o novo motor"): arrastar, trocar o motor →
    a linha vai para onde o motor novo acha (não fica a arrastada), e "dividir esta" corta nela.
    Ctrl+Z da troca: o motor de antes e a linha arrastada. Voltar ao motor de antes pela lista
    também refaz a conta (a linha do motor, não a arrastada)."""
    from core import dividir_scantailor as ds
    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir(janela, tmp_path, [_aberto_torto()])
    projeto, vista = janela.projeto, tela.visualizadores[ABA_CORTE]
    combo = tela.combo_jeito_da_folha
    agora = combo.currentData()
    outro = next(j for j in ds.JEITOS if j != agora)
    _arrastar_com_o_mouse(tela, ARRASTADA)
    antes_da_troca = _foto(tela)
    combo.setCurrentIndex(combo.findData(outro))
    _linha_lida(tela)
    assert projeto.folhas[0].dividir_como == outro
    lida_nova = tela._linha_do_motor(0)[0]
    assert vista.corte_visivel and vista.corte_arrastavel
    assert vista.posicao_corte == pytest.approx(lida_nova.posicao, abs=1e-3)
    assert vista.posicao_corte == pytest.approx(DOBRA, abs=0.03), "a do motor, não a arrastada"
    _desfazer(tela)
    assert not _diferencas(_foto(tela), antes_da_troca), "Ctrl+Z da troca: o motor e a linha arrastada"
    _refazer(tela)
    tela.botao_nao_dividir.click()
    assert projeto.folhas[0].dividir
    assert projeto.folhas[0].posicao_corte == pytest.approx(lida_nova.posicao, abs=1e-3)
    tela.desfazer()
    _linha_lida(tela)
    combo.setCurrentIndex(combo.findData(agora))          # volta ao motor de antes
    _linha_lida(tela)
    assert vista.posicao_corte == pytest.approx(tela._linha_do_motor(0)[0].posicao, abs=1e-3)
    assert vista.posicao_corte != pytest.approx(ARRASTADA, abs=0.01)


# --- 5. "dividir todas" e "usar em todas" -------------------------------------------------------

def test_d609_dividir_todas_corta_a_arrastada_onde_ficou_e_as_outras_no_motor(janela, tmp_path):
    """"dividir todas": a folha em que a pessoa arrastou a linha é cortada nessa linha; as
    outras, cada uma na linha do motor (D-602). Uma ação só; o Ctrl+Z devolve tudo igual."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto(), _aberto_torto()])
    projeto = janela.projeto
    tela._navegar(1)
    _linha_lida(tela)
    _arrastar_com_o_mouse(tela, ARRASTADA)
    _em_branco_medido(tela)
    _linha_lida(tela)
    arrastada = _foto(tela)
    tela.botao_dividir_todas.click()
    _esperar(lambda: all(f.dividir for f in projeto.folhas), motivo="dividir todas")
    f = projeto.folhas
    assert f[1].posicao_corte == pytest.approx(ARRASTADA, abs=0.01), "a arrastada: onde ficou"
    assert f[0].posicao_corte == pytest.approx(DOBRA, abs=0.03)
    assert f[2].posicao_corte == pytest.approx(DOBRA, abs=0.03)
    assert len(projeto.paginas) == 6
    _desfazer(tela)
    assert not _diferencas(_foto(tela), arrastada)


def test_d609_usar_em_todas_copia_a_linha_arrastada(janela, tmp_path, monkeypatch):
    """D-090: o "usar em todas" continua copiando a linha DESTA folha - na folha inteira, a
    linha arrastada."""
    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto(), _aberto_torto()])
    projeto = janela.projeto
    _arrastar_com_o_mouse(tela, ARRASTADA)
    monkeypatch.setattr(tela, "_escolher_folhas_da_linha", lambda: [0, 1, 2])
    tela._corte_em_todas()
    assert [round(f.posicao_corte, 2) for f in projeto.folhas] == [round(ARRASTADA, 2)] * 3


def test_d609_usar_em_todas_deixa_desmarcada_a_folha_arrastada(janela, tmp_path):
    """D-090 ("quando mudar de um não muda de todas"): a folha inteira em que a linha foi
    arrastada tem linha própria - na janela "Em quais páginas?" do "usar em todas" de outra
    folha, ela vem desmarcada."""
    from core import etapas as E

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()])
    projeto = janela.projeto
    _arrastar_com_o_mouse(tela, ARRASTADA)
    assert E.DIVIDIR in projeto.folhas[0].mexida_a_mao, "linha própria (a marca do D-090)"
    assert E.DIVIDIR not in projeto.folhas[1].mexida_a_mao


# --- 6. a folha de uma página só continua sem linha (D-602) -------------------------------------

def test_d609_folha_de_uma_pagina_continua_sem_linha_e_o_mouse_nao_mexe(janela, tmp_path):
    """D-602 ("só nas duplas"): a folha em pé não mostra linha, e apertar e arrastar o mouse
    nela não muda nada (nenhuma ação no desfazer)."""
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest

    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir(janela, tmp_path, [_em_pe(), _aberto_torto()])
    projeto, vista = janela.projeto, tela.visualizadores[ABA_CORTE]
    assert not vista.corte_visivel
    antes = _foto(tela)
    area = vista._area
    y = int(area.center().y())
    QTest.mousePress(vista, Qt.LeftButton, Qt.NoModifier, QPoint(area.center().x(), y))
    QTest.mouseMove(vista, QPoint(int(area.left() + area.width() * 0.3), y))
    QTest.mouseRelease(vista, Qt.LeftButton, Qt.NoModifier,
                       QPoint(int(area.left() + area.width() * 0.3), y))
    _assentar(5)
    assert not _diferencas(_foto(tela), antes) and not janela.acoes.pode_desfazer
    assert getattr(projeto.folhas[0], "linha_a_mao", None) is None


# --- 7. as setas continuam passando de folha depois de arrastar (D-608) ------------------------

def test_d609_seta_passa_de_folha_depois_de_arrastar(janela, tmp_path):
    """D-608: depois de arrastar a linha com o mouse, a seta → vai para a folha seguinte."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()])
    _arrastar_com_o_mouse(tela, ARRASTADA)
    QTest.keyClick(janela.focusWidget() or janela, Qt.Key_Right)
    _assentar(5)
    assert tela.indice_folha == 1


# --- 8. a linha arrastada vale na folha como estava virada --------------------------------------

def test_d609_girar_a_folha_depois_de_arrastar_mostra_a_linha_do_motor(janela, tmp_path):
    """A linha foi arrastada na folha como ela estava virada: girar a folha mostra a linha do
    motor na folha girada (a arrastada não vale mais ali); o Ctrl+Z do giro devolve a
    arrastada."""
    from ui.tela_conferir import ABA_CORTE

    tela = _no_dividir(janela, tmp_path, [_aberto_torto()])
    vista = tela.visualizadores[ABA_CORTE]
    _arrastar_com_o_mouse(tela, ARRASTADA)
    from core.girar import GIRO_MEIA_VOLTA

    tela._girar_folhas(GIRO_MEIA_VOLTA, so_esta=True)
    _linha_lida(tela)
    lida = tela._linha_do_motor(0)[0]
    assert vista.posicao_corte == pytest.approx(lida.posicao, abs=1e-3)
    assert vista.posicao_corte != pytest.approx(ARRASTADA, abs=0.01)
    tela.desfazer()
    _linha_lida(tela)
    assert vista.posicao_corte == pytest.approx(ARRASTADA, abs=0.01)


# --- D-610: dividir em "Duas lado a lado" passa a vista para "Uma página" --------------------
# Samuel, 04/11/2026 (print a-56, Gradus folha 1 dividida em "Duas lado a lado"): "quando eu
# dividir uma folha que estiver em duas lado a lado ela tem que ir para opção uma pagina, se não
# quando eu usar seta ela vai pular uma folha." Livro de decisões: "No Dividir, ao dividir uma
# folha ("dividir esta"; e "dividir todas") com a vista em "Duas lado a lado", a vista passa
# sozinha para "Uma página", para a seta andar uma página por vez sem pular folha. Mais nova que
# a D-601 (lá a vista "Duas lado a lado" ficava)."

def test_reversao_d610_dividir_esta_em_duas_lado_a_lado_passa_para_uma_pagina(janela, tmp_path):
    """D-610 (a-56): folha 1 inteira em "Duas lado a lado" → "dividir esta" → a vista passa para
    "Uma página" (o botão da barra também), aparece a metade esquerda; a seta → anda UMA página
    (a metade direita da mesma folha) e a seguinte vai à folha 2, sem pular. No código de antes
    (e17410fe) a vista ficava em "Duas lado a lado" e a seta pulava para a folha 2: falha lá."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto(), _aberto_torto()],
                       mostrar=DUAS)
    projeto = janela.projeto
    assert tela.mostrar == DUAS
    tela.botao_nao_dividir.click()                         # "dividir esta"
    _assentar(5)
    assert projeto.folhas[0].dividir
    assert tela.mostrar == UMA and tela.botoes_mostrar[UMA].isChecked(), "foi para Uma página"
    assert tela._metade_no_dividir() == "esquerda"
    QTest.keyClick(janela.focusWidget() or janela, Qt.Key_Right)
    _assentar(5)
    assert (tela.indice_folha, tela._metade_no_dividir()) == (0, "direita"), "uma página por vez"
    QTest.keyClick(janela.focusWidget() or janela, Qt.Key_Right)
    _assentar(5)
    assert tela.indice_folha == 1, "não pulou a folha 2"


def test_reversao_d610_dividir_todas_em_duas_lado_a_lado_passa_para_uma_pagina(janela, tmp_path):
    """D-610 ("e "dividir todas""): em "Duas lado a lado", "dividir todas" → "Uma página"."""
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()], mostrar=DUAS)
    projeto = janela.projeto
    tela.botao_dividir_todas.click()
    _esperar(lambda: all(f.dividir for f in projeto.folhas), motivo="dividir todas")
    _assentar(5)
    assert tela.mostrar == UMA and tela.botoes_mostrar[UMA].isChecked()


def test_d610_arrastar_em_duas_lado_a_lado_nao_troca_a_vista(janela, tmp_path):
    """D-609 com a D-610: na folha inteira, em "Duas lado a lado", arrastar a linha continua
    possível e a vista NÃO troca (só troca ao cortar); "juntar"/"não dividir esta" também não
    troca. Em "Uma página", dividir continua em "Uma página"."""
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _no_dividir(janela, tmp_path, [_aberto_torto(), _aberto_torto()], mostrar=DUAS)
    projeto = janela.projeto
    _arrastar_com_o_mouse(tela, ARRASTADA)
    assert tela.mostrar == DUAS and not projeto.folhas[0].dividir
    tela.botao_nao_dividir.click()                         # dividir esta → Uma página
    assert tela.mostrar == UMA
    assert projeto.folhas[0].posicao_corte == pytest.approx(ARRASTADA, abs=0.01)
    tela.botoes_mostrar[DUAS].click()
    tela.botao_nao_dividir.click()                         # não dividir esta: a vista fica
    assert not projeto.folhas[0].dividir and tela.mostrar == DUAS
