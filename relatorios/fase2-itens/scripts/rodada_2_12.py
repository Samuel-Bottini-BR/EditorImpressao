"""Antes/depois do item 2.12 (desentortar) pelo caminho inteiro do programa, com régua (22/10/2026).

PARA QUÊ
    As fotos para o Samuel depois do conserto "cortar uma vez só, no fim"
    (opção A da Central, 22/10/2026). Regras dele (CLAUDE.md §4.10): caminho
    inteiro do programa, cada foto dizendo o caminho e as opções, só páginas
    que vão ser impressas. Pedido da gerente: uma RÉGUA reta fina por cima das
    linhas, nas fotos de antes e de depois, para ver se ficaram retas.

O CAMINHO
    Uma página do acervo (somente leitura) é copiada para um PDF de rascunho
    (com o giro de 90 em 90 que o livro precisa, como o Kaique faria) e passa
    por core.pipeline: analisar_projeto (livro novo, de fábrica) ->
    renderizar_pagina na resolução do PDF: girar -> dividir -> endireitar ->
    cortar -> desentortar -> filtro.

AS COLUNAS
    Hoje (desligado, Original) · Antes do conserto: automático (o desentortar de
    21/10, na página já cortada: o mesmo desentortar chamado sem o papel em
    volta, core.desentortar_scantailor.aplicar, que é o que o código de 21/10
    fazia) · Agora: automático · Agora: pelas margens · Hoje: Preto e branco ·
    Agora: automático + Preto e branco.

A RÉGUA
    Linhas vermelhas finas, retas de beirada a beirada, no pé das linhas de
    texto medido na faixa do MEIO da página (longe da lombada), uma a cada
    poucas linhas. Linha curva perto da lombada se afasta da régua; linha reta
    acompanha.

Uso (da worktree):
    python rodada_2_12.py <nome> "<livro.pdf>" <página do PDF, de 1> <giro> <dividir 0/1> <metade> <pasta>
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
os.environ["LOCALAPPDATA"] = tempfile.mkdtemp(prefix="rodada_2_12_")
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import fitz  # noqa: E402
import numpy as np  # noqa: E402

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
FONTE = Path(r"C:\Windows\Fonts\segoeui.ttf")
FONTE_NEGRITO = Path(r"C:\Windows\Fonts\segoeuib.ttf")
NOME_DA_METADE = {"inteira": "página única", "esquerda": "página da esquerda", "direita": "página da direita"}


def _pdf_de_uma_pagina(livro: str, indice: int, giro: int, pasta: Path) -> Path:
    destino = pasta / "pagina.pdf"
    origem, novo = fitz.open(ACERVO / livro), fitz.open()
    novo.insert_pdf(origem, from_page=indice, to_page=indice)
    if giro:
        novo[0].set_rotation((novo[0].rotation + giro) % 360)
    novo.save(destino)
    novo.close()
    origem.close()
    return destino


def _desenhar(doc, projeto, pagina, **campos):
    from core.pipeline import renderizar_pagina

    antes = {k: getattr(pagina, k) for k in campos}
    try:
        for k, v in campos.items():
            setattr(pagina, k, v)
        return renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)[0]
    finally:
        for k, v in antes.items():
            setattr(pagina, k, v)


def _bgr(img):
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img


def pes_das_linhas(img: np.ndarray, cada: int = 4) -> list[int]:
    """O pé (y) das linhas de texto medido numa faixa perto do meio (a de mais
    tinta entre 30-45%, 42-58% e 55-70% da largura: em página de duas colunas
    a do meio cai no vão), uma a cada `cada` linhas."""
    cinza = cv2.cvtColor(_bgr(img), cv2.COLOR_BGR2GRAY)
    largura = cinza.shape[1]
    faixas = [cinza[:, int(largura * a):int(largura * b)] < 128 for a, b in ((0.3, 0.45), (0.42, 0.58), (0.55, 0.7))]
    faixa = max(faixas, key=lambda f: float(f.mean()) if f.mean() < 0.5 else 0.0)
    perfil = faixa.mean(axis=1)
    perfil[perfil > 0.6] = 0  # a faixa preta do scanner não é linha
    tem = perfil > 0.04
    pes, y = [], 0
    while y < len(tem):
        if tem[y]:
            inicio = y
            while y < len(tem) and tem[y]:
                y += 1
            if y - inicio >= 6:
                pes.append(y)
        y += 1
    return pes[::cada]


def com_a_regua(img: np.ndarray) -> np.ndarray:
    saida = _bgr(img).copy()
    espessura = max(1, img.shape[0] // 1200)
    for y in pes_das_linhas(img):
        cv2.line(saida, (0, y), (saida.shape[1] - 1, y), (0, 0, 230), espessura)
    return saida


def _faixa_de_texto(largura: int, linhas: list[tuple[str, bool]], tamanho: int):
    from PIL import Image, ImageDraw, ImageFont

    altura = sum(tamanho + 10 for _ in linhas) + 8
    faixa = Image.new("RGB", (largura, altura), "white")
    desenho = ImageDraw.Draw(faixa)
    y = 4
    for texto, negrito in linhas:
        fonte = ImageFont.truetype(str(FONTE_NEGRITO if negrito else FONTE), tamanho)
        desenho.text((8, y), texto, fill="black", font=fonte)
        y += tamanho + 10
    return cv2.cvtColor(np.asarray(faixa), cv2.COLOR_RGB2BGR)


def _painel(titulo: list[str], colunas: list[tuple[str, str, np.ndarray]], altura: int) -> np.ndarray:
    pedacos = []
    tamanho = max(15, altura // 50)
    for nome, opcoes, img in colunas:
        img = _bgr(img)
        escala = altura / img.shape[0]
        pequena = cv2.resize(img, (max(1, round(img.shape[1] * escala)), altura), interpolation=cv2.INTER_AREA)
        pequena = cv2.copyMakeBorder(pequena, 0, 0, 0, 10, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        rotulo = _faixa_de_texto(pequena.shape[1], [(nome, True), (opcoes, False)], tamanho)
        pedacos.append(np.vstack([rotulo, pequena]))
    corpo = np.hstack(pedacos)
    topo = _faixa_de_texto(corpo.shape[1], [(t, i == 0) for i, t in enumerate(titulo)], tamanho + 4)
    return np.vstack([topo, corpo])


def _onde_mais_muda(a, b, lado):
    ca = cv2.cvtColor(_bgr(a), cv2.COLOR_BGR2GRAY)
    cb = cv2.cvtColor(_bgr(b), cv2.COLOR_BGR2GRAY)
    if ca.shape != cb.shape:
        return 0, 0
    diferenca = (cv2.absdiff(ca, cb) > 64).astype(np.float32)
    soma = cv2.boxFilter(diferenca, -1, (lado, lado), normalize=False)
    y, x = np.unravel_index(int(np.argmax(soma)), soma.shape)
    return (int(np.clip(y - lado // 2, 0, max(0, ca.shape[0] - lado))),
            int(np.clip(x - lado // 2, 0, max(0, ca.shape[1] - lado))))


def rodar(nome: str, livro: str, pagina_pdf: int, giro: int, dividir: bool, metade: str, pasta: Path,
          dpi_real: float = 0.0) -> dict:
    from core import desentortar_scantailor as ds
    from core.filtros import ORIGINAL, PRETO_E_BRANCO
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    pasta.mkdir(parents=True, exist_ok=True)
    rascunho = Path(tempfile.mkdtemp(prefix="pagina_2_12_"))
    pdf = _pdf_de_uma_pagina(livro, pagina_pdf - 1, giro, rascunho)
    projeto = analisar_projeto(Projeto(caminho_entrada=str(pdf), nome=nome, dividir_folhas=dividir))
    doc = abrir_pdf(str(pdf))
    try:
        paginas = [p for p in projeto.paginas_ativas if p.metade == metade]
        if not paginas:
            raise SystemExit(f"sem a {metade}: {[p.metade for p in projeto.paginas_ativas]}")
        pagina = paginas[0]
        folha = projeto.folhas[pagina.folha]
        tempos = {}

        def medir(rotulo, **campos):
            inicio = time.perf_counter()
            img = _desenhar(doc, projeto, pagina, **campos)
            tempos[rotulo] = round(time.perf_counter() - inicio, 2)
            return img

        from core import analise

        def com_aviso(rotulo, **campos):
            img = medir(rotulo, **campos)
            return img, analise.DESENTORTAR_SAIU_SEM in pagina.alertas

        hoje = medir("hoje", filtro=ORIGINAL, desentortar=ds.DESLIGADO)
        auto, aviso_auto = com_aviso("auto", filtro=ORIGINAL, desentortar=ds.AUTOMATICO)
        maior = medir("aumentar", filtro=ORIGINAL, desentortar=ds.AUTOMATICO, desentortar_aumentar=True)
        margens, aviso_margens = com_aviso("margens", filtro=ORIGINAL, desentortar=ds.PELAS_MARGENS)
        pb_hoje = medir("pb", filtro=PRETO_E_BRANCO, desentortar=ds.DESLIGADO)
        pb_auto = medir("pb_auto", filtro=PRETO_E_BRANCO, desentortar=ds.AUTOMATICO)
        # antes da protecao (o 177f711): o mesmo caminho, com a protecao sem recusar nunca
        recusar = ds.recusar
        ds.recusar = lambda pecas, fundo: False
        try:
            antes = medir("antes", filtro=ORIGINAL, desentortar=ds.AUTOMATICO)
        finally:
            ds.recusar = recusar
        # so para mostrar a causa (pergunta P4): o desentortar ouvindo o tamanho de verdade da pagina
        real = None
        if dpi_real:
            preparar = ds.preparar_no_corte
            ds.preparar_no_corte = lambda reta, caixa, pag, dpi=None, **k: preparar(reta, caixa, pag, dpi_real, **k)
            try:
                real, aviso_real = com_aviso("real", filtro=ORIGINAL, desentortar=ds.AUTOMATICO)
            finally:
                ds.preparar_no_corte = preparar
    finally:
        doc.close()

    caminho = (f"Livro novo, ajustes de fábrica: girar {giro}° → " if giro else "Livro novo, ajustes de fábrica: ") +         ("dividir (ligado no livro) → " if dividir else "") + "endireitar → cortar → desentortar → filtro"
    titulo = [f"{Path(livro).stem.split(' - ')[0][:60]}, página {pagina_pdf} do PDF, {NOME_DA_METADE[metade]}",
              caminho, "Régua vermelha: reta, no pé das linhas do meio da página"]

    def sai(aviso):
        return " · foi para o Para revisar" if aviso else ""

    colunas = [
        ("Hoje", "desentortar desligado · Original", hoje),
        ("Antes da proteção", "automático, sem proteção · Original", antes),
        ("Agora", "automático · Original" + sai(aviso_auto), auto),
        ("Agora, com o botão", "Desentortar aumentando a página · Original", maior),
        ("Agora", "pelas margens · Original" + sai(aviso_margens), margens),
        ("Hoje", "desentortar desligado · Preto e branco", pb_hoje),
        ("Agora", "automático · Preto e branco", pb_auto),
    ]
    if real is not None:
        colunas.append((f"Só para mostrar a causa", f"automático com o tamanho certo ({dpi_real:.0f} DPI)" + sai(aviso_real), real))
    com = [(n, o, com_a_regua(i)) for n, o, i in colunas]
    cv2.imwrite(str(pasta / f"{nome}-pagina.jpg"), _painel(titulo, com, 1300), [cv2.IMWRITE_JPEG_QUALITY, 88])
    lado = max(300, min(hoje.shape[:2]) // 3)
    y0, x0 = _onde_mais_muda(hoje, antes if antes.shape == hoje.shape else auto, lado)
    recortes = [(n, o, i[y0:y0 + lado, x0:x0 + lado]) for n, o, i in com]
    cv2.imwrite(str(pasta / f"{nome}-recorte.jpg"),
                _painel(titulo + [f"ampliado: o quadrado de {lado} pontos onde o automático sem proteção mais muda"],
                        recortes, 700), [cv2.IMWRITE_JPEG_QUALITY, 90])

    def cinza(i):
        return cv2.cvtColor(_bgr(i), cv2.COLOR_BGR2GRAY)

    numeros = {
        "livro": livro, "pagina_pdf": pagina_pdf, "metade": metade, "giro": giro, "dividir": dividir,
        "rotacao_da_folha": folha.rotacao, "tamanho": list(hoje.shape[:2]), "dpi": projeto.qualidade_dpi,
        "pontos_diferentes_de_hoje": {
            n: int((cv2.absdiff(cinza(hoje), cinza(i)) > 64).sum()) if i.shape[:2] == hoje.shape[:2] else None
            for n, i in (("antes_auto", antes), ("auto", auto), ("margens", margens), ("aumentar", maior))},
        "foi_para_revisar": {"auto": aviso_auto, "margens": aviso_margens},
        "tamanho_aumentado": list(maior.shape[:2]),
        "segundos": tempos,
    }
    (pasta / f"{nome}.json").write_text(json.dumps(numeros, ensure_ascii=False, indent=1), encoding="utf-8")
    return numeros


if __name__ == "__main__":
    a = sys.argv[1:]
    print(json.dumps(rodar(a[0], a[1], int(a[2]), int(a[3]), a[4] == "1", a[5], Path(a[6]),
                           float(a[7]) if len(a) > 7 else 0.0), ensure_ascii=False))
