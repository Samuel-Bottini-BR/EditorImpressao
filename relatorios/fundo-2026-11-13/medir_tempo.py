"""Mede, SEM JANELA, o tempo de desenhar as páginas 3 a 6 do Siebmacher (cópia) na resolução
do livro, numa versão do programa, pelos caminhos que o conserto toca: a página em "Tirar o
fundo" (o mesmo caminho nas duas versões) e a página em Original (na versão nova, depois do
"Sim", com o fundo tirado; na de antes, como veio). Uma rodada; quem alterna as versões é
quem chama (antes, depois, antes, depois...).

    python medir_tempo.py <raiz do código> <cópia do Siebmacher> <arquivo .json de saída>
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

RAIZ, LIVRO, SAIDA = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

import fitz  # noqa: E402

from core import pipeline  # noqa: E402
from core.filtros import ORIGINAL, TIRAR_FUNDO  # noqa: E402
from modelos import Projeto  # noqa: E402

projeto = Projeto(caminho_entrada=LIVRO, nome="siebmacher")
projeto.filtro_padrao = TIRAR_FUNDO
projeto.detectar_regioes = False
projeto.dividir_folhas = False
projeto = pipeline.analisar_projeto(projeto)
projeto.limpar = True
assert projeto.tem_camadas
resultado = {}
with fitz.open(LIVRO) as doc:
    for nome, filtro in (("tirar_o_fundo", TIRAR_FUNDO), ("original_depois_do_sim", ORIGINAL)):
        tempos = []
        for i in (2, 3, 4, 5):
            pagina = projeto.paginas[i]
            pagina.filtro = TIRAR_FUNDO
            if hasattr(pagina, "fundo_tirado"):
                pagina.fundo_tirado = True          # o "Sim" da versão nova
            pagina.filtro = filtro
            pipeline.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)  # aquece
            t0 = time.perf_counter()
            pipeline.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
            tempos.append(round(time.perf_counter() - t0, 3))
        resultado[nome] = tempos
print(resultado)
SAIDA.write_text(json.dumps(resultado), encoding="utf-8")
