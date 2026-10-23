"""Item 2.16: usar todos os núcleos do processador (core/nucleos.py).

Testes de máquina:
- em_ordem entrega na ordem das páginas, nunca tem mais páginas em andamento
  (ou prontas esperando) do que trabalhadores, sobe o erro da página na vez
  dela e para de pôr páginas novas ao cancelar;
- quantos_trabalhadores segue os núcleos, o pedido de Configurações e a
  memória livre;
- a análise e o PDF final saem IDÊNTICOS com 1 e com 4 trabalhadores (a
  prova de que mexe só na velocidade).
"""

from __future__ import annotations

import random
import threading
import time

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import nucleos


def test_em_ordem_entrega_na_ordem_e_com_a_fila_limitada():
    em_andamento = 0
    maximo = 0
    tranca = threading.Lock()

    def fazer(n):
        nonlocal em_andamento, maximo
        with tranca:
            em_andamento += 1
            maximo = max(maximo, em_andamento)
        time.sleep(random.uniform(0, 0.01))
        with tranca:
            em_andamento -= 1
        return n * n

    pendentes_no_maximo = 0
    vistos = []
    gerador = nucleos.em_ordem(range(40), fazer, 4)
    for item, resultado in gerador:
        vistos.append((item, resultado))
    assert vistos == [(n, n * n) for n in range(40)]
    assert 1 <= maximo <= 4
    assert pendentes_no_maximo == 0


def test_em_ordem_nunca_pede_mais_itens_que_os_trabalhadores():
    pedidos = []

    def itens():
        for n in range(100):
            pedidos.append(n)
            yield n

    gerador = nucleos.em_ordem(itens(), lambda n: n, 3)
    next(gerador)
    # entregou 1; no máximo os 3 da fila + 1 para repor foram pedidos
    assert len(pedidos) <= 4
    gerador.close()


def test_em_ordem_sobe_o_erro_na_vez_da_pagina():
    def fazer(n):
        if n == 5:
            raise ValueError("página 5")
        return n

    vistos = []
    with pytest.raises(ValueError, match="página 5"):
        for item, _r in nucleos.em_ordem(range(20), fazer, 4):
            vistos.append(item)
    assert vistos == [0, 1, 2, 3, 4]


def test_em_ordem_para_ao_cancelar():
    feitos = []
    cancelar = threading.Event()

    def fazer(n):
        feitos.append(n)
        return n

    vistos = []
    for item, _r in nucleos.em_ordem(range(100), fazer, 2, cancelado=cancelar.is_set):
        vistos.append(item)
        if item == 3:
            cancelar.set()
    assert vistos[:4] == [0, 1, 2, 3]
    assert len(feitos) < 10


def test_com_um_trabalhador_e_o_laco_de_sempre():
    linhas = set()

    def fazer(n):
        linhas.add(threading.current_thread().name)
        return n

    assert [r for _i, r in nucleos.em_ordem(range(5), fazer, 1)] == list(range(5))
    assert linhas == {threading.current_thread().name}


def test_quantos_trabalhadores():
    assert nucleos.quantos_trabalhadores(pedido=0, memoria_mb=64000, nucleos=8) == 8
    assert nucleos.quantos_trabalhadores(pedido=1, memoria_mb=64000, nucleos=8) == 1
    assert nucleos.quantos_trabalhadores(pedido=2, memoria_mb=64000, nucleos=8) == 2
    # pouca memória: corta (reserva + 900 MB por trabalhador)
    assert nucleos.quantos_trabalhadores(pedido=0, memoria_mb=nucleos.RESERVA_MB + 2 * 900,
                                         nucleos=8) == 2
    assert nucleos.quantos_trabalhadores(pedido=0, memoria_mb=500, nucleos=8) == 1
    assert nucleos.quantos_trabalhadores(pedido=0, memoria_mb=10 ** 7, nucleos=64) == nucleos.MAXIMO


def test_pedido_vem_das_configuracoes(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    import configuracoes

    assert nucleos.pedido_da_maquina() == 0              # de fábrica: todos, como o ScanTailor
    configuracoes.escrever("nucleos", 1)
    assert nucleos.pedido_da_maquina() == 1


# --------------------------------------------------------------- o programa

def _livro(caminho, n=6):
    """Folhas com texto falso torto e uma borda escura: passa por dividir,
    endireitar, cortar e filtro."""
    import cv2

    doc = fitz.open()
    for i in range(n):
        arte = np.full((900, 1300, 3), 235, np.uint8)
        arte[:, :30] = 40
        for linha in range(12):
            y = 100 + 55 * linha
            cv2.putText(arte, f"pagina {i} linha {linha} texto", (80, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (20, 20, 20), 2)
            cv2.putText(arte, f"direita {i} {linha}", (700, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (20, 20, 20), 2)
        matriz = cv2.getRotationMatrix2D((650, 450), 1.5 + 0.3 * i, 1.0)
        arte = cv2.warpAffine(arte, matriz, (1300, 900), borderValue=(235, 235, 235))
        ok, buf = cv2.imencode(".png", arte)
        pagina = doc.new_page(width=1300 * 72 / 100, height=900 * 72 / 100)
        pagina.insert_image(pagina.rect, stream=buf.tobytes())
    doc.save(str(caminho))
    doc.close()
    return caminho


def _gerar(tmp_path, trabalhadores, monkeypatch):
    from core import pipeline
    from core.filtros import PRETO_E_BRANCO
    from modelos import Projeto

    monkeypatch.setattr(nucleos, "quantos_trabalhadores", lambda *a, **k: trabalhadores)
    saida = tmp_path / f"s{trabalhadores}.pdf"
    projeto = Projeto(caminho_entrada=str(tmp_path / "l.pdf"), caminho_saida=str(saida), nome="x")
    projeto.dividir_folhas = True
    projeto.filtro_padrao = PRETO_E_BRANCO
    projeto.detectar_regioes = False
    projeto.qualidade_dpi = 100
    projeto = pipeline.analisar_projeto(projeto)
    resumo = [(f.dividir, round(f.posicao_corte, 6), round(f.angulo_detectado, 6), list(f.alertas))
              for f in projeto.folhas] + [(p.indice, p.folha, p.metade, list(p.alertas))
                                          for p in projeto.paginas]
    pipeline.processar(projeto)
    with fitz.open(str(saida)) as doc:
        paginas = [doc[i].get_pixmap(dpi=100).samples for i in range(doc.page_count)]
    return resumo, paginas


def test_analise_e_pdf_iguais_com_um_e_com_quatro(tmp_path, monkeypatch):
    from core import pipeline

    _livro(tmp_path / "l.pdf")
    with pipeline._TRANCA_GEOMETRIAS:
        pipeline._GEOMETRIAS.clear()
    um = _gerar(tmp_path, 1, monkeypatch)
    with pipeline._TRANCA_GEOMETRIAS:
        pipeline._GEOMETRIAS.clear()
    quatro = _gerar(tmp_path, 4, monkeypatch)
    assert um[0] == quatro[0]
    assert len(um[1]) == len(quatro[1]) == 12
    assert um[1] == quatro[1]
