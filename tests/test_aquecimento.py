"""O aquecimento antecipa o import pesado que causava disputa de lock.

Ver core/aquecimento.py para o achado ao vivo (py-spy, 15/09/2026): duas
tarefas de fundo travando juntas na primeira importação de skimage/scipy
logo ao abrir um livro.
"""

from __future__ import annotations

import sys


def test_aquecer_importa_o_modulo_que_o_filtro_precisa():
    sys.modules.pop("skimage.morphology", None)

    from core.aquecimento import aquecer_dependencias_pesadas

    aquecer_dependencias_pesadas()

    assert "skimage.morphology" in sys.modules, (
        "o aquecimento devia deixar o import pronto para as tarefas de fundo"
    )


def test_aquecer_em_segundo_plano_nao_bloqueia_e_nao_quebra():
    from core.aquecimento import aquecer_em_segundo_plano

    tarefa = aquecer_em_segundo_plano()
    tarefa.join(timeout=15)

    assert not tarefa.is_alive(), "o aquecimento nao terminou a tempo"


def test_aquecer_tambem_carrega_o_modelo_de_layout():
    """Achado ao vivo (py-spy, 15/09/2026): `_create_inference_session` do
    modelo de layout (72 MB) também prendia threads na primeira detecção
    automática de uma página. O detector é um singleton do módulo - aquecer
    deve deixar ELE MESMO já carregado.
    """
    from core.aquecimento import aquecer_dependencias_pesadas
    from core.detectar_regioes import _detector

    _detector._tentou = False
    _detector._sessao = None

    aquecer_dependencias_pesadas()

    assert _detector._tentou, "o aquecimento devia ter tentado carregar o modelo"
