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

## Andamento

- [ ] conserto
- [ ] teste de reversão (falha em 016ec37a)
- [ ] provas D-603 no arquivo de provas do caderno
- [ ] testes antigos no PC, um por vez
- [ ] GitHub
- [ ] prints na janela de verdade
- [ ] relatório

## Perguntas para o Samuel

(nenhuma até agora)
