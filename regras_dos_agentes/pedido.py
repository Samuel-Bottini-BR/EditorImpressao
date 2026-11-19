"""A leitura única do pedido de um trabalho: o papel, o commit de partida, o ramo e os arquivos que ele pode mexer.

O pedido vai no pacote que a gerente manda (montado por `montar_pacote.py`) e o agente copia para o começo do
ONDE-PAREI, sem mudar, em duas seções:

    ## Pedido
    - Papel: implementador
    - Commit de partida: 746dbda6
    - Ramo: passo1-windows-2026-11-20

    ## Arquivos que vou mexer
    - `core/windows.py` (novo)
    - `tests/test_windows_*.py`
    - `relatorios/passo1/`

Cada item da lista é o primeiro texto entre crases da linha: um arquivo, uma pasta (termina em "/") ou um padrão com
"*". Daqui saem a lista de arquivos permitidos (D-796: o porteiro barra o agente de tela que mexer em `core/` fora dela,
K13) e as etiquetas do trabalho. `coberto` é o lugar único que diz se um arquivo mexido está na lista.

Seguro mexer: aceitar outro jeito de escrever o papel. Arriscado: `coberto` (o que conta como "está na lista").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from fnmatch import fnmatch

PAPEIS = ("implementador", "layout", "verificador", "pesquisador", "quebrador")


def secoes(texto: str) -> dict[str, str]:
    """As seções `## Título` de um arquivo Markdown e o texto de cada uma (títulos sem espaço sobrando)."""
    partes = re.split(r"^##\s+(.+?)\s*$", texto.replace("\r\n", "\n"), flags=re.M)
    resultado: dict[str, str] = {}
    for i in range(1, len(partes) - 1, 2):
        resultado.setdefault(partes[i].strip(), partes[i + 1].strip())
    return resultado


def secao(texto_ou_secoes: str | dict[str, str], titulo: str) -> str | None:
    """O texto da seção cujo título começa com `titulo` (sem diferença de maiúscula), ou None se não houver."""
    s = secoes(texto_ou_secoes) if isinstance(texto_ou_secoes, str) else texto_ou_secoes
    return next((v for k, v in s.items() if k.lower().startswith(titulo.lower())), None)


@dataclass
class Pedido:
    """O que o pedido diz: papel, partida, ramo e a lista de arquivos (como está escrita)."""

    papel: str = ""
    partida: str = ""
    ramo: str = ""
    arquivos: list[str] = field(default_factory=list)
    problemas: list[str] = field(default_factory=list)

    def bloco(self) -> str:
        """As duas seções que o agente copia para o ONDE-PAREI (o mesmo texto que `ler` lê)."""
        linhas = ["## Pedido", "", f"- Papel: {self.papel}", f"- Commit de partida: {self.partida}",
                  f"- Ramo: {self.ramo}", "", "## Arquivos que vou mexer", ""]
        linhas += [f"- `{a.removeprefix('novo:')}`" + (" (novo)" if a.startswith("novo:") else "")
                   for a in self.arquivos]
        return "\n".join(linhas) + "\n"


def lista_de_arquivos(corpo: str) -> list[str]:
    """Os caminhos de uma lista Markdown: o primeiro texto entre crases de cada item."""
    saida = []
    for l in corpo.splitlines():
        m = re.match(r"^\s*[-*]\s+`([^`]+)`", l)
        if m:
            saida.append(m.group(1).strip().replace("\\", "/"))
    return saida


def ler(texto: str) -> Pedido:
    """Lê o pedido de um ONDE-PAREI (ou de um pacote); o que faltar vai para `problemas`, nunca é adivinhado."""
    s = secoes(texto)
    p = Pedido()
    corpo = secao(s, "Pedido") or ""
    for chave, atributo in (("papel", "papel"), ("commit de partida", "partida"), ("ramo", "ramo")):
        m = re.search(rf"^\s*-\s*{chave}\s*:\s*`?([^`\n]+?)`?\s*$", corpo, re.I | re.M)
        if m:
            setattr(p, atributo, m.group(1).strip())
        else:
            p.problemas.append(f"o pedido não diz '{chave}' (seção 'Pedido')")
    if p.papel and p.papel not in PAPEIS:
        p.problemas.append(f"papel desconhecido: {p.papel} (vale: {', '.join(PAPEIS)})")
    arquivos = secao(s, "Arquivos que vou mexer")
    if arquivos is None:
        p.problemas.append("falta a seção 'Arquivos que vou mexer'")
    else:
        p.arquivos = lista_de_arquivos(arquivos)
        if not p.arquivos:
            p.problemas.append("a seção 'Arquivos que vou mexer' não tem nenhum caminho entre crases")
    return p


def titulo_do_pacote(texto: str) -> str:
    """O título do pacote ("# Pacote de regras: <título>"), que diz em palavras o que o trabalho faz."""
    m = re.search(r"^#\s+Pacote de regras:\s*(.+)$", texto, re.M)
    return m.group(1).strip() if m else ""


def coberto(caminho: str, permitidos: list[str]) -> bool:
    """O arquivo mexido está na lista? (o mesmo arquivo, dentro de uma pasta da lista, ou num padrão com "*")."""
    for p in permitidos:
        p = p.removeprefix("novo:")
        if caminho == p or (p.endswith("/") and caminho.startswith(p)) or ("*" in p and fnmatch(caminho, p)):
            return True
    return False
