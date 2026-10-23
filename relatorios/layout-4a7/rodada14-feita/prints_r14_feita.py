"""Prints da janela de verdade com o que a rodada 14 decidiu, já construído (903 B, 904 A, 907 B,
909 B, 910 A). Uso: python prints_r14_feita.py <pasta>   (arquivo descartável do agente de layout)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prints_r14 as r  # noqa: E402
from prints_etapa3 import RESULTADOS, conferir  # noqa: E402
from prints_layout import abrir_o_livro, esperar, nova_janela  # noqa: E402

from PySide6.QtCore import QPoint  # noqa: E402
from PySide6.QtWidgets import QApplication, QToolTip  # noqa: E402


def grab_cena(janela):
    cena = r.Cena(janela)
    pix = janela.grab()
    r.ESC = pix.devicePixelRatio()
    cena.img = pix.toImage()
    cena.img.setDevicePixelRatio(1)
    return cena


def menu(janela, titulo, nome):
    m = r.menu_do_titulo(janela, titulo)
    onde = r.abrir_menu(janela, m)
    cena = grab_cena(janela)
    cena.colar(m, onde)
    cena.inteira(nome, [QRect_of(onde, m)])
    print("     ", titulo, [a.text() for a in m.actions() if not a.isSeparator()])
    m.close()
    esperar(0.3)


def QRect_of(onde, m):  # noqa: N802
    from PySide6.QtCore import QRect
    return QRect(onde, m.size())


def principal(destino: Path) -> None:
    r.SAIDA = destino
    janela = nova_janela()
    tela = abrir_o_livro(janela, dividir=True)
    tela.ir_para_pagina(4)
    esperar(6)
    tela.trilha.escolher("cortar")
    tela.paineis.fechar()
    esperar(2)
    menu(janela, "Painéis", "1-menu-paineis")
    menu(janela, "Ver", "2-menu-ver")
    janela.menu.acoes["painel_filtro"].trigger()
    esperar(4)
    conferir(tela.paineis.aberto == "filtro" and janela.menu.acoes["painel_filtro"].isChecked(),
             "menu Painéis > Filtro da página abriu o painel e ficou marcado")
    painel = tela.paineis.filtro_da_pagina
    for chave in ("ajuste", "letras", "limpar", "mais"):
        painel.partes[chave].abrir(False)
    painel.partes["pedaco"].abrir(True)
    esperar(1)
    conferir("o mesmo da página" not in [b.text() for b in painel.botoes_do_pedaco.values()]
             and painel.filtro_pedaco == "", "909 B: sem o botão de cima, nenhum aceso")
    grab_cena(janela).inteira("3-so-neste-pedaco", [r.no_janela(painel.partes["pedaco"], janela)])
    tela.trilha.escolher("dividir")
    esperar(4)
    combo = tela.combo_jeito_da_folha
    conferir([combo.itemText(k) for k in range(combo.count())] == ["o do Editor", "o do ScanTailor"],
             "907 B: a lista do Dividir diz 'o do Editor'")
    grab_cena(janela).inteira("4-dividir-o-do-editor", [r.no_janela(combo, janela)])
    tela.trilha.escolher("endireitar")
    esperar(4)
    tela.botao_angulo_horario.click()
    esperar(4)
    linha = tela.rotulo_angulos_medidos
    rolagem = tela.paineis.propriedades.rolagem.verticalScrollBar()
    rolagem.setValue(rolagem.maximum())
    esperar(0.5)
    conferir(linha.text() not in ("", "(medindo...)") and "girou à mão" in linha.toolTip(),
             f"910 A: com o giro à mão a linha continua ({linha.text()!r}) e a frase está no balão")
    QToolTip.showText(linha.mapToGlobal(QPoint(10, linha.height())), linha.toolTip(), linha)
    esperar(0.6)
    balao = next((w for w in QApplication.topLevelWidgets()
                  if w.metaObject().className() == "QTipLabel" and w.isVisible()), None)
    cena = grab_cena(janela)
    if balao is not None:
        cena.colar(balao, linha.mapTo(janela, QPoint(-60, linha.height() + 4)))
    cena.inteira("5-endireitar-a-mao-balao", [r.no_janela(linha, janela)])
    QToolTip.hideText()
    tela.botao_angulo_anti_horario.click()
    esperar(2)
    janela.close()
    falhas = [f for ok, f in RESULTADOS if not ok]
    print(f"\nconferências: {len(RESULTADOS) - len(falhas)} de {len(RESULTADOS)} certas")
    for f in falhas:
        print("  FALHOU:", f)


if __name__ == "__main__":
    destino = Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    principal(destino)
    print("FIM", flush=True)
