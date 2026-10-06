"""Girar a folha de 90 em 90 graus, com "aplicar em" (item 2.3 do plano).

Pedido do Samuel (conferencia 14, G1, 05/10/2026): "(c) Os dois - Os botoes
tem que existir, mas o que vai decidir como vai ser para clicar e como vai
ficar e o agente de layout comigo, mas por enquanto pode ser assim." E da
conferencia 9 (R1): nenhum dos dois programas (o nosso e o ScanTailor) gira
sozinho - girar e sempre a pessoa que manda.

Como o ScanTailor (etapa "Fix Orientation", docs/pesquisa/fase2-mapa-scantailor.md
secao 6.3): tres giros (1/4 a esquerda, 1/4 a direita, meia volta) e "aplicar
em: so esta / todas / daqui em diante / so as pares / so as impares".

O QUE ESTE MODULO FAZ (so contas; nada de tela, nada de imagem)
--------------------------------------------------------------
- folhas_do_alcance: QUAIS folhas o giro pega.
- nova_rotacao: a rotacao da folha depois de um giro.
- campos_do_giro: o que vai para a acao do desfazer (historico_acoes), uma
  rotacao nova POR FOLHA (cada folha pode estar num giro diferente antes).
- descricao_do_giro: a frase do historico ("Girar 1/4 a direita: todas as
  12 folhas").

COMO O GIRO VALE NO RESTO DO PROGRAMA (nada disto e novo; so conferido)
----------------------------------------------------------------------
- O giro e o campo que ja existia, ConfigFolha.rotacao (0, 90, 180, 270, no
  sentido do relogio, como core/endireitar.girar_90). Ja vai e volta do
  projeto.json desde sempre: projeto antigo abre igual (sem o campo = 0).
- O giro e a PRIMEIRA etapa do preparo (core/pipeline.preparar_para_recorte):
  depois dele vem dividir, cortar e endireitar, que sao recalculados sozinhos
  porque a rotacao entra na chave da conta guardada
  (pipeline._chave_da_geometria) e na chave das previas (ui/tarefas.py).
- As zonas da aba Marcar acompanham: a rotacao faz parte da "geometria do
  desenho" (core/zonas_na_folha.geometria_do_desenho), entao ao desenhar a
  pagina girada as zonas sao levadas para ficar sobre o MESMO pedaco do
  papel (zonas_na_folha.acompanhar).

GIRO RELATIVO (decisao do implementador, a confirmar com o layout)
------------------------------------------------------------------
Cada folha do alcance gira o quarto de volta A PARTIR de onde ela esta (uma
folha ja girada a direita, com "todas" + 1/4 a direita, fica de cabeca para
baixo). E o que o botao diz ("girar"). O ScanTailor faz diferente no
"aplicar em": copia para as outras o giro final da folha da vez. Para o caso
comum (nenhuma folha girada ainda) os dois dao o mesmo resultado.

O QUE E SEGURO E O QUE E ARRISCADO MUDAR
----------------------------------------
Seguro: os textos (NOMES_*), a ordem das listas.
Arriscado: o sentido dos giros (GIRO_DIREITA = +90 e o sentido do relogio do
cv2.ROTATE_90_CLOCKWISE em core/endireitar.girar_90 e da matriz de
core/zonas_na_folha._matriz_folha_para_pagina); "pares/impares" contam o
NUMERO DA FOLHA que a tela mostra (indice + 1), nao o indice.
"""

from __future__ import annotations

from typing import Any, Sequence

# Os giros, em graus no sentido do relogio (o da ConfigFolha.rotacao).
GIRO_ESQUERDA = 270      # 1/4 de volta contra o relogio = 3/4 a favor
GIRO_DIREITA = 90
GIRO_MEIA_VOLTA = 180
GIROS = (GIRO_ESQUERDA, GIRO_DIREITA, GIRO_MEIA_VOLTA)

NOMES_DOS_GIROS = {
    GIRO_ESQUERDA: "¼ à esquerda",
    GIRO_DIREITA: "¼ à direita",
    GIRO_MEIA_VOLTA: "meia volta",
}

# Onde o giro vale ("aplicar em").
ALCANCE_ESTA = "esta"
ALCANCE_TODAS = "todas"
ALCANCE_DAQUI = "daqui_em_diante"
ALCANCE_PARES = "pares"
ALCANCE_IMPARES = "impares"
ALCANCES = (ALCANCE_ESTA, ALCANCE_TODAS, ALCANCE_DAQUI, ALCANCE_PARES, ALCANCE_IMPARES)

NOMES_DOS_ALCANCES = {
    ALCANCE_ESTA: "só esta",
    ALCANCE_TODAS: "todas",
    ALCANCE_DAQUI: "daqui em diante",
    ALCANCE_PARES: "só as pares",
    ALCANCE_IMPARES: "só as ímpares",
}


def folhas_do_alcance(total: int, atual: int, alcance: str) -> list[int]:
    """Os indices (comecando em 0) das folhas que o giro pega.

    total: quantas folhas o livro tem. atual: o indice da folha na tela.
    "pares" e "impares" contam o numero que a tela mostra (folha 1, 2, 3...):
    "so as pares" = folhas 2, 4, 6... (indices 1, 3, 5...). Alcance que nao
    existe vale como "so esta" (nunca gira o livro inteiro por engano).
    """
    if total <= 0:
        return []
    atual = min(max(int(atual), 0), total - 1)
    if alcance == ALCANCE_TODAS:
        return list(range(total))
    if alcance == ALCANCE_DAQUI:
        return list(range(atual, total))
    if alcance == ALCANCE_PARES:
        return [i for i in range(total) if (i + 1) % 2 == 0]
    if alcance == ALCANCE_IMPARES:
        return [i for i in range(total) if (i + 1) % 2 == 1]
    return [atual]


def nova_rotacao(rotacao: int, giro: int) -> int:
    """A rotacao (0, 90, 180 ou 270) depois de girar `giro` graus no sentido
    do relogio. Rotacao estranha no projeto (ex.: 45) e arredondada para o
    quarto de volta mais perto antes, para nunca gravar um giro que
    core/endireitar.girar_90 ignoraria."""
    base = int(round(int(rotacao or 0) / 90.0)) * 90
    return (base + int(giro)) % 360


def campos_do_giro(folhas: Sequence[Any], indices: Sequence[int], giro: int) -> dict[str, Any]:
    """Os campos da acao do desfazer: {"rotacao": {"3": 90, "5": 180, ...}}.

    Um valor POR FOLHA (historico_acoes.aplicar aceita o dicionario por
    indice): cada folha gira a partir de onde ela esta. Folhas fora da lista
    sao ignoradas.
    """
    novos = {}
    for i in indices:
        if 0 <= int(i) < len(folhas):
            novos[str(int(i))] = nova_rotacao(folhas[int(i)].rotacao, giro)
    return {"rotacao": novos}


def descricao_do_giro(giro: int, alcance: str, atual: int, quantas: int) -> str:
    """A frase que aparece no historico e no "Desfazer: ...".

    atual: o indice da folha na tela (para "so esta" e "daqui em diante").
    """
    nome = NOMES_DOS_GIROS.get(giro, f"{giro} graus")
    if alcance == ALCANCE_TODAS:
        onde = f"todas as {quantas} folhas"
    elif alcance == ALCANCE_DAQUI:
        onde = f"da folha {atual + 1} em diante ({quantas} folhas)"
    elif alcance == ALCANCE_PARES:
        onde = f"as {quantas} folhas pares"
    elif alcance == ALCANCE_IMPARES:
        onde = f"as {quantas} folhas ímpares"
    else:
        onde = f"a folha {atual + 1}"
    return f"Girar {nome}: {onde}"
