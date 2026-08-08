"""Gera o programa pronto para entregar (Etapa 8).

    python empacotar.py                 # tudo: pasta + arquivo único + instalador
    python empacotar.py --modo pasta        # só a versão portatil em pasta
    python empacotar.py --modo arquivo      # só o .exe único (pendrive)
    python empacotar.py --modo instalador   # pasta + EditorImpressao-Setup.exe

Sai tudo em dist/:

    dist\\EditorImpressao\\                 versão em pasta - abre em ~8 s
    dist\\EditorImpressao.exe               arquivo único  - abre em ~12 s
    dist\\EditorImpressao-Setup.exe         instalador do Windows

A versão em pasta e a que o instalador empacota: o arquivo único se descompacta
inteiro a cada abertura, o que custa uns 4 segundos a mais. Os dois demoram
alguns segundos de qualquer jeito - e o custo de carregar Qt e OpenCV.
(Medido nesta maquina, em aberturas repetidas.)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

NOME = "EditorImpressao"
RAIZ = Path(__file__).parent

# CAMINHO EM DISCO, nao texto de tela: e a pasta que aparece na Area de
# Trabalho do usuário. Trocar isto faz a pasta "mudar de lugar" para quem ja
# estava acostumado com a anterior - por isso os nomes antigos ficam listados,
# para serem apagados em vez de virarem uma segunda pasta parecida.
PASTA_DE_ENTREGA = "Editor de Impressão"
OUTROS_NOMES_DE_ENTREGA = ("Editor de Impressao", "PROGRAMA PRONTO - Editor de Impressao")

# Onde o Inno Setup costuma ficar. O winget instala no perfil do usuario.
CAMINHOS_DO_INNO = [
    Path.home() / "AppData/Local/Programs/Inno Setup 6/ISCC.exe",
    Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe"),
    Path("C:/Program Files/Inno Setup 6/ISCC.exe"),
]

# O PySide6 traz muita coisa que este programa nunca usa. Tirar reduz o tamanho
# em dezenas de MB e diminui o tempo de abertura.
EXCLUIR = [
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtWebEngineQuick",
    "PySide6.QtQuick", "PySide6.QtQml", "PySide6.Qt3DCore", "PySide6.Qt3DRender",
    "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets", "PySide6.QtCharts",
    "PySide6.QtDataVisualization", "PySide6.QtBluetooth", "PySide6.QtNetworkAuth",
    "PySide6.QtPositioning", "PySide6.QtSensors", "PySide6.QtSerialPort",
    "PySide6.QtSql", "PySide6.QtTest", "PySide6.QtDesigner", "PySide6.QtHelp",
    "matplotlib", "scipy", "pandas", "IPython", "tkinter", "pytest",
]

# O DoxaPy e uma biblioteca nativa: o PyInstaller nao acha sozinho.
OCULTOS = ["doxapy", "skimage.filters", "PIL._tkinter_finder"]


def _tamanho(caminho: Path) -> str:
    if caminho.is_file():
        mb = caminho.stat().st_size / 1024 / 1024
    else:
        mb = sum(f.stat().st_size for f in caminho.rglob("*") if f.is_file()) / 1024 / 1024
    return f"{mb:.0f} MB"


def _pyinstaller(onefile: bool) -> bool:
    """Roda o PyInstaller. onefile=False gera a versão em pasta."""
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onefile" if onefile else "--onedir",
        "--windowed",                     # sem janela preta de console atras
        "--name", NOME,
        "--paths", str(RAIZ),
        "--distpath", str(RAIZ / "dist"),
        "--workpath", str(RAIZ / "build" / ("arquivo" if onefile else "pasta")),
        "--specpath", str(RAIZ / "build"),
    ]
    for modulo in EXCLUIR:
        comando += ["--exclude-module", modulo]
    for modulo in OCULTOS:
        comando += ["--hidden-import", modulo]

    recursos = RAIZ / "recursos"
    if recursos.exists() and any(recursos.iterdir()):
        separador = ";" if sys.platform == "win32" else ":"
        comando += ["--add-data", f"{recursos}{separador}recursos"]

    comando.append(str(RAIZ / "main.py"))
    return subprocess.run(comando, cwd=RAIZ).returncode == 0


def achar_inno() -> Path | None:
    for caminho in CAMINHOS_DO_INNO:
        if caminho.exists():
            return caminho
    achado = shutil.which("ISCC")
    return Path(achado) if achado else None


def construir_pasta() -> Path | None:
    """Versao portatil em pasta. E tambem o que o instalador empacota."""
    print("\n=== Versao em pasta (portatil, abre na hora) ===")
    destino = RAIZ / "dist" / NOME
    shutil.rmtree(destino, ignore_errors=True)

    if not _pyinstaller(onefile=False):
        print("  falhou")
        return None
    if not (destino / f"{NOME}.exe").exists():
        print("  o PyInstaller terminou mas o programa não apareceu")
        return None

    # Um bilhete dentro da pasta, para quem receber so ela
    (destino / "COMO USAR.txt").write_text(
        "Editor de Impressão - versão portatil\r\n"
        "\r\n"
        "Não precisa instalar nada. De dois cliques em EditorImpressao.exe.\r\n"
        "A primeira tela leva uns 8 segundos para aparecer.\r\n"
        "\r\n"
        "A pasta inteira precisa andar junto - se copiar só o .exe,\r\n"
        "o programa não abre. Para levar um arquivo só, use a versão\r\n"
        "EditorImpressao.exe que fica fora desta pasta.\r\n",
        encoding="utf-8",
    )
    print(f"  pronto: {destino}  ({_tamanho(destino)})")
    return destino


def construir_arquivo_unico() -> Path | None:
    """Um .exe só, para levar no pendrive."""
    print("\n=== Arquivo único (pendrive) ===")
    destino = RAIZ / "dist" / f"{NOME}.exe"
    destino.unlink(missing_ok=True)

    if not _pyinstaller(onefile=True) or not destino.exists():
        print("  falhou")
        return None

    print(f"  pronto: {destino}  ({_tamanho(destino)})")
    print("  atenção: abre uns 4 segundos mais devagar que a versão em pasta")
    return destino


def construir_instalador() -> Path | None:
    """EditorImpressao-Setup.exe, com atalhos e desinstalador."""
    print("\n=== Instalador do Windows ===")

    # A pasta e SEMPRE refeita. Antes, ela era reaproveitada quando ja existia,
    # e o instalador saia com o codigo de uma compilacao anterior sem avisar
    # nada - o arquivo tem data de hoje e conteudo de ontem. E o pior tipo de
    # erro: o instalador parece pronto e leva o programa errado ao Kaique.
    pasta = RAIZ / "dist" / NOME
    if (pasta / f"{NOME}.exe").exists():
        print("  refazendo a versão em pasta, para o instalador nao levar")
        print("  codigo de uma compilacao anterior")
    if construir_pasta() is None:
        return None

    inno = achar_inno()
    if inno is None:
        print("  Inno Setup não encontrado.")
        print("  Instale com:  winget install --id JRSoftware.InnoSetup")
        return None

    script = RAIZ / "instalador.iss"
    if not script.exists():
        print(f"  {script.name} não encontrado")
        return None

    resultado = subprocess.run(
        [str(inno), str(script)], cwd=RAIZ, capture_output=True, text=True
    )
    if resultado.returncode != 0:
        print("  o Inno Setup recusou o script:")
        for linha in (resultado.stdout + resultado.stderr).splitlines()[-12:]:
            print(f"    {linha}")
        return None

    destino = RAIZ / "dist" / f"{NOME}-Setup.exe"
    if not destino.exists():
        print("  o Inno Setup terminou mas o instalador não apareceu")
        return None

    print(f"  pronto: {destino}  ({_tamanho(destino)})")
    return destino


def entregar() -> Path | None:
    """Gera SO o instalador e deixa ele sozinho na Área de Trabalho.

    Tudo o mais e apagado no fim: build/, dist/ e qualquer versão portatil.
    O que sobra para o usuario final e um arquivo único.
    """
    print("\n=== Entrega: só o instalador ===")

    if construir_instalador() is None:
        return None

    pasta = Path.home() / "Desktop" / PASTA_DE_ENTREGA
    print(f"\n  preparando {pasta}")
    if pasta.exists():
        shutil.rmtree(pasta, ignore_errors=True)
    pasta.mkdir(parents=True, exist_ok=True)

    # Se sobrou a pasta de uma versão anterior, com outro nome, ela vai embora:
    # duas pastas parecidas na Area de Trabalho, uma com o instalador velho, e
    # o usuário nao sabe qual abrir.
    for antigo in OUTROS_NOMES_DE_ENTREGA:
        velha = Path.home() / "Desktop" / antigo
        if velha.is_dir() and velha != pasta:
            print(f"  removendo a pasta antiga: {velha.name}")
            shutil.rmtree(velha, ignore_errors=True)

    origem = RAIZ / "dist" / f"{NOME}-Setup.exe"
    destino = pasta / f"{NOME}-Setup.exe"
    shutil.copy2(origem, destino)

    print("  limpando as sobras do empacotamento")
    shutil.rmtree(RAIZ / "build", ignore_errors=True)
    shutil.rmtree(RAIZ / "dist", ignore_errors=True)

    sobrando = [f.name for f in pasta.iterdir()]
    if sobrando != [f"{NOME}-Setup.exe"]:
        print(f"  ATENCAO: sobrou coisa a mais na pasta: {sobrando}")

    print(f"\n  pronto: {destino}  ({_tamanho(destino)})")
    return destino


def main() -> int:
    analisador = argparse.ArgumentParser(
        description="Gera o Editor de Impressão pronto para entregar."
    )
    analisador.add_argument(
        "--modo",
        choices=["tudo", "pasta", "arquivo", "instalador", "entrega"],
        default="tudo",
        help="entrega = só o instalador, na Área de Trabalho, e apaga o resto",
    )
    argumentos = analisador.parse_args()

    if argumentos.modo == "entrega":
        inicio = time.perf_counter()
        shutil.rmtree(RAIZ / "build", ignore_errors=True)
        shutil.rmtree(RAIZ / "dist", ignore_errors=True)
        resultado = entregar()
        print(f"\nTerminou em {time.perf_counter() - inicio:.0f} s")
        return 0 if resultado else 1

    inicio = time.perf_counter()
    shutil.rmtree(RAIZ / "build", ignore_errors=True)

    resultados: dict[str, Path | None] = {}

    if argumentos.modo in ("tudo", "pasta"):
        resultados["versão em pasta"] = construir_pasta()
    if argumentos.modo in ("tudo", "arquivo"):
        resultados["arquivo único"] = construir_arquivo_unico()
    if argumentos.modo in ("tudo", "instalador"):
        resultados["instalador"] = construir_instalador()

    print(f"\n{'=' * 52}")
    print(f"Terminou em {time.perf_counter() - inicio:.0f} s\n")
    for nome, caminho in resultados.items():
        marca = "ok    " if caminho else "FALHOU"
        print(f"  [{marca}] {nome:<16} {caminho or ''}")

    return 0 if all(resultados.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
