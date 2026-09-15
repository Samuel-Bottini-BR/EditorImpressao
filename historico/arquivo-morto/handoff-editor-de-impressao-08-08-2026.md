# Editor de Impressão — Handoff

Escrito em 08/08/2026. Consolida tudo que foi discutido sobre o projeto: o que o programa é, todas as funcionalidades pedidas, o estado de cada uma, os defeitos abertos, as decisões tomadas e as regras de trabalho. Serve para retomar o assunto do zero, em qualquer conversa nova.

---

## 1. O que é o programa, e para quem

Aplicativo de Windows que recupera PDFs de livros antigos escaneados e os prepara para reimpressão em cadernos. Projeto do Instituto São Bento, instituto católico de preservação de livros esgotados, do Pe. Rosenei.

**Quem usa é o Kaique**, impressor, sem formação técnica. Ele nunca vê "Sauvola", "k" ou "deskew" — vê "Força do preto", "Melhorar", "girar a folha". Substitui o fluxo atual dele, feito no CamScanner pelo celular.

**Duas versões anteriores fracassaram**: uma travava, a outra dava qualidade ruim. Daí as regras rígidas do projeto.

**O fluxo:** arrasta o PDF → marca o que quer fazer → confere página a página → escolhe onde salvar → processa.

**Quatro filtros:** Original · Preto e branco · Melhorar · Mágico pro.

**Pilha técnica:** Python 3.11+/3.14, PySide6, PyMuPDF, OpenCV, DoxaPy. Instalador com PyInstaller + Inno Setup.

**Acervo de teste:** `Desktop\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE` (nove livros). Em `Desktop\BIBLIOTECA DO FIM DOS TEMPOS` ficaram só as queixas e os prints do Kaique. Os PDFs originais são somente leitura.

---

## 2. Todas as funcionalidades

### 2.1 Processamento de imagem

| Funcionalidade | Estado |
|---|---|
| Dividir folhas duplas ao meio, detectando a lombada, com correção manual arrastando a linha | feito |
| Filtro **Preto e branco** (binarização adaptativa, DoxaPy) | feito, com defeitos |
| Filtro **Melhorar** (divisão pelo fundo estimado, preservando a cor) | feito, com defeitos |
| Filtro **Mágico pro** (contraste local em LAB, saturação, nitidez, branqueamento) | feito, com defeitos |
| Endireitar por perfil de projeção, limitado a ±5°, ignorando abaixo de 0,1° | feito |
| Cortar bordas: fundo de escaneamento, faixa de lombada, margem sobrando | feito |
| Montar cadernos (imposição), duas páginas por folha, para imprimir frente e verso sem configurar nada no Acrobat | feito |
| Caminho rápido da imposição: se só a imposição estiver marcada, copiar as páginas sem rasterizar | **não verificado** |
| Escolha do binarizador por página (não há vencedor único entre os 18 testados) | **pendente** |
| Separação de chapas vermelho/preto para impressão em duas cores | **decisão pendente** — ver seção 5 |

### 2.2 Seleção e marcação — o "modo Photoshop"

Origem: o pedido de pesquisar como Photoshop e Adobe PDF fazem seleção, parar só com 99% de certeza, e juntar seleção com filtro.

| Funcionalidade | Estado |
|---|---|
| Marcar regiões como **gravura ou foto · letra e traço · papel** | feito |
| Sete ferramentas: Retângulo · Oval · Laço · Ponto a ponto · Pincel · Varinha mágica · **Pegar tudo desta cor** | feito |
| Modos **somar** e **tirar** | feito |
| **Filtro só neste pedaço** — aplicar um filtro diferente numa região marcada | feito, com emenda visível |
| Detecção automática de regiões (o programa marca sozinho: gravura, letra, papel) | feito — 23 de 26 páginas |
| Reconhecer **letra antiga** — o modelo foi treinado em documento moderno, e 3 das 26 falham por isso | **pendente** |
| Precisão da seleção: "precisa selecionar só o texto, reconhecer desenhos, cores, padrões" | **pendente** |
| Zoom e Mão para navegar a página | feito |

### 2.3 Sistema de alertas — "o princípio central do aplicativo"

11 tipos: página colorida · lombada incerta · não parece dupla · muito torta · ângulo suspeito · em branco · escura demais · apagada demais · corte pegou conteúdo · resolução baixa · tamanho diferente.

| Funcionalidade | Estado |
|---|---|
| Miniatura laranja para página duvidosa | feito |
| Contador clicável no topo | feito |
| Faixa explicativa com botão de correção em um clique | feito |
| Painel "Páginas para revisar" agrupado por tipo | feito |
| Aviso antes de processar se houver páginas não conferidas | feito |
| **"Nunca alertar à toa" — menos de 10% das páginas marcadas** | **reprovado** — 349 de 2903 só em "ângulo suspeito" (12%) |

### 2.4 Conferência e ajustes

| Funcionalidade | Estado |
|---|---|
| Deslizantes: Força do preto · Intensidade · Clareza do fundo (0–100, padrão 50) | feito |
| Cortar bordas com alças arrastáveis | feito |
| Ajustar ângulo arrastando o mouse, com linhas-guia | feito |
| Apagar página, com opção de restaurar | feito |
| "só nesta" · "usar em todas" · "só nas próximas" | feito |
| Filtros diferentes em páginas diferentes, gerando um PDF só | **não verificado ponta a ponta** |
| Ampliar a página em tela grande, com zoom e arrasto | feito |
| Modo comparar — dois filtros lado a lado, sincronizados | **não verificado** |
| Prévia ao vivo ao arrastar o deslizante | **não verificado** |
| Desfazer ilimitado gravado em arquivo (JSON Lines), sobrevivendo a fechar o programa | feito |
| Atalhos: setas · Espaço · Tab · 1 2 3 4 · Delete · Ctrl+Z · letras das ferramentas | feito |

### 2.5 Cadernos e encadernação

| Funcionalidade | Estado |
|---|---|
| Verificação automática: o programa relê o PDF gerado e confere a ordem contra o mapa de imposição | feito |
| **Marca de alceamento** — risco preto na dobra, deslocado a cada caderno, formando escadinha diagonal na lombada | ver seção 5 |
| Numeração discreta do caderno na primeira folha | ver seção 5 |

### 2.6 Projetos salvos

| Funcionalidade | Estado |
|---|---|
| `projetos.py` com assinatura do PDF (64 KB do começo, meio e fim + tamanho) | feito, 24 testes |
| PDF que mudou de pasta religa sozinho | feito |
| PDF trocado por outro de mesmo nome é **recusado** (não aplicar corte de um livro em outro) | feito |
| Resumo por projeto, para a tela inicial montar 50 cartões sem abrir 50 históricos | feito |
| Salvamento automático ligado na tela de conferir, com respiro de 600 ms | feito |
| **Nunca perguntar "quer salvar?"** | feito |
| Arquivo de ações truncado não derruba o programa | feito |

### 2.7 Entrega e instalação

| Funcionalidade | Estado |
|---|---|
| Instalador Inno Setup: Arquivos de Programas, atalho, "Adicionar ou remover programas", assistente em português, desinstalador | feito |
| Versão portátil, para pendrive | **não verificado** |
| Escolher pasta de saída, editar nome do arquivo, lembrar a última pasta, avisar se já existe | feito |
| Rodar em Windows sem Python, sem administrador, com Área de Trabalho no OneDrive, nome de usuário acentuado | **não verificado em máquina limpa** |
| 20 de 20 casos de robustez (PDF corrompido, com senha, disco cheio, 1010 páginas, cancelar no meio) | feito |

---

## 3. As dez queixas do Kaique

Fonte de requisito. Ficam nos `.txt` com print ao lado.

| Queixa, nas palavras dele | Estado |
|---|---|
| "as letras estão ficando pixeladas, precisam ficar mais arredondadas, mais nítidas" | corrigido (o raio da nitidez era largo demais e fazia halo) |
| "o mágico pro está deixando muito pixelado a imagem" | corrigido, mesma causa |
| "às vezes a parte de trás fica com uma mancha da parte da frente" | **NÃO corrigido** — ver seção 4 |
| "o programa não localizou as bordas corretamente" | corrigido |
| "o livro já foi recortado ao meio, sobra dos lados uma parte branca" | corrigido |
| "colocar botão clicável nas páginas que o programa não tem certeza" | feito |
| "a barra de scroll devia ser preta" | feito |
| "como ter certeza que os cadernos estão na sequência correta sem olhar folha por folha?" | feito (verificação automática) |
| "no mágico pro o fundo deveria ficar totalmente branco, preservando as cores" | parcial |
| "queremos que fique branco a página e só as letras pretas" | parcial |

**Nenhuma foi aprovada pelo Samuel.** Tudo marcado como feito foi julgado pelo próprio Claude Code.

---

## 4. Defeitos abertos

### O grave: a mancha do verso

**O Preto e branco não remove a mancha do verso — ele a escurece.** No original o texto do verso é um cinza fraco; depois do filtro vira marca preta legível. Ampliado, dá para ler as letras espelhadas. O Melhorar e o Mágico pro também deixam o fantasma visível.

É o caso que o Kaique chamou de mais difícil, e o programa está piorando a página.

**A régua não pega isso** porque mede o fundo longe da tinta, e ali o fundo ficou branco. O que piorou foi a mancha, que a régua conta como tinta.

**A solução recomendada:** o acervo tem as duas faces da mesma folha escaneadas. Espelhar a imagem do verso, alinhar sobre a frente e subtrair. Não é adivinhação — o programa passa a olhar o que causou a mancha. As tentativas de uma face só já se esgotaram.

### Outros defeitos vistos nas imagens de conferência

| Defeito | Onde |
|---|---|
| Fundo liso vira manchado, com **halo branco** em volta da figura, nos três filtros | estampa colorida |
| **Faixa preta na lateral esquerda**, nos quatro filtros — fundo de scanner não cortado | capa de madeira |
| Folha vai a branco mas fica com **riscos pretos na borda e pontos espalhados** | folha de guarda, no Preto e branco |
| Melhorar e Mágico pro deixam a folha **creme**, não branca | folha de guarda |
| **Rubricação vermelha vira preto** no Preto e branco | Graduale e Livro de Horas |
| Título impresso e uma de quatro legendas saem como **foto**, as outras três como texto, na mesma folha | BRODERIES e Siebmacher |
| **Faixa mais clara no pé da gravura**, emenda visível | filtro só no pedaço |
| Partitura manuscrita sai marcada como desenho | Graduale p. 126 |

### O achado da tinta marrom

O amarelado não estava no papel — o fundo já saía em 250–255. **Está na tinta.** A tinta impressa de 1579 é marrom, não preta, e a orla de cada letra carrega essa cor. Uma página inteira disso o olho lê como amarelada, e a impressora gasta tinta colorida em cada letra.

Correção medida: tirar a cor do que não é cor de verdade (papel velho e tinta amarronzada) e poupar o que é (rubricação, gravura). **Risco a testar:** rubricação desbotada também é marrom — vermelho medieval envelhece para laranja-âmbar. Testar numa página de rubricação gasta, não só de vermelho vivo. Se não separar por cor, separar pela forma: rubrica é linha e letra inteira em vermelho; orla marrom é só a beirada de uma letra preta.

### O problema estrutural da régua

Dos defeitos listados acima, **a régua não pegaria nenhum**. São defeitos de aparência, e ela mede propriedades locais. Faltam dois critérios:

- **Comparar na região onde havia mancha**, não só no fundo limpo. Se o que era fraco ficou forte, é piora.
- **Olhar a moldura da página** — os últimos milímetros de cada borda. Faixa escura ali é fundo de scanner, nunca conteúdo.

Um terceiro, já anotado: **medida de sujeira guardada.** O Otsu marca zero pioras mas guarda o dobro de tinta do Sauvola — mantém a mancha como se fosse letra, e nada pega isso.

### Scan de baixa resolução

As páginas do Boécio têm rampa original entre 0,70 e 0,86 — já nascem fora da faixa saudável. São 4 MB para 50 folhas. **Filtro nenhum recupera resolução que não foi capturada.** Devem ser classificadas à parte, julgadas por piora absoluta, e o remédio é reescanear. É o único ponto do projeto em que "até ficar perfeito" não se aplica.

---

## 5. Decisões tomadas e pendentes

### Tomadas

**Layout novo, modelo Photoshop.** Aprovado pelo Samuel, com desenhos em SVG e PNG a 1366×768.
- Tela de trabalho: barra de menu · barra de opções que muda por ferramenta · trilha de 42 px com nove ferramentas · quatro painéis de 172 px à direita (Para revisar, Marcar como, Filtro da página, Histórico) · tira de páginas no pé · "Salvar em" e "Nome do arquivo" fora da tela.
- Tela inicial: cartões com miniatura da primeira página, barra de progresso, cartão laranja para PDF fora do lugar, busca, menu de contexto com cinco ações.
- A página deve ocupar pelo menos 60% da altura.

**Corte de bordas: uma caixa única para o livro inteiro**, não corte livre por página, senão a mancha de texto pula de posição a cada virada de folha. Dois grupos: metades esquerdas e direitas.

**Preto e branco: saída em cinza com fundo branco**, não binarização pura, para preservar a forma da letra. O deslizante "Força do preto" vai de letra suave a preto duro.

**Supersampling** para arredondar a borda das letras: decidir tinta/papel em resolução dobrada e reduzir com média de área.

**Não perseguir os 612 px do desenho.** 489 px é 64% da janela, e o critério aprovado era 60%. Transformar as abas em modo da página mexeria no arrasto das alças de corte — risco alto por 3% de altura.

### Pendentes

**Separação de chapas vermelho/preto.** O instituto tem prensas de duas cores. Num Gradual ou Livro de Horas, a distinção vermelho/preto **é** a tipografia litúrgica, não enfeite — e o Breviário virá com o mesmo problema. Talvez o certo não seja melhorar a conversão para cinza, mas o filtro separar duas chapas. Muda a estrutura da saída.

**Marca de alceamento.** A verificação automática de sequência já existe e pega erro de cálculo. A marca de alceamento pega o erro humano de dobrar e juntar — são problemas diferentes e só as duas juntas respondem a pergunta do Kaique.

**O veredito do CamScanner.** Pedido em 18/07: "o programa já substitui o CamScanner para o trabalho do Kaique? Sim, não, ou ainda não." A pasta `para_comparar/` foi montada e a comparação nunca foi feita. É a única pergunta que mede o programa contra o que ele usa hoje.

---

## 6. O problema recorrente: o que é feito não chega ao Samuel

**Zero itens aprovados pelo Samuel**, em 57+ commits. Tudo marcado como feito foi julgado pelo próprio Claude Code.

E, na última verificação, **o Samuel abriu o programa e viu a tela antiga** — sem barra de menu, com as quatro linhas de botões, e com a barra preta que tinha sido corrigida na primeira etapa. Hipóteses: executável antigo não reconstruído, mais de uma cópia da pasta no computador, ou tela nova criada sem o programa carregá-la (como aconteceu com o `projetos.py`, que ficou pronto sem chamador).

**Isso precisa ser resolvido antes de qualquer novo desenvolvimento.** Prova visual que sai de um caminho diferente do que o Samuel abre não prova nada.

**A entrega padrão** é `relatorios/para-conferir.html`: um quadro por mudança, antes e depois já ampliados, nome do livro e página, o que olhar em uma frase, os números, e as ressalvas escritas. Ressalva escrita não é demérito; ressalva escondida é.

---

## 7. Regras de trabalho

**Do Samuel para o Claude Code:**

- **Não recomeçar do zero, não reescrever módulos inteiros, não reorganizar o que funciona.** Testar não é permissão para reconstruir.
- **Ir até o fim sem interromper.** Decidir dentro da alçada e executar. Se o contexto acabar, parar num commit com o programa rodando e dizer onde parou.
- **Só chamar quando terminar tudo.**
- **Perguntar apenas antes de mexer em estrutura:** criar ou remover filtro, mudar tela, mudar formato de dados, alterar o desfazer, trocar biblioteca.
- **Abrir todas as imagens antes de dizer que funcionou.** Percentual não é veredito. Já foi reportado "10 de 10 corretas" tendo olhado uma imagem — seis estavam erradas.
- **Medir antes, uma mudança por vez, medir de novo, reverter se qualquer número piorar.** Se achar que vale mesmo assim, não reverter por conta própria: registrar os dois resultados e apresentar.
- **Português comum, sem jargão.** "O programa estava estragando a capa dos livros", não "o balanço de branco eleva o ruído de 5,5 para 17,5". O número vem depois da frase que se entende, nunca no lugar dela.
- **Ser conciso** — o essencial no chat, o detalhe em arquivo.
- Interface **com** acento (UTF-8). Caminhos de disco **sem** acento. **Nenhum emoji** em rótulo. PySide6, nunca tkinter.

**O critério final, nas palavras do Samuel:** *"Eu quero que o papel saia branco, e o desenho também saia perfeito."*

**A lista de pedidos vive em `PEDIDOS.md`, no repositório**, com estados pendente/feito/conferido. Só o Samuel marca CONFERIDO. Isso existe porque a lista, quando só vivia nas conversas, sumia junto com elas.

---

## 8. O que fazer a seguir, em ordem

1. **Descobrir por que o programa que o Samuel abre não é o que foi alterado.** Nada mais importa até isso.
2. **Reconstruir o instalador** e deixá-lo na pasta de testes, com instrução de como abrir a versão nova.
3. **A mancha do verso**, pela técnica das duas faces. É o caso decisivo contra o CamScanner.
4. **Os dois critérios novos da régua** (região da mancha e moldura da página), senão os defeitos continuam passando.
5. **Os outros defeitos de imagem**: halo da estampa, faixa preta da capa, pontos da folha de guarda, rubricação, BRODERIES.
6. **O Samuel conferir o `para-conferir.html`** e marcar CONFERIDO no `PEDIDOS.md`.
7. **O veredito do CamScanner.**
8. Depois disso: letra antiga, precisão da seleção, alceamento, chapas de duas cores.
