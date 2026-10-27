"""A janela de VERDADE, fora da tela, abrindo um livro SEM NENHUMA caixinha marcada (D-001; etapa 2
da obra de 26/10/2026). Cliques e teclas por mensagens nativas do Windows (PostMessage), prints por
PrintWindow (roteiro/base.py, do verificador de 22-23/10). Dados e TEMP numa pasta de saida_teste/,
nunca a pasta de dados do Samuel; o livro é uma CÓPIA (o acervo só é lido). Guarda o PID e fecha só a
própria janela (WM_CLOSE).

Uso (na worktree):
    .venv\\Scripts\\python.exe relatorios\\obra-etapa2\\roteiro\\print_sem_caixinhas.py <worktree> <prefixo>
<worktree> = o código a abrir (esta worktree, ou a do código antigo para o "antes"); <prefixo> = nome
dos prints (ex.: "depois" ou "antes"). Prints em relatorios/obra-etapa2/prints/.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path.insert(0, str(AQUI))
import base  # noqa: E402

WORKTREE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RAIZ
PREFIXO = sys.argv[2] if len(sys.argv) > 2 else "depois"
PRINTS = RAIZ / "relatorios" / "obra-etapa2" / "prints"
TXT = PRINTS / f"{PREFIXO}-o-que-se-ve.txt"
TRAB = RAIZ / "saida_teste" / "obra-etapa2" / f"janela-{PREFIXO}"
VK_DELETE = 0x2E


def main() -> None:
    print("PID deste processo:", os.getpid(), flush=True)
    base.preparar(str(WORKTREE), str(TRAB))
    from PySide6.QtCore import QEvent, QPoint
    from PySide6.QtWidgets import QApplication, QPushButton, QToolTip

    if TXT.exists():
        TXT.unlink()
    livro = base.copia("Sobre a Consolação da Filosofia - Severino Boécio.pdf", "Boecio.pdf")
    janela = base.nova_janela(1280, 657)
    janela.abrir_livro(str(livro))
    base.esperar(1.5)
    opcoes = janela.tela_opcoes
    # 0. como a tela vem de fabrica (as caixinhas marcadas: o quadrado azul com o tique)
    base.print_window(janela, PRINTS / f"{PREFIXO}-00-o-que-fazer-de-fabrica.png")

    # 1. desmarca TODAS as caixinhas de etapa com o mouse de verdade
    for nome in ("cx_dividir", "cx_cortar", "cx_endireitar", "cx_limpar"):
        caixa = getattr(opcoes, nome)
        if caixa.isChecked():
            if hasattr(opcoes, "rolagem"):
                opcoes.rolagem.ensureWidgetVisible(caixa)
                base.esperar(0.3)
            base.clique(janela, caixa, QPoint(10, caixa.height() // 2))
        if caixa.isChecked():                 # o clique não pegou: diz e desmarca por dentro
            print(f"  (o clique não desmarcou {nome}; desmarcado por dentro)", flush=True)
            caixa.setChecked(False)
    base.conferir(not any(getattr(opcoes, n).isChecked()
                          for n in ("cx_dividir", "cx_cortar", "cx_endireitar", "cx_limpar")),
                  "nenhuma caixinha de etapa marcada")
    if hasattr(opcoes, "rolagem"):
        opcoes.rolagem.verticalScrollBar().setValue(0)
    base.esperar(0.5)
    base.print_window(janela, PRINTS / f"{PREFIXO}-01-o-que-fazer-sem-caixinhas.png")
    ativos = [t for t, m in janela.menu.menus.items() if m.menuAction().isEnabled()]
    base.conferir(True, f"menus acesos na tela das caixinhas: {ativos}")

    # 2. Conferir (com o mouse), e espera a área de trabalho
    base.clique(janela, opcoes.botao_conferir)
    for _ in range(150):
        if janela.telas.currentIndex() == 3:
            break
        base.esperar(0.2)
    base.esperar(4)
    tela = janela.tela_conferir
    if not base.conferir(janela.telas.currentIndex() == 3, "abriu a área de trabalho"):
        # o código antigo nem abre o livro sem caixinha ("Conferir" cinza)
        base.conferir(False, f"Conferir aceso: {opcoes.botao_conferir.isEnabled()}; "
                             f"resumo: {opcoes.resumo.text()!r}")
        base.print_window(janela, PRINTS / f"{PREFIXO}-02-nao-abriu.png")
        base.fechar(janela)
        base.gravar_resultados(PRINTS / f"{PREFIXO}-resultado")
        return
    base.conferir(True, f"ferramentas montadas: {tela._abas_ativas}")
    grupos = sorted(tela.trilha.retangulos())
    base.conferir(True, f"botões na trilha: {len(grupos)}")
    ativos = [t for t, m in janela.menu.menus.items() if m.menuAction().isEnabled()]
    base.conferir(True, f"menus acesos na área de trabalho: {ativos}")
    base.print_window(janela, PRINTS / f"{PREFIXO}-02-area-de-trabalho-sem-caixinhas.png")
    base.gravar_textos(janela, TXT, "área de trabalho sem caixinhas")

    # 3. o balão da trilha com o mouse parado em cima (Endireitar, e o grupo do Retângulo).
    #    O Qt só mostra balão em janela ATIVA; esta, fora da tela, abre sem ativar (para não
    #    roubar o teclado do Samuel), e aí nenhum balão aparece - foi por isso que o teste do
    #    Kaique de 26/10 não viu as dicas. Aqui a janela de teste ganha o "mostrar balão
    #    sempre" do Qt; no uso de verdade a janela está ativa e o balão aparece igual.
    from PySide6.QtCore import Qt
    janela.setAttribute(Qt.WA_AlwaysShowToolTips, True)
    trilha = tela.trilha
    from ui.widgets.trilha_agrupada import grupo_de
    for ferramenta in ("endireitar", "retangulo"):
        indice = grupo_de(ferramenta)
        if indice not in trilha.retangulos():
            base.conferir(False, f"{ferramenta} não está na trilha")
            continue
        centro = trilha.retangulos()[indice].center()
        alvo = trilha.mapTo(janela, centro)
        h = int(janela.winId())
        for desloca in (0, 1, 2):
            base.user32.PostMessageW(h, base.WM_MOUSEMOVE, 0,
                                     base._lp(janela, QPoint(alvo.x() + desloca, alvo.y())))
            base.esperar(0.1)
        base.esperar(1.8)
        texto = QToolTip.text() if QToolTip.isVisible() else ""
        if not texto:
            # Com a janela fora da tela, o cursor de verdade não está em cima dela: o Windows
            # manda "o mouse saiu" logo depois de cada movimento postado, e o Qt nunca chega a
            # contar os 0,7 s do balão (depurado em 26/10: a trilha recebe só "Enter"). Mexer
            # no cursor de verdade atrapalharia o Samuel. Então o roteiro manda à trilha o
            # MESMO evento de balão que o Qt manda depois dos 0,7 s parado (QHelpEvent).
            from PySide6.QtGui import QHelpEvent
            print(f"  (o balão por movimento postado não sai fora da tela; mando o evento de "
                  f"balão do Qt para {ferramenta})", flush=True)
            QApplication.sendEvent(trilha, QHelpEvent(
                QEvent.ToolTip, centro, trilha.mapToGlobal(centro)))
            base.esperar(0.6)
            texto = QToolTip.text() if QToolTip.isVisible() else ""
        base.conferir(bool(texto), f"balão de {ferramenta}: {texto!r}")
        dicas = [w for w in QApplication.topLevelWidgets()
                 if w.metaObject().className() == "QTipLabel" and w.isVisible()]
        if dicas:
            # o balao e uma janela transparente: o PrintWindow do Windows a da preta; o
            # desenho do proprio Qt (grab) mostra o que aparece na tela
            dicas[0].grab().save(str(PRINTS / f"{PREFIXO}-03-balao-{ferramenta}.png"))
        base.user32.PostMessageW(h, base.WM_MOUSEMOVE, 0, base._lp(janela, QPoint(640, 300)))
        base.esperar(0.5)

    # 4. as ferramentas pela trilha, com o mouse: Endireitar e Retângulo; o painel Propriedades
    #    mostra no alto "Esta página" com "deixar em branco" e "tirar do livro"
    for ferramenta, nome in (("endireitar", "endireitar"), ("retangulo", "retangulo")):
        indice = grupo_de(ferramenta)
        if indice in trilha.retangulos():
            base.clique(janela, trilha, trilha.retangulos()[indice].center())
            base.esperar(1.5)
            base.conferir(tela.trilha.ferramenta == ferramenta, f"o clique na trilha escolheu {ferramenta}")
            if not getattr(tela.paineis, "aberto", None):
                tela.paineis.abrir("props")
                base.esperar(0.8)
            base.print_window(janela, PRINTS / f"{PREFIXO}-04-{nome}-com-propriedades.png")

    # 5. o menu Ferramentas (se existir) aberto
    if "Ferramentas" in janela.menu.menus:
        menu = janela.menu.menus["Ferramentas"]
        base.print_do_menu_que_abrir(f"{PREFIXO}-05-menu-ferramentas", PRINTS, TXT)
        menu.popup(janela.mapToGlobal(QPoint(120, 30)))
        base.esperar(3)

    # 6. a tecla Delete na página 3 (deixa em branco)
    tela.ir_para_pagina(2)
    base.esperar(1)
    pagina = janela.projeto.paginas[2]
    janela.activateWindow()
    base.tecla(janela, VK_DELETE)
    base.esperar(1.5)
    base.conferir(True, f"Delete na página 3: em_branco={getattr(pagina, 'em_branco', None)}, "
                        f"tirada do livro={pagina.apagada}")
    base.print_window(janela, PRINTS / f"{PREFIXO}-06-delete-deixou-em-branco.png")

    # 7. a área de trabalho 1 (sanfona), pelo menu Ver, se existir
    if "lado_sanfona" in janela.menu.acoes:
        janela.menu.acoes["lado_sanfona"].trigger()
        base.esperar(1.5)
        base.conferir(tela.paineis.jeito == "sanfona", "menu Ver > Lado direito > Sanfona")
        base.print_window(janela, PRINTS / f"{PREFIXO}-07-area-de-trabalho-1-sanfona.png")
        linhas = tela.paineis.linhas_da_sanfona
        base.clique(janela, linhas["revisar"])
        base.esperar(1.2)
        base.conferir(tela.paineis.aberto == "revisar", "clique na linha \"Para revisar\" da sanfona abriu o painel")
        base.print_window(janela, PRINTS / f"{PREFIXO}-08-sanfona-para-revisar-aberto.png")
        janela.menu.acoes["lado_icones"].trigger()       # volta ao de fábrica
        base.esperar(0.8)

    base.fechar(janela)
    base.gravar_resultados(PRINTS / f"{PREFIXO}-resultado")


if __name__ == "__main__":
    main()
