"""As folhas do caderno na etapa 7 "Montar cadernos" do Automático, e a tela grande delas (D-574).

O QUE O SAMUEL DECIDIU (Livro de decisões, docs/plano/DECISOES.md, D-574)
    29/10/2026: "quando mostra para fazer os cadernos lá na parte de fazer caderno tem que ter um
    botão para ver como vai ficar o caderno."
    31/10 (print da etapa 7 "Montar cadernos"): "Ele vai aparecer quando estiver na aba do montar
    caderno como no print que eu mandei, quando a pessoa for nessa aba ela vai poder ver [...]" ·
    "Sim, mas no caso, eu estou falando em tela grande, pois no painel automatico, vamos conseguir
    ver ele só se clicarmos na opção de montar cadernos e lá se apertarmos em ver tela grande
    abriremos o tela grande que já temos mas para versão de caderno."
    No Livro: "No Automático: clicando na etapa 7 "Montar cadernos", o lado direito mostra as
    folhas do livreto; o botão "tela cheia" abre a tela grande que já existe, na versão de
    caderno." O jeito (opção 1, 31/10): a folha como sai da impressora, frente e verso,
    "Folha N de M", setas para passar as folhas.
    02/11: "mas no caso ele vai fazer isso só quando a etapa 7 estiver selecionada no montar
    cadernos né?" → sim; nas outras etapas o lado direito continua o antes e depois (D-577).

O QUE MOSTRA
    FolhasDoCaderno é o lado direito da janela grande do Automático quando a etapa 7 está aberta:
    "Como vai sair da impressora" com a bolinha (D-064), "Folha N de M — frente" e a frente da
    folha, "Folha N de M — verso" e o verso, as setas "‹ folha N ›" com o "(vira o papel)" e o
    "tela cheia" (os mesmos textos do "Montar para imprimir", ui/dialogo_impressao._montar_previa,
    e o mesmo botão da página da direita). O "tela cheia" abre TelaGrandeDoCaderno: a tela grande
    do Automático (TelaCheiaDoAntesEDepois: maximizada, "<" ">", –, +, "ajustar à tela", a roda
    dá zoom, Shift + roda anda de lado, "fechar"), mostrando a folha no lugar do antes e depois.

A FOLHA É A QUE A ETAPA 7 FAZ (D-473, "tela e PDF saem da mesma conta")
    A etapa 7 monta os cadernos "no tamanho do scan (sem A4, sem margem)": core/cadernos.impor_pdf,
    cada lado da folha com duas páginas do livro lado a lado, na ordem da dobra
    (core/cadernos.montar_ordem), cada página encaixada na sua metade sem mudar a proporção e no
    meio dela (show_pdf_page do PyMuPDF). `ordem_das_folhas` usa a MESMA montar_ordem e
    `montar_o_lado` faz o mesmo encaixe na imagem (a prova compara com o PDF que impor_pdf grava).
    Cada página é desenhada como o "depois" da página da direita (core/automatico.
    depois_da_pagina: como ela sai com as etapas marcadas e as opções da janela, o mesmo caminho
    do "Rodar"), numa cópia do projeto: nada muda no livro.
    Diferença que fica (ressalva escrita no ONDE-PAREI): impor_pdf faz cada metade do tamanho da
    MAIOR página do livro inteiro; aqui, da maior página DESTA folha (medir o livro inteiro a
    cada troca levaria minutos). Livro com páginas do mesmo tamanho: igual.

A TELA NUNCA PARA (CLAUDE.md §3)
    A folha inteira (o "depois" das páginas e a montagem) é feita no servidor de páginas, fora do
    processo da janela (core/automatico.folha_do_caderno -> core/paginas_em_outro_processo.
    folha_do_caderno); o fio TarefaFolhaDoCaderno só espera o cano e prepara as imagens. Medido no
    Gradus Primus (02/11): com a conta num fio da janela a tela parava 0,28 a 0,49 s. Trocas seguidas viram uma só (a mesma espera da página da
    direita); só uma conta por vez; a que roda é cancelada; resultado velho é jogado fora. Uma
    folha por vez na memória (a frente e o verso da folha à vista).

Seguro mudar: tamanhos e margens. Arriscado: montar a folha de outro jeito que não o de impor_pdf
(a tela deixaria de ser o arquivo); calcular no projeto aberto em vez da cópia."""

from __future__ import annotations

import json
import traceback

from PySide6.QtCore import QEvent, QObject, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core import cadernos
from ui import estilo

# a resolução das páginas da folha: a mesma do "depois" da página da direita (ui/automatico.
# DPI_DA_PREVIA, 180: abaixo disso o Mágico pro estragava letras na prévia). Seguro mudar junto.
DPI_DA_FOLHA = 180
# a folha volta do servidor reduzida a esta largura (a tela grande nunca mostra mais; um lado da
# folha de páginas largas passava de 4000 pontos, e copiar e reduzir isso no programa prendia o
# Python 0,1 a 0,2 s). Seguro mudar (mais = mais nítido no zoom da tela grande, mais memória).
LARGURA_MAXIMA_DA_FOLHA = 2400
FRENTE, VERSO = "frente", "verso"


# ---------------------------------------------------------------------------
# a conta (sem janela)
# ---------------------------------------------------------------------------

# a conta da folha mora em core/cadernos.py (ao lado de impor_pdf, a montagem do PDF da etapa 7),
# para o servidor de páginas poder montar a folha fora do processo da janela
ordem_das_folhas = cadernos.ordem_das_folhas
montar_o_lado = cadernos.montar_o_lado
montar_a_folha = cadernos.montar_a_folha


def _qimagem(img):
    """A QImage (RGB) de uma imagem BGR do OpenCV, copiada (a QImage não pode apontar para a
    memória do numpy, que o Python solta). Pode rodar fora do fio da tela."""
    import numpy as np
    from PySide6.QtGui import QImage

    rgb = np.ascontiguousarray(img[:, :, ::-1])
    altura, largura = rgb.shape[:2]
    return QImage(rgb.data, largura, altura, largura * 3, QImage.Format_RGB888).copy()


class TarefaFolhaDoCaderno(QThread):
    """Desenha UMA folha do caderno (frente e verso) num fio de fundo. Recebe uma CÓPIA do
    projeto (feita no fio da janela), o pedido do Automático e as páginas da folha (índices em
    projeto.paginas, por posição no PDF). Cada página é o "depois" de core/automatico.
    depois_da_pagina, cada uma numa cópia da cópia (o depois muda a cópia que recebe).
    `cancelar()` para no próximo ponto de parada; cancelada, não emite `pronta`. `terminou` sai
    sempre (o _Guardiao da janela grande solta a tarefa)."""

    # pedido, (frente, verso) numpy BGR, {"inteiras": (QImage, QImage), "pequenas": (QImage, QImage)}
    pronta = Signal(int, object, object)
    falhou = Signal(int)
    terminou = Signal(object)

    def __init__(self, copia, pedido, folha: tuple, indices: dict, dpi: int, numero: int,
                 tamanho_pequeno: tuple = (400, 300)) -> None:
        """`tamanho_pequeno`: o tamanho do quadro de cada face no lado direito (a imagem já vem
        reduzida para ele, feita aqui: reduzir uma folha grande no fio da tela parava a tela)."""
        super().__init__()
        self.tamanho_pequeno = tamanho_pequeno
        self.copia, self.pedido, self.folha, self.indices = copia, pedido, folha, indices
        self.dpi, self.numero = dpi, numero
        self._cancelar = False

    def cancelar(self) -> None:
        self._cancelar = True

    def run(self) -> None:
        """Nunca deixa exceção escapar (CLAUDE.md §3)."""
        from core import automatico
        from core.pipeline import Cancelou
        from registro import registrar_erro

        try:
            # a folha é montada e desenhada no servidor de páginas (outro processo: a tela nunca
            # para, CLAUDE.md §3); servidor fora do ar: aqui, neste fio (core/automatico.
            # folha_do_caderno). Este fio só espera o cano, com o Python solto.
            frente, verso = automatico.folha_do_caderno(
                self.copia, self.pedido, self.folha, self.indices, self.dpi,
                cancelado=lambda: self._cancelar, largura_maxima=LARGURA_MAXIMA_DA_FOLHA)
            if self._cancelar:
                raise Cancelou()
            # as imagens da tela feitas aqui, fora do fio da tela, e sem o QImage.scaled (ele
            # prende o Python ~0,2 s numa folha grande, medido em 02/11): a redução é do OpenCV
            # (que solta o Python) e a QImage é só uma cópia. QPixmap não pode ser feita fora do
            # fio da tela (quem faz é a janela).
            import cv2

            largura, altura = self.tamanho_pequeno
            escala = min(max(1, largura) / frente.shape[1], max(1, altura) / frente.shape[0])
            tamanho = (max(1, round(frente.shape[1] * escala)), max(1, round(frente.shape[0] * escala)))
            pequenas = tuple(_qimagem(cv2.resize(f, tamanho, interpolation=cv2.INTER_AREA))
                             for f in (frente, verso))
            inteiras = tuple(_qimagem(f) for f in (frente, verso))
            if not self._cancelar:
                self.pronta.emit(self.numero, (frente, verso),
                                 {"inteiras": inteiras, "pequenas": pequenas,
                                  "tamanho_pequeno": tuple(self.tamanho_pequeno)})
        except Cancelou:
            pass
        except Exception:  # noqa: BLE001 - nada pode derrubar o programa
            registrar_erro("folha do caderno no automatico", traceback.format_exc())
            self.falhou.emit(self.numero)
        finally:
            self.copia = None
            self.terminou.emit(self)


# ---------------------------------------------------------------------------
# o lado direito da janela grande com a etapa 7 aberta
# ---------------------------------------------------------------------------

class FolhasDoCaderno(QWidget):
    """O lado direito da janela grande do Automático com a etapa 7 "Montar cadernos" aberta
    (D-574, ver o topo do arquivo). `ligar(True)` quando a etapa 7 é a aberta: só então calcula;
    `ligar(False)` para a conta e solta a folha."""

    def __init__(self, estado, projeto=None, parent=None) -> None:
        super().__init__(parent)
        from ui.widgets.bolinha import BolinhaDeCarregamento

        self.estado = estado
        self.projeto = projeto
        self.ligada = False
        self.posicao = 0                 # a folha à vista (0 = a primeira)
        self._numero = 0                 # o número do último pedido: só ele vale
        self._tarefa: TarefaFolhaDoCaderno | None = None
        self._na_espera = False          # um pedido esperando a conta que roda parar
        self._feito = None               # a chave da folha mostrada
        self._querida = None             # a chave do último pedido
        self._folha: tuple | None = None   # (frente, verso) da folha à vista, numpy
        self._pix: tuple | None = None     # as mesmas duas, já em QPixmap (feitas uma vez)
        self._qimagens: dict | None = None  # as QImage feitas no fio da conta (inteiras e pequenas)
        self._fechada = False
        self.tela_grande: TelaGrandeDoCaderno | None = None

        col = QVBoxLayout(self)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(6)
        topo = QHBoxLayout()
        topo.addWidget(QLabel("Como vai sair da impressora"))
        self.bolinha = BolinhaDeCarregamento()
        topo.addWidget(self.bolinha)
        topo.addStretch()
        col.addLayout(topo)

        self.area = QWidget()
        dentro = QVBoxLayout(self.area)
        dentro.setContentsMargins(0, 0, 0, 0)
        dentro.setSpacing(4)
        self.rotulos: dict[str, QLabel] = {}
        self.imagens: dict[str, QLabel] = {}
        for lado in (FRENTE, VERSO):
            rotulo = QLabel("")
            rotulo.setStyleSheet("font-weight: 700;")
            imagem = QLabel()
            imagem.setAlignment(Qt.AlignCenter)
            imagem.setMinimumSize(40, 30)
            estilo.estilizar(imagem, lambda: f"background: {estilo.cor('bar2')};")
            dentro.addWidget(rotulo)
            dentro.addWidget(imagem, 1)
            self.rotulos[lado], self.imagens[lado] = rotulo, imagem
        col.addWidget(self.area, 1)

        barra = QHBoxLayout()
        barra.setSpacing(4)
        self.botao_anterior = QPushButton("‹")
        self.botao_anterior.setToolTip("folha anterior")
        self.botao_anterior.clicked.connect(lambda: self.passar_folha(-1))
        self.rotulo_da_folha = QLabel("")
        self.botao_seguinte = QPushButton("›")
        self.botao_seguinte.setToolTip("próxima folha")
        self.botao_seguinte.clicked.connect(lambda: self.passar_folha(1))
        for botao in (self.botao_anterior, self.botao_seguinte):
            botao.setStyleSheet("padding: 0px 8px; font-size: 16px;")
        self.nota_vira_o_papel = QLabel("(vira o papel)")
        barra.addWidget(self.botao_anterior)
        barra.addWidget(self.rotulo_da_folha)
        barra.addWidget(self.botao_seguinte)
        barra.addSpacing(8)
        barra.addWidget(self.nota_vira_o_papel)
        barra.addStretch()
        self.botao_tela_cheia = QPushButton("tela cheia")
        self.botao_tela_cheia.clicked.connect(self.abrir_em_tela_cheia)
        barra.addWidget(self.botao_tela_cheia)
        col.addLayout(barra)

        from ui.automatico import ESPERA_ANTES_DE_CALCULAR_MS

        self._relogio = QTimer(self)
        self._relogio.setSingleShot(True)
        self._relogio.setInterval(ESPERA_ANTES_DE_CALCULAR_MS)
        self._relogio.timeout.connect(self._calcular_agora)
        estado.mudou.connect(self.pedir)
        self._acertar_textos()

    # --- as contas da folha -------------------------------------------------------

    def _ativas(self) -> list[int]:
        """Os índices (em projeto.paginas) das páginas que vão para o PDF, na ordem do PDF."""
        if self.projeto is None:
            return []
        return [p.indice for p in self.projeto.paginas_ativas]

    def paginas_por_caderno(self) -> int:
        return cadernos.paginas_por_caderno_valido(int(self.estado.opcoes.get("paginas_por_caderno", 20)))

    def folhas(self) -> list[tuple]:
        """As folhas do livro com as páginas por caderno escolhidas na janela agora."""
        return ordem_das_folhas(len(self._ativas()), self.paginas_por_caderno())

    def total(self) -> int:
        return len(self.folhas())

    # --- os textos (D-574: "Folha N de M — frente", "folha N", "(vira o papel)") ---------

    @staticmethod
    def texto_da_face(numero: int, total: int, lado: str) -> str:
        """O mesmo texto do "Montar para imprimir" (DialogoImpressao.texto_da_face)."""
        return f"Folha {numero} de {total} — {lado}"

    def _acertar_textos(self) -> None:
        total = self.total()
        self.posicao = max(0, min(self.posicao, max(0, total - 1)))
        numero = self.posicao + 1
        for lado in (FRENTE, VERSO):
            self.rotulos[lado].setText(self.texto_da_face(numero, total, lado) if total else "")
        self.rotulo_da_folha.setText(f"folha {numero}" if total else "")
        self.botao_anterior.setEnabled(total > 0 and self.posicao > 0)
        self.botao_seguinte.setEnabled(total > 0 and self.posicao < total - 1)
        self.botao_tela_cheia.setEnabled(total > 0)

    # --- ligar, passar a folha, pedir ------------------------------------------------

    def ligar(self, sim: bool) -> None:
        """A etapa 7 abriu (True) ou fechou (False) na janela grande."""
        sim = bool(sim) and not self._fechada
        if sim == self.ligada:
            return
        self.ligada = sim
        if sim:
            self._acertar_textos()
            self.pedir(agora=True)
        else:
            self._parar()
            self._folha = self._feito = self._pix = None
            self._mostrar()

    def passar_folha(self, passo: int) -> None:
        total = self.total()
        nova = max(0, min(self.posicao + passo, max(0, total - 1)))
        if nova == self.posicao:
            return
        self.posicao = nova
        self.pedir(agora=True)

    def _chave(self, pedido) -> str:
        return json.dumps([self.posicao, self.paginas_por_caderno(), pedido.etapas, pedido.opcoes,
                           pedido.paginas, pedido.ordem, pedido.desligar, self._ativas()],
                          sort_keys=True, default=str)

    def calculando(self) -> bool:
        return bool(self._relogio.isActive() or self._tarefa is not None or self._na_espera)

    def pedir(self, agora: bool = False) -> None:
        """Uma troca na janela (opção, páginas por caderno, seta): pede a folha de novo."""
        if self._fechada or not self.ligada:
            return
        self._acertar_textos()
        if agora:
            self._relogio.stop()
            self._calcular_agora()
        else:
            self._relogio.start()
        self._acertar_bolinha()

    def _calcular_agora(self) -> None:
        from core.automatico import copia_para_a_previa

        if self._fechada or not self.ligada or self.projeto is None:
            return
        folhas = self.folhas()
        if not folhas:
            self._folha = self._feito = None
            self._mostrar()
            return
        pedido = self.estado.pedido(pular_mexidas=False)   # como a página da direita (D-577, 30/10)
        chave = self._chave(pedido)
        self._querida = chave
        if chave == self._feito:
            self._na_espera = False
            if self._tarefa is not None:
                self._tarefa.cancelar()
            self._acertar_bolinha()
            return
        if self._folha is not None:
            self._folha = None             # a folha velha sai: era outra folha ou outras opções
            self._mostrar()
        if self._tarefa is not None:
            self._tarefa.cancelar()        # só uma conta por vez: esta espera a vez
            self._na_espera = True
            self._acertar_bolinha()
            return
        self._na_espera = False
        ativas = self._ativas()
        folha = folhas[self.posicao]
        indices = {}
        for lado in folha:
            for posicao in (lado.esquerda, lado.direita):
                if posicao is not None and 0 <= posicao < len(ativas):
                    indices[posicao] = ativas[posicao]
        self._numero += 1
        tarefa = TarefaFolhaDoCaderno(copia_para_a_previa(self.projeto), pedido, folha, indices,
                                      DPI_DA_FOLHA, self._numero, self._tamanho_do_quadro())
        tarefa.chave = chave
        tarefa.pronta.connect(self._chegou)
        tarefa.falhou.connect(self._falhou)
        tarefa.terminou.connect(self._terminou)
        from ui.automatico import _guardiao

        _guardiao().segurar(tarefa)
        self._tarefa = tarefa
        tarefa.start()
        self._acertar_bolinha()

    def _tamanho_do_quadro(self) -> tuple:
        """O tamanho em que cada face cabe no lado direito agora (largura, altura)."""
        alvo = self.imagens[FRENTE]
        return (max(1, alvo.width() - 4), max(1, alvo.height() - 4))

    def _chegou(self, numero: int, faces, imagens) -> None:
        frente, verso = faces
        tarefa = self.sender()
        if numero != self._numero or getattr(tarefa, "chave", None) != self._querida:
            return                          # pedido velho
        self._folha = (frente, verso)       # a única folha guardada (CLAUDE.md §3)
        self._pix = None
        self._qimagens = imagens
        self._feito = self._querida
        self._mostrar()
        if self.tela_grande is None:
            QTimer.singleShot(0, self._preparar_a_tela_grande)

    def _falhou(self, numero: int) -> None:
        if numero != self._numero:
            return
        self._folha = self._feito = None
        self._mostrar(erro=True)

    def _terminou(self, tarefa) -> None:
        if tarefa is self._tarefa:
            self._tarefa = None
        if self._na_espera and not self._fechada:
            self._na_espera = False
            if not self._relogio.isActive():
                self._calcular_agora()
        self._acertar_bolinha()

    def _parar(self) -> None:
        self._relogio.stop()
        self._na_espera = False
        if self._tarefa is not None:
            self._tarefa.cancelar()
            for sinal, alvo in ((self._tarefa.pronta, self._chegou), (self._tarefa.falhou, self._falhou),
                                (self._tarefa.terminou, self._terminou)):
                try:
                    sinal.disconnect(alvo)
                except (RuntimeError, TypeError):
                    pass
            self._tarefa = None
        self._acertar_bolinha()

    def _acertar_bolinha(self) -> None:
        calculando = self.calculando()
        total = self.total()
        dica = ""
        if calculando:
            # o mesmo balão do "Montar para imprimir" (DialogoImpressao._mostrar_carregando)
            quantas = f"{total} {'folha' if total == 1 else 'folhas'}"
            dica = "Montando a folha" + (f" (o livreto tem {quantas})" if total else "")
        self.bolinha.definir(calculando, dica)
        if self.tela_grande is not None and self.tela_grande.aberta:
            self.tela_grande.acertar()

    # --- mostrar ----------------------------------------------------------------------

    def _mostrar(self, erro: bool = False) -> None:
        self._acertar_textos()
        for lado in (FRENTE, VERSO):
            if self._folha is None:
                self.imagens[lado].clear()
                self.imagens[lado]._feito_de = None
            self.imagens[lado].setVisible(True)
            self.rotulos[lado].setVisible(True)
        if erro:
            self.imagens[VERSO].setVisible(False)
            self.rotulos[VERSO].setVisible(False)
            self.rotulos[FRENTE].setText("Não consegui mostrar esta folha.")
        self._desenhar()
        if self.tela_grande is not None and self.tela_grande.aberta:
            self.tela_grande.acertar()

    def pixmaps(self) -> tuple | None:
        """(frente, verso) da folha à vista em QPixmap, feitos uma vez por folha (a conversão
        de uma folha grande custa; a tela grande usa os mesmos)."""
        if self._folha is None:
            self._pix = None
            return None
        if self._pix is None:
            self._pix = tuple(QPixmap.fromImage(img) for img in self._qimagens["inteiras"])
        return self._pix

    def _desenhar(self) -> None:
        pix = self.pixmaps()
        if pix is None:
            return
        for lado, desenho in zip((FRENTE, VERSO), pix):
            alvo = self.imagens[lado]
            tamanho = (max(1, alvo.width() - 4), max(1, alvo.height() - 4))
            atual = alvo.pixmap()
            if (getattr(alvo, "_feito_de", None) is desenho and getattr(alvo, "_tamanho", None) == tamanho
                    and atual is not None and not atual.isNull()):
                continue                    # já desenhada neste tamanho
            pequenas = self._qimagens
            if pequenas and pequenas.get("tamanho_pequeno") == tamanho:
                # já reduzida no fio da conta, para este tamanho
                alvo.setPixmap(QPixmap.fromImage(pequenas["pequenas"][0 if lado == FRENTE else 1]))
            else:
                alvo.setPixmap(desenho.scaled(*tamanho, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            alvo._feito_de, alvo._tamanho = desenho, tamanho

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().resizeEvent(evento)
        QTimer.singleShot(0, self._desenhar)

    def keyPressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Setas e Page Up/Down passam a folha (como o folhear da página da direita)."""
        if evento.key() in (Qt.Key_Left, Qt.Key_PageUp):
            self.passar_folha(-1)
        elif evento.key() in (Qt.Key_Right, Qt.Key_PageDown):
            self.passar_folha(1)
        else:
            super().keyPressEvent(evento)

    def faces(self) -> tuple | None:
        """(frente, verso) da folha à vista (numpy BGR), ou None enquanto monta."""
        return self._folha

    # --- a tela grande ----------------------------------------------------------------

    def _preparar_a_tela_grande(self) -> None:
        """Monta a tela grande escondida logo que a primeira folha chega (uma vez): criar a
        janela e o estilo dela no clique do "tela cheia" parava a tela ~0,15 s a mais (medido
        no Gradus Primus, 02/11). Fechada, ela fica guardada para a próxima vez (vazia)."""
        if self.tela_grande is not None or self._fechada or not self.ligada:
            return
        self.tela_grande = TelaGrandeDoCaderno(self)
        self.tela_grande.ensurePolished()
        self.tela_grande.winId()

    def abrir_em_tela_cheia(self) -> None:
        """O "tela cheia" com a etapa 7 aberta: a tela grande, na versão de caderno."""
        if self.total() == 0:
            return
        if self.tela_grande is None:
            self.tela_grande = TelaGrandeDoCaderno(self)
        self.tela_grande.aberta = True
        self.tela_grande.acertar()
        self.tela_grande.open()
        self.tela_grande.raise_()
        self.tela_grande.activateWindow()

    def fechar(self) -> None:
        """Ao fechar a janela grande: para a conta e solta a folha; nada mais é pedido."""
        if not self._fechada:
            self._fechada = True
            try:
                self.estado.mudou.disconnect(self.pedir)
            except (RuntimeError, TypeError):
                pass
        self._parar()
        if self.tela_grande is not None:
            if self.tela_grande.isVisible():
                self.tela_grande.reject()
            self.tela_grande.deleteLater()
            self.tela_grande = None
        self._folha = self._pix = None


class _RodaNaFolha(QObject):
    """A roda do mouse na tela grande do caderno: Shift + roda anda de lado (D-600,
    ui/widgets/roda_de_lado); a roda sozinha dá zoom (D-577, 3º teste: "não consigo dar zoom
    com o mouse, usando o scrool"), como na tela grande do antes e depois."""

    def __init__(self, tela: "TelaGrandeDoCaderno") -> None:
        super().__init__(tela)
        self.tela = tela

    def eventFilter(self, _alvo, evento) -> bool:  # noqa: N802 - nome do Qt
        if evento.type() != QEvent.Wheel:
            return False
        from ui.widgets.roda_de_lado import shift_roda_na_rolagem
        from ui.widgets.visualizador import PASSO_DA_RODA

        if shift_roda_na_rolagem(self.tela.rolagem, evento):
            return True
        passos = evento.angleDelta().y() / 120.0
        if passos:
            self.tela._zoom(PASSO_DA_RODA ** passos)
        return True


class TelaGrandeDoCaderno(QDialog):
    """A tela grande que já existe (a do antes e depois do Automático, TelaCheiaDoAntesEDepois:
    maximizada, "<" ">", o contador, a bolinha, –, +, "ajustar à tela", "fechar"), na versão de
    caderno (D-574, 31/10): a frente e embaixo o verso da folha, grandes, com "Folha N de M —
    frente/verso" em cima de cada uma. Mostra a MESMA folha de FolhasDoCaderno (nada é calculado
    aqui); passar a folha aqui é passar lá. Sem o "comparar" (é do antes e depois da página)."""

    def __init__(self, painel: FolhasDoCaderno) -> None:
        super().__init__(painel)
        from PySide6.QtGui import QGuiApplication

        from ui.widgets.bolinha import BolinhaDeCarregamento

        self.painel = painel
        self.zoom = 1.0
        self.aberta = False                # o "tela cheia" foi apertado e ela não fechou
        self._feito = None                 # (pixmaps, largura, altura) já postos
        self.setWindowTitle("Como vai sair da impressora")
        estilo.estilizar(self, lambda: estilo.FOLHA_DE_ESTILO)
        self.setSizeGripEnabled(True)

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(14, 14, 14, 12)
        camadas.setSpacing(8)
        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        self.rolagem.setFrameShape(QFrame.NoFrame)
        self.rolagem.setAlignment(Qt.AlignCenter)
        dentro = QWidget()
        col = QVBoxLayout(dentro)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)
        self.rotulos: dict[str, QLabel] = {}
        self.imagens: dict[str, QLabel] = {}
        for lado in (FRENTE, VERSO):
            rotulo = QLabel("")
            rotulo.setStyleSheet("font-weight: 700;")
            rotulo.setAlignment(Qt.AlignCenter)
            imagem = QLabel()
            imagem.setAlignment(Qt.AlignCenter)
            col.addWidget(rotulo)
            col.addWidget(imagem, 1)
            self.rotulos[lado], self.imagens[lado] = rotulo, imagem
        self.rolagem.setWidget(dentro)
        self._roda = _RodaNaFolha(self)
        self.rolagem.viewport().installEventFilter(self._roda)
        camadas.addWidget(self.rolagem, 1)

        barra = QHBoxLayout()
        barra.setSpacing(8)
        self.botao_anterior = QPushButton("<")
        self.botao_anterior.setFixedWidth(44)
        self.botao_anterior.clicked.connect(lambda: painel.passar_folha(-1))
        barra.addWidget(self.botao_anterior)
        self.contador = QLabel("")
        self.contador.setAlignment(Qt.AlignCenter)
        barra.addWidget(self.contador, 1)
        self.bolinha = BolinhaDeCarregamento()
        barra.addWidget(self.bolinha)
        self.botao_proxima = QPushButton(">")
        self.botao_proxima.setFixedWidth(44)
        self.botao_proxima.clicked.connect(lambda: painel.passar_folha(1))
        barra.addWidget(self.botao_proxima)
        self.botao_menos = QPushButton("–")
        self.botao_menos.setToolTip("afastar")
        self.botao_menos.clicked.connect(lambda: self._zoom(0.8))
        self.botao_mais = QPushButton("+")
        self.botao_mais.setToolTip("aproximar")
        self.botao_mais.clicked.connect(lambda: self._zoom(1.25))
        for botao in (self.botao_menos, self.botao_mais):
            botao.setMinimumWidth(44)
            barra.addWidget(botao)
        self.botao_caber = QPushButton("ajustar à tela")
        self.botao_caber.clicked.connect(lambda: self._zoom(None))
        barra.addWidget(self.botao_caber)
        fechar = QPushButton("fechar")
        fechar.setObjectName("primario")
        fechar.clicked.connect(self.accept)
        barra.addWidget(fechar)
        camadas.addLayout(barra)

        tela = self.screen() or QGuiApplication.primaryScreen()
        if tela is not None:
            self.setGeometry(tela.availableGeometry())
        self.setWindowState(Qt.WindowMaximized)

    def acertar(self) -> None:
        """Põe o que o lado direito mostra agora: os textos, os botões, a bolinha e a folha."""
        p = self.painel
        for lado in (FRENTE, VERSO):
            self.rotulos[lado].setText(p.rotulos[lado].text())
            self.rotulos[lado].setVisible(p.rotulos[lado].isVisibleTo(p))
        total = p.total()
        self.contador.setText(f"Folha {p.posicao + 1} de {total}" if total else "")
        self.botao_anterior.setEnabled(p.botao_anterior.isEnabled())
        self.botao_proxima.setEnabled(p.botao_seguinte.isEnabled())
        self.bolinha.definir(p.calculando(), p.bolinha.toolTip())
        self._desenhar()

    def _desenhar(self) -> None:
        """A frente e o verso no tamanho da tela (zoom 1 = os dois cabendo), refeitos só
        quando a folha, o tamanho ou o zoom mudam."""
        pix = self.painel.pixmaps()
        if pix is None:
            for imagem in self.imagens.values():
                imagem.clear()
                imagem.setMinimumSize(1, 1)
            self._feito = None
            return
        area = self.rolagem.viewport().size()
        altura_rotulos = sum(r.sizeHint().height() + 8 for r in self.rotulos.values())
        alto = max(40, (area.height() - altura_rotulos) // 2)
        largo = max(40, area.width() - 8)
        frente = pix[0]
        escala = min(largo / max(1, frente.width()), alto / max(1, frente.height())) * self.zoom
        largura = max(1, round(frente.width() * escala))
        altura = max(1, round(frente.height() * escala))
        if self._feito == (pix, largura, altura):
            return
        self._feito = (pix, largura, altura)
        for lado, desenho in zip((FRENTE, VERSO), pix):
            self.imagens[lado].setPixmap(desenho.scaled(largura, altura, Qt.KeepAspectRatio,
                                                         Qt.SmoothTransformation))
            self.imagens[lado].setMinimumSize(largura, altura)

    def _zoom(self, fator: float | None) -> None:
        """–, + e "ajustar à tela" (1 = a frente e o verso cabendo na tela)."""
        self.zoom = 1.0 if fator is None else max(0.2, min(8.0, self.zoom * fator))
        for imagem in self.imagens.values():
            imagem.setMinimumSize(1, 1)
        self._desenhar()

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().resizeEvent(evento)
        QTimer.singleShot(0, self._desenhar)

    def keyPressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Setas e Page Up/Down passam a folha; Esc fecha."""
        if evento.key() in (Qt.Key_Left, Qt.Key_PageUp):
            self.painel.passar_folha(-1)
        elif evento.key() in (Qt.Key_Right, Qt.Key_PageDown):
            self.painel.passar_folha(1)
        else:
            super().keyPressEvent(evento)

    def done(self, resultado: int) -> None:  # noqa: D401 - nome do Qt
        """Ao fechar: as imagens saem (uma folha por vez na memória); a janela fica guardada,
        escondida, para o próximo "tela cheia"."""
        self.aberta = False
        self._feito = None
        for imagem in self.imagens.values():
            imagem.clear()
        super().done(resultado)
