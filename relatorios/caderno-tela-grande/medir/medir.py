"""Medidas da D-574 na etapa 7 do Automático (02/11/2026), do jeito do medir.py do verificador
da D-574 (relatorios/livreto-ver/verificador/medir.py na cópia verif-livreto): relógio de 5 ms no
fio da tela, sem print no meio, janela de verdade do Windows fora da tela.

  python relatorios/caderno-tela-grande/medir/medir.py <livro: gradus|palatino>

Mede: (1) abrir a etapa 7 na janela grande (a primeira folha); (2) 5 setas; (3) trocar as
páginas por caderno (20 -> 12 -> 20); (4) abrir a tela grande; (5) voltar para outra etapa.
Pasta de dados separada (LOCALAPPDATA em _tmp/medir-caderno)."""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
NOME = sys.argv[1] if len(sys.argv) > 1 else "gradus"
TRAB = RAIZ / "_tmp" / f"medir-caderno-{NOME}"
if TRAB.exists():
    shutil.rmtree(TRAB)
TRAB.mkdir(parents=True)
os.environ["LOCALAPPDATA"] = str(TRAB)
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))
LIVRO = TRAB / f"{NOME}.pdf"
shutil.copy(RAIZ / "_tmp" / "livros" / f"{NOME}.pdf", LIVRO)

from PySide6.QtCore import Qt, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

app = QApplication(sys.argv)
from core import automatico as A  # noqa: E402
from core import perfis  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402

MED: dict = {"livro": NOME}


class Relogio:
    def __init__(self):
        self.ultimo = time.monotonic(); self.maior = 0.0; self.batidas = 0
        self.t = QTimer(); self.t.setInterval(5); self.t.timeout.connect(self.bate); self.t.start()

    def bate(self):
        agora = time.monotonic(); self.maior = max(self.maior, agora - self.ultimo)
        self.ultimo = agora; self.batidas += 1

    def zerar(self):
        self.ultimo = time.monotonic(); self.maior = 0.0; self.batidas = 0


def rodar(seg):
    fim = time.monotonic() + seg
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.002)


def esperar(painel, seg=600):
    t = time.monotonic()
    while time.monotonic() - t < seg:
        app.processEvents()
        if not painel.calculando():
            rodar(0.02)
            if not painel.calculando():
                break
        time.sleep(0.002)
    return round(time.monotonic() - t, 3)


janela = JanelaPrincipal()
janela.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
janela.resize(1280, 657)
janela.move(-32000, -32000)
janela.show()
janela.abrir_livro(str(LIVRO))
rodar(1.0)
# a medida do livro ao abrir (D-284) roda por trás: espera acabar, para medir só a folha
fim = time.monotonic() + 600
while time.monotonic() < fim and getattr(janela, "medida_ao_abrir", None) is not None:
    rodar(0.2)
rodar(2.0)
estado = janela.estado_do_automatico
estado.por_receita(perfis.NOME_DE_FABRICA)
estado.marcadas.add(A.CADERNOS)
grande = janela.abrir_o_automatico(A.LIMPAR)
grande.move(-32000, -32000)
esperar(grande.folhear)
rel = Relogio()
rodar(0.3)

# vigia (só com VIGIA=1): quando o relógio da tela fica mais de 80 ms sem bater, guarda onde o fio
# da tela está (se ele estiver trabalhando; se for outro fio segurando o Python, o vigia nem roda)
if os.environ.get("VIGIA"):
    import threading
    import traceback
    from collections import Counter

    PRINCIPAL = threading.main_thread().ident
    ONDE = Counter()

    def vigiar():
        while True:
            time.sleep(0.02)
            if time.monotonic() - rel.ultimo > 0.08:
                quadro = sys._current_frames().get(PRINCIPAL)
                if quadro is not None:
                    pilha = traceback.extract_stack(quadro)[-6:]
                    ONDE[" <- ".join(f"{Path(q.filename).name}:{q.lineno}:{q.name}" for q in reversed(pilha))] += 1

    threading.Thread(target=vigiar, daemon=True).start()

# a base: a página da direita de hoje (D-577, antes e depois), 3 setas, a mesma medida
base = []
for _ in range(3):
    rel.zerar()
    grande.folhear.virar(1)
    s = esperar(grande.folhear)
    base.append({"pagina": grande.folhear._indice + 1, "s": s, "maior_parada_s": round(rel.maior, 3)})
MED["base_antes_e_depois_setas"] = base

folhas = grande.folhas_do_caderno
lista = grande.painel_de_opcoes.lista
rel.zerar(); t = time.monotonic()
lista.setCurrentItem(lista.item_da_etapa(A.CADERNOS))
clique = round(time.monotonic() - t, 3)
s = esperar(folhas)
MED["abrir_a_etapa_7"] = {"clique_s": clique, "primeira_folha_s": s, "maior_parada_s": round(rel.maior, 3),
                          "batidas_de_5ms": rel.batidas, "folhas": folhas.total()}
setas = []
for _ in range(5):
    rel.zerar(); t = time.monotonic()
    folhas.passar_folha(1)
    s = esperar(folhas)
    setas.append({"folha": folhas.posicao + 1, "s": s, "maior_parada_s": round(rel.maior, 3),
                  "batidas_de_5ms": rel.batidas})
MED["setas"] = setas
combo = grande.controles["paginas_por_caderno"]
trocas = []
for n in (12, 20):
    rel.zerar(); t = time.monotonic()
    combo.setCurrentIndex(combo.findData(n))
    s = esperar(folhas)
    trocas.append({"por_caderno": n, "s": s, "maior_parada_s": round(rel.maior, 3), "folhas": folhas.total()})
MED["trocar_paginas_por_caderno"] = trocas
rel.zerar(); t = time.monotonic()
folhas.abrir_em_tela_cheia()
folhas.tela_grande.move(-32000, -32000)
rodar(0.3)
MED["abrir_a_tela_grande"] = {"s": round(time.monotonic() - t - 0.3, 3), "maior_parada_s": round(rel.maior, 3)}
rel.zerar()
folhas.tela_grande.botao_proxima.click()
s = esperar(folhas)
MED["seta_na_tela_grande"] = {"s": s, "maior_parada_s": round(rel.maior, 3)}
folhas.tela_grande.accept()
rodar(0.2)
rel.zerar(); t = time.monotonic()
lista.setCurrentItem(lista.item_da_etapa(A.LIMPAR))
s = esperar(grande.folhear)
MED["voltar_a_outra_etapa"] = {"s": s, "maior_parada_s": round(rel.maior, 3)}
MED["maior_parada_de_todas_s"] = max(
    [MED["abrir_a_etapa_7"]["maior_parada_s"]] + [x["maior_parada_s"] for x in setas]
    + [x["maior_parada_s"] for x in trocas] + [MED["abrir_a_tela_grande"]["maior_parada_s"],
                                               MED["seta_na_tela_grande"]["maior_parada_s"],
                                               MED["voltar_a_outra_etapa"]["maior_parada_s"]])
grande.reject()
rodar(0.5)
if os.environ.get("VIGIA"):
    MED["vigia"] = ONDE.most_common(12)
print(json.dumps(MED, ensure_ascii=False, indent=1))
(AQUI / f"medir-{NOME}.json").write_text(json.dumps(MED, ensure_ascii=False, indent=1), encoding="utf-8")
janela._fechar_a_janela_do_automatico()
janela.close()
