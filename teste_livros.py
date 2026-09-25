"""Bateria de testes em livros REAIS.

Uso:
    python teste_livros.py "livro.pdf" [outro.pdf ...]
    python teste_livros.py pdfs_teste          (uma pasta inteira)

Para cada arquivo diz:
  - que tipo de material é (folha dupla ou simples, cor, qualidade do scan)
  - o que o programa detectou
  - as páginas que ele mesmo marcou como duvidosas

E gera, em saida_teste/livros/, o comparativo dos quatro filtros das páginas
mais difíceis: a mais amarelada, a mais torta e a com mais marca do verso.
São essas que revelam se o filtro presta - página limpa qualquer receita
resolve.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from core import analise
from core.dividir import detectar_lombada
from core.endireitar import detectar_angulo
from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO, aplicar_filtro
from core.pdf_io import (
    abrir_pdf,
    dpi_real_da_pagina,
    info_paginas,
    limitar_altura,
    pagina_para_array,
)
from core.recortar import detectar_bordas

SAIDA = Path("saida_teste/livros")
DPI_ANALISE = 150
DPI_COMPARATIVO = 300


@dataclass
class Medidas:
    """O que medimos de uma página, para escolher as difíceis."""

    numero: int
    paisagem: bool
    largura_px: int
    altura_px: int
    dpi: float
    amarelado: float      # o quanto o papel puxa para o amarelo
    tem_cor: bool
    saturacao: float
    angulo: float
    confianca_angulo: float
    corte: float
    confianca_corte: float
    verso: float          # marca do texto do verso transparecendo
    tinta: float
    em_branco: bool


def _nivel_de_amarelado(img: np.ndarray) -> float:
    """Quanto o papel puxa para o amarelo, de 0 (branco) para cima.

    Medido no canal b* do LAB, que é exatamente o eixo azul-amarelo, e só nos
    pixels claros - que são o papel. A tinta não entra na conta.
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    luz, b = lab[:, :, 0], lab[:, :, 2].astype(np.float32)
    papel = luz >= np.percentile(luz, 75)
    if papel.sum() < 100:
        return 0.0
    return float(b[papel].mean() - 128.0)   # 128 = neutro


def _marca_do_verso(img: np.ndarray) -> float:
    """Fração de pixels cinza-claros que parecem texto do outro lado da folha.

    O texto da frente é bem escuro; a marca do verso fica num cinza
    intermediário. Contamos o que cai nessa faixa do meio.
    """
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    papel = float(np.percentile(cinza, 80))
    if papel < 10:
        return 0.0
    faixa = (cinza > papel * 0.62) & (cinza < papel * 0.88)
    return float(faixa.mean())


def medir(img: np.ndarray, numero: int, dpi_real: float) -> Medidas:
    """Roda todas as deteccoes numa pagina e devolve o pacote de Medidas dela."""
    altura, largura = img.shape[:2]
    lombada = detectar_lombada(img)
    inclinacao = detectar_angulo(img)
    tem_cor, saturacao = analise.detectar_cor(img)
    tinta = analise.fracao_de_tinta(img)

    return Medidas(
        numero=numero,
        paisagem=lombada.e_paisagem,
        largura_px=largura,
        altura_px=altura,
        dpi=dpi_real,
        amarelado=_nivel_de_amarelado(img),
        tem_cor=tem_cor,
        saturacao=saturacao,
        angulo=inclinacao.angulo,
        confianca_angulo=inclinacao.confianca,
        corte=lombada.posicao,
        confianca_corte=lombada.confianca,
        verso=_marca_do_verso(img),
        tinta=tinta,
        em_branco=tinta < analise.FRACAO_TINTA_BRANCA,
    )


def _rotular(img: np.ndarray, texto: str, altura_faixa: int = 54) -> np.ndarray:
    """Cola uma faixa branca com o nome do filtro em cima da imagem."""
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    faixa = np.full((altura_faixa, img.shape[1], 3), 255, dtype=np.uint8)
    cv2.putText(faixa, texto, (12, 37), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                (0, 0, 0), 2, cv2.LINE_AA)
    cv2.line(faixa, (0, altura_faixa - 1), (img.shape[1], altura_faixa - 1),
             (180, 180, 180), 1)
    return np.vstack([faixa, img])


def _lado_a_lado(paineis: list[np.ndarray]) -> np.ndarray:
    """Junta os paineis lado a lado, com uma tarja cinza entre eles."""
    altura = max(p.shape[0] for p in paineis)
    partes = []
    for p in paineis:
        if p.shape[0] < altura:
            p = np.vstack([p, np.full((altura - p.shape[0], p.shape[1], 3), 255,
                                      dtype=np.uint8)])
        partes.append(p)
        partes.append(np.full((altura, 8, 3), 200, dtype=np.uint8))
    return np.hstack(partes[:-1])


def comparativo(doc, indice: int, destino: Path, motivo: str) -> None:
    """Gera o comparativo dos quatro filtros de uma página."""
    bruta = pagina_para_array(doc, indice, dpi=DPI_COMPARATIVO)

    paineis, zooms = [], []
    for filtro, nome in ((ORIGINAL, "Original"), (PRETO_E_BRANCO, "Preto e branco"),
                         (MELHORAR, "Melhorar"), (MAGICO_PRO, "Magico pro")):
        saida, _ = aplicar_filtro(bruta, filtro)
        if saida.ndim == 2:
            saida = cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)
        paineis.append(_rotular(limitar_altura(saida, 1000), nome))

        # recorte do miolo do texto, para julgar de perto
        h, w = saida.shape[:2]
        y, x = int(h * 0.34), int(w * 0.16)
        zooms.append(_rotular(saida[y:y + 300, x:x + 760], nome))

    cv2.imwrite(str(destino / f"{motivo}_pag{indice + 1:03d}.png"), _lado_a_lado(paineis))
    cv2.imwrite(str(destino / f"{motivo}_pag{indice + 1:03d}_zoom.png"), _lado_a_lado(zooms))


def analisar_arquivo(caminho: Path) -> None:
    """Mede o livro inteiro a DPI_ANALISE, imprime o relatorio de texto
    (`_relatorio`) e gera os comparativos das paginas mais dificeis
    (`_gerar_comparativos`)."""
    print("\n" + "=" * 74)
    print(f"ARQUIVO: {caminho.name}")
    print("=" * 74)

    doc = abrir_pdf(caminho)
    try:
        infos = info_paginas(doc)
        medidas: list[Medidas] = []

        for i, info in enumerate(infos):
            img = pagina_para_array(doc, i, dpi=DPI_ANALISE)
            medidas.append(medir(img, i + 1, dpi_real_da_pagina(doc, i)))
            del img

        _relatorio(caminho, infos, medidas)

        destino = SAIDA / caminho.stem[:40]
        destino.mkdir(parents=True, exist_ok=True)
        _gerar_comparativos(doc, medidas, destino)
        print(f"\n  imagens em: {destino}")
    finally:
        doc.close()


def _relatorio(caminho: Path, infos, medidas: list[Medidas]) -> None:
    total = len(medidas)
    paisagens = sum(1 for m in medidas if m.paisagem)
    coloridas = [m for m in medidas if m.tem_cor]
    brancas = [m for m in medidas if m.em_branco]
    dpi_medio = float(np.median([m.dpi for m in medidas]))
    amarelado = float(np.median([m.amarelado for m in medidas]))
    verso = float(np.median([m.verso for m in medidas]))

    # --- que tipo de material e ------------------------------------------
    print("\nTIPO")
    if paisagens == total:
        tipo = "folhas DUPLAS (todas em paisagem)"
    elif paisagens == 0:
        tipo = "páginas SIMPLES (todas em retrato)"
    else:
        tipo = f"MISTURADO: {paisagens} em paisagem e {total - paisagens} em retrato"
    print(f"  {total} folhas - {tipo}")
    print(f"  tamanho: {infos[0].largura_pt:.0f} x {infos[0].altura_pt:.0f} pt")

    if not coloridas:
        cor = "preto e branco (nenhuma página com cor)"
    elif len(coloridas) == total:
        cor = "colorido do começo ao fim"
    else:
        cor = (f"P&B com {len(coloridas)} página(s) colorida(s): "
               + ", ".join(str(m.numero) for m in coloridas[:8]))
    print(f"  cor: {cor}")

    qualidade = ("boa" if dpi_medio >= 250 else
                 "razoavel" if dpi_medio >= 150 else "baixa")
    print(f"  qualidade do scan: {qualidade} (~{dpi_medio:.0f} DPI)")

    tom = ("branco" if amarelado < 3 else
           "levemente amarelado" if amarelado < 8 else
           "amarelado" if amarelado < 14 else "bem amarelado")
    print(f"  papel: {tom} (b* = {amarelado:+.1f})")
    print(f"  marca do verso: {verso * 100:.1f}% dos pixels em cinza intermediario")

    # --- o que o programa detectou ---------------------------------------
    print("\nO QUE O PROGRAMA DETECTOU")
    if paisagens:
        cortes = [m for m in medidas if m.paisagem]
        confiantes = [m for m in cortes if m.confianca_corte >= 0.5]
        centrados = [m for m in cortes if 0.45 <= m.corte <= 0.55]
        print(f"  lombada: {len(confiantes)}/{len(cortes)} com confiança boa, "
              f"{len(centrados)} dentro de 45-55% da largura")
        posicoes = [m.corte for m in cortes]
        print(f"           posição mediana {np.median(posicoes):.3f} "
              f"(min {min(posicoes):.3f}, max {max(posicoes):.3f})")
    else:
        print("  lombada: não procurada (nenhuma folha em paisagem)")

    tortas = [m for m in medidas if abs(m.angulo) >= 0.3]
    muito = [m for m in medidas if abs(m.angulo) >= 3.0]
    print(f"  inclinação: {len(tortas)} página(s) fora do prumo, "
          f"{len(muito)} acima de 3 graus")
    if tortas:
        pior = max(tortas, key=lambda m: abs(m.angulo))
        print(f"              a mais torta e a {pior.numero} "
              f"({pior.angulo:+.1f} graus, confiança {pior.confianca_angulo:.2f})")

    if brancas:
        print(f"  em branco: {len(brancas)} - "
              + ", ".join(str(m.numero) for m in brancas[:10]))
    else:
        print("  em branco: nenhuma")

    # --- o que ele mesmo marcou para revisao ------------------------------
    marcadas = set()
    for m in medidas:
        if m.paisagem and m.confianca_corte < 0.5:
            marcadas.add(m.numero)
        if abs(m.angulo) >= 3.0:
            marcadas.add(m.numero)
        if m.em_branco:
            marcadas.add(m.numero)
        if m.tem_cor:
            marcadas.add(m.numero)
    pct = 100 * len(marcadas) / max(1, len(medidas))
    print(f"\n  marcadas para você conferir: {len(marcadas)} de {len(medidas)} "
          f"({pct:.0f}%)" + ("  <- acima da meta de 10%" if pct > 10 else ""))
    if marcadas:
        print("    " + ", ".join(str(n) for n in sorted(marcadas)[:20]))


def _gerar_comparativos(doc, medidas: list[Medidas], destino: Path) -> None:
    """Escolhe as páginas mais difíceis e gera o comparativo de cada uma."""
    uteis = [m for m in medidas if not m.em_branco] or medidas

    escolhas = {
        "amarelada": max(uteis, key=lambda m: m.amarelado),
        "torta": max(uteis, key=lambda m: abs(m.angulo)),
        "verso": max(uteis, key=lambda m: m.verso),
    }
    coloridas = [m for m in uteis if m.tem_cor]
    if coloridas:
        escolhas["colorida"] = max(coloridas, key=lambda m: m.saturacao)

    print("\nPAGINAS MAIS DIFICEIS (o comparativo sai destas)")
    ja_feitas: set[int] = set()
    for motivo, m in escolhas.items():
        detalhe = {
            "amarelada": f"b* = {m.amarelado:+.1f}",
            "torta": f"{m.angulo:+.1f} graus",
            "verso": f"{m.verso * 100:.1f}% de cinza intermediario",
            "colorida": f"saturação {m.saturacao:.0f}",
        }[motivo]
        print(f"  {motivo:<10} pagina {m.numero:>3}  ({detalhe})")
        if m.numero in ja_feitas:
            continue
        ja_feitas.add(m.numero)
        comparativo(doc, m.numero - 1, destino, motivo)


def main(alvos: list[str]) -> int:
    """Aceita arquivos e/ou pastas na linha de comando (pasta = todos os
    .pdf dentro) e analisa cada um. Um livro que falha não interrompe os
    outros - o erro so vira uma linha impressa."""
    SAIDA.mkdir(parents=True, exist_ok=True)

    arquivos: list[Path] = []
    for alvo in alvos:
        caminho = Path(alvo)
        if caminho.is_dir():
            arquivos.extend(sorted(caminho.glob("*.pdf")))
        elif caminho.is_file():
            arquivos.append(caminho)
        else:
            print(f"nao achei: {alvo}")

    if not arquivos:
        print("nenhum PDF para analisar")
        return 1

    for arquivo in arquivos:
        try:
            analisar_arquivo(arquivo)
        except Exception as erro:  # noqa: BLE001
            print(f"  ERRO em {arquivo.name}: {erro}")

    print(f"\n\n{len(arquivos)} arquivo(s) analisado(s).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1:]))
