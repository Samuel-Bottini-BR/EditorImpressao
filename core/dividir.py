"""Deteccao da lombada e divisao da folha em duas paginas.

Muitos escaneamentos trazem duas paginas do livro numa folha so, em paisagem.
A lombada aparece como uma faixa escura vertical no meio - e a sombra do vinco
do livro. E isso que procuramos.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

# A folha so e candidata a dupla se for bem mais larga que alta.
RAZAO_PAISAGEM = 1.2

# A lombada de um livro escaneado inteiro fica sempre perto do meio.
# Procurar fora dessa faixa so acha falso positivo (margem, ilustracao).
FAIXA_BUSCA = (0.35, 0.65)

# Faixa em que consideramos a lombada "bem no meio" (secao 4.3).
FAIXA_CONFIAVEL = (0.40, 0.60)

# Largura do perfil analisado. Reduzir acelera muito e nao perde nada:
# a sombra da lombada tem dezenas de pixels de largura.
LARGURA_ANALISE = 1200

# Suavizacao do perfil, em fracao da largura. Tira o ruido de letra sem
# apagar o vale da lombada.
SUAVIZACAO_FRACAO = 1 / 100

# Peso de cada evidencia no custo combinado (precisam somar 1).
# A ausencia de texto e o sinal mais confiavel: existe em todo livro, com ou
# sem sombra de lombada visivel.
PESO_TINTA = 0.65
PESO_SOMBRA = 0.35

# Quanto o ponto escolhido precisa se destacar da faixa para termos certeza.
DESTAQUE_FORTE = 0.25

# Diferenca de custo abaixo da qual duas colunas sao consideradas empatadas.
EMPATE = 0.02


@dataclass(frozen=True)
class Lombada:
    """Onde cortar e o quanto confiamos nisso."""

    posicao: float      # 0.0 a 1.0, relativo a largura
    confianca: float    # 0.0 a 1.0
    e_paisagem: bool

    @property
    def centralizada(self) -> bool:
        return FAIXA_CONFIAVEL[0] <= self.posicao <= FAIXA_CONFIAVEL[1]


def _suavizar(perfil: np.ndarray) -> np.ndarray:
    """Media movel. Tira o ruido de letra sem apagar o vale da lombada."""
    janela = max(3, int(len(perfil) * SUAVIZACAO_FRACAO))
    if janela % 2 == 0:
        janela += 1
    nucleo = np.ones(janela, dtype=np.float32) / janela
    # 'edge' evita que as pontas do perfil afundem artificialmente
    acolchoado = np.pad(perfil.astype(np.float32), janela // 2, mode="edge")
    return np.convolve(acolchoado, nucleo, mode="valid")


def _perfil_de_intensidade(cinza: np.ndarray) -> np.ndarray:
    """Media de intensidade por coluna. Coluna escura = valor baixo."""
    return _suavizar(cinza.mean(axis=0))


def _perfil_de_tinta(cinza: np.ndarray) -> np.ndarray:
    """Fracao de pixels de TEXTO por coluna.

    O limiar e estrito de proposito: so conta o que e bem mais escuro que o
    papel, ou seja, tinta mesmo. A sombra da lombada e um escurecimento suave e
    fica de fora - e justamente por isso este perfil enxerga a lombada como um
    vazio, mesmo quando ela e escura.
    """
    nivel_papel = float(np.percentile(cinza, 80))
    limiar = max(20.0, nivel_papel * 0.55)
    return _suavizar((cinza < limiar).mean(axis=0))


def _normalizar(v: np.ndarray) -> np.ndarray:
    """Leva o vetor para a faixa 0-1. Vetor constante vira tudo 0.5."""
    lo, hi = float(v.min()), float(v.max())
    if hi - lo < 1e-6:
        return np.full_like(v, 0.5)
    return (v - lo) / (hi - lo)


def detectar_lombada(img: np.ndarray) -> Lombada:
    """Acha a coluna da lombada e diz o quanto confia nessa resposta."""
    altura, largura = img.shape[:2]
    e_paisagem = largura > altura * RAZAO_PAISAGEM

    if not e_paisagem:
        # Folha em retrato: quase certamente e uma pagina so.
        return Lombada(posicao=0.5, confianca=0.0, e_paisagem=False)

    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if largura > LARGURA_ANALISE:
        escala = LARGURA_ANALISE / largura
        cinza = cv2.resize(
            cinza, (LARGURA_ANALISE, max(8, int(altura * escala))), interpolation=cv2.INTER_AREA
        )

    tinta = _perfil_de_tinta(cinza)
    intensidade = _perfil_de_intensidade(cinza)
    n = len(tinta)

    ini, fim = int(n * FAIXA_BUSCA[0]), int(n * FAIXA_BUSCA[1])
    if fim - ini < 3:
        return Lombada(posicao=0.5, confianca=0.0, e_paisagem=True)

    # A lombada e onde as duas evidencias se encontram: nao ha texto ali
    # (e a margem interna das duas paginas) e costuma haver sombra.
    # A falta de texto pesa mais porque funciona tambem em scans limpos, sem
    # sombra nenhuma - foi o caso que derrubou a primeira versao desta funcao,
    # que escolhia uma ilustracao escura no lugar da lombada.
    custo = _normalizar(tinta) * PESO_TINTA + _normalizar(intensidade) * PESO_SOMBRA

    faixa = custo[ini:fim]
    deslocamento = _centro_do_vale(faixa)
    coluna = ini + deslocamento
    posicao = coluna / n

    confianca = _confianca(faixa, deslocamento, posicao)
    return Lombada(posicao=posicao, confianca=confianca, e_paisagem=True)


def _centro_do_vale(faixa: np.ndarray) -> int:
    """Indice do MEIO do vale, e nao da primeira coluna dele.

    Num livro bem escaneado a margem entre as duas paginas e uma faixa larga
    sem tinta nenhuma: dezenas de colunas empatam no custo minimo. Pegar o
    argmin direto cairia na beirada dessa faixa e o corte comeria a margem de
    uma das paginas. Aqui pegamos o centro do trecho empatado.
    """
    minimo = float(faixa.min())
    empate = faixa <= minimo + EMPATE

    # trecho contiguo de empate que contem o argmin
    inicio = fim = int(np.argmin(faixa))
    while inicio > 0 and empate[inicio - 1]:
        inicio -= 1
    while fim < len(faixa) - 1 and empate[fim + 1]:
        fim += 1
    return (inicio + fim) // 2


def _confianca(custo_faixa: np.ndarray, indice: int, posicao: float) -> float:
    """Combina duas evidencias: a escolha se destaca? e esta perto do meio?

    Nenhuma das duas sozinha basta. Um vale fundo mas na borda costuma ser a
    sombra da margem; um vale raso bem no meio costuma ser so o papel.
    """
    # 1. destaque: o quanto o melhor ponto e melhor que a faixa em geral.
    tipico = float(np.median(custo_faixa))
    melhor = float(custo_faixa[indice])
    destaque = tipico - melhor
    nota_destaque = float(np.clip(destaque / DESTAQUE_FORTE, 0.0, 1.0))

    # 2. centralidade: cai suavemente conforme se afasta do meio.
    nota_centro = float(np.clip(1.0 - abs(posicao - 0.5) / 0.15, 0.0, 1.0))

    return float(nota_destaque * 0.6 + nota_centro * 0.4)


def dividir_imagem(img: np.ndarray, posicao: float) -> tuple[np.ndarray, np.ndarray]:
    """Corta a folha na posicao dada. Devolve (esquerda, direita), nessa ordem.

    A ordem importa: numa folha dupla de livro ocidental, a pagina da esquerda
    vem antes da direita.
    """
    largura = img.shape[1]
    corte = int(round(np.clip(posicao, 0.02, 0.98) * largura))
    corte = max(1, min(largura - 1, corte))
    return img[:, :corte].copy(), img[:, corte:].copy()
