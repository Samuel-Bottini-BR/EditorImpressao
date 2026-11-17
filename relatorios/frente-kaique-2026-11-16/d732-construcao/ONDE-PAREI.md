# ONDE-PAREI: construção da D-732 a D-736 (17/11/2026)

Ramo `desinstalar-tudo-2026-11-16`, cópia `.claude/worktrees/desinstalar-tudo`. Base: commit 997a3085.

**Divisão mudada pela gerente (17/11):** este agente faz só os itens 1 a 4 (D-732, D-733, B1, D-734, D-735,
D-736). O item 5 (D-731, desinstalar) e o 6 (B2, B3, B4) ficam com outro agente. Não mexer em `ao_desinstalar`
nem nos passos de ligar/desligar/desfazer de `core/testes_a_distancia.py` e `core/_testes_a_distancia_windows.py`.
Nada desses itens tinha sido mexido quando a ordem chegou.

## Decisões que esta tarefa precisa cumprir
- D-732: "não, faz quando o programa é aberto" — procurar ao abrir, não ao ligar o computador.
- D-733: jeito 1 (alternativa B): pergunta do Windows na primeira abertura cria o ajudante (tarefa como o sistema)
  e faz o Visual C++, tirar o Inno e a senha se houver; depois, nenhuma pergunta por atualização nem na volta.
- D-734: com "Depois", entra na próxima vez que o Kaique abrir, com uma espera curta antes da janela; fechar não troca.
- D-735: a pergunta do Windows aparece sempre, com ou sem senha.
- D-736: aberto por teste à distância, não procura; o Samuel manda atualizar de longe pelo mesmo ajudante.
- Continuam: D-714 (publicada de propósito), D-715/D-720 (aviso), D-718/D-719 (volta e frase), D-724 (assinatura),
  D-727 (Visual C++ dentro), D-728 (pelo código nada liga).

## O que já está escolhido e testado aqui
- `tests/test_decisoes_atualizacao.py` (todas), `tests/test_decisoes_testes_a_distancia.py` (todas),
  `tests/test_assinatura.py`, `tests/test_promessas.py` P-215.
- Testes antigos que a decisão nova vai quebrar (não mudar; listar): ver o relatório.

## Como fica para quem usa e no livro
- Primeira abertura: janela da senha (como hoje); depois, com senha ou "Agora não", UMA pergunta do Windows.
- Aberturas seguintes: nada aparece; a versão nova é procurada por trás.
- Versão nova com o programa aberto: o aviso de sempre; "Reiniciar agora" fecha gravando, e o programa volta
  sozinho na versão nova, sem pergunta do Windows. "Depois": entra na próxima abertura (espera curta, sem janela).
- O PDF e os livros: nada muda.

## Regra num lugar só (caminho → função)
- ver relatorio.md (tabela "Caminho → função").

## Estado (17/11)
- [x] código: commits 73dc4122 (atualizacao.py, main.py), f3e05a1d (ui), d92ba757 (provas)
- [x] testes novos: tests/test_decisoes_ajudante_da_atualizacao.py, 23 de 23
- [x] reversão: as 23 falham no código de antes (cópia em D:\agente_temp_testes\d732-codigo-antigo, criada por mim;
      fora do projeto, não apaguei)
- [x] rodadas: atualizacao 35+3 (os 3 esperados), testes_a_distancia 13, assinatura 16, promessas 215: 1
- [x] ensaio da etapa 3: "ENSAIO: CERTO" (saída em D:\agente_temp_testes\d732-ensaio.txt)
- [x] pedido extra da gerente: fonte de teste da etapa 5 (commit f82a6139; 4 provas test_etapa5_*)
- [x] relatório nos três formatos; entregue à gerente como PRONTO PARA CONFERIR
