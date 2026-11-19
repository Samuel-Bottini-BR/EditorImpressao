"""O formulário da entrega (D-792; K19, K20, K21) e o relatório de quem tenta quebrar (D-775).

Palavras do Samuel (D-792, 18/11): "mas e o que vai determinar o que vai nesse formulario? vai ser feito um toda vez que
for enviado um trabalho para um agente?" · "ok". Um formulário só, fixo (F1 a F20 da proposta das regras, §6), mais as
perguntas das etiquetas do trabalho (Windows: quantas perguntas do Windows o Samuel vê; tela: qual print prova; imagem:
em quais páginas foi conferido), montado pela mesma tabela do pacote. O agente preenche no próprio ONDE-PAREI, com os
títulos de seção daqui (`CAMPOS`, o lugar único dos títulos).

Três etapas (a mesma conferência, mais exigente a cada uma):
- `quebrar`: antes de ir ao agente que tenta quebrar;
- `prova`: antes da prova à vista na tela do Samuel (exige o relatório de quem quebrou, F19);
- `pronto`: antes de quem confere escrever o rótulo de pronto para conferir (exige a prova de verdade, F20, no Windows).

O programa vê se cada campo existe, não está vazio nem só com enchimento, e bate com o código, o Livro, o git e o
GitHub. **Não vê se a resposta é boa nem verdadeira**: isso é de quem tenta quebrar e da gerente.

Junto, em toda etapa, roda o porteiro das mudanças (`porteiro_mudancas.py`: K09 a K15, K17, K18).

Quem tenta quebrar (papel "quebrador") preenche, no lugar do formulário, os seis campos do relatório dele
(`CAMPOS_DE_QUEM_QUEBRA`); o mesmo programa confere. O relatório dele vai para o ramo de quem construiu, numa subpasta
da pasta do trabalho (`relatorios/<trabalho>/quem-quebrou/`), e o F19 cita esse arquivo: assim o formulário de quem
construiu acha o relatório, e ele não conta como arquivo mexido pelo trabalho.

Resultado: `problemas` (devolve ao agente), `avisos` (não barram; vão para quem quebra) e `pendentes` (o que não deu
para conferir, ex.: o GitHub sem resposta). Com pendente, o código de saída é 3 ("não conferiu"), nunca 0.

Seguro mexer: as frases. Arriscado: os títulos de `CAMPOS` (todo ONDE-PAREI usa), o que conta como enchimento e as
conferências de cada campo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

from . import conversa_com_o_git as git
from . import conversa_com_o_github as github
from . import pedido as pedido_
from . import porteiro_mudancas, tabela_arquivos
from .livro import NUMERO, Livro
from .porteiro import FORA_DO_PROJETO
from .porteiro_mudancas import QUEM_CONFERE

ETAPAS = ("quebrar", "prova", "pronto")
NOME_DAS_ETAPAS = {"quebrar": "antes de ir ao agente que tenta quebrar", "prova": "antes da prova à vista",
                   "pronto": "antes do rótulo de pronto para conferir"}

# (código, título da seção no ONDE-PAREI, etapa em que passa a ser obrigatório, etiqueta que o exige: "*" = todas)
CAMPOS: list[tuple[str, str, str, str]] = [
    ("F1", "Arquivos que vou mexer", "quebrar", "*"),
    ("F2", "Decisões que esta tarefa precisa cumprir", "quebrar", "*"),
    ("F3", "O que já está escolhido e testado aqui", "quebrar", "*"),
    ("F4", "Como fica para quem usa e no livro", "quebrar", "*"),
    ("F5", "A causa, a regra e todos os caminhos", "quebrar", "*"),
    ("F6", "O que pode falhar e o que o programa faz", "quebrar", "WIN"),
    ("F7", "O que li da peça de fora e onde", "quebrar", "*"),
    ("F8", "O que foi feito", "quebrar", "*"),
    ("F9", "Arquivos criados ou alterados", "quebrar", "*"),
    ("F10", "Como cumpri cada uma", "quebrar", "*"),
    ("F11", "Testes", "quebrar", "*"),
    ("F12", "Caminho e função", "quebrar", "*"),
    ("F13", "Máquina ou olho", "quebrar", "*"),
    ("F14", "Ressalvas", "quebrar", "*"),
    ("F15", "Velocidade", "quebrar", "IMG"),
    ("F16", "Ideias e bugs", "quebrar", "*"),
    ("F17", "Perguntas para o Samuel", "quebrar", "*"),
    ("F18", "Commit", "quebrar", "*"),
    ("F19", "O que o agente que tentou quebrar achou", "prova", "*"),
    ("F20", "A prova de verdade", "pronto", "WIN"),
    # As perguntas das etiquetas (D-792): uma por tipo de trabalho, nas palavras da decisão.
    ("E-WIN", "Perguntas do Windows que o Samuel vê", "quebrar", "WIN"),
    ("E-TELA", "O print que prova", "quebrar", "TELA"),
    ("E-IMG", "Páginas em que foi conferido", "quebrar", "IMG"),
]

# Os seis campos do relatório de quem tenta quebrar (proposta das regras, §6).
CAMPOS_DE_QUEM_QUEBRA: list[tuple[str, str]] = [
    ("Q1", "O que li"),
    ("Q2", "O que conferi nas falhas, nas peças de fora e nos caminhos"),
    ("Q3", "Caminhos que o outro não listou"),
    ("Q4", "Falhas não pensadas e resultado não conferido"),
    ("Q5", "As regras que conferi"),
    ("Q6", "Achados"),
]

ENCHIMENTO = re.compile(r"^\s*(-|—|\.\.\.|…|todo|a fazer|a preencher.*|ver acima|idem|n/?a|tbd|\?|\(a preencher.*\))\s*$",
                        re.I)
NAO_SE_APLICA = re.compile(r"^\s*n[ãa]o se aplica\s*[:,-]\s*(.{10,})", re.I | re.M)
CASOS_DE_FALHA = [("sem licença", r"licen[çc]a"), ("sem internet", r"internet"), ("disco cheio", r"disco cheio"),
                  ("a pessoa diz \"Não\"", r"[\"“']n[ãa]o[\"”']"), ("arquivo preso", r"arquivo preso"),
                  ("desligar no meio", r"desligar no meio")]
PALAVRAS_DE_DENTRO = re.compile(r"\bD-\d{3}\b(?!\))|\.py\b|\betapa \d|\bimplementador\b|\bverificador\b|"
                                r"\bpesquisador\b|\bobra\b|\bK\d\d\b|\bF\d{1,2}\b", re.I)
RODADA = re.compile(r"\b\d{9,12}\b")
COMMIT = re.compile(r"\b[0-9a-f]{7,40}\b")


@dataclass
class Resultado:
    """O que a conferência achou: problemas (volta ao agente), avisos e pendentes (o que não deu para conferir)."""

    etapa: str
    problemas: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    pendentes: list[str] = field(default_factory=list)

    @property
    def codigo_de_saida(self) -> int:
        """0 = passou; 1 = devolvido; 3 = não deu para conferir tudo (nunca 0 com pendente)."""
        return 1 if self.problemas else 3 if self.pendentes else 0

    def explicar(self) -> str:
        """O resultado em português, uma linha por coisa."""
        linhas = [f"DEVOLVIDO: {p}" for p in self.problemas]
        linhas += [f"NÃO CONFERIDO: {p}" for p in self.pendentes]
        linhas += [f"AVISO: {a}" for a in self.avisos]
        if self.problemas:
            fim = f"O formulário volta ao agente ({len(self.problemas)} coisa(s) a acertar)."
        elif self.pendentes:
            fim = "Não deu para conferir tudo: o formulário ainda não passa."
        else:
            fim = f"O formulário passa na etapa \"{NOME_DAS_ETAPAS[self.etapa]}\"."
        return "\n".join(linhas + [fim])


def vazio(corpo: str | None) -> bool:
    """Vazio, só enchimento ("-", "ver acima", "a preencher"...) ou "não se aplica" sem o motivo."""
    if corpo is None:
        return True
    linhas = [l.strip() for l in corpo.splitlines() if l.strip()]
    if not linhas:
        return True
    if all(not l.lstrip("-* ") or ENCHIMENTO.match(l.lstrip("-* ")) for l in linhas):
        return True
    junto = " ".join(linhas)
    if re.match(r"^\s*-?\s*n[ãa]o se aplica\b", junto, re.I) and not NAO_SE_APLICA.search(junto.lstrip("-* ")):
        return True
    return False


def nao_se_aplica(corpo: str) -> bool:
    """O campo diz "não se aplica: motivo" (com o motivo)."""
    return bool(NAO_SE_APLICA.search(corpo.lstrip("-* ")))


def _itens(corpo: str) -> list[str]:
    """Os itens de uma lista Markdown (linhas que começam com "-" ou número), com as linhas de continuação juntas."""
    itens: list[str] = []
    for l in corpo.splitlines():
        if re.match(r"^[-*]\s+|^\d+[.)]\s+", l):
            itens.append(l)
        elif itens and l.strip():
            itens[-1] += " " + l.strip()
    return itens


def _citacoes(texto: str) -> list[str]:
    """Os trechos entre aspas retas ou curvas com 12 letras ou mais (as palavras do Samuel)."""
    return [a or b for a, b in re.findall(r"\"([^\"]{12,}?)\"|“([^”]{12,}?)”", texto)]


class _Repositorio:
    """O que o formulário precisa saber do repositório, lido uma vez (os arquivos do git e as funções definidas)."""

    def __init__(self, raiz: Path):
        """Guarda a raiz e a lista de arquivos do git; as funções definidas só são lidas se alguém pedir."""
        self.raiz = raiz
        self.arquivos = git.arquivos_do_git(raiz)
        self._definidos: set[str] | None = None

    def existe(self, padrao: str) -> bool:
        """Há arquivo do git com esse caminho (ou que casa com esse padrão com "*")?"""
        return any(c == padrao or fnmatch(c, padrao) for c in self.arquivos) or (self.raiz / padrao).exists()

    def definidos(self) -> set[str]:
        """Os nomes de função e de classe definidos nos `.py` do git."""
        if self._definidos is None:
            nomes: set[str] = set()
            for c in self.arquivos:
                if c.endswith(".py") and c.split("/")[0] not in FORA_DO_PROJETO:
                    try:
                        texto = (self.raiz / c).read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        continue
                    nomes |= set(re.findall(r"^\s*(?:async\s+)?(?:def|class)\s+(\w+)", texto, re.M))
            self._definidos = nomes
        return self._definidos

    def teste_existe(self, citado: str) -> bool:
        """`tests/x.py` ou `tests/x.py::test_y` existe (o arquivo e, se dito, a função)?"""
        arquivo, _, funcao = citado.partition("::")
        if not self.existe(arquivo):
            return False
        if not funcao:
            return True
        nome = funcao.split("::")[-1].split("[")[0]
        for c in self.arquivos:
            if c == arquivo or fnmatch(c, arquivo):
                texto = (self.raiz / c).read_text(encoding="utf-8", errors="replace")
                if re.search(rf"^\s*def\s+{re.escape(nome)}\b", texto, re.M):
                    return True
        return False


def _testes_citados(texto: str) -> list[str]:
    """Os testes citados entre crases: `tests/...py` (com ou sem `::função`)."""
    return re.findall(r"`(tests/[^`\s]+?\.py(?:::[\w\[\]-]+)*)`", texto)


def _prints_citados(texto: str) -> list[str]:
    """Os prints e registros citados: `x.png`, (x.png), [..](x.png)."""
    return re.findall(r"[`(]([^`()\s]+\.(?:png|jpg|txt|log|json))[`)]", texto)


def _arquivo_citado_existe(citado: str, pasta: Path, raiz: Path) -> bool:
    """O arquivo citado existe ao lado do ONDE-PAREI ou a partir da raiz da cópia?"""
    return (pasta / citado).exists() or (raiz / citado).exists()


def _conferir_campos(s: dict[str, str], etapa: str, tags: set, r: Resultado) -> dict[str, str]:
    """Os campos obrigatórios desta etapa e destas etiquetas: existem e não estão vazios. Devolve código → texto."""
    achados: dict[str, str] = {}
    for codigo, titulo, desde, quem in CAMPOS:
        if ETAPAS.index(etapa) < ETAPAS.index(desde) or (quem != "*" and quem not in tags):
            continue
        corpo = pedido_.secao(s, titulo)
        if corpo is None:
            r.problemas.append(f"falta a seção \"{titulo}\" ({codigo})")
        elif vazio(corpo):
            r.problemas.append(f"a seção \"{titulo}\" ({codigo}) está vazia, só com enchimento, ou diz \"não se "
                               "aplica\" sem o motivo")
        else:
            achados[codigo] = corpo
    return achados


def _conferir_decisoes(campos: dict[str, str], livro: Livro, r: Resultado) -> None:
    """F2 e K20: cada decisão existe no Livro e as palavras citadas estão lá, letra por letra; F10 cobre todas."""
    pedidas = campos.get("F2")
    if pedidas is None:
        return
    numeros: list[str] = []
    for item in _itens(pedidas):
        achados = NUMERO.findall(item)
        if not achados:
            continue
        numero = achados[0]
        numeros.append(numero)
        if not livro.existe(numero):
            r.problemas.append(f"{numero} não existe no Livro de decisões (K20)")
            continue
        # As palavras dele vêm logo depois do número; o comentário do agente vem depois de "Aqui:" ou "Na prática:".
        parte = re.split(r"\bAqui\s*:|\bNa prática\s*:", item, maxsplit=1, flags=re.I)[0]
        for citacao in _citacoes(parte):
            if not livro.tem_as_palavras(numero, citacao):
                r.problemas.append(f"{numero}: as palavras \"{citacao[:60]}\" não estão no Livro assim (copie do "
                                   "Livro; K20)")
    if not numeros:
        r.problemas.append("a seção de decisões não cita nenhuma decisão do Livro (D-nnn)")
    cumpridas = campos.get("F10", "")
    for numero in sorted(set(numeros) - set(NUMERO.findall(cumpridas))):
        r.problemas.append(f"{numero} pedida e sem \"como cumpri\" (F10)")


def _conferir_citacoes(campos: dict[str, str], repo: _Repositorio, pasta: Path, r: Resultado) -> None:
    """F3, F10, F12 e os outros: os testes e os prints citados existem."""
    for codigo, corpo in campos.items():
        for t in _testes_citados(corpo):
            if not repo.teste_existe(t):
                r.problemas.append(f"o teste citado {t} não existe ({codigo})")
        for p in _prints_citados(corpo):
            if not _arquivo_citado_existe(p, pasta, repo.raiz):
                r.problemas.append(f"o arquivo citado {p} não existe ({codigo})")


def _conferir_conteudo(campos: dict[str, str], tags: set, repo: _Repositorio, r: Resultado) -> None:
    """O que cada campo precisa ter dentro (F4, F5, F6, F7, F11, F12, F14, F15, E-WIN, E-TELA, E-IMG)."""
    f4 = campos.get("F4")
    if f4 is not None and not (re.search(r"\bPDF\b", f4) and (re.search(r"\bantes\b", f4, re.I) and
                                                              re.search(r"\bdepois\b", f4, re.I)
                                                              or re.search(r"\bn(ada|ão) muda", f4, re.I))):
        r.problemas.append("\"Como fica para quem usa e no livro\" tem de falar do PDF e do antes e depois (ou dizer "
                           "que nada muda) (F4)")
    f5 = campos.get("F5")
    if f5 is not None and not nao_se_aplica(f5):
        for nome in re.findall(r"`(?:[\w.]+\.)?(\w+)\(\)`", f5):
            if nome not in repo.definidos():
                r.problemas.append(f"a função {nome}() citada não existe no código (F5)")
        if "F12" in campos and not _testes_citados(campos["F12"]):
            r.problemas.append("\"Caminho e função\" não cita a prova em tests/ que cobra o mesmo resultado em todos "
                               "os caminhos (F12)")
    f6 = campos.get("F6")
    if f6 is not None:
        for nome, padrao in CASOS_DE_FALHA:
            if not re.search(padrao, f6, re.I):
                r.problemas.append(f"\"O que pode falhar\" não fala de: {nome} (ou escreva \"não se aplica: motivo\") "
                                   "(F6)")
    f7 = campos.get("F7")
    if f7 is not None and not nao_se_aplica(f7):
        for item in _itens(f7):
            if not re.search(r"https?://|[\w./-]+\.\w+:\d+|[\w./-]+\.\w+`?,? linhas? \d+", item):
                r.problemas.append(f"peça de fora sem fonte (endereço ou arquivo:linha): {item.strip()[:70]} (F7)")
    f14 = campos.get("F14")
    if f14 is not None and re.match(r"^\s*-?\s*nenhuma\b", f14, re.I):
        r.avisos.append("\"Ressalvas\" diz \"nenhuma\": quem tenta quebrar olha com mais cuidado (F14)")
    f15 = campos.get("F15")
    if f15 is not None and not nao_se_aplica(f15) and not RODADA.search(f15):
        r.problemas.append("\"Velocidade\" não traz o número da rodada do filtro de velocidade (F15)")
    win = campos.get("E-WIN")
    if win is not None and not re.search(r"\d", win):
        r.problemas.append("\"Perguntas do Windows que o Samuel vê\" tem de dizer quantas (um número, mesmo 0)")
    tela = campos.get("E-TELA")
    if tela is not None and not re.search(r"\.png\b", tela):
        r.problemas.append("\"O print que prova\" tem de citar o print (.png)")
    img = campos.get("E-IMG")
    if img is not None and not (re.search(r"p[áa]gina", img, re.I) and re.search(r"\d", img)):
        r.problemas.append("\"Páginas em que foi conferido\" tem de dizer o livro e a página")


def _conferir_arquivos(campos: dict[str, str], mudados: list[str], pasta_rel: str, r: Resultado) -> None:
    """F9: a lista "Arquivos criados ou alterados" bate com o git (sem a pasta do relatório)."""
    f9 = campos.get("F9")
    if f9 is None:
        return
    declarados = pedido_.lista_de_arquivos(f9)
    contam = [m for m in mudados if not m.startswith(pasta_rel)]
    for m in contam:
        if not pedido_.coberto(m, declarados):
            r.problemas.append(f"mexeu em {m} e não declarou em \"Arquivos criados ou alterados\" (F9)")
    for d in declarados:
        if d.startswith(pasta_rel.rstrip("/")):
            continue
        if not any(pedido_.coberto(m, [d]) for m in contam):
            r.problemas.append(f"declarou {d} em \"Arquivos criados ou alterados\" e o git não mostra mudança nele (F9)")


def _conferir_commit(campos: dict[str, str], raiz: Path, pasta_rel: str, r: Resultado) -> None:
    """F18: o commit citado existe, vem antes do atual e, depois dele, só o relatório do trabalho mudou."""
    f18 = campos.get("F18")
    if f18 is None:
        return
    citados = [c for c in COMMIT.findall(f18) if git.existe_commit(raiz, c)]
    if not citados:
        r.problemas.append("\"Commit\" não cita um commit que exista neste repositório (F18)")
        return
    c = citados[-1]
    if not git.e_ancestral(raiz, c):
        r.problemas.append(f"o commit {c} citado não está na história deste ramo (F18)")
        return
    depois = [m for m in git.mudados_entre(raiz, c) if not m.startswith(pasta_rel)]
    if depois:
        r.problemas.append(f"depois do commit {c} citado, mudaram arquivos fora do relatório: {', '.join(depois[:5])} "
                           "(cite o último commit do trabalho) (F18)")


def _problema_da_rodada(rodada: github.Rodada, raiz: Path) -> str | None:
    """O que impede esta rodada de valer para o último commit (None = vale): não passou, outro ramo, código mudado depois."""
    if not rodada.passou:
        return f"a rodada {rodada.numero} do GitHub não passou"
    if not git.existe_commit(raiz, rodada.commit_testado):
        return f"a rodada {rodada.numero} testou o commit {rodada.commit_testado[:8]}, que não está neste repositório"
    if not git.e_ancestral(raiz, rodada.commit_testado):
        return f"a rodada {rodada.numero} testou outro ramo (commit {rodada.commit_testado[:8]})"
    depois = [m for m in git.mudados_entre(raiz, rodada.commit_testado) if not m.endswith(".md")]
    if depois:
        return (f"depois do commit que a rodada {rodada.numero} testou ({rodada.commit_testado[:8]}) mudaram arquivos "
                f"que não são .md: {', '.join(depois[:5])}; rode o GitHub de novo")
    return None


def _conferir_github(campos: dict[str, str], raiz: Path, consultar: bool, r: Resultado) -> None:
    """F11 e K21: alguma rodada citada terminou, passou e testou o último commit (ou só .md mudou depois dela).

    Todas as rodadas citadas em "Testes" são lidas: uma rodada antiga citada (de um commit do meio) não atrapalha, e
    a ordem em que elas aparecem não importa.
    """
    f11 = campos.get("F11")
    if f11 is None:
        return
    numeros = list(dict.fromkeys(RODADA.findall(f11)))
    if not numeros:
        r.problemas.append("\"Testes\" não traz o número da rodada do GitHub (F11, K21)")
        return
    if not consultar:
        r.pendentes.append(f"a(s) rodada(s) {', '.join(numeros)} do GitHub não foi(ram) consultada(s) (K21)")
        return
    motivos, pendentes = [], []
    for numero in numeros:
        try:
            rodada = github.ler_rodada(numero, git.repositorio_no_github(raiz))
        except github.GitHubFalhou as erro:
            pendentes.append(f"não deu para ler a rodada {numero} do GitHub: {erro}")
            continue
        if not rodada.terminada:
            pendentes.append(f"a rodada {numero} ainda não terminou")
            continue
        motivo = _problema_da_rodada(rodada, raiz)
        if motivo is None:
            # Uma rodada que vale para o último commit basta, e o juiz dela (o porteiro da versão de teste) tem de ter
            # conferido: "não conferido" nunca vale como "passou" (R2 da terceira volta de quem quebrou).
            if rodada.porteiro is None:
                r.pendentes.append(f"a rodada {numero} não tem o juiz do porteiro (o porteiro da versão de teste não "
                                   "rodou: a mudança do workflow ainda não foi aplicada) (K21)")
            elif rodada.porteiro.startswith("NAO CONFERIDO"):
                r.pendentes.append(f"o juiz do porteiro da rodada {numero} não conferiu: {rodada.porteiro} (K21)")
            elif rodada.porteiro == "BARROU":
                r.problemas.append(f"o juiz do porteiro barrou a rodada {numero} (K21)")
            return
        motivos.append(motivo)
    if pendentes:
        r.pendentes += [f"{p} (K21)" for p in pendentes]
    else:
        r.problemas.append("nenhuma rodada citada vale para o último commit: " + "; ".join(motivos) + " (K21)")


def conferir_relatorio_de_quem_quebra(texto: str, r: Resultado) -> None:
    """Os seis campos do relatório de quem tenta quebrar existem e não estão vazios; cada achado tem o lugar."""
    s = pedido_.secoes(texto)
    for codigo, titulo in CAMPOS_DE_QUEM_QUEBRA:
        corpo = pedido_.secao(s, titulo)
        if corpo is None:
            r.problemas.append(f"o relatório de quem tenta quebrar não tem a seção \"{titulo}\" ({codigo})")
        elif vazio(corpo):
            r.problemas.append(f"a seção \"{titulo}\" ({codigo}) do relatório de quem tenta quebrar está vazia")
    achados = pedido_.secao(s, "Achados")
    if achados and not re.match(r"^\s*-?\s*nenhum\b.{10,}", achados, re.I | re.S):
        for item in _itens(achados):
            if re.match(r"^\s*\d+[.)]|^[-*]\s+\**\d+", item) and not re.search(r"[\w./-]+\.\w+:\d+", item):
                r.problemas.append(f"achado sem o lugar no código (arquivo:linha): {item.strip()[:70]} (Q6)")


def _conferir_f19(campos: dict[str, str], pasta: Path, raiz: Path, r: Resultado) -> None:
    """F19: o relatório de quem quebrou existe e passa nos seis campos; cada achado tem o seu destino."""
    f19 = campos.get("F19")
    if f19 is None:
        return
    relatorios = [c for c in re.findall(r"`([^`\s]+\.md)`", f19) if _arquivo_citado_existe(c, pasta, raiz)]
    if not relatorios:
        r.problemas.append("\"O que o agente que tentou quebrar achou\" não cita o relatório dele (um .md que "
                           "exista, em relatorios/<trabalho>/quem-quebrou/) (F19)")
    for c in relatorios:
        arquivo = pasta / c if (pasta / c).exists() else raiz / c
        texto = arquivo.read_text(encoding="utf-8")
        quem = pedido_.ler(texto)
        if quem.papel not in QUEM_CONFERE:
            r.problemas.append(f"o relatório {c} não é de quem tenta quebrar (papel: {quem.papel or 'não diz'}) (F19)")
        conferir_relatorio_de_quem_quebra(texto, r)
    for item in _itens(f19):
        if not re.match(r"^\s*\d+[.)]|^[-*]\s+\**\d+", item):
            continue
        consertado = re.search(r"consertado no commit\s+`?([0-9a-f]{7,40})", item, re.I)
        if consertado:
            if not git.existe_commit(raiz, consertado.group(1)):
                r.problemas.append(f"o commit {consertado.group(1)} do conserto não existe (F19)")
        elif not re.search(r"n[ãa]o é defeito|vira pergunta", item, re.I):
            r.problemas.append(f"achado sem destino (consertado no commit X / não é defeito, porquê / vira pergunta): "
                               f"{item.strip()[:70]} (F19)")


def _conferir_f20(campos: dict[str, str], etapa: str, pasta: Path, raiz: Path, r: Resultado) -> None:
    """F20: a prova de verdade, com data, hora e o print ou o registro da janela de prova."""
    f20 = campos.get("F20")
    if f20 is None or nao_se_aplica(f20):
        return
    if re.search(r"falta a sess[ãa]o", f20, re.I):
        r.problemas.append("a prova de verdade ainda falta (\"falta a sessão\"): não pode ser pronto (F20)")
        return
    if not (re.search(r"\b\d{2}/\d{2}/\d{4}\b", f20) and re.search(r"\b\d{1,2}[:h]\d{2}\b", f20)):
        r.problemas.append("a prova de verdade não diz a data (dd/mm/aaaa) e a hora (F20)")
    if not [p for p in _prints_citados(f20) if _arquivo_citado_existe(p, pasta, raiz)]:
        r.problemas.append("a prova de verdade não cita um print ou registro que exista (F20)")


def _conferir_perguntas(campos: dict[str, str], pasta: Path, raiz: Path, r: Resultado) -> None:
    """F17: cada pergunta (um "###") sem palavra de dentro, com "O que você escolhe", print e a sugestão (§11.13)."""
    f17 = campos.get("F17")
    if f17 is None or re.match(r"^\s*-?\s*nenhuma\b", f17, re.I):
        return
    blocos = re.split(r"^###\s+", f17, flags=re.M)[1:]
    if not blocos:
        r.problemas.append("cada pergunta para o Samuel vai num \"###\" próprio (F17)")
    for bloco in blocos:
        titulo = bloco.splitlines()[0][:60]
        dentro = PALAVRAS_DE_DENTRO.search(bloco)
        if dentro:
            r.problemas.append(f"pergunta \"{titulo}\": tem palavra de dentro ({dentro.group(0)}) (F17)")
        if "o que você escolhe" not in bloco.lower():
            r.problemas.append(f"pergunta \"{titulo}\": falta \"O que você escolhe\" (F17)")
        prints = [p for p in re.findall(r"\(([^()\s]+\.png)\)", bloco)]
        if not prints:
            r.problemas.append(f"pergunta \"{titulo}\": sem print (F17)")
        for p in prints:
            if not _arquivo_citado_existe(p, pasta, raiz):
                r.problemas.append(f"pergunta \"{titulo}\": o print {p} não existe (F17)")
        if "sugest" not in bloco.lower():
            r.problemas.append(f"pergunta \"{titulo}\": sem a sugestão (F17)")


def conferir(onde_parei: Path, etapa: str, raiz: Path, pacote: Path | None = None, consultar_github: bool = True,
             olhar_o_github_do_ramo: bool = True) -> Resultado:
    """Confere o formulário do ONDE-PAREI na etapa pedida; roda junto o porteiro das mudanças.

    `pacote`: o pacote que a gerente mandou; o pedido do ONDE-PAREI tem de ser igual ao dele (D-796).
    `consultar_github`: lê a rodada no GitHub (K21); sem isso, a K21 fica pendente (nunca passa calada).
    `olhar_o_github_do_ramo`: confere que o ramo está no GitHub (K18); os testes com repositório sem GitHub desligam.
    """
    if etapa not in ETAPAS:
        raise ValueError(f"etapa desconhecida: {etapa}")
    r = Resultado(etapa)
    raiz = Path(raiz)
    texto = onde_parei.read_text(encoding="utf-8")
    s = pedido_.secoes(texto)
    pedido = pedido_.ler(texto)
    r.problemas += pedido.problemas
    # O pacote da gerente é obrigatório (achado 3 de quem tentou quebrar, 19/11): sem ele, o papel e a lista de
    # arquivos seriam só o que o agente escreveu. O papel e a lista que valem são os do pacote.
    if pacote is None:
        r.problemas.append("falta o pacote do pedido (--pacote): sem ele, o papel e os arquivos permitidos são só o que "
                           "o agente escreveu (D-796)")
        return r
    texto_do_pacote = pacote.read_text(encoding="utf-8")
    do_pacote = pedido_.ler(texto_do_pacote)
    r.problemas += [f"no pacote: {p}" for p in do_pacote.problemas]
    for nome in ("papel", "partida", "ramo", "arquivos"):
        if getattr(do_pacote, nome) != getattr(pedido, nome):
            r.problemas.append(f"o pedido do ONDE-PAREI não é o do pacote da gerente ({nome}): copie sem mudar (D-796)")
    if pedido.problemas or do_pacote.problemas:
        return r
    pedido = do_pacote
    if not git.existe_commit(raiz, pedido.partida):
        r.problemas.append(f"o commit de partida {pedido.partida} não existe neste repositório")
        return r
    pasta = onde_parei.parent
    pasta_rel = pasta.resolve().relative_to(raiz.resolve()).as_posix() + "/"
    livro = Livro.da_versao_de_teste(raiz)    # o que vale é o da versão de teste (achado N1), nunca o do ramo

    for a in porteiro_mudancas.conferir_mudancas(raiz, pedido.partida, pedido.papel, pedido.arquivos, pasta, livro,
                                                 olhar_o_github_do_ramo):
        frase = f"{a.conferencia} {a.arquivo}{':' + str(a.linha) if a.linha else ''}: {a.porque}"
        (r.problemas if a.barra else r.avisos).append(frase)

    if pedido.papel == "quebrador":
        conferir_relatorio_de_quem_quebra(texto, r)
        return r

    tags, avisos_da_tabela = tabela_arquivos.etiquetas_do_trabalho(pedido.arquivos, raiz)
    r.avisos += avisos_da_tabela
    repo = _Repositorio(raiz)
    campos = _conferir_campos(s, etapa, tags, r)
    _conferir_decisoes(campos, livro, r)
    _conferir_citacoes(campos, repo, pasta, r)
    _conferir_conteudo(campos, tags, repo, r)
    _conferir_arquivos(campos, git.arquivos_mudados(raiz, pedido.partida), pasta_rel, r)
    _conferir_commit(campos, raiz, pasta_rel, r)
    _conferir_github(campos, raiz, consultar_github, r)
    _conferir_perguntas(campos, pasta, raiz, r)
    if ETAPAS.index(etapa) >= ETAPAS.index("prova"):
        _conferir_f19(campos, pasta, raiz, r)
    if etapa == "pronto":
        _conferir_f20(campos, etapa, pasta, raiz, r)
    return r
