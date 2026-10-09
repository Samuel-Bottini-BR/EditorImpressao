"""Gera os desenhos da pergunta g6-retangulo da página de escolhas (refeita em 09/10/2026).

O Samuel respondeu "Ainda não entendi" ("eu não entendi, me de mais exemplos e
explique melhor."). Estes desenhos respondem a isso: um passo a passo e três
exemplos (0,3°; 2° com corte justo; 2° com o texto encostado na faixa escura da
lombada), cada um com "o corte que você fez", "Fica no mesmo lugar" e
"Acompanha o texto" lado a lado e uma lupa no canto que importa.

Uso:  python desenhos_g6_retangulo.py <pasta de saída>
Grava retangulo-passo-a-passo.svg e retangulo-ex1/ex2/ex3-*.svg; a gerente
publica na página como img/g6/<nome>.svg.

Seguro mudar: textos, cores, tamanhos dos painéis. Arriscado: as legendas
usam os números calculados (quanto o canto anda, quanto o retângulo cresce);
se mudar os casos, conferir que a frase ainda bate com o desenho.

Esquemas em milímetros: uma página de 150 x 210 mm, um bloco de texto, o
retângulo verde do corte feito à mão. Mudar o ângulo gira a página inteira
(papel e texto) em volta do centro; o retângulo:
  - "fica": não se mexe;
  - "acompanha": vira a caixa que contém o retângulo antigo girado junto
    (o mesmo jeito do desenho de 08/10).
As contas (quanto o canto anda, se a letra sai) são feitas aqui, não
inventadas à mão.
"""
import math, os, sys

SAIDA = sys.argv[1]
os.makedirs(SAIDA, exist_ok=True)

FUNDO = "#1E1F22"; TITULO = "#E6E6E6"; LEG = "#AEB4BD"; PAPEL = "#EFE6D2"
BORDA = "#8a7a5a"; TINTA = "#5a4a32"; VERDE = "#3FBF6F"; AZUL = "#2F6FE0"
VERMELHO = "#FF5A5A"; LARANJA = "#F0A55C"; SOMBRA = "#6b6152"
FONTE = 'font-family="Segoe UI, Arial"'
PW, PH = 150.0, 210.0
CX, CY = PW / 2, PH / 2
S = 1.2           # px por mm na vista da página
ZOOM = 4.0        # aumento da lupa

def rot(x, y, graus):
    a = math.radians(graus)
    dx, dy = x - CX, y - CY
    return (CX + dx * math.cos(a) - dy * math.sin(a), CY + dx * math.sin(a) + dy * math.cos(a))

def txt(x, y, s, cor=LEG, tam=13, peso=None, meio=False):
    p = f' font-weight="{peso}"' if peso else ""
    a = ' text-anchor="middle"' if meio else ""
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x:.1f}" y="{y:.1f}" fill="{cor}" font-size="{tam}" {FONTE}{p}{a}>{s}</text>'

def conteudo(caso):
    """Papel + sombra (se houver) + linhas de texto, em mm, sem giro."""
    t = caso["texto"]
    partes = [f'<rect x="0" y="0" width="{PW}" height="{PH}" fill="{PAPEL}" stroke="{BORDA}" stroke-width="0.6"/>']
    if caso.get("sombra"):
        x0 = caso["sombra"]
        partes.append(f'<rect x="{x0}" y="0" width="{PW-x0}" height="{PH}" fill="{SOMBRA}"/>')
    x0, y0, x1, y1 = t
    largura = x1 - x0
    # título curto e linhas cheias; a primeira e a última linha vão até o canto
    partes.append(f'<rect x="{x0 + largura*0.3:.1f}" y="{y0}" width="{largura*0.4:.1f}" height="6" fill="{TINTA}"/>')
    y = y0 + 14
    n = 0
    while y + 5 <= y1 - 5:
        w = largura if n % 3 != 2 else largura * 0.8
        partes.append(f'<rect x="{x0}" y="{y:.1f}" width="{w:.1f}" height="5" fill="{TINTA}"/>')
        y += 10; n += 1
    partes.append(f'<rect x="{x0}" y="{y1-5:.1f}" width="{largura:.1f}" height="5" fill="{TINTA}"/>')
    # o bloco de texto, para as contas: cantos da primeira linha cheia e da última
    return "".join(partes), [(x0, y0 + 14), (x1, y0 + 14), (x0, y1), (x1, y1)]

def caixa_girada(r, graus):
    x0, y0, x1, y1 = r
    pts = [rot(x, y, graus) for x, y in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))

def cena(caso, modo):
    """Devolve (svg da cena em mm, retângulo, cantos fora, sombra dentro?)."""
    corpo, cantos = conteudo(caso)
    g = 0.0 if modo == "antes" else caso["graus"]
    r = caso["corte"] if modo in ("antes", "fica") else caixa_girada(caso["corte"], g)
    x0, y0, x1, y1 = r
    partes = [f'<g transform="rotate({g} {CX} {CY})">{corpo}</g>']
    partes.append(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1-x0:.2f}" height="{y1-y0:.2f}" fill="none" '
                  f'stroke="{VERDE}" stroke-width="3" stroke-dasharray="7 4" vector-effect="non-scaling-stroke"/>')
    fora = []
    if modo != "antes":
        for (x, y) in cantos:
            px, py = rot(x, y, g)
            if px < x0 or px > x1 or py < y0 or py > y1:
                fora.append((px, py))
                partes.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3" fill="none" stroke="{VERMELHO}" '
                              f'stroke-width="2.5" vector-effect="non-scaling-stroke"/>')
    sombra_dentro = 0.0
    if caso.get("sombra") is not None and modo != "antes":
        # quanto da sombra (a linha x = sombra, girada) entra no retângulo, no pior ponto
        sx = caso["sombra"]
        for yy in (y0, y1):
            # ponto da beirada da sombra na altura yy: resolver aproximando
            melhor = None
            for i in range(0, 2101):
                py = i * PH / 2100
                qx, qy = rot(sx, py, g)
                if abs(qy - yy) < 0.2:
                    melhor = qx; break
            if melhor is not None:
                sombra_dentro = max(sombra_dentro, x1 - melhor)
    return "".join(partes), r, fora, sombra_dentro

def deslocamento(caso):
    _, cantos = conteudo(caso)
    return max(math.hypot(*(a - b for a, b in zip(rot(x, y, caso["graus"]), (x, y)))) for x, y in cantos)

def num(v):
    return f"{v:.1f}".replace(".", ",")

def desenho(caso, nome):
    largura_painel = 240
    gap = 34
    W = 16 * 2 + 3 * largura_painel + 2 * gap
    topo = 70
    pag_h = PH * S
    lupa_r = 62
    lupa_cy = topo + 30 + pag_h + 14 + lupa_r
    leg_y = lupa_cy + lupa_r + 26
    H = leg_y + 18 * 4 + 10
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" width="{W}" role="img">',
           f'<rect width="{W}" height="{H:.0f}" rx="8" fill="{FUNDO}"/>',
           txt(16, 28, caso["titulo"], TITULO, 17, 600), txt(16, 50, caso["subtitulo"], LEG, 14)]
    defs = []
    titulos = {"antes": "1. o corte que você fez", "fica": "2a. Fica no mesmo lugar", "acompanha": "2b. Acompanha o texto"}
    cores = {"antes": TITULO, "fica": TITULO, "acompanha": TITULO}
    info = {}
    for i, modo in enumerate(("antes", "fica", "acompanha")):
        cid = f"{nome}-{modo}"
        svg_cena, r, fora, sombra = cena(caso, modo)
        info[modo] = (r, fora, sombra)
        defs.append(f'<g id="{cid}">{svg_cena}</g>')
        px = 16 + i * (largura_painel + gap)
        out.append(txt(px + largura_painel / 2, topo + 14, titulos[modo], cores[modo], 15, 600, True))
        ox = px + (largura_painel - PW * S) / 2
        oy = topo + 30
        out.append(f'<use href="#{cid}" transform="translate({ox:.1f},{oy:.1f}) scale({S})"/>')
        lupas = caso["lupa"] if isinstance(caso["lupa"], list) else [caso["lupa"]]
        rl = lupa_r if len(lupas) == 1 else 54
        for j, (zx, zy) in enumerate(lupas):
            if len(lupas) == 1:
                lx = px + largura_painel / 2
            else:
                lx = px + largura_painel / 2 + (j - 0.5) * (2 * rl + 10)
            ly = lupa_cy
            mx, my = ox + zx * S, oy + zy * S
            rr = rl / ZOOM
            out.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{rr:.1f}" fill="none" stroke="{AZUL}" stroke-width="1.5"/>')
            out.append(f'<line x1="{mx:.1f}" y1="{my + rr:.1f}" x2="{lx:.1f}" y2="{ly - rl:.1f}" stroke="{AZUL}" stroke-width="1.2" opacity="0.8"/>')
            clip = f"clip-{cid}-{j}"
            defs.append(f'<clipPath id="{clip}"><circle cx="{lx:.1f}" cy="{ly:.1f}" r="{rl}"/></clipPath>')
            out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{rl}" fill="#2a2c30"/>')
            out.append(f'<g clip-path="url(#{clip})"><use href="#{cid}" transform="translate({lx:.1f},{ly:.1f}) '
                       f'scale({S*ZOOM}) translate({-zx},{-zy})"/></g>')
            out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{rl}" fill="none" stroke="{AZUL}" stroke-width="2"/>')
        for k, linha in enumerate(caso["legendas"][modo]):
            cor = LEG
            if linha.startswith("!"):
                cor = VERMELHO; linha = linha[1:]
            elif linha.startswith("+"):
                cor = VERDE; linha = linha[1:]
            elif linha.startswith("~"):
                cor = LARANJA; linha = linha[1:]
            out.append(txt(px, leg_y + k * 18, linha, cor, 13))
        if i < 2:
            ax = px + largura_painel + 4
            ay = topo + 30 + pag_h / 2
            if i == 0:
                out.append(f'<path d="M{ax} {ay} h{gap-8} m-8 -7 l8 7 l-8 7" fill="none" stroke="{AZUL}" stroke-width="3" stroke-linecap="round"/>')
                out.append(txt(ax + (gap - 8) / 2, ay - 14, "gira", LEG, 12, None, True))
                out.append(txt(ax + (gap - 8) / 2, ay + 26, num(caso["graus"]) + "°", LEG, 12, None, True))
    out.insert(2, "<defs>" + "".join(defs) + "</defs>")
    out.append("</svg>")
    with open(os.path.join(SAIDA, f"{nome}.svg"), "w", encoding="utf-8") as f:
        f.write("".join(out))
    return info

# ---------- os três casos ----------
casos = {}

# Caso 1: ângulo muda pouco (0,3°), corte com 5 mm de folga.
c1 = dict(graus=0.3, texto=(20, 22, 130, 188), corte=(15, 17, 135, 193), lupa=(133, 33))
c1["titulo"] = "Exemplo 1: o ângulo muda pouco (0,3°)"
c1["subtitulo"] = "Corte com folga de 5 mm em volta do texto. É o caso mais comum: um ajuste fino nas setas de 0,1°."
casos["retangulo-ex1-pouco"] = c1

# Caso 2: ângulo muda muito (2°), corte justo (2 mm do texto).
c2 = dict(graus=2.0, texto=(20, 22, 130, 188), corte=(18, 20, 132, 190), lupa=(130, 36))
c2["titulo"] = "Exemplo 2: o ângulo muda muito (2°)"
c2["subtitulo"] = "Corte justo, a 2 mm do texto. Acontece quando o programa errou o ângulo e o Kaique corrige bastante."
casos["retangulo-ex2-muito"] = c2

# Caso 3: texto encostado na beirada (sombra da lombada à direita), 2°.
c3 = dict(graus=2.0, texto=(14, 22, 133, 188), corte=(11, 19, 135, 191), lupa=[(134, 36), (134, 184)], sombra=137)
c3["titulo"] = "Exemplo 3: texto encostado na beirada (2°)"
c3["subtitulo"] = "À direita do texto há a faixa escura da lombada. O corte passa espremido entre o texto e a faixa."
casos["retangulo-ex3-beirada"] = c3

relatorio = []
for nome, c in casos.items():
    d = deslocamento(c)
    # primeiro, as contas (sem legendas), para escrever legendas que batem com elas
    c["legendas"] = {"antes": [], "fica": [], "acompanha": []}
    info = desenho(c, nome)
    rf, fora_f, sombra_f = info["fica"]
    ra, fora_a, sombra_a = info["acompanha"]
    cresce = max(rf[0] - ra[0], ra[2] - rf[2], rf[1] - ra[1], ra[3] - rf[3])
    relatorio.append((nome, d, len(fora_f), sombra_f, len(fora_a), sombra_a, cresce))
    c["_contas"] = (d, len(fora_f), sombra_f, len(fora_a), sombra_a, cresce)

# legendas escritas a partir das contas
d, ff, sf, fa, sa, cr = casos["retangulo-ex1-pouco"]["_contas"]
casos["retangulo-ex1-pouco"]["legendas"] = {
    "antes": ["Retângulo verde com folga", "de 5 mm em volta do texto."],
    "fica": ["O retângulo não se mexe.", f"O canto do texto anda {num(d)} mm:", "nem dá para ver.", "+Nada a fazer."],
    "acompanha": ["O retângulo cresce", f"{num(cr)} mm de cada lado:", "nem dá para ver.", "+Nada a fazer."],
}
d, ff, sf, fa, sa, cr = casos["retangulo-ex2-muito"]["_contas"]
casos["retangulo-ex2-muito"]["legendas"] = {
    "antes": ["Retângulo justo, a 2 mm", "do texto."],
    "fica": ["O retângulo não se mexe.", f"Os cantos do texto andam {num(d)} mm", f"!e {ff} cantos saem (em vermelho):", "!letras cortadas. Ajustar de novo."],
    "acompanha": [f"O retângulo cresce {num(cr)} mm", "e o texto todo continua dentro.", "+Nada cortado.", "A margem sai um pouco maior."],
}
d, ff, sf, fa, sa, cr = casos["retangulo-ex3-beirada"]["_contas"]
casos["retangulo-ex3-beirada"]["legendas"] = {
    "antes": ["Retângulo espremido entre", "o texto e a faixa escura."],
    "fica": ["O retângulo não se mexe.", ("!Um canto do texto sai dele," if ff == 1 else f"!{ff} cantos do texto saem dele,"), "~e a faixa escura entra num canto.", "!Ajustar de novo."],
    "acompanha": [f"O retângulo cresce {num(cr)} mm:", "+o texto continua dentro,", "~mas a faixa escura entra mais.", "!Ajustar de novo."],
}
for nome, c in casos.items():
    desenho(c, nome)

# ---------- passo a passo ----------
def passo_a_passo():
    W, H = 16 * 2 + 4 * 170 + 3 * 24, 330
    s = 0.7
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" role="img">',
           f'<rect width="{W}" height="{H}" rx="8" fill="{FUNDO}"/>',
           txt(16, 28, "Quando a pergunta acontece: passo a passo", TITULO, 17, 600)]
    base = dict(graus=0.0, texto=(20, 22, 130, 188), corte=(15, 17, 135, 193))
    corpo, _ = conteudo(base)
    textos = [
        ("1. O programa", "endireita a página", "sozinho.", None),
        ("2. O Kaique ajusta", "o corte à mão", "(retângulo verde).", "corte"),
        ("3. Depois, ele muda", "o ângulo (setas de", "0,1°, bolinha, linha).", "gira"),
        ("4. E o retângulo?", "Fica parado ou", "se mexe junto?", "duvida"),
    ]
    for i, (a, b, c, tipo) in enumerate(textos):
        px = 16 + i * (170 + 24)
        ox = px + (170 - PW * s) / 2
        oy = 50
        g = 0.0
        if i == 0:
            out.append(f'<g transform="translate({ox:.1f},{oy}) scale({s})"><g transform="rotate(-4 {CX} {CY})" opacity="0.35">{corpo}</g>{corpo}</g>')
        else:
            g = 2.0 if i >= 2 else 0.0
            ret = ""
            if tipo in ("corte", "gira", "duvida"):
                x0, y0, x1, y1 = base["corte"]
                ret = (f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" stroke="{VERDE}" '
                       f'stroke-width="3" stroke-dasharray="7 4" vector-effect="non-scaling-stroke"/>')
            if tipo == "duvida":
                ret += f'<text x="{CX}" y="{CY+18}" fill="{AZUL}" font-size="64" font-weight="700" text-anchor="middle" {FONTE}>?</text>'
            out.append(f'<g transform="translate({ox:.1f},{oy}) scale({s})"><g transform="rotate({g} {CX} {CY})">{corpo}</g>{ret}</g>')
        if tipo == "gira":
            cx, cy = px + 170 / 2, oy + PH * s + 22
            out.append(f'<path d="M{cx-26} {cy} a 30 14 0 0 0 52 0" fill="none" stroke="{AZUL}" stroke-width="3"/>'
                       f'<path d="M{cx+26} {cy} l-2 -9 m2 9 l-9 -2" stroke="{AZUL}" stroke-width="3" fill="none" stroke-linecap="round"/>')
        ty = oy + PH * s + 54
        for k, linha in enumerate((a, b, c)):
            out.append(txt(px + 85, ty + k * 18, linha, TITULO if k == 0 else LEG, 14 if k == 0 else 13, 600 if k == 0 else None, True))
        if i < 3:
            ax = px + 170 + 2
            ay = oy + PH * s / 2
            out.append(f'<path d="M{ax} {ay} h20 m-7 -6 l7 6 l-7 6" fill="none" stroke="{AZUL}" stroke-width="3" stroke-linecap="round"/>')
    out.append("</svg>")
    with open(os.path.join(SAIDA, "retangulo-passo-a-passo.svg"), "w", encoding="utf-8") as f:
        f.write("".join(out))

passo_a_passo()
for linha in relatorio:
    print(linha)
