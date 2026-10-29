"""D-582: prints 1280x657, sem janela na tela (offscreen), do "Na escola de Jesus" depois do
Automático (cópia do projeto de teste em <worktree>/_tmp/dados), página 1 (a capa do print dele),
ferramenta Zoom (a página limpa, D-580), painel "Filtro da página" aberto:
  1 e 2: "Uma página", com Preto e branco e depois Mágico pro;
  3 e 4: "antes / depois", com Preto e branco e depois Mágico pro.
Uso: python relatorios/automatico-filtro/fazer_prints.py
Antes, copiar o projeto da pasta de dados de teste para _tmp/dados/EditorImpressao/projetos/
(e apontar a "pasta" do resumo.json para a cópia)."""
import os
import sys
import time
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
RAIZ = Path(__file__).resolve().parents[2]   # a raiz da worktree
sys.path.insert(0, str(RAIZ))
os.environ["LOCALAPPDATA"] = str(RAIZ / "_tmp" / "dados")
SAIDA = Path(__file__).resolve().parent
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
    QDialog.exec = lambda self, *a, **k: 0          # nenhuma caixa fica esperando clique
    QMessageBox.exec = lambda self, *a, **k: 0
    QTimer.singleShot(300000, lambda: (print("tempo esgotado"), app.exit(3)))

    from ui.janela_principal import JanelaPrincipal
    from ui.tela_conferir import PAINEL_FILTRO

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
    tela.ir_para_pagina(0)
    tela.paineis.abrir(PAINEL_FILTRO)
    pagina = janela.projeto.paginas[0]
    print("partida:", pagina.filtro, "limpar:", janela.projeto.limpar,
          "marcacao:", len(pagina.selecao or []), "areas")

    def escolher_e_fotografar(filtro: str, nome: str, antes_depois: bool) -> None:
        tela.paineis.filtro_da_pagina.filtro_escolhido.emit(filtro)
        fim = time.monotonic() + 120
        while time.monotonic() < fim:
            app.processEvents()
            pronta = tela.previas.ja_pronta(0, tela._dpi_atual)
            if antes_depois:
                vista = tela.vista_antes_depois
                if pronta is not None and vista.depois is not None and vista.antes is not None:
                    break
            elif pronta is not None and tela.editor_selecao._img is pronta:
                break
            time.sleep(0.03)
        assentar(4)                              # os cartões do painel e a barra assentam
        janela.resize(1280, 657)
        assentar(0.5)
        print(nome, "filtro:", pagina.filtro, "tamanho:", janela.width(), janela.height())
        janela.grab().save(str(SAIDA / nome), "JPG", 85)

    escolher_e_fotografar("preto_e_branco", "1-uma-pagina-preto-e-branco.jpg", False)
    escolher_e_fotografar("magico_pro", "2-uma-pagina-magico-pro.jpg", False)
    escolher_e_fotografar("original", "_volta-ao-original.jpg", False)
    tela.botao_antes_depois.click()
    assentar(1)
    escolher_e_fotografar("preto_e_branco", "3-antes-depois-preto-e-branco.jpg", True)
    escolher_e_fotografar("magico_pro", "4-antes-depois-magico-pro.jpg", True)
    (SAIDA / "_volta-ao-original.jpg").unlink(missing_ok=True)
    if janela.previas is not None:
        janela.previas.parar()
    janela._salvar_agora()
    janela.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
