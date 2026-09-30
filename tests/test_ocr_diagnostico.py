"""Testes da conferência sem janela dos detectores de texto (core/ocr_diagnostico.py) e de onde
o Tesseract procura os idiomas (item 1.3, 29/09/2026).

A conferência de verdade roda no programa empacotado
(dist\\EditorImpressao\\EditorImpressao.exe --conferir-ocr ...) e leva ~30 s
(abre o motor do Kraken); aqui fica o que tem resposta rápida: argumentos
errados, imagem que não existe, e o main.py desviando antes de abrir janela.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from core import ocr_diagnostico, ocr_tesseract

RAIZ = Path(__file__).resolve().parent.parent


def test_argumentos_errados_dao_codigo_2(tmp_path):
    assert ocr_diagnostico.linha_de_comando([]) == 2
    assert ocr_diagnostico.linha_de_comando(["so_a_imagem.png"]) == 2
    assert ocr_diagnostico.linha_de_comando(["a.png", str(tmp_path / "s.json"), "lat", "nao_e_numero"]) == 2


def test_imagem_que_nao_existe_grava_o_arquivo_e_nao_quebra(tmp_path, monkeypatch):
    """Sem a imagem, os três dizem que não leram; o arquivo sai e o código é 1.
    O motor do Kraken e trocado por um caminho que nao existe (nao abre de verdade)."""
    from core import ocr_kraken

    monkeypatch.setattr(ocr_kraken, "achar_pasta_do_motor", lambda: None)
    saida = tmp_path / "saida.json"
    codigo = ocr_diagnostico.linha_de_comando([str(tmp_path / "nao_existe.png"), str(saida)])
    assert codigo == 1
    dados = json.loads(saida.read_text(encoding="utf-8"))
    assert dados["todos_leram"] is False
    assert set(dados["ocrs"]) == {"doctr", "tesseract", "kraken"}
    assert all(not v["disponivel"] and v["motivo"] for v in dados["ocrs"].values())


def test_main_desvia_antes_de_abrir_janela(tmp_path):
    """--conferir-ocr roda sem Qt: com argumentos errados sai com 2 na hora."""
    resultado = subprocess.run([sys.executable, str(RAIZ / "main.py"), "--conferir-ocr"],
                               capture_output=True, timeout=60)
    assert resultado.returncode == 2


def test_tessdata_do_programa_instalado_vem_primeiro(tmp_path, monkeypatch):
    exe = tmp_path / "EditorImpressao.exe"
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe))
    lugares = ocr_tesseract.lugares_dos_modelos()
    assert lugares[0] == tmp_path / "tesseract" / "tessdata"
    assert lugares[-1] == ocr_tesseract.PASTA_DOS_MODELOS
    (tmp_path / "tesseract" / "tessdata").mkdir(parents=True)
    assert ocr_tesseract.achar_pasta_dos_modelos() == tmp_path / "tesseract" / "tessdata"


def test_seis_idiomas_do_instalador():
    assert ocr_tesseract.IDIOMAS_DO_INSTALADOR == ("lat", "ita", "por", "fra", "eng", "script/Fraktur")


def test_ocr_a_parte_nao_herda_a_pasta_de_dlls_do_programa_empacotado(tmp_path, monkeypatch):
    """Achado em 29/09: no programa empacotado, o motor do Kraken herdava a
    "pasta de DLLs" do PyInstaller (_internal) e carregava de lá o Visual C++
    errado. abrir_processo tira a marca só durante o Popen e a devolve depois."""
    import ctypes
    import os
    import subprocess

    from core.ocr_comum import abrir_processo

    if os.name != "nt":
        return
    kernel32 = ctypes.WinDLL("kernel32")
    interno = tmp_path / "_internal"
    interno.mkdir()
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(interno), raising=False)
    monkeypatch.setenv("PATH", str(interno) + os.pathsep + os.environ.get("PATH", ""))
    filho = ("import ctypes, os; b = ctypes.create_unicode_buffer(32768); "
             "ctypes.WinDLL('kernel32').GetDllDirectoryW(32768, b); "
             "print(repr(b.value)); print(os.environ['PATH'].split(os.pathsep)[0])")
    kernel32.SetDllDirectoryW(str(interno))
    try:
        processo = abrir_processo([sys.executable, "-c", filho], stdout=subprocess.PIPE, text=True)
        saida, _ = processo.communicate(timeout=60)
        memoria = ctypes.create_unicode_buffer(32768)
        kernel32.GetDllDirectoryW(32768, memoria)
        depois = memoria.value
    finally:
        kernel32.SetDllDirectoryW(None)
    linhas = saida.splitlines()
    assert linhas[0] == "''", "o filho herdou a pasta de DLLs do programa"
    assert os.path.normcase(linhas[1]) != os.path.normcase(str(interno)), "o filho herdou o PATH do programa"
    assert depois == str(interno), "o programa perdeu a própria pasta de DLLs"
