"""Servidor do motor do Kraken: roda DENTRO do Python 3.12 à parte (item 1.3 da Fase 1).

    <motor>\\python\\python.exe -I -X utf8 <motor>\\servidor_kraken.py

O QUE FAZ
    Abre o Kraken e o modelo "blla" UMA vez (6 a 7 s) e fica esperando pedidos,
    para o programa não pagar esse arranque a cada página. Só ACHA ONDE ESTÃO
    AS LINHAS DE TEXTO (segmentação "blla"); não transcreve (isso é Fase 7).

    Quem chama é core/ocr_kraken.py (no Python 3.14 do programa). Este arquivo
    é copiado para a pasta do motor por montar_motor_kraken.py; o original
    fica em motor_kraken/ (no git).

A CONVERSA (uma linha de JSON por mensagem, em UTF-8)
    Ao abrir, o servidor manda:
        {"tipo": "pronto", "versao_protocolo": 1, "kraken": "7.1.1", "python": "3.12.10",
         "torch": "...", "segundos_importar": 6.1, "segundos_modelo": 0.5}
    ou, se não conseguir abrir:
        {"tipo": "falhou", "erro": "..."}  (e sai)

    Pedidos (entrada padrão), cada um com um "id" que volta na resposta:
        {"id": 1, "comando": "segmentar", "imagem": "C:\\...\\pagina.npy"}
            A imagem é um .npy (matriz de pontos, cinza ou RGB, uint8) ou
            qualquer arquivo de imagem que o Pillow abra. É lida, convertida
            para RGB (como na régua do WSL) e segmentada no processador.
        {"id": 2, "comando": "diagnostico"}
            Versões e de onde vieram as DLLs da Microsoft carregadas.
        {"id": 3, "comando": "sair"}

    Resposta de "segmentar":
        {"id": 1, "ok": true, "largura": L, "altura": A, "segundos": s,
         "linhas": [{"linha_de_base": [[x, y], ...], "poligono": [[x, y], ...]}, ...],
         "falhas_contorno": n, "linhas_sem_contorno": m, "regioes": {"text": 4}}
        Coordenadas em pontos da imagem recebida. "falhas_contorno" conta as
        mensagens "Polygonizer failed" do Kraken: nessas linhas ele não
        conseguiu desenhar o contorno e JOGOU A LINHA FORA em silêncio (a
        pesquisa achou 8 no Opus Majus 256). Com n > 0 a página deve ir para
        "Para revisar". "linhas_sem_contorno" conta linhas que vieram com
        contorno vazio (não entram em "linhas").
    Erro num pedido nunca derruba o servidor:
        {"id": 1, "ok": false, "erro": "tipo: mensagem"}

    A saída padrão é SÓ da conversa: logo no começo ela é desviada para um
    canal próprio, e tudo o que o Kraken, o PyTorch ou uma biblioteca em C
    imprimir cai na saída de erro (que o programa guarda para o log).
    Quando a entrada padrão fecha (o programa fechou ou morreu), o servidor sai.

O QUE É ARRISCADO MUDAR
    - VERSAO_PROTOCOLO: tem de bater com core/ocr_kraken.py e com
      montar_motor_kraken.py. Mudou o formato de pedido/resposta? Suba os três.
    - O .convert("RGB") e o device="cpu": são os da régua do WSL (relatório do
      1.3). Mudar pode mudar as linhas achadas.
    - A contagem de "Polygonizer failed" depende do texto da mensagem de aviso
      do Kraken 7.1.1 (kraken/lib/segmentation.py). Trocar a versão do Kraken
      = conferir que a mensagem continua a mesma (tests/test_ocr_kraken.py tem
      o Opus Majus 256, que tem 8 falhas).
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import traceback

VERSAO_PROTOCOLO = 1

_TEXTO_DA_FALHA = "Polygonizer failed"


class _ContadorDeFalhas(logging.Handler):
    """Conta os avisos "Polygonizer failed" que o Kraken dá e engole."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.falhas = 0
        self.mensagens: list[str] = []

    def emit(self, registro: logging.LogRecord) -> None:
        try:
            texto = registro.getMessage()
        except Exception:   # mensagem mal formada: não conta, não quebra
            return
        if _TEXTO_DA_FALHA in texto:
            self.falhas += 1
            if len(self.mensagens) < 20:
                self.mensagens.append(texto[:300])


def _desviar_saida_padrao():
    """Guarda a saída padrão verdadeira para a conversa e manda o resto para a saída de erro."""
    canal = os.fdopen(os.dup(1), "w", encoding="utf-8", newline="\n", buffering=1)
    os.dup2(2, 1)          # printf de biblioteca em C vai para a saída de erro
    sys.stdout = sys.stderr
    return canal


def _versao_do_kraken() -> str:
    """A versão instalada do Kraken (o pacote não tem __version__)."""
    try:
        from importlib.metadata import version

        return version("kraken")
    except Exception:
        return "?"


def _mandar(canal, mensagem: dict) -> None:
    canal.write(json.dumps(mensagem, ensure_ascii=False) + "\n")
    canal.flush()


def _abrir_imagem(caminho: str):
    import numpy as np
    from PIL import Image

    if caminho.lower().endswith(".npy"):
        matriz = np.load(caminho, allow_pickle=False)
        if matriz.dtype != np.uint8 or matriz.ndim not in (2, 3):
            raise ValueError(f"matriz {matriz.dtype} {matriz.shape}: esperava uint8 cinza ou RGB")
        if matriz.ndim == 3 and matriz.shape[2] == 1:
            matriz = matriz[:, :, 0]
        imagem = Image.fromarray(np.ascontiguousarray(matriz))
    else:
        imagem = Image.open(caminho)
        imagem.load()
    return imagem.convert("RGB")


def _pontos(sequencia) -> list[list[float]]:
    return [[float(x), float(y)] for x, y in (sequencia or [])]


def _segmentar(pedido: dict, modelo, contador: _ContadorDeFalhas) -> dict:
    from kraken import blla

    imagem = _abrir_imagem(str(pedido["imagem"]))
    contador.falhas = 0
    contador.mensagens = []
    inicio = time.perf_counter()
    seg = blla.segment(imagem, model=modelo, device="cpu")
    segundos = time.perf_counter() - inicio
    linhas, sem_contorno = [], 0
    for linha in seg.lines:
        contorno = _pontos(linha.boundary)
        if len(contorno) < 3:
            sem_contorno += 1
            continue
        linhas.append({"linha_de_base": _pontos(linha.baseline), "poligono": contorno})
    regioes = {str(k): len(v) for k, v in (seg.regions or {}).items()}
    return {"ok": True, "largura": imagem.width, "altura": imagem.height, "segundos": segundos,
            "linhas": linhas, "falhas_contorno": contador.falhas,
            "mensagens_das_falhas": contador.mensagens, "linhas_sem_contorno": sem_contorno,
            "regioes": regioes}


def _diagnostico() -> dict:
    """Versões e as DLLs da Microsoft (Visual C++) carregadas, com o caminho de cada uma."""
    import kraken
    import torch

    dlls = []
    try:
        import psutil

        for mapa in psutil.Process().memory_maps(grouped=True):
            nome = os.path.basename(mapa.path).lower()
            if nome.startswith(("msvcp140", "vcruntime140", "concrt140", "vcomp140")):
                dlls.append(mapa.path)
    except Exception as erro:   # diagnóstico nunca derruba o servidor
        dlls.append(f"(não consegui listar: {erro})")
    return {"ok": True, "python": sys.version.split()[0], "executavel": sys.executable,
            "kraken": _versao_do_kraken(), "torch": torch.__version__,
            "threads": torch.get_num_threads(), "dlls_da_microsoft": sorted(dlls)}


def main() -> int:
    canal = _desviar_saida_padrao()
    try:
        inicio = time.perf_counter()
        import torch
        import kraken
        from kraken import blla  # noqa: F401  (carrega já, para o arranque ficar todo aqui)
        from kraken.lib import vgsl
        segundos_importar = time.perf_counter() - inicio

        contador = _ContadorDeFalhas()
        logging.getLogger("kraken").addHandler(contador)
        # Os avisos também vão para a saída de erro (que o programa guarda no log).
        logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

        # O modelo padrão, que vem dentro do pacote do Kraken 7.1.1 (o da régua do WSL).
        caminho_modelo = os.path.join(os.path.dirname(kraken.__file__), "blla.mlmodel")
        inicio = time.perf_counter()
        modelo = vgsl.TorchVGSLModel.load_model(caminho_modelo)
        segundos_modelo = time.perf_counter() - inicio
    except BaseException as erro:
        traceback.print_exc()
        _mandar(canal, {"tipo": "falhou", "erro": f"{type(erro).__name__}: {erro}"})
        return 1

    _mandar(canal, {"tipo": "pronto", "versao_protocolo": VERSAO_PROTOCOLO,
                    "kraken": _versao_do_kraken(), "python": sys.version.split()[0],
                    "torch": torch.__version__, "threads": torch.get_num_threads(),
                    "modelo": os.path.basename(caminho_modelo),
                    "segundos_importar": segundos_importar, "segundos_modelo": segundos_modelo})

    entrada = sys.stdin.buffer
    for bruto in entrada:
        texto = bruto.decode("utf-8", errors="replace").strip()
        if not texto:
            continue
        identificador = None
        try:
            pedido = json.loads(texto)
            if not isinstance(pedido, dict):
                raise ValueError("pedido não é um objeto JSON")
            identificador = pedido.get("id")
            comando = pedido.get("comando")
            if comando == "sair":
                _mandar(canal, {"id": identificador, "ok": True})
                break
            if comando == "segmentar":
                resposta = _segmentar(pedido, modelo, contador)
            elif comando == "diagnostico":
                resposta = _diagnostico()
            else:
                raise ValueError(f"comando desconhecido: {comando!r}")
        except Exception as erro:
            traceback.print_exc()
            resposta = {"ok": False, "erro": f"{type(erro).__name__}: {erro}"}
        resposta["id"] = identificador
        _mandar(canal, resposta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
