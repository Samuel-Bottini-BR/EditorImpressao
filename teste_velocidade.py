"""Teste de velocidade do Editor de Impressão (item 0.5 do plano).

Mede quanto o programa demora nas três coisas que o Kaique mais sente:

    1. ABRIR O LIVRO: do arquivo escolhido até a análise de todas as folhas
       terminar (lombada, ângulo, bordas, cor);
    2. TROCAR DE PÁGINA: quanto demora a prévia de uma página nunca vista ficar
       pronta na tela de conferir (20 trocas espalhadas pelo livro);
    3. PROCESSAR 10 PÁGINAS: o processamento de verdade até o PDF de saída,
       em Mágico pro e em Preto e branco.

Mais a memória máxima usada e os dados da máquina, para os números do PC do
Samuel e do notebook do Kaique não se confundirem.

A regra 6 do plano ("nenhum item pode deixar o programa mais lento") é
conferida com ele: roda antes e depois de cada mudança de processamento.

Como rodar (da pasta do projeto)::

    .venv\\Scripts\\python.exe teste_velocidade.py --preparar   (uma vez só)
    .venv\\Scripts\\python.exe teste_velocidade.py              (a medição)
    .venv\\Scripts\\python.exe teste_velocidade.py --rapido     (só confere que funciona)

O --preparar grava gabarito\\velocidade\\marial_300.pdf: as 300 primeiras
páginas do Marial do acervo, copiadas como estão. A medição faz 3 rodadas
completas e grava o relatório em relatorios\\velocidade\\ (.md, .html, .pdf e
um .json com os números crus). O --rapido usa 1 rodada, 20 páginas, 3 trocas e
2 páginas processadas: os números dele NÃO valem como medição.

Empacotado (item 0.6, notebook do Kaique, que não tem Python): quem gera o
pacote é empacotar_teste_velocidade.py - leia o cabeçalho dele antes de
empacotar de outro jeito. O .exe procura marial_300.pdf ao lado dele e grava os
resultados na pasta resultados\\ ao lado dele. Nada aqui depende da pasta do
projeto existir. O modelo do detector de gravura e letra
(modelos\\doclayout.onnx, fora do git) é achado por core/detectar_regioes.py ao
lado da pasta core\\ e tem de ir junto no pacote, com console ligado (não
--windowed). Sem o modelo o teste roda, mas mede um programa mais rápido que o
de verdade, e o relatório avisa em destaque. No fim, empacotado, a janela preta
não fecha sozinha, nem com um Enter apertado durante a medição (ver despedir e
esvaziar_o_teclado); durante a medição o Windows não suspende o computador nem
apaga a tela (ver computador_acordado), e um clique dentro da janela preta não
pausa o teste (ver edicao_rapida_desligada; o relatório diz se deu para
desligar). A medição é sempre na janela preta clássica do Windows,
e não no Terminal novo (decisão do Samuel, 25/09/2026): quem garante é o
RODAR O TESTE.bat, que se reabre nela (ver TEXTO_DO_BAT em
empacotar_teste_velocidade.py); daqui, o relatório diz em que janela o teste
rodou, como prova (ver janela_do_teste). O PowerShell, que lê a placa de vídeo
e o disco do livro, é chamado pelo caminho completo, e não pelo PATH (ver
_caminho_do_powershell).

A REGRA DESTE ARQUIVO: medir sempre pelas MESMAS funções que o programa usa,
na mesma ordem. Um caminho mais rápido ou mais lento que o do programa daria
números de outro programa. Cada função medir_* diz no docstring qual código do
programa ela imita e de onde ele foi copiado.

Seguro mudar: os textos do relatório, o formato dos números, as mensagens do
terminal. Arriscado mudar: o que as funções medir_* chamam, a espera entre as
trocas de página e a escolha das páginas - mudar qualquer um deles muda o que
está sendo medido, e aí os números de antes e de depois deixam de se comparar
(suba VERSAO_DO_TESTE quando isso for de propósito).
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import gc
import inspect
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import traceback
import unicodedata
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# o que o teste mede
# ---------------------------------------------------------------------------

# Suba este número quando mudar O QUE é medido (outra página, outra espera,
# outra função). Números de versões diferentes não se comparam.
VERSAO_DO_TESTE = 1

NOME_DO_LIVRO = "marial_300.pdf"
FOLHAS_DO_LIVRO = 300

# O original fica no acervo, que é SOMENTE LEITURA: daqui só se copia.
ORIGINAL_DO_LIVRO = Path(
    r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO"
    r"\LIVROS PARA TESTE\Marial de sermoens - Frei Balthasar Paez. (1).pdf"
)
# Nenhum arquivo é gravado numa pasta com este nome (ver _recusar_o_acervo).
PASTA_DO_ACERVO = "EditorImpressao-arquivos"

RODADAS = 3
TROCAS = 20
PAGINAS_PROCESSADAS = 10

# --rapido: só prova que o teste roda do começo ao fim.
RAPIDO_FOLHAS = 20
RAPIDO_RODADAS = 1
RAPIDO_TROCAS = 3
RAPIDO_PAGINAS = 2

# Os dois filtros medidos no processamento. Os nomes são as chaves de
# core.filtros (rodar_medicao confere que ainda existem). O Mágico pro é o
# mais parecido com o CamScanner que o Kaique usa hoje.
FILTROS_MEDIDOS = ("magico_pro", "preto_e_branco")
NOMES_DOS_FILTROS = {"magico_pro": "Mágico pro", "preto_e_branco": "Preto e branco"}

# O filtro do livro ao abrir: como se o Kaique marcasse "Mágico pro" na tela
# "O que fazer". O programa nasce em Original; o teste usa o Mágico pro porque
# é o que o Kaique usa, e porque assim uma mudança que deixe o filtro mais
# lento aparece também em "trocar de página", e não só em "processar".
# Mudar isto muda o que "trocar de página" mede (suba VERSAO_DO_TESTE).
FILTRO_DO_LIVRO = "magico_pro"

# Quanto esperar uma prévia antes de desistir. Generoso de propósito: o
# notebook do Kaique é mais lento, e uma prévia que não chega é defeito a
# relatar, não a esconder.
LIMITE_DA_PREVIA_S = 300.0


class ErroNaMedicao(Exception):
    """Uma etapa não terminou como o programa terminaria. A mensagem já vem em
    português, para ir direto para o terminal e para o arquivo de erro."""


# ---------------------------------------------------------------------------
# números em português: vírgula decimal, frase antes do número
# ---------------------------------------------------------------------------


def formatar_numero(valor: float, casas: int = 1) -> str:
    """12.44 -> "12,4"; 1234.56 -> "1.234,6" (vírgula decimal, ponto de milhar)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "\0").replace(".", ",").replace("\0", ".")


def _plural(quantidade: int, singular: str, plural: str) -> str:
    """ "1 minuto", "2 minutos"."""
    return f"{quantidade} {singular if quantidade == 1 else plural}"


def _casas(segundos: float) -> int:
    """Duas casas abaixo de 0,1 s (senão tudo vira "0,0"), uma casa no resto."""
    return 2 if segundos < 0.1 else 1


def _horas_minutos_segundos(segundos: float) -> tuple[int, int, int]:
    total = int(round(segundos))
    horas, resto = divmod(total, 3600)
    minutos, segs = divmod(resto, 60)
    return horas, minutos, segs


def segundos_por_extenso(segundos: float | None) -> str:
    """Tempo para ler em frase: "0,4 segundo", "12,4 segundos",
    "1 minuto e 5 segundos". Abaixo de 2 fica no singular, como manda a
    gramática ("1,5 segundo"). None vira "não medido", nunca 0."""
    if segundos is None or segundos < 0:
        return "não medido"
    casas = _casas(segundos)
    if round(segundos, casas) < 60:
        palavra = "segundo" if round(segundos, casas) < 2 else "segundos"
        return f"{formatar_numero(segundos, casas)} {palavra}"
    horas, minutos, segs = _horas_minutos_segundos(segundos)
    if horas:
        partes = [_plural(horas, "hora", "horas")]
        if minutos:
            partes.append(_plural(minutos, "minuto", "minutos"))
    else:
        partes = [_plural(minutos, "minuto", "minutos")]
        if segs:
            partes.append(_plural(segs, "segundo", "segundos"))
    return " e ".join(partes)


def segundos_curto(segundos: float | None) -> str:
    """Tempo curto para tabela: "0,4 s", "42,1 s", "2 min 5 s", "1 h 2 min"."""
    if segundos is None or segundos < 0:
        return "não medido"
    casas = _casas(segundos)
    if round(segundos, casas) < 60:
        return f"{formatar_numero(segundos, casas)} s"
    horas, minutos, segs = _horas_minutos_segundos(segundos)
    if horas:
        return f"{horas} h {minutos} min" if minutos else f"{horas} h"
    return f"{minutos} min {segs} s" if segs else f"{minutos} min"


def formatar_mb(mb: float | None) -> str:
    """ "812 MB", "1.235 MB". None vira "não medida", nunca 0."""
    if mb is None:
        return "não medida"
    return f"{formatar_numero(mb, 0)} MB"


def formatar_gb(gb: float | None) -> str:
    """ "16 GB" quando é redondo, "15,4 GB" quando não é."""
    if gb is None:
        return "não consegui ler"
    if abs(gb - round(gb)) < 0.05:
        return f"{int(round(gb))} GB"
    return f"{formatar_numero(gb, 1)} GB"


def _relogio(segundos: float) -> str:
    """Tempo decorrido na linha de progresso: "4:07", "1:02:05"."""
    horas, minutos, segs = _horas_minutos_segundos(segundos)
    if horas:
        return f"{horas}:{minutos:02d}:{segs:02d}"
    return f"{minutos}:{segs:02d}"


# ---------------------------------------------------------------------------
# onde as coisas ficam
# ---------------------------------------------------------------------------


def pasta_do_programa(congelado: bool | None = None, executavel: str | None = None,
                      arquivo: str | None = None) -> Path:
    """A pasta onde o teste "mora": é dali que ele procura o livro e para onde
    manda os resultados.

    Empacotado pelo PyInstaller (sys.frozen), é a pasta do .exe. NUNCA a de
    __file__: empacotado, __file__ aponta para a pasta temporária onde o
    PyInstaller se desempacota (sys._MEIPASS), que some quando o programa
    fecha - o relatório iria junto. Rodando pelo Python, é a pasta deste
    arquivo (a raiz do projeto). Os parâmetros existem para o teste
    automático; o uso normal é sem nenhum.
    """
    if congelado is None:
        congelado = bool(getattr(sys, "frozen", False))
    if congelado:
        return Path(executavel or sys.executable).resolve().parent
    return Path(arquivo or __file__).resolve().parent


def escolher_livro(argumento: str | None, pasta: Path) -> tuple[Path | None, list[Path]]:
    """Qual PDF medir. Devolve (o livro ou None, os lugares procurados).

    Ordem: o caminho dado na linha de comando; senão marial_300.pdf ao lado do
    programa; senão gabarito\\velocidade\\marial_300.pdf. Quem dá um caminho e
    erra NÃO cai no livro padrão calado: mediria outro livro sem ninguém notar.
    """
    if argumento:
        caminho = Path(argumento).expanduser()
        return (caminho if caminho.is_file() else None), [caminho]
    candidatos = [pasta / NOME_DO_LIVRO, pasta / "gabarito" / "velocidade" / NOME_DO_LIVRO]
    for candidato in candidatos:
        if candidato.is_file():
            return candidato, candidatos
    return None, candidatos


def pasta_de_resultados(pasta: Path, congelado: bool, escolhida: str | None = None) -> Path:
    """Onde gravar o relatório: a pasta pedida em --saida; senão resultados\\
    ao lado do .exe (empacotado) ou relatorios\\velocidade\\ (no projeto)."""
    if escolhida:
        return Path(escolhida)
    if congelado:
        return pasta / "resultados"
    return pasta / "relatorios" / "velocidade"


def nome_seguro(texto: str) -> str:
    """Nome que o Windows aceita, sem acento (regra do projeto para caminho de
    disco): "Estação São Bento?" -> "Estacao-Sao-Bento"."""
    sem_acento = "".join(c for c in unicodedata.normalize("NFKD", texto)
                         if not unicodedata.combining(c))
    limpo = "".join(c if (c.isascii() and (c.isalnum() or c in "-_")) else "-"
                    for c in sem_acento)
    while "--" in limpo:
        limpo = limpo.replace("--", "-")
    return limpo.strip("-_") or "computador"


def nome_base(computador: str, quando: datetime, rapido: bool) -> str:
    """velocidade-<computador>-<AAAA-MM-DD-HHMM>, com -rapido no fim quando for
    o teste rápido (para nunca ser confundido com uma medição)."""
    base = f"velocidade-{nome_seguro(computador)}-{quando:%Y-%m-%d-%H%M}"
    return f"{base}-rapido" if rapido else base


def _recusar_o_acervo(destino: Path) -> None:
    """O acervo é somente leitura: nada deste teste é gravado lá dentro."""
    partes = {parte.lower() for parte in Path(destino).resolve().parts}
    if PASTA_DO_ACERVO.lower() in partes:
        raise ErroNaMedicao(
            f"Recusei gravar em {destino}: a pasta {PASTA_DO_ACERVO} é o acervo, "
            "que é somente leitura.")


# ---------------------------------------------------------------------------
# quais páginas entram na medição
# ---------------------------------------------------------------------------


def paginas_espalhadas(total: int, quantas: int, folga: int = 3) -> list[int]:
    """`quantas` páginas (índices a partir de 0) espalhadas pelo livro inteiro,
    sempre as mesmas para o mesmo livro.

    Ao virar a página o programa já adianta as `folga` seguintes
    (GerenciadorPrevias.pre_carregar). Por isso duas páginas medidas ficam
    SEMPRE a mais de `folga` páginas uma da outra: senão a segunda já estaria
    pronta, e a medida "página nunca vista" mentiria. Livro pequeno demais
    para isso mede menos trocas.
    """
    if total <= 0 or quantas <= 0:
        return []
    cabem = max(1, total // (folga + 1))
    quantas = min(quantas, cabem)
    passo = total / quantas
    # Com passo >= folga + 1, a distância entre dois int() seguidos nunca fica
    # abaixo de folga + 1.
    return [int((k + 0.5) * passo) for k in range(quantas)]


def paginas_seguidas_do_meio(total: int, quantas: int) -> list[int]:
    """`quantas` páginas seguidas do meio do livro. O meio porque o começo de
    um livro antigo costuma ser capa e folha em branco, que não representam o
    trabalho de verdade."""
    if total <= 0 or quantas <= 0:
        return []
    quantas = min(quantas, total)
    inicio = max(0, min(total - quantas, total // 2 - quantas // 2))
    return list(range(inicio, inicio + quantas))


def alinhar_ao_comeco_da_folha(indices: list[int], metades: list[str]) -> list[int]:
    """Numa folha dividida, as duas páginas saem da MESMA leitura da folha
    (processar lê a folha uma vez para as duas metades). Começar a medida numa
    metade da direita leria uma folha a mais só para meia página; por isso a
    lista recua uma casa. `metades` é o campo `metade` de cada página."""
    if not indices:
        return []
    primeiro = indices[0]
    if primeiro > 0 and metades[primeiro] == "direita":
        return [i - 1 for i in indices]
    return list(indices)


# ---------------------------------------------------------------------------
# a máquina
# ---------------------------------------------------------------------------


def _ler_registro(caminho: str, valor: str) -> str | None:
    """Um valor de HKEY_LOCAL_MACHINE, ou None. Só leitura, não precisa de
    administrador."""
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, caminho) as chave:
            dado, _tipo = winreg.QueryValueEx(chave, valor)
        texto = str(dado).strip()
        return texto or None
    except Exception:  # noqa: BLE001 - dado da máquina que falta não para o teste
        return None


def _caminho_do_powershell() -> str:
    """Onde está o powershell.exe: o caminho completo de sempre,
    %SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe (o mesmo em
    todo Windows 10/11); só se ele não existir, "powershell", que o Windows
    procura pelo PATH (o plano B).

    Por quê: essa pasta só é achada pelo PATH, e com o PATH mexido (um
    instalador que o estraga, por exemplo) o nome sozinho não é encontrado.
    _powershell engole o erro, de propósito, e o relatório sai sem a linha
    "Disco do livro" sem ninguém notar - e é ela que mostraria um teste rodado
    direto do pendrive, e não da Área de Trabalho. Visto no PC do Samuel
    (25/09/2026): com o PATH vazio, tipo_do_disco devolvia None; pelo caminho
    completo, "HD externo (USB)".

    Seguro mudar: a ordem de SystemRoot e windir (as duas variáveis dizem a
    pasta do Windows). Arriscado mudar: voltar a chamar só "powershell"
    primeiro.
    """
    windows = os.environ.get("SystemRoot") or os.environ.get("windir") or r"C:\Windows"
    completo = Path(windows) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    return str(completo) if completo.is_file() else "powershell"


def _powershell(comando: str, limite_s: float = 30.0) -> list[str]:
    """Roda um comando curto do PowerShell (que existe em todo Windows 10/11) e
    devolve as linhas não vazias. Lista vazia se não der - nunca levanta.

    O PowerShell é chamado pelo caminho completo, e não pelo PATH (ver
    _caminho_do_powershell)."""
    try:
        feito = subprocess.run(
            [_caminho_do_powershell(), "-NoProfile", "-NonInteractive", "-Command",
             "[Console]::OutputEncoding=[Text.Encoding]::UTF8; " + comando],
            capture_output=True, timeout=limite_s,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception:  # noqa: BLE001
        return []
    if feito.returncode != 0:
        return []
    linhas = feito.stdout.decode("utf-8", "replace").splitlines()
    return [linha.strip() for linha in linhas if linha.strip()]


def _sem_repetir(nomes: list[str]) -> list[str]:
    vistos: list[str] = []
    for nome in nomes:
        if nome and nome not in vistos:
            vistos.append(nome)
    return vistos


def _placas_de_video() -> list[str]:
    """Os nomes das placas de vídeo. Primeiro pelo Windows (Win32_VideoController,
    só as que estão na máquina agora); se não der, pelo registro, que pode
    guardar também uma placa que já saiu da máquina."""
    nomes = _sem_repetir(_powershell("(Get-CimInstance Win32_VideoController).Name"))
    if nomes:
        return nomes
    try:
        import winreg

        classe = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        achados: list[str] = []
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, classe) as chave:
            for i in range(winreg.QueryInfoKey(chave)[0]):
                sub = winreg.EnumKey(chave, i)
                if sub.isdigit():
                    nome = _ler_registro(f"{classe}\\{sub}", "DriverDesc")
                    if nome:
                        achados.append(nome)
        return _sem_repetir(achados)
    except Exception:  # noqa: BLE001
        return []


def _versao_do_windows() -> str:
    """ "Windows 11 Home Single Language 25H2 (compilação 26200.9457)".

    O registro do Windows 11 ainda diz "Windows 10" no ProductName (a
    Microsoft nunca trocou); quem manda é o número da compilação: de 22000 em
    diante é Windows 11.
    """
    base = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
    nome = _ler_registro(base, "ProductName") or f"{platform.system()} {platform.release()}"
    versao = _ler_registro(base, "DisplayVersion") or _ler_registro(base, "ReleaseId")
    compilacao = _ler_registro(base, "CurrentBuildNumber")
    revisao = _ler_registro(base, "UBR")
    if compilacao and compilacao.isdigit() and int(compilacao) >= 22000:
        nome = nome.replace("Windows 10", "Windows 11")
    texto = nome
    if versao:
        texto += f" {versao}"
    if compilacao:
        texto += f" (compilação {compilacao}" + (f".{revisao}" if revisao else "") + ")"
    return texto


def _memoria_gb() -> tuple[float | None, float | None]:
    """(memória instalada, memória que o Windows enxerga), em GB. A instalada é
    a da etiqueta (16 GB); a outra é um pouco menor (15,4 GB), porque parte fica
    reservada para a placa de vídeo e o sistema."""
    instalada = utilizavel = None
    try:
        import ctypes

        kb = ctypes.c_ulonglong(0)
        if ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(kb)):
            instalada = kb.value / 1024 / 1024
    except Exception:  # noqa: BLE001
        pass
    try:
        import psutil

        utilizavel = psutil.virtual_memory().total / 1024 ** 3
    except Exception:  # noqa: BLE001
        pass
    return instalada, utilizavel


def _energia() -> dict:
    """Na tomada ou na bateria. Notebook na bateria anda mais devagar, e os
    dois computadores do plano (o do Samuel e o do Kaique) são notebooks."""
    try:
        import psutil

        bateria = psutil.sensors_battery()
    except Exception:  # noqa: BLE001
        return {"na_tomada": None, "carga": None, "texto": "não consegui ler"}
    if bateria is None:
        return {"na_tomada": True, "carga": None, "texto": "sem bateria (computador de mesa)"}
    carga = f"{bateria.percent:.0f}%"
    if bateria.power_plugged:
        return {"na_tomada": True, "carga": carga, "texto": f"na tomada (bateria em {carga})"}
    return {"na_tomada": False, "carga": carga, "texto": f"na bateria ({carga})"}


def tipo_do_disco(caminho: Path) -> str | None:
    """Que disco guarda o livro: "SSD (NVMe)", "HD externo (USB)"... ou None
    se o Windows não disser. Pesa na primeira vez que o livro é aberto.

    Procura o disco pelo número (DiskNumber = DeviceId). O caminho mais
    curto, Get-Partition | Get-Disk | Get-PhysicalDisk, não devolve nada para
    disco USB - achado no próprio PC do Samuel, em que o projeto mora num HD
    externo USB.
    """
    letra = Path(caminho).resolve().drive.rstrip(":")
    if len(letra) != 1 or not letra.isalpha():
        return None
    linhas = _powershell(
        f"$n = (Get-Partition -DriveLetter {letra}).DiskNumber; "
        "Get-PhysicalDisk | Where-Object { $_.DeviceId -eq [string]$n } | "
        "ForEach-Object { [string]$_.MediaType + '|' + [string]$_.BusType }")
    if not linhas:
        return None
    midia, _barra, barramento = linhas[0].partition("|")
    if midia == "SSD" or barramento == "NVMe":
        tipo = "SSD"
    elif midia == "HDD":
        tipo = "HD"
    else:
        tipo = "disco"
    if barramento == "USB":
        return f"{tipo} externo (USB)"
    return f"{tipo} ({barramento})" if barramento else tipo


def nome_do_computador() -> str:
    return os.environ.get("COMPUTERNAME") or platform.node() or "computador"


def dados_da_maquina() -> dict:
    """O que vai no topo do relatório, para um número de uma máquina nunca ser
    comparado por engano com o de outra."""
    instalada, utilizavel = _memoria_gb()
    try:
        import psutil

        fisicos = psutil.cpu_count(logical=False)
    except Exception:  # noqa: BLE001
        fisicos = None
    processador = (_ler_registro(r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
                                 "ProcessorNameString")
                   or platform.processor() or "não consegui ler")
    return {
        "computador": nome_do_computador(),
        "processador": " ".join(processador.split()),
        "nucleos_fisicos": fisicos,
        "nucleos_logicos": os.cpu_count() or 1,
        "memoria_instalada_gb": instalada,
        "memoria_utilizavel_gb": utilizavel,
        "placas_de_video": _placas_de_video(),
        "windows": _versao_do_windows(),
        "energia": _energia(),
    }


def versoes_das_bibliotecas() -> dict:
    """As versões que pesam na velocidade. Uma troca de versão entre duas
    medições explica número que mudou sem ninguém mexer no código."""
    versoes: dict = {"python": platform.python_version(),
                     "empacotado": bool(getattr(sys, "frozen", False))}
    try:
        import fitz

        versoes["pymupdf"] = str(getattr(fitz, "VersionBind", "") or getattr(fitz, "__version__", "?"))
    except Exception:  # noqa: BLE001
        versoes["pymupdf"] = "?"
    try:
        import cv2

        versoes["opencv"] = cv2.__version__
    except Exception:  # noqa: BLE001
        versoes["opencv"] = "?"
    try:
        import numpy

        versoes["numpy"] = numpy.__version__
    except Exception:  # noqa: BLE001
        versoes["numpy"] = "?"
    try:
        import onnxruntime

        versoes["onnxruntime"] = onnxruntime.__version__
    except Exception:  # noqa: BLE001
        versoes["onnxruntime"] = "?"
    try:
        import PySide6

        versoes["pyside6"] = PySide6.__version__
    except Exception:  # noqa: BLE001
        versoes["pyside6"] = "?"
    return versoes


# ---------------------------------------------------------------------------
# memória
# ---------------------------------------------------------------------------


def pico_de_memoria_mb() -> float | None:
    """O maior uso de memória deste processo desde que ele começou, em MB.

    É o "pico do conjunto de trabalho" que o próprio Windows guarda: não perde
    um pico curto que caia entre duas leituras, como perderia uma amostragem.
    Só sobe; por isso, lido no fim de cada etapa, mostra em que etapa ele foi
    alcançado. psutil primeiro; sem ele, a mesma conta direto no Windows.
    Devolve None se não der para medir - nunca 0.
    """
    try:
        import psutil

        pico = getattr(psutil.Process().memory_info(), "peak_wset", None)
        if pico:
            return pico / 1024 / 1024
    except Exception:  # noqa: BLE001
        pass
    return _pico_pelo_windows()


def _pico_pelo_windows() -> float | None:
    """Plano B sem psutil: GetProcessMemoryInfo, por ctypes.

    Arriscado mexer: os tipos. A primeira versão desta chamada no projeto (ver
    teste_bateria.py) devolvia 0 em silêncio porque o handle do processo era
    truncado em 64 bits. Por isso GetCurrentProcess devolve HANDLE declarado,
    os argumentos têm tipo, e falha vira None, nunca 0.
    """
    try:
        import ctypes
        from ctypes import wintypes

        class ContadoresDeMemoria(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        kernel32.GetCurrentProcess.argtypes = []
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(ContadoresDeMemoria), wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL

        contadores = ContadoresDeMemoria()
        contadores.cb = ctypes.sizeof(ContadoresDeMemoria)
        if not psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(),
                                          ctypes.byref(contadores), contadores.cb):
            return None
        if contadores.PeakWorkingSetSize <= 0:
            return None
        return contadores.PeakWorkingSetSize / 1024 / 1024
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# o livro de teste
# ---------------------------------------------------------------------------


def preparar_livro(origem: Path, destino: Path, folhas: int = FOLHAS_DO_LIVRO) -> bool:
    """Grava as `folhas` primeiras páginas de `origem` em `destino`.

    As páginas são COPIADAS como estão (insert_pdf), sem rasterizar de novo:
    o arquivo sai tão pesado quanto o trecho do original, que é o que o
    programa enfrenta de verdade. O original só é lido. Grava primeiro num
    arquivo .parcial e só no fim troca de nome - interromper no meio não deixa
    um livro pela metade no lugar do bom.

    Devolve True se gravou agora, False se `destino` já existia com essas
    páginas (não refaz: "grave uma vez").
    """
    import fitz

    origem, destino = Path(origem), Path(destino)
    _recusar_o_acervo(destino)
    if destino.is_file():
        try:
            with fitz.open(destino) as pronto:
                if pronto.page_count == folhas:
                    return False
        except Exception:  # noqa: BLE001 - arquivo estragado: refaz por cima
            pass
    if not origem.is_file():
        raise ErroNaMedicao(f"Não achei o livro original em {origem}.")

    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_name(destino.name + ".parcial")
    with fitz.open(origem) as fonte:
        ultima = min(folhas, fonte.page_count) - 1
        novo = fitz.open()
        try:
            novo.insert_pdf(fonte, from_page=0, to_page=ultima)
            novo.save(parcial)
        finally:
            novo.close()
    os.replace(parcial, destino)
    return True


# ---------------------------------------------------------------------------
# as medições - sempre pelas funções do programa
# ---------------------------------------------------------------------------

Avisar = Callable[[str], None]

# A aplicação Qt do teste. Fica aqui (e não numa variável local) para viver
# até o processo acabar: apagá-la no meio deixaria sinais sem dono.
_APLICACAO_QT = None


def _garantir_aplicacao_qt():
    """Sinais e tarefas de fundo do Qt precisam de uma aplicação - mas não de
    janela. QCoreApplication não abre janela nem precisa de tela: não depende
    de QT_QPA_PLATFORM=offscreen nem de plugin de vídeo nenhum, o que também
    simplifica o empacotamento. Se já existir uma (num teste automático, por
    exemplo), usa a que existe."""
    global _APLICACAO_QT
    from PySide6.QtCore import QCoreApplication

    if _APLICACAO_QT is None:
        _APLICACAO_QT = QCoreApplication.instance() or QCoreApplication(
            [sys.argv[0] if sys.argv else "teste_velocidade"])
    return _APLICACAO_QT


def medir_abrir(caminho: Path, avisar: Avisar) -> tuple[dict, object]:
    """ETAPA 1 - abrir o livro: do arquivo escolhido até a análise de todas as
    folhas terminar. Devolve (tempos, o Projeto analisado).

    Faz o que o programa faz, na mesma ordem, sem a tela:

    1. ui/janela_principal.py, JanelaPrincipal.abrir_livro: abrir_pdf, contar
       as folhas, info_paginas, olhar se o PDF tem camadas (item 1.1,
       core.camadas.pdf_tem_camadas), fechar; e a leitura da assinatura do arquivo
       (projetos.assinatura_do_arquivo, que achar_por_assinatura faz para saber
       se o livro já tem projeto). A parte que GRAVA o projeto em
       %LOCALAPPDATA% fica de fora de propósito: o teste não pode encher a
       lista de projetos do programa.
    2. O Kaique clica em "Conferir" na tela "O que fazer" (o tempo dele ali
       não conta).
    3. ui/tarefas.py, TarefaAnalise.run -> core.pipeline.analisar_projeto: a
       análise de TODAS as folhas. É o mesmo run() que a QThread do programa
       executa; aqui ele roda direto, sem thread, porque não há tela para
       manter viva.

    Opções: as que modelos.Projeto já traz (as mesmas caixas marcadas da tela
    "O que fazer"), com o filtro do livro em FILTRO_DO_LIVRO.
    """
    from core.camadas import pdf_tem_camadas
    from core.pdf_io import ErroPDF, abrir_pdf, info_paginas
    from modelos import Projeto
    from projetos import assinatura_do_arquivo
    from ui.tarefas import TarefaAnalise

    inicio = time.perf_counter()
    try:
        doc = abrir_pdf(caminho)
    except ErroPDF as erro:
        # A mensagem do programa já é a que o Kaique leria na tela.
        raise ErroNaMedicao(str(erro)) from erro
    try:
        folhas = doc.page_count
        info_paginas(doc)
        # item 1.1 (29/09/2026): abrir_livro olha também se o PDF vem com
        # camadas (só a estrutura, milissegundos)
        pdf_tem_camadas(doc)
    finally:
        doc.close()
    assinatura_do_arquivo(caminho)
    arquivo_s = time.perf_counter() - inicio

    projeto = Projeto(caminho_entrada=str(caminho), nome=Path(caminho).stem)
    projeto.filtro_padrao = FILTRO_DO_LIVRO

    tarefa = TarefaAnalise(projeto)
    saida: dict = {}
    tarefa.progresso.connect(
        lambda feito, total, _texto: avisar(
            f"abrir o livro: folha {min(feito + 1, total)} de {total}"))
    tarefa.concluida.connect(lambda analisado: saida.setdefault("projeto", analisado))
    tarefa.falhou.connect(lambda mensagem: saida.setdefault("erro", mensagem))

    comeco = time.perf_counter()
    tarefa.run()
    analise_s = time.perf_counter() - comeco

    if "projeto" not in saida:
        raise ErroNaMedicao(
            "A análise do livro não terminou: "
            f"{saida.get('erro', 'o programa não disse por quê')} "
            "(o detalhe técnico fica no erros.log do programa).")
    analisado = saida["projeto"]
    return {"arquivo_s": arquivo_s, "analise_s": analise_s,
            "total_s": arquivo_s + analise_s,
            "folhas": folhas, "paginas": len(analisado.paginas)}, analisado


def medir_trocas(projeto, indices: list[int], dpi: int, avisar: Avisar) -> dict:
    """ETAPA 2 - trocar de página: quanto demora a prévia de uma página nunca
    vista ficar pronta.

    Faz o que ui/tela_conferir.py, TelaConferir._atualizar_previa, faz ao
    virar a página numa aba que mostra a página processada (Bordas,
    Endireitar, Marcar, Filtro)::

        img = self.previas.pegar(self.indice_pagina, self._dpi_atual)
        self.previas.pre_carregar(self.indice_pagina, self._dpi_atual)

    com o GerenciadorPrevias de verdade (ui/tarefas.py): as mesmas 2 linhas
    de trabalho em paralelo, a mesma trava do leitor de PDF e o mesmo
    adiantamento das páginas seguintes, que disputa a máquina com a página
    pedida. Cada prévia passa por _TarefaPrevia.run -> renderizar_pagina. O
    tempo vai da chamada até o sinal `pronta` daquela página. Desenhar a
    imagem na tela fica de fora (não há tela).

    Entre uma troca e outra o teste espera o programa terminar de adiantar as
    páginas seguintes, como o Kaique, que olha a página antes de passar. Sem
    essa espera a medida dependeria da pressa do TESTE em virar as páginas.

    Arriscado mudar: as duas chamadas acima e a espera. `_pedidas` é interno
    do GerenciadorPrevias (o que foi pedido e ainda não chegou); se ele mudar
    de nome no programa, ajuste aqui.
    """
    from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer

    from ui.tarefas import GerenciadorPrevias

    gerenciador = GerenciadorPrevias(projeto.caminho_entrada, projeto)
    chegadas: dict[str, float] = {}
    estado: dict = {"alvo": None, "laco": None}

    def chegou(chave: str, _img) -> None:
        # Roda na linha principal, dentro do GerenciadorPrevias._guardar, no
        # mesmo instante em que a tela receberia a prévia.
        chegadas.setdefault(chave, time.perf_counter())
        if chave == estado["alvo"] and estado["laco"] is not None:
            estado["laco"].quit()

    gerenciador.pronta.connect(chegou)

    def esperar(pronto: Callable[[], bool], limite_s: float) -> bool:
        """Deixa o Qt entregar os sinais até `pronto()` ou o limite. A
        prévia pedida encerra a espera na hora (em chegou); o relógio de 25 ms
        só serve para perceber erro, limite e o fim do adiantamento."""
        if pronto():
            return True
        laco = QEventLoop()
        relogio = QTimer()
        relogio.setInterval(25)
        prazo = time.perf_counter() + limite_s

        def conferir() -> None:
            if pronto() or time.perf_counter() > prazo:
                laco.quit()

        relogio.timeout.connect(conferir)
        estado["laco"] = laco
        relogio.start()
        try:
            laco.exec()
        finally:
            relogio.stop()
            estado["laco"] = None
        return pronto()

    tempos: list[float] = []
    try:
        for numero, indice in enumerate(indices, start=1):
            avisar(f"trocar de página: {numero} de {len(indices)} (página {indice + 1})")
            alvo = gerenciador.chave(indice, dpi)
            estado["alvo"] = alvo

            inicio = time.perf_counter()
            img = gerenciador.pegar(indice, dpi)
            gerenciador.pre_carregar(indice, dpi)
            if img is not None:
                raise ErroNaMedicao(
                    f"A prévia da página {indice + 1} já estava pronta antes de ser "
                    "pedida: ela não era uma página nunca vista, e a medida sairia errada.")

            esperar(lambda: alvo in chegadas or alvo not in gerenciador._pedidas,
                    LIMITE_DA_PREVIA_S)
            estado["alvo"] = None
            if alvo not in chegadas:
                if alvo in gerenciador._pedidas:
                    raise ErroNaMedicao(
                        f"A prévia da página {indice + 1} não ficou pronta em "
                        f"{segundos_por_extenso(LIMITE_DA_PREVIA_S)}.")
                raise ErroNaMedicao(
                    f"A prévia da página {indice + 1} deu erro no programa (o detalhe "
                    "técnico fica no erros.log do programa).")
            tempos.append(chegadas[alvo] - inicio)

            # O Kaique olha a página: o programa termina de adiantar as seguintes.
            esperar(lambda: not gerenciador._pedidas, LIMITE_DA_PREVIA_S * 4)
    finally:
        gerenciador.parar()
        QCoreApplication.processEvents()

    if not tempos:
        raise ErroNaMedicao("Nenhuma troca de página foi medida.")
    pior = max(range(len(tempos)), key=tempos.__getitem__)
    return {"paginas": list(indices), "tempos_s": tempos,
            "media_s": statistics.fmean(tempos), "pior_s": tempos[pior],
            "pior_pagina": indices[pior]}


def medir_processar(projeto_analisado, indices: list[int], filtro: str,
                    pasta_temporaria: Path, avisar: Avisar) -> dict:
    """ETAPA 3 - processar: o processamento de verdade até o PDF de saída.

    Roda ui/tarefas.py, TarefaProcessar.run -> core.pipeline.processar, o
    mesmo que o botão "Confirmar e processar" dispara: dividir -> cortar
    bordas -> endireitar -> achar gravura e letra (garantir_selecao) ->
    filtro -> gravar o PDF, na qualidade do projeto (Projeto.qualidade_dpi,
    300 DPI).

    As páginas medidas recebem o filtro pedido (como quando o Kaique escolhe o
    filtro do livro) e as outras são marcadas como apagadas, que é como o
    próprio programa deixa uma página de fora (Projeto.paginas_ativas). O
    projeto é uma CÓPIA do analisado: nenhuma página chega com a marcação de
    gravura e letra já feita por outra etapa do teste. O PDF sai numa pasta
    temporária e é apagado logo depois de conferido.
    """
    import fitz

    from ui.tarefas import TarefaProcessar

    projeto = copy.deepcopy(projeto_analisado)
    escolhidas = set(indices)
    for pagina in projeto.paginas:
        if pagina.indice in escolhidas:
            pagina.filtro = filtro
        else:
            pagina.apagada = True
    projeto.caminho_saida = str(pasta_temporaria / f"saida-{filtro}.pdf")

    nome = NOMES_DOS_FILTROS.get(filtro, filtro)
    tarefa = TarefaProcessar(projeto)
    saida: dict = {}
    tarefa.progresso.connect(
        lambda feito, total, _texto: avisar(
            f"processar em {nome}: página {min(feito + 1, total)} de {total}"))
    tarefa.concluida.connect(lambda caminho: saida.setdefault("caminho", caminho))
    tarefa.falhou.connect(lambda mensagem: saida.setdefault("erro", mensagem))
    tarefa.cancelada.connect(lambda: saida.setdefault("erro", "o processamento foi cancelado"))

    inicio = time.perf_counter()
    tarefa.run()
    segundos = time.perf_counter() - inicio

    if "caminho" not in saida:
        raise ErroNaMedicao(
            f"O processamento em {nome} não terminou: "
            f"{saida.get('erro', 'o programa não disse por quê')} "
            "(o detalhe técnico fica no erros.log do programa).")
    arquivo = Path(saida["caminho"])
    with fitz.open(arquivo) as pronto:
        paginas = pronto.page_count
    tamanho_mb = arquivo.stat().st_size / 1024 / 1024
    arquivo.unlink(missing_ok=True)
    if paginas != len(indices):
        raise ErroNaMedicao(
            f"O PDF em {nome} saiu com {paginas} páginas, e deviam ser {len(indices)}.")
    return {"lista": list(indices), "segundos": segundos, "paginas": paginas,
            "por_pagina_s": segundos / paginas, "tamanho_saida_mb": tamanho_mb}


def rodar_uma_rodada(numero: int, configuracao: dict, livro: Path, pasta_temporaria: Path,
                     progresso: "Progresso") -> dict:
    """Uma rodada completa: abrir, trocar de página, processar nos dois filtros.
    Cada etapa trabalha numa cópia do projeto analisado, para uma não deixar
    trabalho pronto para a outra."""
    total = configuracao["rodadas"]
    comeco = time.perf_counter()

    def avisar(texto: str) -> None:
        progresso.mostrar(f"Rodada {numero} de {total} | {texto}")

    progresso.dizer(f"Rodada {numero} de {total}")
    memoria: dict[str, float | None] = {}

    abrir, projeto = medir_abrir(livro, avisar)
    memoria["abrir"] = pico_de_memoria_mb()
    progresso.dizer(f"  abrir o livro: {segundos_curto(abrir['total_s'])}")
    gc.collect()

    lista_trocas = paginas_espalhadas(len(projeto.paginas), configuracao["trocas"],
                                      folga=configuracao["paginas_adiantadas"])
    trocas = medir_trocas(copy.deepcopy(projeto), lista_trocas, configuracao["dpi_previa"],
                          avisar)
    memoria["trocas"] = pico_de_memoria_mb()
    progresso.dizer(f"  trocar de página: {segundos_curto(trocas['media_s'])} em média, "
                    f"{segundos_curto(trocas['pior_s'])} a mais demorada")
    gc.collect()

    lista_processadas = alinhar_ao_comeco_da_folha(
        paginas_seguidas_do_meio(len(projeto.paginas), configuracao["paginas_processadas"]),
        [pagina.metade for pagina in projeto.paginas])
    processar: dict[str, dict] = {}
    for filtro in FILTROS_MEDIDOS:
        processar[filtro] = medir_processar(projeto, lista_processadas, filtro,
                                            pasta_temporaria, avisar)
        memoria[f"processar_{filtro}"] = pico_de_memoria_mb()
        progresso.dizer(f"  processar {len(lista_processadas)} páginas em "
                        f"{NOMES_DOS_FILTROS[filtro]}: "
                        f"{segundos_curto(processar[filtro]['segundos'])}")
        gc.collect()

    return {"abrir": abrir, "trocas": trocas, "processar": processar,
            "memoria_pico_mb": memoria, "duracao_s": time.perf_counter() - comeco}


def rodar_medicao(livro: Path, rapido: bool, pasta_temporaria: Path, progresso: "Progresso",
                  maquina: dict, quando: datetime, edicao_rapida: str | None = None,
                  janela: dict | None = None) -> dict:
    """A medição inteira: prepara o que o programa prepara ao ligar, roda as
    rodadas e devolve o resultado completo (o mesmo que vai para o .json).

    `edicao_rapida` e `janela` só passam adiante, para o resultado (ver
    montar_resultado): não mudam nada do que é medido."""
    comeco = time.perf_counter()
    _garantir_aplicacao_qt()

    from core.aquecimento import aquecer_dependencias_pesadas
    from core.detectar_regioes import _detector
    from core.filtros import FILTROS
    from core.pipeline import DPI_ANALISE
    from modelos import Projeto
    from ui.tarefas import GerenciadorPrevias

    # A prévia "Rápida", a padrão da tela de conferir. Vem do próprio código
    # da tela: se ela mudar a resolução da prévia, o teste acompanha. Se a
    # tela mudar de lugar (Fase 4), ajuste este import - o teste precisa pedir
    # a prévia do MESMO tamanho que a tela pede.
    from ui.tela_conferir import DPI_PREVIA

    faltando = [filtro for filtro in FILTROS_MEDIDOS if filtro not in FILTROS]
    if faltando:
        raise ErroNaMedicao(
            f"O programa não tem mais o filtro {', '.join(faltando)}. Ajuste FILTROS_MEDIDOS "
            "em teste_velocidade.py (e suba VERSAO_DO_TESTE).")

    configuracao = {
        "rodadas": RAPIDO_RODADAS if rapido else RODADAS,
        "trocas": RAPIDO_TROCAS if rapido else TROCAS,
        "paginas_processadas": RAPIDO_PAGINAS if rapido else PAGINAS_PROCESSADAS,
        "dpi_analise": DPI_ANALISE,
        "dpi_previa": DPI_PREVIA,
        "dpi_saida": Projeto(caminho_entrada="").qualidade_dpi,
        "filtro_do_livro": FILTRO_DO_LIVRO,
        # Quantas páginas o programa adianta ao virar a página: lido do próprio
        # GerenciadorPrevias, para a escolha das páginas acompanhar se mudar.
        "paginas_adiantadas": inspect.signature(
            GerenciadorPrevias.pre_carregar).parameters["quantas"].default,
    }

    medido = livro
    if rapido:
        medido = pasta_temporaria / f"rapido-{RAPIDO_FOLHAS}-paginas.pdf"
        preparar_livro(livro, medido, RAPIDO_FOLHAS)

    progresso.dizer("Preparando: o mesmo aquecimento que o programa faz ao ligar...")
    inicio = time.perf_counter()
    aquecer_dependencias_pesadas()
    preparo = {"aquecimento_s": time.perf_counter() - inicio,
               "detector_de_regioes": bool(_detector.disponivel),
               "memoria_mb": pico_de_memoria_mb()}
    progresso.dizer(
        f"  levou {segundos_curto(preparo['aquecimento_s'])}; detector de gravura e letra: "
        + ("carregado" if preparo["detector_de_regioes"] else "NÃO CARREGOU"))

    rodadas = []
    for numero in range(1, configuracao["rodadas"] + 1):
        rodadas.append(rodar_uma_rodada(numero, configuracao, medido, pasta_temporaria,
                                        progresso))
        gc.collect()

    configuracao["lista_trocas"] = rodadas[0]["trocas"]["paginas"]
    configuracao["lista_processadas"] = rodadas[0]["processar"][FILTROS_MEDIDOS[0]]["lista"]
    info_livro = {
        "arquivo": livro.name,
        "caminho": str(livro.resolve()),
        "tamanho_mb": medido.stat().st_size / 1024 / 1024,
        "folhas": rodadas[0]["abrir"]["folhas"],
        "paginas": rodadas[0]["abrir"]["paginas"],
        "disco": tipo_do_disco(livro),
        "recortado": rapido,
    }
    return montar_resultado(
        rapido=rapido, quando=quando, maquina=maquina, versoes=versoes_das_bibliotecas(),
        livro=info_livro, configuracao=configuracao, preparo=preparo, rodadas=rodadas,
        duracao_total_s=time.perf_counter() - comeco, edicao_rapida=edicao_rapida,
        janela=janela)


# ---------------------------------------------------------------------------
# o resumo das rodadas
# ---------------------------------------------------------------------------


def _valores_da_rodada(rodada: dict) -> dict[str, float]:
    """Os números de uma rodada que entram no resumo."""
    return {
        "abrir_total_s": rodada["abrir"]["total_s"],
        "abrir_arquivo_s": rodada["abrir"]["arquivo_s"],
        "abrir_analise_s": rodada["abrir"]["analise_s"],
        "troca_media_s": rodada["trocas"]["media_s"],
        "troca_pior_s": rodada["trocas"]["pior_s"],
        "processar_magico_pro_s": rodada["processar"]["magico_pro"]["segundos"],
        "processar_preto_e_branco_s": rodada["processar"]["preto_e_branco"]["segundos"],
    }


def resumir(rodadas: list[dict]) -> dict[str, dict]:
    """Para cada medida: a primeira rodada (a que o Kaique sente ao abrir um
    livro pela primeira vez, com o disco "frio"), a mediana de todas (o valor
    do meio, que uma rodada atrapalhada não puxa) e todas as rodadas."""
    tabela = [_valores_da_rodada(rodada) for rodada in rodadas]
    resumo: dict[str, dict] = {}
    for chave in tabela[0]:
        valores = [linha[chave] for linha in tabela]
        resumo[chave] = {"primeira": valores[0], "mediana": statistics.median(valores),
                         "rodadas": valores}
    return resumo


# Em que ordem as etapas acontecem numa rodada, e como cada uma se lê.
ETAPAS_DA_MEMORIA = (
    ("abrir", "ao abrir o livro"),
    ("trocas", "ao trocar de página"),
    ("processar_magico_pro", "ao processar em Mágico pro"),
    ("processar_preto_e_branco", "ao processar em Preto e branco"),
)


def onde_foi_o_pico(preparo_mb: float | None, rodadas: list[dict]) -> tuple[float | None, str | None]:
    """(maior memória, em que etapa ela foi alcançada).

    O pico do Windows só sobe, e é lido no fim de cada etapa: a primeira etapa
    que chega ao máximo (com 1 MB de folga) é a que o alcançou.
    """
    leituras: list[tuple[float, str]] = []
    if preparo_mb is not None:
        leituras.append((preparo_mb, "ao carregar o programa, antes de abrir o livro"))
    varias = len(rodadas) > 1
    for numero, rodada in enumerate(rodadas, start=1):
        for chave, frase in ETAPAS_DA_MEMORIA:
            valor = rodada["memoria_pico_mb"].get(chave)
            if valor is not None:
                leituras.append((valor, f"{frase} (rodada {numero})" if varias else frase))
    if not leituras:
        return None, None
    maximo = max(valor for valor, _frase in leituras)
    for valor, frase in leituras:
        if valor >= maximo - 1.0:
            return maximo, frase
    return maximo, None


def montar_resultado(*, rapido: bool, quando: datetime, maquina: dict, versoes: dict,
                     livro: dict, configuracao: dict, preparo: dict, rodadas: list[dict],
                     duracao_total_s: float, edicao_rapida: str | None = None,
                     janela: dict | None = None) -> dict:
    """Junta tudo no formato do .json (e do relatório, que é montado dele).

    `edicao_rapida` é o que edicao_rapida_desligada disse (uma de
    SITUACOES_DA_EDICAO_RAPIDA), ou None quando ninguém disse (medição chamada
    fora de main). Não é número medido: só diz se um clique na janela preta
    podia ter pausado a medição.

    `janela` é o que janela_do_teste disse: {"situacao": uma de
    SITUACOES_DA_JANELA, "classe": a classe da janela que o Windows deu}, ou
    None quando ninguém perguntou. Também não é número medido: é a prova de
    que a medição foi na janela clássica.

    Os .json gravados antes destas chaves existirem não as têm; montar_texto
    aceita os dois."""
    pico, onde = onde_foi_o_pico(preparo.get("memoria_mb"), rodadas)
    return {
        "versao_do_teste": VERSAO_DO_TESTE,
        "rapido": rapido,
        "quando": quando.isoformat(timespec="seconds"),
        "maquina": maquina,
        "versoes": versoes,
        "livro": livro,
        "configuracao": configuracao,
        "preparo": preparo,
        "rodadas": rodadas,
        "resumo": resumir(rodadas),
        "memoria": {"pico_mb": pico, "onde": onde},
        "duracao_total_s": duracao_total_s,
        "edicao_rapida": edicao_rapida,
        "janela": janela,
    }


# ---------------------------------------------------------------------------
# o relatório
# ---------------------------------------------------------------------------


def descrever_livro(livro: dict) -> str:
    """ "300 páginas", ou "300 folhas (600 páginas depois de dividir)"."""
    folhas, paginas = livro["folhas"], livro["paginas"]
    if folhas == paginas:
        return f"{paginas} páginas"
    return f"{folhas} folhas ({paginas} páginas depois de dividir)"


def _lista_de_paginas(indices: list[int]) -> str:
    """[7, 22, 37] -> "8, 23 e 38" (a contagem das pessoas começa em 1)."""
    numeros = [str(i + 1) for i in indices]
    if len(numeros) <= 1:
        return "".join(numeros)
    return ", ".join(numeros[:-1]) + " e " + numeros[-1]


def _intervalo_de_paginas(indices: list[int]) -> str:
    """[145, ..., 154] -> "146 a 155"; duas páginas -> "10 e 11"; se não forem
    seguidas, a lista."""
    if len(indices) > 2 and indices == list(range(indices[0], indices[0] + len(indices))):
        return f"{indices[0] + 1} a {indices[-1] + 1}"
    return _lista_de_paginas(indices)


# A linha "Janela preta" de "Como foi medido" junta duas frases, nesta ordem
# (ver _linha_da_janela_preta): em que janela o teste rodou, conforme o que
# janela_do_teste disse, e o que houve com o modo de edição rápida, conforme o
# que edicao_rapida_desligada disse. Seguro mudar: o texto. Toda situação de
# SITUACOES_DA_JANELA e de SITUACOES_DA_EDICAO_RAPIDA precisa ter a sua frase
# (há teste para isso); cada frase termina em ponto.
_FRASES_DA_JANELA = {
    "classica": "o teste rodou na janela clássica do Windows.",
    "terminal_novo": "o teste rodou no Terminal novo do Windows (ou em outro programa do "
                     "mesmo tipo), e não na janela clássica, em que as medições devem ser "
                     "feitas.",
    "sem_janela": "o teste rodou sem janela preta nenhuma.",
    "desconhecida": "não deu para saber em que janela o teste rodou.",
}

_FRASES_DA_EDICAO_RAPIDA = {
    "desligado": "o modo de edição rápida ficou desligado durante a medição: um clique "
                 "dentro da janela não pausava o teste.",
    "ja_desligado": "o modo de edição rápida já estava desligado nesta janela: um clique "
                    "dentro dela não pausava o teste.",
    "sem_janela": "não havia o que desligar: o teste não recebia o teclado de uma janela "
                  "preta (foi chamado por outro programa, por exemplo), e o modo de edição "
                  "rápida ficou como estava.",
    "falhou": "o Windows não deixou desligar o modo de edição rápida. Se alguém clicou "
              "dentro da janela durante a medição, o teste pode ter pausado, e os tempos, "
              "saído maiores.",
}


def _linha_da_janela_preta(resultado: dict) -> list[str]:
    """A linha "Janela preta" de "Como foi medido": primeiro em que janela o
    teste rodou (ver janela_do_teste), depois o modo de edição rápida (ver
    edicao_rapida_desligada), como frases seguidas.

    Sai só o que o resultado disser. Um .json gravado antes de a janela entrar
    no relatório sai com a linha exatamente como era (só a edição rápida); um
    de antes das duas, ou de uma medição chamada fora de main, sai sem a
    linha. Uma "janela" que não seja o dicionário de janela_do_teste (um .json
    mexido a mão) é ignorada, sem erro.
    """
    janela = resultado.get("janela")
    situacao = janela.get("situacao") if isinstance(janela, dict) else None
    if not isinstance(situacao, str):
        situacao = None  # uma lista ali quebraria o .get do dicionário abaixo
    frases = [frase for frase in (_FRASES_DA_JANELA.get(situacao),
                                  _FRASES_DA_EDICAO_RAPIDA.get(resultado.get("edicao_rapida")))
              if frase]
    if not frases:
        return []
    # Da segunda frase em diante, maiúscula no começo: vêm depois de um ponto.
    texto = " ".join([frases[0]] + [frase[:1].upper() + frase[1:] for frase in frases[1:]])
    return [f"- **Janela preta:** {texto}"]


def _avisos(resultado: dict) -> list[str]:
    """O que torna estes números diferentes de uma medição normal."""
    avisos = []
    if not resultado["preparo"].get("detector_de_regioes"):
        avisos.append(
            "o detector de gravura e letra (modelo doclayout.onnx) NÃO carregou: faltou o "
            "arquivo modelos\\doclayout.onnx ou o onnxruntime. Sem ele, trocar de página e "
            "processar ficam mais rápidos que no programa com o detector, e estes números "
            "não se comparam com uma medição feita com ele.")
    energia = resultado["maquina"].get("energia") or {}
    if energia.get("na_tomada") is False:
        carga = f", com {energia['carga']} de carga" if energia.get("carga") else ""
        avisos.append(
            f"o computador estava na bateria{carga}. Notebook na bateria costuma andar mais "
            "devagar: para comparar máquinas, meça na tomada.")
    return avisos


def _frase(rotulo: str, medida: dict, varias: bool) -> str:
    """ "- **Rótulo:** X na primeira vez, Y de costume." (ou só X)."""
    primeira = segundos_por_extenso(medida["primeira"])
    if varias:
        return (f"- **{rotulo}:** {primeira} na primeira vez, "
                f"{segundos_por_extenso(medida['mediana'])} de costume.")
    return f"- **{rotulo}:** {primeira}."


def _frase_de_processar(nome: str, paginas: int, medida: dict, varias: bool) -> str:
    """Processar: o total e quanto dá por página."""
    rotulo = f"Processar {paginas} páginas em {nome}"
    primeira = medida["primeira"]
    texto = (f"- **{rotulo}:** {segundos_por_extenso(primeira)}"
             f"{' na primeira vez' if varias else ''} "
             f"({segundos_por_extenso(primeira / max(paginas, 1))} por página)")
    if varias:
        mediana = medida["mediana"]
        texto += (f", {segundos_por_extenso(mediana)} de costume "
                  f"({segundos_por_extenso(mediana / max(paginas, 1))} por página)")
    return texto + "."


def _frase_de_trocas(resultado: dict, varias: bool) -> str:
    """Trocar de página: a média e a mais demorada."""
    resumo = resultado["resumo"]
    primeira = resultado["rodadas"][0]["trocas"]
    pagina_pior = primeira["pior_pagina"] + 1
    media = segundos_por_extenso(resumo["troca_media_s"]["primeira"])
    pior = segundos_por_extenso(resumo["troca_pior_s"]["primeira"])
    if varias:
        return (f"- **Trocar de página:** na primeira vez, a prévia de uma página nunca vista "
                f"ficou pronta em {media} em média, e a mais demorada (página {pagina_pior}) "
                f"levou {pior}. De costume: "
                f"{segundos_por_extenso(resumo['troca_media_s']['mediana'])} em média, e "
                f"{segundos_por_extenso(resumo['troca_pior_s']['mediana'])} a mais demorada.")
    quantas = len(primeira["tempos_s"])
    return (f"- **Trocar de página:** a prévia de uma página nunca vista ficou pronta em "
            f"{media} em média ({_plural(quantas, 'troca', 'trocas')}), e a mais demorada "
            f"(página {pagina_pior}) levou {pior}.")


def _tabela_da_maquina(resultado: dict, quando: datetime) -> list[str]:
    maquina, livro = resultado["maquina"], resultado["livro"]
    fisicos, logicos = maquina.get("nucleos_fisicos"), maquina.get("nucleos_logicos")
    nucleos = f"{fisicos} físicos, {logicos} lógicos" if fisicos else f"{logicos} lógicos"
    instalada, utilizavel = maquina.get("memoria_instalada_gb"), maquina.get("memoria_utilizavel_gb")
    if instalada and utilizavel:
        memoria = f"{formatar_gb(instalada)} ({formatar_gb(utilizavel)} disponíveis para o Windows)"
    else:
        memoria = formatar_gb(instalada or utilizavel)
    energia = (maquina.get("energia") or {}).get("texto", "não consegui ler")
    linhas = [
        "| O quê | Nesta máquina |",
        "|---|---|",
        f"| Computador | {maquina['computador']} |",
        f"| Processador | {maquina['processador']} |",
        f"| Núcleos | {nucleos} |",
        f"| Memória (RAM) | {memoria} |",
        f"| Placa de vídeo | {'; '.join(maquina.get('placas_de_video') or []) or 'não consegui ler'} |",
        f"| Windows | {maquina['windows']} |",
        f"| Energia | {energia} |",
        f"| Disco do livro | {livro.get('disco') or 'não consegui ler'} |",
        f"| Data e hora | {quando:%d/%m/%Y %H:%M} |",
    ]
    return linhas


def _tabela_das_rodadas(resultado: dict) -> list[str]:
    resumo, rodadas = resultado["resumo"], resultado["rodadas"]
    varias = len(rodadas) > 1
    paginas = len(resultado["configuracao"].get("lista_processadas") or [])
    linhas_da_tabela = [
        ("Abrir o livro", "abrir_total_s"),
        ("Abrir o livro: só o arquivo", "abrir_arquivo_s"),
        ("Abrir o livro: olhar todas as folhas", "abrir_analise_s"),
        ("Trocar de página: média", "troca_media_s"),
        ("Trocar de página: a mais demorada", "troca_pior_s"),
        (f"Processar {paginas} páginas em Mágico pro", "processar_magico_pro_s"),
        (f"Processar {paginas} páginas em Preto e branco", "processar_preto_e_branco_s"),
    ]
    if varias:
        cabecalho = ["O que"] + [f"{n}ª rodada" for n in range(1, len(rodadas) + 1)] + ["De costume"]
    else:
        cabecalho = ["O que", "Tempo"]
    linhas = ["| " + " | ".join(cabecalho) + " |", "|" + "---|" * len(cabecalho)]
    for rotulo, chave in linhas_da_tabela:
        celulas = [segundos_curto(v) for v in resumo[chave]["rodadas"]]
        if varias:
            celulas.append(segundos_curto(resumo[chave]["mediana"]))
        linhas.append(f"| {rotulo} | " + " | ".join(celulas) + " |")
    memorias = []
    for rodada in rodadas:
        medidas = [v for v in rodada["memoria_pico_mb"].values() if v is not None]
        memorias.append(formatar_mb(max(medidas)) if medidas else formatar_mb(None))
    linhas.append("| Memória máxima até o fim da rodada | " + " | ".join(memorias)
                  + (" | - |" if varias else " |"))
    return linhas


def montar_texto(resultado: dict) -> str:
    """O relatório em Markdown, em português comum: primeiro a frase, depois o
    número. Montado só a partir do resultado (o mesmo do .json), para poder
    ser refeito depois sem medir de novo."""
    maquina, livro = resultado["maquina"], resultado["livro"]
    configuracao, preparo = resultado["configuracao"], resultado["preparo"]
    resumo, rodadas = resultado["resumo"], resultado["rodadas"]
    versoes = resultado.get("versoes") or {}
    varias = len(rodadas) > 1
    quando = datetime.fromisoformat(resultado["quando"])
    lista_trocas = configuracao.get("lista_trocas") or []
    lista_processadas = configuracao.get("lista_processadas") or []
    paginas_processadas = len(lista_processadas)
    do_livro = descrever_livro(livro)

    t: list[str] = [f"# Teste de velocidade: {maquina['computador']}", ""]

    if resultado["rapido"]:
        t += ["> **TESTE RÁPIDO: estes números NÃO valem como medição.** Ele só confere que "
              "o teste funciona do começo ao fim, com um livro pequeno e poucas repetições.",
              ""]
    for aviso in _avisos(resultado):
        t += [f"> **Atenção:** {aviso}", ""]

    if livro.get("recortado"):
        sobre_o_livro = f"as {livro['paginas']} primeiras páginas de {livro['arquivo']}"
    else:
        sobre_o_livro = (f"{livro['arquivo']} ({do_livro}, "
                         f"{formatar_numero(livro['tamanho_mb'], 1)} MB)")
    t += [f"Medido em {quando:%d/%m/%Y} às {quando:%H:%M}, no computador "
          f"{maquina['computador']}. Livro: {sobre_o_livro}. O teste inteiro levou "
          f"{segundos_por_extenso(resultado['duracao_total_s'])}.", ""]

    # --- o resultado, em frases -------------------------------------------
    t += ["## Quanto demora", ""]
    if varias:
        t += [f"Cada coisa foi medida {len(rodadas)} vezes. **Na primeira vez** é o que o "
              "Kaique sente ao abrir um livro pela primeira vez. **De costume** é o valor do "
              f"meio entre as {len(rodadas)} vezes (a mediana): não é puxado nem pela vez "
              "mais rápida nem pela mais lenta.", ""]
    else:
        t += ["Cada coisa foi medida uma vez só.", ""]
    t.append(_frase(f"Abrir o livro de {do_livro}", resumo["abrir_total_s"], varias))
    t.append(_frase_de_trocas(resultado, varias))
    for filtro in FILTROS_MEDIDOS:
        t.append(_frase_de_processar(NOMES_DOS_FILTROS[filtro], paginas_processadas,
                                     resumo[f"processar_{filtro}_s"], varias))
    pico, onde = resultado["memoria"]["pico_mb"], resultado["memoria"]["onde"]
    if pico is None:
        t.append("- **Memória máxima usada:** não deu para medir neste computador.")
    else:
        t.append(f"- **Memória máxima usada:** {formatar_mb(pico)}"
                 + (f", {onde}." if onde else "."))
    t.append("")

    # --- a máquina e as rodadas -------------------------------------------
    t += ["## A máquina", ""] + _tabela_da_maquina(resultado, quando) + [""]
    t += ["## Rodada a rodada", ""] + _tabela_das_rodadas(resultado) + [""]
    t += ["Os números crus (cada troca de página, cada etapa, a memória depois de cada "
          "etapa) estão no arquivo .json de mesmo nome.", ""]

    # --- como foi medido --------------------------------------------------
    adiantadas = configuracao.get("paginas_adiantadas", 3)
    nome_do_filtro = NOMES_DOS_FILTROS.get(configuracao.get("filtro_do_livro"),
                                           configuracao.get("filtro_do_livro"))
    t += [
        "## Como foi medido",
        "",
        "Tudo pelas mesmas funções que o programa usa, na mesma ordem, sem abrir janela.",
        "",
        "- **Abrir o livro** = `abrir_pdf` + `info_paginas` + `assinatura_do_arquivo` (o que "
        "`JanelaPrincipal.abrir_livro` faz com o arquivo escolhido) e depois "
        "`TarefaAnalise.run`, que chama `analisar_projeto`: a análise de todas as folhas "
        f"(lombada, ângulo, bordas, cor e alertas), a {configuracao.get('dpi_analise')} DPI. "
        "Opções: as que a tela \"O que fazer\" já traz marcadas (dividir, limpar, endireitar, "
        f"cortar as bordas), com o filtro {nome_do_filtro}. Fica de fora o tempo em que o "
        "Kaique está na tela \"O que fazer\", e gravar o projeto na lista de projetos (o "
        "teste não mexe na lista do programa).",
        f"- **Trocar de página** = `GerenciadorPrevias.pegar` + `pre_carregar`, as duas "
        "chamadas que a tela de conferir faz ao virar a página "
        f"(`TelaConferir._atualizar_previa`), com o mesmo adiantamento das {adiantadas} "
        "páginas seguintes, na qualidade de prévia \"Rápida\" "
        f"({configuracao.get('dpi_previa')} DPI, a padrão). Cada prévia passa por "
        "`renderizar_pagina`: ler a folha, cortar, endireitar, achar gravura e letra e "
        f"aplicar o {nome_do_filtro}. O tempo vai do pedido até a prévia ficar pronta. Entre "
        "uma troca e outra o teste espera o programa terminar de adiantar as páginas "
        "seguintes, como o Kaique, que olha a página antes de passar. Páginas: "
        f"{_lista_de_paginas(lista_trocas)}.",
        "- **Processar** = `TarefaProcessar.run`, que chama `processar` (o botão "
        "\"Confirmar e processar\"): dividir, cortar, endireitar, achar gravura e letra, "
        f"filtro e gravar o PDF, a {configuracao.get('dpi_saida')} DPI, nas páginas "
        f"{_intervalo_de_paginas(lista_processadas)} (as do meio do livro). As outras "
        "páginas ficam marcadas como apagadas, que é como o programa deixa uma página de "
        "fora. O PDF sai numa pasta temporária, apagada no fim.",
        "- **Memória** = o maior uso de memória do processo do teste, medido pelo próprio "
        "Windows. Não conta a tela do programa.",
        "- **Detector de gravura e letra** (modelo doclayout.onnx): "
        + ("carregado." if preparo.get("detector_de_regioes") else "**NÃO carregou.**"),
        "- **Antes de medir**, o teste faz o mesmo aquecimento que o programa faz ao ligar "
        f"(`aquecer_dependencias_pesadas`): levou {segundos_por_extenso(preparo.get('aquecimento_s'))}, "
        "e não entra nos tempos acima.",
        *_linha_da_janela_preta(resultado),
        "",
        "## O que este teste não mede",
        "",
        "- A tela desenhando: a faixa de miniaturas (que roda em segundo plano logo depois "
        "de abrir o livro e disputa o leitor de PDF com as primeiras prévias), os cartões de "
        "filtro e o desenho da prévia. \"Trocar de página\" é o tempo até a prévia ficar "
        "pronta, não até ela aparecer pintada.",
        "- A aba \"Onde cortar\", que mostra a folha crua, sem processamento, e é bem mais "
        "rápida.",
        "- Disco frio de verdade: se o livro acabou de ser copiado para o computador, o "
        "Windows pode já tê-lo na memória, e a primeira vez sai mais rápida do que ao abrir "
        "um livro parado no disco há dias.",
        "",
        "## Versões",
        "",
        " · ".join([
            f"Python {versoes.get('python', '?')}",
            f"PyMuPDF {versoes.get('pymupdf', '?')}",
            f"OpenCV {versoes.get('opencv', '?')}",
            f"numpy {versoes.get('numpy', '?')}",
            f"onnxruntime {versoes.get('onnxruntime', '?')}",
            f"PySide6 {versoes.get('pyside6', '?')}",
            "empacotado (.exe)" if versoes.get("empacotado") else "rodando pelo Python",
            f"teste de velocidade versão {resultado.get('versao_do_teste', VERSAO_DO_TESTE)}",
        ]),
        "",
    ]
    return "\n".join(t)


def gravar_resultados(resultado: dict, base: Path) -> dict[str, Path]:
    """Grava o relatório nos três formatos (relatorio.gravar: .md, .html,
    .pdf) e os números crus em .json. Devolve {formato: caminho}; se o PDF
    não sair, a chave "pdf" não vem (o .md e o .html saem mesmo assim)."""
    import relatorio

    base = Path(base)
    arquivos = relatorio.gravar(montar_texto(resultado), base)
    caminho_json = base.with_name(base.name + ".json")
    caminho_json.write_text(json.dumps(resultado, ensure_ascii=False, indent=2),
                            encoding="utf-8")
    arquivos["json"] = caminho_json
    return arquivos


def _resumo_para_o_terminal(resultado: dict) -> str:
    """O começo do relatório (avisos e as frases de "Quanto demora"), sem a
    marcação do Markdown, para mostrar no fim da medição."""
    texto = montar_texto(resultado).split("## A máquina")[0]
    linhas = []
    for linha in texto.splitlines():
        linha = linha.replace("**", "").replace("`", "")
        if linha.startswith("# ") or linha.startswith("## "):
            linha = linha.lstrip("# ").upper()
        elif linha.startswith("> "):
            linha = linha[2:]
        linhas.append(linha)
    return "\n".join(linhas).strip()


def _gravar_erro(base: Path, mensagem: str, detalhe: str, maquina: dict | None) -> Path | None:
    """Quando o teste para no meio, deixa um arquivo dizendo por quê. No
    notebook do Kaique ninguém técnico está olhando o terminal."""
    texto = (f"O teste de velocidade parou.\n\n{mensagem}\n\n"
             f"Máquina: {json.dumps(maquina or {}, ensure_ascii=False)}\n\n"
             f"Detalhe técnico:\n{detalhe}\n")
    for destino in (base.with_name(base.name + "-ERRO.txt"),
                    Path.home() / "Documents" / (base.name + "-ERRO.txt")):
        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(texto, encoding="utf-8")
            return destino
        except OSError:
            continue
    return None


# ---------------------------------------------------------------------------
# o notebook não pode dormir no meio da medição (item 0.6)
# ---------------------------------------------------------------------------

# Os pedidos de SetThreadExecutionState, com os valores da documentação da
# Microsoft (não mudam).
_ES_CONTINUOUS = 0x80000000       # o pedido vale até ser desfeito, não uma vez só
_ES_SYSTEM_REQUIRED = 0x00000001  # não suspender o computador
_ES_DISPLAY_REQUIRED = 0x00000002  # não apagar a tela


def _pedir_ao_windows(estado: int) -> bool:
    """Chama SetThreadExecutionState(estado). True se o Windows aceitou; False
    se não deu (fora do Windows, por exemplo). Nunca levanta."""
    try:
        import ctypes

        funcao = ctypes.windll.kernel32.SetThreadExecutionState
        funcao.argtypes = [ctypes.c_uint32]
        funcao.restype = ctypes.c_uint32
        return bool(funcao(estado))
    except Exception:  # noqa: BLE001 - sem o pedido a medição segue
        return False


@contextlib.contextmanager
def computador_acordado(pedir: Callable[[int], bool] = _pedir_ao_windows):
    """Enquanto o bloco roda, o Windows não suspende o computador nem apaga a
    tela por falta de uso. Devolve (no `as`) se o Windows aceitou o pedido.

    Por quê: a medição leva de 15 minutos a mais de meia hora sem ninguém
    mexer no computador - as instruções do notebook pedem isso. Para o
    Windows, processador trabalhando não é uso: só teclado, mouse e este
    pedido contam. Sem ele, um notebook com "suspender depois de 10 minutos"
    dormiria no meio da medição, e a única rodada no notebook do Kaique se
    perderia. A tela acesa deixa quem voltar ver o progresso.

    O pedido vale só para este programa, enquanto ele roda: acabou o bloco
    (mesmo por erro), ele é desfeito; se o programa fechar no meio, o Windows
    desfaz sozinho. Nada disto entra nos números medidos. Arriscado mudar:
    tirar _ES_CONTINUOUS (sem ele o pedido não dura) ou chamar isto fora da
    linha principal (o pedido é da linha que chamou, e acaba com ela).
    """
    ligado = pedir(_ES_CONTINUOUS | _ES_SYSTEM_REQUIRED | _ES_DISPLAY_REQUIRED)
    try:
        yield ligado
    finally:
        if ligado:
            pedir(_ES_CONTINUOUS)


# ---------------------------------------------------------------------------
# um clique dentro da janela preta não pode pausar a medição (item 0.6)
# ---------------------------------------------------------------------------

# O modo da entrada da janela preta (GetStdHandle, GetConsoleMode,
# SetConsoleMode), com os valores da documentação da Microsoft (não mudam).
_STD_INPUT_HANDLE = -10 & 0xFFFFFFFF  # ((DWORD)-10): a entrada, o teclado da janela
_ENABLE_QUICK_EDIT_MODE = 0x0040      # o modo de edição rápida
_ENABLE_EXTENDED_FLAGS = 0x0080       # sem ele, o Windows não mexe no bit de cima

# O que edicao_rapida_desligada devolve e o .json guarda em "edicao_rapida".
# Cada uma tem a sua frase no relatório (_FRASES_DA_EDICAO_RAPIDA).
SITUACOES_DA_EDICAO_RAPIDA = ("desligado", "ja_desligado", "sem_janela", "falhou")


def _entrada_da_janela_preta():
    """(kernel32 com os tipos declarados, a entrada da janela preta), prontos
    para GetConsoleMode e SetConsoleMode. Pode levantar: quem chama cuida.

    Arriscado mexer: os tipos. Um kernel32 só daqui (WinDLL), e não o
    ctypes.windll.kernel32 que o processo inteiro divide, para os tipos
    declarados aqui não mudarem os de outra biblioteca; e HANDLE declarado,
    para o identificador não ser cortado em 64 bits (ver _pico_pelo_windows).
    """
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetStdHandle.argtypes = [wintypes.DWORD]
    kernel32.GetStdHandle.restype = wintypes.HANDLE
    kernel32.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel32.GetConsoleMode.restype = wintypes.BOOL
    kernel32.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.SetConsoleMode.restype = wintypes.BOOL
    return kernel32, kernel32.GetStdHandle(_STD_INPUT_HANDLE)


def _ler_modo_da_janela_preta() -> int | None:
    """O modo da entrada da janela preta agora (GetConsoleMode), ou None se o
    teste não recebe o teclado de uma janela preta (chamado por outro
    programa, entrada vinda de arquivo) ou se a chamada falhar. Nunca
    levanta."""
    try:
        import ctypes
        from ctypes import wintypes

        kernel32, entrada = _entrada_da_janela_preta()
        modo = wintypes.DWORD(0)
        if not kernel32.GetConsoleMode(entrada, ctypes.byref(modo)):
            return None
        return int(modo.value)
    except Exception:  # noqa: BLE001 - sem o modo, a medição segue
        return None


def _mudar_modo_da_janela_preta(modo: int) -> bool:
    """SetConsoleMode(modo) na entrada da janela preta. True se o Windows
    respondeu que aceitou. Nunca levanta."""
    try:
        kernel32, entrada = _entrada_da_janela_preta()
        return bool(kernel32.SetConsoleMode(entrada, modo & 0xFFFFFFFF))
    except Exception:  # noqa: BLE001
        return False


@contextlib.contextmanager
def edicao_rapida_desligada(ler: Callable[[], int | None] = _ler_modo_da_janela_preta,
                            mudar: Callable[[int], bool] = _mudar_modo_da_janela_preta):
    """Enquanto o bloco roda, um clique dentro da janela preta não pausa o
    teste. Devolve (no `as`) uma de SITUACOES_DA_EDICAO_RAPIDA:

    - "desligado": o modo de edição rápida foi desligado (o Windows confirmou);
    - "ja_desligado": já estava desligado; nada foi mexido;
    - "sem_janela": o teste não recebe o teclado de uma janela preta (foi
      chamado por outro programa, por exemplo): não há o que desligar;
    - "falhou": o Windows não deixou desligar.

    Por quê: na janela preta clássica do Windows a edição rápida vem ligada, e
    um clique dentro da janela começa a marcar texto. Enquanto houver texto
    marcado, o Windows segura o programa na próxima vez que ele escrever na
    janela, até alguém apertar uma tecla - e o teste escreve o progresso o
    tempo todo. O relógio seguiria andando com a medição parada, e o tempo
    medido sairia maior sem ninguém perceber. Na rodada única no notebook do
    Kaique, isso estragaria os números.

    Só a edição rápida muda: o resto do modo fica como estava (o Ctrl+C
    continua funcionando). No fim do bloco - mesmo por erro ou Ctrl+C - o modo
    de antes volta, antes de gravar o relatório e antes do "Aperte Enter para
    fechar" (ver despedir), e a janela volta a deixar marcar e copiar o texto.
    O modo é só desta janela: nada fica gravado no Windows, e se o programa
    fechar no meio ele some com a janela. Nada disto entra nos números
    medidos. Os parâmetros existem para o teste automático; o uso normal é
    edicao_rapida_desligada(), sem nenhum.

    Conferido no código aberto da janela clássica (o conhost, do repositório
    microsoft/terminal): o clique só começa a marcar texto se a edição rápida
    estiver ligada ou se já houver texto marcado; com ela desligada, o clique
    vira um aviso de mouse que o teste nunca lê. Numa janela clássica de
    verdade (PC do Samuel, 25/09/2026), aberta pelo .bat e direto, o modo lido
    passou de 0x1F7 para 0x1B7 durante o bloco e voltou a 0x1F7 no fim, também
    quando o bloco terminou com erro. O clique em si não deu para simular sem
    usar o mouse de verdade: a janela confere se o botão está apertado.

    O que NÃO é impedido (visto no mesmo código): o "Marcar" e o "Selecionar
    tudo" do menu da janela (o ícone no canto de cima > Editar), segurar a
    barra de rolagem e as teclas Pause e Ctrl+S ainda seguram o programa. Por
    isso as instruções do notebook continuam pedindo para não clicar na
    janela e não usar o notebook.

    Arriscado mudar:
    - tirar _ENABLE_EXTENDED_FLAGS do modo novo: sem ele o Windows ignora o
      pedido, e o clique volta a pausar;
    - confiar só na resposta de SetConsoleMode: a janela clássica às vezes
      responde "não" e muda assim mesmo (quando o modo tem uma combinação que
      ela considera errada). Por isso vale o que GetConsoleMode diz DEPOIS, e o
      modo de antes volta no fim sempre que houve tentativa;
    - se o modo lido vier sem _ENABLE_EXTENDED_FLAGS (outro programa mudou o
      modo sem ele), o Windows não diz como a edição rápida estava: ela é
      desligada mesmo assim e, no fim, volta o número lido - nesse caso raro a
      edição rápida (e a inserção de texto) podem ficar desligadas nessa
      janela até ela fechar.
    """
    try:
        antes = ler()
    except Exception:  # noqa: BLE001 - sem o modo, a medição segue
        antes = None
    if antes is None:
        yield "sem_janela"
        return
    if (antes & _ENABLE_EXTENDED_FLAGS) and not (antes & _ENABLE_QUICK_EDIT_MODE):
        yield "ja_desligado"
        return

    novo = (antes & ~_ENABLE_QUICK_EDIT_MODE) | _ENABLE_EXTENDED_FLAGS
    try:
        aceitou = bool(mudar(novo))
    except Exception:  # noqa: BLE001
        aceitou = False
    try:
        depois = ler()
    except Exception:  # noqa: BLE001
        depois = None
    if depois is None:
        desligado = aceitou  # não deu para conferir: vale a resposta à mudança
    else:
        desligado = bool(depois & _ENABLE_EXTENDED_FLAGS) and not (depois & _ENABLE_QUICK_EDIT_MODE)

    try:
        yield "desligado" if desligado else "falhou"
    finally:
        try:
            mudar(antes)
        except Exception:  # noqa: BLE001 - devolver é cortesia; nunca derruba o teste
            pass


# ---------------------------------------------------------------------------
# em que janela o teste roda: a clássica, o Terminal novo ou nenhuma (item 0.6)
# ---------------------------------------------------------------------------
#
# A medição é sempre na janela preta clássica do Windows (decisão do Samuel,
# 25/09/2026). Quem garante é o RODAR O TESTE.bat, que se reabre nela (ver
# TEXTO_DO_BAT em empacotar_teste_velocidade.py). Daqui, o teste só PERGUNTA
# ao Windows em que janela está e escreve a resposta no relatório e no .json,
# como prova. Não muda nada do que é medido.

# As classes de janela, com os nomes que o Windows usa (não mudam). A janela
# preta clássica é do conhost. Quando quem mostra o texto é outro programa,
# pelo pseudoconsole (o Terminal novo do Windows 11, por exemplo), o conhost
# fica escondido por trás e GetConsoleWindow devolve uma janela invisível
# dele, desta outra classe.
_SITUACAO_PELA_CLASSE = {
    "ConsoleWindowClass": "classica",
    "PseudoConsoleWindow": "terminal_novo",
}

# O que janela_do_teste devolve em "situacao" e o .json guarda em
# "janela". Cada uma tem a sua frase no relatório (_FRASES_DA_JANELA).
SITUACOES_DA_JANELA = ("classica", "terminal_novo", "sem_janela", "desconhecida")


def _janela_do_console():
    """GetConsoleWindow: o identificador da janela do console deste processo,
    ou 0/None se ele não tem console. Pode levantar: quem chama cuida.

    Arriscado mexer: o tipo da resposta. Um kernel32 só daqui (WinDLL), e não
    o ctypes.windll.kernel32 que o processo inteiro divide, para os tipos
    declarados aqui não mudarem os de outra biblioteca; e a resposta declarada
    HWND, para o identificador não ser cortado em 64 bits (ver
    _pico_pelo_windows).
    """
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetConsoleWindow.argtypes = []
    kernel32.GetConsoleWindow.restype = wintypes.HWND
    return kernel32.GetConsoleWindow()


def _classe_da_janela(janela) -> str | None:
    """GetClassNameW: o nome da classe da janela (ex.: "ConsoleWindowClass"),
    ou None se o Windows não disser (janela que já fechou, por exemplo). Pode
    levantar: quem chama cuida. 256 letras é o maior nome de classe que o
    Windows aceita. Arriscado mexer: os tipos, pelo mesmo motivo de
    _janela_do_console."""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetClassNameW.restype = ctypes.c_int
    nome = ctypes.create_unicode_buffer(256)
    letras = user32.GetClassNameW(janela, nome, len(nome))
    return nome.value if letras > 0 else None


def janela_do_teste(pegar_janela: Callable[[], object] = _janela_do_console,
                    pegar_classe: Callable[[object], str | None] = _classe_da_janela) -> dict:
    """Em que janela o teste está rodando, pela classe da janela que
    GetConsoleWindow devolve. Devolve {"situacao": ..., "classe": ...}, com a
    situação uma de SITUACOES_DA_JANELA:

    - "classica": a janela preta clássica do Windows (ConsoleWindowClass);
    - "terminal_novo": o Terminal novo do Windows (PseudoConsoleWindow, a
      janela escondida do pseudoconsole; outro programa que mostre a janela
      preta do mesmo jeito, como o terminal do VS Code, também cai aqui);
    - "sem_janela": o processo não tem janela de console (foi chamado por
      outro programa sem console, por exemplo);
    - "desconhecida": outra classe, ou o Windows não respondeu.

    "classe" é o nome que o Windows deu (a prova crua, para o .json), ou None
    quando não houve janela ou resposta. Uma janela clássica ESCONDIDA (outro
    programa abriu o teste com a janela oculta) também conta como clássica:
    o que vale é quem cuida da janela preta, e não se ela aparece.

    Nunca levanta: qualquer falha vira "desconhecida", e a medição segue. Só
    pergunta; não mexe em nada. Os parâmetros existem para o teste
    automático (as chamadas do Windows de mentira); o uso normal é
    janela_do_teste(), sem nenhum. Seguro mudar: nada aqui entra nos números.
    Arriscado mudar: os nomes das classes em _SITUACAO_PELA_CLASSE.
    """
    try:
        janela = pegar_janela()
        if not janela:
            return {"situacao": "sem_janela", "classe": None}
        classe = pegar_classe(janela)
        if not isinstance(classe, str) or not classe:
            return {"situacao": "desconhecida", "classe": None}
        return {"situacao": _SITUACAO_PELA_CLASSE.get(classe, "desconhecida"), "classe": classe}
    except Exception:  # noqa: BLE001 - sem a resposta, a medição segue
        return {"situacao": "desconhecida", "classe": None}


# ---------------------------------------------------------------------------
# o terminal
# ---------------------------------------------------------------------------


class Progresso:
    """A linha de progresso no terminal: uma linha só, reescrita no lugar.

    Sem terminal de verdade (saída mandada para arquivo) não dá para reescrever
    a linha; aí sai uma linha nova a cada INTERVALO_SEM_TERMINAL_S, para o
    arquivo não virar milhares de linhas. Empacotado sem console
    (sys.stdout None) fica calado - um print ali derrubaria o teste.
    """

    INTERVALO_S = 0.2
    INTERVALO_SEM_TERMINAL_S = 10.0

    def __init__(self, saida=None) -> None:
        self.saida = saida if saida is not None else sys.stdout
        self.terminal = bool(self.saida is not None and hasattr(self.saida, "isatty")
                             and self.saida.isatty())
        # A linha nunca passa da largura da janela: se quebrasse, o "\r" só
        # voltaria ao começo da última parte e a linha viraria uma escada.
        self.LARGURA = max(40, min(118, shutil.get_terminal_size((120, 20)).columns - 1))
        self._tamanho = 0
        self._ultima = 0.0
        self._inicio = time.monotonic()

    def mostrar(self, texto: str) -> None:
        """Atualiza a linha de progresso (no máximo 5 vezes por segundo)."""
        if self.saida is None:
            return
        agora = time.monotonic()
        intervalo = self.INTERVALO_S if self.terminal else self.INTERVALO_SEM_TERMINAL_S
        if agora - self._ultima < intervalo:
            return
        self._ultima = agora
        linha = f"[{_relogio(agora - self._inicio)}] {texto}"[: self.LARGURA]
        try:
            if self.terminal:
                self.saida.write("\r" + linha.ljust(self._tamanho))
                self.saida.flush()
                self._tamanho = len(linha)
            else:
                print(linha, file=self.saida, flush=True)
        except Exception:  # noqa: BLE001 - terminal que falha não para a medição
            pass

    def dizer(self, texto: str) -> None:
        """Uma linha que fica (apaga a linha de progresso antes)."""
        if self.saida is None:
            return
        try:
            if self.terminal and self._tamanho:
                self.saida.write("\r" + " " * self._tamanho + "\r")
                self._tamanho = 0
            print(texto, file=self.saida, flush=True)
        except Exception:  # noqa: BLE001
            pass


def _acertar_o_terminal() -> None:
    """Acento que o terminal não sabe mostrar vira "?", em vez de derrubar o
    teste no meio de uma medição de 15 minutos.

    Com a saída mandada para um arquivo ou outro programa (não é terminal), o
    Windows escreveria em cp1252 e o "á" chegaria estragado do outro lado;
    ali a saída passa a ser UTF-8. No terminal de verdade o Python já escreve
    com acento certo e nada muda.
    """
    for fluxo in (sys.stdout, sys.stderr):
        try:
            if fluxo is None or not hasattr(fluxo, "reconfigure"):
                continue
            if fluxo.isatty():
                fluxo.reconfigure(errors="replace")
            else:
                fluxo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass


def _ler_argumentos(argv: list[str] | None) -> argparse.Namespace:
    analisador = argparse.ArgumentParser(
        prog="teste_velocidade",
        description="Mede quanto o Editor de Impressão demora para abrir um livro de "
                    f"{FOLHAS_DO_LIVRO} páginas, trocar de página e processar "
                    f"{PAGINAS_PROCESSADAS} páginas.")
    analisador.add_argument(
        "livro", nargs="?",
        help=f"o PDF a medir (sem ele: {NOME_DO_LIVRO} ao lado do programa, ou em "
             "gabarito\\velocidade\\)")
    analisador.add_argument(
        "--preparar", action="store_true",
        help=f"grava {NOME_DO_LIVRO} (as {FOLHAS_DO_LIVRO} primeiras páginas do Marial do "
             "acervo) e sai")
    analisador.add_argument(
        "--original",
        help="com --preparar: de onde copiar as páginas (padrão: o Marial do acervo)")
    analisador.add_argument(
        "--rapido", action="store_true",
        help=f"só confere que o teste funciona ({RAPIDO_RODADAS} rodada, {RAPIDO_FOLHAS} "
             f"páginas, {RAPIDO_TROCAS} trocas, {RAPIDO_PAGINAS} páginas processadas): os "
             "números NÃO valem como medição")
    analisador.add_argument(
        "--saida",
        help="pasta onde gravar o relatório (padrão: relatorios\\velocidade\\, ou "
             "resultados\\ ao lado do .exe)")
    return analisador.parse_args(argv)


def _preparar(argumentos: argparse.Namespace, pasta: Path, congelado: bool,
              progresso: Progresso) -> int:
    """--preparar: grava o livro de teste e sai."""
    destino = (pasta / NOME_DO_LIVRO if congelado
               else pasta / "gabarito" / "velocidade" / NOME_DO_LIVRO)
    origem = Path(argumentos.original) if argumentos.original else ORIGINAL_DO_LIVRO
    progresso.dizer(f"Copiando as {FOLHAS_DO_LIVRO} primeiras páginas de:\n  {origem}")
    try:
        gravou = preparar_livro(origem, destino, FOLHAS_DO_LIVRO)
    except ErroNaMedicao as erro:
        progresso.dizer(str(erro))
        return 2
    tamanho = destino.stat().st_size / 1024 / 1024
    situacao = "Gravado" if gravou else "Já existia (não refiz)"
    progresso.dizer(f"{situacao}: {destino} ({formatar_numero(tamanho, 1)} MB)")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Um comando, sem perguntar nada: acha o livro, mede, grava o relatório.
    Sai com 0 (deu certo), 1 (a medição parou), 2 (faltou o livro) ou 130
    (interrompido com Ctrl+C). Quem chama é executar(), que no fim cuida da
    janela preta do .exe empacotado."""
    _acertar_o_terminal()
    argumentos = _ler_argumentos(argv)
    congelado = bool(getattr(sys, "frozen", False))
    pasta = pasta_do_programa()
    progresso = Progresso()

    if argumentos.preparar:
        return _preparar(argumentos, pasta, congelado, progresso)

    livro, procurados = escolher_livro(argumentos.livro, pasta)
    if livro is None:
        progresso.dizer("Não achei o livro de teste. Procurei em:")
        for lugar in procurados:
            progresso.dizer(f"  {lugar}")
        progresso.dizer(f"Ponha o {NOME_DO_LIVRO} ao lado deste programa, ou diga onde ele "
                        "está: teste_velocidade caminho\\do\\livro.pdf")
        return 2

    quando = datetime.now()
    progresso.dizer("Teste de velocidade do Editor de Impressão"
                    + (" (TESTE RÁPIDO: os números NÃO valem como medição)"
                       if argumentos.rapido else ""))
    progresso.dizer(f"Livro: {livro}")
    maquina = dados_da_maquina()
    progresso.dizer(f"Máquina: {maquina['computador']}, {maquina['processador']}, "
                    f"{formatar_gb(maquina['memoria_instalada_gb'] or maquina['memoria_utilizavel_gb'])}"
                    f", {maquina['energia']['texto']}")
    base = pasta_de_resultados(pasta, congelado, argumentos.saida) / nome_base(
        maquina["computador"], quando, argumentos.rapido)
    # Em que janela o teste roda (a clássica, o Terminal novo ou nenhuma): só
    # vai para o relatório e o .json, como prova; não muda o que é medido e
    # nunca levanta (ver janela_do_teste).
    janela = janela_do_teste()

    temporaria = Path(tempfile.mkdtemp(prefix="editor_velocidade_"))
    try:
        # Sem ninguém mexer no computador por meia hora: o Windows não pode
        # suspender no meio (ver computador_acordado), e um clique dentro da
        # janela preta não pode pausar a medição (ver edicao_rapida_desligada).
        # Os dois são desfeitos ao sair deste bloco, mesmo por erro ou Ctrl+C:
        # antes de gravar o relatório e antes do "Aperte Enter para fechar".
        # Arriscado mudar: tirar rodar_medicao de dentro do bloco.
        with computador_acordado(), edicao_rapida_desligada() as edicao_rapida:
            resultado = rodar_medicao(livro, argumentos.rapido, temporaria, progresso,
                                      maquina, quando, edicao_rapida=edicao_rapida,
                                      janela=janela)
        try:
            arquivos = gravar_resultados(resultado, base)
        except OSError:
            # Pasta sem permissão de gravar: o resultado de 15 minutos não se
            # perde, vai para Documentos.
            base = Path.home() / "Documents" / base.name
            arquivos = gravar_resultados(resultado, base)
    except KeyboardInterrupt:
        progresso.dizer("\nTeste interrompido. Nenhum relatório foi gravado.")
        return 130
    except ErroNaMedicao as erro:
        progresso.dizer(f"\nO teste parou: {erro}")
        onde = _gravar_erro(base, str(erro), traceback.format_exc(), maquina)
        if onde:
            progresso.dizer(f"O que aconteceu ficou anotado em: {onde}")
        return 1
    except Exception as erro:  # noqa: BLE001 - vira mensagem e arquivo, nunca só um rastro
        progresso.dizer(f"\nO teste parou por um problema inesperado ({type(erro).__name__}).")
        onde = _gravar_erro(base, "Problema inesperado.", traceback.format_exc(), maquina)
        if onde:
            progresso.dizer(f"O detalhe ficou anotado em: {onde}")
        return 1
    finally:
        shutil.rmtree(temporaria, ignore_errors=True)

    progresso.dizer("")
    progresso.dizer(_resumo_para_o_terminal(resultado))
    progresso.dizer("")
    progresso.dizer("Relatório gravado em:")
    for formato in ("md", "html", "pdf", "json"):
        if formato in arquivos:
            progresso.dizer(f"  {arquivos[formato]}")
    if "pdf" not in arquivos:
        progresso.dizer("  (o PDF do relatório não saiu; o .md e o .html saíram)")
    return 0


# ---------------------------------------------------------------------------
# empacotado: a janela preta não pode fechar sozinha (item 0.6)
# ---------------------------------------------------------------------------
#
# Com dois cliques no .exe, a janela preta é do próprio programa e fecha no
# instante em que ele termina: ninguém veria o resultado nem onde ele foi
# gravado. Por isso, empacotado, o teste termina com uma frase para o Kaique
# e, quando a janela fecharia junto, espera o Enter - depois de jogar fora as
# teclas apertadas durante a medição, para um Enter antigo não responder no
# lugar do Kaique (ver esvaziar_o_teclado). Pelo RODAR O TESTE.bat (o que as
# instruções mandam abrir) quem segura a janela é o "pause" do .bat, que
# também a segura se o programa cair de um jeito que o Python não pega.


def mensagem_do_fim(codigo: int) -> str:
    """A última frase da janela preta, conforme o teste terminou (o código de
    saída de main: 0 deu certo, 1 parou, 2 faltou o livro, 130 interrompido)."""
    if codigo == 0:
        return "Terminou. O resultado está na pasta resultados."
    if codigo == 2:
        return "O teste não começou: não achei o livro de teste (veja acima)."
    if codigo == 130:
        return "O teste foi interrompido antes do fim. Nenhum resultado foi gravado."
    return "O teste parou antes do fim. O motivo está escrito acima."


def _sozinho_no_console() -> bool:
    """True quando este programa é o único ligado à janela preta: foi aberto
    com dois cliques no .exe, e a janela fecha junto com ele.

    Aberto pelo RODAR O TESTE.bat, ou digitado num terminal, o cmd também está
    ligado à janela: ela não fecha quando o teste termina, e esperar o Enter
    aqui seria pedir duas vezes. Sem janela nenhuma (a conta dá 0) ou fora do
    Windows: False.

    Arriscado mudar: a conta só dá 1 porque o pacote é em pasta (onedir), um
    processo só. No arquivo único (onefile) o PyInstaller roda dois processos
    na mesma janela, a conta nunca dá 1 e o Enter nunca seria esperado.
    """
    try:
        import ctypes

        lista = (ctypes.c_uint32 * 8)()
        funcao = ctypes.windll.kernel32.GetConsoleProcessList
        funcao.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
        funcao.restype = ctypes.c_uint32
        return funcao(lista, len(lista)) == 1
    except Exception:  # noqa: BLE001 - na dúvida, não espera
        return False


def _esvaziar_a_entrada_pelo_windows() -> bool:
    """FlushConsoleInputBuffer na entrada da janela preta (a mesma de
    GetConsoleMode, ver _entrada_da_janela_preta): joga fora as teclas e os
    cliques guardados que ninguém leu. True se o Windows respondeu que
    esvaziou; sem janela preta (a entrada não é o teclado de uma janela), ele
    responde que não. Pode levantar: quem chama cuida.

    Arriscado mexer: os tipos (ver _entrada_da_janela_preta).
    """
    from ctypes import wintypes

    kernel32, entrada = _entrada_da_janela_preta()
    kernel32.FlushConsoleInputBuffer.argtypes = [wintypes.HANDLE]
    kernel32.FlushConsoleInputBuffer.restype = wintypes.BOOL
    return bool(kernel32.FlushConsoleInputBuffer(entrada))


def esvaziar_o_teclado(esvaziar: Callable[[], bool] = _esvaziar_a_entrada_pelo_windows) -> bool:
    """Joga fora as teclas guardadas na janela preta. True se o Windows
    esvaziou; False sem janela preta ou se não deu. Nunca levanta: sem
    esvaziar, a despedida segue do mesmo jeito.

    Por quê: tecla apertada numa janela preta fica guardada até alguém ler, e
    o teste não lê o teclado durante a medição. Um Enter apertado ali (o
    Kaique mexendo no notebook, por exemplo) sobrava para o fim e respondia na
    hora ao "Aperte Enter para fechar" de despedir: a janela fechava no
    instante em que o teste terminava, sem dar tempo de ler o "Terminou" (os
    arquivos de resultado ficam gravados do mesmo jeito). Visto no PC do
    Samuel (26/09/2026), num console sem janela: com um Enter guardado, a
    leitura do Enter voltou em 0,04 s; esvaziada a entrada, ela esperou.

    O pause do RODAR O TESTE.bat já se protegia sozinho: ele mesmo descarta o
    que foi digitado antes dele (visto no mesmo teste: com um "x" guardado,
    o pause esperou, e a tecla sumiu). Esvaziar aqui não muda nada para ele.

    Só joga fora o que ninguém leu; o Ctrl+C não fica guardado (o Windows o
    entrega na hora) e continua funcionando. O parâmetro existe para o teste
    automático; o uso normal é esvaziar_o_teclado(), sem nenhum.
    """
    try:
        return bool(esvaziar())
    except Exception:  # noqa: BLE001 - sem esvaziar, a despedida segue
        return False


def despedir(codigo: int, *, congelado: bool | None = None, sozinho: bool | None = None,
             entrada=None, saida=None, esvaziar: Callable[[], bool] | None = None) -> bool:
    """Empacotado: joga fora as teclas apertadas durante a medição
    (esvaziar_o_teclado), escreve a última frase (mensagem_do_fim) e, se a
    janela for fechar junto com o programa, espera o Enter. Devolve True se
    esperou.

    Rodando pelo Python não faz nada, nem mexe no teclado: quem roda pelo
    Python está num terminal que não fecha, e as teclas guardadas nele podem
    ser o próximo comando que a pessoa já digitou. Nunca levanta, e nunca
    prende o programa sem ninguém para apertar Enter: sem janela (sys.stdin ou
    sys.stdout None) ou com a entrada que não é terminal (execução automática,
    entrada vinda de arquivo), não espera. Só roda depois da medição: a
    medição em si nunca pergunta nada. Os parâmetros existem para o teste
    automático (`esvaziar` troca a chamada ao Windows; None é a de verdade);
    o uso normal é despedir(codigo).

    Arriscado mudar: esvaziar DEPOIS da última frase, ou só quando for
    esperar o Enter - um Enter apertado no meio da medição fecharia a janela.
    """
    if congelado is None:
        congelado = bool(getattr(sys, "frozen", False))
    saida = sys.stdout if saida is None else saida
    if not congelado or saida is None:
        return False
    # Antes de tudo: um Enter apertado durante a medição responderia na hora
    # ao "Aperte Enter para fechar" abaixo (ver esvaziar_o_teclado).
    esvaziar_o_teclado(esvaziar or _esvaziar_a_entrada_pelo_windows)
    entrada = sys.stdin if entrada is None else entrada
    try:
        esperar = bool(entrada is not None and entrada.isatty()
                       and (_sozinho_no_console() if sozinho is None else sozinho))
    except Exception:  # noqa: BLE001 - entrada fechada ou estranha: não espera
        esperar = False
    try:
        print("", file=saida)
        print(mensagem_do_fim(codigo) + (" Aperte Enter para fechar." if esperar else ""),
              file=saida, flush=True)
        if esperar:
            entrada.readline()
    except (Exception, KeyboardInterrupt):  # noqa: BLE001 - fechar é o que se queria
        pass
    return esperar


def executar(argv: list[str] | None = None) -> int:
    """O que roda ao abrir o programa: main() e depois despedir(), em todos
    os finais - deu certo, parou, faltou o livro, Ctrl+C, ou um erro que
    main() não pegou (este vai para a tela como rastro, e a janela espera do
    mesmo jeito, em vez de sumir sem dizer nada).

    A exceção é a saída do argparse (--help, opção digitada errada): só se
    chega nela digitando opções, num terminal ou pelo .bat, que não fecham
    sozinhos - e nenhuma frase do fim serve ali ("Terminou" depois do --help
    seria mentira). Sai sem despedida.
    """
    try:
        codigo = main(argv)
    except SystemExit as saida:  # o argparse sai assim
        return saida.code if isinstance(saida.code, int) else (0 if saida.code is None else 1)
    except KeyboardInterrupt:  # Ctrl+C fora da medição (main já cuida do de dentro)
        codigo = 130
    except Exception:  # noqa: BLE001 - o rastro fica na tela; a janela não some
        traceback.print_exc()
        codigo = 1
    despedir(codigo)
    return codigo


if __name__ == "__main__":
    raise SystemExit(executar())
