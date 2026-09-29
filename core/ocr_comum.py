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
      - de_kraken(): converte o ResultadoKraken da ponte do Kraken neste tipo,
        SEM mudar a ponte do Kraken (ver "Proposta" abaixo).

    Só ACHA ONDE ESTÁ O TEXTO. Nenhum campo guarda texto transcrito (Fase 7).

    Os nomes batem com os do ResultadoKraken de propósito (linhas, motivo,
    detalhe_tecnico, segundos, largura, altura, disponivel, precisa_revisar):
    quem já lê o Kraken lê este tipo sem mudar nada, e cada linha tem
    .poligono como a LinhaKraken.

PROPOSTA (não aplicada, 29/09/2026)
    A ponte do Kraken continua devolvendo o ResultadoKraken dela. Quando a
    comparação automática for ligada, a proposta é a ponte do Kraken passar a
    devolver ResultadoOCR direto (motor="kraken", perdidas=falhas_contorno +
    linhas_sem_contorno, extra={"regioes": ...}) e o de_kraken() sair daqui.
    Até lá, de_kraken() faz a ponte entre os dois.

NÃO USA Qt, NÃO IMPORTA ui/, NÃO LEVANTA EXCEÇÃO
    São só tipos de dados. de_kraken() nunca levanta: um objeto estranho vira
    um ResultadoOCR "indisponível" com o motivo.

O QUE É SEGURO MUDAR
    Acrescentar campos novos com valor padrão no fim das classes.

O QUE É ARRISCADO MUDAR
    - Os nomes dos campos que coincidem com o ResultadoKraken (ver acima).
    - poligono em float32 (m, 2), pontos (x, y) na imagem ENVIADA à ponte (não
      na página do PDF): a comparação e o item 1.4 fazem máscara com eles.
"""

from __future__ import annotations

import logging
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


def de_kraken(resultado) -> ResultadoOCR:
    """Converte o ResultadoKraken (core/ocr_kraken.py) em ResultadoOCR.

    Não muda a ponte do Kraken; só lê os campos dela. perdidas =
    falhas_contorno + linhas_sem_contorno (a mesma regra do
    ResultadoKraken.precisa_revisar). Nunca levanta exceção.
    """
    try:
        if resultado.linhas is None:
            return ResultadoOCR(MOTOR_KRAKEN, None, motivo=resultado.motivo,
                                detalhe_tecnico=resultado.detalhe_tecnico)
        linhas = [LinhaOCR(np.asarray(l.poligono, np.float32).reshape(-1, 2),
                           linha_de_base=np.asarray(l.linha_de_base, np.float32).reshape(-1, 2))
                  for l in resultado.linhas]
        return ResultadoOCR(
            MOTOR_KRAKEN, linhas, palavras=None,
            perdidas=int(resultado.falhas_contorno) + int(resultado.linhas_sem_contorno),
            segundos=float(resultado.segundos), largura=int(resultado.largura),
            altura=int(resultado.altura), extra={"regioes": dict(resultado.regioes or {})})
    except Exception as erro:   # objeto estranho: aviso, nunca exceção
        return indisponivel(MOTOR_KRAKEN, "O resultado do detector de linhas do Kraken veio num formato "
                                          "que o programa não entendeu.",
                            f"{type(erro).__name__}: {erro}")
