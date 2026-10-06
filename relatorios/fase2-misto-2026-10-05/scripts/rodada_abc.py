"""Parte C: as opcoes A, B e C do Misto lado a lado (conferencia 8, 05/10/2026).

Pedido do Samuel (05/10): "Quero ver o lado a lado antes de decidir: A, B e
C, com o detector de gravura ligado, no Graduale 222, Palatino 9, Opus 165,
Boecio 22 e Marial 7. Inclua tambem uma pagina com iluminura (Horas 11) e uma
com moldura dourada (Horas 13)." Todas estao no gabarito (copias de uma pagina,
somente leitura).

Para cada pagina, pelo caminho do programa (comum.imagem_preparada, 300 DPI,
detector de gravura do 1.2 ligado como de fabrica): o docTR (fast_base) e o
Kraken acham as linhas (core.misto.mascara_das_linhas) e o Misto sai nas tres
opcoes (core.misto: FORA_REDE = A, FORA_TUDO = B, FORA_APAGAR = C). Grava em
relatorios/conferencia-8-2026-10-05/:
  <pagina>.jpg            Original | A | B | C (pagina inteira, reduzida)
  <pagina>-detalhe-N.jpg  o mesmo, recortado no ponto que importa, na
                          resolucao de impressao (ampliado quando pequeno)
  dados.json              tempos (leitores e cada opcao) e a medida de
                          "tinta forte fora das linhas"
Uso: python rodada_abc.py [pagina,...]
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

import comum

MOTOR = r"D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken"
DESTINO = comum.RAIZ / "relatorios" / "conferencia-8-2026-10-05"
PAGINAS = ["graduale_p222", "palatino_p009", "opusmajus_p165", "boecio_p022",
           "marial_p007", "horas_p011", "horas_p013"]
# recortes (x0, y0, x1, y1) em fracao da PAGINA PREPARADA, e o que mostram
RECORTES = {
    "graduale_p222": [((0.02, 0.0, 0.62, 0.20), "notas e pautas (alto da página)"),
                      ((0.55, 0.40, 1.0, 0.62), "notas e pautas (meio da página)")],
    "palatino_p009": [((0.08, 0.26, 0.47, 0.53), "a capitular Q e as hachuras dela")],
    "opusmajus_p165": [((0.70, 0.30, 1.0, 0.63), "figura 7 e as letrinhas"),
                       ((0.70, 0.71, 1.0, 0.97), "figura 8 e as letrinhas")],
    "boecio_p022": [((0.50, 0.05, 1.0, 0.62), "a escrita do verso na margem direita")],
    "marial_p007": [((0.55, 0.30, 1.0, 0.80), "a escrita do verso na margem direita")],
    "horas_p011": [((0.03, 0.55, 0.50, 0.97), "a iluminura (anjo, flores, fundo)")],
    "horas_p013": [((0.50, 0.65, 0.90, 0.92), "a moldura dourada e o 'pag. 54'")],
}
ROTULOS = ("Original", "A - guardar a tinta forte", "B - tudo em preto e branco",
           "C - só o texto achado")


def _bgr(img):
    return img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def _painel(imagens, altura):
    partes = []
    for img, rotulo in zip(imagens, ROTULOS):
        img = _bgr(img)
        f = altura / img.shape[0]
        interp = cv2.INTER_AREA if f < 1 else cv2.INTER_NEAREST
        peq = cv2.resize(img, (max(1, round(img.shape[1] * f)), altura), interpolation=interp)
        faixa = np.full((46, peq.shape[1], 3), 255, np.uint8)
        cv2.putText(faixa, rotulo.replace("ó", "o"), (8, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 0, 0), 2, cv2.LINE_AA)
        partes += [np.vstack([faixa, peq]), np.full((altura + 46, 14, 3), 150, np.uint8)]
    return np.hstack(partes[:-1])


def main() -> None:
    sys.path.insert(0, str(comum.RAIZ))
    from core.filtros import PRETO_E_BRANCO
    from core.misto import FORA_APAGAR, FORA_REDE, FORA_TUDO, aplicar_misto, mascara_das_linhas
    from core.ocr_doctr import DetectorDoctr
    from core.ocr_kraken import MotorKraken
    from core.selecao import GRAVURA

    paginas = sys.argv[1].split(",") if len(sys.argv) > 1 else PAGINAS
    DESTINO.mkdir(parents=True, exist_ok=True)
    arquivo = DESTINO / "dados.json"
    dados = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else {}
    with DetectorDoctr() as doctr, MotorKraken(MOTOR) as kraken:
        for pid in paginas:
            doc, projeto = comum.abrir(pid, PRETO_E_BRANCO)
            try:
                pagina = projeto.paginas[0]
                inicio = time.perf_counter()
                img, sel = comum.imagem_preparada(doc, projeto, pagina)
                s_prep = time.perf_counter() - inicio
            finally:
                doc.close()
            t0 = time.perf_counter()
            r_d = doctr.segmentar(img)
            s_d = time.perf_counter() - t0
            t0 = time.perf_counter()
            r_k = kraken.segmentar(img)
            s_k = time.perf_counter() - t0
            t0 = time.perf_counter()
            linhas, altura_linha = mascara_das_linhas([r_d, r_k], img.shape)
            s_l = time.perf_counter() - t0
            saidas, tempos, medidas = {}, {}, {}
            for nome, modo in (("A", FORA_REDE), ("B", FORA_TUDO), ("C", FORA_APAGAR)):
                m: dict = {}
                t0 = time.perf_counter()
                saidas[nome], _mono = aplicar_misto(
                    img, sel, pagina.forca_preto, pagina.algoritmo_preto_branco, pagina.despeckle,
                    fora_do_texto=modo, linhas=linhas, altura_linha=altura_linha, medidas=m)
                tempos[nome] = round(time.perf_counter() - t0, 2)
                medidas[nome] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}
            a, l = img.shape[:2]
            gravura = sel.peso(a, l, GRAVURA) > 0.5 if not sel.vazia else np.zeros((a, l), bool)
            dados[pid] = {
                "tamanho": [l, a], "gravura_pct": round(100 * float(gravura.mean()), 1),
                "preparar_s": round(s_prep, 1), "doctr_s": round(s_d, 1), "kraken_s": round(s_k, 1),
                "linhas_s": round(s_l, 2), "linhas": {"doctr": len(r_d.linhas or []),
                                                      "kraken": len(r_k.linhas or [])},
                "kraken_disponivel": r_k.disponivel, "opcao_s": tempos, "medidas": medidas,
                "a_igual_b": bool(np.array_equal(saidas["A"], saidas["B"])),
            }
            print(pid, json.dumps(dados[pid], ensure_ascii=False), flush=True)
            imagens = [img, saidas["A"], saidas["B"], saidas["C"]]
            comum.gravar_jpg(DESTINO / f"{pid}.jpg", _painel(imagens, 1150), lado=4200, qualidade=82)
            for n, ((x0, y0, x1, y1), _texto) in enumerate(RECORTES.get(pid, []), start=1):
                cortes = [x[int(y0 * a):int(y1 * a), int(x0 * l):int(x1 * l)] for x in imagens]
                altura = max(500, min(900, cortes[0].shape[0] * 2))
                comum.gravar_jpg(DESTINO / f"{pid}-detalhe-{n}.jpg", _painel(cortes, altura),
                                 lado=4200, qualidade=85)
            del img, saidas, imagens
            arquivo.write_text(json.dumps(dados, indent=1, ensure_ascii=False), encoding="utf-8")
    print("gravado", arquivo)


if __name__ == "__main__":
    main()
