"""D-619 e D-620 na janela de VERDADE (plataforma Windows), posta fora da tela, como o piloto do
mover-parou (relatorios/mover-parou/piloto.py, ramo mover-parou-2026-11-04): cliques e teclas
por mensagens do Windows ao hwnd (relatorios/obra-etapa3/roteiro/base.py), prints por
PrintWindow.

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus Primus (o livro do
print a-69) é COPIADO da pasta `dados-teste-rodada-de-consertos` (que só é lida) e o PDF também;
na cópia, o caminho do PDF aponta para a cópia.

Rodar (na cópia painel-livro):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\painel-livro\\piloto.py <largura> <altura>
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

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f\scratchpad\painel-livro-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA = int(sys.argv[1]) if len(sys.argv) > 1 else 1366
ALTURA = int(sys.argv[2]) if len(sys.argv) > 2 else 728
FASE = f"{LARGURA}"
LOG = open(AQUI / f"anotacoes-{'opcoes' if FASE == '0' else FASE}.txt", "w", encoding="utf-8")
N = [0]


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n"); LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / "prints" / f"{FASE}-{N[0]:02d}-{nome}.png", so_cliente=True)


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


def barra(j):
    """As medidas da barra de baixo: cada peça à vista cabe inteira dentro dela? A conta do
    livro (nome · N de M conferidas · K com dúvida) aparece inteira?"""
    from PySide6.QtWidgets import QWidget
    t = j.tela_conferir
    b = t.rotulo_do_livro.parentWidget()
    pecas = []
    for w in b.findChildren(QWidget):
        if w.parentWidget() is not b or not w.isVisible():
            continue
        g = w.geometry()
        texto = getattr(w, "text", lambda: "")() if hasattr(w, "text") else ""
        if not texto and hasattr(w, "currentText"):
            texto = w.currentText()
        pecas.append({"peca": texto or type(w).__name__, "x": g.x(), "dir": g.right(),
                      "larg": g.width(), "pede": w.sizeHint().width(),
                      "espremida": g.width() < w.minimumSizeHint().width()})
    pecas.sort(key=lambda d: d["x"])
    fora = [d["peca"] for d in pecas if d["dir"] > b.width() or d["x"] < 0]
    espremidas = [d["peca"] for d in pecas if d["espremida"] and d["peca"] != "_RotuloDoLivro"]
    rotulo = t.rotulo_do_livro
    return {"janela": [j.width(), j.height()], "barra_larg": b.width(),
            "barra_minimo": b.minimumSizeHint().width(),
            "conta_na_tela": rotulo.text(), "conta_inteira": rotulo.texto_inteiro(),
            "conta_cortada": "…" in rotulo.text(), "fora_da_barra": fora,
            "espremidas": espremidas, "pecas": pecas}


def ferramenta(j, letra):
    base.tecla(j, ord(letra)); base.esperar(2.0)


def textos_do_quadro(j, aba):
    from PySide6.QtWidgets import QAbstractButton, QFrame, QLabel
    painel = j.tela_conferir.propriedades_das_abas[aba]
    quadro = [q for q in painel.findChildren(QFrame) if q.objectName() == "parteDoLivro"][0]
    return [w.text() for w in quadro.findChildren(QLabel) + quadro.findChildren(QAbstractButton)]


def main():
    base.preparar(str(RAIZ), str(SCRATCH), limpar=False)
    from ui.tela_conferir import ABA_ANGULO, ABA_BORDAS, ABA_CORTE
    import configuracoes
    import projetos
    configuracoes.escrever("qualidade_previa", "rapida")
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("abriu-em-s", esperar_tela(j))
    t = j.tela_conferir

    # D-619: o quadro com o título novo, no Cortar, no Dividir e no Endireitar
    for letra, aba, nome in (("X", ABA_BORDAS, "cortar"), ("D", ABA_CORTE, "dividir"),
                             ("I", ABA_ANGULO, "endireitar")):
        ferramenta(j, letra)
        rolagem = t.propriedades_das_abas[aba]
        # o quadro fica no fim do painel: rola até ele para o print
        from PySide6.QtWidgets import QScrollArea
        pai = rolagem.parentWidget()
        while pai is not None and not isinstance(pai, QScrollArea):
            pai = pai.parentWidget()
        if pai is not None:
            pai.verticalScrollBar().setValue(pai.verticalScrollBar().maximum()); base.esperar(0.5)
        anotar(f"quadro-{nome}", {"aba": t.aba_atual, "textos": textos_do_quadro(j, aba),
                                 "painel": t.paineis.aberto})
        p(j, f"quadro-{nome}")

    # D-620: a barra de baixo com o Propriedades aberto (o caso mais apertado de todo dia)
    ferramenta(j, "X")
    anotar("barra-cortar-com-painel", barra(j))
    p(j, "barra-cortar-com-painel")
    # a mesma barra sem a qualidade (como era antes), para comparar a folga
    t.rotulo_da_qualidade.hide(); t.seletor_qualidade.hide(); base.esperar(0.8)
    anotar("barra-sem-a-qualidade-para-comparar", barra(j))
    t.rotulo_da_qualidade.show(); t.seletor_qualidade.show(); base.esperar(0.8)
    # miniaturas fechadas (a seta delas, clique de verdade): o "Confirmar e processar" desce para
    # a barra (D-050) - o caso mais cheio da barra
    base.clique(j, t.miniaturas.seta); base.esperar(1.5)
    anotar("barra-miniaturas-fechadas", barra(j))
    p(j, "barra-miniaturas-fechadas")
    base.clique(j, t.miniaturas.seta); base.esperar(1.5)

    # D-620: trocar a qualidade no Cortar, pela lista da barra (clique de verdade), e ver nas outras
    base.clique(j, t.seletor_qualidade); base.esperar(1.0)
    vista = t.seletor_qualidade.view()
    popup = vista.window()
    anotar("lista-aberta", {"visivel": popup.isVisible(), "itens": [t.seletor_qualidade.itemText(i) for i in range(3)]})
    if popup.isVisible():
        p(popup, "lista-aberta")
        indice = vista.model().index(2, 0)
        r = vista.visualRect(indice)
        base.clique(popup, vista.viewport(), r.center()); base.esperar(2.5)
    anotar("depois-de-escolher-alta", {"lista": t.seletor_qualidade.currentText(),
                                        "gravada": configuracoes.ler("qualidade_previa"),
                                        "dpi_da_tela": t._dpi_normal,
                                        "previas": t.previas.dpi_da_tela, "aba": t.aba_atual})
    p(j, "alta-no-cortar")
    for letra, nome in (("I", "endireitar"), ("F", "mover"), ("D", "dividir")):
        ferramenta(j, letra); base.esperar(2.0)
        anotar(f"alta-no-{nome}", {"lista": t.seletor_qualidade.currentText(),
                                  "visivel": t.seletor_qualidade.isVisible(),
                                  "dpi_da_tela": t._dpi_normal, "aba": t.aba_atual})
        p(j, f"alta-no-{nome}")
    anotar("barra-dividir", barra(j))
    # volta à de fábrica do teste
    t.seletor_qualidade.setCurrentIndex(0); base.esperar(1.0)
    base.fechar(j)
    base.gravar_resultados(AQUI / "prints")


def recorte_da_barra(j, nome):
    """Print da janela e, ao lado, só a faixa de baixo (a barra), para a pergunta ao Samuel."""
    img = p(j, nome)
    if img is not None:
        w, h = img.size
        img.crop((0, h - 70, w, h)).save(AQUI / "prints" / f"{FASE}-{N[0]:02d}-{nome}-faixa.png")


def opcoes():
    """Para a pergunta ao Samuel: o mesmo livro, no Cortar com o Propriedades aberto, em 1536
    (a tela dele: 1920 com letra a 125%) e em 1366, com três jeitos de pôr a qualidade na barra.
    Nada aqui fica no programa: só muda o texto das peças da barra nesta janela de teste."""
    base.preparar(str(RAIZ), str(SCRATCH), limpar=False)
    import configuracoes
    import projetos
    configuracoes.escrever("qualidade_previa", "rapida")
    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(1536, 800)
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    anotar("abriu-em-s", esperar_tela(j))
    t = j.tela_conferir
    ferramenta(j, "X")
    lista, rotulo = t.seletor_qualidade, t.rotulo_da_qualidade

    def jeito(qual):
        nomes = {"A": ["Rápida", "Média", "Alta"], "B": ["Rápida", "Média", "Alta"],
                 "C": ["Prévia rápida", "Prévia média", "Prévia alta"],
                 "antes": ["Rápida", "Média", "Alta"], "agora": ["Rápida", "Média", "Alta"]}[qual]
        for i, n in enumerate(nomes):
            lista.setItemText(i, n)
        rotulo.setText("prévia" if qual == "B" else "Qualidade da prévia")
        rotulo.setVisible(qual in ("B", "agora"))
        lista.setVisible(qual != "antes")
        lista.adjustSize()
        base.esperar(1.0)

    for largura in (1536, 1366):
        j.resize(largura, 728 if largura == 1366 else 800); base.esperar(1.5)
        for qual in ("antes", "agora", "A", "B", "C"):
            jeito(qual)
            medida = barra(j)
            anotar(f"opcao-{qual}-{largura}", {k: medida[k] for k in (
                "janela", "barra_larg", "barra_minimo", "conta_na_tela", "conta_cortada",
                "espremidas")})
            recorte_da_barra(j, f"opcao-{qual}-{largura}")
    jeito("agora")
    base.fechar(j)


if __name__ == "__main__":
    if FASE == "0":
        FASE = "opcoes"
        opcoes()
    else:
        main()
