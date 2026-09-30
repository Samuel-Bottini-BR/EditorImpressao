"""Projetos anteriores: a lista da tela de inicio, e a pasta de cada projeto."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from modelos import Projeto, nome_de_arquivo_seguro

# Nomes de arquivo ficam SEM acento de proposito: sao caminhos em disco, nao
# texto de interface. Acentuar aqui abandonaria o historico ja gravado.
ARQUIVO_HISTORICO = "historico.json"
MAXIMO_NO_HISTORICO = 20

# CAMINHO EM DISCO, nao texto de tela. Mexer nesta lista muda onde os PDFs do
# usuário vao parar. O primeiro e o nome usado ao criar; os seguintes existem
# so para reconhecer a pasta de uma versão anterior e continuar usando ela.
NOMES_DA_PASTA_DE_SAIDA = ("Editor de Impressão", "Editor de Impressao")


def pasta_de_dados() -> Path:
    """Onde o programa guarda as coisas dele, sem pedir nada ao usuario."""
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if base:
        raiz = Path(base) / "EditorImpressao"
    else:
        raiz = Path.home() / ".editor_impressao"
    raiz.mkdir(parents=True, exist_ok=True)
    return raiz


def pasta_de_projetos() -> Path:
    """A pasta-mae onde cada projeto tem a sua propria subpasta."""
    pasta = pasta_de_dados() / "projetos"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def pasta_do_projeto(nome: str) -> Path:
    """Uma pasta de projeto escolhida pelo NOME (e criada, com thumbs/).

    NAO usar para gravar o trabalho de um projeto: dois livros de mesmo nome
    caem na mesma pasta (bug grave de 29/09/2026, ver o comentario onde
    ficava salvar_projeto). A pasta de um projeto e a resumo.pasta
    (projetos.criar). Ficou so porque algum script de fora pode usar.
    """
    pasta = pasta_de_projetos() / nome_de_arquivo_seguro(nome)
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "thumbs").mkdir(exist_ok=True)
    return pasta


def pasta_de_saida_padrao() -> Path:
    """Documentos / Editor de Impressão - onde os PDFs prontos vao parar.

    Se JA existir uma pasta de uma versão anterior (o nome era sem acento),
    continuamos usando ela. Criar a pasta nova ao lado faria os PDFs que o
    usuário ja tinha gerado sumirem da vista dele - e o trabalho estaria ali,
    a um palmo, na pasta de nome parecido.
    """
    documentos = Path.home() / "Documents"
    if not documentos.exists():
        documentos = Path.home()

    for nome in NOMES_DA_PASTA_DE_SAIDA:
        candidata = documentos / nome
        if candidata.is_dir():
            return candidata

    pasta = documentos / NOMES_DA_PASTA_DE_SAIDA[0]
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


@dataclass
class Entrada:
    """Uma linha da lista de projetos recentes."""

    nome: str
    caminho_entrada: str
    caminho_saida: str
    data: str
    num_paginas: int
    filtro: str
    funcoes: list[str] = field(default_factory=list)
    miniatura: str = ""

    @property
    def data_amigavel(self) -> str:
        try:
            return datetime.fromisoformat(self.data).strftime("%d/%m/%Y")
        except ValueError:
            return self.data

    @property
    def existe_saida(self) -> bool:
        return bool(self.caminho_saida) and Path(self.caminho_saida).exists()

    @property
    def existe_entrada(self) -> bool:
        return bool(self.caminho_entrada) and Path(self.caminho_entrada).exists()


def _caminho_historico() -> Path:
    """Onde o historico.json mora."""
    return pasta_de_dados() / ARQUIVO_HISTORICO


def carregar() -> list[Entrada]:
    """Le a lista de projetos recentes. Historico corrompido ou ausente vira
    lista vazia - nunca impede o programa de abrir."""
    caminho = _caminho_historico()
    if not caminho.exists():
        return []
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        return [Entrada(**e) for e in dados.get("projetos", [])]
    except (OSError, ValueError, TypeError):
        # historico corrompido nao pode impedir o programa de abrir
        return []


def salvar(entradas: list[Entrada]) -> None:
    """Grava a lista, cortada em MAXIMO_NO_HISTORICO itens."""
    try:
        _caminho_historico().write_text(
            json.dumps(
                {"projetos": [asdict(e) for e in entradas[:MAXIMO_NO_HISTORICO]]},
                ensure_ascii=False, indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        pass


def registrar(projeto: Projeto, num_paginas: int, miniatura: str = "") -> None:
    """Anota o trabalho concluido. Chamado quando a tela final aparece."""
    funcoes = []
    if projeto.dividir_folhas:
        funcoes.append("dividir")
    if projeto.limpar:
        funcoes.append("limpar")
    if projeto.endireitar:
        funcoes.append("endireitar")
    if projeto.cortar_bordas:
        funcoes.append("cortar")
    if projeto.montar_cadernos:
        funcoes.append("cadernos")

    nova = Entrada(
        nome=projeto.nome or Path(projeto.caminho_entrada).stem,
        caminho_entrada=projeto.caminho_entrada,
        caminho_saida=projeto.caminho_saida,
        data=datetime.now().isoformat(timespec="seconds"),
        num_paginas=num_paginas,
        filtro=projeto.filtro_padrao,
        funcoes=funcoes,
        miniatura=miniatura,
    )

    # Uma linha por PDF de saida: a mais nova substitui a antiga. Compara o
    # ARQUIVO, nao o texto (o mesmo PDF escrito com `\` e com `/` repetia a
    # linha; mesma familia do bug grave de 29/09, ver projetos.mesmo_arquivo).
    # Importado aqui dentro porque projetos importa este modulo.
    from projetos import mesmo_arquivo

    entradas = [e for e in carregar()
                if not mesmo_arquivo(e.caminho_saida, nova.caminho_saida)]
    salvar([nova] + entradas)


# salvar_projeto(projeto) e carregar_projeto(nome) moravam aqui ate
# 29/09/2026 e foram TIRADOS: escolhiam a pasta pelo NOME do livro
# (pasta_do_projeto), e nao pela pasta do projeto aberto. Com dois PDFs
# diferentes de mesmo nome, fechar o programa (ou processar) com o segundo
# aberto gravava o estado dele por cima do trabalho do primeiro, sem copia e
# sem aviso (bug grave achado pelo verificador, Lista de bugs de 29/09). E,
# como o nome era limpo de outro jeito que o de projetos._pasta_livre, nasciam
# pastas-sombra so com projeto.json. O trabalho de um projeto e gravado so
# por projetos.salvar_estado(resumo, projeto), na pasta dele (resumo.pasta).
# Nao recriar.


def abrir_pasta(caminho: str | Path) -> None:
    """Abre a pasta do arquivo no explorador do sistema."""
    alvo = Path(caminho)
    pasta = alvo.parent if alvo.is_file() else alvo
    try:
        if sys.platform == "win32":
            if alvo.is_file():
                subprocess.run(["explorer", "/select,", str(alvo)], check=False)
            else:
                os.startfile(str(pasta))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(pasta)], check=False)
        else:
            subprocess.run(["xdg-open", str(pasta)], check=False)
    except OSError:
        pass


def imprimir(caminho: str | Path) -> bool:
    """Manda o PDF para a impressora padrão. Devolve se conseguiu tentar."""
    try:
        if sys.platform == "win32":
            os.startfile(str(caminho), "print")  # type: ignore[attr-defined]
            return True
        subprocess.run(["lp", str(caminho)], check=False)
        return True
    except OSError:
        return False
