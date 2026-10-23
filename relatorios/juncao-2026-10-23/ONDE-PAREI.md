# Onde parei: junção da Fase 2 (23/10/2026)

- Ramo `juncao-fase2-2026-10-23`, saído do `origin/fase-1` em `3f753ca`. Worktree
  `.claude\worktrees\juncao-23` (junções `modelos`, `gabarito\paginas`, `gabarito\scantailor-24-09`:
  desfazer só com `(Get-Item <junção>).Delete()`).
- O `fase-1` **não foi tocado**. Quem põe no `fase-1` é a gerente, depois da suíte inteira no PC.
- Fora da pasta do projeto ficou a pasta de rascunho da compilação da DLL:
  `D:\programas\EditorImpressao-arquivos\ferramentas\build-st-ferramentas-juncao-23` (criada por mim;
  não apaguei: regra de 29/09).

## O que entrou (um merge `--no-ff` por ramo, nesta ordem)

| # | Ramo (ponta) | O que é | Commit da junção |
|---|---|---|---|
| 1 | `consertos-2026-10-21` (`2ff16e7`) | consertos | `f1313ba` |
| 2 | `fase2-para-revisar` (`f54428e`) | "Para revisar" (avisos por página) | `8a78f03` |
| 3 | `layout-etapas4a7-2026-10-19` (`a3f7240`) | layout etapas 4 a 7 (UPDF, tela cheia) | `c8963cf` |
| 4 | `fase2-caixa-conteudo` (`49d1ed3`) | 2.5, 2.13, 2.14 | `2745e1f` |
| 5 | `fase2-scantailor-itens-2026-10-19` (`c3b66fb`) | 2.8, 2.9, 2.11, 2.15, 2.12 (desentortar) | `31ea189` |
| 6 | `fase2-ferramentas-2026-10-22` (`d4c820b`) | 2.4, 2.6, 2.10+1.6, 2.16, 2.17, 2.18 (tinta A/B, papel da área), 2.19 | `99c2ce2` |
| - | DLL `st_ferramentas` versão 10 com tudo | | `f23c854` |
| - | acertos depois da suíte do GitHub | | `d746c8d` |

Não entraram (de propósito): `layout-antes-de-processar-2026-10-22` (rodada logo depois) e os ramos de verificação.

## Conflitos e como resolvi (o comportamento aprovado de cada lado ficou)

1. **"Para revisar" + layout** (`core/pipeline.py`, `ui/tarefas.py`, `ui/widgets/cartao_filtro.py`,
   `ui/tela_conferir.py`): somados. O `dpi_pedido` do "Para revisar" passou a ir até o
   `_filtrar_preto_no_branco` do 2.9 (os dois ramos mexeram no mesmo corpo); o cartão do filtro desenha nos
   pixels de verdade (layout) e com as marcas laranja do aviso (Para revisar).
2. **Caixa do conteúdo**: avisos 2.5 ao lado do 2.15 e do reforço; "Em quais páginas?" e a tela cheia dos
   filtros no `teste_botoes.py`; imports dos dois lados.
3. **2.12 no jeito do "Para revisar"** (como o ONDE-PAREI do `fase2-itens` pedia):
   - "Desentortar não usado" ganhou o segundo botão "está bom assim" (correção `revisar`);
   - "A página ainda saiu deformada": "Desfazer" (`desentortar_desfazer_aumento`) e **"Manter assim" virou o
     segundo botão do aviso** (correção `revisar`: aceita só este motivo; a página fica aumentada). O campo
     `Alerta.confirmar` (o "está certo" da faixa com outro nome) saiu;
   - `_aplicar_correcao` ganhou `desentortar_aumentando` e `desentortar_desfazer_aumento`;
   - `tests/test_desentortar_conferir_de_novo.py` ajustado a isso (os botões do aviso em vez do "está certo").
4. **2.14 (pintar de branco) com o 2.12 (desentortar)**, os dois desligados de fábrica: na ordem antiga pinta
   antes do desentortar (a área é medida na página inteira); na ordem nova pinta depois, **menos** com o
   "Desentortar aumentando a página" (a página muda de tamanho e a conta da área não vale: não pinta).
5. **2.16 (vários núcleos) + 2.15 + "Para revisar"** (`core/pipeline.py`): a análise em vários
   trabalhadores leva também o ângulo de cada página (para o "ângulo diferente das outras");
   `_pagina_pronta` usa o `dpi_pedido` do "Para revisar"; `acertar_faixa_do_livro` roda no fim dos dois
   caminhos do `_escrever_as_paginas`. 2.17/2.18 (`_filtrar_com_a_marcacao`, `_filtro_da_pagina`) recebem o
   `dpi_pedido` e o `no_pdf`.
6. **Lugares de tela** (controles mínimos de outros ramos no layout novo; mesmos nomes e controles; o lugar
   final é do agente de layout):
   - 2.17 "Igualar a luz", "Suavizar as letras", "Tirar o chuvisco": em "Mais ajustes" do painel Filtro (como
     2.9 e 2.11 foram em 22/10);
   - 2.18 "Área" (mostrar as áreas achadas, apagar, pintar de branco, copiar, colar): parte nova do painel
     Propriedades da ferramenta Marcar (o layout exige a fila embaixo da página vazia);
   - 2.16 "Velocidade", 2.19 "Medidas e receitas", 2.6 "Impressão": três partes novas no fim da lista das
     Configurações.
7. **DLL**: o código C++ de todos (caixas v4, saída v5-v6, desentortar v7-v9, luz v8) somado; `luz.cpp` foi
   posto em `namespace st_luz` (o `saida.cpp` tem a mesma classe `output::OutputGenerator::Processor` com
   outros membros; as duas no mesmo namespace seriam comportamento indefinido). Nada dentro das marcas
   "COPIADO SEM MUDANCA" mudou.
8. **Testes que precisaram de acerto** (`d746c8d`): espiões do `_filtro_da_pagina` em
   `tests/test_tinta_papel_preto_e_branco.py` (dois argumentos novos); `tests/test_aquecimento.py` (desde o
   conserto de 21/10 a carga que dá certo não marca `_tentou`; **o teste já falhava no próprio
   `consertos-2026-10-21`**, conferido numa cópia do `2ff16e7`).
9. `memoria/itens/*.md`: as duas atualizações de cada ficha ficaram (a do `fase-1` em cima).

## DLL `st_ferramentas`

Versão da interface **10** (acima de 4, 6, 8 e 9 dos ramos). Compilada com `compilar_st_ferramentas.py
--rascunho build-st-ferramentas-juncao-23`: 675 840 bytes, SHA-256
`95a0748bd4cba0d9b28c1c37945af4c44842f49a94ba6ffc1f03c2e1bf72beb2` (`core/nativo/st_ferramentas.txt`). O
autoteste do script passou (pontinhos, dividir, endireitar, caixas, preto e branco).

## Testes

- PC, um arquivo por vez: os 66 arquivos de teste que a junção muda (depois da DLL) + os 25 do layout logo
  depois do merge 3. Dois arquivos falharam e foram acertados (item 8); rodados de novo, passam.
- GitHub, suíte inteira + `teste_botoes.py`: rodada **39980124099** (`d746c8d`): 163 arquivos, **2690
  passaram, 0 falharam**, 113 pulados; botões **233 ações, 0 falhas**. (A primeira, 39978305829 em
  `f23c854`, deu as 8 falhas do item 8.)
- Filtro de velocidade `fase-1` x junção: rodada **39978310467** — ver abaixo.

## "Desligado de fábrica" junto

32 páginas do gabarito x Original / Preto e branco / Melhorar, cada página como livro novo pelo
`core.pipeline.processar` (`relatorios/fase2-novas/scripts/rodada_processar.py`), código do `fase-1`
(`3f753ca`) x junção (`f23c854`): **96 de 96 somas iguais**. Nenhum trabalho mudou o padrão de fábrica
nessas páginas. Arquivos: `somas-fase1-3f753ca.json`, `somas-juncao-f23c854.json` (nesta pasta).

## Ressalvas

- Com "Cortar seguindo o conteúdo" (2.5) **e** "Margens iguais" (2.4) ligados, a mesma folha muito grande
  pode ter dois avisos parecidos ("Página muito maior" e "Página bem maior que as outras"). Os dois são
  desligados de fábrica; não juntei os avisos (seria decisão de comportamento).
- 2.14 + "Desentortar aumentando a página": não pinta de branco (item 4).
- Os lugares de tela do item 6 são provisórios.

## Perguntas para o Samuel

Nenhuma que segure a junção.
