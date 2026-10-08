"""Rodada 4: os sinais do "Para revisar" medidos no RESULTADO DE VERDADE do
fase-1 de hoje (com o conserto do desenho claro), e tres sinais novos que
sairam dos "Nao concordo" da rodada 3.

Sinais de antes (rodada 2/3; ver criterio.py), agora medidos no resultado:
  apagado_a       tinta fora das linhas e das gravuras que o jeito de fabrica
                  mandou para o branco (preto e branco de base do Misto e
                  nao no resultado) / toda a tinta. Na rodada 3 esta conta
                  refazia a regra antiga e nao via o conserto.
  apagado_junto   a mesma tinta apagada, so onde ela se amontoa (janela de 2
                  alturas de linha com mais de 4% apagado)
  vazou_da_gravura  (medir.py) pedacos grandes encostados por fora na gravura
  beirada_a       (sinais.py) mancha cheia encostada na beirada / area

Sinais novos (rodada 4):
  fio_beirada     FIO preto comprido na beirada do resultado (a sombra da
                  beirada do Camoes 27 e 66: fina demais para o beirada_a, que
                  so ve mancha cheia). Conta: tinta do resultado, fora da
                  gravura, numa faixa de 2,5% do lado menor junto de cada
                  beirada; pedacos com comprimento ao longo da beirada de pelo
                  menos 8% dela e espessura pequena. Mede a soma dos
                  comprimentos / perimetro da pagina.
  letra_falhada   (ver a funcao) texto que o PRETO E BRANCO quebra (nos dois jeitos): em cada
                  linha do leitor, o cinza da linha da o papel (percentil 90) e
                  a tinta (percentil 2); "tinta pela metade" = pontos mais
                  escuros que o meio dos dois. Se o preto e branco guarda
                  menos de LIMITE_GUARDA dessa tinta, a linha esta falhada
                  (letra clara, vermelha ou gasta que sai picotada). Mede a
                  fracao das linhas (pesada pelo comprimento) falhadas.
                  Linhas muito baixas de contraste (papel - tinta < 25) nao
                  contam (sao a mancha do verso que o leitor leu).
  sem_conteudo    pagina sem tinta forte propria (em branco, ou so mancha do
                  verso): longe da beirada (8% de cada lado), tinta forte =
                  pontos com o cinza abaixo de 55% do papel. Mede a fracao da
                  area; e "letras_fortes" = quantos pedacos do tamanho de letra
                  ha nessa tinta (o titulo de uma linha do Gladstone 18 tem
                  letras; o carimbo da Rariora 8 e um borrao so).

Uso: python sinais4.py [pid,...]   (grava <TRABALHO>/sinais-rodada4.json)
"""
from __future__ import annotations

import json
import sys

import cv2
import numpy as np

import comum
import medir
from sinais import beirada_escura

LIMITE_JUNTO_DENS = 0.04
LIMITE_GUARDA = 0.62


def apagado_real(dados, z):
    T = z["base_tinta"]
    total = max(int(T.sum()), 1)
    fora = T & ~z["linhas"] & ~z["imagem"]
    apag = fora & ~z["a_tinta"]
    # pecas apagadas que encostam na beirada (1% da pagina) e ficam nela nao contam: sao a
    # tarja da biblioteca e o fundo do scanner (Egenloff: a barra "SLUB" do pe),
    # que ir para o branco e o certo; e assunto do corte (sinal 3)
    alt, larg = apag.shape
    m = max(2, int(round(0.01 * min(alt, larg))))
    n, rot, st, _c = cv2.connectedComponentsWithStats(apag.view(np.uint8), connectivity=8)
    if n > 1:
        borda = np.zeros_like(apag)
        borda[:m, :] = borda[-m:, :] = True
        borda[:, :m] = borda[:, -m:] = True
        tira = np.zeros(n, bool)
        tira[np.unique(rot[apag & borda])] = True
        # ...mas so a peca que fica toda na faixa de fora (6% de um lado): a
        # pauta vermelha que vai da beirada ate o meio (Antiphonal 46) conta
        x, y = st[:, cv2.CC_STAT_LEFT], st[:, cv2.CC_STAT_TOP]
        x1, y1 = x + st[:, cv2.CC_STAT_WIDTH], y + st[:, cv2.CC_STAT_HEIGHT]
        fx, fy = 0.06 * larg, 0.06 * alt
        so_na_faixa = (y1 <= fy) | (y >= alt - fy) | (x1 <= fx) | (x >= larg - fx)
        tira &= so_na_faixa
        tira[0] = False
        apag = apag & ~tira[rot]
    h = max(float(dados["altura_linha"]), 1.0)
    k = max(3, int(round(2 * h)))
    dens = cv2.boxFilter(apag.astype(np.float32), -1, (k, k), normalize=True)
    junto = apag & (dens > LIMITE_JUNTO_DENS)
    return float(apag.sum()) / total, float(junto.sum()) / total, apag


def maior_pedaco(apag, h: float, linhas=None) -> float:
    """Tinta do maior pedaco apagado (pontos apagados a menos de h/4 um do outro
    contam como um pedaco), em alturas de linha ao quadrado, SO entre os
    pedacos que encostam (a menos de uma altura de linha) numa linha de texto:
    a letra grande fica sempre colada no texto (o T vermelho do Antiphonal 46 da
    1,6); a mancha do canto (Cursus 3) e a sombra da beirada (Matematica 72), nao.
    E so pedaco cheio (ver abaixo)."""
    rad = max(1, int(round(h / 4)))
    junto = cv2.dilate(apag.view(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * rad + 1, 2 * rad + 1)))
    n, rot, st, _c = cv2.connectedComponentsWithStats(junto, connectivity=8)
    if n <= 1:
        return 0.0
    tinta = np.bincount(rot[apag], minlength=n)
    tinta[0] = 0
    # e so pedaco CHEIO (tinta >= 15% da caixa dele): a letra T da 0,20 e a L
    # do Antiphonal 76 0,24; a mancha pontilhada do canto do Cursus 3 da 0,06 e
    # o fio da moldura vermelha do Egenloff 3, 0,04
    caixa = np.maximum(st[:, cv2.CC_STAT_WIDTH] * st[:, cv2.CC_STAT_HEIGHT], 1)
    tinta[tinta < 0.15 * caixa] = 0
    if linhas is not None and linhas.any():
        r = max(1, int(round(h)))
        perto = cv2.dilate(linhas.view(np.uint8), np.ones((2 * r + 1, 2 * r + 1), np.uint8)) > 0
        encosta = np.zeros(n, bool)
        encosta[np.unique(rot[perto & (junto > 0)])] = True
        tinta[~encosta] = 0
    return float(tinta.max()) / (h * h)


def fio_na_beirada(tinta: np.ndarray):
    """(soma dos comprimentos dos fios / perimetro, mascara) no tamanho reduzido."""
    alt, larg = tinta.shape
    f = 1200 / max(alt, larg)
    peq = cv2.resize(tinta.astype(np.uint8) * 255, (max(1, round(larg * f)), max(1, round(alt * f))),
                     interpolation=cv2.INTER_AREA) > 100
    a, l = peq.shape
    faixa = max(3, int(round(0.025 * min(a, l))))
    mascara = np.zeros_like(peq)
    total = 0.0
    lados = {"cima": peq[:faixa, :], "baixo": peq[-faixa:, :],
             "esq": peq[:, :faixa].T, "dir": peq[:, -faixa:].T}
    for lado, banda in lados.items():
        n, rot, st, _ = cv2.connectedComponentsWithStats(banda.astype(np.uint8), connectivity=8)
        comp = banda.shape[1]
        for i in range(1, n):
            w, hh = st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]
            area = st[i, cv2.CC_STAT_AREA]
            if w >= 0.08 * comp and area / max(w, 1) <= 0.6 * faixa:
                total += w
                m = rot == i
                if lado == "cima":
                    mascara[:faixa, :] |= m
                elif lado == "baixo":
                    mascara[-faixa:, :] |= m
                elif lado == "esq":
                    mascara[:, :faixa] |= m.T
                else:
                    mascara[:, -faixa:] |= m.T
    return total / (2 * (a + l)), mascara


def letra_falhada(dados, z, tinta_res):
    """Texto que o preto e branco deixa PELA METADE (versao final da rodada 4).
    So linhas compridas (15% da largura ou mais) e longe da beirada (6% em cima
    e embaixo): carimbo, numero de estante e tarja ficam de fora. Em cada uma:
    papel = percentil 90 do cinza da linha, tinta = percentil 2; "tinta da
    letra" = pontos mais escuros que papel - 30% do contraste (pega o traco
    fino e claro). guarda = quanto dessa tinta o resultado guarda. A linha esta
    falhada se 20% <= guarda < LIMITE_GUARDA: abaixo de 20% a linha sumiu
    inteira, e no acervo isso e carimbo e anotacao a lapis que o preto e branco
    tira (o que se quer). Devolve (n falhadas, n linhas contadas, lista)."""
    cinza = z["cinza"]
    alt, larg = cinza.shape
    contadas, falhadas = 0, []
    for p in dados["poligonos"]:
        pts = np.asarray(p)
        x0, y0 = max(0, pts[:, 0].min()), max(0, pts[:, 1].min())
        x1, y1 = min(larg, pts[:, 0].max() + 1), min(alt, pts[:, 1].max() + 1)
        if (x1 - x0) < 0.15 * larg or y0 < 0.06 * alt or y1 > 0.94 * alt:
            continue
        g = cinza[y0:y1, x0:x1]
        papel, tinta = np.percentile(g, 90), np.percentile(g, 2)
        if papel - tinta < 25:
            continue
        m = g < papel - 0.3 * (papel - tinta)
        guarda = float((tinta_res[y0:y1, x0:x1] & m).sum()) / max(1, int(m.sum()))
        contadas += 1
        if 0.2 <= guarda < LIMITE_GUARDA:
            falhadas.append((int(x0), int(y0), int(x1), int(y1), round(guarda, 3)))
    return len(falhadas), contadas, falhadas


def linhas_por_contraste(dados, z):
    """(linhas fortes, linhas fracas): contraste da linha contra o papel da
    pagina (percentil 60 do miolo); forte = tinta (percentil 2) 50% mais escura
    que o papel. A mancha do verso que o leitor le como texto e fraca."""
    cinza = z["cinza"]
    alt, larg = cinza.shape
    papel = float(np.percentile(cinza[int(.1 * alt):int(.9 * alt), int(.1 * larg):int(.9 * larg)], 60))
    fortes = fracas = 0
    for p in dados["poligonos"]:
        pts = np.asarray(p)
        x0, y0 = max(0, pts[:, 0].min()), max(0, pts[:, 1].min())
        x1, y1 = min(larg, pts[:, 0].max() + 1), min(alt, pts[:, 1].max() + 1)
        if x1 - x0 < 4 or y1 - y0 < 4:
            continue
        c = (papel - float(np.percentile(cinza[y0:y1, x0:x1], 2))) / max(papel, 1.0)
        if c >= 0.5:
            fortes += 1
        else:
            fracas += 1
    return fortes, fracas


def sem_conteudo(z):
    cinza = z["cinza"]
    alt, larg = cinza.shape
    my, mx = int(0.08 * alt), int(0.08 * larg)
    g = cinza[my:alt - my, mx:larg - mx]
    papel = float(np.percentile(g, 60))
    forte = g < 0.55 * papel
    frac = float(forte.mean())
    n, _rot, st, _ = cv2.connectedComponentsWithStats(forte.astype(np.uint8), connectivity=8)
    lado = min(alt, larg)
    letras = 0
    if n > 1:
        tam = np.maximum(st[1:, cv2.CC_STAT_WIDTH], st[1:, cv2.CC_STAT_HEIGHT])
        letras = int(((tam >= 0.006 * lado) & (tam <= 0.06 * lado)).sum())
    return frac, letras


def pasta_de(base: str):
    """dados4 (fase-1 de hoje); se a pagina nao rodou na rodada 4 (o modelo do
    leitor de texto sumiu da pasta modelos/ as 19:20 de 07/10, ver LEIA-ME), os
    dados da rodada 3 (sem o conserto do desenho)."""
    return comum.DADOS if (comum.DADOS / f"{base}.json").exists() else comum.DADOS_R3


def medir_tudo(base: str) -> dict:
    pasta = pasta_de(base)
    dados = json.loads((pasta / f"{base}.json").read_text(encoding="utf-8"))
    z = dict(np.load(pasta / f"{base}.npz"))
    s, _m = medir.sinais(dados, z)     # vazou_da_gravura e companhia (iguais as rodadas 2 e 3)
    s["apagado_a"], s["apagado_junto"], apag = apagado_real(dados, z)
    s["maior_pedaco"] = maior_pedaco(apag, max(float(dados["altura_linha"]), 1.0), z["linhas"])
    s["beirada_a"], _ = beirada_escura(z["a_tinta"] & ~z["imagem"])
    s["fio_beirada"], _ = fio_na_beirada(z["a_tinta"] & ~z["imagem"])
    s["fio_beirada_pb"], _ = fio_na_beirada(z["pb_tinta"])
    s["falhadas_pb"], s["linhas_contadas"], s["falhadas_lista"] = letra_falhada(dados, z, z["pb_tinta"])
    s["sem_conteudo"], s["letras_fortes"] = sem_conteudo(z)
    s["linhas_fortes"], s["linhas_fracas"] = linhas_por_contraste(dados, z)
    med = dados["modos"]["rede"]["medidas"]
    s["desenho_fora"] = med.get("desenho_fora", 0.0)
    s["aviso_hoje"] = bool(dados["modos"]["rede"]["para_revisar"])
    s["dados_da_rodada3"] = pasta == comum.DADOS_R3
    s["alertas_da_analise"] = dados["alertas_da_analise"]
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()}  # noqa


def main() -> None:
    so = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    saida = comum.TRABALHO / "sinais-rodada4.json"
    todos = json.loads(saida.read_text(encoding="utf-8")) if saida.exists() else {}
    bases = sorted({js.stem for js in comum.DADOS.glob("*.json")}
                   | {js.stem for js in comum.DADOS_R3.glob("*.json")
                      if js.stem.split("__")[0] in comum.as_89()})
    for base in bases:
        if so and base.split("__")[0] not in so:
            continue
        s = medir_tudo(base)
        todos[base] = s
        print(f"{base:30s} hoje={int(s['aviso_hoje'])} apag={s['apagado_a']:.3f} junto={s['apagado_junto']:.3f} "
              f"vaz={s['vazou_da_gravura']:.3f} beir={s['beirada_a']:.3f} fio={s['fio_beirada']:.3f} "
              f"falhadas={s['falhadas_pb']}/{s['linhas_contadas']} fortes={s['linhas_fortes']} fracas={s['linhas_fracas']} "
              f"semc={s['sem_conteudo']:.4f} letras={s['letras_fortes']}", flush=True)
    saida.write_text(json.dumps(todos, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
