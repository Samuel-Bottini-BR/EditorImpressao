"""Divide o PLANO-DEFINITIVO.md em partes para a página "Andamento do programa".

A página (https://claude.ai/artifact/XNFrsdVR7q4K8cBcxNftZy) mostra o plano
completo a partir do banco de dados dela, coleção `plano`: um documento por
seção (1, 2, 3), um por fase (dentro da seção 4) e um por lista (5, 6, 7).

Este script só lê o plano e grava um JSON por documento numa pasta; quem
envia é a gerente (Claude Code), com a ferramenta ArtifactData, ação "batch",
uma entrada `set` por arquivo (collection "plano", doc_id = nome do arquivo
sem ".json"). Rodar de novo sempre que o plano mudar.

Uso:
    .venv\\Scripts\\python.exe docs\\plano\\para_a_pagina_de_andamento.py <pasta de saída>

Seguro mudar: os títulos curtos (CURTOS). Arriscado: a forma de dividir
depende de as seções começarem com "## " e as fases com "### FASE".
"""
import datetime
import json
import pathlib
import re
import sys

PLANO = pathlib.Path(__file__).with_name("PLANO-DEFINITIVO.md")

# Marcadores das listas de itens do plano: [x] aprovado, [~] melhorar,
# [-] descartado, [ ] em aberto (regra 4 do plano).
MARCAS = {"x": "aprovado", "~": "melhorar", "-": "descartado", " ": "aberto"}


def contar(md: str) -> dict:
    """Quantos itens de cada estado a parte tem (só linhas de lista com marcador)."""
    conta = {v: 0 for v in MARCAS.values()}
    for m in re.finditer(r"^\s*- \[([x~\- ])\]", md, flags=re.M):
        conta[MARCAS[m.group(1)]] += 1
    return conta


def partes(texto: str) -> list[dict]:
    """Corta o plano em seções "## " e, dentro da seção 4, em fases "### "."""
    linhas = texto.splitlines()
    cortes = []
    for i, l in enumerate(linhas):
        if l.startswith("## ") or l.startswith("### FASE"):
            cortes.append(i)
    saida = [{"id": "p00-topo", "grupo": "topo", "titulo": "O plano",
              "md": "\n".join(linhas[1:cortes[0]]).strip().strip("-").strip()}]
    for n, ini in enumerate(cortes):
        fim = cortes[n + 1] if n + 1 < len(cortes) else len(linhas)
        cab = linhas[ini]
        corpo = "\n".join(linhas[ini + 1:fim]).strip()
        corpo = re.sub(r"\n-{3,}\s*$", "", corpo).strip()
        if cab.startswith("### FASE"):
            titulo = cab[4:].strip()
            num = re.match(r"FASE (\d+)", titulo).group(1)
            saida.append({"id": f"p40-fase-{num}", "grupo": "fase", "titulo": titulo, "md": corpo})
        else:
            titulo = cab[3:].strip()
            num = re.match(r"(\d+)\.", titulo)
            num = num.group(1) if num else "9"
            if num == "4":
                continue  # a seção 4 é só o cabeçalho das fases
            grupo = "regras" if num in ("1", "2", "3") else "lista"
            saida.append({"id": f"p{num}0-secao-{num}", "grupo": grupo, "titulo": titulo, "md": corpo})
    for ordem, p in enumerate(saida):
        p["ordem"] = ordem
        p["contagem"] = contar(p["md"])
    return saida


def main() -> None:
    destino = pathlib.Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    agora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for p in partes(PLANO.read_text(encoding="utf-8")):
        doc = {k: v for k, v in p.items() if k != "id"}
        doc["atualizado"] = agora
        (destino / f"{p['id']}.json").write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        print(p["id"], p["titulo"][:50], p["contagem"], len(p["md"]))


if __name__ == "__main__":
    main()
