# ONDE-PAREI — conserto C dos quadrados brancos (D-668), agente de conserto, 10/11/2026

Ramo `quadrados-c-2026-11-10` (a partir de `obra-2026-10-26`, `58806f81`), cópia em
`D:\programas\EditorImpressao\.claude\worktrees\quadrados-c`. Tudo sem janela (`QT_QPA_PLATFORM=offscreen`),
dados num `LOCALAPPDATA` à parte, acervo só lido.

## Decisões que esta tarefa precisa cumprir

- **D-668** (10/11, Central `quadrados-qual`: "Roxo: o conserto C (recomendo)"; chat: "c"): Melhorar e Mágico pro
  voltam a proteger as pinturas: com "Respeitar as gravuras achadas" marcada, procuram a gravura como o Preto e branco
  (D-659) e não pintam de branco dentro dela; a limpeza do papel só pinta de branco onde em volta também é papel (vale
  também com "Respeitar" desmarcada, print 10). Conserta o "i" e o "t" finos. Pela D-667, uma regra só nos três filtros.
- **D-667** (10/11): "se mudou a ferramenta, muda em todos os lugares."
- **D-659** (09/11): "ele vai procurar só naquela pagina se eu optar para que ele faça aquele ajuste em varias paginas
  ai sim o programa vai ler as outras paginas" (só as páginas onde a opção vale). Testada: "fiz os dois testes que você
  pediu e estão funcionando."
- **D-661** (09/11, "1- pode"): "Pular" deixa a página feita à mão como ele deixou, com a gravura achada.
- **D-586 / D-583** (29/10): caixinha "Respeitar as gravuras achadas", ligada de fábrica; desligada, o filtro não usa o
  que a máquina achou.
- **D-473**: a mesma conta na tela, na prévia, nas miniaturas e no PDF.
- **D-605 / CLAUDE.md §11.8**: o novo não estraga o testado; nunca mudar teste antigo para passar.
- **CLAUDE.md §9**: não desfazer a correção do "magic color".
- Pedido da gerente: não mudar o que sai no Original nem nas páginas que já têm gravura marcada à mão.

## O que já está escolhido e testado aqui

- `core/etapas.py` (`respeitar_procura`, `procura_por_dentro`, `marca_sozinho`): D-659, D-661, D-589, P4.
  Provas: `tests/test_decisoes_gravura_a_mao.py`, `tests/test_decisoes_gravura_pular.py`,
  `tests/test_decisoes_respeitar_gravuras.py`, `tests/test_decisoes_gravuras_cinza.py`, `tests/test_decisoes_so_as_letras.py`.
- `core/pipeline.py` (`garantir_selecao`, `marcacao_que_o_filtro_usa`): D-586/D-587/D-588.
- `core/filtros.py` (`_limpar_o_papel_de_verdade`): mancha do verso, "fundo meio amarelado", grão do pergaminho
  (lista 4.12), papel de dentro da gravura (bug 202, `tests/test_papel_dentro_da_gravura.py`).

## Andamento

- [x] worktree e ramo
- [x] código: uma lista só (`core.filtros.FILTROS_QUE_RESPEITAM_AS_GRAVURAS`) para a procura e para a caixinha
      desmarcada; a quarta pergunta da limpeza (`_em_volta_e_papel`)
- [x] conferido: página 13 sai IGUAL ponto por ponto à simulação C (prévia e PDF, Melhorar com "Respeitar" e Mágico
      pro sem "Respeitar")
- [ ] teste de reversão
- [ ] medidas antes/depois (gabarito, livro inteiro, Horas 47, Boécio)
- [ ] testes no PC, GitHub, velocidade
- [ ] prints e relatório
