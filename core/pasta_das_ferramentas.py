"""Onde fica a pasta das ferramentas do Samuel: o LUGAR ÚNICO dessa regra (passo 2 do plano da parte do Windows, voltas 9 e 10).

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
    cópia de trabalho sabe de que repositório saiu), sem janela de console e com o limite de tempo DA PEÇA (o único
    lugar desse número). Quando o git não responde (não instalado, recusando a pasta por ser de outro dono, o git que
    demora ou dá erro, ou um repositório sem pasta principal):
    - se o código roda de uma pasta cujo `.git` é uma PASTA (a pasta principal) ou que não tem `.git` (uma cópia sem
      repositório, feita com `git archive`), a pasta do próprio código faz o papel da principal: a conta de antes, que é
      a certa na pasta principal;
    - se o `.git` é um ARQUIVO (uma cópia de trabalho de `.claude\\worktrees`: o repositório mora em outro lugar; quem
      olha é a peça do git, `e_copia_de_trabalho`), a pasta de cima do código é a conta errada do defeito 1. Então NÃO
      HÁ RESPOSTA: `SemPastaPrincipal`, com a frase do porquê e do que fazer (passo 2, volta 10, achado 1 do relatório 8
      de quem tentou quebrar: aqui a regra voltava calada à pasta errada de 19/11 e usava o Visual C++ de lá).
    O programa EMPACOTADO (o do Kaique) não tem pasta das ferramentas e nunca pergunta ao git: `pasta_das_ferramentas`
    devolve None antes de qualquer pergunta, e a peça do git nem vai no pacote (`empacotar.EXCLUIR`).

QUEM RECEBE O "NÃO SEI"
    Os scripts de linha de comando que guardam a pasta ao carregar (empacotar, montar_motor_kraken,
    compilar_detector_gravura, e por ele o compilar_st_ferramentas; e quem importa o empacotar: o publicar, o servidor
    das versões) usam `pasta_das_ferramentas_ou_parar`, que para o script com a frase (SystemExit: a frase e o código 1,
    sem o rastro técnico). O programa (o Kraken, rodando pelas fontes) recebe a `SemPastaPrincipal`, que é um erro
    comum: a janela nunca recebe um SystemExit. "Pode gravar?" (`problema_para_gravar`) devolve a mesma frase.

QUEM GRAVA
    Nunca se cria a pasta das ferramentas: quem grava nela (a montagem do Visual C++, o montar_motor_kraken, os
    compiladores) chama antes `problema_para_gravar`, que diz por que não dá quando ela não existe. Assim nenhum caso
    (sem git, cópia sem repositório, pasta principal sem a pasta do Samuel ao lado) cria pasta no lugar errado.

Seguro mexer: as frases. Arriscado: calcular a pasta das ferramentas em outro arquivo (volta o defeito), perguntar ao
git com o programa empacotado, criar a pasta das ferramentas quando ela falta, voltar à pasta de cima do código numa
cópia de trabalho (volta o achado 1), ou levantar SystemExit fora de `pasta_das_ferramentas_ou_parar` (fecharia a janela
do programa).
"""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

NOME_DA_PASTA_DO_SAMUEL = "EditorImpressao-arquivos"
NOME_DAS_FERRAMENTAS = "ferramentas"
# O tempo máximo da pergunta ao git mora na peça do git (`conversa_com_o_git.pasta_principal`, o padrão `limite_s`):
# volta 10, observação 8 do relatório 8 (antes ele estava escrito aqui também).

# A pasta do código (a raiz do repositório onde este arquivo está: core/ fica dentro dela).
RAIZ_DO_CODIGO = Path(__file__).resolve().parent.parent


class SemPastaPrincipal(RuntimeError):
    """A regra não sabe onde fica a pasta das ferramentas: o código roda de uma cópia de trabalho e o git não disse de
    que pasta principal ela saiu. A mensagem é a frase para quem usa (o porquê, com o que o git disse, e o que fazer).
    É um erro comum (não um SystemExit) para a janela do programa nunca fechar por ela."""


def empacotado() -> bool:
    """O programa roda empacotado pelo PyInstaller (o do Kaique)? O lugar único dessa pergunta para a pasta das
    ferramentas e para os lugares do motor (`core/ocr_kraken.lugares_do_motor`; volta 10, observação 8)."""
    return bool(getattr(sys, "frozen", False))


def _frase_sem_pasta_principal(codigo: Path, o_que_o_git_disse: str) -> str:
    """A frase de `SemPastaPrincipal` (um lugar só): o que houve, o que o git disse e o que fazer."""
    return (f"não sei onde fica a pasta das ferramentas ({NOME_DA_PASTA_DO_SAMUEL}\\{NOME_DAS_FERRAMENTAS}, ao lado da "
            f"pasta principal do repositório): o código roda de uma cópia de trabalho ({codigo}), e o git não disse "
            f"de que pasta principal ela saiu ({o_que_o_git_disse}). Nada foi procurado nem criado. Conserte o git (o "
            f'comando git -C "{codigo}" rev-parse --git-common-dir tem de responder) ou rode da pasta principal do '
            "repositório")


def pasta_principal(codigo: Path | str = RAIZ_DO_CODIGO) -> Path:
    """A pasta principal do repositório onde está `codigo` (a raiz do código; o git diz; ver o topo).

    Sem resposta do git: na pasta principal ou numa cópia sem repositório, o próprio `codigo` (a conta de antes); numa
    cópia de trabalho (o `.git` é um arquivo), levanta `SemPastaPrincipal` (volta 10, achado 1 do relatório 8: aqui
    voltava calada a `codigo`, que numa cópia é a conta errada do defeito 1). Não usar com o programa empacotado (quem
    chama confere antes). Arriscado: devolver `codigo` numa cópia de trabalho; decidir aqui, e não na peça do git, se a
    pasta é uma cópia."""
    codigo = Path(codigo)
    try:
        from regras_dos_agentes import conversa_com_o_git as git
    except ImportError:                  # o código sem a peça do git (não acontece pelas fontes): a conta de antes
        return codigo
    try:
        principal = git.pasta_principal(codigo)          # o limite de tempo é o da peça
        o_que_o_git_disse = "o repositório dela não tem uma pasta principal com os arquivos"
    except git.GitFalhou as erro:        # sem git, recusando o dono, fora de um repositório, o git que demora ou erra
        principal, o_que_o_git_disse = None, str(erro)
    if principal is not None:
        return principal
    if git.e_copia_de_trabalho(codigo):
        raise SemPastaPrincipal(_frase_sem_pasta_principal(codigo, o_que_o_git_disse))
    return codigo


@lru_cache(maxsize=None)
def _pasta_das_ferramentas_de(codigo: Path) -> Path:
    """A conta, guardada por processo (o git é perguntado uma vez para cada pasta de código). A `SemPastaPrincipal` não
    fica guardada (o lru_cache guarda só o que a função devolve): a próxima pergunta pergunta de novo ao git."""
    return pasta_principal(codigo).parent / NOME_DA_PASTA_DO_SAMUEL / NOME_DAS_FERRAMENTAS


def pasta_das_ferramentas(codigo: Path | str | None = None) -> Path | None:
    """A pasta das ferramentas do Samuel para o código em `codigo` (a raiz do código; de fábrica, este código). None
    quando o programa roda empacotado (sem perguntar nada). Levanta `SemPastaPrincipal` quando não sabe (ver o topo). A
    pasta pode não existir: quem grava chama `problema_para_gravar` antes."""
    if empacotado():
        return None
    return _pasta_das_ferramentas_de(Path(codigo or RAIZ_DO_CODIGO).resolve())


def pasta_das_ferramentas_ou_parar(codigo: Path | str | None = None) -> Path | None:
    """`pasta_das_ferramentas`, para os scripts de linha de comando que a guardam ao carregar (empacotar,
    montar_motor_kraken, compilar_detector_gravura): quando a regra não sabe, PARA o script com a frase (SystemExit: a
    frase e o código 1, sem o rastro técnico; lido em https://docs.python.org/3/library/exceptions.html#SystemExit).
    Só para scripts: a janela do programa usa `pasta_das_ferramentas` (volta 10, achado 1 do relatório 8)."""
    try:
        return pasta_das_ferramentas(codigo)
    except SemPastaPrincipal as erro:
        raise SystemExit(f"Parei: {erro}.") from None


def problema_para_gravar(codigo: Path | str | None = None) -> str | None:
    """Por que não dá para gravar na pasta das ferramentas, ou None se dá. Nunca cria nada: a pasta das ferramentas tem
    de existir (ela mesma, não só a `EditorImpressao-arquivos` de cima: mutação B5 do relatório 8); uma subpasta que
    falta (ex.: downloads), quem grava pode criar dentro dela. Quando a regra não sabe a pasta (`SemPastaPrincipal`),
    devolve a frase dela. Quem grava num lugar escolhido à mão na linha de comando não precisa perguntar."""
    try:
        ferramentas = pasta_das_ferramentas(codigo)
    except SemPastaPrincipal as erro:    # volta 10: a mesma frase de quando a regra não sabe a pasta
        return str(erro)
    if ferramentas is None:
        return "o programa empacotado não tem a pasta das ferramentas"
    if not ferramentas.is_dir():
        return (f"não existe a pasta das ferramentas {ferramentas} (ao lado da pasta principal "
                f"{ferramentas.parent.parent}); nada foi criado. Rode da pasta principal do repositório ou de uma "
                "cópia de trabalho dela")
    return None
