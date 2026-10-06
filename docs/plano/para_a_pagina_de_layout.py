r"""Prepara o conteúdo da página "Layout do Editor de Impressão" (artifact com banco).

A página (https://claude.ai/artifact/QuzVaghq2tz2WVwJ1AyMWu, ver a memória
editor-impressao-pagina-layout) mostra, a partir do banco de dados dela:
  - coleção `decisoes` / `respostas`: as escolhas de layout (iguais às da
    página de escolhas);
  - coleção `textos`: `botoes` (Botoes e funcoes para o layout.md) e
    `rascunho` (Plano de layout (rascunho).md), copiados inteiros;
  - coleção `telas`: a galeria de todos os prints já mostrados (pasta imagens\),
    um documento por grupo {grupo, ordem, imagens: [{src, legenda}]}.

Este script só lê a pasta layout\ e grava, numa pasta de saída:
  - img\<arquivo>.png: cópia dos prints (para publicar como `files` da página);
  - db\textos-<id>.json e db\telas-<id>.json: um JSON por documento, para a
    gerente enviar com ArtifactData "batch" (op set; collection e doc_id vêm
    do nome do arquivo: "<colecao>-<doc_id>.json").
Rodar de novo quando o rascunho, a lista de botões ou as imagens mudarem.

Uso:
    .venv\\Scripts\\python.exe docs\\plano\\para_a_pagina_de_layout.py <pasta de saída>

Seguro mudar: GRUPOS (nome de cada grupo de prints pelo número do arquivo).
"""
import datetime
import json
import pathlib
import re
import shutil
import sys

LAYOUT = pathlib.Path("D:/programas/EditorImpressao-arquivos/plano-24-09-2026/layout")

# Prefixo do nome do print -> (ordem, nome do grupo na galeria).
GRUPOS = {
    "0": (0, "Mapa das partes"),
    "1": (1, "Área de trabalho"),
    "2": (2, "Tela inicial: primeiras opções"),
    "3": (3, "Miniaturas"),
    "4": (4, "Todas as páginas"),
    "5": (5, "Conferir"),
    "6": (6, "Automático"),
    "7": (7, "Painéis da direita"),
    "8": (8, "Rodada 3: as novas"),
    "9": (9, "Padrão do Kaique"),
    "10": (10, "Rodada 4: tela inicial"),
    "11": (11, "Rodada 5: tela inicial"),
    "12": (12, "Rodada 6: tela inicial"),
    "13": (13, "Rodada 7"),
    "14": (14, "Rodada 8"),
    "15": (15, "Rodada 9"),
    "16": (16, "Rodada 10"),
    "tela": (-1, "O programa antigo"),
}


def legenda(nome: str) -> str:
    """Nome de arquivo -> legenda legível ("1-area-de-trabalho-opcao-2" -> "Area de trabalho opcao 2")."""
    base = re.sub(r"^\d+-", "", pathlib.Path(nome).stem)
    base = base.replace("rodada4-", "").replace("rodada5-", "").replace("rodada6-", "").replace("rodada7-", "")
    texto = base.replace("-", " ").strip()
    return texto[:1].upper() + texto[1:]


def main() -> None:
    saida = pathlib.Path(sys.argv[1])
    (saida / "img").mkdir(parents=True, exist_ok=True)
    (saida / "db").mkdir(parents=True, exist_ok=True)
    agora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for doc_id, arquivo in (("botoes", "Botoes e funcoes para o layout.md"),
                            ("rascunho", "Plano de layout (rascunho).md")):
        md = (LAYOUT / arquivo).read_text(encoding="utf-8")
        (saida / "db" / f"textos-{doc_id}.json").write_text(
            json.dumps({"md": md, "arquivo": arquivo, "atualizado": agora}, ensure_ascii=False), encoding="utf-8")

    n = 0
    grupos = {}
    for png in sorted((LAYOUT / "imagens").glob("*.png")):
        prefixo = png.name.split("-")[0]
        ordem_g, grupo = GRUPOS.get(prefixo, (99, "Outras"))
        shutil.copy2(png, saida / "img" / png.name)
        g = grupos.setdefault(prefixo if prefixo in GRUPOS else "outras", {"grupo": grupo, "ordem": ordem_g, "imagens": []})
        g["imagens"].append({"src": f"img/{png.name}", "legenda": legenda(png.name)})
        n += 1
    for chave, doc in grupos.items():
        (saida / "db" / f"telas-g{chave}.json").write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    print(n, "prints;", "textos: botoes, rascunho")


if __name__ == "__main__":
    main()
