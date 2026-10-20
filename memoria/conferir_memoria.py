"""Confere a memória do projeto (pasta memoria/) contra o plano.

O que é: um script de Python puro (só biblioteca padrão), pedido pela gerente
em 19/10/2026 junto com a memória por assunto (CLAUDE.md §4.9). Ele não muda
nada: só lê e avisa.

Como rodar (da pasta do projeto):

    .venv\\Scripts\\python.exe memoria\\conferir_memoria.py

Sai com código 0 quando não acha nada, 1 quando acha alguma coisa.

O que ele confere (três coisas):

1. **Links quebrados.** Todo link Markdown relativo `[texto](caminho)` dos
   arquivos .md da memória tem de apontar para um arquivo ou pasta que existe.
   Links da internet (http, https, mailto) e âncoras soltas (#...) não são
   conferidos. O que está entre crases (`...`) não é link e não é conferido:
   é assim que a memória escreve caminhos que ficam fora do git ou em outro
   ramo.
2. **Entradas do Registro de mudanças sem ficha.** Para cada linha do
   Registro (PLANO-DEFINITIVO.md, seção 7), o script acha os itens de que ela
   fala (números como 2.13, e palavras como "Para revisar", "layout", "G6",
   "Misto") e procura uma ficha desses itens (memoria/itens/) que cite a data
   da linha (dd/mm/aaaa ou dd/mm). Linha que não fala de item nenhum basta ser
   citada pela data em qualquer arquivo da memória (por exemplo, na
   LINHA-DO-TEMPO.md).
3. **Perguntas abertas já respondidas.** Para cada pergunta de
   geral/perguntas-abertas.md que tem um nome entre crases (ex.:
   `g7-borda-ate-onde`), o script olha a linha mais nova do Registro que cita
   esse nome; se ela diz "decidida", "respondida" e afins (e não diz "sem
   resposta" ou "aberta"), avisa que a pergunta parece já respondida.

O que é seguro mudar: as listas PALAVRAS_DOS_ITENS (palavra → ficha) e
PALAVRAS_DE_DECISAO. O que é arriscado: o formato que o script espera do
Registro (tabela "| dd/mm/aaaa | ... |" depois do título "## 7. Registro de
mudanças"); se o plano mudar esse formato, a conferência 2 deixa de achar as
linhas e passa a dizer que está tudo certo. Por isso o script avisa quando não
acha nenhuma linha.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

# Itens que existem no plano (seção 4 do PLANO-DEFINITIVO). "4" é a Fase 4
# inteira (layout); ela tem a ficha 4.md e a ficha layout.md.
ITENS_DO_PLANO = (
    [f"0.{n}" for n in range(1, 8)]
    + [f"1.{n}" for n in range(1, 7)]
    + [f"2.{n}" for n in range(1, 20)]
    + [f"3.{n}" for n in range(1, 10)]
    + ["5.1", "5.2"]
    + [f"6.{n}" for n in range(1, 9)]
    + [f"7.{n}" for n in range(1, 4)]
)

# Palavra que aparece numa linha do Registro → ficha que deve citá-la.
# Comparação sem diferenciar maiúscula de minúscula.
PALAVRAS_DOS_ITENS = {
    "para revisar": "para-revisar",
    "layout": "layout",
    "g6": "2.2",
    "endireitar": "2.2",
    "misto": "1.5",
    "só as letras": "1.5",
    "tirar o fundo": "1.1",
    "camadas": "1.1",
    "kraken": "1.3",
    "ocr": "1.3",
    "limpar pontinhos": "2.7",
    "dividir": "2.1",
    "girar": "2.3",
    "impressão": "2.6",
    "geometria": "2.13",
    "corte com borda preta": "2.13",
    "caixa do conteúdo": "2.5",
    "fase 0": "0.1",
    "preto e branco": "1.5",
}

PALAVRAS_DE_DECISAO = (
    "decidida",
    "decidido",
    "decididas",
    "respondida",
    "respondido",
    "respondidas",
    "fica assim",
    "aprovado",
)

PALAVRAS_DE_ABERTA = (
    "sem resposta",
    "aberta",
    "abertas",
    "ainda não entendi",
    "não entendi",
    "reaberta",
)

# Número de item: 2.13, 1.5... mas não 1.600 (milhar), não 0.2.69 (versão),
# não v1.2.1 e não 14.44.
_RE_ITEM = re.compile(r"(?<![\w.,])([0-7]\.\d{1,2})(?![\d.]\d)(?!\d)")
# "conferência 6.7" é o nome de uma conferência antiga, não o item 6.7.
_RE_CONFERENCIA = re.compile(r"confer[eê]ncia[\s-]+([0-7]\.\d{1,2})", re.IGNORECASE)
_RE_LINK = re.compile(r"!?\[(?:[^\]\\]|\\.)*\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
_RE_BLOCO_DE_CODIGO = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
_RE_CODIGO_NA_LINHA = re.compile(r"`[^`\n]*`")
_RE_DATA_REGISTRO = re.compile(r"^\|\s*(\d{2})/(\d{2})/(\d{4})\s*\|")
_RE_NOME_ENTRE_CRASES = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`")


@dataclass(frozen=True)
class LinkQuebrado:
    arquivo: Path
    linha: int
    alvo: str


@dataclass(frozen=True)
class EntradaDoRegistro:
    data: str  # dd/mm/aaaa
    texto: str
    linha: int


@dataclass(frozen=True)
class PerguntaRespondida:
    nome: str
    data: str
    trecho: str


def _sem_codigo(texto: str) -> str:
    """Troca blocos e trechos de código por espaços, mantendo as linhas."""

    def _branco(m: re.Match) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))

    texto = _RE_BLOCO_DE_CODIGO.sub(_branco, texto)
    return _RE_CODIGO_NA_LINHA.sub(_branco, texto)


def achar_links(texto: str) -> list[tuple[str, int]]:
    """Devolve (alvo, número da linha) de cada link Markdown fora de código."""
    achados = []
    for numero, linha in enumerate(_sem_codigo(texto).splitlines(), start=1):
        for m in _RE_LINK.finditer(linha):
            alvo = m.group(1).strip()
            if alvo.startswith("<") and alvo.endswith(">"):
                alvo = alvo[1:-1]
            achados.append((alvo, numero))
    return achados


def _e_link_de_fora(alvo: str) -> bool:
    minusculo = alvo.lower()
    return (
        minusculo.startswith(("http://", "https://", "mailto:", "file:"))
        or alvo.startswith("#")
        or alvo == ""
    )


def links_quebrados(pasta_memoria: Path) -> list[LinkQuebrado]:
    """Confere os links relativos de todos os .md dentro da pasta da memória."""
    quebrados = []
    for arquivo in sorted(pasta_memoria.rglob("*.md")):
        texto = arquivo.read_text(encoding="utf-8", errors="replace")
        for alvo, numero in achar_links(texto):
            if _e_link_de_fora(alvo):
                continue
            caminho = unquote(alvo.split("#", 1)[0])
            if not caminho:
                continue
            destino = (arquivo.parent / caminho).resolve()
            if not destino.exists():
                quebrados.append(LinkQuebrado(arquivo, numero, alvo))
    return quebrados


def ler_registro(caminho_plano: Path) -> list[EntradaDoRegistro]:
    """Lê as linhas da tabela do Registro de mudanças (seção 7 do plano)."""
    entradas = []
    dentro = False
    linhas = caminho_plano.read_text(encoding="utf-8", errors="replace").splitlines()
    for numero, linha in enumerate(linhas, start=1):
        if linha.startswith("## "):
            dentro = "registro de mudan" in linha.lower()
            continue
        if not dentro:
            continue
        m = _RE_DATA_REGISTRO.match(linha)
        if m:
            dia, mes, ano = m.groups()
            entradas.append(EntradaDoRegistro(f"{dia}/{mes}/{ano}", linha, numero))
    return entradas


def itens_da_entrada(texto: str) -> set[str]:
    """Fichas (nomes sem .md) de que uma linha do Registro fala."""
    conferencias = set(_RE_CONFERENCIA.findall(texto))
    itens = set()
    for numero in _RE_ITEM.findall(texto):
        if numero in ITENS_DO_PLANO and numero not in conferencias:
            itens.add(numero)
    minusculo = texto.lower()
    for palavra, ficha in PALAVRAS_DOS_ITENS.items():
        if palavra in minusculo:
            itens.add(ficha)
    return itens


def _cita_a_data(texto: str, data: str) -> bool:
    dia, mes, ano = data.split("/")
    padrao = rf"(?<!\d){dia}/{mes}(?:/{ano})?(?!\d)"
    return re.search(padrao, texto) is not None


def entradas_sem_ficha(
    pasta_memoria: Path, entradas: list[EntradaDoRegistro]
) -> list[tuple[EntradaDoRegistro, set[str]]]:
    """Linhas do Registro que nenhuma ficha (do item certo) cita pela data."""
    pasta_itens = pasta_memoria / "itens"
    textos_das_fichas = {}
    if pasta_itens.is_dir():
        for ficha in pasta_itens.glob("*.md"):
            textos_das_fichas[ficha.stem] = ficha.read_text(encoding="utf-8", errors="replace")
    todos_os_textos = [
        arquivo.read_text(encoding="utf-8", errors="replace")
        for arquivo in pasta_memoria.rglob("*.md")
    ]
    faltando = []
    for entrada in entradas:
        itens = itens_da_entrada(entrada.texto)
        if itens:
            achou = any(
                _cita_a_data(textos_das_fichas.get(item, ""), entrada.data) for item in itens
            )
        else:
            achou = any(_cita_a_data(texto, entrada.data) for texto in todos_os_textos)
        if not achou:
            faltando.append((entrada, itens))
    return faltando


def nomes_das_perguntas_abertas(caminho: Path) -> list[str]:
    """O primeiro nome entre crases de cada item de lista de perguntas-abertas.md."""
    if not caminho.exists():
        return []
    nomes = []
    for linha in caminho.read_text(encoding="utf-8", errors="replace").splitlines():
        if not linha.lstrip().startswith(("- ", "* ")):
            continue
        m = _RE_NOME_ENTRE_CRASES.search(linha)
        if m and m.group(1) not in nomes:
            nomes.append(m.group(1))
    return nomes


def _data_para_ordenar(data: str) -> tuple[int, int, int]:
    dia, mes, ano = (int(x) for x in data.split("/"))
    return (ano, mes, dia)


def perguntas_ja_respondidas(
    caminho_perguntas: Path, entradas: list[EntradaDoRegistro]
) -> list[PerguntaRespondida]:
    """Perguntas abertas cuja linha mais nova no Registro diz que foi decidida."""
    respondidas = []
    for nome in nomes_das_perguntas_abertas(caminho_perguntas):
        com_o_nome = [e for e in entradas if nome in e.texto]
        if not com_o_nome:
            continue
        mais_nova = max(com_o_nome, key=lambda e: (_data_para_ordenar(e.data), e.linha))
        texto = mais_nova.texto.lower()
        # Olha só o pedaço da linha perto do nome (uma linha do Registro
        # costuma falar de várias perguntas).
        pos = texto.find(nome)
        trecho = texto[max(0, pos - 40) : pos + len(nome) + 160]
        decidiu = any(p in trecho for p in PALAVRAS_DE_DECISAO)
        aberta = any(p in trecho for p in PALAVRAS_DE_ABERTA)
        if decidiu and not aberta:
            respondidas.append(
                PerguntaRespondida(nome, mais_nova.data, mais_nova.texto[pos : pos + 200])
            )
    return respondidas


def conferir(raiz: Path) -> tuple[str, int]:
    """Roda as três conferências e devolve (relatório em texto, nº de problemas)."""
    pasta_memoria = raiz / "memoria"
    plano = raiz / "docs" / "plano" / "PLANO-DEFINITIVO.md"
    partes = []
    problemas = 0

    quebrados = links_quebrados(pasta_memoria)
    partes.append(f"1. Links quebrados: {len(quebrados)}")
    for q in quebrados:
        partes.append(f"   - {q.arquivo.relative_to(raiz).as_posix()}:{q.linha} -> {q.alvo}")
    problemas += len(quebrados)

    entradas = ler_registro(plano) if plano.exists() else []
    if not entradas:
        partes.append(
            "2. ATENÇÃO: nenhuma linha do Registro de mudanças foi lida "
            f"({plano.relative_to(raiz).as_posix()}); a conferência 2 não valeu."
        )
        problemas += 1
    else:
        faltando = entradas_sem_ficha(pasta_memoria, entradas)
        partes.append(
            f"2. Entradas do Registro sem ficha que as cite: {len(faltando)} de {len(entradas)}"
        )
        for entrada, itens in faltando:
            onde = ", ".join(sorted(itens)) if itens else "nenhum item (procurada em toda a memória)"
            resumo = re.sub(r"\s+", " ", entrada.texto.split("|")[2])[:110].strip()
            partes.append(f"   - {entrada.data} (linha {entrada.linha}; itens: {onde}): {resumo}")
        problemas += len(faltando)

    perguntas = pasta_memoria / "geral" / "perguntas-abertas.md"
    respondidas = perguntas_ja_respondidas(perguntas, entradas)
    partes.append(
        f"3. Perguntas em perguntas-abertas.md que o Registro dá como respondidas: {len(respondidas)}"
    )
    for r in respondidas:
        trecho = re.sub(r"\s+", " ", r.trecho)
        partes.append(f"   - `{r.nome}`: Registro {r.data}: {trecho}")
    problemas += len(respondidas)

    partes.append("")
    partes.append("Tudo certo." if problemas == 0 else f"Problemas achados: {problemas}.")
    return "\n".join(partes), problemas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Confere a pasta memoria/ contra o plano.")
    parser.add_argument(
        "--raiz",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="pasta do projeto (de fábrica, a pasta acima de memoria/)",
    )
    args = parser.parse_args(argv)
    relatorio, problemas = conferir(args.raiz.resolve())
    saida = sys.stdout
    try:
        saida.reconfigure(encoding="utf-8")  # o console do Windows pode estar em cp1252
    except (AttributeError, ValueError):
        pass
    print(relatorio, file=saida)
    return 0 if problemas == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
