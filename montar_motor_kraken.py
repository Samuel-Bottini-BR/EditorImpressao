"""Monta o "motor do Kraken": um Python 3.12 à parte, só para achar as linhas de texto (item 1.3).

    .venv\\Scripts\\python.exe montar_motor_kraken.py                    # monta no destino padrão
    .venv\\Scripts\\python.exe montar_motor_kraken.py --destino X:\\pasta  # monta em outro lugar (empacotador)
    .venv\\Scripts\\python.exe montar_motor_kraken.py --so-servidor      # só recopia o servidor_kraken.py
    .venv\\Scripts\\python.exe montar_motor_kraken.py --gerar-travado    # refaz as somas do arquivo travado

POR QUE EXISTE
    Decisão do Samuel (29/09/2026, Registro de mudanças): o Kraken roda direto
    no Windows, sem WSL, como MOTOR À PARTE - Python 3.12 embutível oficial +
    Kraken original + PyTorch para processador, chamado como outro processo.
    O programa continua no Python 3.14; este Python 3.12 é só do motor e nunca
    é usado pelo programa em si. Pesquisa: docs/pesquisa/fase1-1.3-kraken-windows.md.

O QUE FAZ
    1. Baixa (ou acha na pasta de downloads) o python-3.12.10-embed-amd64.zip
       oficial e confere a soma SHA-256 (a mesma que a python.org publica no
       arquivo .spdx.json ao lado do zip).
    2. Descompacta numa pasta nova "<destino>.montando" e escreve o
       python312._pth (liga a pasta Lib\\site-packages).
    3. Baixa o pip (roda direto do arquivo .whl, conferido pela soma) e instala
       as bibliotecas de motor_kraken/requisitos-travados.txt: versões EXATAS,
       cada uma conferida pela soma (--require-hashes), só pacotes prontos
       (--only-binary, nada é compilado), sem puxar dependência que não esteja
       na lista (--no-deps). O pip NÃO fica no motor.
    4. Pré-compila as bibliotecas (.pyc que valem mesmo sem conferir a data):
       na pasta do programa instalado o motor não tem permissão de escrita, e
       sem isso ele recompilaria tudo a cada arranque.
    5. Lê as importações de todas as DLLs do motor e copia, da pasta de
       redistribuíveis do Visual Studio 2022 (VC\\Redist\\MSVC\\<versão>\\x64\\
       Microsoft.VC143.CRT), as DLLs da Microsoft que faltarem (a pesquisa
       achou MSVCP140.dll e VCRUNTIME140_THREADS.dll; o PyTorch precisa delas
       e o Python embutível não as traz). A licença do Visual Studio permite
       levar esses arquivos, sem modificar, junto do programa (ver LEIA-ME
       gravado no motor).
    6. Copia motor_kraken/servidor_kraken.py e grava LEIA-ME-MOTOR.txt com a
       origem de tudo (versões, somas, de onde vieram as DLLs).
    7. Troca o nome "<destino>.montando" para "<destino>" e testa o motor pelo
       próprio core/ocr_kraken.py: abre, segmenta uma página sintética, confere
       que as DLLs da Microsoft carregadas são as do motor, e fecha.

    Destino padrão (FORA do git):
    D:\\programas\\EditorImpressao-arquivos\\ferramentas\\motor-kraken\\

REGRAS DE SEGURANÇA (CLAUDE.md, seção 10, item 9)
    O script NUNCA apaga pasta. Se o destino (ou a "<destino>.montando" de uma
    tentativa anterior) já existir, ele para e diz o que fazer: quem apaga é a
    pessoa, à mão. Não mexe no .venv do programa, nem no Python instalado da
    máquina, nem no Windows. Nada pede administrador.

O QUE O KAIQUE PRECISA
    Nada. O motor montado vai pronto dentro do instalador (etapa seguinte do
    item 1.3). Este script só roda no PC de quem empacota.

O QUE É ARRISCADO MUDAR
    - motor_kraken/requisitos-travados.txt: são as 73 versões que deram as
      MESMAS linhas do Kraken do WSL nas 22 páginas do 1.3. Trocar uma versão
      exige conferir de novo (tests/test_ocr_kraken.py, com o motor montado).
    - PYTHON_VERSAO / PYTHON_SHA256 e PIP_*: são a garantia de que o arquivo
      baixado é o oficial. Mudar a versão = mudar as três juntas.
    - A linha "import site" do ._pth: sem ela a pasta Lib\\site-packages não
      entra e o motor não acha o Kraken.
    - O -I -X utf8 na hora de rodar o motor (está em core/ocr_kraken.py): o -I
      isola o motor das bibliotecas do usuário; o -X utf8 substitui o
      PYTHONUTF8, que o modo isolado ignora.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PASTA_FONTES = RAIZ / "motor_kraken"
ARQUIVO_TRAVADO = PASTA_FONTES / "requisitos-travados.txt"
SERVIDOR = PASTA_FONTES / "servidor_kraken.py"

PASTA_FERRAMENTAS = RAIZ.parent / "EditorImpressao-arquivos" / "ferramentas"
DESTINO_PADRAO = PASTA_FERRAMENTAS / "motor-kraken"
DOWNLOADS_PADRAO = PASTA_FERRAMENTAS / "downloads"

# Python 3.12 embutível oficial. A soma é a que a python.org publica em
# python-3.12.10-embed-amd64.zip.spdx.json (pacote "cpython").
PYTHON_VERSAO = "3.12.10"
PYTHON_ARQUIVO = f"python-{PYTHON_VERSAO}-embed-amd64.zip"
PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSAO}/{PYTHON_ARQUIVO}"
PYTHON_SHA256 = "4acbed6dd1c744b0376e3b1cf57ce906f9dc9e95e68824584c8099a63025a3c3"

# O pip só é usado para montar; roda direto do .whl e não fica no motor.
PIP_ARQUIVO = "pip-26.2.1-py3-none-any.whl"
PIP_URL = ("https://files.pythonhosted.org/packages/f3/6e/"
           "1736e5b4ae2b778ef2f81c47d797de9f891d4d8acb047a24ca37a60294dd/" + PIP_ARQUIVO)
PIP_SHA256 = "71138adf1f4ca900cdb7d289c21b7494329f2332b6d85f0e1c42108c0384ed3e"

# Onde o Visual Studio 2022 guarda os redistribuíveis do C++ (a licença do
# Visual Studio lista a pasta VC\Redist como "Distributable Code"; a subpasta
# debug_nonredist é a única proibida e não é usada aqui).
PASTAS_VISUAL_STUDIO = [
    Path(r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"),
    Path(r"C:\Program Files\Microsoft Visual Studio\2022\Community"),
    Path(r"C:\Program Files\Microsoft Visual Studio\2022\Professional"),
    Path(r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise"),
    Path(r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Community"),
]

# DLLs da Microsoft que o Windows NÃO traz de fábrica: se alguma DLL do motor
# importar uma destas, ela tem de estar ao lado do python.exe do motor.
_PADRAO_DLL_DA_MICROSOFT = re.compile(
    r"^(msvcp140(_\w+)?|vcruntime140(_\w+)?|concrt140|vcomp140|vccorlib140)\.dll$", re.I)
# vcruntime140.dll e vcruntime140_1.dll vêm no zip do Python, mas numa versão
# mais velha; ficam trocadas pelas do mesmo Visual C++ das outras, para o
# conjunto ser de uma versão só (versão nova serve para programa feito com a velha).
_SEMPRE_DO_MESMO_CONJUNTO = ("vcruntime140.dll", "vcruntime140_1.dll")

# Tem de bater com VERSAO_PROTOCOLO em motor_kraken/servidor_kraken.py e em
# core/ocr_kraken.py (conferido no teste do fim).
VERSAO_PROTOCOLO = 1


class ErroDeMontagem(Exception):
    """Algo impede a montagem; a mensagem diz o quê, em português."""


def dizer(texto: str) -> None:
    print(texto, flush=True)


# ---------------------------------------------------------------- downloads

def _soma(caminho: Path, algoritmo: str = "sha256") -> str:
    h = hashlib.new(algoritmo)
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _baixar_conferido(url: str, destino: Path, sha256: str) -> Path:
    """Baixa para 'destino' (se ainda não estiver lá) e confere a soma.

    Um arquivo que não bate com a soma é trocado de nome para '.errado' (não
    é apagado) e a montagem para.
    """
    if not destino.is_file():
        destino.parent.mkdir(parents=True, exist_ok=True)
        parcial = destino.with_suffix(destino.suffix + ".parcial")
        dizer(f"  baixando {url}")
        with urllib.request.urlopen(url, timeout=120) as resposta, parcial.open("wb") as saida:
            shutil.copyfileobj(resposta, saida, length=1 << 20)
        parcial.replace(destino)
    if _soma(destino) != sha256:
        errado = destino.with_suffix(destino.suffix + ".errado")
        destino.replace(errado)
        raise ErroDeMontagem(f"{destino.name} não bate com a soma oficial; ficou como {errado.name}.")
    return destino


# ---------------------------------------------------------------- arquivo travado

# Bibliotecas que o PyPI só tem como código-fonte para Windows (nenhum pacote
# pronto): o coremltools 9.0 só publica pacote pronto para Mac e Linux; no
# Windows ele é Python puro, montado a partir do .tar.gz (a pesquisa de 29/09
# instalou assim). Elas entram numa SEGUNDA rodada do pip, sem isolamento de
# montagem, usando o setuptools travado que a primeira rodada já instalou.
SO_CODIGO_FONTE = {"coremltools"}


def _blocos_do_travado(caminho: Path) -> list[tuple[str, str, str]]:
    """(biblioteca, versão, texto do bloco com as somas), na ordem do arquivo."""
    blocos: list[list[str]] = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        limpa = linha.split("#", 1)[0].strip()
        if not limpa:
            continue
        if limpa.startswith("--"):
            if not blocos:
                raise ErroDeMontagem(f"Soma solta no começo de {caminho.name}: {linha}")
            blocos[-1].append(linha)
        else:
            blocos.append([linha])
    saida = []
    for bloco in blocos:
        nome, _, versao = bloco[0].split()[0].partition("==")
        if not versao:
            raise ErroDeMontagem(f"Linha sem versão exata em {caminho.name}: {bloco[0]}")
        saida.append((nome, versao, "\n".join(bloco)))
    return saida


def ler_travado(caminho: Path = ARQUIVO_TRAVADO) -> list[tuple[str, str]]:
    """As (biblioteca, versão) do arquivo travado, na ordem do arquivo."""
    return [(nome, versao) for nome, versao, _ in _blocos_do_travado(caminho)]


def _roda_no_motor(nome_arquivo: str) -> bool:
    """O pacote pronto (.whl) serve para Python 3.12, Windows 64 bits?"""
    if not nome_arquivo.endswith(".whl"):
        return False
    partes = nome_arquivo[:-4].split("-")
    pythons, abis, plataformas = (set(p.split(".")) for p in partes[-3:])
    if not plataformas & {"any", "win_amd64"}:
        return False
    if pythons & {"py3", "cp312", "py312"} and abis & {"none", "cp312", "abi3"}:
        return True
    if "abi3" in abis:   # ex.: cp38-abi3 serve para 3.8 em diante
        return any(re.fullmatch(r"cp3(\d+)", p) and int(p[3:]) <= 12 for p in pythons)
    return False


def gerar_travado(caminho: Path = ARQUIVO_TRAVADO) -> None:
    """Reescreve o arquivo travado com as somas SHA-256 publicadas no PyPI.

    Só as somas dos pacotes prontos que servem ao motor (Python 3.12, Windows
    64 bits). As versões NÃO mudam: são as do arquivo.
    """
    pares = ler_travado(caminho)
    linhas = [
        "# Motor do Kraken (item 1.3): as bibliotecas do Python 3.12 à parte, com versão EXATA.",
        "# São as 73 versões da pesquisa de 29/09/2026 (docs/pesquisa/fase1-1.3-kraken-windows.md),",
        "# que deram as MESMAS linhas do Kraken do WSL nas 22 páginas do 1.3.",
        "# Somas: as do PyPI, só dos pacotes prontos para cp312/win_amd64 (e do .tar.gz para",
        "# as de SO_CODIGO_FONTE, em montar_motor_kraken.py: hoje só o coremltools).",
        "# Refazer as somas: montar_motor_kraken.py --gerar-travado. Mudar versão = conferir de novo.",
        "",
    ]
    for nome, versao in pares:
        url = f"https://pypi.org/pypi/{nome}/{versao}/json"
        with urllib.request.urlopen(url, timeout=60) as resposta:
            dados = json.load(resposta)
        if nome.lower() in SO_CODIGO_FONTE:
            somas = sorted({f["digests"]["sha256"] for f in dados["urls"] if f["packagetype"] == "sdist"})
        else:
            somas = sorted({f["digests"]["sha256"] for f in dados["urls"] if _roda_no_motor(f["filename"])})
        if not somas:
            raise ErroDeMontagem(f"{nome}=={versao}: o PyPI não tem pacote pronto para Python 3.12 / Windows 64 bits.")
        linhas.append(f"{nome}=={versao} \\")
        linhas += [f"    --hash=sha256:{s} \\" for s in somas[:-1]]
        linhas.append(f"    --hash=sha256:{somas[-1]}")
        dizer(f"  {nome}=={versao}: {len(somas)} pacote(s)")
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- DLLs (leitor de PE)

def importacoes_da_dll(caminho: Path) -> list[str]:
    """Os nomes das DLLs que um .dll/.pyd/.exe importa (tabela de importação do PE).

    Leitor mínimo, só do que é preciso aqui (PE32+ de 64 bits e PE32). Arquivo
    que não for PE válido devolve lista vazia.
    """
    try:
        dados = caminho.read_bytes()
        if dados[:2] != b"MZ":
            return []
        pe = struct.unpack_from("<I", dados, 0x3C)[0]
        if dados[pe:pe + 4] != b"PE\0\0":
            return []
        n_secoes = struct.unpack_from("<H", dados, pe + 6)[0]
        tam_opcional = struct.unpack_from("<H", dados, pe + 20)[0]
        opcional = pe + 24
        magia = struct.unpack_from("<H", dados, opcional)[0]
        diretorios = opcional + (112 if magia == 0x20B else 96)
        rva_importacao = struct.unpack_from("<I", dados, diretorios + 8)[0]
        if not rva_importacao:
            return []
        secoes = []
        inicio_secoes = opcional + tam_opcional
        for i in range(n_secoes):
            s = inicio_secoes + 40 * i
            tam_virtual, rva, tam_bruto, ptr_bruto = struct.unpack_from("<IIII", dados, s + 8)
            secoes.append((rva, max(tam_virtual, tam_bruto), ptr_bruto))

        def para_arquivo(r: int) -> int:
            for rva, tamanho, ptr in secoes:
                if rva <= r < rva + tamanho:
                    return r - rva + ptr
            raise ValueError("RVA fora das seções")

        nomes = []
        pos = para_arquivo(rva_importacao)
        while True:
            campos = struct.unpack_from("<IIIII", dados, pos)
            if not any(campos):
                break
            nome_pos = para_arquivo(campos[3])
            fim = dados.index(b"\0", nome_pos)
            nomes.append(dados[nome_pos:fim].decode("ascii", "replace"))
            pos += 20
        return nomes
    except (OSError, struct.error, ValueError):
        return []


def achar_pasta_crt() -> Path:
    """A pasta x64\\Microsoft.VC143.CRT mais nova do Visual Studio 2022 instalado."""
    candidatas = []
    for vs in PASTAS_VISUAL_STUDIO:
        for crt in (vs / "VC" / "Redist" / "MSVC").glob("*/x64/Microsoft.VC143.CRT"):
            if (crt / "msvcp140.dll").is_file():
                candidatas.append(crt)
    if not candidatas:
        raise ErroDeMontagem(
            "Não achei os redistribuíveis do Visual C++ (pasta VC\\Redist\\MSVC\\<versão>\\x64\\"
            "Microsoft.VC143.CRT do Visual Studio 2022). Instale o Visual Studio 2022 Build Tools "
            "com C++ (pede administrador: avise antes).")

    def versao(p: Path) -> tuple[int, ...]:
        return tuple(int(x) for x in re.findall(r"\d+", p.parent.parent.name))

    return max(candidatas, key=versao)


def copiar_dlls_da_microsoft(pasta_python: Path) -> list[dict]:
    """Copia para ao lado do python.exe as DLLs do Visual C++ que o motor importa e não tem."""
    crt = achar_pasta_crt()
    pedidas: dict[str, set[str]] = {}
    for arquivo in pasta_python.rglob("*"):
        if arquivo.suffix.lower() in (".dll", ".pyd", ".exe") and arquivo.is_file():
            for nome in importacoes_da_dll(arquivo):
                if _PADRAO_DLL_DA_MICROSOFT.match(nome):
                    pedidas.setdefault(nome.lower(), set()).add(arquivo.name)
    for nome in _SEMPRE_DO_MESMO_CONJUNTO:
        pedidas.setdefault(nome, set()).add("(conjunto de uma versão só)")
    copiadas = []
    for nome in sorted(pedidas):
        origem = crt / nome
        if not origem.is_file():
            # ex.: vcomp140.dll mora em Microsoft.VC143.OpenMP
            outras = list(crt.parent.glob(f"Microsoft.VC143.*/{nome}"))
            if not outras:
                raise ErroDeMontagem(f"O motor precisa de {nome}, e não achei em {crt.parent}.")
            origem = outras[0]
        destino = pasta_python / nome
        shutil.copy2(origem, destino)
        copiadas.append({"dll": nome, "origem": str(origem), "sha256": _soma(destino),
                         "pedida_por": sorted(pedidas[nome])[:5]})
    return copiadas


# ---------------------------------------------------------------- montagem

def _rodar(comando: list[str], **extra) -> None:
    dizer("  > " + " ".join(str(c) for c in comando[:6]) + (" ..." if len(comando) > 6 else ""))
    subprocess.run(comando, check=True, **extra)


def _tamanho_da_pasta(pasta: Path) -> int:
    return sum(f.stat().st_size for f in pasta.rglob("*") if f.is_file())


def montar(destino: Path, downloads: Path) -> Path:
    """Monta o motor em '<destino>.montando' e troca o nome para 'destino' no fim."""
    if os.name != "nt":
        raise ErroDeMontagem("Este script só monta o motor no Windows.")
    if destino.exists():
        raise ErroDeMontagem(
            f"Já existe {destino}. Este script não apaga pasta: troque o nome ou apague à mão "
            "(se for fora do projeto, pergunte ao Samuel antes), ou use --destino.")
    montando = destino.with_name(destino.name + ".montando")
    if montando.exists():
        raise ErroDeMontagem(
            f"Sobrou {montando} de uma tentativa anterior. Apague à mão (ou troque o nome) e rode de novo.")
    pasta_python = montando / "python"
    site_packages = pasta_python / "Lib" / "site-packages"

    dizer("1/7 Python 3.12 embutível")
    zip_python = _baixar_conferido(PYTHON_URL, downloads / PYTHON_ARQUIVO, PYTHON_SHA256)
    pasta_python.mkdir(parents=True)
    with zipfile.ZipFile(zip_python) as z:
        z.extractall(pasta_python)
    pth = pasta_python / "python312._pth"
    pth.write_text("python312.zip\n.\nLib\\site-packages\n\n# liga a pasta das bibliotecas\nimport site\n",
                   encoding="ascii")
    site_packages.mkdir(parents=True)
    python = pasta_python / "python.exe"

    dizer("2/7 pip (só para montar; não fica no motor)")
    pip = _baixar_conferido(PIP_URL, downloads / PIP_ARQUIVO, PIP_SHA256)

    blocos = _blocos_do_travado(ARQUIVO_TRAVADO)
    dizer(f"3/7 bibliotecas travadas ({len(blocos)}, conferidas pela soma; o PyTorch tem ~200 MB)")
    ambiente = {k: v for k, v in os.environ.items() if not k.upper().startswith(("PIP_", "PYTHON"))}
    base = [str(python), "-E", "-s", str(pip / "pip"), "install", "--isolated",
            "--disable-pip-version-check", "--no-input", "--no-warn-script-location",
            "--no-deps", "--require-hashes", "--target", str(site_packages)]
    with tempfile.TemporaryDirectory(prefix="motor-kraken-") as rascunho:
        prontos = Path(rascunho) / "prontos.txt"
        fonte = Path(rascunho) / "fonte.txt"
        prontos.write_text("\n".join(b for n, _, b in blocos if n.lower() not in SO_CODIGO_FONTE) + "\n",
                           encoding="utf-8")
        fonte.write_text("\n".join(b for n, _, b in blocos if n.lower() in SO_CODIGO_FONTE) + "\n",
                         encoding="utf-8")
        _rodar(base + ["--only-binary=:all:", "-r", str(prontos)], env=ambiente)
        if fonte.read_text(encoding="utf-8").strip():
            # --target junta tudo numa pasta temporária e move no fim: por isso
            # a segunda rodada precisa de --upgrade para não recusar as pastas
            # que já existem (ela só instala os pacotes de fonte.txt).
            _rodar(base + ["--no-build-isolation", "--no-binary=:all:", "--upgrade",
                           "-r", str(fonte)], env=ambiente)
    # Os executáveis de linha de comando (kraken.exe, ketos.exe...) apontam para
    # o Python de quem montou; não servem ao motor. Ficam, mas ninguém os usa.

    dizer("4/7 pré-compilando (.pyc que valem sem conferir a data)")
    # -f é obrigatório: o pip já deixou .pyc no modo "confere a data", e sem
    # -f o compileall os acha em dia e não troca nenhum (descoberto em 29/09).
    _rodar([str(python), "-I", "-X", "utf8", "-m", "compileall", "-q", "-f", "-j", "0",
            "--invalidation-mode", "unchecked-hash", str(site_packages)], env=ambiente)

    dizer("5/7 DLLs da Microsoft (Visual C++)")
    copiadas = copiar_dlls_da_microsoft(pasta_python)
    for c in copiadas:
        dizer(f"  {c['dll']:28s} de {Path(c['origem']).parent}")

    dizer("6/7 servidor e LEIA-ME")
    shutil.copy2(SERVIDOR, montando / SERVIDOR.name)
    modelo = site_packages / "kraken" / "blla.mlmodel"
    if not modelo.is_file():
        raise ErroDeMontagem(f"O Kraken instalou, mas o modelo blla não está em {modelo}.")
    gravar_leia_me(montando, copiadas, modelo)

    dizer("7/7 trocando o nome da pasta")
    montando.rename(destino)
    return destino


def gravar_leia_me(motor: Path, copiadas: list[dict], modelo: Path) -> None:
    """LEIA-ME-MOTOR.txt: de onde veio cada parte do motor (para o empacotador e para a licença)."""
    versao_crt = Path(copiadas[0]["origem"]).parent.parent.parent.name if copiadas else "?"
    linhas = [
        "MOTOR DO KRAKEN - Editor de Impressão (item 1.3 da Fase 1)",
        "",
        "Um Python à parte que só acha onde estão as linhas de texto de uma página",
        "(segmentador 'blla' do Kraken). Não transcreve. O programa o chama como outro",
        "processo (core/ocr_kraken.py), com: python\\python.exe -I -X utf8 servidor_kraken.py",
        "",
        f"Montado em:   {datetime.now():%d/%m/%Y %H:%M} por montar_motor_kraken.py",
        f"Python:       {PYTHON_ARQUIVO} (python.org, SHA-256 {PYTHON_SHA256}); licença PSF em python\\LICENSE.txt",
        f"Bibliotecas:  motor_kraken/requisitos-travados.txt ({len(ler_travado())} versões exatas, conferidas pela soma)",
        "              licenças de cada uma: python\\Lib\\site-packages\\*.dist-info\\",
        f"Modelo:       {modelo.relative_to(motor)} (vem no pacote do Kraken 7.1.1, Apache-2.0)",
        f"              SHA-256 {_soma(modelo)}",
        f"Protocolo:    versão {VERSAO_PROTOCOLO} (servidor_kraken.py <-> core/ocr_kraken.py)",
        "",
        f"DLLs da Microsoft (Visual C++ {versao_crt}), copiadas SEM modificar da pasta de",
        "redistribuíveis do Visual Studio 2022 (VC\\Redist\\MSVC\\<versão>\\x64\\Microsoft.VC143.CRT).",
        "A lista 'Distributable Code' do Visual Studio 2022 (https://aka.ms/vs/17/redist.txt)",
        "permite copiar e distribuir com o programa os arquivos da pasta VC\\Redist, sem",
        "modificar, sujeito à licença do Visual Studio (exceto a subpasta debug_nonredist).",
    ]
    for c in copiadas:
        linhas.append(f"  {c['dll']:26s} SHA-256 {c['sha256']}  (pedida por: {', '.join(c['pedida_por'])})")
    (motor / "LEIA-ME-MOTOR.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def testar_o_motor(destino: Path) -> None:
    """Abre o motor pelo módulo do programa, segmenta uma página sintética e fecha."""
    import numpy as np

    sys.path.insert(0, str(RAIZ))
    from core.ocr_kraken import MotorKraken

    pagina = np.full((1400, 1000, 3), 245, np.uint8)
    for i in range(8):   # oito "linhas de texto": tracinhos pretos em fileira
        y = 200 + 120 * i
        for x in range(120, 880, 28):
            pagina[y:y + 34, x:x + 18] = 20
    inicio = time.perf_counter()
    with MotorKraken(pasta=destino) as motor:
        resultado = motor.segmentar(pagina)
        diag = motor.diagnostico()
    if not resultado.disponivel:
        raise ErroDeMontagem(f"O motor foi montado, mas não funcionou: {resultado.motivo} "
                             f"({resultado.detalhe_tecnico})")
    dizer(f"  abriu em {motor.segundos_para_abrir:.1f} s; página sintética: "
          f"{len(resultado.linhas)} linha(s) em {resultado.segundos:.1f} s; "
          f"tudo em {time.perf_counter() - inicio:.1f} s")
    fora = [c for c in (diag or {}).get("dlls_da_microsoft", [])
            if not Path(c).resolve().is_relative_to(destino.resolve())]
    if fora:
        raise ErroDeMontagem("O motor carregou DLLs da Microsoft de fora dele (numa máquina limpa "
                             f"elas não existiriam): {fora}")
    dizer(f"  DLLs da Microsoft carregadas: todas de dentro do motor "
          f"({len((diag or {}).get('dlls_da_microsoft', []))})")


def main(argumentos: list[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(description="Monta o motor do Kraken (Python 3.12 à parte).")
    analisador.add_argument("--destino", type=Path, default=DESTINO_PADRAO,
                            help="pasta do motor (padrão: fora do git, em EditorImpressao-arquivos\\ferramentas)")
    analisador.add_argument("--downloads", type=Path, default=DOWNLOADS_PADRAO,
                            help="onde guardar o zip do Python e o pip baixados")
    analisador.add_argument("--so-servidor", action="store_true",
                            help="só recopia motor_kraken/servidor_kraken.py para um motor já montado")
    analisador.add_argument("--so-testar", action="store_true", help="só testa um motor já montado")
    analisador.add_argument("--gerar-travado", action="store_true",
                            help="refaz as somas SHA-256 do arquivo travado (pelo PyPI)")
    opcoes = analisador.parse_args(argumentos)
    destino = opcoes.destino.resolve()

    inicio = time.perf_counter()
    try:
        if opcoes.gerar_travado:
            gerar_travado()
            dizer(f"Pronto: {ARQUIVO_TRAVADO}")
            return 0
        if opcoes.so_servidor:
            if not (destino / "python" / "python.exe").is_file():
                raise ErroDeMontagem(f"Não há motor montado em {destino}.")
            shutil.copy2(SERVIDOR, destino / SERVIDOR.name)
            dizer(f"Servidor recopiado para {destino}")
        elif not opcoes.so_testar:
            montar(destino, opcoes.downloads.resolve())
        dizer("teste: abrindo o motor pelo core/ocr_kraken.py")
        testar_o_motor(destino)
    except ErroDeMontagem as erro:
        dizer(f"\nNÃO MONTOU: {erro}")
        return 1
    except subprocess.CalledProcessError as erro:
        dizer(f"\nNÃO MONTOU: o comando falhou ({erro}). Veja as mensagens acima.")
        return 1
    dizer(f"\nPronto em {time.perf_counter() - inicio:.0f} s: {destino} "
          f"({_tamanho_da_pasta(destino) / 1e6:.0f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
