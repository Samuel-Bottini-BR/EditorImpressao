"""TELA 4 (Pronto) e a tela de progresso que aparece antes dela.

Duas telas neste arquivo porque uma so faz sentido depois da outra: primeiro
`TelaProgresso` mostra a barra enquanto o pipeline roda numa QThread (a
interface nunca pode congelar, regra 3), depois `TelaFinal` mostra onde o PDF
foi salvo, como imprimir - e, se o livro vai em cadernos, o resultado da
conferencia de sequencia (ver core/cadernos.conferir_sequencia).

Etapa 9a da obra de 26/10/2026:
- "imprimir agora" (D-012, resposta "2"): antes mandava o PDF inteiro para a
  impressora padrao num clique, sem perguntar (lista unica 5.1). Agora abre a
  confirmacao (ui/dialogo_impressao.ConfirmarImpressao): impressora, paginas,
  copias, frente e verso e a frase do que vai sair. So o "imprimir" de la
  manda. ARRISCADO: ligar o botao direto a historico.imprimir de novo.
- Uma frase embaixo dos botoes diz qual "montar" usar (lista unica 5.12: o
  "Montar cadernos" das opcoes e o "montar para imprimir em A4" tinham nomes
  parecidos e a tela nao dizia qual usar; D-330 "Deixar os dois").
- Singular e plural certos ("1 caderno", "1 página").
"""

from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import historico
from core.cadernos import (
    conferir_sequencia,
    contar_cadernos,
    instrucoes_de_impressao,
)
from modelos import Projeto
from ui import estilo


class TelaProgresso(QWidget):
    """Barra, estimativa de tempo e um cancelar que funciona de verdade."""

    cancelar = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._inicio = 0.0

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(80, 60, 80, 60)
        camadas.setSpacing(18)
        camadas.addStretch()

        self.titulo = QLabel("Processando o livro...")
        self.titulo.setObjectName("titulo")
        self.titulo.setAlignment(Qt.AlignCenter)
        camadas.addWidget(self.titulo)

        self.barra = QProgressBar()
        self.barra.setRange(0, 100)
        camadas.addWidget(self.barra)

        self.detalhe = QLabel("")
        self.detalhe.setObjectName("fraco")
        self.detalhe.setAlignment(Qt.AlignCenter)
        camadas.addWidget(self.detalhe)

        linha = QHBoxLayout()
        linha.addStretch()
        botao = QPushButton("cancelar")
        botao.clicked.connect(self.cancelar.emit)
        linha.addWidget(botao)
        linha.addStretch()
        camadas.addLayout(linha)
        camadas.addStretch()

    def comecar(self, titulo: str) -> None:
        """Zera a barra e marca o instante inicial, para avancar() estimar o tempo."""
        self.titulo.setText(titulo)
        self.barra.setValue(0)
        self.detalhe.setText("")
        self._inicio = time.perf_counter()

    def avancar(self, feito: int, total: int, texto: str) -> None:
        """Atualiza a barra e a estimativa de tempo restante.

        So estima depois de pelo menos 3 unidades feitas e 1 segundo
        decorrido - antes disso a media e ruido e a estimativa oscila.
        """
        if total <= 0:
            return
        porcentagem = int(100 * feito / total)
        self.barra.setValue(porcentagem)

        # A estimativa sai da media do que ja foi feito - simples e honesta.
        decorrido = time.perf_counter() - self._inicio
        if feito >= 3 and decorrido > 1:
            restante = decorrido / feito * (total - feito)
            self.detalhe.setText(f"{texto}  -  faltam {_tempo(restante)}")
        else:
            self.detalhe.setText(texto)


def _tempo(segundos: float) -> str:
    """Tempo em portugues, sem número quebrado."""
    if segundos < 10:
        return "poucos segundos"
    if segundos < 90:
        return f"cerca de {int(round(segundos / 5) * 5)} segundos"
    minutos = int(round(segundos / 60))
    return "cerca de 1 minuto" if minutos <= 1 else f"cerca de {minutos} minutos"


class TelaFinal(QWidget):
    """Tudo pronto: onde salvou, como imprimir e o que fazer agora."""

    fazer_outro = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.caminho = ""

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(70, 40, 70, 34)
        camadas.setSpacing(14)
        camadas.addStretch()

        self.marca = _Certo()
        camadas.addWidget(self.marca, 0, Qt.AlignCenter)

        titulo = QLabel("Ficou pronto!")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        camadas.addWidget(titulo)

        self.nome = QLabel("")
        self.nome.setAlignment(Qt.AlignCenter)
        self.nome.setStyleSheet("font-size: 17px; font-weight: 600;")
        camadas.addWidget(self.nome)

        self.detalhe = QLabel("")
        self.detalhe.setObjectName("fraco")
        self.detalhe.setAlignment(Qt.AlignCenter)
        camadas.addWidget(self.detalhe)

        self.local = QLabel("")
        self.local.setObjectName("fraco")
        self.local.setAlignment(Qt.AlignCenter)
        camadas.addWidget(self.local)

        # So aparece quando o PDF antigo estava aberto em outro programa e o
        # novo foi gravado como "(2)" (conserto de 05/10/2026; ver mostrar).
        # Mesmo estilo discreto da linha "Salvo em"; o resto da tela nao muda.
        self.aviso = QLabel("")
        self.aviso.setObjectName("fraco")
        self.aviso.setAlignment(Qt.AlignCenter)
        self.aviso.setWordWrap(True)
        self.aviso.setVisible(False)
        camadas.addWidget(self.aviso)

        self.cartao_impressao = QFrame()
        self.cartao_impressao.setObjectName("cartao")
        instrucoes = QVBoxLayout(self.cartao_impressao)
        instrucoes.setContentsMargins(22, 16, 22, 16)
        instrucoes.setSpacing(6)
        rotulo = QLabel("Como imprimir:")
        rotulo.setStyleSheet("font-weight: 600;")
        instrucoes.addWidget(rotulo)
        self.passos = QVBoxLayout()
        instrucoes.addLayout(self.passos)
        camadas.addWidget(self.cartao_impressao)

        camadas.addStretch()

        linha = QHBoxLayout()
        linha.addStretch()
        self.botao_pasta = QPushButton("abrir a pasta")
        self.botao_pasta.clicked.connect(lambda: historico.abrir_pasta(self.caminho))
        linha.addWidget(self.botao_pasta)

        # D-012: pergunta antes (impressora, paginas, copias); nunca manda
        # direto. Os tres pontos dizem que abre uma janela antes.
        self.botao_imprimir = QPushButton("imprimir agora...")
        self.botao_imprimir.clicked.connect(self.imprimir_agora)
        linha.addWidget(self.botao_imprimir)

        # Item 2.6 (refeita na etapa 9a, D-333; ui/dialogo_impressao.py):
        # a janela de imprimir dentro do programa (livreto A4 com margens e escala, pagina inteira,
        # varias por folha, poster, mandar para a impressora). Trabalha sobre
        # o PDF que acabou de sair, sem mexer nele.
        # nome que diz a diferenca do "Montar cadernos" antigo (pergunta 3
        # do Samuel, 22/10/2026: "Deixar os dois")
        self.botao_montar = QPushButton("montar para imprimir em A4 (com margens)...")
        self.botao_montar.clicked.connect(self.abrir_montar_para_imprimir)
        linha.addWidget(self.botao_montar)

        outro = QPushButton("fazer outro")
        outro.setObjectName("primario")
        outro.clicked.connect(self.fazer_outro.emit)
        linha.addWidget(outro)
        linha.addStretch()
        camadas.addLayout(linha)

        # 5.12: qual dos dois "montar" usar (o texto muda em mostrar)
        self.qual_montar = QLabel("")
        self.qual_montar.setObjectName("fraco")
        self.qual_montar.setAlignment(Qt.AlignCenter)
        self.qual_montar.setWordWrap(True)
        camadas.addWidget(self.qual_montar)
        self._ja_em_cadernos = False

    def mostrar(self, projeto: Projeto, caminho: str, num_paginas: int,
                folhas_de_saida: int | None = None, antigo_preso: str = "") -> None:
        """num_paginas e o total de PAGINAS DO LIVRO.

        Com cadernos, o PDF de saida tem menos páginas que o livro, porque cada
        folha carrega duas. Contar as folhas do arquivo como páginas do livro
        daria um número de cadernos errado - e o usuario separaria os grupos
        errados na hora de dobrar.

        antigo_preso: o nome do PDF antigo que estava aberto em outro programa
        e nao pode ser substituido (o novo, em `caminho`, e o "(2)"). Com ele,
        aparece a frase explicando; vazio (o normal), a frase some - inclusive
        a de um livro anterior.
        """
        if antigo_preso:
            self.aviso.setText(
                f"O arquivo antigo, \"{antigo_preso}\", estava aberto em outro "
                f"programa (o leitor de PDF, por exemplo) e não pôde ser "
                f"substituído. Ele ficou como estava, e o PDF novo foi salvo ao "
                f"lado dele com o nome acima.")
        else:
            self.aviso.setText("")
        self.aviso.setVisible(bool(antigo_preso))
        self.caminho = caminho
        arquivo = Path(caminho)

        self.nome.setText(arquivo.name)

        mb = arquivo.stat().st_size / 1024 / 1024 if arquivo.exists() else 0.0
        partes = [_contar(num_paginas, "página", "páginas"), f"{mb:.1f} MB".replace(".", ",")]
        if projeto.montar_cadernos:
            total = contar_cadernos(num_paginas, projeto.paginas_por_caderno)
            partes.append(_contar(total, "caderno", "cadernos"))
            if folhas_de_saida:
                partes.append(_contar(folhas_de_saida, "folha", "folhas") + " para imprimir")
        self.detalhe.setText("  -  ".join(partes))
        self.local.setText(f"Salvo em: {arquivo.parent}")

        while self.passos.count():
            item = self.passos.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # item 2.6: o PDF ja em cadernos (o "Montar cadernos" de sempre) nao
        # pode ser montado de novo - sairia embaralhado duas vezes
        self._ja_em_cadernos = bool(projeto.montar_cadernos)
        self.botao_montar.setEnabled(not projeto.montar_cadernos)
        self.qual_montar.setText(
            "Este PDF já saiu em cadernos, no tamanho do scan e sem margens (o \"Montar "
            "cadernos\" das opções do livro). Para cadernos em A4 com as margens da "
            "encadernação, desmarque essa opção e gere de novo."
            if projeto.montar_cadernos else
            "Para imprimir em cadernos, use \"montar para imprimir em A4\": arruma as folhas "
            "com as margens da encadernação. O PDF do livro não muda.")
        self.botao_montar.setToolTip(
            "Este PDF já saiu montado em cadernos. Para usar a montagem nova (A4 com margens), "
            "desmarque \"Montar cadernos\" nas opções do livro e gere de novo."
            if projeto.montar_cadernos else
            "Monta as folhas para a impressora: livreto em A4 com as margens da encadernação, "
            "página inteira, várias por folha ou pôster. O PDF do livro não muda.")

        self.cartao_impressao.setVisible(projeto.montar_cadernos)
        if projeto.montar_cadernos:
            linhas = instrucoes_de_impressao(num_paginas, projeto.paginas_por_caderno)
            for i, texto in enumerate(linhas, start=1):
                self.passos.addWidget(QLabel(f"{i}. {texto}"))

            # A resposta ao "como ter certeza que estao na sequencia correta sem
            # olhar folha por folha?". Nao entra na lista numerada porque nao e
            # um passo a fazer: e o resultado de uma conferencia ja feita.
            certo, recado = conferir_sequencia(
                num_paginas, projeto.paginas_por_caderno)
            aviso = QLabel(recado)
            aviso.setWordWrap(True)
            estilo.estilizar(aviso, lambda certo=certo: (
                f"color: {estilo.VERDE if certo else estilo.VERMELHO}; "
                "margin-top: 8px;"))
            self.passos.addWidget(aviso)


    def imprimir_agora(self) -> None:
        """D-012: abre a confirmação; quem manda para a impressora é o botão
        "imprimir" de lá, nunca este clique."""
        from ui.dialogo_impressao import ConfirmarImpressao

        if not self.caminho or not Path(self.caminho).exists():
            return
        # o PDF já em cadernos (o jeito antigo) imprime frente e verso, virando
        # na borda curta (o mesmo do cartão "Como imprimir")
        self.dialogo_imprimir = ConfirmarImpressao(
            self.caminho, self, frente_e_verso_de_fabrica=self._ja_em_cadernos,
            borda_curta=self._ja_em_cadernos)
        self.dialogo_imprimir.open()

    def abrir_montar_para_imprimir(self) -> None:
        """Item 2.6: abre a janela "Montar para imprimir" sobre o PDF gerado."""
        from ui.dialogo_impressao import DialogoImpressao

        if not self.caminho or not Path(self.caminho).exists():
            return
        self.dialogo_impressao = DialogoImpressao(self.caminho, self)
        self.dialogo_impressao.open()


def _contar(n: int, singular: str, plural: str) -> str:
    """'1 página', '2 páginas' (singular só no 1)."""
    return f"{n} {singular if n == 1 else plural}"


class _Certo(QWidget):
    """Um circulo verde com um visto. Desenhado, não emoji (regra 3.4)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(76, 76)

    def paintEvent(self, evento) -> None:  # noqa: N802
        """Desenha o circulo e o visto a mao, com QPainter - nunca emoji (regra 3)."""
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.setPen(QPen(QColor(estilo.VERDE), 4))
        pintor.drawEllipse(4, 4, 68, 68)
        caneta = QPen(QColor(estilo.VERDE), 6)
        caneta.setCapStyle(Qt.RoundCap)
        pintor.setPen(caneta)
        pintor.drawLine(23, 39, 34, 50)
        pintor.drawLine(34, 50, 54, 27)
