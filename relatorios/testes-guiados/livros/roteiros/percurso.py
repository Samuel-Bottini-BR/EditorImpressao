"""Testes com os livros (verificador, 23/10/2026): o caminho inteiro do Kaique num livro, na
janela de verdade, fora da tela do Samuel e com uma pasta de dados própria.

  1. tela inicial -> clique do Windows em "Abrir um PDF" -> a janela de escolher arquivo (a do
     Qt, não a do Windows, para poder ficar fora da tela) recebe o caminho da CÓPIA do livro;
  2. "Marque o que você quer fazer": caixinhas por clique do Windows, como no arquivo de opções;
  3. "Conferir": cada ferramenta da coluna da esquerda (clique do Windows no ícone), várias
     páginas (as com aviso e algumas comuns), o painel "Para revisar" (clique do Windows na
     linha), os botões laranja da faixa, "está certo", arrastar a linha/o retângulo/a bolinha,
     e o desfazer (clique do Windows no botão de baixo);
  4. "Confirmar e processar" -> "Antes de processar" -> "continuar assim mesmo" -> onde salvar
     -> "Processar" -> "Ficou pronto!"; o PDF de saída é aberto e algumas páginas desenhadas;
  5. "montar para imprimir em A4 (com margens)..." -> "gravar o arquivo para imprimir" (a janela
     de salvar do Qt recebe o nome). NUNCA "imprimir agora" nem "mandar para a impressora".

Ir para uma página por número é feito por chamada direta (tc.ir_para_pagina, o mesmo do Ctrl+G);
dito no relatório. Tudo o que acontece vai para <brutos>/log.txt e <brutos>/estado.json.
Uso: python percurso.py <worktree> <config.json>"""
import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base  # noqa: E402

WT, CFG = sys.argv[1], json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
RAIZ = Path(CFG["raiz"])                 # D:\...\testes-livros-saida\<curto>
BRUTOS = RAIZ / "prints"
SAIDA_PDF = RAIZ / "saida"
base.preparar(WT, str(RAIZ / "trab"))
BRUTOS.mkdir(parents=True, exist_ok=True)
SAIDA_PDF.mkdir(parents=True, exist_ok=True)
LOG = BRUTOS / "log.txt"
LOG.write_text("", encoding="utf-8")
ESTADO: dict = {"livro": CFG["acervo"], "eventos": []}

from PySide6.QtCore import QPoint, Qt, QTimer  # noqa: E402
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog, QLineEdit,  # noqa: E402
                               QMessageBox, QPushButton, QWidget)

base.app.setAttribute(Qt.AA_DontUseNativeDialogs, True)
N_PRINT = [0]


def anota(texto):
    print("  · " + texto, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + texto + "\n")


def foto(janela, nome):
    N_PRINT[0] += 1
    return base.print_window(janela, BRUTOS / f"{N_PRINT[0]:03d}-{nome}.png")


def gravar_estado():
    (BRUTOS / "estado.json").write_text(json.dumps(ESTADO, ensure_ascii=False, indent=1), encoding="utf-8")


# --- vigia: caixa de aviso inesperada (QMessageBox) ----------------------------------------
VISTAS = set()


def vigiar():
    for w in QApplication.topLevelWidgets():
        if isinstance(w, QMessageBox) and w.isVisible() and id(w) not in VISTAS:
            VISTAS.add(id(w))
            anota(f"CAIXA DE AVISO apareceu: título '{w.windowTitle()}' texto '{w.text()}' "
                  f"detalhe '{w.informativeText()}' botões {[b.text() for b in w.buttons()]}")
            ESTADO["eventos"].append({"caixa": w.text(), "botoes": [b.text() for b in w.buttons()]})

            def responder(w=w):
                base.print_window(w, BRUTOS / f"caixa-{len(VISTAS)}.png", so_cliente=False)
                b = w.defaultButton() or (w.buttons()[0] if w.buttons() else None)
                if b is not None:
                    anota(f"  respondi a caixa com '{b.text()}' (o botão já escolhido)")
                    base.clique(w, b)
                    base.esperar(0.5)
                if w.isVisible():
                    w.done(0)
            QTimer.singleShot(1500, responder)


relogio = QTimer()
relogio.timeout.connect(vigiar)
relogio.start(700)


def esperar_ate(cond, limite, passo=1.0):
    t0 = time.time()
    while not cond() and time.time() - t0 < limite:
        base.esperar(passo)
    return time.time() - t0


# --- 1. tela inicial e abrir ---------------------------------------------------------------
LIVRO = RAIZ / "trab" / CFG["copia"]
if CFG.get("trecho"):
    import fitz
    a, b = CFG["trecho"]
    with fitz.open(base.ACERVO / CFG["acervo"]) as orig:
        novo = fitz.open()
        novo.insert_pdf(orig, from_page=a - 1, to_page=b - 1)
        novo.save(LIVRO, garbage=0, deflate=False)
        novo.close()
    anota(f"trecho: folhas {a} a {b} do original, numa cópia")
else:
    import shutil
    shutil.copy2(base.ACERVO / CFG["acervo"], LIVRO)

j = base.nova_janela(1536, 800)
foto(j, "inicio")


def no_dialogo_de_abrir(w):
    campo = w.findChild(QLineEdit, "fileNameEdit") or w.findChild(QLineEdit)
    campo.setText(str(LIVRO))
    base.esperar(0.3)
    abrir = [b for b in w.findChildren(QPushButton) if b.isVisible() and b.isEnabled()
             and b.text().replace("&", "").lower() in ("open", "abrir")]
    anota(f"janela de escolher o PDF: '{w.windowTitle()}'; botões {[b.text() for b in w.findChildren(QPushButton) if b.isVisible()]}")
    if abrir:
        base.clique(w, abrir[0])
    else:
        w.accept()


base.quando_abrir_janela(QFileDialog, "abrir-pdf", BRUTOS, LOG, depois=no_dialogo_de_abrir, fechar=False, espera_ms=1200)
base.clique(j, j.tela_inicio.area)               # clique do Windows no "Abrir um PDF"
esperar_ate(lambda: j.telas.currentWidget() is j.tela_opcoes, 60)
base.esperar(2)
op = j.tela_opcoes
base.conferir(j.telas.currentWidget() is op, "abrir o PDF pelo 'Abrir um PDF' leva às caixinhas")
foto(j, "opcoes-de-fabrica")

# --- 2. as caixinhas -------------------------------------------------------------------------


def marcar(cx, ligar=True):
    if cx.isChecked() != ligar:
        op.rolagem.ensureWidgetVisible(cx, 50, 50)
        base.esperar(0.4)
        base.clique(j, cx, cx.rect().topLeft() + QPoint(9, 10))
        base.esperar(0.6)
    ok = cx.isChecked() == ligar
    if not ok:
        anota(f"a caixinha '{cx.text()}' não ficou {'marcada' if ligar else 'desmarcada'} com o clique")
    return ok


CX = {"dividir": op.cx_dividir, "cortar_sobra": op.cx_cortar_sobra, "limpar": op.cx_limpar,
      "endireitar": op.cx_endireitar, "cortar": op.cx_cortar, "cortar_conteudo": op.cx_cortar_pelo_conteudo,
      "borda_preta": op.cx_borda_preta, "margens": op.cx_margens, "cadernos": op.cx_cadernos}
for chave, ligar in CFG["caixas"].items():
    if chave in CX:
        marcar(CX[chave], ligar)
if CFG["caixas"].get("limpar", True):
    from core import filtros as F
    filtro = {"original": F.ORIGINAL, "pb": F.PRETO_E_BRANCO, "melhorar": F.MELHORAR, "magico": F.MAGICO_PRO}[CFG.get("filtro", "original")]
    r = op.radios_de_filtro[filtro]
    op.rolagem.ensureWidgetVisible(r, 50, 50); base.esperar(0.4)
    base.clique(j, r); base.esperar(1)
    base.conferir(r.isChecked(), f"filtro do livro escolhido: {r.text()}")
    if CFG.get("so_as_letras"):
        marcar(op.escolhas_misto.caixa, True)
    for chave in ("achar_gravuras", "tem_fotos"):
        if chave in CFG["caixas"]:
            marcar(getattr(op, "cx_" + chave), CFG["caixas"][chave])
base.esperar(1)
op.rolagem.verticalScrollBar().setValue(0); base.esperar(0.4)
foto(j, "opcoes-escolhidas")
op.rolagem.widget().grab().save(str(BRUTOS / "opcoes-escolhidas-inteira.png"))
p = j.projeto
ESTADO["opcoes"] = {"resumo": op.resumo.text(), "dividir": p.dividir_folhas, "limpar": p.limpar,
                    "endireitar": p.endireitar, "cortar": p.cortar_bordas,
                    "filtro": getattr(p, "filtro_padrao", None)}
anota(f"frase de baixo das opções: '{op.resumo.text()}'")
anota(f"projeto: {ESTADO['opcoes']}")

# --- 3. conferir --------------------------------------------------------------------------------
base.clique(j, op.botao_conferir)
base.esperar(3)
foto(j, "olhando-o-livro")
dur = esperar_ate(lambda: j.telas.currentWidget() is j.tela_conferir, 1800)
anota(f"'Conferir' -> tela de conferir em {dur:.0f} s")
ESTADO["analise_s"] = round(dur)
base.esperar(8)
tc = j.tela_conferir
P = tc.projeto


def situacao(rotulo):
    try:
        pg = P.paginas[tc.indice_pagina]
        fl = P.folhas[tc.indice_folha]
        botoes = [b.text() for b in (tc.botao_sugestao, tc.botao_sugestao_2, tc.botao_sugestao_3) if b.isVisible()]
        t = (f"{rotulo}: aba {tc.aba_atual}; folha {tc.indice_folha + 1}, página {tc.indice_pagina + 1}; "
             f"faixa '{tc.texto_faixa.text()}' botões {botoes}; rodapé '{tc.rotulo_da_pagina.text()}' / "
             f"'{tc.rotulo_do_livro.text()}'; alto '{tc.botao_alertas.text()}'; "
             f"pág: filtro={pg.filtro} recorte={tuple(round(x, 3) for x in pg.recorte) if pg.recorte else None} "
             f"angulo_manual={pg.angulo_manual} apagada={pg.apagada} em_branco={getattr(pg, 'em_branco', False)} "
             f"alertas={list(pg.alertas_pendentes)}; folha: dividir={fl.dividir} corte={round(fl.posicao_corte, 3) if fl.posicao_corte is not None else None}")
    except Exception:  # noqa: BLE001
        t = rotulo + ": (erro ao ler) " + traceback.format_exc().splitlines()[-1]
    anota(t)
    return t


def pendentes():
    return [(pg.indice, list(pg.alertas_pendentes)) for pg in P.paginas if not pg.apagada and pg.alertas_pendentes]


ESTADO["conferir"] = {"abas": list(tc._abas_ativas), "paginas": len(P.paginas), "folhas": len(P.folhas),
                      "pendentes_inicio": len(pendentes()), "alto": tc.botao_alertas.text(),
                      "rodape": tc.rotulo_do_livro.text()}
por_motivo = {}
for i, al in pendentes():
    for a in al:
        por_motivo.setdefault(a, []).append(i + 1)
ESTADO["conferir"]["por_motivo"] = {k: v for k, v in por_motivo.items()}
anota(f"conferir: {ESTADO['conferir']}")
foto(j, "conferir-abriu")
situacao("ao abrir")

tr = tc.trilha
from ui.widgets.trilha_agrupada import GRUPOS  # noqa: E402

# livro escaneado de lado: girar todas as folhas pelo bloco "Girar a folha" do Propriedades
if CFG.get("girar"):
    from core import girar as G
    giro = {"direita": G.GIRO_DIREITA, "esquerda": G.GIRO_ESQUERDA}[CFG["girar"]]
    tc.paineis.abrir("props"); base.esperar(2)
    bg = tc.barra_girar
    bg.definir_alcance(G.ALCANCE_TODAS); base.esperar(0.5)     # a lista "aplicar em" (direto)
    foto(j, "girar-antes")
    base.clique(j, bg.botoes_de_giro[giro])                    # clique do Windows no botão
    dur_giro = esperar_ate(lambda: P.folhas[0].rotacao != 0 and P.folhas[-1].rotacao != 0, 600, 1)
    base.esperar(6)
    anota(f"GIRAR ¼ à {CFG['girar']} em todas: rotação folha 1 = {P.folhas[0].rotacao}, última = "
          f"{P.folhas[-1].rotacao} ({dur_giro:.0f} s); dúvidas agora {tc.botao_alertas.text()}")
    foto(j, "girar-depois")
    tc.paineis.fechar()
VIVOS = {}
for indice, ret in tr.retangulos().items():
    g = GRUPOS[indice]
    if g != "-" and tr._ferramentas_vivas(g):
        VIVOS[g[0]] = (indice, ret)
anota(f"ícones da esquerda: {list(VIVOS)}")
ESTADO["conferir"]["icones"] = list(VIVOS)


def ferramenta(nome):
    if nome not in VIVOS:
        anota(f"ferramenta '{nome}' não está na coluna da esquerda")
        return False
    base.clique(j, tr, VIVOS[nome][1].center())
    base.esperar(3)
    return True


def ir(indice_pagina, espera=4):
    tc.ir_para_pagina(indice_pagina)
    base.esperar(espera)


# páginas para olhar: as do config, a primeira, a última e as 4 primeiras com aviso
avisadas = [i for i, _ in pendentes()]
olhar = sorted(set([0, len(P.paginas) - 1] + [x - 1 for x in CFG.get("olhar", [])] + avisadas[:4]))
olhar = [i for i in olhar if 0 <= i < len(P.paginas)]
anota(f"páginas que vou olhar em cada ferramenta: {[i + 1 for i in olhar]}")
painel_ic = tc.paineis.icones

for nome in ("dividir", "cortar", "endireitar", "filtros"):
    if not ferramenta(nome):
        continue
    for i in olhar:
        ir(i, 5 if nome in ("endireitar", "filtros") else 3)
        situacao(f"{nome}, página {i + 1}")
        foto(j, f"{nome}-p{i + 1}")

# --- arrastar e desfazer em cada ferramenta ------------------------------------------------------
from ui.tela_conferir import ABA_ANGULO, ABA_BORDAS, ABA_CORTE  # noqa: E402


def desfazer_embaixo(rotulo):
    base.clique(j, tc.botao_desfazer_embaixo)
    base.esperar(3)
    return situacao(f"depois do desfazer ({rotulo})")


alvo = olhar[1] if len(olhar) > 1 else 0
if ferramenta("dividir"):
    ir(alvo)
    vis = tc.visualizadores[ABA_CORTE]
    antes = P.folhas[tc.indice_folha].posicao_corte
    a = vis._area
    x = a.left() + int(vis.posicao_corte * a.width())
    base.arrastar(j, vis, QPoint(x, a.center().y()), QPoint(x + 40, a.center().y()))
    base.esperar(2)
    depois = P.folhas[tc.indice_folha].posicao_corte
    anota(f"DIVIDIR arrastar a linha 40 px: corte {antes} -> {depois}")
    foto(j, "dividir-arrastado")
    desfazer_embaixo("dividir")
    anota(f"DIVIDIR desfazer: corte voltou para {P.folhas[tc.indice_folha].posicao_corte} (antes {antes})")
    ESTADO.setdefault("desfazer", {})["dividir"] = [antes, depois, P.folhas[tc.indice_folha].posicao_corte]

if ferramenta("cortar"):
    ir(alvo, 5)
    vis = tc.visualizadores[ABA_BORDAS]
    antes = P.paginas[tc.indice_pagina].recorte
    r = vis._retangulo_recorte()
    base.arrastar(j, vis, r.topLeft(), r.topLeft() + QPoint(30, 30))
    base.esperar(2)
    depois = P.paginas[tc.indice_pagina].recorte
    anota(f"CORTAR arrastar o canto 30 px: recorte {antes} -> {depois}")
    foto(j, "cortar-arrastado")
    desfazer_embaixo("cortar")
    ESTADO.setdefault("desfazer", {})["cortar"] = [antes, depois, P.paginas[tc.indice_pagina].recorte]

if ferramenta("endireitar"):
    ir(alvo, 6)
    vis = tc.visualizadores[ABA_ANGULO]
    antes = P.paginas[tc.indice_pagina].angulo_manual
    c = vis.centro_da_alca().toPoint()
    base.arrastar(j, vis, c, c + QPoint(0, 40))
    base.esperar(3)
    depois = P.paginas[tc.indice_pagina].angulo_manual
    anota(f"ENDIREITAR arrastar a bolinha 40 px: ângulo {antes} -> {depois}")
    foto(j, "endireitar-arrastado")
    desfazer_embaixo("endireitar")
    ESTADO.setdefault("desfazer", {})["endireitar"] = [antes, depois, P.paginas[tc.indice_pagina].angulo_manual]

# --- marcar (gravura/cor) ---------------------------------------------------------------------
if CFG.get("marcar") and ferramenta("retangulo"):
    ir(CFG["marcar"] - 1, 6)
    ed = tc.editor_selecao
    antes = len(getattr(P.paginas[tc.indice_pagina], "selecao", []) or [])
    foto(j, f"marcar-antes-p{CFG['marcar']}")
    w, h = ed.width(), ed.height()
    base.arrastar(j, ed, QPoint(int(w * .35), int(h * .3)), QPoint(int(w * .65), int(h * .6)))
    base.esperar(3)
    depois = len(getattr(P.paginas[tc.indice_pagina], "selecao", []) or [])
    situacao("depois de marcar um retângulo")
    anota(f"MARCAR retângulo: seleções na página {antes} -> {depois}")
    foto(j, f"marcar-depois-p{CFG['marcar']}")
    tc.paineis.abrir("props"); base.esperar(2)
    foto(j, "marcar-propriedades")
    desfazer_embaixo("marcar")
    anota(f"MARCAR desfazer: seleções {len(getattr(P.paginas[tc.indice_pagina], 'selecao', []) or [])}")
    tc.paineis.fechar()

# --- Para revisar: painel, linhas, botões da faixa, desfazer ------------------------------------
ferramenta("filtros") or ferramenta("cortar") or ferramenta("endireitar") or ferramenta("dividir")
ret_rev = painel_ic.retangulos().get("revisar")
if ret_rev is not None:
    base.clique(j, painel_ic, ret_rev.center())
    base.esperar(2)
    pr = tc.paineis.para_revisar
    anota(f"painel Para revisar aberto={tc.paineis.aberto}; frase '{pr.frase.text()}'; linhas {pr.lista.count()}")
    foto(j, "para-revisar-aberto")
    feitos = 0
    tratadas = set()
    for _volta in range(12):
        if feitos >= CFG.get("resolver", 3):
            break
        item = None
        for k in range(pr.lista.count()):
            if pr.lista.item(k).data(Qt.UserRole) not in tratadas:
                item = pr.lista.item(k)
                break
        if item is None:
            break
        nome_linha = item.text()
        tratadas.add(item.data(Qt.UserRole))
        pr.lista.scrollToItem(item); base.esperar(0.3)
        rect = pr.lista.visualItemRect(item)
        base.clique(j, pr.lista.viewport(), rect.center())
        base.esperar(4)
        situacao(f"clique na linha '{nome_linha}' do Para revisar")
        foto(j, f"revisar-{nome_linha.replace(' ', '')}")
        visiveis = [b for b in (tc.botao_sugestao, tc.botao_sugestao_2, tc.botao_sugestao_3) if b.isVisible()]
        if not visiveis:
            anota("  nenhum botão laranja na faixa para esta linha")
            continue
        n_antes = len(pendentes())
        b = visiveis[0]
        rotulo = b.text()
        base.clique(j, b)
        base.esperar(4)
        n_depois = len(pendentes())
        situacao(f"depois do botão '{rotulo}'")
        foto(j, f"revisar-depois-{rotulo.replace(' ', '-')[:20]}")
        anota(f"BOTÃO DA FAIXA '{rotulo}': páginas com dúvida {n_antes} -> {n_depois}")
        ESTADO.setdefault("botoes_da_faixa", []).append([nome_linha, rotulo, n_antes, n_depois])
        feitos += 1
        if feitos == 1:
            desfazer_embaixo(f"botão '{rotulo}'")
            n_desf = len(pendentes())
            anota(f"DESFAZER do botão '{rotulo}': páginas com dúvida {n_desf} (antes do botão {n_antes})")
            foto(j, "revisar-depois-do-desfazer")
            ESTADO.setdefault("desfazer", {})["botao_da_faixa"] = [n_antes, n_depois, n_desf]
            if b.isVisible() and b.text() == rotulo:
                base.clique(j, b)                    # refaz o conserto pelo botão
                base.esperar(3)
    # "está certo" numa página com aviso
    if pendentes():
        i0 = pendentes()[0][0]
        ir(i0)
        n_antes = len(pendentes())
        base.clique(j, tc.botao_esta_certo); base.esperar(2)
        anota(f"'está certo' na página {i0 + 1} (com aviso): dúvidas {n_antes} -> {len(pendentes())}")
        situacao("depois do 'está certo'")
        foto(j, "esta-certo")
    tc.paineis.fechar()

# a fila do filtro (cartõezinhos) numa página comum
ret_f = painel_ic.retangulos().get("filtro")
if ret_f is not None and "filtros" in VIVOS:
    ir(olhar[-1] if olhar else 0)
    base.clique(j, painel_ic, ret_f.center()); base.esperar(6)
    foto(j, "painel-filtro")
    tc.paineis.fechar()

ESTADO["conferir"]["pendentes_fim"] = len(pendentes())
gravar_estado()

# --- 4. processar ---------------------------------------------------------------------------------
from ui.janela_confirmar import JanelaConfirmar  # noqa: E402
from ui.janela_dos_avisos import JanelaDosAvisos  # noqa: E402
NOME_SAIDA = CFG["curto"] + " (pronto).pdf"


VISTO = {"avisos": False, "confirmar": False}


def na_confirmar(w):
    VISTO["confirmar"] = True
    anota(f"janela de confirmar: '{w.windowTitle()}', destino sugerido {w.caminho}")
    base.gravar_textos(w, LOG, "janela de confirmar")
    w.destino.definir(SAIDA_PDF, NOME_SAIDA)
    base.esperar(0.8)
    base.print_window(w, BRUTOS / "processar-2-confirmar.png", so_cliente=False)
    base.clique(w, w.botao_processar)


def nos_avisos(w):
    VISTO["avisos"] = True
    anota(f"a janela 'Antes de processar' apareceu {time.time() - T_CLIQUE:.0f} s depois do clique")
    anota(f"antes de processar: '{w.windowTitle()}' com {w.lista.count()} linhas; frase '{w._frase()}'")
    ESTADO["antes_de_processar"] = {"linhas": w.lista.count(), "frase": w._frase()}
    base.quando_abrir_janela(JanelaConfirmar, "processar-2b", BRUTOS, LOG, depois=na_confirmar, fechar=False)
    base.clique(w, w.botao_continuar)


base.quando_abrir_janela(JanelaDosAvisos, "processar-1-antes", BRUTOS, LOG, depois=nos_avisos, fechar=False)
if not pendentes():
    base.quando_abrir_janela(JanelaConfirmar, "processar-2b", BRUTOS, LOG, depois=na_confirmar, fechar=False)
anota(f"botão 'Confirmar e processar': visível={tc.botao_processar.isVisible()} ligado={tc.botao_processar.isEnabled()}")
T_CLIQUE = time.time()
base.clique(j, tc.botao_processar)
esperar_ate(lambda: VISTO["avisos"] or VISTO["confirmar"], 30, 0.5)
if not (VISTO["avisos"] or VISTO["confirmar"]):
    bp = tc.botao_processar
    cpt = bp.mapTo(j, bp.rect().center())
    debaixo = j.childAt(cpt)
    anota(f"PROBLEMA: o clique do Windows em 'Confirmar e processar' não abriu nada em 30 s. "
          f"No ponto do clique ({cpt.x()},{cpt.y()}) está {type(debaixo).__name__} '{getattr(debaixo, 'text', lambda: '')()}'; "
          f"página {tc.indice_pagina + 1}, aba {tc.aba_atual}, painel {tc.paineis.aberto}, janela ativa modal "
          f"{QApplication.activeModalWidget()}, popup {QApplication.activePopupWidget()}, mouse preso {QWidget.mouseGrabber()}")
    foto(j, "processar-nada-abriu")
    ESTADO["clique_processar_falhou"] = True
    QTimer.singleShot(0, bp.click)          # o mesmo botão, pelo Qt
    esperar_ate(lambda: VISTO["avisos"] or VISTO["confirmar"], 120, 0.5)
anota(f"depois do clique em 'Confirmar e processar', a primeira janela apareceu em {time.time() - T_CLIQUE:.0f} s")
ESTADO["espera_confirmar_s"] = round(time.time() - T_CLIQUE)
anota(f"janelas vistas: {VISTO}")
base.esperar(8)
foto(j, "processando")
t0 = time.time()
limite = CFG.get("limite_processar", 3600)
while j.telas.currentWidget() is not j.tela_final and time.time() - t0 < limite:
    base.esperar(3)
dur = time.time() - t0
anota(f"processar levou {dur:.0f} s; chegou na 'Ficou pronto!'? {j.telas.currentWidget() is j.tela_final}")
ESTADO["processar_s"] = round(dur)
base.esperar(3)
foto(j, "ficou-pronto")
base.gravar_textos(j, LOG, "ficou pronto")
tf = j.tela_final
ESTADO["pronto"] = {"nome": tf.nome.text(), "detalhe": tf.detalhe.text(), "local": tf.local.text()}

import fitz  # noqa: E402
saidas = sorted(SAIDA_PDF.glob("*.pdf"))
esperadas = sum(1 for pg in P.paginas if not pg.apagada)
for arq in saidas:
    with fitz.open(arq) as d:
        anota(f"PDF gerado: {arq.name}, {d.page_count} páginas, {arq.stat().st_size / 1e6:.1f} MB "
              f"(páginas não apagadas no projeto: {esperadas}; apagadas: {len(P.paginas) - esperadas})")
        ESTADO["saida"] = {"arquivo": str(arq), "paginas": d.page_count, "mb": round(arq.stat().st_size / 1e6, 1),
                           "esperadas": esperadas}
gravar_estado()

# --- 5. montar para imprimir ------------------------------------------------------------------------
if tf.botao_montar.isEnabled() and saidas:
    base.clique(j, tf.botao_montar)
    base.esperar(5)
    dlg = getattr(tf, "dialogo_impressao", None)
    if dlg is not None and dlg.isVisible():
        base.print_window(dlg, BRUTOS / "montar-1.png", so_cliente=False)
        base.gravar_textos(dlg, LOG, "montar para imprimir")
        destino_imp = SAIDA_PDF / (CFG["curto"] + " - para imprimir.pdf")

        def no_salvar(w):
            campo = w.findChild(QLineEdit, "fileNameEdit") or w.findChild(QLineEdit)
            campo.setText(str(destino_imp))
            base.esperar(0.3)
            bot = [b for b in w.findChildren(QPushButton) if b.isVisible() and b.isEnabled()
                   and b.text().replace("&", "").lower() in ("save", "salvar")]
            anota(f"janela de salvar: '{w.windowTitle()}'; botões {[b.text() for b in w.findChildren(QPushButton) if b.isVisible()]}")
            base.clique(w, bot[0]) if bot else w.accept()

        base.quando_abrir_janela(QFileDialog, "montar-salvar", BRUTOS, LOG, depois=no_salvar, fechar=False, espera_ms=1200)
        base.clique(dlg, dlg.botao_gravar)
        t0 = time.time()
        esperar_ate(lambda: destino_imp.exists() and dlg.botao_gravar.isEnabled(), 1800, 2)
        base.esperar(3)
        anota(f"montar levou {time.time() - t0:.0f} s; estado: '{dlg.estado.text()}'; avisos: "
              f"'{dlg.avisos.toPlainText() if dlg.avisos.isVisible() else ''}'")
        base.print_window(dlg, BRUTOS / "montar-2-pronto.png", so_cliente=False)
        ESTADO["montar"] = {"estado": dlg.estado.text(), "existe": destino_imp.exists()}
        if destino_imp.exists():
            with fitz.open(destino_imp) as d:
                r = d[0].rect
                anota(f"arquivo para imprimir: {d.page_count} páginas, {r.width / 72 * 2.54:.1f} x {r.height / 72 * 2.54:.1f} cm")
                ESTADO["montar"]["paginas"] = d.page_count
        dlg.reject()
    else:
        anota("a janela 'montar para imprimir' não abriu")
else:
    anota(f"'montar para imprimir' cinza ou sem PDF: {tf.botao_montar.toolTip()}")
gravar_estado()
base.esperar(1)
base.fechar(j)
gravar_estado()
base.gravar_resultados(BRUTOS)
anota("FIM")
