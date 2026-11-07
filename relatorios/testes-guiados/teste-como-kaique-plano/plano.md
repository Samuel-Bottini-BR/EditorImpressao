# Plano do "teste como o Kaique" (06/11/2026)

Pedido do Samuel (06/11): "quando terminar esse teste, pode pegar esse livro Questionario_sobre_as_duas_primeiras_estrofes_d_Os_Lusiadas e fazer uma restauração nele usando o programa como se fosse o kaique e testar para ver se tem algum problema no aplicativo, alguma coisa que não funciona direito, alguma funcionalidade que não dá para apertar, pode me ajudar a pensar em coisas para fazer para achar erros, erros como esses que eu achei usando o aplicativo, analise os erros que eu já achei para montar um plano de como deve ser esses testes."

Status: **proposta, esperando o ok do Samuel.** Nada foi rodado ainda.

## Os erros que você achou, por tipo

Levantados pelo agente em 06/11 nos testes guiados (sessões 0 a 3), na Lista de bugs, em `memoria/bugs.md`, nas queixas do Kaique e no Livro de decisões.

| Tipo | Exemplos seus | Por que os testes automáticos não pegaram |
|---|---|---|
| A tela mostra que fez, o PDF sai diferente | "Preto e branco" saiu igual ao Original; o Mover não chegou ao PDF; "Cortar" desmarcado e o PDF saiu cortado; margem que não aparece na prévia | os testes não vão do clique até abrir o PDF que sai |
| Caixinha que volta marcada, ou desmarcada que é feita | "Montar cadernos" desmarcado e montou (Kaique, 30/10); Dividir marcado de novo depois de rodar (04/11 e 06/11); Gravuras ligada junto com Limpar | os testes rodam uma vez; ninguém faz rodar, voltar, rodar de novo |
| Botão que não responde | "está certo" sem mudar nada (4 vezes); caixinhas do painel que não fazem nada; Mover que para | o teste dos botões só vê se o clique dá erro, não se faz o que promete |
| Funciona numa vista e não em outra | Mover, Cortar e Endireitar em "Duas lado a lado"; zoom; clique na página do par que escolhe a outra | os testes usam só a vista de fábrica |
| Ordem das páginas e cadernos | folhas puladas erradas depois de dividir; a capa no caderno; "Folha 1 de 19" | os testes usam PDFs pequenos fabricados, sem capa aberta |
| Desfazer que não volta tudo | marcações que ficam; Retângulo que sai impresso; "Área branca" que muda depois de Ctrl+Z e Ctrl+Y | o teste faz uma ação e desfaz uma |
| Número ou texto errado | contagem de dúvidas diferente no sino, no rodapé e no processar; "parece em branco" em página com texto; nomes cortados | nenhum teste lê a frase e compara com o que se vê |
| Lento ou recalcula | "Montar cadernos" recalcula a folha já vista (06/11); "Ver de perto" esperando 14 s | os testes usam poucas páginas, com o PC parado |
| Livro grande | falta de memória no Rhetorica | nenhum teste processa um livro grande inteiro |
| Qualidade da imagem | pixelado, amarelado, verso aparecendo, borda branca (Kaique) | as medidas são números; ninguém amplia a página e olha |

## Como o teste é feito

- Um agente usa o programa de verdade, **com o mouse e o teclado na janela**, sem mexer no código por dentro. Usa a versão que você vai testar: a de hoje com as 6 mudanças, depois que os testes passarem.
- Trabalha numa **cópia** do livro. O original não muda.
- Em cada passo confere três coisas: **o que a tela mostra, o que fica salvo no projeto e o PDF que sai.** Cada erro vai com print e o passo a passo para repetir.
- **Não conserta nada.** Só anota. Os erros vêm para você numa página da Central, e você decide o que consertar.
- Antes de anotar um erro, confere no Livro de decisões. Se algo é uma escolha sua, não conta como erro.

## Os passos, na ordem do trabalho de verdade

1. **Abrir o livro** pela janela de escolher arquivo.
2. **Automático** com algumas etapas desmarcadas. Rodar. Conferir que a desmarcada não foi feita no PDF e que a caixinha continua como estava ao voltar.
3. **Rodar o Automático de novo**, com outra escolha. As páginas mexidas à mão continuam certas?
4. **Folhear** em "Uma página", "Duas lado a lado" e "antes / depois". A página clicada é a escolhida? O número da miniatura bate?
5. **Cada ferramenta** (Dividir, Endireitar, Cortar, Mover, Girar, marcar, Filtro) nas três vistas. Processar e ver no PDF se chegou.
6. **Avisos**: apertar "está certo" e ver se a faixa responde; comparar a contagem de dúvidas nos três lugares.
7. **Ctrl+Z em sequência** (10 ações) e Ctrl+Y. Conferir tela, caixinhas, marcações e PDF.
8. **Fechar o programa no meio e reabrir**: tudo igual?
9. **Montar para imprimir**: a ordem de todos os cadernos, a capa, os números das páginas, as folhas em branco; a rodinha do mouse por cima dos números.
10. **Processar** e abrir o PDF final ampliado: letras, papel, gravuras, beiradas.
11. **Janela pequena** (1280×657): textos cortados ou frases que não batem.
12. **No fim**, refazer o que você já aprovou, para ver se nada estragou (regra de 03/11).

## O livro escolhido

Correção do Samuel (06/11): "ilide.info-os-lusiadas-contados-as-crianas-e-lembrado-ao-povo-pr_13bcb7fb9d645f5d2653358634815ab8 esse é o livro certo e está na pasta downloads".

"Os Lusíadas contados às crianças e lembrados ao povo" (João de Barros), em `C:\Users\fotog\Downloads\`:
- 67 folhas, todas deitadas, com duas páginas cada (dá para testar o Dividir);
- a 1ª folha é a capa aberta: contracapa à esquerda, lombada no meio, capa à direita (dá para testar a caixinha da capa e os cadernos);
- tem ilustrações na capa;
- ressalva: o scan é de baixa resolução, cerca de 77 pontos por polegada (o programa trabalha bem a partir de 300). As letras podem sair pixeladas no PDF, e isso vem do scan, não do programa. Fica escrito como ressalva, não como erro do programa.

O teste é feito numa cópia, na pasta de trabalho do agente. O original em Downloads não muda.

## 2ª rodada: só funções (06/11/2026)

O que o Samuel quer achar (06/11): "os erros que eu queria que você achasse são do tipo de função que não funciona" e, sobre a lista de 8 erros de função da 1ª rodada, "esses tipos de erros que eu quero que sejam procurados".

Exemplos da 1ª rodada (o tipo certo): marcações que deviam sumir com a Mão e ficam; a Mão mostra a folha espremida; página que sai deitada no arquivo de imprimir sem aviso; miniatura que não fica branca; faixa e janela de salvar que não atualizam; lista que volta ao topo; o sino que muda sozinho.

Não são o foco: a qualidade da imagem (sujeira, ilustração que some) - essa é outra conversa.

Como muda:
- A janela do programa fica **na tela do Samuel**, para a rodinha do mouse e o Ctrl funcionarem. O PC fica livre por cerca de uma hora.
- **Cada ferramenta em cada vista:** Dividir, Endireitar, Cortar, Mover, Girar, marcar (retângulo, laço, pincel), Filtro, deixar em branco, tirar do livro - em "Uma página", "Duas lado a lado" e "antes / depois".
- **Teclado e rodinha:** Ctrl+Z e Ctrl+Y em sequência, Delete, setas, PageUp/PageDown, Ctrl+Seta do girar, Shift+roda, roda sobre campos de número.
- **Depois de cada ação, conferir que tudo em volta acompanhou:** a tela grande, a miniatura, a faixa de aviso, o painel Propriedades, o sino, o rodapé, o histórico, e o PDF quando a ação deve chegar nele.
- **Cada botão e menu:** apertar e ver se faz o que diz, também nas situações difíceis (página em branco, página tirada, folha dividida e inteira, capa aberta, primeira e última página).
