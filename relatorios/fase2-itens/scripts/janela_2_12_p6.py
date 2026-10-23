"""Prints da janela de verdade para a resposta P6 do 2.12 (23/10/2026), antes x depois.

P6 (b) do Samuel: o desentortar é medido na resolução do livro, por trás, e a prévia
"Rápida" e os cartões usam essa medida, só reduzida. Este roteiro roda a MESMA sequência no
programa da worktree em que está (rodar uma cópia dele numa worktree do código de antes,
2a42cfb, dá o "antes"), sempre com a qualidade da prévia "Rápida" (a de fábrica).

Base do verificador vlm22 (`.claude/worktrees/vlm22/relatorios/conferir/layout-melhorias-
2026-10-22/roteiros/base.py`): pasta de trabalho própria, janela fora da tela, cliques do
Windows, prints por PrintWindow.

Caminho: uma página (só lida; copiada para um PDF de rascunho, com o giro que o livro
precisa) -> abrir -> "Dividir" ligado -> analisar (livro novo, de fábrica) -> Conferir, na
página da direita -> aba Endireitar -> "Desentortar perto da lombada": Automático -> aba
Filtro (prévia e os quatro cartões):
  0  logo depois de ligar (a medida ainda não chegou: o sinal na barra de baixo);
  1  depois da medida (Destino: o aviso "Desentortar não usado"; Righetti: idem);
  2  depois do botão "Desentortar aumentando a página" (Destino: a pergunta "A página
     ainda saiu deformada", com a página deformada na prévia e nos cartões; Righetti: a
     página maior, sem pergunta). No código de antes o aviso não aparece na "Rápida";
     aí o aumento é ligado pelo mesmo método do botão (tela._desentortar_aumentando),
     para mostrar a prévia e os cartões nesse caso.

Uso: python janela_2_12_p6.py <pasta de saída> <pasta de trabalho>
"""
import sys
from pathlib import Path

BASE = Path(r"D:\programas\EditorImpressao\.claude\worktrees\vlm22\relatorios\conferir"
            r"\layout-melhorias-2026-10-22\roteiros")
sys.path.insert(0, str(BASE))
import base  # noqa: E402

WT = str(Path(__file__).resolve().parents[3])
SAIDA, TRAB = Path(sys.argv[1]), Path(sys.argv[2])
SAIDA.mkdir(parents=True, exist_ok=True)
base.preparar(WT, str(TRAB))

import fitz  # noqa: E402

DESTINO = Path(r"D:\Livros para editar\2 - TEOLOGIA\Doutrina Social da Igreja"
               r"\Corporativismo, Integralismo, Distributismo e Municipalismo à luz da DSI"
               r"\9 - Octávio de Faria\Destino do socialismo - Octavio de faria.pdf")
RIGHETTI = base.ACERVO / "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf"


def pdf_de_uma_pagina(livro: Path, indice: int, giro: int, nome: str) -> Path:
    destino = TRAB / nome
    origem, novo = fitz.open(livro), fitz.open()          # o original só é lido
    novo.insert_pdf(origem, from_page=indice, to_page=indice)
    if giro:
        novo[0].set_rotation((novo[0].rotation + giro) % 360)
    novo.save(destino)
    novo.close()
    origem.close()
    return destino


def esperar_que(cond, seg=90):
    import time
    fim = time.time() + seg
    while time.time() < fim:
        base.app.processEvents()
        if cond():
            return True
        time.sleep(0.05)
    return False


def sinal(tela):
    s = getattr(tela, "sinal_desentortando", None)
    return s is not None and not s.isHidden()


def caso(nome, pdf):
    from core import analise
    from core import desentortar_scantailor as ds
    from ui.tela_conferir import FERRAMENTA_ENDIREITAR, FERRAMENTA_FILTROS

    j = base.nova_janela(1536, 816)
    j.abrir_livro(str(pdf))
    base.esperar(3)
    j.projeto.dividir_folhas = True
    j.analisar()
    tela = j.tela_conferir
    base.conferir(esperar_que(lambda: tela.projeto is not None and j.telas.currentWidget() is tela, 120),
                  f"{nome}: a análise terminou e abriu o Conferir")
    base.esperar(3)
    tela._mudar_qualidade_da_previa("rapida")             # a de fábrica
    direita = next(p.indice for p in tela.projeto.paginas if p.metade == "direita")
    tela.ir_para_pagina(direita)
    tela.escolher_ferramenta(FERRAMENTA_ENDIREITAR)
    base.esperar(2)
    pagina = tela.projeto.paginas[direita]
    combo = tela.combo_desentortar
    combo.setCurrentIndex(combo.findData(ds.AUTOMATICO))
    tela.escolher_ferramenta(FERRAMENTA_FILTROS)
    base.esperar(1.5)
    base.conferir(True, f"{nome}: logo depois de ligar, sinal na barra de baixo: {sinal(tela)}")
    base.print_window(j, SAIDA / f"{nome}-0-logo-depois-de-ligar.png")
    ok = esperar_que(lambda: analise.DESENTORTAR_SAIU_SEM in pagina.alertas, 60)
    base.esperar(20)                                    # a prévia e os cartões chegam
    base.conferir(ok, f"{nome}: na prévia 'Rápida' apareceu 'Desentortar não usado'")
    base.conferir(not sinal(tela), f"{nome}: o sinal sumiu depois da medida")
    base.print_window(j, SAIDA / f"{nome}-1-depois-da-medida.png")

    if ok and tela.botao_sugestao.text() == "Desentortar aumentando a página":
        base.clique(j, tela.botao_sugestao)
    else:
        tela._desentortar_aumentando()                  # o mesmo método do botão
    base.esperar(1.5)
    base.print_window(j, SAIDA / f"{nome}-2a-logo-depois-do-botao.png")
    esperar_que(lambda: not sinal(tela) and not tela.previas.desentortar_pendente(direita)
                if hasattr(tela.previas, "desentortar_pendente") else False, 60)
    base.esperar(20)
    base.conferir(True, f"{nome}: depois do botão, avisos {pagina.alertas}")
    base.print_window(j, SAIDA / f"{nome}-2-depois-do-botao.png")
    base.fechar(j)


def principal():
    caso("destino18", pdf_de_uma_pagina(DESTINO, 17, 0, "destino-p18.pdf"))
    caso("righetti96", pdf_de_uma_pagina(RIGHETTI, 95, 270, "righetti-p96.pdf"))
    base.gravar_resultados(SAIDA)


principal()
print("FIM", flush=True)
