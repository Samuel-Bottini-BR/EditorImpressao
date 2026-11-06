"""Mede a memória ao processar UM livro do acervo, com o código novo ou o antigo (04/11/2026).

PARA QUE SERVE
    Pedido do Samuel (04/11/2026): "o teste foi feito com um pdf só?" -> medir o
    conserto da falta de memória nos 9 livros do acervo, não só no Rhetorica.
    É o MESMO caminho do relatorios/memoria-pdf/medir_memoria.py (modo
    "processar"): copia as FOLHAS primeiras páginas do livro (sem rasterizar),
    analisar_projeto + processar de fábrica, uma página por vez (1 trabalhador),
    e anota a memória do processo e dos filhos a cada 0,2 s. Diferenças, só de
    anotação (nada muda no programa):
    - escolhe de qual cópia do código vem o programa (--raiz), para rodar o
      código antigo (antes do conserto) e o novo com o mesmo script;
    - anota em cada amostra a página que está sendo feita, para comparar o pico
      do começo do livro com o do fim (o pico não pode crescer com o livro);
    - guarda o PDF de saída (--guardar), para comparar o antigo com o novo;
    - grava o andamento num .log ao lado do .json, para acompanhar.

USO (um livro por processo, para cada medida começar do zero):
    python medir_livro.py --raiz CODIGO --livro LIVRO.pdf --folhas N
                          --pasta PASTA_DE_TRABALHO --saida SAIDA.json [--guardar]
    --folhas 0 = o livro inteiro.

    O acervo só é lido (fitz.open + insert_pdf numa cópia na PASTA).
    A pasta de dados do programa é uma pasta de teste (isolar_pasta_de_dados).

SEGURO MUDAR: o intervalo das amostras. Nada aqui mexe no programa.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from pathlib import Path


class Amostrador:
    """Memória (bytes privados e RSS) do processo e dos filhos, a cada 0,2 s,
    com a fase e a página da vez. Igual ao do medir_memoria.py, mais a página."""

    def __init__(self, intervalo: float = 0.2) -> None:
        import psutil

        self._psutil = psutil
        self._eu = psutil.Process(os.getpid())
        self.intervalo = intervalo
        self.fase = "começo"
        self.pagina = 0
        self.amostras: list[tuple] = []
        self._parar = threading.Event()
        self._linha = threading.Thread(target=self._rodar, daemon=True)
        self._t0 = time.perf_counter()

    def marcar(self, fase: str) -> None:
        self.fase = fase

    def _medir(self):
        mb = 1024 * 1024
        info = self._eu.memory_info()
        privado = getattr(info, "private", info.rss) / mb
        rss = info.rss / mb
        livre = self._psutil.virtual_memory().available / mb
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
                p, r, f, lv = self._medir()
                self.amostras.append((time.perf_counter() - self._t0, self.fase, self.pagina, p, r, f, lv))
            except Exception:  # noqa: BLE001
                pass
            self._parar.wait(self.intervalo)

    def __enter__(self):
        self._linha.start()
        return self

    def __exit__(self, *_exc):
        self._parar.set()
        self._linha.join()


def _pico(amostras) -> dict:
    if not amostras:
        return {}
    return {"privado_mb": round(max(a[3] for a in amostras)),
            "rss_mb": round(max(a[4] for a in amostras)),
            "filhos_mb": round(max(a[5] for a in amostras)),
            "privado_mais_filhos_mb": round(max(a[3] + a[5] for a in amostras)),
            "menor_livre_no_windows_mb": round(min(a[6] for a in amostras))}


def copiar_folhas(origem: Path, destino: Path, folhas: int) -> int:
    """As `folhas` primeiras páginas (0 = todas), sem rasterizar, como o
    medir_memoria.copiar_folhas. O original só é lido."""
    import fitz

    with fitz.open(origem) as fonte:
        n = fonte.page_count if folhas <= 0 else min(folhas, fonte.page_count)
        novo = fitz.open()
        try:
            novo.insert_pdf(fonte, from_page=0, to_page=n - 1)
            novo.save(destino)
        finally:
            novo.close()
        return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", required=True, type=Path)
    ap.add_argument("--livro", required=True, type=Path)
    ap.add_argument("--folhas", type=int, default=0)
    ap.add_argument("--pasta", required=True, type=Path)
    ap.add_argument("--saida", required=True, type=Path)
    ap.add_argument("--guardar", action="store_true")
    a = ap.parse_args()

    raiz = a.raiz.resolve()
    sys.path.insert(0, str(raiz))
    pasta = a.pasta.resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    log = a.saida.with_suffix(".log")
    log.parent.mkdir(parents=True, exist_ok=True)

    def anotar(texto: str) -> None:
        with log.open("a", encoding="utf-8") as f:
            f.write(time.strftime("%H:%M:%S ") + texto + "\n")

    from pasta_de_dados_dos_scripts import isolar_pasta_de_dados

    isolar_pasta_de_dados("medir_9_livros", raiz=pasta / "dados")

    from core import nucleos
    from core import pdf_io
    from core.pipeline import analisar_projeto, processar
    from modelos import Projeto

    import core.pipeline as _pl
    assert Path(_pl.__file__).resolve().is_relative_to(raiz), _pl.__file__
    anotar(f"código de {raiz} (core.pipeline em {_pl.__file__}); "
           f"tem PDFQueVaiParaODisco: {hasattr(pdf_io, 'PDFQueVaiParaODisco')}")

    nucleos.quantos_trabalhadores = lambda *x, **k: 1   # uma página por vez, como o medir_memoria.py

    entrada = pasta / "livro.pdf"
    folhas = copiar_folhas(a.livro, entrada, a.folhas)
    anotar(f"livro {a.livro.name}: {folhas} folhas copiadas")

    t_inicio = time.time()
    with Amostrador() as amostrador:
        fechar_de_antes = pdf_io.EscritorPDF.fechar

        def fechar_marcando(self):
            amostrador.marcar("gravar o PDF")
            anotar("gravando o PDF")
            return fechar_de_antes(self)

        pdf_io.EscritorPDF.fechar = fechar_marcando

        amostrador.marcar("analisar")
        t0 = time.perf_counter()
        projeto = analisar_projeto(Projeto(caminho_entrada=str(entrada), nome="livro"))
        t_analise = time.perf_counter() - t0
        esperadas = len(projeto.paginas_ativas)
        anotar(f"análise pronta em {t_analise:.0f} s; páginas esperadas no PDF: {esperadas}")

        projeto.montar_cadernos = False
        projeto.caminho_saida = str(pasta / "saida.pdf")
        amostrador.marcar("processar as páginas")
        ultimo = {"t": 0.0}

        def progresso(feito, total, texto):
            amostrador.pagina = feito
            agora = time.perf_counter()
            if agora - ultimo["t"] > 30:
                ultimo["t"] = agora
                anotar(f"{feito}/{total} {texto}")

        erro = None
        caminho = None
        t_processar = None
        t0 = time.perf_counter()
        try:
            caminho = processar(projeto, progresso=progresso)
            t_processar = time.perf_counter() - t0
            amostrador.marcar("pronto")
        except BaseException as exc:  # noqa: BLE001 - a medida guarda o que aconteceu
            erro = f"{type(exc).__name__}: {exc} (na fase '{amostrador.fase}', página {amostrador.pagina})"
            amostrador.marcar("caiu")
            anotar("CAIU: " + erro)
        time.sleep(0.5)

    import fitz

    tamanho_mb = Path(caminho).stat().st_size / 1024 / 1024 if caminho else None
    paginas_saida = None
    if caminho:
        with fitz.open(caminho) as pronto:
            paginas_saida = pronto.page_count

    am = amostrador.amostras
    fases = list(dict.fromkeys(x[1] for x in am))
    # Pico no começo e no fim do livro: a primeira e a última quarta parte das
    # páginas feitas (só a fase "processar as páginas").
    proc = [x for x in am if x[1] == "processar as páginas" and x[2] > 0]
    quartos = {}
    if proc and esperadas:
        q = max(1, esperadas // 4)
        for nome, lo, hi in (("1o_quarto", 1, q), ("2o_quarto", q + 1, 2 * q),
                             ("3o_quarto", 2 * q + 1, 3 * q), ("4o_quarto", 3 * q + 1, esperadas)):
            quartos[nome] = {"paginas": [lo, hi], **_pico([x for x in proc if lo <= x[2] <= hi])}

    resultado = {
        "livro": a.livro.name, "folhas": folhas, "folhas_do_livro_inteiro": None,
        "codigo": str(raiz), "modo": "processar",
        "paginas_esperadas": esperadas, "paginas_no_pdf": paginas_saida,
        "pdf_mb": None if tamanho_mb is None else round(tamanho_mb, 1),
        "erro": erro, "comecou_em": time.strftime("%d/%m/%Y %H:%M", time.localtime(t_inicio)),
        "segundos": {"analisar": round(t_analise, 1),
                     "processar": None if t_processar is None else round(t_processar, 1)},
        "pico_total": _pico(am),
        "pico_por_fase": {f: _pico([x for x in am if x[1] == f]) for f in fases},
        "pico_por_quarto_do_livro": quartos,
        "amostras": [[round(t, 1), f, pg, round(p), round(r), round(c), round(lv)]
                     for t, f, pg, p, r, c, lv in am[::5]],   # 1 a cada segundo (o pico vem de todas)
    }
    with fitz.open(a.livro) as fonte:
        resultado["folhas_do_livro_inteiro"] = fonte.page_count
    a.saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in resultado.items() if k != "amostras"}, ensure_ascii=False))
    anotar("fim: " + json.dumps({k: resultado[k] for k in ("paginas_esperadas", "paginas_no_pdf", "pdf_mb",
                                                          "erro", "segundos", "pico_total")}, ensure_ascii=False))

    # limpa só o que este script criou; o PDF fica se --guardar
    entrada.unlink(missing_ok=True)
    if caminho and not a.guardar:
        Path(caminho).unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
