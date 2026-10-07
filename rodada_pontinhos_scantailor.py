"""Rodada lado a lado: limpar pontinhos de hoje x o do ScanTailor (item M4, 06/10/2026).

PARA QUÊ
    O Samuel (P7, 05/10/2026) quer VER, antes de decidir, o limpar pontinhos do
    ScanTailor (core/pontinhos_scantailor.py) ao lado do nosso. Este script
    monta, para cada página do gabarito, as imagens do teste de olho:

      - <página>-pagina.jpg: a página inteira, cinco colunas: Original · Preto
        e branco de hoje (com o nosso limpar pontinhos) · ScanTailor "pouco" ·
        "normal" · "muito";
      - <página>-recorte-1.png e -recorte-2.png: dois pedaços ampliados onde
        os jeitos de limpar mais discordam (o 2 é perto das letras: pingo do
        "i", acento, letra fina). Três linhas: Original, Hoje e "o que o nosso
        apagou"; os três do ScanTailor; e "o que cada um apagou" (em preto o
        que sumiu, em cinza claro o que ficou, numa imagem À PARTE - nada é
        desenhado por cima da página).

    E grava os números de cada página em dados/<página>.json (quantos pontos
    pretos cada um apagou, em quantos pedaços, e quanto tempo levou).

COMO O "PRETO E BRANCO DE HOJE" É FEITO
    Pelo caminho do programa: core.pipeline.analisar_projeto, a página
    preparada por renderizar_pagina na resolução do PDF (projeto.qualidade_dpi)
    com a marcação de gravura/letra/papel do programa, e o filtro
    core.filtros.aplicar_filtro_com_selecao (o que o pipeline._filtrar chama
    no Preto e branco sem "Só as letras"). Para os do ScanTailor, a MESMA
    conta, trocando só o limpar pontinhos do preto e branco das letras
    (core.filtros.filtro_preto_e_branco) pelo do ScanTailor, por um remendo
    temporário só dentro deste script. A cada página o script confere que o
    "hoje" feito assim é idêntico ao do programa.

    O DPI passado ao ScanTailor é o da página preparada (o que o programa
    passaria): projeto.qualidade_dpi reduzido por pdf_io.dpi_seguro.

USO (da pasta do projeto; uma página por processo, por causa da memória)
    .venv\\Scripts\\python.exe rodada_pontinhos_scantailor.py horas_p026 --imagens
    .venv\\Scripts\\python.exe rodada_pontinhos_scantailor.py horas_p026          (só os números)

Lê o gabarito (somente leitura). A pasta de dados do programa (LOCALAPPDATA)
vai para uma pasta temporária: nada é escrito na pasta real do Samuel.

Seguro mudar: tamanhos e textos das imagens. Arriscado mudar: _resultados
(tem de ser o caminho do programa, senão o lado a lado mostra outra coisa).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
GABARITO = RAIZ / "gabarito"
PASTA = RAIZ / "relatorios" / "conferir" / "limpar-pontinhos-2026-10-06"

_DADOS = Path(tempfile.gettempdir()) / "pontinhos_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import filtros as F  # noqa: E402
from core import pontinhos_scantailor as ps  # noqa: E402

FORCAS = ("pouco", "normal", "muito")
FONTE = Path(r"C:\Windows\Fonts\segoeui.ttf")
FONTE_NEGRITO = Path(r"C:\Windows\Fonts\segoeuib.ttf")


# ------------------------------------------------------------------ a página

def preparar(pid: str):
    """[(nome, img, selecao, pagina, projeto, dpi)] das páginas ativas do PDF do gabarito."""
    from core.filtros import ORIGINAL, PRETO_E_BRANCO
    from core.pdf_io import abrir_pdf, dpi_seguro
    from core.pipeline import analisar_projeto, renderizar_pagina
    from modelos import Projeto

    projeto = Projeto(caminho_entrada=str(GABARITO / "paginas" / f"{pid}.pdf"), nome=pid)
    projeto.filtro_padrao = PRETO_E_BRANCO
    projeto = analisar_projeto(projeto)
    doc = abrir_pdf(projeto.caminho_entrada)
    saida = []
    try:
        ativas = list(projeto.paginas_ativas)
        for pagina in ativas:
            folha = projeto.folhas[pagina.folha]
            dpi = dpi_seguro(doc[folha.indice], projeto.qualidade_dpi)
            pagina.filtro = ORIGINAL
            img, _ = renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
            pagina.filtro = PRETO_E_BRANCO
            nome = pid if len(ativas) == 1 else f"{pid}-{pagina.metade}"
            saida.append((nome, img, pagina.obter_selecao(), pagina, projeto, dpi))
    finally:
        doc.close()
    return saida


@contextmanager
def _preto_e_branco_das_letras(binaria_pronta: np.ndarray):
    """Faz o filtro_preto_e_branco devolver `binaria_pronta` (remendo SÓ deste script)."""
    original = F.filtro_preto_e_branco
    F.filtro_preto_e_branco = lambda *a, **k: binaria_pronta
    try:
        yield
    finally:
        F.filtro_preto_e_branco = original


def _filtro(img, selecao, pagina, projeto, despeckle=True):
    """O Preto e branco do programa (como core.pipeline._filtrar sem "Só as letras")."""
    saida, _mono = F.aplicar_filtro_com_selecao(
        img, F.PRETO_E_BRANCO, selecao, pagina.forca_preto, pagina.clareza_melhorar,
        pagina.intensidade_magico, algoritmo_pb=pagina.algoritmo_preto_branco, despeckle=despeckle,
        decoracao_em_preto_e_branco=bool(getattr(projeto, "pb_decoracao_em_preto_e_branco", False)))
    return saida


def _cinza(img):
    return img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def _pedacos(mascara: np.ndarray) -> int:
    if not mascara.any():
        return 0
    n, _ = cv2.connectedComponents(mascara.astype(np.uint8), connectivity=8)
    return int(n - 1)


def _resultados(img, selecao, pagina, projeto, dpi):
    """As letras em preto e branco antes de limpar, os quatro jeitos de limpar,
    a página inteira de cada um, os números e os tempos."""
    inicio = time.perf_counter()
    sem = F.filtro_preto_e_branco(img, forca=pagina.forca_preto, despeckle=False,
                                  algoritmo=pagina.algoritmo_preto_branco)
    t_pb = time.perf_counter() - inicio

    inicio = time.perf_counter()
    nosso = F._despeckle(sem, sem.shape[0])
    t_nosso = time.perf_counter() - inicio
    letras = {"hoje": nosso}
    tempos = {"preto_e_branco_sem_limpar": t_pb, "nosso": t_nosso}
    for forca in FORCAS:
        r = ps.limpar_pontinhos(sem, dpi, forca)
        if not r.disponivel:
            raise SystemExit(f"o do ScanTailor não rodou: {r.motivo} ({r.detalhe_tecnico})")
        letras[forca] = r.imagem
        tempos[forca] = r.segundos

    paginas = {}
    for nome, binaria in letras.items():
        with _preto_e_branco_das_letras(binaria):
            paginas[nome] = _filtro(img, selecao, pagina, projeto)
    # prova: o "hoje" daqui é o do programa
    do_programa = _filtro(img, selecao, pagina, projeto)
    if not np.array_equal(do_programa, paginas["hoje"]):
        raise SystemExit("o Preto e branco de hoje feito pelo script NÃO bate com o do programa")

    # O que cada um apagou NA PÁGINA QUE SAI (depois da gravura, da foto e da
    # moldura, que não passam pelo limpar pontinhos das letras): comparado com
    # a mesma página sem limpar nada. Medido no preto e branco intermediário,
    # a moldura colorida da Horas 47 parecia cheia de diferença que não aparece.
    with _preto_e_branco_das_letras(sem):
        pagina_sem = _cinza(_filtro(img, selecao, pagina, projeto)) < 128
    tirado = {nome: pagina_sem & (_cinza(p) >= 128) for nome, p in paginas.items()}
    nas_letras = {nome: int(((sem == 0) & (b == 255)).sum()) for nome, b in letras.items()}
    numeros = {
        "dpi": dpi, "tamanho": [int(img.shape[1]), int(img.shape[0])],
        "pontos_pretos_antes": int(pagina_sem.sum()),
        "pedacos_antes": _pedacos(pagina_sem),
        "apagou_pontos_no_preto_e_branco_das_letras": nas_letras,
        "apagou_pontos": {n: int(t.sum()) for n, t in tirado.items()},
        "apagou_pedacos": {n: _pedacos(t) for n, t in tirado.items()},
        "so_o_scantailor_apagou_pedacos": {f: _pedacos(tirado[f] & ~tirado["hoje"]) for f in FORCAS},
        "so_o_nosso_apagou_pedacos": {f: _pedacos(tirado["hoje"] & ~tirado[f]) for f in FORCAS},
        "segundos": tempos,
        "pagina_tem_gravura": bool(selecao is not None and not getattr(selecao, "vazia", True)),
    }
    # Só para informar (não vira imagem): nos PDFs que dizem 72 DPI sem ser, a
    # página é desenhada maior que o papel; com o DPI que o NOSSO limpar
    # pontinhos supõe (altura / 10 polegadas, ver core.filtros._despeckle), o
    # do ScanTailor apagaria isto:
    suposto = int(min(2400, max(30, round(sem.shape[0] / 10))))
    if abs(suposto - dpi) > 0.25 * dpi:
        numeros["dpi_pela_altura"] = suposto
        numeros["apagou_pontos_dpi_pela_altura"] = {
            f: int(((sem == 0) & (ps.limpar_pontinhos(sem, suposto, f).imagem == 255)).sum())
            for f in FORCAS}
    # a página sem limpar, em 0 (preto) e 255, como o resto deste script espera
    return np.where(pagina_sem, 0, 255).astype(np.uint8), letras, paginas, tirado, numeros


# ------------------------------------------------------------------ as imagens

def _fonte(tamanho: int, negrito: bool = False):
    from PIL import ImageFont

    caminho = FONTE_NEGRITO if negrito and FONTE_NEGRITO.is_file() else FONTE
    try:
        return ImageFont.truetype(str(caminho), tamanho)
    except OSError:
        return ImageFont.load_default()


def _com_rotulo(tile_bgr: np.ndarray, texto: str, faixa: int = 46) -> np.ndarray:
    """O rótulo numa faixa branca EM CIMA da imagem (nunca por cima do conteúdo)."""
    from PIL import Image, ImageDraw

    h, w = tile_bgr.shape[:2]
    fundo = Image.new("RGB", (w, h + faixa), (255, 255, 255))
    fundo.paste(Image.fromarray(cv2.cvtColor(tile_bgr, cv2.COLOR_BGR2RGB)), (0, faixa))
    desenho = ImageDraw.Draw(fundo)
    desenho.text((8, 8), texto, fill=(20, 20, 20), font=_fonte(26, negrito=True))
    return cv2.cvtColor(np.asarray(fundo), cv2.COLOR_RGB2BGR)


def _bgr(img):
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img


def _grade(linhas: list[list[np.ndarray]], vao: int = 22) -> np.ndarray:
    """Os quadros lado a lado, separados por uma faixa CINZA (com fundo branco,
    duas páginas em preto e branco coladas pareciam uma só)."""
    altura_linha = [max(t.shape[0] for t in linha) for linha in linhas]
    largura = max(sum(t.shape[1] for t in linha) + vao * (len(linha) - 1) for linha in linhas)
    tela = np.full((sum(altura_linha) + vao * (len(linhas) - 1), largura, 3), 150, np.uint8)
    y = 0
    for linha, h in zip(linhas, altura_linha):
        x = 0
        for t in linha:
            tela[y:y + t.shape[0], x:x + t.shape[1]] = t
            x += t.shape[1] + vao
        y += h + vao
    return tela


def _onde(caixa, forma) -> str:
    """'no alto, à esquerda' etc., pelo centro do recorte."""
    y0, x0, h, w = caixa
    cy, cx = (y0 + h / 2) / forma[0], (x0 + w / 2) / forma[1]
    vertical = "no alto" if cy < 0.34 else ("no meio" if cy < 0.67 else "embaixo")
    horizontal = "à esquerda" if cx < 0.34 else ("no centro" if cx < 0.67 else "à direita")
    return f"{vertical}, {horizontal}"


def _melhor_janela(mapa: np.ndarray, h: int, w: int, proibido=None):
    """(y0, x0) da janela h x w com mais pontos em `mapa` (em escala reduzida, rápido)."""
    passo = max(1, min(h, w) // 12)
    pequeno = cv2.resize(mapa.astype(np.float32), (max(1, mapa.shape[1] // passo),
                                                    max(1, mapa.shape[0] // passo)),
                         interpolation=cv2.INTER_AREA)
    kh, kw = max(1, h // passo), max(1, w // passo)
    soma = cv2.boxFilter(pequeno, -1, (kw, kh), normalize=False, borderType=cv2.BORDER_CONSTANT)
    if proibido is not None:
        py0, px0, ph, pw = proibido
        y0 = max(0, (py0 - h) // passo)
        x0 = max(0, (px0 - w) // passo)
        soma[y0:(py0 + ph + h) // passo + 1, x0:(px0 + pw + w) // passo + 1] = -1
    if soma.max() <= 0:
        return None
    cy, cx = np.unravel_index(int(np.argmax(soma)), soma.shape)
    y = int(np.clip(cy * passo + passo // 2 - h // 2, 0, mapa.shape[0] - h))
    x = int(np.clip(cx * passo + passo // 2 - w // 2, 0, mapa.shape[1] - w))
    return y, x


def _recortes(sem, tirado, forma):
    """Até duas caixas (y, x, h, w): onde os jeitos discordam; e perto das letras."""
    altura = forma[0]
    h = max(60, round(altura * 0.055))
    w = round(h * 4 / 3)
    discorda = np.zeros(forma, bool)
    for f in FORCAS:
        discorda |= tirado[f] ^ tirado["hoje"]
    discorda |= tirado["muito"] & ~tirado["pouco"]
    # perto das letras: em volta das peças grandes (as que nenhum jeito apaga)
    grande = (sem == 0) & ~tirado["muito"] & ~tirado["hoje"]
    raio = max(3, round(altura * 0.006))
    perto = cv2.dilate(grande.astype(np.uint8), cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1))) > 0
    caixas = []
    p1 = _melhor_janela(discorda, h, w)
    if p1 is not None:
        caixas.append((p1[0], p1[1], h, w))
    p2 = _melhor_janela(discorda & perto, h, w, proibido=caixas[0] if caixas else None)
    if p2 is not None:
        caixas.append((p2[0], p2[1], h, w))
    if not caixas:     # nada apagado em lugar nenhum: o pedaço com mais letra
        p = _melhor_janela(sem == 0, h, w)
        caixas.append((p[0], p[1], h, w))
    return caixas


TILE_L, TILE_A = 600, 450


def _ampliar(pedaco: np.ndarray, colorido: bool) -> np.ndarray:
    return cv2.resize(_bgr(pedaco), (TILE_L, TILE_A),
                      interpolation=cv2.INTER_LINEAR if colorido else cv2.INTER_NEAREST)


def _o_que_apagou(sem_pedaco: np.ndarray, tirado_pedaco: np.ndarray) -> np.ndarray:
    """Imagem À PARTE (já do tamanho do quadro): em cinza claro a tinta que
    ficou; em preto o que foi apagado, ENGROSSADO (um ponto apagado tem 1 a 4
    pontos e sumiria no quadro; o rótulo avisa)."""
    tela = np.full((TILE_A, TILE_L), 255, np.uint8)
    ficou = cv2.resize((sem_pedaco == 0).astype(np.uint8), (TILE_L, TILE_A),
                       interpolation=cv2.INTER_NEAREST) > 0
    tela[ficou] = 215
    apagado = cv2.resize(tirado_pedaco.astype(np.uint8), (TILE_L, TILE_A),
                         interpolation=cv2.INTER_NEAREST)
    apagado = cv2.dilate(apagado, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    tela[apagado > 0] = 0
    return tela


def gravar_imagens(nome, img, sem, paginas, tirado, numeros, pasta: Path) -> list[dict]:
    pasta.mkdir(parents=True, exist_ok=True)
    rotulos = {"hoje": "Hoje (o nosso)", "pouco": "ScanTailor: pouco",
               "normal": "ScanTailor: normal", "muito": "ScanTailor: muito"}
    # a página inteira, 5 colunas
    alt = 1000
    def reduzir(i):
        f = alt / i.shape[0]
        return cv2.resize(_bgr(i), (round(i.shape[1] * f), alt), interpolation=cv2.INTER_AREA)
    colunas = [_com_rotulo(reduzir(img), "Original")]
    colunas += [_com_rotulo(reduzir(paginas[n]), rotulos[n]) for n in ("hoje", *FORCAS)]
    cv2.imwrite(str(pasta / f"{nome}-pagina.jpg"), _grade([colunas]), [cv2.IMWRITE_JPEG_QUALITY, 90])

    feitos = []
    for i, (y, x, h, w) in enumerate(_recortes(sem, tirado, sem.shape), start=1):
        corte = (slice(y, y + h), slice(x, x + w))
        def t(n):
            return _com_rotulo(_ampliar(paginas[n][corte], False), rotulos[n])
        def apagou(n, texto):
            return _com_rotulo(_bgr(_o_que_apagou(sem[corte], tirado[n][corte])), texto)
        grade = _grade([
            [_com_rotulo(_ampliar(img[corte], True), "Original"), t("hoje"),
             apagou("hoje", "O que o nosso apagou (engrossado)")],
            [t("pouco"), t("normal"), t("muito")],
            [apagou("pouco", "O que o \"pouco\" apagou (engrossado)"),
             apagou("normal", "O que o \"normal\" apagou (engrossado)"),
             apagou("muito", "O que o \"muito\" apagou (engrossado)")],
        ])
        arquivo = pasta / f"{nome}-recorte-{i}.png"
        cv2.imwrite(str(arquivo), grade)
        feitos.append({"arquivo": arquivo.name, "onde": _onde((y, x, h, w), sem.shape),
                       "caixa": [int(x), int(y), int(w), int(h)],
                       "apagou_pontos_no_recorte": {n: int(tirado[n][corte].sum())
                                                    for n in ("hoje", *FORCAS)}})
    return feitos


# ------------------------------------------------------------------ principal

def main(argv=None) -> int:
    analisador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analisador.add_argument("paginas", nargs="+", help="ids do gabarito (ex.: horas_p026)")
    analisador.add_argument("--imagens", action="store_true", help="grava também as imagens")
    opcoes = analisador.parse_args(argv)

    (PASTA / "dados").mkdir(parents=True, exist_ok=True)
    for pid in opcoes.paginas:
        inicio = time.perf_counter()
        for nome, img, selecao, pagina, projeto, dpi in preparar(pid):
            sem, letras, paginas, tirado, numeros = _resultados(img, selecao, pagina, projeto, dpi)
            if opcoes.imagens:
                numeros["recortes"] = gravar_imagens(nome, img, sem, paginas, tirado, numeros,
                                                     PASTA / "imagens")
            (PASTA / "dados" / f"{nome}.json").write_text(
                json.dumps(numeros, ensure_ascii=False, indent=1), encoding="utf-8")
            a = numeros["apagou_pontos"]
            print(f"{nome}: {dpi} DPI, apagou nosso {a['hoje']} / pouco {a['pouco']} / "
                  f"normal {a['normal']} / muito {a['muito']} pontos; ScanTailor "
                  + " / ".join(f"{numeros['segundos'][f]:.2f}" for f in FORCAS) + " s; "
                  f"nosso {numeros['segundos']['nosso']:.2f} s ({time.perf_counter() - inicio:.0f} s no total)",
                  flush=True)
            del sem, letras, paginas, tirado
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
