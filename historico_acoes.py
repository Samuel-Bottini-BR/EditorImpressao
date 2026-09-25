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
        """
        self.feitas.append(acao)
        self.desfeitas.clear()
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
        try:
            dados = json.loads((self.pasta / ARQUIVO_POSICAO).read_text(encoding="utf-8"))
            aplicadas = int(dados.get("aplicadas", aplicadas))
        except (OSError, ValueError, TypeError):
            pass

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
    """
    itens = projeto.folhas if acao.alvo == "folha" else projeto.paginas

    for indice in acao.indices:
        if not 0 <= indice < len(itens):
            continue
        item = itens[indice]
        for campo, valor in valores.items():
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
