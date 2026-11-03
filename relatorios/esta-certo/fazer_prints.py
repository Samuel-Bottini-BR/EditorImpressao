"""D-572: prints 1280x657, sem janela na tela (offscreen), do Gradus Primus (cópia em <worktree>/_tmp,
pasta de dados separada em <worktree>/_tmp/dados via LOCALAPPDATA), antes e depois do conserto.

Caminho: abrir o livro, Automático só com "Dividir" (como o Kaique e como o print a-43 do Samuel).
  <lado>-1-dividir-folha-1.jpg       Dividir, folha 1, depois de "está certo"
  <lado>-2-dividir-folha-2.jpg       Dividir, folha 2 (sem o ok): a faixa de sempre com o "está certo"
  <lado>-3-filtro-pagina-5.jpg       ferramenta Filtro (os quatro filtros), página 5, depois de "está certo"
  <lado>-4-filtro-pagina-6.jpg       a página 6 (sem o ok)
<lado> = "antes" (o ui/tela_conferir.py do a3a7405, lido de _tmp/antes/tela_conferir.py) ou "depois"
(o desta cópia).

Uso (na raiz da worktree):
  QT_QPA_FONTDIR=C:/Windows/Fonts python relatorios/esta-certo/fazer_prints.py depois
  git show a3a7405:ui/tela_conferir.py > _tmp/antes/tela_conferir.py
  QT_QPA_FONTDIR=C:/Windows/Fonts python relatorios/esta-certo/fazer_prints.py antes
Sem o QT_QPA_FONTDIR o modo sem janela não acha as letras. Nada é gravado fora de _tmp e desta pasta."""
import importlib.util
import os
import shutil
import sys
import time
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
RAIZ = Path(__file__).resolve().parents[2]   # a raiz da worktree
sys.path.insert(0, str(RAIZ))
LADO = sys.argv[1] if len(sys.argv) > 1 else "depois"
os.environ["LOCALAPPDATA"] = str(RAIZ / "_tmp" / f"dados-{LADO}")
SAIDA = Path(__file__).resolve().parent
ORIGINAL = Path(r"C:/Users/fotog/Desktop/Estudos/Latim/pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
COPIA = RAIZ / "_tmp" / "gradus-primus.pdf"


def _codigo_antigo() -> None:
    """No lado "antes", o ui.tela_conferir vem do a3a7405 (o único arquivo do programa que mudou)."""
    antigo = RAIZ / "_tmp" / "antes" / "tela_conferir.py"
    spec = importlib.util.spec_from_file_location("ui.tela_conferir", antigo)
    modulo = importlib.util.module_from_spec(spec)
    import ui
    sys.modules["ui.tela_conferir"] = modulo
    ui.tela_conferir = modulo
    spec.loader.exec_module(modulo)


def main() -> int:
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

    if not COPIA.exists():
        COPIA.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ORIGINAL, COPIA)
    app = QApplication(sys.argv)
    if LADO == "antes":
        _codigo_antigo()
    from ui import rodinha
    from ui.dialogos_de_arquivo import traduzir_o_qt

    rodinha.instalar_no_programa(app)
    traduzir_o_qt(app)
    QDialog.exec = lambda self, *a, **k: 0          # nenhuma caixa fica esperando clique
    QMessageBox.exec = lambda self, *a, **k: 0
    QTimer.singleShot(900000, lambda: (print("tempo esgotado"), app.exit(3)))

    from core import automatico as A
    from ui.janela_principal import JanelaPrincipal
    from ui.tela_conferir import PAINEL_FILTRO

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    janela.show()
    janela.abrir_livro(str(COPIA))

    def assentar(segundos: float) -> None:
        fim = time.monotonic() + segundos
        while time.monotonic() < fim:
            app.processEvents()
            time.sleep(0.03)

    assentar(3)
    estado = janela.estado_do_automatico
    estado.marcadas = {A.DIVIDIR}
    estado.alcance = "livro"
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    assentar(3)
    fim = time.monotonic() + 300
    while time.monotonic() < fim and getattr(janela, "medida_ao_abrir", None) is not None:
        assentar(0.5)
    tela = janela.tela_conferir
    print(LADO, "folhas:", len(janela.projeto.folhas), "páginas:", len(janela.projeto.paginas))

    def foto(nome: str) -> None:
        assentar(4)
        janela.resize(1280, 657)
        assentar(0.5)
        print(nome, "|", tela.texto_faixa.text(), "| está certo à vista:",
              tela.botao_esta_certo.isVisibleTo(tela), "| próxima dúvida à vista:",
              tela.botao_proxima_duvida.isVisibleTo(tela), "|", tela.rotulo_do_livro.text())
        janela.grab().save(str(SAIDA / f"{LADO}-{nome}"), "JPG", 85)

    tela.escolher_ferramenta("dividir")
    tela._ir_para(0)
    assentar(1)
    tela.botao_esta_certo.click()
    tela._ir_para(0)                  # se o clique foi a outra dúvida, volta à folha 1
    foto("1-dividir-folha-1.jpg")
    tela._ir_para(1)
    foto("2-dividir-folha-2.jpg")

    tela.escolher_ferramenta("filtros")
    tela.paineis.abrir(PAINEL_FILTRO)
    tela.ir_para_pagina(4)
    assentar(1)
    tela.botao_esta_certo.click()
    tela.ir_para_pagina(4)
    foto("3-filtro-pagina-5.jpg")
    tela.ir_para_pagina(5)
    foto("4-filtro-pagina-6.jpg")
    print("ferramenta da vez:", tela.aba_atual)

    janela._fechar_a_janela_do_automatico()
    if janela.previas is not None:
        janela.previas.parar()
    janela.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
