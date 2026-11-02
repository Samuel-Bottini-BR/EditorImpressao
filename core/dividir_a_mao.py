"""Dividir à mão UMA folha, a qualquer hora (obra de 26/10/2026, etapa 4).

PEDIDO DO SAMUEL (sessão 1 dos testes guiados, 26/10/2026, print s1-10)
    "quando a tela está assim no dividir, é bom para mudar folhas que sairam
    erradas, eu posso entrar ali e mudar a marcação de folhas erradas, mas
    quando eu escolher para começar no automatico e dividir as folhas o livro
    tem que aparecer em uma pagina por vez para mim."
    Plano de 26/10, etapa 4: "dividir esta" sempre ativo (antes ficava cinza
    no livro aberto sem "Dividir" e depois de girar a folha: lista única 3.1,
    o Righetti escaneado de lado). Dividir, não dividir e mover a linha de UMA
    folha mexem só nas páginas DAQUELA folha, sem recomeçar a conferência nem
    perder o que foi feito nas outras (D-489).

O QUE ESTE MÓDULO FAZ (só contas; a tela é ui/tela_conferir.py)
    - campos_para_dividir / campos_para_juntar: o que vai para UMA ação do
      desfazer (historico_acoes): os campos da folha e as páginas novas dela
      (historico_acoes.PREFIXO_PAGINAS_DA_FOLHA). A lista de páginas do livro
      muda só no pedaço daquela folha; as outras páginas são os MESMOS
      objetos (filtro, corte, "está certo" ficam), só renumeradas.
    - "não dividir esta" junta as duas páginas numa só e GUARDA as duas
      (ConfigFolha.metades_guardadas); "dividir esta" de novo, com a linha no
      mesmo lugar, devolve as duas como estavam (era o que o jeito antigo,
      de esconder a metade da direita, garantia; ver o histórico em
      modelos.Projeto.paginas_ativas).
    - campos_para_juntar_todas (D-590, 30/10/2026): o "juntar todas" da
      ferramenta Dividir - o "não dividir esta" em todas as folhas divididas,
      numa ação só do desfazer.
    - metades_da_pagina: a página inteira partida em duas (as duas herdam o
      filtro e os ajustes dela; corte, ângulo e mover, que eram da folha
      inteira, não passam; a marcação feita à mão vai para a metade em que
      está, D-528, etapa 9d). O Automático usa a mesma conta
      (core/automatico._dividir).
    - achar_a_tampa (D-495; D-559 desde a etapa 9b-2): a faixa preta da tampa
      do scanner em volta do livro, na folha GIRADA. Achada quando a pessoa
      divide a folha à mão (ou acerta a linha dela), no "dividir" da grade e,
      desde a etapa 9b-2 (D-559, 27/10/2026, Central `ac-tampa`: "Como eu
      decidi: sumir em todo o livro, e o Kaique escolhe por livro cortar ou
      pintar de branco"), também pelo Automático, em toda folha que ele olha
      (core/automatico.medir). O que fazer com ela é a escolha do livro "O que
      fica fora da página" (Projeto.borda_preta_fazer, D-092: "O Kaique escolhe
      por livro"): "pintar de branco" pinta (a página fica do tamanho de
      sempre); "cortar fora" (o de fábrica) pinta E corta a página na beirada
      da tampa (corte_sem_a_tampa, chamado pelo preparo da página em
      core/pipeline). A regra (abaixo) foi passada nas 2.903 folhas do acervo
      pela etapa 4 (relatorios/obra-etapa4/varrer-tampa-acervo.json): só achou
      fundo preto de scanner, nenhuma moldura impressa.
    - medir_para_dividir: abre a folha (150 DPI, como a análise), gira, acha a
      tampa e a divisão. Uns décimos de segundo.

O QUE É SEGURO MUDAR
    Os números da tampa (com a prova da moldura impressa passando:
    tests/test_decisoes_dividir.py). O que as metades herdam (LIMPAR_AO_PARTIR).

O QUE É ARRISCADO
    - Mudar a lista de páginas sem passar pela ação do desfazer (o Ctrl+Z e o
      Histórico guardam as páginas pela posição: a troca tem de ser desfeita
      antes das ações mais velhas, e é, porque o desfazer é em pilha).
    - Deixar uma folha sem página nenhuma (projetos.motivo_sem_analise
      recomeçaria a conferência ao abrir: D-489).
    - Afrouxar a regra da tampa (ESPESSURA_MM, LINHA_CHEIA, COLUNA_CHEIA):
      desde a D-559 ela roda em todo o livro pelo Automático, e uma moldura
      impressa preta sumiria (D-495). Passar de novo a varredura do acervo
      antes de mudar.
"""

from __future__ import annotations

import copy
import dataclasses
from typing import Any

import numpy as np

from core import etapas as E
from historico_acoes import PREFIXO_PAGINAS_DA_FOLHA
from modelos import (METADE_DIREITA, METADE_ESQUERDA, METADE_INTEIRA, ConfigPagina,
                     paginas_da_lista)

# O que NÃO passa da página inteira para as metades (e das metades para a
# inteira): era medido na folha inteira e não vale numa metade. O filtro, os
# ajustes dele, "tirar do livro" e "deixar em branco" passam. Mesma regra do
# Automático (etapa 3), agora num lugar só.
LIMPAR_AO_PARTIR: dict[str, Any] = dict(
    recorte=None, angulo_manual=None, selecao=[], geometria_das_zonas=None,
    alertas=[], alertas_aceitos=[], revisada=False, conteudo_escala=1.0,
    conteudo_deslocamento=(0.0, 0.0), tamanho_folha_cm=None, gravura_feita_com="",
    marcacao_provisoria=False)


def _limpos(pagina: ConfigPagina) -> dict[str, Any]:
    """Os campos de LIMPAR_AO_PARTIR (listas novas, nunca a mesma) e a marca
    "mexida à mão" só do filtro (o resto era da folha inteira)."""
    limpos = copy.deepcopy(LIMPAR_AO_PARTIR)
    limpos["mexida_a_mao"] = [m for m in (getattr(pagina, "mexida_a_mao", None) or [])
                              if m == E.FILTRO]
    return limpos


def metades_da_pagina(inteira: ConfigPagina, corte: float | None = None) -> list[ConfigPagina]:
    """A página inteira partida em [esquerda, direita] (o índice no livro é
    posto por quem as põe na lista).

    Etapa 9d da obra (D-528, 27/10/2026: "Ao dividir uma folha pela primeira
    vez, as marcações feitas na folha inteira vão para a metade em que
    estão"): com `corte` (a linha da divisão, fração da largura da folha
    girada), as marcações FEITAS À MÃO da página inteira (gravura, letra,
    papel, "pintar de branco", "só neste pedaço", "Deixar a folha em branco")
    vão para a metade onde está o centro de cada uma
    (core/zonas_na_folha.repartir_nas_metades), no mesmo lugar do papel; a
    metade que as recebe fica com a marca "mexida à mão" do Marcar. As que a
    MÁQUINA achou não passam: a metade ganha a marcação provisória
    (marcacao_provisoria), e o desenho do tamanho do PDF procura a gravura de
    novo nela, com a feita à mão por cima (core.pipeline.garantir_selecao) -
    o detector na página inteira de duas páginas não vale numa metade (a
    "capa" da folha inteira cairia numa metade só). Sem `corte` (quem chama
    não sabe a linha), nada passa, como antes.
    Arriscado: passar as marcações da máquina (ver acima) ou sem a geometria
    em que elas valem (cairiam fora do lugar)."""
    from core import zonas_na_folha
    from core.selecao import MAO

    limpos = _limpos(inteira)
    metades = [dataclasses.replace(copy.deepcopy(inteira), metade=metade, **copy.deepcopy(limpos))
               for metade in (METADE_ESQUERDA, METADE_DIREITA)]
    a_mao = [r for r in (getattr(inteira, "selecao", None) or [])
             if isinstance(r, dict) and str(r.get("origem", MAO)) == MAO]
    if corte is None or not a_mao:
        return metades
    esquerda, direita, geometria = zonas_na_folha.repartir_nas_metades(
        a_mao, getattr(inteira, "geometria_das_zonas", None), corte)
    for metade, regioes in zip(metades, (esquerda, direita)):
        if not regioes:
            continue
        metade.selecao = regioes
        metade.geometria_das_zonas = copy.deepcopy(geometria)
        metade.marcacao_provisoria = True
        if E.MARCAR not in metade.mexida_a_mao:
            metade.mexida_a_mao = [*metade.mexida_a_mao, E.MARCAR]
    return metades


def pagina_inteira_das(paginas: list[ConfigPagina]) -> ConfigPagina:
    """As páginas de uma folha juntadas numa só (o "não dividir esta"). Leva o
    filtro e os ajustes da primeira que não foi tirada do livro (a da esquerda
    quase sempre). Só sai do livro se TODAS tinham saído (a folha não pode
    sumir do PDF por a esquerda ter sido tirada: parecer do verificador,
    06/10/2026, a página de rosto do Gradus); só fica em branco se todas
    estavam em branco."""
    base = next((p for p in paginas if not p.apagada), paginas[0])
    inteira = dataclasses.replace(copy.deepcopy(base), metade=METADE_INTEIRA, **_limpos(base))
    inteira.apagada = all(p.apagada for p in paginas)
    inteira.em_branco = all(getattr(p, "em_branco", False) for p in paginas)
    inteira.revisada = True
    return inteira


def paginas_da_folha(projeto, indice_folha: int) -> list[ConfigPagina]:
    """As páginas da folha, na ordem do livro."""
    return [p for p in projeto.paginas if p.folha == indice_folha]


def em_dicionarios(paginas: list[ConfigPagina]) -> list[dict]:
    """As páginas como o projeto.json grava (para a ação do desfazer)."""
    return [_json(dataclasses.asdict(p)) for p in paginas]


def _json(valor):
    """Tupla vira lista (o JSON não tem tupla), em qualquer profundidade."""
    if isinstance(valor, (tuple, list)):
        return [_json(v) for v in valor]
    if isinstance(valor, dict):
        return {k: _json(v) for k, v in valor.items()}
    return copy.deepcopy(valor)


def trocar_as_paginas_da_folha(projeto, indice_folha: int, novas: list[ConfigPagina]) -> None:
    """Põe `novas` no lugar das páginas da folha, na mesma posição do livro, e
    renumera. As páginas das outras folhas são os mesmos objetos. Folha que
    não tinha página (não acontece no programa) entra antes da primeira
    página de uma folha seguinte."""
    for pagina in novas:
        pagina.folha = indice_folha
    lugares = [n for n, p in enumerate(projeto.paginas) if p.folha == indice_folha]
    if lugares:
        lugar = lugares[0]
    else:
        lugar = next((n for n, p in enumerate(projeto.paginas) if p.folha > indice_folha),
                     len(projeto.paginas))
    resto = [p for p in projeto.paginas if p.folha != indice_folha]
    antes = [p for p in resto[:lugar]]
    projeto.paginas = antes + list(novas) + resto[lugar:]
    for n, pagina in enumerate(projeto.paginas):
        pagina.indice = n


def chave_das_paginas(indice_folha: int) -> str:
    """O nome do campo da ação que troca as páginas da folha."""
    return f"{PREFIXO_PAGINAS_DA_FOLHA}{int(indice_folha)}"


# --- os campos da ação ------------------------------------------------------

def campos_para_dividir(projeto, indice_folha: int, posicao: float | None = None,
                        confianca: float = 1.0, tampa: list | None = None) -> dict[str, Any]:
    """O que "dividir esta" muda, para UMA ação do desfazer (alvo "folha").

    - Folha com duas páginas que não estava dividida (o jeito antigo de "não
      dividir", ou o Automático desligado): a da direita volta, como sempre.
    - Folha com uma página e metades guardadas (a pessoa juntou antes) e
      `posicao` None: as duas voltam como estavam, com a linha de antes.
    - Folha com uma página: partida em duas na `posicao` (metades_da_pagina).
    `tampa`: a faixa da tampa do scanner achada agora (D-495), ou None.
    A marca "mexida à mão" é posta pela tela (_registrar), na mesma ação."""
    folha = projeto.folhas[indice_folha]
    pags = paginas_da_folha(projeto, indice_folha)
    campos: dict[str, Any] = {"dividir": True, "revisada": True}
    if len(pags) >= 2:
        novas = [copy.deepcopy(p) for p in pags]
        direita = next((p for p in novas if p.metade == METADE_DIREITA), None)
        if direita is not None and any(not p.apagada for p in novas if p is not direita):
            direita.apagada = False
    else:
        guardadas = getattr(folha, "metades_guardadas", None)
        inteira = pags[0]
        if posicao is None and guardadas and len(guardadas) == 2:
            novas = paginas_da_lista(guardadas)
            for pagina, metade in zip(novas, (METADE_ESQUERDA, METADE_DIREITA)):
                pagina.metade = metade
                # o que a pessoa fez na página juntada vale nas duas
                pagina.apagada = pagina.apagada or inteira.apagada
                pagina.em_branco = pagina.em_branco or getattr(inteira, "em_branco", False)
        else:
            # D-528 (etapa 9d): as marcações à mão da página inteira vão para
            # a metade em que estão, partidas na linha de agora
            corte = folha.posicao_corte if posicao is None else round(float(posicao), 4)
            novas = metades_da_pagina(inteira, corte=corte)
            if posicao is not None:
                campos["posicao_corte"] = round(float(posicao), 4)
                campos["confianca_corte"] = float(confianca)
        campos["e_paisagem"] = True
        campos["metades_guardadas"] = None
    if tampa is not None:
        campos["tampa_do_scanner"] = list(tampa)
    campos[chave_das_paginas(indice_folha)] = em_dicionarios(novas)
    return campos


def campos_para_juntar(projeto, indice_folha: int) -> dict[str, Any]:
    """O que "não dividir esta" muda, para UMA ação do desfazer: as páginas da
    folha viram uma só (pagina_inteira_das) e as duas ficam guardadas na
    folha (ConfigFolha.metades_guardadas) para o "dividir esta" devolver.
    Folha com uma página só: nada muda na lista (só fica conferida)."""
    pags = paginas_da_folha(projeto, indice_folha)
    campos: dict[str, Any] = {"dividir": False, "revisada": True}
    if len(pags) < 2:
        return campos
    campos["metades_guardadas"] = em_dicionarios(pags[:2])
    campos[chave_das_paginas(indice_folha)] = em_dicionarios([pagina_inteira_das(pags)])
    return campos


def campos_para_juntar_todas(projeto) -> tuple[list[int], dict[str, Any]]:
    """D-590 (30/10/2026; Samuel: "se quiser juntar as folhas de novo deveria
    ter uma opção mais clara né" → "pode ser assim"): o botão "juntar todas"
    da ferramenta Dividir. Devolve (as folhas divididas, os campos de UMA ação
    do desfazer, alvo "folha") que juntam todas elas de uma vez: em cada uma, o
    mesmo que "não dividir esta" (campos_para_juntar: a página inteira no
    lugar das duas, as duas guardadas para "dividir esta" devolver). Os campos
    que mudam de folha para folha vão como {indice: valor} (historico_acoes.
    aplicar); as páginas, uma chave por folha (PREFIXO_PAGINAS_DA_FOLHA).
    Nenhuma folha dividida: ([], {}).
    Diferente do "não dividir esta": as folhas NÃO ficam "conferidas"
    (revisada) - a pessoa não olhou cada uma; a D-590 só manda juntar.
    Arriscado: juntar folha de uma página só (campos_para_juntar não muda a
    lista dela) - por isso só entram as de duas páginas ou mais."""
    indices = [f.indice for f in projeto.folhas
               if len(paginas_da_folha(projeto, f.indice)) >= 2]
    if not indices:
        return [], {}
    campos: dict[str, Any] = {"dividir": False, "metades_guardadas": {}}
    for indice in indices:
        uma = campos_para_juntar(projeto, indice)
        campos["metades_guardadas"][str(indice)] = uma["metades_guardadas"]
        chave = chave_das_paginas(indice)
        campos[chave] = uma[chave]
    return indices, campos


def muda_a_lista(campos: dict) -> bool:
    """A ação troca páginas de alguma folha (a tela redesenha a tira e as
    prévias de todas, porque os números das páginas andam)?"""
    return any(str(c).startswith(PREFIXO_PAGINAS_DA_FOLHA) for c in campos)


# --- D-495: a faixa da tampa do scanner ---------------------------------------
#
# Righetti (folha dupla deitada, girada 270 graus): em cima de cada folha há uma
# tira clara (a tampa do scanner), depois uma faixa preta de ~2 cm atravessando
# a folha INTEIRA (as duas páginas e a lombada), e só então o papel; à esquerda,
# o fundo preto do scanner desde a beirada da imagem. O corte de sempre não a
# tira (a tira clara da beirada faz o papel parecer chegar até a beirada; o
# "só o preto" da borda preta anda da beirada e para na tira clara).
# A regra, feita para NÃO pegar moldura impressa (D-495: "não por regra geral"):
#   - em cima e embaixo: pula uma tira clara de até TIRA_CLARA do lado; depois
#     uma faixa NEUTRA bem escura (mais que ESCURO do tom do papel) em pelo
#     menos LINHA_CHEIA da largura da folha INTEIRA (a moldura de uma página
#     de livro aberto não atravessa a lombada nem chega às beiradas), com
#     ESPESSURA_MM ou mais (a linha de moldura impressa tem 0,5 a 3 mm; a
#     faixa da tampa do Righetti, 22 mm);
#   - dos lados: só a faixa que começa na própria beirada da imagem (a moldura
#     impressa tem papel em volta), COLUNA_CHEIA da altura entre as faixas de
#     cima e de baixo, ESPESSURA_MM ou mais (o fundo do Righetti, 46 mm);
#   - nunca mais que ANDA_NO_MAXIMO do lado.
ESCURO = 0.45               # mais escuro que isto vezes o tom do papel (como core/borda_preta)
CROMA_MAXIMO = 40           # neutro: o fundo do scanner é cinza (como core/borda_preta)
TIRA_CLARA = 0.15           # a tira clara da tampa, no máximo 15% do lado
LINHA_CHEIA = 0.97          # em cima/embaixo: a faixa cobre 97% ou mais da largura
COLUNA_CHEIA = 0.85         # dos lados (começando na beirada): 85% ou mais da altura
ESPESSURA_MM = 8.0          # a faixa tem 8 mm ou mais
ANDA_NO_MAXIMO = 0.30       # nunca tira mais que 30% de um lado
BORDA_CLARA = 0.5           # a beira da faixa (antisserrilhado) até cair abaixo disto


def achar_a_tampa(img: np.ndarray, rotacao: int, dpi: float) -> list | None:
    """[rotacao, x0, y0, x1, y1]: a parte da folha GIRADA (`img`, cinza ou BGR,
    a `dpi`) que fica, em fração; None se não há faixa da tampa. Ver o
    comentário acima (D-495)."""
    import cv2

    if img is None or img.ndim not in (2, 3):
        return None
    g = (img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)).astype(np.float32)
    alt, larg = g.shape
    if alt < 40 or larg < 40:
        return None
    papel = float(np.percentile(g[alt // 4: 3 * alt // 4, larg // 4: 3 * larg // 4], 60))
    escuro = g < papel * ESCURO
    if img.ndim == 3 and img.shape[2] >= 3:
        maior = img[:, :, :3].max(axis=2).astype(np.int16)
        menor = img[:, :, :3].min(axis=2).astype(np.int16)
        escuro &= (maior - menor) < CROMA_MAXIMO
    espessura = max(2, int(round(ESPESSURA_MM * float(dpi) / 25.4)))

    linhas = escuro[:, int(larg * 0.02): int(larg * 0.98)].mean(axis=1)
    y0 = _faixa(linhas, espessura, LINHA_CHEIA, com_tira_clara=True)
    y1 = alt - _faixa(linhas[::-1], espessura, LINHA_CHEIA, com_tira_clara=True)
    if y1 - y0 < alt * 0.3:
        return None
    colunas = escuro[y0:y1, :].mean(axis=0)
    x0 = _faixa(colunas, espessura, COLUNA_CHEIA, com_tira_clara=False)
    x1 = larg - _faixa(colunas[::-1], espessura, COLUNA_CHEIA, com_tira_clara=False)
    if x1 - x0 < larg * 0.3:
        return None
    if (x0, y0, x1, y1) == (0, 0, larg, alt):
        return None
    return [int(rotacao) % 360, round(x0 / larg, 6), round(y0 / alt, 6),
            round(x1 / larg, 6), round(y1 / alt, 6)]


def _faixa(perfil: np.ndarray, espessura: int, cheia: float, com_tira_clara: bool) -> int:
    """Quantas linhas (ou colunas), da beirada para dentro, são tampa: a tira
    clara (só se `com_tira_clara`) e a faixa escura com `cheia` ou mais do
    comprimento escuro, por `espessura` pontos ou mais. 0 = nada."""
    n = len(perfil)
    limite = int(n * ANDA_NO_MAXIMO)
    i = 0
    if com_tira_clara:
        while i < int(n * TIRA_CLARA) and perfil[i] < BORDA_CLARA:
            i += 1
        # a beira de cima da faixa (antisserrilhado) entre a tira e a faixa
        while i < limite and BORDA_CLARA <= perfil[i] < cheia:
            i += 1
    comeco = i
    while i < limite and perfil[i] >= cheia:
        i += 1
    if i - comeco < espessura:
        return 0
    while i < limite and perfil[i] >= BORDA_CLARA:
        i += 1
    return i


def area_da_tampa(folha) -> tuple[float, float, float, float] | None:
    """A parte da folha girada que fica (x0, y0, x1, y1, em fração), se a
    tampa foi achada nesta mesma rotação; senão None (girar a folha de novo
    desliga a tampa: ela foi medida em outra posição)."""
    tampa = getattr(folha, "tampa_do_scanner", None)
    if not tampa or len(tampa) != 5:
        return None
    try:
        rotacao, x0, y0, x1, y1 = (float(v) for v in tampa)
    except (TypeError, ValueError):
        return None
    if int(rotacao) % 360 != int(getattr(folha, "rotacao", 0)) % 360:
        return None
    if not (0.0 <= x0 < x1 <= 1.0 and 0.0 <= y0 < y1 <= 1.0):
        return None
    return (x0, y0, x1, y1)


def pintar_a_tampa(img: np.ndarray, folha) -> np.ndarray:
    """A folha girada com a tampa do scanner pintada de branco (D-495); sem
    tampa (o caso de quase todo livro), a mesma imagem, sem cópia."""
    area = area_da_tampa(folha)
    if area is None:
        return img
    from core.borda_preta import pintar_fora

    return pintar_fora(img, area)


def tampa_ja_medida(folha) -> bool:
    """A tampa desta folha já foi procurada nesta rotação? (ConfigFolha.
    tampa_do_scanner = [rotacao] quando nada foi achado; [rotacao, x0, y0, x1,
    y1] quando foi.) Assim mover a linha de novo não abre o PDF de novo."""
    tampa = getattr(folha, "tampa_do_scanner", None)
    try:
        return bool(tampa) and int(tampa[0]) % 360 == int(getattr(folha, "rotacao", 0)) % 360
    except (TypeError, ValueError):
        return False


def _folha_girada(projeto, indice_folha: int) -> np.ndarray:
    """A folha a 150 DPI (como a análise), girada como ela está."""
    from core.endireitar import girar_90
    from core.pdf_io import abrir_pdf, pagina_para_array
    from core.pipeline import DPI_ANALISE

    folha = projeto.folhas[indice_folha]
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img = pagina_para_array(doc, indice_folha, dpi=DPI_ANALISE)
    finally:
        doc.close()
    return girar_90(img, folha.rotacao) if folha.rotacao else img


def medir_a_tampa(projeto, indice_folha: int, img: np.ndarray | None = None) -> list:
    """O que vai para ConfigFolha.tampa_do_scanner quando a pessoa divide (ou
    acerta a linha de) uma folha à mão (D-495): [rotacao, x0, y0, x1, y1] com
    a tampa achada, ou [rotacao] (procurada, nada achado). `img`: a folha já
    girada a 150 DPI (senão abre o PDF). Levanta ErroPDF se o livro não abre."""
    from core.pipeline import DPI_ANALISE

    folha = projeto.folhas[indice_folha]
    if img is None:
        img = _folha_girada(projeto, indice_folha)
    rotacao = int(folha.rotacao) % 360
    return achar_a_tampa(img, rotacao, DPI_ANALISE) or [rotacao]


def medir_para_dividir(projeto, indice_folha: int, jeito: str):
    """(Lombada, tampa) da folha, para o "dividir esta": abre a folha a 150
    DPI (como a análise), gira como ela está, procura a tampa do scanner
    (D-495; ver medir_a_tampa) e, na folha já sem ela, acha a divisão pelo
    `jeito` (forçada: a pessoa mandou dividir). Levanta ErroPDF se o livro não
    abre."""
    from core.borda_preta import pintar_fora
    from core.pipeline import DPI_ANALISE, achar_divisao

    img = _folha_girada(projeto, indice_folha)
    tampa = medir_a_tampa(projeto, indice_folha, img)
    medida = pintar_fora(img, tuple(tampa[1:])) if len(tampa) == 5 else img
    return achar_divisao(medida, jeito, DPI_ANALISE, forcar=True), tampa



# --- D-559 (etapa 9b-2): cortar fora ou pintar de branco, por livro -------------------

def corta_a_tampa(projeto) -> bool:
    """O livro "corta fora" o que fica fora da página (Projeto.borda_preta_fazer,
    a escolha da D-092, "O Kaique escolhe por livro"; "cortar" de fábrica)? Se
    não, "pintar de branco": a tampa só é pintada (pintar_a_tampa)."""
    from core import borda_preta

    if projeto is None:
        return False
    fazer = borda_preta.fazer_valido(getattr(projeto, "borda_preta_fazer", None))
    return fazer == borda_preta.CORTAR_FORA


def area_da_tampa_na_pagina(folha, pagina, projeto=None) -> tuple[float, float, float, float] | None:
    """A parte da PÁGINA (a metade, se a folha é dividida, depois do corte da
    sobra, se houver) que fica dentro da área sem a tampa, (x0, y0, x1, y1) em
    fração da página; None sem tampa nesta rotação, ou quando a página inteira
    fica (a tampa está toda na outra metade). A conta das colunas é a de
    core/dividir.dividir_imagem (a linha da divisão) e a da sobra
    (core/pipeline.faixa_da_sobra)."""
    area = area_da_tampa(folha)
    if area is None:
        return None
    x0, y0, x1, y1 = area
    if folha.dividir and pagina.metade in (METADE_ESQUERDA, METADE_DIREITA):
        corte = float(np.clip(folha.posicao_corte, 0.02, 0.98))
        if pagina.metade == METADE_ESQUERDA:
            a, b = 0.0, corte
        else:
            a, b = corte, 1.0
    else:
        from core.pipeline import faixa_da_sobra

        a, b = faixa_da_sobra(folha, pagina, projeto) or (0.0, 1.0)
    largura = max(1e-6, b - a)
    px0 = min(1.0, max(0.0, (x0 - a) / largura))
    px1 = min(1.0, max(0.0, (x1 - a) / largura))
    if px1 - px0 < 0.05 or y1 - y0 < 0.05:
        return None
    if (px0, y0, px1, y1) == (0.0, 0.0, 1.0, 1.0):
        return None
    return (round(px0, 6), round(y0, 6), round(px1, 6), round(y1, 6))


def corte_sem_a_tampa(folha, pagina, projeto, recorte):
    """D-559, "cortar fora": o corte da página (core.recortar.Recorte em
    tupla: (x, y, largura, altura) em fração dela, ou None = sem corte) sem
    passar da beirada da tampa do scanner. Sem tampa, com o livro em "pintar
    de branco" ou com o corte feito À MÃO nesta página (D-009: o feito à mão
    vale como está; a tampa já sai branca), devolve `recorte` como veio. Sem
    corte, o corte passa a ser a área sem a tampa."""
    if not corta_a_tampa(projeto) or getattr(pagina, "recorte", None) is not None:
        return recorte
    area = area_da_tampa_na_pagina(folha, pagina, projeto)
    if area is None:
        return recorte
    ax0, ay0, ax1, ay1 = area
    if recorte is None:
        return (ax0, ay0, round(ax1 - ax0, 6), round(ay1 - ay0, 6))
    try:
        x, y, w, h = (float(v) for v in recorte)
    except (TypeError, ValueError):
        return recorte
    x0, y0 = max(x, ax0), max(y, ay0)
    x1, y1 = min(x + w, ax1), min(y + h, ay1)
    if x1 - x0 < 0.05 or y1 - y0 < 0.05:
        return recorte                # nada sobraria: o corte fica o de sempre
    return (round(x0, 6), round(y0, 6), round(x1 - x0, 6), round(y1 - y0, 6))


def assinatura_da_tampa(folha, projeto=None) -> tuple:
    """O que da tampa muda a página desenhada (para as chaves das prévias e das
    contas guardadas): a área, e se o livro corta ou pinta. () sem tampa (as
    chaves dos livros sem tampa ficam iguais às de antes)."""
    area = area_da_tampa(folha)
    if area is None:
        return ()
    fazer = ("cortar",) if corta_a_tampa(projeto) else ("pintar",)
    return (("tampa",) + tuple(round(v, 6) for v in area) + fazer,)
