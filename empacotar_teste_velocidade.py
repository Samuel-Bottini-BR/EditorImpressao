"""Empacota o teste de velocidade para o notebook do Kaique (item 0.6 do plano).

O notebook do Kaique (Samsung Galaxy Book2: i5-1235U, 32 GB, vídeo integrado)
não tem Python nem nada de desenvolvimento. Este script gera, com o
PyInstaller, uma pasta que roda sozinha lá, e um .zip dela para o pendrive.
Um comando só, da pasta do projeto::

    .venv\\Scripts\\python.exe empacotar_teste_velocidade.py

Sai em dist\\ (fora do git)::

    dist\\TesteVelocidade\\                        a pasta que roda
        RODAR O TESTE.bat                        o que o Kaique abre
        TesteVelocidade.exe                      o teste (janela preta)
        COMO RODAR NO NOTEBOOK DO KAIQUE.txt     o passo a passo
        marial_300.pdf                           o livro medido
        _internal\\                               o Python e as bibliotecas
    dist\\TesteVelocidade-notebook-do-Kaique.zip   o conteúdo da pasta acima
    dist\\COMO RODAR NO NOTEBOOK DO KAIQUE.txt     o passo a passo, fora do .zip
                                                 (para ler antes de extrair)

O .zip leva o CONTEÚDO da pasta, sem a pasta em volta: o "Extrair tudo" do
Windows já cria uma pasta com o nome do .zip, e assim o Kaique abre uma pasta
só, e não uma pasta dentro da outra.

Decisões que não são gosto:

- Pasta (onedir), nunca arquivo único (onefile): o arquivo único se
  desempacota inteiro a cada abertura, e esse tempo entraria na medição. E o
  "Aperte Enter para fechar" do teste depende de ser um processo só (ver
  teste_velocidade._sozinho_no_console).
- Com janela preta (console): é ali que o progresso aparece.
- O modelo do detector de gravura e letra (modelos\\doclayout.onnx, 75 MB,
  fora do git) vai para _internal\\modelos\\, que é onde
  core/detectar_regioes.py o procura empacotado: CAMINHO_MODELO é a pasta
  acima de core\\ mais modelos\\, e empacotado core\\ mora em _internal\\.
  Sem o modelo o teste mede um programa mais rápido que o de verdade: por
  isso o script PARA se ele faltar.
- As bibliotecas do Visual C++ (vcruntime140.dll, vcruntime140_1.dll,
  msvcp140.dll e as outras que algum arquivo do pacote pedir) ficam dentro de
  _internal\\: o notebook pode não ter o "Visual C++ Redistributable"
  instalado. O PyInstaller já as traz; o script confere, arquivo por arquivo,
  e completa o que faltar.
- As mesmas exclusões e importações escondidas do programa de verdade
  (empacotar.py): o teste mede o programa como ele é entregue.
- Não usa o EditorImpressao.spec: ele é velho (aponta para a Área de Trabalho
  e tira o scipy, de que o programa precisa).
- Se dist\\TesteVelocidade\\ tiver uma pasta resultados\\ (um teste já rodou
  ali), o script para em vez de apagá-la junto.
- O RODAR O TESTE.bat se reabre, uma vez, na janela preta clássica do Windows
  (o conhost), e só então roda o teste: no Windows 11 os dois cliques podem
  abrir o Terminal novo, e o Samuel decidiu (25/09/2026) que toda medição é
  na clássica. O porquê de cada linha está no comentário de TEXTO_DO_BAT; o
  relatório diz em que janela o teste rodou (teste_velocidade.janela_do_teste).

Seguro mudar: os textos que o .bat e o .txt mostram, o nome do .zip. Arriscado
mudar: onedir e console (ver acima), o destino do modelo (--add-data
...;modelos), --contents-directory, o nome do .exe (o .bat e as instruções
chamam por ele) e as linhas do .bat que o reabrem na janela clássica (ver
TEXTO_DO_BAT).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

# As mesmas opções do programa de verdade (ver o cabeçalho).
from empacotar import EXCLUIR, OCULTOS
from teste_velocidade import NOME_DO_LIVRO

NOME = "TesteVelocidade"
RAIZ = Path(__file__).resolve().parent
DIST = RAIZ / "dist"
PASTA = DIST / NOME
TRABALHO = RAIZ / "build" / "teste_velocidade"
INTERNO = "_internal"  # --contents-directory: onde o PyInstaller põe o resto
MODELO = RAIZ / "modelos" / "doclayout.onnx"
LIVRO = RAIZ / "gabarito" / "velocidade" / NOME_DO_LIVRO
ZIP = DIST / "TesteVelocidade-notebook-do-Kaique.zip"
NOME_DO_BAT = "RODAR O TESTE.bat"
NOME_DAS_INSTRUCOES = "COMO RODAR NO NOTEBOOK DO KAIQUE.txt"

# As bibliotecas do Visual C++ 2015-2022. As três primeiras vão sempre; as
# outras, quando algum arquivo do pacote pedir por elas.
DLLS_DO_VISUAL_C = ("vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll")
PADRAO_DO_VISUAL_C = re.compile(
    r"^(vcruntime140(_1)?|msvcp140(_\w+)?|concrt140|vcomp140|vccorlib140|vcamp140)\.dll$",
    re.IGNORECASE)

# O caminho mais comprido que o notebook aguenta sem "Caminho muito longo" ao
# extrair: 259 letras, menos a pasta da Área de Trabalho com OneDrive e o nome
# da pasta extraída (C:\Users\<nome>\OneDrive\Área de Trabalho\
# TesteVelocidade-notebook-do-Kaique\ = uns 90). Só avisa: quem decide é quem
# lê o aviso.
CAMINHO_MAIS_LONGO_SEGURO = 160


class ErroNoPacote(Exception):
    """O pacote não pode sair assim. A mensagem já diz o que fazer."""


# ---------------------------------------------------------------------------
# os textos que vão junto
# ---------------------------------------------------------------------------

# O relançamento na janela clássica (ver TEXTO_DO_BAT). O .bat é montado com
# estes nomes, e os testes os leem daqui.
CONHOST = r"%SystemRoot%\System32\conhost.exe"   # a janela preta clássica
MARCA_DA_JANELA_CLASSICA = "--ja-na-janela-classica"  # "já fui reaberto nela"
VARIAVEL_DO_BAT = "TESTE_VELOCIDADE_BAT"          # o caminho deste .bat, com aspas
VARIAVEL_DAS_OPCOES = "TESTE_VELOCIDADE_OPCOES"   # o que veio depois do nome do .bat

# UTF-8 sem BOM (um BOM estragaria a primeira linha): o "chcp 65001" do
# começo é o que faz as linhas acentuadas saírem certas. Até ele, só texto sem
# acento (os comentários "rem" ficam sem acento em todo o arquivo).
#
# A MEDIÇÃO É SEMPRE NA JANELA PRETA CLÁSSICA (decisão do Samuel, 25/09/2026).
# No Windows 11, com o "aplicativo de terminal padrão" em "deixar o Windows
# decidir" e o Terminal do Windows instalado, dois cliques no .bat abrem o
# Terminal novo, e não a janela clássica (o conhost). Por isso o .bat, na
# primeira vez, se reabre pelo conhost.exe e sai: a janela em que ele abriu
# fecha, e fica só a clássica. Como e por quê:
#
# - O conhost.exe chamado com uma linha de comando abre sempre a janela
#   clássica: ele nunca a passa para o Terminal novo (no código aberto do
#   conhost, repositório microsoft/terminal, src/server/IoDispatchers.cpp, a
#   passagem para o Terminal só é tentada quando o conhost NÃO foi chamado com
#   uma linha de comando; conferido também na prática, ver abaixo). O "start"
#   solta o conhost e não espera por ele.
# - De dentro do .bat não dá para saber com segurança, sem chamar outro
#   programa, em que janela ele abriu. Então ele se reabre SEMPRE, uma vez;
#   se já estava na clássica, a troca só pisca a janela.
# - A marca (MARCA_DA_JANELA_CLASSICA, o primeiro argumento) diz ao .bat
#   reaberto que ele já está na clássica. Sem ela, cada janela abriria outra,
#   sem fim.
# - O caminho deste .bat (que pode ter espaço, acento, parênteses, &...) e as
#   opções vão em variáveis de ambiente, que a janela nova herda, e NUNCA na
#   linha do conhost: o conhost separa a linha que recebe em pedaços e refaz
#   as aspas de cada um do jeito dos programas em C (com barras), que o cmd
#   não entende. O que vai depois do conhost.exe não tem espaço, aspas nem
#   barra, e chega ao cmd como está. As aspas do caminho vão DENTRO da
#   variável: o "%%...%%" vira "%...%" nesta janela, e o cmd da janela nova só
#   abre a variável depois de olhar as aspas da linha.
# - As opções são guardadas só na primeira janela (depois da marca): no .bat
#   reaberto, %* é a marca, e ela não pode ir para o .exe.
# - Plano B: sem o conhost.exe, ou se o start falhar, mede na janela em que
#   estiver. O "|| goto medir" fica na MESMA linha do start, e nunca um "if
#   errorlevel" depois dele: o start que dá certo não zera o ERRORLEVEL (visto
#   no PC do Samuel, 25/09/2026), e o teste rodaria nas duas janelas ao mesmo
#   tempo.
# - Sem o .exe na pasta, o aviso de extrair o .zip sai logo, na janela que
#   abriu, sem reabrir: não há o que medir (aberto de dentro do .zip, sem
#   extrair, o Windows copia só o .bat para uma pasta temporária).
# - Nenhum bloco entre parênteses: um ")" no nome da pasta ("...-do-Kaique
#   (1)", quando o .zip é baixado duas vezes) fecharia o bloco no meio.
# - "exit /b 0" depois do start: a janela de onde o .bat saiu fecha (o
#   Terminal novo, na configuração de fábrica, fecha sozinho quando o programa
#   sai com 0), e o "/b" não fecha o terminal de quem chamou o .bat digitando.
# - O pause do fim não precisa esvaziar o teclado antes: ele mesmo descarta o
#   que foi digitado antes dele (visto no PC do Samuel, 26/09/2026, num
#   console sem janela). Quem precisava era o "Aperte Enter para fechar" do
#   .exe aberto direto (ver teste_velocidade.esvaziar_o_teclado).
#
# Conferido de verdade no PC do Samuel (25/09/2026: Windows 11 26200,
# Terminal 1.24, terminal padrão em "deixar o Windows decidir"), com um
# TesteVelocidade.exe falso, que não mede nada, numa pasta com espaço, acento
# e parênteses, aberta como nos dois cliques (ShellExecute, o caminho do
# Explorer): o Windows abriu o .bat no Terminal novo, que ficou uns 0,3 s na
# tela; nesse tempo o .bat se reabriu pelo conhost e saiu, o Terminal fechou
# sozinho e ficou só a janela clássica (ConsoleWindowClass), onde o .exe falso
# rodou e disse "classica" (teste_velocidade.janela_do_teste). Nessas rodadas
# a janela clássica pegou o foco e fechou sozinha 2 a 5 s depois: o Samuel
# estava usando o PC, e pelo jeito uma tecla dele respondeu ao pause. Numa
# rodada com a mesma linha do conhost e a janela minimizada, o pause a segurou
# aberta por mais de 10 s, até ela ser fechada. Os testes conferem cada item
# acima no texto, e rodam o .bat de verdade nos caminhos que não abrem janela.
#
# Seguro mudar: os textos das linhas "echo" e "title" (depois do chcp).
# Arriscado mudar: todo o resto - cada item acima tem o seu teste.
TEXTO_DO_BAT = f"""@echo off
setlocal
rem Teste de velocidade do Editor de Impressao (item 0.6 do plano).
rem Dois cliques aqui: roda o {NOME}.exe desta pasta, sempre na
rem janela preta classica do Windows, e no fim deixa a janela aberta ate
rem apertar uma tecla - mesmo que o programa caia no meio.
rem Opcoes escritas depois do nome passam direto para o .exe (ex.: --rapido).
rem Gerado por empacotar_teste_velocidade.py: mude la, nao aqui (o porque de
rem cada linha esta explicado la, em TEXTO_DO_BAT).
chcp 65001 >nul
title Teste de velocidade do Editor de Impressão
if not exist "%~dp0{NOME}.exe" goto sem_programa
rem Reaberto pelo conhost (a marca e o primeiro argumento): ja esta na
rem janela classica.
if "%~1"=="{MARCA_DA_JANELA_CLASSICA}" goto medir
rem Senao: guarda as opcoes, reabre este .bat na janela classica e sai. Sem o
rem conhost, ou se o start falhar, mede aqui mesmo.
set {VARIAVEL_DAS_OPCOES}=%*
if not exist "{CONHOST}" goto medir
set {VARIAVEL_DO_BAT}="%~f0"
start "" "{CONHOST}" cmd.exe /c %%{VARIAVEL_DO_BAT}%% {MARCA_DA_JANELA_CLASSICA} || goto medir
exit /b 0

:medir
cd /d "%~dp0"
"%~dp0{NOME}.exe" %{VARIAVEL_DAS_OPCOES}%
set CODIGO=%ERRORLEVEL%
echo.
pause
exit /b %CODIGO%

:sem_programa
echo Não achei o {NOME}.exe nesta pasta.
echo Extraia o .zip inteiro primeiro: botão direito no .zip, "Extrair tudo".
echo Se já extraiu, o antivírus pode ter apagado o programa: avise o Samuel.
echo.
pause
exit /b 1
"""

PASTA_EXTRAIDA = ZIP.stem  # o nome que o "Extrair tudo" do Windows dá

TEXTO_DAS_INSTRUCOES = f"""TESTE DE VELOCIDADE DO EDITOR DE IMPRESSÃO
Como rodar no notebook do Kaique

Este teste mede quanto o Editor de Impressão demora neste notebook para abrir
um livro de 300 páginas, trocar de página e processar 10 páginas. Ele roda
sozinho e não pergunta nada. Não instala nada, não precisa de internet e não
mexe no Editor de Impressão que já está no notebook. Depois, a pasta pode ser
apagada.


PREPARAR (uns 10 minutos)

1. Ligue o notebook na tomada. Ele fica na tomada até o fim do teste.

2. Copie o arquivo {ZIP.name} do pendrive para a
   Área de Trabalho do notebook.
   Não rode o teste direto do pendrive: o pendrive é lento, e o teste mediria
   o pendrive, e não o notebook.

3. Na Área de Trabalho, clique com o botão direito no arquivo .zip e escolha
   "Extrair tudo", depois "Extrair". Espere terminar (pode levar alguns
   minutos). Vai aparecer a pasta {PASTA_EXTRAIDA}.

4. Deixe o Windows em "Melhor desempenho": aperte a tecla do Windows junto
   com a tecla I (abre as Configurações) > Sistema > Energia e bateria >
   Modo de energia > Melhor desempenho.

5. Feche todos os outros programas (navegador, WhatsApp, Word, o próprio
   Editor de Impressão...). Depois desligue o Wi-Fi: clique no ícone de
   internet perto do relógio e desligue o Wi-Fi. O teste não precisa de
   internet, e assim o Windows não fica baixando coisas no meio da medição.


RODAR (de 20 a 40 minutos)

6. Abra a pasta {PASTA_EXTRAIDA} e dê dois cliques em
   RODAR O TESTE.
   Se aparecer um aviso azul "O Windows protegeu o computador", clique em
   "Mais informações" e depois em "Executar assim mesmo". O programa não tem
   assinatura digital, e esse aviso é esperado.
   Pode aparecer uma janela que pisca e fecha sozinha logo antes de abrir a
   janela preta do teste. Isso é normal: é só esperar.

7. Abre uma janela preta, que vai mostrando em que parte o teste está. No
   começo ela pode parecer parada por um ou dois minutos: é normal.
   O teste mede tudo 3 vezes. No PC do Samuel levou 14 minutos; o notebook
   deve ser mais lento, então conte com 20 a 40 minutos.
   Enquanto o teste roda:
   - não use o notebook;
   - não clique dentro da janela preta (isso pode pausar o teste);
   - não feche a tampa e não tire da tomada.

8. No fim aparece "Terminou. O resultado está na pasta resultados."
   Aperte qualquer tecla para fechar a janela.


TRAZER O RESULTADO

9. Dentro da pasta {PASTA_EXTRAIDA} apareceu a pasta
   "resultados". Copie a pasta "resultados" inteira para o pendrive e traga
   para o PC do Samuel.

10. Pronto. Pode ligar o Wi-Fi de novo e apagar da Área de Trabalho a pasta
    {PASTA_EXTRAIDA} e o arquivo .zip.


SE ALGO DER ERRADO

- Se a janela mostrar "O teste parou", tire uma foto da tela e traga a pasta
  "resultados" do mesmo jeito (o motivo fica anotado lá dentro).
- Se passar de 2 horas e a janela não mostrar "Terminou", tire uma foto da
  tela e avise o Samuel.
"""


# ---------------------------------------------------------------------------
# as etapas
# ---------------------------------------------------------------------------


def tamanho_mb(caminho: Path) -> float:
    """Tamanho em MB de um arquivo, ou de tudo dentro de uma pasta."""
    if caminho.is_file():
        return caminho.stat().st_size / 1024 / 1024
    return sum(f.stat().st_size for f in caminho.rglob("*") if f.is_file()) / 1024 / 1024


def conferir_o_que_vai_junto() -> None:
    """O modelo e o livro têm de existir ANTES de gastar minutos empacotando."""
    if not MODELO.is_file():
        raise ErroNoPacote(
            f"Falta o modelo do detector de gravura e letra: {MODELO}. Ele fica fora do "
            "git; sem ele o teste mediria um programa mais rápido que o de verdade.")
    if not LIVRO.is_file():
        raise ErroNoPacote(
            f"Falta o livro de teste: {LIVRO}. Grave-o com "
            r".venv\Scripts\python.exe teste_velocidade.py --preparar")


def limpar_o_anterior() -> None:
    """Apaga o pacote anterior - mas nunca um resultado de teste que alguém
    tenha deixado dentro dele."""
    resultados = PASTA / "resultados"
    if resultados.exists():
        raise ErroNoPacote(
            f"Há resultados de um teste em {resultados}. Tire essa pasta de lá (ou "
            "copie para relatorios\\velocidade\\) antes de empacotar de novo: "
            "empacotar apaga a pasta inteira.")
    shutil.rmtree(PASTA, ignore_errors=True)
    shutil.rmtree(TRABALHO, ignore_errors=True)
    ZIP.unlink(missing_ok=True)
    if PASTA.exists():
        raise ErroNoPacote(f"Não consegui apagar {PASTA}: algum arquivo dela está aberto?")


def comando_do_pyinstaller() -> list[str]:
    """O comando completo. Caminhos sempre absolutos: com --specpath, o
    PyInstaller lê os relativos a partir da pasta do .spec, não da raiz."""
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onedir",        # pasta, nunca arquivo único (ver o cabeçalho)
        "--console",       # a janela preta com o progresso
        "--noupx",         # nada de DLL comprimida: abre igual em qualquer máquina
        "--contents-directory", INTERNO,
        "--name", NOME,
        "--paths", str(RAIZ),
        "--distpath", str(DIST),
        "--workpath", str(TRABALHO),
        "--specpath", str(TRABALHO),
        "--log-level", "WARN",
        "--add-data", f"{MODELO}{os.pathsep}modelos",
    ]
    for modulo in EXCLUIR:
        comando += ["--exclude-module", modulo]
    for modulo in OCULTOS:
        comando += ["--hidden-import", modulo]
    comando.append(str(RAIZ / "teste_velocidade.py"))
    return comando


def rodar_o_pyinstaller() -> Path:
    """Gera dist\\TesteVelocidade\\ e devolve o caminho do .exe."""
    feito = subprocess.run(comando_do_pyinstaller(), cwd=RAIZ)
    exe = PASTA / f"{NOME}.exe"
    if feito.returncode != 0 or not exe.is_file():
        raise ErroNoPacote(f"O PyInstaller falhou (código {feito.returncode}); veja as "
                           "mensagens acima.")
    return exe


def conferir_o_modelo() -> Path:
    """O modelo tem de estar onde o código empacotado o procura, inteiro."""
    destino = PASTA / INTERNO / "modelos" / MODELO.name
    if not destino.is_file() or destino.stat().st_size != MODELO.stat().st_size:
        raise ErroNoPacote(f"O modelo não chegou inteiro em {destino}.")
    return destino


def _dlls_que_o_arquivo_pede(arquivo: Path) -> set[str]:
    """Os nomes das DLLs que um .exe/.dll/.pyd carrega (importação direta e
    atrasada), em minúsculas. Conjunto vazio se não der para ler."""
    import pefile  # vem junto com o PyInstaller

    try:
        pe = pefile.PE(str(arquivo), fast_load=True)
    except Exception:  # noqa: BLE001 - não é um executável do Windows
        return set()
    try:
        pe.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT"],
        ])
        entradas = (list(getattr(pe, "DIRECTORY_ENTRY_IMPORT", []))
                    + list(getattr(pe, "DIRECTORY_ENTRY_DELAY_IMPORT", [])))
        return {entrada.dll.decode("ascii", "replace").lower() for entrada in entradas}
    except Exception:  # noqa: BLE001
        return set()
    finally:
        pe.close()


def dlls_do_visual_c_pedidas(pasta: Path) -> dict[str, list[str]]:
    """{dll do Visual C++: arquivos do pacote que pedem por ela}. As três de
    DLLS_DO_VISUAL_C entram sempre, mesmo que ninguém peça."""
    pedidas: dict[str, list[str]] = {nome: [] for nome in DLLS_DO_VISUAL_C}
    for arquivo in pasta.rglob("*"):
        if arquivo.suffix.lower() not in (".dll", ".pyd", ".exe") or not arquivo.is_file():
            continue
        for nome in _dlls_que_o_arquivo_pede(arquivo):
            if PADRAO_DO_VISUAL_C.match(nome):
                pedidas.setdefault(nome, []).append(str(arquivo.relative_to(pasta)))
    return pedidas


def versao_do_arquivo(arquivo: Path) -> tuple[int, int, int, int]:
    """A versão gravada no .dll (14.50.35719.0 vira (14, 50, 35719, 0)), ou
    (0, 0, 0, 0) se não der para ler."""
    import pefile

    try:
        pe = pefile.PE(str(arquivo), fast_load=True)
    except Exception:  # noqa: BLE001
        return (0, 0, 0, 0)
    try:
        pe.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
        info = pe.VS_FIXEDFILEINFO[0]
        return (info.FileVersionMS >> 16, info.FileVersionMS & 0xFFFF,
                info.FileVersionLS >> 16, info.FileVersionLS & 0xFFFF)
    except Exception:  # noqa: BLE001
        return (0, 0, 0, 0)
    finally:
        pe.close()


def _onde_achar(nome: str, interno: Path) -> list[Path]:
    """As cópias que existem de uma DLL do Visual C++ que falte no topo de
    _internal - dentro do próprio pacote (a do PySide6, por exemplo), na pasta
    do Python e no Windows desta máquina - da versão mais nova para a mais
    velha.

    A mais nova porque a base da família (msvcp140.dll, vcruntime140.dll) que
    o PyInstaller põe no topo costuma ser a do Windows desta máquina, a mais
    nova: um complemento (msvcp140_1.dll) mais velho que a base funciona, mas
    a família inteira na mesma versão é o que o instalador da Microsoft faz.
    """
    lugares = sorted(interno.rglob(nome))
    lugares.append(Path(sys.base_prefix) / nome)
    lugares.append(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / nome)
    existentes = [lugar for lugar in lugares if lugar.is_file()]
    return sorted(existentes, key=versao_do_arquivo, reverse=True)


def completar_o_visual_c() -> dict[str, str]:
    """Garante no topo de _internal toda DLL do Visual C++ que o pacote pede.

    Por que no topo: é a pasta que o .exe põe na busca de DLL de todo o
    programa, e dali qualquer arquivo do pacote a acha, esteja na subpasta que
    estiver. Achado ao empacotar: o onnxruntime (o detector de gravura e letra)
    pede msvcp140_1.dll, e o PyInstaller só a trazia dentro da pasta do
    PySide6 - num notebook sem o Visual C++, o detector dependeria da ordem em
    que as bibliotecas são carregadas. Devolve {dll: situação}, para o resumo.
    """
    interno = PASTA / INTERNO
    situacao: dict[str, str] = {}
    for nome, quem_pede in sorted(dlls_do_visual_c_pedidas(PASTA).items()):
        pedida_por = f", pedida por {len(quem_pede)} arquivos" if quem_pede else ""
        destino = interno / nome
        if not destino.is_file():
            origens = _onde_achar(nome, interno)
            if not origens:
                raise ErroNoPacote(f"Falta {nome} no pacote e não achei uma cópia para pôr.")
            shutil.copy2(origens[0], destino)
            pedida_por += f"; COPIADA de {origens[0]}"
        versao = ".".join(str(parte) for parte in versao_do_arquivo(destino))
        situacao[nome] = f"versão {versao}{pedida_por}"
    return situacao


def copiar_o_livro() -> Path:
    """O livro vai ao lado do .exe, que é onde o teste empacotado procura.
    O original (em gabarito\\) só é lido."""
    destino = PASTA / NOME_DO_LIVRO
    shutil.copy2(LIVRO, destino)
    if destino.stat().st_size != LIVRO.stat().st_size:
        raise ErroNoPacote(f"O livro não chegou inteiro em {destino}.")
    return destino


def escrever_os_textos() -> tuple[Path, list[Path]]:
    """O .bat (UTF-8 sem BOM, ver TEXTO_DO_BAT) e as instruções (UTF-8 com
    BOM, que o Bloco de Notas de qualquer Windows lê com acento), os dois com
    fim de linha do Windows. As instruções vão dentro da pasta e ao lado do
    .zip. Devolve (o .bat, as instruções)."""
    bat = PASTA / NOME_DO_BAT
    bat.write_text(TEXTO_DO_BAT, encoding="utf-8", newline="\r\n")
    instrucoes = [PASTA / NOME_DAS_INSTRUCOES, DIST / NOME_DAS_INSTRUCOES]
    for destino in instrucoes:
        destino.write_text(TEXTO_DAS_INSTRUCOES, encoding="utf-8-sig", newline="\r\n")
    return bat, instrucoes


def caminho_mais_longo(pasta: Path) -> tuple[int, str]:
    """(quantas letras, qual) do caminho mais comprido dentro da pasta."""
    maior = max((str(f.relative_to(pasta)) for f in pasta.rglob("*")), key=len)
    return len(maior), maior


def compactar() -> int:
    """O conteúdo da pasta, sem a pasta em volta (ver o cabeçalho), num .zip.
    Grava num .parcial e só no fim troca o nome: interromper no meio não deixa
    um .zip pela metade com cara de pronto. Devolve quantos arquivos foram."""
    parcial = ZIP.with_name(ZIP.name + ".parcial")
    arquivos = sorted(f for f in PASTA.rglob("*") if f.is_file())
    with zipfile.ZipFile(parcial, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as pacote:
        for arquivo in arquivos:
            pacote.write(arquivo, arquivo.relative_to(PASTA).as_posix())
    os.replace(parcial, ZIP)
    with zipfile.ZipFile(ZIP) as pacote:
        if pacote.testzip() is not None or len(pacote.namelist()) != len(arquivos):
            raise ErroNoPacote(f"O .zip saiu estragado: {ZIP}.")
    return len(arquivos)


def main() -> int:
    """Faz tudo, na ordem, e para no primeiro problema com uma frase dizendo
    o que fazer. Sai com 0 (pronto) ou 1 (parou)."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(errors="replace")
        except Exception:  # noqa: BLE001 - só para acento não derrubar o script
            pass

    inicio = time.perf_counter()
    try:
        conferir_o_que_vai_junto()
        limpar_o_anterior()
        print(f"Empacotando o teste de velocidade em {PASTA} (leva alguns minutos)...",
              flush=True)
        exe = rodar_o_pyinstaller()
        modelo = conferir_o_modelo()
        visual_c = completar_o_visual_c()
        livro = copiar_o_livro()
        bat, instrucoes = escrever_os_textos()
        letras, mais_longo = caminho_mais_longo(PASTA)
        print("Compactando...", flush=True)
        quantos = compactar()
    except ErroNoPacote as erro:
        print(f"\nO empacotamento parou: {erro}")
        return 1

    print(f"\nPronto em {time.perf_counter() - inicio:.0f} s.\n")
    print(f"  pasta:   {PASTA}  ({tamanho_mb(PASTA):.0f} MB, {quantos} arquivos)")
    print(f"  .zip:    {ZIP}  ({tamanho_mb(ZIP):.0f} MB)")
    print(f"  .exe:    {exe.name}")
    print(f"  .bat:    {bat.name}")
    print(f"  livro:   {livro.name} ({tamanho_mb(livro):.1f} MB)")
    print(f"  modelo:  {modelo.relative_to(PASTA)} ({tamanho_mb(modelo):.1f} MB)")
    print("  Visual C++ (no topo de _internal):")
    for nome, situacao in visual_c.items():
        print(f"    {nome}: {situacao}")
    if len({versao_do_arquivo(PASTA / INTERNO / nome) for nome in visual_c}) > 1:
        print("    ATENÇÃO: versões diferentes do Visual C++ no topo (ver _onde_achar)")
    aviso = "" if letras <= CAMINHO_MAIS_LONGO_SEGURO else "  ATENÇÃO: comprido demais"
    print(f"  caminho mais longo dentro da pasta: {letras} letras{aviso}\n    {mais_longo}")
    print("\nPara o pendrive: o .zip e o arquivo de instruções ao lado dele:")
    print(f"  {ZIP}")
    print(f"  {instrucoes[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
