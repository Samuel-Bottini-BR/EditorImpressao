"""ESBOÇO (18/11/2026, proposta regras-agentes): confere o formulário da entrega no ONDE-PAREI de um agente.

NÃO está ligado em nada (nem gancho, nem teste, nem commit). Mostra como seria a camada 3 da proposta.

O que ele confere (máquina):
  - cada campo obrigatório para as etiquetas do trabalho existe e não está vazio nem com texto de enchimento;
  - "Arquivos criados ou alterados" bate com o `git diff --name-only` do ramo;
  - cada decisão citada existe no Livro e as palavras entre aspas estão lá, letra por letra;
  - cada decisão de "Decisões que esta tarefa precisa cumprir" volta em "Como cumpri cada uma";
  - testes e arquivos de print citados existem;
  - em "O que pode falhar", os seis casos de sempre aparecem (ou "não se aplica: motivo");
  - em "O que li da peça de fora", cada item tem fonte (endereço da internet ou arquivo:linha);
  - em "Perguntas para o Samuel", nenhuma palavra de dentro e o "O que você escolhe".
O que ele NÃO confere: se a resposta é verdadeira ou boa. Isso é do agente que tenta quebrar (D-775) e da gerente.

Uso (esboço): python conferir_entrega.py <ONDE-PAREI.md> <etapa: quebrar|prova|pronto> <etiquetas, por vírgula> <commit de partida>
Saída: lista do que falta; código 0 = passa, 2 = devolvido (é o código que um gancho do Claude Code usaria para não
deixar o agente terminar).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# (título da seção no ONDE-PAREI, etapa em que passa a ser obrigatório, etiquetas que o exigem: "*" = todas)
CAMPOS = [
    ("Arquivos que vou mexer", "quebrar", "*"),
    ("Decisões que esta tarefa precisa cumprir", "quebrar", "*"),
    ("O que já está escolhido e testado aqui", "quebrar", "*"),
    ("Como fica para quem usa e no livro", "quebrar", "*"),
    ("A causa, a regra e todos os caminhos", "quebrar", "*"),
    ("O que pode falhar e o que o programa faz", "quebrar", "WIN"),
    ("O que li da peça de fora e onde", "quebrar", "*"),
    ("O que foi feito", "quebrar", "*"),
    ("Arquivos criados ou alterados", "quebrar", "*"),
    ("Como cumpri cada uma", "quebrar", "*"),
    ("Testes", "quebrar", "*"),
    ("Caminho e função", "quebrar", "*"),
    ("Máquina ou olho", "quebrar", "*"),
    ("Ressalvas", "quebrar", "*"),
    ("Velocidade", "quebrar", "IMG"),
    ("Ideias e bugs", "quebrar", "*"),
    ("Perguntas para o Samuel", "quebrar", "*"),
    ("Commit", "quebrar", "*"),
    ("O que o agente que tentou quebrar achou", "prova", "*"),
    ("A prova de verdade", "pronto", "WIN"),
]
ETAPAS = ["quebrar", "prova", "pronto"]
ENCHIMENTO = re.compile(r"^\s*(-|—|\.\.\.|todo|a fazer|ver acima|idem|n/?a|tbd|\?)\s*$", re.I)
CASOS_DE_FALHA = ["licença", "internet", "disco cheio", '"não"', "arquivo preso", "desligar no meio"]
PALAVRAS_DE_DENTRO = re.compile(r"\bD-\d{3}\b(?!\))|\.py\b|\betapa \d|\bimplementador\b|\bverificador\b|\bpesquisador\b|\bobra\b", re.I)


def secoes(texto: str) -> dict[str, str]:
    """As seções '## Título' do ONDE-PAREI e o texto de cada uma."""
    partes = re.split(r"^##\s+(.+?)\s*$", texto, flags=re.M)
    return {partes[i].strip(): partes[i + 1].strip() for i in range(1, len(partes) - 1, 2)}


def vazio(corpo: str) -> bool:
    """Vazio ou só enchimento ('-', 'ver acima', 'TODO'...)."""
    linhas = [l for l in corpo.splitlines() if l.strip()]
    return not linhas or all(ENCHIMENTO.match(l.lstrip("-* ")) for l in linhas)


def conferir(caminho: Path, etapa: str, etiquetas: set[str], raiz: Path, livro: Path, base: str) -> list[str]:
    """A lista do que falta. Vazia = passa."""
    s = secoes(caminho.read_text(encoding="utf-8"))
    falta: list[str] = []
    for titulo, desde, quem in CAMPOS:
        if ETAPAS.index(etapa) < ETAPAS.index(desde):
            continue
        if quem != "*" and quem not in etiquetas:
            continue
        corpo = next((v for k, v in s.items() if k.lower().startswith(titulo.lower())), None)
        if corpo is None:
            falta.append(f"falta a seção '{titulo}'")
        elif vazio(corpo):
            falta.append(f"a seção '{titulo}' está vazia ou só com enchimento")

    # Arquivos declarados x arquivos mexidos de verdade.
    declarados = set(re.findall(r"`([^`]+\.[a-z0-9]+)`", s.get("Arquivos criados ou alterados", "")))
    # A base é o commit de onde o trabalho partiu (escrito no pedido e no ONDE-PAREI), nunca um ramo fixo:
    # em 18/11 o plano da parte do Windows partiu do obra, e comparar com o fase-1 deu 30 alarmes falsos.
    mexidos = set(subprocess.run(["git", "-c", "core.quotepath=false", "diff", "--name-only", f"{base}...HEAD"], cwd=raiz,
                                 capture_output=True, text=True, encoding="utf-8").stdout.splitlines())
    propria = caminho.parent.resolve().relative_to(raiz.resolve()).as_posix() + "/"   # a pasta do relatório não conta
    for a in sorted(m for m in mexidos - declarados if not m.startswith(propria)):
        falta.append(f"mexeu em {a} e não declarou")

    # Decisões: existem no Livro, as palavras estão lá, e cada uma volta em "Como cumpri".
    texto_livro = livro.read_text(encoding="utf-8") if livro.exists() else ""
    pedidas = s.get("Decisões que esta tarefa precisa cumprir", "")
    for numero, palavras in re.findall(r"(D-\d{3})[^\"\n]*\"([^\"]{12,})\"", pedidas):
        linha = next((l for l in texto_livro.splitlines() if l.startswith(f"| {numero} |")), "")
        if not linha:
            falta.append(f"{numero} não existe no Livro")
        elif palavras[:60] not in linha:
            falta.append(f"{numero}: as palavras entre aspas não estão no Livro assim (copie do Livro)")
    cumpridas = s.get("Como cumpri cada uma", "")
    for numero in sorted(set(re.findall(r"D-\d{3}", pedidas)) - set(re.findall(r"D-\d{3}", cumpridas))):
        falta.append(f"{numero} pedida e sem 'como cumpri'")

    # Testes e prints citados existem.
    for nome in re.findall(r"`(tests/[^`]+\.py)", " ".join(s.values())):
        if not (raiz / nome).exists():
            falta.append(f"o teste citado {nome} não existe")
    for img in re.findall(r"\(([^)\s]+\.png)\)", " ".join(s.values())):
        if not (caminho.parent / img).exists():
            falta.append(f"o print citado {img} não existe")

    # Windows: os seis casos de falha e a fonte de cada peça de fora.
    if "WIN" in etiquetas:
        falhas = s.get("O que pode falhar e o que o programa faz", "").lower()
        for caso in CASOS_DE_FALHA:
            if caso not in falhas:
                falta.append(f"'O que pode falhar' não fala de: {caso} (ou escreva 'não se aplica: motivo')")
    for item in [l for l in s.get("O que li da peça de fora e onde", "").splitlines() if l.lstrip().startswith("-")]:
        if not re.search(r"https?://|\w+\.\w+:\d+", item):
            falta.append(f"peça de fora sem fonte (endereço ou arquivo:linha): {item.strip()[:60]}")

    # Perguntas no jeito do Samuel (§11.13): só o que dá para ver por máquina.
    perguntas = s.get("Perguntas para o Samuel", "")
    if perguntas and not re.match(r"^\s*-?\s*nenhuma", perguntas, re.I):
        for bloco in re.split(r"^###\s+", perguntas, flags=re.M)[1:]:
            titulo = bloco.splitlines()[0][:50]
            if PALAVRAS_DE_DENTRO.search(bloco):
                falta.append(f"pergunta '{titulo}': tem palavra de dentro ({PALAVRAS_DE_DENTRO.search(bloco).group(0)})")
            if "o que você escolhe" not in bloco.lower():
                falta.append(f"pergunta '{titulo}': falta 'O que você escolhe'")
            if not re.search(r"\.png\)", bloco):
                falta.append(f"pergunta '{titulo}': sem print")
            if "sugest" not in bloco.lower():
                falta.append(f"pergunta '{titulo}': sem a sugestão")
    return falta


if __name__ == "__main__":
    arquivo, etapa, tags = Path(sys.argv[1]), sys.argv[2], set(sys.argv[3].split(","))
    base = sys.argv[4] if len(sys.argv) > 4 else "fase-1"
    raiz = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=arquivo.parent, capture_output=True,
                               text=True).stdout.strip())
    resultado = conferir(arquivo, etapa, tags, raiz, raiz / "docs/plano/DECISOES.md", base)
    for r in resultado:
        print("DEVOLVIDO:", r, file=sys.stderr)
    sys.exit(2 if resultado else 0)
