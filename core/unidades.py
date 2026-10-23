"""Item 2.19 (parte 1): as medidas em centímetros, milímetros ou polegadas.

O QUE FAZ
    O ScanTailor deixa escolher em que unidade as medidas aparecem (pixels,
    milímetros, centímetros, polegadas: src/core/Units*, UnitsConverter). Aqui
    é o mesmo para as medidas que o programa mostra na tela: os números do
    corte enquanto se arrasta (ui/widgets/visualizador.py) e o tamanho da folha
    (ui/dialogo_tamanho_da_folha.py). Pixels ficam de fora: o Kaique não pensa
    em pixel (CLAUDE.md §1: nunca "DPI/resolução" na tela).

    Só muda o que se LÊ: por dentro tudo continua em centímetros (os campos
    gravados nos projetos, como ConfigPagina.tamanho_folha_cm, não mudam).

DE FÁBRICA: centímetros - é o que a tela sempre mostrou (não muda nada para
    quem já usa). A escolha é da máquina (configuracoes.json, chave "unidade"),
    em Configurações.

SEGURO MUDAR: os nomes e as casas decimais. ARRISCADO: guardar valor em outra
    unidade que não cm (os projetos antigos leriam errado).
"""

from __future__ import annotations

MM = "mm"
CM = "cm"
POLEGADA = "pol"
UNIDADES = (CM, MM, POLEGADA)
UNIDADE_DE_FABRICA = CM

NOMES = {CM: "centímetros", MM: "milímetros", POLEGADA: "polegadas"}
SUFIXOS = {CM: " cm", MM: " mm", POLEGADA: " pol"}
CASAS = {CM: 2, MM: 1, POLEGADA: 2}
_POR_CM = {CM: 1.0, MM: 10.0, POLEGADA: 1 / 2.54}

CHAVE_DAS_CONFIGURACOES = "unidade"


def valida(unidade) -> str:
    return unidade if unidade in UNIDADES else UNIDADE_DE_FABRICA


def da_maquina() -> str:
    """A unidade escolhida em Configurações (de fábrica, centímetros)."""
    try:
        import configuracoes

        return valida(configuracoes.ler(CHAVE_DAS_CONFIGURACOES))
    except Exception:  # noqa: BLE001 - configuração quebrada não para a tela
        return UNIDADE_DE_FABRICA


def de_cm(valor_cm: float, unidade: str | None = None) -> float:
    """Um valor em cm na unidade pedida (None = a da máquina)."""
    return float(valor_cm) * _POR_CM[valida(unidade or da_maquina())]


def para_cm(valor: float, unidade: str | None = None) -> float:
    """Um valor na unidade pedida, de volta para cm."""
    return float(valor) / _POR_CM[valida(unidade or da_maquina())]


def texto(valor_cm: float, unidade: str | None = None) -> str:
    """"12.34 cm", "123.4 mm" ou "4.86 pol" (o ponto, como a tela já mostrava)."""
    unidade = valida(unidade or da_maquina())
    return f"{de_cm(valor_cm, unidade):.{CASAS[unidade]}f}{SUFIXOS[unidade]}"
