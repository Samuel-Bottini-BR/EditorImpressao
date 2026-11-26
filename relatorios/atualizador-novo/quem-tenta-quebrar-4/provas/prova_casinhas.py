"""Quem tenta quebrar 4 (24/11/2026): casinhas da tabela rodadas com o executor de verdade. EXECUTADO.

De verdade: a regra, o executor (`atualizacao.Atualizacao`), o disco (o bilhete, as marcas, a última boa, os "vistos"),
as assinaturas (chave de prova). De mentira: a peça do Windows e a do Velopack (as do `tests/ajudante_do_atualizador.py`,
que só anotam e devolvem o que a prova manda) e o teste rápido. O PROGRAMDATA e o LOCALAPPDATA trocados DENTRO do
Python e conferidos. Cada caso numa pasta própria.

  C1. Dois cliques nos segundos do teste (o M1 que o Samuel deixou para depois, D-861), DEPOIS da D-863: a volta não é
      pedida (há outra janela), a frase (3), a marca de "sem volta"; e a abertura seguinte, com um clique só?
  C2. A volta que não pôde ser pedida porque o Windows não deu a lista de processos (um instante): a mesma coisa?
  C3. A marca de "sem volta" que não consegue ser gravada (o nome já ocupado, como num disco que não aceita mais nada):
      a volta recusada pelo Windows, três aberturas seguidas pelo atalho.
  C4. A versão aprovada (D-856): a abertura seguinte não testa; e quando a guarda não coube, a última boa de antes vale.
  C5. Sem internet na conferência da assinatura (a fonte que não responde) x a assinatura que não existe (frase 2).
Uso: python prova_casinhas.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
BASE = RAMO / "saida_teste" / "qtq4" / "casinhas"
sys.path.insert(0, str(RAMO))


def ambiente(nome: str) -> Path:
    pasta = BASE / nome
    if pasta.exists():
        shutil.rmtree(pasta)
    (pasta / "LocalAppData").mkdir(parents=True)
    os.environ["PROGRAMDATA"] = str(pasta / "ProgramData")
    os.environ["LOCALAPPDATA"] = str(pasta / "LocalAppData")
    os.environ["USERNAME"] = "Kaique"
    import atualizacao

    assert str(atualizacao.pasta_do_estado()).startswith(str(pasta))
    return pasta


import atualizacao  # noqa: E402
import versao  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402
from tests.ajudante_do_atualizador import (ANTERIOR, NOVA, PACOTE, Prova, PUBLICA, VelopackFalso,  # noqa: E402
                                           WindowsFalso)


def texto(ef) -> str:
    if isinstance(ef, fases.MostrarFalha):
        return "[Atualização] " + atualizacao.frase_da_falha(ef.tipo, ef.motivo_da_tela)
    return type(ef).__name__


def abertura(p: Prova, *argumentos: str, teste=(False, "não passou (de prova)"), outras=None) -> dict:
    """Uma abertura nova (um executor novo) na mesma instalação de prova, rodando a NOVA."""
    versao.VERSAO = NOVA
    testes: list = []
    p.win.outras = None if outras == "sem lista" else ([] if outras is None else outras)
    p.vp.chamadas.clear()
    a = atualizacao.Atualizacao(windows=p.win, velopack=p.vp, raiz=p.raiz, fonte=atualizacao.Fonte(str(p.fonte_pasta)),
                                por_tras=lambda t: t(), pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                motor_no_lugar=lambda m=None: True,
                                teste=lambda: testes.append(1) or teste, chave_publica=PUBLICA)
    a.abrir(list(argumentos))
    tela: list = []
    a.ligar_a_tela(tela.append)
    return {"linha de comando": list(argumentos), "testes rapidos": len(testes),
            "pedidos de troca (volta)": [c[1:3] for c in p.vp.chamadas if c[0] == "trocar"],
            "tela": [texto(e) for e in tela],
            "marca de sem volta": atualizacao.tem_marca(p.raiz, atualizacao.MARCA_SEM_VOLTA, NOVA),
            "fase no fim": a.estado.fase.value}


def c1_c2(nome: str, outras) -> dict:
    pasta = ambiente(nome)
    p = Prova(pasta, ultima_boa=ANTERIOR)
    p.pacote_em_packages(NOVA)
    r = {"1. a abertura que testa (a outra está testando junto / a lista não veio)": abertura(p, outras=outras),
         "2. a abertura seguinte, um clique só, nada mais aberto": abertura(p),
         "3. e a outra seguinte": abertura(p)}
    r["última boa no disco"] = atualizacao.ler_ultima_boa(p.raiz)
    return r


def c3() -> dict:
    pasta = ambiente("C3")
    p = Prova(pasta, ultima_boa=ANTERIOR)
    p.pacote_em_packages(NOVA)
    # O nome da marca já ocupado por uma pasta: a gravação dela falha (como um disco que não aceita mais nada).
    (atualizacao.pasta_da_ultima_boa(p.raiz) / f"{PACOTE}-{NOVA}.sem-volta").mkdir()
    r = {}
    for n in (1, 2, 3):
        # O atalho: o teste falha, a volta é pedida; o Velopack não consegue trocar e reabre a NOVA com --voltando.
        r[f"{n}a. o atalho"] = abertura(p)
        r[f"{n}b. a reabertura pelo Velopack (--voltando)"] = abertura(p, "--voltando", NOVA, ANTERIOR)
    return r


def c4() -> dict:
    pasta = ambiente("C4")
    p = Prova(pasta, ultima_boa=ANTERIOR)
    p.pacote_em_packages(NOVA)
    import assinatura

    # a assinatura da NOVA guardada como "a que chega" (como depois de conferida)
    nome = assinatura.nome_do_arquivo_da_assinatura(PACOTE, NOVA)
    shutil.copy(p.fonte_pasta / nome, atualizacao.pasta_da_ultima_boa(p.raiz) / atualizacao.nome_da_assinatura_que_chega(NOVA))
    # o disco "sem espaço" só para a guarda (a conta é a de verdade, o número de bytes livres é que é de prova)
    original = atualizacao.guardar_ultima_boa
    atualizacao.guardar_ultima_boa = lambda raiz, v, fonte, chave=None, livre=None: original(
        raiz, v, fonte, chave, livre=lambda caminho: 10 * 2**20)
    try:
        r = {"1. a abertura depois da troca: o teste passa, a guarda não cabe": abertura(p, teste=(True, "")),
             "2. a abertura seguinte": abertura(p, teste=(True, "")),
             "última boa": atualizacao.ler_ultima_boa(p.raiz),
             "marca de aprovada": atualizacao.tem_marca(p.raiz, atualizacao.MARCA_APROVADA, NOVA),
             "registro (fim)": atualizacao.caminho_do_registro().read_text(encoding="utf-8").splitlines()[-3:]}
    finally:
        atualizacao.guardar_ultima_boa = original
    return r


def c5() -> dict:
    r = {}
    for caso in ("a fonte não responde", "a assinatura não existe"):
        pasta = ambiente("C5-" + ("sem-rede" if "responde" in caso else "nao-existe"))
        versao.VERSAO = ANTERIOR
        p = Prova(pasta, ultima_boa=ANTERIOR)
        nome = f"{PACOTE}-{NOVA}.assinatura"
        if "responde" in caso:
            p.fonte_pasta.rename(pasta / "fonte-longe")    # a pasta da fonte some (como a rede caída depois de procurar)
        else:
            (p.fonte_pasta / nome).unlink()
        p.abrir()
        p.ligar_a_tela()
        r[caso] = {"tela": [texto(e) for e in p.tela],
                   "registro (fim)": atualizacao.caminho_do_registro().read_text(encoding="utf-8").splitlines()[-1:]}
    return r


def main() -> None:
    resultado = {"C1 dois cliques (outra janela testando junto), depois da D-863": c1_c2(
                     "C1", [(1, r"C:\x\current\EditorImpressao.exe")]),
                 "C2 a lista do Windows que não veio na hora da volta": c1_c2("C2", "sem lista"),
                 "C3 a marca de sem volta que não grava": c3(),
                 "C4 aprovada e a guarda que não cabe": c4(),
                 "C5 sem rede x não existe": c5()}
    t = json.dumps(resultado, ensure_ascii=False, indent=1, default=str)
    Path(__file__).with_name("prova_casinhas-resultado.txt").write_text(t, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(t)


if __name__ == "__main__":
    main()
