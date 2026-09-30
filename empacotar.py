"""Gera o programa pronto para entregar (Etapa 8).

    python empacotar.py                 # tudo: pasta + arquivo único + instalador
    python empacotar.py --modo pasta        # só a versão portatil em pasta
    python empacotar.py --modo arquivo      # só o .exe único (pendrive)
    python empacotar.py --modo instalador   # pasta + EditorImpressao-Setup.exe
    python empacotar.py --modo entrega      # só o instalador, na Área de Trabalho

O QUE ESTE SCRIPT APAGA (conserto de 28/09/2026): so o que ele mesmo gera -
build\\ e, de dist\\, a pasta, o arquivo único e o instalador (ver
gerados_em_dist e apagar_o_que_gerou). Antes, o modo entrega apagava dist\\
inteira, e levaria junto o teste de velocidade do Kaique que mora ali
(TesteVelocidade\\, o .txt e o .zip da Fase 0).

Sai tudo em dist/:

    dist\\EditorImpressao\\                 versão em pasta - abre em ~8 s
    dist\\EditorImpressao.exe               arquivo único  - abre em ~12 s
    dist\\EditorImpressao-Setup.exe         instalador do Windows

A versão em pasta e a que o instalador empacota: o arquivo único se descompacta
inteiro a cada abertura, o que custa uns 4 segundos a mais. Os dois demoram
alguns segundos de qualquer jeito - e o custo de carregar Qt e OpenCV.
(Medido nesta maquina, em aberturas repetidas.)

OS MODELOS VAO JUNTO (conserto de 28/09/2026, Lista de bugs de 25/09). Os
arquivos das redes neurais ficam FORA do git (pasta modelos/, 120 MB) e ate
28/09 nunca entravam no programa empacotado: o instalador de 01/09 e o de
23/09 rodavam sem o detector de gravura e letra e sem a selecao por clique,
sem avisar nada (prova em docs/plano/bugs/2026-09-25-instalador-sem-modelos.txt).
Agora:

- modelos_do_programa() le do PROPRIO codigo (core/detectar_regioes.py e
  core/rede_selecao.py) os caminhos em que cada modelo e procurado, e cada um
  vai para o mesmo caminho relativo dentro do pacote (_internal\\modelos\\...
  na pasta; a raiz do _MEIxxxx no arquivo único). So vai o que o codigo usa:
  nada do mobile_sam.zip, do script de referencia nem do config.yaml.
- Faltando um modelo em modelos/, o script PARA antes de apagar ou gerar
  qualquer coisa, dizendo qual falta e onde.
- Depois de gerar, confere que cada modelo chegou inteiro na pasta
  (conferir_modelos_no_pacote) e que o Inno Setup o comprimiu DENTRO do
  instalador (modelos_faltando_no_registro_do_inno); se nao, apaga o
  instalador incompleto e para. O registro do Inno fica em
  build\\instalador-registro.txt.

OS DETECTORES DE TEXTO VAO JUNTO (item 1.3, 29/09/2026). Decisao do Samuel:
"todos os OCRs instalados", com o Tesseract desligado de fabrica. Na versao
em pasta (e, por ela, no instalador):

- docTR: o modelo modelos\\doctr\\rep_fast_base-1b89ebf9.onnx vai para
  _internal\\modelos\\doctr\\ (mais um em modelos_do_programa) e o OnnxTR
  entra pelo PyInstaller (OCULTOS);
- Kraken: o motor a parte (Python 3.12 + Kraken, ~1,2 GB, montado por
  montar_motor_kraken.py) vai INTEIRO para <pasta>\\motor-kraken\\, ao lado do
  .exe (e onde core/ocr_kraken.py o procura empacotado). O motor tem de ser
  do jeito novo, SEM as DLLs do Visual C++ (conferir_motor_kraken);
- Tesseract: os 27 arquivos do tesseract.exe da UB Mannheim (5.4.0), a
  LICENSE e os AUTHORS, e os seis idiomas da comparacao (lat, ita, por, fra,
  eng, script/Fraktur) vao para <pasta>\\tesseract\\ e
  <pasta>\\tesseract\\tessdata\\;
- Visual C++: o vc_redist.x64.exe OFICIAL da Microsoft (decisao do Samuel,
  29/09: "O instalador roda o instalador oficial da Microsoft, e pula se ja
  estiver instalado"). Baixado de https://aka.ms/vs/17/release/vc_redist.x64.exe
  para a pasta de downloads das ferramentas (fora do git) e conferido pela
  ASSINATURA DIGITAL (a Microsoft nao publica uma soma fixa para ele): o
  Windows tem de dizer "assinatura valida" e o assinante tem de ser a
  Microsoft Corporation (preparar_vc_redist). Vai so dentro do instalador
  (build\\vc_redist.x64.exe), que o roda em silencio quando o Visual C++
  2015-2022 x64 falta ou e mais velho (instalador.iss, secao [Code]).

A TRAVA vale para tudo isso, como para os modelos: faltando qualquer peca
(motor, Tesseract, idioma, licenca, vc_redist, modelo), ou o motor sendo do
jeito velho, o script PARA antes de gerar qualquer coisa, dizendo o que falta
e como resolver; depois de gerar, confere que cada peca chegou inteira na
pasta (conferir_pecas_no_pacote) e dentro do instalador
(pecas_faltando_no_registro_do_inno). O arquivo único (pendrive) NAO leva o
Kraken nem o Tesseract (sao programas a parte, de ~1,4 GB): so o docTR.

Para provar que o programa empacotado acha os tres detectores:
    dist\\EditorImpressao\\EditorImpressao.exe --conferir-ocr <imagem> <saida.json>
(ver core/ocr_diagnostico.py).

Arriscado mudar: o destino de cada modelo (tem de ser o caminho relativo que
o codigo procura, ver modelos_do_programa) e o --contents-directory _internal
(o instalador.iss e as conferencias contam com esse nome); os nomes das
pastas motor-kraken\\ e tesseract\\ (core/ocr_kraken.py e core/ocr_tesseract.py
procuram exatamente ali, ao lado do .exe).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
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

# A Area de Trabalho de quem roda o script: e onde o modo entrega deixa o
# instalador. Constante (e nao Path.home() espalhado) para os testes poderem
# trocar por uma pasta temporaria sem mexer na Area de Trabalho de verdade.
AREA_DE_TRABALHO = Path.home() / "Desktop"

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
    "matplotlib", "pandas", "IPython", "tkinter", "pytest",
]

# O DoxaPy e uma biblioteca nativa: o PyInstaller nao acha sozinho.
# Os detectores de texto (item 1.3) ainda nao estao ligados a tela: vao
# explicitos, e o OnnxTR e importado so dentro de uma funcao (ocr_doctr).
OCULTOS = ["doxapy", "skimage.filters", "PIL._tkinter_finder",
           "core.ocr_comum", "core.ocr_doctr", "core.ocr_tesseract", "core.ocr_kraken",
           "core.ocr_comparar", "core.ocr_diagnostico",
           "onnxtr", "onnxtr.models", "onnxtr.models.detection", "onnxtr.models.builder",
           "onnxtr.models.engine"]

# ---- os detectores de texto que vao ao lado do .exe (item 1.3) ----------
PASTA_DO_MOTOR = "motor-kraken"     # core/ocr_kraken.NOME_DA_PASTA
PASTA_DO_TESSERACT = "tesseract"    # core/ocr_tesseract.lugares_do_tesseract
# Onde procurar um motor do Kraken pronto, em ordem (o primeiro VALIDO vale;
# --motor-kraken passa outro). O de EditorImpressao-arquivos\ferramentas foi
# montado ate 29/09 com as DLLs do Visual C++ dentro, e e recusado.
LUGARES_DO_MOTOR = [
    RAIZ / "motor-kraken",
    RAIZ.parent / "EditorImpressao-arquivos" / "ferramentas" / "motor-kraken",
    RAIZ / "saida_teste" / "motor-kraken",
]
# Os 27 arquivos de que o tesseract.exe 5.4.0 (UB Mannheim) precisa: ele e as
# DLLs que ele carrega, lidas da tabela de importacao em 29/09/2026 e
# testadas numa copia so com elas e o PATH limpo. O resto da pasta do
# Tesseract (ferramentas de treino, Cairo/Pango, documentacao) nao vai.
ARQUIVOS_DO_TESSERACT = (
    "tesseract.exe", "libtesseract-5.dll", "libleptonica-6.dll", "libarchive-13.dll",
    "libb2-1.dll", "libbz2-1.dll", "libcrypto-3-x64.dll", "libdeflate.dll", "libexpat-1.dll",
    "libgcc_s_seh-1.dll", "libgif-7.dll", "libiconv-2.dll", "libjbig-0.dll", "libjpeg-8.dll",
    "libLerc.dll", "liblz4.dll", "liblzma-5.dll", "libopenjp2-7.dll", "libpng16-16.dll",
    "libsharpyuv-0.dll", "libstdc++-6.dll", "libtiff-6.dll", "libwebp-7.dll",
    "libwebpmux-3.dll", "libwinpthread-1.dll", "libzstd.dll", "zlib1.dll",
)
LICENCAS_DO_TESSERACT = ("LICENSE", "AUTHORS")   # da pasta doc\ da instalacao
# O instalador oficial do Visual C++ 2015-2022 x64 (link permanente da Microsoft).
VC_REDIST_URL = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
VC_REDIST_NOME = "vc_redist.x64.exe"
DOWNLOADS = RAIZ.parent / "EditorImpressao-arquivos" / "ferramentas" / "downloads"

# Onde o PyInstaller 6 poe tudo o que nao e o .exe, na versão em pasta. E o
# padrao dele, mas vai explicito no comando: o instalador.iss (a limpeza do
# desinstalador e a conferencia dos modelos) e conferir_modelos_no_pacote
# contam com este nome.
INTERNO = "_internal"

# Onde fica o registro de compilacao do Inno Setup (uma linha "Compressing:"
# por arquivo que entrou no instalador). Em build\, que e rascunho.
REGISTRO_DO_INNO = RAIZ / "build" / "instalador-registro.txt"


# ---------------------------------------------------------------------------
# os modelos (redes neurais), que ficam fora do git
# ---------------------------------------------------------------------------

def modelos_do_programa() -> list[tuple[Path, str]]:
    """Os arquivos de modelo que o programa usa: [(origem, destino no pacote)].

    A origem vem do PROPRIO codigo que procura o modelo - nao e uma copia do
    caminho aqui -, entao se alguem mudar onde o core procura, o empacotamento
    acompanha sozinho:

    - core/detectar_regioes.CAMINHO_MODELO: o detector de gravura e letra
      (modelos/doclayout.onnx, 75 MB);
    - core/rede_selecao.CODIFICADOR e DECODIFICADOR: a selecao por clique
      (modelos/mobile_sam/*.onnx, 45 MB);
    - core/ocr_doctr.CAMINHO_MODELO: o detector de texto docTR fast_base
      (modelos/doctr/rep_fast_base-1b89ebf9.onnx, 42 MB; item 1.3).

    O destino e o caminho da pasta do modelo relativo a raiz do codigo (a
    pasta acima de core/). Empacotado, a raiz do codigo e _internal\\ (na
    pasta) ou o _MEIxxxx (no arquivo único), e o codigo procura o modelo
    exatamente em <raiz do codigo>/modelos/...: por isso o destino e esse
    caminho relativo, e nao outro.

    Importa core/ so aqui dentro, e nao no alto do arquivo: o
    empacotar_teste_velocidade.py importa este modulo so pelas listas
    EXCLUIR e OCULTOS.
    """
    from core import detectar_regioes, ocr_doctr, rede_selecao

    raiz_do_codigo = Path(detectar_regioes.__file__).resolve().parent.parent
    usados = (detectar_regioes.CAMINHO_MODELO,
              rede_selecao.CODIFICADOR, rede_selecao.DECODIFICADOR,
              ocr_doctr.CAMINHO_MODELO)
    return [(origem, origem.relative_to(raiz_do_codigo).parent.as_posix())
            for origem in usados]


def modelos_faltando() -> list[Path]:
    """Os modelos que o programa usa e que nao estao em disco para empacotar."""
    return [origem for origem, _ in modelos_do_programa() if not origem.is_file()]


def _avisar_modelos_faltando() -> bool:
    """Imprime a mensagem de modelo faltando. Devolve True se esta tudo la.

    Chamada ANTES de apagar ou gerar qualquer coisa: sem o modelo, o programa
    empacotado so deixa de achar gravura e letra (ou de selecionar por
    clique), sem avisar ninguem - e o instalador parece pronto.
    """
    faltando = modelos_faltando()
    if not faltando:
        return True
    print("\n  PAREI: falta modelo, e sem ele o programa sairia incompleto.")
    for origem in faltando:
        print(f"    não achei {origem}")
    print("  Os modelos ficam fora do git (pasta modelos\\). Copie os arquivos")
    print("  para os lugares acima - os do mobile_sam estão dentro de")
    print("  modelos\\mobile_sam.zip - e rode de novo.")
    return False


def conferir_modelos_no_pacote(pasta: Path) -> list[str]:
    """Confere a versão em pasta ja gerada: cada modelo tem de estar em
    <pasta>\\_internal\\<destino>\\, com o mesmo tamanho do original.

    Devolve a lista de problemas, em portugues (vazia = tudo certo).
    """
    problemas: list[str] = []
    for origem, destino in modelos_do_programa():
        empacotado = Path(pasta) / INTERNO / destino / origem.name
        if not empacotado.is_file():
            problemas.append(f"{origem.name} não chegou em {empacotado}")
        elif not origem.is_file():
            problemas.append(f"{origem.name}: o original sumiu de {origem}")
        elif empacotado.stat().st_size != origem.stat().st_size:
            problemas.append(f"{origem.name} chegou pela metade em {empacotado}")
    return problemas


def _caminho_no_instalador(origem: Path, destino: str) -> str:
    """'_internal\\modelos\\mobile_sam\\x.onnx': como o modelo aparece dentro da
    pasta que o instalador.iss copia (dist\\EditorImpressao\\*)."""
    return "\\".join([INTERNO, *destino.split("/"), origem.name])


def _comprimidos(registro: str) -> list[str]:
    """Os caminhos das linhas "Compressing:" do registro do Inno, em minusculas.

    Tira o "   (14.44.35211.0)" que o Inno poe no fim da linha de um .exe
    com numero de versao que NAO tem a opcao ignoreversion (achado em 29/09:
    o vc_redist.x64.exe entrou no instalador, mas a conferencia nao o
    reconhecia, e o instalador bom foi apagado pela trava).
    """
    import re

    saida = []
    for linha in registro.splitlines():
        if "Compressing:" not in linha:
            continue
        caminho = re.sub(r"\s+\([\d.]+\)\s*$", "", linha.strip())
        saida.append(caminho.lower().replace("/", "\\"))
    return saida


def modelos_faltando_no_registro_do_inno(registro: str) -> list[str]:
    """Os modelos que o Inno Setup NAO comprimiu para dentro do instalador.

    O ISCC escreve uma linha "Compressing: <caminho completo>" para cada
    arquivo que entra no Setup.exe. Esta e a prova de que o modelo esta la
    dentro, e nao so na pasta dist\\. Devolve os caminhos relativos
    ('_internal\\modelos\\doclayout.onnx') que faltam.
    """
    comprimidos = _comprimidos(registro)
    faltando: list[str] = []
    for origem, destino in modelos_do_programa():
        relativo = _caminho_no_instalador(origem, destino)
        if not any(linha.endswith("\\" + relativo.lower()) for linha in comprimidos):
            faltando.append(relativo)
    return faltando


def _tamanho(caminho: Path) -> str:
    """Tamanho em MB, de um arquivo ou (somando tudo dentro) de uma pasta."""
    if caminho.is_file():
        mb = caminho.stat().st_size / 1024 / 1024
    else:
        mb = sum(f.stat().st_size for f in caminho.rglob("*") if f.is_file()) / 1024 / 1024
    return f"{mb:.0f} MB"


# ---------------------------------------------------------------------------
# os detectores de texto que vao ao lado do .exe (item 1.3, 29/09/2026)
# ---------------------------------------------------------------------------

@dataclass
class PecasDosDetectores:
    """Onde estao, neste PC, as pecas que vao ao lado do .exe e no instalador.

    motor: a pasta do motor do Kraken (vai inteira para motor-kraken\\);
    tesseract: a pasta com o tesseract.exe e as 26 DLLs (so as 27 vao);
    licencas: a pasta com LICENSE e AUTHORS do Tesseract;
    tessdata: a pasta com os seis idiomas;
    vc_redist: o vc_redist.x64.exe oficial conferido; vc_versao: a versao dele.
    """

    motor: Path
    tesseract: Path
    licencas: Path
    tessdata: Path
    vc_redist: Path
    vc_versao: str


def conferir_motor_kraken(pasta: Path) -> list[str]:
    """O que impede esta pasta de ir como motor do Kraken (vazio = pode ir).

    Recusa o motor do jeito velho (com as DLLs do Visual C++ ao lado do
    python.exe, ou com os atalhos bin\\*.exe): desde 29/09 o Visual C++ vem do
    vc_redist oficial, e um motor com as DLLs dentro misturaria versoes.
    """
    import montar_motor_kraken as m
    from core import ocr_kraken

    pasta = Path(pasta)
    python = pasta / "python"
    problemas = []
    if not (python / "python.exe").is_file():
        return [f"não há motor montado em {pasta} (falta python\\python.exe)"]
    servidor = pasta / ocr_kraken.NOME_DO_SERVIDOR
    if not servidor.is_file():
        problemas.append(f"falta {servidor.name} em {pasta}")
    elif f"VERSAO_PROTOCOLO = {ocr_kraken.VERSAO_PROTOCOLO}\n" not in servidor.read_text(encoding="utf-8"):
        problemas.append(f"o {servidor.name} de {pasta} é de outra versão (rode montar_motor_kraken.py "
                         f"--so-servidor --destino {pasta})")
    if not (python / "Lib" / "site-packages" / "kraken" / "blla.mlmodel").is_file():
        problemas.append(f"falta o modelo do Kraken (kraken\\blla.mlmodel) em {pasta}")
    velhas = [n for n in m.DLLS_DO_VISUAL_C if (python / n).is_file()]
    if velhas:
        problemas.append(f"o motor de {pasta} é do jeito velho, com o Visual C++ dentro ({', '.join(velhas)}); "
                         "monte um novo com: montar_motor_kraken.py --destino saida_teste\\motor-kraken")
    if (python / "Lib" / "site-packages" / "bin").is_dir():
        problemas.append(f"o motor de {pasta} ainda tem os atalhos Lib\\site-packages\\bin (jeito velho)")
    return problemas


def achar_motor_kraken(escolhido: Path | None = None) -> tuple[Path | None, list[str]]:
    """O motor que vai no pacote: o escolhido, ou o primeiro VALIDO de LUGARES_DO_MOTOR.

    Devolve (pasta, []) ou (None, [o que ha de errado em cada lugar]).
    """
    lugares = [Path(escolhido)] if escolhido else LUGARES_DO_MOTOR
    problemas = []
    for lugar in lugares:
        if not lugar.exists():
            problemas.append(f"não existe {lugar}")
            continue
        erros = conferir_motor_kraken(lugar)
        if not erros:
            return lugar.resolve(), []
        problemas.extend(erros)
    return None, problemas


def achar_pasta_do_tesseract() -> Path | None:
    """A pasta do tesseract.exe NESTE PC (a que o programa, rodando pelo codigo, usaria)."""
    from core import ocr_tesseract

    exe = ocr_tesseract.achar_tesseract()
    return exe.parent if exe is not None else None


def conferir_tesseract(pasta: Path | None) -> list[str]:
    """O que falta para o Tesseract ir no pacote (vazio = tudo certo)."""
    from core import ocr_tesseract

    if pasta is None:
        return ["não achei o Tesseract neste PC (instale com: winget install UB-Mannheim.TesseractOCR)"]
    problemas = [f"falta {nome} em {pasta}" for nome in ARQUIVOS_DO_TESSERACT if not (pasta / nome).is_file()]
    problemas += [f"falta a licença {nome} em {pasta / 'doc'}" for nome in LICENCAS_DO_TESSERACT
                  if not (pasta / "doc" / nome).is_file()]
    if not problemas:
        versao = ocr_tesseract.MotorTesseract(pasta / "tesseract.exe").versao() or "?"
        if not versao.startswith(ocr_tesseract.VERSAO_DA_COMPARACAO):
            problemas.append(f"o Tesseract de {pasta} é o {versao}; a comparação do 1.3 usou o "
                             f"{ocr_tesseract.VERSAO_DA_COMPARACAO}")
    faltam = ocr_tesseract.modelos_que_faltam("+".join(ocr_tesseract.IDIOMAS_DO_INSTALADOR),
                                              ocr_tesseract.PASTA_DOS_MODELOS)
    problemas += [f"falta o idioma {i} ({i}.traineddata) em {ocr_tesseract.PASTA_DOS_MODELOS}" for i in faltam]
    return problemas


def assinatura_do_arquivo(arquivo: Path) -> dict:
    """A assinatura digital de um arquivo, lida pelo proprio Windows (Get-AuthenticodeSignature).

    Devolve {"status", "assinante", "produto", "versao"} ("status" = "Valid"
    quando a assinatura confere e o certificado e de uma autoridade em que o
    Windows confia). Nunca levanta: erro vira status "erro: ...".
    """
    import json
    import os

    comando = ("$s = Get-AuthenticodeSignature -LiteralPath $env:ARQUIVO_A_CONFERIR; "
               "$v = (Get-Item -LiteralPath $env:ARQUIVO_A_CONFERIR).VersionInfo; "
               "[pscustomobject]@{status=[string]$s.Status; assinante=[string]$s.SignerCertificate.Subject; "
               "produto=[string]$v.ProductName; versao=[string]$v.FileVersion} | ConvertTo-Json -Compress")
    try:
        saida = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", comando],
                               capture_output=True, text=True, timeout=120,
                               env={**os.environ, "ARQUIVO_A_CONFERIR": str(arquivo)})
        return json.loads(saida.stdout)
    except (OSError, subprocess.SubprocessError, ValueError) as erro:
        return {"status": f"erro: {erro}", "assinante": "", "produto": "", "versao": ""}


def vc_redist_confere(assinatura: dict) -> list[str]:
    """O que ha de errado com a assinatura lida (vazio = e o instalador oficial da Microsoft).

    Nao ha soma publicada fixa para o vc_redist.x64.exe (o link permanente da
    Microsoft muda de versao sozinho). A garantia e a assinatura digital:
    valida para o Windows, e de "CN=Microsoft Corporation, O=Microsoft
    Corporation"; e o produto tem de ser o Visual C++ 2015-20xx x64.
    """
    import re

    problemas = []
    if assinatura.get("status") != "Valid":
        problemas.append(f"a assinatura digital não confere (o Windows diz: {assinatura.get('status')})")
    assinante = assinatura.get("assinante") or ""
    if not (assinante.startswith("CN=Microsoft Corporation,") and "O=Microsoft Corporation" in assinante):
        problemas.append(f"o arquivo não foi assinado pela Microsoft (assinante: {assinante or 'nenhum'})")
    if not re.match(r"^Microsoft Visual C\+\+ 2015-20\d\d Redistributable \(x64\)", assinatura.get("produto") or ""):
        problemas.append(f"não é o Visual C++ 2015-2022 x64 (produto: {assinatura.get('produto')})")
    if not (assinatura.get("versao") or "").startswith("14."):
        problemas.append(f"versão inesperada: {assinatura.get('versao')}")
    return problemas


def preparar_vc_redist(baixar: bool = True) -> tuple[Path | None, str, list[str]]:
    """Acha (ou baixa) o vc_redist.x64.exe oficial em DOWNLOADS e confere a assinatura.

    Devolve (arquivo, versao, problemas). Nunca apaga nada: um arquivo que
    nao confere fica onde esta e o empacotamento para, dizendo o que fazer.
    O download vai para um nome provisorio e so ganha o nome certo depois de
    conferido.
    """
    import urllib.request

    arquivo = DOWNLOADS / VC_REDIST_NOME
    if not arquivo.is_file():
        if not baixar:
            return None, "", [f"falta {arquivo}"]
        DOWNLOADS.mkdir(parents=True, exist_ok=True)
        provisorio = arquivo.with_name(arquivo.name + ".baixando")
        if provisorio.exists():
            return None, "", [f"sobrou {provisorio} de um download anterior: apague à mão e rode de novo"]
        print(f"  baixando o Visual C++ oficial de {VC_REDIST_URL}")
        try:
            with urllib.request.urlopen(VC_REDIST_URL, timeout=120) as resposta, open(provisorio, "wb") as saida:
                shutil.copyfileobj(resposta, saida)
        except OSError as erro:
            return None, "", [f"não consegui baixar o Visual C++ ({erro}); baixe à mão de {VC_REDIST_URL} "
                              f"para {arquivo}"]
        problemas = vc_redist_confere(assinatura_do_arquivo(provisorio))
        if problemas:
            return None, "", [f"o arquivo baixado ({provisorio}) não é o oficial: " + "; ".join(problemas)]
        provisorio.rename(arquivo)
    assinatura = assinatura_do_arquivo(arquivo)
    problemas = vc_redist_confere(assinatura)
    if problemas:
        return None, "", [f"{arquivo} não é o oficial da Microsoft: " + "; ".join(problemas)
                          + " (apague à mão e rode de novo para baixar outro)"]
    return arquivo, assinatura.get("versao", ""), []


def juntar_pecas(motor_escolhido: Path | None = None,
                 baixar: bool = True) -> tuple[PecasDosDetectores | None, list[str]]:
    """Confere TODAS as pecas dos detectores de texto. (pecas, []) ou (None, problemas)."""
    from core import ocr_tesseract

    problemas = []
    motor, erros = achar_motor_kraken(motor_escolhido)
    if motor is None:
        problemas.append("motor do Kraken: nenhum motor pronto do jeito novo:")
        problemas += [f"  {e}" for e in erros]
    tesseract = achar_pasta_do_tesseract()
    problemas += [f"Tesseract: {e}" for e in conferir_tesseract(tesseract)]
    vc_redist, versao, erros = preparar_vc_redist(baixar)
    problemas += [f"Visual C++: {e}" for e in erros]
    if problemas:
        return None, problemas
    return PecasDosDetectores(motor, tesseract, tesseract / "doc", ocr_tesseract.PASTA_DOS_MODELOS,
                              vc_redist, versao), []


def _avisar_pecas_faltando(motor_escolhido: Path | None = None) -> PecasDosDetectores | None:
    """juntar_pecas, imprimindo o que falta. Chamada ANTES de apagar ou gerar qualquer coisa."""
    pecas, problemas = juntar_pecas(motor_escolhido)
    if pecas is not None:
        print(f"  motor do Kraken: {pecas.motor}")
        print(f"  Tesseract: {pecas.tesseract}  (idiomas de {pecas.tessdata})")
        print(f"  Visual C++: {pecas.vc_redist}  (versão {pecas.vc_versao}, assinatura da Microsoft conferida)")
        return pecas
    print("\n  PAREI: falta peça dos detectores de texto, e sem ela o programa sairia incompleto.")
    for problema in problemas:
        print(f"    {problema}")
    return None


def _destinos_das_pecas(pecas: PecasDosDetectores) -> list[tuple[Path, str]]:
    """[(origem, caminho relativo dentro da pasta do programa)] de cada arquivo solto.

    O motor do Kraken nao entra aqui (vai a pasta inteira; ver copiar_pecas).
    """
    from core import ocr_tesseract

    saida = [(pecas.tesseract / nome, f"{PASTA_DO_TESSERACT}/{nome}") for nome in ARQUIVOS_DO_TESSERACT]
    saida += [(pecas.licencas / nome, f"{PASTA_DO_TESSERACT}/{nome}") for nome in LICENCAS_DO_TESSERACT]
    saida += [(pecas.tessdata / f"{idioma}.traineddata", f"{PASTA_DO_TESSERACT}/tessdata/{idioma}.traineddata")
              for idioma in ocr_tesseract.IDIOMAS_DO_INSTALADOR]
    return saida


LEIA_ME_DO_TESSERACT = """TESSERACT - Editor de Impressão (item 1.3 da Fase 1)

O programa usa este Tesseract só para ACHAR onde está o texto (vem desligado
de fábrica). Não é usado para transcrever.

Origem: Tesseract {versao}, versão para Windows da UB Mannheim
(https://github.com/UB-Mannheim/tesseract), instalada pelo winget. Só foram
copiados o tesseract.exe e as 26 bibliotecas (.dll) que ele carrega, sem
modificar.
Licença do Tesseract: Apache-2.0 (arquivo LICENSE; autores em AUTHORS).
As bibliotecas (.dll) têm licenças próprias (Leptonica, libarchive, OpenSSL,
libstdc++/libgcc, libiconv, libjpeg, libpng, libtiff, libwebp, OpenJPEG,
zlib, zstd, lz4, xz, bzip2, expat, giflib, JBIG-KIT, LERC, libdeflate,
libb2, winpthreads); ver https://github.com/UB-Mannheim/tesseract.
Idiomas (pasta tessdata): lat, ita, por, fra, eng e script/Fraktur, do
conjunto "tessdata_best" (https://github.com/tesseract-ocr/tessdata_best),
licença Apache-2.0.
"""


def copiar_pecas(pasta: Path, pecas: PecasDosDetectores) -> None:
    """Poe o motor do Kraken e o Tesseract ao lado do .exe, na versao em pasta."""
    from core import ocr_tesseract

    destino_motor = pasta / PASTA_DO_MOTOR
    print(f"  copiando o motor do Kraken ({_tamanho(pecas.motor)}) para {destino_motor.name}\\")
    shutil.copytree(pecas.motor, destino_motor)
    print(f"  copiando o Tesseract e os {len(ocr_tesseract.IDIOMAS_DO_INSTALADOR)} idiomas "
          f"para {PASTA_DO_TESSERACT}\\")
    for origem, relativo in _destinos_das_pecas(pecas):
        alvo = pasta / relativo
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origem, alvo)
    versao = ocr_tesseract.MotorTesseract(pecas.tesseract / "tesseract.exe").versao() or "?"
    (pasta / PASTA_DO_TESSERACT / "LEIA-ME-TESSERACT.txt").write_text(
        LEIA_ME_DO_TESSERACT.format(versao=versao).replace("\n", "\r\n"), encoding="utf-8")


def conferir_pecas_no_pacote(pasta: Path, pecas: PecasDosDetectores) -> list[str]:
    """Confere que cada peca chegou inteira na versao em pasta (vazio = tudo certo)."""
    problemas = []
    for origem, relativo in _destinos_das_pecas(pecas):
        alvo = Path(pasta) / relativo
        if not alvo.is_file():
            problemas.append(f"{relativo} não chegou")
        elif alvo.stat().st_size != origem.stat().st_size:
            problemas.append(f"{relativo} chegou pela metade")
    motor = Path(pasta) / PASTA_DO_MOTOR
    if not motor.is_dir():
        problemas.append(f"{PASTA_DO_MOTOR}\\ não chegou")
    else:
        def resumo(p: Path) -> tuple[int, int]:
            arquivos = [f for f in p.rglob("*") if f.is_file()]
            return len(arquivos), sum(f.stat().st_size for f in arquivos)

        if resumo(motor) != resumo(pecas.motor):
            problemas.append(f"{PASTA_DO_MOTOR}\\ chegou diferente do original ({resumo(motor)} x "
                             f"{resumo(pecas.motor)} arquivos/bytes)")
        problemas += [f"{PASTA_DO_MOTOR}\\: {p}" for p in conferir_motor_kraken(motor)]
    return problemas


# Arquivos do motor que TEM de estar no registro do Inno (uma amostra do que
# importa: o Python, o servidor, o modelo e a biblioteca do PyTorch). Os ~34
# mil arquivos do motor entram pela mesma linha do [Files]; se estes quatro
# entraram, a pasta entrou.
AMOSTRA_DO_MOTOR = ("python\\python.exe", "servidor_kraken.py",
                    "python\\Lib\\site-packages\\kraken\\blla.mlmodel",
                    "python\\Lib\\site-packages\\torch\\lib\\torch_cpu.dll")


def pecas_esperadas_no_instalador(pecas: PecasDosDetectores) -> list[str]:
    """Os caminhos (relativos a dist\\EditorImpressao\\, ou build\\ para o
    vc_redist) que o registro do Inno tem de listar como "Compressing:"."""
    saida = [relativo.replace("/", "\\") for _, relativo in _destinos_das_pecas(pecas)]
    saida += [f"{PASTA_DO_MOTOR}\\{a}" for a in AMOSTRA_DO_MOTOR]
    saida.append(f"build\\{VC_REDIST_NOME}")
    return saida


def pecas_faltando_no_registro_do_inno(registro: str, pecas: PecasDosDetectores) -> list[str]:
    """As pecas que o Inno Setup NAO comprimiu para dentro do instalador."""
    comprimidos = _comprimidos(registro)
    return [relativo for relativo in pecas_esperadas_no_instalador(pecas)
            if not any(linha.endswith("\\" + relativo.lower()) for linha in comprimidos)]


def comando_do_pyinstaller(onefile: bool) -> list[str]:
    """O comando completo do PyInstaller. onefile=False e a versão em pasta.

    Separado de _pyinstaller para os testes conferirem o comando sem rodar o
    PyInstaller (que leva minutos). Caminhos sempre absolutos: com
    --specpath, o PyInstaller le os relativos a partir da pasta do .spec.
    """
    separador = ";" if sys.platform == "win32" else ":"
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
    if not onefile:
        # So existe na versão em pasta (ver INTERNO).
        comando += ["--contents-directory", INTERNO]
    for modulo in EXCLUIR:
        comando += ["--exclude-module", modulo]
    for modulo in OCULTOS:
        comando += ["--hidden-import", modulo]

    recursos = RAIZ / "recursos"
    if recursos.exists() and any(recursos.iterdir()):
        comando += ["--add-data", f"{recursos}{separador}recursos"]

    # Um --add-data por ARQUIVO de modelo, e nao a pasta modelos/ inteira: ela
    # tem tambem o mobile_sam.zip (36 MB, repetindo o que ja vai), um script
    # de referencia e o __pycache__ dele. Ver modelos_do_programa.
    for origem, destino in modelos_do_programa():
        comando += ["--add-data", f"{origem}{separador}{destino}"]

    comando.append(str(RAIZ / "main.py"))
    return comando


def _pyinstaller(onefile: bool) -> bool:
    """Roda o PyInstaller. onefile=False gera a versão em pasta."""
    return subprocess.run(comando_do_pyinstaller(onefile), cwd=RAIZ).returncode == 0


def achar_inno() -> Path | None:
    """Localiza o compilador do Inno Setup (ISCC.exe) nos lugares usuais, ou no PATH."""
    for caminho in CAMINHOS_DO_INNO:
        if caminho.exists():
            return caminho
    achado = shutil.which("ISCC")
    return Path(achado) if achado else None


# O motor do Kraken escolhido na linha de comando (--motor-kraken); None =
# procurar em LUGARES_DO_MOTOR. E as pecas conferidas pela ultima
# construir_pasta, que construir_instalador usa (vc_redist, registro do Inno).
MOTOR_ESCOLHIDO: Path | None = None
_PECAS: PecasDosDetectores | None = None


def construir_pasta() -> Path | None:
    """Versao portatil em pasta. E tambem o que o instalador empacota.

    Para (devolve None) se faltar modelo ou peca dos detectores de texto
    ANTES de apagar a pasta anterior, e de novo se algum modelo ou peca nao
    chegar inteiro (ver conferir_modelos_no_pacote e conferir_pecas_no_pacote).
    """
    global _PECAS
    print("\n=== Versao em pasta (portatil, abre na hora) ===")
    if not _avisar_modelos_faltando():
        return None
    pecas = _avisar_pecas_faltando(MOTOR_ESCOLHIDO)
    if pecas is None:
        return None
    destino = RAIZ / "dist" / NOME
    shutil.rmtree(destino, ignore_errors=True)

    if not _pyinstaller(onefile=False):
        print("  falhou")
        return None
    if not (destino / f"{NOME}.exe").exists():
        print("  o PyInstaller terminou mas o programa não apareceu")
        return None
    problemas = conferir_modelos_no_pacote(destino)
    if problemas:
        print("  PAREI: o programa saiu sem algum modelo:")
        for problema in problemas:
            print(f"    {problema}")
        return None
    print(f"  modelos dentro da pasta: {len(modelos_do_programa())}, conferidos")
    copiar_pecas(destino, pecas)
    problemas = conferir_pecas_no_pacote(destino, pecas)
    if problemas:
        print("  PAREI: o programa saiu sem alguma peça dos detectores de texto:")
        for problema in problemas:
            print(f"    {problema}")
        return None
    print("  motor do Kraken e Tesseract dentro da pasta, conferidos")
    _PECAS = pecas

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
    """Um .exe só, para levar no pendrive.

    Leva os modelos tambem (mesmos --add-data da pasta): sem eles o arquivo
    único rodaria sem o detector, calado. O preco e descompactar 120 MB a
    mais a cada abertura. Aqui nao ha conferencia depois de gerar: os
    arquivos ficam dentro do .exe, e o comando e o mesmo da pasta, que e
    conferida.
    """
    print("\n=== Arquivo único (pendrive) ===")
    if not _avisar_modelos_faltando():
        return None
    destino = RAIZ / "dist" / f"{NOME}.exe"
    destino.unlink(missing_ok=True)

    if not _pyinstaller(onefile=True) or not destino.exists():
        print("  falhou")
        return None

    print(f"  pronto: {destino}  ({_tamanho(destino)})")
    print("  atenção: abre uns 4 segundos mais devagar que a versão em pasta")
    print("  atenção: o arquivo único NÃO leva o Kraken nem o Tesseract (são programas")
    print("  à parte, de ~1,4 GB): nele só o docTR acha texto. Para os três, use o instalador.")
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

    # O vc_redist oficial vai so no instalador (nao em {app}): o .iss o pega
    # de build\ (rascunho) e o roda quando o Visual C++ falta.
    pecas = _PECAS
    if pecas is None:
        print("  PAREI: a versão em pasta não conferiu as peças dos detectores de texto")
        return None
    (RAIZ / "build").mkdir(exist_ok=True)
    shutil.copy2(pecas.vc_redist, RAIZ / "build" / VC_REDIST_NOME)
    print(f"  Visual C++ oficial {pecas.vc_versao} no instalador (roda só se faltar)")
    print("  comprimindo (o motor do Kraken tem ~1,1 GB: leva vários minutos)")

    resultado = subprocess.run(
        [str(inno), str(script)], cwd=RAIZ, capture_output=True, text=True
    )
    # O registro inteiro fica guardado: e ele que lista, arquivo por arquivo,
    # o que entrou no instalador (a prova de que os modelos estao la dentro).
    REGISTRO_DO_INNO.parent.mkdir(parents=True, exist_ok=True)
    REGISTRO_DO_INNO.write_text(resultado.stdout + resultado.stderr, encoding="utf-8")
    if resultado.returncode != 0:
        print("  o Inno Setup recusou o script:")
        for linha in (resultado.stdout + resultado.stderr).splitlines()[-12:]:
            print(f"    {linha}")
        return None

    destino = RAIZ / "dist" / f"{NOME}-Setup.exe"
    if not destino.exists():
        print("  o Inno Setup terminou mas o instalador não apareceu")
        return None

    # Instalador sem modelo nao pode sobrar em dist\: parece pronto e leva ao
    # Kaique um programa sem o detector (o bug de 25/09).
    faltando = modelos_faltando_no_registro_do_inno(resultado.stdout)
    if faltando:
        destino.unlink(missing_ok=True)
        print("  PAREI: o Inno Setup não pôs estes modelos no instalador")
        print("  (o instalador incompleto foi apagado):")
        for relativo in faltando:
            print(f"    {relativo}")
        print(f"  registro completo em {REGISTRO_DO_INNO}")
        return None
    faltando = pecas_faltando_no_registro_do_inno(resultado.stdout, pecas)
    if faltando:
        destino.unlink(missing_ok=True)
        print("  PAREI: o Inno Setup não pôs estas peças dos detectores de texto no instalador")
        print("  (o instalador incompleto foi apagado):")
        for relativo in faltando:
            print(f"    {relativo}")
        print(f"  registro completo em {REGISTRO_DO_INNO}")
        return None
    print("  modelos dentro do instalador (registro do Inno Setup):")
    for origem, destino_no_pacote in modelos_do_programa():
        print(f"    {_caminho_no_instalador(origem, destino_no_pacote)}")
    print(f"  peças dos detectores de texto dentro do instalador: {len(pecas_esperadas_no_instalador(pecas))} "
          "conferidas (motor do Kraken, Tesseract, 6 idiomas, licenças, Visual C++)")

    print(f"  pronto: {destino}  ({_tamanho(destino)})")
    return destino


def gerados_em_dist(raiz: Path | None = None) -> list[Path]:
    """O que ESTE script gera em dist\\: a versão em pasta, o arquivo único e
    o instalador. E so isso que ele apaga (ver apagar_o_que_gerou).

    O resto de dist\\ e de outros scripts e nao e dele: hoje, o teste de
    velocidade do notebook do Kaique (empacotar_teste_velocidade.py), com a
    pasta TesteVelocidade\\, o "COMO RODAR NO NOTEBOOK DO KAIQUE.txt" e o
    TesteVelocidade-notebook-do-Kaique.zip - a versão da Fase 0, que nao pode
    ser apagada nem refeita (Registro de mudanças do plano, 28/09/2026).
    Se este script passar a gerar outra coisa em dist\\, ela entra AQUI.
    """
    dist = Path(raiz or RAIZ) / "dist"
    return [dist / NOME, dist / f"{NOME}.exe", dist / f"{NOME}-Setup.exe"]


def apagar_o_que_gerou(raiz: Path | None = None) -> list[Path]:
    """Apaga o que este script gera: de dist\\, SO gerados_em_dist(); e a
    pasta build\\ inteira. Devolve o que nao conseguiu apagar (vazio = tudo).

    Ate 28/09/2026 o modo entrega apagava a pasta dist\\ INTEIRA, no comeco e
    no fim - e levaria junto o teste de velocidade do Kaique (ver
    gerados_em_dist). O .zip da Fase 0 so escaparia por estar marcado como
    somente leitura. Arriscado mudar: voltar a apagar dist\\ inteira, ou
    acrescentar a gerados_em_dist algo que outro script gera.

    A pasta build\\ continua indo inteira: e rascunho de compilacao, nada ali
    e resultado (o empacotar_teste_velocidade.py refaz o rascunho dele,
    build\\teste_velocidade\\, sozinho, a cada vez). A pasta dist\\ so vai
    embora se ficar vazia depois da limpeza.

    raiz = a pasta do projeto (RAIZ); os testes passam uma pasta temporaria.
    """
    raiz = Path(raiz or RAIZ)
    shutil.rmtree(raiz / "build", ignore_errors=True)
    for gerado in gerados_em_dist(raiz):
        try:
            if gerado.is_dir():
                shutil.rmtree(gerado)
            else:
                gerado.unlink(missing_ok=True)
        except OSError:
            pass  # arquivo aberto em outro programa: vai na lista devolvida
    try:
        (raiz / "dist").rmdir()   # so apaga se estiver vazia
    except OSError:
        pass
    return [gerado for gerado in gerados_em_dist(raiz) if gerado.exists()]


def _limpar_e_avisar() -> None:
    """apagar_o_que_gerou, dizendo o que ficou para tras (nao para: o que
    ficou e sobra, e sera refeito na proxima vez)."""
    for sobra in apagar_o_que_gerou():
        print(f"  ATENCAO: não consegui apagar {sobra} (está aberto?)")


def entregar() -> Path | None:
    """Gera SO o instalador e deixa ele sozinho na Área de Trabalho.

    No fim, apaga o que o proprio script gerou (build\\ e, de dist\\, a
    pasta, o arquivo único e o instalador - ver apagar_o_que_gerou). O que
    sobra para o usuario final e um arquivo único. O que outros scripts
    guardam em dist\\ (o teste de velocidade do Kaique) fica intacto.
    """
    print("\n=== Entrega: só o instalador ===")

    if construir_instalador() is None:
        return None

    pasta = AREA_DE_TRABALHO / PASTA_DE_ENTREGA
    print(f"\n  preparando {pasta}")
    if pasta.exists():
        shutil.rmtree(pasta, ignore_errors=True)
    pasta.mkdir(parents=True, exist_ok=True)

    # Se sobrou a pasta de uma versão anterior, com outro nome, ela vai embora:
    # duas pastas parecidas na Area de Trabalho, uma com o instalador velho, e
    # o usuário nao sabe qual abrir.
    for antigo in OUTROS_NOMES_DE_ENTREGA:
        velha = AREA_DE_TRABALHO / antigo
        if velha.is_dir() and velha != pasta:
            print(f"  removendo a pasta antiga: {velha.name}")
            shutil.rmtree(velha, ignore_errors=True)

    origem = RAIZ / "dist" / f"{NOME}-Setup.exe"
    destino = pasta / f"{NOME}-Setup.exe"
    shutil.copy2(origem, destino)

    print("  limpando as sobras do empacotamento (só o que este script gerou)")
    _limpar_e_avisar()

    sobrando = [f.name for f in pasta.iterdir()]
    if sobrando != [f"{NOME}-Setup.exe"]:
        print(f"  ATENCAO: sobrou coisa a mais na pasta: {sobrando}")

    print(f"\n  pronto: {destino}  ({_tamanho(destino)})")
    return destino


def main(argumentos_da_linha: list[str] | None = None) -> int:
    """Linha de comando: escolhe o que construir conforme --modo (ver o
    cabeçalho do arquivo para os modos disponiveis). argumentos_da_linha e
    para os testes; sem ele, vale o que veio na linha de comando."""
    analisador = argparse.ArgumentParser(
        description="Gera o Editor de Impressão pronto para entregar."
    )
    analisador.add_argument(
        "--modo",
        choices=["tudo", "pasta", "arquivo", "instalador", "entrega"],
        default="tudo",
        help="entrega = só o instalador, na Área de Trabalho, e apaga o resto "
             "do que este script gerou (o que outros scripts guardam em dist "
             "fica)",
    )
    analisador.add_argument(
        "--motor-kraken", type=Path, default=None,
        help="pasta do motor do Kraken a levar (padrão: o primeiro motor do jeito novo "
             "em motor-kraken\\, EditorImpressao-arquivos\\ferramentas\\motor-kraken ou "
             "saida_teste\\motor-kraken)",
    )
    argumentos = analisador.parse_args(argumentos_da_linha)
    global MOTOR_ESCOLHIDO
    MOTOR_ESCOLHIDO = argumentos.motor_kraken

    # Antes de apagar qualquer coisa (o modo entrega apaga, logo abaixo, o que
    # este script gerou antes): sem os modelos, nada do que sairia daqui presta.
    if not _avisar_modelos_faltando():
        return 1
    # O mesmo para as pecas dos detectores de texto (so a versao em pasta e o
    # instalador as levam; o arquivo único nao).
    if argumentos.modo != "arquivo" and _avisar_pecas_faltando(MOTOR_ESCOLHIDO) is None:
        return 1

    if argumentos.modo == "entrega":
        inicio = time.perf_counter()
        # Comeca do zero, mas SO com o que e deste script: o teste de
        # velocidade do Kaique, em dist\, fica (ver apagar_o_que_gerou).
        _limpar_e_avisar()
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
