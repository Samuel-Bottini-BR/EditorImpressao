"""Conferencia guiada: uma amostra por vez, e o veredito de quem esta olhando.

    .venv\\Scripts\\python.exe conferir.py
    .venv\\Scripts\\python.exe conferir.py "caminho\\da\\pasta"

Abre as imagens de uma pasta uma a uma, em tela cheia, com dois botoes e uma
caixa para escrever o que esta errado. No fim grava o relatorio nos tres
formatos, dentro da pasta de testes.

## Por que isto existe

O gargalo do projeto nao e medir - e olhar. A regua diz que uma pagina passou
nos numeros; so o olho diz se ela esta certa. Ate aqui isso era feito abrindo
arquivo por arquivo no explorador e anotando em outro lugar, e a anotacao se
perdia.

## Ditado

A caixa de texto e uma caixa de texto comum do Windows, entao o **ditado do
proprio Windows funciona nela: aperte Win+H e fale**. Nao ha nada a instalar, e
nenhuma biblioteca nova entrou no programa por causa disto.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import relatorio  # noqa: E402
from ui.estilo import FOLHA_DE_ESTILO, TEXTO_FRACO, VERDE, VERMELHO  # noqa: E402

EXTENSOES = {".png", ".jpg", ".jpeg", ".webp"}


class Conferencia(QWidget):
    """Uma imagem por vez, e o que a pessoa disse sobre ela."""

    def __init__(self, imagens: list[Path], assunto: str) -> None:
        """Monta a janela de conferencia com os atalhos de teclado (espaco =
        certa, seta esquerda = voltar, Ctrl+Enter = errada) e mostra a
        primeira imagem."""
        super().__init__()
        self.imagens = imagens
        self.assunto = assunto
        self.vereditos: list[dict[str, str]] = []
        self.atual = 0

        self.setWindowTitle("Conferir as amostras")
        self.resize(1280, 900)

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(18, 14, 18, 14)
        camadas.setSpacing(10)

        self.titulo = QLabel("")
        self.titulo.setStyleSheet("font-size: 17px; font-weight: 600;")
        camadas.addWidget(self.titulo)

        self.figura = QLabel("")
        self.figura.setAlignment(Qt.AlignCenter)
        self.figura.setMinimumHeight(520)
        self.figura.setStyleSheet("background: #ffffff; border: 1px solid #d1d5db;")
        camadas.addWidget(self.figura, 1)

        dica = QLabel(
            "Diga o que está errado - para falar em vez de digitar, aperte "
            "Win+H e fale. Deixe em branco se estiver certo."
        )
        dica.setStyleSheet(f"color: {TEXTO_FRACO};")
        camadas.addWidget(dica)

        self.caixa = QPlainTextEdit()
        self.caixa.setFixedHeight(96)
        self.caixa.setPlaceholderText("o que está errado nesta...")
        camadas.addWidget(self.caixa)

        linha = QHBoxLayout()
        self.contador = QLabel("")
        self.contador.setStyleSheet(f"color: {TEXTO_FRACO};")
        linha.addWidget(self.contador)
        linha.addStretch()

        voltar = QPushButton("voltar uma")
        voltar.clicked.connect(self.voltar)
        linha.addWidget(voltar)

        errado = QPushButton("está errada")
        errado.setStyleSheet(f"color: {VERMELHO}; font-weight: 600;")
        errado.clicked.connect(lambda: self.responder(False))
        linha.addWidget(errado)

        certo = QPushButton("está certa")
        certo.setObjectName("primario")
        certo.setStyleSheet(f"color: {VERDE}; font-weight: 600;")
        certo.clicked.connect(lambda: self.responder(True))
        linha.addWidget(certo)
        camadas.addLayout(linha)

        QShortcut(QKeySequence(Qt.Key_Space), self, lambda: self.responder(True))
        QShortcut(QKeySequence(Qt.Key_Left), self, self.voltar)
        QShortcut(QKeySequence("Ctrl+Return"), self, lambda: self.responder(False))

        self.mostrar()

    def mostrar(self) -> None:
        """Exibe a imagem atual (ou termina a conferencia se acabaram as imagens)."""
        if self.atual >= len(self.imagens):
            self.terminar()
            return
        caminho = self.imagens[self.atual]
        self.titulo.setText(caminho.stem)
        self.contador.setText(f"{self.atual + 1} de {len(self.imagens)}")
        figura = QPixmap(str(caminho))
        if not figura.isNull():
            self.figura.setPixmap(figura.scaled(
                self.figura.width(), self.figura.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.caixa.setPlainText("")
        self.caixa.setFocus()

    def resizeEvent(self, evento):  # noqa: N802 - nome do Qt
        """Reescala a imagem atual quando a janela muda de tamanho."""
        super().resizeEvent(evento)
        if self.atual < len(self.imagens):
            figura = QPixmap(str(self.imagens[self.atual]))
            if not figura.isNull():
                self.figura.setPixmap(figura.scaled(
                    self.figura.width(), self.figura.height(),
                    Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def responder(self, certa: bool) -> None:
        """Registra o veredito da imagem atual e avanca para a proxima.
        "certa" com algo escrito ainda vira ERRADA - o texto e sempre uma ressalva."""
        dito = self.caixa.toPlainText().strip()
        self.vereditos.append({
            "imagem": self.imagens[self.atual].name,
            "veredito": "certa" if certa and not dito else "ERRADA",
            "o_que_disse": dito,
        })
        self.atual += 1
        self.mostrar()

    def voltar(self) -> None:
        """Desfaz o ultimo veredito e volta uma imagem, devolvendo o que foi escrito."""
        if self.atual > 0:
            self.atual -= 1
            if self.vereditos:
                anterior = self.vereditos.pop()
                self.mostrar()
                self.caixa.setPlainText(anterior["o_que_disse"])

    def terminar(self) -> None:
        """Monta o relatorio final (tabela de erradas + tabela completa) e
        grava nos tres formatos (regra do CLAUDE.md secao 2 - ver relatorio.gravar)."""
        pasta = relatorio.pasta_de_teste(self.assunto, "")
        erradas = [v for v in self.vereditos if v["veredito"] == "ERRADA"]

        L = [f"# Conferencia: {self.assunto}", ""]
        L.append(f"Foram olhadas **{len(self.vereditos)} imagens**, uma a uma.")
        L.append("")
        L.append(f"**{len(self.vereditos) - len(erradas)} certas, "
                 f"{len(erradas)} erradas.**")
        L.append("")
        if erradas:
            L.append("## O que esta errado")
            L.append("")
            L.append("| Imagem | O que foi dito |")
            L.append("|---|---|")
            for v in erradas:
                L.append(f"| {v['imagem']} | {v['o_que_disse'] or '(sem detalhe)'} |")
            L.append("")
        L.append("## Uma a uma")
        L.append("")
        L.append("| Imagem | Veredito | O que foi dito |")
        L.append("|---|---|---|")
        for v in self.vereditos:
            L.append(f"| {v['imagem']} | {v['veredito']} | {v['o_que_disse']} |")

        escritos = relatorio.gravar("\n".join(L), pasta / "o que foi conferido",
                                    titulo=f"Conferencia: {self.assunto}")
        print(f"{len(self.vereditos) - len(erradas)} certas, {len(erradas)} erradas.")
        print(f"Relatorio: {escritos['md']}")
        self.close()


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada de linha de comando: acha as imagens na pasta pedida
    (ou relatorios/selecao por padrão) e abre a janela de conferencia."""
    argv = list(sys.argv[1:] if argv is None else argv)
    pasta = Path(argv[0]) if argv else (RAIZ / "relatorios" / "selecao")
    if not pasta.is_dir():
        print(f"Nao achei a pasta: {pasta}")
        return 2

    imagens = sorted(p for p in pasta.iterdir()
                     if p.suffix.lower() in EXTENSOES)
    if not imagens:
        print(f"Nao ha imagem em {pasta}")
        return 2

    assunto = argv[1] if len(argv) > 1 else f"conferencia de {pasta.name}"

    app = QApplication.instance() or QApplication([])
    try:
        app.setStyleSheet(FOLHA_DE_ESTILO)
    except Exception:  # noqa: BLE001 - sem estilo a tela continua servindo
        pass
    janela = Conferencia(imagens, assunto)
    janela.show()
    app.exec()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
