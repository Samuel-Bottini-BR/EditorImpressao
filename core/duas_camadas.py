"""Itens 2.10 e 1.6: o PDF de saída em duas camadas (a letra em cima, o fundo embaixo), como opção.

O QUE É
    1.6 (plano): "PDF de saída em duas camadas (letra em cima, fundo embaixo),
    como opção." 2.10: "Separar a saída em duas camadas" - o ScanTailor separa a
    saída em "foreground" e "background" (output/SplittingOptions,
    OutputImageWithForegroundMask); montar o PDF com elas é nosso (mapa do
    ScanTailor, 6.10), do jeito do Internet Archive (memoria/referencias/
    internet-archive.md): EMBAIXO o fundo, em resolução baixa e bem comprimido;
    EM CIMA a página em resolução cheia, recortada por uma máscara de 1 bit, só
    onde há o que imprimir.

    Decisão do Samuel (conferência 5, P3, 01/10/2026): "Eu quero ter a opção
    1.6, mas eu quero poder deixar como está também, o tamanho do arquivo depois
    não importa". Por isso: OPÇÃO, desmarcada de fábrica
    (Projeto.pdf_em_duas_camadas); desmarcada, o PDF sai exatamente como hoje.
    Motivo do pedido (Lista de bugs, 01/10/2026): o Preto e branco com
    decoração em cor dá 25,6 MB por página na Horas 11; o Mágico pro, ~8 MB.

COMO SE SEPARA
    A máscara de cima é o que NÃO é papel na página pronta: ponto bem mais
    escuro que o papel da página (20 níveis abaixo do claro que mais aparece,
    e nunca acima de LIMIAR_DO_PAPEL) ou com uma cor que foge da do papel
    (croma acima de LIMIAR_DA_COR), engordado um pouco (as bordas da letra
    vão junto). Na página que o filtro levou a branco, o papel é 255; no
    Original, o creme dele. Assim letra, gravura, foto e iluminura ficam em cima, em
    resolução cheia; o papel e a sombra clarinha ficam embaixo, em 1/3. Página em
    1 bit (Preto e branco puro) não precisa: já é pequena e sai como sempre.

    Em cima, a imagem vai em JPEG de qualidade alta (QUALIDADE_DE_CIMA) e a
    máscara em 1 bit sem perda; embaixo, JPEG (QUALIDADE_DE_BAIXO). É por isso
    que o arquivo fica menor - e é a ressalva: a camada de cima tem perda
    (pequena). Quem quer sem perda nenhuma deixa a caixinha desmarcada.

SEGURO MUDAR: as qualidades, a redução e os limiares (só tamanho e nitidez do
    papel). ARRISCADO: tirar o engordar da máscara (a borda da letra sairia
    da cor do fundo, um contorno claro em volta de cada letra).
"""

from __future__ import annotations

import cv2
import numpy as np

REDUCAO_DO_FUNDO = 3          # o Internet Archive usa 1/3 da resolução no fundo
QUALIDADE_DE_CIMA = 92
QUALIDADE_DE_BAIXO = 50
LIMIAR_DO_PAPEL = 235          # mais escuro que isto não é papel
LIMIAR_DA_COR = 24             # croma (no LAB) acima disto é cor, não papel
ENGORDAR = 2                   # pontos em volta de cada coisa impressa


def mascara_de_cima(img: np.ndarray) -> np.ndarray:
    """Onde há o que imprimir (True): vai para a camada de cima."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # O nivel do papel da pagina (o claro que mais aparece): na pagina que o
    # filtro levou a branco e 255; no Original e o creme do papel. O que e
    # bem mais escuro que ele e impresso.
    nivel = float(np.percentile(cinza, 90))
    limiar = min(LIMIAR_DO_PAPEL, nivel - 20)
    papel = cinza >= nivel - 5
    if img.ndim == 2:
        com_cor = np.zeros(img.shape, bool)
    else:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        a = lab[..., 1].astype(np.int16) - 128
        b = lab[..., 2].astype(np.int16) - 128
        # a cor do papel (o creme) nao conta como cor: so o que foge dela
        a0 = float(np.median(a[papel])) if papel.any() else 0.0
        b0 = float(np.median(b[papel])) if papel.any() else 0.0
        com_cor = (np.abs(a - a0) + np.abs(b - b0)) > LIMIAR_DA_COR
    mascara = ((cinza < limiar) | com_cor).astype(np.uint8)
    if ENGORDAR > 0 and mascara.any():
        nucleo = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * ENGORDAR + 1, 2 * ENGORDAR + 1))
        mascara = cv2.dilate(mascara, nucleo)
    return mascara.astype(bool)


def fundo(img: np.ndarray, mascara: np.ndarray) -> np.ndarray:
    """A camada de baixo: a página sem o que está em cima (no lugar, a média
    do papel em volta), reduzida a 1/REDUCAO_DO_FUNDO."""
    altura, largura = img.shape[:2]
    pequeno = (max(1, largura // REDUCAO_DO_FUNDO), max(1, altura // REDUCAO_DO_FUNDO))
    livre = (~mascara).astype(np.float32)
    img_f = img.astype(np.float32)
    if img.ndim == 3:
        livre_c = livre[..., None]
    else:
        livre_c = livre
    soma = cv2.resize(img_f * livre_c, pequeno, interpolation=cv2.INTER_AREA)
    conta = cv2.resize(livre, pequeno, interpolation=cv2.INTER_AREA)
    if img.ndim == 3:
        conta = conta[..., None]
    with np.errstate(invalid="ignore", divide="ignore"):
        media = np.where(conta > 1e-3, soma / np.maximum(conta, 1e-3), np.nan)
    if np.isnan(media).all():
        return np.full(media.shape, 255, np.uint8)
    # onde não sobrou papel nenhum, a cor do papel da página toda
    papel = np.nanmedian(media.reshape(-1, media.shape[-1] if media.ndim == 3 else 1), axis=0)
    buracos = np.isnan(media)
    media = np.where(buracos, papel if media.ndim == 3 else papel[0], media)
    return np.clip(media, 0, 255).astype(np.uint8)


def _jpeg(img: np.ndarray, qualidade: int) -> bytes:
    ok, dados = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, int(qualidade)])
    if not ok:
        raise ValueError("não consegui comprimir a camada")
    return dados.tobytes()


def _png_de_1_bit(mascara: np.ndarray) -> bytes:
    import io

    from PIL import Image

    imagem = Image.fromarray((mascara.astype(np.uint8) * 255)).convert("1", dither=Image.Dither.NONE)
    saida = io.BytesIO()
    imagem.save(saida, format="PNG", optimize=False, compress_level=6)
    return saida.getvalue()


def camadas(img: np.ndarray) -> tuple[bytes, bytes, bytes]:
    """(fundo em JPEG, cima em JPEG, máscara de cima em PNG de 1 bit)."""
    mascara = mascara_de_cima(img)
    de_baixo = _jpeg(fundo(img, mascara), QUALIDADE_DE_BAIXO)
    # fora da máscara a cor de cima não aparece: o papel liso comprime melhor
    cima = img.copy()
    cima[~mascara] = 255
    return de_baixo, _jpeg(cima, QUALIDADE_DE_CIMA), _png_de_1_bit(mascara)
