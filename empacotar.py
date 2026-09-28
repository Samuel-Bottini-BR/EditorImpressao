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

Arriscado mudar: o destino de cada modelo (tem de ser o caminho relativo que
o codigo procura, ver modelos_do_programa) e o --contents-directory _internal
(o instalador.iss e as conferencias contam com esse nome).
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
OCULTOS = ["doxapy", "skimage.filters", "PIL._tkinter_finder"]

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
      (modelos/mobile_sam/*.onnx, 45 MB).

    O destino e o caminho da pasta do modelo relativo a raiz do codigo (a
    pasta acima de core/). Empacotado, a raiz do codigo e _internal\\ (na
    pasta) ou o _MEIxxxx (no arquivo único), e o codigo procura o modelo
    exatamente em <raiz do codigo>/modelos/...: por isso o destino e esse
    caminho relativo, e nao outro.

    Importa core/ so aqui dentro, e nao no alto do arquivo: o
    empacotar_teste_velocidade.py importa este modulo so pelas listas
    EXCLUIR e OCULTOS.
    """
    from core import detectar_regioes, rede_selecao

    raiz_do_codigo = Path(detectar_regioes.__file__).resolve().parent.parent
    usados = (detectar_regioes.CAMINHO_MODELO,
              rede_selecao.CODIFICADOR, rede_selecao.DECODIFICADOR)
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


def modelos_faltando_no_registro_do_inno(registro: str) -> list[str]:
    """Os modelos que o Inno Setup NAO comprimiu para dentro do instalador.

    O ISCC escreve uma linha "Compressing: <caminho completo>" para cada
    arquivo que entra no Setup.exe. Esta e a prova de que o modelo esta la
    dentro, e nao so na pasta dist\\. Devolve os caminhos relativos
    ('_internal\\modelos\\doclayout.onnx') que faltam.
    """
    comprimidos = [linha.strip().lower().replace("/", "\\")
                   for linha in registro.splitlines() if "Compressing:" in linha]
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


def construir_pasta() -> Path | None:
    """Versao portatil em pasta. E tambem o que o instalador empacota.

    Para (devolve None) se faltar modelo ANTES de apagar a pasta anterior, e
    de novo se algum modelo nao chegar inteiro em _internal\\ (ver
    conferir_modelos_no_pacote).
    """
    print("\n=== Versao em pasta (portatil, abre na hora) ===")
    if not _avisar_modelos_faltando():
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
    print("  modelos dentro do instalador (registro do Inno Setup):")
    for origem, destino_no_pacote in modelos_do_programa():
        print(f"    {_caminho_no_instalador(origem, destino_no_pacote)}")

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
    argumentos = analisador.parse_args(argumentos_da_linha)

    # Antes de apagar qualquer coisa (o modo entrega apaga, logo abaixo, o que
    # este script gerou antes): sem os modelos, nada do que sairia daqui presta.
    if not _avisar_modelos_faltando():
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
