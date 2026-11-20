"""Publica, DE PROPOSITO, uma "versao para o Kaique" (decisao D-714), e o motor do Kraken a parte (D-768).

    .venv\\Scripts\\python.exe publicar_versao_kaique.py --criar-chave            (uma vez so)
    .venv\\Scripts\\python.exe publicar_versao_kaique.py --motor                  (o motor do Kraken; raro)
    .venv\\Scripts\\python.exe publicar_versao_kaique.py                          (a versao do programa, no GitHub)
    .venv\\Scripts\\python.exe publicar_versao_kaique.py --com-instalador         (e tambem o .msi, D-777)
    .venv\\Scripts\\python.exe publicar_versao_kaique.py --pasta <servidor>       (numa pasta: as provas)
    .venv\\Scripts\\python.exe publicar_versao_kaique.py --apagar v1.2.0          (apaga uma publicacao: fim da prova)

Refeito no passo 2 do plano da parte do Windows (19/11/2026; peca 8, D-776, D-777, D-789, D-795, D-773, D-768).

O QUE FAZ, PARA UMA VERSAO DO PROGRAMA, em ordem, parando no primeiro problema (nada sai pela metade):
1. acha a chave privada (fora do repositorio; assinatura.caminho_da_chave) e confere que ela e a mesma cuja parte
   publica vai dentro do programa (assinatura.CHAVE_PUBLICA_DO_SAMUEL). Sem a chave, PARA antes de tudo;
2. recusa se a versao do versao.py ja existe no destino (publicada, ou um rascunho que sobrou);
3. le de volta o motor do Kraken que esta versao pede (core/ocr_kraken.VERSAO_DO_MOTOR): ele tem de estar publicado
   e liberado no destino, com a assinatura do Samuel conferindo (D-790: nenhuma versao sem o motor que ela pede);
4. monta a pasta do programa SEM o motor solto (empacotar.construir_pasta(ATUALIZACAO); ou --pasta-pronta, que tem
   de ser desta versao, empacotar.conferir_pasta_pronta), e so entao faz a conta do espaco: o rascunho fica no
   disco de dentro (o C:, D-776) e o comando nao comeca se o disco ficaria com menos de 20 GB livres;
5. empacota pela funcao unica do vpk (empacotar.construir_pacote_do_velopack -> rodar_vpk, com a vigia do espaco),
   sem o pacote de diferenca (D-789), sem .msi e sem zip portatil (D-777); o Setup.exe e apagado na hora (D-795).
   Com --com-instalador, empacota DE NOVO a mesma pasta com o arquivo do motor publicado em instalar\\ e o .msi
   (empacotar.INSTALADOR): o .msi vai para a pasta de saida (PASTA_DE_SAIDA) e para a publicacao (como antes); o
   pacote dele NAO e publicado (o publicado e sempre o da atualizacao, sem o motor);
6. assina o pacote inteiro e confere a propria assinatura;
7. publica num destino (Destino): sobe como RASCUNHO so os arquivos da versao (arquivos_da_versao: o pacote, o indice
   releases.win.json e a assinatura; nunca o Setup.exe), le de volta (a lista do que esta la, a soma de cada
   arquivo, a assinatura lida do destino conferida contra a soma do pacote lida do destino, o indice apontando para
   essa soma, e o motor de novo) e SO ENTAO libera. Qualquer falha antes do pedido de liberar apaga o rascunho do
   destino; depois do pedido de liberar, NADA e apagado, em nenhum destino (D-816): a frase diz o que pode ter ficado
   e os comandos para conferir e apagar;
8. no fim, sempre (tambem com erro): apaga o rascunho do C: e confere que sumiu, e lista o que ficou na pasta de
   saida e no destino, dizendo se o Setup.exe esta em algum deles (D-795).

PARA O MOTOR (--motor): a chave; recusa se o motor desta versao ja foi publicado; acha o motor pronto
(empacotar.achar_motor_kraken) e confere pela ficha (core/ocr_kraken.conferir_motor); conta o espaco; comprime num
arquivo so e confere o zip pela ficha; assina com o nome de pacote do motor (versao.ID_DO_PACOTE_DO_MOTOR: uma
assinatura do motor nunca vale como a do programa); publica pelo mesmo caminho do passo 7 (etiqueta motor-kraken-<v>).

OS DESTINOS (Destino; o lugar unico de "publicar num lugar"):
- DestinoGitHub: o GitHub do projeto, pela ferramenta gh do PC do Samuel (o token fica com o gh; nunca vai para
  dentro do programa, D-719, nem para arquivo nenhum). O rascunho e um "release" de rascunho; liberar e tira-lo de
  rascunho. Nao usa mais o "vpk upload github": ele sobe tambem o Setup.exe (contra a D-795) e libera antes de a
  assinatura subir (o defeito 53 do plano).
- DestinoPasta: uma pasta que faz o papel do GitHub (as provas, D-773; quem a serve pela rede e o
  servidor_das_versoes.py): cada publicacao numa subpasta com o nome da etiqueta (<pasta>\\v1.2.0\\), e o rascunho
  numa subpasta escondida (<pasta>\\.rascunho-v1.2.0\\) que o servidor nao serve; liberar e trocar o nome.

Nunca roda sozinho e nunca a cada salvamento no GitHub: so quando alguem roda este comando (D-714). Nada aqui pede
licenca de administrador (0 perguntas do Windows).

Arriscado mudar: a etiqueta v<versao> (o programa procura a assinatura em releases/download/v<versao>/,
atualizacao.Fonte); o nome do arquivo da assinatura (assinatura.nome_do_arquivo_da_assinatura); o desenho das
subpastas do DestinoPasta (o servidor_das_versoes.py le o mesmo, por NOME_DO_RASCUNHO_NO_DESTINO); a ordem do passo 7
(liberar antes de ler de volta e o defeito 53).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

import assinatura
import atualizacao
import versao

RAIZ = Path(__file__).resolve().parent
# A pasta de saida: o que fica depois de publicar (so o .msi, quando pedido), uma subpasta por etiqueta. No D:, ao lado
# do codigo (dist\ e rascunho do empacotar, mas esta subpasta nao e apagada por ele: empacotar.gerados_em_dist).
PASTA_DE_SAIDA = RAIZ / "dist" / "publicado"
PREFIXO_DO_RASCUNHO = "publicar-"
# Um rascunho que sobrou de outra vez so e apagado depois disto (antes, pode ser de outro publicar rodando agora).
HORAS_ATE_O_RASCUNHO_SER_VELHO = 12
# A subpasta de rascunho no DestinoPasta (o servidor_das_versoes.py nao serve o que comeca com isto).
NOME_DO_RASCUNHO_NO_DESTINO = ".rascunho-"
# As etiquetas aceitas (a de uma versao do programa e a do motor): nada de barra, ponto-ponto ou espaco. O comeco
# da do motor vem do lugar unico dele (versao.PREFIXO_DO_MOTOR; achado 7 do relatorio 2).
ETIQUETA_ACEITA = re.compile(rf"^(v\d+\.\d+\.\d+|{re.escape(versao.PREFIXO_DO_MOTOR)}\d+)$")
LUGAR_DO_GH = Path(r"C:\Program Files\GitHub CLI\gh.exe")


class Parou(Exception):
    """Um problema que impede publicar; a mensagem diz o que fazer."""


class PublicacaoLiberada(Parou):
    """O apagar "só o rascunho" achou a publicação LIBERADA e não apagou (apagar_publicacao com so_rascunho)."""


class SemResposta(Parou):
    """O pedido SAIU para o destino e não houve resposta (o gh foi fechado por tempo ou pela vigia): não se sabe se ele
    foi feito. Quem chama diz isso na frase ("pedi e não deu para conferir"), nunca "não pedi" (achado 3 do relatório 3).
    """


# ---------------------------------------------------------------------------------------------------------------------
# A chave e a assinatura (D-724; assinatura.py nao muda)
# ---------------------------------------------------------------------------------------------------------------------

def criar_chave(destino: Path | None = None) -> Path:
    """Cria a chave privada do Samuel (uma vez so). Recusa se ja existe ou se o lugar e dentro do repositorio."""
    destino = Path(destino or assinatura.caminho_da_chave())
    _recusar_dentro_do_repositorio(destino)
    if destino.exists():
        raise Parou(f"já existe uma chave em {destino}; não criei outra (a do programa deixaria de bater)")
    destino.parent.mkdir(parents=True, exist_ok=True)
    chave = assinatura.nova_chave_privada()
    destino.write_text(assinatura.texto_da_chave_privada(chave), encoding="utf-8")
    print(f"chave privada criada em {destino}")
    print(f"chave pública (vai em assinatura.CHAVE_PUBLICA_DO_SAMUEL): {assinatura.secret_to_public(chave).hex()}")
    return destino


def _recusar_dentro_do_repositorio(caminho: Path) -> None:
    """A chave privada nunca mora dentro do repositorio (iria para o GitHub)."""
    caminho = Path(caminho).resolve()
    if caminho == RAIZ or RAIZ in caminho.parents:
        raise Parou(f"a chave privada não pode morar dentro do repositório ({caminho}): iria para o GitHub")


def achar_chave(arquivo: Path | None = None, chave_publica: str | None = None) -> bytes:
    """A chave privada, conferida contra a chave publica do programa (ou a
    chave_publica dada: so no ensaio e nos testes). Levanta Parou."""
    arquivo = Path(arquivo or assinatura.caminho_da_chave())
    _recusar_dentro_do_repositorio(arquivo)
    if not arquivo.is_file():
        raise Parou(f"não achei a chave privada em {arquivo}. Sem ela não se publica: a versão não seria "
                    "aceita pelo programa do Kaique. (Se a chave sumiu, use a cópia de reserva do HD externo.)")
    try:
        chave = assinatura.ler_chave_privada(arquivo)
    except (OSError, ValueError) as erro:
        raise Parou(str(erro)) from erro
    if assinatura.secret_to_public(chave).hex() != (chave_publica or assinatura.CHAVE_PUBLICA_DO_SAMUEL):
        raise Parou("a chave privada não é a da chave pública que vai dentro do programa "
                    "(assinatura.CHAVE_PUBLICA_DO_SAMUEL)")
    return chave


def assinar_arquivo(chave: bytes, arquivo: Path, pacote: str, versao_assinada: str,
                    chave_publica: str | None = None) -> Path:
    """Escreve <pacote>-<versao>.assinatura ao lado do arquivo e confere a propria assinatura (o lugar unico de
    assinar: a versao do programa e o motor). Levanta Parou."""
    v = assinatura.VersaoAssinada(pacote, versao_assinada, Path(arquivo).name, assinatura.soma_sha256(arquivo))
    texto = assinatura.escrever_assinatura(chave, v)
    motivo = assinatura.conferir_versao(texto, v, chave_publica)
    if motivo is not None:
        raise Parou(f"a assinatura feita agora não confere: {motivo}")
    destino = Path(arquivo).parent / assinatura.nome_do_arquivo_da_assinatura(pacote, versao_assinada)
    destino.write_text(texto, encoding="utf-8")
    return destino


def assinar_pacote(chave: bytes, nupkg: Path, versao_do_pacote: str, chave_publica: str | None = None) -> Path:
    """Assina o pacote inteiro de uma versao do programa (nome de pacote versao.ID_DO_PACOTE)."""
    return assinar_arquivo(chave, nupkg, versao.ID_DO_PACOTE, versao_do_pacote, chave_publica)


# ---------------------------------------------------------------------------------------------------------------------
# O rascunho no disco de dentro (D-776)
# ---------------------------------------------------------------------------------------------------------------------

def pasta_do_rascunho() -> Path:
    """Onde o publicar monta: %LOCALAPPDATA%\\EditorImpressao-publicar\\rascunho (o disco de dentro do PC do Samuel, o
    C:, D-776). Nao e a pasta dos dados do programa (%LOCALAPPDATA%\\EditorImpressao): o nome e outro de proposito."""
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "EditorImpressao-publicar" / "rascunho"


def _e_rascunho_nosso(pasta: Path) -> bool:
    """A pasta e um rascunho criado por este comando (nome com o prefixo, pasta de verdade, nao atalho)?"""
    return pasta.name.startswith(PREFIXO_DO_RASCUNHO) and pasta.is_dir() and not pasta.is_symlink() \
        and not getattr(pasta, "is_junction", lambda: False)()


def apagar_rascunho(pasta: Path, tentativas: int = 5) -> list[str]:
    """Apaga um rascunho deste comando e CONFERE que sumiu. Devolve o que ficou (vazio = apagado).

    So apaga pasta com o nome do publicar (_e_rascunho_nosso). Arquivo preso (o antivirus lendo, um programa que
    o vpk abriu): tenta de novo algumas vezes; se ficar, diz o caminho e o tamanho, nunca "apagado" sem conferir."""
    pasta = Path(pasta)
    if not pasta.exists():
        return []
    if not _e_rascunho_nosso(pasta):
        return [f"{pasta} não é um rascunho do publicar: não apaguei"]
    for vez in range(tentativas):
        shutil.rmtree(pasta, ignore_errors=True)
        if not pasta.exists():
            return []
        time.sleep(1 + vez)
    try:
        import empacotar

        sobra = f" ({empacotar.tamanho_da_pasta(pasta) / 1e6:.0f} MB)"
    except OSError:
        sobra = ""
    return [f"o rascunho {pasta} não saiu inteiro{sobra}: apague à mão quando o arquivo soltar"]


def criar_rascunho(base: Path | None = None) -> Path:
    """Um rascunho novo (vazio) para esta vez, e apaga os rascunhos velhos que sobraram de uma vez interrompida (so os
    do publicar, dentro da base)."""
    base = Path(base or pasta_do_rascunho())
    base.mkdir(parents=True, exist_ok=True)
    for velho in base.iterdir():
        if not _e_rascunho_nosso(velho):
            continue
        if time.time() - velho.stat().st_mtime < HORAS_ATE_O_RASCUNHO_SER_VELHO * 3600:
            print(f"  ATENÇÃO: há um rascunho recente de outra vez ({velho.name}): outro publicar rodando? Não apaguei.")
            continue
        for frase in apagar_rascunho(velho):
            print(f"  ATENÇÃO: {frase}")
    pasta = base / f"{PREFIXO_DO_RASCUNHO}{datetime.now():%Y%m%d-%H%M%S}-{secrets.token_hex(3)}"
    pasta.mkdir()
    return pasta


# ---------------------------------------------------------------------------------------------------------------------
# Os destinos (o lugar unico de "publicar num lugar")
# ---------------------------------------------------------------------------------------------------------------------

def e_etiqueta(nome: str) -> bool:
    """O nome e uma etiqueta nossa (v1.2.0 ou motor-kraken-1), inteiro? (fullmatch: o "$" do re casa antes de uma
    quebra de linha no fim, e "v1.2.0\\n" passava; achado 11 de quem tentou quebrar.) O lugar unico desta regra: o
    publicar e o servidor das versoes usam este."""
    return bool(ETIQUETA_ACEITA.fullmatch(nome or ""))


def _conferir_etiqueta(etiqueta: str) -> str:
    """A etiqueta e uma das nossas (v1.2.0 ou motor-kraken-1)? Levanta Parou."""
    if not e_etiqueta(etiqueta):
        raise Parou(f"etiqueta fora do formato: {etiqueta!r}")
    return etiqueta


class _Destino:
    """O que os dois destinos (DestinoPasta e DestinoGitHub) fazem igual, num lugar so (volta 4 do passo 2):
    - usar_rascunho: onde a leitura de volta pode baixar um arquivo para somar, e a vigia do espaco (achado 7 do
      relatorio 3, D-776: antes o GitHub baixava para %TEMP%, fora do rascunho, da vigia e da conta);
    - soma_pode_baixar: se a soma deste destino pode baixar um arquivo inteiro (a conta do espaco soma o maior);
    - comando_de_apagar e como_conferir: o que a frase da D-816 e a do apagar dizem para conferir e apagar depois.
    Seguro mexer: as frases. Arriscado: a soma baixar para outro lugar que nao o rascunho dado (o C: enche sem vigia)."""

    soma_pode_baixar = False
    _rascunho_da_soma: Path | None = None
    _vigia_da_soma: Callable[[], str | None] | None = None

    def usar_rascunho(self, pasta: Path | None, vigia: Callable[[], str | None] | None) -> None:
        """A pasta (dentro do rascunho do publicar, no C:) e a vigia que a leitura de volta usa se precisar baixar um
        arquivo para somar. None, None: nenhuma (a soma que precisaria baixar para, com a frase)."""
        self._rascunho_da_soma = Path(pasta) if pasta is not None else None
        self._vigia_da_soma = vigia

    def _argumentos_do_destino(self) -> str:
        """O que a linha de comando precisa para apontar para este destino (o GitHub: nada)."""
        return ""

    def comando_de_apagar(self, etiqueta: str) -> str:
        """A linha de comando que apaga a publicacao deste destino (o --apagar, que le de volta e confere)."""
        return f"publicar_versao_kaique.py --apagar {_conferir_etiqueta(etiqueta)}{self._argumentos_do_destino()}"

    def como_conferir(self, etiqueta: str) -> str:
        """Como ver, sem mudar nada, se a publicacao esta liberada, em rascunho ou nao existe."""
        raise NotImplementedError


class DestinoPasta(_Destino):
    """Uma pasta que faz o papel do GitHub (as provas, D-773). Publicacao liberada: <raiz>\\<etiqueta>\\; rascunho:
    <raiz>\\.rascunho-<etiqueta>\\ (o servidor_das_versoes.py nao serve). Todas as funcoes levantam Parou. A soma e
    lida do arquivo na pasta (nunca baixa: soma_pode_baixar = False)."""

    def __init__(self, raiz: Path | str):
        """raiz: a pasta (criada quando precisa)."""
        self.raiz = Path(raiz)

    @property
    def nome(self) -> str:
        """Como o destino aparece nas frases."""
        return f"a pasta {self.raiz}"

    def _argumentos_do_destino(self) -> str:
        """A pasta, na linha de comando."""
        return f' --pasta "{self.raiz}"'

    def como_conferir(self, etiqueta: str) -> str:
        """As duas subpastas: a da versao liberada e a do rascunho."""
        return (f"olhe a pasta {self.raiz}: a subpasta {self._liberada(etiqueta).name} é a liberada e "
                f"{self._rascunho(etiqueta).name} é o rascunho")

    def _liberada(self, etiqueta: str) -> Path:
        """A subpasta da publicacao liberada (o nome e a etiqueta, conferida)."""
        return self.raiz / _conferir_etiqueta(etiqueta)

    def _rascunho(self, etiqueta: str) -> Path:
        """A subpasta do rascunho (escondida: comeca com ponto; o servidor nao serve)."""
        return self.raiz / (NOME_DO_RASCUNHO_NO_DESTINO + _conferir_etiqueta(etiqueta))

    def _onde(self, etiqueta: str) -> Path:
        """A subpasta que existe (liberada ou rascunho); sem nenhuma, Parou."""
        for pasta in (self._liberada(etiqueta), self._rascunho(etiqueta)):
            if pasta.is_dir():
                return pasta
        raise Parou(f"não há publicação {etiqueta} em {self.nome}")

    def liberadas(self) -> list[Path]:
        """As publicacoes liberadas da pasta, em ordem de nome: as subpastas de verdade com nome de etiqueta. Atalho
        (junção ou link) nao conta (o servidor das versoes nao o serve e o apagar o recusa: a mesma regra, aqui)."""
        if not self.raiz.is_dir():
            return []
        return sorted(p for p in self.raiz.iterdir()
                      if e_etiqueta(p.name) and p.is_dir() and not p.is_symlink() and not p.is_junction())

    def situacao(self, etiqueta: str) -> str | None:
        """None (nao existe), "liberada" ou "rascunho"."""
        if self._liberada(etiqueta).is_dir():
            return "liberada"
        return "rascunho" if self._rascunho(etiqueta).is_dir() else None

    def criar_rascunho(self, etiqueta: str, titulo: str, notas: str) -> None:
        """Cria o rascunho vazio. O titulo e as notas NAO sao gravados na pasta (so o GitHub os guarda; achado 8 do
        relatorio 2: este texto dizia que iam num arquivo, e nao iam); recebidos para ter a mesma forma do GitHub."""
        try:
            self.raiz.mkdir(parents=True, exist_ok=True)
            self._rascunho(etiqueta).mkdir()
        except OSError as erro:
            raise Parou(f"não consegui criar o rascunho {etiqueta} em {self.nome} ({erro})") from erro

    def enviar(self, etiqueta: str, arquivo: Path) -> None:
        """Copia um arquivo para o rascunho pela copia conferida (empacotar.copiar_inteiro: nome provisorio, lida de
        volta, trocado de uma vez; nunca um pedaco com o nome certo)."""
        import empacotar

        try:
            empacotar.copiar_inteiro(Path(arquivo), self._rascunho(etiqueta) / Path(arquivo).name)
        except OSError as erro:
            raise Parou(f"não consegui enviar {Path(arquivo).name} para {self.nome} ({erro})") from erro

    def arquivos(self, etiqueta: str) -> dict[str, int]:
        """O que esta na publicacao (liberada ou rascunho): {nome: tamanho}, lido da pasta."""
        pasta = self._onde(etiqueta)
        return {f.name: f.stat().st_size for f in pasta.iterdir() if f.is_file()}

    def soma(self, etiqueta: str, nome: str) -> str:
        """A soma SHA-256 do arquivo como ele esta no destino (lido de la)."""
        caminho = self._onde(etiqueta) / nome
        if not caminho.is_file():
            raise Parou(f"{nome} não está na publicação {etiqueta} em {self.nome}")
        return assinatura.soma_sha256(caminho)

    def baixar(self, etiqueta: str, nome: str, pasta_local: Path) -> Path:
        """Copia um arquivo da publicacao para pasta_local (a leitura de volta). E o baixar_vigiado sem a vigia."""
        return self.baixar_vigiado(etiqueta, nome, pasta_local, None)

    def baixar_vigiado(self, etiqueta: str, nome: str, pasta_local: Path, vigia=None) -> Path:
        """Como baixar, olhando a vigia do espaco durante a copia (empacotar.vigia_do_espaco; o motor baixado para o
        rascunho, achado 7 do relatorio 2). Pela copia conferida (empacotar.copiar_inteiro)."""
        import empacotar

        origem = self._onde(etiqueta) / nome
        alvo = Path(pasta_local) / nome
        try:
            alvo.parent.mkdir(parents=True, exist_ok=True)
            empacotar.copiar_inteiro(origem, alvo, vigia)
        except OSError as erro:
            raise Parou(f"não consegui ler {nome} de {self.nome} ({erro})") from erro
        return alvo

    def liberar(self, etiqueta: str) -> None:
        """Tira do rascunho (troca o nome da subpasta de uma vez)."""
        try:
            os.rename(self._rascunho(etiqueta), self._liberada(etiqueta))
        except OSError as erro:
            raise Parou(f"não consegui liberar {etiqueta} em {self.nome} ({erro})") from erro

    def apagar(self, etiqueta: str) -> None:
        """Apaga a publicacao (rascunho ou liberada), so a subpasta dela. Se a subpasta for um atalho (junção ou link,
        D-809), NAO apaga nada (nem o atalho, nem o outro lado) e para: quem chama confere e diz o que ficou. Dentro
        dela, o shutil.rmtree do Python nao entra em junção (documentação do shutil: "On Windows, will no longer delete
        the contents of a directory junction before removing the junction", desde o 3.8)."""
        for pasta in (self._rascunho(etiqueta), self._liberada(etiqueta)):
            if pasta.is_symlink() or pasta.is_junction():
                raise Parou(f"{pasta} é um atalho para outro lugar: não apaguei (confira à mão)")
            if pasta.is_dir():
                shutil.rmtree(pasta, ignore_errors=True)

    def apagar_rascunho(self, etiqueta: str) -> None:
        """Apaga SO o rascunho (a subpasta .rascunho-<etiqueta>); a liberada nem e olhada: aqui "so o rascunho" vale
        pela construcao (sao pastas diferentes). Atalho: como em apagar."""
        pasta = self._rascunho(etiqueta)
        if pasta.is_symlink() or pasta.is_junction():
            raise Parou(f"{pasta} é um atalho para outro lugar: não apaguei (confira à mão)")
        if pasta.is_dir():
            shutil.rmtree(pasta, ignore_errors=True)


def _caminho_do_gh() -> str:
    """O gh do PC do Samuel (no PATH, ou onde o instalador do GitHub CLI o poe)."""
    return shutil.which("gh") or str(LUGAR_DO_GH)


class DestinoGitHub(_Destino):
    """O GitHub do projeto, pela ferramenta gh (o lugar unico da conversa do publicar com o GitHub: _gh). Lido do gh
    2.99 (cli/cli, pkg/cmd/release/shared/fetch.go): "release view/upload/download/edit/delete <etiqueta>" acham
    tambem o rascunho pela etiqueta; sem publicacao, "release not found". Todas as funcoes levantam Parou. Sem a soma
    pronta do GitHub, a soma baixa o arquivo (soma_pode_baixar = True), no rascunho dado por usar_rascunho."""

    soma_pode_baixar = True

    def __init__(self, repositorio: str | None = None, gh: str | None = None):
        """repositorio: 'dono/nome' (de fabrica, o de atualizacao.REPOSITORIO)."""
        self.repositorio = repositorio or atualizacao.REPOSITORIO.removeprefix("https://github.com/")
        self.gh = gh

    @property
    def nome(self) -> str:
        """Como o destino aparece nas frases."""
        return f"o GitHub ({self.repositorio})"

    def como_conferir(self, etiqueta: str) -> str:
        """O pedido de leitura que o proprio publicar faz (_ver), para rodar a mao."""
        return (f'gh release view {_conferir_etiqueta(etiqueta)} -R {self.repositorio} --json isDraft ("isDraft": '
                'true é rascunho; false, liberada; "release not found", não ficou nada)')

    def _gh(self, *argumentos: str, limite_s: float = 600, vigia=None) -> subprocess.CompletedProcess:
        """Roda o gh e devolve o resultado (o codigo de saida quem decide e quem chama). Pelo laco unico da peca do
        Windows (core/windows.rodar_em_grupo, o mesmo do vpk; volta 4, achado 8 do relatorio 3, CLAUDE.md §11.12,
        ponto 1: antes o gh rodava com o subprocess direto, sem grupo, e fechar fechava so o gh): o gh roda num grupo do
        Windows, com a saida guardada (UTF-8, como o gh escreve); a cada INTERVALO_DA_VIGIA_S o laco olha a 'vigia'
        (empacotar.vigia_do_espaco: o download para o rascunho, achado 7 do relatorio 2) e o 'limite_s'; se e para
        parar, fecha o gh e o que ele abriu (conferido). Ctrl+C: o laco fecha o grupo e repassa.
        O gh que nao abre (ou que a peca recusa): Parou, e nada foi pedido. O gh fechado por tempo ou pela vigia:
        SemResposta (o pedido saiu e nao se sabe se foi feito)."""
        import empacotar
        from core import windows

        comando = [self.gh or _caminho_do_gh(), *argumentos, "-R", self.repositorio]
        r = windows.rodar_em_grupo(comando, vigia=vigia, limite_s=limite_s, intervalo_s=empacotar.INTERVALO_DA_VIGIA_S,
                                   capturar=True, letras="utf-8")
        if not r.dados.get("abriu"):
            raise Parou(f"não consegui falar com o GitHub pelo gh ({r.motivo})")
        if r.dados.get("parou"):
            ficou = "" if r.dados.get("fechado") else f"; ATENÇÃO: {r.dados.get('fechou')}"
            raise SemResposta(f"parei o pedido ao GitHub ({' '.join(argumentos[:2])}): {r.dados['parou']}{ficou}")
        return subprocess.CompletedProcess(comando, r.dados["codigo"], r.dados["saida"], r.dados["erros"])

    def _exigir(self, r: subprocess.CompletedProcess, o_que: str) -> subprocess.CompletedProcess:
        """O gh respondeu sem erro? Senao, Parou com o que ele disse."""
        if r.returncode != 0:
            raise Parou(f"o GitHub não deixou {o_que}: {(r.stderr or r.stdout).strip()[:300]}")
        return r

    def _ver(self, etiqueta: str, campos: str) -> dict | None:
        """'release view --json <campos>': o lido, ou None so quando o gh diz "release not found" (qualquer outro
        erro e Parou: falha nunca vira "nao existe", CLAUDE.md §11.12, ponto 2)."""
        r = self._gh("release", "view", _conferir_etiqueta(etiqueta), "--json", campos)
        if r.returncode != 0:
            if "release not found" in (r.stderr or "").lower():
                return None
            raise Parou(f"não consegui perguntar ao GitHub pela publicação {etiqueta}: "
                        f"{(r.stderr or r.stdout).strip()[:300]}")
        try:
            return json.loads(r.stdout)
        except ValueError as erro:
            raise Parou(f"o GitHub respondeu algo que o publicar não entendeu ({erro})") from erro

    def situacao(self, etiqueta: str) -> str | None:
        """None (nao existe), "liberada" ou "rascunho"."""
        lido = self._ver(etiqueta, "isDraft,tagName")
        if lido is None:
            return None
        return "rascunho" if lido.get("isDraft") else "liberada"

    def criar_rascunho(self, etiqueta: str, titulo: str, notas: str) -> None:
        """Cria o release de rascunho (o GitHub so cria a etiqueta ao liberar)."""
        self._exigir(self._gh("release", "create", _conferir_etiqueta(etiqueta), "--draft", "--title", titulo,
                              "--notes", notas), f"criar o rascunho {etiqueta}")

    def enviar(self, etiqueta: str, arquivo: Path) -> None:
        """Sobe um arquivo para o rascunho."""
        self._exigir(self._gh("release", "upload", _conferir_etiqueta(etiqueta), str(arquivo), limite_s=3 * 3600),
                     f"enviar {Path(arquivo).name}")

    def _assets(self, etiqueta: str) -> list[dict]:
        """Os arquivos da publicacao, como o gh os descreve (nome, tamanho, digest)."""
        lido = self._ver(etiqueta, "assets")
        if lido is None:
            raise Parou(f"não há publicação {etiqueta} em {self.nome}")
        return list(lido.get("assets") or [])

    def arquivos(self, etiqueta: str) -> dict[str, int]:
        """O que esta na publicacao: {nome: tamanho}, lido do GitHub."""
        return {a["name"]: int(a.get("size") or 0) for a in self._assets(etiqueta)}

    def soma(self, etiqueta: str, nome: str) -> str:
        """A soma SHA-256 do arquivo como ele esta no GitHub: a que o GitHub calcula ('digest', "sha256:..."); sem
        ela, baixa o arquivo e soma (a leitura de volta nunca e dada como feita sem ler). O download vai para o
        rascunho dado por usar_rascunho (no C:, apagado no fim), pela peca que baixa vigiada (baixar_vigiado) com a
        vigia do espaco (volta 4, achado 7 do relatorio 3, D-776: antes ia para %TEMP%, fora do rascunho, da vigia e da
        conta); a subpasta e apagada logo depois de somar. Sem rascunho dado: Parou (nunca baixa para outro lugar)."""
        for a in self._assets(etiqueta):
            if a.get("name") == nome:
                digest = str(a.get("digest") or "")
                if digest.startswith("sha256:"):
                    return digest.removeprefix("sha256:").lower()
                if self._rascunho_da_soma is None:
                    raise Parou(f"o GitHub não deu a soma de {nome}, e não há rascunho no disco de dentro para "
                                "baixá-lo e somar: nada foi baixado")
                pasta = self._rascunho_da_soma / f"soma-{secrets.token_hex(3)}"
                try:
                    return assinatura.soma_sha256(self.baixar_vigiado(etiqueta, nome, pasta, self._vigia_da_soma))
                finally:
                    shutil.rmtree(pasta, ignore_errors=True)
        raise Parou(f"{nome} não está na publicação {etiqueta} em {self.nome}")

    def baixar(self, etiqueta: str, nome: str, pasta_local: Path) -> Path:
        """Baixa um arquivo da publicacao para pasta_local (a leitura de volta). E o baixar_vigiado sem a vigia."""
        return self.baixar_vigiado(etiqueta, nome, pasta_local, None)

    def baixar_vigiado(self, etiqueta: str, nome: str, pasta_local: Path, vigia=None) -> Path:
        """Como baixar, olhando a vigia do espaco enquanto o gh baixa (_gh com a vigia)."""
        Path(pasta_local).mkdir(parents=True, exist_ok=True)
        com_vigia = {"vigia": vigia} if vigia is not None else {}    # sem vigia, o pedido de sempre ao gh
        self._exigir(self._gh("release", "download", _conferir_etiqueta(etiqueta), "--pattern", nome,
                              "--dir", str(pasta_local), "--clobber", limite_s=3 * 3600, **com_vigia),
                     f"baixar {nome}")
        baixado = Path(pasta_local) / nome
        if not baixado.is_file():
            raise Parou(f"o GitHub não entregou {nome} da publicação {etiqueta}")
        return baixado

    def liberar(self, etiqueta: str) -> None:
        """Tira do rascunho."""
        self._exigir(self._gh("release", "edit", _conferir_etiqueta(etiqueta), "--draft=false"),
                     f"liberar {etiqueta}")

    def apagar(self, etiqueta: str) -> str | None:
        """Pede ao GitHub para apagar a publicacao (e, se ja liberada, a etiqueta). Devolve o aviso do gh, se ele
        reclamou, ou None. QUEM DIZ SE APAGOU E A LEITURA DE VOLTA (apagar_publicacao), nunca o codigo de saida do gh.

        Lido no gh (cli/cli, pkg/cmd/release/delete/delete.go, deleteRun e deleteTag, 19/11): ele apaga a publicacao
        e, com --cleanup-tag, apaga DEPOIS a etiqueta refs/tags/<etiqueta>, sem olhar se e rascunho, e sai com o erro
        dessa segunda parte. Num rascunho a etiqueta ainda nao existe (o GitHub so a cria ao liberar; o fetch.go chama
        de "pending tag"): pedir --cleanup-tag ali dava erro de uma publicacao que tinha sido apagada (achado 1 de quem
        tentou quebrar). Por isso: rascunho sem --cleanup-tag; liberada com."""
        return self._pedir_para_apagar(etiqueta, self.situacao(etiqueta))

    def apagar_rascunho(self, etiqueta: str) -> str | None:
        """Apaga SO se for rascunho, lido do GitHub AQUI, logo antes de pedir (nunca uma leitura feita antes por quem
        chama; achado 1 do relatorio 2). Liberada: PublicacaoLiberada, sem pedir nada. Devolve o aviso do gh, como em
        apagar. Fica um instante entre esta leitura e o pedido de apagar: o GitHub nao tem um "apague so se for
        rascunho" (a API de apagar recebe so o numero da publicacao); escrito nas Ressalvas do passo 2."""
        situacao = self.situacao(etiqueta)
        if situacao == "liberada":
            raise PublicacaoLiberada(f"{etiqueta} está liberada em {self.nome}: só o rascunho podia ser apagado aqui, "
                                     "e NÃO apaguei")
        return self._pedir_para_apagar(etiqueta, situacao)

    def _pedir_para_apagar(self, etiqueta: str, situacao: str | None) -> str | None:
        """O pedido de apagar ao gh, para a situacao lida (None = nada a pedir): rascunho sem --cleanup-tag, liberada
        com (ver apagar). Devolve o aviso do gh, se ele reclamou."""
        if situacao is None:
            return None
        pedido = ["release", "delete", _conferir_etiqueta(etiqueta), "--yes"]
        if situacao == "liberada":
            pedido.append("--cleanup-tag")
        r = self._gh(*pedido)
        if r.returncode != 0:
            return f"o gh avisou ao apagar: {(r.stderr or r.stdout).strip()[:300]}"
        return None


def destino_de(destino_pasta: Path | None) -> DestinoPasta | DestinoGitHub:
    """O destino pedido na linha de comando: a pasta (--pasta) ou o GitHub."""
    return DestinoPasta(destino_pasta) if destino_pasta is not None else DestinoGitHub()


def apagar_publicacao(destino, etiqueta: str, so_rascunho: bool = False, acabou_de_criar: bool = False) -> str | None:
    """Apaga uma publicacao do destino e CONFERE, lendo de volta, que sumiu. O LUGAR UNICO de apagar uma publicacao (o
    --apagar e o caminho de erro do publicar de antes do pedido de liberar) e o UNICO que escreve a frase de cada
    desfecho, porque so ele sabe se o pedido de apagar chegou a sair (volta 4, achado 3 do relatorio 3: a frase dizia
    "NAO apaguei" tendo pedido e apagado).

    Devolve (o aviso do destino, ou None) so quando: pediu para apagar e a leitura de depois diz que sumiu; ou ja nao
    existia (sem acabou_de_criar). Todo o resto levanta, com a frase pronta, o comando para conferir e o de apagar:
    - a leitura de antes falha: Parou "NAO pedi para apagar nada";
    - acabou_de_criar e a leitura nao acha (volta 4, achado 4: logo depois de criar, "nao achei" nao e "sumiu"; a frase
      dizia "foi apagada (conferido)" com o rascunho no GitHub): Parou "nao achei o rascunho para apagar";
    - so_rascunho e esta liberada (antes, ou na leitura de novo do proprio destino logo antes de pedir):
      PublicacaoLiberada, nada pedido;
    - o pedido nao saiu (o gh nao abriu, a leitura de novo falhou, a publicacao e um atalho): Parou "nao apaguei";
    - o pedido saiu e ficou sem resposta (SemResposta), ou a leitura de depois falha: Parou "pedi para apagar e nao deu
      para conferir se sumiu";
    - depois de pedir, continua la: Parou "continua la" (ou PublicacaoLiberada, se a leitura diz liberada).
    Achado 1 da volta 1: o aviso do gh nao decide; quem decide e a leitura de volta."""
    conferir = f"confira com: {destino.como_conferir(etiqueta)}; e apague com: {destino.comando_de_apagar(etiqueta)}"
    try:
        antes = destino.situacao(etiqueta)
    except Parou as erro:
        raise Parou(f"não consegui ler {etiqueta} em {destino.nome} antes de apagar ({erro}): NÃO pedi para apagar "
                    f"nada; {conferir}") from erro
    if antes is None:
        if acabou_de_criar:
            raise Parou(f"não achei o rascunho {etiqueta} em {destino.nome} para apagar (pode não ter chegado a ser "
                        "criado, ou a leitura logo depois de criar ainda não o mostra): NÃO pedi para apagar nada; "
                        f"{conferir}")
        return None
    if so_rascunho and antes != "rascunho":
        raise PublicacaoLiberada(f"{etiqueta} está liberada em {destino.nome}: só o rascunho podia ser apagado aqui, "
                                 "e NÃO apaguei")
    try:
        aviso = destino.apagar_rascunho(etiqueta) if so_rascunho else destino.apagar(etiqueta)
    except PublicacaoLiberada:
        raise
    except SemResposta as erro:
        raise Parou(f"pedi para apagar {etiqueta} em {destino.nome} e não deu para conferir se sumiu ({erro}); "
                    f"{conferir}") from erro
    except Parou as erro:
        raise Parou(f"não apaguei {etiqueta} em {destino.nome}: {erro}; {conferir}") from erro
    try:
        depois = destino.situacao(etiqueta)
    except Parou as erro:
        raise Parou(f"pedi para apagar {etiqueta} em {destino.nome} e não deu para conferir se sumiu ({erro}); "
                    f"{conferir}") from erro
    if so_rascunho and depois == "liberada":
        raise PublicacaoLiberada(f"pedi para apagar o rascunho {etiqueta} em {destino.nome}, e ele está liberado "
                                 "agora (foi liberado no meio, antes do pedido de apagar)")
    if depois is not None:
        raise Parou(f"pedi para apagar {etiqueta} em {destino.nome}, e ela continua lá" + (f" ({aviso})" if aviso else "")
                    + f"; {conferir}")
    return aviso


def _frase_depois_do_pedido_de_liberar(destino, etiqueta: str) -> str:
    """A frase do caminho de erro DEPOIS do pedido de liberar (D-816, o lugar unico): nada foi apagado; o que pode ter
    ficado (liberada, inteira, ou rascunho); como conferir; e o comando para apagar o rascunho depois. Nao le nada do
    destino (a decisao de nao apagar nao depende de leitura, e uma leitura atrasada nao entra na frase)."""
    return (f"{etiqueta}: pedi para liberar em {destino.nome} e não deu para reconferir agora se ficou liberada. Depois "
            "do pedido de liberar, o publicar nunca apaga nada (uma leitura atrasada poderia apagar a versão já "
            "liberada), e NÃO apaguei. Ela pode ter ficado de dois jeitos: se ficou liberada em "
            f"{destino.nome}, está inteira (tudo foi lido de volta antes do pedido) e vale: não publique de novo com "
            f"{etiqueta}; se ficou como rascunho, apague depois com: {destino.comando_de_apagar(etiqueta)}; e publique "
            f"de novo. Para conferir qual dos dois: {destino.como_conferir(etiqueta)}")


# ---------------------------------------------------------------------------------------------------------------------
# Publicar num destino: rascunho, enviar, ler de volta, liberar (o lugar unico; a versao do programa e o motor)
# ---------------------------------------------------------------------------------------------------------------------

def publicar_arquivos(destino, etiqueta: str, titulo: str, notas: str, arquivos: list[Path],
                      conferir_lido: Callable[[], None]) -> None:
    """Publica 'arquivos' na etiqueta, nunca pela metade (o defeito 53 do plano).

    1. recusa se a etiqueta ja existe (liberada ou rascunho que sobrou);
    2. cria o rascunho e envia SO estes arquivos;
    3. le de volta: a lista do que esta la tem de ser exatamente a enviada (nada a mais: nunca um Setup.exe), e a
       soma de cada um, lida do destino, a do arquivo local; depois conferir_lido() (a assinatura e o resto, lidos do
       destino; levanta Parou);
    4. so entao libera, e confere que ficou liberada.
    Qualquer falha (ou Ctrl+C) ANTES do pedido de liberar (o criar do rascunho incluido: se ele cria e a resposta se
    perde, o rascunho e procurado e apagado; volta 4, achado 4 do relatorio 3) apaga SO O RASCUNHO do destino e confere
    que sumiu (apagar_publicacao com so_rascunho e acabou_de_criar: a regra e a frase moram la).
    DEPOIS do pedido de liberar, NADA e apagado, em nenhum destino, sem ler nada (D-816, Samuel 20/11/2026: "A , mas
    onde estamos antes de você fazer qualquer processo"; volta 4, achado 1 do relatorio 3: com duas leituras atrasadas
    do GitHub, o apagar "so o rascunho" apagava a versao liberada). A frase (_frase_depois_do_pedido_de_liberar) diz
    que pode ter ficado liberada (inteira) ou rascunho, como conferir e o comando para apagar o rascunho depois. Por que
    nao apagar: quando o liberar e pedido, tudo ja foi lido de volta e conferido; apagar uma versao liberada deixaria o
    numero dela livre para outro conteudo ("um numero de versao so", peca 8). Isso troca o que a volta 3 fazia quando o
    liberar falhava e continuava rascunho (apagava o rascunho): agora o rascunho fica, e a frase diz o comando."""
    situacao = destino.situacao(etiqueta)
    if situacao == "liberada":
        raise Parou(f"{etiqueta} já está publicada em {destino.nome}: aumente o número (versao.py ou "
                    "core/ocr_kraken.VERSAO_DO_MOTOR)")
    if situacao == "rascunho":
        raise Parou(f"sobrou um rascunho de {etiqueta} em {destino.nome} (de uma vez interrompida): apague com "
                    f"--apagar {etiqueta} e rode de novo")
    nomes = [Path(a).name for a in arquivos]
    print(f"  {destino.nome}: rascunho {etiqueta} ({', '.join(nomes)})")
    pediu_para_liberar = False
    try:
        destino.criar_rascunho(etiqueta, titulo, notas)
        for arquivo in arquivos:
            destino.enviar(etiqueta, Path(arquivo))
        lidos = destino.arquivos(etiqueta)
        if sorted(lidos) != sorted(nomes):
            raise Parou(f"o rascunho de {etiqueta} tem {sorted(lidos)}, e o enviado foi {sorted(nomes)}")
        for arquivo in arquivos:
            if destino.soma(etiqueta, Path(arquivo).name) != assinatura.soma_sha256(arquivo):
                raise Parou(f"{Path(arquivo).name} chegou diferente em {destino.nome}")
        conferir_lido()
        print(f"  lido de volta de {destino.nome}: {len(nomes)} arquivo(s), somas e assinatura conferidas")
        pediu_para_liberar = True
        destino.liberar(etiqueta)
        if destino.situacao(etiqueta) != "liberada":
            raise Parou(f"pedi para liberar {etiqueta} em {destino.nome}, e ela não ficou liberada")
    except BaseException as erro:
        if pediu_para_liberar:
            desfeito = _frase_depois_do_pedido_de_liberar(destino, etiqueta)          # D-816: nada se apaga
        else:
            try:
                aviso = apagar_publicacao(destino, etiqueta, so_rascunho=True, acabou_de_criar=True)
                desfeito = f"a publicação {etiqueta} foi apagada de {destino.nome} (conferido)" + (
                    f"; {aviso}" if aviso else "")
            except PublicacaoLiberada as liberada:
                desfeito = (f"{liberada}. Eu não pedi para liberar: outra pessoa ou outro publicar a liberou no "
                            f"meio. Confira à mão o que ela tem ({destino.comando_de_apagar(etiqueta)} apaga, se "
                            "estiver errada)")
            except Parou as outro:
                desfeito = f"ATENÇÃO: {outro}"
        if isinstance(erro, Parou):
            raise Parou(f"{erro}. {desfeito}") from erro
        print(f"  {desfeito}")
        raise
    print(f"  {etiqueta} liberada em {destino.nome}")


def obter_motor_publicado(destino, pasta_local: Path, chave_publica: str | None = None,
                          versao_do_motor: int | None = None, exigir_liberado: bool = True):
    """Le de volta o motor que esta versao do programa pede (D-790): publicado e LIBERADO no destino, com o arquivo e
    a assinatura do Samuel (pacote do motor, versao, nome e a soma do arquivo como esta no destino). Devolve o
    empacotar.MotorPublicado. Levanta Parou. exigir_liberado=False so na leitura de volta da propria publicacao do
    motor (ainda em rascunho, publicar_motor): a mesma conferencia, num lugar so."""
    import empacotar
    from core import ocr_kraken

    v = ocr_kraken.VERSAO_DO_MOTOR if versao_do_motor is None else versao_do_motor
    etiqueta, arquivo = versao.etiqueta_do_motor(v), versao.arquivo_do_motor(v)
    nome_da_assinatura = assinatura.nome_do_arquivo_da_assinatura(versao.ID_DO_PACOTE_DO_MOTOR, str(v))
    if destino.situacao(etiqueta) != "liberada" and exigir_liberado:
        raise Parou(f"o motor do Kraken {v}, que esta versão pede, não está publicado em {destino.nome}: publique o "
                    "motor antes (--motor)")
    presentes = destino.arquivos(etiqueta)
    if arquivo not in presentes or nome_da_assinatura not in presentes:
        raise Parou(f"a publicação {etiqueta} em {destino.nome} não tem {arquivo} e {nome_da_assinatura}")
    texto = destino.baixar(etiqueta, nome_da_assinatura, pasta_local).read_text(encoding="utf-8", errors="replace")
    soma = destino.soma(etiqueta, arquivo)
    motivo = assinatura.conferir_versao(
        texto, assinatura.VersaoAssinada(versao.ID_DO_PACOTE_DO_MOTOR, str(v), arquivo, soma), chave_publica)
    if motivo is not None:
        raise Parou(f"o motor publicado em {destino.nome} não confere: {motivo}")
    return empacotar.MotorPublicado(v, arquivo, soma, etiqueta)


def arquivos_da_versao(saida_do_vpk: Path, versao_do_pacote: str, arquivo_da_assinatura: Path,
                       msi: Path | None = None) -> list[Path]:
    """O que vai ao destino numa versao do programa (o LUGAR UNICO): o pacote inteiro, o indice que o programa do
    Kaique le (releases.win.json, gravado pelo vpk so com esta versao), a assinatura e, so quando o instalador foi
    pedido (D-777), o .msi (como antes deste passo, quando o vpk upload subia o .msi junto; o programa do Kaique nao o
    usa para atualizar). Nunca o Setup.exe (D-795), nunca o zip portatil, o assets.win.json nem o RELEASES antigo."""
    import empacotar

    arquivos = [empacotar.nupkg_inteiro(saida_do_vpk, versao_do_pacote),
                Path(saida_do_vpk) / empacotar.NOME_DO_INDICE, Path(arquivo_da_assinatura)]
    return arquivos + ([Path(msi)] if msi is not None else [])


def _conferir_versao_lida(destino, etiqueta: str, versao_do_pacote: str, nupkg: Path, motor,
                          pasta_lida: Path, chave_publica: str | None) -> Callable[[], None]:
    """A leitura de volta de uma versao do programa (para publicar_arquivos): a assinatura lida do destino confere
    com a soma do pacote lida do destino; o indice lido do destino aponta para esse pacote com essa soma; e o motor
    que ela pede continua publicado e e o mesmo do motor-exigido.json."""
    import empacotar

    def conferir() -> None:
        """Le de volta do destino e confere (levanta Parou)."""
        soma = destino.soma(etiqueta, nupkg.name)
        nome = assinatura.nome_do_arquivo_da_assinatura(versao.ID_DO_PACOTE, versao_do_pacote)
        texto = destino.baixar(etiqueta, nome, pasta_lida).read_text(encoding="utf-8", errors="replace")
        motivo = assinatura.conferir_versao(
            texto, assinatura.VersaoAssinada(versao.ID_DO_PACOTE, versao_do_pacote, nupkg.name, soma), chave_publica)
        if motivo is not None:
            raise Parou(f"a assinatura lida de {destino.nome} não confere: {motivo}")
        try:
            indice = json.loads(destino.baixar(etiqueta, empacotar.NOME_DO_INDICE, pasta_lida)
                                .read_text(encoding="utf-8-sig"))
            itens = [a for a in indice.get("Assets", []) if a.get("FileName") == nupkg.name]
        except (ValueError, AttributeError) as erro:
            raise Parou(f"o índice {empacotar.NOME_DO_INDICE} lido de {destino.nome} está estragado ({erro})") from erro
        if len(itens) != 1 or str(itens[0].get("SHA256", "")).lower() != soma or \
                str(itens[0].get("Version")) != versao_do_pacote:
            raise Parou(f"o índice {empacotar.NOME_DO_INDICE} lido de {destino.nome} não aponta para o pacote "
                        "publicado")
        de_novo = obter_motor_publicado(destino, pasta_lida, chave_publica, motor.versao)
        if de_novo != motor:
            raise Parou("o motor publicado mudou durante a publicação")

    return conferir


def conferencia_do_fim(destino, etiqueta: str, pasta_de_saida: Path, rascunho: Path | None,
                       msi_feito: tuple[str, int, str] | None = None) -> list[str]:
    """O que o publicar mostra no fim, sempre (D-795, D-776): o rascunho sumiu?, o que ficou na pasta de saida e no
    destino, e se o Setup.exe esta em algum deles. Lido, nunca suposto.

    O .msi (volta 3, achado 2 do relatorio 2): msi_feito = (nome, tamanho, soma) do .msi como ele saiu no rascunho
    (lido antes de o rascunho ser apagado). O .msi da pasta de saida e comparado com ele (tamanho e soma, lidos do
    arquivo de la); um .msi que nao foi feito agora, um que nao chegou e um pedaco de copia (.copiando) sao acusados."""
    import empacotar

    setup = empacotar.nome_do_setup()
    linhas = []
    if rascunho is not None:
        linhas.append(_linha_do_rascunho(rascunho))
    saida = Path(pasta_de_saida)
    no_saida = sorted(f.name for f in saida.iterdir()) if saida.is_dir() else []
    linhas.append(f"pasta de saída ({saida}): {', '.join(no_saida) or 'vazia'}")
    linhas += _conferir_o_msi_da_saida(saida, no_saida, msi_feito)
    try:
        no_destino = sorted(destino.arquivos(etiqueta)) if destino.situacao(etiqueta) else []
        linhas.append(f"{destino.nome}, {etiqueta}: {', '.join(no_destino) or 'nada publicado'}")
    except Parou as erro:
        no_destino = None
        linhas.append(f"{destino.nome}: não deu para ler ({erro})")
    if setup in no_saida or (no_destino and setup in no_destino):
        linhas.append(f"ATENÇÃO: o {setup} está {'na pasta de saída' if setup in no_saida else 'no destino'}")
    elif no_destino is not None:
        linhas.append(f"{setup}: não está na pasta de saída nem no destino (conferido)")
    return linhas


def _linha_do_rascunho(rascunho: Path) -> str:
    """A linha da conferencia do fim sobre o rascunho do disco de dentro (lido: existe ou nao). O lugar unico: a versao
    do programa e o motor."""
    return f"rascunho do disco de dentro: {f'ainda existe: {rascunho}' if rascunho.exists() else 'apagado (conferido)'}"


def _conferir_o_msi_da_saida(saida: Path, no_saida: list[str], msi_feito: tuple[str, int, str] | None) -> list[str]:
    """As linhas da conferencia do fim sobre o .msi da pasta de saida (ver conferencia_do_fim)."""
    linhas = [f"ATENÇÃO: {nome} na pasta de saída é um pedaço de cópia que não terminou" for nome in no_saida
              if nome.endswith(".copiando")]
    if msi_feito is not None:
        nome, tamanho, soma = msi_feito
        if nome not in no_saida:
            linhas.append(f"instalador {nome}: NÃO está na pasta de saída")
        else:
            try:
                igual = (saida / nome).stat().st_size == tamanho and assinatura.soma_sha256(saida / nome) == soma
                linhas.append(f"instalador {nome}: igual ao feito agora (tamanho e soma conferidos)" if igual else
                              f"ATENÇÃO: o instalador {nome} da pasta de saída é diferente do feito agora")
            except OSError as erro:
                linhas.append(f"ATENÇÃO: não deu para ler o instalador {nome} da pasta de saída ({erro})")
    for nome in no_saida:
        if nome.lower().endswith(".msi") and (msi_feito is None or nome != msi_feito[0]):
            linhas.append(f"ATENÇÃO: {nome} na pasta de saída não foi feito agora")
    return linhas


def _fim(destino, etiqueta: str, pasta_de_saida: Path, rascunho: Path,
         msi_feito: tuple[str, int, str] | None = None) -> list[str]:
    """Apaga o rascunho (conferido) e imprime a conferencia do fim. Devolve o que nao saiu do rascunho."""
    ficou = apagar_rascunho(rascunho)
    for frase in ficou:
        print(f"  ATENÇÃO: {frase}")
    print("\n  Conferência do fim:")
    for linha in conferencia_do_fim(destino, etiqueta, pasta_de_saida, rascunho, msi_feito):
        print(f"    {linha}")
    return ficou


def _notas(o_que: str) -> str:
    """As notas da publicacao: o que e e de que commit saiu (pela peca do git; se nao responder, diz)."""
    try:
        from regras_dos_agentes import conversa_com_o_git as git

        commit = git.commit_completo(RAIZ, "HEAD")
    except Exception as erro:  # noqa: BLE001 - so anota
        commit = f"não deu para ler ({erro})"
    return f"{o_que}. Publicada em {datetime.now():%d/%m/%Y %H:%M} a partir do commit {commit}."


# ---------------------------------------------------------------------------------------------------------------------
# A versao do programa
# ---------------------------------------------------------------------------------------------------------------------

def publicar(versao_do_pacote: str, destino_pasta: Path | None = None, pasta_pronta: Path | None = None,
             arquivo_da_chave: Path | None = None, chave_publica: str | None = None,
             vpk: Path | None = None, com_instalador: bool = False, rascunho_base: Path | None = None,
             pasta_de_saida: Path | None = None, destino=None) -> Path:
    """O caminho inteiro de uma versao do programa (ver o cabecalho). Devolve o nome do pacote publicado (o caminho
    dele no rascunho, que ja foi apagado). Levanta Parou. 'destino' (um Destino pronto) e so para os testes."""
    import empacotar

    chave = achar_chave(arquivo_da_chave, chave_publica)
    versao.numeros(versao_do_pacote)
    destino = destino or destino_de(destino_pasta)
    etiqueta = versao.etiqueta_da_versao(versao_do_pacote)
    if destino.situacao(etiqueta) is not None:
        raise Parou(f"a versão {versao_do_pacote} já existe em {destino.nome} (publicada ou rascunho que sobrou): "
                    f"aumente o número em versao.py, ou apague o rascunho com --apagar {etiqueta}")
    vpk = vpk or empacotar.achar_vpk()
    if vpk is None:
        raise Parou(f"não achei o vpk ({empacotar.COMO_INSTALAR_O_VPK})")
    saida_final = Path(pasta_de_saida or PASTA_DE_SAIDA) / etiqueta
    rascunho = criar_rascunho(rascunho_base)
    print(f"  rascunho: {rascunho}")
    # o que a leitura de volta baixar para somar fica no rascunho, na vigia (achado 7 do relatorio 3)
    destino.usar_rascunho(rascunho / "somar", empacotar.vigia_do_espaco(rascunho))
    msi_feito = None
    try:
        motor = obter_motor_publicado(destino, rascunho / "lido", chave_publica)
        print(f"  motor do Kraken {motor.versao} publicado e conferido ({motor.arquivo})")
        pecas = None
        if pasta_pronta is not None:
            pasta = Path(pasta_pronta)
        else:
            pasta = empacotar.construir_pasta(empacotar.ATUALIZACAO)
            if pasta is None:
                raise Parou("a montagem da pasta do programa parou (o motivo está acima)")
            pecas = empacotar._PECAS
        problemas = empacotar.conferir_pasta_pronta(pasta, versao_do_pacote)
        if problemas:
            raise Parou("a pasta do programa não serve: " + "; ".join(problemas))
        saidas = (empacotar.ATUALIZACAO, empacotar.INSTALADOR) if com_instalador else (empacotar.ATUALIZACAO,)
        tamanho_do_motor = 0
        if com_instalador:
            tamanho_do_motor = destino.arquivos(motor.etiqueta).get(motor.arquivo, 0)
        tamanho_da_pasta = empacotar.tamanho_da_pasta(pasta)
        para_somar = 0
        if destino.soma_pode_baixar:
            # a leitura de volta pode baixar um arquivo de cada vez para somar (achado 7 do relatorio 3): o maior deles
            # (o pacote, ou o .msi com o motor, contados pela pasta; ou o motor publicado)
            motor_publicado = tamanho_do_motor or destino.arquivos(motor.etiqueta).get(motor.arquivo, 0)
            para_somar = max(tamanho_da_pasta + tamanho_do_motor, motor_publicado)
        # o motor baixado para o rascunho (com o instalador) fica la ate o fim: entra na conta (achado 7 do relatorio 2)
        precisa = empacotar.espaco_que_vai_usar(tamanho_da_pasta, saidas, tamanho_do_motor,
                                                baixado_para_o_rascunho=tamanho_do_motor + para_somar)
        motivo = empacotar.conferir_espaco(rascunho, precisa)
        if motivo is not None:
            raise Parou(motivo)
        print(f"  espaço: este trabalho usa uns {precisa / empacotar.GB:.1f} GB em {rascunho.anchor}; "
              f"livres agora: {empacotar.espaco_livre(rascunho) / empacotar.GB:.1f} GB")
        nupkg = empacotar.construir_pacote_do_velopack(rascunho / "atualizacao", versao_do_pacote,
                                                       empacotar.ATUALIZACAO, pasta, motor, rascunho=rascunho,
                                                       vpk=vpk, pecas=pecas)
        if nupkg is None:
            raise Parou("o empacotamento da atualização parou (o motivo está acima)")
        if com_instalador:
            # na vigia do espaco, como o vpk (achado 7 do relatorio 2)
            arquivo_do_motor = destino.baixar_vigiado(motor.etiqueta, motor.arquivo, rascunho / "motor",
                                                      empacotar.vigia_do_espaco(rascunho))
            try:
                outro = empacotar.construir_pacote_do_velopack(rascunho / "instalador", versao_do_pacote,
                                                               empacotar.INSTALADOR, pasta, motor, arquivo_do_motor,
                                                               rascunho=rascunho, vpk=vpk, pecas=pecas)
            finally:
                # a pasta volta a ser a da atualização (tira o arquivo do motor de instalar\), também com erro
                problemas = empacotar.preparar_saida(pasta, empacotar.ATUALIZACAO, None, motor)
            if outro is None or problemas:
                raise Parou("o empacotamento do instalador parou (o motivo está acima) " + "; ".join(problemas))
            # o .msi do vpk tem o mesmo nome em toda versão; publicado com o número dela (achado 7)
            msi = rascunho / "instalador" / empacotar.nome_do_msi_publicado(versao_do_pacote)
            (rascunho / "instalador" / empacotar.nome_do_msi()).replace(msi)
            msi_feito = (msi.name, msi.stat().st_size, assinatura.soma_sha256(msi))
        else:
            msi = None
        arquivo_assinado = assinar_pacote(chave, nupkg, versao_do_pacote, chave_publica)
        arquivos = arquivos_da_versao(nupkg.parent, versao_do_pacote, arquivo_assinado, msi)
        publicar_arquivos(destino, etiqueta, f"Versão para o Kaique {versao_do_pacote}",
                          _notas(f"Versão {versao_do_pacote} do Editor de Impressão (pede o motor do Kraken "
                                 f"{motor.versao})"), arquivos,
                          _conferir_versao_lida(destino, etiqueta, versao_do_pacote, nupkg, motor,
                                                rascunho / "lido-de-volta", chave_publica))
        if msi is not None:
            # só depois de publicada: um .msi de versão que não saiu nunca fica na pasta de saída
            guardar_o_instalador(msi, saida_final, versao_do_pacote, destino)
        print(f"publicada a versão {versao_do_pacote} ({nupkg.name}, assinada)")
        return nupkg
    finally:
        destino.usar_rascunho(None, None)
        _fim(destino, etiqueta, saida_final, rascunho, msi_feito)


def guardar_o_instalador(msi: Path, saida_final: Path, versao_do_pacote: str, destino) -> Path:
    """Copia o .msi (ja publicado e lido de volta no destino) para a pasta de saida, pela copia conferida
    (empacotar.copiar_inteiro: nome provisorio, tamanho e soma lidos de volta, so entao o nome certo). Volta 3, achado
    2 do relatorio 2: o shutil.copyfile deixava um .msi pela metade com o nome certo, e a frase dizia que o que ficou
    pela metade tinha sido apagado. Falhou (disco cheio, Ctrl+C): o pedaco e apagado (conferido) e a frase diz a
    verdade: a versao FOI publicada e esta liberada; o instalador nao chegou a pasta de saida, mas esta inteiro na
    publicacao. Levanta Parou (ou repassa o Ctrl+C, depois de dizer a frase)."""
    import empacotar

    alvo = Path(saida_final) / msi.name
    frase = (f"a versão {versao_do_pacote} FOI publicada e está liberada em {destino.nome}; o instalador {msi.name} "
             f"NÃO chegou à pasta de saída ({Path(saida_final)}), mas está inteiro na publicação (lido de volta): "
             "baixe de lá")
    try:
        Path(saida_final).mkdir(parents=True, exist_ok=True)
        empacotar.copiar_inteiro(msi, alvo)
    except OSError as erro:
        raise Parou(f"{frase}. O que houve: {erro}") from erro
    except BaseException:
        print(f"  {frase}")
        raise
    print(f"  instalador: {alvo} (tamanho e soma conferidos)")
    return alvo


# ---------------------------------------------------------------------------------------------------------------------
# O motor do Kraken (publicacao propria, rara; D-768, D-788)
# ---------------------------------------------------------------------------------------------------------------------

def publicar_motor(destino_pasta: Path | None = None, motor_escolhido: Path | None = None,
                   arquivo_da_chave: Path | None = None, chave_publica: str | None = None,
                   rascunho_base: Path | None = None, destino=None) -> str:
    """Publica o motor do Kraken desta versao (core/ocr_kraken.VERSAO_DO_MOTOR), com etiqueta propria. Devolve a
    etiqueta. Levanta Parou. 'destino' (um Destino pronto) e so para os testes."""
    import empacotar
    from core import ocr_kraken

    chave = achar_chave(arquivo_da_chave, chave_publica)
    destino = destino or destino_de(destino_pasta)
    v = ocr_kraken.VERSAO_DO_MOTOR
    etiqueta, nome = versao.etiqueta_do_motor(v), versao.arquivo_do_motor(v)
    if destino.situacao(etiqueta) is not None:
        raise Parou(f"o motor {v} já existe em {destino.nome} (publicado ou rascunho que sobrou): se o motor mudou, "
                    f"aumente core/ocr_kraken.VERSAO_DO_MOTOR; rascunho velho: --apagar {etiqueta}")
    pasta, problemas = empacotar.achar_motor_kraken(motor_escolhido)
    if pasta is None:
        raise Parou("não achei um motor pronto do jeito novo: " + "; ".join(problemas))
    problemas = ocr_kraken.conferir_motor(pasta, v)
    if problemas:
        raise Parou(f"o motor de {pasta} não confere: " + "; ".join(problemas))
    print(f"  motor do Kraken {v}: {pasta} (conferido pela ficha)")
    rascunho = criar_rascunho(rascunho_base)
    destino.usar_rascunho(rascunho / "somar", empacotar.vigia_do_espaco(rascunho))     # achado 7 do relatorio 3
    try:
        # o zip (no maximo do tamanho da pasta) e, se a soma do destino puder baixar, uma copia dele para somar
        vezes = 2 if destino.soma_pode_baixar else 1
        precisa = vezes * empacotar.tamanho_da_pasta(pasta) + empacotar.MARGEM_DA_CONTA
        motivo = empacotar.conferir_espaco(rascunho, precisa)
        if motivo is not None:
            raise Parou(motivo)
        arquivo = rascunho / nome
        motivo = empacotar.zipar_motor(pasta, arquivo)
        if motivo is not None:
            raise Parou(motivo)
        assinado = assinar_arquivo(chave, arquivo, versao.ID_DO_PACOTE_DO_MOTOR, str(v), chave_publica)

        def conferir() -> None:
            """A assinatura lida do destino confere com a soma do arquivo lida do destino (ainda em rascunho)."""
            obter_motor_publicado(destino, rascunho / "lido-de-volta", chave_publica, v, exigir_liberado=False)

        publicar_arquivos(destino, etiqueta, f"Motor do Kraken {v}", _notas(f"Motor do Kraken {v} (raro)"),
                          [arquivo, assinado], conferir)
        print(f"publicado o motor do Kraken {v} ({nome}, assinado)")
        return etiqueta
    finally:
        destino.usar_rascunho(None, None)
        ficou = apagar_rascunho(rascunho)
        for frase in ficou:
            print(f"  ATENÇÃO: {frase}")
        print("\n  Conferência do fim:")
        print(f"    {_linha_do_rascunho(rascunho)}")


# ---------------------------------------------------------------------------------------------------------------------
# A linha de comando
# ---------------------------------------------------------------------------------------------------------------------

# A frase do fim quando o publicar para por erro do disco ou Ctrl+C: aponta para o que foi LIDO (a conferencia do fim
# e a frase do destino), nunca diz "foi apagado" por conta propria (achado 2 do relatorio 2).
_O_QUE_FICOU = ("O que ficou está nas linhas acima: a conferência do fim, lida do disco e do destino (se ela não "
                "aparece, o erro veio antes de o rascunho ser criado).")


def main(argumentos: list[str] | None = None) -> int:
    """A linha de comando (ver o cabecalho). 0 = feito; 1 = parou (a frase diz por que)."""
    analisador = argparse.ArgumentParser(description="Publica de propósito uma versão para o Kaique.")
    analisador.add_argument("--criar-chave", action="store_true", help="cria a chave privada (uma vez só)")
    analisador.add_argument("--pasta", type=Path, default=None,
                            help="publica numa pasta (a que o servidor das versões de prova serve), não no GitHub")
    analisador.add_argument("--pasta-pronta", type=Path, default=None,
                            help="usa uma pasta do programa já feita, desta versão (não roda o PyInstaller)")
    analisador.add_argument("--chave", type=Path, default=None, help="outro arquivo de chave privada")
    analisador.add_argument("--motor", action="store_true", help="publica o motor do Kraken (raro)")
    analisador.add_argument("--motor-kraken", type=Path, default=None, help="a pasta do motor a publicar")
    analisador.add_argument("--com-instalador", action="store_true",
                            help="faz também o instalador .msi (primeira entrega, ou quando o Samuel pedir)")
    analisador.add_argument("--reserva-gb", type=float, default=None,
                            help="só para a prova do aviso de pouco espaço: AUMENTA a reserva do C: (nunca abaixo de "
                                 "20 GB, D-776)")
    analisador.add_argument("--apagar", default=None, metavar="ETIQUETA",
                            help="apaga uma publicação do destino (ex.: v1.2.0; o fim de uma prova)")
    lido = analisador.parse_args(argumentos)
    import empacotar

    if lido.reserva_gb is not None:
        empacotar.RESERVA_DO_DISCO = max(empacotar.RESERVA_DO_DISCO, int(lido.reserva_gb * empacotar.GB))
    try:
        if lido.criar_chave:
            criar_chave(lido.chave)
            return 0
        if lido.apagar:
            destino = destino_de(lido.pasta)
            apagar_publicacao(destino, _conferir_etiqueta(lido.apagar))
            print(f"{lido.apagar}: não existe em {destino.nome} (conferido)")
            return 0
        if lido.motor:
            publicar_motor(lido.pasta, lido.motor_kraken, lido.chave)
            return 0
        publicar(versao.VERSAO, lido.pasta, lido.pasta_pronta, lido.chave, com_instalador=lido.com_instalador)
        return 0
    except Parou as erro:
        print(f"\nPAREI: {erro}")
        return 1
    except OSError as erro:
        # achado 5 de quem tentou quebrar: um erro do disco (pasta que não cria, arquivo preso pelo antivírus, cópia
        # que falha) saía como a tela de erro do Python. O finally de cada caminho já apagou o rascunho.
        # Volta 3, achado 2 do relatório 2: a frase dizia "o que esta vez fez pela metade foi apagado" sem conferir.
        # Quem diz o que ficou é a conferência do fim (impressa acima, lida do disco e do destino).
        onde = f" ({erro.filename})" if getattr(erro, "filename", None) else ""
        print(f"\nPAREI: o disco não deixou terminar{onde}: {erro.strerror or erro}. {_O_QUE_FICOU}")
        return 1
    except KeyboardInterrupt:
        print(f"\nPAREI: interrompido (Ctrl+C). {_O_QUE_FICOU}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
