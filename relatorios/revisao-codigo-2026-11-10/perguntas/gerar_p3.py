"""Pergunta 3 (achado M5): a linha arrastada no Dividir, e o "dividir" da grade "Todas as páginas".

Gradus Primus (CÓPIA, 70 folhas). Folhas 2 a 70 divididas pela grade, MENOS a folha 10 (fica
inteira: é a "página 18" enquanto não for dividida; depois de dividida, páginas 18 e 19).
  - Ferramenta Dividir, "Duas lado a lado", folha 10: a linha azul onde o motor cortaria (foto);
    a linha arrastada para a esquerda (o soltar do arrasto, D-609; foto).
  - Caminho A, botão "dividir esta" (foto da tela e PDF das páginas 18 e 19). Ctrl+Z (só o
    dividir; a linha arrastada continua).
  - Caminho B, grade "Todas as páginas": página 18 escolhida (foto), botão "dividir" (a tarefa
    de verdade, com a caixa do andamento). Foto da tela e PDF das páginas 18 e 19.
"""
from __future__ import annotations

import time

from comum import (abrir, ctrl_z, esperar, esperar_previa, gravar_estado, pdf_das_paginas,
                   saida)

from tests.test_decisoes_girar_pagina import app, janela, pasta  # noqa: F401

FOLHA = 9            # folha 10
ARRASTADA = 0.40     # onde a pessoa deixa a linha (fração da largura da folha)


def _no_dividir(tela, janela, nome: str) -> dict:
    from ui.tela_conferir import FERRAMENTA_DIVIDIR
    from ui.widgets.paginas_rolando import DUAS

    tela.escolher_ferramenta(FERRAMENTA_DIVIDIR)
    tela.definir_mostrar(DUAS)
    pagina = next(p.indice for p in tela.projeto.paginas if p.folha == FOLHA)
    tela.ir_para_pagina(pagina)
    esperar_previa(tela)
    t0 = time.time()
    while tela._linha_do_motor(FOLHA) is None and time.time() - t0 < 30:
        esperar(0.3)
    esperar(1.5)
    assert tela.indice_folha == FOLHA
    janela.grab().save(str(saida() / f"{nome}.png"))
    folha = tela.projeto.folhas[FOLHA]
    lida = tela._linha_do_motor(FOLHA)
    return {"dividida": folha.dividir, "posicao_corte": folha.posicao_corte,
            "linha_a_mao": getattr(folha, "linha_a_mao", None),
            "linha_do_motor": None if lida is None else round(lida[0].posicao, 4),
            "paginas_da_folha": [p.indice + 1 for p in tela.projeto.paginas if p.folha == FOLHA]}


def test_p3(janela):
    from ui.tela_conferir import ABA_CORTE

    s = saida()
    tela, projeto = abrir(janela)
    tela._dividir_escolhidas([f for f in range(1, len(projeto.folhas)) if f != FOLHA], esperar=True)
    assert not projeto.folhas[FOLHA].dividir
    estado: dict = {"motor": _no_dividir(tela, janela, "p3-linha-do-motor")}

    # a pessoa arrasta a linha azul da folha 10 (ainda inteira) para a esquerda
    tela.visualizadores[ABA_CORTE].corte_movido.emit(ARRASTADA)      # o soltar do arrasto
    esperar(1.0)
    assert tela._linha_arrastada(FOLHA), "a linha arrastada não ficou valendo"
    estado["antes"] = _no_dividir(tela, janela, "p3-antes")
    estado["historico_arrasto"] = janela.acoes.feitas[-1].descricao
    estado["pdf_antes"] = pdf_das_paginas(projeto, [17], s, "p3-antes", dpi=50)
    feitas = len(janela.acoes.feitas)

    # --- caminho A: "dividir esta" --------------------------------------------------------
    tela._dividir_esta()                                    # o botão "dividir esta"
    esperar(1.5)
    estado["historico_esta"] = janela.acoes.feitas[-1].descricao
    estado["depois_esta"] = _no_dividir(tela, janela, "p3-esta")
    estado["pdf_esta"] = pdf_das_paginas(projeto, [17, 18], s, "p3-esta", dpi=50)
    while len(janela.acoes.feitas) > feitas:
        ctrl_z(tela)
    assert not projeto.folhas[FOLHA].dividir and tela._linha_arrastada(FOLHA)
    estado["depois_do_ctrl_z"] = _no_dividir(tela, janela, "p3-depois-do-ctrl-z")

    # --- caminho B: grade "Todas as páginas", "dividir" ---------------------------------
    tela.abrir_todas_as_paginas()
    esperar(2.0)
    grade = tela.todas
    grade.botao_marcar_varias.setChecked(True)
    grade.marcar(17)                                        # a página 18 (a folha 10 inteira)
    esperar(2.0)
    janela.grab().save(str(s / "p3-grade-escolhida.png"))
    estado["grade_escolhidas"] = sorted(i + 1 for i in grade.escolhidas)
    grade.botoes_da_escolha["dividir"].click()              # o botão "dividir" da grade
    t0 = time.time()
    while not projeto.folhas[FOLHA].dividir and time.time() - t0 < 120:
        esperar(0.5)
    esperar(2.0)
    assert projeto.folhas[FOLHA].dividir, "a grade não dividiu a folha 10"
    estado["historico_grade"] = janela.acoes.feitas[-1].descricao
    janela.grab().save(str(s / "p3-grade-depois.png"))
    tela.pilha_da_tela.setCurrentWidget(tela.trabalho)
    estado["depois_grade"] = _no_dividir(tela, janela, "p3-grade")
    estado["pdf_grade"] = pdf_das_paginas(projeto, [17, 18], s, "p3-grade", dpi=50)
    gravar_estado("p3", estado)
    print({k: v for k, v in estado.items() if not k.startswith("pdf")})
