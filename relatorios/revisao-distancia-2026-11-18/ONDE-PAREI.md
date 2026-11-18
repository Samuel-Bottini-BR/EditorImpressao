# ONDE PAREI — revisão dos testes à distância e do pedido de licença (18/11/2026)

Cópia `.claude/worktrees/revisao-distancia`, ramo `revisao-distancia-2026-11-18` (a partir de `obra-2026-10-26`,
`b74a94e2`). Tarefa só de leitura: **nenhuma linha do programa nem dos testes mudou.**

## Situação: ENTREGUE (18/11/2026 ~12:15)
Relatório em `relatorio.md` / `.html` / `.pdf` nesta pasta. Provas em `provas/`.

## Decisões que esta tarefa precisa cumprir
- **D-767** (18/11): "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione" ·
  "quero que faça as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros na hora de montar a estrutura do
  atualizador e testes a distancias". Regra desta tarefa.
- D-705, D-711, D-712, D-716, D-717, D-721, D-722, D-725, D-728, D-731, D-733, D-735, D-736, D-739, D-741, D-743,
  D-749, D-765 (lidas inteiras no Livro).
- D-765: nenhum conserto até a entrega ao Kaique (por isso só leitura).

## Como cumpri cada uma
- D-767: o plano de prova (relatório, seção 4) é todo à vista, no programa de verdade, sem área escondida; as três provas
  desta tarefa rodaram de verdade (sem licença, sem janela, na pasta de rascunho) e não com peça de mentira.
- D-765: nada mudou no programa.
- D-722/D-731/D-741/D-749: os defeitos contra elas estão no relatório (N1, N4, 1.13).
- Regra da etapa 5 (nenhuma senha em arquivo): nenhuma senha foi usada; a prova do acento usa um texto de exemplo.
- Não abri janela na tela do Samuel, não pedi licença, não instalei nada, não toquei no OpenSSH, na conta, na regra nem
  nas pastas que a etapa 5 ligou (nem para ler). Não abri outros agentes.

## O que já está escolhido e testado aqui
Testes que cobrem esta parte (com a peça do Windows trocada por uma de mentira): `tests/test_decisoes_testes_a_distancia.py`
(13), `test_decisoes_desinstalar.py`, `test_decisoes_desinstalar_pasta.py`, `test_decisoes_preparo_d749.py`,
`test_decisoes_ajudante_da_atualizacao.py`, `test_sem_janela_na_tela.py`. Nenhum teste chama `_rodar_elevado` nem
`aplicar_no_windows` (conferido com busca). O desenho proposto não muda nenhuma decisão do Samuel; o que mudaria
comportamento virou pergunta.

## Como fica para quem usa e no livro
Nada muda agora. Com o desenho proposto: janelinha de espera durante o pedido ao Windows; frase do resultado de verdade;
a tela das Configurações mostra o que o computador tem. Nenhuma mudança nos livros nem no PDF.

## Por que os defeitos aconteceram (§11.12)
Quatro escolhas da estrutura: a tela confia na anotação; o ligar para no meio sem desfazer; o programa não lê a resposta
de quem trabalhou com licença; licenças de pasta feitas à mão com um comando que estraga os arquivos de dentro. E a peça
do Windows nunca rodou de verdade antes da etapa 5 (os testes a trocam).

## Caminhos que chegam na peça do Windows (todos passam por `aplicar_no_windows` → `_rodar_elevado`)
- primeira abertura sem senha → `atualizacao.preparar_na_primeira_abertura("")` → `ExecutorWindows.aplicar`
- primeira abertura com senha → `td.ligar` com `_ComOPreparo` → `ExecutorWindows.aplicar`
- pergunta que volta (D-741) → `preparar_na_primeira_abertura("")`
- caixinha marcada / botão "Pôr a senha" → `tdui.pedir_senha_e_ligar` → `td.ligar`
- caixinha desmarcada → `td.desligar`
- dentro da pergunta: `--preparar-o-computador` → `criar_as_tarefas` → `preparar_o_desfazer` →
  `aplicar_ja_como_administrador_no_windows` (sem pergunta)
- desinstalar → `ao_desinstalar` → `mandar_desfazer` → `rodar_a_tarefa_no_windows` (`schtasks /Run`)

## Provas desta tarefa (máquina, PC do Samuel, sem administrador)
- `provas/prova_tranca_da_pasta.sh`: com `/T` o arquivo de dentro fica com a lista de licenças vazia e o comando dá 0;
  sem `/T` fica certo. Pastas de rascunho com as licenças devolvidas no fim (`/reset`).
- `provas/prova_acento.py`: "maçã-Ação" chega ao PowerShell como "maþÒ-AþÒo".
- Leitura sem licença (comando no PowerShell, em coisas que não são nossas): serviço, conta, regra do firewall, portas e
  tarefas se leem; o "recurso instalado" pede licença.

## Sobras
Na pasta de rascunho da conversa (fora do projeto, não apagadas): `icacls-prova\` (licenças já devolvidas) e
`prova_acento.py`. Nada mais.

## Perguntas para o Samuel
As cinco do relatório, seção 5 (senha duas vezes; prova da porta pelo celular; erro no meio do ligar; a peça que vem da
internet; o nome na pergunta do Windows). Faltam os prints (janelas que ainda não existem): a gerente decide se leva com
a foto da janela de hoje.
