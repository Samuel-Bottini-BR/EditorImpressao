"""Prints da etapa 9a (obra de 26/10/2026), sem aparecer na tela do Samuel.

O QUE FAZ
    Abre, fora da tela (QT_QPA_PLATFORM=offscreen), a janela "Montar para
    imprimir" e a confirmação do "imprimir agora", nos tamanhos pedidos:
    a janela do programa em 1280x657 (notebook com 150%) e a janela mínima.
    Grava PNGs em relatorios/obra-etapa9a/prints/<prefixo>-*.png.

    Dados isolados: LOCALAPPDATA aponta para tmp-agente/ (nunca a pasta de
    dados real do Samuel). O livro de teste é um PDF desenhado aqui.

USO
    .venv\\Scripts\\python.exe relatorios\\obra-etapa9a\\fazer_prints.py <prefixo>
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TRABALHO = RAIZ / "tmp-agente" / "prints"
TRABALHO.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(TRABALHO / "dados")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")
sys.path.insert(0, str(RAIZ))

import fitz  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

PRINTS = Path(__file__).resolve().parent / "prints"
PRINTS.mkdir(exist_ok=True)
MM = 72 / 25.4


def livro(caminho: Path, n: int) -> Path:
    """Um livro de n páginas A5 com o número escrito em cada uma."""
    doc = fitz.open()
    for i in range(1, n + 1):
        pagina = doc.new_page(width=146 * MM, height=235 * MM)
        pagina.insert_text((150, 300), f"página {i}", fontsize=30)
    doc.save(str(caminho))
    doc.close()
    return caminho


def guardar(widget, nome: str) -> None:
    QApplication.processEvents()
    widget.grab().save(str(PRINTS / f"{nome}.png"))
    print("gravado", PRINTS / f"{nome}.png")


def main() -> None:
    prefixo = sys.argv[1] if len(sys.argv) > 1 else "depois"
    app = QApplication.instance() or QApplication([])
    from ui import estilo

    if hasattr(estilo, "definir_tema"):
        try:
            estilo.definir_tema("escuro")
        except Exception:  # noqa: BLE001
            pass
    from ui.dialogo_impressao import DialogoImpressao

    entrada = livro(TRABALHO / "La vida eterna - preto e branco.pdf", 37)

    # 1) do tamanho que abre num notebook 1280x657 (150%)
    d = DialogoImpressao(str(entrada))
    d.show()
    tamanho = d.size()
    print("tamanho ao abrir:", tamanho.width(), tamanho.height(),
          "mínimo:", d.minimumWidth(), d.minimumHeight())
    guardar(d, f"{prefixo}-montar-ao-abrir")

    # 2) na janela mínima
    d.resize(d.minimumSize())
    guardar(d, f"{prefixo}-montar-janela-minima")

    # 3) depois de gravar (o resultado à parte)
    destino = TRABALHO / "saida.pdf"
    d.resize(tamanho)
    d.comecar(destino=str(destino))
    d.tarefa.wait(120000)
    app.processEvents()
    guardar(d, f"{prefixo}-montar-depois-de-gravar")
    d.resize(d.minimumSize())
    guardar(d, f"{prefixo}-montar-depois-de-gravar-minima")
    d.reject()

    # 4) a confirmação do "imprimir agora", se existir
    try:
        from ui.dialogo_impressao import ConfirmarImpressao
    except ImportError:
        return
    c = ConfirmarImpressao(str(entrada), impressoras=["EPSON L3250 Series", "Microsoft Print to PDF"],
                           frente_e_verso_de_fabrica=False)
    c.show()
    guardar(c, f"{prefixo}-imprimir-agora-confirmar")
    c.resize(c.minimumSize())
    guardar(c, f"{prefixo}-imprimir-agora-confirmar-minima")
    c.reject()


if __name__ == "__main__":
    main()
