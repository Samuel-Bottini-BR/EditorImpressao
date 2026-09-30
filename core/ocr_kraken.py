"""Ponte até o motor do Kraken: acha as LINHAS DE TEXTO de uma página (item 1.3 da Fase 1).

O QUE FAZ
    O Kraken (segmentador "blla") não roda no Python 3.14 do programa. Por
    decisão do Samuel (29/09/2026), ele roda num MOTOR À PARTE: um Python 3.12
    embutível com o Kraken original e o PyTorch para processador, montado por
    montar_motor_kraken.py e instalado junto do programa. Este módulo:

      1. acha a pasta do motor (achar_pasta_do_motor);
      2. abre o motor como outro processo, UMA vez, e espera ele dizer
         "pronto" (6 a 7 s neste PC; mais na primeira vez depois de instalar);
      3. manda cada página (a imagem vai por um arquivo .npy temporário) e
         recebe as linhas: linha de base e contorno (polígono), em pontos da
         imagem enviada;
      4. fecha o motor (fechar(), ou "with MotorKraken() as motor:").

    Só ACHA ONDE ESTÁ O TEXTO. Não transcreve (Fase 7).

    Uso:
        with MotorKraken() as motor:
            for pagina in paginas:            # uma por vez (regra da memória)
                r = motor.segmentar(pagina)   # BGR, como o resto do programa
                if not r.disponivel:
                    avisar(r.motivo)          # português, para a tela
                elif r.precisa_revisar:
                    ...                       # o Kraken jogou linhas fora

NADA AQUI DERRUBA O PROGRAMA
    Motor ausente, motor que não abre, que morre no meio, que responde errado,
    que passa do tempo, ou pedido cancelado: segmentar() devolve um
    ResultadoOCR "indisponível" (linhas None), com o motivo em português
    (para a tela) e o detalhe técnico (para o erros.log, via logging). Nenhuma
    exceção sai daqui. Motor que passou do tempo, foi cancelado ou respondeu
    errado é FECHADO À FORÇA (só o processo do motor, nunca o programa).

NÃO TRAVA A TELA, MAS É LENTO
    Cada página leva ~10 s neste PC (15 a 25 s estimados no notebook do
    Kaique). segmentar() BLOQUEIA até a resposta: quem chamar tem de estar
    numa QThread. Este módulo não usa Qt (core/ não importa ui/). Para
    cancelar, passe cancelar=<função que devolve True>; ela é consultada
    a cada 0,2 s, e cancelar fecha o motor (o Kraken não para no meio de uma
    página). O motor roda com prioridade "abaixo do normal" para a janela
    continuar respondendo.

AINDA NÃO ESTÁ LIGADO AO PROGRAMA (29/09/2026)
    Nem o pipeline, nem a tela, nem o empacotador usam este módulo ainda: a
    ligação vem na etapa seguinte do item 1.3, junto com o docTR e a
    comparação automática entre os OCRs (onde discordam, "Para revisar").

"PARA REVISAR"
    O Kraken 7.1.1, quando não consegue desenhar o contorno de uma linha,
    avisa "Polygonizer failed" e JOGA A LINHA FORA sem dizer nada a quem
    chamou (a pesquisa achou 8 linhas perdidas no Opus Majus 256). O motor
    conta esses avisos: extra["falhas_contorno"]; eles entram em
    ResultadoOCR.perdidas, e precisa_revisar é
    True quando há falha.

O QUE É SEGURO MUDAR
    Os textos das mensagens; os tempos-limite (TEMPO_PARA_ABRIR,
    TEMPO_POR_PAGINA); a ordem dos lugares onde se procura o motor.

O QUE É ARRISCADO MUDAR
    - VERSAO_PROTOCOLO: tem de bater com motor_kraken/servidor_kraken.py
      (motor com versão diferente é recusado, com aviso para remontar).
    - O "-I -X utf8" do comando: o -I isola o motor das bibliotecas do Python
      do usuário (sem ele, uma pasta do usuário entrou no caminho, na
      pesquisa); o -X utf8 substitui o PYTHONUTF8, que o -I ignora.
    - A conversão BGR -> RGB antes de mandar: a rede do Kraken olha as cores;
      mandar trocado muda as linhas.
    - Ler a saída de erro do motor numa linha de execução própria: sem isso,
      quando o Kraken escreve muito aviso, o cano enche e os dois processos
      ficam esperando um ao outro para sempre.
"""

from __future__ import annotations

import collections
import json
import logging
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Callable

import numpy as np

from core.ocr_comum import MOTOR_KRAKEN, LinhaOCR, ResultadoOCR, indisponivel

_log = logging.getLogger(__name__)

# Tem de bater com motor_kraken/servidor_kraken.py.
VERSAO_PROTOCOLO = 1

# Segundos. Abrir: 6 a 7 s neste PC com o disco "quente"; logo depois de
# instalar (antivírus lendo 1,2 GB) pode passar de 30 s, daí a folga.
# Página: 5 a 25 s neste PC (Opus Majus 256, a tabela, é a mais lenta).
TEMPO_PARA_ABRIR = 180.0
TEMPO_POR_PAGINA = 600.0
TEMPO_PARA_FECHAR = 5.0

NOME_DA_PASTA = "motor-kraken"
NOME_DO_SERVIDOR = "servidor_kraken.py"

# Windows: sem janela preta de console; prioridade abaixo do normal.
_SEM_JANELA = 0x08000000
_PRIORIDADE_BAIXA = 0x00004000

_AVISO_AUSENTE = ("O detector de linhas do Kraken não está instalado (falta a pasta do motor). "
                  "As outras funções continuam funcionando.")
_AVISO_NAO_ABRIU = "O detector de linhas do Kraken não conseguiu abrir."
_AVISO_MORREU = "O detector de linhas do Kraken parou de funcionar no meio da página."
_AVISO_DEMOROU = "O detector de linhas do Kraken demorou demais e foi fechado."
_AVISO_RESPOSTA = "O detector de linhas do Kraken respondeu algo que o programa não entendeu."
_AVISO_CANCELADO = "Cancelado."
_AVISO_PAGINA = "O detector de linhas do Kraken não conseguiu ler esta página."
_AVISO_VERSAO = ("O detector de linhas do Kraken instalado é de outra versão do programa. "
                 "É preciso reinstalar o programa.")


def _raiz_do_codigo() -> Path:
    return Path(__file__).resolve().parent.parent


def lugares_do_motor() -> list[Path]:
    """Onde o motor é procurado, em ordem.

    1. Ao lado do programa instalado ({app}\\motor-kraken, quando o programa
       roda empacotado pelo PyInstaller).
    2. Na raiz do código (motor-kraken\\, para quem quiser deixar ali; fora do git).
    3. A pasta onde montar_motor_kraken.py monta por padrão (fora do git):
       D:\\programas\\EditorImpressao-arquivos\\ferramentas\\motor-kraken
    """
    lugares = []
    if getattr(sys, "frozen", False):
        lugares.append(Path(sys.executable).resolve().parent / NOME_DA_PASTA)
    raiz = _raiz_do_codigo()
    lugares.append(raiz / NOME_DA_PASTA)
    lugares.append(raiz.parent / "EditorImpressao-arquivos" / "ferramentas" / NOME_DA_PASTA)
    return lugares


def _e_motor(pasta: Path) -> bool:
    return (pasta / "python" / "python.exe").is_file() and (pasta / NOME_DO_SERVIDOR).is_file()


def achar_pasta_do_motor() -> Path | None:
    """A primeira pasta de lugares_do_motor() que tem um motor completo, ou None."""
    for pasta in lugares_do_motor():
        try:
            if _e_motor(pasta):
                return pasta
        except OSError:
            continue
    return None


# O resultado é o tipo comum dos OCRs (core/ocr_comum.py, desde 29/09/2026;
# antes era um ResultadoKraken próprio). Do Kraken:
#   - linhas: LinhaOCR com poligono (o contorno) E linha_de_base; confianca
#     None e palavras 0 (o Kraken não separa palavras); palavras do resultado None;
#   - perdidas = falhas_contorno + linhas_sem_contorno (> 0 = "Para revisar");
#   - extra: {"regioes": {"text": 4, ...}, "falhas_contorno": n,
#     "linhas_sem_contorno": m}.
# "falhas_contorno": linhas que o Kraken jogou fora por não conseguir o
# contorno ("Polygonizer failed"); "linhas_sem_contorno": linhas que vieram com
# contorno vazio (não entram em linhas).


def _indisponivel(motivo: str, detalhe: str | None = None) -> ResultadoOCR:
    return indisponivel(MOTOR_KRAKEN, motivo, detalhe)


class _MotorNaoRespondeu(Exception):
    """Uso interno: o motor morreu, passou do tempo, foi cancelado ou respondeu errado."""

    def __init__(self, motivo: str, detalhe: str) -> None:
        super().__init__(detalhe)
        self.motivo = motivo
        self.detalhe = detalhe


class MotorKraken:
    """O processo do motor do Kraken. Abre na primeira página e serve o livro inteiro.

    Uma página por vez (uma tranca protege a conversa). Pode ser usado de uma
    QThread. Sempre feche (fechar() ou "with"): um motor aberto ocupa ~1,3 GB.
    Se o programa morrer sem fechar, o motor percebe que a entrada fechou e sai.
    """

    def __init__(self, pasta: Path | str | None = None, *, comando: list[str] | None = None,
                 tempo_para_abrir: float = TEMPO_PARA_ABRIR,
                 tempo_por_pagina: float = TEMPO_POR_PAGINA,
                 prioridade_baixa: bool = True) -> None:
        """pasta: a pasta do motor (None = procurar em lugares_do_motor()).
        comando: só para os testes - roda outro programa no lugar do motor.
        """
        self.pasta = Path(pasta) if pasta is not None else None
        self._comando_de_teste = list(comando) if comando else None
        self.tempo_para_abrir = tempo_para_abrir
        self.tempo_por_pagina = tempo_por_pagina
        self.prioridade_baixa = prioridade_baixa
        self.info: dict = {}                 # o que o motor disse ao abrir (versões, tempos)
        self.segundos_para_abrir: float = 0.0
        self._processo: subprocess.Popen | None = None
        self._respostas: queue.Queue = queue.Queue()
        self._erros_do_motor: collections.deque[str] = collections.deque(maxlen=60)
        self._proximo_id = 0
        self._falha_ao_abrir: ResultadoOCR | None = None
        self._tranca = threading.RLock()

    # ------------------------------------------------------------ abrir e fechar

    def __enter__(self) -> "MotorKraken":
        return self

    def __exit__(self, *_ignorado) -> None:
        self.fechar()

    @property
    def aberto(self) -> bool:
        return self._processo is not None and self._processo.poll() is None

    def _comando(self) -> tuple[list[str] | None, Path | None, ResultadoOCR | None]:
        if self._comando_de_teste:
            return self._comando_de_teste, None, None
        pasta = self.pasta if self.pasta is not None else achar_pasta_do_motor()
        if pasta is None or not _e_motor(pasta):
            onde = str(pasta) if pasta is not None else ", ".join(str(p) for p in lugares_do_motor())
            return None, None, _indisponivel(_AVISO_AUSENTE, f"motor não encontrado em: {onde}")
        python = pasta / "python" / "python.exe"
        return [str(python), "-I", "-X", "utf8", str(pasta / NOME_DO_SERVIDOR)], pasta, None

    def _abrir(self) -> ResultadoOCR | None:
        """Abre o motor, se ainda não estiver aberto. Devolve None se deu certo, ou o aviso."""
        if self.aberto:
            return None
        if self._falha_ao_abrir is not None:     # não tenta de novo a cada página
            return self._falha_ao_abrir
        comando, pasta, falha = self._comando()
        if falha is not None:
            self._falha_ao_abrir = falha
            return falha
        self._respostas = queue.Queue()
        self._erros_do_motor.clear()
        bandeiras = 0
        if os.name == "nt":
            bandeiras = _SEM_JANELA | (_PRIORIDADE_BAIXA if self.prioridade_baixa else 0)
        inicio = time.perf_counter()
        try:
            self._processo = subprocess.Popen(
                comando, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=str(pasta) if pasta else None, creationflags=bandeiras)
        except OSError as erro:
            self._processo = None
            self._falha_ao_abrir = _indisponivel(_AVISO_NAO_ABRIU, f"não consegui iniciar {comando[0]}: {erro}")
            return self._falha_ao_abrir
        processo = self._processo
        threading.Thread(target=self._ler_respostas, args=(processo, self._respostas),
                         name="kraken-respostas", daemon=True).start()
        threading.Thread(target=self._ler_erros, args=(processo,), name="kraken-erros",
                         daemon=True).start()
        try:
            pronto = self._esperar(lambda m: "tipo" in m, self.tempo_para_abrir, None, _AVISO_NAO_ABRIU)
        except _MotorNaoRespondeu as erro:
            self._matar()
            self._falha_ao_abrir = _indisponivel(erro.motivo, erro.detalhe)
            return self._falha_ao_abrir
        if pronto.get("tipo") != "pronto":
            self._matar()
            self._falha_ao_abrir = _indisponivel(
                _AVISO_NAO_ABRIU, f"o motor não abriu: {pronto.get('erro')!r}; {self._ultimos_erros()}")
            return self._falha_ao_abrir
        if pronto.get("versao_protocolo") != VERSAO_PROTOCOLO:
            self._matar()
            self._falha_ao_abrir = _indisponivel(
                _AVISO_VERSAO, f"protocolo do motor {pronto.get('versao_protocolo')!r}, "
                               f"do programa {VERSAO_PROTOCOLO} (rode montar_motor_kraken.py --so-servidor)")
            return self._falha_ao_abrir
        self.info = pronto
        self.segundos_para_abrir = time.perf_counter() - inicio
        _log.info("ocr_kraken: motor aberto em %.1f s (%s)", self.segundos_para_abrir,
                  {k: pronto.get(k) for k in ("kraken", "python", "torch", "threads")})
        return None

    def fechar(self) -> None:
        """Pede para o motor sair; se não sair em TEMPO_PARA_FECHAR segundos, fecha à força."""
        with self._tranca:
            self._falha_ao_abrir = None      # depois de fechar, a próxima página tenta abrir de novo
            processo = self._processo
            if processo is None:
                return
            try:
                if processo.poll() is None and processo.stdin is not None:
                    processo.stdin.write(b'{"comando": "sair"}\n')
                    processo.stdin.flush()
                    processo.stdin.close()
                processo.wait(timeout=TEMPO_PARA_FECHAR)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                pass
            self._matar()

    def _matar(self) -> None:
        """Fecha à força o processo do motor (só ele) e esquece o processo."""
        processo, self._processo = self._processo, None
        if processo is None:
            return
        try:
            if processo.poll() is None:
                processo.kill()
            processo.wait(timeout=TEMPO_PARA_FECHAR)
        except (OSError, subprocess.TimeoutExpired) as erro:
            _log.warning("ocr_kraken: não consegui fechar o motor (%s)", erro)
        for cano in (processo.stdin, processo.stdout, processo.stderr):
            try:
                if cano is not None:
                    cano.close()
            except OSError:
                pass

    # ------------------------------------------------------------ leitura dos canos

    @staticmethod
    def _ler_respostas(processo: subprocess.Popen, fila: queue.Queue) -> None:
        """Linha de execução: cada linha da saída padrão do motor vira um item da fila."""
        try:
            for bruto in processo.stdout:
                fila.put(bruto)
        except (OSError, ValueError):
            pass
        fila.put(None)   # fim: o motor fechou a saída (saiu ou morreu)

    def _ler_erros(self, processo: subprocess.Popen) -> None:
        """Linha de execução: guarda o fim da saída de erro do motor (para o log)."""
        try:
            for bruto in processo.stderr:
                texto = bruto.decode("utf-8", errors="replace").rstrip()
                if texto:
                    self._erros_do_motor.append(texto)
        except (OSError, ValueError):
            pass

    def _ultimos_erros(self, quantos: int = 8) -> str:
        linhas = list(self._erros_do_motor)[-quantos:]
        return ("saída de erro do motor: " + " | ".join(linhas)) if linhas else "motor não escreveu nada"

    def _esperar(self, aceita: Callable[[dict], bool], tempo_limite: float,
                 cancelar: Callable[[], bool] | None, aviso_se_morrer: str) -> dict:
        """Espera a próxima mensagem aceita. Levanta _MotorNaoRespondeu se não vier."""
        limite = time.monotonic() + tempo_limite
        while True:
            if cancelar is not None:
                try:
                    cancelado = bool(cancelar())
                except Exception as erro:   # a função de cancelar quebrou: trata como cancelar
                    cancelado = True
                    _log.warning("ocr_kraken: a função cancelar() falhou (%s)", erro)
                if cancelado:
                    raise _MotorNaoRespondeu(_AVISO_CANCELADO, "cancelado por quem chamou")
            restante = limite - time.monotonic()
            if restante <= 0:
                raise _MotorNaoRespondeu(_AVISO_DEMOROU, f"sem resposta em {tempo_limite:.0f} s; "
                                                         f"{self._ultimos_erros()}")
            try:
                bruto = self._respostas.get(timeout=min(0.2, restante))
            except queue.Empty:
                continue
            if bruto is None:
                codigo = self._processo.poll() if self._processo else None
                time.sleep(0.1)   # dá tempo à outra linha de execução de ler o fim do erro
                raise _MotorNaoRespondeu(aviso_se_morrer, f"o motor saiu (código {codigo}); "
                                                          f"{self._ultimos_erros()}")
            try:
                mensagem = json.loads(bruto.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise _MotorNaoRespondeu(_AVISO_RESPOSTA, f"linha que não é JSON: {bruto[:200]!r}")
            if not isinstance(mensagem, dict):
                raise _MotorNaoRespondeu(_AVISO_RESPOSTA, f"resposta que não é objeto: {bruto[:200]!r}")
            if aceita(mensagem):
                return mensagem
            _log.debug("ocr_kraken: mensagem ignorada: %r", mensagem)

    def _pedir(self, pedido: dict, tempo_limite: float,
               cancelar: Callable[[], bool] | None) -> dict:
        """Manda um pedido e espera a resposta com o mesmo id. Levanta _MotorNaoRespondeu."""
        self._proximo_id += 1
        identificador = self._proximo_id
        pedido = dict(pedido, id=identificador)
        try:
            self._processo.stdin.write((json.dumps(pedido, ensure_ascii=False) + "\n").encode("utf-8"))
            self._processo.stdin.flush()
        except (OSError, ValueError, AttributeError) as erro:
            raise _MotorNaoRespondeu(_AVISO_MORREU, f"não consegui mandar o pedido: {erro}; "
                                                    f"{self._ultimos_erros()}")
        return self._esperar(lambda m: m.get("id") == identificador, tempo_limite, cancelar, _AVISO_MORREU)

    # ------------------------------------------------------------ o que se pede

    def segmentar(self, imagem: np.ndarray | str | Path, *, ordem: str = "BGR",
                  cancelar: Callable[[], bool] | None = None) -> ResultadoOCR:
        """Acha as linhas de texto de UMA página.

        imagem: uint8, altura x largura (cinza) ou altura x largura x 3 (BGR,
            como o resto do programa; ordem="RGB" para RGB). Um 4.º canal é
            ignorado. Ou o caminho de um arquivo de imagem (o motor o abre).
        cancelar: função sem argumentos; devolvendo True, o motor é fechado e
            o resultado vem "Cancelado." (a próxima chamada abre de novo).
        Nunca levanta exceção (ver docstring do módulo).
        """
        try:
            return self._segmentar(imagem, ordem, cancelar)
        except Exception as erro:   # rede de segurança: nada sai daqui como exceção
            _log.exception("ocr_kraken: erro inesperado")
            return _indisponivel(_AVISO_PAGINA, f"{type(erro).__name__}: {erro}")

    def _segmentar(self, imagem, ordem: str, cancelar) -> ResultadoOCR:
        temporario = None
        try:
            if isinstance(imagem, (str, Path)):
                caminho = Path(imagem)
                if not caminho.is_file():
                    return _indisponivel(_AVISO_PAGINA, f"imagem não encontrada: {caminho}")
            else:
                matriz = _para_rgb(imagem, ordem)
                if matriz is None:
                    return _indisponivel(_AVISO_PAGINA, f"imagem inválida: {getattr(imagem, 'dtype', type(imagem))} "
                                                        f"{getattr(imagem, 'shape', '')}")
                descritor, nome = tempfile.mkstemp(prefix="kraken-pagina-", suffix=".npy")
                temporario = Path(nome)
                with os.fdopen(descritor, "wb") as arquivo:
                    np.save(arquivo, matriz, allow_pickle=False)
                caminho = temporario
            with self._tranca:
                falha = self._abrir()
                if falha is not None:
                    return falha
                try:
                    resposta = self._pedir({"comando": "segmentar", "imagem": str(caminho)},
                                           self.tempo_por_pagina, cancelar)
                except _MotorNaoRespondeu as erro:
                    self._matar()    # estado desconhecido: a próxima página abre um motor novo
                    return _indisponivel(erro.motivo, erro.detalhe)
            return _ler_resultado(resposta)
        finally:
            if temporario is not None:
                try:
                    temporario.unlink()
                except OSError as erro:
                    _log.warning("ocr_kraken: não apaguei o temporário %s (%s)", temporario, erro)

    def diagnostico(self) -> dict | None:
        """Versões e as DLLs da Microsoft que o motor carregou (None se não deu)."""
        try:
            with self._tranca:
                if self._abrir() is not None:
                    return None
                try:
                    resposta = self._pedir({"comando": "diagnostico"}, 60.0, None)
                except _MotorNaoRespondeu as erro:
                    self._matar()
                    _log.warning("ocr_kraken: diagnóstico falhou (%s)", erro.detalhe)
                    return None
            return resposta if resposta.get("ok") else None
        except Exception:
            _log.exception("ocr_kraken: erro inesperado no diagnóstico")
            return None


def _para_rgb(imagem, ordem: str) -> np.ndarray | None:
    """A página como o motor espera: uint8, cinza (A x L) ou RGB (A x L x 3), contígua."""
    if not isinstance(imagem, np.ndarray) or imagem.dtype != np.uint8 or imagem.size == 0:
        return None
    if imagem.ndim == 2:
        return np.ascontiguousarray(imagem)
    if imagem.ndim != 3 or imagem.shape[2] not in (1, 3, 4):
        return None
    if imagem.shape[2] == 1:
        return np.ascontiguousarray(imagem[:, :, 0])
    tres = imagem[:, :, :3]
    if ordem.upper() == "BGR":
        tres = tres[:, :, ::-1]
    elif ordem.upper() != "RGB":
        return None
    return np.ascontiguousarray(tres)


def _ler_resultado(resposta: dict) -> ResultadoOCR:
    """Transforma a resposta do motor em ResultadoOCR, conferindo o formato."""
    if not resposta.get("ok"):
        return _indisponivel(_AVISO_PAGINA, f"o motor recusou a página: {resposta.get('erro')!r}")
    try:
        linhas = []
        for item in resposta["linhas"]:
            base = np.asarray(item["linha_de_base"], dtype=np.float32).reshape(-1, 2)
            poligono = np.asarray(item["poligono"], dtype=np.float32).reshape(-1, 2)
            if len(poligono) < 3 or not (np.isfinite(base).all() and np.isfinite(poligono).all()):
                raise ValueError("linha com contorno inválido")
            linhas.append(LinhaOCR(poligono, linha_de_base=base))
        falhas = int(resposta.get("falhas_contorno", 0))
        sem_contorno = int(resposta.get("linhas_sem_contorno", 0))
        return ResultadoOCR(
            MOTOR_KRAKEN, linhas, palavras=None, perdidas=falhas + sem_contorno,
            segundos=float(resposta.get("segundos", 0.0)),
            largura=int(resposta.get("largura", 0)), altura=int(resposta.get("altura", 0)),
            extra={"regioes": dict(resposta.get("regioes") or {}),
                   "falhas_contorno": falhas, "linhas_sem_contorno": sem_contorno})
    except (KeyError, TypeError, ValueError) as erro:
        return _indisponivel(_AVISO_RESPOSTA, f"resposta fora do formato: {erro}; {str(resposta)[:300]}")


def segmentar_pagina(imagem: np.ndarray | str | Path, **opcoes) -> ResultadoOCR:
    """Atalho para UMA página só: abre o motor, segmenta e fecha (paga os 6-7 s de abrir).

    Para um livro, use MotorKraken diretamente e mantenha-o aberto.
    """
    with MotorKraken() as motor:
        return motor.segmentar(imagem, **opcoes)
