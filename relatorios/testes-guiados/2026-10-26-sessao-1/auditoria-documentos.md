# Auditoria dos documentos do projeto — o que o plano de 26/10 deixou de fora

Pedido do Samuel (26/10/2026): "Por favor revise os documentos do projeto para ver se tem mais alguma coisa faltando,
pois se não os testes que fizemos estarão esquecendo coisas já determinadas e achadas."
Feita por um agente revisor, só leitura (plano, memória, PEDIDOS, histórico PARTES -20 a -12, conferências, Central,
rascunho do layout, testes guiados, ramos do mapa, dos 14 livros e do teste do Kaique). Plano comparado:
`C:\Users\fotog\.claude\plans\ent-o-vamos-fazer-um-cozy-brooks.md`. Fontes: PD = `docs/plano/PLANO-DEFINITIVO.md`.

**Já cobertos (conferido um por um):** os 50 itens da lista única, os achados 0-x e 1-1 a 1-16, os 22 pontos confusos
do mapa e os problemas dos 14 livros. Desde 23/10 o `fase-1` só recebeu documentos: todo defeito aberto naquela data
continua aberto.

## 1. Decidido pelo Samuel, não construído e fora do plano

- **A rodada de melhorias de depois da junção** (22-23/10, "A — Esperar": entra junto com os consertos; PD:660-674) —
  a falha maior:
  - "Antes de processar" mais clara e menor, aprovada (`lm22`); commit `138e425` só no ramo
    `layout-antes-de-processar-2026-10-22`; defeito do "Mostrar" que corta o motivo.
  - Aviso quando "Pintar por cima" cobre letras ("Pintar assim mesmo" / "Voltar"): "1- sim" (`fr-218-aviso`).
  - "Montar para imprimir" bagunçada e "são 1 cadernos": "cheio de letras uma em cima da outra"
    (`relatorios/prints-samuel/2026-10-22-montar-para-imprimir-baguncado.png`; `ui/dialogo_impressao.py:1` "PROVISÓRIO").
  - Tela cheia com letra mais grossa que o PDF (`lu-tc-igual`): "precisamos que o pdf saia que nem está na tela."
  - Tirar a moldura escura antes de desentortar (`d212-1`): "fica anotado para depois da junção".
  - Aviso do Righetti 96 (`d212-2`): "Eu quero o aviso, mas isso fica para depois."
- **Tela troca sozinha pela imagem do PDF, com duas bolinhas de carregamento** (22/10, "é só colocar uma bolinha de
  carregamento…"; `memoria/itens/para-revisar.md`): conserto decidido do defeito grave do T do Antiphonal 46 (PD:388).
- **Retângulo do corte quando o ângulo muda, nos três lugares** (09/10, "quero a b e c juntas."): conta existe
  (`core/pipeline.py:1214`), tela não (`ui/tela_configuracoes.py:14-15`); o lugar "do livro" ficava na tela "O que fazer".
- **Área de trabalho 1 / lado direito escolhido no menu Ver e nas Configurações** (05, 06 e 20/10: "Mas eu também quero
  ter a opção da area de trabalho 1."; "C — Nos dois lugares"): não construído.
- **"C — tudo livre, como o Photoshop"** (05/10, "confirmo"): depois.
- **No livro aberto: "Para revisar", "Receita usada", "Rodar o automático…"** (R6, 06/10, "Sim, fica assim"): pela metade.
- **Grade "Todas as páginas" com várias escolhidas** (marcar/desmarcar; girar, apagar, extrair, inserir, como o UPDF;
  24/09 e 05/10): não construída — é onde o "rodar em escolhidas" escolhe.
- **Janela grande do Automático** com página ao lado, folhear, zoom, "ajustar ›" em cada etapa e grupos (05 e 12/10).
- **Abrir em tela cheia só as páginas que precisam de atenção**, a partir do Para revisar (05/10): falta o botão.
- **"Ver lado a lado" no menu Ver** (904 A, 20/10).
- **Barra de baixo com "antes / depois", zoom "– 78% +" e "ajustar à tela"** (13/10).
- **Na área de trabalho: roda do mouse troca de página, Page Up/Down pulam 10, Home/End** (29/07, 08/08).
- **Botão provisório "Os quatro filtros" ainda na trilha** (R9 403 B).
- **"Recuperar o trabalho anterior" no menu do cartão** (29/09).
- **Delete deixa a página em branco, e os dois botões em qualquer página** (07 e 09/10: "eu quero ter em outras
  paginas") — hoje é ao contrário: Delete = "Apagar esta página".
- **Folga do corte para o livro todo, com aviso de onde ficou ruim** (05/10) — a conferir.
- **Os "8 lugares que podem comer a página"** (22/10, "o resto para o começo da próxima fase"; PD:400-408): só o
  desentortar foi feito.
- **Regras de teste:** nada de lombada ou capa (21/10); bug de comer página se prova primeiro em páginas de verdade;
  teste numa folha na EPSON (22/10).

## 2. Problemas achados, ainda abertos e fora do plano

**Do teste do Kaique:** rodinha muda números no "Montar para imprimir" (grave; `ui/dialogo_impressao.py:286-297`);
"Mover conteúdo" não sai no PDF (grave, a conferir); aviso falso "parece em branco" na p. 7 com "Tirar do livro" ao lado
(grave); falta "centralizar"; aumentar não aumenta o texto; janelas de arquivo em inglês e caminho digitado sem efeito
nem aviso; botões quase iguais; nenhum menu tem Endireitar/Cortar/Dividir; "356 páginas que você não conferiu" depois
de "nada pendente"; "Menor que o corte" com números iguais; "1 foram apagadas"; mudar caixinhas não fica no `acoes.jsonl`.

**Da Lista de bugs e de `memoria/bugs.md`, fora da lista única:** T que some no PDF (grave, PD:388); "Reduzir cores"
apaga letra; foto de celular: sombra vira mancha preta; Righetti 96 com cartão quase em branco e rodapé atrasado;
Egenloff 3 (etiqueta, carimbo partido, corte antigo); ressalvas do G6 (cunhas brancas, moldura colada); Escola 197
(corte come números da margem), Camões 66, Antiphon 260; aviso "as contas discordam" em página reta; quatro botões
piscam ao abrir; janela sumiu em "Deixar em branco" (a conferir); "Usar em todas" da Bordas apaga exceções; Ver >
"Painel: …" sem efeito; "Desfazer" ligado sem nada; `projeto.json` ilegível recomeça sem aviso; cartão "PDF gerado"
desatualizado; "Só neste pedaço" ignorado sem "Limpar a folha"; "letra e traço" à mão não protege a tinta; aviso de
`core/analise.py:80` fala da "aba Marcar"; linha da conta some no Endireitar; textos sem acento e nomes antigos no
Histórico; observações do livro escondidas (PD:380); lentidão (Marial ~58 s, medir 2-3× mais lento, "access violation"
ao fechar). Fases 1 (1.4-1.6, ~20 defeitos "movidos para 1.5"), 3, 5, 6, 7 e itens 0.2/0.6 `[~]`; instalador nunca
testado no notebook do Kaique (6.8). **~50 consertos "esperando o olho do Samuel"** (`memoria/bugs.md` §2).

## 3. Ideias aceitas para depois (Lista de espera, PD:420-484) que o plano deve citar

"Ferramenta primeiro, forma depois" (23/10); pergunta do fundo e "voltar ao original" (30/09, mora na tela que sai);
Laboratório no Automático (21/10); painel Marcar "muito bagunçado" (`tc23`); "A tela decide, o PDF obedece" (22/10);
"Transformar página em folha branca" (30/09). Só anotadas: hora no Histórico; "Marcar como" iluminura e moldura; tirar
ilustrações; alerta de linha apagada; foto em Original dentro do Preto e branco; filtro só onde o detector achou; usar as
áreas achadas; inverter letra branca; grade e layout como o UPDF; velocidade; limpar worktrees velhas.

## 4. Perguntas dele sem resposta

"Aviso que o Kaique pediu" (sem descrição desde 24/09, PD:426); o programa já substitui o CamScanner? (6.7); metade
apagada de folha que deixou de ser dividida (07/10, "vamos discutir mais isso"); escala da tela do notebook do Kaique;
"N com dúvida" do Egenloff e testes encadeados (21/10); `layout3-para-revisar` e `layout3-janela-pequena-e-temas`
(13/10, a conferir); Cursus 3, Camões 104, Pesel 21 (PD:634, a conferir); pendências do layout (espaços Limpo/Completo,
tela pequena, idioma do OCR, observação do livro, teclas em inglês, laranja do "PDF fora do lugar", "Como ter certeza da
sequência sem olhar folha por folha?" do Kaique, "Sem limpeza" de fábrica, "voltar" × "restaurar página", faixa de 5
botões em 1280, painel do Endireitar comprido); da lista única 1.5, 1.10, 1.8, 3.2; página vazia no claude.ai.

## 5. Duvidosos e contradições

- **Agentes ao mesmo tempo = 3** (Central `config/agentes`: "Samuel marcou 1 sem querer"); a conferência de 21/10 ainda
  diz 1 e o Registro não tem a correção. O "um agente por vez" do plano veio desse engano.
- **P3 talvez já respondida:** G10 (05/10) "(b) Avisar e não reduzir… opção para passar isso para todas as folhas" e
  `g10-ajustar-todas` (13/10) "Cada página até encher a folha".
- **P2 bate com a ordem fixa decidida** (`g6-endireitar-antes`, 09/10; "Ordem obrigatória" do CLAUDE.md) × 2a "ordem livre".
- **"Ver lado a lado":** 201 B (botão em cima à direita) × livro aberto como o UPDF aprovado em 22/10 ("Duas lado a lado"
  na barra de baixo).
- "Folha inteira com a linha só dentro do Dividir" fica melhor na etapa 4.
- 5.1 "imprimir agora": o decidido no imp-5 ("também manda direto para a impressora") continua, só que perguntando antes.
- Passada leve ao abrir tem de respeitar "página sempre abre em Original, sem mexer" (29/09, PD:69).
- Etapa 3: as opções da tela "O que fazer" não podem se perder (G2, forma e sensibilidade do detector, g7/g8, conta do
  endireitar, lugar (a) do G6, pergunta do fundo). Etapa 5: as guias do `g8-guias` vão junto.
- Lista única: 5.4 é a causa do contador da etapa 7; 4.4 e 4.8 precisam da conferência de PDF; 2.2, 2.7 e 5.11 vão para
  a janela da etapa 3. 802 A: conferir depois da etapa 2.
- Ramos não juntados: `teste-kaique-2026-10-26`, `mapa-do-programa-2026-10-23`, `testes-livros-2026-10-23`,
  `layout-antes-de-processar-2026-10-22`.
- Fichas desatualizadas (a etapa 0 não deve confiar): `memoria/ONDE-PAREI.md` (20/10); `layout.md:237`;
  `perguntas-abertas.md` §1-2 e l.83; `bugs.md` (`_escolher_forca` já existe; instalador já consertado).
