# ONDE-PAREI — explicações com provas para a Central (17/11/2026)

Verificador. Tarefa: refazer 11 respostas que o Samuel não entendeu (9 do pedido + 2 extras: au-d-484 e
au-d-492), com prints do caso real, no modelo do girar. **Nenhuma linha do programa muda.** Nada é gravado
na Central (a gerente grava). Ramo `explicacoes-central-2026-11-17`, a partir de `obra-2026-10-26`
(`a9d81030`), worktree `.claude/worktrees/explicacoes-central`.

## Decisões que esta tarefa precisa cumprir

- **§11.13 (Samuel, 13/11/2026)** — "precisa ajeitar para isso como regra [...] para responder e fazer
  perguntas". Começar pelo que é e onde fica; sem palavra de dentro; print que prova, no modelo do girar;
  caso real conferido; caminho e se é defeito ou escolha; "O que você escolhe"; curto; controle; origem;
  situação. Depois de "Ainda não entendi": mudar o jeito, não só as palavras.
- **§10 modelo de print (Samuel, 10/11/2026)** — "o jeito como você mostrou o o girar pagina ficou muito
  bom, pode colocar ele como exemplo de como deve ser feito os prints de uma mensagem explicativa".
- **§4.10 (Samuel, 21/10/2026)** — caminho inteiro, só páginas que vão ser impressas ("não faça mais testes
  com lombadas de livros").
- **§11.12 (Samuel, 13/11/2026)** — "o agente não pode fazer gambiarras [...] funcionava de maneira
  diferente em vários lugares" (para au-d-487: procurar conta própria/desvio no botão direito da grade).
- **D-605 (03/11)** — nada novo muda o já testado (aqui: nada muda; só prints e texto).
- **Não abrir na tela dele** — janela fora da tela (-32000, PrintWindow), nunca na tela do Samuel.
- Decisões citadas nas perguntas (linhas inteiras conferidas no Livro da versão de teste):
  D-501 (o livro nunca abre no Dividir), D-500 (corte do ScanTailor na beirada não é a lombada),
  D-489 (recomeço só quando o PDF mudou), D-541 (como o Mover mexe), D-487 (grade com várias escolhidas),
  D-484 (onde cada etapa roda), D-492 (tique do menu Filtro), D-374 (nomes: "o agente não vai escolher os
  nomes ele pode sugerir opções"), D-335 ("Tirar da lista"), D-274/D-283 ("Antes de processar").

## O que já está escolhido e testado aqui

Nada é mexido: tarefa só de prints e texto. As provas que existem para cada decisão citada ficam anotadas
em cada item abaixo.

## Como fica para quem usa e no livro

Nada muda no programa nem no PDF. Os prints mostram o programa de hoje (versão de teste). Onde um print
mostra um nome novo, ele diz "SIMULAÇÃO" (texto trocado só no print, para o Samuel ver como ficaria).

## Plano

1. Ler as regras e as perguntas (feito).
2. Para cada item: conferir no Livro e no código; pilotar a janela de verdade fora da tela, com cópia do
   livro; montar as imagens no modelo do girar (`montar.py`); abrir e conferir cada imagem.
3. Escrever "Respostas para a Central" (abaixo), uma por item, e conferir contra a lista do §11.13.
4. Commit e push a cada item.

## Andamento

- [ ] au-d-501 · [ ] au-d-500 · [ ] au-d-489 · [ ] au-d-541 · [ ] au-d-487 · [ ] nm-folha-pagina ·
  [ ] nm-jeito-pb · [ ] nm-tela-livros · [ ] nm-antes-de-processar · [ ] au-d-484 · [ ] au-d-492

## Respostas para a Central

(a preencher)
