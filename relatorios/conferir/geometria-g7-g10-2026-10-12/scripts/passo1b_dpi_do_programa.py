"""Passo 1b (13/10/2026): refaz as caixas do ScanTailor com a FUNCAO DO PROGRAMA e o
DPI que o programa diz, e grava dados/caixas.json (o que o passo 2 le).

POR QUE
    Em 12/10 medi as caixas dizendo ao ScanTailor o DPI que o PDF diz (passo 1,
    dados/caixas-12-10.json). No Livro de Horas, no Graduale e no Marial o PDF diz
    72, que nao e a resolucao de verdade, e o programa diz outro numero as
    ferramentas do ScanTailor (limpar pontinhos, endireitar, gravura): o de
    core.caixas_scantailor.dpi_para_as_caixas (uns 130 a 140 nesses livros). Com
    ele a caixa do conteudo e outra (achado do implementador, ONDE-PAREI.md,
    ressalva 2). As imagens das perguntas tem de mostrar o que o programa vai fazer.

O QUE FAZ
    Para cada pagina de dados/caixas-12-10.json:
      - chama core.caixas_scantailor.achar_na_pagina(imagem, DPI do desenho, DPI do
        scan), do jeito de fabrica do programa ("claro no escuro" decidido pelo
        ScanTailor): caixa da pagina, caixa do conteudo dentro dela, o mesmo com
        "ajustar os cantos", e o conteudo na folha inteira;
      - guarda as caixas de 12/10 em "scantailor_12_10", para comparar;
      - o corte de hoje ("nosso") nao depende desse DPI e fica como estava.
    DPI do desenho e do scan: nas paginas do gabarito, os da gabarito/lista.json
    (dpi_png e dpi_scan), como o implementador fez em medir.py; nas paginas que eu
    desenhei de um livro (passo 0), o DPI em que desenhei e o DPI do scan lido no
    PDF pela mesma conta de core.pipeline._dpi_do_scan (largura da maior imagem /
    largura da pagina em polegadas); nas folhas da rodada 4 ("faixa"), 150 e scan
    desconhecido.
    Grava tambem dados/mudou-com-o-dpi.json: as paginas em que alguma beirada da
    caixa do conteudo andou mais de 2 pontos.

Nada aqui muda o programa nem as paginas. Uso: python passo1b_dpi_do_programa.py
"""
from __future__ import annotations

import json

import cv2

import comum
from comum import AZUL, LARANJA, VERDE, VERMELHO


def dpi_do_scan_no_pdf(livro: str, pagina: int) -> float | None:
    """A mesma conta de core.pipeline._dpi_do_scan, lida direto no PDF."""
    import fitz

    try:
        with fitz.open(livro) as doc:
            p = doc[pagina - 1]
            maior = max((int(i[2]) for i in p.get_images()), default=0)
            largura_pt = float(p.rect.width)
        return maior / (largura_pt / 72.0) if maior > 0 and largura_pt > 0 else None
    except Exception:  # noqa: BLE001 - sem o DPI do scan, vale o do desenho (como no programa)
        return None


def lista(caixa) -> list[float] | None:
    return None if caixa is None else [round(v, 2) for v in caixa.como_tupla()]


def inspecao(nome: str, png: str, d: dict) -> None:
    """Uma imagem com as caixas novas (cheias) e as de 12/10 (tracejadas), so para eu olhar."""
    img = comum.para_pil(cv2.imread(png, cv2.IMREAD_COLOR))
    e = max(3, img.width // 300)
    comum.retangulo(img, d["nosso"]["caixa"], LARANJA, e)
    novo, velho = d["scantailor"], d.get("scantailor_12_10", {})
    if velho.get("conteudo_na_pagina"):
        comum.retangulo(img, velho["conteudo_na_pagina"], VERMELHO, e, tracejado=True)
    comum.retangulo(img, novo["pagina"], AZUL, e)
    if novo.get("conteudo_na_pagina"):
        comum.retangulo(img, novo["conteudo_na_pagina"], VERDE, e)
    destino = comum.RASCUNHO / "inspecao-dpi-do-programa"
    destino.mkdir(parents=True, exist_ok=True)
    if img.width > 1100:
        img = img.resize((1100, round(img.height * 1100 / img.width)))
    img.save(destino / f"{nome}.jpg", quality=80)


def main() -> None:
    from core import caixas_scantailor as cs

    antigas = json.loads((comum.DADOS / "caixas-12-10.json").read_text(encoding="utf-8"))
    gabarito = comum.lista_do_gabarito()["paginas"]
    extras_arq = comum.DADOS / "paginas-extras.json"
    extras = json.loads(extras_arq.read_text(encoding="utf-8")) if extras_arq.exists() else {}

    dados, mudou = {}, {}
    for nome, d in antigas.items():
        if "@" in nome:                       # as medidas "a 150 DPI" de 12/10 nao sao mais usadas
            continue
        png, dpi_12_10 = d["png"], d["dpi"]
        if nome in gabarito:
            dpi_desenho, dpi_scan = float(gabarito[nome]["dpi_png"]), gabarito[nome].get("dpi_scan")
        elif nome in extras:
            dpi_desenho = float(extras[nome]["dpi"])
            dpi_scan = dpi_do_scan_no_pdf(extras[nome]["livro"], extras[nome]["pagina"])
        else:
            dpi_desenho, dpi_scan = float(dpi_12_10), None
        img = cv2.imread(png, cv2.IMREAD_COLOR)
        alt, larg = img.shape[:2]
        dpi_dito = cs.dpi_para_as_caixas(larg, alt, dpi_desenho, dpi_scan)
        r = cs.achar_na_pagina(img, dpi_desenho, dpi_scan)
        if not r.disponivel:
            raise SystemExit(f"{nome}: {r.motivo} ({r.detalhe_tecnico})")
        cantos = cs.achar_na_pagina(img, dpi_desenho, dpi_scan, ajustar_cantos=True)
        folha = cs.achar_na_pagina(img, dpi_desenho, dpi_scan, achar_pagina=False)
        novo = {
            "de_onde": "core.caixas_scantailor.achar_na_pagina (DLL do programa)",
            "dpi_do_desenho": dpi_desenho, "dpi_do_scan": None if dpi_scan is None else round(float(dpi_scan), 1),
            "dpi_dito": round(float(dpi_dito), 1), "preto_no_branco": r.preto_no_branco,
            "pagina": lista(r.pagina), "conteudo_na_pagina": lista(r.conteudo),
            "pagina_cantos": lista(cantos.pagina), "conteudo_na_pagina_cantos": lista(cantos.conteudo),
            "conteudo_folha": lista(folha.conteudo), "segundos": round(r.segundos, 2),
        }
        dados[nome] = {"png": png, "dpi": dpi_12_10, "nosso": d["nosso"], "scantailor": novo,
                       "scantailor_12_10": d["scantailor"]}
        a, b = d["scantailor"].get("conteudo_na_pagina"), novo["conteudo_na_pagina"]
        if a and b:
            # a de 12/10 ainda nao estava cortada pela caixa da pagina: corta para comparar igual
            p = d["scantailor"]["pagina"]
            a = [max(a[0], p[0]), max(a[1], p[1]), min(a[2], p[2]), min(a[3], p[3])]
            maior = max(abs(x - y) for x, y in zip(a, b))
            if maior > 2:
                mudou[nome] = {"dpi_12_10": dpi_12_10, "dpi_dito": novo["dpi_dito"],
                               "conteudo_12_10": [round(v) for v in a], "conteudo_agora": [round(v) for v in b],
                               "maior_diferenca_em_pontos": round(maior)}
        inspecao(nome, png, dados[nome])
        print(nome, "dpi", dpi_12_10, "->", novo["dpi_dito"], "| conteudo", [round(v) for v in b or []],
              "MUDOU" if nome in mudou else "", flush=True)
    (comum.DADOS / "caixas.json").write_text(json.dumps(dados, indent=1, ensure_ascii=False), encoding="utf-8")
    (comum.DADOS / "mudou-com-o-dpi.json").write_text(json.dumps(mudou, indent=1, ensure_ascii=False), encoding="utf-8")
    print("gravou dados/caixas.json e dados/mudou-com-o-dpi.json;", len(mudou), "paginas mudaram", flush=True)


if __name__ == "__main__":
    main()
