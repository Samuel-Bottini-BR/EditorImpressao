"""D-613 na janela de VERDADE (plataforma Windows), posta fora da tela, como o piloto do
mover-parou (relatorios/mover-parou/piloto.py, ramo mover-parou-2026-11-04): cliques e teclas por
mensagens do Windows ao hwnd (relatorios/obra-etapa3/roteiro/base.py), prints por PrintWindow.

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus é COPIADO da pasta
`dados-teste-rodada-de-consertos` (que só é lida) e o PDF também; na cópia, o caminho do PDF
aponta para a cópia do PDF. A cópia do Gradus está com as 70 folhas juntadas pelo "juntar todas".

O caminho (o exemplo da D-613: "Gradus: juntar a folha 5 à mão, "dividir todas" → aviso
pergunta; escolher pular → a folha 5 fica inteira; escolher dividir → todas divididas"):
  0. sem folha juntada à mão (só as do "juntar todas"): "dividir todas" sem aviso; Ctrl+Z
  1. folha 5: "dividir esta" (a linha azul antes; a seta → depois do botão, D-608), "não dividir esta"
  2. "dividir todas" → aviso → cancelar: nada muda
  3. em "Duas lado a lado": "dividir todas" → aviso → "Pular esta": a 5 inteira, as outras
     divididas, a vista passa para "Uma página" (D-610); Ctrl+Z; Ctrl+Y; Ctrl+Z
  4. "dividir todas" → aviso → "Dividir também": as 70 divididas; Ctrl+Z
  5. "juntar todas" continua juntando (D-590)

Rodar (na cópia dividir-aviso):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\dividir-aviso\\piloto.py
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

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f\scratchpad\dividir-aviso-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA, ALTURA = 1536, 824
LOG = open(AQUI / "anotacoes.txt", "w", encoding="utf-8")
N = [0]
RESPOSTA = {"botao": None}          # o botão que o porteiro clica no próximo aviso


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / "prints" / f"{N[0]:02d}-{nome}.png", so_cliente=False)


class Porteiro:
    """As caixas que abrem por cima: anota o texto, tira o print e clica no botão pedido
    (RESPOSTA["botao"]); sem pedido, no botão de fábrica."""

    def __init__(self):
        from PySide6.QtCore import QTimer
        self.ocupado = False
        self.vistas: list[dict] = []
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
                base.esperar(0.6)
                visto = {"titulo": w.windowTitle(), "texto": w.text(),
                         "explicacao": w.informativeText(),
                         "botoes": [b.text() for b in w.buttons()],
                         "de_fabrica": w.defaultButton().text() if w.defaultButton() else None}
                anotar("caixa", visto)
                self.vistas.append(visto)
                p(w, "aviso-" + (RESPOSTA["botao"] or "fabrica").replace(" ", "-"))
                pedido = RESPOSTA["botao"]
                b = next((x for x in w.buttons() if x.text() == pedido), None) \
                    or w.defaultButton() or w.buttons()[0]
                anotar("cliquei-no-aviso", b.text())
                base.clique(w, b)
            finally:
                self.ocupado = False
            return


def preparar_copia() -> Path:
    """Copia o projeto e o PDF para a pasta de trabalho; o caminho do PDF vai para a cópia."""
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


def estado(j) -> dict:
    from core import dividir_a_mao
    from ui.tela_conferir import ABA_CORTE
    t, pr = j.tela_conferir, j.projeto
    vis = t.visualizadores[ABA_CORTE]
    return {
        "folha": t.indice_folha + 1, "pagina": t.indice_pagina + 1, "mostrar": t.mostrar,
        "divididas": sum(f.dividir for f in pr.folhas),
        "inteiras_com_as_duas_guardadas": sum(bool(not f.dividir and f.metades_guardadas)
                                              for f in pr.folhas),
        "juntadas_a_mao": [x + 1 for x in dividir_a_mao.folhas_juntadas_a_mao(pr, t.acoes.feitas)],
        "folha5_dividida": pr.folhas[4].dividir,
        "paginas": len(pr.paginas),
        "linha_azul_visivel": bool(getattr(vis, "corte_visivel", False)),
        "linha_em": round(float(getattr(vis, "posicao_corte", 0) or 0), 4),
        "feitas": len(t.acoes.feitas), "desfazer": t.acoes.descricao_desfazer(),
    }


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


def mostrar(j, qual):
    from ui.tela_conferir import DUAS, UMA
    t = j.tela_conferir
    base.clique(j, t.botoes_mostrar[UMA if qual == "uma" else DUAS]); base.esperar(1.5)


def linha_lida(j, limite=60):
    from ui.tela_conferir import ABA_CORTE
    vis = j.tela_conferir.visualizadores[ABA_CORTE]
    t = time.time()
    base.esperar(0.5)
    while time.time() - t < limite and getattr(vis, "lendo_a_linha", False):
        base.esperar(0.2)
    base.esperar(0.8)


def ir_folha(j, numero):
    """Vai à folha `numero` clicando a miniatura dela na tira (folhas inteiras: uma por folha)."""
    t = j.tela_conferir
    alvo = next(p.indice for p in j.projeto.paginas if p.folha == numero - 1)
    mini = t.tira._miniaturas[alvo]
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
    base.clique(j, mini); base.esperar(1.0)
    linha_lida(j)


def dividir_todas(j, botao, limite=900):
    """Clica "dividir todas" com a resposta do aviso já pedida e espera a leitura acabar."""
    t = j.tela_conferir
    RESPOSTA["botao"] = botao
    feitas = len(t.acoes.feitas)
    t0 = time.time()
    base.clique(j, t.botao_dividir_todas); base.esperar(2)
    while time.time() - t0 < limite:
        caixa = getattr(t, "_caixa_de_dividir_todas", None)
        try:
            aberta = caixa is not None and caixa.isVisible()
        except RuntimeError:
            aberta = False
        if not aberta and (len(t.acoes.feitas) != feitas or botao == "cancelar"
                           or time.time() - t0 > 8):
            break
        base.esperar(0.5)
    base.esperar(3)
    RESPOSTA["botao"] = None
    anotar(f"dividir-todas-{botao}-levou-s", round(time.time() - t0, 1))


def main():
    base.preparar(str(RAIZ), str(SCRATCH), limpar=False)
    import projetos
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    porteiro = Porteiro()
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("abriu-em-s", esperar_tela(j))
    t = j.tela_conferir
    base.tecla(j, ord("D")); base.esperar(1.5); linha_lida(j)
    anotar("0-dividir-aberto", {"aba": t.aba_atual, **estado(j)}); p(j, "dividir-aberto")

    # 0. sem juntada à mão (só as do "juntar todas"): sem aviso (até a resposta do Samuel)
    avisos = len(porteiro.vistas)
    dividir_todas(j, None)
    anotar("0-sem-juntada-a-mao-dividir-todas", {"avisos_novos": len(porteiro.vistas) - avisos,
                                                  **estado(j)})
    p(j, "sem-juntada-a-mao-dividiu-sem-aviso")
    ctrl(j, ord("Z")); linha_lida(j)
    anotar("0-ctrl-z", estado(j))

    # 1. folha 5: linha azul, "dividir esta", seta → (D-608), volta, "não dividir esta"
    ir_folha(j, 5)
    anotar("1-folha-5", estado(j)); p(j, "folha5-linha-azul")
    base.clique(j, t.botao_nao_dividir); base.esperar(2)          # dividir esta
    anotar("1-dividir-esta", estado(j)); p(j, "folha5-dividir-esta")
    antes = t.indice_pagina
    base.tecla(j, 0x27); base.esperar(1.5)                         # seta →
    anotar("1-seta-depois-do-botao", {"pagina_antes": antes + 1, **estado(j)})
    base.tecla(j, 0x25); base.esperar(1.5)                         # seta ←
    ir_folha(j, 5)
    base.clique(j, t.botao_nao_dividir); base.esperar(2)           # não dividir esta
    linha_lida(j)
    anotar("1-nao-dividir-esta", estado(j)); p(j, "folha5-juntada-a-mao")

    # 2. aviso → cancelar
    dividir_todas(j, "cancelar")
    anotar("2-cancelar", estado(j)); p(j, "depois-do-cancelar")

    # 3. Duas lado a lado, aviso → Pular esta
    mostrar(j, "duas")
    anotar("3-duas-lado-a-lado", estado(j))
    dividir_todas(j, "Pular esta")
    anotar("3-pular", estado(j)); p(j, "depois-do-pular")
    ir_folha_dividida = next(p_.indice for p_ in j.projeto.paginas if p_.folha == 4)
    t.tira.rolagem.ensureWidgetVisible(t.tira._miniaturas[ir_folha_dividida], 60, 0)
    base.clique(j, t.tira._miniaturas[ir_folha_dividida]); base.esperar(1.5); linha_lida(j)
    anotar("3-pular-folha-5", estado(j)); p(j, "depois-do-pular-folha5-inteira")
    ctrl(j, ord("Z")); linha_lida(j)
    anotar("3-ctrl-z", estado(j)); p(j, "pular-ctrl-z")
    ctrl(j, ord("Y")); linha_lida(j)
    anotar("3-ctrl-y", estado(j)); p(j, "pular-ctrl-y")
    ctrl(j, ord("Z")); linha_lida(j)
    anotar("3-ctrl-z-de-novo", estado(j))

    # 4. aviso → Dividir também
    dividir_todas(j, "Dividir também")
    anotar("4-dividir-tambem", estado(j)); p(j, "depois-do-dividir-tambem")
    ctrl(j, ord("Z")); linha_lida(j)
    anotar("4-ctrl-z", estado(j)); p(j, "dividir-tambem-ctrl-z")

    # 5. "juntar todas" continua juntando (D-590): dividir esta na 5, juntar todas
    ir_folha(j, 5)
    base.clique(j, t.botao_nao_dividir); base.esperar(2)            # dividir esta (devolve)
    anotar("5-dividir-esta", estado(j))
    base.clique(j, t.botao_juntar_todas); base.esperar(2)
    anotar("5-juntar-todas", estado(j)); p(j, "juntar-todas")

    anotar("avisos-vistos", porteiro.vistas)
    base.fechar(j)


if __name__ == "__main__":
    main()
