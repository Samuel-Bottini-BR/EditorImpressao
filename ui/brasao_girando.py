"""A tela de carregamento: o brasao girando, solto por cima da tela (D-744, D-745, D-747).

Palavras do Samuel (17/11/2026): "pode fazer um motion dela girando em 3d sem
mudar nada no brasão, tem que continuar exactamente igual só com o movimento
enquanto carrega o programa" (D-744); "A" = "dá a volta inteira, como uma
moeda girando" e "dá para ser sem fundo?" (D-745); "brasão aprovado" para a
pagina de exemplo (D-747).

O QUE E: uma janela sem moldura, com fundo transparente, que fica por cima e
nao entra na barra de tarefas (Qt.SplashScreen). Nela so o brasao, girando no
eixo vertical, uma volta a cada 2,5 s, com a mesma perspectiva da pagina de
exemplo (CSS "perspective: 900px" e "rotateY", ver transformacao). De costas
(entre 90 e 270 graus) desenha-se o brasao de FRENTE outra vez, nunca
espelhado - como a pagina de exemplo, que tem uma segunda imagem igual virada
180 graus e "backface-visibility: hidden". De lado ele vira uma faixa fina.
O desenho nao muda: a imagem e a do vetor (gerar_brasao.py), desenhada no
tamanho da tela; so o movimento e nosso.

ONDE RODA: num processo a parte (rodar_sozinho), aberto pelo main.py antes
dos imports pesados (ui/tela_de_carregamento.py). Motivo: o programa monta a
janela principal na linha principal do Qt (medido em 17/11/2026: ~0,4 s de
import + ~1,2 s para montar + ~0,4 s para mostrar, e bem mais no primeiro
abrir depois de ligar o computador); nesse tempo nada desenha nessa linha. No
processo a parte, o giro tem o laco do Qt so para ele e fica liso enquanto o
programa carrega. O programa fecha este processo quando a janela principal
aparece; se o programa morrer antes, este processo percebe e fecha sozinho.

Arriscado mudar: o sinal de "-angulo" em transformacao (o Qt gira para o
lado contrario do CSS; o teste confere ponto a ponto contra a conta do
navegador); a regra das costas em angulo_visivel (sem ela o brasao sai
espelhado); os sinalizadores da janela (sem SplashScreen ela aparece na
barra de tarefas; sem WA_TranslucentBackground ganha fundo).
"""

from __future__ import annotations

import math
import os
import sys
import time

from PySide6.QtCore import QElapsedTimer, QPointF, Qt, QTimer
from PySide6.QtGui import QGuiApplication, QImage, QPainter, QTransform
from PySide6.QtWidgets import QApplication, QWidget

import brasao

# Folga em volta do brasao dentro da janela, em pixels de tela: de lado, a
# perspectiva aumenta a borda que chega perto (ate 900/800 = 12,5% mais alta).
FOLGA_X = 10
FOLGA_Y = 25

# O desenho e refeito a cada 16 ms (~60 por segundo).
INTERVALO_MS = 16

# Limite de seguranca: se nada fechar a janela, ela some sozinha depois disto.
LIMITE_S = 180


def angulo_visivel(angulo: float) -> float | None:
    """O angulo com que o brasao e desenhado, para o angulo da volta (graus).

    De frente (de -90 a 90) e o proprio angulo. De costas (de 90 a 270), e o
    brasao de frente com 180 graus a menos: assim o que se ve de costas e o
    lado da frente, nunca o espelho (D-745). Exatamente de lado (90 ou 270)
    nao ha o que desenhar: None.
    """
    a = angulo % 360.0
    if a > 270.0:
        a -= 360.0
    if abs(abs(a) - 90.0) < 1e-9:
        return None
    if a > 90.0:
        a -= 180.0
    return a


def angulo_no_tempo(segundos: float) -> float:
    """O angulo da volta (graus, 0 a 360) depois de `segundos`: velocidade
    sempre igual, uma volta a cada brasao.SEGUNDOS_POR_VOLTA (CSS "linear")."""
    return (segundos / brasao.SEGUNDOS_POR_VOLTA) * 360.0 % 360.0


def transformacao(angulo: float, largura: float, altura: float, centro: QPointF) -> QTransform:
    """Leva a imagem do brasao (0..largura, 0..altura) para a tela, girada.

    Igual ao CSS da pagina de exemplo: "rotateY(angulo)" em torno do meio da
    imagem, vista com "perspective: 900px" a partir do meio. No CSS, um ponto
    (x, y) do meio para fora vai para (x.cos * d / (d + x.sen), y * d / (d + x.sen)).
    O QTransform.rotate(a, YAxis, d) do Qt da d - x.sen no lugar de d + x.sen:
    gira para o outro lado. Por isso -angulo.
    """
    t = QTransform()
    t.translate(centro.x(), centro.y())
    t.rotate(-angulo, Qt.Axis.YAxis, brasao.PERSPECTIVA)
    t.translate(-largura / 2.0, -altura / 2.0)
    return t


def carregar_imagem(escala_da_tela: float) -> QImage | None:
    """A imagem do brasao ja desenhada do vetor para esta escala de tela.

    A imagem sabe a escala dela (setDevicePixelRatio): na tela ela ocupa o
    tamanho de brasao.tamanho_do_giro(), sem o Qt aumentar nem diminuir nada
    quando a escala e uma das desenhadas. None se o arquivo nao existir.
    """
    escala, arquivo = brasao.giro_para_a_escala(escala_da_tela)
    imagem = QImage(str(arquivo))
    if imagem.isNull():
        return None
    imagem.setDevicePixelRatio(escala)
    return imagem


def tamanho_da_janela() -> tuple[int, int]:
    """Largura e altura da janela do giro, em pixels de tela (escala 100%)."""
    largura, altura = brasao.tamanho_do_giro()
    # Para cima: na escala 100% a imagem tem exatamente estes pixels, e o meio
    # dela cai num pixel inteiro (de frente, o desenho sai pixel por pixel).
    return (math.ceil(largura) + 2 * FOLGA_X, math.ceil(altura) + 2 * FOLGA_Y)


def pintar(painter: QPainter, imagem: QImage, angulo: float, largura: float, altura: float) -> None:
    """Desenha o brasao no angulo da volta, no meio de uma area largura x altura.

    A mesma conta serve a janela (paintEvent) e as fotos dos testes
    (desenhar_quadro): um lugar so (CLAUDE.md 11.12).
    """
    visivel = angulo_visivel(angulo)
    if visivel is None:
        return
    w = imagem.width() / imagem.devicePixelRatio()
    h = imagem.height() / imagem.devicePixelRatio()
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setTransform(transformacao(visivel, w, h, QPointF(largura / 2.0, altura / 2.0)))
    painter.drawImage(QPointF(0.0, 0.0), imagem)
    painter.resetTransform()


def desenhar_quadro(angulo: float, escala_da_tela: float = 1.0) -> QImage:
    """Uma foto da janela do giro num angulo, sem abrir janela (para as provas).

    Fundo transparente, do tamanho da janela vezes a escala da tela.
    """
    largura, altura = tamanho_da_janela()
    quadro = QImage(int(round(largura * escala_da_tela)), int(round(altura * escala_da_tela)),
                    QImage.Format.Format_ARGB32_Premultiplied)
    quadro.setDevicePixelRatio(escala_da_tela)
    quadro.fill(Qt.GlobalColor.transparent)
    imagem = carregar_imagem(escala_da_tela)
    if imagem is not None:
        painter = QPainter(quadro)
        pintar(painter, imagem, angulo, largura, altura)
        painter.end()
    return quadro


class BrasaoGirando(QWidget):
    """A janela do brasao girando: sem moldura, transparente, por cima, fora da barra de tarefas.

    Nao recebe clique (passa para o que esta embaixo) e nao rouba o foco.
    O angulo vem do relogio (uma volta a cada brasao.SEGUNDOS_POR_VOLTA), entao
    a velocidade e a mesma mesmo se um desenho atrasar.
    """

    SINALIZADORES = (Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint
                     | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.NoDropShadowWindowHint
                     | Qt.WindowType.WindowTransparentForInput | Qt.WindowType.WindowDoesNotAcceptFocus)

    def __init__(self, escala_da_tela: float | None = None) -> None:
        super().__init__(None, self.SINALIZADORES)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAutoFillBackground(False)
        largura, altura = tamanho_da_janela()
        self.setFixedSize(largura, altura)
        tela = QGuiApplication.primaryScreen()
        if escala_da_tela is None:
            escala_da_tela = tela.devicePixelRatio() if tela is not None else 1.0
        self.imagem = carregar_imagem(escala_da_tela)
        self.angulo = 0.0
        self.relogio = QElapsedTimer()
        self.relogio.start()
        self.passo = QTimer(self)
        self.passo.setTimerType(Qt.TimerType.PreciseTimer)
        self.passo.setInterval(INTERVALO_MS)
        self.passo.timeout.connect(self._andar)

    def mostrar_no_meio(self) -> None:
        """Mostra a janela no meio da tela principal e comeca a girar."""
        tela = QGuiApplication.primaryScreen()
        if tela is not None:
            area = tela.availableGeometry()
            self.move(area.center().x() - self.width() // 2, area.center().y() - self.height() // 2)
        self.relogio.restart()
        self.passo.start()
        self.show()

    def _andar(self) -> None:
        self.angulo = angulo_no_tempo(self.relogio.elapsed() / 1000.0)
        self.update()

    def paintEvent(self, _evento) -> None:  # noqa: N802 - nome do Qt
        if self.imagem is None:
            return
        painter = QPainter(self)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        pintar(painter, self.imagem, self.angulo, self.width(), self.height())
        painter.end()


def _programa_vivo(pid: int):
    """Uma funcao que diz se o processo do programa (pid) continua aberto.

    No Windows, abre o processo uma vez (SYNCHRONIZE) e pergunta sem esperar:
    seguro mesmo se o numero do processo for reaproveitado depois.
    """
    if sys.platform == "win32":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        alca = kernel32.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
        if not alca:
            return lambda: False
        return lambda: kernel32.WaitForSingleObject(alca, 0) == 0x102  # WAIT_TIMEOUT = vivo

    def vivo() -> bool:  # pragma: no cover - fora do Windows
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    return vivo  # pragma: no cover


# D-748: quanto o brasao espera, no maximo, a janelinha da atualizacao sumir
# (ela olha a marca a cada 0,2 s; isto e so a seguranca se ela travar).
ESPERA_DA_JANELINHA_S = 3.0


def antes_de_mostrar(marcar=None, ha_janelinha=None, dormir=time.sleep,
                     limite_s: float = ESPERA_DA_JANELINHA_S) -> None:
    """D-748 (Samuel, 17/11/2026: "Sim"): a janelinha some quando o brasao aparece, nunca os dois juntos.

    A regra e uma so, a marca de "programa aberto" (atualizacao.MARCA_DE_ABERTO),
    a mesma que ja fazia a janelinha "Atualizando o programa..." (D-742) sumir
    quando a janela principal abre:
    1. o brasao poe essa marca (atualizacao.marcar_programa_aberto) - a
       janelinha a ve e fecha, ou nem aparece;
    2. so depois olha a marca da janelinha (atualizacao.ha_janelinha) e espera
       ela sumir (no maximo `limite_s`) antes de mostrar a janela.
    A janelinha faz o contrario na mesma ordem (pega a marca dela, depois olha
    a de aberto): por isso nunca ficam os dois na tela. Na abertura comum nao
    ha janelinha e nada espera.
    `marcar`, `ha_janelinha`, `dormir` e `limite_s` so mudam nos testes.
    """
    import atualizacao

    (marcar or atualizacao.marcar_programa_aberto)()
    olhar = ha_janelinha or atualizacao.ha_janelinha
    fim = time.monotonic() + limite_s
    while olhar() and time.monotonic() < fim:
        dormir(0.02)


def rodar_sozinho(pid_do_programa: str | int) -> int:
    """O processo do brasao girando (main.py --brasao-girando <pid>).

    Antes de tudo, a marca de "programa aberto" e a espera da janelinha da
    atualizacao (antes_de_mostrar, D-748). Mostra a janela e gira ate: o
    programa fechar este processo (a janela
    principal apareceu, ui/tela_de_carregamento.py), o programa morrer, ou
    passar LIMITE_S. Nunca mostra erro: sem a imagem, so sai.
    """
    try:
        pid = int(pid_do_programa)
    except (TypeError, ValueError):
        return 2
    antes_de_mostrar()          # D-748: a janelinha da atualizacao sai antes
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication.instance() or QApplication([sys.argv[0]])
    janela = BrasaoGirando()
    if janela.imagem is None:
        return 1
    vivo = _programa_vivo(pid)
    comeco = time.monotonic()

    def vigiar() -> None:
        if not vivo() or time.monotonic() - comeco > LIMITE_S:
            app.quit()

    vigia = QTimer()
    vigia.timeout.connect(vigiar)
    vigia.start(200)
    janela.mostrar_no_meio()
    return app.exec()
