"""Ponte até o Tesseract: acha as PALAVRAS e as LINHAS de texto de uma página (item 1.3).

O QUE FAZ
    Roda o tesseract.exe (programa à parte, da UB Mannheim, licença
    Apache-2.0) numa página e lê a saída hOCR: as caixas das linhas e das
    palavras, com a confiança de cada palavra. Só ACHA ONDE ESTÁ O TEXTO; o
    texto lido pelo Tesseract é jogado fora (a transcrição é da Fase 7).

    Decisão do Samuel (29/09/2026): o Tesseract fica INSTALADO, mas DESLIGADO
    de fábrica na detecção (os ligados são o docTR e o Kraken). A comparação
    do 1.3 mostrou que ele pisa em moldura e retrato e não acha o título da
    Horas 11. A ponte tem de funcionar para quem ligar.

    Uso:
        motor = MotorTesseract()
        for pagina in paginas:                            # uma por vez
            r = motor.segmentar(pagina, idioma="ita", dpi=300)
            if not r.disponivel:
                avisar(r.motivo)                          # português, para a tela
            else:
                ... r.linhas, r.palavras                  # core.ocr_comum.ResultadoOCR

    Cada página abre um tesseract.exe novo (como o pytesseract fazia na
    comparação); não há processo para fechar.

AS MESMAS OPÇÕES DA COMPARAÇÃO DO 1.3 (28/09/2026, configuração "T1")
    Tesseract 5.4.0; modelo "tessdata_best" do idioma do livro, da pasta
    modelos\\tessdata\\; "--psm 3" (a página inteira, divisão automática em
    blocos e linhas); "--dpi" só quando o scan tem 150 DPI ou mais (nos de
    "72 DPI", o número do arquivo não é o de verdade e o Tesseract estima
    sozinho); saída hOCR; página gravada como PNG. O comando é o mesmo que o
    pytesseract montou na comparação, menos o último "hocr" (que lá não fazia
    nada: esse arquivo de configuração não existe em modelos\\tessdata\\).
    Linhas = os elementos ocr_line, ocr_textfloat, ocr_header e ocr_caption
    do hOCR. Sem o filtro de confiança do Internet Archive (a "T2" da
    comparação): cada linha leva a confiança média das palavras, e quem
    quiser filtrar filtra depois.

    O modelo muda pouco as LINHAS (muda a confiança), segundo a comparação;
    o idioma padrão é o latim (IDIOMA_PADRAO).

ONDE FICA O TESSERACT
    lugares_do_tesseract(): ao lado do programa instalado ({app}\\tesseract\\),
    na raiz do código (tesseract\\, fora do git), onde o winget instala
    (C:\\Program Files\\Tesseract-OCR\\), a instalação só do usuário, e o PATH.
    Os modelos (lugares_dos_modelos): no programa instalado,
    {app}\\tesseract\\tessdata\\ (o empacotar.py põe ali os seis idiomas da
    comparação, IDIOMAS_DO_INSTALADOR); no código, modelos\\tessdata\\ (fora
    do git).

NADA AQUI DERRUBA O PROGRAMA
    Tesseract ausente, modelo do idioma ausente, programa que morre, que
    passa do tempo, que não escreve a saída, hOCR ilegível, ou cancelado:
    segmentar() devolve um ResultadoOCR "indisponível" (linhas None), com o
    motivo em português (para a tela) e o detalhe técnico (para o erros.log,
    via logging). Nenhuma exceção sai daqui. O tesseract.exe que passou do
    tempo ou foi cancelado é FECHADO À FORÇA (só ele, nunca o programa).

NÃO TRAVA A TELA, MAS BLOQUEIA
    0,5 a 9 s por página neste PC (a tabela do Opus Majus 256 é a mais
    lenta). segmentar() bloqueia até a resposta: quem chamar tem de estar
    numa QThread. Não usa Qt (core/ não importa ui/). cancelar= é consultado
    a cada 0,2 s.

AINDA NÃO ESTÁ LIGADO AO PROGRAMA (29/09/2026)
    Nem o pipeline, nem a tela, nem o empacotador usam este módulo ainda.

O QUE É SEGURO MUDAR
    Os textos das mensagens; TEMPO_POR_PAGINA; a ordem dos lugares onde se
    procura o tesseract.exe; IDIOMA_PADRAO (o modelo mexe pouco nas linhas).

O QUE É ARRISCADO MUDAR
    - As opções do comando (_montar_comando), o DPI_MINIMO_INFORMADO e as
      CLASSES_DE_LINHA: são as da comparação; mudou, tem de refazer a
      comparação do 1.3 (tests/test_ocr_tesseract.py com o Tesseract presente).
    - Gravar a página como PNG sem perda (JPEG mudaria os pontos).
    - A conversão BGR -> RGB: o Tesseract converte para cinza pelos pesos
      de cada canal; trocado, o cinza muda.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from core.ocr_comum import (MOTOR_TESSERACT, LinhaOCR, PalavraOCR, ResultadoOCR, abrir_processo,
                             indisponivel, retangulo)

_log = logging.getLogger(__name__)

VERSAO_DA_COMPARACAO = "5.4.0"
IDIOMA_PADRAO = "lat"
PSM = 3
DPI_MINIMO_INFORMADO = 150
TEMPO_POR_PAGINA = 300.0   # segundos; a página mais lenta do 1.3 levou 9 s
CLASSES_DE_LINHA = frozenset({"ocr_line", "ocr_textfloat", "ocr_header", "ocr_caption"})

NOME_DO_PROGRAMA = "tesseract.exe" if os.name == "nt" else "tesseract"
PASTA_DOS_MODELOS = Path(__file__).resolve().parent.parent / "modelos" / "tessdata"   # no código
# Os seis idiomas da comparação do 1.3, que o instalador leva (decisão do
# Samuel, 29/09/2026). O empacotar.py confere que os seis existem.
IDIOMAS_DO_INSTALADOR = ("lat", "ita", "por", "fra", "eng", "script/Fraktur")

# Windows: sem janela preta de console; prioridade abaixo do normal.
_SEM_JANELA = 0x08000000
_PRIORIDADE_BAIXA = 0x00004000
# Idioma: "lat", "script/Fraktur", "ita+lat". Nada de espaço, aspas ou "..".
_IDIOMA_VALIDO = re.compile(r"^[A-Za-z0-9_\-]+(/[A-Za-z0-9_\-]+)?(\+[A-Za-z0-9_\-]+(/[A-Za-z0-9_\-]+)?)*$")

_AVISO_AUSENTE = ("O detector de texto Tesseract não está instalado. "
                  "As outras funções continuam funcionando.")
_AVISO_SEM_MODELO = ("O detector de texto Tesseract não tem o modelo deste idioma. "
                     "As outras funções continuam funcionando.")
_AVISO_NAO_ABRIU = "O detector de texto Tesseract não conseguiu abrir."
_AVISO_FALHOU = "O detector de texto Tesseract não conseguiu ler esta página."
_AVISO_DEMOROU = "O detector de texto Tesseract demorou demais e foi fechado."
_AVISO_RESPOSTA = "O detector de texto Tesseract respondeu algo que o programa não entendeu."
_AVISO_CANCELADO = "Cancelado."


def _raiz_do_codigo() -> Path:
    return Path(__file__).resolve().parent.parent


def lugares_do_tesseract() -> list[Path]:
    """Onde o tesseract.exe é procurado, em ordem.

    1. Ao lado do programa instalado ({app}\\tesseract\\tesseract.exe, quando
       o programa roda empacotado pelo PyInstaller): é onde o instalador vai pô-lo.
    2. Na raiz do código (tesseract\\, fora do git), para quem quiser deixar ali.
    3. Onde o winget/instalador da UB Mannheim põe: %ProgramFiles%\\Tesseract-OCR.
    4. A instalação só para o usuário: %LOCALAPPDATA%\\Programs\\Tesseract-OCR.
    5. O PATH do Windows.
    """
    lugares = []
    if getattr(sys, "frozen", False):
        lugares.append(Path(sys.executable).resolve().parent / "tesseract" / NOME_DO_PROGRAMA)
    lugares.append(_raiz_do_codigo() / "tesseract" / NOME_DO_PROGRAMA)
    for variavel, resto in (("ProgramFiles", ("Tesseract-OCR",)),
                            ("LOCALAPPDATA", ("Programs", "Tesseract-OCR"))):
        base = os.environ.get(variavel)
        if base:
            lugares.append(Path(base, *resto) / NOME_DO_PROGRAMA)
    no_path = shutil.which("tesseract")
    if no_path:
        lugares.append(Path(no_path))
    return lugares


def lugares_dos_modelos() -> list[Path]:
    """Onde a pasta tessdata é procurada, em ordem.

    1. Ao lado do programa instalado: {app}\\tesseract\\tessdata (empacotado).
    2. Na raiz do código: modelos\\tessdata (desenvolvimento; fora do git).
    """
    lugares = []
    if getattr(sys, "frozen", False):
        lugares.append(Path(sys.executable).resolve().parent / "tesseract" / "tessdata")
    lugares.append(PASTA_DOS_MODELOS)
    return lugares


def achar_pasta_dos_modelos() -> Path:
    """A primeira pasta de lugares_dos_modelos() que existe (ou a do código, se nenhuma existir)."""
    for pasta in lugares_dos_modelos():
        try:
            if pasta.is_dir():
                return pasta
        except OSError:
            continue
    return PASTA_DOS_MODELOS


def achar_tesseract() -> Path | None:
    """O primeiro tesseract.exe de lugares_do_tesseract() que existe, ou None."""
    for caminho in lugares_do_tesseract():
        try:
            if caminho.is_file():
                return caminho
        except OSError:
            continue
    return None


def modelos_que_faltam(idioma: str, pasta: Path) -> list[str]:
    """Os arquivos .traineddata do idioma ("ita+lat" = dois) que não estão na pasta."""
    return [parte for parte in idioma.split("+")
            if not (pasta / f"{parte}.traineddata").is_file()]


class MotorTesseract:
    """Chama o tesseract.exe, uma página por vez. Não guarda processo aberto.

    Pode ser usado de uma QThread (uma tranca garante uma página por vez).
    """

    def __init__(self, executavel: Path | str | None = None, *,
                 pasta_dos_modelos: Path | str | None = None,
                 comando: list[str] | None = None,
                 tempo_por_pagina: float = TEMPO_POR_PAGINA,
                 prioridade_baixa: bool = True) -> None:
        """executavel: o tesseract.exe (None = procurar em lugares_do_tesseract()).
        pasta_dos_modelos: a pasta tessdata (None = achar_pasta_dos_modelos()).
        comando: só para os testes - roda outro programa no lugar do tesseract.exe
            (os argumentos de sempre vão depois dele).
        """
        self.executavel = Path(executavel) if executavel is not None else None
        self.pasta_dos_modelos = (Path(pasta_dos_modelos) if pasta_dos_modelos is not None
                                  else achar_pasta_dos_modelos())
        self._comando_de_teste = list(comando) if comando else None
        self.tempo_por_pagina = tempo_por_pagina
        self.prioridade_baixa = prioridade_baixa
        self._versao: str | None = None
        self._tranca = threading.RLock()

    def __enter__(self) -> "MotorTesseract":
        return self

    def __exit__(self, *_ignorado) -> None:
        self.fechar()

    def fechar(self) -> None:
        """Nada a fechar (cada página abre e fecha o seu tesseract.exe); existe para
        o MotorTesseract ser usado do mesmo jeito que as outras pontes."""

    def _programa(self) -> tuple[list[str] | None, str]:
        """O começo do comando ([tesseract.exe]) ou (None, detalhe) se não houver."""
        if self._comando_de_teste:
            return self._comando_de_teste, ""
        exe = self.executavel if self.executavel is not None else achar_tesseract()
        if exe is None:
            return None, "tesseract.exe não encontrado em: " + ", ".join(str(p) for p in lugares_do_tesseract())
        try:
            if not exe.is_file():
                return None, f"tesseract.exe não encontrado: {exe}"
        except OSError as erro:
            return None, f"tesseract.exe inacessível: {exe} ({erro})"
        return [str(exe)], ""

    def versao(self) -> str | None:
        """A versão do tesseract.exe (ex.: "5.4.0.20240606"), ou None. Nunca levanta."""
        if self._versao is not None:
            return self._versao
        programa, _ = self._programa()
        if programa is None:
            return None
        try:
            saida = subprocess.run(programa + ["--version"], capture_output=True, timeout=30,
                                   creationflags=_SEM_JANELA if os.name == "nt" else 0)
            texto = (saida.stdout + saida.stderr).decode("utf-8", errors="replace")
            achado = re.search(r"tesseract\s+v?(\d+\.\d+\.\d+[\w.\-]*)", texto)
            self._versao = achado.group(1) if achado else None
        except (OSError, subprocess.SubprocessError) as erro:
            _log.warning("ocr_tesseract: não consegui ler a versão (%s)", erro)
            self._versao = None
        return self._versao

    # ------------------------------------------------------------ o que se pede

    def segmentar(self, imagem: np.ndarray | str | Path, *, idioma: str = IDIOMA_PADRAO,
                  dpi: float | None = None, ordem: str = "BGR",
                  cancelar: Callable[[], bool] | None = None) -> ResultadoOCR:
        """Acha as palavras e as linhas de texto de UMA página.

        imagem: uint8, altura x largura (cinza) ou altura x largura x 3 (BGR,
            como o resto do programa; ordem="RGB" para RGB). Um 4.º canal é
            ignorado. Ou o caminho de um arquivo de imagem (lido e regravado
            como PNG, do mesmo jeito que a página em memória).
        idioma: o modelo em modelos\\tessdata ("lat", "ita", "script/Fraktur",
            "ita+lat"...).
        dpi: a resolução de verdade da imagem; só é passada ao Tesseract a
            partir de 150 (regra da comparação). None = o Tesseract estima.
        cancelar: função sem argumentos, consultada a cada 0,2 s; True fecha o
            tesseract.exe e dá "Cancelado.".
        Nunca levanta exceção (ver docstring do módulo).
        """
        try:
            return self._segmentar(imagem, idioma, dpi, ordem, cancelar)
        except Exception as erro:   # rede de segurança: nada sai daqui como exceção
            _log.exception("ocr_tesseract: erro inesperado")
            return indisponivel(MOTOR_TESSERACT, _AVISO_FALHOU, f"{type(erro).__name__}: {erro}")

    def _segmentar(self, imagem, idioma: str, dpi, ordem: str, cancelar) -> ResultadoOCR:
        if not isinstance(idioma, str) or not _IDIOMA_VALIDO.match(idioma) or ".." in idioma:
            return indisponivel(MOTOR_TESSERACT, _AVISO_SEM_MODELO, f"idioma inválido: {idioma!r}")
        rgb, problema = _para_rgb(imagem, ordem)
        if rgb is None:
            return indisponivel(MOTOR_TESSERACT, _AVISO_FALHOU, problema)
        programa, detalhe = self._programa()
        if programa is None:
            return indisponivel(MOTOR_TESSERACT, _AVISO_AUSENTE, detalhe)
        faltam = modelos_que_faltam(idioma, self.pasta_dos_modelos)
        if faltam:
            return indisponivel(MOTOR_TESSERACT, _AVISO_SEM_MODELO,
                                f"faltam {faltam} em {self.pasta_dos_modelos}")
        altura, largura = rgb.shape[:2]
        with self._tranca, tempfile.TemporaryDirectory(prefix="tesseract-pagina-", ignore_cleanup_errors=True) as pasta:
            entrada = Path(pasta) / "pagina.png"
            ok, png = cv2.imencode(".png", np.ascontiguousarray(rgb[:, :, ::-1]))   # imencode quer BGR
            if not ok:
                return indisponivel(MOTOR_TESSERACT, _AVISO_FALHOU, "não consegui gravar a página como PNG")
            entrada.write_bytes(png.tobytes())
            base_da_saida = Path(pasta) / "saida"
            comando = programa + _montar_comando(entrada, base_da_saida, idioma, dpi, self.pasta_dos_modelos)
            inicio = time.perf_counter()
            resultado = self._rodar(comando, pasta, cancelar)
            segundos = time.perf_counter() - inicio
            if resultado is not None:
                return resultado
            arquivo_hocr = base_da_saida.with_suffix(".hocr")
            try:
                hocr = arquivo_hocr.read_bytes()
            except OSError as erro:
                return indisponivel(MOTOR_TESSERACT, _AVISO_RESPOSTA, f"o Tesseract não gravou {arquivo_hocr.name}: {erro}")
        try:
            palavras, linhas = ler_hocr(hocr)
        except ValueError as erro:
            return indisponivel(MOTOR_TESSERACT, _AVISO_RESPOSTA, f"hOCR ilegível: {erro}")
        return ResultadoOCR(MOTOR_TESSERACT, linhas, palavras=palavras, segundos=segundos,
                            largura=largura, altura=altura,
                            extra={"idioma": idioma, "psm": PSM,
                                   "dpi": _dpi_informado(dpi), "comando": comando[len(programa):]})

    def _rodar(self, comando: list[str], pasta: str, cancelar) -> ResultadoOCR | None:
        """Roda o tesseract.exe até o fim. None se saiu bem; senão, o aviso."""
        bandeiras = 0
        if os.name == "nt":
            bandeiras = _SEM_JANELA | (_PRIORIDADE_BAIXA if self.prioridade_baixa else 0)
        try:
            processo = abrir_processo(comando, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, cwd=pasta, creationflags=bandeiras)
        except OSError as erro:
            return indisponivel(MOTOR_TESSERACT, _AVISO_NAO_ABRIU, f"não consegui iniciar {comando[0]}: {erro}")
        # Ler as saídas em paralelo: o Tesseract pode escrever muito aviso, e o
        # cano cheio faria os dois processos esperarem um ao outro para sempre.
        saidas: dict[str, bytes] = {}
        leitores = [threading.Thread(target=_ler_tudo, args=(cano, saidas, nome), daemon=True)
                    for nome, cano in (("stdout", processo.stdout), ("stderr", processo.stderr))]
        for leitor in leitores:
            leitor.start()
        limite = time.monotonic() + self.tempo_por_pagina
        motivo = None
        while processo.poll() is None:
            if _cancelado(cancelar):
                motivo = (_AVISO_CANCELADO, "cancelado por quem chamou")
                break
            if time.monotonic() > limite:
                motivo = (_AVISO_DEMOROU, f"sem resposta em {self.tempo_por_pagina:.0f} s")
                break
            try:
                processo.wait(timeout=0.2)
            except subprocess.TimeoutExpired:
                pass
        if motivo is not None:
            _matar(processo)
        for leitor in leitores:
            leitor.join(timeout=5)
        erro_do_programa = saidas.get("stderr", b"").decode("utf-8", errors="replace").strip()[-800:]
        if motivo is not None:
            return indisponivel(MOTOR_TESSERACT, motivo[0], motivo[1])
        if processo.returncode != 0:
            return indisponivel(MOTOR_TESSERACT, _AVISO_FALHOU,
                                f"o Tesseract saiu com código {processo.returncode}: {erro_do_programa}")
        if erro_do_programa:
            _log.debug("ocr_tesseract: %s", erro_do_programa)
        return None


def _dpi_informado(dpi) -> int | None:
    """O DPI que vai para o Tesseract: só a partir de DPI_MINIMO_INFORMADO (regra da comparação)."""
    try:
        if dpi is not None and float(dpi) >= DPI_MINIMO_INFORMADO:
            return int(round(float(dpi)))
    except (TypeError, ValueError):
        pass
    return None


def _montar_comando(entrada: Path, base_da_saida: Path, idioma: str, dpi, pasta_dos_modelos: Path) -> list[str]:
    """Os argumentos depois do tesseract.exe, na ordem que o pytesseract usou na comparação.

    pytesseract.image_to_pdf_or_hocr(img, lang=idioma, extension="hocr",
    config="--tessdata-dir <pasta> --psm 3 [--dpi N]") rodava:
        tesseract <entrada> <saida> -l <idioma> -c tessedit_create_hocr=1
                  --tessdata-dir <pasta> --psm 3 [--dpi N] hocr
    O "hocr" do fim não é passado aqui: ele pedia o arquivo de configuração
    tessdata\\configs\\hocr, que não existe em modelos\\tessdata\\ (o Tesseract
    avisava "Can't open hocr" e seguia); quem liga o hOCR é o "-c".
    """
    argumentos = [str(entrada), str(base_da_saida), "-l", idioma, "-c", "tessedit_create_hocr=1",
                  "--tessdata-dir", pasta_dos_modelos.as_posix(), "--psm", str(PSM)]
    informado = _dpi_informado(dpi)
    if informado is not None:
        argumentos += ["--dpi", str(informado)]
    return argumentos


def _ler_tudo(cano, saidas: dict, nome: str) -> None:
    try:
        saidas[nome] = cano.read()
    except (OSError, ValueError):
        saidas[nome] = b""


def _matar(processo: subprocess.Popen) -> None:
    """Fecha à força o tesseract.exe (só ele)."""
    try:
        if processo.poll() is None:
            processo.kill()
        processo.wait(timeout=5)
    except (OSError, subprocess.TimeoutExpired) as erro:
        _log.warning("ocr_tesseract: não consegui fechar o tesseract.exe (%s)", erro)


def _cancelado(cancelar: Callable[[], bool] | None) -> bool:
    if cancelar is None:
        return False
    try:
        return bool(cancelar())
    except Exception as erro:   # a função de cancelar quebrou: trata como cancelar
        _log.warning("ocr_tesseract: a função cancelar() falhou (%s)", erro)
        return True


def _para_rgb(imagem, ordem: str) -> tuple[np.ndarray | None, str]:
    """A página em RGB uint8, altura x largura x 3 (cinza vira 3 canais iguais). (None, motivo) se não der."""
    if isinstance(imagem, (str, Path)):
        caminho = Path(imagem)
        try:
            bgr = cv2.imdecode(np.fromfile(str(caminho), np.uint8), cv2.IMREAD_COLOR)
        except (OSError, ValueError) as erro:
            return None, f"não consegui ler {caminho}: {erro}"
        if bgr is None:
            return None, f"imagem ilegível ou inexistente: {caminho}"
        return np.ascontiguousarray(bgr[:, :, ::-1]), ""
    if not isinstance(imagem, np.ndarray) or imagem.dtype != np.uint8 or imagem.size == 0:
        return None, f"imagem inválida: {getattr(imagem, 'dtype', type(imagem))} {getattr(imagem, 'shape', '')}"
    if ordem.upper() not in ("BGR", "RGB"):
        return None, f"ordem de cores desconhecida: {ordem!r}"
    if imagem.ndim == 2 or (imagem.ndim == 3 and imagem.shape[2] == 1):
        cinza = imagem.reshape(imagem.shape[0], imagem.shape[1])
        return np.ascontiguousarray(np.repeat(cinza[:, :, None], 3, axis=2)), ""
    if imagem.ndim != 3 or imagem.shape[2] not in (3, 4):
        return None, f"imagem inválida: {imagem.dtype} {imagem.shape}"
    tres = imagem[:, :, :3]
    if ordem.upper() == "BGR":
        tres = tres[:, :, ::-1]
    return np.ascontiguousarray(tres), ""


# ---------------------------------------------------------------- leitura do hOCR

_CAIXA = re.compile(r"bbox (-?\d+) (-?\d+) (-?\d+) (-?\d+)")
_CONFIANCA = re.compile(r"x_wconf (\d+)")


class _LeitorHocr(HTMLParser):
    """Junta, para cada linha do hOCR, a caixa e as palavras (caixa e confiança).

    Igual ao leitor da comparação do 1.3 (rodar_tesseract._LeitorHocr): uma
    palavra conta para a ÚLTIMA linha aberta. Acrescenta a caixa de cada palavra.
    """

    def __init__(self) -> None:
        super().__init__()
        self.linhas: list[dict] = []
        self.palavras: list[PalavraOCR] = []

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        classe = atributos.get("class") or ""
        titulo = atributos.get("title") or ""
        if classe in CLASSES_DE_LINHA:
            achado = _CAIXA.search(titulo)
            if achado is None:
                raise ValueError(f"linha sem caixa: {titulo[:100]!r}")
            self.linhas.append({"caixa": tuple(map(int, achado.groups())), "confiancas": []})
        elif classe == "ocrx_word":
            confianca = _CONFIANCA.search(titulo)
            caixa = _CAIXA.search(titulo)
            if caixa is not None:
                self.palavras.append(PalavraOCR(tuple(float(v) for v in caixa.groups()),
                                                float(confianca.group(1)) if confianca else None))
            if self.linhas and confianca:
                self.linhas[-1]["confiancas"].append(int(confianca.group(1)))


def ler_hocr(hocr: bytes | str) -> tuple[list[PalavraOCR], list[LinhaOCR]]:
    """hOCR do Tesseract -> (palavras, linhas). Levanta ValueError se não for hOCR."""
    texto = hocr.decode("utf-8", errors="replace") if isinstance(hocr, bytes) else hocr
    if "ocr_page" not in texto:
        raise ValueError(f"sem ocr_page: {texto[:120]!r}")
    leitor = _LeitorHocr()
    leitor.feed(texto)
    leitor.close()
    linhas = []
    for linha in leitor.linhas:
        x0, y0, x1, y1 = linha["caixa"]
        confiancas = linha["confiancas"]
        linhas.append(LinhaOCR(retangulo(x0, y0, x1, y1),
                               confianca=sum(confiancas) / len(confiancas) if confiancas else 0.0,
                               palavras=len(confiancas)))
    return leitor.palavras, linhas


def segmentar_pagina(imagem: np.ndarray | str | Path, **opcoes) -> ResultadoOCR:
    """Atalho para UMA página: o mesmo que MotorTesseract().segmentar(imagem, **opcoes)."""
    return MotorTesseract().segmentar(imagem, **opcoes)
