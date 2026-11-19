"""Testes da janela de prova (`janela_de_prova.py`; plano da parte do Windows, peça 10a).

Só o que não pede licença e não chega ao Windows com pedido de licença: a janela monta (fora da tela), tem as seis
provas da sessão A, o pedido de CADA prova passa nas regras da peça antes de ir ao Windows (achado 1 de quem tentou
quebrar), a janela não fecha no meio de uma prova (achado 17), e as provas sem pergunta (lançar solto, programa que
não existe) dão o resultado certo. As provas com a pergunta do Windows (1, 2 e 3 da sessão A) e a parte (b) da prova 5
(que chega ao Windows) NÃO rodam aqui: são à vista, com o Samuel (D-767, D-785).

Seguro mexer: acrescentar casos sem pergunta. Arriscado: chamar aqui uma prova que pede a licença ou chega ao Windows.
"""

from __future__ import annotations

import sys
import time
from dataclasses import asdict
from pathlib import Path

import pytest

from tests.test_windows_peca import _pasta_da_conta_no_disco_do_sistema  # noqa: F401 - a pasta da conta (autouse)

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="a peça só existe no Windows")

RAIZ = Path(__file__).resolve().parent.parent


def test_o_pedido_de_cada_prova_passa_nas_regras_da_peca():
    """Achado 1 de quem tentou quebrar (19/11, GRAVE): o nome da tarefa da pergunta 2 tinha parênteses, a peça
    recusava o pedido antes do Windows, e as perguntas 2 e 3 nunca apareciam (o que a pergunta 1 cria ficaria no PC
    do Samuel). Cada pedido de cada prova passa agora pelas mesmas regras que a peça usa antes de pedir: nenhum nome ou
    pedido errado chega à sessão. No código antigo este teste falha (o nome com "(Nao)")."""
    import janela_de_prova as jp
    from core import windows

    pedidos = {"pergunta 1": jp.passos_da_pergunta_1(), "pergunta 2": jp.passos_da_pergunta_2(),
               "pergunta 3 (apagando a pasta do Agendador)": jp.passos_da_pergunta_3(True),
               "pergunta 3 (sem apagar a pasta do Agendador)": jp.passos_da_pergunta_3(False),
               "prova 5": jp.passos_da_prova_5()}
    for prova, passos in pedidos.items():
        assert passos, prova
        for passo in passos:
            assert windows.problemas_do_passo(asdict(passo)) == [], (prova, passo.descricao)
    assert "(" not in jp.TAREFA_DO_NAO and ")" not in jp.TAREFA_DO_NAO
    # a pergunta 3 desfaz o que a 1 e a 2 criam
    criadas = {p.dados["nome"] for p in jp.passos_da_pergunta_1() + jp.passos_da_pergunta_2()
               if p.tipo == "criar_tarefa"}
    apagadas = {p.dados["nome"] for p in jp.passos_da_pergunta_3(True) if p.tipo == "apagar_tarefa"}
    assert criadas <= apagadas
    assert any(p.tipo == "apagar_pasta_segura" for p in jp.passos_da_pergunta_3(False))
    assert any(p.tipo == "apagar_pasta_de_tarefas" for p in jp.passos_da_pergunta_3(True))
    assert not any(p.tipo == "apagar_pasta_de_tarefas" for p in jp.passos_da_pergunta_3(False))


def test_a_pergunta_1_zera_o_resultado_da_tarefa_antes_de_criar():
    """Achado 2: o resultado da tarefa de uma sessão anterior não pode enganar a prova; o passo com licença o deixa
    vazio antes de criar a tarefa (e a janela só aceita o que foi escrito depois de mandar rodar)."""
    import janela_de_prova as jp

    passos = jp.passos_da_pergunta_1()
    zerar = next(i for i, p in enumerate(passos) if p.tipo == "gravar_na_pasta_segura" and p.dados["arquivo"] == jp.RODOU)
    criar = next(i for i, p in enumerate(passos) if p.tipo == "criar_tarefa")
    assert passos[zerar].dados["texto"] == "" and zerar < criar


def test_a_janela_tem_as_seis_provas_da_sessao_a(tmp_path):
    """A janela abre (fora da tela) com uma linha por prova da sessão A, na ordem do plano."""
    import janela_de_prova as jp
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    janela = jp.montar_janela(None, tmp_path / "registro.txt")
    janela.show()
    app.processEvents()
    textos = [b.text() for b in janela.botoes]
    assert len(textos) == 6
    assert textos[1].endswith("clique Sim") and textos[2].endswith("clique Não") and "navegador" in textos[3]
    janela.dizer("linha de teste com acento: ção")
    assert "ção" in (tmp_path / "registro.txt").read_text(encoding="utf-8")
    janela.close()


def test_a_janela_nao_fecha_no_meio_de_uma_prova(tmp_path):
    """Achado 17: fechar a janela no meio de uma prova não fecha (o registro ficaria pela metade); ela pede para
    esperar e fecha depois que a prova acaba. A "prova" aqui só espera um pouco (não fala com o Windows)."""
    import janela_de_prova as jp
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    janela = jp.montar_janela(None, tmp_path / "registro.txt")
    janela.show()
    janela.rodar("espera", lambda dizer, _p, _j: time.sleep(1.5))
    app.processEvents()
    assert janela.close() is False and janela.isVisible()
    assert "Espere a prova acabar" in (tmp_path / "registro.txt").read_text(encoding="utf-8")
    fim = time.monotonic() + 15
    while any(t.isRunning() for t in janela.trabalhos) and time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.05)
    app.processEvents()
    assert janela.close() is True


def test_as_provas_sem_pergunta_dao_o_resultado_certo():
    """Prova 1 (lançar solto): o script roda depois de quem o lançou fechar. Prova 5 (a), programa que não existe:
    frase em português, sem pergunta (a parte (b), que chega ao Windows, é só da sessão à vista)."""
    import janela_de_prova as jp

    linhas: list[str] = []
    jp.prova_lancar_solto(linhas.append, None, None)
    assert any("quem o lançou" in l and l.endswith("já tinha fechado: sim") for l in linhas), linhas
    linhas.clear()
    jp.pedido_para_programa_que_nao_existe(linhas.append, None)
    assert any("FALHOU" in l and "não achei o programa" in l for l in linhas), linhas


def test_a_janela_usa_a_peca_e_nao_fala_com_o_windows_sozinha():
    """A janela importa a peça do programa (nunca uma cópia), não usa nada de dentro dela (nome com "_") e não
    importa nada que fale com o Windows por fora dela (o porteiro também barra)."""
    texto = (RAIZ / "janela_de_prova.py").read_text(encoding="utf-8")
    assert "from core import windows" in texto
    assert "windows._" not in texto
    for proibido in ("import ctypes", "import subprocess", "import winreg"):
        assert proibido not in texto
