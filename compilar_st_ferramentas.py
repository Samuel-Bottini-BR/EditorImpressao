"""Compila a DLL comum das ferramentas do ScanTailor Advanced (item M9 da Fase 2).

    .venv\\Scripts\\python.exe compilar_st_ferramentas.py            # compila
    .venv\\Scripts\\python.exe compilar_st_ferramentas.py --baixar   # baixa o que faltar e compila

O QUE FAZ

O mesmo caminho do compilar_detector_gravura.py (item 1.2), de onde vêm as
peças (ferramentas, Qt, Boost, somas oficiais):
1. acha o CMake e o Visual Studio 2022 Build Tools (C++);
2. acha (ou, com --baixar, baixa e confere) o Qt 6.11.1 de desenvolvimento e os
   cabeçalhos do Boost 1.78.0, FORA do git
   (D:\\programas\\EditorImpressao-arquivos\\ferramentas\\);
3. compila terceiros/scantailor-advanced/ligacao-ferramentas (CMake + MSVC,
   Release) na pasta de rascunho <ferramentas>\\build-st-ferramentas;
4. copia a DLL para core/nativo/st_ferramentas.dll e grava, ao lado,
   core/nativo/st_ferramentas.txt (origem e soma SHA-256);
5. abre a DLL pelo core/st_ferramentas.py e limpa uma imagem sintética, para
   garantir que ela abre com o Qt do PySide6.

NADA AQUI PEDE ADMINISTRADOR. Nada é instalado no Windows nem no .venv.
O Kaique não precisa rodar isto: a DLL pronta vai no programa.

A st_gravura.dll (detector de gravura do 1.2) NÃO é tocada: continua com o
compilar_detector_gravura.py. Ver terceiros/scantailor-advanced/LEIA-ME.md,
"Duas DLLs".

Arriscado mudar: o que vem do compilar_detector_gravura (VERSAO_QT, URLs e
somas): é a garantia de que o Qt e o Boost são os oficiais e o Qt é o do PySide6.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import compilar_detector_gravura as base
from compilar_detector_gravura import ErroDeCompilacao, dizer

RAIZ = Path(__file__).resolve().parent
PASTA_LIGACAO = RAIZ / "terceiros" / "scantailor-advanced" / "ligacao-ferramentas"
PASTA_NATIVO = RAIZ / "core" / "nativo"
NOME_DLL = "st_ferramentas.dll"
NOME_RASCUNHO = "build-st-ferramentas"


def pasta_de_ferramentas_padrao() -> Path:
    """A pasta EditorImpressao-arquivos\\ferramentas ao lado do projeto.

    O compilar_detector_gravura procura só ao lado da pasta do script; numa
    cópia de trabalho (git worktree, em .claude\\worktrees\\<nome>) ela fica
    alguns níveis acima. Procura subindo; se não achar, fica a do
    compilar_detector_gravura (a mensagem de erro dele diz o que falta).
    """
    for pasta in RAIZ.parents:
        candidata = pasta / "EditorImpressao-arquivos" / "ferramentas"
        if candidata.is_dir():
            return candidata
    return base.PASTA_FERRAMENTAS_PADRAO


def compilar(ferramentas: Path, cmake: Path, qt: Path, boost: Path) -> Path:
    """Configura e compila; devolve o caminho da DLL gerada (na pasta de rascunho)."""
    rascunho = ferramentas / NOME_RASCUNHO
    configurar = [
        str(cmake), "-S", str(PASTA_LIGACAO), "-B", str(rascunho),
        "-G", "Visual Studio 17 2022", "-A", "x64",
        f"-DCMAKE_PREFIX_PATH={qt.as_posix()}",
        f"-DBOOST_INCLUDEDIR={boost.as_posix()}",
        f"-DST_FERRAMENTAS_ORIGEM={base.texto_de_origem()}",
    ]
    dizer("  configurando (CMake)")
    subprocess.run(configurar, check=True)
    dizer("  compilando (MSVC, Release)")
    subprocess.run([str(cmake), "--build", str(rascunho), "--config", "Release", "--parallel"],
                   check=True)
    dll = rascunho / "Release" / NOME_DLL
    if not dll.is_file():
        raise ErroDeCompilacao(f"A compilação terminou, mas não achei {dll}.")
    return dll


def instalar_no_programa(dll: Path) -> Path:
    """Copia a DLL para core/nativo/ e grava o texto de origem ao lado."""
    PASTA_NATIVO.mkdir(parents=True, exist_ok=True)
    destino = PASTA_NATIVO / NOME_DLL
    shutil.copy2(dll, destino)
    soma = base._soma(destino, "sha256")
    compilador = base.versao_do_compilador(dll.parent.parent)
    (PASTA_NATIVO / "st_ferramentas.txt").write_text(
        "st_ferramentas.dll - ferramentas de imagem do ScanTailor Advanced (item M9 da Fase 2)\n"
        "Tem: limpar pontinhos (Despeckle).\n"
        "\n"
        f"Código:      {base.REPOSITORIO}\n"
        f"Versão:      {base.VERSAO_SCANTAILOR} (commit {base.COMMIT_SCANTAILOR})\n"
        "Fontes:      terceiros/scantailor-advanced/src (licença GPL-3, ver LEIA-ME.md lá)\n"
        "Ligação:     terceiros/scantailor-advanced/ligacao-ferramentas\n"
        f"Qt:          {base.VERSAO_QT} (o do PySide6; a DLL usa as DLLs do Qt da pasta do PySide6)\n"
        f"Compilador:  {compilador}\n"
        f"Compilada:   {datetime.now():%d/%m/%Y %H:%M} por compilar_st_ferramentas.py\n"
        f"Tamanho:     {destino.stat().st_size} bytes\n"
        f"SHA-256:     {soma}\n",
        encoding="utf-8")
    return destino


def testar_a_dll() -> str:
    """Abre a DLL pelo módulo do programa e limpa uma imagem sintética."""
    import numpy as np

    sys.path.insert(0, str(RAIZ))
    from core import pontinhos_scantailor as ps
    from core.st_ferramentas import BibliotecaScanTailor

    biblioteca = BibliotecaScanTailor()
    if not biblioteca.disponivel:
        raise ErroDeCompilacao(f"A DLL foi gerada, mas não abriu: {biblioteca.motivo_indisponivel}")
    img = np.full((300, 400), 255, np.uint8)
    img[100:200, 100:300] = 0      # uma peça grande: fica
    img[20:22, 20:22] = 0          # um pontinho solto: sai
    resultado = ps.limpar_pontinhos(img, 300, "normal", biblioteca=biblioteca)
    if not resultado.disponivel:
        raise ErroDeCompilacao(f"A DLL abriu, mas falhou: {resultado.motivo} ({resultado.detalhe_tecnico})")
    if resultado.imagem[20, 20] != 255 or resultado.imagem[150, 150] != 0:
        raise ErroDeCompilacao("A DLL abriu, mas o resultado da imagem de prova está errado.")
    return biblioteca.origem or "?"


def main(argumentos: list[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(
        description="Compila a DLL comum das ferramentas do ScanTailor (st_ferramentas).")
    analisador.add_argument("--baixar", action="store_true",
                            help="baixa o Qt e o Boost que faltarem (fora do git)")
    analisador.add_argument("--ferramentas", type=Path, default=pasta_de_ferramentas_padrao(),
                            help="pasta do Qt, do Boost e do rascunho da compilação")
    opcoes = analisador.parse_args(argumentos)

    inicio = time.perf_counter()
    try:
        if os.name != "nt":
            raise ErroDeCompilacao("Este script só compila no Windows.")
        versao_pyside = base.versao_do_qt_do_pyside()
        if versao_pyside != base.VERSAO_QT:
            raise ErroDeCompilacao(
                f"O PySide6 do programa usa o Qt {versao_pyside}, e o compilar_detector_gravura.py "
                f"compila para o Qt {base.VERSAO_QT}. Mude VERSAO_QT, _BASE_QT e ARQUIVO_QT lá.")
        dizer("1/5 ferramentas")
        cmake = base.achar_cmake()
        base.conferir_visual_studio()
        dizer(f"  CMake: {cmake}")
        dizer("2/5 Qt e Boost")
        qt = base.garantir_qt(opcoes.ferramentas, cmake, opcoes.baixar)
        boost = base.garantir_boost(opcoes.ferramentas, cmake, opcoes.baixar)
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
