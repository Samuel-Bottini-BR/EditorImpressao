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

ARQUIVO_HISTORICO = "historico.json"
MAXIMO_NO_HISTORICO = 20


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
    pasta = pasta_de_dados() / "projetos"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def pasta_do_projeto(nome: str) -> Path:
    pasta = pasta_de_projetos() / nome_de_arquivo_seguro(nome)
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "thumbs").mkdir(exist_ok=True)
    return pasta


def pasta_de_saida_padrao() -> Path:
    """Documentos / Editor de Impressão - onde os PDFs prontos vao parar."""
    documentos = Path.home() / "Documents"
    if not documentos.exists():
        documentos = Path.home()
    pasta = documentos / "Editor de Impressão"
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
    return pasta_de_dados() / ARQUIVO_HISTORICO


def carregar() -> list[Entrada]:
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

    entradas = [e for e in carregar() if e.caminho_saida != nova.caminho_saida]
    salvar([nova] + entradas)


def salvar_projeto(projeto: Projeto) -> None:
    """Grava projeto.json na pasta do projeto (o estado atual)."""
    pasta = pasta_do_projeto(projeto.nome or Path(projeto.caminho_entrada).stem)
    try:
        (pasta / "projeto.json").write_text(
            json.dumps(projeto.para_dicionario(), ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
    except OSError:
        pass


def carregar_projeto(nome: str) -> Projeto | None:
    caminho = pasta_do_projeto(nome) / "projeto.json"
    if not caminho.exists():
        return None
    try:
        return Projeto.de_dicionario(json.loads(caminho.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):
        return None


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
