"""A janela de VERDADE, fora da tela (1280 x 657, o notebook do Kaique a 150%), do zero e sem nada
marcado, para os itens de tela da etapa 9b-2 da obra (27/10/2026). Livros: uma CÓPIA do "La vida
eterna" e uma cópia de duas folhas do Righetti (folhas 95 e 96; os originais só são lidos).

Cliques por mensagens nativas do Windows (PostMessage) e prints por PrintWindow
(relatorios/obra-etapa3/roteiro/base.py). Onde o clique nativo não chega (a roda do mouse numa
janela fora da tela, as janelas que abrem com exec()), o passo diz como foi feito. Dados e TEMP
numa pasta de saida_teste/, nunca a pasta de dados do Samuel. Guarda o PID e fecha só a própria
janela (WM_CLOSE).

Uso (na worktree):
    .venv\\Scripts\\python.exe relatorios\\obra-etapa9b2\\roteiro\\prints.py <worktree> <prefixo>
Prints em relatorios/obra-etapa9b2/prints/.
"""
from __future__ import annotations

import os
import shutil
import sys
import traceback
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

WORKTREE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RAIZ
PREFIXO = sys.argv[2] if len(sys.argv) > 2 else "depois"
PRINTS = RAIZ / "relatorios" / "obra-etapa9b2" / "prints"
TRAB = RAIZ / "saida_teste" / "obra-etapa9b2" / f"janela-{PREFIXO}"
LIVRO = Path(r"D:/Livros para editar/2 - TEOLOGIA/Escatologia/La vida eterna y La profundidad del alma.pdf")
RIGHETTI = "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf"


def _p(widget, nome: str, so_cliente=True):
    return base.print_window(widget, PRINTS / f"{PREFIXO}-{nome}.png", so_cliente=so_cliente)


def _esperar_ate(condicao, segundos=60.0) -> bool:
    for _ in range(int(segundos / 0.2)):
        try:
            if condicao():
                return True
        except Exception:  # noqa: BLE001
            pass
        base.esperar(0.2)
    return bool(condicao())


def _passo(nome, funcao):
    try:
        funcao()
    except Exception:  # noqa: BLE001 - um passo que falha não para os outros
        base.conferir(False, f"{nome}: {traceback.format_exc().splitlines()[-1]}")


def _livro(janela, caminho: Path):
    janela.abrir_livro(str(caminho))
    base.esperar(2.0)
    _esperar_ate(lambda: getattr(janela, "medida_ao_abrir", None) is None
                 or not janela.medida_ao_abrir.isRunning(), 240)
    base.esperar(1.0)
    return janela.tela_conferir


def _a_previa(tela, indice):
    _esperar_ate(lambda: tela.previas.ja_pronta(indice, tela._dpi_atual) is not None, 90)
    base.esperar(1.0)


def main() -> None:
    (RAIZ / "saida_teste" / "obra-etapa9b2").mkdir(parents=True, exist_ok=True)
    (RAIZ / "saida_teste" / "obra-etapa9b2" / f"pid-prints-{PREFIXO}.txt").write_text(str(os.getpid()))
    print("PID deste processo:", os.getpid(), flush=True)
    base.preparar(str(WORKTREE), str(TRAB))
    PRINTS.mkdir(parents=True, exist_ok=True)
    livro = TRAB / "La vida eterna.pdf"
    shutil.copy2(LIVRO, livro)
    janela = base.nova_janela(1280, 657)
    tela = _livro(janela, livro)
    projeto = janela.projeto
    base.conferir(not projeto.dividir_folhas and not projeto.cortar_bordas, "abrir sem nada marcado")

    from ui.widgets.paginas_rolando import DUAS, UMA

    def cortar():
        # D-554: a caixinha "Margens iguais" no Cortar
        tela.ir_para_pagina(6)
        tela.escolher_ferramenta("cortar")
        base.esperar(2.0)
        caixa = tela.caixa_margens_iguais
        # a caixinha fica no fim do painel Propriedades: rolar até ela (como o Kaique faria)
        from PySide6.QtCore import QPoint
        from PySide6.QtWidgets import QScrollArea
        rolagem = caixa.parentWidget()
        while rolagem is not None and not isinstance(rolagem, QScrollArea):
            rolagem = rolagem.parentWidget()
        if rolagem is not None:
            rolagem.ensureWidgetVisible(caixa, 10, 60)
        base.esperar(1.0)
        base.conferir(caixa.isVisible() and not caixa.isChecked(), "Cortar: 'Margens iguais' à vista, desmarcada")
        _p(janela, "01-cortar-margens-iguais")
        base.clique(janela, caixa, QPoint(9, caixa.height() // 2))
        base.esperar(1.0)
        base.conferir(projeto.margens_iguais, "clique na caixinha: margens iguais do livro ligadas")
        base.conferir(__import__("core.automatico", fromlist=["MARGENS"]).MARGENS
                      in tela.paineis.automatico.estado.marcadas, "o Automático mostra 'Margens iguais'")
        _p(janela, "02-cortar-margens-iguais-marcada")
        base.clique(janela, caixa, QPoint(9, caixa.height() // 2))   # volta como estava
        base.esperar(1.0)
    _passo("cortar", cortar)

    def grade_dividir():
        # D-558: "dividir" na grade "Todas as páginas"
        tela.abrir_todas_as_paginas()
        base.esperar(2.0)
        tela.todas.comecar_a_escolher([3, 4])
        base.esperar(2.0)
        botao = tela.todas.botoes_da_escolha["dividir"]
        base.conferir(botao.isVisible() and botao.isEnabled(), "grade: 'dividir' aceso com 2 escolhidas")
        _p(janela, "03-grade-dividir")
        antes = len(projeto.paginas)
        base.clique(janela, botao)
        _esperar_ate(lambda: len(projeto.paginas) == antes + 2, 120)
        base.esperar(2.0)
        base.conferir(len(projeto.paginas) == antes + 2, f"dividir: {antes} -> {len(projeto.paginas)} páginas")
        _p(janela, "04-grade-depois-de-dividir")
        tela.todas.voltar.emit()
        base.esperar(1.0)
    _passo("grade", grade_dividir)

    def zoom_e_roda():
        # D-568 / D-570 / D-571
        tela.escolher_ferramenta("mao")
        tela.ir_para_pagina(6)
        _a_previa(tela, 6)
        base.clique(janela, tela.botao_ajustar_a_tela)
        base.conferir(tela.rotulo_do_zoom.text() == "100%", "100% = a página inteira (D-571)")
        _p(janela, "05-zoom-100-pagina-inteira")
        base.clique(janela, tela.botao_mais_zoom)
        base.clique(janela, tela.botao_mais_zoom)
        base.esperar(1.0)
        vista = tela.editor_selecao
        antes = vista.deslocamento.y()
        # a roda do mouse não chega a uma janela fora da tela (etapa 6): o MESMO caminho da
        # roda (TelaConferir._roda_na_pagina) com um evento de roda de verdade do Qt
        from PySide6.QtCore import QPoint, QPointF, Qt
        from PySide6.QtGui import QWheelEvent
        from PySide6.QtWidgets import QApplication
        for _ in range(3):
            centro = QPointF(vista.width() / 2, vista.height() / 2)
            QApplication.sendEvent(vista, QWheelEvent(centro, vista.mapToGlobal(centro), QPoint(0, 0),
                                                      QPoint(0, -120), Qt.NoButton, Qt.NoModifier,
                                                      Qt.NoScrollPhase, False))
        base.esperar(1.0)
        base.conferir(vista.deslocamento.y() < antes and tela.indice_pagina == 6,
                      "com zoom a roda anda pela página (D-568), a página continua a 7")
        _p(janela, "06-zoom-156-roda-andou-para-baixo")
        base.clique(janela, tela.botao_ajustar_a_tela)
        base.clique(janela, tela.botoes_mostrar[DUAS])
        base.esperar(3.0)
        base.clique(janela, tela.botao_mais_zoom)
        base.esperar(3.0)
        base.conferir(tela.rotulo_do_zoom.text() == "125%" and abs(tela.lado_a_lado.zoom - 1.25) < 1e-6,
                      "zoom no 'Duas lado a lado' (D-570)")
        _p(janela, "07-lado-a-lado-zoom-125")
        base.clique(janela, tela.botao_ajustar_a_tela)
        base.clique(janela, tela.botoes_mostrar[UMA])
        base.esperar(1.0)
    _passo("zoom", zoom_e_roda)

    def mover():
        # D-547: a página movida no lado a lado, na miniatura e nos cartões
        tela.escolher_ferramenta("mover")
        tela.ir_para_pagina(8)
        _a_previa(tela, 8)
        tela._mudar_tamanho_do_conteudo(60)
        base.esperar(2.0)
        _p(janela, "08-mover-60-por-cento")
        base.clique(janela, tela.botoes_mostrar[DUAS])
        base.esperar(4.0)
        base.conferir(8 in tela.tira._como_sai, "a miniatura da página 9 é a página movida")
        _p(janela, "09-lado-a-lado-com-a-pagina-movida")
        base.clique(janela, tela.botoes_mostrar[UMA])
        base.esperar(1.0)
    _passo("mover", mover)

    def marcar_e_desfazer():
        # P-129 / 1.3 / 1.9: o retângulo à mão aparece e o desfazer de baixo o tira
        from core.selecao import GRAVURA, MAO, RETANGULO, AUTOMATICO, Regiao
        tela.escolher_ferramenta("retangulo")
        tela.ir_para_pagina(10)
        _a_previa(tela, 10)
        tela.editor_selecao._acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO,
                                                pontos=[(0.05, 0.05), (0.95, 0.95)], origem=AUTOMATICO))
        tela.editor_selecao._acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO,
                                                pontos=[(0.3, 0.3), (0.7, 0.55)], origem=MAO))
        base.esperar(1.5)
        _p(janela, "10-retangulo-a-mao-dentro-da-area-da-maquina")
        base.clique(janela, tela.botao_desfazer_embaixo)
        base.esperar(1.5)
        base.conferir(len(projeto.paginas[10].selecao) == 1, "o desfazer de baixo tirou o retângulo à mão")
        _p(janela, "11-depois-do-desfazer-de-baixo")
        base.clique(janela, tela.botao_desfazer_embaixo)
        base.esperar(1.0)
    _passo("marcar", marcar_e_desfazer)

    def automatico():
        # D-559 (a escolha cortar/pintar à vista) e 5.3 (a caixinha da força sozinha acesa)
        from core import automatico as A
        from core.filtros import PRETO_E_BRANCO
        from ui.automatico import JanelaDoAutomatico
        estado = janela.estado_do_automatico
        estado.opcoes.update({"filtro_padrao": PRETO_E_BRANCO, "misto_so_as_letras": False})
        grande = janela.abrir_o_automatico(A.CORTAR)
        base.esperar(1.5)
        base.conferir(not grande.linhas["borda_preta_fazer"].isHidden(),
                      "Automático, Cortar: 'O que fica fora da página' à vista (D-559)")
        base.print_window(grande, PRINTS / f"{PREFIXO}-12-automatico-cortar.png", so_cliente=False)
        grande.mostrar_etapa(A.LIMPAR)
        base.esperar(1.0)
        base.conferir(grande.cx_forca_sozinha.isEnabled(), "a caixinha da força sozinha acesa (5.3)")
        base.print_window(grande, PRINTS / f"{PREFIXO}-13-automatico-limpar.png", so_cliente=False)
        janela._fechar_a_janela_do_automatico()
        base.esperar(1.0)
        assert JanelaDoAutomatico
    _passo("automatico", automatico)
    base.fechar(janela)

    # D-559: o Righetti (duas folhas, de lado), girado e o Automático só com "Endireitar"
    def righetti():
        import fitz
        origem = base.ACERVO / RIGHETTI
        destino = TRAB / "righetti-95-96.pdf"
        with fitz.open(str(origem)) as doc, fitz.open() as novo:
            novo.insert_pdf(doc, from_page=94, to_page=95)
            novo.save(str(destino))
        j2 = base.nova_janela(1280, 657)
        t2 = _livro(j2, destino)
        t2._acao_nas_escolhidas("girar_esquerda", [0, 1])
        t2.pilha_da_tela.setCurrentWidget(t2.trabalho)
        base.esperar(2.0)
        _a_previa(t2, 1)
        _p(j2, "14-righetti-girado-com-a-faixa-da-tampa")
        from core import automatico as A
        estado = j2.estado_do_automatico
        estado.marcadas = {A.DIVIDIR}
        estado.alcance = "livro"
        j2.rodar_o_automatico(perguntar=False)
        _esperar_ate(lambda: len(j2.projeto.paginas) == 4, 240)
        base.esperar(2.0)
        base.conferir(all(f.tampa_do_scanner and len(f.tampa_do_scanner) == 5 for f in j2.projeto.folhas),
                      "o Automático achou a tampa nas duas folhas (D-559)")
        t2.ir_para_pagina(3)
        _a_previa(t2, 3)
        base.esperar(2.0)
        _p(j2, "15-righetti-pelo-automatico-sem-a-faixa")
        base.fechar(j2)
    _passo("righetti", righetti)
    base.gravar_resultados(TRAB)


if __name__ == "__main__":
    main()
