"""Rodada das opções do detector de gravuras (item 1.2; pedido da gerente, 30/09/2026).

    .venv\\Scripts\\python.exe rodada_opcoes_gravura.py [PASTA_DE_SAIDA]

O QUE FAZ
    Processa, pelo mesmo caminho do botão "Confirmar e processar"
    (core.pipeline.analisar_projeto + processar, a 300 DPI), cada página
    abaixo em Mágico pro e em Preto e branco, com cada combinação das opções
    do grupo "Gravuras e fotos" (COMBINACOES), mais o detector antigo como
    referência. Para cada página monta UMA folha de comparação
    (folhas\\<página>-<filtro>.jpg): o original e cada combinação lado a
    lado, com o rótulo em português e quanto da página virou gravura; e uma
    folha só com a zona de gravura de cada combinação
    (folhas\\<página>-gravura.jpg). Os resultados em tamanho cheio ficam em
    resultado\\. O relatório (.md, .html, .pdf) é escrito à parte.

AS PÁGINAS
    As que pioraram na ligação do 1.2 (Graduale 222, Horas 13, Horas 26, Opus
    Majus 20) e, para ver que as opções não estragam as boas, Horas 11, Horas
    27, Palatino 9, Palatino 67 e Marial 153 (esta copiada do acervo pelo
    rodada_gravura_1_2.py, em saida_teste\\gabarito_1_2\\). O gabarito\\ e o
    acervo não são alterados.

AS COMBINAÇÕES (9 + o antigo, em vez das 24 possíveis)
    A sensibilidade só vale no retângulo (o ScanTailor não a usa no contorno
    livre): as três sensibilidades entram só no retângulo. "Procurar também
    imagens claras" e "Igualar a luz" entram no livre (a forma de fábrica),
    sozinhas e juntas, e no retângulo a 100.

Não é usado pelo programa. Seguro mudar: tudo.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
os.environ.setdefault("LOCALAPPDATA", str(RAIZ / "saida_teste" / "localappdata_rodada_opcoes"))
Path(os.environ["LOCALAPPDATA"]).mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

PAGINAS = {
    "graduale_p222": RAIZ / "gabarito" / "paginas" / "graduale_p222.pdf",
    "horas_p013": RAIZ / "gabarito" / "paginas" / "horas_p013.pdf",
    "horas_p026": RAIZ / "gabarito" / "paginas" / "horas_p026.pdf",
    "opusmajus_p020": RAIZ / "gabarito" / "paginas" / "opusmajus_p020.pdf",
    "horas_p011": RAIZ / "gabarito" / "paginas" / "horas_p011.pdf",
    "horas_p027": RAIZ / "gabarito" / "paginas" / "horas_p027.pdf",
    "palatino_p009": RAIZ / "gabarito" / "paginas" / "palatino_p009.pdf",
    "palatino_p067": RAIZ / "gabarito" / "paginas" / "palatino_p067.pdf",
    "marial_p153": RAIZ / "saida_teste" / "gabarito_1_2" / "paginas" / "marial_p153.pdf",
}
FILTROS = {"magico_pro": "Mágico pro", "preto_e_branco": "Preto e branco"}

# (chave, rótulo em português, detector, forma, sensibilidade, imagens claras, igualar a luz)
COMBINACOES = [
    ("antigo", "Antes (detector antigo)", "antigo", "livre", 100, False, True),
    ("A", "A. Seguindo o desenho (de fábrica)", "scantailor", "livre", 100, False, True),
    ("B", "B. Desenho + imagens claras", "scantailor", "livre", 100, True, True),
    ("C", "C. Desenho, sem igualar a luz", "scantailor", "livre", 100, False, False),
    ("D", "D. Desenho + claras, sem igualar a luz", "scantailor", "livre", 100, True, False),
    ("E", "E. Tem fotos, sensibilidade 100", "scantailor", "retangular", 100, False, True),
    ("F", "F. Tem fotos, sensibilidade 70", "scantailor", "retangular", 70, False, True),
    ("G", "G. Tem fotos, sensibilidade 40", "scantailor", "retangular", 40, False, True),
    ("H", "H. Tem fotos 100 + imagens claras", "scantailor", "retangular", 100, True, True),
    ("I", "I. Tem fotos 100, sem igualar a luz", "scantailor", "retangular", 100, False, False),
]


def processar_uma(pdf: Path, filtro: str, combinacao, pasta: Path):
    """(imagem do resultado, fração da página que virou gravura, segundos)."""
    import fitz

    from core import detectar_regioes as dr
    from core import pipeline
    from core.selecao import GRAVURA
    from modelos import Projeto

    _chave, _rotulo, detector, forma, sens, claras, luz = combinacao
    dr.DETECTOR_DE_GRAVURA_PADRAO = detector
    pipeline._GEOMETRIAS.clear()
    pipeline._DPIS_DO_SCAN.clear()
    projeto = Projeto(caminho_entrada=str(pdf), nome=pdf.stem)
    projeto.filtro_padrao = filtro
    projeto.gravura_forma, projeto.gravura_sensibilidade = forma, sens
    projeto.gravura_mais_sensivel, projeto.gravura_normalizar = claras, luz
    projeto = pipeline.analisar_projeto(projeto)
    projeto.caminho_saida = str(pasta / "saida.pdf")
    inicio = time.perf_counter()
    pipeline.processar(projeto)
    segundos = time.perf_counter() - inicio
    with fitz.open(projeto.caminho_saida) as doc:
        pix = doc[0].get_pixmap(dpi=150, alpha=False)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR if pix.n == 3 else cv2.COLOR_GRAY2BGR)
    Path(projeto.caminho_saida).unlink(missing_ok=True)
    pagina = projeto.paginas[0]
    sel = pagina.obter_selecao()
    gravura = float(sel.mascara(400, 300, GRAVURA).mean()) if not sel.vazia else 0.0
    return img, gravura, segundos, sel


def rotular(img: np.ndarray, texto: str, largura_alvo: int = 520) -> np.ndarray:
    """A imagem na largura pedida, com o rótulo numa faixa branca em cima."""
    from PIL import Image, ImageDraw, ImageFont

    escala = largura_alvo / img.shape[1]
    img = cv2.resize(img, (largura_alvo, int(img.shape[0] * escala)), interpolation=cv2.INTER_AREA)
    faixa = np.full((56, largura_alvo, 3), 255, np.uint8)
    junto = np.vstack([faixa, img])
    pil = Image.fromarray(cv2.cvtColor(junto, cv2.COLOR_BGR2RGB))
    try:
        fonte = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
    except OSError:
        fonte = ImageFont.load_default()
    ImageDraw.Draw(pil).multiline_text((8, 4), texto, fill=(0, 0, 0), font=fonte, spacing=2)
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def grade(paineis: list[np.ndarray], por_linha: int = 4) -> np.ndarray:
    altura = max(p.shape[0] for p in paineis)
    cheios = [np.vstack([p, np.full((altura - p.shape[0], p.shape[1], 3), 255, np.uint8)]) for p in paineis]
    branco = np.full_like(cheios[0], 255)
    linhas = []
    for i in range(0, len(cheios), por_linha):
        linha = cheios[i:i + por_linha]
        linha += [branco] * (por_linha - len(linha))
        linhas.append(np.hstack([np.hstack([p, np.full((p.shape[0], 12, 3), 255, np.uint8)]) for p in linha]))
    return np.vstack([np.vstack([l, np.full((12, l.shape[1], 3), 255, np.uint8)]) for l in linhas])


def original_da_pagina(pdf: Path) -> np.ndarray:
    import fitz

    with fitz.open(pdf) as doc:
        pix = doc[0].get_pixmap(dpi=150, alpha=False)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)


def zona_de_gravura(img: np.ndarray, selecao) -> np.ndarray:
    """O resultado com a gravura em vermelho por cima."""
    from core.selecao import GRAVURA

    vis = img.copy()
    if selecao is not None and not selecao.vazia:
        m = selecao.mascara(img.shape[0], img.shape[1], GRAVURA)
        vis[m] = (vis[m] * 0.45 + np.array([0, 0, 255]) * 0.55).astype(np.uint8)
    return vis


def main(saida: Path) -> None:
    (saida / "folhas").mkdir(parents=True, exist_ok=True)
    (saida / "resultado").mkdir(parents=True, exist_ok=True)
    numeros: dict = {}
    temporaria = Path(tempfile.mkdtemp(prefix="rodada_opcoes_"))
    for pid, pdf in PAGINAS.items():
        original = original_da_pagina(pdf)
        numeros[pid] = {}
        gravuras = [rotular(original, "Original")]
        for filtro, nome_filtro in FILTROS.items():
            paineis = [rotular(original, f"Original\n{pid}")]
            for combinacao in COMBINACOES:
                chave, rotulo = combinacao[0], combinacao[1]
                print(f"{pid} {nome_filtro} {rotulo}", flush=True)
                img, gravura, segundos, sel = processar_uma(pdf, filtro, combinacao, temporaria)
                cv2.imwrite(str(saida / "resultado" / f"{pid}-{filtro}-{chave}.png"), img)
                numeros[pid][f"{filtro}-{chave}"] = {"gravura": round(gravura, 4),
                                                     "segundos": round(segundos, 1)}
                paineis.append(rotular(img, f"{rotulo}\ngravura: {100 * gravura:.0f}% da página"))
                if filtro == "magico_pro":
                    gravuras.append(rotular(zona_de_gravura(img, sel), f"{rotulo}\n{100 * gravura:.0f}%"))
            cv2.imwrite(str(saida / "folhas" / f"{pid}-{filtro}.jpg"), grade(paineis),
                        [cv2.IMWRITE_JPEG_QUALITY, 85])
        cv2.imwrite(str(saida / "folhas" / f"{pid}-gravura.jpg"), grade(gravuras),
                    [cv2.IMWRITE_JPEG_QUALITY, 85])
        (saida / "numeros.json").write_text(json.dumps(numeros, ensure_ascii=False, indent=1),
                                            encoding="utf-8")
    try:
        for arquivo in temporaria.iterdir():
            arquivo.unlink()
        temporaria.rmdir()
    except OSError:
        pass


if __name__ == "__main__":
    from datetime import datetime

    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        RAIZ / "relatorios" / "conferir" / f"fase1-1.2-opcoes-{datetime.now():%Y-%m-%d}")
    main(destino)
