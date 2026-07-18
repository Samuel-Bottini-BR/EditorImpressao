"""Bateria completa do acervo: ficha de cada livro, imagens e relatório geral.

Uso:
    python teste_bateria.py "C:\\...\\LIVROS PARA FAZER TESTE"

Não altera nenhum PDF de origem. Grava:
    <pasta>/<nome do livro>.txt          ficha de cada livro
    <pasta>/RELATORIO_GERAL.txt          tabela e ranking
    <pasta>/resultados/<livro>/          comparativos e ampliações
    <pasta>/para_comparar/               páginas difíceis, para o CamScanner
"""

from __future__ import annotations

import ctypes
import gc
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from core import analise
from core.cadernos import contar_cadernos, montar_ordem
from core.dividir import detectar_lombada
from core.endireitar import detectar_angulo
from core.filtros import (
    MAGICO_PRO,
    MELHORAR,
    ORIGINAL,
    PRETO_E_BRANCO,
    aplicar_filtro,
)
from core.pdf_io import (
    EscritorPDF,
    abrir_pdf,
    dpi_real_da_pagina,
    limitar_altura,
    pagina_para_array,
)
from core.recortar import aplicar_recorte, detectar_bordas

DPI_ANALISE = 110
DPI_IMAGEM = 300
PAGINAS_PROCESSADAS = 12      # amostra para medir tempo e qualidade de verdade


# ---------------------------------------------------------------------------
# memoria
# ---------------------------------------------------------------------------

_PICO = 0.0


def memoria_mb() -> tuple[float, float]:
    """(memória agora, maior valor já visto) em MB.

    Usa o psutil. A primeira versão chamava GetProcessMemoryInfo por ctypes e
    devolvia 0 em silêncio - o handle era truncado em 64 bits. Numero que vai
    para relatório não pode vir de uma chamada que falha calada.
    """
    global _PICO
    try:
        import psutil

        agora = psutil.Process().memory_info().rss / 1024 / 1024
        _PICO = max(_PICO, agora)
        return agora, _PICO
    except Exception:  # noqa: BLE001
        return 0.0, _PICO


def zerar_pico() -> None:
    """Recomeça a contagem do pico. Chamado a cada livro."""
    global _PICO
    _PICO = 0.0


# ---------------------------------------------------------------------------

@dataclass
class Pagina:
    numero: int
    paisagem: bool
    dpi: float
    tem_cor: bool
    saturacao: float
    angulo: float
    confianca_angulo: float
    corte: float
    confianca_corte: float
    amarelado: float
    verso: float
    tinta: float
    alertas: list[str] = field(default_factory=list)

    @property
    def em_branco(self) -> bool:
        return self.tinta < analise.FRACAO_TINTA_BRANCA


def _amarelado(img: np.ndarray) -> float:
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    luz, b = lab[:, :, 0], lab[:, :, 2].astype(np.float32)
    papel = luz >= np.percentile(luz, 75)
    return float(b[papel].mean() - 128.0) if papel.sum() else 0.0


def _verso(img: np.ndarray) -> float:
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    nivel = float(np.percentile(cinza, 80))
    if nivel < 10:
        return 0.0
    return float(((cinza > nivel * 0.62) & (cinza < nivel * 0.88)).mean())


def analisar_livro(caminho: Path, progresso=True) -> tuple[list[Pagina], float]:
    doc = abrir_pdf(caminho)
    paginas: list[Pagina] = []
    t0 = time.perf_counter()
    try:
        total = doc.page_count
        for i in range(total):
            img = pagina_para_array(doc, i, dpi=DPI_ANALISE)
            lombada = detectar_lombada(img)
            inclinacao = detectar_angulo(img)
            tem_cor, sat = analise.detectar_cor(img)

            paginas.append(Pagina(
                numero=i + 1,
                paisagem=lombada.e_paisagem,
                dpi=dpi_real_da_pagina(doc, i),
                tem_cor=tem_cor, saturacao=sat,
                angulo=inclinacao.angulo,
                confianca_angulo=inclinacao.confianca,
                corte=lombada.posicao,
                confianca_corte=lombada.confianca,
                amarelado=_amarelado(img),
                verso=_verso(img),
                tinta=analise.fracao_de_tinta(img),
            ))
            del img
            if progresso and (i + 1) % 100 == 0:
                agora, pico = memoria_mb()
                print(f"      {i + 1}/{total} páginas   memória {agora:.0f} MB "
                      f"(pico {pico:.0f})", flush=True)
    finally:
        doc.close()
    return paginas, time.perf_counter() - t0


def processar_amostra(caminho: Path, paginas: list[Pagina], destino: Path) -> dict:
    """Processa algumas páginas de verdade, para medir tempo e tamanho."""
    uteis = [p for p in paginas if not p.em_branco] or paginas
    passo = max(1, len(uteis) // PAGINAS_PROCESSADAS)
    escolhidas = uteis[::passo][:PAGINAS_PROCESSADAS]

    doc = abrir_pdf(caminho)
    saida = destino / "amostra_processada.pdf"
    bytes_entrada = 0
    t0 = time.perf_counter()
    try:
        with EscritorPDF(saida) as escritor:
            for p in escolhidas:
                img = pagina_para_array(doc, p.numero - 1, dpi=DPI_IMAGEM)
                bytes_entrada += img.nbytes
                img = aplicar_recorte(img, detectar_bordas(img))
                angulo = detectar_angulo(img).angulo
                if angulo:
                    from core.endireitar import rotacionar
                    img = rotacionar(img, angulo)
                filtro = MELHORAR if p.tem_cor else PRETO_E_BRANCO
                img, mono = aplicar_filtro(img, filtro)
                escritor.escrever_imagem(img, dpi=DPI_IMAGEM, monocromatico=mono)
                del img
    finally:
        doc.close()

    segundos = time.perf_counter() - t0
    return {
        "paginas": len(escolhidas),
        "segundos": segundos,
        "s_por_pagina": segundos / max(1, len(escolhidas)),
        "mb_saida": saida.stat().st_size / 1024 / 1024 if saida.exists() else 0.0,
    }


# ---------------------------------------------------------------------------
# imagens
# ---------------------------------------------------------------------------

def gravar_imagem(caminho: Path, img: np.ndarray) -> bool:
    """Grava PNG mesmo quando o caminho tem acento.

    O cv2.imwrite falha EM SILENCIO em caminho com caractere fora do ASCII no
    Windows - devolve False e ninguem percebe. Foi assim que as imagens do
    "Livro de Horas - Luís XIV" simplesmente não apareceram. Codificamos em
    memória e gravamos pelo Python, que lida com o caminho direito.
    """
    ok, buffer = cv2.imencode(".png", img)
    if not ok:
        return False
    caminho.write_bytes(buffer.tobytes())
    return True


def _rotular(img: np.ndarray, texto: str) -> np.ndarray:
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    faixa = np.full((50, img.shape[1], 3), 255, dtype=np.uint8)
    cv2.putText(faixa, texto, (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                (0, 0, 0), 2, cv2.LINE_AA)
    return np.vstack([faixa, img])


def _juntar(paineis: list[np.ndarray]) -> np.ndarray:
    altura = max(p.shape[0] for p in paineis)
    partes = []
    for p in paineis:
        if p.shape[0] < altura:
            p = np.vstack([p, np.full((altura - p.shape[0], p.shape[1], 3), 255,
                                      dtype=np.uint8)])
        partes.append(p)
        partes.append(np.full((altura, 8, 3), 190, dtype=np.uint8))
    return np.hstack(partes[:-1])


def quatro_filtros(bruta: np.ndarray, altura: int = 900) -> np.ndarray:
    paineis = []
    for filtro, nome in ((ORIGINAL, "Original"), (PRETO_E_BRANCO, "Preto e branco"),
                         (MELHORAR, "Melhorar"), (MAGICO_PRO, "Magico pro")):
        img, _ = aplicar_filtro(bruta, filtro)
        paineis.append(_rotular(limitar_altura(img, altura), nome))
    return _juntar(paineis)


def recorte_central(img: np.ndarray, fx=0.20, fy=0.35, largura=900, altura=340):
    h, w = img.shape[:2]
    y, x = int(h * fy), int(w * fx)
    return img[y:min(h, y + altura), x:min(w, x + largura)]


def gerar_imagens(caminho: Path, paginas: list[Pagina], destino: Path) -> list[str]:
    """Comparativos das páginas mais difíceis. Devolve os nomes gerados."""
    destino.mkdir(parents=True, exist_ok=True)
    uteis = [p for p in paginas if not p.em_branco] or paginas
    gerados: list[str] = []

    escolhas = {
        "amarelada": max(uteis, key=lambda p: p.amarelado),
        "bleed_through": max(uteis, key=lambda p: p.verso),
        "torta": max(uteis, key=lambda p: abs(p.angulo)),
    }
    coloridas = [p for p in uteis if p.tem_cor]
    if coloridas:
        escolhas["colorida"] = max(coloridas, key=lambda p: p.saturacao)

    doc = abrir_pdf(caminho)
    try:
        for motivo, p in escolhas.items():
            bruta = pagina_para_array(doc, p.numero - 1, dpi=DPI_IMAGEM)

            nome = f"{motivo}_pag{p.numero:04d}.png"
            gravar_imagem(destino / nome, quatro_filtros(bruta))
            gerados.append(nome)

            recorte = recorte_central(bruta)
            paineis = []
            for filtro, rotulo in ((ORIGINAL, "Original"),
                                   (PRETO_E_BRANCO, "Preto e branco"),
                                   (MELHORAR, "Melhorar")):
                img, _ = aplicar_filtro(recorte, filtro)
                paineis.append(_rotular(img, rotulo))
            nome_zoom = f"{motivo}_pag{p.numero:04d}_AMPLIADO.png"
            gravar_imagem(destino / nome_zoom, _juntar(paineis))
            gerados.append(nome_zoom)
            del bruta
    finally:
        doc.close()
    return gerados


# ---------------------------------------------------------------------------
# ficha
# ---------------------------------------------------------------------------

def escrever_ficha(caminho: Path, paginas: list[Pagina], tempo_analise: float,
                   amostra: dict, imagens: list[str], destino_img: Path,
                   pico_mb: float) -> str:
    total = len(paginas)
    paisagens = [p for p in paginas if p.paisagem]
    coloridas = [p for p in paginas if p.tem_cor]
    tortas = [p for p in paginas if abs(p.angulo) >= 0.3]
    muito_tortas = [p for p in paginas if abs(p.angulo) >= 3.0]
    brancas = [p for p in paginas if p.em_branco]
    incertas = [p for p in paisagens if p.confianca_corte < 0.5]

    dpi = float(np.median([p.dpi for p in paginas]))
    amarelado = float(np.median([p.amarelado for p in paginas]))
    verso = float(np.median([p.verso for p in paginas]))
    mb = caminho.stat().st_size / 1024 / 1024

    def lista(itens, quantos=12):
        nums = [str(p.numero) for p in itens[:quantos]]
        resto = f" (+{len(itens) - quantos})" if len(itens) > quantos else ""
        return ", ".join(nums) + resto if nums else "nenhuma"

    estado = ("bem amarelado" if amarelado >= 14 else
              "amarelado" if amarelado >= 8 else
              "levemente amarelado" if amarelado >= 3 else "claro")
    if verso > 0.18:
        estado += ", papel translúcido (texto do verso aparece muito)"
    elif verso > 0.12:
        estado += ", texto do verso aparece"

    qualidade = ("boa" if dpi >= 250 else "razoável" if dpi >= 150 else "BAIXA")

    linhas = [
        f"ARQUIVO: {caminho.name}",
        f"Testado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        "O QUE ESTE ARQUIVO É",
        f"- {total} páginas · {mb:.0f} MB · ~{dpi:.0f} DPI (qualidade {qualidade})",
        f"- folhas duplas: {'SIM' if len(paisagens) > total * 0.6 else 'não'}"
        f"  ({len(paisagens)} de {total} em paisagem)",
        f"- cor: {len(coloridas)} de {total} páginas com tinta colorida "
        f"({100 * len(coloridas) / total:.0f}%)",
        f"- estado do papel: {estado} (amarelado b*={amarelado:+.1f}, "
        f"verso {verso * 100:.1f}%)",
        "",
        "O QUE O PROGRAMA DETECTOU",
        f"- páginas com cor: {len(coloridas)}  ({lista(coloridas)})",
        f"- páginas tortas: {len(tortas)}"
        + (f"  (maior ângulo: {max(abs(p.angulo) for p in tortas):.1f}°)" if tortas else ""),
        f"- muito tortas (acima de 3°): {len(muito_tortas)}  ({lista(muito_tortas)})",
        f"- páginas em branco: {len(brancas)}  ({lista(brancas)})",
        f"- lombada incerta: {len(incertas)}  ({lista(incertas)})",
        "",
        "DESEMPENHO",
        f"- análise das {total} páginas: {tempo_analise / 60:.1f} min "
        f"({tempo_analise / total:.2f} s por página)",
        f"- processamento (amostra de {amostra['paginas']} páginas a {DPI_IMAGEM} DPI): "
        f"{amostra['s_por_pagina']:.2f} s por página",
        f"- projeção para o livro inteiro: "
        f"{total * amostra['s_por_pagina'] / 60:.0f} min",
        f"- PICO DE MEMÓRIA do processo: {pico_mb:.0f} MB",
        f"- amostra processada: {amostra['mb_saida']:.1f} MB para "
        f"{amostra['paginas']} páginas",
        "",
        "OS 4 CASOS DO KAIQUE NESTE ARQUIVO",
    ]

    # caso 1
    if amarelado >= 8 and len(coloridas) < total * 0.5:
        linhas.append("1. amarelado com texto preto: RESOLVIDO "
                      "(ver imagem 'amarelada' - o Preto e branco tira o fundo)")
    elif amarelado < 8:
        linhas.append("1. amarelado com texto preto: não se aplica "
                      "(este papel não está amarelado)")
    else:
        linhas.append("1. amarelado com texto preto: ver imagem 'amarelada' "
                      "(livro majoritariamente colorido)")

    # caso 2
    if coloridas:
        linhas.append("2. amarelado com imagem colorida: ver imagem 'colorida' - "
                      f"{len(coloridas)} páginas detectadas, Melhorar preserva a cor")
    else:
        linhas.append("2. amarelado com imagem colorida: não se aplica "
                      "(nenhuma página colorida)")

    # caso 3
    if tortas:
        linhas.append(f"3. páginas tortas: {len(tortas)} detectadas, "
                      f"maior {max(abs(p.angulo) for p in tortas):.1f}° - "
                      "ver imagem 'torta'")
    else:
        linhas.append("3. páginas tortas: nenhuma acima de 0,3°")

    # caso 4
    pior = max(paginas, key=lambda p: p.verso)
    if verso > 0.12:
        linhas.append(f"4. bleed-through: ver 'bleed_through_pag{pior.numero:04d}"
                      "_AMPLIADO.png' - JULGAR NA IMAGEM se o texto do verso "
                      "ainda aparece depois do Preto e branco")
    else:
        linhas.append("4. bleed-through: pouco presente neste livro "
                      f"({verso * 100:.1f}%)")

    linhas += [
        "",
        "IMAGENS GERADAS",
        f"- pasta: {destino_img.name}/",
    ] + [f"    {n}" for n in imagens]

    texto = "\n".join(linhas) + "\n"
    # utf-8-sig: com a marca no inicio, o Bloco de Notas do Windows reconhece
    # os acentos. Sem ela sai "RELATORIO" com o til quebrado.
    (caminho.parent / f"{caminho.stem}.txt").write_text(texto, encoding="utf-8-sig")
    return texto


def main(pasta: str) -> int:
    raiz = Path(pasta)
    arquivos = sorted(raiz.glob("*.pdf"))
    if not arquivos:
        print(f"nenhum PDF em {raiz}")
        return 1

    resultados = []
    for arquivo in arquivos:
        print(f"\n=== {arquivo.name} ===", flush=True)
        gc.collect()
        zerar_pico()
        antes, _ = memoria_mb()

        paginas, tempo = analisar_livro(arquivo)
        destino = raiz / "resultados" / arquivo.stem[:40]
        destino.mkdir(parents=True, exist_ok=True)

        amostra = processar_amostra(arquivo, paginas, destino)
        imagens = gerar_imagens(arquivo, paginas, destino)
        _, pico = memoria_mb()

        escrever_ficha(arquivo, paginas, tempo, amostra, imagens, destino, pico)
        print(f"    ficha: {arquivo.stem}.txt   pico de memória {pico:.0f} MB",
              flush=True)

        resultados.append({
            "nome": arquivo.name, "paginas": len(paginas),
            "mb": arquivo.stat().st_size / 1024 / 1024,
            "dpi": float(np.median([p.dpi for p in paginas])),
            "cor": sum(1 for p in paginas if p.tem_cor),
            "tortas": sum(1 for p in paginas if abs(p.angulo) >= 0.3),
            "verso": float(np.median([p.verso for p in paginas])),
            "amarelado": float(np.median([p.amarelado for p in paginas])),
            "s_pagina": amostra["s_por_pagina"],
            "pico": pico,
        })
        gc.collect()

    _relatorio_geral(raiz, resultados)
    return 0


def _relatorio_geral(raiz: Path, resultados: list[dict]) -> None:
    linhas = [
        "RELATÓRIO GERAL - acervo do instituto",
        f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        f"{'livro':<42} {'pág':>5} {'MB':>5} {'DPI':>5} {'cor':>6} {'torta':>6} "
        f"{'amarelo':>8} {'verso':>7} {'s/pág':>6} {'pico MB':>8}",
        "-" * 108,
    ]
    for r in resultados:
        linhas.append(
            f"{r['nome'][:40]:<42} {r['paginas']:>5} {r['mb']:>5.0f} {r['dpi']:>5.0f} "
            f"{100 * r['cor'] / r['paginas']:>5.0f}% "
            f"{100 * r['tortas'] / r['paginas']:>5.0f}% "
            f"{r['amarelado']:>+8.1f} {r['verso'] * 100:>6.1f}% "
            f"{r['s_pagina']:>6.2f} {r['pico']:>8.0f}"
        )

    total_paginas = sum(r["paginas"] for r in resultados)
    tempo_total = sum(r["paginas"] * r["s_pagina"] for r in resultados)
    linhas += [
        "-" * 108,
        f"{len(resultados)} livros · {total_paginas} páginas",
        f"Processar o acervo inteiro a {DPI_IMAGEM} DPI levaria "
        f"~{tempo_total / 3600:.1f} horas",
        f"Maior pico de memória observado: {max(r['pico'] for r in resultados):.0f} MB",
        "",
    ]
    (raiz / "RELATORIO_GERAL.txt").write_text("\n".join(linhas) + "\n",
                                              encoding="utf-8-sig")
    print("\n".join(linhas))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
