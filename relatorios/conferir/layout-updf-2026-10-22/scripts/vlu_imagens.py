"""Monta as imagens (JPG) da conferência lyupdf a partir dos prints do verificador (prints/).
Uso: python vlu_imagens.py   (na pasta scripts/)."""
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent.parent
P = AQUI / "prints"
IMG = AQUI / "img"
IMG.mkdir(exist_ok=True)
CINZA = (60, 60, 60)


def ler(rel):
    im = cv2.imread(str(P / rel))
    assert im is not None, rel
    return im


def corte(im, x0, y0, x1, y1, vezes=1.0):
    c = im[y0:y1, x0:x1]
    if vezes != 1.0:
        c = cv2.resize(c, None, fx=vezes, fy=vezes,
                       interpolation=cv2.INTER_NEAREST if vezes >= 2 else cv2.INTER_CUBIC)
    return c


def legenda(im, texto, alto=44):
    faixa = np.full((alto, im.shape[1], 3), 245, np.uint8)
    cv2.putText(faixa, texto, (12, alto - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2, cv2.LINE_AA)
    return np.vstack([im, faixa])


def lado(*ims, vao=16):
    h = max(i.shape[0] for i in ims)
    out = []
    for k, i in enumerate(ims):
        if i.shape[0] < h:
            i = np.vstack([i, np.full((h - i.shape[0], i.shape[1], 3), 245, np.uint8)])
        out.append(i)
        if k < len(ims) - 1:
            out.append(np.full((h, vao, 3), 245, np.uint8))
    return np.hstack(out)


def gravar(im, nome, largura_max=2000):
    if im.shape[1] > largura_max:
        f = largura_max / im.shape[1]
        im = cv2.resize(im, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    q = 90
    while True:
        cv2.imwrite(str(IMG / nome), im, [cv2.IMWRITE_JPEG_QUALITY, q])
        if (IMG / nome).stat().st_size < 1_400_000 or q <= 60:
            break
        q -= 8
    print(nome, im.shape[1], "x", im.shape[0], (IMG / nome).stat().st_size // 1024, "KB")


# 1. o par: a beirada de baixo das duas páginas, ampliada (antes x depois)
a = ler("livro-antigo/1600x821-2-duas.png")
d = ler("livro-novo/1600x821-2-duas.png")
gravar(lado(legenda(corte(a, 690, 600, 1010, 730, 3), "ANTES: a da direita termina mais alto"),
            legenda(corte(d, 690, 610, 1010, 740, 3), "DEPOIS: as duas terminam juntas")),
       "lu-par-zoom.jpg")
gravar(legenda(d, "DEPOIS, 1600x821: Graduale folhas 302 e 303, Duas lado a lado + Caber a pagina"), "lu-par-depois.jpg")
gravar(legenda(a, "ANTES (codigo 2eeec20), 1600x821: o mesmo par, alturas 545 e 528 pixels"), "lu-par-antes.jpg")

# 2. tamanho da página na janela maximizada (antes fixa em 620 pixels)
a = ler("livro-antigo/maximizada-1-uma-pagina.png")
d = ler("livro-novo/maximizada-1-uma-pagina.png")
gravar(lado(legenda(corte(a, 560, 140, 1360, 930, 1), "ANTES: 620 pixels de altura"),
            legenda(corte(d, 560, 140, 1360, 930, 1), "DEPOIS: 746 pixels, a altura toda")),
       "lu-maximizada-zoom.jpg")
gravar(legenda(corte(d, 860, 340, 1180, 520, 3), "DEPOIS, ampliado 3x: folha 301, nitidez 1,00"), "lu-nitida-zoom.jpg")
gravar(legenda(d, "DEPOIS, maximizada: Uma pagina + Caber a pagina (folha 301)"), "lu-maximizada-depois.jpg")

# 3. a barra de baixo e os jeitos de caber
d = ler("livro-novo/1600x821-2-duas.png")
gravar(legenda(corte(d, 130, 760, 1590, 818, 1.4), "A barra de baixo do livro aberto (1600x821)"), "lu-barra-zoom.jpg")
quatro = []
for arq, txt in (("1600x821-2-duas.png", "Caber a pagina"), ("1600x821-3-duas-altura.png", "Caber a altura"),
                 ("1600x821-4-duas-largura.png", "Caber a largura"), ("1600x821-5-duas-real.png", "Tamanho real")):
    im = corte(ler("livro-novo/" + arq), 125, 140, 1590, 821, 0.62)
    quatro.append(legenda(im, txt))
gravar(np.vstack([lado(quatro[0], quatro[1]), np.full((16, lado(quatro[0], quatro[1]).shape[1], 3), 245, np.uint8),
                  lado(quatro[2], quatro[3])]), "lu-caber-4.jpg")
gravar(legenda(ler("livro-novo/1600x821-6-duas-sem-rolar.png"), "Duas lado a lado SEM Rolar sem parar: so o par da vez"),
       "lu-sem-rolar.jpg")
gravar(legenda(ler("livro-novo/1600x821-8-duas-sem-rolar-depois-da-roda.png"),
               "Depois de 3 voltinhas da roda, sem Rolar sem parar: passou de par em par ate 308-309"),
       "lu-roda.jpg")
# (só a barra: o livro reabre na folha 1, a capa de couro, que não entra em conferência)
gravar(legenda(corte(ler("livro-novo/1600x821-10-reaberto-com-a-escolha.png"), 140, 762, 1590, 818, 1.4),
               "Programa fechado e aberto de novo: a barra voltou em Duas lado a lado + Caber a largura"),
       "lu-escolha-guardada.jpg")

# 4. a grade Todas as páginas: a folha 301, ampliada 3x
a = ler("livro-antigo/1600x821-9-todas-as-paginas.png")
d = ler("livro-novo/1600x821-9-todas-as-paginas.png")
gravar(lado(legenda(corte(a, 1366, 507, 1497, 692, 3), "ANTES: 28 s, nitidez 0,69"),
            legenda(corte(d, 1366, 439, 1497, 625, 3), "DEPOIS: 1,5 s, nitidez 0,97")),
       "lu-grade-zoom.jpg")
gravar(legenda(d, "DEPOIS: Todas as paginas (1600x821). O quadro azul esta na 300; o livro estava na 301"),
       "lu-grade-depois.jpg")

# 5. tela cheia: as opções
tc = "tela-cheia/"
d = ler(tc + "2-tela-cheia-preto_e_branco-1600x821.png")
gravar(legenda(corte(d, 1228, 80, 1600, 720, 1.6), "Preto e branco: as opcoes a direita"), "lu-tc-opcoes-zoom.jpg")
gravar(legenda(d, "Boecio pag. 7: endireitada e cortada (fabrica), Preto e branco, tela cheia 1600x821"),
       "lu-tc-pb.jpg")
gravar(legenda(ler(tc + "4-lista-dos-jeitos.png"), "Jeito do preto e branco (rola: 14 itens)", 40), "lu-tc-lista.jpg")
gravar(legenda(ler(tc + "3-tela-cheia-pb-opcoes-mexidas-maximizada.png"),
               "Maximizada: Preto e branco + So as letras + Limpeza media + Wolf do ScanTailor (mexido, antes de Usar)"),
       "lu-tc-mexida-max.jpg")
gravar(legenda(ler(tc + "1-painel-filtro-preto-e-branco-mais-ajustes.png"),
               "O painel Filtro da pagina: as mesmas opcoes (Mais ajustes aberto)"), "lu-tc-painel.jpg")
m = ler(tc + "2-tela-cheia-melhorar-1600x821.png")
gravar(legenda(corte(m, 1228, 80, 1600, 320, 1.6), "Melhorar: Mais ajustes = Letra clara + Reduzir cores"),
       "lu-tc-melhorar-zoom.jpg")
gravar(legenda(m, "Melhorar na tela cheia (1600x821): o cartao do Magico pro fica cortado embaixo, na fila"),
       "lu-tc-melhorar.jpg")

# 6. tela cheia x PDF gerado
v = ler(tc + "6-tela-cheia-pagina-7.png")
r = ler(tc + "6-pdf-gerado-pagina-7.png")
x = ler(tc + "6-diferenca-tela-x-pdf.png")
y0, y1, x0, x1 = 150, 330, 60, 330
gravar(lado(legenda(corte(v, x0, y0, x1, y1, 3), "TELA CHEIA"), legenda(corte(r, x0, y0, x1, y1, 3), "PDF GERADO"),
            legenda(corte(x, x0, y0, x1, y1, 3), "vermelho: so na tela; azul: so no PDF")),
       "lu-tc-igual-zoom.jpg")
gravar(lado(legenda(v, "tela cheia"), legenda(r, "PDF gerado"), legenda(x, "diferenca")), "lu-tc-igual-inteira.jpg")
