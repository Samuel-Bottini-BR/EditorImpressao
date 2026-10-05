"""Prova de que o caminho de hoje (sem Misto) não muda nem fica mais lento.

Desenha cada página do gabarito, pelo renderizar_pagina do programa na
resolução do PDF final, nos filtros Preto e branco, Melhorar e Mágico pro, e
grava a soma sha256 de cada imagem e o tempo. Rodado antes e depois das
mudanças do Misto, na mesma condição; o comparar.py diz se as imagens são
idênticas e quanto o tempo variou.

Uso: python caminho_atual.py <rotulo>   (grava caminho-atual-<rotulo>.json)
"""

from __future__ import annotations

import json
import sys
import time

import comum


def main() -> None:
    rotulo = sys.argv[1]
    from core.filtros import MAGICO_PRO, MELHORAR, PRETO_E_BRANCO
    from core.pipeline import renderizar_pagina

    resultado: dict = {}
    for pid in comum.todas_as_paginas():
        doc, projeto = comum.abrir(pid, PRETO_E_BRANCO)
        try:
            # a deteccao (a mesma nos tres filtros) fica fora do tempo do filtro
            inicio = time.perf_counter()
            comum.imagem_preparada(doc, projeto, projeto.paginas[0])
            deteccao = time.perf_counter() - inicio
            resultado[pid] = {"deteccao_s": round(deteccao, 3)}
            for filtro in (PRETO_E_BRANCO, MELHORAR, MAGICO_PRO):
                somas, tempo = [], 0.0
                for pagina in projeto.paginas:
                    pagina.filtro = filtro
                    inicio = time.perf_counter()
                    img, mono = renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
                    tempo += time.perf_counter() - inicio
                    somas.append(comum.soma(img) + ("-1bit" if mono else ""))
                resultado[pid][filtro] = {"somas": somas, "s": round(tempo, 3)}
            print(pid, {f: v["s"] for f, v in resultado[pid].items() if isinstance(v, dict)}, flush=True)
        finally:
            doc.close()
    destino = comum.PASTA / "dados" / f"caminho-atual-{rotulo}.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(resultado, indent=1), encoding="utf-8")
    print("gravado", destino)


if __name__ == "__main__":
    main()
