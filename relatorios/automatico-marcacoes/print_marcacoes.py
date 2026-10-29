"""Print 1280x657, sem janela na tela: "Na escola de Jesus" (cópia do projeto de teste em _tmp),
página 12, ferramenta Zoom, com o botão "marcações" desligado (de fábrica) e ligado.
Uso: python relatorios/automatico-marcacoes/print_marcacoes.py <pasta de saida>
Antes, copiar o projeto da pasta de dados de teste para _tmp/dados/EditorImpressao/projetos/."""
import os
import sys
import time
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
RAIZ = Path(__file__).resolve().parents[2]   # a raiz da worktree (o script mora em relatorios/automatico-marcacoes)
sys.path.insert(0, str(RAIZ))
DADOS = RAIZ / "_tmp" / "dados"
os.environ["LOCALAPPDATA"] = str(DADOS)
SAIDA = Path(sys.argv[1])
SAIDA.mkdir(parents=True, exist_ok=True)
ORIGINAL = (r"D:/programas/EditorImpressao-arquivos/dados-teste-rodada-de-consertos/EditorImpressao/"
            r"projetos/Na escola de Jesus - Catecismo explicado com imagens/projeto.json")
LIVRO = (r"D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/"
         r"Na escola de Jesus - Catecismo explicado com imagens..pdf")


def main() -> int:
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

    app = QApplication(sys.argv)
    from ui import rodinha
    from ui.dialogos_de_arquivo import traduzir_o_qt

    rodinha.instalar_no_programa(app)
    traduzir_o_qt(app)

    caixas = []

    def recusar(self, *a, **k):          # nenhuma caixa fica esperando clique
        caixas.append(type(self).__name__ + ": " + (self.windowTitle() or ""))
        return 0

    QDialog.exec = recusar
    QMessageBox.exec = recusar
    QTimer.singleShot(240000, lambda: (print("tempo esgotado"), app.exit(3)))

    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    janela.show()
    janela.abrir_livro(LIVRO)

    def assentar(segundos: float) -> None:
        fim = time.monotonic() + segundos
        while time.monotonic() < fim:
            app.processEvents()
            time.sleep(0.03)

    assentar(3)
    tela = janela.tela_conferir
    tela.escolher_ferramenta("zoom")
    tela.ir_para_pagina(11)
    editor = tela.editor_selecao
    fim = time.monotonic() + 120
    while time.monotonic() < fim and (editor._pixmap is None or editor._pixmap.isNull()):
        assentar(0.2)
    assentar(4)                           # a prévia boa e as bolinhas assentam
    janela.resize(1280, 657)
    assentar(1)
    print("tamanho", janela.width(), janela.height(), "botao", tela.botao_marcacoes.isChecked())
    janela.grab().save(str(SAIDA / "marcacoes-1-desligado-de-fabrica.jpg"), "JPG", 85)
    tela.botao_marcacoes.click()
    assentar(1.5)
    print("botao depois do clique", tela.botao_marcacoes.isChecked())
    janela.grab().save(str(SAIDA / "marcacoes-2-ligado.jpg"), "JPG", 85)
    # D-584: desliga no botão, volta ao Zoom e escolhe o Pincel: as marcações acendem sozinhas
    tela.botao_marcacoes.click()
    tela.escolher_ferramenta("zoom")
    assentar(0.5)
    tela.escolher_ferramenta("pincel")
    assentar(1.5)
    print("botao com o Pincel", tela.botao_marcacoes.isChecked())
    janela.grab().save(str(SAIDA / "marcacoes-3-pincel-acende-sozinho.jpg"), "JPG", 85)
    print("caixas", caixas)
    if janela.previas is not None:
        janela.previas.parar()
    janela._salvar_agora()
    janela.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
