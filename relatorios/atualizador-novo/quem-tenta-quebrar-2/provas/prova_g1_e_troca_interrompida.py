"""Prova EXECUTADA (quem tenta quebrar, volta 2): o executor DE VERDADE (`atualizacao.Atualizacao`), a regra de verdade,
a peça do Windows de verdade (a lista de processos), o `estado.json` de verdade (numa pasta minha: PROGRAMDATA
desviado) e o `Update.exe` DE VERDADE do Velopack esperando um processo (`apply --waitPid`, sem pacote: ele desiste sem
mexer). Só o Velopack da biblioteca (procurar/baixar/trocar) é de mentira.

1. G1: a troca 1.1.0 -> 1.2.0 anotada no disco, o atualizador do Velopack rodando, abre a 1.1.0 "pelo atalho".
2. A troca que parou no meio (o notebook desligou, ou o Velopack morreu) ANTES de trocar: o Velopack já não roda, a
   anotação ficou. Abre a 1.1.0 pelo atalho. O que fica anotado, que frase vai para a tela, e o que acontece na
   abertura seguinte quando a 1.2.0 é achada de novo (D-769: "Se o notebook desligar no meio, nada se perde e a troca
   tenta de novo depois").
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAMO = Path(r"D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo")
R = Path(r"D:\programas\EditorImpressao\rascunho-qtq2\vp")
RAIZ = R / "raiz"
SEM_JANELA = 0x08000000
os.environ["PROGRAMDATA"] = str(R / "env" / "pd-g1")
os.environ["LOCALAPPDATA"] = str(R / "env" / "local-g1")
Path(os.environ["LOCALAPPDATA"]).mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(RAMO))
import atualizacao  # noqa: E402
import versao  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402
from core import windows  # noqa: E402

versao.VERSAO = "1.1.0"
# A instalação de prova é portátil (.portable) para o Velopack de verdade não mexer no registro do Windows nem em
# atalhos; para o executor, ela conta como instalada (só esta troca, na prova).
atualizacao.e_portatil = lambda raiz=None: False


class Achada:
    pacote, versao, arquivo, sha256, tamanho = "EditorImpressaoPrograma", "1.2.0", "x-1.2.0-full.nupkg", "ab" * 32, 1


class VelopackDeMentira:
    @staticmethod
    def procurar(endereco):
        return Achada()


def executor():
    return atualizacao.Atualizacao(windows=windows, velopack=VelopackDeMentira, raiz=RAIZ,
                                   por_tras=lambda f: f(), pasta_grava=lambda r: True,
                                   garantir_motor=lambda: True, motor_no_lugar=lambda v: True)


def anotar_troca():
    atualizacao.gravar_estado({"tentando": {"de": "1.1.0", "para": "1.2.0", "volta": False, "quando": "x"}})


def fotografia(a):
    return {"saida": a.saida, "fase": a.estado.fase.value, "estado.json": atualizacao.ler_estado(),
            "para a tela": [type(e).__name__ + (f"({e.tipo}) -> {atualizacao.FRASES_DA_FALHA[e.tipo]}"
                                                if isinstance(e, fases.MostrarFalha) else "")
                            for e in a._fila_da_tela]}


saida = {}
# 1. G1 com o atualizador do Velopack de verdade esperando
anotar_troca()
esperador_exe = R / "fora" / "esperador.exe"
esperador = subprocess.Popen([str(esperador_exe), "-n", "8", "127.0.0.1"], creationflags=SEM_JANELA,
                             stdout=subprocess.DEVNULL)
apply = subprocess.Popen([str(RAIZ / "Update.exe"), "apply", "--package", str(RAIZ / "packages" / "nao-existe.nupkg"),
                          "--waitPid", str(esperador.pid), "--silent", "--norestart", "--root", str(RAIZ)],
                         env={**os.environ, "LOCALAPPDATA": str(R / "env" / "local"), "TEMP": str(R / "env" / "temp"),
                              "TMP": str(R / "env" / "temp")}, creationflags=SEM_JANELA)
time.sleep(1.5)
a = executor()
a.abrir([])
saida["1_g1_com_o_velopack_esperando"] = fotografia(a)
apply.wait(90)
esperador.wait(30)

# 2. A troca que parou antes de trocar: o Velopack já não roda; a anotação ficou
anotar_troca()
b = executor()
b.abrir([])
saida["2_troca_interrompida_abertura_seguinte"] = fotografia(b)
c = executor()
c.abrir([])
saida["2b_mais_uma_abertura_a_1.2.0_publicada"] = fotografia(c)
with open(atualizacao.caminho_do_registro(), encoding="utf-8") as f:
    saida["registro"] = [l.split(" | ", 2)[2].strip() for l in f.readlines()]

texto = json.dumps(saida, ensure_ascii=False, indent=1)
Path(__file__).with_name("prova_g1_e_troca_interrompida-resultado.txt").write_text(texto, encoding="utf-8")
print(texto)
