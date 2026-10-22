"""Verificador, 20/10/2026: ajudantes para a TELA NOVA (layout aprovado, sem abas), por cima do v.py.
Mesma regra: cliques e teclas nativos; as sondas so leem. Uso: python n.py "<codigo python>" (executa
com v, P e n importados; cada chamada e um processo novo, o programa continua aberto)."""
import sys
import time

import v

P = v.P


def novo_livro(pdf, so_as_letras=True, jeito=None, limite=900):
    (P.CANAL / "resposta_abrir.txt").write_text(str(pdf), encoding="utf-8")
    v.g.clicar_w("jp.tela_inicio.area", espera=2)
    for _ in range(120):
        if any(x[2] == "Conferir" for x in v.itens(classes=("QPushButton",))):
            break
        time.sleep(1)
    time.sleep(1)
    if P.janela("Fundo separado"):
        v.g.responder("Não, deixar como está"); time.sleep(1)
    v.clicar("Preto e branco", classe="QRadioButton", espera=1.5)
    achadas = []
    for _ in range(20):
        achadas = [x[4] for x in v.itens(classes=("QCheckBox",)) if x[2] == "Só as letras"]
        if achadas:
            break
        time.sleep(0.5)
    if achadas and bool(achadas[0]) != bool(so_as_letras):
        v.clicar("Só as letras", classe="QCheckBox", espera=1.5)
    if so_as_letras and jeito:
        v.clicar(jeito, classe="QPushButton", espera=1.0)
    t0 = time.time()
    v.clicar("Conferir", classe="QPushButton", espera=2)
    ok = v.esperar("tc.projeto is not None and tc._pronta() and tc.isVisible()", limite=limite, passo=2)
    time.sleep(3)
    if not ok:
        raise RuntimeError("a tela de conferir nao abriu")
    return round(time.time() - t0)


def clicar_print(x, y, espera=2.0):
    """Clique nativo no ponto (x, y) do PRINT da janela (que inclui a barra de titulo: 40 pontos a mais em y)."""
    P.clicar_em(P.principal(), int(x), int(y) - 40); time.sleep(espera)


def painel_clicar(texto, n=0, espera=2.0):
    """Clique nativo num botao VISIVEL do painel "Para revisar" (posicao lida pelo v.painel())."""
    achados = [b for b in v.painel()[1:] if b[0] == texto and not b[3]]
    x, y = achados[n][1], achados[n][2]
    P.clicar_em(P.principal(), int(x), int(y)); time.sleep(espera)


def botoes():
    return [x for x in v.itens(classes=("QPushButton", "QToolButton")) if x[5] > 0 and x[6] > 0]


if __name__ == "__main__":
    n = sys.modules[__name__]
    exec(sys.argv[1])
