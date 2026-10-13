"""Desenha as três opções da pergunta g6-retangulo-onde da página de escolhas (09/10/2026).

O Samuel escolheu "Fica no mesmo lugar (como no ScanTailor)" e perguntou: "Posso ter as
duas opções mas a opção do scantailor ficar como padrão?". A resposta é sim; a pergunta
nova é ONDE fica a troca. Cada desenho é um esquema da tela (não a tela de verdade) com
a troca destacada em laranja:
  a) tela "O que fazer", por livro, ao lado da "Conta do endireitar:";
  b) Configurações, para todos os livros;
  c) ferramenta Endireitar, por página, junto do "aplicar em".

Uso:  python desenhos_g6_retangulo_onde.py <pasta de saída>
Grava retangulo-onde-livro.svg, retangulo-onde-configuracoes.svg e
retangulo-onde-pagina.svg; a gerente publica como img/g6/<nome>.svg.

Seguro mudar: textos, cores, tamanhos. A aparência final é do agente de layout;
estes desenhos só mostram o lugar.
"""
import os
import sys

SAIDA = sys.argv[1]
os.makedirs(SAIDA, exist_ok=True)

FUNDO = "#1E1F22"; JANELA = "#2a2c30"; BARRA = "#34373c"; TITULO = "#E6E6E6"
LEG = "#AEB4BD"; FRACO = "#7d838c"; LARANJA = "#F0A55C"; AZUL = "#2F6FE0"
PAPEL = "#EFE6D2"; TINTA = "#5a4a32"; VERDE = "#3FBF6F"
F = 'font-family="Segoe UI, Arial"'
W, H = 560, 380


def txt(x, y, s, cor=LEG, tam=13, peso=None, meio=False):
    p = f' font-weight="{peso}"' if peso else ""
    a = ' text-anchor="middle"' if meio else ""
    return f'<text x="{x}" y="{y}" fill="{cor}" font-size="{tam}" {F}{p}{a}>{s}</text>'


def caixa_lista(x, y, w, texto, destaque=False):
    """Uma caixinha de escolha (lista que abre) com o texto escolhido."""
    cor = LARANJA if destaque else FRACO
    return (f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="4" fill="{BARRA}" stroke="{cor}" stroke-width="{2 if destaque else 1}"/>'
            + txt(x + 8, y + 16, texto, TITULO if destaque else LEG, 12)
            + f'<path d="M{x + w - 16} {y + 10} l5 5 l5 -5" fill="none" stroke="{LEG}" stroke-width="1.5"/>')


def realce(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" stroke="{LARANJA}" stroke-width="2.5" stroke-dasharray="6 4"/>'


def moldura(titulo_janela, corpo, rodape):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" role="img">'
            f'<rect width="{W}" height="{H}" rx="8" fill="{FUNDO}"/>'
            f'<rect x="16" y="16" width="{W - 32}" height="{H - 92}" rx="6" fill="{JANELA}" stroke="#44474d"/>'
            f'<rect x="16" y="16" width="{W - 32}" height="28" rx="6" fill="{BARRA}"/>'
            + txt(28, 35, titulo_janela, TITULO, 13, 600)
            + txt(W - 28, 35, "esquema, não é a tela de verdade", FRACO, 11, None, False).replace("<text ", '<text text-anchor="end" ', 1)
            + corpo
            + "".join(txt(16, H - 52 + 18 * i, linha, LARANJA if i == 0 else LEG, 13, 600 if i == 0 else None)
                      for i, linha in enumerate(rodape))
            + "</svg>")


def livro():
    c = txt(36, 72, "O que fazer com este livro", TITULO, 15, 600)
    c += f'<rect x="36" y="88" width="14" height="14" rx="2" fill="none" stroke="{LEG}"/>' + txt(58, 100, "Dividir folhas ao meio")
    c += f'<rect x="36" y="114" width="14" height="14" rx="2" fill="{AZUL}"/>' + txt(58, 126, "Endireitar as páginas")
    c += txt(58, 156, "Conta do endireitar:") + caixa_lista(200, 142, 170, "a do ScanTailor")
    c += realce(48, 172, 470, 40)
    c += txt(58, 197, "Corte à mão, ao mudar o ângulo:", TITULO) + caixa_lista(276, 182, 222, "Fica no mesmo lugar", True)
    c += txt(58, 238, "(as outras escolhas da tela continuam como hoje)", FRACO, 12)
    c += f'<rect x="400" y="256" width="120" height="26" rx="5" fill="{AZUL}"/>' + txt(460, 274, "continuar", "#fff", 13, 600, True)
    return moldura("Editor de Impressão", c, [
        "(a) Na tela \"O que fazer\": uma escolha por livro.",
        "Fica logo abaixo da \"Conta do endireitar:\", que já existe.",
        "Vem em \"Fica no mesmo lugar\"; troca o livro inteiro."])


def configuracoes():
    c = txt(36, 72, "Configurações", TITULO, 15, 600)
    for i, s in enumerate(["...", "Atalhos", "Endireitar", "..."]):
        y = 92 + 30 * i
        sel = s == "Endireitar"
        c += f'<rect x="36" y="{y}" width="110" height="24" rx="4" fill="{AZUL if sel else BARRA}"/>' + txt(46, y + 16, s, "#fff" if sel else LEG, 12)
    c += f'<line x1="160" y1="88" x2="160" y2="270" stroke="#44474d"/>'
    c += txt(176, 104, "Para todos os livros", FRACO, 12)
    c += realce(168, 116, 352, 66)
    c += txt(180, 138, "Corte à mão, ao mudar o ângulo:", TITULO) + caixa_lista(180, 148, 232, "Fica no mesmo lugar", True)
    return moldura("Configurações", c, [
        "(b) Nas Configurações: vale para todos os livros.",
        "Escolhe uma vez e não pergunta mais; o livro não tem",
        "uma escolha própria."])


def pagina():
    c = txt(30, 66, "inclinação:", LEG, 12) + f'<rect x="100" y="52" width="70" height="22" rx="4" fill="{BARRA}"/>' + txt(135, 67, "◀ 0,3° ▶", TITULO, 12, None, True)
    c += txt(184, 66, "aplicar em:", LEG, 12) + caixa_lista(250, 52, 120, "esta página")
    c += realce(378, 48, 150, 32)
    c += caixa_lista(384, 52, 140, "fica no lugar", True)
    # a página, um pouco girada, com a grade azul e o retângulo verde
    c += '<g opacity="0.35">' + "".join(f'<line x1="{x}" y1="90" x2="{x}" y2="276" stroke="{AZUL}"/>' for x in range(120, 461, 40)) + "</g>"
    c += f'<g transform="rotate(2 280 182)"><rect x="200" y="92" width="160" height="180" fill="{PAPEL}"/>'
    c += "".join(f'<rect x="216" y="{y}" width="128" height="5" fill="{TINTA}"/>' for y in range(112, 260, 12)) + "</g>"
    c += f'<rect x="208" y="102" width="144" height="164" fill="none" stroke="{VERDE}" stroke-width="2.5" stroke-dasharray="6 4"/>'
    return moldura("Ferramenta Endireitar", c, [
        "(c) Na ferramenta Endireitar: uma escolha por página.",
        "Fica junto do \"aplicar em\" (esta página, todas, daqui em diante).",
        "Mais controle, mas é mais uma coisa na barra."])


for nome, svg in (("retangulo-onde-livro", livro()), ("retangulo-onde-configuracoes", configuracoes()), ("retangulo-onde-pagina", pagina())):
    with open(os.path.join(SAIDA, nome + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print(nome)
