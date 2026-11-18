# ONDE-PAREI — estudo: o motor do Kraken fora do pacote que se atualiza (18/11/2026)

Pesquisador. Ramo `kraken-separado-2026-11-18` (a partir de `obra-2026-10-26`, `66149fa0`), cópia
`.claude/worktrees/kraken-separado`. Só leitura e escrita deste relatório: **nenhuma linha do programa nem dos testes
mudou**, nada instalado, nenhuma janela aberta na tela do Samuel, nenhuma pergunta do Windows.

## Situação

- [x] Leituras (pesquisador.md, CLAUDE.md inteiro com §11.12 e §11.13, memória: índice, 6.8, 1.3, ambiente, Livro:
      D-723, D-724, D-727, D-731, D-732, D-764, D-766 a D-783, D-132, D-138 a D-140, D-164, D-356, D-480).
- [x] Plano da parte do Windows (inteiro) e estudo de publicar mais rápido (inteiro).
- [x] Código do Velopack 1.2.161 (só leitura, `saida_teste/publicar-rapido/fonte-velopack/`).
- [x] Nosso código (só leitura): `core/ocr_kraken.py`, `core/linhas_do_texto.py`, `core/ocr_diagnostico.py`,
      `atualizacao.py`, `empacotar.py`, `publicar_versao_kaique.py`, `assinatura.py`, `versao.py`, testes que citam o motor.
- [x] Medidas leves (ver relatório, seção 10). A pasta de medida que criei em `saida_teste/kraken-separado/medida-extrair`
      (916 MB, 3.582 arquivos, só meus) foi apagada no fim; a pasta vazia `saida_teste/kraken-separado/` ficou.
- [x] Relatório nos três formatos: `relatorio.md`, `.html`, `.pdf` nesta pasta.
- [x] Commit e push do ramo.

## Decisões que esta tarefa precisa cumprir (palavras dele, do Livro)

- **D-768** (18/11): "mas dai vai ter que baixar o motor do kraken toda vez e reinstalar ele de novo?" · "vou escolher a
  16, vamos para a proxima" → o motor sai do pacote que se atualiza, instalado uma vez, baixado de novo só se mudar;
  entra agora; ele aprova o estudo antes de escrever.
- **D-727** (16/11): "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né" → nada
  baixado na hora de instalar.
- **D-724** (16/11): "gratis, mas o que é essa assinatura e é segura?" → versão sem a assinatura certa não é instalada.
- **D-731** (16/11): "ok" → desinstalar deixa o computador como era, menos os projetos.
- **D-764** (17/11): o desinstalador da 1.2.161 apaga a pasta do título; o nome interno é `EditorImpressaoPrograma`.
- **D-767** (18/11): "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione".
- **D-769** (18/11): "b" → com "Depois", troca ao fechar o programa.
- **D-770** (18/11): "a" → a janelinha "Atualizando" em toda troca.
- **D-773** (18/11): "A" → provas com versões de verdade servidas por uma janela visível.
- **D-775** (18/11): "ok" → escrever, testes, outro agente tenta quebrar, depois a prova à vista.
- **D-776** (18/11): "Sim, no C só tem que cuidar para não encher o disco C inteiro" → publicar no C:, com reserva de
  20 GB livres.
- **D-777** (18/11): "ok, fica assim" → o .msi só na primeira entrega e quando ele pedir.
- **D-779** (18/11): "ta vamos continuar com ele, mas o que fazemos para ele não dar defeito [...]" → fica o Velopack 1.2.161.
- **D-782** (18/11): "sim" → a pergunta do Windows mostra "Editor de Impressão".
- **D-138/D-140** (29/09): "todos os OCRs instalados [...] o Kraken direto no Windows, sem WSL" → o motor continua indo
  ao Kaique.
- CLAUDE.md §11.12 (ampliada em 18/11, ponto 6) e §11.13.

## O que já está escolhido e testado aqui (D-605)

- O motor à parte do Kraken (D-140) e a sua ponte (`core/ocr_kraken.py`, `tests/test_ocr_kraken.py`, 29 testes).
- O Visual C++ dentro do pacote, instalado pelo ajudante só se faltar (D-727; `tests/test_decisoes_atualizacao.py`).
- A assinatura (`assinatura.py`, `tests/test_assinatura.py`, o teste da D-764).
- O instalador do Inno (`tests/test_empacotar.py`, 32 testes; continua até o Samuel decidir tirá-lo).
- Pela busca nos testes (`grep motor-kraken|PASTA_DO_MOTOR|AMOSTRA_DO_MOTOR|lugares_do_motor`), **nenhum teste antigo
  cobra o motor dentro do pacote do Velopack**: o de `test_decisoes_atualizacao.py` monta a lista com a própria função
  (`esperados_no_pacote_do_velopack`). Os do Inno cobram o Inno. A conferir de novo na hora de escrever.

## Como fica para quem usa e no livro (D-637)

- **Kaique, primeira vez:** instala pelo .msi como já combinado. Na primeira abertura, depois do "Sim" do Windows, o
  programa põe o motor no lugar dele (uns minutos a mais na janelinha de espera, só nessa vez; conta, não medido).
- **Kaique, cada versão nova:** igual a hoje para ele (aviso, "Reiniciar agora" ou "Depois"); a troca fica bem mais
  curta e baixa uns 460 MB em vez de 826 MB (conta a partir do pacote medido).
- **Kaique, quando o motor muda (raro):** nada novo na tela; a versão demora mais para chegar só dessa vez.
- **No livro e no PDF:** nada muda. Hoje o Kraken nem é usado no caminho do livro (a "segunda opinião" está desligada,
  `core/linhas_do_texto.py:85`; só a conferência `--conferir-ocr` o abre).

## A peça de fora, lida (CLAUDE.md §11.12, ponto 6)

Velopack 1.2.161 (`92d6a1c9`, MIT), código em `saida_teste/publicar-rapido/fonte-velopack/repo`:

| Caso que usamos | O que o Velopack faz | Fonte |
|---|---|---|
| Trocar de versão | renomeia `current` para uma pasta temporária e põe a nova no lugar; nada mais da raiz é apagado | `src/bins/src/commands/apply_windows_impl.rs:129-177` |
| Trocar com processo aberto | fecha à força tudo o que roda dentro da raiz (inclusive o motor, se estiver lá) | `apply_windows_impl.rs:159`, `src/bins/src/shared/util_windows.rs:81-98` |
| Pasta temporária da troca | `<packages>\VelopackTemp\tmp_<16 letras>` | `src/lib-rust/src/locator.rs:205-213` |
| Onde guarda o pacote baixado | `<raiz>\packages\` se a raiz aceita gravação (o ajudante, como o sistema); senão `%LOCALAPPDATA%\<id>\packages` | `locator.rs:153-166`, `src/lib-rust/src/manager.rs:408-412` |
| Ao baixar | apaga os `*.nupkg` e `*.partial` velhos da pasta `packages` | `manager.rs:419-432` |
| Desinstalar pelo .msi | apaga a pasta de instalação inteira (como o sistema), a `%LOCALAPPDATA%\<id>` e o temporário | `src/wix-dll/src/lib.rs:82-127`; `Msi/Templates/MsiTemplate.hbs:197-199, 235` |
| Desinstalar sem .msi | recusa (manda usar o msiexec) | `src/bins/src/commands/uninstall.rs:9-11` |
| O que o .msi instala | `INSTALLFOLDER\current` e `INSTALLFOLDER\packages` | `MsiTemplate.hbs:17-21` |
| "Instalar por cima" com outro .msi | o modelo não tem regra de atualização maior (`MajorUpgrade`): **não sei** o que acontece | `MsiTemplate.hbs` (procurado, não achado) |
| Peça instalada uma vez e nunca trocada | **não existe**; a documentação manda guardar o que deve durar "um nível acima de `current`" (dura nas trocas, sai ao desinstalar) | `docs/integrating/preserved-files.mdx`; `docs/integrating/uninstalling.mdx` |
| Dependências que ele instala | só uma lista fixa de peças da Microsoft (Visual C++, .NET, WebView2), baixadas da internet | `src/bins/src/windows/runtimes.rs:45-73`, `prerequisite.rs:43-56` |
| Lista de versões no GitHub | lê só as 10 publicações mais novas, pula as que não têm `releases.win.json` e as "pré-lançamento" | `src/lib-rust/src/sources/github.rs:77-88`, `sources/mod.rs:112-144` |

O caminho real da instalação, visto na etapa 5: `C:\Program Files\EditorImpressaoPrograma\`
(`saida_teste/etapa5/registros/comparar-0-com-2.txt`).

## Lista das falhas (o que pode dar errado ao pôr o motor no lugar, e o que o programa faz)

Ver o relatório, seção 4. Resumo: sem internet, internet que cai, disco cheio, notebook desligado no meio, antivírus
que tira um arquivo, assinatura errada, motor estragado depois, "Não" na pergunta do Windows, desinstalar com o motor
aberto. Em todos: o motor velho continua, nunca fica meio motor com o nome certo, e o registro diz o que houve.

## Perguntas para o Samuel

(no formato do CLAUDE.md §11.13; as mesmas do relatório, seção 9)

### Pergunta 1. Onde fica o motor do Kraken e como ele chega

- **Do que se trata.** É a peça do programa que acha as linhas de texto (o "Kraken"). Tem 1 GB e 34 mil arquivos, quase
  todos os arquivos do programa. Fica dentro da pasta do programa, em Arquivos de Programas.
- **O que acontece hoje.** Ela vai inteira em toda versão nova, e o notebook do Kaique a desmonta e monta de novo a cada
  troca. É por isso que a troca leva uns 7 minutos e meio.
- **O que você escolhe:**
  - **Uma pasta própria do motor, junto do programa (sugestão).** A atualização não mexe nela. Na primeira vez ela vem
    dentro do instalador. Quando o motor mudar (raro), o programa baixa só ele, com a sua assinatura. Desinstalar tira
    junto. A versão nova fica com uns 460 MB, e a troca com uns 2 a 3 minutos (conta, não medida). Nada muda na tela
    nem no livro.
  - **Um segundo programa só para o motor.** O Windows mostra dois programas na lista ("Editor de Impressão" e "Motor
    do Kraken"), e desinstalar um não tira o outro sozinho. Não recomendo.
  - **Só comentário.**
- **De onde veio.** Pedido seu de hoje. A ferramenta de atualização não tem um jeito próprio para isso; a documentação
  dela manda guardar o que deve durar numa pasta ao lado da do programa, que é a sugestão.
- **Bom saber.** Hoje o Kraken ainda não é usado em nenhuma tela: a "segunda opinião" dele está desligada. Ele vai ao
  Kaique porque você decidiu, em 29/09, "todos os OCRs instalados".
- **Situação.** Só estudo; nada escrito. Acrescenta ao plano uns 12 a 18 horas de trabalho de agente e uns 20 a 40
  minutos nas provas com você.

### Pergunta 2. A versão inteira ou só o que mudou, agora sem o motor

- **Do que se trata.** É a atualização que chega sozinha no notebook do Kaique quando ele abre o programa. Hoje de manhã
  você deixou essa escolha para depois deste estudo.
- **O que acontece hoje.** Ele baixa só o que mudou (uns 20 MB), mas o notebook remonta a versão inteira antes de trocar
  (22 minutos no seu PC). E por esse caminho a sua assinatura não confere tudo.
- **O que você escolhe:**
  - **A versão inteira (sugestão).** Sem o motor, ela fica com uns 460 MB: uns 1 minuto e meio a 50 Mbps, uns 6
    minutos a 10 Mbps (conta). A troca fica em uns 2 a 3 minutos. A assinatura confere tudo.
  - **Só o que mudou.** Baixa uns 20 MB, mas o notebook ainda remonta a versão (uns 5 a 7 minutos a mais; conta). E a
    assinatura precisa passar a conferir a diferença também (mudança no programa).
  - **Só comentário.** Se souber, diga a velocidade da internet do Kaique.
- **Situação.** Aberta desde hoje de manhã; o resto do plano não depende dela.

### Pergunta 3. Quando o motor muda, a versão nova espera ele chegar?

- **Do que se trata.** É o caso raro em que uma versão nova do programa precisa de um motor novo.
- **O que você escolhe:**
  - **Sim, tudo ou nada (sugestão).** A versão nova só entra depois que o motor novo chegou inteiro e conferido. Se a
    internet cair, o Kaique continua na versão de antes, com o motor de antes, e o programa tenta de novo na próxima
    abertura. É o mesmo jeito que você escolheu para os testes à distância.
  - **Não.** A versão nova entra logo e o motor chega depois; nesse meio-tempo, o Kraken não funciona.
  - **Só comentário.**
- **Situação.** Só estudo. Nada do que já funciona muda.

## Como cumpri cada uma

- D-768: o estudo responde às 8 perguntas da gerente (relatório, seções 1 a 8), com a recomendação e o tempo.
- D-727: o motor vai dentro do instalador da primeira entrega (seção 2.1); nada baixado ao instalar.
- D-724: o motor só entra com a assinatura do Samuel, pela mesma peça `assinatura.py` (seção 2.3).
- D-731/D-764: desinstalar tira o motor pelo próprio desinstalador do Velopack, lido no código (seção 4.2).
- D-767/D-775: a seção 7 lista as provas à vista e onde entram nas sessões do plano.
- D-776: publicar sem o motor usa menos espaço no C: (seção 5).
- D-777: o motor entra só no instalador (seção 2.1).
- D-779: nada exige outra versão do Velopack (seção 8).
- §11.12 ponto 6: a tabela acima, com a fonte de cada afirmação.
- §11.13: as três perguntas acima.

## Disco

- Criado e apagado: `saida_teste/kraken-separado/medida-extrair/` (916 MB, 3.582 arquivos). Ficou a pasta vazia
  `saida_teste/kraken-separado/`.
- Scripts de medida no scratchpad da sessão (fora do projeto, não apagados, poucos KB).
- Nada gravado no C: além desses scripts.
