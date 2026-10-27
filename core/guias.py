"""As linhas de apoio para alinhar o conteúdo na folha (item 2.5, g8-guias).

DECISÃO DO SAMUEL (página de escolhas, 13/10/2026), pergunta g8-guias "Linhas
de apoio para alinhar as páginas: quais o programa deve ter?" -> "As duas"
(as automáticas de hoje continuam, e as linhas do Kaique entram como opção),
com o comentário "Mas ele vai poder tirar a automatica a hora que ele quiser."

O QUE SÃO
    - As AUTOMÁTICAS (já existiam, ui/widgets/visualizador.py, "Mover
      conteúdo"): ao arrastar o conteúdo dentro da folha, ele gruda no meio e
      nas beiradas da folha. Agora dá para desligar, no livro
      (Projeto.guias_automaticas, ligado de fábrica = como hoje).
    - As do KAIQUE (como no ScanTailor, page_layout/Guide.h e ImageView.cpp):
      linhas de pé ou deitadas que ele põe onde quiser e que valem no livro
      todo (Projeto.guias). Como no ScanTailor, cada uma é guardada em
      milímetros a partir do MEIO da folha (ImageView::widgetToGuideCs e
      syncGuidesSettings): numa folha do mesmo tamanho ela cai no mesmo lugar
      em todas as páginas. Ao arrastar o conteúdo, a beirada dele mais perto
      da linha gruda nela (no ScanTailor é com dois cliques,
      attachContentToNearestGuide, a beirada mais perta; aqui é o ímã que o
      programa já usa, com a mesma tolerância).

Tudo aqui é conta pura (sem tela): a tela converte e desenha.

SEGURO MUDAR: TOLERANCIA (o quanto perto o ímã pega).
ARRISCADO: o jeito de guardar (mm a partir do meio): projeto salvo com linhas
passaria a pô-las em outro lugar.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

DE_PE = "de_pe"          # linha vertical (ScanTailor: Qt::Vertical)
DEITADA = "deitada"      # linha horizontal (Qt::Horizontal)
ORIENTACOES = (DE_PE, DEITADA)

# 1% da folha: a mesma tolerância das automáticas de antes
# (ui/widgets/visualizador.TOLERANCIA_DA_GUIA).
TOLERANCIA = 0.01

# Os nomes das automáticas (os mesmos de ui/widgets/visualizador.py).
CENTRO_H = "centro_h"
CENTRO_V = "centro_v"
BORDA_ESQUERDA = "borda_esquerda"
BORDA_DIREITA = "borda_direita"
BORDA_CIMA = "borda_cima"
BORDA_BAIXO = "borda_baixo"
PREFIXO_DO_KAIQUE = "kaique:"     # "kaique:3" = a 4a linha do livro


@dataclass(frozen=True)
class Guia:
    """Uma linha do Kaique: de pé ou deitada, a `mm` milímetros do meio da
    folha (positivo = para a direita ou para baixo)."""

    orientacao: str
    mm: float

    def para_salvar(self) -> dict:
        return {"orientacao": self.orientacao, "mm": round(float(self.mm), 3)}


def do_projeto(guardadas) -> list[Guia]:
    """As linhas guardadas no projeto (lista de dicionários), sem as
    estragadas (orientação desconhecida, número que não é número)."""
    linhas = []
    for item in guardadas or []:
        try:
            orientacao, mm = item["orientacao"], float(item["mm"])
        except (KeyError, TypeError, ValueError):
            continue
        if orientacao in ORIENTACOES and mm == mm:            # tira NaN
            linhas.append(Guia(orientacao, mm))
    return linhas


def para_salvar(linhas: Iterable[Guia]) -> list[dict]:
    return [g.para_salvar() for g in linhas]


def em_fracao(guia: Guia, folha_cm: tuple[float, float]) -> float:
    """Onde a linha cai na folha de `folha_cm` (largura, altura), em fração
    (0 = beirada de cima ou da esquerda)."""
    lado_mm = 10.0 * float(folha_cm[0] if guia.orientacao == DE_PE else folha_cm[1])
    return 0.5 + float(guia.mm) / lado_mm if lado_mm > 0 else 0.5


def de_fracao(orientacao: str, fracao: float, folha_cm: tuple[float, float]) -> Guia:
    """A linha que cai na fração `fracao` da folha de `folha_cm`."""
    lado_mm = 10.0 * float(folha_cm[0] if orientacao == DE_PE else folha_cm[1])
    return Guia(orientacao, (float(fracao) - 0.5) * lado_mm)


def _candidatos(inicio: float, tamanho: float, posicoes, automaticas: bool,
                nomes_automaticos: tuple[str, str, str]) -> list[tuple[float, str, float]]:
    """(distância, nome, posição que encaixaria) num eixo: as automáticas
    (meio, começo e fim da folha) se ligadas, e cada linha do Kaique, que
    pega a beirada do conteúdo mais perto dela (começo ou fim)."""
    centro, comeco, fim = nomes_automaticos
    saida = []
    if automaticas:
        saida += [
            (abs((inicio + tamanho / 2) - 0.5), centro, 0.5 - tamanho / 2),
            (abs(inicio), comeco, 0.0),
            (abs(1.0 - (inicio + tamanho)), fim, 1.0 - tamanho),
        ]
    for nome, g in posicoes:
        saida.append((abs(inicio - g), nome, g))                    # a beirada de cá
        saida.append((abs(inicio + tamanho - g), nome, g - tamanho))  # a de lá
    return saida


def _do_eixo(linhas, orientacao: str):
    return [(f"{PREFIXO_DO_KAIQUE}{i}", float(p)) for i, (o, p) in enumerate(linhas) if o == orientacao]


def ativas(conteudo: tuple[float, float, float, float], linhas=(), automaticas: bool = True,
           tolerancia: float = TOLERANCIA) -> list[str]:
    """As linhas que o conteúdo (x, y, largura, altura, em fração da folha) já
    está bem perto de bater, para desenhar. `linhas`: as do Kaique, como
    (orientação, fração) - a tela converte com em_fracao."""
    x, y, w, h = conteudo
    linhas = list(linhas)
    nomes = []
    for d, nome, _p in _candidatos(x, w, _do_eixo(linhas, DE_PE), automaticas,
                                   (CENTRO_H, BORDA_ESQUERDA, BORDA_DIREITA)):
        if d <= tolerancia and nome not in nomes:
            nomes.append(nome)
    for d, nome, _p in _candidatos(y, h, _do_eixo(linhas, DEITADA), automaticas,
                                   (CENTRO_V, BORDA_CIMA, BORDA_BAIXO)):
        if d <= tolerancia and nome not in nomes:
            nomes.append(nome)
    return nomes


def encaixar(conteudo: tuple[float, float, float, float], linhas=(), automaticas: bool = True,
             tolerancia: float = TOLERANCIA) -> tuple[float, float, float, float]:
    """Puxa o conteúdo para a linha mais perto de cada eixo, se estiver dentro
    da tolerância. Nunca muda largura e altura (o ímã posiciona, não
    redimensiona) e nunca põe para fora da folha o conteúdo que cabe nela
    (o maior que a folha só gruda no meio: _pode_encaixar)."""
    x, y, w, h = conteudo
    linhas = list(linhas)
    cx = _candidatos(x, w, _do_eixo(linhas, DE_PE), automaticas,
                     (CENTRO_H, BORDA_ESQUERDA, BORDA_DIREITA))
    cy = _candidatos(y, h, _do_eixo(linhas, DEITADA), automaticas,
                     (CENTRO_V, BORDA_CIMA, BORDA_BAIXO))
    if cx:
        d, nome, nova = min(cx, key=lambda c: c[0])
        if d <= tolerancia and _pode_encaixar(nova, w, nome, CENTRO_H):
            x = nova
    if cy:
        d, nome, nova = min(cy, key=lambda c: c[0])
        if d <= tolerancia and _pode_encaixar(nova, h, nome, CENTRO_V):
            y = nova
    return (x, y, w, h)


def _pode_encaixar(nova: float, tamanho: float, nome: str, centro: str) -> bool:
    """O ímã nunca empurra para fora da folha o conteúdo que cabe nela. O
    conteúdo MAIOR que a folha (aumentado na ferramenta Mover, etapa 5 da
    obra; D-017: o que passa da beirada fica de fora e é avisado) ainda gruda
    no meio, para ficar com a mesma sobra dos dois lados."""
    if tamanho > 1.0:
        return nome == centro
    return 0.0 <= nova <= 1.0 - tamanho


def mais_perto(linhas, orientacao_e_fracao: tuple[str, float] | None = None, *,
               x: float | None = None, y: float | None = None,
               distancia: float = 0.015) -> int | None:
    """O índice da linha do Kaique mais perto do ponto (x, y em fração da
    folha), se estiver a menos de `distancia`; None se nenhuma. Para "Tirar
    esta linha" (ScanTailor: removeGuide(m_guideUnderMouse))."""
    melhor, indice = distancia, None
    for i, (orientacao, p) in enumerate(linhas):
        alvo = x if orientacao == DE_PE else y
        if alvo is None:
            continue
        if abs(float(alvo) - float(p)) <= melhor:
            melhor, indice = abs(float(alvo) - float(p)), i
    return indice
