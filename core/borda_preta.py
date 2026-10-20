"""A página dentro da borda preta do scanner: o corte que o programa sugere
(item 2.13 da Fase 2).

DECISÕES DO SAMUEL QUE ESTE ARQUIVO CUMPRE
    - G7 (05/10/2026): "(a) Sim, desligada de fábrica; testar com o Siebmacher
      e os livros que eu indicar". A opção do livro é Projeto.borda_preta
      (False de fábrica: livro novo e livro já começado saem como hoje).
    - "Para revisar", rodada 4 (08/10/2026): "o programa sugere o corte, o
      Kaique aceita", com exceções por página e seletor (a tela).
    - g7-borda-ate-onde (20/10/2026): "O Kaique escolhe por livro: só o preto,
      ou até a moldura" (Projeto.borda_preta_ate). A sugestão da pergunta era
      começar em "até a moldura": é o valor que vem escolhido quando ele liga
      (JEITO_PADRAO).

OS DOIS JEITOS
    - "até a moldura" (ATE_A_MOLDURA): a conta do ScanTailor Advanced v1.2.1,
      sem mudança: a caixa da página dentro da borda preta (PageFinder) e,
      dentro dela, a caixa do que está impresso (ContentBoxFinder), pela DLL
      (core/caixas_scantailor). O corte é o impresso + 1 mm, sem passar da
      página. É o "Vai até a moldura (o que está impresso)" que o Samuel viu.
    - "só o preto" (SO_O_PRETO): conta NOSSA (o ScanTailor só tira faixa preta
      reta que cobre 95% do lado, e no Siebmacher quase não corta): a do
      pesquisador mostrada na pergunta (ramo fase2-geometria-perguntas,
      scripts/passo2_imagens.py, so_o_preto), sem mudança de regra: de cada
      beirada anda para dentro enquanto o MEIO do lado for quase todo escuro
      (mais escuro que 45% do tom do papel) e para na primeira linha clara;
      nunca anda mais que 30% do lado. Não tira nada do livro nem o papel
      vazio; ficam a beirada das outras folhas, a sombra da lombada e a ponta
      preta do canto de folha torta (escrito na pergunta).

COMO ISTO ENTRA NO CORTE (core/pipeline.py)
    O que sai daqui é o LIMITE da página (x0, y0, x1, y1, em pontos): o corte
    não passa dele. Com o item 2.5 ligado junto (Projeto.cortar_pelo_conteudo)
    o corte do conteúdo e o tamanho do livro são feitos DENTRO desse limite.

SEGURO MUDAR: os textos. ARRISCADO: os números da conta "só o preto" (é a
que o Samuel viu); ligar a opção de fábrica (decisão G7).
"""

from __future__ import annotations

import cv2
import numpy as np

SO_O_PRETO = "so_o_preto"
ATE_A_MOLDURA = "ate_a_moldura"
JEITOS = (ATE_A_MOLDURA, SO_O_PRETO)
JEITO_PADRAO = ATE_A_MOLDURA
NOMES = {ATE_A_MOLDURA: "até a moldura (o que está impresso)", SO_O_PRETO: "só o preto"}

# A conta "só o preto" (do pesquisador, 12/10/2026; ver o topo).
ESCURO_DO_PAPEL = 0.45     # mais escuro que isto vezes o tom do papel = fundo do scanner
PARTE_ESCURA = 0.5         # a linha é "preta" se mais da metade do meio do lado for escura
ANDA_NO_MAXIMO = 0.3       # nunca tira mais que 30% de um lado
PASSO = 4                  # olha 4 linhas de cada vez (pula um risco claro de 1 ponto)


def jeito_valido(jeito) -> str:
    """O jeito do livro; valor estranho do arquivo vale o de fábrica."""
    return jeito if jeito in JEITOS else JEITO_PADRAO


def so_o_preto(img: np.ndarray) -> tuple[float, float, float, float]:
    """A página sem a faixa preta de cada lado, em pontos de `img` (cinza ou
    BGR). Conta do pesquisador, sem mudança (ver o topo). Sem preto: a imagem
    inteira."""
    g = (img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)).astype(np.float32)
    alt, larg = g.shape
    papel = float(np.percentile(g[alt // 4: 3 * alt // 4, larg // 4: 3 * larg // 4], 60))
    escuro = g < papel * ESCURO_DO_PAPEL
    meio_x = slice(int(larg * 0.25), int(larg * 0.75))
    meio_y = slice(int(alt * 0.25), int(alt * 0.75))

    def anda(perfil: np.ndarray) -> int:
        i = 0
        limite = int(len(perfil) * ANDA_NO_MAXIMO)
        while i < limite and perfil[i:i + PASSO].mean() > PARTE_ESCURA:
            i += 1
        return i

    x0 = anda(escuro[meio_y, :].mean(axis=0))
    x1 = larg - anda(escuro[meio_y, ::-1].mean(axis=0))
    y0 = anda(escuro[:, meio_x].mean(axis=1))
    y1 = alt - anda(escuro[::-1, meio_x].mean(axis=1))
    return (float(x0), float(y0), float(x1), float(y1))
