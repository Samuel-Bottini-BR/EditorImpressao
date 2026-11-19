"""O porteiro das mudanças: as conferências que olham o que a entrega mudou desde o commit de partida.

K09, K10, K11, K12, K13, K14, K15, K17 e K18 da tabela da proposta das regras (§5.1). Precisam do papel do agente, do
commit de partida e da lista de arquivos do pedido (`pedido.py`); rodam quando o formulário da entrega é conferido
(`formulario.py`), em cada uma das três etapas. Tudo é lido dos commits (não da pasta), e a K18 confere que não ficou
nada fora de um commit nem do GitHub.

Decisões que mudaram estas conferências em relação à proposta:
- **K10 com a D-798** (Samuel: "fechou"): o rótulo "PRONTO PARA CONFERIR" é barrado no ramo de quem construiu
  (implementador, layout, pesquisador); só o verificador e quem tenta quebrar podem escrevê-lo. "APROVADO" é barrado
  para todos os agentes.
- **K13 com a D-796** (Samuel: "1, mas tem que ser explissito o pedido né" · "o porteiro tem que bloquear"): o agente
  de tela que mexer num arquivo de `core/` que o pedido não nomeou é barrado.
- **K17 com a D-791** ("nada entra nela sem o sim dele"): o agente que acrescenta item na lista de exceções é barrado.

Texto entre aspas (ou crases) não conta para a K10: a regra pode ser citada ("nunca escreva 'APROVADO'").

Seguro mexer: o texto de `porque`. Arriscado: o que cada papel pode mexer (`PODE_MEXER`), o que conta como arquivo
protegido (`PROTEGIDOS`) e o tirar das aspas (`_fora_das_aspas`): cada um decide o que barra.
"""

from __future__ import annotations

import ast
import re
from fnmatch import fnmatch
from pathlib import Path

from . import conversa_com_o_git as git
from . import excecoes
from . import leitura_do_codigo as leitura
from .livro import NUMERO, Livro
from .pedido import coberto
from . import pedido as pedido_
from .porteiro import FORA_DO_PROJETO, Achado, e_programa

# Quem pode escrever "PRONTO PARA CONFERIR" (D-798): só quem confere. Lugar único (o formulário importa daqui).
QUEM_CONFERE = ("verificador", "quebrador")
# A pasta, dentro da pasta do trabalho de quem construiu, onde fica o relatório de quem quebrou (o F19 lê dali).
PASTA_DE_QUEM_QUEBROU = "quem-quebrou/"

# Arquivos que agente nenhum muda sem o pedido dizer (K17): as regras, o Livro, o plano, o handoff e o próprio
# porteiro (o pacote, o gancho e as provas dele; achado 6 de quem tentou quebrar, 19/11).
PROTEGIDOS = ("CLAUDE.md", ".claude/*", "docs/plano/DECISOES.md", "docs/plano/PLANO-DEFINITIVO.md", "historico/*",
              "regras_dos_agentes/*", "ganchos/*", "tests/test_conferencias_*")


def _fora_das_aspas(linha: str) -> str:
    """A linha sem o que está entre aspas, aspas curvas, crases ou «» (citação não é o agente dizendo)."""
    return re.sub(r"\"[^\"\n]*\"|“[^”\n]*”|`[^`\n]*`|«[^»\n]*»|'[^'\n]*'", " ", linha)


def k09(pasta_do_relatorio: Path, raiz: Path) -> list[Achado]:
    """K09: cada relatório `.md` da pasta do trabalho tem o `.html` e o `.pdf` ao lado (relatorio.gravar).

    O ONDE-PAREI é controle, não relatório; anexos ficam numa subpasta (não são cobrados). O `.pdf` fica fora do git
    (`.gitignore`), então a conferência olha a pasta da cópia.
    """
    saida = []
    for md in sorted(pasta_do_relatorio.glob("*.md")):
        if md.name.upper() == "ONDE-PAREI.MD":
            continue
        faltam = [ext for ext in (".html", ".pdf") if not md.with_suffix(ext).exists()]
        if faltam:
            rel = md.relative_to(raiz).as_posix()
            saida.append(Achado("K09", rel, 0, md.name, f"relatório só em .md: falta {' e '.join(faltam)} "
                                f"(use relatorio.gravar, que grava os três)"))
    return saida


ROTULO_DE_PRONTO = re.compile(r"PRONTO\s+PARA\s+CONFERIR|(?i:^[\W\d_]*pronto\s+para\s+conferir\b)", re.M)


def _relatorios_de_quem_quebrou_aceitos(raiz: Path, base: str) -> set[str]:
    """As pastas `.../quem-quebrou/` onde o rótulo de pronto vale: só as que nenhum commit misturou com outro trabalho.

    O relatório de quem quebra vai para o ramo de quem construiu (D-775), e o rótulo de pronto é dele (D-798). Para o
    rótulo valer ali: (1) o arquivo está numa pasta `quem-quebrou/` de dentro de `relatorios/`; (2) todo commit que
    mexeu nessa pasta mexeu SÓ nela (um commit de quem quebrou, não um commit de quem construiu); (3) o relatório diz,
    no pedido dele, que o papel é de quem confere (conferido em `_rotulo_aceito`). Continua sendo o que está escrito
    no commit e no relatório: a gerente confere com o pacote que deu a quem quebrou.
    """
    limpas: dict[str, bool] = {}
    for _, arquivos in git.arquivos_por_commit(raiz, base):
        pastas = {a[: a.index(PASTA_DE_QUEM_QUEBROU) + len(PASTA_DE_QUEM_QUEBROU)] for a in arquivos
                  if a.startswith("relatorios/") and PASTA_DE_QUEM_QUEBROU in a}
        so_ali = all(any(a.startswith(p) for p in pastas) for a in arquivos)
        for p in pastas:
            limpas[p] = limpas.get(p, True) and so_ali
    return {p for p, limpa in limpas.items() if limpa}


def _rotulo_aceito(raiz: Path, caminho: str, papel: str, pasta_do_relatorio: str, aceitas: set[str],
                   papel_do_arquivo: dict[str, str]) -> bool:
    """O rótulo de pronto neste arquivo vale? (as regras estão na docstring de `k10`)."""
    if papel in QUEM_CONFERE and pasta_do_relatorio and caminho.startswith(pasta_do_relatorio):
        return True
    if not any(caminho.startswith(p) for p in aceitas):
        return False
    if caminho not in papel_do_arquivo:
        papel_do_arquivo[caminho] = pedido_.ler(git.conteudo_no_commit(raiz, "HEAD", caminho) or "").papel
    return papel_do_arquivo[caminho] in QUEM_CONFERE


def k10(raiz: Path, base: str, papel: str, pasta_do_relatorio: str = "") -> list[Achado]:
    """K10: "APROVADO" escrito por agente; [x] no plano ou no Livro; o rótulo de pronto fora do lugar de quem confere.

    Lê só os documentos (não os `.py`: no código, a palavra está sempre num texto entre aspas, como dado, ex.: o próprio
    porteiro). O rótulo conta em maiúsculas em qualquer lugar, ou como linha de situação ("Pronto para conferir.",
    "3. **Pronto para conferir**"), fora das aspas; "antes de pronto para conferir" no meio de uma frase não conta.
    O rótulo vale (D-798) na pasta do próprio trabalho de quem confere (`papel` verificador ou quebrador) e, no ramo
    de quem construiu, só no relatório de quem quebrou (`_relatorios_de_quem_quebrou_aceitos`).
    """
    saida = []
    aceitas = _relatorios_de_quem_quebrou_aceitos(raiz, base)
    papel_do_arquivo: dict[str, str] = {}
    for caminho, linhas in git.linhas_novas(raiz, base).items():
        if caminho.endswith(".py"):
            continue
        for n, texto in linhas:
            fora = _fora_das_aspas(texto)
            if re.search(r"\bAPROVADO\b", fora):
                saida.append(Achado("K10", caminho, n, " ".join(texto.split()), "APROVADO escrito por agente "
                                    "(só o Samuel aprova)"))
            if caminho in ("docs/plano/PLANO-DEFINITIVO.md", "docs/plano/DECISOES.md") and re.search(r"\[[xX]\]", fora):
                saida.append(Achado("K10", caminho, n, " ".join(texto.split()), "[x] posto no plano ou no Livro "
                                    "(só o Samuel marca)"))
            if ROTULO_DE_PRONTO.search(fora) and not _rotulo_aceito(raiz, caminho, papel, pasta_do_relatorio, aceitas,
                                                                     papel_do_arquivo):
                saida.append(Achado("K10", caminho, n, " ".join(texto.split()), f"o rótulo de pronto para conferir "
                                    f"fora do relatório de quem confere ({papel}); só quem confere escreve, e só no "
                                    f"relatório dele (D-798)"))
    return saida


def e_teste_antigo(caminho: str) -> bool:
    """Arquivo de teste: os de `tests/` e os soltos da raiz (`teste_*.py`, ex.: o `teste_botoes.py`, CLAUDE.md §4.5)."""
    return caminho.endswith(".py") and (caminho.startswith("tests/") or
                                        ("/" not in caminho and caminho.startswith("teste_")))


def _testes_de(fonte: str | None, todas: bool = False) -> dict[str, str]:
    """As funções de teste de um arquivo (nome completo → o código dela, sem espaço sobrando no fim das linhas).

    `todas`: num teste solto da raiz, toda função conta como teste (o `teste_botoes.py` não usa o nome `test_`).
    """
    if fonte is None:
        return {}
    texto = leitura.sem_marca_de_utf8(fonte).replace("\r\n", "\n")
    raiz = leitura.arvore(texto)
    saida = {}
    for f in leitura.funcoes(raiz):
        if todas or f.nome.split(".")[-1].startswith("test"):
            trecho = texto.split("\n")[f.inicio - 1:f.fim]
            saida[f.nome] = "\n".join(l.rstrip() for l in trecho)
    return saida


def _autorizado(raiz: Path, base: str, caminho: str, nome: str, livro: Livro) -> bool:
    """Algum commit que mexeu no arquivo cita o nome do teste e uma decisão que existe no Livro (ex.: a D-774)?"""
    for _, msg in git.mensagens_dos_commits(raiz, base, caminho):
        if nome.split(".")[-1] in msg and any(livro.existe(d) for d in NUMERO.findall(msg)):
            return True
    return False


def k11(raiz: Path, base: str, livro: Livro) -> list[Achado]:
    """K11: teste que já existia no commit de partida e foi mudado ou apagado, sem o commit citar a decisão que deixa."""
    saida = []
    for caminho in git.arquivos_mudados(raiz, base):
        if not e_teste_antigo(caminho):
            continue
        todas = not caminho.startswith("tests/")
        try:
            antes = _testes_de(git.conteudo_no_commit(raiz, base, caminho), todas)
            depois = _testes_de(git.conteudo_no_commit(raiz, "HEAD", caminho), todas)
        except leitura.CodigoIlegivel as erro:
            saida.append(Achado("K11", caminho, 0, caminho, f"não deu para ler o teste: {erro}"))
            continue
        for nome, codigo in antes.items():
            if depois.get(nome) == codigo:
                continue
            if _autorizado(raiz, base, caminho, nome, livro):
                continue
            o_que = "apagado" if nome not in depois else "mudado"
            saida.append(Achado("K11", caminho, 0, nome, f"teste antigo {o_que} sem o commit citar o nome dele e a "
                                "decisão do Samuel que autoriza (D-605: teste antigo não muda para passar)"))
    return saida


def k12(raiz: Path, base: str) -> list[Achado]:
    """K12: arquivo `.py` mexido sem docstring no começo, ou função mexida sem docstring.

    Fica de fora a função de até 2 linhas dentro de outra. Só olha as funções que têm linha nova.
    """
    saida = []
    novas = git.linhas_novas(raiz, base)
    for caminho, linhas in novas.items():
        if not caminho.endswith(".py") or caminho.split("/")[0] in FORA_DO_PROJETO or not linhas:
            continue
        fonte = git.conteudo_no_commit(raiz, "HEAD", caminho)
        if fonte is None:
            continue
        try:
            arvore = leitura.arvore(fonte)
        except leitura.CodigoIlegivel as erro:
            saida.append(Achado("K12", caminho, 0, caminho, f"não deu para ler o arquivo: {erro}"))
            continue
        if not (ast.get_docstring(arvore) or "").strip():
            saida.append(Achado("K12", caminho, 1, caminho, "arquivo mexido sem docstring no começo (o que é, o que "
                                "faz, o que é seguro ou arriscado mudar)"))
        mexidas = {n for n, _ in linhas}
        for f in leitura.funcoes(arvore):
            if f.tem_docstring or (f.dentro_de_outra_funcao and f.fim - f.inicio <= 2):
                continue
            if any(f.inicio <= n <= f.fim for n in mexidas):
                saida.append(Achado("K12", caminho, f.inicio, f.nome, f"função mexida sem docstring: {f.nome}"))
    return saida


def k13(mudados: list[str], papel: str, permitidos: list[str], pasta_do_relatorio: str = "") -> list[Achado]:
    """K13: mexeu fora do papel, fora da lista do pedido (D-796).

    O agente de tela (D-796: "Sem isso escrito no pedido, continua só em ui/") é barrado em todo arquivo fora de `ui/`
    que o pedido não nomeou, menos a pasta do relatório do próprio trabalho (achado 4 de quem tentou quebrar, 19/11).
    """
    saida = []
    for c in mudados:
        if coberto(c, permitidos) or (pasta_do_relatorio and c.startswith(pasta_do_relatorio)):
            continue
        if papel == "implementador" and c.startswith("ui/"):
            saida.append(Achado("K13", c, 0, c, "o implementador mexeu em ui/ sem o pedido nomear o arquivo"))
        elif papel == "layout" and not c.startswith("ui/"):
            saida.append(Achado("K13", c, 0, c, "o agente de tela mexeu fora de ui/ sem o pedido nomear o arquivo "
                                "(D-796)"))
        elif papel in ("verificador", "pesquisador", "quebrador") and e_programa(c):
            saida.append(Achado("K13", c, 0, c, f"o {papel} mexeu no programa sem o pedido nomear o arquivo"))
    return saida


def k14(mudados: list[str], permitidos: list[str], pasta_do_relatorio: str) -> list[Achado]:
    """K14: mexeu em arquivo fora da lista do pedido. Só avisa (o pacote é refeito com os arquivos de verdade)."""
    return [Achado("K14", c, 0, c, "mexeu em arquivo fora da lista do pedido: o pacote de regras pode estar "
                   "incompleto (avise a gerente)", barra=False)
            for c in mudados if not coberto(c, permitidos) and not c.startswith(pasta_do_relatorio)]


def k15(raiz: Path, base: str, mudados: list[str], livro: Livro) -> list[Achado]:
    """K15: o requirements.txt mudou sem o commit citar a decisão do Samuel sobre a biblioteca."""
    if "requirements.txt" not in mudados:
        return []
    for _, msg in git.mensagens_dos_commits(raiz, base, "requirements.txt"):
        for d in NUMERO.findall(msg):
            linha = livro.linhas.get(d, "").lower()
            if "biblioteca" in linha or "requirements" in linha:
                return []
    return [Achado("K15", "requirements.txt", 0, "requirements.txt", "trocar ou acrescentar biblioteca pede o "
                   "\"sim\" do Samuel, citado no commit (a decisão do Livro que fala da biblioteca)")]


def mudancas_na_lista(antes: excecoes.Lista | None, depois: excecoes.Lista, livro: Livro) -> list[str]:
    """O que mudou na lista de exceções que só a gerente (com o "sim" do Samuel) pode mudar: o lugar único dessa conta.

    Usada pela K17 (o formulário da entrega), pelo teste do GitHub que compara com a versão de teste
    (`tests/test_conferencias_protecao.py`) e pela conferência antes do commit (achados 6 e 7 de quem quebrou, 19/11):
    - item novo, ou "quantas" maior, sem o "sim" próprio conferido no Livro (D-791);
    - a situação ou o "sim" do Samuel mudados;
    - o passo de um item que continua mudado (a promessa feita ao Samuel sobre quando ele some).
    """
    if antes is None:
        return []
    frases = [f"item novo na lista sem o \"sim\" do Samuel: {i['conferencia']} {i['arquivo']} | {i['texto'][:80]}"
              for i in excecoes.acrescentados_sem_sim(antes, depois, livro)]
    if antes.situacao != depois.situacao:
        frases.append(f"a situação da lista mudou de {antes.situacao!r} para {depois.situacao!r}")
    if antes.sim_do_samuel != depois.sim_do_samuel:
        frases.append("o \"sim\" do Samuel na lista mudou")
    passos = {excecoes.chave(i["arquivo"], i["conferencia"], i["texto"]): i["passo"] for i in antes.itens}
    for i in depois.itens:
        velho = passos.get(excecoes.chave(i["arquivo"], i["conferencia"], i["texto"]))
        if velho is not None and velho != i["passo"]:
            frases.append(f"o passo de um item mudou de {velho!r} para {i['passo']!r}: {i['arquivo']} | "
                          f"{i['texto'][:60]}")
    return frases


def k17(raiz: Path, base: str, mudados: list[str], permitidos: list[str], livro: Livro | None = None) -> list[Achado]:
    """K17: mexeu nas regras, no Livro, no plano, no handoff ou no porteiro sem o pedido dizer; ou mudou a lista do
    jeito que só a gerente pode (`mudancas_na_lista`)."""
    livro = livro or Livro.do_repositorio(raiz)
    saida = [Achado("K17", c, 0, c, "agente mexeu num arquivo que só a gerente muda (com o \"sim\" do Samuel)")
             for c in mudados if any(fnmatch(c, p) for p in PROTEGIDOS) and not coberto(c, permitidos)]
    if excecoes.ARQUIVO_DA_LISTA in mudados:
        antes_txt = git.conteudo_no_commit(raiz, base, excecoes.ARQUIVO_DA_LISTA)
        depois_txt = git.conteudo_no_commit(raiz, "HEAD", excecoes.ARQUIVO_DA_LISTA)
        antes = excecoes.ler(raiz, antes_txt) if antes_txt is not None else None
        if antes is None and not coberto(excecoes.ARQUIVO_DA_LISTA, permitidos):
            saida.append(Achado("K17", excecoes.ARQUIVO_DA_LISTA, 0, "lista criada", "a lista de exceções nasceu "
                                "neste trabalho sem o pedido nomeá-la"))
        if depois_txt is not None:
            for frase in mudancas_na_lista(antes, excecoes.ler(raiz, depois_txt), livro):
                saida.append(Achado("K17", excecoes.ARQUIVO_DA_LISTA, 0, frase[:80], frase))
    return saida


def k18(raiz: Path) -> list[Achado]:
    """K18: nada mudado fora de um commit, e o último commit já está no GitHub (perguntado ao GitHub, não à cópia)."""
    saida = []
    sobras = git.mudancas_sem_commit(raiz)
    if sobras:
        saida.append(Achado("K18", ".", 0, "git status", f"há {len(sobras)} mudança(s) fora de commit: "
                            + ", ".join(s[3:] for s in sobras[:5])))
    remoto = git.commit_no_github(raiz, git.ramo_atual(raiz))
    atual = git.commit_completo(raiz, "HEAD")
    if remoto is None:
        saida.append(Achado("K18", ".", 0, "git push", "o ramo não existe no GitHub: faça o push"))
    elif remoto != atual:
        saida.append(Achado("K18", ".", 0, "git push", "o último commit ainda não está no GitHub: faça o push"))
    return saida


def conferir_mudancas(raiz: Path, base: str, papel: str, permitidos: list[str], pasta_do_relatorio: Path,
                      livro: Livro, olhar_o_github: bool = True) -> list[Achado]:
    """Roda K09 a K15, K17 e K18 (K18 só quando `olhar_o_github`; nos testes com repositório sem GitHub, não)."""
    raiz = Path(raiz)
    mudados = git.arquivos_mudados(raiz, base)
    pasta_rel = pasta_do_relatorio.resolve().relative_to(raiz.resolve()).as_posix() + "/"
    achados = (k09(pasta_do_relatorio, raiz) + k10(raiz, base, papel, pasta_rel) + k11(raiz, base, livro)
               + k12(raiz, base) + k13(mudados, papel, permitidos, pasta_rel) + k14(mudados, permitidos, pasta_rel)
               + k15(raiz, base, mudados, livro) + k17(raiz, base, mudados, permitidos, livro))
    if olhar_o_github:
        achados += k18(raiz)
    return achados
