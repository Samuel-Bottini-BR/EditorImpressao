"""Print 4 (n0411-o-que-vai-sair): o quadro "O que vai sair" do "Montar para imprimir".

Palatino (cópia), aberto do zero e processado como o "Confirmar e processar" grava (ajustes de
fábrica). Depois a janela "Montar para imprimir" (a que a tela "Ficou pronto!" abre) com o PDF
pronto, no tamanho de fábrica (_tamanho_ao_abrir), opções de fábrica.
(a) como abre; (b) o lado direito rolado até o quadro aparecer inteiro.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comum  # noqa: E402

RAIZ = str(AQUI.parent)
CRU = AQUI / "cru" / "p4"
CRU.mkdir(parents=True, exist_ok=True)
NOTAS: dict = {}


def nota(chave, valor):
    NOTAS[chave] = valor
    print(chave, "=>", json.dumps(valor, ensure_ascii=False, default=str), flush=True)
    (CRU / "notas.json").write_text(json.dumps(NOTAS, ensure_ascii=False, indent=1, default=str),
                                    encoding="utf-8")


def caixa(widget, dialogo) -> list[int]:
    from PySide6.QtCore import QPoint

    p = widget.mapTo(dialogo, QPoint(0, 0))
    return [p.x(), p.y(), widget.width(), widget.height()]


def main():
    import faulthandler
    faulthandler.dump_traceback_later(1500, exit=True)
    comum.preparar(RAIZ, "p4")
    from core.pipeline import processar
    from ui.dialogo_impressao import DialogoImpressao

    j = comum.nova_janela()
    j.abrir_livro(str(AQUI / "livros" / "palatino.pdf"))
    nota("abrir (s)", comum.esperar_tela(j))
    p = copy.copy(j.projeto)
    p.caminho_saida = str(CRU / "palatino-pronto.pdf")
    saida = processar(p)
    nota("pdf pronto", str(saida))

    dialogo = DialogoImpressao(str(saida), j)
    dialogo.show()
    dialogo.move(0, 0)

    def quieta():
        return (not dialogo._relogio_da_previa.isActive()
                and not (dialogo.tarefa_previa is not None and dialogo.tarefa_previa.isRunning())
                and not dialogo._previa_pendente and not dialogo.bolinha_da_previa.carregando
                and dialogo.folha_na_tela is not None)

    comum.esperar(1.0)
    nota("previa (s)", comum.ate(quieta, 300, 0.3))
    comum.esperar(1.5)
    nota("tamanho ao abrir", [dialogo.width(), dialogo.height()])
    nota("paginas do livro", dialogo.paginas_do_livro)
    nota("texto do quadro", dialogo.resumo.text())
    rol = dialogo.rolagem_do_resultado
    nota("rolagem (valor, max)", [rol.verticalScrollBar().value(), rol.verticalScrollBar().maximum()])
    from PySide6.QtWidgets import QLabel
    titulo = next(w for w in dialogo.findChildren(QLabel) if w.text().strip().upper() == "O QUE VAI SAIR"
)
    nota("a: titulo (x,y,l,a)", caixa(titulo, dialogo))
    nota("a: quadro (x,y,l,a)", caixa(dialogo.resumo, dialogo))
    nota("a: lado direito (x,y,l,a)", caixa(rol.viewport(), dialogo))
    comum.foto(dialogo, CRU / "a-como-abre.png")
    rol.ensureWidgetVisible(dialogo.resumo, 0, 30)
    comum.esperar(1.0)
    nota("rolagem depois (valor, max)", [rol.verticalScrollBar().value(), rol.verticalScrollBar().maximum()])
    nota("b: titulo (x,y,l,a)", caixa(titulo, dialogo))
    nota("b: quadro (x,y,l,a)", caixa(dialogo.resumo, dialogo))
    comum.foto(dialogo, CRU / "b-rolado.png")
    dialogo.reject()
    comum.fechar(j)


if __name__ == "__main__":
    main()
