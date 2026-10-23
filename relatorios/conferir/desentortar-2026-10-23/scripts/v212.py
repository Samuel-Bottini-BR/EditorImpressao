"""Verificador d212 (23/10/2026): item 2.12, desentortar a página curva perto da lombada.

Roteiro do verificador (não do implementador). Cada página passa pelo caminho inteiro do
programa (core.pipeline.analisar_projeto + processar, o mesmo do botão "Processar"):
(girar) -> (dividir) -> endireitar -> cortar -> [desentortar] -> filtro -> PDF.
As contas usam a imagem guardada dentro do PDF de saída.

USO (um modo por processo; --raiz = a worktree do código que se quer rodar):
    python v212.py somas   --raiz <wt> <saida.json>     32 páginas do gabarito x 3 filtros, de fábrica
    python v212.py ligado  --raiz <wt> <pasta>  [casos]  páginas curvas: desligado / ligado / com o botão
    python v212.py previa  --raiz <wt> <pasta>  [casos]  a prévia Rápida (110 DPI) contra o PDF
    python v212.py reabrir --raiz <wt> <pasta>           projeto gravado e aberto de novo
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

AQUI = Path(__file__).resolve()
_DADOS = Path(tempfile.gettempdir()) / "v212_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
LPE = Path(r"D:\Livros para editar")
DSI = LPE / "2 - TEOLOGIA" / "Doutrina Social da Igreja" / \
    "Corporativismo, Integralismo, Distributismo e Municipalismo à luz da DSI"

# nome: (livro, página do PDF (de 1), giro, dividir, metade, modo, descrição)
CASOS = {
    "destino18": (DSI / "9 - Octávio de Faria" / "Destino do socialismo - Octavio de faria.pdf", 18, 0, True,
                  "direita", "automatico", "Destino do socialismo, p. 18 do PDF, página da direita"),
    "righetti96": (ACERVO / "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf", 96, 270,
                   True, "direita", "automatico", "Righetti, p. 96 do PDF, página da direita"),
    "cursus176": (ACERVO / "Cursus philosophicus. Tomo.2.pdf", 176, 0, False, "inteira", "automatico",
                  "Cursus philosophicus, p. 176"),
    "cursus176m": (ACERVO / "Cursus philosophicus. Tomo.2.pdf", 176, 0, False, "inteira", "pelas_margens",
                   "Cursus philosophicus, p. 176 (pelas margens)"),
    "cursus151": (ACERVO / "Cursus philosophicus. Tomo.2.pdf", 151, 0, False, "inteira", "automatico",
                  "Cursus philosophicus, p. 151"),
    "matematica65": (ACERVO / "Matemática Para vencer.pdf", 65, 0, False, "inteira", "automatico",
                     "Matemática para vencer, p. 65"),
    "matematica31": (ACERVO / "Matemática Para vencer.pdf", 31, 0, False, "inteira", "automatico",
                     "Matemática para vencer, p. 31"),
    "marial41": (ACERVO / "Marial de sermoens - Frei Balthasar Paez. (1).pdf", 41, 0, False, "inteira",
                 "automatico", "Marial de sermões, p. 41"),
    "razoes57": (DSI / "22 - Olbiano de Mello" / "Razões do Integralismo [1935] - Olbiano de Mello.pdf", 57, 0,
                 False, "inteira", "automatico", "Razões do Integralismo, p. 57 (foto de celular)"),
    "ramirez155": (LPE / "3 - TOMISMO" / "Santiago RamÃ_rez - De Analogia - 4.pdf", 155, 0, True, "direita",
                   "automatico", "Santiago Ramírez, De Analogia 4, p. 155, direita (foto de celular)"),
    # página curva FEITA por mim: uma página reta do gabarito com as linhas encurvadas perto da
    # lombada (ver m_sintetica). Mostra se o desentortar endireita quando a curva é de verdade.
    "curvada": (None, 1, 0, False, "inteira", "automatico",
                "Página de teste: Marial 41 encurvada por mim (as linhas de cima e de baixo abrem em arco perto da lombada)"),
    "curvada3": (None, 1, 0, False, "inteira", "automatico",
                 "Página de teste: Righetti 96 (página limpa, sem faixa preta) encurvada por mim perto da lombada"),
    "curvada2": (None, 1, 0, False, "inteira", "automatico",
                 "Página de teste: Marial 41 encurvada por mim (todas as linhas sobem perto da lombada, como livro grosso)"),
}


def _livro(nome):
    livro = CASOS[nome][0]
    if livro is None:
        return Path(_SINTETICA.replace("curvada.pdf", nome + ".pdf"))
    return livro


_SINTETICA = str(_DADOS / "curvada.pdf")


def _pdf_de_uma_pagina(livro: Path, indice: int, giro: int, pasta: Path) -> Path:
    import fitz
    destino = pasta / "pagina.pdf"
    with fitz.open(str(livro)) as origem, fitz.open() as novo:
        novo.insert_pdf(origem, from_page=indice, to_page=indice)
        if giro:
            novo[0].set_rotation((novo[0].rotation + giro) % 360)
        novo.save(str(destino))
    return destino


def _projeto(entrada: Path, saida: Path, dividir=False, filtro=None):
    from core.pipeline import analisar_projeto
    from modelos import Projeto
    projeto = analisar_projeto(Projeto(caminho_entrada=str(entrada), caminho_saida=str(saida),
                                       nome=entrada.stem, dividir_folhas=dividir))
    if filtro is not None:
        projeto.filtro_padrao = filtro
        for p in projeto.paginas:
            p.filtro = filtro
    return projeto


def _somas_pdf(pdf: Path) -> list[str]:
    import fitz
    out = []
    with fitz.open(str(pdf)) as doc:
        for pagina in doc:
            h = hashlib.sha256(f"{pagina.rect.width:.3f}x{pagina.rect.height:.3f}".encode())
            for info in pagina.get_images(full=True):
                pix = fitz.Pixmap(doc, info[0])
                h.update(f"{pix.width}x{pix.height}x{pix.n}".encode())
                h.update(pix.samples)
            out.append(h.hexdigest())
    return out


def _imagens_pdf(pdf: Path):
    """A maior imagem de cada página do PDF, em BGR, no tamanho guardado."""
    import cv2
    import fitz
    import numpy as np
    res = []
    with fitz.open(str(pdf)) as doc:
        for pg in doc:
            infos = pg.get_images(full=True)
            melhor = max(infos, key=lambda i: i[2] * i[3])
            pix = fitz.Pixmap(doc, melhor[0])
            if pix.colorspace is None or pix.colorspace.n != 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            if pix.alpha:
                pix = fitz.Pixmap(pix, 0)
            img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3]
            res.append(cv2.cvtColor(img, cv2.COLOR_RGB2BGR).copy())
    return res


# ------------------------------------------------------------------ 1. somas de fábrica

def m_somas(raiz: Path, saida: Path, _casos):
    from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO
    from core.pipeline import processar
    lista = sorted(json.loads((raiz / "gabarito" / "lista.json").read_text(encoding="utf-8"))["paginas"])
    res = json.loads(saida.read_text(encoding="utf-8")) if saida.is_file() else {}
    pasta = _DADOS / ("somas-" + saida.stem)
    pasta.mkdir(parents=True, exist_ok=True)
    for pid in lista:
        for filtro in (ORIGINAL, PRETO_E_BRANCO, MELHORAR):
            chave = f"{pid}|{filtro}"
            if chave in res:
                continue
            pdf = pasta / f"{pid}-{filtro}.pdf"
            projeto = _projeto(raiz / "gabarito" / "paginas" / f"{pid}.pdf", pdf, filtro=filtro)
            processar(projeto)
            res[chave] = _somas_pdf(pdf)
            pdf.unlink(missing_ok=True)
            saida.write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf-8")
            print(chave, "ok", time.strftime("%H:%M:%S"), flush=True)


# ------------------------------------------------------------------ medidas

def tinta(img):
    """Máscara da tinta (preto/escuro) por Otsu no cinza."""
    import cv2
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, m = cv2.threshold(cv2.GaussianBlur(cinza, (3, 3), 0), 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    return m


def nitidez_das_linhas(img, faixa=(0.0, 1.0)):
    """Quão "retas" estão as linhas do texto numa faixa de largura da página (0..1).
    Soma da tinta linha por linha de pontos; linha de texto reta dá picos altos e vales
    vazios (número alto); linha torta espalha a tinta (número baixo). Conta: desvio padrão
    da projeção / média. Só serve para comparar a MESMA página antes e depois."""
    import numpy as np
    m = tinta(img) > 0
    h, w = m.shape
    a, b = int(w * faixa[0]), int(w * faixa[1])
    # tira 6% de cima e de baixo (cabeço e rodapé, faixa preta do scanner)
    proj = m[int(h * 0.06):int(h * 0.94), a:b].sum(axis=1).astype(float)
    return float(proj.std() / max(1e-6, proj.mean()))


def inclinacao_local(img, faixa):
    """Ângulo médio (graus) das linhas de texto numa faixa vertical da página, pelo
    melhor alinhamento da projeção (procura de -6 a +6 graus). Página reta: ~0 em
    todas as faixas. Página curva perto da lombada: a faixa da lombada inclina."""
    import cv2
    import numpy as np
    m = tinta(img)
    h, w = m.shape
    a, b = int(w * faixa[0]), int(w * faixa[1])
    pedaco = m[int(h * 0.08):int(h * 0.92), a:b]
    pequeno = cv2.resize(pedaco, (max(1, pedaco.shape[1] // 3), max(1, pedaco.shape[0] // 3)),
                         interpolation=cv2.INTER_AREA)
    melhor, ang = -1, 0.0
    for g in np.arange(-6, 6.01, 0.25):
        M = cv2.getRotationMatrix2D((pequeno.shape[1] / 2, pequeno.shape[0] / 2), g, 1.0)
        r = cv2.warpAffine(pequeno, M, (pequeno.shape[1], pequeno.shape[0]))
        p = r.sum(axis=1).astype(float)
        s = p.std()
        if s > melhor:
            melhor, ang = s, float(g)
    return ang


def tinta_na_beirada(img, mm=1.0, dpi=300):
    """Pedaços de tinta (> 1 mm) encostados na beirada da página: letra cortada pelo
    corte. Conta independente da do programa."""
    import cv2
    import numpy as np
    m = tinta(img)
    n, rot, est, _ = cv2.connectedComponentsWithStats(m, 8)
    lado = mm / 25.4 * dpi
    h, w = m.shape
    conta = 0
    for i in range(1, n):
        x, y, ww, hh, area = est[i]
        if max(ww, hh) < lado or ww > w * 0.5 or hh > h * 0.5:   # pontinho, ou faixa/moldura
            continue
        if x <= 1 or y <= 1 or x + ww >= w - 1 or y + hh >= h - 1:
            conta += 1
    return conta


def area_de_tinta_mm2(img, dpi=300):
    """Tinta total da página, em mm² (para ver se sumiu texto)."""
    import numpy as np
    return float((tinta(img) > 0).sum() * (25.4 / dpi) ** 2)


def medidas(img, dpi=300):
    return {
        "tamanho": list(img.shape[:2]),
        "nitidez_toda": round(nitidez_das_linhas(img), 3),
        "nitidez_esq_terco": round(nitidez_das_linhas(img, (0.0, 0.33)), 3),
        "nitidez_dir_terco": round(nitidez_das_linhas(img, (0.67, 1.0)), 3),
        "incl_esq": inclinacao_local(img, (0.0, 0.25)),
        "incl_meio": inclinacao_local(img, (0.375, 0.625)),
        "incl_dir": inclinacao_local(img, (0.75, 1.0)),
        "tinta_cortada_na_beirada": tinta_na_beirada(img, dpi=dpi),
        "tinta_mm2": round(area_de_tinta_mm2(img, dpi), 1),
    }


# ------------------------------------------------------------------ painel

def _fonte(t, negrito=False):
    from PIL import ImageFont
    return ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf" if negrito else r"C:\Windows\Fonts\segoeui.ttf", t)


def painel(titulo: list[str], colunas: list[tuple[str, str, object]], altura=1300, regua=True):
    """Colunas lado a lado, cada uma com duas linhas de legenda. Régua vermelha opcional
    (linhas retas horizontais, a cada 4% da altura) para ver se o texto está reto."""
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw
    pecas = []
    for cima, baixo, img in colunas:
        im = img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        f = altura / im.shape[0]
        im = cv2.resize(im, (max(1, int(im.shape[1] * f)), altura), interpolation=cv2.INTER_AREA)
        if regua:
            for y in range(0, altura, max(1, altura // 25)):
                cv2.line(im, (0, y), (im.shape[1], y), (60, 60, 230), 1)
        pecas.append((cima, baixo, im))
    larg = sum(p[2].shape[1] for p in pecas) + 20 * (len(pecas) + 1)
    topo = 40 + 30 * len(titulo) + 70
    tela = Image.new("RGB", (max(larg, 1400), topo + altura + 20), "white")
    d = ImageDraw.Draw(tela)
    y = 15
    for i, linha in enumerate(titulo):
        d.text((20, y), linha, fill="black", font=_fonte(26 if i == 0 else 22, i == 0))
        y += 30 if i else 34
    x = 20
    for cima, baixo, im in pecas:
        d.text((x, topo - 66), cima, fill="black", font=_fonte(22, True))
        d.text((x, topo - 36), baixo, fill=(60, 60, 60), font=_fonte(20))
        tela.paste(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)), (x, topo))
        x += im.shape[1] + 20
    return cv2.cvtColor(np.array(tela), cv2.COLOR_RGB2BGR)


# ------------------------------------------------------------------ página curvada (sintética)

def m_sintetica(raiz: Path, pasta: Path, _casos):
    """Faz `curvada.pdf`: uma página reta do gabarito (Marial 41) passada pelo caminho do
    programa SEM desentortar, e então encurvada por mim como uma página aberta perto da
    lombada (à esquerda): as linhas descem em arco nos 35% perto da lombada, até 4% da
    altura; a página escurece um pouco na dobra. Gravada a 300 DPI."""
    import cv2
    import fitz
    import numpy as np
    from core.pipeline import processar
    pasta.mkdir(parents=True, exist_ok=True)
    pdf = pasta / "reta.pdf"
    fonte = [c[6:] for c in _casos if c.startswith("fonte=")]
    if fonte:
        # uma página já passada pelo programa (png), sem a faixa preta de cima do scanner
        reta = cv2.imread(fonte[0])
        cinza = cv2.cvtColor(reta, cv2.COLOR_BGR2GRAY)
        escuras = [y for y in range(cinza.shape[0] // 3) if cinza[y].mean() < 120]
        if escuras:
            reta = reta[max(escuras) + 20:]
    else:
        um = _pdf_de_uma_pagina(ACERVO / "Marial de sermoens - Frei Balthasar Paez. (1).pdf", 40, 0, pasta)
        projeto = _projeto(um, pdf)
        processar(projeto)
        reta = _imagens_pdf(pdf)[0]
    h, w = reta.shape[:2]
    # margem branca de papel em volta (o scanner pega o papel inteiro)
    borda = int(0.06 * w)
    cor_papel = np.median(reta.reshape(-1, 3), axis=0).astype(np.uint8)
    grande = np.empty((h + 2 * borda, w + 2 * borda, 3), np.uint8)
    grande[:] = cor_papel
    grande[borda:borda + h, borda:borda + w] = reta
    H, W = grande.shape[:2]
    xs, ys = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    zona = 0.40 * W
    t = np.clip((zona - xs) / zona, 0, 1)            # 1 na lombada (esquerda), 0 longe
    desce = (0.045 * H) * t ** 2                      # o arco: a linha desce perto da lombada
    # as linhas do meio da página descem mais que as de cima e de baixo? não: o livro aberto
    # faz as linhas de cima curvarem para cima e as de baixo para baixo (como um barril)
    rel = (ys - H / 2) / (H / 2)                      # -1 em cima, +1 embaixo
    if "forte" in _casos:
        # livro grosso aberto: TODAS as linhas sobem perto da lombada (o papel levanta), um
        # pouco mais em cima e embaixo; até 3,5% da altura
        mapy = ys + (0.035 * H) * t ** 2 * (1.0 + 0.4 * rel ** 2)
    else:
        mapy = ys - desce * rel
    encolhe = 1.0 - 0.18 * t ** 2                     # a página "foge" na dobra (fica estreita)
    mapx = (xs - 0) / 1.0
    mapx = np.cumsum(1.0 / encolhe, axis=1).astype(np.float32)
    mapx = mapx - mapx[:, :1]
    mapx = mapx * (W - 1) / mapx[:, -1:]
    curva = cv2.remap(grande, mapx.astype(np.float32), mapy.astype(np.float32), cv2.INTER_CUBIC,
                      borderMode=cv2.BORDER_CONSTANT, borderValue=tuple(int(c) for c in cor_papel))
    sombra = (1.0 - 0.35 * t ** 3)[..., None]
    curva = np.clip(curva.astype(np.float32) * sombra, 0, 255).astype(np.uint8)
    nome_saida = ([c[5:] for c in _casos if c.startswith("nome=")] or ["curvada2" if "forte" in _casos else "curvada"])[0]
    cv2.imwrite(str(pasta / f"{nome_saida}.png"), curva)
    ok, jpg = cv2.imencode(".jpg", curva, [cv2.IMWRITE_JPEG_QUALITY, 92])
    doc = fitz.open()
    pg = doc.new_page(width=W * 72 / 300, height=H * 72 / 300)
    pg.insert_image(pg.rect, stream=jpg.tobytes())
    destino = _SINTETICA.replace("curvada.pdf", nome_saida + ".pdf")
    doc.save(destino)
    doc.close()
    print(nome_saida, W, H, destino)


# ------------------------------------------------------------------ 2. ligado

def _um_caso(raiz: Path, nome: str, pasta: Path):
    import cv2
    from core import analise
    from core import desentortar_scantailor as ds
    from core.filtros import ORIGINAL, PRETO_E_BRANCO
    from core.pipeline import processar
    livro, pg, giro, dividir, metade, modo, desc = CASOS[nome]
    livro = _livro(nome)
    rasc = Path(tempfile.mkdtemp(prefix=f"v212_{nome}_", dir=str(_DADOS)))
    entrada = _pdf_de_uma_pagina(livro, pg - 1, giro, rasc)
    imgs, avisos, tempos = {}, {}, {}
    for rotulo, filtro, des, aum in (("hoje", ORIGINAL, ds.DESLIGADO, False),
                                     ("ligado", ORIGINAL, modo, False),
                                     ("botao", ORIGINAL, modo, True),
                                     ("hoje_pb", PRETO_E_BRANCO, ds.DESLIGADO, False),
                                     ("ligado_pb", PRETO_E_BRANCO, modo, False),
                                     ("botao_pb", PRETO_E_BRANCO, modo, True)):
        saida = rasc / f"{rotulo}.pdf"
        projeto = _projeto(entrada, saida, dividir=dividir, filtro=filtro)
        alvo = [p for p in projeto.paginas_ativas if p.metade == metade]
        if not alvo:
            raise SystemExit(f"{nome}: metade {metade} não existe ({[p.metade for p in projeto.paginas_ativas]})")
        for p in projeto.paginas_ativas:
            if p is not alvo[0]:
                p.apagada = True
        alvo[0].desentortar = des
        alvo[0].desentortar_aumentar = aum
        t0 = time.perf_counter()
        processar(projeto)
        tempos[rotulo] = round(time.perf_counter() - t0, 1)
        imgs[rotulo] = _imagens_pdf(saida)[0]
        avisos[rotulo] = [a for a in alvo[0].alertas if a.startswith("desentortar")]
    num = {k: medidas(v) for k, v in imgs.items()}
    import numpy as np
    num["_avisos"] = avisos
    num["_segundos"] = tempos
    num["_ligado_igual_a_hoje"] = bool(imgs["ligado"].shape == imgs["hoje"].shape
                                       and np.array_equal(imgs["ligado"], imgs["hoje"]))
    num["_caminho"] = (f"girar {giro}°, " if giro else "") + ("dividir (ligado no livro), " if dividir else "") + \
        "endireitar, cortar, desentortar, filtro (livro novo, de fábrica)"

    def av(r):
        a = avisos[r]
        if analise.DESENTORTAR_AINDA_DEFORMADA in a:
            return "aviso: \"A página ainda saiu deformada\""
        if analise.DESENTORTAR_SAIU_SEM in a:
            return "aviso: \"Desentortar não usado\""
        return "sem aviso"
    nm = ds.ROTULOS_NA_TELA.get(modo, modo)
    titulo = [desc, "Caminho do programa: " + num["_caminho"] + ". Imagem tirada do PDF de saída.",
              f"Desentortar: {nm}. Linhas vermelhas: retas, só para comparar com as linhas do texto."]
    cols = [("1. Hoje (desligado)", "Original", imgs["hoje"]),
            ("2. Ligado", av("ligado") + " · Original", imgs["ligado"]),
            ("3. Com o botão", "\"Desentortar aumentando\" · " + av("botao"), imgs["botao"]),
            ("4. Hoje (desligado)", "Preto e branco", imgs["hoje_pb"]),
            ("5. Ligado", av("ligado_pb") + " · Preto e branco", imgs["ligado_pb"]),
            ("6. Com o botão", "Preto e branco", imgs["botao_pb"])]
    cv2.imwrite(str(pasta / f"{nome}-pagina.jpg"), painel(titulo, cols), [cv2.IMWRITE_JPEG_QUALITY, 86])
    (pasta / f"{nome}.json").write_text(json.dumps(num, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in ("hoje", "ligado", "botao"):
        cv2.imwrite(str(rasc / f"{r}.png"), imgs[r])
    print(nome, json.dumps({k: num[k] for k in ("_avisos", "_segundos", "_ligado_igual_a_hoje")},
                           ensure_ascii=False), flush=True)
    return num


def m_ligado(raiz: Path, pasta: Path, casos):
    pasta.mkdir(parents=True, exist_ok=True)
    for nome in casos or list(CASOS):
        _um_caso(raiz, nome, pasta)


# ------------------------------------------------------------------ 3. prévia x PDF

def m_previa(raiz: Path, pasta: Path, casos):
    """Para cada caso: a prévia "Rápida" (core.pipeline.renderizar_pagina a 110 DPI, a que
    a tela de conferir usa) ANTES da medida, a medida por trás (medir_o_desentortar), a
    prévia DEPOIS da medida, e o PDF. Compara a prévia com o PDF reduzido ao mesmo tamanho:
    diferença média por ponto (0 = igual). Desligado, ligado e com o botão."""
    import cv2
    import numpy as np
    from core import desentortar_scantailor as ds
    from core.filtros import ORIGINAL
    from core.pdf_io import abrir_pdf
    from core import pipeline
    pasta.mkdir(parents=True, exist_ok=True)
    res = {}
    for nome in casos or ["destino18", "righetti96", "curvada"]:
        livro, pg, giro, dividir, metade, modo, desc = CASOS[nome]
        rasc = Path(tempfile.mkdtemp(prefix=f"v212p_{nome}_", dir=str(_DADOS)))
        entrada = _pdf_de_uma_pagina(_livro(nome), pg - 1, giro, rasc)
        for rotulo, aum in (("ligado", False), ("botao", True)):
            pipeline._DESENTORTADAS.clear()
            saida = rasc / f"{rotulo}.pdf"
            projeto = _projeto(entrada, saida, dividir=dividir, filtro=ORIGINAL)
            alvo = [p for p in projeto.paginas_ativas if p.metade == metade][0]
            for p in projeto.paginas_ativas:
                if p is not alvo:
                    p.apagada = True
            alvo.desentortar = modo
            alvo.desentortar_aumentar = aum
            doc = abrir_pdf(str(entrada))
            try:
                antes, _ = pipeline.renderizar_pagina(doc, projeto, alvo, dpi=110)
                por_medir = pipeline.desentortar_por_medir(projeto, alvo)
                t0 = time.perf_counter()
                mediu = pipeline.medir_o_desentortar(doc, projeto, alvo)
                t_medida = round(time.perf_counter() - t0, 1)
                avisos_medida = [a for a in alvo.alertas if a.startswith("desentortar")]
                depois, _ = pipeline.renderizar_pagina(doc, projeto, alvo, dpi=110)
                t1 = time.perf_counter()
                pipeline.renderizar_pagina(doc, projeto, alvo, dpi=110)
                t_previa_de_novo = round(time.perf_counter() - t1, 2)
            finally:
                doc.close()
            pipeline.processar(projeto)
            pdf_img = _imagens_pdf(saida)[0]
            def dif(a, b):
                b2 = cv2.resize(b, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_AREA)
                return round(float(cv2.absdiff(a, b2).mean()), 2)
            r = {
                "por_medir_antes": por_medir, "mediu": mediu, "segundos_da_medida": t_medida,
                "avisos_depois_da_medida": avisos_medida,
                "previa_antes_tamanho": list(antes.shape[:2]), "previa_depois_tamanho": list(depois.shape[:2]),
                "pdf_tamanho": list(pdf_img.shape[:2]),
                "proporcao_previa_depois": round(depois.shape[1] / depois.shape[0], 4),
                "proporcao_pdf": round(pdf_img.shape[1] / pdf_img.shape[0], 4),
                "proporcao_previa_antes": round(antes.shape[1] / antes.shape[0], 4),
                "dif_previa_depois_x_pdf": dif(depois, pdf_img),
                "dif_previa_antes_x_pdf": dif(antes, pdf_img),
                "segundos_previa_depois_de_medida": t_previa_de_novo,
            }
            res[f"{nome}|{rotulo}"] = r
            cols = [("1. Prévia Rápida, antes da medida", "a tela nos primeiros segundos", antes),
                    ("2. Prévia Rápida, depois da medida", "o que a tela mostra", depois),
                    ("3. PDF de saída", "o que vai ser impresso", pdf_img)]
            cv2.imwrite(str(pasta / f"{nome}-{rotulo}-previa.jpg"),
                        painel([desc + (" · com o botão \"Desentortar aumentando\"" if aum else " · desentortar ligado"),
                                "Original. A prévia Rápida (110 DPI) ampliada para a mesma altura do PDF."], cols, 1100),
                        [cv2.IMWRITE_JPEG_QUALITY, 86])
            print(nome, rotulo, json.dumps(r, ensure_ascii=False), flush=True)
    (pasta / "previa.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


# ------------------------------------------------------------------ reabrir

def m_reabrir(raiz: Path, pasta: Path, casos):
    """casos[0] = "gravar": grava o projeto.json de uma página do gabarito com o código desta
    worktree (no código de antes não existem os campos do desentortar). casos[0] = "ler": lê
    o projeto.json gravado (por qualquer código) e diz como ficaram os campos, e grava de novo
    com os campos ligados para ver se voltam."""
    from modelos import Projeto
    pasta.mkdir(parents=True, exist_ok=True)
    arq = pasta / "projeto.json"
    if casos[0] == "gravar":
        projeto = _projeto(raiz / "gabarito" / "paginas" / "escola_p007.pdf", pasta / "x.pdf")
        arq.write_text(json.dumps(projeto.para_dicionario(), ensure_ascii=False), encoding="utf-8")
        tem = any("desentortar" in json.dumps(p) for p in json.loads(arq.read_text(encoding="utf-8")).get("paginas", []))
        print("gravado; tem campo desentortar:", tem)
        return
    projeto = Projeto.de_dicionario(json.loads(arq.read_text(encoding="utf-8")))
    res = {"abriu_paginas": [(p.desentortar, p.desentortar_aumentar) for p in projeto.paginas]}
    projeto.paginas[0].desentortar = "automatico"
    projeto.paginas[0].desentortar_aumentar = True
    de_novo = Projeto.de_dicionario(json.loads(json.dumps(projeto.para_dicionario())))
    res["gravado_e_aberto_de_novo"] = (de_novo.paginas[0].desentortar, de_novo.paginas[0].desentortar_aumentar)
    (pasta / "reabrir.json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo")
    ap.add_argument("saida", type=Path)
    ap.add_argument("casos", nargs="*")
    ap.add_argument("--raiz", type=Path, required=True)
    a = ap.parse_args()
    raiz = a.raiz.resolve()
    sys.path.insert(0, str(raiz))
    os.chdir(raiz)
    {"somas": m_somas, "ligado": m_ligado, "previa": m_previa, "reabrir": m_reabrir,
     "sintetica": m_sintetica}[a.modo](raiz, a.saida.resolve(), a.casos)


if __name__ == "__main__":
    raise SystemExit(main())
