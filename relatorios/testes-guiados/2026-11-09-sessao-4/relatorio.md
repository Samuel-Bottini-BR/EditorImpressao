# Teste do Samuel, 09/11/2026 (sessão 4)

Versão testada: a versão de teste (`obra-2026-10-26`), livro de 199 páginas (alexandriacatolica), página 8.

## 1. Preto e branco na área de trabalho estraga a gravura (15h56)

Print: `prints/01-manual-pb-gravura-estragada.png` (painel "Filtro da página", Preto e branco, "Respeitar as gravuras
achadas" e "Gravuras em tons de cinza" ligados; a gravura sai em manchas pretas).
Print: `prints/02-automatico-pb-gravura-certa.png` (janela do Automático, mesma página, mesmas opções: a gravura sai em
tons de cinza, certa).

Palavras dele: "acabei de achar um problema no filtro preto e branco, todas aquelas mudanças que a gente tinha feito no
na questão de respeitar gravura e tudo mais no manual não está funcionando, isso é um grande erro, porque aconteceu?
porque o gerente, mas como pode ver no automatico está funcionando normalmente, só ficou meio confuso essa questão do
respeitar gavura, e só as letras fazem a mesma coisa?"

Investigação da gerente (09/11, só leitura do código da versão de teste `obra-2026-10-26`):

- Causa: `core/etapas.py`, `marca_sozinho`. A procura de gravuras só roda com "Limpar a folha" ligado (o Automático
  do filtro, no livro ou na página). Com o filtro escolhido à mão num livro que nunca passou pelo Automático
  ("Livro novo: ainda não passou pelo automático", no print 1), a função para logo na primeira linha
  (`if not limpa_sozinho(...): return False`), antes da "procura por dentro" que a caixinha "Gravuras em tons de
  cinza" (P4, 02/11: "o cinza procura as figuras por conta própria") e o "Só as letras" precisam. Resultado: nenhuma
  gravura achada, as duas caixinhas não têm o que respeitar, e a página inteira vira preto e branco.
- No Automático funciona porque lá "Limpar a folha" está ligado.
- Por que passou: as 17 provas de `tests/test_decisoes_gravuras_cinza.py` começam todas depois do Automático
  (`_depois_do_automatico`). Nenhuma testa o livro novo com o filtro escolhido à mão. O pedido ao agente do conserto
  de 02/11 também não citava esse caso.
- Pelo Livro: D-583 diz "**Depois do Automático**, o filtro escolhido numa página pode respeitar a marcação". Ou seja,
  "Respeitar as gravuras achadas" sozinha, sem Automático, não tem o que respeitar (é o combinado). Já "Gravuras em
  tons de cinza" ligada deveria achar as gravuras sozinha (P4): isso é defeito.

## 2. Mais testes (16h01 a 16h05)

Prints: `prints/03-endireitar-girar-duas-lado-a-lado.png` (Endireitar, "Duas lado a lado", páginas 8 e 9) e
`prints/04-quadro-ja-feito-no-livro-todo.png` (quadro "JÁ FEITO NO LIVRO TODO" do Propriedades).

Palavras dele (respondendo "1" à pergunta 1 da investigação acima, e depois):
"- o girar está funcionando, mas gostaria de poder selecionar duas paginas e girar as duas ao mesmo tempo.
- eu não mexi em nada no automatico e fica esse aviso ai do lado, para que serve? eu pedi isso?
- as vezes quando eu mudo de ferramenta ele tira o zoom que eu tinha dado, por exemplo quando eu vou de uma ferramenta
  para outra, principalmente quando eu vou para o cortar bordas.
- pagina em branco funciona"

Destino:
- Girar uma página (D-618): **funciona** (testado pelo Samuel em 09/11).
- Página em branco pelo botão direito (D-623): **funciona** (testado pelo Samuel em 09/11).
- Girar duas páginas escolhidas ao mesmo tempo: na grade "ver todas" já existe (D-487, "Na grade, com várias páginas
  escolhidas: girar ¼ para os dois lados"); na área de trabalho, não. Pergunta ao Samuel se quer também ali.
- Quadro "JÁ FEITO NO LIVRO TODO": vem da D-051 (12/10, ele escolheu "B — Propriedades com duas partes: 'Só nesta
  página' e 'Para o livro todo'") e da D-619 (04/11: o quadro só mostra o que vale para o livro todo, com o botão
  "mudar no Automático..."). Explicado no chat.
- Zoom que some ao trocar de ferramenta (principalmente ao ir para o Cortar as bordas): defeito novo, para a Lista de bugs.

## Respostas às 2 perguntas da gravura à mão (chat, 09/11, à noite)

Palavras dele: "1- sim / 2-  não entendi"

Destino:
- Pergunta 1 ("Posso trocar um teste antigo e consertar um defeito que apareceu no caminho?"): **sim**. O agente
  aplica a troca do `test_p195` e a mudança em `ui/tarefas.py` e roda os testes de novo. Anotado na Central
  (respostas/gravura-a-mao-testes).
- Pergunta 2 (o Automático depois do Preto e branco à mão): **não entendi**. A gerente explicou no chat com o caso
  da página 8 e pediu ao agente as provas (página 8 à mão; depois do Automático sem "Gravuras e fotos"; o mesmo
  com "Gravuras em tons de cinza"). A pergunta volta na Central com as provas.
