"""Confere, sem abrir janela, se os três detectores de texto funcionam neste programa (item 1.3).

PARA QUE SERVE
    O programa empacotado (dist\\EditorImpressao\\ ou o instalado) leva o
    docTR dentro dele, o Tesseract em {app}\\tesseract\\ e o motor do Kraken em
    {app}\\motor-kraken\\. Esta conferência roda os três numa imagem e grava o
    resultado num arquivo JSON: prova que cada ponte ACHOU o seu motor ou
    modelo no programa empacotado, e não só no código.

    Chamada pelo main.py, antes de subir a janela:
        EditorImpressao.exe --conferir-ocr <imagem> <saida.json> [idioma] [dpi]
    (o .exe empacotado é "sem console": não escreve na tela, por isso a saída
    vai para o arquivo). O código de saída é 0 se os três leram a imagem,
    1 se algum falhou, 2 se os argumentos estão errados.

    No código:
        .venv\\Scripts\\python.exe main.py --conferir-ocr pagina.png saida.json

    Não é usada pelo Kaique. Não abre janela, não mexe em projeto, não grava
    nada além do arquivo de saída.

O QUE É SEGURO MUDAR
    O que vai no JSON (é só para quem confere).
O QUE É ARRISCADO MUDAR
    O nome "--conferir-ocr" (o empacotar.py e o relatório de 29/09 o usam).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path


def conferir(imagem: Path, idioma: str = "lat", dpi: float | None = None) -> dict:
    """Roda docTR, Tesseract e Kraken em UMA imagem e diz onde cada um achou o seu motor."""
    from core import ocr_doctr, ocr_kraken, ocr_tesseract
    from core.ocr_comparar import comparar

    saida: dict = {"empacotado": bool(getattr(sys, "frozen", False)),
                   "executavel": sys.executable, "imagem": str(imagem), "ocrs": {}}
    resultados = []

    def anotar(nome: str, resultado, onde: dict, inicio: float) -> None:
        resultados.append(resultado)
        saida["ocrs"][nome] = {
            "disponivel": resultado.disponivel, "motivo": resultado.motivo,
            "detalhe_tecnico": resultado.detalhe_tecnico,
            "linhas": None if resultado.linhas is None else len(resultado.linhas),
            "palavras": None if resultado.palavras is None else len(resultado.palavras),
            "perdidas": resultado.perdidas, "segundos_na_pagina": round(resultado.segundos, 2),
            "segundos_com_abrir": round(time.perf_counter() - inicio, 2), **onde}

    inicio = time.perf_counter()
    with ocr_doctr.DetectorDoctr() as detector:
        r = detector.segmentar(imagem)
        anotar("doctr", r, {"modelo": str(detector.caminho_modelo),
                            "modelo_existe": detector.caminho_modelo.is_file(),
                            "onnxtr": detector.info.get("onnxtr")}, inicio)

    inicio = time.perf_counter()
    motor = ocr_tesseract.MotorTesseract()
    r = motor.segmentar(imagem, idioma=idioma, dpi=dpi)
    exe = ocr_tesseract.achar_tesseract()
    anotar("tesseract", r, {"executavel": None if exe is None else str(exe), "versao": motor.versao(),
                            "tessdata": str(motor.pasta_dos_modelos),
                            "idiomas_na_tessdata": sorted(
                                p.relative_to(motor.pasta_dos_modelos).with_suffix("").as_posix()
                                for p in motor.pasta_dos_modelos.rglob("*.traineddata"))
                            if motor.pasta_dos_modelos.is_dir() else []}, inicio)

    inicio = time.perf_counter()
    with ocr_kraken.MotorKraken() as kraken:
        r = kraken.segmentar(imagem)
        pasta = ocr_kraken.achar_pasta_do_motor()
        anotar("kraken", r, {"motor": None if pasta is None else str(pasta),
                             "abrir_segundos": round(kraken.segundos_para_abrir, 1),
                             "kraken": kraken.info.get("kraken"), "python": kraken.info.get("python")},
               inicio)
        diagnostico = kraken.diagnostico() if r.disponivel else None
        if diagnostico:
            dlls = diagnostico.get("dlls_da_microsoft") or []
            saida["ocrs"]["kraken"]["dlls_do_visual_c"] = dlls
            # O Visual C++ tem de vir do motor ou do System32 (o vc_redist
            # oficial); de outro lugar (ex.: _internal do programa) é defeito.
            import os

            sistema = os.path.normcase(os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32"))
            motor = os.path.normcase(str(pasta)) if pasta else ""
            saida["ocrs"]["kraken"]["dlls_de_lugar_errado"] = [
                d for d in dlls if os.path.normcase(os.path.dirname(d)) != sistema
                and not (motor and os.path.normcase(d).startswith(motor))]

    c = comparar(resultados)
    saida["comparacao"] = {"para_revisar": c.para_revisar, "motivos": c.motivos,
                           "motores": list(c.motores)}
    saida["todos_leram"] = all(v["disponivel"] for v in saida["ocrs"].values())
    return saida


def linha_de_comando(argumentos: list[str]) -> int:
    """--conferir-ocr <imagem> <saida.json> [idioma] [dpi]. Devolve o código de saída."""
    if len(argumentos) < 2:
        return 2
    imagem, arquivo = Path(argumentos[0]), Path(argumentos[1])
    idioma = argumentos[2] if len(argumentos) > 2 else "lat"
    try:
        dpi = float(argumentos[3]) if len(argumentos) > 3 else None
    except ValueError:
        return 2
    try:
        saida = conferir(imagem, idioma, dpi)
        codigo = 0 if saida["todos_leram"] else 1
    except Exception as erro:   # nada sai daqui como exceção: vai para o arquivo
        import traceback
        saida, codigo = {"erro": f"{type(erro).__name__}: {erro}", "rastro": traceback.format_exc()}, 1
    try:
        arquivo.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError:
        return 1
    return codigo
