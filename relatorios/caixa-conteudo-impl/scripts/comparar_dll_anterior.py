"""Confere que as três ferramentas que já existiam na st_ferramentas.dll
(limpar pontinhos, dividir, endireitar) dão O MESMO com a DLL nova (versão 4,
com as caixas) e com a anterior (versão 3, a do ramo fase-1).

O QUE FAZ
    Tira a DLL anterior do git (git show origin/fase-1:core/nativo/
    st_ferramentas.dll) para saida_teste/caixa-conteudo/dll-v3/ (fora do git),
    abre as duas no mesmo processo e, em cada página PNG de gabarito/paginas:
      - limpar pontinhos nas forças pouco, normal e muito (ponto a ponto);
      - dividir nos modos automático, uma página + sobra e duas páginas (tipo e
        cortes);
      - endireitar (ângulo, ângulo bruto, confiança, "preto no branco").
    Grava relatorios/caixa-conteudo-impl/dados/dll-anterior.json e sai com
    código 1 se houver qualquer diferença.

    Não muda o programa nem as páginas. Uma página por vez na memória.

COMO RODAR (da raiz da worktree, com a .venv da pasta principal)
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\caixa-conteudo-impl\\scripts\\comparar_dll_anterior.py

ARRISCADO: o ramo de onde sai a DLL anterior (RAMO_ANTERIOR). Depois de este
trabalho ser juntado ao fase-1, a "anterior" de lá já é a nova; use o commit
4b19a9b (o fase-1 de 12/10/2026, antes das caixas).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from core import dividir_scantailor as ds  # noqa: E402
from core import endireitar_scantailor as es  # noqa: E402
from core import pontinhos_scantailor as ps  # noqa: E402
from core import st_ferramentas as st  # noqa: E402

RAMO_ANTERIOR = "4b19a9b"          # o fase-1 de 12/10/2026, antes das caixas
PASTA_DA_ANTERIOR = RAIZ / "saida_teste" / "caixa-conteudo" / "dll-v3"


def abrir_a_anterior() -> st.BibliotecaScanTailor:
    """A DLL da versão 3, tirada do git, aberta com os tipos da versão 3."""
    PASTA_DA_ANTERIOR.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_DA_ANTERIOR / "st_ferramentas.dll"
    conteudo = subprocess.run(["git", "-C", str(RAIZ), "show", f"{RAMO_ANTERIOR}:core/nativo/st_ferramentas.dll"],
                              capture_output=True, check=True).stdout
    caminho.write_bytes(conteudo)
    biblioteca = st.BibliotecaScanTailor(caminho)
    versao, assinaturas = st.VERSAO_API, st.ASSINATURAS
    try:
        st.VERSAO_API = 3
        st.ASSINATURAS = {k: v for k, v in assinaturas.items() if k != "st_ferramentas_caixas"}
        if not biblioteca.disponivel:
            raise SystemExit(f"a DLL anterior não abriu: {biblioteca.motivo_indisponivel} "
                             f"({biblioteca.detalhe_indisponivel})")
    finally:
        st.VERSAO_API, st.ASSINATURAS = versao, assinaturas
    return biblioteca


def main() -> int:
    nova = st.padrao()
    if not nova.disponivel:
        raise SystemExit(f"a DLL nova não abriu: {nova.motivo_indisponivel}")
    anterior = abrir_a_anterior()
    lista = json.loads((RAIZ / "gabarito" / "lista.json").read_text(encoding="utf-8"))["paginas"]
    paginas = sorted((RAIZ / "gabarito" / "paginas").glob("*.png"))
    contas = {"pontinhos": [0, 0], "dividir": [0, 0], "endireitar": [0, 0]}     # [iguais, total]
    diferentes = []
    for png in paginas:
        img = cv2.imread(str(png), cv2.IMREAD_COLOR)
        dpi = float(lista.get(png.stem, {}).get("dpi_png", 300))
        cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binaria = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        for forca in ("pouco", "normal", "muito"):
            a = ps.limpar_pontinhos(binaria, dpi, forca, biblioteca=anterior)
            b = ps.limpar_pontinhos(binaria, dpi, forca, biblioteca=nova)
            igual = a.disponivel and b.disponivel and np.array_equal(a.imagem, b.imagem)
            contas["pontinhos"][0] += igual
            contas["pontinhos"][1] += 1
            if not igual:
                diferentes.append(f"pontinhos {png.stem} {forca}")
        for modo in (ds.MODO_AUTOMATICO, ds.MODO_COM_SOBRA, ds.MODO_DUAS_PAGINAS):
            a = ds.achar(img, dpi, modo, biblioteca=anterior)
            b = ds.achar(img, dpi, modo, biblioteca=nova)
            igual = a.disponivel and b.disponivel and a.tipo == b.tipo and a.cortes == b.cortes
            contas["dividir"][0] += igual
            contas["dividir"][1] += 1
            if not igual:
                diferentes.append(f"dividir {png.stem} modo {modo}")
        a = es.medir(img, dpi, biblioteca=anterior)
        b = es.medir(img, dpi, biblioteca=nova)
        igual = (a.disponivel and b.disponivel and (a.angulo, a.angulo_bruto, a.confianca, a.preto_no_branco)
                 == (b.angulo, b.angulo_bruto, b.confianca, b.preto_no_branco))
        contas["endireitar"][0] += igual
        contas["endireitar"][1] += 1
        if not igual:
            diferentes.append(f"endireitar {png.stem}")
        print(png.stem, {k: tuple(v) for k, v in contas.items()}, flush=True)
    saida = {"dll_anterior": f"git show {RAMO_ANTERIOR}:core/nativo/st_ferramentas.dll (versão 3)",
             "paginas": len(paginas), "iguais_de_total": contas, "diferentes": diferentes}
    destino = PASTA / "dados" / "dll-anterior.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(saida, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(saida, ensure_ascii=False), flush=True)
    return 1 if diferentes else 0


if __name__ == "__main__":
    sys.exit(main())
