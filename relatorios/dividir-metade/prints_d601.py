"""Prints da D-601 (no Dividir, "Uma página" mostra só a metade), no Gradus Primus.

O que faz: copia as 6 primeiras folhas do Gradus Primus (só LÊ o original) para
_tmp/d601-<quando>/, com a pasta de dados do programa separada (LOCALAPPDATA e a pasta dos
projetos dentro de _tmp), abre na janela do programa (offscreen, 1280 x 657), escolhe a
ferramenta Dividir na folha 1, clica "dividir esta" e tira os prints:

  1. logo depois de dividir, com "Uma página" (de fábrica);
  2. depois da seta para a direita;
  3. com "Duas lado a lado".

Uso (na pasta da cópia):

    ...python.exe relatorios/dividir-metade/prints_d601.py antes|depois

"antes" é rodado com ui/tela_conferir.py de 110976f posto no lugar só para o print; "depois"
com o código do ramo.
"""

from __future__ import annotations

import os
import shutil
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
QUANDO = sys.argv[1] if len(sys.argv) > 1 else "depois"
# "... depois esta-certo": só os prints 5 e 6 (a faixa antes e depois do "está certo", D-572)
ESTA_CERTO = len(sys.argv) > 2 and sys.argv[2] == "esta-certo"
PASTA = RAIZ / "_tmp" / f"d601-{QUANDO}{'-ok' if ESTA_CERTO else ''}"
shutil.rmtree(PASTA, ignore_errors=True)
(PASTA / "dados").mkdir(parents=True)
(PASTA / "projetos").mkdir(parents=True)

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"       # sem isso o offscreen desenha quadradinhos
os.environ["LOCALAPPDATA"] = str(PASTA / "dados")        # a pasta de dados do Samuel fica intacta
sys.path.insert(0, str(RAIZ))

ORIGINAL = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")


def main() -> None:
    import fitz
    from PySide6.QtWidgets import QApplication

    import projetos

    saida = Path(__file__).resolve().parent
    livro = PASTA / "gradus-primus-6-folhas.pdf"
    with fitz.open(str(ORIGINAL)) as doc:
        novo = fitz.open()
        novo.insert_pdf(doc, from_page=0, to_page=5)
        novo.save(str(livro))
        novo.close()
    projetos.pasta_dos_projetos = lambda: PASTA / "projetos"

    app = QApplication.instance() or QApplication([])
    from ui.janela_principal import JanelaPrincipal
    from ui.tela_conferir import ABA_CORTE
    from ui.widgets.paginas_rolando import DUAS, UMA

    def assentar(vezes: int = 30) -> None:
        for _ in range(vezes):
            app.processEvents()

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    janela.show()
    janela.abrir_livro(str(livro))
    assentar()
    tela = janela.tela_conferir

    def esperar_a_imagem() -> None:
        fim = time.monotonic() + 60
        while time.monotonic() < fim:
            assentar(5)
            v = tela.visualizadores[ABA_CORTE]
            if getattr(v, "_pixmap", None) is not None and not v.carregando:
                break
            time.sleep(0.05)
        tela.atualizar()
        assentar(40)

    def foto(nome: str) -> None:
        esperar_a_imagem()
        janela.grab().save(str(saida / f"{QUANDO}-{nome}.png"))
        pagina = janela.projeto.paginas[tela.indice_pagina]
        print(f"{QUANDO}-{nome}: folha {tela.indice_folha + 1}, página {tela.indice_pagina + 1} "
              f"({pagina.metade}), rótulo '{tela.rotulo_da_pagina.text()}', "
              f"linha à vista={tela.visualizadores[ABA_CORTE].corte_visivel}, "
              f"miniaturas na tira={len(tela.tira._miniaturas)}")

    tela.escolher_ferramenta("dividir")
    tela._ir_para(0)
    assentar()
    esperar_a_imagem()
    tela.botao_nao_dividir.click()            # "dividir esta"
    if ESTA_CERTO:                            # D-572 + D-601: antes e depois do ok
        foto("5-uma-pagina-antes-do-esta-certo")
        tela.botao_esta_certo.click()
        foto("6-uma-pagina-depois-do-esta-certo")
        print(f"faixa: '{tela.texto_faixa.text()}', está certo à vista: "
              f"{tela.botao_esta_certo.isVisible()}")
        janela.close()
        return
    foto("1-dividida-uma-pagina")
    tela.botao_proxima.click()                # a seta da barra de baixo
    foto("2-seta-para-a-direita")
    tela._ir_para(0)                          # de volta à folha 1
    if tela.botoes_mostrar[DUAS].isEnabled():
        tela.botoes_mostrar[DUAS].click()
    else:                                     # antes: o botão ficava apagado no Dividir
        tela.definir_mostrar(DUAS)
    foto("3-duas-lado-a-lado")
    # acréscimo de 02/11: a tira do Dividir; volta ao "Uma página" e clica na
    # miniatura da direita da folha 1 (a capa); antes, o quadro 2 era a folha 2
    tela.definir_mostrar(UMA)
    tela.tira.selecionada.emit(1)
    foto("4-clique-na-miniatura-2")
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


if __name__ == "__main__":
    main()
