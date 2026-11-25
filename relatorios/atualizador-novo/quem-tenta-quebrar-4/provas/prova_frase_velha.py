"""Quem tenta quebrar 4 (24/11/2026): a frase do "Sim" ao fechar (D-858/D-864) aparece depois de a troca ter dado
certo. EXECUTADO.

O caso da própria D-858: o Kaique tem duas janelas do programa abertas, as duas com a versão nova esperando. Fecha a
primeira e responde "Sim": não troca (há outra janela), e a frase da D-864 fica guardada para a abertura seguinte. Fecha
a segunda e responde "Sim": agora troca. Na abertura seguinte, já na versão nova, o que aparece?

De verdade: a regra, o executor (`atualizacao.Atualizacao`), o disco (o bilhete, as marcas, a última boa, os "vistos"),
as assinaturas (com a chave de prova) e a LISTA DE PROCESSOS DO WINDOWS (`core.windows.programas_rodando_de`), com a
"outra janela" sendo um processo de verdade aberto de dentro de `current\\` (uma cópia do ping.exe do Windows, sem
janela). De mentira: o pedido ao Velopack (só anotado; a troca de verdade e a reabertura estão nas provas da volta 4) e o
teste rápido (passa). O PROGRAMDATA e o LOCALAPPDATA trocados DENTRO do Python e conferidos.
Uso: python prova_frase_velha.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
R = RAMO / "saida_teste" / "qtq4" / "frase-velha"
if R.exists():
    shutil.rmtree(R)
(R / "LocalAppData").mkdir(parents=True)
os.environ["PROGRAMDATA"] = str(R / "ProgramData")
os.environ["LOCALAPPDATA"] = str(R / "LocalAppData")
os.environ["USERNAME"] = "Kaique"
sys.path.insert(0, str(RAMO))

import atualizacao  # noqa: E402
import versao  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402
from core import windows  # noqa: E402
from tests.ajudante_do_atualizador import PUBLICA, VelopackFalso, _publicar, pacote_de_prova  # noqa: E402

assert str(atualizacao.pasta_do_estado()).startswith(str(R))


class WindowsDeVerdade:
    """A peça do Windows de verdade para a lista de processos; o resto não é usado nesta prova."""

    DISSE_NAO = windows.DISSE_NAO
    caminho_conferido = staticmethod(windows.caminho_conferido)
    programas_rodando_de = staticmethod(windows.programas_rodando_de)
    numero_deste_processo = staticmethod(windows.numero_deste_processo)
    atualizador_do_velopack_rodando = staticmethod(windows.atualizador_do_velopack_rodando)


def executor(raiz: Path, fonte: Path, vp) -> atualizacao.Atualizacao:
    return atualizacao.Atualizacao(windows=WindowsDeVerdade(), velopack=vp, raiz=raiz,
                                   fonte=atualizacao.Fonte(str(fonte)), por_tras=lambda t: t(),
                                   pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                   motor_no_lugar=lambda m=None: True, teste=lambda: (True, ""),
                                   chave_publica=PUBLICA)


def tela_de(a) -> list:
    tela: list = []
    a.ligar_a_tela(tela.append)
    return tela


def texto(ef) -> str:
    if isinstance(ef, fases.MostrarFalha):
        return "[Atualização] " + atualizacao.frase_da_falha(ef.tipo, ef.motivo_da_tela)
    return type(ef).__name__


def abrir_janela(raiz, fonte, publicada):
    """Uma janela da 1.1.0 abre e acha a 1.2.0 (o aviso)."""
    vp = VelopackFalso(raiz, publicada, "", {})
    a = executor(raiz, fonte, vp)
    a.abrir([])
    return a, vp, tela_de(a)


def fechar_com_sim(a, vp, tela) -> dict:
    """"Depois", fechar, "Sim"."""
    a.evento(fases.Escolheu(False))
    a.evento(fases.Fechando())
    a.evento(fases.RespondeuAoFechar(True))
    return {"tela": [texto(e) for e in tela], "pedidos ao Velopack": [c[0] for c in vp.chamadas],
            "fase": a.estado.fase.value, "bilhete depois": atualizacao.ler_estado()}


def main() -> None:
    resultado: dict = {}
    raiz, fonte = R / "raiz", R / "fonte"
    (raiz / "current").mkdir(parents=True)
    conteudo_11, conteudo_12 = pacote_de_prova("1.1.0"), pacote_de_prova("1.2.0")
    _publicar(fonte, "1.1.0", conteudo_11)
    publicada = _publicar(fonte, "1.2.0", conteudo_12)
    # A 1.1.0 é a última boa (pacote e assinatura guardados); a 1.2.0 já está baixada em packages\\.
    (raiz / "packages").mkdir()
    (raiz / "packages" / atualizacao.nome_do_pacote("1.2.0")).write_bytes(conteudo_12)
    ub = atualizacao.pasta_da_ultima_boa(raiz)
    ub.mkdir()
    (ub / atualizacao.nome_do_pacote("1.1.0")).write_bytes(conteudo_11)
    nome_ass = f"{versao.ID_DO_PACOTE}-1.1.0.assinatura"
    shutil.copy(fonte / nome_ass, ub / nome_ass)
    versao.VERSAO = "1.1.0"
    # A segunda janela: um processo de verdade de dentro de current\\.
    shutil.copy(Path(os.environ["SystemRoot"]) / "System32" / "PING.EXE", raiz / "current" / "EditorImpressao.exe")
    # Aberta por um "cmd /c start" que sai logo: assim ela NAO e da familia deste processo (como a segunda janela do
    # Kaique, aberta pelo atalho), e a peca do Windows a conta como "outra janela".
    subprocess.run(["cmd", "/c", "start", "", "/b", str(raiz / "current" / "EditorImpressao.exe"), "-n", "60",
                    "127.0.0.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    time.sleep(1.5)
    vista = windows.programas_rodando_de(raiz / "current", menos_a_familia_de=windows.numero_deste_processo())
    resultado["0. a outra janela, vista pela peca do Windows"] = vista
    # As duas janelas abrem ANTES de qualquer "Sim" (as duas mostram o aviso). O processo da segunda e o ping.
    janela_b = abrir_janela(raiz, fonte, publicada)
    janela_a = abrir_janela(raiz, fonte, publicada)
    try:
        resultado["1. a primeira janela: Depois, fechar, Sim (a outra janela aberta)"] = fechar_com_sim(*janela_a)
    finally:
        for pid, _ in vista or []:
            os.kill(pid, 9)
    time.sleep(0.5)
    resultado["2. a segunda janela (aberta antes): Depois, fechar, Sim (agora sozinha)"] = fechar_com_sim(*janela_b)
    # O Velopack troca (a troca de verdade está provada à parte) e reabre a 1.2.0 sem janela, com o pedido.
    versao.VERSAO = "1.2.0"
    vp = VelopackFalso(raiz, None, "", {})
    a = executor(raiz, fonte, vp)
    saida = a.abrir([atualizacao.ARG_CONFERIR_NOVA, "1.1.0", "1.2.0", atualizacao.ARG_SEM_JANELA])
    resultado["3. a reabertura sem janela da 1.2.0 (o teste passa)"] = {
        "saida": saida, "ultima boa": atualizacao.ler_ultima_boa(raiz),
        "aprovada": atualizacao.tem_marca(raiz, atualizacao.MARCA_APROVADA, "1.2.0"),
        "bilhete": atualizacao.ler_estado()}
    vp = VelopackFalso(raiz, None, "", {})
    a = executor(raiz, fonte, vp)
    a.abrir([])
    resultado["4. a abertura seguinte, pelo atalho, JÁ NA 1.2.0"] = {
        "versao que roda": versao.VERSAO, "o que aparece na tela": [texto(e) for e in tela_de(a)]}
    t = json.dumps(resultado, ensure_ascii=False, indent=1, default=str)
    Path(__file__).with_name("prova_frase_velha-resultado.txt").write_text(t, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(t)


if __name__ == "__main__":
    main()
