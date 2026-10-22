"""Verificador tc23 (23/10/2026): os dois botões da "Tinta com a cor" na janela de verdade.

O programa de verdade (JanelaPrincipal) da worktree, fora da tela; cliques e arrastos por
mensagens nativas do Windows (PostMessage no hwnd); prints por PrintWindow; fecha com WM_CLOSE.
Toda janela nova (caixa, menu) vai para fora da tela antes de aparecer (base._por_fora_da_tela).

Fase 1 (livro novo, Horas 13 do gabarito, caminho de fábrica: a análise gira, endireita e corta):
  filtro da página Preto e branco (cartão clicado) -> ferramenta Retângulo (trilha) -> painel
  Propriedades (ícone) -> "tinta com a cor, papel branco" -> confere os dois botões -> "cor
  escurecida" -> arrasta um retângulo no título -> "cor como no livro" -> outro retângulo ->
  filtro Original (cartão) -> volta ao Retângulo: os dois botões continuam? -> WM_CLOSE.
Fase 2 (o programa aberto de novo, mesmo livro): as duas áreas voltam com o jeito delas?
Uso: python janela.py <worktree> <saida> <fase> [antes]
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

from PySide6.QtCore import QPoint  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402
from core.selecao import TINTA_COR  # noqa: E402

N = [0]


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
    # fase 2: o mesmo livro aberto de novo (o programa acha o projeto salvo pela assinatura
    # do arquivo e traz o trabalho gravado)
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


def escolher_filtro(j, tela, chave):
    clicar_na_trilha(j, tela, 13)                 # "Os quatro filtros"
    cartao = tela.cartoes.get(chave)
    base.conferir(cartao is not None and cartao.isVisible(), f"o cartão do filtro {chave} está à vista")
    # clicar no cartão escolhe o filtro E abre a "Ver de perto" (janela que espera): um
    # relógio dentro dela tira a foto e fecha com WM_CLOSE (ela já nasce fora da tela)
    from PySide6.QtCore import QTimer

    def fechar_ver_de_perto():
        m = QApplication.activeModalWidget()
        if m is not None:
            base.print_window(m, SAIDA / f"f{FASE}-ver-de-perto-{chave}.png")
            base.user32.PostMessageW(int(m.winId()), base.WM_CLOSE, 0, 0)
        else:
            QTimer.singleShot(1000, fechar_ver_de_perto)
    QTimer.singleShot(5000, fechar_ver_de_perto)
    base.clique(j, cartao)
    base.esperar(6)
    tirar_caixas()
    base.conferir(tela.projeto.paginas[tela.indice_pagina].filtro == chave, f"a página ficou com o filtro {chave}")


def visiveis(mc):
    """Os dois botões à vista? (lista vazia se não existem agora: o painel se refaz a cada escolha)"""
    import shiboken6
    return [b.isVisible() for b in getattr(mc, "botoes_da_cor", {}).values() if shiboken6.isValid(b)]


def jeitos(tela):
    return [(round(r.pontos[0][0], 2), r.tinta_escurecida if hasattr(r, "tinta_escurecida") else "(não existe)")
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
    escolher_filtro(j, tela, "preto_e_branco")
    foto(j, "preto-e-branco")
    clicar_na_trilha(j, tela, 4)                  # Retângulo
    base.conferir(tela.barra_opcoes.ferramenta == "retangulo" or "ret" in str(tela.barra_opcoes.ferramenta),
                  f"a ferramenta da vez é o Retângulo ({tela.barra_opcoes.ferramenta})")
    abrir_propriedades(j, tela)
    mc = tela.paineis.marcar_como
    base.conferir(not any(visiveis(mc)),
                  "antes de escolher a tinta com a cor, os dois botões não aparecem")
    foto(j, "marcar-como-de-fabrica")
    base.clique(j, mc.botoes[TINTA_COR])
    base.esperar(1.5)
    base.conferir(mc.tipo == TINTA_COR, "\"tinta com a cor, papel branco\" ficou escolhida")
    if ANTES:
        base.conferir(not hasattr(mc, "botoes_da_cor"), "(antes) não existem os dois botões")
        foto(j, "pb-tinta-com-cor-escolhida")
        arrastar_area(j, tela, 0.25, 0.13, 0.75, 0.26)
        print("  áreas:", jeitos(tela), flush=True)
        foto(j, "pb-area-marcada")
        return
    bot = getattr(mc, "botoes_da_cor", {})
    textos = [b.text() for b in bot.values()]
    base.conferir(textos == ["cor como no livro", "cor escurecida"] and all(b.isVisible() for b in bot.values()),
                  f"aparecem os dois botões, à vista: {textos}")
    base.conferir(bot[False].property("escolhido") in (True, None) and tela.editor_selecao.tinta_escurecida is False,
                  "de fábrica está o A (\"cor como no livro\"); o editor também (tinta_escurecida False)")
    foto(j, "pb-dois-botoes-A-de-fabrica")
    base.clique(j, mc.botoes_da_cor[True])
    base.esperar(1.5)
    base.conferir(mc.escurecer is True and tela.editor_selecao.tinta_escurecida is True,
                  "clicar em \"cor escurecida\" escolhe a B (painel e editor)")
    base.conferir(all(b.isVisible() for b in mc.botoes_da_cor.values()), "os dois botões continuam à vista depois do clique")
    foto(j, "pb-B-escolhida")
    arrastar_area(j, tela, 0.25, 0.13, 0.75, 0.205)            # TABLE + DE CE QUI EST
    base.conferir(jeitos(tela)[-1:] and jeitos(tela)[-1][1] is True, f"a área desenhada saiu B: {jeitos(tela)}")
    foto(j, "pb-area-B-marcada")
    base.clique(j, mc.botoes_da_cor[False])
    base.esperar(1.5)
    base.conferir(mc.escurecer is False and tela.editor_selecao.tinta_escurecida is False,
                  "clicar em \"cor como no livro\" volta para a A")
    arrastar_area(j, tela, 0.25, 0.215, 0.75, 0.255)           # CONTENU EN CE LIVRE
    js = jeitos(tela)
    base.conferir(len(js) >= 2 and js[-2][1] is True and js[-1][1] is False,
                  f"a área nova saiu A e a já marcada continua B: {js}")
    foto(j, "pb-area-B-e-area-A")
    # filtro Original: os botões continuam aparecendo? (pergunta aberta 9, mostrar os dois casos)
    escolher_filtro(j, tela, "original")
    foto(j, "original-com-as-areas")
    clicar_na_trilha(j, tela, 4)
    abrir_propriedades(j, tela)
    mc = tela.paineis.marcar_como
    vis = visiveis(mc)
    base.conferir(mc.tipo == TINTA_COR and vis == [True, True],
                  f"no Original, com a tinta com a cor escolhida, os dois botões também aparecem ({vis})")
    foto(j, "original-dois-botoes")
    base.conferir([x[1] for x in jeitos(tela)][-2:] == [True, False], f"no Original as áreas guardam o jeito: {jeitos(tela)}")
    # escolhe outro tipo: os botões somem
    from core.selecao import LETRA
    base.clique(j, mc.botoes[LETRA])
    base.esperar(1.5)
    vis = visiveis(mc)
    base.conferir(mc.tipo == LETRA and not any(vis), f"escolhendo \"letra e traço\", os dois botões somem ({vis})")
    foto(j, "original-outro-tipo-sem-botoes")
    base.clique(j, mc.botoes[TINTA_COR])
    base.esperar(1.5)
    base.conferir(mc.escurecer is False and tela.editor_selecao.tinta_escurecida is False,
                  "voltando à tinta com a cor, o jeito escolhido por último (A) continua")
    escolher_filtro(j, tela, "preto_e_branco")
    foto(j, "pb-final")


def fase2(j, tela):
    pg = tela.projeto.paginas[tela.indice_pagina]
    do_projeto = [r.tinta_escurecida for r in pg.obter_selecao().regioes if r.tipo == TINTA_COR]
    base.conferir(do_projeto[-2:] == [True, False], f"no projeto aberto de novo, as áreas da página: {do_projeto}")
    clicar_na_trilha(j, tela, 4)                  # a tela de marcar (o editor nasce aqui)
    js = jeitos(tela)
    print("  áreas ao abrir de novo:", js, flush=True)
    base.conferir([x[1] for x in js][-2:] == [True, False],
                  f"fechando e abrindo o programa, as duas áreas voltam com o jeito delas (B e A): {js}")
    pasta = Path(j.resumo.pasta) if getattr(j, "resumo", None) else None
    if pasta:
        dados = json.loads((pasta / "projeto.json").read_text(encoding="utf-8"))
        texto = json.dumps(dados)
        base.conferir("tinta_escurecida" in texto, "o projeto.json guarda o campo tinta_escurecida")
    abrir_propriedades(j, tela)
    foto(j, "reaberto")


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
