"""As 17 mutações de quem tentou quebrar (`quem-tenta-quebrar-1/provas/mutacoes_qtq.py`), rodadas de novo depois da
volta 2 (24/11/2026), com TODOS os arquivos de teste do atualizador, inclusive os novos.

Por que um arquivo à parte: o script dele roda numa cópia do ramo (858 MB pelo `git archive`) e só com a lista de
testes de antes; este usa a MESMA lista de mutações (importada do arquivo dele), roda nesta cópia de trabalho e
devolve cada arquivo como estava (como o `mutacoes.py`), e acrescenta à lista de testes os da volta 2. Quando o
trecho dele mudou com o conserto, a mutação equivalente no código novo vai em `TRECHOS_NOVOS` (escrito ao lado).
Uso: `.venv\\Scripts\\python.exe relatorios\\atualizador-novo\\mutacoes_qtq_no_lugar.py`. Saída também em
`mutacoes_qtq_no_lugar-resultado.txt`.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DELE = Path(__file__).parent / "quem-tenta-quebrar-1" / "provas" / "mutacoes_qtq.py"
sys.argv = [str(DELE), str(RAIZ)]                 # o script dele lê a raiz do primeiro argumento
_spec = importlib.util.spec_from_file_location("mutacoes_qtq", DELE)
dele = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dele)

TESTES = dele.TESTES + ["tests/test_atualizador_volta2.py", "tests/test_porteiro_licenca_que_acrescenta.py"]
# O trecho dele que mudou com o conserto -> a mesma mutação no código novo.
TRECHOS_NOVOS = {
    "Q4 motor: 'esta no lugar' sempre sim": (
        "    return not ocr_kraken.conferir_motor(ocr_kraken.pasta_do_motor_instalado(raiz, versao_do_motor),\n"
        "                                         versao_do_motor)", "    return True"),
}


def main() -> int:
    """Roda as mutações; devolve quantas sobreviveram."""
    linhas, sobreviveram = [], 0
    for nome, arquivo, de, para in dele.MUTACOES:
        if nome in TRECHOS_NOVOS:
            de, para = TRECHOS_NOVOS[nome]
            nome += " (trecho do código novo)"
        caminho = RAIZ / arquivo
        original = caminho.read_bytes()
        texto = original.decode("utf-8")
        if "\r\n" in texto:
            de, para = de.replace("\n", "\r\n"), para.replace("\n", "\r\n")
        if texto.count(de) != 1:
            linhas.append(f"[ERRO DA MUTAÇÃO] {nome}: o trecho aparece {texto.count(de)} vezes")
            sobreviveram += 1
            continue
        try:
            caminho.write_bytes(texto.replace(de, para).encode("utf-8"))
            feito = subprocess.run([sys.executable, "-m", "pytest", *TESTES, "-q", "-p", "no:cacheprovider",
                                    "--basetemp=saida_teste/pytest-tmp-mutacoes"],
                                   cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace")
        finally:
            caminho.write_bytes(original)
        ultima = (feito.stdout.strip().splitlines() or [""])[-1]
        falhas = [l.split(" - ")[0] for l in feito.stdout.splitlines() if l.startswith(("FAILED", "ERROR"))]
        if feito.returncode == 0:
            sobreviveram += 1
            linhas.append(f"[SOBREVIVEU] {nome} | {ultima}")
        else:
            linhas.append(f"[acusada] {nome} | {ultima} | {falhas[:2]}")
    saida = "\n".join(linhas) + f"\n\n{sobreviveram} de {len(dele.MUTACOES)} mutações sobreviveram.\n"
    print(saida)
    (Path(__file__).parent / "mutacoes_qtq_no_lugar-resultado.txt").write_text(saida, encoding="utf-8")
    return sobreviveram


if __name__ == "__main__":
    raise SystemExit(main())
