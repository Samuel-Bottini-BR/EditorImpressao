# Rodada 3: como o programa vai resolver, e 30 páginas de 5 livros novos

06/10/2026 · agente das decisões do "Para revisar". Nada do programa foi mudado.

## O que o Samuel pediu (rodada 2)

- "Como vamos resolver esses problemas dentro do programa": um cartão por tipo de erro.
- "Quero mais páginas para eu conferir [...] pegue mais 5 livros e me traga 30 páginas."
- Uma explicação do aviso do "Só o texto achado": quando, onde e por quê.
- Ele perguntou "que lista?". A partir daqui o texto usa sempre **"Para revisar"**, e o primeiro cartão
  explica o que é.

## As perguntas (`rodada-3-perguntas.json`, 37)

| # | id | O que é |
|---|---|---|
| 1 | rv3-para-revisar | O que é "Para revisar" (print da tela, painel pintado numa cópia) |
| 2 | rv3-conserto-desenho | Erro 1, desenho claro apagado: o conserto do ramo `misto-desenho-apagado` (em conferência; 13 das 59 melhoraram) |
| 3 | rv3-conserto-gravura | Erro 2, mancha vira gravura ou figura passa da zona: hoje se resolve à mão na aba Marcar ("tirar"/"somar"); está planejado o 2.18/P11b ("mostrar as áreas achadas e clicar para apagar ou pintar") |
| 4 | rv3-conserto-faixa | Erro 3, faixa do scanner: é do corte (2.13, decisão G7, desligado de fábrica); até lá, aviso no livro ou "Para revisar" e corte à mão na aba Bordas |
| 5 | rv3-conserto-graduale588 | Proposta para a letra colorida: zona "Tinta com a cor original, papel branco" (P11, decidida, ainda não feita), com uma **simulação** |
| 6 | rv3-conserto-so-texto | Erro 4, o que some no "Só o texto achado": o Kaique troca a página de jeito ou marca à mão |
| 7 | rv3-aviso-so-texto | O aviso: quando, onde e por quê (desenho da proposta + o exemplo do Palatino 10) |
| 8–37 | rv3-pag-... | 30 páginas: "Pela regra nova, esta página VAI / NÃO VAI para 'Para revisar'. Você concorda?" (Concordo / Não concordo / Não sei) |

Os cartões 2 a 7 têm as opções "Entendi, pode seguir", "Não entendi" e "Quero de outro jeito". Os campos
`hoje`, `regra_nova` e `veredito_agente` não aparecem na página; servem para a análise.

## Os 5 livros (de `D:\Livros para editar`, só leitura; nenhum entrou nas rodadas anteriores)

| Livro | Por quê | Páginas |
|---|---|---|
| Antiphonal 1547 | música impressa em vermelho e preto, capitulares vermelhas e gravadas, manchas de umidade | 6, 31, 46, 76, 192, 252 |
| Rariora Musei Besleriani | gravuras de animais, conchas e pedras; quadros com chaves; folha de rosto clara | 8, 99, 155, 169, 211, 365 |
| Egenloff, Modelbuch 1527 (reedição de 1880) | ornamentos de traço; fundo escuro do scanner e tarja da biblioteca em todas as páginas | 3, 7, 12, 47, 121, 131 |
| Gladstone Chaves de Melo, Novo Manual de Análise Sintática (1954) | livro moderno, só texto e quadros | 5, 18, 55, 96, 116, 136 |
| Camões, A Historia de Portugal justificada pelos Lusíadas (séc. XIX) | gravuras, letras ornamentadas, papel escuro, beirada gasta | 6, 9, 11, 27, 66, 104 |

## O resultado nas 30

- **Pela regra nova vão 9 e não vão 21.** Hoje iriam 20.
- **Vão:**
  - Antiphonal: as páginas 6, 31, 46, 76 e 252.
  - Camões: as páginas 6, 9, 11 e 104.
- **Por livro:**
  - **Antiphonal 1547:** vão 5 de 6. A letra vermelha grande some nas páginas 46 e 76 (errada). As pautas
    vermelhas saem com falhas nas páginas 6, 31 e 252 (leve). Não vai a página 192, que é manuscrita e saiu
    certa.
  - **Rariora:** não vai nenhuma. Hoje vão a 169 e a 365.
    - **A página 169 está errada e a regra não pega:** a concha da Fig. 8 perde o pontilhado. O apagado ficou
      em 2,4% da tinta, logo abaixo do limite de 2,5%.
    - **A página 8 é leve e a regra também não pega:** a página inteira virou gravura e sai bege, como no
      original.
  - **Egenloff:** não vai nenhuma. A faixa do scanner aparece nas 6 páginas e vira aviso do livro. Hoje vão
    todas.
  - **Gladstone:** não vai nenhuma, e todas estão certas. Hoje também não vai nenhuma.
  - **Camões:** vão 4.
    - As páginas 6, 9 e 11 estão erradas: a gravura da estátua e as letras ornamentadas ficam pela metade.
    - A página 104 é leve: a zona de gravura escorre pela beirada.
    - As páginas 27 e 66 saíram certas e não vão; hoje vão, por causa da sombra da beirada.
- **No meu olho:** 6 erradas, 5 leves e 19 certas.
  - A regra pega 5 das 6 erradas (escapa a Rariora 169) e 4 das 5 leves (escapa a Rariora 8).
  - Nenhuma página certa vai para "Para revisar".

## Ressalvas

- **As 30 páginas rodaram com o programa de hoje, sem o conserto do desenho apagado** (que está em outro
  ramo). Com o conserto, as letras do Antiphonal e do Camões e a concha da Rariora 169 devem sair melhores, e
  parte delas deixaria de ir para "Para revisar". Não medi isso.
- **A Rariora 169 mostra que o limite de 2,5% fica no fio.** Vale olhar de novo depois do conserto.
- **A simulação do Graduale 588 não é o programa.** Usa a conta da decoração colorida (`core.filtros`) num
  retângulo à mão, com folga em volta; o tipo de zona ainda não existe.
- **A imagem do aviso do "Só o texto achado" é um desenho da proposta**, não a tela real; o texto do aviso
  é o que ele aprovou na rodada 2.
- **Uma página de cada vez:** cada página rodou num processo próprio, pelo caminho do programa. Os dados
  ficam em `%TEMP%\revisar_decisoes_rodada1`.

## Para refazer

Rode de dentro de `scripts/`, com o Python do projeto:

1. `rodar.py <página>` (uma por vez)
2. `sinais.py`
3. `simular_cor_papel_branco.py`
4. `imagens_prontas.py`
5. `aviso_img.py`
6. `figuras.py`
7. `perguntas.py`

As páginas e os vereditos estão em `paginas_lista.py`; a regra está em `criterio.py`.
