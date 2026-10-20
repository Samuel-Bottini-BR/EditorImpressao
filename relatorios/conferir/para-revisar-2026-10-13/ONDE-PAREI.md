# Segunda conferência do "Para revisar": onde parei

## Retomada de 20/10/2026 (verificador, a pedido da gerente) - TERMINADA

Velocidade: NÃO medida (Mágico pro +1,1% foi para a Fase 5, Samuel 19/10). Tudo no `ce2b835`, pasta `trabalho/dados_teste3`.

- [x] 1. As 19 imagens abertas uma a uma (todas batem); e as 66 citadas nos quadros, contra as decisões.
- [x] 2. As 4 páginas reabertas na janela (`scripts/r3_quatro_paginas.py`):
      - Opus Majus 20: o parecer de 13/10 estava ERRADO. No PDF a foto sai destruída (`r3_processar_opus.py`,
        `img/a4-opus-20.jpg`); o aviso "Figura além da gravura" está certo. Igual no fase-1 (`r3_render_raiz.py`).
      - Cursus 3 (pedaço 1-10; o livro inteiro parou 2 vezes com MemoryError), Antiphon 260 (pedaço 256-264),
        Camões 66: confirmam o parecer.
- [x] 3. Teclado: explicado pelo código (a seta só chega à janela se a tira/medidor não a usarem; no medidor, muda a força).
- [x] 4. Aba 4: `conferencia-aba4.json` (+ .md/.html/.pdf), montado por `scripts/aba4.py` (+ `aba4_reabertos.py`,
      `a4_recortes.py`). NÃO PUBLICAR antes de juntar o fase-1 no ramo (conflito em ui/tela_conferir.py e
      ui/widgets/paineis.py) e refazer as fotos: 25 de 40 são da tela antiga; 3 desatualizadas (quadro "está bom").
- [x] 5. Parecer nos três formatos: `conferencia.md/.html/.pdf` (`scripts/vistas_20_10.py` + `scripts/terceira.py`).

Próximo (quando a gerente mandar): conferir o conserto do Pesel 21; depois, o item 2.8.

## Os 8 pontos na janela de verdade: todos conferidos

Pasta de dados nova (`trabalho/dados_teste2`), mouse e teclado nativos, 1280 x 657. `erros.log` de teste vazio em todas as sessões.

| Ponto | Resultado | Imagem (`img/`) |
|---|---|---|
| 1. A medida não depende mais da prévia | **Vale.** Graduale 221 sem aviso. As 89 páginas na ordem da janela: 22 vão, 75 certas, nenhuma diferente da conta direta (antes: 24 e 73). Resultado em `conferir-89-como-a-janela.json` | `janela-diferente-1-graduale-221-recorte.jpg` |
| 2. Dois cliques no cartão | **Vale.** Abre o "Ver de perto", não grava ação, o aviso continua | `duplo-clique-1-aviso-continua-recorte.jpg` |
| 3. "está bom assim" (3º botão) | **Vale** no Egenloff 12, na Gladstone 18 e no Rariora 8; Ctrl+Z desfaz | `sem-conteudo-1-egenloff-recorte.jpg`, `parece-em-branco-1-recorte.jpg`, `sem-conteudo-5-rariora-recorte.jpg` |
| 4. Teclado | **Em parte.** Os botões do aviso não ficam com o foco; a barra de espaço faz "está certo e avança"; Tab não chega neles. A seta não troca de página na janela de teste, e dá igual no programa de hoje (`scripts/q2_setas.py`): não dá para confirmar a seta. Não conferi com a janela ativa (não tomo o teclado do Samuel) | `teclado-1-recorte.jpg` |
| 5. Frase da lista | **Vale:** "Ainda tem 75 páginas que eu não tive certeza (104 avisos na lista)" (Camões) | `antes-3-lista-camoes.jpg` |
| 6. "usar mais escuro" | **Vale:** no Egenloff 3 com a força em 85 o botão não aparece | `forca-7-egenloff-3-forca-85-recorte.jpg` |
| 7. Força sozinha, mais cautelosa | **Vale.** Camões 27 e 104: age (85, "Desfazer"). Palatino 66, Egenloff 3 e Camões 11: só o aviso "Texto falhado", força 50 | `forca-1-camoes-recorte.jpg`, `palatino-66-2-aviso-recorte.jpg`, `forca-4-egenloff-3-recorte.jpg` |
| 8. Aba Marcar se acerta sozinha | **Acontece:** Graduale 221, 9 áreas viram 18 em 10,7 s. O retângulo marcado à mão no intervalo (página 5) continuou lá | `marcar-1-antes-e-depois.jpg`, `marcar-4-a-mao-recorte.jpg` |

Também conferido no programa novo: processar até "Ficou pronto!" (8 s, PDF com 6 páginas) e abrir um projeto gravado
na primeira conferência (abre em 6 s, as áreas da aba Marcar ficam como estavam).

## O `conferencia.json`: completo para os 8 pontos e as três perguntas

Montado por `scripts/segunda.py` (em cima do `montar_conferencia.py` da primeira). Estado de agora:

- 18 quadros (os 15 `pr-…` de antes, atualizados, mais `pr-marcar-sozinha`, `pr-duplo-clique`, `pr-teclado`), todos com `imgs`.
- **As três perguntas estão escritas:** `pergunta_medir` (tempos atualizados), `pergunta_contagens` (Camões: painel 39,
  lista 75 páginas e 104 avisos, janela de salvar 106) e `pergunta_tela_igual_ao_pdf`. Cada uma com a sugestão marcada como minha e "Ainda não entendi".
- `conferencia.md`, `.html` e `.pdf` gravados com `relatorio.gravar`.
- **Falta no JSON e no relatório:** a tabela do layout (não medido) e a frase do veredito sobre a velocidade (ver abaixo).

## Velocidade: o que existe e o que falta

`teste_velocidade.py`, Marial de 300 folhas, uma rodada por vez. Rodadas em `velocidade/rodadas-2/`.

| Braço | Rodadas feitas | Onde |
|---|---|---|
| 1. `fase-1` de hoje (94f71bd, worktree `velocidade-antes-pr`) | **2** (15:35 e 16:00) | `rodadas-2/antes-1`, `antes-2` |
| 2. "Para revisar" (ce2b835, esta worktree) | **2** (15:48 e 16:11) | `rodadas-2/depois-1`, `depois-2` |
| 3. Layout juntado ao `fase-1` (`origin/juntar-layout3-2026-10-13`, f35bcaf) | **nenhuma** | a worktree `velocidade-layout` **não foi criada** |

Resultado dos braços 1 e 2 (está no relatório): abrir, trocar de página e Preto e branco, não dá para dizer.
**Mágico pro, 10 páginas: 54,6 s contra 55,2 s, +0,6 s (+1,1%), com vai-e-vem de 0,5 s e os dois pares para o mesmo lado
(+0,6 e +0,7): pela minha conta sai "mais lento", por pouco.** Na primeira conferência os dois pares também tinham saído para
o mesmo lado (+0,4 e +0,1). São 0,06 s por página. A gerente decide se conta.

Folhear com "Só as letras" na janela (Antiphonal, 12 páginas parando 1,5 s e 12 sem parar; `velocidade/folhear/*.json`,
2 rodadas de cada): trocar de página não ficou mais lento; **o trabalho por trás depois de parar passou de 8 a 9 s para 44 a 47 s.**

**Falta medir:** o braço do layout. Como pediu a gerente (ordem 1, 2, 3, 1, 2, 3; layout com prioridade), o plano era
rodar agora `fase-1`, layout, `fase-1`, layout, alternando, para o layout ter o seu "antes" na mesma hora, e gravar
`velocidade/velocidade-layout.md`. Passos:

1. `git -C D:\programas\EditorImpressao worktree add --detach .claude/worktrees/velocidade-layout origin/juntar-layout3-2026-10-13`
   e a junção `modelos` (`New-Item -ItemType Junction`).
2. Em `velocidade/rodar_uma.ps1`: acrescentar `layout` ao `ValidateSet` e ao `$copias`, e trocar `rodadas-2` por `rodadas-3`.
3. Rodar `antes-3`, `layout-1`, `antes-4`, `layout-2`; juntar com a mesma conta do `montar_conferencia.velocidade()`.

## O que mais falta

- Abrir as imagens novas que ainda não abri uma a uma: `duplo-clique-1`, `duplo-clique-2-ver-de-perto`, `teclado-1`,
  `teclado-2`, `forca-1`, `forca-2`, `forca-4`, `sem-conteudo-1`, `sem-conteudo-2`, `sem-conteudo-5`, `janela-diferente-1` e `-2`,
  `marcar-2`, `marcar-3`, `palatino-66-3`, `parece-em-branco-2`, `contagens-2`, `contagens-3`, `bug-duplo-clique-tira-o-aviso-tela`.
  Todas passaram na conferência por máquina de print velho (`scripts/achar_prints_velhos.py`) e o estado de cada tela foi lido na hora do print.
- Não reabri na segunda conferência: Opus Majus 20, Antiphon 260, Cursus 3 e Camões 66 (não eram dos consertos).

## Como retomar

- `python scripts/segunda.py` (com a pasta de trabalho na raiz da worktree) refaz o `conferencia.json` e o relatório; não mede nada.
- `scripts/v.py` pilota a janela; `v.fechar()` fecha primeiro o "Ver de perto" que ficar aberto.
- A pasta `trabalho/` (prints brutos, pastas de dados de teste, pedaços de PDF) está no disco, fora do git.
- Worktrees que criei: `verif-para-revisar` (junções `modelos`, `gabarito\paginas`, `gabarito\scantailor-24-09`) e
  `velocidade-antes-pr` (junção `modelos`). Para desfazer, primeiro as junções, com `(Get-Item …).Delete()`.
