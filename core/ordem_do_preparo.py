"""A ordem do preparo da página: cortar antes ou endireitar antes (item 2.2, G6).

DECISÃO DO SAMUEL
    Pergunta g6-endireitar-antes, respondida em 09/10/2026 na página de
    escolhas: "Endireitar antes de cortar (como o ScanTailor): pode começar?"
    -> "Pode começar". A explicação que ele leu: "Livro começado antes desta
    mudança continua saindo exatamente igual, ponto por ponto; só os livros
    novos mudam."

AS DUAS ORDENS
    ENDIREITAR_ANTES (livro novo, de fábrica):
        girar 90 -> dividir -> ENDIREITAR a página inteira -> achar o corte
        na página já reta -> cortar.
        É a ordem do ScanTailor. O corte (automático ou à mão) é medido e
        guardado em fração da página RETA; não precisa mais da folga do giro
        (core/recortar.alargar_para_o_giro), e os cantos do conteúdo não
        ficam mais com menos de 1 mm (bug da Lista).
    CORTAR_ANTES (projeto gravado antes do G6, sem o campo):
        girar 90 -> dividir -> cortar -> endireitar a página cortada, com o
        corte automático alargado para o giro. É o programa de antes de
        09/10/2026, IDÊNTICO ponto por ponto (teste de máquina em
        tests/test_ordem_do_preparo.py).

QUEM USA
    modelos.Projeto.ordem_do_preparo (o campo gravado no projeto.json),
    core/pipeline (_geometria e _preparar_metade_e_geometria) e
    core/zonas_na_folha (a conta das zonas da aba Marcar recebe a ordem como
    dado: chave "ordem" da geometria do desenho).

O QUE É SEGURO MUDAR
    Nada aqui é texto de tela. Os comentários.

O QUE É ARRISCADO
    - Os códigos ORDEM_*: estão gravados nos projetos e na geometria das
      zonas ("geometria_das_zonas"). Trocar o texto faria projeto gravado
      cair na ordem errada.
    - ORDEM_DO_PROJETO_ANTIGO: tem de ser CORTAR_ANTES, senão o projeto
      antigo reaberto muda de corte e as zonas dele andam.
    - ordem_valida(): o que vem estranho cai em CORTAR_ANTES (a ordem que
      sempre existiu), nunca na nova.
"""

from __future__ import annotations

# Códigos gravados no projeto (nunca o texto da tela).
ENDIREITAR_ANTES = "endireitar_antes"
CORTAR_ANTES = "cortar_antes"
ORDENS = (ENDIREITAR_ANTES, CORTAR_ANTES)

# Livro novo: a ordem do ScanTailor (decisão de 09/10/2026).
ORDEM_DO_LIVRO_NOVO = ENDIREITAR_ANTES
# Projeto gravado sem o campo: a ordem de sempre (modelos.Projeto.de_dicionario).
ORDEM_DO_PROJETO_ANTIGO = CORTAR_ANTES


def ordem_valida(ordem) -> str:
    """A ordem gravada, ou CORTAR_ANTES se vier vazia ou estranha (o
    comportamento que sempre existiu; nunca cair na ordem nova por engano)."""
    return ordem if ordem in ORDENS else ORDEM_DO_PROJETO_ANTIGO


def ordem_do_livro(projeto) -> str:
    """A ordem do preparo deste projeto (Projeto.ordem_do_preparo). Objeto sem
    o campo (quem chama de fora com outro tipo de projeto) = a de sempre."""
    return ordem_valida(getattr(projeto, "ordem_do_preparo", ORDEM_DO_PROJETO_ANTIGO))


def endireita_antes(projeto) -> bool:
    """O projeto endireita a página inteira antes de achar o corte?"""
    return ordem_do_livro(projeto) == ENDIREITAR_ANTES
