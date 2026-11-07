# Cunha do giro com o Desentortar ligado e a página segurada (06/11/2026)

Ramo `cunha-desentortar-2026-11-06`, cópia `.claude/worktrees/cunha-desentortar`, a partir do `obra-2026-10-26` (`afd730e5`).
Base: investigação de 06/11 (`.claude/worktrees/investiga-desentortar/relatorios/investiga-desentortar/RESULTADO.md`).

## Decisões que esta tarefa precisa cumprir

- **D-095** (12/10/2026), ressalva do G6 aprovada com "Está bom": "cunhas brancas com corte até a beirada (Boécio 8, Marial 7, Graduale 221)" a consertar.
- **D-639** (06/11/2026), Samuel: "pode consertar o triangulo, mas ainda não entendi." · "e se o fundo do papel fosse branco? no caso o fundo atrás da folha que estamos trabalhando." · "eu criei uma regra para isso?" · "vamos continuar assim, mas deixe anotado que eu quero ver mais afundo essa funcionalidade." → O cantinho do giro continua com a cor do papel da página (a mediana do papel de dentro do corte; nunca a cor do fundo atrás da folha), e passa a ser assim também quando o "Desentortar" está ligado e a página sai sem desentortar.
- **D-105** (22/10/2026): "a página sai sem desentortar e vai para o 'Para revisar'". **Não pode mudar**: a proteção continua segurando a mesma página.
- **D-108** (22/10/2026): "o aviso deve perguntar e não fazer automaticamente". **Não pode mudar**: o aviso continua aparecendo.

## O que já está escolhido e testado aqui

Arquivo que vou tocar: só `core/pipeline.py`, função `_desentortar_com_o_papel_em_volta` (o caminho do Desentortar ligado).
Não toco em `core/endireitar.py` nem em `core/desentortar_scantailor.py` (uso a conta que já existe).

Decisões que passam por ali:
- D-095 / etapa 10a: cunha com a cor do papel no caminho desligado (`_preparar_endireitando_antes`, `rotacionar_e_cortar(..., cunha_com_o_papel=True)`). Não muda.
- D-105, D-106, D-108 (proteção e avisos "Desentortar não usado" / "A página ainda saiu deformada"). A DLL continua recebendo exatamente a mesma página (com a cunha branca de hoje), então a proteção decide igual.
- D-112 (medida na resolução do livro, guardada; a tela usa a mesma página reduzida). A página guardada passa a ter a cunha da cor do papel; o resto igual.
- D-113 (moldura escura pintada só na cópia que a proteção mede). Não muda.
- Escolha do 2.12 (22/10, "cortar uma vez só, no fim"): a página vai inteira ao desentortar. Não muda.
- Ordem "cortar_antes" (projeto de antes de 09/10): idêntica ponto por ponto. Não muda (lá o caminho desligado não pinta a cunha).

Testes que já existem e precisam continuar passando:
- `tests/test_desentortar_conferir_de_novo.py` (hoje falha só no Destino 18: `assert 2292 == 0`; é o defeito desta tarefa).
- `tests/test_desentortar_protecao.py`, `tests/test_desentortar_scantailor.py`, `tests/test_desentortar_medida_por_tras.py`, `tests/test_desentortar_na_tela.py`.
- `tests/test_decisoes.py` (inclui `test_d095_cunha_do_giro_nao_fica_branca_na_beirada`), `tests/test_etapa10a_nao_comer.py` (`test_reversao_boecio_8_sem_cunha_branca_na_beirada`), `tests/test_borda_preta.py`.
- `tests/test_decisoes*.py`.

## Como fica para quem usa e no livro

O que o Kaique faz: abre o livro, liga o "Desentortar" (automático), confere a página.

- **Antes:** na página que o programa não consegue desentortar (ex.: Destino do socialismo p. 18, direita), aparece o aviso "Desentortar não usado" e a página vai para o "Para revisar". A página sai reta, sem desentortar, mas com uma lasca branca fina na beirada (até ~1 mm, afinando), ao lado do papel amarelado. Com o Desentortar desligado essa lasca já saía da cor do papel.
- **Depois:** o mesmo aviso, na mesma página, com o mesmo botão "Desentortar aumentando a página". A lasca sai da cor do papel, igual à página com o Desentortar desligado.
- **No PDF:** só muda essa lasca (alguns milímetros quadrados na beirada), nas páginas com o Desentortar ligado que a proteção segurou. Em "Preto e branco" a lasca já virava branco; em "Original" e "Melhorar" ela deixa de aparecer. As páginas desentortadas de verdade, as do Desentortar desligado e os projetos antigos (antes de 09/10) não mudam.
- **Velocidade:** só as páginas seguradas fazem uma conta a mais (girar de novo só o pedaço do corte); as outras, nada.

## Andamento

- [x] Cópia e ramo criados.
- [ ] Conserto
- [ ] Prova D-095 com o desentortar ligado + reversão no código antigo
- [ ] Testes no PC
- [ ] GitHub (suíte + velocidade)
- [ ] Antes/depois Destino 18

## Perguntas para o Samuel

(nenhuma até agora)
