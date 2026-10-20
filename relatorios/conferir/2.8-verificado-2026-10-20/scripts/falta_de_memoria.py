"""Verificador, 20/10/2026 (item 2.8): quando a DLL responde "faltou memoria" (codigo ERRO_MEMORIA),
(a) a pagina sai igual ao "Automatico"? (b) o motivo chega ao erros.log do programa?
Finge a falta de memoria trocando so a funcao da DLL (a DLL de verdade nao e chamada para isso);
pasta de dados isolada; erros.log de teste lido no fim. Nao muda o programa."""
import logging
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
dados = Path(tempfile.mkdtemp(prefix="verif28_mem_"))
os.environ["LOCALAPPDATA"] = str(dados)
sys.path.insert(0, str(RAIZ))

import numpy as np  # noqa: E402

from core import filtros as F  # noqa: E402
from core import preto_e_branco_scantailor as pbst  # noqa: E402
from core import st_ferramentas as st  # noqa: E402
from registro import caminho_do_log  # noqa: E402

rng = np.random.default_rng(3)
img = np.clip(200 + rng.normal(0, 20, (600, 400)), 0, 255).astype(np.uint8)
img[100:130, 50:350] = 40

biblioteca = st.padrao()
original = biblioteca.funcao


class FuncaoSemMemoria:
    def __call__(self, *args):
        print("    (a DLL fingida foi chamada)")
        erro = args[-2]
        erro.value = b"std::bad_alloc (fingido pelo verificador)"
        return st.ERRO_MEMORIA


biblioteca.funcao = lambda nome: FuncaoSemMemoria() if nome == "st_ferramentas_preto_e_branco" else original(nome)

# o que o programa faz com o log quando roda como o Kaique roda (pythonw, sem configurar o logging)
ouvidos = []


class Ouvido(logging.Handler):
    def emit(self, r):
        ouvidos.append(r.getMessage())


logging.getLogger().addHandler(Ouvido())
logging.getLogger().setLevel(logging.WARNING)          # so para ver se a mensagem foi emitida

class Pontinhos:            # o DPI de verdade, como o programa passa (sem ele, a pagina pequena seria recusada antes)
    dpi = 300


saida = F.filtro_preto_e_branco(img, 50, Pontinhos(), algoritmo="st_sauvola")
auto = F.filtro_preto_e_branco(img, 50, Pontinhos(), algoritmo="auto")
print("(a) saiu igual ao Automatico:", np.array_equal(saida, auto))
print("    mensagens emitidas pelo logging:", ouvidos)
log = caminho_do_log()
print("(b) erros.log existe:", log.exists(), "| conteudo:", log.read_text(encoding="utf-8") if log.exists() else "(nenhum)")
print("    handlers no logger raiz alem do meu:", [h for h in logging.getLogger().handlers if not isinstance(h, Ouvido)])
