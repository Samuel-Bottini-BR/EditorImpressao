# ONDE PAREI — etapa 3 da frente do Kaique (a atualização sozinha, com o Velopack)

Agente implementador, 16/11/2026. Cópia `.claude/worktrees/kaique-etapa3`, ramo `kaique-etapa3-2026-11-16`
(feito do `obra-2026-10-26`, `9414405f`).

## Decisões que esta tarefa precisa cumprir (número + palavras do Samuel)

- **D-706** "a atualização via internet tem que ser como funciona com apps, não pode ser ele ter que baixar de novo um
  instalador fazer tudo de novo" · "as atualizaçõpes não podem estar ligadas via api".
- **D-713** "não precisa ser privado" (o GitHub do projeto continua público; as versões vêm dele).
- **D-714** "1 - vamos seguir sua sugestão" (versão para o Kaique publicada de propósito, nunca a cada salvamento) ·
  "e sim o programa pega sozinho, toda vez que o pc inicializar em segundo plano, assim como os nossos testes acontecem."
- **D-715** "ele dá um aviso se o programa estiver aberto, um aviso para salvar o trabalho atual e reinicializar o
  programa".
- **D-718** "Sim, e tem que avisar a gente de alguma maneira" (se falhar, volta para a versão anterior).
- **D-719** "1" — na tela: "A atualização não deu certo. O programa voltou para a versão anterior e continua
  funcionando. Avise o Samuel."; o erro num registro que a gerente lê daqui; nenhuma senha dentro do programa.
- **D-720** "Sim" — o aviso tem "Reiniciar agora" e "Depois"; com "Depois", entra na próxima vez que o computador ligar.
- **D-722** "Sim" — testar antes no PC do Samuel e desfazer no fim (isto é a etapa 5; aqui nada é instalado de verdade).
- **D-723** "velopack" — o Inno Setup sai, entra o Velopack (Arquivos de Programas, pede administrador); a tarefa do
  Windows aplica ao ligar; a instalação de 28/10 sai; os testes antigos do instalador só mudam com o "sim" dele.
- **D-724** "gratis, mas o que é essa assinatura e é segura?" — o PC do Samuel assina cada versão com uma chave só dele;
  o programa confere antes de instalar; a que não bater não é instalada. A chave nunca no GitHub, com cópia de reserva.
- **D-727** "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né" — nada baixado na
  hora de instalar (o Visual C++ continua dentro).
- **D-605** (regra §11.8): o novo não estraga o que já está escolhido e testado.

## O que já está escolhido e testado aqui

- `empacotar.py` + `instalador.iss` (Inno): as travas dos modelos, das duas DLLs do ScanTailor, do motor do Kraken, do
  Tesseract com 6 idiomas e do Visual C++ oficial (assinatura da Microsoft), e a limpeza que só apaga o que o script gera.
  Testes: `tests/test_empacotar.py` (todos), `tests/test_empacotar_teste_velocidade.py`, `tests/test_requirements.py`,
  `tests/test_ocr_diagnostico.py`, `tests/test_botoes_em_portugues.py` (varre `ui/` e `main.py`).
- `main.py`: `--servidor-de-paginas` e `--conferir-ocr` atendidos antes de qualquer janela; `sys.excepthook`.
- `historico.pasta_de_dados` (`%LOCALAPPDATA%\EditorImpressao`): os projetos do Kaique. Desinstalar não apaga (CLAUDE.md §7).
- `ui/perguntas.py`: caixas com botões escritos por nós.
- **Nada disso muda.** O `instalador.iss` só deixa de ter o número da versão escrito nele: passa a recebê-lo do
  `empacotar.py` (um lugar só). Todos os textos que os testes antigos conferem continuam lá.

## Como fica para quem usa e no livro (o Kaique, passo a passo)

1. **Primeira vez:** ele recebe um instalador novo e dá dois cliques. O Windows pergunta "Deseja permitir...?"; ele
   clica "Sim". O programa vai para Arquivos de Programas. A instalação velha (a de 28/10) sai sozinha; os livros e
   projetos dele (`%LOCALAPPDATA%\EditorImpressao`) ficam como estão. Tudo vem dentro do instalador (sem internet).
2. **Todo dia:** o computador liga; uns minutos depois, por trás, sem janela, o programa procura a "versão para o
   Kaique" no GitHub. Se houver e a assinatura conferir, baixa só o que mudou e troca. Ele não vê nada; da próxima
   vez que abrir, já é a nova.
3. **Se ele estiver com o programa aberto** quando a versão nova chega: aparece "Chegou uma versão nova do programa..."
   com "Reiniciar agora" e "Depois". "Reiniciar agora": o programa grava o trabalho, fecha e abre na versão nova (o
   Windows pode perguntar "Deseja permitir...?" uma vez). "Depois": nada muda agora; entra quando o computador ligar.
4. **Se der errado** (assinatura que não confere, troca que falha, versão nova que não abre): o programa fica (ou volta)
   na versão anterior e, na próxima vez que ele abrir, aparece uma vez: "A atualização não deu certo. O programa voltou
   para a versão anterior e continua funcionando. Avise o Samuel."
5. **No livro (PDF):** nada muda. Nenhum filtro, ferramenta ou tela de trabalho é tocado.

## O meu plano (o que vou fazer, onde, a regra num lugar só, como provo)

Por que assim: é o que o Samuel decidiu (D-714, D-723, D-724, D-727). O que é nosso é só a cola entre o Velopack e a
tarefa do Windows; a troca dos arquivos e a volta quando a troca falha são do próprio Velopack.

1. **`versao.py` (novo):** `VERSAO` — o único lugar do número. Usado por `empacotar.py` (Inno via `/DMinhaVersao=`,
   Velopack via `--packVersion`), pelo comando de publicar e pela atualização. Não há tela "Sobre": não crio nenhuma.
   A primeira versão do Velopack será a `1.1.0` (a de 28/10 do Kaique era a `1.0.0` do Inno).
2. **`assinatura.py` (novo):** Ed25519, o método da RFC 8032 (o mesmo do Mac, do minisign, do TUF), com o código de
   referência da própria RFC e os vetores de teste dela. Não há biblioteca de assinatura no `.venv` (`cryptography` não
   está instalada e só tenho licença para acrescentar o `velopack`). A chave pública do Samuel fica dentro do programa;
   a privada fora do repositório.
3. **`atualizacao.py` (novo; sem Qt):** a regra inteira num lugar só —
   `procurar_e_preparar` (confere a assinatura ANTES de baixar; baixa; se o programa está aberto, deixa "pendente";
   se fechado, pede ao Velopack para trocar e reabrir escondido em `--conferir-a-versao-nova`);
   `conferir_versao_nova` (teste rápido escondido; se falhar, volta para a anterior com o próprio `Update.exe` e um
   pacote assinado); `o_que_avisar` (o que a tela mostra); `registrar` (o registro em
   `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`, que a conta de testes lê); a tarefa do Windows
   (XML, criar, apagar); a marca de "programa aberto"; tirar a instalação do Inno; o Visual C++ de dentro do pacote.
   `atender_linha_de_comando(argv)` é a única entrada: `main.py` chama uma vez, antes de qualquer janela.
4. **`ui/aviso_de_atualizacao.py` (novo):** liga na janela (uma linha no `main.py`): a marca de aberto, um relógio que
   pergunta `atualizacao.o_que_avisar` e mostra o aviso com `ui.perguntas` ("Reiniciar agora" / "Depois") ou o aviso
   da falha (D-719, uma vez). Não toca nas Configurações nem na janela da senha (etapa 4).
5. **`empacotar.py`:** funções novas para o pacote do Velopack (põe o Visual C++ oficial dentro, monta o comando do
   `vpk pack --msi --instLocation PerMachine`, confere que o pacote leva modelos, DLLs, motor, Tesseract e Visual C++).
   A pasta continua sendo feita pela mesma `construir_pasta` (as mesmas travas). O Inno continua lá, sem mudar nada.
6. **`publicar_versao_kaique.py` (novo):** o comando de publicar de propósito: acha a chave (para se não houver),
   confere que a chave bate com a do programa, empacota, `vpk pack`, assina, confere a própria assinatura e publica no
   GitHub (`vpk upload github` + o arquivo da assinatura) ou numa pasta (o servidor de mentira). Token só no PC do
   Samuel, na hora (`gh auth token`), nunca no programa.
7. **Provas:** `tests/test_decisoes_atualizacao.py` (cada decisão) e `tests/test_assinatura.py` (vetores da RFC). E um
   ensaio de verdade: um programinha de mentira empacotado pelo PyInstaller e pelo Velopack (as mesmas funções), versão
   1 numa pasta de teste (pacote "portátil", sem instalar), versão 2 publicada numa pasta-servidor, a atualização
   de mentira 1 → 2, a assinatura errada recusada, e a volta.

**Regra num lugar só:** número da versão → `versao.VERSAO`; assinatura → `assinatura.conferir_versao`; "o que fazer
com a versão nova" → `atualizacao.procurar_e_preparar`; "o que a tela avisa" → `atualizacao.o_que_avisar`; falha →
`atualizacao.registrar_falha`; programa aberto → `atualizacao.ha_programa_aberto` / `marcar_programa_aberto`.

## Andamento

- [ ] plano (este arquivo) — commit
- [ ] versao.py + Inno lendo a versão
- [ ] assinatura.py + vetores da RFC
- [ ] atualizacao.py + testes
- [ ] ui/aviso_de_atualizacao.py + main.py
- [ ] empacotar.py (Velopack) + publicar_versao_kaique.py
- [ ] chave de verdade criada fora do repositório
- [ ] ensaio de mentira 1 → 2 (portátil, pasta de teste)
- [ ] GitHub (conjunto + filtro de velocidade), relatório

## Perguntas para o Samuel

(nenhuma ainda)

## Ressalvas (para a etapa 5)

(a preencher)
