#!/bin/bash
# Roda todos os detectores do 1.3, UM DE CADA VEZ (para o tempo de um nao
# atrapalhar o do outro). Git Bash no Windows. Log em saida_teste/ocr-1.3/log-*.txt.
cd "$(dirname "$0")"
PY=/d/programas/EditorImpressao/.venv-ocr/Scripts/python.exe
LOG=/d/programas/EditorImpressao/saida_teste/ocr-1.3
date > $LOG/inicio.txt
$PY rodar_tesseract.py > $LOG/log-tesseract.txt 2>&1
$PY rodar_onnxtr.py    > $LOG/log-onnxtr.txt 2>&1
$PY rodar_rapidocr.py  > $LOG/log-rapidocr.txt 2>&1
wsl -d Ubuntu -u root -- bash -c "cd /mnt/d/programas/EditorImpressao/relatorios/fase1-1.3-comparacao-ocr-2026-09-28/scripts && /root/ocr-kraken/.venv/bin/python rodar_kraken.py" > $LOG/log-kraken.txt 2>&1
date > $LOG/fim.txt
