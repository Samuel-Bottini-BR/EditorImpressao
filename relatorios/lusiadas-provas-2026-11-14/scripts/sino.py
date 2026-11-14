"""Verificador, 14/11/2026 (D-679, o sino que muda sozinho): numa CÓPIA do projeto da fase b (lida
do disco; nada é gravado), conta as páginas com aviso pendente (core.avisos.quantas_com_duvida, o
número do sino) antes e depois de desenhar cada página no tamanho do PDF (renderizar_pagina,
o mesmo desenho do processar e da medida por trás). Se o número sobe, avisos novos nascem do
desenho da página, sem ninguém mexer. Anota quais avisos nasceram e em que páginas."""
import json, os, sys
from collections import Counter
from pathlib import Path
AQUI = Path(__file__).resolve().parent; PASTA = AQUI.parent; RAIZ = PASTA.parents[1]; TRAB = PASTA / "_dados"
os.environ["LOCALAPPDATA"] = str(TRAB / "dados-analise"); os.chdir(RAIZ); sys.path.insert(0, str(RAIZ))
import projetos  # noqa
projetos.pasta_dos_projetos = lambda: TRAB / "projetos"
from core import pipeline, avisos  # noqa
from core.pdf_io import abrir_pdf  # noqa

pasta = next(p for p in (TRAB / "projetos").iterdir() if (p / "projeto.json").exists())
projeto = projetos.carregar_estado(projetos.ler_resumo(pasta))
doc = abrir_pdf(projeto.caminho_entrada)
antes = avisos.quantas_com_duvida(projeto)
pend_antes = {(a.alvo, a.indice, a.codigo) for a in avisos.pendentes_do_livro(projeto)}
res = {"antes": antes, "por_pagina": []}
for pg in projeto.paginas:
    if pg.apagada:
        continue
    n0 = avisos.quantas_com_duvida(projeto)
    pipeline.renderizar_pagina(doc, projeto, pg, dpi=int(projeto.qualidade_dpi or 300))
    n1 = avisos.quantas_com_duvida(projeto)
    if n1 != n0:
        res["por_pagina"].append({"pagina": pg.indice + 1, "de": n0, "para": n1})
        print(pg.indice + 1, n0, "->", n1, flush=True)
novos = [(a.alvo, a.indice, a.codigo) for a in avisos.pendentes_do_livro(projeto)
         if (a.alvo, a.indice, a.codigo) not in pend_antes]
res["depois"] = avisos.quantas_com_duvida(projeto)
res["avisos_novos_por_motivo"] = dict(Counter(c for _a, _i, c in novos))
res["avisos_novos"] = [{"alvo": a, "indice": i + 1, "codigo": c} for a, i, c in novos][:60]
(AQUI / "sino.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in res.items() if k != "avisos_novos"}, ensure_ascii=False))
