"""D3 (decisao do Samuel, 02/10/2026): nosso endireitar/girar/dividir x o do ScanTailor.

So MOSTRA; nao muda nada no programa. Rodar da raiz do projeto:

    .venv\\Scripts\\python.exe relatorios\\fase2-geometria-d3-2026-10-05\\scripts\\comparar_d3.py

O que faz, para cada pagina-gabarito (gabarito/paginas/<nome>.pdf, a copia da
pagina do PDF original):

1. NOSSO: o mesmo caminho do programa para o PDF final. analisar_projeto
   (dividir: detectar_lombada a 150 DPI), a folha desenhada a 300 DPI
   (projeto.qualidade_dpi), preparar_para_recorte, pipeline._geometria
   (corte detectar_bordas + angulo detectar_angulo na pagina ja cortada,
   folga do giro) e preparar_metade. Tudo com as opcoes de fabrica do livro
   (dividir, cortar e endireitar marcados).
2. SCANTAILOR: a MESMA imagem de 300 DPI vai para o geometria_d3.exe (codigo
   do ScanTailor Advanced v1.2.1, compilado numa pasta de teste fora do
   projeto: D:\\programas\\EditorImpressao-arquivos\\ferramentas\\geometria-d3-2026-10-05),
   que faz o que o ScanTailor faz sozinho: dividir (page_split, modo
   automatico) e endireitar cada pagina (deskew, com a limpeza das sombras).
   Girar de 90 em 90: nenhum dos dois programas tem automatico.
3. Uma imagem por pagina, lado a lado (nosso | ScanTailor), com linhas-guia
   horizontais, e uma tabela com os numeros.

Sentido do angulo: o ScanTailor devolve o giro no sentido do Qt (positivo =
horario na tela); o nosso, no sentido do OpenCV (positivo = anti-horario). O
script confere isso numa folha sintetica (--sinal do exe) antes de comparar, e
a tabela mostra os dois JA no mesmo sentido.

Arquivos temporarios (PNG de 300 DPI) vao para a pasta tmp do teste, em D:,
e sao apagados um a um (o disco C esta quase cheio).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

from core import pipeline  # noqa: E402
from core.endireitar import ANGULO_MINIMO, detectar_angulo, rotacionar  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402
from modelos import Projeto  # noqa: E402

PASTA = Path(__file__).resolve().parents[1]
IMAGENS = PASTA / "imagens"
GABARITO = Path(r"D:\programas\EditorImpressao\gabarito")   # as paginas ficam so na pasta principal
TESTE = Path(r"D:\programas\EditorImpressao-arquivos\ferramentas\geometria-d3-2026-10-05")
EXE = TESTE / "build" / "Release" / "geometria_d3.exe"
TMP = TESTE / "tmp"
DPI = 300

# As paginas com imagem lado a lado: as que o Samuel citou na D3 (Horas 11 e
# 47, Siebmacher 7 e 9) e as de endireitar/dividir/girar do gabarito.
COM_IMAGEM = ["horas_p011", "horas_p047", "siebmacher_p007", "siebmacher_p009",
              "graduale_p221", "escola_p007", "escola_p035", "opusmajus_p256"]


def rodar_exe(*args: str) -> str:
    """Roda o geometria_d3.exe com o Qt do teste no PATH e devolve a saida."""
    import os

    env = dict(os.environ)
    qt = r"D:\programas\EditorImpressao-arquivos\ferramentas\qt\6.11.1\msvc2022_64\bin"
    env["PATH"] = qt + ";" + env.get("PATH", "")
    r = subprocess.run([str(EXE), *args], capture_output=True, text=True, env=env, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"geometria_d3 falhou ({r.returncode}): {r.stderr[-2000:]}")
    return r.stdout


def ler_saida(texto: str) -> list[dict]:
    """Transforma a saida do exe em uma lista de medidas por pagina."""
    paginas: list[dict] = []
    atual: dict | None = None
    for linha in texto.splitlines():
        partes = linha.split()
        if not partes:
            continue
        chave = partes[0]
        campos = dict(p.split("=", 1) for p in partes[1:] if "=" in p)
        if chave in ("PAGINA", "SINAL"):
            atual = {"rotulo": linha, "cortes": [], "subs": []}
            paginas.append(atual)
        elif atual is None:
            continue
        elif chave == "SPLIT":
            atual["tipo"] = campos["tipo"]
        elif chave == "CORTE":
            atual["cortes"].append(tuple(float(campos[k]) for k in ("x1", "y1", "x2", "y2")))
        elif chave == "SUB":
            sub = {"nome": partes[1]}
            for k, v in campos.items():
                sub[k] = float(v)
            atual["subs"].append(sub)
        elif chave == "TAMANHO":
            atual["w"], atual["h"] = int(campos["w"]), int(campos["h"])
    return paginas


def fator_do_sentido() -> tuple[float, str]:
    """Quanto multiplicar o angulo do ScanTailor para ficar no sentido do nosso.

    A folha sintetica e desenhada girada +2 graus no sentido do Qt (horario).
    Para endireitar, o OpenCV precisa girar +2 (anti-horario). O fator e
    (+2) / (angulo que o ScanTailor devolveu). Tambem confere o nosso
    detectar_angulo numa folha girada do mesmo jeito.
    """
    medidas = ler_saida(rodar_exe("--sinal"))
    st_mais = medidas[0]["subs"][0]["angulo_efetivo"]
    st_menos = medidas[1]["subs"][0]["angulo_efetivo"]
    fator = 2.0 / st_mais if abs(st_mais) > 0.5 else float("nan")

    # o nosso, na mesma folha: retangulos pretos em linhas, girados 2 graus no
    # sentido horario (cv2 com angulo -2)
    img = np.full((1754, 1240), 255, np.uint8)
    for y in range(200, 1550, 40):
        for x in range(150, 1090, 60):
            img[y:y + 18, x:x + 45] = 0
    m = cv2.getRotationMatrix2D((620, 877), -2.0, 1.0)
    girada = cv2.warpAffine(img, m, (1240, 1754), borderValue=255)
    nosso = detectar_angulo(girada).angulo
    texto = (f"Folha sintética girada 2° no sentido horário: o ScanTailor devolve {st_mais:+.2f} "
             f"(e {st_menos:+.2f} para a girada ao contrário); o nosso devolve {nosso:+.2f}. "
             f"Fator usado para pôr o ScanTailor no sentido do nosso: {fator:+.0f}.")
    return fator, texto


def nossa_geometria(nome: str, lista: dict) -> dict:
    """O que o NOSSO programa faria com esta folha (caminho do PDF final)."""
    pdf = GABARITO / "paginas" / f"{nome}.pdf"
    projeto = Projeto(caminho_entrada=str(pdf), qualidade_dpi=DPI)
    pipeline.analisar_projeto(projeto)
    folha = projeto.folhas[0]
    doc = abrir_pdf(pdf)
    try:
        img = pagina_para_array(doc, 0, dpi=DPI)
    finally:
        doc.close()
    paginas = []
    for pagina in projeto.paginas:
        base = pipeline.preparar_para_recorte(img, folha, pagina)
        recorte, angulo = pipeline._geometria(base, pagina, projeto, dpi=DPI)
        final = pipeline.preparar_metade(img, folha, pagina, projeto, geometria=(recorte, angulo))
        paginas.append({"metade": pagina.metade, "recorte": recorte, "angulo": float(angulo),
                        "aplicado": float(angulo) if abs(angulo) >= ANGULO_MINIMO else 0.0,
                        "final": final, "largura_base": base.shape[1]})
    return {"img": img, "dividir": bool(folha.dividir), "posicao": float(folha.posicao_corte),
            "confianca": float(folha.confianca_corte), "e_paisagem": bool(folha.e_paisagem),
            "angulo_analise": float(folha.angulo_detectado), "paginas": paginas}


def scantailor(img: np.ndarray, nome: str, fator: float) -> dict:
    """O que o ScanTailor acha nesta mesma imagem (300 DPI)."""
    TMP.mkdir(parents=True, exist_ok=True)
    arquivo = TMP / f"{nome}_300.png"
    cv2.imwrite(str(arquivo), img)
    try:
        med = ler_saida(rodar_exe(str(arquivo), str(DPI)))[0]
    finally:
        arquivo.unlink(missing_ok=True)
    finais = []
    for sub in med["subs"]:
        x, y, w, h = (int(sub[k]) for k in ("x", "y", "w", "h"))
        pedaco = img[y:y + h, x:x + w]
        angulo = sub["angulo_efetivo"] * fator
        finais.append({"nome": sub["nome"], "angulo": angulo, "bruto": sub["angulo_bruto"] * fator,
                       "confianca": sub["confianca"], "caixa": (x, y, w, h),
                       "final": rotacionar(pedaco, angulo) if abs(angulo) >= ANGULO_MINIMO else pedaco})
    return {"tipo": med["tipo"], "cortes": med["cortes"], "subs": finais, "w": med["w"]}


def scantailor_no_dpi_do_scan(nome: str, info: dict, fator: float) -> dict:
    """Variante: o PNG do gabarito, no DPI dele (o do escaneamento, ate 400)."""
    png = GABARITO / info["png"]
    med = ler_saida(rodar_exe(str(png), str(int(info["dpi_png"]))))[0]
    return {"tipo": med["tipo"], "w": med["w"],
            "cortes": [round(100 * 0.5 * (c[0] + c[2]) / med["w"], 1) for c in med["cortes"]],
            "angulos": [round(s["angulo_efetivo"] * fator, 2) for s in med["subs"]]}


# --- desenho -----------------------------------------------------------------

AZUL, VERMELHO, VERDE, CIANO = (200, 90, 20), (40, 40, 220), (40, 160, 40), (200, 170, 0)


def _reduzir(img: np.ndarray, altura: int) -> tuple[np.ndarray, float]:
    escala = altura / img.shape[0]
    return cv2.resize(img, (max(1, int(img.shape[1] * escala)), altura),
                      interpolation=cv2.INTER_AREA), escala


def _com_guias(img: np.ndarray, n: int = 24) -> np.ndarray:
    """Linhas-guia horizontais finas: texto torto cruza as guias."""
    saida = img.copy() if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for i in range(1, n):
        y = int(i * saida.shape[0] / n)
        cv2.line(saida, (0, y), (saida.shape[1] - 1, y), CIANO, 1, cv2.LINE_AA)
    return saida


def _titulo(img: np.ndarray, texto: str, cor=(30, 30, 30)) -> np.ndarray:
    faixa = np.full((44, img.shape[1], 3), 255, np.uint8)
    cv2.putText(faixa, texto, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, cor, 2, cv2.LINE_AA)
    return np.vstack([faixa, img])


def _lado_a_lado(imgs: list[np.ndarray], espaco: int = 12) -> np.ndarray:
    altura = max(i.shape[0] for i in imgs)
    partes = []
    for k, i in enumerate(imgs):
        if i.shape[0] < altura:
            i = np.vstack([i, np.full((altura - i.shape[0], i.shape[1], 3), 255, np.uint8)])
        partes.append(i)
        if k < len(imgs) - 1:
            partes.append(np.full((altura, espaco, 3), 255, np.uint8))
    return np.hstack(partes)


def _empilhar(imgs: list[np.ndarray], espaco: int = 12) -> np.ndarray:
    largura = max(i.shape[1] for i in imgs)
    partes = []
    for k, i in enumerate(imgs):
        if i.shape[1] < largura:
            i = np.hstack([i, np.full((i.shape[0], largura - i.shape[1], 3), 255, np.uint8)])
        partes.append(i)
        if k < len(imgs) - 1:
            partes.append(np.full((espaco, largura, 3), 255, np.uint8))
    return np.vstack(partes)


def _faixa_do_meio(img: np.ndarray, largura: int) -> np.ndarray:
    """Uma faixa horizontal do meio da pagina, ampliada, com tres guias."""
    h = img.shape[0]
    faixa = img[int(h * 0.42):int(h * 0.58)]
    faixa = cv2.resize(faixa, (largura, max(1, int(faixa.shape[0] * largura / faixa.shape[1]))),
                       interpolation=cv2.INTER_AREA)
    return _com_guias(faixa, 6)


def desenhar(nome: str, nosso: dict, st: dict, destino: Path) -> None:
    """Imagem: em cima a folha com os cortes de cada um; embaixo a(s) pagina(s)
    endireitada(s), com guias; no pe, a faixa do meio ampliada."""
    img = nosso["img"]
    alto = 620
    folha_n, esc = _reduzir(img, alto)
    folha_s = folha_n.copy()
    folha_n = np.ascontiguousarray(folha_n)
    # nosso: linha de divisao (azul) e caixa do corte (verde) de cada pagina
    largura_folha = img.shape[1]
    if nosso["dividir"]:
        x = int(nosso["posicao"] * largura_folha * esc)
        cv2.line(folha_n, (x, 0), (x, alto - 1), AZUL, 3)
    deslocamento = 0
    for p in nosso["paginas"]:
        if p["metade"] == "direita":
            deslocamento = int(round(np.clip(nosso["posicao"], 0.02, 0.98) * largura_folha))
        if p["recorte"] is not None:
            rx, ry, rw, rh = p["recorte"]
            lb = p["largura_base"]
            x0 = int((deslocamento + rx * lb) * esc)
            x1 = int((deslocamento + (rx + rw) * lb) * esc)
            cv2.rectangle(folha_n, (x0, int(ry * alto)), (x1, int((ry + rh) * alto)), VERDE, 2)
    # ScanTailor: linhas de corte (vermelho) e caixa de cada pagina
    for c in st["cortes"]:
        cv2.line(folha_s, (int(c[0] * esc), int(c[1] * esc)), (int(c[2] * esc), int(c[3] * esc)), VERMELHO, 3)
    t_n = "NOSSO: " + (f"divide a {100 * nosso['posicao']:.0f}%" if nosso["dividir"] else "uma pagina")
    t_s = "SCANTAILOR: " + {"duas_paginas": "duas paginas", "uma_pagina_sem_corte": "uma pagina",
                            "uma_pagina_com_sobra": "uma pagina + sobra"}.get(st["tipo"], st["tipo"])
    cima = _lado_a_lado([_titulo(folha_n, t_n, AZUL), _titulo(folha_s, t_s, VERMELHO)], 24)

    def coluna(finais, rotulos):
        partes = []
        for f, r in zip(finais, rotulos):
            red, _ = _reduzir(f if f.ndim == 3 else cv2.cvtColor(f, cv2.COLOR_GRAY2BGR), 560)
            partes.append(_titulo(_com_guias(red), r))
        return _lado_a_lado(partes, 8)

    meio_n = coluna([p["final"] for p in nosso["paginas"]],
                    [f"nosso {p['metade']}: {p['aplicado']:+.2f} graus" for p in nosso["paginas"]])
    meio_s = coluna([s["final"] for s in st["subs"]],
                    [f"ScanTailor {s['nome']}: {s['angulo']:+.2f} graus" for s in st["subs"]])
    meio = _lado_a_lado([meio_n, meio_s], 24)
    largura_pe = max(600, meio.shape[1] // 2 - 12)
    pe_n = _titulo(_faixa_do_meio(nosso["paginas"][0]["final"], largura_pe), "nosso: faixa do meio ampliada")
    pe_s = _titulo(_faixa_do_meio(st["subs"][0]["final"], largura_pe), "ScanTailor: faixa do meio ampliada")
    pe = _lado_a_lado([pe_n, pe_s], 24)
    painel = _empilhar([cima, meio, pe], 18)
    if painel.shape[1] > 2200:
        painel, _ = _reduzir(painel, int(painel.shape[0] * 2200 / painel.shape[1]))
    cv2.imwrite(str(destino), painel, [cv2.IMWRITE_JPEG_QUALITY, 88])


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    IMAGENS.mkdir(parents=True, exist_ok=True)
    lista = json.loads((RAIZ / "gabarito" / "lista.json").read_text(encoding="utf-8"))
    fator, texto_sinal = fator_do_sentido()
    print(texto_sinal)
    resultados = {"sentido": texto_sinal, "fator": fator, "paginas": {}}
    nomes = list(lista["paginas"])
    for nome in nomes:
        info = lista["paginas"][nome]
        print("...", nome, flush=True)
        nosso = nossa_geometria(nome, info)
        st = scantailor(nosso["img"], nome, fator)
        variante = scantailor_no_dpi_do_scan(nome, info, fator)
        largura = nosso["img"].shape[1]
        linha = {
            "nosso_divide": nosso["dividir"], "nosso_posicao": round(100 * nosso["posicao"], 1),
            "nosso_confianca": round(nosso["confianca"], 2), "e_paisagem": nosso["e_paisagem"],
            "nosso_angulos": [round(p["aplicado"], 2) for p in nosso["paginas"]],
            "nosso_angulo_analise": round(nosso["angulo_analise"], 2),
            "nosso_recortes": [None if p["recorte"] is None else [round(v, 4) for v in p["recorte"]]
                               for p in nosso["paginas"]],
            "st_tipo": st["tipo"],
            "st_cortes": [round(100 * 0.5 * (c[0] + c[2]) / largura, 1) for c in st["cortes"]],
            "st_angulos": [round(s["angulo"], 2) for s in st["subs"]],
            "st_brutos": [round(s["bruto"], 2) for s in st["subs"]],
            "st_confiancas": [round(s["confianca"], 2) for s in st["subs"]],
            "st_dpi_do_scan": variante, "dpi_png": info["dpi_png"],
        }
        resultados["paginas"][nome] = linha
        print("   ", json.dumps(linha, ensure_ascii=False), flush=True)
        if nome in COM_IMAGEM:
            desenhar(nome, nosso, st, IMAGENS / f"{nome}.jpg")
        del nosso, st
    (PASTA / "dados" / "medidas.json").parent.mkdir(parents=True, exist_ok=True)
    (PASTA / "dados" / "medidas.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1),
                                                   encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
