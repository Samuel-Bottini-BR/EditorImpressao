"""Ajudantes do verificador do "Para revisar" (13/10/2026), por cima do piloto.py e do g.py.

Tudo aqui pilota a janela DE VERDADE com mensagens nativas do Windows (mouse e
teclado), sem tomar o mouse nem o teclado do Samuel; a janela fica fora da tela
e o print sai por PrintWindow. As "sondas" so LEEM o estado do programa (para
saber onde clicar e para conferir o que aconteceu); nenhuma sonda clica nem
muda nada.

Uso (cada chamada e um processo novo; o programa continua aberto entre elas):
    python v.py abrir [maximizada]         abre o programa fora da tela
    python v.py livro <pdf>                clica na area de abrir e escolhe o PDF
    python v.py mapa [filtro]              lista o que ha na tela
    python v.py foto <nome>                print da janela principal
    python v.py fechar
"""
import ctypes
import ctypes.wintypes as W
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import piloto as P  # noqa: E402
import g  # noqa: E402

PRINTS = P.BASE / "trabalho" / "prints"


def tamanho(maximizada=False):
    """Poe a janela fora da tela no tamanho do Kaique (1280 x 657) ou no
    tamanho que ela teria maximizada neste monitor (area de trabalho)."""
    h = P.principal()
    P.u32.ShowWindow(h, 4)
    if maximizada:
        area = W.RECT()
        P.u32.SystemParametersInfoW(0x30, 0, ctypes.byref(area), 0)
        aw, ah = area.right - area.left, area.bottom - area.top
    else:
        aw, ah = round(P.LOGICO[0] * P.ESCALA), round(P.LOGICO[1] * P.ESCALA)
    for _ in range(3):
        r = W.RECT(); P.u32.GetWindowRect(h, ctypes.byref(r)); l, t, rr, b = P.moldura(h)
        P.u32.SetWindowPos(h, 0, -32000, -32000, aw + (r.right - r.left) - (rr - l),
                           ah + (r.bottom - r.top) - (b - t), 0x4 | 0x10)
        time.sleep(0.4)
    l, t, rr, b = P.moldura(h)
    return rr - l, b - t


def abrir(maximizada=False):
    h = P.iniciar(); time.sleep(3)
    return h, tamanho(maximizada)


def foto(nome, hwnd=None):
    # O primeiro PrintWindow depois de abrir o programa (ou de mudar o tamanho
    # da janela) pode devolver a imagem VELHA da janela (a tela inicial, com
    # uma faixa preta a direita): achado em 13/10, 11 prints sairam assim. Por
    # isso tira duas vezes e fica com a segunda, e confere a faixa preta.
    P.printar(nome, h=hwnd)
    time.sleep(0.8)
    d, w, h = P.printar(nome, h=hwnd)
    if hwnd is None:
        import numpy as np
        from PIL import Image
        im = np.asarray(Image.open(d).convert("L"))
        if im[60:-10, im.shape[1] - 60:].max() < 12:
            time.sleep(2.0)
            d, w, h = P.printar(nome, h=hwnd)
    return str(d), w, h


def foto_da_caixa(nome, titulo):
    """Print de uma janela filha (caixa de dialogo), pelo titulo."""
    j = P.janela(titulo)
    if not j:
        raise LookupError(f"caixa {titulo!r} nao esta aberta")
    return foto(nome, j["hwnd"])


def itens(filtro=None, classes=None):
    out = []
    for j in P.mapa():
        for it in j["itens"]:
            t = it["texto"] or ""
            if (filtro is None or filtro.lower() in t.lower()) and (classes is None or it["classe"] in classes):
                out.append((j["titulo"], it["classe"], t[:110], it.get("ativo"), it.get("marcado"),
                            int(it["x"]), int(it["y"]), int(it["w"]), int(it["h"])))
    return out


def clicar(texto, exato=True, n=0, titulo=None, classe=None, espera=0.8):
    """Clique nativo no meio do widget que tem esse texto."""
    return P.clicar(texto, titulo=titulo, classe=classe, exato=exato, n=n, espera=espera)[1]


def clicar_w(expr, espera=0.8):
    return g.clicar_w(expr, espera=espera)


def s(expr, espera=60.0):
    return P.sonda(expr, espera=espera)


def esperar(expr, quer="True", limite=120, passo=0.5):
    return g.esperar(expr, quer, limite, passo)


def estado_da_pagina():
    """So leitura: pagina da vez, avisos, forca, botoes do aviso, texto da faixa."""
    return s("(lambda p: dict(pagina=tc.indice_pagina+1, alertas=list(p.alertas), pendentes=list(p.alertas_pendentes), "
             "aceitos=list(getattr(p,'alertas_aceitos',[])), forca=p.forca_preto, antes=p.forca_antes_do_reforco, "
             "desfeito=p.reforco_desfeito, fora=p.misto_fora_do_texto, em_branco=p.em_branco, apagada=p.apagada, "
             "revisada=p.revisada, filtro=p.filtro, "
             "b1=(tc.botoes_de_sugestao['filtro'].text() if tc.botoes_de_sugestao['filtro'].isVisible() else None), "
             "b2=(tc.botoes_de_sugestao_2['filtro'].text() if tc.botoes_de_sugestao_2['filtro'].isVisible() else None), "
             "contador=tc.botao_alertas.text(), painel=tc.coluna_paineis.para_revisar.cabecalho.text() if hasattr(tc,'coluna_paineis') else None"
             "))(tc.projeto.paginas[tc.indice_pagina])")


def _barra_da_tira():
    """(x, y, w, h) fisicos da barra de rolagem horizontal da tira, na janela."""
    return eval(s("(lambda sb, d: (sb.mapTo(jp, sb.rect().topLeft()).x()*d, sb.mapTo(jp, sb.rect().topLeft()).y()*d, "
                  "sb.width()*d, sb.height()*d, sb.value(), sb.maximum(), sb.pageStep()))"
                  "(tc.tira.rolagem.horizontalScrollBar(), jp.devicePixelRatioF())"))


def _mini_visivel(n):
    return eval(s(f"(lambda sb, m, vp: (sb.value() <= m.x() and m.x() + m.width() <= sb.value() + vp.width()))"
                  f"(tc.tira.rolagem.horizontalScrollBar(), tc.tira._miniaturas[{n - 1}], tc.tira.rolagem.viewport())"))


def ir_pagina(n, espera=1.5):
    """Vai para a pagina n (contando de 1) como a pessoa: arrasta a barra de
    rolagem da tira de miniaturas ate a miniatura aparecer e clica nela (tudo
    com mensagens nativas de mouse). As sondas so leem onde a barra e a
    miniatura estao."""
    h = P.principal()
    for _ in range(8):
        if _mini_visivel(n):
            break
        x, y, w, hh, val, mx, page = _barra_da_tira()
        alvo = eval(s(f"(lambda m, vp: max(0, m.x() - vp.width()//2))(tc.tira._miniaturas[{n - 1}], tc.tira.rolagem.viewport())"))
        alvo = min(mx, alvo)
        comp = max(w * page / (mx + page), 20 * P.ESCALA)
        de = x + (w - comp) * (val / mx if mx else 0) + comp / 2
        para = x + (w - comp) * (alvo / mx if mx else 0) + comp / 2
        P.arrastar_em(h, int(de), int(y + hh / 2), int(para), int(y + hh / 2), passos=20)
        time.sleep(0.8)
    if not _mini_visivel(n):
        raise RuntimeError(f"nao consegui trazer a miniatura {n} para a vista")
    g.clicar_w(f"tc.tira._miniaturas[{n - 1}]", espera=espera)
    return int(s("tc.indice_pagina")) + 1


def medida_pronta():
    """So leitura: a medida por tras da pagina da vez (na resolucao do PDF) ja chegou?"""
    return s("tc.previas.chave_da_medida(tc.indice_pagina) in tc.previas._cache") == "True"


def esperar_medida(limite=180):
    t0 = time.time()
    while time.time() - t0 < limite:
        if medida_pronta():
            time.sleep(1.5)
            return round(time.time() - t0, 1)
        time.sleep(0.5)
    return None


def novo_livro(pdf, so_as_letras=True, jeito=None, limite=900):
    """Abre um livro NOVO como a pessoa: clica na area "Arraste o PDF...", a
    caixa de escolher arquivo responde `pdf` (o lancador troca so essa caixa do
    Windows), responde "Nao" a caixa do fundo separado se ela vier, marca Preto
    e branco e "So as letras" e clica em Conferir. Tudo clique nativo.
    Devolve os segundos ate a tela de conferir ficar pronta."""
    (P.CANAL / "resposta_abrir.txt").write_text(str(pdf), encoding="utf-8")
    g.clicar_w("jp.tela_inicio.area", espera=2)
    for _ in range(120):
        if any(x[2] == "Conferir" for x in itens(classes=("QPushButton",))):
            break
        time.sleep(1)
    time.sleep(1)
    if P.janela("Fundo separado"):
        g.responder("Não, deixar como está"); time.sleep(1)
    clicar("Preto e branco", classe="QRadioButton", espera=1.5)
    # a tela "O que fazer" lembra a escolha do livro anterior da sessao: so
    # clica na caixinha se ela nao estiver do jeito pedido (le o estado, clica nativo)
    marcada = [x[4] for x in itens(classes=("QCheckBox",)) if x[2] == "Só as letras"][0]
    if bool(marcada) != bool(so_as_letras):
        clicar("Só as letras", classe="QCheckBox", espera=1.5)
    if so_as_letras:
        if jeito:
            clicar(jeito, classe="QPushButton", espera=1.0)
    t0 = time.time()
    clicar("Conferir", classe="QPushButton", espera=2)
    ok = esperar("tc.projeto is not None and tc._pronta() and tc.isVisible()", limite=limite, passo=2)
    time.sleep(3)
    if not ok:
        raise RuntimeError("a tela de conferir nao abriu")
    aba("Filtro"); time.sleep(2)
    return round(time.time() - t0)


def curto():
    """Estado da pagina da vez em poucas palavras (so leitura)."""
    e = eval(estado_da_pagina())
    return (f"p{e['pagina']} pend={e['pendentes']} aceitos={e['aceitos']} forca={e['forca']} antes={e['antes']} "
            f"fora={e['fora']} branco={e['em_branco']} apagada={e['apagada']} rev={e['revisada']} "
            f"b1={e['b1']!r} b2={e['b2']!r} | {e['contador']}")


def faixa():
    """O texto da faixa de aviso da aba que esta na frente (so leitura)."""
    return s("tc.rotulo_faixa.text() if hasattr(tc,'rotulo_faixa') else [w.text() for w in tc.faixa.findChildren(QtWidgets.QLabel) if w.isVisible()]")


def passo(nome, espera_medida=0):
    if espera_medida:
        print("  medida:", esperar_medida(espera_medida), "s")
    print(" ", curto())
    print("  foto:", Path(foto(nome)[0]).name)


def botao_da_caixa(titulo, texto, parte=False, espera=1.5):
    """Clique nativo num botao de uma caixa de dialogo (pelo titulo da caixa)."""
    for j in P.mapa():
        if j["classe"] == "JanelaPrincipal" or (titulo and titulo not in j["titulo"]):
            continue
        for it in j["itens"]:
            if it["classe"] == "QPushButton" and (texto in it["texto"] if parte else it["texto"] == texto):
                P.clicar_em(j["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2))
                time.sleep(espera)
                return True
    return False


def caixas():
    return [(j["titulo"], [it["texto"] for it in j["itens"] if it["texto"]]) for j in P.mapa()
            if j["classe"] != "JanelaPrincipal"]


def linhas_da_lista():
    """As linhas da janela dos avisos aberta (so leitura)."""
    return eval(s("[w for w in QtWidgets.QApplication.topLevelWidgets() if type(w).__name__=='JanelaDosAvisos' and w.isVisible()][0].linhas()"))


def painel():
    """Os botoes do painel "Para revisar" (texto e posicao), so leitura."""
    return eval(s("(lambda pr, d: [pr.cabecalho.text()] + [(b.text(), int(b.mapTo(jp, b.rect().center()).x()*d), int(b.mapTo(jp, b.rect().center()).y()*d), b.visibleRegion().isEmpty()) "
                  "for b in pr.findChildren(QtWidgets.QPushButton) if b is not pr.cabecalho])"
                  "([w for w in tc.findChildren(QtWidgets.QWidget) if type(w).__name__=='PainelParaRevisar'][0], jp.devicePixelRatioF())"))


_COLUNA = "[w for w in tc.findChildren(QtWidgets.QWidget) if type(w).__name__=='ColunaDePaineis'][0]"
_PAINEL = "[w for w in tc.findChildren(QtWidgets.QWidget) if type(w).__name__=='PainelParaRevisar'][0]"


def clicar_no_painel(texto, n=0, parte=False, espera=2.0):
    """Clique nativo num botao do painel "Para revisar" (o n-esimo com esse
    texto). Se ele estiver fora da vista, arrasta antes a barra de rolagem da
    coluna dos paineis (arrasto nativo). As sondas so leem posicoes."""
    cond = f"({texto!r} in b.text())" if parte else f"(b.text() == {texto!r})"
    alvo = f"[b for b in {_PAINEL}.findChildren(QtWidgets.QPushButton) if {cond}][{n}]"
    h = P.principal()
    for _ in range(10):
        dentro = eval(s(f"(lambda c, b: (lambda y: 4 <= y and y + b.height() <= c.viewport().height() - 4)(b.mapTo(c.viewport(), b.rect().topLeft()).y()))({_COLUNA}, {alvo})"))
        if dentro:
            break
        x, y, w, hh, val, mx, page, falta = eval(s(
            f"(lambda c, b, d: (lambda sb: (sb.mapTo(jp, sb.rect().topLeft()).x()*d, sb.mapTo(jp, sb.rect().topLeft()).y()*d, sb.width()*d, sb.height()*d, "
            f"sb.value(), sb.maximum(), sb.pageStep(), b.mapTo(c.widget(), b.rect().center()).y() - c.viewport().height()//2))(c.verticalScrollBar()))({_COLUNA}, {alvo}, jp.devicePixelRatioF())"))
        novo = max(0, min(mx, falta))
        comp = max(hh * page / (mx + page), 20 * P.ESCALA)
        de = y + (hh - comp) * (val / mx if mx else 0) + comp / 2
        para = y + (hh - comp) * (novo / mx if mx else 0) + comp / 2
        P.arrastar_em(h, int(x + w / 2), int(de), int(x + w / 2), int(para), passos=15)
        time.sleep(0.8)
    g.clicar_w(alvo, espera=espera)


def contagem():
    return s("(tc.botao_alertas.text(), " + _PAINEL + ".cabecalho.text(), dict(__import__('collections').Counter(a for p in tc.projeto.paginas for a in p.alertas_pendentes)))")


def historico():
    return s("[a.descricao for a in tc.acoes.feitas]")


def ctrl_z(vezes=1):
    for _ in range(vezes):
        P.tecla("Z", mods=("ctrl",)); time.sleep(1.5)


def continuar_projeto(parte_do_nome, limite=600, rotulo=None):
    """Na tela inicial, clica (nativo) no botao "continuar" do cartao do livro
    cujo nome contem `parte_do_nome`, e espera a tela de conferir."""
    # digita o nome na caixa "procurar pelo nome" (clique e teclas nativos): o
    # cartao do livro sobe para a primeira fila
    g.clicar_w("jp.tela_inicio.busca", espera=0.8)
    for letra in parte_do_nome:
        P.tecla(letra); time.sleep(0.15)
    time.sleep(1.5)
    j = [x for x in P.mapa() if x["classe"] == "JanelaPrincipal"][0]
    rot = [it for it in j["itens"] if it["classe"] == "QLabel" and (rotulo or parte_do_nome).lower() in (it["texto"] or "").lower()][0]
    bot = [it for it in j["itens"] if it["classe"] == "QPushButton" and it["texto"] == "continuar"
           and rot["x"] - 10 <= it["x"] <= rot["x"] + rot["w"] + 10 and 0 < it["y"] - rot["y"] < 160 * P.ESCALA][0]
    t0 = time.time()
    P.clicar_em(j["hwnd"], int(bot["x"] + bot["w"] / 2), int(bot["y"] + bot["h"] / 2)); time.sleep(3)
    for _ in range(limite):
        if caixas():
            return ("caixa", caixas())
        if s("jp.telas.currentWidget() is tc and tc.projeto is not None and tc._pronta()") == "True":
            break
        time.sleep(1)
    time.sleep(3)
    return round(time.time() - t0)


def escolher_motivo_na_lista(parte):
    """Na janela dos avisos aberta, escolhe um motivo na caixa "Mostrar"
    (clique nativo na caixa e setas nativas ate o item)."""
    JA = "[w for w in QtWidgets.QApplication.topLevelWidgets() if type(w).__name__=='JanelaDosAvisos' and w.isVisible()][0]"
    textos = eval(s(f"[{JA}.combo_motivo.itemText(i) for i in range({JA}.combo_motivo.count())]"))
    alvo = [i for i, t in enumerate(textos) if parte in t]
    if not alvo:
        return None
    j = [x for x in P.mapa() if x["classe"] == "JanelaDosAvisos"][0]
    combo = [it for it in j["itens"] if it["classe"] == "QComboBox"][0]
    atual = int(s(f"{JA}.combo_motivo.currentIndex()"))
    P.clicar_em(j["hwnd"], int(combo["x"] + combo["w"] / 2), int(combo["y"] + combo["h"] / 2)); time.sleep(1)
    pops = [x for x in P.mapa() if x["classe"] not in ("JanelaPrincipal", "JanelaDosAvisos")]
    h = pops[-1]["hwnd"] if pops else j["hwnd"]
    for _ in range(abs(alvo[0] - atual)):
        P.tecla(0x28 if alvo[0] > atual else 0x26, h); time.sleep(0.3)
    P.tecla(0x0D, h); time.sleep(1)
    return s(f"{JA}.combo_motivo.currentText()")


def erros_log():
    return P.erros_log()


def aba(nome, espera=1.5):
    return clicar(nome, classe="aba", espera=espera)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "abrir":
        print(abrir(len(sys.argv) > 2 and sys.argv[2] == "maximizada"))
    elif cmd == "tamanho":
        print(tamanho(len(sys.argv) > 2 and sys.argv[2] == "maximizada"))
    elif cmd == "mapa":
        for linha in itens(sys.argv[2] if len(sys.argv) > 2 else None):
            print(linha)
    elif cmd == "foto":
        print(foto(sys.argv[2]))
    elif cmd == "fechar":
        print(P.fechar())
    elif cmd == "sonda":
        print(s(sys.argv[2]))
    elif cmd == "estado":
        print(estado_da_pagina())
    elif cmd == "janelas":
        print(P.janelas())
