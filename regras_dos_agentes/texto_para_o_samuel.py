"""O texto curto que a gerente mostra ao Samuel para ele dizer "sim" à lista de exceções (D-791; CLAUDE.md §11.13).

Sai da própria lista (os números são contados aqui, nunca escritos à mão), em português comum: o que é e onde fica,
um caso real (um lugar de verdade do código de hoje que o porteiro acha, contado sem código), o que o porteiro faz e o
que ele não faz, em que parte do trabalho cada grupo some e o que ele deixou para depois da entrega: os 5 primeiros
(D-800) e os 56 da busca ampliada (D-802, 19/11: "ok, continuamos assim e vamos proceguir"). Lugar que nenhuma regra
classifica ("fora do plano") ainda vira pergunta no fim. Sem número de decisão, nome de arquivo nem código no meio do
texto (§11.13, regra 2).

D-802 (19/11): a pergunta dos 56 saiu; os 56 aparecem em "ficam para depois da entrega", com o que cada pedaço faz.

Refeito em 19/11 depois de quem tentou quebrar (achado 8): a imagem do próprio texto não provava nada, faltava o caso
real, e "barra qualquer erro novo" prometia mais do que o porteiro faz.

Seguro mexer: as frases. Arriscado: a conta (vem de `excecoes.resumo`), a separação por decisão (vem de
`excecoes.decisao_que_deixou_para_depois`, nunca de uma lista de funções copiada aqui) e os nomes de cada grupo
(`GRUPOS`, `DE_FORA`, `O_QUE_O_PEDACO_FAZ`), que dizem ao Samuel o que cada passo conserta.
"""

from __future__ import annotations

from .excecoes import DEPOIS_DA_ENTREGA, FORA_DO_PLANO, Lista, decisao_que_deixou_para_depois, resumo

# O que cada passo do plano conserta, dito como o Samuel conhece (a ordem é a do plano).
GRUPOS = [
    ("2", "quando a gente arrumar o publicar das versões"),
    ("3", "quando a gente arrumar a atualização sozinha"),
    ("4", "quando a gente arrumar os testes à distância"),
    ("5", "quando a gente arrumar o desinstalar"),
]

# Os 5 pedaços que ele deixou para depois da entrega primeiro (D-800), ditos como ele conhece, por arquivo. Do teste
# de velocidade, a D-800 foi só a leitura da placa de vídeo e do disco pelo PowerShell (R4 da terceira volta de quem
# quebrou); o resto do teste de velocidade é da D-802 (`O_QUE_O_PEDACO_FAZ`).
DE_FORA = {
    "ui/automatico.py": "as duas dicas do Automático que mostram um número ao Kaique",
    "teste_velocidade.py": "o teste de velocidade lendo a placa de vídeo e o tipo de disco pelo PowerShell",
    "avaliar.py": "a régua dos filtros, que pergunta ao Windows onde fica a Área de Trabalho",
}
# Quantos lugares a conta de 19/11 (D-800) tinha em cada um desses pedaços.
NA_DECISAO_DELE = {"ui/automatico.py": 2, "teste_velocidade.py": 2, "avaliar.py": 1}

# Os 56 pedaços da busca ampliada (D-802; antes eram a pergunta "fora do plano"), ditos como ele conhece, por arquivo:
# o que aquele pedaço faz com o Windows. Também diz o pedaço de um lugar que ainda esteja "fora do plano".
O_QUE_O_PEDACO_FAZ = {
    "teste_velocidade.py": "o resto do teste de velocidade: ele lê a memória do computador e do próprio teste, lê no "
                           "registro do Windows o nome do Windows, do processador e da placa de vídeo, impede o "
                           "computador de dormir durante a medida e mexe na janela preta onde roda",
    "historico.py": "a tela de início abre a pasta do projeto e manda imprimir pelo Windows",
    "core/nucleos.py": "o programa pergunta ao Windows quanta memória está livre",
    "core/ocr_comum.py": "o motor de achar texto ajusta, no Windows, onde procurar as bibliotecas dele",
    "ui/brasao_girando.py": "o brasão que gira pergunta ao Windows se o programa ainda está aberto",
    "empacotar_teste_velocidade.py": "o pacote do teste de velocidade abre a janela preta pelo Windows",
}

# O print do caso real (uma cópia do print da instalação de 18/11, com o botão marcado), ao lado do texto.
PRINT_DO_CASO_REAL = "prints/caso-real-reiniciar-agora.png"


def _lugares(n: int) -> str:
    """'1 lugar' ou 'N lugares'."""
    return f"{n} lugar" if n == 1 else f"{n} lugares"


def _por_arquivo(lista: Lista, passo: str, decisao: str | None = "qualquer") -> dict[str, int]:
    """Quantos lugares de um passo há em cada arquivo, na ordem da lista.

    `decisao`: só os lugares que essa decisão deixou para depois ("D-800", "D-802"; None = de nenhuma), pela mesma
    regra que deu o passo (`excecoes.decisao_que_deixou_para_depois`). "qualquer" não separa.
    """
    contagem: dict[str, int] = {}
    for item in lista.itens:
        if item["passo"] != passo:
            continue
        if decisao != "qualquer" and decisao_que_deixou_para_depois(
                item["arquivo"], item["conferencia"], item["funcao"]) != decisao:
            continue
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
        "**Um caso real:** o botão \"Reiniciar agora\", da janela de versão nova, abre o PowerShell de um jeito que o "
        "faz fechar sem rodar (foi um dos defeitos da instalação no seu computador, em 18/11). A conferência acha esse "
        "jeito no código.",
        "",
        f"![O botão \"Reiniciar agora\" marcado em vermelho, no print da instalação de 18/11]({PRINT_DO_CASO_REAL})",
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
        partes = []
        # Primeiro os 5 pedaços que ele deixou para depois primeiro (D-800), com a conta daquela hora.
        for a, n in _por_arquivo(lista, DEPOIS_DA_ENTREGA, "D-800").items():
            antes = NA_DECISAO_DELE.get(a)
            conta = f"; na conta de 19/11 eram {antes}, a busca maior achou mais linhas no mesmo pedaço" if (
                antes is not None and antes != n) else ""
            partes.append(f"- {DE_FORA.get(a, 'outro pedaço')} ({_lugares(n)}{conta}).")
        # Depois os que conversam com o Windows por conta própria, que ele deixou para depois em seguida (D-802).
        # Um "depois da entrega" sem decisão conhecida (não deve existir) também aparece aqui, nunca some do texto.
        outros = _por_arquivo(lista, DEPOIS_DA_ENTREGA, "D-802")
        for a, n in _por_arquivo(lista, DEPOIS_DA_ENTREGA, None).items():
            outros[a] = outros.get(a, 0) + n
        if outros:
            partes += ["", "E os pedaços que conversam com o Windows por conta própria, que você deixou para depois "
                       "logo em seguida:", ""]
            partes += [f"- {O_QUE_O_PEDACO_FAZ.get(a, 'outro pedaço do programa')} ({_lugares(n)})."
                       for a, n in sorted(outros.items(), key=lambda x: -x[1])]
        linhas += ["", f"**Ficam para depois da entrega ao Kaique, como você escolheu em 19/11 ({_lugares(depois)}):**",
                   "", *partes]
    linhas += [
        "",
        "**O que você escolhe:** sim, a lista entra assim e a conferência passa a barrar; ou não, e diga o que mudar "
        "(enquanto não entra, a conferência não barra nada no código). Sugestão: sim. Nada do programa muda com isso, "
        "e nada do que já funciona muda.",
        "",
        "**De onde veio:** do seu \"sim\" de 19/11 à lista que só diminui. A conta saiu do próprio programa que confere.",
    ]
    if fora:
        partes = [f"- {O_QUE_O_PEDACO_FAZ.get(a, 'outro pedaço do programa')} ({_lugares(n)})."
                  for a, n in sorted(_por_arquivo(lista, FORA_DO_PLANO).items(), key=lambda x: -x[1])]
        linhas += [
            "",
            f"**Uma pergunta a mais: {_lugares(fora)} novos, fora do plano.** Procurando com mais palavras, a "
            "conferência achou outros pedaços do programa que conversam com o Windows por conta própria e que o plano "
            "da parte do Windows não conserta:",
            "",
            *partes,
            "",
            "**O que você escolhe para esses:** ficam para depois da entrega ao Kaique, como os outros pedaços que você "
            "já deixou para depois (ficam na lista até lá); ou entram no plano (cada um vira conserto antes da "
            "entrega). Sugestão: depois da entrega, como você decidiu para os outros. Nada do programa muda com "
            "nenhuma das duas escolhas agora.",
            "",
            # Achado Q7 da quarta volta: a gerente aceitou sem print, com esta ressalva escrita no próprio texto.
            "**Ressalva: esta pergunta não tem print.** Esses pedaços são código que não aparece na tela: conversam com "
            "o Windows por baixo, sem janela nem botão. Não há o que fotografar; o que existe é a linha do código, que "
            "está na lista.",
        ]
    return "\n".join(linhas)
