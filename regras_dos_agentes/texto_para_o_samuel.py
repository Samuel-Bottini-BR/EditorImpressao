"""O texto curto que a gerente mostra ao Samuel para ele dizer "sim" à lista de exceções (D-791; CLAUDE.md §11.13).

Sai da própria lista (os números são contados aqui, nunca escritos à mão), em português comum: o que é, quantos
lugares, em que parte do trabalho cada grupo some, e os 5 que ficam para depois da entrega (D-800). Sem número de
decisão, nome de arquivo nem código no meio do texto (§11.13, regra 2).

Seguro mexer: as frases. Arriscado: a conta (vem de `excecoes.resumo`) e os nomes de cada grupo (`GRUPOS`), que dizem
ao Samuel o que cada passo conserta.
"""

from __future__ import annotations

from .excecoes import DEPOIS_DA_ENTREGA, Lista, resumo

# O que cada passo do plano conserta, dito como o Samuel conhece (a ordem é a do plano).
GRUPOS = [
    ("2", "quando a gente arrumar o publicar das versões"),
    ("3", "quando a gente arrumar a atualização sozinha"),
    ("4", "quando a gente arrumar os testes à distância"),
    ("5", "quando a gente arrumar o desinstalar"),
]


# Os lugares de fora da parte do Windows (D-800), ditos como o Samuel conhece, por arquivo.
DE_FORA = {
    "ui/automatico.py": "as dicas do Automático que mostram um número ao Kaique",
    "teste_velocidade.py": "o teste de velocidade, que abre o PowerShell por conta própria",
    "avaliar.py": "a régua dos filtros, que pergunta ao Windows onde fica a Área de Trabalho",
}


def _lugares(n: int) -> str:
    """'1 lugar' ou 'N lugares'."""
    return f"{n} lugar" if n == 1 else f"{n} lugares"


def texto(lista: Lista) -> str:
    """O texto para o Samuel, montado a partir da lista."""
    r = resumo(lista)
    por_passo = r["por_passo"]
    no_plano = sum(v for k, v in por_passo.items() if k != DEPOIS_DA_ENTREGA)
    fora = por_passo.get(DEPOIS_DA_ENTREGA, 0)
    linhas = [
        "**O que é:** o porteiro é a conferência automática que barra um trabalho de agente quando o código tem um erro "
        "que já conhecemos (por exemplo, pedir licença ao Windows por fora da peça única, ou um número de decisão "
        "aparecendo na tela). Ele roda nos testes do GitHub, em toda entrega.",
        "",
        f"**O que já está errado hoje:** o porteiro leu o programa e achou {_lugares(r['lugares'])} com esses erros. "
        "Eles ficam numa lista de exceções: o porteiro deixa passar só esses e barra qualquer erro novo. A lista só "
        "diminui: cada conserto tira o seu lugar.",
        "",
        f"**Quando cada grupo some ({_lugares(no_plano)} no plano da parte do Windows):**",
        "",
    ]
    for passo, nome in GRUPOS:
        if por_passo.get(passo):
            linhas.append(f"- {_lugares(por_passo[passo])}: {nome}.")
    if fora:
        por_arquivo: dict[str, int] = {}
        for item in lista.itens:
            if item["passo"] == DEPOIS_DA_ENTREGA:
                por_arquivo[item["arquivo"]] = por_arquivo.get(item["arquivo"], 0) + int(item["quantas"])
        partes = [f"{DE_FORA.get(a, a)} ({_lugares(n)})" for a, n in por_arquivo.items()]
        linhas += ["", f"**Os {fora} que ficam para depois da entrega ao Kaique, como você escolheu:** "
                   + "; ".join(partes) + "."]
    linhas += [
        "",
        "**O que você escolhe:** sim, a lista entra assim e o porteiro passa a barrar; ou não, e diga o que mudar. "
        "Sugestão: sim. Nada do programa muda com isso: é só a conferência dos trabalhos dos agentes.",
    ]
    return "\n".join(linhas)
