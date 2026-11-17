"""Abre e fecha a tela de carregamento (o brasao girando), do lado do programa.

Decisoes do Samuel de 17/11/2026: D-744 ("enquanto carrega o programa"),
D-745 (volta inteira, sem fundo, sem quadro), D-747 ("brasão aprovado").
O desenho e o giro estao em ui/brasao_girando.py; aqui so o "quando".

QUANDO APARECE: o main.py chama abrir_o_brasao() logo no comeco do main(),
antes dos imports pesados. Este arquivo NAO importa o Qt (nem nada pesado):
ele so abre um processo a parte (o mesmo programa com --brasao-girando
<numero deste processo>), que mostra a janela. Assim o brasao aparece cedo e
gira liso enquanto este processo carrega e monta a janela principal (que
ocupa a linha do Qt deste processo e nao deixaria nada girar aqui).

QUANDO SOME: quando a janela principal aparece, o main.py chama fechar()
(pelo laco do Qt, logo depois de janela.show()). Se o programa morrer antes,
o processo do brasao percebe sozinho e fecha (ui/brasao_girando.rodar_sozinho).

QUANDO NAO APARECE (nao_mostrar):
- nos testes (pytest, ou o Qt desenhando fora da tela, "offscreen"): nada
  pode aparecer na tela do Samuel nos testes (tests/conftest.py);
- na conta dos testes a distancia (D-736: aberto por um teste a distancia,
  o programa so faz o necessario; a mesma regra da atualizacao,
  atualizacao.e_a_conta_de_testes);
- se as imagens do brasao nao estiverem no programa.
Os modos sem janela do main.py (servidor de paginas, ajudante da
atualizacao, conferir os detectores) saem antes do main() e nunca chegam aqui.

Arriscado mudar: abrir o processo sem CREATE_NO_WINDOW (pelo codigo, com o
python.exe, abriria uma janela preta); tirar a regra dos testes (o brasao
apareceria na tela do Samuel em toda rodada); fechar so no fim do main() (o
brasao ficaria por cima da janela principal).
"""

from __future__ import annotations

import atexit
import os
import subprocess
import sys
from pathlib import Path

import brasao

ARGUMENTO = "--brasao-girando"
RAIZ = Path(__file__).resolve().parent.parent


def nao_mostrar(ambiente: dict | None = None, conta_de_testes=None) -> str | None:
    """Por que o brasao nao deve aparecer agora, ou None se deve aparecer."""
    ambiente = os.environ if ambiente is None else ambiente
    if "PYTEST_CURRENT_TEST" in ambiente:
        return "teste"
    if ambiente.get("QT_QPA_PLATFORM", "").lower() in ("offscreen", "minimal"):
        return "fora da tela"
    if conta_de_testes is None:
        from atualizacao import e_a_conta_de_testes as conta_de_testes
    if conta_de_testes():
        return "conta dos testes a distancia"
    if not brasao.arquivo_do_giro(1.0).exists():
        return "sem as imagens do brasao"
    return None


def comando() -> list[str]:
    """O comando que abre o processo do brasao girando.

    Empacotado: o proprio .exe com --brasao-girando. Pelo codigo: o mesmo
    Python com o main.py (o main.py atende esse argumento antes de tudo).
    """
    pid = str(os.getpid())
    if getattr(sys, "frozen", False):
        return [sys.executable, ARGUMENTO, pid]
    return [sys.executable, str(RAIZ / "main.py"), ARGUMENTO, pid]


class BrasaoAberto:
    """O brasao girando que o programa abriu (ou nada, se nao abriu).

    fechar() pode ser chamado quantas vezes for; sem processo nao faz nada.
    """

    def __init__(self, processo: subprocess.Popen | None = None, motivo: str | None = None) -> None:
        self.processo = processo
        self.motivo = motivo     # por que nao abriu (None se abriu)
        if processo is not None:
            atexit.register(self.fechar)

    @property
    def aberto(self) -> bool:
        return self.processo is not None and self.processo.poll() is None

    def fechar(self) -> None:
        """Some com o brasao (o processo dele nao guarda nada: pode fechar ja)."""
        processo, self.processo = self.processo, None
        if processo is None or processo.poll() is not None:
            return
        try:
            processo.terminate()
        except OSError:
            pass


def abrir_o_brasao(ambiente: dict | None = None, conta_de_testes=None, abrir=subprocess.Popen) -> BrasaoAberto:
    """Abre o brasao girando num processo a parte, se for o caso (ver nao_mostrar).

    Nunca levanta erro: se nao der para abrir, o programa abre sem o brasao.
    `ambiente`, `conta_de_testes` e `abrir` so mudam nos testes.
    """
    try:
        motivo = nao_mostrar(ambiente, conta_de_testes)
        if motivo is not None:
            return BrasaoAberto(None, motivo)
        processo = abrir(comando(), cwd=str(RAIZ), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return BrasaoAberto(processo)
    except Exception as erro:  # noqa: BLE001 - o brasao nunca impede o programa de abrir
        try:
            from registro import registrar_erro

            registrar_erro("brasão girando", repr(erro))
        except Exception:  # noqa: BLE001
            pass
        return BrasaoAberto(None, "erro ao abrir")
