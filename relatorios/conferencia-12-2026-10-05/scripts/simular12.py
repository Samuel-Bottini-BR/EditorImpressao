r"""Imagens da conferencia 12 (05/10/2026, conferir-aqui-12.html). PROTOTIPO: nada aqui muda o programa.

Reaproveita comum11/simular da conferencia 11 (via comum12) e grava os .jpg em
relatorios/conferencia-12-2026-10-05/. As paginas sao as do gabarito (somente leitura), preparadas
pelo caminho do programa (comum11.preparada).

  P2  Palatino 5, o retrato: o Misto (core.misto.aplicar_misto) com papel_da_gravura_branco=True
      (a, "papel a branco") e False (b, "papel creme"). Nada simulado: e a chave que o Misto ja tem.
      p2_risco: onde a (a) apaga traco claro do desenho:
        - no proprio retrato: a janela com mais pontos "traco claro do original que a (a) levou a
          branco" (medido, ver _janela_do_risco);
        - na capitular do Palatino 9: o detector NAO a marca como gravura (ela vai ao preto e branco);
          aqui um retangulo "gravura ou foto" a mao em volta dela (como o Kaique faria) e o Misto (a)
          e (b). A zona a mao e a unica parte "simulacao".
  P3  Escola 7 e Opus Majus 20: o Misto (foto com a cor) e o Preto e branco de hoje
      (core.filtros.aplicar_filtro_com_selecao), sem simulacao.
  P4  Horas 13 e Horas 11, as letras coloridas: original | letras com a cor e o fundo como no
      original | letras com a cor e papel branco. As duas ultimas sao SIMULACAO, pela conta deduzida
      do ScanTailor (OutputGenerator.cpp, modifyBinarizationMask, "Add to foreground"; simular.py da
      conferencia 11, tinta_com_a_cor): dentro da zona, onde o preto e branco da pagina diz tinta,
      o ponto do original; o resto, branco. "Fundo como no original": o ponto do original na zona
      inteira. Zona: retangulo a mao (o miolo da moldura da Horas 13; o miolo do oval da Horas 11,
      so o que no Misto de hoje e papel ou letra - o festao fica como o Misto o deixa).
      Tambem a conta do proprio programa sem a letra preta (core.filtros._com_a_decoracao com
      letras_pretas=False) na Horas 11, para comparar (medida no json).
  P11 o tipo 3 ("tinta preta, fundo original", Add to background) no titulo da Horas 13.

Uso: .venv\Scripts\python.exe relatorios\conferencia-12-2026-10-05\scripts\simular12.py [p2 p2_risco p3 p4 p11]
"""
from __future__ import annotations

import json
import sys

import cv2
import numpy as np

import comum12  # noqa: F401  (ajusta os caminhos e comum11.AQUI)
import comum11
import simular as S

from core import filtros as F
from core.misto import aplicar_misto, _peso_da_imagem
from core.selecao import GRAVURA, MAO, RETANGULO, Regiao

MEDIDAS: dict = {}


def misto(img, sel, aj, **kw):
    return aplicar_misto(img, sel, aj["forca_preto"], aj["algoritmo_pb"], aj["despeckle"],
                         aj["clareza"], aj["intensidade"], **kw)[0]


def rec(img, caixa):
    return S._recorte(img, caixa)


# --- P2 ------------------------------------------------------------------------------------

def p2():
    img, sel, aj = comum11.preparada("palatino_p005")
    a = misto(img, sel, aj, papel_da_gravura_branco=True)
    b = misto(img, sel, aj, papel_da_gravura_branco=False)
    rot = ["(a) Papel a branco", "(b) Papel creme"]
    subs = ["o papel entre os traços vai a branco", "a gravura como foi escaneada"]
    S.gravar(S.painel([a, b], rot, 1100, subs), "p2-palatino5-a-b.jpg")
    caixa = (0.30, 0.40, 0.66, 0.62)
    S.gravar(S.painel([rec(x, caixa) for x in (img, a, b)], ["Original", rot[0], rot[1]], 640,
                      ["", "", ""]), "p2-palatino5-rosto.jpg")


def _janela_do_risco(img, a, zona, lado):
    """A janela (lado x lado pontos) com mais 'traco claro' do original que a (a) levou a branco:
    ponto do original mais escuro que o papel do retrato (mediana da zona) em 12 a 45 niveis de
    cinza, e na (a) acima de 240."""
    cinza = cv2.cvtColor(F._tres_canais(img), cv2.COLOR_BGR2GRAY).astype(np.int16)
    cinza_a = cv2.cvtColor(F._tres_canais(a), cv2.COLOR_BGR2GRAY)
    papel = int(np.percentile(cinza[zona], 80))
    claro = zona & (cinza < papel - 12) & (cinza > papel - 45)
    perdido = (claro & (cinza_a > 240)).astype(np.float32)
    soma = cv2.boxFilter(perdido, -1, (lado, lado), normalize=False)
    soma[~zona] = 0
    y, x = np.unravel_index(int(np.argmax(soma)), soma.shape)
    MEDIDAS["p2_papel_do_retrato_cinza"] = papel
    MEDIDAS["p2_tracos_claros_no_retrato"] = int(claro.sum())
    MEDIDAS["p2_tracos_claros_levados_a_branco"] = int(perdido.sum())
    return max(0, x - lado // 2), max(0, y - lado // 2)


PALATINO9_CAPITULAR = (0.105, 0.292, 0.427, 0.503)


def p2_risco():
    img, sel, aj = comum11.preparada("palatino_p005")
    a = misto(img, sel, aj, papel_da_gravura_branco=True)
    b = misto(img, sel, aj, papel_da_gravura_branco=False)
    h, w = img.shape[:2]
    zona = _peso_da_imagem(sel, h, w) > 0.99
    zona = cv2.erode(zona.astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
    lado = int(0.12 * w)
    x, y = _janela_do_risco(img, a, zona, lado)
    MEDIDAS["p2_janela_risco_frac"] = [round(x / w, 3), round(y / h, 3), round((x + lado) / w, 3),
                                       round((y + lado) / h, 3)]
    caixa = (x / w, y / h, (x + lado) / w, (y + lado) / h)
    S.gravar(S.painel([rec(t, caixa) for t in (img, a, b)], ["Original", "(a) Papel a branco",
                                                               "(b) Papel creme"], 640),
             "p2-palatino5-risco.jpg")

    img, sel, aj = comum11.preparada("palatino_p009")
    hoje = misto(img, sel, aj)
    com = comum11.copia(sel)
    com.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO,
                           pontos=[PALATINO9_CAPITULAR[:2], PALATINO9_CAPITULAR[2:]], origem=MAO))
    a = misto(img, com, aj, papel_da_gravura_branco=True)
    b = misto(img, com, aj, papel_da_gravura_branco=False)
    caixa = (0.09, 0.28, 0.44, 0.54)
    S.gravar(S.painel([rec(S.contorno(img, PALATINO9_CAPITULAR, cor=(0, 110, 255)), caixa)] + [rec(t, caixa) for t in (hoje, a, b)],
                      ["Original", "Misto, sem marcar", "(a) Papel a branco", "(b) Papel creme"], 640,
                      ["laranja: marcada como gravura", "a capitular vai ao preto e branco",
                       "marcada como gravura", "marcada como gravura"], colunas=2),
             "p2-palatino9-capitular.jpg")


# --- P3 ------------------------------------------------------------------------------------

def p3():
    for pid, nome in (("escola_p007", "p3-escola7.jpg"), ("opusmajus_p020", "p3-opus20.jpg")):
        img, sel, aj = comum11.preparada(pid)
        m = misto(img, sel, aj)
        pb = S._pb(img, sel, aj)
        S.gravar(S.painel([img, m, pb], ["Original", "Com \"Só as letras\"", "Preto e branco normal"], 1000,
                          ["a página como veio", "a foto fica com a cor", "a foto sai em tons de cinza"]),
                 nome)


# --- P4 ------------------------------------------------------------------------------------

HORAS13_MIOLO = (0.115, 0.118, 0.765, 0.835)
HORAS11_MIOLO = (0.30, 0.10, 0.97, 0.80)


def _zona(img, caixa):
    return S._zona(img, Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[caixa[:2], caixa[2:]], origem=MAO))


def fundo_original(base, img, zona):
    out = F._tres_canais(base).copy()
    out[zona] = F._tres_canais(img)[zona]
    return out


def p4():
    # Horas 13: o miolo da moldura (titulos vermelhos e azuis, palavras azuis no texto)
    img, sel, aj = comum11.preparada("horas_p013")
    hoje = misto(img, sel, aj)
    zona = _zona(img, HORAS13_MIOLO)
    tinta = S._tinta(img, aj)
    creme = fundo_original(hoje, img, zona)
    branco = S.tinta_com_a_cor(hoje, img, zona, tinta)
    rot = ["Original", "Letras com a cor, fundo original", "Letras com a cor, papel branco"]
    subs = ["a página como veio", "simulação", "simulação (a nova)"]
    S.gravar(S.painel([img, creme, branco], rot, 1000, subs), "p4-horas13.jpg")
    caixa = (0.10, 0.10, 0.78, 0.40)
    S.gravar(S.painel([rec(t, caixa) for t in (img, creme, branco)], rot, 430, subs, colunas=1),
             "p4-horas13-detalhe.jpg", largura_max=1100)

    # Horas 11: o oval, letras vermelhas, azuis e douradas
    img, sel, aj = comum11.preparada("horas_p011")
    hoje = misto(img, sel, aj)
    # so o que no Misto de hoje e papel branco ou letra preta (o festao fica como esta)
    cinza = cv2.cvtColor(F._tres_canais(hoje), cv2.COLOR_BGR2GRAY)
    papel_ou_letra = (cinza >= 250) | (cinza <= 5)
    # o festao = pedacos GRANDES do que nao e papel nem letra (a beirada da letra, pequena, entra)
    caixa_zona = _zona(img, HORAS11_MIOLO)
    nao = (caixa_zona & ~papel_ou_letra).astype(np.uint8)
    n, rotulos, medidas, _c = cv2.connectedComponentsWithStats(nao, connectivity=8)
    grande = np.zeros(n, bool)
    grande[1:] = medidas[1:, cv2.CC_STAT_AREA] > 0.002 * nao.size
    zona = caixa_zona & ~grande[rotulos]
    tinta = S._tinta(img, aj)
    creme = misto(img, sel, aj, papel_da_gravura_branco=False)   # a decoracao inteira como no original
    branco = S.tinta_com_a_cor(hoje, img, zona, tinta)
    # a conta do proprio programa, sem a letra preta (para comparar)
    h, w = img.shape[:2]
    peso = _peso_da_imagem(sel, h, w)
    img3 = F._tres_canais(img)
    _rot, _foto, _deco, ref = F._tipos_das_zonas(img3, peso)
    programa = F._com_a_decoracao(img3.copy(), img3, peso, ref or F._referencia_do_papel(img3, peso > 0),
                                  letras_pretas=False)
    caixa = (0.28, 0.08, 0.98, 0.62)
    S.gravar(S.painel([rec(t, caixa) for t in (img, creme, branco)], rot, 700, subs),
             "p4-horas11.jpg")
    # perto, as letras douradas de LOUIS, com as duas contas de "papel branco"
    caixa = (0.33, 0.36, 0.80, 0.48)
    S.gravar(S.painel([rec(t, caixa) for t in (img, creme, branco, programa)],
                      rot + ["Letras com a cor, papel branco"], 330,
                      subs + ["simulação (outra conta: a do nosso programa, sem pôr a letra preta)"],
                      colunas=1), "p4-horas11-dourado.jpg", largura_max=1100)


# --- P11 -----------------------------------------------------------------------------------

def p11():
    img, sel, aj = comum11.preparada("horas_p013")
    hoje = misto(img, sel, aj)
    zona = _zona(img, S.TITULO_H13)
    tinta = S._tinta(img, aj)
    bg = S.tinta_preta_fundo_original(hoje, img, zona, tinta)
    caixa = (0.09, 0.10, 0.79, 0.29)
    S.gravar(S.painel([rec(t, caixa) for t in (img, bg)],
                      ["Original", "Tipo 3: tinta preta, fundo original"], 420,
                      ["a página como veio", "simulação (dedução do ScanTailor)"], colunas=1),
             "p11-tipo3-horas13.jpg", largura_max=1100)


if __name__ == "__main__":
    quais = sys.argv[1:] or ["p2", "p2_risco", "p3", "p4", "p11"]
    for q in quais:
        globals()[q]()
    js = comum12.AQUI / "scripts" / "simular12.json"
    antigo = json.loads(js.read_text(encoding="utf-8")) if js.exists() else {}
    antigo.update(MEDIDAS)
    js.write_text(json.dumps(antigo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(MEDIDAS)
