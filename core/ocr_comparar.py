"""Comparação automática entre os detectores de texto (OCRs) de UMA página (item 1.3).

O QUE FAZ
    Decisão do Samuel (29/09/2026): "comparação automática entre eles (onde
    discordam, a página vai para 'Para revisar')". De fábrica ficam ligados o
    docTR e o Kraken; o Tesseract pode ser ligado. comparar() recebe os
    resultados dos OCRs ligados (core.ocr_comum.ResultadoOCR; 2 ou 3, em
    qualquer combinação) e devolve uma Comparacao:

      - para_revisar / motivos: se a página vai para "Para revisar" e por quê,
        em português comum (ex.: "O docTR achou texto em 2 lugares onde o
        Kraken não achou: confira se há texto ou mancha.");
      - zonas: onde discordam (caixa em pontos da imagem, quem achou, quem não);
      - mascara / linhas: o texto combinado que o item 1.4 vai usar.

    Com 1 OCR só não há comparação: a máscara é a dele, e a página só vai para
    revisar se o próprio OCR avisou que perdeu linhas.

O QUE É "DISCORDAR" (calibrado nas 22 páginas do 1.3, 29/09/2026)
    1. ÁREA QUE UM ACHA E O OUTRO NÃO. Para cada par de OCRs, o que as linhas
       de um cobrem e as do outro não, com uma folga de TOLERANCIA alturas de
       linha em volta do outro (o docTR desenha retângulos, o Kraken contornos
       colados na letra: a borda nunca coincide). Tiram-se as lascas mais
       finas que ESPESSURA_MINIMA alturas de linha; o que sobra e tem pelo
       menos AREA_MINIMA "quadrados de altura de linha" (um quadrado = a
       altura mediana das linhas ao quadrado, mais ou menos uma letra grande)
       é uma zona de discordância. Uma letra solta a mais ou a menos NÃO manda
       para revisar; uma palavra, uma caixa na gravura ou uma linha inteira, sim.
    2. LINHAS PERDIDAS AVISADAS PELO PRÓPRIO OCR (ResultadoOCR.perdidas; o
       Kraken joga fora as linhas cujo contorno não consegue desenhar, como na
       tabela do Opus Majus 256).
    3. OCR LIGADO QUE NÃO CONSEGUIU LER A PÁGINA (indisponível): não houve
       comparação completa, então a página vai para revisar.
    NÃO contam, de propósito: o número de linhas e a "linha partida em duas".
    Nas 22 páginas eles variam muito em página boa (Horas 27: docTR 38
    linhas, Kraken 74, porque o Kraken separa as colunas do calendário e o
    docTR as junta), então mandariam página boa para revisar sem motivo. São
    medidos e guardados em Comparacao.medidas, para o log e para quem quiser
    olhar.

O TEXTO COMBINADO (para o item 1.4): VOTO POR LINHA
    Uma linha de um OCR entra na máscara se a maioria dos OCRs a confirma:
    com 2 OCRs, os dois; com 3, pelo menos 2. "Confirmar" = as linhas do
    outro cobrem pelo menos METADE da linha (com a mesma folga). A máscara é a
    união das linhas confirmadas, com o contorno de cada OCR (o retângulo do
    docTR e o contorno do Kraken para a mesma linha somam-se).
    Por que não a união simples nem a interseção (medido nas 22 páginas, ver
    relatorios/fase1-1.3-comparar-ocr-2026-09-29/):
      - a união soma os erros dos dois (caixa do docTR na borda do retrato e
        na mancha do verso, "linhas" do Kraken na moldura do Siebmacher);
      - a interseção pixel a pixel corta a letra onde um contorno é mais
        justo que o outro (o docTR não cobre a perna das letras que o Kraken
        cobre), e perde texto;
      - o voto por linha tira as caixas que só um OCR viu (as que caem em
        figura, quase sempre) e guarda a linha inteira quando os dois a veem.
    O que só um viu não entra na máscara, e a página vai para revisar: o
    Samuel confere. A máscara NÃO leva o alargamento de 15% da comparação do
    1.3 (as hastes das letras): isso é do item 1.4.

NADA AQUI DERRUBA O PROGRAMA
    comparar() nunca levanta exceção: se algo der errado, a página vai para
    revisar com o motivo "Não deu para comparar..." e o detalhe vai para o
    log. Não usa Qt, não importa ui/. Uma página por vez: as máscaras são do
    tamanho de UMA página (a comparação trabalha numa cópia reduzida a
    LADO_DE_TRABALHO pontos, ~20 ms; a máscara final é no tamanho da imagem).

O QUE É SEGURO MUDAR
    Os textos dos motivos; NOMES.

O QUE É ARRISCADO MUDAR
    TOLERANCIA, ESPESSURA_MINIMA, AREA_MINIMA, COBERTURA_PARA_CONFIRMAR e
    LADO_DE_TRABALHO: foram calibrados juntos nas 22 páginas do 1.3, e a
    folga entre página boa e página com erro é pequena (a maior zona numa
    página boa: 1,13; a menor numa página com erro: 1,64; o limite é 1,4).
    Mudou um, rode tests/test_ocr_comparar.py e
    relatorios/fase1-1.3-comparar-ocr-2026-09-29/scripts/calibrar.py.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, replace
from typing import Sequence

import cv2
import numpy as np

from core.ocr_comum import LinhaOCR, ResultadoOCR

_log = logging.getLogger(__name__)

TOLERANCIA = 0.35               # folga em volta do outro OCR, em alturas de linha
ESPESSURA_MINIMA = 0.4          # zona mais fina que isso (em alturas de linha) é lasca de borda
AREA_MINIMA = 1.4               # zona menor que isso (em alturas de linha ao quadrado) não conta
COBERTURA_PARA_CONFIRMAR = 0.5  # parte da linha que o outro OCR tem de cobrir para confirmá-la
LADO_DE_TRABALHO = 1600         # a comparação roda numa cópia com o lado maior até isso (pontos)

NOMES = {"doctr": "docTR", "kraken": "Kraken", "tesseract": "Tesseract"}


@dataclass(frozen=True)
class ZonaDiscordante:
    """Um lugar da página onde os OCRs discordam.

    caixa: (x0, y0, x1, y1) em pontos da imagem que os OCRs receberam.
    acharam / nao_acharam: os motores ("doctr", "kraken", "tesseract").
    tamanho: a área da zona em "quadrados de altura de linha".
    """

    caixa: tuple[int, int, int, int]
    acharam: tuple[str, ...]
    nao_acharam: tuple[str, ...]
    tamanho: float


@dataclass(frozen=True)
class Comparacao:
    """O resultado da comparação de UMA página.

    para_revisar: a página vai para "Para revisar".
    motivos: por quê, em português comum (vazio quando concorda).
    zonas: onde discordam (ZonaDiscordante).
    mascara: bool (altura, largura), o texto combinado (voto por linha), ou
        None se nenhum OCR leu a página ou a comparação falhou.
    linhas: as linhas que entraram na máscara, como (motor, LinhaOCR).
    motores: os OCRs que leram a página e entraram na comparação.
    comparou: False quando havia menos de 2 OCRs para comparar.
    medidas: números para o log e a calibração (linhas de cada um, linhas
        partidas, altura de linha, a maior zona...). Não decidem nada fora
        do que está em motivos.
    """

    para_revisar: bool
    motivos: list[str] = field(default_factory=list)
    zonas: list[ZonaDiscordante] = field(default_factory=list)
    mascara: np.ndarray | None = None
    linhas: list[tuple[str, LinhaOCR]] = field(default_factory=list)
    motores: tuple[str, ...] = ()
    comparou: bool = False
    medidas: dict = field(default_factory=dict)

    @property
    def concorda(self) -> bool:
        return not self.para_revisar


def _nome(motor: str) -> str:
    return NOMES.get(motor, motor)


def _lista(nomes: Sequence[str]) -> str:
    """("docTR",) -> "o docTR"; ("docTR", "Kraken") -> "o docTR e o Kraken"."""
    partes = [f"o {n}" for n in nomes]
    return partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " e " + partes[-1]


def comparar(resultados: Sequence[ResultadoOCR]) -> Comparacao:
    """Compara os OCRs ligados numa página. Nunca levanta exceção (ver docstring do módulo).

    resultados: um ResultadoOCR de cada OCR LIGADO nesta página, todos da
        mesma imagem. Passe só os OCRs ligados e instalados: um resultado
        "indisponível" (o OCR falhou nesta página) manda a página para revisar.
    """
    try:
        return _comparar(list(resultados))
    except Exception as erro:   # rede de segurança: nada sai daqui como exceção
        _log.exception("ocr_comparar: erro inesperado")
        return Comparacao(True, ["Não deu para comparar os detectores de texto nesta página: confira a página."],
                          medidas={"erro": f"{type(erro).__name__}: {erro}"})


def _comparar(resultados: list[ResultadoOCR]) -> Comparacao:
    motivos: list[str] = []
    for r in resultados:
        if not r.disponivel:
            motivos.append(f"O {_nome(r.motor)} não conseguiu ler esta página, então não deu para comparar.")
    lidos = [r for r in resultados if r.disponivel]
    # Linha com ponto que não é número (NaN, infinito) ou com menos de 3 pontos
    # não entra (e fica contada nas medidas): nenhum OCR deveria mandar isso.
    invalidas = 0
    limpos = []
    for r in lidos:
        boas = [l for l in r.linhas if _linha_valida(l)]
        invalidas += len(r.linhas) - len(boas)
        limpos.append(r if len(boas) == len(r.linhas) else replace(r, linhas=boas))
    lidos = limpos
    for r in lidos:
        if r.perdidas > 0:
            motivos.append(f"O {_nome(r.motor)} avisou que não conseguiu desenhar {r.perdidas} "
                           f"linha{'s' if r.perdidas > 1 else ''} nesta página: confira se falta texto.")
    motores = tuple(r.motor for r in lidos)
    if not lidos:
        return Comparacao(bool(motivos), motivos, motores=motores)

    largura, altura = max(r.largura for r in lidos), max(r.altura for r in lidos)
    if largura <= 0 or altura <= 0:
        raise ValueError(f"tamanho da imagem desconhecido: {largura} x {altura}")
    # Pontos de cada OCR na imagem de referência (se algum recebeu outra escala).
    pontos = {id(r): (largura / r.largura if r.largura else 1.0, altura / r.altura if r.altura else 1.0)
              for r in lidos}

    def poligono(r: ResultadoOCR, linha: LinhaOCR) -> np.ndarray:
        fx, fy = pontos[id(r)]
        return np.asarray(linha.poligono, np.float64) * (fx, fy)

    alturas = [_altura(poligono(r, l)) for r in lidos for l in r.linhas]
    altura_linha = float(np.median(alturas)) if alturas else 0.0
    medidas: dict = {"linhas": {r.motor: len(r.linhas) for r in lidos}, "altura_linha": altura_linha,
                     "linhas_invalidas": invalidas}

    if len(lidos) == 1:
        r = lidos[0]
        linhas = [(r.motor, l) for l in r.linhas]
        mascara = _desenhar([poligono(r, l) for l in r.linhas], altura, largura, 1.0)
        return Comparacao(bool(motivos), motivos, [], mascara.astype(bool), linhas, motores, False, medidas)

    # ---- a comparação, numa cópia reduzida
    escala = min(1.0, LADO_DE_TRABALHO / max(largura, altura))
    h, w = max(1, int(round(altura * escala))), max(1, int(round(largura * escala)))
    hl = max(altura_linha * escala, 2.0)          # altura de linha na cópia reduzida
    folga = _nucleo(max(1, int(round(TOLERANCIA * hl))))
    abrir = _nucleo(max(1, int(round(ESPESSURA_MINIMA * hl / 2))))

    mascaras = {}
    cheias = {}
    for r in lidos:
        m = _desenhar([poligono(r, l) for l in r.linhas], h, w, escala)
        mascaras[r.motor] = m
        cheias[r.motor] = cv2.dilate(m, folga)

    # 1) zonas que um acha e outro não (todos os pares), juntadas numa só máscara
    disputa = np.zeros((h, w), np.uint8)
    for a in lidos:
        for b in lidos:
            if a is not b:
                so_a = mascaras[a.motor] & (1 - cheias[b.motor])
                disputa |= cv2.morphologyEx(so_a, cv2.MORPH_OPEN, abrir)
    zonas = []
    n, rotulos, estat, _ = cv2.connectedComponentsWithStats(disputa, 8)
    for i in range(1, n):
        tamanho = float(estat[i, cv2.CC_STAT_AREA]) / (hl * hl)
        if tamanho < AREA_MINIMA:
            continue
        zona = rotulos == i
        acharam = tuple(r.motor for r in lidos
                        if np.count_nonzero(mascaras[r.motor][zona]) >= 0.5 * np.count_nonzero(zona))
        nao = tuple(r.motor for r in lidos if r.motor not in acharam)
        x, y, lw, lh = (int(v) for v in estat[i, :4])
        caixa = (int(x / escala), int(y / escala), int(np.ceil((x + lw) / escala)), int(np.ceil((y + lh) / escala)))
        zonas.append(ZonaDiscordante(caixa, acharam, nao, round(tamanho, 2)))
    zonas.sort(key=lambda z: (z.caixa[1], z.caixa[0]))
    medidas["maior_zona"] = max((float(estat[i, cv2.CC_STAT_AREA]) / (hl * hl) for i in range(1, n)), default=0.0)
    motivos.extend(_motivos_das_zonas(zonas))

    # 2) o texto combinado: voto por linha
    votos = len(lidos) // 2 + 1
    confirmadas = []
    for r in lidos:
        for linha in r.linhas:
            pontos_da_linha = poligono(r, linha) * escala
            if len(pontos_da_linha) < 3:
                continue
            outros = sum(1 for o in lidos if o is not r
                         and _cobertura(pontos_da_linha, cheias[o.motor]) >= COBERTURA_PARA_CONFIRMAR)
            if 1 + outros >= votos:
                confirmadas.append((r, linha))
    mascara = _desenhar([poligono(r, l) for r, l in confirmadas], altura, largura, 1.0).astype(bool)
    medidas["linhas_confirmadas"] = {r.motor: sum(1 for o, _ in confirmadas if o is r) for r in lidos}
    medidas["linhas_partidas"] = _linhas_partidas(lidos, mascaras, poligono, h, w, escala)

    return Comparacao(bool(motivos), motivos, zonas, mascara, [(r.motor, l) for r, l in confirmadas],
                      motores, True, medidas)


def _motivos_das_zonas(zonas: list[ZonaDiscordante]) -> list[str]:
    """Uma frase por combinação "quem achou / quem não achou", com a contagem de lugares."""
    grupos: dict[tuple, int] = {}
    for z in zonas:
        grupos[(z.acharam, z.nao_acharam)] = grupos.get((z.acharam, z.nao_acharam), 0) + 1
    frases = []
    for (acharam, nao), quantos in grupos.items():
        onde = "nesta área" if quantos == 1 else f"em {quantos} lugares"
        if acharam and nao:
            verbo = "achou" if len(acharam) == 1 else "acharam"
            quem = _lista([_nome(m) for m in acharam])
            frases.append(f"{quem[0].upper()}{quem[1:]} {verbo} texto {onde} "
                          f"e {_lista([_nome(m) for m in nao])} não: confira se há texto ou mancha.")
        else:
            frases.append(f"Os detectores de texto desenharam as linhas de jeitos diferentes {onde}: "
                          f"confira se há texto ou mancha.")
    return frases


def _linhas_partidas(lidos, mascaras, poligono, h, w, escala) -> dict:
    """Quantas linhas de cada OCR são cobertas, lado a lado, por 2 ou mais linhas de outro.

    Só medida (não decide nada; ver docstring do módulo).
    """
    saida = {}
    for a in lidos:
        for b in lidos:
            if a is b:
                continue
            partidas = 0
            caixas_b = [cv2.boundingRect(np.round(poligono(b, l) * escala).astype(np.int32)) for l in b.linhas]
            for linha in a.linhas:
                x, y, lw, lh = cv2.boundingRect(np.round(poligono(a, linha) * escala).astype(np.int32))
                meio = y + lh / 2
                dentro = [c for c in caixas_b if c[1] <= meio <= c[1] + c[3]
                          and min(x + lw, c[0] + c[2]) - max(x, c[0]) >= 0.5 * c[2]]
                if len(dentro) >= 2:
                    partidas += 1
            saida[f"{a.motor}/{b.motor}"] = partidas
    return saida


def _linha_valida(linha: LinhaOCR) -> bool:
    pontos = np.asarray(linha.poligono)
    return pontos.ndim == 2 and pontos.shape[0] >= 3 and pontos.shape[1] == 2 and bool(np.isfinite(pontos).all())


def _altura(pontos: np.ndarray) -> float:
    """A altura de uma linha: o lado menor do retângulo girado que a envolve."""
    if len(pontos) < 3:
        return 0.0
    (_, _), (a, b), _ = cv2.minAreaRect(np.asarray(pontos, np.float32))
    return float(min(a, b))


def _desenhar(poligonos: list[np.ndarray], h: int, w: int, escala: float) -> np.ndarray:
    """Máscara uint8 (0/1) com a UNIÃO dos polígonos, na escala pedida.

    Um fillPoly por polígono: com vários de uma vez, o OpenCV pode deixar
    buraco onde dois se sobrepõem (arriscado mudar).
    """
    mascara = np.zeros((h, w), np.uint8)
    for p in poligonos:
        if len(p) >= 3:
            cv2.fillPoly(mascara, [np.round(np.asarray(p) * escala).astype(np.int32).reshape(-1, 1, 2)], 1)
    return mascara


def _cobertura(pontos: np.ndarray, outra: np.ndarray) -> float:
    """Quanto da linha (pontos já na escala da máscara) a máscara 'outra' cobre (0 a 1)."""
    inteiros = np.round(pontos).astype(np.int32)
    h, w = outra.shape
    x0, y0 = max(0, int(inteiros[:, 0].min())), max(0, int(inteiros[:, 1].min()))
    x1, y1 = min(w, int(inteiros[:, 0].max()) + 1), min(h, int(inteiros[:, 1].max()) + 1)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    local = np.zeros((y1 - y0, x1 - x0), np.uint8)
    cv2.fillPoly(local, [(inteiros - (x0, y0)).reshape(-1, 1, 2)], 1)
    area = np.count_nonzero(local)
    if area == 0:
        return 0.0
    return np.count_nonzero(local & outra[y0:y1, x0:x1]) / area


def _nucleo(raio: int) -> np.ndarray:
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1))
