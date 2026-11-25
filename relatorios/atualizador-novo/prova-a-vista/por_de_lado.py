"""Os "estragos" de propósito da prova à vista do atualizador novo, e o desfazer de cada um. NÃO é parte do programa.
Nada aqui pede licença ao Windows (a pasta do programa aceita gravação de Usuários depois do "Sim" do passo 1), nada
abre janela, nada fecha processo.

COMANDOS (python por_de_lado.py <comando>)
    atualizador-de-lado   o atualizador do Velopack (<programa>\\Update.exe) vai para <BASE>\\de-lado\\ (como um
                          antivírus que o põe de lado). Recusa se ele estiver rodando.
    atualizador-de-volta  ele volta para o lugar
    motor-de-lado         o motor do Kraken (<programa>\\motor-kraken\\1) vai para <BASE>\\de-lado\\. Recusa com o programa
                          aberto (algum processo rodando da pasta do programa)
    motor-de-volta        ele volta
    segurar-a-pasta [N]   ESTE processo entra na pasta <programa>\\current e fica nela (a pasta de trabalho dele), até
                          existir o arquivo <BASE>\\de-lado\\soltar ou passarem N segundos (padrão 900). Enquanto isso o
                          Windows não deixa o Velopack trocar o nome de `current` (erro 32, o mesmo da prova de 22/11):
                          é "o Windows recusando a troca". Rodar por trás; para soltar, `soltar`.
    soltar                cria o arquivo que faz o `segurar-a-pasta` sair (ele sai sozinho; ninguém é fechado à força)
    estado                onde estão o atualizador, o motor, e se alguém segura a pasta

Cada comando confere de novo, no disco, o que fez (§11.12 ponto 2). As conversas com o Windows (quem está rodando da
pasta) passam pela peça do programa (`core.windows.programas_rodando_de`, `atualizador_do_velopack_rodando`).

Seguro mexer: os textos e o tempo padrão. Arriscado: apagar em vez de mover (não haveria desfazer); mover para outro
disco (deixa de ser uma troca de nome instantânea).
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import prova_comum as comum  # noqa: E402

sys.path.insert(0, str(comum.RAMO))
from core import windows  # noqa: E402

ATUALIZADOR = "Update.exe"
MOTOR = Path("motor-kraken") / "1"
SOLTAR = comum.DE_LADO / "soltar"
SEGURANDO = comum.DE_LADO / "segurando.txt"


def _mover(origem: Path, alvo: Path) -> None:
    """Troca de nome (o mesmo disco); confere depois."""
    if not origem.exists():
        raise SystemExit(f"PAREI: {origem} não existe")
    if alvo.exists():
        raise SystemExit(f"PAREI: {alvo} já existe")
    alvo.parent.mkdir(parents=True, exist_ok=True)
    os.rename(origem, alvo)
    if origem.exists() or not alvo.exists():
        raise SystemExit(f"PAREI: a troca de {origem} para {alvo} não ficou no disco")


def _programa_aberto() -> list[tuple[int, str]] | None:
    """Os processos que rodam da pasta do programa (pela peça; None = o Windows não deu a lista)."""
    return windows.programas_rodando_de(comum.PROGRAMA)


def estado() -> None:
    """Onde está cada coisa, lido agora."""
    print(f"atualizador: {'no lugar' if (comum.PROGRAMA / ATUALIZADOR).is_file() else 'FORA do lugar'}"
          f"{' (está de lado)' if (comum.DE_LADO / ATUALIZADOR).is_file() else ''}")
    print(f"motor: {'no lugar' if (comum.PROGRAMA / MOTOR).is_dir() else 'FORA do lugar'}"
          f"{' (está de lado)' if (comum.DE_LADO / 'motor-kraken-1').is_dir() else ''}")
    print(f"pasta current: {'SEGURADA (' + SEGURANDO.read_text(encoding='utf-8') + ')' if SEGURANDO.exists() else 'solta'}")
    rodando = _programa_aberto()
    print("rodando da pasta do programa: " + ("o Windows não deu a lista" if rodando is None else
                                             ", ".join(f"{n} {c}" for n, c in rodando) or "nada"))


def segurar(segundos: float) -> int:
    """Fica com a pasta de trabalho em <programa>\\current até `soltar` ou até o tempo acabar."""
    pasta = comum.PROGRAMA / "current"
    if not pasta.is_dir():
        raise SystemExit(f"PAREI: {pasta} não existe")
    SOLTAR.unlink(missing_ok=True)
    comum.DE_LADO.mkdir(parents=True, exist_ok=True)
    os.chdir(pasta)
    SEGURANDO.write_text(f"processo {os.getpid()}, desde {time.strftime('%H:%M:%S')}", encoding="utf-8")
    print(f"segurando {pasta} desde {time.strftime('%H:%M:%S')} (processo {os.getpid()})", flush=True)
    fim = time.time() + segundos
    try:
        while time.time() < fim and not SOLTAR.exists():
            time.sleep(0.5)
    finally:
        os.chdir(comum.BASE)
        SEGURANDO.unlink(missing_ok=True)
        SOLTAR.unlink(missing_ok=True)
    print(f"soltei a pasta às {time.strftime('%H:%M:%S')}", flush=True)
    return 0


def main(argumentos: list[str]) -> int:
    """A linha de comando (ver o topo)."""
    comando = argumentos[0] if argumentos else ""
    if comando == "atualizador-de-lado":
        if windows.atualizador_do_velopack_rodando(comum.PROGRAMA) is not False:
            raise SystemExit("PAREI: o atualizador está rodando (ou o Windows não deixou saber): espere a troca acabar")
        _mover(comum.PROGRAMA / ATUALIZADOR, comum.DE_LADO / ATUALIZADOR)
    elif comando == "atualizador-de-volta":
        _mover(comum.DE_LADO / ATUALIZADOR, comum.PROGRAMA / ATUALIZADOR)
    elif comando == "motor-de-lado":
        rodando = _programa_aberto()
        if rodando is None or rodando:
            raise SystemExit("PAREI: feche o programa antes (ou o Windows não deu a lista de processos)")
        _mover(comum.PROGRAMA / MOTOR, comum.DE_LADO / "motor-kraken-1")
    elif comando == "motor-de-volta":
        _mover(comum.DE_LADO / "motor-kraken-1", comum.PROGRAMA / MOTOR)
    elif comando == "segurar-a-pasta":
        return segurar(float(argumentos[1]) if len(argumentos) > 1 else 900)
    elif comando == "soltar":
        comum.DE_LADO.mkdir(parents=True, exist_ok=True)
        SOLTAR.write_text("soltar", encoding="utf-8")
        for _ in range(20):
            if not SEGURANDO.exists():
                break
            time.sleep(0.5)
    elif comando != "estado":
        print(__doc__)
        return 1
    estado()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
