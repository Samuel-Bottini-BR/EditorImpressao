"""O montador do pacote de regras de um trabalho (D-784; veio do esboço da proposta das regras).

Palavras do Samuel (D-784, 18/11): "ok, mas como vai saber que regras enviar para o agente?" · "ok". A gerente diz o
papel, os arquivos que o trabalho mexe (os que existem e os novos, com "novo:" na frente), as decisões do Livro que o
pedido toca, o commit de partida e o ramo. O programa devolve o texto que o agente recebe:
  1. o pedido (papel, partida, ramo e os arquivos que ele pode mexer), que ele copia sem mudar para o ONDE-PAREI: o
     porteiro lê dali (D-796) e a gerente compara com o pacote guardado;
  2. as regras "sempre" (10);
  3. as regras das etiquetas que saem dos arquivos (`tabela_arquivos.etiquetas_do_trabalho`), só as do papel dele,
     com o aviso das contradições (as já resolvidas pelo Samuel dizem qual texto vale);
  4. as decisões, com as palavras copiadas do Livro (`livro.py`, nunca de memória);
  5. o formulário da entrega com os campos que essas etiquetas exigem (`formulario.CAMPOS`, os mesmos títulos que o
     programa confere, escolhidos pela mesma função, `formulario.vale_para`), já como títulos de seção para
     preencher;
  6. o que ele NÃO recebeu e quando parar.

Quem tenta quebrar (papel "quebrador") recebe todas as regras (D-775) e, no lugar do formulário, os seis campos do
relatório dele.

Seguro mexer: o texto em volta. Arriscado: a escolha das regras (`escolher_regras`), que decide o que o agente lê.
"""

from __future__ import annotations

from pathlib import Path

from . import catalogo, excecoes, formulario, tabela_arquivos
from .pedido import coberto
from .livro import Livro
from .pedido import Pedido

PAPEIS = {"implementador": {"todos", "codigo"}, "layout": {"todos", "codigo", "layout"},
          "verificador": {"todos", "verif"}, "pesquisador": {"todos", "pesq"},
          "quebrador": {"todos", "codigo", "verif", "layout", "pesq"}}
ORDEM_DAS_ETIQUETAS = ("WIN", "TELA", "IMG", "TESTE", "PERG", "GIT", "PESQ", "TODO")


def escolher_regras(tags: set, papel: str) -> list[dict]:
    """As regras do catálogo para estas etiquetas e este papel, sem as que o "sempre" já cobre."""
    cobertas = {i for s in catalogo.SEMPRE for i in s["cobre"]} | {"R135"}   # R135: o formulário substitui
    quem = PAPEIS[papel]
    if papel == "quebrador":          # quem tenta quebrar recebe a lista completa (D-775)
        tags = set(catalogo.ETIQUETAS) - {"GER"}
    saida = []
    for r in catalogo.REGRAS:
        if r["papel"] not in quem or r["id"] in cobertas:
            continue
        # Regra com assunto (tela, Windows, imagem, perguntas, git, pesquisa) só vai se o trabalho tem esse assunto;
        # regra só de "todo trabalho" ou só de "testes" vai sempre que o trabalho tem testes ou é de todo trabalho.
        assunto = set(r["tags"]) - {"TODO", "TESTE", "GER"}
        if "GER" in r["tags"] and not assunto and "TODO" not in r["tags"]:
            continue
        # Regra marcada `basta_uma`: vai a todo trabalho que tem QUALQUER uma das etiquetas dela (ex.: a R157, para o
        # trabalho do Windows e para o de testes, como a D-810 pede).
        if r.get("basta_uma"):
            if set(r["tags"]) & tags:
                saida.append(r)
            continue
        if assunto:
            if assunto & tags:
                saida.append(r)
        elif "TODO" in r["tags"] or ("TESTE" in r["tags"] and "TESTE" in tags):
            saida.append(r)
    return saida


def formulario_em_branco(tags: set, papel: str) -> list[str]:
    """Os títulos de seção do formulário (ou dos seis campos de quem quebra), com a etapa em que passam a valer."""
    if papel == "quebrador":
        return [f"## {titulo}\n\n(a preencher)\n" for _, titulo in formulario.CAMPOS_DE_QUEM_QUEBRA]
    saida = []
    for codigo, titulo, etapa, quem in formulario.CAMPOS:
        if codigo == "F1" or not formulario.vale_para(quem, tags):
            continue          # F1 já vem preenchido no pedido
        quando = f"obrigatório {formulario.NOME_DAS_ETAPAS[etapa]}"
        if codigo in formulario.SO_COM_PERGUNTAS:
            quando = (f"{quando}, se houver pergunta para o Samuel: um \"###\" por pergunta, com o mesmo título, as "
                      "decisões do Livro procuradas e \"Por que ainda não está respondida: ...\"")
        saida.append(f"## {titulo}\n\n(a preencher; {quando})\n")
    return saida


def lugares_da_lista(arquivos: list[str], raiz: Path, passo: str | None = None) -> list[str]:
    """Os lugares da lista de exceções nos arquivos do pedido, com o aviso de como a lista funciona (achado 11).

    A lista identifica cada lugar pela função e pelo texto da linha: mexer numa dessas linhas sem consertá-la, ou
    renomear ou mover a função onde ela está, vira erro novo (e nenhum item entra na lista por ramo de agente). Quem
    conserta tira o item no mesmo commit (`python -m regras_dos_agentes excecoes --diminuir`). Com `passo`, diz também
    quais funções guardam lugares de OUTROS passos e não podem ser renomeadas nem movidas neste (achado Q3 da quarta
    volta de quem quebrou).
    """
    caminho = Path(raiz) / excecoes.ARQUIVO_DA_LISTA
    if not caminho.exists():
        return []
    lista = excecoes.ler(raiz)
    nos_arquivos = [i for i in lista.itens if coberto(i["arquivo"], [a.removeprefix("novo:") for a in arquivos])]
    if not nos_arquivos:
        return []
    saida = ["## Lugares da lista de exceções nos seus arquivos", "",
             f"{sum(int(i['quantas']) for i in nos_arquivos)} lugares. Cada um é identificado pela função e pelo texto da "
             "linha: mexer numa dessas linhas sem consertá-la, ou renomear ou mover a função onde ela está, vira erro "
             "novo (e nenhum item entra na lista por ramo de agente). Quem conserta tira o item no mesmo commit "
             "(`python -m regras_dos_agentes excecoes --diminuir`).", ""]
    if passo is not None:
        outras = sorted({(i["arquivo"], i["funcao"] or "(fora de função)", i["passo"]) for i in nos_arquivos
                         if i["passo"] != passo})
        if outras:
            saida += [f"**Não renomeie nem mova estas funções neste trabalho (passo {passo}): elas guardam lugares de "
                      "outros passos, e o lugar é a função e o texto.**", ""]
            saida += [f"- `{a}`, função `{f}` (lugares do passo {p})" for a, f, p in outras]
            saida.append("")
    saida += [f"- {i['conferencia']} `{i['arquivo']}` ({i['funcao'] or 'fora de função'}, passo {i['passo']}, "
              f"{i['quantas']}x): `{i['texto'][:90]}`" for i in nos_arquivos]
    return saida + [""]


def montar(papel: str, titulo: str, numeros: list[str], arquivos: list[str], raiz: Path, partida: str,
           ramo: str, passo: str | None = None) -> str:
    """O texto do pacote."""
    if papel not in PAPEIS:
        raise ValueError(f"papel desconhecido: {papel} (vale: {', '.join(PAPEIS)})")
    tags, avisos = tabela_arquivos.etiquetas_do_trabalho(arquivos, raiz)
    regras = escolher_regras(tags, papel)
    nomes = ", ".join(catalogo.ETIQUETAS[t] for t in sorted(tags) if t in catalogo.ETIQUETAS and t != "GER")
    fora = sorted(set(catalogo.ETIQUETAS) - tags - {"GER", "TODO"}) if papel != "quebrador" else []
    livro = Livro.do_repositorio(raiz)
    pedido = Pedido(papel=papel, partida=partida, ramo=ramo, arquivos=list(arquivos))

    p = [f"# Pacote de regras: {titulo}", "",
         f"Papel: **{papel}**. Tipo de trabalho (sai dos arquivos): {nomes}.", ""]
    p += [f"> Aviso à gerente: {a}" for a in avisos]
    p += ["", "Copie as duas seções abaixo, sem mudar nada, para o começo do seu ONDE-PAREI: o porteiro lê dali quais "
          "arquivos você pode mexer, e a gerente compara com este pacote.", "", pedido.bloco()]
    p += lugares_da_lista(arquivos, raiz, passo)
    p += ["## 1. Sempre (todo trabalho)", ""]
    for s in catalogo.SEMPRE:
        p.append(f"{s['n']}. **{s['titulo']}.** {s['texto']} *Por quê:* {s['porque']}")
    p += ["", f"## 2. As regras do seu trabalho ({len(regras)})", ""]
    por_tag: dict[str, list] = {}
    for r in regras:
        chave = next((t for t in ORDEM_DAS_ETIQUETAS if t in r["tags"] and t in tags | {"TODO"}), "TODO")
        por_tag.setdefault(chave, []).append(r)
    for t in ORDEM_DAS_ETIQUETAS:
        if t in por_tag:
            p.append(f"**{catalogo.ETIQUETAS[t].capitalize()}**")
            for r in por_tag[t]:
                p.append(f"- {r['nome']}: {r['curta']} ({r['onde'][0]}){catalogo.aviso_de_contradicao(r)}")
            p.append("")
    p += ["## 3. As decisões que este trabalho precisa cumprir (copiadas do Livro)", ""]
    p += [livro.resumo(n) for n in numeros] if numeros else ["- (a gerente põe aqui as decisões do pedido)"]
    p += ["", "## 4. O formulário da entrega (no seu ONDE-PAREI; um programa confere, campo vazio volta)", "",
          "Use estes títulos de seção, exatamente assim. \"Não se aplica\" só vale com o motivo (\"não se aplica: "
          "este passo não pede licença ao Windows\"). Nas decisões, as palavras do Samuel vêm entre aspas logo depois "
          "do número, copiadas do Livro; o seu comentário vem depois de \"Aqui:\". Confira antes de entregar: "
          "`python -m regras_dos_agentes entrega relatorios/<pasta>/ONDE-PAREI.md --etapa quebrar`.", ""]
    p += formulario_em_branco(tags, papel)
    p += ["## 5. O que você não recebeu, e quando parar", "",
          f"Este pacote não traz as regras de: {', '.join(catalogo.ETIQUETAS[t] for t in fora) or 'nada (recebeu todas)'}. "
          "Se precisar mexer num arquivo fora da lista do pedido, pare e avise a gerente: o pacote muda. "
          "Se tiver pergunta para o Samuel, a regra 8 acima é o mínimo; a lista inteira está no CLAUDE.md §11.13, e a "
          "gerente devolve a pergunta que não passar. "
          "O texto que vale é o do CLAUDE.md (nas regras novas do catálogo dos erros, ainda não escritas lá, a decisão "
          "do Livro): a fonte de cada regra está entre parênteses; leia lá quando tiver dúvida.",
          ""]
    return "\n".join(p)
