"""Monta as imagens das perguntas 3 e 4 (relatorios/girar-capa-provas) com o que gerar_provas.py gravou.

    python montar_provas.py <pasta crua (com antigo/ e novo/)> <pasta de saída>

Cada imagem tem, no alto, uma faixa colorida com o rótulo em letra grande ("ANTES do clique",
"DEPOIS — jeito antigo", "DEPOIS — jeito novo"...) e, embaixo dela, o que olhar. A folha que
interessa fica circulada em vermelho. Largura entre 900 e 1600 pontos.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTE = "C:/Windows/Fonts/segoeui.ttf"
FONTE_N = "C:/Windows/Fonts/segoeuib.ttf"
LARGURA = 1500
FUNDO = (250, 249, 246)
VERMELHO = (220, 20, 20)
CORES = {"antes": (60, 90, 150), "antigo": (190, 90, 10), "novo": (25, 130, 60),
         "fica": (190, 90, 10), "pagina": (25, 130, 60)}


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


def _cabeca(rotulo: str, cor, legenda: str, largura: int = LARGURA) -> Image.Image:
    """A faixa colorida com o rótulo grande e, embaixo, a legenda (o que olhar)."""
    f_rot, f_leg = _fonte(46, True), _fonte(26)
    linhas = _quebrar(legenda, f_leg, largura - 40)
    img = Image.new("RGB", (largura, 86 + 14 + 36 * len(linhas) + 10), FUNDO)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, largura, 86], fill=cor)
    d.text((20, 12), rotulo, fill="white", font=f_rot)
    for n, texto in enumerate(linhas):
        d.text((20, 100 + 36 * n), texto, fill=(30, 30, 30), font=f_leg)
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


def _grade(imagens: list[Image.Image], numeros: list[int], por_linha: int, caixa: int,
           circular: set[int], moldura: bool = True, legenda_extra: dict | None = None) -> Image.Image:
    """Páginas (ou miniaturas) em quadros iguais, com "página N" grande em cima de cada uma e um
    círculo vermelho em volta das de `circular`."""
    f_num = _fonte(30, True)
    topo, margem = 46, 14
    cel_l, cel_a = caixa + 2 * margem, caixa + topo + 2 * margem
    linhas = (len(imagens) + por_linha - 1) // por_linha
    img = Image.new("RGB", (cel_l * por_linha, cel_a * linhas), FUNDO)
    d = ImageDraw.Draw(img)
    for n, (pagina, numero) in enumerate(zip(imagens, numeros)):
        x0, y0 = (n % por_linha) * cel_l, (n // por_linha) * cel_a
        texto = (legenda_extra or {}).get(numero, f"página {numero}")
        cor = VERMELHO if numero in circular else (30, 30, 30)
        d.text((x0 + cel_l / 2, y0 + 6), texto, fill=cor, font=f_num, anchor="mt")
        p = _caber(pagina, caixa, caixa)
        px, py = x0 + (cel_l - p.width) // 2, y0 + topo + margem + (caixa - p.height) // 2
        img.paste(p, (px, py))
        if moldura:
            d.rectangle([px - 1, py - 1, px + p.width, py + p.height], outline=(150, 150, 150))
        if numero in circular:
            d.ellipse([x0 + 2, y0 + topo - 4, x0 + cel_l - 3, y0 + cel_a - 3], outline=VERMELHO, width=7)
    return img


def _abrir(pasta: Path, nomes: list[str]) -> list[Image.Image]:
    return [Image.open(pasta / n).convert("RGB") for n in nomes]


def _sem_numero(mini: Image.Image) -> Image.Image:
    """A miniatura sem o número miúdo de baixo (o número grande vai em cima)."""
    return mini.crop((0, 0, mini.width, round(mini.height * 0.80)))


def _tela(pasta: Path, nome: str, largura: int = LARGURA - 40) -> Image.Image:
    img = Image.open(pasta / nome).convert("RGB")
    return img.resize((largura, round(img.height * largura / img.width)), Image.LANCZOS)


def _area_da_folha(pasta: Path, nome: str, largura: int) -> Image.Image:
    """Só a área da folha na tela do Dividir (sem os painéis), para o resumo."""
    img = Image.open(pasta / nome).convert("RGB")
    corte = img.crop((90, 80, 2110, 1165))
    return corte.resize((largura, round(corte.height * largura / corte.width)), Image.LANCZOS)


def _salvar(img: Image.Image, destino: Path, legendas: dict, legenda: str) -> None:
    assert 900 <= img.width <= 1600, (destino, img.width)
    img.save(destino, optimize=True)
    legendas[destino.name] = legenda


def pergunta_4(cru: Path, saida: Path, legendas: dict) -> None:
    antigo, novo = cru / "antigo", cru / "novo"
    numeros = list(range(1, 9))
    situacoes = (
        ("antes", "ANTES do clique", novo, "q4-novo-antes",
         "Gradus Primus (cópia). Estou na página 3 (borda azul). A página 6 é uma folha que ficou "
         "INTEIRA (\"não dividir esta\"): está circulada em vermelho. As outras são metades de folhas "
         "divididas. Tudo em pé."),
        ("antigo", "DEPOIS — jeito antigo", antigo, "q4-antigo-depois",
         "O que o teste antigo cobra (programa sem o conserto). Na página 3, \"daqui em diante\" + "
         "¼ à direita: as páginas 3, 4, 5, 7 e 8 deitaram, mas a folha inteira (página 6, em "
         "vermelho) NÃO girou: ficou em pé."),
        ("novo", "DEPOIS — jeito novo", novo, "q4-novo-depois",
         "A sua resposta \"Giram também\" (programa com o conserto). O mesmo clique: as páginas 3, 4, "
         "5, 7 e 8 deitaram e a folha inteira (página 6, em vermelho) TAMBÉM girou, junto com elas."),
    )
    resumo = []
    for n, (chave, rotulo, pasta, prefixo, legenda) in enumerate(situacoes, start=1):
        minis = [_sem_numero(m) for m in _abrir(pasta, [f"mini-{prefixo}-{i}.png" for i in numeros])]
        grade = _grade(minis, numeros, 8, 150, {6}, moldura=False)
        img = _empilhar([_cabeca(rotulo, CORES[chave], "Miniaturas da tira (como o programa "
                                 "mostra). " + legenda), grade])
        _salvar(img, saida / f"q4-{n}-miniaturas-{chave}.png", legendas,
                f"{rotulo}. Miniaturas das páginas 1 a 8. {legenda}")
        paginas = _abrir(pasta, [f"pdf-{prefixo}-{i}.png" for i in numeros])
        grade = _grade(paginas, numeros, 4, 330, {6})
        img = _empilhar([_cabeca(rotulo, CORES[chave], "As páginas como saem no PDF. " + legenda),
                         grade])
        _salvar(img, saida / f"q4-{n + 3}-pdf-{chave}.png", legendas,
                f"{rotulo}. Páginas 1 a 8 como saem no PDF. {legenda}")
        resumo.append(_empilhar([_cabeca(rotulo, CORES[chave], {
            "antes": "Página 6 = folha inteira (em vermelho). Tudo em pé.",
            "antigo": "Na página 3, \"daqui em diante\" + ¼: a página 6 NÃO gira.",
            "novo": "O mesmo clique: a página 6 gira junto (\"Giram também\")."}[chave]),
            _grade(paginas, numeros, 8, 155, {6})], espaco=6))
    img = _empilhar([_cabeca("Pergunta 4 — resumo", (40, 40, 40),
                             "Gradus, folha 4 sem dividir (página 6). Na página 3: \"daqui em diante\" "
                             "+ ¼ à direita. Páginas 1 a 8 como saem no PDF."), *resumo])
    _salvar(img, saida / "q4-resumo.png", legendas,
            "Resumo da pergunta 4: antes, jeito antigo e jeito novo, um embaixo do outro (páginas do PDF).")


def pergunta_3(cru: Path, saida: Path, legendas: dict) -> None:
    novo = cru / "novo"
    numeros = [1, 18, 19, 20, 21]
    extra = {1: "1 (capa)"}
    situacoes = (
        ("antes", "ANTES do clique", "tela-q3-antes-dividir.png", "q3-antes-paginas",
         "Ferramenta Dividir, vista \"Duas lado a lado\", folha 10 (páginas 18 e 19, em vermelho). "
         "A folha aparece inteira, com a linha azul no meio. Tudo em pé.", None),
        ("fica", "DEPOIS — \"Fica como está\"", "tela-q3-fica-dividir.png", "q3-fica-paginas",
         "O programa de hoje (com o conserto). No Dividir com \"Duas lado a lado\", \"todas as "
         "folhas\" + ¼ à direita: as 70 folhas giram INTEIRAS e a linha azul continua no mesmo "
         "lugar. Ela passa a cortar o meio das duas páginas deitadas: cada página do livro sai como "
         "uma tira estreita com metade da página 18 e metade da 19 (a confusão do seu print a-70).",
         None),
        ("pagina", "DEPOIS — \"Página por página também\"", "tela-q3-pagina-dividir.png",
         "q3-pagina-paginas",
         "SIMULAÇÃO: esse jeito ainda não existe no Dividir. Resultado feito pelo caminho que já "
         "gira página por página (Cortar as bordas, página 18, \"todas as páginas\" + ¼ à direita, "
         "D-636). Cada página deita sozinha, inteira, sem pedaço da vizinha; a capa gira inteira. "
         "Na tela do Dividir de hoje (foto de cima) a folha grande continua em pé, como veio no "
         "scan, com a linha no mesmo lugar; só as miniaturas mostram as páginas deitadas.",
         None),
    )
    resumo = []
    for n, (chave, rotulo, tela, prefixo, legenda, _) in enumerate(situacoes, start=1):
        minis = [_sem_numero(m) for m in _abrir(novo, [f"mini-{prefixo}-{i}.png" for i in numeros])]
        paginas = _abrir(novo, [f"pdf-{prefixo}-{i}.png" for i in range(1, 6)])
        f_sub = _fonte(30, True)

        def _titulo(texto: str) -> Image.Image:
            t = Image.new("RGB", (LARGURA - 40, 46), FUNDO)
            ImageDraw.Draw(t).text((0, 4), texto, fill=(30, 30, 30), font=f_sub)
            return t

        img = _empilhar([
            _cabeca(rotulo, CORES[chave], legenda),
            _titulo("1) A tela do Dividir (\"Duas lado a lado\"), folha 10:"),
            _tela(novo, tela),
            _titulo("2) As miniaturas das páginas (tira da área de trabalho):"),
            _grade(minis, numeros, 5, 170, {18, 19}, moldura=False, legenda_extra=extra),
            _titulo("3) As páginas como saem no PDF:"),
            _grade(paginas, numeros, 5, 260, {18, 19}, legenda_extra=extra),
        ])
        _salvar(img, saida / f"q3-{n}-{chave}.png", legendas, f"{rotulo}. {legenda}")
        resumo.append(_empilhar([
            _cabeca(rotulo, CORES[chave], {
                "antes": "Dividir, \"Duas lado a lado\", folha 10 (páginas 18 e 19). Tudo em pé.",
                "fica": "As folhas giram inteiras; a linha corta as duas páginas ao meio: "
                        "cada página sai uma tira com metade de cada uma.",
                "pagina": "SIMULAÇÃO (pelo \"todas as páginas\" da área de trabalho): cada página "
                          "deita sozinha e inteira. A tela do Dividir não muda."}[chave]),
            _area_da_folha(novo, tela, 640),
            _grade(paginas, numeros, 5, 260, {18, 19}, legenda_extra=extra)], espaco=6))
    img = _empilhar([_cabeca("Pergunta 3 — resumo", (40, 40, 40),
                             "Dividir com \"Duas lado a lado\", \"todas as folhas\" + ¼ à direita. "
                             "Em cada parte: a tela do Dividir e as páginas como saem no PDF."),
                     *resumo])
    _salvar(img, saida / "q3-resumo.png", legendas,
            "Resumo da pergunta 3: antes, \"Fica como está\" e \"Página por página também\" "
            "(simulação), um embaixo do outro (tela do Dividir e páginas do PDF).")


def main() -> None:
    cru, saida = Path(sys.argv[1]), Path(sys.argv[2])
    saida.mkdir(parents=True, exist_ok=True)
    legendas: dict = {}
    pergunta_4(cru, saida, legendas)
    pergunta_3(cru, saida, legendas)
    for nome in ("estado-q4-antigo.json",):
        (saida / nome).write_bytes((cru / "antigo" / nome).read_bytes())
    for nome in ("estado-q4-novo.json", "estado-q3-novo.json"):
        (saida / nome).write_bytes((cru / "novo" / nome).read_bytes())
    (saida / "legendas.json").write_text(json.dumps(legendas, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
    print("ok", saida)


if __name__ == "__main__":
    main()
