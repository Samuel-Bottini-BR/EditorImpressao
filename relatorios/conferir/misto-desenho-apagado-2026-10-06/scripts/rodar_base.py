"""Roda cada pagina do estudo pelo caminho do programa e guarda o que e preciso
para comparar o Misto de hoje com o consertado SEM rodar o leitor de texto
de novo (06/10/2026, tarefa "Misto: desenho claro apagado").

Baseado em relatorios/revisar-criterios-2026-10-06/scripts/rodar.py (o
estudo, que nao foi mudado). Para cada pagina (e metade):
  - a pagina preparada (img) e a marcacao (selecao), como o programa acha;
  - o Preto e branco puro (sem "So as letras");
  - o Misto no jeito de fabrica ("Guardar a tinta forte"), pelo
    core.pipeline.renderizar_pagina, com o codigo DESTA worktree no momento
    em que o script roda (rode antes do conserto: e o "Misto de hoje");
  - as linhas do leitor (as mesmas que o Misto usou), a altura delas, a
    mascara da imagem (gravura) e o preto e branco de base do Misto.

Uso: python rodar_base.py [pid,pid,...]   (sem argumento: as 59; pula as feitas)
Grava em <TRABALHO>/base/<pid>__<metade>.npz (+ .json)
"""

from __future__ import annotations

import gc
import json
import sys
import time
import traceback

import numpy as np

import comum

BASE = comum.TRABALHO / "base"


def main() -> None:
    from core import filtros as F
    from core import misto
    from core import pipeline as P
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    pids = sys.argv[1].split(",") if len(sys.argv) > 1 else comum.todas()
    BASE.mkdir(parents=True, exist_ok=True)

    vistas: list[dict] = []
    original_misto = misto.aplicar_misto

    def espiao(*args, **kwargs):
        t0 = time.perf_counter()
        resultado = original_misto(*args, **kwargs)
        vistas.append({"linhas": kwargs.get("linhas"),
                       "altura_linha": kwargs.get("altura_linha", 0.0),
                       "medidas": dict(kwargs.get("medidas") or {}),
                       "segundos": time.perf_counter() - t0})
        return resultado

    P.misto.aplicar_misto = espiao

    for pid in pids:
        if list(BASE.glob(f"{pid}__*.json")):
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
                pagina.filtro = ORIGINAL
                img, _m = P.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
                pagina.filtro = PRETO_E_BRANCO
                sel = pagina.obter_selecao()
                alt, larg = img.shape[:2]

                projeto.misto_so_as_letras = False
                pb, _m = P.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)

                projeto.misto_so_as_letras = True
                projeto.misto_fora_do_texto = misto.FORA_REDE
                vistas.clear()
                a, mono_a = P.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
                visto = vistas[-1] if vistas else {}
                projeto.misto_so_as_letras = False
                linhas = visto.get("linhas")
                altura_linha = float(visto.get("altura_linha") or 0.0)

                binaria = F.filtro_preto_e_branco(img, forca=pagina.forca_preto,
                                                  algoritmo=pagina.algoritmo_preto_branco,
                                                  despeckle=pagina.despeckle)
                imagem = misto._peso_da_imagem(sel, alt, larg) > 0 if sel is not None \
                    else np.zeros((alt, larg), bool)
                base = f"{pid}__{pagina.metade}"
                np.savez_compressed(
                    BASE / f"{base}.npz", img=img, pb=pb, a=a, binaria=binaria,
                    cinza=F._cinza_para_binarizar(img),
                    linhas=linhas if linhas is not None else np.zeros((alt, larg), bool),
                    imagem=imagem)
                # a marcacao, para rodar o aplicar_misto de novo sem o detector
                import pickle

                (BASE / f"{base}.sel.pkl").write_bytes(pickle.dumps(sel))
                dados = {"pid": pid, "metade": pagina.metade, "tamanho": [larg, alt],
                         "altura_linha": altura_linha, "tem_linhas": linhas is not None,
                         "medidas_a": {k: v for k, v in visto.get("medidas", {}).items()},
                         "segundos_misto_a": round(visto.get("segundos", -1), 3),
                         "um_bit_a": bool(mono_a),
                         "opcoes": {"forca_preto": pagina.forca_preto,
                                    "algoritmo": pagina.algoritmo_preto_branco,
                                    "despeckle": pagina.despeckle,
                                    "clareza": pagina.clareza_melhorar,
                                    "intensidade": pagina.intensidade_magico}}
                (BASE / f"{base}.json").write_text(json.dumps(dados, ensure_ascii=False),
                                                   encoding="utf-8")
                print(base, "linhas", linhas is not None, round(altura_linha, 1),
                      f"misto {visto.get('segundos', -1):.2f}s",
                      f"total {time.perf_counter() - t0:.1f}s", flush=True)
                del img, pb, a, binaria, imagem, linhas
                gc.collect()
        except Exception:  # noqa: BLE001
            traceback.print_exc()
        finally:
            doc.close()
            del projeto
            gc.collect()


if __name__ == "__main__":
    main()
