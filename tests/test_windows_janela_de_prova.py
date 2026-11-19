"""Testes da janela de prova (`janela_de_prova.py`; plano da parte do Windows, peça 10a).

Só o que não pede licença e não chega ao Windows com pedido de licença: a janela monta (fora da tela), tem as seis
provas da sessão A, o pedido de CADA prova passa nas regras da peça antes de ir ao Windows (achado 1 de quem tentou
quebrar), a janela não fecha no meio de uma prova (achado 17), e as provas sem pergunta (lançar solto, programa que
não existe) dão o resultado certo. As provas com a pergunta do Windows (1, 2 e 3 da sessão A) e a parte (b) da prova 5
(que chega ao Windows) NÃO rodam aqui: são à vista, com o Samuel (D-767, D-785).

Seguro mexer: acrescentar casos sem pergunta. Arriscado: chamar aqui uma prova que pede a licença ou chega ao Windows.
"""

from __future__ import annotations

import json
import os
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


# ---------------------------------------------------------------------------------------------------------------------
# A segunda volta de quem tentou quebrar (19/11): as decisões da janela, sem o Windows
# ---------------------------------------------------------------------------------------------------------------------

def test_a_frase_da_pasta_do_agendador_nunca_diz_apagada_sem_ter_sido_criada():
    """Achado 6 da segunda volta: a janela dizia "foi apagada" quando a pasta nem tinha sido criada. A frase compara
    antes e agora, e só diz o que leu."""
    import janela_de_prova as jp

    for existia in (True, False, None):
        for agora in (True, False, None):
            assert "foi apagada" not in jp.frase_da_pasta_do_agendador(existia, agora)
    assert "está como estava" in jp.frase_da_pasta_do_agendador(False, False)
    assert "ELA FICOU" in jp.frase_da_pasta_do_agendador(False, True)
    assert "NÃO EXISTE MAIS" in jp.frase_da_pasta_do_agendador(True, False)


def test_a_decisao_de_apagar_a_pasta_do_agendador():
    """Achado 6: a pasta do programa no Agendador só é apagada pela pergunta 3 se não existia antes da prova; se
    existia, ou se não se sabe, fica."""
    import janela_de_prova as jp

    assert jp.apagar_a_pasta_do_agendador(False) is True
    assert jp.apagar_a_pasta_do_agendador(True) is False
    assert jp.apagar_a_pasta_do_agendador(None) is False


def _pergunta_3_sem_o_windows(monkeypatch, tmp_path, existia):
    """Roda a pergunta 3 com o pedido de licença trocado por um que anota o pedido e responde "Não" (nenhuma pergunta
    do Windows), o estado de antes num arquivo do teste e as leituras da pasta do Agendador dizendo "não existe"."""
    import janela_de_prova as jp
    from core import windows

    estado = tmp_path / "antes.json"
    if existia is not None:
        estado.write_text(json.dumps({"pasta_do_agendador_existia": existia}), encoding="utf-8")
    pedidos = []

    def pedir(passos, **opcoes):
        """Anota o pedido e responde "Não"."""
        pedidos.append((passos, opcoes))
        return windows.Resposta(windows.DISSE_NAO, "você disse Não; nada mudou")

    monkeypatch.setattr(jp, "ESTADO_DE_ANTES", estado)
    monkeypatch.setattr(jp, "ESPERA_ANTES_DA_PERGUNTA_3_S", 0)
    monkeypatch.setattr(windows, "pedir_licenca", pedir)
    monkeypatch.setattr(windows, "pasta_de_tarefas_existe", lambda: False)
    linhas: list[str] = []
    jp.prova_pergunta_3(linhas.append, None, None)
    return pedidos, linhas


def test_a_pergunta_3_pede_ate_o_fim_e_a_pasta_do_agendador_so_se_a_prova_a_criou(monkeypatch, tmp_path):
    """Mutações A1c e A6 da segunda volta: a pergunta 3 pede "ir até o fim" e inclui apagar a pasta do Agendador só
    quando o estado de antes diz que ela não existia; a frase do fim não diz "foi apagada"."""
    pedidos, linhas = _pergunta_3_sem_o_windows(monkeypatch, tmp_path, existia=False)
    passos, opcoes = pedidos[0]
    assert opcoes.get("ate_o_fim") is True
    assert [p.tipo for p in passos].count("apagar_pasta_de_tarefas") == 1
    assert any("não existia antes da prova e não existe agora" in l for l in linhas)
    assert not any("foi apagada" in l for l in linhas)
    pedidos, _ = _pergunta_3_sem_o_windows(monkeypatch, tmp_path, existia=True)
    assert "apagar_pasta_de_tarefas" not in [p.tipo for p in pedidos[0][0]]


def _pergunta_1_sem_o_windows(monkeypatch, tmp_path, resultado_novo: bool):
    """Roda a pergunta 1 sem o Windows: o pedido de licença responde "deu certo", a tarefa "existe", e o resultado
    da tarefa numa pasta do teste: um arquivo velho (da vez anterior) e, se `resultado_novo`, um novo escrito quando a
    tarefa "roda"."""
    import janela_de_prova as jp
    from core import windows

    rodou = tmp_path / jp.RODOU
    rodou.write_text(windows.SID_SISTEMA + "|VELHO|01:02:03", encoding="utf-8")
    velho = time.time() - 3600
    os.utime(rodou, (velho, velho))

    def rodar(_nome, limite_s=60):
        """A tarefa "roda": escreve o resultado novo, se o teste pediu."""
        if resultado_novo:
            rodou.write_text(windows.SID_SISTEMA + "|NOVO|10:20:30", encoding="utf-8")
        return windows.Resposta(windows.DEU_CERTO, dados={"saida": "ÊXITO"})

    monkeypatch.setattr(jp, "ESTADO_DE_ANTES", tmp_path / "antes.json")
    monkeypatch.setattr(jp, "ESPERA_DO_RESULTADO_DA_TAREFA_S", 2)
    monkeypatch.setattr(windows, "pasta_de_tarefas_existe", lambda: False)
    monkeypatch.setattr(windows, "pedir_licenca", lambda passos, **o: windows.Resposta(windows.DEU_CERTO))
    monkeypatch.setattr(windows, "conferir_pasta_segura", lambda nome: windows.Resposta(windows.FALHOU,
                                                                                      dados={"existe": False}))
    monkeypatch.setattr(windows, "ler_tarefa", lambda nome, limite_s=60: windows.Tarefa(nome, True, True))
    monkeypatch.setattr(windows, "rodar_tarefa", rodar)
    monkeypatch.setattr(windows, "pasta_segura", lambda nome: tmp_path)
    linhas: list[str] = []
    jp.prova_pergunta_1(linhas.append, None, None)
    return linhas


def test_a_pergunta_1_nao_aceita_o_resultado_velho_da_tarefa(monkeypatch, tmp_path):
    """Mutação A2 da segunda volta: a janela só aceita o resultado da tarefa escrito DEPOIS de mandar rodar. Com só o
    arquivo velho, diz que a tarefa não escreveu; com o novo, diz a hora nova."""
    linhas = _pergunta_1_sem_o_windows(monkeypatch, tmp_path, resultado_novo=False)
    assert any("não escreveu que rodou" in l for l in linhas) and not any("VELHO" in l for l in linhas)
    linhas = _pergunta_1_sem_o_windows(monkeypatch, tmp_path, resultado_novo=True)
    assert any("rodou às 10:20:30" in l and "é o sistema, certo" in l for l in linhas)
