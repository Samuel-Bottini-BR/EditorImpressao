"""Monta as imagens do relatorio "de onde vieram os quadrados brancos" no modelo de print do
girar (docs/plano/central/modelo-de-print/montar_provas_exemplo.py, CLAUDE.md §10): resumo
primeiro; uma faixa por situacao com cor e titulo grande (azul ANTES, laranja DEPOIS (hoje),
verde "So essa mudanca desfeita", roxo "Conserto C"); as mesmas paginas, no mesmo recorte e na
mesma ordem em todas as faixas, com o nome em cima; o que olhar com o nome em vermelho e um
contorno vermelho POR FORA do recorte (nada cobre a pintura).

    python montar.py <pasta de trabalho (saida/ e livros/)> <pasta das imagens>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTE = "C:/Windows/Fonts/segoeui.ttf"
FONTE_N = "C:/Windows/Fonts/segoeuib.ttf"
LARGURA = 1500
FUNDO = (250, 249, 246)
VERMELHO = (220, 20, 20)
AZUL, LARANJA, VERDE, ROXO, CINZA = (60, 90, 150), (190, 90, 10), (25, 130, 60), (110, 60, 150), (40, 40, 40)

ANTES = ("ANTES da mudança (versão de 26/10, commit ddd4d74a)", AZUL)
DEPOIS = ("DEPOIS da mudança (hoje, commit d9f80eb4)", LARANJA)
DESFEITA = ("Só essa mudança desfeita (simulação em cópia)", VERDE)
CONSERTO_C = ("Conserto C do verificador (simulação em cópia)", ROXO)


def _fonte(tamanho: int, negrito: bool = False):
    return ImageFont.truetype(FONTE_N if negrito else FONTE, tamanho)


def _quebrar(texto: str, fonte, largura: int) -> list[str]:
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if fonte.getlength(teste) > largura and atual:
            linhas.append(atual)
            atual = palavra
        else:
            atual = teste
    return linhas + ([atual] if atual else [])


def _cabeca(rotulo: str, cor, legenda: str, largura: int = LARGURA, grande: int = 44) -> Image.Image:
    f_rot, f_leg = _fonte(grande, True), _fonte(26)
    linhas_rot = _quebrar(rotulo, f_rot, largura - 40)
    alto_rot = 20 + (grande + 12) * len(linhas_rot)
    linhas = _quebrar(legenda, f_leg, largura - 40)
    img = Image.new("RGB", (largura, alto_rot + 14 + 36 * len(linhas) + 10), FUNDO)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, largura, alto_rot], fill=cor)
    for n, t in enumerate(linhas_rot):
        d.text((20, 10 + (grande + 12) * n), t, fill="white", font=f_rot)
    for n, texto in enumerate(linhas):
        d.text((20, alto_rot + 12 + 36 * n), texto, fill=(30, 30, 30), font=f_leg)
    return img


def _empilhar(partes: list[Image.Image], espaco: int = 16, largura: int = LARGURA) -> Image.Image:
    altura = sum(p.height for p in partes) + espaco * (len(partes) + 1)
    img = Image.new("RGB", (largura, altura), FUNDO)
    y = espaco
    for p in partes:
        img.paste(p, ((largura - p.width) // 2, y))
        y += p.height + espaco
    return img


def _caber(img: Image.Image, caixa_l: int, caixa_a: int) -> Image.Image:
    escala = min(caixa_l / img.width, caixa_a / img.height)
    return img.resize((max(1, round(img.width * escala)), max(1, round(img.height * escala))),
                      Image.LANCZOS)


def _salvar(img: Image.Image, destino: Path, legendas: dict, legenda: str) -> None:
    assert 900 <= img.width <= 1600, (destino, img.width)
    img.save(destino, optimize=True)
    legendas[destino.name] = legenda


def _abrir(caminho: Path) -> Image.Image:
    return Image.open(caminho).convert("RGB")


def caixa_da_pintura(pdf: Path, numero: int) -> tuple[float, float, float, float]:
    """A caixa (em fracao) da maior area de pintura da pagina, achada no ORIGINAL (o que tem cor
    bem mais forte que o papel). A mesma caixa vale para todas as faixas."""
    doc = fitz.open(str(pdf))
    pix = doc[numero - 1].get_pixmap(dpi=75)
    rgb = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3]
    hsv = cv2.cvtColor(np.ascontiguousarray(rgb), cv2.COLOR_RGB2HSV)
    papel_s = float(np.percentile(hsv[:, :, 1], 30))
    h, w = hsv.shape[:2]
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


def _recorte(img: Image.Image, cx) -> Image.Image:
    x0, y0, x1, y1 = cx
    return img.crop((round(x0 * img.width), round(y0 * img.height),
                     round(x1 * img.width), round(y1 * img.height)))


def _grade(imgs: list[Image.Image], nomes: list[str], caixas: list, por_linha: int, caixa: int,
           marcar: set[int], caixa_a: int | None = None) -> Image.Image:
    """Recortes em quadros iguais, o nome em cima; os de `marcar` (indices) com o nome em vermelho
    e um contorno vermelho por fora do recorte."""
    f_num = _fonte(28, True)
    topo, margem = 46, 20
    caixa_a = caixa_a or caixa
    cel_l, cel_a = caixa + 2 * margem, caixa_a + topo + 2 * margem
    linhas = (len(imgs) + por_linha - 1) // por_linha
    img = Image.new("RGB", (cel_l * por_linha, cel_a * linhas), FUNDO)
    d = ImageDraw.Draw(img)
    for n, (pag, nome, cx) in enumerate(zip(imgs, nomes, caixas)):
        x0, y0 = (n % por_linha) * cel_l, (n // por_linha) * cel_a
        cor = VERMELHO if n in marcar else (30, 30, 30)
        d.text((x0 + cel_l / 2, y0 + 6), nome, fill=cor, font=f_num, anchor="mt")
        r = _caber(_recorte(pag, cx) if cx else pag, caixa, caixa_a)
        px, py = x0 + (cel_l - r.width) // 2, y0 + topo + margem + (caixa_a - r.height) // 2
        img.paste(r, (px, py))
        if n in marcar:
            d.rounded_rectangle([px - 12, py - 12, px + r.width + 11, py + r.height + 11], radius=18,
                                outline=VERMELHO, width=6)
        else:
            d.rectangle([px - 1, py - 1, px + r.width, py + r.height], outline=(150, 150, 150))
    return img


def _faixa(rotulo_cor, legenda: str, imgs, nomes, caixas, por_linha, caixa, marcar,
          caixa_a: int | None = None) -> Image.Image:
    rotulo, cor = rotulo_cor
    return _empilhar([_cabeca(rotulo, cor, legenda),
                      _grade(imgs, nomes, caixas, por_linha, caixa, marcar, caixa_a)],
                     espaco=6)


def com_buraco(medidas: dict, chave: str, numero: int, limite: float = 6.0) -> bool:
    m = medidas.get(chave, {}).get(str(numero)) or {}
    return (m.get("buraco_pintura_pct") or 0) >= limite


def main() -> None:
    trab, saida = Path(sys.argv[1]), Path(sys.argv[2])
    saida.mkdir(parents=True, exist_ok=True)
    S = trab / "saida"
    medidas = json.loads((trab / "medidas_amostra.json").read_text(encoding="utf-8"))
    legendas: dict = {}
    escola = trab / "livros" / "escola.pdf"
    PAGS = [13, 18, 29, 36, 51, 66, 97, 119]
    caixas = {p: caixa_da_pintura(escola, p) for p in PAGS}

    def imgs(versao, filtro, pags, livro="escola"):
        return [_abrir(S / livro / versao / f"{filtro}_p{p:03d}.png") for p in pags]

    def marcar(versao, filtro, pags, livro="escola"):
        return {i for i, p in enumerate(pags) if com_buraco(medidas, f"{livro}/{versao}:{filtro}", p)}

    # --- 0. resumo: 4 paginas, Melhorar, antes / depois / desfeita ----------------------------
    R = [13, 29, 51, 119]
    nomes = [f"página {p}" for p in R]
    cx = [caixas[p] for p in R]
    partes = [_cabeca("Quadrados brancos — de onde vieram (resumo)", CINZA,
                      "Livro \"Na escola de Jesus\" (cópia), páginas 13, 29, 51 e 119. Livro novo, filtro "
                      "Melhorar \"bem forte\" escolhido à mão na página. Só a pintura de cada página, como "
                      "sai no PDF. Em vermelho: as pinturas com buracos brancos.")]
    for versao, rc, frase in (
            ("antes", ANTES, "O programa procurava a gravura sozinho e a protegia: a pintura sai inteira."),
            ("hoje", DEPOIS, "O programa não procura mais a gravura nesse caminho: a água e o céu viram "
                             "buracos brancos em blocos."),
            ("desfeita", DESFEITA, "O programa de hoje, só com aquela regra de volta como era: a pintura "
                                   "sai inteira de novo, igual ao ANTES.")):
        partes.append(_faixa(rc, frase, imgs(versao, "melhorar", R), nomes, cx, 4, 330,
                             marcar(versao, "melhorar", R)))
    _salvar(_empilhar(partes), saida / "0-resumo.png", legendas,
            "Resumo: as mesmas 4 pinturas antes da mudança, depois (hoje) e com só a mudança desfeita.")

    # --- 1. a bissecao na pagina 13 --------------------------------------------------------------
    VERS = [("v0928", "28/09 · a329166d · conserto do bug 202 (Fase 1)"),
            ("antes", "26/10 21h06 · ddd4d74a · antes da obra (= fase-1)"),
            ("etapa1", "26/10 21h25 · 175addb7 · etapa 1, livro aberto como na época"),
            ("etapa1_semlimpar", "26/10 21h25 · 175addb7 · etapa 1, \"Limpar a folha\" desmarcada"),
            ("v4d535", "26/10 23h17 · 4d535ab6 · etapa 3, só o núcleo"),
            ("e2321", "26/10 23h33 · e2321b16 · etapa 3, livro abre direto"),
            ("v1029", "29/10 · 99a3cdc5 · caixinha \"Respeitar\""),
            ("v1103", "03/11 · 9f765d75"),
            ("v1109", "09/11 · d25e2b76 · depois da D-659"),
            ("hoje", "10/11 · d9f80eb4 · hoje")]
    c13 = caixas[13]
    partes = [_cabeca("Página 13 em cada versão do programa (bisseção)", CINZA,
                      "Na escola de Jesus, página 13, Melhorar \"bem forte\" escolhido à mão, a mesma "
                      "pintura em cada versão, da mais velha para a mais nova. Azul = sai inteira; "
                      "laranja = sai com buracos brancos (circulada em vermelho).")]
    f_t = _fonte(24, True)
    linha = []
    for versao, titulo in VERS:
        caminho = S / versao / "melhorar_p013.png"
        if versao == "v0928":
            caminho = S / "escola" / "v0928" / "melhorar_p013.png"
        im = _abrir(caminho)
        ruim = com_buraco(medidas, ("escola/v0928:melhorar" if versao == "v0928" else f"saida/{versao}:melhorar"), 13)
        cor = LARANJA if ruim else AZUL
        r = _caber(_recorte(im, c13), 340, 240)
        cel = Image.new("RGB", (360, 330), FUNDO)
        d = ImageDraw.Draw(cel)
        d.rectangle([0, 0, 360, 60], fill=cor)
        for n, t in enumerate(_quebrar(titulo, _fonte(19, True), 350)[:2]):
            d.text((6, 4 + 26 * n), t, fill="white", font=_fonte(19, True))
        px, py = (360 - r.width) // 2, 72
        cel.paste(r, (px, py))
        if ruim:
            d.rounded_rectangle([px - 7, py - 7, px + r.width + 6, py + r.height + 6], radius=12,
                                outline=VERMELHO, width=5)
        linha.append(cel)
    grade = Image.new("RGB", (4 * 365, ((len(linha) + 3) // 4) * 335), FUNDO)
    for n, cel in enumerate(linha):
        grade.paste(cel, ((n % 4) * 365, (n // 4) * 335))
    partes.append(grade)
    _salvar(_empilhar(partes), saida / "1-bissecao-pagina-13.png", legendas,
            "Bisseção: a página 13 em dez versões do programa; os buracos aparecem a partir da etapa 3 da obra "
            "(26/10, e2321b16), com a regra da etapa 1 (175addb7).")

    # --- 2 e 3. o livro: 8 paginas, Melhorar e Magico pro, 4 faixas ----------------------------
    for n_img, filtro, nome, ajuste in ((2, "melhorar", "Melhorar", "Clareza \"bem forte\""),
                                        (3, "magico_pro", "Mágico pro", "Intensidade \"bem fraco\"")):
        nomes = [f"página {p}" for p in PAGS]
        cx = [caixas[p] for p in PAGS]
        partes = [_cabeca(f"Na escola de Jesus — {nome}", CINZA,
                          f"Livro novo (cópia), {nome} escolhido à mão, {ajuste}. Oito páginas com pintura, "
                          "só a pintura, o mesmo recorte e a mesma ordem nas quatro faixas; como sai no PDF. "
                          "Em vermelho: pintura com buracos brancos.")]
        for versao, rc, frase in (
                ("antes", ANTES, "A gravura era procurada e protegida: as pinturas saem inteiras."),
                ("hoje", DEPOIS, "Sem a procura: buracos brancos na água, no céu e nas roupas claras."),
                ("desfeita", DESFEITA, "Só a regra de antes de volta: igual ao ANTES."),
                ("conserto_c", CONSERTO_C, "O conserto C (procurar a gravura com \"Respeitar\" marcada + "
                                           "regra \"em volta é papel\"): também sai inteira.")):
            partes.append(_faixa(rc, frase, imgs(versao, filtro, PAGS), nomes, cx, 4, 330,
                                 marcar(versao, filtro, PAGS)))
        _salvar(_empilhar(partes), saida / f"{n_img}-livro-escola-{filtro.replace('_', '-')}.png", legendas,
                f"Na escola de Jesus, {nome}: oito pinturas antes, hoje, com só a mudança desfeita e com o conserto C.")

    # --- 4. letras finas (pagina 13) -------------------------------------------------------------
    LETRAS = (0.06, 0.535, 0.60, 0.60)
    partes = [_cabeca("As letras finas (o \"i\" e o \"t\")", CINZA,
                      "Na escola de Jesus, página 13, Melhorar \"bem forte\", o mesmo pedaço do texto (três "
                      "linhas, tamanho do PDF). Olhe o \"i\" de \"dia\", \"disse\", \"cidade\" e o \"t\" de "
                      "\"Profeta\".")]
    for versao, rc, frase in (
            ("antes", ANTES, "Letras inteiras."),
            ("hoje", DEPOIS, "O pingo e o pé do \"i\" e o meio do \"t\" somem; o acento de \"fôsse\" some."),
            ("desfeita", DESFEITA, "Letras inteiras de novo, igual ao ANTES."),
            ("conserto_c", CONSERTO_C, "Letras inteiras.")):
        im = _abrir(S / "escola" / versao / "melhorar_p013.png")
        r = _caber(_recorte(im, LETRAS), LARGURA - 60, 400)
        partes.append(_empilhar([_cabeca(rc[0], rc[1], frase), r], espaco=6))
    _salvar(_empilhar(partes), saida / "4-letras-finas-pagina-13.png", legendas,
            "As letras finas da página 13: antes, hoje, com só a mudança desfeita e com o conserto C.")

    # --- 5. Livro de Horas 47 --------------------------------------------------------------------
    horas = trab / "livros" / "horas.pdf"
    RECORTE_47 = (0.15, 0.03, 0.85, 0.25)
    partes = [_cabeca("Livro de Horas, página 47", CINZA,
                      "Outro livro do acervo (cópia), livro novo, Melhorar \"bem forte\" escolhido à mão. A "
                      "pintura das bodas de Caná, no alto da página, como sai no PDF.")]
    for versao, rc, frase in (
            ("antes", ANTES, "O prédio, o céu e as colunas atrás das figuras saem inteiros."),
            ("hoje", DEPOIS, "O prédio, o céu e riscos nas colunas viram branco puro."),
            ("desfeita", DESFEITA, "Igual ao ANTES."),
            ("conserto_c", CONSERTO_C, "Inteira, como o ANTES.")):
        im = _abrir(S / "horas" / versao / "melhorar_p047.png")
        ruim = com_buraco(medidas, f"horas/{versao}:melhorar", 47, 0.5)
        partes.append(_faixa(rc, frase, [im], ["página 47"], [RECORTE_47], 1, 1300,
                             {0} if ruim else set(), caixa_a=470))
    _salvar(_empilhar(partes), saida / "5-livro-de-horas-47.png", legendas,
            "Livro de Horas 47: antes, hoje, com só a mudança desfeita e com o conserto C.")

    # --- 6. Boecio: a mancha do verso --------------------------------------------------------------
    BOE = [3, 7, 8, 22, 33]
    partes = [_cabeca("Mancha do verso e papel (Boécio)", CINZA,
                      "Sobre a Consolação da Filosofia (cópia), páginas 3, 7, 8, 22 e 33, Melhorar \"bem forte\" "
                      "escolhido à mão, página inteira como sai no PDF, e embaixo o mesmo pedaço da página 33 "
                      "ampliado. Em vermelho: papel que não ficou branco (manchas cinza).")]
    for versao, rc, frase in (
            ("antes", ANTES, "Papel branco; a mancha do verso quase toda some (sobram pontinhos)."),
            ("hoje", DEPOIS, "Sobram faixas cinza entre as linhas e manchas cinza na margem (a mancha do verso "
                             "e o papel que não foi a branco)."),
            ("desfeita", DESFEITA, "Papel branco e a mancha do verso some, como no ANTES."),
            ("conserto_c", CONSERTO_C, "Igual ao \"só essa mudança desfeita\".")):
        ims = [_abrir(S / "boecio" / versao / f"melhorar_p{p:03d}.png") for p in BOE]
        sujas = {i for i, p in enumerate(BOE)
                 if ((medidas.get(f"boecio/{versao}:melhorar", {}).get(str(p)) or {}).get("papel_sujo_pct") or 0) >= 2}
        faixa = _faixa(rc, frase, ims, [f"página {p}" for p in BOE], [None] * 5, 5, 255, sujas, caixa_a=360)
        zoom = _caber(_recorte(ims[4], (0.08, 0.25, 0.60, 0.42)), LARGURA - 80, 330)
        partes.append(_empilhar([faixa, zoom], espaco=4))
    _salvar(_empilhar(partes), saida / "6-boecio-mancha-do-verso.png", legendas,
            "Boécio: antes, hoje, com só a mudança desfeita e com o conserto C (mancha do verso e papel).")

    # --- 7. quando a gravura nao e usada: o programa de antes sem a procura, e o print 10 ------------
    p10 = json.loads((trab / "medidas_p10.json").read_text(encoding="utf-8"))
    medidas.update(p10)
    partes = [_cabeca("Quando a gravura não é usada (página 13)", CINZA,
                      "Na escola de Jesus, página 13, só a pintura, como sai no PDF. Em cima, o programa de antes "
                      "com a caixinha \"Procurar gravura e letra\" desmarcada. Embaixo, o caso do seu print 10: "
                      "Mágico pro \"bem fraco\" com \"Limpar a folha\" do Automático e \"Respeitar as gravuras "
                      "achadas\" DESMARCADA. Em vermelho: com buracos brancos.")]
    casos = (
        (("ANTES da mudança (26/10, ddd4d74a), \"Procurar gravura e letra\" desmarcada", AZUL),
         S / "antes_sem_procurar" / "melhorar_p013.png", "saida/antes_sem_procurar:melhorar",
         "Melhorar \"bem forte\". Sem a procura, o programa de antes também fazia os buracos: o passo da "
         "limpeza é o mesmo. Só que de fábrica a caixinha vinha marcada."),
        (("DEPOIS da mudança (hoje): o caso do print 10", LARANJA), S / "p10" / "hoje" / "magico_pro_p013.png",
         "p10/hoje:magico_pro", "A gravura é achada, mas a caixinha desmarcada manda o filtro valer na página "
                                "inteira (D-586): buracos."),
        (("Só essa mudança desfeita: o caso do print 10", VERDE), S / "p10" / "desfeita" / "magico_pro_p013.png",
         "p10/desfeita:magico_pro", "Igual a hoje: desfazer a mudança não muda este caso."),
        (("Conserto C do verificador: o caso do print 10", ROXO), S / "p10" / "conserto_c" / "magico_pro_p013.png",
         "p10/conserto_c:magico_pro", "A regra \"em volta é papel\" tira a maior parte dos buracos; sobram "
                                      "alguns perto da beirada."),
    )
    for rc, arq, chave, frase in casos:
        ruim = com_buraco(medidas, chave, 13, 4.0)
        partes.append(_faixa(rc, frase, [_abrir(arq)], ["página 13"], [caixas[13]], 1, 1000,
                             {0} if ruim else set(), caixa_a=430))
    _salvar(_empilhar(partes), saida / "7-quando-a-gravura-nao-e-usada.png", legendas,
            "Página 13: o programa de antes sem a procura da gravura, e o caso do print 10 (caixinha "
            "\"Respeitar\" desmarcada) hoje, com só a mudança desfeita e com o conserto C.")

    (saida / "legendas.json").write_text(json.dumps(legendas, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ok", saida)


if __name__ == "__main__":
    main()
