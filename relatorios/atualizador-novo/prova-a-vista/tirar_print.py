"""Tira um print da tela inteira (todas as telas) na prova à vista. NÃO é parte do programa. SÓ LÊ a tela.

    python tirar_print.py p02-aviso-da-versao-nova

Grava <BASE>\\prints\\<nome>-<HHMMSS>.png e diz o caminho. A pergunta do Windows ("Deseja permitir...?") NÃO sai em
print nenhum (o Windows a mostra numa área protegida): dela, a foto é do celular do Samuel.

Não rodado antes da prova (rodar agora tiraria print da tela do Samuel, com o que ele estiver fazendo).
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from PIL import ImageGrab

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import prova_comum as comum  # noqa: E402


def main(argumentos: list[str]) -> int:
    """Um print com o nome dado."""
    if len(argumentos) != 1 or not argumentos[0].replace("-", "").isalnum():
        print(__doc__)
        return 1
    pasta = comum.BASE / "prints"
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"{argumentos[0]}-{datetime.now():%H%M%S}.png"
    ImageGrab.grab(all_screens=True).save(destino)
    print(destino)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
