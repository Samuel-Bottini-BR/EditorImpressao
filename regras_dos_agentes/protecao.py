"""A proteção do porteiro e da lista contra o próprio agente: compara com a versão de teste (achados 6 e 7, 19/11).

Quem tentou quebrar o passo 0 provou que um agente podia afrouxar o porteiro no próprio ramo: tirar uma palavra da
busca, pôr o próprio erro na lista, mudar o passo de um item, trocar "proposta" por "valendo". O formulário (K17)
pegava, mas só quando a gerente o rodava. Aqui está a mesma conta, que o teste do GitHub
(`tests/test_conferencias_protecao.py`) roda em toda entrega, contra a versão de teste (`VERSAO_DE_TESTE`, D-797):

- **a lista** (`porteiro_mudancas.mudancas_na_lista`, o lugar único dessa conta): item novo sem o "sim" próprio
  conferido no Livro, a situação ou o "sim" do Samuel mudados, o passo de um item mudado;
- **os dados das buscas** (`PROTEGIDOS`, abaixo): em cada um, nada da versão de teste pode sumir (acrescentar é livre)
  ou, nos marcados "igual", nada pode mudar.

O que continua sem esta proteção (escrito também na entrega): o código das funções do porteiro (o que conta como
"programa", como se compara), os próprios testes, e este arquivo. Para esses, vale a K17 do formulário (o porteiro e
as provas dele estão entre os arquivos que só a gerente muda) e quem tenta quebrar.

A versão de teste é buscada no GitHub pela peça única do git (`conversa_com_o_git.buscar_ramo`). Sem internet, o teste
falha com o motivo (nunca passa calado). Enquanto a versão de teste não tiver o porteiro (antes de juntar o passo 0),
não há com o que comparar, e o teste diz isso (fica parado, com o motivo).

Seguro mexer: acrescentar um nome em `PROTEGIDOS`. Arriscado: tirar um nome, ou trocar "igual" por "não some".
"""

from __future__ import annotations

import ast
from pathlib import Path

from . import conversa_com_o_git as git
from . import excecoes
from .livro import Livro

VERSAO_DE_TESTE = "obra-2026-10-26"     # D-797: a versão de teste, onde a gerente junta o trabalho

# (arquivo, nome da atribuição, regra): "nao_some" = nada da versão de teste some; "igual" = nada muda.
PROTEGIDOS: list[tuple[str, str, str]] = [
    ("regras_dos_agentes/porteiro.py", "PROTEGIDAS", "nao_some"),
    ("regras_dos_agentes/porteiro.py", "PALAVRAS_DO_WINDOWS", "nao_some"),
    ("regras_dos_agentes/porteiro.py", "PALAVRAS_DE_DETACHED", "nao_some"),
    ("regras_dos_agentes/porteiro.py", "PALAVRAS_DE_LICENCA", "nao_some"),
    ("regras_dos_agentes/porteiro.py", "PADRAO_DO_NUMERO_DE_DECISAO", "igual"),
    ("regras_dos_agentes/porteiro.py", "PADRAO_DO_EMOJI", "igual"),
    ("regras_dos_agentes/porteiro.py", "GERADORES", "nao_some"),
    ("regras_dos_agentes/porteiro.py", "PADRAO_DAS_FERRAMENTAS_PROIBIDAS", "igual"),
    ("regras_dos_agentes/porteiro.py", "BARRA_DE_ROLAGEM", "igual"),
    ("regras_dos_agentes/porteiro.py", "PECA_UNICA_DO_WINDOWS", "igual"),
    ("regras_dos_agentes/porteiro.py", "FORA_DO_PROJETO", "igual"),
    ("regras_dos_agentes/porteiro_mudancas.py", "PROTEGIDOS", "nao_some"),
    ("regras_dos_agentes/porteiro_mudancas.py", "QUEM_CONFERE", "igual"),
]


def literais(fonte: str) -> dict[str, object]:
    """Os valores literais das atribuições de primeiro nível de um arquivo (`NOME = [...]`, `NOME: tipo = {...}`)."""
    valores: dict[str, object] = {}
    for no in ast.parse(fonte).body:
        alvos = [no.target] if isinstance(no, ast.AnnAssign) else no.targets if isinstance(no, ast.Assign) else []
        for alvo in alvos:
            if isinstance(alvo, ast.Name) and getattr(no, "value", None) is not None:
                try:
                    valores[alvo.id] = ast.literal_eval(no.value)
                except ValueError:
                    pass
    return valores


def o_que_afrouxou(antes: str, depois: str, nomes: list[tuple[str, str]]) -> list[str]:
    """O que sumiu ou mudou, nos dados protegidos, entre duas versões de um arquivo."""
    va, vd = literais(antes), literais(depois)
    frases = []
    for nome, regra in nomes:
        if nome not in va:
            continue                    # o nome é novo nesta versão: nada a comparar
        if nome not in vd:
            frases.append(f"{nome} sumiu (ou deixou de ser um valor escrito no arquivo)")
            continue
        a, d = va[nome], vd[nome]
        if regra == "igual" or not isinstance(a, (list, tuple, set, frozenset, dict)):
            if a != d:
                frases.append(f"{nome} mudou")
        elif isinstance(a, dict):
            frases += [f"{nome}[{k!r}] sumiu ou mudou" for k, v in a.items() if not isinstance(d, dict) or d.get(k) != v]
        else:
            frases += [f"{nome}: {item!r} sumiu" for item in a if item not in d]
    return frases


def comparar(raiz: Path | str, ramo: str = VERSAO_DE_TESTE) -> list[str] | None:
    """O que este ramo afrouxou em relação ao `ramo` (a versão de teste), ou None se lá ainda não há porteiro.

    Levanta `GitFalhou` se o GitHub não responde: quem chama diz que não deu para conferir.
    """
    raiz = Path(raiz)
    base = git.buscar_ramo(raiz, ramo)
    lista_antes = git.conteudo_no_commit(raiz, base, excecoes.ARQUIVO_DA_LISTA)
    if lista_antes is None:
        return None
    from .porteiro_mudancas import mudancas_na_lista

    livro = Livro.do_repositorio(raiz)
    frases = mudancas_na_lista(excecoes.ler(raiz, lista_antes), excecoes.ler(raiz), livro)
    por_arquivo: dict[str, list[tuple[str, str]]] = {}
    for arquivo, nome, regra in PROTEGIDOS:
        por_arquivo.setdefault(arquivo, []).append((nome, regra))
    for arquivo, nomes in por_arquivo.items():
        antes = git.conteudo_no_commit(raiz, base, arquivo)
        if antes is None:
            continue
        agora = raiz / arquivo
        if not agora.exists():
            frases.append(f"{arquivo} sumiu")
            continue
        frases += [f"{arquivo}: {f}" for f in o_que_afrouxou(antes, agora.read_text(encoding="utf-8"), nomes)]
    return frases
