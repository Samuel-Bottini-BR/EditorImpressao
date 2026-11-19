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
