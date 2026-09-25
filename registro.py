"""Arquivo de log.

Regra 3.3: o erro técnico vai para o arquivo, nunca para a tela. Na tela o
usuario le uma frase em portugues e o programa continua aberto.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

_ARQUIVO = "erros.log"
_TAMANHO_MAXIMO = 1_000_000  # 1 MB: passou disso, recomeca


def caminho_do_log() -> Path:
    """Onde o erros.log mora - dentro da pasta de dados do programa (%LOCALAPPDATA%)."""
    from historico import pasta_de_dados

    return pasta_de_dados() / _ARQUIVO


def registrar_erro(origem: str, detalhe: str) -> None:
    """Anota um erro. Nunca levanta excecao - seria ironico."""
    try:
        caminho = caminho_do_log()
        if caminho.exists() and caminho.stat().st_size > _TAMANHO_MAXIMO:
            caminho.unlink(missing_ok=True)
        momento = datetime.now().isoformat(timespec="seconds")
        with caminho.open("a", encoding="utf-8") as arquivo:
            arquivo.write(f"\n===== {momento} | {origem} =====\n{detalhe}\n")
    except Exception:  # noqa: BLE001
        pass
