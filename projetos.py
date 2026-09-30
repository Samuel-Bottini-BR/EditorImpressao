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
import os
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

    O acoes.jsonl e o posicao.json nao sao descartados pelo recomeco (as
    acoes novas vao para o fim do mesmo arquivo e a posicao e regravada), mas
    vao junto para a copia ficar inteira: e com os tres que se remonta o
    trabalho de antes.

    Nunca sobrescreve copia anterior: se ja ha copia naquele minuto, a nova
    ganha "-2", "-3"... e cada arquivo e criado em modo exclusivo ("x"), que
    falha em vez de escrever por cima. Devolve o caminho da copia do
    projeto.json, ou None se nao havia projeto salvo (ou nao deu para
    copiar). Nunca levanta: nao poder copiar nao pode derrubar a abertura do
    livro - mas ai quem chama deve saber que nao ha copia (None).
    """
    from historico_acoes import ARQUIVO_ACOES, ARQUIVO_POSICAO

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
    caminho = Path(resumo.pasta) / ARQUIVO_ESTADO
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        if not isinstance(dados, dict):
            return False
        dados.update(campos)
        temporario = caminho.with_name(ARQUIVO_ESTADO + ".novo")
        temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=1),
                              encoding="utf-8")
        temporario.replace(caminho)
        return True
    except (OSError, ValueError, TypeError):
        return False


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
      3. outro numero de paginas (mudou "Dividir folhas ao meio").

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
                f"agora o livro tem {agora}. Isso acontece quando se muda a opção "
                "“Dividir folhas ao meio”")
    return ""


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
