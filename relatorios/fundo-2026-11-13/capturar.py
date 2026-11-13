"""Captura, SEM JANELA NA TELA (QT_QPA_PLATFORM=offscreen), as imagens e as medidas do
conserto do fundo tirado (D-646/D-699), numa versão do programa (a de antes, 863cdde3, ou a
nova, ramo fundo-2026-11-13).

    python capturar.py <raiz do código> <pasta de saída> <cópia do Siebmacher (10 páginas)>

O caminho do teste como o Kaique de 07/11: abrir o livro, "Sim, tirar o fundo", rodar o
Automático do jeito que ele abre ("Limpar a folha" em Original, mais Endireitar e Cortar as
bordas, os de fábrica). Depois, na versão nova, também: "Desfazer o tirar o fundo" na página
3 (pelo menu Filtro) e o Automático com Preto e branco (o filtro por cima da página sem o
fundo). As páginas
são desenhadas pelo caminho do PDF (core.pipeline.renderizar_pagina). Medidas, por página:
o brilho do papel (mediana do canal azul da página: o papel amarelado tem pouco azul; o
branco, 255). (O tempo é medido à parte: medir_tempo.py.) LOCALAPPDATA e projetos à parte; só
uma CÓPIA do livro.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

RAIZ, SAIDA, LIVRO = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
SAIDA.mkdir(parents=True, exist_ok=True)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")
dados = Path(tempfile.mkdtemp(prefix="fundo-"))
os.environ["LOCALAPPDATA"] = str(dados / "dados")
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from PySide6.QtWidgets import QAbstractButton, QApplication  # noqa: E402

import projetos  # noqa: E402

(dados / "projetos").mkdir()
projetos.pasta_dos_projetos = lambda: dados / "projetos"
app = QApplication.instance() or QApplication([])

from core import automatico as A  # noqa: E402
from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.pipeline import renderizar_pagina  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402

PAGINAS = [2, 3, 4, 5]          # páginas 3 a 6 do print da pergunta
medidas: dict = {}


def assentar(segundos: float) -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.02)


def desenhar(janela, nome: str, medir_tempo: bool = False) -> None:
    doc = abrir_pdf(LIVRO)
    linha = {}
    try:
        for i in PAGINAS:
            pagina = janela.projeto.paginas[i]
            img, _ = renderizar_pagina(doc, janela.projeto, pagina, dpi=50)
            cor = img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cv2.imwrite(str(SAIDA / f"{nome}-{i + 1}.png"), cor)
            azul = float(np.median(cor[:, :, 0]))
            tempo = None
            if medir_tempo:
                t0 = time.perf_counter()
                renderizar_pagina(doc, janela.projeto, pagina, dpi=janela.projeto.qualidade_dpi)
                tempo = round(time.perf_counter() - t0, 3)
            linha[i + 1] = {"filtro": pagina.filtro,
                            "fundo_tirado": getattr(pagina, "fundo_tirado", "(não existe)"),
                            "papel_azul": azul, "tempo_s": tempo}
            print(nome, i + 1, linha[i + 1])
    finally:
        doc.close()
    medidas[nome] = linha


def rodar(janela, filtro: str) -> None:
    pedido = A.Pedido(etapas=[A.ENDIREITAR, A.CORTAR, A.LIMPAR],
                      opcoes={"filtro_padrao": filtro}, pular_mexidas=True)
    janela.rodar_o_automatico(pedido=pedido, esperar=True, perguntar=False)
    assentar(1)


janela = JanelaPrincipal()
janela.abrir_livro(LIVRO)
assentar(0.5)
caixa = janela.aviso_do_fundo
next(b for b in caixa.findChildren(QAbstractButton) if b.text() == "Sim, tirar o fundo").click()
assentar(0.5)
desenhar(janela, "1-com-o-fundo-tirado")
rodar(janela, ORIGINAL)
desenhar(janela, "2-depois-do-automatico-original")
conferir = janela.tela_conferir
if hasattr(conferir, "desfazer_o_tirar_o_fundo"):
    conferir.ir_para_pagina(2)
    janela._marcar_o_filtro_no_menu()
    janela.menu.acoes["desfazer_tirar_fundo"].trigger()
    desenhar(janela, "3-desfazer-o-tirar-o-fundo-na-pagina-3")
    rodar(janela, PRETO_E_BRANCO)
    desenhar(janela, "4-depois-do-automatico-preto-e-branco")
if janela.previas is not None:
    janela.previas.parar()
janela.close()
(SAIDA / "medidas.json").write_text(json.dumps(medidas, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
print("pronto", SAIDA)
