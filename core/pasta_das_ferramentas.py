"""Onde fica a pasta das ferramentas do Samuel: o LUGAR ÚNICO dessa regra (passo 2 do plano da parte do Windows).

O QUE É
    As ferramentas grandes que não vão para o git (o motor do Kraken montado, o Visual C++ baixado, o Qt e o Boost do
    ScanTailor, os rascunhos das compilações) moram numa pasta do PC do Samuel: `PASTA_DAS_FERRAMENTAS`,
    `D:\\programas\\EditorImpressao-arquivos\\ferramentas`, escrita AQUI e em nenhum outro lugar. Vale igual rodando da
    pasta principal do repositório ou de uma cópia de trabalho (`.claude\\worktrees\\<nome>`).

POR QUE É ASSIM (D-820, Samuel, 21/11/2026: "não era melhor só ver se está instaldo no pc?" · "A")
    Até a volta 8, cinco lugares calculavam essa pasta cada um por conta própria, como "a pasta de cima do código", que
    numa cópia de trabalho é `.claude\\worktrees` (o defeito 1 da prova à vista de 20/11: o motor não foi achado, e uma
    montagem de 19/11 criou uma pasta no lugar errado). As voltas 9 e 10 perguntavam ao git onde estava a pasta
    principal; quando o git não respondia, a conta voltava calada à pasta errada (relatório 8 de quem tentou quebrar). O
    jeito mais simples (D-819) é o melhor aqui: a pasta é uma só, conhecida, no PC do Samuel; escrever o caminho não
    depende do git, nem de onde o código está, nem do nome das pastas. Quem roda em outro PC (o Windows do GitHub) não
    tem essa pasta: quem procura uma peça diz onde procurou e como apontar outro lugar (as opções que já existem, como
    `--motor-kraken`, `--destino`, `--ferramentas`), e quem grava para (`problema_para_gravar`).

QUEM USA (os seis lugares; nenhum tem conta própria)
    `empacotar` (FERRAMENTAS, e dela DOWNLOADS e LUGARES_DO_MOTOR), `core/ocr_kraken.lugares_do_motor`,
    `montar_motor_kraken` (PASTA_FERRAMENTAS), `compilar_detector_gravura` (PASTA_FERRAMENTAS_PADRAO) e, por ele,
    `compilar_st_ferramentas.pasta_de_ferramentas_padrao`.

O PROGRAMA DO KAIQUE (empacotado) não tem pasta das ferramentas: `pasta_das_ferramentas` devolve None, e o motor é
procurado ao lado do programa, como sempre (D-605, D-788).

QUEM GRAVA
    Nunca se cria a pasta das ferramentas: quem grava nela (a montagem do Visual C++, o montar_motor_kraken, os
    compiladores) chama antes `problema_para_gravar`, que diz por que não dá quando ela não existe.

Seguro mexer: as frases; o caminho, se a pasta do Samuel mudar de lugar (só aqui). Arriscado: calcular a pasta em outro
arquivo, ou a partir de onde o código está (volta o defeito 1); criar a pasta quando ela falta; olhar esta pasta no
programa empacotado. Nos testes, o caminho é trocado aqui, num lugar só (o atributo `PASTA_DAS_FERRAMENTAS`, ou esta
linha na cópia do código que o teste monta).
"""

from __future__ import annotations

import sys
from pathlib import Path

# A pasta das ferramentas do Samuel (D-820). O único lugar deste caminho no programa.
PASTA_DAS_FERRAMENTAS = Path(r"D:\programas\EditorImpressao-arquivos\ferramentas")
NOME_DA_PASTA_DO_SAMUEL = "EditorImpressao-arquivos"     # o nome da pasta de cima (as frases e os testes o usam)


def empacotado() -> bool:
    """O programa roda empacotado pelo PyInstaller (o do Kaique)? O lugar único dessa pergunta para a pasta das
    ferramentas e para os lugares do motor (`core/ocr_kraken.lugares_do_motor`; observação 8 do relatório 8)."""
    return bool(getattr(sys, "frozen", False))


def pasta_das_ferramentas() -> Path | None:
    """A pasta das ferramentas do Samuel (`PASTA_DAS_FERRAMENTAS`), ou None quando o programa roda empacotado. A pasta
    pode não existir (outro PC): quem grava chama `problema_para_gravar` antes; quem procura uma peça diz onde
    procurou."""
    if empacotado():
        return None
    return PASTA_DAS_FERRAMENTAS


def problema_para_gravar() -> str | None:
    """Por que não dá para gravar na pasta das ferramentas, ou None se dá. Nunca cria nada: a pasta das ferramentas tem
    de existir (ela mesma, não só a `EditorImpressao-arquivos` de cima: mutação B5 do relatório 8); uma subpasta que
    falta (ex.: downloads), quem grava pode criar dentro dela. Quem grava num lugar escolhido à mão na linha de comando
    não precisa perguntar (e quem chama acrescenta a opção que aponta outro lugar)."""
    ferramentas = pasta_das_ferramentas()
    if ferramentas is None:
        return "o programa empacotado não tem a pasta das ferramentas"
    if not ferramentas.is_dir():
        return (f"não existe a pasta das ferramentas {ferramentas} (o lugar escrito em core/pasta_das_ferramentas.py); "
                "nada foi criado. Rode no PC onde ela existe")
    return None
