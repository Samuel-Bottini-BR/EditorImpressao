"""Quem tenta quebrar 5 (25/11/2026): casos da tabela das falhas que o escritor não rodou, EXECUTADOS neste Windows.

De verdade: a regra (`core/fases_da_atualizacao.py`), o executor (`atualizacao.Atualizacao`), o disco (bilhete,
vistos, marcas, `ultima-boa`, `packages`), as assinaturas (chave de prova). De mentira: a borda (a peça do Windows e a do
Velopack do `tests/ajudante_do_atualizador.py`, que só anotam; a caixa do Windows anota e "clica OK"). A caixa de
verdade e o Velopack de verdade estão nas outras provas desta pasta.

O PROGRAMDATA e o LOCALAPPDATA são trocados DENTRO deste processo, para uma pasta do projeto, e conferidos com assert.
Uso: python prova_casos.py <raiz do código a provar> <pasta de trabalho>
(a raiz pode ser uma cópia `git archive` de outro commit, para saber se um defeito já existia antes).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CODIGO, BASE = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
BASE.mkdir(parents=True, exist_ok=True)
os.environ["PROGRAMDATA"] = str(BASE / "ProgramData")
os.environ["LOCALAPPDATA"] = str(BASE / "LocalAppData")
os.environ["USERNAME"] = "Kaique"
sys.path.insert(0, str(CODIGO))

import atualizacao  # noqa: E402
import historico  # noqa: E402
import versao  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402
from tests.ajudante_do_atualizador import NOVA, Prova  # noqa: E402

assert str(atualizacao.pasta_do_estado()).startswith(str(BASE)), atualizacao.pasta_do_estado()
assert str(historico.pasta_de_dados()).startswith(str(BASE)), historico.pasta_de_dados()
assert str(atualizacao.caminho_do_registro()).startswith(str(BASE))

sys.stdout.reconfigure(encoding="utf-8")
RES: dict = {"codigo": str(CODIGO)}
PROVA = getattr(Prova.__init__, "__code__").co_varnames
CAIXA = "caixa_de_verdade" in PROVA


def _limpo(nome: str) -> Path:
    """Uma pasta nova por caso, e um bilhete e vistos novos (cada caso é uma instalação e uma conta)."""
    p = BASE / nome
    import shutil
    for sub in (p, BASE / "ProgramData", BASE / "LocalAppData"):
        if sub.exists():
            shutil.rmtree(sub)
    (BASE / "LocalAppData").mkdir(parents=True)
    return p


def _prova(pasta: Path, **kw) -> Prova:
    if CAIXA:
        kw.setdefault("caixa_de_verdade", True)
    return Prova(pasta, **kw)


def _viu(p: Prova) -> list[str]:
    """O que o Kaique viu nesta abertura: as caixas do Windows (texto) e o que foi para a janela (tipo e texto)."""
    vistas = [f"CAIXA DO WINDOWS: {t}" for _, t in getattr(p.win, "caixas", [])]
    for ef in p.tela:
        if isinstance(ef, fases.MostrarFalha):
            vistas.append(f"JANELA: {atualizacao.frase_da_falha(ef.tipo, ef.motivo_da_tela)}")
        else:
            vistas.append(f"JANELA: {type(ef).__name__}")
    return vistas


# ---- L1: o Velopack não troca duas vezes para a MESMA versão ("Reiniciar agora", arquivo preso), em dias diferentes
def l1():
    versao.VERSAO = "7.0.0"
    pasta = _limpo("L1")
    out = []
    for vez in (1, 2):
        p = _prova(pasta / f"vez{vez}", publicar_nova=False)
        p.abrir(atualizacao.ARG_CONFERIR_NOVA, "7.0.0", "7.0.1")
        p.ligar_a_tela()
        out.append({"vez": vez, "o Kaique viu": _viu(p)})
    RES["L1 a troca que o Velopack não fez, duas vezes para a mesma versão"] = out


# ---- L2: uma marca .sem-volta de uma versão de prova anterior (volta 4) ficou na pasta da última boa
def l2():
    versao.VERSAO = "0.1.0"
    pasta = _limpo("L2")
    p = _prova(pasta, ultima_boa="0.1.0")
    boa = atualizacao.pasta_da_ultima_boa(p.raiz)
    (boa / f"{versao.ID_DO_PACOTE}-0.1.0.sem-volta").write_bytes(b"")
    (boa / f"{versao.ID_DO_PACOTE}-9.9.0.sem-volta").write_bytes(b"")
    p.abrir()
    p.ligar_a_tela()
    RES["L2 marca .sem-volta velha no disco"] = {
        "ultima boa lida": atualizacao.ler_ultima_boa(p.raiz), "fase": p.atual.estado.fase.value,
        "pedidos ao Velopack": p.vp.nomes(), "o Kaique viu": _viu(p)}


# ---- L3: a reprovada (primeira abertura), a abertura seguinte e a correção publicada
def l3():
    versao.VERSAO = "9.9.0"
    pasta = _limpo("L3")
    out = []
    p = _prova(pasta / "a1", teste=(False, "de prova"), ultima_boa="0.1.0", publicar_nova=False)
    p.pacote_em_packages("9.9.0")
    p.abrir(atualizacao.ARG_CONFERIR_NOVA, "0.1.0", "9.9.0")
    out.append({"abertura": "1 (reaberta depois da troca)", "fase": p.atual.estado.fase.value,
                "pedidos ao Velopack": p.vp.nomes(), "o Kaique viu antes da janela": _viu(p),
                "reprovadas": atualizacao.ler_estado().get("reprovadas")})
    p2 = _prova(pasta / "a2", teste=(False, "de prova"), ultima_boa="0.1.0", publicar_nova=False)
    p2.pacote_em_packages("9.9.0")
    testes = []
    p2.atual._teste = lambda: testes.append(1) or (False, "de prova")
    p2.abrir()
    p2.ligar_a_tela()
    out.append({"abertura": "2 (pelo atalho)", "testes rodados": len(testes), "fase": p2.atual.estado.fase.value,
                "pedidos ao Velopack": p2.vp.nomes(), "o Kaique viu": _viu(p2)})
    # a correção: 9.9.1 publicada; a 9.9.0 ainda é a que roda
    p3 = _prova(pasta / "a3", ultima_boa="0.1.0", publicar_nova=False)
    p3.pacote_em_packages("9.9.0")
    p3.conteudo_de("9.9.1")
    from tests import ajudante_do_atualizador as aj
    p3.vp.publicada = aj._publicar(p3.fonte_pasta, "9.9.1", p3.conteudos["9.9.1"])
    p3.abrir()
    p3.ligar_a_tela()
    out.append({"abertura": "3 (a correção 9.9.1 publicada)", "fase": p3.atual.estado.fase.value,
                "pedidos ao Velopack": p3.vp.nomes(), "o Kaique viu": _viu(p3)})
    # a 9.9.1 instalada (a troca deu certo e passou): a frase da 9.9.0 não aparece
    versao.VERSAO = "9.9.1"
    p4 = _prova(pasta / "a4", ultima_boa="0.1.0", publicar_nova=False)
    p4.pacote_em_packages("9.9.1")
    p4.abrir(atualizacao.ARG_CONFERIR_NOVA, "9.9.0", "9.9.1")
    p4.ligar_a_tela()
    out.append({"abertura": "4 (na 9.9.1)", "fase": p4.atual.estado.fase.value, "o Kaique viu": _viu(p4)})
    RES["L3 a reprovada e depois"] = out


# ---- L4: reprovada depois do "Sim" ao fechar (sem janela), e as duas aberturas seguintes
def l4():
    versao.VERSAO = "9.9.0"
    pasta = _limpo("L4")
    out = []
    p = _prova(pasta / "a1", teste=(False, "de prova"), ultima_boa="0.1.0", publicar_nova=False)
    p.pacote_em_packages("9.9.0")
    saida = p.abrir(atualizacao.ARG_CONFERIR_NOVA, "0.1.0", "9.9.0", atualizacao.ARG_SEM_JANELA)
    out.append({"abertura": "reaberta sem janela (o Sim ao fechar)", "saída": saida, "o Kaique viu": _viu(p),
                "frase no bilhete": atualizacao.ler_estado().get("frase")})
    for n in (2, 3):
        q = _prova(pasta / f"a{n}", ultima_boa="0.1.0", publicar_nova=False)
        q.pacote_em_packages("9.9.0")
        q.abrir()
        q.ligar_a_tela()
        out.append({"abertura": f"{n} (pelo atalho)", "o Kaique viu": _viu(q), "fase": q.atual.estado.fase.value})
    RES["L4 reprovada depois do Sim ao fechar"] = out


# ---- L5: duas frases na mesma abertura (a da D-839 e a guardada), a caixa não pôde aparecer (sem área de trabalho)
def l5():
    if not CAIXA:
        RES["L5"] = "não se aplica a este código (sem a caixa do Windows)"
        return
    versao.VERSAO = "7.0.0"
    pasta = _limpo("L5")
    atualizacao.guardar_frase(fases.NAO_DEU_AGORA, "7.0.1", fases.MOTIVO_HAVIA_OUTRA_JANELA)
    p = _prova(pasta / "a1", publicar_nova=False)
    p.win.caixa_aparece = False                                   # como sem área de trabalho à vista
    p.abrir(atualizacao.ARG_CONFERIR_NOVA, "7.0.0", "7.0.1")
    antes = list(p.win.caixas)
    q = _prova(pasta / "a2", publicar_nova=False)                 # a abertura seguinte, com tela
    q.abrir()
    q.ligar_a_tela()
    RES["L5 duas frases, a caixa sem tela"] = {"tentadas sem tela": [t for _, t in antes],
                                                "a abertura seguinte com tela viu": _viu(q)}


# ---- L6: "Sim" ao fechar com outra janela; depois "Reiniciar agora" na abertura seguinte troca certo (M1 pelo outro caminho)
def l6():
    versao.VERSAO = "0.1.0"
    pasta = _limpo("L6")
    p = _prova(pasta / "a1", outras=[(1234, "C:/x/current/EditorImpressao.exe")])
    p.win.caminho_conferido = lambda c: True
    p.abrir()
    p.ligar_a_tela()
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    frase = atualizacao.ler_estado().get("frase")
    # a troca de verdade aconteceu por outro caminho; abre já na nova
    versao.VERSAO = NOVA
    q = _prova(pasta / "a2", publicar_nova=False)
    q.pacote_em_packages(NOVA)
    q.abrir(atualizacao.ARG_CONFERIR_NOVA, "0.1.0", NOVA)
    q.ligar_a_tela()
    RES["L6 M1 pelo Reiniciar agora da abertura seguinte"] = {"frase guardada pelo Sim": frase,
                                                              "na nova o Kaique viu": _viu(q)}


for caso in (l1, l2, l3, l4, l5, l6):
    try:
        caso()
    except Exception as erro:  # noqa: BLE001
        import traceback
        RES[caso.__name__] = "ERRO NA PROVA: " + "".join(traceback.format_exception(erro))[-1500:]
print(json.dumps(RES, ensure_ascii=False, indent=1))
