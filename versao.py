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
# A REGRA (D-763, Samuel 17/11/2026: "ok, pode fazer"): nem este nome nem o
# titulo do pacote sao o nome da pasta dos dados do programa
# (historico.pasta_de_dados, %LOCALAPPDATA%\EditorImpressao, onde moram os
# projetos). Por que (provas de 17/11/2026, relatorios/velopack-pasta-2026-11-17/
# e relatorios/nome-pacote-2026-11-17/, Velopack 1.2.161):
# - o Velopack usa %LOCALAPPDATA%\<ID> como pasta de reserva: grava ali
#   Update.exe e packages\ a cada abertura na conta do Kaique;
# - o desinstalador do .msi apaga %LOCALAPPDATA%\<titulo> inteira (o modelo
#   do .msi da 1.2.161 passa o TITULO a limpeza; o Velopack mais novo tem outra
#   limpeza que apaga %LocalAppData%\<nome>). Na prova de 17/11 o titulo era
#   igual ao nome, e ele apagou a pasta com um projeto de mentira dentro.
# Ate 17/11 este nome era "EditorImpressao", igual ao da pasta dos projetos,
# por acaso. tests/test_nome_do_pacote.py cobra a regra.
#
# Por que PODE trocar agora e NUNCA MAIS depois: o Velopack reconhece o
# programa instalado por este nome (e o .msi se registra no Windows com ele).
# Em 17/11/2026 nenhum pacote do Velopack foi instalado de verdade (nem no
# notebook do Kaique, nem no PC do Samuel; a de 28/10 do Kaique e do Inno, que
# tem outro nome, atualizacao.APPID_DO_INNO). Depois da primeira instalacao de
# verdade, trocar faz o Velopack achar que e OUTRO programa: a atualizacao nao
# acha a instalada e ficam dois programas no computador.
ID_DO_PACOTE = "EditorImpressaoPrograma"

# O motor do Kraken a parte (plano da parte do Windows, passo 2; D-768, D-788):
# ele tem publicacao propria, rara, com este nome de pacote NA ASSINATURA (outro
# nome = uma assinatura do motor nunca vale como a do programa, nem o contrario:
# assinatura.conferir_versao recusa "outro pacote"). Nao e um pacote do Velopack
# (o Velopack nunca o ve) e nao e o nome de nenhuma pasta. A versao do motor mora
# em core/ocr_kraken.VERSAO_DO_MOTOR (o programa pede a dele).
# Arriscado mudar depois da primeira publicacao do motor: a assinatura publicada
# diz este nome.
ID_DO_PACOTE_DO_MOTOR = "EditorImpressaoMotorKraken"


def etiqueta_da_versao(versao_do_pacote: str) -> str:
    """A etiqueta da publicacao de uma versao do programa: 'v1.2.0' (o programa procura
    a assinatura em releases/download/v<versao>/, atualizacao.Fonte)."""
    return f"v{versao_do_pacote}"


# O comeco do nome da etiqueta e do arquivo do motor publicado: o LUGAR UNICO (volta 3 do passo 2, achado 7 do
# relatorio 2 de quem tentou quebrar: estava escrito a mao em mais tres lugares). Quem precisa reconhecer um nome
# do motor (a etiqueta aceita do publicar, os arquivos do motor em instalar\) le daqui ou das duas funcoes abaixo.
# Arriscado mudar depois da primeira publicacao do motor (as etiquetas publicadas tem este nome).
PREFIXO_DO_MOTOR = "motor-kraken-"


def etiqueta_do_motor(versao_do_motor: int | str) -> str:
    """A etiqueta da publicacao do motor: 'motor-kraken-1' (plano-v3, peca 8)."""
    return f"{PREFIXO_DO_MOTOR}{versao_do_motor}"


def arquivo_do_motor(versao_do_motor: int | str) -> str:
    """O nome do arquivo do motor publicado (um zip so): 'motor-kraken-1.zip'. E o mesmo
    nome dentro de instalar\\ no instalador (D-788, D-727). Com "*", o molde de busca
    (Path.glob) de todos os arquivos de motor."""
    return f"{PREFIXO_DO_MOTOR}{versao_do_motor}.zip"


def numeros(versao: str) -> tuple[int, int, int]:
    """'1.2.3' -> (1, 2, 3), para comparar versoes. Levanta ValueError se o
    texto nao for tres numeros separados por ponto."""
    partes = versao.strip().split(".")
    if len(partes) != 3 or not all(p.isdigit() for p in partes):
        raise ValueError(f"versão fora do formato 1.2.3: {versao!r}")
    return int(partes[0]), int(partes[1]), int(partes[2])
