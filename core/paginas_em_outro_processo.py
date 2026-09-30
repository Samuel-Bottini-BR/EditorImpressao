"""Desenha as paginas do PDF num processo a parte, para a janela nunca congelar.

POR QUE EXISTE (30/09/2026, bug grave achado pelo verificador: a janela ficava
~16 s sem responder ao terminar a analise de um livro de 80 paginas)
--------------------------------------------------------------------------
O PyMuPDF (fitz) NAO solta o GIL do Python enquanto desenha uma pagina: medido
em 30/09, numa thread de fundo, get_pixmap de uma pagina do Internet Archive
(imagem JPEG 2000, 3325 x 2568) segura o GIL ~0,5 s, e nesse tempo NENHUMA
outra thread do programa roda - nem a da janela. Com a analise, as miniaturas
e as previas desenhando ao mesmo tempo, a janela chegava a esperar 9 s (o
proprio PyMuPDF manda usar processos para trabalhar em paralelo,
pymupdf/_apply_pages.py). Por isso nao adianta "mandar para uma QThread":
elas ja estavam em QThread. O desenho tem de sair do processo.

O QUE FAZ
---------
`pagina(caminho, indice, dpi)` pede a um processo auxiliar (o "servidor de
paginas") o mesmo que core.pdf_io.pagina_para_array faria aqui, e devolve a
mesma imagem (BGR uint8), ponto por ponto igual: o servidor roda o MESMO codigo
(pdf_io.pagina_para_array, com a delegacao desligada). Enquanto espera a
resposta pelo cano, a thread que pediu solta o GIL: a janela continua viva.

- Dois servidores, cada um atendendo um pedido por vez (as previas, as
  miniaturas e a analise pedem ao mesmo tempo). Aqui dentro, o desenho era
  um por vez (pdf_io._TRANCA); em processos separados os dois desenham em
  paralelo.
- Sobem sozinhos na primeira vez que forem usados (ou antes, com
  iniciar_em_segundo_plano(), chamado quando a janela abre), e morrem junto
  com o programa (atexit; e se o programa cair, o cano quebra e eles saem).
- Se um servidor cair (o MuPDF ja derrubou o processo inteiro em PDF
  estranho - ver pdf_io._TRANCA), ele e trocado por outro e o pedido e feito
  de novo, uma vez; se nao der, a pagina e desenhada aqui mesmo, como antes
  (e fica anotado no erros.log). O programa nunca fica sem pagina por causa
  disto.
- EDITOR_PAGINAS_AQUI=1 no ambiente desliga tudo (desenha aqui dentro, como
  antes de 30/09): para depurar, ou se algo der errado no computador do
  Kaique.

Programa empacotado (PyInstaller): o servidor e o proprio EditorImpressao.exe
com o argumento --servidor-de-paginas (main.py atende esse argumento antes de
abrir qualquer janela). Em desenvolvimento: python -m core.paginas_em_outro_processo.

Seguro mudar: QUANTOS_SERVIDORES, TEMPO_PARA_SUBIR_S. Arriscado: fazer o
servidor desenhar de outro jeito que nao pdf_io.pagina_para_array (a previa
deixaria de ser igual ao PDF final); tirar o CREATE_NO_WINDOW (abriria uma
janela preta de console no Windows); tirar o recomeco quando o servidor cai.
"""

from __future__ import annotations

import atexit
import os
import queue
import subprocess
import sys
import threading
import traceback
from pathlib import Path

import numpy as np

# Desliga a delegacao (desenha aqui dentro, como antes). Tambem e o que o
# proprio servidor usa, para nao pedir a si mesmo.
VARIAVEL_DESLIGA = "EDITOR_PAGINAS_AQUI"

QUANTOS_SERVIDORES = 2
# O servidor fecha o livro depois deste tempo sem pedido (o arquivo fica
# livre para mover, renomear ou apagar). Ver servir().
SEGUNDOS_PARADO = 0.5
TEMPO_PARA_SUBIR_S = 60.0         # a primeira vez depois de instalar pode demorar
ARGUMENTO_DO_SERVIDOR = "--servidor-de-paginas"


def ligado() -> bool:
    """A delegacao esta ligada? (Desligada no proprio servidor e com
    EDITOR_PAGINAS_AQUI=1.)"""
    return os.environ.get(VARIAVEL_DESLIGA) != "1"


# ---------------------------------------------------------------------------
# lado do programa
# ---------------------------------------------------------------------------


class _Servidor:
    """Um processo auxiliar e o cano ate ele. Um pedido por vez (quem usa pega
    o servidor da fila _livres, e so devolve depois da resposta)."""

    def __init__(self) -> None:
        from multiprocessing.connection import Listener

        chave = os.urandom(16)
        self._escuta = Listener(family="AF_PIPE", authkey=chave)
        comando = _comando_do_servidor(self._escuta.address, chave.hex())
        ambiente = dict(os.environ)
        ambiente[VARIAVEL_DESLIGA] = "1"
        ambiente.pop("QT_QPA_PLATFORM", None)
        self.processo = subprocess.Popen(
            comando, env=ambiente, cwd=str(_raiz()),
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.cano = None
        self._bloco = None
        erro: list[BaseException] = []

        def aceitar() -> None:
            try:
                self.cano = self._escuta.accept()
            except BaseException as exc:  # noqa: BLE001
                erro.append(exc)

        espera = threading.Thread(target=aceitar, daemon=True)
        espera.start()
        espera.join(TEMPO_PARA_SUBIR_S)
        if self.cano is None:
            self.fechar()
            raise RuntimeError(f"o servidor de paginas nao subiu: {erro or 'tempo esgotado'}")

    def pedir(self, caminho: str, indice: int, dpi: int) -> np.ndarray:
        """Manda o pedido e espera a imagem (esperando, o GIL fica solto)."""
        self.cano.send(("pagina", caminho, indice, dpi))
        resposta = self.cano.recv()
        if resposta[0] == "ok":
            _, altura, largura, canais, nome_do_bloco = resposta
            # A imagem vem por memoria compartilhada (o bloco do servidor):
            # passar 25 MB pelo cano custava ~25 ms por pagina a 300 DPI, e o
            # PDF final le cada pagina 2 ou 3 vezes. Copia para um array
            # proprio (como o de pagina_para_array, que se pode alterar): o
            # servidor reaproveita o bloco na proxima pagina.
            bloco = self._bloco_do_servidor(nome_do_bloco)
            vista = np.ndarray((altura, largura, canais), dtype=np.uint8, buffer=bloco.buf)
            imagem = vista.copy()
            del vista
            return imagem
        _, classe, mensagem = resposta
        if classe == "ErroPDF":
            from core.pdf_io import ErroPDF

            raise ErroPDF(mensagem)
        raise _ErroDoServidor(f"{classe}: {mensagem}")

    def _bloco_do_servidor(self, nome: str):
        """O bloco de memoria compartilhada que o servidor usa agora (ele troca
        por um maior quando a pagina nao cabe). Fica aberto ate mudar."""
        from multiprocessing import shared_memory

        if self._bloco is None or self._bloco.name != nome:
            self._fechar_bloco()
            self._bloco = shared_memory.SharedMemory(name=nome)
        return self._bloco

    def _fechar_bloco(self) -> None:
        if self._bloco is not None:
            try:
                self._bloco.close()
            except (OSError, BufferError):
                pass
            self._bloco = None

    def vivo(self) -> bool:
        return self.processo.poll() is None

    def fechar(self) -> None:
        """Pede para sair; se nao sair, fecha a forca. Nunca levanta."""
        try:
            if self.cano is not None:
                self.cano.send(("fim",))
                self.cano.close()
        except (OSError, EOFError, ValueError):
            pass
        try:
            self.processo.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.processo.kill()
        except OSError:
            pass
        try:
            self._escuta.close()
        except OSError:
            pass
        self._fechar_bloco()


class _ErroDoServidor(Exception):
    """O servidor respondeu com um erro que nao e do PDF (vira desenho aqui)."""


def _raiz() -> Path:
    return Path(__file__).resolve().parent.parent


def _comando_do_servidor(endereco: str, chave_hex: str) -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, ARGUMENTO_DO_SERVIDOR, endereco, chave_hex]
    return [sys.executable, "-m", "core.paginas_em_outro_processo", endereco, chave_hex]


_livres: "queue.Queue[_Servidor | None]" = queue.Queue()
_todos: list[_Servidor] = []
_tranca = threading.Lock()
_iniciado = False
_falhou_ao_subir = False


def _garantir_servidores() -> bool:
    """Sobe os servidores na primeira vez. False se nao deu (desenha aqui)."""
    global _iniciado, _falhou_ao_subir
    with _tranca:
        if _iniciado:
            return not _falhou_ao_subir
        _iniciado = True
        try:
            for _ in range(QUANTOS_SERVIDORES):
                servidor = _Servidor()
                _todos.append(servidor)
                _livres.put(servidor)
        except Exception:  # noqa: BLE001 - sem servidor, desenha aqui, como antes
            _anotar("nao consegui subir o servidor de paginas; desenhando aqui")
            _falhou_ao_subir = not _todos
        return not _falhou_ao_subir


def iniciar_em_segundo_plano() -> None:
    """Sobe os servidores numa thread, para o primeiro pedido nao esperar.
    Chamado quando a janela abre. Nunca levanta."""
    if ligado():
        threading.Thread(target=_garantir_servidores, daemon=True,
                         name="servidores de paginas").start()


# A pagina seguinte, adiantada (ver _adiantar): chave -> [pronta, imagem].
_adiantadas: dict[tuple, list] = {}
_tranca_das_adiantadas = threading.Lock()
MAXIMO_DE_ADIANTADAS = 2        # cada uma e uma pagina na memoria (10 a 26 MB)


def _chave(caminho: str, indice: int, dpi: int) -> tuple | None:
    """O pedido, com a marca do arquivo (se ele mudar no disco, a pagina
    adiantada nao vale mais)."""
    try:
        return (caminho, indice, dpi, os.path.getmtime(caminho), os.path.getsize(caminho))
    except OSError:
        return None


def pagina(caminho: str, indice: int, dpi: int, total: int | None = None) -> np.ndarray | None:
    """A pagina desenhada pelo servidor, ou None para desenhar aqui (servidor
    desligado ou quebrado). Levanta ErroPDF como pdf_io.pagina_para_array.

    `total` (o numero de paginas do PDF), quando dado, liga o adiantamento:
    enquanto quem pediu trabalha nesta pagina, o outro servidor ja desenha a
    seguinte (_adiantar) - a analise e o PDF final pedem as paginas em ordem.

    Servidor que caiu (o MuPDF ja derrubou processo em PDF estranho) e
    trocado por outro e o pedido e feito de novo, uma vez; se nao subir outro,
    None (desenha aqui) - e os proximos pedidos tambem, sem esperar.
    """
    if not ligado() or not _garantir_servidores():
        return None
    chave = _chave(caminho, indice, dpi)
    if chave is not None:
        with _tranca_das_adiantadas:
            adiantada = _adiantadas.pop(chave, None)
        if adiantada is not None and adiantada[0].wait(TEMPO_PARA_SUBIR_S) and adiantada[1] is not None:
            _adiantar(caminho, indice + 1, dpi, total)
            return adiantada[1]
    imagem = _pedir(caminho, indice, dpi)
    if imagem is not None:
        _adiantar(caminho, indice + 1, dpi, total)
    return imagem


def _adiantar(caminho: str, indice: int, dpi: int, total: int | None) -> None:
    """Pede, numa thread, a pagina `indice` ao servidor que estiver livre -
    so se houver um livre agora (nunca faz ninguem esperar) e se a pagina
    existir. O resultado fica em _adiantadas para o proximo pagina() que a
    pedir; se ninguem pedir, sai quando chegarem outras (MAXIMO_DE_ADIANTADAS)
    ou quando o livro for solto. Nao muda a imagem: e o mesmo pedido, feito
    antes. Seguro mudar: MAXIMO_DE_ADIANTADAS (0 desliga)."""
    if total is None or not 0 <= indice < total or MAXIMO_DE_ADIANTADAS <= 0:
        return
    chave = _chave(caminho, indice, dpi)
    if chave is None:
        return
    with _tranca_das_adiantadas:
        if chave in _adiantadas:
            return
        try:
            servidor = _livres.get_nowait()
        except queue.Empty:
            return
        if servidor is None or not servidor.vivo():
            _livres.put(servidor)
            return
        while len(_adiantadas) >= MAXIMO_DE_ADIANTADAS:
            _adiantadas.pop(next(iter(_adiantadas)))
        adiantada = [threading.Event(), None]
        _adiantadas[chave] = adiantada

    def desenhar() -> None:
        from core.pdf_io import ErroPDF

        try:
            adiantada[1] = servidor.pedir(caminho, indice, dpi)
            _livres.put(servidor)
        except (_ErroDoServidor, ErroPDF):
            _livres.put(servidor)
        except (OSError, EOFError, ValueError):
            novo = _trocar(servidor, f"o servidor de paginas caiu adiantando a pagina {indice + 1}")
            if novo is not None:
                _livres.put(novo)
        except BaseException:  # noqa: BLE001 - adiantar nunca derruba nada
            _livres.put(servidor)
        finally:
            adiantada[0].set()

    threading.Thread(target=desenhar, daemon=True, name="pagina adiantada").start()


def _pedir(caminho: str, indice: int, dpi: int) -> np.ndarray | None:
    """O pedido de uma pagina a um servidor livre (esperando um, se preciso)."""
    for tentativa in range(2):
        servidor = _livres.get()
        if servidor is None or _falhou_ao_subir:
            _livres.put(servidor)            # destrava o proximo que esperar
            return None
        if not servidor.vivo():
            servidor = _trocar(servidor, f"o servidor de paginas tinha caido (pagina {indice + 1})")
            if servidor is None:
                return None
        try:
            imagem = servidor.pedir(caminho, indice, dpi)
            _livres.put(servidor)
            return imagem
        except _ErroDoServidor as erro:
            _livres.put(servidor)
            _anotar(f"o servidor de paginas falhou na pagina {indice + 1}: {erro}")
            return None
        except (OSError, EOFError, ValueError):
            novo = _trocar(servidor, f"o servidor de paginas caiu na pagina {indice + 1} de {caminho}")
            if novo is None:
                return None
            _livres.put(novo)
            if tentativa == 1:
                return None
        except BaseException:
            _livres.put(servidor)
            raise
    return None


def soltar_livro(caminho: str | None = None) -> None:
    """Os servidores fecham o livro `caminho` (None = qualquer um) na hora,
    sem esperar o tempo parado: chamado quando o livro e fechado ou trocado
    (ui/tarefas.GerenciadorPrevias.parar, ui/widgets/tira_miniaturas.parar),
    para a pessoa poder mover o PDF logo em seguida. Espera cada servidor
    acabar o que esta fazendo (uma pagina). Nunca levanta."""
    with _tranca_das_adiantadas:
        for chave in [c for c in _adiantadas if caminho is None or c[0] == caminho]:
            _adiantadas.pop(chave)
    if not ligado() or not _iniciado or _falhou_ao_subir:
        return
    pegos = []
    try:
        for _ in range(len(_todos)):
            try:
                servidor = _livres.get(timeout=10)
            except queue.Empty:
                break
            pegos.append(servidor)
            if servidor is None or not servidor.vivo():
                continue
            try:
                servidor.cano.send(("soltar", caminho))
                servidor.cano.recv()
            except (OSError, EOFError, ValueError):
                pass
    finally:
        for servidor in pegos:
            _livres.put(servidor)


def _trocar(morto: _Servidor, motivo: str) -> _Servidor | None:
    """Fecha o servidor que caiu e sobe outro, que e devolvido (quem chamou o
    usa ou o devolve a fila). None se nao subir: dai em diante o desenho e
    feito aqui (e a fila recebe um None, para ninguem ficar esperando)."""
    global _falhou_ao_subir
    _anotar(motivo)
    morto.fechar()
    with _tranca:
        if morto in _todos:
            _todos.remove(morto)
        try:
            novo = _Servidor()
        except Exception:  # noqa: BLE001
            _anotar("nao consegui subir um servidor de paginas novo; desenhando aqui")
            _falhou_ao_subir = True
            _livres.put(None)
            return None
        _todos.append(novo)
        return novo


def _anotar(frase: str) -> None:
    try:
        from registro import registrar_erro

        registrar_erro("servidor de paginas", frase + "\n" + traceback.format_exc())
    except Exception:  # noqa: BLE001
        pass


@atexit.register
def encerrar() -> None:
    """Fecha os servidores (ao sair do programa, e nos testes)."""
    global _iniciado, _falhou_ao_subir
    with _tranca:
        for servidor in _todos:
            servidor.fechar()
        _todos.clear()
        while not _livres.empty():
            _livres.get_nowait()
        with _tranca_das_adiantadas:
            _adiantadas.clear()
        _iniciado = False
        _falhou_ao_subir = False


# ---------------------------------------------------------------------------
# lado do servidor
# ---------------------------------------------------------------------------


def servir(endereco: str, chave_hex: str) -> None:
    """O laco do servidor: recebe pedidos, desenha com pdf_io.pagina_para_array
    (aqui dentro, com a delegacao desligada) e devolve. Sai quando o programa
    pede ("fim") ou quando o cano quebra (o programa fechou ou caiu)."""
    from multiprocessing.connection import Client

    from multiprocessing import shared_memory

    os.environ[VARIAVEL_DESLIGA] = "1"
    from core.pdf_io import ErroPDF, abrir_pdf, pagina_para_array

    cano = Client(endereco, family="AF_PIPE", authkey=bytes.fromhex(chave_hex))
    bloco = None
    # O livro aberto agora (caminho, marca do arquivo, documento), ou None.
    # Fica aberto so enquanto chegam pedidos seguidos (a analise, a tira de
    # miniaturas): reabrir a cada pagina custava 3 a 4 ms (300 paginas = 1 s
    # a mais na analise). Arquivo aberto fica PRESO no Windows (nao se move,
    # renomeia nem apaga - achado pelo outro implementador em 30/09, 4 testes
    # quebrados), entao ele e fechado: depois de SEGUNDOS_PARADO sem pedido,
    # ao pedir outro livro, e quando o programa manda "soltar" (o livro foi
    # fechado ou trocado: soltar_livro). Arriscado: tirar o fechamento por
    # tempo parado ou o "soltar".
    aberto = None

    def fechar_o_aberto() -> None:
        nonlocal aberto
        if aberto is not None:
            try:
                aberto[2].close()
            except Exception:  # noqa: BLE001
                pass
            aberto = None

    try:
        while True:
            try:
                if aberto is not None and not cano.poll(SEGUNDOS_PARADO):
                    fechar_o_aberto()                 # parado: solta o arquivo
                pedido = cano.recv()
            except (EOFError, OSError):
                return
            if pedido[0] == "soltar":
                if aberto is not None and (pedido[1] is None or aberto[0] == pedido[1]):
                    fechar_o_aberto()
                cano.send(("solto",))
                continue
            if pedido[0] != "pagina":
                return
            _, caminho, indice, dpi = pedido
            try:
                marca = (os.path.getmtime(caminho), os.path.getsize(caminho))
                if aberto is None or aberto[0] != caminho or aberto[1] != marca:
                    fechar_o_aberto()
                    aberto = (caminho, marca, abrir_pdf(caminho))
                imagem = pagina_para_array(aberto[2], indice, dpi=dpi)
                altura, largura, canais = imagem.shape
                # A imagem vai pelo bloco de memoria compartilhada (um so,
                # trocado por um maior quando a pagina nao cabe): o programa
                # copia de la antes de pedir a proxima.
                if bloco is None or bloco.size < imagem.nbytes:
                    if bloco is not None:
                        bloco.close()
                        bloco.unlink()
                    bloco = shared_memory.SharedMemory(
                        create=True, size=max(imagem.nbytes * 5 // 4, 1 << 20))
                vista = np.ndarray(imagem.shape, dtype=np.uint8, buffer=bloco.buf)
                vista[...] = imagem
                del vista
                cano.send(("ok", altura, largura, canais, bloco.name))
            except ErroPDF as erro:
                cano.send(("erro", "ErroPDF", str(erro)))
            except Exception as erro:  # noqa: BLE001
                cano.send(("erro", type(erro).__name__, str(erro)))
    finally:
        fechar_o_aberto()
        if bloco is not None:
            try:
                bloco.close()
                bloco.unlink()
            except (OSError, BufferError):
                pass
        cano.close()


if __name__ == "__main__":
    servir(sys.argv[1], sys.argv[2])
