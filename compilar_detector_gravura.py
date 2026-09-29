"""Compila o detector de gravura do ScanTailor Advanced (item 1.2 da Fase 1).

    .venv\\Scripts\\python.exe compilar_detector_gravura.py            # compila
    .venv\\Scripts\\python.exe compilar_detector_gravura.py --baixar   # baixa o que faltar e compila

O QUE FAZ

1. Acha as ferramentas: o CMake e o Visual Studio 2022 Build Tools (C++).
2. Acha (ou, com --baixar, baixa e confere) o Qt de desenvolvimento e os
   cabeçalhos do Boost, numa pasta FORA do git:
   D:\\programas\\EditorImpressao-arquivos\\ferramentas\\ (mude com --ferramentas).
   - Qt: só a parte "qtbase" do Qt 6.11.1 para MSVC 2022 64 bits, direto do
     servidor oficial (download.qt.io), conferido pela soma SHA-1 que o
     próprio servidor publica. É a MESMA versão do Qt que o PySide6 do .venv
     traz; o script recusa compilar se as versões não baterem.
   - Boost 1.78.0 (a versão das instruções de compilação do ScanTailor para
     Windows), conferido pela soma SHA-256 publicada em archives.boost.io. Só
     a pasta boost/ (cabeçalhos) é extraída.
3. Compila terceiros/scantailor-advanced/ligacao (CMake + MSVC, Release) na
   pasta de rascunho <ferramentas>\\build-st-gravura.
4. Copia a DLL para core/nativo/st_gravura.dll e grava, ao lado,
   core/nativo/st_gravura.txt dizendo de onde ela veio e a soma SHA-256.
5. Carrega a DLL pelo core/gravura_scantailor.py e roda uma página sintética,
   para garantir que ela abre com o Qt do PySide6.

NADA AQUI PEDE ADMINISTRADOR. Nada é instalado no Windows nem no .venv.

O Kaique não precisa rodar isto: a DLL pronta vai no programa. Só é preciso
recompilar se o código em terceiros/scantailor-advanced mudar, ou se o PySide6
mudar de versão do Qt.

Arriscado mudar: VERSAO_QT (tem de ser a do PySide6), as URLs e as somas
(são a garantia de que o arquivo baixado é o oficial).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PASTA_LIGACAO = RAIZ / "terceiros" / "scantailor-advanced" / "ligacao"
PASTA_NATIVO = RAIZ / "core" / "nativo"
NOME_DLL = "st_gravura.dll"

# De onde veio o código do ScanTailor (conferir com terceiros/scantailor-advanced/LEIA-ME.md).
REPOSITORIO = "https://github.com/ScanTailor-Advanced/scantailor-advanced"
VERSAO_SCANTAILOR = "v1.2.1"
COMMIT_SCANTAILOR = "5eaac1884cdcabb6514bd632114f688631bd8dbc"

# Qt: a mesma versão do PySide6 do .venv.
VERSAO_QT = "6.11.1"
_BASE_QT = ("https://download.qt.io/online/qtsdkrepository/windows_x86/desktop/"
            "qt6_6111/qt6_6111_msvc2022_64/qt.qt6.6111.win64_msvc2022_64/")
ARQUIVO_QT = ("6.11.1-0-202605090529qtbase-Windows-Windows_11_24H2-MSVC2022-"
              "Windows-Windows_11_24H2-X86_64.7z")

# Boost: só cabeçalhos.
VERSAO_BOOST = "1.78.0"
URL_BOOST = "https://archives.boost.io/release/1.78.0/source/boost_1_78_0.7z"
SHA256_BOOST = "090cefea470bca990fa3f3ed793d865389426915b37a2a3258524a7258f0790c"

PASTA_FERRAMENTAS_PADRAO = RAIZ.parent / "EditorImpressao-arquivos" / "ferramentas"

CMAKE_CANDIDATOS = [
    Path(r"C:\Program Files\CMake\bin\cmake.exe"),
    Path(r"C:\Program Files (x86)\CMake\bin\cmake.exe"),
]
VCVARS = Path(r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
              r"\VC\Auxiliary\Build\vcvars64.bat")


class ErroDeCompilacao(Exception):
    """Algo impede a compilação; a mensagem diz o quê, em português."""


def dizer(texto: str) -> None:
    print(texto, flush=True)


# ---------------------------------------------------------------- ferramentas

def achar_cmake() -> Path:
    """O cmake.exe: primeiro o do PATH, depois as pastas de instalação comuns."""
    no_path = shutil.which("cmake")
    if no_path:
        return Path(no_path)
    for candidato in CMAKE_CANDIDATOS:
        if candidato.is_file():
            return candidato
    raise ErroDeCompilacao("Não achei o CMake. Instale pelo winget (Kitware.CMake).")


def conferir_visual_studio() -> None:
    """O compilador C++ do Visual Studio 2022 (Build Tools, 'Desenvolvimento para desktop com C++')."""
    if not VCVARS.is_file():
        raise ErroDeCompilacao(
            "Não achei o Visual Studio 2022 Build Tools com C++ "
            f"(faltou {VCVARS}). A instalação pede administrador: avise antes de instalar.")


def versao_do_qt_do_pyside() -> str:
    """A versão do Qt que o PySide6 do programa traz (ex.: 6.11.1)."""
    from PySide6 import QtCore

    return QtCore.qVersion()


# ---------------------------------------------------------------- downloads

def _baixar(url: str, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_suffix(destino.suffix + ".parcial")
    dizer(f"  baixando {url}")
    with urllib.request.urlopen(url, timeout=120) as resposta, parcial.open("wb") as saida:
        shutil.copyfileobj(resposta, saida, length=1 << 20)
    parcial.replace(destino)


def _soma(caminho: Path, algoritmo: str) -> str:
    h = hashlib.new(algoritmo)
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _extrair(cmake: Path, arquivo: Path, destino: Path, membros: list[str] | None = None) -> None:
    """Extrai um .7z com o próprio CMake (cmake -E tar sabe ler 7z): nada a instalar."""
    destino.mkdir(parents=True, exist_ok=True)
    comando = [str(cmake), "-E", "tar", "xf", str(arquivo)] + (membros or [])
    subprocess.run(comando, cwd=destino, check=True)


def pasta_do_qt(ferramentas: Path) -> Path:
    return ferramentas / "qt" / VERSAO_QT / "msvc2022_64"


def pasta_do_boost(ferramentas: Path) -> Path:
    return ferramentas / "boost" / "boost_1_78_0"


def garantir_qt(ferramentas: Path, cmake: Path, baixar: bool) -> Path:
    """O Qt de desenvolvimento (cabeçalhos + .lib + arquivos do CMake)."""
    pasta = pasta_do_qt(ferramentas)
    if (pasta / "lib" / "cmake" / "Qt6" / "Qt6Config.cmake").is_file():
        return pasta
    if not baixar:
        raise ErroDeCompilacao(f"Falta o Qt de desenvolvimento em {pasta}. Rode com --baixar.")
    arquivo = ferramentas / "downloads" / f"qtbase-{VERSAO_QT}-msvc2022_64.7z"
    if not arquivo.is_file():
        _baixar(_BASE_QT + ARQUIVO_QT, arquivo)
    soma_oficial = urllib.request.urlopen(_BASE_QT + ARQUIVO_QT + ".sha1", timeout=60).read()
    soma_oficial = soma_oficial.decode("ascii").split()[0].strip().lower()
    if _soma(arquivo, "sha1") != soma_oficial:
        arquivo.unlink(missing_ok=True)
        raise ErroDeCompilacao("O Qt baixado não bate com a soma oficial; apaguei. Tente de novo.")
    dizer("  extraindo o Qt (cerca de 1 minuto)")
    _extrair(cmake, arquivo, pasta)
    return pasta


def garantir_boost(ferramentas: Path, cmake: Path, baixar: bool) -> Path:
    """Os cabeçalhos do Boost (o ScanTailor não usa nenhuma parte compilada no detector)."""
    pasta = pasta_do_boost(ferramentas)
    if (pasta / "boost" / "config.hpp").is_file():
        return pasta
    if not baixar:
        raise ErroDeCompilacao(f"Faltam os cabeçalhos do Boost em {pasta}. Rode com --baixar.")
    arquivo = ferramentas / "downloads" / "boost_1_78_0.7z"
    if not arquivo.is_file():
        _baixar(URL_BOOST, arquivo)
    if _soma(arquivo, "sha256") != SHA256_BOOST:
        arquivo.unlink(missing_ok=True)
        raise ErroDeCompilacao("O Boost baixado não bate com a soma oficial; apaguei. Tente de novo.")
    dizer("  extraindo os cabeçalhos do Boost")
    _extrair(cmake, arquivo, pasta.parent, ["boost_1_78_0/boost", "boost_1_78_0/LICENSE_1_0.txt"])
    return pasta


# ---------------------------------------------------------------- compilação

def texto_de_origem() -> str:
    return (f"ScanTailor-Advanced/scantailor-advanced {VERSAO_SCANTAILOR} "
            f"(commit {COMMIT_SCANTAILOR[:12]}), Qt {VERSAO_QT}")


def compilar(ferramentas: Path, cmake: Path, qt: Path, boost: Path) -> Path:
    """Configura e compila; devolve o caminho da DLL gerada (na pasta de rascunho)."""
    rascunho = ferramentas / "build-st-gravura"
    configurar = [
        str(cmake), "-S", str(PASTA_LIGACAO), "-B", str(rascunho),
        "-G", "Visual Studio 17 2022", "-A", "x64",
        f"-DCMAKE_PREFIX_PATH={qt.as_posix()}",
        f"-DBOOST_INCLUDEDIR={boost.as_posix()}",
        f"-DST_GRAVURA_ORIGEM={texto_de_origem()}",
    ]
    dizer("  configurando (CMake)")
    subprocess.run(configurar, check=True)
    dizer("  compilando (MSVC, Release)")
    subprocess.run([str(cmake), "--build", str(rascunho), "--config", "Release", "--parallel"], check=True)
    dll = rascunho / "Release" / NOME_DLL
    if not dll.is_file():
        raise ErroDeCompilacao(f"A compilação terminou, mas não achei {dll}.")
    return dll


def versao_do_compilador(rascunho: Path) -> str:
    """A versao do MSVC que o CMake achou (CMakeFiles/<versao>/CMakeCXXCompiler.cmake)."""
    for arquivo in sorted(rascunho.glob("CMakeFiles/*/CMakeCXXCompiler.cmake")):
        for linha in arquivo.read_text(encoding="utf-8", errors="replace").splitlines():
            if linha.startswith('set(CMAKE_CXX_COMPILER_VERSION "'):
                return "MSVC " + linha.split('"')[1]
    return "MSVC 2022 (Build Tools)"


def instalar_no_programa(dll: Path) -> Path:
    """Copia a DLL para core/nativo/ e grava o texto de origem ao lado."""
    PASTA_NATIVO.mkdir(parents=True, exist_ok=True)
    destino = PASTA_NATIVO / NOME_DLL
    shutil.copy2(dll, destino)
    soma = _soma(destino, "sha256")
    compilador = versao_do_compilador(dll.parent.parent)
    (PASTA_NATIVO / "st_gravura.txt").write_text(
        "st_gravura.dll - detector de gravura do ScanTailor Advanced (item 1.2 da Fase 1)\n"
        "\n"
        f"Código:      {REPOSITORIO}\n"
        f"Versão:      {VERSAO_SCANTAILOR} (commit {COMMIT_SCANTAILOR})\n"
        "Fontes:      terceiros/scantailor-advanced/ (licença GPL-3, ver LEIA-ME.md lá)\n"
        f"Qt:          {VERSAO_QT} (o do PySide6; a DLL usa as DLLs do Qt da pasta do PySide6)\n"
        f"Compilador:  {compilador}\n"
        f"Compilada:   {datetime.now():%d/%m/%Y %H:%M} por compilar_detector_gravura.py\n"
        f"Tamanho:     {destino.stat().st_size} bytes\n"
        f"SHA-256:     {soma}\n",
        encoding="utf-8")
    return destino


def testar_a_dll() -> str:
    """Abre a DLL pelo módulo do programa e roda uma página sintética."""
    import numpy as np

    sys.path.insert(0, str(RAIZ))
    from core.gravura_scantailor import DetectorGravuraScanTailor

    detector = DetectorGravuraScanTailor()
    pagina = np.full((600, 450, 3), 235, np.uint8)
    pagina[150:450, 100:350] = 128
    resultado = detector.detectar(pagina, 150)
    if not resultado.disponivel:
        raise ErroDeCompilacao(f"A DLL foi gerada, mas não abriu: {resultado.motivo}")
    return detector.origem or "?"


def main(argumentos: list[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(description="Compila o detector de gravura do ScanTailor.")
    analisador.add_argument("--baixar", action="store_true",
                            help="baixa o Qt e o Boost que faltarem (fora do git)")
    analisador.add_argument("--ferramentas", type=Path, default=PASTA_FERRAMENTAS_PADRAO,
                            help="pasta do Qt, do Boost e do rascunho da compilação")
    opcoes = analisador.parse_args(argumentos)

    inicio = time.perf_counter()
    try:
        if os.name != "nt":
            raise ErroDeCompilacao("Este script só compila no Windows.")
        versao_pyside = versao_do_qt_do_pyside()
        if versao_pyside != VERSAO_QT:
            raise ErroDeCompilacao(
                f"O PySide6 do programa usa o Qt {versao_pyside}, e este script compila para o "
                f"Qt {VERSAO_QT}. Mude VERSAO_QT, _BASE_QT e ARQUIVO_QT juntos.")
        dizer("1/5 ferramentas")
        cmake = achar_cmake()
        conferir_visual_studio()
        dizer(f"  CMake: {cmake}")
        dizer("2/5 Qt e Boost")
        qt = garantir_qt(opcoes.ferramentas, cmake, opcoes.baixar)
        boost = garantir_boost(opcoes.ferramentas, cmake, opcoes.baixar)
        dizer(f"  Qt:    {qt}\n  Boost: {boost}")
        dizer("3/5 compilação")
        dll = compilar(opcoes.ferramentas, cmake, qt, boost)
        dizer("4/5 copiando para core/nativo/")
        destino = instalar_no_programa(dll)
        dizer("5/5 testando a DLL com o Qt do PySide6")
        origem = testar_a_dll()
    except ErroDeCompilacao as erro:
        dizer(f"\nNÃO COMPILOU: {erro}")
        return 1
    except subprocess.CalledProcessError as erro:
        dizer(f"\nNÃO COMPILOU: o comando falhou ({erro}). Veja as mensagens acima.")
        return 1
    dizer(f"\nPronto em {time.perf_counter() - inicio:.0f} s: {destino} "
          f"({destino.stat().st_size / 1024:.0f} KB)\n  origem: {origem}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
