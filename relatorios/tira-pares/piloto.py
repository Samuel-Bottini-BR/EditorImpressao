"""Piloto da D-611 no caminho do Samuel (04/11/2026, print a-57): o projeto do Gradus dele, COPIADO
da pasta `dados-teste-rodada-de-consertos` (só lida), aberto na janela de VERDADE (fora da tela),
com as configurações dele; ferramenta Dividir, "Duas lado a lado"; mede onde cada miniatura da
tira está e quanto de vão sobra entre os DESENHOS (não entre os quadros), e tira prints.

Cliques e teclas por mensagens do Windows ao hwnd (relatorios/obra-etapa3/roteiro/base.py),
prints por PrintWindow; dados, projetos e TEMP numa pasta própria no scratchpad (nunca a pasta
de dados de verdade). O PDF do Gradus é copiado; a cópia do projeto aponta para a cópia do PDF.

Rodar (na cópia tira-pares):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\tira-pares\\piloto.py <fase> [rotulo]
fases: "abrir" (só abre e mede, como o print a-57), "caminho" (abrir, dividir todas, Duas lado a
lado, setas, Ctrl+Z, clique na miniatura, Uma página, Cortar).
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog"
               r"\05fa28dc-c2f5-4152-b355-e6ab76bb386f\scratchpad\tira-pares-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
DADOS_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao")
PROJ_ORIGEM = DADOS_ORIGEM / "projetos" / "pdfcoffee-com_gradus-primus-pdf-pdf-free"
LARGURA, ALTURA = 1536, 824
FASE = sys.argv[1] if len(sys.argv) > 1 else "abrir"
ROTULO = sys.argv[2] if len(sys.argv) > 2 else "agora"
LOG = open(AQUI / f"anotacoes-{FASE}-{ROTULO}.txt", "w", encoding="utf-8")
N = [0]


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / "prints" / f"{ROTULO}-{FASE}-{N[0]:02d}-{nome}.png", so_cliente=False)


def preparar_copia() -> Path:
    """Copia o projeto, as configurações dele e o PDF para a pasta de trabalho."""
    livros = base.TRAB / "livros"
    livros.mkdir(parents=True, exist_ok=True)
    pdf = livros / GRADUS.name
    if not pdf.exists():
        shutil.copy2(GRADUS, pdf)
    conf = base.TRAB / "dados" / "EditorImpressao"
    conf.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DADOS_ORIGEM / "configuracoes.json", conf / "configuracoes.json")
    destino = base.TRAB / "projetos" / PROJ_ORIGEM.name
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
    base.esperar(3.0)


def esperar_miniaturas(j, limite=120):
    t = time.time()
    tira = j.tela_conferir.tira
    while time.time() - t < limite:
        base.esperar(0.5)
        if all(m._pixmap is not None for m in tira._miniaturas[:20]):
            break
    base.esperar(1.0)


def desenhos(j, quantos=16) -> list[tuple[int, int]]:
    """Onde está o DESENHO de cada miniatura (x esquerdo, x direito), na tira, em pontos: o
    quadro (Miniatura) tem largura fixa e o desenho fica no meio dele, do tamanho da página."""
    from ui.widgets.tira_miniaturas import Miniatura  # noqa: F401
    tira = j.tela_conferir.tira
    dentro = tira.rolagem.widget()
    saida = []
    for m in tira._miniaturas[:quantos]:
        x0 = m.mapTo(dentro, m.rect().topLeft()).x()
        area_l = m.width() - 4
        area_a = m.height() - 4 - 16 - 2
        if m._pixmap is None:
            saida.append((x0, x0 + m.width()))
            continue
        pw, ph = m._pixmap.width(), m._pixmap.height()
        esc = min((area_l - 4) / pw, (area_a - 4) / ph)
        largura = round(pw * esc)
        esq = x0 + 2 + (area_l - largura) // 2
        saida.append((esq, esq + largura))
    return saida


def medir(j, nome):
    """Anota a vista, as colunas da grade, os quadros e os vãos entre os desenhos."""
    t = j.tela_conferir
    tira = t.tira
    grade = []
    for m in tira._miniaturas[:16]:
        i = tira.linha.indexOf(m)
        grade.append(tira.linha.getItemPosition(i)[:2])
    d = desenhos(j)
    vaos = [d[k + 1][0] - d[k][1] for k in range(len(d) - 1)]
    anotar(nome, {
        "aba": t.aba_atual, "mostrar": t.mostrar, "pronta": t._pronta(),
        "folha": t.indice_folha + 1, "pagina": t.indice_pagina + 1,
        "divididas": sum(f.dividir for f in j.projeto.folhas), "folhas": len(j.projeto.folhas),
        "miniaturas": len(tira._miniaturas), "pares_pela_vista": tira.pares_pela_vista,
        "em_pares_do_menu": tira.em_pares, "grade": grade,
        "quadros_x": [m.geometry().x() for m in tira._miniaturas[:16]],
        "desenhos": d, "vaos_entre_desenhos": vaos,
        "escolhida": [m.numero for m in tira._miniaturas if m.selecionada],
        "passou_pelo_automatico": j.projeto.passou_pelo_automatico,
    })


def ferramenta(j, letra):
    base.tecla(j, ord(letra)); base.esperar(2.0)


def mostrar(j, qual):
    from ui.widgets.paginas_rolando import DUAS, UMA
    base.clique(j, j.tela_conferir.botoes_mostrar[UMA if qual == "uma" else DUAS]); base.esperar(2.0)


def ctrl(j, vk):
    import ctypes
    h = int(j.winId())
    est = (ctypes.c_ubyte * 256)()
    base.user32.GetKeyboardState(est)
    est[0x11] = est[0xA2] = 0x80
    base.user32.SetKeyboardState(est)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, 0x11, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYDOWN, vk, 1); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, vk, 0xC0000001); base.esperar(0.05)
    base.user32.PostMessageW(h, base.WM_KEYUP, 0x11, 0xC0000001); base.esperar(0.3)
    est[0x11] = est[0xA2] = 0
    base.user32.SetKeyboardState(est); base.esperar(3)


def recorte_da_tira(img, j, nome):
    """Guarda a tira de perto (o pedaço do print onde ela está), ampliada 2x."""
    if img is None:
        return
    t = j.tela_conferir
    r = t.tira.rolagem
    canto = r.mapTo(j, r.rect().topLeft())
    e = j.devicePixelRatioF()
    # a janela com moldura: o print inclui a borda; ajustar pela diferença do cliente
    import ctypes.wintypes as wt
    h = int(j.winId())
    rj = wt.RECT(); base.user32.GetWindowRect(h, base.ctypes.byref(rj))
    pt = wt.POINT(0, 0); base.user32.ClientToScreen(h, base.ctypes.byref(pt))
    dx, dy = pt.x - rj.left, pt.y - rj.top
    x0, y0 = int(canto.x() * e) + dx, int(canto.y() * e) + dy
    x1, y1 = x0 + int(min(r.width(), 900) * e), y0 + int(r.height() * e)
    pedaco = img.crop((x0, y0, x1, y1))
    pedaco = pedaco.resize((pedaco.width * 2, pedaco.height * 2))
    N[0] += 1
    destino = AQUI / "prints" / f"{ROTULO}-{FASE}-{N[0]:02d}-{nome}-tira-de-perto.png"
    pedaco.save(destino)
    print(f"  print {destino.name}", flush=True)


def abrir():
    base.preparar(str(RAIZ), str(SCRATCH / ROTULO / FASE))
    import projetos
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    esperar_tela(j)
    return j


def fase_abrir(j):
    """Como o a-57: abre o projeto dele, vai ao Dividir, escolhe "Duas lado a lado"."""
    t = j.tela_conferir
    medir(j, "abriu")
    ferramenta(j, "D")
    esperar_miniaturas(j)
    medir(j, "dividir")
    img = p(j, "dividir-como-abriu"); recorte_da_tira(img, j, "dividir-como-abriu")
    if t.mostrar != "duas":
        mostrar(j, "duas"); esperar_miniaturas(j)
    medir(j, "dividir-duas")
    img = p(j, "dividir-duas"); recorte_da_tira(img, j, "dividir-duas")
    # o caso do a-57: as folhas divididas (dividir todas leva a "Uma página" pela D-610; volta)
    base.clique(j, t.botao_dividir_todas); base.esperar(3)
    fim = time.time() + 600
    while time.time() < fim and getattr(t, "_caixa_de_dividir_todas", None) is not None:
        base.esperar(0.5)
    tarefa = getattr(t, "_tarefa_do_em_branco", None)
    if tarefa is not None:
        tarefa.wait(120000)
    base.esperar(3)
    medir(j, "dividiu-todas")
    mostrar(j, "duas"); esperar_miniaturas(j)
    medir(j, "dividida-duas")
    img = p(j, "dividida-duas"); recorte_da_tira(img, j, "dividida-duas")
    # a folha 2, como no a-57 (clique na miniatura da página 3, a primeira da folha 2)
    mini = t.tira._miniaturas[2]
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
    base.clique(j, mini); base.esperar(2)
    medir(j, "dividida-duas-folha-2")
    img = p(j, "dividida-duas-folha-2"); recorte_da_tira(img, j, "dividida-duas-folha-2")
    mostrar(j, "uma"); esperar_miniaturas(j)
    medir(j, "dividida-uma")
    img = p(j, "dividida-uma"); recorte_da_tira(img, j, "dividida-uma")
    return t


def fase_caminho(j):
    """Depois do a-57: o que já funcionava ao redor - setas, Ctrl+Z, clique na miniatura, Uma
    página, Cortar."""
    t = fase_abrir(j)
    mostrar(j, "duas")
    base.tecla(j, 0x27); base.esperar(2)                   # seta para a direita
    medir(j, "duas-seta-direita")
    base.tecla(j, 0x27); base.esperar(2)
    medir(j, "duas-seta-direita-2")
    img = p(j, "duas-depois-de-duas-setas"); recorte_da_tira(img, j, "duas-depois-de-duas-setas")
    mini = t.tira._miniaturas[9]
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); base.esperar(0.4)
    base.clique(j, mini); base.esperar(2)
    anotar("clique-na-miniatura-10", {"pagina": t.indice_pagina + 1, "folha": t.indice_folha + 1,
                                      "folha_da_pagina_10": j.projeto.paginas[
                                          t._passos_do_dividir()[9]].folha + 1})
    medir(j, "duas-clique-10")
    ctrl(j, ord("Z"))
    medir(j, "duas-ctrl-z")
    img = p(j, "duas-ctrl-z"); recorte_da_tira(img, j, "duas-ctrl-z")
    ctrl(j, ord("Y"))
    medir(j, "duas-ctrl-y")
    ferramenta(j, "X"); esperar_miniaturas(j)
    medir(j, "cortar-duas")
    img = p(j, "cortar-duas"); recorte_da_tira(img, j, "cortar-duas")
    mostrar(j, "uma"); esperar_miniaturas(j)
    medir(j, "cortar-uma")
    img = p(j, "cortar-uma"); recorte_da_tira(img, j, "cortar-uma")


def main():
    j = abrir()
    {"abrir": fase_abrir, "caminho": fase_caminho}[FASE](j)
    base.fechar(j)


if __name__ == "__main__":
    main()
