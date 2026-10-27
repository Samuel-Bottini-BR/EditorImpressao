"""As janelas de abrir PDF, salvar PDF e escolher pasta, em português.

POR QUE EXISTE
    Teste do Kaique (agente leigo, 26/10/2026): a janela de escolher arquivo
    estava "toda em inglês: 'Look in:', 'File name:', 'Files of type:', 'Open',
    'Cancel', 'My Computer'"; "digitar o caminho completo [...] não abriu o
    livro [...] sem nenhum aviso"; e não havia atalho para a Área de Trabalho
    nem para Downloads. Decisão D-301 (18/07/2026): "escolher onde salvar o PDF
    [...] lembrar a última pasta usada [...] avisar em português".

    Achado ao investigar: a janela em inglês é a do PRÓPRIO Qt, que aparece
    quando a janela do Windows não pode ser usada (o piloto do teste liga
    `AA_DontUseNativeDialogs`; fora do Windows também). O programa não carrega
    a tradução do Qt (ver ui/perguntas.py), então ela sai em inglês.

O QUE FAZ
    - No Windows de verdade: usa a janela do próprio Windows (já em português,
      com Área de Trabalho, Documentos e Downloads do lado esquerdo), abrindo
      na última pasta de onde se abriu um livro. O Windows mesmo avisa, em
      português, quando o nome digitado não existe; e, na volta, o caminho é
      conferido de novo aqui.
    - Quando a janela do Windows não pode ser usada: a janela do Qt, com todos
      os textos em português (a tradução do Qt é carregada, e os rótulos são
      escritos aqui), atalhos do lado esquerdo (Área de Trabalho, Documentos,
      Downloads, Livros prontos e a Última pasta aberta) e um aviso claro em
      português quando o caminho digitado não existe.
    - Guarda a última pasta de onde se abriu um livro
      (configuracoes "ultima_pasta_de_entrada").

QUEM USA
    ui/widgets/area_arrastar.py (abrir o livro), ui/widgets/destino.py (pasta
    de saída), ui/dialogo_impressao.py (gravar o arquivo para imprimir). Faltam
    (a gerente troca na junção; ver relatorios/obra-etapa9a/ONDE-PAREI.md):
    ui/janela_principal.py `_escolher_pasta_de_saida` e ui/tela_inicio.py
    `procurar_o_livro_a_mao`.

TESTES
    Os testes e o teste_botoes.py trocam as funções prontas do Qt
    (QFileDialog.getOpenFileName...) por respostas fixas. Quando elas estão
    trocadas, este módulo usa a troca (ver `_trocada_por_teste`), para nenhum
    teste ficar esperando um clique.

SEGURO MUDAR: os textos, a lista de atalhos.
ARRISCADO: tirar a conferência do caminho na volta (um caminho que não existe
    seguiria adiante e o erro apareceria longe, sem explicação).
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QLibraryInfo, QStandardPaths, Qt, QTranslator, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QDialog, QFileDialog, QLineEdit, QListView, QWidget

FILTRO_PDF = "Arquivos PDF (*.pdf)"

ABRIR_PDF = "abrir"
SALVAR_PDF = "salvar"
PASTA = "pasta"

_TRADUCAO: list[QTranslator] = []

# Onde o Qt guarda o endereço de cada atalho do lado esquerdo (QUrlModel::UrlRole).
_PAPEL_DO_ENDERECO = Qt.ItemDataRole.UserRole + 1


# --------------------------------------------------------------- utilidades

def janela_do_windows_disponivel() -> bool:
    """O programa pode usar a janela de arquivo do próprio Windows?"""
    return (sys.platform == "win32"
            and QGuiApplication.platformName() == "windows"
            and not QCoreApplication.testAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs))


def _trocada_por_teste(nome: str) -> bool:
    """A função pronta do Qt foi trocada por uma resposta fixa (testes)?"""
    return not inspect.isbuiltin(getattr(QFileDialog, nome))


def traduzir_o_qt(app: QCoreApplication | None = None) -> bool:
    """Carrega a tradução em português do Brasil dos textos do próprio Qt
    (uma vez só). Devolve se conseguiu. Pode ser chamada em main.py para o
    programa todo; aqui é chamada antes de abrir a janela de arquivo do Qt."""
    if _TRADUCAO:
        return True
    app = app or QCoreApplication.instance()
    if app is None:
        return False
    tradutor = QTranslator(app)
    pasta = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if not tradutor.load("qtbase_pt_BR", pasta):
        return False
    app.installTranslator(tradutor)
    _TRADUCAO.append(tradutor)
    return True


def _pasta_padrao(local: QStandardPaths.StandardLocation) -> Path | None:
    texto = QStandardPaths.writableLocation(local)
    return Path(texto) if texto else None


def pasta_dos_livros() -> Path | None:
    """A última pasta de onde se abriu um livro, se ainda existir."""
    import configuracoes

    texto = configuracoes.ler("ultima_pasta_de_entrada") or ""
    pasta = Path(texto) if texto else None
    return pasta if pasta is not None and pasta.is_dir() else None


def lembrar_pasta_dos_livros(pasta: str | Path) -> None:
    """Guarda a pasta de onde o livro foi aberto (só se existir)."""
    import configuracoes

    caminho = Path(pasta)
    if caminho.is_dir():
        configuracoes.escrever("ultima_pasta_de_entrada", str(caminho))


def pasta_dos_livros_prontos() -> Path | None:
    """Documentos/Editor de Impressão (onde os PDFs prontos vão), se existir.
    Não cria a pasta (historico.pasta_de_saida_padrao cria; aqui é só atalho)."""
    from historico import NOMES_DA_PASTA_DE_SAIDA

    documentos = _pasta_padrao(QStandardPaths.StandardLocation.DocumentsLocation)
    for nome in NOMES_DA_PASTA_DE_SAIDA:
        if documentos is not None and (documentos / nome).is_dir():
            return documentos / nome
    return None


def atalhos() -> list[tuple[str, Path]]:
    """Os atalhos do lado esquerdo da janela do Qt: (nome, pasta), só os que
    existem e sem repetir."""
    candidatos = [
        ("Área de Trabalho", _pasta_padrao(QStandardPaths.StandardLocation.DesktopLocation)),
        ("Documentos", _pasta_padrao(QStandardPaths.StandardLocation.DocumentsLocation)),
        ("Downloads", _pasta_padrao(QStandardPaths.StandardLocation.DownloadLocation)),
        ("Livros prontos", pasta_dos_livros_prontos()),
        ("Última pasta aberta", pasta_dos_livros()),
    ]
    vistos: set[str] = set()
    lista: list[tuple[str, Path]] = []
    for nome, pasta in candidatos:
        if pasta is None or not pasta.is_dir():
            continue
        chave = str(pasta.resolve()).lower()
        if chave in vistos:
            continue
        vistos.add(chave)
        lista.append((nome, pasta))
    return lista


def _avisar(pai, titulo: str, texto: str) -> None:
    from ui import perguntas

    perguntas.avisar(pai, titulo, texto)


def _limpar(texto: str) -> str:
    """Tira espaços e as aspas que o Windows põe ao copiar o caminho."""
    return texto.strip().strip('"').strip()


# --------------------------------------------------------------- a janela do Qt

class JanelaDeArquivo(QFileDialog):
    """A janela de arquivo do Qt, em português, com atalhos e aviso claro.

    Usada só quando a janela do Windows não pode ser usada. `escolhido` guarda
    o caminho aceito (vazio se cancelou)."""

    def __init__(self, pai: QWidget | None, titulo: str, modo: str, inicio: str = "") -> None:
        traduzir_o_qt()
        super().__init__(pai, titulo)
        self.modo = modo
        self.escolhido = ""
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        rotulos = {
            QFileDialog.DialogLabel.LookIn: "Procurar em:",
            QFileDialog.DialogLabel.FileName: "Nome do arquivo:",
            QFileDialog.DialogLabel.FileType: "Tipo:",
            QFileDialog.DialogLabel.Accept: "Abrir",
            QFileDialog.DialogLabel.Reject: "Cancelar",
        }
        if modo == SALVAR_PDF:
            self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            self.setFileMode(QFileDialog.FileMode.AnyFile)
            self.setDefaultSuffix("pdf")
            self.setNameFilter(FILTRO_PDF)
            rotulos[QFileDialog.DialogLabel.Accept] = "Salvar"
        elif modo == PASTA:
            self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            self.setFileMode(QFileDialog.FileMode.Directory)
            self.setOption(QFileDialog.Option.ShowDirsOnly, True)
            rotulos[QFileDialog.DialogLabel.FileName] = "Pasta:"
            rotulos[QFileDialog.DialogLabel.Accept] = "Escolher esta pasta"
        else:
            self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            self.setFileMode(QFileDialog.FileMode.ExistingFile)
            self.setNameFilter(FILTRO_PDF)
        for qual, texto in rotulos.items():
            self.setLabelText(qual, texto)
        self._nomes_dos_atalhos = {QUrl.fromLocalFile(str(p)).toString(): n for n, p in atalhos()}
        self.setSidebarUrls([QUrl(u) for u in self._nomes_dos_atalhos])
        lado = self.findChild(QListView, "sidebar")
        self._modelo_dos_atalhos = lado.model() if lado is not None else None
        if self._modelo_dos_atalhos is not None:
            # O Qt mostra o nome da pasta no disco ("Desktop", "Documents");
            # e o reescreve a cada atualização. Renomeia de novo quando ele
            # reescrever, com os nomes que o Windows mostra em português.
            self._modelo_dos_atalhos.dataChanged.connect(self._renomear_atalhos)
            self._renomear_atalhos()
        self.resize(860, 520)

        inicio_p = Path(inicio) if inicio else None
        if inicio_p is not None and inicio_p.is_dir():
            self.setDirectory(str(inicio_p))
        elif inicio_p is not None and inicio_p.parent.is_dir():
            self.setDirectory(str(inicio_p.parent))
            if modo == SALVAR_PDF:
                self.selectFile(inicio_p.name)

    def _renomear_atalhos(self, *_args) -> None:
        """Põe nos atalhos os nomes em português ("Área de Trabalho"...)."""
        modelo = self._modelo_dos_atalhos
        for linha in range(modelo.rowCount()):
            indice = modelo.index(linha, 0)
            url = indice.data(_PAPEL_DO_ENDERECO)
            nome = self._nomes_dos_atalhos.get(url.toString() if isinstance(url, QUrl) else str(url))
            if nome and indice.data() != nome:
                modelo.setData(indice, nome, Qt.ItemDataRole.DisplayRole)

    def nomes_dos_atalhos(self) -> list[str]:
        """Os nomes que aparecem do lado esquerdo (para os testes)."""
        modelo = self._modelo_dos_atalhos
        if modelo is None:
            return []
        return [modelo.index(i, 0).data() for i in range(modelo.rowCount())]

    # --- o que foi digitado

    def campo_do_nome(self) -> QLineEdit | None:
        """O campo "Nome do arquivo" de baixo."""
        return self.findChild(QLineEdit, "fileNameEdit") or self.findChild(QLineEdit)

    def _digitado(self) -> str:
        campo = self.campo_do_nome()
        return _limpar(campo.text()) if campo is not None else ""

    def _caminho_de(self, texto: str) -> Path:
        caminho = Path(texto).expanduser()
        if not caminho.is_absolute():
            caminho = Path(self.directory().absolutePath()) / caminho
        return caminho

    def _entrar_na_pasta(self, pasta: Path) -> None:
        self.setDirectory(str(pasta))
        campo = self.campo_do_nome()
        if campo is not None:
            campo.clear()

    def accept(self) -> None:  # noqa: D401 - nome do Qt
        """Confere o que foi digitado antes de aceitar. Pasta: entra nela.
        Caminho que não existe: aviso em português, a janela fica aberta."""
        texto = self._digitado()
        if not texto:
            if self.modo == PASTA:
                self.escolhido = self.directory().absolutePath()
                QDialog.accept(self)
                return
            super().accept()        # o Qt entra na pasta marcada na lista
            return
        caminho = self._caminho_de(texto)

        if self.modo == PASTA:
            if caminho.is_dir():
                self.escolhido = str(caminho)
                QDialog.accept(self)
                return
            _avisar(self, "Não achei a pasta",
                    f"Não achei esta pasta:\n{caminho}\n\nConfira se o nome está certo, ou "
                    "escolha a pasta na lista.")
            return

        if caminho.is_dir():
            self._entrar_na_pasta(caminho)
            return

        if self.modo == SALVAR_PDF:
            if caminho.suffix.lower() != ".pdf":
                caminho = caminho.with_name(caminho.name + ".pdf")
            if not caminho.parent.is_dir():
                _avisar(self, "Não achei a pasta",
                        f"A pasta onde o arquivo seria salvo não existe:\n{caminho.parent}\n\n"
                        "Confira o caminho, ou escolha a pasta na lista.")
                return
            if caminho.exists():
                from ui import perguntas

                if not perguntas.perguntar(
                        self, "Substituir o arquivo?",
                        f"Já existe um arquivo com esse nome:\n{caminho.name}\n\nQuer substituir?",
                        sim="Substituir", nao="Não, escolher outro nome"):
                    return
            self.escolhido = str(caminho)
            QDialog.accept(self)
            return

        # abrir um PDF
        if not caminho.exists() and caminho.suffix.lower() != ".pdf":
            com_pdf = caminho.with_name(caminho.name + ".pdf")
            if com_pdf.is_file():
                caminho = com_pdf
        if not caminho.is_file():
            _avisar(self, "Não achei o arquivo",
                    f"Não achei este arquivo:\n{caminho}\n\nConfira se o nome e a pasta estão "
                    "certos, ou procure o livro na lista.")
            return
        if caminho.suffix.lower() != ".pdf":
            _avisar(self, "Este arquivo não é um PDF",
                    f"O programa só abre livros em PDF.\n{caminho.name} não é um PDF.")
            return
        self.escolhido = str(caminho)
        QDialog.accept(self)


def _pela_janela_do_qt(pai, titulo: str, modo: str, inicio: str) -> str:
    janela = JanelaDeArquivo(pai, titulo, modo, inicio)
    if janela.exec() != QDialog.DialogCode.Accepted:
        return ""
    return janela.escolhido


# --------------------------------------------------------------- as três perguntas

def _conferir_na_volta(pai, caminho: str, modo: str) -> str:
    """A janela do Windows (ou a troca dos testes) devolveu `caminho`:
    confere de novo e avisa em português se não existir."""
    if not caminho:
        return ""
    alvo = Path(caminho)
    if modo == ABRIR_PDF and not alvo.is_file():
        _avisar(pai, "Não achei o arquivo",
                f"Não achei este arquivo:\n{alvo}\n\nConfira se o nome e a pasta estão certos.")
        return ""
    if modo == PASTA and not alvo.is_dir():
        _avisar(pai, "Não achei a pasta", f"Não achei esta pasta:\n{alvo}")
        return ""
    if modo == SALVAR_PDF and not alvo.parent.is_dir():
        _avisar(pai, "Não achei a pasta",
                f"A pasta onde o arquivo seria salvo não existe:\n{alvo.parent}")
        return ""
    return caminho


def escolher_pdf_para_abrir(pai: QWidget | None, titulo: str = "Escolha o PDF do livro",
                            pasta: str = "") -> str:
    """Pergunta qual PDF abrir. Devolve o caminho, ou "" se cancelou."""
    inicio = pasta or str(pasta_dos_livros() or Path.home())
    if janela_do_windows_disponivel() or _trocada_por_teste("getOpenFileName"):
        caminho, _filtro = QFileDialog.getOpenFileName(pai, titulo, inicio, FILTRO_PDF)
        caminho = _conferir_na_volta(pai, caminho, ABRIR_PDF)
    else:
        caminho = _pela_janela_do_qt(pai, titulo, ABRIR_PDF, inicio)
    if caminho:
        lembrar_pasta_dos_livros(Path(caminho).parent)
    return caminho


def escolher_onde_salvar_pdf(pai: QWidget | None, titulo: str, sugerido: str) -> str:
    """Pergunta onde salvar um PDF (`sugerido` = caminho completo proposto).
    Devolve o caminho, ou "" se cancelou."""
    if janela_do_windows_disponivel() or _trocada_por_teste("getSaveFileName"):
        caminho, _filtro = QFileDialog.getSaveFileName(pai, titulo, sugerido, FILTRO_PDF)
        return _conferir_na_volta(pai, caminho, SALVAR_PDF)
    return _pela_janela_do_qt(pai, titulo, SALVAR_PDF, sugerido)


def escolher_pasta(pai: QWidget | None, titulo: str, pasta: str = "") -> str:
    """Pergunta uma pasta. Devolve o caminho, ou "" se cancelou."""
    if janela_do_windows_disponivel() or _trocada_por_teste("getExistingDirectory"):
        caminho = QFileDialog.getExistingDirectory(pai, titulo, pasta,
                                                   QFileDialog.Option.ShowDirsOnly)
        return _conferir_na_volta(pai, caminho, PASTA)
    return _pela_janela_do_qt(pai, titulo, PASTA, pasta)


__all__ = [
    "JanelaDeArquivo", "atalhos", "escolher_onde_salvar_pdf", "escolher_pasta",
    "escolher_pdf_para_abrir", "janela_do_windows_disponivel", "lembrar_pasta_dos_livros",
    "pasta_dos_livros", "traduzir_o_qt",
]
