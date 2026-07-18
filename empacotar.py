"""Gera o EditorImpressao.exe (Etapa 8).

Uso:
    python empacotar.py

Sai um arquivo unico em dist/. Sem instalador, sem Python na maquina do Kaique.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

NOME = "EditorImpressao"

# O PySide6 traz muita coisa que este programa nunca usa. Tirar reduz o .exe
# em dezenas de MB e diminui o tempo de abertura.
EXCLUIR = [
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtWebEngineQuick",
    "PySide6.QtQuick", "PySide6.QtQml", "PySide6.Qt3DCore", "PySide6.Qt3DRender",
    "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets", "PySide6.QtCharts",
    "PySide6.QtDataVisualization", "PySide6.QtBluetooth", "PySide6.QtNetworkAuth",
    "PySide6.QtPositioning", "PySide6.QtSensors", "PySide6.QtSerialPort",
    "PySide6.QtSql", "PySide6.QtTest", "PySide6.QtDesigner", "PySide6.QtHelp",
    "matplotlib", "scipy", "pandas", "IPython", "tkinter", "pytest",
]

# O DoxaPy e uma biblioteca nativa: o PyInstaller nao acha sozinho.
OCULTOS = ["doxapy", "skimage.filters", "PIL._tkinter_finder"]


def main() -> int:
    raiz = Path(__file__).parent
    for pasta in ("build", "dist"):
        shutil.rmtree(raiz / pasta, ignore_errors=True)

    comando = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onefile",           # um arquivo so
        "--windowed",          # sem janela preta de console atras
        "--name", NOME,
        "--paths", str(raiz),
    ]
    for modulo in EXCLUIR:
        comando += ["--exclude-module", modulo]
    for modulo in OCULTOS:
        comando += ["--hidden-import", modulo]

    recursos = raiz / "recursos"
    if recursos.exists() and any(recursos.iterdir()):
        comando += ["--add-data", f"{recursos}{';' if sys.platform == 'win32' else ':'}recursos"]

    comando.append(str(raiz / "main.py"))

    print("Empacotando... isso leva alguns minutos.\n")
    resultado = subprocess.run(comando, cwd=raiz)
    if resultado.returncode != 0:
        print("\nO empacotamento falhou.")
        return resultado.returncode

    exe = raiz / "dist" / (f"{NOME}.exe" if sys.platform == "win32" else NOME)
    if not exe.exists():
        print("\nO PyInstaller terminou mas o arquivo nao apareceu.")
        return 1

    print(f"\nPronto: {exe}")
    print(f"Tamanho: {exe.stat().st_size / 1024 / 1024:.0f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
