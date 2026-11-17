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

# O nome INTERNO do pacote para o Velopack (o --packId do vpk). Aparece so em
# lugares tecnicos: os arquivos <ID>-<versao>-full.nupkg e <ID>-<versao>.assinatura
# publicados, a chave do desinstalador no registro do Windows (MSI:<ID>) e a
# pasta de reserva do Velopack, %LOCALAPPDATA%\<ID>. O Kaique NAO ve este nome:
# a pasta em Arquivos de Programas, o nome na lista de programas e os atalhos
# vem do titulo do pacote (empacotar.TITULO_DO_PACOTE, "Editor de Impressão").
#
# A REGRA (D-763, Samuel 17/11/2026: "ok, pode fazer"): este nome NUNCA e o da
# pasta dos dados do programa (historico.pasta_de_dados, %LOCALAPPDATA%\EditorImpressao,
# onde moram os projetos). O Velopack usa %LOCALAPPDATA%\<ID> como pasta de
# reserva (grava Update.exe e packages\ a cada abertura na conta do Kaique) e
# o desinstalador do .msi limpa essa pasta. Ate 17/11 o nome era
# "EditorImpressao", igual ao da pasta dos projetos, por acaso: a prova de
# 17/11 (relatorios/velopack-pasta-2026-11-17/) mostrou o desinstalador
# apagando a pasta inteira com um projeto de mentira dentro. A prova
# tests/test_nome_do_pacote.py cobra a regra.
#
# Por que PODE trocar agora e NUNCA MAIS depois: o Velopack reconhece o
# programa instalado por este nome (e o .msi se registra no Windows com ele).
# Em 17/11/2026 nenhum pacote do Velopack foi instalado de verdade (nem no notebook do Kaique, nem no PC do Samuel; a de 28/10 do Kaique e do
# Inno, que tem outro nome, atualizacao.APPID_DO_INNO). Depois da primeira
# instalacao de verdade, trocar faz o Velopack achar que e OUTRO programa: a
# atualizacao nao acha a instalada e ficam dois programas no computador.
ID_DO_PACOTE = "EditorImpressaoPrograma"


def numeros(versao: str) -> tuple[int, int, int]:
    """'1.2.3' -> (1, 2, 3), para comparar versoes. Levanta ValueError se o
    texto nao for tres numeros separados por ponto."""
    partes = versao.strip().split(".")
    if len(partes) != 3 or not all(p.isdigit() for p in partes):
        raise ValueError(f"versão fora do formato 1.2.3: {versao!r}")
    return int(partes[0]), int(partes[1]), int(partes[2])
