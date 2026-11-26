"""Prova EXECUTADA (quem tenta quebrar, volta 2): o "Reiniciar agora" pela ponte da tela DE VERDADE
(`ui/aviso_de_atualizacao.PonteDaTela`, com uma janela Qt de verdade, fora da tela: QT_QPA_PLATFORM=offscreen), o
executor e a regra de verdade, a lista de processos de verdade, um pacote de verdade de ~460 MB em <raiz>\\packages.
De mentira: as caixas (a de "Reiniciar agora / Depois" responde "Reiniciar agora"; as outras só anotam) e o Velopack
da biblioteca (a troca).

A. A janela fica parada? Um relógio do Qt bate a cada 50 ms; mede-se o maior intervalo sem bater ENTRE o clique em
   "Reiniciar agora" e o fechar da janela (a janela ainda está na tela nesse tempo).
B. "Reiniciar agora" quando a troca não pode por outro motivo que não outra janela (aqui: o pacote baixado sumiu, como
   um antivírus que o põe de lado): o que aparece na tela depois do clique.
"""
import hashlib
import json
import os
import sys
import time
import zipfile
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
RAMO = Path(r"D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo")
R = Path(r"D:\programas\EditorImpressao\rascunho-qtq2\tela")
os.environ["PROGRAMDATA"] = str(R / "pd")
os.environ["LOCALAPPDATA"] = str(R / "local")
for p in (R / "raiz" / "current", R / "raiz" / "packages", R / "local"):
    p.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(RAMO))
from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QWidget  # noqa: E402

import atualizacao  # noqa: E402
from core import conversa_com_o_velopack as conversa  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402
from ui import aviso_de_atualizacao as aviso  # noqa: E402

PACOTE = R / "raiz" / "packages" / "EditorImpressaoPrograma-1.2.0-full.nupkg"
if not PACOTE.exists():
    with zipfile.ZipFile(PACOTE, "w", compression=zipfile.ZIP_STORED) as z:
        z.writestr("lib/app/motor-exigido.json", json.dumps({"versao": 1}))
        with z.open("lib/app/grande.bin", "w", force_zip64=True) as f:
            bloco = os.urandom(1 << 20)
            for _ in range(460):
                f.write(bloco)
SOMA = hashlib.sha256(PACOTE.read_bytes()).hexdigest()
app = QApplication.instance() or QApplication([])


class Velopack:
    def trocar(self, endereco, v, reabrir, argumentos):
        pass


def rodar(pacote_some=False):
    janela = QWidget()
    janela.show()
    a = atualizacao.Atualizacao(velopack=Velopack(), raiz=R / "raiz", por_tras=lambda f: f(),
                                pasta_grava=lambda r: True, garantir_motor=lambda: True, motor_no_lugar=lambda v: True)
    a._achada = conversa.VersaoDoVelopack("EditorImpressaoPrograma", "1.2.0", PACOTE.name, SOMA, PACOTE.stat().st_size)
    a._somas_assinadas["1.2.0"] = SOMA
    a._estado = fases.Estado(fase=fases.Fase.PRONTA, versao="1.1.0", nova="1.2.0")
    caixas, marcas = [], {}
    batidas = []

    def perguntar(_j, titulo, texto, sim, nao):
        caixas.append(("pergunta", titulo, texto))
        marcas["clique"] = time.perf_counter()
        if pacote_some:
            PACOTE.rename(PACOTE.with_suffix(".posto-de-lado"))
        return len([c for c in caixas if c[0] == "pergunta"]) == 1   # só o primeiro aviso: "Reiniciar agora"

    def avisar(_j, titulo, texto, icone=None):
        caixas.append(("aviso", titulo, texto))

    ponte = aviso.PonteDaTela(janela, a, perguntar=perguntar, avisar=avisar)
    janela._ponte_da_atualizacao = ponte
    fechar_original = janela.close

    def fechar():
        marcas["fechou"] = time.perf_counter()
        return fechar_original()
    janela.close = fechar
    a.ligar_a_tela(ponte.receber)
    relogio = QTimer()
    relogio.timeout.connect(lambda: batidas.append(time.perf_counter()))
    relogio.start(50)
    QTimer.singleShot(300, lambda: a._para_a_tela(fases.MostrarVersaoNova("1.2.0")))
    QTimer.singleShot(4000 if not pacote_some else 1500, app.quit)
    app.exec()
    relogio.stop()
    if pacote_some and PACOTE.with_suffix(".posto-de-lado").exists():
        PACOTE.with_suffix(".posto-de-lado").rename(PACOTE)
    fim = marcas.get("fechou", time.perf_counter())
    pontos = [marcas.get("clique", 0)] + [b for b in batidas if marcas.get("clique", 0) <= b <= fim] + [fim]
    maior = max((b - a_ for a_, b in zip(pontos, pontos[1:])), default=0)
    return {"caixas na tela": caixas, "a janela fechou": "fechou" in marcas, "janela ainda visível": janela.isVisible(),
            "fase": a.estado.fase.value,
            "do clique ao fechar (s)": round(marcas["fechou"] - marcas["clique"], 2) if "fechou" in marcas else None,
            "maior tempo da tela parada entre o clique e o fechar (s)": round(maior, 2)}


resultado = {"A (pacote no lugar)": rodar(), "B (o pacote sumiu antes do clique)": rodar(pacote_some=True)}
texto = json.dumps(resultado, ensure_ascii=False, indent=1)
Path(__file__).with_name("prova_reiniciar_agora_na_tela-resultado.txt").write_text(texto, encoding="utf-8")
print(texto)
