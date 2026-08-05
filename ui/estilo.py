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
QScrollBar:horizontal {{ height: 12px; background: {FUNDO_DESABILITADO}; border-radius: 6px; }}
QScrollBar::handle:horizontal {{ background: {TEXTO}; border-radius: 6px; min-width: 40px; }}
QScrollBar:vertical {{ width: 12px; background: {FUNDO_DESABILITADO}; border-radius: 6px; }}
QScrollBar::handle:vertical {{ background: {TEXTO}; border-radius: 6px; min-height: 40px; }}
QScrollBar::handle:horizontal:hover, QScrollBar::handle:vertical:hover {{ background: black; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QToolTip {{
    background: {TEXTO}; color: white; border: none; padding: 6px 9px; border-radius: 5px;
}}
"""
