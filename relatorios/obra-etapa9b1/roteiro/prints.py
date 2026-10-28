"""A janela de VERDADE, fora da tela (1280 x 657, o tamanho do notebook do Kaique a 150%), para os
prints da etapa 9b-1 da obra de 26/10/2026 (menus, impressão, janelas e lado direito).

Livros: CÓPIAS do Boécio ("Sobre a Consolação da Filosofia - Severino Boécio.pdf", nome com acento)
e do Marial (página 7, a do teste do "Pintar por cima"); os originais só são lidos.

Cliques por mensagens nativas do Windows (PostMessage), prints por PrintWindow
(relatorios/obra-etapa3/roteiro/base.py). A troca do jeito do lado direito é pelo item do menu
(QAction.trigger: o menu aberto por mensagem do Windows fecha sozinho fora da tela); os cliques nas
abas, nos botões do painel solto, nos ícones e na lista do Automático são por mensagem do Windows.
Dados e TEMP numa pasta de saida_teste/, nunca a pasta de dados do Samuel. Guarda o PID e fecha só a
própria janela (WM_CLOSE). NUNCA processa: a janela de salvar é fechada em "voltar", a "Antes de
processar" em "fechar"/Esc.

Uso (na worktree):
    .venv\\Scripts\\python.exe relatorios\\obra-etapa9b1\\roteiro\\prints.py <worktree> <prefixo>
<worktree> = o código a abrir (esta worktree, ou a cópia do código antigo para o "antes");
<prefixo> = "depois" ou "antes". Prints em relatorios/obra-etapa9b1/prints/.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

WORKTREE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RAIZ
PREFIXO = sys.argv[2] if len(sys.argv) > 2 else "depois"
PRINTS = RAIZ / "relatorios" / "obra-etapa9b1" / "prints"
TRAB = RAIZ / "saida_teste" / "obra-etapa9b1" / f"janela-{PREFIXO}"
TXT = PRINTS / f"{PREFIXO}-textos.txt"
NUMEROS: dict[str, str] = {}


def _p(widget, nome: str, so_cliente: bool = True):
    return base.print_window(widget, PRINTS / f"{PREFIXO}-{nome}.png", so_cliente=so_cliente)


def _esperar_ate(condicao, segundos=60.0) -> bool:
    for _ in range(int(segundos / 0.2)):
        if condicao():
            return True
        base.esperar(0.2)
    return condicao()


def _print_do_menu(janela, titulo: str, nome: str, submenu=None):
    """Abre o menu `titulo` da barra (popup, fora da tela), tira o print e lista os itens."""
    from PySide6.QtCore import QPoint

    menu = submenu if submenu is not None else janela.menu.menus[titulo]
    base.print_do_menu_que_abrir(f"{PREFIXO}-{nome}", PRINTS, TXT)
    menu.popup(QPoint(-30000, -30000))
    base.esperar(1.6)
    if menu.isVisible():
        menu.close()


def _clicar_na_fila(janela, fila, painel):
    base.clique(janela, fila, fila.retangulos()[painel].center())
    base.esperar(0.8)


def main() -> None:
    from PySide6.QtCore import QPoint

    (RAIZ / "saida_teste" / "obra-etapa9b1").mkdir(parents=True, exist_ok=True)
    (RAIZ / "saida_teste" / "obra-etapa9b1" / f"pid-prints-{PREFIXO}.txt").write_text(str(os.getpid()))
    print("PID deste processo:", os.getpid(), flush=True)
    base.preparar(str(WORKTREE), str(TRAB))
    PRINTS.mkdir(parents=True, exist_ok=True)
    if TXT.exists():
        TXT.unlink()
    boecio = base.copia("Sobre a Consolação da Filosofia - Severino Boécio.pdf",
                        "Sobre a Consolação da Filosofia - Severino Boécio.pdf")
    janela = base.nova_janela(1280, 657)
    janela.abrir_livro(str(boecio))
    base.esperar(2.0)
    tela = janela.tela_conferir
    _esperar_ate(lambda: getattr(janela, "medida_ao_abrir", None) is None, 240)
    base.esperar(1.0)
    paineis = tela.paineis

    # 9 (P-125): livro recém-aberto, nada feito -> Desfazer cinza no menu Editar
    NUMEROS["Editar > Desfazer aceso sem nada feito"] = str(janela.menu.acoes["desfazer"].isEnabled())
    _print_do_menu(janela, "Editar", "01-menu-editar-sem-nada-feito")

    # 3 (D-492): página 2 em Preto e branco pela tecla 2 (na página), o menu Filtro marca;
    # página 1 (Original), o menu marca Original
    base.clique(janela, tela.area_imagem.currentWidget())
    tela.ir_para_pagina(1)
    base.esperar(1.0)
    base.tecla(janela, 0x32)                     # "2" = Preto e branco
    base.esperar(1.5)
    NUMEROS["página 2: filtro"] = tela.projeto.paginas[1].filtro
    _print_do_menu(janela, "Filtro", "02-menu-filtro-pagina-2-preto-e-branco")
    tela.ir_para_pagina(0)
    base.esperar(1.0)
    NUMEROS["página 1: filtro"] = tela.projeto.paginas[0].filtro
    _print_do_menu(janela, "Filtro", "03-menu-filtro-pagina-1-original")
    NUMEROS["Editar > Desfazer aceso depois do filtro"] = str(janela.menu.acoes["desfazer"].isEnabled())

    # 2 (D-033): o menu Ver > Lado direito e os quatro jeitos
    _print_do_menu(janela, "Ver", "04-menu-ver-lado-direito", submenu=janela.menu.menu_do_lado_direito)
    icones = paineis.icones
    base.clique(janela, icones, icones.retangulos()["revisar"].center())
    base.esperar(1.2)
    _p(janela, "05-lado-icones-na-borda")
    if "lado_abas" in janela.menu.acoes:
        janela.menu.acoes["lado_abas"].trigger()
        base.esperar(1.5)
        base.conferir(paineis.jeito == "abas" and paineis.abas.isVisible(), "abas no alto à vista")
        _p(janela, "06-lado-abas-no-alto")
        _clicar_na_fila(janela, paineis.fila_de_abas, "filtro")
        base.conferir(paineis.aberto == "filtro", "clique na aba 'Filtro' abriu o painel Filtro da página")
        _p(janela, "07-lado-abas-no-alto-filtro")
        janela.menu.acoes["lado_solto"].trigger()
        base.esperar(1.5)
        base.conferir(paineis.botoes_do_alto.isVisible(), "painel solto: os botões na linha de cima")
        largura = tela.vista_da_pagina.width()
        _clicar_na_fila(janela, paineis.botoes_do_alto, "revisar")
        base.esperar(0.8)
        base.conferir(paineis.aberto == "revisar" and paineis.moldura_do_solto.isVisible(),
                      "clique no botão 'Para revisar' de cima: o painel por cima da página")
        base.conferir(tela.vista_da_pagina.width() == largura, "a página não encolheu (painel solto)")
        _p(janela, "08-lado-painel-solto")
        _clicar_na_fila(janela, paineis.botoes_do_alto, "revisar")
        base.conferir(paineis.aberto is None, "clique de novo no botão: fechou")
        janela.menu.acoes["lado_sanfona"].trigger()
        base.esperar(1.5)
        _p(janela, "09-lado-sanfona")
        janela.menu.acoes["lado_icones"].trigger()
        base.esperar(1.0)
    # as Configurações > Aparência (o mesmo "Lado direito")
    from ui.tela_configuracoes import TelaConfiguracoes

    configuracoes = TelaConfiguracoes(janela)
    configuracoes.resize(900, 600)
    configuracoes.show()
    base.esperar(1.5)
    _p(configuracoes, "10-configuracoes-lado-direito", so_cliente=False)
    base.gravar_textos(configuracoes, TXT, "Configurações")
    configuracoes.close()
    base.esperar(0.5)

    # 10: a barra de baixo a 1280 com um painel aberto (o contador inteiro)
    if paineis.aberto != "revisar":
        base.clique(janela, icones, icones.retangulos()["revisar"].center())
        base.esperar(1.2)
    NUMEROS["rodapé, painel aberto (o que se vê)"] = repr(tela.rotulo_do_livro.text())
    NUMEROS["rodapé (balão)"] = tela.rotulo_do_livro.toolTip()
    _p(janela, "11-barra-de-baixo-com-painel-aberto")

    # 8: clique na lista do Automático, depois Page Down chega à página
    base.clique(janela, icones, icones.retangulos()["automatico"].center())
    base.esperar(1.2)
    lista = paineis.automatico.lista
    base.clique(janela, tela.area_imagem.currentWidget())
    ret = lista.visualItemRect(lista.item(1))
    base.clique(janela, lista.viewport(), QPoint(ret.center().x(), ret.center().y()))
    antes = tela.indice_atual
    base.tecla(janela, 0x22)                    # Page Down
    base.esperar(1.5)
    NUMEROS["Page Down depois de clicar na lista do Automático"] = f"página {antes + 1} -> {tela.indice_atual + 1}"
    _p(janela, "12-page-down-depois-da-lista-do-automatico")

    # 4 + 6 (D-274, D-283): menu Arquivo > "Confirmar e processar" com avisos pendentes -> a
    # "Antes de processar" (avisos postos para a foto: 12 páginas com "Endireitar: as contas
    # discordam", o motivo mais comprido) -> "Mostrar" nesse motivo -> fechar (não processa)
    from core import analise
    from ui.janela_dos_avisos import JanelaDosAvisos

    for indice in range(2, 14):
        tela.projeto.paginas[indice].alertas = [analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
        tela.projeto.paginas[indice].revisada = False
    tela.atualizar()
    base.esperar(1.0)

    def no_mostrar(w):
        NUMEROS["Antes de processar (frase)"] = w.rotulo.text()
        NUMEROS["Antes de processar (tamanho)"] = f"{w.width()} x {w.height()}"
        combo = w.combo_motivo
        for i in range(combo.count()):
            if combo.itemText(i).startswith("Endireitar"):
                combo.setCurrentIndex(i)
        base.esperar(0.8)
        NUMEROS["Mostrar"] = combo.currentText()
        base.print_window(w, PRINTS / f"{PREFIXO}-14-antes-de-processar-mostrar.png", so_cliente=False)

    base.quando_abrir_janela(JanelaDosAvisos, f"{PREFIXO}-13-antes-de-processar-pelo-menu", PRINTS, TXT,
                             depois=no_mostrar, fechar=True)
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    from ui.janela_confirmar import JanelaConfirmar

    def se_foi_direto_para_salvar():
        """No código antigo o menu ia direto à janela de salvar (sem a "Antes de processar"):
        print dela e "voltar" (nunca processa)."""
        for w in QApplication.topLevelWidgets():
            if isinstance(w, JanelaConfirmar) and w.isVisible():
                NUMEROS["menu processar foi direto para a janela de salvar"] = "sim"
                base.print_window(w, PRINTS / f"{PREFIXO}-13-menu-processar-foi-direto-para-salvar.png",
                                  so_cliente=False)
                w.reject()

    QTimer.singleShot(4000, se_foi_direto_para_salvar)
    janela.menu.acoes["processar"].trigger()
    base.esperar(6.0)
    NUMEROS["menu processar mostrou a 'Antes de processar'"] = str(
        (PRINTS / f"{PREFIXO}-13-antes-de-processar-pelo-menu.png").exists())

    # 5 (D-555): a janela de salvar (pelo botão, "continuar assim mesmo") com o nome sugerido
    from ui.janela_confirmar import JanelaConfirmar

    def continuar(w):
        w.botao_continuar.click()

    def nome_sugerido(w):
        campo = getattr(getattr(w, "destino", None), "campo_nome", None)
        NUMEROS["nome sugerido"] = campo.text() if campo is not None else "(ver o print)"

    base.quando_abrir_janela(JanelaDosAvisos, f"{PREFIXO}-15-antes-de-processar-pelo-botao", PRINTS, TXT,
                             depois=continuar, fechar=False)
    base.quando_abrir_janela(JanelaConfirmar, f"{PREFIXO}-16-janela-de-salvar-nome-com-acento", PRINTS, TXT,
                             depois=nome_sugerido, fechar=True, espera_ms=2500)
    base.clique(janela, tela.botao_processar)
    base.esperar(10.0)

    # 1 (C3): a "Montar para imprimir" com os nomes do fase-1 (sobre a cópia do Boécio)
    from ui.dialogo_impressao import DialogoImpressao

    dialogo = DialogoImpressao(str(boecio), janela)
    dialogo.show()
    base.esperar(2.0)
    _p(dialogo, "17-montar-para-imprimir", so_cliente=False)
    base.gravar_textos(dialogo, TXT, "Montar para imprimir")
    from PySide6.QtWidgets import QScrollArea

    for rolagem in dialogo.findChildren(QScrollArea):     # as opções de baixo (rolando)
        barra = rolagem.verticalScrollBar()
        barra.setValue(barra.maximum())
    base.esperar(1.0)
    _p(dialogo, "17b-montar-para-imprimir-embaixo", so_cliente=False)
    NUMEROS["Montar para imprimir: nome sugerido"] = dialogo.destino_sugerido().name
    dialogo.reject()
    base.esperar(0.5)

    # 7 (D-250): "Pintar por cima" sobre o começo das linhas do Marial 7 -> o aviso -> "Voltar"
    marial = base.copia("Marial de sermoens - Frei Balthasar Paez. (1).pdf", "Marial de sermões.pdf")
    janela.abrir_livro(str(marial))
    base.esperar(3.0)
    tela = janela.tela_conferir
    tela.ir_para_pagina(6)
    base.esperar(1.5)
    from core.selecao import PINTAR
    from ui.widgets.editor_selecao import FERRAMENTA_RETANGULO

    tela.escolher_ferramenta("retangulo")
    base.esperar(1.0)
    editor = tela.editor_selecao
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    editor.definir_tipo(PINTAR)
    base.esperar(2.0)
    antes = len(editor.selecao)
    from PySide6.QtWidgets import QMessageBox

    def voltar(w):
        alvo = next((b for b in w.buttons() if b.text().replace("&", "") == "Voltar"), None)
        NUMEROS["aviso do Pintar por cima"] = w.text() + " | " + ", ".join(b.text() for b in w.buttons())
        if alvo is not None:
            alvo.click()

    base.quando_abrir_janela(QMessageBox, f"{PREFIXO}-18-pintar-por-cima-aviso", PRINTS, TXT,
                             depois=voltar, fechar=False)
    base.arrastar(janela, editor, editor._para_tela(0.05, 0.15), editor._para_tela(0.20, 0.45))
    base.esperar(4.0)
    NUMEROS["áreas depois do 'Voltar'"] = f"{antes} -> {len(editor.selecao)}"
    _p(janela, "19-pintar-por-cima-depois-do-voltar")

    with open(PRINTS / f"{PREFIXO}-numeros.txt", "w", encoding="utf-8") as f:
        for chave, valor in NUMEROS.items():
            f.write(f"{chave}: {valor}\n")
    for chave, valor in NUMEROS.items():
        print(f"  {chave}: {valor}", flush=True)
    base.fechar(janela)
    base.gravar_resultados(TRAB)


if __name__ == "__main__":
    main()
