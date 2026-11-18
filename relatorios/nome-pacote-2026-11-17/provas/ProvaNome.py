"""ProvaNome: programa de mentira para repetir a prova de 17/11 com o nome novo (D-763).

Copia do ProvaPasta.py da prova de 17/11 (ramo velopack-pasta-2026-11-17,
relatorios/velopack-pasta-2026-11-17/provas/ProvaPasta.py), com tres trocas:
- BASE: a pasta desta prova (D:\\agente_temp_testes\\nome-pacote\\prova);
- os nomes das tarefas e marcas do Windows: EditorImpressaoProvaNome\\...;
- leva o atualizacao.py/versao.py da worktree nome-pacote (o codigo NOVO).
O nome do pacote NAO e escrito aqui: o pacote e montado por montar_e_provar.py
com o nome tirado da mesma regra do programa (versao.ID_DO_PACOTE + "Prova").
Chama as MESMAS funcoes que o Editor chama ao abrir e que o ajudante chama ao
atualizar. Seguranca (igual a de 17/11):
- PROGRAMDATA e LOCALAPPDATA (variaveis) -> pastas de mentira no D:
  (o Velopack nao le a variavel: pergunta ao Windows);
- tarefas do Windows com nome de mentira (nao existem: o schtasks so falha);
- a peca que fala com o Windows nos testes a distancia -> uma que so anota;
- preparar_o_computador -> nada (nao mexe no Visual C++ nem no Inno de verdade);
- a chave publica -> a de mentira de 17/11 (a do Samuel nao e usada);
- "programa aberto" -> sempre sim (nunca pede ao Velopack para trocar a pasta).
"""
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

BASE = Path(r"D:\agente_temp_testes\nome-pacote\prova")
CHAVE_DE_MENTIRA = Path(r"D:\agente_temp_testes\velopack-pasta\chave-de-mentira\publica.txt")
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

    atualizacao.NOME_DA_TAREFA = "EditorImpressaoProvaNome\\Procurar versao nova"
    atualizacao.MARCA_DE_ABERTO = "Global\\EditorImpressaoProvaNome-programa-aberto"
    atualizacao.MARCA_DA_JANELINHA = "Local\\EditorImpressaoProvaNome-janelinha"
    td.PASTA_DAS_TAREFAS = "EditorImpressaoProvaNome"
    td.PASTA_DOS_TESTES = str(BASE / "programdata-de-mentira" / "testes-a-distancia")
    assinatura.CHAVE_PUBLICA_DO_SAMUEL = CHAVE_DE_MENTIRA.read_text().strip()
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
    else:
        # ganchos do Velopack (--veloapp-*), --procurar-atualizacao, ou sem argumento
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
