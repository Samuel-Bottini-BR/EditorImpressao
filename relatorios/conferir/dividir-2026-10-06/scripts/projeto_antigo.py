"""Projeto antigo abre como estava? (teste de maquina do item 2.1)

Uso:
    python projeto_antigo.py <raiz do codigo> <saida.json>

Monta, com o codigo de <raiz>, o projeto que o programa de antes montava
(gravado no disco e lido de volta, como o projeto.json do Samuel: dividir
marcado, sem os campos do 2.1) para dois pedacos de livro (as 8 primeiras
folhas do Hugon, livro aberto, e as 6 primeiras do Siebmacher, folhas
deitadas), analisa, desenha cada pagina como a previa (preparar_metade, com
corte e endireitar ligados) e gera o PDF final. Grava a soma SHA-256 de cada
pagina desenhada e de cada pagina do PDF (desenhada de volta a 72 DPI), para
comparar o codigo de antes com o de agora. A pasta de dados e propria (ver o bloco logo abaixo).
"""

from __future__ import annotations

# Pasta de dados PROPRIA (nunca a %LOCALAPPDATA%\EditorImpressao do Samuel):
# o programa le LOCALAPPDATA na hora de gravar (historico.pasta_de_dados), e
# os processos filhos herdam. Fica em trabalho\dados-scripts, ao lado deste
# relatorio (fora do git). Pedido da gerente, 06/10/2026.
import os as _os
from pathlib import Path as _Path

_DADOS = _Path(__file__).resolve().parents[1] / "trabalho" / "dados-scripts"
_DADOS.mkdir(parents=True, exist_ok=True)
_os.environ.setdefault("EDITOR_IMPRESSAO_LOCALAPPDATA_REAL", _os.environ.get("LOCALAPPDATA", ""))
_os.environ["LOCALAPPDATA"] = str(_DADOS)

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

LIVROS = [
    (r"D:\Livros para editar\Tractatus Dogmatici (vol. 3)_  - Hugon, Édouard, O.P._7207.pdf", 8),
    (r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE"
     r"\Schön Neues Modell Buch - Johann Siebmacher.pdf", 6),
]


def main() -> int:
    raiz, saida = sys.argv[1:3]
    sys.path.insert(0, raiz)
    import fitz
    from core import pipeline
    from core.pdf_io import abrir_pdf, pagina_para_array
    from modelos import Projeto

    resultado = {}
    for livro, folhas in LIVROS:
        origem = fitz.open(livro)
        pedaco = fitz.open()
        pedaco.insert_pdf(origem, from_page=0, to_page=folhas - 1)
        caminho = Path(tempfile.gettempdir()) / f"antigo_{os.getpid()}_{folhas}.pdf"
        pedaco.save(str(caminho))
        pedaco.close()
        origem.close()

        # o projeto como o programa de ANTES gravava (sem os campos do 2.1)
        antes = Projeto(caminho_entrada=str(caminho), nome="antigo", dividir_folhas=True,
                        detectar_regioes=False)
        dados = json.loads(json.dumps(antes.para_dicionario()))
        for campo in ("dividir_como", "cortar_sobra"):
            dados.pop(campo, None)
        projeto = Projeto.de_dicionario(dados)
        pipeline.analisar_projeto(projeto)

        somas = []
        doc = abrir_pdf(str(caminho))
        try:
            for pagina in projeto.paginas:
                folha = projeto.folhas[pagina.folha]
                img = pagina_para_array(doc, folha.indice, dpi=100)
                pronta = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=100)
                somas.append(hashlib.sha256(pronta.tobytes()).hexdigest()[:16])
        finally:
            doc.close()
        projeto.caminho_saida = str(Path(tempfile.gettempdir()) / f"antigo_saida_{os.getpid()}.pdf")
        final = pipeline.processar(projeto)
        pdf = fitz.open(final)
        no_pdf = [hashlib.sha256(p.get_pixmap(dpi=72).samples).hexdigest()[:16] for p in pdf]
        pdf.close()
        Path(final).unlink(missing_ok=True)
        caminho.unlink(missing_ok=True)
        resultado[Path(livro).stem[:30]] = {
            "folhas": [(f.dividir, round(f.posicao_corte, 6)) for f in projeto.folhas],
            "paginas": len(projeto.paginas), "previas": somas, "pdf": no_pdf}
    Path(saida).write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: (v["paginas"], len(v["pdf"])) for k, v in resultado.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
