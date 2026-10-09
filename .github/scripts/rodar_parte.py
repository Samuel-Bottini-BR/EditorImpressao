"""Roda UMA das partes da suite de testes, arquivo por arquivo, como no PC do Samuel.

Usado pelo .github/workflows/testes-windows.yml (os testes no Windows do GitHub).
Nao e parte do programa: nada aqui e importado por core/, ui/ ou tests/.

    python .github/scripts/rodar_parte.py --parte 1 --de 5 --saida relatorio-parte-1
    python .github/scripts/rodar_parte.py --listar --de 5      # so mostra a divisao

O que faz:
  1. Divide os tests/test_*.py em N partes de forma ESTAVEL (a mesma lista de
     arquivos da sempre a mesma divisao) e EQUILIBRADA: cada arquivo tem um
     "peso" (o tempo medido numa rodada anterior, em .github/tempos-dos-testes.json,
     ou, para arquivo que nao esta la, uma estimativa pelo tamanho do arquivo,
     multiplicada para os testes que abrem a janela de verdade, que sao os mais
     lentos). Os mais pesados vao primeiro, sempre para a parte mais leve
     (o metodo guloso classico, "LPT").
  2. Roda cada arquivo da parte num pytest separado, como o Samuel roda no PC
     (PARTE -13 do resumo): -p no:cacheprovider, --basetemp proprio por arquivo,
     TEMP/TMP dentro da pasta de trabalho (quem chama ja define), relatorio
     junit (.xml) por arquivo e a saida em texto (.txt) por arquivo.
  3. Grava resumo.txt (uma linha por arquivo: codigo de saida, segundos e a
     ultima linha do pytest) e tempos.json (segundos por arquivo, para afinar a
     divisao da proxima vez).
  Devolve 1 se algum arquivo falhou (codigo do pytest diferente de 0 e de 5).

Seguro mudar: o numero de partes (--de), o peso estimado dos arquivos sem tempo
medido, o limite de tempo por arquivo. Arriscado: rodar varios arquivos no mesmo
pytest (o Samuel roda um por vez; juntar muda a ordem e o estado compartilhado
entre arquivos, e um resultado diferente do PC dele deixaria de ser comparavel);
trocar o criterio de divisao por algo nao deterministico (cada execucao rodaria
os arquivos em maquinas diferentes, e um defeito que depende da ordem sumiria e
voltaria). Nunca acrescentar aqui -k, --deselect, skip ou xfail para "ficar verde".
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
# Segundos por arquivo medidos no Windows do GitHub (execucao 37977429818, 09/10/2026),
# copiados do job "Resumo". JSON puro, sem comentario. Atualizar quando a suite mudar muito.
TEMPOS = RAIZ / ".github" / "tempos-dos-testes.json"

# Teste que abre a JanelaPrincipal ou mexe nas telas pesa mais que o tamanho
# do arquivo sugere (cada um monta a janela inteira). Fator escolhido a olho;
# so vale ate existir tempo medido para o arquivo.
FATOR_DE_TELA = 4.0
PALAVRAS_DE_TELA = ("JanelaPrincipal", "TelaConferir", "tela_conferir", "QApplication")

# Limite por arquivo: um arquivo travado nao segura a parte inteira ate o
# limite do job (60 min). Folgado: o mais lento no PC do Samuel leva poucos minutos.
LIMITE_POR_ARQUIVO_S = 25 * 60


def arquivos_de_teste() -> list[Path]:
    """Todos os tests/test_*.py, em ordem de nome (a ordem estavel)."""
    return sorted((RAIZ / "tests").glob("test_*.py"))


def peso(arquivo: Path, medidos: dict[str, float]) -> float:
    """Segundos medidos, ou uma estimativa: 1 s por 2 KB, vezes FATOR_DE_TELA
    se o arquivo mexe na janela."""
    if arquivo.name in medidos:
        return float(medidos[arquivo.name])
    texto = arquivo.read_text(encoding="utf-8", errors="replace")
    estimado = max(1.0, arquivo.stat().st_size / 2048)
    if any(p in texto for p in PALAVRAS_DE_TELA):
        estimado *= FATOR_DE_TELA
    return estimado


def dividir(n: int) -> list[list[Path]]:
    """N listas de arquivos, equilibradas pelo peso (guloso, deterministico:
    empate de peso desempata pelo nome; empate de parte, pela de menor numero)."""
    medidos: dict[str, float] = {}
    if TEMPOS.is_file():
        medidos = json.loads(TEMPOS.read_text(encoding="utf-8"))
    pesados = sorted(arquivos_de_teste(), key=lambda a: (-peso(a, medidos), a.name))
    partes: list[list[Path]] = [[] for _ in range(n)]
    somas = [0.0] * n
    for arquivo in pesados:
        i = min(range(n), key=lambda k: (somas[k], k))
        partes[i].append(arquivo)
        somas[i] += peso(arquivo, medidos)
    for parte in partes:
        parte.sort(key=lambda a: a.name)
    return partes


def rodar(arquivos: list[Path], saida: Path) -> int:
    """Roda cada arquivo num pytest proprio e grava os relatorios em `saida`."""
    saida.mkdir(parents=True, exist_ok=True)
    base = Path(os.environ.get("PASTA_TEMP_DOS_TESTES", RAIZ / "_temp_testes"))
    # O pytest cria a pasta do --basetemp, mas nao as pastas acima dela (no
    # Windows do GitHub, sem isto, todo teste com tmp_path dava FileNotFoundError).
    (base / "pytest").mkdir(parents=True, exist_ok=True)
    resumo, tempos, falhou = [], {}, False
    for arquivo in arquivos:
        nome = arquivo.stem
        comando = [sys.executable, "-m", "pytest", str(arquivo.relative_to(RAIZ)), "-q",
                   "-p", "no:cacheprovider", "-rfEs",
                   f"--basetemp={base / 'pytest' / nome}",
                   f"--junitxml={saida / (nome + '.xml')}"]
        print(f"\n===== {arquivo.name} =====", flush=True)
        inicio = time.time()
        try:
            r = subprocess.run(comando, cwd=RAIZ, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=LIMITE_POR_ARQUIVO_S)
            codigo, texto = r.returncode, r.stdout + r.stderr
        except subprocess.TimeoutExpired as e:
            codigo = -999
            texto = ((e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes)
                     else (e.stdout or "")) + f"\nPASSOU DO LIMITE DE {LIMITE_POR_ARQUIVO_S} s\n"
        segundos = time.time() - inicio
        (saida / f"{nome}.txt").write_text(texto, encoding="utf-8")
        linhas = [l for l in texto.strip().splitlines() if l.strip()]
        ultima = linhas[-1] if linhas else "(sem saida)"
        print(texto[-3000:] if codigo not in (0, 5) else ultima, flush=True)
        resumo.append(f"{codigo:5d}  {segundos:7.1f} s  {arquivo.name}  |  {ultima}")
        tempos[arquivo.name] = round(segundos, 1)
        if codigo not in (0, 5):   # 5 = nenhum teste coletado
            falhou = True
    (saida / "resumo.txt").write_text("\n".join(resumo) + "\n", encoding="utf-8")
    (saida / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                       encoding="utf-8")
    print("\n" + "\n".join(resumo))
    return 1 if falhou else 0


def main() -> int:
    """Le os argumentos e lista a divisao ou roda a parte pedida."""
    p = argparse.ArgumentParser()
    p.add_argument("--parte", type=int, default=1, help="1..N")
    p.add_argument("--de", type=int, default=5, help="N partes")
    p.add_argument("--saida", default="relatorio-testes")
    p.add_argument("--listar", action="store_true")
    a = p.parse_args()
    partes = dividir(a.de)
    if a.listar:
        medidos = json.loads(TEMPOS.read_text(encoding="utf-8")) if TEMPOS.is_file() else {}
        for i, parte in enumerate(partes, 1):
            print(f"parte {i}: {len(parte)} arquivos, peso {sum(peso(x, medidos) for x in parte):.0f}")
            for x in parte:
                print("   ", x.name)
        return 0
    return rodar(partes[a.parte - 1], Path(a.saida).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
