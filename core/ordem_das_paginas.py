"""A ordem das páginas do livro: mudar folhas e páginas de lugar (D-615, D-616).

PEDIDO DO SAMUEL (04/11/2026, prints a-61 e a-62)
    "eu quero poder mover folhas para onde eu quiser dentro do app, quero poder
    arrastar e mover folhas, caso eu precise resolver esse problema na mão, mas
    qual seria o jeito para resolver esse problema sem ser na mão?" → proposta
    (arrastar a miniatura da tira; caixinha "A 1ª folha é a capa aberta" no
    Dividir do Automático) → "ok".

ONDE MORA A ORDEM
    A ordem do livro É a ordem da lista `Projeto.paginas`: o PDF (Projeto.
    paginas_ativas), a tela (a tira, as setas, "página N de M"), os cadernos e a
    prévia do Automático já seguem essa lista. Ela já vai para o projeto.json
    como está; por isso nada novo é gravado no projeto, e o projeto antigo (a
    lista na ordem das folhas) abre exatamente como antes.

O QUE ESTE MÓDULO FAZ (só contas; a tela é ui/tela_conferir.py e a tira
ui/widgets/tira_miniaturas.py)
    - bloco: as páginas que andam juntas (a página de uma folha DIVIDIDA anda
      sozinha; a folha não dividida anda inteira, com todas as páginas dela).
    - campos_para_mover: o campo da ação do desfazer (CAMPO_DA_ORDEM) que leva
      um bloco para antes de outra página (ou para o fim).
    - chaves / por_na_ordem: a ordem como o desfazer guarda ([folha, metade] de
      cada página) e a lista posta nessa ordem (as páginas são os MESMOS
      objetos: filtro, corte, "está certo" vão junto).
    - fora_da_ordem_do_pdf: a lista não está mais na ordem das folhas do PDF (o
      caminho rápido dos cadernos, Projeto.so_cadernos, monta com as folhas do
      PDF e não pode ser usado).
    - ordem_depois_de_trocar: a ordem que o "não dividir esta" / "juntar todas"
      deixa, para o Ctrl+Z dele devolver as páginas separadas ao lugar delas.
    - capa_na_frente (D-616): a metade da direita da 1ª folha vai para a frente
      e a da esquerda para o fim.

O QUE É ARRISCADO
    Mudar a lista sem passar por uma ação do desfazer: as ações mais velhas
    guardam as páginas pela posição (o desfazer é em pilha, então a ação de
    mudar a ordem é sempre desfeita antes delas).
"""

from __future__ import annotations

from collections import defaultdict, deque

# O campo da ação do desfazer (historico_acoes.aplicar) com a ordem do livro:
# [[folha, metade], ...] de cada página, na ordem. Mora em historico_acoes (como
# PREFIXO_PAGINAS_DA_FOLHA). Arriscado: mudar o nome (as ações gravadas
# deixariam de valer).
from historico_acoes import CAMPO_DA_ORDEM  # noqa: E402


def chave(pagina) -> list:
    """[folha, metade] da página: o que a identifica na ordem guardada."""
    return [int(pagina.folha), str(pagina.metade)]


def chaves(projeto) -> list[list]:
    """A ordem de agora, como o desfazer guarda."""
    return [chave(p) for p in projeto.paginas]


def renumerar(projeto) -> None:
    """ConfigPagina.indice = a posição de cada página na lista."""
    for n, pagina in enumerate(projeto.paginas):
        pagina.indice = n


def por_na_ordem(projeto, ordem) -> None:
    """Põe as páginas do livro na `ordem` (lista de [folha, metade]) e renumera.
    As páginas são os mesmos objetos. Página que a ordem não cita (não
    acontece: o desfazer é em pilha) fica no fim, na ordem em que estava."""
    if not isinstance(ordem, list):
        return
    filas: dict[tuple, deque] = defaultdict(deque)
    for pagina in projeto.paginas:
        filas[tuple(chave(pagina))].append(pagina)
    nova = []
    usadas = set()
    for item in ordem:
        try:
            fila = filas.get((int(item[0]), str(item[1])))
        except (TypeError, ValueError, IndexError):
            continue
        if fila:
            pagina = fila.popleft()
            nova.append(pagina)
            usadas.add(id(pagina))
    nova += [p for p in projeto.paginas if id(p) not in usadas]
    projeto.paginas = nova
    renumerar(projeto)


def _dividida(projeto, pagina) -> bool:
    """A página é a metade de uma folha dividida (anda sozinha)?"""
    folhas = projeto.folhas
    return (pagina.metade != "inteira" and 0 <= pagina.folha < len(folhas)
            and bool(folhas[pagina.folha].dividir))


def bloco(projeto, posicao: int) -> list[int]:
    """As posições (em projeto.paginas) que andam junto com a página
    `posicao`: só ela, se é metade de folha dividida ("se já estiver dividida,
    muda a página"); senão todas as páginas da folha dela (a folha anda
    inteira; projeto antigo pode ter duas páginas numa folha não dividida)."""
    paginas = projeto.paginas
    if not 0 <= posicao < len(paginas):
        return []
    pagina = paginas[posicao]
    if _dividida(projeto, pagina):
        return [posicao]
    return [n for n, p in enumerate(paginas)
            if p.folha == pagina.folha and not _dividida(projeto, p)]


def ordem_depois_de_mover(projeto, posicoes: list[int], antes_de: int | None) -> list:
    """A lista de páginas (objetos) com as `posicoes` tiradas e postas, na
    mesma ordem entre si, antes da página `antes_de` (posição de agora; None =
    no fim). Se `antes_de` está entre as que andam, nada muda."""
    paginas = list(projeto.paginas)
    andam = set(posicoes)
    if not andam or (antes_de is not None and antes_de in andam):
        return paginas
    movidas = [paginas[n] for n in sorted(andam) if 0 <= n < len(paginas)]
    alvo = paginas[antes_de] if antes_de is not None and 0 <= antes_de < len(paginas) else None
    resto = [p for n, p in enumerate(paginas) if n not in andam]
    lugar = len(resto) if alvo is None else next(i for i, p in enumerate(resto) if p is alvo)
    return resto[:lugar] + movidas + resto[lugar:]


def campos_para_mover(projeto, posicoes: list[int], antes_de: int | None) -> dict:
    """Os campos de UMA ação do desfazer (alvo "pagina", sem índices) que levam
    as páginas `posicoes` para antes de `antes_de` (None = o fim). {} se a ordem
    não muda (soltou no mesmo lugar)."""
    nova = ordem_depois_de_mover(projeto, posicoes, antes_de)
    if all(a is b for a, b in zip(nova, projeto.paginas)):
        return {}
    return {CAMPO_DA_ORDEM: [chave(p) for p in nova]}


def fora_da_ordem_do_pdf(projeto) -> bool:
    """Alguma página vem antes de uma página de folha anterior (a ordem foi
    mudada à mão ou pela capa aberta)? Livro sem ordem mudada: False."""
    paginas = projeto.paginas
    return any(paginas[n].folha > paginas[n + 1].folha for n in range(len(paginas) - 1))


def folha_espalhada(projeto, indice_folha: int) -> bool:
    """As páginas da folha não estão uma seguida da outra na lista (uma delas
    foi mudada de lugar)?"""
    lugares = [n for n, p in enumerate(projeto.paginas) if p.folha == indice_folha]
    return bool(lugares) and lugares[-1] - lugares[0] + 1 != len(lugares)


def ordem_depois_de_trocar(projeto, trocas: dict[int, list]) -> list[list]:
    """A ordem ([folha, metade]) depois de pôr, no lugar das páginas de cada
    folha de `trocas` (folha -> lista de [folha, metade] das páginas novas), as
    páginas novas: no lugar da PRIMEIRA página da folha, como
    core/dividir_a_mao.trocar_as_paginas_da_folha faz."""
    ordem = []
    ja = set()
    for pagina in projeto.paginas:
        f = pagina.folha
        if f in trocas:
            if f not in ja:
                ja.add(f)
                ordem.extend([list(c) for c in trocas[f]])
            continue
        ordem.append(chave(pagina))
    return ordem


# --- D-616: a capa aberta ----------------------------------------------------

def capa_na_frente(projeto, folha: int = 0) -> bool:
    """D-616 (Samuel, 04/11/2026: caixinha "A 1ª folha é a capa aberta" → "ok"):
    com a `folha` (a 1ª do PDF) dividida, a metade da DIREITA (a capa) vai para
    o começo do livro e a da ESQUERDA (a contracapa) para o fim. Devolve True se
    a ordem mudou. Quem chama guarda o antes para o desfazer
    (core/automatico._dividir: na ação do Automático)."""
    nova = ordem_com_a_capa_na_frente(projeto, folha)
    if nova is None:
        return False
    projeto.paginas = nova
    renumerar(projeto)
    return True


def ordem_com_a_capa_na_frente(projeto, folha: int = 0) -> list | None:
    """A lista de páginas (os mesmos objetos) com a capa na frente e a contracapa
    no fim (capa_na_frente), sem mudar o projeto. None se nada muda (a folha não
    está dividida, falta uma das metades, ou já está assim)."""
    if not 0 <= folha < len(projeto.folhas) or not projeto.folhas[folha].dividir:
        return None
    paginas = projeto.paginas
    direita = next((p for p in paginas if p.folha == folha and p.metade == "direita"), None)
    esquerda = next((p for p in paginas if p.folha == folha and p.metade == "esquerda"), None)
    if direita is None or esquerda is None:
        return None
    resto = [p for p in paginas if p is not direita and p is not esquerda]
    nova = [direita] + resto + [esquerda]
    if all(a is b for a, b in zip(nova, paginas)):
        return None
    return nova


def capa_na_frente_na_lista(lista: list, folha: int = 0) -> list:
    """A mesma regra de capa_na_frente numa lista de tuplas (origem, folha,
    metade, ...) (core/automatico.paginas_do_pdf_depois: a prévia sem copiar o
    projeto). Sem as duas metades da folha: a lista como veio."""
    direita = next((t for t in lista if t[1] == folha and t[2] == "direita"), None)
    esquerda = next((t for t in lista if t[1] == folha and t[2] == "esquerda"), None)
    if direita is None or esquerda is None:
        return list(lista)
    resto = [t for t in lista if t is not direita and t is not esquerda]
    return [direita] + resto + [esquerda]
