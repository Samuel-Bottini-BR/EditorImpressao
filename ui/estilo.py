"""Cores, fontes e folha de estilo.

Regra do projeto: nada de emoji em rotulo. A versão anterior quebrou no Windows
por causa disso. Onde faria falta um icone, usamos texto ou desenho vetorial.
"""

from __future__ import annotations

AZUL = "#2563eb"
AZUL_CLARO = "#dbeafe"
AZUL_ESCURO = "#1d4ed8"
LARANJA = "#ea580c"
LARANJA_CLARO = "#ffedd5"
VERDE = "#16a34a"
VERMELHO = "#dc2626"

TEXTO = "#1f2937"
TEXTO_FRACO = "#6b7280"
BORDA = "#d1d5db"
FUNDO = "#f9fafb"
FUNDO_CARTAO = "#ffffff"
FUNDO_DESABILITADO = "#e5e7eb"

FOLHA_DE_ESTILO = f"""
QWidget {{
    background: {FUNDO};
    color: {TEXTO};
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 14px;
}}

QLabel#titulo {{ font-size: 26px; font-weight: 600; }}
QLabel#subtitulo {{ font-size: 17px; color: {TEXTO_FRACO}; }}
QLabel#secao {{ font-size: 19px; font-weight: 600; }}
QLabel#fraco {{ color: {TEXTO_FRACO}; }}
QLabel#atalhos {{ color: {TEXTO_FRACO}; font-size: 12px; }}

QFrame#cartao {{
    background: {FUNDO_CARTAO};
    border: 1px solid {BORDA};
    border-radius: 10px;
}}

QFrame#faixaInfo {{
    background: {AZUL_CLARO};
    border: 1px solid {AZUL};
    border-radius: 8px;
}}
QFrame#faixaAlerta {{
    background: {LARANJA_CLARO};
    border: 1px solid {LARANJA};
    border-radius: 8px;
}}

QPushButton {{
    background: {FUNDO_CARTAO};
    border: 1px solid {BORDA};
    border-radius: 8px;
    padding: 9px 16px;
}}
QPushButton:hover {{ background: #f3f4f6; }}
QPushButton:pressed {{ background: #e5e7eb; }}
QPushButton:disabled {{ color: #9ca3af; background: {FUNDO_DESABILITADO}; }}

QPushButton#primario {{
    background: {AZUL};
    color: white;
    border: none;
    font-size: 16px;
    font-weight: 600;
    padding: 13px 30px;
}}
QPushButton#primario:hover {{ background: {AZUL_ESCURO}; }}
QPushButton#primario:disabled {{ background: #9ca3af; color: #f3f4f6; }}

QPushButton#sugestao {{
    background: {LARANJA};
    color: white;
    border: none;
    font-weight: 600;
}}
QPushButton#sugestao:hover {{ background: #c2410c; }}

QPushButton#contadorAlerta {{
    background: {LARANJA_CLARO};
    color: {LARANJA};
    border: 1px solid {LARANJA};
    font-weight: 600;
}}

/* Botoes que ficam "apertados", como a força do preto */
QPushButton:checked {{
    background: {AZUL};
    color: white;
    border-color: {AZUL};
    font-weight: 600;
}}

/* Acao principal de uma linha de botões: destaque sem o tamanho do #primario */
QPushButton#acaoPrimaria {{
    background: {AZUL};
    color: white;
    border: none;
    font-weight: 600;
}}
QPushButton#acaoPrimaria:hover {{ background: {AZUL_ESCURO}; }}

/* Acao destrutiva: precisa parecer diferente das outras da mesma linha */
QPushButton#destrutivo {{ color: {VERMELHO}; border-color: #fecaca; }}
QPushButton#destrutivo:hover {{ background: #fef2f2; border-color: {VERMELHO}; }}

QLabel#rotuloBloco {{
    color: {TEXTO_FRACO};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}}

QSlider::groove:horizontal {{ height: 6px; background: {BORDA}; border-radius: 3px; }}
QSlider::sub-page:horizontal {{ background: {AZUL}; border-radius: 3px; }}
QSlider::handle:horizontal {{
    background: white;
    border: 2px solid {AZUL};
    width: 16px;
    margin: -7px 0;
    border-radius: 9px;
}}
QSlider::handle:horizontal:hover {{ background: {AZUL_CLARO}; }}

QPushButton#plano {{ border: none; background: transparent; color: {AZUL}; }}
QPushButton#plano:hover {{ text-decoration: underline; background: transparent; }}

QCheckBox {{ spacing: 10px; font-size: 16px; font-weight: 600; }}
QCheckBox::indicator {{ width: 22px; height: 22px; }}

QRadioButton {{ spacing: 8px; }}

QProgressBar {{
    border: 1px solid {BORDA};
    border-radius: 8px;
    background: {FUNDO_CARTAO};
    height: 22px;
    text-align: center;
}}
QProgressBar::chunk {{ background: {AZUL}; border-radius: 7px; }}

QTabBar::tab {{
    background: {FUNDO_CARTAO};
    border: 1px solid {BORDA};
    padding: 10px 22px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 15px;
}}
QTabBar::tab:selected {{ background: {AZUL}; color: white; border-color: {AZUL}; }}
QTabWidget::pane {{ border: 1px solid {BORDA}; border-radius: 8px; background: {FUNDO_CARTAO}; }}

QComboBox, QSpinBox {{
    background: {FUNDO_CARTAO};
    border: 1px solid {BORDA};
    border-radius: 6px;
    padding: 6px 10px;
}}

QScrollArea {{ border: none; background: transparent; }}
/* Barra de rolagem escura, a pedido do Kaique: a de antes era cinza claro
   sobre fundo claro e ele nao a enxergava na tira de miniaturas - "a barra de
   scrool devia ser preta para ficar com visualizacao mais facil". O trilho fica
   claro para o punho se destacar dentro dele. */
/* A alca era {TEXTO}, quase preta: uma barra dessas atravessada no pe da
   tela le como um risco preto no meio do trabalho, e nao como um controle.
   Cinza medio se enxerga igual e nao disputa com a pagina. */
QScrollBar:horizontal {{ height: 12px; background: {FUNDO_DESABILITADO}; border-radius: 6px; }}
QScrollBar::handle:horizontal {{ background: #a8a49e; border-radius: 6px; min-width: 40px; }}
QScrollBar:vertical {{ width: 12px; background: {FUNDO_DESABILITADO}; border-radius: 6px; }}
QScrollBar::handle:vertical {{ background: #a8a49e; border-radius: 6px; min-height: 40px; }}
QScrollBar::handle:horizontal:hover, QScrollBar::handle:vertical:hover {{ background: #7d7a74; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QToolTip {{
    background: {TEXTO}; color: white; border: none; padding: 6px 9px; border-radius: 5px;
}}
"""


# ---------------------------------------------------------------------------
# Caixinha COM QUADRADO (item 1.2, parecer do verificador de 30/09/2026, r06)
# ---------------------------------------------------------------------------
# Na janela de verdade (estilo "windows11" do Qt), a folha de estilo acima faz
# a caixinha DESMARCADA sair sem quadrado nenhum: so o texto, e a pessoa nao
# sabe que ali se clica ("Esta pagina tem foto", "Este livro tem fotos"). A
# marcada sai so com o tique. Esta e a caixinha com quadrado nas duas: borda
# cinza e fundo branco desmarcada; azul com tique branco marcada. Usada, por
# enquanto, so nas caixinhas do grupo "Gravuras e fotos" e na da aba Marcar;
# as outras caixinhas do programa continuam como estao (mudar todas e decisao
# de tela: Lista de bugs de 30/09).
#
# O tique e desenhado uma vez, com o proprio Qt, num PNG na pasta temporaria
# (a folha de estilo so aceita imagem por arquivo, e assim nada precisa ir
# junto no instalador). Se nao der para gravar, a marcada fica azul cheia,
# sem tique - continua dando para ver o que esta marcado. Seguro mudar: as
# cores. Chamar so depois de existir a QApplication.

_CAIXINHA_COM_QUADRADO: str | None = None


def _desenhar_o_tique() -> str | None:
    """Grava o tique branco (24 x 24) num PNG temporario e devolve o caminho
    com barras normais (o que a folha de estilo quer), ou None."""
    try:
        import tempfile
        from pathlib import Path

        from PySide6.QtCore import QPointF, Qt
        from PySide6.QtGui import QColor, QPainter, QPen, QPixmap

        caminho = Path(tempfile.gettempdir()) / "editor_impressao_tique.png"
        if not caminho.is_file():
            imagem = QPixmap(48, 48)
            imagem.fill(Qt.transparent)
            pintor = QPainter(imagem)
            pintor.setRenderHint(QPainter.Antialiasing)
            caneta = QPen(QColor("white"), 6.5)
            caneta.setCapStyle(Qt.RoundCap)
            caneta.setJoinStyle(Qt.RoundJoin)
            pintor.setPen(caneta)
            pintor.drawPolyline([QPointF(10.5, 25.5), QPointF(20, 35), QPointF(38, 14)])
            pintor.end()
            if not imagem.save(str(caminho), "PNG"):
                return None
        return caminho.as_posix()
    except Exception:  # noqa: BLE001 - sem o tique, a caixinha marcada fica azul cheia
        return None


def estilo_da_caixinha_com_quadrado(tamanho_da_letra: int = 14) -> str:
    """A folha de estilo de uma caixinha com quadrado (ver acima), para
    QCheckBox.setStyleSheet."""
    global _CAIXINHA_COM_QUADRADO
    if _CAIXINHA_COM_QUADRADO is None:
        tique = _desenhar_o_tique()
        imagem = f" image: url({tique});" if tique else ""
        _CAIXINHA_COM_QUADRADO = (
            "QCheckBox::indicator { width: 16px; height: 16px; border: 2px solid #9ca3af;"
            " border-radius: 4px; background: white; }"
            f" QCheckBox::indicator:checked {{ border-color: {AZUL}; background: {AZUL};{imagem} }}"
            " QCheckBox::indicator:disabled { border-color: #d1d5db; background: #f3f4f6; }")
    return (f"QCheckBox {{ font-size: {tamanho_da_letra}px; font-weight: normal; spacing: 8px; }} "
            + _CAIXINHA_COM_QUADRADO)
