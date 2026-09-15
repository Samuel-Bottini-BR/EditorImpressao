"""Aquecimento de dependências pesadas.

Achado ao vivo em 15/09/2026 (py-spy, PID travado logo na abertura do
programa): `core.filtros._medir_k_para_a_letra` importa `skimage.morphology`
(que por sua vez importa `scipy.ndimage`) só na primeira vez que é chamada -
lazy import de propósito, para não pesar a abertura de quem nunca usa o
filtro Preto e branco. O problema: assim que um livro é aberto, várias
tarefas de fundo (miniaturas, prévia, cartões) podem chamar essa função ao
mesmo tempo, e a PRIMEIRA importação de um módulo é serializada pelo lock de
import do próprio Python - todo mundo trava esperando a mesma importação
lenta (scipy é notoriamente pesado, ~1-3s frio), e como isso coincide com
threads também disputando o lock do MuPDF, o usuário via um travamento real
de vários segundos logo ao abrir o programa - repetido a cada abertura,
porque é processo novo toda vez.

Chamar `aquecer_dependencias_pesadas()` uma vez, cedo, numa thread separada,
faz essa importação terminar sozinha antes que qualquer tarefa de fundo
precise dela - as chamadas seguintes de `import` viram apenas uma consulta
em `sys.modules`, instantânea, sem disputa de lock nenhuma.
"""

from __future__ import annotations

import threading


def aquecer_dependencias_pesadas() -> None:
    """Importa/carrega de propósito o que ficaria pesado na primeira chamada.

    Chamado numa thread própria; se falhar por qualquer motivo, não importa -
    o carregamento lento simplesmente volta a acontecer sob demanda, como
    antes.
    """
    try:
        from skimage.morphology import skeletonize  # noqa: F401
    except Exception:  # noqa: BLE001 - aquecimento e so uma otimizacao
        pass

    try:
        # Mesmo achado: carregar o modelo ONNX de layout (72 MB) na primeira
        # vez que uma pagina precisa de deteccao automatica tambem prendeu
        # threads (py-spy, 15/09/2026, `_create_inference_session`). O
        # detector e um singleton do modulo (`_detector`, "carrega uma vez e
        # serve o livro inteiro") - aquecer ESSA mesma instancia aqui faz as
        # chamadas seguintes reaproveitarem a sessao ja carregada.
        from core.detectar_regioes import _detector

        _detector._carregar()  # noqa: SLF001 - aquecimento de propósito
    except Exception:  # noqa: BLE001 - aquecimento e so uma otimizacao
        pass


def aquecer_em_segundo_plano() -> threading.Thread:
    """Dispara o aquecimento numa thread daemon e devolve ela (para testes)."""
    tarefa = threading.Thread(
        target=aquecer_dependencias_pesadas, daemon=True, name="aquecimento"
    )
    tarefa.start()
    return tarefa
