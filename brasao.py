"""O brasao do projeto: onde ficam os arquivos e as medidas do desenho.

Decisoes do Samuel de 17/11/2026:
- D-744: "pode fazer um motion dela girando em 3d sem mudar nada no brasão,
  tem que continuar exactamente igual só com o movimento enquanto carrega o
  programa e pode mudar o icone do programa também para esse brasão."
- D-745: da a volta inteira, como uma moeda girando; de costas aparece de
  frente outra vez, sem espelhar; sem fundo e sem quadro.
- D-746: o icone e o brasao INTEIRO em todos os tamanhos, desenhado direto do
  vetor em cada tamanho (nunca uma imagem diminuida).
- D-747: "brasão aprovado", como na pagina de exemplo
  (D:\\programas\\EditorImpressao-arquivos\\brasao-previas-17-11\\exemplo-brasao.html):
  uma volta a cada 2,5 s.

Este arquivo e o LUGAR SO dessas medidas (CLAUDE.md 11.12): o gerar_brasao.py
(que desenha os arquivos a partir do vetor), a tela de carregamento
(ui/brasao_girando.py, ui/tela_de_carregamento.py), o main.py (icone da
janela) e o empacotar.py (icone do .exe e do instalador) leem daqui.
Nao importa nada pesado (nem Qt, nem PyMuPDF): o main.py o usa antes dos
imports pesados.

O que e arriscado mudar: CAIXA_DO_BRASAO e MARGEM_PT sao os numeros da pagina
de exemplo aprovada (mudar = outro corte do desenho, que ele nao aprovou);
SEGUNDOS_POR_VOLTA, LARGURA_DO_GIRO e PERSPECTIVA sao os da pagina (CSS
"animation: 2.5s linear", ".cena{width:200px; perspective:900px}").
Depois de mudar qualquer um, rode o gerar_brasao.py de novo.
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# O desenho original (copia sem acento de "C:\Users\fotog\Desktop\Brasão 1.ai").
# Fica FORA de recursos/ de proposito: recursos/ vai inteiro para dentro do
# programa empacotado (empacotar.comando_do_pyinstaller), e o .ai nao precisa ir.
ORIGINAL = RAIZ / "arte" / "brasao" / "brasao.ai"

# O que o gerar_brasao.py desenha e o programa usa (vai no git e no pacote).
PASTA = RAIZ / "recursos" / "brasao"
ICONE = PASTA / "brasao.ico"

# Onde o brasao esta na pagina do .ai, em pontos (x0, y0, x1, y1): a caixa do
# desenho (achada pela parte nao transparente) e a margem em volta. Os mesmos
# numeros do script que fez a pagina de exemplo aprovada (D-747).
CAIXA_DO_BRASAO = (293.80, 55.43, 618.56, 494.27)
MARGEM_PT = 2.0

# Icone: todos estes tamanhos, cada um desenhado do vetor (D-746).
TAMANHOS_DO_ICONE = (16, 20, 24, 32, 40, 48, 64, 128, 256)

# Giro (D-745, D-747): na pagina de exemplo o brasao ocupa uma caixa de 200 px
# de largura (".cena{width:200px;height:270px}", imagem "object-fit:contain"),
# com perspectiva de 900 px, e da uma volta a cada 2,5 s, em velocidade igual.
LARGURA_DO_GIRO = 200.0           # pixels de tela (sem a escala do Windows)
PERSPECTIVA = 900.0               # pixels de tela
SEGUNDOS_POR_VOLTA = 2.5

# As escalas de tela do Windows (100%, 125%, ...) para as quais a imagem do
# giro ja vem desenhada do vetor no tamanho certo. Numa escala que nao esta
# aqui, usa-se a mais proxima (giro_para_a_escala).
ESCALAS_DO_GIRO = (1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0)


def caixa_com_margem() -> tuple[float, float, float, float]:
    """A caixa do brasao com a margem transparente em volta (pontos do .ai)."""
    x0, y0, x1, y1 = CAIXA_DO_BRASAO
    return (x0 - MARGEM_PT, y0 - MARGEM_PT, x1 + MARGEM_PT, y1 + MARGEM_PT)


def quadrado_do_icone() -> tuple[float, float, float, float]:
    """O quadrado do icone: centrado no brasao, com o lado da altura dele mais
    a margem. O brasao e mais alto que largo, entao sobra margem transparente
    dos lados (como na pagina de exemplo)."""
    x0, y0, x1, y1 = CAIXA_DO_BRASAO
    lado = (y1 - y0) + 2 * MARGEM_PT
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return (cx - lado / 2, cy - lado / 2, cx + lado / 2, cy + lado / 2)


def escala_do_giro() -> float:
    """Pixels de tela por ponto do .ai no giro, na escala 100% do Windows."""
    x0, _y0, x1, _y1 = caixa_com_margem()
    return LARGURA_DO_GIRO / (x1 - x0)


def tamanho_do_giro() -> tuple[float, float]:
    """Largura e altura do brasao girando, em pixels de tela (escala 100%)."""
    x0, y0, x1, y1 = caixa_com_margem()
    k = escala_do_giro()
    return ((x1 - x0) * k, (y1 - y0) * k)


def arquivo_do_giro(escala: float) -> Path:
    """A imagem do giro desenhada para uma escala da tela (ex.: 1.25 -> giro-125.png)."""
    return PASTA / f"giro-{round(escala * 100)}.png"


def giro_para_a_escala(escala_da_tela: float) -> tuple[float, Path]:
    """A escala ja desenhada mais proxima da escala da tela, e o arquivo dela."""
    melhor = min(ESCALAS_DO_GIRO, key=lambda e: (abs(e - escala_da_tela), -e))
    return melhor, arquivo_do_giro(melhor)
