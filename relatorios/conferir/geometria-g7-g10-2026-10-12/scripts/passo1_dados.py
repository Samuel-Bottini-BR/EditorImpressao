"""Passo 1: mede, em cada pagina usada nas perguntas, onde cada conta corta.

ATENCAO (13/10/2026): este passo diz ao ScanTailor o DPI que o PDF diz (72 no
Livro de Horas, no Graduale e no Marial), e o programa NAO faz assim: ele diz o
DPI de core.caixas_scantailor.achar_na_pagina (uns 130 a 140 nesses livros), e a
caixa do conteudo muda. As imagens das perguntas usam o passo 1b
(passo1b_dpi_do_programa.py), que parte deste arquivo e refaz as caixas do
ScanTailor com a funcao e o DPI do programa. Este passo continua valendo para o
corte de hoje ("nosso") e como registro do que foi medido em 12/10.

Para cada pagina:
  - "nosso": o corte de bordas do NOSSO programa como roda hoje
    (core.recortar.detectar_bordas, o mesmo que o pipeline chama com "Cortar
    bordas" ligado), calculado na mesma imagem;
  - as caixas do ScanTailor Advanced v1.2.1 (codigo original), pelo programa de
    teste caixas.exe (scripts/caixas.cpp): caixa da pagina (item 2.13), com e
    sem "ajustar os cantos", e caixa do conteudo (item 2.5), na folha inteira e
    dentro da caixa da pagina.
Grava dados/caixas-12-10.json (tudo em pontos da imagem: x0, y0, x1, y1) e, para eu
conferir a olho, uma imagem por pagina com as caixas desenhadas em
saida_teste/geometria-perguntas/inspecao/ (fora do git).

Nada aqui muda o programa nem as paginas. Uso: python passo1_dados.py
"""
from __future__ import annotations

import json
import os
import subprocess

import cv2

import comum
from comum import AZUL, LARANJA, VERDE, VERMELHO

# Paginas do gabarito (nome -> DPI vem da lista.json).
DO_GABARITO = [
    "siebmacher_p007", "siebmacher_p009",
    "horas_p011", "horas_p013", "horas_p014", "horas_p026", "horas_p027", "horas_p047",
    "graduale_p221", "graduale_p222", "graduale_p223",
    "palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010", "palatino_p057",
    "palatino_p066", "palatino_p067",
    "escola_p007", "escola_p035", "marial_p007",
    "opusmajus_p003", "opusmajus_p011", "opusmajus_p020", "opusmajus_p165", "opusmajus_p256",
]

# Folhas cruas com borda preta, ja desenhadas a 150 DPI na rodada 4 do "Para revisar"
# (somente leitura): nome -> DPI.
DA_FAIXA = {"egenloff_p047": 150, "egenloff_p003": 150, "matematica_p032": 150, "camoes_p066": 150,
            "cursus_p314": 150, "antiphon_p088": 150}

def paginas_extras() -> dict[str, tuple[str, float]]:
    """As paginas desenhadas pelo passo 0 (dados/paginas-extras.json): nome -> (png, dpi)."""
    arquivo = comum.DADOS / "paginas-extras.json"
    if not arquivo.exists():
        return {}
    registro = json.loads(arquivo.read_text(encoding="utf-8"))
    return {nome: (d["png"], float(d["dpi"])) for nome, d in registro.items()}


def caixas_do_scantailor(paginas: dict[str, tuple[str, float]]) -> dict[str, dict]:
    """Roda caixas.exe (uma chamada, uma pagina por vez la dentro)."""
    env = dict(os.environ)
    env["PATH"] = str(comum.QT_BIN) + os.pathsep + env.get("PATH", "")
    env["QT_PLUGIN_PATH"] = str(comum.QT_BIN.parent / "plugins")
    resultado = {}
    for nome, (png, dpi) in paginas.items():
        r = subprocess.run([str(comum.CAIXAS_EXE), png, str(int(round(dpi)))], capture_output=True,
                           text=True, env=env, timeout=600)
        linha = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        try:
            resultado[nome] = json.loads(linha.replace("\\", "/"))
        except json.JSONDecodeError:
            print("FALHOU", nome, r.stdout[-300:], r.stderr[-300:], flush=True)
            resultado[nome] = {}
        print(nome, resultado[nome].get("pagina"), resultado[nome].get("conteudo_na_pagina"),
              resultado[nome].get("ms"), "ms", flush=True)
    return resultado


def nosso_corte(png: str, dpi: float) -> dict:
    from core.recortar import detectar_bordas

    img = cv2.imread(png, cv2.IMREAD_COLOR)
    alt, larg = img.shape[:2]
    r = detectar_bordas(img, dpi=dpi)
    return {"caixa": [r.x * larg, r.y * alt, (r.x + r.largura) * larg, (r.y + r.altura) * alt],
            "encostou": bool(r.encostou_no_conteudo), "tamanho": [larg, alt]}


def inspecao(nome: str, png: str, d: dict) -> None:
    """Uma imagem com as caixas, so para o pesquisador olhar."""
    img = comum.para_pil(cv2.imread(png, cv2.IMREAD_COLOR))
    e = max(3, img.width // 300)
    if d.get("nosso"):
        comum.retangulo(img, d["nosso"]["caixa"], LARANJA, e)
    st = d.get("scantailor", {})
    for chave, cor, trac in (("pagina", AZUL, False), ("pagina_cantos", AZUL, True),
                             ("conteudo_na_pagina", VERDE, False), ("conteudo_folha", VERMELHO, True)):
        if st.get(chave):
            comum.retangulo(img, st[chave], cor, e, tracejado=trac)
    destino = comum.RASCUNHO / "inspecao"
    destino.mkdir(parents=True, exist_ok=True)
    if img.width > 1100:
        img = img.resize((1100, round(img.height * 1100 / img.width)))
    img.save(destino / f"{nome}.jpg", quality=80)


def main() -> None:
    lista = comum.lista_do_gabarito()["paginas"]
    paginas: dict[str, tuple[str, float]] = {}
    for nome in DO_GABARITO:
        paginas[nome] = (str(comum.GABARITO / lista[nome]["png"]), float(lista[nome]["dpi_png"]))
    for nome, dpi in DA_FAIXA.items():
        paginas[nome] = (str(comum.FAIXA / f"{nome}.png"), dpi)
    paginas.update(paginas_extras())

    st = caixas_do_scantailor(paginas)
    # O mesmo Horas 13 e Graduale 222 com o DPI que o pesquisador usou em 01/10 (150),
    # para ver quanto o DPI declarado muda a caixa do ScanTailor.
    extra = caixas_do_scantailor({f"{n}@150": (paginas[n][0], 150) for n in ("horas_p013", "graduale_p222")})

    dados = {}
    for nome, (png, dpi) in paginas.items():
        dados[nome] = {"png": png, "dpi": dpi, "nosso": nosso_corte(png, dpi), "scantailor": st.get(nome, {})}
        inspecao(nome, png, dados[nome])
        print(nome, "nosso", [round(v) for v in dados[nome]["nosso"]["caixa"]], flush=True)
    for nome, d in extra.items():
        dados[nome] = {"scantailor": d}
    comum.DADOS.mkdir(parents=True, exist_ok=True)
    (comum.DADOS / "caixas-12-10.json").write_text(json.dumps(dados, indent=1, ensure_ascii=False), encoding="utf-8")
    print("gravou dados/caixas-12-10.json", flush=True)


if __name__ == "__main__":
    main()
