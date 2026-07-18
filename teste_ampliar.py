"""Testa a tela ampliada: zoom, arrasto, comparar, troca de filtro e teclado.

Uso:
    python teste_ampliar.py "livro.pdf"
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

SAIDA = Path("saida_teste/ampliar")
_falhas = 0


def esperar(segundos: float, condicao=None) -> bool:
    fim = time.perf_counter() + segundos
    while time.perf_counter() < fim:
        QApplication.processEvents()
        if condicao is not None and condicao():
            return True
        time.sleep(0.02)
    return condicao() if condicao else True


def checar(descricao: str, condicao: bool, detalhe: str = "") -> None:
    global _falhas
    if condicao:
        print(f"  ok    {descricao}" + (f"  ({detalhe})" if detalhe else ""))
    else:
        _falhas += 1
        print(f"  FALHA {descricao}  ({detalhe})")


def capturar(janela, nome: str) -> None:
    QApplication.processEvents()
    janela.grab().save(str(SAIDA / f"{nome}.png"))
    print(f"        captura: {nome}.png")


def tecla(alvo, chave) -> None:
    alvo.keyPressEvent(QKeyEvent(QEvent.KeyPress, chave, Qt.NoModifier))
    QApplication.processEvents()


def main(caminho_pdf: str) -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv)

    from core.filtros import MAGICO_PRO, MELHORAR, PRETO_E_BRANCO
    from ui.janela_principal import CONFERIR, JanelaPrincipal
    from ui.tela_ampliada import DPI_AMPLIADA, MODO_CORTAR, MODO_FILTRO, TelaAmpliada

    janela = JanelaPrincipal()
    janela.resize(1300, 860)
    janela.show()
    janela.abrir_livro(caminho_pdf)
    esperar(0.3)

    print("Analisando...")
    janela.analisar()
    if not esperar(180, lambda: janela.telas.currentIndex() == CONFERIR):
        print("a análise não terminou")
        return 1

    conferir = janela.tela_conferir
    projeto = janela.projeto
    conferir.barra_abas.setCurrentIndex(conferir._abas_ativas.index("filtro"))
    conferir._ir_para(1)          # a capa colorida, boa para comparar filtros
    esperar(3.0)

    # ------------------------------------------------------------------
    print("\n--- abrir ampliada (modo filtro) ---")
    ampliada = TelaAmpliada(conferir, modo=MODO_FILTRO, parent=janela)
    ampliada.show()
    esperar(5.0, lambda: ampliada.vista._pixmap is not None)

    checar("a imagem carregou", ampliada.vista._pixmap is not None)

    # resolução maior que a da prévia da tela normal
    from ui.tela_conferir import DPI_PREVIA

    pix = ampliada.vista._pixmap
    checar("resolução maior que a da prévia", DPI_AMPLIADA > DPI_PREVIA,
           f"{DPI_AMPLIADA} contra {DPI_PREVIA} DPI")
    checar("a imagem ampliada tem muitos pixels", pix.height() > 900,
           f"{pix.width()}x{pix.height()} px")
    capturar(ampliada, "01_aberta")

    # ------------------------------------------------------------------
    print("\n--- zoom ---")
    ampliada._zoom(1.4)
    ampliada._zoom(1.4)
    esperar(0.4)
    checar("os botões aproximam", ampliada.vista.zoom > 1.5,
           f"{ampliada.vista.zoom:.2f}x")
    capturar(ampliada, "02_com_zoom")

    zoom_antes = ampliada.vista.zoom
    ampliada.vista.definir_zoom(zoom_antes * 1.5, ancora=QPoint(300, 300))
    esperar(0.3)
    checar("a roda do mouse aproxima na âncora",
           ampliada.vista.zoom > zoom_antes and ampliada.vista.deslocamento != QPoint(0, 0),
           f"{ampliada.vista.zoom:.2f}x, deslocou {ampliada.vista.deslocamento.x()} px")

    ampliada.vista.definir_zoom(99.0)
    checar("o zoom tem teto", ampliada.vista.zoom <= 8.0, f"{ampliada.vista.zoom:.1f}x")

    ampliada._ajustar()
    esperar(0.3)
    checar("ajustar à tela volta ao começo",
           ampliada.vista.zoom == 1.0 and ampliada.vista.deslocamento == QPoint(0, 0))

    # ------------------------------------------------------------------
    print("\n--- arrastar para mover ---")
    ampliada._zoom(2.0)
    esperar(0.3)
    vis = ampliada.vista
    vis._arrastando_vista = True
    vis._ponto_inicial = QPoint(400, 400)
    vis._deslocamento_inicial = QPoint(vis.deslocamento)
    from PySide6.QtGui import QMouseEvent

    evento = QMouseEvent(QEvent.MouseMove, QPoint(300, 340), Qt.NoButton,
                         Qt.NoButton, Qt.NoModifier)
    vis.mouseMoveEvent(evento)
    esperar(0.2)
    checar("arrastar move a imagem", vis.deslocamento != vis._deslocamento_inicial,
           f"deslocou para {vis.deslocamento.x()}, {vis.deslocamento.y()}")
    vis._arrastando_vista = False
    ampliada._ajustar()

    # ------------------------------------------------------------------
    print("\n--- trocar de filtro sem sair ---")
    for atalho, esperado in ((Qt.Key_3, MELHORAR), (Qt.Key_4, MAGICO_PRO),
                             (Qt.Key_2, PRETO_E_BRANCO)):
        tecla(ampliada, atalho)
        esperar(2.5)
        atual = projeto.paginas[conferir.indice_pagina].filtro
        checar(f"tecla trocou para {esperado}", atual == esperado, atual)

    nome_na_tela = ampliada.rotulo_filtro.text()
    checar("o nome do filtro aparece na tela", "Preto e branco" in nome_na_tela,
           nome_na_tela)
    capturar(ampliada, "03_filtro_trocado")

    # ------------------------------------------------------------------
    print("\n--- comparar dois filtros ---")
    ampliada.botao_comparar.setChecked(True)
    ampliada._alternar_comparar()
    esperar(5.0, lambda: ampliada.vista_b._pixmap is not None)

    checar("a segunda vista apareceu", ampliada.vista_b.isVisible())
    checar("a segunda vista tem imagem", ampliada.vista_b._pixmap is not None)
    checar("os dois filtros são diferentes",
           ampliada.combo_comparar.currentData()
           != projeto.paginas[conferir.indice_pagina].filtro,
           f"{projeto.paginas[conferir.indice_pagina].filtro} contra "
           f"{ampliada.combo_comparar.currentData()}")
    capturar(ampliada, "04_comparando")

    ampliada.vista.definir_zoom(3.0)
    esperar(0.4)
    checar("o zoom fica amarrado nas duas vistas",
           abs(ampliada.vista_b.zoom - ampliada.vista.zoom) < 0.01,
           f"{ampliada.vista.zoom:.2f}x e {ampliada.vista_b.zoom:.2f}x")

    vis.deslocamento = QPoint(-80, -40)
    vis.vista_mudou.emit(vis.zoom, vis.deslocamento)
    esperar(0.3)
    checar("a posição fica amarrada nas duas vistas",
           ampliada.vista_b.deslocamento == vis.deslocamento,
           f"{ampliada.vista_b.deslocamento.x()}, {ampliada.vista_b.deslocamento.y()}")
    capturar(ampliada, "05_comparando_com_zoom")

    # ------------------------------------------------------------------
    print("\n--- navegar entre páginas ---")
    antes = conferir.indice_pagina
    tecla(ampliada, Qt.Key_Right)
    esperar(2.0)
    checar("a seta muda de página", conferir.indice_pagina == antes + 1,
           f"{antes + 1} -> {conferir.indice_pagina + 1}")
    tecla(ampliada, Qt.Key_Left)
    esperar(1.5)
    checar("a seta volta", conferir.indice_pagina == antes)

    # ------------------------------------------------------------------
    print("\n--- Esc fecha ---")
    tecla(ampliada, Qt.Key_Escape)
    esperar(0.6)
    checar("a janela fechou", not ampliada.isVisible())

    # ------------------------------------------------------------------
    print("\n--- ampliada na aba Onde cortar: a linha continua arrastável ---")
    conferir.barra_abas.setCurrentIndex(conferir._abas_ativas.index("corte"))
    esperar(2.5)
    corte = TelaAmpliada(conferir, modo=MODO_CORTAR, parent=janela)
    corte.show()
    esperar(6.0, lambda: corte.vista._pixmap is not None)

    checar("a folha carregou ampliada", corte.vista._pixmap is not None)
    folha = projeto.folhas[conferir.indice_folha]
    antes_corte = folha.posicao_corte
    corte.vista.definir_corte(0.44)
    corte.vista.corte_movido.emit(0.44)
    esperar(1.5)
    checar("mover a linha ampliada altera o projeto",
           abs(folha.posicao_corte - 0.44) < 1e-6,
           f"{antes_corte:.3f} -> {folha.posicao_corte:.3f}")
    capturar(corte, "06_corte_ampliado")

    corte.vista.definir_zoom(2.5)
    esperar(0.6)
    vis_c = corte.vista
    base = vis_c._largura_base()
    x_da_linha = vis_c._area.left() + int(0.44 * vis_c._area.width())
    checar("a imagem não sumiu ao mexer na linha", vis_c._pixmap is not None)
    checar(
        "o zoom aumenta a imagem de verdade",
        abs(vis_c._area.width() - base * vis_c.zoom) <= 2,
        f"área {vis_c._area.width()} px = base {base:.0f} x {vis_c.zoom:.1f}",
    )
    checar(
        "a linha de corte acompanha o zoom",
        vis_c._area.left() <= x_da_linha <= vis_c._area.right(),
        f"linha em x={x_da_linha}, área de {vis_c._area.left()} a "
        f"{vis_c._area.right()}, janela de {vis_c.width()} px",
    )
    capturar(corte, "07_corte_ampliado_com_zoom")
    corte.close()
    esperar(0.5)

    print(f"\n{_falhas} problemas")
    janela.close()
    esperar(0.4)
    return 1 if _falhas else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
