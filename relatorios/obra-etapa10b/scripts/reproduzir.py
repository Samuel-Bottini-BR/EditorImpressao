"""Reproduz uma página dos testes dos 14 livros (23/10/2026) pelo caminho inteiro.

PARA QUÊ (obra de 26/10, etapa 10a)
    Os defeitos de geometria da lista única (4.2, 4.4, 4.8, 4.10, 1.4) foram achados
    pelo verificador com a janela de verdade; o projeto de cada livro ficou gravado
    em D:\\programas\\EditorImpressao-arquivos\\testes-livros-saida\\<livro>\\trab\\
    projetos\\<livro>\\projeto.json (com as caixinhas e o que foi feito à mão). Aqui
    o projeto é lido (só leitura) e a página passa pelo MESMO corpo do processar
    (core.pipeline._pagina_pronta), com o filtro do livro e também em Original
    (para ver só a geometria). Regra de 22/10 (`a-comer-pagina`): "Primeiro provar
    em páginas de verdade".

USO (da pasta da worktree):
    python relatorios/obra-etapa10a/scripts/reproduzir.py --raiz <código> --saida <pasta> livro:pagina [...]
    pagina = número da página no PDF da cópia do teste, começando em 1.
    --campos '{"borda_preta": false}' troca campos do projeto (opcional).
    --sem-mao  esquece o que foi feito à mão na página (recorte, ângulo).

Grava <pasta>/<livro>-p<NNN>-<rotulo>.png (pronta em Original e com o filtro do
livro, e o original da folha) e imprime o tamanho da página pronta em cm.
A pasta de dados do programa vai para uma pasta temporária.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ACERVO_TESTES = Path(r"D:\programas\EditorImpressao-arquivos\testes-livros-saida")
COPIAS = {
    "antiphon": "antiphon-trecho.pdf", "boecio": "boecio.pdf", "cursus": "cursus.pdf",
    "escola": "escola.pdf", "graduale": "graduale-trecho.pdf", "horas": "horas-trecho.pdf",
    "ljs47": "ljs47.pdf", "marial": "marial-trecho.pdf", "matematica": "matematica.pdf",
    "palatino": "palatino.pdf", "pesel": "pesel.pdf", "righetti": "righetti.pdf",
    "siebmacher": "siebmacher.pdf", "valades": "valades.pdf",
}

_DADOS = Path(tempfile.gettempdir()) / "etapa10b_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)


def carregar(livro: str, campos: dict | None = None):
    """O Projeto salvo do teste do livro, apontando para a cópia do PDF."""
    from modelos import Projeto

    base = ACERVO_TESTES / livro / "trab"
    pasta = base / "projetos" / Path(COPIAS[livro]).stem
    dados = json.loads((pasta / "projeto.json").read_text(encoding="utf-8"))
    projeto = Projeto.de_dicionario(dados)
    projeto.caminho_entrada = str(base / COPIAS[livro])
    for chave, valor in (campos or {}).items():
        setattr(projeto, chave, valor)
    return projeto


ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
LIVROS_DO_ACERVO = {
    "antiphon": "Antiphon_25.pdf", "boecio": "Sobre a Consolação da Filosofia - Severino Boécio.pdf",
    "cursus": "Cursus philosophicus. Tomo.2.pdf", "escola": "Na escola de Jesus - Catecismo explicado com imagens..pdf",
    "graduale": "Graduale - Saeculum XIV.pdf", "horas": "Livro de Horas - Luís XIV.pdf", "ljs47": "ljs47.pdf",
    "marial": "Marial de sermoens - Frei Balthasar Paez. (1).pdf", "matematica": "Matemática Para vencer.pdf",
    "palatino": "Giovambattista Palatino cittadino romano.pdf",
    "pesel": "POINTS d´ANCIENNES BRODERIES ANGLAISES - Louisa F. Pesel.pdf",
    "righetti": "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf",
    "siebmacher": "Schön Neues Modell Buch - Johann Siebmacher.pdf",
    "valades": "Rhetorica Christiana -  Fray Diego Valadés.pdf",
}


def carregar_de_fabrica(livro: str, numero: int, campos: dict | None = None):
    """Livro NOVO de fábrica com só a página `numero` do livro do acervo (cópia
    de uma página numa pasta temporária; o acervo é só lido). Devolve
    (projeto, 1). `campos` troca opções do livro ANTES da análise."""
    import fitz

    from core.pipeline import analisar_projeto
    from modelos import Projeto

    pasta = _DADOS / "paginas"
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"{livro}_p{numero:03d}.pdf"
    if not destino.is_file():
        with fitz.open(str(ACERVO / LIVROS_DO_ACERVO[livro])) as doc:
            um = fitz.open()
            um.insert_pdf(doc, from_page=numero - 1, to_page=numero - 1)
            um.save(str(destino))
            um.close()
    projeto = Projeto(caminho_entrada=str(destino), caminho_saida=str(pasta / "saida.pdf"),
                      nome=destino.stem)
    campos = dict(campos or {})
    girar = campos.pop("_girar_e_dividir", None)
    for chave, valor in campos.items():
        setattr(projeto, chave, valor)
    projeto = analisar_projeto(projeto)
    if girar is not None:
        # folha dupla escaneada deitada (Righetti): gira e divide como a pessoa
        # faria na tela (o automático não gira sozinho, Lista de bugs 22/10)
        from core import pipeline
        from core.endireitar import girar_90
        from core.pdf_io import abrir_pdf, pagina_para_array
        from modelos import ConfigPagina

        doc = abrir_pdf(str(destino))
        img = girar_90(pagina_para_array(doc, 0, dpi=pipeline.DPI_ANALISE), int(girar))
        doc.close()
        folha = projeto.folhas[0]
        folha.rotacao, folha.dividir = int(girar), True
        folha.posicao_corte = pipeline.achar_divisao(img, projeto.dividir_como, pipeline.DPI_ANALISE).posicao
        filtro = projeto.paginas[0].filtro
        projeto.paginas = [ConfigPagina(indice=0, folha=0, metade="esquerda", filtro=filtro),
                           ConfigPagina(indice=1, folha=0, metade="direita", filtro=filtro)]
    return projeto, 1


def carregar_gabarito(pid: str, campos: dict | None = None):
    """Etapa 10b: livro NOVO de fábrica com a página-gabarito `pid` (ex.:
    palatino_p005), como o rodada_processar.py faz. Devolve (projeto, 1)."""
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    raiz = Path(__file__).resolve().parents[3]
    entrada = raiz / "gabarito" / "paginas" / f"{pid}.pdf"
    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(_DADOS / "saida.pdf"),
                      nome=pid)
    for chave, valor in (campos or {}).items():
        setattr(projeto, chave, valor)
    return analisar_projeto(projeto), 1


def refazer_a_sobra(projeto, numero: int) -> None:
    """Mede de novo o corte da sobra da folha `numero` com o código de `--raiz`
    (como a análise de um livro novo faria), para o projeto salvo antes do
    conserto da etapa 10a ganhar a folga do giro."""
    from core import pipeline
    from core.endireitar import detectar_angulo
    from core.pdf_io import abrir_pdf, pagina_para_array

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img = pagina_para_array(doc, numero - 1, dpi=pipeline.DPI_ANALISE)
    finally:
        doc.close()
    folha = projeto.folhas[numero - 1]
    sobra = pipeline.achar_sobra(img, pipeline.DPI_ANALISE)
    if hasattr(pipeline, "folga_do_giro_na_sobra"):
        sobra = pipeline.folga_do_giro_na_sobra(sobra, img.shape, detectar_angulo(img).angulo,
                                                pipeline.DPI_ANALISE)
    print("sobra", folha.sobra, "->", sobra)
    folha.sobra = sobra


def paginas_da_folha(projeto, numero: int):
    """As páginas ativas que vêm da folha `numero` (1 = primeira)."""
    return [p for p in projeto.paginas if p.folha == numero - 1 and not p.apagada]


def pronta(projeto, pagina, filtro: str | None = None):
    """A página pronta, como no PDF (o corpo do processar)."""
    from core import pipeline
    from core.pdf_io import abrir_pdf

    if filtro is not None:
        pagina.filtro = filtro
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        folha = projeto.folhas[pagina.folha]
        img, _mono = pipeline._pagina_pronta(projeto, doc, folha, pagina, pipeline._FolhaDaVez(), 0)
    finally:
        doc.close()
    return img


def original(projeto, numero: int, dpi: int = 150):
    from core.pdf_io import abrir_pdf, pagina_para_array

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        return pagina_para_array(doc, numero - 1, dpi=dpi)
    finally:
        doc.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--campos", default="{}")
    ap.add_argument("--rotulo", default="")
    ap.add_argument("--sem-mao", action="store_true")
    ap.add_argument("--refazer-sobra", action="store_true",
                    help="mede de novo o corte da sobra (como a análise de um livro novo)")
    ap.add_argument("--so-original", action="store_true", help="só o filtro Original (rápido)")
    ap.add_argument("--filtro", default="", help="filtro a usar no lugar do da página")
    ap.add_argument("alvos", nargs="+")
    a = ap.parse_args()
    sys.path.insert(0, str(Path(a.raiz).resolve()))
    import cv2

    from core.filtros import ORIGINAL

    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    campos = json.loads(a.campos)
    rot = ("-" + a.rotulo) if a.rotulo else ""
    for alvo in a.alvos:
        livro, numero = alvo.split(":")
        numero = int(numero) if numero.isdigit() else 0
        if livro == "gab":                     # página-gabarito como livro novo
            projeto, no_doc = carregar_gabarito(alvo.split(":", 1)[1], campos)
            numero = 1
            livro = alvo.split(":", 1)[1]
        elif livro.startswith("fab-"):           # livro novo de fábrica, só esta página
            projeto, no_doc = carregar_de_fabrica(livro[4:], numero, campos)
        else:                                  # o projeto salvo do teste dos 14 livros
            projeto, no_doc = carregar(livro, campos), numero
            if a.refazer_sobra:
                refazer_a_sobra(projeto, numero)
        cv2.imwrite(str(saida / f"{livro}-p{numero:03d}-original.png"), original(projeto, no_doc))
        for k, pagina in enumerate(paginas_da_folha(projeto, no_doc)):
            if a.sem_mao:
                pagina.recorte = None
                pagina.angulo_manual = None
            filtros = [ORIGINAL] if a.so_original else [ORIGINAL, a.filtro or pagina.filtro]
            for filtro in dict.fromkeys(filtros):
                img = pronta(projeto, pagina, filtro)
                nome = f"{livro}-p{numero:03d}-{pagina.metade}-{filtro}{rot}.png"
                cv2.imwrite(str(saida / nome), img)
                dpi = projeto.qualidade_dpi
                print(f"{alvo} {pagina.metade} {filtro}: {img.shape[1] / dpi * 2.54:.2f} x "
                      f"{img.shape[0] / dpi * 2.54:.2f} cm  recorte={pagina.recorte} "
                      f"angulo_manual={pagina.angulo_manual} alertas={pagina.alertas}", flush=True)


if __name__ == "__main__":
    main()
