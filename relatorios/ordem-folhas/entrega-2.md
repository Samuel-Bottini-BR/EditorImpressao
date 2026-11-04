# Entrega 2: D-616, a caixinha "A 1ª folha é a capa aberta"

Ramo `ordem-folhas-2026-11-04`, depois da entrega 1. Está **pronta para conferir**: passou nos testes da máquina e na janela de verdade. Quem dá o "está bom" é o Samuel.

## O que o Samuel pediu

Print a-61, com a contracapa na frente da folha 1 do caderno: "essa capa está no lugar certo?". E também: "qual seria o jeito para resolver esse problema sem ser na mão?". A gerente propôs a caixinha "A 1ª folha é a capa aberta" no Dividir do Automático, e ele respondeu "ok".

## O que mudou, em português simples

- No Automático, a etapa "Dividir folhas ao meio" ganhou a caixinha **"A 1ª folha é a capa aberta"**, desmarcada.
  Embaixo dela há uma explicação em uma frase.
- **Marcada:** ao rodar o Dividir, a metade da direita da 1ª folha (a capa) vira a página 1. A metade da esquerda (a contracapa) vai para a última página.
- **Antes do "Rodar"**, a prévia e as folhas do caderno da etapa 7 já mostram o livro assim. A prévia começa pela capa, e a folha 1 do caderno tem a capa na frente.
- A escolha fica guardada **no livro** e não vai na receita.
- O **Ctrl+Z** desfaz tudo de uma vez: a ordem das páginas e a caixinha guardada.
- **Desmarcada**, nada muda. Se a etapa Dividir não estiver marcada, a caixinha também não faz nada (D-589).

## Como cumpri cada decisão

| Decisão | Como | Prova |
|---|---|---|
| D-616 caixinha, desmarcada, por livro | `Projeto.capa_aberta` (False de fábrica e no projeto antigo); opção da etapa Dividir; fora da receita | `test_d616_caixinha_desmarcada...`, print e2-02 |
| D-616 capa na página 1, contracapa na última | `core/automatico._capa_aberta` com o mesmo jeito de mudar a ordem da D-615 | `test_d616_marcada_o_dividir...`, prints e2-07 e e2-pdf-e2-pagina-1 |
| D-603 / D-614 antes do Rodar | `paginas_do_pdf_depois` segue a mesma regra; o "depois" da prévia aplica o pedido numa cópia | `test_d616_a_previa_e_o_caderno...`, prints e2-04 e e2-06 (o e2-03 é o "antes", igual ao a-61) |
| D-589 desmarcada não faz | sem a caixinha, ou sem a etapa Dividir: nada | `test_d616_desmarcada...`, `test_d616_marcada_sem_o_dividir...` |
| D-004 páginas mexidas à mão | a regra só vale se o Dividir rodou de verdade na 1ª folha (não pulada) | código (`feitas`) |
| Livro já dividido | rodar de novo com a caixinha põe a capa na frente; rodar outra vez não muda nada | `test_d616_folha_ja_dividida...` |

## Decisões técnicas (minhas)

- "1ª folha" quer dizer a folha 1 do PDF.
- A caixinha vale **só para o Dividir do Automático**, que é onde ela está. O "dividir esta" e o "dividir todas" da ferramenta Dividir não olham para ela. Para casos assim, existe o arrastar da D-615.
- Desmarcar a caixinha e rodar de novo **não** devolve a contracapa ao lugar (D-589: o que está desmarcado não é feito). Para voltar, use o Ctrl+Z ou arraste.

## Testes no PC (um arquivo por vez)

Novo: `tests/test_decisoes_capa_aberta.py`, com 6 testes que passaram. Na ponta da entrega 1 (`c34699d3`), 5 deles falham. O que passa lá é o "desmarcada nada muda", que só confere que nada mudou.

Testes antigos dos arquivos que mexi, todos passaram e nenhum foi mudado:

| Arquivo | Passaram |
|---|---|
| test_decisoes_automatico | 29 |
| test_decisoes_automatico_ver_como_fica | 22 |
| test_caderno_segue_as_etapas | 11 |
| test_decisoes_montar_cadernos | 13 |
| test_decisoes_caderno_tela_grande | 14 (1 pulado) |
| test_decisoes_automatico_margens_no_depois | 5 |
| test_decisoes_automatico_opcoes_do_filtro | 21 |
| test_unidades_e_perfis | 9 |
| test_automatico_pular_depois_de_dividir | 4 |
| test_dividir_desmarcada_caixinha | 3 |
| test_decisoes_dividir | 21 |
| test_projetos | 24 |
| test_decisoes_filtro_automatico | 4 |
| test_corte_pelo_conteudo_na_tela | 13 |
| test_limpar_pontinhos_na_tela | 19 |
| test_decisoes | 26 |
| test_decisoes_ordem_folhas | 12 |

## Janela de verdade (Gradus Primus, numa cópia)

Rodei `piloto.py e2`. As anotações estão em `anotacoes-e2.txt`:

- **e2-02:** a caixinha aparece desmarcada.
- **e2-03:** etapa 7 sem a caixinha. A contracapa fica na frente, igual ao a-61.
- **e2-04:** com a caixinha marcada, o 1º passo da prévia mostra a capa.
- **e2-05:** o último passo da prévia mostra a contracapa.
- **e2-06:** etapa 7 com a caixinha. A capa azul fica na frente da folha 1.
- **e2-07:** depois de "Rodar", o livro começa por "1d" e termina por "1e".
- **e2-pdf-e2-pagina-1:** a página 1 do PDF de saída é a capa.
- **e2-08:** o Ctrl+Z volta tudo.

## Ressalva

- Na prévia, o contador continua mostrando o número que a página tem hoje (D-614: "N = a página do livro"). Por isso, antes de rodar, a capa aparece como "página 2 de 140" e a contracapa como "página 1 de 140" (prints e2-04 e e2-05). Não mexi nisso porque é uma escolha já testada (D-605). Se ele quiser o número de depois, é uma pergunta nova; a D-617, de outra frente, mexe nesse número.

## Perguntas para o Samuel

Nenhuma nova. A da entrega 1 continua aberta.

## GitHub

- Entrega 1: testes 41885681255 passaram inteiros; velocidade 41885686939 (obra-2026-10-26 -> ordem-folhas) "igual".
- Entrega 2: testes 41888422108 passaram inteiros (com botões e prints da janela real); velocidade 41888426950
  (755bfae3 -> ordem-folhas) "igual".
