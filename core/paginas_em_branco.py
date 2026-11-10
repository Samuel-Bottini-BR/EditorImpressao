"""Páginas em branco postas à mão no livro (D-623).

PEDIDO DO SAMUEL (04/11/2026, print a-80)
    "as paginas ainda estão em lugar errado né? eu queria conseguir com botão direito apertando no
    meio das paginas aperece opção de adicionar folha em branco." Livro de decisões: botão direito
    numa miniatura da tira de baixo → "adicionar página em branco antes" / "adicionar página em
    branco depois". A página em branco tem o tamanho das vizinhas, entra no livro, no PDF e nos
    cadernos; "tirar do livro" a remove; Ctrl+Z desfaz. Muda o modelo de dados (página que não vem
    do PDF; a D-487 deixou o "inserir" para depois por isso): projeto antigo abre igual.

COMO É GUARDADA
    É uma ConfigPagina como as outras, na lista Projeto.paginas (a ordem do livro é a ordem da
    lista, D-615), com:
      - inserida = um número > 0, único no livro (ConfigPagina.inserida; 0 = a página veio do PDF,
        que é o padrão: projeto antigo não tem o campo e abre igual);
      - em_branco = True (o "Deixar em branco" de sempre: a página fica no livro, do tamanho dela,
        toda branca; core.pipeline);
      - os campos de tamanho COPIADOS da página vizinha (a clicada): folha, metade, corte, ângulo,
        tamanho de folha, mover. Assim ela é desenhada como a vizinha (mesmo tamanho) e sai branca.
    Ela não é "da folha": o que mexe nas páginas de uma folha (dividir/juntar à mão, o Dividir do
    Automático, mudar a folha de lugar) não a leva junto (inserida(), usada por core/dividir_a_mao,
    core/automatico, core/ordem_das_paginas e modelos.Projeto.paginas_ativas).

O DESFAZER
    Uma ação com o campo historico_acoes.CAMPO_DAS_INSERIDAS: a lista de TODAS as páginas postas à
    mão, com a posição de cada uma no livro ({"posicao", "pagina"}), de antes e de depois.
    por_as_inseridas tira todas da lista e as põe de volta nas posições (a página que continua é o
    mesmo objeto; a que volta pelo Ctrl+Y é refeita do dicionário). O desfazer é em pilha, então
    as posições valem na hora em que a ação é aplicada.

Seguro mudar: os textos. Arriscado: mudar o número de uma página posta (a ordem guardada pelo
D-615 a acha por [folha, metade, número]); desenhar a página posta sem branco.
"""

from __future__ import annotations

import copy
from typing import Any

from historico_acoes import CAMPO_DAS_INSERIDAS  # noqa: F401 (o nome do campo mora lá)


def inserida(pagina) -> bool:
    """A página foi posta à mão (não vem do PDF)? Objeto de versão antiga: não."""
    try:
        return int(getattr(pagina, "inserida", 0) or 0) > 0
    except (TypeError, ValueError):
        return False


def numero(pagina) -> int:
    """O número da página posta (0 = veio do PDF)."""
    try:
        return int(getattr(pagina, "inserida", 0) or 0)
    except (TypeError, ValueError):
        return 0


def tem_inseridas(projeto) -> bool:
    """O livro tem alguma página posta à mão (que não esteja tirada do livro)?"""
    return any(inserida(p) and not getattr(p, "apagada", False)
               for p in getattr(projeto, "paginas", []))


def _proximo_numero(projeto) -> int:
    return max([numero(p) for p in projeto.paginas] + [0]) + 1


# Campos que a página posta NÃO herda da vizinha (voltam ao de fábrica): o que é do conteúdo da
# vizinha (marcação, avisos, o "está certo") e não do tamanho.
_NAO_HERDA = ("selecao", "alertas", "alertas_aceitos", "revisada", "apagada", "mexida_a_mao",
              "automatico", "faixa_na_beirada", "marcacao_provisoria", "geometria_das_zonas",
              "gravura_feita_com", "forca_antes_do_reforco", "reforco_desfeito", "tem_cor",
              # D-661 (09/11/2026): a gravura achada a mao e da marcacao da vizinha
              "gravura_achada_a_mao")


def pagina_em_branco_como(vizinha, numero_novo: int):
    """Uma página nova, em branco, do tamanho de `vizinha` (cópia dos campos de tamanho e de
    jeito), com o número `numero_novo`. Não entra no livro: quem põe é por_as_inseridas."""
    nova = copy.deepcopy(vizinha)
    padrao = type(vizinha)(indice=0, folha=0)
    for campo in _NAO_HERDA:
        if hasattr(nova, campo):
            setattr(nova, campo, copy.deepcopy(getattr(padrao, campo)))
    nova.em_branco = True
    nova.inserida = int(numero_novo)
    return nova


def lista(projeto) -> list[dict[str, Any]]:
    """As páginas postas à mão, como o desfazer guarda: [{"posicao", "pagina"}] na ordem."""
    from core.dividir_a_mao import em_dicionarios

    return [{"posicao": n, "pagina": em_dicionarios([p])[0]}
            for n, p in enumerate(projeto.paginas) if inserida(p)]


def por_as_inseridas(projeto, valor) -> None:
    """Deixa no livro exatamente as páginas postas de `valor` (lista de {"posicao", "pagina"}),
    cada uma na posição dela, e renumera. Página posta que continua é o mesmo objeto (o que foi
    mudado nela depois fica); a que não está mais na lista sai; a que volta é refeita do
    dicionário. Valor que não é lista: nada muda."""
    if not isinstance(valor, list):
        return
    from modelos import paginas_da_lista

    existentes = {numero(p): p for p in projeto.paginas if inserida(p)}
    base = [p for p in projeto.paginas if not inserida(p)]
    itens = []
    for item in valor:
        try:
            itens.append((int(item["posicao"]), dict(item["pagina"])))
        except (KeyError, TypeError, ValueError):
            continue
    for posicao, dados in sorted(itens, key=lambda par: par[0]):
        num = int(dados.get("inserida", 0) or 0)
        pagina = existentes.get(num)
        if pagina is None:
            pagina = paginas_da_lista([dados])[0]
        base.insert(max(0, min(posicao, len(base))), pagina)
    projeto.paginas = base
    for n, pagina in enumerate(projeto.paginas):
        pagina.indice = n


def lugar_do_lado(projeto, posicao: int, depois: bool) -> int:
    """Onde a página em branco entra, ao lado da página `posicao`: antes dela ou logo depois. Na
    folha não dividida com mais de uma página na lista (projeto antigo) a folha é um bloco só
    (core/ordem_das_paginas.bloco): antes da primeira ou depois da última página dela."""
    from core.ordem_das_paginas import bloco

    juntas = bloco(projeto, posicao) or [posicao]
    return (max(juntas) + 1) if depois else min(juntas)


def campos_para_inserir(projeto, posicao: int, depois: bool) -> dict[str, Any]:
    """O campo de UMA ação do desfazer (alvo "pagina", sem índices) que põe uma página em branco
    antes (`depois` False) ou depois da página `posicao`, do tamanho dela. {} se a posição não
    existe."""
    if not 0 <= posicao < len(projeto.paginas):
        return {}
    nova = pagina_em_branco_como(projeto.paginas[posicao], _proximo_numero(projeto))
    paginas = list(projeto.paginas)
    paginas.insert(lugar_do_lado(projeto, posicao, depois), nova)
    from core.dividir_a_mao import em_dicionarios

    return {CAMPO_DAS_INSERIDAS: [{"posicao": n, "pagina": em_dicionarios([p])[0]}
                                  for n, p in enumerate(paginas) if inserida(p)]}


def onde_entrou(projeto, campos: dict) -> int | None:
    """A posição da página nova depois de aplicar `campos` (a de número mais alto)."""
    itens = campos.get(CAMPO_DAS_INSERIDAS) or []
    if not itens:
        return None
    maior = max(itens, key=lambda item: int(item["pagina"].get("inserida", 0) or 0))
    return int(maior["posicao"])
