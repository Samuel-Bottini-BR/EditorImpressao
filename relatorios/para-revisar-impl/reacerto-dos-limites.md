# Reacerto dos limites do "Para revisar" para o preparo do livro novo

Gerado por `reacertar_limites.py` (13/10/2026). 89 páginas do estudo, o programa de verdade a 300 DPI. "Iguais ao estudo" = páginas com a mesma decisão (vai / não vai) que a regra do estudo deu; "certas" = contra o gabarito (as respostas do Samuel e o veredito do estudo).

## Os limites

| Limite | Aprovado na rodada 4 | Agora | Folga (sem piorar) |
|---|---|---|---|
| junto | 0.02 | 0.02 | 0.01 a 0.04 |
| apagado | 0.025 | 0.025 | 0.025 a 0.03 |
| pedaco | 1.5 | 1.2 **(mudou)** | 0.9 a 1.4 |
| vazou | 0.1 | 0.1 | 0.09 a 0.12 |
| beirada | 0.03 | 0.03 | 0.0225 a 0.0325 |
| sem_conteudo | 0.005 | 0.005 | 0.003 a 0.009 |
| guarda | 0.62 | 0.62 | 0.62 a 0.62 |
| guarda_minima | 0.2 | 0.13 **(mudou)** | 0.1 a 0.14 |

## As contas

| Preparo | Limites | Vão | Certas | Iguais ao estudo | Faixa vira aviso do livro |
|---|---|---|---|---|---|
| preparo do livro novo (G6 + conta do ScanTailor) | aprovados na rodada 4 | 20 | 73 | 82 de 89 | antiphon, egenloff |
| preparo do livro novo (G6 + conta do ScanTailor) | de agora | 22 | 75 | 84 de 89 | antiphon, egenloff |
| preparo do dia do estudo (projeto antigo) | aprovados na rodada 4 | 21 | 78 | 89 de 89 | egenloff, matematica |
| preparo do dia do estudo (projeto antigo) | de agora | 21 | 78 | 89 de 89 | egenloff, matematica |

## Página por página

Só as páginas que vão em algum dos casos, ou que deveriam ir. "sim" = vai para a lista; **negrito** = diferente do estudo.

| Página | Gabarito | Estudo | Novo, antes | Novo, depois | Antigo, antes | Antigo, depois | Motivos (novo, depois) |
|---|---|---|---|---|---|---|---|
| antiphon_p088 | não | sim | sim | sim | sim | sim | desenho apagado |
| antiphon_p260 | sim | sim | **não** | **não** | sim | sim | - |
| antiphonal1547_p006 | sim | não | não | não | não | não | - |
| antiphonal1547_p031 | sim | não | não | não | não | não | - |
| antiphonal1547_p046 | sim | sim | **não** | sim | sim | sim | desenho apagado |
| antiphonal1547_p076 | sim | sim | sim | sim | sim | sim | desenho apagado |
| antiphonal1547_p252 | sim | sim | sim | sim | sim | sim | desenho apagado, texto falhado |
| camoes_p006 | sim | sim | sim | sim | sim | sim | desenho apagado |
| camoes_p009 | sim | não | não | não | não | não | - |
| camoes_p011 | sim | sim | sim | sim | sim | sim | texto falhado |
| camoes_p027 | sim | sim | sim | sim | sim | sim | texto falhado |
| camoes_p066 | sim | não | não | não | não | não | - |
| camoes_p104 | sim | sim | sim | sim | sim | sim | texto falhado |
| cursus_p003 | não | não | **sim** | **sim** | não | não | faixa na beirada |
| egenloff_p003 | sim | sim | **não** | sim | sim | sim | texto falhado |
| egenloff_p012 | sim | sim | sim | sim | sim | sim | página sem conteúdo |
| egenloff_p047 | sim | não | não | não | não | não | - |
| graduale_p269 | não | sim | sim | sim | sim | sim | figura além da gravura |
| ljs47_p026 | não | sim | sim | sim | sim | sim | figura além da gravura, faixa na beirada |
| ljs47_p103 | sim | sim | sim | sim | sim | sim | texto falhado, faixa na beirada |
| marial_p454 | sim | sim | sim | sim | sim | sim | figura além da gravura |
| matematica_p032 | sim | sim | sim | sim | sim | sim | figura além da gravura, faixa na beirada |
| matematica_p072 | não | sim | **não** | **não** | sim | sim | - |
| opusmajus_p020 | não | não | **sim** | **sim** | não | não | figura além da gravura |
| palatino_p066 | não | não | **sim** | **sim** | não | não | texto falhado |
| pesel_p021 | sim | sim | sim | sim | sim | sim | desenho apagado, figura além da gravura |
| rariora_p008 | sim | sim | sim | sim | sim | sim | página sem conteúdo |
| siebmacher_p007 direita | não | sim | sim | sim | sim | sim | desenho apagado |
| siebmacher_p009 direita | não | sim | sim | sim | sim | sim | desenho apagado |

## As que continuam diferentes do estudo, e por quê

- **antiphon_p260**, preparo do livro novo (G6 + conta do ScanTailor): o estudo mandava (figura além da gravura achada); agora não vai (-). Sinais: apagado 0.0122, amontoado 0.0, maior pedaço 0.0, figura além 0.0102, beirada 0.0761, guardas das linhas falhadas ou perto [0.6213]. Gabarito: vai. **Por que limite não resolve:** No preparo novo quase nada da figura fica fora da gravura achada (1,0% da tinta; no dia do estudo, 15,5%). Limite nenhum separa 1,0% das páginas boas. A página tem faixa na beirada (7,6%), mas no Antiphon a faixa está em todas as páginas medidas e é aviso do livro.
- **cursus_p003**, preparo do livro novo (G6 + conta do ScanTailor): o estudo não mandava (-); agora vai (faixa na beirada). Sinais: apagado 0.0098, amontoado 0.0072, maior pedaço 0.0, figura além 0.0, beirada 0.0739, guardas das linhas falhadas ou perto []. Gabarito: não vai. **Por que limite não resolve:** No preparo novo sobra faixa escura em 7,4% da página (no dia do estudo, 0,5%). Para ela não ir, o limite da faixa teria de subir de 3% para mais de 7,4%: aí a faixa deixaria de ser aviso do livro no Egenloff, a Egenloff 47 passaria a ir, e no preparo do projeto antigo duas páginas mudariam de decisão (medido com --procurar).
- **matematica_p072**, preparo do livro novo (G6 + conta do ScanTailor): o estudo mandava (desenho apagado, figura além da gravura achada); agora não vai (-). Sinais: apagado 0.0032, amontoado 0.0032, maior pedaço 0.0, figura além 0.0376, beirada 0.0004, guardas das linhas falhadas ou perto [0.7351, 0.7265]. Gabarito: não vai. **Por que limite não resolve:** No preparo novo o desenho quase não é apagado (0,3% da tinta; no dia do estudo, 16,6%) e a figura passa pouco da gravura (3,8%; antes 34%). O gabarito diz que ela não precisava ir: aqui o programa de hoje acerta e a regra do estudo mandava sem precisar.
- **opusmajus_p020**, preparo do livro novo (G6 + conta do ScanTailor): o estudo não mandava (-); agora vai (figura além da gravura). Sinais: apagado 0.0042, amontoado 0.0033, maior pedaço 0.0, figura além 0.155, beirada 0.0, guardas das linhas falhadas ou perto []. Gabarito: não vai. **Por que limite não resolve:** No preparo novo a figura além da gravura dá 15,5% (no dia do estudo, 8,2%). O Marial 454, que tem de ir só por este motivo, dá 15,6%: limite nenhum separa os dois.
- **palatino_p066**, preparo do livro novo (G6 + conta do ScanTailor): o estudo não mandava (-); agora vai (texto falhado). Sinais: apagado 0.0069, amontoado 0.0, maior pedaço 0.0, figura além 0.0, beirada 0.0, guardas das linhas falhadas ou perto [0.7241, 0.702, 0.4998, 0.5665, 0.6174]. Gabarito: não vai. **Por que limite não resolve:** No preparo novo três linhas guardam 50%, 57% e 62% da tinta (no dia do estudo, uma só). Para ela não ir, o limite da guarda teria de cair abaixo de 0,57, e o Camões 11 e o Camões 27 (linhas entre 0,59 e 0,61), que têm de ir, sairiam junto.

As imagens destas páginas não foram olhadas pelo implementador: os motivos acima saem dos números das duas rodadas. Vale o verificador olhar o Cursus 3, o Opus Majus 20 e o Palatino 66 no preparo novo (as três passaram a ir) e o Antiphon 260 (deixou de ir).

## Como os limites foram escolhidos

- `pedaco` (o maior pedaço apagado, em alturas de linha ao quadrado): entre 0,8 e 2,0 só existem duas páginas nas 89, nos dois preparos: a letra T do Antiphonal 46 (1,43 no preparo novo; 1,57 no do estudo) e a letra L do Antiphonal 76 (2,11 e 2,04). Com 1,5 a letra T ficava de fora no preparo novo; 1,2 pega as duas nos dois preparos, com folga dos dois lados.
- `guarda_minima` (abaixo dela a linha é dada como "sumiu inteira"): entre 0,10 e 0,20 só há linhas do Egenloff 3 (0,121 e 0,148 no preparo novo; 0,143 no do estudo) e uma do Boécio 22 (0,15 e 0,199), que sozinha não manda a página. Com 0,20 o Egenloff 3 ficava com uma linha falhada só no preparo novo; com 0,13 volta a ter duas. **É o reacerto mais apertado: apoia-se numa linha de uma página.**
- Um conjunto só de limites para os dois preparos (não foi preciso separar por ordem do preparo): no preparo do projeto antigo nada muda de decisão.
- Não foi tentado mudar a forma da regra. Subir o limite da faixa de 3% para 7,5% daria 77 certas no preparo novo, mas mudaria as decisões do estudo no preparo antigo e deixaria de avisar faixas de 3% a 7%: não fiz.
