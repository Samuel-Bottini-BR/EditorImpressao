# Promessas dos botões do Editor de Impressão

Bateria nova de 26/10/2026, parte 4. **D-010**, palavras do Samuel: "eu acho que o botão tem que ser provado que ele
faz o que se diz que se faz, e não só se ele muda algo na tela." Escrita pelo verificador (que não construiu o
programa), a partir do **nome do botão**, da **dica** (o balão do mouse) e das **decisões do Livro**
(`docs/plano/DECISOES.md`, citadas pelo número). A prova é `tests/test_promessas.py`.

## Como ler e como mexer

- Uma entrada por botão. Quando a MESMA ação mora em vários lugares (menu, painel, canto da página), é uma entrada
  só, com todas as chaves; a prova aperta cada lugar.
- **chaves:** onde o botão está, como a varredura do teste o acha: `tela/lugar/rótulo` (números trocados por N).
  `menu/<chave>` é um item da barra de menus; `trilha/<ferramenta>` e `ícones da direita/<painel>` são os botões
  desenhados à mão; `aviso/<conserto>` são os botões que os avisos põem na faixa embaixo da página (pelo que fazem:
  o mesmo "está bom assim" aparece em vários avisos); `caixa “título”/botão` são os botões das caixas de pergunta.
- **na tela / no projeto / no PDF:** o que tem de acontecer. "No projeto" é o `projeto.json` e o `acoes.jsonl`
  gravados na pasta do livro. "No PDF" é o PDF gerado de verdade pelo "Confirmar e processar". Quando diz
  "não muda", a prova confere que o projeto gravado não mudou (o PDF sai só do livro e do projeto).
- **aguarda:** a promessa é de uma decisão ainda não construída; a prova fica `xfail(strict=True)` com esse motivo e
  passa a ser exigida quando a etapa fizer.
- **sai na:** o botão vai sair do programa (a tela "O que fazer" sai na etapa 3, D-002); a prova vale até lá.
- **fora da varredura:** a varredura não sabe chegar ao botão (o motivo vai escrito); a prova chega.
- **defeito:** a promessa está quebrada no programa de hoje (achado desta bateria). A prova fica vermelha de
  propósito. Para juntar sem vermelho, a gerente dá dono (etapa) e troca por **aguarda**.
- Botão novo no programa sem entrada aqui faz o teste reprovar: escreva a promessa dele (do nome, da dica e do Livro)
  e a prova, antes de juntar.

## Tela dos livros

### P-001 · "+" (abrir um PDF novo)
- **chaves:** `início/livros/+ (abrir um PDF)`, `menu/abrir`
- **dica:** o cartão "+ Abrir um PDF novo"; menu Arquivo > "Abrir um livro..." (Ctrl+O)
- **decisões:** D-344 ("Cartão '+' no começo da grade"), D-009, D-002
- **na tela:** abre a janela de escolher o arquivo; escolhido o PDF, o livro abre para trabalhar.
- **no projeto:** nasce o projeto do livro escolhido (pasta com `projeto.json`, `caminho_entrada` = o PDF).
- **no PDF:** nada ainda.

### P-002 · Configurações
- **chaves:** `início/livros/Configurações`, `menu/configuracoes`
- **dica:** "Tema, atalhos de teclado e outras escolhas"
- **decisões:** D-338 (no alto só "Configurações" e "Ajuda"), D-363 (partes com a lista à esquerda)
- **na tela:** abre a janela Configurações, com a lista das partes à esquerda.
- **no projeto:** nada muda. **no PDF:** nada muda.

### P-003 · Ajuda (a lista de atalhos)
- **chaves:** `início/livros/Ajuda`, `menu/atalhos`, `caixa “Lista de atalhos”/fechar`, `caixa “Lista de atalhos”/Mostrar detalhes...`
- **dica:** "A lista de atalhos de teclado (F1)"
- **decisões:** D-338, D-351
- **na tela:** abre "Lista de atalhos" com os atalhos tirados dos próprios menus (ex.: "Desfazer — Ctrl+Z"), em
  português ("Mostrar detalhes...", não "Show Details..."); "fechar" fecha.
- **no projeto:** nada muda. **no PDF:** nada muda.

### P-004 · clique no cartão do livro
- **chaves:** `início/livros/(clique no cartão)`
- **decisões:** D-340 ("queria que ele tomasse toda a tela [...] só visse os livros novamente quando eu fechasse")
- **na tela:** o livro abre na tela inteira (nome, páginas para folhear), sem os outros cartões.
- **no projeto:** nada muda.

### P-005 · "continuar" (cartão, livro aberto e menu do livro)
- **chaves:** `início/livros/continuar`, `início/livro aberto/Continuar`, `início/menu do livro/continuar`,
  `início/livro aberto/Mais... continuar`
- **dica:** "Abre o trabalho deste livro onde parou"
- **decisões:** D-342 ("vai ter que ser capaz de abrir arquivos de versões anteriores"), D-002
- **na tela:** a área de trabalho do livro, com o que já tinha sido feito (o filtro escolhido numa página continua).
- **no projeto:** o trabalho volta igual (nada se perde).
- **no PDF:** o PDF gerado depois de continuar sai com o trabalho de antes.

### P-006 · "começar de novo" (menu do livro)
- **chaves:** `início/menu do livro/começar de novo`, `início/livro aberto/Mais... começar de novo`,
  `caixa “Começar de novo?”/Começar de novo`, `caixa “Começar de novo?”/Não, deixar`
- **decisões:** D-335 (cópia de segurança guardada)
- **na tela:** pergunta antes; "Não, deixar" não muda nada; "Começar de novo" abre o livro do zero.
- **no projeto:** com "Começar de novo", o trabalho de antes sai do projeto (a página em Preto e branco volta ao Original) e uma
  cópia de segurança do trabalho antigo fica guardada; com "Não", o projeto fica igual.
- **no PDF:** depois do "Sim", o PDF sai sem o trabalho antigo.

### P-007 · "renomear" (menu do livro)
- **chaves:** `início/menu do livro/renomear`, `início/livro aberto/Mais... renomear`, `caixa “Renomear”/OK`,
  `caixa “Renomear”/Cancelar`
- **na tela:** pede o nome; com OK o cartão passa a mostrar o nome novo; com Cancelar nada muda.
- **no projeto:** o nome novo fica gravado (aparece de novo ao reabrir a tela dos livros). O PDF do livro não muda.

### P-008 · "abrir a pasta de saída" / "abrir a pasta"
- **chaves:** `início/menu do livro/abrir a pasta de saída`, `início/livro aberto/Mais... abrir a pasta de saída`,
  `início/livros/abrir a pasta`, `ficou pronto/abrir a pasta`
- **na tela:** abre o Explorador do Windows na pasta onde o PDF pronto foi gravado.
- **no projeto:** nada muda. **no PDF:** nada muda.

### P-009 · "remover da lista" (Tirar da lista)
- **chaves:** `início/menu do livro/remover da lista`, `início/livro aberto/Mais... remover da lista`,
  `caixa “Tirar da lista?”/Tirar da lista`, `caixa “Tirar da lista?”/Não, deixar`
- **decisões:** D-335 ("Tirar da lista" não apaga as cópias de segurança)
- **na tela:** pergunta antes; "Tirar da lista" faz o cartão sumir; "Não, deixar" não muda nada.
- **no projeto:** a pasta do projeto sai da lista (as cópias de segurança vão para `copias-de-seguranca`).
- **no PDF:** o PDF do livro (a entrada) continua onde estava, intacto.

### P-010 · "Voltar para os livros" (Esc)
- **chaves:** `início/livro aberto/Voltar para os livros`
- **dica:** "Volta para os cartões dos livros (tecla Esc)"
- **decisões:** D-340
- **na tela:** volta aos cartões, com o cartão deste livro marcado.

### P-011 · "Rodar o automático..." (livro aberto), como é hoje
- **chaves:** `início/livro aberto/Rodar o automático...`
- **dica:** "Abre a tela “O que fazer” deste livro, com as escolhas dele"
- **sai na:** etapa 3 (D-002: a tela "O que fazer" sai)
- **na tela:** abre as escolhas do automático deste livro, com as que ele já tinha.
- **no projeto:** nada muda até confirmar.

### P-012 · "Rodar o automático..." abre o Automático de verdade
- **chaves:** `início/livro aberto/Rodar o automático...`
- **decisões:** D-002 ("Trabalho automático = painel 'Automático' [...] Funciona antes/ao abrir o livro e depois"),
  D-018 (abre a janela grande do Automático já com a receita marcada)
- **aguarda:** etapa 3, D-002/D-018
- **na tela:** abre o livro na área de trabalho com o Automático (painel ou janela grande), não a tela "O que fazer".

### P-013 · "Ver todas as páginas" (livro aberto)
- **chaves:** `início/livro aberto/Ver todas as páginas`
- **dica:** "Todas as folhas do livro, em grade"
- **decisões:** D-343, D-346 ("Todas as páginas" abre sempre em "uma a uma")
- **na tela:** a grade com todas as páginas, em "uma a uma". **no projeto:** nada muda.

### P-014 · "Confirmar e processar..." (livro aberto)
- **chaves:** `início/livro aberto/Confirmar e processar...`
- **dica:** "Abre o trabalho e pede a confirmação para gerar o PDF"
- **na tela:** abre o trabalho e mostra a janela de confirmar o destino; confirmado, gera.
- **no PDF:** o PDF sai com todas as páginas do livro.

### P-015 · "Uma página" / "Duas lado a lado" (livro aberto)
- **chaves:** `início/livro aberto/Uma página`, `início/livro aberto/Duas lado a lado`
- **decisões:** D-347 (livro aberto como no UPDF; "escolha lembrada"), D-345
- **na tela:** mostra uma página por vez, ou as páginas em pares; a escolha fica para o próximo livro.
- **no projeto:** nada muda (a escolha vai para as configurações do programa).

### P-016 · "Rolar sem parar" (livro aberto)
- **chaves:** `início/livro aberto/Rolar sem parar`
- **decisões:** D-347
- **na tela:** ligado, as páginas rolam uma atrás da outra; desligado, uma de cada vez. Lembrado.

### P-017 · "Caber a página" / "Caber a altura" / "Caber a largura" / "Tamanho real" (livro aberto)
- **chaves:** `início/livro aberto/Caber a página`, `início/livro aberto/Caber a altura`,
  `início/livro aberto/Caber a largura`, `início/livro aberto/Tamanho real`
- **decisões:** D-347
- **na tela:** o tamanho da página na tela muda como diz o nome; o botão escolhido fica aceso; lembrado.

### P-018 · "‹" / "›" (folha anterior / próxima, no livro aberto)
- **chaves:** `início/livro aberto/‹`, `início/livro aberto/›`
- **dica:** "folha anterior" / "próxima folha"
- **na tela:** vai para a folha de antes / a de depois.

### P-019 · "Todas as páginas": "uma a uma" / "em pares" / "todas" / "só as que precisam de atenção"
- **chaves:** `início/todas as páginas/uma a uma`, `início/todas as páginas/em pares`, `início/todas as páginas/todas`,
  `início/todas as páginas/só as que precisam de atenção (N)`, `área de trabalho/todas as páginas/uma a uma`,
  `área de trabalho/todas as páginas/em pares`, `área de trabalho/todas as páginas/todas`,
  `área de trabalho/todas as páginas/só as que precisam de atenção (N)`
- **decisões:** D-343 ("Ter as opções 1 e 2 [...] só as que precisam de atenção"), D-346
- **na tela:** a grade mostra uma a uma, em pares, todas ou só as que têm aviso (a contagem entre parênteses bate com
  as páginas com aviso).
- **no projeto:** nada muda.

### P-020 · "voltar ao livro" / "voltar ao trabalho" (Todas as páginas)
- **chaves:** `início/todas as páginas/voltar ao livro`, `área de trabalho/todas as páginas/voltar ao trabalho`
- **decisões:** D-346 ("volta na mesma página")
- **na tela:** sai da grade e volta na mesma página em que estava.

### P-026 · "Mais..." (livro aberto)
- **chaves:** `início/livro aberto/Mais...`
- **na tela:** abre o menu do livro (continuar, começar de novo, renomear, abrir a pasta de saída, remover da lista).
- **no projeto:** nada muda só por abrir o menu.

## Tela "O que fazer" (sai na etapa 3, D-002)

### P-021 · "Conferir"
- **chaves:** `o que fazer/Conferir`
- **sai na:** etapa 3
- **decisões:** D-009 ("abrir o livro sem escolher nenhuma opção")
- **na tela:** leva à área de trabalho, mesmo sem nenhuma caixinha marcada.
- **no projeto:** as escolhas da tela ficam gravadas no projeto.

### P-022 · "voltar" (tela "O que fazer")
- **chaves:** `o que fazer/voltar`
- **sai na:** etapa 3
- **na tela:** volta para a tela dos livros, sem abrir a área de trabalho.

### P-023 · receitas: "pôr neste livro" / "guardar" / "apagar"
- **chaves:** `o que fazer/pôr neste livro`, `o que fazer/guardar`, `o que fazer/apagar`
- **sai na:** etapa 3 (as receitas vão para o Automático, D-071)
- **decisões:** D-355 ("receita salva → livro novo abre com ela"), D-071
- **na tela:** "guardar" guarda as caixinhas de agora com o nome digitado (aparece na lista); "pôr neste livro" marca
  as caixinhas da receita escolhida; "apagar" tira a receita da lista.
- **no projeto:** a receita fica gravada nas configurações do programa.

### P-024 · "Mais opções" (tela "O que fazer")
- **chaves:** `o que fazer/Mais opções`
- **sai na:** etapa 3
- **na tela:** abre as opções a mais daquele grupo (abre e fecha).

### P-025 · folhear o PDF: "<", ">", "tela cheia" (tela "O que fazer")
- **chaves:** `o que fazer/<`, `o que fazer/>`, `o que fazer/tela cheia`
- **sai na:** etapa 3
- **na tela:** a página mostrada passa para a de antes / a de depois; "tela cheia" abre a página grande.

## Área de trabalho: ferramentas (trilha e menu Ferramentas)

### P-030 · Dividir a folha
- **chaves:** `trilha/dividir`, `menu/usar_dividir`
- **decisões:** D-001 (todas as ferramentas sempre à vista), D-052 (Propriedades abre sozinho), D-007
- **na tela:** a ferramenta fica escolhida (marcada na trilha e no menu Ferramentas); a folha inteira aparece com a
  linha de divisão; o Propriedades abre com os botões do Dividir.
- **no projeto:** nada muda só por escolher a ferramenta. **no PDF:** nada muda.

### P-031 · Cortar as bordas
- **chaves:** `trilha/cortar`, `menu/usar_cortar`
- **decisões:** D-001, D-047, D-052
- **na tela:** a ferramenta fica escolhida; o Propriedades abre com os botões do Cortar.
- **no projeto:** nada muda. **no PDF:** nada muda.

### P-032 · Endireitar
- **chaves:** `trilha/endireitar`, `menu/usar_endireitar`
- **decisões:** D-001, D-052, D-083 (grade, número e alça)
- **na tela:** a ferramenta fica escolhida; o Propriedades abre com os botões do Endireitar.
- **no projeto:** nada muda. **no PDF:** nada muda.

### P-033 · ferramentas de marcar (Retângulo, Oval, Laço, Ponto a ponto, Pincel, Varinha, Pegar tudo desta cor, Mover e mudar o tamanho da área)
- **chaves:** `trilha/retangulo`, `menu/usar_retangulo`, `trilha/elipse`, `menu/usar_elipse`, `trilha/laco`,
  `menu/usar_laco`, `trilha/poligono`, `menu/usar_poligono`, `trilha/pincel`, `menu/usar_pincel`, `trilha/varinha`,
  `menu/usar_varinha`, `trilha/cor`, `menu/usar_cor`, `trilha/ajustar`, `menu/usar_ajustar`
- **decisões:** D-001, D-041 (balão com nome e letra), D-044
- **na tela:** a ferramenta fica escolhida (trilha, menu Ferramentas e o editor de marcar com ela); o Propriedades
  mostra o "Marcar como".
- **no projeto:** nada muda só por escolher. **no PDF:** nada muda.

### P-034 · Zoom e Mão
- **chaves:** `trilha/zoom`, `menu/usar_zoom`, `trilha/mao`, `menu/usar_mao`
- **decisões:** D-001
- **na tela:** a ferramenta fica escolhida; o Propriedades diz que ela só serve para olhar.
- **no projeto:** nada muda. **no PDF:** nada muda.

## Área de trabalho: painéis da direita

### P-040 · ícone de cada painel / menu Painéis
- **chaves:** `ícones da direita/revisar`, `ícones da direita/automatico`, `ícones da direita/props`,
  `ícones da direita/filtro`, `ícones da direita/historico`, `menu/painel_revisar`, `menu/painel_automatico`,
  `menu/painel_props`, `menu/painel_filtro`, `menu/painel_historico`
- **decisões:** D-037 (ícones na borda), D-043 ("Empurra a página"), D-057 (menu Painéis, "a marca acompanha")
- **na tela:** abre o painel (um por vez), ao lado da página, nunca por cima; o ícone e o menu Painéis marcam o
  aberto; clicar de novo no ícone do aberto fecha.
- **no projeto:** nada muda.

### P-041 · seta dos ícones / "Ícones da direita"
- **chaves:** `ícones da direita/seta`, `menu/icones`
- **decisões:** D-037 ("uma seta de dropdown que eu abro ou fecho"), D-058
- **na tela:** esconde os ícones da direita (sobra a seta) e mostra de novo; o item do menu acompanha.

### P-042 · "fechar o painel" / "Fechar o painel" / "esconder os painéis"
- **chaves:** `área de trabalho/para revisar/fechar o painel`, `área de trabalho/automático/fechar o painel`,
  `área de trabalho/propriedades/fechar o painel`, `área de trabalho/filtro da página/fechar o painel`,
  `área de trabalho/histórico/fechar o painel`, `menu/painel_fechar`, `área de trabalho/lado direito/esconder os painéis`
- **decisões:** D-023 ("queria pode fechar e abrir ela"), D-057
- **na tela:** o painel aberto fecha e a página ganha o lugar dele.

### P-043 · "Lado direito": ícones na borda / sanfona (área de trabalho 1)
- **chaves:** `menu/lado_icones`, `menu/lado_sanfona`
- **decisões:** D-037 ("eu também quero ter a opção da area de trabalho 1"), D-033 ("C — Nos dois lugares")
- **na tela:** troca o jeito do lado direito; fica guardado para a próxima vez que o programa abrir.

## Área de trabalho: "Girar a folha" e "Esta página" (alto do Propriedades)

### P-050 · Girar ¼ à direita
- **chaves:** `área de trabalho/girar a folha/¼ à direita`, `área de trabalho/girar do canto/Girar ¼ à direita`,
  `menu/girar`
- **decisões:** D-030 (girar pelo botão e pelo menu, "mesma coisa"), D-049, D-053 (o do canto gira só esta folha)
- **na tela:** a folha aparece girada 90° no sentido do relógio.
- **no projeto:** a folha fica com giro de 90° gravado (uma ação no histórico).
- **no PDF:** a página sai deitada (mais larga que alta) e o conteúdo girado.

### P-051 · Girar ¼ à esquerda
- **chaves:** `área de trabalho/girar a folha/¼ à esquerda`, `área de trabalho/girar do canto/Girar ¼ à esquerda`,
  `menu/girar_esquerda`
- **decisões:** D-030, D-049, D-053
- **na tela / no projeto / no PDF:** como o de cima, no sentido contrário (giro 270°).

### P-052 · Girar meia volta
- **chaves:** `área de trabalho/girar a folha/meia volta`, `área de trabalho/girar do canto/Girar meia volta`,
  `menu/girar_meia_volta`
- **decisões:** D-030, D-049
- **no projeto:** giro de 180° gravado. **no PDF:** a página sai de cabeça para baixo (em pé).

### P-053 · "Aplicar o giro em" (só esta / todas / daqui em diante / ímpares / pares)
- **chaves:** `menu/giro_em_esta`, `menu/giro_em_todas`, `menu/giro_em_daqui_em_diante`, `menu/giro_em_impares`,
  `menu/giro_em_pares`
- **decisões:** D-035 ("Todas ficam viradas como a folha da vez"), D-036 (folha ímpar + "só as pares" avisa e não
  gira), D-371
- **na tela:** o próximo giro do menu e do painel vale para as folhas escolhidas.
- **no projeto / no PDF:** com "todas", girar uma folha deixa TODAS giradas no projeto e todas as páginas saem
  deitadas no PDF.

### P-054 · "deixar em branco" (Esta página, painel Filtro, menu Página, tecla Delete)
- **chaves:** `área de trabalho/esta página/deixar em branco`, `área de trabalho/filtro da página/deixar em branco`,
  `menu/deixar_em_branco`
- **dica:** "A página fica no livro, no mesmo lugar, e sai toda branca"
- **decisões:** D-046 ("tem que ser colocada uma no lugar dele [...] se não a encadernação vai ficar errada";
  "a tecla Delete deixa em branco")
- **na tela:** o botão vira "voltar a página"; a página fica conferida.
- **no projeto:** a página fica com `em_branco` gravado (uma ação no histórico).
- **no PDF:** o PDF tem o MESMO número de páginas, e essa página sai toda branca, no mesmo lugar.

### P-055 · "voltar a página" (depois do "deixar em branco")
- **chaves:** `área de trabalho/esta página/voltar a página`, `área de trabalho/faixa do aviso/voltar a página`
- **decisões:** D-046
- **no projeto:** a página deixa de sair em branco. **no PDF:** a página sai com o conteúdo dela de novo.

### P-056 · "tirar do livro" (Esta página, painel Filtro, menu Página, Shift+Delete)
- **chaves:** `área de trabalho/esta página/tirar do livro`, `área de trabalho/filtro da página/tirar do livro`,
  `menu/tirar_do_livro`
- **dica:** "A página sai do livro de vez (para o que não é página do livro)"
- **decisões:** D-046, D-269, D-271
- **no projeto:** a página fica `apagada` (uma ação no histórico).
- **no PDF:** a página some do PDF: uma página a menos, e as outras saem na ordem, sem ela.

### P-057 · "trazer de volta" / "Trazer de volta a página tirada"
- **chaves:** `área de trabalho/esta página/trazer de volta`, `menu/restaurar`
- **decisões:** D-046
- **no projeto:** a página tirada volta. **no PDF:** ela volta ao PDF, no lugar dela.

## Área de trabalho: Dividir, Cortar, Endireitar (Propriedades)

### P-060 · "dividir esta" / "não dividir esta"
- **chaves:** `área de trabalho/dividir/dividir esta`, `área de trabalho/dividir/não dividir esta`
- **dica:** "Esta folha entrou como uma página só: o jeito de dividir do ScanTailor..." / o contrário
- **decisões:** D-080 ("trocando numa folha se um ficar ruim"), D-009 (feito à mão vale no PDF)
- **na tela:** a folha passa a ter a linha de divisão (ou deixa de ter).
- **no projeto:** a folha fica dividida em duas páginas (ou volta a uma).
- **no PDF:** a folha dividida sai como duas páginas.

### P-061 · "usar em todas" (Dividir)
- **chaves:** `área de trabalho/dividir/usar em todas`
- **dica:** "Põe a linha de divisão desta folha em todas as folhas."
- **decisões:** D-090 ("eu devo conseguir abrir uma aba para selecionar as que eu quero [...] quando mudar de um não
  muda de todas"): abre a lista das páginas, com as exceções desmarcadas, e nunca apaga exceção.
- **aguarda:** etapa 9, D-090 ("Usar em todas" que apaga exceções; no Dividir ainda aplica em todas sem seletor)
- **na tela:** abre a lista das folhas para escolher.
- **no projeto:** só as folhas marcadas recebem a linha; a folha com linha própria (exceção) fica com a dela.

### P-062 · "mudar nas opções do livro..." (Dividir, Cortar, Endireitar)
- **chaves:** `área de trabalho/dividir/mudar nas opções do livro...`, `área de trabalho/cortar/mudar nas opções do livro...`,
  `área de trabalho/endireitar/mudar nas opções do livro...`
- **dica:** "Volta à tela "O que fazer", onde esta escolha vale para o livro todo."
- **sai na:** etapa 3 (D-002: as escolhas do livro vão para o Automático)
- **na tela:** leva às escolhas do livro inteiro, sem perder o trabalho feito.
- **no projeto:** nada muda só por ir.

### P-063 · "não cortar esta"
- **chaves:** `área de trabalho/cortar/não cortar esta`, `aviso/sem_recorte`
- **dica:** "Esta página sai inteira, sem cortar a borda."
- **decisões:** D-009
- **no projeto:** a página fica sem corte (o corte dela é a página inteira).
- **no PDF:** a página sai no tamanho inteiro do scan.

### P-064 · "usar o corte do programa"
- **chaves:** `área de trabalho/cortar/usar o corte do programa`
- **dica:** "Desfaz o corte que você arrastou nesta página: volta a valer o corte do programa"
- **decisões:** D-368
- **no projeto:** o corte à mão desta página sai; vale o do programa. **no PDF:** a página sai como antes do ajuste.

### P-065 · "usar em todas" (Cortar)
- **chaves:** `área de trabalho/cortar/usar em todas`
- **dica:** "Põe o corte desta página em todas as páginas."
- **decisões:** D-090 ("usar em todas" abre a lista das páginas com as exceções desmarcadas e nunca apaga exceção),
  D-091 ("Selecionar todas" e "Nenhuma")
- **na tela:** abre a lista das páginas para escolher.
- **no projeto:** as páginas marcadas ficam com o corte desta; a que tem corte próprio (exceção) fica com o dela.
- **no PDF:** as páginas marcadas saem com o tamanho do corte desta página.

### P-066 · "tamanho..." (Cortar)
- **chaves:** `área de trabalho/cortar/tamanho...`, `tamanho da folha/A4`, `tamanho da folha/A5`, `tamanho da folha/Carta`, `tamanho da folha/OK`,
  `tamanho da folha/Cancelar`
- **dica:** "Escolhe o tamanho da folha em que esta página vai sair."
- **na tela:** abre a janela "Tamanho da folha"; A4/A5/Carta enchem os números; OK aceita, Cancelar não muda nada.
- **no projeto:** com OK, a página fica com o tamanho de folha escolhido; o corte dela não muda.
- **no PDF:** a página sai no tamanho de folha escolhido (ex.: A5 = 148 × 210 mm).

### P-067 · "0,1°" anti-horário e horário (Endireitar)
- **chaves:** `área de trabalho/endireitar/N,N° — Gira a página 0,1 grau no sentido anti-horário`,
  `área de trabalho/endireitar/N,N° — Gira a página 0,1 grau no sentido horário`
- **dica:** "Gira a página 0,1 grau no sentido anti-horário" / "horário"
- **decisões:** D-083 ("setas de 0,1°")
- **no projeto:** o ângulo da página muda 0,1° (para um lado ou para o outro), gravado como ângulo à mão.
- **no PDF:** a página sai endireitada com esse ângulo.

### P-068 · "deixar como veio" (Endireitar)
- **chaves:** `área de trabalho/endireitar/deixar como veio`, `aviso/angulo_zero`
- **dica:** "Não endireita: a página sai com a inclinação com que veio"
- **decisões:** D-368
- **no projeto:** ângulo 0 nesta página. **no PDF:** a página sai sem girar.

### P-069 · "usar o ângulo do programa" (Endireitar)
- **chaves:** `área de trabalho/endireitar/usar o ângulo do programa`
- **dica:** "Desfaz o seu ajuste: volta a valer o ângulo que o programa achou"
- **decisões:** D-368
- **no projeto:** o ângulo à mão sai. **no PDF:** a página sai com o ângulo do programa.

## Área de trabalho: ferramentas de marcar (Propriedades)

### P-070 · "Marcar como": gravura ou foto / letra e traço / papel / pintar por cima / manter a cor da tinta / tinta preta, fundo original
- **chaves:** `área de trabalho/marcar/gravura ou foto`, `área de trabalho/marcar/letra e traço`, `área de trabalho/marcar/papel`,
  `área de trabalho/marcar/pintar por cima`, `área de trabalho/marcar/manter a cor da tinta`,
  `área de trabalho/marcar/tinta preta, fundo original`
- **decisões:** D-231, D-229, D-375, D-243
- **na tela:** o tipo fica aceso; a próxima área desenhada é desse tipo.
- **no projeto:** a área desenhada depois fica gravada com esse tipo.
- **no PDF:** "papel" na página inteira deixa a página branca (D-200); "gravura ou foto" guarda a cor da área.

### P-071 · "cor de pintar"
- **chaves:** `área de trabalho/marcar/cor de pintar`
- **decisões:** D-231
- **na tela:** abre a escolha da cor do "pintar por cima". **no projeto:** a área pintada usa a cor escolhida.

### P-072 · "detectar automaticamente" / menu "Procurar de novo"
- **chaves:** `área de trabalho/marcar/detectar automaticamente`, `menu/procurar_de_novo`
- **dica:** "Procura de novo a gravura, a letra e o papel desta página. O que você marcou à mão continua."
- **no projeto:** o que foi marcado à mão continua na página.

### P-073 · "usar em todas" / "daqui em diante" (marcação desta página)
- **chaves:** `área de trabalho/marcar/usar em todas — Copia a marcação desta página (gravura, letra, papel)`,
  `área de trabalho/marcar/daqui em diante — Copia a marcação desta página para esta e`
- **dica:** "Copia a marcação desta página (gravura, letra, papel) para todas as páginas." / "para esta e as seguintes"
- **decisões:** D-371
- **no projeto:** a marcação desta página fica gravada em todas as páginas (ou desta em diante, não nas de antes).
- **no PDF:** a página com a folha inteira marcada como papel faz todas (ou as seguintes) saírem brancas.

### P-074 · "usar em todas" / "daqui em diante" (Esta página tem foto)
- **chaves:** `área de trabalho/marcar/usar em todas — Leva o "Esta página tem foto" desta página`,
  `área de trabalho/marcar/daqui em diante — Leva o "Esta página tem foto" desta página`
- **decisões:** D-213 ("Quero poder trocar também só numa página")
- **no projeto:** o "Esta página tem foto" desta página fica igual em todas (ou desta em diante).

### P-075 · "apagar a área" / "pintar de branco" / "copiar" / "colar"
- **chaves:** `área de trabalho/marcar/apagar a área`, `área de trabalho/marcar/pintar de branco`,
  `área de trabalho/marcar/copiar`, `área de trabalho/marcar/colar`
- **dica:** "Escolha a área antes, com a ferramenta "Mover e mudar o tamanho da área" (tecla A)."
- **decisões:** D-227 ("clicar numa área laranja e 'pintar de branco' → no PDF sai branca"), D-231 (copiar e colar)
- **no projeto:** "apagar a área" tira a área; "pintar de branco" a troca por papel; "copiar" + "colar" (noutra
  página) põe a mesma área lá.
- **no PDF:** a área pintada de branco sai branca.

### P-076 · "Ajustar o pedaço à figura"
- **chaves:** `área de trabalho/marcar/Ajustar o pedaço à figura`
- **fora da varredura:** só aparece quando a página tem um pedaço com outro filtro e papel demais em volta.
- **decisões:** D-232 ("caso ele não queira mudar, fica do jeito que está"), D-236
- **no projeto:** o retângulo do pedaço encolhe até a figura (uma ação no histórico); sem clicar, nada muda.

### P-077 · menu Marcar > "Limpar tudo"
- **chaves:** `menu/limpar_marcacao`
- **no projeto:** a marcação da página da vez sai (com desfazer).

### P-078 · menu Marcar > "Deixar a folha em branco"
- **chaves:** `menu/folha_em_branco`
- **decisões:** D-027 ("escolher a opção para virar uma folha branca"), D-200
- **no projeto:** a folha inteira fica marcada como papel. **no PDF:** a página sai toda branca, no mesmo lugar.

## Área de trabalho: painel "Filtro da página"

### P-080 · os quatro filtros (painel, menu Filtro, teclas 1 a 4)
- **chaves:** `área de trabalho/filtro da página/Original`, `área de trabalho/filtro da página/Preto e branco`,
  `área de trabalho/filtro da página/Melhorar`, `área de trabalho/filtro da página/Mágico pro`, `menu/filtro_original`,
  `menu/filtro_preto_e_branco`, `menu/filtro_melhorar`, `menu/filtro_magico_pro`
- **decisões:** D-298 ("filtros diferentes em páginas diferentes do mesmo livro, gerando um PDF só"), D-134 (abre em
  Original), D-009
- **na tela:** o filtro escolhido fica aceso no painel e marcado no menu Filtro.
- **no projeto:** a página fica com o filtro gravado (uma ação no histórico); só ela.
- **no PDF:** essa página sai no filtro (Preto e branco: só preto e branco, sem amarelo); as outras continuam como
  estavam (amareladas no Original).

### P-081 · "só nesta" / "todas" / "daqui em diante" (painel Filtro)
- **chaves:** `área de trabalho/filtro da página/só nesta`, `área de trabalho/filtro da página/todas`,
  `área de trabalho/filtro da página/daqui em diante`
- **decisões:** D-371 ("daqui em diante" em todos)
- **no projeto:** "todas" leva o filtro desta página a todas; "daqui em diante" a esta e às seguintes (as de antes
  ficam); "só nesta" deixa só esta e a dá por conferida.
- **no PDF:** com "todas", todas as páginas saem em Preto e branco.

### P-082 · ícone "Ver os filtros em tela cheia" / menu Ver > "Filtros em tela cheia"
- **chaves:** `área de trabalho/filtro da página/Ver os filtros em tela cheia`, `menu/filtros_tela_cheia`
- **decisões:** D-181, D-182 ("ícone no título do painel"), D-058
- **na tela:** abre os filtros em tela cheia, na página da vez. **no projeto:** nada muda até "Usar".

### P-083 · os jeitos do "Só as letras" (Guardar a tinta forte / Guardar tudo / Guardar só o texto) e "Mais opções"
- **chaves:** `área de trabalho/filtro da página/Guardar a tinta forte`, `área de trabalho/filtro da página/Guardar tudo`,
  `área de trabalho/filtro da página/Guardar só o texto`, `área de trabalho/filtro da página/Mais opções`,
  `área de trabalho/filtro da página/Menos opções`,
  `o que fazer/Guardar a tinta forte`, `o que fazer/Guardar tudo`, `o que fazer/Guardar só o texto`
- **decisões:** D-165 ("tem que ser algo bem visível para eu poder escolher"), D-163, D-366
- **no projeto:** o jeito escolhido fica gravado nesta página. "Mais opções" abre as escolhas a mais.

## Área de trabalho: "Para revisar"

### P-090 · "Por página" / "Por motivo"
- **chaves:** `área de trabalho/para revisar/Por página`, `área de trabalho/para revisar/Por motivo`
- **decisões:** D-265 ("A — Abas “Por página / Por motivo”"), D-266 (abre sempre em "Por página")
- **na tela:** troca a lista; a mesma dúvida aparece nas duas. **no projeto:** nada muda.

### P-091 · botão do motivo ("Por motivo")
- **chaves:** `área de trabalho/para revisar/motivo (o botão do grupo)`
- **dica:** "páginas: ..."; "clicar no motivo leva à primeira página"
- **decisões:** D-255 ("Colocar botão clicavel nas paginas que o programa não tem certeza")
- **na tela:** vai para a primeira página com aquele motivo. **no projeto:** nada muda.

### P-092 · "está bom: todas" (um motivo, em todas as páginas)
- **chaves:** `área de trabalho/para revisar/está bom: todas`
- **dica:** "Tira da lista as N páginas com o aviso ... Não muda nada nas páginas; o Desfazer traz de volta."
- **decisões:** D-272 ("com todas as paginas ou com todos os motivos")
- **na tela:** o motivo sai da lista e o número do painel desce.
- **no projeto:** o aviso fica dado por visto nessas páginas (gravado); nada mais muda nas páginas.
- **no PDF:** as páginas saem iguais.

### P-093 · "está bom em tudo"
- **chaves:** `área de trabalho/para revisar/está bom em tudo`
- **dica:** "Tira da lista todos os avisos de todas as páginas. Não muda nada nas páginas"
- **decisões:** D-272 ("'Está bom em tudo' → painel em 0; Ctrl+Z desfaz de uma vez")
- **na tela:** o painel fica em 0. **no projeto:** nenhum aviso pendente; um Ctrl+Z traz todos de volta.

### P-094 · "ver a lista…" e a lista dos avisos
- **chaves:** `área de trabalho/para revisar/ver a lista…`, `lista dos avisos/ver`, `lista dos avisos/fechar`,
  `lista dos avisos/está bom nas marcadas`, `lista dos avisos/Selecionar todas`, `lista dos avisos/Nenhuma`
- **decisões:** D-272 ("abrir um selecionador em aba grande mostrando todas as paginas com aquele problema e
  deselecionar ou dar ok em todas"), D-280
- **na tela:** abre a lista grande; "ver" leva à página; "Selecionar todas"/"Nenhuma" marcam e desmarcam;
  "está bom nas marcadas" tira só as marcadas; "fechar" não muda nada.
- **no projeto:** só as marcadas ficam dadas por vistas.

### P-095 · "ver as N em tela cheia" (só as páginas com dúvida)
- **chaves:** `área de trabalho/para revisar/ver as N em tela cheia`
- **decisões:** D-259 ("abrir todas as páginas em tela cheia (como no UPDF) mostrando as que precisam de atenção")
- **aguarda:** etapa 7, D-259
- **na tela:** abre a tela cheia só com as páginas com dúvida.

## Área de trabalho: a faixa embaixo da página e os botões dos avisos

### P-100 · "está certo" (o que já vale hoje)
- **chaves:** `área de trabalho/faixa do aviso/está certo`
- **dica:** "Marca como conferida (a barra de espaço marca e já vai para a próxima)."
- **na tela:** o aviso da página sai da faixa.
- **no projeto:** a página fica conferida (`revisada`), numa ação do histórico; os avisos dela ficam dados por vistos.
- **no PDF:** a página sai igual.

### P-101 · "está certo" com resposta (tique, contador, próxima dúvida)
- **chaves:** `área de trabalho/faixa do aviso/está certo`
- **decisões:** plano de 26/10, etapa 7 ("'está certo' com resposta: tique, contador certo, próxima dúvida"; lista
  única 1.1; Samuel na sessão 1: o "está certo" mudo), D-010 (o exemplo dele: "a folha fica conferida, tique na
  miniatura, contador sobe, vai para a próxima dúvida")
- **aguarda:** etapa 7 (lista única 1.1)
- **na tela:** a miniatura ganha o tique, o contador de conferidas sobe, e a tela vai para a próxima página com dúvida.

### P-102 · "próxima dúvida"
- **chaves:** `área de trabalho/faixa do aviso/próxima dúvida`
- **dica:** "Vai para a próxima com dúvida (tecla Tab)."
- **na tela:** vai para a próxima página que ainda tem aviso. **no projeto:** nada muda.

### P-103 · aviso: "está bom assim"
- **chaves:** `aviso/revisar`, `área de trabalho/faixa do aviso/está bom assim`
- **decisões:** D-272 ("com um motivo individual de uma pagina"), D-269
- **no projeto:** só este motivo desta página fica dado por visto; a página não muda.
- **no PDF:** a página sai igual.

### P-104 · aviso: "Deixar em branco"
- **chaves:** `aviso/em_branco`, `área de trabalho/faixa do aviso/Deixar em branco`
- **decisões:** D-269, D-271 ("'Deixar em branco' mantém a página branca no lugar"), D-046
- **no projeto / no PDF:** como P-054 (mesmo número de páginas, esta toda branca).

### P-105 · aviso: "Tirar do livro"
- **chaves:** `aviso/apagar`, `área de trabalho/faixa do aviso/Tirar do livro`
- **decisões:** D-269, D-271
- **no projeto / no PDF:** como P-056 (a página some do PDF).

### P-106 · aviso: "Trazer de volta nesta página"
- **chaves:** `aviso/misto_fora:tudo`, `aviso/misto_fora:rede`
- **decisões:** D-278, D-279
- **no projeto:** o jeito do "Só as letras" desta página passa a ser o que guarda o que sumiu ("Guardar tudo" ou
  "Guardar a tinta forte"); só nela.

### P-107 · aviso: "usar mais escuro" / "usar mais fraco"
- **chaves:** `aviso/forca:mais_escuro`, `aviso/forca:mais_fraco`
- **decisões:** D-287 ("aviso com 'usar mais escuro' que funciona")
- **no projeto:** a força do preto desta página fica mais escura (ou mais fraca), só nela.
- **no PDF:** a página em Preto e branco sai com mais (ou menos) tinta.

### P-108 · aviso: "Desfazer" (força do preto escurecida)
- **chaves:** `aviso/desfazer_reforco`
- **decisões:** D-277 ("'Desfazer' que volta a força")
- **no projeto:** a força volta à que a página tinha antes de o programa escurecer.

### P-109 · aviso: "usar Mágico pro nesta"
- **chaves:** `aviso/filtro:magico_pro`
- **no projeto:** esta página fica no Mágico pro. **no PDF:** esta página sai no Mágico pro.

### P-110 · aviso: "usar o corte alargado"
- **chaves:** `aviso/corte_alargado`
- **decisões:** D-098 ("usar o corte alargado mostra o que foi tirado")
- **no projeto:** o corte desta página passa a ser o alargado (como corte à mão), com desfazer.

### P-111 · aviso: "Desentortar aumentando a página" / "Desfazer" do aumento
- **chaves:** `aviso/desentortar_aumentando`, `aviso/desentortar_desfazer_aumento`
- **decisões:** D-105, D-108 ("o aviso deve perguntar e não fazer automaticamente")
- **no projeto:** liga (ou desliga) o "desentortar aumentando" só nesta página.

### P-112 · aviso: "não dividir esta"
- **chaves:** `aviso/nao_dividir`
- **no projeto:** a folha deixa de ser dividida. **no PDF:** a folha sai como uma página só.

### P-113 · aviso: "alinhar com as outras"
- **chaves:** `aviso/alinhar_com_as_outras`
- **decisões:** D-294 ("Inclinação diferente das outras")
- **no projeto:** o ângulo desta página passa a ser o das outras.

## Área de trabalho: miniaturas e barra de baixo

### P-120 · seta das miniaturas ("Fechar as miniaturas" / "Abrir as miniaturas") e menu Ver > "Miniaturas"
- **chaves:** `área de trabalho/miniaturas/Fechar as miniaturas`, `área de trabalho/miniaturas/Abrir as miniaturas`,
  `área de trabalho/miniaturas/… Fechar as miniaturas`, `menu/miniaturas`
- **decisões:** D-038 ("quero conseguir fechar ou abrir as miniaturas com um drop down"), D-050 ("Confirmar e
  processar" desce para a barra de baixo), D-060 (lembrado para o próximo livro)
- **na tela:** a tira de miniaturas fecha (o cabeçalho fica) e abre; o menu Ver acompanha.
- **no projeto:** nada muda (a escolha vai para as configurações do programa).

### P-121 · "Mais opções das miniaturas" (⋯): "Ver em pares" e "Lugar"
- **chaves:** `área de trabalho/miniaturas/Mais opções das miniaturas`, `área de trabalho/miniaturas/… Ver em pares`,
  `área de trabalho/miniaturas/… Lugar > embaixo`, `área de trabalho/miniaturas/… Lugar > à esquerda`,
  `área de trabalho/miniaturas/… Lugar > à direita, junto da página`
- **decisões:** D-039 ("três pontinhos"), D-032 (embaixo, esquerda, direita, em pares), D-060
- **na tela:** "Ver em pares" junta as miniaturas em pares; "Lugar" põe a tira embaixo, à esquerda ou à direita.

### P-122 · "ver todas" / menu Ver > "Todas as páginas"
- **chaves:** `área de trabalho/miniaturas/ver todas`, `menu/todas_as_paginas`
- **decisões:** D-054, D-346
- **na tela:** abre a grade "Todas as páginas" em "uma a uma", com a página da vez marcada.

### P-123 · "‹" / "›" (página anterior / próxima, barra de baixo)
- **chaves:** `área de trabalho/barra de baixo/‹`, `área de trabalho/barra de baixo/›`
- **dica:** "página anterior (seta para a esquerda)" / "próxima página (seta para a direita)"
- **na tela:** vai para a página de antes / de depois; "página N de M" acompanha. **no projeto:** nada muda.

### P-124 · Desfazer / Refazer (barra de baixo, painel Histórico, menu Editar)
- **chaves:** `área de trabalho/barra de baixo/Desfazer`, `área de trabalho/barra de baixo/Refazer`,
  `área de trabalho/histórico/Desfazer`, `área de trabalho/histórico/Refazer`, `menu/desfazer`, `menu/refazer`
- **decisões:** D-020 ("Ctrl+Z desfaz qualquer alteração [...] e Ctrl+Shift+Z refaz"), D-045
- **na tela:** volta a última mudança (e a refaz).
- **no projeto:** o projeto gravado volta a ser o de antes da mudança; o `acoes.jsonl` acompanha.
- **no PDF:** depois do desfazer, o PDF sai como antes da mudança.

### P-125 · Desfazer aceso sem nada para desfazer
- **chaves:** `área de trabalho/barra de baixo/Desfazer`, `menu/desfazer`
- **decisões:** D-020 ("Desfazer ligado sem nada", aberto)
- **aguarda:** etapa 9 (Desfazer ligado sem nada)
- **na tela:** num livro recém-aberto, sem nada feito, o Desfazer fica apagado (barra de baixo e menu).

### P-126 · botão do Histórico (barra de baixo) / menu Editar > "Mostrar o histórico"
- **chaves:** `área de trabalho/barra de baixo/Abrir ou fechar o painel Histórico`, `menu/historico`
- **decisões:** D-045 ("a lista no painel Histórico")
- **na tela:** abre (e fecha) o painel Histórico, com a lista do que foi feito.

### P-128 · linhas do painel Histórico (cada ação feita ou desfeita)
- **chaves:** `área de trabalho/histórico/ação feita (volta até aqui)`,
  `área de trabalho/histórico/ação desfeita (refaz até aqui)`
- **dica:** "clicar volta o trabalho até aqui" / "desfeita: clicar refaz até aqui"
- **decisões:** D-045, D-020
- **no projeto:** clicar numa ação de antes desfaz tudo o que veio depois dela; clicar numa desfeita refaz até ela.
- **no PDF:** sai como o trabalho naquele ponto.

### P-127 · "Confirmar e processar" (área de trabalho e menu Arquivo)
- **chaves:** `área de trabalho/processar/Confirmar e processar`, `menu/processar`
- **decisões:** D-050, D-274 ("quando alguém tentar imprimir sem ver os alertas o programa para e mostra os alertas")
- **na tela:** com avisos pendentes, mostra antes a janela "Antes de processar"; depois a de confirmar o destino; no
  fim, "Ficou pronto!".
- **no projeto:** o destino do PDF fica gravado.
- **no PDF:** o PDF é gravado no destino, com uma página por página do livro, na ordem.

## Janelas da área de trabalho

### P-130 · "Antes de processar": "ver" / "continuar assim mesmo" / "está bom nas marcadas" / "Selecionar todas" / "Nenhuma"
- **chaves:** `antes de processar/ver`, `antes de processar/continuar assim mesmo`, `antes de processar/está bom nas marcadas`,
  `antes de processar/Selecionar todas`, `antes de processar/Nenhuma`
- **decisões:** D-274 ("Lista as páginas e os motivos"), D-280
- **na tela:** "ver" leva à página e NÃO processa; "continuar assim mesmo" processa; "está bom nas marcadas" tira só
  as marcadas da lista.
- **no PDF:** com "continuar assim mesmo" o PDF sai; com "ver", nenhum PDF.

### P-131 · "Confirmar e processar" (a janela): "Escolher pasta" / "Processar" / "voltar"
- **chaves:** `confirmar e processar/Escolher pasta`, `confirmar e processar/Processar`, `confirmar e processar/voltar`
- **decisões:** D-301 ("escolher onde salvar o PDF [...] lembrar a última pasta usada")
- **na tela:** "Escolher pasta" troca a pasta mostrada; "Processar" segue com a pasta e o nome; "voltar" não gera.
- **no PDF:** "Processar" grava o PDF na pasta e com o nome mostrados; "voltar" não grava nada.

### P-132 · "Já existe um arquivo com esse nome": "substituir o antigo" / "salvar como (2)" / "cancelar"
- **chaves:** `caixa “Já existe um arquivo com esse nome”/substituir o antigo`,
  `caixa “Já existe um arquivo com esse nome”/salvar como pronto (N).pdf`,
  `caixa “Já existe um arquivo com esse nome”/cancelar`
- **decisões:** D-301, D-308, D-310
- **no PDF:** "substituir" troca o arquivo antigo pelo novo; "salvar como (2)" grava o novo ao lado e não toca no
  antigo; "cancelar" não grava nada e o antigo fica igual.

### P-133 · lista de páginas ("usar em todas" do Cortar): "Selecionar todas" / "Nenhuma" / "Aplicar" / "Cancelar"
- **chaves:** `escolher as páginas/Selecionar todas`, `escolher as páginas/Nenhuma`, `escolher as páginas/Aplicar`,
  `escolher as páginas/Cancelar`
- **decisões:** D-091, D-280, D-090
- **na tela:** "Selecionar todas" marca todas, "Nenhuma" desmarca todas.
- **no projeto:** "Aplicar" leva o corte só às marcadas; "Cancelar" não muda nada.

### P-134 · "Filtros em tela cheia": "‹" / "›" / "Fechar" / "Fechar sem mudar" / "Usar <filtro>" / "só nesta" / "todas" / "daqui em diante"
- **chaves:** `filtros em tela cheia/‹`, `filtros em tela cheia/›`, `filtros em tela cheia/Fechar`,
  `filtros em tela cheia/Fechar sem mudar`, `filtros em tela cheia/Usar Original`, `filtros em tela cheia/só nesta`,
  `filtros em tela cheia/todas`, `filtros em tela cheia/daqui em diante`
- **decisões:** D-184 ("A — A “um grande”, com a chave “Comparar com o Original”"), D-192
- **na tela:** "‹"/"›" trocam a página; escolher um filtro só MOSTRA; "Fechar"/"Fechar sem mudar" não mudam nada.
- **no projeto:** "Usar <filtro>" grava o filtro nesta página (com "todas", em todas; "daqui em diante", desta em
  diante), com desfazer.
- **no PDF:** a página sai no filtro usado.

### P-135 · menu Ver > "Modo comparar" (abre a página ampliada comparando)
- **chaves:** `menu/comparar`
- **na tela:** abre a página grande com dois filtros lado a lado. **no projeto:** nada muda.

### P-148 · página ampliada: os filtros (Original / Preto e branco / Melhorar / Mágico pro)
- **chaves:** `página ampliada/Original`, `página ampliada/Preto e branco`, `página ampliada/Melhorar`,
  `página ampliada/Mágico pro`
- **na tela:** a página grande passa a mostrar o filtro; o botão fica aceso.
- **no projeto:** a página da vez fica com esse filtro (o mesmo caminho do painel Filtro, com desfazer).
- **no PDF:** a página sai nesse filtro.

### P-149 · página ampliada: "<" / ">" / "+" / "-" / "ajustar à tela" / "comparar" / "X"
- **chaves:** `página ampliada/<`, `página ampliada/>`, `página ampliada/+`, `página ampliada/-`,
  `página ampliada/ajustar à tela`, `página ampliada/comparar`, `página ampliada/X`
- **na tela:** "<"/">" passam de página (a área de trabalho acompanha); "+"/"-" aproximam e afastam; "ajustar à
  tela" volta a caber; "comparar" mostra dois filtros lado a lado; "X" fecha.
- **no projeto:** nada muda.

### P-136 · "Ver lado a lado" na área de trabalho
- **chaves:** `menu/lado_a_lado`, `área de trabalho/barra de baixo/Duas lado a lado`
- **decisões:** D-015 ("Uma página / Duas lado a lado" na barra de baixo, e no menu Ver), D-006, D-058
- **aguarda:** etapa 6, D-015/D-058
- **na tela:** as páginas em pares rolando, na barra de baixo e no menu Ver.

### P-137 · aviso de livro novo: "Rodar o automático…" / "agora não"
- **chaves:** `área de trabalho/aviso de livro novo/Rodar o automático…`, `área de trabalho/aviso de livro novo/agora não`
- **decisões:** D-005 ("B — Um aviso embaixo da página"), D-018
- **aguarda:** etapa 3, D-005/D-018
- **na tela:** livro novo mostra o aviso; "Rodar o automático…" abre a janela grande com a receita de sempre marcada;
  "agora não" fecha o aviso.

### P-138 · painel Automático: "Voltar para as opções"
- **chaves:** `área de trabalho/automático/Voltar para as opções`
- **dica:** "Volta à tela "O que fazer", onde cada etapa se liga e desliga"
- **sai na:** etapa 3 (D-002: o Automático vira painel de verdade)
- **na tela:** leva às escolhas do automático do livro, sem perder o trabalho.

### P-139 · painel Automático de verdade (rodar em todas / escolhidas / numa página, uma etapa só, ordem arrastando)
- **chaves:** `área de trabalho/automático/Rodar`
- **decisões:** D-002 ("eu quero poder sim fazer automatico para todo livro, mas também quero pode fazer uma a uma"),
  D-003, D-004, D-016, D-068
- **aguarda:** etapa 3, D-002/D-003/D-004
- **no projeto / no PDF:** rodar só "endireitar" numa página muda só ela.

## Menus que só existem na barra de menus

### P-140 · Arquivo > "Livros recentes"
- **chaves:** `menu/livros recentes`
- **na tela:** lista os livros abertos antes; clicar num abre aquele livro.

### P-141 · Arquivo > "Escolher a pasta de saída..."
- **chaves:** `menu/pasta_de_saida`
- **decisões:** D-301
- **na tela:** abre a escolha da pasta; a pasta escolhida aparece na próxima janela "Confirmar e processar".
- **no PDF:** o próximo PDF vai para essa pasta.

### P-142 · Arquivo > "Nome do arquivo..."
- **chaves:** `menu/nome_do_arquivo`, `caixa “Nome do arquivo”/OK`, `caixa “Nome do arquivo”/Cancelar`
- **na tela:** pede o nome; OK guarda, Cancelar não muda.
- **no projeto:** o nome escolhido fica no destino gravado. **no PDF:** o próximo PDF sai com esse nome.

### P-143 · Arquivo > "Voltar para as opções"
- **chaves:** `menu/voltar`
- **sai na:** etapa 3 (D-002)
- **na tela:** leva à tela "O que fazer" do livro, sem perder o trabalho.

### P-144 · Arquivo > "Sair"
- **chaves:** `menu/sair`
- **na tela:** fecha o programa. **no projeto:** o trabalho fica gravado antes de fechar (nada se perde).

### P-145 · Página > "Ir para a página..." (Ctrl+G)
- **chaves:** `menu/ir_para_pagina`, `caixa “Ir para a página”/OK`, `caixa “Ir para a página”/Cancelar`
- **decisões:** D-021 ("Ctrl+G → pula para a página")
- **na tela:** pede o número; OK vai para a página; Cancelar fica onde está.

### P-146 · Ver > "Aproximar" / "Afastar" / "Ajustar à tela"
- **chaves:** `menu/mais_zoom`, `menu/menos_zoom`, `menu/ajustar`
- **decisões:** D-026 (zoom confiável)
- **na tela:** a página aumenta / diminui / volta a caber na tela. **no projeto:** nada muda.

### P-147 · Ver > "Tema": Escuro / Cinza / Claro
- **chaves:** `menu/tema_escuro`, `menu/tema_cinza`, `menu/tema_claro`
- **decisões:** D-359 ("Os três: escuro, cinza e claro"), D-360 (o escolhido fica guardado), D-362
- **na tela:** as cores mudam na hora; fica guardado para a próxima vez. **no projeto:** nada muda.

## Ficou pronto! e Processando

### P-150 · "cancelar" (processando)
- **chaves:** `processando/cancelar`
- **decisões:** D-310 ("cancelar não apaga o PDF antigo")
- **na tela:** para o processamento e volta à área de trabalho.
- **no PDF:** nenhum PDF pela metade fica no destino; se havia um antigo, fica igual.

### P-151 · "imprimir agora..."
- **chaves:** `ficou pronto/imprimir agora...`, `imprimir agora/imprimir N páginas`, `imprimir agora/cancelar`,
  `imprimir agora/parar`
- **decisões:** D-012 ("Clicar 'imprimir agora' pede impressora, cópias e confirmação")
- **na tela:** NÃO manda nada à impressora no clique: abre a confirmação (impressora, páginas, cópias).
- **na impressora:** só o "imprimir N páginas" manda, com as páginas e as cópias escolhidas; "cancelar" não manda nada.

### P-152 · "montar para imprimir em A4 (com margens)..."
- **chaves:** `ficou pronto/montar para imprimir em A4 (com margens)...`
- **decisões:** D-314, D-315, D-330 ("Deixar os dois")
- **na tela:** abre a janela "Montar para imprimir" sobre o PDF que acabou de sair.
- **no PDF:** o PDF do livro não muda.

### P-153 · "fazer outro"
- **chaves:** `ficou pronto/fazer outro`
- **na tela:** volta para a tela dos livros, com o cartão deste livro dizendo que o PDF foi gerado.

## Montar para imprimir

### P-160 · "gravar o arquivo para imprimir"
- **chaves:** `montar para imprimir/gravar o arquivo para imprimir`
- **decisões:** D-316 ("Livreto A4 deitada com duas A5, embaralhado sozinho na ordem da dobra"), D-318 (margens),
  D-315
- **na tela:** pergunta onde gravar; no fim diz "Pronto" e onde gravou.
- **no PDF:** grava um PDF novo para a impressora (no livreto: folhas A4 deitadas, cada uma com duas páginas A5,
  na ordem da dobra); o PDF do livro não muda.

### P-161 · "mandar para a impressora..."
- **chaves:** `montar para imprimir/mandar para a impressora...`, `caixa “Mandar para a impressora?”/mandar`,
  `caixa “Mandar para a impressora?”/cancelar`
- **decisões:** D-325 ("Também manda direto para a impressora"), D-012 (pergunta antes)
- **na tela:** pergunta antes ("Mandar para a impressora?").
- **na impressora:** "mandar" manda as folhas montadas, com as cópias escolhidas; "cancelar" não manda nada.

### P-162 · "parar" / "fechar" (Montar para imprimir)
- **chaves:** `montar para imprimir/parar`, `montar para imprimir/fechar`
- **na tela:** "parar" interrompe a montagem (nada fica pela metade); "fechar" fecha a janela sem gravar.

## Configurações

### P-170 · "Fechar" (Configurações)
- **chaves:** `configurações/Aparência/Fechar`, `configurações/Atalhos de teclado/Fechar`, `configurações/Velocidade/Fechar`,
  `configurações/Medidas e receitas/Fechar`, `configurações/Impressão/Fechar`
- **na tela:** fecha a janela; o que foi mudado continua valendo. **no projeto:** nada muda.

### P-171 · "Restaurar todos os padrões" (Atalhos de teclado)
- **chaves:** `configurações/Atalhos de teclado/Restaurar todos os padrões`
- **decisões:** D-351 ("Mudar um atalho e reabrir → vale o novo")
- **na tela:** todos os atalhos voltam aos de fábrica (e o menu mostra a tecla de fábrica).
- **no projeto:** nada muda; as configurações do programa ficam sem atalho mudado.
