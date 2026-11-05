"""Provas de comportamento da D-623 (04/11/2026): página em branco pelo botão direito na tira.

Samuel (print a-80): "as paginas ainda estão em lugar errado né? eu queria conseguir com botão
direito apertando no meio das paginas aperece opção de adicionar folha em branco."
Livro de decisões: "Botão direito na tira de baixo, numa miniatura (no meio das páginas), tem
“adicionar página em branco antes” e “adicionar página em branco depois”. A página em branco tem o
tamanho das vizinhas, entra no livro, no PDF e nos cadernos; “tirar do livro” a remove; Ctrl+Z
desfaz. Fica no mesmo menu do botão direito da D-621. Muda o modelo de dados (página que não vem do
PDF [...]): projeto antigo abre igual."

O que se mede: a lista de páginas do projeto, o Histórico (Ctrl+Z, Ctrl+Y), o PDF que o programa
grava (core.pipeline.processar, o do "Confirmar e processar"), o PDF com cadernos, a lista do
caderno da etapa 7 (core/automatico.paginas_do_pdf_depois), o livro reaberto e o projeto antigo.
Livro sintético de tests/test_decisoes_ordem_folhas.py: cada folha tem uma faixa preta numa altura
diferente, para saber no PDF qual folha saiu em cada lugar.

Todos falham no código de antes (sem a página posta à mão): relatorios/desfazer-pagina/
reversao-d623.txt.
"""

from __future__ import annotations

import copy

import numpy as np
import pytest

pytest.importorskip("fitz")
pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from tests.test_decisoes_dividir import app, janela, pasta  # noqa: E402,F401  (fixtures)
from tests.test_decisoes_ordem_folhas import (  # noqa: E402
    _aberta,
    _assentar,
    _gerar,
    _livro,
    _pdf,
    _qual,
)


def _branca(img: np.ndarray) -> bool:
    """A página do PDF é toda branca (nenhum ponto escuro)?"""
    return float((img.mean(axis=2) < 200).mean()) < 0.001


def _quais(paginas) -> list:
    """Qual folha saiu em cada página do PDF ("branca" na página em branco)."""
    return ["branca" if _branca(p) else _qual(p) for p in paginas]


def _menu_da_miniatura(tela, quadro: int):
    """Botão direito na miniatura `quadro` da tira (o evento do Qt, como o mouse manda)."""
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QContextMenuEvent
    from PySide6.QtWidgets import QApplication

    from ui.widgets.tira_miniaturas import Miniatura

    tela.show()
    tela.window().show()
    _assentar()
    mini = next(m for m in tela.tira.findChildren(Miniatura) if m.numero == quadro + 1)
    ponto = QPoint(mini.width() // 2, mini.height() // 2)
    QApplication.sendEvent(mini, QContextMenuEvent(QContextMenuEvent.Mouse, ponto,
                                                   mini.mapToGlobal(ponto)))
    _assentar()
    menu = getattr(tela, "_menu_desfazer", None)
    assert menu is not None, "o botão direito na miniatura não abriu menu"
    return menu


def _acao(menu, texto: str):
    acoes = [a for a in menu.actions() if a.text() == texto]
    assert acoes, f"o menu não tem {texto!r}: {[a.text() for a in menu.actions()]}"
    return acoes[0]


# --- o menu e a página nova ---------------------------------------------------------------------

def test_d623_menu_da_miniatura_tem_antes_e_depois_junto_do_desfazer(janela, tmp_path):
    """D-623: o botão direito numa miniatura da tira mostra "adicionar página em branco antes" e
    "adicionar página em branco depois", no mesmo menu do "Desfazer nesta página" (D-621).
    "depois" na miniatura 2 → a página em branco vira a 3 (o exemplo do Livro), do tamanho da 2;
    a tira ganha um quadro; uma ação só no Histórico."""
    janela.abrir_livro(_livro(tmp_path))
    tela, projeto = janela.tela_conferir, janela.projeto
    feitas = len(janela.acoes.feitas)
    menu = _menu_da_miniatura(tela, 1)
    textos = [a.text() for a in menu.actions() if not a.isSeparator()]
    assert textos == ["Desfazer nesta página", "adicionar página em branco antes",
                      "adicionar página em branco depois"]
    _acao(menu, "adicionar página em branco depois").trigger()
    _assentar()
    assert len(projeto.paginas) == 6
    nova = projeto.paginas[2]
    assert nova.inserida > 0 and nova.em_branco and not nova.apagada
    assert [p.indice for p in projeto.paginas] == list(range(6))
    assert len(janela.acoes.feitas) == feitas + 1
    assert len(tela.tira._miniaturas) == 6
    paginas = _gerar(janela, tmp_path, "depois")
    assert _quais(paginas) == [0, 1, "branca", 2, 3, 4]
    assert paginas[2].shape == paginas[1].shape            # do tamanho da vizinha


def test_d623_antes_poe_a_pagina_antes_da_clicada(janela, tmp_path):
    """D-623: "adicionar página em branco antes" na miniatura 1 → a página em branco é a 1."""
    janela.abrir_livro(_livro(tmp_path, folhas=3))
    tela = janela.tela_conferir
    _acao(_menu_da_miniatura(tela, 0), "adicionar página em branco antes").trigger()
    _assentar()
    assert _quais(_gerar(janela, tmp_path, "antes")) == ["branca", 0, 1, 2]


def test_d623_ctrl_z_tira_e_ctrl_y_poe_de_novo(janela, tmp_path):
    """D-623: "Ctrl+Z desfaz": o PDF volta igual, ponto por ponto, ao de antes; o Ctrl+Y põe a
    página em branco de volta no mesmo lugar."""
    janela.abrir_livro(_livro(tmp_path, folhas=4))
    tela, projeto = janela.tela_conferir, janela.projeto
    antes = _gerar(janela, tmp_path, "antes")
    tela.adicionar_pagina_em_branco(1, depois=True)
    assert len(projeto.paginas) == 5
    tela.desfazer()
    assert len(projeto.paginas) == 4 and not any(p.inserida for p in projeto.paginas)
    depois = _gerar(janela, tmp_path, "desfeito")
    assert len(depois) == len(antes) and all(np.array_equal(a, b) for a, b in zip(antes, depois))
    tela.refazer()
    assert [p.inserida > 0 for p in projeto.paginas] == [False, False, True, False, False]
    assert _quais(_gerar(janela, tmp_path, "refeito")) == [0, 1, "branca", 2, 3]


def test_d623_tirar_do_livro_remove_a_pagina_em_branco(janela, tmp_path):
    """D-623: ""tirar do livro" a remove": a página em branco tirada do livro não sai no PDF; o
    Ctrl+Z a traz de volta."""
    janela.abrir_livro(_livro(tmp_path, folhas=3))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela.adicionar_pagina_em_branco(0, depois=True)
    tela.ir_para_pagina(1)
    tela.botao_tirar_do_livro.click()
    assert projeto.paginas[1].apagada
    assert _quais(_gerar(janela, tmp_path, "tirada")) == [0, 1, 2]
    tela.desfazer()
    assert _quais(_gerar(janela, tmp_path, "volta")) == [0, "branca", 1, 2]


def test_d623_entra_nos_cadernos(janela, tmp_path):
    """D-623: a página em branco "entra [...] nos cadernos". Livro de 3 folhas + 1 em branco
    depois da 1 = 4 páginas = um caderno de 4: frente [4 | 1] = [folha 2 | folha 0], verso
    [2 | 3] = [branca | folha 1]. A lista do caderno da etapa 7 também tem a página em branco."""
    from core import automatico as A

    janela.abrir_livro(_livro(tmp_path, folhas=3))
    tela, projeto = janela.tela_conferir, janela.projeto
    projeto.montar_cadernos, projeto.paginas_por_caderno = True, 4
    projeto.limpar = projeto.endireitar = projeto.cortar_bordas = False
    tela.adicionar_pagina_em_branco(0, depois=True)
    assert not projeto.so_cadernos                 # o caminho rápido monta só com as folhas
    lista = A.paginas_do_pdf_depois(projeto, A.Pedido(etapas=[A.DIVIDIR]))
    assert len(lista) == 4
    paginas = _gerar(janela, tmp_path, "cadernos")
    assert len(paginas) == 2
    frente, verso = paginas
    meio = frente.shape[1] // 2
    assert _qual(frente[:, meio:]) == 0 and _qual(frente[:, :meio]) == 2
    assert _branca(verso[:, :meio]) and _qual(verso[:, meio:]) == 1


def test_d623_folha_dividida_a_pagina_em_branco_nao_e_da_folha(janela, tmp_path):
    """A página em branco tem o tamanho da vizinha (a metade da folha dividida), mas não é "da
    folha": "não dividir esta" na folha junta só as duas páginas dela e a página em branco fica
    no lugar; o Ctrl+Z devolve tudo."""
    from core import dividir_a_mao

    janela.abrir_livro(_pdf(tmp_path / "abertas.pdf", [_aberta(n) for n in range(2)]))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela._registrar("dividir_a_mao", "folha", [0],
                    dividir_a_mao.campos_para_dividir(projeto, 0, 0.5), "dividir")
    assert [(p.folha, p.metade) for p in projeto.paginas] == [
        (0, "esquerda"), (0, "direita"), (1, "inteira")]
    tela.adicionar_pagina_em_branco(0, depois=True)          # entre as duas metades
    paginas = _gerar(janela, tmp_path, "dividida")
    assert len(paginas) == 4 and _branca(paginas[1]) and paginas[1].shape == paginas[0].shape
    tela._registrar("juntar_a_mao", "folha", [0], dividir_a_mao.campos_para_juntar(projeto, 0),
                    "juntar")
    assert [(p.metade, p.inserida > 0) for p in projeto.paginas] == [
        ("inteira", False), ("esquerda", True), ("inteira", False)]
    assert _quais(_gerar(janela, tmp_path, "juntada"))[1] == "branca"
    tela.desfazer()
    tela.desfazer()
    assert len(projeto.paginas) == 3 and not any(p.inserida for p in projeto.paginas)


def test_d623_mudar_de_lugar_arrastando_vale_para_a_pagina_em_branco(janela, tmp_path):
    """D-615 + D-623: a página em branco muda de lugar como as outras (anda sozinha) e o Ctrl+Z
    a devolve."""
    from core import ordem_das_paginas as O

    janela.abrir_livro(_livro(tmp_path, folhas=3))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela.adicionar_pagina_em_branco(0, depois=True)
    assert O.bloco(projeto, 1) == [1]
    tela._registrar("mudar_de_lugar", "pagina", [], O.campos_para_mover(projeto, [1], None),
                    "mover")
    assert _quais(_gerar(janela, tmp_path, "movida")) == [0, 1, 2, "branca"]
    tela.desfazer()
    assert _quais(_gerar(janela, tmp_path, "devolvida")) == [0, "branca", 1, 2]


def test_d623_fechar_e_abrir_mantem_a_pagina_em_branco(janela, tmp_path):
    """Fechar e abrir o projeto mantém a página em branco (e o Ctrl+Z dela)."""
    caminho = _livro(tmp_path, folhas=3)
    janela.abrir_livro(caminho)
    janela.tela_conferir.adicionar_pagina_em_branco(2, depois=False)
    janela._salvar_agora()
    janela.abrir_livro(caminho)
    assert [p.inserida > 0 for p in janela.projeto.paginas] == [False, False, True, False]
    assert _quais(_gerar(janela, tmp_path, "reaberto")) == [0, 1, "branca", 2]
    janela.tela_conferir.desfazer()
    assert len(janela.projeto.paginas) == 3


def test_d623_projeto_antigo_abre_igual(tmp_path):
    """Projeto gravado antes (sem o campo "inserida" nas páginas) abre igual: nenhuma página é
    posta à mão, o projeto gravado de novo é igual ao de antes mais o campo com 0."""
    from modelos import ConfigFolha, ConfigPagina, Projeto

    projeto = Projeto(caminho_entrada=str(tmp_path / "x.pdf"))
    projeto.folhas = [ConfigFolha(indice=i) for i in range(2)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i) for i in range(2)]
    dados = projeto.para_dicionario()
    for pagina in dados["paginas"]:
        pagina.pop("inserida", None)                       # como o projeto.json de antes
    aberto = Projeto.de_dicionario(copy.deepcopy(dados))
    assert [p.inserida for p in aberto.paginas] == [0, 0]
    assert len(aberto.paginas_ativas) == 2


# --- a tela mostra a página posta como ela sai: branca (defeito B do verificador, 05/11/2026) ----
# relatorios/verificacao-04-11/relatorio.md, §5: "A página posta em branco, no Cortar, mostra a
# imagem da página vizinha [...] Se o Kaique apertar "voltar a página", [...] a faixa diz "Esta
# página vai sair em Original" — mas o PDF continua saindo branco". Gerente (05/11): "a página
# posta em branco aparece branca na tela, em todas as ferramentas, igual ao PDF (D-623). A faixa
# não pode dizer que ela vai sair diferente do que sai." (D-637: a tela e o PDF concordam.)

FRASE_DO_BRANCO = "Esta página vai sair em branco (uma folha branca no lugar dela)."


def _imagem_do(vis) -> np.ndarray:
    from PySide6.QtGui import QImage

    img = vis._pixmap.toImage().convertToFormat(QImage.Format_RGB32)
    largura, altura = img.width(), img.height()
    pontos = np.frombuffer(img.constBits(), np.uint8).reshape(altura, img.bytesPerLine() // 4, 4)
    return pontos[:, :largura, :3]


def _esperar(condicao, limite: float = 90.0) -> bool:
    import time

    fim = time.time() + limite
    while time.time() < fim:
        _assentar()
        if condicao():
            return True
        time.sleep(0.05)
    return False


def _na_ferramenta(tela, ferramenta: str, indice: int):
    """Escolhe a ferramenta, vai à página `indice` e espera a imagem dela chegar na tela."""
    from ui.tela_conferir import ABA_DA_FERRAMENTA

    tela.show()
    tela.window().show()
    tela.escolher_ferramenta(ferramenta)
    tela.ir_para_pagina(indice)
    vis = tela.visualizadores[ABA_DA_FERRAMENTA[ferramenta]]
    assert _esperar(lambda: vis._pixmap is not None and not vis.carregando), \
        f"a imagem da página não chegou no {ferramenta}"
    return vis


def _branca_na_tela(img: np.ndarray) -> bool:
    return float((np.asarray(img).reshape(-1, img.shape[-1] if img.ndim == 3 else 1)
                  .mean(axis=1) < 200).mean()) < 0.001


def test_d623_a_pagina_posta_aparece_branca_no_cortar_e_nos_cartoes_do_filtro(janela, tmp_path):
    """Defeito B (05/11): no Cortar a página posta mostrava a imagem da vizinha, e os cartões
    Preto e branco / Melhorar / Mágico pro mostravam a vizinha com o filtro. O PDF sai branco: a
    tela também (em todas as ferramentas da página: Cortar, Endireitar, Mover, Filtros)."""
    from ui.widgets.trilha_agrupada import (FERRAMENTA_CORTAR, FERRAMENTA_ENDIREITAR,
                                            FERRAMENTA_FILTROS, FERRAMENTA_MOVER)

    janela.abrir_livro(_livro(tmp_path, folhas=3))
    tela = janela.tela_conferir
    tela.adicionar_pagina_em_branco(1, depois=True)
    for ferramenta in (FERRAMENTA_CORTAR, FERRAMENTA_ENDIREITAR, FERRAMENTA_MOVER):
        vis = _na_ferramenta(tela, ferramenta, 2)
        assert _branca_na_tela(_imagem_do(vis)), f"no {ferramenta} a página posta não é branca"
        assert tela.texto_faixa.text().startswith(FRASE_DO_BRANCO)
    # a vizinha (página 2) continua com a imagem dela no Cortar
    assert not _branca_na_tela(_imagem_do(_na_ferramenta(tela, FERRAMENTA_CORTAR, 1)))
    tela.escolher_ferramenta(FERRAMENTA_FILTROS)
    tela.ir_para_pagina(2)
    assert _esperar(lambda: all(c.ultima_amostra is not None for c in tela.cartoes.values()))
    for chave, cartao in tela.cartoes.items():
        assert _branca_na_tela(cartao.ultima_amostra), f"o cartão {chave} não é branco"
    assert _quais(_gerar(janela, tmp_path, "pdf")) == [0, 1, "branca", 2]


def test_d623_voltar_a_pagina_na_posta_a_faixa_diz_como_ela_sai(janela, tmp_path):
    """Defeito B (05/11): na página posta, depois do "voltar a página" a faixa dizia "Esta página
    vai sair em Original" e a tela mostrava a vizinha, mas o PDF sai branco. A faixa e a tela dizem
    o que sai: branca. O botão continua o mesmo (não se tira nem se põe botão: §6)."""
    from ui.widgets.trilha_agrupada import FERRAMENTA_CORTAR, FERRAMENTA_FILTROS

    janela.abrir_livro(_livro(tmp_path, folhas=3))
    tela, projeto = janela.tela_conferir, janela.projeto
    tela.adicionar_pagina_em_branco(1, depois=True)
    _na_ferramenta(tela, FERRAMENTA_CORTAR, 2)
    assert tela.botao_em_branco.text() == "voltar a página"
    tela.botao_em_branco.click()
    _assentar()
    assert projeto.paginas[2].em_branco is False         # o botão fez o que sempre fez
    vis = _na_ferramenta(tela, FERRAMENTA_CORTAR, 2)
    assert _branca_na_tela(_imagem_do(vis))
    assert tela.texto_faixa.text().startswith(FRASE_DO_BRANCO), tela.texto_faixa.text()
    tela.escolher_ferramenta(FERRAMENTA_FILTROS)
    tela.ir_para_pagina(2)
    _assentar()
    assert tela.texto_faixa.text().startswith(FRASE_DO_BRANCO), tela.texto_faixa.text()
    assert _quais(_gerar(janela, tmp_path, "pdf")) == [0, 1, "branca", 2]
