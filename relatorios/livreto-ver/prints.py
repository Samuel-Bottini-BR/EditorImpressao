"""Prints da D-574 com o Palatino de verdade (fora da tela, offscreen).

Usa uma CÓPIA do PDF que o Samuel usou ("Giovambattista Palatino cittadino
romano - sem fundo (2).pdf", da Área de Trabalho; o original só foi lido) em
_tmp/palatino/, e uma pasta de dados própria (_tmp/dados-prints) (nada vai
para o configuracoes.json dele). Grava os prints e medidas.json aqui ao lado.

Rodar: .venv\\Scripts\\python.exe relatorios\\livreto-ver\\prints.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
os.environ["QT_QPA_PLATFORM"] = "offscreen"
(RAIZ / "_tmp" / "dados-prints").mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(RAIZ / "_tmp" / "dados-prints")
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

import fitz  # noqa: E402
import numpy as np  # noqa: E402
from PySide6.QtGui import QFontDatabase  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from core import impressao as imp  # noqa: E402

PALATINO = RAIZ / "_tmp" / "palatino" / "palatino-sem-fundo-2.pdf"
NOME_DELE = "Giovambattista Palatino cittadino romano - sem fundo (2).pdf"


def esperar(condicao, segundos=120.0) -> float:
    inicio = time.monotonic()
    while time.monotonic() - inicio < segundos:
        app.processEvents()
        if condicao():
            return time.monotonic() - inicio
        time.sleep(0.01)
    raise TimeoutError


def quieta(d) -> bool:
    return (not d._relogio_da_previa.isActive() and not d._previa_pendente
            and not (d.tarefa_previa is not None and d.tarefa_previa.isRunning())
            and not d.bolinha_da_previa.carregando and d.folha_na_tela is not None)


def foto(d, nome: str) -> str:
    for _ in range(5):
        app.processEvents()
        time.sleep(0.02)
    caminho = AQUI / nome
    d.grab().save(str(caminho))
    return caminho.name


app = QApplication.instance() or QApplication(sys.argv)
for arquivo in ("segoeui.ttf", "segoeuib.ttf", "seguisb.ttf"):
    if Path("C:/Windows/Fonts", arquivo).is_file():
        QFontDatabase.addApplicationFont(str(Path("C:/Windows/Fonts", arquivo)))

from ui.dialogo_impressao import DialogoImpressao  # noqa: E402

# o nome do arquivo na janela é o dele (a cópia fica numa pasta com o mesmo nome)
pasta = RAIZ / "_tmp" / "palatino" / "com-o-nome-dele"
pasta.mkdir(parents=True, exist_ok=True)
entrada = pasta / NOME_DELE
try:
    if not entrada.exists():
        os.link(PALATINO, entrada)          # mesmo disco: sem copiar 172 MB de novo
except OSError:
    import shutil
    if not entrada.exists():
        shutil.copy2(PALATINO, entrada)

medidas: dict = {}
opcoes = imp.OpcoesDeImpressao()
opcoes.paginas_por_caderno = 20
d = DialogoImpressao(str(entrada))
d.definir_opcoes(opcoes)
d.resize(1000, 640)
d.show()
inicio = time.monotonic()
esperar(lambda: d.bolinha_da_previa.carregando, 5)
fotos = [foto(d, "1-ao-abrir-montando.png")]
esperar(lambda: quieta(d))
medidas["primeira_folha_desde_abrir_s"] = round(time.monotonic() - inicio, 2)
fotos.append(foto(d, "2-folha-1-frente-e-verso.png"))
medidas["folha_1"] = [d.rotulos_da_face[l].text() for l in (imp.FRENTE, imp.VERSO)]

# quais páginas a montagem pôs na folha 1 (a mesma conta do arquivo)
with fitz.open(str(entrada)) as doc:
    escolhidas = imp._paginas_escolhidas(doc.page_count, opcoes)
lados = imp._lados_do_livreto(len(escolhidas), opcoes)
medidas["folha_1_paginas"] = {
    "frente": [None if p is None else p + 1 for p in (lados[0].esquerda, lados[0].direita)],
    "verso": [None if p is None else p + 1 for p in (lados[1].esquerda, lados[1].direita)],
}

# a prévia é o PDF? folha 1 gravada de verdade (como sai de fábrica) x prévia
so_1 = imp.OpcoesDeImpressao.de_dicionario(opcoes.para_dicionario())
so_1.folhas_de = so_1.folhas_ate = 1
saida = pasta / "folha1.pdf"
imp.montar_para_impressao(str(entrada), saida, so_1)
diferencas = []
with fitz.open(str(saida)) as pdf:
    for n, face in enumerate(d.folha_na_tela.faces):
        zoom = face.largura / pdf[n].rect.width
        pix = pdf[n].get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csRGB, alpha=False)
        a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width * 3]
        b = np.frombuffer(face.amostras, np.uint8).reshape(face.altura, face.largura * 3)
        diferencas.append(round(float(np.abs(a.astype(int) - b.astype(int)).mean()), 3))
medidas["diferenca_media_previa_x_pdf_0_a_255"] = diferencas

# a seta: folha 2
t = time.monotonic()
d.botao_folha_seguinte.click()
medidas["clique_na_seta_volta_em_s"] = round(time.monotonic() - t, 3)
medidas["folha_2_s"] = round(esperar(lambda: quieta(d) and d.folha_na_tela.numero == 2), 2)
fotos.append(foto(d, "3-seta-folha-2.png"))
medidas["folha_2"] = [d.rotulos_da_face[l].text() for l in (imp.FRENTE, imp.VERSO)]

# trocar a opção: 16 páginas por caderno refaz a folha
d.combo_caderno.setCurrentIndex(d.combo_caderno.findData(16))
medidas["troca_16_por_caderno_s"] = round(esperar(lambda: quieta(d)), 2)
fotos.append(foto(d, "4-trocou-para-16-por-caderno.png"))
medidas["depois_de_trocar"] = [d.rotulos_da_face[l].text() for l in (imp.FRENTE, imp.VERSO)]

# o tamanho do notebook dele (1000 x 617) e a janela mínima
d.combo_caderno.setCurrentIndex(d.combo_caderno.findData(20))
esperar(lambda: quieta(d))
d.resize(1000, 617)
fotos.append(foto(d, "5-notebook-1000x617.png"))
d.resize(d.minimumSize())
fotos.append(foto(d, "6-janela-minima.png"))
d.reject()

medidas["fotos"] = fotos
(AQUI / "medidas.json").write_text(json.dumps(medidas, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(medidas, ensure_ascii=False, indent=1))
