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

import json
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

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


def gravar_resumo(resumo: Resumo) -> None:
    """Grava o resumo. Nunca levanta: perder o resumo nao pode travar nada."""
    try:
        pasta = Path(resumo.pasta)
        pasta.mkdir(parents=True, exist_ok=True)
        resumo.mexido_em = datetime.now().isoformat(timespec="seconds")
        if not resumo.criado_em:
            resumo.criado_em = resumo.mexido_em
        _caminho_do_resumo(pasta).write_text(
            json.dumps(asdict(resumo), ensure_ascii=False, indent=1),
            encoding="utf-8")
    except OSError:
        pass


def ler_resumo(pasta: str | Path) -> Resumo | None:
    """Le o resumo.json de uma pasta de projeto, ou None se faltar/estiver corrompido."""
    caminho = _caminho_do_resumo(Path(pasta))
    if not caminho.is_file():
        return None
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    conhecidos = {campo for campo in Resumo().__dict__}
    limpo = {c: v for c, v in dados.items() if c in conhecidos}
    resumo = Resumo(**limpo)
    resumo.pasta = str(pasta)          # a pasta manda, e nao o que estava escrito
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


def atualizar(resumo: Resumo, projeto, pagina_atual: int | None = None) -> Resumo:
    """Anota o andamento. Chamado a cada acao - e por isso tem de ser barato."""
    resumo.caminho_saida = projeto.caminho_saida or resumo.caminho_saida
    resumo.total_paginas = len(projeto.paginas) or resumo.total_paginas
    resumo.conferidas = sum(1 for p in projeto.paginas if p.revisada)
    if pagina_atual is not None:
        resumo.pagina_atual = int(pagina_atual)
    gravar_resumo(resumo)
    return resumo


# --- o estado da conferencia -----------------------------------------------

ARQUIVO_ESTADO = "projeto.json"


def salvar_estado(resumo: Resumo, projeto) -> None:
    """Grava o trabalho da pagina: filtro, corte, angulo, marcacao, tudo.

    Nunca levanta. Falhar ao gravar nao pode derrubar a tela em que a pessoa
    esta trabalhando - o pior caso aceitavel e perder a ultima acao, e nao a
    sessao inteira.
    """
    try:
        pasta = Path(resumo.pasta)
        pasta.mkdir(parents=True, exist_ok=True)
        temporario = pasta / (ARQUIVO_ESTADO + ".novo")
        # Grava num arquivo ao lado e so entao troca. Escrever por cima do bom
        # deixaria o projeto pela metade se a energia caisse no meio - e o
        # arquivo pela metade e justamente o que nao pode acontecer aqui.
        temporario.write_text(
            json.dumps(projeto.para_dicionario(), ensure_ascii=False, indent=1),
            encoding="utf-8")
        temporario.replace(pasta / ARQUIVO_ESTADO)
    except (OSError, ValueError, TypeError):
        pass


def carregar_estado(resumo: Resumo):
    """Devolve o Projeto gravado, ou None se nao houver ou nao der para ler."""
    from modelos import Projeto

    caminho = Path(resumo.pasta) / ARQUIVO_ESTADO
    if not caminho.is_file():
        return None
    try:
        return Projeto.de_dicionario(json.loads(caminho.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):
        return None


def combina_com(salvo, recem_analisado) -> bool:
    """O trabalho salvo pode ser aplicado neste livro recem-aberto?

    So se for o MESMO livro e a mesma divisao. Se a pessoa trocou "dividir
    folhas ao meio" entre uma sessao e outra, a pagina 40 salva nao e a pagina
    40 de agora, e devolver o corte de uma na outra estragaria o trabalho.
    """
    if salvo is None or recem_analisado is None:
        return False
    return (len(salvo.paginas) == len(recem_analisado.paginas)
            and len(salvo.folhas) == len(recem_analisado.folhas)
            and salvo.caminho_entrada == recem_analisado.caminho_entrada)


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


def remover_da_lista(resumo: Resumo) -> None:
    """Tira o projeto da tela inicial, apagando a pasta DELE.

    O PDF de origem nunca e tocado: ele nunca esteve aqui dentro.
    """
    import shutil

    pasta = Path(resumo.pasta)
    raiz = pasta_dos_projetos()
    try:
        # trava de seguranca: so apaga dentro da pasta de projetos
        if pasta.is_dir() and raiz in pasta.parents:
            shutil.rmtree(pasta, ignore_errors=True)
    except OSError:
        pass


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
