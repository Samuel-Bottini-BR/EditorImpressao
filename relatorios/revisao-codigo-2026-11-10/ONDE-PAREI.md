# ONDE-PAREI — revisão do código (10/11/2026)

Ramo: `revisao-codigo-2026-11-10` (saiu do `obra-2026-10-26`, commit `bc766007`). Worktree: `.claude/worktrees/revisao-codigo`.
Só documentos: nenhuma linha do programa nem dos testes mudou.

## O que o Samuel pediu

Em 10/11/2026, depois de ver que o "Girar" faz coisas diferentes conforme a opção (Gradus, Dividir com "Duas lado a lado", folha 10: "todas as folhas" gira página por página, "só as pares" gira a folha inteira):
"se mudou a ferramenta, muda em todos os lugares." · "Isso me faz parecer que você está fazendo gambiarra no codigo" · "Eu não quero remendos nesse código, gambiarras, pode botar um agente para revisar o codigo e achar coisas parecidas, eu quero as praticas de um programador senior na hora de codar".
A gerente pediu: revisar `ui/` e `core/`, achar remendos parecidos, e propor "Regras de código para os agentes". Sem mudar o programa e sem propor comportamento novo (CLAUDE.md §11.7).

## Decisões que esta tarefa precisa cumprir

- D-667 / CLAUDE.md §11.10: "se mudou a ferramenta, muda em todos os lugares." A regra da ferramenta num lugar só do código.
- §11.7, "Só o que ele mandou": a revisão fala de como o código está feito; o que parece contra uma decisão vira pergunta.
- D-605 / §11.8: nada muda no que já está escolhido e testado (aqui, nada muda: é só leitura).

## Andamento

- [x] Ramo e worktree criados a partir do `obra-2026-10-26` (o worktree `obra-juncao` não foi tocado).
- [x] Lidos: `ui/tela_conferir.py`, `ui/janela_principal.py`, `ui/tarefas.py`, `ui/tela_ampliada.py`, `ui/desfazer_nesta_pagina.py`, `core/pipeline.py`, `core/filtros.py`, `core/automatico.py`, `core/etapas.py`, `core/girar.py`, `core/dividir_a_mao.py`, `core/perfis.py`, `modelos.py`.
- [x] Uma prova por script, sem janela, com prioridade baixa e `LOCALAPPDATA` à parte (`prova/juntar.py`, achado A4). Não rodei a suíte.
- [x] Relatório nos três formatos: `relatorio.md`, `relatorio-completo.html`, `relatorio.pdf` (o PDF fica fora do git).
- [x] Proposta de "Regras de código para os agentes" (10 regras), no fim do relatório. O `CLAUDE.md` não foi mudado.
- Os três ajudantes que abri no começo foram parados pela gerente (regra: no máximo dois agentes ao mesmo tempo). Fiz a revisão inteira sozinho; eles não deixaram nada escrito.

## O que achei

17 achados: 4 de gravidade alta, 9 média, 4 baixa. Detalhes, linhas e exemplos em `relatorio.md`.

Alta (já sai diferente para quem usa):
- A1. O Girar tem sete caminhos, um por decisão (o caso do Gradus, folha 10).
- A2. As figurinhas do Filtro e o "comparar" da tela grande usam uma conta mais simples que a da página (a gravura aparece como mancha preta na figurinha e sai guardada na página).
- A3. "Usar em todas" quer dizer uma coisa em cada ferramenta; no Marcar ele apaga a gravura marcada à mão das outras páginas.
- A4. O Automático e o "não dividir esta" deixam a folha inteira de dois jeitos (o contador passa a dizer "1 apagadas" sem ninguém ter tirado nada). Provado por script.

Média: M1 seis caminhos para gravar no Histórico · M2 "como sai no PDF" escrito três vezes · M3 a prévia lê o livro ao vivo (conserto de 09/11 tratou o sintoma) · M4 trocar o motor de corte numa folha dividida mede sem pintar a tampa · M5 o "dividir" da grade ignora a linha arrastada · M6 a página girada sozinha não chegou a todos os lugares · M7 a página em branco posta à mão conferida em 31 lugares · M8 erros engolidos que mudam o PDF · M9 a lista dos campos do filtro escrita em seis lugares, e já diverge.

Baixa: B1 bandeira dentro do texto da chave · B2 tela de conferir com 10.041 linhas e estado espalhado · B3 duas perguntas "mexida à mão?" · B4 erros escondidos na janela principal.

## Perguntas para o Samuel

1. O "usar em todas" do Marcar, do Filtro, do Endireitar e do Girar também deveria deixar de fora as páginas mexidas à mão, como o Cortar, o Dividir e o Mover (D-090)? Sugestão: sim.
2. "Letra clara em fundo escuro" deve ir junto no "todas" do painel Filtro, como já vai pelo Automático? Sugestão: sim.
3. O "dividir" da grade "Todas as páginas" deve cortar na linha que você arrastou, como o "dividir esta" (D-609)? Sugestão: sim.
4. O girar da grade "Todas as páginas" deve deixar todas viradas como a página da vez, como o painel (D-035)? Sem sugestão.
