# Conferência das 7 ferramentas do Implementador B (2.4, 2.6, 2.10+1.6, 2.16, 2.17, 2.18, 2.19) — verificador, 22/10/2026 — ONDE PAREI

Código conferido: ramo `fase2-ferramentas-2026-10-22` em `f26407c` (o último código é `7d13a5f`; `f26407c` só muda o
ONDE-PAREI dele). "Antes" = `9804b98` (`git merge-base` com `fase-1`). Meu ramo: `verif-ferramentas-2026-10-22`
(sai de `f26407c`). Nunca marco aprovado: no máximo "PRONTO PARA CONFERIR".

Worktrees (com junções `modelos` e `gabarito\paginas`; **não apagar com Remove-Item -Recurse**; desfazer a junção com
`(Get-Item <junção>).Delete()`): `.claude/worktrees/vfr22-novo` (meu ramo), `.claude/worktrees/vfr22-antes` (`9804b98`).

## Pendência registrada (não é defeito)
- **b-8 "Tinta com a cor original"**: o Samuel respondeu "As duas: A e B como opções separadas" (Registro 22/10).
  **Ainda não foi feito** no ramo: só existe a A (a cor do original). Fica como pendência do implementador.

## Passos
- [x] 0. GitHub 39807401594 lido: testou `fase2-ferramentas-2026-10-22` em `7d13a5f` (o código de `f26407c` é o mesmo:
  de `7d13a5f` para `f26407c` só muda o ONDE-PAREI dele). **2177 passaram, 0 falharam, 0 erros, 73 pulados**, 124
  arquivos; botões: **234 ações, 0 falhas**. Não disparei outra rodada (o código não mudou).
- [x] 1. Testes de reversão no código antigo (`vfr22-antes`, `9804b98`; cada arquivo novo copiado para lá com outro
  nome, rodado sozinho e apagado):
  - `tests/test_cadernos.py` (o único conserto de defeito, o "último caderno menor", imp-4): **14 falham no antigo**,
    28 passam no novo. O principal falha pela substância: `test_ultimo_caderno_sai_menor_...` dá **17 páginas em branco
    no antigo** (esperado 1); `conferir_sequencia(907, 20)` diz "sobram 13 páginas em branco" no antigo. Os 11
    parametrizados falham no antigo porque `tamanhos_dos_cadernos` não existe lá (falha por falta da função, não pela conta).
  - Os arquivos novos (ferramentas que não existiam) falham todos no antigo: `test_impressao`, `test_dialogo_impressao`,
    `test_duas_camadas`, `test_editar_zonas`, `test_luz_scantailor`, `test_margens_scantailor`, `test_nucleos`,
    `test_unidades_e_perfis` (erro de importação: o módulo não existe); `test_margens_na_tela` (4 falham);
    `test_paineis` (2 falham: nome novo da caixinha e os seis "Marcar como"); `test_trilha_e_opcoes` (2 falham: a
    ferramenta nova "ajustar").
  - Ressalva: fora o último caderno, não houve conserto de defeito neste ramo; os outros testes são de ferramenta nova
    (falhar no antigo é esperado, não prova conserto).
- [ ] 2. Fotos pelo caminho inteiro, item por item (uma linha por página)
- [ ] 3. 2.6: PDF de impressão de verdade + dobra simulada
- [ ] 4. Janela de verdade (fora da tela, WM_CLOSE)
- [ ] 5. Velocidade antes x depois alternados
- [ ] 6. conferencia.json

## Perguntas para o Samuel
(nenhuma ainda)
