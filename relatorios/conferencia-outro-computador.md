# Conferência num computador limpo

Esta lista existe porque metade da Etapa 4 do protocolo **não pode ser
verificada na máquina de desenvolvimento**. Coisas como o SmartScreen bloquear
o instalador, o antivírus barrar o programa ou faltar a biblioteca do Visual
C++ só aparecem num computador que nunca teve o programa nem o Python.

Quem executa: o Samuel ou o Kaique. Onde: um computador limpo, de preferência o
que o Kaique vai usar de verdade.

Marque cada item. Onde falhar, anote o que apareceu na tela — a frase exata
ajuda mais que a descrição.

---

## Antes de começar, anote a máquina

| | |
|---|---|
| Windows (10 ou 11, versão) | |
| Memória | |
| Processador | |
| Já teve Python instalado? | |
| Antivírus em uso | |

---

## 1. A instalação

- [ ] **O instalador abre.** Se o Windows mostrar uma tela azul dizendo
      "O Windows protegeu o computador", isso é o SmartScreen. É esperado num
      programa sem assinatura digital. Clique em **Mais informações** e depois
      em **Executar assim mesmo**.
      Apareceu? ( ) sim ( ) não
- [ ] **O antivírus deixou instalar.** Se bloqueou, anote o nome do antivírus e
      a mensagem.
- [ ] **Instalou sem pedir senha de administrador.** O instalador foi feito
      para instalar só para o usuário atual. Se pediu senha, é defeito.
- [ ] O programa aparece no menu Iniciar.

## 2. A primeira abertura

- [ ] **O programa abre.** Anote quantos segundos levou até a janela aparecer:
      ______
- [ ] **Não apareceu erro sobre biblioteca faltando.** Se aparecer algo como
      "VCRUNTIME140.dll não encontrado" ou "MSVCP140.dll", falta a biblioteca do
      Visual C++ e ela precisa entrar no instalador. Anote a mensagem exata.
- [ ] **Abre num computador que nunca teve Python.** Se pedir Python, o
      empacotamento falhou.

## 3. A janela cabe na tela

Teste em cada resolução que a máquina permitir.

- [ ] Em **1366 × 768** a janela cabe inteira, sem cortar botão nem texto.
- [ ] Com a escala do Windows em **100%** está legível.
- [ ] Com a escala em **125%** os botões continuam inteiros.
- [ ] Com a escala em **150%** o texto não corta.

A escala fica em: Configurações → Sistema → Vídeo → Escala.

## 4. Um livro do começo ao fim

Use um livro de verdade, de preferência um que o Kaique vá processar.

- [ ] Abre um PDF.
- [ ] As miniaturas aparecem. Quantos segundos até a primeira: ______
- [ ] Aplica um filtro e a prévia muda.
- [ ] Gera o resultado até o fim, sem travar.
- [ ] O PDF final abre e está correto.
- [ ] **Quanto tempo levou um livro de cem páginas:** ______

## 5. Sem internet

- [ ] Desligue a internet (avião, ou tire o cabo) e repita o item 4 inteiro.
      O programa não pode depender de rede para nada.

## 6. Coisas que já quebraram antes

- [ ] **Área de Trabalho no OneDrive.** Se esta máquina tem a Área de Trabalho
      sincronizada com o OneDrive, abra um livro que esteja lá. O programa
      pergunta ao Windows onde a Área de Trabalho está, em vez de montar o
      caminho na mão — mas convém confirmar.
- [ ] **Nome de usuário com acento.** Se o usuário do Windows tiver acento
      (José, Conceição), confirme que o programa abre e grava normalmente.
- [ ] **Nome de arquivo difícil.** Tente abrir um PDF chamado
      `Diário do Pároco (cópia 2) - versão final.pdf`.
- [ ] **Pasta de rede ou pendrive.** Grave o resultado num pendrive e confirme
      que funciona.

## 7. Formato de número

- [ ] O programa mostra número decimal com **vírgula** (1,5 e não 1.5) e nada
      aparece errado por causa disso.

---

## Se algo falhar

Anote três coisas e me mande:

1. Em qual item da lista
2. A frase exata que apareceu na tela
3. Uma foto ou print, se der

Com isso eu consigo reproduzir aqui. Sem a frase exata, costuma virar
adivinhação.

---

## O que já foi verificado na máquina de desenvolvimento

Estes itens **não precisam** ser refeitos, mas estão listados para você saber o
que já está coberto:

| | Situação |
|---|---|
| Nome de arquivo com acento, espaço e parêntese | passa |
| Caminho com mais de 260 caracteres | passa |
| PDF corrompido, com senha, vazio, só vetor | passa, com mensagem em português |
| Mais de mil páginas | passa |
| Página gigante, toda preta, toda branca | passa |
| Pendrive removido no meio | passa, com mensagem em português |
| Disco cheio ou pasta inexistente | passa, com mensagem em português |
| Cancelar no meio | passa, sem deixar arquivo pela metade |
| Vários livros seguidos sem reiniciar | passa |
| Memória não cresce com o tamanho do livro | 1 página: +4 MB; 1010 páginas: +0 MB |

São os 20 casos da Etapa 3, todos passando. O detalhe está em
`relatorios/robustez.pdf`.
