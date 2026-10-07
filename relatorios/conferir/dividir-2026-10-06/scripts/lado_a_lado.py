"""Material para o Samuel ver o item 2.1 (dividir): lado a lado dos jeitos.

Uso (da raiz do projeto, com a pasta de dados de mentira):
    .venv\\Scripts\\python.exe relatorios\\conferir\\dividir-2026-10-06\\scripts\\lado_a_lado.py

Para cada folha (paginas-gabarito do dividir e folhas de um livro escaneado
aberto), passa a folha pelo PROGRAMA (core.pipeline.analisar_projeto, a 150
DPI, como ao abrir o livro) em quatro configuracoes do livro:
    A. "o do programa"          (dividir marcado, jeito programa)
    B. "o do ScanTailor"        (dividir marcado, jeito scantailor)
    C. "ScanTailor + sobra"     (B + "Cortar a beirada da folha vizinha")
    D. "nao dividir + sobra"    (dividir desmarcado + o corte da sobra)
e grava uma imagem por folha: em cima, CADA jeito numa COPIA do original com a
linha desenhada (nunca por cima do resultado); embaixo, as paginas que saem
(core.pipeline.preparar_metade, sem cortar bordas nem endireitar, para so a
divisao aparecer). Grava tambem dados/medidas.json.

Nada aqui muda o programa nem os livros (somente leitura).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

from core import dividir_scantailor as ds  # noqa: E402
from core import pipeline  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402
from modelos import Projeto  # noqa: E402

PASTA = Path(__file__).resolve().parents[1]
IMAGENS = PASTA / "imagens"
DADOS = PASTA / "dados"

GABARITO = ["siebmacher_p007", "siebmacher_p009", "opusmajus_p256", "escola_p007",
            "escola_p035", "graduale_p221", "graduale_p222", "horas_p011", "palatino_p005"]

LIVRO_ABERTO = Path(r"D:\Livros para editar\Tractatus Dogmatici (vol. 3)_  - Hugon, Édouard, O.P._7207.pdf")
FOLHAS_DO_LIVRO = [0, 40, 120, 240, 360, 470]
LIVRO_ABERTO_2 = Path(r"D:\Livros para editar\2 - TEOLOGIA\Padre M. Teixeira Leite Penido - O Corpo Místico.pdf")
FOLHAS_DO_LIVRO_2 = [2, 90]

JEITOS = {
    "A": dict(nome="o do programa", dividir_folhas=True, dividir_como=ds.JEITO_PROGRAMA, cortar_sobra=False),
    "B": dict(nome="o do ScanTailor", dividir_folhas=True, dividir_como=ds.JEITO_SCANTAILOR, cortar_sobra=False),
    "C": dict(nome="ScanTailor + corte da sobra", dividir_folhas=True, dividir_como=ds.JEITO_SCANTAILOR,
              cortar_sobra=True),
    "D": dict(nome="não dividir + corte da sobra", dividir_folhas=False, dividir_como=ds.JEITO_PROGRAMA,
              cortar_sobra=True),
}
CORES = {"A": (200, 90, 20), "B": (30, 30, 220), "C": (20, 140, 230), "D": (40, 150, 40)}   # BGR
ALTURA_ORIGINAL = 520
ALTURA_PAGINA = 360


def _projeto(caminho: str, jeito: dict) -> Projeto:
    return Projeto(caminho_entrada=caminho, endireitar=False, cortar_bordas=False,
                   dividir_folhas=jeito["dividir_folhas"], dividir_como=jeito["dividir_como"],
                   cortar_sobra=jeito["cortar_sobra"], detectar_regioes=False)


def _reduzir(img: np.ndarray, altura: int) -> np.ndarray:
    escala = altura / img.shape[0]
    return cv2.resize(img, (max(1, int(img.shape[1] * escala)), altura), interpolation=cv2.INTER_AREA)


def _linha_vertical(img, x, cor, espessura=3, tracejada=False):
    h = img.shape[0]
    if not tracejada:
        cv2.line(img, (x, 0), (x, h - 1), cor, espessura)
        return
    for y in range(0, h, 18):
        cv2.line(img, (x, y), (x, min(h - 1, y + 10)), cor, espessura)


def _rotulo(img, texto, cor=(0, 0, 0)):
    """Uma ou mais linhas de texto em cima da imagem (separadas por |)."""
    linhas = texto.split("|")
    faixa = np.full((10 + 28 * len(linhas), img.shape[1], 3), 255, np.uint8)
    for i, linha in enumerate(linhas):
        cv2.putText(faixa, linha.strip(), (6, 28 + 28 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.62, cor, 2,
                    cv2.LINE_AA)
    return np.vstack([faixa, img])


def _texto_ascii(texto: str) -> str:
    """O putText do OpenCV nao desenha acento."""
    import unicodedata
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


def _caixa(img, largura, altura):
    """Centraliza img numa caixa branca largura x altura."""
    caixa = np.full((altura, largura, 3), 255, np.uint8)
    h, w = img.shape[:2]
    y, x = (altura - h) // 2, (largura - w) // 2
    caixa[y:y + h, x:x + w] = img
    return caixa


def uma_folha(caminho_pdf: str, indice: int, nome: str, dpi_desenho: int = 110) -> dict:
    """Passa a folha pelos quatro jeitos e grava a imagem lado a lado."""
    doc = abrir_pdf(caminho_pdf)
    try:
        original = pagina_para_array(doc, indice, dpi=dpi_desenho)
    finally:
        doc.close()
    medidas = {"nome": nome, "folha": indice + 1, "jeitos": {}}
    colunas = []
    for chave, jeito in JEITOS.items():
        projeto = _projeto(caminho_pdf, jeito)
        # so a folha pedida: um "livro" de uma folha seria o PDF inteiro;
        # analisar_projeto le todas, entao aqui a analise e feita a mao, com
        # as MESMAS funcoes que ela usa (achar_divisao, achar_sobra).
        doc = abrir_pdf(caminho_pdf)
        try:
            img150 = pagina_para_array(doc, indice, dpi=pipeline.DPI_ANALISE)
        finally:
            doc.close()
        inicio = time.perf_counter()
        lombada = (pipeline.achar_divisao(img150, jeito["dividir_como"], pipeline.DPI_ANALISE)
                   if jeito["dividir_folhas"] else None)
        dividir = bool(lombada and lombada.e_paisagem)
        sobra = (pipeline.achar_sobra(img150, pipeline.DPI_ANALISE)
                 if jeito["cortar_sobra"] and not dividir else None)
        segundos = time.perf_counter() - inicio
        from modelos import METADE_DIREITA, METADE_ESQUERDA, METADE_INTEIRA, ConfigFolha, ConfigPagina
        folha = ConfigFolha(indice=indice, dividir=dividir,
                            posicao_corte=lombada.posicao if lombada else 0.5, sobra=sobra)
        metades = [METADE_ESQUERDA, METADE_DIREITA] if dividir else [METADE_INTEIRA]
        paginas = [pipeline.preparar_metade(original, folha, ConfigPagina(indice=0, folha=indice, metade=m),
                                            projeto) for m in metades]
        medidas["jeitos"][chave] = {
            "divide": dividir, "posicao": round(folha.posicao_corte, 4) if dividir else None,
            "sobra": list(sobra) if sobra else None, "segundos": round(segundos, 3),
            "paginas_px": [list(p.shape[1::-1]) for p in paginas]}

        # em cima: uma COPIA do original com a linha deste jeito
        copia = _reduzir(original, ALTURA_ORIGINAL).copy()
        w = copia.shape[1]
        if dividir:
            _linha_vertical(copia, int(round(folha.posicao_corte * w)), CORES[chave], 4)
        if sobra and jeito["cortar_sobra"]:
            for v in sobra:
                if 0.0 < v < 1.0:
                    _linha_vertical(copia, int(round(v * w)), CORES[chave], 3, tracejada=True)
        if dividir:
            frase = f"{chave}. {jeito['nome']}|divide a {folha.posicao_corte * 100:.0f}% da largura"
        elif sobra:
            frase = (f"{chave}. {jeito['nome']}|1 pagina; fica de {sobra[0]*100:.0f}% "
                     f"a {sobra[1]*100:.0f}% (tracejado)")
        else:
            frase = f"{chave}. {jeito['nome']}|1 pagina, nada cortado"
        copia = _caixa(copia, max(copia.shape[1], 440), copia.shape[0])
        topo = _rotulo(copia, _texto_ascii(frase), CORES[chave])

        # embaixo: as paginas que saem, lado a lado, com um espaco entre elas
        saidas = [_reduzir(p, ALTURA_PAGINA) for p in paginas]
        juntas = saidas[0]
        for s in saidas[1:]:
            juntas = np.hstack([juntas, np.full((ALTURA_PAGINA, 14, 3), 200, np.uint8), s])
        largura = max(topo.shape[1], juntas.shape[1])
        baixo = _rotulo(juntas, f"sai: {len(paginas)} pagina(s)")
        coluna = np.vstack([_caixa(topo, largura, topo.shape[0]),
                            np.full((10, largura, 3), 255, np.uint8),
                            _caixa(baixo, largura, baixo.shape[0])])
        colunas.append(coluna)

    # Detalhe da dobra (folhas de livro aberto): a faixa do meio ampliada,
    # uma COPIA para cada jeito que divide, com a linha dele
    posicoes = {k: v["posicao"] for k, v in medidas["jeitos"].items() if k in ("A", "B") and v["divide"]}
    if len(posicoes) == 2:
        doc = abrir_pdf(caminho_pdf)
        try:
            grande = pagina_para_array(doc, indice, dpi=200)
        finally:
            doc.close()
        h, w = grande.shape[:2]
        meio = sum(posicoes.values()) / 2
        x0 = max(0, int((meio - 0.12) * w))
        x1 = min(w, int((meio + 0.12) * w))
        y0, y1 = int(0.25 * h), int(0.65 * h)
        recortes = []
        for k, pos in posicoes.items():
            pedaco = grande[y0:y1, x0:x1].copy()
            _linha_vertical(pedaco, int(round(pos * w)) - x0, CORES[k], 3)
            recortes.append(_rotulo(_reduzir(pedaco, 520), _texto_ascii(f"{k}. {JEITOS[k]['nome']} (ampliado)"),
                                    CORES[k]))
            recortes.append(np.full((recortes[-1].shape[0], 20, 3), 255, np.uint8))
        detalhe = np.hstack(recortes[:-1])
        cv2.imwrite(str(IMAGENS / f"{nome}_dobra.jpg"), detalhe, [cv2.IMWRITE_JPEG_QUALITY, 88])
        medidas["dobra"] = f"imagens/{nome}_dobra.jpg"

    altura = max(c.shape[0] for c in colunas)
    linha = np.hstack([np.vstack([c, np.full((altura - c.shape[0], c.shape[1], 3), 255, np.uint8)])
                       for c in _com_separadores(colunas)])
    IMAGENS.mkdir(parents=True, exist_ok=True)
    arquivo = IMAGENS / f"{nome}.jpg"
    cv2.imwrite(str(arquivo), linha, [cv2.IMWRITE_JPEG_QUALITY, 88])
    medidas["imagem"] = f"imagens/{arquivo.name}"
    return medidas


def _com_separadores(colunas):
    saida = []
    for i, c in enumerate(colunas):
        if i:
            saida.append(np.full((c.shape[0], 24, 3), 255, np.uint8))
        saida.append(c)
    return saida


def main() -> int:
    lista = json.loads((RAIZ / "gabarito" / "lista.json").read_text(encoding="utf-8"))["paginas"]
    todas = []
    for nome in GABARITO:
        caminho = str(RAIZ / "gabarito" / lista[nome]["pdf"])
        todas.append(uma_folha(caminho, 0, nome))
        print(nome, json.dumps(todas[-1]["jeitos"], ensure_ascii=False), flush=True)
    for livro, folhas, prefixo in ((LIVRO_ABERTO, FOLHAS_DO_LIVRO, "hugon"),
                                   (LIVRO_ABERTO_2, FOLHAS_DO_LIVRO_2, "penido")):
        for indice in folhas:
            todas.append(uma_folha(str(livro), indice, f"{prefixo}_f{indice + 1:03d}"))
            print(todas[-1]["nome"], json.dumps(todas[-1]["jeitos"], ensure_ascii=False), flush=True)
    DADOS.mkdir(parents=True, exist_ok=True)
    (DADOS / "medidas.json").write_text(json.dumps(todas, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
