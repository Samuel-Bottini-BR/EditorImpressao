"""Desfazer e refazer ilimitados, gravados em arquivo.

Padrao Command: guardamos a ACAO, não uma copia do projeto. Uma acao ocupa
algumas centenas de bytes, entao dar Ctrl+Z quinhentas vezes e barato. Copiar o
estado inteiro a cada mexida, com 500 páginas, não seria.

O histórico vai para acoes.jsonl (uma acao por linha). JSON Lines porque da
para acrescentar no fim sem reescrever o arquivo, e porque um fechamento
inesperado no meio da escrita perde no máximo a última linha.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from modelos import Acao, Projeto

ARQUIVO_ACOES = "acoes.jsonl"
ARQUIVO_POSICAO = "posicao.json"


class HistoricoAcoes:
    """As duas pilhas mais a gravacao em disco."""

    def __init__(self, pasta_projeto: Path | str | None = None) -> None:
        self.pasta = Path(pasta_projeto) if pasta_projeto else None
        self.feitas: list[Acao] = []     # ja aplicadas, do mais antigo ao mais novo
        self.desfeitas: list[Acao] = []  # desfeitas, prontas para refazer
        # Quantas linhas o carregar() nao conseguiu ler. Fica guardado para a
        # tela poder avisar: sem aviso, a pessoa procura um trabalho que a
        # queda de energia levou e acha que o programa comeu.
        self.linhas_perdidas = 0

    # --- consulta ---------------------------------------------------------

    @property
    def pode_desfazer(self) -> bool:
        return bool(self.feitas)

    @property
    def pode_refazer(self) -> bool:
        return bool(self.desfeitas)

    def descricao_desfazer(self) -> str:
        return f"Desfazer: {self.feitas[-1].descricao}" if self.feitas else "Nada para desfazer"

    def descricao_refazer(self) -> str:
        return f"Refazer: {self.desfeitas[-1].descricao}" if self.desfeitas else "Nada para refazer"

    # --- registrar --------------------------------------------------------

    def registrar(self, acao: Acao) -> None:
        """Guarda uma acao já aplicada ao projeto.

        Uma acao nova depois de um desfazer limpa a pilha de refazer - e o
        comportamento que todo mundo espera de qualquer editor.

        A pilha de refazer e limpa no ARQUIVO tambem (Lista de bugs,
        06/10/2026): antes ela so era limpa na memoria, a acao nova ia para
        o fim do acoes.jsonl, depois das desfeitas, e ao reabrir o livro o
        Ctrl+Z desfazia a acao errada. Agora, se havia algo para refazer, o
        arquivo e regravado inteiro so com o historico que vale
        (_regravar_tudo); sem nada para refazer (o caso comum), a acao
        continua so indo para o fim do arquivo, que e barato. Arriscado:
        voltar a so acrescentar quando havia refazer.
        """
        havia_refazer = bool(self.desfeitas)
        self.feitas.append(acao)
        self.desfeitas.clear()
        if havia_refazer:
            self._regravar_tudo()
        else:
            self._gravar(acao)

    # --- desfazer / refazer -----------------------------------------------

    def desfazer(self, projeto: Projeto) -> Acao | None:
        if not self.feitas:
            return None
        acao = self.feitas.pop()
        aplicar(projeto, acao, acao.antes)
        self.desfeitas.append(acao)
        self._gravar_posicao()
        return acao

    def refazer(self, projeto: Projeto) -> Acao | None:
        if not self.desfeitas:
            return None
        acao = self.desfeitas.pop()
        aplicar(projeto, acao, acao.depois)
        self.feitas.append(acao)
        self._gravar_posicao()
        return acao

    def voltar_para(self, projeto: Projeto, posicao: int) -> None:
        """Leva o projeto até um ponto do histórico (painel 'Historico')."""
        while len(self.feitas) > posicao and self.desfazer(projeto):
            pass
        while len(self.feitas) < posicao and self.refazer(projeto):
            pass

    # --- disco ------------------------------------------------------------

    def _gravar(self, acao: Acao) -> None:
        if self.pasta is None:
            return
        try:
            self.pasta.mkdir(parents=True, exist_ok=True)
            caminho = self.pasta / ARQUIVO_ACOES
            with caminho.open("a", encoding="utf-8") as arquivo:
                arquivo.write(json.dumps(acao.para_dicionario(), ensure_ascii=False) + "\n")
            self._gravar_posicao()
        except OSError:
            # Nao poder gravar o historico nao pode derrubar o programa:
            # o desfazer continua funcionando na memoria.
            pass

    def _regravar_tudo(self) -> None:
        """Regrava o acoes.jsonl inteiro com o historico que vale agora
        (feitas e, depois, as desfeitas na ordem em que seriam refeitas) e o
        posicao.json.

        Grava do jeito seguro do projeto.json (projetos._escrever_e_trocar):
        tudo num arquivo ao lado, forcado ate o disco (fsync) e so entao
        trocado pelo de antes. Uma queda de energia no meio deixa o arquivo
        velho inteiro ou o novo inteiro, nunca pela metade. E feito na hora
        (nao pelo fio que grava por tras) de proposito: a proxima acao vai
        para o fim DESTE arquivo, e uma regravacao atrasada poderia apagar
        essa acao. So acontece numa acao feita logo depois de um desfazer
        (e ao abrir um livro com o arquivo errado), e o arquivo e pequeno
        (umas centenas de bytes por acao).

        Nao poder gravar nao derruba o programa (o desfazer continua na
        memoria), como no _gravar. Arriscado: escrever direto por cima do
        acoes.jsonl (uma queda no meio perderia o historico inteiro, nao so
        a ultima linha).
        """
        if self.pasta is None:
            return
        from projetos import _escrever_e_trocar   # aqui dentro: projetos e pesado

        historico = self.feitas + list(reversed(self.desfeitas))
        texto = "".join(
            json.dumps(acao.para_dicionario(), ensure_ascii=False) + "\n"
            for acao in historico)
        try:
            self.pasta.mkdir(parents=True, exist_ok=True)
            _escrever_e_trocar(self.pasta / ARQUIVO_ACOES, texto)
            self._gravar_posicao()
        except OSError:
            pass

    def _guardar_arquivo_errado(self) -> bool:
        """Guarda ao lado o acoes.jsonl e o posicao.json como estavam, antes
        de o carregar() acertar um arquivo errado (ver la).

        Nomes "acoes.antigo-historico-AAAA-MM-DD-HHMM.jsonl" e
        "posicao.antigo-historico-....json": tem o ".antigo-" de proposito,
        como as outras copias de seguranca (projetos.guardar_copia_do_
        trabalho), para o "Tirar da lista" as guardar junto (projetos.
        copias_do_trabalho). Nunca por cima de outra copia (modo "x", e
        "-2", "-3"... no mesmo minuto), e forcada ate o disco antes de o
        arquivo ser regravado. Devolve False se nao deu para copiar: ai o
        arquivo errado NAO e regravado (nada se perde; so o historico desta
        vez fica com a acao certa na memoria).
        """
        from datetime import datetime

        carimbo = datetime.now().strftime("%Y-%m-%d-%H%M")
        origens = [self.pasta / ARQUIVO_ACOES, self.pasta / ARQUIVO_POSICAO]

        def destino(origem: Path, sufixo: str) -> Path:
            return origem.with_name(f"{origem.stem}.antigo-historico-{sufixo}{origem.suffix}")

        for numero in range(1, 1000):
            sufixo = carimbo if numero == 1 else f"{carimbo}-{numero}"
            if any(destino(o, sufixo).exists() for o in origens):
                continue
            try:
                for origem in origens:
                    if not origem.is_file():
                        continue
                    with destino(origem, sufixo).open("xb") as copia:
                        copia.write(origem.read_bytes())
                        copia.flush()
                        os.fsync(copia.fileno())
            except FileExistsError:
                continue
            except OSError:
                return False
            return True
        return False

    def recomecar(self, copia_do_trabalho: Path | None = None) -> bool:
        """A conferencia recomecou: o desfazer e o refazer comecam vazios, e o
        historico antigo sai do acoes.jsonl SEM se perder.

        Lista de bugs, 06/10/2026 (parecer do verificador dos consertos de
        06/10, item 5): quando o trabalho salvo nao combina com o livro (a
        pessoa mudou "Dividir folhas ao meio", o PDF foi trocado, o
        projeto.json nao da para ler), ui/janela_principal.py
        (_analise_pronta) recomeca a conferencia e guarda o trabalho antigo
        (projetos.guardar_copia_do_trabalho), mas o historico continuava o
        da conferencia anterior: num PDF de 12 paginas que ficou com 6, o
        primeiro Ctrl+Z pos a pagina 1 em Preto e branco, uma acao feita na
        metade esquerda da folha 1 (outra pagina). Agora a janela chama isto
        em vez de carregar().

        `copia_do_trabalho`: o projeto.antigo-<data>.json que a janela acabou
        de guardar (ou None). Essa copia ja leva o acoes.jsonl e o
        posicao.json do mesmo momento (acoes.antigo-<data>.jsonl,
        posicao.antigo-<data>.json). Se as copias deles estao la e iguais,
        byte a byte, aos de agora, os de agora sao apagados (o historico
        antigo fica so junto da copia do trabalho, como pedido). Senao (sem
        copia do trabalho, ou ela nao bate), eles sao RENOMEADOS para
        acoes.antigo-historico-<data>.jsonl e posicao.antigo-historico-....
        json, os nomes do conserto do arquivo errado (_guardar_arquivo_errado;
        o ".antigo-" faz o "Tirar da lista" guarda-los junto). Renomear nao
        precisa de espaco no disco e nunca escreve por cima (nome ja usado:
        "-2", "-3"...).

        Devolve False so se o acoes.jsonl antigo nao pode sair do caminho
        (arquivo preso, sem permissao): ai NADA e apagado, e o historico
        desta conferencia fica so na memoria (self.pasta = None), para as
        acoes novas nao irem para o fim do arquivo antigo, misturadas com as
        da conferencia anterior. Ressalva: nesse caso raro, ao reabrir o
        livro, o historico antigo volta (o defeito de antes, so nesse caso).

        Arriscado: apagar o acoes.jsonl sem conferir que a copia bate (o
        historico antigo se perderia); chamar isto quando o trabalho combina
        (o Ctrl+Z de um trabalho que continua se perderia).
        """
        self.feitas = []
        self.desfeitas = []
        self.linhas_perdidas = 0
        if self.pasta is None:
            return True
        acoes = self.pasta / ARQUIVO_ACOES
        posicao = self.pasta / ARQUIVO_POSICAO
        origens = [arquivo for arquivo in (acoes, posicao) if arquivo.is_file()]
        if not origens:
            return True
        if self._ja_estao_na_copia(origens, copia_do_trabalho):
            for origem in origens:
                try:
                    origem.unlink()
                except OSError:
                    pass          # tenta renomear logo abaixo
            origens = [arquivo for arquivo in origens if arquivo.is_file()]
            if not origens:
                return True
        if self._renomear_para_antigo_historico(origens) or not acoes.is_file():
            return True
        self.pasta = None         # nada saiu do caminho: so na memoria (ver acima)
        return False

    def _ja_estao_na_copia(self, origens: list[Path], copia_do_trabalho: Path | None) -> bool:
        """Os arquivos `origens` (acoes.jsonl, posicao.json) estao, iguais
        byte a byte, na copia do trabalho (projetos.guardar_copia_do_trabalho,
        mesmo <data> no nome: projeto.antigo-<data>.json leva
        acoes.antigo-<data>.jsonl e posicao.antigo-<data>.json)? Copia de
        outra pasta, ou de nome que nao segue o padrao: nao."""
        if copia_do_trabalho is None:
            return False
        copia = Path(copia_do_trabalho)
        if ".antigo-" not in copia.stem or copia.parent.resolve() != self.pasta.resolve():
            return False
        sufixo = copia.stem.split(".antigo-", 1)[1]
        try:
            for origem in origens:
                guardada = origem.with_name(f"{origem.stem}.antigo-{sufixo}{origem.suffix}")
                if not guardada.is_file() or guardada.read_bytes() != origem.read_bytes():
                    return False
        except OSError:
            return False
        return True

    def _renomear_para_antigo_historico(self, origens: list[Path]) -> bool:
        """Renomeia `origens` para <nome>.antigo-historico-AAAA-MM-DD-HHMM,
        todos com o mesmo <data> (com "-2", "-3"... se algum nome ja existe;
        e o rename do Windows falha em vez de escrever por cima). Devolve
        True se o acoes.jsonl saiu do caminho (ou nao estava la)."""
        from datetime import datetime

        carimbo = datetime.now().strftime("%Y-%m-%d-%H%M")
        for numero in range(1, 1000):
            sufixo = carimbo if numero == 1 else f"{carimbo}-{numero}"
            destinos = {origem: origem.with_name(
                f"{origem.stem}.antigo-historico-{sufixo}{origem.suffix}") for origem in origens}
            if any(destino.exists() for destino in destinos.values()):
                continue
            for origem, destino in destinos.items():
                try:
                    origem.rename(destino)
                except OSError:
                    pass          # quem chama confere se o acoes.jsonl saiu
            break
        return not (self.pasta / ARQUIVO_ACOES).is_file()

    def _gravar_posicao(self) -> None:
        if self.pasta is None:
            return
        try:
            dados = {"aplicadas": len(self.feitas), "total": len(self.feitas) + len(self.desfeitas)}
            (self.pasta / ARQUIVO_POSICAO).write_text(
                json.dumps(dados), encoding="utf-8"
            )
        except OSError:
            pass

    def carregar(self) -> None:
        """Le o histórico do disco.

        A posição tambem e restaurada, entao reabrir o programa no meio de um
        livro mantem o refazer disponível, não só o desfazer.
        """
        if self.pasta is None:
            return
        caminho = self.pasta / ARQUIVO_ACOES
        if not caminho.exists():
            return

        acoes: list[Acao] = []
        self.linhas_perdidas = 0
        try:
            # errors="replace" de proposito: uma queda de energia no meio da
            # gravacao deixa bytes pela metade, e read_text sem isso levanta
            # UnicodeDecodeError - que nao e OSError e derrubaria o programa
            # ao abrir o projeto. O projeto nao pode se perder por causa da
            # ultima linha.
            texto = caminho.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return

        for linha in texto.splitlines():
            linha = linha.strip()
            if not linha:
                continue
            try:
                acoes.append(Acao.de_dicionario(json.loads(linha)))
            except (ValueError, TypeError):
                # linha cortada por um fechamento no meio. Ela e ignorada, mas
                # CONTADA: a pessoa precisa saber que as ultimas acoes se
                # perderam, senao vai procurar um trabalho que nao esta la.
                self.linhas_perdidas += 1

        aplicadas = len(acoes)
        total = len(acoes)
        try:
            dados = json.loads((self.pasta / ARQUIVO_POSICAO).read_text(encoding="utf-8"))
            aplicadas = int(dados.get("aplicadas", aplicadas))
            total = int(dados.get("total", total))
        except (OSError, ValueError, TypeError):
            pass

        if 0 <= total < len(acoes):
            # Arquivo errado, deixado pelo programa de antes de 06/10/2026
            # (Lista de bugs): uma acao feita depois de um desfazer ia para o
            # fim do arquivo SEM tirar as desfeitas, entao o arquivo tem mais
            # linhas que o historico (o "total" do posicao.json). As linhas
            # a mais sao acoes desfeitas, mas o arquivo nao diz QUAIS (o
            # desfazer nao deixa marca nele): depois de A, B, desfazer B, C,
            # o arquivo e [A, B, C] e o historico de verdade e [A, C]. Ler
            # as primeiras linhas (como antes) da [A, B] - o defeito.
            #
            # O que se sabe com certeza: a ULTIMA linha e a ultima acao
            # registrada, e ela foi a ultima do historico. Se o posicao.json
            # diz que tudo estava feito (aplicadas == total), ela esta
            # aplicada e o Ctrl+Z dela devolve exatamente o que havia antes
            # (o "antes" foi fotografado na hora). Fica so ela. Se a ultima
            # coisa foi um desfazer, nao se sabe o que esta feito: o
            # historico fica vazio - melhor nao oferecer o Ctrl+Z do que
            # desfazer a acao errada. O livro em si (projeto.json) nao muda
            # nada: so o que o Ctrl+Z alcanca.
            #
            # O arquivo e acertado (regravado so com o que ficou), para a
            # proxima acao ir para o fim certo, mas ANTES o de antes e
            # guardado ao lado, sem apagar nada. Arriscado: "adivinhar" as
            # outras linhas; regravar sem a copia.
            self.feitas = acoes[-1:] if aplicadas == total else []
            self.desfeitas = []
            if self._guardar_arquivo_errado():
                self._regravar_tudo()
            return

        aplicadas = max(0, min(aplicadas, len(acoes)))
        self.feitas = acoes[:aplicadas]
        self.desfeitas = list(reversed(acoes[aplicadas:]))


# ---------------------------------------------------------------------------
# aplicacao das acoes no projeto
# ---------------------------------------------------------------------------

def aplicar(projeto: Projeto, acao: Acao, valores: dict[str, Any]) -> None:
    """Escreve os campos de 'valores' nos itens que a acao aponta.

    Cada campo pode vir de duas formas:
      - valor simples: vale para todos os indices da acao
      - dicionario {indice: valor}: cada item recebe o seu

    A segunda forma existe para o desfazer de uma acao em lote: ao aplicar
    "usar em todas", cada página tinha um filtro anterior diferente, e o
    Ctrl+Z precisa devolver o de cada uma.

    Campo com o prefixo "livro." vale para o PROJETO, e nao para os itens
    (ex.: "livro.filtro_padrao", o filtro do livro): assim uma acao so muda
    paginas e o filtro do livro juntos, e o desfazer devolve os dois. Usado
    pelo "Sim" da pergunta do fundo (ui/janela_principal.py,
    _tirar_o_fundo_do_livro_inteiro; pedido do verificador, 30/09). Arquivo
    de acoes antigo nao tem esses campos: nada muda para ele. Arriscado: por
    "livro." em campo que nao existe no Projeto (o setattr criaria um).
    """
    itens = projeto.folhas if acao.alvo == "folha" else projeto.paginas

    for campo, valor in valores.items():
        if campo.startswith("livro."):
            nome = campo[len("livro."):]
            if hasattr(projeto, nome):
                setattr(projeto, nome, valor)

    for indice in acao.indices:
        if not 0 <= indice < len(itens):
            continue
        item = itens[indice]
        for campo, valor in valores.items():
            if campo.startswith("livro."):
                continue
            if isinstance(valor, dict):
                if str(indice) in valor:
                    setattr(item, campo, _restaurar_tipo(campo, valor[str(indice)]))
            else:
                setattr(item, campo, _restaurar_tipo(campo, valor))


# Campos que sao tupla em modelos.py mas o JSON grava como lista - o
# desfazer/refazer precisa devolver ao formato certo, senao uma comparacao
# `== (a, b)` depois de um Ctrl+Z falha (bug latente achado no plano "corrigir
# bugs do teste do Boecio", secao 3a: `conteudo_deslocamento` ja tinha esse
# problema, nunca pego por nunca ter sido lido antes de `tamanho_folha_cm`
# existir).
_CAMPOS_TUPLA = ("recorte", "recorte_detectado", "tamanho_folha_cm", "conteudo_deslocamento")


def _restaurar_tipo(campo: str, valor: Any) -> Any:
    """O JSON perde a tupla do recorte; devolvemos ao formato certo."""
    if campo in _CAMPOS_TUPLA and isinstance(valor, list):
        return tuple(valor)
    return valor


def montar_acao(
    projeto: Projeto, tipo: str, alvo: str, indices: list[int],
    campos: dict[str, Any], descricao: str,
) -> Acao:
    """Fotografa os valores atuais dos campos e monta a acao a registrar.

    Chamar ANTES de alterar o projeto: e daqui que sai o 'antes' do desfazer.
    """
    itens = projeto.folhas if alvo == "folha" else projeto.paginas

    antes: dict[str, Any] = {}
    for campo in campos:
        antes[campo] = {
            str(i): _serializavel(getattr(itens[i], campo))
            for i in indices
            if 0 <= i < len(itens)
        }

    depois = {campo: _serializavel(valor) for campo, valor in campos.items()}
    return Acao.nova(tipo, alvo, indices, antes, depois, descricao)


def _serializavel(valor: Any) -> Any:
    return list(valor) if isinstance(valor, tuple) else valor
