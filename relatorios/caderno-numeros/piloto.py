"""D-604 na janela de VERDADE (plataforma Windows), posta fora da tela: os números das páginas nas
folhas do caderno. Como relatorios/mover-parou/piloto.py (ramo mover-parou-2026-11-04): cliques por
mensagens do Windows ao hwnd (relatorios/obra-etapa3/roteiro/base.py), prints por PrintWindow.

Dados, projetos e TEMP numa pasta própria no scratchpad. O projeto do Gradus é COPIADO da pasta
`dados-teste-rodada-de-consertos` (que só é lida) e o PDF também; na cópia, o caminho do PDF aponta
para a cópia do PDF.

O que faz (prints em relatorios/caderno-numeros/prints/):
  1. Automático, etapa 7 aberta (só "Montar cadernos" marcada, 20 por caderno): folha 1, folha 2
     (clicando "›"), a última folha (as páginas em branco do fim do último caderno).
  2. Marca a etapa 1 "Dividir" (D-603): folha 1 com as páginas já divididas.
  3. "tela cheia": a tela grande de caderno.
  4. "Montar para imprimir" (DialogoImpressao, a janela que a tela "Ficou pronto!" abre), Livreto
     20 por caderno: folha 1, folha 2 (clicando "›").

Rodar (na cópia caderno-numeros):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\caderno-numeros\\piloto.py
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

SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\195a7ef9582f81cd\e4fd3df2-ffc2-4ff8-9d6b-c5c2f4b2d0ca"
               r"\scratchpad\caderno-numeros-dados")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
LARGURA, ALTURA = 1536, 824
LOG = open(AQUI / "anotacoes.txt", "w", encoding="utf-8")
N = [0]


def anotar(chave, valor=None):
    linha = f"{chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    LOG.write(linha + "\n")
    LOG.flush()


def p(widget, nome):
    N[0] += 1
    return base.print_window(widget, AQUI / "prints" / f"{N[0]:02d}-{nome}.png", so_cliente=False)


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


def esperar_folha(folhas, limite=240):
    t = time.time()
    base.esperar(0.5)
    while time.time() - t < limite and (folhas.calculando() or folhas.faces() is None):
        base.esperar(0.3)
    base.esperar(0.8)
    return round(time.time() - t, 1)


def linhas(rotulos, numeros) -> dict:
    return {lado: rotulos[lado].text() + numeros[lado].text() for lado in ("frente", "verso")}


def parte_automatico(j):
    from PySide6.QtCore import Qt

    from core import automatico as A

    estado = j.estado_do_automatico
    estado.marcadas = {A.CADERNOS}
    estado.opcoes["paginas_por_caderno"] = 20
    grande = j.abrir_o_automatico(A.CADERNOS)
    base.esperar(1.5)
    folhas = grande.folhas_do_caderno
    anotar("paginas no livro (como está)", len(j.projeto.paginas_ativas))
    anotar("folha 1 (s)", esperar_folha(folhas))
    anotar("folha 1", linhas(folhas.rotulos, folhas.numeros_das_paginas))
    p(grande, "etapa7-folha-1")

    base.clique(grande, folhas.botao_seguinte)
    anotar("folha 2 logo depois do clique", linhas(folhas.rotulos, folhas.numeros_das_paginas))
    anotar("folha 2 (s)", esperar_folha(folhas))
    p(grande, "etapa7-folha-2")

    for _ in range(folhas.total()):
        if not folhas.botao_seguinte.isEnabled():
            break
        base.clique(grande, folhas.botao_seguinte)
        base.esperar(0.15)
    anotar("ultima folha (s)", esperar_folha(folhas))
    anotar("ultima folha", linhas(folhas.rotulos, folhas.numeros_das_paginas))
    p(grande, "etapa7-ultima-folha")
    base.clique(grande, folhas.botao_anterior)
    anotar("penultima folha (s)", esperar_folha(folhas))
    anotar("penultima folha", linhas(folhas.rotulos, folhas.numeros_das_paginas))
    p(grande, "etapa7-penultima-folha")
    # o lugar em branco do último caderno (70 páginas: o último caderno tem 10 páginas em 12
    # lugares; os 2 lugares sem página caem na primeira folha dele): voltar até aparecer
    for _ in range(4):
        if "em branco" in "".join(linhas(folhas.rotulos, folhas.numeros_das_paginas).values()):
            break
        base.clique(grande, folhas.botao_anterior)
        base.esperar(0.3)
    anotar("folha com lugar em branco (s)", esperar_folha(folhas))
    anotar("folha com lugar em branco", linhas(folhas.rotulos, folhas.numeros_das_paginas))
    p(grande, "etapa7-folha-com-lugar-em-branco")

    # D-603: marcar "Dividir" na lista (a caixinha da etapa 1)
    item = grande.painel_de_opcoes.lista.item_da_etapa(A.DIVIDIR)
    item.setCheckState(Qt.Checked)
    base.esperar(1.0)
    folhas.posicao = 0
    folhas.pedir(agora=True)
    anotar("com Dividir, folha 1 (s)", esperar_folha(folhas, 400))
    anotar("com Dividir, folha 1", linhas(folhas.rotulos, folhas.numeros_das_paginas))
    p(grande, "etapa7-dividir-folha-1")

    base.clique(grande, folhas.botao_tela_cheia)
    base.esperar(2.5)
    tela = folhas.tela_grande
    anotar("tela grande", linhas(tela.rotulos, tela.numeros_das_paginas))
    p(tela, "tela-grande-folha-1")
    base.clique(tela, tela.botao_proxima)
    anotar("tela grande, folha 2 logo depois do clique", linhas(tela.rotulos, tela.numeros_das_paginas))
    anotar("tela grande folha 2 (s)", esperar_folha(folhas, 400))
    base.esperar(1.0)
    anotar("tela grande, folha 2", linhas(tela.rotulos, tela.numeros_das_paginas))
    p(tela, "tela-grande-folha-2")
    tela.reject()
    base.esperar(0.5)
    grande.reject()
    base.esperar(1.0)


def parte_montar_para_imprimir(j):
    from core import impressao as imp
    from ui.dialogo_impressao import DialogoImpressao

    dialogo = DialogoImpressao(j.projeto.caminho_entrada, j)
    o = imp.OpcoesDeImpressao()
    o.formato = imp.LIVRETO
    o.paginas_por_caderno = 20
    dialogo.definir_opcoes(o)
    dialogo.show()

    def quieta():
        return (not dialogo._relogio_da_previa.isActive()
                and not (dialogo.tarefa_previa is not None and dialogo.tarefa_previa.isRunning())
                and not dialogo._previa_pendente and not dialogo.bolinha_da_previa.carregando
                and dialogo.folha_na_tela is not None)

    def esperar(limite=120):
        t = time.time()
        base.esperar(0.5)
        while time.time() - t < limite and not quieta():
            base.esperar(0.3)
        base.esperar(0.8)

    esperar()
    anotar("montar para imprimir: paginas do PDF", dialogo.paginas_do_livro)
    anotar("montar para imprimir, folha 1", linhas(dialogo.rotulos_da_face, dialogo.paginas_da_face))
    p(dialogo, "montar-para-imprimir-folha-1")
    base.clique(dialogo, dialogo.botao_folha_seguinte)
    anotar("montar para imprimir, folha 2 logo depois do clique",
           linhas(dialogo.rotulos_da_face, dialogo.paginas_da_face))
    esperar()
    anotar("montar para imprimir, folha 2", linhas(dialogo.rotulos_da_face, dialogo.paginas_da_face))
    p(dialogo, "montar-para-imprimir-folha-2")
    dialogo.reject()
    base.esperar(1.0)


def main():
    base.preparar(str(RAIZ), str(SCRATCH), limpar=False)
    import projetos

    pasta = preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(LARGURA, ALTURA)
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    esperar_tela(j)
    p(j, "abriu")
    parte_automatico(j)
    parte_montar_para_imprimir(j)
    base.fechar(j)


if __name__ == "__main__":
    main()
