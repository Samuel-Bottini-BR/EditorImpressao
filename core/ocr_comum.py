"""O resultado comum dos detectores de texto (OCRs) do item 1.3 da Fase 1.

O QUE É
    Três OCRs vão dizer "aqui tem texto" na mesma página: o docTR
    (core/ocr_doctr.py), o Kraken (core/ocr_kraken.py) e o Tesseract
    (core/ocr_tesseract.py). A comparação automática entre eles (que vem
    depois: "onde discordam, a página vai para 'Para revisar'") precisa ler os
    três do mesmo jeito. Este módulo é esse jeito:

      - ResultadoOCR: o que cada ponte devolve para UMA página;
      - LinhaOCR: uma linha de texto (o contorno, em pontos da imagem enviada);
      - PalavraOCR: uma palavra (caixa reta), quando o OCR as dá;
      - para_dict() / de_dict(): o resultado em dicionário simples (JSON),
        para guardar num arquivo e ler de volta sem rodar o OCR de novo (o
        Kraken leva ~10 s por página).

    Só ACHA ONDE ESTÁ O TEXTO. Nenhum campo guarda texto transcrito (Fase 7).

    As três pontes devolvem este tipo direto (a do Kraken desde 29/09/2026;
    antes ela tinha um ResultadoKraken próprio, com os mesmos nomes).
    A comparação automática entre eles é core/ocr_comparar.py.

NÃO USA Qt, NÃO IMPORTA ui/, NÃO LEVANTA EXCEÇÃO
    São só tipos de dados.

O QUE É SEGURO MUDAR
    Acrescentar campos novos com valor padrão no fim das classes.

O QUE É ARRISCADO MUDAR
    - Os nomes dos campos: as três pontes e core/ocr_comparar.py os leem.
    - poligono em float32 (m, 2), pontos (x, y) na imagem ENVIADA à ponte (não
      na página do PDF): a comparação e o item 1.4 fazem máscara com eles.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
from dataclasses import dataclass, field

import numpy as np

_log = logging.getLogger(__name__)

MOTOR_DOCTR = "doctr"
MOTOR_KRAKEN = "kraken"
MOTOR_TESSERACT = "tesseract"


@dataclass(frozen=True)
class PalavraOCR:
    """Uma palavra achada, como caixa reta, em pontos da imagem enviada.

    caixa: (x0, y0, x1, y1), com x0 < x1 e y0 < y1.
    confianca: o quanto o OCR acha que ali é texto. A escala é do OCR:
        docTR de 0 a 1; Tesseract de 0 a 100 (confiança da leitura). None se
        o OCR não dá.
    """

    caixa: tuple[float, float, float, float]
    confianca: float | None = None


@dataclass(frozen=True)
class LinhaOCR:
    """Uma linha de texto achada, em pontos da imagem enviada.

    poligono: float32 (m, 2), o contorno da linha (m >= 3). No docTR e no
        Tesseract é o retângulo reto da linha (4 pontos); no Kraken, o
        contorno de verdade.
    confianca: média das palavras da linha, na escala do OCR (ver PalavraOCR).
        None quando o OCR não dá (Kraken).
    palavras: quantas palavras a linha tem (0 quando o OCR não separa palavras).
    linha_de_base: float32 (n, 2), a linha em que as letras assentam. Só o
        Kraken dá; None nos outros.
    """

    poligono: np.ndarray
    confianca: float | None = None
    palavras: int = 0
    linha_de_base: np.ndarray | None = None


@dataclass(frozen=True)
class ResultadoOCR:
    """O que uma ponte de OCR devolve para UMA página.

    motor: "doctr", "kraken" ou "tesseract".
    linhas: as linhas achadas; None = indisponível (ver motivo). Lista vazia
        é resposta válida ("não achei texto nesta página").
    palavras: as palavras, quando o OCR as dá (docTR, Tesseract); None no Kraken.
    perdidas: linhas que o OCR sabe que jogou fora (Kraken: "Polygonizer
        failed"). > 0 manda a página para "Para revisar".
    motivo: por que ficou indisponível, em português (para a tela). None se deu certo.
    detalhe_tecnico: o erro de verdade, para o erros.log (nunca para a tela).
    segundos: quanto o OCR levou na página (sem contar abrir o modelo/motor).
    largura, altura: da imagem que o OCR recebeu (é nela que estão os pontos).
    extra: informações do OCR (modelo, opções, versão), para o log e os testes.
    """

    motor: str
    linhas: list[LinhaOCR] | None
    palavras: list[PalavraOCR] | None = None
    perdidas: int = 0
    motivo: str | None = None
    detalhe_tecnico: str | None = None
    segundos: float = 0.0
    largura: int = 0
    altura: int = 0
    extra: dict = field(default_factory=dict)

    @property
    def disponivel(self) -> bool:
        return self.linhas is not None

    @property
    def precisa_revisar(self) -> bool:
        """O próprio OCR avisou que perdeu linhas nesta página."""
        return self.perdidas > 0


def indisponivel(motor: str, motivo: str, detalhe: str | None = None) -> ResultadoOCR:
    """Um ResultadoOCR "indisponível": o aviso vai para a tela, o detalhe para o log."""
    if detalhe:
        _log.warning("ocr_%s: %s (%s)", motor, motivo, detalhe)
    return ResultadoOCR(motor, None, motivo=motivo, detalhe_tecnico=detalhe)


def retangulo(x0: float, y0: float, x1: float, y1: float) -> np.ndarray:
    """O polígono (4 pontos, float32) de uma caixa reta, na ordem da comparação do 1.3."""
    return np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=np.float32)


def para_dict(resultado: ResultadoOCR) -> dict:
    """O resultado como dicionário simples, que o json grava (listas, números, textos)."""
    def linha(l: LinhaOCR) -> dict:
        d = {"poligono": np.asarray(l.poligono, np.float64).tolist(), "confianca": l.confianca,
             "palavras": int(l.palavras)}
        if l.linha_de_base is not None:
            d["linha_de_base"] = np.asarray(l.linha_de_base, np.float64).tolist()
        return d

    return {
        "motor": resultado.motor,
        "linhas": None if resultado.linhas is None else [linha(l) for l in resultado.linhas],
        "palavras": None if resultado.palavras is None else
        [{"caixa": list(p.caixa), "confianca": p.confianca} for p in resultado.palavras],
        "perdidas": int(resultado.perdidas), "motivo": resultado.motivo,
        "detalhe_tecnico": resultado.detalhe_tecnico, "segundos": float(resultado.segundos),
        "largura": int(resultado.largura), "altura": int(resultado.altura),
        "extra": resultado.extra,
    }


def de_dict(dados: dict) -> ResultadoOCR:
    """O contrário de para_dict(). Levanta KeyError/TypeError/ValueError se o dicionário
    estiver fora do formato (quem lê de arquivo deve tratar)."""
    def linha(d: dict) -> LinhaOCR:
        base = d.get("linha_de_base")
        return LinhaOCR(np.asarray(d["poligono"], np.float32).reshape(-1, 2), d.get("confianca"),
                        int(d.get("palavras", 0)),
                        None if base is None else np.asarray(base, np.float32).reshape(-1, 2))

    linhas = dados["linhas"]
    palavras = dados.get("palavras")
    return ResultadoOCR(
        str(dados["motor"]),
        None if linhas is None else [linha(d) for d in linhas],
        palavras=None if palavras is None else
        [PalavraOCR(tuple(float(v) for v in p["caixa"]), p.get("confianca")) for p in palavras],
        perdidas=int(dados.get("perdidas", 0)), motivo=dados.get("motivo"),
        detalhe_tecnico=dados.get("detalhe_tecnico"), segundos=float(dados.get("segundos", 0.0)),
        largura=int(dados.get("largura", 0)), altura=int(dados.get("altura", 0)),
        extra=dict(dados.get("extra") or {}))


# ---------------------------------------------------------------- abrir um OCR à parte

_TRANCA_DA_PASTA_DE_DLLS = threading.Lock()


def abrir_processo(comando: list[str], **opcoes) -> subprocess.Popen:
    """subprocess.Popen para um OCR que roda à parte (motor do Kraken, tesseract.exe).

    POR QUE EXISTE (achado em 29/09/2026, conferindo o programa empacotado):
    o PyInstaller marca a pasta _internal\\ do programa como "pasta de DLLs"
    (SetDllDirectoryW), e o Windows passa essa marca para os processos
    filhos. O motor do Kraken, aberto pelo programa empacotado, carregava o
    msvcp140.dll e o vcruntime140*.dll de _internal\\ (os que o PyInstaller
    trouxe para o próprio programa), e não os do Visual C++ oficial no
    System32, misturando versões. Aqui a marca é tirada só durante o Popen e
    posta de volta logo depois; e as pastas do programa empacotado saem do
    PATH do filho. Fora do programa empacotado, é um Popen comum.

    Arriscado mudar: a volta da marca no finally (sem ela, o próprio
    programa deixaria de achar as DLLs de _internal\\ que carrega depois).
    Pode levantar OSError (como o Popen); quem chama trata.
    """
    empacotado = bool(getattr(sys, "frozen", False)) and os.name == "nt"
    if not empacotado:
        return subprocess.Popen(comando, **opcoes)
    base = os.path.normcase(os.path.abspath(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))))
    caminhos = [p for p in os.environ.get("PATH", "").split(os.pathsep)
                if p and not os.path.normcase(os.path.abspath(p)).startswith(base)]
    opcoes.setdefault("env", {**os.environ, "PATH": os.pathsep.join(caminhos)})
    import ctypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    with _TRANCA_DA_PASTA_DE_DLLS:
        memoria = ctypes.create_unicode_buffer(32768)
        tamanho = kernel32.GetDllDirectoryW(32768, memoria)
        antes = memoria.value if tamanho else None
        if antes:
            kernel32.SetDllDirectoryW(None)
        try:
            return subprocess.Popen(comando, **opcoes)
        finally:
            if antes:
                kernel32.SetDllDirectoryW(antes)
