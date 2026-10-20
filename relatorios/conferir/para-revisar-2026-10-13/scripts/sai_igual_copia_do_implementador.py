r"""Prova de que o LIVRO JÁ COMEÇADO sem o "Para revisar" sai igual ao fase-1
nas páginas-gabarito (pedido da gerente, 20/10/2026, na junção com o layout).

O que é "livro já começado": um projeto gravado pelo programa de hoje (o
fase-1), sem nenhum campo novo do "Para revisar" (`reforcar_texto_falhado`,
`alertas_aceitos`, `em_branco`, `forca_antes_do_reforco`, `reforco_desfeito`,
`faixa_na_beirada`, `marcacao_provisoria`). Ao abrir, o programa novo põe o
valor padrão de projeto antigo (a força do preto sozinha DESLIGADA etc.).

Como prova, em duas etapas, sempre pelo mesmo caminho do programa
(ui/tarefas.py: TarefaAnalise.run e TarefaProcessar.run, PDF gravado e lido de
volta, como conferencia.processar_pelo_programa):

  1. "analisar" (com o código do fase-1): para cada página do gabarito e cada
     jeito, a análise automática e o projeto gravado em JSON
     (Projeto.para_dicionario, o mesmo do projeto.json);
  2. "processar" (rodado DUAS vezes: com o fase-1 e com o ramo juntado): abre
     cada JSON (Projeto.de_dicionario, como abrir o projeto), processa, tira as
     páginas do PDF e grava a soma (sha256) dos pontos de cada página.

Os dois somas.json têm de ser iguais, página por página.

Jeitos: "pb_letras" (Preto e branco com "Só as letras" de fábrica: é onde o
"Para revisar" mede e onde a força do preto sozinha agiria) e "magico_pro"
(o filtro de fábrica do livro novo).

Uso (uma coisa pesada por vez; nenhuma janela; LOCALAPPDATA e TEMP
descartáveis, dentro da PASTA):
    python sai_igual_projeto_antigo.py analisar  RAIZ_FASE1 PASTA
    python sai_igual_projeto_antigo.py processar RAIZ_DO_CODIGO PASTA NOME
Os PDFs do gabarito e a pasta modelos\ são só lidos.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

etapa, raiz, pasta = sys.argv[1], Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
nome = sys.argv[4] if len(sys.argv) > 4 else ""
pasta.mkdir(parents=True, exist_ok=True)
dados = pasta / f"_localappdata_{etapa}_{nome}"
tmp = pasta / f"_tmp_{etapa}_{nome}"
dados.mkdir(exist_ok=True)
tmp.mkdir(exist_ok=True)
os.environ["LOCALAPPDATA"] = str(dados)
os.environ["TEMP"] = os.environ["TMP"] = str(tmp)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.chdir(raiz)
sys.path.insert(0, str(raiz))

import tempfile  # noqa: E402

tempfile.tempdir = str(tmp)

MODELOS = Path(r"D:\programas\EditorImpressao\modelos")     # somente leitura
if not (raiz / "modelos").exists():
    import core.detectar_regioes as _dr
    import core.ocr_doctr as _doctr
    import core.ocr_tesseract as _tess
    import core.rede_selecao as _rede

    _dr.CAMINHO_MODELO = MODELOS / "doclayout.onnx"
    _dr._detector.caminho = _dr.CAMINHO_MODELO
    _doctr.CAMINHO_MODELO = MODELOS / "doctr" / _doctr.CAMINHO_MODELO.name
    _tess.PASTA_DOS_MODELOS = MODELOS / "tessdata"
    _rede.PASTA = MODELOS / "mobile_sam"
    _rede.CODIFICADOR = _rede.PASTA / _rede.CODIFICADOR.name
    _rede.DECODIFICADOR = _rede.PASTA / _rede.DECODIFICADOR.name

import conferencia  # noqa: E402  (o do código escolhido)
from core.filtros import MAGICO_PRO, PRETO_E_BRANCO  # noqa: E402
from modelos import Projeto  # noqa: E402
from ui.tarefas import TarefaAnalise, TarefaProcessar  # noqa: E402

GABARITO = Path(r"D:\programas\EditorImpressao\gabarito")
lista = json.loads((GABARITO / "lista.json").read_text(encoding="utf-8"))
IDS = list(lista["paginas"])
JEITOS = {"pb_letras": (PRETO_E_BRANCO, True), "magico_pro": (MAGICO_PRO, False)}
PROJETOS = pasta / "projetos"


def analisar() -> None:
    """Etapa 1, com o fase-1: a análise automática e o projeto gravado."""
    PROJETOS.mkdir(exist_ok=True)
    for pid in IDS:
        pdf = GABARITO / lista["paginas"][pid]["pdf"]
        for jeito, (filtro, so_as_letras) in JEITOS.items():
            destino = PROJETOS / f"{pid}__{jeito}.json"
            if destino.exists():
                continue
            projeto = Projeto(caminho_entrada=str(pdf), nome=pdf.stem)
            projeto.filtro_padrao = filtro
            projeto.misto_so_as_letras = so_as_letras
            feito: dict = {}
            tarefa = TarefaAnalise(projeto)
            tarefa.concluida.connect(lambda r: feito.setdefault("projeto", r))
            tarefa.falhou.connect(lambda m: feito.setdefault("erro", m))
            tarefa.run()
            if "projeto" not in feito:
                print(pid, jeito, "ANÁLISE FALHOU:", feito.get("erro"), flush=True)
                continue
            texto = json.dumps(feito["projeto"].para_dicionario(), ensure_ascii=False)
            destino.write_text(texto, encoding="utf-8")
            print(pid, jeito, "analisado", flush=True)


def processar() -> None:
    """Etapa 2: abre cada projeto gravado pelo fase-1, processa e soma os pontos."""
    saida = pasta / f"somas-{nome}.json"
    somas = json.loads(saida.read_text(encoding="utf-8")) if saida.exists() else {}
    for arquivo in sorted(PROJETOS.glob("*.json")):
        chave = arquivo.stem
        if chave in somas:
            continue
        projeto = Projeto.de_dicionario(json.loads(arquivo.read_text(encoding="utf-8")))
        projeto.caminho_saida = str(tmp / f"{chave}.pdf")
        feito: dict = {}
        tarefa = TarefaProcessar(projeto)
        tarefa.concluida.connect(lambda c: feito.setdefault("caminho", c))
        tarefa.falhou.connect(lambda m: feito.setdefault("erro", m))
        tarefa.cancelada.connect(lambda: feito.setdefault("erro", "cancelado"))
        inicio = time.perf_counter()
        tarefa.run()
        if "caminho" not in feito:
            somas[chave] = {"erro": str(feito.get("erro"))}
        else:
            caminho = Path(feito["caminho"])
            partes = conferencia.paginas_do_pdf(caminho, projeto.qualidade_dpi)
            caminho.unlink(missing_ok=True)
            somas[chave] = {
                "paginas": [{"forma": list(p.shape),
                             "sha256": hashlib.sha256(p.tobytes()).hexdigest()} for p in partes],
                "segundos": round(time.perf_counter() - inicio, 1),
                "reforcar_texto_falhado": bool(getattr(projeto, "reforcar_texto_falhado", False)),
                "forcas": [int(getattr(p, "forca_preto", 0)) for p in projeto.paginas],
            }
        print(chave, somas[chave].get("erro") or somas[chave]["paginas"][0]["sha256"][:12],
              flush=True)
        saida.write_text(json.dumps(somas, indent=1, ensure_ascii=False), encoding="utf-8")


conferencia._garantir_aplicacao_qt()
from core.aquecimento import aquecer_dependencias_pesadas  # noqa: E402

aquecer_dependencias_pesadas()
try:
    analisar() if etapa == "analisar" else processar()
finally:
    shutil.rmtree(dados, ignore_errors=True)
    shutil.rmtree(tmp, ignore_errors=True)
print("FIM", etapa, nome, flush=True)
