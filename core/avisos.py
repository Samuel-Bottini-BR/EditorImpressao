"""A lista do "Para revisar" e o "está bom" em cada nivel (12/10/2026).

O PEDIDO
    Samuel, rodada 4 do "Para revisar" (08/10/2026, `rv4-aviso-so-texto`): "Eu
    tenho que conseguir fazer isso com uma pagina individual, com um motivo
    individual de uma pagina e com todas as paginas ou com todos os motivos de
    todas as paginas, e eu devo conseguir abrir um selecionador em aba grande
    mostrando todas as paginas com aquele problema e deselecionar ou dar ok em
    todas [...] quando alguém tentar imprimir sem ver os alertas o programa
    para e mostra os alertas e a pessoa diz se quer ver ou continuar". Rodada 5
    (`rv5-aviso-so-texto`): a janela "Antes de processar" "Lista as páginas e
    os motivos".

O QUE FAZ
    pendentes_do_livro() devolve, na ordem do livro, cada aviso que ainda pede
    um olhar (um por motivo de cada folha e de cada pagina). E a mesma lista
    para o painel "Para revisar", para a janela "Antes de processar" e para o
    seletor grande (ui/janela_dos_avisos.py).

    campos_para_aceitar() diz o que mudar no projeto para dar "está bom" num
    conjunto qualquer desses avisos - um motivo de uma pagina, todas as
    paginas de um motivo, ou tudo: cada item ganha os codigos em
    `alertas_aceitos` (modelos.ConfigPagina). Quem aplica e a tela, pelo
    historico (ui/tela_conferir._registrar), para o Ctrl+Z desfazer. "A
    pagina inteira esta boa" continua sendo o campo `revisada`.

Nao importa ui/. So le o projeto (nada aqui o muda). Seguro mudar: os textos
de nome_do_item. Arriscado: mudar a ordem de pendentes_do_livro sem olhar a
janela (ela mostra nessa ordem).
"""

from __future__ import annotations

from dataclasses import dataclass

from core import analise

FOLHA = "folha"
PAGINA = "pagina"


@dataclass(frozen=True)
class Aviso:
    """Um motivo de uma folha ou de uma pagina que ainda pede um olhar."""

    alvo: str          # FOLHA ou PAGINA (o mesmo "alvo" das acoes do desfazer)
    indice: int        # posicao em projeto.folhas ou projeto.paginas
    codigo: str        # o codigo do alerta (core/analise.py)

    @property
    def titulo(self) -> str:
        """O nome curto do motivo, como aparece na tela."""
        return analise.descrever(self.codigo).titulo

    @property
    def onde(self) -> str:
        """"Página 12" ou "Folha 3" (contando a partir de 1)."""
        return nome_do_item(self.alvo, self.indice)


def nome_do_item(alvo: str, indice: int) -> str:
    return f"{'Folha' if alvo == FOLHA else 'Página'} {indice + 1}"


def onde_no_livro(aviso: Aviso, projeto) -> str:
    """Onde está o aviso, sempre em PÁGINAS do livro (as da tira de
    miniaturas): "Página 4", ou "Páginas 1 e 2" para o aviso de uma folha que
    foi dividida. Só quando a folha não tem página nenhuma no livro (todas
    tiradas) sobra "Folha N", porque não há página para nomear.

    O defeito (verificador, 20/10/2026): a lista "Antes de processar"
    misturava "Folha N" e "Página N" - e depois de uma folha dividida a folha
    2 já não é a página 2. Seguro mudar: as palavras. Arriscado: voltar a
    usar o número da folha como se fosse o da página."""
    if aviso.alvo != FOLHA or projeto is None:
        return aviso.onde
    numeros = sorted(p.indice + 1 for p in projeto.paginas
                     if p.folha == aviso.indice and not p.apagada)
    if not numeros:
        return aviso.onde
    if len(numeros) == 1:
        return f"Página {numeros[0]}"
    return "Páginas " + ", ".join(str(n) for n in numeros[:-1]) + f" e {numeros[-1]}"


def _paginas_vivas_por_folha(projeto) -> dict[int, list]:
    """As paginas que vao para o PDF (nao apagadas), por folha."""
    vivas: dict[int, list] = {}
    for pagina in projeto.paginas:
        if not pagina.apagada:
            vivas.setdefault(pagina.folha, []).append(pagina)
    return vivas


def _folha_ainda_pede(projeto, folha, vivas: dict[int, list] | None = None) -> bool:
    """Os avisos de uma FOLHA ainda pedem um olhar? Nao, se a folha foi
    apagada, se todas as paginas dela foram tiradas do livro, ou se todas as
    paginas dela que vao para o PDF ja foram dadas como conferidas ("está
    certo" em cada uma). Folha sem pagina nenhuma conhecida: pede (como
    sempre).

    Etapa 7 da obra (26/10/2026; lista unica 5.5, "um numero so de duvidas";
    teste do Kaique: "356 páginas que você não conferiu" depois de "nada
    pendente"): o aviso de uma folha (o corte, o angulo, o tamanho) agora
    aparece na faixa das paginas dela (avisos_da_pagina), e o "está certo" de
    cada pagina responde por ele naquela pagina. Antes so o "está certo" do
    Dividir o tirava, e nas outras ferramentas o aviso ficava escondido,
    contado so no fim. Arriscado: voltar a contar a folha cujas paginas ja
    foram todas conferidas (o numero do fim volta a ser maior que o do painel)."""
    if getattr(folha, "apagada", False):
        return False
    if vivas is None:
        vivas = _paginas_vivas_por_folha(projeto)
    delas = vivas.get(folha.indice)
    if not delas:
        # nenhuma pagina viva: ou todas foram tiradas do livro (nao pede), ou
        # a folha nao tem pagina nenhuma conhecida (pede, como sempre)
        return not any(p.folha == folha.indice for p in projeto.paginas)
    return any(not p.revisada for p in delas)


def pendentes_do_livro(projeto) -> list[Aviso]:
    """Todos os avisos que ainda pedem um olhar, na ordem do livro: para cada
    folha, os dela (o corte, o angulo, o tamanho) e depois os das paginas que
    sairam dela. Folha e pagina apagadas ficam de fora (nao vao para o PDF);
    a folha cujas paginas ja foram todas conferidas tambem (_folha_ainda_pede)."""
    paginas_da_folha: dict[int, list] = {}
    for pagina in projeto.paginas:
        paginas_da_folha.setdefault(pagina.folha, []).append(pagina)
    vivas = _paginas_vivas_por_folha(projeto)
    avisos: list[Aviso] = []
    vistas: set[int] = set()
    for folha in projeto.folhas:
        if _folha_ainda_pede(projeto, folha, vivas):
            avisos.extend(Aviso(FOLHA, folha.indice, c) for c in folha.alertas_pendentes)
        for pagina in paginas_da_folha.get(folha.indice, []):
            vistas.add(pagina.indice)
            if not pagina.apagada:
                avisos.extend(Aviso(PAGINA, pagina.indice, c) for c in pagina.alertas_pendentes)
    for pagina in projeto.paginas:            # pagina sem folha conhecida (nunca visto)
        if pagina.indice not in vistas and not pagina.apagada:
            avisos.extend(Aviso(PAGINA, pagina.indice, c) for c in pagina.alertas_pendentes)
    return avisos


# Os avisos de folha que sao da DIVISAO: "ver" leva ao Dividir (D-501, etapa 4).
DA_DIVISAO = frozenset({analise.NAO_PARECE_DUPLA, analise.LOMBADA_INCERTA})


def avisos_da_pagina(projeto, indice: int) -> list[Aviso]:
    """Os avisos que a PAGINA `indice` mostra na faixa e no "Para revisar":
    primeiro os dela (o que acabou de mudar nela aparece na hora na faixa),
    depois os da folha dela que ainda pedem um olhar. Nenhum
    se a pagina foi tirada do livro ou ja foi dada como conferida (`revisada`:
    o "está certo" vale para tudo o que a faixa dela mostrou). Barato: so le
    campos. Etapa 7 da obra (um numero so de duvidas, lista unica 5.5)."""
    if projeto is None or not 0 <= indice < len(projeto.paginas):
        return []
    pagina = projeto.paginas[indice]
    if pagina.apagada or pagina.revisada:
        return []
    avisos: list[Aviso] = [Aviso(PAGINA, pagina.indice, c) for c in pagina.alertas_pendentes]
    if 0 <= pagina.folha < len(projeto.folhas):
        folha = projeto.folhas[pagina.folha]
        if not getattr(folha, "apagada", False):
            avisos.extend(Aviso(FOLHA, folha.indice, c) for c in folha.alertas_pendentes)
    return avisos


def avisos_da_folha(projeto, indice: int) -> list[Aviso]:
    """Os avisos que a FOLHA `indice` mostra no Dividir (onde se confere a
    folha inteira): os dela que ainda pedem um olhar (_folha_ainda_pede)."""
    if projeto is None or not 0 <= indice < len(projeto.folhas):
        return []
    folha = projeto.folhas[indice]
    if not _folha_ainda_pede(projeto, folha):
        return []
    return [Aviso(FOLHA, indice, c) for c in folha.alertas_pendentes]


def linhas_do_para_revisar(projeto) -> list[tuple[str, int, list[Aviso]]]:
    """Uma linha por PAGINA com duvida, na ordem do livro: (PAGINA, indice,
    os avisos dela e os da folha dela - avisos_da_pagina). Uma folha que ainda pede um olhar
    mas nao tem pagina nenhuma conhecida (caso raro) vira a linha (FOLHA,
    indice, avisos). E a lista do painel "Para revisar" (ui/widgets/paineis);
    o numero de linhas e o quantas_com_duvida."""
    if projeto is None:
        return []
    linhas: list[tuple[str, int, list[Aviso]]] = []
    for alvo, indice in _itens_com_aviso(pendentes_do_livro(projeto), projeto):
        if alvo == PAGINA:
            avisos = avisos_da_pagina(projeto, indice)
        else:
            avisos = avisos_da_folha(projeto, indice)
        linhas.append((alvo, indice, avisos))
    return linhas


def quantas_com_duvida(projeto) -> int:
    """O NUMERO de duvidas do livro, o mesmo em todo lugar (etapa 7 da obra;
    lista unica 5.5: "Três lugares contam as dúvidas, cada um dá um número";
    D-285, `pr-contagens`: "A janela de salvar passa a contar as páginas com
    aviso pendente"): as paginas que vao para o PDF com algum aviso que ainda
    pede um olhar - o dela ou o da folha dela. O rodape, o painel "Para
    revisar" e o icone dele, a janela "Antes de processar", a janela de
    salvar, a grade "só as que precisam de atenção" e o livro aberto da tela
    inicial usam este numero. Arriscado: contar de outro jeito num deles."""
    if projeto is None:
        return 0
    return paginas_com_aviso(pendentes_do_livro(projeto), projeto)


def por_motivo(avisos: list[Aviso]) -> dict[str, list[Aviso]]:
    """Os avisos agrupados pelo codigo do motivo, os motivos com mais
    paginas primeiro (a ordem do painel "Para revisar")."""
    grupos: dict[str, list[Aviso]] = {}
    for aviso in avisos:
        grupos.setdefault(aviso.codigo, []).append(aviso)
    return dict(sorted(grupos.items(), key=lambda par: -len(par[1])))


def por_item(avisos: list[Aviso]) -> dict[tuple[str, int], list[Aviso]]:
    """Os avisos agrupados por folha ou pagina, na ordem em que vieram."""
    grupos: dict[tuple[str, int], list[Aviso]] = {}
    for aviso in avisos:
        grupos.setdefault((aviso.alvo, aviso.indice), []).append(aviso)
    return grupos


def campos_para_aceitar(projeto, avisos: list[Aviso]) -> dict[str, tuple[list[int], dict]]:
    """O que mudar para dar "está bom" nos `avisos`: para cada alvo (FOLHA,
    PAGINA) que tem algum, (indices, campos), prontos para uma acao do
    historico - campos = {"alertas_aceitos": {"<indice>": lista nova}}, o
    formato "um valor por item" de historico_acoes.aplicar. Aviso que ja
    nao esta pendente (a pagina mudou no meio) e pulado. Nao muda o projeto."""
    mudancas: dict[str, tuple[list[int], dict]] = {}
    for (alvo, indice), do_item in por_item(avisos).items():
        itens = projeto.folhas if alvo == FOLHA else projeto.paginas
        if not 0 <= indice < len(itens):
            continue
        item = itens[indice]
        pendentes = item.alertas_pendentes
        novos = [a.codigo for a in do_item if a.codigo in pendentes]
        if not novos:
            continue
        aceitos = list(getattr(item, "alertas_aceitos", None) or [])
        aceitos += [c for c in dict.fromkeys(novos) if c not in aceitos]
        indices, campos = mudancas.setdefault(alvo, ([], {"alertas_aceitos": {}}))
        indices.append(indice)
        campos["alertas_aceitos"][str(indice)] = aceitos
    return mudancas


def paginas_com_aviso(avisos: list[Aviso], projeto=None) -> int:
    """Quantas PAGINAS do livro tem algum dos `avisos`. O aviso de uma folha
    (qualidade baixa, tamanho diferente, corte) conta para as paginas que
    sairam dela: a folha 4 e a pagina 4 sao a mesma pagina do livro, uma vez
    so. Sem `projeto` (ou folha sem pagina nenhuma), a folha conta como uma.

    O defeito (verificador, 13/10/2026): a frase da janela contava folhas e
    paginas como coisas separadas - no Camoes dizia "100 páginas" num livro
    em que as paginas com aviso eram menos, porque a folha com "Qualidade
    baixa" e a pagina dela com "Endireitar" entravam como duas.

    Etapa 7 da obra: o aviso da folha conta so para as paginas dela que ainda
    nao foram conferidas (o "está certo" da pagina responde por ele ali)."""
    return len(_itens_com_aviso(avisos, projeto))


def _itens_com_aviso(avisos: list[Aviso], projeto=None) -> list[tuple[str, int]]:
    """As paginas (PAGINA, indice) com algum dos `avisos`, na ordem do livro,
    cada uma uma vez so. O aviso de uma folha conta para as paginas dela que
    vao para o PDF e ainda nao foram conferidas; sem `projeto` (ou folha sem
    pagina nenhuma no livro), a folha vira um item (FOLHA, indice)."""
    paginas_da_folha: dict[int, list] = {}
    if projeto is not None:
        for pagina in projeto.paginas:
            if not pagina.apagada:
                paginas_da_folha.setdefault(pagina.folha, []).append(pagina)
    vistas: dict[tuple[str, int], tuple[int, int]] = {}
    for aviso in avisos:
        if aviso.alvo == PAGINA:
            vistas.setdefault((PAGINA, aviso.indice), (aviso.indice, 1))
            continue
        delas = paginas_da_folha.get(aviso.indice)
        if delas:
            for pagina in delas:
                if not pagina.revisada:
                    vistas.setdefault((PAGINA, pagina.indice), (pagina.indice, 1))
        else:
            vistas.setdefault((FOLHA, aviso.indice), (aviso.indice, 0))
    # na ordem do livro (a folha sem pagina fica no lugar do numero dela)
    return sorted(vistas, key=lambda item: vistas[item])


def frase_de_quantos(avisos: list[Aviso], projeto=None) -> str:
    """"Ainda tem 3 páginas que eu não tive certeza (4 avisos na lista)." -
    para o alto da janela "Antes de processar". As PAGINAS sao contadas por
    paginas_com_aviso (folha e pagina da mesma folha, uma vez so); os avisos
    sao as linhas da lista (um por motivo). Os dois numeros aparecem com o
    nome de cada um, para nao parecerem a mesma conta."""
    paginas = paginas_com_aviso(avisos, projeto)
    frase = ("Ainda tem 1 página que eu não tive certeza" if paginas == 1
             else f"Ainda tem {paginas} páginas que eu não tive certeza")
    if len(avisos) != paginas:
        frase += f" ({len(avisos)} avisos na lista)"
    return frase + "."
