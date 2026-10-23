"""Prints e conferência da janela DE VERDADE para a etapa 4 do layout.

Mesma montagem de prints_layout.py / prints_r14.py (cópia do Boécio, dados em saida_teste/, janela
fora da tela em 1280 x 657, sem roubar o foco); cliques por mensagens nativas do Windows
(prints_etapa3.clique_nativo). Cada passo confere o que aconteceu e escreve "ok" ou "FALHOU".

Uso: python prints_etapa4.py <pasta_de_saida>   (arquivo descartável do agente de layout)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prints_r14 as r  # noqa: E402  (a montagem e a Cena)
from prints_etapa3 import RESULTADOS, clique_nativo, conferir  # noqa: E402
from prints_layout import abrir_o_livro, esperar, nova_janela  # noqa: E402

from PySide6.QtCore import QPoint, QRect  # noqa: E402
from PySide6.QtWidgets import QPushButton  # noqa: E402


def foto(janela, nome, contornos=(), popup=None, onde=None):
    """A janela de verdade (grab, na escala da tela) com a peça solta colada."""
    cena = r.Cena(janela)
    pix = janela.grab()
    r.ESC = pix.devicePixelRatio()
    cena.img = pix.toImage()
    cena.img.setDevicePixelRatio(1)
    if popup is not None:
        cena.colar(popup, onde)
    cena.inteira(nome, list(contornos))
    return cena


def principal(destino: Path) -> None:
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    r.SAIDA = destino
    janela = nova_janela()
    tela = abrir_o_livro(janela, dividir=True)
    paineis = tela.paineis
    tela.ir_para_pagina(4)
    esperar(6)

    # --- 1. marcar: os botões no Propriedades, a fila de baixo vazia ---
    print("\n1. ferramentas de marcar")
    tela.escolher_ferramenta("retangulo")
    paineis.fechar()
    esperar(3)
    conferir(tela.barra_botoes.height() == 0, "Retângulo: a fila embaixo da página está vazia")
    foto(janela, "1-marcar-fechado")
    r.clicar = None
    from prints_etapa3 import clicar_no_icone
    clicar_no_icone(janela, tela, "props")
    esperar(2)
    extra = paineis.propriedades.extra_de_marcar
    conferir(paineis.aberto == "props" and extra.isVisible(),
             "clique nativo no ícone: o Propriedades mostra as partes de marcar")
    foto(janela, "1-marcar-propriedades", [r.no_janela(extra, janela)])
    from PySide6.QtWidgets import QAbstractButton
    espremidos = [(b.text(), b.height(), b.sizeHint().height())
                  for b in paineis.propriedades.corpo.findChildren(QAbstractButton)
                  if b.isVisible() and b.height() < b.sizeHint().height()]
    conferir(not espremidos, f"nenhum botão do Propriedades de marcar espremido ({espremidos})")
    rolagem = paineis.propriedades.rolagem.verticalScrollBar()
    rolagem.setValue(rolagem.maximum())
    esperar(0.5)
    foto(janela, "1-marcar-propriedades-rolado")
    rolagem.setValue(0)
    botao = next(b for b in extra.findChildren(QPushButton) if b.text() == "detectar automaticamente")
    rolagem.setValue(rolagem.maximum())
    esperar(0.3)
    clique_nativo(janela, botao)
    esperar(4)
    conferir("à mão continua" in tela.aviso_marcacao.text() or tela.aviso_marcacao.text() != "",
             f"clique nativo em 'detectar automaticamente' (aviso: {tela.aviso_marcacao.text()!r})")
    clique_nativo(janela, tela.caixa_tem_foto)
    esperar(3)
    conferir(tela.caixa_tem_foto.isChecked(), "clique nativo marcou 'Esta página tem foto'")
    clique_nativo(janela, tela.caixa_tem_foto)
    esperar(3)
    rolagem.setValue(0)

    # --- 2. o painel Filtro ---
    print("\n2. o painel Filtro")
    tela.trilha.escolher("cortar")
    paineis.fechar()
    esperar(3)
    clicar_no_icone(janela, tela, "filtro")
    esperar(8)
    painel = paineis.filtro_da_pagina
    conferir(paineis.aberto == "filtro" and painel.montado, "clique nativo abriu o painel Filtro montado")
    com_amostra = [c for c in painel.cartoes.values() if c.desenho.pixmap is not None]
    print("     páginas pequenas na fila:", len(com_amostra), "de", len(painel.cartoes))
    conferir(len(com_amostra) >= len(painel.cartoes) - 1,
             "a fila mostra a página nos filtros (com a ferramenta Cortar)")
    foto(janela, "2-filtro-original", [r.no_janela(painel.corpo, janela)])
    # escolher o Preto e branco pela fila (clique nativo)
    clique_nativo(janela, painel.cartoes[PRETO_E_BRANCO])
    esperar(6)
    pagina = janela.projeto.paginas[tela.indice_pagina]
    conferir(pagina.filtro == PRETO_E_BRANCO, "clique nativo na fila escolheu o Preto e branco")
    conferir(not painel.partes["letras"].isHidden() and not painel.partes["limpar"].isHidden(),
             "no Preto e branco aparecem 'Só as letras', 'Limpar a sujeira' e 'Mais ajustes'")
    foto(janela, "2-filtro-preto-e-branco")
    # abrir as partes pelo cabeçalho (clique nativo)
    for chave in ("ajuste", "limpar", "mais"):
        parte = painel.partes[chave]
        if not parte.aberta:
            painel.rolagem.ensureWidgetVisible(parte.cabeca)
            esperar(0.3)
            clique_nativo(janela, parte.cabeca)
            esperar(0.8)
        conferir(parte.aberta, f"clique nativo no cabeçalho abriu a parte '{chave}'")
    # o Só as letras ligado
    if not tela.escolhas_misto.caixa.isChecked():
        tela.escolhas_misto.caixa.setChecked(True)
        esperar(5)
    painel.rolagem.verticalScrollBar().setValue(0)
    esperar(0.5)
    foto(janela, "3-filtro-partes-abertas")
    espremidos = [(b.text(), b.height(), b.sizeHint().height())
                  for b in painel.corpo.findChildren(QPushButton)
                  if b.isVisible() and b.height() < b.sizeHint().height()]
    conferir(not espremidos, f"nenhum botão do painel Filtro espremido ({espremidos})")
    painel.rolagem.verticalScrollBar().setValue(painel.rolagem.verticalScrollBar().maximum())
    esperar(0.5)
    foto(janela, "3-filtro-partes-abertas-rolado")
    # as listas com amostra, abertas
    for nome, lista in (("4-lista-limpar-aberta", tela.seletor_pontinhos),
                        ("4-lista-letras-aberta", tela.escolhas_misto.lista_do_texto)):
        painel.rolagem.ensureWidgetVisible(lista)
        esperar(0.4)
        lista.showPopup()
        esperar(0.8)
        caixa = lista.view().window()
        onde = lista.mapTo(janela, QPoint(0, lista.height()))
        cena = foto(janela, nome, popup=caixa, onde=onde)
        cena.ampliado(nome + "-ampliado", r.com_folga(QRect(onde, caixa.size()).united(
            r.no_janela(lista, janela)), 8, janela), "A lista com amostra, aberta")
        lista.hidePopup()
        esperar(0.4)
    # trocar a limpeza pela lista
    antes = tela.seletor_pontinhos.currentData()
    from core import pontinhos_scantailor as ps
    tela.seletor_pontinhos.setCurrentIndex(tela.seletor_pontinhos.findData(ps.NORMAL))
    esperar(4)
    conferir(pagina.limpar_pontinhos == ps.NORMAL and antes != ps.NORMAL,
             "a lista 'Limpar a sujeira' grava na página")
    tela.desfazer()
    esperar(3)
    # Aplicar em, no pé
    pe = painel.pe
    conferir(pe.isVisible() and {b.text() for b in pe.findChildren(QPushButton)}
             >= {"só nesta", "todas", "daqui em diante"}, "o pé tem 'Aplicar em' com os três")
    # de volta ao Original (a fila fica no alto do painel: rolar até ela)
    painel.rolagem.verticalScrollBar().setValue(0)
    esperar(0.5)
    clique_nativo(janela, painel.cartoes[ORIGINAL])
    esperar(5)
    conferir(janela.projeto.paginas[tela.indice_pagina].filtro == ORIGINAL
             and painel.partes["letras"].isHidden(), "de volta ao Original, as partes do P&B somem")

    # --- 5. tamanhos e temas ---
    print("\n5. janela mínima, maximizada e temas")
    clique_nativo(janela, painel.cartoes[PRETO_E_BRANCO])
    esperar(5)
    painel.rolagem.verticalScrollBar().setValue(0)
    janela.resize(1000, 600)
    janela.move(-32000, -32000)
    esperar(3)
    foto(janela, "5-minima-filtro")
    janela.resize(1536, 785)
    janela.move(-32000, -32000)
    esperar(3)
    foto(janela, "5-maximizada-filtro")
    janela.resize(1280, 657)
    janela.move(-32000, -32000)
    esperar(2)
    for tema in ("escuro", "claro"):
        janela._trocar_tema(tema)
        esperar(1.5)
        foto(janela, f"5-filtro-{tema}")
    janela._trocar_tema("cinza")
    esperar(1)
    tela.escolher_ferramenta("retangulo")
    clicar_no_icone(janela, tela, "props")
    esperar(2)
    for tema in ("escuro", "claro"):
        janela._trocar_tema(tema)
        esperar(1.5)
        foto(janela, f"5-marcar-{tema}")
    janela._trocar_tema("cinza")
    esperar(1)

    # --- 6. os menus ligados ---
    print("\n6. menus")
    zoom_antes = tela.editor_selecao.zoom
    janela.menu.acoes["mais_zoom"].trigger()
    esperar(1)
    conferir(tela.editor_selecao.zoom > zoom_antes, "Ver > Aproximar aproximou a página")
    janela.menu.acoes["ajustar"].trigger()
    esperar(1)
    conferir(abs(tela.editor_selecao.zoom - 1.0) < 1e-6, "Ver > Ajustar à tela voltou a 100%")
    paineis.fechar()
    janela.menu.acoes["historico"].trigger()
    esperar(1)
    conferir(paineis.aberto == "historico", "Editar > Mostrar o histórico abriu o Histórico")
    arquivo = r.menu_do_titulo(janela, "Arquivo")
    onde = r.abrir_menu(janela, arquivo)
    recentes = janela.menu.menu_recentes
    recentes.aboutToShow.emit()
    geo = arquivo.actionGeometry(recentes.menuAction())
    recentes.popup(QPoint(-30000, -31000))
    esperar(0.5)
    cena = r.Cena(janela)
    cena.colar(arquivo, onde)
    cena.colar(recentes, QPoint(onde.x() + arquivo.width() - 4, onde.y() + geo.top()))
    cena.inteira("6-menu-livros-recentes")
    print("     livros recentes:", [a.text() for a in recentes.actions()])
    recentes.close()
    arquivo.close()
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
