"""A "internet" da prova à vista do atualizador novo: põe e tira versões do lugar de onde o programa instalado as lê.
NÃO é parte do programa do Kaique. Nada aqui pede licença ao Windows nem abre janela.

POR QUE EXISTE (achado da preparação, 25/11/2026). O programa instalado lê as versões de prova de uma PASTA (a linha
do `C:\\ProgramData\\EditorImpressao\\fonte-de-teste.txt`; `atualizacao.fonte_de_teste` só aceita uma pasta que existe,
e `atualizacao.Fonte.ler` lê a assinatura em `<pasta>\\<nome>`). O Velopack, com uma pasta, lê `<pasta>\\releases.win.json`
e copia `<pasta>\\<arquivo>` (`src/lib-rust/src/sources/file.rs`, 1.2.161: `read_to_string` e `std::fs::copy`). O
publicar, numa pasta, grava cada versão numa subpasta (`DestinoPasta`: `<pasta>\\v1.9.1\\`). Então a pasta que o
programa lê tem de ser uma pasta "plana", com o índice de todas as versões publicadas juntado. O índice juntado é o do
`servidor_das_versoes.Versoes.indice` (a regra única: a mais nova primeiro, sem repetir arquivo), não uma cópia dele.

AS TRÊS PASTAS (prova_comum.py)
    estoque   tudo o que foi montado (o destino do publicar)
    servida   o que está "publicado agora" (o mesmo desenho do DestinoPasta)
    fonte     o que o programa lê: o índice juntado das versões servidas e os arquivos delas, por ligação do disco
              (`os.link`: o mesmo arquivo com dois nomes, sem cópia nem espaço a mais; o mesmo disco C:)

COMANDOS (python fonte_da_prova.py <comando>)
    liberar 1.9.1     passa a versão do estoque para a servida (troca de nome no mesmo disco) e refaz a fonte
    tirar 1.9.1       o contrário
    sem-resposta      a fonte deixa de responder (o índice ganha outro nome): procurar dá erro, como sem internet
    com-resposta      volta o índice
    estado            mostra o que está em cada pasta e o que o índice da fonte oferece
    conferir          confere a fonte arquivo por arquivo contra a servida (o tamanho, e que é o MESMO arquivo)

Cada comando, no fim, lê de novo o que ficou e imprime (§11.12 ponto 2: nada dá como feito o que não conferiu).

Seguro mexer: os textos. Arriscado: COPIAR os pacotes para a fonte em vez de ligar (mais 460 MB por versão no C:);
juntar o índice por outra conta que não a do servidor_das_versoes (seriam duas regras).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import prova_comum as comum  # noqa: E402

sys.path.insert(0, str(comum.RAMO))
import publicar_versao_kaique as pub  # noqa: E402
import servidor_das_versoes as srv  # noqa: E402

INDICE = srv.NOME_DO_INDICE
SEM_RESPOSTA = INDICE + ".sem-resposta"


def _versoes(pasta: Path) -> list[Path]:
    """As publicações de versão do programa (as `v...`) liberadas numa pasta, pela regra do publicar."""
    return [p for p in pub.DestinoPasta(pasta).liberadas() if p.name.startswith("v")]


def _mesmo_arquivo(a: Path, b: Path) -> bool:
    """Os dois nomes são o mesmo arquivo no disco (a ligação)?"""
    try:
        return os.path.samefile(a, b)
    except OSError:
        return False


def refazer_a_fonte() -> None:
    """A fonte = os arquivos das versões servidas (ligados) + o índice juntado. Tira o que não está mais servido. O
    índice é gravado por último, por inteiro (nome provisório e troca), para o programa nunca ler um índice que aponta
    para arquivo que ainda não está lá."""
    fonte = comum.FONTE
    fonte.mkdir(parents=True, exist_ok=True)
    queridos: dict[str, Path] = {}
    for publicacao in _versoes(comum.SERVIDA):
        for arquivo in publicacao.iterdir():
            if arquivo.is_file() and arquivo.name != INDICE:
                queridos[arquivo.name] = arquivo
    for nome, origem in queridos.items():
        alvo = fonte / nome
        if alvo.exists() and _mesmo_arquivo(alvo, origem):
            continue
        if alvo.exists():
            alvo.unlink()
        os.link(origem, alvo)
    indice_novo = srv.Versoes(comum.SERVIDA).indice()
    provisorio = fonte / (INDICE + ".gravando")
    provisorio.write_bytes(indice_novo)
    destino = fonte / (SEM_RESPOSTA if (fonte / SEM_RESPOSTA).exists() else INDICE)
    os.replace(provisorio, destino)
    for arquivo in fonte.iterdir():
        if arquivo.name in (INDICE, SEM_RESPOSTA) or arquivo.name in queridos:
            continue
        arquivo.unlink()


def mover(v: str, de: Path, para: Path) -> None:
    """Passa a publicação v<v> de uma pasta para a outra (troca de nome, no mesmo disco)."""
    etiqueta = f"v{v}"
    origem, alvo = de / etiqueta, para / etiqueta
    if not origem.is_dir():
        raise SystemExit(f"PAREI: {origem} não existe")
    if alvo.exists():
        raise SystemExit(f"PAREI: {alvo} já existe")
    para.mkdir(parents=True, exist_ok=True)
    os.rename(origem, alvo)


def oferecidas() -> list[str]:
    """As versões que o índice da fonte oferece agora (lido do disco), ou o motivo de não responder."""
    indice = comum.FONTE / INDICE
    if not indice.is_file():
        return ["(a fonte não responde: não há índice)"]
    lido = json.loads(indice.read_text(encoding="utf-8-sig"))
    return [f"{a.get('Version')} ({a.get('FileName')}, {int(a.get('Size', 0)) // 2**20} MB)" for a in lido["Assets"]]


def estado() -> None:
    """O que está em cada pasta, lido agora."""
    print(f"estoque: {', '.join(p.name for p in _versoes(comum.ESTOQUE)) or '(nada)'}")
    print(f"servida: {', '.join(p.name for p in _versoes(comum.SERVIDA)) or '(nada)'}")
    print("a fonte oferece (a mais nova primeiro): " + "; ".join(oferecidas()))


def conferir() -> int:
    """Cada arquivo que o índice da fonte cita está na fonte, com o tamanho do índice, e é o mesmo arquivo da servida.
    0 = tudo certo."""
    erros = []
    indice = comum.FONTE / INDICE
    if indice.is_file():
        for item in json.loads(indice.read_text(encoding="utf-8-sig"))["Assets"]:
            nome = item["FileName"]
            arquivo = comum.FONTE / nome
            if not arquivo.is_file():
                erros.append(f"falta {nome}")
            elif arquivo.stat().st_size != int(item["Size"]):
                erros.append(f"{nome}: tamanho {arquivo.stat().st_size}, o índice diz {item['Size']}")
    for publicacao in _versoes(comum.SERVIDA):
        for arquivo in publicacao.iterdir():
            if arquivo.is_file() and arquivo.name != INDICE and not _mesmo_arquivo(arquivo, comum.FONTE / arquivo.name):
                erros.append(f"{arquivo.name} da servida não é o mesmo da fonte")
    print("conferido: tudo certo" if not erros else "PROBLEMAS: " + "; ".join(erros))
    return 0 if not erros else 1


def main(argumentos: list[str]) -> int:
    """A linha de comando (ver o topo)."""
    if not argumentos:
        print(__doc__)
        return 1
    comando = argumentos[0]
    if comando == "liberar" and len(argumentos) == 2:
        mover(argumentos[1], comum.ESTOQUE, comum.SERVIDA)
        refazer_a_fonte()
    elif comando == "tirar" and len(argumentos) == 2:
        mover(argumentos[1], comum.SERVIDA, comum.ESTOQUE)
        refazer_a_fonte()
    elif comando == "refazer":
        refazer_a_fonte()
    elif comando == "sem-resposta":
        if (comum.FONTE / INDICE).exists():
            os.replace(comum.FONTE / INDICE, comum.FONTE / SEM_RESPOSTA)
    elif comando == "com-resposta":
        if (comum.FONTE / SEM_RESPOSTA).exists():
            os.replace(comum.FONTE / SEM_RESPOSTA, comum.FONTE / INDICE)
    elif comando == "conferir":
        return conferir()
    elif comando != "estado":
        print(__doc__)
        return 1
    estado()
    return conferir() if comando in ("liberar", "tirar", "refazer") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
