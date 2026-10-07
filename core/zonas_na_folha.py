"""Zonas da aba Marcar presas a FOLHA ORIGINAL (decisao D2 do Samuel, 02/10/2026).

Pedido literal: "Sim, pode mudar (com copia de seguranca dos projetos)" - as
zonas passam a ser guardadas em relacao a folha original, como o ScanTailor
faz, para sobreviver a mudancas de corte, angulo, divisao e giro.

O PROBLEMA QUE ISTO RESOLVE
---------------------------
A selecao (core/selecao.py) guarda pontos em FRACAO DA PAGINA JA PREPARADA:
girada de 90 em 90, dividida, cortada e endireitada. Se o corte ou o angulo
mudam depois (a pessoa mexe na aba Bordas ou Endireitar; ou, na Fase 2, o
corte e o endireitar do ScanTailor entram no lugar dos nossos), as mesmas
fracoes caem em outro pedaco da folha: a zona "anda" sozinha.

COMO FICOU (o que muda e o que NAO muda)
----------------------------------------
- NA MEMORIA, nada muda: ConfigPagina.selecao continua em fracao da pagina
  preparada, e e assim que a tela (aba Marcar) e o pipeline (garantir_selecao,
  filtros) recebem as zonas. Ao lado dela, ConfigPagina.geometria_das_zonas
  diz EM QUE preparo da pagina essas fracoes valem (a "geometria": giro de
  90, divisao, corte, angulo e a proporcao da folha). E um dicionario simples,
  feito por geometria_do_desenho.
- QUANDO A PAGINA E DESENHADA (core/pipeline: renderizar_pagina e processar),
  acompanhar() compara a geometria guardada com a de agora:
    * pagina sem geometria guardada (projeto de antes desta mudanca, ou zona
      nova): so anota a de agora. Nada anda - e exatamente o que o programa
      fazia antes (as fracoes valem na pagina de agora);
    * geometria igual: nada;
    * geometria diferente: as zonas sao levadas da geometria antiga para a
      folha original e da folha para a geometria nova. A zona fica sobre o
      MESMO pedaco do papel.
- NO DISCO (modelos.Projeto.para_dicionario / de_dicionario), cada pagina
  com geometria anotada grava:
    "zonas_na_folha":      as zonas em fracao da FOLHA ORIGINAL (a verdade);
    "geometria_das_zonas": a geometria anotada;
    "selecao":             a copia em fracao da pagina, como sempre - so para
                           o programa instalado antigo, que nao conhece os dois
                           campos novos, abrir o projeto sem zona deslocada.
  Ao abrir, "zonas_na_folha" manda: e convertida de volta para a pagina com a
  geometria anotada. Se a conta bate com a copia "selecao" (diferenca menor
  que um bilionesimo), a copia e usada como esta - assim a zona volta
  identica, bit a bit, e o PDF sai igual.
- Projeto antigo (so "selecao", sem os campos novos) abre como sempre; cada
  pagina e convertida da primeira vez que e desenhada, e o projeto.json antigo
  ganha uma copia de seguranca antes da primeira gravacao no formato novo
  (projetos.salvar_estado, copia "projeto.antigo-zonas-na-folha-*.json",
  nunca apagada).
- Desde 05/10/2026 (decisao Z1 (b)), ao abrir o livro uma tarefa de fundo
  converte TODAS as paginas antigas, uma folha por vez
  (core/pipeline.converter_zonas_do_livro, usando paginas_por_converter e
  anotar_se_ainda_antiga, abaixo). A pagina desenhada antes de a tarefa
  chegar nela continua sendo convertida na hora, pelo acompanhar().

FORMAS
------
RETANGULO e ELIPSE sao guardados na folha pelos QUATRO cantos (o retangulo
girado continua retangulo, e a oval dentro dele continua a oval inscrita - a
conta e afim). Voltando para a pagina: se os quatro cantos ficam alinhados com
a pagina, viram de novo os dois pontos de sempre; senao a regiao fica com
quatro pontos, e core/selecao._desenhar desenha o quadrilatero (ou a oval
inscrita nele). POLIGONO e TRACO: cada ponto e levado. A espessura do pincel
e a suavidade (fracao do menor lado da pagina) sao corrigidas pela mudanca de
tamanho da pagina.

A "folha inteira em branco" da aba Marcar (retangulo de PAPEL de (0,0) a
(1,1), ver ui/tela_conferir._folha_em_branco e filtros.FOLHA_INTEIRA_EM_BRANCO)
quer dizer "a pagina toda", qualquer que seja o corte: fica como esta, sem
ser levada (marcada no disco com "pagina_inteira": true).

O QUE E SEGURO E O QUE E ARRISCADO MUDAR
----------------------------------------
Seguro: as tolerancias (TOLERANCIA_*), o numero de pontos da oval desenhada.
Arriscado:
  - a ordem das etapas em _matriz_folha_para_pagina tem de ser a MESMA de
    core/pipeline.preparar_metade (girar 90 -> dividir -> cortar ->
    endireitar). Se o pipeline mudar de ordem (Fase 2: o ScanTailor endireita
    antes de cortar), esta conta muda junto - e os projetos ja gravados
    continuam certos, porque a verdade no disco e a folha;
  - o sentido do angulo e o do OpenCV (core/endireitar.rotacionar:
    getRotationMatrix2D em volta do centro, mesmo tamanho);
  - gravar "zonas_na_folha" sem "geometria_das_zonas" (nao daria para voltar).
"""

from __future__ import annotations

import math
import threading
from typing import Any

import numpy as np

# Duas geometrias sao "a mesma" se o corte, a divisao e o angulo batem ate
# aqui. Os valores vem do mesmo calculo guardado (pipeline._GEOMETRIAS), entao
# na pratica sao iguais bit a bit.
TOLERANCIA_GEOMETRIA = 1e-9

# A proporcao da folha (largura / altura) e medida na imagem desenhada, e o
# arredondamento para pontos muda a quarta casa entre a previa (~110 DPI) e o
# PDF (300 DPI). Abaixo disto nao e mudanca de verdade.
TOLERANCIA_PROPORCAO = 5e-3

# Cantos "alinhados com a pagina" ate aqui (fracao): o retangulo volta a ter
# dois pontos.
TOLERANCIA_ALINHADO = 1e-9

# Pontos da oval desenhada dentro de um quadrilatero (so quando ela foi girada).
PONTOS_DA_OVAL = 96

# A copia "selecao" do disco e usada como esta se a conta da folha bate ate aqui.
TOLERANCIA_COPIA = 1e-9

# O retangulo "pagina inteira" (a folha em branco da aba Marcar).
_PAGINA_INTEIRA = ((0.0, 0.0), (1.0, 1.0))

# Uma so trava para trocar a selecao e a geometria de uma pagina juntas
# (acompanhar) e para fotografar o projeto inteiro antes de gravar
# (modelos.Projeto.para_dicionario). Arriscado: trocar por duas travas.
TRANCA_DAS_ZONAS = threading.Lock()


# ---------------------------------------------------------------------------
# A geometria de um desenho da pagina
# ---------------------------------------------------------------------------

def geometria_do_desenho(proporcao_folha: float, rotacao: int, corte: float | None,
                         metade: str, recorte, angulo: float,
                         sobra=None) -> dict[str, Any]:
    """O preparo da pagina, num dicionario simples (vai para o projeto.json).

    proporcao_folha: largura / altura da folha COMO VEIO do PDF (antes do giro
        de 90), medida na imagem desenhada.
    rotacao: o giro de 90 em 90 (ConfigFolha.rotacao).
    corte: a posicao da divisao em fracao da largura da folha ja girada, ou
        None quando a pagina nao vem de uma folha dividida.
    metade: "inteira", "esquerda" ou "direita".
    recorte: (x, y, largura, altura) em fracao da pagina dividida, ou None
        quando nao corta (o corte que foi MESMO aplicado).
    angulo: o angulo que foi MESMO aplicado, em graus, no sentido do OpenCV
        (0.0 quando nao gira).
    sobra: (esquerda, direita) em fracao da largura da folha girada: o corte
        da sobra do ScanTailor (item 2.1, core.pipeline.faixa_da_sobra), so em
        pagina "inteira"; None quando nao corta. So entra no dicionario quando
        existe: a geometria gravada antes do item 2.1 (sem a chave) e a de
        uma pagina sem sobra sao iguais.
    """
    desenho = {
        "proporcao": float(proporcao_folha),
        "rotacao": int(rotacao) % 360,
        "corte": None if corte is None else float(corte),
        "metade": str(metade),
        "recorte": None if recorte is None else [float(v) for v in recorte],
        "angulo": float(angulo or 0.0),
    }
    if sobra is not None:
        desenho["sobra"] = [float(v) for v in sobra]
    return desenho


def geometria_valida(g: Any) -> bool:
    """Tem tudo o que a conta precisa? (arquivo estranho nao derruba nada)."""
    if not isinstance(g, dict):
        return False
    try:
        if float(g["proporcao"]) <= 0 or int(g["rotacao"]) % 90 != 0:
            return False
        if g["metade"] not in ("inteira", "esquerda", "direita"):
            return False
        if g["metade"] != "inteira" and g.get("corte") is None:
            return False
        if g.get("recorte") is not None:
            x, y, w, h = (float(v) for v in g["recorte"])
            if w <= 0 or h <= 0:
                return False
        if g.get("sobra") is not None:          # item 2.1
            a, b = (float(v) for v in g["sobra"])
            if not 0.0 <= a < b <= 1.0:
                return False
        float(g.get("angulo", 0.0))
    except (KeyError, TypeError, ValueError):
        return False
    return True


def mesma_geometria(a: dict | None, b: dict | None) -> bool:
    """As duas geometrias poem as zonas no mesmo lugar da folha?"""
    if a is None or b is None:
        return a is b
    if int(a["rotacao"]) % 360 != int(b["rotacao"]) % 360 or a["metade"] != b["metade"]:
        return False

    def perto(x, y, tol=TOLERANCIA_GEOMETRIA):
        if x is None or y is None:
            return x is None and y is None
        return abs(float(x) - float(y)) <= tol

    if a["metade"] != "inteira" and not perto(a.get("corte"), b.get("corte")):
        return False
    ra, rb = a.get("recorte"), b.get("recorte")
    if (ra is None) != (rb is None):
        return False
    if ra is not None and not all(perto(x, y) for x, y in zip(ra, rb)):
        return False
    sa, sb = a.get("sobra"), b.get("sobra")     # item 2.1: o corte da sobra
    if (sa is None) != (sb is None):
        return False
    if sa is not None and not all(perto(x, y) for x, y in zip(sa, sb)):
        return False
    if not perto(a.get("angulo", 0.0), b.get("angulo", 0.0)):
        return False
    if abs(float(a.get("angulo", 0.0))) > 0:
        pa, pb = float(a["proporcao"]), float(b["proporcao"])
        if abs(pa - pb) > TOLERANCIA_PROPORCAO * max(pa, pb):
            return False
    return True


# ---------------------------------------------------------------------------
# A conta: folha original <-> pagina preparada
# ---------------------------------------------------------------------------

def _tamanhos(g: dict) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    """(folha, folha girada, pagina final), cada um (largura, altura), na
    unidade "altura da folha como veio = 1"."""
    proporcao = float(g["proporcao"])
    folha = (proporcao, 1.0)
    girada = folha if int(g["rotacao"]) % 180 == 0 else (1.0, proporcao)
    largura, altura = girada
    if g["metade"] != "inteira":
        corte = _corte_efetivo(g)
        largura *= corte if g["metade"] == "esquerda" else (1.0 - corte)
    elif g.get("sobra") is not None:            # item 2.1: o corte da sobra
        a, b = (float(v) for v in g["sobra"])
        largura *= b - a
    if g.get("recorte") is not None:
        _, _, w, h = (float(v) for v in g["recorte"])
        largura *= w
        altura *= h
    return folha, girada, (largura, altura)


def _corte_efetivo(g: dict) -> float:
    """A posicao da divisao como core/dividir.dividir_imagem usa (0,02 a 0,98)."""
    return float(np.clip(float(g["corte"]), 0.02, 0.98))


def _matriz_folha_para_pagina(g: dict) -> np.ndarray:
    """Matriz 3x3 que leva (u, v) em fracao da FOLHA para fracao da PAGINA.

    As etapas na ordem de core/pipeline.preparar_metade: girar 90 (cv2.rotate)
    -> dividir (dividir_imagem; ou, em pagina inteira, o corte da sobra do
    item 2.1, pipeline._cortar_a_sobra) -> cortar (fatiar) -> endireitar
    (rotacionar, em volta do centro, mesmo tamanho). Conta continua (sem o arredondamento
    para pontos inteiros, que muda menos de um ponto).
    """
    m = np.eye(3)
    rotacao = int(g["rotacao"]) % 360
    if rotacao == 90:        # horario: (x, y) -> (H - y, x)
        m = np.array([[0.0, -1.0, 1.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]) @ m
    elif rotacao == 180:
        m = np.array([[-1.0, 0.0, 1.0], [0.0, -1.0, 1.0], [0.0, 0.0, 1.0]]) @ m
    elif rotacao == 270:     # anti-horario: (x, y) -> (y, W - x)
        m = np.array([[0.0, 1.0, 0.0], [-1.0, 0.0, 1.0], [0.0, 0.0, 1.0]]) @ m

    if g["metade"] != "inteira":
        c = _corte_efetivo(g)
        if g["metade"] == "esquerda":
            m = np.array([[1.0 / c, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]) @ m
        else:
            m = np.array([[1.0 / (1.0 - c), 0.0, -c / (1.0 - c)], [0.0, 1.0, 0.0],
                          [0.0, 0.0, 1.0]]) @ m
    elif g.get("sobra") is not None:            # item 2.1: o corte da sobra
        a, b = (float(v) for v in g["sobra"])
        m = np.array([[1.0 / (b - a), 0.0, -a / (b - a)], [0.0, 1.0, 0.0],
                      [0.0, 0.0, 1.0]]) @ m

    if g.get("recorte") is not None:
        x, y, w, h = (float(v) for v in g["recorte"])
        m = np.array([[1.0 / w, 0.0, -x / w], [0.0, 1.0 / h, -y / h], [0.0, 0.0, 1.0]]) @ m

    angulo = float(g.get("angulo", 0.0))
    if angulo:
        largura, altura = _tamanhos(g)[2]
        a = largura / altura                          # proporcao da pagina cortada
        cos, sen = math.cos(math.radians(angulo)), math.sin(math.radians(angulo))
        # em unidades (X = u * a, Y = v), girar em volta do centro como o
        # cv2.getRotationMatrix2D: X' - cx = cos (X - cx) + sen (Y - cy);
        # Y' - cy = -sen (X - cx) + cos (Y - cy)
        escala = np.diag([a, 1.0, 1.0])
        volta = np.diag([1.0 / a, 1.0, 1.0])
        cx, cy = a / 2.0, 0.5
        giro = np.array([[cos, sen, cx - cos * cx - sen * cy],
                         [-sen, cos, cy + sen * cx - cos * cy],
                         [0.0, 0.0, 1.0]])
        m = volta @ giro @ escala @ m
    return m


def _levar(pontos, m: np.ndarray) -> list[tuple[float, float]]:
    if not pontos:
        return []
    p = np.asarray([[float(x), float(y), 1.0] for x, y in pontos]).T
    q = m @ p
    return [(float(q[0, i]), float(q[1, i])) for i in range(q.shape[1])]


def _menor_lado(tamanho: tuple[float, float]) -> float:
    return min(tamanho)


def _cantos(pontos) -> list[tuple[float, float]]:
    """Os quatro cantos de um retangulo dado por dois pontos opostos, na
    ordem (x0,y0) (x1,y0) (x1,y1) (x0,y1): o 1o e o 3o sao os pontos dados."""
    (x0, y0), (x1, y1) = pontos[0], pontos[1]
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _alinhado(cantos) -> bool:
    """Os quatro cantos formam um retangulo alinhado com a pagina?"""
    (a, b, c, d) = cantos
    t = TOLERANCIA_ALINHADO
    deitado = (abs(a[1] - b[1]) <= t and abs(b[0] - c[0]) <= t
               and abs(c[1] - d[1]) <= t and abs(d[0] - a[0]) <= t)
    em_pe = (abs(a[0] - b[0]) <= t and abs(b[1] - c[1]) <= t
             and abs(c[0] - d[0]) <= t and abs(d[1] - a[1]) <= t)
    return deitado or em_pe


def _e_pagina_inteira(regiao: dict) -> bool:
    """O retangulo da "folha em branco" (0,0)-(1,1) da aba Marcar."""
    if regiao.get("forma") != "retangulo":
        return False
    pontos = regiao.get("pontos") or []
    if len(pontos) != 2:
        return False
    return all(abs(float(p[k]) - _PAGINA_INTEIRA[i][k]) <= 1e-12
               for i, p in enumerate(pontos) for k in (0, 1))


def _converter(regioes: list[dict], m: np.ndarray, escala_comprimento: float,
               para_a_folha: bool) -> list[dict]:
    """Leva cada regiao (dicionario de core.selecao.Regiao) pela matriz m.

    escala_comprimento: quanto multiplicar a espessura e a suavidade (fracao
    do menor lado da imagem de chegada / de saida). Devolve dicionarios
    novos; nunca muda os de entrada (o desfazer guarda copias deles).
    """
    saida: list[dict] = []
    for regiao in regioes:
        if not isinstance(regiao, dict):
            continue
        nova = dict(regiao)
        if para_a_folha and _e_pagina_inteira(regiao):
            nova["pagina_inteira"] = True
            nova["pontos"] = [[0.0, 0.0], [1.0, 1.0]]
            saida.append(nova)
            continue
        if not para_a_folha and regiao.get("pagina_inteira"):
            nova.pop("pagina_inteira", None)
            nova["pontos"] = [[0.0, 0.0], [1.0, 1.0]]
            saida.append(nova)
            continue
        nova.pop("pagina_inteira", None)
        pontos = [(float(p[0]), float(p[1])) for p in (regiao.get("pontos") or []) if len(p) >= 2]
        forma = regiao.get("forma")
        if forma in ("retangulo", "elipse"):
            cantos = _cantos(pontos) if len(pontos) == 2 else pontos[:4]
            if len(cantos) != 4:
                continue
            levados = _levar(cantos, m)
            if not para_a_folha and _alinhado(levados):
                levados = [levados[0], levados[2]]
            pontos = levados
        else:
            pontos = _levar(pontos, m)
        nova["pontos"] = [[x, y] for x, y in pontos]
        for campo in ("espessura", "suavidade"):
            if campo in regiao and regiao[campo] is not None:
                nova[campo] = float(regiao[campo]) * escala_comprimento
        saida.append(nova)
    return saida


def pagina_para_folha(regioes: list[dict], g: dict) -> list[dict]:
    """As zonas (fracao da pagina preparada com a geometria g) em fracao da
    FOLHA ORIGINAL. E o que vai para "zonas_na_folha" no projeto.json."""
    m = np.linalg.inv(_matriz_folha_para_pagina(g))
    folha, _, pagina = _tamanhos(g)
    return _converter(regioes, m, _menor_lado(pagina) / _menor_lado(folha), para_a_folha=True)


def folha_para_pagina(regioes: list[dict], g: dict) -> list[dict]:
    """O caminho de volta: zonas na folha original -> fracao da pagina
    preparada com a geometria g."""
    m = _matriz_folha_para_pagina(g)
    folha, _, pagina = _tamanhos(g)
    return _converter(regioes, m, _menor_lado(folha) / _menor_lado(pagina), para_a_folha=False)


def trocar_de_geometria(regioes: list[dict], antes: dict, depois: dict) -> list[dict]:
    """As zonas da pagina preparada com `antes`, na pagina preparada com
    `depois`, sobre o mesmo pedaco da folha."""
    return folha_para_pagina(pagina_para_folha(regioes, antes), depois)


# ---------------------------------------------------------------------------
# Na memoria: acompanhar a geometria de cada desenho
# ---------------------------------------------------------------------------

def acompanhar(pagina, geometria: dict | None) -> bool:
    """Deixa pagina.selecao valendo na pagina desenhada com `geometria`.

    Chamado por core/pipeline logo depois de preparar a pagina (previa e
    PDF), antes de a selecao ser usada. Devolve True se as zonas foram
    levadas para a geometria nova. Ver o docstring do modulo.

    Atribui listas e dicionarios NOVOS (nunca muda os que estao la): a copia
    da pagina feita por dataclasses.replace (pipeline.renderizar_com_filtro)
    e as fotografias do desfazer continuam intactas.
    """
    if geometria is None:
        return False
    with TRANCA_DAS_ZONAS:
        antiga = getattr(pagina, "geometria_das_zonas", None)
        if not geometria_valida(antiga):
            pagina.geometria_das_zonas = dict(geometria)
            return False
        if mesma_geometria(antiga, geometria):
            return False
        if pagina.selecao:
            pagina.selecao = trocar_de_geometria(pagina.selecao, antiga, geometria)
        pagina.geometria_das_zonas = dict(geometria)
        return True


# ---------------------------------------------------------------------------
# O livro inteiro, por tras, ao abrir (decisao Z1 (b) do Samuel, 05/10/2026)
# ---------------------------------------------------------------------------
#
# "O livro inteiro, por tras, ao abrir - ele poderia fazer isso quando abre o
# livro e fica carregando dai né?" (conferencia 9). Converter uma pagina =
# anotar nela o preparo de HOJE (geometria_das_zonas), sem mexer nas zonas:
# e exatamente o que acompanhar() faz da primeira vez que a pagina e
# desenhada. Quem percorre o livro e core/pipeline.converter_zonas_do_livro
# (precisa desenhar a folha para saber o corte e o angulo automaticos);
# aqui ficam so as duas pecas sem desenho.

def paginas_por_converter(projeto) -> list:
    """As paginas que ainda tem zonas no formato antigo: com zonas e sem a
    geometria anotada. Pagina sem zonas nao precisa (a geometria e anotada
    quando ela for desenhada, e no disco ela nao muda nada)."""
    folhas = len(getattr(projeto, "folhas", None) or [])
    return [p for p in (getattr(projeto, "paginas", None) or [])
            if p.selecao and not geometria_valida(getattr(p, "geometria_das_zonas", None))
            and 0 <= int(p.folha) < folhas]


def zonas_valem_no_desenho(pagina, geometria: dict | None) -> bool:
    """As zonas da pagina (pagina.selecao) estao no preparo `geometria`?

    Para quem le as zonas sobre uma imagem preparada FORA do pipeline (o
    "Ajustar o pedaco a figura" da aba Marcar, ui/tela_conferir), sem leva-las
    (so a previa leva, ao desenhar - acompanhar). True quando a geometria
    anotada e a mesma, ou quando nao ha geometria anotada (pagina antiga ou
    nunca desenhada: as fracoes valem na pagina de agora, como sempre).
    False logo depois de um giro, de um corte ou de um angulo novo, ate a
    previa nova chegar (junção do girar ao fase-1, 06/10/2026). Nunca muda
    nada. Arriscado: devolver True com geometrias diferentes (o retangulo
    velho seria medido na pagina nova).
    """
    if geometria is None:
        return True
    antiga = getattr(pagina, "geometria_das_zonas", None)
    if not geometria_valida(antiga):
        return True
    return mesma_geometria(antiga, geometria)


def anotar_se_ainda_antiga(pagina, geometria: dict, ainda_vale=None) -> bool:
    """Anota `geometria` na pagina SO se ela ainda nao tem geometria (a previa
    pode ter chegado antes, no outro fio) e se `ainda_vale()` (o que a
    geometria usou - corte, angulo, divisao - continua igual). Nunca mexe
    nas zonas. Devolve True se anotou.

    Arriscado: anotar por cima de uma geometria ja anotada, ou sem conferir
    `ainda_vale` - se o Kaique mudou o corte no meio, a previa seguinte
    levaria as zonas de um preparo que nunca foi o delas.
    """
    if not geometria_valida(geometria):
        return False
    with TRANCA_DAS_ZONAS:
        if geometria_valida(getattr(pagina, "geometria_das_zonas", None)):
            return False
        if ainda_vale is not None and not ainda_vale():
            return False
        pagina.geometria_das_zonas = dict(geometria)
        return True


# ---------------------------------------------------------------------------
# No disco: o que modelos.Projeto grava e le
# ---------------------------------------------------------------------------

CAMPO_NA_FOLHA = "zonas_na_folha"


def para_o_disco(dados_da_pagina: dict) -> dict:
    """Acrescenta "zonas_na_folha" ao dicionario de uma pagina (o de
    dataclasses.asdict), quando ela tem zonas e geometria anotada. A copia em
    fracao da pagina ("selecao") fica, para o programa antigo."""
    g = dados_da_pagina.get("geometria_das_zonas")
    selecao = dados_da_pagina.get("selecao") or []
    if selecao and geometria_valida(g):
        dados_da_pagina[CAMPO_NA_FOLHA] = pagina_para_folha(selecao, g)
    return dados_da_pagina


def do_disco(dados_da_pagina: dict) -> dict:
    """O caminho de volta, antes de virar ConfigPagina: "zonas_na_folha" com
    "geometria_das_zonas" vira "selecao" em fracao da pagina. Pagina antiga
    (sem os campos) passa como esta, sem geometria. Nunca levanta: campo
    estranho e ignorado e vale a copia "selecao"."""
    zonas = dados_da_pagina.pop(CAMPO_NA_FOLHA, None)
    g = dados_da_pagina.get("geometria_das_zonas")
    if g is not None and not geometria_valida(g):
        dados_da_pagina["geometria_das_zonas"] = None
        return dados_da_pagina
    if not isinstance(zonas, list) or g is None:
        return dados_da_pagina
    try:
        calculada = folha_para_pagina(zonas, g)
    except Exception:  # noqa: BLE001 - zona estranha nao derruba o projeto
        return dados_da_pagina
    copia = dados_da_pagina.get("selecao")
    dados_da_pagina["selecao"] = copia if _iguais(copia, calculada) else calculada
    return dados_da_pagina


def _iguais(copia: Any, calculada: list[dict]) -> bool:
    """A copia em fracao da pagina bate com a conta feita a partir da folha?"""
    if not isinstance(copia, list) or len(copia) != len(calculada):
        return False
    for a, b in zip(copia, calculada):
        if not isinstance(a, dict):
            return False
        if a.get("forma") != b.get("forma") or a.get("tipo") != b.get("tipo") \
                or a.get("operacao") != b.get("operacao") or a.get("filtro", "") != b.get("filtro", ""):
            return False
        pa, pb = a.get("pontos") or [], b.get("pontos") or []
        if len(pa) != len(pb):
            return False
        for p, q in zip(pa, pb):
            if abs(float(p[0]) - q[0]) > TOLERANCIA_COPIA or abs(float(p[1]) - q[1]) > TOLERANCIA_COPIA:
                return False
        for campo in ("espessura", "suavidade"):
            if campo in a and abs(float(a[campo]) - float(b.get(campo, a[campo]))) > TOLERANCIA_COPIA:
                return False
    return True


def tem_formato_novo(dados_do_projeto: Any) -> bool:
    """O projeto.json (ja lido) tem alguma pagina com zonas na folha?"""
    if not isinstance(dados_do_projeto, dict):
        return False
    return any(isinstance(p, dict) and p.get(CAMPO_NA_FOLHA)
               for p in dados_do_projeto.get("paginas") or [])


def tem_zonas_no_formato_antigo(dados_do_projeto: Any) -> bool:
    """O projeto.json (ja lido) tem zonas so em fracao da pagina (formato de
    antes de 05/10/2026)? E o que pede copia de seguranca antes de regravar."""
    if not isinstance(dados_do_projeto, dict):
        return False
    return any(isinstance(p, dict) and p.get("selecao") and not p.get(CAMPO_NA_FOLHA)
               for p in dados_do_projeto.get("paginas") or [])
