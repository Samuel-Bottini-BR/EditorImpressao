"""Prova EXECUTADA (volta 3 do atualizador novo, 24/11/2026): o processo morto no meio, e o seguinte refazendo.

Dois processos de verdade, um depois do outro, com a regra, o executor, o disco, a peça do Windows (a lista de
processos de verdade) e a biblioteca do Velopack de verdade (o `baixar` da volta pela pasta da última boa, numa
instalação de prova). De mentira: só o teste rápido (falha ou passa de propósito) e o pedido final da troca (`trocar`
só escreve um arquivo dizendo para qual versão seria; o atualizador do Velopack de verdade não roda: ele mexeria na
pasta e reabriria o programa).

Casos:
  G1  a volta interrompida: a 1.2.0 não passa no teste; o processo MORRE (`os._exit(9)`, como o Windows desligando)
      logo antes de pedir a troca de volta. O processo seguinte (o atalho, sem linha de comando) roda o teste de novo e
      pede a volta para a 1.1.0, sem a frase "voltou para a versão anterior".
  G   a guarda interrompida: a 1.2.0 passa no teste; o processo morre no meio da cópia do pacote para a última boa.
      A última boa continua a 1.1.0 (o pedaço copiado não vira nada); o processo seguinte testa de novo e guarda.
Uso: python prova_dois_processos.py   (os dois casos; a saída vai para prova_dois_processos-resultado.txt)
     python prova_dois_processos.py <caso> <passo>   (um processo; só a própria prova chama assim)
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RAMO = Path(__file__).resolve().parents[3]
R = Path(os.environ.get("PROVA_PASTA", r"D:\programas\EditorImpressao\saida_teste\prova-volta3"))
sys.path.insert(0, str(RAMO))
CHAVE_DE_PROVA = bytes(range(32))


def montar(caso: str) -> Path:
    """A instalação de prova (raiz, current, packages, ultima-boa com a 1.1.0) e os pacotes assinados de prova."""
    import assinatura
    import atualizacao

    base = R / caso
    if base.exists():
        shutil.rmtree(base)
    raiz = base / "raiz"
    (raiz / "current").mkdir(parents=True)
    (raiz / "packages").mkdir()
    (raiz / "Update.exe").write_bytes(b"MZ")
    (raiz / "current" / "sq.version").write_text(nuspec("1.2.0"), encoding="utf-8")
    pasta = atualizacao.pasta_da_ultima_boa(raiz)
    pasta.mkdir()
    for v in ("1.1.0", "1.2.0"):
        dado = nupkg(v)
        nome = atualizacao.nome_do_pacote(v)
        assinada = assinatura.escrever_assinatura(CHAVE_DE_PROVA, assinatura.VersaoAssinada(
            "EditorImpressaoPrograma", v, nome, hashlib.sha256(dado).hexdigest()))
        (base / f"{v}.assinatura").write_text(assinada, encoding="utf-8")
        (base / f"{v}.nupkg").write_bytes(dado)
    shutil.copy(base / "1.1.0.nupkg", pasta / atualizacao.nome_do_pacote("1.1.0"))
    shutil.copy(base / "1.1.0.assinatura", pasta / "EditorImpressaoPrograma-1.1.0.assinatura")
    shutil.copy(base / "1.2.0.nupkg", raiz / "packages" / atualizacao.nome_do_pacote("1.2.0"))   # a que roda
    shutil.copy(base / "1.2.0.assinatura", pasta / "EditorImpressaoPrograma-1.2.0.assinatura")   # guardada ao conferir
    return base


def nuspec(v: str) -> str:
    return (f'<?xml version="1.0"?><package><metadata><id>EditorImpressaoPrograma</id><version>{v}</version>'
            '<title>Editor</title><authors>x</authors><description>x</description>'
            '<mainExe>EditorImpressao.exe</mainExe></metadata></package>')


def nupkg(v: str) -> bytes:
    dados = io.BytesIO()
    with zipfile.ZipFile(dados, "w") as z:
        z.writestr("EditorImpressaoPrograma.nuspec", nuspec(v))
        z.writestr("lib/app/motor-exigido.json", json.dumps({"versao": 1}))
        z.writestr("lib/app/peso.bin", os.urandom(2_000_000))
    return dados.getvalue()


def processo(caso: str, passo: str) -> None:
    """Um processo do programa (o executor de verdade) na instalação de prova."""
    base = R / caso
    os.environ["PROGRAMDATA"] = str(base / "ProgramData")
    os.environ["LOCALAPPDATA"] = str(base / "local")
    (base / "local").mkdir(exist_ok=True)
    import assinatura
    import atualizacao
    import versao
    import velopack
    from core import conversa_com_o_velopack as conversa
    from core import fases_da_atualizacao as fases
    from core import windows

    versao.VERSAO = "1.2.0"
    raiz = base / "raiz"
    localizador = velopack.VelopackLocatorConfig(raiz, raiz / "Update.exe", raiz / "packages",
                                                 raiz / "current" / "sq.version", raiz / "current", False)

    class PecaDoVelopack:
        """A peça de verdade com o localizador da instalação de prova; `trocar` só anota (e, no G1, morre antes)."""

        pacote_da_versao = staticmethod(conversa.pacote_da_versao)

        @staticmethod
        def baixar(endereco, v):
            conversa.baixar(endereco, v, localizador)

        @staticmethod
        def pendente(endereco):
            return conversa.pendente(endereco, localizador)

        @staticmethod
        def procurar(endereco):
            return None

        @staticmethod
        def trocar(endereco, v, reabrir, argumentos):
            if caso == "G1" and passo == "1":
                os._exit(9)                                   # morre antes de pedir a troca de volta
            (base / f"troca-pedida-{passo}.txt").write_text(f"{v.versao} {reabrir} {argumentos}", encoding="utf-8")

    if caso == "G" and passo == "1":
        original = atualizacao._copiar_somando

        def copia_que_morre(origem, destino):
            with origem.open("rb") as de, destino.open("wb") as para:
                para.write(de.read(500_000))
                para.flush()
            os._exit(9)                                       # morre no meio da cópia

        atualizacao._copiar_somando = copia_que_morre
        _ = original
    passa = caso == "G"
    a = atualizacao.Atualizacao(windows=windows, velopack=PecaDoVelopack(), raiz=raiz,
                                fonte=atualizacao.Fonte(str(base / "sem-internet")), por_tras=lambda t: t(),
                                pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                motor_no_lugar=lambda m=None: True,
                                teste=lambda: (passa, "o teste rápido de prova"),
                                chave_publica=assinatura.secret_to_public(CHAVE_DE_PROVA).hex())
    argumentos = [atualizacao.ARG_CONFERIR_NOVA, "1.1.0", "1.2.0"] if passo == "1" else []
    saida = a.abrir(argumentos)
    print(json.dumps({"saida": saida, "fase": a.estado.fase.value,
                      "frases para a tela": [e.tipo for e in a._fila_da_tela if isinstance(e, fases.MostrarFalha)],
                      "ultima boa": atualizacao.ler_ultima_boa(raiz)}, ensure_ascii=False))


def rodar(caso: str) -> dict:
    """Os dois processos, um depois do outro, e o que ficou no disco entre eles."""
    import atualizacao

    base = montar(caso)
    p1 = subprocess.run([sys.executable, __file__, caso, "1"], capture_output=True, text=True, encoding="utf-8")
    raiz = base / "raiz"
    entre = {"codigo de saida do 1 (9 = morreu)": p1.returncode,
             "ultima boa no disco": atualizacao.ler_ultima_boa(raiz),
             "arquivos da ultima-boa": sorted(x.name for x in (raiz / "ultima-boa").iterdir()),
             "packages": sorted(x.name for x in (raiz / "packages").iterdir()),
             "bilhete": json.loads((base / "ProgramData" / "EditorImpressao" / "atualizacao" / "estado.json")
                                   .read_text(encoding="utf-8"))
             if (base / "ProgramData" / "EditorImpressao" / "atualizacao" / "estado.json").exists() else {}}
    p2 = subprocess.run([sys.executable, __file__, caso, "2"], capture_output=True, text=True, encoding="utf-8")
    registro = base / "ProgramData" / "EditorImpressao" / "atualizacao" / "atualizacao.log"
    troca = base / "troca-pedida-2.txt"
    return {"depois do processo 1": entre,
            "processo 2 (o atalho, sem linha de comando)": json.loads(p2.stdout.strip().splitlines()[-1])
            if p2.stdout.strip() else p2.stderr[-1500:],
            "troca pedida pelo 2": troca.read_text(encoding="utf-8") if troca.exists() else "nenhuma",
            "registro": registro.read_text(encoding="utf-8") if registro.exists() else "",
            "erros": (p1.stderr + p2.stderr)[-1500:]}


if __name__ == "__main__":
    if len(sys.argv) == 3:
        processo(sys.argv[1], sys.argv[2])
    else:
        resultado = {caso: rodar(caso) for caso in ("G1", "G")}
        texto = json.dumps(resultado, ensure_ascii=False, indent=1)
        Path(__file__).with_name("prova_dois_processos-resultado.txt").write_text(texto, encoding="utf-8")
        print(texto)
