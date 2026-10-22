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
- [ ] 2. Fotos pelo caminho inteiro, item por item (uma linha por página). Script `scripts/caminho.py` (Projeto
  novo → `analisar_projeto` → `processar`), fotos `scripts/fotos.py`, rodada `scripts/rodada1.sh`.

### 2.4 Margens iguais (olho; todas as fotos abertas). Caminho: girar (automático) → não dividiu (uma página por
folha) → endireitada → cortada (automático) → filtro Original; antes = código `9804b98`, depois = caixinha marcada
(10/5/10/5 mm, no meio). Fotos `img/24_<livro>.jpg`.
- **Graduale** (3 páginas, de 33,7/26,6/33,7 cm de largura) → as três saem 35,7 x 47,6 cm.
  - p. 221: ganha 1 cm de cada lado e 0,5 cm em cima e embaixo, branco; nada some.
  - p. 222 (a estreita; gabarito do 2.4, "aumentar a margem do lado direito"): fica no meio, com ~4,5 cm de branco de
    cada lado. A margem da direita cresce, mas a da esquerda também (alinhamento "no meio").
  - p. 223 (gabarito, "mais margem do lado esquerdo"): é a mais larga, ganha só 1 cm de cada lado; o pedido de mais
    margem à esquerda **não** é atendido pelas margens iguais (precisaria do alinhamento ou da margem da costura).
- **Horas** (4 páginas) → todas 37,3 x 51,1 cm.
  - p. 11 (frontispício): inteiro, com branco em volta.
  - p. 13 (moldura dourada): inteira, o lápis "c" no canto continua.
  - p. 14 (gabarito, "centralizar, margem muito à esquerda"): a página fica no meio da folha nova, **mas a tabela
    continua deslocada dentro dela** (mais papel de um lado que do outro), porque o "conteúdo" é a página já
    cortada, não a caixa do conteúdo do 2.5 (ressalva que o próprio implementador escreveu).
  - p. 47 (iluminura): inteira, no meio; o aviso "contas do endireitar discordam" da p. 11 é igual antes e depois.
- **Palatino** (7 páginas, 10 a 11,3 cm de largura) → todas 13,3 x 18,5 cm; p. 5, 7, 9, 10, 57 (gabarito,
  "centralizar"), 66 e 67 inteiras, cada uma no meio com branco em volta.
- **Opus Majus** (5 páginas): p. 11, 20 e 165 saem 12,8 x 20 cm; **p. 3 (folha de rosto, 14,6 x 23,5 cm) e p. 256
  (tabela dobrável) ficam fora da conta e ganham o aviso "Página bem maior que as outras"**. A tabela é o caso
  decidido (g9-pagina-muito-maior); a folha de rosto não é tabela, é só 35 % maior (o limite é 25 % acima da
  mediana) e vai ser impressa de outro tamanho. Ressalva.
- "Desligado de fábrica sai igual" (máquina): 6 páginas (graduale 222, horas 14, palatino 57, escola 7, horas 11,
  marial 7) em Preto e branco e Melhorar, antigo x novo: **12 de 12 somas iguais** (o implementador fez 96).

### 2.10 + 1.6 PDF em duas camadas (olho + máquina; 12 fotos abertas). Caminho: girar → não dividiu → endireitada →
cortada → filtro (Preto e branco, Melhorar ou Mágico pro); "uma" = caixinha desmarcada, "duas" = marcada. Um livro
de 6 páginas. Fotos `img/210_<página>_<filtro>.jpg` (inteira + pedaço ampliado a 300 DPI).
- Tamanho do arquivo: Preto e branco **29,1 → 8,1 MB**; Melhorar **51,2 → 11,9 MB**; Mágico pro **50,9 → 11,9 MB**.
  Horas 11 no Preto e branco: **24,2 → 4,2 MB** (o caso do pedido). Tempo de processar igual ou menor.
- Diferença ponto a ponto (150 DPI): média de 0 a 1,5 em 255, máximo 42; nenhum ponto com diferença acima de 40
  em nenhuma página. Página de 1 bit (Palatino 5 e Graduale 221 no Preto e branco) sai **idêntica** (0).
- Uma linha por página (as duas lado a lado, olhadas inteiras e ampliadas):
  - Horas 11 (PB e Melhorar): iluminura, título em cor e letra preta iguais; não achei diferença a olho.
  - Horas 13 (PB e Melhorar): moldura dourada, título vermelho e azul, o "c" de lápis: iguais.
  - Escola 7 (PB e Melhorar): texto, gravura colorida, endereço do blog: iguais.
  - Palatino 5 (PB idêntica; Melhorar): retrato e letras iguais a olho.
  - Graduale 221 (PB idêntica; Melhorar): linhas vermelhas, neumas, capitular: iguais.
  - Opus Majus 20 (PB e Melhorar): igual entre as duas; **nos dois a foto da estátua sai estragada** (Melhorar: manchas
    pontilhadas no fundo escuro; PB: blocos pretos e cinza liso) — é o filtro de hoje com o PDF de camadas (Fase 1.1),
    não deste item.
- Ressalva: a camada de cima vai em JPEG de qualidade 92 (perda pequena); o implementador escreveu isso. Não testei
  abrir o PDF de duas camadas em outro leitor além do PyMuPDF (Acrobat/navegador).

### 2.17 Igualar a luz, suavizar, tirar o chuvisco (olho; 19 fotos abertas). Caminho: girar → não dividiu →
endireitada → cortada → filtro (Preto e branco, Melhorar ou Original) → a opção ligada em todas as páginas. Livro
de 6 páginas. Fotos `img/217_<página>_<pb|melhorar|original>.jpg` e `img/217_escola_p035_legenda.jpg`.
- **Marial 7** — PB: "chuvisco 20" tira os pontinhos do verso em volta de "O Pref. Fr. Francisco..." (melhor) e
  engrossa a letra; igualar e suavizar quase iguais ao de hoje; a sombra cinza do canto de cima à esquerda fica em
  todos. Melhorar: igualar tira a sombra do canto e branqueia o papel (melhor), tinta um pouco mais clara; chuvisco
  20/50 quase sem diferença. Original: igualar deixa a página mais uniforme.
- **Graduale 221** — PB: igualar e chuvisco 20 afinam/tiram a faixa preta da beirada esquerda; suavizar alisa as
  bordas. Melhorar: **igualar deixa a tinta lavada** (marrom e vermelho mais claros; é o aviso que aparece);
  chuvisco 20/50 quase igual. Original: igualar quase igual.
- **Horas 47** — Melhorar: **igualar desbota o texto dourado e azul** (lavada); chuvisco sem diferença visível. PB:
  suavizar afina a letra, chuvisco 20 engrossa; iluminura igual. Original: igual.
- **Boécio 7** — PB: chuvisco 20 tira parte dos pontinhos do verso à direita dos versos, mas a letra fica mais
  grossa e manchada. Melhorar: chuvisco 20/50 engrossa e borra a letra. Original: igualar igual.
- **Escola 35** — **PB + chuvisco 20 apaga a legenda pequena "Adão e Eva expulsos do Paraíso"** (fica "A ... e Eva
  e..."; `img/217_escola_p035_legenda.jpg`). O aviso do chuvisco só aparece **acima** de 20, e o próprio aviso diz
  que "os valores que mais ajudam ficam entre 10 e 20": com 20 a letra pequena já some. **Ressalva grave.**
  Melhorar: chuvisco 50 deixa a legenda inteira. Original: igual.
- **Palatino 10** — PB: chuvisco 20 engrossa e emenda letras; suavizar quase igual. Melhorar: chuvisco 20/50
  engrossa e borra. Original: igual.
- "Suavizar as letras" no Melhorar não foi testado (é só do Preto e branco, como no ScanTailor).

### 2.18 Áreas mudadas à mão (olho; 5 fotos abertas). Caminho: girar → não dividiu → endireitada → cortada →
Preto e branco → a marcação que o programa acha sozinho (a mesma da tela) → a área à mão por cima → processar.
Script `scripts/zonas218.py`. Fotos `img/218_*.jpg`.
- **Horas 13** (`218_horas_p013.jpg`): título como "Tinta com a cor original, papel branco" → TABLE e CONTENU
  vermelhos, DE CE QUI EST azul, papel branco (certo); "Tinta preta, fundo original" → letra preta com o creme do papel
  dentro do retângulo (certo, como pedido); "Pintar por cima" (branco) no canto de cima → o "c" de lápis some.
- **Escola 7** (`218_escola_p007.jpg`): endereço do blog com "Pintar por cima" branco → some; com a cor cinza
  #c0c0c0 → um retângulo cinza no lugar (a cor escolhida vale).
- **Marial 7** (`218_marial_p007_mancha.jpg`): a área que a máquina achou na mancha (a "gravura" do canto de cima) —
  **apagada** → a mancha cinza sai, sobra o risco preto da beirada do scanner; **pintada de branco (o botão)** → a
  mancha sai igual; um retângulo à mão "Pintar por cima" no mesmo lugar → sai também o começo das linhas que estão
  dentro dele (é o retângulo; esperado).
- **Achado (suspeita, no código, não na tela):** se a pessoa apagar **todas** as áreas achadas de uma página, a
  marcação fica vazia e, ao processar, o programa **acha tudo de novo** (`core/pipeline.py` ~linha 1205: "se a
  marcação guardada está vazia, detectar"). No Marial 7, apagando as 15 áreas, o PDF saiu igual ao de hoje, com a
  mancha (`218_marial_p007.jpg`). Apagar uma área só (sobrando outras) funciona. O código antigo faz o mesmo (não é
  deste ramo), mas toca a decisão P11b ("apagar"). Ressalva.
- Teste ruim meu (descartado, fica a foto `218_marial_p007_maior_branca.jpg`): pintei de branco a MAIOR área achada,
  que é uma "letra" do tamanho da página; ela vira "papel" e as outras letras por cima continuam: nada muda.
- Contas de mover / mudar o tamanho / copiar (máquina, `trabalho/2.18/contas.json`): mover (0,1; 0,05) anda certo;
  mudar o tamanho dá exatamente a caixa pedida; a cópia sai 3 % ao lado; a área original não muda.
- **Pendência b-8 (não é defeito):** "Tinta com a cor original" saiu só como a opção A (cor do original); a B
  (escurecida), que o Samuel pediu como opção separada, **ainda não foi feita**.

### 2.16 Todos os núcleos + velocidade (máquina). Livro: Marial 11 a 33 (23 páginas), Preto e branco, pelo caminho
inteiro; antes (`9804b98`) e depois alternados, um processo por vez, duas vezes cada. Este PC está com pouca memória
livre (0,6 a 3 GB; outros programas abertos), e **de fábrica o programa novo escolhe 1 trabalhador aqui** (corta pela
memória: 900 MB por trabalhador + 1,5 GB de reserva). Para ver o ganho forcei 3 trabalhadores.
| | abrir (análise) | processar |
|---|---|---|
| antes, vez 1 / 2 | 7,9 / 7,8 s | 89,4 / 102,2 s |
| novo com 1 trabalhador (o que este PC escolhe), vez 1 / 2 | 7,8 / 7,5 s | 96,3 / 97,6 s |
| novo com 3 trabalhadores, vez 1 / 2 | 4,9 / 5,2 s | 58,2 / 59,0 s |
- **O PDF sai idêntico** (somas de todas as 23 páginas iguais) no antes, no novo com 1 e no novo com 3.
- Com 1 trabalhador fica igual ao antes (dentro do vai-e-vem: 89 a 102 s). Com 3, ~40 % mais rápido, como o filtro
  do GitHub achou (39787700625 e 39791117352: "parece mais rápido").
- Ressalva: no PC do Samuel com pouca memória livre o ganho não aparece (o programa cai para 1, igual a antes). A
  medida que vale para a fase é a da gerente.

- Observação (2.4): as margens são branco puro; no filtro Original o papel creme fica com uma moldura branca em volta
  (como o ScanTailor faz).
- [x] 3. 2.6: PDF de impressão de verdade + dobra simulada (máquina + olho). Livro: **Marial, páginas 11 a 33 do PDF
  (23 páginas de miolo, sem capa)**, pelo caminho inteiro (girar → não dividiu → endireitada → cortada → Original) e
  depois `core.impressao.montar_para_impressao` (o mesmo do botão "gravar o arquivo para imprimir"). A dobra é
  conferida **sem o código do programa** (`scripts/impressao26.py conferir`): cada metade de cada lado é reconhecida
  comparando com as páginas do livro, e as folhas de cada caderno são empilhadas e dobradas na conta (frente e verso
  virando na borda curta). Fotos `img/26_*.jpg` (cada metade com o número achado em vermelho), todas abertas.
  - **Livreto A4 de fábrica**: 6 folhas, cadernos de 20 + 4 (o último menor, imp-4); leitura depois de dobrar
    **1, 2, ..., 23 e 1 branca no fim**: certa. Margens medidas: ≥ 12,7 mm do lado de fora (pedido 13), ≥ 9,5 mm na
    costura (pedido 10), 16,5 a 17 mm em cima e embaixo (a medida é a 0,6 mm por ponto). A página 20 (mais estreita)
    fica no meio da metade dela.
  - **Esquerda 90 % + página 5 com 80 %**: dobra certa; as páginas da esquerda menores, a página 5 menor ainda, as da
    direita do tamanho de fábrica (exceção vale para uma página só, imp-1).
  - **Cadernos de 8**: 3 cadernos (8, 8, 8), dobra certa, 1 branca.
  - **Sem as margens**: mesma ordem das folhas do de fábrica (conferido lado a lado, `img/26_sem_margens_x_fabrica.jpg`);
    a minha conta de reconhecer erra 3 páginas porque, sem margem, a página encosta na dobra — não é defeito do programa.
  - **Página inteira A4 em pé**: 23 páginas na ordem, 12 folhas.
  - **"Montar cadernos no tamanho do scan" (o de sempre)**: código novo **certo, 2 cadernos (20 + 4), 1 branca**;
    código antigo: **20 lados, 17 páginas em branco** (3 folhas e meia vazias) — é o defeito consertado. A minha conta
    acusa "errada" no antigo só porque calcula o último caderno do jeito novo; olhando a foto, a ordem antiga também
    dobra certo (`img/26_cadernos_tamanho_do_scan_antes.jpg`).
  - **Escala personalizada 120 %** (`img/26_livreto_escala120.jpg`): é 120 % do **tamanho real** do scan (Marial tem
    24 x 33 cm), então cada metade A5 mostra só um pedaço do meio da página, e o resto é cortado. O programa avisa em
    todas as páginas ("a margem ficou abaixo de 1 cm - em cima -9,3 cm ..."). É o defeito já na Lista de bugs
    (22/10, "Imprimir com escala acima de 100% corta..."). Para "aumentar" depois do Ajustar (imp-2) o caminho é a
    escala de cada lado; o nome "Escala personalizada" não diz que é sobre o tamanho real. Ressalva de tela.
  - Imprimir direto: **não testado na impressora de verdade** (o Samuel disse que testa na conferência).
- [ ] 4. Janela de verdade (fora da tela, WM_CLOSE)
- [ ] 5. Velocidade antes x depois alternados
- [ ] 6. conferencia.json

## Perguntas para o Samuel

### P1 (2.17, 22/10 16h) — "Tirar o chuvisco" no Preto e branco apaga letra miúda antes do aviso aparecer
O que acontece: você decidiu "Tirar o chuvisco" de 0 a 100, com aviso **acima de 20** (o aviso diz "os valores que
mais ajudam ficam entre 10 e 20"). No Preto e branco, a legenda pequena embaixo da gravura do Escola 35 ("Adão e Eva
expulsos do Paraíso", letra de ~1,5 mm) já começa a falhar com **10** e fica ilegível com **15 e 20** — sem aviso
nenhum. No Boécio 7, com 10, o chuvisco do verso sai e a letra fica boa; com 20 a letra engrossa.
Fotos: `img/217_pergunta_chuvisco_q.jpg` (Escola 35: 0, 10, 15, 20, legenda ampliada) e
`img/217_pergunta_chuvisco_qb.jpg` (Boécio 7: 0, 10, 15, 20). Caminho: girar → não dividiu → endireitada → cortada
→ Preto e branco → Tirar o chuvisco N.
- **A — Deixar como está** (aviso só acima de 20). Bom: nada muda. Ruim: com 10 a 20 a letra miúda pode sumir sem aviso.
- **B — No Preto e branco, avisar desde o primeiro número** ("pode apagar letra muito pequena; confira as legendas").
  Bom: quem liga sabe do risco. Ruim: o aviso aparece sempre que a opção é usada no Preto e branco. *(sugestão do verificador)*
- **C — No Preto e branco, aviso a partir de 10** (e 20 no Melhorar/Mágico pro/Original). Bom: avisa onde começou a
  estragar nestas páginas. Ruim: o número 10 vem de duas páginas só.
