"""Pergunta 1 (achado A3): o "usar em todas" do Cortar e o do Marcar, na mesma página mexida à mão.

Gradus Primus (CÓPIA, 70 folhas), folhas 2 a 70 divididas pela grade (139 páginas).
  - Página 15 (a gravura da águia), mexida à mão nas duas ferramentas: no Cortar, o corte puxado
    só em volta do título e da gravura; no Marcar (Retângulo, "gravura ou foto"), um retângulo em
    volta da águia.
  - Página 17 (onde se aperta o "usar em todas"), também mexida à mão: no Cortar, um corte justo
    em volta do conteúdo; no Marcar ("letra e traço"), um retângulo no texto de baixo.
  - Páginas 16 e 18: nada feito.
Caminho do Cortar: página 17, "usar em todas" → a janela "Em quais páginas?" (foto) → "Aplicar"
com a escolha de fábrica. Ctrl+Z. Caminho do Marcar: página 17, "usar em todas". Ctrl+Z.
Conferência por números (sem foto) do Filtro, do Endireitar e do Girar, na mesma página 15.

Fotos: a página na tela do Cortar (o retângulo verde é o corte) e na tela do Marcar (as cores
são as áreas marcadas), páginas 15 a 18, antes e depois de cada caminho.
"""
from __future__ import annotations

from comum import (abrir, ctrl_z, esperar, esperar_editor, esperar_previa, gravar_estado,
                   saida)

from tests.test_decisoes_girar_pagina import app, janela, pasta  # noqa: F401

PAGINAS = [14, 15, 16, 17]             # páginas 15, 16, 17 e 18
MEXIDA, DA_VEZ = 14, 16                # página 15 e página 17
CORTE_15 = (0.04, 0.10, 0.96, 0.50)    # título + gravura da águia
CORTE_17 = (0.06, 0.12, 0.94, 0.93)    # justo em volta do conteúdo
GRAVURA_15 = ((0.06, 0.22), (0.76, 0.47))   # a águia
LETRA_17 = ((0.03, 0.56), (0.97, 0.93))     # o texto de baixo


def _fotos(tela, janela, nome: str) -> None:
    """As páginas 15 a 18 no Cortar e no Marcar (o widget da página, sem os painéis)."""
    from ui.tela_conferir import ABA_BORDAS, FERRAMENTA_CORTAR

    s = saida()
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    for i in PAGINAS:
        tela.ir_para_pagina(i)
        esperar_previa(tela)
        tela.visualizadores[ABA_BORDAS].grab().save(str(s / f"{nome}-cortar-{i + 1}.png"))
    tela.escolher_ferramenta("retangulo")
    for i in PAGINAS:
        tela.ir_para_pagina(i)
        esperar_editor(tela)
        tela.editor_selecao.grab().save(str(s / f"{nome}-marcar-{i + 1}.png"))


def _estado(projeto) -> dict:
    return {str(i + 1): {"recorte": projeto.paginas[i].recorte,
                         "marcacao": [(r.tipo, r.origem, [tuple(round(v, 3) for v in p) for p in r.pontos])
                                      for r in projeto.paginas[i].obter_selecao().regioes],
                         "filtro": projeto.paginas[i].filtro,
                         "angulo_manual": projeto.paginas[i].angulo_manual,
                         "giro_da_pagina": projeto.paginas[i].giro_da_pagina}
            for i in PAGINAS}


def _arrastar(editor, de, ate) -> None:
    """Arrasta o mouse no editor, como a pessoa (Retângulo)."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    p0, p1 = editor._para_tela(*de), editor._para_tela(*ate)
    QTest.mousePress(editor, Qt.LeftButton, Qt.NoModifier, p0)
    for k in range(1, 6):
        QTest.mouseMove(editor, p0 + (p1 - p0) * (k / 5))
    QTest.mouseRelease(editor, Qt.LeftButton, Qt.NoModifier, p1)
    esperar(0.5)


def test_p1(janela):
    from core import girar
    from core.filtros import MELHORAR, PRETO_E_BRANCO
    from core.selecao import GRAVURA, LETRA
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from ui.tela_conferir import ABA_BORDAS, FERRAMENTA_CORTAR, FERRAMENTA_ENDIREITAR

    s = saida()
    tela, projeto = abrir(janela)
    tela._dividir_escolhidas(list(range(1, len(projeto.folhas))), esperar=True)
    assert (projeto.paginas[MEXIDA].folha, projeto.paginas[MEXIDA].metade) == (7, "direita")
    estado: dict = {}

    # --- o que se faz à mão, antes -------------------------------------------------------
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    for i, corte in ((MEXIDA, CORTE_15), (DA_VEZ, CORTE_17)):
        tela.ir_para_pagina(i)
        esperar_previa(tela)
        tela.visualizadores[ABA_BORDAS].recorte_movido.emit(corte)     # o soltar do arrasto
        esperar(0.5)
    tela.escolher_ferramenta("retangulo")
    for i, tipo, (de, ate) in ((MEXIDA, GRAVURA, GRAVURA_15), (DA_VEZ, LETRA, LETRA_17)):
        tela.ir_para_pagina(i)
        esperar_editor(tela)
        tela._escolher_tipo_de_marcacao(tipo)
        _arrastar(tela.editor_selecao, de, ate)
    estado["antes"] = _estado(projeto)
    estado["mexida_a_mao_15"] = list(getattr(projeto.paginas[MEXIDA], "mexida_a_mao", []) or [])
    _fotos(tela, janela, "p1-antes")
    pdf_antes = len(janela.acoes.feitas)

    # --- caminho do Cortar: "usar em todas" na página 17 ---------------------------------
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    tela.ir_para_pagina(DA_VEZ)
    esperar_previa(tela)
    janela.grab().save(str(s / "p1-tela-cortar-17.png"))
    vista: dict = {}

    def foto_da_janela_e_aplicar():
        caixa = QApplication.activeModalWidget()
        assert caixa is not None, "a janela 'Em quais páginas?' não abriu"
        caixa.resize(420, 560)
        caixa.lista.scrollToItem(caixa.lista.item(MEXIDA))
        esperar(0.3)
        caixa.grab().save(str(s / "p1-janela-em-quais-paginas.png"))
        vista["marcadas"] = [i + 1 for i in caixa.escolhidas()]
        vista["textos"] = [caixa.lista.item(i).text() for i in range(12, 18)]
        caixa.accept()                                   # "Aplicar", com a escolha de fábrica

    QTimer.singleShot(800, foto_da_janela_e_aplicar)
    tela._recorte_em_todas()                             # o botão "usar em todas" do Cortar
    esperar(1.0)
    estado["janela_do_cortar"] = {"marcadas_de_fabrica_ate_20": [n for n in vista["marcadas"] if n <= 20],
                                  "linhas_13_a_18": vista["textos"]}
    estado["depois_cortar"] = _estado(projeto)
    estado["historico_cortar"] = janela.acoes.feitas[-1].descricao
    _fotos(tela, janela, "p1-cortar")
    ctrl_z(tela)
    assert _estado(projeto) == estado["antes"], "o Ctrl+Z não devolveu o antes"

    # --- caminho do Marcar: "usar em todas" na página 17 ---------------------------------
    tela.escolher_ferramenta("retangulo")
    tela.ir_para_pagina(DA_VEZ)
    esperar_editor(tela)
    janela.grab().save(str(s / "p1-tela-marcar-17.png"))
    tela._marcacao_em_todas()                            # o botão "usar em todas" do Marcar
    esperar(1.0)
    estado["depois_marcar"] = _estado(projeto)
    estado["historico_marcar"] = janela.acoes.feitas[-1].descricao
    _fotos(tela, janela, "p1-marcar")
    ctrl_z(tela)
    assert _estado(projeto) == estado["antes"], "o Ctrl+Z não devolveu o antes"
    assert len(janela.acoes.feitas) == pdf_antes

    # --- conferência por números: Filtro, Endireitar e Girar ----------------------------
    numeros: dict = {}
    # Filtro: página 15 em Melhorar à mão; página 17 em Preto e branco, "todas"
    tela.ir_para_pagina(MEXIDA)
    esperar(0.5)
    tela._escolher_filtro(MELHORAR)
    tela.ir_para_pagina(DA_VEZ)
    esperar(0.5)
    tela._escolher_filtro(PRETO_E_BRANCO)
    antes = projeto.paginas[MEXIDA].filtro
    tela._filtro_em_todas()
    numeros["filtro"] = {"pagina_15_antes": antes, "pagina_15_depois": projeto.paginas[MEXIDA].filtro,
                         "historico": janela.acoes.feitas[-1].descricao}
    for _ in range(3):
        ctrl_z(tela)
    # Endireitar: página 15 com +2,00 graus à mão; página 17 com -1,00, "todas as páginas"
    tela.escolher_ferramenta(FERRAMENTA_ENDIREITAR)
    tela.ir_para_pagina(MEXIDA)
    esperar_previa(tela)
    tela._gravar_angulo(MEXIDA, 2.0)
    antes = projeto.paginas[MEXIDA].angulo_manual
    tela.ir_para_pagina(DA_VEZ)
    esperar_previa(tela)
    combo = tela.combo_alcance_do_angulo
    combo.setCurrentIndex(combo.findData(girar.ALCANCE_TODAS))
    tela._gravar_angulo(DA_VEZ, -1.0)
    numeros["endireitar"] = {"pagina_15_antes": antes,
                             "pagina_15_depois": projeto.paginas[MEXIDA].angulo_manual,
                             "lista": combo.currentText(),
                             "historico": janela.acoes.feitas[-1].descricao}
    for _ in range(2):
        ctrl_z(tela)
    combo.setCurrentIndex(combo.findData(girar.ALCANCE_ESTA))
    # Girar: página 15 virada ¼ à direita ("só esta página"); página 17, "todas as páginas" + ¼ à esquerda
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    tela.ir_para_pagina(MEXIDA)
    esperar_previa(tela)
    tela.barra_girar.definir_alcance(girar.ALCANCE_ESTA)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    esperar(0.5)
    antes = projeto.paginas[MEXIDA].giro_da_pagina
    tela.ir_para_pagina(DA_VEZ)
    esperar_previa(tela)
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
    esperar(0.5)
    numeros["girar"] = {"pagina_15_antes": antes, "pagina_15_depois": projeto.paginas[MEXIDA].giro_da_pagina,
                        "pagina_17_depois": projeto.paginas[DA_VEZ].giro_da_pagina,
                        "pagina_16_depois": projeto.paginas[15].giro_da_pagina,
                        "lista": tela.barra_girar.combo_alcance.currentText(),
                        "historico": janela.acoes.feitas[-1].descricao}
    estado["outras_ferramentas"] = numeros
    gravar_estado("p1", estado)
    print(numeros)
