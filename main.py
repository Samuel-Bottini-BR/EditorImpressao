"""Editor de Impressão - ponto de entrada.

Recupera PDFs de livros antigos escaneados e prepara para reimpressao.
"""

from __future__ import annotations

import sys
import traceback


def main() -> int:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QMessageBox

    from registro import registrar_erro

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Editor de Impressão")

    # Rede de seguranca final: qualquer erro nao tratado vira aviso em
    # portugues e o programa continua aberto (regra 3.3).
    def tratar(tipo, valor, rastro) -> None:
        registrar_erro("não tratado", "".join(traceback.format_exception(tipo, valor, rastro)))
        QMessageBox.information(
            None, "Um momento",
            "Aconteceu um problema inesperado, mas o programa continua funcionando.",
        )

    sys.excepthook = tratar

    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.show()

    if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".pdf"):
        janela.abrir_livro(sys.argv[1])

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
