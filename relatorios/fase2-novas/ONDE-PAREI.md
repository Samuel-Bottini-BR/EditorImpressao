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

## Os 7 itens, na ordem (estado em 22/10/2026, fim do trabalho)

Todos **PRONTO PARA CONFERIR** (falta verificador e Samuel). Relatório da entrega (três formatos):
`relatorios/fase2-novas/conferencia/entrega-2026-10-22.*`. Antes/depois (fora do git):
`relatorios/conferir/fase2-novas/<item>/`.

| # | Item | Commits | Prova / GitHub |
|---|---|---|---|
| 1 | 2.4 margens iguais + alinhamento | `c180af3` | 96/96 somas iguais (`c31489c`) |
| 2 | 2.6 arquivo para impressão (+ último caderno menor) | `cac76b0`, `f41201a`, `c31489c`, `4990e13` | 96/96; reversão do último caderno: 14 falham no antigo |
| 3 | 2.16 todos os núcleos | `14a7f97` | PDF igual com 1 e 4 trabalhadores (teste) |
| 4 | 2.17 igualar a luz e suavizar | `5f5c2e3` (DLL v8), `fa269d9` | 96/96 (`c9f3335`) |
| 5 | 2.18 mudar à mão as áreas | `bfad304`, `578c1a5`, `d652248` | 96/96 (`c9f3335`) |
| 6 | 2.19 unidades e receitas | `2d0a850` | 96/96 (`c9f3335`) |
| 7 | 2.10 + 1.6 duas camadas | `c9f3335` | 96/96 (`c9f3335`) |

GitHub: suíte `39787683890` (`fa269d9`) 2150/0, botões 222/0; suíte `39791078658` (`4990e13`) 2171 passaram, 2
falharam (trilha antiga com 9 ferramentas, consertado em `d652248`); suíte `39794419960` (`d652248`) e velocidade
`39787700625` (`9804b98`→`fa269d9`), `39791117352` (`9804b98`→`4990e13`): ver a entrega à gerente.

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

## Escolhas de tela feitas depois

- **2.17:** linha na aba Filtro (bloco AJUSTE): "Igualar a luz da página", "Suavizar as letras" (só no Preto e
  branco) e "Tirar o chuvisco: [0-100]". "Todas"/"daqui em diante" levam os três.
- **2.18:** ferramenta nova "Mover e mudar o tamanho da área" (tecla A) na trilha, depois de "Pegar pela cor";
  linha "Área:" embaixo da página na ferramenta de marcar ("Mostrar as áreas achadas", apagar a área, pintar de
  branco, copiar, colar); "Marcar como" com seis tipos e o botão "cor de pintar".
- **2.19:** linha "Receita:" no alto da tela "O que fazer"; em Configurações "Medidas em" e "Receita de todo livro novo".
- **2.10/1.6:** caixinha "Gravar em duas camadas..." na janela "Confirmar e processar".
- **2.6:** parte "Impressão" em Configurações (margem 10 mm e o que a impressora não imprime, 3 mm).

## Perguntas novas (do olho nos antes/depois)

6. **2.17:** igualar a luz antes do Melhorar/Mágico pro deixa a tinta lavada (Graduale 221, Horas 47). Deixar o
   "igualar" só no Preto e branco e no Original?
7. **2.17:** "tirar o chuvisco" acima de ~20 borra a letra. Limitar a escala?
8. **2.18:** a "tinta com a cor" numa página em Preto e branco deixa a letra cinza (a cor do original). É isso?
