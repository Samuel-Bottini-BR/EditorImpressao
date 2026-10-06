"""A gravacao sozinha (o relogio de salvar) nao para a janela (R1 do
verificador, 05/10/2026).

O defeito: durante a conversao das zonas do Siebmacher (268 paginas), a janela
ficou 6 s ou mais sem responder, uma vez em cada rodada. Medido pelo
implementador com a janela instrumentada: a unica coisa que parava o fio da
janela durante a conversao era a gravacao do projeto inteiro (3 a 6 MB), que o
relogio de salvar faz a cada pagina folheada - 0,25 a 0,37 s cada vez, com a
janela parada DENTRO da escrita do arquivo (o D: das conferencias e um disco
USB; com o disco ocupado ou o computador sem memoria livre, a escrita demora
mais). Agora o relogio grava por tras (projetos.salvar_estado_por_tras): a
janela so tira a fotografia do projeto, e o disco fica com um fio de fundo.

O que se prende aqui (teste de maquina):
- com o disco levando 1,5 s para escrever, gravar pelo relogio volta na hora
  e a janela continua respondendo enquanto folheia e converte;
- o arquivo que chega ao disco e o ultimo pedido (pedidos seguidos se juntam);
- gravar na hora (fechar, trocar de livro, processar) espera a fila e fica por
  ultimo; ler o projeto espera a fila;
- erro de disco no fio de fundo nao o mata: a gravacao seguinte funciona.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

import projetos
from core.filtros import MAGICO_PRO, ORIGINAL, PRETO_E_BRANCO
from modelos import ConfigFolha, ConfigPagina, Projeto


def _projeto(n: int = 40) -> Projeto:
    projeto = Projeto(caminho_entrada="x.pdf", nome="livro")
    projeto.folhas = [ConfigFolha(indice=i) for i in range(n)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i, filtro=ORIGINAL) for i in range(n)]
    return projeto


def _resumo(tmp_path) -> projetos.Resumo:
    pasta = tmp_path / "projeto"
    pasta.mkdir(exist_ok=True)
    return projetos.Resumo(pasta=str(pasta), nome="livro", caminho_entrada="x.pdf")


def _no_disco(resumo) -> dict:
    return json.loads((Path(resumo.pasta) / projetos.ARQUIVO_ESTADO).read_text(encoding="utf-8"))


@pytest.fixture
def disco_lento(monkeypatch):
    """O disco leva `segundos` para escrever o projeto.json (e o resumo.json);
    conta as escritas do projeto.json."""
    estado = {"segundos": 1.5, "escritas": 0, "fios": set()}
    original = projetos._escrever_estado
    original_resumo = projetos._escrever_resumo

    def devagar(pasta, texto):
        estado["fios"].add(threading.current_thread().name)
        time.sleep(estado["segundos"])
        estado["escritas"] += 1
        original(pasta, texto)

    def resumo_devagar(pasta, dados):
        estado["fios"].add(threading.current_thread().name)
        time.sleep(estado["segundos"])
        original_resumo(pasta, dados)

    monkeypatch.setattr(projetos, "_escrever_estado", devagar)
    monkeypatch.setattr(projetos, "_escrever_resumo", resumo_devagar)
    yield estado
    projetos.esperar_gravacoes(30)


def test_por_tras_volta_na_hora_mesmo_com_o_disco_lento(tmp_path, disco_lento):
    resumo, projeto = _resumo(tmp_path), _projeto()
    projeto.paginas[3].filtro = MAGICO_PRO
    t = time.perf_counter()
    projetos.salvar_estado_por_tras(resumo, projeto)
    assert time.perf_counter() - t < 0.5            # nao esperou o disco
    projeto.paginas[3].filtro = PRETO_E_BRANCO       # mexer depois nao muda o pedido
    assert projetos.esperar_gravacoes(10)
    assert _no_disco(resumo)["paginas"][3]["filtro"] == MAGICO_PRO
    assert disco_lento["fios"] == {"gravar o projeto"}   # o disco foi no fio de fundo


def test_pedidos_seguidos_se_juntam_e_o_ultimo_vale(tmp_path, disco_lento):
    disco_lento["segundos"] = 0.5
    resumo, projeto = _resumo(tmp_path), _projeto()
    for filtro in (MAGICO_PRO, PRETO_E_BRANCO, ORIGINAL, MAGICO_PRO, PRETO_E_BRANCO):
        projeto.paginas[0].filtro = filtro
        projetos.salvar_estado_por_tras(resumo, projeto)
    assert projetos.esperar_gravacoes(10)
    assert _no_disco(resumo)["paginas"][0]["filtro"] == PRETO_E_BRANCO
    assert disco_lento["escritas"] <= 2              # o primeiro e o ultimo, no maximo


def test_gravar_na_hora_espera_a_fila_e_fica_por_ultimo(tmp_path, disco_lento):
    resumo, projeto = _resumo(tmp_path), _projeto()
    projeto.paginas[1].filtro = MAGICO_PRO
    projetos.salvar_estado_por_tras(resumo, projeto)
    projeto.paginas[1].filtro = PRETO_E_BRANCO
    projetos.salvar_estado(resumo, projeto)          # fechar o programa, por exemplo
    # quando salvar_estado volta, o disco ja tem o ultimo, sem esperar mais nada
    assert _no_disco(resumo)["paginas"][1]["filtro"] == PRETO_E_BRANCO
    assert projetos.esperar_gravacoes(0)


def test_ler_o_projeto_espera_a_fila(tmp_path, disco_lento):
    resumo, projeto = _resumo(tmp_path), _projeto()
    projeto.paginas[2].filtro = MAGICO_PRO
    projetos.salvar_estado_por_tras(resumo, projeto)
    lido = projetos.carregar_estado(resumo)
    assert lido is not None and lido.paginas[2].filtro == MAGICO_PRO
    assert projetos.tem_trabalho_salvo(resumo)


def test_o_resumo_tambem_vai_por_tras(tmp_path, disco_lento):
    resumo, projeto = _resumo(tmp_path), _projeto()
    t = time.perf_counter()
    projetos.atualizar(resumo, projeto, pagina_atual=7, por_tras=True)
    assert time.perf_counter() - t < 0.5
    lido = projetos.ler_resumo(resumo.pasta)             # espera a fila
    assert lido is not None and lido.pagina_atual == 7
    assert disco_lento["fios"] == {"gravar o projeto"}


def test_erro_no_disco_nao_mata_o_fio_de_gravar(tmp_path, monkeypatch):
    resumo, projeto = _resumo(tmp_path), _projeto()
    original = projetos._escrever_estado
    vezes = []

    def falha_a_primeira(pasta, texto):
        vezes.append(1)
        if len(vezes) == 1:
            raise OSError("disco cheio")
        original(pasta, texto)

    monkeypatch.setattr(projetos, "_escrever_estado", falha_a_primeira)
    projetos.salvar_estado_por_tras(resumo, projeto)
    assert projetos.esperar_gravacoes(10)
    assert not (Path(resumo.pasta) / projetos.ARQUIVO_ESTADO).exists()
    projeto.paginas[0].filtro = MAGICO_PRO
    projetos.salvar_estado_por_tras(resumo, projeto)
    assert projetos.esperar_gravacoes(10)
    assert _no_disco(resumo)["paginas"][0]["filtro"] == MAGICO_PRO


def test_a_fotografia_e_o_disco_dao_o_mesmo_que_antes(tmp_path):
    """Dividir para_dicionario em fotografar + para_o_disco nao muda o arquivo."""
    projeto = _projeto(5)
    projeto.paginas[1].selecao = [{"tipo": "gravura", "forma": "retangulo",
                                   "pontos": [[0.1, 0.1], [0.5, 0.5]]}]
    assert Projeto.para_o_disco(projeto.fotografar()) == projeto.para_dicionario()


# ---------------------------------------------------------------------------
# Na janela: folhear enquanto converte, com o disco lento
# ---------------------------------------------------------------------------

from tests.test_converter_zonas_ao_abrir import (  # noqa: E402, F401 - fixtures
    _abrir_projeto_antigo,
    _esperar,
    app,
    janela,
    pdf,
    raiz,
)


def test_folhear_com_o_disco_lento_nao_para_a_janela(janela, app, pdf, disco_lento):
    """O caso do R1: o relogio de salvar dispara a cada pagina folheada.
    Com o disco levando 1,5 s por gravacao, a janela tem de continuar
    respondendo (antes ficava 1,5 s parada a cada pagina). E ao fechar o
    ultimo estado vai para o disco."""
    arquivo = _abrir_projeto_antigo(janela, pdf)
    projetos.esperar_gravacoes(30)
    total = len(janela.projeto.paginas)
    inicio = time.perf_counter()
    piores = []
    for passo in range(4):                           # 4 paginas, uma gravacao cada
        janela.tela_conferir.ir_para_pagina(passo % total)
        janela._relogio_de_salvar.timeout.emit()     # o relogio de salvar dispara
        piores.append(_esperar(app, lambda t=time.perf_counter(): time.perf_counter() - t > 0.4,
                               limite_s=5))
    assert max(piores) < 0.5, f"a janela ficou {max(piores):.2f} s sem responder"
    assert time.perf_counter() - inicio < 4.5        # nao esperou 4 x 1,5 s
    janela.projeto.paginas[0].filtro = MAGICO_PRO
    janela.close()                                   # grava na hora, depois da fila
    assert json.loads(arquivo.read_text(encoding="utf-8"))["paginas"][0]["filtro"] == MAGICO_PRO
