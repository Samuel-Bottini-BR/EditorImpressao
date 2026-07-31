"""Leitura e escrita de PDF.

Este modulo e a única porta de entrada e saida de PDF do projeto.
Regra de ouro (secao 3.1 da especificacao): NUNCA carregar o livro inteiro
na memória. Sempre uma página por vez: ler -> processar -> escrever -> soltar.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

import cv2
import fitz  # PyMuPDF
import numpy as np
from PIL import Image

# Teto de pixels por pagina. Acima disso o DPI e reduzido automaticamente.
# 40 milhoes de pixels ~= uma folha A4 a 550 DPI. Passar disso estoura a
# memoria quando o livro tem 500+ paginas.
MAX_PIXELS = 40_000_000

DPI_PADRAO = 300
DPI_PREVIA = 150
DPI_MINIATURA = 25


class ErroPDF(Exception):
    """Erro de leitura/escrita de PDF já traduzido para o usuario final."""


@dataclass(frozen=True)
class InfoPagina:
    """Dados de uma página sem carregar a imagem dela."""

    indice: int
    largura_pt: float
    altura_pt: float

    @property
    def paisagem(self) -> bool:
        # 1.2 e a folga usada na deteccao de folha dupla (secao 4.1).
        return self.largura_pt > self.altura_pt * 1.2


def abrir_pdf(caminho: str | Path) -> fitz.Document:
    """Abre o PDF e devolve o documento aberto.

    Levanta ErroPDF com mensagem em portugues se não der.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        raise ErroPDF(
            "Não consegui achar esse arquivo. Ele pode ter sido movido ou apagado."
        )
    try:
        doc = fitz.open(caminho)
    except Exception as exc:  # noqa: BLE001 - qualquer falha vira mensagem amigavel
        raise ErroPDF(
            "Não consegui abrir esse arquivo. Ele pode estar danificado ou não ser um PDF."
        ) from exc

    if doc.page_count == 0:
        doc.close()
        raise ErroPDF("Esse PDF está vazio, não tem nenhuma página.")

    if doc.needs_pass:
        doc.close()
        raise ErroPDF("Esse PDF está protegido por senha. Não consigo abrir.")

    return doc


def info_paginas(doc: fitz.Document) -> list[InfoPagina]:
    """Tamanho de cada página, sem rasterizar nada (rapido mesmo com 500 páginas)."""
    infos: list[InfoPagina] = []
    for i in range(doc.page_count):
        r = doc[i].rect
        infos.append(InfoPagina(indice=i, largura_pt=r.width, altura_pt=r.height))
    return infos


def dpi_real_da_pagina(doc: fitz.Document, indice: int) -> float:
    """Com quantos pontos por polegada a página foi ESCANEADA de verdade.

    Vem da imagem embutida no PDF, e não do tamanho com que nós a
    rasterizamos. Medir na imagem rasterizada devolve sempre o DPI que nós
    mesmos pedimos - foi assim que o alerta de qualidade baixa ficou sem nunca
    disparar, nem em scan de 112 DPI.

    Devolve 0.0 quando a página não tem imagem embutida (PDF de texto).
    """
    try:
        pagina = doc[indice]
        largura_pt = pagina.rect.width
        if largura_pt <= 0:
            return 0.0

        maior = 0
        for imagem in pagina.get_images():
            try:
                dados = doc.extract_image(imagem[0])
            except Exception:  # noqa: BLE001 - imagem estranha não derruba nada
                continue
            maior = max(maior, int(dados.get("width", 0)))

        if maior <= 0:
            return 0.0
        return maior / (largura_pt / 72.0)
    except Exception:  # noqa: BLE001
        return 0.0


def dpi_seguro(pagina: fitz.Page, dpi: int) -> int:
    """Reduz o DPI até a página caber em MAX_PIXELS.

    Trabalha em pontos (1 pt = 1/72 pol), entao pixels = pt / 72 * dpi.
    """
    largura_pol = pagina.rect.width / 72.0
    altura_pol = pagina.rect.height / 72.0
    area_pol = largura_pol * altura_pol
    if area_pol <= 0:
        return dpi
    dpi_max = int((MAX_PIXELS / area_pol) ** 0.5)
    return max(50, min(dpi, dpi_max))


def pagina_para_array(
    doc: fitz.Document, indice: int, dpi: int = DPI_PADRAO
) -> np.ndarray:
    """Rasteriza uma página e devolve um array BGR (uint8), no formato do OpenCV.

    O DPI pedido e reduzido sozinho se a página for grande demais.
    """
    if not 0 <= indice < doc.page_count:
        raise ErroPDF(f"Essa página não existe (pedi a {indice + 1}).")

    pagina = doc[indice]
    dpi_usado = dpi_seguro(pagina, dpi)
    escala = dpi_usado / 72.0
    pix = pagina.get_pixmap(matrix=fitz.Matrix(escala, escala), alpha=False)

    # frombuffer nao copia; o reshape cria a visao. O .copy() no fim garante que
    # o array sobrevive ao descarte do pixmap logo abaixo.
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    resultado = np.ascontiguousarray(img)
    del pix  # solta a memoria do pixmap na hora
    return resultado


def limitar_altura(img: np.ndarray, altura_max: int) -> np.ndarray:
    """Reduz a imagem se ela passar da altura dada. Usado nas prévias e miniaturas."""
    h = img.shape[0]
    if h <= altura_max:
        return img
    escala = altura_max / h
    novo = (max(1, int(img.shape[1] * escala)), altura_max)
    return cv2.resize(img, novo, interpolation=cv2.INTER_AREA)


class EscritorPDF:
    """Monta o PDF de saida página por página.

    Uso:
        with EscritorPDF("saida.pdf") as saida:
            saida.escrever_imagem(img, dpi=300)
    """

    def __init__(self, caminho: str | Path) -> None:
        self.caminho = Path(caminho)
        self.doc = fitz.open()
        self._paginas = 0

    def __enter__(self) -> "EscritorPDF":
        return self

    def __exit__(self, *_exc) -> None:
        self.fechar()

    @property
    def paginas(self) -> int:
        return self._paginas

    def escrever_imagem(
        self, img: np.ndarray, dpi: int = DPI_PADRAO, monocromatico: bool = False
    ) -> None:
        """Acrescenta uma página cujo conteúdo e a imagem dada.

        monocromatico=True salva em 1 bit (PNG preto e branco puro). O arquivo
        final fica muito menor - e o que faz o filtro Preto e branco valer a pena.
        """
        altura, largura = img.shape[:2]
        largura_pt = largura / dpi * 72.0
        altura_pt = altura / dpi * 72.0

        dados = _codificar_png(img, monocromatico=monocromatico)

        pagina = self.doc.new_page(width=largura_pt, height=altura_pt)
        pagina.insert_image(fitz.Rect(0, 0, largura_pt, altura_pt), stream=dados)
        self._paginas += 1

    def copiar_pagina(self, origem: fitz.Document, indice: int) -> None:
        """Copia a página do PDF de origem sem rasterizar.

        Preserva texto vetorial e qualidade original. E o caminho rapido do modo
        "só cadernos" (secao 4.5).
        """
        self.doc.insert_pdf(origem, from_page=indice, to_page=indice)
        self._paginas += 1

    def fechar(self) -> None:
        if self.doc is None:
            return
        try:
            if self._paginas:
                # A gravacao e o momento em que disco cheio, pendrive arrancado
                # e pasta sem permissao aparecem. Nada disso pode chegar na tela
                # como erro tecnico.
                try:
                    self.caminho.parent.mkdir(parents=True, exist_ok=True)
                    self.doc.save(self.caminho, garbage=3, deflate=True)
                except OSError as exc:
                    raise ErroPDF(
                        "Não consegui gravar o arquivo final. O disco pode estar "
                        "cheio, a pasta pode ter sido removida ou você pode não "
                        "ter permissão para gravar nela. Escolha outra pasta e "
                        "tente de novo."
                    ) from exc
        finally:
            self.doc.close()
            self.doc = None  # type: ignore[assignment]


def _codificar_png(img: np.ndarray, monocromatico: bool = False) -> bytes:
    """Converte o array em bytes PNG prontos para entrar no PDF."""
    if monocromatico:
        cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # mode "1" = 1 bit por pixel. O ponto do filtro Eco.
        pil = Image.fromarray(cinza).convert("1", dither=Image.Dither.NONE)
    elif img.ndim == 2:
        pil = Image.fromarray(img, mode="L")
    else:
        pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), mode="RGB")

    buffer = io.BytesIO()
    pil.save(buffer, format="PNG", optimize=False, compress_level=6)
    return buffer.getvalue()
