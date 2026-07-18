"""Modelos de dados do Editor de Impressão.

Uma observacao sobre a estrutura, que se afasta de proposito da especificacao:

A especificacao prévia uma única lista de ConfigPagina. Na pratica existem dois
niveis diferentes, e mistura-los complicaria a interface:

  - FOLHA  = o que veio no PDF de entrada. E onde moram dividir, posição do
             corte, rotação e recorte. E o que a aba "Onde cortar" mostra.
  - PAGINA = o que vai sair no PDF final. Uma folha dividida vira DUAS páginas.
             E onde mora o filtro, que a especificacao exige que seja por
             página. E o que a aba "Filtro" mostra.

Assim "livro todo em preto e branco, só a capa em Mágico pro" cai naturalmente,
e a tira de miniaturas de cada aba mostra exatamente a unidade que aquela aba
edita.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from core.filtros import FILTROS, PRETO_E_BRANCO

METADE_INTEIRA = "inteira"
METADE_ESQUERDA = "esquerda"
METADE_DIREITA = "direita"


@dataclass
class ConfigFolha:
    """Uma folha do PDF de entrada."""

    indice: int
    dividir: bool = True
    posicao_corte: float = 0.5       # 0.0 a 1.0, relativo a largura
    confianca_corte: float = 0.0     # 0.0 a 1.0
    rotacao: int = 0                 # 0, 90, 180, 270
    angulo_detectado: float = 0.0    # so para o alerta "muito torta"
    confianca_angulo: float = 0.0
    apagada: bool = False
    e_paisagem: bool = True
    alertas: list[str] = field(default_factory=list)
    revisada: bool = False

    @property
    def precisa_revisao(self) -> bool:
        return bool(self.alertas) and not self.revisada


@dataclass
class ConfigPagina:
    """Uma página do PDF de saida."""

    indice: int                      # posicao no livro final, comecando em 0
    folha: int                       # de qual folha de entrada ela veio
    metade: str = METADE_INTEIRA     # inteira | esquerda | direita

    # Recorte e angulo moram na PAGINA, e nao na folha, porque o pipeline os
    # aplica depois da divisao: cada metade tem a sua sombra de lombada de um
    # lado so, e pode estar torta de um jeito diferente da outra.
    recorte: tuple[float, float, float, float] | None = None  # None = automatico
    angulo_manual: float | None = None                        # None = automatico

    filtro: str = PRETO_E_BRANCO
    forca_preto: str = "normal"      # mais_fraco | normal | mais_escuro
    apagada: bool = False
    tem_cor: bool = False
    alertas: list[str] = field(default_factory=list)
    revisada: bool = False

    @property
    def precisa_revisao(self) -> bool:
        return bool(self.alertas) and not self.revisada


@dataclass
class Projeto:
    """Um livro sendo trabalhado."""

    caminho_entrada: str
    caminho_saida: str = ""
    nome: str = ""

    dividir_folhas: bool = True
    limpar: bool = True
    filtro_padrao: str = PRETO_E_BRANCO
    endireitar: bool = True
    cortar_bordas: bool = True
    montar_cadernos: bool = False
    paginas_por_caderno: int = 20
    qualidade_dpi: int = 300

    folhas: list[ConfigFolha] = field(default_factory=list)
    paginas: list[ConfigPagina] = field(default_factory=list)
    criado_em: str = ""

    # --- conveniencias ----------------------------------------------------

    @property
    def paginas_ativas(self) -> list[ConfigPagina]:
        return [p for p in self.paginas if not p.apagada]

    @property
    def total_apagadas(self) -> int:
        return sum(1 for p in self.paginas if p.apagada)

    @property
    def so_cadernos(self) -> bool:
        """Caminho rapido: nenhuma alteracao de imagem, só reordenar."""
        return (
            self.montar_cadernos
            and not self.dividir_folhas
            and not self.limpar
            and not self.endireitar
            and not self.cortar_bordas
            and self.total_apagadas == 0
        )

    @property
    def alguma_funcao_marcada(self) -> bool:
        return any(
            (self.dividir_folhas, self.limpar, self.endireitar,
             self.cortar_bordas, self.montar_cadernos)
        )

    def pendentes_de_revisao(self) -> int:
        return sum(1 for f in self.folhas if f.precisa_revisao) + sum(
            1 for p in self.paginas if p.precisa_revisao
        )

    # --- serializacao -----------------------------------------------------

    def para_dicionario(self) -> dict[str, Any]:
        dados = asdict(self)
        # tuplas viram listas no JSON; guardamos assim mesmo e convertemos na volta
        return dados

    @staticmethod
    def de_dicionario(dados: dict[str, Any]) -> "Projeto":
        folhas = [ConfigFolha(**f) for f in dados.pop("folhas", [])]
        paginas = [ConfigPagina(**_com_tuplas(p)) for p in dados.pop("paginas", [])]
        projeto = Projeto(**dados)
        projeto.folhas = folhas
        projeto.paginas = paginas
        return projeto


def _com_tuplas(dados: dict[str, Any]) -> dict[str, Any]:
    """JSON não tem tupla; devolve os recortes ao formato original."""
    valor = dados.get("recorte")
    if isinstance(valor, list):
        dados["recorte"] = tuple(valor)
    return dados


@dataclass
class Acao:
    """Uma alteracao feita pelo usuario, para desfazer e refazer.

    Guardamos a ACAO, não uma copia do projeto: com centenas de páginas, copiar
    o estado a cada mexida seria pesado demais. Assim o desfazer e ilimitado.
    """

    momento: str
    tipo: str
    alvo: str                  # "folha" ou "pagina"
    indices: list[int]
    antes: dict[str, Any]
    depois: dict[str, Any]
    descricao: str

    @staticmethod
    def nova(
        tipo: str, alvo: str, indices: list[int],
        antes: dict[str, Any], depois: dict[str, Any], descricao: str,
    ) -> "Acao":
        return Acao(
            momento=datetime.now().isoformat(timespec="seconds"),
            tipo=tipo, alvo=alvo, indices=list(indices),
            antes=dict(antes), depois=dict(depois), descricao=descricao,
        )

    def para_dicionario(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def de_dicionario(dados: dict[str, Any]) -> "Acao":
        return Acao(**dados)


def nome_de_arquivo_seguro(nome: str) -> str:
    """Tira do nome os caracteres que o Windows não aceita em arquivo."""
    proibidos = '<>:"/\\|?*'
    limpo = "".join("-" if c in proibidos else c for c in nome).strip(" .")
    return limpo or "livro"


def nome_de_saida_sugerido(projeto: "Projeto") -> str:
    """Nome de arquivo proposto, já com a extensao.

    O sufixo conta o que foi feito, para o Kaique diferenciar duas versoes do
    mesmo livro na mesma pasta.
    """
    from core.filtros import NOMES_AMIGAVEIS

    base = nome_de_arquivo_seguro(projeto.nome or "livro")

    if projeto.montar_cadernos:
        sufixo = "cadernos"
    elif projeto.limpar:
        sufixo = NOMES_AMIGAVEIS.get(projeto.filtro_padrao, projeto.filtro_padrao).lower()
    else:
        sufixo = "arrumado"

    return f"{base} - {sufixo}.pdf"


def filtro_valido(filtro: str) -> str:
    return filtro if filtro in FILTROS else PRETO_E_BRANCO
