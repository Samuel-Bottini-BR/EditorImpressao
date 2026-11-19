"""A linha de comando do pacote de regras: `python -m regras_dos_agentes <comando>` (rodar na pasta da cópia).

Comandos:
- `porteiro`: roda as conferências do código parado no repositório inteiro e compara com a lista de exceções.
- `antes-do-commit`: o mesmo, só nos arquivos que vão no próximo commit (chamado por `ganchos/pre-commit`).
- `excecoes --gerar`: gera a lista de partida (só a primeira vez; sai "proposta").
- `excecoes --diminuir`: depois de um conserto, tira da lista o que o código já não tem (nunca acrescenta).
- `excecoes --texto`: o texto curto para o Samuel dizer "sim".
- `tabela`: os arquivos do git sem linha na tabela de etiquetas.
- `pacote`: monta o pacote de regras de um pedido.
- `entrega`: confere o formulário da entrega de um agente (o ONDE-PAREI) numa das três etapas.
- `juiz --conferido <pasta>`: o porteiro desta pasta (tirada da versão de teste) julga a cópia de um ramo (a rodada do
  GitHub roda assim; ver `juiz.py`).

Código de saída: 0 = passou; 1 = barrou (há o que consertar); 3 = não deu para conferir (ex.: o git não respondeu).
Nunca 0 quando não conferiu (CLAUDE.md §11.12, ponto 2).

Seguro mexer: textos de ajuda. Arriscado: os códigos de saída (o gancho do git e quem chama dependem deles).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PASSOU, BARROU, NAO_CONFERIU = 0, 1, 3


def _escrever(texto: str) -> None:
    """Escreve na tela em UTF-8, mesmo no console do Windows."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(texto)


def comando_porteiro(raiz: Path, so_o_proximo_commit: bool) -> int:
    """Roda o porteiro do código parado e compara com a lista de exceções."""
    from . import conversa_com_o_git as git
    from . import excecoes, porteiro

    if so_o_proximo_commit:
        # Tudo como vai no commit: os arquivos e a lista de exceções lidos do índice, não da pasta.
        caminhos, achados = porteiro.achados_do_proximo_commit(raiz)
        try:
            lista = excecoes.ler(raiz, git.conteudo_no_indice(raiz, excecoes.ARQUIVO_DA_LISTA))
        except git.GitFalhou:
            lista = None
        so = caminhos
    else:
        caminhos, achados = porteiro.achados_do_repositorio(raiz)
        lista = excecoes.ler(raiz) if (raiz / excecoes.ARQUIVO_DA_LISTA).exists() else None
        so = None
    if lista is None:
        _escrever("O porteiro não achou a lista de exceções (tests/conferencias_excecoes.json): não deu para conferir.")
        return NAO_CONFERIU
    if so_o_proximo_commit and excecoes.ARQUIVO_DA_LISTA in caminhos:
        # A lista do commit contra a do último commit (achado 7; R1 da terceira volta): item novo, "quantas" maior, o
        # passo, a situação ou o "sim" mudados barram, com ou sem "sim". Isso só se muda por commit da gerente direto
        # na versão de teste (onde esta conferência deixa: ela é quem liga a lista, depois do "sim" do Samuel). Quem
        # garante é o juiz da rodada do GitHub (`juiz.py`), que lê a versão de teste; aqui só se avisa cedo.
        from .livro import VERSAO_DE_TESTE
        from .porteiro_mudancas import mudancas_na_lista

        texto_antes = git.conteudo_no_commit(raiz, "HEAD", excecoes.ARQUIVO_DA_LISTA) if git.existe_commit(
            raiz, "HEAD") else None
        antes = excecoes.ler(raiz, texto_antes) if texto_antes is not None else None
        frases = mudancas_na_lista(antes, lista)
        if frases and git.ramo_atual(raiz) != VERSAO_DE_TESTE:
            _escrever("O porteiro barrou a lista de exceções (num ramo de agente ela só diminui; item novo e o ligar só "
                      "pela gerente, direto na versão de teste):")
            for frase in frases:
                _escrever("  " + frase)
            return BARROU
    if not lista.vale:
        _escrever(f"A lista de exceções ainda é proposta (espera o \"sim\" do Samuel): o porteiro não barra o "
                  f"código ainda. Achados agora: {len(achados)}.")
        comparacao = excecoes.comparar(achados, lista, so)
        for frase in comparacao.explicar():
            _escrever("  (quando valer, barraria) " + frase)
        return PASSOU
    comparacao = excecoes.comparar(achados, lista, so)
    if comparacao.passa:
        _escrever(f"Porteiro: nada novo ({len(caminhos)} arquivos lidos; a lista deixa {lista.lugares()} lugares).")
        return PASSOU
    _escrever("O porteiro barrou:")
    for frase in comparacao.explicar():
        _escrever("  " + frase)
    return BARROU


def comando_excecoes(raiz: Path, args: argparse.Namespace) -> int:
    """Gera, diminui ou mostra a lista de exceções."""
    from . import conversa_com_o_git as git
    from . import excecoes, porteiro, texto_para_o_samuel

    if args.gerar:
        if (raiz / excecoes.ARQUIVO_DA_LISTA).exists() and not args.de_novo:
            _escrever("A lista já existe. Ela só diminui: depois de um conserto, use --diminuir. (--gerar --de-novo "
                      "refaz do zero e só serve antes do \"sim\" do Samuel.)")
            return BARROU
        if (raiz / excecoes.ARQUIVO_DA_LISTA).exists() and excecoes.ler(raiz).vale:
            _escrever("A lista já vale (o Samuel disse \"sim\"): não se refaz do zero. Use --diminuir.")
            return BARROU
        _, achados = porteiro.achados_do_repositorio(raiz)
        destino = excecoes.gravar(raiz, excecoes.gerar(achados, git.commit_completo(raiz, "HEAD")))
        lista = excecoes.ler(raiz)
        _escrever(f"Gravada {destino}: {lista.lugares()} lugares em {len(lista.itens)} itens (proposta).")
        return PASSOU
    if args.diminuir:
        lista = excecoes.ler(raiz)
        _, achados = porteiro.achados_do_repositorio(raiz)
        antes = lista.lugares()
        excecoes.gravar(raiz, excecoes.diminuir(lista, achados))
        _escrever(f"A lista passou de {antes} para {excecoes.ler(raiz).lugares()} lugares.")
        return PASSOU
    if args.texto:
        _escrever(texto_para_o_samuel.texto(excecoes.ler(raiz)))
        return PASSOU
    _escrever(str(excecoes.resumo(excecoes.ler(raiz))))
    return PASSOU


def principal(argv: list[str] | None = None) -> int:
    """Lê o comando e roda; qualquer falha de conferência vira código 3 com o motivo, nunca 0."""
    from . import conversa_com_o_git as git
    from . import excecoes

    analisador = argparse.ArgumentParser(prog="python -m regras_dos_agentes", description=__doc__.split("\n")[0])
    sub = analisador.add_subparsers(dest="comando", required=True)
    sub.add_parser("porteiro", help="o porteiro no repositório inteiro")
    sub.add_parser("antes-do-commit", help="o porteiro só no que vai no próximo commit")
    e = sub.add_parser("excecoes", help="a lista de exceções")
    e.add_argument("--gerar", action="store_true")
    e.add_argument("--de-novo", action="store_true")
    e.add_argument("--diminuir", action="store_true")
    e.add_argument("--texto", action="store_true")
    sub.add_parser("tabela", help="arquivos do git sem linha na tabela")
    p = sub.add_parser("pacote", help="monta o pacote de regras de um pedido")
    p.add_argument("--papel", required=True)
    p.add_argument("--titulo", required=True)
    p.add_argument("--decisoes", default="", help="D-nnn,D-nnn")
    p.add_argument("--partida", required=True, help="o commit de onde o trabalho sai")
    p.add_argument("--ramo", required=True)
    p.add_argument("--saida", help="grava o pacote neste arquivo (a gerente guarda para conferir a entrega)")
    p.add_argument("--passo", help="o passo do plano deste trabalho (o pacote diz quais funções não se mexem)")
    p.add_argument("arquivos", nargs="+", help="arquivos do pedido; novo: na frente para arquivo que ainda não existe")
    f = sub.add_parser("entrega", help="confere o formulário da entrega")
    f.add_argument("onde_parei")
    f.add_argument("--etapa", required=True, choices=["quebrar", "prova", "pronto"])
    f.add_argument("--pacote", help="o pacote que a gerente mandou (para comparar o pedido)")
    f.add_argument("--sem-github", action="store_true", help="não consultar a rodada do GitHub (K21 fica pendente)")
    j = sub.add_parser("juiz", help="o porteiro desta pasta (a versão de teste) julgando a cópia de um ramo")
    j.add_argument("--conferido", required=True, help="a pasta da cópia do ramo a julgar (um repositório git)")
    args = analisador.parse_args(argv)

    try:
        if args.comando == "juiz":
            # O juiz roda de dentro da pasta tirada da versão de teste, que não é um repositório: não usa a pasta atual
            # como repositório, só a cópia conferida.
            from . import juiz
            marca, frases = juiz.julgar(Path(args.conferido).resolve())
            _escrever(juiz.anunciar(marca, frases))
            return BARROU if marca == juiz.MARCA_BARROU else PASSOU
        raiz = git.raiz_do_repositorio(Path.cwd())
        if args.comando == "porteiro":
            return comando_porteiro(raiz, False)
        if args.comando == "antes-do-commit":
            return comando_porteiro(raiz, True)
        if args.comando == "excecoes":
            return comando_excecoes(raiz, args)
        if args.comando == "tabela":
            from . import tabela_arquivos
            sem = tabela_arquivos.sem_linha(git.arquivos_do_git(raiz))
            _escrever(f"Arquivos sem linha na tabela: {len(sem)}")
            for c in sem:
                _escrever("  " + c)
            return BARROU if sem else PASSOU
        if args.comando == "pacote":
            from . import montar_pacote
            texto = montar_pacote.montar(args.papel, args.titulo, [d for d in args.decisoes.split(",") if d],
                                         args.arquivos, raiz, args.partida, args.ramo, args.passo)
            if args.saida:
                Path(args.saida).write_text(texto, encoding="utf-8", newline="\n")
            _escrever(texto)
            return PASSOU
        if args.comando == "entrega":
            from . import formulario
            resultado = formulario.conferir(Path(args.onde_parei).resolve(), args.etapa, raiz,
                                            pacote=Path(args.pacote) if args.pacote else None,
                                            consultar_github=not args.sem_github)
            _escrever(resultado.explicar())
            return resultado.codigo_de_saida
    except git.GitFalhou as erro:
        _escrever(f"PORTEIRO: NAO CONFERIDO (não deu para conferir: {erro})" if args.comando == "juiz"
                  else f"Não deu para conferir: {erro}")
        return NAO_CONFERIU
    except excecoes.ListaErrada as erro:
        _escrever(f"Não deu para conferir: {erro}")
        return NAO_CONFERIU
    except OSError as erro:
        _escrever(f"Não deu para conferir (arquivo): {erro}")
        return NAO_CONFERIU
    return NAO_CONFERIU


if __name__ == "__main__":
    sys.exit(principal())
