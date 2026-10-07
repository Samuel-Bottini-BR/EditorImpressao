"""Desenha as duas opções do "Aplicar em" do girar, para a página de escolhas."""
import pathlib

SAIDA = pathlib.Path(r"C:\Users\fotog\AppData\Local\Temp\claude\d--programas\35d489db-9216-4d07-a049-6468d4552ad0\scratchpad\escolhas\img")

W, H = 960, 560
COLS = [200, 480, 760]
Y_ANTES, Y_DEPOIS = 150, 420


def folha(cx, cy, ang, borda="#555", destaque=None):
    linhas = "".join(
        f'<rect x="-32" y="{-22 + i * 12}" width="{64 if i % 3 else 52}" height="4" rx="2" fill="#9a958c"/>'
        for i in range(6)
    )
    g = (
        f'<g transform="translate({cx},{cy}) rotate({ang})">'
        f'<rect x="-44" y="-60" width="88" height="120" rx="3" fill="#fbf8f1" stroke="{borda}" stroke-width="{4 if destaque else 2}"/>'
        f'<text x="0" y="-36" text-anchor="middle" font-family="Georgia,serif" font-size="17" font-weight="700" fill="#7a1f1f">TÍTULO</text>'
        f'{linhas}'
        f'<polygon points="0,-76 -9,-64 9,-64" fill="{borda}"/>'
        f'</g>'
    )
    return g


def imagem(nome, titulo, depois, notas):
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        f'<text x="24" y="40" font-family="Segoe UI,Arial" font-size="24" font-weight="700" fill="#1f1f1f">{titulo}</text>',
        f'<text x="24" y="{Y_ANTES + 6}" font-family="Segoe UI,Arial" font-size="18" fill="#666">Antes</text>',
        f'<text x="24" y="{Y_DEPOIS + 6}" font-family="Segoe UI,Arial" font-size="18" fill="#666">Depois</text>',
    ]
    antes = [-90, 0, -90]
    for i, cx in enumerate(COLS):
        partes.append(f'<text x="{cx}" y="72" text-anchor="middle" font-family="Segoe UI,Arial" font-size="18" font-weight="600" fill="#1f1f1f">Folha {i + 1}</text>')
        partes.append(folha(cx, Y_ANTES, antes[i], borda="#2f6fe0" if i == 0 else "#555", destaque=(i == 0)))
        partes.append(f'<path d="M{cx} {Y_ANTES + 78} L{cx} {Y_DEPOIS - 92}" stroke="#999" stroke-width="3"/>')
        partes.append(f'<polygon points="{cx - 9},{Y_DEPOIS - 96} {cx + 9},{Y_DEPOIS - 96} {cx},{Y_DEPOIS - 82}" fill="#999"/>')
        cor, texto = notas[i]
        partes.append(folha(cx, Y_DEPOIS, depois[i], borda=cor, destaque=(cor != "#555")))
        partes.append(f'<text x="{cx}" y="{Y_DEPOIS + 104}" text-anchor="middle" font-family="Segoe UI,Arial" font-size="17" font-weight="600" fill="{cor}">{texto}</text>')
    partes.append(f'<text x="{COLS[0]}" y="{Y_ANTES + 92}" text-anchor="middle" font-family="Segoe UI,Arial" font-size="14" fill="#2f6fe0">a folha da vez</text>')
    partes.append("</svg>")
    (SAIDA / nome).write_text("".join(partes), encoding="utf-8")


VERDE, VERMELHO, CINZA = "#1e7d3a", "#c0392b", "#555"

imagem(
    "girar-aplicar-relativo.svg",
    "Cada folha gira ¼ a partir de onde está",
    [0, 90, 0],
    [(VERDE, "em pé"), (VERMELHO, "ficou deitada (estragou)"), (VERDE, "em pé")],
)
imagem(
    "girar-aplicar-copiar.svg",
    "Todas ficam viradas como a folha da vez",
    [0, 0, 0],
    [(VERDE, "em pé"), (VERDE, "continua em pé"), (VERDE, "em pé")],
)
print("ok")
