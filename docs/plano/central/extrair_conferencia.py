"""Tira da página de conferência publicada os relatórios que ainda esperam o Samuel e grava um JSON cada.

A página de conferência (https://claude.ai/artifact/J8AwcyyUwrZ2n7kSevyGvX) guarda os quadros dentro do
próprio HTML, em variáveis `var PR4 = {...}`, `var LY5 = {...}` etc. A Central de decisões mostra esses mesmos
relatórios, um por aba, dentro da aba "Conferência". Este script lê o HTML baixado (Artifact read com
path "index.html"), separa cada variável e grava `conferencias/<nome>.json`, mais `_imagens.txt` com todas as
fotos citadas (para copiar para a Central com `files: {artifact, path}`).

Uso:
    .venv\\Scripts\\python.exe docs\\plano\\central\\extrair_conferencia.py <index.html baixado>

Seguro mudar: a lista RELATORIOS (acrescentar uma variável nova quando a conferência ganhar aba).
Arriscado: o corte depende de as variáveis serem JSON puro (as de 21/10 são; G6, LAYOUT e CORTE não são).
"""
import json
import pathlib
import sys

AQUI = pathlib.Path(__file__).resolve().parent

# variável na página de conferência -> (id na Central, nome curto da aba, trabalho da Central)
# Os cinco abaixo foram respondidos pelo Samuel em 21/10/2026; os JSON ficaram em conferencias/respondidas/.
# Não rode de novo com eles (recriaria abas já respondidas). Relatório novo: entra aqui ou como JSON direto em
# conferencias/ (como o ly67.json, feito da conferência do layout 6 e 7 do ramo verif-layout-4a5-2026-10-21).
RELATORIOS_RESPONDIDOS = {
    "PR4": ("pr", "Para revisar", "para-revisar"),
    "LY5": ("ly", "Layout 4 e 5", "layout-4a5"),
    "P28": ("p28", "Preto e branco (2.8)", "2.8"),
    "P29": ("p29", "Letra clara (2.9)", "2.9"),
    "P211": ("p211", "Cores e páginas diferentes (2.11 e 2.15)", "2.11-2.15"),
}
RELATORIOS: dict = {}


def cortar_objeto(texto: str, nome: str) -> dict:
    """Acha `var NOME = {` e devolve o objeto, contando chaves fora das aspas."""
    i = texto.index(f"var {nome} = ")
    ini = texto.index("{", i)
    fundo, em_texto, escape = 0, False, False
    for j in range(ini, len(texto)):
        c = texto[j]
        if em_texto:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                em_texto = False
            continue
        if c == '"':
            em_texto = True
        elif c == "{":
            fundo += 1
        elif c == "}":
            fundo -= 1
            if fundo == 0:
                return json.loads(texto[ini:j + 1])
    raise ValueError(f"{nome}: fim do objeto não achado")


def imagens(o, achadas: set) -> None:
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "src" and isinstance(v, str):
                achadas.add(v)
            else:
                imagens(v, achadas)
    elif isinstance(o, list):
        for v in o:
            imagens(v, achadas)


def prefixar(o, prefixo: str):
    """Põe o prefixo em todo "src" (a Central guarda as fotos de cada página numa pasta)."""
    if isinstance(o, dict):
        return {k: (prefixo + v if k == "src" and isinstance(v, str) else prefixar(v, prefixo)) for k, v in o.items()}
    if isinstance(o, list):
        return [prefixar(v, prefixo) for v in o]
    return o


def impressao(pasta: pathlib.Path) -> dict:
    """As perguntas abertas da parte "Impressão" da página de escolhas, no formato das perguntas do PR4."""
    perguntas = []
    for arq in sorted(pasta.glob("*.json")):
        d = json.loads(arq.read_text(encoding="utf-8"))
        if d.get("parte") != "Impressão" or d.get("status") == "decidida":
            continue
        perguntas.append({
            "id": arq.stem, "titulo": d.get("pergunta", ""), "ordem": d.get("ordem", 0),
            "explicacao": [x.strip() for x in str(d.get("explicacao", "")).split("\n\n") if x.strip()],
            "exemplos": d.get("exemplos", []),
            "opcoes": [{"id": o.get("id"), "nome": o.get("nome"), "texto": o.get("texto", ""), "imgs": o.get("imgs", [])}
                       for o in d.get("opcoes", [])],
        })
    perguntas.sort(key=lambda q: q["ordem"])
    return {"resumo": {"titulo": "As perguntas da fase de impressão", "paragrafos": [
        "A pesquisa da fase de impressão está entregue. Faltam estas respostas para começar o código das margens e do arquivo para imprimir (itens 2.4 e 2.6)."]},
        "quadros": [], "perguntas": perguntas}


def main() -> None:
    texto = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    pasta = AQUI / "conferencias"
    pasta.mkdir(exist_ok=True)
    todas: set = set()
    for n, (var, (cid, nome, trabalho)) in enumerate(RELATORIOS.items()):
        o = cortar_objeto(texto, var)
        o = prefixar({"id": cid, "nome": nome, "trabalho": trabalho, "ordem": n, "origem": var, **o}, "conf/")
        imagens(o, todas)
        (pasta / f"{cid}.json").write_text(json.dumps(o, ensure_ascii=False, indent=1), encoding="utf-8")
        print(cid, len(o.get("quadros", [])), "quadros", len(o.get("perguntas", [])), "perguntas")
    if len(sys.argv) > 2:
        o = prefixar(impressao(pathlib.Path(sys.argv[2])), "esc/")
        o = {"id": "imp", "nome": "Impressão (6 perguntas)", "trabalho": "impressao", "ordem": len(RELATORIOS), "origem": "escolhas", **o}
        imagens(o, todas)
        (pasta / "imp.json").write_text(json.dumps(o, ensure_ascii=False, indent=1), encoding="utf-8")
        print("imp", len(o["perguntas"]), "perguntas")
    # uma linha por foto: caminho na Central <tab> página de origem <tab> caminho na origem
    linhas = [f"{s}\t{'conferencia' if s.startswith('conf/') else 'escolhas'}\t{s.split('/', 1)[1]}" for s in sorted(todas)]
    (pasta / "_imagens.txt").write_text("\n".join(linhas), encoding="utf-8")
    print("imagens:", len(todas))


if __name__ == "__main__":
    main()
