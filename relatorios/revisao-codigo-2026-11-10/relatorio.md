# Revisão do código: remendos parecidos com o do Girar (10/11/2026)

Ramo lido: `obra-2026-10-26` (a versão de teste), commit `bc766007`. Só leitura: nenhuma linha do programa nem dos testes mudou.
Quem fez: o agente revisor, a pedido da gerente, depois de o Samuel dizer: "se mudou a ferramenta, muda em todos os lugares." · "Eu não quero remendos nesse código, gambiarras [...] eu quero as praticas de um programador senior na hora de codar" (D-667, `CLAUDE.md` §11.10).

## Resumo em 5 linhas

1. O defeito do Girar não é o único: achei **17 remendos parecidos** (4 de gravidade alta, 9 média, 4 baixa).
2. O padrão é sempre o mesmo: a mesma ferramenta tem dois, três ou sete caminhos, e cada decisão nova ganhou um caminho novo em vez de mudar a regra.
3. Quatro já saem diferentes para quem usa: o **Girar**, as **figurinhas do Filtro** (mostram outra coisa que a página vai ter), o **"usar em todas"** (umas ferramentas protegem o que você fez à mão, outras apagam) e o **"não dividir" do Automático** (deixa a folha de um jeito diferente do botão da tela).
4. Os de gravidade média ainda não aparecem na tela, mas cada um é o lugar onde o próximo pedido vai virar outro remendo.
5. No fim há 10 regras de código propostas para os agentes e 4 perguntas para o Samuel.

## Os de gravidade alta (já sai diferente para quem usa)

- **A1. O Girar tem sete caminhos.** No Dividir com "Duas lado a lado" (Gradus, folha 10), "todas as folhas" gira as páginas 18 e 19 cada uma sozinha, mas "só as pares" gira a folha inteira com as duas juntas.
- **A2. As figurinhas do painel Filtro e o "comparar" da tela grande usam uma conta mais simples que a da página.** Numa página com gravura, a figurinha "Preto e branco" mostra a gravura virando mancha preta, mas ao escolher, a página sai com a gravura guardada.
- **A3. "Usar em todas" quer dizer uma coisa em cada ferramenta.** No Cortar, no Dividir e no Mover, as páginas que você mexeu à mão vêm desmarcadas e ficam como estão. No Marcar, o "usar em todas" apaga a gravura que você marcou à mão na página 12 e põe por cima as áreas da página onde você está.
- **A4. O Automático e o botão "não dividir esta" deixam a folha inteira de dois jeitos.** Pelo botão, a folha vira uma página só. Pelo Automático, fica uma página escondida "tirada do livro": o contador passa a dizer "1 apagadas" sem você ter tirado nada.

---

## Como li o código

- Li, pelo código de verdade, `ui/tela_conferir.py`, `ui/janela_principal.py`, `ui/tarefas.py`, `ui/tela_ampliada.py`, `ui/desfazer_nesta_pagina.py`, `core/pipeline.py`, `core/filtros.py`, `core/automatico.py`, `core/etapas.py`, `core/girar.py`, `core/dividir_a_mao.py`, `core/perfis.py` e `modelos.py`.
- Cada achado abaixo foi conferido lendo as linhas citadas. Nada de suspeita sem conferir.
- Um achado (A4) foi provado com um script curto, sem janela, com prioridade baixa e um `LOCALAPPDATA` à parte (script em "Prova do A4", no fim). Não rodei a suíte.
- As linhas são as do commit `bc766007`.

---

## Achados de gravidade ALTA

### A1. O Girar tem sete caminhos, um por decisão

**Onde:** `ui/tela_conferir.py` 6444-6756 (`_girar_folhas` e as seis funções que ela chama) e 7179-7268 (o girar da grade "Todas as páginas"); `core/girar.py` 236-491.

**O que faz hoje.** Para o mesmo clique em "girar", o programa escolhe um entre sete caminhos, cada um com a sua conta:

1. botões do canto e "só esta" numa página de folha dividida: gira só a página (`_girar_so_a_pagina`, D-618);
2. página de folha dividida com "todas / daqui em diante / pares / ímpares": conta **páginas**, gira cada uma sozinha (`_girar_as_paginas`, D-636) e ainda gira a capa inteira do grupo (`_com_as_folhas_inteiras_tambem`, D-640/D-645);
3. Dividir com "Duas lado a lado", folha dividida, **só "todas"**: vai pelo caminho 2, com outra página de referência (`_pagina_da_folha_dividida_no_dividir_em_duas`, D-662);
4. Dividir com "Duas lado a lado", folha dividida, "só esta / daqui em diante / pares / ímpares": gira a **folha** do scan com as duas páginas juntas (o caminho de antes da D-618);
5. folha inteira (a capa) com mais de uma folha no "aplicar em": as inteiras giram como folha, as divididas página por página (`_girar_as_divididas_pagina_por_pagina`, D-638);
6. folha inteira sem nenhuma dividida no alcance: o giro de sempre (`campos_do_giro`, D-035);
7. a grade "Todas as páginas": cada escolhida gira **a partir de onde está** (`_girar_as_escolhidas_que_sao_metade`), enquanto o painel faz todas ficarem **viradas como a da vez** (D-035). A grade ainda soma o giro da folha com outra fórmula (`(rotacao + giro) % 360`, linha 7196) em vez de `girar.nova_rotacao`.

O caminho é escolhido pelo **jeito de ver a tela** ("Uma página" ou "Duas lado a lado", linhas 6612 e 6691), e não pelo que a folha é.

**O que o Kaique vê.** Gradus, Dividir, "Duas lado a lado", folha 10 (páginas 18 e 19): com "todas as folhas" as duas páginas deitam cada uma sozinha. Com "só as pares", a folha 10 inteira deita, com as duas páginas juntas e com pedaço da vizinha: a confusão que o Samuel mostrou nos prints a-70 a a-73.

**Decisões que tocam aqui.** D-035 ("Todas ficam viradas como a folha da vez") · D-036 ("O programa avisa: 'vá a uma folha par'") · D-618 ("Ele gira as duas folhas ao mesmo tempo, faz uma confusão com as paginas") · D-636 ("1- pode ser, só garanta que não crie mais problemas fazendo isso") · D-638 ("Pode ser, mas isso vai acontecer se elas estiverem cortadas e se não estiverem cortadas né?") · D-640 ("vamos deixar como gira todas as paginas") · D-645 ("Giram também") · D-662 ("Página por página também") · D-666 ("Sim, os três também", ainda não construída) · D-667 ("se mudou a ferramenta, muda em todos os lugares").

**O jeito certo, em uma frase.** Uma regra só, em `core/girar.py`: "página de folha dividida gira sozinha, folha inteira gira como foto, e o 'aplicar em' só escolhe **quais** páginas entram", usada igual pelo painel, pelo menu, pelas teclas, pelos botões do canto, pelo Dividir e pela grade, sem olhar o jeito de ver a tela.

**Gravidade:** alta.

---

### A2. As figurinhas do Filtro e o "comparar" da tela grande não usam a conta da página

**Onde:** `core/pipeline.py` 3523-3547 (`filtro_com_as_caixinhas`); `ui/tarefas.py` 824-849 (a tarefa das figurinhas); `ui/tela_conferir.py` 4778-4862 e 5095-5116 (`_atualizar_cartoes`, `_imagem_sem_filtro`), e os dois desvios 4990-5026 (`_cartao_pb_pelo_misto`, `_cartao_do_misto`) e 4972 (`_cartao_sem_fundo`); `ui/tela_ampliada.py` 304-347 (`_imagem_do_outro_filtro`).

**O que faz hoje.** A página da tela e o PDF passam pela conta inteira (`_filtrar_a_pagina`, linha 3414): a marcação das gravuras, a caixinha "Respeitar as gravuras achadas", "Gravuras em tons de cinza", "Só as letras", "Igualar a luz", "Tirar o chuvisco" e "Suavizar as letras". As figurinhas dos **outros** filtros e o "comparar" da tela grande passam por uma conta à parte, `filtro_com_as_caixinhas`, que só sabe três caixinhas ("Letra clara em fundo escuro", "Letras com a cor delas", "Reduzir cores") e aplica o filtro na página inteira, sem a marcação.

Quando isso deu defeito, cada vez o conserto foi um desvio para um caso só: "Tirar o fundo" (item 1.1) e "Só as letras" (bug Misto 2, 05/10) vão pela conta de verdade (`renderizar_com_filtro`); todo o resto continua pela conta simples. O desvio do "Só as letras" foi posto só nas figurinhas: o "comparar" da tela grande não o tem (não há nenhuma linha sobre o Misto em `ui/tela_ampliada.py`). A tela cheia dos filtros já usa a conta de verdade (`ui/widgets/filtros_tela_cheia.py` 85-100). São três jeitos de mostrar "como fica com este filtro".

O "comparar" ainda faz o filtro na hora, na própria janela (linha 342), e o Preto e branco pode levar segundos numa página de traço fino (o próprio código diz isso na linha 4782).

**O que o Kaique vê.** Página com gravura, no "Melhorar": a figurinha "Preto e branco" mostra a gravura virando manchas pretas. Ele não escolhe o Preto e branco por causa disso, mas a página sairia com a gravura guardada (a caixinha "Respeitar as gravuras achadas" vem ligada). Com "Igualar a luz" ligada, nenhuma figurinha mostra a luz igualada. No "comparar" da tela grande, numa página com "Só as letras", o Preto e branco mostra a gravura em preto e branco e a página sai com ela em cor: o mesmo defeito que foi consertado só nas figurinhas.

**Decisões que tocam aqui.** D-066 ("precisamos que o pdf saia que nem está na tela") · D-473 ("Tela e PDF diferentes é defeito, nunca escolha") · D-547 (cartões do Filtro mostram como sai no PDF) · D-586 (a caixinha "Respeitar as gravuras achadas") · D-588 ("Gravuras em tons de cinza") · D-649 ("o resultado final tem que sair como a edição foi mostrada no preview").

**O jeito certo, em uma frase.** "Como fica esta página com o filtro X" tem uma conta só (a de `_filtrar_a_pagina`, numa cópia da página), feita por trás, e as figurinhas, o "comparar" e a tela cheia pedem todos a ela, menor se precisar.

**Gravidade:** alta.

---

### A3. "Aplicar em" e "usar em todas" querem dizer uma coisa em cada ferramenta

**Onde (`ui/tela_conferir.py`):**

| Ferramenta | Função (linha) | Pergunta "Em quais páginas?" | Respeita o que foi feito à mão |
|---|---|---|---|
| Cortar | `_recorte_em_todas` (6938) | sim | sim, vem desmarcada |
| Dividir (linha) | `_corte_em_todas` (6031) | sim, por folha | sim |
| Mover | `_mover_em_todas` (2556) | sim | sim |
| Filtro | `_filtro_em_todas` (9001), `_filtro_nas_proximas` (9038) | não, só "todas / daqui em diante" | não, troca o filtro de todas |
| Endireitar | `_mudar_o_angulo` (7007) | não, lista de 5 opções contadas em páginas | não |
| Girar | `_girar_folhas` (6444) | não, lista de 5 opções em folhas **ou** páginas (A1) | não |
| Marcar (marcação) | `_marcacao_em_todas` (3310), `_marcacao_nas_proximas` (3330) | não | **não: copia a marcação inteira por cima** |
| Marcar ("tem foto") | `_forma_nas` (3260) | não | não |

**O que faz hoje.** Cada ferramenta escreveu o seu "aplicar em". Três seguem a D-090 (a lista com as exceções desmarcadas). As outras sobrescrevem tudo. No Marcar, o "usar em todas" grava em todas as páginas uma **cópia da marcação desta página** (`{"selecao": copy.deepcopy(pagina.selecao)}`, linha 3325), com as áreas nos lugares desta página, e o que as outras páginas tinham marcado à mão some. O comentário do próprio Filtro (linha 9004) diz "nunca apaga exceção" (D-090/D-545), e o Marcar, logo acima, apaga.

**O que o Kaique vê.** Ele marca à mão a gravura da página 12. Vai à página 3, marca a letra capitular, aperta "usar em todas" no Marcar: a página 12 perde a gravura marcada e ganha um retângulo no lugar da capitular da página 3. No Cortar, o mesmo "usar em todas" teria deixado a página 12 desmarcada e como ele fez.

**Decisões que tocam aqui.** D-090 ("eu devo conseguir abrir uma aba para selecionar as que eu quero ( as paginas) ou também simplismente apertar num botão e selecionar todas") · D-091 ("'Selecionar todas' e 'Nenhuma'") · D-545 (o Mover) · D-367 (as palavras "folha" e "página" da lista).

**O jeito certo, em uma frase.** Um "aplicar em" só (quais páginas, e como as mexidas à mão são tratadas), escrito uma vez e chamado por todas as ferramentas, que só dizem **o que** levam. Se o Samuel quiser que alguma ferramenta se comporte diferente, isso vira uma escolha escrita, não um jeito por acidente (ver Pergunta 1).

**Gravidade:** alta. **Contra decisão?** O Marcar apaga trabalho feito à mão, e o próprio programa promete que isso não acontece: vira a Pergunta 1.

---

### A4. O Automático e o "não dividir esta" deixam a folha inteira de dois jeitos

**Onde:** `core/automatico.py` 952-956 (`_dividir`) e `core/dividir_a_mao.py` 267-294 (`campos_para_juntar`); contador em `modelos.py` 885 (`total_apagadas`) e `ui/tela_conferir.py` 5673-5682.

**O que faz hoje.** Desde a etapa 4 da obra, "não dividir esta" troca as duas páginas da folha por **uma** página inteira e guarda as duas para o "dividir esta" devolver. O Automático, quando mede uma folha que já tinha duas páginas e acha que ela é de uma página só, ainda usa o jeito de antes da etapa 4: deixa as duas na lista e marca a da direita como **"tirada do livro"** (`g.na_pagina(direita, "apagada", not medida.dividir)`). O comentário da função diz "como o 'não dividir esta' da ferramenta", e isso deixou de ser verdade na etapa 4. O próprio `ui/tela_conferir.py` (linha 6104) conta que esse jeito antigo "mostrava a folha duas vezes".

**Prova** (script no fim, sem janela):

```
A MAO : 1 paginas na lista; [('inteira', False)] ; ativas: 1
AUTO  : 2 paginas na lista; [('esquerda', False), ('direita', True)] ; ativas: 1
```

O PDF sai igual (uma página), mas a tela não.

**O que o Kaique vê.** Ele roda o Automático com o Dividir num livro já dividido, e a capa é medida como de uma página só. O contador passa a dizer "… 1 apagadas" sem ele ter tirado nada; "página N de M" conta uma página a mais; a página escondida aparece como "tirada" na grade e pode ser "trazida de volta". Se ele tivesse apertado "não dividir esta", nada disso aconteceria.

**Decisões que tocam aqui.** D-590 ("pode ser assim": "juntar todas"; "desmarcar o Dividir no Automático não junta nada") · D-498 (a folha juntada guarda as duas páginas) · D-605 ("nenhuma função nova [...] pode alterar o que já está escolhido e testado").

**O jeito certo, em uma frase.** "Juntar uma folha" mora num lugar só (`core/dividir_a_mao`), e o Automático chama a mesma função que o botão.

**Gravidade:** alta.

---

## Achados de gravidade MÉDIA (vai dar defeito no próximo pedido)

### M1. Seis caminhos para gravar uma mudança no Histórico, cada um com um pedaço dos passos

**Onde:** `ui/tela_conferir.py` 5816 (`_registrar`, o caminho "oficial"), 3097 (`_registrar_a_marcacao`), 2261 (`_gravar_no_livro`), 9328 (`_aceitar_avisos`); `ui/desfazer_nesta_pagina.py` 182-223; `ui/janela_principal.py` 924-962 (`_tirar_o_fundo_do_livro_inteiro`); `core/automatico.py` 827 (`aplicar`).

**O que faz hoje.** `_registrar` faz cinco coisas: espera as marcações antigas serem convertidas, grava a marca "mexida à mão", guarda os avisos de agora (para o Ctrl+Z devolvê-los), aplica, e joga fora as prévias. Os outros caminhos copiam só parte disso. O "Desfazer nesta página" copia o `_registrar` à mão ("É o caminho do TelaConferir._registrar, sem a marca automática dele") e chama 3 funções internas da tela. O "Tirar o fundo" da pergunta do fundo e o "está bom" (`_aceitar_avisos`) pulam o `_registrar`. O "está bom" diz por quê: o `_registrar` sempre joga fora as prévias e refaria todas. Isso é remendo do sintoma: o certo seria o `_registrar` saber quais campos mudam a imagem (ele já tem uma exceção à mão para o Mover, `CAMPOS_SO_DO_MOVER`, linha 9908).

**O que o Kaique vê.** Nada visível comprovado hoje. Mas cada passo novo que alguém puser no `_registrar` (como foi a D-020 dos avisos) não vale nos outros cinco caminhos, e o defeito aparece só ali.

**Decisões.** D-020 ("Ctrl+Z desfaz qualquer alteração, sem limite de quantidade"); D-004 e D-009 (a marca "mexida à mão").

**O jeito certo.** Um caminho só para gravar mudança, que recebe "esta mudança muda a imagem?" e "marca como mexida à mão?" como informação da mudança, sem ninguém ter de copiar o caminho.

**Gravidade:** média.

---

### M2. "Como sai no PDF" está escrito três vezes, e a prévia e o PDF são duas listas de passos feitas à mão

**Onde:** `core/pipeline.py` 4778-4812 (o PDF: margens iguais e depois a folha escolhida), `ui/tela_conferir.py` 4881-4921 (`_como_sai_no_pdf`) e `core/automatico.py` 1280-1299 (`como_sai_na_tela`, que diz ser "A MESMA conta da tela de conferir"). E `core/pipeline.py` 2791 (`renderizar_pagina`, a prévia) contra 4711 (`_pagina_pronta`, o PDF), dois roteiros dos mesmos passos ("a conta e a mesma, linha por linha", linha 4717), que já não são iguais (só a prévia mede o "parece em branco", linha 2852).

**O que o Kaique vê.** Nada visível comprovado hoje. Quando alguém mudar a composição num lugar (ex.: a D-649, "a miniatura mostrava o título no lugar e o PDF saía sem ele", ainda a fazer), os outros dois ficam do jeito antigo.

**Decisões.** D-473, D-547, D-649.

**O jeito certo.** Uma função em `core/` faz "a página pronta" (filtro, margens, folha), e a prévia, a tela de conferir, o Automático e o PDF a chamam, mudando só a resolução.

**Gravidade:** média.

---

### M3. A prévia lê o livro enquanto a tela muda o livro (e o conserto de 09/11 tratou o sintoma)

**Onde:** `ui/tarefas.py` 947-981 (a tarefa da prévia, num fio por trás, usa `self.projeto`, o livro aberto, e não uma cópia); `core/pipeline.py` 2866-2917 (`_resolucao_para_a_procura`, o conserto de 09/11).

**O que faz hoje.** A prévia é desenhada por trás lendo a página "ao vivo", e ainda escreve nela (avisos, marcação provisória, zonas). Se a pessoa muda a página no meio do desenho, metade do desenho vê o valor velho e metade vê o novo. Em 09/11 isso fez aparecer o aviso falso "o detector de gravuras falhou". O conserto não tirou a causa (ler o livro ao vivo): pôs uma conta "preguiçosa" da resolução guardada no fio, só para esse caso. A prévia do Automático, ao contrário, desenha numa cópia (`copy.deepcopy`, linha 743): dois jeitos no mesmo arquivo.

**O que o Kaique vê.** Hoje, nada (o desenho velho é jogado fora e o aviso foi consertado). Amanhã, qualquer outro valor lido no meio do desenho pode dar outro aviso falso, e vai ganhar outro remendo.

**Decisões.** D-659 (o conserto de 09/11 nasceu dela); CLAUDE.md §3 ("Interface nunca congela").

**O jeito certo.** A tarefa da prévia recebe uma cópia da página e do que ela precisa no momento do pedido, como a do Automático e a das figurinhas já fazem, e devolve os avisos para a tela gravar no fio da janela.

**Gravidade:** média.

---

### M4. Trocar o motor de corte numa folha dividida mede sem pintar a tampa do scanner

**Onde:** `core/pipeline.py` 461-476 (`recalcular_divisao`, usada em `ui/tela_conferir.py` 6416) contra `core/dividir_a_mao.py` 589-628 (`ler_a_linha`, usada pela linha azul, pelo "dividir esta" e pelo "dividir todas").

**O que faz hoje.** São duas contas de "onde fica a linha desta folha". A de `ler_a_linha` pinta de branco a faixa preta da tampa do scanner antes de procurar a linha (D-495/D-559) e avisa no comentário: "Arriscado: mudar a imagem lida (DPI, giro, tampa) só aqui - a linha mostrada deixaria de ser a do 'dividir esta'". A de `recalcular_divisao` não pinta a tampa. A folha **inteira** usa a primeira; a folha **dividida**, ao trocar o motor, usa a segunda.

**O que o Kaique vê.** Num livro com a faixa preta da tampa (ex.: o Righetti), o mesmo motor pode pôr a linha num lugar na folha inteira e em outro na folha já dividida. Não provei num livro: conferido lendo as duas funções.

**Decisões.** D-495 / D-559 (a tampa), D-602 ("o programa deveria carregar com a conta que está escolhida"), D-606 ("Ele deve fazer a conta novamente com o novo motor").

**O jeito certo.** Uma conta só para "a linha desta folha com este motor" (`ler_a_linha`), chamada também ao trocar o motor.

**Gravidade:** média.

---

### M5. Dividir: três caminhos que tratam a linha arrastada de jeitos diferentes

**Onde:** `ui/tela_conferir.py` 6302-6356 ("dividir esta"), 6275-6299 ("dividir todas"), 7285-7336 (o "dividir" da grade "Todas as páginas", que manda medir de novo por `dividir_a_mao.medir_para_dividir`).

**O que faz hoje.** O "dividir esta" e o "dividir todas" cortam na linha que a pessoa arrastou (D-609). O "dividir" da grade sempre mede de novo, com a conta forçada, e não olha a linha arrastada. O comentário do bloco (linhas 7276-7279) diz "pela MESMA conta do 'dividir esta'", e isso deixou de ser verdade quando a D-609 entrou só nos outros dois.

**O que o Kaique vê.** Ele arrasta a linha da folha 5 no Dividir, vai à grade, escolhe a página dessa folha e aperta "dividir": a folha é cortada na linha do motor, não onde ele deixou.

**Decisões.** D-558 (o "dividir" na grade), D-602, D-609 ("'dividir esta' corta onde a linha ficou"), D-667.

**O jeito certo.** Uma função "a linha com que esta folha vai ser cortada" (a arrastada, a de antes ou a do motor), usada pelos três botões.

**Gravidade:** média. **Contra decisão?** A D-609 fala só do "dividir esta"; vira a Pergunta 3.

---

### M6. A página girada sozinha (D-618) não chegou a todos os lugares

**Onde:** `ui/tela_conferir.py` 10000-10029 (`MARCAS_DA_PAGINA`, sem `giro_da_pagina`); `core/etapas.py` 100-103 (`GIRAR` só existe para a folha); `ui/janela_principal.py` 1644 (a capa do cartão segue só `folhas[0].rotacao`); `ui/tela_conferir.py` 7035-7066 e 8703-8739 (duas cópias da conta do tamanho da página, cada uma recebeu o seu "# D-618: a pagina deitou", e já diferem num limite: `min(0.95, parte)` só numa).

**O que faz hoje.** Quando o giro de uma página passou a morar na página (D-618), ele entrou em cada lugar por cópia. Faltaram: a marca "mexida à mão" (girar uma página sozinha não conta como mexida), e a capa do cartão na tela inicial (só acompanha o giro da folha 1 inteira).

**O que o Kaique vê.** Se a capa é metade de uma folha dividida e ele a gira sozinha, a capa do livro na tela inicial continua em pé. O resto, nada visível hoje.

**Decisões.** D-618, D-004, D-667.

**O jeito certo.** Uma pergunta só, "quanto esta página está girada no fim" (folha + página), em `core/girar.py`, usada pela marca, pela capa, pelas contas de tamanho e pela tira.

**Gravidade:** média.

---

### M7. "Página em branco posta à mão" (D-623) é conferida em 31 lugares

**Onde:** 31 testes `getattr(p, "inserida", 0)` e parecidos, em 8 arquivos (`ui/tarefas.py`, `ui/tela_conferir.py`, `core/automatico.py`, `core/dividir_a_mao.py`, `core/ordem_das_paginas.py`, `core/paginas_em_branco.py`, `core/pipeline.py`, `modelos.py`); 30 citações da D-623. Ex.: `core/pipeline.py` 3406, `core/automatico.py` 389, 943, 1697, 1714, 1742; `ui/tela_conferir.py` 4817.

**O que faz hoje.** Em vez de a página posta à mão ser um tipo de página que já sai branca e não pertence a nenhuma folha, cada função que lida com páginas ganhou o seu `if` para ela.

**O que o Kaique vê.** Nada visível hoje. A próxima ferramenta que lidar com páginas (ou a próxima mudança numa delas) tem 31 lugares para lembrar; esquecer um é um defeito novo, como o "defeito B do verificador" da linha 4817.

**Decisões.** D-623.

**O jeito certo.** A regra "página posta à mão" mora num lugar (`core/paginas_em_branco`), com perguntas como "esta página vem de uma folha?", e as outras funções usam essas perguntas.

**Gravidade:** média.

---

### M8. Erros engolidos onde o defeito devia aparecer

**Onde e o que cada um esconde:**

- `core/pipeline.py` 2637-2643: "Tirar o fundo" deu erro → a página sai **como veio**, só no registro de erros. A frase "Não consegui tirar o fundo desta página; ela sai como veio." é montada, mas não vira aviso: o "conferir" fica falso (linha 4730) e nada entra no "Para revisar".
- `core/pipeline.py` 2517-2519: a procura de gravura deu erro → o filtro trata a folha toda (a gravura pode virar mancha preta no PDF), só no registro. O detector tem um aviso de "uma vez por sessão" (`core/detectar_regioes.py` 1306), mas este erro de fora não passa por ele.
- `ui/tela_conferir.py` 4919-4921 e `core/automatico.py` 1298-1299: se a conta "como sai no PDF" falha, a tela mostra a página **sem** a composição, e o PDF sai **com** ela; no Automático nem vai para o registro.
- `ui/tarefas.py` 848-849: figurinha que falha fica "preparando..." para sempre.

**O que o Kaique vê.** No primeiro caso: ele escolhe "Tirar o fundo", o PDF sai com o fundo numa página, e nada no programa diz isso.

**Decisões.** D-473 ("Tela e PDF diferentes é defeito, nunca escolha"); CLAUDE.md §3 ("Nenhuma exceção fecha a janela. Vira aviso em português").

**O jeito certo.** Erro que muda o que sai no PDF vira aviso da página no "Para revisar" (como o "conferir" já é), em vez de só ir para o registro.

**Gravidade:** média.

---

### M9. A lista "o que é do filtro" está escrita à mão em pelo menos seis lugares, e já diverge

**Onde:** `ui/tela_conferir.py` 9010-9033 e 9047-9070 (`_filtro_em_todas` e `_filtro_nas_proximas`: o mesmo dicionário copiado e colado), 10000-10029 (`MARCAS_DA_PAGINA`); `core/automatico.py` 146-151 (`CAMPOS_DA_PAGINA`); `core/perfis.py` 60-66 (a receita); `ui/widgets/filtros_tela_cheia.py` 620-629; `ui/tarefas.py` 1135-1196 (a chave das prévias: cada campo entrou à mão, e o próprio comentário lembra o defeito de 21/10, quando faltou um).

**O que faz hoje.** Cada lugar diz por conta própria quais campos são "do filtro". Já diverge: "Letra clara em fundo escuro" vai junto no Automático ("Limpar a folha") e na receita, mas **não** no "Aplicar em" do painel Filtro.

**O que o Kaique vê.** Ele marca "Letra clara em fundo escuro" na página 5 e aperta "todas" no painel Filtro: as outras páginas ganham o filtro, mas não a caixinha. Se fizesse o mesmo pelo Automático, ganhariam (ver Pergunta 2). E quem acrescentar uma opção nova ao filtro tem seis lugares para lembrar.

**Decisões.** D-177 ("Uma caixinha por página, 'Letra clara em fundo escuro'"), D-586 e D-588 ("Vale com o 'Aplicar em'"), D-594 (as opções do Filtro no Automático).

**O jeito certo.** Uma lista só, em `core/`, "os campos do filtro da página" (com o que cada um precisa), usada pelo painel, pelo Automático, pela receita, pela tela cheia, pela marca e pela chave das prévias.

**Gravidade:** média.

---

## Achados de gravidade BAIXA (arrumação)

### B1. O jeito de desenhar escolhido por um pedaço de texto da chave

`ui/tarefas.py` 944 (`if ":recorte:" in self.chave`) e 952 (`if MARCA_DA_MEDIDA in self.chave`): a tarefa da prévia decide o que fazer procurando um pedaço de texto dentro da chave do guardado. Nada visível hoje; uma chave nova que contenha esse texto por acaso mudaria o desenho. **Jeito certo:** o pedido diz o que quer num campo próprio. **Gravidade:** baixa.

### B2. A tela de conferir é um arquivo de 10.041 linhas com 406 funções e estado espalhado

`ui/tela_conferir.py`: a classe `TelaConferir` vai da linha 649 ao fim; 374 citações de decisão; 19 lugares guardam estado com `getattr(self, "_algo", None)` (ex.: `_tarefa_de_dividir`, `_caixa_de_dividir`, `_tarefa_de_dividir_todas`, duas tarefas quase iguais com caixas quase iguais, 6156-6273 e 7285-7368). `_tamanhos_das_folhas` é a mesma memória usada por duas funções que a leem de jeitos diferentes (7035 e 8703). Nada visível hoje; é o motivo de cada decisão nova virar um `if` aqui dentro. **Jeito certo:** as regras das ferramentas vão para `core/` (como o `core/girar.py` começou), e a tela só chama. **Gravidade:** baixa.

### B3. Duas perguntas "mexida à mão?"

`core/etapas.py` 170 (`mexida_a_mao`) e `core/automatico.py` 382 e 416 (`_filtro_trocado_na_pagina`, uma regra a mais que só a pergunta do Automático usa). Está explicado no comentário (projeto antigo), mas são duas respostas para a mesma pergunta. **Jeito certo:** a regra a mais mora dentro de `core/etapas`. **Gravidade:** baixa.

### B4. Erros escondidos na janela principal

`ui/janela_principal.py` 1898-1899 (`except Exception: return`, sem registro) e 1928-1929 (`folhas_de_saida = 0` sem registro: a tela "Ficou pronto!" pode dizer 0 páginas sem ninguém saber por quê). **Jeito certo:** todo erro engolido vai pelo menos para o `erros.log`. **Gravidade:** baixa.

---

## Regras de código para os agentes (proposta para o Samuel aprovar)

São uma proposta. Nada foi mudado no `CLAUDE.md`. Cada regra diz o que fazer, por que, e um exemplo tirado dos achados acima.

1. **Uma ferramenta, uma regra, num lugar só.** A regra de cada ferramenta (girar, cortar, dividir, filtro, marcar, mover, desfazer) mora numa função de `core/`, e a tela, o menu, as teclas, a grade, a tela grande e o Automático só a chamam. *Por quê:* se cada botão tem a sua conta, mudar a ferramenta exige achar todos os botões, e um sempre fica de fora. *Exemplo:* A1, o Girar com sete caminhos.

2. **Nada de desvio por decisão, por tela ou por opção.** É proibido acrescentar `if` do tipo "se for o Dividir e for 'todas as folhas', vai por aqui". Se uma decisão nova muda a ferramenta, muda-se a regra, e todas as opções passam a segui-la. *Por quê:* cada desvio deixa as outras opções do jeito antigo, e o próximo pedido vira outro desvio. *Exemplo:* A1 (D-662 feita só no "todas"); A2 (o "Só as letras" consertado só nas figurinhas).

3. **A tela, a prévia, as miniaturas e o PDF usam a mesma conta.** O que muda é só o tamanho da imagem. Nunca escrever uma "conta parecida" para a tela. *Por quê:* D-473, "Tela e PDF diferentes é defeito, nunca escolha". *Exemplo:* A2 (figurinhas), M2 ("como sai no PDF" escrito três vezes).

4. **Uma lista, um lugar.** Lista de campos, de etapas, de opções: escrita uma vez, em `core/`, e importada. Nunca copiar e colar um dicionário. *Por quê:* cópias divergem sem ninguém ver. *Exemplo:* M9 (os campos do filtro em seis lugares, já diferentes); `_filtro_em_todas` e `_filtro_nas_proximas`, iguais linha por linha.

5. **Consertar a causa, não o sintoma.** Antes de consertar, escrever no ONDE-PAREI **por que** o defeito aconteceu. Se o conserto só evita que o sintoma apareça naquele caso, não é conserto. *Por quê:* remendo do sintoma deixa a causa pronta para outro defeito. *Exemplo:* M3 (a prévia lê o livro ao vivo; o conserto de 09/11 só tratou o aviso); M1 (o "está bom" pula o `_registrar` em vez de o `_registrar` saber que a imagem não mudou).

6. **Nunca engolir erro que muda o que sai.** `except Exception` só onde a falha não muda o PDF (uma bolinha, um enfeite), e sempre com registro no `erros.log`. Se a falha muda a página que sai, vira aviso da página no "Para revisar". *Por quê:* o Kaique não lê o registro de erros; se a página sai diferente, ele precisa saber. *Exemplo:* M8 (o "Tirar o fundo" que falha e a página sai como veio, calada).

7. **Mudou a ferramenta: listar todos os lugares antes de codar, e provar cada um.** Antes de mexer, procurar com `grep` todos os lugares que usam o campo ou a função (as opções da lista, as telas, a grade, a tela grande, o Automático, a tira, o PDF) e escrever essa lista no ONDE-PAREI. A entrega tem um teste para cada lugar. *Por quê:* D-667, "se mudou a ferramenta, muda em todos os lugares". *Exemplo:* M6 (a D-618 ficou de fora da marca "mexida à mão" e da capa do cartão); M5 (a D-609 ficou de fora da grade).

8. **Mudança grande vem com o plano antes.** Se a mudança mexe em mais de uma ferramenta, junta caminhos ou tira código, o agente escreve o plano (o que junta, o que sai, o que o Kaique vê antes e depois, quais testes provam que nada mudou) e espera a aprovação antes de codar. *Por quê:* juntar os sete caminhos do Girar ou as três contas das figurinhas mexe em coisas já testadas pelo Samuel (D-605). *Exemplo:* A1, A2, A3.

9. **Um dado, um jeito de guardar.** A mesma situação do livro (ex.: "folha não dividida") é sempre guardada do mesmo jeito, por qualquer caminho que a crie. *Por quê:* dois jeitos fazem a tela contar diferente. *Exemplo:* A4 (o Automático deixa uma página "tirada" escondida; o botão deixa uma página só).

10. **O comentário diz a verdade, ou sai.** Quando o código muda, os comentários que dizem "é a mesma conta de…" ou "como o botão X" são conferidos na hora. *Por quê:* o próximo agente confia no comentário e não confere. *Exemplo:* A4 ("como o 'não dividir esta'", falso desde a etapa 4); M5 ("pela MESMA conta do 'dividir esta'", falso desde a D-609).

---

## Perguntas para o Samuel

1. **"Usar em todas" no Marcar, no Filtro, no Endireitar e no Girar.** No Cortar, no Dividir e no Mover, as páginas em que você mexeu à mão vêm desmarcadas e ficam como estão (D-090). No Marcar, o "usar em todas" apaga a gravura que você marcou à mão nas outras páginas. Essas quatro também deveriam deixar de fora as páginas mexidas à mão? (Sugestão do revisor: sim, igual ao Cortar.)
2. **"Letra clara em fundo escuro" e o "Aplicar em".** Pelo Automático, essa caixinha vai para todas as páginas escolhidas; pelo "todas" do painel Filtro, não vai. Ela deve ir junto no "todas" do painel? (Sugestão: sim, igual ao Automático.)
3. **Dividir pela grade "Todas as páginas".** Se você arrastou a linha de uma folha no Dividir e depois a divide pela grade, ela deve ser cortada onde você deixou a linha, como no "dividir esta"? (Sugestão: sim.)
4. **Girar pela grade "Todas as páginas".** Na grade, cada página escolhida gira a partir de onde está. No painel, todas ficam viradas como a página da vez (D-035). A grade deve seguir o painel? (Sem sugestão: é a escolha dele.)

---

## Prova do A4

Script `prova/juntar.py`, rodado com `.venv\Scripts\python.exe`, `nice -n 19`, `QT_QPA_PLATFORM=offscreen` e um `LOCALAPPDATA` à parte, sem abrir janela:

```python
p = livro()   # 1 folha dividida, paginas esquerda e direita
campos = D.campos_para_juntar(p, 0)                      # "nao dividir esta"
acao = montar_acao(p, "nao_dividir", "folha", [0], campos, "x"); aplicar(p, acao, acao.depois)
# -> 1 pagina na lista: inteira

p = livro()
m = A.MedidaDaFolha(indice=0, dividir=False, ...)        # o Automatico acha "uma pagina so"
A._dividir(p, A.Pedido(etapas=[A.DIVIDIR]), {0: m}, A._Puladas(p, []), A._Gravador(p))
# -> 2 paginas na lista: esquerda e direita "tirada do livro"
```
