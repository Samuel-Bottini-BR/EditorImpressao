"""Desenhos da página de escolhas (07/10/2026), refeitos depois das respostas do Samuel:

- tempo-preto-e-branco.svg: quanto tempo a mais o Preto e branco leva com o limpar pontinhos
  do ScanTailor (números do parecer do verificador, commit a755087, PC parado).
- metade-antes-do-conserto.svg, metade-inteira.svg, metade-so-metade.svg: a história da folha
  que deixou de ser dividida com uma metade apagada (o que acontecia antes e as duas opções).

Rodar: python desenhos_dividir_e_tempo.py <pasta de saída>. Só gera imagens; não mexe no programa.
"""
import pathlib
import sys

SAIDA = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SAIDA.mkdir(parents=True, exist_ok=True)

FONTE = 'font-family="Segoe UI,Arial"'
VERDE, VERMELHO, AZUL, CINZA = "#1e7d3a", "#c0392b", "#2f6fe0", "#555"


def texto(x, y, t, tam=18, cor="#1f1f1f", peso=400, ancora="start"):
    return (f'<text x="{x}" y="{y}" {FONTE} font-size="{tam}" font-weight="{peso}" '
            f'fill="{cor}" text-anchor="{ancora}">{t}</text>')


# ---------------------------------------------------------------- tempo
def mmss(seg):
    seg = round(seg)
    return f"{seg} s" if seg < 60 else f"{seg // 60} min {seg % 60:02d} s"


def tempo():
    # Segundos por página do Preto e branco (parecer do verificador, 06/10/2026).
    comuns_hoje = [0.76, 0.44, 0.48, 0.74, 0.11, 0.81]
    comuns_com = [0.84, 0.51, 0.55, 0.88, 0.15, 0.90]
    grandes_hoje = [4.56, 3.02, 1.71, 1.46, 1.06]
    grandes_com = [5.29, 3.52, 2.61, 2.13, 1.60]
    media = lambda v: sum(v) / len(v)
    grupos = [
        ("Livro comum de 300 páginas (como o Palatino, a Escola, o Opus Majus)",
         300 * media(comuns_hoje), 300 * media(comuns_com)),
        ("Livro de 300 páginas grandes (como o Livro de Horas, o Graduale, o Marial)",
         300 * media(grandes_hoje), 300 * media(grandes_com)),
    ]
    W, H = 1100, 520
    maximo = max(g[2] for g in grupos)
    larg = 640
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         texto(24, 40, "Quanto tempo o Preto e branco leva (só esta parte do processamento)", 24, peso=700)]
    y = 90
    for titulo, hoje, com in grupos:
        p.append(texto(24, y, titulo, 19, peso=600))
        for rot, val, cor in (("Hoje", hoje, "#8a8f98"), ("Com o limpar pontinhos", com, AZUL)):
            y += 22
            w = larg * val / maximo
            p.append(texto(24, y + 24, rot, 17, CINZA))
            p.append(f'<rect x="230" y="{y + 6}" width="{w:.0f}" height="28" rx="4" fill="{cor}"/>')
            p.append(texto(240 + w, y + 27, mmss(val), 17, peso=600))
            y += 30
        p.append(texto(230, y + 34, f"Diferença: {mmss(com - hoje)} a mais no livro inteiro", 19, VERMELHO, 700))
        y += 110
    p.append(texto(24, H - 20, "Medido com o PC parado, página por página, em 11 páginas de 7 livros.", 15, CINZA))
    p.append("</svg>")
    (SAIDA / "tempo-preto-e-branco.svg").write_text("".join(p), encoding="utf-8")


# ---------------------------------------------------------------- metade apagada
PW, PH = 200, 260  # tamanho da folha desenhada


def folha(x, y, dividida=False, esquerda_apagada=False, so_direita=False, vazia=False):
    """Uma folha escaneada que é UMA página só (título no meio, atravessando a dobra)."""
    g = [f'<g transform="translate({x},{y})">']
    if vazia:
        g.append(f'<rect width="{PW}" height="{PH}" rx="4" fill="none" stroke="{VERMELHO}" '
                 f'stroke-width="3" stroke-dasharray="10 8"/>')
        g.append(texto(PW / 2, PH / 2 - 6, "nada:", 22, VERMELHO, 700, "middle"))
        g.append(texto(PW / 2, PH / 2 + 22, "a folha sumia", 20, VERMELHO, 700, "middle"))
        g.append("</g>")
        return "".join(g)
    x0 = PW / 2 if so_direita else 0
    g.append(f'<clipPath id="c{x}{y}{int(so_direita)}"><rect x="{x0}" y="0" width="{PW - x0}" height="{PH}"/></clipPath>')
    g.append(f'<g clip-path="url(#c{x}{y}{int(so_direita)})">')
    g.append(f'<rect width="{PW}" height="{PH}" rx="4" fill="#fbf8f1" stroke="{CINZA}" stroke-width="2"/>')
    g.append(f'<text x="{PW / 2}" y="78" text-anchor="middle" font-family="Georgia,serif" font-size="25" '
             f'font-weight="700" fill="#7a1f1f">CURSO DE</text>')
    g.append(f'<text x="{PW / 2}" y="110" text-anchor="middle" font-family="Georgia,serif" font-size="25" '
             f'font-weight="700" fill="#7a1f1f">LATIM</text>')
    for i in range(4):
        g.append(f'<rect x="{40 + (i % 2) * 10}" y="{150 + i * 18}" width="{120 - (i % 2) * 20}" height="6" rx="3" fill="#9a958c"/>')
    g.append("</g>")
    if so_direita:
        g.append(f'<rect x="{PW / 2}" width="{PW / 2}" height="{PH}" rx="4" fill="none" stroke="{CINZA}" stroke-width="2"/>')
    if esquerda_apagada:
        g.append(f'<rect x="0" y="0" width="{PW / 2}" height="{PH}" fill="#c0392b" fill-opacity="0.18"/>')
        g.append(f'<path d="M10 10 L{PW / 2 - 10} {PH - 10} M{PW / 2 - 10} 10 L10 {PH - 10}" stroke="{VERMELHO}" stroke-width="4"/>')
        g.append(texto(PW / 4, PH + 22, "apagada", 16, VERMELHO, 700, "middle"))
    if dividida:
        g.append(f'<path d="M{PW / 2} -8 L{PW / 2} {PH + 8}" stroke="{AZUL}" stroke-width="3" stroke-dasharray="9 6"/>')
    g.append("</g>")
    return "".join(g)


def historia(nome, titulo, final, legenda_final, cor_final):
    W, H = 1200, 470
    xs = [40, 330, 620, 930]
    y = 120
    passos = [
        ("1. O programa dividiu a folha", "ao meio (linha azul)"),
        ("2. O Kaique apaga a", "página da esquerda"),
        ("3. Depois aperta", "“não dividir esta”"),
        ("4. O que vai para o PDF", ""),
    ]
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         texto(24, 40, titulo, 24, peso=700)]
    for i, (l1, l2) in enumerate(passos):
        p.append(texto(xs[i] + PW / 2, 78, l1, 17, peso=600, ancora="middle"))
        p.append(texto(xs[i] + PW / 2, 100, l2, 17, peso=600, ancora="middle"))
        if i < 3:
            ax = xs[i] + PW + 18
            p.append(f'<path d="M{ax} {y + PH / 2} L{xs[i + 1] - 22} {y + PH / 2}" stroke="#999" stroke-width="3"/>')
            p.append(f'<polygon points="{xs[i + 1] - 26},{y + PH / 2 - 9} {xs[i + 1] - 26},{y + PH / 2 + 9} '
                     f'{xs[i + 1] - 12},{y + PH / 2}" fill="#999"/>')
    p.append(folha(xs[0], y, dividida=True))
    p.append(folha(xs[1], y, dividida=True, esquerda_apagada=True))
    p.append(folha(xs[2], y, esquerda_apagada=True))
    p.append(final(xs[3], y))
    p.append(f'<rect x="{xs[3] - 14}" y="{y - 14}" width="{PW + 28}" height="{PH + 28}" rx="8" fill="none" '
             f'stroke="{cor_final}" stroke-width="3"/>')
    p.append(texto(xs[3] + PW / 2, y + PH + 50, legenda_final, 18, cor_final, 700, "middle"))
    p.append("</svg>")
    (SAIDA / nome).write_text("".join(p), encoding="utf-8")


# ---------------------------------------------------------------- encadernação
def encadernacao():
    """Por que apagar uma página do livro estraga a encadernação (pedido do Samuel, 07/10).

    Cada folha impressa tem frente e verso; os cadernos são montados com as páginas
    que sobram, na ordem. Tirar uma página empurra todas as seguintes um lado.
    """
    W, H = 1200, 520
    LW, LH = 92, 120  # tamanho de cada lado da folha

    def lado(x, y, rot, cor="#fbf8f1", borda=CINZA, texto_cor="#1f1f1f"):
        g = [f'<rect x="{x}" y="{y}" width="{LW}" height="{LH}" rx="3" fill="{cor}" stroke="{borda}" stroke-width="2"/>']
        for i, linha in enumerate(rot.split("|")):
            g.append(texto(x + LW / 2, y + LH / 2 - 6 + i * 20, linha, 16, texto_cor, 700, "middle"))
        return "".join(g)

    def fileira(y, titulo, cor_titulo, folhas, nota, cor_nota):
        p = [texto(24, y, titulo, 20, cor_titulo, 700)]
        x = 24
        for n, (frente, verso, destaque) in enumerate(folhas):
            p.append(texto(x + LW, y + 30, f"folha {n + 1}", 15, CINZA, 600, "middle"))
            for k, (rot, nome) in enumerate(((frente, "frente"), (verso, "verso"))):
                cor, borda = "#fbf8f1", CINZA
                if rot == "branca":
                    cor, rot = "#ffffff", "página|branca"
                if destaque == k:
                    borda = cor_nota
                p.append(lado(x + k * LW, y + 40, rot, cor, borda))
                p.append(texto(x + k * LW + LW / 2, y + 40 + LH + 20, nome, 14, CINZA, 400, "middle"))
            x += 2 * LW + 40
        p.append(texto(x + 10, y + 40 + LH / 2, nota[0], 18, cor_nota, 700))
        p.append(texto(x + 10, y + 40 + LH / 2 + 24, nota[1], 18, cor_nota, 700))
        return "".join(p)

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         texto(24, 36, "Exemplo: o Kaique apaga o verso em branco da capa (a página 2)", 22, peso=700)]
    p.append(fileira(84, "Como está hoje: a página apagada sai da fila", VERMELHO,
                     [("1|capa", "3|rosto", 1), ("4", "5", None), ("6", "7", None)],
                     ("o rosto foi parar no verso,", "e todas as seguintes trocam de lado"), VERMELHO))
    p.append(fileira(314, "Com página branca no lugar da apagada", VERDE,
                     [("1|capa", "branca", 1), ("3|rosto", "4", None), ("5", "6", None)],
                     ("cada página continua", "no seu lado, como no livro"), VERDE))
    p.append("</svg>")
    (SAIDA / "encadernacao-pagina-apagada.svg").write_text("".join(p), encoding="utf-8")


if __name__ == "__main__":
    encadernacao()
    tempo()
    historia("metade-antes-do-conserto.svg", "Antes do conserto (o defeito que o verificador achou)",
             lambda x, y: folha(x, y, vazia=True), "a folha inteira sumia do PDF", VERMELHO)
    historia("metade-inteira.svg", "Opção “Sai a folha inteira”",
             lambda x, y: folha(x, y), "a folha inteira, uma vez", VERDE)
    historia("metade-so-metade.svg", "Opção “Sai só a metade que não foi apagada”",
             lambda x, y: folha(x, y, so_direita=True), "só a metade da direita", AZUL)
    print("ok:", SAIDA)
