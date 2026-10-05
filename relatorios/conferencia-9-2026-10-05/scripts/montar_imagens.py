"""Imagens da conferencia 9 (05/10/2026): copias reduzidas/recortadas das imagens prontas do D3
(relatorios/fase2-geometria-d3-2026-10-05/imagens). Nenhuma pagina e processada aqui."""
from pathlib import Path
from PIL import Image

AQUI = Path(__file__).resolve().parent.parent
ORIGEM = AQUI.parent / "fase2-geometria-d3-2026-10-05" / "imagens"
SAIDA = AQUI / "cartoes"
SAIDA.mkdir(exist_ok=True)


def gravar(im, nome, largura=None):
    im = im.convert("RGB")
    if largura and im.width > largura:
        im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)
    im.save(SAIDA / nome, quality=82, optimize=True)


# paginas esticadas 5x na altura (endireitar)
for pag in ["horas_p011", "horas_p047", "horas_p027", "palatino_p057"]:
    gravar(Image.open(ORIGEM / f"esticada_{pag}.jpg"), f"esticada_{pag}.jpg", 900)

# so a fileira de cima (onde cada um divide a folha)
for pag in ["siebmacher_p007", "siebmacher_p009", "opusmajus_p256"]:
    im = Image.open(ORIGEM / f"{pag}.jpg")
    gravar(im.crop((0, 0, im.width, 668)), f"divisao_{pag}.jpg", 1300)

# ampliacoes de onde a tesoura do ScanTailor passa (ja sao pequenas)
for nome in ["corte_st_opusmajus_p256_esq", "corte_st_escola_p007_dir", "corte_st_graduale_p221_dir"]:
    gravar(Image.open(ORIGEM / f"{nome}.jpg"), f"{nome}.jpg")

for f in sorted(SAIDA.iterdir()):
    print(f.name, Image.open(f).size, f.stat().st_size // 1024, "KB")
