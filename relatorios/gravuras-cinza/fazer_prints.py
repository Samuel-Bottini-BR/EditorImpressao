"""D-588: prints 1280x657, sem janela na tela (offscreen), do "Na escola de Jesus" (cópia do projeto
de teste em <worktree>/_tmp/dados, depois do Automático, com a marcação que o "Gravuras e fotos"
deixou), página 1 (a capa), Preto e branco, ferramenta Zoom, painel "Filtro da página" aberto:
  1: caixinha "Gravuras em tons de cinza" desmarcada (a pintura guarda a cor: D-585);
  2: marcada (a pintura em tons de cinza, o texto preto e branco);
  3: "antes / depois", marcada;
  4: "Só as letras" ligado na página: a caixinha cinza (pergunta ao Samuel);
  5: "Respeitar as gravuras achadas" desligada: a caixinha cinza (pergunta ao Samuel);
  6: a tela cheia dos filtros, no Preto e branco, com a caixinha marcada;
  7: a janela grande do Automático, etapa "Limpar a folha", Preto e branco.
E a capa desenhada (o desenho da tela e do PDF, core.pipeline.renderizar_pagina, 110 DPI) sem e
com a caixinha: capa-sem-a-caixinha.jpg e capa-com-a-caixinha.jpg.
Por onde a capa passou: endireitada, cortada, "Limpar a folha", "Gravuras e fotos" (a marcação
do Automático do livro dele), Preto e branco, "Respeitar as gravuras achadas" ligada (na cópia
ela estava desligada, como o Samuel deixou; o script a liga antes), "Só as letras" desligado.
Uso: QT_QPA_FONTDIR=C:/Windows/Fonts python relatorios/gravuras-cinza/fazer_prints.py
(sem o QT_QPA_FONTDIR, o modo sem janela não acha as letras e os textos saem como quadradinhos)
Antes, copiar o projeto da pasta de dados de teste para _tmp/dados/EditorImpressao/projetos/ (e
apontar a "pasta" do resumo.json para a cópia). Nada é gravado fora de _tmp e desta pasta."""
import copy
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
    import cv2
    import numpy as np
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QCheckBox, QDialog, QMessageBox

    app = QApplication(sys.argv)
    from ui import rodinha
    from ui.dialogos_de_arquivo import traduzir_o_qt

    rodinha.instalar_no_programa(app)
    traduzir_o_qt(app)
    QDialog.exec = lambda self, *a, **k: 0          # nenhuma caixa fica esperando clique
    QMessageBox.exec = lambda self, *a, **k: 0
    QTimer.singleShot(600000, lambda: (print("tempo esgotado"), app.exit(3)))

    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina
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
    projeto = janela.projeto
    pagina = projeto.paginas[0]
    print("partida:", pagina.filtro, "marcacao:", len(pagina.selecao or []), "areas",
          "respeitar:", pagina.respeitar_gravuras_achadas)
    if pagina.filtro != "preto_e_branco":
        tela.paineis.filtro_da_pagina.filtro_escolhido.emit("preto_e_branco")
    if not tela.caixa_respeitar_gravuras.isChecked():
        tela.caixa_respeitar_gravuras.click()
    assentar(0.5)
    caixa = tela.caixa_gravuras_cinza

    def desenho(nome: str) -> np.ndarray:
        doc = abrir_pdf(projeto.caminho_entrada)
        try:
            img, _ = renderizar_pagina(doc, copy.deepcopy(projeto), copy.deepcopy(pagina), dpi=110)
        finally:
            doc.close()
        cv2.imwrite(str(SAIDA / nome), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return img

    def esperar_e_fotografar(nome: str, antes_depois: bool) -> None:
        fim = time.monotonic() + 240
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
        assentar(4)
        janela.resize(1280, 657)
        assentar(0.5)
        print(nome, "filtro:", pagina.filtro, "cinza:", pagina.gravuras_em_tons_de_cinza,
              "caixinha:", caixa.isChecked(), "habilitada:", caixa.isEnabled(),
              "visivel:", caixa.isVisibleTo(tela))
        janela.grab().save(str(SAIDA / nome), "JPG", 85)

    def por_a_caixinha(marcada: bool) -> None:
        if caixa.isChecked() != marcada:
            caixa.click()
        assentar(0.3)

    por_a_caixinha(False)
    sem = desenho("capa-sem-a-caixinha.jpg")
    esperar_e_fotografar("1-capa-sem-a-caixinha.jpg", False)
    por_a_caixinha(True)
    com = desenho("capa-com-a-caixinha.jpg")
    esperar_e_fotografar("2-capa-com-a-caixinha.jpg", False)
    for nome, img in (("sem", sem), ("com", com)):
        hsv = cv2.cvtColor(img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR),
                           cv2.COLOR_BGR2HSV)
        cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print(f"capa {nome} a caixinha: canais={img.ndim}, pontos coloridos="
              f"{float((hsv[:, :, 1] > 60).mean()):.1%}, tons do meio="
              f"{float(((cinza > 10) & (cinza < 245)).mean()):.1%}")
    tela.botao_antes_depois.click()
    assentar(1)
    esperar_e_fotografar("3-antes-depois-com-a-caixinha.jpg", True)
    tela.botao_antes_depois.click()
    assentar(1)
    so_as_letras = next(c for c in tela.paineis.filtro_da_pagina.findChildren(QCheckBox)
                        if c.text() == "Só as letras" and c.isVisibleTo(tela))
    so_as_letras.click()
    assentar(0.5)
    esperar_e_fotografar("4-so-as-letras-caixinha-cinza.jpg", False)
    so_as_letras.click()
    assentar(0.5)
    tela.caixa_respeitar_gravuras.click()
    assentar(0.5)
    esperar_e_fotografar("5-respeitar-desligada-caixinha-cinza.jpg", False)
    tela.caixa_respeitar_gravuras.click()
    assentar(0.5)

    # 6: a tela cheia dos filtros
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia
    dialogo = FiltrosEmTelaCheia(tela)
    dialogo.escolher("preto_e_branco")
    dialogo.show()
    dialogo.resize(1280, 657)
    fim = time.monotonic() + 240
    while dialogo._imagem("preto_e_branco") is None and time.monotonic() < fim:
        assentar(0.2)
    assentar(2)
    print("tela cheia: caixinha", dialogo.caixa_gravuras_cinza.text(),
          "marcada:", dialogo.caixa_gravuras_cinza.isChecked())
    dialogo.grab().save(str(SAIDA / "6-tela-cheia-com-a-caixinha.jpg"), "JPG", 85)
    dialogo.reject()
    assentar(0.5)

    # 7: a janela grande do Automático, "Limpar a folha", Preto e branco
    from core import automatico as A
    grande = janela.abrir_o_automatico()
    if grande is not None:
        grande.radios_de_filtro["preto_e_branco"].setChecked(True)
        grande.estado.definir_opcao("misto_so_as_letras", False)   # só na janela (sem Rodar)
        grande.mostrar_etapa(A.LIMPAR)
        assentar(3)
        grande.paginas_das_etapas[A.LIMPAR].ensureWidgetVisible(grande.cx_gravuras_cinza, 50, 120)
        alvo = grande.window() if hasattr(grande, "window") else grande
        try:
            alvo.resize(1280, 657)
        except Exception:  # noqa: BLE001
            pass
        assentar(2)
        print("automatico: caixinha", grande.cx_gravuras_cinza.text(),
              "visivel:", grande.cx_gravuras_cinza.isVisibleTo(grande.cx_gravuras_cinza.window()))
        alvo.grab().save(str(SAIDA / "7-automatico-limpar-a-folha.jpg"), "JPG", 85)
        janela._fechar_a_janela_do_automatico()
    if janela.previas is not None:
        janela.previas.parar()
    janela._salvar_agora()
    janela.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
