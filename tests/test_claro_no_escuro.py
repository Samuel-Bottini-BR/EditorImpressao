"""Texto claro em fundo escuro (item 2.9 da Fase 2, 20/10/2026).

Decisão do Samuel P9 (a), 05/10/2026: caixinha por página, marcada à mão.
Igual ao ScanTailor: a página é invertida na entrada, tratada como uma página
comum (marcação de gravura inclusive) e invertida de novo no fim.

Testes de máquina:
- de fábrica a caixinha vem desmarcada, e projeto salvo antes abre desmarcado;
- com ela, a página de letra clara em fundo escuro sai no Preto e branco com a
  letra BRANCA e o fundo PRETO (como no livro, só que limpa); sem ela, a mesma
  página sai quase toda preta (o defeito que a caixinha resolve);
- é exatamente "inverter, o caminho de sempre, inverter";
- Original e "Tirar o fundo" não mudam;
- a assinatura da marcação de gravura só muda com a caixinha LIGADA (livro já
  começado não refaz nada); ligar refaz a parte automática.
"""

from __future__ import annotations

import numpy as np

from core import claro_no_escuro as cne
from core import pipeline as P
from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO, TIRAR_FUNDO
from modelos import ConfigFolha, ConfigPagina, Projeto


def pagina_clara_no_escuro(largura: int = 600, altura: int = 400) -> np.ndarray:
    """Fundo escuro (35) com linhas de letras claras (215) e um pouco de grão."""
    rng = np.random.default_rng(3)
    img = np.full((altura, largura), 35.0, np.float32)
    for linha in range(4):
        y0 = 60 + linha * 80
        for k in range(20):
            img[y0:y0 + 30, 40 + k * 26:46 + k * 26] = 215
    img = np.clip(img + rng.normal(0, 5, img.shape), 0, 255).astype(np.uint8)
    return np.dstack([img, img, img])


def letras(forma) -> np.ndarray:
    m = np.zeros(forma[:2], bool)
    for linha in range(4):
        y0 = 60 + linha * 80
        for k in range(20):
            m[y0:y0 + 30, 40 + k * 26:46 + k * 26] = True
    return m


def projeto_e_pagina(filtro=PRETO_E_BRANCO, claro=False):
    projeto = Projeto(caminho_entrada="x.pdf", detectar_regioes=False)
    projeto.folhas = [ConfigFolha(indice=0, dividir=False)]
    pagina = ConfigPagina(indice=0, folha=0, filtro=filtro)
    pagina.claro_no_escuro = claro
    projeto.paginas = [pagina]
    return projeto, pagina


def test_de_fabrica_desmarcada_e_projeto_antigo_abre_desmarcado():
    assert ConfigPagina(indice=0, folha=0).claro_no_escuro is False
    assert not cne.ligado(ConfigPagina(indice=0, folha=0))
    assert not cne.ligado(object())          # objeto de antes do campo existir
    projeto, pagina = projeto_e_pagina()
    dados = projeto.para_dicionario()
    for p in dados["paginas"]:
        p.pop("claro_no_escuro", None)       # salvo antes do item 2.9
    assert Projeto.de_dicionario(dados).paginas[0].claro_no_escuro is False
    pagina.claro_no_escuro = True
    assert Projeto.de_dicionario(projeto.para_dicionario()).paginas[0].claro_no_escuro is True


def test_inverter_e_o_do_scantailor():
    img = np.array([[0, 10, 255]], np.uint8)
    assert np.array_equal(cne.inverter(img), [[255, 245, 0]])
    cor = np.zeros((2, 2, 3), np.uint8)
    assert (cne.inverter(cor) == 255).all() and (cor == 0).all(), "não mexe na entrada"


def test_com_a_caixinha_a_letra_sai_branca_no_fundo_preto():
    img = pagina_clara_no_escuro()
    m = letras(img.shape)
    projeto, pagina = projeto_e_pagina(claro=True)
    saida, mono = P._filtrar(projeto, pagina, img)
    assert mono
    assert (saida[m] == 255).mean() > 0.9, "a letra tinha de sair branca"
    assert (saida[~m] == 0).mean() > 0.9, "o fundo tinha de sair preto"


def test_sem_a_caixinha_a_mesma_pagina_sai_errada():
    """O defeito que a caixinha resolve: sem ela, a página escura vira um
    borrão (o fundo escuro é lido como tinta)."""
    img = pagina_clara_no_escuro()
    m = letras(img.shape)
    projeto, pagina = projeto_e_pagina(claro=False)
    saida, _ = P._filtrar(projeto, pagina, img)
    com, _ = P._filtrar(*projeto_e_pagina(claro=True), img)
    assert not np.array_equal(saida, com)
    # sem a caixinha a letra NÃO sai branca em fundo preto limpo
    assert not ((saida[m] == 255).mean() > 0.9 and (saida[~m] == 0).mean() > 0.9)


def test_e_inverter_o_caminho_de_sempre_e_inverter():
    img = pagina_clara_no_escuro()
    for filtro in (PRETO_E_BRANCO, MELHORAR):
        com, _ = P._filtrar(*projeto_e_pagina(filtro, claro=True), img)
        sem, _ = P._filtrar(*projeto_e_pagina(filtro, claro=False), cne.inverter(img))
        assert np.array_equal(com, cne.inverter(sem)), filtro


def test_original_e_tirar_o_fundo_nao_mudam():
    img = pagina_clara_no_escuro()
    for filtro in (ORIGINAL, TIRAR_FUNDO):
        com, _ = P._filtrar(*projeto_e_pagina(filtro, claro=True), img)
        assert np.array_equal(com, img), filtro


def test_a_assinatura_da_gravura_so_muda_com_a_caixinha_ligada():
    from core.detectar_regioes import assinatura_da_gravura

    projeto, pagina = projeto_e_pagina()
    de_sempre = assinatura_da_gravura(*P.escolha_da_gravura(projeto, pagina))
    assert P._assinatura_da_gravura_da_pagina(projeto, pagina) == de_sempre
    pagina.claro_no_escuro = True
    assert P._assinatura_da_gravura_da_pagina(projeto, pagina) == de_sempre + cne.SUFIXO_DA_GRAVURA


def test_ligar_a_caixinha_refaz_a_marcacao_automatica():
    from core.detectar_regioes import assinatura_da_gravura

    projeto, pagina = projeto_e_pagina()
    pagina.selecao = [{"forma": "retangulo"}]          # uma marcação qualquer, guardada
    pagina.gravura_feita_com = assinatura_da_gravura(*P.escolha_da_gravura(projeto, pagina))
    assert not P._gravura_a_refazer(projeto, pagina)
    pagina.claro_no_escuro = True
    assert P._gravura_a_refazer(projeto, pagina)
