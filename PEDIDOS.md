# PEDIDOS.md — a lista de conferência do Editor de Impressão

Este arquivo fica na raiz do repositório e é a única lista que vale.
Enquanto ela vivia só nas conversas, sumia junto com elas.

**Só o Samuel marca APROVADO.**

---

## Como marcar

| Marca | Quer dizer |
|---|---|
| `[ ]` | pendente — ninguém olhou ainda |
| `[?]` | **pronto para conferir** — o Claude Code fez e preparou; falta o Samuel |
| `[x]` | **APROVADO** — o Samuel abriu, testou e aprovou |
| `[~]` | melhorar — o Samuel testou e não gostou; virou tarefa |
| `[-]` | descartado — não precisamos disso |

## Quem confere

| Sigla | Quem |
|---|---|
| **M** | máquina — o Claude Code roda e decide sozinho |
| **S** | Samuel — precisa de olho humano |

O Claude Code pode marcar `[?]`. **Nunca `[x]`.**

## Os PDFs de teste

Sete livros fixos, escolhidos pelo Samuel em 08/09/2026, para o resultado ser
comparável entre um dia e outro. Todos em
`D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE\`.

1. **Giovambattista Palatino cittadino romano** — folha dupla amarelada, o caso
   mais comum (texto simples, sem outro defeito somado)
2. **Livro de Horas - Luís XIV** — capa colorida / iluminura com ouro (pág. 61
   já documentada em `para_comparar/LEIA.txt`)
3. **Rhetorica Christiana - Fray Diego Valadés** — página com gravura,
   xilogravura de traço fino (pág. 73 já documentada)
4. **Marial de sermoens - Frei Balthasar Paez** — folha quase transparente,
   mancha do verso, o pior defeito aberto (pág. 862 já documentada); também
   tem página bem amarelada (pág. 575)
5. **Sobre a Consolação da Filosofia - Severino Boécio** — scan ruim, baixa
   resolução (4 MB para 50 folhas); também tem página torta (pág. 2)
6. **Na escola de Jesus - Catecismo explicado com imagens** — catecismo com
   imagens, ainda sem defeito específico documentado
7. **Schön Neues Modell Buch - Johann Siebmacher** — livro de padrões/gravuras,
   ainda sem defeito específico documentado

Ficaram de fora: Graduale - Saeculum XIV (partitura manuscrita, tratada à parte
em `avaliar.py`) e POINTS d'ANCIENNES BRODERIES ANGLAISES.

---

# BLOCO 1 — Abrir o programa e carregar o PDF

| | Item | O que fazer | O que esperar | Quem |
|---|---|---|---|---|
| `[ ]` | Abrir pelo atalho | Clicar no atalho da Área de Trabalho | Abre a tela **nova**, com barra de menu no topo. Se aparecer a tela antiga de quatro linhas de botões, **pare tudo** — é o problema da cópia fantasma | S |
| `[ ]` | Arrastar PDF para a tela inicial | Arrastar cada um dos 5 PDFs | Carrega sem erro, mostra as páginas | S |
| `[ ]` | Cartões de projetos anteriores | Fechar e reabrir | Os projetos aparecem com miniatura da primeira página e barra de progresso | S |
| `[ ]` | Busca e menu de contexto na tela inicial | Buscar um projeto, clicar com o botão direito | Encontra; o menu mostra as cinco ações | S |
| `[ ]` | PDF que mudou de pasta religa sozinho | Mover o PDF para outra pasta e reabrir o projeto | Cartão laranja, e religa ao apontar o novo lugar | S |
| `[ ]` | PDF trocado por outro de mesmo nome é recusado | Substituir o arquivo por outro livro com o mesmo nome | **Recusa.** Não pode aplicar corte de um livro em outro | M |
| `[ ]` | Nunca perguntar "quer salvar?" | Fechar o programa no meio do trabalho | Fecha direto; ao reabrir, o trabalho está lá | S |
| `[ ]` | Salvamento automático | Mexer em várias páginas seguidas | Salva sozinho, com respiro de 600 ms, sem travar a tela | M |
| `[ ]` | Arquivo de ações truncado não derruba | (teste automático) | Programa abre normalmente | M |
| `[ ]` | Robustez: PDF corrompido | (teste automático) | Aviso em português, programa continua aberto | M |
| `[ ]` | Robustez: PDF com senha | (teste automático) | Aviso em português, programa continua aberto | M |
| `[ ]` | Robustez: arquivo some no meio | (teste automático) | Aviso em português, trabalho não se perde | M |
| `[ ]` | Robustez: disco cheio | (teste automático) | Aviso em português, trabalho não se perde | M |
| `[ ]` | Robustez: livro de 1010 páginas | (teste automático) | Termina, e a memória não cresce com o tamanho | M |
| `[ ]` | Robustez: cancelar no meio | Clicar em cancelar durante o processamento | Para de verdade, sem travar e sem PDF pela metade | S |

---

# BLOCO 2 — Dividir folhas ao meio

| | Item | O que fazer | O que esperar | Quem |
|---|---|---|---|---|
| `[ ]` | Detecção automática da lombada | Abrir o PDF de folha dupla | A linha cai na sombra da lombada, não no meio cego | S |
| `[ ]` | Arrastar a linha de corte | Arrastar com o mouse | Anda suave, e a prévia acompanha | S |
| `[ ]` | "Não dividir esta página" | Usar numa capa ou ilustração de página inteira | A folha fica inteira | S |
| `[ ]` | "Usar em todas" | Ajustar uma e aplicar ao livro | A posição relativa vai para todas as folhas | S |
| `[ ]` | Girar 90° | Clicar horário e anti-horário | Gira e a prévia acompanha | S |
| `[ ]` | Ordem esquerda → direita | Conferir o resultado | Cada folha vira duas páginas, na ordem certa | M |
| `[ ]` | Alerta "lombada incerta" | Ver as páginas marcadas | Marca as duvidosas de verdade, não as óbvias | S |
| `[ ]` | Alerta "não parece dupla" | Ver as páginas marcadas | Idem | S |

---

# BLOCO 3 — Cortar bordas e endireitar

| | Item | O que fazer | O que esperar | Quem |
|---|---|---|---|---|
| `[ ]` | Cortar bordas com alças arrastáveis | Arrastar as alças | Andam suave, a prévia acompanha | S |
| `[ ]` | Caixa única para o livro inteiro | Ajustar o corte | Vale para o livro todo, em dois grupos: metades esquerdas e direitas. A mancha de texto **não** pula de posição a cada virada de folha | S |
| `[ ]` | Cortar fundo de escaneamento | PDF da capa de madeira | **Defeito conhecido:** faixa preta na lateral esquerda em todos os filtros | S |
| `[ ]` | Endireitar automático | Páginas tortas | Limitado a ±5°, ignora abaixo de 0,1° | S |
| `[ ]` | Ajustar ângulo arrastando | Arrastar com o mouse | Linhas-guia aparecem e ajudam | S |
| `[ ]` | Alerta "muito torta" | Ver as marcadas | Acima de 3° | M |
| `[ ]` | Alerta "ângulo suspeito" | Ver as marcadas | **Reprovado hoje:** 349 de 2903 folhas (12%). O combinado era menos de 10% | S |
| `[ ]` | Alerta "corte pegou conteúdo" | Ver as marcadas | Avisa quando o recorte encostou em texto | S |

---

# BLOCO 4 — Os quatro filtros

| | Item | O que fazer | O que esperar | Quem |
|---|---|---|---|---|
| `[ ]` | Original | Aplicar | Não mexe em nada | M |
| `[ ]` | Preto e branco | Aplicar nos 5 PDFs | Papel branco, letras pretas, forma da letra preservada | S |
| `[ ]` | Melhorar | Aplicar nos 5 PDFs | Fundo limpo, **cores originais preservadas**, sem saturar | S |
| `[ ]` | Mágico pro | Aplicar nos 5 PDFs | Cor viva, texto nítido, fundo branco | S |
| `[ ]` | Deslizante "Força do preto" | Arrastar de 0 a 100 | Muda de letra suave a preto duro | S |
| `[ ]` | Deslizante "Intensidade" (Mágico pro) | Arrastar | Muda de suave a bem forte | S |
| `[ ]` | Deslizante "Clareza do fundo" (Melhorar) | Arrastar | Empurra o fundo para o branco | S |
| `[ ]` | Prévia ao vivo ao arrastar | Arrastar devagar e rápido | Atualiza em tempo real, sem travar (baixa resolução no arrasto, normal ao soltar) | S |
| `[ ]` | "Só nesta página" | Trocar o filtro de uma página | Só ela muda | S |
| `[ ]` | "Usar em todas" | Aplicar | O livro inteiro muda | S |
| `[ ]` | "Só nas próximas" | Aplicar no meio do livro | Da página atual em diante | S |
| `[ ]` | Filtros diferentes — **um PDF só** | Livro em P&B, só a capa em Mágico pro | Sai um PDF único, cada página com o seu filtro. **Nunca conferido ponta a ponta** | S |
| `[ ]` | Ampliar a página em tela grande | Clicar num cartão de filtro | Ocupa a janela inteira, em resolução maior — não é miniatura esticada | S |
| `[ ]` | Zoom e arrasto no ampliado | Roda do mouse, botões + / − / ajustar, arrastar | Funciona | S |
| `[ ]` | Teclas no ampliado | Setas, 1 2 3 4, Esc | Setas mudam de página, números trocam o filtro, Esc volta | S |
| `[ ]` | Modo comparar lado a lado | Abrir dois filtros | Zoom e posição **sincronizados**. Nunca verificado | S |
| `[ ]` | **Mancha do verso** | PDF da folha transparente | **Defeito grave aberto:** o P&B escurece a mancha em vez de tirar. Ampliado dá para ler as letras espelhadas | S |
| `[ ]` | Rubricação vermelha | Graduale e Livro de Horas | **Defeito aberto:** vermelho vira barra preta no P&B | S |
| `[ ]` | Halo em volta da figura | Estampa colorida | **Defeito aberto:** fundo liso vira manchado, com halo branco, nos três filtros | S |
| `[ ]` | Pontos na folha de guarda | Folha de guarda no P&B | **Defeito aberto:** riscos pretos na borda e pontos espalhados | S |
| `[ ]` | Folha creme em vez de branca | Folha de guarda, Melhorar e Mágico pro | **Defeito aberto** | S |
| `[ ]` | Escolha do binarizador por página | — | **Pendente.** Não há vencedor único entre os 18 do DoxaPy | S |
| `[ ]` | Saída 1 bit no P&B | Conferir o tamanho do arquivo | Arquivo pequeno | M |

---

# BLOCO 5 — Alertas (as páginas laranja)

| | Item | O que fazer | O que esperar | Quem |
|---|---|---|---|---|
| `[ ]` | Os 11 tipos de alerta | Rodar nos 5 PDFs | Colorida · lombada incerta · não parece dupla · muito torta · ângulo suspeito · em branco · escura demais · apagada demais · corte pegou conteúdo · resolução baixa · tamanho diferente | M |
| `[ ]` | Miniatura laranja com "!" | Olhar a tira | Só as duvidosas ficam laranja | S |
| `[ ]` | Contador clicável no topo | Clicar | Leva para a primeira; Tab pula para a próxima | S |
| `[ ]` | Faixa explicativa com correção em um clique | Ler a faixa | Texto em português simples, com botão que aplica a sugestão | S |
| `[ ]` | Painel "Páginas para revisar" | Abrir | Agrupado por tipo, com os números das páginas | S |
| `[ ]` | Aviso antes de processar | Processar com páginas não conferidas | Avisa antes | S |
| `[ ]` | **Menos de 10% marcadas** | Contar no acervo | **Reprovado hoje:** 12% só em "ângulo suspeito" (349 de 2903) e 305 em "tem cor". O alerta corre risco de virar ruído | M |

---

# BLOCO 6 — Seleção e marcação (o "modo Photoshop")

| | Item | O que fazer | O que esperar | Quem |
|---|---|---|---|---|
| `[ ]` | Marcar gravura · letra · papel | Marcar à mão numa página | As três classes funcionam | S |
| `[ ]` | Ferramenta Retângulo | Usar | Funciona | S |
| `[ ]` | Ferramenta Oval | Usar | Funciona | S |
| `[ ]` | Ferramenta Laço | Usar | Funciona | S |
| `[ ]` | Ferramenta Ponto a ponto | Usar | Funciona | S |
| `[ ]` | Ferramenta Pincel | Usar | Funciona | S |
| `[ ]` | Varinha mágica | Usar na partitura do Graduale | **Defeito conhecido:** vaza e leva 99,8% da folha | S |
| `[ ]` | "Pegar tudo desta cor" | Usar na mesma partitura | Pega 7,7% — as pautas vermelhas e as letras rubricadas. Compara só o matiz | S |
| `[ ]` | Modos somar e tirar | Usar | Funcionam | S |
| `[ ]` | "Filtro só neste pedaço" | Folha em P&B, gravura no Original | Funciona, mas **há emenda visível**: faixa mais clara no pé da gravura | S |
| `[ ]` | Marcar folha inteira como papel = folha em branco | Usar numa capa indesejada | A folha sai em branco | S |
| `[ ]` | Detecção automática de regiões | Rodar `avaliar_selecao.py` | 23 de 26 hoje | M |
| `[ ]` | Letra antiga reconhecida | Graduale 126, Siebmacher 45, Pesel 73 | **Pendente.** O modelo foi treinado em documento moderno. Os três falham por isso | S |
| `[ ]` | Admite a dúvida | Ver as páginas incertas | Fica laranja com "Desenho ou escrita? Não tenho certeza" | S |
| `[ ]` | Zoom e Mão para navegar | Usar | Funcionam | S |

---

# BLOCO 7 — Cadernos e imposição

| | Item | O que fazer | O que esperar | Quem |
|---|---|---|---|---|
| `[ ]` | Montar cadernos | Processar um livro | Duas páginas por folha, pronto para imprimir frente e verso sem configurar nada no Acrobat | S |
| `[ ]` | Verificação automática da sequência | Processar | O programa relê o PDF gerado, simula a dobra e confere: leitura sai 1, 2, 3 até o fim; folhas em pares frente/verso; nenhuma página sumiu ou repetiu | M |
| `[ ]` | Caminho rápido sem rasterizar | Marcar só a imposição | Copia as páginas sem rasterizar — rápido e sem perder qualidade. **Nunca verificado** | M |
| `[ ]` | Marca de alceamento | — | **Pendente.** Risco preto na dobra, deslocado a cada caderno, formando escadinha na lombada. Pega o erro humano de dobrar e juntar, que a verificação automática não pega | S |
| `[ ]` | Numeração discreta do caderno | — | **Pendente** | S |
| `[ ]` | Separação de chapas vermelho/preto | — | **Decisão pendente.** O instituto tem prensas de duas cores, e num Gradual a distinção vermelho/preto é a tipografia, não enfeite | S |

---

# BLOCO 8 — Salvar, desfazer e instalar

| | Item | O que fazer | O que esperar | Quem |
|---|---|---|---|---|
| `[ ]` | Escolher pasta de saída | Clicar em "Escolher pasta" | Abre o seletor do Windows | S |
| `[ ]` | Editar o nome do arquivo | Digitar outro nome | Funciona | S |
| `[ ]` | Lembrar a última pasta | Processar duas vezes | Sugere a última usada | S |
| `[ ]` | Avisar se o arquivo já existe | Salvar com nome repetido | Oferece substituir ou renomear | S |
| `[ ]` | Pasta sem permissão | Escolher uma pasta protegida | Avisa em português e sugere outra | M |
| `[ ]` | Desfazer ilimitado | Ctrl+Z várias vezes | Volta passo a passo | S |
| `[ ]` | Desfazer sobrevive a fechar o programa | Fechar e reabrir, e desfazer | O histórico continua lá (gravado em JSON Lines) | S |
| `[ ]` | Atalhos de teclado | Setas · Espaço · Tab · 1 2 3 4 · Delete · Ctrl+Z · letras das ferramentas | Todos funcionam | S |
| `[ ]` | Instalador Inno Setup | Instalar numa máquina | Instala em Arquivos de Programas, cria atalho no menu Iniciar e na Área de Trabalho, aparece em "Adicionar ou remover programas", assistente em português, tem desinstalador | S |
| `[ ]` | Versão portátil | Rodar de pendrive | **Nunca verificado** | S |
| `[ ]` | Windows limpo, sem Python, sem administrador | Instalar numa máquina que nunca teve o projeto | Funciona | S |
| `[ ]` | Área de Trabalho no OneDrive | Instalar assim | Funciona | S |
| `[ ]` | Nome de usuário com acento | Instalar assim | Funciona | S |
| `[ ]` | Textos da interface com acento | Percorrer todas as telas | Impressão, página, Mágico, só nesta, próximas, Força, Espaço, dúvida, não | M |
| `[ ]` | Nenhum emoji em rótulo | (teste automático) | Nenhum | M |

---

# BLOCO 9 — As dez queixas do Kaique

Fonte de requisito, nas palavras dele. **Nenhuma foi aprovada pelo Samuel** —
tudo marcado feito foi julgado pelo próprio Claude Code.

| | Queixa | Estado alegado | Quem |
|---|---|---|---|
| `[ ]` | "as letras estão ficando pixeladas, precisam ficar mais arredondadas" | corrigido — o raio da nitidez era largo demais e fazia halo | S |
| `[ ]` | "o mágico pro está deixando muito pixelado a imagem" | corrigido, mesma causa | S |
| `[ ]` | "às vezes a parte de trás fica com uma mancha da parte da frente" | **NÃO corrigido** — o pior defeito aberto | S |
| `[ ]` | "o programa não localizou as bordas corretamente" | corrigido | S |
| `[ ]` | "o livro já foi recortado ao meio, sobra dos lados uma parte branca" | corrigido | S |
| `[ ]` | "colocar botão clicável nas páginas que o programa não tem certeza" | feito | S |
| `[ ]` | "a barra de scroll devia ser preta" | **feita, e depois revertida para cinza médio em 08/08 — ver seção 9 do CLAUDE.md** | S |
| `[ ]` | "como ter certeza que os cadernos estão na sequência correta sem olhar folha por folha?" | feito | S |
| `[ ]` | "no mágico pro o fundo deveria ficar totalmente branco, preservando as cores" | parcial | S |
| `[ ]` | "queremos que fique branco a página e só as letras pretas" | parcial | S |

---

# BLOCO 10 — A pergunta que está aberta desde 18/07/2026

| | Item | O que fazer | Quem |
|---|---|---|---|
| `[ ]` | **O veredito do CamScanner** | Pegar as cinco páginas difíceis, passar no CamScanner e no nosso programa, e pôr lado a lado. Responder em uma frase: **o programa já substitui o CamScanner para o trabalho do Kaique? Sim, não, ou ainda não.** A pasta `para_comparar/` foi montada e a comparação nunca foi feita | S |

---

## Histórico das conferências

Aqui vai a data e o resultado de cada sessão de teste, para dar para ver o
projeto andando.

| Data | Bloco testado | Aprovados | A melhorar | Descartados |
|---|---|---|---|---|
| | | | | |
