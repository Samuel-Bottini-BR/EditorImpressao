"""Antes/depois do conserto de 06/11/2026 (D-095 / D-639): Destino do
socialismo, p. 18, pagina da direita, com o Desentortar automatico e a
protecao segurando a pagina ("Desentortar não usado").

Caminho inteiro do programa (CLAUDE.md §4.10): livro novo de fabrica
(analisar_projeto), dividida (direita) -> endireitada -> cortada ->
Desentortar automatico (segurado) -> filtro de fabrica (Original), desenhada
na resolucao do livro com core.pipeline.renderizar_pagina (o mesmo desenho
do PDF).

"Antes" = o codigo de antes do conserto: a unica linha nova
(_segurada_com_a_cunha_do_papel) trocada por "devolve a pagina como veio".
Tambem gera a pagina com o Desentortar desligado (a referencia: o cantinho
ja saia da cor do papel). So le o PDF do Samuel.

Uso: .venv\\Scripts\\python.exe relatorios\\cunha-desentortar\\antes_depois.py
"""
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from core import analise, pipeline  # noqa: E402
from core import desentortar_scantailor as ds  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from tests.test_desentortar_conferir_de_novo import DESTINO  # noqa: E402
from tests.test_desentortar_protecao import _pagina_do_acervo  # noqa: E402

SAIDA = Path(__file__).parent
CAMINHO = ("Caminho: livro novo de fábrica, dividida (página da direita), endireitada, cortada, "
           "Desentortar automático (a proteção segurou: aviso \"Desentortar não usado\"), filtro Original")


def desenhar(projeto, pagina, modo):
    pipeline._DESENTORTADAS.clear()
    pagina.desentortar = modo
    pagina.filtro = ORIGINAL
    pagina.alertas = [a for a in pagina.alertas if a != analise.DESENTORTAR_SAIU_SEM]
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
    finally:
        doc.close()
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img, analise.DESENTORTAR_SAIU_SEM in pagina.alertas


def fonte(tamanho):
    for nome in ("arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            pass
    return ImageFont.load_default()


def quadro(img, titulo, linhas):
    """O canto de cima, à esquerda (onde fica a lasca), ampliado 5x."""
    canto = img[:160, :120]
    grande = cv2.resize(canto, (canto.shape[1] * 5, canto.shape[0] * 5), interpolation=cv2.INTER_NEAREST)
    rgb = Image.fromarray(cv2.cvtColor(grande, cv2.COLOR_BGR2RGB))
    tela = Image.new("RGB", (rgb.width + 20, rgb.height + 46 + 26 * len(linhas)), "white")
    topo = 40 + 26 * len(linhas)
    tela.paste(rgb, (10, topo))
    d = ImageDraw.Draw(tela)
    # moldura cinza: sem ela a lasca branca some no branco do quadro
    d.rectangle((7, topo - 3, 10 + rgb.width + 2, topo + rgb.height + 2), outline=(90, 90, 90), width=3)
    d.text((10, 8), titulo, fill="black", font=fonte(26))
    for i, linha in enumerate(linhas):
        d.text((10, 42 + 26 * i), linha, fill=(60, 60, 60), font=fonte(18))
    return tela


def main():
    tmp = Path(tempfile.mkdtemp())
    _, folha, pagina, projeto = _pagina_do_acervo(tmp, DESTINO, 17, 0, True, "direita")

    original = pipeline._segurada_com_a_cunha_do_papel
    pipeline._segurada_com_a_cunha_do_papel = lambda preparo, *a, **k: preparo
    try:
        antes, aviso_antes = desenhar(projeto, pagina, ds.AUTOMATICO)
    finally:
        pipeline._segurada_com_a_cunha_do_papel = original
    depois, aviso_depois = desenhar(projeto, pagina, ds.AUTOMATICO)
    desligado, _ = desenhar(projeto, pagina, ds.DESLIGADO)

    def brancos(img):
        return int((img[:, :12].min(axis=2) >= 254).sum())

    def dif(a, b):
        return int((np.abs(a.astype(int) - b.astype(int)) > 64).sum()) if a.shape == b.shape else -1

    quadros = [
        quadro(antes, "ANTES (código de antes do conserto)",
               [f"aviso \"Desentortar não usado\": {'sim' if aviso_antes else 'NÃO'}",
                f"pontos branco puro nos 12 pontos da esquerda: {brancos(antes)}"]),
        quadro(depois, "DEPOIS (com o conserto)",
               [f"aviso \"Desentortar não usado\": {'sim' if aviso_depois else 'NÃO'}",
                f"pontos branco puro nos 12 pontos da esquerda: {brancos(depois)}"]),
        quadro(desligado, "REFERÊNCIA: Desentortar desligado",
               ["(sem aviso: o Desentortar está desligado)",
                f"pontos branco puro nos 12 pontos da esquerda: {brancos(desligado)}"]),
    ]
    largura = sum(q.width for q in quadros)
    altura = max(q.height for q in quadros)
    cab = 90
    final = Image.new("RGB", (largura, altura + cab), "white")
    d = ImageDraw.Draw(final)
    d.text((10, 8), "Destino do socialismo (Octávio de Faria), p. 18, página da direita; "
                    "canto de cima à esquerda, ampliado 5 vezes", fill="black", font=fonte(22))
    d.text((10, 40), CAMINHO, fill=(60, 60, 60), font=fonte(16))
    d.text((10, 62), "Desenhada na resolução do livro (300 DPI), o mesmo desenho do PDF.",
           fill=(60, 60, 60), font=fonte(16))
    x = 0
    for q in quadros:
        final.paste(q, (x, cab))
        x += q.width
    final.save(SAIDA / "destino18-direita-antes-depois.png")
    cv2.imwrite(str(SAIDA / "destino18-direita-antes-pagina-inteira.jpg"),
                cv2.resize(antes, None, fx=0.35, fy=0.35, interpolation=cv2.INTER_AREA))
    cv2.imwrite(str(SAIDA / "destino18-direita-depois-pagina-inteira.jpg"),
                cv2.resize(depois, None, fx=0.35, fy=0.35, interpolation=cv2.INTER_AREA))

    print("aviso antes/depois:", aviso_antes, aviso_depois)
    print("brancos na beirada esquerda antes/depois/desligado:", brancos(antes), brancos(depois), brancos(desligado))
    print("valores >64 contra o desligado, antes/depois:", dif(antes, desligado), dif(depois, desligado))
    print("valores >64 entre antes e depois:", dif(antes, depois))


if __name__ == "__main__":
    main()
