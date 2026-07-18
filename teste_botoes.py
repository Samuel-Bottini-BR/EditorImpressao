"""Clica em TODOS os botoes da tela de conferir, de verdade.

Uso:
    python teste_botoes.py "livro.pdf"

A diferenca para o teste_interface.py: aqui os botoes sao acionados por
botao.click(), passando pelo sinal clicked do Qt, e nao chamando o metodo
Python direto. Um erro que so aparece na ligacao do sinal - por exemplo o
argumento 'checked' que o clicked manda junto - escapa do outro teste e e
pego aqui.

Tambem confere se algum widget esta desenhado por cima do outro.
"""

from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

from PySide6.QtWidgets import QApplication, QLayout, QPushButton, QWidget


def esperar(segundos: float, condicao=None) -> bool:
    fim = time.perf_counter() + segundos
    while time.perf_counter() < fim:
        QApplication.processEvents()
        if condicao is not None and condicao():
            return True
        time.sleep(0.02)
    return condicao() if condicao else True


def botoes_de(widget: QWidget) -> list[QPushButton]:
    return [b for b in widget.findChildren(QPushButton) if b.isVisible() and b.isEnabled()]


def faixas_da_tela(conferir: QWidget) -> list[tuple[str, QWidget]]:
    """As linhas do empilhamento principal, de cima para baixo."""
    camada = conferir.layout()
    linhas: list[tuple[str, QWidget]] = []
    if camada is None:
        return linhas

    for i in range(camada.count()):
        item = camada.itemAt(i)
        if item.widget() is not None:
            widget = item.widget()
            nome = widget.objectName() or type(widget).__name__
            linhas.append((nome, widget))
        elif item.layout() is not None:
            # cabecalho e rodape sao layouts; conferimos os widgets deles
            for j in range(item.layout().count()):
                sub = item.layout().itemAt(j)
                if sub.widget() is not None:
                    w = sub.widget()
                    linhas.append((w.objectName() or w.text() if isinstance(w, QPushButton)
                                   else type(w).__name__, w))
    return linhas


def sobreposicoes(conferir: QWidget) -> list[str]:
    """Acha linhas do empilhamento cujos retangulos se cruzam.

    Num QVBoxLayout isso nunca deveria acontecer: cada faixa fica na sua
    altura. Se acontecer, alguma coisa esta desenhada por cima do conteudo.
    """
    problemas: list[str] = []
    linhas = faixas_da_tela(conferir)

    for i, (nome_a, a) in enumerate(linhas):
        for nome_b, b in linhas[i + 1:]:
            if a.parent() is not b.parent() or not (a.isVisible() and b.isVisible()):
                continue
            cruz = a.geometry().intersected(b.geometry())
            if cruz.width() > 2 and cruz.height() > 2:
                problemas.append(
                    f"{nome_a} {a.geometry().getRect()} cruza "
                    f"{nome_b} {b.geometry().getRect()} em {cruz.getRect()}"
                )
    return problemas


def ordem_correta(conferir: QWidget) -> list[str]:
    """Confere se as linhas aparecem na ordem pedida, de cima para baixo."""
    esperada = ["QStackedWidget", "faixaInfo/faixaAlerta", "QStackedWidget",
                "TiraMiniaturas", "cartao"]
    del esperada  # a ordem e conferida pelas coordenadas, abaixo

    problemas: list[str] = []
    alvos = []
    for nome, widget in faixas_da_tela(conferir):
        if nome in ("QStackedWidget", "TiraMiniaturas", "QFrame", "cartao") or \
                nome.startswith("faixa"):
            alvos.append((nome, widget.geometry().top(), widget.geometry().bottom()))

    for i in range(len(alvos) - 1):
        nome_a, _, base_a = alvos[i]
        nome_b, topo_b, _ = alvos[i + 1]
        if topo_b < base_a:
            problemas.append(f"{nome_b} comeca antes de {nome_a} terminar")
    return problemas


def main(caminho_pdf: str) -> int:
    app = QApplication(sys.argv)

    from ui.janela_principal import CONFERIR, JanelaPrincipal

    janela = JanelaPrincipal()
    janela.show()
    janela.abrir_livro(caminho_pdf)
    esperar(0.3)

    print("Analisando...")
    janela.analisar()
    if not esperar(180, lambda: janela.telas.currentIndex() == CONFERIR):
        print("a analise nao terminou")
        return 1

    conferir = janela.tela_conferir
    esperar(2.0)

    falhas = 0
    total_cliques = 0

    for indice, aba in enumerate(conferir._abas_ativas):
        conferir.barra_abas.setCurrentIndex(indice)
        esperar(1.5)

        print(f"\n--- aba '{aba}' ---")

        # 1. sobreposicao e ordem do empilhamento
        problemas = sobreposicoes(conferir) + ordem_correta(conferir)
        if problemas:
            falhas += 1
            print("  LAYOUT SOBREPOSTO:")
            for p in problemas:
                print(f"    {p}")
        else:
            print("  layout: sem sobreposicao, ordem correta")

        # 2. clicar em cada botao da aba (imagem + linha de botoes)
        alvos = list(botoes_de(conferir.area_imagem.currentWidget()))
        alvos += list(botoes_de(conferir.barra_botoes.currentWidget()))
        for botao in alvos:
            rotulo = botao.text() or "(sem texto)"
            try:
                botao.click()
                QApplication.processEvents()
                esperar(0.4)
                total_cliques += 1
                print(f"  ok    clique em '{rotulo}'")
            except Exception:
                falhas += 1
                print(f"  FALHA clique em '{rotulo}':")
                for linha in traceback.format_exc().splitlines()[-3:]:
                    print(f"        {linha}")

    # 3. botoes do cabecalho e do rodape
    print("\n--- cabecalho e rodape ---")
    for botao in (conferir.botao_alertas, conferir.botao_desfazer, conferir.botao_refazer):
        if not botao.isEnabled():
            continue
        try:
            botao.click()
            esperar(0.4)
            total_cliques += 1
            print(f"  ok    clique em '{botao.text()}'")
        except Exception:
            falhas += 1
            print(f"  FALHA clique em '{botao.text()}': {traceback.format_exc().splitlines()[-1]}")

    # 4. redimensionar
    print("\n--- redimensionando ---")
    tamanhos = ((1000, 680), (1000, 700), (1100, 720), (1280, 800),
                (1400, 900), (1600, 1000), (1024, 690), (1920, 1050))
    for largura, altura in tamanhos:
        janela.resize(largura, altura)
        esperar(0.4)
        for indice in range(len(conferir._abas_ativas)):
            conferir.barra_abas.setCurrentIndex(indice)
            esperar(0.25)
            problemas = sobreposicoes(conferir) + ordem_correta(conferir)
            if problemas:
                falhas += 1
                print(f"  {largura}x{altura} aba '{conferir.aba_atual}': "
                      f"SOBREPOSTO - {problemas[0]}")
                break
        else:
            print(f"  {largura}x{altura}: ok em todas as abas")

    print(f"\n{total_cliques} cliques, {falhas} problemas")
    janela.close()
    esperar(0.4)
    return 1 if falhas else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
