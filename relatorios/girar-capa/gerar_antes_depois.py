"""Antes/depois da D-638 e da D-640 no Gradus Primus, SEM janela na tela (relatorios/girar-capa).

Roda como um teste do pytest, com o conftest dos testes (offscreen: o Qt desenha na memória e nada
aparece na tela; caixas modais com vigia; LOCALAPPDATA de mentira), no código que se quer medir:

    cd <código: a cópia girar-capa, ou a extração do código de antes>
    set GIRAR_CAPA_PDF=<cópia do Gradus>   (nunca o original)
    set GIRAR_CAPA_SAIDA=<pasta das imagens>
    set GIRAR_CAPA_NOME=antes | depois
    set QT_QPA_FONTDIR=C:\Windows\Fonts   (sem isto, as letras da foto da janela saem como quadradinhos)
    python -m pytest -p tests.conftest <este arquivo> -q -s

O caminho (o mesmo do Kaique, pelos mesmos métodos que os botões chamam): abrir o livro (ajustes
de fábrica do livro novo), dividir as folhas 2 a 70 pela conta do "dividir" (a lombada pelo jeito
do ScanTailor; a folha 1, capa e contracapa abertas, fica inteira), ferramenta Cortar as bordas.
Situação 1: na página 1 (a capa inteira), "todas as folhas" + "¼ à esquerda" do Propriedades.
Situação 2: na página 14 (folha dividida), "todas as páginas" + "¼ à esquerda".
Depois de cada uma: o PDF que sai (só as páginas 1, 2, 3, 14 e 15, numa CÓPIA do projeto), uma
foto da janela (desenhada na memória) e o Ctrl+Z. Grava PNGs e um estado.json na pasta de saída.
"""
from __future__ import annotations

import copy
import json
import os
import time
from pathlib import Path

import pytest

from tests.test_decisoes_girar_pagina import app, janela, pasta  # noqa: F401

PAGINAS = [0, 1, 2, 13, 14]          # páginas 1, 2, 3, 14 e 15


def _esperar(segundos: float) -> None:
    from PySide6.QtWidgets import QApplication

    fim = time.time() + segundos
    while time.time() < fim:
        QApplication.processEvents()
        time.sleep(0.05)


def _esperar_previa(tela, limite: float = 60.0) -> None:
    """Espera a prévia da ferramenta da vez chegar (como o piloto do girar-pagina)."""
    _esperar(0.5)
    t0 = time.time()
    while time.time() - t0 < limite:
        vis = getattr(tela, "visualizadores", {}).get(tela.aba_atual) or tela.area_imagem.currentWidget()
        if getattr(vis, "_pixmap", 1) is not None and not getattr(vis, "carregando", False):
            break
        _esperar(0.2)
    _esperar(1.5)


def _ctrl(tela, tecla) -> None:
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent

    assert tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, tecla, Qt.ControlModifier))


def _pdf(projeto, saida: Path, nome: str) -> list[dict]:
    """O PDF que sai, só com as PAGINAS (as outras tiradas numa CÓPIA do projeto), pela conta do
    programa (core/pipeline.processar); cada página vira um PNG."""
    import fitz

    from core import pipeline

    copia = copy.deepcopy(projeto)
    for pg in copia.paginas:
        if pg.indice not in PAGINAS:
            pg.apagada = True
    copia.caminho_saida = str(saida / f"_{nome}.pdf")
    caminho = pipeline.processar(copia)
    lista = []
    with fitz.open(caminho) as doc:
        for n, pagina in enumerate(doc):
            png = saida / f"pdf-{nome}-{n + 1}.png"
            pagina.get_pixmap(dpi=40).save(str(png))
            lista.append({"png": png.name, "pt": [round(pagina.rect.width), round(pagina.rect.height)]})
    Path(caminho).unlink(missing_ok=True)
    return lista


def _estado(projeto) -> dict:
    return {"rotacoes": [f.rotacao for f in projeto.folhas][:8],
            "giros": [p.giro_da_pagina for p in projeto.paginas][:16],
            "folhas_giradas": sum(1 for f in projeto.folhas if f.rotacao),
            "paginas_giradas": sum(1 for p in projeto.paginas if p.giro_da_pagina)}


def test_gerar_antes_depois(janela, tmp_path):
    from core import girar
    from ui.tela_conferir import FERRAMENTA_CORTAR

    pdf = Path(os.environ["GIRAR_CAPA_PDF"])
    saida = Path(os.environ["GIRAR_CAPA_SAIDA"])
    nome = os.environ.get("GIRAR_CAPA_NOME", "x")
    saida.mkdir(parents=True, exist_ok=True)
    estado: dict = {"codigo": nome}

    janela.resize(1400, 820)
    janela.show()                                   # offscreen: desenhado só na memória
    janela.abrir_livro(str(pdf))
    _esperar(2.0)
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._dividir_escolhidas(list(range(1, len(projeto.folhas))), esperar=True)
    assert not projeto.folhas[0].dividir and all(f.dividir for f in projeto.folhas[1:])
    estado["livro"] = {"folhas": len(projeto.folhas), "paginas": len(projeto.paginas),
                       "cortar_bordas": projeto.cortar_bordas,
                       "endireitar": getattr(projeto, "endireitar", None),
                       "ordem_do_preparo": getattr(projeto, "ordem_do_preparo", None),
                       "filtro_padrao": getattr(projeto, "filtro_padrao", None)}
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    estado["pdf-original"] = _pdf(projeto, saida, "original")

    for situacao, pagina, palavras in (("s1", 0, "todas as folhas"), ("s2", 13, "todas as páginas")):
        tela.ir_para_pagina(pagina)
        _esperar_previa(tela)
        tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
        assert tela.barra_girar.combo_alcance.currentText() == palavras, (
            tela.barra_girar.combo_alcance.currentText())
        tela.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA].click()
        _esperar_previa(tela)
        estado[situacao] = {"pagina": pagina + 1, "lista": palavras,
                            "quadro": tela.barra_girar.rotulo.text(),
                            "historico": janela.acoes.feitas[-1].descricao, **_estado(projeto)}
        janela.grab().save(str(saida / f"tela-{situacao}-pagina{pagina + 1}.png"))
        tela.ir_para_pagina(0 if pagina else 13)              # a outra ponta, na tela
        _esperar_previa(tela)
        janela.grab().save(str(saida / f"tela-{situacao}-pagina{(0 if pagina else 13) + 1}.png"))
        estado[f"pdf-{situacao}"] = _pdf(projeto, saida, situacao)
        from PySide6.QtCore import Qt

        _ctrl(tela, Qt.Key_Z)
        estado[situacao]["depois_do_ctrl_z"] = _estado(projeto)
        _ctrl(tela, Qt.Key_Y)
        estado[situacao]["depois_do_ctrl_y"] = _estado(projeto)
        _ctrl(tela, Qt.Key_Z)
        assert estado[situacao]["depois_do_ctrl_z"]["folhas_giradas"] == 0
        assert estado[situacao]["depois_do_ctrl_z"]["paginas_giradas"] == 0

    (saida / "estado.json").write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
