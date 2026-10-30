"""Prints da D-589 ("Montar cadernos" volta sozinho), no caminho do Kaique, num livro de verdade.

O que faz: copia as 12 primeiras páginas do "Sobre a Consolação da Filosofia" (só LÊ o original)
para _tmp/d589/, abre na janela do programa (offscreen), roda o Automático com "Limpar a folha"
(Preto e branco) e "Montar cadernos" no livro todo, abre a janela grande, DESMARCA "Montar
cadernos" e roda; tira os prints e grava o PDF. Uso (na pasta da cópia):

    $env:QT_QPA_PLATFORM="offscreen"; ...python.exe relatorios/automatico-cadernos/prints_d589.py antes|depois

"antes" é rodado com o código de antes do conserto (core/automatico.py e ui/automatico.py de
d93c506 postos no lugar só para o print); "depois" com o código do ramo.
"""

from __future__ import annotations

import copy
import os
import shutil
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"       # sem isso o offscreen desenha quadradinhos

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

ORIGINAL = Path(r"D:\programas\EditorImpressao-arquivos\LIVROS PARA FAZER TESTE (duplicata)"
                r"\Sobre a Consolação da Filosofia - Severino Boécio.pdf")


def main(quando: str) -> None:
    import fitz
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    import projetos
    from core import automatico as A
    from core.filtros import PRETO_E_BRANCO
    from core.pipeline import processar

    saida = Path(__file__).resolve().parent
    pasta = RAIZ / "_tmp" / f"d589-{quando}"
    shutil.rmtree(pasta, ignore_errors=True)
    (pasta / "projetos").mkdir(parents=True)
    livro = pasta / "consolacao-12-paginas.pdf"
    with fitz.open(str(ORIGINAL)) as doc:
        novo = fitz.open()
        novo.insert_pdf(doc, from_page=0, to_page=11)
        novo.save(str(livro))
        novo.close()
    projetos.pasta_dos_projetos = lambda: pasta / "projetos"

    app = QApplication.instance() or QApplication([])
    from ui.janela_principal import JanelaPrincipal

    def assentar(vezes: int = 30) -> None:
        for _ in range(vezes):
            app.processEvents()

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    janela.show()
    janela.abrir_livro(str(livro))
    assentar()
    estado = janela.estado_do_automatico

    # uma rodada anterior: Limpar (Preto e branco) e Montar cadernos no livro todo
    estado.marcadas = {A.LIMPAR, A.CADERNOS}
    estado.opcoes["filtro_padrao"] = PRETO_E_BRANCO
    janela.rodar_o_automatico(esperar=True, perguntar=False)
    assentar()

    # o Kaique abre a janela grande e desmarca "Montar cadernos"
    jan = janela.abrir_o_automatico(A.LIMPAR)
    assentar()
    jan.lista.item_da_etapa(A.CADERNOS).setCheckState(Qt.Unchecked)
    jan.lista.scrollToBottom()
    assentar(60)
    jan.grab().save(str(saida / f"{quando}-1-janela-montar-cadernos-desmarcada.png"))
    jan.botao_rodar.click()
    if janela.tarefa is not None:
        janela.tarefa.wait(120000)
    assentar(60)

    # o painel depois de rodar
    janela.tela_conferir.paineis.mostrar_painel("automatico", True)
    painel = janela.tela_conferir.paineis.automatico
    painel.lista.scrollToBottom()
    assentar(30)
    janela.grab().save(str(saida / f"{quando}-2-painel-depois-de-rodar.png"))

    # a janela grande aberta de novo
    jan = janela.abrir_o_automatico(A.LIMPAR)
    jan.lista.scrollToBottom()
    assentar(60)
    jan.grab().save(str(saida / f"{quando}-3-janela-aberta-de-novo.png"))
    janela._fechar_a_janela_do_automatico()

    # o PDF, como o "Confirmar e processar" grava
    projeto = copy.copy(janela.projeto)
    projeto.caminho_saida = str(pasta / f"{quando}.pdf")
    pdf = processar(projeto)
    with fitz.open(pdf) as doc:
        folhas = [(round(p.rect.width), round(p.rect.height)) for p in doc]
        doc[0].get_pixmap(dpi=60).save(str(saida / f"{quando}-4-pdf-primeira-folha.png"))
    marcada = A.CADERNOS in estado.marcadas
    print(f"{quando}: montar_cadernos={janela.projeto.montar_cadernos} "
          f"caixinha_marcada_depois={marcada} situacao='{estado.situacoes[A.CADERNOS]}' "
          f"folhas_do_pdf={len(folhas)} primeira={folhas[0]}")
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "depois")
