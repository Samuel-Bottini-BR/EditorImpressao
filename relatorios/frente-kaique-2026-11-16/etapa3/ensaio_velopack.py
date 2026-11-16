"""Ensaio da atualizacao de verdade, com o Velopack, SEM instalar (etapa 3 da frente do Kaique).

    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\frente-kaique-2026-11-16\\etapa3\\ensaio_velopack.py

O que prova (com o Velopack e o Update.exe de verdade, e o nosso atualizacao.py
e assinatura.py de verdade):
  A. versao 1.1.0 "instalada" (o pacote portatil, numa pasta de teste) -> a
     1.2.0 publicada numa pasta-servidor -> --procurar-atualizacao -> o
     Velopack troca, reabre escondido em --conferir-a-versao-nova, o teste
     rapido passa: a pasta passa a ter a 1.2.0 (D-714);
  B. a 1.3.0 publicada ESTRAGADA (o teste rapido dela falha) -> troca, o teste
     falha, volta para a 1.2.0 com o pacote assinado (D-718), e o estado diz
     "falhou" (a frase da D-719 apareceria na tela);
  C. a 1.4.0 publicada com a assinatura de OUTRA chave -> recusada, nada
     baixado, continua a 1.2.0 (D-724).

Cuidados (regras do Samuel):
- nada vai para Arquivos de Programas, nada de tarefa do Windows, nada no
  registro do Windows: o pacote PORTATIL do Velopack e so uma pasta, e o
  preparar_o_computador nao roda em pacote portatil;
- nenhuma janela: o programinha e --windowed (sem console) e o Update.exe
  roda em silencio;
- o ProgramData e o LOCALAPPDATA dos processos do ensaio apontam para
  build\\ensaio-velopack\\ (nada no do Samuel);
- o programinha NAO e o Editor de Impressao: e um "app.py" que usa o
  atualizacao.py, o assinatura.py e o versao.py do programa, com outro nome de
  pacote (EditorImpressaoEnsaio) e uma CHAVE DE MENTIRA (a chave do Samuel
  nunca assina pacote de ensaio: um pacote de ensaio assinado por ela poderia
  ser servido ao programa do Kaique).

O resultado sai em build\\ensaio-velopack\\resultado.json e na tela.
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

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import assinatura  # noqa: E402
import empacotar  # noqa: E402
import publicar_versao_kaique as pub  # noqa: E402
import versao  # noqa: E402

PASTA = RAIZ / "build" / "ensaio-velopack"
SERVIDOR = PASTA / "servidor"
INSTALADO = PASTA / "instalado"
DADOS = PASTA / "ProgramData"
ID_DO_ENSAIO = "EditorImpressaoEnsaio"
CHAVE_DO_ENSAIO = bytes(range(100, 132))
PUBLICA_DO_ENSAIO = assinatura.secret_to_public(CHAVE_DO_ENSAIO).hex()
SEM_JANELA = getattr(subprocess, "CREATE_NO_WINDOW", 0)

APP = '''"""Programinha do ensaio: so a cola da atualizacao do Editor de Impressao."""
import os, sys
ESTRAGADA = {estragada}
if sys.argv[1:2] == ["--teste-rapido"]:
    sys.exit(1 if ESTRAGADA else 0)
if sys.argv[1:2] == ["--qual-versao"]:
    import versao
    open(sys.argv[2], "w", encoding="utf-8").write(versao.VERSAO)
    sys.exit(0)
from atualizacao import atender_linha_de_comando
codigo = atender_linha_de_comando(sys.argv)
sys.exit(codigo or 0)
'''


def _fonte_do_programinha(destino: Path, numero: str, estragada: bool) -> Path:
    """Copia atualizacao.py, assinatura.py e versao.py, trocando so o numero, o
    nome do pacote e a chave publica (a de mentira)."""
    destino.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RAIZ / "atualizacao.py", destino / "atualizacao.py")
    texto = (RAIZ / "assinatura.py").read_text(encoding="utf-8")
    texto = texto.replace(f'CHAVE_PUBLICA_DO_SAMUEL = "{assinatura.CHAVE_PUBLICA_DO_SAMUEL}"',
                          f'CHAVE_PUBLICA_DO_SAMUEL = "{PUBLICA_DO_ENSAIO}"')
    assert PUBLICA_DO_ENSAIO in texto
    (destino / "assinatura.py").write_text(texto, encoding="utf-8")
    texto = (RAIZ / "versao.py").read_text(encoding="utf-8")
    texto = texto.replace(f'VERSAO = "{versao.VERSAO}"', f'VERSAO = "{numero}"')
    texto = texto.replace(f'ID_DO_PACOTE = "{versao.ID_DO_PACOTE}"', f'ID_DO_PACOTE = "{ID_DO_ENSAIO}"')
    (destino / "versao.py").write_text(texto, encoding="utf-8")
    (destino / "app.py").write_text(APP.format(estragada=estragada), encoding="utf-8")
    return destino / "app.py"


def _empacotar_programinha(numero: str, estragada: bool = False) -> Path:
    fonte = _fonte_do_programinha(PASTA / "fonte" / numero, numero, estragada)
    dist = PASTA / "dist" / numero
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--onedir", "--windowed",
                    "--name", "EditorImpressao", "--distpath", str(dist),
                    "--workpath", str(PASTA / "pyi" / numero), "--specpath", str(PASTA / "pyi" / numero),
                    "--paths", str(fonte.parent), "--log-level", "WARN", str(fonte)],
                   check=True, creationflags=SEM_JANELA)
    pasta = dist / "EditorImpressao"
    assert list(pasta.rglob("velopack*.pyd")), "o PyInstaller não levou o velopack"
    return pasta


def _publicar(numero: str, estragada: bool = False) -> None:
    pasta = _empacotar_programinha(numero, estragada)
    pub.publicar(numero, destino_pasta=SERVIDOR, pasta_pronta=pasta, arquivo_da_chave=PASTA / "chave.txt",
                 chave_publica=PUBLICA_DO_ENSAIO)


def _ambiente() -> dict:
    return {**os.environ, "PROGRAMDATA": str(DADOS), "LOCALAPPDATA": str(PASTA / "LocalAppData"),
            "QT_QPA_PLATFORM": "offscreen"}


def _qual_versao() -> str:
    saida = PASTA / "versao-que-abriu.txt"
    saida.unlink(missing_ok=True)
    subprocess.run([str(INSTALADO / "current" / "EditorImpressao.exe"), "--qual-versao", str(saida)],
                   env=_ambiente(), creationflags=SEM_JANELA, timeout=60)
    return saida.read_text(encoding="utf-8")


def _estado() -> dict:
    try:
        return json.loads((DADOS / "EditorImpressao" / "atualizacao" / "estado.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _procurar_e_esperar(espera_versao: str, espera_fase: str, limite: int = 240) -> dict:
    """Roda --procurar-atualizacao e espera o Velopack trocar (e reabrir) ate a versao e a fase esperadas."""
    subprocess.run([str(INSTALADO / "current" / "EditorImpressao.exe"), "--procurar-atualizacao",
                    "--fonte", str(SERVIDOR)], env=_ambiente(), creationflags=SEM_JANELA, timeout=600)
    fim = time.time() + limite
    while time.time() < fim:
        time.sleep(3)
        try:
            if _estado().get("fase") == espera_fase and _qual_versao() == espera_versao:
                break
        except (OSError, subprocess.SubprocessError):
            pass   # no meio da troca a pasta current some por um instante
    time.sleep(5)
    return {"versao": _qual_versao(), "estado": _estado()}


def main() -> int:
    if PASTA.exists():
        shutil.rmtree(PASTA)
    PASTA.mkdir(parents=True)
    (PASTA / "chave.txt").write_text(assinatura.texto_da_chave_privada(CHAVE_DO_ENSAIO), encoding="utf-8")
    # o ensaio usa o seu proprio nome de pacote (nunca o do programa) e confere
    # o pacote so pelo .exe (o programinha nao tem modelos nem DLLs)
    versao.ID_DO_PACOTE = ID_DO_ENSAIO
    empacotar.esperados_no_pacote_do_velopack = lambda pecas: ["EditorImpressao.exe"]
    pub.RAIZ = PASTA / "fora-do-repositorio"   # a chave de mentira mora em build\ (rascunho)
    resultado: dict = {}

    _publicar("1.1.0")
    portatil = next(SERVIDOR.glob("*-Portable.zip"))
    with zipfile.ZipFile(portatil) as z:
        z.extractall(INSTALADO)
    resultado["arquivos do servidor"] = sorted(p.name for p in SERVIDOR.iterdir())
    resultado["0 instalada (portatil)"] = _qual_versao()

    _publicar("1.2.0")
    resultado["A 1.1.0 -> 1.2.0"] = _procurar_e_esperar("1.2.0", "ok")

    _publicar("1.3.0", estragada=True)
    resultado["B 1.3.0 estragada -> volta"] = _procurar_e_esperar("1.2.0", "falhou")

    _publicar("1.4.0")
    outra = bytes(range(1, 33))
    nupkg = SERVIDOR / f"{ID_DO_ENSAIO}-1.4.0-full.nupkg"
    v = assinatura.VersaoAssinada(ID_DO_ENSAIO, "1.4.0", nupkg.name, assinatura.soma_sha256(nupkg))
    (SERVIDOR / assinatura.nome_do_arquivo_da_assinatura(ID_DO_ENSAIO, "1.4.0")).write_text(
        assinatura.escrever_assinatura(outra, v), encoding="utf-8")
    subprocess.run([str(INSTALADO / "current" / "EditorImpressao.exe"), "--procurar-atualizacao",
                    "--fonte", str(SERVIDOR)], env=_ambiente(), creationflags=SEM_JANELA, timeout=600)
    time.sleep(5)
    pacotes = sorted(p.name for p in (INSTALADO / "packages").glob("*.nupkg"))
    resultado["C 1.4.0 com a assinatura de outra chave"] = {"versao": _qual_versao(), "estado": _estado(),
                                                            "pacotes baixados": pacotes}
    registro = DADOS / "EditorImpressao" / "atualizacao" / "atualizacao.log"
    resultado["registro"] = registro.read_text(encoding="utf-8").splitlines() if registro.exists() else []
    (PASTA / "resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=1))
    certo = (resultado["0 instalada (portatil)"] == "1.1.0"
             and resultado["A 1.1.0 -> 1.2.0"]["versao"] == "1.2.0"
             and resultado["A 1.1.0 -> 1.2.0"]["estado"].get("fase") == "ok"
             and resultado["B 1.3.0 estragada -> volta"]["versao"] == "1.2.0"
             and resultado["B 1.3.0 estragada -> volta"]["estado"].get("id") == "teste-1.3.0"
             and resultado["C 1.4.0 com a assinatura de outra chave"]["versao"] == "1.2.0"
             and resultado["C 1.4.0 com a assinatura de outra chave"]["estado"].get("id") == "recusada-1.4.0"
             and not any("1.4.0" in p for p in pacotes))
    print("\nENSAIO:", "CERTO" if certo else "NAO DEU CERTO")
    return 0 if certo else 1


if __name__ == "__main__":
    raise SystemExit(main())
