"""Provas das perguntas 3 e 4 do girar-capa, no Gradus Primus (CÓPIA), SEM janela na tela.

Roda como um teste do pytest, com o conftest dos testes (offscreen: o Qt desenha na memória e
nada aparece na tela; LOCALAPPDATA de mentira), no código que se quer medir:

    cd <código: girar-capa (com o conserto) ou provas-girar-antigo (6904a634, sem o conserto)>
    set QT_QPA_PLATFORM=offscreen
    set QT_SCALE_FACTOR=2                 (as fotos saem com o dobro de pontos)
    set QT_QPA_FONTDIR=C:\\Windows\\Fonts
    set PROVAS_PDF=<cópia do Gradus>      (nunca o original)
    set PROVAS_SAIDA=<pasta das fotos cruas>
    set PROVAS_NOME=antigo | novo
    python -m pytest -p tests.conftest <este arquivo> -q -s -k q4    (ou -k q3)

Pergunta 4 (o teste antigo do "daqui em diante"): folhas 2 a 70 divididas, MENOS a folha 4
("não dividir esta": fica inteira, é a página 6). Ferramenta Cortar as bordas, página 3,
"daqui em diante" + ¼ à direita. Fotos: as miniaturas das páginas 1 a 8 e as páginas 1 a 8 do
PDF, antes e depois do clique.

Pergunta 3 (o Dividir com "Duas lado a lado"): folhas 2 a 70 divididas (a capa inteira).
Ferramenta Dividir, "Duas lado a lado", folha 10 (páginas 18 e 19), "todas as folhas" + ¼ à
direita (o jeito de hoje, "Fica como está"). Ctrl+Z. Depois, a simulação do "Página por página
também" pelo caminho que já existe (D-636): ferramenta Cortar as bordas, página 18, "todas as
páginas" + ¼ à direita; e a tela do Dividir ("Duas lado a lado") depois disso.
"""
from __future__ import annotations

import copy
import json
import os
import time
from pathlib import Path

import pytest

from tests.test_decisoes_girar_pagina import app, janela, pasta  # noqa: F401

PAGINAS_Q4 = list(range(8))                  # páginas 1 a 8
PAGINAS_Q3 = [0, 17, 18, 19, 20]             # páginas 1, 18, 19, 20 e 21
FOLHA_Q3 = 9                                 # folha 10 do scan: páginas 18 e 19


def _esperar(segundos: float) -> None:
    from PySide6.QtWidgets import QApplication

    fim = time.time() + segundos
    while time.time() < fim:
        QApplication.processEvents()
        time.sleep(0.05)


def _esperar_previa(tela, limite: float = 60.0) -> None:
    _esperar(0.5)
    t0 = time.time()
    while time.time() - t0 < limite:
        vis = getattr(tela, "visualizadores", {}).get(tela.aba_atual) or tela.area_imagem.currentWidget()
        if getattr(vis, "_pixmap", 1) is not None and not getattr(vis, "carregando", False):
            break
        _esperar(0.2)
    _esperar(1.5)


def _esperar_miniaturas(tela, folhas, limite: float = 90.0) -> None:
    t0 = time.time()
    while time.time() - t0 < limite:
        if all(f in tela.tira._cruas for f in folhas):
            break
        _esperar(0.3)
    _esperar(1.0)


def _ctrl(tela, tecla) -> None:
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent

    assert tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, tecla, Qt.ControlModifier))


def _pdf(projeto, paginas, saida: Path, nome: str) -> list[dict]:
    """O PDF que sai (core/pipeline.processar), só com `paginas` (as outras tiradas numa CÓPIA
    do projeto); cada página vira um PNG."""
    import fitz

    from core import pipeline

    copia = copy.deepcopy(projeto)
    for pg in copia.paginas:
        if pg.indice not in paginas:
            pg.apagada = True
    copia.caminho_saida = str(saida / f"_{nome}.pdf")
    caminho = pipeline.processar(copia)
    lista = []
    with fitz.open(caminho) as doc:
        for n, pagina in enumerate(doc):
            png = saida / f"pdf-{nome}-{n + 1}.png"
            pagina.get_pixmap(dpi=60).save(str(png))
            lista.append({"png": png.name, "pt": [round(pagina.rect.width), round(pagina.rect.height)]})
    Path(caminho).unlink(missing_ok=True)
    return lista


def _miniaturas(tela, indices, saida: Path, nome: str) -> None:
    """Foto de cada miniatura da tira (o quadrinho do programa, como ele desenha) e da tira toda."""
    for i in indices:
        tela.tira._miniaturas[i].grab().save(str(saida / f"mini-{nome}-{i + 1}.png"))
    tela.tira.grab().save(str(saida / f"tira-{nome}.png"))


def _estado(projeto, tela, janela) -> dict:
    return {"rotacoes": [f.rotacao for f in projeto.folhas][:12],
            "giros": [p.giro_da_pagina for p in projeto.paginas][:22],
            "folhas_giradas": sum(1 for f in projeto.folhas if f.rotacao),
            "paginas_giradas": sum(1 for p in projeto.paginas if p.giro_da_pagina),
            "quadro": tela.barra_girar.rotulo.text(),
            "lista": tela.barra_girar.combo_alcance.currentText(),
            "historico": janela.acoes.feitas[-1].descricao if janela.acoes.feitas else ""}


def _abrir(janela):
    pdf = Path(os.environ["PROVAS_PDF"])
    janela.resize(1400, 820)
    janela.show()                                   # offscreen: desenhado só na memória
    janela.abrir_livro(str(pdf))
    _esperar(2.0)
    return janela.tela_conferir, janela.projeto


def test_q4_daqui_em_diante_com_folha_inteira(janela):
    from core import girar
    from ui.tela_conferir import FERRAMENTA_CORTAR

    saida = Path(os.environ["PROVAS_SAIDA"])
    nome = os.environ.get("PROVAS_NOME", "x")
    saida.mkdir(parents=True, exist_ok=True)
    tela, projeto = _abrir(janela)
    # folhas 2 a 70 divididas, menos a folha 4 (índice 3): "não dividir esta"
    tela._dividir_escolhidas([i for i in range(1, len(projeto.folhas)) if i != 3], esperar=True)
    assert [(p.folha, p.metade) for p in projeto.paginas[:8]] == [
        (0, "inteira"), (1, "esquerda"), (1, "direita"), (2, "esquerda"), (2, "direita"),
        (3, "inteira"), (4, "esquerda"), (4, "direita")], [(p.folha, p.metade) for p in projeto.paginas[:8]]
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    tela.ir_para_pagina(2)                          # página 3
    _esperar_previa(tela)
    _esperar_miniaturas(tela, range(0, 5))
    estado = {"codigo": nome, "antes": _estado(projeto, tela, janela)}
    _miniaturas(tela, PAGINAS_Q4, saida, f"q4-{nome}-antes")
    janela.grab().save(str(saida / f"tela-q4-{nome}-antes.png"))
    estado["pdf-antes"] = _pdf(projeto, PAGINAS_Q4, saida, f"q4-{nome}-antes")

    tela.barra_girar.definir_alcance(girar.ALCANCE_DAQUI)
    assert tela.barra_girar.combo_alcance.currentText() == "daqui em diante"
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    _esperar_previa(tela)
    _esperar(3.0)
    estado["depois"] = _estado(projeto, tela, janela)
    _miniaturas(tela, PAGINAS_Q4, saida, f"q4-{nome}-depois")
    janela.grab().save(str(saida / f"tela-q4-{nome}-depois.png"))
    estado["pdf-depois"] = _pdf(projeto, PAGINAS_Q4, saida, f"q4-{nome}-depois")
    (saida / f"estado-q4-{nome}.json").write_text(json.dumps(estado, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")


def test_q3_dividir_duas_lado_a_lado(janela):
    from PySide6.QtCore import Qt

    from core import girar
    from ui.tela_conferir import FERRAMENTA_CORTAR, FERRAMENTA_DIVIDIR
    from ui.widgets.paginas_rolando import DUAS, UMA

    saida = Path(os.environ["PROVAS_SAIDA"])
    nome = os.environ.get("PROVAS_NOME", "x")
    saida.mkdir(parents=True, exist_ok=True)
    tela, projeto = _abrir(janela)
    tela._dividir_escolhidas(list(range(1, len(projeto.folhas))), esperar=True)
    assert projeto.paginas[17].folha == FOLHA_Q3 and projeto.paginas[18].folha == FOLHA_Q3
    estado: dict = {"codigo": nome}

    def no_dividir(foto: str) -> None:
        tela.escolher_ferramenta(FERRAMENTA_DIVIDIR)
        tela.definir_mostrar(DUAS)
        tela.ir_para_pagina(17)
        _esperar_previa(tela)
        _esperar_miniaturas(tela, [0, FOLHA_Q3, FOLHA_Q3 + 1])
        assert tela.indice_folha == FOLHA_Q3
        estado[foto] = _estado(projeto, tela, janela)
        estado[foto]["itens_da_lista"] = [tela.barra_girar.combo_alcance.itemText(i)
                                          for i in range(tela.barra_girar.combo_alcance.count())]
        janela.grab().save(str(saida / f"tela-{foto}.png"))
        tela.tira.grab().save(str(saida / f"tira-{foto}.png"))

    def no_cortar(foto: str) -> None:
        tela.escolher_ferramenta(FERRAMENTA_CORTAR)
        tela.definir_mostrar(UMA)
        tela.ir_para_pagina(17)
        _esperar_previa(tela)
        _esperar_miniaturas(tela, [0, FOLHA_Q3, FOLHA_Q3 + 1])
        estado[foto] = _estado(projeto, tela, janela)
        _miniaturas(tela, PAGINAS_Q3, saida, foto)
        janela.grab().save(str(saida / f"tela-{foto}.png"))
        estado[f"pdf-{foto}"] = _pdf(projeto, PAGINAS_Q3, saida, foto)

    # ANTES do clique
    no_dividir("q3-antes-dividir")
    no_cortar("q3-antes-paginas")

    # opção "Fica como está": o jeito de hoje, no Dividir com "Duas lado a lado"
    no_dividir("q3-fica-dividir-antes-do-clique")
    assert tela._pagina_que_gira_sozinha() is None
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    estado["fica-lista"] = tela.barra_girar.combo_alcance.currentText()
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    _esperar_previa(tela)
    _esperar(3.0)
    estado["fica-clique"] = _estado(projeto, tela, janela)
    janela.grab().save(str(saida / "tela-q3-fica-dividir.png"))
    tela.tira.grab().save(str(saida / "tira-q3-fica-dividir.png"))
    no_cortar("q3-fica-paginas")
    _ctrl(tela, Qt.Key_Z)
    estado["fica-depois-do-ctrl-z"] = _estado(projeto, tela, janela)
    assert estado["fica-depois-do-ctrl-z"]["folhas_giradas"] == 0
    assert estado["fica-depois-do-ctrl-z"]["paginas_giradas"] == 0

    # opção "Página por página também": SIMULAÇÃO pelo caminho que já gira página por página
    # (D-636): Cortar as bordas, página 18, "todas as páginas" + ¼ à direita
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    tela.definir_mostrar(UMA)
    tela.ir_para_pagina(17)
    _esperar_previa(tela)
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    estado["pagina-lista"] = tela.barra_girar.combo_alcance.currentText()
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    _esperar_previa(tela)
    _esperar(3.0)
    estado["pagina-clique"] = _estado(projeto, tela, janela)
    no_cortar("q3-pagina-paginas")
    no_dividir("q3-pagina-dividir")

    # para anotar: o Dividir com "Uma página" já gira página por página (D-601/D-618)
    tela.escolher_ferramenta(FERRAMENTA_DIVIDIR)
    tela.definir_mostrar(UMA)
    tela.ir_para_pagina(17)
    _esperar_previa(tela)
    estado["dividir-uma-pagina"] = {
        "quadro": tela.barra_girar.rotulo.text(),
        "itens_da_lista": [tela.barra_girar.combo_alcance.itemText(i)
                           for i in range(tela.barra_girar.combo_alcance.count())],
        "gira_so_a_pagina": tela._pagina_que_gira_sozinha()}
    (saida / f"estado-q3-{nome}.json").write_text(json.dumps(estado, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")
