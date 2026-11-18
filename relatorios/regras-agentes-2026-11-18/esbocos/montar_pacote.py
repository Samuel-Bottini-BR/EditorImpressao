"""ESBOÇO (18/11/2026, proposta regras-agentes): monta o pacote de regras de um trabalho (camada 2 da proposta).

NÃO está ligado em nada. A gerente diria: o papel do agente, os arquivos que o trabalho mexe (os que existem e os
novos) e as decisões do Livro que o pedido toca. O programa devolve o texto que o agente recebe:
  1. as regras "sempre" (10);
  2. as regras das etiquetas que saem dos arquivos (tabela_arquivos.py), só as do papel dele, sem as da gerente;
  3. as decisões, com as palavras copiadas do Livro (nunca de memória);
  4. o formulário da entrega com os campos que essas etiquetas exigem (conferir_entrega.py);
  5. o que ele NÃO recebeu e por quê (para ele saber quando parar e pedir o pacote de novo).

Uso (esboço): python montar_pacote.py <papel> <livro DECISOES.md> <titulo> <D-nnn,D-nnn> <arquivo> [arquivo ...]
  arquivo novo: prefixo "novo:" (ex.: novo:core/windows.py); a pasta do relatório do próprio trabalho não conta.
Seguro mexer: o texto em volta. Arriscado: a escolha das regras (escolher_regras), que decide o que o agente lê.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import catalogo  # noqa: E402
import conferir_entrega  # noqa: E402
import tabela_arquivos  # noqa: E402

PAPEIS = {"implementador": {"todos", "codigo"}, "layout": {"todos", "codigo", "layout"},
          "verificador": {"todos", "verif"}, "pesquisador": {"todos", "pesq"},
          "quebrador": {"todos", "codigo", "verif", "layout", "pesq"}}


def etiquetas(arquivos: list[str], raiz: Path) -> tuple[set, list[str]]:
    """As etiquetas do trabalho e os avisos (arquivo fora da tabela)."""
    tags, avisos = set(), []
    for a in arquivos:
        novo = a.startswith("novo:")
        caminho = a.removeprefix("novo:")
        conteudo = "" if novo or not (raiz / caminho).exists() else (raiz / caminho).read_text(encoding="utf-8", errors="replace")
        t, casou = tabela_arquivos.etiquetas_do_arquivo(caminho, conteudo)
        if not casou:
            avisos.append(f"{caminho} não está na tabela: recebe todas as regras e a gerente é avisada")
        tags |= t
    tags.add("GIT")      # todo trabalho faz commit no seu ramo
    return tags, avisos


def escolher_regras(tags: set, papel: str) -> list[dict]:
    """As regras do catálogo para estas etiquetas e este papel, sem as que o 'sempre' já cobre."""
    cobertas = {i for s in catalogo.SEMPRE for i in s["cobre"]} | {"R135"}   # R135: o formulário substitui
    quem = PAPEIS[papel]
    if papel == "quebrador":          # o agente que tenta quebrar recebe a lista completa (D-775)
        tags = set(catalogo.ETIQUETAS) - {"GER"}
    saida = []
    for r in catalogo.REGRAS:
        if r["papel"] not in quem or r["id"] in cobertas:
            continue
        # Regra com assunto (tela, Windows, imagem, perguntas, git, pesquisa) só vai se o trabalho tem esse assunto;
        # regra só de "todo trabalho" ou só de "testes" vai sempre que o trabalho tem testes ou é de todo trabalho.
        assunto = set(r["tags"]) - {"TODO", "TESTE", "GER"}
        if "GER" in r["tags"] and not assunto and "TODO" not in r["tags"]:
            continue
        if assunto:
            if assunto & tags:
                saida.append(r)
        elif "TODO" in r["tags"] or ("TESTE" in r["tags"] and "TESTE" in tags):
            saida.append(r)
    return saida


def decisoes_do_livro(livro: Path, numeros: list[str]) -> list[str]:
    """Para cada número, as palavras dele e o 'na prática' em negrito, copiados da linha do Livro."""
    linhas = livro.read_text(encoding="utf-8").splitlines()
    saida = []
    for n in numeros:
        linha = next((l for l in linhas if l.startswith(f"| {n} |")), None)
        if linha is None:
            saida.append(f"- **{n}**: NÃO ACHADA NO LIVRO (a gerente confere antes de mandar)")
            continue
        col = [c.strip() for c in linha.split(" | ")]
        palavras = col[2]
        pratica = col[3].replace("**", "")
        if len(pratica) > 700:
            pratica = pratica[:700].rsplit(" ", 1)[0] + " [...]"
        saida.append(f"- **{n}** ({col[1]}): {palavras}\n  Na prática: {pratica}")
    return saida


def campos_do_formulario(tags: set) -> list[str]:
    """Os campos obrigatórios do formulário para estas etiquetas, na ordem e com a etapa."""
    nomes = {"quebrar": "antes de ir ao agente que tenta quebrar", "prova": "antes da prova à vista",
             "pronto": "antes de 'pronto para conferir'"}
    return [f"- [ ] **{t}** ({nomes[e]})" for t, e, q in conferir_entrega.CAMPOS if q == "*" or q in tags]


def montar(papel: str, livro: Path, titulo: str, numeros: list[str], arquivos: list[str], raiz: Path) -> str:
    """O texto do pacote."""
    tags, avisos = etiquetas(arquivos, raiz)
    regras = escolher_regras(tags, papel)
    nomes = ", ".join(catalogo.ETIQUETAS[t] for t in sorted(tags) if t in catalogo.ETIQUETAS and t != "GER")
    fora = sorted(set(catalogo.ETIQUETAS) - tags - {"GER", "TODO"})
    p = [f"# Pacote de regras: {titulo}", "",
         f"Papel: **{papel}**. Arquivos: {', '.join('`' + a.removeprefix('novo:') + '`' + (' (novo)' if a.startswith('novo:') else '') for a in arquivos)}.",
         f"Tipo de trabalho (sai dos arquivos): {nomes}.", ""]
    p += [f"> Aviso: {a}" for a in avisos]
    p += ["## 1. Sempre (todo trabalho)", ""]
    for s in catalogo.SEMPRE:
        p.append(f"{s['n']}. **{s['titulo']}.** {s['texto']} *Por quê:* {s['porque']}")
    p += ["", f"## 2. As regras do seu trabalho ({len(regras)})", ""]
    por_tag: dict[str, list] = {}
    for r in regras:
        chave = next((t for t in ("WIN", "TELA", "IMG", "TESTE", "PERG", "GIT", "PESQ", "TODO") if t in r["tags"] and t in tags | {"TODO"}), "TODO")
        por_tag.setdefault(chave, []).append(r)
    for t in ("WIN", "TELA", "IMG", "TESTE", "PERG", "GIT", "PESQ", "TODO"):
        if t in por_tag:
            p.append(f"**{catalogo.ETIQUETAS[t].capitalize()}**")
            for r in por_tag[t]:
                aviso = (" **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**"
                         if r.get("contra", "") in catalogo.CONTRADICOES else "")
                p.append(f"- {r['nome']}: {r['curta']} ({r['onde'][0]}){aviso}")
            p.append("")
    p += ["## 3. As decisões que este trabalho precisa cumprir (copiadas do Livro)", ""]
    p += decisoes_do_livro(livro, numeros) if numeros else ["- (a gerente põe aqui as decisões do pedido)"]
    p += ["", "## 4. O formulário da entrega (no seu ONDE-PAREI; um programa confere, campo vazio volta)", ""]
    p += campos_do_formulario(tags)
    p += ["", "## 5. O que você não recebeu, e quando parar", "",
          f"Este pacote não traz as regras de: {', '.join(catalogo.ETIQUETAS[t] for t in fora) or 'nada (recebeu todas)'}. "
          "Se precisar mexer num arquivo fora da lista acima, pare e avise a gerente: o pacote muda. "
          "Se tiver pergunta para o Samuel, a regra 8 acima é o mínimo; a lista inteira está no CLAUDE.md §11.13, e a "
          "gerente devolve a pergunta que não passar. "
          "O texto que vale é o do CLAUDE.md: a fonte de cada regra está entre parênteses; leia lá quando tiver dúvida.", ""]
    return "\n".join(p)


if __name__ == "__main__":
    papel, livro, titulo, numeros, *arquivos = sys.argv[1:]
    texto = montar(papel, Path(livro), titulo, [n for n in numeros.split(",") if n], arquivos, Path.cwd())
    sys.stdout.reconfigure(encoding="utf-8")
    print(texto)
    print(f"\n<!-- {len(texto)} caracteres -->")
