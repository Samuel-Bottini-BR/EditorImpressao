"""Monta as fotos antes × depois da conferência da etapa 10b (JPG de até ~300 KB).

Cada foto: as imagens lado a lado, na mesma altura, com o nome de cada uma em
cima (Original / Antes / Agora) e, embaixo, por onde a página passou e com
quais opções (regra de 21/10). As imagens de entrada são as que os roteiros
reproduzir.py e somas_da_imagem.py gravam (pasta _tmp da worktree, fora do
git). USO: python fazer_imagens.py [nome ...]  (grava em ../conferencia/img/).
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
T = RAIZ / "_tmp"
SAIDA = AQUI.parent / "conferencia" / "img"
_FONTE = None


def _fonte(tamanho: int):
    for nome in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def _ler(caminho: str, recorte=None) -> np.ndarray:
    img = cv2.imread(str(T / caminho), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(caminho)
    if recorte:
        h, w = img.shape[:2]
        x0, y0, x1, y1 = recorte
        img = img[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
    return img


def _escrever(img: np.ndarray, texto: str, y: int, tamanho: int = 30) -> np.ndarray:
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ImageDraw.Draw(pil).text((12, y), texto, fill=(160, 20, 20), font=_fonte(tamanho))
    return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)


def foto(nome: str, caminho: str, partes: list, altura: int = 900, recorte=None) -> None:
    """partes: [(rótulo, arquivo em _tmp, recorte ou None)]."""
    tiras = []
    for rotulo, arquivo, rec in partes:
        img = _ler(arquivo, rec or recorte)
        img = cv2.resize(img, (max(1, int(img.shape[1] * altura / img.shape[0])), altura),
                         interpolation=cv2.INTER_AREA)
        img = cv2.copyMakeBorder(img, 50, 0, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        img = _escrever(img, rotulo, 6)
        tiras += [img, np.full((altura + 50, 10, 3), (40, 40, 200), np.uint8)]
    junta = np.hstack(tiras[:-1])
    rodape = _escrever(np.full((48, junta.shape[1], 3), 255, np.uint8), caminho, 8, 26)
    junta = np.vstack([junta, rodape])
    if junta.shape[1] > 2400:
        f = 2400 / junta.shape[1]
        junta = cv2.resize(junta, (2400, int(junta.shape[0] * f)), interpolation=cv2.INTER_AREA)
    SAIDA.mkdir(parents=True, exist_ok=True)
    for q in (85, 78, 70, 62, 55, 48, 40):
        _ok, dados = cv2.imencode(".jpg", junta, [cv2.IMWRITE_JPEG_QUALITY, q])
        if len(dados) <= 300_000:
            break
    (SAIDA / f"{nome}.jpg").write_bytes(dados.tobytes())
    print(nome, junta.shape[1], "x", junta.shape[0], len(dados) // 1024, "KB", flush=True)


LIVRO = "projeto do teste de 23/10 (endireitada, cortada)"
NOVO = "livro novo de fábrica (dividir, endireitar, cortar)"
CASOS = [
    ("4-1-palatino74", f"Palatino 74 - {LIVRO}, Preto e branco, Achar gravuras ligado", [
        ("Original", "antes/palatino-p074-inteira-original.png", None),
        ("Antes", "antes/palatino-p074-inteira-preto_e_branco.png", None),
        ("Agora", "depois/palatino-p074-inteira-preto_e_branco.png", None)]),
    ("4-1-valades41", f"Valadés 41 (perto) - {LIVRO}, Preto e branco, Achar gravuras ligado", [
        ("Original", "antes/valades-p041-inteira-original.png", None),
        ("Antes", "antes/valades-p041-inteira-preto_e_branco.png", None),
        ("Agora", "depois/valades-p041-inteira-preto_e_branco.png", None)], (0.0, 0.18, 0.55, 0.52)),
    ("4-1-siebmacher110", f"Siebmacher 110 - {LIVRO}, Preto e branco", [
        ("Original", "antes/siebmacher-p110-inteira-original.png", None),
        ("Antes", "antes/siebmacher-p110-inteira-preto_e_branco.png", None),
        ("Agora", "depois/siebmacher-p110-inteira-preto_e_branco.png", None)]),
    ("4-3-boecio49", f"Boécio 49 (folha de guarda) - {LIVRO}, Preto e branco", [
        ("Original", "antes/boecio-p049-inteira-original.png", None),
        ("Antes", "antes/boecio-p049-inteira-preto_e_branco.png", None),
        ("Agora", "depois/boecio-p049-inteira-preto_e_branco.png", None)]),
    ("4-3-marial2", f"Marial 2 - {LIVRO}, Preto e branco", [
        ("Original", "antes/marial-p002-inteira-original.png", None),
        ("Antes", "antes/marial-p002-inteira-preto_e_branco.png", None),
        ("Agora", "depois/marial-p002-inteira-preto_e_branco.png", None)]),
    ("4-3-siebmacher74", f"Siebmacher 74 e 86 - {LIVRO}, Preto e branco", [
        ("74 Original", "antes/siebmacher-p074-inteira-original.png", None),
        ("74 Antes", "antes/siebmacher-p074-inteira-preto_e_branco.png", None),
        ("74 Agora", "depois/siebmacher-p074-inteira-preto_e_branco.png", None),
        ("86 Antes", "antes/siebmacher-p086-inteira-preto_e_branco.png", None),
        ("86 Agora", "depois/siebmacher-p086-inteira-preto_e_branco.png", None)]),
    ("4-2-matematica40", f"Matemática 40 (perto da lombada) - {LIVRO}, Preto e branco", [
        ("Original", "antes/matematica-p040-inteira-original.png", None),
        ("Antes", "antes/matematica-p040-inteira-preto_e_branco.png", None),
        ("Agora", "depois/matematica-p040-inteira-preto_e_branco.png", None)], (0.0, 0.0, 0.5, 0.45)),
    ("4-2-matematica66", f"Matemática 66 (perto da lombada) - {LIVRO}, Preto e branco", [
        ("Original", "antes/matematica-p066-inteira-original.png", None),
        ("Antes", "antes/matematica-p066-inteira-preto_e_branco.png", None),
        ("Agora", "depois/matematica-p066-inteira-preto_e_branco.png", None)], (0.0, 0.0, 0.5, 0.45)),
    ("celular", f"Fotos de celular: Razões do Integralismo 57 e Atanásio 8 - {NOVO}, Preto e branco", [
        ("Razões Original", "antes/fab-razoes-p057-inteira-original.png", None),
        ("Antes", "antes/fab-razoes-p057-inteira-preto_e_branco.png", None),
        ("Agora", "depois/fab-razoes-p057-inteira-preto_e_branco.png", None),
        ("Atanásio Antes", "antes/fab-atanasio-p008-inteira-preto_e_branco.png", None),
        ("Agora", "depois/fab-atanasio-p008-inteira-preto_e_branco.png", None)]),
    ("4-7-pesel51", f"Pesel 51 e 59 - {LIVRO}, Mágico pro", [
        ("51 Antes", "antes/pesel-p051-inteira-magico_pro.png", None),
        ("51 Agora", "depois/pesel-p051-inteira-magico_pro.png", None),
        ("59 Antes", "antes/pesel-p059-inteira-magico_pro.png", None),
        ("59 Agora", "depois/pesel-p059-inteira-magico_pro.png", None)]),
    ("4-7-pesel67", f"Pesel 67 e 75 - {LIVRO}, Mágico pro", [
        ("67 Antes", "antes/pesel-p067-inteira-magico_pro.png", None),
        ("67 Agora", "depois/pesel-p067-inteira-magico_pro.png", None),
        ("75 Antes", "antes/pesel-p075-inteira-magico_pro.png", None),
        ("75 Agora", "depois/pesel-p075-inteira-magico_pro.png", None)]),
    ("4-11-valades203", f"Valadés 203 (perto da mancha) - {LIVRO}, Preto e branco", [
        ("Original", "antes/valades-p203-inteira-original.png", None),
        ("Antes", "antes/valades-p203-inteira-preto_e_branco.png", None),
        ("Agora", "depois/valades-p203-inteira-preto_e_branco.png", None)], (0.3, 0.53, 0.7, 0.62)),
    ("4-12-antiphon56", f"Antiphon 56 (margem da direita) - {LIVRO}, Mágico pro (o retângulo cinza é o 4.6, de outra etapa)", [
        ("Original", "antes/antiphon-p056-inteira-original.png", None),
        ("Antes", "antes/antiphon-p056-inteira-magico_pro.png", None),
        ("Agora", "depois/antiphon-p056-inteira-magico_pro.png", None)], (0.55, 0.25, 1.0, 0.65)),
    ("t-antiphonal46", f"Antiphonal 1547, p. 46 - {NOVO}, Preto e branco + Só as letras (Guardar a tinta forte)", [
        ("Antes: tela (prévia)", "t46-prev-novo.png", None),
        ("Antes: PDF", "t46-pdf-novo.png", None),
        ("Agora: tela", "t46-prev-fix.png", None),
        ("Agora: PDF", "t46-pdf-fix.png", None)], (0.0, 0.15, 1.0, 0.45)),
    ("reduzir-cores-horas26", f"Livro de Horas 26 - página-gabarito, {NOVO}, Preto e branco + Letras com a cor delas + Reduzir cores", [
        ("Sem Reduzir", "red-antes-a.png", None),
        ("Antes: com Reduzir", "red-antes-b.png", None),
        ("Agora: com Reduzir", "red-depois-b.png", None)], (0.05, 0.2, 0.5, 0.45)),
    ("d493-desentortar", "Página curva com notas na margem (a do D-113, Marial 41) - Desentortar aumentando a página", [
        ("Antes", "curvada-obra-etapa10b-antes-aumentado.png", None),
        ("Agora (só o bloco do texto)", "curvada-.-aumentado.png", None)], (0.05, 0.5, 0.5, 0.95)),
    ("somas-opus20-melhorar", f"Opus Majus 20 - página-gabarito, {NOVO}, Melhorar (o vão escuro atrás da estátua)", [
        ("Antes", "gab-antes/opusmajus_p020-melhorar-0.png", None),
        ("Agora", "gab-depois/opusmajus_p020-melhorar-0.png", None)]),
    ("somas-graduale222-pb", f"Graduale 222 (beirada da direita) - página-gabarito, {NOVO}, Preto e branco", [
        ("Antes", "gab-antes/graduale_p222-preto_e_branco-0.png", None),
        ("Agora", "gab-depois/graduale_p222-preto_e_branco-0.png", None)], (0.7, 0.1, 1.0, 0.6)),
    ("somas-marial7-melhorar", f"Marial 7 - página-gabarito, {NOVO}, Melhorar (o grão do papel)", [
        ("Antes", "gab-antes/marial_p007-melhorar-0.png", None),
        ("Agora", "gab-depois/marial_p007-melhorar-0.png", None)], (0.0, 0.3, 0.5, 0.7)),
    ("tela-cheia-boecio22", "Boécio 22 (perto) - página-gabarito, Preto e branco, jeito Wolf do ScanTailor: tela cheia (150 DPI) e PDF", [
        ("Antes: tela cheia", "tc-antes-tela.png", None),
        ("Agora: tela cheia", "tc-depois-tela.png", None),
        ("PDF reduzido (igual nos dois)", "tc-depois-pdf.png", None)], (0.1, 0.3, 0.5, 0.5)),
]

if __name__ == "__main__":
    pedidos = set(sys.argv[1:])
    for caso in CASOS:
        nome, caminho, partes = caso[0], caso[1], caso[2]
        if pedidos and nome not in pedidos:
            continue
        recorte = caso[3] if len(caso) > 3 else None
        try:
            foto(nome, caminho, partes, recorte=recorte)
        except FileNotFoundError as falta:
            print(nome, "FALTA", falta)
