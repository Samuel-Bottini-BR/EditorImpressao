"""A regua da SELECAO: mede o detector de regioes em numeros, nao no olho.

Roda sobre paginas guardadas do acervo e grava relatorios/selecao.md, .html e
.pdf.

    .venv\\Scripts\\python.exe avaliar_selecao.py

## Por que esta regua existe

Ate aqui a selecao era julgada abrindo as imagens. Isso pega o defeito gritante
e deixa passar o resto: no dia 05/08/2026 o detector marcou como gravura de
ponta a ponta uma partitura manuscrita CHEIA de texto, e ninguem viu por dois
dias - a pagina 126 do Graduale.

Olhar continua obrigatorio (ver a skill conferir-testes-visuais). O que esta
regua acrescenta e o que o olho nao faz: medir as mesmas paginas em toda rodada,
sempre do mesmo jeito, e reprovar sozinha.

## Como a industria mede isto

As nossas tres categorias sao, uma a uma, as tres camadas do modelo MRC da
ITU T.44 - o mesmo que o Acrobat usa para comprimir PDF escaneado:

    letra   -> mask layer      (binaria: onde ha tinta de texto)
    gravura -> foreground/background de tom continuo
    papel   -> background liso

E a medida consagrada para segmentacao de layout e a Intersecao sobre Uniao
(IoU) por classe, calculada pagina a pagina e depois promediada - foi assim que
a competicao ICDAR 2017 avaliou o DIVA-HisDB, 150 paginas de manuscritos
medievais anotadas pixel a pixel.

IoU pixel a pixel exige gabarito pixel a pixel, que nao temos e daria semanas
para desenhar. O que da para afirmar sem desenhar nada, e que ja pega todos os
defeitos conhecidos, e o que esta regua cobra:

  - o que a pagina E, no todo: so texto, so desenho, capa, ou os dois juntos;
  - o que uma FAIXA da pagina tem de ser: o titulo impresso do Pesel tem de ser
    letra, a legenda do Siebmacher tem de ser letra;
  - o que NAO pode aparecer: respingo de gravura solto por cima da caligrafia.

Cada expectativa e uma frase que uma pessoa olhando a pagina assinaria. Nenhuma
foi escrita a partir do que o programa devolve - esse foi o erro de 30/07, que
esta contado na skill.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import relatorio  # noqa: E402
from core.detectar_regioes import detectar  # noqa: E402
from core.selecao import GRAVURA, LETRA  # noqa: E402

PASTA_RELATORIOS = RAIZ / "relatorios"

# --- o que se cobra de cada tipo de pagina ----------------------------------
#
# Os limites sao folgados de proposito: a regua tem de pegar estrago, nao
# variacao. "So texto" nao exige gravura zero - uma inicial rubricada pode e
# deve sair como gravura; exige que a pagina nao vire um bloco vermelho.

GRAVURA_MAXIMA_EM_TEXTO = 0.15     # acima disso a pagina de texto virou desenho
LETRA_MINIMA_EM_TEXTO = 0.03       # abaixo disso o texto nao foi marcado
GRAVURA_MINIMA_EM_DESENHO = 0.60   # uma estampa de pagina inteira e vermelha
LETRA_MAXIMA_EM_DESENHO = 0.20     # legenda cabe; corpo de texto nao
COBERTURA_MINIMA_DA_FAIXA = 0.30   # quanto da faixa tem de estar marcado

# Capa TEM de sair marcada como gravura, e esta e a correcao de uma regra
# errada do proprio projeto. O relatorio de 03/08/2026 mandava o contrario -
# "pagina sem conteudo (capa, folha de guarda) nao pode ter marcacao nenhuma" -
# e escrevi essa regra aqui tambem, sem testar o que ela custa.
#
# Custa a capa. Sem marcacao, a selecao fica vazia e o Preto e branco binariza a
# folha inteira: medido e fotografado, a capa de pergaminho do Boecio sai uma
# folha BRANCA, com so a etiqueta da biblioteca sobrando. A do Marial, que o
# detector marca como gravura, sai inteira. Ver relatorios/selecao/ - a amostra
# esta la ao lado deste relatorio.
GRAVURA_MINIMA_EM_CAPA = 0.60

# E o contrario vale para a folha de guarda EM BRANCO, que e papel e nao
# objeto: marcada como gravura ela para de ir a branco. Medido na folha 446
# da Rhetorica: sem marcacao o Preto e branco leva o fundo de 202 para 255;
# marcada como gravura, ele para em 210. O Kaique pediu papel branco.
MARCACAO_MAXIMA_EM_FOLHA_NUA = 0.05


@dataclass
class Caso:
    """Uma pagina do acervo e o que uma pessoa diria olhando para ela."""

    arquivo: str
    livro: str
    pagina: int
    o_que_e: str          # descricao em portugues, escrita OLHANDO a pagina
    tipo: str             # texto | desenho | capa | texto_e_desenho
    faixas_de_letra: list[tuple[float, float, float, float]] = field(default_factory=list)
    observacao: str = ""


def _fracao(selecao, altura: int, largura: int, tipo: str) -> float:
    """Que fracao da pagina inteira esta marcada com este tipo (0.0 a 1.0)."""
    return float(selecao.mascara(altura, largura, tipo).mean())


def _cobertura_da_faixa(selecao, altura: int, largura: int, tipo: str,
                        faixa: tuple[float, float, float, float]) -> float:
    """Que fracao de uma faixa da pagina esta marcada com este tipo.

    A faixa vem em fracoes (x0, y0, x1, y1), como a propria selecao guarda.
    """
    mascara = selecao.mascara(altura, largura, tipo)
    x0 = int(faixa[0] * largura); x1 = int(faixa[2] * largura)
    y0 = int(faixa[1] * altura); y1 = int(faixa[3] * altura)
    pedaco = mascara[max(0, y0):max(1, y1), max(0, x0):max(1, x1)]
    return float(pedaco.mean()) if pedaco.size else 0.0


def _respingos(selecao, altura: int, largura: int) -> int:
    """Quantas manchinhas de gravura soltas ha, longe de qualquer gravura seria.

    E a queixa do Palatino: pontos vermelhos espalhados por cima da caligrafia.
    Conta componentes menores que meio por cento da pagina.
    """
    mascara = (selecao.mascara(altura, largura, GRAVURA) > 0).astype(np.uint8)
    if not mascara.any():
        return 0
    num, _rot, stats, _c = cv2.connectedComponentsWithStats(mascara, connectivity=8)
    limite = 0.005 * altura * largura
    return sum(1 for i in range(1, num) if stats[i, cv2.CC_STAT_AREA] < limite)


def julgar(caso: Caso, gravura: float, letra: float, respingos: int,
           faixas: list[float]) -> list[str]:
    """O que esta errado nesta pagina. Lista vazia quer dizer que passou."""
    erros: list[str] = []

    if caso.tipo == "texto":
        if gravura > GRAVURA_MAXIMA_EM_TEXTO:
            erros.append(
                f"pagina de texto marcada como desenho: {gravura:.0%} de gravura")
        if letra < LETRA_MINIMA_EM_TEXTO:
            erros.append(f"o texto nao foi marcado: so {letra:.1%} de letra")
    elif caso.tipo == "desenho":
        if gravura < GRAVURA_MINIMA_EM_DESENHO:
            erros.append(
                f"desenho de pagina inteira nao foi marcado: {gravura:.0%} de gravura")
        if letra > LETRA_MAXIMA_EM_DESENHO:
            erros.append(f"marcou letra demais num desenho: {letra:.0%}")
    elif caso.tipo == "capa":
        if gravura < GRAVURA_MINIMA_EM_CAPA:
            erros.append(
                f"capa desprotegida: so {gravura:.0%} de gravura - o Preto e "
                f"branco vai binarizar e apagar a folha")
    elif caso.tipo == "folha_nua":
        if gravura > MARCACAO_MAXIMA_EM_FOLHA_NUA:
            erros.append(
                f"folha em branco marcada como gravura: {gravura:.0%} - assim "
                f"ela para de ir a branco")
        if letra > MARCACAO_MAXIMA_EM_FOLHA_NUA:
            erros.append(f"folha em branco com {letra:.0%} de letra marcada")
    elif caso.tipo == "texto_e_desenho":
        if gravura < 0.02:
            erros.append("a gravura desta pagina nao foi marcada")
        if letra < LETRA_MINIMA_EM_TEXTO:
            erros.append(f"o texto desta pagina nao foi marcado: {letra:.1%} de letra")

    if respingos > 2:
        erros.append(f"{respingos} manchinhas de gravura soltas pela pagina")

    for faixa, cobertura in zip(caso.faixas_de_letra, faixas):
        if cobertura < COBERTURA_MINIMA_DA_FAIXA:
            erros.append(
                f"texto impresso nao virou letra: so {cobertura:.0%} da faixa "
                f"em y={faixa[1]:.2f}-{faixa[3]:.2f}")
    return erros


def medir(caso: Caso, pasta: Path) -> dict[str, Any]:
    """Roda o detector numa pagina do acervo e julga o resultado contra o `Caso`.

    Devolve um dicionario com {"erro": ...} se a imagem nao existir/nao abrir,
    ou com as medidas (gravura, letra, respingos, faixas, erros) caso contrario.
    """
    caminho = pasta / caso.arquivo
    if not caminho.exists():
        return {"caso": caso, "erro": f"nao achei {caso.arquivo}"}

    img = cv2.imread(str(caminho), cv2.IMREAD_COLOR)
    if img is None:
        return {"caso": caso, "erro": f"nao consegui ler {caso.arquivo}"}

    altura, largura = img.shape[:2]
    selecao = detectar(img)
    gravura = _fracao(selecao, altura, largura, GRAVURA)
    letra = _fracao(selecao, altura, largura, LETRA)
    respingos = _respingos(selecao, altura, largura)
    faixas = [_cobertura_da_faixa(selecao, altura, largura, LETRA, f)
              for f in caso.faixas_de_letra]

    return {
        "caso": caso, "img": img, "selecao": selecao,
        "gravura": gravura, "letra": letra, "respingos": respingos,
        "faixas": faixas, "regioes": len(selecao),
        "erros": julgar(caso, gravura, letra, respingos, faixas),
    }


# --- os casos ---------------------------------------------------------------
#
# Cada linha foi escrita OLHANDO a pagina. A coluna "o que e" e o que eu diria a
# alguem que perguntasse o que ha ali - e e contra isso que o programa e medido,
# nunca contra o que ele devolve.

CASOS = [
    # --- capas, guardas e folhas nuas: nao se marca nada ---
    Caso("Graduale_-_Saeculum_XIV-p1.png", "Graduale", 1,
         "capa de couro vermelho com fechos de metal", "capa"),
    Caso("Graduale_-_Saeculum_XIV-p750.png", "Graduale", 750,
         "foto do corte do livro fechado, visto de lado", "capa"),
    Caso("Sobre_a_Consolacao_da_Filoso-p1.png", "Boecio", 1,
         "capa de pergaminho com a etiqueta RESERVADO 623 da biblioteca", "capa"),
    # Este caso estava classificado como folha de guarda, e nao e: e a CAPA DE
    # TRAS do mesmo pergaminho da p1. Aberta e comparada com ela lado a lado, a
    # cor e o grao do couro sao os mesmos, e as duas trazem a etiqueta octogonal
    # RESERVADO / B. N. L. da biblioteca - na p1 a esquerda, na p50 a direita,
    # como e de esperar do verso. A textura mede 5,05, junto com as outras capas
    # (5,05 a 12,48) e longe das folhas nuas (0,00 a 1,91).
    #
    # A classificacao errada escondia um bug de verdade: com ela, o Preto e
    # branco apagava esta capa e devolvia uma folha branca.
    Caso("Sobre_a_Consolacao_da_Filosofia-p50.png", "Boecio", 50,
         "capa de tras, do mesmo pergaminho da p1, com a etiqueta da biblioteca",
         "capa"),
    Caso("Giovambattista_Palatino-p1.png", "Palatino", 1,
         "capa de madeira com veio, sem letra", "capa"),
    Caso("Giovambattista_Palatino_citt-p132.png", "Palatino", 132,
         "guarda em branco com um carimbo apagado", "folha_nua"),
    Caso("Rhetorica_Christiana_-__Fray-p1.png", "Rhetorica", 1,
         "folha de guarda de pergaminho, em branco", "folha_nua"),
    Caso("Rhetorica_Christiana-p446.png", "Rhetorica", 446,
         "folha em branco, so o creme do papel", "folha_nua"),
    Caso("POINTS_d_ANCIENNES_BRODERIES-p1.png", "Pesel", 1,
         "capa de tecido com o titulo gravado a ouro e um bordado embutido", "capa"),
    Caso("POINTS_d_ANCIENNES_BRODERIES-p92.png", "Pesel", 92,
         "contracapa de tecido com a etiqueta de codigo de barras", "capa"),
    Caso("POINTS_d_ANCIENNES_BRODERIES-p16.png", "Pesel", 16,
         "folha parda sem tinta, com um carimbo pequeno", "folha_nua"),
    Caso("POINTS_d_ANCIENNES_BRODERIES-p46.png", "Pesel", 46,
         "folha parda sem tinta, com um carimbo pequeno", "folha_nua"),
    Caso("Marial_de_sermoens_-_Frei_Ba-p1.png", "Marial", 1,
         "foto da capa de pergaminho, com a lombada escura a esquerda", "capa"),
    Caso("Livro_de_Horas_-_Luis_XIV-p3.png", "Horas", 3,
         "capa de couro verde com fechos dourados", "capa"),
    Caso("Schon_Neues_Modell_Buch_-_Jo-p1.png", "Siebmacher", 1,
         "capa de couro gasta, sem letra", "capa"),
    Caso("Schon_Neues_Modell_Buch_-_Jo-p268.png", "Siebmacher", 268,
         "contracapa de couro gasta, sem letra", "capa"),

    # --- pagina de texto: o texto tem de virar letra, e a folha nao vira desenho ---
    Caso("Graduale_-_Saeculum_XIV-p126.png", "Graduale", 126,
         "partitura manuscrita: texto gotico, pautas vermelhas e neumas pretos",
         "texto",
         observacao="Em 05/08/2026 saia 100% gravura e 0% letra - o erro que a "
                    "regra do projeto cita pelo nome."),
    Caso("Graduale_-_Saeculum_XIV-p376.png", "Graduale", 376,
         "partitura manuscrita com letra gotica ocre e pautas vermelhas", "texto"),
    Caso("Sobre_a_Consolacao_da_Filoso-p33.png", "Boecio", 33,
         "pagina de texto impresso em italico, com mancha do verso", "texto"),
    Caso("Sobre_a_Consolacao_da_Filoso-p17.png", "Boecio", 17,
         "pagina de texto impresso", "texto"),
    Caso("Rhetorica_Christiana_-__Fray-p223.png", "Rhetorica", 223,
         "pagina so de texto, com notas na margem e manchas de papel velho",
         "texto",
         observacao="Ja saiu com 39% da folha em vermelho, tomando mancha de "
                    "papel velho por pintura."),

    # --- desenho de pagina inteira ---
    Caso("Na_escola_de_Jesus_-_Catecis-p199.png", "Catecismo", 199,
         "estampa colorida de pagina inteira: figura sobre fundo azul, sem texto",
         "desenho"),
    Caso("Schon_Neues_Modell_Buch_-_Jo-p45.png", "Siebmacher", 45,
         "prancha de padrao de bordado, com duas legendas impressas miudas",
         "desenho",
         faixas_de_letra=[(0.25, 0.03, 0.85, 0.10), (0.25, 0.54, 0.85, 0.63)],
         observacao="As legendas impressas tem de sair como letra."),
    Caso("Schon_Neues_Modell_Buch_-_Jo-p133.png", "Siebmacher", 133,
         "prancha de padrao de bordado, em tres faixas", "desenho"),

    # --- texto e desenho na mesma pagina ---
    Caso("POINTS_d_ANCIENNES_BRODERIES-p73.png", "Pesel", 73,
         "foto de bordado montado, com titulo impresso no alto e quatro caixas "
         "de legenda no pe", "texto_e_desenho",
         faixas_de_letra=[(0.05, 0.03, 0.95, 0.11), (0.03, 0.85, 0.97, 0.99)],
         observacao="O titulo e a quarta legenda saiam como foto; as outras "
                    "tres saiam como texto - dois criterios na mesma folha."),
    Caso("Rhetorica_Christiana_-__Fray-p112.png", "Rhetorica", 112,
         "xilogravura emoldurada embaixo de um bloco de texto", "texto_e_desenho"),
]


def desenhar(img: np.ndarray, selecao) -> np.ndarray:
    """A pagina com a marcacao por cima: vermelho gravura, azul letra."""
    altura, largura = img.shape[:2]
    saida = img.copy()
    for tipo, cor in ((GRAVURA, (60, 60, 200)), (LETRA, (200, 90, 40))):
        onde = selecao.mascara(altura, largura, tipo) > 0
        if onde.any():
            camada = np.zeros_like(saida)
            camada[onde] = cor
            saida = cv2.addWeighted(saida, 0.62, camada, 0.38, 0)
    return saida


def main(argv: list[str] | None = None) -> int:
    """Mede todos os CASOS, grava relatorios/selecao (md/html/pdf) e as amostras
    marcadas em relatorios/selecao/, e devolve 1 se algum caso reprovou."""
    argv = list(sys.argv[1:] if argv is None else argv)
    pasta = Path(argv[0]) if argv else (RAIZ / "saida-avaliacao" / "paginas")
    destino = PASTA_RELATORIOS / "selecao"
    destino.mkdir(parents=True, exist_ok=True)

    print(f"Paginas: {pasta}")
    resultados = [medir(caso, pasta) for caso in CASOS]

    medidos = [r for r in resultados if "erro" not in r]
    reprovados = [r for r in medidos if r["erros"]]
    faltando = [r for r in resultados if "erro" in r]

    L: list[str] = ["# A regua da selecao", ""]
    L.append("Mede o detector de regioes nas mesmas paginas em toda rodada. Cada")
    L.append("expectativa foi escrita OLHANDO a pagina, nunca a partir do que o")
    L.append("programa devolve.")
    L.append("")
    L.append(f"**{len(medidos) - len(reprovados)} de {len(medidos)} paginas passaram.**")
    if faltando:
        L.append("")
        L.append(f"Faltaram {len(faltando)} paginas na pasta de trabalho.")
    L.append("")

    if reprovados:
        L.append("## O que esta errado")
        L.append("")
        L.append("| Livro | Pagina | O que a pagina e | O que saiu errado |")
        L.append("|---|---|---|---|")
        for r in reprovados:
            c = r["caso"]
            L.append(f"| {c.livro} | {c.pagina} | {c.o_que_e} | "
                     f"{'; '.join(r['erros'])} |")
        L.append("")

    L.append("## Pagina a pagina")
    L.append("")
    L.append("| Livro | Pagina | O que e | Tipo | Gravura | Letra | Respingos | Passou |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in medidos:
        c = r["caso"]
        L.append(f"| {c.livro} | {c.pagina} | {c.o_que_e[:52]} | {c.tipo} | "
                 f"{r['gravura']:.1%} | {r['letra']:.1%} | {r['respingos']} | "
                 f"{'sim' if not r['erros'] else 'NAO'} |")
    L.append("")

    com_historia = [r for r in medidos if r["caso"].observacao]
    if com_historia:
        L.append("## A historia dos casos dificeis")
        L.append("")
        for r in com_historia:
            c = r["caso"]
            L.append(f"- **{c.livro} p{c.pagina}** - {c.observacao}")
        L.append("")

    L.append("## As amostras")
    L.append("")
    L.append("Uma imagem por pagina, com a marcacao por cima: **vermelho e gravura,")
    L.append("azul e letra, sem cor e papel**. Estao na pasta `selecao/` ao lado")
    L.append("deste relatorio, e as erradas tem ERRADO no nome.")

    for r in medidos:
        c = r["caso"]
        marca = "" if not r["erros"] else " - ERRADO"
        cv2.imwrite(str(destino / f"{c.livro}-p{c.pagina}{marca}.png"),
                    desenhar(r["img"], r["selecao"]))

    escritos = relatorio.gravar("\n".join(L), PASTA_RELATORIOS / "selecao",
                                titulo="A regua da selecao")
    print(f"Passaram {len(medidos) - len(reprovados)} de {len(medidos)}.")
    for r in reprovados:
        print(f"  ERRADO  {r['caso'].livro} p{r['caso'].pagina}: "
              f"{'; '.join(r['erros'])}")
    for r in faltando:
        print(f"  faltou  {r['erro']}")
    print(f"Relatorio: {escritos['md']}")
    print(f"Amostras:  {destino}")
    return 1 if reprovados else 0


if __name__ == "__main__":
    raise SystemExit(main())
