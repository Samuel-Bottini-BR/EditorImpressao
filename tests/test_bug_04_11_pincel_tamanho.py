"""Bug de 04/11/2026 (testes guiados, print a-65-pincel-roda-tamanho.png; Samuel: "no modo do
pincel, quando eu giro o scrool ele fica aumentando e diminuindo o tamnho do pincel no painel
direito mas no painel de cima 'tamanho' ele não muda nada").

O que vale (D-600, 02/11, "sim"): a roda sozinha muda o pincel nas ferramentas de marcar. O
defeito: o deslizante "tamanho" da barra de cima não acompanhava; e o caminho contrário (mexer no
"tamanho" de cima) mudava o pincel, mas o número do painel ("Pincel: N% da página") ficava velho.
E escolher o Pincel de novo punha o deslizante no tamanho de fábrica, não no de agora.

O mesmo vale para a "tolerância" da Varinha (a roda também a muda; mesma peça da barra).

Teste de reversão: em `18cb692e` falham; com o conserto passam.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QWheelEvent  # noqa: E402
from PySide6.QtWidgets import QApplication, QSlider  # noqa: E402

from tests.test_decisoes_mover import (  # noqa: E402,F401
    _assentar,
    _esperar,
    _pdf,
    app,
    janela,
    pasta,
)


def _aberto(janela, tmp_path, ferramenta: str):
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf"))
    janela.show()
    tela = janela.tela_conferir
    tela.escolher_ferramenta(ferramenta)
    _assentar()
    editor = tela.editor_selecao
    assert _esperar(lambda: editor._pixmap is not None)
    return tela, editor


def _deslizante(tela) -> QSlider:
    """O deslizante que está na barra de cima agora (o da ferramenta da vez)."""
    barra = tela.barra_opcoes
    vivos = [s for s in barra.findChildren(QSlider) if s.isVisibleTo(barra)]
    assert len(vivos) == 1, vivos
    return vivos[0]


def _roda(editor, passos: int = 1) -> None:
    """A roda do mouse em cima da página (sem Ctrl), como a mão."""
    meio = QPointF(editor.rect().center())
    for _ in range(abs(passos)):
        evento = QWheelEvent(meio, QPointF(editor.mapToGlobal(meio.toPoint())), QPoint(0, 0),
                             QPoint(0, 120 if passos > 0 else -120), Qt.NoButton, Qt.NoModifier,
                             Qt.NoScrollPhase, False)
        QApplication.sendEvent(editor, evento)
    _assentar()


def test_reversao_bug_04_11_a_roda_muda_o_tamanho_de_cima(janela, tmp_path):
    """A roda aumenta o pincel (D-600, fica) e o "tamanho" de cima vai junto; diminuir também."""
    tela, editor = _aberto(janela, tmp_path, "pincel")
    deslizante = _deslizante(tela)
    antes = editor.espessura
    _roda(editor, 5)
    assert editor.espessura > antes * 1.5                        # a roda continua mudando o pincel
    assert deslizante.value() == round(editor.espessura * 1000), (
        f"o tamanho de cima ficou em {deslizante.value()}, o pincel está em {editor.espessura:.4f}")
    _roda(editor, -8)
    assert deslizante.value() == round(editor.espessura * 1000)
    assert f"{editor.espessura * 100:.1f}%" in tela.aviso_marcacao.text()


def test_reversao_bug_04_11_o_tamanho_de_cima_muda_o_pincel_e_o_painel(janela, tmp_path):
    """O caminho contrário: mexer no "tamanho" de cima muda o pincel e o número do painel."""
    tela, editor = _aberto(janela, tmp_path, "pincel")
    _deslizante(tela).setValue(100)
    _assentar()
    assert editor.espessura == pytest.approx(0.100)
    assert "Pincel: 10.0% da página" in tela.aviso_marcacao.text()


def test_reversao_bug_04_11_escolher_o_pincel_de_novo_mostra_o_tamanho_de_agora(janela, tmp_path):
    """Pincel aumentado pela roda, outra ferramenta, Pincel de novo: o "tamanho" de cima mostra o
    tamanho de agora (o pincel não volta sozinho ao de fábrica)."""
    tela, editor = _aberto(janela, tmp_path, "pincel")
    _roda(editor, 6)
    tamanho = editor.espessura
    tela.escolher_ferramenta("retangulo")
    tela.escolher_ferramenta("pincel")
    _assentar()
    assert editor.espessura == pytest.approx(tamanho)
    assert _deslizante(tela).value() == round(tamanho * 1000)


def test_reversao_bug_04_11_varinha_a_roda_muda_a_tolerancia_de_cima(janela, tmp_path):
    """A mesma peça na Varinha: a roda muda a tolerância e a "tolerância" de cima acompanha."""
    tela, editor = _aberto(janela, tmp_path, "varinha")
    antes = editor.tolerancia
    _roda(editor, 4)
    assert editor.tolerancia > antes
    assert _deslizante(tela).value() == editor.tolerancia
