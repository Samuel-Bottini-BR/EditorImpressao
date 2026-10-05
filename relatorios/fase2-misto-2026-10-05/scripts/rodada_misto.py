"""Antes/depois do modo Misto nas paginas do gabarito (parte B).

Para cada pagina: a pagina preparada pelo programa (Original), o Preto e branco
de hoje (core.filtros.aplicar_filtro_com_selecao, o filtro do programa) e o
Misto (core.misto.aplicar_misto, pelo montar_misto.misto_da_pagina), com a
MESMA imagem e a MESMA marcacao. Nas paginas pedidas pela gerente, tambem as
duas variantes que viram pergunta ao Samuel: papel da gravura creme (o Misto
puro do ScanTailor) e foto em tons de cinza.

Grava em relatorios/fase2-misto-2026-10-05/:
  paineis/<pagina>.jpg            Original | Preto e branco hoje | Misto
  paineis/<pagina>-detalhe.jpg    o mesmo, ampliado no ponto do gabarito
  variantes/<pagina>.jpg          Misto | papel creme | foto em cinza
  mascaras/<pagina>.jpg           onde o Misto deixa a imagem (laranja)
  dados/rodada-misto.json         tempos e o que saiu (1 bit ou nao)

Uso: python rodada_misto.py [pagina,pagina,...]
"""

from __future__ import annotations

import json
import sys
import time

import cv2
import numpy as np

import comum

ROTULOS = ("Original", "Preto e branco hoje", "Misto")


def _bgr(img):
    return img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def _painel(imagens, rotulos, altura=1100):
    partes = []
    for img, rotulo in zip(imagens, rotulos):
        img = _bgr(img)
        f = altura / img.shape[0]
        peq = cv2.resize(img, (max(1, round(img.shape[1] * f)), altura), interpolation=cv2.INTER_AREA)
        faixa = np.full((44, peq.shape[1], 3), 255, np.uint8)
        cv2.putText(faixa, rotulo, (8, 31), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2, cv2.LINE_AA)
        partes.append(np.vstack([faixa, peq]))
        partes.append(np.full((altura + 44, 12, 3), 160, np.uint8))
    return np.hstack(partes[:-1])


def _recorte(img, detalhe):
    a, l = img.shape[:2]
    x0, y0, x1, y1 = detalhe
    return img[int(y0 * a):int(y1 * a), int(x0 * l):int(x1 * l)]


def main() -> None:
    sys.path.insert(0, str(comum.RAIZ))
    from core.filtros import PRETO_E_BRANCO, aplicar_filtro_com_selecao
    from core.misto import aplicar_misto
    from core.selecao import GRAVURA
    from montar_misto import misto_da_pagina

    paginas = sys.argv[1].split(",") if len(sys.argv) > 1 else comum.todas_as_paginas()
    lista = json.loads((comum.GABARITO / "lista.json").read_text(encoding="utf-8"))["paginas"]
    dados: dict = {}
    for pid in paginas:
        doc, projeto = comum.abrir(pid, PRETO_E_BRANCO)
        try:
            for n, pagina in enumerate(projeto.paginas_ativas):
                nome = pid if len(projeto.paginas_ativas) == 1 else f"{pid}-{n + 1}"
                misto, mono_m, prep, sel, s_misto = misto_da_pagina(doc, projeto, pagina)
                inicio = time.perf_counter()
                pb, mono_pb = aplicar_filtro_com_selecao(
                    prep, PRETO_E_BRANCO, sel, pagina.forca_preto, pagina.clareza_melhorar,
                    pagina.intensidade_magico, algoritmo_pb=pagina.algoritmo_preto_branco,
                    despeckle=pagina.despeckle)
                s_pb = time.perf_counter() - inicio
                altura, largura = prep.shape[:2]
                gravura = sel.peso(altura, largura, GRAVURA) if not sel.vazia else np.zeros((altura, largura), np.float32)
                igual = bool(pb.shape == misto.shape and np.array_equal(pb, misto))
                dados[nome] = {"pb_s": round(s_pb, 2), "misto_s": round(s_misto, 2),
                               "pb_1bit": mono_pb, "misto_1bit": mono_m,
                               "gravura_pct": round(100 * float((gravura > 0.5).mean()), 2),
                               "misto_igual_ao_pb": igual}
                print(nome, dados[nome], flush=True)

                comum.gravar_jpg(comum.PASTA / "paineis" / f"{nome}.jpg",
                                 _painel([prep, pb, misto], ROTULOS), lado=3000, qualidade=85)
                detalhe = lista.get(pid, {}).get("detalhe")
                if detalhe:
                    comum.gravar_jpg(comum.PASTA / "paineis" / f"{nome}-detalhe.jpg",
                                     _painel([_recorte(x, detalhe) for x in (prep, pb, misto)],
                                             ROTULOS, altura=900), lado=3000, qualidade=88)
                vista = _bgr(prep).copy()
                laranja = np.zeros_like(vista)
                laranja[:] = (0, 140, 255)
                peso = np.clip(gravura, 0, 1)[:, :, None] * 0.45
                vista = (vista * (1 - peso) + laranja * peso).astype(np.uint8)
                comum.gravar_jpg(comum.PASTA / "mascaras" / f"{nome}.jpg", vista, lado=1400)

                if pid in comum.OBRIGATORIAS and (gravura > 0).any():
                    creme, _ = aplicar_misto(prep, sel, pagina.forca_preto, pagina.algoritmo_preto_branco,
                                             pagina.despeckle, papel_da_gravura_branco=False)
                    cinza, _ = aplicar_misto(prep, sel, pagina.forca_preto, pagina.algoritmo_preto_branco,
                                             pagina.despeckle, foto_em_cinza=True)
                    rot = ("Misto (de fabrica)", "Variante: papel da gravura creme",
                           "Variante: foto em cinza")
                    comum.gravar_jpg(comum.PASTA / "variantes" / f"{nome}.jpg",
                                     _painel([misto, creme, cinza], rot), lado=3000, qualidade=85)
                    if detalhe:
                        comum.gravar_jpg(comum.PASTA / "variantes" / f"{nome}-detalhe.jpg",
                                         _painel([_recorte(x, detalhe) for x in (misto, creme, cinza)],
                                                 rot, altura=900), lado=3000, qualidade=88)
                    del creme, cinza
                del misto, prep, pb
        finally:
            doc.close()
    destino = comum.PASTA / "dados" / "rodada-misto.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    antigo = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    antigo.update(dados)
    destino.write_text(json.dumps(antigo, indent=1), encoding="utf-8")
    print("gravado", destino)


if __name__ == "__main__":
    main()
