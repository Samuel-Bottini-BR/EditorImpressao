"""Monta a proposta (proposta.md/.html/.pdf) e o pedido de exemplo a partir dos dados dos esboços.

Só desta proposta (18/11/2026); não está ligado em nada. Roda da cópia regras-agentes:
    .venv\\Scripts\\python.exe relatorios\\regras-agentes-2026-11-18\\esbocos\\montar_proposta.py <cópia do obra>
A cópia do obra dá o Livro com as decisões de 17 e 18/11 e o índice da memória.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parent.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ))
import catalogo as c  # noqa: E402
import montar_pacote  # noqa: E402
import relatorio  # noqa: E402
import tabela_arquivos  # noqa: E402

OBRA = Path(sys.argv[1] if len(sys.argv) > 1 else RAIZ.parent / "obra-juncao")
LIVRO = OBRA / "docs/plano/DECISOES.md"
DECISOES_DO_PEDIDO = ["D-767", "D-775", "D-605", "D-637", "D-741", "D-763", "D-717", "D-771"]
ARQUIVOS_DO_PEDIDO = ["novo:core/windows.py", "novo:tests/test_windows.py"]

PEDIDO = """> Você é o **implementador** do Editor de Impressão. Não abra outros agentes.
>
> **Trabalho:** escrever o porteiro do Windows e a pasta segura (peças 1 e 2), a peça única que todo o programa vai
> usar para pedir licença, lançar processo, rodar comando, mexer em tarefa e ler como o Windows está. Vem do plano da
> parte do Windows (`relatorios/plano-windows-2026-11-18/plano.md`, ramo `plano-windows-2026-11-18`): seção 1.2, peças
> 1 e 2; seção 2, defeitos 1 a 16; seção 3, passos 1 e 2.
> **Cópia e ramo:** `.claude/worktrees/porteiro-windows`, ramo `porteiro-windows-<data>`, a partir de `<commit do obra>`.
> Relatório em `relatorios/porteiro-windows-<data>/`.
> **Arquivos:** `core/windows.py` (novo) e `tests/test_windows.py` (novo). Mexer fora deles: pare e me avise (o pacote muda).
> **Fica de fora:** nenhum chamador muda ainda (o atualizador e os testes à distância passam a usar o porteiro nos
> passos 3 e 4). Nada roda no Windows de verdade neste trabalho: a prova à vista é a sessão A, que a gerente marca
> com o Samuel depois do agente que tenta quebrar.
> **Pronto quer dizer:** o formulário passa na etapa "antes de quem tenta quebrar"; o script da sessão A fica descrito
> no ONDE-PAREI (o que cada linha da janela de prova vai mostrar).
> **Leia:** este pacote inteiro; as seções do plano acima; as fichas `memoria/geral/ambiente.md` e
> `memoria/licoes.md` (parte D). O CLAUDE.md só nas seções que o pacote cita, quando tiver dúvida.
"""


def tabela_catalogo() -> str:
    """O catálogo em tabela."""
    linhas = ["| # | Regra | Onde | Etiquetas | Papel | Máquina | Repete / contra |", "|---|---|---|---|---|---|---|"]
    for r in c.REGRAS:
        onde = "; ".join(o.replace("CLAUDE.md ", "C ").replace(".md", "") for o in r["onde"])
        rep = r.get("rep", "")
        if r.get("contra"):
            rep = (rep + " · " if rep else "") + r["contra"]
        linhas.append(f"| {r['id']} | {r['nome']} | {onde} | {' '.join(r['tags'])} | {r['papel']} | {r['maq']} | {rep} |")
    return "\n".join(linhas)


def lista(d: dict) -> str:
    """Um dicionário de apontamentos em lista."""
    quem = {}
    for r in c.REGRAS:
        if r.get("contra"):
            quem.setdefault(r["contra"], []).append(r["id"])
    return "\n".join(f"- **{k}.** {v}" + (f" (regras {', '.join(quem[k])})" if k in quem else "") for k, v in d.items())


def tabela_de_arquivos() -> str:
    """A tabela de arquivos → etiquetas."""
    linhas = ["| Arquivo ou pasta | Etiquetas | Por quê |", "|---|---|---|"]
    for padrao, tags, porque in tabela_arquivos.TABELA:
        reserva = " (reserva)" if padrao in tabela_arquivos.RESERVA else ""
        linhas.append(f"| `{padrao}`{reserva} | {' '.join(tags)} | {porque} |")
    return "\n".join(linhas)


def secoes(texto: str) -> dict[str, int]:
    """Tamanho de cada seção '## ' do pacote."""
    partes = re.split(r"^## ", texto, flags=re.M)
    return {p.splitlines()[0][:2]: len(p) for p in partes[1:]}


def main() -> None:
    """Monta tudo e grava."""
    n = c.contar()
    pacote = montar_pacote.montar("implementador", LIVRO,
                                  "o porteiro do Windows e a pasta segura (passo 1 do plano da parte do Windows)",
                                  DECISOES_DO_PEDIDO, ARQUIVOS_DO_PEDIDO, OBRA)
    (PASTA / "pacote-exemplo.md").write_text(pacote, encoding="utf-8")
    pedido = "# Pedido de exemplo: a peça nova do Windows\n\n" + PEDIDO + "\n" + pacote
    relatorio.gravar(pedido, PASTA / "pedido-exemplo")

    tam = secoes(pacote)
    c_claude = len((RAIZ / "CLAUDE.md").read_text(encoding="utf-8"))
    c_impl = len((RAIZ / ".claude/agents/implementador.md").read_text(encoding="utf-8"))
    c_ind = len((OBRA / "memoria/INDICE.md").read_text(encoding="utf-8"))
    extra = sum(len((OBRA / "memoria" / f).read_text(encoding="utf-8")) for f in
                ("geral/regras-de-trabalho.md", "geral/perguntas-abertas.md", "licoes.md"))
    hoje_min, hoje_max = c_claude + c_impl + c_ind, c_claude + c_impl + c_ind + extra
    c_regras = tam["1."] + tam["2."]
    n_trab = int(re.search(r"regras do seu trabalho \((\d+)\)", pacote).group(1))
    total_pedido = len(PEDIDO) + len(pacote)

    outros = []
    for papel, arqs, nome in [("layout", ["ui/tela_conferir.py", "ui/widgets/barra_girar.py", "tests/test_girar_na_tela.py"], "um trabalho de tela do girar"),
                              ("implementador", ["core/filtros.py", "tests/test_filtros_algoritmos.py"], "um trabalho no filtro"),
                              ("pesquisador", ["docs/pesquisa/velopack.md"], "uma pesquisa"),
                              ("quebrador", ["core/windows.py"], "o agente que tenta quebrar a peça do Windows")]:
        t = montar_pacote.montar(papel, LIVRO, "t", [], arqs, OBRA)
        k = int(re.search(r"regras do seu trabalho \((\d+)\)", t).group(1))
        outros.append(f"{nome}: {k} regras do trabalho e {len(t):,} caracteres sem as decisões".replace(",", "."))

    def mil(x):
        return f"{x / 1000:.1f}".replace(".", ",")

    def num(x):
        return f"{x:,}".replace(",", ".")

    rep = [r for r in c.REGRAS if len(r["onde"]) >= 2]
    kw = re.compile("diferen|acrescenta|parecid|resum|ainda diz|cada agente|cada um|só repete|lista mais|contradiz|"
                    "dizem test|listam seis|põe o Livro|obra", re.I)
    dif = [r for r in rep if kw.search(r["rep"]) or (r.get("contra") and "iguais" not in r["rep"])]
    valores = {
        "N_TOTAL": n["total"], "N_INFO": n["informacao"], "N_REP": n["repetidas"], "N_DIF": len(dif),
        "N_CONTRA": n["contradicoes"], "N_PEQ": n["diferencas"], "N_VENC": n["vencidas"],
        "N_GER": sum(1 for r in c.REGRAS if r["papel"] == "gerente"),
        "HOJE_MIN": mil(hoje_min).split(",")[0], "HOJE_MAX": mil(hoje_max).split(",")[0],
        "PAC_REGRAS": mil(c_regras), "PAC_N": n_trab, "PAC_TOTAL": mil(total_pedido),
        "RAZAO": round((c_claude + c_impl) / c_regras),
        "N_MAQ_SIM": n["maq"]["sim"], "N_MAQ_PARTE": n["maq"]["em parte"], "N_JA": 24, "N_ESTUDO": 14,
        "C_CLAUDE": num(c_claude), "C_IMPL": num(c_impl), "C_INDICE": num(c_ind),
        "HOJE_MIN_N": num(hoje_min), "HOJE_MAX_N": num(hoje_max), "C_SEMPRE": num(tam["1."]), "C_TRAB": num(tam["2."]),
        "C_REGRAS_N": num(c_regras), "C_DEC": num(tam["3."]) + " caracteres", "C_FORM": num(tam["4."]) + " caracteres",
        "PAC_TOTAL_N": num(total_pedido), "OUTROS": "; ".join(outros),
        "CATALOGO": tabela_catalogo(), "CONTRADICOES": lista(c.CONTRADICOES), "DIFERENCAS": lista(c.DIFERENCAS_PEQUENAS),
        "VENCIDAS": lista(c.VENCIDAS),
        "INFORMACAO": "\n".join(f"- {a}: {b} ({x})" for a, b, x in c.INFORMACAO),
        "SEMPRE": "\n".join(f"{s['n']}. **{s['titulo']}.** {s['texto']}\n   *Por que está aqui:* {s['porque']} "
                            f"(cobre {', '.join(s['cobre'])})" for s in c.SEMPRE),
        "TABELA": tabela_de_arquivos(),
        "PEDIDO": "\n".join("    " + l for l in (PEDIDO + "\n" + pacote).splitlines()),
    }
    texto = (PASTA / "proposta-base.md").read_text(encoding="utf-8")
    for k, v in valores.items():
        texto = texto.replace("{{" + k + "}}", str(v))
    sobra = re.findall(r"\{\{\w+\}\}", texto)
    assert not sobra, sobra
    relatorio.gravar(texto, PASTA / "proposta")
    print({k: v for k, v in valores.items() if len(str(v)) < 80})


if __name__ == "__main__":
    main()
