r"""Tentativa de reproduzir a janela que sumiu sem log (verificador, 21/10/2026:
"A janela de teste sumiu uma vez (Egenloff, ao clicar 'Deixar em branco'), sem
nada no erros.log; reaberta, o mesmo clique funcionou").

Janela sumida sem erros.log = o processo morreu sem passar pelo sys.excepthook:
falha dentro do Qt/OpenCV/PyMuPDF (C++) ou o Windows matando o processo. Por isso
o faulthandler grava, em PASTA\faulthandler.txt, onde cada fio estava se o
processo cair.

O que faz: o livro Egenloff 1 a 14 (cópia do pedaço do verificador), como livro
novo, em Preto e branco com "Só as letras", na tela de conferir de verdade
(TelaConferir + GerenciadorPrevias, com os fios de verdade), sem aparecer. Vai à
página 12, espera o aviso "Página sem conteúdo" chegar (a medida por trás) e
clica "Deixar em branco"; espera, desfaz, e repete. Três jeitos, N vezes cada:
  a) clica e espera a prévia nova;
  b) clica e troca de página logo em seguida (a medida e a prévia ainda rodando);
  c) clica, desfaz e clica de novo sem esperar;
  d) o livro aberto de novo a cada vez, e o clique logo que o aviso chega pela
     primeira vez (a medida acabou de terminar), trocando de página na hora.

Uso: python reproduzir_deixar_em_branco.py PDF PASTA [N]
LOCALAPPDATA e TEMP descartáveis dentro da PASTA.
"""
from __future__ import annotations

import faulthandler
import os
import sys
import time
from pathlib import Path

pdf, pasta = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
vezes = int(sys.argv[3]) if len(sys.argv) > 3 else 10
pasta.mkdir(parents=True, exist_ok=True)
for nome in ("_localappdata", "_tmp"):
    (pasta / nome).mkdir(exist_ok=True)
os.environ["LOCALAPPDATA"] = str(pasta / "_localappdata")
os.environ["TEMP"] = os.environ["TMP"] = str(pasta / "_tmp")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
RAIZ = Path(__file__).resolve().parents[2]
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))
arquivo_falha = open(pasta / "faulthandler.txt", "w", encoding="utf-8")
faulthandler.enable(arquivo_falha, all_threads=True)

from PySide6.QtWidgets import QApplication  # noqa: E402

app = QApplication.instance() or QApplication([])

from core import analise  # noqa: E402
from core.aquecimento import aquecer_dependencias_pesadas  # noqa: E402
from core.filtros import PRETO_E_BRANCO  # noqa: E402
from historico_acoes import HistoricoAcoes  # noqa: E402
from modelos import Projeto  # noqa: E402
from ui.tarefas import GerenciadorPrevias, TarefaAnalise  # noqa: E402
from ui.tela_conferir import TelaConferir  # noqa: E402


def esperar(segundos: float, ate=None) -> bool:
    fim = time.time() + segundos
    while time.time() < fim:
        app.processEvents()
        if ate is not None and ate():
            return True
        time.sleep(0.02)
    return ate() if ate is not None else True


def dizer(*partes) -> None:
    print(time.strftime("%H:%M:%S"), *partes, flush=True)


aquecer_dependencias_pesadas()
projeto = Projeto(caminho_entrada=str(pdf), nome=pdf.stem)
projeto.filtro_padrao = PRETO_E_BRANCO
projeto.misto_so_as_letras = True
feito: dict = {}
tarefa = TarefaAnalise(projeto)
tarefa.concluida.connect(lambda r: feito.setdefault("p", r))
tarefa.falhou.connect(lambda m: feito.setdefault("erro", m))
tarefa.run()
projeto = feito["p"]
dizer("analisado:", len(projeto.paginas), "páginas")

tela = TelaConferir()
tela.resize(1280, 657)
tela.show()
previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
tela.carregar(projeto, HistoricoAcoes(), previas)
ALVO = 11                                   # a página 12


def botao_em_branco():
    b = tela.botao_sugestao
    return b if (b.isVisible() and b.text() == "Deixar em branco") else None


def chegar() -> bool:
    tela.ir_para_pagina(ALVO)
    ok = esperar(90, lambda: botao_em_branco() is not None)
    if not ok:
        dizer("  o aviso não chegou em 90 s; alertas:", projeto.paginas[ALVO].alertas)
    return ok


cliques = 0
for jeito in ("a", "b", "c"):
    for vez in range(vezes):
        if not chegar():
            break
        botao_em_branco().click()
        cliques += 1
        if jeito == "a":
            esperar(6)
        elif jeito == "b":
            tela.ir_para_pagina(ALVO + 1)
            esperar(0.3)
            tela.ir_para_pagina(ALVO - 1)
            esperar(4)
            tela.ir_para_pagina(ALVO)
            esperar(2)
        else:
            tela.desfazer()
            esperar(0.05)
            if botao_em_branco() is not None:
                botao_em_branco().click()
                cliques += 1
            esperar(3)
        pagina = projeto.paginas[ALVO]
        dizer(f"jeito {jeito} vez {vez + 1}: em_branco={pagina.em_branco}, cliques={cliques}")
        while tela.acoes.pode_desfazer and projeto.paginas[ALVO].em_branco:
            tela.desfazer()
        esperar(2)

previas.parar()

# d) livro aberto de novo, várias vezes: o clique logo que o aviso chega pela
# PRIMEIRA vez (a medida por trás acabou de terminar e a prévia ainda está sendo
# refeita), que é o caso da conferência; depois troca de página na hora.
import json  # noqa: E402

from modelos import Projeto as _P  # noqa: E402

dados_do_livro = json.dumps(projeto.para_dicionario())
for vez in range(vezes):
    novo = _P.de_dicionario(json.loads(dados_do_livro))
    novo.reforcar_texto_falhado = True
    tela2 = TelaConferir()
    tela2.resize(1280, 657)
    tela2.show()
    previas2 = GerenciadorPrevias(novo.caminho_entrada, novo, tela2)
    tela2.carregar(novo, HistoricoAcoes(), previas2)
    tela2.ir_para_pagina(ALVO)
    b = tela2.botao_sugestao
    ok = esperar(90, lambda: b.isVisible() and b.text() == "Deixar em branco")
    if ok:
        b.click()
        cliques += 1
        tela2.ir_para_pagina(ALVO + 1)
        esperar(5)
    dizer(f"jeito d vez {vez + 1}: aviso chegou={ok}, em_branco={novo.paginas[ALVO].em_branco}")
    previas2.parar()
    tela2.close()
    tela2.deleteLater()
    esperar(1)

erros = Path(os.environ["LOCALAPPDATA"])
logs = list(erros.rglob("erros.log"))
dizer("FIM: cliques", cliques, "; erros.log:",
      [(str(p), p.read_text(encoding="utf-8", errors="replace")[-2000:]) for p in logs] or "nenhum")
