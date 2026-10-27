"""As provas de comportamento da etapa 7 da obra de 26/10/2026: o "está certo" com resposta e os
avisos (CLAUDE.md §11, regra 4; Livro de decisões, docs/plano/DECISOES.md).

Cada teste diz a decisão e as palavras do Samuel. Aparência não conta: o que se mede é o projeto
gravado (conferida, avisos aceitos), a página/folha da vez, o tique da miniatura, os números que
cada lugar mostra, os botões que existem no cartão e o que o clique deles faz.

  Plano de 26/10, etapa 7 (aprovado): "'está certo' com resposta [...]: tique, contador certo,
      próxima dúvida (1.1); botões no cartão do aviso (1.8); um número só de dúvidas (5.5)".
  D-010 / P-101: o exemplo dele, "a folha fica conferida, tique na miniatura, contador sobe, vai
      para a próxima dúvida". Sessão 1, 1-5: "eu clico no esta certo e não acontece nada."
  Sessão 0, 0-7: "tem os avisos mas não tem como apertar para fazer ele sumir ou alguma sugestão
      de como se livrar dele." · D-268: "(a) Botão no aviso". 0-8: o clique no cartão levou ao
      Dividir, "sem os botões do aviso".
  D-285: "A janela de salvar passa a contar as páginas com aviso pendente". Teste do Kaique (26/10):
      "356 páginas que você não conferiu" depois de "nada pendente".
  D-259 / P-095: "abrir todas as páginas em tela cheia (como no UPDF) mostrando as que precisam de
      atenção" (no desenho decidido, rodada 13, "ver as N em tela cheia" no pé do "Para revisar").
  D-521: "No alto do painel \"Para revisar\" e no livro aberto da tela inicial (recomendo)".
  D-543: o aviso "Parte do impresso fica de fora" com "ver no Mover" e "está bom assim".
  D-497: a tela chama, por trás, a conta da etapa 9d (core.pipeline.medir_o_em_branco) depois de
      mexer na divisão; enquanto a 9d não está na obra, a prova usa uma conta de mentira.

Livro sintético (papel amarelado com "texto"), dividido pelo Automático como o Kaique faz.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import analise  # noqa: E402
from core import automatico as A  # noqa: E402
from core import avisos as avisos_do_livro  # noqa: E402

DPI = 100
AMARELADO = (170, 215, 235)            # BGR: papel velho
FOLHAS = 5                             # 10 páginas depois de dividir


# --- o livro de teste -------------------------------------------------------------

def _pagina(largura: int = 420, altura: int = 600) -> np.ndarray:
    img = np.full((altura, largura, 3), AMARELADO, np.uint8)
    for y in range(140, altura - 120, 30):
        img[y:y + 9, 70:largura - 70] = 25
    return img


def _pdf(caminho: Path, folhas: int) -> str:
    doc = fitz.open()
    for _f in range(folhas):
        img = np.concatenate([_pagina(), _pagina()], axis=1)
        ok, buffer = cv2.imencode(".png", img)
        assert ok
        largura, altura = img.shape[1] / DPI * 72, img.shape[0] / DPI * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    import projetos

    projetos_dir = tmp_path / "projetos"
    projetos_dir.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: projetos_dir)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "dados"))
    return tmp_path


@pytest.fixture
def janela(app, pasta):
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    yield janela
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    if janela.previas is not None:
        janela.previas.parar()
    janela.close()


def _assentar(vezes: int = 6) -> None:
    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        QApplication.processEvents()


def _esperar(condicao, segundos: float = 30.0, motivo: str = "") -> None:
    import time

    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar(2)
        if condicao():
            return
        time.sleep(0.02)
    raise AssertionError(f"não aconteceu a tempo: {motivo}")


def _dividido(janela, tmp_path: Path):
    """O caminho do Kaique: abrir o livro e rodar o Automático só com "Dividir"; depois, nenhum
    aviso em lugar nenhum (cada prova põe os seus)."""
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", FOLHAS))
    estado = janela.estado_do_automatico
    estado.marcadas = {A.DIVIDIR}
    estado.alcance = "livro"
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    tela = janela.tela_conferir
    assert len(janela.projeto.paginas) == 2 * FOLHAS
    # a medida por trás do livro novo (D-284) põe os avisos dela quando termina: espera, para
    # ela não trocar os avisos de cada prova no meio
    _esperar(lambda: getattr(janela, "medida_ao_abrir", None) is None, motivo="a medida ao abrir")
    medida = getattr(janela, "medida_do_livro", None)
    if medida is not None:
        _esperar(lambda: not medida.isRunning(), motivo="a medida do livro")
    _assentar(10)
    _sem_avisos(janela)
    return tela


def _sem_avisos(janela) -> None:
    for item in list(janela.projeto.folhas) + list(janela.projeto.paginas):
        item.alertas, item.revisada, item.alertas_aceitos = [], False, []
    janela.projeto.observacoes = []


def _na_pagina(tela, indice: int) -> None:
    """A página `indice` numa ferramenta de página (a Mão), como o Kaique depois de dividir."""
    tela.escolher_ferramenta("mao")
    tela.ir_para_pagina(indice)
    tela.atualizar()
    _assentar()


def _no_dividir(tela, folha: int) -> None:
    tela.escolher_ferramenta("dividir")
    assert tela.trabalha_com_folhas
    tela._ir_para(folha)
    _assentar()


def _gravado(janela) -> dict:
    import json

    import projetos

    projetos.esperar_gravacoes()
    janela._salvar_estado() if hasattr(janela, "_salvar_estado") else None
    projetos.esperar_gravacoes()
    pasta = Path(janela.resumo.pasta)
    return json.loads((pasta / "projeto.json").read_text(encoding="utf-8"))


# --- 1.1 / D-010 / P-101: o "está certo" responde -----------------------------------

def test_p101_esta_certo_na_pagina_conferida_tique_contador_e_proxima_duvida(janela, tmp_path):
    """Lista única 1.1 e sessão 1, 1-5 ("eu clico no esta certo e não acontece nada"); D-010, o
    exemplo do Samuel: "a folha fica conferida, tique na miniatura, contador sobe, vai para a
    próxima dúvida". Antes: o clique gravava, e nada na tela mudava (a página, a miniatura e o
    contador ficavam iguais)."""
    tela = _dividido(janela, tmp_path)
    for indice in (2, 6):
        janela.projeto.paginas[indice].alertas = [analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
    _na_pagina(tela, 2)
    assert "0 de 10 conferidas" in tela.rotulo_do_livro.text()
    assert not tela.tira._miniaturas[2].conferida

    tela.botao_esta_certo.click()
    _assentar()

    assert janela.projeto.paginas[2].revisada, "a página não ficou conferida"
    assert tela.tira._miniaturas[2].conferida, "a miniatura não ganhou o tique"
    assert "1 de 10 conferidas" in tela.rotulo_do_livro.text(), "o contador não subiu"
    assert tela.indice_pagina == 6, "não foi para a próxima dúvida"
    assert any(a.tipo == "revisar" for a in janela.acoes.feitas), "não ficou no desfazer"


def test_esta_certo_no_dividir_conta_folhas_e_vai_para_a_proxima_folha_com_duvida(janela, tmp_path):
    """Lista única 1.1 e 5.4 (sessão 0, 0-3; mapa nº 8): no Dividir se confere a FOLHA, e o
    rodapé contava PÁGINAS ("0 de 360 conferidas" não mexia). Agora: a folha fica conferida, a
    miniatura dela ganha o tique, o contador (de folhas, como o "folha N de M" ao lado) sobe e a
    tela vai à próxima folha com dúvida."""
    tela = _dividido(janela, tmp_path)
    janela.projeto.folhas[3].alertas = [analise.LOMBADA_INCERTA]
    _no_dividir(tela, 0)
    assert f"0 de {FOLHAS} conferidas" in tela.rotulo_do_livro.text()

    tela.botao_esta_certo.click()
    _assentar()

    assert janela.projeto.folhas[0].revisada
    assert tela.tira._miniaturas[0].conferida, "a miniatura da folha não ganhou o tique"
    assert f"1 de {FOLHAS} conferidas" in tela.rotulo_do_livro.text(), "o contador não subiu"
    assert tela.indice_folha == 3, "não foi para a próxima folha com dúvida"


def test_esta_certo_sem_outra_duvida_fica_e_mostra_o_tique(janela, tmp_path):
    """Sem outra dúvida no livro, a tela fica onde está (não anda à toa), e o tique e o contador
    mostram que o clique pegou."""
    tela = _dividido(janela, tmp_path)
    _na_pagina(tela, 4)
    tela.botao_esta_certo.click()
    _assentar()
    assert tela.indice_pagina == 4
    assert tela.tira._miniaturas[4].conferida
    assert "1 de 10 conferidas" in tela.rotulo_do_livro.text()


# --- 5.5 / D-285: um número só, e o aviso da folha não fica escondido ---------------

def _numeros(janela, tela) -> dict:
    """O número de dúvidas em cada lugar onde ele aparece."""
    import re

    import projetos
    from ui.janela_confirmar import JanelaConfirmar

    tela.atualizar()
    tela._atualizar_paineis()
    _assentar()
    rodape = int(re.search(r"(\d+) com dúvida", tela.rotulo_do_livro.text()).group(1))
    frase = avisos_do_livro.frase_de_quantos(avisos_do_livro.pendentes_do_livro(janela.projeto),
                                             janela.projeto)
    antes = re.search(r"(\d+) página", frase)
    confirmar = JanelaConfirmar(janela.projeto, "livro.pdf", janela)
    salvar = confirmar._nao_conferidas()
    confirmar.deleteLater()
    tela.abrir_todas_as_paginas()
    grade = int(re.search(r"\((\d+)\)", tela.todas.botao_atencao.text()).group(1))
    tela._voltar_das_todas(None)
    resumo = projetos.atualizar(janela.resumo, janela.projeto)
    return {
        "rodapé": rodape,
        "Para revisar": tela.paineis.para_revisar._paginas,
        "linhas do Para revisar": tela.paineis.para_revisar.lista.count(),
        "Antes de processar": int(antes.group(1)) if antes else 0,
        "janela de salvar": salvar,
        "grade (só as que precisam)": grade,
        "livro aberto (Para revisar: N)": resumo.para_revisar,
    }


def test_5_5_um_numero_so_em_todo_lugar_com_os_avisos_da_folha(janela, tmp_path):
    """Lista única 5.5: "Três lugares contam as dúvidas, cada um dá um número, e os avisos de
    folha ficam escondidos". D-285 (`pr-contagens`): "A janela de salvar passa a contar as
    páginas com aviso pendente". Folha 1 (páginas 3 e 4) com "Qualidade baixa" e página 8 com
    um aviso: 3 páginas com dúvida, o MESMO 3 no rodapé, no "Para revisar" (uma linha por
    página), na "Antes de processar", na janela de salvar, na grade e no livro aberto. Antes:
    painel 1 (a folha escondida), janela de salvar 10 (toda página sem "está certo")."""
    tela = _dividido(janela, tmp_path)
    janela.projeto.folhas[1].alertas = [analise.RESOLUCAO_BAIXA]
    janela.projeto.paginas[7].alertas = [analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
    _na_pagina(tela, 0)
    numeros = _numeros(janela, tela)
    assert set(numeros.values()) == {3}, numeros


def test_kaique_356_nao_conferidas_depois_de_nada_pendente(janela, tmp_path):
    """Teste do Kaique (26/10): depois de "está bom em tudo" o painel dizia "nada pendente" e a
    janela final cobrava "356 páginas que você não conferiu". Agora a janela de salvar conta as
    páginas com aviso pendente (D-285): depois de "está bom em tudo", 0 em todo lugar."""
    from ui.janela_confirmar import JanelaConfirmar

    tela = _dividido(janela, tmp_path)
    janela.projeto.folhas[1].alertas = [analise.LOMBADA_INCERTA]
    janela.projeto.paginas[7].alertas = [analise.CONTAS_DO_ENDIREITAR_DISCORDAM]
    _na_pagina(tela, 0)
    tela.paineis.para_revisar.botao_esta_bom_em_tudo.click()
    _assentar()
    assert tela.paineis.para_revisar.frase.text() == "nada pendente"
    confirmar = JanelaConfirmar(janela.projeto, "livro.pdf", janela)
    assert confirmar._nao_conferidas() == 0
    assert confirmar.aviso_conferir.isHidden(), "a janela de salvar ainda cobra páginas"
    confirmar.deleteLater()
    assert set(_numeros(janela, tela).values()) == {0}


def test_aviso_da_folha_aparece_na_pagina_com_o_botao_e_o_esta_certo_responde(janela, tmp_path):
    """5.5 ("os avisos de folha ficam escondidos"): o aviso de uma folha aparece na faixa das
    páginas dela, com o botão; o "está certo" de cada página responde por ele ali, e quando as
    duas páginas da folha estão conferidas o aviso sai também da "Antes de processar"."""
    tela = _dividido(janela, tmp_path)
    janela.projeto.folhas[1].alertas = [analise.RESOLUCAO_BAIXA]
    _na_pagina(tela, 2)
    titulo = analise.descrever(analise.RESOLUCAO_BAIXA)
    assert titulo.mensagem in tela.texto_faixa.text(), "o aviso da folha não aparece na página"
    assert tela.botao_sugestao.isVisibleTo(tela) and tela.botao_sugestao.text() == titulo.acao
    assert avisos_do_livro.quantas_com_duvida(janela.projeto) == 2

    tela.botao_esta_certo.click()
    _assentar()
    assert tela.indice_pagina == 3, "não foi para a outra página da folha (a próxima dúvida)"
    assert avisos_do_livro.quantas_com_duvida(janela.projeto) == 1
    assert titulo.mensagem in tela.texto_faixa.text()
    tela.botao_esta_certo.click()
    _assentar()
    assert avisos_do_livro.quantas_com_duvida(janela.projeto) == 0
    assert avisos_do_livro.pendentes_do_livro(janela.projeto) == []


# --- 1.8 / D-268 / D-543: o cartão do aviso com os botões -----------------------------

def test_1_8_cartao_do_aviso_tem_os_botoes_e_o_clique_faz_o_que_o_aviso_diz(janela, tmp_path):
    """Lista única 1.8; sessão 0, 0-7: "tem os avisos mas não tem como apertar para fazer ele
    sumir ou alguma sugestão de como se livrar dele."; D-268: "(a) Botão no aviso". D-543: o
    aviso "Parte do impresso fica de fora" com "ver no Mover" e "está bom assim". O cartão da
    página da vez no "Para revisar" tem os mesmos botões da faixa, e o clique faz o mesmo."""
    tela = _dividido(janela, tmp_path)
    janela.projeto.paginas[5].alertas = [analise.IMPRESSO_DE_FORA]
    _na_pagina(tela, 5)
    tela.paineis.abrir("revisar")
    tela._atualizar_paineis()
    _assentar()
    painel = tela.paineis.para_revisar
    textos = [b.text() for b in painel.botoes_do_cartao if b.isVisibleTo(painel)]
    assert textos == ["ver no Mover", "está bom assim"], textos

    painel.botoes_do_cartao[0].click()
    _assentar()
    assert tela.aba_atual == "mover" and tela.indice_pagina == 5, "'ver no Mover' não levou ao Mover"

    # (no Mover a conta do impresso de fora é refeita e, sem nada movido, o aviso some sozinho -
    # D-273; põe de novo para provar o segundo botão)
    janela.projeto.paginas[5].alertas = [analise.IMPRESSO_DE_FORA]
    _na_pagina(tela, 5)
    tela._atualizar_paineis()
    _assentar()
    assert [b.text() for b in painel.botoes_do_cartao] == ["ver no Mover", "está bom assim"]
    painel.botoes_do_cartao[1].click()           # "está bom assim"
    _assentar()
    assert not avisos_do_livro.avisos_da_pagina(janela.projeto, 5), "o aviso não saiu"
    assert painel._paginas == 0 and not painel.botoes_do_cartao


def test_0_8_clicar_no_cartao_estando_no_dividir_mostra_o_aviso_da_pagina(janela, tmp_path):
    """Sessão 0, 0-8: clicou no cartão "Página 7 — Parece em branco" estando no Dividir; o
    programa foi à folha 4, mas a faixa continuou com "Achei a lombada..." e sem os botões. Agora
    o clique sai do Dividir para a página (D-007/D-501: "ver" num aviso que não é da divisão leva
    à página), e o aviso aparece com os botões, na faixa e no cartão."""
    tela = _dividido(janela, tmp_path)
    janela.projeto.paginas[6].alertas = [analise.IMPRESSO_DE_FORA]
    _no_dividir(tela, 0)
    tela.paineis.abrir("revisar")
    tela._atualizar_paineis()
    _assentar()
    painel = tela.paineis.para_revisar
    item = next(painel.lista.item(i) for i in range(painel.lista.count())
                if painel.lista.item(i).text() == "Página 7")
    painel._clicou_na_lista(item)
    _assentar()
    assert not tela.trabalha_com_folhas, "ficou no Dividir"
    assert tela.indice_pagina == 6
    assert analise.descrever(analise.IMPRESSO_DE_FORA).mensagem in tela.texto_faixa.text()
    assert [b.text() for b in painel.botoes_do_cartao] == ["ver no Mover", "está bom assim"]


def test_d501_cartao_com_aviso_da_divisao_vai_ao_dividir(janela, tmp_path):
    """D-500/D-501: a folha com o corte duvidoso vai para o "Para revisar" como "Lombada
    incerta" (antes nem aparecia no painel), e o clique no cartão leva ao Dividir, na folha."""
    tela = _dividido(janela, tmp_path)
    janela.projeto.folhas[2].alertas = [analise.LOMBADA_INCERTA]
    _na_pagina(tela, 0)
    tela._atualizar_paineis()
    painel = tela.paineis.para_revisar
    nomes = [painel.lista.item(i).text() for i in range(painel.lista.count())]
    assert nomes == ["Página 5", "Página 6"], nomes
    painel._clicou_na_lista(painel.lista.item(0))
    _assentar()
    assert tela.trabalha_com_folhas and tela.indice_folha == 2


# --- D-259 / P-095: "ver as N em tela cheia" -----------------------------------------

def test_d259_ver_as_n_em_tela_cheia_abre_so_as_que_precisam(janela, tmp_path):
    """D-259 (05/10): "abrir todas as páginas em tela cheia (como no UPDF) mostrando as que
    precisam de atenção"; rodada 2: "Aprovado"; desenho da rodada 13: "ver as N em tela cheia" no
    pé do "Para revisar". O botão diz o número de todo lugar e abre a grade só com elas."""
    tela = _dividido(janela, tmp_path)
    janela.projeto.folhas[1].alertas = [analise.RESOLUCAO_BAIXA]
    janela.projeto.paginas[8].alertas = [analise.IMPRESSO_DE_FORA]
    _na_pagina(tela, 0)
    tela.paineis.abrir("revisar")
    tela._atualizar_paineis()
    _assentar()
    botao = tela.paineis.para_revisar.botao_tela_cheia
    assert botao.isVisibleTo(tela.paineis.para_revisar)
    assert botao.text() == "ver as 3 em tela cheia"
    botao.click()
    _assentar()
    assert tela.pilha_da_tela.currentWidget() is tela.todas
    assert tela.todas.so_atencao
    assert [i.indice for g in tela.todas._grupos() for i in g] == [2, 3, 8]
    assert tela.todas.botao_atencao.text().endswith("(3)")


# --- D-521: os avisos do livro inteiro, no alto do painel e no livro aberto ----------

def test_d521_avisos_do_livro_no_alto_do_para_revisar_e_no_livro_aberto(janela, tmp_path):
    """D-521 (Central `pd-avisos-do-livro`): "No alto do painel \"Para revisar\" e no livro
    aberto da tela inicial (recomendo)". Antes: só a faixa escura aparecia no painel; os outros
    fatos do livro ("o livro inteiro é colorido") moravam num rótulo escondido, e o livro aberto
    não dizia nada."""
    import projetos

    tela = _dividido(janela, tmp_path)
    cor = analise.OBSERVACOES[analise.COR]
    faixa = analise.OBSERVACOES[analise.TAMANHO_DIFERENTE]
    janela.projeto.observacoes = [cor, faixa]
    _na_pagina(tela, 0)
    tela._atualizar_paineis()
    painel = tela.paineis.para_revisar
    assert painel.frase_do_livro.isVisibleTo(painel)
    assert cor in painel.frase_do_livro.text() and faixa in painel.frase_do_livro.text()

    resumo = projetos.atualizar(janela.resumo, janela.projeto)
    livro_aberto = janela.tela_inicio.livro_aberto
    livro_aberto.mostrar(resumo)
    assert livro_aberto.avisos_do_livro.text() == painel.frase_do_livro.text()
    assert not livro_aberto.avisos_do_livro.isHidden()


def test_livro_aberto_ver_todas_conta_as_mesmas_duvidas(janela, tmp_path):
    """Lista única 5.5: o "Ver todas as páginas" do livro aberto dizia "(0)". Agora "só as que
    precisam de atenção (N)" dá o número do "Para revisar: N" (folha do PDF com as duas páginas
    com dúvida conta 2)."""
    import projetos

    tela = _dividido(janela, tmp_path)
    janela.projeto.folhas[1].alertas = [analise.RESOLUCAO_BAIXA]
    janela.projeto.paginas[8].alertas = [analise.IMPRESSO_DE_FORA]
    _na_pagina(tela, 0)
    resumo = projetos.atualizar(janela.resumo, janela.projeto)
    livro_aberto = janela.tela_inicio.livro_aberto
    livro_aberto.mostrar(resumo)
    assert livro_aberto.para_revisar.text() == "Para revisar: 3"
    livro_aberto._ver_todas()
    assert livro_aberto.todas.botao_atencao.text().endswith("(3)")
    livro_aberto.todas.definir_so_atencao(True)
    assert [i.folha for g in livro_aberto.todas._grupos() for i in g] == [1, 4]
    livro_aberto.fechar()


# --- D-497: a tela pronta para a conta da etapa 9d -----------------------------------

def test_d497_mexer_na_divisao_chama_por_tras_a_conta_do_em_branco(janela, tmp_path, monkeypatch):
    """D-497: "Página que fica branca depois de mudar a divisão ganha o aviso 'Parece em
    branco' [...]". A conta é do núcleo (etapa 9d, core.pipeline.medir_o_em_branco); a tela a
    chama por trás depois de mover a linha, e o aviso aparece no "Para revisar". Aqui com uma
    conta de mentira (a da 9d ainda não está nesta obra)."""
    from core import pipeline

    chamadas = []

    def medir(_doc, _projeto, pagina):
        chamadas.append(pagina.indice)
        if pagina.indice == 5 and analise.EM_BRANCO not in pagina.alertas:
            pagina.alertas = pagina.alertas + [analise.EM_BRANCO]
            return True
        return False

    monkeypatch.setattr(pipeline, "medir_o_em_branco", medir, raising=False)
    tela = _dividido(janela, tmp_path)
    _no_dividir(tela, 2)
    tela._mover_corte(0.9)
    _esperar(lambda: tela.paineis.para_revisar._paginas == 1, motivo="o aviso não chegou ao painel")
    assert sorted(set(chamadas)) == [4, 5]
    assert tela.paineis.para_revisar.lista.item(0).text() == "Página 6"
