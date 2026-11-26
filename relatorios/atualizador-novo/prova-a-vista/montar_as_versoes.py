"""Monta as versões de prova da prova à vista do atualizador novo (25/11/2026). NÃO é parte do programa do Kaique.

O QUE FAZ
    Publica, pelo publicar de verdade (`publicar_versao_kaique.py --pasta`, o DestinoPasta: nunca o GitHub), as versões
    que a prova à vista usa, todas do MESMO commit do ramo `atualizador-novo-2026-11-23` (8e09e193), montadas numa cópia
    de trabalho só para isso (`.claude\\worktrees\\prova-a-vista-montagem`, destacada nesse commit, com uma CÓPIA da pasta
    `modelos\\`, sem junção). Muda, nessa cópia, só o número em `versao.py` (e, na 1.9.3, tira um arquivo: ver abaixo), e
    devolve os arquivos ao commit depois de cada versão (`git checkout`), conferindo que a cópia ficou limpa.

    Ordem: o motor do Kraken (a publicação dele, que toda versão exige no destino), depois as versões:
      1.9.0  com o instalador (.msi): a primeira instalada
      1.9.1  normal ("Reiniciar agora")
      1.9.2  normal ("Depois", "Não", "Sim" ao fechar)
      1.9.3  QUEBRADA DE PROPÓSITO: montada sem o arquivo ui\\tela_final.py (a janela principal não abre; o teste
             rápido acusa "erro ao abrir"). O publicar aceita: o que ele confere é o que vai no pacote (modelos, DLLs,
             Tesseract, Visual C++), não o código Python
      1.9.4  a correção (normal)
      1.9.5  normal, e depois a ASSINATURA TROCADA por uma feita com outra chave (a do Samuel fica guardada fora da
             pasta servida): o programa tem de recusá-la (frase 2 da D-778)
      1.9.6  normal (os passos do motor, do "sem resposta da fonte", do atualizador posto de lado, do arquivo preso e
             do clique no atalho durante a troca)

    Retomável: versão já liberada no estoque é pulada. Cada versão tem o seu registro em `<base>\\registros\\`.

    Antes e depois de cada publicar, confere que a pasta dos projetos do Samuel (`%LOCALAPPDATA%\\EditorImpressao`) não
    mudou (nomes, tamanhos e datas lidos de novo); se mudou, PARA.

COMO RODAR (do ramo atualizador-novo; nada pede licença; nenhuma janela)
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\atualizador-novo\\prova-a-vista\\montar_as_versoes.py

Seguro mexer: a lista VERSOES (acrescentar uma no fim). Arriscado: mudar o BASE (o roteiro e os outros scripts da prova
leem o mesmo lugar, em `prova_comum.py`); montar na cópia do ramo (o versao.py dele mudaria).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import prova_comum as comum  # noqa: E402

PYTHON = Path(r"D:\programas\EditorImpressao\.venv\Scripts\python.exe")

# (versão, com instalador?, o que se faz de diferente)
VERSOES = [
    ("1.9.0", True, None),
    ("1.9.1", False, None),
    ("1.9.2", False, None),
    ("1.9.3", False, "sem_tela_final"),
    ("1.9.4", False, None),
    ("1.9.5", False, "assinatura_falsa"),
    ("1.9.6", False, None),
]
ARQUIVO_TIRADO_NA_QUEBRADA = Path("ui") / "tela_final.py"


def foto_dos_projetos() -> list[tuple[str, int, float]]:
    """Os arquivos da pasta dos projetos do Samuel (só leitura): caminho, tamanho e data."""
    pasta = Path(os.environ["LOCALAPPDATA"]) / "EditorImpressao"
    saida = []
    for raiz, _pastas, arquivos in os.walk(pasta):
        for nome in arquivos:
            p = Path(raiz) / nome
            try:
                s = p.stat()
                saida.append((str(p), s.st_size, s.st_mtime))
            except OSError:
                saida.append((str(p), -1, -1))
    return sorted(saida)


def git(*argumentos: str) -> str:
    """Um comando do git na cópia de montagem (nunca na do ramo)."""
    r = subprocess.run(["git", "-C", str(comum.MONTAGEM), *argumentos], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"PAREI: git {' '.join(argumentos)}: {r.stderr.strip()}")
    return r.stdout


def cópia_limpa() -> None:
    """Devolve a cópia de montagem ao commit e confere (nada mudado no que o git acompanha)."""
    git("checkout", "--", "versao.py", ARQUIVO_TIRADO_NA_QUEBRADA.as_posix())
    sujo = git("status", "--porcelain", "--untracked-files=no").strip()
    if sujo:
        raise SystemExit(f"PAREI: a cópia de montagem não voltou ao commit:\n{sujo}")
    if git("rev-parse", "HEAD").strip() != comum.COMMIT:
        raise SystemExit("PAREI: a cópia de montagem não está no commit da prova")


def pôr_o_numero(v: str) -> None:
    """Troca SÓ a linha `VERSAO = "..."` do versao.py da cópia de montagem."""
    arquivo = comum.MONTAGEM / "versao.py"
    linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)
    achadas = [i for i, linha in enumerate(linhas) if linha.startswith("VERSAO = ")]
    if len(achadas) != 1:
        raise SystemExit("PAREI: não achei uma linha só 'VERSAO = ' no versao.py")
    linhas[achadas[0]] = f'VERSAO = "{v}"\n'
    arquivo.write_text("".join(linhas), encoding="utf-8")


def publicar(argumentos: list[str], registro: Path) -> int:
    """Roda o publicar de verdade na cópia de montagem, com a saída num arquivo. Devolve o código."""
    registro.parent.mkdir(parents=True, exist_ok=True)
    antes = foto_dos_projetos()
    inicio = time.time()
    with registro.open("w", encoding="utf-8") as saida:
        saida.write(f"== {' '.join(argumentos)} | {time.strftime('%d/%m/%Y %H:%M:%S')} ==\n")
        saida.flush()
        ambiente = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        r = subprocess.run([str(PYTHON), "publicar_versao_kaique.py", *argumentos], cwd=comum.MONTAGEM,
                           stdout=saida, stderr=subprocess.STDOUT, env=ambiente)
        saida.write(f"\n== saída {r.returncode}; {time.time() - inicio:.0f} s ==\n")
    if foto_dos_projetos() != antes:
        raise SystemExit("PAREI: a pasta dos projetos do Samuel mudou durante o publicar (não devia)")
    return r.returncode


def assinatura_falsa(v: str) -> None:
    """Troca a assinatura da versão por uma feita com uma chave nova (não a do Samuel) e guarda a verdadeira fora do
    estoque. Confere: a falsa é recusada pela conferência do programa; a verdadeira é aceita."""
    sys.path.insert(0, str(comum.MONTAGEM))
    import assinatura
    import versao

    pasta = comum.ESTOQUE / f"v{v}"
    nome_pacote = f"{versao.ID_DO_PACOTE}-{v}-full.nupkg"
    nome_assinatura = assinatura.nome_do_arquivo_da_assinatura(versao.ID_DO_PACOTE, v)
    pacote, arquivo = pasta / nome_pacote, pasta / nome_assinatura
    esperado = assinatura.VersaoAssinada(versao.ID_DO_PACOTE, v, nome_pacote, assinatura.soma_sha256(pacote))
    guardada = comum.ASSINATURA_VERDADEIRA / nome_assinatura
    if not guardada.exists():
        if assinatura.conferir_versao(arquivo.read_text(encoding="utf-8"), esperado) is not None:
            raise SystemExit("PAREI: a assinatura publicada da 1.9.5 nem é a verdadeira")
        guardada.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(arquivo, guardada)
    falsa = assinatura.escrever_assinatura(assinatura.nova_chave_privada(), esperado)
    arquivo.write_text(falsa, encoding="utf-8")
    motivo = assinatura.conferir_versao(arquivo.read_text(encoding="utf-8"), esperado)
    if motivo is None:
        raise SystemExit("PAREI: a assinatura falsa foi aceita (não devia)")
    if assinatura.conferir_versao(guardada.read_text(encoding="utf-8"), esperado) is not None:
        raise SystemExit("PAREI: a assinatura verdadeira guardada não confere")
    print(f"  {v}: assinatura trocada pela falsa; a conferência do programa diz: {motivo}")


def main() -> int:
    """Monta tudo o que falta, na ordem."""
    comum.conferir_espaco_do_c()
    cópia_limpa()
    estoque = comum.ESTOQUE
    if not (estoque / "motor-kraken-1").is_dir():
        print("motor do Kraken: publicando no estoque...", flush=True)
        if publicar(["--motor", "--pasta", str(estoque)], comum.REGISTROS / "motor.txt") != 0:
            raise SystemExit("PAREI: o publicar do motor parou (ver o registro)")
    for v, com_instalador, especial in VERSOES:
        if (estoque / f"v{v}").is_dir():
            print(f"{v}: já está no estoque, pulo")
            if especial == "assinatura_falsa" and not (comum.ASSINATURA_VERDADEIRA).is_dir():
                assinatura_falsa(v)          # retomada: publicada, mas a troca da assinatura não tinha sido feita
            continue
        comum.conferir_espaco_do_c()
        print(f"{v}: montando e publicando no estoque ({time.strftime('%H:%M:%S')})...", flush=True)
        try:
            pôr_o_numero(v)
            if especial == "sem_tela_final":
                (comum.MONTAGEM / ARQUIVO_TIRADO_NA_QUEBRADA).unlink()
            argumentos = ["--pasta", str(estoque)] + (["--com-instalador"] if com_instalador else [])
            codigo = publicar(argumentos, comum.REGISTROS / f"v{v}.txt")
        finally:
            cópia_limpa()
        if codigo != 0:
            raise SystemExit(f"PAREI: o publicar da {v} parou (ver {comum.REGISTROS / f'v{v}.txt'})")
        if especial == "assinatura_falsa":
            assinatura_falsa(v)
        print(f"{v}: pronta ({time.strftime('%H:%M:%S')})", flush=True)
    print("FIM: todas as versões estão no estoque")
    return 0


if __name__ == "__main__":
    sys.exit(main())
