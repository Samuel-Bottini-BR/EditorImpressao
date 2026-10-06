"""Rodada 3: desenho do aviso do "Só o texto achado" (PROPOSTA; nao e a tela
real). Quatro passos em caixas + o exemplo do Palatino 10 (imagem da rodada 2).
Uso: python aviso_img.py"""
from PIL import Image, ImageDraw

import comum
from figuras import DESTINO, _fonte

PASSOS = [
    ("1. Quando", "Só quando você escolhe 'Só o texto achado' (para o livro, na tela 'O que fazer', "
                  "ou para uma página, na aba Filtro). Nos outros jeitos, este aviso não existe."),
    ("2. Uma vez", "Aparece UMA vez, na hora em que você escolhe, numa caixa com este texto:"),
    ("", "\"Neste jeito, só fica o texto que eu achei. Tudo o que não é texto nem gravura vai para o "
         "branco: letra grande, moldura, música, números da margem, tabelas e desenhos que eu não "
         "reconheci. Confira o livro antes de imprimir.\""),
    ("3. Fica escrito", "Depois fica escrito nas observações do livro, na tela de conferir, para não "
                        "ser esquecido."),
    ("4. Páginas", "E as páginas em que sumiu algo grande (moldura, letra grande, música, desenho) "
                   "vão para 'Para revisar', uma por uma. Exemplo abaixo: Palatino 10."),
    ("Por quê", "Porque esse jeito apaga tudo fora das linhas de texto: nas 59 páginas testadas, "
                "estragou 43. O aviso do livro avisa antes; o 'Para revisar' mostra onde."),
]


def quebrar(d, texto, fonte, largura):
    linhas, atual = [], ""
    for p in texto.split():
        t = (atual + " " + p).strip()
        if d.textlength(t, font=fonte) > largura:
            linhas.append(atual)
            atual = p
        else:
            atual = t
    return linhas + [atual]


def main() -> None:
    tela = Image.new("RGB", (1800, 1600), "white")
    d = ImageDraw.Draw(tela)
    d.text((10, 8), "Como vai funcionar o aviso do 'Só o texto achado' (proposta; desenho, não é a tela real)",
           font=_fonte(30, True), fill=(20, 20, 20))
    y = 60
    for tit, txt in PASSOS:
        f = _fonte(27, False) if tit else _fonte(27, False)
        linhas = quebrar(d, txt, f, 1440)
        alto = 20 + 36 * len(linhas)
        cor = (255, 246, 214) if not tit else (238, 244, 252)
        d.rounded_rectangle([10, y, 1790, y + alto], 10, fill=cor, outline=(170, 170, 170))
        if tit:
            d.text((24, y + 10), tit, font=_fonte(27, True), fill=(20, 60, 140))
        for k, l in enumerate(linhas):
            d.text((330, y + 10 + 36 * k), l, font=f, fill=(25, 25, 25))
        y += alto + 12
    ex = Image.open(comum.PASTA.parent / "rodada-2" / "img" / "resp-palatino010-so-texto.jpg").convert("RGB")
    ex = ex.resize((1780, round(ex.height * 1780 / ex.width)))
    tela.paste(ex, (10, y + 6))
    tela = tela.crop((0, 0, 1800, y + 6 + ex.height + 6))
    tela.save(DESTINO / "aviso-so-texto.jpg", quality=88)
    print(tela.size, (DESTINO / "aviso-so-texto.jpg").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
