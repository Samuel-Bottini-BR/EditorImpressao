# Opinião do verificador: item 1.1 ligado ao programa (commit bb54b7d), rodada 16:03 de 29/09/2026

> **Aviso (decisão do Samuel, 28/09): moldura dourada e iluminura são defeito conhecido** até a Fase 1 ficar pronta (itens 1.2, 1.4 e 1.5). Nenhuma página desta conferência tem moldura dourada nem iluminura; o aviso vale para o item inteiro.

## Veredito

**NÃO ESTÁ PRONTO, por causa de dois defeitos de tela.** A imagem está certa: pelo programa, as 16 páginas saem exatamente iguais ao núcleo que eu já tinha conferido, ponto por ponto, e o Palatino 5 (intacto no núcleo) sai no Mágico pro, como devia. A caixinha aparece e some nas horas certas e o alerta "Conferir o fundo tirado" aparece nas páginas certas. Mas:

1. **A escolha da caixinha se perde quando se abre o mesmo livro de novo pelo "Abrir um livro" (ou arrastando o PDF).** A caixinha volta marcada e, ao clicar em "Conferir", o "desligado" salvo é apagado. Pelo cartão "continuar" da tela inicial, a escolha é mantida.
2. **Na página em que a pessoa escolhe o filtro, o alerta "conferir" nasce escondido.** Escolher o filtro marca a página como "conferida", e o alerta, que só aparece depois, já chega "conferido". Como página nova começa em "Original", este é justamente o caminho comum (ressalva "a" do implementador): a página duvidosa não fica marcada para quem escolhe o filtro página por página.

Quem decide é o Samuel. Isto não é aprovação.

## O que foi feito (máquina ou olho)

| O quê | Tipo | Resultado |
|---|---|---|
| Testes automáticos (`pytest tests -q`) | máquina | **879 passaram**, nenhum falhou (o instável `test_marcacao_em_todas` passou desta vez) |
| O resultado pelo programa (1603) é o mesmo do núcleo? | máquina | Rodei o núcleo nas 16 páginas a 300 DPI e apliquei o mesmo corte e o mesmo endireitamento do programa: **as 16 saem idênticas ponto a ponto** (inclusive as duas metades do Siebmacher 7 e 9) |
| Palatino 5 (intacta no núcleo) sai no Mágico pro? | máquina | Sim: **idêntica ponto a ponto** ao programa com a caixinha desligada |
| Quais páginas saem "conferir" | máquina | Palatino 9, 57, 66 e Opus Majus 3: **as mesmas da rodada 09:56** |
| Todas as imagens da rodada 16:03 (16 páginas: original, rodada anterior, resultado e ScanTailor, página inteira e detalhe) | olho | Abertas todas, página por página (colunas de cada página juntas numa folha só) |
| Beiradas dos resultados (o corte comeu conteúdo?) | olho + máquina | Ver abaixo |
| Janela real do programa: 54 prints, todos olhados | olho | Ver "A janela, passo a passo" |
| Velocidade | — | **Não medida**, por ordem da gerente (outro agente usa a máquina) |

## O que vi em cada página (rodada 16:03 contra 09:56)

A diferença entre a coluna "Rodada anterior" (núcleo sozinho, folha inteira) e o resultado é só o corte das bordas e o endireitamento, que o programa faz por cima. O miolo da página é o mesmo (confirmado ponto a ponto).

| Página | O que vi |
|---|---|
| Palatino 5 | Antes intacta e amarela; **agora sai no Mágico pro**, como pedido (o núcleo deixa intacta, a página segue o filtro). Retrato e letras inteiros. Sai com "Desenho ou escrita?", sem "conferir". |
| Palatino 7 | Igual ao núcleo, cortado: papel branco, texto inteiro; ficam os pontinhos do verso perto do "A ii". |
| Palatino 9 | Igual ao núcleo; molduras cheias, Q inteiro. Sai "conferir". |
| Palatino 10 | Igual ao núcleo; continua a faixa cinza ao lado da moldura (bug já conhecido). |
| Palatino 57 | Igual ao núcleo; moldura dupla cheia. Sai "conferir". |
| Palatino 66 | Igual ao núcleo; título cheio e mais claro que o original. Sai "conferir". |
| Palatino 67 | Igual ao núcleo; manchas laranja continuam (Fase 6). |
| Opus Majus 3 | Igual ao núcleo (a página não é cortada: o corte pega a folha inteira). Sai "conferir" (o carimbo). |
| Opus Majus 11 | Igual ao núcleo, texto inteiro. |
| Opus Majus 20 | Igual ao núcleo: foto no tom do original, legenda inteira. |
| Opus Majus 165 | Igual ao núcleo; figuras 7 e 8 inteiras. |
| Opus Majus 256 | Igual ao núcleo; tabela inteira. |
| Rhetorica 18 | Igual ao núcleo; texto e notas da margem inteiros. |
| Rhetorica 73 | Igual ao núcleo. O corte de cima encosta na régua do título (fica no limite, sem perder a régua a olho). O corte é o mesmo de antes do 1.1. |
| Siebmacher 7 | **A folha é dividida em duas** (a página é uma só, deitada; o programa corta a 57%, com "lombada incerta"). As duas metades saem certas e iguais ao núcleo, mas a divisão em si está errada: é o problema já conhecido do item 2.1, não vem do 1.1. Retalhos pretos do scanner na borda (já conhecidos, item 2.13). |
| Siebmacher 9 | Igual ao 7: dividida em duas (a linha passa no meio de "Sibmacher"); metades iguais ao núcleo; retalhos pretos na borda de baixo e da direita. |

**O corte comeu conteúdo?** Não, em nenhuma das 16: olhei as quatro beiradas de cada resultado. O corte e o ângulo são os mesmos de antes do 1.1 (medidos na folha como veio), então qualquer defeito de corte já existia antes.

## A janela, passo a passo (olho, janela real)

Instância nova (`pythonw main.py`), com uma pasta de dados própria para não mexer nos projetos do Samuel, fora da tela, clique por mensagem nativa, prints com `PrintWindow`. Livro com camadas: Palatino 9, 5, 7 e Opus Majus 3 (cópia das páginas do gabarito); sem camadas: Boécio 3, 7 e 8.

| Passo | O que vi | Print |
|---|---|---|
| Abrir livro com camadas | A caixinha "Tirar o fundo sozinho", "este PDF já vem com o texto separado do fundo", aparece marcada, recuada sob "Limpar a folha". Resumo: "... e tirar o fundo sozinho nas páginas em que você escolher um filtro." Certo. | t01 |
| Desmarcar "Limpar a folha" | Filtros e caixinha somem juntos; resumo sem falar do fundo. Remarcar: voltam. Certo. | t02 |
| Livro sem camadas | A caixinha não aparece. Certo. | t03 |
| Livro em "Original", escolher Preto e branco na página 1 (Palatino 9) | A página passa a sair com o fundo tirado (conferi na tela ampliada). **Mas o alerta "conferir" não aparece**: "Para revisar: nada pendente". No projeto salvo, a página tem o alerta e está marcada "conferida". **Defeito 2.** | t04 |
| Tela ampliada, Mágico pro | Papel branco, sem a sombra do verso: é o fundo tirado. | t05 |
| Tela ampliada, Original | Fica como veio (papel amarelo, verso aparecendo). Certo. | t06 |
| "comparar" da tela ampliada | Lado direito "Mágico pro" mostra o filtro comum (Q com o fundo sujo, marquinha perto de "RIDOLFO"), diferente do lado esquerdo, que é o que vai sair. Confirma a ressalva "c". | t07 |
| Voltar a "O que fazer" e desmarcar a caixinha | Resumo sem o fundo. Salvo no projeto como desligado. Certo. | t08 |
| Conferir de novo, tela ampliada | A prévia volta ao Mágico pro comum (a marquinha perto de "RIDOLFO" volta). O alerta da página some. Certo. | t09 |
| Fechar e reabrir pelo cartão "continuar" | A caixinha volta **desmarcada**. Certo. | t10 |
| Fechar e reabrir o mesmo PDF pelo "Abrir" | A caixinha volta **marcada** (e "Dividir" também, embora estivesse desmarcado). Ao clicar "Conferir", o projeto salvo passa a "ligado". **Defeito 1.** | t11 |
| Livro novo com "Mágico pro" escolhido em "O que fazer" | Páginas 1 e 3 (Palatino 9 e Opus Majus 3) ganham o alerta: faixa laranja "Tirei o fundo desta página, e pode ter sumido escrita fraca ou traço fino junto: confira.", miniatura com "!", "Para revisar 2", botão "está bom assim". A página 2 (Palatino 7) não. Certo. | t12 |
| "está bom assim" | A página 1 fica conferida: faixa volta ao normal, miniatura sem "!"; a 3 continua marcada. Certo. | t13 |
| Na aba Bordas | A faixa laranja aparece, mas o quadro "Para revisar" ainda diz "nada pendente" (só atualiza na aba Filtro), e o botão "está bom assim" fica cortado ("tá bom assi") nesta largura. Pequeno. | t14 |

Textos: todos com acento, sem jargão, sem emoji. O resumo usa "mágico pro" em minúsculas no meio da frase ("uso o mágico pro"), o que é aceitável.

## As ressalvas do implementador

- **(a) Página nova começa em "Original", então o fundo só sai depois que a pessoa escolhe um filtro.** Concordo, e confirmei na janela. Acrescento: quando ela escolhe o filtro na própria página, o alerta "conferir" dessa página nasce escondido (defeito 2). Se o filtro do livro for escolhido já em "O que fazer", o fundo sai em todas e os alertas aparecem certos.
- **(b) Projeto antigo abre com a caixinha marcada e pode mudar a aparência de páginas já conferidas.** Concordo, e o efeito é grande: olhei (só leitura) os projetos salvos do Samuel. Palatino (134 páginas), Rhetorica (446) e Siebmacher (134) estão todos com o filtro do livro em Preto e branco; ao reabrir, **todas essas páginas passam a sair com o fundo tirado**, inclusive as já conferidas com filtro (9 na Rhetorica e 6 no Siebmacher; as conferidas em "Original" não mudam). Nas conferidas, o alerta "conferir" também nasce escondido.
- **(c) Cartões de filtro e "comparar" mostram os filtros comuns.** Concordo; confirmei nos dois (t07, t12). Quem compara lá vê um resultado diferente do que vai sair. Com a caixinha ligada, os quatro cartões não mostram o que o livro vai receber.

## Outras ressalvas

1. **Velocidade não medida** (ordem da gerente). O implementador mediu a primeira prévia 2% a 21% mais lenta em livro com camadas (regra 6), com a máquina dividida.
2. **Roda do mouse não testada** (não funciona sem foco). Não era preciso para este item.
3. O "filtro do livro" escolhido em "O que fazer" **depois** da primeira conferência também se perde (o projeto salvo continuou em "Original"). É o bug já registrado em 29/09 ("as caixinhas perdem o que se muda na volta"), consertado só para a caixinha do fundo.
4. Não testei trocar, na mesma janela, de um livro com camadas para um sem camadas (testei cada um numa janela nova).
5. Os círculos de escolha do filtro do livro em "O que fazer" não aparecem (não dá para ver qual está escolhido, só pelo resumo). Já era assim antes do 1.1.
6. A divisão errada do Siebmacher 7 e 9 (página única cortada em duas) aparece nesta rodada porque ela passa pelo caminho do programa; é o item 2.1.

## Bugs para a Lista de bugs

- **29/09, Item 1.1 ligado (tela):** a escolha "Tirar o fundo sozinho" desmarcada se perde ao abrir o mesmo livro pelo "Abrir um livro" (ou arrastando): a caixinha volta marcada e o "Conferir" grava "ligado" por cima. Pelo "continuar" funciona. `ui/janela_principal.py` (`abrir_livro` não traz o salvo; `_analise_pronta` põe a caixinha da tela por cima). Print: `t11-abrir-de-novo-volta-marcada.jpg`.
- **29/09, Item 1.1 ligado (tela):** na página em que a pessoa escolhe o filtro, o alerta "Conferir o fundo tirado" nasce já "conferido" e não aparece (escolher o filtro marca a página como revisada, e o alerta só é posto depois, quando a prévia chega). `ui/tela_conferir.py` (`_escolher_filtro`) / `core/pipeline.py` (`_anotar_conferir`). Print: `t04-escolheu-filtro-alerta-escondido.jpg`.
- **29/09, pequeno:** na aba Bordas, com o alerta "conferir" na faixa, o quadro "Para revisar" continua "nada pendente" até ir à aba Filtro; e o botão "está bom assim" sai cortado nessa largura de janela. `ui/tela_conferir.py`. Print: `t14-alerta-na-aba-bordas.jpg`.

## Arquivos

- Esta opinião: `relatorios\conferir\fase1-2026-09-29-1603\verificador\opiniao-do-verificador.html`
- A página de antes/depois: `relatorios\conferir\fase1-2026-09-29-1603\conferencia-fase1.html`
- Os prints da janela (t01 a t14) estão nesta mesma pasta.

![](t04-escolheu-filtro-alerta-escondido.jpg)

![](t11-abrir-de-novo-volta-marcada.jpg)

![](t12-alerta-conferir.jpg)

![](t13-esta-bom-assim.jpg)

![](t07-comparar-mostra-filtro-comum.jpg)

![](t14-alerta-na-aba-bordas.jpg)

![](t01-caixinha-aparece-com-camadas.jpg)

![](t03-sem-camadas-nao-aparece.jpg)

![](t10-continuar-mantem-desmarcada.jpg)
