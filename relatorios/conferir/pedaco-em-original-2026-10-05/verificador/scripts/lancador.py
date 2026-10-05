"""Lancador do verificador de tela (02/10/2026, prints na tela do Samuel).

Roda o main.py da pasta principal (ramo fase-1) SEM mudar nada do programa.
O que este arquivo acrescenta, so por fora:

- toda janela do programa aparece SEM tomar o foco (WA_ShowWithoutActivating),
  para nao roubar o teclado do Samuel; desta vez ela fica NA TELA (autorizado);
- as caixas do Windows "abrir PDF" e "escolher pasta" sao trocadas por uma
  resposta lida de resposta_abrir.txt / resposta_pasta.txt (caminhos sempre
  dentro de dados/), e anotadas em caixas_windows.log;
- um canal de LEITURA (comando.txt -> mapa.json): grava cada janela visivel e
  os botoes, rotulos, abas, menus e deslizantes dela, com texto e posicao em
  pixels. Os cliques e teclas continuam sendo mensagens nativas do Windows
  (piloto.py). O comando "sonda <expr>" avalia uma expressao SO DE LEITURA
  (ex.: valor gravado no projeto) e grava o resultado em sonda.json.
"""
import json
import os
import runpy
import sys
import traceback
from pathlib import Path

RAIZ = r"D:/programas/EditorImpressao/.claude/worktrees/consertos3"
AQUI = Path(__file__).parent
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)

from PySide6 import QtWidgets  # noqa: E402
from PySide6.QtCore import QEvent, QObject, QPoint, Qt, QTimer  # noqa: E402


class SemFoco(QObject):
    def eventFilter(self, obj, ev):  # noqa: N802
        try:
            if ev.type() == QEvent.Type.Show and isinstance(obj, QtWidgets.QWidget) and obj.isWindow():
                obj.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
                if obj.windowHandle() is not None:
                    obj.windowHandle().setProperty("_q_showWithoutActivating", True)
                # verificador 05/10: caixas e janelas secundarias tambem fora da
                # tela (a principal e posta fora pelo passo.py)
                if type(obj).__name__ != "JanelaPrincipal" and not isinstance(obj, QtWidgets.QMenu):
                    QTimer.singleShot(0, lambda o=obj: o.move(-30000, -30000))
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
        except RuntimeError:  # menu ja apagado pelo Qt
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


def _vigiar_comando():
    cmd = AQUI / "comando.txt"
    try:
        if not cmd.is_file():
            return
        pedido = cmd.read_text(encoding="utf-8").strip()
        cmd.unlink()
        if pedido == "mapa":
            tmp = AQUI / "mapa.tmp"
            tmp.write_text(json.dumps(_mapa(), ensure_ascii=False, indent=1), encoding="utf-8")
            os.replace(tmp, AQUI / "mapa.json")
        elif pedido.startswith("sonda "):
            jp = _janela_principal()
            ambiente = {"jp": jp, "QtWidgets": QtWidgets, "tc": getattr(jp, "tela_conferir", None)}
            try:
                res = eval(pedido[6:], ambiente)  # noqa: S307 - so leitura, script do verificador
                saida = {"ok": True, "valor": repr(res)}
            except Exception:  # noqa: BLE001
                saida = {"ok": False, "erro": traceback.format_exc()}
            tmp = AQUI / "sonda.tmp"
            tmp.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
            os.replace(tmp, AQUI / "sonda.json")
    except Exception as e:  # noqa: BLE001
        (AQUI / "mapa_erro.txt").write_text(repr(e) + "\n" + traceback.format_exc(), encoding="utf-8")


_Original = QtWidgets.QApplication


class AppSemFoco(_Original):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._semfoco = SemFoco()
        self.installEventFilter(self._semfoco)
        self._relogio = QTimer()
        self._relogio.timeout.connect(_vigiar_comando)
        self._relogio.start(250)


QtWidgets.QApplication = AppSemFoco


def _log(texto):
    with open(AQUI / "caixas_windows.log", "a", encoding="utf-8") as log:
        log.write(texto + "\n")


def _abrir_de_mentira(*_a, **_k):
    resp = AQUI / "resposta_abrir.txt"
    caminho = resp.read_text(encoding="utf-8").strip() if resp.is_file() else ""
    _log(f"caixa Abrir PDF respondeu: {caminho!r}")
    return caminho, ("PDF (*.pdf)" if caminho else "")


def _pasta_de_mentira(*_a, **_k):
    resp = AQUI / "resposta_pasta.txt"
    caminho = resp.read_text(encoding="utf-8").strip() if resp.is_file() else ""
    _log(f"caixa Escolher pasta respondeu: {caminho!r}")
    return caminho


QtWidgets.QFileDialog.getOpenFileName = staticmethod(_abrir_de_mentira)
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(_pasta_de_mentira)

sys.argv = [str(Path(RAIZ) / "main.py"), *sys.argv[1:]]
runpy.run_path(str(Path(RAIZ) / "main.py"), run_name="__main__")
