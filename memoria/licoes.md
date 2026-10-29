# Lições: erros já cometidos e a regra que nasceu de cada um

Cada lição aqui é um erro de verdade da gerente, de um agente ou do Claude Code de antes, e a regra
que existe por causa dele. **Leia antes de trabalhar**: quase toda regra do projeto que parece
exagerada é uma destas cicatrizes. O plano manda; se uma regra daqui e o
[plano](../docs/plano/PLANO-DEFINITIVO.md) discordarem, vale o plano.

Abreviações: **H** = [histórico](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)
(PARTE -N §k); **R** = [plano, Registro de mudanças](../docs/plano/PLANO-DEFINITIVO.md);
**Bugs** = [plano, Lista de bugs](../docs/plano/PLANO-DEFINITIVO.md) (seção 5);
**Agentes** = os quatro arquivos de [.claude/agents/](../.claude/agents/verificador.md)
(implementador, verificador, pesquisador, layout). Montado em 20/10/2026 pelo ajudante A.

Partes: A. Aprovação e conferência · B. Perguntas ao Samuel · C. Medir e testar · D. Arquivos, disco
e PC do Samuel · E. Registros que mentiam · F. Ferramentas e comandos · G. Rumo do trabalho ·
H. Caminhos técnicos já fechados.

---

## A. Aprovação e conferência

### A1. 57+ commits marcados "feito" e zero aprovados
- **O que aconteceu:** de 18/07 a 08/08/2026 o próprio Claude Code julgava e marcava tudo como feito.
  Em 07/09/2026 o diagnóstico: "Zero itens aprovados por você em 57+ commits"
  ([PLANO-RETOMADA.md](../PLANO-RETOMADA.md)). Em 12-13/09/2026 de novo: dos 109 itens do `PEDIDOS.md`,
  zero aprovados e zero sequer preparados para conferência (H, PARTE -3, "Descoberta dura").
- **A regra que nasceu:** o Claude Code escreve "PRONTO PARA CONFERIR" e a opinião dele, **nunca
  "APROVADO"**; só o Samuel marca `[x]`, `[~]` ou `[-]` no plano. Todo item diz se o teste foi de
  máquina ou de olho.
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §4 (abertura) e §4.3; plano, regra 4; Agentes
  (verificador "nunca marca aprovado").

### A2. "10 de 10 corretas" olhando uma imagem
- **O que aconteceu:** antes de 08/08/2026 (data exata não achada; citado no handoff de 08/08 e na
  PARTE 1 do H) foi reportado "10 de 10 corretas" tendo olhado uma imagem; seis estavam erradas.
- **A regra que nasceu:** abrir **todas** as imagens antes de dizer que funcionou; percentual não é
  veredito. Pedido do Samuel em 03/08/2026: "por favor, confira os teste que você fez sozinho, não vou
  ter como fazer isso." (H, PARTE 2, pedido 36).
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §4 (abertura) e §4.2 item 2; verificador ("Abra todas
  as imagens geradas, uma por uma").

### A3. A conferência do layout com fotos desatualizadas; rodada 12 refeita (12/10/2026)
- **O que aconteceu:** a rodada 12 de layout (feita na nuvem em 09/10) usou fotos do programa parado na
  etapa 2, sem os painéis já decididos nas rodadas 7 a 11, e os arquivos-fonte dos esquemas não tinham
  sido guardados. Depois, a aba de conferência da etapa 2 também estava desatualizada. O Samuel:
  "cade o layout que tinhamos feito novo, as perguntas do layout estão usando o layout antigo, e nós já
  tinhamos feito varias escolhas, da uma olhada." e "no relatorio do editor de impressão tem uma aba do
  layout que eu acredito que não esteja atualizada com as escolhas passadas" (R, 12/10/2026).
- **A regra que nasceu:** antes de publicar uma conferência, um conferente abre **todas as fotos contra
  as decisões** dele; perguntas de layout são desenhadas na tela-base mais nova já decidida.
- **Onde está hoje:** H, PARTE -15 §5 ("Pedir conferência ao Samuel sem comparar as fotos com as
  escolhas dele antes"); R, 12/10/2026 e 13/10/2026 ("Fotos conferidas contra as escolhas antes de irem a
  ele"). Não achei a regra no CLAUDE.md nem nos agentes.

### A4. G6 juntado ao programa com poucas páginas-gabarito (12-13/10/2026)
- **O que aconteceu:** o endireitar antes de cortar (G6) passou nas páginas-gabarito e foi juntado em
  12/10; em 13/10 o verificador olhou 89 páginas de 19 livros e achou 6 que pioraram, todas **fora** do
  gabarito (faixa preta de 1,6 a 4,4 cm no Cursus 3, Matemática 32, Antiphon 88 e 260; números comidos
  na Escola 197). O defeito ficou no programa até o conserto em ramo (R, 13/10/2026).
- **A regra que nasceu:** incluir no gabarito do corte o Cursus 3, a Matemática 32, o Antiphon 260 e a
  Escola 197; conferir mais livros antes de juntar mudança de corte.
- **Onde está hoje:** R, 13/10/2026 ("Lição para o gabarito"); H, PARTE -15 §5. Não conferi se já
  entrou no `gabarito/lista.json`.

### A5. A mancha do verso dada como "feito e conferido"
- **O que aconteceu:** a PARTE 3 do H (tabela das queixas do Kaique, de 07/09/2026) diz, para "às vezes
  a parte de trás fica com uma mancha da parte da frente": "Feito e conferido". Está **errado**: a
  mancha do verso é o defeito mais grave aberto.
- **A regra que nasceu:** o estado que vale é o do [ESTADO-ATUAL](../docs/plano/ESTADO-ATUAL.md), não
  o da prosa antiga. A mancha do verso é o item 6.1 do plano.
- **Onde está hoje:** [ESTADO-ATUAL](../docs/plano/ESTADO-ATUAL.md) §4 ("NÃO corrigida"); [CLAUDE.md](../CLAUDE.md)
  §9 (primeiro ponto); [PEDIDOS.md](../PEDIDOS.md) BLOCO 9 ("NÃO corrigido").

### A6. Verificador é mais rigoroso que o implementador
- **O que aconteceu:** de 25 a 29/09/2026 os verificadores acharam várias vezes o que o implementador
  não viu (perda de trabalho sem aviso, contagens erradas; H, PARTE -8 §1). Em 13/10 o verificador
  achou "a tela mostra o que o PDF não tem" e a faixa preta do G6.
- **A regra que nasceu:** todo item passa por verificador independente; "não pular essa etapa".
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §8 (passos 6 a 8) e §10.1; H, PARTE -8 §1.

### A7. Página de conferência com dois trabalhos misturados (12/10/2026)
- **O que aconteceu:** a página tinha o G6 e o layout um embaixo do outro. O Samuel: "respondi o
  endireitar, mas ele trouxe junto coisas do layout, por favor confira, pois acho que teve alguma
  confusão". Em 09/10 a gerente já tinha posto várias imagens com uma pergunta só.
- **A regra que nasceu:** **um trabalho por aba**; em conferência de imagens, **cada quadro tem a sua
  pergunta e o seu comentário**.
- **Onde está hoje:** R, 12/10/2026 (G6); H, PARTE -14 §6.

### A8. Explicação errada num cartão de conferência (30/09/2026)
- **O que aconteceu:** o cartão D2 dizia que a zona do OCR decide como o programa trata a letra; não
  decide (as zonas são só a régua dos OCRs). A gerente corrigiu no Registro.
- **A regra que nasceu:** conferir no código antes de explicar; mostrar o resultado de cada escolha
  para ele decidir vendo ("preciso ver o resultado de cada tipo de seleção para saber qual escolher").
- **Onde está hoje:** R, 30/09/2026 (Conferência 3, "Correção da gerente"). Caso parecido em 17/09: a
  gerente explicou a prévia a 150 DPI e era 110 (H, PARTE -5 §4).

### A9. Livro inteiro pega o que página solta não pega (21/10/2026)
- **O que aconteceu:** a caixa do conteúdo passava em todas as páginas soltas e perdia o tamanho do livro ao gerar o Egenloff 1-14 (DPI da conta × DPI do desenho: a passada media a 150 e a geração era a 300).
- **A regra que nasceu:** conferir com um **livro inteiro** gerado, não só com páginas soltas; o tamanho do livro foi consertado em `57de8af`.
- **Onde está hoje:** H, PARTE -17 §4; ficha [2.5](itens/2.5.md).

---

## B. Perguntas ao Samuel

### B1. Pergunta mal explicada que voltou várias vezes ("Ainda não entendi")
- **O que aconteceu:** várias vezes. 30/09/2026: cartões F6, B4, B6, D1–D7, P1 "mal explicados, a
  refazer com explicação e fotos" (R, 30/09). 07/10: limpar pontinhos "Isso ficou horrivel para
  conferir, [...] traga exemplos melhores e que eu consiga destinguir o que é para ver" e "não entendi,
  explique melhor e com exemplos." (R, 07/10). 08/10: três perguntas da rodada 4 que falavam em "o jeito
  rápido e o manual" sem mostrar (H, PARTE -13 §0 e §4). 09/10: `g6-retangulo` "eu não entendi, me de
  mais exemplos e explique melhor." (R, 09/10). 12/10: três perguntas de layout, "Explique de maneira
  mais fácil e concisa.", "explique melhor e de maneira mais facil o que estou escolhendo" e "explique
  melhor, por favor e de forma mais simples." (R, 12/10). 19/10: no chat, a caixinha de pergunta cobria
  o texto (memória do Claude Code no PC do Samuel).
- **A regra que nasceu:** toda pergunta começa por "O que você está escolhendo: …", no máximo 3
  parágrafos curtos, a primeira imagem é só a parte que muda, ampliada, depois a tela inteira; imagem em
  cada opção; sempre a opção "Ainda não entendi". O comentário dele vale como resposta e a pergunta
  volta refeita na própria página.
- **Onde está hoje:** H, PARTE -15 §6 ("Como o Samuel entende uma pergunta"); H, PARTE -13 §0;
  [CLAUDE.md](../CLAUDE.md) §10.10; [geral/jeito-do-samuel.md](geral/jeito-do-samuel.md).

### B2. Perguntas G7 a G10 dadas como "nunca feitas" e já respondidas (12/10/2026)
- **O que aconteceu:** o resumo da nuvem (H, PARTE -14 §5) dizia que as perguntas G7 a G10 "nunca foram
  feitas"; o pesquisador conferiu que o Samuel já as tinha respondido em 05/10/2026
  ([relatorios/conferencia-samuel-2026-10-05-g.md](../relatorios/conferencia-samuel-2026-10-05-g.md)).
  Em 14/10 uma pergunta já respondida voltou e ele reclamou: "Porque essa opção voltou ? eu já não tinha
  respondido?" (R, 14/10/2026).
- **A regra que nasceu:** antes de perguntar, procurar a resposta nas respostas literais de
  `relatorios/` e no Registro; perguntar só o que falta.
- **Onde está hoje:** R, 12/10/2026 ("Correção de registro"). Regra parecida na memória do Claude Code
  no PC do Samuel ("Não mudar o combinado por pergunta": conferir o registro e citar onde está escrito).
  Não achei regra própria no CLAUDE.md.

### B3. Responder no chat o que ele perguntou na página (07/10/2026)
- **O que aconteceu:** ele comentou na página (a encadernação estragada ao apagar página) e a gerente
  respondeu com proposta e perguntas no chat.
- **A regra que nasceu:** "não me responda no chat quando tiver questionamentos nas conferencias,
  responda nas conferencias." e "o meu comentario serve como resposta, porque você não responde ele e me
  mostra a questão de novo?"; o comentário anterior **fica fixado** quando a pergunta volta.
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §10.10; R, 07/10/2026.

### B4. Retângulo rosa do cartão escondendo o "A" de CRISTÃ (01/10/2026)
- **O que aconteceu:** num formulário de conferência, um retângulo desenhado por cima da página
  escondeu a perna do "A" de "CRISTÃ" (Escola 7) e o Samuel achou que o programa cortava a letra. O
  `conferencia.py` (`gravar_paineis`) desenha esse retângulo rosa por cima.
- **A regra que nasceu:** **nunca desenhar retângulo por cima do conteúdo**; toda pergunta com foto,
  dizendo onde olhar, com o resultado ao lado do original. Para o que foi tirado: preto = fica, vermelho
  = o programa tirou, folha inteira em cima e a parte ampliada pintada de amarelo transparente.
- **Onde está hoje:** H, PARTE -9 §1 e §6; H, PARTE -12 §0 ("Formato de imagem que ele entende").

### B5. Imagens das perguntas feitas a 72 DPI (12-13/10/2026)
- **O que aconteceu:** as imagens das perguntas de geometria de 12/10 foram feitas com o DPI que o PDF
  declara (72 DPI no Horas, Graduale e Marial), mas o programa usa o DPI real do scan e a caixa do
  conteúdo muda com o DPI. Na Horas 14, com o DPI certo, a resposta mostrada mudava de verdade (R,
  13/10/2026, duas entradas).
- **A regra que nasceu:** imagem de pergunta sai **pela mesma conta e no mesmo DPI que o programa usa**
  (`core.caixas_scantailor.achar_na_pagina`); PDF que "diz 72 DPI" tem o DPI real calculado pela conta do
  detector de gravura.
- **Onde está hoje:** R, 13/10/2026; H, PARTE -15 §5 e PARTE -12 §5.

### B6. Imagens em grade 3×3 que não se entendem (06/10/2026)
- **O que aconteceu:** as imagens do limpar pontinhos em grade 3×3: ele não entendeu o que foi tirado
  e o que ficou.
- **A regra que nasceu:** uma linha de quadros lado a lado, legenda fixa embaixo (ver B4).
- **Onde está hoje:** H, PARTE -12 §0 e §4.

---

## C. Medir e testar

### C1. A régua dava número bom com a mancha piorando
- **O que aconteceu:** o `avaliar.py` mede o fundo longe da tinta; o Preto e branco escurece a mancha do
  verso (cinza fraco vira marca preta legível) e a régua não vê ([PLANO-RETOMADA.md](../PLANO-RETOMADA.md),
  07/09/2026). O Otsu marca zero pioras mas guarda o dobro de tinta do Sauvola.
- **A regra que nasceu:** "Número que não pega o pior defeito não pode dar veredito." O olho do Samuel
  decide; faltam critérios novos na régua.
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §4.2 e §9 (segundo ponto).

### C2. Velocidade medida com a máquina dividida (29 e 30/09/2026)
- **O que aconteceu:** em 29/09 uma medição feita com um agente rodando foi descartada; às 14:45 tudo
  saiu mais lento, até o que nenhuma mudança tocou. Em 30/09 às 16:26 deu "tudo mais lento" e era o
  emulador Android, o OBS e o Chrome do Samuel; o código antigo medido na mesma hora também saiu lento
  (R, 29/09/2026; H, PARTE -9 §1). Em 09/10: no Windows do GitHub as máquinas variam até 70% entre si
  (H, PARTE -14 §1).
- **A regra que nasceu:** comparar **antes e depois alternados (A, B, A, B) na mesma máquina**; a medida
  que vale é no PC do Samuel, parado e sem agentes, no fim de cada fase; no GitHub só o filtro alternado.
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §4.6 (decisão de 19/10/2026, "opção 2"); Agentes
  (seção de velocidade).

### C3. Teste simulado passa e o uso real falha (22/09/2026)
- **O que aconteceu:** duas vezes na mesma frente (arrastar no canto direito; mover conteúdo) o teste
  com clique simulado passou 100% e o Samuel não conseguia usar (o clique simulado é sempre exato).
  Em 23-24/09, de novo: o teste do widget isolado nunca refazia a prévia (H, PARTE -7 §4).
- **A regra que nasceu:** função de arrastar ou clicar só é dada como pronta depois de testada na
  **janela real com mensagens nativas de mouse**; toda área clicável precisa de pista visual.
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §8 passo 6; H, PARTE -6 §3 e §4; plano item 3.9.

### C4. Testes gravando no `erros.log` e na pasta de dados real do Samuel
- **O que aconteceu:** 29/09/2026: testes gravavam no `erros.log` real e criavam projetos na tela
  inicial dele ("camadas", "comum", 23 "fixture_gerado"). 30/09, ~13:35: ~6 linhas de teste no
  `erros.log` real. 06/10: o `teste_velocidade.py` gravou lá (16:18) e um verificador deixou 2 linhas
  (21:39 e 21:40). 08/10: o `tests/conftest.py` devolvia a pasta real no fim da sessão (Bugs; H, PARTE
  -12 §5 e PARTE -13 §1). Sobre as linhas antigas o Samuel disse (O2, 02/10): "Não, deixe como está -
  explique melhor, o que isso vai influenciar? e esses erros já foram resolvidos?"
  ([decisoes-samuel-2026-10-02.md](../relatorios/decisoes-samuel-2026-10-02.md)).
- **A regra que nasceu:** teste e script de teste usam **pasta de dados própria** e conferem o
  `erros.log` antes e depois; ninguém apaga as linhas do arquivo dele.
- **Onde está hoje:** R, 30/09/2026 (`c1c3cc2`) e 06/10/2026 (`9b4d87d`); `tests/conftest.py`;
  `pasta_de_dados_dos_scripts.py`; conserto do conftest juntado na nuvem (`a358d4e`, H, PARTE -14 §2).

### C5. Caixa "Tirar da lista?" aberta na tela do Samuel (30/09/2026)
- **O que aconteceu:** entre ~00:59 e 01:03 de 30/09, uma rodada de testes de um agente abriu uma caixa
  "Tirar da lista?" na tela do Samuel por uns 4 minutos (R, 30/09/2026). Antes disso, em 15-16/09, testes
  com `pywinauto` tomavam o mouse e o teclado dele (ele reclamou duas vezes; H, PARTE -4 §4).
- **A regra que nasceu:** **nenhum teste abre janela na tela do Samuel**: Qt sem tela, caixa sem
  resposta falha em 20 s. Para pilotar a janela real: instância própria, fora da tela, mensagens nativas.
- **Onde está hoje:** R, 30/09/2026 (`c1c3cc2`); H, PARTE -9 §1; [CLAUDE.md](../CLAUDE.md) §4.6 (piloto da
  janela de verdade é no PC, pelo verificador).

### C6. `teste_botoes.py` clicando em botões escondidos
- **O que aconteceu:** o `teste_botoes.py` clica também em botões escondidos; com os botões novos de
  apagar, o roteiro apagava as duas páginas do livro de teste e chegava ao "Processar" sem página nenhuma
  (13/10/2026, consertado em `b5b224f`). Já em 29/09 um PDF de 2 folhas falhava assim (Bugs, 29/09).
- **A regra que nasceu:** falha do `teste_botoes` pode ser do roteiro, não do programa: conferir antes
  de culpar o código.
- **Onde está hoje:** H, PARTE -15 §6; R, 13/10/2026 (parecer do verificador do "Para revisar").

### C7. A tela mostra o que o PDF não tem
- **O que aconteceu:** a prévia é desenhada a 110 DPI (abas) ou 150 DPI (análise) e o PDF a 300; as duas
  decidem diferente. 28/09/2026: cortes diferentes na prévia e no PDF (até 8% no Palatino 5). 06/10:
  conserto do desenho e "muito" do limpar pontinhos quase não aparecem na prévia. **13/10 (grave):** no
  "Só as letras" a letra T do Antiphonal 46 aparece inteira na tela e some no PDF (Bugs, 13/10).
- **A regra que nasceu:** conferir no PDF gerado, não só na tela; ainda é pergunta ao Samuel se a tela
  passa a mostrar o desenho do tamanho do PDF.
- **Onde está hoje:** Bugs (28/09 e 13/10); H, PARTE -15 §6 e PARTE -12 §5; R, 13/10/2026 (pergunta
  "mostrar na tela o mesmo que o PDF").

### C8. Testar em isolamento não pega travamento de concorrência (08/09/2026)
- **O que aconteceu:** o travamento do MuPDF nunca aparecia rodando uma thread só; só com várias threads
  lendo o mesmo PDF. E em 12-13/09 as correções "resolvidas nos testes" travaram de novo na mão do Samuel.
- **A regra que nasceu:** reproduzir o travamento como o programa roda de verdade (`py-spy` no processo
  vivo); travamento só se dá como resolvido com navegação real.
- **Onde está hoje:** H, PARTE -2 ("Caminhos tentados e descartados") e PARTE -3.

### C9. `teste_botoes.py` contra um livro do acervo quase apagou um projeto (07/09/2026)
- **O que aconteceu:** a limpeza do fim do script ("remover da lista") quase apagou o projeto do Boécio
  de 05/08 (só não apagou porque o script travou antes).
- **A regra que nasceu:** o `teste_botoes.py` gera o próprio PDF sintético; nunca usar livro do acervo.
- **Onde está hoje:** H, PARTE -1; [PLANO-RETOMADA.md](../PLANO-RETOMADA.md) (Fase 0, item 3).

### C10. Prints sem a tela de verdade (17/09/2026)
- **O que aconteceu:** os prints no modo `offscreen` saíram com o texto em quadradinhos (esse modo não
  tem fonte) e o "offscreen" engana sobre tamanho (30/09).
- **A regra que nasceu:** texto não se confere em print `offscreen`; para desenhos SVG, usar o Chrome sem
  janela.
- **Onde está hoje:** H, PARTE -5 §1 e PARTE -16 §6; verificador.

### C11. O teste tem de medir o que é pintado (20-21/10/2026)
- **O que aconteceu:** no Qt com a escala do Windows em 125%, a imagem guardada no tamanho certo e pintada com `pix.scaled(tamanho lógico)` ficou borrada; o teste olhava a imagem guardada, não a pintada.
- **A regra que nasceu:** reduzir nos pixels de verdade (`razao_do_pintor`) e testar o que é **pintado**.
- **Onde está hoje:** H, PARTE -17 §4; ficha [layout](itens/layout.md).

### C12. Testar a ferramenta sobre a página que já passou pelas etapas anteriores (20/10/2026)
- **O que aconteceu:** o Samuel viu que o corte falhava no teste porque a página não tinha sido endireitada antes: "vamos ficar tentando concertar uma ferramenta que não precisa ser consertada".
- **A regra que nasceu (pedido dele, 20/10/2026):** cada funcionalidade testada sobre páginas que passaram pelas etapas anteriores. Como aplicar em todos os testes: pergunta ainda não feita a ele.
- **Onde está hoje:** R, 20/10/2026 (`cg6`); H, PARTE -17 §1; ficha [2.2](itens/2.2.md).

### C13. O mesmo código nem sempre dá a mesma imagem (20/10/2026)
- **O que aconteceu:** a Horas 11 em Mágico pro saiu diferente numa passada longa com pouca memória: o modelo de regiões ficava desligado a sessão inteira e o detector de gravura caía no antigo. A prova de "sai igual" por soma acusou diferença falsa.
- **A regra que nasceu:** repetir antes de concluir; consertado em `2ff16e7` (tenta de novo).
- **Onde está hoje:** H, PARTE -17 §4; Lista de bugs 20/10/2026; [bugs](bugs.md).

---

## D. Arquivos, disco e PC do Samuel

### D1. Um agente apagou `D:\d` (29/09/2026)
- **O que aconteceu:** o agente criou sem querer a pasta (o caminho do Git Bash `/d/programas` virou
  `D:\d\programas`), moveu o download e apagou a pasta inteira sem olhar o que havia dentro. Apagado por
  comando não vai para a Lixeira. A pergunta "você tinha uma pasta `D:\d`?" nunca foi respondida.
- **A regra que nasceu (Samuel, 29/09/2026):** fora da pasta do projeto, nada é apagado sem perguntar
  ao Samuel (o agente para e relata à gerente); dentro, só o que o próprio agente criou naquela tarefa.
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §10.9; Agentes ("Apagar arquivo ou pasta"); H, PARTE -12 §0.

### D2. `robocopy /MOVE` sem `/XJ` esvaziou `modelos\` e `gabarito\` (07/10/2026)
- **O que aconteceu:** a gerente moveu os temporários antigos do Claude do C: para o D: com robocopy,
  que seguiu as junções de um scratchpad e esvaziou `modelos\` (18 arquivos) e `gabarito\paginas\` +
  `scantailor-24-09\` (117 arquivos) das 19h20 às 22h. Restaurado da cópia no D:.
- **A regra que nasceu:** **nunca mover nem apagar uma árvore de pastas sem listar as junções antes**;
  junção se desfaz só com `(Get-Item <junção>).Delete()`, nunca `Remove-Item -Recurse`.
- **Onde está hoje:** R, 07/10/2026; H, PARTE -13 §0; Agentes ("Pastas com junção").

### D3. Quatro agentes esgotaram a memória do PC (07/10/2026)
- **O que aconteceu:** às 18h36, quatro agentes com testes em paralelo esgotaram os 15 GB de memória; o
  `C:\pagefile.sys` chegou a 33 GB, o C: a 0 GB, e o Claude Code caiu levando os agentes. Em 05-06/10 já
  havia testes falhando por falta de memória com vários agentes (H, PARTE -11 §4).
- **A regra que nasceu:** no máximo 3 a 4 agentes ao mesmo tempo; um arquivo de pytest por vez no PC;
  TEMP, TMP e `--basetemp` dentro da worktree; esperar com menos de 3 GB livres. Desde 19/10 a suíte
  inteira roda no GitHub.
- **Onde está hoje:** R, 07/10/2026; H, PARTE -13 §0; [CLAUDE.md](../CLAUDE.md) §4.6.

### D4. `git stash` com arquivos de outro agente (01/10/2026)
- **O que aconteceu:** um agente rodou `git stash`/`stash pop` por ~2 s na mesma pasta em que outro
  agente tinha arquivos não salvos; voltaram sem conflito, por sorte (R, 01/10/2026, consertos da
  conferência 5).
- **A regra que nasceu:** cada frente trabalha **na sua própria cópia (worktree) e no seu ramo**.
  Não achei uma regra escrita só sobre `git stash` (procurei no CLAUDE.md e nos agentes).
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §10.3.

### D5. O programa que o Samuel abria não era o programa alterado (até 07/09/2026)
- **O que aconteceu:** ele abriu e viu a tela antiga (sem menu, com a barra já corrigida): rodava um dos
  instaladores `.exe` antigos soltos na área de trabalho. Em 22/09 o atalho antigo da Área de Trabalho
  Pública (instalador de 01/09) de novo confundiu um teste (H, PARTE -6 §3).
- **A regra que nasceu:** abrir sempre pelo atalho "Editor de Impressao (desenvolvimento)"; apagar o
  atalho antigo (item 0.2, ainda `[~]`: o Samuel apaga à mão, precisa de admin).
- **Onde está hoje:** [PLANO-RETOMADA.md](../PLANO-RETOMADA.md) (Fase 0); [CLAUDE.md](../CLAUDE.md) §8
  passo 9; plano item 0.2.

### D6. Trabalho sem commit desde 17/09 e plano mudando a cada conversa
- **O que aconteceu:** de 17 a 23/09/2026 o trabalho acumulou sem commit (~34 arquivos) porque a sessão
  acabava antes de o Samuel testar; houve 5 versões de handoff e ~110 itens, nenhum aprovado; o trabalho
  foi para a tela, não para a imagem.
- **A regra que nasceu:** o plano definitivo (24/09) só muda pelo Samuel, com Registro; ideia nova vai
  para a Lista de espera; cada item vira **commit separado** no ramo `fase-1` (28/09); nenhum plano novo
  apaga pendência por omissão.
- **Onde está hoje:** [ESTADO-ATUAL](../docs/plano/ESTADO-ATUAL.md) §3 ("Por que o projeto parou"); plano,
  regras 2, 3 e 7; R, 28/09/2026; [CLAUDE.md](../CLAUDE.md) §10.2 e §10.6.

### D7. A cópia do plano do Samuel sobrescrita (25/09/2026)
- **O que aconteceu:** uma conversa do claude.ai que não enxergava a cópia do repositório sobrescreveu a
  cópia do plano do Samuel e apagou anotações; foi preciso juntar à mão (H, PARTE -8).
- **A regra que nasceu:** o plano tem duas cópias, comparadas no começo de cada conversa e mudadas
  juntas; antes de gravar a do HD, conferir que não mudou e guardar a anterior. Pedido do Samuel em
  09/10: "ok, por favor tome muito cuidado, porque não quero apagar as varias rodadas que eu fiquei
  respondendo relatorios, quero que isso continue salvo e que o plano não mude, só seja acrescentado
  coisas."
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §10.4; R, 09/10/2026; H, PARTE -14 §6.

### D8. 48 MB de imagens no histórico do `fase-1` (28-29/09/2026)
- **O que aconteceu:** imagens de uma rodada de conferência entraram num commit por engano.
- **A regra que nasceu:** `relatorios/conferir/**` guarda só os `.md` no git; o Samuel decidiu juntar o
  trabalho aprovado num commit só ao levar ao `master` (O4: "Juntar (um commit só no master)").
- **Onde está hoje:** H, PARTE -8 §2; R, 02/10/2026 (O4).

### D9. Processos e janelas deixados abertos pelos agentes (05-07/10/2026)
- **O que aconteceu:** verificadores interrompidos deixaram 14 processos abertos (o Samuel fechou à
  mão); 31 `grep.exe` órfãos; a ferramenta de segurança não deixa a gerente encerrar processos do
  Samuel ("Interfere With Workloads").
- **A regra que nasceu:** cada agente fecha as próprias janelas e vigias ao terminar; para fechar o que
  é do Samuel, pedir a ele.
- **Onde está hoje:** H, PARTE -11 §4, PARTE -13 §4 e PARTE -6 §3.

---

## E. Registros que mentiam

### E1. Prosa de checkpoint dizendo "corrigido" e outro documento o contrário (menu "Abrir")
- **O que aconteceu:** o bug do menu "Abrir" foi corrigido em 07/09/2026 (`9d27b76`) e o handoff disse
  isso no mesmo dia, mas o CLAUDE.md §9 continuou dizendo "não corrigido" até 22/09.
- **A regra que nasceu:** prosa de checkpoint é registro histórico, não prova; quando o estado importa,
  checar o código e o `git log`.
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §9 (último ponto) e §10.8.

### E2. Pesquisa que só existiu na conversa (15-16/09/2026)
- **O que aconteceu:** o documento completo da pesquisa do ScanTailor (o que existe lá, o que falta no
  nosso) não foi salvo em arquivo; se retomado, teria de ser refeito.
- **A regra que nasceu:** "Toda decisão tomada em qualquer conversa vira documento no projeto. As
  conversas não enxergam umas às outras, só os documentos." O pesquisador grava em `docs/pesquisa/`.
- **Onde está hoje:** plano, regra 7; [CLAUDE.md](../CLAUDE.md) §10.1 e §10.7; H, PARTE -4 §2.

---

## F. Ferramentas e comandos

### F1. Limite de uso da conta derrubando agentes
- **O que aconteceu:** com 3 ou mais agentes por horas, a conta bateu o limite e todos pararam no meio:
  3 vezes de 25 a 29/09 (H, PARTE -8 §1), 05/10 ~21h40 (PARTE -11 §4), 06/10 (PARTE -12 §5) e 3 vezes
  em 12-13/10 (PARTE -15 §6).
- **A regra que nasceu:** cada agente faz **commit e push a cada passo** e mantém um `ONDE-PAREI.md`;
  retomar com SendMessage para o mesmo agente (ele continua do ponto).
- **Onde está hoje:** Agentes ("Commit e push a cada passo... o limite de uso da conta já derrubou
  agentes três vezes"); H, PARTE -15 §6.

### F2. `Set-Content` com BOM e commit com aspas no PowerShell
- **O que aconteceu:** no PowerShell 5.1, mensagem de commit com aspas quebra em `-m`; `Set-Content
  -Encoding utf8` põe BOM (o título do commit `7485e1b` ficou com um).
- **A regra que nasceu:** usar `git commit -F arquivo`; gravar texto com a ferramenta Write (UTF-8 sem
  BOM).
- **Onde está hoje:** H, PARTE -15 §6.

### F3. A ferramenta Bash estragando barra invertida (29/09 a 02/10/2026)
- **O que aconteceu:** strings com `\` dentro de heredoc viraram caracteres de controle no plano duas
  vezes (`\f`, `\b`; `%TEMP%\verif`); um heredoc longo com aspas falhou; o formulário 7 ficou quebrado
  alguns minutos no GitHub por um `]},` a mais; um `&&` encadeado commitou um passo quebrado.
- **A regra que nasceu:** texto com `\` ou longo: gravar com Write e só depois inserir por script;
  conferir "caracteres de controle = 0"; validar o JavaScript (`node -e "new Function(...)"`) e
  renderizar no Chrome sem tela antes de commitar.
- **Onde está hoje:** H, PARTE -9 §1 e PARTE -10 §4.

### F4. A ação `open` da ferramenta Artifact não chega ao navegador do Samuel (06/10/2026)
- **O que aconteceu:** a ação respondia "Opened" e nada abria para ele; ele reclamou.
- **A regra que nasceu:** abrir com `start "" "<endereço>"`.
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §10.10; H, PARTE -12 §0.

### F5. Páginas do claude.ai: fotos que não apareciam e publicação recusada
- **O que aconteceu:** 09/10/2026: página publicada com o contrato novo (0.2.75) não mostrava as fotos
  para o Samuel. 13-14/10: publicar numa página feita em outra sessão é recusado na primeira (e às vezes
  na segunda) tentativa.
- **A regra que nasceu:** manter o contrato da página (0.2.69/0.2.70); reenviar o mesmo conteúdo;
  imagens em `files` com `root`; escrever no banco com a versão lida (`if_version`).
- **Onde está hoje:** H, PARTE -14 §6, PARTE -15 §6 e PARTE -16 §6.

### F6. Isolamento automático de worktree do Agent (05/10/2026)
- **O que aconteceu:** o `isolation: "worktree"` criou cópias a partir do `master` antigo, misturadas com
  arquivos soltos.
- **A regra que nasceu:** não usar; criar as worktrees à mão a partir do `fase-1`.
- **Onde está hoje:** H, PARTE -11 §3.

### F7. Rodar a suíte inteira depois de cada junção (07-08/10/2026)
- **O que aconteceu:** ~110 arquivos, ~23 min por rodada no PC; depois de cada junção levava horas.
- **A regra que nasceu:** juntar tudo e rodar uma vez; desde 19/10 a suíte inteira roda no Windows do
  GitHub em toda entrega, e no PC (com os agentes parados) antes de entrar no `fase-1`.
- **Onde está hoje:** H, PARTE -13 §0 e §4; [CLAUDE.md](../CLAUDE.md) §4.6.

### F1b. Limite da conta com 5 a 8 agentes (20-21/10/2026)
- **O que aconteceu:** a conta bateu o limite três vezes (20/10 de manhã, 20/10 à tarde, 21/10 de madrugada); os agentes pararam no meio.
- **A regra que vale:** a de F1 (commit + `ONDE-PAREI.md` a cada passo, retomar com SendMessage depois do horário que o erro informa). Nada se perdeu.
- **Onde está hoje:** H, PARTE -17 §4; [pc-e-github](geral/pc-e-github.md).

### F7b. Mensagem de commit pelo scratchpad compartilhado (20/10/2026)
- **O que aconteceu:** um agente pegou a mensagem de commit de outro, gravada no scratchpad compartilhado.
- **A regra que nasceu:** cada agente grava a mensagem num arquivo dentro da **própria** worktree.
- **Onde está hoje:** H, PARTE -17 §4; [regras-de-trabalho](geral/regras-de-trabalho.md) §9.

### F8. `gh run watch` de vários agentes esgota a API do GitHub (20/10/2026)
- **O que aconteceu:** vários agentes com `gh run watch` ao mesmo tempo bateram no limite de consultas (HTTP 403).
- **A regra que nasceu:** disparar a rodada e ler o resultado **uma vez só, no fim**.
- **Onde está hoje:** H, PARTE -17 §4; [pc-e-github](geral/pc-e-github.md) §10.

### F9. Medir velocidade direto no GitHub (20/10/2026)
- **O que aconteceu:** as máquinas do GitHub variam até 70%.
- **A regra que nasceu:** medir antes e depois **na mesma máquina, alternando**, com espera do processador (< 15%) e piso de 2% (filtro `velocidade_ab`).
- **Onde está hoje:** H, PARTE -17 §3; [pc-e-github](geral/pc-e-github.md) §10.

---

## G. Rumo do trabalho

### G1. Duas versões anteriores fracassaram (antes de 18/07/2026)
- **O que aconteceu:** a v4/v5 em customtkinter **travava** (memória e customtkinter) e a qualidade dos
  filtros, feitos "à mão" com fórmula caseira, ficou ruim.
- **A regra que nasceu:** PySide6, nunca tkinter/customtkinter; uma página por vez na memória; algoritmo
  consagrado em vez de fórmula própria; nenhum modelo generativo.
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §1 e §3; H, Apêndice A ("Histórico do projeto").

### G2. Emoji quebrou no Windows
- **O que aconteceu:** a versão anterior quebrou no Windows por causa de emojis em rótulos.
- **A regra que nasceu:** nenhum emoji em rótulo de interface (ícones desenhados ou texto puro).
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §3; H, Apêndice A §3.4.

### G3. O seletor de gravura recriado duas vezes e falhou (31/07 e 16/09/2026)
- **O que aconteceu:** o detector do ScanTailor foi recriado em Python a partir da descrição em 31/07
  (`e8aeec9`) e de novo em 16/09; nas duas, a régua da seleção piorou (24/26 → 20/26), porque o vão entre
  linhas de um livro é menor que o vão entre traços de gravura de outro. O seletor **original** do
  ScanTailor, testado em 24/09, funcionou bem melhor.
- **A regra que nasceu:** usar o **código original** do ScanTailor Advanced (compilado), não recriar;
  "Não vale tentar de novo sem uma ideia genuinamente diferente." Desde 13/10, a Fase 2 é "igual ao
  ScanTailor, sem perguntar antes".
- **Onde está hoje:** [ESTADO-ATUAL](../docs/plano/ESTADO-ATUAL.md) §3 e §4; plano item 1.2 e abertura
  da Fase 2; H, PARTE -4 §2.

### G4. ScanTailor implementado e revertido (15-16/09/2026)
- **O que aconteceu:** o Samuel pediu para trazer o que havia de bom no ScanTailor; foram implementadas
  9 frentes (312 testes passando), e ao ver o resumo ele decidiu: "não vou comitar, quero voltar a versão
  que estava antes." Revertido com `git stash`.
- **A regra que nasceu:** planejar e combinar o plano inteiro antes de codar; frente grande só com o
  plano aprovado. (Em 17/09 ele pediu planejar devagar, uma decisão por vez.)
- **Onde está hoje:** H, PARTE -4 §2; [CLAUDE.md](../CLAUDE.md) §2 ("Planejar antes de codar"); memória
  do Claude Code no PC do Samuel ("Planejar devagar, um por um").

### G5. O "tirar o fundo" automático trocado por filtro (29/09/2026)
- **O que aconteceu:** o item 1.1 foi ligado como automático, com caixinha por livro; o verificador
  mostrou que projetos salvos do Samuel mudariam de aparência ao reabrir e que o fundo só saía depois de
  escolher um filtro. Ele mudou a decisão no mesmo dia.
- **A regra que nasceu:** "Página sempre abre em 'Original', sem mexer." e "Assim eu decido se tiro ou
  não, e o Kaique escolhe um filtro só, sem mudança escondida." Toda função automática tem botão de
  ligar e desligar.
- **Onde está hoje:** plano item 1.1 e regra 8; R, 29/09/2026.

### G6. "Porque não vai até o final?" (04/08/2026)
- **O que aconteceu:** o Claude Code parava a cada etapa perguntando por onde seguir.
- **A regra que nasceu:** "porque você continua travando , porque não vai até o final?": decidir
  sozinho dentro da alçada e executar o protocolo inteiro. **Mas** perguntar antes de mexer em estrutura,
  em tela ou no que está na lista de "precisa perguntar".
- **Onde está hoje:** [CLAUDE.md](../CLAUDE.md) §2 e §6; memória do Claude Code no PC do Samuel ("Ir
  até o fim").

---

## H. Caminhos técnicos já fechados

Não são erros de processo, mas caminhos que custaram caro e **não devem ser repetidos** sem ideia nova.
O detalhe de cada um está em `relatorios/melhorias.md` e nas seções "Tentado e descartado" do H.

- Cinco sinais para separar escrita antiga de foto: os números se cruzam nos cinco
  ([CLAUDE.md](../CLAUDE.md) §5; H, PARTE 5 §2).
- Receita difundida de "magic color" (dividir por `GaussianBlur` canal a canal): estraga capas
  coloridas ([CLAUDE.md](../CLAUDE.md) §9).
- Realçar a cor do Mágico pro em LAB, YCrCb ou devolvendo o cinza: as três consertavam o papel e
  engrossavam a rubricação (H, PARTE 4).
- Moldura em traço preto no Preto e branco de fábrica; pontilhados para foto no Preto e branco: reprovados
  pelo Samuel (H, PARTE -9 §5).
- Usar só as linhas do OCR no Misto: apaga música, capitulares e figuras; opção D (papel não branco)
  descartada: "A opção D fica de fora, porque o papel tem que sair branco." (R, 05/10/2026; H, PARTE -11 §3).
- Aviso "tinta forte fora do texto > 10%" como critério do "Para revisar": manda páginas certas à toa
  (H, PARTE -12 §4).
- Corte da sobra do ScanTailor no modo "forçado": jogou fora uma página inteira (H, PARTE -12 §4).
- Corte do G6: girar preenchendo a cunha com a beirada; máscara da cunha em todas as contas (H, PARTE -15 §5).
- Procurar a marcação do tamanho do PDF na frente da prévia: atrasava a primeira prévia (H, PARTE -15 §5).
- Hipóteses de travamento já descartadas: modelo ONNX carregando devagar; "glitch de repintura" (H, PARTE -2).
- Mexer em pywinauto com o Samuel usando o PC; roda do mouse por mensagem sem foco; área de trabalho
  virtual nova (H, PARTE -4 §4).

## Acrescentadas em 24/10/2026 ([PARTE -20](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §4)

- **Agente que já sabe usar o programa não acha o que confunde o leigo.** O verificador dos 14 livros marcou as caixinhas certas e não reencontrou os achados do Samuel; ele cobrou: "ele não achou nem os problemas que eu mesmo disse que achei?". Regra: confusão de uso se acha com o Samuel (testes guiados) ou com roteiro que imite o leigo; relatório de agente sempre cruzado com os achados dele.
- **Nunca fechar `python.exe` em geral.** Guardar o PID de tudo o que o agente abre e fechar só esses (o agente do mapa fechou processos sem conferir). Toda janela nova fora da tela, inclusive "Antes de processar" (apareceu na tela do Samuel em 23/10).
- **Suíte que passa no GitHub pode falhar no PC pela ordem dos testes.** Estado global de "uma vez por sessão" (aviso da gravura) vazava entre testes; o conserto é limpar no `tests/conftest.py`, não arquivo por arquivo. Achar a origem com uma sonda (`-p` plugin espiando a função), não com palpite.
- **Caminho Windows em Python dentro de heredoc do Bash quebra** (`\2`, `\p`). Usar `D:/...` ou o Write.
- **Agentes pesados no PC enquanto o Samuel testa derrubam o programa dele.** Em 28/10, 4 agentes rodando testes e prints ao mesmo tempo coincidiram com duas falhas de memória no processar dele (2-12). Com ele usando o PC: um processo pesado por vez, e avisar antes.
- **Print mandado no meio do turno não vira arquivo.** Conferir a pasta `images` da sessão e pedir de novo; nunca dizer "guardei" sem o arquivo.
- **Responder ao que ele perguntou, não ao que parece.** Em 28/10 a gerente disse que o "está certo" funcionou (o tique apareceu); ele: "você está vendo errado [...] deveria sumir quando eu aperto está certo." Ler o que ele circulou.
