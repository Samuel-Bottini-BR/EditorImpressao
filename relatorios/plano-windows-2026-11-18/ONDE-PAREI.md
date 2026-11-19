# ONDE PAREI: plano da parte do Windows (18/11/2026)

Cópia `.claude/worktrees/plano-windows`, ramo `plano-windows-2026-11-18`, a partir de `obra-2026-10-26` (`0e510978`).
Tarefa só de leitura e escrita do plano: **nenhuma linha do programa nem dos testes muda.** Nenhuma janela na tela do
Samuel, nenhuma pergunta do Windows, nada instalado, nada apagado. Nenhum agente aberto.

## Decisões que esta tarefa precisa cumprir
- D-767 (18/11): "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione" · "quero
  que faça as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros na hora de montar a estrutura do
  atualizador e testes a distancias". O plano prova cada peça de verdade e à vista; peça de mentira não conta como prova.
- D-765 (17/11): "eu não quero fazer nenhum conserto até o .exe estar pronto para o kaique e a questão de eu poder lançar
  testes no pc dele funcionar." O plano é só da frente do notebook do Kaique.
- D-766 (17/11): "os proximos consertos eu quero poder arrumar e poder atualizar a versão dele sempre que eu puder".
- D-605 (03/11): "nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e
  testado". O plano lista cada decisão que muda e cada teste antigo que muda; nada disso sem o "sim" dele.
- CLAUDE.md §11.12, ampliada em 18/11 ("eu acho que tinhamos que atualizar a regra de gambiarras para que ela se
  aplicasse a tudo né?"): uma peça só para cada conversa com o Windows; nada dá como feito o que não conferiu; a lista
  das falhas antes de escrever; teste com peça de mentira não prova.
- CLAUDE.md §11.13: as perguntas no formato "Do que se trata · O que acontece hoje · Sua dúvida → resposta · O que você
  escolhe", sem palavra de dentro.
- D-709 (16/11): plano antes de mexer, com a causa do erro.
- As decisões D-705 a D-764 da frente do notebook do Kaique (lidas inteiras; as que o plano toca estão no plano, seção 4).

## O que já está escolhido e testado aqui
- Decisões cumpridas na etapa 5 (relatório da etapa 5): D-711, D-712, D-713, D-714 (parte), D-715, D-716, D-718, D-719,
  D-721, D-723, D-724, D-728, D-729, D-730, D-732, D-733, D-735, D-736, D-738, D-763. Pela metade: D-717, D-722, D-727,
  D-737, D-764. Não cumpridas: D-720, D-734, D-731. Não testadas: D-741.
- Testes que existem para estas partes: `test_decisoes_atualizacao.py`, `test_decisoes_ajudante_da_atualizacao.py`,
  `test_decisoes_testes_a_distancia.py`, `test_decisoes_desinstalar.py`, `test_decisoes_desinstalar_pasta.py`,
  `test_decisoes_preparo_d749.py`, `test_assinatura.py`, `test_empacotar.py`, `test_nome_do_pacote.py`,
  `test_sem_janela_na_tela.py`, `test_decisoes.py`. Os que o plano mudaria estão no plano, seção 4.2.

## Como fica para quem usa e no livro
Esta tarefa não muda nada. O que o plano mudaria para o Kaique está no plano, seção 1.4. Nada muda nos livros nem no PDF.

## Feito
- [x] Data conferida (`date`: qua 18/11/2026 14:32).
- [x] Cópia nova criada (`git worktree add`, ramo `plano-windows-2026-11-18`).
- [x] Lidos inteiros: `implementador.md`; CLAUDE.md §1 a §11.13; `memoria/INDICE.md` e `memoria/itens/6.8.md`
  (não existem fichas próprias de atualização nem de testes à distância na memória: anotado no plano, riscos);
  D-605 e D-700 a D-767 do Livro; as linhas de 17 e 18/11 da Lista de bugs e do Registro do Plano
  (`D:\programas\EditorImpressao\docs\plano\PLANO-DEFINITIVO.md`); os três relatórios de hoje; o relatório e o ONDE-PAREI
  da etapa 5.
- [x] Lidos no código (só leitura): `core/_testes_a_distancia_windows.py` inteiro; as funções de `atualizacao.py`,
  `core/testes_a_distancia.py`, `main.py`, `ui/tela_configuracoes.py`, `ui/aviso_de_atualizacao.py`; os testes antigos
  que o plano tocaria. O código é o mesmo que as revisões leram (`b74a94e2`): de lá até `0e510978` só mudou o CLAUDE.md.
- [x] Plano escrito: `plano.md`, `plano.html`, `plano.pdf` nesta pasta.

## Perguntas para o Samuel
Estão no plano, seção 5 (16 decisões, em ordem, no formato do CLAUDE.md §11.13). A gerente leva à Central.

## Versão 2 do plano (18/11/2026, 18:10)
- [x] Data conferida (`date`: qua 18/11/2026 17:54).
- [x] Lidos inteiros: `implementador.md`; o CLAUDE.md inteiro (com a §11.12 ampliada, seis pontos, e a §11.13);
  `memoria/INDICE.md`; D-765 a D-790 do Livro (`obra-2026-10-26`, `48d2c3a8`) e D-712, D-721, D-724, D-727, D-739, D-741
  para conferir; `plano.md` e este ONDE-PAREI; o estudo do Kraken (`kraken-separado-2026-11-18`); a proposta das regras
  (§1 contradições, §2, §3, §5, §6, §9).
- [x] Escrito `plano-v2.md` (+ .html e .pdf por `relatorio.gravar`). O `plano.md` ficou como estava (histórico).
- Decisões que esta versão precisa cumprir: D-765 a D-790 (lista "decisão → onde está" na seção 10 do plano-v2).
- Nenhuma linha do programa nem dos testes mudou. Nenhuma janela, nenhuma pergunta do Windows, nenhum agente aberto.
- Perguntas para o Samuel: no plano-v2, seções 6.2 (o que depende dele) e 6.3 (três pontos em que duas decisões, ao pé
  da letra, não combinam). A gerente as leva no formato do CLAUDE.md §11.13.

## Versão 3 do plano (18/11/2026, começada 21:42 pelo relógio do PC; o Livro data as respostas novas de 19/11)

Pedido da gerente: aplicar as respostas do Samuel de hoje (D-791 a D-798, a aprovação do estudo do Kraken na D-768, o
fato novo da pergunta do Windows) e montar um resumo de uma página para ele aprovar. Só documento.

### Decisões que esta tarefa precisa cumprir
- D-791: "b" (o porteiro barra desde o primeiro dia); lista de exceções: "Sim" · "sim" (cada erro que já existe com data
  e o passo que o conserta; só diminui; nada entra sem o "sim" dele). Feito em `tests/` e no git, não como gancho.
- D-792: "ok" (o formulário único da entrega, conferido por um programa).
- D-793: "ok" (agentes sem a ferramenta de abrir agente nem a da Central; construída).
- D-794 (muda a D-769): "eu acho que deveria aparecer o aviso para atualizar ou não na hora de fechar e se ele disser
  sim, o programa fecha e fica uma janelinha em segundo plano tipo esses iconizinhos, mostrando porcentagem
  atualizando" · "da proxima vez que ele abrir o programa".
- D-795: "ok" (o Setup.exe continua sendo feito, mas o publicar o apaga no fim, também com erro; não vai ao GitHub nem ao
  Kaique).
- D-796: "1, mas tem que ser explissito o pedido né" · "o porteiro tem que bloquear".
- D-797: "Só precisa de dois lugares né?" · "ok" (versão de teste e oficial; o `master` sai das regras).
- D-798: "fechou" (só quem confere escreve PRONTO PARA CONFERIR, nunca sobre o que construiu).
- D-768: estudo do Kraken aprovado ("sim", 19/11).
- Continuam: D-765 ("eu não quero fazer nenhum conserto até o .exe estar pronto para o kaique..."), D-767, D-775, D-785,
  D-605, CLAUDE.md §11.12 (ampliada) e §11.13.
- Fato novo (Samuel, 19/11: "veio direito"): com o programa na frente, a pergunta do Windows veio no meio da tela.
- Em aberto, não decidir: X3 (adiada), X6, X9, X10.

### O que já está escolhido e testado aqui
- Tudo o que o plano-v2 lista (seção 9 e o ONDE-PAREI da v1). Novo para a v3: o fechar do programa grava primeiro e
  não pergunta "quer salvar?" (`ui/janela_principal.py`, `closeEvent`, docstring: "um 'não' por engano apagaria um dia
  de trabalho do Kaique"). A pergunta "Atualizar agora?" da D-794 não pode mudar isso: ela vem depois de gravar e o
  "Não" nunca perde trabalho.

### Como fica para quem usa e no livro
Esta tarefa não muda nada. O que a v3 muda para o Kaique está no plano-v3, seção 4. Nada muda nos livros nem no PDF.

### Feito (v3)
- [x] Lidos: `implementador.md`; CLAUDE.md inteiro (§11.12 e §11.13); `memoria/INDICE.md`,
  `memoria/geral/atualizador.md`, `memoria/geral/testes-a-distancia.md`; D-767 a D-798 inteiras (obra-juncao,
  `82ef9e64`); o plano-v2; a proposta das regras §1 (contradições) e §5 (as 24 conferências).
- [x] Contada a lista de exceções no código da versão de teste (o código é o mesmo desde `b74a94e2`; conferido com
  `git diff`): ver plano-v3, passo 0.
- [x] Lidos para a D-794 (§11.12, ponto 6): documentação do `QSystemTrayIcon` (Qt for Python 6); código do Velopack
  1.2.161 (`apply_windows_impl.rs`, `util_windows.rs`, `l18n/src/progress.rs`); Microsoft sobre a sessão 0; a pergunta
  do Microsoft Q&A sobre os ícones escondidos do Windows 11. O que cada um diz está no plano-v3, peça 11.
- [x] Escrito `plano-v3.md` (+ `.html` e `.pdf` por `relatorio.gravar`; o `.pdf` fica fora do git pelo `.gitignore`,
  como o da v2). O `plano-v2.md` ficou como estava (histórico).
- [x] Escrito `resumo-v3.md` (+ `.html` e `.pdf`): o PDF tem uma página (conferido abrindo a imagem da página).
- Nenhuma linha do programa nem dos testes mudou. Nenhuma janela, nenhuma pergunta do Windows, nenhum agente aberto,
  nada apagado. O esboço do porteiro foi rodado só lendo, a partir de uma cópia numa pasta temporária, contra a cópia
  `obra-juncao`.

### Como cumpri cada uma
- **D-791** → plano-v3, passo 0 (o porteiro em `tests/` e no git, sem gancho; a lista de partida contada: 43 lugares,
  cada um com o passo; as três correções do esboço); "Lista de exceções do porteiro" em cada passo; seção 6.3, ponto 1
  (os 5 de fora). Prova: a conta reproduzível com o esboço (31 achados, os mesmos da proposta) e com a busca corrigida
  (25 de K01), descrita no detalhe técnico do plano.
- **D-792, D-793** → passo 0 (o formulário sem condição; K23 passa hoje: os quatro arquivos de agente têm `tools:` sem
  a ferramenta de abrir agente, conferido com `grep`).
- **D-794** → peças 4, 6a e 11 (nova), passo 3 (leitura antes, quem quebra, prova à vista com "Não" e "Sim"), seção 4,
  seção 6.2 item 3, seção 6.3 ponto 2, seção 8 itens 8 e 10. As fontes lidas, com as linhas, estão na peça 11.
- **D-795** → peça 8, passo 2 (prova sem erro e com erro de propósito).
- **D-796** → "Regras de todos os passos", passo 0 (K13), passos 3 e 4 (arquivos nomeados).
- **D-797** → "Regras de todos os passos" ("Onde se junta"); o `master` não aparece mais no plano.
- **D-798** → "Regras de todos os passos", passo 0 (K10), passo 6. Esta entrega não traz o rótulo.
- **D-768 (aprovado)** → seção 1 e seção 6.2 (saiu a pendência).
- **Fato de 19/11** → seção 6.1, risco 1; passo 1 (a sessão A prova só o que falta).
- **X3, X6, X9, X10** → seção 6.2, item 2: apontadas, nenhuma decidida.
- **D-765** → os 5 lugares de fora não entram em passo nenhum; viraram a pergunta 1 abaixo.
- **D-605 / §11.8** → o fechar continua gravando e sem "quer salvar?" (`tests/test_salva_sozinho.py` continua como
  está: seção 6.3, "parecem não combinar"; seção 8, item 10).

## Perguntas para o Samuel (v3, no formato do CLAUDE.md §11.13)

Ressalva para a gerente: as perguntas 2, 3 e 4 pedem print (regra 3). Eu não posso abrir janela; o print sai quando o
agente do passo 3 desenhar a pergunta e o ícone, antes de construir. Sugiro levá-las juntas nessa hora. A pergunta 1
pode ir já. A pergunta 5 só vai se, na sessão B, o ícone nascer escondido. O "sim" à lista de partida das exceções vai
quando o programa do passo 0 gerar a lista (a conta de 43 é minha, lida no código).

### Pergunta 1 — os 5 lugares que o porteiro acha fora da parte do Windows
- **Do que se trata.** O porteiro é a conferência automática que barra o trabalho de um agente quando o código tem um
  erro já conhecido. Os erros desse tipo que já estão no programa vão numa lista; cada conserto tira o seu. Contei 43
  na versão de teste. 38 estão na parte do Windows, e este plano conserta cada um num passo.
- **O que acontece hoje.** Os outros 5 estão fora da parte do Windows: as duas dicas do painel Automático (ao passar o
  mouse em "desligar as marcadas" e na escolha do corte depois do Endireitar) que mostram ao Kaique um número de
  decisão; o teste de velocidade, que abre o PowerShell por conta própria para ler a placa de vídeo e o tipo de disco
  (é o teste que você roda de longe no notebook do Kaique); e a régua dos filtros, que pergunta ao Windows onde fica a
  Área de Trabalho. Não é defeito novo: as duas dicas já estão na lista de defeitos de 18/11.
- **Por que é pergunta.** Você mandou que a lista fique vazia no fim do plano, e também que nada do programa seja
  consertado antes da entrega ao Kaique, fora a parte do Windows. Para estes 5, as duas ordens não cabem juntas.
- **O que você escolhe:**
  - **A:** os 5 ficam na lista com "depois da entrega ao Kaique"; a lista só fica vazia depois. Nada muda no programa
    agora.
  - **B:** este plano conserta os 5 (é pouco: tirar o número das duas dicas e fazer os dois programas de medir pedirem
    ao Windows pelo mesmo caminho que o resto). É conserto fora da parte do Windows antes da entrega.
  - **C:** só o teste de velocidade entra no plano (ele roda no notebook do Kaique pelos testes à distância); as duas
    dicas e a régua ficam para depois da entrega.
  - **Só comentário.**
- **O que muda no que já funciona:** em A, nada; em C, só o jeito de o teste de velocidade perguntar ao Windows; em B,
  também o texto das duas dicas e o jeito de a régua perguntar. O resultado das medidas não muda.
- **Situação:** só plano. **De onde veio:** a conta que fiz no código para a lista que você confirmou em 19/11.
- Sem sugestão minha (cada saída muda uma ordem sua); a gerente põe a dela.

### Pergunta 2 — a pergunta "Atualizar agora?" ao fechar
- **Do que se trata.** Quando chega uma versão nova e o Kaique clica "Depois", você escolheu que, ao fechar o programa,
  apareça "Atualizar agora?". Sim: fecha, e o ícone perto do relógio mostra a porcentagem. Não: fecha sem trocar, e o
  aviso volta na próxima abertura.
- **O que ainda falta você dizer:**
  - **o texto e os botões.** Sugestão de agente, para a gerente levar: título "Versão nova"; texto "Há uma versão nova
    do Editor de Impressão. Atualizar agora? Leva uns 2 a 3 minutos, com o programa fechado."; botões "Sim, atualizar"
    e "Não, só fechar". Outras opções para os botões: "Atualizar agora" e "Agora não"; ou "Sim" e "Não".
  - **o X da pergunta:** A (sugestão) fecha sem trocar, igual ao "Não" (ele já tinha pedido para fechar, e o trabalho já
    foi gravado); B volta para o programa sem fechar (como o Word faz quando pergunta algo ao fechar).
- **O que já funciona e não muda:** o programa grava antes de fechar e nunca pergunta "quer salvar?"; a pergunta nova vem
  depois de gravar, e nenhuma resposta perde trabalho.
- **Situação:** decidida em 18/11 à noite, não construída. O print vai junto quando o agente desenhar. **Só comentário.**

### Pergunta 3 — o ícone perto do relógio
- **Do que se trata.** Depois do "Sim", o programa fecha e um ícone pequeno perto do relógio mostra a porcentagem da
  troca.
- **O que você escolhe:**
  - **como mostra o número:** A (sugestão) uma figura que vai enchendo no ícone, com "Atualizando o Editor de
    Impressão: 40%" quando se passa o mouse; B o número desenhado no próprio ícone (ele é muito pequeno).
  - **no fim:** A (sugestão) some sozinho; B some e o Windows mostra um aviso "Pronto" no canto (pode não aparecer, se o
    Windows estiver configurado para não mostrar avisos); C abre o programa.
  - **clicar nele:** A (sugestão) não faz nada; B abre a janelinha "Atualizando o programa, espere um pouco...".
  - **se a troca falhar:** A (sugestão) o ícone some e a frase de falha aparece na próxima abertura, como já está
    decidido; B o ícone avisa na hora.
- **De onde vem o número:** do trabalho feito de verdade (o que já foi copiado e desempacotado), nunca de um relógio. Num
  trecho que a ferramenta de atualizar faz por dentro, se não der para medir, o ícone diz "atualizando" sem número.
- **De onde veio:** pedido seu de 18/11 à noite, com o print dos ícones perto do relógio. Programas como o OneDrive e o
  Dropbox mostram o andamento assim. **Situação:** decidida, não construída. **Só comentário.**

### Pergunta 4 — dois casos que você ainda não disse
- **O Windows desligando com o programa aberto e uma versão esperando.** A (sugestão) a pergunta não aparece, conta como
  "Não", e o aviso volta na próxima abertura (uma pergunta aberta na hora de desligar faz o Windows dizer que um
  programa está impedindo o desligamento); B outra coisa que você disser.
- **Fechar sem ter clicado nem "Reiniciar agora" nem "Depois" no aviso.** A (sugestão) a pergunta aparece do mesmo jeito
  (a versão está esperando igual); B só aparece se ele clicou "Depois".
- **Situação:** não decidido; aparece na prova da sessão do atualizador. **Só comentário.**

### Pergunta 5 (só se acontecer na sessão do atualizador) — o ícone escondido atrás da setinha "^"
- **Do que se trata.** No Windows 11, o ícone de um programa novo costuma nascer escondido atrás da setinha "^" ao lado
  do relógio, e volta a esconder depois de cada atualização do programa (li num fórum da Microsoft, resposta de um
  moderador, não documentação oficial). O programa não força o ícone para fora: seria mexer por dentro numa
  configuração do Windows.
- **O que você escolhe:** A aceitar (você, na instalação no notebook, pode deixá-lo sempre à vista nas Configurações do
  Windows, se o Windows guardar a escolha); B junto com o ícone, um aviso do Windows no canto dizendo onde ver o
  andamento (coisa nova; e o Windows pode não mostrar o aviso); C a janelinha pequena da troca no lugar do ícone (muda
  o que você escolheu). **Só comentário.** Sem sugestão minha.
- **Situação:** só se confirma vendo no seu PC, na sessão do atualizador; antes disso a gerente não pergunta.
