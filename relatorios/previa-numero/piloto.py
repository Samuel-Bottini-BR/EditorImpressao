"""D-617 na janela de VERDADE (plataforma Windows), posta fora da tela, como o piloto do
`mover-parou` (relatorios/mover-parou/piloto.py, ramo mover-parou-2026-11-04): cliques e teclas por
mensagens do Windows ao hwnd (relatorios/obra-etapa3/roteiro/base.py), prints por PrintWindow.

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus é COPIADO da pasta
`dados-teste-rodada-de-consertos` (que só é lida) e o PDF também; na cópia, o caminho do PDF
aponta para a cópia do PDF.

Fases:
  base  - o código de antes: onde está o foco ao abrir o Automático e o que as setas do teclado
          fazem (para provar depois que continuam iguais).
  novo  - escrever 45 + Enter vai à folha 45; vazio e 0 voltam ao número atual; as setas do
          teclado continuam; com o Dividir marcado, < > andam pelas metades.

Rodar (na cópia previa-numero):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\previa-numero\\piloto.py <fase>
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

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f"
               r"\scratchpad\previa-numero-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA, ALTURA = 1536, 824
FASE = sys.argv[1] if len(sys.argv) > 1 else "base"
LOG = open(AQUI / f"anotacoes-{FASE}.txt", "w", encoding="utf-8")
N = [0]
VK_LEFT, VK_RIGHT, VK_UP, VK_DOWN, VK_BACK, VK_END = 0x25, 0x27, 0x26, 0x28, 0x08, 0x23


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n")
    LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / "prints" / f"{FASE}-{N[0]:02d}-{nome}.png", so_cliente=False)


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


def esperar_previa(painel, limite=120):
    t = time.time()
    base.esperar(0.3)
    while time.time() - t < limite and painel.calculando():
        base.esperar(0.2)
    base.esperar(0.8)


def estado(grande) -> dict:
    from PySide6.QtWidgets import QApplication
    painel = grande.antes_e_depois
    foco = QApplication.focusWidget()
    campo = getattr(painel, "campo_pagina", None)
    return {
        "indice": painel._indice, "pagina": painel._indice + 1, "metade": painel._metade,
        "contador": painel.contador.text(),
        "campo": campo.text() if campo is not None else None,
        "foco": (type(foco).__name__ + (f"#{foco.objectName()}" if foco and foco.objectName() else "")
                 + (f" '{foco.text()}'" if foco is not None and hasattr(foco, "text")
                    and isinstance(getattr(foco, "text")(), str) else "")) if foco else None,
        "anterior": painel.botao_anterior.isEnabled(), "proxima": painel.botao_proxima.isEnabled(),
    }


def abrir():
    base.preparar(str(RAIZ), str(SCRATCH), limpar=False)
    import projetos
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("abriu-em-s", esperar_tela(j))
    j.tela_conferir.ir_para_pagina(29)          # a página 30, como no print a-63
    base.esperar(1.0)
    grande = j.abrir_o_automatico()
    base.esperar(1.0)
    grande.resize(LARGURA - 60, ALTURA - 60)
    base.esperar(0.5)
    esperar_previa(grande.antes_e_depois)
    return j, grande


def setas(grande, nome):
    """Direita, Direita, Esquerda pelo teclado (para a janela do Automático, ao widget com foco)."""
    painel = grande.antes_e_depois
    anotar(f"{nome}-antes-das-setas", estado(grande))
    base.tecla(grande, VK_RIGHT)
    anotar(f"{nome}-depois-de-Direita", estado(grande))
    base.tecla(grande, VK_RIGHT)
    anotar(f"{nome}-depois-de-Direita-2", estado(grande))
    base.tecla(grande, VK_LEFT)
    anotar(f"{nome}-depois-de-Esquerda", estado(grande))
    esperar_previa(painel)


def fase_base(j, grande):
    painel = grande.antes_e_depois
    anotar("abriu-o-automatico", estado(grande))
    p(grande, "abriu")
    setas(grande, "ao-abrir")
    # clicar o ">" com o mouse e depois usar as setas (onde fica o foco depois do clique)
    base.clique(grande, painel.botao_proxima)
    esperar_previa(painel)
    anotar("depois-de-clicar->", estado(grande))
    setas(grande, "depois-do-clique-no->")
    # clicar na imagem da prévia e depois usar as setas
    base.clique(grande, painel.visor, painel.visor.rect().center() + __import__(
        "PySide6.QtCore", fromlist=["QPoint"]).QPoint(0, 40))
    anotar("depois-de-clicar-na-imagem", estado(grande))
    setas(grande, "depois-do-clique-na-imagem")
    p(grande, "fim")


def escrever(grande, texto, nome, enter=True):
    """Clica no número, apaga o que há (End + Backspace) e escreve `texto` (+ Enter)."""
    painel = grande.antes_e_depois
    campo = painel.campo_pagina
    base.clique(grande, campo)
    base.tecla(grande, VK_END)
    base.tecla(grande, VK_BACK, vezes=4)
    base.digitar(grande, texto, enter=enter)
    esperar_previa(painel)
    anotar(nome, estado(grande))


def fase_novo(j, grande):
    from core import automatico as A
    painel = grande.antes_e_depois
    anotar("abriu-o-automatico", estado(grande))
    p(grande, "abriu-na-30")
    setas(grande, "ao-abrir")
    # D-617: escrever 45 e Enter vai à folha 45
    escrever(grande, "45", "escreveu-45-enter")
    base.conferir(painel._indice == 44 and painel.contador.text() == "página 45 de 70",
                  "45 + Enter mostra a página 45")
    p(grande, "escreveu-45")
    # as setas do teclado depois de escrever
    setas(grande, "depois-de-escrever")
    base.conferir(painel._indice == 45, "as setas do teclado continuam depois de escrever (Direita, Direita, Esquerda = 46)")
    # vazio e fora do intervalo: volta ao número atual, sem mensagem
    escrever(grande, "", "vazio-enter")
    base.conferir(painel._indice == 45 and painel.campo_pagina.text() == "46", "vazio + Enter: fica na 46")
    escrever(grande, "0", "zero-enter")
    base.conferir(painel._indice == 45 and painel.campo_pagina.text() == "46", "0 + Enter: fica na 46")
    escrever(grande, "99", "noventa-e-nove-enter")
    base.conferir(painel._indice == 45 and painel.campo_pagina.text() == "46", "99 + Enter: fica na 46")
    p(grande, "fora-do-intervalo-fica")
    # < > com o mouse
    base.clique(grande, painel.botao_anterior)
    esperar_previa(painel)
    anotar("clicou-<", estado(grande))
    base.conferir(painel._indice == 44, "< com o mouse volta uma")
    # D-614: com o Dividir marcado, < > andam pelas metades
    item = grande.lista.item_da_etapa(A.DIVIDIR)
    from PySide6.QtCore import Qt
    if item.checkState() != Qt.Checked:
        item.setCheckState(Qt.Checked)
    esperar_previa(painel)
    escrever(grande, "30", "dividir-escreveu-30")
    p(grande, "dividir-30-esquerda")
    passos = []
    for k in range(3):
        base.clique(grande, painel.botao_proxima)
        esperar_previa(painel)
        passos.append(estado(grande))
        anotar(f"dividir-clicou->-{k + 1}", passos[-1])
        p(grande, f"dividir-depois-de->-{k + 1}")
    base.conferir([(s["indice"], s["metade"]) for s in passos][:1] == [(29, "direita")] or passos[0]["indice"] == 29,
                  "com o Dividir, o > da 30 mostra a outra metade da mesma folha")
    setas(grande, "dividir-teclado")


def main():
    j, grande = abrir()
    {"base": fase_base, "novo": fase_novo}[FASE](j, grande)
    j._fechar_a_janela_do_automatico()
    base.esperar(1.0)
    base.fechar(j)
    base.gravar_resultados(AQUI / f"resultado-{FASE}")


if __name__ == "__main__":
    main()
