# A regua da selecao

Mede o detector de regioes nas mesmas paginas em toda rodada. Cada
expectativa foi escrita OLHANDO a pagina, nunca a partir do que o
programa devolve.

**24 de 26 paginas passaram.**

## O que esta errado

| Livro | Pagina | O que a pagina e | O que saiu errado |
|---|---|---|---|
| Graduale | 126 | partitura manuscrita: texto gotico, pautas vermelhas e neumas pretos | pagina de texto marcada como desenho: 100% de gravura; o texto nao foi marcado: so 0.0% de letra |
| Siebmacher | 45 | prancha de padrao de bordado, com duas legendas impressas miudas | texto impresso nao virou letra: so 0% da faixa em y=0.03-0.10; texto impresso nao virou letra: so 0% da faixa em y=0.54-0.63 |

## Pagina a pagina

| Livro | Pagina | O que e | Tipo | Gravura | Letra | Respingos | Passou |
|---|---|---|---|---|---|---|---|
| Graduale | 1 | capa de couro vermelho com fechos de metal | capa | 100.0% | 0.0% | 0 | sim |
| Graduale | 750 | foto do corte do livro fechado, visto de lado | capa | 100.0% | 0.0% | 0 | sim |
| Boecio | 1 | capa de pergaminho com a etiqueta RESERVADO 623 da b | capa | 100.0% | 0.0% | 0 | sim |
| Boecio | 50 | folha de guarda, sem nada impresso | folha_nua | 0.0% | 0.0% | 0 | sim |
| Palatino | 1 | capa de madeira com veio, sem letra | capa | 100.0% | 0.0% | 0 | sim |
| Palatino | 132 | guarda em branco com um carimbo apagado | folha_nua | 0.0% | 0.0% | 0 | sim |
| Rhetorica | 1 | folha de guarda de pergaminho, em branco | folha_nua | 0.0% | 0.0% | 0 | sim |
| Rhetorica | 446 | folha em branco, so o creme do papel | folha_nua | 0.0% | 0.0% | 0 | sim |
| Pesel | 1 | capa de tecido com o titulo gravado a ouro e um bord | capa | 100.0% | 0.0% | 0 | sim |
| Pesel | 92 | contracapa de tecido com a etiqueta de codigo de bar | capa | 100.0% | 0.0% | 0 | sim |
| Pesel | 16 | folha parda sem tinta, com um carimbo pequeno | folha_nua | 0.0% | 0.0% | 0 | sim |
| Pesel | 46 | folha parda sem tinta, com um carimbo pequeno | folha_nua | 0.0% | 0.0% | 0 | sim |
| Marial | 1 | foto da capa de pergaminho, com a lombada escura a e | capa | 100.0% | 0.0% | 0 | sim |
| Horas | 3 | capa de couro verde com fechos dourados | capa | 100.0% | 0.0% | 0 | sim |
| Siebmacher | 1 | capa de couro gasta, sem letra | capa | 100.0% | 0.0% | 0 | sim |
| Siebmacher | 268 | contracapa de couro gasta, sem letra | capa | 100.0% | 0.0% | 0 | sim |
| Graduale | 126 | partitura manuscrita: texto gotico, pautas vermelhas | texto | 100.0% | 0.0% | 0 | NAO |
| Graduale | 376 | partitura manuscrita com letra gotica ocre e pautas  | texto | 0.0% | 89.9% | 0 | sim |
| Boecio | 33 | pagina de texto impresso em italico, com mancha do v | texto | 0.0% | 45.6% | 0 | sim |
| Boecio | 17 | pagina de texto impresso | texto | 0.0% | 54.5% | 0 | sim |
| Rhetorica | 223 | pagina so de texto, com notas na margem e manchas de | texto | 0.0% | 97.2% | 0 | sim |
| Catecismo | 199 | estampa colorida de pagina inteira: figura sobre fun | desenho | 100.0% | 0.0% | 0 | sim |
| Siebmacher | 45 | prancha de padrao de bordado, com duas legendas impr | desenho | 100.0% | 0.0% | 0 | NAO |
| Siebmacher | 133 | prancha de padrao de bordado, em tres faixas | desenho | 100.0% | 0.0% | 0 | sim |
| Pesel | 73 | foto de bordado montado, com titulo impresso no alto | texto_e_desenho | 58.4% | 20.2% | 0 | sim |
| Rhetorica | 112 | xilogravura emoldurada embaixo de um bloco de texto | texto_e_desenho | 48.1% | 23.3% | 0 | sim |

## A historia dos casos dificeis

- **Graduale p126** - Em 05/08/2026 saia 100% gravura e 0% letra - o erro que a regra do projeto cita pelo nome.
- **Rhetorica p223** - Ja saiu com 39% da folha em vermelho, tomando mancha de papel velho por pintura.
- **Siebmacher p45** - As legendas impressas tem de sair como letra.
- **Pesel p73** - O titulo e a quarta legenda saiam como foto; as outras tres saiam como texto - dois criterios na mesma folha.

## As amostras

Uma imagem por pagina, com a marcacao por cima: **vermelho e gravura,
azul e letra, sem cor e papel**. Estao na pasta `selecao/` ao lado
deste relatorio, e as erradas tem ERRADO no nome.