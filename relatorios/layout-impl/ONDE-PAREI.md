# Onde parei: o layout no programa (atualizado em 13/10/2026)

**PRONTO PARA CONFERIR:** etapa 2 + etapa 3 + painel Propriedades (Dividir, Cortar, Endireitar) + girar no lugar novo + os textos das rodadas 12 e 13. O Samuel confere tudo de uma vez (a conferência antiga da etapa 2 foi dada por desatualizada em 12/10).

- Ramo: `layout-impl-2026-10-08`, com o `fase-1` de 12/10 juntado (`8968704`, que traz o G6: endireitar antes de cortar). A junção não teve conflito.
- Worktree: `.claude/worktrees/layout-impl`.
- Regras: só mexer em `ui/` e nos testes de tela; testes um arquivo por vez, com 3 GB de memória livre; push só neste ramo, nunca no `fase-1` (quem junta é a gerente).

Fontes das decisões: a página "Layout do Editor de Impressão" (rodadas 7 a 13, todas decididas) e o `Plano de layout (rascunho).md`, em `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\`, com as palavras do Samuel. A tela-alvo é `prototipo\21-rodada13-base.html` (prints `imagens\21-rodada13-tela-decidida*.png`).

## O que mudou na tela (em uma frase cada)

1. À direita há uma **coluna de ícones**; clicar num ícone abre o painel dele **ao lado da página** (ela encolhe); de fábrica tudo vem fechado; uma seta esconde os ícones.
2. Os botões de **Dividir, Cortar e Endireitar** saíram da fila embaixo da página e moram no painel **Propriedades**, que **abre sozinho** ao escolher uma dessas três ferramentas.
3. A **faixa embaixo da página** ganhou os botões: a sugestão laranja do aviso, "está certo" e "próxima dúvida".
4. **Girar a folha** saiu da linha dos menus: há um bloco no alto do Propriedades (com o "aplicar em") e três botões pequenos no canto da área da página (giram só esta folha).
5. A **linha dos menus** mostra só o nome da ferramenta e os ajustes dela.
6. **Nomes novos:** "deixar como veio", "usar o ângulo do programa", "usar o corte do programa", "só esta folha / todas as folhas", "só esta página / todas as páginas", "daqui em diante" (no lugar de "só nas próximas"), "Editor" na linha da conta do Endireitar.

## Etapa 1: temas (pronta, commit 7ebbc04)

Os três temas, cinza de fábrica; a troca fica no menu Ver > Tema. A escolha fica na chave "tema" do `configuracoes.json` (5280490).
**Falta (decidido, 707 C e 807 B):** a troca também nas Configurações, na parte "Aparência" (a tela de Configurações em partes ainda não foi construída).
**Para a gerente:** o comentário da chave "tema" em `configuracoes.py` (raiz) está desatualizado ("a tela ainda guarda a escolha no tema.json").

## Etapa 2: tela de trabalho sem abas (commit a783bd9)

As abas sumiram (continuam por dentro, escondidas); trilha agrupada à esquerda; barra de opções na linha dos menus; faixa do conferir embaixo da página; barra de baixo com "‹ página N de M ›", desfazer, refazer e o botão do Histórico. As três pendências que a etapa 2 deixou foram resolvidas agora: a fila do Cortar que não cabia (foi para o Propriedades), a frase cortada na linha dos menus (702 C: só o nome) e a conferência no Windows (feita neste PC).

## Etapa 3: coluna de ícones e painéis (commits 6c54817 e 84871de)

- **Coluna de ícones** (44 px) na borda direita, com a seta no alto. O ícone do painel aberto fica azul; o "Para revisar" leva a bolinha laranja com quantas páginas têm dúvida; o mouse vira mãozinha e o balão diz o nome.
- **Painel aberto ao lado da página** (300 px), um por vez; fecha no ícone ou no "x".
- **Para revisar:** abas "Por página | Por motivo", abrindo sempre em "Por página" (602 A). Por página: uma linha por página com dúvida, na ordem do livro, com o motivo e a frase do aviso; a página da vez fica destacada; clicar leva até ela. Por motivo: o que o painel já fazia (um botão por motivo, com a contagem). Os textos dos avisos vêm de `core/analise`; nada do conteúdo foi reescrito.
- **Automático:** só o que existe hoje. Mostra as etapas do livro (ligada ou desligada) com a escolha do livro de cada uma e o botão "Voltar para as opções" (o mesmo do menu Arquivo).
- **Filtro da página:** o conteúdo de antes, no painel novo.
- **Histórico:** Desfazer e Refazer em cima e a lista (as 40 ações mais recentes). A ação desfeita fica na lista, apagada, com "(desfeita)"; clicar nela refaz até ali. O botão do relógio da barra de baixo abre e fecha este painel.

## Painel Propriedades (rodada 12, 701 A e 706 B; rodada 13, 802 A)

- **Abre sozinho** ao escolher Dividir, Cortar ou Endireitar (clique na trilha ou por tecla). Só ao escolher: se a pessoa fechar, fica fechado até escolher outra dessas três. **Abrir um livro não abre painel** (203 D: de fábrica, tudo fechado), mesmo que a primeira ferramenta seja uma dessas.
- **Girar a folha** no alto, em todas as ferramentas: "¼ à esquerda", "¼ à direita", "meia volta" e "aplicar em".
- **Cortar:** "não cortar esta", "usar o corte do programa", "usar em todas", "tamanho..."; caixinhas "Espelhado (tecla M)", "Proporção travada (tecla T)", "Mover conteúdo"; "Qualidade da prévia".
- **Endireitar:** setas de 0,1 grau e o número; "aplicar em"; "deixar como veio"; "usar o ângulo do programa"; "Conta" com os dois ângulos ("ScanTailor … · Editor …").
- **Dividir:** a lista "jeito:", "não dividir esta", "usar em todas", "girar".
- **Para o livro todo** (706 B): mostra a escolha do livro e o botão "mudar nas opções do livro...", que leva à tela "O que fazer". Mudar daqui mesmo não existe no programa (pede refazer a conferência do livro) e não foi inventado.
- **Ferramentas de marcar:** o Propriedades mostra o "Marcar como". Os outros botões de marcar continuam embaixo da página.

## Textos (rodadas 12 e 13)

- **710 B:** "deixar como veio", "usar o ângulo do programa" (Endireitar) e "usar o corte do programa" (Cortar).
- **709 B:** "só esta folha / todas as folhas" (girar e menu Página) e "só esta página / todas as páginas" (endireitar).
- **702 C:** linha dos menus só com o nome e os ajustes; a frase do que fazer no balão da ferramenta, na trilha.
- **805 C:** "Editor" na linha da conta do Endireitar. A lista "conta:" e o Dividir não foram mexidos (não decidido).
- **806 B:** "daqui em diante" nos botões do Filtro e da marcação.
- Acento consertado na faixa do Cortar ("retângulo").
- **Não mudaram, de propósito:** os códigos gravados no projeto e as frases gravadas no histórico de ações ("Não endireitar a página 3", "Voltar ao corte automático na página 3").

## Conferência (12 e 13/10, neste PC, Windows a 125%)

- **Testes de tela, um arquivo por vez (máquina):** os 43 arquivos de teste que usam a tela passaram (`saida_teste/etapa3-testes.txt`). Novos: `tests/test_paineis.py` (33 testes, refeito) e `tests/test_paineis_na_tela.py` (22). Acertados para o lugar e as palavras novas: `test_trilha_agrupada.py`, `test_trilha_e_opcoes.py`, `test_girar_na_tela.py`, `test_endireitar_na_tela.py`, `test_gravura_na_aba_marcar.py`.
- **Janela de verdade (máquina):** `saida_teste/prints_etapa3.py` abre o programa fora da tela, numa cópia do Boécio, e usa **cliques e arrasto por mensagens nativas do Windows**: 49 de 49 conferências certas (cada ícone abre o painel e a página encolhe 300 px; a aba "Por motivo"; clique numa linha do "Para revisar"; o "x"; o botão do relógio; clique na trilha abre o Propriedades sozinho; os botões do Cortar e do Endireitar; as caixinhas; arrasto do lado direito do retângulo do corte com o painel aberto; "está certo" da faixa; girar pelo canto com "todas as folhas" no painel gira só a folha da vez; Desfazer e a ação desfeita no Histórico; a seta dos ícones; com as letras de verdade, todos os botões do Propriedades inteiros dentro do painel e o número do ângulo inteiro no campo; na janela mínima, a coluna de ícones dentro da janela).
- **`teste_botoes.py`:** ver "Ressalvas".
- **Não conferido:** a roda do mouse (não funciona sem a janela em foco); o programa empacotado; outro monitor ou outra escala do Windows.

## Prints (janela de verdade, tema cinza salvo onde dito)

Pasta `relatorios/layout-impl/etapa3/`. Os de 1280 x 657 saem com 1600 x 821 pontos porque este PC amplia a tela em 125%. "Maximizada" é a janela no tamanho que teria maximizada nesta tela (1536 x 785), sem maximizar de verdade na tela do Samuel.

### Antes e depois, nas mesmas telas

| Tela | Antes (`fase-1` de 12/10) | Depois (este ramo) |
|---|---|---|
| Dividir | `antes/antes-1280x657-dividir.png`, `antes/antes-maximizada-dividir.png` | `3-propriedades-dividir.png`, `9-maximizada-propriedades-dividir.png` |
| Cortar | `antes/antes-1280x657-cortar.png`, `antes/antes-maximizada-cortar.png` | `3-propriedades-cortar.png` (e `-rolado`), `9-maximizada-propriedades-cortar.png` |
| Endireitar | `antes/antes-1280x657-endireitar.png`, `antes/antes-maximizada-endireitar.png` | `3-propriedades-endireitar.png`, `9-maximizada-propriedades-endireitar.png` |
| Marcar | `antes/antes-1280x657-marcar.png`, `antes/antes-maximizada-marcar.png` | `1-fechado-marcar-retangulo.png`, `3-propriedades-marcar.png`, `9-maximizada-fechado-retangulo.png` |
| Filtros | `antes/antes-1280x657-filtros.png`, `antes/antes-maximizada-filtros.png` | `1-fechado-filtros-provisorio.png`, `9-maximizada-fechado-filtros.png` |

### O que em cada print já é o layout decidido e o que ainda é antigo

**Vale para todos os prints de "depois" (o que ainda é antigo):**
- **Miniaturas:** a tira antiga, sem o cabeçalho "PÁGINAS", a seta, os três pontinhos e a alça. É a etapa 5. O "Confirmar e processar" ao lado delas é o decidido (704 A); descer para a barra de baixo com as miniaturas fechadas (801 A) e o botão "ver todas" (808 A) entram na etapa 5.
- **Barra de baixo:** falta, à direita, "antes / depois", o zoom "– 78% +" e "ajustar à tela" do desenho. Não têm etapa marcada na obra (para a gerente decidir onde entram).
- **Ícones** da trilha e da coluna da direita: desenhados à mão, parecidos mas não iguais aos do desenho.
- **Faixa do conferir:** tem os três botões do desenho; ainda é uma caixa com cantos arredondados (no desenho vai de lado a lado, com um risco em cima).

**Um por um:**
- `1-ao-abrir-o-livro.png`: decidido (ícones na borda, tudo fechado; linha dos menus só com o nome; girar no canto, sem lista). Antigo: miniaturas.
- `1-fechado-dividir.png`, `1-fechado-cortar.png`, `1-fechado-endireitar.png`: decidido (sem fila de botões embaixo da página; faixa com "está certo" e "próxima dúvida"). É a tela depois de a pessoa FECHAR o painel; ao escolher a ferramenta ele abre (prints 3).
- `1-fechado-marcar-retangulo.png`, `1-fechado-marcar-varinha.png`, `1-fechado-zoom.png`: decidido (linha dos menus com o nome e o ajuste; "daqui em diante"). **Antigo:** as três filas de botões de marcar embaixo da página (vão para o Propriedades, etapa 4).
- `1-fechado-filtros-provisorio.png`: **antigo quase todo** (a tela dos quatro cartões e a fila "Aplicar em"), PROVISÓRIO até o painel Filtro novo e a tela cheia dos filtros (etapas 4 e 6). Decidido nele: "daqui em diante", a coluna de ícones. Aqui os botões de girar do canto ficam escondidos (cobririam o último cartão).
- `2-painel-revisar.png`, `2-painel-revisar-por-motivo.png`, `2-painel-revisar-pagina-20.png`: decidido (abas, abre em "Por página", bolinha com a contagem, a página da vez destacada). **Falta do desenho:** a miniatura da página em cada linha, "ver as N em tela cheia" e, em "Por motivo", os números de cada página (hoje o botão leva à primeira). Os avisos das páginas 2, 7, 12 e 20 foram postos à mão para o print; os outros são do livro.
- `2-painel-automatico.png`: **só o que existe hoje** (as etapas do livro e "Voltar para as opções"). Falta do desenho: receita, ordem arrastando, "ajustar ›", "Rodar N etapas", "escolher páginas…", janela grande (não existem no programa).
- `2-painel-props.png`, `3-propriedades-cortar.png`, `3-propriedades-cortar-rolado.png`, `4-cortar-nao-cortar-esta.png`, `4-cortar-arrastado-com-o-painel-aberto.png`: decidido (as duas partes, os nomes novos, as caixinhas, girar no alto). **Diferente do desenho:** "meia volta" e "aplicar em" ficam em linhas separadas (com a letra do programa não cabem juntas em 300 px), e por isso o Cortar precisa de rolagem em 1280 x 657 (72 pontos); "Para o livro todo" só mostra e leva às opções; falta "Folga do corte" (não existe no programa).
- `3-propriedades-endireitar.png`, `7-endireitar-0,2-grau.png`: decidido (nomes novos, "só esta página", "Editor"). Falta do desenho: "Retângulo do corte, nesta página" (o G6 juntado ao `fase-1` mudou a ordem do preparo, mas não traz essa escolha por página para a tela).
- `3-propriedades-dividir.png`: decidido (duas partes). Diferente: "Onde dividir" é a lista "jeito:" de antes, e não as duas bolinhas; o botão "girar" de antes continua.
- `3-propriedades-marcar.png`: decidido (Propriedades com o "Marcar como", com a cor de cada um). **Antigo:** três jeitos em vez de cinco (705 A depende do processamento); os botões "Na área marcada" e os de marcar ainda embaixo da página.
- `3-propriedades-zoom.png`, `3-propriedades-filtros-provisorio.png`: a frase de "sem propriedades" (decidido para Zoom e Mão; provisório nos filtros).
- `4b-girado-pelo-canto.png`: decidido (canto gira só esta folha).
- `2-painel-filtro.png`: **antigo por dentro** (nome do filtro, tecla e "só neste pedaço"), no painel novo. O painel Filtro decidido (fila de filtros, partes, menus com amostra, ícone da tela cheia) é a etapa 4.
- `2-painel-historico.png`, `5-historico-com-uma-desfeita.png`: decidido (botões e lista; a desfeita apagada). Falta do desenho: a primeira linha "Abriu o livro".
- `6-icones-escondidos.png`: decidido (a seta esconde os ícones).
- `8-minima-*.png` (1000 x 600): as mesmas telas na janela mínima. Com o painel aberto a página fica pequena e a frase da faixa quebra em até três linhas.
- `9-maximizada-*.png` (1536 x 785): as mesmas telas no tamanho de maximizada; o Cortar cabe sem rolagem.
- `10-propriedades-cortar-escuro.png`, `10-para-revisar-escuro.png`, `10-propriedades-cortar-claro.png`, `10-para-revisar-claro.png`: os outros dois temas.

**Prints que abri e olhei um a um:** 38 dos 54 de depois e 6 dos 10 de antes. **Não abri (16 de depois):** `1-fechado-dividir`, `1-fechado-marcar-retangulo`, `1-fechado-zoom`, `3-propriedades-cortar` (é a mesma tela de `2-painel-props`, que vi), `8-minima-fechado-cortar`, `8-minima-fechado-endireitar`, `8-minima-fechado-retangulo` e nove da série 9 (`fechado-cortar`, `fechado-endireitar`, `fechado-dividir`, `propriedades-dividir`, `propriedades-retangulo`, `fechado-filtros`, `propriedades-filtros`, `painel-automatico`, `painel-filtro`). **De antes, não abri:** os quatro "maximizada" de dividir, endireitar, marcar e filtros. São as mesmas telas dos que vi, em outro tamanho ou com o painel fechado; mesmo assim, quem conferir deve olhá-los. Nove dos 38 (`2-painel-historico`, `2-painel-filtro`, `3-propriedades-endireitar`, `3-propriedades-dividir`, `4-cortar-arrastado…`, `4b-girado-pelo-canto`, `5-historico…`, `6-icones-escondidos`, `7-endireitar…`) eu vi na tirada anterior à final; entre as duas só mudou a frase do "Marcar como".

## Ressalvas e achados

1. **`teste_botoes.py` (raiz):** precisei mexer nele (único arquivo fora de `ui/` e `tests/`), porque os botões de Dividir, Cortar e Endireitar saíram de onde ele os procurava. Ele agora abre o Propriedades, clica nos botões e caixinhas, na faixa, em cada ícone da direita e nos botões de girar do canto. **Última rodada (13/10, 02:51): 221 ações, 0 falhas** (no `fase-1`, no mesmo dia: 174 ações, 0 falhas). Foram precisas seis rodadas até chegar a zero, e todos os erros eram do roteiro, não do programa: a bateria clica em "apagar" e "restaurar" em vários lugares e dependia da ordem antiga dos cliques; com os botões em lugar novo, o livro de teste (duas páginas) chegava ao "Processar" sem página nenhuma. O último culpado era o próprio roteiro clicar só o "Desfazer" do painel Histórico, sem o "Refazer". O roteiro agora escreve, em cada parte, quais páginas estão apagadas. **Não conferi** se o `teste_botoes.py` passava no fim da etapa 2 (commit a783bd9); desconfio que não, porque as setas "<" e ">" dos lados da página, de que a ordem dependia, foram escondidas ali.
1b. **No "Para revisar", aba "Por página", a frase comprida de um aviso é cortada na segunda linha** (print `2-painel-revisar.png`: "…Confira na"). A frase inteira aparece no balão do mouse e na faixa embaixo da página.
2. **Com os painéis fechados, os botões de Dividir, Cortar e Endireitar não aparecem** (só depois de escolher a ferramenta ou clicar no ícone do Propriedades). É o decidido (203 D + 802 A), mas é a mudança que o Kaique mais vai sentir.
3. **A sugestão laranja do aviso ainda diz "não endireitar esta"** (print `2-painel-revisar.png`), e o botão novo se chama "deixar como veio". O texto vem de `core/analise.py` (fora de `ui/`): pedir ao implementador.
4. **Botões de girar no canto** ficam por cima do canto da área da página (decidido na 703 D sabendo disso). Com a página larga ou com zoom podem cobrir um pedaço dela; no Endireitar ficam perto da bolinha azul.
5. **No tema claro,** a bolinha da contagem tem letra escura sobre laranja escuro (lê-se mal).
6. **Na janela mínima com um painel aberto,** os quatro cartões dos filtros ficam apertados (tela provisória).
7. **A contagem do "Para revisar"** passou a contar páginas (como a barra de baixo), e não mais avisos (uma página com dois avisos contava duas vezes).

### Bugs que já existiam (não consertados; para a Lista de bugs, 13/10/2026)

- **Menu Ver > "Painel: Para revisar / Marcar como / Filtro da página / Histórico": os quatro itens não fazem nada** (nunca foram ligados a nada; `ui/janela_principal.py` não tem `ligar("painel_…")`). A lista dos painéis no menu Ver está na rodada 14.
- **Histórico: "Conferir a pagina 5", sem acento** (print `5-historico-com-uma-desfeita.png`; a frase nasce em `ui/tela_conferir._marcar_revisada` e fica gravada no histórico de ações).
- **"só neste pedaço" (painel Filtro da página) num livro sem as ferramentas de marcar:** o clique chama o editor de marcar, que não existe nesse livro (`_escolher_filtro_da_regiao`); não vi quebrar, mas o caminho não tem proteção.
- **Clicar no motivo "Endireitar: as contas discordam"** levou à página 9 e o aviso dela sumiu sozinho (a lista foi de 11 para 10 páginas; prints `2-painel-revisar.png` e `2-painel-revisar-pagina-20.png`). É do conteúdo dos avisos (outro agente).

## O que ainda falta (na ordem da obra)

4. **Propriedades, o resto:** os botões de Marcar (detectar automaticamente, "Esta página tem foto", "Ajustar o pedaço à figura", "usar em todas", "daqui em diante") ainda embaixo da página. **Painel Filtro (R9 403 B)** com os nomes do conjunto 2 e os menus com amostra; sai o botão provisório "Os quatro filtros".
5. **Miniaturas** (cabeçalho "PÁGINAS", seta, três pontinhos, alça), com a 801 A e a 808 A.
6. **Tela cheia dos filtros** (R11 601 A).
7. **Tela inicial.**

**Decidido na rodada 13 e ainda não construído:**
- **804 B (aviso "Livro novo: ainda não passou pelo automático"):** hoje o programa não tem como estar na tela de trabalho sem ter passado pelo automático, porque o livro só chega a ela depois da tela "O que fazer" e do "Conferir". O aviso só faz sentido quando o livro puder abrir direto na tela de trabalho (etapa 7) e houver um "Rodar o automático" a partir dela. **Do processamento não falta nada que eu tenha visto;** falta o caminho de tela.
- **807 B + 707 C:** Configurações com a lista das partes à esquerda e o tema em "Aparência".
- **801 A e 808 A:** com as miniaturas (etapa 5).

**Segue aberto (rodada 14):** a lista dos painéis no menu Ver; se o Dividir ("o do programa / o do ScanTailor") muda de palavra como a conta do Endireitar; onde se escolhe a área de trabalho 1.
