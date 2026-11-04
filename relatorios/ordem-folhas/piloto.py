"""D-615 / D-616 na janela de VERDADE (plataforma Windows), posta fora da tela: cliques, arrastos e
teclas por mensagens do Windows ao hwnd (relatorios/obra-etapa3/roteiro/base.py), prints por
PrintWindow. Mesmo jeito do piloto do ramo mover-parou (relatorios/mover-parou/piloto.py).

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus Primus é COPIADO da
pasta `dados-teste-rodada-de-consertos` (que só é lida) e o PDF também; na cópia, o caminho do PDF
aponta para a cópia.

Rodar (na cópia ordem-folhas):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\ordem-folhas\\piloto.py e1
    (e1 = entrega 1, D-615; e2 = entrega 2, D-616)
"""
from __future__ import annotations

import ctypes
import json
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f\scratchpad\ordem-folhas-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA, ALTURA = 1536, 824
FASE = sys.argv[1] if len(sys.argv) > 1 else "e1"
(AQUI / "prints").mkdir(exist_ok=True)
LOG = open(AQUI / f"anotacoes-{FASE}.txt", "w", encoding="utf-8")
N = [0]


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / "prints" / f"{FASE}-{N[0]:02d}-{nome}.png", so_cliente=False)


class Porteiro:
    """As caixas que abrem por cima: anota o texto e clica no botão padrão."""

    def __init__(self):
        from PySide6.QtCore import QTimer
        self.ocupado = False
        self.t = QTimer(); self.t.setInterval(250); self.t.timeout.connect(self.olhar); self.t.start()

    def olhar(self):
        if self.ocupado:
            return
        from PySide6.QtWidgets import QApplication, QMessageBox
        for w in QApplication.topLevelWidgets():
            try:
                if not w.isVisible() or w.property("_visto") or not isinstance(w, QMessageBox):
                    continue
            except RuntimeError:
                continue
            w.setProperty("_visto", True)
            self.ocupado = True
            try:
                base.esperar(0.5)
                anotar("caixa", {"titulo": w.windowTitle(), "texto": w.text(),
                                 "botoes": [b.text() for b in w.buttons()]})
                b = w.defaultButton() or w.buttons()[0]
                base.clique(w, b)
            finally:
                self.ocupado = False
            return


def preparar_copia() -> Path:
    livros = base.TRAB / "livros"
    livros.mkdir(parents=True, exist_ok=True)
    pdf = livros / GRADUS.name
    if not pdf.exists():
        shutil.copy2(GRADUS, pdf)
    destino = base.TRAB / "projetos" / PROJ_ORIGEM.name
    if destino.exists():
        shutil.rmtree(destino)               # só a cópia, na pasta de trabalho deste script
    shutil.copytree(PROJ_ORIGEM, destino)
    for nome in ("projeto.json", "resumo.json"):
        arq = destino / nome
        dados = json.loads(arq.read_text(encoding="utf-8"))
        dados["caminho_entrada"] = str(pdf).replace("\\", "/")
        if "pasta" in dados:
            dados["pasta"] = str(destino)
        if "miniatura" in dados:
            dados["miniatura"] = str(destino / "capa.png")
        arq.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    return destino


def esperar_tela(j, limite=300):
    from ui.janela_principal import CONFERIR
    t = time.time()
    while time.time() - t < limite:
        base.esperar(0.3)
        if j.telas.currentIndex() == CONFERIR and j.tela_conferir._pronta():
            break
    base.esperar(2.0)
    return round(time.time() - t, 1)


def ctrl(j, tecla_vk):
    h = int(j.winId())
    VK_CONTROL, VK_LCONTROL = 0x11, 0xA2
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0x80
    base.user32.SetKeyboardState(est)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, VK_CONTROL, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, tecla_vk, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, tecla_vk, 0xC0000001); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, VK_CONTROL, 0xC0000001); base.esperar(0.3)
    est[VK_CONTROL] = est[VK_LCONTROL] = 0
    base.user32.SetKeyboardState(est); base.esperar(2.0)


def ordem(j, quantas=6):
    """As primeiras e as últimas páginas do livro: "folha.metade"."""
    nomes = [f"{q.folha + 1}{q.metade[0]}" for q in j.projeto.paginas]
    return {"comeco": nomes[:quantas], "fim": nomes[-quantas:], "total": len(nomes)}


def estado(j) -> dict:
    t = j.tela_conferir
    return {"aba": t.aba_atual, "pagina": t.indice_pagina + 1, "folha": t.indice_folha + 1,
            "mostrar": t.mostrar, "feitas": len(t.acoes.feitas) if t.acoes else None,
            "ordem": ordem(j), "quadros": len(t.tira._miniaturas),
            "selecionado": next((m.numero for m in t.tira._miniaturas if m.selecionada), None)}


def abrir():
    base.preparar(str(RAIZ), str(SCRATCH), limpar=False)
    import projetos
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    porteiro = Porteiro()
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("abriu-em-s", esperar_tela(j))
    return j, porteiro, resumo


def mini(j, i):
    t = j.tela_conferir
    m = t.tira._miniaturas[i]
    t.tira.rolagem.ensureWidgetVisible(m, 60, 0); base.esperar(0.5)
    return m


def arrastar_mini(j, de, para_antes_de, print_no_meio=None, segurar=0.0):
    """Arrasta a miniatura `de` até o vão antes da `para_antes_de` (None = a beirada direita da
    tira, segurando `segurar` segundos para ela rolar até o fim). Por mensagens do Windows:
    apertar, andar em passos, (print no meio), soltar."""
    from PySide6.QtCore import QPoint
    t = j.tela_conferir
    h = int(j.winId())
    origem = mini(j, de)
    a = origem.mapTo(j, origem.rect().center())
    base.user32.PostMessageW(h, base.WM_MOUSEMOVE, 0, base._lp(j, a)); base.esperar(0.15)
    base.user32.PostMessageW(h, base.WM_LBUTTONDOWN, base.MK_LBUTTON, base._lp(j, a)); base.esperar(0.6)
    if para_antes_de is None:
        vp = t.tira.rolagem.viewport()
        b = vp.mapTo(j, QPoint(vp.width() - 12, vp.height() // 2))
    else:
        alvo = t.tira._miniaturas[para_antes_de]
        b = alvo.mapTo(j, alvo.rect().center() - QPoint(alvo.width() // 3, 0))
    passos = 14
    for k in range(1, passos + 1):
        m = QPoint(round(a.x() + (b.x() - a.x()) * k / passos), round(a.y() + (b.y() - a.y()) * k / passos))
        base.user32.PostMessageW(h, base.WM_MOUSEMOVE, base.MK_LBUTTON, base._lp(j, m)); base.esperar(0.06)
    if segurar:
        base.esperar(segurar)
        base.user32.PostMessageW(h, base.WM_MOUSEMOVE, base.MK_LBUTTON, base._lp(j, b)); base.esperar(0.3)
    base.esperar(0.4)
    anotar("arrastando", {"arrastando": t.tira.arrastando(), "linha_azul": t.tira.sinal_do_vao.isVisible(),
                          "vao": (t.tira._arrasto or {}).get("vao")})
    if print_no_meio:
        p(j, print_no_meio)
    base.user32.PostMessageW(h, base.WM_LBUTTONUP, 0, base._lp(j, b)); base.esperar(2.0)


def ferramenta(j, letra):
    base.tecla(j, ord(letra)); base.esperar(1.5)


def mostrar(j, qual):
    from ui.tela_conferir import DUAS, UMA
    base.clique(j, j.tela_conferir.botoes_mostrar[UMA if qual == "uma" else DUAS]); base.esperar(1.5)


def gerar_pdf(j, nome):
    """O PDF de saída (o mesmo processar do "Confirmar e processar"), numa cópia do projeto; as
    páginas 1, 2 e a última viram PNG para olhar."""
    import copy

    import fitz

    from core.pipeline import processar
    projeto = copy.copy(j.projeto)
    projeto.caminho_saida = str(base.TRAB / f"{nome}.pdf")
    saida = processar(projeto)
    with fitz.open(saida) as doc:
        n = doc.page_count
        for k in sorted({0, 1, n - 1}):
            doc[k].get_pixmap(dpi=40).save(str(AQUI / "prints" / f"{FASE}-pdf-{nome}-pagina-{k + 1}.png"))
    anotar(f"pdf-{nome}", {"paginas": n, "arquivo": saida})


def fase_e1(j, resumo):
    """D-615: clique, arrastar a capa para a frente, a contracapa para o fim (rolando), Ctrl+Z,
    Ctrl+Y, reabrir, PDF, e o que já funcionava ao redor (setas, Dividir, pares)."""
    t = j.tela_conferir
    anotar("inicio", estado(j)); p(j, "abriu")
    # 1. clique simples na miniatura 3: vai para a página 3, nada muda de lugar
    base.clique(j, mini(j, 2)); base.esperar(1.5)
    anotar("clique-na-3", estado(j)); p(j, "clique-na-miniatura-3")
    # 2. a capa (página 2 = metade da direita da folha 1) arrastada para antes da página 1
    arrastar_mini(j, 1, 0, print_no_meio="arrastando-a-capa-linha-azul")
    anotar("capa-para-a-frente", estado(j)); p(j, "capa-na-frente")
    # 3. a contracapa (agora a página 2) para o fim do livro (a tira rola sozinha na beirada)
    arrastar_mini(j, 1, None, print_no_meio="arrastando-a-contracapa-para-o-fim", segurar=9.0)
    anotar("contracapa-para-o-fim", estado(j)); p(j, "contracapa-no-fim")
    # 4. Ctrl+Z (volta a contracapa), Ctrl+Y (refaz)
    ctrl(j, ord("Z")); anotar("ctrl-z", estado(j)); p(j, "ctrl-z")
    ctrl(j, ord("Y")); anotar("ctrl-y", estado(j)); p(j, "ctrl-y")
    # 5. setas: a página seguinte é a da ordem nova
    base.clique(j, mini(j, 0)); base.esperar(1)
    base.tecla(j, 0x27); base.esperar(1.5)
    anotar("seta-direita-da-capa", estado(j)); p(j, "seta-depois-da-capa")
    # 6. o PDF de saída
    gerar_pdf(j, "e1")
    # 7. Duas lado a lado: a tira em pares, na ordem nova (D-611)
    mostrar(j, "duas"); anotar("duas-lado-a-lado", estado(j)); p(j, "duas-lado-a-lado-pares")
    # arrastar com os pares: a página 5 para antes da 3
    arrastar_mini(j, 4, 2, print_no_meio="arrastando-nos-pares")
    anotar("arrastou-nos-pares", estado(j)); p(j, "depois-de-arrastar-nos-pares")
    ctrl(j, ord("Z")); anotar("ctrl-z-pares", estado(j))
    mostrar(j, "uma")
    # 8. a ferramenta Dividir: a tira das metades, na ordem nova
    ferramenta(j, "D"); anotar("dividir", estado(j)); p(j, "ferramenta-dividir")
    # 9. fechar e abrir de novo
    j._salvar_agora()
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("reabriu-em-s", esperar_tela(j))
    anotar("reaberto", estado(j)); p(j, "reaberto")


def fase_dbg(j, resumo):
    """Só para achar defeito: anota cada passo do arrastar para a beirada esquerda."""
    t = j.tela_conferir
    original = t.tira._mostrar_o_vao

    def com_nota(ponto):
        vp = t.tira.rolagem.viewport()
        anotar("vao", {"global": [ponto.x(), ponto.y()], "local": [vp.mapFromGlobal(ponto).x(),
                       vp.mapFromGlobal(ponto).y()], "vao": t.tira.vao_do_ponto(ponto)})
        original(ponto)
    t.tira._mostrar_o_vao = com_nota
    anotar("inicio", estado(j)); p(j, "abriu")
    base.clique(j, mini(j, 2)); base.esperar(1.5)
    anotar("clique-na-3", estado(j)); p(j, "clique-na-miniatura-3")
    arrastar_mini(j, 1, 0, print_no_meio="dbg")
    anotar("depois", estado(j))


def clicar_etapa(jan, etapa):
    """Clica no nome da etapa na lista da janela do Automático (abre as opções dela)."""
    lista = jan.painel_de_opcoes.lista
    item = lista.item_da_etapa(etapa)
    centro = lista.visualItemRect(item).center()
    base.clique(jan, lista.viewport(), centro); base.esperar(1.5)


def esperar_caderno(jan, limite=240):
    """Espera a folha do caderno da etapa 7 ficar pronta (a bolinha some)."""
    folhas = jan.folhas_do_caderno
    t = time.time()
    base.esperar(1.0)
    while time.time() - t < limite and (folhas.calculando() or folhas._folha is None):
        base.esperar(0.5)
    base.esperar(1.0)
    return round(time.time() - t, 1)


def esperar_previa_do_auto(jan, limite=120):
    """Espera o "depois" da prévia da janela do Automático chegar."""
    ver = jan.antes_e_depois
    t = time.time()
    base.esperar(1.0)
    while time.time() - t < limite and getattr(ver, "_depois", None) is None:
        base.esperar(0.5)
    base.esperar(1.5)
    return round(time.time() - t, 1)


def fase_e2(j, resumo):
    """D-616: a caixinha "A 1ª folha é a capa aberta" no Dividir do Automático; a etapa 7 sem e
    com ela (o print a-61 era sem); a prévia; Rodar; a ordem, o PDF e o Ctrl+Z."""
    from PySide6.QtCore import Qt

    from core import automatico as A
    anotar("inicio", estado(j)); p(j, "abriu")
    jan = j.abrir_o_automatico(A.DIVIDIR); base.esperar(2.5)
    caixa = jan.controles["capa_aberta"]
    anotar("caixinha", {"texto": caixa.text(), "marcada": caixa.isChecked(), "a_vista": caixa.isVisible()})
    p(jan, "dividir-caixinha-desmarcada")
    item = jan.painel_de_opcoes.lista.item_da_etapa(A.DIVIDIR)
    item.setCheckState(Qt.Checked); base.esperar(1.0)
    anotar("marcadas", sorted(j.estado_do_automatico.marcadas))
    # a etapa 7 sem a caixinha: a folha 1 do caderno como no print a-61
    clicar_etapa(jan, A.CADERNOS)
    anotar("caderno-sem-a-caixinha-em-s", esperar_caderno(jan))
    anotar("lista-sem", [(f + 1, m) for _o, f, m in jan.folhas_do_caderno._depois()][:3])
    p(jan, "etapa7-sem-a-caixinha")
    # marca a caixinha (clique de verdade)
    clicar_etapa(jan, A.DIVIDIR)
    from PySide6.QtCore import QPoint
    base.clique(jan, caixa, QPoint(10, caixa.height() // 2)); base.esperar(1.0)   # no quadradinho
    anotar("caixinha-depois-do-clique", {"marcada": caixa.isChecked(),
                                         "estado": j.estado_do_automatico.opcoes.get("capa_aberta")})
    passos = jan.antes_e_depois._passos()
    anotar("previa-passos", passos[:2] + passos[-1:])
    jan.antes_e_depois.ir_para(*passos[0])                 # o 1o passo da prévia: a capa
    anotar("previa-em-s", esperar_previa_do_auto(jan))
    anotar("previa-contador", jan.antes_e_depois.contador.text())
    p(jan, "dividir-caixinha-marcada-previa-primeira")
    jan.antes_e_depois.ir_para(*passos[-1])                # o último: a contracapa
    anotar("previa-ultima-em-s", esperar_previa_do_auto(jan))
    anotar("previa-contador-ultima", jan.antes_e_depois.contador.text())
    p(jan, "dividir-caixinha-marcada-previa-ultima")
    # a etapa 7 com a caixinha: a capa na frente da folha 1
    clicar_etapa(jan, A.CADERNOS)
    anotar("caderno-com-a-caixinha-em-s", esperar_caderno(jan))
    anotar("lista-com", [(f + 1, m) for _o, f, m in jan.folhas_do_caderno._depois()][:3])
    p(jan, "etapa7-com-a-caixinha-capa-na-frente")
    # Rodar (só o Dividir marcado)
    feitas = len(j.acoes.feitas)
    base.clique(jan, jan.botao_rodar)
    t0 = time.time()
    while time.time() - t0 < 120 and len(j.acoes.feitas) == feitas:
        base.esperar(0.5)
        if time.time() - t0 > 8 and int(time.time() - t0) % 30 == 0:
            from PySide6.QtWidgets import QApplication
            anotar("esperando", [type(w).__name__ + ":" + w.windowTitle() for w in QApplication.topLevelWidgets()
                                 if w.isVisible()])
    base.esperar(3.0)
    anotar("rodou", {"feitas": len(j.acoes.feitas), "capa_no_livro": j.projeto.capa_aberta, **estado(j)})
    p(j, "depois-de-rodar")
    gerar_pdf(j, "e2")
    ctrl(j, ord("Z"))
    anotar("ctrl-z", {"capa_no_livro": j.projeto.capa_aberta, **estado(j)}); p(j, "ctrl-z")


def main():
    j, _porteiro, resumo = abrir()
    {"e1": fase_e1, "e2": fase_e2, "dbg": fase_dbg}.get(FASE, fase_e1)(j, resumo)
    base.fechar(j)


if __name__ == "__main__":
    main()
