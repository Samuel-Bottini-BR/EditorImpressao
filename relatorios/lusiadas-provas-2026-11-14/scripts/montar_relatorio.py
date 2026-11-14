"""Verificador, 14/11/2026: junta as partes do relatório (escritas no rascunho) e grava os três
formatos com relatorio.gravar, em relatorios/lusiadas-provas-2026-11-14/relatorio.{md,html,pdf}.

    python montar_relatorio.py <pasta das partes>
As partes: relatorio-topo.md, relatorio-parte1.md (erros 1,5,7,10,12,13), relatorio-parte1b.md
(erros 2,3,4,6,8,9,11), relatorio-parte2.md e relatorio-parte2b.md (técnica). Os erros saem na
ordem 1 a 13."""
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[1]
sys.path.insert(0, str(RAIZ))
import relatorio  # noqa: E402

partes = Path(sys.argv[1])
ler = lambda n: (partes / n).read_text(encoding="utf-8")  # noqa: E731


def blocos(texto):
    """'### Erro N — ...' -> {N: bloco}"""
    saida = {}
    for m in re.finditer(r"^### Erro (\d+) .*?(?=^### |^---|\Z)", texto, re.S | re.M):
        saida[int(m.group(1))] = m.group(0).rstrip() + "\n"
    return saida


erros = {**blocos(ler("relatorio-parte1.md")), **blocos(ler("relatorio-parte1b.md"))}
assert sorted(erros) == list(range(1, 14)), sorted(erros)
texto = ler("relatorio-topo.md") + "\n".join(erros[n] for n in range(1, 14))
t1, t2 = ler("relatorio-parte2.md"), ler("relatorio-parte2b.md")
cabeca = t1[:t1.index("### Erro")]
tec = {**blocos(t1), **blocos(t2)}
assert sorted(tec) == list(range(1, 14)), sorted(tec)
resto = t2[t2.index("### Arquivo gravado"):]
texto += "\n---\n\n" + cabeca + "\n".join(tec[n] for n in range(1, 14)) + "\n" + resto
for chave, valor in (("RESUMO_LISTA", ler("resumo.md").strip()),
                     ("SINO_RESULTADO", ler("sino-samuel.md").strip()),
                     ("SINO_D", ler("sino-gerente.md").strip())):
    texto = texto.replace(chave, valor)
# o markdown só abre uma lista depois de uma linha em branco: põe a linha antes do 1º item
linhas, saida = texto.split("\n"), []
for linha in linhas:
    if re.match(r"(- |\d+\. )", linha) and saida and saida[-1].strip() \
            and not re.match(r"(- |\d+\. |  )", saida[-1]):
        saida.append("")
    saida.append(linha)
texto = "\n".join(saida)
assert not re.search(r"\b(RESUMO_LISTA|SINO_RESULTADO|SINO_D|MAO_\w+)\b", texto)
print(relatorio.gravar(texto, PASTA / "relatorio"))
