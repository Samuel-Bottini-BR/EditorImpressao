"""Quem tenta quebrar 4 (24/11/2026): o processo morto no meio da guarda da última boa (D-856). EXECUTADO.

Pergunta (a tabela, "Guardar x desliga no meio da cópia"): a versão nova passou no teste; a marca de aprovada já está
no disco; o processo morre (à força) no meio da cópia de 300 MB. A última boa de antes continua? A abertura seguinte
testa ou copia de novo? O que sobra no disco?

De verdade: a regra, o executor, a guarda (`guardar_ultima_boa`, a cópia somada de verdade), o disco, as assinaturas
(chave de prova), o processo de verdade morto à força (TerminateProcess) no meio da cópia. De mentira: a peça do Windows
e a do Velopack (só anotam), o teste rápido (passa). O PROGRAMDATA e o LOCALAPPDATA trocados DENTRO do Python.
Uso: python prova_guarda_morta.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
R = RAMO / "saida_teste" / "qtq4" / "guarda-morta"
TAMANHO = 300 * 2**20


def ambiente() -> None:
    os.environ["PROGRAMDATA"] = str(R / "ProgramData")
    os.environ["LOCALAPPDATA"] = str(R / "LocalAppData")
    os.environ["USERNAME"] = "Kaique"
    sys.path.insert(0, str(RAMO))
    import atualizacao

    assert str(atualizacao.pasta_do_estado()).startswith(str(R))


def executor(argumentos: list[str]) -> dict:
    ambiente()
    import atualizacao
    import versao
    import assinatura
    from tests.ajudante_do_atualizador import VelopackFalso, WindowsFalso

    # a chave de prova é a mesma do processo que assinou (gravada por `preparar`; cada processo sortearia a sua)
    PUBLICA = assinatura.secret_to_public((R / "chave-de-prova.bin").read_bytes()).hex()
    versao.VERSAO = "1.2.0"
    raiz = R / "raiz"
    testes: list = []
    a = atualizacao.Atualizacao(windows=WindowsFalso(), velopack=VelopackFalso(raiz, None, "sem internet", {}),
                                raiz=raiz, fonte=atualizacao.Fonte(str(R / "sem-fonte")), por_tras=lambda t: t(),
                                pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                motor_no_lugar=lambda m=None: True, teste=lambda: testes.append(1) or (True, ""),
                                chave_publica=PUBLICA)
    saida = a.abrir(argumentos)
    return {"saida": saida, "testes rapidos": len(testes)}


def preparar() -> None:
    ambiente()
    import assinatura
    import atualizacao
    from tests.ajudante_do_atualizador import CHAVE, PACOTE

    (R / "chave-de-prova.bin").write_bytes(CHAVE)
    raiz = R / "raiz"
    (raiz / "current").mkdir(parents=True)
    (raiz / "packages").mkdir()
    ub = atualizacao.pasta_da_ultima_boa(raiz)
    ub.mkdir()
    pequeno = b"pacote da 1.1.0"
    n11 = atualizacao.nome_do_pacote("1.1.0")
    (ub / n11).write_bytes(pequeno)
    (ub / assinatura.nome_do_arquivo_da_assinatura(PACOTE, "1.1.0")).write_text(assinatura.escrever_assinatura(
        CHAVE, assinatura.VersaoAssinada(PACOTE, "1.1.0", n11, hashlib.sha256(pequeno).hexdigest())), encoding="utf-8")
    n12 = atualizacao.nome_do_pacote("1.2.0")
    soma = hashlib.sha256()
    with (raiz / "packages" / n12).open("wb") as f:
        for _ in range(TAMANHO // 2**20):
            bloco = os.urandom(2**20)
            soma.update(bloco)
            f.write(bloco)
    (ub / atualizacao.nome_da_assinatura_que_chega("1.2.0")).write_text(assinatura.escrever_assinatura(
        CHAVE, assinatura.VersaoAssinada(PACOTE, "1.2.0", n12, soma.hexdigest())), encoding="utf-8")


def olhar() -> dict:
    import atualizacao

    raiz = R / "raiz"
    ub = atualizacao.pasta_da_ultima_boa(raiz)
    try:
        registro = atualizacao.caminho_do_registro().read_text(encoding="utf-8").splitlines()[-2:]
    except OSError:
        registro = []
    return {"registro (fim)": registro, "última boa": atualizacao.ler_ultima_boa(raiz),
            "aprovada (1.2.0)": atualizacao.tem_marca(raiz, atualizacao.MARCA_APROVADA, "1.2.0"),
            "ultima-boa\\ (MB)": {p.name: round(p.stat().st_size / 2**20, 1) for p in sorted(ub.iterdir())}}


def main() -> None:
    if R.exists():
        shutil.rmtree(R)
    (R / "LocalAppData").mkdir(parents=True)
    preparar()
    resultado: dict = {}
    filho = subprocess.Popen([sys.executable, "-I", __file__, "filho", "--conferir-a-versao-nova", "1.1.0", "1.2.0",
                              "--sem-janela"], cwd=str(RAMO))
    import atualizacao

    chegando = atualizacao.pasta_da_ultima_boa(R / "raiz") / (atualizacao.nome_do_pacote("1.2.0") + ".chegando")
    fim = time.time() + 60
    while time.time() < fim and not (chegando.exists() and chegando.stat().st_size > 60 * 2**20):
        time.sleep(0.05)
    filho.kill()
    filho.wait()
    resultado["1. a reabertura sem janela (o teste passa) morta à força no meio da cópia"] = {
        "a cópia tinha chegado a (MB)": round(chegando.stat().st_size / 2**20, 1) if chegando.exists() else None,
        **olhar()}
    for n in (1, 2):
        r = subprocess.run([sys.executable, "-I", __file__, "filho"], cwd=str(RAMO), capture_output=True, text=True,
                           encoding="utf-8")
        resultado[f"2.{n} a abertura seguinte, pelo atalho"] = {
            **json.loads(r.stdout.strip().splitlines()[-1]), **olhar()}
    t = json.dumps(resultado, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_guarda_morta-resultado.txt").write_text(t, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(t)
    shutil.rmtree(R)                      # 300 MB a menos no disco (tudo daqui foi criado por esta prova)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "filho":
        print(json.dumps(executor(sys.argv[2:]), ensure_ascii=False))
    else:
        ambiente()
        main()
