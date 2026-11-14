
### Erro 2 (D-679) — números
- **"de 134":** `ui/automatico.py` — `EstadoDoAutomatico.do_projeto` (`self.total_paginas = len(projeto.paginas)`, ~l.322 e
  l.343) alimenta `A.resumo(...)` ("no livro todo (N páginas)"); `PaginaAntesEDepois._numero_e_total` (~l.1840) devolve
  `len(self.projeto.paginas)` sem o Dividir, e `len(passos)` com ele (os passos também incluem a tirada: print b-10 "132
  de 134"; c-03 mostra a 133 tirada como "página 133 de 134"). O comentário logo acima diz que é de propósito
  ("contar pelos passos sem o Dividir (página tirada do livro mudaria a numeração de sempre)"). A barra de baixo
  (`rotulo_da_pagina`: "página 133 de 134") conta igual; a `JanelaConfirmar._frase_do_livro` conta `paginas_ativas`
  (133). Três telas, duas contas.
- **Sino:** reproduzido na fase d (abaixo). Antes, sem repetir: fase a, 134 parado 60 s e andando; fase b (todos os
  avisos aceitos), 0 parado 60 s e em 40 setas. `scripts/sino.py`: desenhar as 133 páginas no tamanho do PDF (`renderizar_pagina`) numa cópia do projeto
  não criou nenhum aviso pendente novo (`scripts/sino.json`; ali nenhum aviso C1 "nasceu" porque todos já estavam aceitos). SINO_D. Caminhos que acrescentam avisos depois de
  abrir: `ui/tela_conferir._alertas_da_previa` (prévia e medida do "Para revisar" que chegam por trás), a medida por
  trás ao abrir (D-284) e `_medir_o_em_branco_por_tras` (`ui/tarefas.py`); o cartão da tela inicial lê o
  `resumo.json` gravado num momento anterior (por isso 27 × 25).
- **Ideia de conserto (sino):** medir o C1 uma vez (na análise do Automático, no tamanho do PDF) e não pôr nem tirar
  o aviso escondido depois; ou, se a medida por trás muda, avisar na faixa daquela página ("este aviso apareceu agora").
- **Ideia de conserto:** uma função só para "páginas do livro que vão para o PDF" (já existe `Projeto.paginas_ativas`),
  usada no Automático, na barra de baixo e na janela de salvar; se a tirada continuar numerada, dizer na tela
  ("134, 1 fora do livro").

### Erro 3 (D-680) — miniatura da página em branco
- **Causa:** `ui/tela_conferir._acertar_as_miniaturas_movidas` só troca a miniatura em dois casos: `inserida` (D-623,
  `_miniatura_branca`) e `_pagina_sai_movida` (D-547/D-649). `em_branco` não entra; a tira fica com a folha crua.
  A grade "Todas as páginas" (`_pagina_dentro_da_folha` → `miniatura_como_sai`) tem a mesma falta.
- **Gambiarra a evitar (§11.12):** é o caso típico de duas regras para a mesma coisa ("sai branca": `inserida` e
  `em_branco`). `core/pipeline._filtrar` já trata as duas juntas (`em_branco or inserida`); a tela não.
- **Ideia de conserto:** uma função "a página sai branca?" (a mesma do `_filtrar`) usada pela tira e pela grade.

### Erro 4 (D-681) — barra de baixo
- **Causa:** a barra (`ui/tela_conferir.py`, montagem ~l.1200-1250: `botoes_mostrar`, "antes / depois", "marcações",
  zoom, qualidade) é um `QHBoxLayout` sem regra de encolher/quebrar; com o painel da direita aberto a 1280 × 657 o
  espaço fica menor que a soma dos botões e o Qt corta o texto. Nesta rodada a janela grande (1582 lógicos) coube.
- **Ideia de conserto:** decidir o que some ou encolhe primeiro (ex.: "página N de M" vira "N/M"; textos dos botões
  com largura mínima garantida), na montagem da barra, para todas as ferramentas.

### Erro 6 (D-683) — folha espremida
- **Situação:** não reproduzido hoje (p.1, 2, 5, 8, 14 com a Mão: `pixmap_editor` na forma da página) nem na versão
  `51bdcb0b` (cópia `teste-kaique-lusiadas`, mesma rota; `_dados/saida-mao.txt`, prints `mao-*`). Depende de tempo.
- **Causa achada antes (agente graves, `relatorios/graves-2026-11-10/ONDE-PAREI.md`):** a folha crua devolvida como
  "imagem do PDF" pela procura da gravura por trás, esticada pela tela (`ui/tarefas.GerenciadorPrevias.
  _por_a_imagem_do_pdf`, `cv2.resize`). Consertada na origem em `88731637` (09/11), depois da versão do Kaique.
  Provas `tests/test_decisoes_gravura_a_mao.py::test_d659_a_tela_nao_troca_a_previa_pela_folha_crua` e
  `tests/test_graves_d649_miniatura_igual_ao_pdf.py::test_d649_a_o_mover_mostra_a_pagina_e_nao_a_folha_espremida`:
  rodei as duas hoje, passam (2 passed). A prova de que a primeira falha no código antigo é do agente graves, não
  refeita por mim.
- **Ponto fraco que continua:** o `cv2.resize` calado em `_por_a_imagem_do_pdf` (achado 1 do agente graves): qualquer
  outro caminho que entregue imagem de outra forma vira "folha espremida" em vez de erro visível.

### Erro 8 (D-685) — aviso velho na janela de salvar
- **Causa:** `ui/widgets/destino.py`: `campo_nome.textEdited` → só `_conferir()` (o aviso pequeno do seletor); o sinal
  `alterado` só é emitido em `escolher_pasta`. `ui/janela_confirmar.JanelaConfirmar` liga `destino.alterado` a
  `_reavaliar`, que é quem mostra/esconde `aviso_existe`. Trocar o nome nunca chama `_reavaliar`.
- **Origem (git):** seletor e `alterado` de `c3840ebd` (18/07, "Escolher onde salvar..."); a faixa `aviso_existe` e a
  ligação só ao `alterado` de `765a56f3` (08/08, "Secao 2, etapa 1 - barra de menu, e o destino sai da tela de
  trabalho", autor Claude); a docstring falsa "Chamado toda vez que o destino muda (sinal `alterado`)" de `c8ae8b6a`
  (25/09, "Comentarios explicativos no codigo"). O pedido: Pedido 5 de 18/07 ("avisar se já existir arquivo com o
  mesmo nome, oferecendo substituir ou renomear"; `historico/arquivo-morto/...68 pedidos).md` l.68).
- **Por que o teste não pegou:** `tests/test_barra_de_menu.py::test_a_janela_de_confirmar_avisa_que_vai_substituir`
  chama `janela.destino.definir(...)` e depois `janela._reavaliar()` à mão; nenhum teste digita no campo.
- **Outros caminhos:** a mesma faixa não aparece no caso contrário (abrir com nome livre e digitar o nome de um
  arquivo que existe): só o aviso pequeno cinza aparece; a pergunta "substituir / salvar como (2)" de
  `JanelaPrincipal._perguntar_sobre_substituir` continua protegendo o arquivo. O menu Arquivo > "Nome do arquivo..."
  não usa este seletor.
- **Ideia de conserto:** o seletor emite `alterado` também quando o nome muda (um sinal só para "o destino mudou"),
  e a prova digita no campo.

### Erro 9 (D-686) — frase velha depois de "tirar do livro"
- **Causa:** `ui/tela_conferir._atualizar_faixa` tem ramo para `em_branco` e para a conferida, não para `apagada`; cai
  em `_texto_tranquilo(aba)` ("Esta página vai sair em {filtro}" na Mão/marcar/Filtro/Mover; "Vou endireitar
  sozinho..." no Endireitar; "Vou cortar a borda sozinho..." no Cortar). `_conferida_na_faixa` já exclui `apagada`,
  e `_atualizar_os_botoes_da_pagina` já troca o botão para "trazer de volta": só a frase ficou.
- **Origem:** a frase "vai sair em" é de `d9fae8c2` (18/07); "tirar do livro" em toda página é de `82cdadae` (26/10,
  etapa 2 da obra), sem tocar a faixa.
- **Outros caminhos:** menu Página, grade "Todas as páginas" (tirar várias), no Dividir (folha `apagada`: o
  `_texto_tranquilo` do Dividir também não olha).
- **Ideia de conserto:** um ramo `apagada` em `_atualizar_faixa` (antes do texto da ferramenta), com o botão "trazer
  de volta", como o do `em_branco`.

### Erro 11 (D-688) — a lista volta ao topo
- **Causa:** `ui/automatico.ListaDeEtapas.refazer` (ligado a `estado.mudou`) faz `clear()` e recria todos os itens a
  cada mudança; o `QListWidget` volta a barra para 0. Medido: barra 2 → 0 ao marcar "6 Margens iguais" e "7 Montar
  cadernos" na janela a 1280 × 657.
- **Outros caminhos:** qualquer opção que mude o estado (caixinhas de dentro, combos, receita) e o painel Automático
  compacto (mesma classe).
- **Ideia de conserto:** em `refazer`, atualizar texto e caixinha dos itens que já existem (ou guardar e devolver a
  posição da barra), recriando só quando a ordem muda.

### Arquivo gravado fora do projeto
O 1º processar da fase a gravou `C:/Users/fotog/Documents/Editor de Impressao/lusiadas - preto e branco.pdf`
(18,7 MB, 14/11 13:07): com uma pasta de dados nova, a pasta de saída sugerida é Documentos. Nada dele foi substituído
(a pasta só tinha três PDFs do Gradus de 18/07). Não apaguei. A gerente pergunta ao Samuel se pode apagar.
