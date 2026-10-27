"""Ajudante dos testes de tela para o caminho novo (obra de 26/10/2026, etapa 3).

Antes, os testes abriam o livro (que ia para a tela "O que fazer"), marcavam caixinhas
(janela.tela_opcoes.cx_...) e chamavam o "Conferir" (janela._analise_pronta com a análise do
livro). Desde a etapa 3 (D-002: "nós tínhamos que abrir direto na área de trabalho") o livro
abre DIRETO na área de trabalho, sem nada ligado, e o automático roda quando se pede (o painel
Automático). `rodar_como_o_conferir` faz o que o "Conferir" de antes fazia, pelo caminho novo:
roda o Automático no livro todo com as etapas da receita de fábrica (as caixinhas que a tela
"O que fazer" trazia marcadas: Limpar a folha, Endireitar, Cortar as bordas; Dividir e Montar
cadernos desligados), trocadas pelo que o teste pedir. Assim o que cada teste protege continua
igual; só o caminho até a área de trabalho mudou.

Não é um arquivo de teste (não começa com "test_"): o pytest não o coleta.
"""

from __future__ import annotations

# As caixinhas que a tela "O que fazer" trazia marcadas num livro novo
# (modelos.Projeto de fábrica: limpar, endireitar e cortar ligados).
DE_FABRICA = {"dividir_folhas": False, "endireitar": True, "cortar_bordas": True,
              "limpar": True, "montar_cadernos": False}


def rodar_como_o_conferir(janela, detectar_regioes: bool = False, sempre: bool = False,
                          **campos) -> bool:
    """O antigo "Conferir", pelo caminho novo: roda o Automático no livro todo
    (medindo no mesmo fio, sem a pergunta das páginas mexidas: elas ficam como
    estão), com as caixinhas de fábrica trocadas por `campos` (nomes dos
    campos de modelos.Projeto: dividir_folhas, limpar, filtro_padrao...).

    Livro que já passou pelo automático (o trabalho salvo voltou) e nenhum
    campo pedido: não faz nada - é o "continuar" de antes, em que o trabalho
    salvo voltava como estava (`sempre=True` roda assim mesmo).
    `detectar_regioes`: o "Procurar gravura e letra" do livro (os testes de
    antes desligavam: o modelo é lento e não é o assunto deles)."""
    from core import automatico as A

    projeto = janela.projeto
    if projeto is None:
        return False
    if getattr(projeto, "passou_pelo_automatico", True) and not campos and not sempre:
        return False
    escolhas = {**DE_FABRICA, **campos}
    etapas = [e for e, campo in A.CAMPO_DO_LIVRO.items() if escolhas.get(campo)]
    opcoes = {k: v for k, v in escolhas.items() if k not in A.CAMPO_DO_LIVRO.values()}
    projeto.detectar_regioes = bool(detectar_regioes)
    # as outras escolhas do livro (filtro, gravuras, "So as letras"...) vao
    # direto para o livro, como a tela "O que fazer" fazia antes do "Conferir"
    for campo, valor in opcoes.items():
        if hasattr(projeto, campo):
            setattr(projeto, campo, valor)
    if not etapas:
        # nada marcado: o livro fica como veio (D-009), so passa a contar como
        # "passou pelo automatico" (o aviso do livro novo some, como antes)
        projeto.passou_pelo_automatico = True
        for campo, valor in opcoes.items():
            if hasattr(projeto, campo):
                setattr(projeto, campo, valor)
        janela.tela_conferir.atualizar()
        return True
    pedido = A.Pedido(etapas=etapas, opcoes=opcoes, pular_mexidas=True)
    return janela.rodar_o_automatico(pedido=pedido, esperar=True, perguntar=False)


def abrir_e_conferir(janela, caminho: str, detectar_regioes: bool = False, **campos):
    """Abre o livro e roda o antigo "Conferir" (rodar_como_o_conferir).
    Devolve a tela de trabalho."""
    janela.abrir_livro(str(caminho))
    rodar_como_o_conferir(janela, detectar_regioes=detectar_regioes, **campos)
    return janela.tela_conferir
