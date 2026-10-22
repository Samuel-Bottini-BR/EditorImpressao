"""Item 2.19 (parte 2): perfis de configuração ("receitas"), igual ao ScanTailor.

O QUE FAZ
    O ScanTailor guarda "perfis" das opções de um projeto (Settings, "Default
    parameters": src/core/DefaultParams*, DefaultParamsProfileManager): o
    "Default" (o de fábrica), o "Source" e os que a pessoa salvar com um nome;
    um perfil escolhido vale para os projetos NOVOS. Aqui é o mesmo para as
    escolhas do livro inteiro (as caixinhas da tela "O que fazer": dividir,
    endireitar, cortar, o filtro do livro, as gravuras, o "Só as letras", o
    limpar pontinhos, as margens iguais, os cadernos...): guardar com um nome,
    pôr num livro, e escolher um para todo livro novo.

    A conferência do layout de 12/10/2026 chamou isso de "receitas" (Registro
    12/10/2026: "Pendências sem etapa nem dono"); na tela o nome é "receita".

ONDE FICA: configuracoes.json, chave "perfis" ({nome: {campo: valor}}) e
    "perfil_do_livro_novo" (o nome, ou "" = o de fábrica, que é não mexer em
    nada). Preferência da máquina, não do livro.

DESLIGADO DE FÁBRICA: sem receita escolhida para livro novo, nada muda.

O QUE NÃO ENTRA: o que é de cada folha e de cada página (corte, ângulo,
    marcação) - receita é do livro. Nem o que é fato do PDF (tem_camadas) ou
    história do projeto (ordem_do_preparo, perguntou_fundo).

SEGURO MUDAR: CAMPOS (acrescentar campo de livro novo).
ARRISCADO: pôr em CAMPOS um campo que diz como o projeto foi gravado
    (ordem_do_preparo: um livro antigo mudaria de corte).
"""

from __future__ import annotations

import copy
from typing import Any

# As escolhas do livro inteiro que uma receita leva (campos de modelos.Projeto).
CAMPOS = (
    "dividir_folhas", "dividir_como", "cortar_sobra", "limpar", "filtro_padrao",
    "endireitar", "endireitar_como", "cortar_bordas", "montar_cadernos",
    "paginas_por_caderno", "detectar_regioes",
    "gravura_forma", "gravura_sensibilidade", "gravura_mais_sensivel", "gravura_normalizar",
    "pb_decoracao_em_preto_e_branco",
    "misto_so_as_letras", "misto_fora_do_texto", "misto_papel_da_gravura",
    "misto_letras_na_moldura", "limpar_pontinhos",
    "margens_iguais", "margens_mm", "margens_alinhamento",
)

CHAVE_DOS_PERFIS = "perfis"
CHAVE_DO_LIVRO_NOVO = "perfil_do_livro_novo"
NOME_DE_FABRICA = "De fábrica"


def _ler(chave: str, padrao):
    try:
        import configuracoes

        valor = configuracoes.ler(chave)
    except Exception:  # noqa: BLE001
        return padrao
    return padrao if valor is None else valor


def _escrever(chave: str, valor) -> None:
    import configuracoes

    configuracoes.escrever(chave, valor)


def do_projeto(projeto) -> dict[str, Any]:
    """As escolhas do livro, prontas para guardar (cópias)."""
    return {campo: copy.deepcopy(getattr(projeto, campo)) for campo in CAMPOS
            if hasattr(projeto, campo)}


def de_fabrica() -> dict[str, Any]:
    """A receita "De fábrica": as escolhas de um livro novo sem nada mudado."""
    from modelos import Projeto

    return do_projeto(Projeto(caminho_entrada=""))


def nomes() -> list[str]:
    """As receitas guardadas, em ordem alfabética ("De fábrica" sempre existe,
    e vem primeiro)."""
    perfis = _ler(CHAVE_DOS_PERFIS, {})
    guardados = sorted(n for n in perfis if isinstance(perfis.get(n), dict))
    return [NOME_DE_FABRICA] + [n for n in guardados if n != NOME_DE_FABRICA]


def ler(nome: str) -> dict[str, Any] | None:
    if nome == NOME_DE_FABRICA:
        return de_fabrica()
    perfil = _ler(CHAVE_DOS_PERFIS, {}).get(nome)
    return dict(perfil) if isinstance(perfil, dict) else None


def guardar(nome: str, projeto) -> str:
    """Guarda as escolhas do livro com o nome dado. Devolve o nome usado ("De
    fábrica" não pode ser trocado: ganha "(minha)")."""
    nome = (nome or "").strip() or "Minha receita"
    if nome == NOME_DE_FABRICA:
        nome = f"{NOME_DE_FABRICA} (minha)"
    perfis = dict(_ler(CHAVE_DOS_PERFIS, {}))
    perfis[nome] = do_projeto(projeto)
    _escrever(CHAVE_DOS_PERFIS, perfis)
    return nome


def apagar(nome: str) -> bool:
    if nome == NOME_DE_FABRICA:
        return False
    perfis = dict(_ler(CHAVE_DOS_PERFIS, {}))
    if nome not in perfis:
        return False
    del perfis[nome]
    _escrever(CHAVE_DOS_PERFIS, perfis)
    if _ler(CHAVE_DO_LIVRO_NOVO, "") == nome:
        _escrever(CHAVE_DO_LIVRO_NOVO, "")
    return True


def aplicar(nome: str, projeto) -> bool:
    """Põe a receita no livro (só os campos que ela tem e que o livro conhece;
    valor estranho de um campo é corrigido por quem o lê, como sempre)."""
    perfil = ler(nome)
    if perfil is None:
        return False
    for campo, valor in perfil.items():
        if campo in CAMPOS and hasattr(projeto, campo):
            setattr(projeto, campo, copy.deepcopy(valor))
    return True


def do_livro_novo() -> str:
    """O nome da receita de todo livro novo ("" = nenhuma: o de fábrica)."""
    nome = _ler(CHAVE_DO_LIVRO_NOVO, "")
    return nome if nome and ler(nome) is not None else ""


def definir_do_livro_novo(nome: str) -> None:
    _escrever(CHAVE_DO_LIVRO_NOVO, "" if nome in ("", NOME_DE_FABRICA) else nome)


def aplicar_no_livro_novo(projeto) -> str:
    """Chamado quando um livro é aberto pela primeira vez: põe a receita
    escolhida para livro novo, se houver. Devolve o nome ("" = nenhuma)."""
    nome = do_livro_novo()
    if nome:
        aplicar(nome, projeto)
    return nome
