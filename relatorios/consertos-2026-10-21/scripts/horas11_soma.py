"""Soma da Horas 11 em Mágico pro, processada pelo programa (como a prova
"sai igual"). Com 'sem_gravura_st' simula a DLL de gravura respondendo
"faltou memória" (o detector antigo entra), para ver se isso muda a imagem.
Uso: python horas11_soma.py [sem_gravura_st]"""
import hashlib, sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
import numpy as np
from core import pipeline, gravura_scantailor as gs
from core.filtros import MAGICO_PRO
from core.pdf_io import abrir_pdf
from modelos import Projeto
PDF = Path(r"D:\programas\EditorImpressao\gabarito\paginas\horas_p011.pdf")
if sys.argv[1:] == ["sem_gravura_st"]:
    gs.detectar_gravura = lambda *a, **k: gs._indisponivel(gs._MOTIVO_FALTOU_MEMORIA, "simulado")
p = Projeto(caminho_entrada=str(PDF), nome="h"); p.filtro_padrao = MAGICO_PRO; p.qualidade_dpi = 300
p = pipeline.analisar_projeto(p)
doc = abrir_pdf(str(PDF))
img, _ = pipeline.renderizar_pagina(doc, p, p.paginas[0], dpi=300)
print(sys.argv[1:] or ["normal"], img.shape, hashlib.sha256(np.ascontiguousarray(img).tobytes()).hexdigest()[:12])
