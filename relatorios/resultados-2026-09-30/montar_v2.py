# Segunda versao da pagina de resultados (30/09/2026): mais exemplos aprovados pelo Samuel
# nas conferencias 1, 2 e 3, e os pedidos de mudanca. Rodar de dentro de relatorios/.
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import shutil
C = Path("conferir")
L = C/"fase1-1.2-ligacao-2026-09-30/2-depois-magico-pro/1.2-2026-09-30-0023/paineis"
OP = C/"fase1-1.2-opcoes-2026-09-30/resultado"
TF = C/"fase1-2026-09-29-1826/resultado"
F = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 44)
LARG = 1100
def ajusta(img): return img.resize((LARG, int(img.height*LARG/img.width)), Image.LANCZOS)
def rotulo(img, t, cor):
    n = Image.new("RGB", (img.width, img.height+70), "white"); n.paste(img, (0,70))
    d = ImageDraw.Draw(n); d.rectangle([0,0,img.width,70], fill=cor); d.text((18,10), t, fill="white", font=F); return n
def par(a, b, ta, tb, cor_b):
    a = rotulo(ajusta(Image.open(a).convert("RGB")), ta, (120,120,120))
    b = rotulo(ajusta(Image.open(b).convert("RGB")), tb, cor_b)
    l = Image.new("RGB", (a.width+b.width+20, max(a.height,b.height)), "white"); l.paste(a,(0,0)); l.paste(b,(a.width+20,0)); return l
def salvar(nome, linhas):
    t = Image.new("RGB", (linhas[0].width, sum(x.height for x in linhas)+30*(len(linhas)-1)), "white"); y = 0
    for x in linhas: t.paste(x,(0,y)); y += x.height+30
    t.save(f"resultados-2026-09-30/img2/{nome}.jpg", quality=88); print("ok", nome)
VERDE = (46,125,50)
# pares com pagina inteira + detalhe (paineis prontos)
def com_detalhe(nome, orig, res, tb="DEPOIS (programa)"):
    salvar(nome, [par(f"{orig}.jpg", f"{res}.jpg", "ANTES (como veio)", tb, VERDE),
                  par(f"{orig}-detalhe.jpg", f"{res}-detalhe.jpg", "ANTES - DETALHE", tb+" - DETALHE", VERDE)])
for nome, n in {"horas47":"08-horas_p047", "escola7":"05-escola_p007", "opus165":"12-opusmajus_p165",
                "rhetorica18":"18-rhetorica_p018", "palatino67":"17-palatino_p067", "marial153":"21-marial_p153"}.items():
    com_detalhe(nome, L/f"{n}-1-original", L/f"{n}-3-resultado")
# so pagina inteira (resultados mais novos, com o detector consertado)
for nome, orig, res, tb in [
  ("horas13", L/"07-horas_p013-1-original.jpg", OP/"horas_p013-magico_pro-A.png", "DEPOIS (programa)"),
  ("horas26", L/"14-horas_p026-1-original.jpg", OP/"horas_p026-magico_pro-A.png", "DEPOIS (programa)"),
  ("horas27", L/"15-horas_p027-1-original.jpg", OP/"horas_p027-magico_pro-A.png", "DEPOIS (programa)"),
  ("graduale222", L/"19-graduale_p222-1-original.jpg", OP/"graduale_p222-magico_pro-A.png", "DEPOIS (programa)"),
  ("opus20-fotos", L/"11-opusmajus_p020-1-original.jpg", OP/"opusmajus_p020-magico_pro-E.png", "DEPOIS: \"Este livro tem fotos\""),
  ("opus256", L/"13-opusmajus_p256-1-original.jpg", TF/"opusmajus_p256.png", "DEPOIS: \"Tirar o fundo\""),
]:
    salvar(nome, [par(orig, res, "ANTES (como veio)", tb, VERDE)])
shutil.copy("conferencia-3-2026-09-30/d1-palatino57-resultado.jpg", "resultados-2026-09-30/img2/palatino57.jpg")
for n in ["1-papel-branco","2-pintura-cor","3-corte","4-tirar-fundo","7-partitura","8-pergunta","n1-iluminura","n2-foto-pb","n3-titulo-vermelho-pb","n4-papel-atras-titulo"]:
    shutil.copy(f"resultados-2026-09-30/img/{n}.jpg", f"resultados-2026-09-30/img2/{n}.jpg")
shutil.copy("conferencia-2-2026-09-30/pb-novo/pb-horas026.jpg", "resultados-2026-09-30/img2/pb-moldura.jpg")
shutil.copy("conferencia-2-2026-09-30/refazer/b6-previa-igual-pdf.jpg", "resultados-2026-09-30/img2/corte-crista.jpg")
shutil.copy("conferencia-2-2026-09-30/refazer/b4-marial7-borda-direita.jpg", "resultados-2026-09-30/img2/marial7.jpg")
print("ok copias")
