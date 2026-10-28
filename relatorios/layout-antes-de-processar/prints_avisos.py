"""Prints da janela DE VERDADE: "Antes de processar" (a lista dos avisos), 22/10/2026.
Abre uma CÓPIA do Palatino no programa de verdade (fontes do Windows, fora da tela), roda a
análise, passa pelas primeiras páginas (os avisos medidos por trás chegam) e aperta
"Confirmar e processar" com clique do Windows. Quando a janela "Antes de processar" abre,
fotografa a janela do programa com ela por cima (onde o Qt a põe: no meio do programa), em
1280 x 657 (print de 1600 x 821 a 125%) e em 1536 x 816 ("maximizada"), e sai pelo "ver"
(clique do Windows; não processa). Também mede o tamanho da janela dos avisos.
Uso: python prints_avisos.py <pasta>   (arquivo descartável do agente de layout, em saida_teste/)."""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prints_etapa3 import RESULTADOS, clique_nativo, conferir  # noqa: E402
from prints_layout import ACERVO, TRAB, esperar, nova_janela  # noqa: E402

from PySide6.QtCore import QPoint, QTimer  # noqa: E402
from PySide6.QtGui import QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

PALATINO = TRAB / "Palatino (copia).pdf"
shutil.copy2(ACERVO / "Giovambattista Palatino cittadino romano.pdf", PALATINO)
DESTINO = Path(".")
MEDIDAS = []


def foto_com_a_janela(janela, caixa, nome):
    """O print do programa com a janela dos avisos colada no meio, como ela abre."""
    fundo = janela.grab()
    foto = caixa.grab()
    x = max(0, (janela.width() - caixa.width()) // 2)
    y = max(0, (janela.height() - caixa.height()) // 2)
    pintor = QPainter(fundo)
    pintor.drawPixmap(QPoint(x, y), foto)
    pintor.end()
    fundo.save(str(DESTINO / f"{nome}.png"))
    foto.save(str(DESTINO / f"{nome}-so-a-janela.png"))
    linha = (f"{nome}: janela dos avisos com {caixa.width()} x {caixa.height()} pontos "
             f"(programa {janela.width()} x {janela.height()}), {caixa.lista.count()} linhas")
    MEDIDAS.append(linha)
    print("   ", linha, flush=True)


def principal() -> None:
    from ui.janela_dos_avisos import JanelaDosAvisos

    janela = nova_janela()
    janela.abrir_livro(str(PALATINO))
    esperar(3)
    janela.analisar()
    tela = janela.tela_conferir
    for _ in range(300):
        if tela.projeto is not None:
            break
        esperar(1)
    print("  análise pronta:", tela.projeto is not None, flush=True)
    esperar(5)
    for i in range(min(40, len(tela.projeto.paginas))):     # os avisos medidos por trás
        tela.ir_para_pagina(i)
        esperar(1.2)
    esperar(5)
    while QApplication.activeModalWidget() is not None:    # um aviso que abriu no caminho
        caixa = QApplication.activeModalWidget()
        print("  fechando um aviso aberto:", getattr(caixa, "text", lambda: "")(), flush=True)
        caixa.reject() if hasattr(caixa, "reject") else caixa.close()
        esperar(1)
    from core import avisos as avisos_do_livro
    print("  avisos pendentes:", len(avisos_do_livro.pendentes_do_livro(tela.projeto)),
          "| botão:", repr(tela.botao_processar.text()), tela.botao_processar.isVisible(),
          tela.botao_processar.isEnabled(), flush=True)
    for tamanho, sufixo in (((1280, 657), "1600x821"), ((1536, 816), "maximizada")):
        janela.resize(*tamanho)
        janela.move(-32000, -32000)
        esperar(2)
        vista = {}

        def quando_abrir():
            caixa = next((w for w in QApplication.topLevelWidgets()
                          if isinstance(w, JanelaDosAvisos) and w.isVisible()), None)
            if caixa is None:
                QTimer.singleShot(300, quando_abrir)
                return
            caixa.move(-31000, -31000)
            esperar(1.5)
            foto_com_a_janela(janela, caixa, f"{sufixo}-antes-de-processar")
            vista["ok"] = True
            clique_nativo(caixa, caixa.botao_ver)          # "ver": vai à página, não processa
            QTimer.singleShot(1500, lambda: caixa.isVisible() and caixa.reject())

        QTimer.singleShot(500, quando_abrir)
        ponto = tela.botao_processar.mapTo(janela, tela.botao_processar.rect().center())
        print("  no ponto do botão está:", janela.childAt(ponto), "| modal aberta:",
              QApplication.activeModalWidget(), "| pop-up:", QApplication.activePopupWidget(), flush=True)
        tela.botao_processar.pressed.connect(lambda: print("  (o botão recebeu o aperto)", flush=True))
        tela.botao_processar.clicked.connect(lambda: print("  (o botão recebeu o clique)", flush=True))
        clique_nativo(janela, tela.botao_processar)
        esperar(3)
        conferir(vista.get("ok", False), f"{sufixo}: clique do Windows em processar abriu 'Antes de processar'")
        conferir(not any(isinstance(w, JanelaDosAvisos) and w.isVisible() for w in QApplication.topLevelWidgets()),
                 f"{sufixo}: o 'ver' (clique do Windows) fechou a janela sem processar")
    janela.close()
    esperar(1)
    falhas = [f for ok, f in RESULTADOS if not ok]
    print(f"\nconferências: {len(RESULTADOS) - len(falhas)} de {len(RESULTADOS)} certas")
    (DESTINO / "medidas.txt").write_text("\n".join(MEDIDAS) + "\n" + "\n".join(
        ("ok   " if ok else "FALHOU ") + f for ok, f in RESULTADOS), encoding="utf-8")


if __name__ == "__main__":
    DESTINO = Path(sys.argv[1])
    DESTINO.mkdir(parents=True, exist_ok=True)
    principal()
    print("FIM", flush=True)
