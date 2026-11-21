"""Onde fica a pasta das ferramentas do Samuel: o LUGAR ÚNICO dessa regra (passo 2 do plano da parte do Windows, volta 9).

O QUE É
    As ferramentas grandes que não vão para o git (o motor do Kraken montado, o Visual C++ baixado, o Qt e o Boost do
    ScanTailor, os rascunhos das compilações) moram em `EditorImpressao-arquivos\\ferramentas`, AO LADO DA PASTA
    PRINCIPAL do repositório (no PC do Samuel: `D:\\programas\\EditorImpressao-arquivos\\ferramentas`, ao lado de
    `D:\\programas\\EditorImpressao`).

POR QUE EXISTE (o defeito 1 da prova à vista de 20/11/2026, prova 6b)
    Cinco lugares calculavam essa pasta cada um por conta própria, como "a pasta de cima de onde está este arquivo de
    código" (e um sexto subia as pastas e ficava com a primeira que existisse). Isso só acerta na pasta principal: numa
    cópia de trabalho (`.claude\\worktrees\\<nome>`), a pasta de cima é `.claude\\worktrees`. O publicar rodado da cópia
    não achou o motor, e uma montagem baixou o Visual C++ para uma pasta criada no lugar errado (19/11). Agora todos
    perguntam aqui: `empacotar` (DOWNLOADS, LUGARES_DO_MOTOR), `core/ocr_kraken.lugares_do_motor`,
    `montar_motor_kraken`, `compilar_detector_gravura` e `compilar_st_ferramentas`.

COMO ACHA
    A pasta principal vem do git, pela peça única dele (`regras_dos_agentes.conversa_com_o_git.pasta_principal`: a
    cópia de trabalho sabe de que repositório saiu), sem janela de console e com limite de tempo. Quando o git não
    responde (não instalado, uma cópia sem repositório feita com `git archive`, o git que demora ou dá erro), a pasta do
    próprio código faz o papel da principal: a conta de antes, que é a certa quando o código roda da pasta principal.
    O programa EMPACOTADO (o do Kaique) não tem pasta das ferramentas e nunca pergunta ao git: `pasta_das_ferramentas`
    devolve None antes de qualquer pergunta, e a peça do git nem vai no pacote (`empacotar.EXCLUIR`).

QUEM GRAVA
    Nunca se cria a pasta das ferramentas: quem grava nela (a montagem do Visual C++, o montar_motor_kraken, os
    compiladores) chama antes `problema_para_gravar`, que diz por que não dá quando ela não existe. Assim nenhum caso
    (sem git, cópia sem repositório, pasta principal sem a pasta do Samuel ao lado) cria pasta no lugar errado.

Seguro mexer: as frases. Arriscado: calcular a pasta das ferramentas em outro arquivo (volta o defeito), perguntar ao
git com o programa empacotado, ou criar a pasta das ferramentas quando ela falta.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

NOME_DA_PASTA_DO_SAMUEL = "EditorImpressao-arquivos"
NOME_DAS_FERRAMENTAS = "ferramentas"
# O tempo máximo da pergunta ao git (ela responde em menos de um segundo; passou disso, algo está errado).
LIMITE_DO_GIT_S = 30

# A pasta do código (a raiz do repositório onde este arquivo está: core/ fica dentro dela).
RAIZ_DO_CODIGO = Path(__file__).resolve().parent.parent


def empacotado() -> bool:
    """O programa roda empacotado pelo PyInstaller (o do Kaique)?"""
    return bool(getattr(sys, "frozen", False))


def pasta_principal(codigo: Path | str = RAIZ_DO_CODIGO) -> Path:
    """A pasta principal do repositório onde está `codigo` (o git diz; ver o topo). Sem resposta do git: o próprio
    `codigo` (a conta de antes). Nunca levanta. Não usar com o programa empacotado (quem chama confere antes)."""
    codigo = Path(codigo)
    try:
        from regras_dos_agentes import conversa_com_o_git as git
    except ImportError:                  # o código sem a peça do git (não acontece pelas fontes): a conta de antes
        return codigo
    try:
        principal = git.pasta_principal(codigo, limite_s=LIMITE_DO_GIT_S)
    except git.GitFalhou:                # sem git, fora de um repositório, o git que demora ou dá erro
        return codigo
    return principal if principal is not None else codigo


@lru_cache(maxsize=None)
def _pasta_das_ferramentas_de(codigo: Path) -> Path:
    """A conta, guardada por processo (o git é perguntado uma vez para cada pasta de código)."""
    return pasta_principal(codigo).parent / NOME_DA_PASTA_DO_SAMUEL / NOME_DAS_FERRAMENTAS


def pasta_das_ferramentas(codigo: Path | str | None = None) -> Path | None:
    """A pasta das ferramentas do Samuel para o código em `codigo` (de fábrica, este código). None quando o programa
    roda empacotado (sem perguntar nada). A pasta pode não existir: quem grava chama `problema_para_gravar` antes."""
    if empacotado():
        return None
    return _pasta_das_ferramentas_de(Path(codigo or RAIZ_DO_CODIGO).resolve())


def problema_para_gravar(codigo: Path | str | None = None) -> str | None:
    """Por que não dá para gravar na pasta das ferramentas, ou None se dá. Nunca cria nada: a pasta das ferramentas tem
    de existir; uma subpasta que falta (ex.: downloads), quem grava pode criar dentro dela. Quem grava num lugar
    escolhido à mão na linha de comando não precisa perguntar."""
    ferramentas = pasta_das_ferramentas(codigo)
    if ferramentas is None:
        return "o programa empacotado não tem a pasta das ferramentas"
    if not ferramentas.is_dir():
        return (f"não existe a pasta das ferramentas {ferramentas} (ao lado da pasta principal "
                f"{ferramentas.parent.parent}); nada foi criado. Rode da pasta principal do repositório ou de uma "
                "cópia de trabalho dela")
    return None
