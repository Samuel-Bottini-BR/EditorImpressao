"""Conserto de 02/11/2026 (o cinza sem o "Respeitar"): prints de ANTES e DEPOIS, sem janela na tela.

Roda com o código da pasta em argv[1] (o 091b200, de antes do conserto, ou esta cópia) e grava os
prints com o sufixo argv[2] ("antes" ou "depois") nesta pasta. Livro: "Na escola de Jesus", página
13 de 199 (Jonas e a baleia), onde o Samuel testou em 02/11, numa CÓPIA do projeto da pasta de
dados de teste dele em <worktree>/_tmp/dados (nada é gravado na pasta dele). Na cópia, a página 13
fica sem "Só as letras" (no livro dele ela herda o "Só as letras" do livro; esse caso é a pergunta
1, que fica como está), em Preto e branco, com "Respeitar" ligada e o cinza desmarcado; o resto é
feito com cliques, como ele fez:
  1 painel Filtro: marcar "Gravuras em tons de cinza" e depois desligar "Respeitar as gravuras
    achadas" (antes: a caixinha marcada mas apagada e a gravura em preto e branco chapado, o a-27);
  2 a tela cheia dos filtros, no Preto e branco, com o "Respeitar" desligado;
  3 a janela do Automático, "Limpar a folha", Preto e branco, "Respeitar" desligada e o cinza
    marcado (o a-27), com a página 13 no "antes e depois";
  e o desenho da página 13 (o da tela e do PDF, 110 DPI) nesse estado: pagina-13-<sufixo>.jpg.
Uso: QT_QPA_FONTDIR=C:/Windows/Fonts python fazer_prints_conserto.py <pasta do código> antes|depois
(sem o QT_QPA_FONTDIR os textos saem como quadradinhos). Antes de cada rodada, copiar de novo o
projeto para _tmp/dados (o script faz isso sozinho)."""
import copy
import json
import os
import shutil
import sys
import time
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
CODIGO = Path(sys.argv[1]).resolve()
SUFIXO = sys.argv[2]
sys.path.insert(0, str(CODIGO))
RAIZ = Path(__file__).resolve().parents[2]   # a raiz da worktree
SAIDA = Path(__file__).resolve().parent
DADOS = RAIZ / "_tmp" / "dados-conserto"
os.environ["LOCALAPPDATA"] = str(DADOS)
NOME = "Na escola de Jesus - Catecismo explicado com imagens"
ORIGEM = Path(r"D:/programas/EditorImpressao-arquivos/dados-teste-rodada-de-consertos/EditorImpressao")
LIVRO = (r"D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/"
         r"Na escola de Jesus - Catecismo explicado com imagens..pdf")
INDICE = 12                                   # a página 13


def copiar_os_dados() -> None:
    """Uma cópia nova do projeto dele em _tmp/dados-conserto (só o que o programa lê)."""
    destino = DADOS / "EditorImpressao" / "projetos" / NOME
    if destino.exists():
        shutil.rmtree(destino)                # só a cópia que este script fez
    destino.mkdir(parents=True)
    for arquivo in ("projeto.json", "resumo.json", "posicao.json", "capa.png", "acoes.jsonl"):
        shutil.copy2(ORIGEM / "projetos" / NOME / arquivo, destino / arquivo)
    for arquivo in ("configuracoes.json", "historico.json"):
        shutil.copy2(ORIGEM / arquivo, DADOS / "EditorImpressao" / arquivo)
    resumo = json.loads((destino / "resumo.json").read_text(encoding="utf-8"))
    resumo["pasta"] = str(destino)
    (destino / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    dados = json.loads((destino / "projeto.json").read_text(encoding="utf-8"))
    pagina = dados["paginas"][INDICE]
    pagina.update(filtro="preto_e_branco", misto_so_as_letras=False,
                  respeitar_gravuras_achadas=True, gravuras_em_tons_de_cinza=False)
    (destino / "projeto.json").write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    copiar_os_dados()
    import cv2
    import numpy as np
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

    app = QApplication(sys.argv[:1])
    from ui import rodinha
    from ui.dialogos_de_arquivo import traduzir_o_qt

    rodinha.instalar_no_programa(app)
    traduzir_o_qt(app)
    QDialog.exec = lambda self, *a, **k: 0          # nenhuma caixa fica esperando clique
    QMessageBox.exec = lambda self, *a, **k: 0
    QTimer.singleShot(900000, lambda: (print("tempo esgotado"), app.exit(3)))

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
    tela.ir_para_pagina(INDICE)
    tela.paineis.abrir(PAINEL_FILTRO)
    projeto = janela.projeto
    pagina = projeto.paginas[INDICE]
    caixa = tela.caixa_gravuras_cinza
    assentar(1)

    def esperar_a_previa() -> None:
        fim = time.monotonic() + 240
        while time.monotonic() < fim:
            app.processEvents()
            pronta = tela.previas.ja_pronta(INDICE, tela._dpi_atual)
            if pronta is not None and tela.editor_selecao._img is pronta:
                break
            time.sleep(0.03)
        assentar(3)

    def estado(onde: str) -> str:
        return (f"{onde}: filtro={pagina.filtro} respeitar={pagina.respeitar_gravuras_achadas} "
                f"cinza={pagina.gravuras_em_tons_de_cinza} caixinha marcada={caixa.isChecked()} "
                f"clicavel={caixa.isEnabled()}")

    # 1: o painel Filtro, como ele fez: marca o cinza, depois desliga o Respeitar
    caixa.click()
    assentar(0.5)
    tela.caixa_respeitar_gravuras.click()
    assentar(0.5)
    if not caixa.isChecked() and caixa.isEnabled():
        caixa.click()
        assentar(0.5)
    esperar_a_previa()
    print(estado("painel"))
    janela.grab().save(str(SAIDA / f"conserto-1-painel-pagina-13-{SUFIXO}.jpg"), "JPG", 85)

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img, _ = renderizar_pagina(doc, copy.deepcopy(projeto), copy.deepcopy(pagina), dpi=110)
    finally:
        doc.close()
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print(f"pagina 13 desenhada: tons do meio={float(((cinza > 10) & (cinza < 245)).mean()):.1%} "
          f"(preto e branco chapado = 0%)")
    cv2.imwrite(str(SAIDA / f"pagina-13-{SUFIXO}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 90])

    # 2: a tela cheia dos filtros, Preto e branco, com o Respeitar desligado na página
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia
    dialogo = FiltrosEmTelaCheia(tela)
    dialogo.escolher("preto_e_branco")
    dialogo.show()
    dialogo.resize(1280, 657)
    fim = time.monotonic() + 240
    while dialogo._imagem("preto_e_branco") is None and time.monotonic() < fim:
        assentar(0.2)
    assentar(2)
    print("tela cheia: marcada", dialogo.caixa_gravuras_cinza.isChecked(),
          "clicavel", dialogo.caixa_gravuras_cinza.isEnabled())
    dialogo.grab().save(str(SAIDA / f"conserto-2-tela-cheia-pagina-13-{SUFIXO}.jpg"), "JPG", 85)
    dialogo.reject()
    assentar(0.5)

    # 3: o Automático, "Limpar a folha" (o a-27): Preto e branco, Respeitar desligada, cinza marcado
    from core import automatico as A
    grande = janela.abrir_o_automatico()
    if grande is not None:
        e = grande.estado
        grande.radios_de_filtro["preto_e_branco"].setChecked(True)
        e.definir_opcao("misto_so_as_letras", False)       # só na janela (sem Rodar)
        e.definir_opcao("respeitar_gravuras_achadas", False)
        e.definir_opcao("gravuras_em_tons_de_cinza", True)
        grande.mostrar_etapa(A.LIMPAR)
        assentar(2)
        grande.paginas_das_etapas[A.LIMPAR].ensureWidgetVisible(grande.cx_gravuras_cinza, 50, 200)
        alvo = grande.window() if hasattr(grande, "window") else grande
        try:
            alvo.resize(1280, 657)
        except Exception:  # noqa: BLE001
            pass
        assentar(40)                                       # o "antes e depois" da página
        print("automatico: marcada", grande.cx_gravuras_cinza.isChecked(),
              "clicavel", grande.cx_gravuras_cinza.isEnabled())
        alvo.grab().save(str(SAIDA / f"conserto-3-automatico-pagina-13-{SUFIXO}.jpg"), "JPG", 85)
        janela._fechar_a_janela_do_automatico()
    if janela.previas is not None:
        janela.previas.parar()
    janela.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
