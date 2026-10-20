# O Kaique: quem usa o programa, e o que isso muda

O **Kaique** é o impressor do instituto do Pe. Rosenei e o **usuário final** do Editor de Impressão.
**Sem formação técnica nenhuma.** Hoje ele limpa as páginas escaneadas no **CamScanner do celular**
(filtro Mágico Pro), e é contra isso que o programa é medido: o programa só está pronto quando
substitui o CamScanner no trabalho dele (plano §2; item [6.7](../itens/6.7.md)).

O plano manda: se algo aqui discordar do [plano](../../docs/plano/PLANO-DEFINITIVO.md), vale o plano.
Abreviações: **H** = [histórico](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)
(PARTE -N §k); **R** = [plano, Registro de mudanças](../../docs/plano/PLANO-DEFINITIVO.md).
Montado em 20/10/2026 pelo ajudante A.

---

## 1. O que ele quer, nas palavras dele

O resultado-alvo do plano (§2) é o Mágico Pro do CamScanner. Nas palavras do Kaique:

> "removeu o amarelado do fundo, manteve apenas as letras e imagens preservando suas cores originais, e
> alinhou a página que estava inclinada"

Os **quatro casos** que ele descreveu em 18/07/2026 são o critério de sucesso original (H, Apêndice B,
"PARTE 1 — O que o usuário final precisa"):

1. Folha amarelada com texto preto: "remover o amarelo e deixar as letras" (Preto e branco).
2. Livro amarelado com imagens coloridas: "tem que preservar... ele vai remover o fundo amarelo e vai
   deixar as partes coloridas, as pinturas, e ele dá até uma melhorada nas cores" (Melhorar, Mágico pro).
3. Páginas tortas (endireitar).
4. O mais difícil, a mancha do verso: "a folha é tão antiga que ela já está quase transparente, então as
   letras da parte de trás acabam aparecendo. Esses filtros no scanner, ele remove." Hoje é o item
   [6.1](../itens/6.1.md), **ainda não resolvido**.

As **fotos do CamScanner** que ele fez (Mágico Pro) estão no gabarito, em `gabarito/camscanner/`: Livro
de Horas p. 26 (NOVEMBRE) e 27 (DECEMBRE) e "Na escola de Jesus" p. 37 impressa (p. 35 do PDF) (R,
25/09/2026). São capturas da tela do celular (576×1280): servem para comparar cor, não detalhe (H,
PARTE -8 §6).

A pergunta decisiva, aberta desde 18/07/2026: **"o programa já substitui o CamScanner para o trabalho do
Kaique? Sim, não, ou ainda não."** Nunca foi respondida ([PEDIDOS.md](../../PEDIDOS.md) BLOCO 10;
hoje é o item [6.7](../itens/6.7.md)).

---

## 2. O que muda no programa por ser ele quem usa

**Sem jargão.** Ele nunca vê "Sauvola", "k" ou "deskew"; vê "Força do preto", "Melhorar", "girar a
folha". Toda a interface em português do Brasil ([CLAUDE.md](../../CLAUDE.md) §1). A especificação de
18/07 manda: nunca "imposição" (é "montar para impressão"), nunca "deskew", nunca "DPI/resolução" (é
"qualidade: normal / alta"), nunca "threshold, kernel, pipeline"; e erro sempre gentil, nunca
"FileNotFoundError" (H, Apêndice A §7).

**Nomes dos botões que ele entenda.** Na rodada 9 do layout (06/10/2026) os nomes "o nosso" e "limpar
pontinhos" foram para a rodada 10, pensando em "como o Kaique vai diferenciar qual é qual" (R,
06/10/2026). Ficaram (rodada 10, 07/10): "Limpar a sujeira" = Sem limpeza · Limpeza bruta · Limpeza
cuidadosa (leve · média · forte); "Só as letras" = Guardar a tinta forte · Guardar tudo · Guardar só o
texto (R, 07/10/2026). Outros nomes trocados pelo Samuel em 12-13/10: "deixar como veio", "usar o ângulo
do programa", "usar o corte do programa", "daqui em diante", "Editor" (R, 12/10 e 13/10/2026).

**Nada escondido.** "o Kaique escolhe um filtro só, sem mudança escondida" (Samuel, 29/09/2026, plano
item 1.1): por isso "Tirar o fundo" virou um filtro visível, e não algo automático por baixo. Toda função
automática tem botão de ligar e desligar (plano, regra 8). Quando o programa decide algo sozinho, mostra
e deixa desfazer (ex.: força do preto sozinha, com "Desfazer"; ver [para-revisar.md](../itens/para-revisar.md)).

**Ele escolhe por livro e por página.** Várias decisões do Samuel deixam a escolha com o Kaique: "O
programa sugere, o Kaique aceita" o corte da borda preta (rodada 4, 08/10; item [2.13](../itens/2.13.md));
"O Kaique escolhe por livro" entre cortar fora ou pintar de branco a tarja da biblioteca (rodada 5,
09/10; itens [2.13](../itens/2.13.md) e [2.14](../itens/2.14.md)); dividir "só quando o Kaique pedir,
livro a livro" (G2, 05/10; item [2.1](../itens/2.1.md)).

**O que ele vê e o que nunca vê.**
- Vê: os quatro filtros (e "Tirar o fundo" em livro com camadas), os medidores (Força do preto,
  Intensidade, Clareza do fundo, de 0 a 100), os avisos em laranja com botão de conserto, o "Para
  revisar", a tela "Ficou pronto!" com "Como imprimir" ([CLAUDE.md](../../CLAUDE.md) §1 e §7; H, Apêndice A).
- Nunca vê: nome de algoritmo, número técnico, rastro de erro (vai para o `erros.log`; na tela só
  "Aconteceu um problema inesperado, mas o programa continua funcionando.", [CLAUDE.md](../../CLAUDE.md) §3).
- **Defeito aberto:** as observações do livro ("o livro inteiro é colorido" etc.) vão para um rótulo
  escondido: "o Kaique não as vê" (Lista de bugs, 12/10/2026, no plano).
- **Dúvida aberta:** num livro dividido, com a página "2" na tela (folha 1), "só as pares" avisa "Você
  está numa folha ímpar": certo, "mas pode confundir o Kaique" (R, 06/10/2026; pergunta ainda não feita
  ao Samuel).

**O tamanho da tela dele.** O programa precisa caber no notebook do Kaique: 15,6", 1920 × 1080, com
escala do Windows de 125% ou 150%. A 150% a área útil é de uns **1280 × 657 pontos**; a janela tinha
altura mínima de 680 e não cabia. Em 30/09/2026 a janela passou a ter **mínimo de 1000×600**
(commit `b05fa7d`, Lista de bugs do plano, 30/09, "a conferir"). Desde então os verificadores pilotam a
janela em 1600 × 821 pixels deste PC, que é 1280 × 657 pontos (H, PARTE -10 §4). **A escala real do
notebook nunca foi conferida** ("125% ou 150%"); o Samuel, em 05/10/2026: "Isso pode ser resolvido
depois" (R, 05/10/2026). Fontes: `relatorios/conferir/fase1-1.2-tela-2026-09-30/prints-tela-1-2.md`;
[inventário de telas](../../relatorios/layout-inventario-2026-10-02/inventario-telas-e-funcoes.md) (regras de tela).

---

## 3. O notebook dele

- **Samsung Galaxy Book2: i5-1235U, 32 GB, SSD NVMe, placa de vídeo integrada Iris Xe** (plano, item
  [0.6](../itens/0.6.md)). Sem placa de vídeo dedicada: o programa tem de rodar bem assim (item
  [5.2](../itens/5.2.md)).
- **O teste de velocidade da Fase 0** foi preparado para rodar uma vez nele e no PC do Samuel; a diferença
  vira a régua (item 0.6, **`[~]`**, "o teste no notebook do Kaique fica para outro dia", R, 28/09/2026).
  O pacote é o `dist\TesteVelocidade-notebook-do-Kaique.zip` (fora do git), **que não pode ser apagado
  nem refeito**; SHA-256
  `65ef4db543e5faa6b091436f88d0542fb9484d768911d4a84f9f80a1a855dd04`, marcado como somente leitura
  (R, 28/09/2026). Junto ia um `COMO RODAR NO NOTEBOOK DO KAIQUE.txt` em `dist\` (Lista de bugs, 28/09).
- **A régua final de velocidade é o notebook dele**, "quando ele puder" ([CLAUDE.md](../../CLAUDE.md)
  §4.6, decisão de 19/10/2026). No dia a dia a régua é o PC do Samuel, por ser sempre a mesma máquina.
  A meta de tempos no notebook é o item [5.1](../itens/5.1.md).
- **Nada de treino pesado nele.** A Iris Xe não serve para treinar; tempos estimados só com o
  processador. "PP-OCR fica fora do treino no notebook." (Samuel, 29/09/2026, Lista de espera); o docTR
  na placa de vídeo do PC do Samuel "não serve ao notebook do Kaique" (Lista de espera, 29/09). A tela
  "Idiomas e modelos" prevista para a Fase 7 tem botão de **importar modelo** pensando no notebook dele
  sem internet (Lista de espera, 29/09; item [7.2](../itens/7.2.md)).

---

## 4. Como ele encaderna e imprime

- **Encadernação manual, em folhas de 4 páginas.** Palavras do Samuel na conferência 9 (05/10/2026),
  G10: "Segundo o kaique ele faz encardenações manuais então tu sabe dizer que geralmente as folhas são
  impressas com 4 paginas cada uma, entendeu? então isso ai não pode interferir nisso."
  ([conferencia-samuel-2026-10-05-g.md](../../relatorios/conferencia-samuel-2026-10-05-g.md)). Por isso
  "avisar e não reduzir" quando o conteúdo não cabe (item [2.6](../itens/2.6.md)).
- **Cadernos:** o programa monta cadernos (padrão de 20 páginas, múltiplo de 4) e confere a sequência
  simulando a dobra (H, Apêndice A §4.5; PARTE 4). A conversa de origem fala de 5 folhas A4 com 4
  páginas cada, 20 páginas por caderno ([genesis](../../historico/genesis-conversa-imposicao-cadernos.md);
  quem fala ali não está identificado). Item [6.5](../itens/6.5.md).
- **Apagar página estraga a encadernação.** Ideia do Samuel em 07/10/2026: "quando é apagada uma folha,
  tem que ser colocada uma no lugar dele né, pois se não a encadernação vai ficar errada" (Lista de
  espera, Fase 6).
- **A conversa do Samuel com o Kaique sobre a impressão (13/10/2026).** Ao responder `g10-ajustar-todas`
  o Samuel escreveu: "Mas temos que conversar sobre isso, de como a impressão final vai sair, estive hoje
  discutindo com kaique sobre isso e vou informar melhor lá no chat do claude code."
  ([conferencia-samuel-2026-10-13.md](../../relatorios/conferencia-samuel-2026-10-13.md)). No dia
  seguinte (14/10) veio a **explicação da impressão**: duas fases; na edição cada página ocupa a folha
  inteira; formato, escala e margens só na hora de gerar o arquivo para impressão (livreto em A4 deitada
  com duas A5, "como o embaralhador antigo"; A4 inteira em pé; "Quero TODAS essas opções dentro do
  programa"); margens na A5, mínimo 1 cm, costura 1 cm; "A impressora ainda come mais uns 3 mm na
  borda." Texto literal:
  [explicacao-da-impressao.md](../../relatorios/conferencia-samuel-2026-10-14/explicacao-da-impressao.md).
  Decidido depois: `g11` "1 cm a partir de onde a impressora imprime (1,3 cm do papel)"; `g12` "Em todas,
  e dá para mudar uma folha só" (R, 14/10/2026). Item [2.6](../itens/2.6.md).
- **Estado em 20/10/2026:** um pesquisador estuda a fase de impressão no ramo
  `pesquisa-impressao-2026-10-19` (`ramo pesquisa-impressao-2026-10-19: docs/pesquisa/ONDE-PAREI-impressao.md`):
  achou o embaralhador antigo (o `imposicao_cadernos.py` da conversa de origem, mesma conta do
  `core/cadernos.py`); falta pesquisar cada opção da janela de imprimir e escrever o documento.

---

## 5. As dez queixas do Kaique e onde está cada uma hoje

Fonte de requisito ([CLAUDE.md](../../CLAUDE.md) §7). As frases abaixo são as **literais dos `.txt`**
da pasta de queixas (escritos em 27/07/2026); o histórico (H, PARTE 3) e o
[PEDIDOS.md](../../PEDIDOS.md) BLOCO 9 as citam um pouco resumidas. **Nenhuma foi aprovada pelo
Samuel.** Atenção: a tabela da PARTE 3 do H diz "Feito e conferido" em várias; isso é **antigo e não
vale** (a da mancha do verso está errada, [ESTADO-ATUAL](../../docs/plano/ESTADO-ATUAL.md) §4).

| Queixa (literal) | Arquivo | Onde está hoje |
|---|---|---|
| "as letras estão ficando pixeladas, precisamos que elas fiquem mais arredondadas, mais nítidas." | `teste 4\Novo(a) Documento de Texto.txt` | sem item próprio; em agosto foi "corrigido" (raio da nitidez) sem aprovação; perto dela a Lista de espera de 30/09 ("Melhorar o contorno das letras") e a comparação final [6.7](../itens/6.7.md) |
| "Outro problema é o magico pro, está deixando muito pixelado a imagem, queremos que a imagem não fique pixelada." | `Observação do programa 1\23.txt` | idem; Mágico pro e decoração na Fase 1 ([1.5](../itens/1.5.md)); [6.7](../itens/6.7.md) |
| "Você pode ver que são prints da mesma folha só que de lados diferentes, as vezes a parte de trás fica com uma mancha da parte da frente." | `teste 3\teste 3.txt` | **não resolvida**: item [6.1](../itens/6.1.md) (mancha do verso, o defeito mais grave) |
| "o programa não localizou as bordas corretamente" | `teste 1\Novo(a) Documento de Texto.txt` | corte: itens [2.13](../itens/2.13.md) e [2.5](../itens/2.5.md) (caixa do conteúdo do ScanTailor, pronta em ramo, não ligada); conserto do corte do G6 em ramo |
| "Nessas duas paginas vemos que o livro foi já recortado ao meio, e por isso sobre dos lados uma parte branca que devia ser recortado a, queremos fica só com o conteúdo da pagina , o recortador de bordas tem que conseguir reconhecer isso." | `teste 2\Novo(a) Documento de Texto.txt` | itens [2.5](../itens/2.5.md) e [2.1](../itens/2.1.md) ("cortar a beirada da folha vizinha", opção desligada) |
| "Colocar botão clicavel nas paginas que o programa não tem certeza que estão corretas." | `Observação do programa 1\Novo(a) Documento de Texto.txt` | existe (avisos laranja); o "Para revisar" novo, com botão no próprio aviso, está em ramo: [para-revisar.md](../itens/para-revisar.md) |
| "a barra de scrool devia ser preta para ficar com visualização mais fácil" | `teste 1\problema no\scrool.txt` | feita preta em 05-06/08 e **revertida para cinza médio em 08/08**; decisão adiada pelo Samuel em 07/09 ("isso é irrelevante agora, deixe para depois."); [CLAUDE.md](../../CLAUDE.md) §9; temas do layout ([layout.md](../itens/layout.md)) |
| "Pode dar problema na sequência dos cadernos? Como ter certeza que estão todas na sequência correta sem ter que olhar folha por folha?" | `Observação do programa 1\Novo(a) Documento de Texto (2).txt` | feito em 06/08 (o programa simula a dobra e avisa "não imprima assim"); a conferir; item [6.5](../itens/6.5.md) |
| "No filtro mágico pro o fundo deveria remover o amarelado da folha e deixar totalmente branco, e preservar as cores do textos e imagens." | `teste 5\Novo(a) Documento de Texto.txt` | é o resultado-alvo do plano (§2) e as regras da Fase 1 (papel todo branco, cor original); itens [1.4](../itens/1.4.md), [1.5](../itens/1.5.md) e [6.7](../itens/6.7.md) |
| "o preto e branco não ficou tão bom nessa, a folha original está com leitura mais legível, mas o objetivo era tirar o amarelado da pagina, pois a impressora pinta esse amarelo na pagina e se colocar em preto e branco, ela pinta esse amarelo de cinza, nós queremos que fique branco a pagina e só a letras pretas." | `teste 3\preto e b\o preto e ban.txt` | parcial; tipos de preto e branco no item [2.8](../itens/2.8.md); tinta clara no [1.4](../itens/1.4.md); mancha do verso no [6.1](../itens/6.1.md) |

---

## 6. A pasta de queixas

`D:\programas\EditorImpressao-arquivos\BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros` (fora do
repositório, **somente leitura**). Listada em 20/10/2026:

| Pasta | Arquivos | Data dos arquivos |
|---|---|---|
| `teste 1\` | 2 prints (`Captura de tela 2026-07-27 145047.png`, `...145252.png`) + `Novo(a) Documento de Texto.txt` (bordas) | 27/07/2026 |
| `teste 1\problema no\` | 1 print (`...145319.png`) + `scrool.txt` (barra de rolagem) | 27/07/2026 |
| `teste 2\` | 2 prints (`...145857.png`, `...150003.png`) + `Novo(a) Documento de Texto.txt` (sobra branca) | 27/07/2026 |
| `teste 3\` | 2 prints (`...150559.png`, `...150848.png`) + `teste 3.txt` (mancha do verso) | 27/07 (txt de 29/07/2026) |
| `teste 3\preto e b\` | 2 prints (`...150953.png`, `...151305.png`) + `o preto e ban.txt` (Preto e branco) | 27/07/2026 |
| `teste 4\` | 1 print (`...155056.png`) + `Novo(a) Documento de Texto.txt` (letras pixeladas) | 27/07/2026 |
| `teste 5\` | 1 print (`...161825.png`) + `Novo(a) Documento de Texto.txt` (Mágico pro, fundo branco) | 27/07/2026 |
| `Observação do programa 1\` | 1 print (`...162747.png`) + `23.txt` (Mágico pro pixelado) + `Novo(a) Documento de Texto.txt` (botão clicável) + `Novo(a) Documento de Texto (2).txt` (sequência dos cadernos) | 27/07 (`23.txt` de 29/07/2026) |
| `observações 2\` | `observação 2.docx` e `observação 2.1.docx` (não lidos: só os `.txt` foram lidos) | 22/09/2026 |

Os `.docx` de `observações 2` são de 22/09/2026 (dia da sessão de testes ao vivo da PARTE -6 do H);
quem escreveu e o que dizem não foi conferido. Também existe `historico/arquivo-morto/kaique explica (duplicata - original em
EditorImpressao-arquivos slash soltos-area-de-trabalho).docx` (não lido).

---

## 7. O aviso que o Kaique pediu (ainda sem descrição)

Na Lista de espera do plano, 24/09/2026: "Aviso que o Kaique pediu (ainda sem descrição: o áudio enviado
não fala disso)", quem pediu: Kaique, fase "a definir". Continuou aberto nas PARTEs -11 §5 e -12 §2 do H
("sem descrição em nenhuma fonte"). **Não achei a descrição** (procurei no plano, no histórico, no
`PEDIDOS.md` e nos `.txt` da pasta de queixas). É pergunta para o Samuel.

---

## 8. O instalador que ele recebeu e o que falta testar nele

- **23/09/2026:** um `.exe` foi gerado e entregue ao Kaique a pedido do Samuel, a partir do código
  daquele dia, **com um bug conhecido dentro** (o redimensionar conteúdo); não tem a correção do recorte
  feita em seguida (H, PARTE -7 §1 e §2). Foi compactado com o WinRAR.
- **Provavelmente sem os modelos:** o instalador de 01/09 confirmadamente não levava os modelos (detector
  de gravura e letra, seleção por clique) e roda sem avisar; o de 23/09 tem o mesmo tamanho (120,5 MB) e
  "quase certamente também não tem"; o Samuel ia conferir no notebook (Lista de bugs, 25/09/2026).
- **O instalador novo (561 MB)**, com os três OCRs e o `vc_redist` oficial, **nunca foi instalado de
  verdade**: "isso entra no teste do notebook do Kaique (0.6 / 6.8)" (Samuel, R, 29/09/2026, resposta 5).
- **O que falta testar no notebook** (itens [0.6](../itens/0.6.md) e [6.8](../itens/6.8.md)):
  - o teste de velocidade da Fase 0 (o zip congelado);
  - instalar e desinstalar; o `vc_redist` rodando numa máquina sem Visual C++ (R, 29/09/2026: "Não
    testado");
  - o programa empacotado com os servidores de páginas (risco de abrir uma segunda janela; Lista de bugs,
    30/09/2026);
  - a primeira abertura do motor do Kraken depois de instalar (52 a 65 s no PC do Samuel, pelo
    antivírus; H, PARTE -9 §6);
  - usar o `EditorImpressao.exe --conferir-ocr` como verificação depois de instalar (Lista de espera,
    29/09/2026, para o 6.8);
  - a escala do Windows dele e se a janela cabe (seção 2).
  - Há uma lista pronta para isso: [conferência num computador limpo](../../relatorios/conferencia-outro-computador.md)
    ("Quem executa: o Samuel ou o Kaique").
- **Também esperando o Kaique:** a opinião dele sobre o arquivo de resultados de 30/09/2026
  (`relatorios/Editor-de-Impressao-resultados-2026-09-30.html`, fora do git, 12 MB; "não chegou", H,
  PARTE -9 §7); nesse arquivo a foto da estátua fica, "Mas precisa ser melhorado" (Samuel, 02/10/2026, O3).
