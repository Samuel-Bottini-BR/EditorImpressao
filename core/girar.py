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
- rotacao_final: o giro com que a folha da vez fica (e todas as escolhidas).
- campos_do_giro: o que vai para a acao do desfazer (historico_acoes), uma
  rotacao nova POR FOLHA (o desfazer devolve a cada uma o giro que ela
  tinha, que podia ser diferente em cada folha).
- descricao_do_giro: a frase do historico ("Girar 1/4 a direita: todas as
  12 folhas, viradas como a folha 3").
- D-618 (04/11/2026): numa folha ja dividida gira so a pagina da tela
  (gira_so_a_pagina, giro_da_pagina, recorte_girado, campos_do_giro_da_pagina;
  ver o bloco "D-618" mais abaixo).

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

"APLICAR EM" COPIA O GIRO DA FOLHA DA VEZ (decisao do Samuel, 06/10/2026)
-----------------------------------------------------------------------
Pergunta feita a ele, com desenhos: "Aplicar em todas: como as outras folhas
giram?". Resposta: "Todas ficam viradas como a folha da vez" (como o
ScanTailor, etapa "Fix Orientation"). Entao: a folha da vez gira o quarto de
volta a partir de onde esta, e TODAS as folhas do alcance (todas / daqui em
diante / pares / impares) terminam com esse MESMO giro final, qualquer que
fosse o giro de cada uma antes. "So esta" e o mesmo caso com uma folha so
(gira a partir de onde esta, como sempre). O desfazer devolve a cada folha o
giro que ela tinha (historico_acoes guarda o "antes" por folha).
Ate 06/10 era relativo (cada folha girava a partir de onde estava); para o
caso comum (nenhuma folha girada ainda) os dois dao o mesmo resultado.
Caso de canto, decisao do Samuel (06/10/2026): com "so as pares" numa folha
impar (ou "so as impares" numa folha par) o programa AVISA ("va a uma folha
par") e nao gira nada (aviso_fora_do_alcance; quem pergunta e a tela,
ui/tela_conferir._girar_folhas). Ate 06/10 a folha da vez ficava parada e as
escolhidas ficavam viradas como ela ficaria (decisao provisoria do
implementador): confuso, porque o giro que se copiava nao aparecia na tela.

O QUE E SEGURO E O QUE E ARRISCADO MUDAR
----------------------------------------
Seguro: os textos (NOMES_*, AVISO_*), a ordem das listas.
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


# O aviso quando a folha da vez nao entra no "so as pares"/"so as impares"
# (decisao do Samuel, 06/10/2026: "O programa avisa: 'va a uma folha par'").
AVISO_PARES_NA_IMPAR = ("Você está numa folha ímpar. Para girar só as pares, "
                        "vá a uma folha par e gire de lá.")
AVISO_IMPARES_NA_PAR = ("Você está numa folha par. Para girar só as ímpares, "
                        "vá a uma folha ímpar e gire de lá.")
# O mesmo aviso no "aplicar em" da aba Endireitar (item 2.2, G5), que conta
# PAGINAS e nao folhas. Seguro mudar: a frase.
AVISO_PARES_NA_IMPAR_PAGINA = ("Você está numa página ímpar. Para mudar só as pares, "
                               "vá a uma página par e mude de lá.")
AVISO_IMPARES_NA_PAR_PAGINA = ("Você está numa página par. Para mudar só as ímpares, "
                               "vá a uma página ímpar e mude de lá.")


def aviso_fora_do_alcance(atual: int, alcance: str, coisa: str = "folha") -> str:
    """A frase para avisar, se a folha da vez fica FORA do "aplicar em"; ""
    se pode girar.

    So acontece com "so as pares" numa folha impar e "so as impares" numa
    folha par (as outras escolhas sempre incluem a folha da vez). Nesse caso
    a tela avisa e nao gira nada: o giro de todas copia o giro final da
    folha da vez, e girar sem ela copiaria um giro que a pessoa nao ve.
    atual: o indice da folha na tela; par/impar conta o numero que a tela
    mostra (indice + 1), como em folhas_do_alcance. Seguro mudar: a frase.
    coisa: "folha" (o girar) ou "página" (o "aplicar em" da aba Endireitar,
    item 2.2: a mesma conta, sobre o indice da pagina).
    """
    numero = int(atual) + 1
    pagina = coisa == "página"
    if alcance == ALCANCE_PARES and numero % 2 == 1:
        return AVISO_PARES_NA_IMPAR_PAGINA if pagina else AVISO_PARES_NA_IMPAR
    if alcance == ALCANCE_IMPARES and numero % 2 == 0:
        return AVISO_IMPARES_NA_PAR_PAGINA if pagina else AVISO_IMPARES_NA_PAR
    return ""


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


def rotacao_final(folhas: Sequence[Any], giro: int, atual: int) -> int:
    """O giro com que a folha da vez fica depois deste giro: o dela mais o
    quarto (ou a meia volta) pedido. E o giro final de TODAS as folhas do
    "aplicar em" (decisao do Samuel, 06/10/2026: "Todas ficam viradas como a
    folha da vez"). `atual` fora do livro vale como a folha mais perto."""
    if not folhas:
        return nova_rotacao(0, giro)
    atual = min(max(int(atual), 0), len(folhas) - 1)
    return nova_rotacao(folhas[atual].rotacao, giro)


def campos_do_giro(folhas: Sequence[Any], indices: Sequence[int], giro: int,
                   atual: int) -> dict[str, Any]:
    """Os campos da acao do desfazer: {"rotacao": {"3": 90, "5": 90, ...}}.

    Todas as folhas da lista ficam com o MESMO giro, o final da folha da vez
    (rotacao_final; `atual` = o indice da folha na tela). Vai um valor POR
    FOLHA (historico_acoes.aplicar aceita o dicionario por indice) porque o
    desfazer guarda o "antes" de cada uma e devolve a cada folha o giro que
    ela tinha. Folhas fora do livro sao ignoradas.
    Arriscado: voltar ao giro relativo (cada folha a partir de onde esta):
    foi a regra ate 06/10, trocada por decisao do Samuel.
    """
    final = rotacao_final(folhas, giro, atual)
    novos = {}
    for i in indices:
        if 0 <= int(i) < len(folhas):
            novos[str(int(i))] = final
    return {"rotacao": novos}


# ---------------------------------------------------------------------------
# D-618 (Samuel, 04/11/2026): numa folha JA DIVIDIDA gira so a pagina da tela
# ---------------------------------------------------------------------------
# Palavras dele (prints a-70 a a-73, Gradus pagina 14): "ele deveria girar o
# conteudo só que é da pagina cortada, mas ele gira a pagina verdadeira do
# scan. tanto que quando você vai girando ele cai na folha branca. Ele gira as
# duas folhas ao mesmo tempo, faz uma confusão com as paginas."
#
# A causa (provada em relatorios/girar-pagina/): o giro morava so na FOLHA
# (ConfigFolha.rotacao, o scan inteiro) e vinha antes de dividir; a folha
# girada era dividida de novo pela MESMA linha (fracao da largura), entao cada
# "pagina" virava meia folha deitada com pedacos das duas paginas, e com meia
# volta a pagina 14 mostrava a 13 (a branca).
#
# O conserto: o giro de uma metade de folha dividida mora na PAGINA
# (ConfigPagina.giro_da_pagina, 0/90/180/270 no sentido do relogio) e e
# aplicado DEPOIS de dividir (core/pipeline.preparar_para_recorte), antes do
# endireitar e do corte. A outra pagina e a linha nao mudam. Folha inteira (nao
# dividida): o giro continua na folha, como antes. O corte a mao da pagina
# (pagina.recorte, fracao da pagina antes do corte) gira junto na mesma acao
# (recorte_girado), para continuar sobre o mesmo pedaco do papel.
# Projeto antigo nao tem o campo: 0 (sai igual).
# Arriscado: aplicar giro_da_pagina numa pagina "inteira" (a folha ja gira) ou
# antes de dividir (voltaria o defeito); mudar o sentido (o mesmo de
# core/endireitar.girar_90 e de core/zonas_na_folha).

def gira_so_a_pagina(folha: Any, pagina: Any) -> bool:
    """A pagina e metade de uma folha dividida? Ai o giro e so dela (D-618)."""
    return bool(getattr(folha, "dividir", False)) and getattr(pagina, "metade", "") in (
        "esquerda", "direita")


def giro_da_pagina(folha: Any, pagina: Any) -> int:
    """O giro de 90 em 90 SO desta pagina que vale agora (0, 90, 180, 270):
    o pagina.giro_da_pagina quando ela e metade de uma folha dividida; 0 em
    pagina inteira (ali quem gira e a folha) e em projeto antigo (sem o campo)."""
    if not gira_so_a_pagina(folha, pagina):
        return 0
    return nova_rotacao(getattr(pagina, "giro_da_pagina", 0) or 0, 0)


def recorte_girado(recorte: Sequence[float] | None, giro: int) -> list[float] | None:
    """O corte a mao (x, y, largura, altura em fracao da pagina) depois de a
    pagina girar `giro` graus no sentido do relogio: o MESMO pedaco do papel,
    nas fracoes da pagina girada. None continua None (corte automatico, que e
    medido de novo na pagina girada). Mesmo sentido de core/endireitar.girar_90:
    a 90 graus o ponto (u, v) vai para (1 - v, u)."""
    if recorte is None:
        return None
    x, y, w, h = (float(v) for v in recorte)
    g = nova_rotacao(0, giro)
    if g == 90:
        novo = (1.0 - (y + h), x, h, w)
    elif g == 180:
        novo = (1.0 - (x + w), 1.0 - (y + h), w, h)
    elif g == 270:
        novo = (y, 1.0 - (x + w), h, w)
    else:
        novo = (x, y, w, h)
    return [round(min(1.0, max(0.0, v)), 6) for v in novo]


def campos_da_pagina_que_giram_junto(pagina: Any, giro: int) -> dict[str, Any]:
    """O que a pagina leva junto quando ela (ou a folha inteira dela) gira
    `giro` graus, como uma foto girada (Samuel, 04/11/2026, "girar - sim" a
    proposta da gerente: "girar a folha inteira é como girar uma foto. A folha
    larga, com as duas páginas, fica em pé, inteira, sem esticar, sem apertar
    e sem cortar nada"):
      - o corte a mao (recorte) continua sobre o MESMO pedaco do papel
        (recorte_girado); sem isso o corte de antes cortaria outro pedaco;
      - o tamanho de folha escolhido no "tamanho..." / Mover
        (tamanho_folha_cm, largura x altura) deita junto num quarto de volta;
        sem isso a pagina deitada seria apertada dentro da folha em pe;
      - o lugar do conteudo na area branca (conteudo_deslocamento, fracao a
        partir do centro) gira junto.
    So devolve o que a pagina tem diferente do padrao (nada = {}); a escala
    do conteudo e o angulo do endireitar nao mudam com um giro de 90.
    Seguro mudar: nada. Arriscado: esquecer um destes campos (a pagina girada
    sairia cortada, apertada ou fora do lugar)."""
    g = nova_rotacao(0, giro)
    if not g:
        return {}
    campos: dict[str, Any] = {}
    recorte = getattr(pagina, "recorte", None)
    if recorte is not None:
        campos["recorte"] = recorte_girado(recorte, g)
    tamanho = getattr(pagina, "tamanho_folha_cm", None)
    if tamanho is not None and g in (90, 270):
        campos["tamanho_folha_cm"] = [float(tamanho[1]), float(tamanho[0])]
    dx, dy = (float(v) for v in (getattr(pagina, "conteudo_deslocamento", None) or (0.0, 0.0)))
    if dx or dy:
        # em fracao a partir do centro: (u, v) -> (1 - v, u) a 90 graus
        novo = {90: (-dy, dx), 180: (-dx, -dy), 270: (dy, -dx)}[g]
        campos["conteudo_deslocamento"] = [round(v, 6) + 0.0 for v in novo]
    return campos


def campos_do_giro_da_pagina(pagina: Any, giro: int) -> dict[str, Any]:
    """Os campos da acao do desfazer de girar SO esta pagina (alvo "pagina"):
    o giro novo e o que gira junto com ela (campos_da_pagina_que_giram_junto:
    o corte a mao, o tamanho de folha escolhido, o lugar do conteudo). O
    desfazer (historico_acoes, que ja guarda o "antes" de cada campo) devolve
    tudo. Seguro mudar: nada. Arriscado: girar sem levar o corte (o corte a
    mao cairia em outro pedaco da pagina)."""
    campos: dict[str, Any] = {
        "giro_da_pagina": nova_rotacao(getattr(pagina, "giro_da_pagina", 0) or 0, giro)}
    campos.update(campos_da_pagina_que_giram_junto(pagina, giro))
    return campos


def descricao_do_giro_da_pagina(giro: int, pagina: int) -> str:
    """A frase do historico de girar so a pagina (pagina: o indice; a frase
    mostra o numero). Seguro mudar: o texto."""
    nome = NOMES_DOS_GIROS.get(giro, f"{giro} graus")
    return f"Girar {nome}: a página {int(pagina) + 1}"


def descricao_do_giro(giro: int, alcance: str, atual: int, quantas: int) -> str:
    """A frase que aparece no historico e no "Desfazer: ...".

    atual: o indice da folha na tela (a folha da vez, cujo giro as outras
    copiam). Seguro mudar: o texto (aparece no Historico e no menu Editar).
    """
    nome = NOMES_DOS_GIROS.get(giro, f"{giro} graus")
    # singular no 1 (etapa 9c: "da folha 180 em diante (1 folhas)")
    folhas = "1 folha" if quantas == 1 else f"{quantas} folhas"
    if alcance == ALCANCE_TODAS:
        onde = "a única folha" if quantas == 1 else f"todas as {quantas} folhas"
    elif alcance == ALCANCE_DAQUI:
        onde = f"da folha {atual + 1} em diante ({folhas})"
    elif alcance == ALCANCE_PARES:
        onde = "a única folha par" if quantas == 1 else f"as {quantas} folhas pares"
    elif alcance == ALCANCE_IMPARES:
        onde = "a única folha ímpar" if quantas == 1 else f"as {quantas} folhas ímpares"
    else:
        return f"Girar {nome}: a folha {atual + 1}"
    # com mais de uma folha, a frase diz que elas copiam o giro da folha da
    # vez (decisao do Samuel, 06/10/2026)
    viradas = "virada" if quantas == 1 else "viradas"
    return f"Girar {nome}: {onde}, {viradas} como a folha {atual + 1}"
