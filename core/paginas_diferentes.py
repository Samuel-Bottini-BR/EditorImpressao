"""Destacar as páginas diferentes das outras, igual ao ScanTailor (item 2.15, 20/10/2026).

O ScanTailor Advanced marca com um asterisco vermelho a miniatura da página
cujo número se afasta muito do das outras páginas do livro, e deixa ordenar
as páginas "pela diferença" (`src/core/DeviationProvider.h`, 163 linhas, e
`src/core/OrderByDeviationProvider.cpp`, v1.2.1). Três números, um por etapa:

- endireitar (`deskew/Settings.cpp`): o ângulo da página, em graus;
- caixa do conteúdo (`select_content/Settings.cpp`): a diagonal do conteúdo,
  em mm (conteúdo vazio = sem número, e aí a página CONTA como diferente:
  `isDeviant(..., true)` em `select_content/CacheDrivenTask.cpp`);
- margens (`page_layout/Settings.cpp`): a "diagonal" das margens, em mm:
  raiz((esq + dir)^2 + (cima + baixo)^2).

A conta (`DeviationProvider::isDeviant` e `update`), copiada aqui em Python
sem mudança: média e desvio-padrão (amostral, n - 1) dos números das páginas
que têm número; a página é diferente quando
    |valor - média| > max(coeficiente x desvio-padrão, limite% x média),
e nunca com menos de 3 páginas. Ajustes de fábrica do ScanTailor
(`ApplicationSettings.cpp`): endireitar 1,5 e 1%, conteúdo 0,35 e 1%,
margens 0,35 e 1%; destacar ligado.

No programa (decisão do layout: "Para revisar + filtro na grade"): a página
diferente ganha um aviso, que entra no "Para revisar" (agrupado pelo motivo)
e pinta a moldura laranja da miniatura. Hoje só o número do endireitar
existe neste ramo: a caixa do conteúdo (2.5) e as margens (2.4) estão no
ramo `fase2-caixa-conteudo`, ainda fora do `fase-1`; as contas delas já
estão aqui (valor_do_conteudo, valor_das_margens) para quando chegarem.
Não muda a imagem de nenhuma página.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Iterable
from dataclasses import dataclass

# Os ajustes de fábrica do ScanTailor (ApplicationSettings.cpp, linhas 18-24).
DESTACAR_DE_FABRICA = True


@dataclass(frozen=True)
class Ajuste:
    """Coeficiente (vezes o desvio-padrão) e limite (em % da média)."""

    coeficiente: float
    limite: float


ENDIREITAR = Ajuste(1.5, 1.0)      # DEFAULT_DESKEW_DEVIATION_COEF / _THRESHOLD
CONTEUDO = Ajuste(0.35, 1.0)       # DEFAULT_SELECT_CONTENT_DEVIATION_COEF / _THRESHOLD
MARGENS = Ajuste(0.35, 1.0)        # DEFAULT_MARGINS_DEVIATION_COEF / _THRESHOLD

SEM_NUMERO = math.nan              # o NAN do ScanTailor: "esta página não tem o número"


class Desvio:
    """DeviationProvider<K> do ScanTailor, em Python: um número por página
    (chave), e quais se afastam das outras. Igual ao original, linha a linha:
    a média e o desvio-padrão ignoram as páginas sem número (NaN), mas o
    "menos de 3 páginas" conta todas as que estão no mapa."""

    def __init__(self, valores: dict[Hashable, float] | None = None) -> None:
        self._valores: dict[Hashable, float] = dict(valores or {})

    def guardar(self, chave: Hashable, valor: float | None) -> None:
        """addOrUpdate(key, value). None vira NaN (sem número)."""
        self._valores[chave] = SEM_NUMERO if valor is None else float(valor)

    def tirar(self, chave: Hashable) -> None:
        """remove(key)."""
        self._valores.pop(chave, None)

    def _media_e_desvio(self) -> tuple[float, float]:
        """update(): média e desvio-padrão amostral dos números que existem.
        Com 0 número a média sai NaN e com 1 o desvio sai NaN, como no C++
        (0/0); nesses casos nenhuma comparação dá verdadeiro."""
        numeros = [v for v in self._valores.values() if not math.isnan(v)]
        quantos = len(numeros)
        if quantos == 0:
            return SEM_NUMERO, SEM_NUMERO
        media = sum(numeros) / quantos
        if quantos == 1:
            return media, SEM_NUMERO
        soma = sum((v - media) ** 2 for v in numeros)
        return media, math.sqrt(soma / (quantos - 1))

    def diferente(self, chave: Hashable, ajuste: Ajuste, sem_numero_conta: bool = False) -> bool:
        """isDeviant(key, coefficient, threshold, defaultVal)."""
        if chave not in self._valores or len(self._valores) < 3:
            return False
        valor = self._valores[chave]
        if math.isnan(valor):
            return sem_numero_conta
        media, desvio = self._media_e_desvio()
        # std::max(a, b) devolve a quando nenhum dos dois é maior (NaN): o max
        # do Python faz igual, com a ordem dos argumentos mantida.
        return abs(valor - media) > max(ajuste.coeficiente * desvio, (ajuste.limite / 100) * media)

    def quanto(self, chave: Hashable) -> float:
        """getDeviationValue(key): a distância até a média, para ordenar
        "pela diferença" (OrderByDeviationProvider: maior primeiro). -1 quando
        a página não está ou não tem número; 0 com menos de 2 páginas."""
        if chave not in self._valores:
            return -1.0
        if len(self._valores) < 2:
            return 0.0
        valor = self._valores[chave]
        if math.isnan(valor):
            return -1.0
        media, _ = self._media_e_desvio()
        return abs(valor - media)


def valor_do_angulo(angulo: float | None) -> float:
    """deskew/Settings.cpp: o ângulo da página, ou sem número."""
    return SEM_NUMERO if angulo is None else float(angulo)


def valor_do_conteudo(largura_mm: float | None, altura_mm: float | None) -> float:
    """select_content/Settings.cpp: a diagonal do conteúdo em mm; sem número
    quando o conteúdo é vazio (QSizeF::toSize().isEmpty(): algum lado
    arredondado a menos de 1 mm)."""
    if largura_mm is None or altura_mm is None:
        return SEM_NUMERO
    if _arredondar_qt(largura_mm) <= 0 or _arredondar_qt(altura_mm) <= 0:
        return SEM_NUMERO
    return math.sqrt(largura_mm ** 2 + altura_mm ** 2)


def valor_das_margens(esquerda: float, cima: float, direita: float, baixo: float) -> float:
    """page_layout/Settings.cpp: raiz((esq + dir)^2 + (cima + baixo)^2), em mm."""
    return math.sqrt((esquerda + direita) ** 2 + (cima + baixo) ** 2)


def _arredondar_qt(valor: float) -> int:
    """qRound: meio para longe do zero."""
    return int(math.floor(valor + 0.5)) if valor >= 0 else int(math.ceil(valor - 0.5))


def diferentes(valores: Iterable[float | None], ajuste: Ajuste,
               sem_numero_conta: bool = False) -> list[bool]:
    """Para cada página (na ordem), se ela é diferente das outras."""
    lista = list(valores)
    desvio = Desvio({i: (SEM_NUMERO if v is None else float(v)) for i, v in enumerate(lista)})
    return [desvio.diferente(i, ajuste, sem_numero_conta) for i in range(len(lista))]


def ordem_pela_diferenca(valores: Iterable[float | None]) -> list[int]:
    """As posições das páginas da mais diferente para a menos
    (OrderByDeviationProvider::precedes; as sem número vão para o fim)."""
    lista = list(valores)
    desvio = Desvio({i: (SEM_NUMERO if v is None else float(v)) for i, v in enumerate(lista)})
    return sorted(range(len(lista)), key=lambda i: -desvio.quanto(i))
