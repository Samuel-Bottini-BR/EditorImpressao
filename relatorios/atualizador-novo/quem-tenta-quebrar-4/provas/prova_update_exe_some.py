"""Quem tenta quebrar 4 (24/11/2026): o atualizador do Velopack (`Update.exe`) some entre o download e o clique.
EXECUTADO com a biblioteca do Velopack de verdade.

Pergunta (item 3 do pedido; o caso que o terceiro "quem tenta quebrar" achou): a versão nova já baixada, o aviso na
tela, e um antivírus põe o `Update.exe` de lado. O Kaique clica "Reiniciar agora". O que ele vê agora, ao fechar, e nas
aberturas seguintes? A frase "Tente ao fechar o programa" leva a alguma coisa?

De verdade: a biblioteca `velopack` 1.2.161 (o `UpdateManager` de verdade, numa instalação de prova numa pasta minha,
com o localizador apontando para ela), a peça `core.conversa_com_o_velopack` (procurar, pendente, baixar, trocar), a
regra, o executor, o disco, as assinaturas (chave de prova), a lista de processos do Windows. De mentira: o reabrir do
programa (`lancar_solto`, só anotado: abriria o nosso .exe, que aqui não existe) e o teste rápido. O PROGRAMDATA e o
LOCALAPPDATA trocados DENTRO do Python e conferidos.
Uso: python prova_update_exe_some.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
R = RAMO / "saida_teste" / "qtq4" / "update-exe"
if R.exists():
    shutil.rmtree(R)
(R / "LocalAppData").mkdir(parents=True)
os.environ["PROGRAMDATA"] = str(R / "ProgramData")
os.environ["LOCALAPPDATA"] = str(R / "LocalAppData")
os.environ["USERNAME"] = "Kaique"
sys.path.insert(0, str(RAMO))

import atualizacao  # noqa: E402
import velopack  # noqa: E402
import versao  # noqa: E402
from core import conversa_com_o_velopack as conversa  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402
from core import windows  # noqa: E402
from tests.ajudante_do_atualizador import PUBLICA, WindowsFalso, _publicar, pacote_de_prova  # noqa: E402

assert str(atualizacao.pasta_do_estado()).startswith(str(R))
PACOTE = versao.ID_DO_PACOTE
RAIZ, FONTE = R / "instalado", R / "fonte"
LOC = velopack.VelopackLocatorConfig(RAIZ, RAIZ / "Update.exe", RAIZ / "packages", RAIZ / "current" / "sq.version",
                                     RAIZ / "current", False)


class VelopackDeVerdade:
    """A peça de verdade, com o localizador da instalação de prova (o programa de verdade acha o dele sozinho)."""

    def procurar(self, endereco):
        return conversa.procurar(endereco, LOC)

    def pendente(self, endereco):
        return conversa.pendente(endereco, LOC)

    def baixar(self, endereco, v):
        return conversa.baixar(endereco, v, LOC)

    def pacote_da_versao(self, *a):
        return conversa.pacote_da_versao(*a)

    def trocar(self, endereco, v, reabrir, argumentos):
        # A troca de verdade abriria o Update.exe; aqui ele já sumiu, e é a biblioteca que recusa (como no programa).
        vp = conversa._gerente(endereco, permitir_voltar=True, localizador=LOC)     # o mesmo da peça, com o LOC
        vp.wait_exit_then_apply_updates(v.pedido, silent=False, restart=bool(reabrir),
                                        restart_args=[str(a) for a in argumentos])


class WindowsMeio(WindowsFalso):
    """A lista de processos e o atualizador rodando, de verdade; o reabrir só anotado."""

    programas_rodando_de = staticmethod(windows.programas_rodando_de)
    numero_deste_processo = staticmethod(windows.numero_deste_processo)
    atualizador_do_velopack_rodando = staticmethod(windows.atualizador_do_velopack_rodando)


def executor(win) -> atualizacao.Atualizacao:
    return atualizacao.Atualizacao(windows=win, velopack=VelopackDeVerdade(), raiz=RAIZ,
                                   fonte=atualizacao.Fonte(str(FONTE)), por_tras=lambda t: t(),
                                   pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                   motor_no_lugar=lambda m=None: True, teste=lambda: (True, ""),
                                   chave_publica=PUBLICA)


def texto(ef) -> str:
    if isinstance(ef, fases.MostrarFalha):
        return "[Atualização] " + atualizacao.frase_da_falha(ef.tipo, ef.motivo_da_tela)
    return type(ef).__name__


def tentar(nome, f) -> str:
    try:
        return f"{nome}: {f()!r}"
    except Exception as erro:  # noqa: BLE001
        return f"{nome}: ERRO {erro}"


def main() -> None:
    resultado: dict = {}
    (RAIZ / "current").mkdir(parents=True)
    (RAIZ / "packages").mkdir()
    (RAIZ / "current" / "sq.version").write_text(
        f'<?xml version="1.0"?><package><metadata><id>{PACOTE}</id><version>1.1.0</version><title>E</title>'
        '<authors>x</authors><description>x</description><mainExe>EditorImpressao.exe</mainExe></metadata>'
        '</package>', encoding="utf-8")
    (RAIZ / "Update.exe").write_bytes(b"MZ")           # existe (a biblioteca só confere que existe)
    c11, c12 = pacote_de_prova("1.1.0"), pacote_de_prova("1.2.0")
    _publicar(FONTE, "1.1.0", c11)
    _publicar(FONTE, "1.2.0", c12)
    for v, c in (("1.1.0", c11), ("1.2.0", c12)):
        (FONTE / atualizacao.nome_do_pacote(v)).write_bytes(c)
    # o índice que o Velopack lê da pasta (o publicar grava releases.win.json) precisa de SHA1 também
    indice = json.loads((FONTE / "releases.win.json").read_text(encoding="utf-8"))
    for a in indice["Assets"]:
        dado = (FONTE / a["FileName"]).read_bytes()
        a["SHA1"] = hashlib.sha1(dado).hexdigest()
    (FONTE / "releases.win.json").write_text(json.dumps(indice), encoding="utf-8")
    versao.VERSAO = "1.1.0"
    win = WindowsMeio()
    win._pasta_de_troca = R / "troca"
    a = executor(win)
    a.abrir([])
    tela: list = []
    a.ligar_a_tela(tela.append)
    resultado["1. a abertura com o Update.exe no lugar"] = {
        "tela": [texto(e) for e in tela], "baixado em packages": sorted(p.name for p in (RAIZ / "packages").iterdir())}
    (RAIZ / "Update.exe").unlink()                     # o antivírus pôs de lado
    tela.clear()
    a.evento(fases.Escolheu(True))                      # "Reiniciar agora"
    resultado["2. o Update.exe some; o clique em Reiniciar agora"] = {
        "tela (antes de a janela fechar)": [texto(e) for e in tela], "fase": a.estado.fase.value}
    a.evento(fases.JanelaFechou(True))                  # a janela fechou (a ponte da tela faria isso)
    resultado["3. depois de a janela fechar"] = {
        "fase": a.estado.fase.value, "reaberturas pedidas": win.reaberturas, "bilhete": atualizacao.ler_estado()}
    for n in (1, 2):
        win2 = WindowsMeio()
        win2._pasta_de_troca = R / "troca"
        b = executor(win2)
        b.abrir([])
        tela2: list = []
        b.ligar_a_tela(tela2.append)
        b.evento(fases.Fechando())
        resultado[f"4.{n} a abertura seguinte (a reaberta) e o fechar"] = {
            "tela": [texto(e) for e in tela2], "fase depois de fechar": b.estado.fase.value,
            "a peça do Velopack agora": [tentar("pendente", lambda: conversa.pendente(str(FONTE), LOC)),
                                         tentar("procurar", lambda: conversa.procurar(str(FONTE), LOC))]}
    resultado["5. o registro"] = atualizacao.caminho_do_registro().read_text(encoding="utf-8").splitlines()[-12:]
    t = json.dumps(resultado, ensure_ascii=False, indent=1, default=str)
    Path(__file__).with_name("prova_update_exe_some-resultado.txt").write_text(t, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(t)


if __name__ == "__main__":
    main()
