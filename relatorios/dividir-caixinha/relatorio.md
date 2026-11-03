# D-590: a caixinha do "Dividir" desmarcada fica desmarcada

Ramo `dividir-caixinha-2026-11-03` (saiu de `obra-2026-10-26` em `8846017`). Implementador, 03/11/2026.

## O que foi feito

Agora, com "1 Dividir folhas ao meio" desmarcada e Rodar, **as folhas continuam divididas e a caixinha fica
desmarcada** (no painel, na janela grande aberta de novo e depois de fechar e reabrir o trabalho); a etapa fica
"desligada" e a frase de baixo não fala mais em dividir. Marcar de novo e rodar divide e a etapa volta "ligada no
livro todo". O Ctrl+Z traz de volta.

**Por que acontecia:** o "Rodar" desliga as etapas desmarcadas (D-589), mas o Dividir ficava de fora de propósito
(com medo de juntar as folhas). Então o livro continuava com o Dividir "ligado no livro todo", e o painel, ao reler
o livro depois do Rodar, marcava a caixinha de novo.

**O conserto:** o Rodar desliga também o Dividir desmarcado, mas **só a caixinha do livro** (`dividir_folhas`);
nenhuma folha é tocada. Junto, um cuidado necessário: com o Dividir desligado e só "Montar cadernos", o programa
usava um atalho que monta os cadernos com as folhas cruas do PDF, e isso **juntaria as folhas** nos cadernos
(medido: 2 folhas de 1152 pt no lugar de 4 de 576 pt). O atalho agora não vale quando há página que é metade de
folha dividida.

## Arquivos alterados

- `core/automatico.py`: `DESLIGAM_DESMARCADAS` (agora com o DIVIDIR) e os docstrings de
  `_desligar_as_desmarcadas` e de `Pedido.desmarcadas`. **Não toquei** em `_dividir`, `paginas_mexidas` nem no uso
  de `pular` (o trecho do outro agente).
- `modelos.py`: `Projeto.so_cadernos` (uma condição a mais) e a função nova `_tem_metade_de_folha_dividida`.
- `tests/test_dividir_desmarcada_caixinha.py` (novo, 3 testes).
- `relatorios/dividir-caixinha/`: ONDE-PAREI, este relatório, `olhar_etapas.py` (script dos prints e do olhar),
  `olhar_etapas-saida.txt` e os prints.

## Prints (janela real, offscreen, pasta de dados isolada em `_tmp/dividir-caixinha-dados`)

- `1-painel-depois-de-rodar-dividir-desmarcado.png`: o painel depois do Rodar.
- `2-janela-reaberta-dividir-desmarcado.png`: a janela grande aberta de novo: "1 Dividir · desligada", caixinha
  vazia, frase "Vou deixar a página em Original (sem filtro), no livro todo (6 páginas)."
- `3-trabalho-reaberto-janela-dividir.png`: o trabalho fechado e reaberto: igual, 6 páginas.
- `4-`, `5-`, `6-olhar-*-desmarcada-reaberta.png`: o olhar das etapas 2, 3 e 4 (abaixo).

## Achados para o Samuel (só olhados, **sem conserto**: regra "Só o que ele mandou")

Medido pela janela grande (script `olhar_etapas.py`, saída em `olhar_etapas-saida.txt`):

1. **"2 Endireitar", "3 Cortar as bordas" e "4 Limpar a folha" têm o mesmo defeito que o Dividir tinha.** Ligadas
   numa rodada, desmarcadas na janela grande e Rodar → a caixinha **volta marcada**, a etapa continua "ligada no
   livro todo" e a frase de baixo diz "Vou endireitar…" / "Vou cortar as bordas…" / "Vou limpar em Preto e
   branco…". **E a etapa continua valendo**: o campo do livro que o PDF lê (`endireitar`, `cortar_bordas`,
   `limpar`; `core/etapas.endireita_sozinho` / `corta_sozinho` / `limpa_sozinho`) fica ligado, então o livro sai
   endireitado, cortado e limpo mesmo com a caixinha desmarcada. Prints `4-olhar-endireitar-…`,
   `5-olhar-cortar-…`, `6-olhar-limpar-…`. No código está escrito de propósito: "Endireitar, Cortar e Limpar
   desmarcados ficam como estão (ainda a perguntar)" (`core/automatico.DESLIGAM_DESMARCADAS`). Pela D-589 ("se
   algo não está marcado, não é para fazer") pareceria que elas devem desligar também; **falta a decisão dele**
   (pergunta abaixo).
2. **"5 Gravuras e fotos" marcada sozinha e Rodar → a caixinha volta DESMARCADA.** É o contrário: num livro sem
   "Limpar a folha" ligada, marcar só a etapa 5 e rodar faz a caixinha desmarcar sozinha, porque o programa só conta
   a etapa 5 como ligada quando o "Limpar a folha" também está (`core/automatico.ligada_no_livro`). Visto no
   script ("SO GRAVURAS marcada e Rodar -> marcadas depois: []").
3. **"Limpar a folha" liga a "Gravuras e fotos" junto (anotado em 01/11):** pela janela, com a etapa 5
   desmarcada, **não se reproduziu** nesta versão: o desligar da D-589 a desliga no mesmo Rodar ("SO LIMPAR
   marcada e Rodar -> marcadas depois: ['limpar']"). A ligação continua no código (`ligada_no_livro`: a etapa 5
   conta como ligada sempre que "Limpar" está ligada e o "Procurar" do livro está ligado, e o "Procurar" vem ligado
   de fábrica). Por outro caminho que não leve as desmarcadas (ex.: um pedido montado fora da janela) ela ainda
   apareceria ligada.
4. As outras (1 Dividir, 6 Margens, 7 Cadernos), marcadas sozinhas e rodadas, ficam só elas marcadas: nenhuma
   ligou sozinha.

## Perguntas para o Samuel

- **P1 (achado 1).** "Quando você desmarca 'Endireitar', 'Cortar as bordas' ou 'Limpar a folha' e roda, hoje a
  caixinha volta marcada e o livro continua saindo endireitado, cortado ou limpo. Sugestão: a caixinha fica
  desmarcada e a etapa deixa de ser feita no livro todo (como já é com Cadernos, Margens e Gravuras). As páginas que
  você mexeu à mão continuam como você deixou. Pode ser assim?"
- **P2 (achado 2).** "Marcar só 'Gravuras e fotos' (sem 'Limpar a folha') e rodar faz a caixinha voltar
  desmarcada. Sugestão: ela fica marcada como você deixou. Pode ser?" (Observação técnica para a gerente: a
  procura das gravuras só muda a página quando há filtro; sem "Limpar a folha", marcar a etapa 5 hoje não muda o
  PDF.)

## Ideias / bugs

- Bug para a Lista de bugs (não impede): na janela grande, a linha **selecionada** com a caixinha desmarcada
  mostra a caixinha como um quadrado preto cheio (ver o "4 Limpar a folha" no print `4-olhar-endireitar-…`), que
  pode ser lido como "marcada". Já era assim antes; não mexi.
