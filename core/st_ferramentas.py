"""A DLL comum das ferramentas do ScanTailor Advanced (item M9 da Fase 2, 06/10/2026).

O QUE FAZ
    Abre core/nativo/st_ferramentas.dll - o código original do ScanTailor
    Advanced v1.2.1 (terceiros/scantailor-advanced/src, GPL-3, sem mudança)
    mais uma "ligação" nossa em C (terceiros/scantailor-advanced/
    ligacao-ferramentas) - e entrega as funções dela já com os tipos certos
    para o ctypes. Não depende da versão do Python. Usa o Qt que o PySide6 já
    traz (a pasta do PySide6 entra na busca de DLLs, como no item 1.2).

    É o mesmo jeito do detector de gravura do item 1.2
    (core/gravura_scantailor.py + st_gravura.dll), feito para receber as
    outras ferramentas sem refazer nada: cada ferramenta é um módulo em core/
    que pede a função aqui (hoje: core/pontinhos_scantailor.py, limpar
    pontinhos). Ver "Duas DLLs" em terceiros/scantailor-advanced/LEIA-ME.md.

    Recompilar: .venv\\Scripts\\python.exe compilar_st_ferramentas.py

SE A DLL FALTAR OU FALHAR
    Nada levanta exceção: `disponivel` fica False e `motivo_indisponivel` diz
    por quê, em português; o detalhe técnico vai para o log. Quem chama decide
    o que fazer (por exemplo, usar o que o programa já tem).

O QUE É SEGURO MUDAR
    Os textos das mensagens.

O QUE É ARRISCADO
    - ASSINATURAS: os tipos de cada função em C. O ctypes não confere nada; um
      tipo errado aqui vira travamento, não mensagem. Tem de bater, linha a
      linha, com terceiros/scantailor-advanced/ligacao-ferramentas/st_ferramentas.h.
    - VERSAO_API: tem de bater com ST_FERRAMENTAS_VERSAO_API do .h. A DLL de
      outra versão é recusada (melhor recusar do que chamar com tipos velhos).
    - DPI_MINIMO/DPI_MAXIMO e PONTOS_MAXIMOS: a mesma trava do item 1.2 (ver
      core/gravura_scantailor.py, TRAVA DE SEGURANÇA). Não afrouxar sem medir
      em processo filho.
"""

from __future__ import annotations

import ctypes
import logging
import os
import threading
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_log = logging.getLogger(__name__)

CAMINHO_DLL = Path(__file__).resolve().parent / "nativo" / "st_ferramentas.dll"

# Tem de bater com ST_FERRAMENTAS_VERSAO_API em st_ferramentas.h.
VERSAO_API = 1

# Códigos de st_ferramentas.h (iguais para todas as funções).
OK, ERRO_PARAMETRO, ERRO_MEMORIA, ERRO_INTERNO = 0, 1, 2, 3

# A mesma trava do item 1.2 (core/gravura_scantailor.py).
DPI_MINIMO = 30
DPI_MAXIMO = 2400
PONTOS_MAXIMOS = 120_000_000

# Os tipos de cada função em C: (tipo de volta, [tipos dos argumentos]).
# Copiado de st_ferramentas.h - ver "ARRISCADO" no topo.
ASSINATURAS = {
    "st_ferramentas_versao_api": (ctypes.c_int, []),
    "st_ferramentas_origem": (ctypes.c_char_p, []),
    "st_ferramentas_pontinhos": (ctypes.c_int, [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int,   # entrada, largura, altura, passo
        ctypes.c_int, ctypes.c_int,                                  # dpi x, y
        ctypes.c_double,                                             # força
        ctypes.c_void_p, ctypes.c_int,                               # saída, passo
        ctypes.c_char_p, ctypes.c_int,                               # erro
    ]),
}


@dataclass(frozen=True)
class Resultado:
    """O que uma ferramenta devolve.

    imagem: o resultado (numpy), ou None se ficou indisponível.
    motivo: por que ficou indisponível, em português (para a tela). None se deu certo.
    detalhe_tecnico: o erro de verdade, para o erros.log (nunca para a tela).
    segundos: quanto a DLL levou.
    """

    imagem: np.ndarray | None
    motivo: str | None = None
    detalhe_tecnico: str | None = None
    segundos: float = 0.0

    @property
    def disponivel(self) -> bool:
        return self.imagem is not None


def indisponivel(motivo: str, detalhe: str | None = None) -> Resultado:
    """Resultado "indisponível", com o detalhe no log."""
    if detalhe:
        _log.warning("st_ferramentas: %s (%s)", motivo, detalhe)
    return Resultado(None, motivo, detalhe)


def dpi_inteiro(dpi) -> tuple[int, int]:
    """(x, y) inteiros: o ScanTailor guarda o DPI como número inteiro (classe Dpi).

    Aceita um número ou um par. Levanta ValueError se não for positivo.
    """
    if isinstance(dpi, (int, float, np.integer, np.floating)):
        x = y = float(dpi)
    else:
        x, y = (float(v) for v in dpi)
    x_i, y_i = int(round(x)), int(round(y))
    if x_i <= 0 or y_i <= 0:
        raise ValueError(f"DPI inválido: {dpi!r}")
    return x_i, y_i


def motivo_de_recusa(largura: int, altura: int, dpi_x: int, dpi_y: int,
                     nome: str = "a ferramenta do ScanTailor") -> str | None:
    """Por que a imagem NÃO pode ir para a DLL, ou None (ver a trava no topo)."""
    for dpi in (dpi_x, dpi_y):
        if not DPI_MINIMO <= dpi <= DPI_MAXIMO:
            return (f"O DPI da página ({dpi}) está fora da faixa que {nome} aceita "
                    f"({DPI_MINIMO} a {DPI_MAXIMO}).")
    if largura <= 0 or altura <= 0:
        return f"A página está vazia para {nome}."
    if largura * altura > PONTOS_MAXIMOS:
        return f"A página é grande demais para {nome}."
    return None


class BibliotecaScanTailor:
    """A st_ferramentas.dll. Abre uma vez (na primeira chamada) e serve o livro inteiro.

    Pode ser chamada de uma QThread: enquanto a DLL trabalha, o ctypes solta o
    GIL, e a tela continua respondendo.
    """

    def __init__(self, caminho: Path | None = None) -> None:
        self.caminho = Path(caminho or CAMINHO_DLL).resolve()   # o ctypes quer caminho completo
        self._dll = None
        self._tentou = False
        self._motivo: str | None = None
        self._detalhe: str | None = None
        self._pasta_do_qt = None   # guarda o registro da pasta de DLLs do PySide6
        self._tranca = threading.Lock()

    def _carregar(self):
        """Abre a DLL uma única vez. Em caso de falha, guarda o motivo e devolve None."""
        with self._tranca:
            if self._tentou:
                return self._dll
            self._tentou = True
            if os.name != "nt":
                self._motivo = "As ferramentas do ScanTailor só existem para Windows."
                return None
            if not self.caminho.is_file():
                self._motivo = ("As ferramentas do ScanTailor não foram encontradas "
                                f"(falta {self.caminho.name}).")
                return None
            try:
                # A DLL usa o Qt6Core/Qt6Gui do PySide6: a pasta dele entra na busca de DLLs.
                import PySide6

                self._pasta_do_qt = os.add_dll_directory(str(Path(PySide6.__file__).parent))
                dll = ctypes.CDLL(str(self.caminho))
                for nome, (volta, argumentos) in ASSINATURAS.items():
                    funcao = getattr(dll, nome)
                    funcao.restype = volta
                    funcao.argtypes = argumentos
                versao = dll.st_ferramentas_versao_api()
            except Exception as erro:  # noqa: BLE001 - nada aqui pode derrubar o programa
                self._motivo = "As ferramentas do ScanTailor não abriram."
                self._detalhe = f"{type(erro).__name__}: {erro}"
                _log.warning("st_ferramentas: %s", self._detalhe)
                return None
            if versao != VERSAO_API:
                self._motivo = ("As ferramentas do ScanTailor são de outra versão "
                                "(recompile com compilar_st_ferramentas.py).")
                self._detalhe = f"versão da DLL {versao}, esperada {VERSAO_API}"
                return None
            self._dll = dll
            return dll

    @property
    def disponivel(self) -> bool:
        """A DLL existe e abriu?"""
        return self._carregar() is not None

    @property
    def motivo_indisponivel(self) -> str | None:
        self._carregar()
        return self._motivo

    @property
    def detalhe_indisponivel(self) -> str | None:
        self._carregar()
        return self._detalhe

    @property
    def origem(self) -> str | None:
        """De onde veio o código (repositório, versão, commit), gravado na DLL."""
        dll = self._carregar()
        if dll is None:
            return None
        return dll.st_ferramentas_origem().decode("utf-8", "replace")

    def funcao(self, nome: str):
        """A função em C já com os tipos (ASSINATURAS), ou None se a DLL não abriu."""
        dll = self._carregar()
        if dll is None:
            return None
        return getattr(dll, nome)


_padrao = BibliotecaScanTailor()


def padrao() -> BibliotecaScanTailor:
    """A biblioteca do programa (a de core/nativo/), aberta uma vez só."""
    return _padrao


def disponivel() -> bool:
    return _padrao.disponivel


def origem() -> str | None:
    return _padrao.origem
