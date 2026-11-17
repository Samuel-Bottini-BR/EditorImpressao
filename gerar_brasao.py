"""Desenha, a partir do vetor do brasao (.ai), o icone do programa e as imagens do giro.

Decisoes do Samuel de 17/11/2026 (D-744 a D-747; medidas e caminhos em
brasao.py). Palavras dele que este script cumpre: "eu mandei um arquivo em .ai
que daria para vetorizar sem problemas, porque não fez isso?" (D-746). Por
isso CADA tamanho do icone e CADA escala do giro sao desenhados direto do
vetor, no tamanho final; nunca se desenha uma imagem grande para depois
diminuir.

Como usar (so quando o brasao ou as medidas mudarem):
    .venv\\Scripts\\python.exe gerar_brasao.py
Grava em recursos/brasao/:
- brasao.ico: os tamanhos de brasao.TAMANHOS_DO_ICONE num arquivo so. Ate 128
  em BMP de 32 bits (o formato classico, que todo programa do Windows le); o
  256 em PNG (o jeito do proprio Windows para esse tamanho).
- giro-100.png, giro-125.png, ...: o brasao do giro em cada escala de tela do
  Windows (brasao.ESCALAS_DO_GIRO), com fundo transparente.
O resultado entra no git, para o empacotamento nao depender deste script.

O .ai abre como PDF no PyMuPDF (o Illustrator grava uma copia PDF dentro).
O desenho nao e mexido: nem cor, nem corte, nem sombra (D-744). A unica
coisa escolhida aqui e o recorte da pagina (brasao.CAIXA_DO_BRASAO), o mesmo
da pagina de exemplo aprovada (D-747).

Arriscado mudar: o formato do .ico (escrever_ico) - o Windows, o PyInstaller,
o Inno e o Velopack leem esse arquivo; os testes em
tests/test_decisoes_brasao.py conferem cada tamanho contra um desenho novo do
vetor.
"""

from __future__ import annotations

import io
import struct
import sys
from pathlib import Path

import brasao


def _desenhar(recorte: tuple[float, float, float, float], escala: float, original: Path | None = None):
    """Desenha um pedaco da pagina do .ai, direto do vetor, com fundo transparente.

    `recorte` em pontos do .ai; `escala` = pixels por ponto. A matriz leva o
    canto do recorte ao pixel (0, 0), para o resultado ter exatamente o
    tamanho pedido (sem a coluna/linha a mais que um canto fracionario daria).
    Devolve uma imagem RGBA do Pillow (cores sem pre-multiplicar).
    """
    import fitz
    from PIL import Image

    x0, y0, x1, y1 = recorte
    documento = fitz.open(str(original or brasao.ORIGINAL))
    try:
        matriz = fitz.Matrix(escala, 0, 0, escala, -x0 * escala, -y0 * escala)
        pixmap = documento[0].get_pixmap(matrix=matriz, clip=fitz.Rect(x0, y0, x1, y1), alpha=True)
        png = pixmap.tobytes("png")
    finally:
        documento.close()
    return Image.open(io.BytesIO(png)).convert("RGBA")


def desenhar_icone(tamanho: int, original: Path | None = None):
    """O brasao inteiro num quadrado de `tamanho` x `tamanho`, desenhado do vetor."""
    x0, _y0, x1, _y1 = brasao.quadrado_do_icone()
    imagem = _desenhar(brasao.quadrado_do_icone(), tamanho / (x1 - x0), original)
    if imagem.size != (tamanho, tamanho):  # pragma: no cover - so se o PyMuPDF mudar o arredondamento
        raise RuntimeError(f"o icone de {tamanho} saiu com {imagem.size}")
    return imagem


def desenhar_giro(escala_da_tela: float, original: Path | None = None):
    """O brasao do giro para uma escala de tela do Windows, desenhado do vetor."""
    return _desenhar(brasao.caixa_com_margem(), brasao.escala_do_giro() * escala_da_tela, original)


def _entrada_bmp(imagem) -> bytes:
    """Uma imagem do .ico no formato classico: BMP de 32 bits (azul, verde,
    vermelho, transparencia), de baixo para cima, mais a mascara de 1 bit (toda
    zero: quem manda e a transparencia)."""
    largura, altura = imagem.size
    cabecalho = struct.pack("<IiiHHIIiiII", 40, largura, altura * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    r, g, b, a = imagem.split()
    from PIL import Image

    bgra = Image.merge("RGBA", (b, g, r, a)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes()
    linha_da_mascara = ((largura + 31) // 32) * 4
    return cabecalho + bgra + bytes(linha_da_mascara * altura)


def escrever_ico(imagens: list) -> bytes:
    """Junta as imagens (quadradas, de tamanhos diferentes) num arquivo .ico.

    Cada imagem entra como esta (nada e redimensionado). Ate 128 px em BMP de
    32 bits; 256 px em PNG.
    """
    imagens = sorted(imagens, key=lambda i: i.size[0])
    dados = []
    for imagem in imagens:
        if imagem.size[0] >= 256:
            saida = io.BytesIO()
            imagem.save(saida, format="PNG")
            dados.append(saida.getvalue())
        else:
            dados.append(_entrada_bmp(imagem))
    cabecalho = struct.pack("<HHH", 0, 1, len(imagens))
    posicao = 6 + 16 * len(imagens)
    diretorio = b""
    for imagem, bloco in zip(imagens, dados):
        lado = imagem.size[0]
        byte_do_lado = 0 if lado >= 256 else lado
        diretorio += struct.pack("<BBBBHHII", byte_do_lado, byte_do_lado, 0, 0, 1, 32, len(bloco), posicao)
        posicao += len(bloco)
    return cabecalho + diretorio + b"".join(dados)


def ler_ico(conteudo: bytes) -> dict:
    """Le um .ico escrito por escrever_ico: {lado: imagem RGBA do Pillow}.

    Feito aqui (e nao pelo Pillow) para o teste conferir byte a byte o que o
    arquivo tem, sem o Pillow escolher ou redimensionar nada.
    """
    from PIL import Image

    _reservado, _tipo, quantos = struct.unpack_from("<HHH", conteudo, 0)
    imagens = {}
    for i in range(quantos):
        lado, _a, _c, _r, _p, _bits, tamanho, posicao = struct.unpack_from("<BBBBHHII", conteudo, 6 + 16 * i)
        lado = lado or 256
        bloco = conteudo[posicao:posicao + tamanho]
        if bloco[:8] == b"\x89PNG\r\n\x1a\n":
            imagens[lado] = Image.open(io.BytesIO(bloco)).convert("RGBA")
            continue
        bgra = bloco[40:40 + lado * lado * 4]
        b, g, r, a = Image.frombytes("RGBA", (lado, lado), bgra).split()
        imagens[lado] = Image.merge("RGBA", (r, g, b, a)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    return imagens


def gerar(original: Path | None = None, pasta: Path | None = None) -> list[Path]:
    """Desenha o icone e as imagens do giro e grava em `pasta` (recursos/brasao)."""
    pasta = pasta or brasao.PASTA
    pasta.mkdir(parents=True, exist_ok=True)
    gravados = []
    icone = pasta / brasao.ICONE.name
    icone.write_bytes(escrever_ico([desenhar_icone(n, original) for n in brasao.TAMANHOS_DO_ICONE]))
    gravados.append(icone)
    for escala in brasao.ESCALAS_DO_GIRO:
        destino = pasta / brasao.arquivo_do_giro(escala).name
        desenhar_giro(escala, original).save(destino, format="PNG")
        gravados.append(destino)
    return gravados


def main() -> int:
    if not brasao.ORIGINAL.exists():
        print(f"Não achei o desenho do brasão: {brasao.ORIGINAL}")
        return 1
    for caminho in gerar():
        print(f"gravado: {caminho.relative_to(brasao.RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
