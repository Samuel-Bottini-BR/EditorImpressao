## Parte 2 — Para a gerente: a causa no código (não vai para o Samuel)

Versão lida e rodada: `obra-2026-10-26` em `c7e34fd8` (cópia `lusiadas-provas`). Teste de máquina = log e medidas do
piloto (`scripts/anotacoes-*.txt`, `scripts/analise*.json`); teste de olho = os prints abertos um por um.

### Erro 1 (D-678) — remendos na página 14
- **Causa:** a marcação da página 14 tem 4 regiões `LETRA` de origem `rede` (o modelo de regiões, `core/rede_selecao.py`
  / `core/detectar_regioes.py`) dentro da pintura: peito do homem da direita e nuca/rosto do da frente
  (`prints/analise/p14-2-marcado.jpg`). Em `core/filtros.aplicar_filtro_com_selecao` → `_preto_e_branco_com_gravura`, a
  pintura vira cinza só onde `peso_gravura > 0`; o resto recebe a `binaria` da página inteira. As regiões de letra
  ficam fora da zona de gravura → retângulos em 1 bit no meio do cinza.
- **Outros caminhos:** a mesma marcação vale na prévia, nas figurinhas, no "antes / depois", na tela cheia e no PDF
  (`_filtrar_com_a_marcacao` é o ponto único). "Gravuras em tons de cinza" NÃO resolve
  (`prints/analise/p14-5-com-gravuras-em-cinza.png`): a regra continua "letra fora da gravura". "Só as letras" não
  testado aqui.
- **Ideia de conserto:** num ponto só (`garantir_selecao` ou a união das regiões da máquina), letra achada pela rede
  que fica cercada por gravura e não tem forma de linha de texto passa a contar como gravura.

### Erro 12 (D-689) — página 22 suja
- **Causa:** página quase branca (cinza 249 a 255 no desenho de 300 DPI). `algoritmo_preto_branco = "auto"` →
  `core/filtros.escolher_algoritmo_automatico` limiariza a página com Otsu e mede a "espessura do traço" dessas manchas
  de papel; dá traço grosso → escolhe Otsu. Otsu numa página sem tinta separa dois tons de papel: 10,7% de preto.
  Sauvola na mesma página: 0,0%; Wolf: 6,6% (`scripts/analise.json`, `prints/analise/p22-pb-*.png`). Não há
  verificação de contraste mínimo antes de escolher.
- **Outros caminhos:** toda página em Preto e branco "auto" sem gravura e quase vazia (versos em branco do livro todo;
  o aviso "Parece em branco" marcou 7 no teste do Kaique). O aviso `em_branco` acerta, mas não muda nada sozinho.
- **Ideia de conserto:** em `escolher_algoritmo_automatico`, página sem contraste de tinta (ex.: diferença entre os
  percentis claros e escuros menor que um limite) fica no Sauvola; a mesma regra serve a prévia e o PDF (já é uma
  função só).

### Erro 13 (D-690) — pintura da página 8
- **Causa:** a pintura FOI achada (gravura 55% da página, origem `rede`). `_tipos_das_zonas` classificou a zona
  única como "desenho" (nem foto/pintura, nem enfeite) → `_desenho_em_preto_e_branco` (traço em 1 bit): o cinza
  claro vai a branco. Além disso, partes do céu e do mar claros foram marcadas `PAPEL` (amarelo em
  `p8-2-marcado.jpg`) → branco. Com `gravuras_em_tons_de_cinza=True` (D-588) a página sai inteira em cinza
  (`p8-5-com-gravuras-em-cinza.png`). Mesma família da D-585 (pintura confundida com enfeite, aceita até depois).
- **Outros caminhos:** prévia, figurinhas e PDF passam pela mesma função; vale para toda pintura clara de pincel.
- **Ideia de conserto:** é decisão do Samuel (ver o que ele escolhe): ou a pintura clara passa a contar como pintura
  em `_tipos_das_zonas` (regra de imagem, precisa medida e teste em mais livros), ou o aviso da página leva a
  "Gravuras em tons de cinza".

### Erro 5 (D-682) — página deitada no arquivo para imprimir
- **Causa (duas peças):** (1) o Dividir (`core/dividir_scantailor` / motor "o do ScanTailor") pôs a linha fora do meio
  nas folhas sem lombada visível (folha 2 em 0,239; folha 7 em 0,732, ambas com `lombada_incerta`, `confianca_corte`
  1,0 gravada mesmo assim); a página que sobra fica mais larga que alta. (2) `core/impressao._gira` gira 90° toda
  página "deitada" (largura > 1,02 × altura) numa vaga em pé (`rotacao_automatica=True` de fábrica). O aviso
  `_avisos_de_giro` existe, mas `ui/dialogo_impressao._terminou` só o mostra depois de gravar, no fim da coluna da
  direita, abaixo de "Como imprimir" (fora da vista; `prints/crus/a-21`).
- **Outros caminhos:** qualquer página larga (folha não dividida, página com "Mover" para folha deitada) gira igual;
  "mandar para a impressora" também (mesma `montar_para_impressao`).
- **Ideia de conserto:** o aviso aparecer antes de gravar (na prévia da janela, junto da folha) e a página larga que
  veio de uma folha dividida com "Lombada incerta" ser apontada no "Antes de processar" — sem girar escondido.

### Erro 7 (D-684) — laranja com a Mão
- **Causa:** `ui/tela_conferir._mostrar_as_achadas` liga `editor_selecao.mostrar_achadas` quando
  `pagina.precisa_revisao` (D-237, 08/10: "no para revisar, elas já vão aparecer laranjas"), qualquer que seja a
  ferramenta. O botão "marcações" (D-580/D-584) só controla `mostrar_marcacao` (as cores); o `paintEvent` de
  `ui/widgets/editor_selecao.py` pinta o laranja das achadas sempre, de propósito (docstring: "Arriscado: pôr o
  _pintar_achadas_e_escolhida de volta dentro do if"). Depois do Automático quase toda página tem aviso → laranja em
  quase todas. São duas decisões que se cruzam: precisa da escolha do Samuel.
- **Outros caminhos:** Zoom igual à Mão; "Duas lado a lado" e "antes / depois" com a peça do editor (D-612).

### Erro 10 (D-687) — códigos na tela
Busca em todos os textos de `ui/` (`scripts/codigos_na_tela.py` → `scripts/codigos_na_tela.txt`; strings que não são
docstring nem comentário):
- `ui/automatico.py:2285` — texto à vista na etapa Dividir: "só quando esta etapa roda **(G2)**".
- `ui/automatico.py:765-767` — balão do botão "desligar as marcadas": "(**D-068**: toda função automática liga e
  desliga)".
- `ui/automatico.py:2304-2305` — balão da lista "Quando o ângulo muda depois do corte à mão, o corte:": "**D-094**: a
  mesma escolha existe nas Configurações...".
- Não são código interno: "(F1)" (`ui/tela_inicio.py:183`, é a tecla) e "A4" (tamanho de papel). Em `core/`, os textos
  com "item 2.11", "item 2.12", "item 1.2", "item 2.2", "item 2.8" vão só para o `erros.log`, não para a tela.
- Os três vieram juntos no commit `e2321b16` (26/10, "Etapa 3: ... painel Automático e janela grande de verdade").
- **Ideia de conserto:** tirar os três e pôr em `tests/test_decisoes*.py` uma prova que varre os textos de `ui/` com o
  mesmo padrão (pedido da própria D-687).
