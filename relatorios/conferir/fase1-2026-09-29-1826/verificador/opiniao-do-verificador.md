# Opinião do verificador: "Tirar o fundo" como filtro (item 1.1, commit dfe3b89), rodada 18:26 de 29/09/2026

> **Aviso (decisão do Samuel, 28/09): moldura dourada e iluminura são defeito conhecido** até a Fase 1 ficar pronta (itens 1.2, 1.4 e 1.5). Nenhuma página desta conferência tem moldura dourada nem iluminura; o aviso vale para o item inteiro.

## Veredito

**PRONTO PARA CONFERIR, com ressalvas.** A imagem está certa e a forma de uso nova funciona como o Samuel pediu: a página abre em "Original"; "Tirar o fundo" aparece como quinto filtro só em livro com camadas; o aviso "Este livro tem fundo separado. Quer tirar o fundo?" aparece na primeira abertura; "Sim" põe o livro inteiro no filtro e "Não", Esc e o X deixam tudo em Original. Os dois defeitos da rodada 16:03 não voltaram. Achei um defeito pequeno novo (o quadro "Para revisar" demora a contar o alerta na primeira vez que a página aparece) e, de passagem, um defeito **antigo e grave** que não vem deste item: abrir o mesmo livro por um caminho escrito de outro jeito apaga o trabalho salvo (ver "Bugs").

Quem decide é o Samuel. Isto não é aprovação.

## O que foi feito (máquina ou olho)

| O quê | Tipo | Resultado |
|---|---|---|
| Testes automáticos (`pytest tests -q`) | máquina | **897 passaram**, nenhum falhou (o instável `test_marcacao_em_todas` passou) |
| As 16 páginas da rodada 18:26 contra a 16:03 | máquina | **15 idênticas ponto a ponto**; só o Palatino 5 muda |
| Rodei eu mesmo as 16 páginas pelo caminho do programa, no filtro "Tirar o fundo" | máquina | **as 16 saem idênticas** às da rodada 18:26; as mesmas 4 saem "conferir" (Palatino 9, 57, 66, Opus Majus 3) |
| Palatino 5 ("intacta") no filtro sai igual ao Original? | máquina | **Sim, idêntica ponto a ponto** ao mesmo caminho no filtro Original |
| Todas as imagens da rodada (16 páginas: original, rodada anterior, resultado, ScanTailor; página inteira e detalhe) | olho | Abertas todas, página por página, e também os 16 resultados em tamanho de página |
| Janela real do programa: 59 prints, todos olhados | olho | Ver "A janela, passo a passo" |
| Velocidade | — | **Não medida**, por ordem da gerente (o teste oficial já rodou hoje com a máquina parada) |

## O que vi em cada página (rodada 18:26 contra 16:03)

| Página | O que vi |
|---|---|
| Palatino 5 | **Mudou, como pedido:** antes saía no Mágico pro; agora sai como veio (papel amarelo, retrato inteiro), igual ao Original ponto a ponto. É a página que o "tirar o fundo" deixa intacta. Pela regra da Fase 1 (papel branco) ainda não está boa: fica para o 1.5. O corte encosta nas letras do título ("L" e "A" da primeira linha), o mesmo corte de antes do 1.1. |
| Palatino 7 | Idêntica. Papel branco, texto inteiro; ficam os pontinhos do verso perto do "Blosius". |
| Palatino 9 | Idêntica. Molduras cheias, Q inteiro. Sai "conferir". |
| Palatino 10 | Idêntica. Continua a faixa cinza ao lado da moldura (bug já conhecido). |
| Palatino 57 | Idêntica. Moldura dupla cheia. Sai "conferir". |
| Palatino 66 | Idêntica. Título cheio, mais claro que o original; manchas laranja no título ficam. Sai "conferir". |
| Palatino 67 | Idêntica. Manchas laranja ("8", "a8") continuam (Fase 6). |
| Opus Majus 3 | Idêntica. Carimbo sumido, título vermelho. Sai "conferir" (o carimbo). |
| Opus Majus 11 | Idêntica. Texto inteiro. |
| Opus Majus 20 | Idêntica. Foto no tom do original, legenda inteira. |
| Opus Majus 165 | Idêntica. Figuras 7 e 8 inteiras. |
| Opus Majus 256 | Idêntica. Tabela inteira. |
| Rhetorica 18 | Idêntica. Texto e notas da margem inteiros. |
| Rhetorica 73 | Idêntica. O corte de cima continua no limite da régua do título (já era assim). |
| Siebmacher 7 | Idêntica. Continua dividida em duas (problema conhecido do item 2.1, não do 1.1); retalhos pretos do scanner na borda. |
| Siebmacher 9 | Idêntica. Igual ao 7. |

## A janela, passo a passo (olho, janela real)

Instância nova (`pythonw main.py`), pasta de dados própria (LOCALAPPDATA trocado para a pasta de rascunho), fora da tela, clique por mensagem nativa, prints com `PrintWindow`, fechada com `WM_CLOSE`. Livros com camadas: cópias das páginas do gabarito (Palatino 9, 5, 7 e Opus Majus 3; Palatino 10, Opus Majus 20 e Palatino 57; mais dois pequenos para o Esc e o X). Sem camadas: Boécio 3, 7 e 8. O "Abrir" foi feito pela caixa de verdade do Windows, tirada da tela.

| Passo | O que vi | Print |
|---|---|---|
| Primeira abertura de livro com camadas | A caixa "Fundo separado": "Este livro tem fundo separado. Quer tirar o fundo?", explicação, botões "Sim, tirar o fundo" e "Não, deixar como está". Certo. | t01 |
| "Sim" | O filtro do livro vira "Tirar o fundo"; resumo: "... e tirar o fundo de todas as páginas, que este PDF já traz separado do que está impresso (onde não der, a página fica como veio)". Depois de "Conferir", as 4 páginas estão no filtro. Certo. | t02 |
| Aba Filtro, página 1 (Palatino 9) | Cinco cartões, "A mesma página nos cinco filtros"; o quinto mostra o resultado de verdade (papel branco). Faixa laranja "Tirei o fundo desta página, e pode ter sumido escrita fraca ou traço fino junto: confira." e "está bom assim". **Mas o quadro "Para revisar" diz "nada pendente" por pelo menos 5 segundos**; só conta ao virar a página. Defeito pequeno (ver Bugs). | t03 |
| Página 2 (Palatino 5, intacta) | O quinto cartão mostra a página como veio (amarela), igual ao Original. Nenhum aviso de que ali o fundo não saiu; a faixa mostra "O texto quase sumiu. Tente mais escuro." com "usar mais escuro", que é o aviso do Preto e branco (já existia antes, vale para qualquer filtro). | t04 |
| "está bom assim" (página 1) | A faixa volta ao normal ("Vou tirar o fundo desta página. Onde não der, ela sai como veio."), a miniatura perde o "!". Certo. | t05 |
| Tela ampliada e "comparar" | Botão "Tirar o fundo" na barra de filtros da tela ampliada; o "comparar" mostra, lado a lado, "Tirar o fundo" (de verdade) e o outro filtro. Com a página em Original, escolhendo "Tirar o fundo" no seletor do comparar, o lado direito é o resultado de verdade (Palatino 57 igual ao da rodada). A escolha no seletor não mudou a página nem pôs alerta nela. Certo. | t06, t15 |
| Sair do filtro (página 4, Opus Majus 3, para Mágico pro) | O alerta some, "Para revisar" baixa. Certo. Os botões "Aplicar em" ficam espremidos, sem texto, nesta altura de janela; acontece igual no livro sem camadas (t23), então não vem do 1.1. | t07 |
| Desfazer a troca | Pelo "Histórico" ("clicar volta até a ação"): a página volta a "Tirar o fundo" e o alerta volta. Certo. O "Refazer" e o Ctrl+Z não consegui testar (ver ressalvas). | t08 |
| Reabrir pelo "continuar" | Nenhuma pergunta; os filtros, o alerta e o "está bom assim" voltam como estavam. Certo. | t09 |
| Segundo livro com camadas, "Não" | Tudo em Original. Certo. | t12 |
| **Defeito 2 da rodada 16:03** (escolher o filtro na página "conferir") | Página 3 (Palatino 57) em Original; ao escolher "Tirar o fundo", o alerta aparece na hora, "Para revisar 1", miniatura com "!". **Consertado.** | t13 |
| Voltar a Original | O alerta some, "nada pendente". Certo. | t14 |
| "todas" | As 3 páginas vão para "Tirar o fundo". Certo. | t16 |
| **Defeito 1 da rodada 16:03** (reabrir o mesmo livro pelo "Abrir") | Pela caixa "Abrir": nenhuma pergunta; depois de "Conferir", as 3 páginas continuam em "Tirar o fundo" e o alerta da página 3 continua. **Consertado.** Mas a tela "O que fazer", antes do "Conferir", mostra o filtro do livro em "Original" e o resumo sem falar do fundo, embora o livro esteja salvo com o fundo tirado (t10): é a família do bug já registrado "as caixinhas perdem o que se muda na volta". | t17, t10 |
| Alerta que chega depois (página nunca desenhada) | Escolhi "Tirar o fundo" antes de o cartão chegar (Opus Majus 3, sessão nova): primeiro a faixa diz "Vou tirar o fundo desta página..."; cerca de 1 segundo depois vem a faixa laranja, "Para revisar 1" e o "!". Certo. | t18, t19 |
| Projeto antigo (com os campos da rodada anterior, sem `tem_camadas`, tudo em Preto e branco) | Abre normalmente, nenhuma pergunta, as páginas continuam em Preto e branco, nenhum fundo tirado, nenhum alerta. O quinto cartão aparece (o PDF tem camadas). Certo. | t20 |
| Livro sem camadas | Nenhuma pergunta; "O que fazer" sem "Tirar o fundo"; "nos quatro filtros" com quatro cartões; tela ampliada só com os quatro botões. Trocar, na mesma janela, de um livro com camadas para um sem camadas: o filtro some. Certo. | t21, t22, t25 |
| Esc e X na pergunta | Os dois deixam o livro em Original. Certo. | t24 |
| Teclas e menu | Pelo código, as teclas 1 a 4 continuam os quatro filtros e "Tirar o fundo" não tem tecla (o painel não mostra "tecla" para ele); "só neste pedaço" não oferece "Tirar o fundo" (visto nas telas). Não consegui apertar teclas na tela ampliada por mensagem (o foco estava no seletor). | — |

Textos: todos com acento, sem jargão, sem emoji. Única exceção, antiga: o Histórico diz "Conferir a pagina 1", sem acento (já existia antes do 1.1).

## As ressalvas do implementador, na minha opinião

- **Aviso só na primeira abertura (projeto novo).** Concordo em não perguntar a cada reabertura: seria chato e a resposta já fica nos filtros. **Mas há um efeito que o Samuel deve saber:** os livros que ele já tem salvos com camadas (Palatino, Rhetorica, Siebmacher) nunca vão mostrar a pergunta, porque o projeto já existe. Sugestão: perguntar uma vez por livro, e não só em projeto novo (por exemplo, também quando o projeto salvo ainda não tem o campo `tem_camadas`, que é o caso dos três).
- **Sem menu nem tecla para "Tirar o fundo".** Aceitável agora: o filtro está nos cartões, na tela ampliada e em "O que fazer". Fica uma pequena desigualdade (o menu Filtro e as teclas 1 a 4 não o alcançam). Se um dia entrar, a tecla 5 é a natural. Pode esperar o layout (Fase 4).
- **Alerta que chega de 1 a 3 segundos depois.** Aceitável na página que está na tela: medi cerca de 1 segundo, e nesse meio tempo a faixa diz "Vou tirar o fundo desta página. Onde não der, ela sai como veio.", que não engana. Duas ressalvas: (1) o quadro "Para revisar" não acompanha quando o alerta chega assim na primeira vez que a página aparece (t03); (2) pelo código, o alerta só existe depois que a página é desenhada (visitada, ou pré-carregada). Num livro grande posto inteiro no filtro, o "Para revisar" não vai listar de antemão as páginas duvidosas: elas aparecem conforme a pessoa passa por elas. Não testei com livro grande.

## Outras ressalvas

1. **Velocidade não medida** (ordem da gerente).
2. **Refazer e Ctrl+Z não testados na janela real.** O menu Editar abre fora da janela (na tela do Samuel) e as teclas com Ctrl não passam por mensagem. O desfazer foi testado pelo Histórico, que é o mesmo mecanismo; a volta do alerta ao desfazer funcionou.
3. **Roda do mouse não testada** (não funciona sem foco). Não era preciso.
4. Alguns prints saíram "velhos" (o Windows devolveu a imagem anterior da janela enquanto ela trabalhava); esses passos foram conferidos pelo estado do projeto e por outro print, e os prints velhos não entraram no relatório.
5. Na primeira tentativa do "Abrir", a caixa do Windows apareceu por alguns segundos no canto da tela antes de eu tirá-la de lá.
6. Não testei páginas divididas ao meio no filtro novo (os livros de teste são de página única; o Siebmacher dividido saiu certo na rodada).

## Bugs para a Lista de bugs

- **29/09, pequeno, item 1.1:** quando o alerta "Conferir o fundo tirado" chega pela prévia (primeira vez que a página aparece), a faixa e a miniatura mostram o alerta, mas o quadro "Para revisar" continua "nada pendente" até virar a página. `ui/tela_conferir.py` (`_alertas_da_previa` não chama `_atualizar_paineis`). Print: `t03-cinco-cartoes-alerta-mas-para-revisar-vazio.jpg`.
- **29/09, grave, antigo (não é do 1.1): abrir o mesmo livro com o caminho escrito de outro jeito apaga o trabalho salvo.** O projeto guarda o caminho do PDF como veio; `projetos.combina_com` compara o texto do caminho. Abrindo pela associação de arquivo (caminho com `\`) e depois pelo "Abrir" ou arrastando (caminho com `/`), o trabalho não volta e aparece "Você mudou as opções desde a última vez, e o livro ficou com outro número de páginas. Comecei a conferência de novo", sem a pessoa ter mudado nada; o Histórico antigo continua lá. Os projetos salvos do Samuel estão misturados (Palatino com `\`, Rhetorica com `/`): o Palatino, reaberto pelo "Abrir", perderia o trabalho. `projetos.py` (`combina_com`). Print: `t11-abrir-perdeu-o-trabalho.jpg`.
- **29/09, antigo, mesma família do bug "as caixinhas perdem o que se muda na volta":** reabrindo um livro salvo pelo "Abrir", a tela "O que fazer" mostra o filtro do livro em "Original" e o resumo sem o fundo, embora o livro esteja salvo em "Tirar o fundo" (depois do "Conferir" o salvo volta certo). `ui/janela_principal.py` (`abrir_livro`). Print: `t10-abrir-mostra-original-no-o-que-fazer.jpg`.
- **29/09, pequeno, antigo:** o aviso do Preto e branco ("O texto quase sumiu. Tente mais escuro." / "usar mais escuro") aparece em página que está em outro filtro (visto no Palatino 5 em "Tirar o fundo"). `ui/tela_conferir.py` (`_conferir_qualidade_do_preto_e_branco`). Print: `t04-palatino5-intacta-sai-como-veio.jpg`.
- **29/09, pequeno, antigo:** com Mágico pro, numa janela de 1440 x 880, os botões "Aplicar em" ficam espremidos e sem texto. Acontece também em livro sem camadas. `ui/tela_conferir.py`. Prints: `t07-...jpg`, `t23-sem-camadas-botoes-espremidos-tambem.jpg`.
- **29/09, pequeno, antigo:** "Conferir a pagina 1" sem acento no Histórico. `ui/tela_conferir.py` (texto com o nome interno "pagina").
- **29/09, arrumação (fora do projeto, não apaguei nada):** a pasta de dados real do Samuel (`%LOCALAPPDATA%\EditorImpressao\projetos`) tem projetos criados por testes: "camadas" e "comum" (29/09 15:36, de uma rodada de pytest), "teste_botoes_camadas" e "teste_botoes_camadas3" (29/09, 16:20 e 16:36) e 23 "fixture_gerado" (desde 08/09). Aparecem na tela inicial dele. A minha rodada de pytest de hoje não criou nenhum. Apagar só com a palavra do Samuel (CLAUDE.md, seção 10, item 9).

## Arquivos

- Esta opinião: `relatorios\conferir\fase1-2026-09-29-1826\verificador\opiniao-do-verificador.html`
- A página de antes/depois: `relatorios\conferir\fase1-2026-09-29-1826\conferencia-fase1.html`
- Os prints da janela (t01 a t25) estão nesta mesma pasta.

![](t01-aviso-primeira-abertura.jpg)

![](t03-cinco-cartoes-alerta-mas-para-revisar-vazio.jpg)

![](t13-defeito2-alerta-aparece-ao-escolher.jpg)

![](t17-defeito1-abrir-de-novo-mantem-filtros.jpg)

![](t15-comparar-mostra-tirar-fundo-de-verdade.jpg)

![](t04-palatino5-intacta-sai-como-veio.jpg)

![](t19-alerta-chegou-1s-depois.jpg)

![](t20-projeto-antigo-em-preto-e-branco.jpg)

![](t21-sem-camadas-quatro-cartoes.jpg)

![](t11-abrir-perdeu-o-trabalho.jpg)

![](t10-abrir-mostra-original-no-o-que-fazer.jpg)
