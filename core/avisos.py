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


def pendentes_do_livro(projeto) -> list[Aviso]:
    """Todos os avisos que ainda pedem um olhar, na ordem do livro: para cada
    folha, os dela (o corte, o angulo, o tamanho) e depois os das paginas que
    sairam dela. Folha e pagina apagadas ficam de fora (nao vao para o PDF)."""
    paginas_da_folha: dict[int, list] = {}
    for pagina in projeto.paginas:
        paginas_da_folha.setdefault(pagina.folha, []).append(pagina)
    avisos: list[Aviso] = []
    vistas: set[int] = set()
    for folha in projeto.folhas:
        if not getattr(folha, "apagada", False):
            avisos.extend(Aviso(FOLHA, folha.indice, c) for c in folha.alertas_pendentes)
        for pagina in paginas_da_folha.get(folha.indice, []):
            vistas.add(pagina.indice)
            if not pagina.apagada:
                avisos.extend(Aviso(PAGINA, pagina.indice, c) for c in pagina.alertas_pendentes)
    for pagina in projeto.paginas:            # pagina sem folha conhecida (nunca visto)
        if pagina.indice not in vistas and not pagina.apagada:
            avisos.extend(Aviso(PAGINA, pagina.indice, c) for c in pagina.alertas_pendentes)
    return avisos


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
    baixa" e a pagina dela com "Endireitar" entravam como duas."""
    paginas_da_folha: dict[int, list[int]] = {}
    if projeto is not None:
        for pagina in projeto.paginas:
            if not pagina.apagada:
                paginas_da_folha.setdefault(pagina.folha, []).append(pagina.indice)
    vistas: set = set()
    for aviso in avisos:
        if aviso.alvo == PAGINA:
            vistas.add((PAGINA, aviso.indice))
            continue
        delas = paginas_da_folha.get(aviso.indice)
        if delas:
            vistas.update((PAGINA, indice) for indice in delas)
        else:
            vistas.add((FOLHA, aviso.indice))
    return len(vistas)


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
