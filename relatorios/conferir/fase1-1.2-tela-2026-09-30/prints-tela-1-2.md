# Item 1.2: a tela "Gravuras e fotos" nos tamanhos de janela (30/09/2026)

Prints da **janela real** do programa (plataforma do Windows, não a de teste), aberta fora da tela: o Samuel não viu nada. Implementador, depois do parecer do verificador (r01, r02, r04, r06, r15). Teste de olho: quem decide é o Samuel.

**Onde olhar:** a pasta `prints\`. O nome de cada arquivo diz a escala do Windows e o tamanho da tela. Os arquivos `-rolada` são a mesma tela rolada até o fim. Nesses prints estão marcadas "Este livro tem fotos" e "Mais opções", o caso mais alto.

| Arquivo | O que é |
|---|---|
| `antes-125-1440x880` | Antes do conserto: o grupo espremido (o r01 do verificador) |
| `100-1366x768`, `100-1440x880`, `100-1600x1000`, `100-1920x1080` | Escala de 100% |
| `125-1440x880`, `125-1600x1000` | Escala de 125% (a deste PC; o r01 e o r02 foram tirados assim) |
| `125-1920x1080-notebook`, `150-1920x1080-notebook` | O notebook do Kaique: 15,6", 1920 × 1080, escala 125% ou 150% |
| `125-1920x1080-como-abre` | Como a tela abre: "Mais opções" fechado |
| `marcar-125-1440x880`, `marcar-150-1920x1080` | Aba Marcar: "Esta página tem foto" com quadrado; as linhas "Marcação:" e "Foto:" |

**Área útil das telas** (em pontos do Qt):

- Notebook do Kaique a 125%: uns 1536 × 795.
- Notebook do Kaique a 150%: uns 1280 × 657. A janela do programa não fica mais baixa que 680 pontos, que é o mínimo da janela principal (`ui/janela_principal.py`), então não cabe inteira: a parte de baixo passa uns 23 pontos da tela. Isso é da janela principal, não deste grupo.

**Numa janela baixa aparece a barra de rolagem no cartão das opções.** Nenhuma linha é espremida e nenhuma frase é cortada. O resumo e os botões "voltar" e "Conferir" ficam sempre à vista.
