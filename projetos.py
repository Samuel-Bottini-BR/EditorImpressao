"""Os projetos salvos: o trabalho do Kaique sobrevive a fechar o programa.

Antes, "abrir de novo" guardava so o caminho do arquivo. Quem conferia 80
paginas e fechava o programa reabria do zero.

Tres coisas moram aqui:

**A assinatura do PDF.** Nunca se copia o livro para dentro do projeto - ha
livro de 300 MB no acervo, e copiar enche o disco. Guarda-se o caminho mais
alguns bytes lidos do comeco, do meio e do fim, e o tamanho. Isso separa dois
casos que dao errado de formas diferentes:

  o arquivo mudou de pasta       procura nas pastas usadas e religa sozinho
  o arquivo foi TROCADO por      a assinatura nao bate: avisa e nao aplica os
  outro de mesmo nome            ajustes salvos numa pagina que nao e aquela

O segundo e o pior desfecho possivel: aplicar corte de um livro em outro
estraga o trabalho sem ninguem perceber.

**O resumo.** Um arquivo pequeno por projeto - nome, origem, assinatura,
contagem, progresso, datas. A tela inicial monta os cartoes lendo so isso.
Abrir o historico inteiro de cinquenta projetos para desenhar cinquenta
cartoes deixaria a tela inicial lenta justamente em quem mais usa o programa.

**Salvar sozinho.** Nunca perguntar "quer salvar?". Essa pergunta e uma
armadilha para quem nao e tecnico: um "nao" por engano apaga um dia de
trabalho. Toda acao grava na hora.
"""

from __future__ import annotations

import atexit
import json
import os
import threading
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

import historico

# Quanto se le de cada ponta do arquivo para a assinatura. 64 KB do comeco, do
# meio e do fim: o suficiente para dois PDFs diferentes divergirem, e barato o
# bastante para nao pesar ao abrir a tela inicial com cinquenta projetos.
PEDACO_DA_ASSINATURA = 64 * 1024

# Onde procurar um PDF que saiu do lugar, alem da pasta original.
PASTAS_ONDE_PROCURAR = 8

ARQUIVO_RESUMO = "resumo.json"
ARQUIVO_MINIATURA = "capa.png"


def _sem_acento(texto: str) -> str:
    """Caminhos de disco vao sem acento - e regra do projeto."""
    limpo = unicodedata.normalize("NFKD", texto)
    limpo = "".join(c for c in limpo if not unicodedata.combining(c))
    permitido = [c if (c.isalnum() or c in " -_") else "-" for c in limpo]
    return " ".join("".join(permitido).split()).strip("-. ") or "projeto"


# --- a assinatura -----------------------------------------------------------


def assinatura_do_arquivo(caminho: str | Path) -> str:
    """Poucos bytes que identificam ESTE arquivo, sem copiar o livro.

    Le tres pedacos - comeco, meio e fim - e junta com o tamanho. Ler so o
    comeco nao serve: dois PDFs do mesmo digitalizador comecam iguais.
    """
    from hashlib import blake2b

    caminho = Path(caminho)
    try:
        tamanho = caminho.stat().st_size
    except OSError:
        return ""

    resumo = blake2b(digest_size=16)
    resumo.update(str(tamanho).encode())
    try:
        with caminho.open("rb") as arquivo:
            for posicao in (0, max(0, tamanho // 2 - PEDACO_DA_ASSINATURA // 2),
                            max(0, tamanho - PEDACO_DA_ASSINATURA)):
                arquivo.seek(posicao)
                resumo.update(arquivo.read(PEDACO_DA_ASSINATURA))
    except OSError:
        return ""
    return resumo.hexdigest()


def _pastas_conhecidas() -> list[Path]:
    """Onde procurar um livro que saiu do lugar: as pastas ja usadas."""
    vistas: list[Path] = []
    for resumo in listar():
        pasta = Path(resumo.caminho_entrada).parent
        if pasta.is_dir() and pasta not in vistas:
            vistas.append(pasta)
    for entrada in historico.carregar():
        pasta = Path(entrada.caminho_entrada).parent
        if pasta.is_dir() and pasta not in vistas:
            vistas.append(pasta)
    return vistas[:PASTAS_ONDE_PROCURAR]


# O que se descobre ao tentar reabrir um projeto.
ACHOU = "achou"                  # o arquivo esta la, e e ele mesmo
RELIGADO = "religado"            # mudou de pasta; achamos e religamos
SUMIU = "sumiu"                  # nao esta em lugar nenhum que conhecemos
TROCADO = "trocado"              # ha um arquivo com esse nome, mas e OUTRO


def procurar_o_livro(resumo: Resumo) -> tuple[str, str]:
    """Onde esta o PDF deste projeto? Devolve (situacao, caminho).

    Nunca devolve um caminho de arquivo cuja assinatura nao bata: aplicar os
    ajustes de um livro em outro estraga o trabalho em silencio.
    """
    original = Path(resumo.caminho_entrada)
    if original.is_file():
        if not resumo.assinatura:
            return ACHOU, str(original)          # projeto antigo, sem assinatura
        if assinatura_do_arquivo(original) == resumo.assinatura:
            return ACHOU, str(original)
        return TROCADO, str(original)

    if not resumo.assinatura:
        return SUMIU, ""

    nome = original.name
    for pasta in _pastas_conhecidas():
        candidato = pasta / nome
        if candidato.is_file() and assinatura_do_arquivo(candidato) == resumo.assinatura:
            return RELIGADO, str(candidato)
    return SUMIU, ""


# --- o resumo ---------------------------------------------------------------


@dataclass
class Resumo:
    """O cartao da tela inicial, sem abrir o historico do projeto."""

    pasta: str = ""                  # a pasta do projeto em disco
    nome: str = ""                   # o nome que aparece na tela, com acento
    caminho_entrada: str = ""
    assinatura: str = ""
    caminho_saida: str = ""
    total_paginas: int = 0
    conferidas: int = 0
    pdf_gerado: bool = False
    pagina_atual: int = 0
    criado_em: str = ""
    mexido_em: str = ""
    miniatura: str = ""

    @property
    def progresso(self) -> float:
        """Fracao de 0 a 1 (paginas conferidas / total), para a barrinha do cartao."""
        if self.total_paginas <= 0:
            return 0.0
        return min(1.0, self.conferidas / self.total_paginas)

    @property
    def frase_do_progresso(self) -> str:
        """O texto embaixo da barra: "pronto", "ainda nao olhado" ou "X de Y conferidas"."""
        if self.pdf_gerado:
            return "pronto, PDF gerado"
        if self.total_paginas <= 0:
            return "ainda não olhado"
        return f"{self.conferidas} de {self.total_paginas} conferidas"

    @property
    def data_amigavel(self) -> str:
        """Linguagem comum quando for recente - "ontem", "há 3 dias"."""
        try:
            quando = datetime.fromisoformat(self.mexido_em or self.criado_em)
        except ValueError:
            return self.mexido_em or ""
        dias = (datetime.now().date() - quando.date()).days
        if dias <= 0:
            return "hoje"
        if dias == 1:
            return "ontem"
        if dias < 7:
            return f"há {dias} dias"
        return quando.strftime("%d/%m/%Y")


def pasta_dos_projetos() -> Path:
    """A pasta-mae onde cada projeto tem a sua subpasta (atalho para
    historico.pasta_de_projetos)."""
    return historico.pasta_de_projetos()


def _caminho_do_resumo(pasta: Path) -> Path:
    """Onde o resumo.json de UM projeto mora."""
    return Path(pasta) / ARQUIVO_RESUMO


def gravar_resumo(resumo: Resumo, por_tras: bool = False) -> None:
    """Grava o resumo. Nunca levanta: perder o resumo nao pode travar nada.

    por_tras=True (o relogio de salvar, via atualizar; R1 de 05/10/2026): a
    escrita vai para o fio de gravar (_Gravador), como o projeto.json - criar
    um arquivo no disco USB das conferencias chegou a parar a janela 0,4 s.
    Sem por_tras, espera antes a fila (a ordem no disco nao muda)."""
    pasta = Path(resumo.pasta)
    resumo.mexido_em = datetime.now().isoformat(timespec="seconds")
    if not resumo.criado_em:
        resumo.criado_em = resumo.mexido_em
    dados = asdict(resumo)
    if por_tras:
        _GRAVADOR.pedir(("resumo", str(pasta)), lambda: _escrever_resumo(pasta, dados))
        return
    esperar_gravacoes()
    _escrever_resumo(pasta, dados)


def _escrever_resumo(pasta: Path, dados: dict) -> None:
    """A parte de disco de gravar_resumo. Nunca levanta.

    Escreve num arquivo ao lado e troca, como o projeto.json (O1 do
    verificador-2, 06/10/2026): antes era write_text direto por cima, e um
    resumo.json pela metade fazia o projeto SUMIR da lista (listar pula a
    pasta) com o projeto.json intacto ao lado. Arriscado: voltar a escrever
    direto por cima.

    Pasta que nao existe mais nao e recriada (R-B do verificador-3,
    06/10/2026; ver _pasta_existe): o resumo.json e o que poe o cartao na
    tela inicial, e um projeto tirado da lista voltava por aqui."""
    try:
        if not _pasta_existe(pasta):
            return
        _escrever_e_trocar(_caminho_do_resumo(pasta),
                           json.dumps(dados, ensure_ascii=False, indent=1))
    except OSError:
        pass


def _pasta_existe(pasta: Path) -> bool:
    """A pasta do projeto ainda esta no disco? As gravacoes do projeto
    (_escrever_resumo, _gravar_no_disco) so escrevem se estiver.

    R-B do verificador-3 (06/10/2026): "Tirar da lista" o livro aberto e
    depois fechar o programa (ou o relogio de salvar disparar, ou a
    conversao das zonas terminar) recriava a pasta com mkdir, e o cartao
    voltava para a lista. A janela ja solta o livro tirado
    (ui/janela_principal._soltar_o_livro_tirado_da_lista); isto e a segunda
    camada, para qualquer caminho que ainda pedir uma gravacao depois (uma
    gravacao por tras que ja estava na fila, um caminho novo da janela).

    Ressalva: se a pasta sumir por outro motivo com o livro aberto (alguem
    apagou a pasta de dados), o trabalho deixa de ser gravado em vez de
    recriar a pasta. Arriscado: recriar a pasta aqui (o projeto tirado da
    lista volta)."""
    try:
        return pasta.is_dir()
    except OSError:
        return False


def ler_resumo(pasta: str | Path) -> Resumo | None:
    """Le o resumo.json de uma pasta de projeto. Espera antes as gravacoes
    por tras.

    None se o resumo.json nao existe (pasta que nao e projeto, ou o que
    sobrou de um "Tirar da lista" que nao conseguiu apagar tudo: nao pode
    voltar para a lista) ou nao da para ler o arquivo (sem permissao).
    Se ele existe mas esta estragado (pela metade, vazio, nao e JSON), e
    refeito a partir do projeto.json (_refazer_resumo; O1 do verificador-2,
    06/10/2026) - antes devolvia None, e o projeto sumia da lista."""
    esperar_gravacoes()
    pasta = Path(pasta)
    caminho = _caminho_do_resumo(pasta)
    if not caminho.is_file():
        return None
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        if not isinstance(dados, dict):
            raise ValueError("o resumo nao e um dicionario")
        conhecidos = {campo for campo in Resumo().__dict__}
        resumo = Resumo(**{c: v for c, v in dados.items() if c in conhecidos})
    except OSError:
        return None
    except (ValueError, TypeError):
        return _refazer_resumo(pasta)
    resumo.pasta = str(pasta)          # a pasta manda, e nao o que estava escrito
    return resumo


def _refazer_resumo(pasta: Path) -> Resumo | None:
    """Monta de novo o resumo de um projeto cujo resumo.json estragou, a
    partir do projeto.json ao lado, e o grava. None se nao ha projeto.json
    legivel com o caminho do livro (ai nao ha o que mostrar no cartao).

    O que volta: o livro (caminho_entrada), o nome (o do projeto, com o
    "(2)" da pasta quando houver), o PDF de saida, o total de paginas e as
    conferidas, a capa (capa.png, se existir) e as datas (a do projeto.json).
    O que se perde: um nome trocado pelo "Renomear", a pagina em que
    parou (volta na 1a), o "pronto, PDF gerado".

    A assinatura e recalculada do PDF que esta no caminho do livro, se ele
    existir; sem o PDF, fica vazia (o cartao oferece "procurar de novo").
    Ressalva: se o PDF desse caminho tiver sido TROCADO por outro, a
    assinatura nova seria a do outro - mas o resumo vazio tambem aceitaria
    qualquer arquivo nesse caminho (procurar_o_livro), e a conferencia so
    volta se o numero de folhas e de paginas bater (combina_com). Arriscado:
    refazer sem projeto.json (o cartao apontaria para lugar nenhum), ou
    refazer quando o resumo.json NAO existe (traria de volta o projeto
    tirado da lista).
    """
    import re

    estado = pasta / ARQUIVO_ESTADO
    try:
        dados = json.loads(estado.read_text(encoding="utf-8"))
        quando = datetime.fromtimestamp(estado.stat().st_mtime).isoformat(timespec="seconds")
    except (OSError, ValueError):
        return None
    if not isinstance(dados, dict) or not dados.get("caminho_entrada"):
        return None
    caminho = str(dados["caminho_entrada"])
    paginas = [p for p in (dados.get("paginas") or []) if isinstance(p, dict)]
    nome = str(dados.get("nome") or Path(caminho).stem or pasta.name)
    numero = re.search(r" \(\d+\)$", pasta.name)
    if numero and not nome.endswith(numero.group(0)):
        nome += numero.group(0)
    capa = pasta / ARQUIVO_MINIATURA
    resumo = Resumo(
        pasta=str(pasta),
        nome=nome,
        caminho_entrada=caminho,
        assinatura=assinatura_do_arquivo(caminho) if Path(caminho).is_file() else "",
        caminho_saida=str(dados.get("caminho_saida") or ""),
        total_paginas=len(paginas),
        conferidas=sum(1 for p in paginas if p.get("revisada")),
        criado_em=quando,
        mexido_em=quando,
        miniatura=str(capa) if capa.is_file() else "",
    )
    _escrever_resumo(pasta, asdict(resumo))
    return resumo


def listar() -> list[Resumo]:
    """Todos os projetos, do mexido mais recentemente para o mais antigo."""
    raiz = pasta_dos_projetos()
    if not raiz.is_dir():
        return []
    achados = []
    for pasta in raiz.iterdir():
        if not pasta.is_dir():
            continue
        resumo = ler_resumo(pasta)
        if resumo is not None:
            achados.append(resumo)
    achados.sort(key=lambda r: r.mexido_em or r.criado_em, reverse=True)
    return achados


def _pasta_livre(nome: str) -> tuple[Path, str]:
    """Pasta em disco sem acento, numerando quando ja houver igual.

    Dois projetos do mesmo PDF sao permitidos - e o nome na tela ganha o
    numero junto, senao a pessoa ve dois cartoes identicos.
    """
    raiz = pasta_dos_projetos()
    raiz.mkdir(parents=True, exist_ok=True)
    base = _sem_acento(nome)
    pasta = raiz / base
    if not pasta.exists():
        return pasta, nome
    numero = 2
    while (raiz / f"{base} ({numero})").exists():
        numero += 1
    return raiz / f"{base} ({numero})", f"{nome} ({numero})"


def criar(projeto, total_paginas: int = 0) -> Resumo:
    """Abre um projeto novo em disco e devolve o resumo dele."""
    nome_pedido = projeto.nome or Path(projeto.caminho_entrada).stem
    pasta, nome_na_tela = _pasta_livre(nome_pedido)
    pasta.mkdir(parents=True, exist_ok=True)
    resumo = Resumo(
        pasta=str(pasta),
        nome=nome_na_tela,
        caminho_entrada=projeto.caminho_entrada,
        assinatura=assinatura_do_arquivo(projeto.caminho_entrada),
        caminho_saida=projeto.caminho_saida,
        total_paginas=total_paginas,
    )
    gravar_resumo(resumo)
    return resumo


def atualizar(resumo: Resumo, projeto, pagina_atual: int | None = None,
              por_tras: bool = False) -> Resumo:
    """Anota o andamento. Chamado a cada acao - e por isso tem de ser barato.
    por_tras: ver gravar_resumo."""
    resumo.caminho_saida = projeto.caminho_saida or resumo.caminho_saida
    resumo.total_paginas = len(projeto.paginas) or resumo.total_paginas
    resumo.conferidas = sum(1 for p in projeto.paginas if p.revisada)
    if pagina_atual is not None:
        resumo.pagina_atual = int(pagina_atual)
    gravar_resumo(resumo, por_tras=por_tras)
    return resumo


# --- o estado da conferencia -----------------------------------------------

ARQUIVO_ESTADO = "projeto.json"


def salvar_estado(resumo: Resumo, projeto) -> None:
    """Grava o trabalho da pagina: filtro, corte, angulo, marcacao, tudo.
    Quando volta, o projeto.json ja esta no disco (fechar o programa, trocar
    de livro, processar e os testes dependem disso).

    Antes de gravar, espera as gravacoes por tras que ainda estejam na fila
    (salvar_estado_por_tras): a ordem no disco e sempre a ordem dos pedidos.

    Nunca levanta. Falhar ao gravar nao pode derrubar a tela em que a pessoa
    esta trabalhando - o pior caso aceitavel e perder a ultima acao, e nao a
    sessao inteira.
    """
    try:
        pasta = Path(resumo.pasta)
        dados = projeto.para_dicionario()
    except (ValueError, TypeError):
        return
    esperar_gravacoes()
    _gravar_no_disco(pasta, dados)


def salvar_estado_por_tras(resumo: Resumo, projeto) -> None:
    """Como salvar_estado, mas a parte de DISCO (as zonas na folha, o texto
    do JSON, a copia de seguranca, escrever e trocar o arquivo) fica para um
    fio de fundo (_Gravador): volta em centesimos de segundo.

    POR QUE EXISTE (R1 do verificador, 05/10/2026): o relogio de salvar da
    janela (ui/janela_principal._salvar_por_tras) grava o projeto inteiro a
    cada pagina folheada. Num livro de 268 paginas sao 3 a 6 MB: medido,
    0,25 a 0,37 s com a janela parada a cada pagina (o fio da janela ficava
    dentro do write), e mais quando o disco demora (o D: das conferencias e
    um disco USB; disco ocupado ou computador sem memoria livre seguram a
    escrita). Aqui o fio da janela so tira a fotografia do projeto
    (Projeto.fotografar, ~0,03 s) - o que tem de ser no fio da janela,
    porque e ele que mexe no projeto.

    Pedidos seguidos para a mesma pasta se juntam: so o ultimo e gravado
    (cada um e o projeto inteiro). Nunca levanta. Arriscado: gravar no fio de
    fundo um dicionario que a janela ainda mexe (por isso a fotografia e
    uma copia), ou esquecer de esperar_gravacoes() antes de ler ou mexer no
    projeto.json.
    """
    try:
        pasta = Path(resumo.pasta)
        fotografia = projeto.fotografar()
    except (ValueError, TypeError):
        return

    def gravar() -> None:
        from modelos import Projeto

        _gravar_no_disco(pasta, Projeto.para_o_disco(fotografia))

    _GRAVADOR.pedir(("estado", str(pasta)), gravar)


def esperar_gravacoes(limite_s: float | None = None) -> bool:
    """Espera as gravacoes por tras (salvar_estado_por_tras) chegarem ao
    disco. True se nao ficou nenhuma. Quem le ou mexe no projeto.json chama
    antes; o fechar do programa tambem (via salvar_estado)."""
    return _GRAVADOR.esperar(limite_s)


def _gravar_no_disco(pasta: Path, dados: dict) -> None:
    """A parte de disco de uma gravacao (no fio de quem chamou: a janela em
    salvar_estado, o _Gravador em salvar_estado_por_tras). Uma de cada vez
    (_TRAVA_DO_DISCO). Nunca levanta.

    Nao grava numa pasta de projeto que nao existe mais, e nunca a recria
    (R-B do verificador-3, 06/10/2026): e o projeto que a pessoa tirou da
    lista ("Tirar da lista" apaga a pasta), e recria-la trazia o cartao de
    volta. Quem cria a pasta e criar(). Arriscado: voltar o mkdir aqui."""
    with _TRAVA_DO_DISCO:
        try:
            if not _pasta_existe(pasta):
                return
            # Decisao D2 (02/10/2026): "com copia de seguranca dos projetos". A
            # primeira gravacao no formato novo (zonas na folha original) por
            # cima de um projeto.json antigo com zonas guarda o antigo antes.
            if not _copia_antes_das_zonas_na_folha(pasta, dados):
                # Sem a copia (disco cheio, sem permissao), grava no formato de
                # antes: so a "selecao" em fracao da pagina, que vale com a
                # geometria anotada. O trabalho nao deixa de ser gravado; a
                # conversao fica para a proxima gravacao que conseguir a copia.
                from core.zonas_na_folha import CAMPO_NA_FOLHA

                for pagina in dados.get("paginas", []):
                    pagina.pop(CAMPO_NA_FOLHA, None)
            _escrever_estado(pasta, json.dumps(dados, ensure_ascii=False, indent=1))
        except (OSError, ValueError, TypeError):
            pass


def _escrever_estado(pasta: Path, texto: str) -> None:
    """Escreve o projeto.json. Grava num arquivo ao lado e so entao troca.
    Escrever por cima do bom deixaria o projeto pela metade se a energia
    caisse no meio - e o arquivo pela metade e justamente o que nao pode
    acontecer aqui. (Separado para os testes simularem um disco lento.)"""
    _escrever_e_trocar(pasta / ARQUIVO_ESTADO, texto)


def _escrever_e_trocar(destino: Path, texto: str) -> None:
    """Escreve `texto` em `destino` sem nunca deixar `destino` pela metade:
    grava tudo num arquivo ao lado ("<nome>.novo") e so entao o troca pelo
    de antes (os.replace, que no mesmo disco e uma troca so: ou fica o
    arquivo velho inteiro, ou o novo inteiro). Usado pelo projeto.json e
    pelo resumo.json. Levanta OSError (quem chama decide).

    Antes da troca, o arquivo novo e forcado ate o disco (os.fsync; O2 do
    verificador-2, 06/10/2026). Sem isso, numa queda de energia (ou disco
    USB puxado) logo depois, a TROCA podia ficar registrada no disco e o
    CONTEUDO novo ainda na memoria do Windows: o projeto.json ficaria vazio
    ou com lixo. Custo medido em 06/10/2026 (projeto.json de 5,7 MB do
    Siebmacher, 10 vezes): no D: (disco USB giratorio) nada a mais - 182 ms
    com e sem, o Windows ja grava direto nesse disco; no C: (NVMe) +14 ms
    (18 -> 32 ms), e +12 ms no resumo.json. O relogio de salvar grava por
    tras, entao a janela nao espera; fechar, trocar de livro e processar
    esperam esses milissegundos a mais.

    Arriscado: escrever direto em `destino`; tirar o fsync ou po-lo depois
    da troca; o ".novo" em outro disco (a troca deixa de ser uma so).
    Texto em modo texto (fim de linha do Windows), como o write_text de
    antes: os bytes gravados nao mudam."""
    temporario = destino.with_name(destino.name + ".novo")
    with open(temporario, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)
        arquivo.flush()
        os.fsync(arquivo.fileno())
    os.replace(temporario, destino)


# Uma gravacao no disco por vez, venha da janela ou do fio de fundo.
_TRAVA_DO_DISCO = threading.Lock()


class _Gravador:
    """O fio que grava por tras (salvar_estado_por_tras e atualizar com
    por_tras=True). Um so, criado na primeira gravacao; guarda so o ULTIMO
    pedido de cada arquivo (chave: o que e + a pasta).

    O fio e daemon (nao segura o programa aberto), por isso o fechar da
    janela grava com salvar_estado, que espera a fila antes; e ha um atexit
    que espera ate 10 s, para o caso de o programa sair por outro caminho.
    Seguro mudar: o limite do atexit. Arriscado: mais de um fio (a ordem das
    gravacoes de uma pasta deixaria de ser garantida).
    """

    def __init__(self) -> None:
        self._condicao = threading.Condition()
        self._fila: dict[tuple, Callable[[], None]] = {}
        self._gravando = False
        self._fio: threading.Thread | None = None

    def pedir(self, chave: tuple, trabalho: Callable[[], None]) -> None:
        """Poe `trabalho` (uma gravacao inteira, que nunca levanta) na fila,
        no lugar do pedido anterior com a mesma chave, se ele ainda nao
        comecou."""
        with self._condicao:
            self._fila[chave] = trabalho           # o mais novo substitui
            if self._fio is None or not self._fio.is_alive():
                self._fio = threading.Thread(target=self._rodar, daemon=True,
                                             name="gravar o projeto")
                self._fio.start()
            self._condicao.notify_all()

    def esperar(self, limite_s: float | None = None) -> bool:
        if threading.current_thread() is self._fio:
            return True                    # o proprio fio de gravar: nao espera a si mesmo
        with self._condicao:
            return self._condicao.wait_for(
                lambda: not self._fila and not self._gravando, timeout=limite_s)

    def _rodar(self) -> None:
        while True:
            with self._condicao:
                while not self._fila:
                    self._condicao.wait()
                trabalho = self._fila.pop(next(iter(self._fila)))
                self._gravando = True
            try:
                trabalho()
            except Exception:  # noqa: BLE001 - o fio de gravar nunca morre
                pass
            finally:
                with self._condicao:
                    self._gravando = False
                    self._condicao.notify_all()


_GRAVADOR = _Gravador()


@atexit.register
def _esperar_ao_sair() -> None:
    esperar_gravacoes(10.0)


# Pastas de projeto que ja nao precisam da copia das zonas nesta sessao: o
# projeto.json ja estava no formato novo, nao tinha zonas, ou a copia ja foi
# feita (_copia_antes_das_zonas_na_folha). Nao precisam ser lidas de novo a
# cada gravacao. Seguro esvaziar a qualquer hora (so custa ler o arquivo uma
# vez; com o arquivo ja regravado pelo programa novo, pode sair mais uma copia).
_JA_NO_FORMATO_NOVO: set[str] = set()

# Nome da copia: "projeto.antigo-zonas-na-folha-AAAA-MM-DD-HHMM.json". Tem o
# ".antigo-" de proposito: copias_do_trabalho a acha, e o "Tirar da lista" a
# guarda junto das outras copias (decisao do Samuel de 29/09).
MOTIVO_DA_COPIA_DAS_ZONAS = "zonas-na-folha"


def _copia_antes_das_zonas_na_folha(pasta: Path, dados: dict | None = None,
                                    agora: datetime | None = None) -> bool:
    """Guarda o projeto.json antigo antes de o programa novo gravar por cima
    dele (decisao D2 do Samuel, 02/10/2026: "Sim, pode mudar (com copia de
    seguranca dos projetos)").

    A copia e o arquivo EXATAMENTE como estava, byte a byte (ressalva R2 do
    verificador, 05/10/2026): por isso ela e feita antes de QUALQUER gravacao
    do programa novo por cima de um projeto.json com zonas so no formato
    antigo (core/zonas_na_folha) - inclusive a primeira, que ainda vai no
    formato antigo (a que a janela faz ao abrir, ui/janela_principal.
    _analise_pronta, antes de converter) e que ja mudaria o arquivo (acrescenta
    "geometria_das_zonas": null em cada pagina). Antes do R2 a copia so era
    feita na primeira gravacao com zonas no formato novo, e guardava o arquivo
    ja regravado. `dados` (o que vai ser gravado) nao decide mais nada; fica
    na assinatura so por compatibilidade.

    Uma vez por pasta nesta sessao (_JA_NO_FORMATO_NOVO), em modo exclusivo,
    nunca por cima de outra, e nada no programa a apaga. Os bytes copiados
    sao os mesmos que foram lidos para decidir (uma leitura so). Devolve
    False se havia o que guardar e nao deu (ai quem chama grava no formato
    de antes, sem converter: o trabalho e gravado e a conversao espera).
    Arriscado: devolver True sem a copia feita; voltar a exigir que `dados`
    esteja no formato novo (a copia voltaria a ser do arquivo ja regravado).
    """
    from core.zonas_na_folha import tem_formato_novo, tem_zonas_no_formato_antigo

    chave = str(pasta.resolve())
    if chave in _JA_NO_FORMATO_NOVO:
        return True
    estado = pasta / ARQUIVO_ESTADO
    try:
        bytes_antigos = estado.read_bytes() if estado.is_file() else None
    except OSError:
        return False                  # existe e nao deu para ler: tenta na proxima
    if bytes_antigos is None:
        _JA_NO_FORMATO_NOVO.add(chave)
        return True
    try:
        antigo = json.loads(bytes_antigos.decode("utf-8"))
    except ValueError:
        antigo = {"paginas": [{"selecao": ["?"]}]}   # ilegivel: a copia guarda os bytes
    if tem_formato_novo(antigo) or not tem_zonas_no_formato_antigo(antigo):
        _JA_NO_FORMATO_NOVO.add(chave)
        return True
    carimbo = (agora or datetime.now()).strftime("%Y-%m-%d-%H%M")
    for numero in range(1, 1000):
        sufixo = carimbo if numero == 1 else f"{carimbo}-{numero}"
        destino = pasta / f"projeto.antigo-{MOTIVO_DA_COPIA_DAS_ZONAS}-{sufixo}.json"
        try:
            with destino.open("xb") as copia:
                copia.write(bytes_antigos)
                _forcar_ao_disco(copia)
        except FileExistsError:
            continue
        except OSError:
            return False
        _JA_NO_FORMATO_NOVO.add(chave)
        return True
    return False


def _forcar_ao_disco(arquivo) -> None:
    """Forca o que foi escrito em `arquivo` (aberto) ate o disco (os.fsync).
    Para as copias de seguranca (O2 do verificador-2, 06/10/2026): elas tem
    de estar no disco ANTES de o projeto.json de antes ser trocado, senao
    uma queda de energia logo depois poderia deixar o projeto.json novo e a
    copia vazia. Uma vez por copia (raro), entao o custo nao pesa."""
    arquivo.flush()
    os.fsync(arquivo.fileno())


def guardar_copia_do_trabalho(resumo: Resumo, agora: datetime | None = None) -> Path | None:
    """Guarda ao lado uma copia do trabalho salvo, antes de ele ser regravado.

    Rede de seguranca pedida pela gerente em 29/09/2026 (bug grave "livro que
    mudou de pasta perde o trabalho de vez"): quando a conferencia recomeca
    por cima de um projeto salvo (ui/janela_principal.py, _analise_pronta),
    o projeto.json antigo ia embora na hora. Agora ele fica, com data e hora
    no nome, e nada e apagado:

        projeto.antigo-2026-09-29-1930.json
        acoes.antigo-2026-09-29-1930.jsonl      (o Historico de acoes)
        posicao.antigo-2026-09-29-1930.json     (onde o desfazer estava)

    O acoes.jsonl e o posicao.json vao junto para a copia ficar inteira: e
    com os tres que se remonta o trabalho de antes. Desde 06/10/2026 (Lista
    de bugs: o Ctrl+Z da conferencia recomecada desfazia acoes da anterior),
    a janela, logo depois desta copia, tira os dois do caminho
    (historico_acoes.HistoricoAcoes.recomecar): o historico antigo fica so
    aqui, na copia, e o da conferencia nova comeca vazio. Arriscado: mudar
    os nomes da copia sem mudar HistoricoAcoes._ja_estao_na_copia (que acha
    o acoes.antigo-<data>.jsonl pelo nome do projeto.antigo-<data>.json; se
    nao achar, o historico e guardado de novo, a parte, e nada se perde).

    Nunca sobrescreve copia anterior: se ja ha copia naquele minuto, a nova
    ganha "-2", "-3"... e cada arquivo e criado em modo exclusivo ("x"), que
    falha em vez de escrever por cima. Devolve o caminho da copia do
    projeto.json, ou None se nao havia projeto salvo (ou nao deu para
    copiar). Nunca levanta: nao poder copiar nao pode derrubar a abertura do
    livro - mas ai quem chama deve saber que nao ha copia (None).
    """
    from historico_acoes import ARQUIVO_ACOES, ARQUIVO_POSICAO

    esperar_gravacoes()                   # copia o que ja chegou ao disco
    pasta = Path(resumo.pasta)
    estado = pasta / ARQUIVO_ESTADO
    if not estado.is_file():
        return None
    carimbo = (agora or datetime.now()).strftime("%Y-%m-%d-%H%M")
    origens = [pasta / nome for nome in (ARQUIVO_ESTADO, ARQUIVO_ACOES, ARQUIVO_POSICAO)]

    def destino(origem: Path, sufixo: str) -> Path:
        return origem.with_name(f"{origem.stem}.antigo-{sufixo}{origem.suffix}")

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
                    _forcar_ao_disco(copia)          # O2: no disco antes do regravar
        except FileExistsError:
            continue                 # outra copia nasceu no mesmo instante
        except OSError:
            return None
        return destino(estado, sufixo)
    return None


def tem_trabalho_salvo(resumo: Resumo) -> bool:
    """Ha trabalho de conferencia gravado neste projeto (que nao pode ser
    regravado por um projeto ainda nao analisado)?

    Sim quando o projeto.json existe e tem paginas, ou quando existe mas nao
    da para ler (pode ser recuperado a mao; regravar apagaria). Nao quando
    nao existe, ou quando so tem as opcoes (0 paginas: o livro foi aberto e
    fechado no "O que fazer" sem nunca ter sido conferido).

    Usado por ui/janela_principal.py (_salvar_agora) - bug grave de
    29/09/2026 achado pelo verificador: abrir um livro salvo e fechar o
    programa antes do fim da analise gravava um projeto vazio por cima do
    trabalho. Le o arquivo inteiro: so e chamado antes de a analise acabar.
    Arriscado: devolver False para arquivo ilegivel.
    """
    esperar_gravacoes()                   # le o que esta na fila de gravar
    caminho = Path(resumo.pasta) / ARQUIVO_ESTADO
    if not caminho.is_file():
        return False
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True
    return not isinstance(dados, dict) or bool(dados.get("paginas"))


def anotar_no_estado(resumo: Resumo, **campos) -> bool:
    """Muda so alguns campos de cima do projeto.json gravado, sem tocar no
    resto (paginas, folhas, trabalho). Devolve False se nao ha projeto.json
    legivel (ai nada e gravado).

    Existe para o que precisa ficar gravado ANTES de o trabalho ser carregado
    (entre abrir o livro e o fim da analise, quando _salvar_agora nao grava
    por cima do trabalho salvo): hoje, que a pergunta do fundo ja foi feita
    (Projeto.perguntou_fundo, item 1.1). Grava num arquivo ao lado e troca,
    como salvar_estado. Nunca levanta. Arriscado: usar para mudar paginas ou
    folhas (e trabalho de salvar_estado, com o projeto inteiro).
    """
    esperar_gravacoes()                   # na ordem das gravacoes por tras
    caminho = Path(resumo.pasta) / ARQUIVO_ESTADO
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        if not isinstance(dados, dict):
            return False
        dados.update(campos)
        # R2 (05/10/2026): a copia de seguranca do projeto.json antigo com
        # zonas vem antes de QUALQUER gravacao do programa novo, esta tambem.
        _copia_antes_das_zonas_na_folha(caminho.parent)
        # ao lado, forcado ao disco e trocado (O2, 06/10/2026)
        _escrever_e_trocar(caminho, json.dumps(dados, ensure_ascii=False, indent=1))
        return True
    except (OSError, ValueError, TypeError):
        return False


def carregar_estado(resumo: Resumo):
    """Devolve o Projeto gravado, ou None se nao houver ou nao der para ler.
    Espera antes as gravacoes por tras (salvar_estado_por_tras)."""
    from modelos import Projeto

    esperar_gravacoes()
    caminho = Path(resumo.pasta) / ARQUIVO_ESTADO
    if not caminho.is_file():
        return None
    try:
        return Projeto.de_dicionario(json.loads(caminho.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):
        return None


def _forma_comum(caminho: str | Path) -> str:
    """O caminho escrito de um jeito so, para comparar: absoluto, sem `..`,
    com a barra do sistema e, no Windows, em minusculas (os.path.normcase).

    So para COMPARAR. Nunca gravar isto no projeto nem abrir o arquivo por
    ele: o que se grava continua sendo o caminho como veio (formato de sempre).
    """
    return os.path.normcase(os.path.abspath(os.fspath(caminho)))


def mesmo_arquivo(a: str | Path, b: str | Path) -> bool:
    """Os dois caminhos apontam para o MESMO arquivo, escritos como for?

    Conserto do bug grave de 29/09/2026 (Lista de bugs, achado pelo
    verificador): o mesmo PDF chega com `\\` pela associacao de arquivo do
    Windows e com `/` pela caixa "Abrir" ou arrastando, e comparar o texto
    dizia "outro livro" - e o trabalho salvo era descartado.

    Duas etapas:
      1. a forma comum (_forma_comum): cobre `\\` x `/`, maiusculas e
         minusculas (o Windows nao diferencia), letra de unidade, caminho
         relativo e `..`. Funciona mesmo se o arquivo nao existir mais;
      2. se a forma nao bate mas os dois existem, pergunta ao sistema
         (os.path.samefile): cobre atalhos de pasta (junction), nome curto
         do DOS (PROGRA~1) e unidade mapeada para a mesma pasta.

    Caminho vazio so e "o mesmo" que outro vazio (comportamento de antes).
    Nunca levanta. Seguro mudar: acrescentar casos que devolvem True para o
    mesmo arquivo. Arriscado: qualquer coisa que devolva True para arquivos
    DIFERENTES - o trabalho de um livro seria aplicado noutro sem aviso.
    Caminho relativo e resolvido pela pasta atual do programa: dois relativos
    iguais escritos em pastas atuais diferentes nao sao comparaveis (o
    programa so recebe caminho absoluto, das caixas do Windows e do Qt).
    """
    a = os.fspath(a) if a else ""
    b = os.fspath(b) if b else ""
    if not a or not b:
        return a == b
    if a == b:
        return True
    try:
        if _forma_comum(a) == _forma_comum(b):
            return True
    except (TypeError, ValueError):
        return False
    try:
        return os.path.samefile(a, b)
    except (OSError, ValueError):
        return False


def _mesmo_livro(salvo, recem_analisado, assinatura: str) -> bool:
    """O trabalho salvo e deste livro? (Sem olhar a contagem de paginas.)

    Duas formas de ser o mesmo livro:
      1. o mesmo ARQUIVO (mesmo_arquivo): o caminho gravado e o de agora
         apontam para o mesmo lugar, escritos como for;
      2. a mesma ASSINATURA: o arquivo aberto agora tem a assinatura do
         projeto (`assinatura`, a resumo.assinatura, gravada quando o
         projeto nasceu). Cobre o livro que mudou de pasta e a copia do
         mesmo PDF em outra pasta - o caminho gravado nao existe mais, ou
         aponta para outro lugar. Bug grave de 29/09/2026: o projeto era
         achado pela assinatura, mas aqui so se olhava o caminho, e o
         trabalho ia embora.

    Assinatura vazia (projeto antigo, de antes da assinatura) nao vale: sem
    ela nao ha como saber se o outro arquivo e o mesmo livro.

    O risco do caso contrario (dois PDFs diferentes com a mesma assinatura):
    a assinatura le o tamanho e 64 KB do comeco, do meio e do fim
    (assinatura_do_arquivo). Dois PDFs diferentes so a dividem se tiverem o
    MESMO tamanho em bytes e forem iguais nesses tres pedacos - o fim de um
    PDF tem a tabela de onde fica cada objeto, que muda quando qualquer
    coisa muda de tamanho. E achar_por_assinatura ja liga o projeto ao
    arquivo por ela mesma. Arriscado: aceitar assinatura vazia, ou trocar a
    assinatura por algo mais fraco (so o nome, so o tamanho).
    """
    if mesmo_arquivo(salvo.caminho_entrada, recem_analisado.caminho_entrada):
        return True
    return bool(assinatura) and assinatura_do_arquivo(recem_analisado.caminho_entrada) == assinatura


def combina_com(salvo, recem_analisado, assinatura: str = "") -> bool:
    """O trabalho salvo pode ser aplicado neste livro recem-aberto?

    So se for o MESMO livro e a mesma divisao. Se a pessoa trocou "dividir
    folhas ao meio" entre uma sessao e outra, a pagina 40 salva nao e a pagina
    40 de agora, e devolver o corte de uma na outra estragaria o trabalho.

    "Mesmo livro" = mesmo ARQUIVO (mesmo_arquivo), e nao o mesmo texto de
    caminho: ate 29/09/2026 comparava o texto, e o mesmo PDF aberto com `/`
    depois de salvo com `\\` perdia o trabalho (bug grave da Lista de bugs).
    Ou a mesma assinatura do arquivo, quando `assinatura` (a do projeto,
    resumo.assinatura) e dada: livro que mudou de pasta ou copia em outra
    pasta (ver _mesmo_livro). Arriscado: voltar a comparar com `==`.
    """
    if salvo is None or recem_analisado is None:
        return False
    return motivo_para_nao_combinar(salvo, recem_analisado, assinatura) == ""


def _quantas(numero: int, singular: str, plural: str) -> str:
    """"1 página", "3 páginas" - para as frases da tela."""
    return f"{numero} {singular if numero == 1 else plural}"


def motivo_para_nao_combinar(salvo, recem_analisado, assinatura: str = "") -> str:
    """Por que o trabalho salvo NAO serve para este livro? "" se serve.

    E a regra de combina_com (que so pergunta se o motivo e vazio) e, ao mesmo
    tempo, o texto que a janela mostra quando a conferencia recomeca
    (ui/janela_principal.py, _analise_pronta). Pedido da gerente em
    29/09/2026: a mensagem dizia "Voce mudou as opcoes... outro numero de
    paginas" para qualquer motivo, inclusive o livro que so mudou de pasta.

    Os motivos, na ordem em que sao olhados (o primeiro que valer e o dito):
      1. nao e o mesmo livro (_mesmo_livro: nem o mesmo arquivo, nem a mesma
         assinatura);
      2. o arquivo tem outro numero de folhas (o PDF mudou);
      3. outro numero de paginas;
      4. o mesmo numero, mas outras folhas divididas (item 2.1).
    Em 3 e 4, a segunda frase diz o que mudou: a caixinha "Dividir folhas ao
    meio" ou o jeito de dividir do livro (_o_que_mudou_na_divisao).

    Frase em portugues comum, comecando em minuscula, sem ponto final (a
    janela a encaixa no meio da mensagem). Seguro mudar: o texto. Arriscado:
    a ordem ou as condicoes - elas decidem se o trabalho volta.
    """
    if not _mesmo_livro(salvo, recem_analisado, assinatura):
        return "o arquivo aberto agora não é o mesmo livro do trabalho salvo"
    antes, agora = len(salvo.folhas), len(recem_analisado.folhas)
    if antes != agora:
        return (f"o arquivo tinha {_quantas(antes, 'folha', 'folhas')} quando o "
                f"trabalho foi salvo e agora tem {agora}: ele foi trocado ou mudou")
    antes, agora = len(salvo.paginas), len(recem_analisado.paginas)
    if antes != agora:
        return (f"o trabalho salvo tinha {_quantas(antes, 'página', 'páginas')} e "
                f"agora o livro tem {agora}. "
                + _o_que_mudou_na_divisao(salvo, recem_analisado))
    # Item 2.1 (06/10/2026): com dois jeitos de dividir, o total pode bater e
    # as folhas divididas serem outras (uma folha a mais dividida num lugar,
    # uma a menos noutro): a pagina 40 salva ja nao seria a 40 de agora. Por
    # isso, alem do total, cada folha tem de ter as mesmas paginas.
    if _paginas_por_folha(salvo) != _paginas_por_folha(recem_analisado):
        return ("as folhas divididas em duas páginas não são as mesmas do trabalho "
                "salvo. " + _o_que_mudou_na_divisao(salvo, recem_analisado))
    return ""


def _o_que_mudou_na_divisao(salvo, recem_analisado) -> str:
    """A segunda frase do motivo 3 e 4 de motivo_para_nao_combinar: o que
    mudou de verdade na divisao. Parecer do verificador (06/10/2026): trocar
    so o JEITO de dividir do livro tambem muda as paginas, e o aviso falava
    em "Dividir folhas ao meio". Sem ponto final (a janela poe). Seguro
    mudar: o texto."""
    from core import dividir_scantailor

    if bool(getattr(salvo, "dividir_folhas", True)) != bool(
            getattr(recem_analisado, "dividir_folhas", True)):
        return "Isso acontece quando se muda a opção “Dividir folhas ao meio”"
    antes = dividir_scantailor.jeito_valido(getattr(salvo, "dividir_como", None))
    agora = dividir_scantailor.jeito_valido(getattr(recem_analisado, "dividir_como", None))
    if antes != agora:
        nomes = dividir_scantailor.NOMES_DOS_JEITOS
        return (f"Você trocou o jeito de dividir do livro (de “{nomes[antes]}” para "
                f"“{nomes[agora]}”), e o jeito novo divide outras folhas")
    # nenhuma das duas opcoes mudou (projeto de antes das opcoes gravadas,
    # ou o programa passou a achar outra divisao): a frase de sempre
    return ("Isso acontece quando se muda a opção “Dividir folhas ao meio” ou o "
            "jeito de dividir do livro")


def _paginas_por_folha(projeto) -> list[tuple[int, str]]:
    """(folha, metade) de cada pagina, na ordem: a "forma" da divisao do
    livro, que o trabalho salvo tem de repetir para voltar (motivo 4 de
    motivo_para_nao_combinar)."""
    return [(int(p.folha), str(p.metade)) for p in getattr(projeto, "paginas", [])]


def achar_por_assinatura(caminho_pdf: str) -> Resumo | None:
    """Ja ha um projeto deste mesmo livro? Devolve o mais recente.

    E o que faz "abrir o mesmo livro de novo" continuar de onde parou em vez de
    comecar um projeto novo ao lado do antigo.
    """
    assinatura = assinatura_do_arquivo(caminho_pdf)
    if not assinatura:
        return None
    for resumo in listar():           # ja vem do mais recente para o mais antigo
        if resumo.assinatura == assinatura:
            return resumo
    return None


# --- a miniatura do cartao --------------------------------------------------

# Altura da miniatura guardada. A area dela no cartao tem 112 px; o dobro
# aguenta uma tela em 200% sem ficar borrada, e um PNG desse tamanho nao chega
# a 30 KB.
ALTURA_DA_MINIATURA = 224


def caminho_da_miniatura(resumo: Resumo) -> Path:
    """Onde a capa.png deste projeto mora (pode nao existir ainda - ver garantir_miniatura)."""
    return Path(resumo.pasta) / ARQUIVO_MINIATURA


def garantir_miniatura(resumo: Resumo, caminho_pdf: str = "") -> str:
    """A primeira pagina do livro, gravada uma vez.

    E isto que distingue quatro projetos de nome parecido: a pessoa reconhece o
    livro pela aparencia, e nao pelo nome. Gerada uma vez e reaproveitada -
    abrir cinquenta PDFs a cada vez que a tela inicial aparece seria lento
    justamente em quem mais usa o programa.
    """
    destino = caminho_da_miniatura(resumo)
    if destino.is_file():
        return str(destino)

    origem = caminho_pdf or resumo.caminho_entrada
    if not origem or not Path(origem).is_file():
        return ""
    try:
        import cv2

        from core.pdf_io import abrir_pdf, limitar_altura, pagina_para_array

        doc = abrir_pdf(origem)
        try:
            img = pagina_para_array(doc, 0, dpi=40)
        finally:
            doc.close()
        destino.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(destino), limitar_altura(img, ALTURA_DA_MINIATURA))
    except Exception:  # noqa: BLE001 - sem capa o cartao ainda serve
        return ""

    resumo.miniatura = str(destino)
    gravar_resumo(resumo)
    return str(destino)


def refazer_miniatura_por_tras(resumo: Resumo, rotacao: int) -> None:
    """Refaz a capa.png com a primeira folha no giro `rotacao` (0/90/180/270),
    num fio de fundo (o mesmo _GRAVADOR do projeto.json).

    D2 do verificador (06/10/2026): a capa do cartao da tela inicial e a
    primeira folha do livro, desenhada uma vez como veio no PDF, e nao
    acompanhava o giro. Quem chama e a janela, quando o giro da primeira
    folha muda (ui/janela_principal._acertar_a_capa). Desenhar a folha (40
    DPI, centesimos de segundo) fica fora do fio da janela.

    Pedidos seguidos do mesmo projeto se juntam (so o ultimo vale). Nao
    grava em pasta que nao existe mais (o projeto tirado da lista nao volta,
    R-B). Nunca levanta: sem capa nova, o cartao continua com a de antes.
    Seguro mudar: a resolucao. Arriscado: desenhar no fio da janela.
    """
    pasta = Path(resumo.pasta)
    origem = resumo.caminho_entrada
    giro = int(rotacao) % 360

    def gravar() -> None:
        _escrever_miniatura(pasta, origem, giro)

    _GRAVADOR.pedir(("capa", str(pasta)), gravar)


def _escrever_miniatura(pasta: Path, origem: str, rotacao: int) -> bool:
    """Desenha a primeira folha de `origem` (como garantir_miniatura), gira e
    grava em pasta/capa.png sem nunca deixar o arquivo pela metade (arquivo
    ao lado e troca). True se gravou."""
    try:
        if not _pasta_existe(pasta) or not origem or not Path(origem).is_file():
            return False
        import cv2

        from core.endireitar import girar_90
        from core.pdf_io import abrir_pdf, limitar_altura, pagina_para_array

        doc = abrir_pdf(origem)
        try:
            img = pagina_para_array(doc, 0, dpi=40)
        finally:
            doc.close()
        if rotacao:
            img = girar_90(img, rotacao)
        certo, dados = cv2.imencode(".png", limitar_altura(img, ALTURA_DA_MINIATURA))
        if not certo:
            return False
        destino = pasta / ARQUIVO_MINIATURA
        temporario = destino.with_name(destino.name + ".novo")
        temporario.write_bytes(dados.tobytes())
        os.replace(temporario, destino)
        return True
    except Exception:  # noqa: BLE001 - sem capa nova o cartao ainda serve
        return False


PASTA_DAS_COPIAS = "copias-de-seguranca"


def copias_do_trabalho(resumo: Resumo) -> list[Path]:
    """As copias de seguranca que estao na pasta do projeto
    (projeto.antigo-*, acoes.antigo-*, posicao.antigo-*; ver
    guardar_copia_do_trabalho)."""
    esperar_gravacoes()                   # a copia das zonas sai pelo fio de gravar
    pasta = Path(resumo.pasta)
    if not pasta.is_dir():
        return []
    return sorted(c for c in pasta.glob("*.antigo-*") if c.is_file())


def pasta_das_copias_guardadas() -> Path:
    """Onde ficam as copias de seguranca de projetos tirados da lista:
    %LOCALAPPDATA%\\EditorImpressao\\copias-de-seguranca. Fora da pasta de
    projetos de proposito: la dentro, com o resumo.json copiado junto, a
    pasta viraria um cartao falso na tela inicial (listar), e ocuparia o
    nome de um projeto novo do mesmo livro."""
    return historico.pasta_de_dados() / PASTA_DAS_COPIAS


def remover_da_lista(resumo: Resumo, agora: datetime | None = None) -> Path | None:
    """Tira o projeto da tela inicial, apagando a pasta DELE - mas as copias
    de seguranca nao vao junto.

    Decisao do Samuel (29/09/2026, Registro de mudancas): "'Tirar da lista'
    nao deve apagar as copias de seguranca (projeto.antigo-*)". Antes de
    apagar a pasta, as copias (e o resumo.json, que diz de que livro sao)
    sao copiadas para pasta_das_copias_guardadas() / "<pasta do projeto>
    (tirado da lista em AAAA-MM-DD-HHMM)", com um LEIA-ME.txt. Nunca por cima
    de outra: no mesmo minuto ganha "-2", "-3"...

    Devolve a pasta onde as copias ficaram, ou None se nao havia copias. Se
    as copias NAO puderem ser guardadas (disco cheio, sem permissao), nada e
    apagado e devolve None: o cartao continua na lista. O que se perde no
    "Tirar da lista" e o trabalho atual (projeto.json) - a pergunta da tela
    inicial avisa.

    O PDF de origem nunca e tocado: ele nunca esteve aqui dentro. Arriscado:
    apagar a pasta antes de conferir que as copias foram guardadas.
    """
    import shutil

    esperar_gravacoes()                   # nada gravando na pasta que vai embora
    pasta = Path(resumo.pasta)
    raiz = pasta_dos_projetos()
    # trava de seguranca: so apaga dentro da pasta de projetos
    if not (pasta.is_dir() and raiz in pasta.parents):
        return None

    copias = copias_do_trabalho(resumo)
    guardadas = None
    if copias:
        carimbo = (agora or datetime.now()).strftime("%Y-%m-%d-%H%M")
        base = pasta_das_copias_guardadas()
        nome = f"{pasta.name} (tirado da lista em {carimbo})"
        guardadas = base / nome
        numero = 2
        while guardadas.exists():
            guardadas = base / f"{nome}-{numero}"
            numero += 1
        try:
            guardadas.mkdir(parents=True)
            for copia in copias:
                shutil.copy2(copia, guardadas / copia.name)
            resumo_do_livro = _caminho_do_resumo(pasta)
            if resumo_do_livro.is_file():
                shutil.copy2(resumo_do_livro, guardadas / ARQUIVO_RESUMO)
            (guardadas / "LEIA-ME.txt").write_text(
                f"Copias de seguranca do trabalho do livro \"{resumo.nome}\",\n"
                f"guardadas quando o projeto foi tirado da lista em {carimbo}.\n"
                f"Livro: {resumo.caminho_entrada}\n\n"
                "Cada projeto.antigo-*.json e o trabalho como estava antes de a\n"
                "conferencia recomecar; o acoes.antigo-*.jsonl e o posicao.antigo-*.json\n"
                "da mesma data e hora sao o Historico daquele momento.\n",
                encoding="utf-8")
        except OSError:
            return None                  # nada e apagado sem as copias guardadas
    try:
        shutil.rmtree(pasta, ignore_errors=True)
    except OSError:
        pass
    return guardadas


def renomear(resumo: Resumo, novo_nome: str) -> Resumo:
    """Troca so o nome que aparece na tela. A pasta em disco fica onde esta.

    Mexer na pasta obrigaria a mover o historico de acoes junto, e um erro no
    meio disso perderia trabalho. O nome na tela nao precisa do mesmo risco.
    """
    novo = (novo_nome or "").strip()
    if novo:
        resumo.nome = novo
        gravar_resumo(resumo)
    return resumo
