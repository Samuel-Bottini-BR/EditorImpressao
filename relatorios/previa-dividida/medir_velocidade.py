"""D-614: quanto a prévia do Automático leva para mostrar o "depois" de uma página do Gradus Primus
(página 68, folha dupla ainda inteira) com o Dividir marcado, no código de antes e no de agora.

Antes = `ui/automatico.py` e `ui/tarefas.py` do commit `ad563c35` (postos à frente no caminho do
pacote `ui`, só esses dois arquivos); agora = os da cópia. Cada rodada é um processo novo; as
rodadas se alternam (antes, agora, antes, agora...), na mesma máquina.

O projeto do Gradus é COPIADO (com o PDF) para uma pasta de trabalho no scratchpad; a pasta
`dados-teste-rodada-de-consertos` só é lida. Mede:
  - "abrir": ir à página 68 (sem etapa marcada) até o antes e o depois chegarem;
  - "marcar": marcar o Dividir até o depois novo chegar;
  - "outra metade": o ">" (no código de agora, a metade da direita da mesma folha; no de antes,
    a folha seguinte), até a imagem chegar.

Rodar (na cópia previa-dividida):
    .venv\\Scripts\\python.exe relatorios\\previa-dividida\\medir_velocidade.py <antes|agora>
    .venv\\Scripts\\python.exe relatorios\\previa-dividida\\medir_velocidade.py todas 3
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog\05fa28dc-c2f5-4152-b355-e6ab76bb386f"
               r"\scratchpad\previa-dividida-velocidade")
GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
COMMIT_ANTES = "ad563c35"
PAGINA = 67                       # "página 68 de 70"


def preparar_codigo_antigo() -> Path:
    """Os dois arquivos de antes, numa pasta à parte (só eles)."""
    pasta = SCRATCH / "ui-antes"
    pasta.mkdir(parents=True, exist_ok=True)
    for nome in ("automatico.py", "tarefas.py"):
        texto = subprocess.run(["git", "show", f"{COMMIT_ANTES}:ui/{nome}"], cwd=RAIZ,
                               capture_output=True, check=True).stdout
        (pasta / nome).write_bytes(texto)
    return pasta


def preparar_copia(trab: Path) -> Path:
    """O projeto e o PDF copiados; o caminho do PDF aponta para a cópia."""
    livros = SCRATCH / "livros"
    livros.mkdir(parents=True, exist_ok=True)
    pdf = livros / GRADUS.name
    if not pdf.exists():
        shutil.copy2(GRADUS, pdf)
    destino = trab / "projetos" / PROJ_ORIGEM.name
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


def uma_rodada(qual: str) -> dict:
    trab = SCRATCH / f"trab-{qual}"
    (trab / "dados").mkdir(parents=True, exist_ok=True)
    os.environ["LOCALAPPDATA"] = str(trab / "dados")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    sys.path.insert(0, str(RAIZ))
    os.chdir(RAIZ)
    import ui
    if qual == "antes":
        ui.__path__.insert(0, str(preparar_codigo_antigo()))
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    import projetos
    projetos.pasta_dos_projetos = lambda: trab / "projetos"
    pasta = preparar_copia(trab)
    from core import automatico as A
    from ui import automatico as UA
    from ui.janela_principal import JanelaPrincipal
    assert ("ui-antes" in UA.__file__) == (qual == "antes"), UA.__file__

    def esperar(painel, limite=300):
        t = time.perf_counter()
        while time.perf_counter() - t < limite:
            app.processEvents()
            if not painel.calculando():
                app.processEvents()
                if not painel.calculando():
                    return round(time.perf_counter() - t, 3)
            time.sleep(0.005)
        raise SystemExit("não terminou")

    j = JanelaPrincipal()
    j.resize(1536, 824)
    resumo = projetos.ler_resumo(pasta)
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    for _ in range(50):
        app.processEvents()
    j.tela_conferir.ir_para_pagina(PAGINA)
    grande = j.abrir_o_automatico()
    painel = grande.antes_e_depois
    for etapa in A.ETAPAS:                      # nenhuma marcada (como no print a-59 antes do 1)
        grande.estado.marcar(etapa, False)
    esperar(painel)
    painel.ir_para(PAGINA + 1)                  # outra página e volta: o antes é calculado de novo
    esperar(painel)
    t0 = time.perf_counter()
    painel.ir_para(PAGINA)
    esperar(painel)
    abrir = round(time.perf_counter() - t0, 3)
    lista_s = None
    if qual == "agora" and os.environ.get("MEDIR_LISTA"):
        # só a conta dos passos (core/automatico.paginas_do_pdf_depois), fria e guardada
        pedido = A.Pedido(etapas=[A.DIVIDIR], opcoes=dict(grande.estado.opcoes), pular_mexidas=False)
        t0 = time.perf_counter()
        A.paginas_do_pdf_depois(j.projeto, pedido)
        frio = time.perf_counter() - t0
        t0 = time.perf_counter()
        A.paginas_do_pdf_depois(j.projeto, pedido)
        lista_s = (round(frio, 4), round(time.perf_counter() - t0, 4))
    t0 = time.perf_counter()
    grande.estado.marcar(A.DIVIDIR, True)
    painel.pedir(agora=True)
    esperar(painel)
    marcar = round(time.perf_counter() - t0, 3)
    largura = painel._depois[1].shape[1] if painel._depois else None
    t0 = time.perf_counter()
    painel.botao_proxima.click()
    esperar(painel)
    outra = round(time.perf_counter() - t0, 3)
    res = {"qual": qual, "abrir_s": abrir, "marcar_dividir_s": marcar, "seta_s": outra,
           "largura_do_depois": largura, "contador": painel.contador.text(),
           "indice_depois_da_seta": painel._indice, "lista_fria_e_guardada_s": lista_s}
    print(json.dumps(res, ensure_ascii=False), flush=True)
    j._fechar_a_janela_do_automatico()
    os._exit(0)


def todas(vezes: int) -> None:
    py = sys.executable
    linhas = []
    for _ in range(vezes):
        for qual in ("antes", "agora"):
            saida = subprocess.run([py, __file__, qual], capture_output=True, text=True, encoding="utf-8")
            ultima = [x for x in saida.stdout.splitlines() if x.startswith("{")]
            linhas.append(ultima[-1] if ultima else f"ERRO {qual}: {saida.stderr[-800:]}")
            print(linhas[-1], flush=True)
    (AQUI / "velocidade.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1] == "todas":
        todas(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
    else:
        uma_rodada(sys.argv[1])
