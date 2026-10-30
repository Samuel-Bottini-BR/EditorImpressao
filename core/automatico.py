"""O Automatico: rodar as etapas no livro todo, em paginas escolhidas ou numa pagina.

POR QUE EXISTE (obra de 26/10/2026, etapa 3). Decisoes do Samuel:
  D-002 (25/09): "Trabalho automático = painel 'Automático' que abre e fecha
      (substitui a tela 7). [...] Funciona antes/ao abrir o livro e depois, na
      área de trabalho (ex.: abrir o PDF sem mexer e rodar as etapas depois)."
      Kaique, 22/09: "Essa pagina não era mais para aparecer – nós tínhamos que
      abrir direto na área de trabalho". 26/10: "eu quero poder sim fazer
      automatico para todo livro, mas também quero pode fazer uma a uma."
  D-003 (28/09) + D-016 (escolha da gerente): a ordem das etapas muda
      arrastando; muda a ordem em que elas RODAM (o que o programa procura e
      decide primeiro); a montagem da pagina segue sempre a ordem obrigatoria
      (core/ordem_do_preparo: endireita, depois corta uma vez so).
  D-004 (28/09): "Automático em livro já mexido à mão: o programa pergunta se
      quer pular as páginas mexidas." (paginas_mexidas, Pedido.pular_mexidas).
  Defeito de 29/09 (teste do Kaique de 26/10, tarefas 7 e 8): antes, mudar uma
      opcao num livro ja conferido era jogado fora (o projeto salvo voltava por
      cima da analise nova). Aqui o Automatico grava DIRETO no projeto aberto:
      o que ele roda vale, e o resto do trabalho fica como estava.

O QUE FAZ
  Antes, a tela "O que fazer" ligava as caixinhas do livro (Projeto.dividir_
  folhas, .endireitar, .cortar_bordas, .limpar...) e o "Conferir" analisava o
  livro inteiro de novo. Agora o livro abre sem nada ligado (a pagina como
  veio, "sempre abre em Original, sem mexer", 29/09) e o Automatico roda quando
  a pessoa pede:
    - no LIVRO TODO: liga a caixinha da etapa no livro (como o "Conferir"
      fazia), com as opcoes dela;
    - em PAGINAS ESCOLHIDAS (ou numa so): liga a etapa so nelas
      (ConfigPagina.automatico; core/etapas le com a pagina). Dividir mexe nas
      folhas dessas paginas. As etapas da saida (margens iguais, cadernos) e as
      opcoes das gravuras valem sempre no livro todo (sao do livro, nao da
      pagina).
  O que precisa de imagem (achar onde dividir, os avisos de torta, de corte,
  de cor e de pagina em branco) e medido por `medir`, que so LE o PDF e nao
  toca no projeto (roda num fio de fundo: ui/tarefas.TarefaAutomatico). O que
  muda o projeto e `aplicar`, no fio da janela, numa acao so do Historico
  (o Ctrl+Z desfaz o Automatico inteiro; fica no acoes.jsonl).

  O corte e o angulo continuam sendo calculados como sempre, quando a pagina e
  desenhada (a previa e o PDF, core/pipeline): ligar a etapa e o que manda o
  pipeline fazer a conta. Por isso rodar so "Endireitar" numa pagina muda so
  ela, e a ordem arrastada nao muda a pagina pronta (D-016).

O QUE E "MEXIDA A MAO" AQUI (pergunta D-004): a pagina (ou a folha, no
  dividir) tem a marca ou o valor a mao da etapa que vai rodar
  (core/etapas.mexida_a_mao). Pular = a pagina fica como esta naquela etapa.
  Nao pular = o valor a mao daquela etapa sai (o corte a mao, o angulo a mao,
  o filtro escolhido a mao, a divisao a mao) e o automatico vale nela.

Nunca importa ui/. Seguro mudar: NOMES, EXPLICACOES, GRUPOS (textos).
Arriscado: CAMPO_DO_LIVRO e OPCOES (sao os campos de modelos.Projeto que o
Automatico escreve; tirar um faz a opcao sumir da janela e da receita); medir
tocar no projeto (corre num fio de fundo).
"""

from __future__ import annotations

import copy
import dataclasses
from dataclasses import dataclass, field
from typing import Any, Callable

from core import etapas as E

# --- as etapas do Automatico (codigos internos, nunca texto de tela) ---------

DIVIDIR = "dividir"
ENDIREITAR = "endireitar"
CORTAR = "cortar"
LIMPAR = "limpar"
GRAVURAS = "gravuras"
MARGENS = "margens"
CADERNOS = "cadernos"

ETAPAS = (DIVIDIR, ENDIREITAR, CORTAR, LIMPAR, GRAVURAS, MARGENS, CADERNOS)
ORDEM_DE_FABRICA = ETAPAS

# Os nomes da tela (os da tela "O que fazer" e do desenho aprovado, rodada 12b)
NOMES = {
    DIVIDIR: "Dividir folhas ao meio",
    ENDIREITAR: "Endireitar folhas tortas",
    CORTAR: "Cortar as bordas",
    LIMPAR: "Limpar a folha",
    GRAVURAS: "Gravuras e fotos",
    MARGENS: "Margens iguais",
    CADERNOS: "Montar cadernos",
}
EXPLICACOES = {
    DIVIDIR: "quando a folha tem 2 páginas do livro",
    ENDIREITAR: "corrige páginas inclinadas",
    CORTAR: "tira a borda preta e a sombra do scanner",
    LIMPAR: "tira o amarelado",
    GRAVURAS: "separa desenho, foto e moldura do texto",
    MARGENS: "todas as páginas do tamanho da maior, com a margem em volta",
    CADERNOS: "para imprimir, dobrar ao meio e costurar (no tamanho do scan)",
}
# Os grupos do desenho (rascunho do layout, "O painel Automático vai crescer":
# "Página · Limpeza · Letra e gravura · Saída")
GRUPOS = (
    ("Página", (DIVIDIR, ENDIREITAR, CORTAR)),
    ("Limpeza", (LIMPAR,)),
    ("Gravuras e fotos", (GRAVURAS,)),
    ("Saída", (MARGENS, CADERNOS)),
)
# Etapas que sao do livro, nao da pagina: rodam sempre no livro todo
DO_LIVRO_TODO = (GRAVURAS, MARGENS, CADERNOS)

# A caixinha do livro de cada etapa (o "automatico ligado no livro todo").
# GRAVURAS nao tem caixinha: ligada = detectar_regioes e a forma nao
# "desligada" (ver ligada_no_livro).
CAMPO_DO_LIVRO = {
    DIVIDIR: "dividir_folhas",
    ENDIREITAR: "endireitar",
    CORTAR: "cortar_bordas",
    LIMPAR: "limpar",
    MARGENS: "margens_iguais",
    CADERNOS: "montar_cadernos",
}

# As opcoes de cada etapa (campos de modelos.Projeto): tudo o que morava na tela
# "O que fazer" (ui/tela_opcoes._mudou), agora dentro da etapa a que pertence.
OPCOES = {
    DIVIDIR: ("dividir_como",),
    ENDIREITAR: ("endireitar_como", "retangulo_do_corte"),
    CORTAR: ("cortar_sobra", "cortar_pelo_conteudo", "borda_preta", "borda_preta_ate",
             "borda_preta_fazer"),
    LIMPAR: ("filtro_padrao", "pb_decoracao_em_preto_e_branco", "misto_so_as_letras",
             "misto_fora_do_texto", "misto_papel_da_gravura", "misto_letras_na_moldura",
             "reforcar_texto_falhado", "limpar_pontinhos"),
    GRAVURAS: ("gravura_forma", "gravura_sensibilidade", "gravura_mais_sensivel",
               "gravura_normalizar"),
    MARGENS: ("margens_mm", "margens_alinhamento"),
    CADERNOS: ("paginas_por_caderno",),
}

# A etapa de core/etapas que cada uma liga numa pagina (as outras sao do livro
# ou da folha)
NA_PAGINA = {ENDIREITAR: E.ENDIREITAR, CORTAR: E.CORTAR, LIMPAR: E.FILTRO}
# A marca "mexida a mao" que conta para a pergunta D-004
MEXIDA = {DIVIDIR: E.DIVIDIR, ENDIREITAR: E.ENDIREITAR, CORTAR: E.CORTAR, LIMPAR: E.FILTRO}


def todas_as_opcoes() -> tuple[str, ...]:
    """Os campos do Projeto que o Automatico mostra e grava: as caixinhas das
    etapas e as opcoes de cada uma. (A prova "nenhuma opcao da tela 'O que
    fazer' se perdeu" confere esta lista: tests/test_decisoes_automatico.py.)"""
    campos = list(CAMPO_DO_LIVRO.values()) + ["detectar_regioes"]
    for etapa in ETAPAS:
        campos.extend(OPCOES[etapa])
    return tuple(dict.fromkeys(campos))


# --- o estado de cada etapa no livro -----------------------------------------

def ordem(projeto) -> list[str]:
    """A ordem em que as etapas rodam neste livro (D-003): a gravada
    (Projeto.ordem_do_automatico), sem codigo estranho, com as que faltarem no
    fim, na ordem de fabrica."""
    gravada = [e for e in (getattr(projeto, "ordem_do_automatico", None) or []) if e in ETAPAS]
    gravada = list(dict.fromkeys(gravada))
    return gravada + [e for e in ORDEM_DE_FABRICA if e not in gravada]


def ligada_no_livro(projeto, etapa: str) -> bool:
    """A etapa esta ligada no livro todo?"""
    if etapa == GRAVURAS:
        return bool(getattr(projeto, "detectar_regioes", True)
                    and getattr(projeto, "gravura_forma", "livre") != "desligada"
                    and getattr(projeto, "limpar", False))
    return bool(getattr(projeto, CAMPO_DO_LIVRO[etapa], False))


def paginas_com_a_etapa(projeto, etapa: str) -> list[int]:
    """As paginas em que a etapa esta ligada SO nelas (ConfigPagina.automatico)."""
    codigo = NA_PAGINA.get(etapa)
    if codigo is None:
        return []
    return [p.indice for p in getattr(projeto, "paginas", [])
            if E.no_automatico_da_pagina(p, codigo)]


def situacao(projeto, etapa: str) -> str:
    """Em portugues, onde a etapa esta ligada: "ligada no livro todo",
    "ligada em 3 páginas", "desligada"."""
    if ligada_no_livro(projeto, etapa):
        return "ligada no livro todo"
    algumas = paginas_com_a_etapa(projeto, etapa)
    if algumas:
        return f"ligada em {len(algumas)} página" + ("" if len(algumas) == 1 else "s")
    return "desligada"


def opcoes_do_livro(projeto) -> dict[str, Any]:
    """As opcoes de agora do livro (copias), para a janela comecar delas."""
    return {campo: copy.deepcopy(getattr(projeto, campo)) for campo in todas_as_opcoes()
            if hasattr(projeto, campo)}


def etapas_ligadas(projeto) -> list[str]:
    """As etapas ligadas no livro todo ou em alguma pagina, na ordem de rodar."""
    return [e for e in ordem(projeto)
            if ligada_no_livro(projeto, e) or paginas_com_a_etapa(projeto, e)]


# --- o pedido ----------------------------------------------------------------

@dataclass
class Pedido:
    """O que a pessoa pediu ao Automatico.

    etapas: as marcadas (codigos de ETAPAS), na ordem em que rodam.
    opcoes: os campos do Projeto escolhidos na janela (todas_as_opcoes; os que
        faltarem ficam como estao no livro).
    paginas: os indices das paginas (projeto.paginas) em que rodar; None = o
        livro todo.
    pular_mexidas: a resposta da pergunta D-004 (True = as paginas mexidas a
        mao ficam como estao nas etapas pedidas).
    receita: o nome da receita que estava escolhida ("" = nenhuma), para o
        "Receita usada".
    desligar: True = tirar o automatico das etapas pedidas (D-068: "Toda
        função automática tem botão de ligar e desligar.").
    ordem: a ordem das etapas arrastada na janela (vai para o livro).
    """

    etapas: list[str]
    opcoes: dict[str, Any] = field(default_factory=dict)
    paginas: list[int] | None = None
    pular_mexidas: bool = True
    receita: str = ""
    desligar: bool = False
    ordem: list[str] | None = None

    @property
    def no_livro_todo(self) -> bool:
        return self.paginas is None


def _paginas_do_pedido(projeto, pedido: Pedido) -> list:
    if pedido.paginas is None:
        return list(projeto.paginas)
    validos = set(i for i in pedido.paginas if 0 <= i < len(projeto.paginas))
    return [p for p in projeto.paginas if p.indice in validos]


def folhas_do_pedido(projeto, pedido: Pedido) -> list[int]:
    """As folhas das paginas do pedido (para dividir e para medir)."""
    if pedido.paginas is None:
        return [f.indice for f in projeto.folhas]
    return sorted({p.folha for p in _paginas_do_pedido(projeto, pedido)
                   if 0 <= p.folha < len(projeto.folhas)})


def paginas_mexidas(projeto, pedido: Pedido) -> list[int]:
    """As paginas do pedido mexidas a mao nas etapas pedidas (D-004: e a
    contagem da pergunta "pular as N paginas mexidas?"). Folha mexida a mao no
    dividir conta com as paginas dela."""
    if pedido.desligar:
        return []
    marcas = [MEXIDA[e] for e in pedido.etapas if e in MEXIDA and e != DIVIDIR]
    achadas = set()
    for pagina in _paginas_do_pedido(projeto, pedido):
        if any(E.mexida_a_mao(projeto, pagina, m) for m in marcas):
            achadas.add(pagina.indice)
        elif LIMPAR in pedido.etapas and _filtro_trocado_na_pagina(projeto, pagina):
            achadas.add(pagina.indice)
    if DIVIDIR in pedido.etapas:
        folhas = set(folhas_do_pedido(projeto, pedido))
        for folha in projeto.folhas:
            if folha.indice in folhas and E.mexida_a_mao(projeto, folha, E.DIVIDIR):
                achadas.update(p.indice for p in projeto.paginas if p.folha == folha.indice)
    return sorted(achadas)


def _filtro_trocado_na_pagina(projeto, pagina) -> bool:
    """A pagina tem um filtro diferente do filtro do livro, com o "Limpar a
    folha" valendo nela, e nao por o Automatico ter rodado so nela? Conta
    como "mexida a mao" para a pergunta D-004 (e para o pular): no projeto
    gravado antes da etapa 1 o filtro escolhido numa pagina nao tem a marca
    (core/etapas: o filtro so conta pela marca), e rodar "Limpar a folha" no
    livro todo o trocaria pelo do livro - o trabalho se perderia calado.
    Escolha da gerente (D-014), etapa 3. So para a pergunta: o PDF continua
    seguindo core/etapas.filtro_que_vale."""
    return bool(E.limpa_sozinho(projeto, pagina)
                and not E.no_automatico_da_pagina(pagina, E.FILTRO)
                and getattr(pagina, "filtro", None) != getattr(projeto, "filtro_padrao", None))


def resumo(pedido: Pedido, total_paginas: int, filtro_nome: str = "") -> str:
    """A frase de baixo da janela: "Vou dividir, endireitar e limpar em Preto e
    branco, no livro todo (200 páginas)." (como no desenho aprovado)."""
    if not pedido.etapas:
        return "Nenhuma etapa marcada: nada vai mudar."
    # "limpar em Original" nao diz nada (o Original nao mexe na pagina): diz isso
    limpar = ("deixar a página em Original (sem filtro)" if filtro_nome.strip().lower() == "original"
              else "limpar" + (f" em {filtro_nome}" if filtro_nome else ""))
    verbos = {DIVIDIR: "dividir as folhas", ENDIREITAR: "endireitar", CORTAR: "cortar as bordas",
              LIMPAR: limpar,
              GRAVURAS: "achar gravuras e fotos", MARGENS: "deixar as margens iguais",
              CADERNOS: "montar os cadernos"}
    partes = [verbos[e] for e in pedido.etapas]
    lista = partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " e " + partes[-1]
    if pedido.paginas is None:
        onde = f"no livro todo ({total_paginas} páginas)"
    elif len(pedido.paginas) == 1:
        onde = f"só na página {pedido.paginas[0] + 1}"
    else:
        onde = f"em {len(pedido.paginas)} páginas escolhidas"
    if pedido.desligar:
        return f"Vou desligar: {lista}, {onde}."
    return f"Vou {lista}, {onde}."


# --- a passada leve ao abrir (D-284; "sempre abre em Original, sem mexer") ----

def livro_leve(projeto, tamanhos: list[tuple[float, float]]) -> None:
    """Prepara um livro recem-aberto SEM medir nada: uma folha por pagina do
    PDF, uma pagina por folha (inteira, no Original), e nenhuma etapa do
    automatico ligada (a pagina como veio). `tamanhos` = (largura, altura) em
    pontos de cada pagina do PDF (core.pdf_io.info_paginas: milissegundos).
    Marca o livro como "ainda nao passou pelo automatico" (o aviso D-005).
    Arriscado: ligar alguma caixinha aqui (a pagina mudaria sem a pessoa
    pedir, contra "sempre abre em Original, sem mexer")."""
    from core.filtros import ORIGINAL
    from modelos import METADE_INTEIRA, ConfigFolha, ConfigPagina

    for campo in CAMPO_DO_LIVRO.values():
        setattr(projeto, campo, False)
    projeto.passou_pelo_automatico = False
    folhas, paginas = [], []
    for indice, (largura, altura) in enumerate(tamanhos):
        folhas.append(ConfigFolha(indice=indice, dividir=False, posicao_corte=0.5,
                                  e_paisagem=bool(largura > altura * 1.2)))
        paginas.append(ConfigPagina(indice=indice, folha=indice, metade=METADE_INTEIRA,
                                    filtro=ORIGINAL))
    projeto.folhas = folhas
    projeto.paginas = paginas


# --- medir (le o PDF, nao toca no projeto: pode rodar num fio de fundo) -------

@dataclass
class _FolhaParaMedir:
    indice: int
    rotacao: int
    dividir: bool              # como esta agora
    posicao_corte: float
    redividir: bool            # o pedido vai achar onde dividir esta folha?
    filtros: dict              # metade -> filtro que a pagina vai ter (para o aviso de cor)
    endireitar_como: dict      # metade -> conta da pagina (None = a do livro)


@dataclass
class Fotografia:
    """O que `medir` precisa do projeto, copiado no fio da janela (assim o
    fio de fundo nunca le o projeto que a pessoa esta mexendo)."""

    caminho: str
    folhas: list[_FolhaParaMedir]
    etapas: list[str]
    dividir_como: str
    cortar_sobra: bool
    vai_endireitar: bool
    vai_cortar: bool
    vai_dividir: bool
    livro: Any                 # copia rasa do projeto, sem folhas/paginas (as contas de endireitar)


@dataclass
class MedidaDaFolha:
    """O que foi medido numa folha: a divisao achada (se pedida), a sobra, o
    angulo da analise, os avisos da folha e, de cada pagina que ela vai ter
    (na ordem esquerda/direita ou inteira), os avisos e a cor."""

    indice: int
    dividir: bool
    posicao_corte: float
    confianca_corte: float
    e_paisagem: bool
    sobra: Any
    angulo_detectado: float
    confianca_angulo: float
    alertas: list[str]
    partes: list[tuple[str, list[str], bool, bool, float | None]]   # metade, alertas, tem_cor, discorda, angulo
    # Etapa 9b-2 (D-559): a tampa do scanner achada nesta folha, como vai para
    # ConfigFolha.tampa_do_scanner ([rotacao, x0, y0, x1, y1], ou [rotacao]
    # quando procurada e nada achado); None = nao procurada (quem mede sem ela)
    tampa: list | None = None


def fotografar(projeto, pedido: Pedido) -> Fotografia:
    """Copia, no fio da janela, o que `medir` precisa (ver Fotografia)."""
    opcoes = {**opcoes_do_livro(projeto), **(pedido.opcoes or {})}
    rodando = set() if pedido.desligar else set(pedido.etapas)
    filtro_novo = opcoes.get("filtro_padrao", getattr(projeto, "filtro_padrao", "original"))
    pular = set(paginas_mexidas(projeto, pedido)) if pedido.pular_mexidas else set()
    folhas = []
    paginas_por_folha: dict[int, list] = {}
    for pagina in projeto.paginas:
        paginas_por_folha.setdefault(pagina.folha, []).append(pagina)
    for indice in folhas_do_pedido(projeto, pedido):
        folha = projeto.folhas[indice]
        pags = paginas_por_folha.get(indice, [])
        redividir = DIVIDIR in rodando and not any(p.indice in pular for p in pags)
        filtros, contas = {}, {}
        for p in pags:
            vai_limpar = LIMPAR in rodando and p.indice not in pular
            filtros[p.metade] = filtro_novo if vai_limpar else E.filtro_que_vale(projeto, p)
            contas[p.metade] = getattr(p, "endireitar_como", None)
        folhas.append(_FolhaParaMedir(indice, int(folha.rotacao) % 360, bool(folha.dividir),
                                      float(folha.posicao_corte), redividir, filtros, contas))
    livro = copy.copy(projeto)
    livro.folhas, livro.paginas = [], []
    for campo, valor in opcoes.items():
        if hasattr(livro, campo):
            setattr(livro, campo, copy.deepcopy(valor))
    vai_endireitar = ENDIREITAR in rodando or bool(projeto.endireitar)
    livro.endireitar = vai_endireitar
    return Fotografia(
        caminho=projeto.caminho_entrada, folhas=folhas, etapas=list(pedido.etapas),
        dividir_como=opcoes.get("dividir_como", projeto.dividir_como),
        cortar_sobra=bool(opcoes.get("cortar_sobra", False)) and CORTAR in rodando,
        vai_endireitar=vai_endireitar,
        vai_cortar=CORTAR in rodando or bool(projeto.cortar_bordas),
        vai_dividir=DIVIDIR in rodando or bool(projeto.dividir_folhas),
        livro=livro)


def precisa_medir(pedido: Pedido) -> bool:
    """O pedido precisa olhar as paginas (fio de fundo)? Desligar, e as etapas
    so do livro, nao."""
    return not pedido.desligar and any(e in pedido.etapas for e in (DIVIDIR, ENDIREITAR, CORTAR, LIMPAR))


def medir(foto: Fotografia, progresso: Callable | None = None,
          cancelado: Callable | None = None) -> dict[int, MedidaDaFolha]:
    """Mede as folhas da fotografia a 150 DPI (como a analise de sempre,
    core/pipeline.analisar_projeto): onde dividir (se pedido), a sobra, o
    angulo, o corte (so para o aviso) e, por pagina, os avisos de cor e de
    pagina em branco e as duas contas do endireitar. Nunca toca no projeto.
    `cancelado()` True = para (levanta core.pipeline.Cancelou). Uma folha por
    vez na memoria."""
    from core import analise, dividir_a_mao
    from core import pipeline as P
    from core.borda_preta import pintar_fora
    from core.dividir import Lombada, dividir_imagem
    from core.endireitar import Inclinacao, detectar_angulo, girar_90
    from core.pdf_io import abrir_pdf, dpi_real_da_pagina, info_paginas, pagina_para_array
    from core.recortar import Recorte, detectar_bordas
    from modelos import METADE_DIREITA, METADE_ESQUERDA, METADE_INTEIRA, ConfigPagina

    medidas: dict[int, MedidaDaFolha] = {}
    doc = abrir_pdf(foto.caminho)
    try:
        infos = info_paginas(doc)
        fora = analise.tamanhos_fora_do_padrao([(i.largura_pt, i.altura_pt) for i in infos])
        total = len(foto.folhas)
        es = P.endireitar_scantailor
        for n, f in enumerate(foto.folhas):
            if cancelado is not None and cancelado():
                raise P.Cancelou()
            if progresso is not None:
                progresso(n, total, f"Olhando a folha {n + 1} de {total}")
            img = pagina_para_array(doc, f.indice, dpi=P.DPI_ANALISE)
            if f.rotacao:
                img = girar_90(img, f.rotacao)
            # Etapa 9b-2 (D-559, 27/10/2026, Central `ac-tampa`: "sumir em todo
            # o livro, e o Kaique escolhe por livro cortar ou pintar de branco";
            # D-097: "É para sumir totalmente."): a tampa do scanner e procurada
            # em TODA folha que o Automatico olha (a mesma regra do dividir a
            # mao, core/dividir_a_mao.achar_a_tampa, que nao pega moldura
            # impressa: varredura das 2.903 folhas do acervo na etapa 4), e o
            # resto da medida e feito na folha ja sem ela (como o "dividir
            # esta": a lombada, o angulo e o corte nao confundem a faixa preta
            # com o livro). Sem tampa (quase todo livro) a imagem e a mesma.
            tampa = dividir_a_mao.achar_a_tampa(img, f.rotacao, P.DPI_ANALISE) or [f.rotacao]
            if len(tampa) == 5:
                img = pintar_fora(img, tuple(tampa[1:]))
            if f.redividir:
                lombada = P.achar_divisao(img, foto.dividir_como, P.DPI_ANALISE)
                dividir = bool(lombada.e_paisagem)
                posicao, confianca, paisagem = lombada.posicao, lombada.confianca, lombada.e_paisagem
            else:
                dividir, posicao = f.dividir, f.posicao_corte
                lombada = Lombada(posicao, 1.0, dividir)
                confianca, paisagem = 1.0, dividir
            sobra = (P.achar_sobra(img, P.DPI_ANALISE)
                     if foto.cortar_sobra and not dividir and f.rotacao == 0 else None)
            inclinacao = detectar_angulo(img) if foto.vai_endireitar else Inclinacao(0.0, 0.0)
            recorte = detectar_bordas(img, dpi=P.DPI_ANALISE) if foto.vai_cortar else Recorte.inteiro()
            dpi_real = dpi_real_da_pagina(doc, f.indice)
            alertas = analise.analisar_folha(
                img, lombada, inclinacao, recorte,
                vai_dividir=foto.vai_dividir and f.redividir,
                vai_endireitar=foto.vai_endireitar, vai_cortar=foto.vai_cortar,
                dpi_real=dpi_real, tamanho_fora_do_padrao=bool(fora[f.indice]))
            if dividir:
                esq, dir_ = dividir_imagem(img, posicao)
                pedacos = [(METADE_ESQUERDA, esq), (METADE_DIREITA, dir_)]
            else:
                pedacos = [(METADE_INTEIRA, img)]
            medir_as_duas = (foto.vai_endireitar and es.jeito_do_livro(foto.livro)
                             == es.JEITO_SCANTAILOR)
            partes = []
            for metade, pedaco in pedacos:
                filtro = f.filtros.get(metade) or f.filtros.get(METADE_INTEIRA) \
                    or next(iter(f.filtros.values()), "original")
                avisos, tem_cor = analise.analisar_pagina(pedaco, filtro)
                discorda, angulo = False, (inclinacao.angulo if foto.vai_endireitar else None)
                if medir_as_duas:
                    provisoria = ConfigPagina(indice=0, folha=f.indice, metade=metade,
                                              endireitar_como=f.endireitar_como.get(metade))
                    contas: dict = {}
                    P._geometria(pedaco, provisoria, foto.livro, dpi=P.DPI_ANALISE,
                                 dpi_do_scan=dpi_real, medidas=contas, com_o_corte=False)
                    discorda = bool(contas.get("discordam"))
                    angulo = P._angulo_que_valeu(contas, angulo)
                partes.append((metade, avisos, bool(tem_cor), discorda, angulo))
            medidas[f.indice] = MedidaDaFolha(
                f.indice, dividir, float(posicao), float(confianca), bool(paisagem), sobra,
                float(inclinacao.angulo), float(inclinacao.confianca), alertas, partes,
                tampa=list(tampa))
            del img
        if progresso is not None:
            progresso(total, total, "Pronto")
    finally:
        doc.close()
    return medidas


# --- aplicar (no fio da janela: muda o projeto, numa acao do Historico) -------

# Os avisos que a medida refaz (os outros, da previa e do PDF, ficam)
_DA_FOLHA = {DIVIDIR: ("nao_parece_dupla", "lombada_incerta"),
             ENDIREITAR: ("muito_torta", "angulo_suspeito"),
             CORTAR: ("corte_pegou_conteudo",)}
_DA_FOLHA_SEMPRE = ("resolucao_baixa", "tamanho_diferente")
_DA_PAGINA_SEMPRE = ("em_branco",)
_DA_PAGINA = {LIMPAR: ("cor",), ENDIREITAR: ("contas_do_endireitar_discordam",)}


class _Gravador:
    """Anota o valor de antes de cada campo que o Automatico muda (livro,
    folha, pagina), para montar a acao do Historico (o desfazer devolve tudo).
    Quando a lista de paginas muda (dividir uma folha que tinha uma pagina so),
    guarda as listas inteiras de antes (`estrutura`)."""

    def __init__(self, projeto) -> None:
        self.projeto = projeto
        self.livro: dict[str, Any] = {}
        self.folhas: dict[tuple[int, str], Any] = {}
        self.paginas: dict[tuple[int, str], Any] = {}
        self.estrutura: dict[str, list] | None = None

    def no_livro(self, campo: str, valor) -> None:
        if campo not in self.livro:
            self.livro[campo] = copy.deepcopy(getattr(self.projeto, campo))
        setattr(self.projeto, campo, valor)

    def na_folha(self, folha, campo: str, valor) -> None:
        chave = (folha.indice, campo)
        if self.estrutura is None and chave not in self.folhas:
            self.folhas[chave] = copy.deepcopy(getattr(folha, campo))
        setattr(folha, campo, valor)

    def na_pagina(self, pagina, campo: str, valor) -> None:
        chave = (pagina.indice, campo)
        if self.estrutura is None and chave not in self.paginas:
            self.paginas[chave] = copy.deepcopy(getattr(pagina, campo))
        setattr(pagina, campo, valor)

    def guardar_a_estrutura(self) -> None:
        """Antes de a lista de paginas mudar: as duas listas inteiras de agora
        (o que foi anotado campo a campo ate aqui volta junto com elas)."""
        if self.estrutura is not None:
            return
        folhas = [dataclasses.asdict(f) for f in self.projeto.folhas]
        paginas = [dataclasses.asdict(p) for p in self.projeto.paginas]
        for (i, campo), valor in self.folhas.items():
            folhas[i][campo] = _json(valor)
        for (i, campo), valor in self.paginas.items():
            paginas[i][campo] = _json(valor)
        self.estrutura = {"folhas": folhas, "paginas": paginas}
        self.folhas, self.paginas = {}, {}

    def acao(self, descricao: str):
        """A acao do Historico com tudo o que mudou (None se nada mudou)."""
        from modelos import Acao

        antes: dict[str, Any] = {}
        depois: dict[str, Any] = {}
        for campo, valor in self.livro.items():
            agora = getattr(self.projeto, campo)
            if _json(agora) != _json(valor):
                antes[f"livro.{campo}"] = _json(valor)
                depois[f"livro.{campo}"] = _json(agora)
        if self.estrutura is not None:
            antes["livro.folhas"] = self.estrutura["folhas"]
            antes["livro.paginas"] = self.estrutura["paginas"]
            depois["livro.folhas"] = [_json(dataclasses.asdict(f)) for f in self.projeto.folhas]
            depois["livro.paginas"] = [_json(dataclasses.asdict(p)) for p in self.projeto.paginas]
            return Acao.nova("automatico", "pagina", [], antes, depois, descricao)
        for (i, campo), valor in self.folhas.items():
            agora = getattr(self.projeto.folhas[i], campo)
            if _json(agora) != _json(valor):
                antes[f"folha:{i}.{campo}"] = _json(valor)
                depois[f"folha:{i}.{campo}"] = _json(agora)
        indices = set()
        for (i, campo), valor in self.paginas.items():
            agora = getattr(self.projeto.paginas[i], campo)
            if _json(agora) != _json(valor):
                antes.setdefault(campo, {})[str(i)] = _json(valor)
                depois.setdefault(campo, {})[str(i)] = _json(agora)
                indices.add(i)
        if not antes:
            return None
        return Acao.nova("automatico", "pagina", sorted(indices), antes, depois, descricao)


def _json(valor):
    """O valor como o JSON grava (tupla vira lista), para comparar e guardar."""
    if isinstance(valor, tuple):
        return [_json(v) for v in valor]
    if isinstance(valor, list):
        return [_json(v) for v in valor]
    if isinstance(valor, dict):
        return {k: _json(v) for k, v in valor.items()}
    return copy.deepcopy(valor)


@dataclass
class Resultado:
    """O que o aplicar fez, para a tela dizer e gravar."""

    acao: Any                      # modelos.Acao ja aplicada (None = nada mudou)
    paginas_mudadas: int = 0
    gravuras_refeitas: int = 0
    estrutura_mudou: bool = False


def _sem_o_codigo(lista, codigo: str) -> list[str]:
    return [c for c in (lista or []) if c != codigo]


def _com_o_codigo(lista, codigo: str) -> list[str]:
    lista = list(lista or [])
    return lista if codigo in lista else lista + [codigo]


def _juntar_avisos(antigos, novos, refeitos) -> list[str]:
    ficam = [a for a in (antigos or []) if a not in refeitos]
    return ficam + [a for a in novos if a not in ficam]


def aplicar(projeto, pedido: Pedido, medidas: dict[int, MedidaDaFolha] | None = None,
            descricao: str = "") -> Resultado:
    """Poe o pedido no projeto aberto (fio da janela). Devolve o Resultado,
    com a acao do Historico JA APLICADA (quem chama so a registra:
    HistoricoAcoes.registrar). Ver o docstring do modulo.

    Arriscado: mudar o projeto sem passar pelo _Gravador (o Ctrl+Z nao
    devolveria); mexer nas paginas que a pessoa escolheu pular (D-004)."""
    medidas = medidas or {}
    g = _Gravador(projeto)
    opcoes = pedido.opcoes or {}
    etapas_pedidas = [e for e in pedido.etapas if e in ETAPAS]
    pular = set(paginas_mexidas(projeto, pedido)) if pedido.pular_mexidas else set()
    escopo = _paginas_do_pedido(projeto, pedido)
    refeitas = 0

    # a ordem arrastada (D-003) e a receita usada (R6) vao para o livro
    if pedido.ordem:
        g.no_livro("ordem_do_automatico", [e for e in pedido.ordem if e in ETAPAS])
    if pedido.receita and not pedido.desligar:
        g.no_livro("receita_usada", pedido.receita)

    # as opcoes das etapas pedidas (sempre do livro)
    for etapa in etapas_pedidas:
        for campo in OPCOES[etapa]:
            if campo in opcoes and hasattr(projeto, campo) and etapa != GRAVURAS:
                if _json(getattr(projeto, campo)) != _json(opcoes[campo]):
                    g.no_livro(campo, copy.deepcopy(opcoes[campo]))

    if pedido.desligar:
        _desligar(projeto, pedido, etapas_pedidas, escopo, g)
    else:
        for etapa in etapas_pedidas:          # na ordem de rodar (D-003/D-016)
            if etapa == DIVIDIR:
                _dividir(projeto, pedido, medidas, pular, g)
                escopo = _paginas_do_pedido_depois_de_dividir(projeto, pedido, escopo)
            elif etapa in NA_PAGINA:
                _ligar_na_pagina(projeto, pedido, etapa, escopo, pular, opcoes, g)
            elif etapa == GRAVURAS:
                g.no_livro("detectar_regioes", True)
                novas = copy.copy(projeto)
                for campo in OPCOES[GRAVURAS]:
                    # "Achar gravuras e fotos" desmarcada vem como a forma
                    # "desligada" (nao procurar: o desligar da regra 8, D-212)
                    setattr(novas, campo, opcoes.get(campo, getattr(projeto, campo)))
                for campo in OPCOES[GRAVURAS]:
                    g.no_livro(campo, getattr(projeto, campo))   # anota o antes
                from core.pipeline import trocar_opcoes_da_gravura
                refeitas = trocar_opcoes_da_gravura(projeto, novas)
            else:                                 # MARGENS, CADERNOS
                g.no_livro(CAMPO_DO_LIVRO[etapa], True)
        _avisos_medidos(projeto, pedido, medidas, g)
        _a_tampa(projeto, medidas, g)                  # etapa 9b-2 (D-559)
        if pedido.no_livro_todo or etapas_pedidas:
            g.no_livro("passou_pelo_automatico", True)

    texto = descricao or ("Automático: " + ", ".join(NOMES[e] for e in etapas_pedidas).lower()
                          + ("" if pedido.paginas is None else
                             f" ({len(escopo)} página{'' if len(escopo) == 1 else 's'})"))
    if pedido.desligar:
        texto = descricao or ("Automático desligado: "
                              + ", ".join(NOMES[e] for e in etapas_pedidas).lower())
    acao = g.acao(texto)
    return Resultado(acao=acao, paginas_mudadas=len(acao.indices) if acao else 0,
                     gravuras_refeitas=refeitas, estrutura_mudou=g.estrutura is not None)


def _a_tampa(projeto, medidas, g: _Gravador) -> None:
    """Etapa 9b-2 (D-559: a tampa do scanner some em todo o livro, também no
    Automático): cada folha medida guarda a tampa achada agora
    (ConfigFolha.tampa_do_scanner; o preparo da página a pinta de branco e, no
    livro em "cortar fora", corta a página na beirada dela). Na mesma ação do
    Automático (o Ctrl+Z a devolve). A folha que não mudou nada (sem tampa, e
    já procurada nesta rotação) não entra na ação."""
    for folha in projeto.folhas:
        medida = medidas.get(folha.indice)
        if medida is None or medida.tampa is None:
            continue
        if _json(getattr(folha, "tampa_do_scanner", None)) != _json(medida.tampa):
            g.na_folha(folha, "tampa_do_scanner", list(medida.tampa))


def _paginas_do_pedido_depois_de_dividir(projeto, pedido: Pedido, antes: list) -> list:
    """Depois de dividir, as paginas do escopo sao as das mesmas folhas (uma
    folha que virou duas paginas entra com as duas)."""
    if pedido.paginas is None:
        return list(projeto.paginas)
    folhas = {p.folha for p in antes}
    return [p for p in projeto.paginas if p.folha in folhas]


def _dividir(projeto, pedido: Pedido, medidas, pular: set, g: _Gravador) -> None:
    """Dividir: cada folha medida ganha a divisao achada. Folha com duas
    paginas na lista: so muda a divisao e a metade da direita (como o "não
    dividir esta" da ferramenta, ui/tela_conferir._alternar_dividir). Folha
    com uma pagina so que passa a ser dividida: a lista de paginas muda (a
    pagina inteira vira esquerda e direita, cada uma com o filtro e os ajustes
    dela; corte, angulo e marcacao, que eram da folha inteira, nao passam).
    Obra 26/10, etapa 4: a pagina partida e a do dividir a mao (core/
    dividir_a_mao.metades_da_pagina); a folha juntada a mao ("não dividir
    esta": uma pagina so) entra aqui como qualquer folha de uma pagina.
    Etapa 9d (D-528): a marcacao feita A MAO na pagina inteira passa para a
    metade em que esta (metades_da_pagina com o corte achado)."""
    from modelos import METADE_DIREITA

    if pedido.no_livro_todo:
        g.no_livro("dividir_folhas", True)
    for folha in projeto.folhas:
        medida = medidas.get(folha.indice)
        if medida is None:
            continue
        pags = [p for p in projeto.paginas if p.folha == folha.indice]
        if any(p.indice in pular for p in pags):
            continue
        g.na_folha(folha, "posicao_corte", round(float(medida.posicao_corte), 4))
        g.na_folha(folha, "confianca_corte", float(medida.confianca_corte))
        g.na_folha(folha, "e_paisagem", bool(medida.e_paisagem))
        g.na_folha(folha, "dividir_como", None)
        g.na_folha(folha, "mexida_a_mao", _sem_o_codigo(folha.mexida_a_mao, E.DIVIDIR))
        if len(pags) >= 2:
            g.na_folha(folha, "dividir", bool(medida.dividir))
            direita = next((p for p in pags if p.metade == METADE_DIREITA), None)
            if direita is not None and any(not p.apagada for p in pags if p is not direita):
                g.na_pagina(direita, "apagada", not medida.dividir)
        elif medida.dividir and pags:
            g.guardar_a_estrutura()
            folha.dividir = True
            # etapa 4: as metades guardadas por um "não dividir esta" eram de
            # outra linha; o Automatico parte a pagina inteira (a mesma conta
            # do dividir a mao: core/dividir_a_mao.metades_da_pagina)
            folha.metades_guardadas = None
            inteira = pags[0]
            from core.dividir_a_mao import metades_da_pagina

            lugar = projeto.paginas.index(inteira)
            # D-528 (etapa 9d): as marcacoes a mao da pagina inteira vao para
            # a metade em que estao (partidas na linha achada agora)
            projeto.paginas[lugar:lugar + 1] = metades_da_pagina(
                inteira, corte=round(float(medida.posicao_corte), 4))
            for n, pagina in enumerate(projeto.paginas):
                pagina.indice = n
        else:
            # uma pagina so, e nao divide: a folha continua inteira
            g.na_folha(folha, "dividir", False)
        if medida.sobra is not None or getattr(folha, "sobra", None) is not None:
            g.na_folha(folha, "sobra", medida.sobra)


def _ligar_na_pagina(projeto, pedido: Pedido, etapa: str, escopo: list, pular: set,
                     opcoes: dict, g: _Gravador) -> None:
    """Endireitar, Cortar, Limpar: no livro todo liga a caixinha; em paginas
    escolhidas liga so nelas (ConfigPagina.automatico). Pagina mexida a mao
    que a pessoa nao quis pular perde o valor a mao daquela etapa (o
    automatico passa a valer nela)."""
    codigo = NA_PAGINA[etapa]
    if pedido.no_livro_todo:
        g.no_livro(CAMPO_DO_LIVRO[etapa], True)
    filtro = opcoes.get("filtro_padrao", projeto.filtro_padrao)
    if etapa == LIMPAR:
        from core import filtros

        if filtro not in filtros.filtros_do_livro(projeto) and filtro != filtros.TIRAR_FUNDO:
            filtro = filtros.ORIGINAL
        if pedido.no_livro_todo:
            g.no_livro("filtro_padrao", filtro)
    for pagina in escopo:
        mexida = E.mexida_a_mao(projeto, pagina, codigo)
        if pagina.indice in pular:
            continue
        if not pedido.no_livro_todo:
            g.na_pagina(pagina, "automatico", _com_o_codigo(pagina.automatico, codigo))
        if mexida or (etapa == LIMPAR and _filtro_trocado_na_pagina(projeto, pagina)):
            g.na_pagina(pagina, "mexida_a_mao", _sem_o_codigo(pagina.mexida_a_mao, codigo))
            if etapa == ENDIREITAR and pagina.angulo_manual is not None:
                g.na_pagina(pagina, "angulo_manual", None)
            if etapa == CORTAR and pagina.recorte is not None:
                g.na_pagina(pagina, "recorte", None)
        if etapa == LIMPAR and pagina.filtro != filtro:
            g.na_pagina(pagina, "filtro", filtro)


def _desligar(projeto, pedido: Pedido, etapas_pedidas: list, escopo: list, g: _Gravador) -> None:
    """Tira o automatico das etapas pedidas (D-068). No livro todo: a caixinha
    desliga e nenhuma pagina fica com a etapa so nela. Em paginas escolhidas:
    elas saem; se a etapa estava ligada no livro todo, ela passa a valer so
    nas OUTRAS paginas (assim as escolhidas ficam sem ela)."""
    nas_escolhidas = {p.indice for p in escopo}
    for etapa in etapas_pedidas:
        if etapa == GRAVURAS:
            g.no_livro("gravura_forma", "desligada")
            continue
        if etapa in (MARGENS, CADERNOS):
            g.no_livro(CAMPO_DO_LIVRO[etapa], False)
            continue
        if etapa == DIVIDIR:
            if pedido.no_livro_todo:
                g.no_livro("dividir_folhas", False)
            folhas = {p.folha for p in escopo}
            for folha in projeto.folhas:
                if folha.indice not in folhas or not folha.dividir:
                    continue
                pags = [p for p in projeto.paginas if p.folha == folha.indice]
                g.na_folha(folha, "dividir", False)
                from modelos import METADE_DIREITA

                direita = next((p for p in pags if p.metade == METADE_DIREITA), None)
                if direita is not None and any(not p.apagada for p in pags if p is not direita):
                    g.na_pagina(direita, "apagada", True)
            continue
        codigo = NA_PAGINA[etapa]
        ligada = ligada_no_livro(projeto, etapa)
        if pedido.no_livro_todo or ligada:
            g.no_livro(CAMPO_DO_LIVRO[etapa], False)
        for pagina in projeto.paginas:
            dentro = pedido.no_livro_todo or pagina.indice in nas_escolhidas
            if dentro:
                if codigo in (pagina.automatico or []):
                    g.na_pagina(pagina, "automatico", _sem_o_codigo(pagina.automatico, codigo))
            elif ligada:
                g.na_pagina(pagina, "automatico", _com_o_codigo(pagina.automatico, codigo))


def _avisos_medidos(projeto, pedido: Pedido, medidas, g: _Gravador) -> None:
    """Os avisos medidos entram nas folhas e paginas medidas (so os codigos
    que a medida refaz; os da previa e do PDF ficam)."""
    from core import analise

    if not medidas:
        return
    rodou = set(pedido.etapas)
    refeitos_folha = set(_DA_FOLHA_SEMPRE)
    for etapa, codigos in _DA_FOLHA.items():
        if etapa in rodou:
            refeitos_folha.update(codigos)
    refeitos_pagina = set(_DA_PAGINA_SEMPRE)
    for etapa, codigos in _DA_PAGINA.items():
        if etapa in rodou:
            refeitos_pagina.update(codigos)
    angulos = []
    for folha in projeto.folhas:
        medida = medidas.get(folha.indice)
        if medida is None:
            continue
        g.na_folha(folha, "alertas", _juntar_avisos(folha.alertas, medida.alertas, refeitos_folha))
        if ENDIREITAR in rodou:
            g.na_folha(folha, "angulo_detectado", float(medida.angulo_detectado))
            g.na_folha(folha, "confianca_angulo", float(medida.confianca_angulo))
        pags = [p for p in projeto.paginas if p.folha == folha.indice]
        for metade, avisos, tem_cor, discorda, angulo in medida.partes:
            pagina = next((p for p in pags if p.metade == metade), None)
            if pagina is None and len(pags) == 1:
                pagina = pags[0]
            if pagina is None:
                continue
            novos = list(avisos)
            if discorda and ENDIREITAR in rodou:
                novos.append(analise.CONTAS_DO_ENDIREITAR_DISCORDAM)
            g.na_pagina(pagina, "alertas", _juntar_avisos(pagina.alertas, novos, refeitos_pagina))
            g.na_pagina(pagina, "tem_cor", bool(tem_cor))
            angulos.append((pagina, angulo))
    if pedido.no_livro_todo and ENDIREITAR in rodou and angulos:
        from core.pipeline import marcar_paginas_diferentes

        antes = {p.indice: list(p.alertas) for p, _ in angulos}
        marcar_paginas_diferentes([p for p, _ in angulos], [a for _, a in angulos])
        for pagina, _ in angulos:
            depois = list(pagina.alertas)
            pagina.alertas = antes[pagina.indice]
            g.na_pagina(pagina, "alertas", depois)


# --- tudo de uma vez (testes e linha de comando) -----------------------------

def rodar(projeto, pedido: Pedido, progresso=None, cancelado=None) -> Resultado:
    """Mede (se precisar) e aplica, no mesmo fio. A janela faz as duas coisas
    separadas (medir num fio de fundo). Quem quiser o desfazer registra
    Resultado.acao no HistoricoAcoes."""
    medidas = medir(fotografar(projeto, pedido), progresso, cancelado) \
        if precisa_medir(pedido) else {}
    return aplicar(projeto, pedido, medidas)


# --- ver como fica (D-577): a pagina da vez, antes e depois do Automatico -------
#
# Decisao D-577 (29/10/2026). Samuel: "eu queria poder nessa etapa do automatico
# poder ver como iria ficar conforme as opções que eu fosse escolhendo." e, sobre a
# pagina da direita da janela grande mostrar o antes e depois com a linha que se
# arrasta: "sim, mas coloca uma bolinha de carregamento [...] porque as vezes vai
# demorar para processar né?". So MOSTRA: o projeto, o historico e o disco nao mudam.
#
# COMO A PREVIA NAO MENTE: o "depois" passa pelo MESMO caminho do "Rodar" de verdade
# (ui/janela_principal.rodar_o_automatico): fotografar -> medir -> aplicar, e a
# pagina desenhada como a tela de conferir a desenha depois (core/pipeline.
# renderizar_pagina, com a mesma composicao "como sai no PDF" da tela). A unica
# diferenca e que `medir` olha so a folha da pagina da vez (o rodar olha todas):
# `medir` mede cada folha sozinha, sem olhar as outras, entao a medida dessa folha
# e a mesma. Tudo acontece numa COPIA do projeto (copia_para_a_previa, feita no
# fio da janela); o que aplicar e o desenho anotam fica na copia, que e jogada fora.
# Os guardados de memoria do pipeline (corte e angulo ja medidos, por chave) sao
# os mesmos do programa: a chave tem tudo de que a conta depende, entao a previa
# so adianta o que o rodar de verdade faria igual.
#
# O QUE A PREVIA NAO MOSTRA IGUAL (ressalvas escritas, ver tambem a entrega):
#   - "Margens iguais": a conta precisa de TODAS as paginas medidas
#     (pipeline.conta_das_margens_para_a_tela); sem isso a tela de conferir mostra
#     sem margem ate medir por tras, e a previa tambem (nao mede o livro inteiro).
#   - "Cortar seguindo o conteúdo": "todas as páginas do tamanho da maior" depende
#     do livro inteiro medido (pipeline.tamanho_do_livro); a previa corta pelo
#     conteudo da propria pagina, como a tela de conferir logo depois de rodar.
#   - "Montar cadernos": nao muda a pagina (monta as folhas para imprimir).
#   - A pergunta das paginas mexidas a mao (D-004): a previa usa o pedido como
#     esta (de fabrica, pular as mexidas); o rodar de verdade pergunta.
#   - A resolucao: o desenho e na resolucao da tela (quem chama escolhe o dpi);
#     o corte e o angulo sao os da resolucao do PDF (renderizar_pagina ja faz
#     assim), mas a marcacao achada sozinha e a provisoria da resolucao da tela,
#     como na previa da tela de conferir (o PDF acha na resolucao dele).
#
# Seguro mudar: nada aqui sem mudar junto o rodar de verdade. Arriscado: medir
# folhas fora do pedido (aplicar dividiria/mexeria nelas: _dividir usa toda folha
# que tem medida), ou fazer qualquer conta no projeto aberto em vez da copia.

def copia_para_a_previa(projeto):
    """Uma copia inteira do projeto, para a previa mexer a vontade. Fazer no
    fio da janela (o projeto aberto so muda nele); a tarefa de fundo so le a
    copia."""
    return copy.deepcopy(projeto)


def paginas_depois(projeto, folha: int, metade: str) -> list:
    """As paginas que a pagina (folha, metade) vira DEPOIS do aplicar, na copia:
    a mesma metade da mesma folha, se ainda existe e vai para o PDF; senao as
    paginas da folha que vao para o PDF (Projeto.paginas_ativas, na ordem do
    PDF: a folha inteira que foi dividida vira
    as duas metades; a dividida que foi juntada vira a inteira)."""
    da_folha = [p for p in projeto.paginas_ativas if p.folha == folha]
    iguais = [p for p in da_folha if p.metade == metade]
    return iguais[:1] if iguais else da_folha


def como_sai_na_tela(img, projeto, pagina, dpi: float):
    """A pagina desenhada `img` como ela sai no PDF: com as margens iguais (se
    ja medidas) e movida na folha. A MESMA conta da tela de conferir
    (ui/tela_conferir._como_sai_no_pdf, D-547), sem pedir medida nenhuma.
    Nunca levanta (devolve `img`)."""
    from core.etapas import conteudo_mexido
    from core.folha import compor_na_folha
    from core.pipeline import conta_das_margens_para_a_tela, margens_na_tela

    if img is None:
        return img
    try:
        conta = conta_das_margens_para_a_tela(projeto)
        com_margens = margens_na_tela(img, projeto, pagina, conta) if conta is not None else img
        return compor_na_folha(com_margens, pagina.tamanho_folha_cm, dpi,
                               escala=pagina.conteudo_escala,
                               deslocamento=pagina.conteudo_deslocamento,
                               mexido_a_mao=conteudo_mexido(projeto, pagina))
    except Exception:  # noqa: BLE001 - a previa mostra a pagina como veio do desenho
        return img


def antes_da_pagina(doc, copia, indice: int, dpi: int):
    """O "antes" da previa do Automatico (D-577, 30/10/2026, depois do 2o
    teste): a folha da pagina `indice` CRUA, como veio do PDF - sem filtro,
    sem girar, sem dividir, sem endireitar, sem cortar, sem margens.

    Samuel: "o antes é sem filtro e sem cortar sem nada, o depois na tela de
    atualizar que aplica os filtros de endireitar cortar ou fazer qualquer
    outra coisa para ver como iria ficar." (no lugar de "mostra já cortada e
    endireitada se tiver sido feito isso.", dito antes no mesmo dia). O antes
    e o depois podem ter tamanhos diferentes: a vista com a linha poe os dois
    na mesma escala (ui/automatico.VistaAntesDepoisComZoom).

    FOLHA DIVIDIDA (resposta do Samuel, "pode", 30/10, palavra por palavra):
      (1) "A folha já foi dividida: o antes mostra só a metade dela, crua, sem
          filtro e sem endireitar. O depois mostra essa mesma metade pronta."
      (2) "A folha ainda não foi dividida e 'Dividir folhas ao meio' está
          marcada: o antes mostra a folha inteira, crua. O depois mostra as
          duas metades prontas, uma ao lado da outra, como já faz hoje."
      (3) "[...] O antes continua sendo a folha inteira crua, porque é dela
          que as duas metades vão sair. Se ela desmarcar 'Dividir', o depois
          volta a ser a folha inteira pronta. Se a folha já tinha sido
          dividida antes, o antes mostra só a metade crua, com 'Dividir'
          marcado ou não."
    Quem decide e a pagina NO LIVRO (a `copia` ainda sem o pedido aplicado):
    metade de folha dividida -> so a metade; senao -> a folha inteira. Nao
    depende do "Dividir" marcado na janela.
    A metade e tirada da folha crua como o programa divide (o giro de 90 da
    folha, que diz para que lado ela fica de pe, e a linha do corte:
    core.pipeline.girar_90 e dividir_imagem), e mais nada: sem a tampa
    pintada, sem a sobra, sem cortar, sem endireitar, sem filtro. A folha
    inteira sai sem giro nenhum (como veio do PDF).

    Ate 30/10 (29/10) o antes era a pagina como esta no livro, com o filtro
    dela: agora e pagina_como_esta (o "comparar" da tela cheia). Nao muda a
    `copia`. Arriscado: decidir pela metade DEPOIS do aplicar (o caso 3
    mudaria com o "Dividir" marcado)."""
    from core.pdf_io import pagina_para_array
    from core.pipeline import dividir_imagem, girar_90
    from modelos import METADE_ESQUERDA, METADE_INTEIRA

    pagina = copia.paginas[indice]
    folha = copia.folhas[pagina.folha]
    crua = pagina_para_array(doc, folha.indice, dpi=dpi)
    if not (folha.dividir and pagina.metade != METADE_INTEIRA):
        return crua
    if folha.rotacao:
        crua = girar_90(crua, folha.rotacao)
    esquerda, direita = dividir_imagem(crua, folha.posicao_corte)
    return esquerda if pagina.metade == METADE_ESQUERDA else direita


def pagina_como_esta(doc, copia, indice: int, dpi: int):
    """A pagina `indice` como esta agora no livro, COM o filtro que ela ja tem
    (Original ou o aplicado), desenhada na `copia`. E a tela da esquerda do
    "comparar" da tela cheia da previa (D-577, 30/10: "nessa vai ter o filtro
    que estava antes, seja ele original ou que foi aplicado e o filtro que
    está selecionado no momento")."""
    from core.pipeline import renderizar_pagina

    pagina = copia.paginas[indice]
    img, _ = renderizar_pagina(doc, copia, pagina, dpi=dpi)
    return como_sai_na_tela(img, copia, pagina, dpi)


def filtro_depois(copia, folha: int, metade: str) -> str:
    """O filtro com que a pagina (folha, metade) sai DEPOIS do aplicar na
    `copia` (o rotulo da tela da direita do "comparar"). "" se ela nao vai
    para o PDF."""
    from core import etapas

    novas = paginas_depois(copia, folha, metade)
    return etapas.filtro_que_vale(copia, novas[0]) if novas else ""


def depois_da_pagina(doc, copia, pedido: Pedido, indice: int, dpi: int,
                     cancelado: Callable | None = None) -> list:
    """O "depois" da pagina `indice`: como ela sai se o Automatico rodar com o
    `pedido`. MUDA A `copia` (aplica o pedido nela): passar sempre uma copia
    (copia_para_a_previa). Devolve as imagens das paginas que ela vira (uma; ou
    duas, quando a folha inteira e dividida; ver paginas_depois).
    `cancelado()` True = para (levanta core.pipeline.Cancelou)."""
    from core import pipeline as P

    pagina = copia.paginas[indice]
    folha, metade = pagina.folha, pagina.metade
    medidas: dict = {}
    if precisa_medir(pedido):
        foto = fotografar(copia, pedido)
        # so a folha da pagina da vez (e so se ela esta no pedido: fotografar
        # ja deixa de fora as folhas fora do "Rodar em")
        foto.folhas = [f for f in foto.folhas if f.indice == folha]
        if foto.folhas:
            medidas = medir(foto, cancelado=cancelado)
    if cancelado is not None and cancelado():
        raise P.Cancelou()
    aplicar(copia, pedido, medidas)
    imagens = []
    for nova in paginas_depois(copia, folha, metade):
        if cancelado is not None and cancelado():
            raise P.Cancelou()
        img, _ = P.renderizar_pagina(doc, copia, nova, dpi=dpi)
        imagens.append(como_sai_na_tela(img, copia, nova, dpi))
    return imagens


def medir_o_livro_ao_abrir(projeto, progresso=None, cancelado=None) -> dict[int, MedidaDaFolha]:
    """D-284 ("Medir o livro inteiro por trás, depois de abrir"): mede as
    folhas como estao, sem ligar etapa nenhuma (os avisos de pagina em branco,
    de cor, de resolucao baixa e de tamanho diferente). So LE: quem poe os
    avisos no projeto e `avisos_do_livro` (no fio da janela)."""
    return medir(fotografar(projeto, Pedido(etapas=[])), progresso, cancelado)


def avisos_do_livro(projeto, medidas: dict[int, MedidaDaFolha]) -> int:
    """Poe no projeto os avisos da medida feita ao abrir (D-284) e tira as
    observacoes do livro (o que vale para quase todas as paginas vira uma frase
    so). NAO muda pagina nenhuma (nem filtro, nem corte, nem angulo): so os
    avisos e a cor. Nao entra no Historico (avisos nao sao trabalho). Devolve
    quantas folhas mudaram de aviso."""
    from core import analise

    mudaram = 0
    for folha in projeto.folhas:
        medida = medidas.get(folha.indice)
        if medida is None:
            continue
        novos = _juntar_avisos(folha.alertas, medida.alertas, set(_DA_FOLHA_SEMPRE))
        if novos != folha.alertas:
            folha.alertas = novos
            mudaram += 1
        pags = [p for p in projeto.paginas if p.folha == folha.indice]
        for metade, avisos, tem_cor, _d, _a in medida.partes:
            pagina = next((p for p in pags if p.metade == metade), None)
            if pagina is None and len(pags) == 1:
                pagina = pags[0]
            if pagina is None:
                continue
            pagina.alertas = _juntar_avisos(pagina.alertas, avisos, set(_DA_PAGINA_SEMPRE))
            pagina.tem_cor = bool(tem_cor)
    if len(medidas) == len(projeto.folhas):
        observacoes: list[str] = []
        for itens in (projeto.folhas, projeto.paginas):
            achadas, remover = analise.separar_observacoes([i.alertas for i in itens])
            observacoes.extend(achadas)
            if remover:
                for item in itens:
                    item.alertas = [a for a in item.alertas if a not in remover]
        projeto.observacoes = observacoes
    return mudaram
