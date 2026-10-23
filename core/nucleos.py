"""Item 2.16: usar todos os núcleos do processador, igual ao ScanTailor.

O QUE FAZ
    O ScanTailor processa várias páginas ao mesmo tempo, uma por linha de
    execução (`src/core/WorkerThreadPool.cpp`): de fábrica, tantas quantos
    núcleos o computador tem (`QThread::idealThreadCount()`), e a pessoa pode
    escolher menos ("settings/batch_processing_threads"). Aqui é a mesma ideia
    para as duas passadas longas do programa: a análise do livro e o processar
    (o PDF final).

    `em_ordem` entrega os resultados NA ORDEM das páginas, com no máximo
    `trabalhadores` páginas sendo feitas ao mesmo tempo: o PDF sai idêntico ao
    de uma linha só (cada página é feita pela mesma conta, só em paralelo).

A REGRA "UMA PÁGINA POR VEZ NA MEMÓRIA" (CLAUDE.md §3)
    Vale POR TRABALHADOR: cada um tem a sua folha da vez, e nunca há lista com
    as páginas do livro - quem fica pronto antes da vez espera no máximo
    `trabalhadores` lugares (a fila tem esse tamanho). O pico cresce com o
    número de trabalhadores, NUNCA com o tamanho do livro. Para não faltar
    memória, `quantos_trabalhadores` corta o número pela memória livre
    (MEMORIA_POR_TRABALHADOR_MB cada, e RESERVA_MB para o resto do Windows).

POR QUE LINHAS (threads) E NÃO PROCESSOS
    O pesado já solta o Python: o OpenCV e o numpy, as DLLs do ScanTailor pelo
    ctypes, e o desenho do PDF, que vai para os servidores de páginas
    (core/paginas_em_outro_processo.py). As prévias da tela já rodam assim, com
    duas ou três ao mesmo tempo (ui/tarefas.GerenciadorPrevias), e as partes
    que não podem andar juntas já têm tranca (as caches do pipeline, o leitor
    de texto, o motor do Kraken). Processos teriam de carregar cada modelo de
    novo (memória vezes N).

DESLIGAR (regra 8 do plano): é preferência da máquina (não do livro), no
    configuracoes.json, chave "nucleos" (0 = todos, como o ScanTailor; 1 = uma
    página por vez, como era antes), escolhida em Configurações. Mexe só na
    velocidade, nunca na imagem.

SEGURO MUDAR: MEMORIA_POR_TRABALHADOR_MB, RESERVA_MB, MAXIMO (só velocidade e
    memória). ARRISCADO: deixar a fila sem limite (a memória cresceria com o
    livro) ou entregar fora de ordem (as páginas do PDF trocariam de lugar).
"""

from __future__ import annotations

import ctypes
import os
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, Iterator, TypeVar

T = TypeVar("T")
R = TypeVar("R")

# Uma folha de 300 DPI em cor com as cópias do preparo e do filtro passa de
# 300 MB nas folhas grandes do acervo (Antiphon: 38 milhões de pontos). Conta
# folgada de propósito: faltar memória é pior que ir um pouco mais devagar.
MEMORIA_POR_TRABALHADOR_MB = 900
RESERVA_MB = 1500
MAXIMO = 16

CHAVE_DAS_CONFIGURACOES = "nucleos"


def memoria_livre_mb() -> float | None:
    """A memória livre do Windows, em MB (None fora do Windows ou se falhar)."""
    if os.name != "nt":
        return None

    class _Estado(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

    estado = _Estado()
    estado.dwLength = ctypes.sizeof(_Estado)
    try:
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(estado)):
            return None
    except Exception:  # noqa: BLE001
        return None
    return estado.ullAvailPhys / (1024 * 1024)


def pedido_da_maquina() -> int:
    """O que está no configuracoes.json: 0 = todos os núcleos (de fábrica, como
    o ScanTailor), 1 = uma página por vez, N = no máximo N."""
    try:
        import configuracoes

        valor = int(configuracoes.ler(CHAVE_DAS_CONFIGURACOES) or 0)
    except Exception:  # noqa: BLE001 - configuração quebrada não para o programa
        valor = 0
    return max(0, valor)


def quantos_trabalhadores(pedido: int | None = None, memoria_mb: float | None = None,
                          nucleos: int | None = None) -> int:
    """Quantas páginas ao mesmo tempo: os núcleos (ou o pedido, se menor),
    cortado pela memória livre. Nunca menos de 1."""
    if pedido is None:
        pedido = pedido_da_maquina()
    nucleos = nucleos or os.cpu_count() or 1
    n = nucleos if pedido <= 0 else min(nucleos, pedido)
    if memoria_mb is None:
        memoria_mb = memoria_livre_mb()
    if memoria_mb is not None:
        n = min(n, max(1, int((memoria_mb - RESERVA_MB) // MEMORIA_POR_TRABALHADOR_MB)))
    return max(1, min(n, MAXIMO))


def em_ordem(itens: Iterable[T], fazer: Callable[[T], R], trabalhadores: int,
             cancelado: Callable[[], bool] | None = None) -> Iterator[tuple[T, R]]:
    """Faz `fazer(item)` em até `trabalhadores` linhas ao mesmo tempo e entrega
    (item, resultado) na ordem dos itens. Com 1 trabalhador, faz tudo aqui
    mesmo, sem linha nenhuma (o comportamento de antes).

    No máximo `trabalhadores` itens estão em andamento ou prontos esperando a
    vez. Um erro em qualquer item sobe na vez dele (os seguintes são
    abandonados); `cancelado()` verdadeiro para de pôr itens novos (os em
    andamento terminam e são jogados fora)."""
    if trabalhadores <= 1:
        for item in itens:
            if cancelado is not None and cancelado():
                return
            yield item, fazer(item)
        return

    fila: deque = deque()
    iterador = iter(itens)
    with ThreadPoolExecutor(max_workers=trabalhadores, thread_name_prefix="pagina") as executor:
        try:
            def encher() -> None:
                while len(fila) < trabalhadores:
                    if cancelado is not None and cancelado():
                        return
                    try:
                        item = next(iterador)
                    except StopIteration:
                        return
                    fila.append((item, executor.submit(fazer, item)))

            encher()
            while fila:
                item, futuro = fila.popleft()
                resultado = futuro.result()
                encher()
                yield item, resultado
        finally:
            for _item, futuro in fila:
                futuro.cancel()
