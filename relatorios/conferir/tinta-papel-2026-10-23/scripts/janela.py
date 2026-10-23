"""Verificador tp23 (23/10/2026): os quatro botões da "Tinta com a cor" na janela de verdade
(os dois da cor, A e B, e os dois do papel, "papel branco" e "papel como o resto da página").

O programa de verdade (JanelaPrincipal) da worktree, fora da tela; cliques e arrastos por
mensagens nativas do Windows (PostMessage no hwnd); prints por PrintWindow; fecha com WM_CLOSE.
Toda janela nova (caixa, menu, "Ver de perto") vai para fora da tela antes de aparecer
(base._por_fora_da_tela).

Fase 1 (livro novo, Horas 13 do gabarito, caminho de fábrica: a análise gira, endireita e corta):
  filtro Original (cartão) -> Retângulo (trilha) -> Propriedades (ícone) -> "tinta com a cor, papel
  branco" -> os quatro botões -> "papel como o resto da página" -> área 1 (A, papel da página) ->
  "cor escurecida" -> área 2 (B, papel da página) -> "papel branco" + "cor como no livro" -> área 3
  (A, papel branco) -> "Ver de perto" em Original e em Preto e branco -> "letra e traço" (somem) ->
  WM_CLOSE.
Fase 2 (o programa aberto de novo, mesmo livro): as três áreas voltam com o jeito delas?
Uso: python janela.py <worktree> <saida> <fase> [antes]

Ajuste da resposta 11 (23/10/2026, código d4c820b): o botão agora se chama "manter a cor da tinta";
confere o texto do botão, o aviso "Área escolhida: ..." e a linha "Marcado: ..." (sem "papel branco").
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base  # noqa: E402

WT, SAIDA, FASE = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3])
ANTES = len(sys.argv) > 4 and sys.argv[4] == "antes"
TRAB = SAIDA.parent / ("trab-" + SAIDA.name)
base.preparar(WT, str(TRAB), limpar=(FASE == 1))
LIVRO = TRAB / "Horas 13 (copia).pdf"
if not LIVRO.exists():
    shutil.copy2(Path(WT) / "gabarito" / "paginas" / "horas_p013.pdf", LIVRO)   # o gabarito nunca é aberto

from PySide6.QtWidgets import QApplication  # noqa: E402
from core.selecao import LETRA, TINTA_COR  # noqa: E402

N = [0]
AREA1 = (0.25, 0.13, 0.75, 0.205)      # TABLE / DE CE QUI EST
AREA2 = (0.25, 0.215, 0.75, 0.255)     # CONTENU EN CE LIVRE
AREA3 = (0.22, 0.30, 0.78, 0.40)       # o começo do texto


def foto(j, nome):
    N[0] += 1
    base.esperar(2.5)
    base.print_window(j, SAIDA / f"f{FASE}-{N[0]:02d}-{nome}.png")


def tirar_caixas():
    for _ in range(10):
        m = QApplication.activeModalWidget()
        if m is None:
            return
        print("  (caixa aberta:", type(m).__name__, getattr(m, "windowTitle", lambda: "")(), ") -> reject", flush=True)
        m.reject()
        base.esperar(1)


def abrir(j):
    j.abrir_livro(str(LIVRO))
    base.esperar(3)
    j.analisar()
    tela = j.tela_conferir
    for _ in range(300):
        if tela.projeto is not None:
            break
        base.esperar(1)
    base.esperar(6)
    tirar_caixas()
    base.esperar(3)
    return tela


def clicar_na_trilha(j, tela, grupo):
    ret = tela.trilha.retangulos()[grupo]
    base.clique(j, tela.trilha, ret.center())
    base.esperar(2)


def abrir_propriedades(j, tela):
    col = tela.paineis.icones
    if tela.paineis.aberto != "props":
        base.clique(j, col, col.retangulos()["props"].center())
        base.esperar(1.5)
    base.conferir(tela.paineis.aberto == "props", "o painel Propriedades abriu pelo clique no ícone")


def escolher_filtro(j, tela, chave, rotulo):
    clicar_na_trilha(j, tela, 13)                 # "Os quatro filtros"
    cartao = tela.cartoes.get(chave)
    base.conferir(cartao is not None and cartao.isVisible(), f"o cartão do filtro {chave} está à vista")
    # clicar no cartão escolhe o filtro E abre a "Ver de perto" (janela que espera): um
    # relógio dentro dela tira a foto e fecha com WM_CLOSE (ela já nasce fora da tela)
    from PySide6.QtCore import QTimer

    def fechar_ver_de_perto():
        m = QApplication.activeModalWidget()
        if m is not None:
            base.esperar(1.5)
            base.print_window(m, SAIDA / f"f{FASE}-ver-de-perto-{rotulo}.png")
            base.user32.PostMessageW(int(m.winId()), base.WM_CLOSE, 0, 0)
        else:
            QTimer.singleShot(1000, fechar_ver_de_perto)
    QTimer.singleShot(6000, fechar_ver_de_perto)
    base.clique(j, cartao)
    base.esperar(8)
    tirar_caixas()
    base.conferir(tela.projeto.paginas[tela.indice_pagina].filtro == chave, f"a página ficou com o filtro {chave}")


def _vis(d):
    import shiboken6
    return [b.isVisible() for b in d.values() if shiboken6.isValid(b)]


def visiveis(mc):
    """Os botões da cor e do papel à vista? (o painel se refaz a cada escolha)"""
    return _vis(getattr(mc, "botoes_da_cor", {})) + _vis(getattr(mc, "botoes_do_papel", {}))


def jeitos(tela):
    return [(round(r.pontos[0][1], 3), r.tinta_escurecida, getattr(r, "papel_da_pagina", "(não existe)"))
            for r in tela.editor_selecao.selecao.regioes if r.tipo == TINTA_COR]


def arrastar_area(j, tela, x0, y0, x1, y1):
    ed = tela.editor_selecao
    a, b = ed._para_tela(x0, y0), ed._para_tela(x1, y1)
    base.arrastar(j, ed, a, b, passos=14)
    base.esperar(4)


def fase1(j, tela):
    base.conferir(tela.projeto is not None, "o livro abriu e a análise terminou")
    print("  filtro da página ao abrir:", tela.projeto.paginas[tela.indice_pagina].filtro, flush=True)
    foto(j, "livro-aberto")
    escolher_filtro(j, tela, "original", "original-sem-area")
    clicar_na_trilha(j, tela, 4)                  # Retângulo
    base.conferir("ret" in str(tela.barra_opcoes.ferramenta), f"a ferramenta da vez é o Retângulo ({tela.barra_opcoes.ferramenta})")
    abrir_propriedades(j, tela)
    mc = tela.paineis.marcar_como
    base.conferir(not any(visiveis(mc)), "antes de escolher \"manter a cor da tinta\", os botões da cor e do papel não aparecem")
    foto(j, "marcar-como-de-fabrica")
    base.clique(j, mc.botoes[TINTA_COR])
    base.esperar(1.5)
    base.conferir(mc.tipo == TINTA_COR, "\"manter a cor da tinta\" ficou escolhida")
    if not ANTES:
        texto = mc.botoes[TINTA_COR].text()
        base.conferir(texto == "manter a cor da tinta", f"o botão se chama \"manter a cor da tinta\" (resposta 11): \"{texto}\"")
    if ANTES:
        base.conferir(not hasattr(mc, "botoes_do_papel"), "(antes) não existem os botões do papel")
        print("  botões da cor (antes):", [b.text() for b in getattr(mc, "botoes_da_cor", {}).values()], flush=True)
        foto(j, "original-tinta-com-cor-escolhida")
        arrastar_area(j, tela, *AREA1)
        print("  áreas:", jeitos(tela), flush=True)
        foto(j, "original-area-marcada")
        escolher_filtro(j, tela, "original", "original-com-area")
        return
    cor = [b.text() for b in mc.botoes_da_cor.values()]
    papel = [b.text() for b in mc.botoes_do_papel.values()]
    base.conferir(cor == ["cor como no livro", "cor escurecida"] and papel == ["papel branco", "papel como o resto da página"]
                  and all(visiveis(mc)) and len(visiveis(mc)) == 4,
                  f"aparecem os quatro botões, à vista: {cor} + {papel}")
    base.conferir(mc.papel_da_pagina is False and tela.editor_selecao.papel_da_pagina is False
                  and mc.escurecer is False and tela.editor_selecao.tinta_escurecida is False,
                  "de fábrica: \"cor como no livro\" e \"papel branco\" (painel e editor)")
    ga, gb = mc.botoes_do_papel[False].geometry(), mc.botoes_do_papel[True].geometry()
    base.conferir(gb.top() > ga.top() and gb.left() == ga.left(), f"os dois do papel ficam um sob o outro ({ga.getRect()} / {gb.getRect()})")
    largura = mc.botoes_do_papel[True].width()
    precisa = mc.botoes_do_papel[True].sizeHint().width()
    base.conferir(largura >= precisa, f"\"papel como o resto da página\" cabe inteiro no botão ({largura} >= {precisa} px)")
    foto(j, "original-quatro-botoes-de-fabrica")
    base.clique(j, mc.botoes_do_papel[True])
    base.esperar(1.5)
    mc = tela.paineis.marcar_como
    base.conferir(mc.papel_da_pagina is True and tela.editor_selecao.papel_da_pagina is True,
                  "clicar em \"papel como o resto da página\" escolhe o papel da página (painel e editor)")
    base.conferir(all(visiveis(mc)) and len(visiveis(mc)) == 4, "os quatro botões continuam à vista depois do clique")
    base.conferir(mc.escurecer is False, "a cor não mudou (continua \"cor como no livro\")")
    foto(j, "original-papel-da-pagina-escolhido")
    arrastar_area(j, tela, *AREA1)
    js = jeitos(tela)
    base.conferir(js and js[-1][1:] == (False, True), f"área 1 saiu A + papel da página: {js}")
    base.clique(j, mc.botoes_da_cor[True])
    base.esperar(1.5)
    mc = tela.paineis.marcar_como
    base.conferir(mc.escurecer is True and mc.papel_da_pagina is True, "\"cor escurecida\" escolhida, papel da página continua")
    arrastar_area(j, tela, *AREA2)
    js = jeitos(tela)
    base.conferir(len(js) >= 2 and js[-1][1:] == (True, True) and js[-2][1:] == (False, True),
                  f"área 2 saiu B + papel da página; a 1 não mudou: {js}")
    foto(j, "original-areas-1-e-2")
    base.clique(j, mc.botoes_do_papel[False])
    base.esperar(1.5)
    mc = tela.paineis.marcar_como
    base.clique(j, mc.botoes_da_cor[False])
    base.esperar(1.5)
    mc = tela.paineis.marcar_como
    base.conferir(mc.escurecer is False and mc.papel_da_pagina is False
                  and tela.editor_selecao.tinta_escurecida is False and tela.editor_selecao.papel_da_pagina is False,
                  "de volta a \"cor como no livro\" + \"papel branco\" (painel e editor)")
    arrastar_area(j, tela, *AREA3)
    js = jeitos(tela)
    base.conferir(len(js) >= 3 and [x[1:] for x in js[-3:]] == [(False, True), (True, True), (False, False)],
                  f"área 3 saiu A + papel branco; as outras não mudaram: {js}")
    marcado = tela.aviso_marcacao.text()
    print("  linha embaixo da aba Marcar:", marcado, flush=True)
    base.conferir(marcado.startswith("Marcado:") and "manter a cor da tinta" in marcado and "papel branco" not in marcado,
                  f"a linha \"Marcado:\" usa o nome novo e não diz \"papel branco\": \"{marcado}\"")
    foto(j, "original-tres-areas")
    ed = tela.editor_selecao
    idx = ed.escolher_area(((AREA1[0] + AREA1[2]) / 2, (AREA1[1] + AREA1[3]) / 2))
    aviso = tela.aviso_marcacao.text()
    print("  aviso ao escolher a área 1:", idx, aviso, flush=True)
    base.conferir(idx is not None and ed.selecao.regioes[idx].tipo == TINTA_COR
                  and aviso.startswith("Área escolhida: manter a cor da tinta.") and "papel branco" not in aviso,
                  f"escolhendo a área 1, o aviso diz o nome novo: \"{aviso}\"")
    foto(j, "original-area-1-escolhida")
    ed.escolhida = None
    ed.update()
    escolher_filtro(j, tela, "original", "original-tres-areas")
    escolher_filtro(j, tela, "preto_e_branco", "pb-tres-areas")
    foto(j, "pb-tres-areas")
    clicar_na_trilha(j, tela, 4)
    abrir_propriedades(j, tela)
    mc = tela.paineis.marcar_como
    vis = visiveis(mc)
    base.conferir(mc.tipo == TINTA_COR and vis == [True] * 4, f"no Preto e branco, os quatro botões também aparecem ({vis})")
    foto(j, "pb-quatro-botoes")
    base.clique(j, mc.botoes[LETRA])
    base.esperar(1.5)
    mc = tela.paineis.marcar_como
    vis = visiveis(mc)
    base.conferir(mc.tipo == LETRA and not any(vis), f"escolhendo \"letra e traço\", os quatro botões somem ({vis})")
    foto(j, "pb-letra-sem-botoes")
    base.clique(j, mc.botoes[TINTA_COR])
    base.esperar(1.5)
    mc = tela.paineis.marcar_como
    base.conferir(mc.papel_da_pagina is False and tela.editor_selecao.papel_da_pagina is False,
                  "voltando a \"manter a cor da tinta\", o papel escolhido por último (papel branco) continua")


def fase2(j, tela):
    pg = tela.projeto.paginas[tela.indice_pagina]
    do_projeto = [(r.tinta_escurecida, getattr(r, "papel_da_pagina", None)) for r in pg.obter_selecao().regioes if r.tipo == TINTA_COR]
    base.conferir(do_projeto[-3:] == [(False, True), (True, True), (False, False)], f"no projeto aberto de novo, as áreas da página: {do_projeto}")
    clicar_na_trilha(j, tela, 4)
    js = jeitos(tela)
    print("  áreas ao abrir de novo:", js, flush=True)
    base.conferir([x[1:] for x in js][-3:] == [(False, True), (True, True), (False, False)],
                  f"fechando e abrindo o programa, as três áreas voltam com o jeito delas: {js}")
    pasta = Path(j.resumo.pasta) if getattr(j, "resumo", None) else None
    achou = None
    for cand in ([pasta] if pasta else []) + list((TRAB / "projetos").glob("*")):
        if cand and (cand / "projeto.json").is_file():
            achou = cand / "projeto.json"
            break
    if achou:
        # o programa grava a marcação em duas listas da página (selecao e zonas_na_folha): confere as duas
        dados = json.loads(achou.read_text(encoding="utf-8"))
        pg0 = dados["paginas"][0]
        for lista in ("selecao", "zonas_na_folha"):
            jts = [(r.get("tinta_escurecida", False), r.get("papel_da_pagina", False))
                   for r in (pg0.get(lista) or []) if isinstance(r, dict) and r.get("tipo") == "tinta_cor"]
            base.conferir(jts[-3:] == [(False, True), (True, True), (False, False)],
                          f"o projeto.json guarda o jeito das três áreas em {lista}: {jts}")
    else:
        base.conferir(False, "achei o projeto.json gravado")
    abrir_propriedades(j, tela)
    foto(j, "reaberto")
    escolher_filtro(j, tela, "original", "reaberto-original")


j = base.nova_janela(1280, 800)
tela = abrir(j)
try:
    (fase1 if FASE == 1 else fase2)(j, tela)
except Exception as e:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    base.conferir(False, f"o roteiro parou: {e!r}")
base.esperar(3)
base.fechar(j)
base.gravar_resultados(SAIDA / f"fase{FASE}")
