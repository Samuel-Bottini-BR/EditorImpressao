# Monta as comparacoes da pagina de resultados de 30/09/2026 (para mostrar ao Kaique).
# Cada imagem: pagina inteira lado a lado em cima, detalhe ampliado lado a lado embaixo,
# com rotulos grandes. Rodar de dentro de relatorios/.
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import shutil
C = Path("conferir")
L2 = C/"fase1-1.2-ligacao-2026-09-30/2-depois-magico-pro/1.2-2026-09-30-0023/paineis"
L4 = next((C/"fase1-1.2-ligacao-2026-09-30/4-depois-preto-e-branco").glob("*/paineis"))
PB = C/"pb-regra-30-09/depois/1.2-2026-09-30-1031/paineis"
BONS = {
 "1-papel-branco": (C/"fase1-2026-09-28-1927-2/paineis/01-palatino_p005-1-original", C/"fase1-2026-09-28-1927-2/paineis/01-palatino_p005-3-resultado"),
 "2-pintura-cor": (C/"fase1-2026-09-28-1927-2/paineis/19-escola_p035-1-original", C/"fase1-2026-09-28-1927-2/paineis/19-escola_p035-3-resultado"),
 "4-tirar-fundo": (C/"fase1-2026-09-29-0956/paineis/10-opusmajus_p020-1-original", C/"fase1-2026-09-29-0956/paineis/10-opusmajus_p020-3-resultado"),
 "5-moldura": (L2/"14-horas_p026-1-original", L2/"14-horas_p026-3-resultado"),
 "7-partitura": (C/"fase1-2026-09-28-2058-2/paineis/01-graduale_p222-1-original", C/"fase1-2026-09-28-2058-2/paineis/01-graduale_p222-3-resultado"),
}
ANDAMENTO = {"6-preto-e-branco": (PB/"03-horas_p026-1-original", PB/"03-horas_p026-3-resultado")}
RUINS = {
 "n1-iluminura": (L2/"06-horas_p011-1-original", L2/"06-horas_p011-3-resultado"),
 "n2-foto-pb": (L4/"11-opusmajus_p020-1-original", L4/"11-opusmajus_p020-3-resultado"),
 "n3-titulo-vermelho-pb": (PB/"02-horas_p013-1-original", PB/"02-horas_p013-3-resultado"),
 "n4-papel-atras-titulo": (L2/"21-marial_p153-1-original", L2/"21-marial_p153-3-resultado"),
}
FONTE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 44)
LARG = 1100

def ajusta(img):
    return img.resize((LARG, int(img.height * LARG / img.width)), Image.LANCZOS)

def rotulo(img, texto, cor):
    novo = Image.new("RGB", (img.width, img.height + 70), "white")
    novo.paste(img, (0, 70))
    d = ImageDraw.Draw(novo); d.rectangle([0, 0, img.width, 70], fill=cor)
    d.text((18, 10), texto, fill="white", font=FONTE)
    return novo

def montar(pares, texto_depois, cor_depois):
    for nome, (antes, depois) in pares.items():
        partes = []
        for suf, tit in (("", "PÁGINA INTEIRA"), ("-detalhe", "DETALHE AMPLIADO")):
            a = rotulo(ajusta(Image.open(f"{antes}{suf}.jpg").convert("RGB")), f"ANTES (como veio) - {tit}", (120, 120, 120))
            b = rotulo(ajusta(Image.open(f"{depois}{suf}.jpg").convert("RGB")), f"{texto_depois} - {tit}", cor_depois)
            linha = Image.new("RGB", (a.width + b.width + 20, max(a.height, b.height)), "white")
            linha.paste(a, (0, 0)); linha.paste(b, (a.width + 20, 0)); partes.append(linha)
        tela = Image.new("RGB", (partes[0].width, sum(p.height for p in partes) + 30), "white")
        y = 0
        for p in partes:
            tela.paste(p, (0, y)); y += p.height + 30
        tela.save(f"resultados-2026-09-30/img/{nome}.jpg", quality=88); print("ok", nome)

montar(BONS, "DEPOIS (programa)", (46, 125, 50))
montar(ANDAMENTO, "PROGRAMA HOJE", (21, 101, 192))
montar(RUINS, "PROGRAMA HOJE", (198, 40, 40))
shutil.copy(C/"fase1-2026-09-28-1745/verificador/01-escola35.jpg", "resultados-2026-09-30/img/3-corte.jpg")
shutil.copy(C/"fase1-2026-09-29-1826/verificador/t01-aviso-primeira-abertura.jpg", "resultados-2026-09-30/img/8-pergunta.jpg")
print("ok copias")
