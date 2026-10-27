"""Prova "projeto antigo sai igual" com valores à mão (obra 26/10/2026, etapa 1).

PARA QUÊ
    A prova de fábrica (somas_todas.sh, 96 de 96) usa livros novos sem nada à
    mão: não pega a mudança desta etapa. Esta pega: um projeto.json gravado
    ANTES da etapa 1 (sem o campo feito_a_mao_sempre_vale), com corte, ângulo,
    filtro, pedaço "só neste pedaço" e mover feitos à mão, em várias combinações
    de caixinhas, é aberto por Projeto.de_dicionario e processado pelo
    core.pipeline.processar - no código antigo (--raiz da worktree ddd4d74) e
    no novo. As somas (SHA-256 dos pontos de cada página do PDF) têm de ser
    iguais.

    Variantes (todas em páginas do gabarito que vão ser impressas):
      desligado-cortar-antes   caixinhas desligadas, ordem antiga (sem o campo)
      desligado-endireitar-antes  caixinhas desligadas, ordem do livro novo
      ligado-endireitar-antes  cortar + endireitar + limpar + gravura ligados
      so-limpar                só "Limpar a folha" (Preto e branco), sem marcação

USO (da pasta da worktree obra-etapa1; um processo por variante)
    python relatorios\\obra-etapa1\\scripts\\prova_projeto_antigo.py --raiz <código> --saida s.json <variante>

Lê o gabarito (somente leitura). Dados do programa numa pasta temporária.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve()
WORKTREE = AQUI.parents[3]
GABARITO = Path(r"D:\programas\EditorImpressao\gabarito\paginas")
_DADOS = Path(tempfile.gettempdir()) / "obra_etapa1_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)

PAGINAS = ["escola_p007", "horas_p013", "marial_p007", "opusmajus_p011", "boecio_p022",
           "graduale_p221"]

VARIANTES = {
    "desligado-cortar-antes": dict(cortar_bordas=False, endireitar=False, limpar=False,
                                   detectar_regioes=False, ordem=None),
    "desligado-endireitar-antes": dict(cortar_bordas=False, endireitar=False, limpar=False,
                                       detectar_regioes=False, ordem="endireitar_antes"),
    "ligado-endireitar-antes": dict(cortar_bordas=True, endireitar=True, limpar=True,
                                    detectar_regioes=True, ordem="endireitar_antes"),
    "so-limpar": dict(cortar_bordas=False, endireitar=False, limpar=True,
                      detectar_regioes=False, ordem="endireitar_antes"),
}


def _livro(destino: Path) -> Path:
    import fitz

    saida = fitz.open()
    for pid in PAGINAS:
        with fitz.open(str(GABARITO / f"{pid}.pdf")) as um:
            saida.insert_pdf(um)
    saida.save(str(destino))
    saida.close()
    return destino


def _dicionario_antigo(entrada: Path, saida: Path, variante: dict) -> dict:
    """O projeto.json como o programa gravava ANTES da etapa 1: as opções do
    livro, uma folha por página e os valores à mão (sem os campos novos)."""
    import fitz

    with fitz.open(str(entrada)) as doc:
        total = len(doc)
    pedaco = [{"tipo": "papel", "forma": "retangulo", "pontos": [[0.0, 0.0], [1.0, 0.4]],
               "operacao": "somar", "origem": "mao", "filtro": "preto_e_branco"}]
    paginas = []
    for i in range(total):
        pagina = {"indice": i, "folha": i, "metade": "inteira", "filtro": "original"}
        if i % 2 == 0:
            pagina["recorte"] = [0.05, 0.04, 0.9, 0.92]
        if i % 2 == 1:
            pagina["angulo_manual"] = 1.5
        if i % 3 == 0:
            pagina["filtro"] = "preto_e_branco"
        if i == 1:
            pagina["selecao"] = pedaco
        if i == 2:
            pagina["conteudo_deslocamento"] = [0.05, 0.0]
        if i == 4:
            pagina["conteudo_escala"] = 0.9
            pagina["conteudo_deslocamento"] = [-0.03, 0.02]
        paginas.append(pagina)
    dados = {
        "caminho_entrada": str(entrada), "caminho_saida": str(saida), "nome": "prova",
        "dividir_folhas": False, "dividir_como": "programa", "filtro_padrao": "original",
        "montar_cadernos": False, "qualidade_dpi": 300, "endireitar_como": "programa",
        "cortar_bordas": variante["cortar_bordas"], "endireitar": variante["endireitar"],
        "limpar": variante["limpar"], "detectar_regioes": variante["detectar_regioes"],
        "folhas": [{"indice": i, "dividir": False} for i in range(total)],
        "paginas": paginas,
    }
    if variante["ordem"]:
        dados["ordem_do_preparo"] = variante["ordem"]
    return dados


def _somas(caminho: Path) -> list[str]:
    import fitz

    somas = []
    with fitz.open(str(caminho)) as doc:
        for pagina in doc:
            h = hashlib.sha256(f"{pagina.rect.width:.3f}x{pagina.rect.height:.3f}".encode())
            for info in pagina.get_images(full=True):
                pix = fitz.Pixmap(doc, info[0])
                h.update(f"{pix.width}x{pix.height}x{pix.n}".encode())
                h.update(pix.samples)
            somas.append(h.hexdigest())
    return somas


def main() -> int:
    analisador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analisador.add_argument("--raiz", type=Path, required=True)
    analisador.add_argument("--saida", type=Path, required=True)
    analisador.add_argument("variante", choices=sorted(VARIANTES))
    opcoes = analisador.parse_args()
    sys.path.insert(0, str(opcoes.raiz.resolve()))
    from core.pipeline import processar
    from modelos import Projeto

    resultado = (json.loads(opcoes.saida.read_text(encoding="utf-8"))
                 if opcoes.saida.is_file() else {})
    with tempfile.TemporaryDirectory(dir=str(_DADOS)) as tmp:
        entrada = _livro(Path(tmp) / "livro.pdf")
        pdf = Path(tmp) / "saida.pdf"
        projeto = Projeto.de_dicionario(_dicionario_antigo(entrada, pdf, VARIANTES[opcoes.variante]))
        processar(projeto)
        for i, soma in enumerate(_somas(pdf)):
            resultado[f"{opcoes.variante}|{i}"] = soma
    opcoes.saida.write_text(json.dumps(resultado, indent=1, sort_keys=True), encoding="utf-8")
    print(opcoes.variante, "ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
