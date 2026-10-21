"""Gera o banco da Central de decisões (https://claude.ai/artifact/XNFrsdVR7q4K8cBcxNftZy).

Junta quatro fontes:
  - docs/plano/central/fonte.json  os trabalhos, os agentes e a velocidade (a gerente mantém);
  - docs/plano/PLANO-DEFINITIVO.md  as fases (texto de cada uma, para abrir na aba Etapas);
  - memoria/bugs.md                 os defeitos abertos e os consertados a conferir;
  - o git                           confere se cada trabalho "no programa" está mesmo no fase-1
                                    e se os outros ainda não estão (avisa se não bater).

Grava um JSON por documento em <pasta>/<coleção>/<id>.json e, em <pasta>/lotes/, os lotes
para a ferramenta ArtifactData (ação "batch", até 50 por lote, com file_path). As coleções que
a página escreve (ordens, testes, ideias, config) não são tocadas.

Uso:
    .venv\\Scripts\\python.exe docs\\plano\\para_a_central.py <pasta de saída>

Substitui o para_a_pagina_de_andamento.py (a página de andamento virou a Central em 21/10/2026).
"""
import datetime
import json
import pathlib
import re
import subprocess
import sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
from para_a_pagina_de_andamento import partes  # noqa: E402

NO_PROGRAMA = {"programa", "sem-aprovado"}
NOMES_FASE = {
    "0": "Arrumar a casa", "1": "Separar o escrito do fundo", "2": "Ferramentas do ScanTailor",
    "3": "Seleção manual", "4": "Layout", "5": "Desempenho", "6": "O resto do resultado final",
    "7": "Treinar os OCRs",
}


def no_fase1(commit: str) -> bool | None:
    r = subprocess.run(["git", "-C", str(RAIZ), "merge-base", "--is-ancestor", commit, "fase-1"],
                       capture_output=True)
    if r.returncode in (0, 1):
        return r.returncode == 0
    return None  # commit desconhecido


def defeitos() -> list[dict]:
    """Lê as tabelas das seções 1 (abertos) e 2 (consertados, a conferir) do memoria/bugs.md."""
    texto = (RAIZ / "memoria" / "bugs.md").read_text(encoding="utf-8")
    saida, secao, onde = [], None, ""
    for linha in texto.splitlines():
        if linha.startswith("## "):
            secao = "aberto" if linha.startswith("## 1.") else "conferir" if linha.startswith("## 2.") else None
            continue
        if linha.startswith("### "):
            onde = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", linha[4:]).replace("`", "").strip()
            continue
        if not secao or not linha.startswith("|") or linha.startswith("|---") or linha.startswith("| Linha"):
            continue
        cel = [c.strip() for c in linha.strip("|").split("|")]
        if len(cel) < 4:
            continue
        situacao = cel[3].replace("`", "")
        grav = "aceito" if re.search(r"aceit|movido|Fase 5|por enquanto", situacao, re.I) else "aberto"
        if secao == "conferir":
            grav = "conferir"
        saida.append({
            "onde": onde, "data": cel[1], "texto": re.sub(r"`", "", cel[2]),
            "situacao": situacao, "grupo": grav, "teste": cel[4] if len(cel) > 4 else "",
        })
    for n, d in enumerate(saida):
        d["ordem"] = n
    return saida


def main() -> None:
    destino = pathlib.Path(sys.argv[1])
    fonte = json.loads((AQUI / "central" / "fonte.json").read_text(encoding="utf-8"))
    agora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    docs: dict[tuple[str, str], dict] = {}
    avisos = []

    for n, t in enumerate(fonte["trabalhos"]):
        t = dict(t)
        t["ordem"] = n
        t["atualizado"] = agora
        if t.get("commit"):
            dentro = no_fase1(t["commit"])
            t["noFase1"] = dentro
            esperado = t["coluna"] in NO_PROGRAMA
            if dentro is None:
                avisos.append(f"{t['id']}: commit {t['commit']} não achado no git")
            elif dentro != esperado:
                avisos.append(f"{t['id']}: coluna '{t['coluna']}' mas commit {'está' if dentro else 'não está'} no fase-1")
        docs[("trabalhos", t.pop("id"))] = t

    textos = {}
    for p in partes((AQUI / "PLANO-DEFINITIVO.md").read_text(encoding="utf-8")):
        m = re.match(r"FASE (\d+)", p["titulo"])
        if p["grupo"] == "fase" and m:
            textos[m.group(1)] = p["md"]
    for num, nome in NOMES_FASE.items():
        conta = {}
        for t in fonte["trabalhos"]:
            if t["fase"] == num:
                conta[t["coluna"]] = conta.get(t["coluna"], 0) + 1
        docs[("fases", f"fase-{num}")] = {
            "num": int(num), "nome": nome, "atual": num == fonte["geral"]["faseAtual"],
            "contagem": conta, "md": textos.get(num, ""), "atualizado": agora,
        }

    for n, a in enumerate(fonte["agentes"]):
        a = dict(a, ordem=n)
        docs[("agentes", a.pop("id"))] = a

    docs[("defeitos", "lista")] = {"itens": defeitos(), "atualizado": agora}

    docs[("velocidade", "dados")] = dict(fonte["velocidade"], atualizado=agora)
    docs[("geral", "resumo")] = dict(fonte["geral"], atualizado=agora, avisos=avisos)

    for (col, i), d in docs.items():
        arq = destino / col / f"{i}.json"
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    lotes = destino / "lotes"
    lotes.mkdir(parents=True, exist_ok=True)
    chaves = sorted(docs)
    for k in range(0, len(chaves), 50):
        lote = [{"op": "set", "collection": c, "doc_id": i, "file_path": str((destino / c / f"{i}.json").resolve())}
                for c, i in chaves[k:k + 50]]
        (lotes / f"lote-{k // 50 + 1}.json").write_text(json.dumps(lote, ensure_ascii=False, indent=1), encoding="utf-8")

    por_col = {}
    for c, _ in chaves:
        por_col[c] = por_col.get(c, 0) + 1
    print("documentos:", por_col)
    print("lotes:", (len(chaves) + 49) // 50)
    for a in avisos:
        print("AVISO:", a)


if __name__ == "__main__":
    main()
