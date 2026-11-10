"""Pergunta 2 (achado M9): "Letra clara em fundo escuro" no "todas" do painel Filtro e no Automático.

Siebmacher, Schön Neues Modell Buch (CÓPIA). As páginas 11, 13, 15 e 17 são riscos de bordado com
o desenho CLARO em fundo ESCURO.
  - ANTES: o Automático com só "Limpar a folha" e Preto e branco, caixinha "Letra clara em fundo
    escuro" DESMARCADA, no livro todo (assim os dois caminhos partem do mesmo livro e a única
    diferença entre eles é a caixinha).
  - Caminho do painel Filtro: ferramenta Zoom, painel "Filtro da página" aberto, página 13 (já
    em Preto e branco): caixinha "Letra clara em fundo escuro" marcada + "Aplicar em: todas".
  - Ctrl+Z até o começo.
  - Caminho do Automático: a janela do Automático com o mesmo pedido do ANTES, agora com
    "Letra clara em fundo escuro" marcada (foto da janela) → "Rodar" no livro todo.
Fotos: as páginas 11, 13, 15 e 17 como saem no PDF; o painel Filtro na página 13 e na 15.
"""
from __future__ import annotations

from comum import abrir, ctrl_z, esperar, esperar_previa, gravar_estado, pdf_das_paginas, saida

from tests.test_decisoes_girar_pagina import app, janela, pasta  # noqa: F401

PAGINAS = [10, 12, 14, 16]          # páginas 11, 13, 15 e 17
DA_VEZ = 12                         # página 13


def _estado(projeto) -> dict:
    return {str(i + 1): {"filtro": projeto.paginas[i].filtro,
                         "claro_no_escuro": bool(getattr(projeto.paginas[i], "claro_no_escuro", False))}
            for i in PAGINAS}


def _onde(widget, janela) -> list[int]:
    """O retângulo do widget na foto da janela (para o círculo vermelho)."""
    from PySide6.QtCore import QPoint

    p = widget.mapTo(janela, QPoint(0, 0))
    return [p.x(), p.y(), p.x() + widget.width(), p.y() + widget.height()]


def _foto_do_painel(tela, janela, indice: int, nome: str) -> list[int]:
    """Foto da janela com a parte "Mais ajustes" do painel Filtro aberta (o clique no cabeçalho
    dela), para a caixinha "Letra clara em fundo escuro" aparecer. Devolve onde ela está."""
    from ui.widgets.paineis import ParteQueAbre

    tela.ir_para_pagina(indice)
    esperar_previa(tela)
    for parte in tela.findChildren(ParteQueAbre):
        if parte.nome in ("Só as letras", "Ajuste") and parte.aberta:
            parte.alternar()
        if parte.nome == "Mais ajustes" and not parte.aberta:
            parte.alternar()
    esperar(2.0)
    janela.grab().save(str(saida() / nome))
    return _onde(tela.caixa_claro_no_escuro, janela)


def test_p2(janela):
    from core import automatico as A
    from core.filtros import PRETO_E_BRANCO
    from ui.tela_conferir import PAINEL_FILTRO

    s = saida()
    tela, projeto = abrir(janela)
    assert not projeto.passou_pelo_automatico
    # ANTES: o Automático (só "Limpar a folha", Preto e branco, caixinha desmarcada), livro todo
    auto = janela.estado_do_automatico
    auto.marcadas = {A.LIMPAR}
    auto.definir_opcao("filtro_padrao", PRETO_E_BRANCO)
    auto.definir_opcao("claro_no_escuro", False)
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    esperar(2.0)
    tela.escolher_ferramenta("zoom")
    tela.paineis.abrir(PAINEL_FILTRO)
    estado: dict = {"antes": _estado(projeto)}
    estado["pdf_antes"] = pdf_das_paginas(projeto, PAGINAS, s, "p2-antes", dpi=40)
    feitas = len(janela.acoes.feitas)

    # --- caminho do painel Filtro --------------------------------------------------------
    tela.ir_para_pagina(DA_VEZ)
    esperar_previa(tela)
    assert projeto.paginas[DA_VEZ].filtro == PRETO_E_BRANCO
    tela.caixa_claro_no_escuro.setChecked(True)                             # o clique na caixinha
    esperar(0.5)
    assert projeto.paginas[DA_VEZ].claro_no_escuro
    tela._filtro_em_todas()                                                 # "Aplicar em: todas"
    esperar(1.0)
    estado["historico_painel"] = janela.acoes.feitas[-1].descricao
    estado["depois_painel"] = _estado(projeto)
    estado["caixinha_na_tela"] = {}
    for i in (DA_VEZ, 14):
        onde = _foto_do_painel(tela, janela, i, f"p2-painel-pagina-{i + 1}.png")
        estado["caixinha_na_tela"][str(i + 1)] = tela.caixa_claro_no_escuro.isChecked()
        estado.setdefault("onde_a_caixinha", {})[f"painel-{i + 1}"] = onde
    estado["pdf_painel"] = pdf_das_paginas(projeto, PAGINAS, s, "p2-painel", dpi=40)
    while len(janela.acoes.feitas) > feitas:
        ctrl_z(tela)
    assert _estado(projeto) == estado["antes"], "o Ctrl+Z não devolveu o antes"

    # --- caminho do Automático -----------------------------------------------------------
    tela.ir_para_pagina(DA_VEZ)
    esperar_previa(tela)
    janela_auto = janela.abrir_o_automatico(etapa=A.LIMPAR)
    esperar(1.0)
    auto.marcadas = {A.LIMPAR}
    auto.definir_opcao("filtro_padrao", PRETO_E_BRANCO)
    auto.definir_opcao("claro_no_escuro", True)
    auto.mudou.emit()
    esperar(1.5)
    janela_auto.resize(1300, 820)
    esperar(0.5)
    from PySide6.QtWidgets import QCheckBox, QScrollArea
    caixa_auto = next(c for c in janela_auto.findChildren(QCheckBox) if "Letra clara" in c.text())
    for rolagem in janela_auto.findChildren(QScrollArea):     # rolar até a caixinha
        if rolagem.isAncestorOf(caixa_auto):
            rolagem.ensureWidgetVisible(caixa_auto, 50, 120)
    esperar(1.0)
    janela_auto.grab().save(str(s / "p2-janela-do-automatico.png"))
    estado.setdefault("onde_a_caixinha", {})["janela-do-automatico"] = _onde(caixa_auto, janela_auto)
    caixas = {c.text(): c.isChecked() for c in janela_auto.findChildren(QCheckBox)
              if "Letra clara" in c.text()}
    estado["janela_do_automatico_caixinha"] = caixas
    estado["pedido"] = {"etapas": auto.etapas_marcadas(), "opcoes": auto.opcoes,
                        "paginas": auto.paginas()}
    janela._fechar_a_janela_do_automatico()          # o "Rodar" fecha a janela e roda
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    esperar(2.0)
    estado["historico_automatico"] = janela.acoes.feitas[-1].descricao
    estado["depois_automatico"] = _estado(projeto)
    estado["caixinha_na_tela_automatico"] = {}
    tela.escolher_ferramenta("zoom")
    tela.paineis.abrir(PAINEL_FILTRO)
    for i in (14,):
        onde = _foto_do_painel(tela, janela, i, f"p2-automatico-painel-pagina-{i + 1}.png")
        estado["caixinha_na_tela_automatico"][str(i + 1)] = tela.caixa_claro_no_escuro.isChecked()
        estado.setdefault("onde_a_caixinha", {})[f"automatico-{i + 1}"] = onde
    estado["pdf_automatico"] = pdf_das_paginas(projeto, PAGINAS, s, "p2-automatico", dpi=40)
    gravar_estado("p2", estado)
    print(estado["depois_painel"], estado["depois_automatico"], caixas)
