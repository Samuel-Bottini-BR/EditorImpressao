"""Gera o programa pronto para entregar (Etapa 8).

    python empacotar.py                 # tudo: pasta + arquivo único + instalador
    python empacotar.py --modo pasta        # só a versão portatil em pasta
    python empacotar.py --modo arquivo      # só o .exe único (pendrive)
    python empacotar.py --modo instalador   # pasta + EditorImpressao-Setup.exe
    python empacotar.py --modo entrega      # só o instalador, na Área de Trabalho

AS TRES SAIDAS (passo 2 do plano da parte do Windows, 19/11/2026): a pasta
portatil (com o motor do Kraken solto, como sempre), a atualizacao do Velopack
(sem o motor, com o motor-exigido.json) e o instalador .msi (com o motor
publicado num arquivo so em instalar\\). O que muda entre elas mora num lugar
so: SAIDAS. O vpk roda so por rodar_vpk. Quem publica e o
publicar_versao_kaique.py.

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
  Microsoft Corporation (preparar_vc_redist). No Inno, vai so dentro do
  instalador (build\\vc_redist.x64.exe), que o roda em silencio quando o Visual
  C++ 2015-2022 x64 falta ou e mais velho (instalador.iss, secao [Code]). Nas
  saidas do Velopack, vai em <pasta>\\instalar\\, posto pela montagem
  (Saida.vc_em_instalar; ver "o pacote do Velopack" abaixo).

A TRAVA vale para tudo isso, como para os modelos: faltando qualquer peca
(motor, Tesseract, idioma, licenca, vc_redist, modelo), ou o motor sendo do
jeito velho, o script PARA antes de gerar qualquer coisa, dizendo o que falta
e como resolver; depois de gerar, confere que cada peca chegou inteira na
pasta (conferir_pecas_no_pacote) e dentro do instalador
(pecas_faltando_no_registro_do_inno). O arquivo único (pendrive) NAO leva o
Kraken nem o Tesseract (sao programas a parte, de ~1,4 GB): so o docTR.

O DETECTOR DE GRAVURA DO SCANTAILOR VAI JUNTO (item 1.2, 29/09/2026). A DLL
core\\nativo\\st_gravura.dll (codigo original do ScanTailor Advanced, GPL-3,
compilado por compilar_detector_gravura.py) e o st_gravura.txt que diz de
onde ela veio vao para _internal\\core\\nativo\\ (onde
core/gravura_scantailor.CAMINHO_DLL a procura; ver nativos_do_programa).
Mesma trava dos modelos: faltando, o script PARA antes de gerar; depois,
confere que chegou inteira na pasta e dentro do instalador; e o
instalador.iss recusa compilar sem ela. Sem a DLL o programa nao quebra (cai
no detector de gravura antigo), mas perde o 1.2 calado - o mesmo tipo de
defeito do instalador sem modelos de 25/09.

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
# O icone do programa (D-746): um lugar so, o brasao.py. Fica no git, gerado
# pelo gerar_brasao.py: empacotar nao depende de desenhar nada.
import brasao  # noqa: E402 - so caminhos e numeros, nada pesado

ICONE = brasao.ICONE

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
           "core.gravura_scantailor",
           # a DLL comum das ferramentas do ScanTailor (bug de 20/10/2026)
           "core.st_ferramentas",
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
# as tres saidas (plano da parte do Windows, passo 2, peca 8; D-768, D-777, D-788)
# ---------------------------------------------------------------------------
#
# O LUGAR UNICO do que muda entre o que este script monta. Tudo o que difere
# entre a pasta portatil, a atualizacao e o instalador le daqui (construir_pasta,
# o comando do vpk, a preparacao da pasta, o que o pacote tem de ter e o que nao
# pode ter, a conta do espaco). Nao escreva "se for o instalador..." em outro
# lugar: acrescente um campo aqui (CLAUDE.md §11.12).
#
# - pasta portatil (--modo pasta, e o que o Inno empacota): o motor do Kraken
#   solto ao lado do .exe, como sempre;
# - atualizacao (o que o publicar sobe a cada versao): SEM o motor (D-768), com o
#   motor-exigido.json (que motor esta versao pede); sem .msi e sem zip portatil
#   (D-777);
# - instalador (so quando o Samuel pede, D-777): a atualizacao mais o motor como
#   UM arquivo so em instalar\ (D-788, D-727), e o .msi. O pacote dele (.nupkg)
#   NAO e o publicado: o publicado e sempre o da atualizacao (senao todo mundo
#   baixaria o motor na proxima atualizacao, contra a D-768). Por isso o mesmo
#   numero de versao tem dois conteudos: e de proposito (estudo do Kraken, risco 5).
# - o Visual C++ em instalar\ (D-727) vai nas duas saidas do Velopack (a
#   atualizacao e o instalador) e NAO na pasta portatil (o Inno o pega de build\,
#   construir_instalador). Passo 2, volta 6 (a prova a vista de 20/11/2026): ele
#   era posto so em preparar_saida, depois da conferencia da pasta, e toda
#   publicacao montada do zero parava em "nao tem o Visual C++ em instalar\".
#   Agora quem o poe e a MONTAGEM (construir_pasta), quem confere e
#   conferir_pasta_pronta, e as duas leem vc_em_instalar daqui.

@dataclass(frozen=True)
class Saida:
    """Uma das tres saidas do empacotador (ver o comentario acima)."""

    nome: str
    motor_solto: bool          # a pasta motor-kraken\ inteira ao lado do .exe
    motor_exigido: bool        # o motor-exigido.json dentro do pacote
    motor_em_instalar: bool    # o arquivo do motor (um zip so) em instalar\
    com_msi: bool              # o vpk faz o .msi (instalar em Arquivos de Programas)
    vc_em_instalar: bool       # o Visual C++ oficial em instalar\ (posto na montagem, D-727)


PORTATIL = Saida("pasta portátil", motor_solto=True, motor_exigido=False, motor_em_instalar=False, com_msi=False,
                 vc_em_instalar=False)
ATUALIZACAO = Saida("atualização", motor_solto=False, motor_exigido=True, motor_em_instalar=False, com_msi=False,
                    vc_em_instalar=True)
INSTALADOR = Saida("instalador", motor_solto=False, motor_exigido=True, motor_em_instalar=True, com_msi=True,
                   vc_em_instalar=True)
SAIDAS = (PORTATIL, ATUALIZACAO, INSTALADOR)

# O arquivo que diz que motor a versao pede (dentro do pacote, na raiz da pasta do
# programa: current\motor-exigido.json no instalado). Coberto pela assinatura do
# programa, porque vai dentro do .nupkg assinado. Quem le e o ajudante (passo 3).
NOME_DO_MOTOR_EXIGIDO = "motor-exigido.json"
# A ficha da versao (que versao e de que commit a pasta saiu; plano v1, peca 8,
# "um numero de versao so"): o publicar recusa uma pasta pronta de outra versao.
NOME_DA_FICHA_DA_VERSAO = "versao-do-pacote.json"


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


# ---------------------------------------------------------------------------
# o detector de gravura do ScanTailor (item 1.2), que e uma DLL nossa
# ---------------------------------------------------------------------------

def nativos_do_programa() -> list[tuple[Path, str]]:
    """As bibliotecas nativas (DLL) que o programa usa: [(origem, destino no pacote)].

    As duas DLLs do ScanTailor, cada uma com o .txt ao lado (de onde veio o
    codigo, versao, soma - e a licenca GPL-3 exige dizer isso):
      - core/nativo/st_gravura.dll, o detector de gravura (item 1.2; o
        caminho vem de core/gravura_scantailor.CAMINHO_DLL);
      - core/nativo/st_ferramentas.dll, a DLL comum das outras ferramentas do
        ScanTailor (limpar pontinhos, dividir, endireitar, caixas; o caminho
        vem de core/st_ferramentas.CAMINHO_DLL). Entrou em 21/10/2026: o bug
        da Lista de bugs de 20/10 ("Instalador sem a st_ferramentas.dll") -
        sem ela o programa instalado caia no caminho "nosso" sem avisar. O destino e o caminho relativo a raiz do codigo
    (core/nativo), onde o codigo empacotado procura. Vai por --add-data, e nao
    --add-binary: a DLL usa o Qt do PySide6 que ja vai no pacote, e a analise
    de dependencias do PyInstaller so arrastaria copias dele.
    """
    from core import detectar_regioes, gravura_scantailor, st_ferramentas

    raiz_do_codigo = Path(detectar_regioes.__file__).resolve().parent.parent
    usados = tuple(caminho for dll in (gravura_scantailor.CAMINHO_DLL, st_ferramentas.CAMINHO_DLL)
                   for caminho in (dll, dll.with_suffix(".txt")))
    return [(origem, origem.relative_to(raiz_do_codigo).parent.as_posix()) for origem in usados]


def nativos_faltando() -> list[Path]:
    """As DLLs (e o .txt delas) que o programa usa e que nao estao em disco."""
    return [origem for origem, _ in nativos_do_programa() if not origem.is_file()]


def _avisar_nativos_faltando() -> bool:
    """Imprime a mensagem de DLL faltando. Devolve True se esta tudo la.

    Chamada ANTES de apagar ou gerar qualquer coisa (a trava dos modelos).
    """
    faltando = nativos_faltando()
    if not faltando:
        return True
    print("\n  PAREI: falta uma DLL do ScanTailor, e sem ela o programa sairia usando")
    print("  as contas antigas, sem avisar.")
    for origem in faltando:
        print(f"    não achei {origem}")
    print("  As DLLs estão no git (core\\nativo\\). Se sumiram, recompile com:")
    print("    .venv\\Scripts\\python.exe compilar_detector_gravura.py   (st_gravura)")
    print("    .venv\\Scripts\\python.exe compilar_st_ferramentas.py     (st_ferramentas)")
    return False


def conferir_nativos_no_pacote(pasta: Path) -> list[str]:
    """A versao em pasta ja gerada tem cada DLL em <pasta>\\_internal\\<destino>\\,
    com o mesmo tamanho do original? Devolve os problemas (vazio = tudo certo)."""
    problemas: list[str] = []
    for origem, destino in nativos_do_programa():
        empacotado = Path(pasta) / INTERNO / destino / origem.name
        if not empacotado.is_file():
            problemas.append(f"{origem.name} não chegou em {empacotado}")
        elif not origem.is_file():
            problemas.append(f"{origem.name}: o original sumiu de {origem}")
        elif empacotado.stat().st_size != origem.stat().st_size:
            problemas.append(f"{origem.name} chegou pela metade em {empacotado}")
    return problemas


def nativos_faltando_no_registro_do_inno(registro: str) -> list[str]:
    """As DLLs que o Inno Setup NAO comprimiu para dentro do instalador (ver
    modelos_faltando_no_registro_do_inno)."""
    comprimidos = _comprimidos(registro)
    faltando: list[str] = []
    for origem, destino in nativos_do_programa():
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
    motor e None quando a saida nao leva o motor solto (a atualizacao e o
    instalador, ver SAIDAS; passo 2 do plano da parte do Windows).
    """

    motor: Path | None
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

    A forma do motor (o Python, o servidor do protocolo certo, o modelo) vem da
    peca unica do motor, core/ocr_kraken.problemas_da_forma (passo 2 do plano,
    19/11/2026: antes esta conta estava escrita aqui). Aqui fica so a regra de
    montagem (jeito velho). Esta funcao NAO le a ficha (motor.json): o "inteiro
    e da versao certa" e core/ocr_kraken.conferir_motor, que juntar_pecas e o
    publicar chamam depois de escolher o motor (os testes antigos usam um motor
    de mentira sem ficha aqui).
    """
    import montar_motor_kraken as m
    from core import ocr_kraken

    pasta = Path(pasta)
    python = pasta / "python"
    problemas = ocr_kraken.problemas_da_forma(pasta)
    if not (python / "python.exe").is_file():
        return problemas
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
    """A assinatura digital de um arquivo, lida pelo proprio Windows, pela peca unica do Windows
    (core/windows.ler_assinatura_digital; ate o passo 2 do plano da parte do Windows este arquivo abria o
    PowerShell por conta propria, item K01 da lista de excecoes do porteiro).

    Devolve {"status", "assinante", "produto", "versao"} ("status" = "Valid"
    quando a assinatura confere; quem assinou e conferido por vc_redist_confere).
    Nunca levanta: a falha da peca vira status "erro: <motivo>", que nunca confere.
    Arriscado: abrir o PowerShell aqui de novo (o porteiro barra, K01).
    """
    from core import windows

    lido = windows.ler_assinatura_digital(arquivo)
    if not lido.deu_certo:
        return {"status": f"erro: {lido.motivo}", "assinante": "", "produto": "", "versao": ""}
    return {chave: lido.dados[chave] for chave in ("status", "assinante", "produto", "versao")}


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


def conferir_o_visual_c(arquivo: Path) -> tuple[str, list[str]]:
    """O arquivo e o Visual C++ oficial da Microsoft? Devolve (a versao lida da assinatura, os problemas; vazio = e).

    O LUGAR UNICO da regua do Visual C++ (passo 2, volta 7, D-818): a assinatura lida pelo Windows
    (assinatura_do_arquivo, pela peca unica) e conferida por vc_redist_confere. Usada pela montagem
    (preparar_vc_redist, no arquivo baixado e no achado) e pela conferencia da pasta (conferir_pasta_pronta, no
    arquivo que esta em instalar\\ de qualquer pasta, montada do zero ou ja montada). Antes a montagem conferia pela
    assinatura e a pasta ja montada so pelo nome do arquivo (achado 1 do relatorio 6). Arriscado: conferir o Visual
    C++ por outra conta em qualquer lugar (duas reguas para a mesma regra, CLAUDE.md §11.12)."""
    assinatura = assinatura_do_arquivo(arquivo)
    return assinatura.get("versao", "") or "", vc_redist_confere(assinatura)


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
        _, problemas = conferir_o_visual_c(provisorio)
        if problemas:
            return None, "", [f"o arquivo baixado ({provisorio}) não é o oficial: " + "; ".join(problemas)]
        provisorio.rename(arquivo)
    versao, problemas = conferir_o_visual_c(arquivo)
    if problemas:
        return None, "", [f"{arquivo} não é o oficial da Microsoft: " + "; ".join(problemas)
                          + " (apague à mão e rode de novo para baixar outro)"]
    return arquivo, versao, []


def juntar_pecas(motor_escolhido: Path | None = None, baixar: bool = True,
                 com_motor: bool = True) -> tuple[PecasDosDetectores | None, list[str]]:
    """Confere TODAS as pecas dos detectores de texto. (pecas, []) ou (None, problemas).

    com_motor=False (a saida nao leva o motor solto, Saida.motor_solto): nao
    procura o motor do Kraken neste PC (a atualizacao pede o motor PUBLICADO,
    pelo motor-exigido.json; o instalador leva o arquivo publicado). Com
    com_motor=True (a pasta portatil), como sempre."""
    from core import ocr_tesseract

    problemas = []
    motor = None
    if com_motor:
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


def _avisar_pecas_faltando(motor_escolhido: Path | None = None,
                           com_motor: bool = True) -> PecasDosDetectores | None:
    """juntar_pecas, imprimindo o que falta. Chamada ANTES de apagar ou gerar qualquer coisa."""
    pecas, problemas = juntar_pecas(motor_escolhido, com_motor=com_motor)
    if pecas is not None:
        print(f"  motor do Kraken: {pecas.motor or 'não vai solto nesta saída (vai o motor publicado)'}")
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
    Os caminhos vem da lista unica relativos_do_tesseract (volta 7 do passo 2); aqui so se junta a origem de cada um.
    """
    from core import ocr_tesseract

    origens = [pecas.tesseract / nome for nome in ARQUIVOS_DO_TESSERACT]
    origens += [pecas.licencas / nome for nome in LICENCAS_DO_TESSERACT]
    origens += [pecas.tessdata / f"{idioma}.traineddata" for idioma in ocr_tesseract.IDIOMAS_DO_INSTALADOR]
    return list(zip(origens, relativos_do_tesseract(), strict=True))


def relativos_do_tesseract() -> list[str]:
    """Os caminhos (relativos a pasta do programa, com /) do Tesseract que vai ao lado do .exe: os 27 arquivos, as
    licencas e os idiomas. A LISTA UNICA (passo 2, volta 7, D-818): o que a montagem copia (_destinos_das_pecas, na
    mesma ordem), o que o Inno confere, o que a conferencia da pasta cobra de qualquer pasta (conferir_pasta_pronta) e
    o que a conferencia do pacote cobra (esperados_no_pacote_do_velopack). Arriscado: escrever esta lista em outro
    lugar."""
    from core import ocr_tesseract

    return ([f"{PASTA_DO_TESSERACT}/{nome}" for nome in (*ARQUIVOS_DO_TESSERACT, *LICENCAS_DO_TESSERACT)]
            + [f"{PASTA_DO_TESSERACT}/tessdata/{idioma}.traineddata" for idioma in ocr_tesseract.IDIOMAS_DO_INSTALADOR])


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
    """Poe o motor do Kraken (so quando pecas.motor existe: a pasta portatil, SAIDAS)
    e o Tesseract ao lado do .exe, na versao em pasta."""
    from core import ocr_tesseract

    if pecas.motor is not None:
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
    """Confere que cada peca chegou inteira na versao em pasta (vazio = tudo certo).

    Sem motor nas pecas (a atualizacao e o instalador, SAIDAS): confere que a
    pasta motor-kraken\\ NAO esta la (D-768: a atualizacao nunca leva o motor)."""
    problemas = []
    for origem, relativo in _destinos_das_pecas(pecas):
        alvo = Path(pasta) / relativo
        if not alvo.is_file():
            problemas.append(f"{relativo} não chegou")
        elif alvo.stat().st_size != origem.stat().st_size:
            problemas.append(f"{relativo} chegou pela metade")
    motor = Path(pasta) / PASTA_DO_MOTOR
    if pecas.motor is None:
        if motor.exists():
            problemas.append(f"{PASTA_DO_MOTOR}\\ está na pasta, e esta saída não leva o motor solto")
    elif not motor.is_dir():
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
    # O icone do .exe (e dos atalhos, que usam o do .exe) e o brasao, desenhado
    # do vetor em cada tamanho (D-746, 17/11/2026; brasao.py, gerar_brasao.py).
    # As imagens do giro da tela de carregamento vao junto com recursos/ acima.
    comando += ["--icon", str(ICONE)]

    # Um --add-data por ARQUIVO de modelo, e nao a pasta modelos/ inteira: ela
    # tem tambem o mobile_sam.zip (36 MB, repetindo o que ja vai), um script
    # de referencia e o __pycache__ dele. Ver modelos_do_programa.
    for origem, destino in modelos_do_programa():
        comando += ["--add-data", f"{origem}{separador}{destino}"]
    # a DLL do detector de gravura do ScanTailor (item 1.2): nativos_do_programa
    for origem, destino in nativos_do_programa():
        comando += ["--add-data", f"{origem}{separador}{destino}"]

    comando.append(str(RAIZ / "main.py"))
    return comando


def _pyinstaller(onefile: bool) -> bool:
    """Roda o PyInstaller. onefile=False gera a versão em pasta."""
    return subprocess.run(comando_do_pyinstaller(onefile), cwd=RAIZ).returncode == 0


def comando_do_inno(inno: Path, script: Path) -> list[str]:
    """O comando do compilador do Inno Setup, com a versao lida do versao.py.

    16/11/2026 (etapa 3 da frente do Kaique): o instalador.iss nao tem mais o
    numero escrito nele; recebe-o daqui (/DMinhaVersao=...) e recusa compilar
    sem ele. Um lugar so para o numero: versao.VERSAO.
    """
    import versao

    return [str(inno), f"/DMinhaVersao={versao.VERSAO}", str(script)]


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


def construir_pasta(saida: Saida = PORTATIL) -> Path | None:
    """A pasta do programa (dist\\EditorImpressao\\). De fabrica, a versao portatil
    em pasta, que e tambem o que o instalador do Inno empacota; com
    saida=ATUALIZACAO (o publicar), a mesma pasta SEM o motor do Kraken solto
    (SAIDAS, D-768).

    Para (devolve None) se faltar modelo ou peca dos detectores de texto
    ANTES de apagar a pasta anterior, e de novo se algum modelo ou peca nao
    chegar inteiro (ver conferir_modelos_no_pacote e conferir_pecas_no_pacote).
    Nas saidas do Velopack (Saida.vc_em_instalar: a atualizacao e o instalador)
    poe o Visual C++ conferido em instalar\\ (preparar_pasta_para_o_velopack; o
    LUGAR UNICO que o poe; passo 2, volta 6: antes ele so era posto depois da
    conferencia da pasta, em preparar_saida, e o publicar montado do zero parava
    sempre). Assim a pasta montada aqui sai no mesmo estado que
    conferir_pasta_pronta cobra de uma pasta que vem de fora.
    No fim grava a ficha da versao (gravar_ficha_da_versao). A ficha vem DEPOIS
    de tudo de proposito: e o sinal de "montada inteira" (uma montagem que para
    no meio fica sem ficha, e conferir_pasta_pronta a recusa). Arriscado: gravar
    a ficha antes de alguma peca, ou por o Visual C++ na pasta portatil (o Inno
    o instalaria tambem em {app}).
    """
    global _PECAS
    print(f"\n=== Versao em pasta ({saida.nome}) ===")
    if not _avisar_modelos_faltando() or not _avisar_nativos_faltando():
        return None
    pecas = _avisar_pecas_faltando(MOTOR_ESCOLHIDO, com_motor=saida.motor_solto)
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
    problemas = conferir_nativos_no_pacote(destino)
    if problemas:
        print("  PAREI: o programa saiu sem o detector de gravura do ScanTailor:")
        for problema in problemas:
            print(f"    {problema}")
        return None
    print("  detector de gravura do ScanTailor (core\\nativo\\st_gravura.dll) dentro da pasta, conferido")
    copiar_pecas(destino, pecas)
    problemas = conferir_pecas_no_pacote(destino, pecas)
    if problemas:
        print("  PAREI: o programa saiu sem alguma peça dos detectores de texto:")
        for problema in problemas:
            print(f"    {problema}")
        return None
    print("  motor do Kraken e Tesseract dentro da pasta, conferidos" if pecas.motor is not None
          else "  Tesseract dentro da pasta, conferido; o motor do Kraken não vai solto nesta saída (conferido)")
    if saida.vc_em_instalar:
        problemas = preparar_pasta_para_o_velopack(destino, pecas)
        if problemas:
            print("  PAREI: o Visual C++ não chegou inteiro na pasta:")
            for problema in problemas:
                print(f"    {problema}")
            return None
        import atualizacao

        print(f"  Visual C++ em {atualizacao.PASTA_DO_QUE_SE_INSTALA}\\, conferido (o tamanho do original)")
    _PECAS = pecas
    gravar_ficha_da_versao(destino, saida)

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
    if not _avisar_modelos_faltando() or not _avisar_nativos_faltando():
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
        comando_do_inno(inno, script), cwd=RAIZ, capture_output=True, text=True
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
    faltando = nativos_faltando_no_registro_do_inno(resultado.stdout)
    if faltando:
        destino.unlink(missing_ok=True)
        print("  PAREI: o Inno Setup não pôs o detector de gravura do ScanTailor no instalador")
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


# ---------------------------------------------------------------------------
# o pacote do Velopack (etapa 3 da frente do Kaique, 16/11/2026; D-723, D-727;
# refeito no passo 2 do plano da parte do Windows, 19/11/2026)
# ---------------------------------------------------------------------------
#
# O Velopack (decisao D-723, "velopack") troca o Inno Setup: monta o
# instalador (MSI "por maquina": Arquivos de Programas, pede administrador) e
# o pacote de atualizacao. A pasta que ele empacota e a dist\EditorImpressao\
# da construir_pasta, com as mesmas travas (modelos, DLLs, Tesseract), mas SEM o
# motor do Kraken solto (SAIDAS, D-768). O que muda:
# - o Visual C++ oficial vai DENTRO do pacote, em instalar\ (D-727: "se tiver
#   qualquer coisa que o kaique precise, ele tem que estar no instalador"); o
#   "--framework vcredist143-x64" do Velopack baixaria da internet, e por isso
#   NAO e usado. Quem o roda (so se faltar) e a tarefa do Windows, como SYSTEM
#   (atualizacao.instalar_visual_c_se_faltar). Quem o poe na pasta e a montagem
#   (construir_pasta, Saida.vc_em_instalar), antes da ficha; quem confere a pasta
#   antes do vpk e conferir_pasta_pronta (volta 6 do passo 2);
# - o motor-exigido.json (que motor esta versao pede, lido do motor PUBLICADO) e,
#   so no instalador, o arquivo do motor em instalar\ (preparar_saida);
# - sem o pacote de diferenca (--delta None, D-789) e sem o zip portatil
#   (--noPortable, D-777); o .msi so no instalador. O Setup.exe o vpk sempre faz
#   (a 1.2.161 recusa --noInst com --noPortable): quem o apaga e o publicar (D-795);
# - UMA funcao roda o vpk (rodar_vpk), com a pasta temporaria dentro do rascunho
#   e a vigia do espaco (D-776);
# - depois de montar, conferir_pacote_do_velopack abre o pacote e confere que
#   cada peca esta la dentro e que nada proibido esta (o motor solto).
# Quem chama: publicar_versao_kaique.py (a "versao para o Kaique"). O Inno
# Setup continua aqui, sem mudar, ate o Samuel decidir tira-lo (os testes dele).

TITULO_DO_PACOTE = "Editor de Impressão"        # nome no menu Iniciar e no atalho
AUTORES_DO_PACOTE = "Instituto de Preservacao de Livros"   # o mesmo do instalador.iss
# Onde o dotnet tool install -g poe o vpk (o empacotador do Velopack).
LUGARES_DO_VPK = [Path.home() / ".dotnet" / "tools" / "vpk.exe"]
# A versao do vpk, PRESA (D-763): a mesma do velopack do pip (requirements.txt,
# velopack==...; tests/test_nome_do_pacote.py cobra que as duas batem). O vpk
# leva para dentro do .msi a limpeza do desinstalador: a 1.2.161 foi a provada
# em 17/11/2026 (relatorios/velopack-pasta-2026-11-17/ e
# relatorios/nome-pacote-2026-11-17/): o desinstalador dela apaga
# %LOCALAPPDATA%\<TITULO_DO_PACOTE> (o modelo do .msi passa o titulo a limpeza).
# SUBIR DE VERSAO EXIGE REPETIR A PROVA: o Velopack mais novo tem outra limpeza
# (UserCleanupDeferred), que roda como quem desinstala e apaga
# %LocalAppData%\<nome do pacote> de proposito. Tambem por isso o titulo nunca
# e o nome da pasta dos projetos (tests/test_nome_do_pacote.py).
VERSAO_DO_VPK = "1.2.161"
COMO_INSTALAR_O_VPK = f"dotnet tool install -g vpk --version {VERSAO_DO_VPK}"
# Dentro do pacote do Velopack (.nupkg, um zip), a pasta do programa fica em lib\app\.
PASTA_NO_NUPKG = "lib/app/"

# Os nomes do que o vpk 1.2.161 grava na pasta de saida (lidos no codigo dele,
# src/vpk/Velopack.Core/DefaultName.cs: o sufixo e "-" + o canal, "win"; e
# conferidos na pasta da etapa 5). NOME_DO_INDICE e o que o programa do Kaique
# le para achar as versoes (releases.win.json).
NOME_DO_INDICE = "releases.win.json"


def nome_do_setup() -> str:
    """'<ID>-win-Setup.exe': o instalador pequeno que o vpk sempre faz (D-795: o publicar o apaga)."""
    import versao

    return f"{versao.ID_DO_PACOTE}-win-Setup.exe"


def nome_do_msi() -> str:
    """'<ID>-win.msi': o instalador .msi como o vpk o grava (so na saida INSTALADOR). O mesmo nome em toda versao."""
    import versao

    return f"{versao.ID_DO_PACOTE}-win.msi"


def nome_do_msi_publicado(versao_do_pacote: str) -> str:
    """'<ID>-<versao>-win.msi': o nome com que o .msi e publicado e guardado (achado 7 de quem tentou quebrar: com o
    nome do vpk, igual em toda versao, o servidor das versoes entregava o .msi de outra versao)."""
    import versao

    return f"{versao.ID_DO_PACOTE}-{versao_do_pacote}-win.msi"


def achar_vpk() -> Path | None:
    """O vpk.exe (dotnet tool install -g vpk), ou None."""
    achado = shutil.which("vpk")
    if achado:
        return Path(achado)
    return next((c for c in LUGARES_DO_VPK if c.is_file()), None)


def preparar_pasta_para_o_velopack(pasta: Path, pecas: PecasDosDetectores) -> list[str]:
    """Poe o Visual C++ oficial (ja conferido pela assinatura da Microsoft) em
    <pasta>\\instalar\\, com a versao dele num .txt ao lado. Devolve os problemas
    (o arquivo que chegou menor que o original). O LUGAR UNICO que poe o Visual
    C++ na pasta do Velopack. Chamada so pela montagem (construir_pasta, nas
    saidas com Saida.vc_em_instalar); ate a volta 6 do passo 2 era chamada por
    preparar_saida, depois da conferencia da pasta (o defeito da prova a vista
    de 20/11/2026). O nome e o de antes: os testes antigos o usam."""
    import atualizacao

    destino = Path(pasta) / atualizacao.PASTA_DO_QUE_SE_INSTALA
    destino.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pecas.vc_redist, destino / atualizacao.VC_REDIST_NOME)
    (destino / atualizacao.VC_REDIST_VERSAO).write_text(pecas.vc_versao, encoding="utf-8")
    if (destino / atualizacao.VC_REDIST_NOME).stat().st_size != Path(pecas.vc_redist).stat().st_size:
        return [f"{atualizacao.VC_REDIST_NOME} chegou pela metade em {destino}"]
    return []


# ---- o motor PUBLICADO que a versao pede (D-768, D-788, D-790) -------------

@dataclass(frozen=True)
class MotorPublicado:
    """O motor do Kraken publicado e lido de volta (pelo publicar): a versao do
    motor, o nome do arquivo, a soma SHA-256 dele (a da assinatura do Samuel,
    conferida) e a etiqueta da publicacao. E o que vai no motor-exigido.json."""

    versao: int
    arquivo: str
    sha256: str
    etiqueta: str


def texto_do_motor_exigido(motor: MotorPublicado) -> str:
    """O conteudo do motor-exigido.json (o lugar unico do formato; o ajudante le no passo 3)."""
    import json

    import versao

    return json.dumps({"formato": 1, "pacote": versao.ID_DO_PACOTE_DO_MOTOR, "versao": motor.versao,
                       "etiqueta": motor.etiqueta, "arquivo": motor.arquivo, "sha256": motor.sha256.lower()},
                      ensure_ascii=False, indent=1)


def preparar_saida(pasta: Path, saida: Saida, pecas: PecasDosDetectores | None,
                   motor: MotorPublicado | None, arquivo_do_motor: Path | None = None) -> list[str]:
    """Faz na pasta o que MUDA entre as saidas do Velopack (SAIDAS; o lugar unico):

    - motor-exigido.json, se a saida pede (motor e o publicado, lido de volta);
    - o arquivo do motor em instalar\\, se a saida pede (arquivo_do_motor: o zip
      ja conferido pela soma assinada; e copiado, nunca movido);
    - e tira de instalar\\ um arquivo de motor que nao deve ir (a mesma pasta
      serve as duas saidas, em sequencia: atualizacao e depois instalador).
    Devolve os problemas (vazio = feito). Quem diz se a pasta esta pronta para o
    vpk e conferir_pasta_pronta (construir_pacote_do_velopack a chama antes desta,
    para uma pasta recusada nunca ser mexida; volta 7, achado 4 do relatorio 6).

    O Visual C++ NAO e posto aqui (passo 2, volta 6): ele e igual nas duas saidas
    e vem da montagem (construir_pasta) ou da pasta pronta. Antes era posto aqui,
    quando havia pecas, DEPOIS da conferencia da pasta: o publicar montado do
    zero parava sempre (a prova a vista de 20/11/2026). 'pecas' nao e mais usado;
    fica na assinatura porque quem chama o passa pela posicao (o publicar e
    tests/test_publicar_motor.py). Arriscado: voltar a por o Visual C++ aqui
    (duas pecas poriam o mesmo arquivo, e a conferencia voltaria a ver a pasta
    antes dele)."""
    import atualizacao
    import versao

    pasta = Path(pasta)
    problemas: list[str] = []
    if saida.motor_exigido:
        if motor is None:
            return problemas + ["falta saber qual motor publicado esta versão pede"]
        (pasta / NOME_DO_MOTOR_EXIGIDO).write_text(texto_do_motor_exigido(motor), encoding="utf-8")
    instalar = pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA
    for sobra in instalar.glob(versao.arquivo_do_motor("*")):
        if not (saida.motor_em_instalar and motor is not None and sobra.name == motor.arquivo):
            sobra.unlink()
    if saida.motor_em_instalar:
        if motor is None or arquivo_do_motor is None or not Path(arquivo_do_motor).is_file():
            return problemas + ["falta o arquivo do motor publicado para pôr no instalador"]
        import assinatura

        instalar.mkdir(parents=True, exist_ok=True)
        alvo = instalar / motor.arquivo
        shutil.copyfile(arquivo_do_motor, alvo)
        if assinatura.soma_sha256(alvo) != motor.sha256.lower():
            alvo.unlink()
            problemas.append(f"o arquivo do motor copiado para {instalar} não tem a soma assinada")
    return problemas


def comando_do_vpk(vpk: Path, pasta: Path, saida: Path, versao_do_pacote: str, com_msi: bool = True) -> list[str]:
    """O comando do 'vpk pack' (separado para os testes conferirem sem rodar). O LUGAR UNICO do comando.

    --msi --instLocation PerMachine (so quando com_msi: a saida INSTALADOR):
    instala em Arquivos de Programas, para todas as contas do computador (a
    conta dos testes a distancia usa o mesmo programa, D-717), e pede
    administrador (D-723). com_msi=True de fabrica e so o valor padrao do
    parametro (os testes antigos da D-727 conferem o comando do instalador):
    quem decide e a saida (Saida.com_msi), que o construir_pacote_do_velopack passa.
    Sem --framework: nada se baixa na hora de instalar (D-727).
    --delta None: sem o pacote de diferenca (D-789). --noPortable: sem o zip
    portatil (D-777); o vpk 1.2.161 recusa --noInst junto, por isso o Setup.exe
    sempre sai (D-795).
    """
    import versao

    comando = [str(vpk), "pack",
               "--packId", versao.ID_DO_PACOTE,
               "--packVersion", versao_do_pacote,
               "--packDir", str(pasta),
               "--mainExe", f"{NOME}.exe",
               "--packTitle", TITULO_DO_PACOTE,
               "--packAuthors", AUTORES_DO_PACOTE,
               "--outputDir", str(saida),
               # 64 bits (o Python e o programa sao x64). Sem isto o vpk supoe x86
               # e o MSI iria para "Arquivos de Programas (x86)" (achado no ensaio).
               "--runtime", "win-x64",
               "--delta", "None",
               "--noPortable"]
    if com_msi:
        comando += ["--msi", "--instLocation", "PerMachine"]
    # o icone do instalador e do programa na lista de programas (D-746)
    comando += ["--icon", str(ICONE), "--skip-updates"]
    return comando


# ---- o espaco no disco do rascunho (D-776) ---------------------------------

GB = 1024 ** 3
# A reserva do C: (D-776, Samuel 18/11: "ok" a 20 GB): o publicar nao comeca se,
# somando o que vai usar, o disco do rascunho ficaria com menos que isto, e para
# se, durante, o espaco livre cair abaixo disto. Lida na hora por quem confere
# (o publicar --reserva-gb so a AUMENTA, para a prova do aviso; nunca abaixo de 20).
RESERVA_DO_DISCO = 20 * GB
MARGEM_DA_CONTA = 1 * GB          # o que a conta acrescenta por cima (registros, a ficha, o .nupkg do instalador)
INTERVALO_DA_VIGIA_S = 2.0


def espaco_livre(pasta: Path) -> int:
    """Bytes livres no disco da pasta (a primeira pasta que existe subindo). Levanta OSError."""
    pasta = Path(pasta)
    while not pasta.exists() and pasta.parent != pasta:
        pasta = pasta.parent
    return shutil.disk_usage(pasta).free


def tamanho_da_pasta(pasta: Path) -> int:
    """Bytes de todos os arquivos dentro da pasta."""
    return sum(f.stat().st_size for f in Path(pasta).rglob("*") if f.is_file())


def espaco_que_vai_usar(tamanho_da_pasta_do_programa: int, saidas: tuple[Saida, ...],
                        tamanho_do_motor: int = 0, baixado_para_o_rascunho: int = 0) -> int:
    """A conta do que o vpk vai usar no disco do rascunho (D-776: "o que vai usar de verdade").

    Conta refeita na volta 2 (achado 9 de quem tentou quebrar), pela leitura do vpk 1.2.161:
    - PackageBuilder.cs:76 (a pasta temporaria do pacote vive ate o FIM do pack) e
      :117-162: a copia do pre-processo (P) e a copia do pacote (P) ficam ao mesmo
      tempo que o pacote (C) e o Setup.exe, que leva o pacote dentro (C):
      2P + 2C;
    - WindowsPackCommandRunner.cs:230-250: o .msi copia a pasta MAIS uma vez (P) e o
      WiX grava o .msi (C); MsiBuilder.cs:186-221: o WiX roda com a pasta temporaria
      do vpk, e os pedacos comprimidos que ele junta no .msi (C, deduzido do WiX,
      nao lido) ficam la ate o fim: mais P + 2C;
    - o comprimido C e contado igual a pasta P (o arquivo do motor ja e comprimido e
      nao encolhe; o resto encolhe para uns 53%, estudo do Kraken): a conta nunca
      fica curta por compressao;
    - entao: sem .msi, 4 vezes a pasta; com o .msi, 7 vezes (P com o motor). As
      saidas rodam uma depois da outra e o vpk apaga a temporaria no fim de cada
      uma; entre elas fica o pacote da primeira (ate 1 vez a pasta).
    A saida INSTALADOR leva tambem o arquivo do motor (tamanho_do_motor).
    baixado_para_o_rascunho: o que o publicar baixa para o rascunho antes do vpk e que fica la ate o fim (o arquivo do
    motor publicado, para o instalador; volta 3, achado 7 do relatorio 2: ficava fora da conta). Zero de fabrica: a
    conta so do vpk continua a mesma.
    Arriscado: diminuir os fatores sem medir (o C: enche); o .msi nunca foi medido."""
    total = baixado_para_o_rascunho
    for i, saida in enumerate(saidas):
        pasta = tamanho_da_pasta_do_programa + (tamanho_do_motor if saida.motor_em_instalar else 0)
        total += pasta * (7 if saida.com_msi else 4) if i == len(saidas) - 1 else pasta
    return total + MARGEM_DA_CONTA


def conferir_espaco(pasta: Path, precisa: int, reserva: int | None = None) -> str | None:
    """None se o disco da pasta aguenta 'precisa' bytes e ainda fica com a reserva (de fabrica, RESERVA_DO_DISCO,
    lida na hora); senao a frase (em GB)."""
    reserva = reserva or RESERVA_DO_DISCO
    try:
        livre = espaco_livre(pasta)
    except OSError as erro:
        return f"não consegui ler o espaço livre do disco de {pasta} ({erro})"
    if livre - precisa < reserva:
        return (f"o disco de {Path(pasta).anchor or pasta} tem {livre / GB:.1f} GB livres; este trabalho usa uns "
                f"{precisa / GB:.1f} GB e o disco tem de ficar com pelo menos {reserva / GB:.0f} GB livres. "
                f"Libere uns {(reserva + precisa - livre) / GB:.1f} GB e rode de novo")
    return None


def vigia_do_espaco(pasta: Path, reserva: int | None = None, livre=None):
    """A vigia do espaco (D-776: "ele vigia o espaco durante o trabalho e para com aviso se cair perto da reserva"): o
    LUGAR UNICO da regra. Devolve uma funcao que, a cada chamada, le o espaco livre do disco da pasta (do Windows, na
    hora) e devolve None (pode continuar) ou o motivo de parar, em portugues: abaixo da reserva, ou nao deu para ler
    (na duvida, para). Quem usa: rodar_vpk (durante o vpk), zipar_motor (durante a compressao do motor), a copia
    conferida (copiar_inteiro) e o publicar (durante o download do motor para o rascunho, achado 7 do relatorio 2, e o
    download para somar quando o GitHub nao da a soma pronta, achado 7 do relatorio 3). 'livre' e trocavel so nos
    testes."""
    livre = livre or espaco_livre
    reserva = reserva or RESERVA_DO_DISCO

    def olhar() -> str | None:
        """None = pode continuar; senao o motivo de parar."""
        try:
            sobra = livre(pasta)
        except OSError as erro:
            return f"não consegui ler o espaço livre durante o trabalho ({erro})"
        if sobra < reserva:
            return (f"o disco do rascunho ficou com {sobra / GB:.1f} GB livres, abaixo da reserva de "
                    f"{reserva / GB:.0f} GB (outro programa pode estar usando o disco)")
        return None

    return olhar


# O pedaco da copia conferida (copiar_inteiro): a vigia olha a cada tantos bytes.
PEDACO_DA_COPIA = 8 * 1024 * 1024
VIGIA_A_CADA = 64 * 1024 * 1024


def copiar_inteiro(origem: Path, alvo: Path, vigia=None) -> None:
    """Copia um arquivo sem nunca deixar um pedaco com o nome certo (o LUGAR UNICO da copia conferida: o envio e a
    leitura de volta do DestinoPasta, o motor baixado para o rascunho, o .msi para a pasta de saida).

    Copia para <alvo>.copiando; pede ao Windows para gravar a copia no disco (core/windows.gravar_no_disco, o lugar
    unico; volta 4, achado 11 do relatorio 3: antes, "lida de volta do disco" sem pedir isso); CONFERE a copia lendo-a
    de volta (o tamanho e a soma SHA-256 iguais aos da origem; a leitura vem do que o Windows guarda na memoria, o que
    a gravacao garante e que o conteudo ja foi mandado ao disco quando o nome certo aparece); so entao da o nome
    certo, de uma vez (os.replace). 'vigia' (vigia_do_espaco): olhada no comeco e a
    cada VIGIA_A_CADA bytes; se mandar parar, a copia para. Qualquer falha (disco cheio, a vigia, a copia diferente, Ctrl+C): apaga o
    provisorio e CONFERE que sumiu; levanta OSError com o que houve e o que ficou (ou repassa o Ctrl+C). Volta 3 do
    passo 2, achado 2 do relatorio 2: o shutil.copyfile nao apaga o destino quando falha no meio, e um .msi pela metade
    ficava na pasta de saida com o nome certo.
    Arriscado: copiar direto no nome certo; tirar a conferencia lida de volta."""
    import hashlib
    import os

    from core import windows

    origem, alvo = Path(origem), Path(alvo)
    provisorio = alvo.with_name(alvo.name + ".copiando")
    comecou = []                                      # vira [True] quando o provisorio e aberto (criado)

    def limpar() -> str:
        """Apaga o provisorio e diz o que ficou (conferido; "nada foi copiado" se ele nem chegou a nascer)."""
        if not comecou:
            return "nada foi copiado"
        try:
            provisorio.unlink(missing_ok=True)
        except OSError:
            pass
        if provisorio.exists():
            return f"ATENÇÃO: ficou o pedaço {provisorio}; apague à mão"
        return f"o pedaço {provisorio.name} foi apagado (conferido)"

    motivo = vigia() if vigia is not None else None
    if motivo:
        raise OSError(f"não comecei a copiar {origem.name}: {motivo}; nada foi copiado")
    try:
        soma, copiados, desde_a_vigia = hashlib.sha256(), 0, 0
        with open(origem, "rb") as de, open(provisorio, "wb") as para:
            comecou.append(True)
            while pedaco := de.read(PEDACO_DA_COPIA):
                para.write(pedaco)
                soma.update(pedaco)
                copiados += len(pedaco)
                desde_a_vigia += len(pedaco)
                if vigia is not None and desde_a_vigia >= VIGIA_A_CADA:
                    desde_a_vigia = 0
                    motivo = vigia()
                    if motivo:
                        raise OSError(f"parei de copiar {origem.name}: {motivo}")
            windows.gravar_no_disco(para)
        lido = hashlib.sha256()
        with open(provisorio, "rb") as copia:
            while pedaco := copia.read(PEDACO_DA_COPIA):
                lido.update(pedaco)
        if provisorio.stat().st_size != copiados or lido.hexdigest() != soma.hexdigest():
            raise OSError(f"a cópia de {origem.name} saiu diferente do original (tamanho ou soma)")
        os.replace(provisorio, alvo)
    except OSError as erro:
        raise OSError(f"{erro}; {limpar()}") from erro
    except BaseException:
        limpar()
        raise


def rodar_vpk(comando: list, rascunho: Path, reserva: int | None = None,
              intervalo_s: float = INTERVALO_DA_VIGIA_S, livre=None) -> str | None:
    """A UNICA funcao que roda o vpk (plano-v3, peca 8). None = terminou bem; senao o motivo, em portugues.

    - o vpk roda pelo laco unico da peca do Windows (core/windows.rodar_em_grupo,
      o mesmo do gh do publicar; volta 4, achado 8 do relatorio 3), num grupo do
      Windows: fechar o vpk fecha tambem o que ele abriu. Lido no vpk 1.2.161: o .msi
      sai de outro programa, "cmd.exe /S /C wix.exe build ..." (MsiBuilder.cs:216,
      Exe.cs:46); antes (achado 2 de quem tentou quebrar), fechar so o vpk deixava
      o WiX gravando no C: abaixo da reserva;
    - a pasta temporaria do vpk (VELOPACK_TEMP, TEMP e TMP: o vpk 1.2.161 le nessa
      ordem, src/lib-csharp/Util/TempUtil.cs) fica em <rascunho>\\temp, no mesmo
      disco do rascunho (o C:, D-776) e e apagada junto com ele;
    - a vigia (D-776): a cada 'intervalo_s', le o espaco livre do disco do
      rascunho; se cair abaixo da reserva, o laco fecha o grupo inteiro, CONFERE que
      nada ficou vivo, e a frase diz o motivo e se algo ficou. Quem chamou apaga o rascunho;
    - Ctrl+C: o laco fecha o grupo inteiro e repassa a interrupcao.
    A saida do vpk aparece no terminal de quem publica (nao e guardada).
    'livre' e trocavel so nos testes (para simular o disco enchendo).
    Arriscado: rodar o vpk por outro caminho (era o defeito 56 do plano: dois
    caminhos, a pasta temporaria desviada a mao); fechar so o vpk (o achado 2)."""
    import os

    from core import windows

    vigia = vigia_do_espaco(rascunho, reserva, livre)
    temp = Path(rascunho) / "temp"
    temp.mkdir(parents=True, exist_ok=True)
    ambiente = {**os.environ, "VELOPACK_TEMP": str(temp), "TEMP": str(temp), "TMP": str(temp)}
    r = windows.rodar_em_grupo(comando, pasta=rascunho, ambiente=ambiente, vigia=vigia, intervalo_s=intervalo_s)
    if r.deu_certo:
        return None
    if not r.dados.get("abriu"):
        return f"não consegui abrir o vpk ({r.motivo})"
    if r.dados.get("parou"):
        if r.dados.get("fechado"):
            return f"parei: {r.dados['parou']}; o vpk e os programas que ele abriu foram fechados (conferido)"
        return f"parei: {r.dados['parou']}; ATENÇÃO: {r.dados.get('fechou')} (veja no Gerenciador de Tarefas)"
    return f"o vpk parou com erro (código {r.dados.get('codigo')}); as mensagens dele estão acima"


# ---- o que o pacote tem de ter, e o que nao pode ter -----------------------

def nupkg_inteiro(saida: Path, versao_do_pacote: str) -> Path:
    """O pacote inteiro que o vpk gera: <saida>\\<versao.ID_DO_PACOTE>-<versao>-full.nupkg."""
    import versao

    return Path(saida) / f"{versao.ID_DO_PACOTE}-{versao_do_pacote}-full.nupkg"


def esperados_no_pacote_do_velopack(pecas: PecasDosDetectores | None, saida: Saida = ATUALIZACAO) -> list[str]:
    """Os caminhos (relativos a pasta do programa, com /) que TEM de estar no
    pacote do Velopack: o .exe, cada modelo, cada DLL, o Tesseract e os idiomas
    (relativos_do_tesseract), o Visual C++ e o arquivo da versao dele; o
    motor-exigido.json e o arquivo do motor em instalar\\ quando a saida pede
    (SAIDAS). O motor solto so na saida que o leva (nenhuma das do Velopack).

    Passo 2, volta 7 (achado 3 do relatorio 6, D-818): o Tesseract e cobrado
    sempre (antes, so quando havia pecas: com a pasta ja montada ele nem era
    procurado) e o arquivo da versao do Visual C++ tambem (o programa instalado
    o le para decidir se instala). 'pecas' nao e mais usado; fica na assinatura
    porque quem chama o passa pela posicao (tests/test_decisoes_atualizacao.py)."""
    import atualizacao
    import versao
    from core import ocr_kraken

    saida_ = [f"{NOME}.exe"]
    saida_ += [f"{INTERNO}/{destino}/{origem.name}" for origem, destino in modelos_do_programa()]
    saida_ += [f"{INTERNO}/{destino}/{origem.name}" for origem, destino in nativos_do_programa()]
    saida_ += relativos_do_tesseract()
    # o Visual C++ (D-727) e a versao dele nas saidas que o levam (Saida.vc_em_instalar: as duas do Velopack)
    if saida.vc_em_instalar:
        saida_ += [f"{atualizacao.PASTA_DO_QUE_SE_INSTALA}/{atualizacao.VC_REDIST_NOME}",
                   f"{atualizacao.PASTA_DO_QUE_SE_INSTALA}/{atualizacao.VC_REDIST_VERSAO}"]
    if saida.motor_solto:
        saida_ += [f"{PASTA_DO_MOTOR}/{a.replace(chr(92), '/')}" for a in AMOSTRA_DO_MOTOR]
    if saida.motor_exigido:
        saida_ += [NOME_DO_MOTOR_EXIGIDO]
    if saida.motor_em_instalar:
        saida_ += [f"{atualizacao.PASTA_DO_QUE_SE_INSTALA}/{versao.arquivo_do_motor(ocr_kraken.VERSAO_DO_MOTOR)}"]
    return saida_


def proibidos_no_pacote_do_velopack(saida: Saida = ATUALIZACAO) -> list[str]:
    """Os comecos de caminho (relativos a pasta do programa, com /) que NAO podem
    estar no pacote, lidos de SAIDAS: o motor solto, na saida que nao o leva
    (D-768); o arquivo do motor em instalar\\, na saida que nao o leva (a
    atualizacao; achado 8 de quem tentou quebrar: so preparar_saida o tirava)."""
    import atualizacao
    import versao

    proibidos = [] if saida.motor_solto else [f"{PASTA_DO_MOTOR}/"]
    if not saida.motor_em_instalar:
        proibidos.append(f"{atualizacao.PASTA_DO_QUE_SE_INSTALA}/{versao.PREFIXO_DO_MOTOR}")
    return proibidos


def conferir_pacote_do_velopack(nupkg: Path, pecas: PecasDosDetectores | None,
                                saida: Saida = ATUALIZACAO) -> list[str]:
    """Abre o .nupkg (um zip) e confere que cada peca esperada esta la dentro e
    que nada proibido esta. Devolve o que falta ou sobra (vazio = tudo certo)."""
    import zipfile

    try:
        with zipfile.ZipFile(nupkg) as pacote:
            nomes = {n.replace("\\", "/").lower() for n in pacote.namelist()}
    except (OSError, zipfile.BadZipFile) as erro:
        return [f"não consegui abrir {nupkg}: {erro}"]
    faltando = [relativo for relativo in esperados_no_pacote_do_velopack(pecas, saida)
                if (PASTA_NO_NUPKG + relativo).lower() not in nomes]
    for comeco in proibidos_no_pacote_do_velopack(saida):
        if any(n.startswith((PASTA_NO_NUPKG + comeco).lower()) for n in nomes):
            faltando.append(f"{comeco} (não pode ir nesta saída: {saida.nome})")
    return faltando


def construir_pacote_do_velopack(saida_do_vpk: Path, versao_do_pacote: str, saida: Saida = ATUALIZACAO,
                                 pasta: Path | None = None, motor: MotorPublicado | None = None,
                                 arquivo_do_motor: Path | None = None, rascunho: Path | None = None,
                                 vpk: Path | None = None, pecas: PecasDosDetectores | None = None) -> Path | None:
    """Monta o pacote do Velopack de uma saida (ATUALIZACAO ou INSTALADOR): a pasta
    (construir_pasta, com todas as travas; ou a 'pasta' ja pronta), a
    conferencia da pasta (conferir_pasta_pronta, a mesma de todo caminho: o
    Visual C++ pela assinatura e a versao dele, o Tesseract, a ficha desta
    versao, nada de motor solto; voltas 6 e 7 do passo 2) ANTES de mexer nela,
    preparar_saida, rodar_vpk (a funcao unica), apaga o Setup.exe na hora (D-795) e confere o
    pacote. Devolve o .nupkg inteiro, ou None (o motivo foi impresso).

    saida_do_vpk: a pasta de saida do vpk (tem de ser nova: o vpk pergunta se ja
    houver versao la). rascunho: onde fica a pasta temporaria do vpk (o rascunho
    do publicar, no C:); sem ele, a pasta acima de saida_do_vpk. pecas: as pecas
    conferidas quando a pasta foi montada por construir_pasta (para conferir o
    Tesseract no pacote); com uma pasta pronta de outro jeito, None."""
    print(f"\n=== Pacote do Velopack ({saida.nome}, versão {versao_do_pacote}) ===")
    vpk = vpk or achar_vpk()
    if vpk is None:
        print(f"  PAREI: não achei o vpk. Instale com: {COMO_INSTALAR_O_VPK}")
        return None
    if pasta is None:
        pasta = construir_pasta(ATUALIZACAO)
        if pasta is None or _PECAS is None:
            return None
        pecas = _PECAS
    # a mesma conferencia de toda pasta, antes do vpk, em todo caminho que chega aqui (passo 2, volta 6: o publicar a
    # chamava, mas quem chamasse esta funcao direto, com uma pasta de fora, chegava ao vpk sem ela), e ANTES de mexer
    # na pasta (volta 7, achado 4 do relatorio 6: preparar_saida gravava o motor-exigido.json e apagava o zip do motor
    # de uma pasta que depois era recusada). Ela nao depende de nada que preparar_saida faz.
    problemas = conferir_pasta_pronta(pasta, versao_do_pacote, saida)
    problemas = problemas or preparar_saida(pasta, saida, pecas, motor, arquivo_do_motor)
    if problemas:
        print("  PAREI: " + "; ".join(problemas))
        return None
    Path(saida_do_vpk).mkdir(parents=True, exist_ok=True)
    motivo = rodar_vpk(comando_do_vpk(vpk, pasta, saida_do_vpk, versao_do_pacote, com_msi=saida.com_msi),
                       Path(rascunho or Path(saida_do_vpk).parent))
    (Path(saida_do_vpk) / nome_do_setup()).unlink(missing_ok=True)       # D-795: nunca vai a lugar nenhum
    nupkg = nupkg_inteiro(saida_do_vpk, versao_do_pacote)
    if motivo is not None or not nupkg.is_file():
        print(f"  PAREI: {motivo or 'o vpk pack não deixou o pacote'}")
        return None
    if saida.com_msi and not (Path(saida_do_vpk) / nome_do_msi()).is_file():
        print(f"  PAREI: o vpk pack não deixou o {nome_do_msi()}")
        return None
    faltando = conferir_pacote_do_velopack(nupkg, pecas, saida)
    if faltando:
        print("  PAREI: o pacote do Velopack saiu errado:")
        for relativo in faltando:
            print(f"    {relativo}")
        return None
    print(f"  pronto: {nupkg}  ({_tamanho(nupkg)}); {len(esperados_no_pacote_do_velopack(pecas, saida))} peças "
          "conferidas")
    return nupkg


# ---- a ficha da versao (plano v1, peca 8: "um numero de versao so") --------

def gravar_ficha_da_versao(pasta: Path, saida: Saida) -> Path:
    """Escreve <pasta>\\versao-do-pacote.json: a versao (versao.VERSAO), a saida e de
    que commit a pasta saiu (pela peca do git, regras_dos_agentes.conversa_com_o_git;
    se o git nao responder, diz isso, nunca inventa). O publicar recusa uma pasta
    pronta cuja ficha seja de outra versao ou de outra saida (o defeito da etapa 5:
    "versao 1.1.0" numa 1.1.5)."""
    import datetime
    import json

    import versao

    commit, sem_commit = "não deu para ler (o git não respondeu)", None
    try:
        from regras_dos_agentes import conversa_com_o_git as git

        commit = git.commit_completo(RAIZ, "HEAD")
        sem_commit = len(git.mudancas_sem_commit(RAIZ))
    except Exception as erro:  # noqa: BLE001 - so anota; a ficha diz que nao leu
        commit = f"não deu para ler ({erro})"
    destino = Path(pasta) / NOME_DA_FICHA_DA_VERSAO
    destino.write_text(json.dumps({"versao": versao.VERSAO, "saida": saida.nome, "commit": commit,
                                   "arquivos_mudados_sem_commit": sem_commit,
                                   "montada_em": datetime.datetime.now().isoformat(timespec="seconds")},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
    return destino


def conferir_pasta_pronta(pasta: Path, versao_do_pacote: str, saida: Saida = ATUALIZACAO) -> list[str]:
    """O que impede uma pasta ja montada de ir para o vpk nesta saida (vazio = pode).

    A FUNCAO UNICA de "a pasta esta pronta para o vpk" (passo 2, volta 6): o
    publicar a chama cedo (antes da conta do espaco), para a pasta montada do zero
    e para a pasta pronta, e construir_pacote_do_velopack a chama de novo logo
    antes de rodar o vpk (todo caminho ate o vpk passa por ela). A pasta montada
    por construir_pasta(ATUALIZACAO) sai no estado que ela cobra.

    Cobra: o .exe; a ficha da versao, da MESMA versao e montada para uma saida
    sem o motor solto (o motor nao pode ir na atualizacao); o Visual C++ em
    instalar\\ (D-727), nas saidas que o levam (Saida.vc_em_instalar: as duas do
    Velopack), conferido pela assinatura da Microsoft (conferir_o_visual_c, a
    mesma regua da montagem), com o arquivo da versao dele igual a versao lida da
    assinatura (o arquivo lido por atualizacao.versao_do_visual_c_do_pacote, a
    leitura unica, a mesma do programa instalado; volta 8); o Tesseract inteiro (relativos_do_tesseract, cada arquivo nao
    vazio); e que a pasta motor-kraken\\ nao esteja la (D-768).

    Passo 2, volta 7 (D-818, Samuel: "vai ter que reprogramar?" · "A"; achado 1
    do relatorio 6): antes, do Visual C++ so se olhava o nome do arquivo, e a
    versao dele e o Tesseract nem eram procurados; uma pasta ja montada a mao
    passava. A montada do zero continua passando (ela traz tudo isso). O
    Tesseract nao e comparado com o original aqui (a pasta ja montada nao tem
    origem); a montagem o compara na hora de copiar (conferir_pecas_no_pacote).
    Arriscado: afrouxar qualquer uma (a pasta pronta vem de fora: so isto a
    confere antes do vpk); ler a assinatura por outra conta."""
    import json

    import atualizacao

    pasta = Path(pasta)
    if not (pasta / f"{NOME}.exe").is_file():
        return [f"{pasta} não é uma pasta do programa (falta {NOME}.exe)"]
    problemas = []
    try:
        ficha = json.loads((pasta / NOME_DA_FICHA_DA_VERSAO).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        ficha = None
    if not isinstance(ficha, dict):
        problemas.append(f"a pasta {pasta} não tem a ficha da versão ({NOME_DA_FICHA_DA_VERSAO}): monte de novo")
    else:
        if ficha.get("versao") != versao_do_pacote:
            problemas.append(f"a pasta {pasta} é da versão {ficha.get('versao')}, e a versão a publicar é a "
                             f"{versao_do_pacote}")
        if ficha.get("saida") == PORTATIL.nome:
            problemas.append(f"a pasta {pasta} foi montada como {PORTATIL.nome} (com o motor solto)")
    instalar = pasta / atualizacao.PASTA_DO_QUE_SE_INSTALA
    visual_c = instalar / atualizacao.VC_REDIST_NOME
    if saida.vc_em_instalar and not visual_c.is_file():
        problemas.append(f"a pasta {pasta} não tem o Visual C++ em {atualizacao.PASTA_DO_QUE_SE_INSTALA}\\")
    elif saida.vc_em_instalar:
        # a regua da montagem (D-818): a assinatura da Microsoft e a versao, lida dela, igual ao arquivo da versao
        versao_do_vc, errado = conferir_o_visual_c(visual_c)
        # o arquivo da versao, pela leitura unica (a mesma do programa instalado; volta 8, achado 6 do relatorio 7)
        lida = None if errado else atualizacao.versao_do_visual_c_do_pacote(pasta)
        if errado:
            problemas.append(f"o Visual C++ da pasta {pasta} ({atualizacao.PASTA_DO_QUE_SE_INSTALA}\\"
                             f"{atualizacao.VC_REDIST_NOME}) não é o oficial da Microsoft: " + "; ".join(errado))
        elif lida is None:
            problemas.append(f"a pasta {pasta} não tem a versão do Visual C++ ({atualizacao.PASTA_DO_QUE_SE_INSTALA}\\"
                             f"{atualizacao.VC_REDIST_VERSAO})")
        else:
            if lida != versao_do_vc:
                problemas.append(f"a pasta {pasta} diz que o Visual C++ é o {lida} "
                                 f"({atualizacao.VC_REDIST_VERSAO}), e o arquivo dele é o {versao_do_vc} (pela "
                                 "assinatura)")
    faltam = [r for r in relativos_do_tesseract() if not ((pasta / r).is_file() and (pasta / r).stat().st_size > 0)]
    if faltam:
        mais = f" e mais {len(faltam) - 5}" if len(faltam) > 5 else ""
        problemas.append(f"a pasta {pasta} não tem o Tesseract inteiro: falta {', '.join(faltam[:5])}{mais}")
    if not saida.motor_solto and (pasta / PASTA_DO_MOTOR).exists():
        problemas.append(f"a pasta {pasta} tem o motor do Kraken solto ({PASTA_DO_MOTOR}\\), e a {saida.nome} "
                         "não leva")
    return problemas


# ---- o arquivo do motor (a publicacao propria do motor, D-768, D-788) ------

def zipar_motor(pasta_do_motor: Path, destino: Path, reserva: int | None = None,
                livre=None) -> str | None:
    """Comprime a pasta do motor num arquivo so (o que vai a publicacao do motor e,
    no instalador, a instalar\\). None = pronto e conferido; senao o motivo.

    Grava num nome provisorio, pede ao Windows para grava-lo no disco (core/windows.gravar_no_disco,
    o lugar unico; volta 4, achado 11 do relatorio 3) e so da o nome final depois de conferir que cada
    arquivo da ficha do motor esta no zip com o tamanho certo (problemas_do_zip_do_motor).
    Vigia o espaco do disco do destino a cada 500 arquivos (D-776, pela vigia unica,
    vigia_do_espaco); para abaixo da reserva e apaga o provisorio. 'livre' e trocavel so nos testes."""
    import zipfile

    from core import windows

    pasta_do_motor, destino = Path(pasta_do_motor), Path(destino)
    vigia = vigia_do_espaco(destino.parent, reserva, livre)
    provisorio = destino.with_name(destino.name + ".fazendo")
    provisorio.unlink(missing_ok=True)
    arquivos = sorted(f for f in pasta_do_motor.rglob("*") if f.is_file())
    try:
        with open(provisorio, "wb") as aberto:
            with zipfile.ZipFile(aberto, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
                for i, arquivo in enumerate(arquivos):
                    motivo = vigia() if i % 500 == 0 else None
                    if motivo:
                        raise OSError(motivo)
                    z.write(arquivo, arquivo.relative_to(pasta_do_motor).as_posix())
            windows.gravar_no_disco(aberto)
    except (OSError, zipfile.BadZipFile) as erro:
        provisorio.unlink(missing_ok=True)
        return f"parei de comprimir o motor: {erro}"
    problemas = problemas_do_zip_do_motor(provisorio)
    if problemas:
        provisorio.unlink(missing_ok=True)
        return "o arquivo do motor saiu errado: " + "; ".join(problemas)
    import os

    os.replace(provisorio, destino)
    return None


def problemas_do_zip_do_motor(arquivo: Path) -> list[str]:
    """O zip do motor tem a ficha (motor.json) da versao pedida e cada arquivo dela, com o tamanho dela? (Vazio =
    sim.) A ficha e lida de dentro do zip, e a regra e a mesma da pasta (core/ocr_kraken.conferir_ficha), aplicada
    as entradas do zip."""
    import json
    import zipfile

    from core import ocr_kraken

    try:
        with zipfile.ZipFile(arquivo) as z:
            tamanhos = {i.filename: i.file_size for i in z.infolist()}
            ficha = json.loads(z.read(ocr_kraken.NOME_DA_FICHA).decode("utf-8"))
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as erro:
        return [f"não consegui ler a ficha do motor dentro de {arquivo} ({erro})"]
    if not isinstance(ficha, dict):
        return [f"a ficha do motor dentro de {arquivo} está estragada"]
    return ocr_kraken.conferir_ficha(ficha, tamanhos.get, f"o motor dentro de {Path(arquivo).name}")


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
