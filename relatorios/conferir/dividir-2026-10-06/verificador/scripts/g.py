"""Ajudantes do verificador 2.1 para pilotar a janela (por cima do piloto.py)."""
import time, json
import piloto as P

def geo(expr):
    """Centro (x, y) em pontos fisicos, na janela principal, do widget `expr`."""
    v = P.sonda(f"(lambda w: (w.mapTo(jp, w.rect().center()).x()*jp.devicePixelRatioF(), w.mapTo(jp, w.rect().center()).y()*jp.devicePixelRatioF(), w.isVisible(), w.isEnabled()))({expr})")
    return eval(v)

def clicar_w(expr, espera=0.8, duplo=False):
    x, y, vis, ativo = geo(expr)
    P.clicar_em(P.principal(), int(x), int(y), duplo=duplo)
    time.sleep(espera)
    return vis, ativo

def s(expr):
    return P.sonda(expr)

def esperar(expr, quer="True", limite=300, passo=0.5):
    fim = time.time() + limite
    while time.time() < fim:
        try:
            if P.sonda(expr) == quer:
                return True
        except RuntimeError:
            pass
        time.sleep(passo)
    return False

def foto(nome):
    return P.printar(nome, pasta=P.BASE / "prints")

def itens(filtro=None):
    out = []
    for j in P.mapa():
        for it in j["itens"]:
            t = it["texto"] or ""
            if filtro is None or filtro in t:
                out.append((j["titulo"], it["classe"], t[:70], it.get("ativo"), it.get("marcado"), int(it["x"]), int(it["y"]), int(it["w"]), int(it["h"])))
    return out

def escolher_combo(expr, texto, espera=1.0):
    """Abre a lista (clique nativo) e anda com a seta ate `texto`, Enter (teclas nativas)."""
    clicar_w(expr, espera=0.8)
    pops = [j for j in P.mapa() if j["classe"] != "JanelaPrincipal"]
    alvo = pops[-1]["hwnd"] if pops else P.principal()
    for _ in range(12):
        atual = P.sonda(f"{expr}.view().currentIndex().data()")
        if atual == repr(texto):
            break
        P.tecla(0x28, alvo); time.sleep(0.3)
    P.tecla(0x0D, alvo); time.sleep(espera)
    return P.sonda(f"{expr}.currentText()")

def ir_folha(n, limite=20):
    """Anda com os botoes < > ate a folha de indice n (aba de folhas)."""
    for _ in range(limite):
        atual = int(P.sonda("tc.indice_folha"))
        if atual == n:
            return True
        P.clicar(">" if atual < n else "<", classe="QPushButton", espera=1.0)
    return int(P.sonda("tc.indice_folha")) == n

ESTADO = ("(tc.indice_folha, [(f.dividir, round(f.posicao_corte,4), f.dividir_como) for f in tc.projeto.folhas],"
          " [(p.indice, p.folha, p.metade, p.apagada) for p in tc.projeto.paginas if p.apagada],"
          " len(tc.projeto.paginas_ativas), tc.botao_nao_dividir.text(), tc.botao_nao_dividir.isEnabled(),"
          " tc.combo_jeito_da_folha.currentText(), tc.combo_jeito_da_folha.isEnabled())")

def caixas():
    return [j for j in P.mapa() if j["classe"] != "JanelaPrincipal"]

def responder(botao, espera=1.0):
    for j in caixas():
        for it in j["itens"]:
            if it["classe"] == "QPushButton" and it["texto"] == botao:
                P.clicar_em(j["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2))
                time.sleep(espera)
                return True
    return False

def textos_das_caixas():
    return [[it["texto"] for it in j["itens"] if it["texto"]] for j in caixas()]

def escolher_combo(expr, texto, espera=1.0):
    """Abre a lista (clique nativo) e anda com as setas ate `texto`, Enter (teclas nativas)."""
    alvo_i = int(P.sonda(f"{expr}.findText({texto!r})"))
    clicar_w(expr, espera=0.8)
    pops = [j for j in P.mapa() if j["classe"] != "JanelaPrincipal"]
    alvo = pops[-1]["hwnd"] if pops else P.principal()
    for _ in range(12):
        atual = int(P.sonda(f"{expr}.view().currentIndex().row()"))
        if atual == alvo_i:
            break
        P.tecla(0x28 if atual < alvo_i else 0x26, alvo); time.sleep(0.3)
    P.tecla(0x0D, alvo); time.sleep(espera)
    return P.sonda(f"{expr}.currentText()")
