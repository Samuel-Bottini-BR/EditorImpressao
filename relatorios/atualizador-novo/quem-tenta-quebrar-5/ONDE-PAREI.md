# Quem tenta quebrar 5 — ONDE-PAREI

Ramo `atualizador-novo-2026-11-23`, commit conferido `0d9cac4e`. Não escrevi o código; não mudo o programa.

## Decisões que esta tarefa precisa cumprir
D-842 (nenhum item aberto; executado x lido), D-862 (a tabela contra o código), D-867 a D-876 (volta 5), e as que
continuam (D-778 (2), D-839, D-845/D-847/D-858/D-864, D-846, D-854, D-856, D-857, D-859, D-840/D-841, D-848/D-849).

## Onde estou
- [x] li regras, CLAUDE.md, Livro D-842..D-876, Fable 24/11 18:05 e 25/11 09:38, relatório do quarto, ONDE-PAREI volta 5
- [x] li o diff de atualizacao.py, fases, windows.py, velopack, main.py
- [ ] provas de verdade, mutações, testes, relatório

## INCIDENTE 25/11/2026 14:17 — uma caixa minha apareceu na tela do Samuel (culpa minha)
- O quê: a prova `provas/prova_caixa.py`, caso FUNDO, às 14:17:37. A caixa do Windows de verdade, título "Atualização",
  texto "Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do Samuel. O programa continua
  funcionando. Avise o Samuel.", botão OK. Alguém clicou OK às 14:17:41 (a minha vigia não a viu, então foi na tela dele).
- Por quê: a área de trabalho separada vale POR FIO (`SetThreadDesktop`). O processo da prova entrou nela só no fio
  principal; nesse caso a caixa vem do fio por trás do executor (um fio novo), que nasceu na área de trabalho normal
  do Windows, a da tela dele. Os outros casos (caixa no fio principal) ficaram na área separada (a vigia leu e clicou).
- Parado: nenhuma prova minha roda; nenhum processo da prova sobrou. Nada visível até a gerente responder.
- Conserto da prova (antes de rodar de novo): todo fio que pode chamar a caixa entra na área separada antes, ou a
  prova roda o processo inteiro já iniciado na área separada (`STARTUPINFO.lpDesktop`), que vale para todos os fios.
- O registro de verdade (`C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`) não mudou: 16110 bytes,
  24/11 16:38, a mesma soma antes e depois.

## Achados até aqui (antes do incidente)
- Médio, EXECUTADO, já existia antes da volta 5 (aba7b844 igual): a troca que o Windows não deixa (D-839) para a
  MESMA versão, na segunda vez, não mostra frase nenhuma (o nome "troca-<versão>" já está nos vistos). O Kaique clica
  "Reiniciar agora" de novo, a janela fecha, reabre, e nada diz que não deu. `provas/prova_casos-resultado-*.txt`, L1.
- Leve, EXECUTADO: sem área de trabalho à vista, duas frases na mesma abertura: a primeira é sobrescrita no bilhete e
  se perde (L5). Parecido com a ressalva 6 do escritor.
- Conferido e certo, EXECUTADO: a marca `.sem-volta` velha é ignorada (L2); a reprovada para nesta abertura, não é
  testada de novo, a procura volta e a correção é oferecida, e a frase dela não aparece na versão corrigida (L3); a
  reprovada depois do "Sim" ao fechar aparece uma vez na abertura seguinte (L4); M1 pelo outro caminho (L6); a caixa
  de verdade: morto com a caixa na tela, a abertura seguinte mostra de novo e depois não; o X conta como OK (vista);
  a abertura espera o OK (6 s); a frase que chega por trás aparece uma vez só e a janela não espera o OK (FUNDO).
- Testes antigos mudados: todos na lista da D-836 (`provas/testes_mudados-resultado.txt`).
- Falta: o `Update.exe` com o Velopack de verdade, as mutações, os testes um por vez, o relatório nos três formatos.
