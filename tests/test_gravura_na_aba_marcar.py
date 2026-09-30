"""A aba Marcar e a gravura do ScanTailor (item 1.2, 30/09/2026).

- "detectar automaticamente" usa o MESMO detector e as mesmas opções do livro
  que a prévia e o PDF (antes usava o detector antigo, na prévia filtrada: o
  que o Kaique via ali não era o que ia para o PDF). A marcação à mão fica.
- "Esta página tem foto" troca a forma só desta página (decisão do Samuel:
  "Quero poder trocar também só numa página"), com "usar em todas", "só nas
  próximas" e desfazer/refazer como os outros controles de página.

Com PDF de verdade e o GerenciadorPrevias real (padrão de
tests/test_marcacao_em_todas.py); nenhuma janela aparece (tests/conftest.py).
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

from core import detectar_regioes as dr  # noqa: E402
from core import pipeline  # noqa: E402
from core.selecao import MAO, Selecao, retangulo  # noqa: E402
from historico_acoes import HistoricoAcoes  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def livro(tmp_path):
    caminho = tmp_path / "livro.pdf"
    doc = fitz.open()
    for i in range(4):
        pagina = doc.new_page(width=400, height=560)
        pagina.insert_text((40, 60), f"pagina {i}", fontsize=14)
    doc.save(str(caminho))
    doc.close()
    return caminho


@pytest.fixture
def conferir(app, livro):
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import ABA_MARCAR, TelaConferir

    projeto = Projeto(caminho_entrada=str(livro), nome="x")
    projeto.dividir_folhas = projeto.endireitar = projeto.cortar_bordas = False
    projeto.folhas = [ConfigFolha(indice=i) for i in range(4)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i) for i in range(4)]
    tela = TelaConferir()
    previas = GerenciadorPrevias(str(livro), projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index(ABA_MARCAR))
    yield tela
    previas.parar()


def _com_maquina_e_mao(pagina) -> tuple[dict, dict]:
    s = Selecao()
    maquina = retangulo(0.1, 0.1, 0.5, 0.5, origem="rede")
    a_mao = retangulo(0.6, 0.6, 0.8, 0.8, origem=MAO, filtro="original")
    s.acrescentar(maquina)
    s.acrescentar(a_mao)
    pagina.guardar_selecao(s)
    pagina.gravura_feita_com = dr.assinatura_da_gravura(dr.GRAVURA_SCANTAILOR, dr.OpcoesDaGravura())
    return maquina.para_dicionario(), a_mao.para_dicionario()


def _sem_previas(conferir) -> None:
    """Para as prévias de fundo: senão elas refazem a página ao mesmo tempo
    que o teste olha (a tela pede a prévia de novo depois do botão)."""
    conferir.previas.parar()
    conferir.previas = None


def test_detectar_de_novo_usa_o_caminho_do_programa_e_mantem_a_mao(conferir, monkeypatch):
    _sem_previas(conferir)
    chamadas = []
    monkeypatch.setattr(dr, "detectar", lambda *a, **k: chamadas.append(k))   # não pode ser chamado daqui
    pagina = conferir.projeto.paginas[0]
    maquina, a_mao = _com_maquina_e_mao(pagina)
    conferir._atualizar_marcacao(None, pagina)     # o editor mostra a página

    conferir._detectar_de_novo()

    assert chamadas == [], "a tela não pode chamar o detector direto"
    assert pagina.selecao == [a_mao], "sai só o que a máquina marcou"
    assert pagina.gravura_feita_com == pipeline.REFAZER_A_GRAVURA
    assert pipeline._gravura_a_refazer(conferir.projeto, pagina)
    assert "à mão continua" in conferir.aviso_marcacao.text()


def test_detectar_de_novo_procura_com_as_opcoes_do_livro(conferir, monkeypatch):
    """O que garantir_selecao faz depois do botão: o detector do livro, a mão por cima."""
    import numpy as np

    _sem_previas(conferir)
    conferir.projeto.gravura_forma = "retangular"
    pagina = conferir.projeto.paginas[0]
    _maquina, a_mao = _com_maquina_e_mao(pagina)
    conferir._atualizar_marcacao(None, pagina)
    conferir._detectar_de_novo()
    pedidos = []
    original = dr.detectar

    def espiao(img, *a, **k):
        pedidos.append(k)
        return original(img, *a, **{**k, "usar_layout": False})

    monkeypatch.setattr(dr, "detectar", espiao)
    img = np.full((560, 400, 3), 235, np.uint8)
    img[100:300, 80:320] = 90
    nova = pipeline.garantir_selecao(conferir.projeto, pagina, img, 72, 72)
    assert pedidos[0]["opcoes_da_gravura"].forma == "retangular"
    assert pedidos[0]["detector_de_gravura"] == dr.GRAVURA_SCANTAILOR
    assert nova.regioes[-1].para_dicionario() == a_mao


def test_esta_pagina_tem_foto_troca_so_esta_pagina_e_desfaz(conferir):
    projeto = conferir.projeto
    conferir.ir_para_pagina(1)
    conferir._atualizar_marcacao(None, projeto.paginas[1])
    assert not conferir.caixa_tem_foto.isChecked()

    conferir.caixa_tem_foto.setChecked(True)
    assert projeto.paginas[1].gravura_forma == "retangular"
    assert all(p.gravura_forma is None for i, p in enumerate(projeto.paginas) if i != 1)
    assert pipeline.escolha_da_gravura(projeto, projeto.paginas[1])[1].forma == "retangular"

    conferir.desfazer()
    assert projeto.paginas[1].gravura_forma is None
    conferir.refazer()
    assert projeto.paginas[1].gravura_forma == "retangular"


def test_desmarcar_num_livro_com_fotos_guarda_livre(conferir):
    projeto = conferir.projeto
    projeto.gravura_forma = "retangular"
    conferir._atualizar_marcacao(None, projeto.paginas[0])
    assert conferir.caixa_tem_foto.isChecked(), "segue o livro"
    conferir.caixa_tem_foto.setChecked(False)
    assert projeto.paginas[0].gravura_forma == "livre"
    conferir.caixa_tem_foto.setChecked(True)
    assert projeto.paginas[0].gravura_forma is None, "igual ao livro volta a seguir o livro"


def test_usar_em_todas_e_so_nas_proximas(conferir):
    projeto = conferir.projeto
    conferir.ir_para_pagina(2)
    conferir._atualizar_marcacao(None, projeto.paginas[2])
    conferir.caixa_tem_foto.setChecked(True)
    conferir._forma_nas_proximas()
    assert [p.gravura_forma for p in projeto.paginas] == [None, None, "retangular", "retangular"]
    conferir._forma_em_todas()
    assert all(p.gravura_forma == "retangular" for p in projeto.paginas)
    conferir.desfazer()
    assert [p.gravura_forma for p in projeto.paginas] == [None, None, "retangular", "retangular"]


def test_pagina_de_projeto_antigo_que_muda_de_forma_e_refeita(conferir):
    """Marcação sem assinatura (feita antes do campo) é refeita quando a forma
    da página muda - e só a que muda."""
    projeto = conferir.projeto
    for pagina in projeto.paginas:
        s = Selecao()
        s.acrescentar(retangulo(0.1, 0.1, 0.5, 0.5, origem="rede"))
        pagina.guardar_selecao(s)
    conferir.ir_para_pagina(0)
    conferir._atualizar_marcacao(None, projeto.paginas[0])
    conferir.caixa_tem_foto.setChecked(True)
    assert projeto.paginas[0].gravura_feita_com == pipeline.REFAZER_A_GRAVURA
    assert all(p.gravura_feita_com == "" for p in projeto.paginas[1:])


def test_livro_em_nao_procurar_apaga_a_caixinha(conferir):
    conferir.projeto.gravura_forma = "desligada"
    conferir._atualizar_marcacao(None, conferir.projeto.paginas[0])
    assert not conferir.caixa_tem_foto.isEnabled()
    assert not conferir.caixa_tem_foto.isChecked()
