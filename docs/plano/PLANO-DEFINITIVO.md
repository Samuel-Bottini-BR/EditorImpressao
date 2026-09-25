# Editor de Impressão — PLANO DEFINITIVO

Discutido ponto por ponto com o Samuel e aprovado por ele em 24/09/2026. **Este é o plano. Ele não muda sozinho.**

---

## 1. Regras do plano

1. **Uma fase de cada vez, na ordem.** Uma fase só começa quando todos os itens da anterior estão aprovados `[x]` ou descartados `[-]` pelo Samuel.
2. **Ideia nova não entra na fase atual.** Vai para a **Lista de espera** (seção 6), com data. O Samuel decide em que fase ela entra.
3. **Só o Samuel muda este plano.** Toda mudança vai para o **Registro de mudanças** (seção 7), com data e motivo. O Claude Code pode sugerir uma mudança, nunca aplicar.
4. **Todo item termina igual:**
   - o verificador gera uma página de antes/depois só das páginas-gabarito daquele item;
   - o Samuel confere em até 10 minutos, abrindo pelo atalho "(desenvolvimento)";
   - ele marca `[x]` (aprovado), `[~]` (melhorar) ou `[-]` (descartado);
   - se aprovado, o trabalho é salvo no git (commit) **na hora**.
5. **Bugs que aparecem no meio de outra tarefa:**
   - Se o bug **impede** a tarefa atual, é consertado na hora, como parte dela.
   - Se **não impede**, vai para a **Lista de bugs** (seção 5), com print e data.
   - A Lista de bugs é resolvida **no começo de cada fase**, antes do primeiro item novo.
6. **Nenhum item pode deixar o programa mais lento** (medido pelo teste de velocidade da Fase 0).
7. **Toda decisão tomada em qualquer conversa vira documento no projeto.** As conversas não enxergam umas às outras, só os documentos.
8. **Toda função automática tem botão de ligar e desligar.**
9. As regras técnicas do `CLAUDE.md` continuam valendo: PySide6, uma página por vez na memória, nenhum modelo que desenhe pixel, interface em português sem jargão.

---

## 2. O resultado-alvo

**O Mágico Pro do CamScanner, que o Kaique usa hoje.** Nas palavras do Kaique:

> "removeu o amarelado do fundo, manteve apenas as letras e imagens preservando suas cores originais, e alinhou a página que estava inclinada"

Critério do Samuel: *"Eu quero que o papel saia branco, e o desenho também saia perfeito."*

As fotos do CamScanner enviadas pelo Samuel em 24/09 (calendário Novembre/Decembre e "Na escola de Jesus" p. 37) são gabarito de comparação.

---

## 3. Como o trabalho é feito (agentes)

- **Uma conversa "gerente" no Claude Code.** Ela conversa com o Samuel, distribui o trabalho e junta tudo.
- **Agentes** (arquivos de regra em `.claude/agents/`):
  - **implementador**: escreve o código do processamento;
  - **verificador**: roda os testes, gera a página de antes/depois e nunca marca aprovado;
  - **pesquisador**: estuda o ScanTailor, OCRs etc.;
  - **agente de layout**: só mexe nos arquivos de tela (`ui/`).
- **Sem choque entre frentes:** cada frente trabalha na sua própria cópia do projeto (git worktree) e no seu ramo (branch). O processamento mexe em `core/` e o layout em `ui/`. Só o gerente junta as frentes.
- **Layout em paralelo:** a Fase 1 roda no Claude Code enquanto o Samuel discute o plano do layout numa conversa separada no projeto do claude.ai. Quando o plano do layout estiver pronto, ele vira documento e o Samuel entrega na conversa do Claude Code, que aciona o agente de layout. A partir daí, processamento e layout andam juntos, cada um na sua cópia.

---

## 4. As fases

### FASE 0 — Arrumar a casa

- [ ] 0.1 Fazer uma cópia de segurança, num ramo separado (`trabalho-17-a-23-09`), do trabalho sem commit desde 17/09, e depois salvar esse trabalho no programa principal (ver Registro de mudanças, 25/09).
- [ ] 0.2 Apagar o atalho antigo `C:\Users\Public\Desktop\Editor de Impressao.lnk` (o Samuel apaga à mão, precisa de admin).
- [ ] 0.3 Montar a pasta `gabarito/` com as páginas fixas: as do "Vamos recapitular", as fotos do CamScanner e as do Opus Majus.
- [ ] 0.4 Criar o script que gera a página de antes/depois de qualquer item.
- [ ] 0.5 Criar o **teste de velocidade**: abrir livro de 300 páginas, trocar de página, processar 10 páginas.
- [ ] 0.6 Rodar o teste de velocidade **uma vez** no notebook do Kaique (Samsung Galaxy Book2: i5-1235U, 32 GB, SSD NVMe, placa de vídeo integrada Iris Xe) e no PC do Samuel. A diferença entre os dois vira a régua. Daí em diante, o Samuel testa só no PC dele.
- [ ] 0.7 Criar os arquivos dos agentes (`.claude/agents/`) e atualizar o `CLAUDE.md` com as regras deste plano.

### FASE 1 — Separar o escrito do fundo (automático)

- [ ] 1.1 **Tirar o fundo de PDF que já vem com camadas** (Internet Archive; o Opus Majus e o Palatino são assim). O programa detecta e tira sozinho. Páginas em que tudo está na camada de baixo ficam intactas.
- [ ] 1.2 **Trazer o seletor de gravura do ScanTailor Advanced, com o código original** compilado e ligado ao programa (caminho A, decisão de 24/09). Referência: `TESTE-SCANTAILOR-MISTO.md`.
- [ ] 1.3 **Comparar OCRs já treinados**, só para achar onde está o texto: Tesseract (modelos normais e os históricos da UB Mannheim), docTR, PaddleOCR e Kraken. Ficam os 2 melhores.
- [ ] 1.4 **Máscara de tinta como o Internet Archive:** achar a tinta só dentro das linhas de texto, guardando a **cor original** (resolve o texto colorido que o ScanTailor transforma em preto).
- [ ] 1.5 **Juntar os dois detectores** (ScanTailor + OCR) e montar a página: papel branco, letra com a cor original, gravura intacta, página endireitada.
- [ ] 1.6 **PDF de saída em duas camadas** (letra em cima, fundo embaixo), como opção.
- Gabarito: Palatino 5, 7, 9, 10; Escola de Jesus 7; Horas 11, 13, 47; Opus Majus; fotos do CamScanner.

### FASE 2 — As outras ferramentas do ScanTailor Advanced

Com o código original, como na 1.2.

| # | Ferramenta |
|---|---|
| 2.1 | Dividir a folha (sabe quando é uma página só; hoje o nosso tenta dividir folha que é claramente uma) |
| 2.2 | Endireitar (o nosso hoje funciona mal) |
| 2.3 | Orientação / girar (o nosso hoje funciona mal, na tela e no funcionamento) |
| 2.4 | Margens iguais em todas as páginas + alinhamento |
| 2.5 | Caixa da página e guias |
| 2.6 | Tamanho final da página em cm/mm |
| 2.7 | Limpar pontinhos, com controle de força |
| 2.8 | Preto e branco Sauvola e Wolf (conferir o que já existe) |
| 2.9 | Texto claro em fundo escuro |
| 2.10 | Separar a saída em duas camadas |
| 2.11 | Segmentação de cor / reduzir cores |
| 2.12 | Desentortar página curva perto da lombada |
| 2.13 | Detectar a página dentro da borda preta do scanner |
| 2.14 | Preencher o que sobra fora da página com branco |
| 2.15 | Destacar páginas diferentes das outras |
| 2.16 | Usar todos os núcleos do processador |
| 2.17 | Normalizar iluminação e suavizar |
| 2.18 | Edição manual das zonas de gravura (retângulo, polígono, laço, copiar, colar) |
| 2.19 | Unidades cm/mm, perfis de configuração, tema claro/escuro |

**Já no programa, a aperfeiçoar nesta fase** (feito de 17 a 23/09; ver Registro de mudanças, 25/09):
- [ ] Aba Bordas e margens: recorte com Espelhado e Proporção travada, medidas em cm enquanto arrasta, tamanho da folha (A4/A5/Carta), moldura e margem branca, mover e redimensionar o conteúdo na folha, qualidade da prévia. Entra junto de 2.4 a 2.6.
- [ ] Aba Filtro: três tipos de preto e branco (Sauvola, Otsu, Wolf), limpar pontinhos e o aviso de "escuro/apagado demais". Entra junto de 2.7 e 2.8. *(Fase sugerida pela gerente, a confirmar pelo Samuel: o Registro de 25/09 não diz a fase deste.)*

### FASE 3 — Seleção manual no nível do Photoshop

Para corrigir onde o automático errar.

- [ ] 3.1 Selecionar objeto com um clique (a IA só aponta, não desenha)
- [ ] 3.2 Seleção rápida (pincel que gruda na borda)
- [ ] 3.3 Varinha mágica com tolerância e "só a área encostada"
- [ ] 3.4 Intervalo de cores com suavidade (substitui o "pegar tudo desta cor" atual)
- [ ] 3.5 Laço, laço magnético, retângulo, oval
- [ ] 3.6 Refinar a borda da seleção
- [ ] 3.7 Somar, tirar e cruzar seleções; salvar seleção
- [ ] 3.8 Consertar o zoom que às vezes não funciona e o travamento com muitos cliques
- [ ] 3.9 Tudo testado com mouse de verdade, não só com clique simulado

**Já no programa, a aperfeiçoar nesta fase** (feito de 17 a 23/09; ver Registro de mudanças, 25/09):
- [ ] Aba Marcar: detecção automática por botão (não detecta mais sozinha ao abrir) e "usar em todas" / "só nas próximas".

### FASE 4 — Layout Photoshop / After Effects

Feito pelo agente de layout, a partir do plano discutido na conversa separada (ver seção 3). **Começa em paralelo com a Fase 1**, assim que o plano do layout estiver pronto.

**Já no programa, a aperfeiçoar nesta fase** (feito de 17 a 23/09; ver Registro de mudanças, 25/09):
- [ ] Tela de Configurações com atalhos de teclado editáveis.

### FASE 5 — Desempenho

- [ ] 5.1 Atingir, no notebook do Kaique, os tempos combinados depois da Fase 0.
- [ ] 5.2 Rodar bem sem placa de vídeo dedicada.

### FASE 6 — O resto do resultado final

- [ ] 6.1 Mancha do verso (subtrair usando a frente e o verso da mesma folha)
- [ ] 6.2 Manchas vermelhas e marrons sem mexer no título (Palatino 66, 76)
- [ ] 6.3 Tinta vermelha não virar preto (Graduale, Horas)
- [ ] 6.4 Apagar texto repetido em todas as páginas (endereço de site, Escola de Jesus 7)
- [ ] 6.5 Cadernos: caminho rápido, marca de alceamento, numeração
- [ ] 6.6 Decidir: separar chapas vermelho/preto para as prensas de duas cores?
- [ ] 6.7 Comparação final com o CamScanner: o programa já substitui?
- [ ] 6.8 Instalador testado no notebook do Kaique

### FASE 7 — Treinar os OCRs para transcrever

- [ ] 7.1 Decidir a regra da IA no OCR (opções a, b, c do documento `OCR-PESQUISA.md`)
- [ ] 7.2 Treinar mais de um OCR (Tesseract, Calamari e Kraken; o Kraken precisa do WSL no Windows)
- [ ] 7.3 Decidir se os manuscritos (Graduale, Palatino) entram

---

## 5. Lista de bugs (resolvida no começo de cada fase)

| Data | Bug | Onde | Print |
|---|---|---|---|
| 15-16/09 | Travamento ao usar o zoom muitas vezes; roda do mouse não funciona às vezes | aba Marcar | — |
| 24/09 | Zoom não funciona em algumas sessões | — | — |

## 6. Lista de espera (ideias novas)

| Data | Ideia | Quem pediu | Fase sugerida |
|---|---|---|---|
| 24/09/2026 | Ver todas as páginas do livro em grade, como o "Organizar páginas" do UPDF: seleção múltipla, girar, apagar, extrair, inserir, dividir. Referência: `referencias-layout/updf-todas-as-paginas.jpg` | Samuel | Fase 4 (layout), a confirmar |
| 24/09/2026 | Layout limpo como o do UPDF: página no centro, poucas ferramentas em ícones numa barra fina no topo, miniaturas numa coluna à esquerda que dá para esconder, navegação e zoom num canto de baixo. Referência: `referencias-layout/updf-tela-de-leitura.jpg` | Samuel | Fase 4 (layout), a confirmar |
| 24/09/2026 | Aviso que o Kaique pediu (ainda sem descrição: o áudio enviado não fala disso) | Kaique | a definir |

## 7. Registro de mudanças

| Data | O que mudou | Por quê | Aprovado por |
|---|---|---|---|
| 24/09/2026 | Plano criado e discutido ponto por ponto | projeto parado há mais de 1 mês | Samuel |
| 25/09/2026 | As mudanças feitas de 17 a 23/09 (aba Bordas, Configurações, três tipos de preto e branco, aba Marcar, página nova em "Original") **ficam no programa principal**, marcadas como "a aperfeiçoar": Bordas/margens na Fase 2, aba Marcar na Fase 3, Configurações/atalhos na Fase 4. O ramo `trabalho-17-a-23-09` fica só como cópia de segurança. Os comentários de código de 22/09 entram no programa principal (pedido do Samuel: código comentado para manutenção futura). | o Samuel quer manter essas melhorias e não perder o trabalho | Samuel |
| 25/09/2026 | Item 0.3: as fotos do CamScanner (Mágico Pro, feitas pelo Kaique) estão em `camscanner/`. O calendário é do **Livro de Horas de Luís XIV, páginas 26 (NOVEMBRE) e 27 (DECEMBRE)**; a outra é a página 37 da "Na escola de Jesus". As três entram no gabarito para comparar o nosso resultado com o CamScanner. | resultado-alvo do plano (seção 2) | Samuel |
