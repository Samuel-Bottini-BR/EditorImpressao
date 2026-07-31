"""A selecao: onde cada tratamento vale dentro da pagina.

Esta e a fundacao que faltava. Ate aqui cada filtro decidia sozinho, olhando a
folha inteira do mesmo jeito, e por isso o realce que servia a gravura estragava
o papel e o limiar que servia a letra engolia a pauta vermelha.

Agora existe UMA selecao por pagina, e os filtros leem dela.

O ponto principal do desenho: as tres formas de marcar produzem a MESMA coisa.

    automatico  ->  regioes
    rede neural ->  regioes      -> uma lista so, na ordem em que foram feitas
    a mao       ->  regioes

Nao ha caminho separado para a rede. Ela desenha no mesmo lugar que a mao, e
por isso da para corrigir por cima do que ela fez, apagar o que ela errou e
somar o que ela nao viu. Se fossem sistemas separados, a correcao manual teria
de ser refeita toda vez que a rede rodasse de novo.

Guardamos FORMA, e nao imagem. Um retangulo sao dois pontos, um traco de
pincel e uma linha com espessura. Isso mantem o arquivo de projeto pequeno,
sobrevive a mudanca de resolucao - a mesma selecao vale na previa de 150 DPI e
na exportacao de 600 - e permite desfazer regiao por regiao.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Any

import cv2
import numpy as np

# --- o que uma regiao pode ser ---------------------------------------------

GRAVURA = "gravura"     # desenho, foto, iluminura: tom continuo, nao binarizar
LETRA = "letra"         # texto e traco: contraste e nitidez, sem realce de fundo
PAPEL = "papel"         # fundo: pode ir a branco sem pena
FORA = "fora"           # nao entra no resultado (sombra da lombada, borda do scanner)

TIPOS = (GRAVURA, LETRA, PAPEL, FORA)

NOMES_AMIGAVEIS = {
    GRAVURA: "Gravura ou foto",
    LETRA: "Letra e traço",
    PAPEL: "Papel",
    FORA: "Fora da página",
}

# --- de que jeito ela foi desenhada -----------------------------------------

RETANGULO = "retangulo"
POLIGONO = "poligono"
TRACO = "traco"         # pincel: uma linha com espessura
ELIPSE = "elipse"

FORMAS = (RETANGULO, POLIGONO, TRACO, ELIPSE)

# --- somar ou tirar ---------------------------------------------------------

SOMAR = "somar"
SUBTRAIR = "subtrair"

# --- quem desenhou ----------------------------------------------------------

AUTOMATICO = "automatico"
REDE = "rede"
MAO = "mao"

ORIGENS = (AUTOMATICO, REDE, MAO)


@dataclass
class Regiao:
    """Uma area marcada da pagina.

    Os pontos sao FRACOES de 0 a 1, relativas a largura e a altura da pagina.
    Guardar em fracao e o que faz a mesma selecao valer na miniatura, na previa
    e na exportacao em qualquer DPI.
    """

    tipo: str = GRAVURA
    forma: str = RETANGULO
    pontos: list[tuple[float, float]] = field(default_factory=list)
    operacao: str = SOMAR
    origem: str = MAO

    # so para TRACO: espessura do pincel, em fracao da MENOR dimensao da pagina
    espessura: float = 0.02

    # so para o que veio da rede ou do automatico
    confianca: float = 1.0
    rotulo: str = ""        # o nome que o detector deu, para o relatorio

    # suavizacao da borda, em fracao da menor dimensao. Zero e corte seco.
    suavidade: float = 0.0

    def valida(self) -> bool:
        if self.tipo not in TIPOS or self.forma not in FORMAS:
            return False
        minimo = {RETANGULO: 2, ELIPSE: 2, POLIGONO: 3, TRACO: 1}[self.forma]
        return len(self.pontos) >= minimo

    # --- serializacao -------------------------------------------------------

    def para_dicionario(self) -> dict[str, Any]:
        dados = asdict(self)
        dados["pontos"] = [[float(x), float(y)] for x, y in self.pontos]
        return dados

    @staticmethod
    def de_dicionario(dados: dict[str, Any]) -> "Regiao":
        validos = {c.name for c in fields(Regiao)}
        limpos = {k: v for k, v in dados.items() if k in validos}
        pontos = limpos.get("pontos") or []
        limpos["pontos"] = [(float(p[0]), float(p[1])) for p in pontos if len(p) >= 2]
        return Regiao(**limpos)


def _pixels(pontos, largura: int, altura: int) -> np.ndarray:
    return np.array(
        [[int(round(x * largura)), int(round(y * altura))] for x, y in pontos],
        dtype=np.int32,
    )


def _desenhar(tela: np.ndarray, regiao: Regiao) -> None:
    """Pinta a regiao de 255 na tela dada."""
    altura, largura = tela.shape[:2]
    pts = _pixels(regiao.pontos, largura, altura)

    if regiao.forma == RETANGULO and len(pts) >= 2:
        x0, y0 = pts[0]
        x1, y1 = pts[1]
        cv2.rectangle(tela, (min(x0, x1), min(y0, y1)), (max(x0, x1), max(y0, y1)),
                      255, thickness=-1)

    elif regiao.forma == ELIPSE and len(pts) >= 2:
        x0, y0 = pts[0]
        x1, y1 = pts[1]
        centro = ((x0 + x1) // 2, (y0 + y1) // 2)
        eixos = (max(1, abs(x1 - x0) // 2), max(1, abs(y1 - y0) // 2))
        cv2.ellipse(tela, centro, eixos, 0, 0, 360, 255, thickness=-1)

    elif regiao.forma == POLIGONO and len(pts) >= 3:
        cv2.fillPoly(tela, [pts], 255)

    elif regiao.forma == TRACO and len(pts) >= 1:
        grossura = max(1, int(round(regiao.espessura * min(largura, altura))))
        if len(pts) == 1:
            cv2.circle(tela, tuple(pts[0]), max(1, grossura // 2), 255, -1)
        else:
            cv2.polylines(tela, [pts], False, 255, thickness=grossura,
                          lineType=cv2.LINE_8)
            # ponta redonda nas duas extremidades, senao o traco fica quadrado
            for ponta in (pts[0], pts[-1]):
                cv2.circle(tela, tuple(ponta), max(1, grossura // 2), 255, -1)


@dataclass
class Selecao:
    """Todas as regioes de uma pagina, na ordem em que foram feitas.

    A ordem importa: uma regiao de subtrair so apaga o que veio ANTES dela.
    E o que permite "a rede marcou a gravura inteira, eu tirei o pedaco de
    texto que ela pegou junto".
    """

    regioes: list[Regiao] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.regioes)

    @property
    def vazia(self) -> bool:
        return not self.regioes

    def acrescentar(self, regiao: Regiao) -> None:
        if regiao.valida():
            self.regioes.append(regiao)

    def limpar_origem(self, origem: str) -> int:
        """Tira tudo que veio de uma origem. Devolve quantas saíram.

        E o que faz "rodar a deteccao de novo" nao apagar o trabalho manual:
        limpa so o que a maquina desenhou e mantem o que a pessoa fez.
        """
        antes = len(self.regioes)
        self.regioes = [r for r in self.regioes if r.origem != origem]
        return antes - len(self.regioes)

    def mascara(self, altura: int, largura: int, tipo: str) -> np.ndarray:
        """A mascara booleana de um tipo, no tamanho pedido.

        Percorre as regioes na ordem: as de somar acendem, as de subtrair
        apagam. So contam as do tipo pedido.
        """
        tela = np.zeros((altura, largura), np.uint8)
        for regiao in self.regioes:
            if regiao.tipo != tipo or not regiao.valida():
                continue
            camada = np.zeros_like(tela)
            _desenhar(camada, regiao)
            if regiao.operacao == SOMAR:
                tela = np.maximum(tela, camada)
            else:
                tela[camada > 0] = 0
        return tela > 0

    def peso(self, altura: int, largura: int, tipo: str) -> np.ndarray:
        """A mesma coisa, mas de 0 a 1 e com a borda suavizada.

        Serve para misturar tratamentos sem deixar emenda visivel: um corte
        seco entre a area tratada e a nao tratada aparece como degrau na
        impressao. A suavidade sai da regiao mais suave daquele tipo.
        """
        dura = self.mascara(altura, largura, tipo).astype(np.float32)
        suavidades = [r.suavidade for r in self.regioes
                      if r.tipo == tipo and r.suavidade > 0]
        if not suavidades:
            return dura
        raio = max(suavidades) * min(altura, largura)
        sigma = max(0.6, raio / 2.0)
        return np.clip(cv2.GaussianBlur(dura, (0, 0), sigmaX=sigma, sigmaY=sigma), 0, 1)

    def tipos_presentes(self) -> list[str]:
        return [t for t in TIPOS if any(r.tipo == t for r in self.regioes)]

    def resumo_em_portugues(self) -> str:
        """Uma frase para a tela, sem jargao."""
        if self.vazia:
            return "Nada marcado nesta página."
        contagem: dict[str, int] = {}
        for r in self.regioes:
            contagem[r.tipo] = contagem.get(r.tipo, 0) + 1
        partes = [f"{n} de {NOMES_AMIGAVEIS.get(t, t).lower()}"
                  for t, n in contagem.items()]
        if len(partes) == 1:
            return f"Marcado: {partes[0]}."
        return f"Marcado: {', '.join(partes[:-1])} e {partes[-1]}."

    # --- serializacao -------------------------------------------------------

    def para_lista(self) -> list[dict[str, Any]]:
        return [r.para_dicionario() for r in self.regioes]

    @staticmethod
    def de_lista(dados: Any) -> "Selecao":
        """Tolera arquivo de versao anterior: o que nao entender, ignora."""
        if not isinstance(dados, list):
            return Selecao()
        regioes: list[Regiao] = []
        for item in dados:
            if not isinstance(item, dict):
                continue
            try:
                regiao = Regiao.de_dicionario(item)
            except Exception:  # noqa: BLE001 - regiao estranha nao derruba o projeto
                continue
            if regiao.valida():
                regioes.append(regiao)
        return Selecao(regioes=regioes)


# --- atalhos para quem desenha ----------------------------------------------

def retangulo(x0: float, y0: float, x1: float, y1: float, tipo: str = GRAVURA,
              origem: str = MAO, **extra) -> Regiao:
    return Regiao(tipo=tipo, forma=RETANGULO, pontos=[(x0, y0), (x1, y1)],
                  origem=origem, **extra)


def poligono(pontos, tipo: str = GRAVURA, origem: str = MAO, **extra) -> Regiao:
    return Regiao(tipo=tipo, forma=POLIGONO, pontos=list(pontos),
                  origem=origem, **extra)


def traco(pontos, espessura: float = 0.02, tipo: str = GRAVURA,
          origem: str = MAO, **extra) -> Regiao:
    return Regiao(tipo=tipo, forma=TRACO, pontos=list(pontos),
                  espessura=espessura, origem=origem, **extra)


def de_mascara(mascara: np.ndarray, tipo: str = GRAVURA, origem: str = REDE,
               area_minima: float = 0.0005, **extra) -> list[Regiao]:
    """Converte uma mascara de pixels em regioes de poligono.

    E a ponte entre a rede neural e a selecao: a rede devolve pixels, e aqui
    eles viram forma editavel. Sem isto a saida da rede seria intocavel, e o
    usuario nao poderia corrigir o que ela errasse.
    """
    if mascara.dtype != np.uint8:
        mascara = mascara.astype(np.uint8)
    altura, largura = mascara.shape[:2]
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    minimo = area_minima * altura * largura
    saida: list[Regiao] = []
    for contorno in contornos:
        if cv2.contourArea(contorno) < minimo:
            continue
        # simplifica: um contorno de mil pontos nao e editavel a mao
        epsilon = 0.004 * cv2.arcLength(contorno, True)
        simples = cv2.approxPolyDP(contorno, epsilon, True)
        pontos = [(float(p[0][0]) / largura, float(p[0][1]) / altura) for p in simples]
        if len(pontos) >= 3:
            saida.append(Regiao(tipo=tipo, forma=POLIGONO, pontos=pontos,
                                origem=origem, **extra))
    return saida
