"""Prints da janela de verdade para a resposta P5 do 2.12 (23/10/2026).

O programa de verdade (JanelaPrincipal) desta worktree, FORA DA TELA, com a base do
verificador vlm22 (`.claude/worktrees/vlm22/relatorios/conferir/layout-melhorias-2026-10-22/
roteiros/base.py`: dados numa pasta de trabalho própria, toda janela nova posta fora da tela
antes de aparecer, cliques por mensagens do Windows, prints por PrintWindow).

Caminho: uma página (só lida; copiada para um PDF de rascunho, com o giro de 90 em 90 que o
livro precisa) -> abrir -> "Dividir" ligado -> analisar (livro novo, de fábrica) -> Conferir,
na página da direita -> aba Endireitar -> "Desentortar perto da lombada": Automático ->
espera a prévia -> clique (do Windows) nos botões da faixa.

Uso: python janela_2_12_p5.py <pasta de saída> <pasta de trabalho>
"""
import sys
import tempfile
from pathlib import Path

BASE = Path(r"D:\programas\EditorImpressao\.claude\worktrees\vlm22\relatorios\conferir"
            r"\layout-melhorias-2026-10-22\roteiros")
sys.path.insert(0, str(BASE))
import base  # noqa: E402

WT = str(Path(__file__).resolve().parents[3])
SAIDA, TRAB = Path(sys.argv[1]), Path(sys.argv[2])
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


def caso(nome, pdf, deve_perguntar):
    from core import analise
    from core import desentortar_scantailor as ds

    j = base.nova_janela(1536, 816)
    j.abrir_livro(str(pdf))
    base.esperar(3)
    j.projeto.dividir_folhas = True                     # "Dividir" ligado, como o Kaique faria
    j.analisar()
    tela = j.tela_conferir
    base.conferir(esperar_que(lambda: tela.projeto is not None and j.telas.currentWidget() is tela, 120),
                  f"{nome}: a análise terminou e abriu o Conferir")
    base.esperar(3)
    direita = next(p.indice for p in tela.projeto.paginas if p.metade == "direita")
    # Qualidade da prévia "Alta" (300 DPI, o seletor da tela): na "Rápida" (110 DPI, a de
    # fábrica) o desentortar da prévia não acha as curvas e a proteção nem chega a medir
    # (ver ONDE-PAREI, 23/10/2026: pergunta P6)
    tela._mudar_qualidade_da_previa("alta")
    tela.ir_para_pagina(direita)
    from ui.tela_conferir import FERRAMENTA_ENDIREITAR
    tela.escolher_ferramenta(FERRAMENTA_ENDIREITAR)    # a aba Endireitar (a lista mora nela)
    base.esperar(2)
    pagina = tela.projeto.paginas[direita]
    combo = tela.combo_desentortar
    combo.setCurrentIndex(combo.findData(ds.AUTOMATICO))  # a lista do Propriedades
    base.conferir(pagina.desentortar == ds.AUTOMATICO, f"{nome}: desentortar Automático na página {direita + 1}")
    base.esperar(8)                                     # a prévia da aba chega
    base.print_window(j, SAIDA / f"{nome}-0-endireitar-automatico.png")
    # a aba Endireitar mostra a página inteira, antes do corte e do desentortar;
    # a página pronta (e o aviso da proteção) vem na aba Filtro
    from ui.tela_conferir import FERRAMENTA_FILTROS
    tela.escolher_ferramenta(FERRAMENTA_FILTROS)
    ok = esperar_que(lambda: analise.DESENTORTAR_SAIU_SEM in pagina.alertas)
    base.esperar(25)                                    # os quatro cartões terminam de chegar
    base.conferir(ok, f"{nome}: a proteção segurou (aviso 'Desentortar não usado')")
    base.conferir(tela.botao_sugestao.text() == "Desentortar aumentando a página",
                  f"{nome}: o botão da faixa é '{tela.botao_sugestao.text()}'")
    base.print_window(j, SAIDA / f"{nome}-1-protecao-segurou.png")

    base.clique(j, tela.botao_sugestao)                 # "Desentortar aumentando a página"
    base.conferir(pagina.desentortar_aumentar, f"{nome}: o clique do Windows ligou o aumento")
    if deve_perguntar:
        ok = esperar_que(lambda: analise.DESENTORTAR_AINDA_DEFORMADA in pagina.alertas)
        base.esperar(3)
        base.conferir(ok, f"{nome}: depois do clique apareceu 'A página ainda saiu deformada'")
        base.conferir(tela.botao_sugestao.text() == "Desfazer" and tela.botao_esta_certo.text() == "Manter assim",
                      f"{nome}: os botões são '{tela.botao_sugestao.text()}' e '{tela.botao_esta_certo.text()}'")
        base.conferir(pagina.desentortar_aumentar, f"{nome}: a página não voltou sozinha")
        base.print_window(j, SAIDA / f"{nome}-2-pergunta.png")

        base.clique(j, tela.botao_sugestao)             # "Desfazer"
        ok = esperar_que(lambda: analise.DESENTORTAR_SAIU_SEM in pagina.alertas
                         and analise.DESENTORTAR_AINDA_DEFORMADA not in pagina.alertas)
        base.esperar(3)
        base.conferir(ok and not pagina.desentortar_aumentar,
                      f"{nome}: 'Desfazer' voltou a página como antes do clique")
        base.print_window(j, SAIDA / f"{nome}-3-depois-do-desfazer.png")

        tela.desfazer()                                 # o Ctrl+Z (o mesmo método da tecla)
        ok = esperar_que(lambda: analise.DESENTORTAR_AINDA_DEFORMADA in pagina.alertas)
        base.esperar(3)
        base.conferir(ok and pagina.desentortar_aumentar, f"{nome}: o Ctrl+Z trouxe o aumento e a pergunta de volta")
        base.print_window(j, SAIDA / f"{nome}-4-ctrl-z.png")

        base.clique(j, tela.botao_esta_certo)           # "Manter assim"
        base.esperar(20)                                # os cartões chegam de novo
        base.conferir(pagina.revisada and pagina.desentortar_aumentar
                      and tela.botao_esta_certo.text() == "está certo",
                      f"{nome}: 'Manter assim' manteve a página aumentada e a marcou como conferida")
        base.print_window(j, SAIDA / f"{nome}-5-manter-assim.png")
    else:
        ok = esperar_que(lambda: analise.DESENTORTAR_SAIU_SEM not in pagina.alertas)
        base.esperar(6)
        base.conferir(ok and analise.DESENTORTAR_AINDA_DEFORMADA not in pagina.alertas,
                      f"{nome}: o botão deu certo e não apareceu pergunta (avisos: {pagina.alertas})")
        base.print_window(j, SAIDA / f"{nome}-2-sem-pergunta.png")
    base.fechar(j)


def principal():
    caso("destino18", pdf_de_uma_pagina(DESTINO, 17, 0, "destino-p18.pdf"), True)
    caso("righetti96", pdf_de_uma_pagina(RIGHETTI, 95, 270, "righetti-p96.pdf"), False)
    base.gravar_resultados(SAIDA)


principal()
print("FIM", flush=True)
