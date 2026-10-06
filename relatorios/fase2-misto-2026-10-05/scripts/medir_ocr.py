"""Quanta tinta de verdade cai FORA das linhas dos OCRs (parte A, item 6 do plano do Misto).

A ideia do Internet Archive (archive-pdf-tools, mrc.py): o preto e branco so
dentro das linhas de texto que o OCR achou; mancha fora das linhas nunca vira
tinta. O Samuel exige que letra que o OCR nao enxerga (capitular, notas do
Graduale, letrinhas dos diagramas do Opus 165) nao fique sem tratamento. Aqui
so se MEDE, sem mudar nada no programa:

  - a pagina e a preparada pelo programa (a mesma que o Misto recebe:
    comum.imagem_preparada), na resolucao do PDF final;
  - "tinta" = os pontos pretos do Preto e branco de hoje da pagina inteira
    (core.filtros.filtro_preto_e_branco, com os ajustes de fabrica);
  - as linhas: docTR e Kraken (as pontes do 1.3), e o texto combinado por voto
    (core.ocr_comparar.comparar, o que o item 1.4 usaria) e a uniao dos dois;
    com e sem uma folga de 0,35 altura de linha em volta (a TOLERANCIA da
    comparacao);
  - a tinta fora das linhas e separada em "dentro da gravura" (o Misto deixa
    como no original de qualquer jeito) e "fora da gravura" (a que ficaria SEM
    TRATAMENTO num Misto so pelas linhas: e esta que importa).

Imagem de cada pagina (ocr/<pagina>.jpg): papel claro; tinta dentro das
linhas em cinza escuro; tinta fora das linhas e fora da gravura em VERMELHO;
tinta fora das linhas mas dentro da gravura em AZUL; contorno das linhas
(uniao) em verde; contorno da gravura em laranja. Mais um recorte ampliado no
ponto do gabarito (o campo "detalhe" da lista).

Uso: python medir_ocr.py [pagina,pagina,...]
"""

from __future__ import annotations

import json
import sys
import time

import cv2
import numpy as np

import comum

# o motor do Kraken fica fora do git; numa worktree a procura automatica
# (core.ocr_kraken.lugares_do_motor) nao o acha, entao vai o caminho direto
MOTOR = r"D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken"


def _desenhar(linhas, altura, largura) -> np.ndarray:
    tela = np.zeros((altura, largura), np.uint8)
    for linha in linhas:
        pontos = np.round(np.asarray(linha.poligono, np.float64)).astype(np.int32)
        if len(pontos) >= 3:
            cv2.fillPoly(tela, [pontos], 255)
    return tela > 0


def _folga(mascara: np.ndarray, raio: int) -> np.ndarray:
    if raio < 1:
        return mascara
    nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1))
    return cv2.dilate(mascara.astype(np.uint8), nucleo) > 0


def _pct(parte: int, todo: int) -> float:
    return round(100.0 * parte / todo, 2) if todo else 0.0


def main() -> None:
    from core.filtros import filtro_preto_e_branco, PRETO_E_BRANCO
    from core.ocr_comparar import comparar
    from core.ocr_doctr import DetectorDoctr
    from core.ocr_kraken import MotorKraken
    from core.selecao import GRAVURA

    paginas = sys.argv[1].split(",") if len(sys.argv) > 1 else comum.OBRIGATORIAS
    lista = json.loads((comum.GABARITO / "lista.json").read_text(encoding="utf-8"))["paginas"]
    pasta = comum.PASTA / "ocr"
    pasta.mkdir(parents=True, exist_ok=True)
    dados: dict = {}
    with DetectorDoctr() as doctr, MotorKraken(MOTOR) as kraken:
        for pid in paginas:
            doc, projeto = comum.abrir(pid, PRETO_E_BRANCO)
            try:
                img, sel = comum.imagem_preparada(doc, projeto, projeto.paginas[0])
            finally:
                doc.close()
            altura, largura = img.shape[:2]
            tinta = filtro_preto_e_branco(img) == 0
            gravura = sel.peso(altura, largura, GRAVURA) > 0.5

            t0 = time.perf_counter()
            r_d = doctr.segmentar(img)
            t_d = time.perf_counter() - t0
            t0 = time.perf_counter()
            r_k = kraken.segmentar(img)
            t_k = time.perf_counter() - t0
            comp = comparar([r for r in (r_d, r_k) if r.disponivel])
            altura_linha = float(comp.medidas.get("altura_linha", 0.0) or 0.0)
            raio = int(round(0.35 * altura_linha))

            voto = comp.mascara if comp.mascara is not None else np.zeros((altura, largura), bool)
            if voto.shape != (altura, largura):
                voto = cv2.resize(voto.astype(np.uint8), (largura, altura),
                                  interpolation=cv2.INTER_NEAREST) > 0
            uniao = np.zeros((altura, largura), bool)
            for r in (r_d, r_k):
                if r.disponivel:
                    uniao |= _desenhar(r.linhas, altura, largura)

            total = int(tinta.sum())
            medida = {"tamanho": [largura, altura], "tinta_pontos": total,
                      "tinta_na_gravura_pct": _pct(int((tinta & gravura).sum()), total),
                      "doctr_s": round(t_d, 2), "kraken_s": round(t_k, 2),
                      "linhas": {"doctr": len(r_d.linhas or []), "kraken": len(r_k.linhas or [])},
                      "kraken_perdidas": r_k.perdidas, "altura_linha": round(altura_linha, 1),
                      "motivos_revisar": comp.motivos}
            for nome, mascara in (("voto", voto), ("uniao", uniao)):
                for com_folga in (False, True):
                    m = _folga(mascara, raio) if com_folga else mascara
                    fora = tinta & ~m
                    chave = nome + ("_com_folga" if com_folga else "")
                    medida[chave] = {
                        "fora_das_linhas_pct": _pct(int(fora.sum()), total),
                        "fora_e_fora_da_gravura_pct": _pct(int((fora & ~gravura).sum()), total),
                        "fora_mas_na_gravura_pct": _pct(int((fora & gravura).sum()), total),
                    }
            dados[pid] = medida
            print(pid, medida["voto_com_folga"], medida["uniao_com_folga"],
                  f"docTR {t_d:.1f}s Kraken {t_k:.1f}s", flush=True)

            # a imagem: o que vira tinta e onde ficaria sem tratamento
            m = _folga(uniao, raio)
            fora = tinta & ~m
            claro = (img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)).astype(np.float32)
            vista = (255 - (255 - claro) * 0.25).astype(np.uint8)
            vista[tinta & m] = (70, 70, 70)
            vista[fora & gravura] = (230, 120, 0)
            vista[fora & ~gravura] = (0, 0, 230)
            espessura = max(2, round(max(altura, largura) / 1000))
            for mascara, cor in ((uniao, (0, 170, 0)), (gravura, (0, 140, 255))):
                contornos, _h = cv2.findContours(mascara.astype(np.uint8), cv2.RETR_EXTERNAL,
                                                 cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(vista, contornos, -1, cor, espessura)
            comum.gravar_jpg(pasta / f"{pid}.jpg", vista, lado=1800)
            detalhe = lista.get(pid, {}).get("detalhe")
            if detalhe:
                x0, y0, x1, y1 = detalhe
                recorte = vista[int(y0 * altura):int(y1 * altura), int(x0 * largura):int(x1 * largura)]
                if recorte.size:
                    comum.gravar_jpg(pasta / f"{pid}-detalhe.jpg", recorte, lado=1400)
            del img, tinta, gravura, vista
    # rodar so algumas paginas acrescenta ao que ja estava medido
    arquivo = pasta / "medidas-ocr.json"
    antigo = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else {}
    antigo.update(dados)
    arquivo.write_text(json.dumps(antigo, indent=1, ensure_ascii=False), encoding="utf-8")
    print("gravado", pasta / "medidas-ocr.json")


if __name__ == "__main__":
    main()
