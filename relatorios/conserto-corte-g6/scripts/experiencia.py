"""EXPERIENCIA (nada do programa muda): que conserto da busca do corte serve?

Conserto do corte do G6 (implementador, 13/10/2026). O defeito: na ordem
nova a pagina e girada inteira (core.endireitar.rotacionar poe BRANCO na
cunha que sobra) e so depois o corte e procurado; o branco esconde a borda
preta do scanner (relatorio do verificador, ramo verif-corte-g6-2026-10-13).

Este script mede, nas 43 paginas que giram, varias VARIANTES da busca do
corte, trocando por fora (sem mudar o arquivo) as funcoes internas de
core.recortar. Serve para escolher a mudanca antes de escreve-la no programa
(CLAUDE.md, secao 5: medir antes, uma mudanca por vez, medir de novo).

As paginas vem das copias JPEG a 300 DPI que o verificador deixou em
.claude/worktrees/verif-corte-g6/_tmp/finais/<base>__inteira.jpg (so
leitura). Por serem JPEG, os numeros sao perto, nao iguais, aos do programa
(que le o PDF): a medida que vale e a do medir.py.

As variantes sao letras juntas:
    b / r   a cunha do giro pintada de Branco (como hoje) ou Repetindo a beirada
    p       a pagina chega com a cunha branca (como hoje), mas a tinta e
            achada com a cunha Preenchida pelo ponto de imagem mais proximo
            (na imagem reduzida): some a "tinta" que o degrau branco cria
    h       como "p", mas so onde a cunha encosta em FUNDO ESCURO do scanner
            (mais escuro que ESCURO_DO_SCANNER x o papel); onde encosta em
            papel a cunha fica branca, como hoje
    m<n>    quantos pontos de vizinhanca da cunha contam como cunha
    Z       a tinta que cai na cunha (e na vizinhanca dela) nao conta
    S       borda solida do scanner: a fracao de escuro e contada so nos
            pontos que sao imagem de verdade
    U       como S, mas SOMANDO ao apagar de hoje (borda solida e risca
            como hoje, e mais as linhas e colunas que o S acha)
    A       tira a "tinta" que so existe pelo degrau branco da cunha e esta
            em fundo escuro do scanner (duas contas do limiar local)
    a       (com U) a mesma tinta do "A", mas tirada so no fim, depois do
            apagar de hoje: o que hoje e apagado continua sendo
    N       (so "bN") o conserto COMO ESTA NO PROGRAMA: core.recortar.
            detectar_bordas com `girada`. E o "bUa", mais um acerto achado
            pelo teste de maquina (a coluna apagada como borda deixa de
            contar na conta das linhas).
    D       (com S) o fundo escuro do scanner conta como borda solida mesmo
            onde o limiar local nao ve tinta (fundo preto liso, Antiphon)
    R       risca de dobra: idem, e "encostar na beirada" e encostar na
            beirada da imagem de verdade
    P       peca de tinta que encosta na cunha e tratada como a que encosta
            na beirada da imagem (nao e peca)
"b" sozinho e o programa de hoje; "r" sozinho e a experiencia do verificador.

USO   python experiencia.py b,r,bS,bZS,...  [base,base,...]
Grava experiencia.json nesta pasta (junta com o que ja houver).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[1]
FINAIS = RAIZ.parent / "verif-corte-g6" / "_tmp" / "finais"
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(AQUI))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

import medir as M  # noqa: E402
from core import recortar as R  # noqa: E402
from core.endireitar import rotacionar, rotacionar_e_cortar  # noqa: E402

ORIGINAIS = {n: getattr(R, n) for n in ("_mascara_de_tinta_local", "_apagar_bordas_solidas",
                                        "_apagar_riscas_de_dobra", "_pecas_de_tinta")}
CTX: dict = {}


def girar(cinza: np.ndarray, angulo: float, modo: str) -> np.ndarray:
    if modo == "b":
        return rotacionar(cinza, angulo)
    alt, larg = cinza.shape[:2]
    matriz = cv2.getRotationMatrix2D((larg / 2.0, alt / 2.0), angulo, 1.0)
    return cv2.warpAffine(cinza, matriz, (larg, alt), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)


def fora_da_imagem(forma, angulo: float, margem: int) -> np.ndarray:
    """Na imagem reduzida de forma `forma`, os pontos que sao cunha do giro
    (nao vieram da pagina), mais `margem` pontos de vizinhanca."""
    alt, larg = forma[:2]
    matriz = cv2.getRotationMatrix2D((larg / 2.0, alt / 2.0), angulo, 1.0)
    cobre = cv2.warpAffine(np.ones((alt, larg), np.float32), matriz, (larg, alt),
                           flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    fora = cobre < 0.999
    if margem > 0:
        fora = cv2.dilate(fora.astype(np.uint8), np.ones((2 * margem + 1, 2 * margem + 1), np.uint8)) > 0
    return fora


def preencher(cinza: np.ndarray, fora: np.ndarray) -> np.ndarray:
    """A imagem com cada ponto da cunha trocado pelo ponto de imagem de
    verdade mais proximo (o que o "repetir a beirada" faz, mas na imagem
    reduzida): o limiar local deixa de ver um degrau branco que nao existe."""
    if not fora.any():
        return cinza
    _d, rotulos = cv2.distanceTransformWithLabels(fora.astype(np.uint8), cv2.DIST_L2, 3,
                                                  labelType=cv2.DIST_LABEL_PIXEL)
    # rotulos: para cada ponto, o numero do ponto de imagem (zero da mascara) mais proximo
    valores = np.zeros(int(rotulos.max()) + 1, cinza.dtype)
    valores[rotulos[~fora]] = cinza[~fora]
    cheia = cinza.copy()
    cheia[fora] = valores[rotulos[fora]]
    return cheia


def _mascara(cinza):
    if CTX["variante"][0] == "p":
        # "p": a pagina chega com a cunha branca (como hoje), mas o limiar
        # local e calculado com a cunha preenchida pela vizinha de verdade
        fora = fora_da_imagem(cinza.shape, CTX["angulo"], 0)
        tinta = ORIGINAIS["_mascara_de_tinta_local"](preencher(cinza, fora))
        CTX["fora"] = fora_da_imagem(cinza.shape, CTX["angulo"], CTX.get("margem", 0))
        return tinta
    if CTX["variante"][0] == "h":
        # "h": so onde a cunha encosta em FUNDO ESCURO do scanner ela e
        # preenchida com esse fundo; onde encosta em papel fica branca, como
        # hoje. A borda preta volta a chegar ate a beirada da imagem.
        fora = fora_da_imagem(cinza.shape, CTX["angulo"], 0)
        cheia = preencher(cinza, fora)
        papel = float(np.percentile(cinza[~fora][::7], 90))
        limite = float(CTX.get("escuro", R.ESCURO_DO_SCANNER)) * papel
        trocar = fora & (cheia < limite)
        cinza = np.where(trocar, cheia, cinza)
        CTX["fora"] = fora & ~trocar
        CTX["cinza"] = cinza
        return ORIGINAIS["_mascara_de_tinta_local"](cinza)
    tinta = ORIGINAIS["_mascara_de_tinta_local"](cinza)
    CTX["fora"] = fora_da_imagem(cinza.shape, CTX["angulo"], CTX.get("margem", 1))
    CTX["cinza"] = cinza
    if "a" in CTX["variante"]:
        # "a": a mesma tinta artificial do "A", mas tirada so NO FIM, depois
        # do apagar de hoje (ver _riscas_de_verdade, "U"): aqui so e achada
        fora = fora_da_imagem(cinza.shape, CTX["angulo"], 0)
        cheia = preencher(cinza, fora)
        sem_degrau = ORIGINAIS["_mascara_de_tinta_local"](cheia)
        papel = float(np.percentile(cinza[~fora][::7], 90))
        artificial = (tinta > 0) & (sem_degrau == 0) & (cheia < R.ESCURO_DO_SCANNER * papel)
        nucleo = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        sem = tinta.copy()
        sem[artificial] = 0
        CTX["fechada_sem_artificial"] = cv2.morphologyEx(sem, cv2.MORPH_CLOSE, nucleo)
    if "A" in CTX["variante"]:
        # "A": tira a tinta que so existe por causa do degrau branco da
        # cunha (nao e tinta com a cunha preenchida) E esta em fundo escuro
        # do scanner. A do papel fica, como hoje.
        fora = fora_da_imagem(cinza.shape, CTX["angulo"], 0)
        cheia = preencher(cinza, fora)
        sem_degrau = ORIGINAIS["_mascara_de_tinta_local"](cheia)
        papel = float(np.percentile(cinza[~fora][::7], 90))
        artificial = (tinta > 0) & (sem_degrau == 0) & (cheia < R.ESCURO_DO_SCANNER * papel)
        CTX["artificial"] = int(artificial.sum())
        tinta = tinta.copy()
        tinta[artificial] = 0
    return tinta


def _bordas_solidas(tinta):
    saida = _bordas_solidas_de_verdade(tinta)
    CTX["bruta"], CTX["sem_borda"] = tinta.copy(), saida.copy()
    return saida


def _bordas_solidas_de_verdade(tinta):
    v = CTX["variante"]
    fora = CTX["fora"]
    if "Z" in v:
        tinta = tinta.copy()
        tinta[fora] = 0
    if "U" in v:
        # "U": o apagar de hoje, inteiro (borda solida e risca), MAIS as
        # linhas e colunas que a conta "so na imagem de verdade" acha: nada
        # do que hoje e apagado deixa de ser (ver _riscas_de_verdade)
        com_s = _bordas_solidas_s(tinta, fora, v)
        CTX["linhas_s"] = np.flatnonzero((tinta.sum(axis=1) > 0) & (com_s.sum(axis=1) == 0))
        CTX["colunas_s"] = np.flatnonzero((tinta.sum(axis=0) > 0) & (com_s.sum(axis=0) == 0))
        return ORIGINAIS["_apagar_bordas_solidas"](tinta)
    if "S" not in v:
        return ORIGINAIS["_apagar_bordas_solidas"](tinta)
    return _bordas_solidas_s(tinta, fora, v)


def _bordas_solidas_s(tinta, fora, v):
    limpa = tinta.copy()
    altura, largura = limpa.shape[:2]
    dentro = ~fora
    limite_x, limite_y = int(largura * R.CORTE_MAXIMO), int(altura * R.CORTE_MAXIMO)
    # "D": o fundo escuro do scanner (mais escuro que ESCURO_DO_SCANNER x o
    # papel) conta como borda, mesmo onde o limiar local nao ve tinta (fundo
    # preto liso). `cheia` e so para a conta; quem e apagado e a tinta.
    cheia = limpa > 0
    if "D" in v:
        cinza = CTX["cinza"]
        papel = float(np.percentile(cinza[dentro][::7], 90))
        cheia = cheia | (cinza < R.ESCURO_DO_SCANNER * papel)

    def solida(faixa, vale):
        n = int(vale.sum())
        if n == 0:
            return True
        return float(faixa[vale].sum()) / n >= R.FRACAO_BORDA_SOLIDA

    # "B": a borda reta do scanner fica INCLINADA na pagina endireitada, e a
    # cobertura cai aos poucos de 100% a 0 em comprimento x tan(angulo)
    # linhas. Depois de a caminhada parar (menos de 80%), segue por no maximo
    # essas linhas enquanto a cobertura for de borrao (COBERTURA_DE_BORRAO).
    tan = abs(np.tan(np.radians(CTX["angulo"])))
    mais_x = int(np.ceil(altura * tan)) + 1 if "B" in v else 0
    mais_y = int(np.ceil(largura * tan)) + 1 if "B" in v else 0

    def borrao(faixa, vale):
        n = int(vale.sum())
        return n > 0 and float(faixa[vale].sum()) / n >= R.COBERTURA_DE_BORRAO

    def caminhar(eixo, inicio, passo, limite, mais):
        def pega(i):
            return (cheia[:, i], dentro[:, i]) if eixo == 1 else (cheia[i, :], dentro[i, :])

        def apaga(i):
            if eixo == 1:
                limpa[:, i] = 0
                cheia[:, i] = False
            else:
                limpa[i, :] = 0
                cheia[i, :] = False

        i, andou = inicio, 0
        while andou < limite and solida(*pega(i)):
            apaga(i)
            i += passo
            andou += 1
        if andou:
            extra = 0
            while extra < mais and andou + extra < limite and borrao(*pega(i)):
                apaga(i)
                i += passo
                extra += 1

    caminhar(1, 0, 1, limite_x, mais_x)
    caminhar(1, largura - 1, -1, limite_x, mais_x)
    caminhar(0, 0, 1, limite_y, mais_y)
    caminhar(0, altura - 1, -1, limite_y, mais_y)
    return limpa


def _riscas(tinta):
    saida = _riscas_de_verdade(tinta)
    CTX["limpa"] = saida.copy()
    return saida


def _riscas_de_verdade(tinta):
    v = CTX["variante"]
    if "U" in v:
        limpa = ORIGINAIS["_apagar_riscas_de_dobra"](tinta)
        limpa[CTX["linhas_s"], :] = 0
        limpa[:, CTX["colunas_s"]] = 0
        if "a" in v:
            limpa[CTX["fechada_sem_artificial"] == 0] = 0
        return limpa
    if "R" not in v:
        return ORIGINAIS["_apagar_riscas_de_dobra"](tinta)
    fora = CTX["fora"]
    dentro = ~fora
    limpa = tinta.copy()
    altura, largura = limpa.shape[:2]
    for eixo, tamanho, comprimento in ((1, largura, altura), (0, altura, largura)):
        banda = int(tamanho * R.CORTE_MAXIMO)
        espessura_maxima = max(1, int(tamanho * R.ESPESSURA_DE_RISCA))
        ponta = max(1, int(comprimento * R.PONTA_DA_IMAGEM))
        candidatas = []
        for i in list(range(0, banda)) + list(range(tamanho - banda, tamanho)):
            faixa = limpa[:, i] if eixo == 1 else limpa[i, :]
            vale = dentro[:, i] if eixo == 1 else dentro[i, :]
            n = int(vale.sum())
            if n == 0 or float(faixa[vale].sum()) / n < R.COBERTURA_DE_RISCA:
                continue
            onde = np.flatnonzero(faixa)
            quais = np.flatnonzero(vale)
            if onde[0] <= quais[0] + ponta or onde[-1] >= quais[-1] - ponta:
                candidatas.append(i)
        def cobertura(i: int) -> float:
            faixa = limpa[:, i] if eixo == 1 else limpa[i, :]
            vale = dentro[:, i] if eixo == 1 else dentro[i, :]
            n = int(vale.sum())
            return float(faixa[vale].sum()) / n if n else 0.0

        for grupo in R._agrupar_vizinhas(candidatas):
            if len(grupo) > espessura_maxima:
                continue
            # o borrao, com a cobertura contada so na imagem de verdade
            inicio, fim = grupo[0], grupo[-1]
            limite = espessura_maxima * 2
            while inicio > 0 and (fim - inicio) < limite and cobertura(inicio - 1) >= R.COBERTURA_DE_BORRAO:
                inicio -= 1
            while fim < tamanho - 1 and (fim - inicio) < limite and cobertura(fim + 1) >= R.COBERTURA_DE_BORRAO:
                fim += 1
            for i in range(inicio, fim + 1):
                if eixo == 1:
                    limpa[:, i] = 0
                else:
                    limpa[i, :] = 0
    return limpa


def _pecas(tinta):
    v = CTX["variante"]
    if "P" not in v:
        return ORIGINAIS["_pecas_de_tinta"](tinta)
    altura, largura = tinta.shape[:2]
    n, rot, caixas, _ = cv2.connectedComponentsWithStats(tinta.astype(np.uint8), connectivity=8)
    if n <= 1:
        return np.zeros((0, 5), np.int64)
    perto = cv2.dilate(CTX["fora"].astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    na_cunha = np.zeros(n, bool)
    na_cunha[np.unique(rot[perto])] = True
    x, y, w, h = (caixas[1:, i].astype(np.int64) for i in range(4))
    encosta = (x <= 1) | (y <= 1) | (x + w >= largura - 1) | (y + h >= altura - 1) | na_cunha[1:]
    comprida = (w > R.PECA_GRANDE * largura) | (h > R.PECA_GRANDE * altura)
    fina = np.minimum(w / largura, h / altura) < R.PECA_FINA
    risco = (comprida & fina).astype(np.int64)
    fica = ~encosta
    return np.stack([x[fica], y[fica], (x + w)[fica], (y + h)[fica], risco[fica]], axis=1)


R._mascara_de_tinta_local = _mascara
R._apagar_bordas_solidas = _bordas_solidas
R._apagar_riscas_de_dobra = _riscas
R._pecas_de_tinta = _pecas


VER = None      # pasta onde desenhar as mascaras (ver main)


def desenhar(variante: str, recorte, reta) -> None:
    """A mascara do corte desta variante: preto = tinta que conta; cinza =
    a que foi jogada fora (borda solida, risca); azul claro = cunha do giro;
    vermelho = o corte. Ao lado, a pagina reta reduzida, com o corte."""
    bruta, limpa, fora = CTX["bruta"], CTX["limpa"], CTX["fora"]
    img = np.full(bruta.shape + (3,), 255, np.uint8)
    img[fora] = (255, 220, 170)
    img[bruta > 0] = (170, 170, 170)
    img[limpa > 0] = (0, 0, 0)
    a, l = bruta.shape
    x, y, w, h = recorte
    pagina = cv2.cvtColor(cv2.resize(reta, (l, a), interpolation=cv2.INTER_AREA), cv2.COLOR_GRAY2BGR)
    for q in (img, pagina):
        cv2.rectangle(q, (int(x * l), int(y * a)), (int((x + w) * l) - 1, int((y + h) * a) - 1), (0, 0, 255), 1)
    junto = np.hstack([img, pagina])
    junto = cv2.resize(junto, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    VER.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(VER / f"{CTX['base']}-{variante}.png"), junto)


def medir_variante(inteira, cinza, angulo, pecas, variante: str, base: str = "") -> dict:
    CTX.clear()
    CTX.update(angulo=angulo, variante=variante, base=base,
               margem=(int(variante[variante.index("m") + 1]) if "m" in variante
                       else (0 if variante[0] == "p" else 1)))
    reta = girar(cinza, angulo, "r" if variante[0] == "r" else "b")
    # "bN": o conserto como esta escrito no programa (detectar_bordas com `girada`)
    recorte = R.detectar_bordas(reta, dpi=M.DPI, girada=angulo if "N" in variante else None).tupla
    if VER is not None:
        desenhar(variante, recorte, reta)
    caixa = R.caixa_em_pontos(inteira.shape, recorte)
    final = rotacionar_e_cortar(inteira, angulo, caixa) if caixa else rotacionar(inteira, angulo)
    cz = M._cinza(final)
    fr, enc, f = M._beirada(cz < 0.6 * M._nivel_do_papel(cz))
    c = M._medir_o_conteudo(pecas, recorte, angulo, True, True)
    return {"recorte": [round(float(v), 4) for v in recorte],
            "tamanho_mm": [round(final.shape[1] * 25.4 / M.DPI, 1), round(final.shape[0] * 25.4 / M.DPI, 1)],
            "beirada_escuro": round(fr, 5), "lados_mm": {k: v["mm"] for k, v in M._por_lado(enc, f).items()},
            "tinta_perdida": c["tinta_perdida"], "pecas_partidas": c["pecas_partidas"],
            "pecas_fora": c["pecas_fora"], "folga_mm": c["folga_mm"],
            "cunha_branca": M._cunha_branca(inteira.shape, recorte, angulo, True, True)}


def main() -> int:
    global VER
    if sys.argv[1] == "--ver":      # desenha as mascaras em _tmp/ver/
        VER = RAIZ / "_tmp" / "ver"
        sys.argv.pop(1)
    variantes = sys.argv[1].split(",")
    so = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
    dados = json.loads((PASTA / "dados-verificador.json").read_text(encoding="utf-8"))
    destino = PASTA / "experiencia.json"
    saida = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    for base, d in sorted(dados.items()):
        if "C" not in d or abs(d["C"]["angulo"]) < 0.1 or (so and base not in so):
            continue
        inteira = cv2.imread(str(FINAIS / f"{base}__inteira.jpg"))
        cinza = cv2.cvtColor(inteira, cv2.COLOR_BGR2GRAY)
        angulo = d["C"]["angulo"]
        pecas = M._pecas_do_conteudo(inteira)
        r = saida.setdefault(base, {})
        r["antiga_B"] = {k: d["B"][k] for k in ("tamanho_mm", "beirada_escuro", "tinta_perdida",
                                                 "pecas_partidas", "pecas_fora", "cunha_branca")}
        linha = f"{base:30s} B {100 * d['B']['beirada_escuro']:5.2f}/{100 * d['B']['tinta_perdida']:.2f}"
        for v in variantes:
            r[v] = medir_variante(inteira, cinza, angulo, pecas, v, base)
            q = r[v]
            linha += (f" | {v} {100 * q['beirada_escuro']:5.2f}/{100 * q['tinta_perdida']:.2f}"
                      f"/{q['pecas_partidas']}+{q['pecas_fora']} {q['tamanho_mm'][0]:.0f}x{q['tamanho_mm'][1]:.0f}")
        print(linha, flush=True)
        destino.write_text(json.dumps(saida, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
