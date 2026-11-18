# ONDE PAREI: proposta de como passar as regras aos agentes (18/11/2026)

Ramo `regras-agentes-2026-11-18` (a partir de `fase-1`, `0014e618`), cópia `.claude/worktrees/regras-agentes`.
Tarefa só de ler e escrever proposta: **nenhuma regra mudou de texto, nenhuma linha do programa nem dos testes mudou.**
Os esboços em `esbocos/` não estão ligados em nada (nem gancho, nem teste, nem commit).

## Decisões que esta tarefa precisa cumprir

- D-605 (03/11): "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está
  escolhido e testado [...]". Cumprida: nada do programa, dos testes nem das regras muda; tudo é proposta.
- D-775 (18/11): "o agente vai tentar quebrar antes de fazer o teste real na tela né?" → "ok". A proposta põe o
  formulário da entrega como material de trabalho do agente que tenta quebrar.
- D-767 (18/11): "não faça mais nada escodindo ou de mentira". A proposta pede a prova de verdade como campo obrigatório
  do formulário em trabalho de Windows.
- D-765 a D-779: lidas; entram no pacote de exemplo (a peça nova do Windows, passo 1 do plano da parte do Windows).

## O que já está escolhido e testado aqui

- O texto de todas as regras (CLAUDE.md e os 4 agentes) fica como está; a proposta só cataloga e aponta repetições e
  contradições, sem resolver.
- Nenhum teste existente é tocado. Os esboços só leem o código.

## Como fica para quem usa e no livro

Nada muda para o Kaique nem no PDF: é trabalho de organização das regras dos agentes.

## Feito

1. Lidos inteiros: CLAUDE.md (fase-1, 71.186 caracteres), os 4 arquivos de agente, memoria/INDICE.md e as fichas de
   regras (regras-de-trabalho, pc-e-github, licoes, jeito-do-samuel por cabeçalhos), D-605 e D-765 a D-779 do Livro,
   o plano da parte do Windows.
2. Catálogo em dados (`esbocos/catalogo.py`), tabela de arquivos (`esbocos/tabela_arquivos.py`), montador do pacote
   (`esbocos/montar_pacote.py`), dois esboços de conferência (`esbocos/conferir_codigo.py`,
   `esbocos/conferir_entrega.py`).
3. Proposta nos três formatos: `proposta.md`, `proposta.html`, `proposta.pdf` (gerada por
   `esbocos/montar_proposta.py` a partir de `proposta-base.md` e dos dados); pedido de exemplo em
   `pedido-exemplo.md/.html/.pdf`; `pacote-exemplo.md`.
4. Resultado: 155 regras (+9 trechos de informação); 80 em dois lugares ou mais, 28 com cópias um pouco diferentes;
   10 contradições, 6 diferenças pequenas, 4 vencidas; 23 só da gerente. Regras do pacote de exemplo: 9.189
   caracteres (hoje 93.135, até 167.069); pacote inteiro com o pedido 18.582. 24 conferências já, 14 com estudo.
5. Esboços rodados só lendo: a tabela cobre todos os arquivos do obra e do fase-1; `conferir_codigo.py` no obra acha
   31 lugares sem exceções (inclusive os defeitos 1 e 4 da etapa 5) e 15 com exceções (número de decisão em texto).

## Achado para a Lista de bugs (não impede; não consertado)

- `ui/automatico.py` 765 e 2304 (obra): dicas de tela mostram "D-068" e "D-094" ao Kaique.

## Ressalvas

- Os números de "dá para fazer já" são estimativa de leitura; só K01 a K08 têm esboço rodado.
- O catálogo é leitura minha: etiqueta e "máquina pode cobrar" são julgamento, para a gerente conferir.
- As contas de tamanho usam caracteres (len), não bytes.

## Perguntas para o Samuel

Estão no fim da proposta (seção 9), no formato do CLAUDE.md §11.13.
