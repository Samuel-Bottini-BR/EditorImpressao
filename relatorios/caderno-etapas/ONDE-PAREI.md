# ONDE PAREI — caderno segue as etapas marcadas (D-603)

Ramo `caderno-etapas-2026-11-04` (saiu de `obra-2026-10-26`, ponta `016ec37a`). Worktree
`.claude/worktrees/caderno-etapas`. Implementador, 04/11/2026.

## Decisões que esta tarefa precisa cumprir

- **D-603 (03/11):** print a-49 (etapa 1 "Dividir" marcada, etapa 7 aberta, caderno com os scans
  inteiros): "eu fui lá e apertei o botão de dividir e nos cadernos ainda aparece a folha sem
  divisão, era para ser com divisão, já que eu cliquei lá em cima, mesmo que eu não tenha processado
  ainda, pois é o preview." · pergunta: "as folhas do caderno passam a seguir todas as etapas
  marcadas (dividir, cortar, margens e as outras), igual ao "depois", mesmo antes de rodar. Num livro
  grande isso pode demorar um pouco na primeira vez, então a bolinha de carregamento aparece enquanto
  ele monta. Pode ser assim?" → "pode ser assim nos cadernos".
  04/11 (Samuel): "essa questão da folha carregar no automatico, ele só carrega a folha que está
  aparecendo né?" → sim; continua assim (só a folha à vista; nunca o livro todo na memória, §3).
- **D-605 (03/11):** "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode
  alterar o que já está escolhido e testado, coisas novas não podem criar novos problemas, essa é uma
  nova regra que todos os agentes precisam ler".
- **D-577:** a página da direita mostra o antes e depois; o "depois" é como vai sair com as etapas e
  opções marcadas, muda a cada opção; bolinha enquanto calcula; só mostra, não muda o projeto.
  "Folha ainda não dividida [...] com 'Dividir' marcado, o depois mostra as duas metades lado a lado".
- **D-574:** etapa 7 aberta → o lado direito mostra as folhas do livreto, frente e verso, "Folha N de
  M", setas; "tela cheia" abre a tela grande de caderno; no tamanho do scan; caixinha da etapa 7
  desmarcada mostra as folhas igual; abre sempre na folha 1.
- **D-589:** "Sim, se algo não está marcado, não é para fazer, certo?" — etapa desmarcada não entra.
- **D-590:** "Dividir" desmarcada no Automático não junta nada (folhas já divididas continuam
  divididas); 03/11: "Sim a caixinha continua desmacada."
- **D-064:** bolinha de carregamento ("é só colocar uma bolinha de carregamento [...]").
- **Não fazer a D-604** (números das páginas em cada lado): próxima tarefa.

## O que já está escolhido e testado aqui (D-605)

- D-574 / D-577 / D-589 / D-590 / D-064 acima, todas construídas e com provas.
- Testes que já existem e não podem quebrar (nem ser mudados):
  - `tests/test_decisoes_caderno_tela_grande.py` (11 provas da etapa 7 e da tela grande: ordem da
    dobra, folha = PDF da etapa 7, trocar páginas por caderno, tela cheia, caixinha desmarcada, só
    mostra, tela não para < 0,3 s, servidor = aqui, cancelar no servidor).
  - `tests/test_decisoes_automatico_ver_como_fica.py`, `test_decisoes_automatico_margens_no_depois.py`,
    `test_decisoes_automatico.py`, `test_decisoes_automatico_opcoes_do_filtro.py`,
    `test_decisoes_montar_cadernos.py`, `test_decisoes_juntar_todas.py`, `test_decisoes_dividir*.py`,
    `test_decisoes_livreto_ver.py`, `test_decisoes_impressao.py`, `test_cadernos.py`,
    `test_previa_composta.py`, `test_automatico_pular_depois_de_dividir.py`, `test_promessas.py`
    (p211 setas da folha do caderno), `tests/test_decisoes*.py` em geral.
- `core/automatico.folha_do_caderno(copia, pedido, folha, indices, dpi)`: a assinatura que os testes
  antigos usam continua valendo (só ganha um parâmetro opcional).

## Causa (achada 04/11)

`ui/widgets/folhas_do_caderno.FolhasDoCaderno._ativas()` pega as páginas do livro **como está**
(`projeto.paginas_ativas`, antes do pedido). Com "Dividir" marcado e o Gradus sem dividir: 70
páginas (folhas inteiras) → a conta das folhas usa 70; e cada posição recebe o "depois" da folha
inteira, que são as DUAS metades — `cadernos.paginas_lado_a_lado` as cola lado a lado, e a metade da
folha do caderno mostra a folha aberta (parece o scan inteiro, print a-49).

## Conserto (04/11)

- `core/automatico.paginas_do_pdf_depois(projeto, pedido)`: a lista das páginas do PDF depois do
  pedido, SEM desenhar. Só o Dividir muda a lista; quais folhas ele parte sai da MESMA regra da
  medida no modo automático, que só olha o tamanho da folha girada (ScanTailor: mais larga que
  alta, `ProjectPages::adviseNumberOfLogicalPages`; programa: mais larga que 1,2 x a altura). O
  tamanho vem do `page.rect` do PDF (guardado por arquivo). Faz com a lista o que o `_dividir` do
  Rodar faz (pula as folhas mexidas à mão, D-004) e o que `paginas_ativas` escolhe. Dividir
  desmarcado ou "Desligar": o livro como está (igual a antes; D-589/D-590).
- `core/automatico.folha_do_caderno(..., metades=None)`: com `metades`, cada posição recebe só a
  sua metade (antes: as duas metades coladas). A folha do scan é desenhada uma vez para as duas
  posições que saem dela, só durante a folha à vista. Sem `metades`: como antes.
- `core/paginas_em_outro_processo`: leva `metades` pelo cano (8º item; o servidor aceita 7 ou 8).
- `ui/widgets/folhas_do_caderno.FolhasDoCaderno`: a conta das folhas e as páginas de cada lado
  vêm de `_depois()` (a lista acima, guardada enquanto o pedido e o livro não mudam).
- Primeira versão rodava o `_dividir` de verdade numa cópia: 0,35 s num livro de 700 folhas (a tela
  pararia). Trocada pela conta direta (13 ms); prova de que dá o mesmo que o Rodar em
  `tests/test_caderno_segue_as_etapas.py`.

## Tempos medidos (PC, 04/11)

- Conta das páginas depois do Dividir (sem desenhar), no fio da tela:
  - Gradus Primus (70 folhas -> 140 páginas): 1ª vez 144 ms (inclui abrir a DLL do ScanTailor,
    67 ms, uma vez por sessão, e ler os tamanhos do PDF, 9 ms); depois 1 ms.
  - Livro grande (Gradus repetido 10 vezes: 700 folhas -> 1400 páginas, 108 MB): 1ª vez 75 ms
    (ler os tamanhos, 58 ms), depois 13 ms. Sem o Dividir: 0,2 ms.
- (prints: ver prints.json)

## Andamento

- [x] conserto (`35affb34`, `8bf6356a`)
- [x] teste de reversão: `tests/test_caderno_segue_as_etapas.py::test_d603_dividir_marcado_o_caderno_mostra_as_paginas_divididas`
      falha em 016ec37a ("Folha 1 de 2" no lugar de "Folha 1 de 3"), passa no novo
- [x] provas D-603 em `tests/test_decisoes_caderno_tela_grande.py` (4 novas; as 11 antigas passam)
- [ ] testes antigos no PC, um por vez (rodando)
- [ ] GitHub: conjunto 41777456037; velocidade 41777458962 (rodando)
- [ ] prints na janela de verdade
- [ ] relatório

## Perguntas para o Samuel

(nenhuma até agora)
