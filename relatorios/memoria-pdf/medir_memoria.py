"""Mede a memória do programa ao processar um livro e gerar o PDF (04/11/2026).

PARA QUE SERVE
    Responder, com medida e não com chute, à pergunta do Samuel sobre o aviso
    "Este livro ficou grande demais para a memória do computador": o pico de
    memória do programa cresce com o tamanho do livro? Roda as MESMAS funções
    do programa (core.pipeline.analisar_projeto, core.pipeline.processar,
    core.impressao.montar_para_impressao), sem janela, e anota a memória do
    processo e dos processos filhos (o servidor de páginas) a cada 0,2 s.

USO (uma medida por processo, para cada uma começar do zero):
    python relatorios/memoria-pdf/medir_memoria.py LIVRO.pdf FOLHAS MODO SAIDA.json
    MODO: processar | cadernos | livreto
    - processar: o "Confirmar e processar" de sempre (livro novo, de fábrica).
    - cadernos:  o mesmo, com "Montar cadernos" ligado.
    - livreto:   processa e depois monta o livreto ("Montar para imprimir",
                 opções de fábrica) a partir do PDF pronto.

    O livro é COPIADO (as FOLHAS primeiras páginas) para a pasta temporária do
    sistema; o acervo só é lido. A pasta de dados do programa é uma pasta de
    teste (pasta_de_dados_dos_scripts.isolar_pasta_de_dados), nunca a do
    Samuel. Uma página por vez (1 trabalhador), para comparar só o tamanho do
    livro.

SEGURO MUDAR: o intervalo das amostras, o caminho da pasta temporária.
ARRISCADO: medir com várias páginas ao mesmo tempo (o pico passa a depender
    da memória livre na hora, não só do livro).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))


class Amostrador:
    """Anota a memória (bytes "privados" = o que o processo reservou para si,
    e RSS = o que está de fato na memória física) do processo e dos filhos,
    numa linha de fundo, a cada `intervalo` segundos. `marcar(fase)` anota em
    que parte do trabalho cada amostra caiu."""

    def __init__(self, intervalo: float = 0.2) -> None:
        import psutil

        self._psutil = psutil
        self._eu = psutil.Process(os.getpid())
        self.intervalo = intervalo
        self.fase = "começo"
        self.amostras: list[tuple[float, str, float, float, float, float]] = []
        self._parar = threading.Event()
        self._linha = threading.Thread(target=self._rodar, daemon=True)
        self._t0 = time.perf_counter()

    def marcar(self, fase: str) -> None:
        self.fase = fase

    def _medir(self) -> tuple[float, float, float]:
        mb = 1024 * 1024
        info = self._eu.memory_info()
        privado = getattr(info, "private", info.rss) / mb
        rss = info.rss / mb
        livre = _memoria_livre_mb()
        filhos = 0.0
        for filho in self._eu.children(recursive=True):
            try:
                fi = filho.memory_info()
                filhos += getattr(fi, "private", fi.rss) / mb
            except Exception:  # noqa: BLE001 - filho que acabou de sair
                pass
        return privado, rss, filhos, livre

    def _rodar(self) -> None:
        while not self._parar.is_set():
            try:
                privado, rss, filhos, livre = self._medir()
                self.amostras.append((time.perf_counter() - self._t0, self.fase,
                                      privado, rss, filhos, livre))
            except Exception:  # noqa: BLE001
                pass
            self._parar.wait(self.intervalo)

    def __enter__(self) -> "Amostrador":
        self._linha.start()
        return self

    def __exit__(self, *_exc) -> None:
        self._parar.set()
        self._linha.join()

    def pico(self, fase: str | None = None) -> dict:
        escolhidas = [a for a in self.amostras if fase is None or a[1] == fase]
        if not escolhidas:
            return {}
        return {"privado_mb": round(max(a[2] for a in escolhidas)),
                "rss_mb": round(max(a[3] for a in escolhidas)),
                "filhos_mb": round(max(a[4] for a in escolhidas)),
                "privado_mais_filhos_mb": round(max(a[2] + a[4] for a in escolhidas)),
                "menor_livre_no_windows_mb": round(min(a[5] for a in escolhidas))}


def _memoria_livre_mb() -> float:
    """Memoria livre do Windows inteiro (para mostrar o estado da maquina)."""
    import psutil

    return psutil.virtual_memory().available / 1024 / 1024


def copiar_folhas(origem: Path, destino: Path, folhas: int) -> int:
    """As `folhas` primeiras páginas do livro, copiadas sem rasterizar (como o
    teste_velocidade.preparar_livro). O original só é lido."""
    import fitz

    with fitz.open(origem) as fonte:
        ultima = min(folhas, fonte.page_count) - 1
        novo = fitz.open()
        try:
            novo.insert_pdf(fonte, from_page=0, to_page=ultima)
            novo.save(destino)
        finally:
            novo.close()
        return ultima + 1


def main() -> int:
    livro, folhas, modo, saida_json = Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3], Path(sys.argv[4])

    from pasta_de_dados_dos_scripts import isolar_pasta_de_dados

    pasta_tmp = Path(tempfile.mkdtemp(prefix="medir_memoria_"))
    isolar_pasta_de_dados("medir_memoria", raiz=pasta_tmp / "dados")

    from core import nucleos
    from core import pdf_io
    from core.pipeline import analisar_projeto, processar
    from modelos import Projeto

    nucleos.quantos_trabalhadores = lambda *a, **k: 1   # uma página por vez (ver o docstring)

    entrada = pasta_tmp / "livro.pdf"
    paginas = copiar_folhas(livro, entrada, folhas)

    with Amostrador() as amostrador:
        # a hora em que o EscritorPDF grava o arquivo (o doc.save do fim)
        fechar_de_antes = pdf_io.EscritorPDF.fechar

        def fechar_marcando(self):
            amostrador.marcar("gravar o PDF")
            return fechar_de_antes(self)

        pdf_io.EscritorPDF.fechar = fechar_marcando

        amostrador.marcar("analisar")
        t0 = time.perf_counter()
        projeto = analisar_projeto(Projeto(caminho_entrada=str(entrada), nome="livro"))
        t_analise = time.perf_counter() - t0

        projeto.montar_cadernos = modo == "cadernos"
        projeto.caminho_saida = str(pasta_tmp / "saida.pdf")
        amostrador.marcar("processar as páginas")

        andamento = {"pagina": 0}

        def progresso(feito, total, texto):
            andamento["pagina"] = feito
            if "cadernos" in texto.lower():
                amostrador.marcar("montar os cadernos")

        erro = None
        caminho = None
        t_processar = t_livreto = None
        t0 = time.perf_counter()
        try:
            caminho = processar(projeto, progresso=progresso)
            t_processar = time.perf_counter() - t0
            amostrador.marcar("pronto")
            if modo == "livreto":
                from core.impressao import montar_para_impressao

                amostrador.marcar("montar o livreto")
                t0 = time.perf_counter()
                montar_para_impressao(caminho, pasta_tmp / "livreto.pdf")
                t_livreto = time.perf_counter() - t0
                amostrador.marcar("pronto")
        except BaseException as exc:  # noqa: BLE001 - a medida guarda o que aconteceu
            erro = f"{type(exc).__name__}: {exc} (na fase '{amostrador.fase}', página {andamento['pagina']})"
            amostrador.marcar("caiu")
        time.sleep(0.5)

    import fitz

    tamanho_mb = Path(caminho).stat().st_size / 1024 / 1024 if caminho else None
    paginas_saida = None
    if caminho:
        with fitz.open(caminho) as pronto:
            paginas_saida = pronto.page_count

    fases = sorted({a[1] for a in amostrador.amostras}, key=lambda f: [a[1] for a in amostrador.amostras].index(f))
    resultado = {
        "livro": livro.name, "folhas": paginas, "modo": modo,
        "paginas_no_pdf": paginas_saida, "pdf_mb": None if tamanho_mb is None else round(tamanho_mb, 1),
        "erro": erro,
        "segundos": {"analisar": round(t_analise, 1),
                     "processar": None if t_processar is None else round(t_processar, 1),
                     "livreto": None if t_livreto is None else round(t_livreto, 1)},
        "pico_total": amostrador.pico(),
        "pico_por_fase": {f: amostrador.pico(f) for f in fases},
        "amostras": [[round(t, 2), f, round(p), round(r), round(c), round(lv)]
                     for t, f, p, r, c, lv in amostrador.amostras],
    }
    saida_json.parent.mkdir(parents=True, exist_ok=True)
    saida_json.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in resultado.items() if k != "amostras"}, ensure_ascii=False))

    # limpa só o que este script criou (livro copiado e PDFs de saída)
    for nome in ("livro.pdf", "saida.pdf", "livreto.pdf"):
        (pasta_tmp / nome).unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
