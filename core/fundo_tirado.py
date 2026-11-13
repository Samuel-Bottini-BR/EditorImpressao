"""O "fundo tirado" da pagina: a regra UNICA de quando o fundo fica tirado.

POR QUE EXISTE (conserto de 13/11/2026, ramo fundo-2026-11-13)

D-646 (Samuel, 07/11/2026): "É só criar uma opção para desfazer o tirar fundo, e
só vai desfazer o tirar fundo quando apertar ela. E via de regra, nenhum filtro
deve fazer o fundo voltar." D-699 (13/11/2026, "Ok"): o botão "Desfazer o tirar o
fundo" fica logo abaixo do "Tirar o fundo", no menu Filtro e no painel "Filtro da
página", com o "Aplicar em" de sempre; depois do "Tirar o fundo", o Preto e
branco, o Melhorar, o Mágico pro, o Original e o Automático trabalham em cima da
página já sem o fundo. D-134 (29/09): "eu quero poder escolher tirar o fundo sem
colocar nenhum filtro" (o cartão "Tirar o fundo" continua sendo isso). D-667 e
CLAUDE.md §11.12: a regra vale em todos os caminhos, escrita num lugar só.

A CAUSA DO DEFEITO: o fundo tirado era guardado SÓ no filtro da página
(ConfigPagina.filtro == "tirar_fundo"). Qualquer troca de filtro (o "Original"
que o Automático põe, o cartão, a tecla, o menu, o "Aplicar em") apagava junto
a única marca de que o fundo tinha sido tirado, e o pipeline voltava a desenhar
a folha com o papel velho.

O CONSERTO: o fundo tirado é um dado da página, SEPARADO do filtro
(ConfigPagina.fundo_tirado), lido e gravado só pelas funções daqui:

    esta_sem_o_fundo(projeto, pagina)   a página está sem o fundo? (a prévia, as
                                        figurinhas, o PDF: core/pipeline.usa_tirar_fundo)
    depois_da_troca(projeto, pagina, f) o fundo tirado da página DEPOIS de o filtro
                                        virar `f` - A REGRA: nenhum filtro traz o
                                        fundo de volta; "Tirar o fundo" o tira
    com_o_fundo_que_fica(...)           o campo "fundo_tirado" que vai junto em toda
                                        ação do desfazer que troca filtro de página
                                        (historico_acoes.montar_acao: painel,
                                        figurinhas, teclas, menu, tela cheia,
                                        "Aplicar em", "Sim" da pergunta do fundo)
    campos_para_desfazer(...)           o "Desfazer o tirar o fundo" (o único que traz
                                        o fundo de volta; menu e painel chamam a
                                        mesma função da tela, que usa esta)
    campos_do_aplicar_em(pagina)        o que o "Aplicar em" do painel leva junto
    filtro_por_cima(projeto, pagina)    o filtro passa por cima da página sem o fundo?
    so_o_fundo_tirado(pagina)           a página sai só sem o fundo, sem filtro
    migrar_projeto_antigo(...)          projeto gravado antes deste campo

O Automático grava a troca de filtro pelo seu gravador (core/automatico._Gravador),
que chama depois_da_troca na mesma hora; o desfazer/refazer devolve o campo porque
ele vai na mesma ação.

OS TRÊS VALORES DE ConfigPagina.fundo_tirado
    True   o fundo foi tirado (pelo "Tirar o fundo", pelo "Sim" da pergunta, pelo
           Automático com "Tirar o fundo", ou ficou tirado numa troca de filtro);
    False  a pessoa apertou "Desfazer o tirar o fundo" nesta página;
    None   nunca foi tirado nem desfeito (a página nova, o de fábrica).
A diferença entre False e None só serve ao "Aplicar em": ele leva o True (a página
sem o fundo) e o False (o "Desfazer" desta página) às outras, e o None não leva
nada (as outras ficam como estão). Assim só o botão "Desfazer o tirar o fundo"
traz o fundo de volta, também nas outras páginas.

A página no filtro "Tirar o fundo" sem o campo (montada pela análise com o filtro
do livro, ou de projeto antigo) também está sem o fundo: esta_sem_o_fundo olha o
filtro que vale (core/etapas.filtro_que_vale), como sempre olhou.

Seguro mudar: os textos. Arriscado: fazer outro lugar do programa ler ou gravar
ConfigPagina.fundo_tirado sem passar por aqui (o defeito volta naquele lugar);
deixar uma troca de filtro sem passar por depois_da_troca.
"""

from __future__ import annotations

from typing import Any

from core import etapas
from core.filtros import ORIGINAL, TIRAR_FUNDO

CAMPO = "fundo_tirado"


def valor(pagina) -> bool | None:
    """O ConfigPagina.fundo_tirado (None na página de antes deste campo)."""
    return getattr(pagina, CAMPO, None)


def esta_sem_o_fundo(projeto, pagina) -> bool:
    """A página está sem o fundo, pelo que a pessoa escolheu? Sim com o fundo
    tirado (True), ou com o filtro "Tirar o fundo" valendo nela (o de sempre:
    core/etapas.filtro_que_vale, com "Limpar a folha" ou escolhido à mão). Se o
    PDF tem camadas e a página não está em branco, quem decide é
    core/pipeline.usa_tirar_fundo (que chama esta)."""
    if valor(pagina) is True:
        return True
    return etapas.filtro_que_vale(projeto, pagina) == TIRAR_FUNDO


def depois_da_troca(projeto, pagina, filtro_novo: str) -> bool | None:
    """A REGRA (D-646, D-699): o fundo tirado da página depois de o filtro dela
    virar `filtro_novo`. "Tirar o fundo" tira (True). Qualquer outro filtro,
    Original inclusive, deixa a página como estava: se ela estava sem o fundo,
    continua sem ele (True); se não, fica o que era (None ou False). Chamar
    ANTES de trocar o filtro."""
    if filtro_novo == TIRAR_FUNDO or esta_sem_o_fundo(projeto, pagina):
        return True
    return valor(pagina)


def _filtro_de(campos_filtro: Any, indice: int) -> str | None:
    """O filtro novo da página `indice` numa ação (valor simples ou {indice: valor},
    como historico_acoes.aplicar aceita); None se a ação não muda o dela."""
    if isinstance(campos_filtro, dict):
        return campos_filtro.get(str(indice))
    return campos_filtro


def com_o_fundo_que_fica(projeto, indices: list[int], campos: dict) -> dict:
    """Os `campos` de uma ação de PÁGINA, com o "fundo_tirado" que a regra
    (depois_da_troca) manda, quando a ação troca o filtro. Chamada por
    historico_acoes.montar_acao, por onde passam todas as trocas de filtro da
    tela (cartão, tecla 1 a 4, menu Filtro, tela cheia dos filtros, tela grande,
    "Aplicar em", "Sim" da pergunta do fundo, "desfazer nesta página"); o
    desfazer e o refazer devolvem o campo junto. Ação que já diz o fundo (o
    "Desfazer o tirar o fundo", o "Aplicar em" de uma página com o campo) passa
    como está. Sem mudança no fundo de nenhuma página: os mesmos `campos`."""
    if "filtro" not in campos or CAMPO in campos:
        return campos
    novos: dict[str, Any] = {}
    muda = False
    for indice in indices:
        if not 0 <= indice < len(projeto.paginas):
            continue
        filtro = _filtro_de(campos["filtro"], indice)
        if filtro is None:
            continue
        pagina = projeto.paginas[indice]
        depois = depois_da_troca(projeto, pagina, filtro)
        novos[str(indice)] = depois
        muda = muda or depois != valor(pagina)
    if not muda:
        return campos
    return {**campos, CAMPO: novos}


def pode_desfazer(projeto, pagina) -> bool:
    """O "Desfazer o tirar o fundo" faz alguma coisa nesta página? (o botão do
    painel e o item do menu ficam acesos só assim)."""
    return bool(getattr(projeto, "tem_camadas", False)) and esta_sem_o_fundo(projeto, pagina)


def campos_para_desfazer(projeto, indices: list[int]) -> dict:
    """O "Desfazer o tirar o fundo" (D-646/D-699) nas páginas `indices`: o fundo
    volta (False = desfeito à mão) e a página que estava no filtro "Tirar o
    fundo" fica no Original (sem filtro, como ela estava antes de tirar). As
    outras ficam com o filtro delas. Vazio se nenhuma está sem o fundo. O menu
    Filtro e o painel chamam a mesma função da tela
    (ui/tela_conferir.TelaConferir.desfazer_o_tirar_o_fundo), que usa esta."""
    sem = [i for i in indices if 0 <= i < len(projeto.paginas)
           and esta_sem_o_fundo(projeto, projeto.paginas[i])]
    if not sem:
        return {}
    campos: dict[str, Any] = {CAMPO: {str(i): False for i in sem}}
    if any(projeto.paginas[i].filtro == TIRAR_FUNDO for i in sem):
        campos["filtro"] = {
            str(i): ORIGINAL if projeto.paginas[i].filtro == TIRAR_FUNDO else projeto.paginas[i].filtro
            for i in sem}
    return campos


def campos_do_aplicar_em(pagina) -> dict:
    """O que o "Aplicar em" (todas / daqui em diante) do painel Filtro leva desta
    página, além do filtro: o fundo tirado (True) ou desfeito (False). Página
    que nunca teve o fundo tirado nem desfeito (None): nada, e as outras ficam
    como estão (nenhum filtro traz o fundo de volta)."""
    atual = valor(pagina)
    return {} if atual is None else {CAMPO: atual}


def filtro_por_cima(projeto, pagina) -> bool:
    """Na página sem o fundo, passa um filtro por cima (Preto e branco, Melhorar,
    Mágico pro: D-699)? Não no Original nem no "Tirar o fundo": aí a página sai
    só sem o fundo, pelo caminho de sempre do "Tirar o fundo" (com o "só neste
    pedaço" da D-172)."""
    return etapas.filtro_que_vale(projeto, pagina) not in (ORIGINAL, TIRAR_FUNDO)


def so_o_fundo_tirado(pagina) -> bool:
    """A página sai só sem o fundo, sem filtro por cima: no filtro "Tirar o
    fundo", ou no Original com o fundo tirado (o que um projeto antigo em
    "Tirar o fundo" vira ao abrir). As contas que o "Tirar o fundo" pula
    (procurar gravura e letra, o filtro) pulam igual nos dois."""
    return pagina.filtro == TIRAR_FUNDO or (valor(pagina) is True and pagina.filtro == ORIGINAL)


def migrar_projeto_antigo(projeto, paginas_sem_o_campo) -> None:
    """Projeto gravado antes deste campo (a página não tem a chave
    "fundo_tirado"): a página que estava em "Tirar o fundo", com o filtro
    valendo, abre com o fundo tirado e o filtro Original (palavras da pergunta
    aprovada na D-699). O PDF sai igual (so_o_fundo_tirado: o mesmo caminho).
    Página em "Tirar o fundo" que não valia (sem "Limpar a folha"): fica como
    estava. `paginas_sem_o_campo`: as ConfigPagina que vieram sem a chave."""
    for pagina in paginas_sem_o_campo:
        if pagina.filtro == TIRAR_FUNDO and etapas.filtro_que_vale(projeto, pagina) == TIRAR_FUNDO:
            pagina.fundo_tirado = True
            pagina.filtro = ORIGINAL
