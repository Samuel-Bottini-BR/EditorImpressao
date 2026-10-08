"""RODADA 4 (07/10/2026): roda com o fase-1 de hoje (conserto do desenho claro,
limpar pontinhos desligado de fabrica). Mudou da rodada 3: os jeitos rodados sao
"Guardar a tinta forte" (rede, de fabrica) e "Guardar tudo" (tudo); o "So o texto
achado" nao entra. Sem argumento: as 89 paginas (comum.as_89).

COPIA do rodar.py do estudo revisar-criterios-2026-10-06 (rodada 1 das decisoes).
Mudou: imagens com lado 4000 e qualidade 94 (para ampliar recortes) e sem o
jeito "Tudo em preto e branco" (nao entra nas perguntas).

Roda o Misto como o programa roda, uma pagina por vez, e guarda o que for
preciso para medir os sinais depois (medir.py) sem rodar o leitor de novo.

Para cada pagina (e cada metade, se a folha e dividida):
  - a pagina preparada e a marcacao (gravura/letra) como o programa acha;
  - o Preto e branco de hoje (sem "So as letras");
  - o Misto nos tres jeitos, pelo core.pipeline.renderizar_pagina:
      rede   = "Guardar a tinta forte" (de fabrica)
      tudo   = "Tudo em preto e branco"
      apagar = "So o texto achado"
    com a medida de dentro (forte_fora etc.) e se o aviso foi posto;
  - as linhas do leitor de texto (as mesmas que o Misto usou), a mascara da
    imagem (gravura) e o preto e branco de base do Misto.

Uso: python rodar.py [pid,pid,...]   (sem argumento: todas; pula as feitas)
Grava em <TRABALHO>/dados/<pid>__<metade>.{npz,json} e os jpg de olhar.
"""

from __future__ import annotations

import gc
import json
import sys
import time
import traceback

import cv2
import numpy as np

import comum

LADO_JPG = 4000


def main() -> None:
    from core import analise, linhas_do_texto, misto
    from core import filtros as F
    from core import pipeline as P
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    pids = sys.argv[1].split(",") if len(sys.argv) > 1 else comum.as_89()
    comum.DADOS.mkdir(parents=True, exist_ok=True)

    vistas: list[dict] = []
    original_misto = misto.aplicar_misto

    def espiao(*args, **kwargs):
        resultado = original_misto(*args, **kwargs)
        vistas.append({"medidas": dict(kwargs.get("medidas") or {}),
                       "linhas": kwargs.get("linhas"),
                       "altura_linha": kwargs.get("altura_linha", 0.0),
                       "fora_do_texto": kwargs.get("fora_do_texto")})
        return resultado

    P.misto.aplicar_misto = espiao

    for pid in pids:
        feito = list(comum.DADOS.glob(f"{pid}__*.json"))
        if feito:
            print("ja feito", pid, flush=True)
            continue
        t0 = time.perf_counter()
        try:
            doc, projeto = comum.abrir(pid, PRETO_E_BRANCO)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            continue
        try:
            for pagina in projeto.paginas:
                alertas_da_analise = list(pagina.alertas)
                # a pagina preparada e a marcacao (a deteccao roda aqui)
                pagina.filtro = ORIGINAL
                img, _m = P.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
                pagina.filtro = PRETO_E_BRANCO
                sel = pagina.obter_selecao()
                alt, larg = img.shape[:2]

                # o Preto e branco de hoje
                projeto.misto_so_as_letras = False
                pb, _m = P.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)

                saidas, info_modos = {}, {}
                linhas_mask, altura_linha = None, 0.0
                for modo in (misto.FORA_REDE, misto.FORA_TUDO):
                    projeto.misto_so_as_letras = True
                    projeto.misto_fora_do_texto = modo
                    vistas.clear()
                    out, mono = P.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
                    visto = vistas[-1] if vistas else {}
                    if visto.get("linhas") is not None:
                        linhas_mask = visto["linhas"]
                        altura_linha = float(visto["altura_linha"])
                    info_modos[modo] = {
                        "medidas": {k: (round(v, 5) if isinstance(v, float) else v)
                                    for k, v in visto.get("medidas", {}).items()},
                        "para_revisar": analise.TINTA_FORTE_FORA_DO_TEXTO in pagina.alertas,
                        "alertas": list(pagina.alertas),
                        "um_bit": bool(mono),
                    }
                    saidas[modo] = out
                projeto.misto_so_as_letras = False

                # as linhas, uma a uma (as mesmas guardadas: nao roda o leitor de novo)
                resultados = linhas_do_texto.linhas_da_pagina(img, P._chave_das_linhas(projeto, pagina))
                poligonos = []
                for r in resultados:
                    fx = larg / r.largura if r.largura else 1.0
                    fy = alt / r.altura if r.altura else 1.0
                    for linha in r.linhas:
                        pts = np.asarray(linha.poligono, np.float64) * (fx, fy)
                        if len(pts) >= 3 and np.isfinite(pts).all():
                            poligonos.append(np.round(pts).astype(int).tolist())
                if linhas_mask is None:
                    linhas_mask, altura_linha = misto.mascara_das_linhas(resultados, img.shape)

                binaria = F.filtro_preto_e_branco(img, forca=pagina.forca_preto,
                                                  algoritmo=pagina.algoritmo_preto_branco,
                                                  despeckle=P.pontinhos_da_pagina(
                                                      projeto, pagina, img, dpi=projeto.qualidade_dpi))
                cinza = F._cinza_para_binarizar(img)
                imagem = misto._peso_da_imagem(sel, alt, larg) > 0

                def tinta(x):
                    g = x if x.ndim == 2 else cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)
                    return g < 128

                base = f"{pid}__{pagina.metade}"
                np.savez_compressed(
                    comum.DADOS / f"{base}.npz",
                    cinza=cinza, base_tinta=binaria == 0, linhas=linhas_mask, imagem=imagem,
                    a_tinta=tinta(saidas[misto.FORA_REDE]), t_tinta=tinta(saidas[misto.FORA_TUDO]),
                    pb_tinta=tinta(pb))
                for nome, x in (("original", img), ("pb", pb), ("a", saidas[misto.FORA_REDE]),
                                ("t", saidas[misto.FORA_TUDO])):
                    comum.gravar_jpg(comum.DADOS / f"{base}__{nome}.jpg", x, lado=LADO_JPG, qualidade=94)
                regioes = [{"tipo": r.tipo, "origem": r.origem, "operacao": r.operacao}
                           for r in (sel.regioes if sel is not None else [])]
                dados = {
                    "pid": pid, "metade": pagina.metade, "tamanho": [larg, alt],
                    "altura_linha": altura_linha, "n_linhas": len(poligonos),
                    "poligonos": poligonos, "modos": info_modos,
                    "alertas_da_analise": alertas_da_analise,
                    "em_duvida": bool(getattr(sel, "em_duvida", False)),
                    "regioes": regioes,
                    "segundos": round(time.perf_counter() - t0, 1),
                }
                (comum.DADOS / f"{base}.json").write_text(json.dumps(dados, ensure_ascii=False),
                                                         encoding="utf-8")
                print(base, "linhas", len(poligonos),
                      {m: (round(i["medidas"].get("forte_fora", -1), 3), i["para_revisar"])
                       for m, i in info_modos.items()},
                      f"{time.perf_counter() - t0:.1f}s", flush=True)
                del img, pb, saidas, binaria, cinza, imagem, linhas_mask
                gc.collect()
        except Exception:  # noqa: BLE001
            traceback.print_exc()
        finally:
            doc.close()
            del projeto
            gc.collect()


if __name__ == "__main__":
    main()
