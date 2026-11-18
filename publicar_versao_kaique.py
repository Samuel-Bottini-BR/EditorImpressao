"""Publica, DE PROPOSITO, uma "versao para o Kaique" (decisao D-714).

    .venv\\Scripts\\python.exe publicar_versao_kaique.py --criar-chave       (uma vez so)
    .venv\\Scripts\\python.exe publicar_versao_kaique.py                     (GitHub)
    .venv\\Scripts\\python.exe publicar_versao_kaique.py --pasta <servidor>  (pasta: ensaio)

O que faz, em ordem, parando no primeiro problema (nada sai pela metade):
1. acha a chave privada (fora do repositorio; assinatura.caminho_da_chave) e
   confere que ela e a mesma cuja parte publica vai dentro do programa
   (assinatura.CHAVE_PUBLICA_DO_SAMUEL). Sem a chave, PARA antes de tudo;
2. recusa se a versao do versao.py ja foi publicada (e preciso aumentar o numero);
3. baixa a ultima versao publicada (vpk download), para o Velopack montar o
   pacote "so o que mudou";
4. empacota (empacotar.construir_pacote_do_velopack: a pasta com todas as
   travas, o Visual C++ dentro, o vpk pack e a conferencia do pacote). Com
   --pasta-pronta, usa uma pasta ja feita (o ensaio usa isto);
5. assina o pacote inteiro (arquivo <versao.ID_DO_PACOTE>-<versao>.assinatura) e
   confere a propria assinatura com a chave publica do programa;
6. publica: no GitHub (vpk upload github --publish, etiqueta v<versao>, mais o
   arquivo da assinatura com o gh), ou na pasta do ensaio (vpk upload local).

Nunca roda sozinho e nunca a cada salvamento no GitHub: so quando alguem
roda este comando (D-714). O token do GitHub e pedido na hora ao gh (gh auth
token), so no PC do Samuel; nunca vai para dentro do programa (D-719) nem
para arquivo nenhum.

Arriscado mudar: a etiqueta v<versao> (o programa procura a assinatura em
releases/download/v<versao>/, atualizacao.Fonte); o nome do arquivo da
assinatura (assinatura.nome_do_arquivo_da_assinatura).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import assinatura
import atualizacao
import versao

RAIZ = Path(__file__).resolve().parent
# Pasta de trabalho do publicar (rascunho; refeita a cada vez).
PASTA_DE_TRABALHO = RAIZ / "build" / "publicar"


class Parou(Exception):
    """Um problema que impede publicar; a mensagem diz o que fazer."""


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


def assinar_pacote(chave: bytes, nupkg: Path, versao_do_pacote: str, chave_publica: str | None = None) -> Path:
    """Escreve <pacote>-<versao>.assinatura ao lado do .nupkg e confere a propria assinatura."""
    v = assinatura.VersaoAssinada(versao.ID_DO_PACOTE, versao_do_pacote, Path(nupkg).name,
                                  assinatura.soma_sha256(nupkg))
    texto = assinatura.escrever_assinatura(chave, v)
    motivo = assinatura.conferir_versao(texto, v, chave_publica)
    if motivo is not None:
        raise Parou(f"a assinatura feita agora não confere: {motivo}")
    arquivo = Path(nupkg).parent / assinatura.nome_do_arquivo_da_assinatura(versao.ID_DO_PACOTE, versao_do_pacote)
    arquivo.write_text(texto, encoding="utf-8")
    return arquivo


def _rodar(comando: list[str]) -> None:
    feito = subprocess.run(comando)
    if feito.returncode != 0:
        raise Parou(f"o comando falhou (código {feito.returncode}): {' '.join(comando[:3])} ...")


def _token_do_github() -> str:
    """O token, pedido na hora ao gh do PC do Samuel (nunca gravado)."""
    gh = shutil.which("gh") or "C:\\Program Files\\GitHub CLI\\gh.exe"
    feito = subprocess.run([gh, "auth", "token"], capture_output=True, text=True)
    if feito.returncode != 0 or not feito.stdout.strip():
        raise Parou("o gh não está com a conta do GitHub (rode: gh auth login)")
    return feito.stdout.strip()


def ja_publicada(destino_pasta: Path | None, versao_do_pacote: str) -> bool:
    """A versao ja existe no destino (pasta: o arquivo; GitHub: a etiqueta)?"""
    if destino_pasta is not None:
        return (Path(destino_pasta) / f"{versao.ID_DO_PACOTE}-{versao_do_pacote}-full.nupkg").exists()
    gh = shutil.which("gh") or "C:\\Program Files\\GitHub CLI\\gh.exe"
    feito = subprocess.run([gh, "release", "view", f"v{versao_do_pacote}", "-R", _repo()],
                           capture_output=True, text=True)
    return feito.returncode == 0


def _repo() -> str:
    return atualizacao.REPOSITORIO.removeprefix("https://github.com/")


def publicar(versao_do_pacote: str, destino_pasta: Path | None = None, pasta_pronta: Path | None = None,
             arquivo_da_chave: Path | None = None, chave_publica: str | None = None,
             vpk: Path | None = None) -> Path:
    """O caminho inteiro (ver o cabecalho). Devolve o .nupkg publicado. Levanta Parou."""
    import empacotar

    chave = achar_chave(arquivo_da_chave, chave_publica)
    versao.numeros(versao_do_pacote)
    if ja_publicada(destino_pasta, versao_do_pacote):
        raise Parou(f"a versão {versao_do_pacote} já foi publicada: aumente o número em versao.py")
    vpk = vpk or empacotar.achar_vpk()
    if vpk is None:
        raise Parou(f"não achei o vpk ({empacotar.COMO_INSTALAR_O_VPK})")
    saida = PASTA_DE_TRABALHO / versao_do_pacote
    shutil.rmtree(saida, ignore_errors=True)
    saida.mkdir(parents=True)
    # 3. a ultima publicada, para o pacote "so o que mudou"
    if destino_pasta is not None:
        if any(Path(destino_pasta).glob("*.nupkg")):
            _rodar([str(vpk), "download", "local", "--path", str(destino_pasta), "--outputDir", str(saida)])
    else:
        _rodar([str(vpk), "download", "github", "--repoUrl", atualizacao.REPOSITORIO, "--outputDir", str(saida)])
    # 4. empacotar
    if pasta_pronta is not None:
        _rodar(empacotar.comando_do_vpk(vpk, Path(pasta_pronta), saida, versao_do_pacote))
        nupkg = empacotar.nupkg_inteiro(saida, versao_do_pacote)
        faltando = empacotar.conferir_pacote_do_velopack(nupkg, None)
        if faltando:
            raise Parou("o pacote saiu sem: " + ", ".join(faltando))
    else:
        nupkg = empacotar.construir_pacote_do_velopack(saida, versao_do_pacote)
        if nupkg is None:
            raise Parou("o empacotamento parou (o motivo está acima)")
    # 5. assinar
    arquivo_assinado = assinar_pacote(chave, nupkg, versao_do_pacote, chave_publica)
    # 6. publicar
    if destino_pasta is not None:
        Path(destino_pasta).mkdir(parents=True, exist_ok=True)
        _rodar([str(vpk), "upload", "local", "--path", str(destino_pasta), "--outputDir", str(saida)])
        shutil.copy2(arquivo_assinado, Path(destino_pasta) / arquivo_assinado.name)
    else:
        token = _token_do_github()
        _rodar([str(vpk), "upload", "github", "--repoUrl", atualizacao.REPOSITORIO, "--token", token,
                "--outputDir", str(saida), "--publish", "--tag", f"v{versao_do_pacote}",
                "--releaseName", f"Versão para o Kaique {versao_do_pacote}"])
        gh = shutil.which("gh") or "C:\\Program Files\\GitHub CLI\\gh.exe"
        _rodar([gh, "release", "upload", f"v{versao_do_pacote}", str(arquivo_assinado), "-R", _repo()])
    print(f"publicada a versão {versao_do_pacote} ({nupkg.name}, assinada)")
    return nupkg


def main(argumentos: list[str] | None = None) -> int:
    analisador = argparse.ArgumentParser(description="Publica de propósito uma versão para o Kaique.")
    analisador.add_argument("--criar-chave", action="store_true", help="cria a chave privada (uma vez só)")
    analisador.add_argument("--pasta", type=Path, default=None,
                            help="publica numa pasta (servidor de mentira do ensaio), não no GitHub")
    analisador.add_argument("--pasta-pronta", type=Path, default=None,
                            help="usa uma pasta do programa já feita (não roda o empacotar)")
    analisador.add_argument("--chave", type=Path, default=None, help="outro arquivo de chave privada")
    lido = analisador.parse_args(argumentos)
    try:
        if lido.criar_chave:
            criar_chave(lido.chave)
            return 0
        publicar(versao.VERSAO, lido.pasta, lido.pasta_pronta, lido.chave)
        return 0
    except Parou as erro:
        print(f"\nPAREI: {erro}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
