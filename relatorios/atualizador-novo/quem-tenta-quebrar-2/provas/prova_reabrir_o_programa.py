"""Prova EXECUTADA (quem tenta quebrar, volta 2): os caminhos que levam ao efeito ReabrirOPrograma ("Reiniciar agora"
cuja troca não pôde ser pedida DEPOIS de a janela fechar), pelo executor de verdade, a regra de verdade, o estado.json
de verdade (PROGRAMDATA desviado), um pacote de verdade em <raiz>\\packages (zip com o motor-exigido.json) e a lista de
processos de verdade do Windows. De mentira: só o Velopack da biblioteca (trocar), o motor (sempre no lugar), a tela
(a ponte que fecha a janela devolve "fechou") e o lançar do programa de novo (anotado, não lançado).

Cada caso: o que a conferência ANTES de fechar disse, o que a segunda conferência (dentro de trocar_para) disse, se o
programa foi reaberto, e o que fica.
  R2  o estado.json preso por outro processo (aberto sem deixar apagar, como um antivírus ou outra conta o lendo)
  R3  outra janela do programa aberta nos segundos do fechar (um processo de verdade de dentro de current\\)
  R4  o pacote trocado nos segundos do fechar
  R6  o Velopack não aceita o pedido
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path

RAMO = Path(r"D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo")
R = Path(r"D:\programas\EditorImpressao\rascunho-qtq2\reabrir")
RAIZ = R / "raiz"
SEM_JANELA = 0x08000000
os.environ["PROGRAMDATA"] = str(R / "pd")
os.environ["LOCALAPPDATA"] = str(R / "local")
for p in (RAIZ / "current", RAIZ / "packages", R / "local"):
    p.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(RAMO))
import atualizacao  # noqa: E402
import versao  # noqa: E402
from core import conversa_com_o_velopack as conversa  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402
from core import windows as windows_de_verdade  # noqa: E402

versao.VERSAO = "1.1.0"
PY = sys.base_prefix  # a instalação do Python por trás da .venv
OUTRA = RAIZ / "current" / "EditorImpressao.exe"
if not OUTRA.exists():
    OUTRA.write_bytes(Path(PY, "pythonw.exe").read_bytes())
    for dll in ("python314.dll", "python3.dll", "vcruntime140.dll", "vcruntime140_1.dll"):
        (RAIZ / "current" / dll).write_bytes(Path(PY, dll).read_bytes())

PACOTE = RAIZ / "packages" / "EditorImpressaoPrograma-1.2.0-full.nupkg"


def montar_pacote():
    with zipfile.ZipFile(PACOTE, "w") as z:
        z.writestr("lib/app/motor-exigido.json", json.dumps({"versao": 1}))
    return hashlib.sha256(PACOTE.read_bytes()).hexdigest()


class Windows:
    """A peça de verdade, menos o lançar de novo (anotado)."""
    def __init__(self):
        self.reaberto = []

    def __getattr__(self, nome):
        return getattr(windows_de_verdade, nome)

    def lancar_solto(self, comando, sinal, espera_s):
        self.reaberto.append(comando)
        return windows_de_verdade._certo()


class Velopack:
    recusar = False

    def trocar(self, endereco, v, reabrir, argumentos):
        if self.recusar:
            raise conversa.ErroDoVelopack("trocar: o atualizador não abriu (de mentira)")


def caso(nome, no_fechar=None, antes=None, velopack_recusa=False):
    atualizacao.gravar_estado({})
    soma = montar_pacote()
    w, vp = Windows(), Velopack()
    vp.recusar = velopack_recusa
    a = atualizacao.Atualizacao(windows=w, velopack=vp, raiz=RAIZ, por_tras=lambda f: f(),
                                pasta_grava=lambda r: True, garantir_motor=lambda: True, motor_no_lugar=lambda v: True)
    a._achada = conversa.VersaoDoVelopack("EditorImpressaoPrograma", "1.2.0", PACOTE.name, soma, PACOTE.stat().st_size)
    a._somas_assinadas["1.2.0"] = soma
    a._estado = fases.Estado(fase=fases.Fase.PRONTA, versao="1.1.0", nova="1.2.0")
    tela = []
    conferencias = []
    original = a.conferencia_da_troca

    def conferencia(v):
        c = original(v)
        conferencias.append({"pode": c.pode, "motivo": c.motivo, "recusada": c.recusada,
                             "outra_janela": c.outra_janela})
        return c
    a.conferencia_da_troca = conferencia

    def mostrar(ef):
        tela.append(type(ef).__name__)
        if isinstance(ef, fases.FecharJanela):
            if no_fechar:
                no_fechar()
            a.evento(fases.JanelaFechou(True))
    a.ligar_a_tela(mostrar)
    segurar = antes() if antes else None
    try:
        a.evento(fases.Escolheu(True))
    finally:
        if segurar is not None:
            segurar.kill()
            segurar.wait()
    seguinte = atualizacao.Atualizacao(windows=w, velopack=vp, raiz=RAIZ, por_tras=lambda f: None,
                                       pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                       motor_no_lugar=lambda v: True)
    seguinte.abrir([])
    return {"caso": nome, "conferencias (antes de fechar, dentro de trocar_para)": conferencias, "tela": tela,
            "reaberto": bool(w.reaberto), "fase no fim": a.estado.fase.value, "estado.json": atualizacao.ler_estado(),
            "a abertura reaberta mostra": [f"{e.tipo}: {atualizacao.FRASES_DA_FALHA[e.tipo]}"
                                           for e in seguinte._fila_da_tela if isinstance(e, fases.MostrarFalha)]}


def segurar_o_estado():
    alvo = atualizacao.pasta_do_estado() / "estado.json"
    p = subprocess.Popen([sys.executable, "-c", f"f=open(r'{alvo}','rb'); import time; time.sleep(60)"],
                         creationflags=SEM_JANELA)
    time.sleep(1.0)
    return p


outras = []


def abrir_outra_janela():
    """Como o atalho: o programa é aberto por um processo que sai logo (o `Update.exe start`), não por este."""
    lancador = (f"import subprocess,os; subprocess.Popen([r'{OUTRA}', '-c', 'import time; time.sleep(20)'], "
                f"env={{**os.environ, 'PYTHONHOME': r'{PY}'}}, creationflags={SEM_JANELA})")
    subprocess.run([sys.executable, "-c", lancador], creationflags=SEM_JANELA, timeout=30)
    time.sleep(0.8)
    outras.extend(windows_de_verdade.programas_rodando_de(RAIZ / "current") or [])


def trocar_o_pacote():
    with open(PACOTE, "ab") as f:
        f.write(b"x")


resultado = [caso("R2 estado.json preso", antes=segurar_o_estado),
             caso("R4 pacote trocado nos segundos do fechar", no_fechar=trocar_o_pacote),
             caso("R6 o Velopack não aceita o pedido", velopack_recusa=True),
             caso("R3 outra janela aberta nos segundos do fechar", no_fechar=abrir_outra_janela)]
with open(atualizacao.caminho_do_registro(), encoding="utf-8") as f:
    resultado.append({"registro": [l.split(" | ", 2)[2].strip() for l in f]})
for pid, _ in outras:
    subprocess.run(['taskkill', '/PID', str(pid), '/F'], capture_output=True)
texto = json.dumps(resultado, ensure_ascii=False, indent=1)
Path(__file__).with_name("prova_reabrir_o_programa-resultado.txt").write_text(texto, encoding="utf-8")
print(texto)
