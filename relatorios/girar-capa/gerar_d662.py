"""Antes/depois da D-662 no Gradus Primus (CÓPIA), SEM janela na tela (relatorios/girar-capa).

D-662 (Samuel, Central, 10/11/2026): "No Dividir, com "Duas lado a lado", "todas as folhas": gira a
folha inteira ou página por página?" → "Página por página também".

Roda como um teste do pytest, com o conftest dos testes (offscreen: o Qt desenha na memória e nada
aparece na tela; LOCALAPPDATA de mentira), no código que se quer medir:

    cd <código: girar-capa (com o conserto, c76d4b97) ou uma cópia em 3216b885 (sem o conserto)>
    set QT_QPA_PLATFORM=offscreen
    set QT_SCALE_FACTOR=2                 (as fotos saem com o dobro de pontos, como em 09/11)
    set QT_QPA_FONTDIR=C:\\Windows\\Fonts
    set D662_PDF=<cópia do Gradus>        (nunca o original)
    set D662_SAIDA=<pasta das fotos cruas>
    python -m pytest -p tests.conftest <este arquivo> -q -s

O mesmo enquadramento das provas de 09/11 (relatorios/girar-capa-provas, pergunta 3): folhas 2 a 70
divididas (a capa inteira); ferramenta Dividir, "Duas lado a lado", folha 10 (páginas 18 e 19);
"todas as folhas" + ¼ à direita. Fotos: a janela do Dividir (desenhada na memória), a tira do Dividir,
as miniaturas das páginas 1, 18, 19, 20 e 21 (na ferramenta Cortar as bordas) e essas páginas como
saem no PDF. A MEDIDA: cada página do PDF de depois comparada com a mesma página de antes girada ¼
(tamanho igual e diferença média pequena = a página inteira deitada; tamanho outro = uma tira com
pedaço da vizinha). Depois o Ctrl+Z (tudo volta) e o Ctrl+Y.
"""
from __future__ import annotations

import copy
import json
import os
import time
from pathlib import Path

import numpy as np
import pytest

from tests.test_decisoes_girar_pagina import app, janela, pasta  # noqa: F401

PAGINAS = [0, 17, 18, 19, 20]                # páginas 1 (capa), 18, 19, 20 e 21
FOLHA = 9                                    # folha 10 do scan: páginas 18 e 19


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


def _esperar_miniaturas(tela, indices, limite: float = 90.0) -> None:
    t0 = time.time()
    while time.time() - t0 < limite:
        if all(i in tela.tira._cruas for i in indices):
            break
        _esperar(0.3)
    _esperar(1.0)


def _ctrl(tela, tecla) -> None:
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent

    assert tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, tecla, Qt.ControlModifier))


def _pdf(projeto, saida: Path, nome: str) -> tuple[list[dict], list[np.ndarray]]:
    """O PDF que sai (core/pipeline.processar), só com PAGINAS (as outras tiradas numa CÓPIA do
    projeto); cada página vira um PNG (60 ppp) e uma matriz (para a medida)."""
    import fitz

    from core import pipeline

    copia = copy.deepcopy(projeto)
    for pg in copia.paginas:
        if pg.indice not in PAGINAS:
            pg.apagada = True
    copia.caminho_saida = str(saida / f"_{nome}.pdf")
    caminho = pipeline.processar(copia)
    lista, matrizes = [], []
    with fitz.open(caminho) as doc:
        for n, pagina in enumerate(doc):
            pix = pagina.get_pixmap(dpi=60)
            png = saida / f"pdf-{nome}-{n + 1}.png"
            pix.save(str(png))
            lista.append({"png": png.name, "pt": [round(pagina.rect.width), round(pagina.rect.height)]})
            matrizes.append(np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3].copy())
    Path(caminho).unlink(missing_ok=True)
    return lista, matrizes


def _medida(antes: list[np.ndarray], depois: list[np.ndarray]) -> list[dict]:
    """Cada página de depois contra a mesma de antes girada ¼ à direita: tamanho igual e diferença
    média (0 a 255) pequena = a página inteira deitada, sem pedaço da vizinha."""
    import cv2

    saida = []
    for numero, a, d in zip([p + 1 for p in PAGINAS], antes, depois):
        girada = cv2.rotate(a, cv2.ROTATE_90_CLOCKWISE)
        linha = {"pagina": numero, "antes": list(a.shape[:2]), "depois": list(d.shape[:2]),
                 "antes_girada": list(girada.shape[:2])}
        if girada.shape == d.shape:
            linha["diferenca_media"] = round(float(np.abs(girada.astype(int) - d.astype(int)).mean()), 2)
            linha["veredito"] = "inteira, deitada" if linha["diferenca_media"] < 8 else "outra imagem"
        else:
            linha["diferenca_media"] = None
            linha["veredito"] = "outra forma (tira com pedaço da vizinha)"
        saida.append(linha)
    return saida


def _estado(projeto, tela, janela) -> dict:
    return {"rotacoes": [f.rotacao for f in projeto.folhas][:12],
            "giros": [p.giro_da_pagina for p in projeto.paginas][:22],
            "folhas_giradas": sum(1 for f in projeto.folhas if f.rotacao),
            "paginas_giradas": sum(1 for p in projeto.paginas if p.giro_da_pagina),
            "linhas_10": projeto.folhas[FOLHA].posicao_corte,
            "quadro": tela.barra_girar.rotulo.text(),
            "lista": tela.barra_girar.combo_alcance.currentText(),
            "historico": janela.acoes.feitas[-1].descricao if janela.acoes.feitas else ""}


def test_d662_gradus(janela):
    from PySide6.QtCore import Qt

    from core import girar
    from ui.tela_conferir import FERRAMENTA_CORTAR, FERRAMENTA_DIVIDIR
    from ui.widgets.paginas_rolando import DUAS, UMA

    saida = Path(os.environ["D662_SAIDA"])
    saida.mkdir(parents=True, exist_ok=True)
    janela.resize(1400, 820)
    janela.show()                                   # offscreen: desenhado só na memória
    janela.abrir_livro(str(Path(os.environ["D662_PDF"])))
    _esperar(2.0)
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._dividir_escolhidas(list(range(1, len(projeto.folhas))), esperar=True)
    assert projeto.paginas[17].folha == FOLHA and projeto.paginas[18].folha == FOLHA
    estado: dict = {}

    def no_dividir(foto: str) -> None:
        tela.escolher_ferramenta(FERRAMENTA_DIVIDIR)
        tela.definir_mostrar(DUAS)
        tela.ir_para_pagina(17)
        _esperar_previa(tela)
        _esperar_miniaturas(tela, [0, FOLHA, FOLHA + 1])
        assert tela.indice_folha == FOLHA
        estado[foto] = _estado(projeto, tela, janela)
        janela.grab().save(str(saida / f"tela-{foto}.png"))
        tela.tira.grab().save(str(saida / f"tira-{foto}.png"))

    def no_cortar(foto: str) -> list[np.ndarray]:
        tela.escolher_ferramenta(FERRAMENTA_CORTAR)
        tela.definir_mostrar(UMA)
        tela.ir_para_pagina(17)
        _esperar_previa(tela)
        _esperar_miniaturas(tela, PAGINAS)
        for i in PAGINAS:
            tela.tira._miniaturas[i].grab().save(str(saida / f"mini-{foto}-{i + 1}.png"))
        lista, matrizes = _pdf(projeto, saida, foto)
        estado[f"pdf-{foto}"] = lista
        return matrizes

    no_dividir("antes-dividir")
    pdf_antes = no_cortar("antes")

    # o clique: Dividir, "Duas lado a lado", folha 10, "todas as folhas" + ¼ à direita
    no_dividir("clique-dividir")
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    estado["lista-do-clique"] = tela.barra_girar.combo_alcance.currentText()
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    _esperar_previa(tela)
    _esperar(3.0)
    estado["depois-do-clique"] = _estado(projeto, tela, janela)
    janela.grab().save(str(saida / "tela-depois-dividir.png"))
    tela.tira.grab().save(str(saida / "tira-depois-dividir.png"))
    pdf_depois = no_cortar("depois")
    estado["medida"] = _medida(pdf_antes, pdf_depois)

    _ctrl(tela, Qt.Key_Z)
    estado["depois-do-ctrl-z"] = _estado(projeto, tela, janela)
    _ctrl(tela, Qt.Key_Y)
    estado["depois-do-ctrl-y"] = _estado(projeto, tela, janela)
    (saida / "estado.json").write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
