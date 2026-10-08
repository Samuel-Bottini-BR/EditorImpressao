"""Cores, fontes e folha de estilo, nos três temas do programa.

Regra do projeto: nada de emoji em rotulo. A versão anterior quebrou no Windows
por causa disso. Onde faria falta um icone, usamos texto ou desenho vetorial.

TEMAS (layout, rodada 7, decidido pelo Samuel em 06/10/2026): ficam os três,
escuro, cinza e claro; o de fábrica é o CINZA. As cores são as do protótipo
de layout (pasta layout\\prototipo, telas 13-rodada7-tema-*), que vieram do
protótipo de 28/09. A troca fica no menu Ver > Tema (lugar provisório: onde a
troca mora ainda não foi decidido; pode ir para as Configurações).

Como as cores chegam às telas:
  - a folha de estilo (folha()) é montada a partir do tema da vez; a janela a
    aplica ao abrir e de novo quando o tema muda (definir_tema);
  - os nomes antigos (AZUL, TEXTO, TEXTO_FRACO, ...) continuam existindo, e são
    acertados a cada troca de tema. Quem pinta à mão (paintEvent) deve ler
    `estilo.AZUL` (ou cor("azul")) NA HORA de pintar, e não guardar o valor
    na importação: `from ui.estilo import AZUL` congela a cor do tema que
    estava valendo quando o módulo foi importado;
  - quem põe cor num setStyleSheet próprio deve preferir um objectName com a
    regra aqui na folha, para a troca de tema pegar sem nada a mais.

O tema escolhido fica num arquivo pequeno na pasta de dados do programa
(tema.json, ao lado do configuracoes.json): o configuracoes.py só guarda as
chaves que ele conhece, e ele não é da tela (pedido para a gerente: pôr
"tema" nos PADROES dele, e então este arquivo pode sair).

Seguro mudar: as cores de cada tema. Arriscado: tirar um dos nomes antigos
(alguma tela ainda usa) ou o tamanho das letras (as telas foram medidas para
caber em 1280 x 657).
"""

from __future__ import annotations

import json

# ---------------------------------------------------------------------------
# os três temas
# ---------------------------------------------------------------------------
# Papéis (os mesmos nomes do protótipo):
#   fora     moldura mais escura (atrás da página, fora do programa)
#   app      fundo da janela          bar/bar2  faixas (menus, tira)
#   painel   fundo dos painéis         cabeca    cabeçalho de painel
#   tela     fundo atrás da página (área da imagem)
#   linha    risco entre faixas        sep       borda de botão e caixa
#   texto    letra comum               forte     letra de destaque
#   fraco    letra secundária          apagado   letra terciária
#   botao    fundo de botão            botao_h   botão com o mouse em cima
#   linha_f  fundo de item de lista    linha_b   borda do item
#   icone    traço dos ícones          link      azul de link
#   aviso    laranja de aviso          aviso_f   fundo de aviso   aviso_b  borda
#   ok       verde                     sel       fundo do escolhido
#   rolagem  alça da barra de rolagem  rolagem_f trilho dela
#   azul     azul de ação              azul_e    azul apertado
#   verm     vermelho (apagar)
TEMAS: dict[str, dict[str, str]] = {
    "escuro": {
        "fora": "#141517", "app": "#1E1F22", "bar": "#1A1B1E", "bar2": "#232428",
        "painel": "#26282C", "cabeca": "#2C2E33", "tela": "#17181A", "linha": "#303237",
        "sep": "#3A3D43", "texto": "#E4E4E1", "forte": "#FFFFFF", "fraco": "#A3A6AC",
        "apagado": "#868990", "botao": "#34373D", "botao_h": "#3E4148", "linha_f": "#2C2E33",
        "linha_b": "#3C3F46", "icone": "#B9BCC2", "link": "#7FB0FF", "aviso": "#F0A55C",
        "aviso_f": "#33281D", "aviso_b": "#6E4E2E", "ok": "#7FD49A", "sel": "#2F3A52",
        "rolagem": "#4A4D54", "rolagem_f": "#1A1B1E", "azul": "#2F6FE0", "azul_e": "#2459B8",
        "verm": "#E8766B", "desligado": "#6B6E75",
    },
    "cinza": {
        "fora": "#202020", "app": "#3A3A3A", "bar": "#333333", "bar2": "#404040",
        "painel": "#454545", "cabeca": "#4E4E4E", "tela": "#2B2B2B", "linha": "#2E2E2E",
        "sep": "#5C5C5C", "texto": "#EDEDED", "forte": "#FFFFFF", "fraco": "#C4C4C4",
        "apagado": "#ABABAB", "botao": "#555555", "botao_h": "#606060", "linha_f": "#4E4E4E",
        "linha_b": "#5E5E5E", "icone": "#D0D0D0", "link": "#9CC2FF", "aviso": "#FFB672",
        "aviso_f": "#4A3E30", "aviso_b": "#8E6A44", "ok": "#8FE0A8", "sel": "#475670",
        "rolagem": "#6A6A6A", "rolagem_f": "#333333", "azul": "#2F6FE0", "azul_e": "#2459B8",
        "verm": "#E8766B", "desligado": "#808080",
    },
    "claro": {
        "fora": "#D9D7D1", "app": "#F1F0EC", "bar": "#F7F6F3", "bar2": "#FFFFFF",
        "painel": "#FBFAF8", "cabeca": "#EFEEEA", "tela": "#D6D4CE", "linha": "#DDDBD4",
        "sep": "#CFCDC6", "texto": "#26272A", "forte": "#111214", "fraco": "#5C5E65",
        "apagado": "#6C6E75", "botao": "#F0EFEB", "botao_h": "#E4E3DE", "linha_f": "#FFFFFF",
        "linha_b": "#D8D6CF", "icone": "#4A4C52", "link": "#1F5BC7", "aviso": "#B45309",
        "aviso_f": "#FBEBD9", "aviso_b": "#E3B27A", "ok": "#1E7A3C", "sel": "#DCE7FB",
        "rolagem": "#B5B3AC", "rolagem_f": "#EFEEEA", "azul": "#2F6FE0", "azul_e": "#2459B8",
        "verm": "#B91C1C", "desligado": "#A8A6A0",
    },
}
TEMA_DE_FABRICA = "cinza"
NOMES_DOS_TEMAS = {"escuro": "Escuro", "cinza": "Cinza", "claro": "Claro"}

_tema = TEMA_DE_FABRICA
_CORES: dict[str, str] = dict(TEMAS[_tema])


def cor(papel: str) -> str:
    """A cor de um papel (ver a tabela acima) no tema da vez."""
    return _CORES[papel]


def tema_atual() -> str:
    """O nome do tema que está valendo ("escuro", "cinza" ou "claro")."""
    return _tema


# ---------------------------------------------------------------------------
# os nomes antigos, acertados a cada troca de tema
# ---------------------------------------------------------------------------
# Eles vinham do tema claro de antes (AZUL_CLARO era um fundo azul-clarinho,
# LARANJA_CLARO um fundo laranja-clarinho). Agora cada um aponta para o papel
# que fazia: AZUL_CLARO = fundo do escolhido, LARANJA_CLARO = fundo de aviso.
AZUL = AZUL_CLARO = AZUL_ESCURO = LARANJA = LARANJA_CLARO = VERDE = VERMELHO = ""
TEXTO = TEXTO_FRACO = BORDA = FUNDO = FUNDO_CARTAO = FUNDO_DESABILITADO = ""
FOLHA_DE_ESTILO = ""


def _acertar_os_nomes() -> None:
    """Copia as cores do tema da vez para os nomes antigos e remonta a folha."""
    global AZUL, AZUL_CLARO, AZUL_ESCURO, LARANJA, LARANJA_CLARO, VERDE, VERMELHO
    global TEXTO, TEXTO_FRACO, BORDA, FUNDO, FUNDO_CARTAO, FUNDO_DESABILITADO
    global FOLHA_DE_ESTILO, _CAIXINHA_COM_QUADRADO
    c = _CORES
    AZUL, AZUL_CLARO, AZUL_ESCURO = c["azul"], c["sel"], c["azul_e"]
    LARANJA, LARANJA_CLARO = c["aviso"], c["aviso_f"]
    VERDE, VERMELHO = c["ok"], c["verm"]
    TEXTO, TEXTO_FRACO, BORDA = c["texto"], c["fraco"], c["sep"]
    FUNDO, FUNDO_CARTAO, FUNDO_DESABILITADO = c["app"], c["botao"], c["bar2"]
    _CAIXINHA_COM_QUADRADO = None   # a caixinha com quadrado tem cor do tema
    FOLHA_DE_ESTILO = _montar_a_folha(c)


def definir_tema(nome: str, guardar: bool = True) -> str:
    """Troca o tema (nome desconhecido vira o de fábrica), guarda a escolha e
    devolve a folha de estilo nova, para a janela aplicar."""
    global _tema, _CORES
    if nome not in TEMAS:
        nome = TEMA_DE_FABRICA
    _tema = nome
    _CORES = dict(TEMAS[nome])
    _acertar_os_nomes()
    if guardar:
        _gravar_o_tema(nome)
    return FOLHA_DE_ESTILO


def folha() -> str:
    """A folha de estilo do tema da vez (use esta, e não a constante
    importada, em janela ou caixa criada depois de uma troca de tema)."""
    return FOLHA_DE_ESTILO


def _arquivo_do_tema():
    """Onde a escolha do tema fica guardada (pasta de dados do programa)."""
    from historico import pasta_de_dados

    return pasta_de_dados() / "tema.json"


def tema_guardado() -> str:
    """O tema que a pessoa escolheu da última vez, ou o de fábrica. Nunca
    quebra: arquivo sumido ou estragado vira o de fábrica."""
    try:
        arquivo = _arquivo_do_tema()
        if arquivo.is_file():
            nome = json.loads(arquivo.read_text(encoding="utf-8")).get("tema")
            if nome in TEMAS:
                return nome
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return TEMA_DE_FABRICA


def _gravar_o_tema(nome: str) -> None:
    """Grava a escolha do tema. Falha em silêncio (não é essencial)."""
    try:
        arquivo = _arquivo_do_tema()
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        arquivo.write_text(json.dumps({"tema": nome}), encoding="utf-8")
    except OSError:
        pass


def carregar_o_tema_guardado() -> str:
    """Põe para valer o tema guardado (ao abrir o programa) e devolve a folha."""
    return definir_tema(tema_guardado(), guardar=False)


def _montar_a_folha(c: dict[str, str]) -> str:
    """A folha de estilo do programa, com as cores do tema `c`."""
    return f"""
QWidget {{
    background: {c["app"]};
    color: {c["texto"]};
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 14px;
}}
QMenuBar {{ background: {c["bar"]}; border-bottom: 1px solid {c["linha"]}; }}
QMenuBar::item {{ background: transparent; padding: 6px 10px; }}
QMenuBar::item:selected {{ background: {c["botao_h"]}; }}
QMenuBar::item:disabled {{ color: {c["desligado"]}; }}
QMenu {{ background: {c["painel"]}; border: 1px solid {c["sep"]}; padding: 4px; }}
QMenu::item {{ padding: 6px 26px 6px 22px; border-radius: 4px; }}
QMenu::item:selected {{ background: {c["sel"]}; color: {c["forte"]}; }}
QMenu::item:disabled {{ color: {c["desligado"]}; }}
QMenu::separator {{ height: 1px; background: {c["linha"]}; margin: 4px 6px; }}

QLabel#titulo {{ font-size: 26px; font-weight: 600; color: {c["forte"]}; }}
QLabel#subtitulo {{ font-size: 17px; color: {c["fraco"]}; }}
QLabel#secao {{ font-size: 19px; font-weight: 600; color: {c["forte"]}; }}
QLabel#fraco {{ color: {c["fraco"]}; }}
QLabel#atalhos {{ color: {c["fraco"]}; font-size: 12px; }}
QLabel#avisoFraco {{ color: {c["aviso"]}; font-size: 12px; }}
QLabel#avisoErro {{ color: {c["verm"]}; }}
QLabel#separador {{ color: {c["sep"]}; margin: 0 8px; }}

QFrame#cartao {{
    background: {c["painel"]};
    border: 1px solid {c["sep"]};
    border-radius: 10px;
}}

QFrame#faixaInfo {{
    background: {c["bar2"]};
    border: 1px solid {c["sep"]};
    border-radius: 8px;
}}
QFrame#faixaAlerta {{
    background: {c["aviso_f"]};
    border: 1px solid {c["aviso_b"]};
    border-radius: 8px;
}}

QPushButton {{
    background: {c["botao"]};
    color: {c["texto"]};
    border: 1px solid {c["sep"]};
    border-radius: 8px;
    padding: 9px 16px;
}}
QPushButton:hover {{ background: {c["botao_h"]}; }}
QPushButton:pressed {{ background: {c["sel"]}; }}
QPushButton:disabled {{ color: {c["desligado"]}; background: {c["bar2"]}; border-color: {c["linha"]}; }}

QPushButton#primario {{
    background: {c["azul"]};
    color: white;
    border: none;
    font-size: 16px;
    font-weight: 600;
    padding: 13px 30px;
}}
QPushButton#primario:hover {{ background: {c["azul_e"]}; }}
QPushButton#primario:disabled {{ background: {c["desligado"]}; color: {c["bar2"]}; }}

QPushButton#sugestao {{
    background: {c["aviso"]};
    color: #2A1808;
    border: none;
    font-weight: 600;
}}
QPushButton#sugestao:hover {{ background: {c["aviso_b"]}; color: white; }}

QPushButton#contadorAlerta {{
    background: {c["aviso_f"]};
    color: {c["aviso"]};
    border: 1px solid {c["aviso_b"]};
    font-weight: 600;
}}

/* Botoes que ficam "apertados", como a força do preto */
QPushButton:checked {{
    background: {c["azul"]};
    color: white;
    border-color: {c["azul"]};
    font-weight: 600;
}}

/* Acao principal de uma linha de botões: destaque sem o tamanho do #primario */
QPushButton#acaoPrimaria {{
    background: {c["azul"]};
    color: white;
    border: none;
    font-weight: 600;
}}
QPushButton#acaoPrimaria:hover {{ background: {c["azul_e"]}; }}

/* Acao destrutiva: precisa parecer diferente das outras da mesma linha */
QPushButton#destrutivo {{ color: {c["verm"]}; border-color: {c["verm"]}; background: transparent; }}
QPushButton#destrutivo:hover {{ background: {c["aviso_f"]}; border-color: {c["verm"]}; }}

QLabel#rotuloBloco {{
    color: {c["fraco"]};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}}

QSlider {{ background: transparent; }}
QSlider::groove:horizontal {{ height: 6px; background: {c["sep"]}; border-radius: 3px; }}
QSlider::sub-page:horizontal {{ background: {c["azul"]}; border-radius: 3px; }}
QSlider::handle:horizontal {{
    background: #F2F2F2;
    border: 2px solid {c["azul"]};
    width: 16px;
    margin: -7px 0;
    border-radius: 9px;
}}
QSlider::handle:horizontal:hover {{ background: {c["sel"]}; }}
QSlider::sub-page:horizontal:disabled {{ background: {c["sep"]}; }}
QSlider::handle:horizontal:disabled {{ border-color: {c["sep"]}; }}

QPushButton#plano {{ border: none; background: transparent; color: {c["link"]}; }}
QPushButton#plano:hover {{ text-decoration: underline; background: transparent; }}

QCheckBox {{ spacing: 10px; font-size: 16px; font-weight: 600; background: transparent; }}
QCheckBox::indicator {{ width: 22px; height: 22px; }}
QCheckBox:disabled {{ color: {c["desligado"]}; }}
QLabel:disabled {{ color: {c["desligado"]}; }}

QRadioButton {{ spacing: 8px; background: transparent; }}
/* A bolinha desenhada pela folha: no tema escuro a do Windows sumia (a
   escolhida saía sem bolinha nenhuma, achado no print da etapa 1). */
QRadioButton::indicator {{ width: 14px; height: 14px; border-radius: 9px;
    border: 2px solid {c["fraco"]}; background: {c["bar2"]}; }}
QRadioButton::indicator:checked {{ border: 5px solid {c["azul"]}; background: #FFFFFF; }}
QRadioButton::indicator:disabled {{ border-color: {c["linha"]}; }}
/* Rótulo nunca pinta fundo próprio: no tema escuro, o fundo da janela atrás de
   cada frase dentro de um cartão aparecia como uma faixa escura. */
QLabel {{ background: transparent; }}

QProgressBar {{
    border: 1px solid {c["sep"]};
    border-radius: 8px;
    background: {c["bar2"]};
    height: 22px;
    text-align: center;
}}
QProgressBar::chunk {{ background: {c["azul"]}; border-radius: 7px; }}

QTabBar::tab {{
    background: {c["botao"]};
    color: {c["texto"]};
    border: 1px solid {c["sep"]};
    padding: 10px 22px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 15px;
}}
QTabBar::tab:selected {{ background: {c["azul"]}; color: white; border-color: {c["azul"]}; }}
QTabWidget::pane {{ border: 1px solid {c["sep"]}; border-radius: 8px; background: {c["painel"]}; }}

QComboBox, QSpinBox, QLineEdit, QDoubleSpinBox {{
    background: {c["bar2"]};
    color: {c["texto"]};
    border: 1px solid {c["sep"]};
    border-radius: 6px;
    padding: 6px 10px;
}}
QComboBox QAbstractItemView {{ background: {c["painel"]}; color: {c["texto"]};
    selection-background-color: {c["sel"]}; border: 1px solid {c["sep"]}; }}

QScrollArea {{ border: none; background: transparent; }}
/* Barra de rolagem que se enxerga (pedido do Kaique: "a barra de scrool devia
   ser preta para ficar com visualizacao mais facil"). A alça contrasta com o
   trilho em cada tema, sem virar um risco no meio do trabalho. */
QScrollBar:horizontal {{ height: 12px; background: {c["rolagem_f"]}; border-radius: 6px; }}
QScrollBar::handle:horizontal {{ background: {c["rolagem"]}; border-radius: 6px; min-width: 40px; }}
QScrollBar:vertical {{ width: 12px; background: {c["rolagem_f"]}; border-radius: 6px; }}
QScrollBar::handle:vertical {{ background: {c["rolagem"]}; border-radius: 6px; min-height: 40px; }}
QScrollBar::handle:horizontal:hover, QScrollBar::handle:vertical:hover {{ background: {c["fraco"]}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QToolTip {{
    background: #1E1E1E; color: #F2F2F2; border: 1px solid #555555; padding: 6px 9px; border-radius: 5px;
}}

QMessageBox, QDialog {{ background: {c["app"]}; }}

/* Etapa 2 do layout: a linha dos menus (menus + barra de opções + girar), a
   barra de baixo da tela de trabalho e o fundo atrás da página. */
QWidget#linhaDosMenus {{ background: {c["bar"]}; border-bottom: 1px solid {c["linha"]}; }}
QWidget#linhaDosMenus QMenuBar {{ border: none; }}
QFrame#separadorDosMenus {{ background: {c["sep"]}; }}
QFrame#barraDeBaixo {{ background: {c["bar"]}; border-top: 1px solid {c["linha"]}; }}
QLabel#rotuloDaBarraDeBaixo {{ color: {c["fraco"]}; font-size: 12px; }}
QPushButton#botaoDaBarraDeBaixo {{ background: transparent; border: 1px solid transparent;
    border-radius: 4px; padding: 0px 7px; min-height: 22px; font-size: 16px; color: {c["fraco"]}; }}
QPushButton#botaoDaBarraDeBaixo:hover {{ background: {c["botao_h"]}; }}
QPushButton#botaoDaBarraDeBaixo:disabled {{ color: {c["desligado"]}; background: transparent; }}
QStackedWidget#areaDaPagina {{ background: {c["tela"]}; }}
/* os botões da ferramenta embaixo da página (provisório até a etapa 4): mais
   enxutos, para caber a fila inteira entre a trilha e os painéis */
QStackedWidget#barraDeBotoes QPushButton {{ padding: 5px 10px; font-size: 13px; border-radius: 6px; }}
QStackedWidget#barraDeBotoes QComboBox {{ padding: 4px 8px; font-size: 13px; }}
QStackedWidget#barraDeBotoes QLabel {{ font-size: 13px; }}
QStackedWidget#barraDeBotoes QCheckBox {{ font-size: 13px; }}
"""


# ---------------------------------------------------------------------------
# Caixinha COM QUADRADO (item 1.2, parecer do verificador de 30/09/2026, r06)
# ---------------------------------------------------------------------------
# Na janela de verdade (estilo "windows11" do Qt), a folha de estilo acima faz
# a caixinha DESMARCADA sair sem quadrado nenhum: so o texto, e a pessoa nao
# sabe que ali se clica ("Esta pagina tem foto", "Este livro tem fotos"). A
# marcada sai so com o tique. Esta e a caixinha com quadrado nas duas: borda
# da cor do tema desmarcada; azul com tique branco marcada. Usada, por
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
            f"QCheckBox::indicator {{ width: 16px; height: 16px; border: 2px solid {cor('fraco')};"
            f" border-radius: 4px; background: {cor('bar2')}; }}"
            f" QCheckBox::indicator:checked {{ border-color: {AZUL}; background: {AZUL};{imagem} }}"
            f" QCheckBox::indicator:disabled {{ border-color: {cor('linha')}; background: {cor('bar')}; }}")
    return (f"QCheckBox {{ font-size: {tamanho_da_letra}px; font-weight: normal; spacing: 8px; }} "
            + _CAIXINHA_COM_QUADRADO)


# ---------------------------------------------------------------------------
# estilo próprio de uma peça, que acompanha a troca de tema
# ---------------------------------------------------------------------------

def estilizar(widget, montar) -> None:
    """Põe em `widget` a folha que `montar()` devolve e lembra de refazer a
    cada troca de tema (reaplicar_em_tudo). Use no lugar de
    widget.setStyleSheet(f"... {COR} ...") quando a cor vem do tema: o
    setStyleSheet sozinho congela a cor do tema que valia na hora."""
    widget._estilo_do_tema = montar
    widget.setStyleSheet(montar())


def reaplicar_em_tudo() -> None:
    """Depois de definir_tema: refaz o estilo próprio de cada peça viva que
    usou estilizar(), e pede para todas se pintarem de novo (quem pinta à mão
    lê as cores na hora)."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        return
    for peca in app.allWidgets():
        montar = getattr(peca, "_estilo_do_tema", None)
        if montar is not None:
            try:
                peca.setStyleSheet(montar())
            except RuntimeError:   # a peça já foi destruída pelo Qt
                continue
        peca.update()


# A folha e os nomes antigos já nascem com o tema de fábrica; a janela põe o
# tema guardado para valer ao abrir (carregar_o_tema_guardado).
_acertar_os_nomes()
