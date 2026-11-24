"""Prova EXECUTADA (volta 4 do atualizador novo, 24/11/2026; D-855, D-863): a volta tenta uma vez e nunca fica em laço,
com o atualizador do Velopack DE VERDADE e o executor de verdade.

Tudo numa pasta minha (`saida_teste\\prova-volta4`), com um programa de prova de outro nome (`ProvaV4`, um .exe SEM
JANELA feito com o PyInstaller que só anota com que argumentos foi aberto e sai). O `vpk` 1.2.161 de verdade monta a
1.1.0 e a 1.2.0 (com `--delta None`, como o nosso publicar); a instalação é a portátil do vpk (sem registro do Windows,
sem atalho); o `Update.exe` de verdade roda com `--silent` (sem a janelinha: a única diferença para o programa). Nada é
instalado; nada encosta no programa do Samuel; o PROGRAMDATA e o LOCALAPPDATA são trocados DENTRO do Python.

  A. a volta 1.2.0 -> 1.1.0 pedida como o programa pede agora (`--voltando 1.2.0 1.1.0`), com um arquivo de `current\\`
     preso por este processo: o Velopack desiste e reabre a 1.2.0 COM o pedido?
  B. o executor de verdade, aberto com a linha de comando que o Velopack passou em A (lida do registro do programa de
     prova), numa instalação de prova com a última boa 1.1.0: não testa, mostra a frase (3), põe a marca de "sem volta";
     e a abertura seguinte (o atalho, sem linha de comando) não testa nem pede a volta.
  C. a mesma volta sem nada preso: dá certo, e o Velopack reabre a 1.1.0 com o pedido; o executor nela mostra a (1).
Uso: python prova_volta_uma_vez.py   (a saída vai para prova_volta_uma_vez-resultado.txt)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

RAMO = Path(__file__).resolve().parents[3]
R = Path(r"D:\programas\EditorImpressao\saida_teste\prova-volta4")
LOG = R / "aberturas.log"
ID = "ProvaV4"
VPK = Path(os.environ["USERPROFILE"]) / ".dotnet" / "tools" / "vpk.exe"
PYINSTALLER = [sys.executable, "-m", "PyInstaller"]     # o pyinstaller.exe da .venv não abre; o módulo sim


def rodar(comando: list, **kw) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in comando], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", **kw)


def fazer_o_programa_de_prova() -> Path:
    """O .exe de prova, sem janela: anota a versão, a pasta e os argumentos com que foi aberto."""
    fonte = R / "build" / "ProvaV4.py"
    fonte.parent.mkdir(parents=True, exist_ok=True)
    fonte.write_text(
        "import datetime, pathlib, sys\n"
        f"log = pathlib.Path(r'{LOG}')\n"
        "pasta = pathlib.Path(sys.executable).resolve().parent\n"
        "v = (pasta / 'versao.txt').read_text(encoding='utf-8').strip() if (pasta / 'versao.txt').exists() else '?'\n"
        "with log.open('a', encoding='utf-8') as f:\n"
        "    f.write(repr({'versao': v, 'args': sys.argv[1:]}) + '\\n')\n", encoding="utf-8")
    feito = rodar(PYINSTALLER + ["--onefile", "--noconsole", "--name", ID, "--distpath", R / "build" / "dist",
                   "--workpath", R / "build" / "work", "--specpath", R / "build", fonte])
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

    return [ast.literal_eval(linha) for linha in LOG.read_text(encoding="utf-8").splitlines()] if LOG.exists() else []


def aplicar(raiz: Path, pacote: Path, argumentos: list[str]) -> dict:
    """O mesmo pedido que a biblioteca monta (`manager.rs` 612-674), sem o `--waitPid` e com `--silent`."""
    antes = len(aberturas())
    feito = rodar([raiz / "Update.exe", "apply", "--package", pacote, "--silent", "--root", raiz,
                   "--packageDir", raiz / "packages", "--"] + argumentos)
    # O Velopack abre o programa também para os ganchos (`--veloapp-obsolete`, `--veloapp-updated`); a reabertura é a
    # que não é gancho. Espera por ela até 15 s.
    fim = time.time() + 15
    while not [a for a in aberturas()[antes:] if not str(a["args"][:1]).count("--veloapp")] and time.time() < fim:
        time.sleep(0.3)
    todas = aberturas()[antes:]
    reabertura = [a for a in todas if not str(a["args"][:1]).count("--veloapp")]
    return {"codigo do Update.exe": feito.returncode,
            "versao em current depois": (raiz / "current" / "versao.txt").read_text(encoding="utf-8"),
            "o Velopack abriu o programa (o registro do programa de prova, com os ganchos)": todas,
            "a reabertura (sem os ganchos)": reabertura[-1] if reabertura else None}


def executor(raiz: Path, versao_que_roda: str, argumentos: list[str], testes: list) -> dict:
    """O executor de verdade (a regra, o disco, as marcas), com o teste rápido e o pedido ao Velopack de mentira (o
    pedido só anota); a abertura com a linha de comando que o Velopack passou."""
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
            "testes rapidos rodados": len(testes), "pedidos ao Velopack": vp.nomes(),
            "frases na tela": [atualizacao.frase_da_falha(e.tipo, e.motivo_da_tela) for e in tela
                               if isinstance(e, fases.MostrarFalha)],
            "marca de sem volta no disco": atualizacao.tem_marca(raiz, atualizacao.MARCA_SEM_VOLTA, versao_que_roda)}


def instalacao_de_prova(nome: str) -> Path:
    """Uma instalação do NOSSO programa (de prova), com a última boa 1.1.0 guardada e a 1.2.0 reprovada no bilhete."""
    import assinatura
    import atualizacao
    from tests.ajudante_do_atualizador import CHAVE, PACOTE

    raiz = R / nome
    (raiz / "current").mkdir(parents=True)
    (raiz / "packages").mkdir()
    pasta = atualizacao.pasta_da_ultima_boa(raiz)
    pasta.mkdir()
    dado = b"pacote de prova 1.1.0"
    nome_pacote = atualizacao.nome_do_pacote("1.1.0")
    (pasta / nome_pacote).write_bytes(dado)
    import hashlib

    (pasta / assinatura.nome_do_arquivo_da_assinatura(PACOTE, "1.1.0")).write_text(assinatura.escrever_assinatura(
        CHAVE, assinatura.VersaoAssinada(PACOTE, "1.1.0", nome_pacote, hashlib.sha256(dado).hexdigest())),
        encoding="utf-8")
    atualizacao.gravar_estado({"reprovadas": ["1.2.0"]})
    return raiz


def main() -> None:
    if R.exists():
        shutil.rmtree(R)
    R.mkdir(parents=True)
    os.environ["PROGRAMDATA"] = str(R / "ProgramData")          # DENTRO do Python (o do Git Bash não chega)
    os.environ["LOCALAPPDATA"] = str(R / "LocalAppData")
    (R / "LocalAppData").mkdir()
    sys.path.insert(0, str(RAMO))
    exe = fazer_o_programa_de_prova()
    resultado: dict = {"vpk 1.1.0": montar(exe, "1.1.0"), "vpk 1.2.0": montar(exe, "1.2.0")}
    saida = R / "saida"
    raiz = R / "instalado"
    with zipfile.ZipFile(next(saida.glob("*Portable.zip"))) as z:      # o portátil é o da última montada (1.2.0)
        z.extractall(raiz)
    (raiz / "packages").mkdir(exist_ok=True)
    pacote_110 = raiz / "packages" / f"{ID}-1.1.0-full.nupkg"
    shutil.copy(saida / f"{ID}-1.1.0-full.nupkg", pacote_110)       # o que a volta copia para packages\\
    preso = (raiz / "current" / "versao.txt").open("rb")             # um programa de fora segurando um arquivo
    try:
        a = aplicar(raiz, pacote_110, ["--voltando", "1.2.0", "1.1.0"])
    finally:
        preso.close()
    resultado["A. a volta recusada pelo Windows (um arquivo preso), com --voltando"] = a
    argumentos = a["a reabertura (sem os ganchos)"]["args"] if a["a reabertura (sem os ganchos)"] else []
    nossa = instalacao_de_prova("nossa-B")
    testes: list = []
    resultado["B1. o executor reaberto com o que o Velopack passou"] = executor(nossa, "1.2.0", argumentos, testes)
    resultado["B2. a abertura seguinte, pelo atalho"] = executor(nossa, "1.2.0", [], testes)
    resultado["B3. e a outra seguinte"] = executor(nossa, "1.2.0", [], testes)
    c = aplicar(raiz, pacote_110, ["--voltando", "1.2.0", "1.1.0"])
    resultado["C. a mesma volta sem nada preso"] = c
    argumentos = c["a reabertura (sem os ganchos)"]["args"] if c["a reabertura (sem os ganchos)"] else []
    resultado["C1. o executor na anterior, reaberto com o que o Velopack passou"] = executor(
        instalacao_de_prova("nossa-C"), "1.1.0", argumentos, [])
    texto = json.dumps(resultado, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_volta_uma_vez-resultado.txt").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
