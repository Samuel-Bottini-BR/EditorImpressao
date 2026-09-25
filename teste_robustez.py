"""Parte 5: robustez. Cada caso que pode dar errado na mão do Kaique.

Uso:
    python teste_robustez.py "pasta com os livros"

Não altera nenhum PDF de origem: os arquivos defeituosos são fabricados numa
pasta temporária.
"""

from __future__ import annotations

import ctypes
import gc
import shutil
import sys
import tempfile
import time
from pathlib import Path

import fitz
import numpy as np

_ok = _falhou = 0


def checar(descricao: str, condicao: bool, detalhe: str = "") -> bool:
    """Imprime ok/FALHA para uma checagem, soma nos contadores globais e
    devolve a propria condicao (para poder ser usada em `if checar(...)`)."""
    global _ok, _falhou
    if condicao:
        _ok += 1
        print(f"  ok    {descricao}" + (f"  ({detalhe})" if detalhe else ""))
    else:
        _falhou += 1
        print(f"  FALHA {descricao}  ({detalhe})")
    return condicao


def memoria_mb() -> float:
    """Memória do processo agora, em MB.

    Via psutil. A primeira versão chamava GetProcessMemoryInfo por ctypes e
    devolvia 0 em silêncio, o que faria o teste de vazamento passar sempre.
    """
    import psutil

    return psutil.Process().memory_info().rss / 1024 / 1024


# ---------------------------------------------------------------------------
# arquivos defeituosos, fabricados
# ---------------------------------------------------------------------------

def fabricar(pasta: Path) -> dict[str, Path]:
    """Cria, do zero (nunca a partir de um PDF do acervo), um PDF defeituoso
    de cada tipo que pode aparecer na mão do Kaique: pagina unica, tamanhos
    variados, protegido por senha, corrompido de proposito, um arquivo que
    nao e PDF de verdade e um arquivo vazio. Devolve {rotulo: caminho}."""
    import cv2

    arte = np.full((900, 600, 3), 235, dtype=np.uint8)
    arte[100:130, 80:520] = 30
    _, buffer = cv2.imencode(".png", arte)

    arquivos: dict[str, Path] = {}

    # PDF de uma página só
    doc = fitz.open()
    p = doc.new_page(width=420, height=630)
    p.insert_image(fitz.Rect(0, 0, 420, 630), stream=buffer.tobytes())
    arquivos["uma_pagina"] = pasta / "uma_pagina.pdf"
    doc.save(arquivos["uma_pagina"])
    doc.close()

    # PDF com páginas de tamanhos diferentes
    doc = fitz.open()
    for largura, altura in ((420, 630), (840, 420), (300, 900), (420, 630)):
        pag = doc.new_page(width=largura, height=altura)
        pag.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    arquivos["tamanhos_variados"] = pasta / "tamanhos_variados.pdf"
    doc.save(arquivos["tamanhos_variados"])
    doc.close()

    # PDF protegido por senha
    doc = fitz.open()
    pag = doc.new_page(width=420, height=630)
    pag.insert_image(fitz.Rect(0, 0, 420, 630), stream=buffer.tobytes())
    arquivos["com_senha"] = pasta / "com_senha.pdf"
    doc.save(arquivos["com_senha"], encryption=fitz.PDF_ENCRYPT_AES_256,
             owner_pw="segredo", user_pw="segredo")
    doc.close()

    # PDF corrompido: cabeçalho certo, miolo picado
    bons = (pasta / "uma_pagina.pdf").read_bytes()
    arquivos["corrompido"] = pasta / "corrompido.pdf"
    arquivos["corrompido"].write_bytes(bons[:len(bons) // 3] + b"\x00lixo\x00" * 40)

    # arquivo que não é PDF, renomeado
    arquivos["nao_e_pdf"] = pasta / "na_verdade_e_texto.pdf"
    arquivos["nao_e_pdf"].write_text("isto aqui e um texto qualquer, nao um PDF",
                                     encoding="utf-8")

    # arquivo vazio
    arquivos["vazio"] = pasta / "vazio.pdf"
    arquivos["vazio"].write_bytes(b"")

    return arquivos


# ---------------------------------------------------------------------------

def testar_arquivos_ruins(temporaria: Path) -> None:
    """Confere que cada arquivo problematico de `fabricar` e tratado
    corretamente: senha/nao-PDF/vazio/inexistente sao recusados com aviso em
    português (nunca stack trace); o corrompido tanto pode ser recusado
    quanto recuperado (o PyMuPDF as vezes recupera o que da, e isso e melhor
    que recusar); e os formatos incomuns que TEM que funcionar (1 pagina so,
    tamanhos variados) processam ate o fim."""
    from core.pdf_io import ErroPDF, abrir_pdf

    print("\n--- arquivos problemáticos ---")
    arquivos = fabricar(temporaria)

    # O PDF corrompido sai desta lista: o PyMuPDF recupera o que da e a
    # pagina renderiza. Recuperar e MELHOR que recusar para o usuario final,
    # entao ele e testado a parte, exigindo apenas que não derrube o programa.
    for rotulo, chave in (("PDF protegido por senha", "com_senha"),
                          ("arquivo que não é PDF", "nao_e_pdf"),
                          ("arquivo vazio", "vazio"),
                          ("PDF que não existe", None)):
        caminho = arquivos[chave] if chave else temporaria / "nao_existe.pdf"
        try:
            doc = abrir_pdf(caminho)
            doc.close()
            checar(f"{rotulo}: recusado com aviso", False, "abriu sem reclamar")
        except ErroPDF as erro:
            texto = str(erro)
            tecnico = any(t in texto for t in ("Error", "Errno", "Traceback",
                                               "Exception", "None"))
            checar(f"{rotulo}: aviso em português",
                   not tecnico and texto[0].isupper(), texto[:58])
        except Exception as erro:  # noqa: BLE001
            checar(f"{rotulo}: aviso em português", False,
                   f"vazou {type(erro).__name__}")

    # PDF corrompido: exigimos que não trave, seja recusando, seja recuperando
    from core.pdf_io import pagina_para_array

    try:
        doc = abrir_pdf(arquivos["corrompido"])
        try:
            pagina_para_array(doc, 0, dpi=72)
            checar("PDF corrompido: recuperado sem travar", True,
                   f"abriu com {doc.page_count} página(s) e renderizou")
        finally:
            doc.close()
    except ErroPDF as erro:
        checar("PDF corrompido: recusado com aviso em português", True, str(erro)[:50])
    except Exception as erro:  # noqa: BLE001
        checar("PDF corrompido: não pode travar", False,
               f"vazou {type(erro).__name__}")

    # os que TEM que funcionar
    from core.pipeline import analisar_projeto, processar
    from modelos import Projeto

    print("\n--- formatos incomuns que devem funcionar ---")
    for rotulo, chave, esperado in (("PDF de 1 página só", "uma_pagina", 2),
                                    ("PDF de tamanhos variados", "tamanhos_variados", None)):
        try:
            projeto = Projeto(caminho_entrada=str(arquivos[chave]),
                              caminho_saida=str(temporaria / f"saida_{chave}.pdf"),
                              dividir_folhas=True, limpar=True,
                              endireitar=True, cortar_bordas=True)
            analisar_projeto(projeto)
            processar(projeto)
            existe = Path(projeto.caminho_saida).exists()
            checar(f"{rotulo}: processou", existe,
                   f"{len(projeto.folhas)} folhas -> {len(projeto.paginas)} páginas")
        except Exception as erro:  # noqa: BLE001
            checar(f"{rotulo}: processou", False, f"{type(erro).__name__}: {erro}")


def testar_cancelamento(livro: Path, temporaria: Path) -> None:
    """Cancela o processamento no meio (apos a 5a pagina) e confere que
    levanta Cancelou e que nao sobra PDF pela metade no disco."""
    from core.pipeline import Cancelou, analisar_projeto, processar
    from modelos import Projeto

    print("\n--- cancelar no meio ---")
    projeto = Projeto(caminho_entrada=str(livro),
                      caminho_saida=str(temporaria / "cancelado.pdf"),
                      dividir_folhas=False, limpar=True,
                      endireitar=False, cortar_bordas=False)
    analisar_projeto(projeto, cancelado=lambda: False)

    contador = {"n": 0}

    def cancelar_no_quinto() -> bool:
        contador["n"] += 1
        return contador["n"] > 5

    try:
        processar(projeto, cancelado=cancelar_no_quinto)
        checar("cancelar interrompe", False, "processou tudo mesmo assim")
    except Cancelou:
        sobrou = Path(projeto.caminho_saida).exists()
        checar("cancelar interrompe e não deixa PDF pela metade", not sobrou,
               "PDF parcial apagado" if not sobrou else "sobrou arquivo incompleto")
    except Exception as erro:  # noqa: BLE001
        checar("cancelar interrompe", False, f"{type(erro).__name__}: {erro}")


def testar_repetibilidade(livro: Path, temporaria: Path) -> None:
    """Processa o mesmo livro duas vezes e confere que a IMAGEM de saida e
    identica (compara o hash dos pixels renderizados, nao os bytes do
    arquivo - todo PDF leva um /ID unico gerado na hora de gravar)."""
    import hashlib

    from core.pipeline import analisar_projeto, processar
    from modelos import Projeto

    print("\n--- processar duas vezes dá o mesmo resultado ---")
    # Comparamos a IMAGEM renderizada, não os bytes do arquivo: todo PDF leva
    # um identificador unico (/ID) gerado na hora de gravar, entao dois
    # arquivos com o mesmo conteudo nunca tem os mesmos bytes.
    somas = []
    for volta in (1, 2):
        projeto = Projeto(caminho_entrada=str(livro),
                          caminho_saida=str(temporaria / f"repetido_{volta}.pdf"),
                          dividir_folhas=False, limpar=True,
                          endireitar=True, cortar_bordas=True)
        analisar_projeto(projeto)
        projeto.paginas = projeto.paginas[:6]
        processar(projeto)

        from core.pdf_io import abrir_pdf, pagina_para_array

        doc = abrir_pdf(projeto.caminho_saida)
        digestor = hashlib.sha256()
        try:
            for i in range(doc.page_count):
                digestor.update(pagina_para_array(doc, i, dpi=72).tobytes())
        finally:
            doc.close()
        somas.append(digestor.hexdigest()[:16])

    checar("o resultado é idêntico nas duas vezes", somas[0] == somas[1],
           f"{somas[0]} e {somas[1]}")


def testar_pasta_sem_permissao() -> None:
    """Confere que uma unidade inexistente e recusada com mensagem em
    português (nunca um erro tecnico tipo WinError)."""
    import configuracoes

    print("\n--- pasta onde não dá para gravar ---")
    pode, motivo = configuracoes.pode_gravar_em("Z:/nao_existe_de_jeito_nenhum")
    tecnico = any(t in motivo for t in ("Error", "Errno", "WinError"))
    checar("pasta inválida recusada em português", not pode and not tecnico, motivo)


def testar_contagem(livro: Path) -> None:
    """Confere a aritmetica da divisao de folhas: N duplas + M simples tem de
    virar exatamente 2N+M paginas, sem pagina repetida nem folha esquecida."""
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    print("\n--- integridade da contagem ---")
    projeto = Projeto(caminho_entrada=str(livro), dividir_folhas=True, limpar=False,
                      endireitar=False, cortar_bordas=False)
    analisar_projeto(projeto)

    divididas = [f for f in projeto.folhas if f.dividir]
    inteiras = [f for f in projeto.folhas if not f.dividir]
    esperado = len(divididas) * 2 + len(inteiras)
    checar("N folhas duplas viram exatamente 2N páginas",
           len(projeto.paginas) == esperado,
           f"{len(divididas)} duplas + {len(inteiras)} simples = "
           f"{esperado}, saíram {len(projeto.paginas)}")

    origens = [(p.folha, p.metade) for p in projeto.paginas]
    checar("nenhuma página duplicada", len(origens) == len(set(origens)),
           f"{len(origens) - len(set(origens))} repetidas")

    folhas_vistas = {p.folha for p in projeto.paginas}
    checar("nenhuma folha ficou de fora",
           folhas_vistas == set(range(len(projeto.folhas))),
           f"{len(folhas_vistas)} de {len(projeto.folhas)}")


def testar_imposicao() -> None:
    """Simula a dobra fisica de um caderno de 20 paginas e confere que a
    leitura sai 1..20 em ordem - a mesma conta de core.cadernos.conferir_sequencia,
    aqui rodada a mao para ilustrar passo a passo no console."""
    from core.cadernos import montar_ordem

    print("\n--- imposição: simular a dobra de um caderno de 20 ---")
    lados = montar_ordem(20, 20)
    frentes = [l for l in lados if l.frente]
    versos = [l for l in lados if not l.frente]

    print("      folha | frente        | verso")
    for i, (f, v) in enumerate(zip(frentes, versos)):
        print(f"        {i + 1}   | {f.esquerda + 1:>2}  {f.direita + 1:>2}      "
              f"| {v.esquerda + 1:>2}  {v.direita + 1:>2}")

    inicio, fim = [], []
    for f, v in zip(frentes, versos):
        inicio += [f.direita, v.esquerda]
        fim += [f.esquerda, v.direita]
    leitura = [n + 1 for n in inicio + list(reversed(fim))]

    print(f"      dobrando, a leitura sai: {leitura}")
    checar("a dobra devolve 1..20 em ordem", leitura == list(range(1, 21)),
           "conferido página a página")


def testar_vazamento(livros: list[Path], temporaria: Path) -> None:
    """Analisa 5 livros seguidos e confere que a memoria do processo nao fica
    subindo sem parar entre um livro e outro (regra 3: pico nao pode
    acompanhar o tamanho do acervo)."""
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    print("\n--- vazamento de memória: 5 livros seguidos ---")
    base = memoria_mb()
    print(f"      antes de tudo: {base:.0f} MB")

    medidas = []
    for livro in livros[:5]:
        projeto = Projeto(caminho_entrada=str(livro), dividir_folhas=False,
                          limpar=True, endireitar=False, cortar_bordas=False)
        analisar_projeto(projeto)
        del projeto
        gc.collect()
        agora = memoria_mb()
        medidas.append(agora)
        print(f"      depois de {livro.name[:34]:<36} {agora:>6.0f} MB")

    crescimento = medidas[-1] - base
    checar("a memória não cresce sem parar", crescimento < 400,
           f"cresceu {crescimento:+.0f} MB em 5 livros")


def main(pasta: str) -> int:
    """Roda todas as baterias de robustez (arquivos ruins, cancelamento,
    repetibilidade, pasta sem permissao, contagem, imposicao, vazamento) e
    resume ok/falhas no fim. Usa o menor PDF da pasta para os testes de
    fluxo, por serem os mais rapidos de rodar."""
    raiz = Path(pasta)
    livros = sorted(raiz.glob("*.pdf"), key=lambda p: p.stat().st_size)
    if not livros:
        print(f"nenhum PDF em {raiz}")
        return 1

    menor = livros[0]
    print(f"livro pequeno usado nos testes de fluxo: {menor.name}")

    temporaria = Path(tempfile.mkdtemp(prefix="robustez_"))
    try:
        testar_arquivos_ruins(temporaria)
        testar_cancelamento(menor, temporaria)
        testar_repetibilidade(menor, temporaria)
        testar_pasta_sem_permissao()
        testar_contagem(menor)
        testar_imposicao()
        testar_vazamento(livros, temporaria)
    finally:
        shutil.rmtree(temporaria, ignore_errors=True)

    print(f"\n{_ok} passaram, {_falhou} falharam")
    return 1 if _falhou else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
