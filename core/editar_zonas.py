"""Item 2.18: mudar à mão as áreas de gravura (e as outras), e os três jeitos novos.

O QUE FAZ (as decisões do Samuel, literais na ficha memoria/itens/2.18.md)
    - P11b (05/10/2026): "Clicar numa área que o programa já marcou e apagar ou
      pintar de branco: Sim" -> `area_no_ponto`, `sem_a_area`, `pintada_de_branco`.
    - P11 (a) (05/10/2026): "Trazer agora 'Pintar por cima' e 'Tinta com a cor
      original, papel branco', mais copiar, colar e mover zona" -> os tipos
      PINTAR e TINTA_COR (core/selecao.py), `copia`, `movida`.
    - TINTA3 (05/10/2026): "Sim, como opção" -> o tipo TINTA_PRETA ("Tinta
      preta, fundo original").
    - Rodadas 4 e 5 do "Para revisar" (08 e 09/10/2026): mostrar as áreas
      achadas delineadas e mudar o tamanho delas, "Os dois": puxar pelos
      quadradinhos (`redimensionada`, `caixa_da_area`) e o pincel somar/tirar
      (o pincel de sempre, com "tirar", já existe em ui/widgets/editor_selecao).
    - "Mostrar as áreas achadas delineadas": `contornos` (o contorno de cada
      área achada pela máquina, para a tela desenhar em laranja).

    Os três tipos novos valem POR CIMA do filtro da página, dentro da área
    (`aplicar_por_cima`), como as "fill zones" do ScanTailor, que são a última
    coisa da saída dele (OutputGenerator.cpp, applyFillZonesInPlace):
        PINTAR       a área inteira de uma cor (Regiao.cor; vazio = branco);
        TINTA_COR    a tinta com a cor do original, o resto em branco
                     (desde 22/10/2026 com duas opções, resposta do Samuel à
                     pergunta b-8-tinta-com-cor, "As duas: A e B como opções
                     separadas": A "cor como no livro", o de fábrica, e B
                     "cor escurecida", Regiao.tinta_escurecida; ver
                     `escurecida`); e, desde 22/10/2026, o papel da área
                     também em dois jeitos (resposta do Samuel à pergunta
                     tc23-1, "As duas: escolher o papel em cada área"):
                     "papel branco", o de fábrica, e "papel como o resto da
                     página", Regiao.papel_da_pagina (o papel fica como o
                     filtro da página o deixou; só a tinta muda);
        TINTA_PRETA  a tinta em preto, o resto como no original.
    A "tinta" é o preto do Preto e branco da página (o mesmo binarizador, com a
    força da página), medido só no retângulo da área.

TUDO É CÓPIA: nenhuma função muda a Regiao recebida (o desfazer da tela guarda
as antigas). Pontos em fração da página, como em core/selecao.py.

SEGURO MUDAR: DESLOCAMENTO_DA_COPIA, LADO_DA_BUSCA, e (só mudam a opção B)
BRILHO_DA_ESCURECIDA e FORCA_DA_COR_ESCURECIDA. ARRISCADO: a ordem em
`aplicar_por_cima` (PINTAR por último: a pessoa pintou por cima de tudo); e o
caminho da opção A dentro dela, que tem de sair igual ponto por ponto ao de
antes de 22/10/2026 (tests/test_tinta_escurecida.py confere); e o "papel
branco" de fábrica, que também tem de sair igual ao de antes
(tests/test_tinta_papel_da_pagina.py confere).
"""

from __future__ import annotations

import copy

import cv2
import numpy as np

from core.selecao import (AUTOMATICO, MAO, PAPEL, PINTAR, REDE, SOMAR, SUBTRAIR, TINTA_COR,
                          TINTA_PRETA, TIPOS_POR_CIMA, TRACO, Regiao, Selecao)

DESLOCAMENTO_DA_COPIA = 0.03     # a cópia colada aparece um pouco ao lado
LADO_DA_BUSCA = 800              # resolução da conta de "em que área cliquei"

# Opção B da "Tinta com a cor original" ("cor escurecida", 22/10/2026). São os
# números da simulação que o Samuel viu e escolheu (pergunta 8, fotos em
# relatorios/conferir/fase2-novas/pergunta-8/): o brilho (L do Lab) pela
# metade e a cor (a e b do Lab) 25% mais forte. Mudar aqui muda a cor de toda
# área B já marcada nos projetos (não fica gravado na área): conferir com ele.
BRILHO_DA_ESCURECIDA = 0.5
FORCA_DA_COR_ESCURECIDA = 1.25


# --------------------------------------------------------------- escolher

def caixa_da_area(regiao: Regiao) -> tuple[float, float, float, float]:
    """O retângulo (x0, y0, x1, y1) em fração que cerca a área (o traço do
    pincel conta a espessura)."""
    xs = [p[0] for p in regiao.pontos]
    ys = [p[1] for p in regiao.pontos]
    meia = regiao.espessura / 2 if regiao.forma == TRACO else 0.0
    return (max(0.0, min(xs) - meia), max(0.0, min(ys) - meia),
            min(1.0, max(xs) + meia), min(1.0, max(ys) + meia))


def area_no_ponto(selecao: Selecao, ponto: tuple[float, float],
                  proporcao: float = 0.75) -> int | None:
    """O índice da área (de somar) que está no ponto clicado, a de cima
    primeiro (a última desenhada). None se não há área ali. `proporcao` =
    largura/altura da página, para a conta não deformar as formas."""
    altura = LADO_DA_BUSCA
    largura = max(1, int(round(LADO_DA_BUSCA * proporcao)))
    x = min(largura - 1, max(0, int(ponto[0] * largura)))
    y = min(altura - 1, max(0, int(ponto[1] * altura)))
    for indice in range(len(selecao.regioes) - 1, -1, -1):
        regiao = selecao.regioes[indice]
        if regiao.operacao != SOMAR or not regiao.valida():
            continue
        x0, y0, x1, y1 = caixa_da_area(regiao)
        if not (x0 - 0.002 <= ponto[0] <= x1 + 0.002 and y0 - 0.002 <= ponto[1] <= y1 + 0.002):
            continue
        so_ela = Selecao([regiao])
        if so_ela.mascara(altura, largura, regiao.tipo)[y, x]:
            return indice
    return None


# --------------------------------------------------------------- mexer

def _nova(regiao: Regiao, pontos) -> Regiao:
    nova = copy.deepcopy(regiao)
    nova.pontos = [(min(1.0, max(0.0, float(x))), min(1.0, max(0.0, float(y)))) for x, y in pontos]
    return nova


def movida(regiao: Regiao, dx: float, dy: float) -> Regiao:
    """A área andada (dx, dy) em fração; não sai da página (para na beirada)."""
    x0, y0, x1, y1 = caixa_da_area(regiao)
    dx = min(max(dx, -x0), 1.0 - x1)
    dy = min(max(dy, -y0), 1.0 - y1)
    nova = _nova(regiao, [(x + dx, y + dy) for x, y in regiao.pontos])
    if regiao.origem != MAO:
        nova.origem = MAO          # a pessoa mexeu: agora é dela
    return nova


def redimensionada(regiao: Regiao, caixa_nova: tuple[float, float, float, float]) -> Regiao:
    """A área esticada ou encolhida da caixa dela para `caixa_nova` (é o que os
    quadradinhos da tela fazem). Caixa pequena demais (menos de 0,5% da página)
    fica do tamanho mínimo."""
    ax0, ay0, ax1, ay1 = caixa_da_area(regiao)
    bx0, by0, bx1, by1 = caixa_nova
    if bx1 < bx0:
        bx0, bx1 = bx1, bx0
    if by1 < by0:
        by0, by1 = by1, by0
    bx1, by1 = max(bx1, bx0 + 0.005), max(by1, by0 + 0.005)
    escala_x = (bx1 - bx0) / max(ax1 - ax0, 1e-6)
    escala_y = (by1 - by0) / max(ay1 - ay0, 1e-6)
    nova = _nova(regiao, [(bx0 + (x - ax0) * escala_x, by0 + (y - ay0) * escala_y)
                          for x, y in regiao.pontos])
    if regiao.forma == TRACO:
        nova.espessura = regiao.espessura * min(escala_x, escala_y)
    if regiao.origem != MAO:
        nova.origem = MAO
    return nova


def copia(regiao: Regiao, deslocamento: float = DESLOCAMENTO_DA_COPIA) -> Regiao:
    """A cópia para colar: um pouco ao lado, desenhada "à mão"."""
    nova = movida(regiao, deslocamento, deslocamento)
    nova.origem = MAO
    return nova


def pintada_de_branco(regiao: Regiao) -> Regiao:
    """P11b "pintar de branco": a mesma área, agora como papel (vai a branco)."""
    nova = _nova(regiao, regiao.pontos)
    nova.tipo = PAPEL
    nova.origem = MAO
    nova.filtro = ""
    return nova


def sem_a_area(selecao: Selecao, indice: int) -> Selecao:
    """P11b "apagar": a seleção sem a área `indice` (uma cópia)."""
    regioes = [copy.deepcopy(r) for i, r in enumerate(selecao.regioes) if i != indice]
    return Selecao(regioes)


def com_a_area_trocada(selecao: Selecao, indice: int, nova: Regiao) -> Selecao:
    """A seleção com a área `indice` trocada por `nova` (uma cópia)."""
    regioes = [copy.deepcopy(r) for r in selecao.regioes]
    if 0 <= indice < len(regioes):
        regioes[indice] = nova
    return Selecao(regioes)


# --------------------------------------------------------------- ver

def contornos(selecao: Selecao, altura: int, largura: int,
              so_da_maquina: bool = True) -> list[np.ndarray]:
    """O contorno de cada área (em pontos da imagem altura x largura), para a
    tela desenhar delineado. `so_da_maquina`: só as achadas pelo programa
    (automático ou rede), como pediu a rodada 4 ("mostrar as áreas achadas
    delineadas")."""
    linhas: list[np.ndarray] = []
    for regiao in selecao.regioes:
        if regiao.operacao != SOMAR or not regiao.valida():
            continue
        if so_da_maquina and regiao.origem not in (AUTOMATICO, REDE):
            continue
        mascara = Selecao([regiao]).mascara(altura, largura, regiao.tipo).astype(np.uint8)
        achados, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        linhas.extend(achados)
    return linhas


# --------------------------------------------------------------- na imagem

def _cor_em_bgr(cor: str) -> tuple[int, int, int]:
    texto = (cor or "#ffffff").lstrip("#")
    try:
        r, g, b = int(texto[0:2], 16), int(texto[2:4], 16), int(texto[4:6], 16)
    except (ValueError, IndexError):
        return 255, 255, 255
    return b, g, r


def tem_por_cima(selecao) -> bool:
    return bool(selecao is not None and any(
        r.tipo in TIPOS_POR_CIMA for r in getattr(selecao, "regioes", [])))


def aplicar_por_cima(original: np.ndarray, saida: np.ndarray, monocromatica: bool, selecao,
                     forca_preto: int = 50, algoritmo: str = "auto") -> tuple[np.ndarray, bool]:
    """Os três tipos novos, por cima do resultado do filtro. Sem nenhum deles:
    devolve (saida, monocromatica) como veio - o mesmo objeto."""
    if not tem_por_cima(selecao):
        return saida, monocromatica
    altura, largura = saida.shape[:2]
    original = original if original.shape[:2] == (altura, largura) else cv2.resize(
        original, (largura, altura), interpolation=cv2.INTER_AREA)
    resultado = saida if saida.ndim == 3 else cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)
    # `filtrada` é a saída do filtro da página, intocada (o papel do "papel
    # como o resto da página" vem dela); `resultado` é a cópia que se pinta.
    filtrada = resultado
    resultado = resultado.copy()
    original3 = original if original.ndim == 3 else cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)

    for tipo in (TINTA_COR, TINTA_PRETA):
        mascara = selecao.mascara(altura, largura, tipo)
        if not mascara.any():
            continue
        tinta = _tinta_na_area(original, mascara, forca_preto, algoritmo)
        if tipo == TINTA_COR:
            # Opção A ("cor como no livro"), o de fábrica: estas duas linhas são
            # as de antes de 22/10/2026 e valem para TODA a área, mesmo quando
            # há área B (que só é trocada depois, por cima). ARRISCADO mexer:
            # é o que garante o livro já começado sair igual ponto por ponto.
            resultado[mascara & tinta] = original3[mascara & tinta]
            resultado[mascara & ~tinta] = 255
            escura = _mascara_escurecida(selecao, altura, largura) & mascara & tinta
            if escura.any():
                resultado[escura] = escurecida(original3, escura)[escura]
            # "papel como o resto da página" (22/10/2026, tc23-1): o papel
            # (o que não é tinta) da área volta a ser o do filtro da página.
            # Só mexe no que não é tinta, então a tinta A ou B fica como
            # acima. Sem área assim: nada é desenhado (o de fábrica, "papel
            # branco", sai igual ao de antes ponto por ponto).
            papel = _mascara_do_jeito(selecao, altura, largura, "papel_da_pagina")
            if papel.any():
                papel &= mascara & ~tinta
                resultado[papel] = filtrada[papel]
        else:
            resultado[mascara & tinta] = 0
            resultado[mascara & ~tinta] = original3[mascara & ~tinta]

    # PINTAR por último, área por área (cada uma com a cor dela); o "tirar"
    # do pincel desfaz o que veio antes dele, como em toda a marcação
    for i, regiao in enumerate(selecao.regioes):
        if regiao.tipo != PINTAR or regiao.operacao != SOMAR or not regiao.valida():
            continue
        depois = [r for r in selecao.regioes[i + 1:] if r.tipo == PINTAR and r.operacao == SUBTRAIR]
        mascara = Selecao([regiao] + depois).mascara(altura, largura, PINTAR)
        resultado[mascara] = _cor_em_bgr(regiao.cor)
    return resultado, False


def _mascara_escurecida(selecao, altura: int, largura: int) -> np.ndarray:
    """Onde a "Tinta com a cor" é a opção B ("cor escurecida"). Ver
    `_mascara_do_jeito` (a mesma conta, com o campo tinta_escurecida)."""
    return _mascara_do_jeito(selecao, altura, largura, "tinta_escurecida")


def _mascara_do_jeito(selecao, altura: int, largura: int, campo: str) -> np.ndarray:
    """Onde as áreas "Tinta com a cor" têm o `campo` ligado
    ("tinta_escurecida" = cor escurecida; "papel_da_pagina" = papel como o
    resto da página). A última área desenhada manda no pedaço em que duas se
    cruzam (como em toda a marcação); o "tirar" do pincel já está fora da
    máscara do tipo, que a chamadora junta com esta. Sem área com o campo
    ligado: tudo False, sem desenhar nada (caminho de fábrica). ARRISCADO:
    trocar a ordem (a última manda) muda áreas já marcadas nos projetos."""
    marcada = np.zeros((altura, largura), bool)
    regioes = [r for r in getattr(selecao, "regioes", [])
               if r.tipo == TINTA_COR and r.operacao == SOMAR and r.valida()]
    if not any(getattr(r, campo, False) for r in regioes):
        return marcada
    for regiao in regioes:
        dela = Selecao([regiao]).mascara(altura, largura, TINTA_COR)
        marcada[dela] = bool(getattr(regiao, campo, False))
    return marcada


def escurecida(original3: np.ndarray, onde: np.ndarray) -> np.ndarray:
    """A opção B: a cor do original mais escura e um pouco mais forte, no Lab
    (BRILHO_DA_ESCURECIDA no L, FORCA_DA_COR_ESCURECIDA no a e no b). Só o
    retângulo que cerca `onde` é calculado (o resto volta como no original):
    a página inteira em Lab custaria à toa. Vermelho vira vermelho-escuro,
    azul vira azul-marinho, tinta desbotada fica marrom-escura; o branco do
    papel não entra (só a tinta é trocada, na chamadora)."""
    saida = original3.copy()
    ys, xs = np.nonzero(onde)
    if ys.size == 0:
        return saida
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    lab = cv2.cvtColor(np.ascontiguousarray(original3[y0:y1, x0:x1]),
                       cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[..., 0] *= BRILHO_DA_ESCURECIDA
    lab[..., 1:] = (lab[..., 1:] - 128.0) * FORCA_DA_COR_ESCURECIDA + 128.0
    saida[y0:y1, x0:x1] = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    return saida


def _tinta_na_area(original: np.ndarray, mascara: np.ndarray, forca_preto: int,
                   algoritmo: str) -> np.ndarray:
    """Onde há tinta, pelo Preto e branco da página, medido só no retângulo
    que cerca a área (mais rápido, e o papel de fora não muda o limiar)."""
    from core.filtros import filtro_preto_e_branco

    ys, xs = np.nonzero(mascara)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    margem = 16
    y0, x0 = max(0, y0 - margem), max(0, x0 - margem)
    y1, x1 = min(mascara.shape[0], y1 + margem), min(mascara.shape[1], x1 + margem)
    pedaco = np.ascontiguousarray(original[y0:y1, x0:x1])
    binaria = filtro_preto_e_branco(pedaco, forca=forca_preto, despeckle=False, algoritmo=algoritmo)
    tinta = np.zeros(mascara.shape, bool)
    tinta[y0:y1, x0:x1] = binaria < 128
    return tinta
