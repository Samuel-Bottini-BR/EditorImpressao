"""D-585: as imagens da pergunta. Cada página pelo caminho inteiro (livro novo de uma página,
Automático de sempre: endireitar, cortar, "Limpar a folha", "Gravuras e fotos"), no tamanho do
PDF, em três versões lado a lado:
  1. Original (endireitada e cortada, sem filtro);
  2. Preto e branco HOJE, sem "Só as letras" (o que o programa faz no 226536c);
  3. Preto e branco com a OPÇÃO B (protótipo, só neste script; o programa não muda): no Preto
     e branco sem "Só as letras" nada fica colorido - o que hoje fica com a cor como "enfeite"
     (moldura, iluminura e a pintura que o programa toma por enfeite) sai em tons de cinza,
     com a mesma conta da foto (_foto_em_tons_de_cinza, a da D-147).
Uso: python relatorios/automatico-pintura/opcoes_d585.py [alvo ...]   (alvos como medir_gabarito.py)
Grava relatorios/automatico-pintura/d585-<alvo>.jpg (menos de 400 KB).
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

import medir_gabarito as M  # noqa: E402  (põe a raiz da worktree no caminho e a pasta de dados em _tmp)
from core import filtros as F  # noqa: E402

ALVOS = ["escola-capa-do-samuel", "escola:19", "escola:45", "escola:173", "horas_p011", "horas_p013",
         "horas_p026", "horas_p047"]
NOMES = {"escola-capa-do-samuel": "Na escola de Jesus, capa (página 1 do projeto dele)",
         "escola:19": "Na escola de Jesus, página 19", "escola:45": "Na escola de Jesus, página 45",
         "escola:173": "Na escola de Jesus, página 173", "horas_p011": "Livro de Horas, página 11 (iluminura)",
         "horas_p013": "Livro de Horas, página 13 (moldura dourada)",
         "horas_p026": "Livro de Horas, página 26 (moldura)", "horas_p047": "Livro de Horas, página 47 (iluminura)"}

_tipos_de_hoje = F._tipos_das_zonas
_fechos_de_hoje = F._fechos_de_foto
_VIRARAM_FOTO: list = []      # as zonas que eram enfeite (o fecho da foto nao vale nelas)


def _fechos_sem_os_enfeites(rotulos, foto, peso_gravura):
    """O fecho convexo da foto (Opus 20) so nas fotos de verdade: no enfeite que virou cinza ele
    cobriria o texto que a iluminura emoldura (as letras sairiam cinza)."""
    if _VIRARAM_FOTO:
        foto = foto & ~_VIRARAM_FOTO[-1]
    return _fechos_de_hoje(rotulos, foto, peso_gravura) if foto.any() else None


def _tudo_em_cinza(img3, peso_gravura, com_decoracao=True, so_a_decoracao=False):
    """Opção B (protótipo): no Preto e branco, o enfeite colorido vira "foto" (tons de cinza)."""
    rotulos, foto, decoracao, referencia = _tipos_de_hoje(img3, peso_gravura, com_decoracao, so_a_decoracao)
    if not so_a_decoracao and decoracao.any():
        _VIRARAM_FOTO.append(decoracao.copy())
        foto = foto | decoracao
        decoracao = np.zeros_like(decoracao)
    return rotulos, foto, decoracao, referencia


def _reduzir(img, altura=900):
    img = img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    h, w = img.shape[:2]
    return cv2.resize(img, (max(1, int(w * altura / h)), altura), interpolation=cv2.INTER_AREA)


def _com_titulo(img, texto):
    from PIL import Image, ImageDraw, ImageFont

    faixa = np.full((44, img.shape[1], 3), 255, np.uint8)
    pil = Image.fromarray(np.vstack([faixa, img])[..., ::-1])
    desenho = ImageDraw.Draw(pil)
    try:
        fonte = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
    except OSError:
        fonte = ImageFont.load_default()
    desenho.text((8, 8), texto, fill=(0, 0, 0), font=fonte)
    return np.asarray(pil)[..., ::-1].copy()


def main() -> None:
    alvos = sys.argv[1:] or ALVOS
    for alvo in alvos:
        M.ALVO = alvo
        projeto, pagina = M.carregar(alvo)
        partes = []
        for rotulo, filtro, tipos in (("Original", "original", _tipos_de_hoje),
                                      ("Preto e branco HOJE", "preto_e_branco", _tipos_de_hoje),
                                      ("Opção B: tudo em tons de cinza", "preto_e_branco", _tudo_em_cinza)):
            F._tipos_das_zonas = tipos
            F._fechos_de_foto = _fechos_sem_os_enfeites if tipos is _tudo_em_cinza else _fechos_de_hoje
            p = copy.deepcopy(pagina)
            p.filtro = filtro
            img = M.pronta(projeto, p)
            partes.append(_com_titulo(_reduzir(img), rotulo))
        F._tipos_das_zonas = _tipos_de_hoje
        F._fechos_de_foto = _fechos_de_hoje
        h = max(x.shape[0] for x in partes)
        partes = [np.pad(x, ((0, h - x.shape[0]), (0, 12), (0, 0)), constant_values=255) for x in partes]
        quadro = _com_titulo(np.hstack(partes), NOMES.get(alvo, alvo) + " - endireitada, cortada, "
                             "Limpar a folha, Gravuras e fotos; Preto e branco SEM 'Só as letras'")
        nome = AQUI / f"d585-{alvo.replace(':', '-p').replace('_', '-')}.jpg"
        for qualidade in (85, 75, 65, 55):
            cv2.imwrite(str(nome), quadro, [cv2.IMWRITE_JPEG_QUALITY, qualidade])
            if nome.stat().st_size < 400_000:
                break
        print(nome.name, nome.stat().st_size // 1024, "KB", flush=True)


if __name__ == "__main__":
    main()
