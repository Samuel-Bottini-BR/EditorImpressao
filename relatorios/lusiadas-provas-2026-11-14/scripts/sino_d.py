"""Verificador, 14/11/2026 (D-679): lista os avisos pendentes do projeto da fase d (lido do disco),
por página e motivo, para ver qual aviso nasceu enquanto só se andava pelas páginas."""
import json, os, sys
from pathlib import Path
AQUI = Path(__file__).resolve().parent; PASTA = AQUI.parent; RAIZ = PASTA.parents[1]; TRAB = PASTA / "_dados-d"
os.environ["LOCALAPPDATA"] = str(PASTA / "_dados" / "dados-analise"); os.chdir(RAIZ); sys.path.insert(0, str(RAIZ))
import projetos  # noqa
projetos.pasta_dos_projetos = lambda: TRAB / "projetos"
from core import avisos  # noqa
pasta = next(p for p in (TRAB / "projetos").iterdir() if (p / "projeto.json").exists())
pr = projetos.carregar_estado(projetos.ler_resumo(pasta))
lin = []
for a in avisos.pendentes_do_livro(pr):
    lin.append({"onde": avisos.onde_no_livro(a, pr), "alvo": a.alvo, "indice": a.indice + 1, "codigo": a.codigo,
                "titulo": a.titulo})
print(avisos.quantas_com_duvida(pr), "páginas com dúvida")
for l in lin:
    print(l)
(AQUI / "sino_d.json").write_text(json.dumps(lin, ensure_ascii=False, indent=1), encoding="utf-8")
