"""A lista de exceções do porteiro (D-791, D-800): o que já está errado hoje no código, um item por lugar.

Palavras do Samuel (D-791, 19/11): à pergunta "o que já está errado no código fica numa lista, que só diminui e só
ganha item com o seu "sim"?": "Sim"; e a "Então anoto a lista de exceções como combinamos?": "sim".

Como funciona:
- **Um item por lugar** (correção 2 do plano-v3, passo 0): arquivo, conferência, o texto achado e quantas vezes ele
  aparece. Nunca o arquivo inteiro: um erro novo no mesmo arquivo (outro texto, ou o mesmo texto uma vez a mais) é
  barrado. O número da linha não entra na chave (muda quando se escreve acima); fica só para achar o lugar.
- **Cada item tem a data e o passo do plano que o conserta** (`PASSO_QUE_CONSERTA`, o lugar único dessa conta, tirada
  da tabela do plano-v3, passo 0). Os 5 lugares de fora da parte do Windows ficam "depois da entrega" (D-800).
- **Só diminui:** item que o código já não tem faz o porteiro reclamar até ser tirado da lista (no mesmo commit do
  conserto); item novo só entra com o "sim" do Samuel (a gerente põe; o agente que acrescenta é barrado, K17).
- **Enquanto o Samuel não disser "sim", a lista não vale** (`situacao: "proposta"`): o teste que barra o código do
  repositório fica parado, com o motivo escrito. A gerente liga trocando para `"valendo"` e escrevendo o "sim" dele
  (data e palavras) em `sim_do_samuel`; um teste cobra que "valendo" sem o "sim" não passa.

O arquivo de dados é `tests/conferencias_excecoes.json` (ao lado dos testes; no git). Ele é gerado por este programa
(`python -m regras_dos_agentes excecoes --gerar`), nunca escrito à mão.

Seguro mexer: os textos de `motivo`. Arriscado: a chave do item (`chave`), a comparação (`comparar`) e o
`PASSO_QUE_CONSERTA` (muda a promessa feita ao Samuel sobre quando cada lugar some).
"""

from __future__ import annotations

import datetime
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable

from .porteiro import Achado

ARQUIVO_DA_LISTA = "tests/conferencias_excecoes.json"
DEPOIS_DA_ENTREGA = "depois da entrega"

# (arquivo, conferência, função) → (passo do plano-v3 que conserta, por quê). A primeira linha que casa vale.
# Tirado da tabela "A lista de partida" do plano-v3, passo 0 (relatorios/plano-windows-2026-11-18/plano-v3.md).
PASSO_QUE_CONSERTA: list[tuple[str, str, str, str, str]] = [
    ("empacotar.py", "*", "*", "2", "o publicar passa a ler a assinatura pela peça única do Windows"),
    ("atualizacao.py", "K04", "criar_as_tarefas", "5", "o desinstalar limpo tira o número de decisão do registro"),
    ("atualizacao.py", "K04", "ao_desinstalar", "5", "o desinstalar limpo tira o número de decisão do registro"),
    ("atualizacao.py", "*", "*", "3", "o atualizador passa a conversar com o Windows só pela peça única"),
    ("core/_testes_a_distancia_windows.py", "*", "*", "4", "os testes à distância passam a usar a peça única"),
    ("core/testes_a_distancia.py", "*", "xml_da_tarefa_do_desfazer", "5", "o desinstalar limpo troca a tarefa do desfazer"),
    ("core/testes_a_distancia.py", "*", "*", "4", "os testes à distância passam a usar a peça única e a pasta segura"),
    ("ui/automatico.py", "K04", "*", DEPOIS_DA_ENTREGA, "dicas do Automático com número de decisão; D-800"),
    ("teste_velocidade.py", "K01", "*", DEPOIS_DA_ENTREGA, "o teste de velocidade abre o PowerShell; D-800"),
    ("avaliar.py", "K01", "*", DEPOIS_DA_ENTREGA, "a régua dos filtros pergunta a Área de Trabalho ao Windows; D-800"),
]


class ListaErrada(ValueError):
    """O arquivo da lista não está no formato combinado, ou um lugar não tem passo que o conserte."""


def chave(arquivo: str, conferencia: str, texto: str) -> tuple[str, str, str]:
    """O que identifica um lugar na lista (sem o número da linha)."""
    return (arquivo, conferencia, texto)


@dataclass
class Lista:
    """A lista lida do arquivo: a situação, o "sim" do Samuel e os itens."""

    situacao: str
    sim_do_samuel: dict | None
    itens: list[dict]
    dados: dict = field(default_factory=dict)

    @property
    def vale(self) -> bool:
        """A lista vale (o Samuel disse "sim")? Enquanto não, o teste que barra o repositório fica parado."""
        return self.situacao == "valendo"

    def permitidos(self) -> dict[tuple[str, str, str], int]:
        """Quantas vezes cada lugar pode aparecer."""
        return {chave(i["arquivo"], i["conferencia"], i["texto"]): int(i["quantas"]) for i in self.itens}

    def lugares(self) -> int:
        """Quantos lugares a lista deixa passar (a soma de "quantas")."""
        return sum(int(i["quantas"]) for i in self.itens)


def ler(raiz: Path | str, conteudo: str | None = None) -> Lista:
    """Lê a lista do repositório (ou de um texto já lido) e confere o formato; `ListaErrada` se estiver fora dele."""
    texto = conteudo if conteudo is not None else (Path(raiz) / ARQUIVO_DA_LISTA).read_text(encoding="utf-8")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as erro:
        raise ListaErrada(f"a lista de exceções não é um JSON válido: {erro}") from erro
    situacao = dados.get("situacao")
    if situacao not in ("proposta", "valendo"):
        raise ListaErrada(f"situação da lista desconhecida: {situacao!r} (só 'proposta' ou 'valendo')")
    sim = dados.get("sim_do_samuel")
    if situacao == "valendo" and not (isinstance(sim, dict) and str(sim.get("em", "")).strip()
                                      and str(sim.get("palavras", "")).strip()):
        raise ListaErrada("a lista está 'valendo' sem o 'sim' do Samuel escrito (sim_do_samuel: em e palavras)")
    itens = dados.get("itens")
    if not isinstance(itens, list):
        raise ListaErrada("a lista não tem 'itens'")
    vistos = set()
    for i in itens:
        for campo in ("arquivo", "conferencia", "texto", "quantas", "data", "passo", "motivo"):
            if not str(i.get(campo, "")).strip():
                raise ListaErrada(f"item sem '{campo}': {i}")
        if int(i["quantas"]) < 1:
            raise ListaErrada(f"item com 'quantas' menor que 1: {i}")
        k = chave(i["arquivo"], i["conferencia"], i["texto"])
        if k in vistos:
            raise ListaErrada(f"o mesmo lugar aparece duas vezes na lista: {k}")
        vistos.add(k)
    return Lista(situacao, sim, itens, dados)


def passo_do_lugar(arquivo: str, conferencia: str, funcao: str) -> tuple[str, str]:
    """O passo do plano que conserta o lugar e o porquê; `ListaErrada` se nenhuma linha de `PASSO_QUE_CONSERTA` casa."""
    for arq, conf, func, passo, motivo in PASSO_QUE_CONSERTA:
        if fnmatch(arquivo, arq) and conf in ("*", conferencia) and func in ("*", funcao):
            return passo, motivo
    raise ListaErrada(f"lugar sem passo que o conserte (a gerente decide antes de entrar na lista): "
                      f"{arquivo} {conferencia} {funcao or '(fora de função)'}")


def gerar(achados: Iterable[Achado], commit_lido: str, data: str | None = None) -> dict:
    """A lista de partida, tirada dos achados do porteiro no código de hoje. Sai como 'proposta', sem o "sim"."""
    data = data or datetime.date.today().isoformat()
    grupos: dict[tuple[str, str, str], list[Achado]] = defaultdict(list)
    for a in achados:
        if a.conferencia == "K00":
            raise ListaErrada(f"o porteiro não conseguiu ler {a.arquivo}: arrume antes de gerar a lista")
        grupos[chave(a.arquivo, a.conferencia, a.texto)].append(a)
    itens = []
    for (arquivo, conferencia, texto), lista in sorted(grupos.items()):
        funcoes = sorted({a.funcao for a in lista})
        passo, motivo = passo_do_lugar(arquivo, conferencia, funcoes[0])
        for f in funcoes[1:]:
            if passo_do_lugar(arquivo, conferencia, f)[0] != passo:
                raise ListaErrada(f"o mesmo texto em {arquivo} tem passos diferentes conforme a função: {texto}")
        itens.append({"arquivo": arquivo, "conferencia": conferencia, "texto": texto, "quantas": len(lista),
                      "linhas_quando_gerada": sorted(a.linha for a in lista),
                      "funcao": ", ".join(f or "(fora de função)" for f in funcoes),
                      "data": data, "passo": passo, "motivo": motivo})
    return {
        "explicacao": ("Lista de exceções do porteiro (D-791, D-800). Gerada por `python -m regras_dos_agentes excecoes "
                       "--gerar`; não escreva à mão. Um item por lugar (arquivo, conferência, texto, quantas). Só "
                       "diminui: cada conserto tira o seu item no mesmo commit. Item novo só com o 'sim' do Samuel. "
                       "Enquanto 'situacao' for 'proposta', a lista não vale e o teste que barra o repositório fica "
                       "parado; a gerente liga trocando para 'valendo' e escrevendo o 'sim' dele em 'sim_do_samuel'."),
        "situacao": "proposta",
        "sim_do_samuel": None,
        "gerada_em": data,
        "commit_lido": commit_lido,
        "itens": itens,
    }


@dataclass
class Comparacao:
    """O resultado de comparar os achados com a lista."""

    novos: list[Achado] = field(default_factory=list)          # erro que a lista não deixa (barra)
    consertados: list[tuple[dict, int]] = field(default_factory=list)   # (item, quantos sobraram no código)

    @property
    def passa(self) -> bool:
        """Passa quando não há erro novo nem item da lista que o código já não tem."""
        return not self.novos and not self.consertados

    def explicar(self) -> list[str]:
        """As frases do que está errado, uma por lugar, para o agente consertar."""
        saida = []
        for a in self.novos:
            saida.append(f"{a.conferencia} {a.arquivo}:{a.linha} ({a.funcao or 'fora de função'}): {a.porque} "
                         f"| {a.texto[:120]}")
        for item, sobrou in self.consertados:
            saida.append(f"a lista de exceções tem um lugar que o código já não tem (sobraram {sobrou} de "
                         f"{item['quantas']}): tire ou diminua o item {item['conferencia']} {item['arquivo']} "
                         f"| {item['texto'][:100]} (rode `python -m regras_dos_agentes excecoes --gerar`)")
        return saida


def comparar(achados: Iterable[Achado], lista: Lista, so_arquivos: Iterable[str] | None = None) -> Comparacao:
    """Compara o que o porteiro achou com o que a lista deixa passar.

    `so_arquivos`: quando só uma parte do repositório foi lida (antes do commit), só os itens desses arquivos contam.
    O K00 (arquivo que o porteiro não conseguiu ler) nunca é exceção.
    """
    so = set(so_arquivos) if so_arquivos is not None else None
    achados = [a for a in achados if so is None or a.arquivo in so]
    por_chave: dict[tuple[str, str, str], list[Achado]] = defaultdict(list)
    for a in achados:
        por_chave[chave(a.arquivo, a.conferencia, a.texto)].append(a)
    permitidos = lista.permitidos()
    r = Comparacao()
    for k, lugares in sorted(por_chave.items()):
        deixa = 0 if lugares[0].conferencia == "K00" else permitidos.get(k, 0)
        if len(lugares) > deixa:
            r.novos += sorted(lugares, key=lambda a: a.linha)[deixa:] if deixa else lugares
    contagem = Counter({k: len(v) for k, v in por_chave.items()})
    for item in lista.itens:
        if so is not None and item["arquivo"] not in so:
            continue
        k = chave(item["arquivo"], item["conferencia"], item["texto"])
        if contagem.get(k, 0) < int(item["quantas"]):
            r.consertados.append((item, contagem.get(k, 0)))
    return r


def diminuir(lista: Lista, achados: Iterable[Achado]) -> dict:
    """A lista depois de um conserto: tira (ou diminui) os itens que o código já não tem. Nunca acrescenta.

    Se houver erro novo (um lugar que a lista não deixa), levanta `ListaErrada`: erro novo se conserta, não entra na
    lista (só com o "sim" do Samuel, pela gerente). A situação, o "sim" e as datas dos itens que ficam não mudam.
    """
    achados = list(achados)
    novos = comparar(achados, lista).novos
    if novos:
        raise ListaErrada("há erro novo que a lista não deixa; conserte antes (a lista não ganha item sem o 'sim' do "
                          "Samuel):\n  " + "\n  ".join(Comparacao(novos=novos).explicar()))
    contagem = Counter(chave(a.arquivo, a.conferencia, a.texto) for a in achados)
    itens = []
    for item in lista.itens:
        ficam = min(int(item["quantas"]), contagem.get(chave(item["arquivo"], item["conferencia"], item["texto"]), 0))
        if ficam:
            itens.append(dict(item, quantas=ficam))
    return dict(lista.dados, itens=itens)


def itens_acrescentados(antes: Lista | None, depois: Lista) -> list[dict]:
    """Os itens que a lista ganhou (lugar novo, ou "quantas" maior) entre duas versões. A lista só diminui."""
    if antes is None:
        return list(depois.itens)
    permitidos = antes.permitidos()
    return [i for i in depois.itens
            if int(i["quantas"]) > permitidos.get(chave(i["arquivo"], i["conferencia"], i["texto"]), 0)]


def resumo(lista: Lista) -> dict:
    """Quantos lugares e itens por passo, e por conferência, para o relatório e o texto ao Samuel."""
    por_passo: Counter = Counter()
    itens_por_passo: Counter = Counter()
    por_conf: Counter = Counter()
    for i in lista.itens:
        por_passo[i["passo"]] += int(i["quantas"])
        itens_por_passo[i["passo"]] += 1
        por_conf[i["conferencia"]] += int(i["quantas"])
    return {"lugares": lista.lugares(), "itens": len(lista.itens), "por_passo": dict(por_passo),
            "itens_por_passo": dict(itens_por_passo), "por_conferencia": dict(por_conf)}


def gravar(raiz: Path | str, dados: dict) -> Path:
    """Grava a lista no arquivo de dados (UTF-8, quebra de linha do git, uma chave por linha)."""
    destino = Path(raiz) / ARQUIVO_DA_LISTA
    destino.write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return destino
