"""O lugar UNICO que responde, por pagina: "esta etapa vale aqui?".

POR QUE EXISTE (obra de 26/10/2026, etapa 1; decisao D-009 do Samuel, 26/10/2026:
"eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo
manualmente.")

Ate aqui cada caixinha da tela "O que fazer" (Projeto.cortar_bordas,
.endireitar, .limpar, .detectar_regioes) queria dizer DUAS coisas ao mesmo tempo:
"o automatico faz esta etapa" e "o que a pessoa fez a mao nesta etapa vale".
Com a caixinha desligada, core/pipeline.py jogava fora o corte a mao, o angulo
a mao, o filtro da pagina, a marcacao a mao e o "so neste pedaco". Agora as duas
coisas sao separadas:

    a etapa vale nesta pagina = o automatico dela esta ligado
                                OU a pessoa mexeu a mao nesta pagina, nesta etapa

e TODO o pipeline pergunta aqui (corta, endireita, filtra, filtro_que_vale,
marca_sozinho, marcacao_a_mao, conteudo_mexido...), em vez de olhar a caixinha.
O automatico continua morando na caixinha (Projeto.cortar_bordas etc.): o que
o programa MEDE sozinho (corte, angulo, gravura) so e medido com ela ligada.

A MARCA "MEXIDA A MAO" (decisao D-004, 28/09/2026: "Automático em livro já
mexido à mão: o programa pergunta se quer pular as páginas mexidas.")

ConfigPagina.mexida_a_mao e ConfigFolha.mexida_a_mao: a lista das etapas em que
a pessoa mexeu a mao naquela pagina/folha (codigos abaixo, nunca texto de
tela). Quem grava: a tela, chamando marcar_mexida_a_mao / desmarcar_mexida_a_mao
ao mexer (as etapas 2 e 3 da obra ligam isso); e a migracao do projeto
(marcar_pelos_valores, chamada por modelos.Projeto.de_dicionario), que marca a
partir dos valores a mao que ja existem. Quem le: a pergunta do Automatico
(etapa 3, paginas_mexidas_a_mao) e feito_a_mao_vale (abaixo).

PROJETO ANTIGO SAI IGUAL (escolha do implementador, D-014; ONDE-PAREI)

Projeto.feito_a_mao_sempre_vale: True no livro novo (de fabrica); False no
projeto gravado ANTES desta etapa (modelos.Projeto.de_dicionario, setdefault).
Num projeto antigo o valor a mao com a etapa desligada era ignorado; para o PDF
dele sair identico, ali o valor a mao so vale com a etapa ligada (como sempre)
ou quando a pagina tem a MARCA da etapa (isto e, foi mexida a mao depois desta
versao, pela tela). A migracao so marca o que ja valia (a etapa estava ligada),
entao nada muda no PDF do projeto antigo ao abrir. Livro novo: todo valor a mao
vale, com marca ou sem (o filtro e o dividir so pela marca: ver abaixo).

O QUE CONTA COMO "VALOR A MAO" EM CADA ETAPA (_tem_valor_a_mao)

    cortar      ConfigPagina.recorte nao e None (o automatico nunca o grava)
    endireitar  ConfigPagina.angulo_manual nao e None
    filtro      NADA pelo valor: so a MARCA conta. A pagina nasce com o filtro do
                livro, mas o filtro do livro pode mudar depois na tela "O que
                fazer" (o radio continua escolhido mesmo com "Limpar a folha"
                desligado) e as paginas ficam com o de antes: "filtro diferente
                do livro" marcaria o livro inteiro como mexido a mao e o PDF
                sairia filtrado com "Limpar" desligado. A tela grava a marca
                FILTRO ao escolher o filtro (ou um ajuste dele) numa pagina.
    marcar      alguma regiao da marcacao feita a mao (core.selecao.MAO)
    mover       conteudo_escala diferente de 1, deslocamento diferente de (0, 0)
                ou um tamanho de folha escolhido (tamanho_folha_cm)
    dividir     (folha) NADA pelo valor, como o filtro: a folha pode ter ficado
                dividida de uma analise com "Dividir folhas" ligado; so a marca
    girar       (folha) girada de 90 em 90 (ConfigFolha.rotacao)
O que nao da para saber pelo valor (ex.: a forca do preto mexida numa pagina
que ficou no filtro do livro; a linha de divisao arrastada com o "Dividir"
ligado) so conta pela MARCA que a tela grava.

O AUTOMATICO POR PAGINA (obra de 26/10/2026, etapa 3; D-002, 26/10: "eu quero poder
sim fazer automatico para todo livro, mas também quero pode fazer uma a uma.")

O automatico de cada etapa mora na caixinha do livro (Projeto.cortar_bordas,
.endireitar, .limpar) quando roda no livro todo. Quando o Automatico roda so em
algumas paginas (ou numa so), a etapa fica ligada SO nelas:
ConfigPagina.automatico = lista das etapas (CORTAR, ENDIREITAR, FILTRO) que o
automatico faz naquela pagina mesmo com a caixinha do livro desligada. Quem
grava: core/automatico.py (rodar em paginas escolhidas); quem le: as funcoes
"sozinho" daqui (corta_sozinho(projeto, pagina), endireita_sozinho,
limpa_sozinho, marca_sozinho), que o pipeline chama com a pagina. Sem a pagina
(quem pergunta pelo livro), so a caixinha. Pagina de projeto antigo nao tem o
campo: lista vazia, nada muda.

Seguro mudar: acrescentar etapa nova (codigo + _tem_valor_a_mao + uma funcao
"vale?"). Arriscado: (1) fazer uma funcao "vale?" devolver True num projeto
antigo sem a marca (o PDF dele mudaria: prova em tests/test_decisoes.py e
relatorios/obra-etapa1/); (2) fazer o AUTOMATICO medir com a caixinha
desligada (marca_sozinho, Projeto.cortar_bordas...): mudaria o livro novo de
fabrica (prova "Desligado de fabrica", 96 de 96); (3) importar ui/ aqui.

Nunca importa modelos.py no topo (modelos.py usa este modulo na migracao):
le os campos por getattr, com padrao, e serve para objeto de versao antiga.
"""

from __future__ import annotations

# --- os codigos das etapas (internos; nunca texto de tela) ------------------

CORTAR = "cortar"          # corte das bordas (ConfigPagina.recorte)
ENDIREITAR = "endireitar"  # angulo (ConfigPagina.angulo_manual)
FILTRO = "filtro"          # filtro da pagina e os ajustes dele
MARCAR = "marcar"          # marcacao de gravura/letra/papel e "so neste pedaco"
MOVER = "mover"            # mover/redimensionar o conteudo e o tamanho da folha
DIVIDIR = "dividir"        # (folha) dividir e a linha de divisao
GIRAR = "girar"            # (folha) girar de 90 em 90

ETAPAS_DA_PAGINA = (CORTAR, ENDIREITAR, FILTRO, MARCAR, MOVER)
ETAPAS_DA_FOLHA = (DIVIDIR, GIRAR)

_TOLERANCIA = 1e-9


# --- a marca "mexida a mao" (D-004) ------------------------------------------

def _marcas(item) -> list:
    marcas = getattr(item, "mexida_a_mao", None)
    return marcas if isinstance(marcas, list) else []


def marcar_mexida_a_mao(item, etapa: str) -> bool:
    """O que a TELA chama quando a pessoa mexe a mao numa pagina (ConfigPagina)
    ou folha (ConfigFolha), numa etapa (CORTAR, ENDIREITAR, FILTRO, MARCAR,
    MOVER; DIVIDIR, GIRAR na folha). Devolve True se a marca e nova. Grava uma
    lista NOVA (quem guardou a antiga, como o desfazer, nao ve a mudanca por
    baixo). Nao muda imagem nenhuma por si: so diz que a pessoa mexeu.
    Item sem o campo (objeto de versao antiga): ganha o campo."""
    marcas = _marcas(item)
    if etapa in marcas:
        return False
    item.mexida_a_mao = [*marcas, etapa]
    return True


def desmarcar_mexida_a_mao(item, etapa: str) -> bool:
    """O contrario de marcar_mexida_a_mao: o que a tela chama quando a pessoa
    devolve a etapa ao automatico ("voltar ao automatico", desfazer ate o
    comeco). Devolve True se havia a marca."""
    marcas = _marcas(item)
    if etapa not in marcas:
        return False
    item.mexida_a_mao = [m for m in marcas if m != etapa]
    return True


def _regioes_a_mao(pagina) -> list:
    """As regioes da marcacao da pagina feitas a mao, como gravadas
    (dicionarios). Barato: nao monta objeto."""
    from core.selecao import MAO

    selecao = getattr(pagina, "selecao", None) or []
    return [r for r in selecao if isinstance(r, dict) and str(r.get("origem", MAO)) == MAO]


def _tem_valor_a_mao(projeto, item, etapa: str) -> bool:
    """O item tem um valor que so a pessoa poe, nesta etapa? (ver o docstring
    do modulo). Le so campos."""
    if etapa == CORTAR:
        return getattr(item, "recorte", None) is not None
    if etapa == ENDIREITAR:
        return getattr(item, "angulo_manual", None) is not None
    if etapa == FILTRO:
        return False        # so pela marca (ver o docstring do modulo)
    if etapa == MARCAR:
        return bool(_regioes_a_mao(item))
    if etapa == MOVER:
        return (_conteudo_fora_do_padrao(item)
                or getattr(item, "tamanho_folha_cm", None) is not None)
    if etapa == DIVIDIR:
        return False        # so pela marca (ver o docstring do modulo)
    if etapa == GIRAR:
        return int(getattr(item, "rotacao", 0) or 0) % 360 != 0
    return False


def mexida_a_mao(projeto, item, etapa: str) -> bool:
    """A pagina/folha foi mexida a mao nesta etapa? A MARCA gravada, ou um
    valor que so a pessoa poe (_tem_valor_a_mao). E o que a pergunta do
    Automatico (D-004, etapa 3) usa para saber quem pular. Nao diz se o valor
    VALE no PDF: isso e feito_a_mao_vale (projeto antigo)."""
    return etapa in _marcas(item) or _tem_valor_a_mao(projeto, item, etapa)


def etapas_mexidas_a_mao(projeto, item) -> list[str]:
    """As etapas em que a pagina (ou folha) foi mexida a mao, na ordem de
    ETAPAS_DA_PAGINA / ETAPAS_DA_FOLHA."""
    todas = ETAPAS_DA_FOLHA if hasattr(item, "rotacao") else ETAPAS_DA_PAGINA
    return [e for e in todas if mexida_a_mao(projeto, item, e)]


def paginas_mexidas_a_mao(projeto, etapa: str | None = None) -> list:
    """As paginas mexidas a mao (numa etapa, ou em qualquer uma). Para a
    pergunta "pular as paginas mexidas?" do Automatico (D-004, etapa 3)."""
    etapas = ETAPAS_DA_PAGINA if etapa is None else (etapa,)
    return [p for p in getattr(projeto, "paginas", [])
            if any(mexida_a_mao(projeto, p, e) for e in etapas)]


def folhas_mexidas_a_mao(projeto, etapa: str | None = None) -> list:
    """As folhas mexidas a mao (dividir, girar). Ver paginas_mexidas_a_mao."""
    etapas = ETAPAS_DA_FOLHA if etapa is None else (etapa,)
    return [f for f in getattr(projeto, "folhas", [])
            if any(mexida_a_mao(projeto, f, e) for e in etapas)]


def _etapa_ligada(projeto, etapa: str, pagina=None) -> bool:
    """O automatico desta etapa esta ligado no livro (a caixinha) ou, com a
    `pagina`, so nela (ConfigPagina.automatico, etapa 3 da obra)?"""
    if etapa == CORTAR:
        return corta_sozinho(projeto, pagina)
    if etapa == ENDIREITAR:
        return endireita_sozinho(projeto, pagina)
    if etapa == FILTRO:
        return limpa_sozinho(projeto, pagina)
    if etapa == MARCAR:
        return marca_sozinho(projeto, pagina)
    if etapa in (DIVIDIR, GIRAR):
        # dividir e girar a mao sempre valeram no pipeline; so o caminho rapido
        # "so cadernos" (Projeto.so_cadernos) os ignorava
        return not getattr(projeto, "so_cadernos", False)
    return False      # MOVER: nao tem automatico


def marcar_pelos_valores(projeto) -> int:
    """A migracao: grava a marca "mexida a mao" a partir dos valores a mao que
    ja existem (chamada por modelos.Projeto.de_dicionario). Devolve quantas
    marcas novas.

    Livro novo (feito_a_mao_sempre_vale): marca todo valor a mao (ele ja vale).
    Projeto antigo: so marca onde o valor JA VALIA no PDF (a etapa ligada), para
    o PDF continuar identico; o valor que era ignorado (etapa desligada) fica
    sem marca e continua ignorado ate a pessoa mexer de novo pela tela. MOVER
    nunca e marcado no projeto antigo: a marca muda a conta do compor_na_folha
    (core/folha.py) e o PDF dele poderia mudar um ponto."""
    novo = bool(getattr(projeto, "feito_a_mao_sempre_vale", True))
    novas = 0
    for pagina in getattr(projeto, "paginas", []):
        for etapa in ETAPAS_DA_PAGINA:
            if not novo and (etapa == MOVER or not _etapa_ligada(projeto, etapa, pagina)):
                continue
            if _tem_valor_a_mao(projeto, pagina, etapa):
                novas += marcar_mexida_a_mao(pagina, etapa)
    for folha in getattr(projeto, "folhas", []):
        for etapa in ETAPAS_DA_FOLHA:
            if not novo and not _etapa_ligada(projeto, etapa):
                continue
            if _tem_valor_a_mao(projeto, folha, etapa):
                novas += marcar_mexida_a_mao(folha, etapa)
    return novas


# --- o feito a mao vale? (D-009) ---------------------------------------------

def feito_a_mao_vale(projeto, item, etapa: str) -> bool:
    """O valor a mao desta etapa vale no PDF mesmo com o automatico dela
    desligado? Livro novo: sempre (D-009). Projeto antigo: so com a marca (ver
    o docstring do modulo). Com a etapa ligada, o valor a mao vale sempre, como
    sempre valeu (quem chama ja olha a caixinha antes)."""
    if getattr(projeto, "feito_a_mao_sempre_vale", True):
        return True
    return etapa in _marcas(item)


def _vale(projeto, item, etapa: str) -> bool:
    return _etapa_ligada(projeto, etapa, item) or feito_a_mao_vale(projeto, item, etapa)


# --- cortar e endireitar -----------------------------------------------------

def recorte_a_mao(projeto, pagina):
    """O corte a mao que vale nesta pagina (x, y, largura, altura em fracao),
    ou None (sem corte a mao, ou projeto antigo com a etapa desligada e sem a
    marca). Com "Cortar as bordas" ligado e o recorte gravado, e ele, como
    sempre foi."""
    recorte = getattr(pagina, "recorte", None)
    if recorte is None or not _vale(projeto, pagina, CORTAR):
        return None
    return tuple(recorte)


def no_automatico_da_pagina(pagina, etapa: str) -> bool:
    """A etapa esta ligada SO nesta pagina (ConfigPagina.automatico: o
    Automatico rodou nela, etapa 3 da obra)? Pagina None ou sem o campo: nao."""
    if pagina is None:
        return False
    automatico = getattr(pagina, "automatico", None)
    return isinstance(automatico, list) and etapa in automatico


def corta_sozinho(projeto, pagina=None) -> bool:
    """O AUTOMATICO do corte esta ligado (mede o corte das paginas sem corte a
    mao)? E a caixinha "Cortar as bordas" do livro OU, com a `pagina`, o
    Automatico rodado so nela (etapa 3 da obra)."""
    return (bool(getattr(projeto, "cortar_bordas", False))
            or no_automatico_da_pagina(pagina, CORTAR))


def corta(projeto, pagina) -> bool:
    """Esta pagina e cortada? Automatico ligado OU corte a mao que vale."""
    return corta_sozinho(projeto, pagina) or recorte_a_mao(projeto, pagina) is not None


def angulo_a_mao(projeto, pagina) -> float | None:
    """O angulo a mao que vale nesta pagina (graus), ou None. Ver recorte_a_mao."""
    angulo = getattr(pagina, "angulo_manual", None)
    if angulo is None or not _vale(projeto, pagina, ENDIREITAR):
        return None
    return float(angulo)


def endireita_sozinho(projeto, pagina=None) -> bool:
    """O AUTOMATICO do endireitar esta ligado (mede o angulo das paginas sem
    angulo a mao)? E a caixinha "Endireitar" do livro OU, com a `pagina`, o
    Automatico rodado so nela (etapa 3 da obra)."""
    return (bool(getattr(projeto, "endireitar", False))
            or no_automatico_da_pagina(pagina, ENDIREITAR))


def endireita(projeto, pagina) -> bool:
    """Esta pagina e endireitada (girada pelo angulo)? Automatico ligado OU
    angulo a mao que vale. Quem gira ainda olha o ANGULO_MINIMO."""
    return endireita_sozinho(projeto, pagina) or angulo_a_mao(projeto, pagina) is not None


# --- filtro e marcacao -------------------------------------------------------

def filtro_a_mao(projeto, pagina) -> bool:
    """O filtro desta pagina foi escolhido a mao (com "Limpar a folha"
    desligado)? So pela marca FILTRO, que a tela grava (o valor nao diz: ver o
    docstring do modulo). Vale no livro novo e no projeto antigo."""
    return FILTRO in _marcas(pagina)


def limpa_sozinho(projeto, pagina=None) -> bool:
    """O AUTOMATICO do filtro ("Limpar a folha") esta ligado? A caixinha do
    livro OU, com a `pagina`, o Automatico rodado so nela (etapa 3 da obra)."""
    return (bool(getattr(projeto, "limpar", False))
            or no_automatico_da_pagina(pagina, FILTRO))


def filtro_que_vale(projeto, pagina) -> str:
    """O filtro com que a pagina sai: o dela, com "Limpar a folha" ligado (como
    sempre; no livro ou so nesta pagina) ou escolhido a mao; senao o Original
    (a pagina como veio). E o que as contas que perguntavam "projeto.limpar
    and pagina.filtro == X" usam."""
    from core.filtros import ORIGINAL

    if limpa_sozinho(projeto, pagina) or filtro_a_mao(projeto, pagina):
        return getattr(pagina, "filtro", ORIGINAL)
    return ORIGINAL


def marca_sozinho(projeto, pagina=None) -> bool:
    """O AUTOMATICO da marcacao (procurar gravura, letra e papel) esta ligado?
    "Limpar a folha" (do livro, ou so nesta `pagina`: limpa_sozinho) e
    "Procurar gravura e letra" (Projeto.detectar_regioes)."""
    return bool(limpa_sozinho(projeto, pagina) and getattr(projeto, "detectar_regioes", False))


def marcacao_a_mao_vale(projeto, pagina) -> bool:
    """A pagina tem marcacao feita a mao que vale (com o automatico da
    marcacao desligado)?"""
    return bool(_regioes_a_mao(pagina)) and feito_a_mao_vale(projeto, pagina, MARCAR)


def marcacao_a_mao(projeto, pagina):
    """A marcacao que vale com o automatico desligado: so as regioes feitas a
    mao (core.selecao.MAO), na ordem em que estavam (um "tirar" a mao so apaga
    o que veio antes dele). Vazia se nao valem (projeto antigo sem a marca)."""
    from core.selecao import MAO, Selecao

    if not marcacao_a_mao_vale(projeto, pagina):
        return Selecao()
    selecao = Selecao.de_lista(getattr(pagina, "selecao", None) or [])
    return Selecao(regioes=[r for r in selecao.regioes if r.origem == MAO])


def tem_pedaco_a_mao(projeto, pagina) -> bool:
    """A marcacao a mao que vale tem "so neste pedaco" (um filtro proprio)?"""
    return any(str(r.get("filtro") or "") for r in _regioes_a_mao(pagina)) \
        and feito_a_mao_vale(projeto, pagina, MARCAR)


def filtra(projeto, pagina) -> bool:
    """A etapa do filtro roda nesta pagina? "Limpar a folha" ligado (como
    sempre) OU o filtro escolhido a mao OU marcacao a mao (pedaco, "pintar por
    cima"...). Com so a marcacao, a pagina fica no Original e so o que foi
    marcado a mao muda (core.pipeline._filtrar_a_pagina)."""
    return (limpa_sozinho(projeto, pagina) or filtro_a_mao(projeto, pagina)
            or marcacao_a_mao_vale(projeto, pagina))


# --- mover e redimensionar o conteudo (D-008) --------------------------------

def _conteudo_fora_do_padrao(pagina) -> bool:
    escala = float(getattr(pagina, "conteudo_escala", 1.0) or 1.0)
    deslocamento = getattr(pagina, "conteudo_deslocamento", (0.0, 0.0)) or (0.0, 0.0)
    return (abs(escala - 1.0) > _TOLERANCIA
            or any(abs(float(v)) > _TOLERANCIA for v in tuple(deslocamento)[:2]))


def conteudo_fora_do_padrao(pagina) -> bool:
    """A pagina tem tamanho ou posicao do conteudo diferentes do de fabrica
    (escala 1, deslocamento 0)? Le so os campos, sem olhar se vale. Para o
    "usar em todas" da ferramenta Mover (etapa 5 da obra) desmarcar as
    paginas que ja tem o seu (D-090: "nunca apaga exceção")."""
    return _conteudo_fora_do_padrao(pagina)


def conteudo_mexido(projeto, pagina) -> bool:
    """O conteudo desta pagina foi movido ou redimensionado a mao, e isso vale?
    Com True, core/folha.compor_na_folha nunca joga o mover fora (sem tamanho
    de folha, a folha e a propria pagina; com 1 ponto de arredondamento a mais,
    nao desiste). Projeto antigo sem a marca MOVER: False (a conta de sempre)."""
    return _conteudo_fora_do_padrao(pagina) and feito_a_mao_vale(projeto, pagina, MOVER)


# --- o livro inteiro ---------------------------------------------------------

def tem_feito_a_mao_que_vale(projeto) -> bool:
    """Ha alguma pagina ou folha mexida a mao cujo valor vale no PDF? Para o
    caminho rapido "so cadernos" (modelos.Projeto.so_cadernos), que nao desenha
    pagina nenhuma: com algo a mao valendo, o livro tem de passar pelo caminho
    inteiro. Projeto antigo: so as marcas (o caminho rapido dele fica igual)."""
    novo = bool(getattr(projeto, "feito_a_mao_sempre_vale", True))
    for pagina in getattr(projeto, "paginas", []):
        if getattr(pagina, "apagada", False):
            continue
        for etapa in ETAPAS_DA_PAGINA:
            if etapa == FILTRO:
                vale = filtro_a_mao(projeto, pagina)
            elif etapa == MARCAR:
                vale = marcacao_a_mao_vale(projeto, pagina)
            elif etapa == MOVER:
                vale = feito_a_mao_vale(projeto, pagina, MOVER) and (
                    _tem_valor_a_mao(projeto, pagina, MOVER))
            else:
                vale = feito_a_mao_vale(projeto, pagina, etapa) and (
                    _tem_valor_a_mao(projeto, pagina, etapa))
            if vale:
                return True
        if getattr(pagina, "em_branco", False) and novo:
            return True
    for folha in getattr(projeto, "folhas", []):
        for etapa in ETAPAS_DA_FOLHA:
            if (novo or etapa in _marcas(folha)) and _tem_valor_a_mao(projeto, folha, etapa):
                return True
    return False


def paginas_a_mao_fora_do_automatico(projeto) -> list:
    """As paginas com algo feito a mao que vale numa etapa cujo automatico
    esta DESLIGADO (o que so sai no PDF por causa da D-009). Para o resumo da
    tela "O que fazer" dizer que isso vai junto (core.pipeline.
    resumo_em_portugues). Le so campos."""
    achadas = []
    for pagina in getattr(projeto, "paginas", []):
        if getattr(pagina, "apagada", False):
            continue
        if ((not corta_sozinho(projeto, pagina) and recorte_a_mao(projeto, pagina) is not None)
                or (not endireita_sozinho(projeto, pagina) and angulo_a_mao(projeto, pagina) is not None)
                or (not limpa_sozinho(projeto, pagina)
                    and (filtro_a_mao(projeto, pagina) or marcacao_a_mao_vale(projeto, pagina)))
                or (getattr(pagina, "tamanho_folha_cm", None) is None
                    and conteudo_mexido(projeto, pagina))):
            achadas.append(pagina)
    return achadas


# --- o automatico por pagina, no livro inteiro (etapa 3 da obra) -------------

def tem_automatico_por_pagina(projeto) -> bool:
    """Alguma pagina (nao apagada) tem etapa do Automatico ligada so nela
    (ConfigPagina.automatico)? Para o caminho rapido "so cadernos"
    (modelos.Projeto.so_cadernos), que nao desenha pagina nenhuma."""
    return any(getattr(p, "automatico", None) and not getattr(p, "apagada", False)
               for p in getattr(projeto, "paginas", []))


def algum_corta_sozinho(projeto) -> bool:
    """O corte automatico vale em alguma pagina (no livro todo, ou so em
    algumas)? Para as contas do livro inteiro (o tamanho do livro do corte
    pelo conteudo, item 2.5)."""
    return bool(getattr(projeto, "cortar_bordas", False)) or any(
        no_automatico_da_pagina(p, CORTAR) for p in getattr(projeto, "paginas", []))
