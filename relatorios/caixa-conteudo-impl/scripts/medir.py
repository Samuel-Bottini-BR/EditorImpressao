"""Mede as caixas do ScanTailor (core/caixas_scantailor.py) nas páginas que o
pesquisador mediu em 12/10/2026 e compara com os números dele.

O QUE FAZ
    Para cada página de tests/dados/caixas_scantailor_pesquisador.json:
      - chama core.caixas_scantailor.achar() com o MESMO DPI e do mesmo jeito
        do programa de teste dele (sempre "preto no branco");
      - compara as caixas (página, conteúdo antes do corte pela página);
      - guarda o tempo de cada parte (preparo, caixa da página, caixa do
        conteúdo), a melhor de `--vezes` rodadas;
      - repete com o "claro no escuro" decidido pelo ScanTailor (o de fábrica
        dele) e diz em que páginas a caixa muda;
      - mede o DPI que o programa diria (achar_na_pagina) nas páginas do
        gabarito.
    Grava relatorios/caixa-conteudo-impl/dados/medidas.json.

    Não muda o programa nem as páginas (os livros e as pastas de fora são
    somente leitura). Uma página por vez na memória.

COMO RODAR (da raiz da worktree, com a .venv da pasta principal)
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\caixa-conteudo-impl\\scripts\\medir.py
    opções: --vezes 3 (rodadas por página; fica a mais rápida)
            --so siebmacher_p007 horas_p013 (só estas páginas)

SEGURO MUDAR: as opções e o que é impresso. ARRISCADO: os caminhos de leitura.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from core import caixas_scantailor as cs  # noqa: E402

DADOS_DO_PESQUISADOR = RAIZ / "tests" / "dados" / "caixas_scantailor_pesquisador.json"
GABARITO = RAIZ / "gabarito"
# Somente leitura (fora do projeto).
ARQUIVOS = Path(r"D:\programas\EditorImpressao-arquivos")
FAIXA = ARQUIVOS / "revisar-decisoes-trabalho" / "faixa"
LIVROS = ARQUIVOS / "TESTES EDITOR DE IMPRESSAO" / "LIVROS PARA TESTE"


def carregar(fonte: dict) -> np.ndarray | None:
    """A imagem (BGR) de uma página, ou None se a fonte não existe neste PC."""
    if fonte["tipo"] == "gabarito":
        return cv2.imread(str(GABARITO / "paginas" / fonte["png"]), cv2.IMREAD_COLOR)
    if fonte["tipo"] == "faixa":
        return cv2.imread(str(FAIXA / fonte["png"]), cv2.IMREAD_COLOR)
    if fonte["tipo"] == "livro":
        import fitz

        livro = Path(fonte["livro"])
        if not livro.is_absolute():
            livro = LIVROS / livro
        if not livro.is_file():
            return None
        with fitz.open(str(livro)) as doc:
            pix = doc[fonte["pagina"] - 1].get_pixmap(dpi=fonte["dpi_do_desenho"], alpha=False)
            rgb = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR if pix.n == 3 else cv2.COLOR_GRAY2BGR)
    return None


def _lista(caixa) -> list[float] | None:
    return None if caixa is None else [round(v, 3) for v in caixa.como_tupla()]


def _maior_diferenca(minha, dele) -> float | None:
    if minha is None or dele is None:
        return None
    return max(abs(a - b) for a, b in zip(minha, dele))


def medir_pagina(nome: str, esperado: dict, vezes: int) -> dict:
    img = carregar(esperado["fonte"])
    if img is None:
        return {"faltou": True}
    altura, largura = img.shape[:2]
    saida: dict = {"largura": largura, "altura": altura, "dpi": esperado["dpi"],
                   "tamanho_confere": [largura, altura] == [esperado["largura"], esperado["altura"]]}
    melhor = None
    for _ in range(vezes):
        r = cs.achar(img, esperado["dpi"], claro_no_escuro=False)
        if not r.disponivel:
            return {**saida, "erro": r.motivo, "detalhe": r.detalhe_tecnico}
        if melhor is None or r.segundos < melhor.segundos:
            melhor = r
    r = melhor
    saida.update({
        "pagina": _lista(r.pagina), "conteudo": _lista(r.conteudo), "conteudo_bruto": _lista(r.conteudo_bruto),
        "pagina_mm": _lista(r.pagina_mm), "conteudo_mm": _lista(r.conteudo_mm),
        "tamanho_do_conteudo_mm": None if r.tamanho_do_conteudo_mm is None
        else [round(v, 3) for v in r.tamanho_do_conteudo_mm],
        "segundos": round(r.segundos, 3), "segundos_do_preparo": round(r.segundos_do_preparo, 3),
        "segundos_da_pagina": round(r.segundos_da_pagina, 3),
        "segundos_do_conteudo": round(r.segundos_do_conteudo, 3),
        "megapontos_a_150": round(cs.pontos_a_150(largura, altura, *r.dpi) / 1e6, 2),
        "diferenca_pagina": _maior_diferenca(_lista(r.pagina), esperado["pagina"]),
        "diferenca_conteudo": _maior_diferenca(_lista(r.conteudo_bruto), esperado["conteudo_na_pagina"]),
        "conteudo_passava_da_pagina": _lista(r.conteudo) != _lista(r.conteudo_bruto),
    })
    # O "claro no escuro" decidido pelo ScanTailor (o de fábrica dele).
    auto = cs.achar(img, esperado["dpi"], claro_no_escuro=None)
    saida["scantailor_viu_claro_no_escuro"] = not auto.preto_no_branco
    if not auto.preto_no_branco:
        saida["invertida"] = {"pagina": _lista(auto.pagina), "conteudo": _lista(auto.conteudo)}
    # As outras duas contas que o pesquisador mediu: sem a caixa da página e
    # com o "ajustar os cantos".
    folha = cs.achar(img, esperado["dpi"], achar_pagina=False, claro_no_escuro=False)
    saida["conteudo_folha"] = _lista(folha.conteudo_bruto)
    saida["diferenca_conteudo_folha"] = _maior_diferenca(_lista(folha.conteudo_bruto), esperado["conteudo_folha"])
    cantos = cs.achar(img, esperado["dpi"], ajustar_cantos=True, claro_no_escuro=False)
    saida["pagina_cantos"] = _lista(cantos.pagina)
    saida["conteudo_na_pagina_cantos"] = _lista(cantos.conteudo_bruto)
    saida["diferenca_pagina_cantos"] = _maior_diferenca(_lista(cantos.pagina), esperado["pagina_cantos"])
    saida["diferenca_conteudo_cantos"] = _maior_diferenca(_lista(cantos.conteudo_bruto),
                                                          esperado["conteudo_na_pagina_cantos"])
    # O DPI que o programa diria (só faz sentido nas páginas do gabarito, que
    # têm o DPI do desenho e o do scan na lista).
    if esperado["fonte"]["tipo"] == "gabarito" and "@" not in nome:
        lista = json.loads((GABARITO / "lista.json").read_text(encoding="utf-8"))["paginas"].get(nome)
        if lista:
            dpi_dito = cs.dpi_para_as_caixas(largura, altura, lista["dpi_png"], lista.get("dpi_scan"))
            saida["dpi_do_programa"] = round(dpi_dito, 1)
            if round(dpi_dito) != esperado["dpi"]:
                p = cs.achar_na_pagina(img, lista["dpi_png"], lista.get("dpi_scan"), claro_no_escuro=False)
                saida["com_o_dpi_do_programa"] = {
                    "pagina": _lista(p.pagina), "conteudo": _lista(p.conteudo),
                    "conteudo_mm": _lista(p.conteudo_mm), "segundos": round(p.segundos, 3)}
    return saida


def main() -> None:
    analisador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analisador.add_argument("--vezes", type=int, default=2)
    analisador.add_argument("--so", nargs="*", default=None)
    opcoes = analisador.parse_args()

    esperados = json.loads(DADOS_DO_PESQUISADOR.read_text(encoding="utf-8"))["paginas"]
    destino = PASTA / "dados" / "medidas.json"
    medidas = json.loads(destino.read_text(encoding="utf-8")) if destino.is_file() and opcoes.so else {}
    inicio = time.perf_counter()
    for nome, esperado in esperados.items():
        if opcoes.so and nome not in opcoes.so:
            continue
        m = medir_pagina(nome, esperado, opcoes.vezes)
        medidas[nome] = m
        print(nome, json.dumps({k: m.get(k) for k in (
            "faltou", "erro", "pagina", "conteudo_bruto", "diferenca_pagina", "diferenca_conteudo",
            "diferenca_conteudo_folha", "diferenca_pagina_cantos", "diferenca_conteudo_cantos",
            "conteudo_passava_da_pagina", "scantailor_viu_claro_no_escuro", "segundos", "segundos_do_preparo",
            "segundos_da_pagina", "segundos_do_conteudo", "megapontos_a_150", "dpi_do_programa")},
            ensure_ascii=False), flush=True)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(medidas, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"gravou {destino} em {time.perf_counter() - inicio:.0f} s", flush=True)


if __name__ == "__main__":
    main()
