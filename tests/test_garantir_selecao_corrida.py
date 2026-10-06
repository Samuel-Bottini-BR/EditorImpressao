"""A deteccao de gravura e letra nunca apaga o que a pessoa marcou no meio.

Por que existe (juncao do girar ao fase-1, 06/10/2026): core/pipeline.
garantir_selecao roda no fio da previa, e a deteccao leva quase um segundo.
Ela comecava com a pagina sem marcacao e, ao terminar, gravava o resultado
POR CIMA do que a pessoa tinha marcado na aba Marcar nesse meio-tempo (o
retangulo a mao sumia). Apareceu como falha de vez em quando em
tests/test_ajustar_pedaco_na_aba_marcar.py: a previa gravava a marcacao vazia
por cima do pedaco que o teste acabara de pôr.

Teste de maquina: a "pessoa" marca durante a deteccao (a deteccao falsa
grava a marcacao dela no meio); no fim vale a marcacao dela. Sem ninguem
marcar no meio, a deteccao grava como sempre.
"""

from __future__ import annotations

import numpy as np

from core import pipeline
from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao, retangulo
from modelos import ConfigFolha, ConfigPagina, Projeto


def _projeto() -> Projeto:
    projeto = Projeto(caminho_entrada="x.pdf", nome="corrida")
    projeto.detectar_regioes = True
    projeto.folhas = [ConfigFolha(indice=0)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0)]
    return projeto


def _da_maquina() -> Selecao:
    s = Selecao()
    s.acrescentar(retangulo(0.1, 0.1, 0.9, 0.5, origem="rede"))
    return s


def _da_pessoa() -> Selecao:
    s = Selecao()
    s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.2, 0.2), (0.6, 0.7)],
                         origem=MAO, filtro="original"))
    return s


def test_a_marcacao_feita_durante_a_deteccao_vale(monkeypatch):
    import core.detectar_regioes as dr

    projeto = _projeto()
    pagina = projeto.paginas[0]

    def detectar_enquanto_a_pessoa_marca(*_a, **_k):
        pagina.guardar_selecao(_da_pessoa())        # a tela, no meio da deteccao
        return _da_maquina()

    monkeypatch.setattr(dr, "detectar", detectar_enquanto_a_pessoa_marca)
    img = np.full((60, 40, 3), 230, np.uint8)
    devolvida = pipeline.garantir_selecao(projeto, pagina, img)

    assert pagina.selecao == _da_pessoa().para_lista(), "a deteccao apagou a marcacao a mao"
    assert devolvida.para_lista() == _da_pessoa().para_lista()
    assert not pagina.gravura_feita_com, "anotou uma deteccao que nao foi usada"


def test_sem_ninguem_marcar_a_deteccao_grava_como_sempre(monkeypatch):
    import core.detectar_regioes as dr

    projeto = _projeto()
    pagina = projeto.paginas[0]
    monkeypatch.setattr(dr, "detectar", lambda *_a, **_k: _da_maquina())
    img = np.full((60, 40, 3), 230, np.uint8)
    pipeline.garantir_selecao(projeto, pagina, img)
    assert pagina.selecao == _da_maquina().para_lista()
    assert pagina.gravura_feita_com
