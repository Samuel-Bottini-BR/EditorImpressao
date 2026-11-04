"""Reproduzir "depois de usar o dividir e voltar ao automatico ele está marcado de novo" (Samuel,
04/11/2026, print a-67) na janela de VERDADE (plataforma Windows), posta fora da tela, com cliques,
teclas e roda do mouse por mensagens do Windows ao hwnd (relatorios/obra-etapa3/roteiro/base.py) e
prints por PrintWindow. Modelo: relatorios/mover-parou/piloto.py (ramo mover-parou-2026-11-04).

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus é COPIADO da pasta
`dados-teste-rodada-de-consertos` (que só é lida) e o PDF também; na cópia, o caminho do PDF aponta
para a cópia do PDF.

Fases (uma por processo, cada uma com uma cópia nova do Gradus):
  rodar      desmarca "1 Dividir" na janela grande e Rodar; depois cada caminho da ferramenta Dividir
             (não dividir esta, dividir esta, juntar todas, dividir todas com o aviso da D-613,
             arrastar a linha, motor de corte), cada um com Ctrl+Z e Ctrl+Y, voltando ao Automático
             (painel e janela grande) depois de cada um; Rodar só o Limpar; fechar e abrir.
  sem-rodar  desmarca "1 Dividir" no painel e NÃO roda; os mesmos caminhos.

Rodar (na cópia caixinha-volta):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\caixinha-volta\\piloto.py <fase>
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

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f"
               r"\scratchpad\caixinha-volta-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA, ALTURA = 1536, 824
FASE = sys.argv[1] if len(sys.argv) > 1 else "rodar"
# "antes" (o código de 50b242c7) ou "depois" (o conserto): só muda o nome dos prints e anotações
VERSAO = sys.argv[2] if len(sys.argv) > 2 else "depois"
(AQUI / "prints").mkdir(exist_ok=True)
LOG = open(AQUI / f"anotacoes-{VERSAO}-{FASE}.txt", "w", encoding="utf-8")
N = [0]
FALHAS: list[str] = []


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / "prints" / f"{VERSAO}-{FASE}-{N[0]:02d}-{nome}.png", so_cliente=False)


class Porteiro:
    """As caixas que abrem por cima: anota o texto e clica no botão de fábrica (no aviso da D-613,
    "Pular"; na pergunta das mexidas, o de fábrica dela)."""

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
                p(w, "caixa")
                anotar("caixa", {"titulo": w.windowTitle(), "texto": w.text(),
                                 "botoes": [b.text() for b in w.buttons()]})
                b = w.defaultButton() or w.buttons()[0]
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


def esperar_tarefa(j, limite=600):
    """Espera o Rodar do Automático (fio de fundo) terminar e a tela voltar."""
    t = time.time()
    base.esperar(1.0)
    while time.time() - t < limite:
        tarefa = getattr(j, "tarefa", None)
        try:
            rodando = tarefa is not None and tarefa.isRunning()
        except RuntimeError:
            rodando = False
        if not rodando:
            break
        base.esperar(0.5)
    return esperar_tela(j, 120)


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


def roda(j, widget, cliques=1):
    """Roda do mouse por mensagem do Windows (WM_MOUSEWHEEL leva a posição na TELA)."""
    h = int(j.winId())
    alvo = widget.mapToGlobal(widget.rect().center())
    e = j.devicePixelRatioF()
    x, y = round(alvo.x() * e), round(alvo.y() * e)
    lp = ((y & 0xFFFF) << 16) | (x & 0xFFFF)
    delta = 120 if cliques > 0 else -120
    for _ in range(abs(cliques)):
        wp = (delta & 0xFFFF) << 16
        base.user32.PostMessageW(h, 0x020A, wp, lp); base.esperar(0.2)
    base.esperar(1.5)


def ferramenta(j, letra):
    base.tecla(j, ord(letra)); base.esperar(1.5)


# --- a caixinha do Dividir --------------------------------------------------------------------

def _ponto_da_caixinha(lista, etapa):
    """O meio da caixinha (o indicador) da etapa na lista, nas coordenadas do viewport."""
    from PySide6.QtCore import QPoint
    item = lista.item_da_etapa(etapa)
    r = lista.visualItemRect(item)
    return QPoint(r.left() + 16, r.center().y())


def clicar_caixinha(janela_alvo, lista, etapa, nome, marcar=False):
    """Clica na caixinha da etapa (só se ela não estiver já como `marcar` pede)."""
    from PySide6.QtCore import Qt
    from core import automatico as A
    antes = lista.item_da_etapa(etapa).checkState() == Qt.Checked
    if antes == marcar:
        anotar(f"caixinha {A.NOMES[etapa]} ({nome}) já estava", antes)
        return antes
    lista.scrollToItem(lista.item_da_etapa(etapa)); base.esperar(0.3)
    base.clique(janela_alvo, lista.viewport(), _ponto_da_caixinha(lista, etapa))
    depois = lista.item_da_etapa(etapa).checkState() == Qt.Checked
    if depois == antes:     # o clique caiu fora do indicador: a barra de espaço na etapa escolhida
        base.clique(janela_alvo, lista.viewport(), lista.visualItemRect(lista.item_da_etapa(etapa)).center())
        base.tecla(janela_alvo, 0x20)
        depois = lista.item_da_etapa(etapa).checkState() == Qt.Checked
    anotar(f"clique na caixinha {A.NOMES[etapa]} ({nome})", {"antes": antes, "depois": depois})
    return depois


def painel(j):
    return j.tela_conferir.paineis.automatico


def mostrar_o_painel(j):
    """Volta ao Automático: o painel à vista (como o botão do painel)."""
    j.tela_conferir.paineis.mostrar_painel("automatico", True)
    base.esperar(1.0)


def abrir_a_grande(j):
    pa = painel(j)
    base.clique(j, pa.botao_janela)
    base.esperar(2.5)
    return j.janela_do_automatico


def fechar_a_grande(j):
    jan = j.janela_do_automatico
    if jan is not None:
        base.tecla(jan, 0x1B)       # Esc
        base.esperar(1.0)
    if j.janela_do_automatico is not None and j.janela_do_automatico.isVisible():
        j._fechar_a_janela_do_automatico(); base.esperar(0.5)


def conferir_caixinha(j, nome, esperado_marcada=False, livro_esperado=None):
    """Volta ao Automático e olha a caixinha do Dividir: no painel e na janela grande."""
    from PySide6.QtCore import Qt
    from core import automatico as A
    mostrar_o_painel(j)
    pa = painel(j)
    no_painel = pa.lista.item_da_etapa(A.DIVIDIR).checkState() == Qt.Checked
    p(j, f"{nome}-painel")
    jan = abrir_a_grande(j)
    na_grande = jan.lista.item_da_etapa(A.DIVIDIR).checkState() == Qt.Checked if jan else None
    frase = jan.frase.text() if jan is not None else ""
    if jan is not None:
        p(jan, f"{nome}-janela-grande")
    fechar_a_grande(j)
    pr = j.projeto
    r = {"painel": no_painel, "janela_grande": na_grande,
         "situacao": j.estado_do_automatico.situacoes.get(A.DIVIDIR),
         "livro_dividir_folhas": pr.dividir_folhas,
         "folhas_divididas": sum(1 for f in pr.folhas if f.dividir), "paginas": len(pr.paginas),
         "acoes": len(j.acoes.feitas), "frase_diz_dividir": "dividir" in frase.lower()}
    falhou = (no_painel != esperado_marcada) or (na_grande != esperado_marcada) or (
        livro_esperado is not None and pr.dividir_folhas != livro_esperado)
    if falhou:
        FALHAS.append(nome)
    anotar(("FALHOU " if falhou else "ok ") + nome, r)
    return r


# --- os caminhos -------------------------------------------------------------------------------

def ir_folha(j, indice):
    j.tela_conferir._ir_para(indice); base.esperar(2.0)


def esperar_dividir_todas(j, limite=900):
    t = j.tela_conferir
    t0 = time.time()
    base.esperar(2)
    while time.time() - t0 < limite:
        caixa = getattr(t, "_caixa_de_dividir_todas", None)
        try:
            aberta = caixa is not None and caixa.isVisible()
        except RuntimeError:
            aberta = False
        if not aberta:
            break
        base.esperar(0.5)
    base.esperar(3)
    return round(time.time() - t0, 1)


def com_ctrl_z_y(j, nome, livro):
    ctrl(j, ord("Z"))
    conferir_caixinha(j, nome + "-ctrl-z", livro_esperado=livro)
    ctrl(j, ord("Y"))
    conferir_caixinha(j, nome + "-ctrl-y", livro_esperado=livro)


def no_dividir(j):
    """A ferramenta Dividir pela letra D (atalho). A lista de etapas do painel, com o foco, come as
    letras (busca do Qt): o foco vai antes para a tela (como clicar fora da lista)."""
    from ui.tela_conferir import ABA_CORTE
    t = j.tela_conferir
    t.setFocus(); base.esperar(0.3)
    ferramenta(j, "D")
    if t.aba_atual != ABA_CORTE:
        anotar("a letra D nao chegou; escolho pela trilha", t.aba_atual)
        t.escolher_ferramenta("dividir"); base.esperar(1.5)
    anotar("ferramenta", t.aba_atual)


def caminhos(j, livro):
    """Todos os caminhos da ferramenta Dividir, um por vez, cada um seguido do Ctrl+Z e Ctrl+Y,
    voltando ao Automático depois de cada passo. `livro`: o dividir_folhas que tem de ficar."""
    t = j.tela_conferir
    # 1. "não dividir esta" (folha 5)
    no_dividir(j); ir_folha(j, 4)
    p(j, "dividir-folha-5")
    base.clique(j, t.botao_nao_dividir); base.esperar(2)
    conferir_caixinha(j, "1-nao-dividir-esta", livro_esperado=livro)
    no_dividir(j); com_ctrl_z_y(j, "1-nao-dividir-esta", livro)
    # 2. "dividir esta" na folha juntada (volta como estava) e numa folha juntada pelo "juntar todas"
    no_dividir(j); ir_folha(j, 4)
    base.clique(j, t.botao_nao_dividir); base.esperar(2)     # o Ctrl+Y já juntou: agora "dividir esta"
    conferir_caixinha(j, "2-dividir-esta", livro_esperado=livro)
    no_dividir(j); com_ctrl_z_y(j, "2-dividir-esta", livro)
    # 3. "juntar todas"
    no_dividir(j)
    base.clique(j, t.botao_juntar_todas); base.esperar(3)
    conferir_caixinha(j, "3-juntar-todas", livro_esperado=livro)
    no_dividir(j); com_ctrl_z_y(j, "3-juntar-todas", livro)
    # 4. "dividir todas" depois do "juntar todas" (todas inteiras, sem o aviso: D-613 "2- ok")
    no_dividir(j)
    base.clique(j, t.botao_dividir_todas)
    anotar("dividir-todas-levou-s", esperar_dividir_todas(j))
    conferir_caixinha(j, "4-dividir-todas", livro_esperado=livro)
    no_dividir(j); com_ctrl_z_y(j, "4-dividir-todas", livro)
    # 5. o aviso da D-613: juntar a folha 5 à mão e "dividir todas" (o Porteiro clica "Pular esta")
    no_dividir(j); ir_folha(j, 4)
    if t.projeto.folhas[4].dividir:
        base.clique(j, t.botao_nao_dividir); base.esperar(2)
    base.clique(j, t.botao_dividir_todas)
    anotar("dividir-todas-com-aviso-levou-s", esperar_dividir_todas(j))
    conferir_caixinha(j, "5-dividir-todas-aviso-d613", livro_esperado=livro)
    no_dividir(j); com_ctrl_z_y(j, "5-dividir-todas-aviso-d613", livro)
    # 6. arrastar a linha (folha 5 inteira, "Duas lado a lado" mostra a linha; D-609)
    no_dividir(j); ir_folha(j, 4)
    from ui.tela_conferir import ABA_CORTE, DUAS
    base.clique(j, t.botoes_mostrar[DUAS]); base.esperar(2)
    vis = t.visualizadores[ABA_CORTE]
    folha = t.projeto.folhas[4]
    antes = folha.posicao_corte
    area = getattr(vis, "_area", None)
    if area is not None and area.width() > 0:
        from PySide6.QtCore import QPoint
        x = round(area.left() + area.width() * float(vis.posicao_corte))
        base.arrastar(j, vis, QPoint(x, area.center().y()), QPoint(x - 40, area.center().y()))
    anotar("arrastar-linha", {"antes": antes, "depois": folha.posicao_corte, "area": str(area),
                              "inteira": not folha.dividir, "vis_visivel": vis.isVisible()})
    p(j, "arrastar-linha")
    conferir_caixinha(j, "6-arrastar-a-linha", livro_esperado=livro)
    no_dividir(j); com_ctrl_z_y(j, "6-arrastar-a-linha", livro)
    # 7. trocar o motor de corte (roda do mouse na lista "motor de corte")
    no_dividir(j); ir_folha(j, 6)
    combo = t.combo_jeito_da_folha
    antes = combo.currentData()
    roda(j, combo, -1)
    if combo.currentData() == antes:
        roda(j, combo, 1)
    anotar("motor", {"antes": antes, "depois": combo.currentData()})
    conferir_caixinha(j, "7-motor-de-corte", livro_esperado=livro)
    no_dividir(j); com_ctrl_z_y(j, "7-motor-de-corte", livro)


def abrir(copiar=True):
    base.preparar(str(RAIZ), str(SCRATCH / f"{VERSAO}-{FASE}"), limpar=copiar)
    import projetos
    pasta = preparar_copia() if copiar else base.TRAB / "projetos" / PROJ_ORIGEM.name
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("abriu-em-s", esperar_tela(j))
    return j


def reabrir(j):
    """Fecha a janela (WM_CLOSE: o programa grava) e abre o mesmo trabalho numa janela nova."""
    import projetos
    j._salvar_agora()
    base.fechar(j)
    pasta = base.TRAB / "projetos" / PROJ_ORIGEM.name
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("reabriu-em-s", esperar_tela(j))
    return j


def ligar_o_dividir_se_preciso(j):
    """O livro tem de começar com o Dividir "ligado no livro todo" (como no print a-67). A cópia
    é tirada da pasta de teste na hora (o Samuel pode estar mexendo nela): se o livro estiver com
    o Dividir desligado, marca o Dividir e Rodar (como o Samuel às 14:40 de 04/11)."""
    from core import automatico as A
    if j.projeto.dividir_folhas:
        return
    anotar("o livro veio com o Dividir desligado: marco e Rodar", None)
    jan = abrir_a_grande(j)
    clicar_caixinha(jan, jan.lista, A.DIVIDIR, "janela grande", marcar=True)
    base.clique(jan, jan.botao_rodar)
    anotar("rodou-em-s", esperar_tarefa(j))


def fase_rodar(j):
    from core import automatico as A
    ligar_o_dividir_se_preciso(j)
    conferir_caixinha(j, "0-abriu", esperado_marcada=True, livro_esperado=True)
    # desmarcar o Dividir na janela grande e Rodar (o Limpar continua marcado)
    jan = abrir_a_grande(j)
    clicar_caixinha(jan, jan.lista, A.DIVIDIR, "janela grande")
    p(jan, "desmarcado-na-janela-grande")
    base.clique(jan, jan.botao_rodar)
    anotar("rodou-em-s", esperar_tarefa(j))
    conferir_caixinha(j, "0-desmarcou-e-rodou", livro_esperado=False)
    caminhos(j, livro=False)
    # 8. Rodar outra etapa (só o Limpar) com o Dividir desmarcado
    mostrar_o_painel(j)
    base.clique(j, painel(j).botao_rodar)
    anotar("rodou-limpar-em-s", esperar_tarefa(j))
    conferir_caixinha(j, "8-rodar-so-o-limpar", livro_esperado=False)
    # 9. fechar e abrir
    j = reabrir(j)
    conferir_caixinha(j, "9-fechar-e-abrir", livro_esperado=False)
    return j


def fase_sem_rodar(j):
    from core import automatico as A
    ligar_o_dividir_se_preciso(j)
    conferir_caixinha(j, "0-abriu", esperado_marcada=True, livro_esperado=True)
    mostrar_o_painel(j)
    clicar_caixinha(j, painel(j).lista, A.DIVIDIR, "painel")
    conferir_caixinha(j, "0-desmarcou-no-painel-sem-rodar", livro_esperado=True)
    caminhos(j, livro=True)
    # 8a. a caixinha "Margens iguais" do Cortar (letra X), ligar e desligar
    t = j.tela_conferir
    t.setFocus(); base.esperar(0.3)
    ferramenta(j, "X")
    anotar("ferramenta", t.aba_atual)
    caixa = t.caixa_margens_iguais
    if caixa.isVisible():
        base.clique(j, caixa); base.esperar(2)
        anotar("margens iguais", j.projeto.margens_iguais)
        conferir_caixinha(j, "8a-margens-iguais-do-cortar", livro_esperado=True)
        t.setFocus(); ferramenta(j, "X")
        if caixa.isVisible():
            base.clique(j, caixa); base.esperar(2)
    else:
        anotar("a caixinha Margens iguais não está à vista", None)
    # 8b. "desligar as marcadas" (o Limpar marcado, o Dividir desmarcado)
    mostrar_o_painel(j)
    base.clique(j, painel(j).botao_desligar)
    anotar("desligou-em-s", esperar_tarefa(j))
    anotar("limpar no livro", j.projeto.limpar)
    conferir_caixinha(j, "8b-desligar-as-marcadas", livro_esperado=True)
    j = reabrir(j)
    conferir_caixinha(j, "9-fechar-e-abrir", livro_esperado=True)
    return j


def main():
    j = abrir()
    _porteiro = Porteiro()  # noqa: F841
    p(j, "abriu")
    j = {"rodar": fase_rodar, "sem-rodar": fase_sem_rodar}[FASE](j)
    anotar("FALHAS", FALHAS)
    base.fechar(j)


if __name__ == "__main__":
    main()
