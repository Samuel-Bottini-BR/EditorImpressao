"""Mede, na TELA DE CONFERIR de verdade (sem aparecer no monitor, com os fios
de verdade), quanto tempo leva para a previa aparecer ao trocar de pagina num
livro que ainda nao tem marcacao nenhuma.

Para que: a regra 6 do plano. Desde 13/10/2026 a marcacao do tamanho do PDF e
procurada por tras, depois de a previa aparecer. O tempo de desenhar UMA previa
sozinha (tempo_da_primeira_previa.py) nao mostra se esse trabalho de tras
atrapalha a previa da pagina SEGUINTE (os dois dividem os fios e o
processador). Este script mostra: passa pelas paginas como o Kaique, parando
`pausa` segundos em cada uma, e anota quanto a previa de cada pagina demorou
para aparecer depois do pedido de ir para ela.

Uso:  python tempo_de_trocar_de_pagina.py <pasta do codigo> <livro.pdf> [pausa] [paginas]
      pasta do codigo: a raiz de uma copia do projeto (esta worktree, ou a de
      um commit antigo tirada com `git archive`); pausa em segundos (padrao
      1.5; 0 = troca assim que a previa aparece); paginas: quantas (padrao 12).

O livro e so lido. Pasta de dados do programa isolada. Aba Filtro, filtro de
fabrica. A primeira pagina aquece e fica fora da conta.
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
AQUI = Path(__file__).resolve().parent
CODIGO = Path(sys.argv[1]).resolve()
LIVRO = str(Path(sys.argv[2]).resolve())
PAUSA = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
PAGINAS = int(sys.argv[4]) if len(sys.argv) > 4 else 12
sys.path.insert(0, str(CODIGO))
os.chdir(CODIGO)

from pasta_de_dados_dos_scripts import isolar_pasta_de_dados  # noqa: E402

isolar_pasta_de_dados("tempo-de-trocar-de-pagina",
                      raiz=AQUI.parents[1] / "saida_teste" / "dados_dos_scripts")

from PySide6.QtWidgets import QApplication  # noqa: E402

from core import pipeline as P  # noqa: E402
from historico_acoes import HistoricoAcoes  # noqa: E402
from modelos import Projeto  # noqa: E402
from ui.tarefas import GerenciadorPrevias  # noqa: E402
from ui.tela_conferir import ABA_FILTRO, TelaConferir  # noqa: E402

app = QApplication.instance() or QApplication([])


def rodar_eventos(segundos: float, ate=None) -> float:
    """Roda a fila do Qt por `segundos`, ou ate `ate()` valer. Devolve quanto passou."""
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < segundos:
        app.processEvents()
        if ate is not None and ate():
            break
        time.sleep(0.005)
    return time.perf_counter() - t0


projeto = P.analisar_projeto(Projeto(caminho_entrada=LIVRO, nome="x"))
tela = TelaConferir()
previas = GerenciadorPrevias(LIVRO, projeto, tela)
tela.carregar(projeto, HistoricoAcoes(), previas)
tela.barra_abas.setCurrentIndex(tela._abas_ativas.index(ABA_FILTRO))
quantas = min(PAGINAS, len(projeto.paginas))


def previa_na_tela(i: int) -> bool:
    return previas.chave(i, tela._dpi_atual) in previas._cache


tela.ir_para_pagina(0)
rodar_eventos(60, lambda: previa_na_tela(0))
rodar_eventos(PAUSA)
tempos = []
for i in range(1, quantas):
    t0 = time.perf_counter()
    tela.ir_para_pagina(i)
    rodar_eventos(120, lambda: previa_na_tela(i))
    tempos.append(round(time.perf_counter() - t0, 3))
    rodar_eventos(PAUSA)
# deixa o trabalho de tras acabar antes de fechar (e diz quanto levou)
resto = rodar_eventos(300, lambda: (not previas._pedidas
                                    and not getattr(previas, "_medidas_a_espera", None)
                                    and previas._pool.activeThreadCount() == 0))
previas.parar()
print(f"pausa {PAUSA:.1f} s, {len(tempos)} trocas: media {statistics.mean(tempos):.2f} s, "
      f"mediana {statistics.median(tempos):.2f} s, pior {max(tempos):.2f} s; "
      f"trabalho de tras depois da ultima pagina: {resto:.1f} s   (codigo: {CODIGO.name})")
print(json.dumps({"codigo": str(CODIGO), "livro": LIVRO, "pausa": PAUSA, "tempos": tempos,
                  "media": round(statistics.mean(tempos), 3),
                  "mediana": round(statistics.median(tempos), 3), "pior": max(tempos)}))
