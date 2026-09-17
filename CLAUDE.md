# CLAUDE.md — Editor de Impressão

Este arquivo fica na raiz do repositório. O Claude Code lê antes de qualquer coisa.

Escrito em 07/09/2026, ao retomar o projeto depois de um mês parado. Substitui
a versão anterior — a versão anterior media tudo por número e nunca chegava a
"aprovado pelo Samuel"; esta corrige isso (ver seção 4).

---

## 1. O que é este programa, e para quem

Aplicativo de desktop para Windows que recupera PDFs de livros antigos
escaneados e os prepara para reimpressão em cadernos. Um "CamScanner para PC".
Projeto do Instituto São Bento, do Pe. Rosenei, de preservação de livros
esgotados.

**Quem usa é o Kaique, impressor, sem formação técnica.** Ele nunca vê
"Sauvola", "k" ou "deskew" — vê "Força do preto", "Melhorar", "girar a folha".
Toda a interface é em português do Brasil, sem jargão.

**O fluxo:** arrasta o PDF → marca o que quer fazer → confere página a página →
escolhe onde salvar → processa.

**Quatro filtros:** Original · Preto e branco · Melhorar · Mágico pro.

**Duas versões anteriores fracassaram.** Uma travava (customtkinter), a outra
dava qualidade ruim (filtro de fórmula caseira). As regras da seção 3 vieram
daí. Nenhuma é preferência de estilo — cada uma é cicatriz.

**O critério final, em uma frase:**

> "Eu quero que o papel saia branco, e o desenho também saia perfeito."

---

## 2. Como trabalhar comigo (Samuel)

- **Não recomeçar do zero.** Não reescrever módulos inteiros, não reorganizar o
  que funciona. Testar não é permissão para reconstruir.
- **Uma mudança por vez.** Antes de alterar um arquivo, me mostrar o diff e
  esperar minha confirmação.
- **Planejar antes de codar.** Perguntar antes de mexer em estrutura.
- **Ir até o fim dentro da alçada.** Decidir o que é da alçada e executar o
  protocolo inteiro, em vez de parar a cada passo. Se o contexto acabar, parar
  num commit com o programa rodando e dizer onde parou.
- **Português comum, sem jargão.** Primeiro a frase que se entende, depois o
  número. "O programa estava estragando a capa dos livros" — não "o balanço de
  branco eleva o ruído de 5,5 para 17,5". O número vem **depois** da frase,
  nunca no lugar dela.
- **Ser conciso.** O essencial no chat, o detalhe em arquivo.
- **Ser honesto.** Se eu estiver enganado ou correndo um risco, me avisar. Não
  concordar só para agradar.
- **Não inventar detalhe** que eu não forneci.

### Todo relatório sai em três formatos

O Samuel **não abre `.md`** — o Acrobat recusa o arquivo. Relatório que a
pessoa não consegue abrir não é relatório.

Use `relatorio.gravar(texto, destino)`, que grava os três de uma vez:

| | para quem |
|---|---|
| `.md` | para o Claude Code, e para o git comparar linha a linha |
| `.html` | leitura rápida, abre com dois cliques no navegador |
| `.pdf` | arquivo e referência futura |

Nunca gravar só o `.md`. Isso vale para qualquer relatório de teste/conferência
(ver seção 4) — não vale para arquivos de controle do próprio repositório como
este `CLAUDE.md`, `PEDIDOS.md` ou o handoff em `historico/`.

---

## 3. As regras técnicas que não se negociam

- **PySide6, nunca tkinter nem customtkinter.**
- **Uma página por vez na memória.** O pico não pode crescer com o tamanho do
  livro; há livro de 300 MB no acervo. Nunca montar lista com todas as páginas
  processadas.
- **Interface nunca congela.** Todo processamento em QThread, com barra de
  progresso e botão de cancelar que funciona.
- **Nenhuma exceção fecha a janela.** Vira aviso em português numa caixa de
  diálogo; o erro técnico vai para o log, não para a tela.
- **Nenhum emoji em rótulo de interface.** Quebrou no Windows na versão
  anterior.
- **Textos de interface com acento (UTF-8). Caminhos de disco sem acento.**
- **Algoritmo consagrado em vez de fórmula própria.**
- **Nenhum modelo generativo.** Modelo que produz pixel pode inventar detalhe
  numa gravura de 1579, e detalhe inventado entra no PDF como se fosse o livro.
  Rede neural aqui só segmenta: aponta onde estão as coisas, nunca desenha.
- **A máquina só tem Python 3.14**, e todas as dependências funcionam nele
  (PySide6 6.11, PyMuPDF, OpenCV, numpy, Pillow, doxapy, scikit-image).
  **Não sugerir rebaixar a versão do Python.**
- **GPU: GTX 1650 4 GB, sem tensor cores** — nada que dependa de float16 rápido.
- **Erro nunca aparece como stack trace.** `sys.excepthook` grava em `erros.log`
  e mostra "Aconteceu um problema inesperado, mas o programa continua
  funcionando."

**Licença — decisão mudou em 17/09/2026.** Código GPL pode ser incorporado
direto agora (não só estudado de longe): o Samuel decidiu que, se um dia o
programa for liberado, é de graça com doação voluntária — então o programa
inteiro virar GPL (a obrigação que vem de usar código GPL) não é problema.
Isso também resolve a ressalva antiga do PyMuPDF: ele é AGPL (mais estrito
que GPL comum), e antes isso só valia "para uso interno está tudo certo, se
distribuir fora precisa rever" — agora, com a decisão de liberar com
código-fonte aberto, essa ressalva deixa de existir. PySide6 continua LGPL,
OpenCV/numpy Apache-2.0/BSD, DoxaPy CC0, scikit-image BSD, Pillow HPND — sem
mudança nenhuma nesses.

---

## 4. Testes — e a regra que existe por causa do que já deu errado

Foram 57+ commits com tudo marcado "feito" pelo próprio Claude Code, e **zero
itens aprovados por mim**. Já foi reportado "10 de 10 corretas" tendo olhado
uma imagem — seis estavam erradas. Por isso os testes agora têm dois tipos, e
só um deles o Claude Code decide.

### 4.1 Teste de máquina — o Claude Code faz e decide sozinho

Perguntas com resposta objetiva, que não dependem de gosto:

- O programa fecha ao clicar em algum botão, em qualquer tela, em qualquer
  tamanho de janela?
- O PDF de saída tem o mesmo número de páginas esperado? Alguma sumiu ou
  repetiu?
- A memória cresce com o tamanho do livro?
- PDF corrompido, protegido por senha, arquivo que some no meio, disco cheio,
  livro de 1010 páginas, cancelar no meio — o programa segura?
- Os cadernos saem na sequência certa quando se simula a dobra?
- Os textos da interface estão com acento?

Isso roda a cada mudança, automaticamente. **Essa é a aceleração do projeto** —
eu nunca preciso olhar.

### 4.2 Teste de olho — o Claude Code prepara, eu decido

"O papel saiu branco?" "O desenho ficou perfeito?" "A linha de corte está no
lugar certo?" Aqui o Claude Code já errou, e a régua também: hoje `avaliar.py`
dá número bom enquanto a mancha do verso piora. **Número que não pega o pior
defeito não pode dar veredito.**

O que o Claude Code faz:

1. Roda a mudança em **todos** os PDFs do conjunto de teste
2. Gera antes/depois e **abre todas as imagens** — não uma amostra
3. Monta `relatorios/para-conferir.html`: um quadro por mudança, já ampliado,
   com nome do livro e da página, o que olhar em uma frase, os números, e as
   ressalvas escritas
4. Escreve a própria opinião **junto com as ressalvas**
5. **Para. E me chama.**

**Ressalva escrita não é demérito. Ressalva escondida é.**

### 4.3 A regra de ouro

> O Claude Code pode escrever **"PRONTO PARA CONFERIR"** e a opinião dele.
> **Nunca "APROVADO".** Só eu marco APROVADO, no `PEDIDOS.md`.
>
> E todo item precisa dizer se foi teste de **máquina** ou de **olho**.

### 4.4 Auditoria por amostragem

De vez em quando eu confiro um item que o Claude Code deu como verificado por
máquina. Se bater, ele ganha mais autonomia. Se eu pegar um erro, a categoria
"máquina" encolhe. A confiança aqui é medida, não prometida.

### 4.5 Quantos testes existem de verdade

Conferido em 07/09/2026, direto no código (os documentos antigos divergiam
entre 59 e 150 — nenhum dos dois batia):

- **241 funções `def test_...`** escritas em `tests/` (15 arquivos).
- **279 casos** que o `pytest -q --collect-only` de fato coleta (a diferença
  vem de `@pytest.mark.parametrize`).
- **17 scripts `teste_*.py` soltos na raiz** (fora de `tests/`) — são testes
  manuais/exploratórios que geram relatório e imagem, não são coletados pelo
  pytest, e cada um cobre uma etapa ou bateria diferente. O principal para
  interface é o `teste_botoes.py` (clica em botões de verdade, via
  `botao.click()`/sinal `clicked` do Qt — não confundir com `teste_interface.py`,
  que dirige a lógica interna diretamente, sem clique real, e serve para outra
  coisa: validar o resultado de uma ação, não a fiação do botão).

---

## 5. O protocolo de qualquer mudança de imagem

**Medir antes — uma mudança por vez — medir de novo — reverter se qualquer
número piorar.**

Se parecer valer a pena mesmo assim, **não reverter sozinho**: registrar os dois
resultados e me apresentar.

Tudo que foi tentado, **inclusive o que falhou**, vai para
`relatorios/melhorias.md`. Isso existe para ninguém repetir caminho já fechado —
por exemplo, os cinco sinais medidos para separar escrita antiga de foto, em que
os números das duas se cruzam nos cinco.

---

## 6. Fronteira de autonomia

**Pode decidir sozinho:** limiar, janela, `k`, tamanho de bloco, ordem interna
de operações dentro de um filtro, troca de algoritmo de binarização, cache,
paralelismo, memória.

**Precisa perguntar antes:** criar ou remover filtro, mudar nome de filtro,
mudar qualquer tela, acrescentar ou tirar controle da interface, mudar o formato
dos arquivos de dados, alterar desfazer/refazer, trocar biblioteca.

---

## 7. Onde ficam as coisas

```
core/filtros.py            os quatro filtros
core/selecao.py             as regiões marcadas (gravura, letra, papel)
core/detectar_regioes.py    acha sozinho o que é o quê
core/rede_selecao.py        a rede neural de segmentação (só aponta, nunca desenha)
core/pipeline.py            dividir, cortar, endireitar, filtrar, impor
core/cadernos.py            imposição e conferência da sequência
core/analise.py             os alertas
projetos.py                 projetos salvos
avaliar.py                  a régua dos filtros
avaliar_selecao.py          a régua da seleção
conferir.py                 a tela de conferir amostras falando
teste_botoes.py              clica em botões de verdade, redimensiona a janela
PEDIDOS.md                  a lista de conferência — só o Samuel marca APROVADO
relatorios/melhorias.md     tudo que foi tentado, inclusive o que falhou
relatorios/para-conferir.html   a entrega padrão
```

Regra de arquitetura: **`core/` não importa nada de `ui/`.** Todo o
processamento tem que rodar por linha de comando, sem abrir janela.

**O modelo de dados — a decisão que mais importa.** São dois níveis, de
propósito:

- **`ConfigFolha`** = o que veio no PDF de entrada. Guarda `dividir`,
  `posicao_corte`, `confianca_corte`, `rotacao`, `angulo_detectado`, `apagada`,
  `e_paisagem`, `alertas`, `revisada`.
- **`ConfigPagina`** = o que vai sair no PDF final. Uma folha dividida vira
  **duas** páginas (`metade` = inteira/esquerda/direita). Guarda `filtro`,
  `recorte`, `angulo_manual`, `tem_cor`, `apagada`, e os três ajustes
  **separados** (`forca_preto`, `clareza_melhorar`, `intensidade_magico`, 0–100
  com 50 no meio) — separados porque trocar de filtro e voltar tem que devolver
  o ajuste daquele filtro, sem herdar o do outro.

Recorte e ângulo moram na **página**, não na folha, porque o pipeline os aplica
*depois* de dividir. As abas da tela de conferir seguem essa separação: "Onde
cortar" edita folhas, "Filtro" edita páginas.

**Onde o programa guarda estado:** `%LOCALAPPDATA%\EditorImpressao` —
`historico.json`, `configuracoes.json`, `erros.log`, e por projeto
`projeto.json`, `acoes.jsonl`, `posicao.json`. Fechar e reabrir preserva o
projeto **e o histórico de ações**. Desinstalar **não apaga** essa pasta, de
propósito.

**Desempenho já resolvido, não refazer:** a análise roda a 150 DPI (lombada,
ângulo e cor aparecem de sobra) — livro inteiro em segundos. O fundo dos filtros
é estimado numa miniatura de ~400 px e reescalado: mesmo resultado ~10× mais
rápido (5,0 s → 0,5 s por página a 300 DPI).

**Ordem obrigatória do processamento:**
`dividir folhas → cortar bordas → endireitar → filtro → montar cadernos`
Páginas apagadas são descartadas logo depois da etapa 1.

Comandos:

```
.venv\Scripts\python.exe main.py                 o programa
.venv\Scripts\python.exe -m pytest tests -q      os testes (279 casos)
.venv\Scripts\python.exe avaliar.py              a régua dos filtros
.venv\Scripts\python.exe avaliar_selecao.py      a régua da seleção
.venv\Scripts\python.exe conferir.py             conferir amostras falando
.venv\Scripts\python.exe teste_botoes.py         clica em botões de verdade, todas as telas
```

Acervo: `D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE
IMPRESSAO\LIVROS PARA TESTE` — nove livros, 2903 folhas. **Somente leitura.**
Mudou da área de trabalho para lá em 07/09/2026; `avaliar.py` acha sozinho.

As queixas do Kaique: `D:\programas\EditorImpressao-arquivos\BIBLIOTECA DO FIM
DOS TEMPOS\Teste de livros` — `.txt` soltos com um print ao lado. **São fonte
de requisito.**

**Handoff:** `historico/Editor de Impressao - resumo para o Claude.md` é o
mais completo e atualizado — leia primeiro numa sessão nova. Só atualize esse
arquivo (ou crie um novo) quando o Samuel pedir explicitamente.

---

## 8. O ciclo de uma mudança, do começo ao fim

1. Eu escolho um item do `PEDIDOS.md`.
2. O Claude Code mostra o diff e espera minha confirmação.
3. Faz a mudança. Uma só.
4. Roda os testes de máquina. Se algum quebrar, conserta antes de seguir.
5. Roda a régua nos PDFs de teste. Se qualquer número piorar, reverte — ou
   apresenta os dois resultados.
6. Abre **todas** as imagens.
7. Monta o `para-conferir.html` com a opinião e as ressalvas.
8. Marca o item como **PRONTO PARA CONFERIR** e me chama.
9. **Eu abro o programa pelo atalho, testo, e marco APROVADO, melhorar ou
   descartado.**
10. Commit com o defeito que resolveu escrito por extenso, e `git push` (o
    repositório tem GitHub remoto — não é preciso perguntar cada vez, mas
    sempre revisar o que está sendo commitado antes: nunca commitar segredo,
    nunca desfazer o `.gitignore` sem avisar).

---

## 9. O que já se sabe que está errado (não redescobrir)

- **A mancha do verso é o defeito mais grave aberto.** O Preto e branco não a
  remove — ele a escurece: no original é cinza fraco, depois do filtro vira
  marca preta legível. A régua não pega isso porque mede o fundo longe da tinta.
  Solução recomendada: o acervo tem as duas faces da mesma folha; espelhar o
  verso, alinhar sobre a frente e subtrair.
- **A régua precisa de dois critérios novos:** comparar na região onde havia
  mancha (não só no fundo limpo), e olhar a moldura da página (faixa escura nos
  últimos milímetros é fundo de scanner, nunca conteúdo). Falta um terceiro:
  medir sujeira guardada — o Otsu marca zero pioras mas guarda o dobro de tinta
  do Sauvola.
- **O amarelado não está no papel, está na tinta.** A tinta impressa de 1579 é
  marrom, e a orla de cada letra carrega essa cor. Cuidado: rubricação
  desbotada também é marrom.
- **Não existe binarizador vencedor único.** Os 18 do DoxaPy foram comparados em
  36 páginas. No Palatino o Otsu sai sólido e o Sauvola quebra o traço; noutras
  se inverte.
- **A receita difundida de "magic color" estraga capas coloridas.** Dividir por
  `GaussianBlur` canal a canal: numa área azul uniforme o próprio azul é o
  fundo, então a divisão lava a cor e desloca o matiz — o título azul virou
  vermelho no livro de teste. A correção já adotada em `core/filtros.py`:
  dividir pelo fundo **relativo ao nível do papel** com ganho igual nos três
  canais; **pesar** a correção por quanto o fundo local ainda parece papel; e
  branquear com **curva de ombro** no canal L do LAB, nunca multiplicação
  linear. **Não desfazer isso.**
- **Scan de baixa resolução não se recupera.** As páginas do Boécio já nascem
  fora da faixa saudável — 4 MB para 50 folhas. O remédio é reescanear. É o
  único ponto do projeto em que "até ficar perfeito" não se aplica.
- **A barra de rolagem não é mais preta.** Ficou quase-preta em 05/08 (a
  pedido do Kaique), e foi revertida para cinza médio (`#a8a49e`) em 08/08 —
  o preto puro lia como risco de erro atravessado no pé da tela. O estado
  atual (cinza) é intencional e documentado no próprio `ui/estilo.py`; não
  reverter sem decisão explícita do Samuel.
- **Achado em 07/09/2026, ainda não corrigido:** a ação "Abrir" do menu
  (`ui/janela_principal.py`, `_montar_menu`) está ligada a
  `lambda: self.tela_inicio.area.mousePressEvent(None)` — isso passa `None`
  como evento, e `AreaArrastar.mousePressEvent` começa lendo `evento.button()`,
  o que levanta `AttributeError` em tempo de execução. A ação fica habilitada
  em qualquer tela. Provável primeira falha que um teste de clique real no
  menu vai reportar. Correção sugerida: abrir o `QFileDialog` diretamente (ou
  expor um método público tipo `abrir_pelo_menu()`), não simular o evento de
  mouse. **Não corrigido ainda — mostrar o diff antes de mexer, por ser
  mudança de tela.**
