"""As provas de comportamento da D-574 na etapa 7 "Montar cadernos" do Automático (CLAUDE.md §11,
regra 4; Livro de decisões, docs/plano/DECISOES.md).

  D-574. 29/10/2026: "quando mostra para fazer os cadernos lá na parte de fazer caderno tem que
      ter um botão para ver como vai ficar o caderno." · 31/10: "Sim, mas no caso, eu estou
      falando em tela grande, pois no painel automatico, vamos conseguir ver ele só se clicarmos
      na opção de montar cadernos e lá se apertarmos em ver tela grande abriremos o tela grande
      que já temos mas para versão de caderno." · No Livro: "No Automático: clicando na etapa 7
      "Montar cadernos", o lado direito mostra as folhas do livreto; o botão "tela cheia" abre
      a tela grande que já existe, na versão de caderno." Jeito (opção 1): frente e verso,
      "Folha N de M", setas. 02/11: "aonde fica o ver caderno aqui?" (print a-44) · "mas no caso
      ele vai fazer isso só quando a etapa 7 estiver selecionada no montar cadernos né?" → sim.
  D-473 (26/10): tela e PDF saem da mesma conta (a folha mostrada = a do PDF da etapa 7).
  CLAUDE.md §3: a tela nunca congela (limite 0,3 s, o mesmo do verificador da D-574).

Teste de reversão (CLAUDE.md §4.7): no código antigo (`110976f`) o lado direito com a etapa 7
aberta continuava o antes e depois da página (print a-44): estas provas falham lá.

Livro sintético de propósito: 10 páginas, cada uma com uma faixa preta numa altura diferente
(a página k tem a faixa na k-ésima altura), para ler qual página caiu em cada metade da folha.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from tests.test_decisoes_automatico import _pdf  # noqa: E402

LIMITE_S = 180
LIMITE_DA_PARADA_S = 0.3
PAGINAS = 10
ALTURA, LARGURA = 840, 600


def _pagina_marcada(k: int) -> np.ndarray:
    """Papel branco com a faixa preta da página k (0, 1, ...) numa altura só dela."""
    img = np.full((ALTURA, LARGURA, 3), 245, np.uint8)
    y = 40 + k * 70
    img[y:y + 50, 100:LARGURA - 100] = 20
    return img


def _livro_marcado(tmp_path: Path) -> str:
    caminho = tmp_path / "marcado.pdf"
    if not caminho.exists():
        _pdf(caminho, [_pagina_marcada(k) for k in range(PAGINAS)])
    return str(caminho)


def _qual_pagina(metade: np.ndarray):
    """Qual página (1, 2, ...) está nesta metade da folha, pela altura da faixa; None = branca."""
    cinza = metade if metade.ndim == 2 else metade.mean(axis=2)
    linhas = np.where((cinza < 100).mean(axis=1) > 0.3)[0]
    if len(linhas) == 0:
        return None
    meio = linhas.mean() / cinza.shape[0] * ALTURA
    return int(round((meio - 65) / 70)) + 1


def _paginas_do_lado(face: np.ndarray) -> tuple:
    meio = face.shape[1] // 2
    return _qual_pagina(face[:, :meio]), _qual_pagina(face[:, meio:])


# --- a janela ---------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def janela(app, tmp_path, monkeypatch):
    import projetos
    from ui.automatico import _guardiao
    from ui.janela_principal import JanelaPrincipal

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    yield janela
    janela._fechar_a_janela_do_automatico()
    for tarefa in list(_guardiao().tarefas):
        tarefa.wait(60000)
    _assentar(app)
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


def _assentar(app, vezes: int = 5) -> None:
    for _ in range(vezes):
        app.processEvents()


def _esperar(app, painel) -> None:
    fim = time.monotonic() + LIMITE_S
    while time.monotonic() < fim:
        app.processEvents()
        if not painel.calculando():
            _assentar(app)
            if not painel.calculando():
                return
        time.sleep(0.02)
    raise AssertionError("a folha do caderno não terminou")


def _abrir(janela, app, tmp_path, etapa: str = A.CADERNOS, por_caderno: int = 8):
    """O livro marcado aberto e a janela grande do Automático na `etapa`; só "Montar cadernos"
    marcada (as páginas saem como vieram: dá para ler a faixa de cada uma)."""
    janela.abrir_livro(_livro_marcado(tmp_path))
    _assentar(app)
    estado = janela.estado_do_automatico
    estado.marcadas = {A.CADERNOS}
    estado.opcoes["paginas_por_caderno"] = por_caderno
    grande = janela.abrir_o_automatico(etapa)
    assert grande is not None
    _assentar(app)
    return grande


def _folhas(grande):
    """O lado direito das folhas do caderno (None no código antigo: a prova falha aí)."""
    folhas = getattr(grande, "folhas_do_caderno", None)
    assert folhas is not None, "com a etapa 7 aberta o lado direito não mostra as folhas do caderno"
    return folhas


# --- D-574: a etapa 7 aberta mostra as folhas; as outras, o antes e depois -----------

def test_d574_etapa_7_aberta_mostra_as_folhas_e_as_outras_o_antes_e_depois(janela, app, tmp_path):
    """D-574 (31/10 e 02/11): "clicando na etapa 7 "Montar cadernos", o lado direito mostra as
    folhas do livreto" · "só quando a etapa 7 estiver selecionada". O antigo (print a-44: com a
    etapa 7 aberta, o lado direito era "A página, antes e depois") saiu."""
    grande = _abrir(janela, app, tmp_path, etapa=A.CADERNOS)
    folhas = _folhas(grande)
    assert grande.lado_direito.currentWidget() is folhas
    assert folhas.isVisibleTo(grande) and not grande.folhear.isVisibleTo(grande)
    _esperar(app, folhas)
    assert folhas.faces() is not None
    assert folhas.rotulos["frente"].text() == "Folha 1 de 3 — frente"
    assert folhas.rotulos["verso"].text() == "Folha 1 de 3 — verso"
    assert folhas.rotulo_da_folha.text() == "folha 1"
    assert folhas.nota_vira_o_papel.text() == "(vira o papel)"

    # clicar noutra etapa: volta o antes e depois da página (D-577), e as folhas param
    grande.painel_de_opcoes.lista.setCurrentItem(grande.painel_de_opcoes.lista.item_da_etapa(A.LIMPAR))
    _assentar(app)
    assert grande.lado_direito.currentWidget() is grande.folhear
    assert grande.folhear.isVisibleTo(grande) and not folhas.isVisibleTo(grande)
    assert not folhas.ligada and folhas.faces() is None and not folhas.calculando()

    # e clicar de novo na etapa 7 (como o Samuel, na lista): as folhas voltam
    grande.painel_de_opcoes.lista.setCurrentItem(grande.painel_de_opcoes.lista.item_da_etapa(A.CADERNOS))
    _assentar(app)
    assert grande.lado_direito.currentWidget() is folhas and folhas.ligada


def test_d574_a_folha_tem_as_paginas_na_ordem_da_dobra(janela, app, tmp_path):
    """D-574 opção 1 (frente e verso) + D-473: 10 páginas em cadernos de 8 → 3 folhas; folha 1:
    frente 8 e 1, verso 2 e 7; folha 3 (o último caderno, menor): frente branca e 9, verso 10 e
    branca (core/cadernos.montar_ordem, a conta do PDF da etapa 7)."""
    grande = _abrir(janela, app, tmp_path)
    folhas = _folhas(grande)
    _esperar(app, folhas)
    frente, verso = folhas.faces()
    assert _paginas_do_lado(frente) == (8, 1)
    assert _paginas_do_lado(verso) == (2, 7)
    folhas.passar_folha(1)
    _esperar(app, folhas)
    assert folhas.rotulos["frente"].text() == "Folha 2 de 3 — frente"
    assert _paginas_do_lado(folhas.faces()[0]) == (6, 3)
    assert _paginas_do_lado(folhas.faces()[1]) == (4, 5)
    folhas.passar_folha(1)
    _esperar(app, folhas)
    assert _paginas_do_lado(folhas.faces()[0]) == (None, 9)
    assert _paginas_do_lado(folhas.faces()[1]) == (10, None)
    assert not folhas.botao_seguinte.isEnabled() and folhas.botao_anterior.isEnabled()


def test_d574_a_folha_da_tela_e_a_do_pdf_da_etapa_7(janela, app, tmp_path):
    """D-473 ("Tela e PDF saem da mesma conta"): a folha que a tela mostra é a folha 1 do PDF
    que a etapa 7 grava (core/cadernos.impor_pdf, a mesma ordem e o mesmo encaixe). O PDF é
    gravado de verdade e desenhado na mesma resolução da tela; a diferença, ponto a ponto, fica
    no arredondamento do desenho."""
    from core.cadernos import impor_pdf

    grande = _abrir(janela, app, tmp_path)
    folhas = _folhas(grande)
    _esperar(app, folhas)
    frente, verso = folhas.faces()
    saida = tmp_path / "cadernos.pdf"
    impor_pdf(_livro_marcado(tmp_path), saida, 8)
    from ui.widgets.folhas_do_caderno import DPI_DA_FOLHA

    with fitz.open(str(saida)) as doc:
        for n, face in enumerate((frente, verso)):
            pix = doc[n].get_pixmap(dpi=DPI_DA_FOLHA, colorspace=fitz.csRGB)
            pdf = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)[..., ::-1]
            if pdf.shape != face.shape:
                pdf = cv2.resize(pdf, (face.shape[1], face.shape[0]), interpolation=cv2.INTER_AREA)
            diferenca = float(np.abs(pdf.astype(int) - face.astype(int)).mean())
            assert diferenca < 4.0, f"lado {n}: a tela difere do PDF ({diferenca:.1f} de 255)"
            assert _paginas_do_lado(face) == _paginas_do_lado(pdf)


def test_d574_trocar_as_paginas_por_caderno_refaz_a_folha(janela, app, tmp_path):
    """D-574: as páginas por caderno escolhidas ali; mudando o número, a folha se refaz (pedido
    da gerente, 02/11). 10 páginas: em cadernos de 8, folha 1 frente 8 e 1; em cadernos de 12
    (um caderno só, com duas brancas no fim), folha 1 frente branca (a 12) e 1, verso 2 e branca
    (a 11); de volta a 8, frente 8 e 1."""
    grande = _abrir(janela, app, tmp_path)
    folhas = _folhas(grande)
    _esperar(app, folhas)
    assert _paginas_do_lado(folhas.faces()[0]) == (8, 1)
    combo = grande.controles["paginas_por_caderno"]
    combo.setCurrentIndex(combo.findData(12))
    _assentar(app)
    assert folhas.calculando()                          # refaz (a bolinha gira)
    _esperar(app, folhas)
    assert folhas.rotulos["frente"].text() == "Folha 1 de 3 — frente"
    assert _paginas_do_lado(folhas.faces()[0]) == (None, 1)
    assert _paginas_do_lado(folhas.faces()[1]) == (2, None)
    combo.setCurrentIndex(combo.findData(8))
    _assentar(app)
    _esperar(app, folhas)
    assert _paginas_do_lado(folhas.faces()[0]) == (8, 1)


def test_d574_tela_cheia_com_a_etapa_7_abre_a_tela_grande_de_caderno(janela, app, tmp_path):
    """D-574 (31/10): "lá se apertarmos em ver tela grande abriremos o tela grande que já temos
    mas para versão de caderno." Com a etapa 7: a tela grande mostra a frente e o verso da
    folha, as setas passam a folha. Noutra etapa: continua a tela grande do antes e depois."""
    from ui.automatico import TelaCheiaDoAntesEDepois
    from ui.widgets.folhas_do_caderno import TelaGrandeDoCaderno

    grande = _abrir(janela, app, tmp_path)
    folhas = _folhas(grande)
    _esperar(app, folhas)
    folhas.botao_tela_cheia.click()
    _assentar(app)
    tela = folhas.tela_grande
    assert isinstance(tela, TelaGrandeDoCaderno) and tela.isVisible()
    assert tela.rotulos["frente"].text() == "Folha 1 de 3 — frente"
    assert tela.imagens["frente"].pixmap() is not None and not tela.imagens["frente"].pixmap().isNull()
    largura = tela.imagens["frente"].pixmap().width()
    tela.botao_mais.click()
    _assentar(app)
    assert tela.imagens["frente"].pixmap().width() > largura      # o zoom da tela grande
    tela.botao_proxima.click()
    _esperar(app, folhas)
    _assentar(app)
    assert folhas.posicao == 1 and tela.contador.text() == "Folha 2 de 3"
    assert _paginas_do_lado(folhas.faces()[0]) == (6, 3)
    tela.accept()
    _assentar(app)
    assert not tela.isVisible() and tela.imagens["frente"].pixmap().isNull()

    grande.painel_de_opcoes.lista.setCurrentItem(grande.painel_de_opcoes.lista.item_da_etapa(A.LIMPAR))
    _assentar(app)
    grande.folhear.botao_tela_cheia.click()
    _assentar(app)
    assert isinstance(grande.folhear.tela_cheia, TelaCheiaDoAntesEDepois)


def test_d574_ajustar_a_etapa_7_no_painel_abre_a_janela_nas_folhas(janela, app, tmp_path):
    """D-574 (31/10): "no painel automatico, vamos conseguir ver ele só se clicarmos na opção de
    montar cadernos e lá se apertarmos em ver tela grande". O painel Automático da área de
    trabalho não tem lugar para a folha: "ajustar a etapa escolhida ›" com a etapa 7 escolhida
    abre a janela grande já nas folhas do caderno."""
    janela.abrir_livro(_livro_marcado(tmp_path))
    _assentar(app)
    from ui.automatico import PainelAutomatico

    painel = janela.findChildren(PainelAutomatico)[0]
    painel.lista.setCurrentItem(painel.lista.item_da_etapa(A.CADERNOS))
    painel.botao_ajustar.click()
    _assentar(app)
    grande = janela.janela_do_automatico
    assert grande is not None
    assert grande.etapa_aberta() == A.CADERNOS
    assert grande.lado_direito.currentWidget() is _folhas(grande)


def test_d574_caixinha_desmarcada_mostra_as_folhas_igual(janela, app, tmp_path):
    """D-574, pergunta 2 (02/11): "com a etapa 7 clicada e a caixinha "Montar cadernos"
    desmarcada, mostra as folhas igual?" → "sim". Desmarcar a caixinha com a etapa aberta não
    troca o lado direito: continuam as folhas, na mesma ordem."""
    from PySide6.QtCore import Qt

    grande = _abrir(janela, app, tmp_path)
    folhas = _folhas(grande)
    _esperar(app, folhas)
    item = grande.painel_de_opcoes.lista.item_da_etapa(A.CADERNOS)
    item.setCheckState(Qt.Unchecked)
    _assentar(app)
    assert A.CADERNOS not in janela.estado_do_automatico.marcadas
    assert grande.etapa_aberta() == A.CADERNOS
    assert grande.lado_direito.currentWidget() is folhas and folhas.ligada
    _esperar(app, folhas)
    assert folhas.rotulos["frente"].text() == "Folha 1 de 3 — frente"
    assert _paginas_do_lado(folhas.faces()[0]) == (8, 1)


def test_d574_so_mostra_nao_muda_o_livro(janela, app, tmp_path):
    """D-577/D-574: a janela só mostra; passar folhas e trocar o caderno não muda o projeto."""
    import dataclasses
    import json

    grande = _abrir(janela, app, tmp_path)
    antes = json.dumps(dataclasses.asdict(janela.projeto), sort_keys=True, default=str)
    folhas = _folhas(grande)
    _esperar(app, folhas)
    folhas.passar_folha(1)
    _esperar(app, folhas)
    grande.reject()
    _assentar(app)
    assert json.dumps(dataclasses.asdict(janela.projeto), sort_keys=True, default=str) == antes


def _livro_pesado(tmp_path: Path) -> str:
    """Gradus Primus ou Palatino (cópias em _tmp/livros/ da cópia do projeto), quando estão lá;
    senão o livro marcado."""
    raiz = Path(__file__).resolve().parents[1] / "_tmp" / "livros"
    for nome in ("gradus.pdf", "palatino.pdf"):
        if (raiz / nome).is_file():
            return str(raiz / nome)
    return _livro_marcado(tmp_path)


def test_d574_a_tela_nao_para_enquanto_monta_a_folha(janela, app, tmp_path):
    """CLAUDE.md §3 ("Interface nunca congela"): enquanto a folha do caderno monta (4 páginas
    desenhadas com as etapas de fábrica), um relógio de 5 ms continua batendo no fio da tela;
    a maior parada fica abaixo de 0,3 s (o limite do verificador da D-574)."""
    from PySide6.QtCore import QTimer

    janela.abrir_livro(_livro_pesado(tmp_path))
    _assentar(app)
    # a medida do livro ao abrir (D-284) roda por trás e não é desta tela: espera ela acabar,
    # para o relógio medir só a folha do caderno (o medir.py do verificador faz o mesmo)
    fim = time.monotonic() + LIMITE_S
    while getattr(janela, "medida_ao_abrir", None) is not None and time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.05)
    from core import perfis

    estado = janela.estado_do_automatico
    estado.por_receita(perfis.NOME_DE_FABRICA)        # as etapas de fábrica (print a-44)
    estado.marcadas.add(A.CADERNOS)
    grande = janela.abrir_o_automatico(A.LIMPAR)
    _assentar(app)
    _esperar(app, grande.folhear)
    marcas = {"ultimo": time.monotonic(), "maior": 0.0}

    def bate():
        agora = time.monotonic()
        marcas["maior"] = max(marcas["maior"], agora - marcas["ultimo"])
        marcas["ultimo"] = agora

    relogio = QTimer()
    relogio.setInterval(5)
    relogio.timeout.connect(bate)
    relogio.start()
    try:
        marcas["ultimo"], marcas["maior"] = time.monotonic(), 0.0
        grande.painel_de_opcoes.lista.setCurrentItem(grande.painel_de_opcoes.lista.item_da_etapa(A.CADERNOS))
        folhas = _folhas(grande)
        _esperar(app, folhas)
        folhas.passar_folha(1)
        _esperar(app, folhas)
    finally:
        relogio.stop()
    assert folhas.faces() is not None
    assert marcas["maior"] < LIMITE_DA_PARADA_S, f"a tela parou {marcas['maior']:.2f} s"


def _pedido_da_folha(janela, numero: int = 0):
    """(cópia do projeto, pedido, folha, índices) da folha `numero`, como a janela pede."""
    from core import cadernos
    from core.automatico import copia_para_a_previa

    ativas = [p.indice for p in janela.projeto.paginas_ativas]
    folha = cadernos.ordem_das_folhas(len(ativas), 8)[numero]
    indices = {pos: ativas[pos] for lado in folha for pos in (lado.esquerda, lado.direita)
               if pos is not None and pos < len(ativas)}
    return (copia_para_a_previa(janela.projeto), janela.estado_do_automatico.pedido(pular_mexidas=False),
            folha, indices)


def test_d574_folha_do_servidor_e_igual_a_feita_aqui(janela, app, tmp_path, monkeypatch):
    """D-473 + §3: a folha montada no servidor de páginas (fora do processo da janela) é a
    MESMA, ponto por ponto, que a montada aqui (é a mesma função, core/automatico.
    folha_do_caderno), também com um filtro ligado (Preto e branco)."""
    from core import automatico
    from core import paginas_em_outro_processo as servidor
    from core.filtros import PRETO_E_BRANCO

    janela.abrir_livro(_livro_marcado(tmp_path))
    _assentar(app)
    estado = janela.estado_do_automatico
    chamadas = []
    original = servidor.folha_do_caderno
    monkeypatch.setattr(servidor, "folha_do_caderno",
                        lambda *a, **k: chamadas.append(1) or original(*a, **k))
    for etapas, filtro in (({A.CADERNOS}, None), ({A.LIMPAR, A.CADERNOS}, PRETO_E_BRANCO)):
        estado.marcadas = set(etapas)
        if filtro:
            estado.opcoes["filtro_padrao"] = filtro
        copia, pedido, folha, indices = _pedido_da_folha(janela)
        monkeypatch.delenv(servidor.VARIAVEL_DESLIGA, raising=False)
        chamadas.clear()
        de_la = automatico.folha_do_caderno(copia, pedido, folha, indices, 120)
        assert chamadas, "a folha não foi pedida ao servidor"
        monkeypatch.setenv(servidor.VARIAVEL_DESLIGA, "1")
        daqui = automatico.folha_do_caderno(copia, pedido, folha, indices, 120)
        monkeypatch.delenv(servidor.VARIAVEL_DESLIGA, raising=False)
        for a, b in zip(de_la, daqui):
            assert a.shape == b.shape and np.array_equal(a, b)
        assert _paginas_do_lado(de_la[0]) == (8, 1)


def test_d574_cancelar_para_a_folha_no_servidor(janela, app, tmp_path):
    """A opção mudou no meio (ou a janela fechou): a folha pedida ao servidor volta na hora,
    cancelada, e o servidor continua atendendo (a folha seguinte sai certa). A folha pedida é
    pesada de propósito (Mágico pro a 300 DPI) e o "cancelar" vem logo depois de o pedido sair
    (a 2ª pergunta "cancelou?" já é dentro da espera pelo servidor)."""
    from core import automatico
    from core import paginas_em_outro_processo as servidor
    from core.filtros import MAGICO_PRO
    from core.pipeline import Cancelou

    janela.abrir_livro(_livro_marcado(tmp_path))
    _assentar(app)
    estado = janela.estado_do_automatico
    estado.marcadas = {A.LIMPAR, A.CADERNOS}
    estado.opcoes["filtro_padrao"] = MAGICO_PRO
    copia, pedido, folha, indices = _pedido_da_folha(janela)
    perguntas = []

    def cancelado():
        perguntas.append(1)
        return len(perguntas) >= 2

    assert servidor.ligado()
    inicio = time.monotonic()
    with pytest.raises(Cancelou):
        automatico.folha_do_caderno(copia, pedido, folha, indices, 300, cancelado=cancelado)
    assert time.monotonic() - inicio < 2.0
    estado.marcadas = {A.CADERNOS}
    copia, pedido, folha, indices = _pedido_da_folha(janela, 1)
    frente, _verso = automatico.folha_do_caderno(copia, pedido, folha, indices, 120)
    assert _paginas_do_lado(frente) == (6, 3)
