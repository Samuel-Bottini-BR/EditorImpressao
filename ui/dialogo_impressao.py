"""A janela "Montar para imprimir" e a confirmação do "imprimir agora".

MONTAR PARA IMPRIMIR (item 2.6; refeita na etapa 9a da obra de 26/10/2026)
    É a janela de imprimir do UPDF dentro do programa, como o Samuel pediu em
    14/10/2026 (D-315: "Quero TODAS essas opções dentro do programa, para ter
    bastante escolha"). Abre da tela "Ficou pronto!" e trabalha sobre o PDF
    que acabou de ser gerado: grava um arquivo à parte com as folhas prontas
    para a impressora, ou manda direto para ela (imp-5, D-325).

    Refeita por causa da D-333 (22/10/2026): "Só tem que melhorar esse layout,
    cheio de letras uma em cima da outra , tudo bagunçado e dificil de saber o
    que é o que." (print relatorios/prints-samuel/2026-10-22-montar-para-
    imprimir-baguncado.png). O que mudou na disposição:
    - Duas colunas: à esquerda as OPÇÕES (rolam sozinhas); à direita, num
      cartão à parte, "O QUE VAI SAIR" (o resumo antes de gravar e o resultado
      depois). O resultado nunca mais espreme as opções (antes ele ficava
      embaixo e empurrava as opções para uma faixa de 4 linhas).
    - Seções com título curto em vez das molduras do Qt (o título da moldura
      riscava a linha de cima); frases de caixinha curtas, com a explicação
      embaixo, em letra menor e com quebra de linha (caixinha não quebra linha
      e a frase comprida passava por baixo da barra de rolagem).
    - Lista de formato com nomes curtos e a explicação do formato escolhido
      embaixo; campos de "0 = todas" mostram a palavra "todas".
    - Singular e plural certos ("1 caderno", não "1 cadernos").
    - A rodinha do mouse não muda número nem lista sem clique (ui/rodinha.py;
      teste do Kaique, 26/10: 100% virou 60% ao rolar a janela).
    - "mandar para a impressora" pergunta antes (como o "imprimir agora").
    Nenhuma opção saiu (D-315); os de fábrica são os das decisões imp-1 a imp-6.

IMPRIMIR AGORA (D-012, 26/10/2026: "2" - conserto na etapa 9)
    Antes, o botão da tela "Ficou pronto!" mandava o PDF inteiro para a
    impressora padrão do Windows num clique, sem escolher nada nem perguntar
    (lista única 5.1). `ConfirmarImpressao` pergunta antes: impressora, páginas,
    cópias e frente e verso, com a frase clara do que vai sair ("Vão para a
    impressora EPSON: 359 páginas, 1 cópia"). Só o botão "imprimir" da
    confirmação manda; fechar, Esc e "cancelar" não mandam nada.

Tudo o que é conta mora em core/impressao.py e core/impressora.py; aqui só
os controles, um fio (QThread) para a janela não parar e os avisos em
português. As escolhas ficam guardadas no configuracoes.json (chave
"impressao"), como a "Predefinição: Última configuração" do UPDF.

SEGURO MUDAR: os textos, a ordem das seções, as larguras.
ARRISCADO: montar ou imprimir no fio da tela (a janela pararia num livro
grande); tirar a confirmação de antes de imprimir (D-012).
"""

from __future__ import annotations

import math
import traceback
import unicodedata
from pathlib import Path

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import configuracoes
from core import impressao as imp
from registro import registrar_erro
from ui import estilo, rodinha

CHAVE_DAS_CONFIGURACOES = "impressao"
OPCOES_CADERNO = [8, 12, 16, 20, 24, 32, 40]

# A frase de quando o programa espera a impressora (D-332, b-5: o QPrinter
# leva até ~50 s para nascer com a impressora desligada na rede).
FALANDO_COM_A_IMPRESSORA = "Falando com a impressora (pode demorar um pouco)"

# Nomes curtos na lista (o nome comprido do core alargava a janela inteira)
# e a explicação de cada formato, que aparece embaixo da lista.
NOMES_CURTOS = {
    imp.LIVRETO: "Livreto (cadernos)",
    imp.PAGINA_INTEIRA: "Página inteira",
    imp.MULTIPLO: "Várias páginas por folha",
    imp.POSTER: "Pôster",
}
EXPLICACAO_DO_FORMATO = {
    imp.LIVRETO: "Duas páginas de cada lado de uma folha A4 deitada, já na ordem dos cadernos: "
                 "é só imprimir, dobrar ao meio e costurar.",
    imp.PAGINA_INTEIRA: "Uma página do livro em cada folha de papel.",
    imp.MULTIPLO: "Várias páginas do livro lado a lado na mesma folha.",
    imp.POSTER: "Uma página grande dividida em pedaços, cada um numa folha.",
}

# Folha de estilo só desta janela, por cima da do programa: letra de 14 px
# (a de fábrica das caixinhas é 16 px em negrito, larga demais aqui).
_ESTILO_DA_JANELA = """
QCheckBox { font-size: 14px; font-weight: 600; spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; }
QLabel#explicacao { font-size: 12px; }
QLabel#tituloDaSecao { font-size: 12px; font-weight: 700; letter-spacing: 1px; }
"""


# --------------------------------------------------------------- textos

def contar(n: int, singular: str, plural: str) -> str:
    """'1 folha', '2 folhas', '0 folhas' (singular só no 1)."""
    return f"{n} {singular if n == 1 else plural}"


def quebravel(caminho: str) -> str:
    """O caminho com pontos de quebra invisíveis depois de cada barra: um
    caminho comprido sem espaço alargava o cartão do resultado e cortava o
    texto (a linha não tinha onde quebrar)."""
    return caminho.replace("\\", "\\\u200b").replace("/", "/\u200b")


def sem_acento(texto: str) -> str:
    """Tira os acentos (caminho de disco sem acento, CLAUDE.md §3; lista
    única 5.15: o nome sugerido saía com "mágico pro")."""
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def ler_excecoes(texto: str) -> dict[int, float]:
    """"12=90; 15=85" -> {12: 90.0, 15: 85.0}. O que não se entende é ignorado."""
    excecoes: dict[int, float] = {}
    for pedaco in texto.replace(",", ";").split(";"):
        if "=" not in pedaco:
            continue
        pagina, _, valor = pedaco.partition("=")
        try:
            numero, por_cento = int(pagina.strip()), float(valor.strip().rstrip("%"))
        except ValueError:
            continue
        if numero > 0 and por_cento > 0:
            excecoes[numero] = por_cento
    return excecoes


def escrever_excecoes(excecoes: dict) -> str:
    """{12: 90.0} -> "12=90" (o contrário de ler_excecoes)."""
    return "; ".join(f"{n}={v:g}" for n, v in sorted(excecoes.items()))


def paginas_do_pdf(caminho: str) -> int:
    """Quantas páginas tem o PDF (0 se não der para abrir)."""
    try:
        import fitz

        with fitz.open(caminho) as doc:
            return doc.page_count
    except Exception:  # noqa: BLE001 - só serve para o texto; nunca fecha a janela
        registrar_erro("contar as páginas do PDF", traceback.format_exc())
        return 0


def listar_impressoras() -> list[str]:
    """As impressoras do Windows (a de sempre primeiro); [] se não der."""
    try:
        from core import impressora

        return impressora.listar_impressoras()
    except Exception:  # noqa: BLE001
        registrar_erro("listar impressoras", traceback.format_exc())
        return []


# --------------------------------------------------------------- peças da tela

def _titulo_da_secao(texto: str) -> QLabel:
    rotulo = QLabel(texto.upper())
    rotulo.setObjectName("tituloDaSecao")
    estilo.estilizar(rotulo, lambda: f"color: {estilo.TEXTO_FRACO};")
    return rotulo


def _explicacao(texto: str = "") -> QLabel:
    rotulo = QLabel(texto)
    rotulo.setObjectName("explicacao")
    rotulo.setWordWrap(True)
    estilo.estilizar(rotulo, lambda: f"color: {estilo.TEXTO_FRACO};")
    return rotulo


def _caixinha(texto: str, explicacao: str = "") -> tuple[QCheckBox, QWidget]:
    """Caixinha de frase curta com a explicação embaixo (quebra a linha)."""
    caixa = QCheckBox(texto)
    if not explicacao:
        return caixa, caixa
    bloco = QWidget()
    coluna = QVBoxLayout(bloco)
    coluna.setContentsMargins(0, 0, 0, 0)
    coluna.setSpacing(0)
    coluna.addWidget(caixa)
    nota = _explicacao(explicacao)
    nota.setContentsMargins(26, 0, 0, 0)     # alinhada com a frase, não com o quadradinho
    coluna.addWidget(nota)
    return caixa, bloco


def _formulario() -> QFormLayout:
    form = QFormLayout()
    form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    form.setHorizontalSpacing(12)
    form.setVerticalSpacing(8)
    return form


def _lista(codigos, nomes) -> QComboBox:
    combo = QComboBox()
    combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    combo.setMinimumContentsLength(12)
    for codigo in codigos:
        combo.addItem(nomes.get(codigo, str(codigo)), codigo)
    return combo


def _por_cento() -> QDoubleSpinBox:
    caixa = QDoubleSpinBox()
    caixa.setRange(10.0, 400.0)
    caixa.setDecimals(0)
    caixa.setSingleStep(5.0)
    caixa.setSuffix(" %")
    caixa.setFixedWidth(120)
    return caixa


def _numero_ou_todas() -> QSpinBox:
    """Caixa de número em que o 0 aparece escrito "todas" (antes: "(0 = todas)")."""
    caixa = QSpinBox()
    caixa.setRange(0, 99999)
    caixa.setSpecialValueText("todas")
    caixa.setFixedWidth(110)
    return caixa


def _de_ate(a: QWidget, b: QWidget) -> QWidget:
    caixa = QWidget()
    linha = QHBoxLayout(caixa)
    linha.setContentsMargins(0, 0, 0, 0)
    linha.addWidget(a)
    linha.addWidget(QLabel("até"))
    linha.addWidget(b)
    linha.addStretch()
    return caixa


# --------------------------------------------------------------- os fios

class _Tarefa(QThread):
    """Monta o arquivo (ou imprime) fora do fio da tela."""

    progresso = Signal(int, int, str)
    concluida = Signal(object)
    falhou = Signal(str)

    def __init__(self, entrada: str, opcoes: imp.OpcoesDeImpressao, destino: str = "",
                 impressora: str = "", copias: int = 1, agrupar: bool = True) -> None:
        super().__init__()
        self.entrada, self.opcoes, self.destino = entrada, opcoes, destino
        self.impressora, self.copias, self.agrupar = impressora, copias, agrupar
        self._cancelar = False

    def cancelar(self) -> None:
        self._cancelar = True

    def run(self) -> None:
        try:
            avisar = lambda f, t, txt: self.progresso.emit(f, t, txt)  # noqa: E731
            if self.destino:
                resultado = imp.montar_para_impressao(self.entrada, self.destino, self.opcoes,
                                                      progresso=avisar,
                                                      cancelado=lambda: self._cancelar)
            else:
                from core import impressora

                self.progresso.emit(0, 1, FALANDO_COM_A_IMPRESSORA)
                folhas, resultado = imp.montar_em_memoria(self.entrada, self.opcoes)
                try:
                    lado = (impressora.BORDA_CURTA if self.opcoes.formato == imp.LIVRETO
                            else impressora.BORDA_COMPRIDA)
                    if self.opcoes.lados != imp.AMBOS:
                        lado = impressora.SO_UM_LADO
                    impressora.imprimir(folhas, self.impressora, self.copias, self.agrupar, lado,
                                        progresso=avisar, cancelado=lambda: self._cancelar)
                finally:
                    folhas.close()
            self.concluida.emit(resultado)
        except imp.Cancelou:
            self.falhou.emit("Cancelado: nada foi gravado.")
        except Exception:  # noqa: BLE001 - nunca fecha a janela (CLAUDE.md §3)
            registrar_erro("montar para imprimir", traceback.format_exc())
            self.falhou.emit("Não consegui montar o arquivo para imprimir. "
                             "O livro continua salvo como estava.")


class _TarefaImprimirArquivo(QThread):
    """"imprimir agora": manda as páginas escolhidas do PDF pronto para a
    impressora, fora do fio da tela (core/impressora.imprimir)."""

    progresso = Signal(int, int, str)
    concluida = Signal(int)
    falhou = Signal(str)

    def __init__(self, caminho: str, impressora: str, de: int, ate: int, copias: int,
                 lados: str) -> None:
        super().__init__()
        self.caminho, self.impressora = caminho, impressora
        self.de, self.ate, self.copias, self.lados = de, ate, copias, lados
        self._cancelar = False

    def cancelar(self) -> None:
        self._cancelar = True

    def run(self) -> None:
        try:
            import fitz

            from core import impressora

            self.progresso.emit(0, 1, FALANDO_COM_A_IMPRESSORA)
            with fitz.open(self.caminho) as livro:
                escolhidas = fitz.open()
                try:
                    escolhidas.insert_pdf(livro, from_page=self.de - 1, to_page=self.ate - 1)
                    mandadas = impressora.imprimir(
                        escolhidas, self.impressora, self.copias, True, self.lados,
                        progresso=lambda f, t, txt: self.progresso.emit(f, t, txt),
                        cancelado=lambda: self._cancelar)
                finally:
                    escolhidas.close()
            if self._cancelar:
                self.falhou.emit(f"Parado: {contar(mandadas, 'página foi', 'páginas foram')} "
                                 "para a impressora antes de parar.")
                return
            self.concluida.emit(mandadas)
        except Exception:  # noqa: BLE001 - nunca fecha a janela (CLAUDE.md §3)
            registrar_erro("imprimir agora", traceback.format_exc())
            self.falhou.emit("Não consegui mandar para a impressora. Confira se ela está ligada "
                             "e tente de novo. O livro continua salvo como estava.")


# --------------------------------------------------------------- montar para imprimir

class DialogoImpressao(QDialog):
    """A janela de imprimir. `entrada` é o PDF do livro (as páginas em ordem)."""

    LARGURA_DO_RESULTADO = 290

    def __init__(self, entrada: str, parent=None) -> None:
        super().__init__(parent)
        self.entrada = entrada
        self.tarefa: _Tarefa | None = None
        self.ultimo_resultado: imp.Resultado | None = None
        self.paginas_do_livro = paginas_do_pdf(entrada)
        self.setWindowTitle("Montar para imprimir")
        estilo.estilizar(self, lambda: estilo.FOLHA_DE_ESTILO + _ESTILO_DA_JANELA)
        self.setMinimumSize(760, 460)

        externo = QVBoxLayout(self)
        externo.setContentsMargins(18, 14, 18, 14)
        externo.setSpacing(10)

        cabecalho = QLabel(
            f"<b>{Path(entrada).name}</b> &nbsp;·&nbsp; "
            f"{contar(self.paginas_do_livro, 'página', 'páginas')}")
        cabecalho.setWordWrap(True)
        externo.addWidget(cabecalho)
        externo.addWidget(_explicacao(
            "O PDF do livro não muda: aqui só se arrumam as folhas para a impressora."))

        corpo = QHBoxLayout()
        corpo.setSpacing(14)
        externo.addLayout(corpo, 1)
        corpo.addWidget(self._montar_opcoes(), 1)
        corpo.addWidget(self._montar_resultado())

        externo.addLayout(self._montar_botoes())

        for sinal in (self.combo_formato.currentIndexChanged, self.combo_escala.currentIndexChanged):
            sinal.connect(lambda _i: self._acertar_grupos())
        for sinal in (self.combo_formato.currentIndexChanged, self.combo_papel.currentIndexChanged,
                      self.combo_caderno.currentIndexChanged, self.combo_lados.currentIndexChanged,
                      self.folhas_de.valueChanged, self.folhas_ate.valueChanged,
                      self.paginas_de.valueChanged, self.paginas_ate.valueChanged):
            sinal.connect(lambda *_a: self._mostrar_resumo())
        self.definir_opcoes(imp.OpcoesDeImpressao.de_dicionario(
            configuracoes.ler(CHAVE_DAS_CONFIGURACOES)))
        rodinha.proteger(self)
        self._tamanho_ao_abrir()

    # --- montagem da janela

    def _montar_opcoes(self) -> QScrollArea:
        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        rolagem.setFrameShape(QFrame.Shape.NoFrame)
        dentro = QWidget()
        coluna = QVBoxLayout(dentro)
        coluna.setContentsMargins(0, 0, 14, 0)     # folga para a barra de rolagem
        coluna.setSpacing(6)
        rolagem.setWidget(dentro)
        self.area_das_opcoes = rolagem

        def secao(titulo: str) -> tuple[QWidget, QFormLayout]:
            bloco = QWidget()
            interno = QVBoxLayout(bloco)
            interno.setContentsMargins(0, 10, 0, 4)
            interno.setSpacing(6)
            interno.addWidget(_titulo_da_secao(titulo))
            form = _formulario()
            interno.addLayout(form)
            coluna.addWidget(bloco)
            return bloco, form

        # 1. formato e papel (D-314: o formato só se escolhe aqui)
        _bloco, form = secao("Como vai sair")
        self.combo_formato = _lista(imp.FORMATOS, NOMES_CURTOS)
        form.addRow("Formato:", self.combo_formato)
        self.explicacao_do_formato = _explicacao()
        form.addRow(self.explicacao_do_formato)
        self.combo_papel = _lista(tuple(imp.PAPEIS_MM), {p: p for p in imp.PAPEIS_MM})
        form.addRow("Papel:", self.combo_papel)
        self.combo_orientacao = _lista(("", imp.RETRATO, imp.PAISAGEM),
                                       {"": "a do formato", imp.RETRATO: "em pé",
                                        imp.PAISAGEM: "deitada"})
        form.addRow("Folha:", self.combo_orientacao)
        self.combo_escala = _lista(imp.ESCALAS, imp.NOMES_DAS_ESCALAS)
        form.addRow("Tamanho:", self.combo_escala)
        self.escala_percentual = _por_cento()
        form.addRow("Escala:", self.escala_percentual)
        self._form_como_vai_sair = form

        # 2. livreto (D-316, imp-4)
        self.grupo_livreto, form = secao("Livreto")
        self.combo_caderno = QComboBox()
        for valor in OPCOES_CADERNO:
            self.combo_caderno.addItem(f"{valor} páginas", valor)
        form.addRow("Cada caderno:", self.combo_caderno)
        self.combo_encadernacao = _lista((imp.ESQUERDA, imp.DIREITA),
                                         {imp.ESQUERDA: "costura à esquerda",
                                          imp.DIREITA: "costura à direita"})
        form.addRow("Encadernação:", self.combo_encadernacao)
        self.combo_lados = _lista((imp.AMBOS, imp.SO_FRENTE, imp.SO_VERSO),
                                  {imp.AMBOS: "frente e verso", imp.SO_FRENTE: "só a frente",
                                   imp.SO_VERSO: "só o verso"})
        form.addRow("Imprimir:", self.combo_lados)
        self.folhas_de, self.folhas_ate = _numero_ou_todas(), _numero_ou_todas()
        form.addRow("Folhas de papel:", _de_ate(self.folhas_de, self.folhas_ate))

        # 3. várias por folha e pôster
        self.grupo_multiplo, form = secao("Várias páginas por folha")
        self.combo_por_folha = _lista(imp.POR_FOLHA, {n: str(n) for n in imp.POR_FOLHA})
        form.addRow("Páginas por folha:", self.combo_por_folha)
        self.combo_ordem = _lista((imp.HORIZONTAL, imp.VERTICAL),
                                  {imp.HORIZONTAL: "deitada (linha por linha)",
                                   imp.VERTICAL: "em pé (coluna por coluna)"})
        form.addRow("Ordem:", self.combo_ordem)
        self.cx_moldura, bloco = _caixinha("Moldura em volta de cada página")
        form.addRow(bloco)

        self.grupo_poster, form = secao("Pôster")
        self.poster_escala = _por_cento()
        form.addRow("Escala do pedaço:", self.poster_escala)
        self.poster_sobra = QDoubleSpinBox()
        self.poster_sobra.setRange(0, 50)
        self.poster_sobra.setSuffix(" mm")
        self.poster_sobra.setFixedWidth(120)
        form.addRow("Sobreposição:", self.poster_sobra)
        self.cx_marcas, bloco = _caixinha("Marcas de corte e o nome de cada pedaço")
        form.addRow(bloco)
        self.cx_so_grandes, bloco = _caixinha("Só as páginas grandes",
                                              "As que cabem na folha saem inteiras.")
        form.addRow(bloco)

        # 4. escala de cada lado (D-317, imp-1, imp-2, imp-3)
        _bloco, form = secao("Tamanho de cada lado")
        form.addRow(_explicacao("Em % sobre o tamanho escolhido acima. Página diminuída fica no "
                                "meio da sua metade."))
        self.escala_esquerda = _por_cento()
        self.escala_direita = _por_cento()
        form.addRow("Páginas da esquerda (pares):", self.escala_esquerda)
        form.addRow("Páginas da direita (ímpares):", self.escala_direita)
        self.excecoes = QLineEdit()
        self.excecoes.setPlaceholderText("ex.: 12=90; 15=85")
        self.excecoes.setToolTip("Uma página só, com outro tamanho: número da página do livro = %.")
        form.addRow("Uma página só:", self.excecoes)
        form.addRow(_explicacao("Número da página do livro = tamanho em %. Vale só para "
                                "aquela página, não para a folha inteira."))

        # 5. margens e ajustes (D-318, D-320, D-331)
        _bloco, form = secao("Margens e ajustes")
        self.cx_margens, bloco = _caixinha(
            "Margens da encadernação",
            "1,3 cm da beirada do papel e 1 cm na costura, em cada página. Avisa se o "
            "texto passar disso.")
        form.addRow(bloco)
        self.cx_girar, bloco = _caixinha(
            "Girar sozinho a página deitada",
            "Uma tabela deitada fica de pé na folha, com o alto à esquerda.")
        form.addRow(bloco)
        self.cx_centralizar, bloco = _caixinha("Centralizar sozinho")
        form.addRow(bloco)

        # 6. o resto da janela do UPDF (imp-6)
        _bloco, form = secao("Outras opções")
        self.paginas_de, self.paginas_ate = _numero_ou_todas(), _numero_ou_todas()
        form.addRow("Páginas do livro:", _de_ate(self.paginas_de, self.paginas_ate))
        self.cx_imagem, bloco = _caixinha("Imprimir como imagem",
                                          "Ligada de fábrica: sem ela pode sair algo errado.")
        form.addRow(bloco)
        self.cx_cinza, bloco = _caixinha("Imprimir em tons de cinza")
        form.addRow(bloco)
        self.cx_reverter, bloco = _caixinha("Ordem invertida",
                                            "Da última folha para a primeira.")
        form.addRow(bloco)

        # 7. impressora (imp-5)
        _bloco, form = secao("Impressora (só para mandar direto)")
        self.combo_impressora = QComboBox()
        self.combo_impressora.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_impressora.setMinimumContentsLength(14)
        self.combo_impressora.addItem("a de sempre do Windows", "")
        form.addRow("Impressora:", self.combo_impressora)
        self.copias = QSpinBox()
        self.copias.setRange(1, 99)
        self.copias.setFixedWidth(90)
        form.addRow("Cópias:", self.copias)
        self.cx_agrupar, bloco = _caixinha("Agrupar as cópias",
                                           "Sai o livro inteiro, depois o livro inteiro de novo.")
        self.cx_agrupar.setChecked(True)
        form.addRow(bloco)
        coluna.addStretch()
        QTimer.singleShot(0, self._carregar_impressoras)
        return rolagem

    def _montar_resultado(self) -> QFrame:
        cartao = QFrame()
        cartao.setObjectName("cartao")
        cartao.setFixedWidth(self.LARGURA_DO_RESULTADO)
        de_fora = QVBoxLayout(cartao)
        de_fora.setContentsMargins(0, 0, 0, 0)
        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        rolagem.setFrameShape(QFrame.Shape.NoFrame)
        de_fora.addWidget(rolagem)
        dentro = QWidget()
        coluna = QVBoxLayout(dentro)
        coluna.setContentsMargins(14, 12, 14, 12)
        coluna.setSpacing(8)
        rolagem.setWidget(dentro)

        coluna.addWidget(_titulo_da_secao("O que vai sair"))
        self.resumo = QLabel("")
        self.resumo.setWordWrap(True)
        coluna.addWidget(self.resumo)

        self.estado = QLabel("")
        self.estado.setWordWrap(True)
        self.estado.setVisible(False)
        coluna.addWidget(self.estado)
        self.barra = QProgressBar()
        self.barra.setVisible(False)
        coluna.addWidget(self.barra)

        self.passos = QLabel("")
        self.passos.setWordWrap(True)
        self.passos.setVisible(False)
        coluna.addWidget(self.passos)

        self.conferencia = QLabel("")
        self.conferencia.setWordWrap(True)
        self.conferencia.setVisible(False)
        coluna.addWidget(self.conferencia)

        self.titulo_avisos = _titulo_da_secao("Avisos")
        self.titulo_avisos.setVisible(False)
        coluna.addWidget(self.titulo_avisos)
        # Os avisos em rótulo com quebra de linha (antes, uma caixa de texto de
        # 120 px de altura que tomava o lugar das opções).
        self.avisos = QLabel("")
        self.avisos.setWordWrap(True)
        self.avisos.setVisible(False)
        estilo.estilizar(self.avisos, lambda: f"color: {estilo.cor('aviso')};")
        coluna.addWidget(self.avisos)
        coluna.addStretch()
        return cartao

    def _montar_botoes(self) -> QHBoxLayout:
        botoes = QHBoxLayout()
        botoes.setSpacing(8)
        self.botao_gravar = QPushButton("gravar o arquivo para imprimir")
        self.botao_gravar.setObjectName("primario")
        self.botao_gravar.clicked.connect(self._gravar)
        self.botao_imprimir = QPushButton("mandar para a impressora...")
        self.botao_imprimir.clicked.connect(self._imprimir)
        self.botao_cancelar = QPushButton("parar")
        self.botao_cancelar.clicked.connect(self._cancelar)
        self.botao_cancelar.setEnabled(False)
        self.botao_fechar = QPushButton("fechar")
        self.botao_fechar.clicked.connect(self.reject)
        for botao in (self.botao_gravar, self.botao_imprimir, self.botao_cancelar):
            botao.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            botoes.addWidget(botao)
        botoes.addStretch()
        botoes.addWidget(self.botao_fechar)
        return botoes

    def _tamanho_ao_abrir(self) -> None:
        """Do tamanho que cabe na tela (notebook 1280x657 com 150%: cabe)."""
        largura, altura = 1000, 640
        tela = self.screen().availableGeometry() if self.screen() is not None else None
        if tela is not None and tela.width() > 0:
            largura = min(largura, tela.width() - 40)
            altura = min(altura, tela.height() - 40)
        self.resize(max(largura, self.minimumWidth()), max(altura, self.minimumHeight()))

    def _carregar_impressoras(self) -> None:
        if self.combo_impressora.count() > 1:
            return
        for nome in listar_impressoras():
            self.combo_impressora.addItem(nome, nome)

    def _acertar_grupos(self) -> None:
        formato = self.combo_formato.currentData()
        self.grupo_livreto.setVisible(formato == imp.LIVRETO)
        self.grupo_multiplo.setVisible(formato == imp.MULTIPLO)
        self.grupo_poster.setVisible(formato == imp.POSTER)
        self.explicacao_do_formato.setText(EXPLICACAO_DO_FORMATO.get(formato, ""))
        personalizada = self.combo_escala.currentData() == imp.PERSONALIZADA
        self.escala_percentual.setEnabled(personalizada)
        self._form_como_vai_sair.setRowVisible(self.escala_percentual, personalizada)

    # --- o resumo de antes de gravar

    def resumo_antes(self) -> str:
        """O que vai sair, em palavras, com as opções de agora (sem montar)."""
        o = self.opcoes()
        total = self.paginas_do_livro
        linhas = [f"{NOMES_CURTOS.get(o.formato, o.formato)} em papel {o.papel}."]
        if total <= 0:
            return " ".join(linhas)
        escolhidas = imp._paginas_escolhidas(total, o)          # noqa: SLF001 - conta pura
        reais = sum(1 for p in escolhidas if p is not None)
        if reais == total:
            linhas.append(f"Entram {'a' if total == 1 else 'as'} "
                          f"{contar(total, 'página', 'páginas')} do livro.")
        else:
            linhas.append(f"Entram {contar(reais, 'página', 'páginas')} de {total} do livro.")
        if o.formato == imp.LIVRETO:
            from core import cadernos

            lados = imp._lados_do_livreto(len(escolhidas), o)    # noqa: SLF001 - conta pura
            folhas = math.ceil(len(lados) / 2) if o.lados == imp.AMBOS else len(lados)
            tamanhos = cadernos.tamanhos_dos_cadernos(len(escolhidas), o.paginas_por_caderno)
            frase = f"Saem {contar(folhas, 'folha', 'folhas')} de papel"
            if o.lados == imp.AMBOS:
                frase += " (frente e verso)"
            if o.folhas_de == 0 and o.folhas_ate == 0:
                frase += f", {contar(len(tamanhos), 'caderno', 'cadernos')}"
                if len(tamanhos) > 1 and tamanhos[-1] < tamanhos[0]:
                    frase += (f"; o último com {contar(tamanhos[-1] // 4, 'folha', 'folhas')}")
            linhas.append(frase + ".")
        linhas.append("Ao gravar, os passos para imprimir e dobrar aparecem aqui.")
        return "\n\n".join(linhas)

    def _mostrar_resumo(self) -> None:
        """Opção mudou: mostra o resumo novo e tira o resultado velho (que
        valia para as opções de antes)."""
        self.resumo.setText(self.resumo_antes())
        self.resumo.setVisible(True)
        if self.tarefa is None or not self.tarefa.isRunning():
            for rotulo in (self.estado, self.passos, self.conferencia, self.avisos,
                           self.titulo_avisos):
                rotulo.setVisible(False)

    # --- as opções

    def definir_opcoes(self, o: imp.OpcoesDeImpressao) -> None:
        """Põe as opções nos controles."""
        def escolher(combo, valor):
            i = combo.findData(valor)
            combo.setCurrentIndex(i if i >= 0 else 0)

        escolher(self.combo_formato, o.formato)
        escolher(self.combo_papel, o.papel)
        escolher(self.combo_orientacao, o.orientacao)
        escolher(self.combo_escala, o.escala)
        self.escala_percentual.setValue(o.escala_percentual)
        self.cx_girar.setChecked(o.rotacao_automatica)
        self.cx_centralizar.setChecked(o.centralizar)
        self.cx_margens.setChecked(o.margens)
        self.escala_esquerda.setValue(o.escala_esquerda)
        self.escala_direita.setValue(o.escala_direita)
        self.excecoes.setText(escrever_excecoes(o.excecoes))
        escolher(self.combo_caderno, o.paginas_por_caderno)
        escolher(self.combo_encadernacao, o.encadernacao)
        escolher(self.combo_lados, o.lados)
        self.folhas_de.setValue(o.folhas_de)
        self.folhas_ate.setValue(o.folhas_ate)
        escolher(self.combo_por_folha, o.multiplo_por_folha)
        escolher(self.combo_ordem, o.multiplo_ordem)
        self.cx_moldura.setChecked(o.multiplo_moldura)
        self.poster_escala.setValue(o.poster_escala)
        self.poster_sobra.setValue(o.poster_sobreposicao_mm)
        self.cx_marcas.setChecked(o.poster_marcas)
        self.cx_so_grandes.setChecked(o.poster_so_grandes)
        self.paginas_de.setValue(o.paginas_de)
        self.paginas_ate.setValue(o.paginas_ate)
        self.cx_cinza.setChecked(o.cinza)
        self.cx_imagem.setChecked(o.como_imagem)
        self.cx_reverter.setChecked(o.reverter)
        self._acertar_grupos()
        self._mostrar_resumo()

    def opcoes(self) -> imp.OpcoesDeImpressao:
        """As opções que estão nos controles."""
        o = imp.OpcoesDeImpressao()
        o.formato = self.combo_formato.currentData()
        o.papel = self.combo_papel.currentData()
        o.orientacao = self.combo_orientacao.currentData()
        o.escala = self.combo_escala.currentData()
        o.escala_percentual = self.escala_percentual.value()
        o.rotacao_automatica = self.cx_girar.isChecked()
        o.centralizar = self.cx_centralizar.isChecked()
        o.margens = self.cx_margens.isChecked()
        o.escala_esquerda = self.escala_esquerda.value()
        o.escala_direita = self.escala_direita.value()
        o.excecoes = ler_excecoes(self.excecoes.text())
        o.paginas_por_caderno = int(self.combo_caderno.currentData())
        o.encadernacao = self.combo_encadernacao.currentData()
        o.lados = self.combo_lados.currentData()
        o.folhas_de, o.folhas_ate = self.folhas_de.value(), self.folhas_ate.value()
        o.multiplo_por_folha = int(self.combo_por_folha.currentData())
        o.multiplo_ordem = self.combo_ordem.currentData()
        o.multiplo_moldura = self.cx_moldura.isChecked()
        o.poster_escala = self.poster_escala.value()
        o.poster_sobreposicao_mm = self.poster_sobra.value()
        o.poster_marcas = self.cx_marcas.isChecked()
        o.poster_so_grandes = self.cx_so_grandes.isChecked()
        o.paginas_de, o.paginas_ate = self.paginas_de.value(), self.paginas_ate.value()
        o.cinza = self.cx_cinza.isChecked()
        o.como_imagem = self.cx_imagem.isChecked()
        o.reverter = self.cx_reverter.isChecked()
        return o

    def _guardar(self) -> imp.OpcoesDeImpressao:
        opcoes = self.opcoes()
        configuracoes.escrever(CHAVE_DAS_CONFIGURACOES, opcoes.para_dicionario())
        return opcoes

    # --- as ações

    def destino_sugerido(self) -> Path:
        """"<livro> - para imprimir.pdf", ao lado do livro e sem acento (5.15)."""
        entrada = Path(self.entrada)
        return entrada.with_name(sem_acento(f"{entrada.stem} - para imprimir.pdf"))

    def _gravar(self) -> None:
        from ui.dialogos_de_arquivo import escolher_onde_salvar_pdf

        caminho = escolher_onde_salvar_pdf(self, "Gravar o arquivo para imprimir",
                                           str(self.destino_sugerido()))
        if caminho:
            self.comecar(destino=caminho)

    def _imprimir(self) -> None:
        """imp-5, com pergunta antes (como o "imprimir agora", D-012)."""
        from ui import perguntas

        self._carregar_impressoras()
        nome = self.combo_impressora.currentText()
        opcoes = self.opcoes()
        copias = self.copias.value()
        lados = ("frente e verso" if opcoes.lados == imp.AMBOS else
                 "só a frente" if opcoes.lados == imp.SO_FRENTE else "só o verso")
        if not perguntas.perguntar(
                self, "Mandar para a impressora?",
                f"Vai para a impressora \"{nome}\": {NOMES_CURTOS.get(opcoes.formato, '')}, "
                f"{lados}, {contar(copias, 'cópia', 'cópias')}.\n\n"
                + self.resumo_antes().split("\n\n")[-2] + "\n\nMandar agora?",
                sim="mandar", nao="cancelar"):
            return
        self.comecar(impressora=self.combo_impressora.currentData() or "")

    def comecar(self, destino: str = "", impressora: str = "") -> None:
        """Começa a montar (destino) ou a imprimir, num fio à parte."""
        if self.tarefa is not None and self.tarefa.isRunning():
            return
        opcoes = self._guardar()
        self.tarefa = _Tarefa(self.entrada, opcoes, destino, impressora,
                              self.copias.value(), self.cx_agrupar.isChecked())
        self.tarefa.progresso.connect(self._andou)
        self.tarefa.concluida.connect(lambda r, d=destino: self._pronto(r, d))
        self.tarefa.falhou.connect(self._falhou)
        for botao in (self.botao_gravar, self.botao_imprimir):
            botao.setEnabled(False)
        self.botao_cancelar.setEnabled(True)
        for rotulo in (self.passos, self.conferencia, self.avisos, self.titulo_avisos):
            rotulo.setVisible(False)
        self.estado.setText("Começando...")
        self.estado.setVisible(True)
        self.barra.setRange(0, 0)
        self.barra.setVisible(True)
        self.tarefa.start()

    def _andou(self, feito: int, total: int, texto: str) -> None:
        self.estado.setText(texto)
        if total > 1:
            self.barra.setRange(0, total)
            self.barra.setValue(feito)

    def _cancelar(self) -> None:
        if self.tarefa is not None:
            self.tarefa.cancelar()

    def _terminou(self) -> None:
        for botao in (self.botao_gravar, self.botao_imprimir):
            botao.setEnabled(True)
        self.botao_cancelar.setEnabled(False)
        self.barra.setVisible(False)

    def _pronto(self, resultado: imp.Resultado, destino: str) -> None:
        self._terminou()
        self.ultimo_resultado = resultado
        partes = [contar(resultado.paginas_do_arquivo, "página", "páginas") + " no arquivo"]
        if resultado.folhas_de_papel:
            partes.append(contar(resultado.folhas_de_papel, "folha", "folhas") + " de papel")
        if resultado.cadernos:
            partes.append(contar(resultado.cadernos, "caderno", "cadernos"))
        texto = "<b>Pronto:</b> " + ", ".join(partes) + "."
        if destino:
            texto += f"<br><br>Gravado em:<br>{quebravel(destino)}"
        else:
            texto += "<br><br>Mandado para a impressora."
        self.estado.setText(texto)
        self.estado.setVisible(True)
        self.resumo.setVisible(False)       # o resultado de verdade toma o lugar

        if resultado.instrucoes:
            self.passos.setText("<b>Como imprimir:</b><br>" + "<br>".join(
                f"{i}. {linha}" for i, linha in enumerate(resultado.instrucoes, start=1)))
        self.passos.setVisible(bool(resultado.instrucoes))
        if resultado.conferencia is not None:
            certo, recado = resultado.conferencia
            self.conferencia.setText(recado)
            estilo.estilizar(self.conferencia, lambda certo=certo: (
                f"color: {estilo.VERDE if certo else estilo.VERMELHO};"))
        self.conferencia.setVisible(resultado.conferencia is not None)
        self.avisos.setText("<br><br>".join(a.texto for a in resultado.avisos))
        self.avisos.setVisible(bool(resultado.avisos))
        self.titulo_avisos.setVisible(bool(resultado.avisos))

    def _falhou(self, texto: str) -> None:
        self._terminou()
        self.estado.setText(texto)
        self.estado.setVisible(True)

    def _parar_e_esperar(self) -> None:
        if self.tarefa is not None and self.tarefa.isRunning():
            self.tarefa.cancelar()
            self.tarefa.wait(30000)

    def closeEvent(self, evento) -> None:  # noqa: N802
        """Fechar no meio cancela e espera o fio terminar (nada fica pela metade)."""
        self._parar_e_esperar()
        super().closeEvent(evento)

    def reject(self) -> None:
        self._parar_e_esperar()
        super().reject()


# --------------------------------------------------------------- imprimir agora

class ConfirmarImpressao(QDialog):
    """D-012: o "imprimir agora" pergunta antes de mandar.

    Mostra o arquivo e quantas páginas tem, e deixa escolher impressora,
    páginas, cópias e frente e verso, com a frase do que vai sair. Só o botão
    "imprimir" manda (num fio à parte, com "parar"); "cancelar", Esc e o X não
    mandam nada. `impressoras` serve aos testes (sem ele, as do Windows).
    """

    LADOS = (("um_lado", "só a frente"),
             ("comprida", "frente e verso (virando na borda comprida)"),
             ("curta", "frente e verso (virando na borda curta)"))

    def __init__(self, caminho: str, parent=None, impressoras: list[str] | None = None,
                 frente_e_verso_de_fabrica: bool = False, borda_curta: bool = False) -> None:
        super().__init__(parent)
        self.caminho = caminho
        self.tarefa: _TarefaImprimirArquivo | None = None
        self.mandadas: int | None = None
        self.total = paginas_do_pdf(caminho)
        self.setWindowTitle("Imprimir agora")
        estilo.estilizar(self, lambda: estilo.FOLHA_DE_ESTILO + _ESTILO_DA_JANELA)
        self.setMinimumSize(520, 400)

        coluna = QVBoxLayout(self)
        coluna.setContentsMargins(20, 16, 20, 16)
        coluna.setSpacing(10)
        cabecalho = QLabel(f"<b>{Path(caminho).name}</b> &nbsp;·&nbsp; "
                           f"{contar(self.total, 'página', 'páginas')}")
        cabecalho.setWordWrap(True)
        coluna.addWidget(cabecalho)
        coluna.addWidget(_explicacao(
            "Escolha a impressora e confira antes de mandar. Nada é impresso sem você clicar "
            "em \"imprimir\"."))

        form = _formulario()
        self.combo_impressora = QComboBox()
        self.combo_impressora.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_impressora.setMinimumContentsLength(16)
        nomes = listar_impressoras() if impressoras is None else list(impressoras)
        for i, nome in enumerate(nomes):
            self.combo_impressora.addItem(f"{nome} (a de sempre)" if i == 0 else nome, nome)
        if not nomes:
            self.combo_impressora.addItem("a de sempre do Windows", "")
        form.addRow("Impressora:", self.combo_impressora)

        ultima = max(1, self.total)
        self.de, self.ate = QSpinBox(), QSpinBox()
        for caixa, valor in ((self.de, 1), (self.ate, ultima)):
            caixa.setRange(1, ultima)
            caixa.setValue(valor)
            caixa.setFixedWidth(100)
        form.addRow("Páginas: de", _de_ate(self.de, self.ate))
        self.copias = QSpinBox()
        self.copias.setRange(1, 99)
        self.copias.setFixedWidth(90)
        form.addRow("Cópias:", self.copias)
        self.combo_lados = _lista([c for c, _n in self.LADOS], dict(self.LADOS))
        if frente_e_verso_de_fabrica:
            self.combo_lados.setCurrentIndex(2 if borda_curta else 1)
        form.addRow("Lados do papel:", self.combo_lados)
        coluna.addLayout(form)

        self.frase = QLabel("")
        self.frase.setWordWrap(True)
        estilo.estilizar(self.frase, lambda: (
            f"background: {estilo.cor('bar2')}; border-radius: 8px; padding: 10px 12px;"
            " font-size: 15px;"))
        coluna.addWidget(self.frase)
        self.estado = QLabel("")
        self.estado.setWordWrap(True)
        self.estado.setVisible(False)
        coluna.addWidget(self.estado)
        self.barra = QProgressBar()
        self.barra.setVisible(False)
        coluna.addWidget(self.barra)
        coluna.addStretch()

        botoes = QHBoxLayout()
        self.botao_cancelar = QPushButton("cancelar")
        self.botao_cancelar.clicked.connect(self.reject)
        self.botao_parar = QPushButton("parar")
        self.botao_parar.clicked.connect(self._parar)
        self.botao_parar.setVisible(False)
        self.botao_imprimir = QPushButton("imprimir")
        self.botao_imprimir.setObjectName("primario")
        self.botao_imprimir.clicked.connect(self.imprimir)
        # Enter não imprime: o botão padrão é o "cancelar" (D-012, segurança)
        self.botao_imprimir.setAutoDefault(False)
        self.botao_cancelar.setDefault(True)
        botoes.addStretch()
        for botao in (self.botao_cancelar, self.botao_parar, self.botao_imprimir):
            botoes.addWidget(botao)
        coluna.addLayout(botoes)

        for sinal in (self.combo_impressora.currentIndexChanged, self.de.valueChanged,
                      self.ate.valueChanged, self.copias.valueChanged,
                      self.combo_lados.currentIndexChanged):
            sinal.connect(lambda *_a: self._atualizar())
        self._atualizar()
        rodinha.proteger(self)
        self.resize(600, 440)

    # --- o que vai sair

    def escolhas(self) -> dict:
        de, ate = sorted((self.de.value(), self.ate.value()))
        return {"impressora": self.combo_impressora.currentData() or "", "de": de, "ate": ate,
                "copias": self.copias.value(), "lados": self.combo_lados.currentData()}

    def frase_do_que_sai(self) -> str:
        e = self.escolhas()
        paginas = e["ate"] - e["de"] + 1
        nome = self.combo_impressora.currentData() or "a de sempre do Windows"
        folhas = (paginas if e["lados"] == "um_lado" else math.ceil(paginas / 2)) * e["copias"]
        quais = ("o livro inteiro" if paginas == self.total
                 else f"da página {e['de']} à {e['ate']}")
        return (f"Vão para a impressora <b>{nome}</b>: "
                f"{contar(paginas, 'página', 'páginas')} ({quais}), "
                f"{contar(e['copias'], 'cópia', 'cópias')}. "
                f"Gasta {contar(folhas, 'folha', 'folhas')} de papel.")

    def _atualizar(self) -> None:
        self.frase.setText(self.frase_do_que_sai())
        paginas = self.escolhas()["ate"] - self.escolhas()["de"] + 1
        self.botao_imprimir.setText(f"imprimir {contar(paginas, 'página', 'páginas')}")
        self.botao_imprimir.setEnabled(self.total > 0 and self.tarefa is None)

    # --- mandar

    def imprimir(self) -> None:
        """O único caminho que manda para a impressora (botão "imprimir")."""
        if self.total <= 0 or (self.tarefa is not None and self.tarefa.isRunning()):
            return
        e = self.escolhas()
        self.tarefa = _TarefaImprimirArquivo(self.caminho, e["impressora"], e["de"], e["ate"],
                                             e["copias"], e["lados"])
        self.tarefa.progresso.connect(self._andou)
        self.tarefa.concluida.connect(self._pronto)
        self.tarefa.falhou.connect(self._falhou)
        for peca in (self.combo_impressora, self.de, self.ate, self.copias, self.combo_lados,
                     self.botao_imprimir):
            peca.setEnabled(False)
        self.botao_cancelar.setVisible(False)
        self.botao_parar.setVisible(True)
        self.estado.setText(FALANDO_COM_A_IMPRESSORA)
        self.estado.setVisible(True)
        self.barra.setRange(0, 0)
        self.barra.setVisible(True)
        self.tarefa.start()

    def _andou(self, feito: int, total: int, texto: str) -> None:
        self.estado.setText(texto)
        if total > 1:
            self.barra.setRange(0, total)
            self.barra.setValue(feito)

    def _fim(self) -> None:
        self.barra.setVisible(False)
        self.botao_parar.setVisible(False)
        self.botao_cancelar.setVisible(True)
        self.botao_cancelar.setText("fechar")

    def _pronto(self, mandadas: int) -> None:
        self.mandadas = mandadas
        self._fim()
        self.estado.setText(f"Pronto: {contar(mandadas, 'página mandada', 'páginas mandadas')} "
                            "para a impressora. Confira as folhas que saírem.")

    def _falhou(self, texto: str) -> None:
        self._fim()
        self.estado.setText(texto)

    def _parar(self) -> None:
        if self.tarefa is not None:
            self.tarefa.cancelar()
            self.estado.setText("Parando...")

    def _parar_e_esperar(self) -> None:
        if self.tarefa is not None and self.tarefa.isRunning():
            self.tarefa.cancelar()
            self.tarefa.wait(30000)

    def closeEvent(self, evento) -> None:  # noqa: N802
        self._parar_e_esperar()
        super().closeEvent(evento)

    def reject(self) -> None:
        self._parar_e_esperar()
        super().reject()
