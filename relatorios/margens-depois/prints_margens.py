"""Prints do defeito de 02/11/2026 ("coloquei margem e ela não apareceu no preview.") no Gradus
Primus: o Automático com "Margens iguais" marcada (10 / 5 / 10 / 5 mm), no livro já dividido.

Roda sem tela, numa pasta de dados só dele (LOCALAPPDATA trocado, pasta_de_dados_dos_scripts),
com a cópia do livro em _tmp\\gradus.pdf (copiada da Área de Trabalho; o original não é tocado).
Uso, na raiz da cópia (a de antes ou a de depois do conserto):
    $env:QT_QPA_PLATFORM="offscreen"
    .venv\\Scripts\\python.exe relatorios\\margens-depois\\prints_margens.py <prefixo> [pasta dos PNG]
<prefixo> vai no começo do nome de cada PNG ("antes" ou "depois"). Grava também o tempo de cada
conta no terminal.

Caminho de cada foto: o Gradus aberto sem mexer, o Automático rodado com "Dividir folhas ao meio"
(o livro fica dividido, como o do Samuel), a página 21 (uma metade), e na janela do Automático só
"Margens iguais" marcada; o "depois" é a metade como vai sair (sem filtro: Original).
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"     # sem isto o modo sem tela desenha caixinhas
PREFIXO = sys.argv[1] if len(sys.argv) > 1 else "depois"
SAIDA = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent
LIVRO = Path(sys.argv[3]) if len(sys.argv) > 3 else RAIZ / "_tmp" / "gradus.pdf"
PAGINA = 20                                            # a página 21 do livro dividido


def main() -> None:
    from pasta_de_dados_dos_scripts import isolar_pasta_de_dados

    isolar_pasta_de_dados("prints-margens", RAIZ / "_tmp" / "dados")
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    from core import automatico as A
    from ui.janela_principal import JanelaPrincipal

    def assentar(n=8):
        for _ in range(n):
            app.processEvents()

    def esperar(*paineis, limite=900):
        fim = time.monotonic() + limite
        while time.monotonic() < fim:
            assentar(2)
            if not any(p is not None and p.calculando() for p in paineis):
                assentar()
                if not any(p is not None and p.calculando() for p in paineis):
                    return
            time.sleep(0.03)
        raise SystemExit("a conta não terminou")

    def foto(widget, nome):
        caminho = SAIDA / f"{PREFIXO}-{nome}.png"
        widget.grab().save(str(caminho))
        print("foto:", caminho)

    def forma(painel):
        d = painel._depois[1] if painel._depois and painel._depois[0] == painel._indice else None
        return None if d is None else d.shape[:2]

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    janela.show()
    janela.abrir_livro(str(LIVRO))
    fim = time.monotonic() + 120
    while not (janela.projeto is not None and janela.trabalho_carregado) and time.monotonic() < fim:
        assentar(2)
    # o livro dividido, como o do Samuel
    assert janela.rodar_o_automatico(pedido=A.Pedido(etapas=[A.DIVIDIR]), esperar=True, perguntar=False)
    assentar()
    print("páginas:", len(janela.projeto.paginas))
    janela.tela_conferir.ir_para_pagina(PAGINA)
    grande = janela.abrir_o_automatico("margens")
    grande.resize(1280, 657)
    painel = grande.antes_e_depois
    for etapa in A.ETAPAS:                               # nada marcado
        item = grande.lista.item_da_etapa(etapa)
        if item.checkState() != Qt.Unchecked:
            item.setCheckState(Qt.Unchecked)
    esperar(painel)
    print("sem margens, depois:", forma(painel))
    t0 = time.monotonic()
    grande.lista.item_da_etapa(A.MARGENS).setCheckState(Qt.Checked)
    assentar()
    time.sleep(1.0)
    assentar()
    if painel.calculando():
        foto(grande, "1-medindo-o-livro-bolinha")
    esperar(painel)
    print(f"margens marcadas: {time.monotonic() - t0:.1f} s, depois: {forma(painel)}")
    foto(grande, "2-margens-10-5-10-5")
    t0 = time.monotonic()
    grande.margens_mm["esquerda"].setValue(25.0)
    grande.margens_mm["direita"].setValue(25.0)
    esperar(painel)
    print(f"margens 25 dos lados: {time.monotonic() - t0:.1f} s, depois: {forma(painel)}")
    foto(grande, "3-margens-25-dos-lados")
    grande.margens_mm["esquerda"].setValue(10.0)
    grande.margens_mm["direita"].setValue(10.0)
    esperar(painel)

    painel.abrir_em_tela_cheia()
    tela = painel.tela_cheia
    tela.setWindowState(Qt.WindowNoState)             # o modo sem tela tem uma tela pequena
    tela.resize(1280, 657)
    assentar()
    foto(tela, "4-tela-cheia")
    tela.botao_comparar.click()
    esperar(painel)
    tela.lado_b.botao_opcoes.click()
    tela.lado_b.painel.mostrar_etapa(A.MARGENS)
    tela.lado_b.painel.margens_mm["esquerda"].setValue(30.0)
    assentar()
    esperar(painel, tela.lado_b.motor)
    assentar()
    foto(tela, "5-comparar-direita-30-mm-a-esquerda")
    tela.accept()
    assentar()
    janela._fechar_a_janela_do_automatico()
    assentar()
    janela.close()


if __name__ == "__main__":
    main()
