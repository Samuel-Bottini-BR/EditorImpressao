"""A proteção do porteiro e da lista contra o próprio agente: compara com a versão de teste (achados 6 e 7, 19/11).

Quem tentou quebrar o passo 0 provou que um agente podia afrouxar o porteiro no próprio ramo: tirar uma palavra da
busca, pôr o próprio erro na lista, mudar o passo de um item, trocar "proposta" por "valendo". O formulário (K17)
pegava, mas só quando a gerente o rodava. Aqui está a mesma conta, que o teste do GitHub
(`tests/test_conferencias_protecao.py`) roda em toda entrega, contra a versão de teste (`VERSAO_DE_TESTE`, D-797):

- **a lista** (`porteiro_mudancas.mudancas_na_lista`, o lugar único dessa conta): qualquer item novo, a situação ou o
  "sim" do Samuel mudados, o passo de um item mudado (nada disso entra por ramo de agente, R1);
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
from .livro import VERSAO_DE_TESTE

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
    ("regras_dos_agentes/porteiro.py", "NAO_E_PROGRAMA", "igual"),
    ("regras_dos_agentes/porteiro.py", "FONTE_PYTHON", "igual"),
    ("regras_dos_agentes/porteiro.py", "COMPILADO_PYTHON", "igual"),
    # K25 (D-809, 20/11). As listas do que acusar não perdem item (acrescentar deixa mais rígido); as duas peças do git
    # (a exceção) e o que conta como "conferiu o atalho" ficam iguais: crescer qualquer um dos dois afrouxa a K25.
    ("regras_dos_agentes/porteiro.py", "PECAS_DO_GIT", "igual"),
    ("regras_dos_agentes/porteiro.py", "COMANDOS_DE_TERMINAL", "nao_some"),
    ("regras_dos_agentes/porteiro.py", "PALAVRAS_DO_GIT", "nao_some"),
    ("regras_dos_agentes/porteiro.py", "PALAVRAS_DE_APAGAR", "nao_some"),
    ("regras_dos_agentes/porteiro.py", "CONFERE_SE_E_ATALHO", "igual"),
    ("regras_dos_agentes/porteiro.py", "SO_NO_GITHUB", "igual"),
    ("regras_dos_agentes/porteiro.py", "EXEMPLOS_DA_K25", "nao_some"),
    ("regras_dos_agentes/porteiro_mudancas.py", "PROTEGIDOS", "nao_some"),
    ("regras_dos_agentes/porteiro_mudancas.py", "QUEM_CONFERE", "igual"),
]


class _NaoELiteral(ValueError):
    """O valor não é um dado escrito no arquivo (tem chamada de função, por exemplo)."""


def _valor(no: ast.AST, ja: dict[str, object]) -> object:
    """O valor de um dado escrito no arquivo: textos, números, listas, tuplas, conjuntos, dicionários, um nome já
    definido antes no mesmo arquivo e a soma de textos (`_SEP + "..."`). Nada é executado."""
    if isinstance(no, ast.Constant):
        return no.value
    if isinstance(no, ast.Name) and no.id in ja:
        return ja[no.id]
    if isinstance(no, ast.BinOp) and isinstance(no.op, ast.Add):
        esquerda, direita = _valor(no.left, ja), _valor(no.right, ja)
        if isinstance(esquerda, str) and isinstance(direita, str):
            return esquerda + direita
    if isinstance(no, (ast.List, ast.Tuple, ast.Set)):
        itens = [_valor(e, ja) for e in no.elts]
        return list(itens) if isinstance(no, ast.List) else tuple(itens) if isinstance(no, ast.Tuple) else set(itens)
    if isinstance(no, ast.Dict) and None not in no.keys:
        return {_valor(k, ja): _valor(v, ja) for k, v in zip(no.keys, no.values)}
    raise _NaoELiteral(ast.dump(no)[:60])


def literais(fonte: str) -> dict[str, object]:
    """Os valores dos dados de primeiro nível de um arquivo (`NOME = [...]`, `NOME: tipo = {...}`), sem executar nada."""
    valores: dict[str, object] = {}
    for no in ast.parse(fonte).body:
        alvos = [no.target] if isinstance(no, ast.AnnAssign) else no.targets if isinstance(no, ast.Assign) else []
        for alvo in alvos:
            if isinstance(alvo, ast.Name) and getattr(no, "value", None) is not None:
                try:
                    valores[alvo.id] = _valor(no.value, valores)
                except (_NaoELiteral, TypeError):
                    pass
    return valores


# Cada exemplo das listas da versão de teste, com a conferência que tem de achá-lo (achado N3 da segunda volta).
EXEMPLOS = [("PALAVRAS_DO_WINDOWS", "K01", 2), ("PALAVRAS_DE_DETACHED", "K02", 1), ("PALAVRAS_DE_LICENCA", "K03", 1),
            ("PALAVRAS_DO_GIT", "K25", 2), ("PALAVRAS_DE_APAGAR", "K25", 2)]


def exemplos_que_o_porteiro_nao_acha(fonte_da_versao_de_teste: str) -> list[str]:
    """Os exemplos das listas da versão de teste que o porteiro DESTE ramo não acha mais (afrouxar pelo uso).

    Cada exemplo vira uma linha de um arquivo do programa (`atualizacao.py`) e passa pelo porteiro de agora; se a
    conferência daquela lista não acusar a linha, a busca foi afrouxada: tirando palavra, mudando o jeito de juntar as
    palavras ou o que conta como programa. Gerado a partir dos dados da versão de teste, nunca escrito à mão.
    """
    from . import porteiro

    valores = literais(fonte_da_versao_de_teste)
    faltam = []
    for nome, conferencia, posicao in EXEMPLOS:
        for entrada in valores.get(nome, []) or []:
            exemplo = entrada[posicao] if isinstance(entrada, (list, tuple)) and len(entrada) > posicao else None
            if not isinstance(exemplo, str):
                continue
            fonte = ('"""Exemplo da proteção."""\nimport ctypes\nimport os\nimport subprocess\n\n\n'
                     'def f(c, pasta, info, bandeiras, advapi32, a):\n    """Exemplo."""\n    ' + exemplo + "\n")
            achados = porteiro.conferir_codigo(["atualizacao.py"], lambda _c, f=fonte: f)
            if not any(a.conferencia == conferencia and a.linha == 9 for a in achados):
                faltam.append(f"{nome}: o porteiro deste ramo não acha mais o exemplo {exemplo!r} ({conferencia})")
    # A K25 lê o comando de vários jeitos (a chamada, a lista guardada, o texto guardado, os arquivos do terminal):
    # um exemplo de cada, com o arquivo inteiro e a linha que tem de ser acusada (achado 4 de quem quebrou, 20/11).
    for entrada in valores.get("EXEMPLOS_DA_K25", []) or []:
        if not (isinstance(entrada, (list, tuple)) and len(entrada) >= 4):
            continue
        caminho, texto, linha, jeito = entrada[:4]
        achados = porteiro.conferir_codigo([caminho], lambda _c, f=texto: f)
        if not any(a.conferencia == "K25" and a.linha == linha for a in achados):
            faltam.append(f"EXEMPLOS_DA_K25: o porteiro deste ramo não acha mais {jeito} ({caminho}, linha {linha}) "
                          "(K25)")
    return faltam


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

    frases = mudancas_na_lista(excecoes.ler(raiz, lista_antes), excecoes.ler(raiz))
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
    fonte_base = git.conteudo_no_commit(raiz, base, "regras_dos_agentes/porteiro.py")
    if fonte_base is not None:
        frases += exemplos_que_o_porteiro_nao_acha(fonte_base)
    return frases
