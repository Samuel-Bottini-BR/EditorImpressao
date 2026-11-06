"""Provas de comportamento da D-621 (04/11/2026): "Desfazer nesta página" pelo botão direito.

Samuel: "eu quero um botão para desfazer ajustes em uma pagina só, por exemplo, vamos supor que eu
passei o automatico e só uma pagina veio com defeito, e eu gostaria de tirar algumas etapas que foram
feitas somente com ela, eu quero poder clicar e falar quais coisas eu quero que sejam tirar, porque
geralmnete quando a pagina já foi dividida, ela está certa e se eu juntar uma pagina na outra, a outra
pagina que está certa vai voltar a ser uma junto com a que está errada e eu vou ter que refazer o
processo em duas, e eu quero fazer só em uma." · jeito escolhido: "A2" (botão direito, caixinhas).

Livro de decisões: botão direito na página (área de trabalho) ou na miniatura (tira) → "Desfazer nesta
página": a lista das etapas que mexeram nessa página (Endireitar, Corte das bordas, Mover e tamanho,
Filtro, Gravuras e fotos), cada uma com caixinha, e o botão "desfazer". Só as marcadas voltam ao que
veio do scan, só nessa página. A divisão não entra na lista: a página continua separada e a outra
página da folha não muda. Uma ação só no desfazer (Ctrl+Z volta tudo).

O que se mede: os campos da página e da outra página da folha (o que vai para o projeto.json), o
Histórico (uma ação só, Ctrl+Z e Ctrl+Y) e o PDF que o programa grava (core.pipeline.processar, o
mesmo do "Confirmar e processar"). O livro é o livro aberto sintético de tests/test_decisoes_dividir.py
(3 folhas → 6 páginas pelo Automático); a folha 1 vira as páginas 2 (esquerda) e 3 (direita).

Todos falham no código de antes (`1d2ed264`, sem ui/desfazer_nesta_pagina.py e sem o botão direito
na página): ver relatorios/desfazer-pagina/reversao.txt.
"""

from __future__ import annotations

import dataclasses
import time

import numpy as np
import pytest

pytest.importorskip("fitz")
pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from core import etapas as E  # noqa: E402
from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixtures app, pasta, janela)
    _gerar,
    _livro_aberto,
    _rodar,
    app,
    janela,
    pasta,
    precisa_da_dll,
)

ESQUERDA, DIREITA = 2, 3           # as duas páginas da folha 1 depois do Automático
TODAS = ("endireitar", "cortar", "mover", "filtro", "marcar")


def _assentar(vezes: int = 6) -> None:
    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        QApplication.processEvents()


def _esperar_as_marcacoes(tela, projeto, indice: int, limite: float = 120.0) -> None:
    """Espera (deixando a janela trabalhar) a página `indice` sair da lista das que têm a marcação
    ainda solta da folha (core/zonas_na_folha.paginas_por_converter): a prévia dela prende."""
    import time

    from core.zonas_na_folha import paginas_por_converter

    fim = time.time() + limite
    while time.time() < fim:
        if all(p.indice != indice for p in paginas_por_converter(projeto)):
            return
        _assentar()
        time.sleep(0.05)
    raise AssertionError(f"a marcação da página {indice + 1} não ficou pronta em {limite:.0f} s")


def _regiao_a_mao():
    from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao

    selecao = Selecao()
    selecao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.2, 0.2), (0.5, 0.5)],
                               origem=MAO))
    return selecao


def _mexer_a_mao(tela, projeto, indice: int) -> None:
    """Endireitar, cortar, mover, filtro e uma gravura marcada à mão na página `indice`, pelos
    mesmos métodos que os botões da tela chamam."""
    tela.ir_para_pagina(indice)
    tela._gravar_angulo(indice, 1.5)
    tela._mover_recorte((0.06, 0.05, 0.86, 0.88))
    tela._gravar_o_conteudo(0.8, (0.03, 0.02), "mover", indices=[indice])
    tela._escolher_filtro(PRETO_E_BRANCO)
    pagina = projeto.paginas[indice]
    pagina.guardar_selecao(_regiao_a_mao())
    E.marcar_mexida_a_mao(pagina, E.MARCAR)


def _livro_com_as_duas_paginas_mexidas(janela, tmp_path):
    janela.abrir_livro(_livro_aberto(tmp_path))
    assert _rodar(janela, [A.DIVIDIR])
    tela, projeto = janela.tela_conferir, janela.projeto
    assert len(projeto.paginas) == 6
    assert projeto.paginas[ESQUERDA].folha == projeto.paginas[DIREITA].folha == 1
    for indice in (ESQUERDA, DIREITA):
        _mexer_a_mao(tela, projeto, indice)
    return tela, projeto


# Campos que o PROGRAMA preenche sozinho ao desenhar a página por trás (não são escolha de
# ninguém; modelos.ConfigPagina): as zonas presas à folha, a marcação provisória, a assinatura da
# gravura, a faixa medida e os avisos medidos. Mudam com a prévia que chega por trás, em qualquer
# página, com ou sem o "Desfazer nesta página"; ficam fora da comparação.
_DO_DESENHO = ("geometria_das_zonas", "marcacao_provisoria", "gravura_feita_com",
               "faixa_na_beirada", "alertas")


def _foto(objeto) -> dict:
    return {c: v for c, v in dataclasses.asdict(objeto).items() if c not in _DO_DESENHO}


VEIO_DO_SCAN = {   # o que cada etapa grava ao ser desfeita (o mesmo do botão da ferramenta)
    "endireitar": {"angulo_manual": 0.0},
    "cortar": {"recorte": (0.0, 0.0, 1.0, 1.0)},
    "mover": {"conteudo_escala": 1.0, "conteudo_deslocamento": (0.0, 0.0)},
    "filtro": {"filtro": ORIGINAL},
    "marcar": {"selecao": [], "respeitar_gravuras_achadas": False},
}


# --- a lista mostra o que mexeu, e cada etapa sozinha volta ao que veio do scan ----------------

@precisa_da_dll
@pytest.mark.parametrize("etapa", TODAS)
def test_d621_cada_etapa_sozinha_volta_so_ela_so_nesta_pagina(janela, tmp_path, etapa):
    """D-621: "eu quero poder clicar e falar quais coisas eu quero que sejam tirar". Página 2 (a
    esquerda da folha 1) e página 3 (a direita) mexidas nas cinco etapas → a lista da página 2 tem as
    cinco acesas → desfazer SÓ uma → só aquela volta ao que veio do scan (o valor do botão da
    ferramenta: "deixar como veio", "não cortar esta", "voltar como veio", Original, sem marcação);
    as outras quatro da página 2 ficam; a página 3 e a folha não mudam nada; uma ação só."""
    from ui import desfazer_nesta_pagina as D

    tela, projeto = _livro_com_as_duas_paginas_mexidas(janela, tmp_path)
    pagina, vizinha = projeto.paginas[ESQUERDA], projeto.paginas[DIREITA]
    assert D.etapas_que_mexeram(projeto, pagina) == list(TODAS)
    antes, antes_vizinha, antes_folha = _foto(pagina), _foto(vizinha), _foto(projeto.folhas[1])
    feitas = len(janela.acoes.feitas)

    assert tela.desfazer_nesta_pagina(ESQUERDA, [etapa])

    depois = _foto(pagina)
    for campo, valor in VEIO_DO_SCAN[etapa].items():
        assert getattr(pagina, campo) == valor, campo
    mudaram = {c for c in antes if antes[c] != depois[c]}
    esperados = set(VEIO_DO_SCAN[etapa]) | {"mexida_a_mao", "revisada"}
    assert mudaram <= esperados, mudaram - esperados          # as outras etapas ficaram
    assert etapa not in D.etapas_que_mexeram(projeto, pagina)
    assert [e for e in TODAS if e != etapa] == D.etapas_que_mexeram(projeto, pagina)
    assert _foto(vizinha) == antes_vizinha                    # a outra página da folha
    assert _foto(projeto.folhas[1]) == antes_folha            # a folha continua dividida
    assert projeto.folhas[1].dividir and len(projeto.paginas) == 6
    assert len(janela.acoes.feitas) == feitas + 1             # uma ação só


@precisa_da_dll
def test_d621_varias_juntas_numa_acao_e_o_ctrl_z_volta_tudo(janela, tmp_path):
    """D-621: "Uma ação só no desfazer (Ctrl+Z volta tudo)". Desfazer as cinco de uma vez na
    página 2 → uma ação só no Histórico, com o nome das etapas; o desfazer (o da barra de baixo, o
    mesmo do Ctrl+Z) devolve a página 2 exatamente como estava; o refazer (Ctrl+Y) desfaz de novo.
    A página 3 não muda em nenhum momento."""
    tela, projeto = _livro_com_as_duas_paginas_mexidas(janela, tmp_path)
    pagina, vizinha = projeto.paginas[ESQUERDA], projeto.paginas[DIREITA]
    antes, antes_vizinha = _foto(pagina), _foto(vizinha)
    feitas = len(janela.acoes.feitas)

    assert tela.desfazer_nesta_pagina(ESQUERDA, list(TODAS))
    assert len(janela.acoes.feitas) == feitas + 1
    ultima = janela.acoes.feitas[-1]
    assert ultima.indices == [ESQUERDA]
    assert ultima.descricao == ("Desfazer na página 3: Endireitar, Corte das bordas, Mover e tamanho, "
                                "Filtro e Gravuras e fotos")
    desfeita = _foto(pagina)
    for valores in VEIO_DO_SCAN.values():
        for campo, valor in valores.items():
            assert getattr(pagina, campo) == valor, campo

    tela.botao_desfazer_embaixo.click()                       # o desfazer de baixo = Ctrl+Z
    _assentar()
    assert _foto(pagina) == antes
    assert len(janela.acoes.feitas) == feitas
    tela.refazer()                                            # Ctrl+Y
    _assentar()
    assert _foto(pagina) == desfeita
    assert _foto(vizinha) == antes_vizinha


@precisa_da_dll
def test_d621_o_pdf_sai_com_a_pagina_desfeita_e_a_vizinha_igual(janela, tmp_path):
    """D-621, o exemplo do Livro: "botão direito → marcar Corte e Filtro → desfazer → só a página
    volta sem corte e em Original; a outra não muda". No PDF gravado: a página 2 sai do tamanho da
    metade inteira (sem corte) e com o papel amarelado do scan (Original); a página 3 sai igual,
    ponto por ponto, à de antes (cortada, Preto e branco). Seis páginas antes e depois."""
    tela, projeto = _livro_com_as_duas_paginas_mexidas(janela, tmp_path)
    antes = _gerar(janela, tmp_path, "antes")
    assert len(antes) == 6

    assert tela.desfazer_nesta_pagina(ESQUERDA, ["cortar", "filtro"])
    depois = _gerar(janela, tmp_path, "depois")
    assert len(depois) == 6

    sem_corte = depois[ESQUERDA]
    assert sem_corte.shape[0] > antes[ESQUERDA].shape[0] * 1.08          # maior: sem o corte
    assert sem_corte.shape[1] > antes[ESQUERDA].shape[1] * 1.08
    def papel(img):          # RGB do papel embaixo do "texto" (o Mover de 80% continua valendo)
        altura, largura = img.shape[:2]
        return img[int(0.8 * altura):int(0.86 * altura),
                   int(0.4 * largura):int(0.6 * largura)].reshape(-1, 3).mean(axis=0)

    assert papel(sem_corte)[0] - papel(sem_corte)[2] > 25                   # amarelado (Original)
    assert abs(papel(antes[ESQUERDA])[0] - papel(antes[ESQUERDA])[2]) < 8   # antes: Preto e branco
    assert depois[DIREITA].shape == antes[DIREITA].shape
    assert np.array_equal(depois[DIREITA], antes[DIREITA])                  # a vizinha igual
    for outra in (0, 1, 4, 5):
        assert np.array_equal(depois[outra], antes[outra])


# --- a página fica como com "deixar como veio" e "não cortar esta" (D-004) -------------------

@precisa_da_dll
def test_d621_a_pagina_fica_igual_a_deixar_como_veio_e_nao_cortar_esta(janela, tmp_path):
    """D-004 + D-368: depois de desfazer, a página fica como o programa já deixa com "deixar como
    veio" (Endireitar) e "não cortar esta" (Cortar): o mesmo valor, a marca "mexida à mão" da etapa
    (a pergunta do Automático vê a página) e "conferida". Página 2 pelo "Desfazer nesta página";
    página 3 pelos dois botões das ferramentas → os mesmos campos."""
    tela, projeto = _livro_com_as_duas_paginas_mexidas(janela, tmp_path)
    tela.desfazer_nesta_pagina(ESQUERDA, ["endireitar", "cortar"])
    tela.ir_para_pagina(DIREITA)
    # Os botões da ferramenta esperam a prévia da página prender a gravura marcada à mão à
    # folha (o "Um momento" de _espera_pelas_marcacoes, como na mão do Samuel). Na máquina lenta
    # do GitHub (rodada 41949496078) o botão foi apertado antes: espera a prévia, como a pessoa.
    _esperar_as_marcacoes(tela, projeto, DIREITA)
    tela._angulo_zero()
    tela._sem_recorte()
    pagina, pelos_botoes = projeto.paginas[ESQUERDA], projeto.paginas[DIREITA]
    for campo in ("angulo_manual", "recorte", "revisada"):
        assert getattr(pagina, campo) == getattr(pelos_botoes, campo), campo
    for etapa in (E.ENDIREITAR, E.CORTAR):
        assert E.mexida_a_mao(projeto, pagina, etapa) and etapa in pagina.mexida_a_mao
        assert etapa in pelos_botoes.mexida_a_mao


def test_d621_etapas_do_automatico_sem_valor_a_mao_tambem_aparecem_e_voltam(tmp_path):
    """D-621: "vamos supor que eu passei o automatico e só uma pagina veio com defeito". Página sem
    nada à mão num livro com o corte e o filtro do Automático ligados (Preto e branco) → a lista tem
    Corte das bordas e Filtro acesos e o resto apagado → desfeitos, a página sai sem corte e em
    Original mesmo com o Automático ligado no livro; as outras páginas continuam no automático."""
    from modelos import ConfigPagina, Projeto
    from ui import desfazer_nesta_pagina as D

    projeto = Projeto(caminho_entrada=str(tmp_path / "x.pdf"))
    projeto.endireitar = False
    projeto.cortar_bordas = True
    projeto.limpar = True
    projeto.paginas = [ConfigPagina(indice=i, folha=0, filtro=PRETO_E_BRANCO) for i in range(2)]
    pagina = projeto.paginas[0]
    assert D.etapas_que_mexeram(projeto, pagina) == ["cortar", "filtro"]
    campos = D.campos_para_desfazer(projeto, pagina, ["cortar", "filtro"])
    assert campos["recorte"] == [0.0, 0.0, 1.0, 1.0] and campos["filtro"] == ORIGINAL
    for campo, valor in campos.items():
        setattr(pagina, campo, tuple(valor) if campo == "recorte" else valor)
    assert E.recorte_a_mao(projeto, pagina) == (0.0, 0.0, 1.0, 1.0)
    assert E.filtro_que_vale(projeto, pagina) == ORIGINAL
    assert D.etapas_que_mexeram(projeto, pagina) == []
    assert E.filtro_que_vale(projeto, projeto.paginas[1]) == PRETO_E_BRANCO
    assert E.recorte_a_mao(projeto, projeto.paginas[1]) is None


def test_d621_gravuras_desfeitas_nao_voltam_pela_procura_da_maquina(tmp_path):
    """D-621, "Gravuras e fotos" → "sem as marcações". Com "Gravuras e fotos" ligada no livro a
    máquina procuraria de novo numa marcação vazia; por isso a caixinha "Respeitar as gravuras
    achadas" (D-586) da página fica desligada: o filtro dela não usa o que a máquina achar
    (core.pipeline.marcacao_que_o_filtro_usa só devolve o feito à mão, e não há nada à mão)."""
    from core.pipeline import marcacao_que_o_filtro_usa
    from core.selecao import AUTOMATICO, GRAVURA, RETANGULO, Regiao, Selecao
    from modelos import ConfigPagina, Projeto
    from ui import desfazer_nesta_pagina as D

    projeto = Projeto(caminho_entrada=str(tmp_path / "x.pdf"))
    projeto.endireitar = projeto.cortar_bordas = False
    projeto.limpar = True
    projeto.detectar_regioes = True
    pagina = ConfigPagina(indice=0, folha=0, filtro=PRETO_E_BRANCO)
    projeto.paginas = [pagina]
    achada = Selecao()
    achada.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.1, 0.1), (0.6, 0.6)],
                              origem=AUTOMATICO))
    pagina.guardar_selecao(achada)
    assert D.etapas_que_mexeram(projeto, pagina) == ["filtro", "marcar"]
    for campo, valor in D.campos_para_desfazer(projeto, pagina, ["marcar"]).items():
        setattr(pagina, campo, valor)
    assert pagina.selecao == [] and pagina.respeitar_gravuras_achadas is False
    pagina.guardar_selecao(achada)                           # a máquina achou de novo
    assert marcacao_que_o_filtro_usa(projeto, pagina, pagina.obter_selecao()).vazia
    assert D.etapas_que_mexeram(projeto, pagina) == ["filtro"]
    assert pagina.filtro == PRETO_E_BRANCO                    # o filtro não foi desfeito


# --- o botão direito ----------------------------------------------------------------------

def _botao_direito(widget, ponto=None) -> None:
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QContextMenuEvent
    from PySide6.QtWidgets import QApplication

    ponto = ponto or QPoint(widget.width() // 2, widget.height() // 2)
    evento = QContextMenuEvent(QContextMenuEvent.Mouse, ponto, widget.mapToGlobal(ponto))
    QApplication.sendEvent(widget, evento)
    _assentar()


def _o_menu(tela):
    menu = getattr(tela, "_menu_desfazer", None)
    assert menu is not None, "o botão direito não abriu menu"
    submenus = [a.menu() for a in menu.actions() if a.menu() is not None]
    assert [s.title() for s in submenus] == ["Desfazer nesta página"]
    return submenus[0]


@precisa_da_dll
def test_d621_botao_direito_na_pagina_abre_a_lista_e_o_desfazer_funciona(janela, tmp_path):
    """D-621: "Botão direito na página (na área de trabalho) [...] abre “Desfazer nesta página”: a
    lista das etapas que mexeram nessa página [...] cada uma com caixinha, e o botão “desfazer”."
    Ferramenta Cortar, "Uma página", página 2: botão direito no meio da página → o menu tem
    "Desfazer nesta página" com as cinco caixinhas (desmarcadas; acesas as que mexeram) e o botão
    "desfazer" (apagado até marcar uma) → marcar Corte e Filtro → "desfazer" → só a página 2 volta
    sem corte e em Original; a página 3 não muda. Numa página sem nada mexido as caixinhas ficam
    apagadas."""
    from ui.tela_conferir import ABA_BORDAS

    janela.show()
    tela, projeto = _livro_com_as_duas_paginas_mexidas(janela, tmp_path)
    antes_vizinha = _foto(projeto.paginas[DIREITA])
    tela.escolher_ferramenta("cortar")
    tela.ir_para_pagina(ESQUERDA)
    _assentar()
    _botao_direito(tela.visualizadores[ABA_BORDAS])
    submenu = _o_menu(tela)
    lista = submenu.lista
    assert submenu.indice == ESQUERDA
    assert [c.text() for c in lista.caixas.values()] == [
        "Endireitar", "Corte das bordas", "Mover e tamanho", "Filtro", "Gravuras e fotos"]
    assert all(c.isEnabled() and not c.isChecked() for c in lista.caixas.values())
    assert lista.botao.text() == "desfazer" and not lista.botao.isEnabled()
    lista.caixas["cortar"].setChecked(True)
    lista.caixas["filtro"].setChecked(True)
    assert lista.botao.isEnabled()
    lista.botao.click()
    _assentar()
    pagina = projeto.paginas[ESQUERDA]
    assert pagina.recorte == (0.0, 0.0, 1.0, 1.0) and pagina.filtro == ORIGINAL
    assert pagina.angulo_manual == 1.5                       # o que não foi marcado ficou
    assert _foto(projeto.paginas[DIREITA]) == antes_vizinha

    tela.ir_para_pagina(0)                                   # a página 1: nada mexido nela
    _assentar()
    _botao_direito(tela.visualizadores[ABA_BORDAS])
    lista = _o_menu(tela).lista
    assert not any(c.isEnabled() for c in lista.caixas.values())
    assert not lista.botao.isEnabled()


@precisa_da_dll
def test_d621_botao_direito_na_miniatura_e_da_pagina_dela(janela, tmp_path):
    """D-621: "ou na miniatura dela (na tira de baixo)". Com a página 1 na tela, o botão direito
    na miniatura da página 3 abre a lista DA PÁGINA 3 (a dela), e o desfazer muda só a página 3."""
    janela.show()
    tela, projeto = _livro_com_as_duas_paginas_mexidas(janela, tmp_path)
    tela.escolher_ferramenta("cortar")
    tela.ir_para_pagina(0)
    _assentar()
    from ui.widgets.tira_miniaturas import Miniatura

    miniatura = next(m for m in tela.tira.findChildren(Miniatura) if m.numero == DIREITA + 1)
    antes_esquerda = _foto(projeto.paginas[ESQUERDA])
    _botao_direito(miniatura)
    submenu = _o_menu(tela)
    assert submenu.indice == DIREITA
    submenu.lista.caixas["filtro"].setChecked(True)
    submenu.lista.botao.click()
    _assentar()
    assert projeto.paginas[DIREITA].filtro == ORIGINAL
    assert _foto(projeto.paginas[ESQUERDA]) == antes_esquerda
    assert tela.indice_pagina == 0                           # a tela não mudou de página


@precisa_da_dll
def test_d621_no_duas_lado_a_lado_vale_a_pagina_clicada(janela, tmp_path):
    """D-621 em "Duas lado a lado" (D-015/D-006): o botão direito na página da DIREITA do par abre
    a lista dela, mesmo com a da esquerda sendo a da vez."""
    from ui.widgets.paginas_rolando import DUAS

    janela.show()
    tela, projeto = _livro_com_as_duas_paginas_mexidas(janela, tmp_path)
    tela.escolher_ferramenta("cortar")
    tela.ir_para_pagina(ESQUERDA)
    tela.botoes_mostrar[DUAS].click()                        # "Duas lado a lado"
    _assentar(20)
    lado = tela.lado_a_lado
    assert tela.vista_da_pagina.currentWidget() is lado
    alvo = next((ret for pos, ret in lado._ret if lado.indices[pos] == DIREITA), None)
    assert alvo is not None, "a página 3 não está à vista no par"
    from PySide6.QtCore import QPoint
    ponto = lado.folhas.mapTo(lado.viewport(), QPoint(int(alvo.center().x()), int(alvo.center().y())))
    _botao_direito(lado.viewport(), ponto)
    assert _o_menu(tela).indice == DIREITA


@precisa_da_dll
def test_d621_no_mover_o_menu_das_linhas_continua_e_ganha_o_desfazer(janela, tmp_path, monkeypatch):
    """D-605 (o que já está escolhido e testado não muda) + D-621. No Mover o botão direito já
    abria o menu das linhas de apoio (D-056, g8-guias): ele continua com as mesmas opções, na mesma
    ordem, e ganha embaixo o "Desfazer nesta página" da página da vez."""
    from PySide6.QtWidgets import QMenu

    from ui.tela_conferir import ABA_MOVER

    janela.show()
    tela, _projeto = _livro_com_as_duas_paginas_mexidas(janela, tmp_path)
    tela.escolher_ferramenta("mover")
    tela.ir_para_pagina(ESQUERDA)
    _assentar(10)
    vistos = []

    class MenuQueNaoEspera(QMenu):
        """O menu do Mover sem o exec que espera o clique (só anota os itens)."""

        def exec(self, *_a, **_k):  # noqa: A003 - o nome do Qt
            vistos.append([(a.text(), a.menu().title() if a.menu() else None)
                           for a in self.actions() if not a.isSeparator()])
            return None

    import ui.widgets.visualizador as modulo_do_visualizador
    monkeypatch.setattr(modulo_do_visualizador, "QMenu", MenuQueNaoEspera)
    vis = tela.visualizadores[ABA_MOVER]
    fim = time.monotonic() + 60
    while vis._area.width() <= 0 and time.monotonic() < fim:     # a prévia do Mover chega
        _assentar(2)
        time.sleep(0.05)
    area = vis._area
    assert area.width() > 0, "a prévia do Mover não chegou"
    from PySide6.QtCore import QPoint
    _botao_direito(vis, QPoint(area.center().x(), area.center().y()))
    assert vistos, "o menu do Mover não abriu"
    textos = [t for t, _m in vistos[0]]
    assert textos[:2] == ["Pôr uma linha de pé aqui", "Pôr uma linha deitada aqui"]
    assert textos[-1] == "Desfazer nesta página"
