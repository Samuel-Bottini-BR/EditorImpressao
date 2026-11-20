"""O servidor das versões de prova (plano da parte do Windows, versão 3, peça 10b; D-773).

O QUE É
    Uma janela pequena e visível, no PC do Samuel, que faz o papel do GitHub nas provas: serve pela rede (de verdade,
    em http://127.0.0.1:<porta>/) as versões de verdade que o publicar pôs numa pasta (`publicar_versao_kaique.py
    --pasta <pasta>`), e mostra uma linha por pedido (a hora, o que foi pedido, se foi entregue inteiro ou cortado).
    **Fechar a janela é a internet caindo:** ela para de atender e corta no meio o que estiver sendo baixado.

    NÃO é parte do programa do Kaique (fica na raiz do projeto; o empacotador não a leva). Não fala com o Windows (só
    abre uma porta na própria máquina, 127.0.0.1, que não pede licença nem passa pelo firewall).

O QUE ELA SERVE (lido no código do Velopack 1.2.161, `src/lib-rust/src/sources/http.rs`: o programa, com um endereço
http://, pede `<endereço>/releases.win.json?localVersion=...&id=...&stagingId=...` e depois `<endereço>/<FileName>`)
    - `/releases.win.json`: o índice de TODAS as publicações liberadas da pasta (cada uma traz o seu, gravado pelo vpk
      só com a versão dela), juntos num só, a mais nova primeiro (o GitHub faz o mesmo papel com os "releases");
    - `/<nome de um arquivo>`: o arquivo com esse nome em qualquer publicação liberada (o pacote, a assinatura, o
      arquivo do motor, o .msi; o publicar põe a versão em todos os nomes). Nome repetido em duas publicações não é
      entregue (404): não se sabe qual é.
    O desenho da pasta é o do `publicar_versao_kaique.DestinoPasta` (uma subpasta por etiqueta, `v1.2.0\\`,
    `motor-kraken-1\\`; o rascunho, `.rascunho-v1.2.0\\`, NÃO é servido: como no GitHub, rascunho não aparece). As regras
    do desenho são lidas de lá (`DestinoPasta.liberadas`), nunca copiadas.
    Recusa (404, com a linha na janela): nome com barra, "..", começo com ponto, ou que não está numa publicação.

COMO ABRIR
    `.venv\\Scripts\\python.exe servidor_das_versoes.py --pasta <pasta das versões> [--porta 8765] [--limite 2000]`
    `--limite` (KB por segundo, opcional): deixa o envio mais lento, para dar tempo de fechar a janela no meio de um
    download na prova (sem ele, na própria máquina, 460 MB passam em segundos). Cada linha vai também para um
    registro em texto (`--registro`, ou `relatorios/servidor-das-versoes/registro-<data>.txt`).
    O programa instalado acha este servidor pela fonte de teste (que só o administrador cria; passo 3 do plano).

Seguro mexer: os textos, o tamanho do pedaço enviado. Arriscado: servir o rascunho (a prova de "nada liberado antes da
assinatura" deixa de valer); servir nome com barra ou ".." (sairia da pasta); escutar fora de 127.0.0.1 (o Windows
perguntaria pelo firewall, e outra máquina poderia baixar).
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import unquote, urlsplit

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

import empacotar  # noqa: E402
import publicar_versao_kaique as pub  # noqa: E402

ENDERECO = "127.0.0.1"
PORTA_DE_FABRICA = 8765
NOME_DO_INDICE = empacotar.NOME_DO_INDICE     # o nome com que o vpk grava o índice (lugar único: empacotar)
PEDACO = 64 * 1024


def _agora() -> str:
    """A hora de agora, para cada linha."""
    return datetime.now().strftime("%H:%M:%S")


def _ordem_da_versao(texto: str) -> tuple:
    """'1.2.10' -> (1, 2, 10) para pôr a mais nova primeiro (o que não for número vai para o fim)."""
    try:
        return tuple(int(p) for p in str(texto).split("."))
    except ValueError:
        return ()


class Versoes:
    """O que a pasta tem para servir: só as publicações liberadas (as subpastas com nome de etiqueta, DestinoPasta
    do publicar); o rascunho e qualquer outra coisa ficam de fora. Lido a cada pedido (o publicar pode liberar uma
    versão com a janela aberta)."""

    def __init__(self, pasta: Path | str):
        """pasta: a mesma do `publicar_versao_kaique.py --pasta`."""
        self.pasta = Path(pasta)

    def publicacoes(self) -> list[Path]:
        """As subpastas liberadas, pela MESMA regra do publicar (`DestinoPasta.liberadas`: nome de etiqueta inteiro,
        pasta de verdade, nunca atalho nem junção; achado 7 de quem tentou quebrar: antes a regra estava aqui também,
        e a junção passava)."""
        return pub.DestinoPasta(self.pasta).liberadas()

    def achar(self, nome: str) -> Path | None:
        """O arquivo com este nome numa publicação liberada, ou None (o motivo, em `procurar`)."""
        return self.procurar(nome)[0]

    def procurar(self, nome: str) -> tuple[Path | None, str]:
        """(o arquivo, "") ou (None, o motivo de não entregar, para a linha da janela): nome com barra, "..", começo
        com ponto ou dois-pontos (para quem pede, como o que não existe: "não existe aqui"); o MESMO nome em mais de uma publicação (não se sabe qual entregar;
        achado 7 da volta 1: o .msi de outra versão saía); ou não existe. Volta 3, achado 8 do relatório 2: a janela
        dizia "não existe aqui" também do nome repetido, que existe duas vezes."""
        if not nome or "/" in nome or "\\" in nome or ".." in nome or nome.startswith(".") or ":" in nome:
            return None, "não existe aqui (404)"
        achados = [publicacao / nome for publicacao in self.publicacoes() if (publicacao / nome).is_file()]
        if len(achados) > 1:
            return None, (f"está em {len(achados)} publicações ({', '.join(a.parent.name for a in achados)}): não "
                          "entrego, não se sabe qual (404)")
        if not achados:
            return None, "não existe aqui (404)"
        return achados[0], ""

    def indice(self) -> bytes:
        """O índice de todas as publicações liberadas, juntos (sem repetir arquivo), a versão mais nova primeiro."""
        itens: dict[str, dict] = {}
        for publicacao in self.publicacoes():
            try:
                lido = json.loads((publicacao / NOME_DO_INDICE).read_text(encoding="utf-8-sig"))
            except (OSError, ValueError):
                continue                                   # a do motor não tem índice; a estragada fica de fora
            for item in lido.get("Assets", []) if isinstance(lido, dict) else []:
                if isinstance(item, dict) and item.get("FileName"):
                    itens.setdefault(str(item["FileName"]), item)
        ordem = sorted(itens.values(), key=lambda i: _ordem_da_versao(i.get("Version", "")), reverse=True)
        return json.dumps({"Assets": ordem}).encode("utf-8")


class _ServidorHttp(ThreadingHTTPServer):
    """O HTTP da biblioteca, com a porta só nossa. O http.server liga de fábrica o "reusar o endereço", e no Windows
    isso deixa um SEGUNDO servidor abrir a mesma porta sem erro (achado no teste, 19/11): os dois atenderiam e a prova
    de "fechar a janela" mentiria. Aqui: sem reusar, e com a porta exclusiva do Windows (SO_EXCLUSIVEADDRUSE), a
    segunda abertura dá erro (a janela diz "porta ocupada")."""

    allow_reuse_address = False
    daemon_threads = True

    def server_bind(self) -> None:
        """Pede a porta exclusiva antes de abrir."""
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


class Servidor:
    """O servidor de verdade (HTTP na própria máquina), sem a janela: a janela e os testes usam este.

    `dizer(texto)` recebe cada linha (de vários fios ao mesmo tempo: quem mostra cuida de passar para o fio da tela).
    `limite_kb_s`: o envio no máximo a tantos KB por segundo (None = sem limite). `fechar()` para de atender e CORTA o
    que estiver sendo enviado (a internet caindo)."""

    def __init__(self, pasta: Path | str, porta: int = PORTA_DE_FABRICA, limite_kb_s: float | None = None,
                 dizer: Callable[[str], None] = print):
        """Prepara (não abre a porta ainda: ver iniciar)."""
        self.versoes = Versoes(pasta)
        self.porta_pedida = porta
        self.limite_kb_s = limite_kb_s
        self.dizer = dizer
        self._http: _ServidorHttp | None = None
        self._fio: threading.Thread | None = None
        self._conexoes: set[socket.socket] = set()
        self._tranca = threading.Lock()
        self.fechado = threading.Event()

    @property
    def endereco(self) -> str:
        """http://127.0.0.1:<porta>/ (a porta de verdade, depois de iniciar)."""
        porta = self._http.server_address[1] if self._http else self.porta_pedida
        return f"http://{ENDERECO}:{porta}/"

    def iniciar(self) -> None:
        """Abre a porta e começa a atender num fio à parte. Levanta OSError se a porta está ocupada."""
        servidor = self

        class Atender(BaseHTTPRequestHandler):
            """Um pedido: o índice, um arquivo, ou 404."""

            def setup(self) -> None:
                """Anota a conexao aberta (para fechar() poder corta-la)."""
                super().setup()
                with servidor._tranca:
                    servidor._conexoes.add(self.connection)

            def finish(self) -> None:
                """Tira a conexao da lista."""
                try:
                    super().finish()
                finally:
                    with servidor._tranca:
                        servidor._conexoes.discard(self.connection)

            def log_message(self, *_args) -> None:
                """Calado: cada pedido vira uma linha nossa (dizer), não o registro do http.server."""

            def do_HEAD(self) -> None:  # noqa: N802 - nome do http.server
                self._responder(corpo=False)

            def do_GET(self) -> None:  # noqa: N802 - nome do http.server
                self._responder(corpo=True)

            def _responder(self, corpo: bool) -> None:
                """O indice, o arquivo pedido, ou 404 (a linha na janela vem antes da resposta de erro)."""
                nome = unquote(urlsplit(self.path).path).lstrip("/")
                de_onde = self.client_address[0]
                if nome == NOME_DO_INDICE:
                    dados = servidor.versoes.indice()
                    self._enviar_dados(nome, dados, corpo, de_onde)
                    return
                caminho, motivo = servidor.versoes.procurar(nome)
                if caminho is None:
                    servidor.dizer(f"{_agora()}  {de_onde}  {nome or '/'}: {motivo}")
                    self.send_error(404, "não existe")
                    return
                self._enviar_arquivo(nome, caminho, corpo, de_onde)

            def _cabecalho(self, tamanho: int, tipo: str) -> None:
                """O 200 com o tamanho anunciado (quem baixa sabe quando chegou incompleto)."""
                self.send_response(200)
                self.send_header("Content-Type", tipo)
                self.send_header("Content-Length", str(tamanho))
                self.end_headers()

            def _enviar_dados(self, nome: str, dados: bytes, corpo: bool, de_onde: str) -> None:
                """Envia um texto pequeno (o indice)."""
                self._cabecalho(len(dados), "application/json")
                if corpo:
                    self.wfile.write(dados)
                servidor.dizer(f"{_agora()}  {de_onde}  {nome}: entregue ({len(dados):,} bytes)".replace(",", "."))

            def _enviar_arquivo(self, nome: str, caminho: Path, corpo: bool, de_onde: str) -> None:
                """Envia o arquivo aos pedacos (com o limite de velocidade, se houver); a janela fechada corta."""
                tamanho = caminho.stat().st_size
                self._cabecalho(tamanho, "application/octet-stream")
                if not corpo:
                    return
                enviado = 0
                inicio = time.perf_counter()
                try:
                    with caminho.open("rb") as arquivo:
                        while pedaco := arquivo.read(PEDACO):
                            if servidor.fechado.is_set():
                                raise ConnectionAbortedError("a janela foi fechada")
                            self.wfile.write(pedaco)
                            enviado += len(pedaco)
                            if servidor.limite_kb_s:
                                espera = enviado / (servidor.limite_kb_s * 1024) - (time.perf_counter() - inicio)
                                if espera > 0:
                                    time.sleep(espera)
                    servidor.dizer(f"{_agora()}  {de_onde}  {nome}: entregue inteiro ({tamanho:,} bytes)"
                                   .replace(",", "."))
                except (ConnectionError, OSError) as erro:
                    servidor.dizer(f"{_agora()}  {de_onde}  {nome}: CORTADO no meio ({enviado:,} de {tamanho:,} "
                                   f"bytes; {erro.__class__.__name__})".replace(",", "."))

        self._http = _ServidorHttp((ENDERECO, self.porta_pedida), Atender)
        self._fio = threading.Thread(target=self._http.serve_forever, kwargs={"poll_interval": 0.2}, daemon=True)
        self._fio.start()
        self.dizer(f"{_agora()}  servindo {self.versoes.pasta} em {self.endereco}")

    def fechar(self) -> None:
        """Para de atender e corta o que estiver sendo enviado (a internet caindo). Pode ser chamada mais de uma vez."""
        if self.fechado.is_set():
            return
        self.fechado.set()
        if self._http is not None:
            self._http.shutdown()
            self._http.server_close()
        with self._tranca:
            abertas = list(self._conexoes)
        for conexao in abertas:
            try:
                conexao.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                conexao.close()
            except OSError:
                pass
        self.dizer(f"{_agora()}  servidor fechado (a internet caiu); {len(abertas)} envio(s) cortado(s)")


# ---------------------------------------------------------------------------------------------------------------------
# A janela
# ---------------------------------------------------------------------------------------------------------------------

def montar_janela(servidor: Servidor, registro: Path | None, erro_ao_abrir: str | None = None):
    """Monta a janela (PySide6): o endereço, a pasta, as versões servidas (lidas de novo a cada 2 s) e uma linha por
    pedido. Fechar a janela fecha o servidor (servidor.fechar). Com erro_ao_abrir (ex.: porta ocupada), mostra o erro
    e não serve nada."""
    from PySide6.QtCore import QObject, QTimer, Signal
    from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget

    class Ponte(QObject):
        """Passa as linhas dos fios do servidor para o fio da tela."""

        linha = Signal(str)

    class Janela(QWidget):
        """A janela pequena do servidor das versões de prova."""

        def __init__(self) -> None:
            """Os textos de cima, a lista das versões e as linhas dos pedidos."""
            super().__init__()
            self.setWindowTitle("Servidor das versões de prova")
            self.resize(820, 520)
            caixa = QVBoxLayout(self)
            if erro_ao_abrir:
                caixa.addWidget(QLabel(f"NÃO ESTÁ SERVINDO: {erro_ao_abrir}"))
            else:
                caixa.addWidget(QLabel(f"Endereço: {servidor.endereco}   (fechar esta janela = a internet caindo)"))
            caixa.addWidget(QLabel(f"Pasta: {servidor.versoes.pasta}"
                                   + (f"   ·   limite: {servidor.limite_kb_s:g} KB/s" if servidor.limite_kb_s else "")))
            self.versoes = QLabel()
            caixa.addWidget(self.versoes)
            self.pedidos = QPlainTextEdit()
            self.pedidos.setReadOnly(True)
            caixa.addWidget(self.pedidos, 1)
            self.ponte = Ponte()
            self.ponte.linha.connect(self.dizer)
            servidor.dizer = self.ponte.linha.emit
            self.relogio = QTimer(self)
            self.relogio.timeout.connect(self.mostrar_versoes)
            self.relogio.start(2000)
            self.mostrar_versoes()
            if not erro_ao_abrir:
                self.dizer(f"{_agora()}  servindo {servidor.versoes.pasta} em {servidor.endereco}")

        def mostrar_versoes(self) -> None:
            """As publicações que estão sendo servidas agora."""
            nomes = [p.name for p in servidor.versoes.publicacoes()]
            self.versoes.setText("Servindo: " + (", ".join(nomes) if nomes else "nada (a pasta não tem publicação)"))

        def dizer(self, texto: str) -> None:
            """Uma linha na janela e no registro."""
            self.pedidos.appendPlainText(texto)
            if registro is not None:
                try:
                    with registro.open("a", encoding="utf-8") as arquivo:
                        arquivo.write(texto + "\n")
                except OSError:
                    pass

        def closeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
            """Fechar a janela fecha o servidor (e corta o que está sendo baixado)."""
            self.relogio.stop()
            servidor.fechar()
            evento.accept()

    return Janela()


def principal(argumentos: list[str]) -> int:
    """Abre o servidor e a janela."""
    leitor = argparse.ArgumentParser(description="Servidor das versões de prova (faz o papel do GitHub)")
    leitor.add_argument("--pasta", required=True, help="a pasta das versões (a do publicar_versao_kaique.py --pasta)")
    leitor.add_argument("--porta", type=int, default=PORTA_DE_FABRICA)
    leitor.add_argument("--limite", type=float, default=None, help="KB por segundo (para fechar no meio de um envio)")
    leitor.add_argument("--registro", help="arquivo onde cada linha fica escrita")
    args = leitor.parse_args(argumentos)
    registro = Path(args.registro) if args.registro else (
        RAIZ / "relatorios" / "servidor-das-versoes" / f"registro-{datetime.now():%Y-%m-%d-%H%M%S}.txt")
    registro.parent.mkdir(parents=True, exist_ok=True)
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv[:1])
    servidor = Servidor(args.pasta, args.porta, args.limite)
    erro = None
    try:
        servidor.iniciar()
    except OSError as falha:
        erro = f"a porta {args.porta} está ocupada ou não abriu ({falha})"
    janela = montar_janela(servidor, registro, erro)
    janela.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(principal(sys.argv[1:]))
