"""Volta 5 (25/11/2026), M2 (D-870): o atualizador do Velopack (`Update.exe`) some e depois volta. EXECUTADO com a
biblioteca do Velopack de verdade.

Pergunta: com a versão nova baixada e o aviso na tela, o `Update.exe` é posto de lado (um antivírus). O que o Kaique vê
no "Reiniciar agora", no "Sim" ao fechar e nas aberturas seguintes? E quando o `Update.exe` volta, a versão é oferecida
de novo?

De verdade: a biblioteca `velopack` 1.2.161 (o `UpdateManager` de verdade, numa instalação de prova numa pasta minha,
com o localizador apontando para ela: procurar, pendente, baixar), a peça `core.conversa_com_o_velopack`, a regra, o
executor, o disco, as assinaturas (chave de prova), a lista de processos do Windows. De mentira: a caixa do Windows (só
anota o texto; a caixa de verdade está em `prova_caixa_de_verdade.py`), o reabrir do programa e o teste rápido. A troca
nunca é pedida ao Velopack nesta prova (o `Update.exe` daqui é um arquivo de dois bytes: a biblioteca só confere que
ele existe). O PROGRAMDATA e o LOCALAPPDATA trocados DENTRO do Python e conferidos com `assert` antes de tudo.
Adaptada de `quem-tenta-quebrar-4/provas/prova_update_exe_some.py` (a mesma instalação de prova).
Uso: python prova_update_exe_volta.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

RAMO = Path(__file__).resolve().parents[3]
R = RAMO / "saida_teste" / "v5" / "update-exe"
if R.exists():
    shutil.rmtree(R)
(R / "LocalAppData").mkdir(parents=True)
os.environ["PROGRAMDATA"] = str(R / "ProgramData")
os.environ["LOCALAPPDATA"] = str(R / "LocalAppData")
os.environ["USERNAME"] = "Kaique"
sys.path.insert(0, str(RAMO))

import atualizacao  # noqa: E402
import historico  # noqa: E402
import velopack  # noqa: E402
import versao  # noqa: E402
from core import conversa_com_o_velopack as conversa  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402
from core import windows  # noqa: E402
from tests.ajudante_do_atualizador import PUBLICA, WindowsFalso, _publicar, pacote_de_prova  # noqa: E402

assert str(atualizacao.pasta_do_estado()).startswith(str(R)), atualizacao.pasta_do_estado()
assert str(historico.pasta_de_dados()).startswith(str(R)), historico.pasta_de_dados()
PACOTE = versao.ID_DO_PACOTE
RAIZ, FONTE = R / "instalado", R / "fonte"
LOC = velopack.VelopackLocatorConfig(RAIZ, RAIZ / "Update.exe", RAIZ / "packages", RAIZ / "current" / "sq.version",
                                     RAIZ / "current", False)


class VelopackDeVerdade:
    """A peça de verdade, com o localizador da instalação de prova (o programa de verdade acha o dele sozinho)."""

    def __init__(self):
        self.pedidos: list[str] = []

    def procurar(self, endereco):
        self.pedidos.append("procurar")
        return conversa.procurar(endereco, LOC)

    def pendente(self, endereco):
        self.pedidos.append("pendente")
        return conversa.pendente(endereco, LOC)

    def baixar(self, endereco, v):
        self.pedidos.append("baixar")
        return conversa.baixar(endereco, v, LOC)

    def pacote_da_versao(self, *a):
        return conversa.pacote_da_versao(*a)

    def trocar(self, endereco, v, reabrir, argumentos):
        self.pedidos.append("trocar")
        raise AssertionError("a troca não pode ser pedida nesta prova")


class WindowsMeio(WindowsFalso):
    """A lista de processos e o atualizador rodando, de verdade; a caixa do Windows e o reabrir, só anotados."""

    programas_rodando_de = staticmethod(windows.programas_rodando_de)
    numero_deste_processo = staticmethod(windows.numero_deste_processo)
    atualizador_do_velopack_rodando = staticmethod(windows.atualizador_do_velopack_rodando)

    def __init__(self):
        super().__init__(pasta_de_troca=R / "troca")
        self.caixas: list[str] = []

    def mostrar_caixa_do_windows(self, titulo, texto):
        self.caixas.append(f"[{titulo}] {texto}")
        return windows.Resposta(windows.DEU_CERTO)


def abertura():
    """Uma abertura do programa instalado (o executor de verdade), com a tela anotada."""
    win, vp = WindowsMeio(), VelopackDeVerdade()
    a = atualizacao.Atualizacao(windows=win, velopack=vp, raiz=RAIZ, fonte=atualizacao.Fonte(str(FONTE)),
                                por_tras=lambda t: t(), pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                motor_no_lugar=lambda m=None: True, teste=lambda: (True, ""), chave_publica=PUBLICA)
    saida = a.abrir([])
    tela: list = []
    a.ligar_a_tela(tela.append)
    return a, win, vp, tela, saida


def texto(ef) -> str:
    if isinstance(ef, fases.MostrarFalha):
        return "[Atualização] " + atualizacao.frase_da_falha(ef.tipo, ef.motivo_da_tela)
    return type(ef).__name__


def tentar(nome, f) -> str:
    try:
        return f"{nome}: {f()!r}"
    except Exception as erro:  # noqa: BLE001
        return f"{nome}: ERRO {str(erro)[:160]}"


def main() -> None:
    resultado: dict = {}
    (RAIZ / "current").mkdir(parents=True)
    (RAIZ / "packages").mkdir()
    (RAIZ / "current" / "sq.version").write_text(
        f'<?xml version="1.0"?><package><metadata><id>{PACOTE}</id><version>1.1.0</version><title>E</title>'
        '<authors>x</authors><description>x</description><mainExe>EditorImpressao.exe</mainExe></metadata>'
        '</package>', encoding="utf-8")
    (RAIZ / "Update.exe").write_bytes(b"MZ")
    c11, c12 = pacote_de_prova("1.1.0"), pacote_de_prova("1.2.0")
    _publicar(FONTE, "1.1.0", c11)
    _publicar(FONTE, "1.2.0", c12)
    for v, c in (("1.1.0", c11), ("1.2.0", c12)):
        (FONTE / atualizacao.nome_do_pacote(v)).write_bytes(c)
    indice = json.loads((FONTE / "releases.win.json").read_text(encoding="utf-8"))
    for item in indice["Assets"]:
        item["SHA1"] = hashlib.sha1((FONTE / item["FileName"]).read_bytes()).hexdigest()
    (FONTE / "releases.win.json").write_text(json.dumps(indice), encoding="utf-8")
    versao.VERSAO = "1.1.0"

    a, win, vp, tela, _ = abertura()
    resultado["1. a abertura com o Update.exe no lugar"] = {
        "tela": [texto(e) for e in tela], "pedidos à biblioteca": vp.pedidos,
        "em packages": sorted(p.name for p in (RAIZ / "packages").iterdir() if p.suffix == ".nupkg")}
    (RAIZ / "Update.exe").unlink()                     # o antivírus pôs de lado
    tela.clear()
    a.evento(fases.Escolheu(True))                      # "Reiniciar agora"
    resultado["2. o Update.exe some; o clique em Reiniciar agora"] = {
        "tela (a janela continua aberta)": [texto(e) for e in tela], "fase": a.estado.fase.value}
    tela.clear()
    a.evento(fases.Fechando())
    resultado["3. fechar o programa depois"] = {"tela": [texto(e) for e in tela], "fase": a.estado.fase.value,
                                                "a troca foi pedida?": "trocar" in vp.pedidos}

    b, win_b, vp_b, tela_b, _ = abertura()
    b.evento(fases.Fechando())
    resultado["4. a abertura seguinte, ainda sem o Update.exe"] = {
        "caixas do Windows": win_b.caixas, "tela": [texto(e) for e in tela_b],
        "fase depois de fechar": b.estado.fase.value,
        "a biblioteca agora": [tentar("pendente", lambda: conversa.pendente(str(FONTE), LOC)),
                               tentar("procurar", lambda: conversa.procurar(str(FONTE), LOC))]}

    (RAIZ / "Update.exe").write_bytes(b"MZ")           # voltou (o antivírus devolveu; ou o Samuel reinstalou)
    c, win_c, vp_c, tela_c, _ = abertura()
    resultado["5. o Update.exe volta: a abertura seguinte"] = {
        "tela": [texto(e) for e in tela_c], "caixas do Windows": win_c.caixas, "pedidos à biblioteca": vp_c.pedidos,
        "a biblioteca": [tentar("pendente", lambda: conversa.pendente(str(FONTE), LOC))]}

    # O "Sim" ao fechar sem o Update.exe: a frase própria guardada, e a abertura seguinte a mostra antes da janela.
    tela_c.clear()
    (RAIZ / "Update.exe").unlink()
    c.evento(fases.Escolheu(False))
    c.evento(fases.Fechando())
    c.evento(fases.RespondeuAoFechar(True))
    resultado["6. 'Depois', fechar, 'Sim', sem o Update.exe"] = {
        "a troca foi pedida?": "trocar" in vp_c.pedidos, "bilhete": atualizacao.ler_estado()}
    d, win_d, _, tela_d, _ = abertura()
    resultado["7. a abertura seguinte"] = {"caixas do Windows (antes da janela)": win_d.caixas,
                                          "tela": [texto(e) for e in tela_d]}
    resultado["8. o registro (as últimas linhas)"] = atualizacao.caminho_do_registro().read_text(
        encoding="utf-8").splitlines()[-14:]
    t = json.dumps(resultado, ensure_ascii=False, indent=1, default=str)
    Path(__file__).with_name("prova_update_exe_volta-resultado.txt").write_text(t, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(t)


if __name__ == "__main__":
    main()
