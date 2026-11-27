# Parte A: as regras de hoje e o destino de cada uma (27/11/2026)

**Em uma frase:** das 158 regras escritas hoje para os agentes, 46 são jeito de fazer (viram skill), 40 o computador já
confere ou pode conferir lendo o código em segundos, 24 são contexto que fica no CLAUDE.md, 16 valem só para certas
pastas, 13 precisam do programa rodando no GitHub, 10 são coisas que o agente simplesmente não deveria poder fazer, 2
viram ação automática num momento fixo, 2 podem sair e 5 dependem do Samuel.

Feito pelo agente da triagem, só lendo (D-887). Nenhum arquivo do projeto mudou. Nenhuma regra nova: a coluna "destino"
diz para onde cada regra que já existe iria, não o que construir.

## De onde veio a lista

- **As 158 regras** são as do catálogo das regras (`regras_dos_agentes/catalogo.py`, R001 a R158, feito em 18-19/11,
  D-784), conferidas contra o texto de hoje: o `CLAUDE.md` desta cópia (819 linhas, ramo `obra-2026-10-26`) não muda
  desde 18/11 (`fc2a0c53`) e os quatro arquivos de agente desde 18/11 (`afa68e46`), antes do catálogo (19/11). Os
  quatro arquivos de agente são iguais na pasta principal e nesta cópia.
- **Os dois CLAUDE.md** são iguais, menos um trecho do §10.10 (linhas 562-603 do de 859): a aba Respostas, o "responder
  de novo", o modelo de print do girar e o celular da Central só estão no de 859 linhas (ramo `fase-1`). Na tabela:
  R082, R083, R085 e parte da R084. Todas as outras regras estão nos dois.
- **O porteiro** (`regras_dos_agentes/porteiro.py`), a **lista de exceções**, o **gancho antes do commit**
  (`ganchos/pre-commit`) e a **skill** (`.claude/skills/conferir-testes-visuais/`) estão nas seções do fim.

## Como ler

- **nº**: o número do catálogo (R001...). **onde**: CLAUDE = CLAUDE.md; impl, verif, pesq, layout = os arquivos dos
  agentes; Livro = só no Livro de decisões.
- **desde e por quê**: a data e o erro que a motivou, quando o texto diz.
- **teste · cópias**: o teste que já cobre (arquivo em `tests/`; "(K..)" = a conferência do porteiro) e em quantos
  lugares a regra está escrita. "contradição X.." = o catálogo achou outro texto que diz diferente.

## Contagem por destino

| destino | quantas | o que quer dizer aqui |
|---|---|---|
| SKILL | 46 | jeito de fazer: como escrever ao Samuel (§11.13), pilotar a janela, Central, pesquisa, imagem |
| FISCAL RÁPIDO | 40 | 34 já são cobradas por uma conferência do porteiro (K01 a K25); 6 dariam para ter (segredo no commit, as duas cópias do plano, decisão sem dono, e as três de "um lugar só") |
| FICA NO CLAUDE.md | 24 | contexto: o Kaique, o livro, a máquina, quem manda, princípios |
| REGRA POR PASTA | 16 | imagem (`core/filtros`...), tela (`ui/`), modelo de dados, Windows |
| FISCAL GITHUB | 13 | memória, janela que não congela, velocidade, provas das decisões, Windows de verdade |
| PERMISSÃO | 10 | acervo, apagar fora, gravar fora da cópia, instalar no .venv, fechar processo alheio |
| DÚVIDA | 5 | quatro presas a contradições sem resposta (X3, X9) e uma talvez vencida (V2) |
| GANCHO | 2 | ler a memória ao abrir o agente; avisar a gerente quando aparece pergunta nova |
| APAGAR | 2 | a do plano de layout (vencida) e a que só repete "sem gambiarra vale para tudo" |
| **total** | **158** | |

## A tabela

| nº | regra | onde | desde e por quê | destino | motivo | teste · cópias |
|---|---|---|---|---|---|---|
| R001 | Ordem de leitura e quem manda | CLAUDE topo; impl; verif; pesq; layout | 24/09 (o plano manda); item 0 em 26/10 | **FICA NO CLAUDE.md** | contexto: quem manda; falta acertar a ordem (contradição X10, sem resposta) | — · 5 lugares; contradição X10 |
| R002 | PEDIDOS.md e handoff são histórico | CLAUDE topo; CLAUDE §7 | 24/09 (o plano manda); item 0 em 26/10 | **FICA NO CLAUDE.md** | contexto de uma linha; a 2ª cópia no §7 pode sair | — · 2 lugares |
| R003 | Tela em português sem jargão | CLAUDE §1; layout | 07/09 (duas versões fracassaram) | **FICA NO CLAUDE.md** | quem é o Kaique não se lê no código; botão em inglês já tem fiscal | test_botoes_em_portugues.py (em parte) · 2 lugares |
| R004 | Critério final do livro | CLAUDE §1 | 07/09 (duas versões fracassaram) | **FICA NO CLAUDE.md** | o critério do livro, contexto que vale sempre | — · 1 lugar |
| R005 | Não recomeçar do zero | CLAUDE §2 | 07/09; 'claro e direto' 29/10 | **FICA NO CLAUDE.md** | jeito de trabalhar, não se confere lendo código | — · 1 lugar |
| R006 | Uma mudança por vez | CLAUDE §2; CLAUDE §8 passo 3; impl | 07/09; 'claro e direto' 29/10 | **DÚVIDA** | a obra (D-014) e a D-765/D-885 suspendem; contradição X9 sem resposta | — · 3 lugares; contradição X9 |
| R007 | Planejar antes; perguntar antes de mexer em estrutura | CLAUDE §2 | 07/09; 'claro e direto' 29/10 | **SKILL** | procedimento: vai no modelo da ordem de serviço (Parte C) | — · 1 lugar |
| R008 | Ir até o fim dentro da alçada | CLAUDE §2 | 07/09; 'claro e direto' 29/10 | **FICA NO CLAUDE.md** | jeito de trabalhar | — · 1 lugar |
| R009 | Primeiro a frase, depois o número | CLAUDE §2; impl; verif; pesq; layout; CLAUDE §11.13.7 | 07/09; 'claro e direto' 29/10 | **SKILL** | jeito de escrever para o Samuel; 6 cópias viram uma skill | — · 6 lugares |
| R010 | Conciso: essencial no chat, detalhe em arquivo | CLAUDE §2 | 07/09; 'claro e direto' 29/10 | **SKILL** | idem (escrever para o Samuel) | — · 1 lugar |
| R011 | Claro e direto com o Samuel | CLAUDE §2; CLAUDE §11.13.7 | 07/09; 'claro e direto' 29/10 | **SKILL** | idem (escrever para o Samuel) | — · 2 lugares; contradição X11 |
| R012 | Honesto: avisar erro e risco | CLAUDE §2 | 07/09; 'claro e direto' 29/10 | **FICA NO CLAUDE.md** | princípio, não se confere | — · 1 lugar |
| R013 | Não inventar detalhe | CLAUDE §2 | 07/09; 'claro e direto' 29/10 | **FISCAL RÁPIDO** | K20 já compara as palavras citadas com o Livro, letra por letra | test_conferencias_formulario.py (K20) · 1 lugar |
| R014 | Relatório em três formatos | CLAUDE §2; CLAUDE §8 passo 7; verif | 07/09; 'claro e direto' 29/10 | **FISCAL RÁPIDO** | K09 já acusa .md sem .html/.pdf | test_conferencias_mudancas.py (K09); test_relatorio.py · 3 lugares |
| R015 | PySide6, nunca tkinter | CLAUDE §3; layout | 07/09 (cicatrizes das versões antigas) | **FISCAL RÁPIDO** | K07 já acusa tkinter | test_conferencias_codigo.py (K07) · 2 lugares |
| R016 | Uma página por vez na memória | CLAUDE §3 | 07/09 (cicatrizes das versões antigas) | **FISCAL GITHUB** | só se prova abrindo livro grande | test_memoria_nao_cresce_com_o_livro.py · 1 lugar |
| R017 | A janela nunca congela | CLAUDE §3; layout | 07/09 (cicatrizes das versões antigas) | **FISCAL GITHUB** | só se prova com o programa rodando | test_gravar_pdf_sem_parar_a_janela.py (em parte) · 2 lugares |
| R018 | Nenhuma exceção fecha a janela | CLAUDE §3 | 07/09 (cicatrizes das versões antigas) | **FISCAL GITHUB** | só se prova clicando em tudo (teste_botoes.py) | teste_botoes.py (no GitHub) · 1 lugar |
| R019 | Nenhum emoji em rótulo | CLAUDE §3; layout | 07/09 (cicatrizes das versões antigas) | **FISCAL RÁPIDO** | K05 já acusa emoji em texto de tela | test_conferencias_codigo.py (K05) · 2 lugares |
| R020 | Texto com acento, caminho sem acento | CLAUDE §3 | 07/09 (cicatrizes das versões antigas) | **FISCAL RÁPIDO** | K08 acusa nome de arquivo com acento; texto sem acento não tem fiscal | test_conferencias_codigo.py (K08) · 1 lugar |
| R021 | Algoritmo consagrado | CLAUDE §3 | 07/09 (cicatrizes das versões antigas) | **REGRA POR PASTA** | só vale para imagem (core/filtros, core/camadas...) | — · 1 lugar |
| R022 | Nenhum modelo generativo | CLAUDE §3; impl; pesq | 07/09 (cicatrizes das versões antigas) | **FISCAL RÁPIDO** | K16 já acusa biblioteca que desenha | test_conferencias_codigo.py (K16) · 3 lugares |
| R023 | Python 3.14, não rebaixar | CLAUDE §3; impl | 07/09 (cicatrizes das versões antigas) | **FICA NO CLAUDE.md** | contexto da máquina, uma linha | — · 2 lugares |
| R024 | GPU sem float16 rápido | CLAUDE §3; pesq | 07/09 (cicatrizes das versões antigas) | **FICA NO CLAUDE.md** | contexto da máquina e do notebook do Kaique | — · 2 lugares |
| R025 | Erro nunca como stack trace | CLAUDE §3 | 07/09 (cicatrizes das versões antigas) | **FISCAL GITHUB** | só se prova provocando erro com o programa aberto | test_decisoes_automatico.py (em parte) · 1 lugar |
| R026 | Licença: GPL pode entrar | CLAUDE §3; pesq | 07/09 (cicatrizes das versões antigas) | **FICA NO CLAUDE.md** | contexto (licença), vale sempre para pesquisa | — · 2 lugares |
| R027 | Teste de máquina: o agente decide | CLAUDE §4.1 | 07/09 (57 commits 'feito', zero aprovados) | **FICA NO CLAUDE.md** | a divisão máquina/olho é contexto do projeto | — · 1 lugar |
| R028 | Teste de olho: prepara, abre tudo, para e chama | CLAUDE §4.2; verif | 07/09 ('10 de 10' com seis erradas) | **SKILL** | já é a skill conferir-testes-visuais; contradição X3 (quais páginas) sem resposta | — · 2 lugares; contradição X3 |
| R029 | Número que não pega o pior defeito não dá veredito | CLAUDE §4.2 | 07/09 ('10 de 10' com seis erradas) | **SKILL** | já está na skill conferir-testes-visuais | — · 1 lugar |
| R030 | Ressalva escrita, nunca escondida | CLAUDE §4.2; impl; verif | 07/09 ('10 de 10' com seis erradas) | **FISCAL RÁPIDO** | K19 cobra a seção 'Ressalvas'; o conteúdo, só quem confere | test_conferencias_formulario.py (K19) · 3 lugares |
| R031 | Nunca 'APROVADO' | CLAUDE §4.3; CLAUDE §8; impl; verif | 07/09 (só o Samuel aprova) | **FISCAL RÁPIDO** | K10 já acusa 'APROVADO' e [x] posto por agente | test_conferencias_formulario.py, _mudancas.py (K10) · 5 lugares; contradição X4 |
| R032 | Máquina ou olho, item por item | CLAUDE §4.3; verif | 07/09 (só o Samuel aprova) | **FISCAL RÁPIDO** | K19 cobra a seção 'Máquina ou olho' (F13) | test_conferencias_formulario.py (K19) · 3 lugares |
| R033 | Auditoria por amostragem | CLAUDE §4.4 | 07/09 | **FICA NO CLAUDE.md** | só a gerente; não se confere em código | — · 1 lugar |
| R034 | Onde roda cada teste | CLAUDE §4.6; impl; verif; pesq; layout | 19/10 (D-453, D-458) | **FISCAL RÁPIDO** | K21 confere que a rodada existe, é do último commit e passou (X2 resolvida, D-787) | test_conferencias_formulario.py (K21) · 5 lugares; contradição X2 |
| R035 | Só documentos: entra com o GitHub | CLAUDE §4.6 | 19/10 (D-453, D-458) | **FICA NO CLAUDE.md** | só a gerente | — · 1 lugar |
| R036 | Filtro de velocidade no GitHub | CLAUDE §4.6; impl; verif; pesq; layout | 19/10 (D-453, D-458) | **FISCAL GITHUB** | é a própria rodada de velocidade no GitHub (X1 resolvida, D-786) | workflow 'Testes no Windows' (velocidade_ab) · 5 lugares; contradição X1 |
| R037 | Lentidão pequena vai para a Fase 5 | CLAUDE §4.6 | 19/10 (D-453, D-458) | **FICA NO CLAUDE.md** | só a gerente | — · 1 lugar; contradição X1 |
| R038 | Teste de reversão em todo conserto | CLAUDE §4.7; impl; verif; layout | 19/10 (D-457) | **FISCAL GITHUB** | dá para rodar o teste novo no commit de partida, sozinho, na rodada | nenhum (hoje só o verificador prova) · 4 lugares |
| R039 | Agente entrega sempre à gerente | CLAUDE §4.8; impl; verif; pesq; layout | 19/10 (D-456) | **PERMISSÃO** | o agente já não tem a ferramenta de abrir agente (D-793) | test_conferencias_codigo.py (K23) · 5 lugares |
| R040 | Recados de outras janelas | CLAUDE §4.8 | 19/10 (D-456) | **FICA NO CLAUDE.md** | só a gerente | — · 1 lugar |
| R041 | Ler a memória antes | CLAUDE §4.9; impl; verif; pesq; layout | 19/10 (D-454) | **GANCHO** | ao abrir o agente, o pacote já leva índice e fichas; texto 'se a pasta já existir' vencido (V3) | — · 5 lugares |
| R042 | Teste de imagem pelo caminho inteiro | CLAUDE §4.10; impl; verif; layout; CLAUDE §11.13.4 | 21/10 (lombada, corte sem endireitar; D-461, D-462) | **SKILL** | procedimento de teste de imagem | — · 5 lugares |
| R043 | Cada foto diz o caminho e as opções | CLAUDE §4.10; impl; verif; layout; CLAUDE §11.13.5 | 21/10 (lombada, corte sem endireitar; D-461, D-462) | **SKILL** | procedimento de foto de conferência | — · 5 lugares |
| R044 | Só páginas que vão ser impressas | CLAUDE §4.10; impl; verif; layout; CLAUDE §11.13.4 | 21/10 (lombada, corte sem endireitar; D-461, D-462) | **SKILL** | procedimento; a lista de páginas que não se imprimem poderia virar dado do gabarito | — · 5 lugares |
| R045 | Protocolo de mudança de imagem | CLAUDE §5 | 07/09 (régua que mentia) | **SKILL** | procedimento de mudança de imagem (medir, mudar um, medir) | — · 1 lugar |
| R046 | Tudo o que foi tentado vai para melhorias.md | CLAUDE §5; pesq | 07/09 (régua que mentia) | **REGRA POR PASTA** | só vale para trabalho de imagem | — · 2 lugares |
| R047 | O que o agente decide sozinho | CLAUDE §6 | 07/09 | **REGRA POR PASTA** | alçada técnica de imagem | — · 1 lugar |
| R048 | O que precisa perguntar antes | CLAUDE §6; impl | 07/09 | **FISCAL RÁPIDO** | K15 acusa requirements mudado sem 'sim'; o resto do §6 não tem fiscal | test_conferencias_mudancas.py (K15) · 2 lugares |
| R049 | core/ não importa ui/ | CLAUDE §7; impl | 07/09; ordem do preparo 09/10 | **FISCAL RÁPIDO** | K06 já acusa core/ importando ui/ | test_conferencias_codigo.py (K06) · 2 lugares |
| R050 | Modelo de dados em dois níveis | CLAUDE §7 | 07/09; ordem do preparo 09/10 | **REGRA POR PASTA** | vale para modelos.py e quem grava ConfigPagina/ConfigFolha | — · 1 lugar |
| R051 | Onde o programa guarda estado | CLAUDE §7 | 07/09; ordem do preparo 09/10 | **REGRA POR PASTA** | vale para configuracoes.py, projetos.py | — · 1 lugar |
| R052 | Desempenho já resolvido, não refazer | CLAUDE §7 | 07/09; ordem do preparo 09/10 | **REGRA POR PASTA** | vale para core/filtros, core/analise | — · 1 lugar |
| R053 | Ordem obrigatória do processamento | CLAUDE §7 | 07/09; ordem do preparo 09/10 | **FISCAL GITHUB** | já tem teste que roda páginas | test_ordem_do_preparo.py · 1 lugar |
| R054 | Acervo e originais só para ler | CLAUDE §7; impl; verif | 07/09; ordem do preparo 09/10 | **PERMISSÃO** | pastas do acervo e originais: o agente não deve poder gravar lá | — · 3 lugares |
| R055 | Queixas do Kaique são requisito | CLAUDE §7 | 07/09; ordem do preparo 09/10 | **FICA NO CLAUDE.md** | contexto: onde estão as queixas do Kaique | — · 1 lugar |
| R056 | Handoff só com pedido do Samuel | CLAUDE §7 | 07/09; ordem do preparo 09/10 | **FISCAL RÁPIDO** | K17 acusa agente mexendo no handoff, CLAUDE.md, Livro, plano | test_conferencias_mudancas.py (K17) · 1 lugar |
| R057 | Item da fase atual, na ordem | CLAUDE §8 passo 1; CLAUDE §10.2; impl | 25/09 (plano definitivo) | **DÚVIDA** | contradição X9 (fase atual × obra × D-765) sem resposta | — · 3 lugares; contradição X9 |
| R058 | Testes quebrados: conserta antes de seguir | CLAUDE §8 passo 4; impl | 25/09 (plano definitivo) | **FISCAL GITHUB** | a rodada do GitHub barra (K21) | test_conferencias_formulario.py (K21) · 2 lugares |
| R059 | Régua e velocidade; nada mais lento | CLAUDE §8 passo 5; impl; verif | 25/09 (plano definitivo) | **FISCAL GITHUB** | régua e velocidade só no GitHub; o texto antigo do §8 passo 5 sobra (X1, D-786) | workflow (velocidade_ab) · 3 lugares; contradição X1 |
| R060 | Antes/depois só nas páginas-gabarito do item | CLAUDE §8 passo 6; verif | 25/09 (plano definitivo) | **DÚVIDA** | contradição X3 (todas as páginas × só gabarito) sem resposta | — · 2 lugares; contradição X3 |
| R061 | Item de tela: janela real com mouse nativo | CLAUDE §8 passo 6; verif; layout | 25/09 (plano definitivo) | **SKILL** | procedimento de pilotar a janela | — · 3 lugares |
| R062 | Commit na hora com o defeito por extenso; nunca segredo | CLAUDE §8 passo 10 | 25/09 (plano definitivo) | **FISCAL RÁPIDO** | o antes-do-commit pode barrar arquivo de segredo; 'commit na hora' contradiz X12 | — · 1 lugar; contradição X12 |
| R063 | Mancha do verso: o defeito mais grave | CLAUDE §9 | 07/09 (achados que não se redescobrem) | **REGRA POR PASTA** | achado técnico de imagem (core/filtros, avaliar.py) | — · 1 lugar |
| R064 | A régua precisa de critérios novos | CLAUDE §9 | 07/09 (achados que não se redescobrem) | **REGRA POR PASTA** | achado técnico da régua (avaliar.py) | — · 1 lugar |
| R065 | Amarelado está na tinta | CLAUDE §9 | 07/09 (achados que não se redescobrem) | **REGRA POR PASTA** | achado técnico de imagem | — · 1 lugar |
| R066 | Não há binarizador vencedor | CLAUDE §9 | 07/09 (achados que não se redescobrem) | **REGRA POR PASTA** | achado técnico de imagem | — · 1 lugar |
| R067 | Não desfazer a correção do 'magic color' | CLAUDE §9 | 07/09 (achados que não se redescobrem) | **REGRA POR PASTA** | vale para core/filtros; poderia ganhar teste da capa azul | — · 1 lugar |
| R068 | Scan de baixa resolução não se recupera | CLAUDE §9 | 07/09 (achados que não se redescobrem) | **REGRA POR PASTA** | achado técnico de imagem | — · 1 lugar |
| R069 | Barra de rolagem cinza, de propósito | CLAUDE §9 | 07/09 (achados que não se redescobrem) | **FISCAL RÁPIDO** | K22 confere os valores de ui/estilo.py (P0-v1-18: o valor do §9 não bate com o da K22) | test_conferencias_codigo.py (K22) · 1 lugar |
| R070 | Gerente não escreve código | CLAUDE §10.1 | 25/09 (gerente + agentes) | **FICA NO CLAUDE.md** | só a gerente; não há como travar a conversa principal | — · 1 lugar |
| R071 | Cada papel no seu lugar | CLAUDE §10.1; impl; verif; pesq; layout | 25/09 (gerente + agentes) | **FISCAL RÁPIDO** | K13 acusa quem mexe fora do papel | test_conferencias_mudancas.py (K13) · 5 lugares; contradição X7 |
| R072 | Layout só começa com o plano de layout | CLAUDE §10.1; layout | 25/09 (gerente + agentes) | **APAGAR** | vencida (V1): a obra do layout já existe; a cópia 'layout' não é mais usada | — · 2 lugares; contradição V1 |
| R073 | Ideia nova vai para a Lista de espera; bug que não impede, para a Lista de bugs | CLAUDE §10.2; impl; layout | 25/09 | **FISCAL RÁPIDO** | K19 cobra a seção 'Ideias e bugs' (F16) | test_conferencias_formulario.py (K19) · 3 lugares; contradição X9 |
| R074 | Uma cópia e um ramo por frente | CLAUDE §10.3; layout | 25/09 | **PERMISSÃO** | o agente só deve poder gravar na própria cópia | — · 2 lugares; contradição X5 |
| R075 | Plano em duas cópias | CLAUDE §10.4 | 25/09 (cópia do plano sobrescrita) | **FISCAL RÁPIDO** | comparar as duas cópias do plano é conta de máquina | — · 1 lugar |
| R076 | Docstring em tudo o que tocar | CLAUDE §10.5; impl; layout | 25/09 (D-406) | **FISCAL RÁPIDO** | K12 acusa função mudada sem docstring | test_conferencias_mudancas.py (K12) · 3 lugares |
| R077 | Plano novo não apaga pendência | CLAUDE §10.6 | 25/09 | **FICA NO CLAUDE.md** | princípio da gerente | — · 1 lugar |
| R078 | Item resolvido guarda o pedido original | CLAUDE §10.7 | 25/09 | **FICA NO CLAUDE.md** | só a gerente | — · 1 lugar |
| R079 | Prosa de checkpoint não é prova | CLAUDE §10.8; CLAUDE §9 (menu Abrir) | 22/09 (menu 'Abrir') | **FICA NO CLAUDE.md** | princípio: prosa de checkpoint não é prova | — · 2 lugares |
| R080 | Apagar: fora do projeto nada; dentro só o seu; junções | CLAUDE §10.9; impl; verif; pesq; layout | 29/09 (D:\d apagada) | **PERMISSÃO** | apagar fora do projeto não deve ser possível; K25 já acusa rm -r em script | test_conferencias_codigo.py (K25) · 5 lugares |
| R081 | Conferências em página do claude.ai com banco | CLAUDE §10.10 | 06/10 a 13/11 (páginas, Central) | **SKILL** | procedimento da Central (só a gerente) | — · 1 lugar |
| R082 | Aba Respostas: gerente responde no documento | CLAUDE §10.10 | 06/10 a 13/11 (páginas, Central) | **SKILL** | procedimento da Central (só a gerente); SÓ NO CLAUDE.md DE 859 LINHAS | — · 1 lugar |
| R083 | Responder de novo guardando a antiga | CLAUDE §10.10 | 06/10 a 13/11 (páginas, Central) | **SKILL** | procedimento da Central (só a gerente); SÓ NO CLAUDE.md DE 859 LINHAS | — · 1 lugar |
| R084 | Modelo de print (o do girar) | CLAUDE §10.10; CLAUDE §11.13.3 | 06/10 a 13/11 (páginas, Central) | **SKILL** | o modelo do girar vira a skill de print; §10.10 só no de 859, §11.13.3 nos dois | — · 2 lugares |
| R085 | Central: um jeito de ver e celular | CLAUDE §10.10 | 06/10 a 13/11 (páginas, Central) | **SKILL** | procedimento da Central (só a gerente); SÓ NO CLAUDE.md DE 859 LINHAS | — · 1 lugar |
| R086 | Central: atualizar sempre | CLAUDE §10.10 | 06/10 a 13/11 (páginas, Central) | **SKILL** | procedimento da Central (só a gerente) | — · 1 lugar |
| R087 | Central: ler as ordens dele primeiro | CLAUDE §10.10 | 06/10 a 13/11 (páginas, Central) | **SKILL** | procedimento da Central (só a gerente) | — · 1 lugar |
| R088 | Aviso no celular ao pôr cartão | CLAUDE §10.10 | 06/10 a 13/11 (páginas, Central) | **SKILL** | procedimento da Central (só a gerente) | — · 1 lugar |
| R089 | Pergunta de agente vai à Central na hora | CLAUDE §10.10; impl; verif; pesq; layout | 06/10 a 13/11 (páginas, Central) | **GANCHO** | quando a seção 'Perguntas para o Samuel' muda, a gerente é avisada sozinha | — · 5 lugares; contradição X13 |
| R090 | Agente não grava na Central | CLAUDE §10.10 | 06/10 a 13/11 (páginas, Central) | **PERMISSÃO** | já tirada a ferramenta da Central dos agentes (D-793) | test_conferencias_codigo.py (K23) · 1 lugar |
| R091 | Aba Conferência | CLAUDE §10.10 | 06/10 a 13/11 (páginas, Central) | **SKILL** | procedimento da Central (só a gerente) | — · 1 lugar |
| R092 | Abrir a conferência sozinha no navegador | CLAUDE §10.10 | 06/10 a 13/11 (páginas, Central) | **SKILL** | procedimento da Central (só a gerente) | — · 1 lugar; contradição X13 |
| R093 | Comentário dele se responde na página | CLAUDE §10.10 | 06/10 a 13/11 (páginas, Central) | **SKILL** | procedimento da Central (só a gerente) | — · 1 lugar |
| R094 | Livro de decisões único | CLAUDE §11.1 | 26/10 (decisões de 25/09 nunca feitas) | **FICA NO CLAUDE.md** | contexto: onde ficam as decisões | — · 1 lugar |
| R095 | Nenhuma decisão sem dono | CLAUDE §11.2 | 26/10 (painel Automático sem dono) | **FISCAL RÁPIDO** | coluna 'Dono' vazia se acha lendo o Livro | nenhum · 1 lugar |
| R096 | Pedido leva as decisões; ONDE-PAREI diz como cumpriu | CLAUDE §11.3; impl; verif; pesq; layout | 26/10 (o agente recebia a etapa, não a decisão) | **FISCAL RÁPIDO** | K19/K20 cobram 'Decisões...' e 'Como cumpri cada uma' | test_conferencias_formulario.py (K19, K20) · 5 lugares |
| R097 | Cada decisão tem prova de comportamento; aparência não é prova | CLAUDE §11.4; CLAUDE §11.8; impl; verif; pesq; layout | 26/10 ('Photoshop puro' só na aparência) | **FISCAL GITHUB** | as provas das decisões rodam no GitHub | tests/test_decisoes*.py (97 arquivos) · 6 lugares |
| R098 | Quem confere não construiu, e confere do zero | CLAUDE §11.5; verif | 26/10 | **FISCAL RÁPIDO** | K10 acusa 'PRONTO' no ramo de quem construiu; agente novo a cada volta (D-815) | test_conferencias_formulario.py (K10) · 2 lugares |
| R099 | Na dúvida, parar e perguntar | CLAUDE §11.6; impl; verif; pesq; layout | 26/10 | **FICA NO CLAUDE.md** | princípio: na dúvida, parar | — · 5 lugares |
| R100 | Gerente procura no Livro antes de perguntar | CLAUDE §11.6; CLAUDE §11.13.10 | 26/10 | **FISCAL RÁPIDO** | F23 'Decisões procuradas antes de cada pergunta' (D-814) | test_conferencias_formulario.py (K19) · 2 lugares |
| R101 | Só o que ele mandou | CLAUDE §11.7 | 27/10 (D-549: agentes mudando o decidido) | **FICA NO CLAUDE.md** | princípio; K14 pega só o arquivo fora da lista | test_conferencias_mudancas.py (K14, em parte) · 1 lugar |
| R102 | O novo não estraga o escolhido e testado (D-605) | CLAUDE §11.8; impl; verif; pesq; layout | 03/11 (D-605) | **FISCAL RÁPIDO** | K11 acusa teste antigo mudado sem a decisão no commit | test_conferencias_mudancas.py (K11) · 5 lugares; contradição X14 |
| R103 | Verificador confere o que funcionava ao redor | CLAUDE §11.8; impl; verif; pesq; layout | 03/11 (D-605) | **SKILL** | procedimento do verificador | — · 5 lugares |
| R104 | Como fica para quem usa e no livro (D-637) | CLAUDE §11.9; impl; verif; pesq; layout | 05/11 (D-637) | **FISCAL RÁPIDO** | K19 cobra a seção (F4) | test_conferencias_formulario.py (K19) · 5 lugares |
| R105 | Mudou a ferramenta, muda em todos os lugares (D-667) | CLAUDE §11.10 | 10/11 (D-667: D-662 feita só no 'todas') | **FISCAL RÁPIDO** | trava por leitura de código: cada campo gravado por uma porta só (Fable, Pergunta 2) | nenhum · 1 lugar |
| R106 | Agente não abre agente | CLAUDE §11.11 | 10/11 (cinco agentes rodando) | **PERMISSÃO** | já feito (D-793); o número máximo de agentes é contradição X6, sem resposta | test_conferencias_codigo.py (K23) · 1 lugar; contradição X6 |
| R107 | Sem gambiarra: a causa, a regra, todos os caminhos | CLAUDE §11.12; impl; verif; pesq; layout | 13/11 (Girar com 7 caminhos; 17 remendos) | **FISCAL RÁPIDO** | trava por leitura de código: lista derivada do modelo, uma porta (Fable) | nenhum · 5 lugares |
| R108 | Como conserta: um lugar só | CLAUDE §11.12 | 13/11 (Girar com 7 caminhos; 17 remendos) | **FISCAL RÁPIDO** | mesmo fiscal da R107 | nenhum · 1 lugar; contradição X7 |
| R109 | Prova: caminho → função e o mesmo resultado em todos | CLAUDE §11.12; impl; verif | 13/11 (Girar com 7 caminhos; 17 remendos) | **FISCAL RÁPIDO** | K19 cobra 'Caminho e função' (F12); 'o mesmo resultado' pede teste de pixels no GitHub | test_conferencias_formulario.py (K19) · 3 lugares |
| R110 | Quando só der remendo: parar | CLAUDE §11.12 | 13/11 (Girar com 7 caminhos; 17 remendos) | **FICA NO CLAUDE.md** | princípio: remendo nunca calado | — · 1 lugar |
| R111 | Gerente pede sobre a ferramenta inteira | CLAUDE §11.12; CLAUDE §11.10 | 13/11 (Girar com 7 caminhos; 17 remendos) | **SKILL** | vai no modelo da ordem de serviço (Parte C) | — · 2 lugares |
| R112 | Sem gambiarra vale para tudo | CLAUDE §11.12 (18/11); impl; verif; pesq; layout | 18/11 (etapa 5: 7 defeitos + 26) | **APAGAR** | repete a R107; basta a R107 dizer 'em tudo' | — · 5 lugares |
| R113 | Uma peça só para conversar com o que está fora | CLAUDE §11.12.1; impl; verif; pesq; layout | 18/11 (etapa 5: 7 defeitos no Windows) | **FISCAL RÁPIDO** | K01, K02, K03 (hoje por lista de palavras; o Fable sugere leitura de import) | test_conferencias_codigo.py; test_windows_peca.py; test_trava_windows.py · 5 lugares |
| R114 | Nada dá como feito o que não conferiu | CLAUDE §11.12.2; impl; verif; pesq; layout | 18/11 (etapa 5: 7 defeitos no Windows) | **FISCAL GITHUB** | só se prova desligando a conferência e vendo um teste falhar (mutação) | anexos de mutação dos quebradores (manual) · 5 lugares |
| R115 | Antes de escrever, a lista das falhas | CLAUDE §11.12.3; impl; verif; pesq; layout | 18/11 (etapa 5: 7 defeitos no Windows) | **FISCAL RÁPIDO** | K19 cobra a seção 'O que pode falhar' (F6) | test_conferencias_formulario.py (K19) · 5 lugares |
| R116 | Peça de mentira não prova (D-767) | CLAUDE §11.12.4; impl; verif; pesq; layout | 18/11 (etapa 5: 7 defeitos no Windows) | **FISCAL GITHUB** | só conta rodando no Windows de verdade (X8 resolvida, D-785) | test_velopack_de_verdade.py; test_atualizador_volta3_de_verdade.py · 5 lugares; contradição X8 |
| R117 | Gerente não aceita 'pronto' sem prova | CLAUDE §11.12.5; impl; verif; pesq; layout | 18/11 (etapa 5: 7 defeitos no Windows) | **FISCAL RÁPIDO** | K19 + K21: sem prova a entrega volta | test_conferencias_formulario.py · 5 lugares |
| R118 | Ler a peça de fora antes de usar | CLAUDE §11.12.6; impl; verif; pesq; layout; Livro D-813 | 18/11 (etapa 5: 7 defeitos no Windows) | **FISCAL RÁPIDO** | K19 cobra 'O que li da peça de fora' (F7); acréscimo D-813 não está no CLAUDE.md | test_conferencias_formulario.py (K19) · 6 lugares |
| R119 | Perguntar: comece pelo que é e onde fica | CLAUDE §11.13.1; impl; verif; pesq; layout | 13/11 (106 'Ainda não entendi') | **SKILL** | como perguntar ao Samuel (§11.13) | — · 5 lugares |
| R120 | Perguntar: nenhuma palavra de dentro | CLAUDE §11.13.2; impl; verif; pesq; layout | 13/11 (106 'Ainda não entendi') | **FISCAL RÁPIDO** | número de decisão, arquivo ou código no texto para ele se acha lendo; K04 já faz na tela | test_conferencias_codigo.py (K04, só tela) · 5 lugares |
| R121 | Perguntar: print que prova | CLAUDE §11.13.3; impl; verif; pesq; layout | 13/11 (106 'Ainda não entendi') | **SKILL** | como perguntar (o print) | — · 5 lugares |
| R122 | Perguntar: o caso que o Kaique encontra, print conferido | CLAUDE §11.13.4; impl; verif; pesq; layout | 13/11 (106 'Ainda não entendi') | **SKILL** | como perguntar (o caso real) | — · 5 lugares |
| R123 | Perguntar: o caminho, e se é defeito ou escolha | CLAUDE §11.13.5; impl; verif; pesq; layout | 13/11 (106 'Ainda não entendi') | **SKILL** | como perguntar | — · 5 lugares |
| R124 | Perguntar: o que você escolhe e o que muda | CLAUDE §11.13.6; impl; verif; pesq; layout | 13/11 (106 'Ainda não entendi') | **SKILL** | como perguntar | — · 5 lugares |
| R125 | Perguntar: curto, sem ficha | CLAUDE §11.13.7; impl; verif; pesq; layout | 13/11 (106 'Ainda não entendi') | **SKILL** | como perguntar | — · 5 lugares |
| R126 | Perguntar: ele continua no controle? | CLAUDE §11.13.8; impl; verif; pesq; layout | 13/11 (106 'Ainda não entendi') | **SKILL** | como perguntar | — · 5 lugares |
| R127 | Perguntar: de onde veio | CLAUDE §11.13.9; impl; verif; pesq; layout | 13/11 (106 'Ainda não entendi') | **SKILL** | como perguntar | — · 5 lugares |
| R128 | Perguntar: a situação de agora, sem repetir | CLAUDE §11.13.10; impl; verif; pesq; layout | 13/11 (106 'Ainda não entendi') | **SKILL** | como perguntar; F23 cobra parte | — · 5 lugares |
| R129 | Depois de 'Ainda não entendi': mudar o jeito | CLAUDE §11.13 | 13/11 (106 'Ainda não entendi') | **SKILL** | como perguntar (gerente) | — · 1 lugar |
| R130 | A lista de conferência antes de mandar | CLAUDE §11.13; CLAUDE §10.10 | 13/11 (106 'Ainda não entendi') | **SKILL** | a lista de conferência da gerente antes de mandar | — · 2 lugares |
| R131 | Obra D-014: o que não vale durante a obra | CLAUDE fim | 26/10 (D-014, a obra) | **DÚVIDA** | a obra ainda vale? (D-014 × D-765 × D-885) | — · 1 lugar; contradição X9 |
| R132 | Teste escrito antes do código, quando der | impl | 25/09 (agentes criados) | **SKILL** | procedimento de conserto | — · 1 lugar |
| R133 | Nunca commit no master | impl; layout | 25/09 (agentes criados) | **PERMISSÃO** | gravar no ramo da gerente não deve ser possível; trocar 'master' pelos dois de hoje (D-797) | — · 2 lugares; contradição X5 |
| R134 | Nunca fechar à força janela que o Samuel usa | impl; verif; layout | 16/09 a 22/09 (janela do Samuel) | **PERMISSÃO** | fechar processo alheio já é bloqueado pelo Claude Code; caso de 25/11 mostra o furo por código | — · 3 lugares |
| R135 | Como entregar (lista do papel) | impl; verif; pesq; layout | 25/09 (agentes criados) | **FISCAL RÁPIDO** | o formulário único (K19) substitui as 4 listas; as 4 podem sair | test_conferencias_formulario.py (K19) · 4 lugares |
| R136 | Commit e push a cada passo; ONDE-PAREI | impl; verif; pesq; layout | 19/10 | **FISCAL RÁPIDO** | K18 acusa trabalho sem commit/push | test_conferencias_mudancas.py (K18) · 4 lugares; contradição X12 |
| R137 | Verificador: não conserta código | verif | 25/09 (agentes criados) | **PERMISSÃO** | verificador sem escrita em core/ e ui/ | test_conferencias_mudancas.py (K13) · 2 lugares |
| R138 | Verificador: skill conferir-testes-visuais | verif | 30/07 ('10 de 10' com seis erradas) | **SKILL** | já é skill | — · 1 lugar |
| R139 | Defeitos conhecidos da Fase 1 em destaque | verif | 28/09 (D-409) | **DÚVIDA** | vencida? 'até a Fase 1 ficar pronta' (V2) | — · 1 lugar; contradição V2 |
| R140 | Pilotar: instância nova, nunca a dele | verif | 25/09; janela real 22/09 e 16/09 | **SKILL** | pilotar a janela | — · 1 lugar |
| R141 | Pilotar: mouse por mensagem nativa ao hwnd | verif | 25/09; janela real 22/09 e 16/09 | **SKILL** | pilotar a janela | — · 1 lugar |
| R142 | Pilotar: nunca pywinauto click_input/send_keys | verif | 25/09; janela real 22/09 e 16/09 | **FISCAL RÁPIDO** | K24 já acusa click_input/send_keys | test_conferencias_codigo.py (K24) · 1 lugar |
| R143 | Pilotar: roda do mouse não funciona sem foco | verif | 25/09; janela real 22/09 e 16/09 | **SKILL** | pilotar a janela (limite conhecido) | — · 1 lugar |
| R144 | Pilotar: print fora da tela | verif | 25/09; janela real 22/09 e 16/09 | **SKILL** | pilotar a janela; X8 resolvida pela D-785 | — · 1 lugar; contradição X8 |
| R145 | offscreen não tem fonte | verif | 25/09; janela real 22/09 e 16/09 | **SKILL** | pilotar a janela (limite conhecido) | — · 1 lugar |
| R146 | Verificador: prova de reversão numa cópia à parte | verif | 19/10 | **FISCAL GITHUB** | rodar o teste novo no código antigo dá para fazer sozinho na rodada | nenhum · 1 lugar |
| R147 | Pesquisador: não repetir caminho fechado | pesq | 25/09 (agentes criados) | **SKILL** | procedimento de pesquisa | — · 1 lugar |
| R148 | Pesquisador: resumir com as próprias palavras | pesq | 25/09 | **SKILL** | procedimento de pesquisa | — · 1 lugar |
| R149 | Pesquisador: roda aqui e no notebook do Kaique? | pesq | 25/09 | **SKILL** | procedimento de pesquisa | — · 1 lugar |
| R150 | Lido na fonte separado de dedução | pesq | 25/09 | **SKILL** | procedimento de pesquisa; F7 cobra a seção | — · 2 lugares |
| R151 | Pesquisa gravada em docs/pesquisa/ com data e links | pesq | 25/09 (pesquisa que só existiu na conversa) | **FISCAL RÁPIDO** | K13 já confere onde o pesquisador grava | test_conferencias_mudancas.py (K13) · 1 lugar |
| R152 | Não instalar no .venv sem pedido | pesq | 25/09 | **PERMISSÃO** | instalar no .venv não deve ser possível sem pedido | — · 1 lugar |
| R153 | Layout: pista visual em toda área de clicar | layout | 22/09 (arrasto 'não funcionava' sem pista) | **REGRA POR PASTA** | só vale para ui/ | — · 1 lugar |
| R154 | Toda função automática tem ligar e desligar | layout; impl | 24/09 (regra 8 do plano) | **REGRA POR PASTA** | vale para ui/ e core/automatico.py | — · 2 lugares |
| R155 | Layout: ler a Lista de espera e as referências | layout | 25/09 (agentes criados) | **REGRA POR PASTA** | só vale para ui/ | — · 1 lugar |
| R156 | A cópia divide o .git com o Samuel: nada de comando que muda o .git inteiro | Livro D-809 | 19/11 (repositório raso; modelos/ esvaziada) | **FISCAL RÁPIDO** | K25 já acusa | test_conferencias_codigo.py; test_conferencias_protecao.py (K25) · 1 lugar |
| R157 | O teste do Windows roda em três computadores diferentes | Livro D-810 | 19/11 (3 rodadas perdidas: Windows em inglês) | **REGRA POR PASTA** | vale para tests/ do Windows e core/windows.py | — · 1 lugar |
| R158 | Toda conferência diz de onde vem cada dado | Livro D-812 | 19/11 ('sim' forjável) | **FISCAL RÁPIDO** | K19 cobra 'De onde vem cada dado' (F22) | test_conferencias_formulario.py (K19) · 1 lugar |

## O porteiro: as 25 conferências que já existem

A ordem fala em "K01 a K09"; no código são **25** (K01 a K25). 13 leem o código parado; 12 olham o que a entrega mudou.
Todas são FISCAL RÁPIDO por natureza. "Observação" é só o que vi, não plano.

| K | confere | tipo | regra | onde roda hoje | teste do próprio fiscal | observação |
|---|---|---|---|---|---|---|
| K01 | conversa com o Windows fora de `core/windows.py` | código | R113 | GitHub, em toda rodada | test_conferencias_codigo.py, _excecoes, _juiz, _protecao; test_windows_peca.py | é lista de palavras; o vizinho passou em 6 voltas do passo 0 (família F2); o Fable sugere ler o import |
| K02 | DETACHED_PROCESS | código | R113 | GitHub | test_conferencias_codigo.py | — |
| K03 | licença de pasta à mão (icacls...) | código | R113 | GitHub | test_conferencias_codigo.py; test_porteiro_licenca_que_acrescenta.py | 1 exceção aberta pela D-837 |
| K04 | número de decisão em texto de tela | código | R120 | GitHub | test_conferencias_codigo.py | não olha o texto para o Samuel (Central, ONDE-PAREI) |
| K05 | emoji em texto de tela | código | R019 | GitHub | test_conferencias_codigo.py | — |
| K06 | `core/` importa `ui/` | código | R049 | GitHub | test_conferencias_codigo.py | falta a inversa (`ui/` monta campos), Fable, Pergunta 6 |
| K07 | tkinter | código | R015 | GitHub | test_conferencias_codigo.py | — |
| K08 | nome de arquivo com acento | código | R020 | GitHub | test_conferencias_codigo.py | — |
| K09 | relatório só em .md | entrega | R014 | ao conferir a entrega | test_conferencias_mudancas.py | — |
| K10 | "APROVADO" de agente; PRONTO no ramo de quem fez | entrega | R031, R098 | ao conferir a entrega | test_conferencias_formulario.py, _mudancas | — |
| K11 | teste antigo mudado sem decisão citada | entrega | R102 | ao conferir a entrega | test_conferencias_mudancas.py | — |
| K12 | função tocada sem docstring | entrega | R076 | ao conferir a entrega | test_conferencias_mudancas.py | — |
| K13 | mexeu fora do papel | entrega | R071 | ao conferir a entrega | test_conferencias_mudancas.py | — |
| K14 | arquivo fora da lista do pedido (só avisa) | entrega | — | ao conferir a entrega | test_conferencias_mudancas.py | é o "Fora" da Parte C, mas não barra |
| K15 | requirements.txt sem "sim" | entrega | R048 | ao conferir a entrega | test_conferencias_mudancas.py | — |
| K16 | biblioteca que desenha | código | R022 | GitHub | test_conferencias_codigo.py | — |
| K17 | agente mexeu em CLAUDE.md, agentes, Livro, plano, handoff | entrega | R056, R094 | ao conferir a entrega | test_conferencias_mudancas.py | — |
| K18 | sem commit ou sem push | entrega | R136 | ao conferir a entrega | test_conferencias_mudancas.py | — |
| K19 | o formulário da entrega (F1 a F23) | entrega | R096, R104, R115, R118 | ao conferir a entrega | test_conferencias_formulario.py | só confere que a seção existe |
| K20 | palavras do Samuel batem com o Livro | entrega | R013, R096 | ao conferir a entrega | test_conferencias_formulario.py | — |
| K21 | rodada do GitHub do último commit passou | entrega | R034 | ao conferir a entrega | test_conferencias_formulario.py | — |
| K22 | barra de rolagem cinza | código | R069 | GitHub | test_conferencias_codigo.py | o valor da K22 não bate com o `#a8a49e` do §9 (P0-v1-18) |
| K23 | agente sem ferramenta de abrir agente e de gravar na Central | código | R106, R090 | GitHub | test_conferencias_codigo.py | — |
| K24 | pywinauto click_input / send_keys | código | R142 | GitHub | test_conferencias_codigo.py | — |
| K25 | comando que muda o .git inteiro ou apaga pasta com tudo | código | R156 | GitHub | test_conferencias_codigo.py, _protecao | — |

**As 12 "de entrega" dependem do pedido** (papel, commit de partida, lista de arquivos), que vem do pacote (D-784).
Achei o pacote copiado no ONDE-PAREI dos passos 0, 1 e 2 (19 a 21/11) e no `zoom-mouse`. Do atualizador novo (23/11) em
diante, os ONDE-PAREI não têm as seções "Pedido" e "Arquivos que vou mexer". Então, de 23/11 para cá, essas 12 não
tinham o que conferir. (Achado por leitura; não rodei o porteiro.)

## A lista de exceções: quantas são de verdade

- A ordem diz 164. **Hoje são 135** (`tests/conferencias_excecoes.json` desta cópia, ligada com o "sim" do Samuel,
  D-801). O 164 é o número que o Fable leu em 23/11 ("164 exceções em 4 arquivos"). A lista nasceu com 176 (19/11),
  passou a 175 e perdeu 40 em 24/11 (`f2d0ad14`).
- Por conferência: **124 da K01**, 9 da K04, 2 da K03. Por arquivo: 71 em `core/`, 52 em `teste_velocidade.py`, 7 em
  `ui/`, 5 em outros.
- Por quando somem: 69 "depois da entrega" (D-800, D-802), 50 no passo 4 e 16 no passo 5 do plano da parte do Windows.
- **No ramo `fase-1` (a pasta principal) a lista não existe:** o porteiro só está na versão de teste.
- **Destino:** FISCAL RÁPIDO (é parte do porteiro). Pelo Fable, elas somem quando a K01 virar leitura de import e os
  arquivos se acertarem; até lá, só diminuem.

## O gancho antes do commit

- `ganchos/pre-commit` roda as conferências "de código" só nos arquivos do commit. **Não está ligado:** o próprio
  arquivo diz "NÃO ESTÁ LIGADA", e `git config core.hooksPath` não tem valor no repositório (conferido hoje). Quem
  garante hoje é o GitHub.
- **Destino:** GANCHO (já é gancho do git; falta ligar). Faz o mesmo que o GitHub, mais cedo.
- Não há `.claude/settings.json` no projeto: **nenhuma permissão e nenhum gancho do Claude Code** estão configurados.
  As 10 regras com destino PERMISSÃO e as 2 com GANCHO não têm onde morar hoje.

## A skill que existe

| skill | o que faz | destino | observação |
|---|---|---|---|
| `conferir-testes-visuais` | abrir todas as imagens, veredito por imagem, percentual não é veredito (caso de 30/07) | SKILL (fica) | cobre R028, R029, R138; só o verificador a cita |

## As ferramentas dos agentes

Os quatro arquivos de agente já tiram "abrir outro agente" e "gravar na Central" (D-793, conferido pela K23). É a única
PERMISSÃO construída hoje.

## Regras que só estão no Livro (nem no CLAUDE.md, nem nos agentes)

Achei por busca do número em `CLAUDE.md`, `.claude/agents/` e no catálogo. São decisões do Samuel sobre o jeito de
trabalhar, de 16 a 25/11, que o agente só recebe se a gerente copiar no pedido. Não estão na contagem de 158.

| decisão | o que diz (resumo) | no catálogo? | destino que ela pediria |
|---|---|---|---|
| D-709 (16/11) | plano antes de mexer, com o porquê do erro e o guia de leitura | não | SKILL (vai no modelo da ordem, Parte C); falta ele dizer se o agente espera o "sim" |
| D-710 (16/11) | um modelo por tipo de tarefa | não | DÚVIDA (proposta da gerente sem resposta) |
| D-760 (17/11) | a contagem de páginas e folhas numa conta só; "rever as regras dos agentes" | não | FISCAL RÁPIDO (é a R105/R107 num caso) |
| D-791, D-792 (18/11) | porteiro barra desde o 1º dia; formulário único | não (é o próprio porteiro) | FISCAL RÁPIDO |
| D-796, D-797, D-798 (19/11) | tela pode mexer em `core/` se nomeado; dois ramos só; só quem confere escreve PRONTO | sim, como contradição resolvida | o texto do CLAUDE.md e dos agentes ainda diz o contrário |
| D-807 (19/11) | conjunto inteiro dos testes só no GitHub | não | PERMISSÃO (não rodar a suíte inteira no PC) |
| D-809, D-810, D-812 (19/11) | .git dividido; três computadores; de onde vem o dado | sim (R156 a R158) | já na tabela |
| D-811, D-814 (19/11) | perguntas F21 e F23 do formulário | só no formulário | FISCAL RÁPIDO |
| D-813 (19/11) | acréscimo à regra 6 do §11.12 | só no catálogo | FICA o texto; FISCAL RÁPIDO a seção F7 |
| D-815 (20/11) | quem tenta quebrar é sempre um agente novo | não | GANCHO (a cada volta, agente novo) |
| D-819 (21/11) | comparar o jeito mais simples antes de aceitar um plano | não | SKILL (modelo da ordem) |
| D-827 (22/11) | proteção sem teste nunca é "pequena" | não | FISCAL GITHUB (mutação) |
| D-842 (24/11) | nenhum item aberto entra na prova à vista | não | FISCAL RÁPIDO (achado sem "consertar" ou "deixo para depois" barra) |
| D-879 (25/11) | conferência curta, do tamanho da mudança | não | SKILL (do quem tenta quebrar) |

## As contradições ainda abertas (do catálogo)

As X1, X2, X4, X5, X7 e X8 foram resolvidas pelo Samuel (D-785 a D-798), **mas o texto do CLAUDE.md e dos agentes
ainda diz o antigo** (o catálogo avisa isso no pacote). Continuam sem resposta: **X3** (quais páginas no antes/depois),
**X6** (quantos agentes ao mesmo tempo), **X9** (o ritmo: fase atual × obra × D-765), **X10** (a ordem de leitura) e a
vencida **V2** (o aviso da moldura até a Fase 1). Vão na lista de dúvidas do resumo.

## Ressalvas

- **Destino é julgamento meu.** Onde dois cabiam (ex.: R014, relatório em três formatos: fiscal e skill), escolhi um e
  disse o outro no motivo.
- **"Teste que cobre"** é o que achei por busca de nome e da conferência; não rodei nenhum teste (a ordem proíbe). Um
  teste marcado "(em parte)" cobre só um pedaço da regra.
- **O catálogo é de 19/11.** Conferi que o CLAUDE.md e os agentes não mudaram depois; segui a divisão do catálogo (ele
  pode ter juntado duas frases numa regra só).
- **Não contei como regra** os itens de informação do catálogo (quantos testes existem, mapa de pastas, comandos) nem a
  história do §11.12 (o que aconteceu em 10/11 e 18/11). Ficam como contexto.
