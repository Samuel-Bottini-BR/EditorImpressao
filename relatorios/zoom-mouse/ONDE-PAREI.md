# ONDE-PAREI — zoom para o mouse e nomes do "Mais ajustes" (01/11/2026)

Cópia: `.claude/worktrees/zoom-mouse`, ramo `zoom-mouse-2026-11-01` (parte de `obra-2026-10-26`, `6b4e4f9`).

## Pedido

1. Samuel, 31/10/2026: "mesmo assim, na area de trabalho o zoom se comporta sozinho, porque ele se direciona
   somente para o centro da pagina e não onde o mouse está, que é como o zoom se comporta em outros lugares no
   programa."
2. Print do Samuel (janela 1280 x 657 a 125%): no painel Filtro, "Mais ajustes", nomes cortados: "Igual"
   ("Igualar a luz da página"), "Suavi" ("Suavizar as letras"), "Tirar o chu" ("Tirar o chuvisco").

## Causa achada

1. **Zoom.** Na área de trabalho, Ctrl + roda passava por `TelaConferir._roda_na_pagina`, que chamava
   `vista.definir_zoom(vista.zoom * fator)` sem dizer onde estava o mouse: a página crescia a partir do meio.
   No "Duas lado a lado", `PaginasLadoALado.wheelEvent` chamava `definir_zoom`, que põe o par no meio da largura
   e o alto da página da vez no alto da tela. Além disso, nos dois lugares a página ficava presa no meio de lado
   enquanto era mais estreita que a tela (o limite do deslocamento da "Uma página" e a largura do que rola no lado
   a lado), então mesmo com a conta certa o zoom não iria para o mouse para os lados.
2. **Nomes cortados.** Em `_montar_aba_filtro`, as caixinhas "Igualar a luz da página", "Suavizar as letras" e o
   "Tirar o chuvisco:" com o número ficavam numa MESMA linha. O painel tem largura fixa (300 pontos); a linha
   precisava de uns 480 no Windows, e o Qt espremeu cada peça (a "Igualar..." ficou com 58 dos 180 pontos).

## O que mudou

- `ui/tela_conferir.py`
  - `_roda_na_pagina`: o Ctrl + roda chama `_zoom_no_ponteiro(vista, fator, ponto do mouse)`.
  - `_zoom_no_ponteiro` (novo): guarda em que ponto da página o mouse está, dá o zoom e põe o deslocamento que
    deixa esse ponto debaixo do mouse. Conta pelo zoom e deslocamento de agora (não pelo último desenho): várias
    voltas seguidas dão certo (D-026). Volta a 100%: no meio, como sempre.
  - `_andar_pela_pagina` passou a usar `_tamanho_da_pagina_na_tela` e `_por_o_deslocamento` (as mesmas contas de
    antes, separadas para o zoom usar também).
  - `_por_o_deslocamento`: o limite de quanto a página anda é o de antes OU o da área de rolar da janela do
    Automático (a tela vezes o zoom), o que for maior, sem o meio da página sair da tela. **Ressalva:** isso vale
    também para a roda com zoom (D-568): com Shift, a página mais estreita que a tela pode andar para os lados até
    essa conta (antes ficava presa no meio). Sem isso, rolar depois de um zoom faria a página pular de lado.
  - `_montar_aba_filtro`: "Igualar a luz da página" e "Suavizar as letras" uma por linha (como as caixinhas de
    cima); "Tirar o chuvisco:" com o número na linha dele. Nomes, controles e ações iguais.
- `ui/widgets/paginas_lado_a_lado.py`: `zoom_no_ponteiro` e `_pagina_mais_perto` (novos); o Ctrl + roda usa o
  `zoom_no_ponteiro`. `_largura_do_conteudo`: com zoom, o que rola fica pelo menos a tela vezes o zoom (até o
  dobro), com o par no meio, como a área de rolar do Automático.
- `ui/widgets/paginas_rolando.py`: `_largura_do_conteudo` (gancho; no livro aberto continua a largura da tela).
- Não mudou: os botões "–", "+", "ajustar à tela" (continuam pelo centro); a roda sem Ctrl (D-568); a roda dos
  outros lugares (D-577); o Automático (`PainelDeOpcoes` tem o "Mais ajustes" dele, montado à parte em
  `ui/automatico.py`, já uma caixinha por linha: o conserto 2 não o toca).

## Testes

- Novo: `tests/test_zoom_no_ponteiro.py` (4 casos): Ctrl + roda na Mão e no Endireitar, no lado a lado, e os nomes
  inteiros no "Mais ajustes" (com a letra Segoe UI carregada no teste: no "offscreen" o Qt mede cada letra como
  um quadrado).
- Reversão (§4.7): os 4 falham no código de `6b4e4f9` (arquivos de `ui/` trocados pelos antigos, teste novo
  mantido) — saída em `reversao-no-codigo-antigo.txt`; passam no novo.
- Arquivos que tocam zoom, roda, painel Filtro e tela cheia, um por vez, offscreen: 22 arquivos, todos passaram
  (936 casos, 1 xfail já existente), entre eles `test_decisoes_9b2` 30, `test_livro_aberto` 14, `test_luz_scantailor`
  14, `test_filtros_tela_cheia` 11, `test_paineis_na_tela` 22, `test_promessas` 262. Lista em `testes-locais.txt`.

## Prints (janela de verdade, plataforma do Windows, 1280 x 657)

- `mais-ajustes-antes.png` / `mais-ajustes-depois.png` (e `janela-mais-ajustes-*`).
- `uma-pagina-1-sem-zoom-*.png` e `uma-pagina-2-ctrl-roda-3-vezes-*.png`: a cruz vermelha é onde está o mouse.
- `lado-a-lado-1-sem-zoom-*.png` e `lado-a-lado-2-ctrl-roda-3-vezes-*.png`.

## GitHub

Rodada 41324371101 ("Testes no Windows", ramo `zoom-mouse-2026-11-01`, commit `c269e33`):
- 1ª tentativa: partes 2 a 5 e "Botões e prints da janela real" passaram; parte 1 falhou só em
  `test_promessas.py::test_p090_por_pagina_e_por_motivo` (ERROR na desmontagem: uma prévia em segundo plano
  (`ui/tarefas.py::_folha_crua`) tentou abrir o PDF do teste que já tinha sido apagado; "um botão falhou por
  baixo (erros.log)"). Não passa pelo código mexido aqui; no PC, `test_promessas` passou inteiro (262).
- 2ª tentativa (só a parte que falhou, rodada de novo uma vez): **passou**. Rodada inteira: sucesso.

## Perguntas para o Samuel

Nenhuma.

---

## Defeito de 01/11/2026: Shift + roda no "Duas lado a lado" com zoom trocava de página

Samuel, testando a junção `d6d6e6f`: "1- funcionando" · "2- funciona o zoom mas com shift para os lados não
funciona ele rola as paginas para pagina, no caso troca de pagina." · "3- ok". A escolha de a página sair um pouco
do meio (e o Shift mover página estreita) foi aprovada: "sim" (D-599).

- **Causa:** no lado a lado, a roda sem Ctrl ia para o rolar padrão do Qt (`PaginasRolando.wheelEvent` ->
  `QScrollArea`), que usa o Shift para rolar de página em página na barra de pé. Então Shift + roda descia
  páginas (no print de antes, da página 3 para a 6) em vez de andar para os lados.
- **Conserto:** `ui/widgets/paginas_lado_a_lado.py`, `PaginasLadoALado.wheelEvent`: com zoom e Shift, a roda anda
  na barra de baixo, o mesmo tanto que a roda anda para cima e para baixo (3 linhas por dente); a roda de lado
  (tilt) também. Sem zoom, e a roda sem Shift, como antes. Nada mais mudou.
- **Teste:** `tests/test_zoom_no_ponteiro.py::test_bug_01_11_shift_roda_no_lado_a_lado_com_zoom_anda_para_os_lados`.
  Falha em `a6b9e02` (arquivo antigo trocado, teste novo mantido; saída em
  `reversao-shift-no-codigo-antigo.txt`) e passa no novo.
- **Testes no PC** (offscreen, um por vez; `testes-locais-shift.txt`): 10 arquivos, todos passaram (418 casos, 1 xfail
  que já existia): test_zoom_no_ponteiro 5, test_decisoes_9b2 30, test_livro_aberto 14, test_decisoes_9b1 25,
  test_decisoes_ver 11, test_decisoes_automatico_ver_como_fica 22, test_ajustar_pedaco 13, test_dividir_scantailor 13,
  test_girar_cartoes_e_previas 23, test_promessas 262.
- **Prints:** `shift-lado-a-lado-1-com-zoom-*.png` e `shift-lado-a-lado-2-shift-roda-3-vezes-*.png` (cruz = mouse).
  Antes: as páginas descem (página 3 -> 6). Depois: o par anda para os lados, mesma altura, página 3.
- **GitHub:** rodada 41331010059 (commit `aba8c37`). 1ª tentativa: só a parte 1 falhou, no instável conhecido
  `test_promessas.py::test_p107_forca_do_preto[aviso/forca:mais_escuro-True]` ("um botão falhou por baixo"); no PC
  `test_promessas` passou inteiro. 2ª tentativa (só a parte que falhou): **passou**. Rodada inteira: sucesso.
- **Perguntas para o Samuel:** nenhuma.


---

## 02/11 — D-600: Shift + roda em todas as telas

Pedido do Samuel (02/11/2026), testando a D-599: "3- shift não funciona no automatico para mover para o lado. No duas
paginas lado a lado está funcionando" · "e no automatico pode colocar o shift tambem, o shift tem que funcionar em todas
as telas". Primeiro passo: juntado o `obra-2026-10-26` (`091b200`) neste ramo (avançou direto, sem conflito).

### Decisões que esta tarefa precisa cumprir

- **D-600** (02/11/2026): "Shift + roda move a imagem para os lados em todas as telas do programa que mostram página com
  zoom (área de trabalho, "antes e depois" do Automático e as outras), como já faz no "Duas lado a lado"."
- **D-599** (01/11/2026): "Na área de trabalho, Ctrl + roda dá zoom para onde está o mouse (Uma página e Duas lado a
  lado); a página pode sair um pouco do meio para os lados (o meio dela nunca sai da tela), e Shift + roda move para os
  lados também uma página estreita. Os botões "–", "+" e "ajustar à tela" continuam pelo centro; a roda sem Ctrl
  continua como na D-568." (na área de trabalho, fica como está)
- **D-568** (27/10/2026): "Como ficou: sem zoom troca de página; Ctrl + roda dá zoom" → roda sem zoom troca de página;
  com zoom anda pela página; Ctrl + roda dá zoom. (não muda)
- **D-577** (30/10/2026, 3º teste: "não consigo dar zoom com o mouse, usando o scrool"): no Automático a roda dá zoom.
  (não muda: só o Shift muda)
- CLAUDE.md §11 item 7 (só o que ele mandou): nada de botão, aviso ou comportamento a mais; a diferença entre telas no
  "roda sozinha × Ctrl + roda" é pergunta aberta dele e não se mexe.

### As telas com página que pode ficar maior que o espaço dela

| Tela | Arquivo e classe | Situação |
|---|---|---|
| Área de trabalho, "Uma página" (todas as ferramentas de página e a Mão/Zoom) | `ui/tela_conferir.py`, `TelaConferir._roda_na_pagina` (sobre `Visualizador` e `EditorSelecao`) | já funcionava (D-568/D-599); não mexi |
| Área de trabalho, "Uma página", ferramentas de marcar (Pincel, Varinha, Retângulo...) | `ui/widgets/editor_selecao.py`, `EditorSelecao.wheelEvent` | **pergunta 2** (abaixo); não mexi |
| Área de trabalho, "Duas lado a lado" | `ui/widgets/paginas_lado_a_lado.py`, `PaginasLadoALado.wheelEvent` | já funcionava (`aba8c37`); agora usa a peça única, o que faz não mudou |
| Área de trabalho, "antes / depois" | `ui/widgets/filtros_tela_cheia.py`, `VistaAntesDepois` | sem zoom (a página sempre inteira): não se aplica |
| Automático, "A página, antes e depois" | `ui/automatico.py`, `PaginaAntesEDepois` → `VistaAntesDepoisComZoom.wheelEvent` | **feita** |
| Automático, "tela cheia" | `ui/automatico.py`, `TelaCheiaDoAntesEDepois` → `VistaAntesDepoisComZoom` (a mesma) | **feita** |
| Automático, "comparar" da tela cheia | `ui/automatico.py`, `TelaCheiaDoAntesEDepois.vista_a/vista_b` → `Visualizador.wheelEvent` | **feita** (as duas andam juntas) |
| "Ver de perto" (e o "comparar" dele) | `ui/tela_ampliada.py`, `TelaAmpliada.vista/vista_b` → `Visualizador.wheelEvent` | **feita** |
| Filtros em tela cheia | `ui/widgets/filtros_tela_cheia.py`, `FiltrosEmTelaCheia` (`VistaAntesDepois`) | sem zoom: não se aplica |
| Livro aberto (tela de início) | `ui/tela_inicio.py`, `LivroAberto` → `ui/widgets/paginas_rolando.py`, `PaginasRolando.wheelEvent` | **feita** (só quando as páginas passam da largura, ex.: "Tamanho real"; ver a ressalva) |
| Imprimir / "Montar cadernos" | `ui/dialogo_impressao.py`, `DialogoImpressao` | não mostra página (só textos): não se aplica |
| Miniaturas e "Todas as páginas" | `ui/widgets/tira_miniaturas.py`, `ui/widgets/todas_as_paginas.py` | miniaturas, sem zoom: não se aplica |
| Folhear do PDF e a tela cheia dele | `ui/widgets/folhear_pdf.py`, `FolhearPDF`/`TelaCheiaDoPDF` | não abre em lugar nenhum hoje (a `TelaOpcoes` que o usava não é criada); usa o `Visualizador`, então ganhou o Shift junto |

### O que mudou

- **Peça única nova: `ui/widgets/roda_de_lado.py`** (a conta do conserto `aba8c37`, para nenhuma tela copiar a da outra):
  - `shift_roda_na_rolagem`: numa área de rolar, com Shift (sem Ctrl) e a barra de baixo com espaço, anda a barra de
    baixo (3 linhas por dente, como a roda anda de cima para baixo) e não deixa a roda ir para o zoom nem para o rolar
    do Qt.
  - `shift_roda_no_visualizador`: no `Visualizador`, com Shift (sem Ctrl) e zoom acima de 100%, muda o deslocamento para
    os lados (o mesmo do arrastar), avisa o "comparar". O limite de quanto anda é a conta da área de trabalho (D-599):
    a beirada para na beirada, e uma página estreita com zoom pode sair um pouco do meio (o meio dela não sai da tela).
- `ui/automatico.py`, `VistaAntesDepoisComZoom.wheelEvent`: Shift + roda passa pela peça antes do zoom.
- `ui/widgets/visualizador.py`, `Visualizador.wheelEvent`: idem (vale para o "Ver de perto" e o "comparar"). Na área de
  trabalho a roda é decidida antes, pela `TelaConferir` (nada muda lá).
- `ui/widgets/paginas_rolando.py`, `PaginasRolando.wheelEvent`: idem (livro aberto; e o "Duas lado a lado" sem zoom, se as
  páginas passarem da largura).
- `ui/widgets/paginas_lado_a_lado.py`: usa `andar_na_barra`/`quanto_de_lado` da peça (a mesma conta de antes).
- Não mudou: a roda sozinha e o Ctrl + roda de nenhuma tela; nenhum botão, aviso ou texto.

**Ressalvas (para a gerente conferir):**
1. Livro aberto: o Livro diz "telas que mostram página com zoom"; o livro aberto não tem zoom, mas no "Tamanho real" (ou
   "Caber a altura" em duas lado a lado numa janela estreita) a página passa da largura e há barra de baixo. Pus o Shift
   ali pela ordem dele, "o shift tem que funcionar em todas as telas". Antes, ali, Shift + roda descia uma tela inteira.
   Se a gerente achar que o livro aberto fica de fora, é só tirar as 3 linhas de `PaginasRolando.wheelEvent`.
2. "Ver de perto" e "comparar": com zoom, uma página ainda mais estreita que a vista também anda um pouco para os lados
   (a mesma regra que ele aprovou na área de trabalho, D-599). Sem isso, numa janela larga com página alta, o Shift + roda
   com zoom 300% caía no zoom e afastava a página (visto na 1ª versão do print `shift-ver-de-perto-2-...-depois.png`,
   que mostrava 153%; o print foi refeito depois do acerto e mostra 300%).

### Como cumpri cada uma

- **D-600**: Automático (página da direita e tela cheia), "comparar" do Automático, "Ver de perto" (e o "comparar" dele)
  e livro aberto: com zoom, Shift + roda anda para os lados, sem zoom e sem trocar de página. Prova:
  `tests/test_decisoes_shift_todas_as_telas.py` (6 casos) e os prints `shift-*-depois.png`. Área de trabalho: já
  tinha (`tests/test_zoom_no_ponteiro.py`, `tests/test_decisoes_9b2.py`).
- **D-599**: área de trabalho sem mudança (`ui/tela_conferir.py` não foi tocado; `test_zoom_no_ponteiro` e
  `test_decisoes_9b2` passam).
- **D-568** e **D-577**: a roda sozinha e o Ctrl + roda não mudaram em nenhuma tela (os testes novos conferem que a roda
  sem Shift continua dando zoom no Automático e no "Ver de perto" e descendo no livro aberto).

### Testes

- Teste de reversão (§4.7): os 6 casos novos **falham** no código de antes (`091b200`, os 4 arquivos de `ui/` trocados
  pelos antigos, teste novo mantido): no Automático e no "Ver de perto" "o Shift + roda deu zoom (2.0 -> 1.6)"; no livro
  aberto "Shift + roda para baixo não andou para a direita". Saída em `reversao-d600-no-codigo-antigo.txt`. No novo,
  passam.

### Prints (sem janela na tela, letras do Windows, 1280 x 657, "Na escola de Jesus" página 2; a cruz vermelha é o mouse)

Script: `fazer_prints_shift.py antes|depois`. Cada tela: `-1-com-zoom` e `-2-shift-roda-3-vezes`, antes e depois.
- `shift-automatico-*`: antes, o Shift + roda afastou a página até caber (zoom); depois, a página anda para a direita.
- `shift-automatico-tela-cheia-*` e `shift-automatico-comparar-*`: o mesmo (no "comparar", as duas telas juntas).
- `shift-ver-de-perto-*`: antes, zoom de 300% caiu; depois, 300% e a página andou para a direita.
- `shift-livro-aberto-*` ("Duas lado a lado", "Tamanho real"): antes, desceu uma tela (página 3 para o texto da 4);
  depois, o par anda para a direita na mesma altura.

### Perguntas para o Samuel

**Pergunta 1 — Shift + roda com a página inteira cabendo (sem zoom).** A D-600 fala das telas "com zoom". Quando a
página está inteira na tela (sem zoom), não há para onde ir de lado, e hoje o Shift + roda faz coisas diferentes em cada
tela: no Automático e no "Ver de perto" dá zoom, como a roda sozinha (print `pergunta-1-sem-zoom-antes-do-shift-roda.png`
→ `pergunta-1-sem-zoom-depois-de-1-shift-roda.png`: a página ficou menor); na área de trabalho troca de página, como a roda
sozinha (D-568); no livro aberto desce a tela. Deixei como está.
Texto para ele: "Quando a página está inteira na tela, sem zoom, o Shift + roda não tem para onde levar a página de lado.
Hoje ele faz o mesmo que a roda sozinha daquela tela: no Automático e no Ver de perto aproxima ou afasta; na área de
trabalho troca de página. Pode continuar assim? (sugestão: sim, continua assim)"

**Pergunta 2 — Shift + roda nas ferramentas de marcar da área de trabalho, com zoom.** Com o Pincel, a Varinha ou as de
marcar (Retângulo, Laço...), a roda não anda pela página: no Pincel muda o tamanho do pincel, na Varinha a tolerância
(D-568: "na ferramenta de marcar com o Pincel ou a Varinha, a roda continua mudando a espessura ou a tolerância"), nas
outras não faz nada. O Shift + roda faz o mesmo: no print `pergunta-2-pincel-com-zoom-antes-do-shift-roda.png` →
`pergunta-2-pincel-depois-de-3-shift-roda.png` (zoom 156%), a página não andou e o pincel foi de 2% para 1,5%; no Retângulo,
nada. A área de trabalho ficou como estava (D-599).
Texto para ele: "Na área de trabalho, com zoom e uma ferramenta de marcar (Pincel, Varinha, Retângulo...), o Shift + roda
hoje não leva a página para os lados: no Pincel ele muda o tamanho do pincel. Quer que o Shift + roda leve a página para
os lados também nessas ferramentas (a roda sozinha continua mudando o pincel)? (sugestão: sim)"