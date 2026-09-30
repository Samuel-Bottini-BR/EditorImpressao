"""Roda as TRÊS pontes do programa (docTR, Kraken, Tesseract) nas 22 páginas do 1.3 e guarda o resultado.

Uso (no .venv do programa, a partir da raiz do código):
    .venv\\Scripts\\python.exe relatorios\\fase1-1.3-comparar-ocr-2026-09-29\\scripts\\rodar_pontes.py [motor ...]

    motor: doctr, kraken, tesseract (sem nada, os três).

Grava saida_teste\\ocr-comparar\\<motor>\\<pagina>.json (core.ocr_comum.para_dict),
fora do git. É daí que calibrar.py e tests/test_ocr_comparar.py leem, para não
rodar o Kraken (~4 min nas 22 páginas) a cada vez.

As páginas são as imagens da comparação do 1.3 (saida_teste\\ocr-1.3\\imagens);
o Tesseract usa o idioma de cada livro e o DPI da comparação (como a "T1").
Seguro mudar: nada que mude o resultado; é só um laço sobre as pontes.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

from core.ocr_comum import para_dict  # noqa: E402

IMAGENS = RAIZ / "saida_teste" / "ocr-1.3" / "imagens"
SAIDA = RAIZ / "saida_teste" / "ocr-comparar"
LISTA = RAIZ / "gabarito" / "lista.json"

PAGINAS = [
    "palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010",
    "escola_p007", "horas_p011", "horas_p013", "horas_p047",
    "opusmajus_p011", "opusmajus_p003", "opusmajus_p020", "opusmajus_p165",
    "opusmajus_p256", "horas_p026", "horas_p027", "escola_p035",
    "rhetorica_p018", "siebmacher_p009", "palatino_p057",
    "graduale_p221", "graduale_p222", "graduale_p223",
]
IDIOMA_DO_LIVRO = {
    "palatino": "ita", "escola": "por", "horas": "fra", "opusmajus": "eng",
    "rhetorica": "lat", "siebmacher": "script/Fraktur", "graduale": "lat",
}


def _dpi(pagina: str) -> float:
    lista = json.loads(LISTA.read_text(encoding="utf-8"))
    return min(float(lista["paginas"][pagina]["dpi_scan"]), 300.0)


def _gravar(motor: str, pagina: str, resultado) -> None:
    pasta = SAIDA / motor
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / f"{pagina}.json").write_text(json.dumps(para_dict(resultado)), encoding="utf-8")
    n = "-" if resultado.linhas is None else len(resultado.linhas)
    print(f"{motor:9s} {pagina:16s} {n!s:>4} linhas  perdidas {resultado.perdidas}  "
          f"{resultado.segundos:6.2f} s  {resultado.motivo or ''}", flush=True)


def main(motores: list[str]) -> None:
    if "doctr" in motores:
        from core.ocr_doctr import DetectorDoctr
        with DetectorDoctr() as detector:
            for pagina in PAGINAS:
                _gravar("doctr", pagina, detector.segmentar(IMAGENS / f"{pagina}.png"))
    if "tesseract" in motores:
        from core.ocr_tesseract import MotorTesseract
        motor = MotorTesseract()
        for pagina in PAGINAS:
            _gravar("tesseract", pagina, motor.segmentar(
                IMAGENS / f"{pagina}.png", idioma=IDIOMA_DO_LIVRO[pagina.split("_")[0]], dpi=_dpi(pagina)))
    if "kraken" in motores:
        from core.ocr_kraken import MotorKraken
        inicio = time.perf_counter()
        with MotorKraken() as motor:
            for pagina in PAGINAS:
                _gravar("kraken", pagina, motor.segmentar(IMAGENS / f"{pagina}.png"))
        print(f"kraken: {time.perf_counter() - inicio:.0f} s no total")


if __name__ == "__main__":
    main([a for a in sys.argv[1:]] or ["doctr", "tesseract", "kraken"])
