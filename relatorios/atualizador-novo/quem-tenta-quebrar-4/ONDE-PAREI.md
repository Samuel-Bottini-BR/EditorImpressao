# Quem tenta quebrar 4 do atualizador novo: onde parei (24/11/2026)

Verificador (quem tenta quebrar 4). Ramo `atualizador-novo-2026-11-23`, commit `5dfcdc9d` (GitHub verde, rodada
45520421089, que testou exatamente esse commit: conferido no registro da rodada). Não escrevi o código e não o conserto.
Não abri agente nem janela na tela do Samuel; nada em `C:\ProgramData\EditorImpressao`, em `%LOCALAPPDATA%\EditorImpressao`
nem na instalação dele (o PROGRAMDATA e o LOCALAPPDATA trocados DENTRO do Python em toda prova, conferidos com `assert`
antes de rodar).

## Decisões que esta tarefa precisa cumprir

D-719, D-767 ("não faça mais nada escodindo ou de mentira"), D-775 (outro agente tenta quebrar antes da prova à vista),
D-778 (as três frases), D-811/D-827 (proteção sem teste nunca é "baixo"), D-812, D-813, D-830, D-834 a D-866 (as do
atualizador novo; as da volta 4: D-855 a D-864), D-842 ("pequeno" é só o que o Kaique nunca veria; o relatório separa o
executado do lido). Deixados para depois pelo Samuel (não contam como abertos): M1 (D-861), D-865 e os quatro da D-866.

## O que já está escolhido e testado aqui

As decisões acima e os testes do atualizador (15 arquivos) e as provas das decisões (`tests/test_decisoes*.py`, 64
arquivos). Não mudo nada disso: só rodo, um arquivo por vez.

## Como fica para quem usa (o que eu confiro)

O que o Kaique vê em cada casinha da tabela da volta 4 (`relatorios/atualizador-novo/ONDE-PAREI.md`, "Volta 4 — a
tabela das falhas") e se o disco fica como ela diz. No livro (PDF): nada muda nesta entrega.

## Andamento

- [x] Li tudo o que o pedido mandou ler (verificador.md, CLAUDE.md, memória, ONDE-PAREI da volta 4 e 3, o Fable, o
  relatório 3, as decisões).
- [x] Provas executadas (`provas/`): janela que não abre, frase velha, Update.exe que some, pacote esperando sem
  internet, volta sem janela (vpk + Update.exe de verdade), casinhas, guarda morta no meio, GitHub 404 de verdade.
- [x] Mutações numa cópia (`provas/mutacoes_qtq4.py`).
- [x] Testes um arquivo por vez (`saida_teste/qtq4/testes-resultado.txt`, copiado para `provas/`).
- [x] Relatório nos três formatos; commit só desta pasta.

## Perguntas para o Samuel

Vão no relatório (seção "O que precisa da palavra do Samuel"); a gerente leva à Central.
