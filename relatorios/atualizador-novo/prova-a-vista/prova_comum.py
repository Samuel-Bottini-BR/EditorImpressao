"""Os lugares e as contas comuns dos scripts da prova à vista do atualizador novo (25/11/2026). NÃO é parte do programa.

Um lugar só para cada caminho que os scripts da prova usam (CLAUDE.md §11.12): `montar_as_versoes.py`,
`fonte_da_prova.py`, `vigiar_janelas.py` e `por_de_lado.py` leem daqui. O roteiro (`roteiro.md`) cita os mesmos.

    BASE      C:\\EditorImpressaoProva\\prova-a-vista-25-11   (no C:, como o publicar, D-776; criada por esta preparação)
    ESTOQUE   <BASE>\\estoque     o destino do publicar (`--pasta`): TODAS as versões montadas, uma subpasta cada
    SERVIDA   <BASE>\\servida     as versões "publicadas agora" na prova (a gerente passa uma do estoque para cá)
    FONTE     <BASE>\\fonte       o que o programa instalado lê (a linha do fonte-de-teste.txt): uma pasta só, com o
                                  índice juntado e os arquivos das versões servidas (ligações do disco, sem cópia)
    DE_LADO   <BASE>\\de-lado     onde o atualizador (Update.exe) e o motor ficam quando são "postos de lado"

SÓ O ENSAIO (ensaio_dos_scripts.py) troca dois lugares pelas variáveis PROVA_ENSAIO_BASE e PROVA_ENSAIO_PROGRAMA,
para rodar os scripts numa pasta de ensaio antes da prova. Na prova elas não existem.

Seguro mexer: os textos. Arriscado: mudar BASE depois de o fonte-de-teste.txt ser criado (o programa leria outra
pasta); pôr BASE fora do C: (a troca copiaria do HD externo, mais lenta, e o publicar monta no C:).
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

RAMO = Path(__file__).resolve().parents[3]                        # a cópia do ramo atualizador-novo
MONTAGEM = RAMO.parent / "prova-a-vista-montagem"                   # a cópia de trabalho só para montar
COMMIT = "8e09e193e0607a65e21c3224e0172a3b5cbfbfcd"
BASE = Path(os.environ.get("PROVA_ENSAIO_BASE") or r"C:\EditorImpressaoProva\prova-a-vista-25-11")
ESTOQUE = BASE / "estoque"
SERVIDA = BASE / "servida"
FONTE = BASE / "fonte"
DE_LADO = BASE / "de-lado"
REGISTROS = BASE / "registros"
ASSINATURA_VERDADEIRA = BASE / "assinatura-verdadeira-1.9.5"

# A instalação de verdade (só existe depois do .msi, na prova).
PROGRAMA = Path(os.environ.get("PROVA_ENSAIO_PROGRAMA") or r"C:\Program Files\EditorImpressaoPrograma")
REGISTRO_DA_ATUALIZACAO = Path(r"C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log")
FONTE_DE_TESTE = Path(r"C:\ProgramData\EditorImpressao\fonte-de-teste.txt")

RESERVA_DO_C = 20 * 1024 ** 3          # D-776: nunca menos de 20 GB livres no C:
GB = 1024 ** 3


def conferir_espaco_do_c(precisa: int = 2 * GB) -> None:
    """Para (SystemExit) se, gastando `precisa`, o C: ficaria com menos de 20 GB livres (D-776)."""
    livre = shutil.disk_usage("C:\\").free
    if livre - precisa < RESERVA_DO_C:
        raise SystemExit(f"PAREI: o C: tem {livre / GB:.1f} GB livres; com mais {precisa / GB:.1f} GB ficaria abaixo "
                         "dos 20 GB (D-776)")
