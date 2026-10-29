# D-582: filtro "por cima" depois do Automático — onde parei

Ramo `automatico-filtro-2026-10-29` (saiu de `obra-2026-10-26`, commit `dd13350`), worktree
`.claude/worktrees/auto-filtro`. Agente: implementador do D-582, 29/10/2026.

## Decisões que esta tarefa precisa cumprir (escrito antes de mexer)

- **D-582** (29/10/2026): "depois de rodar o automatico, quando eu tento escolher outro filtro para
  uma folha só, ele joga o filtro em cima do filtro que já tinha sido aplicado, e quando eu escolho
  outro filtro ainda, ele nem mostra a mudança em tela mesmo eu estando na opção antes e depois."
  Prova pedida: rodar o Automático → trocar o filtro de uma página duas vezes → a tela mostra cada
  filtro escolhido.
- **D-583** (29/10/2026): "Precisamos da opção de jogar o filtro em cima de outro filtro ou só
  substituir o filtro que está colocado em cima." Não construir: vira pergunta.
- **D-221** (30/09 e 29/10/2026): "eu gostaria de poder aplicar o filtro magico pro onde o
  selecionador achou." · "ou só colocar os filtros em cima das gravuras, por exemplo nesse livro eu
  gostaria de passa o magico pro em cima de todas as gravuras que ele achou muito bem, mas não dá."
  Pela metade, Fase 1.5. Não mexer.
- **D-144** (30/09/2026): "Mantém a cor original (como o ANTES); traço preto só se eu escolher" ·
  "Sim, mantém a cor - [...] o resultado do preto e branco da iluminura não está bom." (No Preto e
  branco, moldura e iluminura ficam com a cor.) Não mexer.
- **D-126/D-127/D-128** (28/09/2026): papel branco até dentro da gravura; "Iluminura sai intacta:
  cores, figuras, fundos e dourados como no original"; moldura dourada mantida sem mudar a cor nos
  filtros de cor. Não mexer.
- **D-147** (30/09/2026): "Cinza (tons de cinza): BOM" — no Preto e branco, foto e pintura saem em
  tons de cinza. Não mexer.
- **D-148** (30/09 e 05/10/2026): "Só as letras" dentro do Preto e branco (só as letras viram preto
  e branco). Não mexer.
- **D-136** (29/09/2026): o "Sim" do fundo troca só as páginas em Original. Lida: não toca aqui.
- **D-224** (01/10/2026): "espero ter a escolha de conseguir deixar a foto em original, caso
  precise." Pela metade. Não mexer.
- **D-484** (27/10/2026): "Gravuras e fotos" vale sempre para o livro todo. Não mexer.
- **D-498** (27/10/2026): lida; fala das páginas herdarem o filtro e não a marcação ao dividir ("a
  mesma regra do Automático"). Não toca aqui.
- **D-580/D-584** (29/10/2026): botão "marcações" na barra de baixo, liga sozinho nas ferramentas
  de marcar. Não mexer (os prints usam o Zoom para a página aparecer limpa).
- **CLAUDE.md §11, regra 7** ("Só o que ele mandou"): nenhum botão, aviso ou texto novo; não mexer
  no que "fica por cima".
- **CLAUDE.md §4.7** (teste de reversão em todo conserto de bug) e **§4.10** (caminho inteiro;
  cada foto diz por onde a página passou).

## A causa (em português simples, com o caso real)

O caso: livro "Na escola de Jesus", página 1 (a capa), depois do Automático (Endireitar, Cortar,
Limpar a folha, Gravuras e fotos). Cópia do projeto dele em `_tmp/dados` (nada foi escrito na
pasta de dados de teste nem no `%LOCALAPPDATA%`).

### (a) O que fica "por cima"?

**Não é um filtro por cima do outro.** Toda vez que se escolhe um filtro, o programa desenha a
página de novo, a partir do scan (do PDF), com o filtro escolhido. Prova: Preto e branco e depois
Mágico pro dá exatamente a mesma imagem que o Mágico pro escolhido direto, numa cópia que nunca
passou pelo Preto e branco
(`tests/test_decisoes_filtro_automatico.py::test_d582_o_filtro_novo_nao_vai_por_cima_do_anterior`).

**O que fica valendo de um filtro para o outro é a MARCAÇÃO que o Automático deixou na página.**
A etapa "Gravuras e fotos" do Automático marca onde estão gravura, letra e papel (as cores que
aparecem com o botão "marcações"). Com "Limpar a folha" ligado, todo filtro obedece a essa
marcação (`core/pipeline.garantir_selecao` → `core/filtros.aplicar_filtro_com_selecao`). Na capa:

- a gravura marcada cobre 82% da página; o programa achou que essa pintura colorida é um
  **"enfeite colorido"** (o mesmo tipo de moldura dourada e iluminura: muita cor forte,
  `core/filtros._e_decoracao_colorida`) — medida em `medida-filtros-com-e-sem-marcacao.txt`
  ("zona 1: 87,2% da página → DECORAÇÃO COLORIDA");
- enfeite colorido **fica com a cor do original em todos os filtros**, só com o papel em volta
  branco: no Preto e branco pela **D-144** ("Mantém a cor original (como o ANTES); traço preto só se
  eu escolher"), no Melhorar e no Mágico pro pela **D-127/D-128** ("Iluminura sai intacta: cores,
  figuras, fundos e dourados como no original"; moldura dourada sem mudar a cor);
- as áreas que o detector chamou de **papel** (parte do céu claro da pintura) vão a branco em todos
  os filtros (**D-126**: "todo o papel totalmente branco");
- a letra marcada recebe só nitidez (a mesma conta no Melhorar e no Mágico pro).

Por isso **a gravura sai colorida no Preto e branco com "Só as letras" desligado**: não é o "Só as
letras" (D-148), é a regra do enfeite colorido (D-144) valendo na pintura inteira. **É regra
decidida, não defeito de programa** — com uma ressalva: pela **D-147** ("Cinza (tons de cinza):
BOM"), foto e **pintura** deveriam sair em tons de cinza no Preto e branco. O programa não soube
separar "pintura colorida" de "iluminura" nesta capa e aplicou a regra da iluminura. Não mexi (vai
como pergunta abaixo).

### (b) Por que a tela "não muda" ao escolher outro filtro?

**A tela muda, e mostra sempre o filtro escolhido; não é defeito de tela.** Medido na cópia do
livro dele, pelo mesmo sinal do clique no cartão do painel "Filtro da página"
(`medida-tela-recebe-o-filtro.txt`): em "Uma página" e no "antes / depois", a imagem que a vista
recebe é idêntica (diferença 0,0) ao desenho do filtro escolhido, toda vez, e chega em 0,5 a 1,4 s.
O clique grava (a página passa para o filtro), a prévia é pedida de novo e o "antes / depois" pega a
prévia nova.

O que acontece é que **na capa, com a marcação do Automático, os três filtros dão quase a mesma
imagem** (`medida-filtros-com-e-sem-marcacao.txt`, diferença média em tons de 0 a 255):

| na capa | com a marcação do Automático | sem marcação nenhuma |
|---|---|---|
| Preto e branco × Melhorar | 2,2 | 69,6 |
| Preto e branco × Mágico pro | 2,2 | 68,7 |
| Melhorar × Mágico pro | 0,2 | 13,1 |
| Original × Preto e branco | 10,4 | 82,6 |

Ou seja: do Original para o Preto e branco a tela muda um pouco (o papel e o céu claro ficam
brancos); do Preto e branco para o Melhorar ou o Mágico pro a mudança é tão pequena que não se vê.
Foi isso que ele viu. Numa página de texto com gravura (página 9) acontece o mesmo entre Melhorar e
Mágico pro (0,14): com a marcação, os dois tratam gravura, letra e papel do mesmo jeito.
Foto lado a lado: `5-capa-nos-4-filtros-com-e-sem-a-marcacao.jpg`.

## O que mudou

**Nenhuma linha do programa.** Pelo item 3 do pedido ("Se (b) não for defeito do programa [...]
diga com prova e não mexa"), não houve conserto. Entraram só:

- `tests/test_decisoes_filtro_automatico.py` (4 provas do D-582: "Uma página" e "antes / depois"
  mostram cada filtro escolhido depois do Automático; o filtro novo não vai por cima do anterior;
  o Melhorar também aparece);
- esta pasta: medidas, scripts das medidas, prints e a prova de que os testes pegam uma prévia velha
  (`mutacao-previa-velha.txt`).

## Como cumpri cada uma

| Decisão | Como |
|---|---|
| D-582 | Investigado e medido; a prova pedida ("trocar o filtro duas vezes → a tela mostra cada filtro") está em `tests/test_decisoes_filtro_automatico.py` (4 passaram). Prints 1 a 4. |
| D-583 | Não construída; a pergunta está abaixo, com o que achei. |
| D-221, D-224 | Intocadas (continuam pela metade, Fase 1.5). |
| D-144, D-126, D-127, D-128, D-147, D-148 | Intocadas; explicadas na causa (a). |
| D-136, D-484, D-498 | Lidas; não tocam aqui; intocadas. |
| D-580/D-584 | Intocadas; os prints usam o Zoom (página limpa). |
| §11 regra 7 | Nenhum botão, aviso, texto ou comportamento novo. |
| §4.7 | Sem conserto não há código "antigo" e "novo"; ver Ressalvas. |
| §4.10 | Página do livro dele pelo caminho inteiro do Automático (endireitada, cortada, "Limpar a folha", "Gravuras e fotos"); cada print diz o filtro. |

## Prints (offscreen, 1280 × 657, sem abrir janela)

"Na escola de Jesus", página 1 (capa), depois do Automático do livro dele (endireitada, cortada,
"Limpar a folha", "Gravuras e fotos"), ferramenta Zoom, painel "Filtro da página" aberto,
"Só as letras" desligado:

- `1-uma-pagina-preto-e-branco.jpg` — "Uma página", Preto e branco escolhido;
- `2-uma-pagina-magico-pro.jpg` — "Uma página", Mágico pro escolhido (quase igual ao 1);
- `3-antes-depois-preto-e-branco.jpg` — "antes / depois", antes: Original × depois: Preto e branco
  (a mesma situação do print dele);
- `4-antes-depois-magico-pro.jpg` — "antes / depois", antes: Original × depois: Mágico pro;
- `5-capa-nos-4-filtros-com-e-sem-a-marcacao.jpg` — não é print da tela: a capa nos 4 filtros com
  a marcação do Automático e sem marcação nenhuma (medida fora da tela, o mesmo desenho da prévia).

Refazer: copiar o projeto para `_tmp/dados/EditorImpressao/projetos/`, apontar a "pasta" do
`resumo.json` para a cópia e rodar `fazer_prints.py` com `QT_QPA_FONTDIR=C:/Windows/Fonts`.

## Testes (um arquivo por vez, offscreen, `--basetemp` em `_tmp`)

- `tests/test_decisoes_filtro_automatico.py`: **4 passed in 7.52s**
- `tests/test_decisoes_ver.py` (o "antes / depois" e o ver; nada mudou nele, rodado só para
  conferir): **11 passed in 22.59s**
- Não rodei `test_decisoes_tela.py`, `test_decisoes_automatico.py`, os de prévia nem o
  `test_promessas.py`: nenhum arquivo do programa mudou (`git diff dd13350 --stat` só mostra
  `tests/` e `relatorios/`).

## Ressalvas

- **Sem teste de reversão (§4.7):** não houve conserto, então não existe código "antigo" e "novo".
  Os 4 testes passam no `dd13350` (é o mesmo código do programa). Para mostrar que eles pegariam um
  defeito de tela de verdade, estraguei de propósito a troca da prévia (a chave da prévia sem o
  filtro + sem o "invalidar" da página) e os 4 falharam (`mutacao-previa-velha.txt`); depois voltei
  os dois arquivos com `git checkout`.
- Nos testes, a marcação do "Gravuras e fotos" é posta direto na página (pintura como gravura,
  texto como letra), sem rodar o detector (lento e não é o assunto). O caso real foi medido no livro
  dele, fora do pytest.
- O estado da capa na hora do print dele (13:54) pode ter sido um pouco diferente da cópia que usei
  (o projeto foi mexido até as 15:36). A cópia tem a mesma situação do print: "Limpar a folha" e
  "Gravuras e fotos" ligados, 20 áreas achadas na capa, e o "antes / depois" sai igual ao dele.
- Achado à parte, **não consertado** (não é o pedido, regra 7): as figurinhas do painel "Filtro da
  página" não usam a marcação. Com o Mágico pro escolhido na capa, a figurinha do "Preto e branco"
  mostra a pintura toda em preto e branco (print 2), mas ao clicar nela a página sai colorida
  (print 1). A figurinha promete uma coisa e a página faz outra — isso também ajuda a parecer que
  "o filtro não foi aplicado". Para a Lista de bugs, se a gerente concordar (29/10/2026, prints 1
  e 2 desta pasta).

## Perguntas para o Samuel

1. **D-583 — "jogar o filtro em cima de outro filtro ou só substituir".** O que eu achei: o programa
   já **substitui** o filtro (desenha sempre do scan); o que continua "por cima" é a **marcação de
   gravura, letra e papel que o Automático fez**. Na capa, essa marcação diz "enfeite colorido" para
   a pintura inteira, e enfeite colorido fica com a cor em todos os filtros (D-144/D-127/D-128). Por
   isso os filtros parecem iguais. O que você quer quando escolhe um filtro numa página que passou
   pelo Automático?
   - **A —** o filtro vale na página toda, sem a marcação do Automático (a capa no Preto e branco
     sairia como na linha de baixo da foto 5: toda em preto e branco);
   - **B —** continua como está: o filtro respeita a marcação (enfeite fica com a cor, papel branco);
   - **C —** as duas, com uma escolha no painel "Filtro da página" (como fica na tela: perguntar).
2. **D-147 × D-144 na capa:** a pintura colorida da capa foi tratada como iluminura (fica com a
   cor). Pela D-147, pintura no Preto e branco sai em tons de cinza. Nesta capa você queria tons de
   cinza ou a cor?
3. **D-221 ("passar o mágico pro em cima de todas as gravuras que ele achou"):** hoje, com a
   marcação, o Mágico pro **não** é passado na gravura — ela recebe o tratamento suave (papel branco,
   tom guardado), igual no Melhorar e no Mágico pro; por isso os dois saem quase iguais (diferença
   0,2 na capa, 0,14 na página 9). Isso continua para a Fase 1.5, junto com a D-221?
4. **As figurinhas do painel** (achado acima): devem mostrar a página com a marcação, igual ao que
   sai ao clicar?
