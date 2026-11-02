"""Prints da D-590 ("juntar todas" na ferramenta Dividir), num livro de verdade copiado.

Copia as folhas 3 a 8 do "Schön Neues Modell Buch" (livro aberto: duas páginas por folha; só
LÊ o original) para _tmp/d590/, abre na janela (offscreen), roda o Automático com "Dividir",
vai à ferramenta Dividir e clica "juntar todas"; depois desmarca "Dividir", divide de novo
pelo Desfazer e roda outra etapa (as folhas continuam divididas). Uso, na pasta da cópia:

    ...python.exe relatorios/automatico-cadernos/d590/prints_d590.py
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"       # sem isso o offscreen desenha quadradinhos

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
ORIGINAL = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE"
                r"\Schön Neues Modell Buch - Johann Siebmacher.pdf")


def main() -> None:
    import fitz
    from PySide6.QtWidgets import QApplication

    import projetos
    from core import automatico as A

    saida = Path(__file__).resolve().parent
    pasta = RAIZ / "_tmp" / "d590"
    shutil.rmtree(pasta, ignore_errors=True)
    (pasta / "projetos").mkdir(parents=True)
    livro = pasta / "schon-6-folhas.pdf"
    with fitz.open(str(ORIGINAL)) as doc:
        novo = fitz.open()
        novo.insert_pdf(doc, from_page=2, to_page=7)
        novo.save(str(livro))
        novo.close()
    projetos.pasta_dos_projetos = lambda: pasta / "projetos"

    app = QApplication.instance() or QApplication([])
    from ui.janela_principal import JanelaPrincipal

    def assentar(vezes: int = 40) -> None:
        import time

        for _ in range(vezes):
            app.processEvents()
            time.sleep(0.05)          # a prévia é desenhada num fio de fundo

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    janela.show()
    janela.abrir_livro(str(livro))
    assentar()
    estado = janela.estado_do_automatico
    estado.marcadas = {A.DIVIDIR}
    janela.rodar_o_automatico(esperar=True, perguntar=False)
    assentar()
    tela, projeto = janela.tela_conferir, janela.projeto
    print("depois do Automático:", len(projeto.paginas), "páginas")
    tela.escolher_ferramenta("dividir")
    tela._ir_para(0)
    assentar(80)
    janela.grab().save(str(saida / "1-dividir-com-juntar-todas.png"))

    tela.botao_juntar_todas.click()
    assentar(80)
    print("depois de 'juntar todas':", len(projeto.paginas), "páginas;",
          "histórico:", janela.acoes.feitas[-1].descricao)
    janela.grab().save(str(saida / "2-depois-de-juntar-todas.png"))

    tela.desfazer()
    assentar(80)
    print("depois do Desfazer:", len(projeto.paginas), "páginas")
    janela.grab().save(str(saida / "3-desfazer-divide-de-novo.png"))

    estado.marcadas = {A.LIMPAR}
    janela.rodar_o_automatico(esperar=True, perguntar=False)
    assentar(80)
    print("Dividir desmarcada e Rodar (só Limpar):", len(projeto.paginas), "páginas;",
          "Dividir:", estado.situacoes[A.DIVIDIR])
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


if __name__ == "__main__":
    main()
