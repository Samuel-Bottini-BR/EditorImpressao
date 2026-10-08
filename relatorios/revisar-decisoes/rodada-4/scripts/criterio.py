"""O criterio que saiu das respostas do Samuel na rodada 1 (06/10/2026).

No jeito de fabrica ("Guardar a tinta forte"), a pagina vai para "Para
revisar" quando QUALQUER UM destes e verdade (sinais de sinais.py):

  (1) desenho comido   apagado_junto >= 2%   OU  apagado_a >= 2,5%
      (o programa mandou para o branco tinta que o Preto e branco de sempre
      imprime, amontoada num desenho, ou muita)
  (2) figura alem da beirada  vazou_da_gravura >= 10%
      (um pedaco grande encosta por fora da gravura achada: a figura e
      maior que a zona, ou a zona pegou mancha/remendo)
  (3) faixa escura na beirada  beirada_a >= LIMITE_BEIRADA da pagina
      (sinal novo da rodada 2: mancha cheia de tinta encostada na beirada
      no resultado; e o fundo do scanner, assunto do corte - item 2.13)

(1) e (2) sao a "opcao 1" do estudo revisar-criterios-2026-10-06.

Faixa no livro inteiro: se a faixa (3) aparece em 70% ou mais das paginas do
livro (a mesma regra que o programa ja usa para virar "observacao do livro",
core/analise.FRACAO_VIRA_OBSERVACAO), ela sai das paginas e vira UM aviso do
livro (pedido do Samuel na rodada 1: "avisar uma vez no livro"). Ai a pagina so
vai para a lista por (1) ou (2).
"""

LIMITE_JUNTO = 0.02
LIMITE_APAGADO = 0.025
LIMITE_VAZOU = 0.10
LIMITE_BEIRADA = 0.03


FRACAO_VIRA_AVISO_DO_LIVRO = 0.7


def motivos(s: dict, faixa_no_livro: bool = False) -> list[str]:
    m = []
    if s["apagado_junto"] >= LIMITE_JUNTO or s["apagado_a"] >= LIMITE_APAGADO:
        m.append("desenho apagado")
    if s["vazou_da_gravura"] >= LIMITE_VAZOU:
        m.append("figura além da gravura achada")
    if s.get("beirada_a", 0.0) >= LIMITE_BEIRADA and not faixa_no_livro:
        m.append("faixa escura na beirada")
    return m


def vai_para_a_lista(s: dict, faixa_no_livro: bool = False) -> bool:
    return bool(motivos(s, faixa_no_livro))


def faixa_no_livro(sinais_do_livro: list[dict]) -> bool:
    if not sinais_do_livro:
        return False
    com = sum(1 for s in sinais_do_livro if s.get("beirada_a", 0.0) >= LIMITE_BEIRADA)
    return com / len(sinais_do_livro) >= FRACAO_VIRA_AVISO_DO_LIVRO
