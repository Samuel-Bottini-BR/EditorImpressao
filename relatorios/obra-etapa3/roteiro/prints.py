"""A janela de VERDADE, fora da tela, no caminho novo da etapa 3 da obra (26/10/2026): o livro abre
direto na área de trabalho com o aviso do livro novo; painel Automático; "Rodar o automático…" abre a
janela grande com a receita de sempre; "escolher páginas..." na grade; Rodar; a grade com várias
escolhidas; o retângulo do corte na página e nas Configurações; o livro aberto com "Para revisar" e
"Receita usada". Cliques por mensagens nativas do Windows (PostMessage), prints por PrintWindow
(roteiro/base.py, do verificador de 22-23/10). Dados e TEMP numa pasta de saida_teste/, nunca a pasta
de dados do Samuel; o livro é uma CÓPIA (o acervo só é lido). Guarda o PID e fecha só a própria
janela (WM_CLOSE).

Uso (na worktree):
    .venv\\Scripts\\python.exe relatorios\\obra-etapa3\\roteiro\\prints.py <worktree> <prefixo>
<worktree> = o código a abrir (esta worktree, ou a do código antigo para o "antes"); <prefixo> =
nome dos prints ("depois" ou "antes"). Prints em relatorios/obra-etapa3/prints/.
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
PRINTS = RAIZ / "relatorios" / "obra-etapa3" / "prints"
TRAB = RAIZ / "saida_teste" / "obra-etapa3" / f"janela-{PREFIXO}"


def _p(janela_ou_widget, nome: str):
    return base.print_window(janela_ou_widget, PRINTS / f"{PREFIXO}-{nome}.png")


def _esperar_ate(condicao, segundos=60.0) -> bool:
    for _ in range(int(segundos / 0.2)):
        if condicao():
            return True
        base.esperar(0.2)
    return condicao()


def main() -> None:
    (RAIZ / "saida_teste" / "obra-etapa3").mkdir(parents=True, exist_ok=True)
    (RAIZ / "saida_teste" / "obra-etapa3" / f"pid-prints-{PREFIXO}.txt").write_text(str(os.getpid()))
    print("PID deste processo:", os.getpid(), flush=True)
    base.preparar(str(WORKTREE), str(TRAB))
    from ui.janela_principal import CONFERIR

    livro = base.copia("Sobre a Consolação da Filosofia - Severino Boécio.pdf", "Boecio.pdf")
    janela = base.nova_janela(1280, 657)
    _p(janela, "00-tela-dos-livros")
    janela.abrir_livro(str(livro))
    base.esperar(2.0)
    if hasattr(janela, "tela_opcoes") and janela.telas.currentIndex() != CONFERIR:
        # o codigo antigo: abrir leva a tela "O que fazer"
        base.conferir(True, "código antigo: abrir o livro leva à tela 'O que fazer'")
        _p(janela, "01-abrir-o-livro")
        base.fechar(janela)
        base.gravar_resultados(TRAB)
        return

    tela = janela.tela_conferir
    base.conferir(janela.telas.currentIndex() == CONFERIR, "D-002: o livro abriu direto na área de trabalho")
    base.conferir(tela.aviso_do_livro_novo.isVisible(), "D-005: o aviso do livro novo está na tela")
    _esperar_ate(lambda: getattr(janela, "medida_ao_abrir", None) is None
                 or not janela.medida_ao_abrir.isRunning(), 120)
    base.esperar(1.0)
    _p(janela, "01-abrir-o-livro")

    # o painel Automatico
    tela.paineis.mostrar_painel("automatico", True)
    base.esperar(1.0)
    _p(janela, "02-painel-automatico")

    # "Rodar o automatico…" do aviso, com o mouse -> a janela grande com a receita de sempre
    base.clique(janela, tela.botao_rodar_do_aviso)
    base.esperar(1.5)
    jan = janela.janela_do_automatico
    if not base.conferir(jan is not None and jan.isVisible(), "D-018: o aviso abriu a janela grande"):
        base.fechar(janela)
        base.gravar_resultados(TRAB)
        return
    # o MoveWindow do base.py (que poe a janela fora da tela) usa o tamanho de antes do Show:
    # devolve o tamanho que o programa da (92% da janela principal)
    jan.resize(int(janela.width() * 0.92), int(janela.height() * 0.92))
    base.esperar(1.0)
    # o PrintWindow pegava o meio ainda sem pintar (o grab do Qt mostra certo): passar pela
    # etapa de novo faz o Windows pintar
    from core import automatico as A

    jan.mostrar_etapa(A.LIMPAR)
    base.esperar(0.3)
    jan.mostrar_etapa(A.ENDIREITAR)
    base.esperar(1.0)
    _p(jan, "03-janela-grande-receita-de-sempre")

    for etapa, nome in ((A.LIMPAR, "04-janela-grande-limpar"), (A.GRAVURAS, "05-janela-grande-gravuras"),
                        (A.ENDIREITAR, "06-janela-grande-endireitar")):
        jan.mostrar_etapa(etapa)
        base.esperar(0.8)
        _p(jan, nome)

    # "escolher paginas..." -> a grade escolhendo
    base.clique(jan, jan.botao_escolher)
    base.esperar(1.5)
    grade = tela.todas
    base.conferir(tela.pilha_da_tela.currentWidget() is grade, "D-334: 'escolher páginas...' abriu a grade")
    for indice in (2, 3, 5):
        grade.marcar(indice)
    base.esperar(1.0)
    _p(janela, "07-grade-escolhendo-para-o-automatico")
    base.clique(janela, grade.botao_usar)
    base.esperar(1.5)
    jan = janela.janela_do_automatico
    base.conferir(jan is not None and janela.estado_do_automatico.escolhidas == [2, 3, 5],
                  "a grade devolveu as 3 páginas ao Automático")
    janela.estado_do_automatico.definir_alcance("livro")
    base.esperar(0.5)

    # Rodar (com o mouse), no livro todo, com a receita de sempre
    base.clique(jan, jan.botao_rodar)
    _esperar_ate(lambda: getattr(janela, "tarefa", None) is None or not janela.tarefa.isRunning(), 300)
    base.esperar(3.0)
    base.conferir(janela.projeto.passou_pelo_automatico and janela.projeto.endireitar,
                  "Rodar ligou as etapas no livro")
    base.conferir(not tela.aviso_do_livro_novo.isVisible(), "o aviso do livro novo sumiu")
    _p(janela, "08-depois-de-rodar")

    # a grade com varias escolhidas (girar, em branco, tirar, extrair, rodar nelas)
    _esperar_ate(tela._pronta, 60)
    tela.abrir_todas_as_paginas()
    base.esperar(1.0)
    base.conferir(tela.pilha_da_tela.currentWidget() is grade, "a grade abriu")
    grade.comecar_a_escolher([])
    for indice in (1, 4, 6):
        grade.marcar(indice)
    base.esperar(1.0)
    _p(janela, "09-grade-varias-escolhidas")
    grade.escolher_nenhuma()
    tela.ir_para_pagina(3)
    tela.pilha_da_tela.setCurrentIndex(0)
    base.esperar(1.0)

    # a pagina: Endireitar com o retangulo do corte (D-094)
    from ui.widgets.trilha_agrupada import FERRAMENTA_ENDIREITAR

    tela.escolher_ferramenta(FERRAMENTA_ENDIREITAR)
    base.esperar(1.5)
    from PySide6.QtWidgets import QScrollArea

    combo = tela.combo_retangulo_da_pagina
    for rolagem in janela.findChildren(QScrollArea):
        if rolagem.isAncestorOf(combo):
            rolagem.ensureWidgetVisible(combo)
    base.esperar(0.8)
    base.conferir(combo.isVisible(), "D-094: a página tem o retângulo do corte")
    _p(janela, "10-pagina-endireitar-retangulo")

    # o livro aberto (voltar para os livros): Para revisar e Receita usada
    janela._sair_da_conferencia()
    base.esperar(1.5)
    import projetos

    janela.tela_inicio.abrir_o_livro(projetos.listar()[0])
    base.esperar(1.5)
    aberto = janela.tela_inicio.livro_aberto
    base.conferir("Receita usada" in aberto.receita_usada.text(), "livro aberto: 'Receita usada'")
    base.conferir("Para revisar" in aberto.para_revisar.text(), "livro aberto: 'Para revisar'")
    _p(janela, "11-livro-aberto")

    # Configuracoes > Medidas e receitas: o retangulo do corte
    from ui.tela_configuracoes import TelaConfiguracoes

    config = TelaConfiguracoes(janela, parte="Medidas e receitas")
    config.setAttribute(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.WA_ShowWithoutActivating)
    config.show()
    base.esperar(1.5)
    base.conferir(config.combo_retangulo.isVisible(), "D-094: Configurações têm o retângulo do corte")
    _p(config, "12-configuracoes-retangulo")
    config.close()
    base.esperar(0.5)

    base.fechar(janela)
    base.gravar_resultados(TRAB)


if __name__ == "__main__":
    main()
