"""Prints e conferência da janela DE VERDADE para a etapa 6 (tela cheia dos filtros, 601 A).

A tela cheia é aberta pelo clique nativo no ícone do título do painel Filtro; para o roteiro não
parar no exec() (janela modal), o exec é trocado aqui por show() fora da tela. Os cliques dentro dela
são mensagens nativas do Windows para a janela dela. Uso: python prints_etapa6.py <pasta>."""
import ctypes
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prints_r14 as r  # noqa: E402
from prints_etapa3 import RESULTADOS, _lparam, clicar_no_icone, clique_nativo, conferir  # noqa: E402
from prints_layout import abrir_o_livro, esperar, nova_janela  # noqa: E402

from PySide6.QtCore import QPoint, Qt  # noqa: E402

user32 = ctypes.windll.user32
ABERTAS = []


def foto(janela, nome, contornos=()):
    cena = r.Cena(janela)
    pix = janela.grab()
    r.ESC = pix.devicePixelRatio()
    cena.img = pix.toImage()
    cena.img.setDevicePixelRatio(1)
    cena.inteira(nome, list(contornos))
    return cena


def principal(destino: Path) -> None:
    from core.filtros import MAGICO_PRO, ORIGINAL, PRETO_E_BRANCO
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

    def exec_sem_travar(self):
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.move(-32000, -32000)
        self.show()
        self.move(-32000, -32000)
        ABERTAS.append(self)
        return 0

    FiltrosEmTelaCheia.exec = exec_sem_travar
    r.SAIDA = destino
    janela = nova_janela()
    tela = abrir_o_livro(janela, dividir=True)
    tela.ir_para_pagina(4)
    esperar(6)
    tela.trilha.escolher("cortar")
    tela.paineis.fechar()
    esperar(2)
    clicar_no_icone(janela, tela, "filtro")
    esperar(6)
    painel = tela.paineis.filtro_da_pagina
    foto(janela, "1-icone-no-titulo-do-painel", [r.no_janela(painel.botao_tela_cheia, janela)])
    clique_nativo(janela, painel.botao_tela_cheia)
    esperar(10)
    conferir(len(ABERTAS) == 1, "clique nativo no ícone do título abriu a tela cheia dos filtros")
    d = ABERTAS[0]
    d.resize(1280, 657)
    d.move(-32000, -32000)
    esperar(8)
    pagina = janela.projeto.paginas[tela.indice_pagina]
    filtro_antes = pagina.filtro
    foto(d, "2-tela-cheia-ao-abrir")
    clique_nativo(d, d.cartoes[PRETO_E_BRANCO])
    esperar(8)
    conferir(d.escolhido == PRETO_E_BRANCO and pagina.filtro == filtro_antes,
             "clique nativo no Preto e branco da fila: mostra, sem mudar a página")
    foto(d, "3-preto-e-branco-escolhido")
    clique_nativo(d, d.chave_comparar, QPoint(8, d.chave_comparar.height() // 2))
    esperar(8)
    conferir(d.chave_comparar.isChecked() and d.vista.comparando,
             "clique nativo na chave 'Comparar com o Original': antes e depois")
    foto(d, "4-comparando", [r.no_janela(d.vista, d)])
    # arrasto nativo da linha
    vista = d.vista
    area = vista._area(vista.depois) if vista.depois is not None else None
    if area is not None:
        inicio = QPoint(int(area.left() + area.width() * 0.5), int(area.center().y()))
        fim = QPoint(int(area.left() + area.width() * 0.25), int(area.center().y()))
        hwnd = int(d.winId())
        a, b = vista.mapTo(d, inicio), vista.mapTo(d, fim)
        user32.PostMessageW(hwnd, 0x0200, 0, _lparam(d, a))
        esperar(0.2)
        user32.PostMessageW(hwnd, 0x0201, 1, _lparam(d, a))
        esperar(0.2)
        for passo in range(1, 9):
            m = QPoint(round(a.x() + (b.x() - a.x()) * passo / 8), a.y())
            user32.PostMessageW(hwnd, 0x0200, 1, _lparam(d, m))
            esperar(0.06)
        user32.PostMessageW(hwnd, 0x0202, 0, _lparam(d, b))
        esperar(1)
        conferir(vista.posicao < 0.4, f"arrasto nativo da linha do antes e depois (posição {vista.posicao:.2f})")
        foto(d, "5-linha-arrastada")
    clique_nativo(d, d.cartoes[ORIGINAL])
    esperar(3)
    conferir("outro filtro" in d.vista.aviso, "com o Original e a chave ligada, o aviso pede outro filtro")
    foto(d, "6-original-comparando-aviso")
    clique_nativo(d, d.chave_comparar, QPoint(8, d.chave_comparar.height() // 2))
    d.cartoes[MAGICO_PRO].parentWidget().parentWidget().parentWidget().ensureWidgetVisible(d.cartoes[MAGICO_PRO])
    esperar(0.5)
    clique_nativo(d, d.cartoes[MAGICO_PRO])
    esperar(8)
    print("     escolhido depois do clique no Mágico pro:", d.escolhido)
    d._ajuste_mudou(80)
    esperar(10)
    foto(d, "7-magico-pro-ajuste-mexido")
    clique_nativo(d, d.botao_usar)
    esperar(6)
    conferir(pagina.filtro == MAGICO_PRO and pagina.intensidade_magico == 80,
             "clique nativo em 'Usar Mágico pro': filtro e ajuste gravados na página")
    tela.desfazer()
    tela.desfazer()
    esperar(3)
    conferir(pagina.filtro == filtro_antes, "dois Ctrl+Z voltam a página ao filtro de antes")
    # menu Ver
    janela.menu.acoes["filtros_tela_cheia"].trigger()
    esperar(4)
    conferir(len(ABERTAS) == 2, "menu Ver > Filtros em tela cheia abre a tela cheia")
    ABERTAS[1].resize(1000, 600)
    ABERTAS[1].move(-32000, -32000)
    esperar(6)
    foto(ABERTAS[1], "8-janela-minima")
    janela._trocar_tema("claro")
    esperar(2)
    ABERTAS[1].resize(1280, 657)
    esperar(3)
    foto(ABERTAS[1], "9-claro")
    janela._trocar_tema("cinza")
    ABERTAS[1].reject()
    janela.close()
    esperar(1)
    falhas = [f for ok, f in RESULTADOS if not ok]
    print(f"\nconferências: {len(RESULTADOS) - len(falhas)} de {len(RESULTADOS)} certas")
    for f in falhas:
        print("  FALHOU:", f)


if __name__ == "__main__":
    destino = Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    principal(destino)
    print("FIM", flush=True)
