"""Rodada nas páginas-gabarito para os itens da Fase 2 (implementador, 20/10/2026).

PARA QUÊ
    Duas provas para cada item, pelo caminho do programa (core.pipeline:
    analisar_projeto -> renderizar_pagina na resolução do PDF, a mesma conta
    de _filtrar que o PDF final usa):

    1. --hashes: a soma (SHA-256) dos pontos de cada página em cada filtro
       comum, com tudo DE FÁBRICA. Rodado no código antigo e no novo, as somas
       têm de ser iguais: é a prova de que "desligado de fábrica" quer dizer
       "livro já começado sai igual ao de hoje".
    2. --item X: o antes/depois com a ferramenta LIGADA: uma imagem por página
       com as colunas lado a lado (Original, como sai hoje, e cada variante do
       item), mais um recorte ampliado, para o verificador e para as fotos do
       Samuel. Os números (quantos pontos mudaram) vão para um .json ao lado.

USO (da pasta da worktree; uma página por processo, por causa da memória)
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\fase2-itens\\scripts\\rodada_gabarito.py horas_p013 --hashes saida.json
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\fase2-itens\\scripts\\rodada_gabarito.py horas_p013 --item 2.8 --pasta relatorios\\fase2-itens\\2.8\\imagens

Lê o gabarito (somente leitura). A pasta de dados do programa (LOCALAPPDATA)
vai para uma pasta temporária: nada é escrito na pasta real do Samuel.

Seguro mudar: tamanhos e textos das imagens, as variantes de cada item.
Arriscado mudar: _desenhar (tem de ser o caminho do programa).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
GABARITO = RAIZ / "gabarito"

_DADOS = Path(tempfile.gettempdir()) / "fase2_itens_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

# As vezes em que um jeito do ScanTailor não rodou e o programa caiu no
# Automático (core.preto_e_branco_scantailor._avisar_uma_vez, trocado abaixo
# SÓ neste script): a coluna dessa variante seria o Automático com o nome
# errado. A rodada tenta de novo uma vez e, se falhar, escreve na coluna.
FALHAS: list[tuple] = []


def _registrar_falhas() -> None:
    from core import preto_e_branco_scantailor as pbst

    pbst._avisar_uma_vez = lambda motivo, detalhe: FALHAS.append((motivo, detalhe))
    from core import desentortar_scantailor as ds   # item 2.12

    ds._avisar_uma_vez = lambda motivo, detalhe: FALHAS.append((motivo, detalhe))


FONTE = Path(r"C:\Windows\Fonts\segoeui.ttf")
FONTE_NEGRITO = Path(r"C:\Windows\Fonts\segoeuib.ttf")


# ------------------------------------------------------------------ o programa

# --pdf: um PDF de fora do gabarito (uma página copiada do acervo para uma
# pasta de rascunho; o acervo é somente leitura). None = gabarito/paginas/<pid>.pdf.
PDF_DE_FORA: Path | None = None


def abrir(pid: str):
    """(projeto, doc) do PDF do gabarito (ou de --pdf), analisado como o programa faz."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    caminho = PDF_DE_FORA or (GABARITO / "paginas" / f"{pid}.pdf")
    projeto = Projeto(caminho_entrada=str(caminho), nome=pid)
    projeto = analisar_projeto(projeto)
    return projeto, abrir_pdf(projeto.caminho_entrada)


def _desenhar(doc, projeto, pagina, **campos) -> np.ndarray:
    """A página como sai no PDF, com os campos da página trocados só nesta
    conta (a página de verdade volta como estava)."""
    from core.pipeline import renderizar_pagina

    antes = {k: getattr(pagina, k) for k in campos}
    try:
        for k, v in campos.items():
            setattr(pagina, k, v)
        img, _mono = renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
        return img
    finally:
        for k, v in antes.items():
            setattr(pagina, k, v)


def _soma(img: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(img).tobytes() + str(img.shape).encode()).hexdigest()


def hashes(pid: str) -> dict:
    """As somas de cada página nos filtros comuns, tudo de fábrica."""
    from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO

    projeto, doc = abrir(pid)
    saida = {}
    try:
        for pagina in projeto.paginas_ativas:
            nome = pid if len(projeto.paginas_ativas) == 1 else f"{pid}-{pagina.metade}"
            for filtro in (ORIGINAL, PRETO_E_BRANCO, MELHORAR):
                saida[f"{nome}|{filtro}"] = _soma(_desenhar(doc, projeto, pagina, filtro=filtro))
    finally:
        doc.close()
    return saida


# ------------------------------------------------------------------ os itens

def variantes_2_8():
    """Item 2.8: o Automático (hoje) contra os do ScanTailor. Na página de
    cada um, só o algoritmo muda; filtro Preto e branco."""
    from core.filtros import PRETO_E_BRANCO
    from core import preto_e_branco_scantailor as pbst

    base = {"filtro": PRETO_E_BRANCO}
    lista = [("Hoje: Automático", dict(base, algoritmo_preto_branco="auto"))]
    for codigo in ("st_otsu", "st_sauvola", "st_wolf"):
        lista.append((pbst.NOMES_NA_TELA[codigo], dict(base, algoritmo_preto_branco=codigo)))
    return lista


def variantes_2_9():
    """Item 2.9: cada filtro sem e com a caixinha "Letra clara em fundo escuro"."""
    from core.filtros import MELHORAR, PRETO_E_BRANCO

    return [("Hoje: Preto e branco", {"filtro": PRETO_E_BRANCO, "claro_no_escuro": False}),
            ("Preto e branco + Letra clara", {"filtro": PRETO_E_BRANCO, "claro_no_escuro": True}),
            ("Hoje: Melhorar", {"filtro": MELHORAR, "claro_no_escuro": False}),
            ("Melhorar + Letra clara", {"filtro": MELHORAR, "claro_no_escuro": True})]


def variantes_2_11():
    """Item 2.11: as cores do ScanTailor no Preto e branco e no Melhorar."""
    from core.filtros import MELHORAR, PRETO_E_BRANCO

    return [("Hoje: Preto e branco", {"filtro": PRETO_E_BRANCO}),
            ("Letras com a cor delas", {"filtro": PRETO_E_BRANCO, "letras_com_a_cor": True}),
            ("Letras com a cor + Reduzir cores", {"filtro": PRETO_E_BRANCO, "letras_com_a_cor": True,
                                                  "reduzir_cores": True}),
            ("Melhorar + Reduzir cores", {"filtro": MELHORAR, "reduzir_cores": True})]


def variantes_2_12():
    """Item 2.12: o desentortar do ScanTailor, no Original (só a geometria) e
    no Preto e branco."""
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    return [("Hoje: Original", {"filtro": ORIGINAL, "desentortar": "desligado"}),
            ("Desentortar automático", {"filtro": ORIGINAL, "desentortar": "automatico"}),
            ("Desentortar pelas margens", {"filtro": ORIGINAL, "desentortar": "pelas_margens"}),
            ("Hoje: Preto e branco", {"filtro": PRETO_E_BRANCO, "desentortar": "desligado"}),
            ("Automático + Preto e branco", {"filtro": PRETO_E_BRANCO, "desentortar": "automatico"})]


ITENS = {"2.8": variantes_2_8, "2.9": variantes_2_9, "2.11": variantes_2_11, "2.12": variantes_2_12}


# ------------------------------------------------------------------ as imagens

def _texto(img: np.ndarray, texto: str, negrito: bool = True, tamanho: int = 26) -> np.ndarray:
    """Uma faixa branca com o texto em cima da imagem (Pillow, com acento)."""
    from PIL import Image, ImageDraw, ImageFont

    faixa = Image.new("RGB", (img.shape[1], tamanho + 16), "white")
    fonte = ImageFont.truetype(str(FONTE_NEGRITO if negrito else FONTE), tamanho)
    ImageDraw.Draw(faixa).text((8, 6), texto, fill="black", font=fonte)
    return np.vstack([cv2.cvtColor(np.asarray(faixa), cv2.COLOR_RGB2BGR), img])


def _bgr(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img


def _lado_a_lado(colunas: list[tuple[str, np.ndarray]], altura: int) -> np.ndarray:
    pedacos = []
    for nome, img in colunas:
        img = _bgr(img)
        escala = altura / img.shape[0]
        pequena = cv2.resize(img, (max(1, round(img.shape[1] * escala)), altura),
                             interpolation=cv2.INTER_AREA)
        pequena = cv2.copyMakeBorder(pequena, 0, 0, 0, 8, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        pedacos.append(_texto(pequena, nome, tamanho=max(16, altura // 45)))
    return np.hstack(pedacos)


def _onde_mais_muda(a: np.ndarray, b: np.ndarray, lado: int) -> tuple[int, int]:
    """O canto do quadrado de `lado` pontos onde a e b mais discordam."""
    diferenca = (cv2.absdiff(_cinza(a), _cinza(b)) > 64).astype(np.float32)
    if not diferenca.any():
        return (a.shape[0] - lado) // 2, (a.shape[1] - lado) // 2
    soma = cv2.boxFilter(diferenca, -1, (lado, lado), normalize=False)
    y, x = np.unravel_index(int(np.argmax(soma)), soma.shape)
    y0 = int(np.clip(y - lado // 2, 0, max(0, a.shape[0] - lado)))
    x0 = int(np.clip(x - lado // 2, 0, max(0, a.shape[1] - lado)))
    return y0, x0


def _cinza(img: np.ndarray) -> np.ndarray:
    return img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def rodada_do_item(pid: str, item: str, pasta: Path) -> dict:
    from core.filtros import ORIGINAL

    pasta.mkdir(parents=True, exist_ok=True)
    projeto, doc = abrir(pid)
    numeros = {}
    try:
        for pagina in projeto.paginas_ativas:
            nome = pid if len(projeto.paginas_ativas) == 1 else f"{pid}-{pagina.metade}"
            original = _desenhar(doc, projeto, pagina, filtro=ORIGINAL)
            colunas = [("Original", original)]
            tempos = {}
            falhou = {}
            for rotulo, campos in ITENS[item]():
                for _tentativa in range(2):
                    FALHAS.clear()
                    inicio = time.perf_counter()
                    img = _desenhar(doc, projeto, pagina, **campos)
                    tempos[rotulo] = round(time.perf_counter() - inicio, 2)
                    if not FALHAS:
                        break
                if FALHAS:
                    falhou[rotulo] = [str(f) for f in FALHAS]
                    rotulo = f"{rotulo} (NÃO RODOU)"
                colunas.append((rotulo, img))
            hoje = colunas[1][1]
            # a página inteira
            cv2.imwrite(str(pasta / f"{nome}-pagina.jpg"), _lado_a_lado(colunas, 1100),
                        [cv2.IMWRITE_JPEG_QUALITY, 88])
            # o recorte onde a primeira variante nova mais discorda de hoje
            lado = max(200, min(original.shape[:2]) // 4)
            y0, x0 = _onde_mais_muda(hoje, colunas[2][1], lado)
            recortes = [(n, im[y0:y0 + lado, x0:x0 + lado]) for n, im in colunas]
            cv2.imwrite(str(pasta / f"{nome}-recorte.png"), _lado_a_lado(recortes, 520))
            numeros[nome] = {
                "tamanho": [int(original.shape[1]), int(original.shape[0])],
                "dpi": projeto.qualidade_dpi,
                "recorte_xy_lado": [x0, y0, lado],
                "pontos_pretos": {n: int((_cinza(im) < 128).sum()) for n, im in colunas[1:]},
                "pontos_diferentes_de_hoje": {
                    n: int((cv2.absdiff(_cinza(hoje), _cinza(im)) > 64).sum()) for n, im in colunas[2:]},
                "segundos": tempos,
                "nao_rodou": falhou,
            }
    finally:
        doc.close()
    (pasta / f"{pid}.json").write_text(json.dumps(numeros, ensure_ascii=False, indent=1), encoding="utf-8")
    return numeros


def main() -> int:
    analisador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analisador.add_argument("pid")
    analisador.add_argument("--hashes", type=Path, help="grava as somas de fábrica neste .json (acrescenta)")
    analisador.add_argument("--item", choices=sorted(ITENS))
    analisador.add_argument("--pasta", type=Path)
    analisador.add_argument("--pdf", type=Path, help="PDF de fora do gabarito (ver PDF_DE_FORA)")
    opcoes = analisador.parse_args()
    global PDF_DE_FORA
    PDF_DE_FORA = opcoes.pdf
    _registrar_falhas()
    if opcoes.hashes:
        somas = json.loads(opcoes.hashes.read_text(encoding="utf-8")) if opcoes.hashes.is_file() else {}
        somas.update(hashes(opcoes.pid))
        opcoes.hashes.write_text(json.dumps(somas, indent=1, sort_keys=True), encoding="utf-8")
    if opcoes.item:
        print(json.dumps(rodada_do_item(opcoes.pid, opcoes.item, opcoes.pasta), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
