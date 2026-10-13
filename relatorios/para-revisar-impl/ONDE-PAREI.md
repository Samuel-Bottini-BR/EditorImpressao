# O "Para revisar" da Fase 2: onde parei

Implementador, 12/10/2026. Ramo `fase2-para-revisar` (saiu do `fase-1` em `9c51801`), cópia em
`.claude/worktrees/para-revisar`. Bloco do plano: "Decidido pelo Samuel, a fazer: o 'Para revisar'"
(PLANO-DEFINITIVO, Fase 2). **Nada aqui está aprovado: é para o verificador conferir.**

## O que está feito

**PRONTO PARA CONFERIR** (os seis itens estão no programa e funcionam nos testes de máquina; falta o olho
do verificador na janela e duas decisões, escritas nas ressalvas 1 e 2).

Commits no ramo (todos no GitHub):

| Commit | O que é |
|---|---|
| `7695b46` | Item 1: a regra ajustada (e, nos mesmos arquivos de `core/`, as peças dos itens 2, 4 e 6 ainda sem tela) |
| `90d0708` | Item 6, parte sem tela: a lista dos avisos e o "está bom" por motivo; testes de "Deixar em branco" e da força sozinha |
| `fbe0b7f` | Itens 2 a 6 na tela: botões do aviso, lugar marcado, lista ao processar, "está bom" em cada nível, caixinha da força |
| `2e400c8` | Junção do `fase-1` (G6, `8968704`), pedida pela gerente; dois conflitos de linhas vizinhas |
| `8923370` | A regra só é medida na resolução do PDF; a tela mede por trás (achado da conferência nas 89 páginas) |

### O critério de aceite (89 páginas do estudo)

| Como conferi | Vão | Certas | Decidem diferente do estudo |
|---|---|---|---|
| Aviso de antes (do estudo) | 55 | 52 | |
| Regra ajustada, **a conta do programa sobre as máscaras do estudo** (`conferir_89.py`) | **21** | **78** | nenhuma; os números de cada sinal batem um a um |
| **O programa de verdade**, 300 DPI, página preparada como no dia do estudo (`--programa --preparo-do-estudo`) | **21** | **78** | nenhuma |
| O programa de verdade, 300 DPI, preparo do livro novo de hoje (G6 + conta do ScanTailor) | 20 | 73 | 7 (ressalva 1) |
| O programa de verdade, 110 DPI (a prévia), sem a força sozinha | 39 | 60 | 22 (por isso a prévia não mede mais) |

Os resultados página a página estão nos `conferir-89-*.json` desta pasta.

### Testes de máquina

- Novos: `tests/test_revisar.py` (25), `tests/test_avisos.py` (24), `tests/test_para_revisar_na_tela.py` (20);
  refeitos: os do aviso em `tests/test_misto_no_programa.py` (31 no arquivo).
- A suíte inteira, um arquivo de pytest por vez: antes da junção do `fase-1`, 114 arquivos, 2036 passaram,
  nenhum falhou; depois da junção, 115 arquivos, 2080 passaram, nenhum falhou (`test_ordem_do_preparo.py`: 43).
  Depois da última mudança (a medida por trás) rodei só os arquivos mexidos e os vizinhos (`test_misto_no_programa`,
  `test_para_revisar_na_tela`, `test_avisos`, `test_revisar`, `test_misto_consertos`, `test_misto_na_tela`,
  `test_tirar_fundo_no_programa`): todos passaram. **A suíte inteira não foi rodada de novo depois dela.**
- `conferir_na_tela.py`: a tela de conferir de verdade (sem aparecer no monitor), com os fios de verdade, em três
  páginas reais: Antiphonal 46 (aviso, marca, "Trazer de volta"), Camões 27 (força sozinha, "Desfazer"),
  Egenloff 12 ("Página sem conteúdo", "Deixar em branco"). Tudo certo.
- Tempo da conta da regra: 268 ms por página em média nas 89 (30 ms por milhão de pontos; a mais lenta 1,09 s),
  só nas páginas em "Só as letras" (jeitos "Guardar a tinta forte" e "Guardar só o texto").
  **O `teste_velocidade.py` não foi rodado** (fica para o verificador).

## O que cada pedido virou no programa

| # | Pedido do Samuel | O que o programa faz agora | Onde |
|---|---|---|---|
| 1 | Regra ajustada (`rv4-resumo`: "Fica assim") | No "Só as letras", a página vai para a lista por: desenho apagado, texto falhado, página sem conteúdo, figura além da gravura achada, faixa escura na beirada. O aviso "Tinta forte fora do texto" não existe mais (sai sozinho do projeto antigo). No "Guardar só o texto" vale a conta de antes (tinta forte apagada acima de 10%), com nome novo. A faixa em 70% ou mais das páginas medidas vira um aviso só, do livro. | `core/revisar.py`, `core/pipeline.py` (`_acertar_avisos_do_misto`, `acertar_faixa_do_livro`), `core/analise.py` |
| 2 | Um aviso para cada coisa, dois botões (`rv5-em-branco`) | "Parece em branco" e "Página sem conteúdo" são dois avisos; cada um com "Deixar em branco" (folha branca no lugar, a página fica no livro) e "Tirar do livro" (o apagar de sempre). | `core/analise.py` (`Alerta.botoes`), `modelos.ConfigPagina.em_branco`, `core/pipeline._filtrar`, `ui/tela_conferir.py` |
| 3 | Conserto rápido como botão do aviso (`rv4-conserto-desenho`, `rv5-erro-1-desenho`, `rv5-erro-6-so-texto`) | "Trazer de volta nesta página": no desenho apagado troca a página para "Guardar tudo"; no "Guardar só o texto" troca para "Guardar a tinta forte". O lugar onde sumiu aparece em retângulo laranja tracejado nos cartões de filtro e na aba Marcar. | `core/revisar.caixas_de`, `core/pipeline.marcas_do_aviso`, `ui/widgets/cartao_filtro.py`, `ui/widgets/editor_selecao.py` |
| 4 | Força do preto sozinha (`rv4-erro-4-texto-falhado`) | Texto falhado: o programa põe a força do preto em 85 só nessa página, filtra de novo e mostra o aviso "Força do preto escurecida", com "Desfazer". Caixinha para ligar e desligar na tela "O que fazer" (regra 8 do plano). Livro novo: ligado; projeto antigo: desligado. | `core/pipeline` (`_reforcar_se_o_texto_falhou`, `acertar_aviso_do_reforco`), `modelos`, `ui/tela_opcoes.py` |
| 5 | "Antes de processar" lista as páginas e os motivos (`rv5-aviso-so-texto`) | A janela mostra uma linha por motivo de cada página, com "ver" e "continuar assim mesmo". | `ui/janela_dos_avisos.py`, `ui/tela_conferir._pedir_processamento` |
| 6 | "Está bom" em cada nível (`rv4-aviso-so-texto`) | Página inteira: "está certo" da aba (como antes). Um motivo de uma página: "está bom assim" do aviso. Um motivo em todas: "está bom: todas" no painel. Tudo: "está bom em tudo" no painel. As que ele escolher: "ver a lista…" (a mesma janela, com caixinhas, "Selecionar todas" e "Nenhuma"). Tudo com Ctrl+Z. O aviso some sozinho quando o problema é resolvido (a conta é refeita a cada desenho). | `core/avisos.py`, `modelos` (`alertas_aceitos`), `ui/widgets/paineis.py`, `ui/tela_conferir.py` |

## O que o verificador precisa conferir na janela

Abrir um livro, tela "O que fazer": Preto e branco, "Só as letras" marcada (de fábrica "Guardar a tinta
forte"). Pasta de dados de teste, nunca a do Samuel.

| O que | Página | O que tem de aparecer |
|---|---|---|
| Letra grande que some | Antiphonal 1547, p. 46 (`D:\Livros para editar\Antiphonal 1547.pdf`) | Aviso "Desenho apagado"; retângulo laranja em volta da letra T nos cartões e na aba Marcar; botão "Trazer de volta nesta página" traz a letra (a página passa a "Guardar tudo") e o aviso some sozinho; Ctrl+Z desfaz. |
| "Guardar só o texto" apaga a música | Graduale p. 222 (gabarito), com "Guardar só o texto" | Aviso "Sumiu algo no 'Guardar só o texto'", pautas marcadas, "Trazer de volta nesta página" troca só essa página para "Guardar a tinta forte". |
| Texto falhado e força sozinha | Camões p. 27 e p. 104; Egenloff p. 3 (`D:\Livros para editar\...`) | A força do preto vai sozinha para 85 só nessas páginas (o medidor mostra), aviso "Força do preto escurecida" com "Desfazer". No Egenloff 3 o aviso "Texto falhado" fica junto (a força não resolve o vermelho). Com a caixinha desligada em "O que fazer": só o aviso "Texto falhado", com "usar mais escuro". |
| Página sem conteúdo | Egenloff p. 12, Rariora p. 8 | Aviso "Página sem conteúdo" com "Deixar em branco" e "Tirar do livro". "Deixar em branco": a prévia fica branca, a página continua na tira e no PDF (mesmo número de páginas). "Tirar do livro": some do PDF. |
| Parece em branco | qualquer folha branca de verdade | Aviso "Parece em branco" com os mesmos dois botões. |
| Não vão mais para a lista | Graduale 221 a 223, Palatino 9, 10, 57 (moldura e música guardadas) | Nenhum aviso (antes: "Tinta forte fora do texto"). |
| "Antes de processar" | qualquer livro com avisos, clicar "Confirmar e processar" | Lista "Página N - motivo"; "ver" leva à página e não processa; "continuar assim mesmo" processa; fechar no X não processa. |
| "Está bom" | livro com vários avisos | Os quatro níveis do item 6, cada um com Ctrl+Z; o contador e o painel acompanham. |
| Faixa do livro | Egenloff ou Matemática, vendo 4 ou mais páginas | A faixa sai das páginas e vira uma frase do livro (ver ressalva sobre onde a frase aparece). |
| Projeto antigo | um projeto salvo antes de 12/10 com "Tinta forte fora do texto" | Abre; o aviso antigo some; nenhuma força muda sozinha. |

## Ressalvas

1. **Com o preparo do livro novo de hoje, 7 das 89 páginas decidem diferente do estudo (20 vão, 73 certas).** A
   regra foi acertada em páginas preparadas como no programa de 07/10 (corta antes de endireitar, conta do
   endireitar do programa). Com o G6 (endireitar antes de cortar) e a conta do ScanTailor, as máscaras mudam um
   pouco e as páginas na beirada do limite trocam de lado: a letra T do Antiphonal 46 dá 1,43 (limite 1,5) e
   deixa de ir; Egenloff 3 (1 linha falhada em vez de 2), Matemática 72 e Antiphon 260 mudam; Cursus 3, Opus
   Majus 20 e Palatino 66 passam a ir. Com o preparo do estudo, o programa dá exatamente 21 e 78. **Não mexi
   nos limites aprovados.** Decisão para a gerente e o Samuel: aceitar assim, ou reacertar os limites no
   preparo novo (precisa de estudo e de olho).
2. **A regra só é medida na resolução do PDF, não na prévia.** A 110 DPI ela erra (39 vão, 60 certas). A tela
   pede, por trás, um desenho na resolução do PDF só para medir a página da vez: custa um desenho desse
   tamanho por página visitada e por mudança de filtro, força ou corte nela (segundos, em fila atrás da
   prévia; nada congela). As páginas vizinhas não são medidas sozinhas (antes o aviso antigo aparecia também
   nas 3 páginas seguintes, que a prévia adianta); as não visitadas só são medidas ao gerar o PDF. Então a
   janela "Antes de processar" só lista o que já foi medido, e a força do preto sozinha pode agir numa página
   nunca vista só na hora do PDF (o aviso fica no livro para depois). Se o Samuel quiser todas medidas antes,
   é uma varredura do livro inteiro na resolução do PDF (pesada): não fiz.
3. **A regra só vale no "Só as letras" com "Guardar a tinta forte" ou "Guardar só o texto"** (é onde o programa
   sabe onde está o texto, e onde o estudo mediu). No "Guardar tudo" e no Preto e branco sem "Só as letras" não
   há aviso nenhum da regra: uma página sem conteúdo ou de texto falhado não é avisada ali. Por isso "Trazer de
   volta nesta página" (que troca para "Guardar tudo") tira todos os avisos da regra daquela página.
4. **"Trazer de volta" troca a página inteira de jeito**, como o Samuel escolheu (opção 1); o retângulo laranja
   só mostra onde sumiu, não é uma zona que se ajusta. Marcar "letra e traço" à mão em volta da letra NÃO a
   traz de volta hoje (o "Guardar a tinta forte" apaga do mesmo jeito): a rodada 5 dizia que trazia. Vai para
   a Lista de bugs (abaixo).
5. **Campos novos no `projeto.json`** (todos com padrão; projeto antigo abre igual): na página `em_branco`,
   `alertas_aceitos`, `forca_antes_do_reforco`, `reforco_desfeito`, `faixa_na_beirada`; na folha
   `alertas_aceitos`; no livro `reforcar_texto_falhado` (livro novo ligado; projeto antigo desligado). É
   mudança de formato de dados: entendi que as decisões das rodadas 4 e 5 a autorizam, como nos itens
   anteriores; confirmar.
6. **"Deixar em branco" só aparece nos dois avisos** ("Parece em branco" e "Página sem conteúdo"); os dois botões
   em qualquer página são da Lista de espera (Fase 6) e não foram feitos. A tecla Delete continua "apagar".
7. **O aviso "Parece em branco" continua com a conta de antes** (o erro da Gladstone 18, que tem título, está
   na Lista de bugs de 08/10 e não foi consertado aqui; a regra nova, "Página sem conteúdo", não a pega).
8. **Faixa do livro**: a frase "as páginas deste livro têm uma faixa escura na beirada: confira o corte" aparece
   no painel "Para revisar". As outras frases do livro (ex.: "o livro inteiro é colorido") continuam num
   rótulo que está escondido na tela de hoje (ver Lista de bugs).
9. **A força sozinha**: depois de reforçar, a página é medida de novo já com a força nova (um filtro a mais só
   nessas páginas). O reforço é 85, o valor testado na rodada 4. No Egenloff 3 (texto vermelho) ele não
   resolve e o aviso "Texto falhado" fica junto. Se a pessoa mexer no medidor depois do reforço, o "Desfazer"
   some e o programa não reforça de novo aquela página.
10. **Três commits em vez de seis**: escrevi os seis itens enquanto a medição de velocidade ocupava o PC (sem
    poder rodar nada), e os arquivos de `core/` ficaram com mais de um item. As mensagens dizem o que cada um traz.
11. **Não rodei o programa na janela de verdade** nem o `teste_botoes.py` (ele foi ensinado a fechar a janela
    nova, mas não foi rodado). A aparência é provisória, do jeito mais simples: é do agente de layout.
12. Um arquivo vazio meu ficou fora do projeto por engano: `C:\Users\fotog\AppData\Local\Temp\p2.py` (0 bytes,
    12/10 19:22). Não apaguei (regra de 29/09): a gerente decide.

## Bugs para a Lista de bugs (não consertados, não impedem)

| Data | Bug | Onde |
|---|---|---|
| 12/10/2026 | Marcar "letra e traço" à mão não protege a tinta do "Guardar a tinta forte" nem do "Guardar só o texto": a letra grande marcada some do mesmo jeito (a rodada 5 mostrou ao Samuel, em simulação, que voltava). | `core/misto.py` (`_fora_do_texto` só olha as linhas do leitor e a gravura) |
| 12/10/2026 | As observações do livro ("o livro inteiro é colorido", "este livro tem uma página por folha"...) são escritas num rótulo de um cabeçalho escondido: o Kaique não as vê. | `ui/tela_conferir.py` (`rotulo_observacoes`, `_montar_cabecalho`) |
| 12/10/2026 | (consertado, por impedir o botão novo) Os botões "usar mais fraco" / "usar mais escuro" dos avisos "Ficou escura" / "Texto quase sumiu" chamavam um método que não existia (`_escolher_forca`) e davam "Não consegui fazer isso agora". | `ui/tela_conferir.py` |
| 12/10/2026 | Com o preparo do livro novo, o Siebmacher 7 e 9 continua sem ser dividido sozinho (já anotado na rodada 4); nos scripts continua dividido à mão. | divisão do ScanTailor |

## Ideias para a Lista de espera

- Medir o livro inteiro na resolução do PDF por trás, com barra de andamento, para a lista "Para revisar" e a
  janela "Antes de processar" ficarem completas antes de processar (ressalva 2).
- Reacertar os limites da regra no preparo novo (G6), com um livro novo no estudo (ressalva 1).
- Fazer a marcação "letra e traço" à mão valer contra o apagar do "Só as letras" (bug acima), para o
  retângulo laranja poder virar uma zona ajustável, como o Samuel descreveu ("como na opção 3").
