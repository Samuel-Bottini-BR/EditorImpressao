# Para conferir — correções do teste do Boécio (22/09/2026)

Feito a partir do que você relatou testando o atalho "(desenvolvimento)", mais duas
observações em documentos separados, e depois ajustado de novo a partir do seu teste ao
vivo do mesmo dia. **Nada foi commitado** — segue a regra do projeto: só commita depois de
você abrir pelo atalho, testar, e aprovar.

**Antes de testar: feche a janela do programa que já está aberta e abra de novo pelo
atalho.** Ela está rodando com o código de antes das correções 4 e 5 (o processo continua
vivo desde mais cedo hoje); só abrindo de novo carrega o código corrigido.

## O que foi corrigido de verdade

### 1. Arrastar o recorte perto da borda da página (o bug do "só abre pro lado esquerdo")

Achado o problema real: perto do limite da página (comum logo depois da detecção
automática de bordas), arrastar QUALQUER alça ou canto para abrir mais o recorte — direita,
esquerda, qualquer canto — empurrava sempre o lado esquerdo/de cima pra fora, não importa
qual lado você tocasse. Corrigido: agora cada alça trava no lado que deveria ficar parado.

**O que testar**: abra um livro, aba Bordas, arraste a alça direita e os cantos direitos
perto da borda da página (recorte já quase do tamanho da página inteira) — a largura deve
crescer, sem o lado esquerdo se mexer sozinho. Teste os 3 modos: normal, Espelhado (tecla
M), Proporção travada (tecla T).

### 2. Botão "tamanho..." não mexe mais no seu recorte

Antes, usar o botão "tamanho..." recentralizava e substituía sua seleção manual. Agora ele
só define o tamanho final da folha de impressão — sua seleção continua exatamente onde
você deixou, e a folha maior aparece como margem branca ao redor, **já visível na tela**
enquanto você edita (não só no arquivo final).

Se você digitar um tamanho de folha menor que o que já recortou, ou se aumentar o recorte
depois e a folha escolhida ficar pequena demais, aparece um aviso visível na tela (não
bloqueia, só avisa) — o corte nunca é cortado escondido.

**O que testar**: recorte algo fora do centro, use "tamanho..." e escolha A4 — sua seleção
não deve se mexer, só deve aparecer a margem branca ao redor, na posição certa. Tente
também escolher um tamanho menor que o recorte, pra ver o aviso.

### 3. Aba Marcar: "usar em todas" / "só nas próximas" para a detecção automática

A detecção automática (letra/gravura) agora pode ser aplicada à página atual, a todas, ou
só nas próximas — mesmo padrão que corte, bordas e filtro já tinham. Copia a marcação já
calculada nesta página (não roda a detecção de novo em cada uma — isso travaria a tela num
livro grande).

### 4. A margem da folha agora é branca de verdade

Achada a causa: a sombra que escurece o que "vai ficar de fora" ao arrastar o recorte
estava sendo desenhada em cima da folha inteira, não só do conteúdo — por isso a margem
aparecia cinza (185,185,185) em vez de branca. Corrigido: a sombra agora só cobre a área do
conteúdo, a margem fica branca de verdade. Confirmado lendo o pixel real da tela, não só em
teste automático.

**O que testar**: escolha uma folha maior que o recorte — a margem ao redor tem que estar
branca de verdade, não acinzentada.

### 5. Mover e redimensionar o conteúdo dentro da folha (aba Bordas)

Você testou a primeira versão do "Mover conteúdo" e continuou sem conseguir mover — com
razão: o clique só funcionava se caísse **exatamente em cima do retângulo do conteúdo**, sem
nenhuma pista visual de onde esse retângulo começava (sem alça, sem cursor diferente). Na
prática, qualquer clique um pouco fora do pixel exato — o normal de um clique de verdade —
caía "no vazio" e não fazia nada. Reproduzido com a janela de verdade (mouse pilotado de
verdade, não simulado) antes de corrigir.

**Corrigido**: agora qualquer clique dentro da folha visível arrasta o conteúdo — como
arrastar uma foto dentro de uma moldura, não precisa acertar o retângulo exato. Continua com
linhas-guia e "ímã" de alinhamento como antes.

**Redimensionar, novo**: 4 alças azuis nos cantos do conteúdo. Arrastar um canto redimensiona
mantendo a proporção da imagem (não distorce), sempre ancorado no centro — a posição não
muda, só o tamanho. Cursor muda sobre as alças pra indicar que dá pra redimensionar ali.
Sem ímã de tamanho por enquanto (ex.: "gruda em 100%") — se quiser isso, é uma entrega à
parte, avise.

**O que testar**: aba Bordas, escolha um tamanho de folha maior que o recorte, clique "Mover
conteúdo" — arraste clicando em qualquer lugar da folha (não só em cima da imagem) e veja se
move; depois arraste um dos 4 cantos azuis e veja se redimensiona sem distorcer, mantendo o
centro parado.

## Sobre os itens que NÃO precisaram de conserto

- **A tela de Configurações existe e funciona** (Arquivo → Configurações...) — testado
  clicando de verdade. Bem provável que você estivesse procurando um botão dedicado na
  tela, e não um item dentro do menu Arquivo — isso é uma questão de onde as coisas ficam
  na interface, não um defeito. Fica anotado para quando tratarmos do redesenho de layout
  (você pediu um estilo mais parecido com Photoshop/After Effects — ainda não iniciado).
- **A detecção de gravura continua preenchendo a caixa inteira**, não o contorno exato —
  uma tentativa anterior de contornar isso (reconstrução morfológica) já foi tentada e
  falhou neste acervo. Não mexemos nisso agora; avise se quiser retomar essa investigação
  com uma ideia diferente.

## Testes automáticos

- `pytest tests -q`: **434 passando** (eram 349 no início do dia), sem nenhum teste antigo
  removido ou alterado — só testes novos ao lado dos existentes.
- `teste_botoes.py` (clique real, não simulado): **128 ações, 0 falhas**.
- Os itens 1, 4 e 5 foram, além disso, confirmados pilotando a janela real do programa com
  mouse de verdade (não só em teste automático) — é o padrão que este projeto usa depois de
  já ter visto teste simulado passar enquanto o uso real falhava.

## Outras mudanças desta sessão, sem precisar do seu teste ao vivo

- Regras novas registradas no `CLAUDE.md` (seção 10): trabalho por subagentes, branches
  separadas quando houver duas conversas em paralelo, documentação obrigatória de código,
  nunca perder pendência antiga, sempre guardar o pedido original de todo item resolvido.
- `PEDIDOS.md` ganhou um bloco novo com ~12 pendências que só existiam soltas no histórico
  (a mais importante: **ninguém nunca respondeu se o programa já substitui o CamScanner do
  Kaique de verdade** — fica registrada, priorizável quando você quiser).
- Boa parte do código existente ganhou comentários/docstrings explicando o que cada parte
  faz (trabalho separado, numa cópia isolada do repositório, sem mudar nenhum
  comportamento).

## Próximo passo

**Feche e reabra o programa pelo atalho "Editor de Impressao (desenvolvimento)"** (importante
para os itens 4 e 5), teste os 5 itens acima, e me diga se aprova, quer ajuste, ou quer
adiar algum.
