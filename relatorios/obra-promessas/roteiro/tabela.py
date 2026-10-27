"""Monta a tabela "botão | promessa | cumpre / quebra / aguarda etapa" do ONDE-PAREI a partir da
lista de promessas (tests/promessas/promessas.md) e do resultado de uma rodada do
tests/test_promessas.py gravada com --junitxml.

Uso (verificador, 27/10/2026):
    .venv\\Scripts\\python.exe -m pytest tests\\test_promessas.py --junitxml=saida_teste\\promessas.xml
    .venv\\Scripts\\python.exe relatorios\\obra-promessas\\roteiro\\tabela.py saida_teste\\promessas.xml
Escreve a tabela na saída (markdown).
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

from tests.promessas.ajudantes import ler_promessas  # noqa: E402

FONTE = (RAIZ / "tests" / "test_promessas.py").read_text(encoding="utf-8")


def _testes_de_cada_promessa() -> dict[str, list[str]]:
    """Promessa -> nomes das funções de prova (pelo @prova("P-NNN") logo acima do def)."""
    saida: dict[str, list[str]] = {}
    for m in re.finditer(r'@prova\("(P-\d{3})"\)', FONTE):
        funcao = re.search(r"\ndef (test_\w+)", FONTE[m.end():])
        saida.setdefault(m.group(1), []).append(funcao.group(1))
    return saida


def _resultados(xml: Path) -> dict[str, list[str]]:
    """Nome da função -> lista de resultados de cada caso ("passou", "falhou", "xfail", "pulou")."""
    saida: dict[str, list[str]] = {}
    for caso in ET.parse(xml).getroot().iter("testcase"):
        nome = caso.get("name", "").split("[")[0]
        if caso.find("failure") is not None or caso.find("error") is not None:
            r = "falhou"
        elif caso.find("skipped") is not None:
            tipo = caso.find("skipped").get("type", "")
            r = "xfail" if "xfail" in tipo or "xfail" in (caso.find("skipped").get("message") or "") else "pulou"
        else:
            r = "passou"
        saida.setdefault(nome, []).append(r)
    return saida


def main() -> None:
    promessas = ler_promessas()
    provas = _testes_de_cada_promessa()
    resultados = _resultados(Path(sys.argv[1]))
    contagem = {"cumpre": 0, "quebra": 0, "aguarda etapa": 0, "não testada": 0}
    print("| Promessa | Botão (onde) | O que promete (resumo) | Situação |")
    print("|---|---|---|---|")
    for numero, p in promessas.items():
        casos = [r for f in provas.get(numero, []) for r in resultados.get(f, [])]
        if p.aguarda:
            situacao = f"aguarda {p.aguarda}" + (" (passou? ver)" if "passou" in casos else "")
            contagem["aguarda etapa"] += 1
        elif "falhou" in casos:
            situacao = "**QUEBRA**" + (" (defeito " + re.search(r"defeito (\w)", p.campos.get("defeito", "defeito ?")).group(1) + ")"
                                        if "defeito" in p.campos else "")
            contagem["quebra"] += 1
        elif casos and all(c in ("passou",) for c in casos):
            situacao = "cumpre"
            contagem["cumpre"] += 1
        elif casos and "passou" in casos:
            situacao = "cumpre (parte pulada)"
            contagem["cumpre"] += 1
        else:
            situacao = "não testada (" + ", ".join(sorted(set(casos))) + ")"
            contagem["não testada"] += 1
        onde = ", ".join(f"`{c}`" for c in p.chaves[:3]) + (" …" if len(p.chaves) > 3 else "")
        promete = " ".join(p.campos.get(k, "") for k in ("no pdf", "no projeto", "na tela") if p.campos.get(k))
        promete = promete[:140] + ("…" if len(promete) > 140 else "")
        print(f"| {numero} | {p.titulo} — {onde} | {promete} | {situacao} |")
    print()
    print("Total:", len(promessas), "·", " · ".join(f"{k}: {v}" for k, v in contagem.items()))


if __name__ == "__main__":
    main()
