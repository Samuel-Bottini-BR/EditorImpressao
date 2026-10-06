"""A imagem-tabela da pergunta-resumo (rodada 2): as 16 paginas da rodada 1,
a resposta do Samuel, o aviso de hoje e o criterio novo (criterio.py).
Uso: python tabela_img.py   (grava ../img/criterio-tabela.jpg e imprime a tabela)"""
import json

from PIL import Image, ImageDraw

import comum
import criterio as C
from figuras import DESTINO, _fonte

SINAIS = json.loads((comum.TRABALHO / "sinais-rodada2.json").read_text(encoding="utf-8"))
MOTIVO = {"desenho apagado": "apagou desenho", "figura além da gravura achada": "figura/mancha fora da gravura",
          "faixa escura na beirada": "faixa escura na beirada"}
# (nome, base, resposta do Samuel)
LINHAS = [
    ("Palatino 76", "palatino_p076__inteira", True), ("Palatino 67", "palatino_p067__inteira", True),
    ("Palatino 66", "palatino_p066__inteira", True), ("Siebmacher 7", "siebmacher_p007__esquerda", True),
    ("ljs47 103", "ljs47_p103__inteira", True), ("Marial 454", "marial_p454__inteira", True),
    ("Antiphon 260", "antiphon_p260__inteira", True), ("Pesel 21", "pesel_p021__inteira", True),
    ("Matemática 32", "matematica_p032__inteira", True),
    ("Graduale 222", "graduale_p222__inteira", False), ("Horas 14", "horas_p014__inteira", False),
    ("Graduale 588", "graduale_p588__inteira", False), ("Palatino 10", "palatino_p010__inteira", False),
    ("Boécio 7", "boecio_p007__inteira", False), ("Horas 175", "horas_p175__inteira", False),
    ("Rhetorica 34", "rhetorica_p034__inteira", False),
]
VERDE, VERMELHO, CINZA = (214, 240, 214), (248, 214, 210), (245, 245, 245)


def main() -> None:
    cols = [("Página", 260), ("Sua resposta", 250), ("Hoje", 250), ("Critério novo", 270), ("Por quê (critério novo)", 770)]
    alto = 58
    tela = Image.new("RGB", (1800, alto * (len(LINHAS) + 2) + 20), "white")
    d = ImageDraw.Draw(tela)
    f, fb = _fonte(27), _fonte(27, True)
    x = 0
    for nome, w in cols:
        d.rectangle([x, 0, x + w, alto], fill=(225, 225, 225), outline=(180, 180, 180))
        d.text((x + 10, 14), nome, font=fb, fill=(20, 20, 20))
        x += w
    acertos_hoje = acertos_novo = 0
    for i, (nome, base, resp) in enumerate(LINHAS, start=1):
        s = SINAIS[base]
        hoje, novo = bool(s["aviso_hoje"]), C.vai_para_a_lista(s)
        acertos_hoje += hoje == resp
        acertos_novo += novo == resp
        mot = ", ".join(MOTIVO[m] for m in C.motivos(s)) or "quase nada apagado"
        celulas = [(nome, CINZA), ("vai" if resp else "não vai", CINZA),
                   ("vai" if hoje else "não vai", VERDE if hoje == resp else VERMELHO),
                   ("vai" if novo else "não vai", VERDE if novo == resp else VERMELHO), (mot, CINZA)]
        y = alto * i
        x = 0
        for (txt, cor), (_n, w) in zip(celulas, cols):
            d.rectangle([x, y, x + w, y + alto], fill=cor, outline=(200, 200, 200))
            d.text((x + 10, y + 14), txt, font=f, fill=(20, 20, 20))
            x += w
        print(f"{nome:15s} resposta={'vai' if resp else 'nao'} hoje={'vai' if hoje else 'nao'} "
              f"novo={'vai' if novo else 'nao'} {mot}")
    y = alto * (len(LINHAS) + 1) + 10
    d.text((10, y), f"Verde: igual à sua resposta. Vermelho: diferente.   Hoje: {acertos_hoje} de 16.   "
                    f"Critério novo: {acertos_novo} de 16.", font=fb, fill=(20, 20, 20))
    DESTINO.mkdir(parents=True, exist_ok=True)
    tela.save(DESTINO / "criterio-tabela.jpg", quality=90)
    print("hoje", acertos_hoje, "novo", acertos_novo)


if __name__ == "__main__":
    main()
