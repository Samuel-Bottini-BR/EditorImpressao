"""A versao do Editor de Impressao: o UNICO lugar onde o numero esta escrito.

Etapa 3 da frente do notebook do Kaique (16/11/2026; decisoes D-714, D-723).
Antes, o programa nao sabia a propria versao: so havia "1.0.0" escrito a mao
no instalador.iss. Agora todo mundo le daqui:

- empacotar.py: passa ao Inno Setup (ISCC /DMinhaVersao=...) e ao Velopack
  (vpk pack --packVersion ...);
- publicar_versao_kaique.py: o numero da "versao para o Kaique" que vai ao
  GitHub (etiqueta v<VERSAO>) e a assinatura;
- atualizacao.py: na falta do Velopack (programa rodando pelo codigo), e a
  versao que o programa diz ter.

Nao ha tela "Sobre" no programa; esta etapa nao cria nenhuma.

Como mudar: para publicar uma versao nova para o Kaique, AUMENTE este numero
(1.1.0 -> 1.1.1, ou 1.2.0) e rode publicar_versao_kaique.py. O comando recusa
publicar um numero que ja foi publicado.

Arriscado mudar: o formato. Tem de ser tres numeros separados por ponto
(SemVer, exigido pelo Velopack). Diminuir o numero faz o programa do Kaique
achar que a versao publicada e mais velha e nao trocar. A 1.0.0 foi a do
instalador do Inno de 28/10/2026 (a que o Kaique tem): a primeira do Velopack
e a 1.1.0.
"""

from __future__ import annotations

VERSAO = "1.1.0"

# O nome do pacote para o Velopack (a pasta em Arquivos de Programas, os
# arquivos EditorImpressao-<versao>-full.nupkg). Trocar depois de instalado no
# Kaique faz o Velopack achar que e OUTRO programa: nunca trocar.
ID_DO_PACOTE = "EditorImpressao"


def numeros(versao: str) -> tuple[int, int, int]:
    """'1.2.3' -> (1, 2, 3), para comparar versoes. Levanta ValueError se o
    texto nao for tres numeros separados por ponto."""
    partes = versao.strip().split(".")
    if len(partes) != 3 or not all(p.isdigit() for p in partes):
        raise ValueError(f"versão fora do formato 1.2.3: {versao!r}")
    return int(partes[0]), int(partes[1]), int(partes[2])
