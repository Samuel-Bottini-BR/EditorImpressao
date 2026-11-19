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
   (empacotar.INSTALADOR): o .msi vai para a pasta de saida (PASTA_DE_SAIDA); o pacote dele NAO e publicado (o
   publicado e sempre o da atualizacao, sem o motor);
6. assina o pacote inteiro e confere a propria assinatura;
7. publica num destino (Destino): sobe como RASCUNHO so os arquivos da versao (arquivos_da_versao: o pacote, o indice
   releases.win.json e a assinatura; nunca o Setup.exe), le de volta (a lista do que esta la, a soma de cada
   arquivo, a assinatura lida do destino conferida contra a soma do pacote lida do destino, o indice apontando para
   essa soma, e o motor de novo) e SO ENTAO libera. Qualquer falha antes de liberar apaga o rascunho do destino;
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
# A subpasta de rascunho no DestinoPasta (o servidor_das_versoes.py nao serve o que comeca com isto).
NOME_DO_RASCUNHO_NO_DESTINO = ".rascunho-"
# As etiquetas aceitas (a de uma versao do programa e a do motor): nada de barra, ponto-ponto ou espaco.
ETIQUETA_ACEITA = re.compile(r"^(v\d+\.\d+\.\d+|motor-kraken-\d+)$")
LUGAR_DO_GH = Path(r"C:\Program Files\GitHub CLI\gh.exe")


class Parou(Exception):
    """Um problema que impede publicar; a mensagem diz o que fazer."""


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
        if _e_rascunho_nosso(velho):
            for frase in apagar_rascunho(velho):
                print(f"  ATENÇÃO: {frase}")
    pasta = base / f"{PREFIXO_DO_RASCUNHO}{datetime.now():%Y%m%d-%H%M%S}-{secrets.token_hex(3)}"
    pasta.mkdir()
    return pasta


# ---------------------------------------------------------------------------------------------------------------------
# Os destinos (o lugar unico de "publicar num lugar")
# ---------------------------------------------------------------------------------------------------------------------

def _conferir_etiqueta(etiqueta: str) -> str:
    """A etiqueta e uma das nossas (v1.2.0 ou motor-kraken-1)? Levanta Parou."""
    if not ETIQUETA_ACEITA.match(etiqueta or ""):
        raise Parou(f"etiqueta fora do formato: {etiqueta!r}")
    return etiqueta


class DestinoPasta:
    """Uma pasta que faz o papel do GitHub (as provas, D-773). Publicacao liberada: <raiz>\\<etiqueta>\\; rascunho:
    <raiz>\\.rascunho-<etiqueta>\\ (o servidor_das_versoes.py nao serve). Todas as funcoes levantam Parou."""

    def __init__(self, raiz: Path | str):
        """raiz: a pasta (criada quando precisa)."""
        self.raiz = Path(raiz)

    @property
    def nome(self) -> str:
        """Como o destino aparece nas frases."""
        return f"a pasta {self.raiz}"

    def _liberada(self, etiqueta: str) -> Path:
        return self.raiz / _conferir_etiqueta(etiqueta)

    def _rascunho(self, etiqueta: str) -> Path:
        return self.raiz / (NOME_DO_RASCUNHO_NO_DESTINO + _conferir_etiqueta(etiqueta))

    def _onde(self, etiqueta: str) -> Path:
        for pasta in (self._liberada(etiqueta), self._rascunho(etiqueta)):
            if pasta.is_dir():
                return pasta
        raise Parou(f"não há publicação {etiqueta} em {self.nome}")

    def situacao(self, etiqueta: str) -> str | None:
        """None (nao existe), "liberada" ou "rascunho"."""
        if self._liberada(etiqueta).is_dir():
            return "liberada"
        return "rascunho" if self._rascunho(etiqueta).is_dir() else None

    def criar_rascunho(self, etiqueta: str, titulo: str, notas: str) -> None:
        """Cria o rascunho vazio (com as notas num arquivo de texto que nao e publicado como versao)."""
        try:
            self.raiz.mkdir(parents=True, exist_ok=True)
            self._rascunho(etiqueta).mkdir()
        except OSError as erro:
            raise Parou(f"não consegui criar o rascunho {etiqueta} em {self.nome} ({erro})") from erro

    def enviar(self, etiqueta: str, arquivo: Path) -> None:
        """Copia um arquivo para o rascunho (num nome provisorio, trocado de uma vez)."""
        alvo = self._rascunho(etiqueta) / Path(arquivo).name
        provisorio = alvo.with_name(alvo.name + ".enviando")
        try:
            shutil.copyfile(arquivo, provisorio)
            os.replace(provisorio, alvo)
        except OSError as erro:
            provisorio.unlink(missing_ok=True)
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
        """Copia um arquivo da publicacao para pasta_local (a leitura de volta)."""
        origem = self._onde(etiqueta) / nome
        Path(pasta_local).mkdir(parents=True, exist_ok=True)
        try:
            return Path(shutil.copyfile(origem, Path(pasta_local) / nome))
        except OSError as erro:
            raise Parou(f"não consegui ler {nome} de {self.nome} ({erro})") from erro

    def liberar(self, etiqueta: str) -> None:
        """Tira do rascunho (troca o nome da subpasta de uma vez)."""
        try:
            os.rename(self._rascunho(etiqueta), self._liberada(etiqueta))
        except OSError as erro:
            raise Parou(f"não consegui liberar {etiqueta} em {self.nome} ({erro})") from erro

    def apagar(self, etiqueta: str) -> None:
        """Apaga a publicacao (rascunho ou liberada), so a subpasta dela."""
        for pasta in (self._rascunho(etiqueta), self._liberada(etiqueta)):
            if pasta.is_dir() and not pasta.is_symlink():
                shutil.rmtree(pasta, ignore_errors=True)


def _caminho_do_gh() -> str:
    """O gh do PC do Samuel (no PATH, ou onde o instalador do GitHub CLI o poe)."""
    return shutil.which("gh") or str(LUGAR_DO_GH)


class DestinoGitHub:
    """O GitHub do projeto, pela ferramenta gh (o lugar unico da conversa do publicar com o GitHub: _gh). Lido do gh
    2.99 (cli/cli, pkg/cmd/release/shared/fetch.go): "release view/upload/download/edit/delete <etiqueta>" acham
    tambem o rascunho pela etiqueta; sem publicacao, "release not found". Todas as funcoes levantam Parou."""

    def __init__(self, repositorio: str | None = None, gh: str | None = None):
        """repositorio: 'dono/nome' (de fabrica, o de atualizacao.REPOSITORIO)."""
        self.repositorio = repositorio or atualizacao.REPOSITORIO.removeprefix("https://github.com/")
        self.gh = gh

    @property
    def nome(self) -> str:
        """Como o destino aparece nas frases."""
        return f"o GitHub ({self.repositorio})"

    def _gh(self, *argumentos: str, limite_s: float = 600) -> subprocess.CompletedProcess:
        """Roda o gh e devolve o resultado (o que falhar ao abrir vira Parou; o codigo de saida quem decide e quem
        chama)."""
        try:
            return subprocess.run([self.gh or _caminho_do_gh(), *argumentos, "-R", self.repositorio],
                                  capture_output=True, text=True, encoding="utf-8", errors="replace",
                                  timeout=limite_s)
        except (OSError, subprocess.TimeoutExpired) as erro:
            raise Parou(f"não consegui falar com o GitHub pelo gh ({erro})") from erro

    def _exigir(self, r: subprocess.CompletedProcess, o_que: str) -> subprocess.CompletedProcess:
        if r.returncode != 0:
            raise Parou(f"o GitHub não deixou {o_que}: {(r.stderr or r.stdout).strip()[:300]}")
        return r

    def _ver(self, etiqueta: str, campos: str) -> dict | None:
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
        lido = self._ver(etiqueta, "assets")
        if lido is None:
            raise Parou(f"não há publicação {etiqueta} em {self.nome}")
        return list(lido.get("assets") or [])

    def arquivos(self, etiqueta: str) -> dict[str, int]:
        """O que esta na publicacao: {nome: tamanho}, lido do GitHub."""
        return {a["name"]: int(a.get("size") or 0) for a in self._assets(etiqueta)}

    def soma(self, etiqueta: str, nome: str) -> str:
        """A soma SHA-256 do arquivo como ele esta no GitHub: a que o GitHub calcula ('digest', "sha256:..."); sem
        ela, baixa o arquivo e soma (a leitura de volta nunca e dada como feita sem ler)."""
        for a in self._assets(etiqueta):
            if a.get("name") == nome:
                digest = str(a.get("digest") or "")
                if digest.startswith("sha256:"):
                    return digest.removeprefix("sha256:").lower()
                pasta = Path(os.environ.get("TEMP", ".")) / f"publicar-soma-{secrets.token_hex(3)}"
                try:
                    return assinatura.soma_sha256(self.baixar(etiqueta, nome, pasta))
                finally:
                    shutil.rmtree(pasta, ignore_errors=True)
        raise Parou(f"{nome} não está na publicação {etiqueta} em {self.nome}")

    def baixar(self, etiqueta: str, nome: str, pasta_local: Path) -> Path:
        """Baixa um arquivo da publicacao para pasta_local (a leitura de volta)."""
        Path(pasta_local).mkdir(parents=True, exist_ok=True)
        self._exigir(self._gh("release", "download", _conferir_etiqueta(etiqueta), "--pattern", nome,
                              "--dir", str(pasta_local), "--clobber", limite_s=3 * 3600), f"baixar {nome}")
        baixado = Path(pasta_local) / nome
        if not baixado.is_file():
            raise Parou(f"o GitHub não entregou {nome} da publicação {etiqueta}")
        return baixado

    def liberar(self, etiqueta: str) -> None:
        """Tira do rascunho."""
        self._exigir(self._gh("release", "edit", _conferir_etiqueta(etiqueta), "--draft=false"),
                     f"liberar {etiqueta}")

    def apagar(self, etiqueta: str) -> None:
        """Apaga a publicacao e a etiqueta."""
        self._exigir(self._gh("release", "delete", _conferir_etiqueta(etiqueta), "--yes", "--cleanup-tag"),
                     f"apagar {etiqueta}")


def destino_de(destino_pasta: Path | None) -> DestinoPasta | DestinoGitHub:
    """O destino pedido na linha de comando: a pasta (--pasta) ou o GitHub."""
    return DestinoPasta(destino_pasta) if destino_pasta is not None else DestinoGitHub()


def apagar_publicacao(destino, etiqueta: str) -> None:
    """Apaga uma publicacao do destino e CONFERE que sumiu (levanta Parou se ficou)."""
    if destino.situacao(etiqueta) is None:
        return
    destino.apagar(etiqueta)
    if destino.situacao(etiqueta) is not None:
        raise Parou(f"pedi para apagar {etiqueta} em {destino.nome}, e ela continua lá")


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
    Qualquer falha (ou Ctrl+C) antes de terminar apaga a publicacao do destino e confere que sumiu; se nao der para
    apagar, a frase diz o que ficou e como apagar."""
    situacao = destino.situacao(etiqueta)
    if situacao == "liberada":
        raise Parou(f"{etiqueta} já está publicada em {destino.nome}: aumente o número (versao.py ou "
                    "core/ocr_kraken.VERSAO_DO_MOTOR)")
    if situacao == "rascunho":
        raise Parou(f"sobrou um rascunho de {etiqueta} em {destino.nome} (de uma vez interrompida): apague com "
                    f"--apagar {etiqueta} e rode de novo")
    nomes = [Path(a).name for a in arquivos]
    print(f"  {destino.nome}: rascunho {etiqueta} ({', '.join(nomes)})")
    destino.criar_rascunho(etiqueta, titulo, notas)
    try:
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
        destino.liberar(etiqueta)
        if destino.situacao(etiqueta) != "liberada":
            raise Parou(f"pedi para liberar {etiqueta} em {destino.nome}, e ela não ficou liberada")
    except BaseException as erro:
        try:
            apagar_publicacao(destino, etiqueta)
            desfeito = f"a publicação {etiqueta} foi apagada de {destino.nome} (conferido)"
        except Parou as outro:
            desfeito = f"ATENÇÃO: {outro}; apague com --apagar {etiqueta}"
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


def arquivos_da_versao(saida_do_vpk: Path, versao_do_pacote: str, arquivo_da_assinatura: Path) -> list[Path]:
    """O que vai ao destino numa versao do programa (o LUGAR UNICO): o pacote inteiro, o indice que o programa do
    Kaique le (releases.win.json, gravado pelo vpk so com esta versao) e a assinatura. Nunca o Setup.exe (D-795),
    nunca o .msi, nunca o assets.win.json nem o RELEASES antigo."""
    import empacotar

    return [empacotar.nupkg_inteiro(saida_do_vpk, versao_do_pacote), Path(saida_do_vpk) / empacotar.NOME_DO_INDICE,
            Path(arquivo_da_assinatura)]


def _conferir_versao_lida(destino, etiqueta: str, versao_do_pacote: str, nupkg: Path, motor,
                          pasta_lida: Path, chave_publica: str | None) -> Callable[[], None]:
    """A leitura de volta de uma versao do programa (para publicar_arquivos): a assinatura lida do destino confere
    com a soma do pacote lida do destino; o indice lido do destino aponta para esse pacote com essa soma; e o motor
    que ela pede continua publicado e e o mesmo do motor-exigido.json."""
    import empacotar

    def conferir() -> None:
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


def conferencia_do_fim(destino, etiqueta: str, pasta_de_saida: Path, rascunho: Path | None) -> list[str]:
    """O que o publicar mostra no fim, sempre (D-795, D-776): o rascunho sumiu?, o que ficou na pasta de saida e no
    destino, e se o Setup.exe esta em algum deles. Lido, nunca suposto."""
    import empacotar

    setup = empacotar.nome_do_setup()
    linhas = []
    if rascunho is not None:
        linhas.append(f"rascunho do disco de dentro: {'ainda existe: ' + str(rascunho) if rascunho.exists() else 'apagado (conferido)'}")
    saida = Path(pasta_de_saida)
    no_saida = sorted(f.name for f in saida.iterdir()) if saida.is_dir() else []
    linhas.append(f"pasta de saída ({saida}): {', '.join(no_saida) or 'vazia'}")
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


def _fim(destino, etiqueta: str, pasta_de_saida: Path, rascunho: Path) -> list[str]:
    """Apaga o rascunho (conferido) e imprime a conferencia do fim. Devolve o que nao saiu do rascunho."""
    ficou = apagar_rascunho(rascunho)
    for frase in ficou:
        print(f"  ATENÇÃO: {frase}")
    print("\n  Conferência do fim:")
    for linha in conferencia_do_fim(destino, etiqueta, pasta_de_saida, rascunho):
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
        precisa = empacotar.espaco_que_vai_usar(empacotar.tamanho_da_pasta(pasta), saidas, tamanho_do_motor)
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
            arquivo_do_motor = destino.baixar(motor.etiqueta, motor.arquivo, rascunho / "motor")
            outro = empacotar.construir_pacote_do_velopack(rascunho / "instalador", versao_do_pacote,
                                                           empacotar.INSTALADOR, pasta, motor, arquivo_do_motor,
                                                           rascunho=rascunho, vpk=vpk, pecas=pecas)
            problemas = empacotar.preparar_saida(pasta, empacotar.ATUALIZACAO, None, motor)  # tira o motor da pasta
            if outro is None or problemas:
                raise Parou("o empacotamento do instalador parou (o motivo está acima) " + "; ".join(problemas))
            saida_final.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(rascunho / "instalador" / empacotar.nome_do_msi(), saida_final / empacotar.nome_do_msi())
            print(f"  instalador: {saida_final / empacotar.nome_do_msi()}")
        arquivo_assinado = assinar_pacote(chave, nupkg, versao_do_pacote, chave_publica)
        arquivos = arquivos_da_versao(nupkg.parent, versao_do_pacote, arquivo_assinado)
        publicar_arquivos(destino, etiqueta, f"Versão para o Kaique {versao_do_pacote}",
                          _notas(f"Versão {versao_do_pacote} do Editor de Impressão (pede o motor do Kraken "
                                 f"{motor.versao})"), arquivos,
                          _conferir_versao_lida(destino, etiqueta, versao_do_pacote, nupkg, motor,
                                                rascunho / "lido-de-volta", chave_publica))
        print(f"publicada a versão {versao_do_pacote} ({nupkg.name}, assinada)")
        return nupkg
    finally:
        _fim(destino, etiqueta, saida_final, rascunho)


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
    try:
        precisa = empacotar.tamanho_da_pasta(pasta) + empacotar.MARGEM_DA_CONTA
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
        ficou = apagar_rascunho(rascunho)
        for frase in ficou:
            print(f"  ATENÇÃO: {frase}")


# ---------------------------------------------------------------------------------------------------------------------
# A linha de comando
# ---------------------------------------------------------------------------------------------------------------------

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
    analisador.add_argument("--apagar", default=None, metavar="ETIQUETA",
                            help="apaga uma publicação do destino (ex.: v1.2.0; o fim de uma prova)")
    lido = analisador.parse_args(argumentos)
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


if __name__ == "__main__":
    sys.exit(main())
