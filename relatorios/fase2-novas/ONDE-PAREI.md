# Onde parei: Fase 2, as 7 ferramentas que faltam (Implementador B)

Pedido da gerente em 22/10/2026. Ramo `fase2-ferramentas-2026-10-22`, criado do `origin/fase-1` em `9804b98`.
Worktree `D:\programas\EditorImpressao\.claude\worktrees\fase2-novas`, com as junções `modelos`,
`gabarito\paginas` e `gabarito\scantailor-24-09` (nunca `Remove-Item -Recurse` nelas; desfazer com
`(Get-Item <junção>).Delete()`).

Worktrees de apoio criadas por mim (só para as provas de "sai igual"; podem ser removidas pela gerente
depois de tirar as junções `modelos` e `gabarito\paginas`):
- `.claude\worktrees\fase2-novas-antes` (destacada em `9804b98`, o `fase-1` de partida);
- `.claude\worktrees\fase2-novas-prova` (destacada no commit que está sendo provado).

Regras que valem aqui: igual ao ScanTailor com os ajustes de fábrica dele, desligado de fábrica quando muda a
imagem (prova com somas iguais nas páginas-gabarito); testes seguem a ordem das etapas (dividir → endireitar →
cortar → filtro) e só com páginas que vão ser impressas; um arquivo de teste por vez no PC; suíte e velocidade
no GitHub, lidas uma vez no fim de cada item; nunca juntar ao `fase-1`; no máximo "PRONTO PARA CONFERIR".

## Os 7 itens, na ordem

| # | Item | Situação | Commits | GitHub |
|---|---|---|---|---|
| 1 | 2.4 margens iguais + alinhamento | código e tela prontos; prova de fábrica rodando | `c180af3` | (no fim) |
| 2 | 2.6 arquivo para impressão | código e tela prontos | `cac76b0` (último caderno), `f41201a` (core), `c31489c` (tela) | (no fim) |
| 3 | 2.16 todos os núcleos | código e Configurações prontos | `14a7f97` | (no fim) |
| 4 | 2.17 igualar a luz e suavizar | DLL versão 8 compilada (`5f5c2e3`); falta o módulo, a ligação e a tela | `5f5c2e3` | |
| 5 | 2.18 mudar à mão as áreas de gravura | não começado | | |
| 6 | 2.19 unidades e perfis | não começado | | |
| 7 | 2.10 + 1.6 duas camadas | não começado | | |

## Provas de "sai igual de fábrica"

Script: `relatorios/fase2-novas/scripts/rodada_processar.py` (cada página-gabarito vira um livro novo e passa
pelo `core.pipeline.processar` inteiro: dividir → endireitar → cortar → filtro; soma de cada página do PDF em
Original, Preto e branco e Melhorar). `somas_todas.sh <raiz> <saida.json>` roda as 32, uma por processo.
- Código antigo (`9804b98`): `relatorios/fase2-novas/somas-antigo-9804b98.json` — 96 somas.
- **Lição (22/10):** a prova do "novo" tem de rodar numa worktree parada no commit (`fase2-novas-prova`),
  nunca na worktree em que eu estou mexendo: mudei o `core/st_ferramentas.py` no meio de uma rodada e tive
  de jogar a rodada fora.
- O PC está com pouca memória livre (≈2 GB; o Samuel joga e outro agente mede velocidade): a rodada espera
  2,5 GB livres antes de cada página, então anda devagar.

## Escolhas de tela (para o agente de layout e o Samuel revisarem)

- **2.4:** caixinha "Margens iguais em todas as páginas" na tela "O que fazer", logo abaixo de "Cortar as
  bordas" (é opção do livro inteiro, e as opções do livro moram ali; o "Para o livro todo" do Propriedades do
  Cortar manda para lá). Marcada, mostra as quatro margens em mm (de fábrica 10/5/10/5, as do ScanTailor) e
  dois "onde a página menor fica" (de cima a baixo / de um lado ao outro: em cima, no meio, embaixo, o
  programa escolhe, onde estava na página). Desmarcada de fábrica. Provisório.
- **2.4:** aviso novo "Página bem maior que as outras" (vai para o "Para revisar" da página).
- **2.6:** botão "montar para imprimir..." na tela "Ficou pronto!", ao lado do "imprimir agora" (o lugar da
  impressão: a janela de salvar/processar). Abre a janela "Montar para imprimir" com todas as opções da janela
  do UPDF em grupos (Como vai sair · Escala de cada lado · Livreto · Várias por folha · Pôster · Outras opções ·
  Impressora) e dois botões: "gravar o arquivo para imprimir" e "mandar para a impressora". As escolhas ficam
  guardadas (como a "Última configuração" do UPDF). O botão fica apagado quando o PDF já saiu com o
  "Montar cadernos" antigo. Provisório: a aparência é do agente de layout.
- **2.6:** a exceção de "uma página só" é digitada como "12=90; 15=85" (página = %). Provisório; pede um jeito
  melhor (clicar na página na prévia?).
- **2.16:** Configurações ganhou a parte "Velocidade", com "Páginas ao mesmo tempo" (Todos os núcleos (N) · Uma
  página por vez (como antes) · 2 · 4 · 8). Provisório.

## Perguntas para o Samuel (via gerente)

1. **2.4 x explicação de 14/10:** fiz as margens iguais como o ScanTailor (na edição, para o PDF do livro),
   desligadas de fábrica, porque a ficha 2.4 e a gerente mandaram. A explicação de 14/10 diz que margem é só na
   impressão. As duas convivem (a de 2.4 deixa todas as páginas do mesmo tamanho, o que ajuda o "Ajustar" do
   livreto a dar a mesma escala em todas), mas falta ele dizer se quer as duas.
2. **2.4:** a tela de conferir não mostra as margens iguais (só o PDF tem). Mostrar na prévia?
3. **2.6:** o "Montar cadernos" antigo (folha com o dobro da largura) continua existindo ao lado da montagem nova
   em A4. Tirar o antigo, ou deixar os dois?
4. **2.6, rotação automática:** a página deitada gira no sentido anti-horário (o alto da tabela fica à
   esquerda). É o que ele quer?
5. **2.6, imprimir direto:** testei mandando para um PDF (sem papel). Na impressora de verdade não testei; e
   neste PC o Windows leva ~50 s só para "falar" com a impressora de fábrica (a EPSON ET-3750 da rede), antes de
   imprimir.

## Ressalvas até aqui

- 2.4 usa como "conteúdo" a página já cortada pelo programa (a caixa do conteúdo do ScanTailor, item 2.5, está
  no ramo `fase2-caixa-conteudo`, fora do `fase-1`). Sem "Cortar as bordas", o conteúdo é a página inteira.
- 2.4 custa uma passada a mais no livro quando ligado (só mede; o corte fica guardado para a segunda).
- 2.6 "Imprimir como imagem" de fábrica ligado (imp-6) deixa o arquivo de impressão grande (cada folha é uma
  imagem sem perda a 300 DPI) e a montagem mais lenta.
- 2.16: com pouca memória livre o programa usa 1 trabalhador (igual a antes); o ganho só aparece com memória.
- DLL versão 8: os ramos `fase2-caixa-conteudo` (4) e `fase2-scantailor-itens-2026-10-19` (5 a 7) também mudam
  a DLL; quem juntar recompila com tudo. A minha cola `luz.cpp` tem uma classe com o nome
  `output::OutputGenerator::Processor` (como a `st_gravura.cpp`); se o ramo dos itens tiver outra com o mesmo
  nome na mesma DLL, dá conflito na hora de juntar.
