"""A tela cheia dos filtros (etapa 6 do layout; rodada 11, 601 A; rodada 10, 503; rodada 14, 904 A)."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from tests.test_misto_consertos import conferir_original, pasta  # noqa: F401, E402 - fixtures
from tests.test_gravura_na_aba_marcar import app  # noqa: F401, E402 - fixture


def _tela_cheia(tela):
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia
    return FiltrosEmTelaCheia(tela)


def test_abre_pelo_icone_do_titulo_do_painel(conferir_original, monkeypatch):  # noqa: F811
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

    abertas = []
    monkeypatch.setattr(FiltrosEmTelaCheia, "exec", lambda self: abertas.append(self) or 0)
    conferir_original.paineis.filtro_da_pagina.botao_tela_cheia.click()
    assert len(abertas) == 1
    dialogo = abertas[0]
    assert dialogo.titulo.text() == "Filtros da página 1"
    assert list(dialogo.cartoes) == dialogo.filtros and len(dialogo.filtros) >= 4
    assert not dialogo.chave_comparar.isChecked(), "a chave começa desligada (601 A)"


def test_escolher_nao_muda_a_pagina_e_usar_muda(conferir_original):  # noqa: F811
    from core.filtros import MELHORAR, ORIGINAL

    tela = conferir_original
    pagina = tela.projeto.paginas[0]
    assert pagina.filtro == ORIGINAL
    dialogo = _tela_cheia(tela)
    dialogo.escolher(MELHORAR)
    assert pagina.filtro == ORIGINAL, "escolher na tela cheia só mostra"
    assert dialogo.botao_usar.text() == "Usar Melhorar"
    dialogo._ajuste_mudou(80)
    dialogo.usar()
    assert pagina.filtro == MELHORAR and pagina.clareza_melhorar == 80
    tela.desfazer()
    assert pagina.clareza_melhorar != 80
    tela.desfazer()
    assert pagina.filtro == ORIGINAL


def test_aplicar_em_todas(conferir_original):  # noqa: F811
    from core.filtros import MAGICO_PRO

    tela = conferir_original
    dialogo = _tela_cheia(tela)
    dialogo.escolher(MAGICO_PRO)
    dialogo.botoes_alcance["todas"].click()
    dialogo.usar()
    assert all(p.filtro == MAGICO_PRO for p in tela.projeto.paginas)


def test_comparar_com_o_original_sem_outro_filtro_avisa(conferir_original):  # noqa: F811
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    dialogo = _tela_cheia(conferir_original)
    dialogo.escolher(ORIGINAL)
    dialogo.chave_comparar.setChecked(True)
    assert "outro filtro" in dialogo.vista.aviso and not dialogo.vista.comparando
    dialogo.escolher(PRETO_E_BRANCO)
    assert dialogo.vista.aviso == ""
    dialogo.reject()


def test_fechar_sem_mudar_nao_muda(conferir_original):  # noqa: F811
    from core.filtros import MELHORAR

    tela = conferir_original
    antes = [p.filtro for p in tela.projeto.paginas]
    dialogo = _tela_cheia(tela)
    dialogo.escolher(MELHORAR)
    dialogo.botao_sem_mudar.click()
    assert [p.filtro for p in tela.projeto.paginas] == antes
    assert not tela.acoes.pode_desfazer


def test_no_melhorar_nao_aparece_o_jeito_do_preto_e_branco(conferir_original):  # noqa: F811
    """Verificador, 21/10/2026: no Melhorar não pode aparecer o rótulo da lista
    do Preto e branco (o "Algoritmo:" de antes) sem nada ao lado. No painel
    Filtro a lista mora em "Mais ajustes". Desde a junção com a Fase 2
    (22/10/2026) "Mais ajustes" aparece também no Melhorar, com "Letra clara em
    fundo escuro" (2.9) e "Reduzir cores" (2.11), mas sem a lista do preto e
    branco nem "Letras com a cor delas"."""
    from PySide6.QtWidgets import QApplication, QLabel

    from core.filtros import MELHORAR, PRETO_E_BRANCO

    tela = conferir_original
    tela.resize(1280, 657)
    tela.show()
    tela.paineis.abrir("filtro")
    tela._escolher_filtro(MELHORAR)
    QApplication.processEvents()
    painel = tela.paineis.filtro_da_pagina
    visiveis = [r.text() for r in painel.findChildren(QLabel) if r.isVisible()]
    assert not any("Algoritmo" in t or "Jeito do preto" in t for t in visiveis), visiveis
    assert not painel.partes["mais"].isHidden()
    assert tela.seletor_algoritmo_pb.isHidden() and tela.caixa_letras_com_a_cor.isHidden()
    assert not tela.caixa_claro_no_escuro.isHidden() and not tela.caixa_reduzir_cores.isHidden()
    tela._escolher_filtro(PRETO_E_BRANCO)
    QApplication.processEvents()
    assert not painel.partes["mais"].isHidden()
    tela.hide()


# --- Todas as opções na tela cheia (Samuel, 22/10/2026, quadro l67-tela-cheia) --------
# "esse aqui é para mostrar só o antes e depois? mas no programa vai aparecer as opções dos
# filtros né? o agente de layout fez já as opções de preto e branco que trouxemos do scan?"
# e "faça o recomendado".

def _esperar_a_imagem(dialogo, filtro, segundos=90.0):
    """A página grande da tela cheia no `filtro`, esperando ela chegar."""
    import time

    from PySide6.QtWidgets import QApplication

    fim = time.time() + segundos
    while time.time() < fim:
        img = dialogo._imagem(filtro)
        if img is not None:
            return img
        QApplication.processEvents()
        time.sleep(0.05)
    return None


def _aquecer(tela):
    """Desenha a página 1 uma vez antes da tela cheia: a primeira vez que o core
    desenha uma página ele grava nela a geometria das zonas, e essa primeira sai
    umas dezenas de pixels diferente das seguintes (achado de 22/10/2026, do
    core, fora da tela). Assim a cópia da tela cheia e a do teste partem da
    mesma página."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina

    doc = abrir_pdf(tela.projeto.caminho_entrada)
    try:
        renderizar_pagina(doc, tela.projeto, tela.projeto.paginas[0], dpi=60)
    finally:
        doc.close()


def test_mostra_todas_as_opcoes_do_filtro_escolhido(conferir_original):  # noqa: F811
    """No Preto e branco: "Só as letras", "Limpar a sujeira" e "Mais ajustes"
    (o jeito do preto e branco com os dez do ScanTailor, "Letra clara em fundo
    escuro", "Letras com a cor delas", "Reduzir cores"), com os nomes do painel;
    nos outros filtros com ajuste, "Letra clara" e "Reduzir cores"."""
    from core import preto_e_branco_scantailor
    from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO

    tela = conferir_original
    dialogo = _tela_cheia(tela)
    dialogo.escolher(PRETO_E_BRANCO)
    partes = dialogo.partes_das_opcoes
    assert not any(p.isHidden() for p in partes.values())
    dados = [dialogo.seletor_algoritmo_pb.itemData(i) for i in range(dialogo.seletor_algoritmo_pb.count())]
    assert all(c in dados for c in preto_e_branco_scantailor.CODIGOS), "os dez do ScanTailor (2.8)"
    nomes = {c: dialogo.caixas[c].text() for c in dialogo.caixas}
    assert nomes == {"claro_no_escuro": tela.caixa_claro_no_escuro.text(),
                     "letras_com_a_cor": tela.caixa_letras_com_a_cor.text(),
                     "reduzir_cores": tela.caixa_reduzir_cores.text()}, "os mesmos nomes do painel"
    assert not any(c.isHidden() for c in dialogo.caixas.values())
    assert not any(c.isChecked() for c in dialogo.caixas.values()), "desligadas de fábrica"
    dialogo.escolher(MELHORAR)
    assert partes["Só as letras"].isHidden() and partes["Limpar a sujeira"].isHidden()
    assert not partes["Mais ajustes"].isHidden()
    assert dialogo.seletor_algoritmo_pb.isHidden() and dialogo.caixas["letras_com_a_cor"].isHidden()
    assert not dialogo.caixas["claro_no_escuro"].isHidden() and not dialogo.caixas["reduzir_cores"].isHidden()
    dialogo.escolher(ORIGINAL)
    assert all(p.isHidden() for p in partes.values()), "o Original não tem opções"
    dialogo.reject()


def test_a_pagina_da_tela_cheia_e_a_que_sai(conferir_original):  # noqa: F811
    """O que se vê é o que sai: com opções mexidas na tela cheia (o ajuste, um
    jeito do ScanTailor, "Limpar a sujeira", "Reduzir cores"), a página grande
    é igual, ponto por ponto, à que o programa gera com essas opções
    (core.pipeline.renderizar_com_filtro) e à página depois de "Usar" (antes,
    21/10, o ajuste mexido mostrava a página sem o "Só as letras")."""
    from dataclasses import replace

    import numpy as np

    from core import pontinhos_scantailor as pontinhos
    from core import preto_e_branco_scantailor
    from core.filtros import PRETO_E_BRANCO
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_com_filtro, renderizar_pagina
    from ui.widgets.filtros_tela_cheia import DPI_DA_TELA_CHEIA

    tela = conferir_original
    pagina = tela.projeto.paginas[0]
    _aquecer(tela)
    dialogo = _tela_cheia(tela)
    dialogo.escolher(PRETO_E_BRANCO)
    jeito = preto_e_branco_scantailor.CODIGOS[1]
    limpeza = next(c for c in pontinhos.ESCOLHAS if c != pontinhos.escolha_da_pagina(tela.projeto, pagina))
    dialogo._ajuste_mudou(70)
    dialogo.seletor_algoritmo_pb.setCurrentIndex(dialogo.seletor_algoritmo_pb.findData(jeito))
    dialogo.seletor_pontinhos.setCurrentIndex(dialogo.seletor_pontinhos.findData(limpeza))
    dialogo.caixas["reduzir_cores"].setChecked(True)
    assert dialogo.opcoes == {"algoritmo_preto_branco": jeito, "limpar_pontinhos": limpeza,
                              "reduzir_cores": True}
    assert pagina.algoritmo_preto_branco != jeito and not pagina.reduzir_cores, "a página não mudou"
    vista = _esperar_a_imagem(dialogo, PRETO_E_BRANCO)
    assert vista is not None
    copia = replace(pagina, forca_preto=70, algoritmo_preto_branco=jeito, limpar_pontinhos=limpeza,
                    reduzir_cores=True, alertas=list(pagina.alertas))
    doc = abrir_pdf(tela.projeto.caminho_entrada)
    try:
        esperada, _ = renderizar_com_filtro(doc, tela.projeto, copia, PRETO_E_BRANCO, dpi=DPI_DA_TELA_CHEIA)
    finally:
        doc.close()
    assert np.array_equal(vista, esperada), "a tela cheia mostra outra página que a do filtro"
    dialogo.usar()
    assert (pagina.filtro, pagina.forca_preto, pagina.algoritmo_preto_branco, pagina.limpar_pontinhos,
            pagina.reduzir_cores) == (PRETO_E_BRANCO, 70, jeito, limpeza, True)
    doc = abrir_pdf(tela.projeto.caminho_entrada)
    try:
        saiu, _ = renderizar_pagina(doc, tela.projeto, pagina, dpi=DPI_DA_TELA_CHEIA)
    finally:
        doc.close()
    assert np.array_equal(vista, saiu), "a página depois de Usar não é a que a tela cheia mostrou"
    # cada opção é uma ação do desfazer, como no painel
    for _ in range(5):
        tela.desfazer()
    assert pagina.algoritmo_preto_branco != jeito and not pagina.reduzir_cores


def test_fechar_sem_mudar_com_opcoes_mexidas_nao_muda_nada(conferir_original):  # noqa: F811
    from core.filtros import PRETO_E_BRANCO

    tela = conferir_original
    antes = tela.projeto.fotografar()
    dialogo = _tela_cheia(tela)
    dialogo.escolher(PRETO_E_BRANCO)
    dialogo.caixas["claro_no_escuro"].setChecked(True)
    dialogo.escolhas_misto.caixa.setChecked(True)
    assert dialogo.opcoes
    dialogo.botao_sem_mudar.click()
    assert tela.projeto.fotografar() == antes
    assert not tela.acoes.pode_desfazer


def test_livro_ja_comecado_sai_igual(conferir_original):  # noqa: F811
    """Livro começado antes das opções novas (o projeto.json sem os campos do
    2.8, 2.9 e 2.11): a página lida tem as opções desligadas, a tela cheia as
    mostra desligadas, e "Usar" sem mexer nelas só troca o filtro (nenhuma
    opção nova é gravada): a página sai igual à de antes."""
    import numpy as np

    from core.filtros import PRETO_E_BRANCO
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina
    from modelos import Projeto

    tela = conferir_original
    dados = tela.projeto.para_dicionario()
    for pagina in dados["paginas"]:
        for campo in ("claro_no_escuro", "letras_com_a_cor", "reduzir_cores"):
            pagina.pop(campo, None)
    velho = Projeto.de_dicionario(dados)
    assert all(not (p.claro_no_escuro or p.letras_com_a_cor or p.reduzir_cores) for p in velho.paginas)
    from dataclasses import replace

    pagina = tela.projeto.paginas[0]
    dialogo = _tela_cheia(tela)
    dialogo.escolher(PRETO_E_BRANCO)
    assert not any(c.isChecked() for c in dialogo.caixas.values())
    dialogo.usar()
    assert dialogo.opcoes == {}
    assert not (pagina.claro_no_escuro or pagina.letras_com_a_cor or pagina.reduzir_cores)
    doc = abrir_pdf(tela.projeto.caminho_entrada)
    try:
        # cada página desenhada duas vezes, e comparada a segunda: a primeira vez
        # que o core desenha uma página ele grava nela a geometria das zonas (e
        # pode acertar um alerta do endireitar), e essa primeira sai uns 60
        # pixels diferente das seguintes (achado de 22/10/2026, fora das opções
        # novas e fora da tela; anotado para a gerente)
        velha = replace(velho.paginas[0], filtro=PRETO_E_BRANCO, revisada=True)
        for _ in range(2):
            depois, _ = renderizar_pagina(doc, tela.projeto, pagina, dpi=100)
            antes, _ = renderizar_pagina(doc, velho, velha, dpi=100)
    finally:
        doc.close()
    assert np.array_equal(antes, depois), "o livro começado antes das opções novas sai diferente"


def test_ajuste_mexido_mostra_a_pagina_como_sai(conferir_original):  # noqa: F811
    """Defeito de 21/10/2026 (ressalva da etapa 6): mexendo só no ajuste na tela
    cheia, a página grande era refeita por outro caminho, só com o filtro (sem o
    "Só as letras", sem o "Reduzir cores" e o "Letra clara" da página), e não
    era a página que ia sair. Agora é a do mesmo caminho do PDF. Aqui a página
    tem "Reduzir cores" (marcado no painel) e o ajuste do Melhorar é mexido na
    tela cheia. Falha no d285b48 (o código de antes desta mudança)."""
    from dataclasses import replace

    import numpy as np

    from core.filtros import MELHORAR
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_com_filtro
    from ui.widgets.filtros_tela_cheia import DPI_DA_TELA_CHEIA

    tela = conferir_original
    pagina = tela.projeto.paginas[0]
    pagina.reduzir_cores = True                      # como se marcado no painel
    _aquecer(tela)
    dialogo = _tela_cheia(tela)
    dialogo.escolher(MELHORAR)
    dialogo._ajuste_mudou(80)
    vista = _esperar_a_imagem(dialogo, MELHORAR)
    assert vista is not None
    doc = abrir_pdf(tela.projeto.caminho_entrada)
    try:
        esperada, _ = renderizar_com_filtro(doc, tela.projeto, replace(pagina, clareza_melhorar=80),
                                            MELHORAR, dpi=DPI_DA_TELA_CHEIA)
    finally:
        doc.close()
    assert vista.shape == esperada.shape and np.array_equal(vista, esperada),         "com o ajuste mexido, a tela cheia não mostra a página que vai sair"
    dialogo.reject()
