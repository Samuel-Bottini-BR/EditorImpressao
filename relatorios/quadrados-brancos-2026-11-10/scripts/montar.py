"""Monta as imagens do relatorio dos quadrados brancos no modelo de print do Samuel
(docs/plano/central/modelo-de-print, CLAUDE.md §10 do fase-1): resumo primeiro; faixa azul
= Original, laranja = como sai hoje, verde = como sairia com o conserto (SIMULACAO, nao esta
no programa); as mesmas paginas e o mesmo recorte em todas as faixas; o que olhar circulado
em vermelho.

    python montar.py <pasta crua> <pasta de saida>

A pasta crua tem os PNG/JPG gravados por reproduzir.py e varrer.py (scratchpad)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, r"D:\programas\EditorImpressao\docs\plano\central\modelo-de-print")
import montar_provas_exemplo as M  # noqa: E402  (as mesmas faixas, grade e circulo do modelo)

AZUL, LARANJA, VERDE, CINZA = (60, 90, 150), (190, 90, 10), (25, 130, 60), (40, 40, 40)
# recorte ampliado da pagina 13 (fracao da pagina): a agua e o ceu, onde nascem os quadrados
RECORTE_13 = (0.12, 0.13, 0.62, 0.36)


def _abrir(caminho: Path) -> Image.Image:
    return Image.open(caminho).convert("RGB")


def _recorte(img: Image.Image, caixa) -> Image.Image:
    w, h = img.size
    return img.crop((round(caixa[0] * w), round(caixa[1] * h), round(caixa[2] * w), round(caixa[3] * h)))


def _com_retangulo(img: Image.Image, caixa) -> Image.Image:
    """A pagina inteira com um retangulo vermelho FINO so na borda do recorte (sem cobrir)."""
    img = img.copy()
    w, h = img.size
    d = ImageDraw.Draw(img)
    d.rectangle([caixa[0] * w - 6, caixa[1] * h - 6, caixa[2] * w + 6, caixa[3] * h + 6],
                outline=M.VERMELHO, width=max(4, w // 250))
    return img


def _celulas(pagina: Image.Image, caixa_l: int, caixa_r: int, rotulo_pag: str, rotulo_rec: str,
             recorte=RECORTE_13):
    """[pagina inteira | recorte ampliado], o recorte circulado."""
    f_num = M._fonte(30, True)
    topo, margem = 60, 22
    p = M._caber(_com_retangulo(pagina, recorte), caixa_l, caixa_l)
    r = M._caber(_recorte(pagina, recorte), caixa_r, caixa_l)
    largura = p.width + r.width + 4 * margem + 40
    altura = caixa_l + topo + 2 * margem
    img = Image.new("RGB", (largura, altura), M.FUNDO)
    d = ImageDraw.Draw(img)
    x = margem
    d.text((x + p.width / 2, 6), rotulo_pag, fill=(30, 30, 30), font=f_num, anchor="mt")
    img.paste(p, (x, topo + margem))
    d.rectangle([x - 1, topo + margem - 1, x + p.width, topo + margem + p.height], outline=(150, 150, 150))
    x2 = x + p.width + 2 * margem + 40
    d.text((x2 + r.width / 2, 6), rotulo_rec, fill=M.VERMELHO, font=f_num, anchor="mt")
    y2 = topo + margem + (caixa_l - r.height) // 2
    img.paste(r, (x2, y2))
    # contorno vermelho arredondado POR FORA do recorte (nao cobre nada do conteudo)
    d.rounded_rectangle([x2 - 14, y2 - 14, x2 + r.width + 13, y2 + r.height + 13], radius=28,
                        outline=M.VERMELHO, width=7)
    return img


def resumo_13(cru: Path, saida: Path, legendas: dict) -> None:
    faixas = (
        ("ORIGINAL (como veio no PDF)", AZUL, "original",
         "Página 13 do Na escola de Jesus, sem filtro. A água e o céu são cinza-azulados claros."),
        ("HOJE — Melhorar, Clareza \"bem forte\"", LARANJA, "melhorar_forte_respeitar",
         "Livro novo, Melhorar escolhido no painel, \"Respeitar as gravuras achadas\" marcada: a água "
         "e o céu viram buracos brancos em blocos (o seu print 09). Igual no PDF."),
        ("HOJE — Mágico pro, Intensidade \"bem fraco\"", LARANJA, "magico_fraco_sem_respeitar",
         "Mágico pro, \"Respeitar\" desmarcada (o seu print 10): os mesmos buracos. Igual no PDF."),
        ("CONSERTADO (simulação) — Melhorar \"bem forte\"", VERDE, "cand_melhorar_forte_respeitar",
         "SIMULAÇÃO, não está no programa: a limpeza final deixa de pintar de branco o meio de uma pintura. "
         "A água e o céu ficam; o papel da página continua branco."),
        ("CONSERTADO (simulação) — Mágico pro \"bem fraco\"", VERDE, "cand_magico_fraco_sem_respeitar",
         "SIMULAÇÃO, não está no programa: a mesma regra no Mágico pro."),
    )
    partes = [M._cabeca("Quadrados brancos — resumo", CINZA,
                        "Na escola de Jesus, página 13 (Jonas e a baleia), livro novo sem o Automático. "
                        "Como sai no PDF (300 DPI). À esquerda a página inteira, à direita o pedaço "
                        "do retângulo vermelho, ampliado.")]
    for rotulo, cor, nome, legenda in faixas:
        pagina = _abrir(cru / f"{nome}_pdf.png")
        partes.append(M._empilhar([M._cabeca(rotulo, cor, legenda),
                                   _celulas(pagina, 360, 900, "página 13", "água e céu, ampliado")],
                                  espaco=6))
    img = M._empilhar(partes)
    M._salvar(img, saida / "1-resumo-pagina-13.png", legendas,
              "Resumo: página 13, Original, como sai hoje (Melhorar e Mágico pro) e como sairia com o "
              "conserto (simulação), página inteira e água ampliada.")
    # a previa da tela, para mostrar que e igual ao PDF
    partes = [M._cabeca("Prévia da tela = PDF", CINZA,
                        "A mesma página 13, Melhorar \"bem forte\": a prévia da tela (150 DPI) e o PDF "
                        "(300 DPI). Os quadrados estão nos dois: não é defeito só da tela.")]
    for rotulo, cor, arq in (("ORIGINAL", AZUL, "original_pdf.png"),
                             ("HOJE — na prévia da tela", LARANJA, "melhorar_forte_respeitar_previa.png"),
                             ("HOJE — no PDF", LARANJA, "melhorar_forte_respeitar_pdf.png")):
        partes.append(M._empilhar([M._cabeca(rotulo, cor, ""),
                                   _celulas(_abrir(cru / arq), 360, 900, "página 13",
                                            "água e céu, ampliado")], espaco=6))
    M._salvar(M._empilhar(partes), saida / "2-previa-igual-ao-pdf.png", legendas,
              "A prévia da tela e o PDF têm os mesmos quadrados (página 13, Melhorar bem forte).")


def caixa_da_gravura(orig: Image.Image) -> tuple[float, float, float, float]:
    """A caixa (em fracao) da maior area de pintura da pagina, achada no ORIGINAL: o que nao
    e papel claro, juntado com um fechamento largo. A mesma caixa vale para as tres faixas."""
    import cv2
    import numpy as np

    rgb = np.asarray(orig)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    papel_s = float(np.percentile(hsv[:, :, 1], 30))      # a cor do papel creme
    h, w = hsv.shape[:2]
    # pintura = cor bem mais forte que a do papel; a letra preta e o papel creme ficam de fora
    m = (hsv[:, :, 1].astype(np.float32) > papel_s + 35).astype(np.uint8)
    m[: int(0.04 * h)] = 0; m[-int(0.04 * h):] = 0; m[:, : int(0.04 * w)] = 0; m[:, -int(0.04 * w):] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, _r, st, _c = cv2.connectedComponentsWithStats(m, 8)
    if n <= 1:
        return (0.0, 0.0, 1.0, 1.0)
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, bw, bh = st[i, 0], st[i, 1], st[i, 2], st[i, 3]
    return (x / w, y / h, (x + bw) / w, (y + bh) / h)


def _grade_recortes(imgs: list[Image.Image], numeros: list[int], caixas: list, por_linha: int,
                    caixa: int, marcar: set[int]) -> Image.Image:
    """Recortes (a gravura de cada pagina) em quadros iguais, "pagina N" em cima; as paginas de
    `marcar` com o nome em vermelho e um contorno vermelho POR FORA do recorte."""
    f_num = M._fonte(30, True)
    topo, margem = 50, 22
    cel_l, cel_a = caixa + 2 * margem, caixa + topo + 2 * margem
    linhas = (len(imgs) + por_linha - 1) // por_linha
    img = Image.new("RGB", (cel_l * por_linha, cel_a * linhas), M.FUNDO)
    d = ImageDraw.Draw(img)
    for n, (pag, numero, cx) in enumerate(zip(imgs, numeros, caixas)):
        x0, y0 = (n % por_linha) * cel_l, (n // por_linha) * cel_a
        cor = M.VERMELHO if numero in marcar else (30, 30, 30)
        d.text((x0 + cel_l / 2, y0 + 6), f"página {numero}", fill=cor, font=f_num, anchor="mt")
        r = M._caber(_recorte(pag, cx), caixa, caixa)
        px, py = x0 + (cel_l - r.width) // 2, y0 + topo + margem + (caixa - r.height) // 2
        img.paste(r, (px, py))
        if numero in marcar:
            d.rounded_rectangle([px - 12, py - 12, px + r.width + 11, py + r.height + 11], radius=20,
                                outline=M.VERMELHO, width=6)
        else:
            d.rectangle([px - 1, py - 1, px + r.width, py + r.height], outline=(150, 150, 150))
    return img


def livro(cru: Path, saida: Path, legendas: dict, nome_arq: str, titulo: str, linha: str,
          paginas: list[int], pastas: list[tuple[str, tuple, str, str]],
          circular: list[int] | None = None) -> None:
    """Uma faixa por situacao, as mesmas paginas e o MESMO recorte (a gravura, achada no
    original) em todas; as paginas com quadrados marcadas em vermelho."""
    caixas = [caixa_da_gravura(_abrir(cru / pastas[0][3].format(p=p))) for p in paginas]
    partes = [M._cabeca(titulo, CINZA, linha)]
    for rotulo, cor, legenda, molde in pastas:
        imgs = [_abrir(cru / molde.format(p=p)) for p in paginas]
        grade = _grade_recortes(imgs, paginas, caixas, 4, 330, set(circular or paginas))
        partes.append(M._empilhar([M._cabeca(rotulo, cor, legenda), grade], espaco=6))
    M._salvar(M._empilhar(partes), saida / nome_arq, legendas, f"{titulo}. {linha}")


RECORTE_HORAS_47 = (0.15, 0.03, 0.85, 0.25)


def horas_47(cru: Path, saida: Path, legendas: dict) -> None:
    """O outro livro: Livro de Horas, pagina 47, a pintura de cima ampliada."""
    faixas = (
        ("ORIGINAL", AZUL, "horas47_original_pdf.png", "Como veio no PDF: colunas, prédio e céu claros atrás das figuras."),
        ("HOJE — Melhorar \"bem forte\"", LARANJA, "horas47_melhorar_pdf.png",
         "O prédio, o céu e riscos nas colunas e nas roupas claras viram branco puro."),
        ("CONSERTADO (simulação) — Melhorar", VERDE, "horas47_cand_melhorar_pdf.png",
         "SIMULAÇÃO, não está no programa: o prédio de trás volta; ainda sobram riscos brancos nas "
         "colunas e na roupa clara da esquerda (a pintura tem traço fino, e o conserto ali deixa limpar)."),
    )
    partes = [M._cabeca("Outro livro — Livro de Horas, página 47", CINZA,
                        "Livro novo, Melhorar \"bem forte\" escolhido à mão. Como sai no PDF. À esquerda "
                        "a página inteira, à direita a pintura de cima ampliada.")]
    for rotulo, cor, arq, legenda in faixas:
        partes.append(M._empilhar([M._cabeca(rotulo, cor, legenda),
                                   _celulas(_abrir(cru / arq), 360, 900, "página 47",
                                            "pintura de cima, ampliada", RECORTE_HORAS_47)], espaco=6))
    M._salvar(M._empilhar(partes), saida / "5-outro-livro-horas-47.png", legendas,
              "Livro de Horas, página 47: Original, como sai hoje e como sairia com o conserto (simulação).")


def main() -> None:
    cru, saida = Path(sys.argv[1]), Path(sys.argv[2])
    saida.mkdir(parents=True, exist_ok=True)
    legendas: dict = {}
    resumo_13(cru, saida, legendas)
    if (cru / "horas47_original_pdf.png").is_file():
        horas_47(cru, saida, legendas)
    extra = json.loads((cru / "extra.json").read_text(encoding="utf-8"))
    for item in extra:
        livro(cru, saida, legendas, item["arquivo"], item["titulo"], item["linha"], item["paginas"],
              [(r, tuple(c), l, m) for r, c, l, m in item["faixas"]], item.get("circular"))
    (saida / "legendas.json").write_text(json.dumps(legendas, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ok", saida)


if __name__ == "__main__":
    main()
