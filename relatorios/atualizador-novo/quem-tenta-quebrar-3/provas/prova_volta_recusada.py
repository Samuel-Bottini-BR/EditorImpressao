"""Prova EXECUTADA (quem tenta quebrar 3, 24/11/2026): o que o atualizador do Velopack DE VERDADE faz quando a troca
não consegue acontecer (um arquivo de `current\\` preso por outro programa), na TROCA NORMAL e na VOLTA para a anterior.

Pergunta: a volta (`Atualizacao._voltar` -> `trocar_para(..., volta=True)`) pede ao Velopack a troca SEM argumento
nenhum. Se o Windows não deixar trocar, o Velopack reabre a versão de antes (a que falhou no teste) com esses mesmos
argumentos (vazios) (`apply.rs` 57-61). A versão que falhou abre como uma abertura comum: o que o programa faz?

Tudo numa pasta minha (`saida_teste\\qtq3\\volta-recusada`), com um programa de prova de outro nome (`ProvaVolta`, um
.exe SEM JANELA feito com o PyInstaller que só anota numa linha com que argumentos foi aberto e sai). O `vpk` 1.2.161
de verdade monta as versões 1.1.0 e 1.2.0; a instalação é a portátil do próprio vpk (sem registro do Windows, sem
atalho); o `Update.exe` de verdade roda com `--silent` (sem a janelinha: a única diferença para o programa, que pede
com `silent=False`). Nada é instalado, nada encosta no programa do Samuel.

Parte A: a VOLTA recusada (o Update.exe aplica o pacote da 1.1.0 sobre a 1.2.0, sem argumentos, com um arquivo de
          current\\ preso por este processo).
Parte B: a TROCA NORMAL recusada (com os argumentos `--conferir-a-versao-nova`, o caso da D-839), o mesmo arquivo preso.
Parte C: a mesma volta, sem nada preso (dá certo).
Parte D: a regra de verdade (`core.fases_da_atualizacao.proxima_fase`) com o que o disco mostra depois da parte A
          (a versão que roda, a última boa lida da pasta de verdade por `atualizacao.ler_ultima_boa`, as reprovadas):
          o que ela manda fazer, três aberturas seguidas.
Uso: python prova_volta_recusada.py  (a saída vai para prova_volta_recusada-resultado.txt)
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

RAMO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAMO))
R = RAMO / "saida_teste" / "qtq3" / "volta-recusada"
EXE = R / "build" / "dist" / "ProvaVolta.exe"
LOG = R / "aberturas.log"
ID = "ProvaVolta"
VPK = Path(os.environ["USERPROFILE"]) / ".dotnet" / "tools" / "vpk.exe"


def rodar(comando: list, **kw) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in comando], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", **kw)


def montar(v: str) -> int:
    pasta = R / f"programa-{v}"
    pasta.mkdir(parents=True)
    shutil.copy(EXE, pasta / f"{ID}.exe")
    (pasta / "versao.txt").write_text(v, encoding="utf-8")
    feito = rodar([VPK, "pack", "--packId", ID, "--packVersion", v, "--packDir", pasta, "--mainExe", f"{ID}.exe",
                   "--packTitle", "ProvaVolta", "--outputDir", R / "saida", "--runtime", "win-x64", "--delta", "None"])
    return feito.returncode


def linhas_novas(antes: int) -> list[str]:
    time.sleep(3)          # o programa de prova é aberto pelo Update.exe e escreve em menos de 1 s
    if not LOG.exists():
        return []
    return LOG.read_text(encoding="utf-8").splitlines()[antes:]


def contar() -> int:
    return len(LOG.read_text(encoding="utf-8").splitlines()) if LOG.exists() else 0


def aplicar(raiz: Path, pacote: Path, argumentos: list[str]) -> dict:
    """O mesmo pedido que a biblioteca monta (`manager.rs` 612-674, `unsafe_apply_updates`), sem o `--waitPid` (não há
    programa para esperar) e com `--silent` (sem janela na tela)."""
    comando = [raiz / "Update.exe", "apply", "--package", pacote, "--silent", "--root", raiz,
               "--packageDir", raiz / "packages"]
    if argumentos:
        comando += ["--"] + argumentos
    antes = contar()
    inicio = time.time()
    feito = rodar(comando)
    return {"codigo do Update.exe": feito.returncode, "segundos": round(time.time() - inicio, 1),
            "versao em current depois": (raiz / "current" / "versao.txt").read_text(encoding="utf-8"),
            "aberturas do programa de prova (o log dele)": linhas_novas(antes),
            "fim do registro do Update.exe": [l for l in (feito.stdout + feito.stderr).splitlines()
                                              if "ERRO" in l.upper() or "Unable" in l or "Error" in l
                                              or "Starting" in l or "applied" in l.lower()][-8:]}


def main() -> None:
    if R.exists():
        for p in R.iterdir():
            if p.name != "build":
                shutil.rmtree(p) if p.is_dir() else p.unlink()
    resultado: dict = {"vpk 1.1.0": montar("1.1.0"), "vpk 1.2.0": montar("1.2.0")}
    saida = R / "saida"
    raiz = R / "instalado"
    with zipfile.ZipFile(next(saida.glob("*Portable.zip"))) as z:       # o portátil é o da última montada (1.2.0)
        z.extractall(raiz)
    (raiz / "packages").mkdir(exist_ok=True)
    resultado["instalada (current)"] = (raiz / "current" / "versao.txt").read_text(encoding="utf-8")
    pacote_110 = raiz / "packages" / f"{ID}-1.1.0-full.nupkg"
    shutil.copy(saida / f"{ID}-1.1.0-full.nupkg", pacote_110)       # o que a volta deixa em packages\\ (baixar)

    preso = (raiz / "current" / "versao.txt").open("rb")             # um programa de fora segurando um arquivo
    try:
        resultado["A. a VOLTA 1.2.0 -> 1.1.0 com um arquivo preso, sem argumentos (como `_voltar` pede)"] = aplicar(
            raiz, pacote_110, [])
        resultado["B. a TROCA NORMAL com um arquivo preso, com os argumentos do pedido (o caso da D-839)"] = aplicar(
            raiz, pacote_110, ["--conferir-a-versao-nova", "1.2.0", "1.1.0"])
    finally:
        preso.close()
    resultado["packages depois de A e B"] = sorted(p.name for p in (raiz / "packages").iterdir())
    resultado["C. a mesma volta, sem nada preso"] = aplicar(raiz, pacote_110, [])
    resultado["D. a regra de verdade com o disco depois da parte A"] = parte_d()
    texto = json.dumps(resultado, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_volta_recusada-resultado.txt").write_text(texto, encoding="utf-8")
    print(texto)


def parte_d() -> list:
    """A regra de verdade, três aberturas seguidas, com o disco que a parte A deixa: a versão que roda é a 1.2.0 (o
    Velopack a reabriu), a última boa é a 1.1.0 (pacote e assinatura na pasta de verdade, lida por `ler_ultima_boa`),
    o bilhete tem a 1.2.0 reprovada, e a linha de comando não tem nada (a volta não passa argumento)."""
    import atualizacao
    import versao as versao_mod
    from core import fases_da_atualizacao as f

    raiz = R / "regra"
    boa = atualizacao.pasta_da_ultima_boa(raiz)
    boa.mkdir(parents=True)
    (boa / atualizacao.nome_do_pacote("1.1.0")).write_bytes(b"pacote")
    import assinatura
    (boa / assinatura.nome_do_arquivo_da_assinatura(versao_mod.ID_DO_PACOTE, "1.1.0")).write_text("x")
    ultima = atualizacao.ler_ultima_boa(raiz)
    saida = []
    for abertura in (1, 2, 3):
        estado, efeitos = f.proxima_fase(f.Estado(), f.Abriu(
            instalado=True, conta_de_testes=False, portatil=False, pasta_grava=True, versao="1.2.0",
            ultima_boa=ultima, nao_tentar=("1.2.0",), pendente="", troca_em_curso=False))
        todos = list(efeitos)
        estado, efeitos = f.proxima_fase(estado, f.TesteRapido(False, "código 1"))
        todos += efeitos
        estado, efeitos = f.proxima_fase(estado, f.VoltaPedida(True))       # o pedido ao Velopack dá certo
        todos += efeitos
        saida.append({"abertura": abertura, "ultima boa lida do disco": ultima,
                      "efeitos": [type(e).__name__ + ("" if not hasattr(e, "antes_da_janela") else
                                                      f"(antes_da_janela={e.antes_da_janela})") for e in todos],
                      "alguma frase na tela ou guardada": [repr(e) for e in todos
                                                           if isinstance(e, (f.MostrarFalha, f.GuardarFrase))]})
    shutil.rmtree(raiz)
    return saida


if __name__ == "__main__":
    main()
