"""Editor de Impressão - ponto de entrada.

Recupera PDFs de livros antigos escaneados e prepara para reimpressao.
"""

from __future__ import annotations

import sys
import traceback


def main() -> int:
    """Sobe o QApplication, arma a rede de seguranca contra excecao nao
    tratada (regra 3.3: nunca stack trace na tela) e abre a janela principal.
    Se o programa foi chamado com um caminho de PDF (associacao de arquivo do
    instalador), abre esse livro direto."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QMessageBox

    from registro import registrar_erro

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Editor de Impressão")

    # Aquece em segundo plano o import pesado que o filtro Preto e branco
    # faria sob demanda - ver core/aquecimento.py para o motivo.
    from core.aquecimento import aquecer_em_segundo_plano

    aquecer_em_segundo_plano()

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
    # Conferência dos detectores de texto, sem janela (item 1.3): prova que o
    # programa EMPACOTADO acha o docTR, o Tesseract e o motor do Kraken. Ver
    # core/ocr_diagnostico.py. Não é usada pelo Kaique.
    if len(sys.argv) > 1 and sys.argv[1] == "--conferir-ocr":
        from core.ocr_diagnostico import linha_de_comando

        raise SystemExit(linha_de_comando(sys.argv[2:]))
    raise SystemExit(main())
