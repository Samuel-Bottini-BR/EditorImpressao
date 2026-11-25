"""Quem tenta quebrar 4 (24/11/2026): a volta pedida pela reabertura SEM JANELA (o "Sim" ao fechar), com um arquivo
preso. EXECUTADO com o vpk e o Update.exe de verdade.

Pergunta: a tabela diz (Voltar x Windows nega) que "o Velopack reabre a que falhou com a marca; ela não testa, põe a
marca de sem volta, mostra a frase (3) e abre". Isso vale também quando a versão nova entrou pelo "Sim" ao fechar? Nesse
caminho a regra pede a volta com `reabrir=False` (nada abre na tela, D-769), e o Velopack só reabre o programa quando
pedem para reabrir (apply.rs 57-60: `if restart`).

De verdade: o `vpk` 1.2.161 monta a 1.1.0 e a 1.2.0 de um programa de prova SEM JANELA (PyInstaller; só anota com que
argumentos foi aberto); a instalação portátil do vpk numa pasta minha; o `Update.exe` de verdade, com `--silent` (sem
a janelinha) e com o `--norestart` que a biblioteca põe quando `restart=False` (manager.rs 640-642); um arquivo de
`current\\` preso por este processo. Depois, o executor de verdade (a regra, o disco, as marcas) nas duas aberturas,
com o teste rápido e o pedido ao Velopack de mentira. O PROGRAMDATA e o LOCALAPPDATA trocados DENTRO do Python.
Uso: python prova_volta_sem_janela.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
R = RAMO / "saida_teste" / "qtq4" / "volta-sem-janela"
LOG = R / "aberturas.log"
ID = "ProvaQ4"
VPK = Path(os.environ["USERPROFILE"]) / ".dotnet" / "tools" / "vpk.exe"


def rodar(comando: list, **kw) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in comando], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", **kw)


def fazer_o_programa_de_prova() -> Path:
    fonte = R / "build" / f"{ID}.py"
    fonte.parent.mkdir(parents=True, exist_ok=True)
    fonte.write_text(
        "import pathlib, sys\n"
        f"log = pathlib.Path(r'{LOG}')\n"
        "pasta = pathlib.Path(sys.executable).resolve().parent\n"
        "v = (pasta / 'versao.txt').read_text(encoding='utf-8').strip() if (pasta / 'versao.txt').exists() else '?'\n"
        "with log.open('a', encoding='utf-8') as f:\n"
        "    f.write(repr({'versao': v, 'args': sys.argv[1:]}) + '\\n')\n", encoding="utf-8")
    feito = rodar([sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", "--name", ID, "--distpath",
                   R / "build" / "dist", "--workpath", R / "build" / "work", "--specpath", R / "build", fonte])
    if feito.returncode != 0:
        raise SystemExit(feito.stderr[-2000:])
    return R / "build" / "dist" / f"{ID}.exe"


def montar(exe: Path, v: str) -> int:
    pasta = R / f"programa-{v}"
    pasta.mkdir(parents=True)
    shutil.copy(exe, pasta / f"{ID}.exe")
    (pasta / "versao.txt").write_text(v, encoding="utf-8")
    return rodar([VPK, "pack", "--packId", ID, "--packVersion", v, "--packDir", pasta, "--mainExe", f"{ID}.exe",
                  "--packTitle", ID, "--outputDir", R / "saida", "--runtime", "win-x64", "--delta", "None",
                  "--skip-updates"]).returncode


def aberturas() -> list[dict]:
    import ast

    return [ast.literal_eval(l) for l in LOG.read_text(encoding="utf-8").splitlines()] if LOG.exists() else []


def aplicar(raiz: Path, pacote: Path, argumentos: list[str], reabrir: bool) -> dict:
    """O pedido que a biblioteca monta (manager.rs 612-674), sem o `--waitPid`, com `--silent`, e com `--norestart`
    quando não é para reabrir (como `restart=False`)."""
    antes = len(aberturas())
    comando = [raiz / "Update.exe", "apply", "--package", pacote, "--silent"] + ([] if reabrir else ["--norestart"])
    comando += ["--root", raiz, "--packageDir", raiz / "packages", "--"] + argumentos
    feito = rodar(comando)
    time.sleep(8)
    todas = aberturas()[antes:]
    return {"o pedido": [str(c) for c in comando[1:]], "codigo do Update.exe": feito.returncode,
            "versao em current depois": (raiz / "current" / "versao.txt").read_text(encoding="utf-8"),
            "o Velopack abriu o programa (com os ganchos)": todas,
            "a reabertura (sem os ganchos)": [a for a in todas if not str(a["args"][:1]).count("--veloapp")]}


def executor(raiz: Path, versao_que_roda: str, argumentos: list[str], testes: list) -> dict:
    import atualizacao
    import versao
    from core import fases_da_atualizacao as fases
    from tests.ajudante_do_atualizador import PUBLICA, VelopackFalso, WindowsFalso

    versao.VERSAO = versao_que_roda
    vp = VelopackFalso(raiz, None, "sem internet", {})
    a = atualizacao.Atualizacao(windows=WindowsFalso(), velopack=vp, raiz=raiz,
                                fonte=atualizacao.Fonte(str(R / "sem-internet")), por_tras=lambda t: t(),
                                pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                motor_no_lugar=lambda m=None: True,
                                teste=lambda: testes.append(versao_que_roda) or (False, "o teste de prova"),
                                chave_publica=PUBLICA)
    saida = a.abrir(argumentos)
    tela: list = []
    a.ligar_a_tela(tela.append)
    return {"versao que roda": versao_que_roda, "linha de comando": argumentos, "saida": saida,
            "testes rapidos rodados ate aqui": len(testes),
            "pedidos de troca ao Velopack (versao, reabrir, argumentos)": [c[1:] for c in vp.chamadas
                                                                          if c[0] == "trocar"],
            "frases na tela": [atualizacao.frase_da_falha(e.tipo, e.motivo_da_tela) for e in tela
                               if isinstance(e, fases.MostrarFalha)],
            "marca de sem volta no disco": atualizacao.tem_marca(raiz, atualizacao.MARCA_SEM_VOLTA, versao_que_roda)}


def instalacao_nossa(nome: str) -> Path:
    import assinatura
    import atualizacao
    from tests.ajudante_do_atualizador import CHAVE, PACOTE, pacote_de_prova

    raiz = R / nome
    (raiz / "current").mkdir(parents=True)
    (raiz / "packages").mkdir()
    pasta = atualizacao.pasta_da_ultima_boa(raiz)
    pasta.mkdir()
    dado = pacote_de_prova("1.1.0")
    nome_pacote = atualizacao.nome_do_pacote("1.1.0")
    (pasta / nome_pacote).write_bytes(dado)
    (pasta / assinatura.nome_do_arquivo_da_assinatura(PACOTE, "1.1.0")).write_text(assinatura.escrever_assinatura(
        CHAVE, assinatura.VersaoAssinada(PACOTE, "1.1.0", nome_pacote, hashlib.sha256(dado).hexdigest())),
        encoding="utf-8")
    return raiz


def main() -> None:
    if R.exists():
        shutil.rmtree(R)
    R.mkdir(parents=True)
    os.environ["PROGRAMDATA"] = str(R / "ProgramData")
    os.environ["LOCALAPPDATA"] = str(R / "LocalAppData")
    os.environ["USERNAME"] = "Kaique"
    (R / "LocalAppData").mkdir()
    sys.path.insert(0, str(RAMO))
    import atualizacao

    assert str(atualizacao.pasta_do_estado()).startswith(str(R))
    exe = fazer_o_programa_de_prova()
    resultado: dict = {"vpk 1.1.0": montar(exe, "1.1.0"), "vpk 1.2.0": montar(exe, "1.2.0")}
    saida = R / "saida"
    raiz = R / "instalado"
    with zipfile.ZipFile(next(saida.glob("*Portable.zip"))) as z:      # o portátil da última montada (1.2.0)
        z.extractall(raiz)
    (raiz / "packages").mkdir(exist_ok=True)
    pacote_110 = raiz / "packages" / f"{ID}-1.1.0-full.nupkg"
    shutil.copy(saida / f"{ID}-1.1.0-full.nupkg", pacote_110)
    preso = (raiz / "current" / "versao.txt").open("rb")
    try:
        resultado["A. a volta da reabertura sem janela (--norestart), com um arquivo preso"] = aplicar(
            raiz, pacote_110, ["--voltando", "1.2.0", "1.1.0"], reabrir=False)
    finally:
        preso.close()
    nossa = instalacao_nossa("nossa")
    testes: list = []
    resultado["B1. a reabertura sem janela da 1.2.0 (o Sim ao fechar): o teste falha"] = executor(
        nossa, "1.2.0", ["--conferir-a-versao-nova", "1.1.0", "1.2.0", "--sem-janela"], testes)
    resultado["B2. a abertura seguinte, pelo atalho (o Velopack não reabriu nada em A)"] = executor(
        nossa, "1.2.0", [], testes)
    t = json.dumps(resultado, ensure_ascii=False, indent=1, default=str)
    Path(__file__).with_name("prova_volta_sem_janela-resultado.txt").write_text(t, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(t)


if __name__ == "__main__":
    main()
