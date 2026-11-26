"""Prova EXECUTADA (quem tenta quebrar, volta 2): a volta para a versão anterior interrompida no meio (o notebook
desligado, ou o processo sem janela morto, depois do "Sim" ao fechar).

Dois processos de verdade, um depois do outro, com o executor e a regra de verdade e o estado.json de verdade numa pasta
minha (PROGRAMDATA desviado):
  1. a reabertura sem janela da 1.2.0 que o Velopack faz depois do "Sim" ao fechar (`--conferir-a-versao-nova 1.1.0
     1.2.0 --sem-janela`); o teste rápido falha (de mentira) e a volta começa; no primeiro passo da volta (buscar a
     assinatura da 1.1.0 na fonte) o processo MORRE (`os._exit`, como o Windows desligando);
  2. o Kaique abre o programa pelo atalho no dia seguinte: a 1.2.0 (a que falhou) abre, sem linha de comando.
Uso: python prova_volta_interrompida.py [1|2]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RAMO = Path(r"D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo")
R = Path(r"D:\programas\EditorImpressao\rascunho-qtq2\volta")
os.environ["PROGRAMDATA"] = str(R / "pd")
os.environ["LOCALAPPDATA"] = str(R / "local")
(R / "local").mkdir(parents=True, exist_ok=True)
(R / "raiz" / "current").mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(RAMO))
import atualizacao  # noqa: E402
import versao  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402

versao.VERSAO = "1.2.0"


class FonteQueMorre(atualizacao.Fonte):
    def ler(self, versao_do_arquivo, nome, limite=1_000_000):
        os._exit(9)                      # o processo morre aqui, como num desligar


def executor(teste_passa):
    return atualizacao.Atualizacao(windows=None, velopack=None, raiz=R / "raiz", fonte=FonteQueMorre(str(R)),
                                   por_tras=lambda f: None, pasta_grava=lambda r: True,
                                   garantir_motor=lambda: True, motor_no_lugar=lambda v: True,
                                   teste=lambda: (teste_passa, "falta um arquivo (de mentira)"))


if len(sys.argv) > 1 and sys.argv[1] == "1":
    atualizacao.gravar_estado({"tentando": {"de": "1.1.0", "para": "1.2.0", "volta": False, "quando": "x"}})
    executor(False).abrir([atualizacao.ARG_CONFERIR_NOVA, "1.1.0", "1.2.0", atualizacao.ARG_SEM_JANELA])
    print("não morreu")
elif len(sys.argv) > 1 and sys.argv[1] == "2":
    a = executor(True)
    a.abrir([])
    print(json.dumps({"versao que roda": versao.VERSAO, "fase": a.estado.fase.value, "saida": a.saida,
                      "para a tela": [f"{e.tipo}: {atualizacao.FRASES_DA_FALHA[e.tipo]}" for e in a._fila_da_tela
                                      if isinstance(e, fases.MostrarFalha)],
                      "teste rapido rodou de novo?": a.estado.fase is fases.Fase.CONFERINDO_NOVA}, ensure_ascii=False))
else:
    p1 = subprocess.run([sys.executable, __file__, "1"], capture_output=True, text=True, encoding="utf-8")
    depois_1 = atualizacao.ler_estado()
    p2 = subprocess.run([sys.executable, __file__, "2"], capture_output=True, text=True, encoding="utf-8")
    texto = json.dumps({"processo 1: codigo de saida (9 = morreu no meio da volta)": p1.returncode,
                        "estado.json depois do processo 1": depois_1,
                        "processo 2 (o atalho no dia seguinte)": json.loads(p2.stdout or "{}"),
                        "erros": (p1.stderr + p2.stderr)[-2000:],
                        "registro": (atualizacao.caminho_do_registro().read_text(encoding="utf-8")
                                     if atualizacao.caminho_do_registro().exists() else "")},
                       ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_volta_interrompida-resultado.txt").write_text(texto, encoding="utf-8")
    print(texto)
