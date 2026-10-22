"""Lancador do verificador-2 (05/10/2026, gravacao por tras). NAO muda o programa.

Diferencas para o lancador do verificador-1:

- o canal de comandos (comando.txt -> resposta) e lido por um FIO DE FUNDO,
  nao pelo fio da janela: a janela so faz a conta pedida (mapa / sonda), que
  chega a ela como um evento enfileirado do Qt. Assim a leitura e a escrita
  dos arquivos do canal nao param a janela (pedido do implementador);
- a resposta traz "lat": quanto o fio da janela demorou para pegar o pedido,
  medido DENTRO do processo (nao depende do disco);
- um "coracao": um relogio de 25 ms no fio da janela anota a hora; um fio
  vigia anota toda parada >= 0,25 s (inicio, duracao) em paradas.log e, se a
  parada passar de 1 s, a pilha do fio da janela naquele instante;
- cada soltar do mouse que chega ao fio da janela fica anotado (hora), para o
  piloto medir quanto o clique demorou para ser atendido.

As caixas do Windows "abrir PDF"/"escolher pasta" continuam trocadas por
respostas em arquivo, e toda janela aparece sem tomar o foco.
"""
import json
import os
import runpy
import sys
import threading
import time
import traceback
from pathlib import Path

RAIZ = os.environ["VERIF_RAIZ"]
AQUI = Path(__file__).parent
CANAL = Path(os.environ.get("VERIF_CANAL", str(AQUI)))
CANAL.mkdir(parents=True, exist_ok=True)
import faulthandler  # noqa: E402
_FALHA = open(CANAL / f"falha_{os.getpid()}.log", "w", encoding="utf-8")
faulthandler.enable(_FALHA, all_threads=True)
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)

MODELOS = Path(r"D:/programas/EditorImpressao/modelos")
if not (Path(RAIZ) / "modelos").is_dir():
    import core.detectar_regioes as _dr  # noqa: E402
    import core.rede_selecao as _rede  # noqa: E402
    _dr.CAMINHO_MODELO = MODELOS / "doclayout.onnx"
    _dr._detector.caminho = _dr.CAMINHO_MODELO
    _rede.PASTA = MODELOS / "mobile_sam"
    _rede.CODIFICADOR = _rede.PASTA / _rede.CODIFICADOR.name
    _rede.DECODIFICADOR = _rede.PASTA / _rede.DECODIFICADOR.name

from PySide6 import QtWidgets  # noqa: E402
from PySide6.QtCore import QEvent, QObject, QPoint, Qt, QTimer, Signal  # noqa: E402

# ------------------------------------------------------------ medidas
BATIDA = [time.perf_counter()]          # ultima batida do coracao (fio da janela)
SOLTAR = [0.0]                          # time.time() do ultimo soltar do mouse atendido
PARADAS = []                            # (inicio time.time(), duracao s)
FIO_JANELA = [None]


def _mover_fora(o):
    try:
        o.move(-30000, -30000)
    except RuntimeError:
        pass


class SemFoco(QObject):
    def eventFilter(self, obj, ev):  # noqa: N802
        try:
            t = ev.type()
            if t == QEvent.Type.MouseButtonRelease:
                SOLTAR[0] = time.time()
            elif t == QEvent.Type.Show and isinstance(obj, QtWidgets.QWidget) and obj.isWindow():
                obj.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
                if obj.windowHandle() is not None:
                    obj.windowHandle().setProperty("_q_showWithoutActivating", True)
                if type(obj).__name__ != "JanelaPrincipal" and not isinstance(obj, QtWidgets.QMenu):
                    QTimer.singleShot(0, lambda o=obj: _mover_fora(o))
        except Exception:  # noqa: BLE001
            pass
        return False


def _item(w, c, texto, dpr, classe=None, extra=None):
    p = c.mapTo(w, QPoint(0, 0))
    it = {"classe": classe or type(c).__name__, "texto": texto, "x": p.x() * dpr, "y": p.y() * dpr,
          "w": c.width() * dpr, "h": c.height() * dpr, "ativo": c.isEnabled(), "nome": c.objectName()}
    if extra:
        it.update(extra)
    return it


def _mapa():
    janelas = []
    for w in QtWidgets.QApplication.topLevelWidgets():
        try:
            if not w.isVisible():
                continue
        except RuntimeError:
            continue
        dpr = w.devicePixelRatioF()
        itens = []
        if isinstance(w, QtWidgets.QMenu):
            for a in w.actions():
                r = w.actionGeometry(a)
                if r.isEmpty():
                    continue
                itens.append({"classe": "acao_menu", "texto": a.text(), "x": r.x() * dpr, "y": r.y() * dpr,
                              "w": r.width() * dpr, "h": r.height() * dpr, "ativo": a.isEnabled(),
                              "marcado": a.isChecked() if a.isCheckable() else None,
                              "submenu": a.menu() is not None})
        for c in w.findChildren(QtWidgets.QWidget):
            if not c.isVisible():
                continue
            if isinstance(c, QtWidgets.QMenuBar):
                for a in c.actions():
                    r = c.actionGeometry(a)
                    p = c.mapTo(w, r.topLeft())
                    itens.append({"classe": "menu_barra", "texto": a.text(), "x": p.x() * dpr, "y": p.y() * dpr,
                                  "w": r.width() * dpr, "h": r.height() * dpr, "ativo": a.isEnabled()})
                continue
            if isinstance(c, QtWidgets.QTabBar):
                for i in range(c.count()):
                    r = c.tabRect(i)
                    p = c.mapTo(w, r.topLeft())
                    itens.append({"classe": "aba", "texto": c.tabText(i), "x": p.x() * dpr, "y": p.y() * dpr,
                                  "w": r.width() * dpr, "h": r.height() * dpr, "ativo": c.currentIndex() == i})
                continue
            extra = {}
            if isinstance(c, QtWidgets.QAbstractButton):
                texto = c.text()
                if c.isCheckable():
                    extra["marcado"] = c.isChecked()
            elif isinstance(c, QtWidgets.QLabel):
                texto = c.text()
            elif isinstance(c, QtWidgets.QComboBox):
                texto = c.currentText()
            elif isinstance(c, QtWidgets.QAbstractSlider):
                texto = str(c.value())
                extra["min"] = c.minimum(); extra["max"] = c.maximum()
            elif isinstance(c, (QtWidgets.QLineEdit, QtWidgets.QAbstractSpinBox)):
                texto = c.text()
            elif isinstance(c, QtWidgets.QGraphicsView) or type(c).__name__.lower().find("canvas") >= 0 \
                    or type(c).__name__.lower().find("vis") >= 0:
                texto = ""
                extra["vista"] = True
            else:
                if c.toolTip():
                    texto = ""
                else:
                    continue
            if c.toolTip():
                extra["dica"] = c.toolTip()
            itens.append(_item(w, c, texto, dpr, extra=extra))
        janelas.append({"titulo": w.windowTitle(), "classe": type(w).__name__, "hwnd": int(w.winId()),
                        "dpr": dpr, "w": w.width() * dpr, "h": w.height() * dpr,
                        "x": w.x(), "y": w.y(), "itens": itens})
    return janelas


def _janela_principal():
    for w in QtWidgets.QApplication.topLevelWidgets():
        if type(w).__name__ == "JanelaPrincipal":
            return w
    return None


def _executar_no_fio_da_janela(pedido):
    """Roda NO FIO DA JANELA (slot da Ponte). So conta; nada de disco."""
    if pedido == "mapa":
        return _mapa()
    if pedido.startswith("sonda "):
        jp = _janela_principal()
        ambiente = {"jp": jp, "QtWidgets": QtWidgets, "tc": getattr(jp, "tela_conferir", None),
                    "SOLTAR": SOLTAR, "PARADAS": PARADAS, "time": time}
        try:
            res = eval(pedido[6:], ambiente)  # noqa: S307 - so leitura, script do verificador
            return {"ok": True, "valor": repr(res)}
        except Exception:  # noqa: BLE001
            return {"ok": False, "erro": traceback.format_exc()}
    return {"ok": False, "erro": "comando?"}


class Ponte(QObject):
    pedido = Signal(object)

    def __init__(self):
        super().__init__()
        self.pedido.connect(self._atender)   # emitido de outro fio -> enfileirado

    def _atender(self, caixa):
        caixa["t_atendido"] = time.perf_counter()
        try:
            caixa["resultado"] = _executar_no_fio_da_janela(caixa["pedido"])
        except Exception:  # noqa: BLE001
            caixa["resultado"] = {"ok": False, "erro": traceback.format_exc()}
        caixa["t_fim"] = time.perf_counter()
        caixa["pronto"].set()


PONTE = []


def _gravar_json(nome, dados):
    tmp = CANAL / (nome + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, CANAL / nome)


def _fio_do_canal():
    """FIO DE FUNDO: le comando.txt, pede a conta ao fio da janela e grava a resposta."""
    cmd = CANAL / "comando.txt"
    while True:
        try:
            if not PONTE or not cmd.is_file():
                time.sleep(0.02)
                continue
            pedido = cmd.read_text(encoding="utf-8").strip()
            cmd.unlink()
            caixa = {"pedido": pedido, "pronto": threading.Event()}
            t0 = time.perf_counter()
            PONTE[0].pedido.emit(caixa)
            caixa["pronto"].wait(600)
            res = caixa.get("resultado", {"ok": False, "erro": "fio da janela nao atendeu em 600 s"})
            lat = caixa.get("t_atendido", time.perf_counter()) - t0
            conta = caixa.get("t_fim", time.perf_counter()) - caixa.get("t_atendido", time.perf_counter())
            if pedido == "mapa":
                _gravar_json("mapa.json", res)
            else:
                res = dict(res)
                res["lat"] = lat
                res["conta"] = conta
                _gravar_json("sonda.json", res)
        except Exception as e:  # noqa: BLE001
            try:
                (CANAL / "canal_erro.txt").write_text(repr(e) + "\n" + traceback.format_exc(), encoding="utf-8")
            except OSError:
                pass
            time.sleep(0.1)


def _bater():
    BATIDA[0] = time.perf_counter()


def _fio_vigia():
    """Anota as paradas do fio da janela (>= 0,25 s). Arquivo escrito por este fio."""
    log = CANAL / "paradas.log"
    em_parada, inicio, despejou = False, 0.0, False
    while True:
        time.sleep(0.01)
        agora = time.perf_counter()
        gap = agora - BATIDA[0]
        if gap >= 0.25:
            if not em_parada:
                em_parada, despejou = True, False
                inicio = time.time() - gap
            if gap >= 1.0 and not despejou and FIO_JANELA[0] is not None:
                despejou = True
                try:
                    quadro = sys._current_frames().get(FIO_JANELA[0])
                    pilha = "".join(traceback.format_stack(quadro)) if quadro else "?"
                    with open(log, "a", encoding="utf-8") as f:
                        f.write(f"PILHA em parada que comecou {inicio:.3f} (ja {gap:.2f} s):\n{pilha}\n")
                except Exception:  # noqa: BLE001
                    pass
        elif em_parada:
            em_parada = False
            dur = time.time() - inicio
            PARADAS.append((inicio, dur))
            try:
                with open(log, "a", encoding="utf-8") as f:
                    f.write(f"PARADA inicio={inicio:.3f} dur={dur:.3f}\n")
            except OSError:
                pass


_Original = QtWidgets.QApplication


class AppSemFoco(_Original):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        FIO_JANELA[0] = threading.get_ident()
        self._semfoco = SemFoco()
        self.installEventFilter(self._semfoco)
        PONTE.append(Ponte())
        self._coracao = QTimer()
        self._coracao.setTimerType(Qt.TimerType.PreciseTimer)
        self._coracao.timeout.connect(_bater)
        self._coracao.start(25)
        BATIDA[0] = time.perf_counter()
        threading.Thread(target=_fio_do_canal, daemon=True, name="verif canal").start()
        threading.Thread(target=_fio_vigia, daemon=True, name="verif vigia").start()


QtWidgets.QApplication = AppSemFoco


def _log(texto):
    with open(CANAL / "caixas_windows.log", "a", encoding="utf-8") as log:
        log.write(texto + "\n")


def _abrir_de_mentira(*_a, **_k):
    resp = CANAL / "resposta_abrir.txt"
    caminho = resp.read_text(encoding="utf-8").strip() if resp.is_file() else ""
    _log(f"caixa Abrir PDF respondeu: {caminho!r}")
    return caminho, ("PDF (*.pdf)" if caminho else "")


def _pasta_de_mentira(*_a, **_k):
    resp = CANAL / "resposta_pasta.txt"
    caminho = resp.read_text(encoding="utf-8").strip() if resp.is_file() else ""
    _log(f"caixa Escolher pasta respondeu: {caminho!r}")
    return caminho


if os.environ.get("VERIF_CAIXA_REAL") != "1":   # verificador-3: caixa Abrir de verdade quando pedido
    QtWidgets.QFileDialog.getOpenFileName = staticmethod(_abrir_de_mentira)
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(_pasta_de_mentira)

sys.argv = [str(Path(RAIZ) / "main.py"), *sys.argv[1:]]
runpy.run_path(str(Path(RAIZ) / "main.py"), run_name="__main__")
