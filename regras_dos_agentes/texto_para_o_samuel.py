"""O texto curto que a gerente mostra ao Samuel para ele dizer "sim" à lista de exceções (D-791; CLAUDE.md §11.13).

Sai da própria lista (os números são contados aqui, nunca escritos à mão), em português comum: o que é e onde fica,
um caso real (um lugar de verdade do código de hoje que o porteiro acha, contado sem código), o que o porteiro faz e o
que ele não faz, em que parte do trabalho cada grupo some, os 5 que ele deixou para depois da entrega (D-800) e, como
pergunta, os lugares novos fora do plano (achados pela busca ampliada em 19/11). Sem número de decisão, nome de
arquivo nem código no meio do texto (§11.13, regra 2).

Refeito em 19/11 depois de quem tentou quebrar (achado 8): a imagem do próprio texto não provava nada, faltava o caso
real, e "barra qualquer erro novo" prometia mais do que o porteiro faz.

Seguro mexer: as frases. Arriscado: a conta (vem de `excecoes.resumo`) e os nomes de cada grupo (`GRUPOS`, `DE_FORA`,
`FORA_DO_PLANO`), que dizem ao Samuel o que cada passo conserta.
"""

from __future__ import annotations

from .excecoes import DEPOIS_DA_ENTREGA, FORA_DO_PLANO, Lista, resumo

# O que cada passo do plano conserta, dito como o Samuel conhece (a ordem é a do plano).
GRUPOS = [
    ("2", "quando a gente arrumar o publicar das versões"),
    ("3", "quando a gente arrumar a atualização sozinha"),
    ("4", "quando a gente arrumar os testes à distância"),
    ("5", "quando a gente arrumar o desinstalar"),
]

# Os lugares que ele deixou para depois da entrega (D-800), ditos como ele conhece, por arquivo.
DE_FORA = {
    "ui/automatico.py": "as dicas do Automático que mostram um número ao Kaique",
    "teste_velocidade.py": "o teste de velocidade, que abre o PowerShell por conta própria",
    "avaliar.py": "a régua dos filtros, que pergunta ao Windows onde fica a Área de Trabalho",
}

# Os lugares novos fora do plano, ditos como ele conhece, por arquivo (o que aquele pedaço faz com o Windows).
FORA_DO_PLANO_POR_ARQUIVO = {
    "teste_velocidade.py": "o teste de velocidade lê a memória, a placa de vídeo e o disco direto no Windows e mexe na "
                           "janela preta onde ele roda",
    "historico.py": "a tela de início abre a pasta do projeto e manda imprimir pelo Windows",
    "core/nucleos.py": "o programa pergunta ao Windows quanta memória está livre",
    "core/ocr_comum.py": "o motor de achar texto ajusta, no Windows, onde procurar as bibliotecas dele",
    "ui/brasao_girando.py": "o brasão que gira pergunta ao Windows se o programa ainda está aberto",
    "empacotar_teste_velocidade.py": "o pacote do teste de velocidade abre a janela preta pelo Windows",
}


def _lugares(n: int) -> str:
    """'1 lugar' ou 'N lugares'."""
    return f"{n} lugar" if n == 1 else f"{n} lugares"


def _por_arquivo(lista: Lista, passo: str) -> dict[str, int]:
    """Quantos lugares de um passo há em cada arquivo."""
    contagem: dict[str, int] = {}
    for item in lista.itens:
        if item["passo"] == passo:
            contagem[item["arquivo"]] = contagem.get(item["arquivo"], 0) + int(item["quantas"])
    return contagem


def texto(lista: Lista) -> str:
    """O texto para o Samuel, montado a partir da lista."""
    r = resumo(lista)
    por_passo = r["por_passo"]
    no_plano = sum(por_passo.get(p, 0) for p, _ in GRUPOS)
    depois = por_passo.get(DEPOIS_DA_ENTREGA, 0)
    fora = por_passo.get(FORA_DO_PLANO, 0)
    linhas = [
        "**O que é e onde fica:** é a conferência automática dos trabalhos dos agentes. Ela roda nos testes do GitHub, "
        "em toda entrega; você não vê nada dela no programa.",
        "",
        "**Um caso real:** o botão \"Reiniciar agora\", do aviso de versão nova, abre o PowerShell de um jeito que o "
        "faz fechar sem rodar (foi um dos defeitos da instalação no seu computador, em 18/11). A conferência acha esse "
        "jeito no código. Outro caso: duas dicas do Automático mostram ao Kaique um número de decisão no meio do texto.",
        "",
        f"**O que já está errado hoje:** ela leu o programa e achou {_lugares(r['lugares'])} desses erros. Eles ficam "
        "numa lista: a conferência deixa passar esses e barra o trabalho de agente que acrescentar mais um lugar com "
        "um desses erros, escrito com as palavras que ela conhece. A lista só diminui: cada conserto tira o seu lugar.",
        "",
        "**O que ela não faz:** não pega o mesmo erro escrito de um jeito que ela não conhece, e não pega defeito que só "
        "aparece usando o programa (esses continuam indo para a lista de defeitos).",
        "",
        f"**Quando cada grupo some ({_lugares(no_plano)} no plano da parte do Windows):**",
        "",
    ]
    for passo, nome in GRUPOS:
        if por_passo.get(passo):
            linhas.append(f"- {_lugares(por_passo[passo])}: {nome}.")
    if depois:
        partes = [f"{DE_FORA.get(a, a)} ({_lugares(n)})" for a, n in _por_arquivo(lista, DEPOIS_DA_ENTREGA).items()]
        linhas += ["", f"**Os {depois} que ficam para depois da entrega ao Kaique, como você escolheu:** "
                   + "; ".join(partes) + "."]
    linhas += [
        "",
        "**O que você escolhe:** sim, a lista entra assim e a conferência passa a barrar; ou não, e diga o que mudar "
        "(enquanto não entra, a conferência não barra nada no código). Sugestão: sim. Nada do programa muda com isso, "
        "e nada do que já funciona muda.",
        "",
        "**De onde veio:** do seu \"sim\" de 19/11 à lista que só diminui. A conta saiu do próprio programa que confere.",
    ]
    if fora:
        partes = [f"- {FORA_DO_PLANO_POR_ARQUIVO.get(a, a)} ({_lugares(n)})."
                  for a, n in sorted(_por_arquivo(lista, FORA_DO_PLANO).items(), key=lambda x: -x[1])]
        linhas += [
            "",
            f"**Uma pergunta a mais: {_lugares(fora)} novos, fora do plano.** Procurando com mais palavras, a "
            "conferência achou outros pedaços do programa que conversam com o Windows por conta própria e que o plano "
            "da parte do Windows não conserta:",
            "",
            *partes,
            "",
            "**O que você escolhe para esses:** ficam para depois da entrega ao Kaique, como os outros 5 (ficam na lista "
            "até lá); ou entram no plano (cada um vira conserto antes da entrega). Sugestão: depois da entrega, como você "
            "decidiu para os outros 5. Nada do programa muda com nenhuma das duas escolhas agora.",
        ]
    return "\n".join(linhas)
