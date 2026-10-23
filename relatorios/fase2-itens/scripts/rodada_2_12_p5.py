"""Antes/depois da resposta P5 do 2.12 (23/10/2026): o botão "Desentortar aumentando a página" e a conferência de novo.

PARA QUÊ
    As fotos para o Samuel da resposta P5 ("C — Aparece sempre, mas depois do
    clique o programa confere de novo...", "o aviso deve perguntar e não fazer
    automaticamente"). Caminho inteiro do programa (CLAUDE.md §4.10), com a
    régua vermelha de rodada_2_12.py.

O CAMINHO
    A página (somente leitura) vai para um PDF de rascunho e passa por
    core.pipeline: analisar_projeto (livro novo, de fábrica) ->
    renderizar_pagina: (girar) -> (dividir) -> endireitar -> cortar ->
    desentortar -> filtro.

AS COLUNAS
    Hoje (desligado) · Agora, desentortar ligado (a proteção segura: aviso
    "Desentortar não usado") · Com o botão (diz se apareceu a pergunta "A
    página ainda saiu deformada") · Depois de "Desfazer" (só quando a pergunta
    apareceu) · Hoje em Preto e branco · Com o botão em Preto e branco.

Uso (da worktree):
    python rodada_2_12_p5.py <nome> "<livro.pdf>" <página do PDF, de 1> <giro> <dividir 0/1> <metade> <modo> <pasta>
    <modo>: automatico | pelas_margens. O livro pode ser caminho inteiro (fora do acervo).
"""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rodada_2_12 as base  # noqa: E402  (põe LOCALAPPDATA num rascunho e a raiz no sys.path)

import cv2  # noqa: E402
import numpy as np  # noqa: E402


def rodar(nome, livro, pagina_pdf, giro, dividir, metade, modo, pasta: Path) -> dict:
    from core import analise
    from core import desentortar_scantailor as ds
    from core.filtros import ORIGINAL, PRETO_E_BRANCO
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    pasta.mkdir(parents=True, exist_ok=True)
    rascunho = Path(tempfile.mkdtemp(prefix="pagina_2_12_p5_"))
    pdf = base._pdf_de_uma_pagina(livro, pagina_pdf - 1, giro, rascunho)
    projeto = analisar_projeto(Projeto(caminho_entrada=str(pdf), nome=nome, dividir_folhas=dividir))
    doc = abrir_pdf(str(pdf))
    tempos, avisos = {}, {}
    try:
        pagina = [p for p in projeto.paginas_ativas if p.metade == metade][0]

        def medir(rotulo, **campos):
            inicio = time.perf_counter()
            img = base._desenhar(doc, projeto, pagina, **campos)
            tempos[rotulo] = round(time.perf_counter() - inicio, 2)
            avisos[rotulo] = list(pagina.alertas)
            return img

        hoje = medir("hoje", filtro=ORIGINAL, desentortar=ds.DESLIGADO)
        ligado = medir("ligado", filtro=ORIGINAL, desentortar=modo)
        botao = medir("botao", filtro=ORIGINAL, desentortar=modo, desentortar_aumentar=True)
        pergunta = analise.DESENTORTAR_AINDA_DEFORMADA in avisos["botao"]
        desfeito = medir("desfazer", filtro=ORIGINAL, desentortar=modo, desentortar_aumentar=False)
        pb_hoje = medir("pb_hoje", filtro=PRETO_E_BRANCO, desentortar=ds.DESLIGADO)
        pb_botao = medir("pb_botao", filtro=PRETO_E_BRANCO, desentortar=modo, desentortar_aumentar=True)
    finally:
        doc.close()

    nome_modo = ds.ROTULOS_NA_TELA.get(modo, modo)
    caminho = ((f"Livro novo, ajustes de fábrica: girar {giro}° → " if giro else "Livro novo, ajustes de fábrica: ")
               + ("dividir (ligado no livro) → " if dividir else "") + "endireitar → cortar → desentortar → filtro")
    titulo = [f"{Path(livro).stem.split(' - ')[0][:60]}, página {pagina_pdf} do PDF, {base.NOME_DA_METADE[metade]}",
              caminho, f"Desentortar: {nome_modo}. Régua vermelha: reta, no pé das linhas do meio da página"]

    def aviso(rotulo):
        a = avisos[rotulo]
        if analise.DESENTORTAR_AINDA_DEFORMADA in a:
            return "aviso: A página ainda saiu deformada"
        if analise.DESENTORTAR_SAIU_SEM in a:
            return "aviso: Desentortar não usado"
        return "sem aviso do desentortar"

    # o aviso vai na linha de cima (em negrito), curto, para não ser cortado
    colunas = [
        ("Hoje · desligado", "Original", hoje),
        ("Ligado · " + aviso("ligado"),
         ("a proteção segura · " if analise.DESENTORTAR_SAIU_SEM in avisos["ligado"] else "") + "Original", ligado),
        ("Com o botão · " + aviso("botao"), "Desentortar aumentando a página · Original", botao),
    ]
    if pergunta:
        colunas.append(("Depois de \"Desfazer\" · " + aviso("desfazer"), "volta como antes do clique · Original",
                        desfeito))
    colunas += [
        ("Hoje · desligado", "Preto e branco", pb_hoje),
        ("Com o botão", "Desentortar aumentando a página · Preto e branco", pb_botao),
    ]
    com = [(n, o, base.com_a_regua(i)) for n, o, i in colunas]
    cv2.imwrite(str(pasta / f"{nome}-pagina.jpg"), base._painel(titulo, com, 1300), [cv2.IMWRITE_JPEG_QUALITY, 88])

    def cinza(i):
        return cv2.cvtColor(base._bgr(i), cv2.COLOR_BGR2GRAY)

    numeros = {
        "livro": str(livro), "pagina_pdf": pagina_pdf, "metade": metade, "giro": giro, "dividir": dividir,
        "modo": modo, "tamanho_hoje": list(hoje.shape[:2]), "tamanho_com_o_botao": list(botao.shape[:2]),
        "apareceu_a_pergunta": pergunta, "avisos": avisos,
        "ligado_igual_a_hoje_pontos_mudados": int((cv2.absdiff(cinza(hoje), cinza(ligado)) > 64).sum())
        if hoje.shape == ligado.shape else None,
        "desfazer_igual_a_ligado": bool(np.array_equal(desfeito, ligado)),
        "segundos": tempos,
    }
    (pasta / f"{nome}.json").write_text(json.dumps(numeros, ensure_ascii=False, indent=1), encoding="utf-8")
    return numeros


if __name__ == "__main__":
    a = sys.argv[1:]
    print(json.dumps(rodar(a[0], a[1], int(a[2]), int(a[3]), a[4] == "1", a[5], a[6], Path(a[7])),
                     ensure_ascii=False))
