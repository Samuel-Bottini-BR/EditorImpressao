# Gera um arquivo HTML unico, com as imagens embutidas (data URI), para mandar ao Kaique.
# Parte de resultados.html e da pasta img/. Rodar de dentro de relatorios/.
import base64, io, re
from PIL import Image
BASE = "resultados-2026-09-30/"
LARG = 1500          # largura maxima de cada imagem embutida (arquivo leve para mandar)
QUAL = 80
html = open(BASE + "resultados.html", encoding="utf-8").read()

# O cartao do Preto e branco passa a mostrar a comparacao com a moldura dourada (decisao de 30/09).
TROCA_IMG = {"6-preto-e-branco": "conferencia-2-2026-09-30/pb-novo/pb-horas026.jpg"}
html = html.replace(
    '["6-preto-e-branco","Preto e branco: a moldura vira desenho","No Preto e branco, a moldura dourada sai como desenho (traço preto, fundo branco) em vez de mancha preta. Ainda falha em alguns trechos da linha."]',
    '["6-preto-e-branco","Preto e branco: texto nítido, moldura com a cor","No Preto e branco o texto sai preto e nítido e o papel branco. Decidido em 30/09: a moldura dourada mantém a cor original, como na imagem do meio (\\"ANTES\\"); a da direita (moldura em traço preto) fica só como opção. Ainda falta aplicar essa decisão no programa."]')
html = html.replace(
    '["n2-foto-pb","Foto no Preto e branco","A foto da estátua fica ruim no Preto e branco. Ainda vamos decidir se foto sai em tons de cinza ou em pontinhos, como jornal. (Opus Majus, página 20)"]',
    '["n2-foto-pb","Foto no Preto e branco","A foto da estátua fica ruim no Preto e branco. Decidido em 30/09: foto e pintura vão sair em tons de cinza. Ainda falta aplicar. (Opus Majus, página 20)"]')
assert "texto nítido, moldura com a cor" in html and "Decidido em 30/09: foto" in html

nomes = re.findall(r'\["([0-9a-z-]+)","', html)
dados = {}
for n in nomes:
    caminho = TROCA_IMG.get(n, BASE + "img/" + n + ".jpg")
    img = Image.open(caminho).convert("RGB")
    if img.width > LARG:
        img = img.resize((LARG, int(img.height * LARG / img.width)), Image.LANCZOS)
    b = io.BytesIO(); img.save(b, "JPEG", quality=QUAL, optimize=True)
    dados[n] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
js = "const IMAGENS = {" + ",".join(f'"{k}":"{v}"' for k, v in dados.items()) + "};\n"
html = html.replace("<script>\n", "<script>\n" + js, 1)
assert 'src="img/${img}.jpg"' in html
html = html.replace('src="img/${img}.jpg"', 'src="${IMAGENS[img]}"')
html = html.replace("<title>Editor de Impressão - resultados</title>", "<title>Editor de Impressão - resultados (30/09/2026)</title>")
open("Editor-de-Impressao-resultados-2026-09-30.html", "w", encoding="utf-8").write(html)
print(len(nomes), "imagens;", round(len(html.encode()) / 1e6, 1), "MB")
