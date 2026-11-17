"""ProvaPasta: programa de mentira para provar onde o Velopack 1.2.161 grava.

Id do pacote: EditorImpressaoProvaPasta (NUNCA EditorImpressao). Leva o
atualizacao.py de verdade (da worktree velopack-pasta) e chama as MESMAS
funcoes que o Editor chama ao abrir e que o ajudante chama ao atualizar.
Seguranca (so muda o que nao e da pasta de reserva):
- PROGRAMDATA e LOCALAPPDATA (variaveis) -> pastas de mentira no D:
  (o Velopack nao le a variavel: pergunta ao Windows; e isso que se prova);
- nomes das tarefas e marcas do Windows -> EditorImpressaoProvaPasta\...;
- a peca que fala com o Windows nos testes a distancia -> uma que so anota;
- preparar_o_computador -> nada (nao mexe no Visual C++ nem no Inno de verdade);
- a chave publica -> a de mentira desta prova;
- "programa aberto" -> sempre sim (nunca pede ao Velopack para trocar a pasta).
"""
import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path

BASE = Path(r"D:\agente_temp_testes\velopack-pasta")
os.environ["PROGRAMDATA"] = str(BASE / "programdata-de-mentira")
os.environ["LOCALAPPDATA"] = str(BASE / "localappdata-de-mentira")
REG = BASE / "registro-do-app.txt"


def anotar(texto):
    with open(REG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='milliseconds')} pid={os.getpid()} {texto}\n")


anotar(f"COMECO argv={sys.argv!r} usuario={os.environ.get('USERNAME')} exe={sys.executable}")

try:
    import atualizacao
    import assinatura
    from core import testes_a_distancia as td

    atualizacao.NOME_DA_TAREFA = "EditorImpressaoProvaPasta\Procurar versao nova"
    atualizacao.MARCA_DE_ABERTO = "Global\EditorImpressaoProvaPasta-programa-aberto"
    atualizacao.MARCA_DA_JANELINHA = "Local\EditorImpressaoProvaPasta-janelinha"
    td.PASTA_DAS_TAREFAS = "EditorImpressaoProvaPasta"
    td.PASTA_DOS_TESTES = str(BASE / "programdata-de-mentira" / "testes-a-distancia")
    chave = (BASE / "chave-de-mentira" / "publica.txt").read_text().strip()
    assinatura.CHAVE_PUBLICA_DO_SAMUEL = chave
    atualizacao.preparar_o_computador = lambda gerente: (anotar("preparar_o_computador (desligado na prova)"), True)[1]
    atualizacao.ha_programa_aberto = lambda: True

    class ExecutorQueSoAnota(td.Executor):
        def rodar_a_tarefa(self, nome):
            anotar(f"executor de mentira: rodar_a_tarefa({nome!r})")
            return td.Resultado(False, mensagem="executor de mentira (prova)")

        def aplicar(self, passos, senha=""):
            anotar(f"executor de mentira: aplicar({len(passos)} passos)")
            return td.Resultado(False, mensagem="executor de mentira (prova)")

        def aplicar_ja_como_administrador(self, passos):
            anotar(f"executor de mentira: aplicar_ja_como_administrador({len(passos)} passos)")
            return td.Resultado(False, mensagem="executor de mentira (prova)")

    td._executor = ExecutorQueSoAnota()

    _ao_desinstalar = atualizacao.ao_desinstalar

    def ao_desinstalar(v, portatil=atualizacao.e_portatil):
        anotar(f"GANCHO ao_desinstalar({v}) comecou")
        _ao_desinstalar(v, portatil)
        anotar("GANCHO ao_desinstalar terminou")

    atualizacao.ao_desinstalar = ao_desinstalar
    _ao_instalar = atualizacao.ao_instalar

    def ao_instalar(v, portatil=atualizacao.e_portatil):
        anotar(f"GANCHO ao_instalar({v})")
        _ao_instalar(v, portatil)

    atualizacao.ao_instalar = ao_instalar

    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    codigo = 0
    if modo == "prova-app-run":
        atualizacao._rodar_o_velopack()
        anotar("App().run() voltou")
    elif modo == "prova-versao":
        anotar(f"versao_que_roda() = {atualizacao.versao_que_roda()}")
    elif modo == "prova-portatil":
        anotar(f"e_portatil() = {atualizacao.e_portatil()}")
    elif modo == "prova-procurar-ao-abrir":
        anotar(f"procurar_ao_abrir() = {atualizacao.procurar_ao_abrir()}")
    elif modo == "prova-abrir":
        # o que main.py faz ao abrir a janela, na ordem, sem janela
        r = atualizacao.atender_linha_de_comando(sys.argv)
        anotar(f"atender_linha_de_comando -> {r}")
        anotar(f"falta_a_pergunta_do_windows() = {atualizacao.falta_a_pergunta_do_windows()}")
        anotar(f"procurar_ao_abrir() = {atualizacao.procurar_ao_abrir()}")
        anotar(f"versao_que_roda() (o aviso) = {atualizacao.versao_que_roda()}")
    else:
        # ganchos do Velopack (--veloapp-*), --procurar-atualizacao, --conferir..., ou sem argumento
        r = atualizacao.atender_linha_de_comando(sys.argv)
        anotar(f"atender_linha_de_comando -> {r}")
        codigo = r or 0
    anotar(f"FIM codigo={codigo}")
    sys.exit(codigo)
except SystemExit:
    raise
except BaseException:
    anotar("ERRO " + traceback.format_exc().replace("\n", " | "))
    sys.exit(3)
