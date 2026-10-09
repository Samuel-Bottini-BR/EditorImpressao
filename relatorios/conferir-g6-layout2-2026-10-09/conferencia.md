# Conferência de 09/10/2026: endireitar antes de cortar (G6) e tela de trabalho sem abas

Verificador. Dois trabalhos prontos que ainda não entraram no programa (`fase-1`). **Nenhum dos dois está aprovado: só o Samuel marca.**

Página de conferência (imagens grandes, Aprovado / Melhorar / Descartar e comentário, resposta salva na hora):
https://claude.ai/artifact/J8AwcyyUwrZ2n7kSevyGvX

Defeito conhecido, não é destes trabalhos: moldura dourada e iluminura ainda não saem certas nos filtros (itens 1.4 e 1.5). Aqui todas as páginas estão no filtro Original.

## 1. Endireitar antes de cortar (item 2.2, G6), ramo `fase2-endireitar-2` (44cbf21)

**PRONTO PARA CONFERIR.** Minha opinião: melhora os cantos na maioria das páginas, mas piora a margem de cima em duas e ainda deixa cunha branca quando o corte vai até a beirada da folha.

### Máquina

| O que | Resultado |
|---|---|
| Testes automáticos, Windows do GitHub (rodada 37986736160) | 1991 passaram, 0 falharam, 72 pulados |
| teste_botoes.py (mesma rodada) | passou |
| Velocidade (rodada 37987258208, 3 repetições de cada) | inconclusiva (ver abaixo) |
| Palatino 66 e Horas 27 (sem giro) | idênticas ao fase-1, diferença zero em todos os pontos |

Velocidade: as máquinas do GitHub variam até 70% na mesma versão. Em máquinas iguais (EPYC 7763), igual: abrir o livro 64 s antes, 60 e 65 s depois; Mágico pro 77 s antes, 72 e 75 s depois. Em outro par de máquinas iguais (EPYC 9V74), mais lento depois: abrir o livro 53 s antes e 71 s depois; Mágico pro 64 s antes e 80 s depois. O implementador mediu cerca de 0,05 s a mais por página. **Ressalva grave pela regra 6 até medir no PC do Samuel.**

### Olho (12 páginas, livro novo, filtro Original; abri as 37 imagens)

Como foi feito: script novo `.github/scripts/antes_depois_endireitar.py`, job `antes_depois` do workflow (rodada 37991590406). Antes = fase-1 (d04bd11). Depois = fase2-endireitar-2 (44cbf21). Imagens no ramo `prints-testes`, pastas `2026-10-09_2111_*_antes-depois`.

| Página | O que vi | Opinião |
|---|---|---|
| Graduale 221 (item 2.2) | Antes: tiras brancas em cima à esquerda, na direita e embaixo à direita. Depois: quase todas somem; sobra fio branco embaixo à esquerda. Pautas retas nas duas. | melhor |
| Graduale 222 | Antes: tiras brancas à esquerda e embaixo; primeira pauta quase no alto. Depois: sem tiras e com papel acima. Sombra da lombada continua à direita nas duas. | melhor |
| Escola 7 (item 2.2) | Depois tira a faixa e a linha escura do alto, mas o título fica colado na borda de cima e as letras encostam nos lados. | pior em cima |
| Escola 35 | Fio branco no alto some; o resto igual. | um pouco melhor |
| Siebmacher 7 | Praticamente igual; fundo preto do scanner nos cantos da direita nas duas. | igual |
| Siebmacher 9 | Some a tira branca embaixo à esquerda, mas a moldura de cima fica colada na borda. Fundo preto nos cantos da direita nas duas. | um pouco pior em cima |
| Palatino 66 | Idênticas (ângulo zero). | igual |
| Horas 11 | Tiras brancas da direita somem; margem à direita da iluminura um pouco mais estreita. As duas contas do ângulo discordam (-0,5 e +0,6 graus). | melhor |
| Horas 27 | Idênticas (ângulo zero). | igual |
| Opus Majus 20 | Fio branco à direita e embaixo some. | um pouco melhor |
| Boécio 8 | Somem as tiras de antes, mas aparecem cunhas brancas na beirada esquerda em cima e direita embaixo. | troca um defeito por outro |
| Marial 7 | Tiras menores, mas ainda cunha branca em cima à esquerda e embaixo à direita. | melhor, não resolvido |

### Ressalvas

1. **Achado novo:** quando o corte automático vai até a beirada da folha (Boécio 8, Marial 7, Graduale 221 embaixo à esquerda), o giro ainda deixa cunha branca. No log, o corte dessas páginas começa ou termina em 0 ou 1 (por exemplo Boécio: esquerda 0 e direita 1; Marial: cima 0 e baixo 1).
2. Escola 7 e Siebmacher 9: o corte novo encosta no que está impresso no alto (título e moldura). Escola 7 já era ressalva conhecida.
3. Cunhas brancas nos cantos da ferramenta Cortar (conhecida); Graduale 222 com a sombra da lombada (conhecida).
4. Não conferi por olho: projeto antigo sair igual ao de hoje, e o retângulo do corte à mão ficar no mesmo lugar quando o ângulo muda. Só existe o teste de máquina do implementador (`tests/test_ordem_do_preparo.py`).
5. Velocidade sem veredito (ver acima).

## 2. Tela de trabalho sem abas (layout, etapa 2), ramo `layout-impl-2026-10-08` (a783bd9)

**PRONTO PARA CONFERIR.** Minha opinião: a tela ficou mais limpa e a página ganhou espaço; as ressalvas são de acabamento.

### Máquina

| O que | Resultado |
|---|---|
| Testes automáticos, Windows do GitHub (rodada 37986429190, código e306e1c; a783bd9 só muda o ONDE-PAREI) | 1965 passaram, 0 falharam |
| teste_botoes.py (rodada 37991595697, a783bd9) | 166 ações, 0 falhas |
| Velocidade | não medida (trabalho só de tela) |

### Olho (13 telas, prints da janela real, Windows do GitHub 1920 x 1080; abri as 25 imagens)

Antes: rodada 37991592793 (fase-1, d04bd11). Depois: rodada 37991595697 (a783bd9). Pastas `2026-10-09_2114_*` do ramo `prints-testes`. Acrescentei ao roteiro de prints as telas Dividir, Filtro, Marcar e o grupo Contornar aberto.

| Tela | O que vi |
|---|---|
| Inicial (três temas) e O que fazer | iguais; menus à esquerda |
| Conferir ao chegar | sem abas; Dividir aceso na fila; nome e frase na linha dos menus; página maior; barra de baixo com folha 1 de 6, desfazer, refazer, histórico, contagem |
| Cortar, tela cheia | página maior, fila de botões cabe |
| Endireitar, tela cheia | mesmos controles em duas linhas; frase curta na linha dos menus |
| Cortar, 1280 x 657 | voltar ao automático e Proporção travada cortados; girar vira só ícones |
| Endireitar, 1280 x 657 | cabe |
| Dividir, tela cheia | igual, página maior |
| Os quatro filtros | páginas maiores; a frase A mesma página nos quatro filtros aparece duas vezes |
| Marcar retângulo | somar/tirar na linha dos menus; página encosta no alto da área |
| Grupo Contornar aberto | lista ao lado do ícone com Laço (L) e Ponto a ponto (P) |

### Ressalvas

1. Cortar em 1280 x 657 não cabe (conhecida; pergunta de layout à parte).
2. Frase repetida no Filtro.
3. Ícones da fila menores e sem a letra do atalho embaixo; a letra só no balão do mouse.
4. Setas de página na barra de baixo pequenas e apagadas; as setas grandes dos lados da página sumiram.
5. Não testado: mouse de verdade (segurar ícone, roda), PC do Samuel em 125%, 1000 x 600, temas escuro e claro na tela de conferir.

## O que mudei para conseguir rodar

No ramo `claude/list-server-files-gkos8v` (commit 060b615, com push): input `antes_depois` e job novo no workflow, input `so_janela`, script `.github/scripts/antes_depois_endireitar.py`, e mais 4 telas em `.github/scripts/fotografar_janela.py`. Nenhum outro ramo foi alterado; as imagens foram gravadas pelo workflow em `prints-testes`.
