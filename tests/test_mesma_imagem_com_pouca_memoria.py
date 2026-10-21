"""Bug da Lista de bugs (20/10/2026): "O mesmo código nem sempre dá a mesma
imagem": a Horas p. 11 em Mágico pro saiu diferente UMA vez, numa passada
longa com pouca memória livre (o PC ficou sem memória três vezes); repetida
quatro vezes, deu sempre a mesma soma.

Causa achada (21/10/2026): dois caminhos que, quando falta memória, trocam a
conta em SILÊNCIO e mudam a imagem (as regiões de gravura e de texto mudam, e
com elas o Mágico pro):
  1. o modelo de layout (core/detectar_regioes.DetectorDeLayout) era
     carregado uma vez; se a carga falhava (MemoryError), ficava sem modelo a
     sessão inteira;
  2. o detector de gravura do ScanTailor, ao responder "faltou memória" numa
     página, caía no detector antigo nessa página.
Agora: a carga que falhou é tentada de novo na próxima página (só o arquivo
ou a biblioteca ausentes ficam de vez), e a falta de memória numa página é
tentada de novo depois de soltar memória (gc), antes de cair no antigo.

Testes de máquina, com as falhas simuladas (sem DLL nem modelo de verdade).
"""

from __future__ import annotations

import sys
import types

import numpy as np
import pytest

from core import detectar_regioes as dr
from core import gravura_scantailor as gs


def test_regressao_modelo_de_layout_que_falhou_por_memoria_e_tentado_de_novo(tmp_path, monkeypatch):
    arquivo = tmp_path / "doclayout.onnx"
    arquivo.write_bytes(b"x")
    chamadas = []

    class Sessao:
        pass

    def sessao(*_a, **_k):
        chamadas.append(1)
        if len(chamadas) == 1:
            raise MemoryError("sem memória")
        return Sessao()

    falso = types.SimpleNamespace(
        SessionOptions=lambda: types.SimpleNamespace(graph_optimization_level=None),
        GraphOptimizationLevel=types.SimpleNamespace(ORT_ENABLE_ALL=99),
        InferenceSession=sessao)
    monkeypatch.setitem(sys.modules, "onnxruntime", falso)
    detector = dr.DetectorDeLayout(arquivo)
    assert detector._carregar() is None                 # a 1a carga falhou
    assert isinstance(detector._carregar(), Sessao), "a falha de memória ficou para a sessão inteira"
    assert len(chamadas) == 2


def test_modelo_ausente_nao_fica_tentando(tmp_path):
    detector = dr.DetectorDeLayout(tmp_path / "nao_existe.onnx")
    assert detector._carregar() is None and detector._carregar() is None


def test_regressao_gravura_com_falta_de_memoria_tenta_de_novo(monkeypatch):
    """A DLL responde "faltou memória" na primeira vez e dá certo na segunda: a
    página tem de ficar com a gravura do ScanTailor, e não cair no detector
    antigo (o que mudava a imagem)."""
    respostas = [gs._indisponivel("Faltou memória para achar as gravuras desta página.", "código"),
                 gs.ResultadoGravura(np.ones((20, 30), bool))]
    monkeypatch.setattr(gs, "detectar_gravura", lambda *_a, **_k: respostas.pop(0))
    img = np.full((20, 30, 3), 255, np.uint8)
    mascara, motivo = dr._gravura_pelo_scantailor(img, 150.0, 150.0, "livre")
    assert motivo is None and mascara is not None, motivo


def test_gravura_com_outra_falha_nao_repete(monkeypatch):
    vezes = []

    def falha(*_a, **_k):
        vezes.append(1)
        return gs._indisponivel("O detector de gravura do ScanTailor falhou nesta página.", "x")

    monkeypatch.setattr(gs, "detectar_gravura", falha)
    mascara, motivo = dr._gravura_pelo_scantailor(np.full((20, 30, 3), 255, np.uint8), 150.0, 150.0, "livre")
    assert mascara is None and motivo and len(vezes) == 1
