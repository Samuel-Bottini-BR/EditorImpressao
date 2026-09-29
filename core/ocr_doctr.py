"""Ponte até o docTR (pelo OnnxTR): acha as PALAVRAS e as LINHAS de texto de uma página (item 1.3).

O QUE FAZ
    Roda o detector "fast_base" do docTR, pela biblioteca OnnxTR (a versão do
    docTR que roda com o onnxruntime, sem PyTorch), DENTRO do programa (Python
    3.14, .venv). Só a DETECÇÃO: não lê o texto (a transcrição é da Fase 7).

      1. carrega o modelo uma vez (modelos\\doctr\\rep_fast_base-1b89ebf9.onnx,
         42 MB; ~1 s), na primeira página;
      2. para cada página, devolve as caixas das palavras e as linhas (as
         palavras juntadas pelo próprio montador de linhas do docTR), em
         pontos da imagem enviada;
      3. fechar() solta o modelo da memória.

    Decisão do Samuel (29/09/2026): de fábrica, o docTR fast_base e o Kraken
    ficam ligados na detecção; onde discordam, a página vai para "Para revisar".

    Uso:
        with DetectorDoctr() as detector:
            for pagina in paginas:             # uma por vez (regra da memória)
                r = detector.segmentar(pagina) # BGR, como o resto do programa
                if not r.disponivel:
                    avisar(r.motivo)           # português, para a tela
                else:
                    ... r.linhas, r.palavras   # core.ocr_comum.ResultadoOCR

AS MESMAS OPÇÕES DA COMPARAÇÃO DO 1.3 (28/09/2026)
    A pesquisa de treino (docs/pesquisa/treinar-ocr-e-detector.md, 4.3) viu
    que opções diferentes do "preditor" mudam muito as caixas. Aqui elas
    ficam FIXAS e escritas (OPCOES_DO_PREDITOR, LIMIARES), iguais às que o
    OnnxTR 0.9.0 usou na comparação (relatorios/fase1-1.3-comparacao-ocr-
    2026-09-28/scripts/rodar_onnxtr.py, configuração "D2"): a página inteira
    entra de uma vez, o OnnxTR a reduz para 1024 x 1024 por dentro mantendo a
    proporção, com preenchimento dos dois lados; caixas retas; limiares 0,1.
    Com isso, as 22 páginas do 1.3 dão as mesmas palavras e linhas da
    comparação (tests/test_ocr_doctr.py).

ONDE FICA O MODELO
    modelos\\doctr\\ (fora do git, como o doclayout.onnx). O OnnxTR baixaria
    o modelo da internet sozinho na primeira vez, mas o programa instalado no
    notebook do Kaique não pode depender disso: aqui o caminho é sempre um
    arquivo local, e o OnnxTR nunca é chamado com endereço de internet.
    Empacotado, o arquivo vai para _internal\\modelos\\doctr\\ (o mesmo
    caminho relativo à raiz do código, como os outros modelos: ver
    empacotar.modelos_do_programa, que ainda NÃO inclui este; vem na ligação).
    O arquivo é conferido pela soma SHA-256 ao carregar: modelo danificado
    vira aviso, não caixa errada.

NADA AQUI DERRUBA O PROGRAMA
    OnnxTR não instalado, modelo ausente ou danificado, imagem inválida, erro
    dentro do onnxruntime: segmentar() devolve um ResultadoOCR "indisponível"
    (linhas None), com o motivo em português (para a tela) e o detalhe técnico
    (para o erros.log, via logging). Nenhuma exceção sai daqui.

NÃO TRAVA A TELA, MAS BLOQUEIA
    ~1 s por página neste PC (Ryzen 7 5800H), com o modelo já carregado.
    segmentar() bloqueia até terminar: quem chamar tem de estar numa QThread.
    Este módulo não usa Qt (core/ não importa ui/). O docTR não para no meio
    de uma página; cancelar= só é consultado antes de começar.

AINDA NÃO ESTÁ LIGADO AO PROGRAMA (29/09/2026)
    Nem o pipeline, nem a tela, nem o empacotador usam este módulo ainda.

O QUE É SEGURO MUDAR
    Os textos das mensagens; o lugar do modelo (CAMINHO_MODELO) se o arquivo
    for junto.

O QUE É ARRISCADO MUDAR
    - OPCOES_DO_PREDITOR e LIMIARES: mudam as caixas (ver acima). Mudou, tem
      de refazer a comparação do 1.3.
    - A conversão BGR -> RGB antes do detector: a rede olha as cores (a média
      e o desvio de cada canal são diferentes); mandar trocado muda as caixas.
    - O montador de linhas usa um método interno do OnnxTR
      (DocumentBuilder._resolve_lines). Por isso a versão do OnnxTR está
      travada no requirements.txt (0.9.0); trocar a versão pede rodar
      tests/test_ocr_doctr.py com o modelo presente.
    - Forçar o processador (CPUExecutionProvider): com o onnxruntime para
      placa de vídeo instalado, o OnnxTR mudaria de aparelho sozinho, e o
      resultado pode mudar um pouco. A comparação foi no processador.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from core.ocr_comum import MOTOR_DOCTR, LinhaOCR, PalavraOCR, ResultadoOCR, indisponivel, retangulo

_log = logging.getLogger(__name__)

ARQUITETURA = "fast_base"
NOME_DO_MODELO = "rep_fast_base-1b89ebf9.onnx"
CAMINHO_MODELO = Path(__file__).resolve().parent.parent / "modelos" / "doctr" / NOME_DO_MODELO
# SHA-256 do arquivo que o OnnxTR 0.9.0 baixa de
# https://github.com/felixdittrich92/OnnxTR/releases/download/v0.0.1/rep_fast_base-1b89ebf9.onnx
# (os 8 primeiros caracteres estão no próprio nome do arquivo).
SOMA_DO_MODELO = "1b89ebf9b6a5e01eb21b1775efc54aab6dbf8c726dcce938e40ddcb91404b43a"
VERSAO_ONNXTR = "0.9.0"

# As opções da comparação do 1.3: os valores de fábrica do OnnxTR 0.9.0,
# escritos aqui para não mudarem se a biblioteca mudar o padrão.
OPCOES_DO_PREDITOR = {
    "assume_straight_pages": True,   # caixas retas
    "preserve_aspect_ratio": True,   # reduz para 1024 x 1024 sem deformar...
    "symmetric_pad": True,           # ...preenchendo dos dois lados
    "batch_size": 2,
}
LIMIARES = {"bin_thresh": 0.1, "box_thresh": 0.1}   # os do FAST no OnnxTR 0.9.0

_AVISO_SEM_BIBLIOTECA = ("O detector de texto docTR não está instalado (falta a biblioteca OnnxTR). "
                         "As outras funções continuam funcionando.")
_AVISO_SEM_MODELO = ("O detector de texto docTR não está instalado (falta o arquivo do modelo). "
                     "As outras funções continuam funcionando.")
_AVISO_DANIFICADO = ("O arquivo do detector de texto docTR está danificado. "
                     "É preciso reinstalar o programa.")
_AVISO_NAO_ABRIU = "O detector de texto docTR não conseguiu abrir."
_AVISO_PAGINA = "O detector de texto docTR não conseguiu ler esta página."
_AVISO_CANCELADO = "Cancelado."


def _importar_onnxtr():
    """Importa o OnnxTR só quando o detector é aberto (a importação leva 1 a 3 s).

    Devolve (fast_base, detection_predictor, EngineConfig, DocumentBuilder, versão).
    Separado numa função para os testes simularem "OnnxTR não instalado".
    """
    import onnxtr
    from onnxtr.models import detection_predictor
    from onnxtr.models.builder import DocumentBuilder
    from onnxtr.models.detection import fast_base
    from onnxtr.models.engine import EngineConfig

    return fast_base, detection_predictor, EngineConfig, DocumentBuilder, str(onnxtr.__version__)


def soma_sha256(caminho: Path) -> str:
    """A soma SHA-256 de um arquivo, lida em pedaços (não carrega os 42 MB de uma vez)."""
    soma = hashlib.sha256()
    with open(caminho, "rb") as arquivo:
        for pedaco in iter(lambda: arquivo.read(1 << 20), b""):
            soma.update(pedaco)
    return soma.hexdigest()


class DetectorDoctr:
    """O detector fast_base do docTR. Carrega na primeira página e serve o livro inteiro.

    Uma página por vez (uma tranca protege o modelo). Pode ser usado de uma
    QThread. fechar() (ou "with") solta o modelo da memória (~200 MB com o
    onnxruntime).
    """

    def __init__(self, caminho_modelo: Path | str | None = None, *,
                 soma_esperada: str | None = SOMA_DO_MODELO) -> None:
        """caminho_modelo: o .onnx (None = CAMINHO_MODELO).
        soma_esperada: SHA-256 que o arquivo tem de ter (None = não conferir;
            só para um modelo treinado depois, na Fase 7).
        """
        self.caminho_modelo = Path(caminho_modelo) if caminho_modelo is not None else CAMINHO_MODELO
        self.soma_esperada = soma_esperada
        self.info: dict = {}                  # versão do OnnxTR, modelo, opções
        self.segundos_para_abrir: float = 0.0
        self._preditor = None
        self._montador = None
        self._falha_ao_abrir: ResultadoOCR | None = None
        self._tranca = threading.RLock()

    # ------------------------------------------------------------ abrir e fechar

    def __enter__(self) -> "DetectorDoctr":
        return self

    def __exit__(self, *_ignorado) -> None:
        self.fechar()

    @property
    def aberto(self) -> bool:
        return self._preditor is not None

    def _abrir(self) -> ResultadoOCR | None:
        """Carrega o modelo, se ainda não estiver carregado. None se deu certo, ou o aviso."""
        if self._preditor is not None:
            return None
        if self._falha_ao_abrir is not None:     # não tenta de novo a cada página
            return self._falha_ao_abrir
        inicio = time.perf_counter()
        caminho = self.caminho_modelo
        try:
            existe = caminho.is_file()
        except OSError:
            existe = False
        if not existe:
            self._falha_ao_abrir = indisponivel(MOTOR_DOCTR, _AVISO_SEM_MODELO,
                                                f"modelo não encontrado: {caminho}")
            return self._falha_ao_abrir
        try:
            fast_base, detection_predictor, EngineConfig, DocumentBuilder, versao = _importar_onnxtr()
        except Exception as erro:   # ImportError, ou uma dependência quebrada por dentro
            self._falha_ao_abrir = indisponivel(MOTOR_DOCTR, _AVISO_SEM_BIBLIOTECA,
                                                f"importar onnxtr: {type(erro).__name__}: {erro}")
            return self._falha_ao_abrir
        if self.soma_esperada:
            try:
                soma = soma_sha256(caminho)
            except OSError as erro:
                self._falha_ao_abrir = indisponivel(MOTOR_DOCTR, _AVISO_NAO_ABRIU,
                                                    f"não consegui ler {caminho}: {erro}")
                return self._falha_ao_abrir
            if soma != self.soma_esperada:
                self._falha_ao_abrir = indisponivel(
                    MOTOR_DOCTR, _AVISO_DANIFICADO,
                    f"soma de {caminho} é {soma}, esperada {self.soma_esperada}")
                return self._falha_ao_abrir
        try:
            # Só o processador, com as opções de fábrica do OnnxTR para ele.
            motor = EngineConfig(providers=[("CPUExecutionProvider", {"arena_extend_strategy": "kSameAsRequested"})])
            # str(): o caminho nunca tem "http", então o OnnxTR não tenta baixar nada.
            modelo = fast_base(model_path=str(caminho), engine_cfg=motor, **LIMIARES)
            self._preditor = detection_predictor(arch=modelo, **OPCOES_DO_PREDITOR)
            self._montador = DocumentBuilder()
        except Exception as erro:
            self._preditor = self._montador = None
            self._falha_ao_abrir = indisponivel(MOTOR_DOCTR, _AVISO_NAO_ABRIU,
                                                f"carregar {caminho}: {type(erro).__name__}: {erro}")
            return self._falha_ao_abrir
        if versao.lstrip("v") != VERSAO_ONNXTR:
            _log.warning("ocr_doctr: OnnxTR %s, a comparação do 1.3 usou o %s: as caixas podem mudar",
                         versao, VERSAO_ONNXTR)
        self.segundos_para_abrir = time.perf_counter() - inicio
        self.info = {"onnxtr": versao, "arquitetura": ARQUITETURA, "modelo": str(caminho),
                     "opcoes": dict(OPCOES_DO_PREDITOR, **LIMIARES)}
        _log.info("ocr_doctr: modelo carregado em %.1f s (%s)", self.segundos_para_abrir, self.info)
        return None

    def fechar(self) -> None:
        """Solta o modelo da memória. A próxima página carrega de novo."""
        with self._tranca:
            self._preditor = self._montador = None
            self._falha_ao_abrir = None

    # ------------------------------------------------------------ o que se pede

    def segmentar(self, imagem: np.ndarray | str | Path, *, ordem: str = "BGR",
                  cancelar: Callable[[], bool] | None = None) -> ResultadoOCR:
        """Acha as palavras e as linhas de texto de UMA página.

        imagem: uint8, altura x largura (cinza) ou altura x largura x 3 (BGR,
            como o resto do programa; ordem="RGB" para RGB). Um 4.º canal é
            ignorado. Ou o caminho de um arquivo de imagem.
        cancelar: função sem argumentos, consultada antes de começar; True dá
            "Cancelado." (o docTR não para no meio de uma página, ~1 s).
        Nunca levanta exceção (ver docstring do módulo).
        """
        try:
            return self._segmentar(imagem, ordem, cancelar)
        except Exception as erro:   # rede de segurança: nada sai daqui como exceção
            _log.exception("ocr_doctr: erro inesperado")
            return indisponivel(MOTOR_DOCTR, _AVISO_PAGINA, f"{type(erro).__name__}: {erro}")

    def _segmentar(self, imagem, ordem: str, cancelar) -> ResultadoOCR:
        if _cancelado(cancelar):
            return indisponivel(MOTOR_DOCTR, _AVISO_CANCELADO, "cancelado por quem chamou")
        rgb, problema = _para_rgb(imagem, ordem)
        if rgb is None:
            return indisponivel(MOTOR_DOCTR, _AVISO_PAGINA, problema)
        with self._tranca:
            falha = self._abrir()
            if falha is not None:
                return falha
            altura, largura = rgb.shape[:2]
            inicio = time.perf_counter()
            try:
                caixas = np.asarray(self._preditor([rgb])[0], dtype=np.float64)
                palavras, linhas = _palavras_e_linhas(caixas, largura, altura, self._montador)
            except Exception as erro:
                return indisponivel(MOTOR_DOCTR, _AVISO_PAGINA, f"detectar: {type(erro).__name__}: {erro}")
            segundos = time.perf_counter() - inicio
        return ResultadoOCR(MOTOR_DOCTR, linhas, palavras=palavras, segundos=segundos,
                            largura=largura, altura=altura, extra=dict(self.info))


def _cancelado(cancelar: Callable[[], bool] | None) -> bool:
    if cancelar is None:
        return False
    try:
        return bool(cancelar())
    except Exception as erro:   # a função de cancelar quebrou: trata como cancelar
        _log.warning("ocr_doctr: a função cancelar() falhou (%s)", erro)
        return True


def _para_rgb(imagem, ordem: str) -> tuple[np.ndarray | None, str]:
    """A página como o docTR espera: uint8, RGB, altura x largura x 3. (None, motivo) se não der."""
    if isinstance(imagem, (str, Path)):
        caminho = Path(imagem)
        try:
            # imdecode + fromfile: funciona com acento no caminho (o imread não).
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


def _palavras_e_linhas(caixas: np.ndarray, largura: int, altura: int,
                       montador) -> tuple[list[PalavraOCR], list[LinhaOCR]]:
    """Caixas do docTR (relativas, N x 5: x0, y0, x1, y1, confiança) -> palavras e linhas em pontos.

    As linhas saem do montador do próprio docTR (mesma altura; o vão entre
    palavras quebra a linha), exatamente como na comparação do 1.3
    (rodar_onnxtr.linhas_de_palavras): a caixa da linha é o retângulo que
    envolve as suas palavras. Arriscado mudar: é a regra da comparação.
    """
    if caixas.ndim != 2 or len(caixas) == 0:
        return [], []
    if caixas.shape[1] < 5:
        raise ValueError(f"caixas em formato inesperado: {caixas.shape}")
    relativas = caixas[:, :4].astype(np.float64)
    palavras = [PalavraOCR((float(c[0] * largura), float(c[1] * altura),
                            float(c[2] * largura), float(c[3] * altura)), float(c[4]))
                for c in caixas]
    linhas = []
    for indices in montador._resolve_lines(relativas):
        grupo = relativas[indices]
        x0, y0 = grupo[:, 0].min() * largura, grupo[:, 1].min() * altura
        x1, y1 = grupo[:, 2].max() * largura, grupo[:, 3].max() * altura
        linhas.append(LinhaOCR(retangulo(x0, y0, x1, y1), confianca=float(caixas[indices, 4].mean()),
                               palavras=len(indices)))
    return palavras, linhas


def segmentar_pagina(imagem: np.ndarray | str | Path, **opcoes) -> ResultadoOCR:
    """Atalho para UMA página só: carrega o modelo, detecta e solta (paga ~1 s de carregar).

    Para um livro, use DetectorDoctr diretamente e mantenha-o aberto.
    """
    with DetectorDoctr() as detector:
        return detector.segmentar(imagem, **opcoes)
