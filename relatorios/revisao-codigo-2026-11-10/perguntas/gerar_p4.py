"""Pergunta 4 (achado A1, caminho 7): o girar do painel e o girar da grade "Todas as páginas".

Gradus Primus (CÓPIA, 70 folhas), folhas 2 a 70 divididas pela grade (139 páginas).
  - ANTES: ferramenta Cortar as bordas, página 19 virada ¼ à direita ("só esta página"); as
    outras em pé.
  - Caminho do painel: página 18, "aplicar em: todas as páginas" + "¼ à direita" (foto da tela).
    Ctrl+Z.
  - Caminho da grade: "Todas as páginas", "marcar várias", "todas" (todas escolhidas, foto),
    "girar ¼ →".
Fotos: as páginas 17 a 20 como saem no PDF, antes e depois de cada caminho.
"""
from __future__ import annotations

from comum import (abrir, ctrl_z, esperar, esperar_previa, gravar_estado, pdf_das_paginas,
                   saida)

from tests.test_decisoes_girar_pagina import app, janela, pasta  # noqa: F401

PAGINAS = [16, 17, 18, 19]          # páginas 17, 18, 19 e 20
DA_VEZ, VIRADA = 17, 18             # página 18 (de onde se gira) e página 19 (já virada à mão)


def _giros(projeto) -> dict:
    return {str(i + 1): {"giro_da_pagina": projeto.paginas[i].giro_da_pagina,
                         "rotacao_da_folha": projeto.folhas[projeto.paginas[i].folha].rotacao}
            for i in PAGINAS}


def test_p4(janela):
    from core import girar
    from ui.tela_conferir import FERRAMENTA_CORTAR
    from ui.widgets.paginas_rolando import UMA

    s = saida()
    tela, projeto = abrir(janela)
    tela._dividir_escolhidas(list(range(1, len(projeto.folhas))), esperar=True)
    assert projeto.paginas[DA_VEZ].folha == 9 and projeto.paginas[VIRADA].folha == 9
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    tela.definir_mostrar(UMA)
    # ANTES: a página 19 virada ¼ à direita, só ela
    tela.ir_para_pagina(VIRADA)
    esperar_previa(tela)
    tela.barra_girar.definir_alcance(girar.ALCANCE_ESTA)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    esperar(1.0)
    estado: dict = {"antes": _giros(projeto)}
    estado["pdf_antes"] = pdf_das_paginas(projeto, PAGINAS, s, "p4-antes", dpi=40)
    feitas = len(janela.acoes.feitas)

    # --- caminho do painel ----------------------------------------------------------------
    tela.ir_para_pagina(DA_VEZ)
    esperar_previa(tela)
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    estado["lista_do_painel"] = tela.barra_girar.combo_alcance.currentText()
    estado["quadro_do_painel"] = tela.barra_girar.rotulo.text()
    janela.grab().save(str(s / "p4-painel-antes-do-clique.png"))
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    esperar_previa(tela)
    esperar(2.0)
    estado["historico_painel"] = janela.acoes.feitas[-1].descricao
    estado["depois_painel"] = _giros(projeto)
    estado["pdf_painel"] = pdf_das_paginas(projeto, PAGINAS, s, "p4-painel", dpi=40)
    while len(janela.acoes.feitas) > feitas:
        ctrl_z(tela)
    assert _giros(projeto) == estado["antes"], "o Ctrl+Z não devolveu o antes"
    tela.barra_girar.definir_alcance(girar.ALCANCE_ESTA)

    # --- caminho da grade "Todas as páginas" --------------------------------------------
    tela.ir_para_pagina(DA_VEZ)
    esperar_previa(tela)
    tela.abrir_todas_as_paginas()
    esperar(2.0)
    grade = tela.todas
    grade.botao_marcar_varias.setChecked(True)
    grade.botoes_da_escolha["todas"].click()                 # todas escolhidas
    esperar(3.0)
    estado["grade_escolhidas"] = len(grade.escolhidas)
    janela.grab().save(str(s / "p4-grade-escolhidas.png"))
    grade.botoes_da_escolha["girar_direita"].click()         # "girar ¼ →"
    esperar(4.0)
    estado["historico_grade"] = janela.acoes.feitas[-1].descricao
    estado["depois_grade"] = _giros(projeto)
    janela.grab().save(str(s / "p4-grade-depois.png"))
    estado["pdf_grade"] = pdf_das_paginas(projeto, PAGINAS, s, "p4-grade", dpi=40)
    gravar_estado("p4", estado)
    print({k: v for k, v in estado.items() if not k.startswith("pdf")})
