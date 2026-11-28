# Testes à distância e o pedido de licença do Windows

Ficha criada no checkpoint de 18/11/2026 ([PARTE -38](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)),
como o plano da parte do Windows sugeriu. **O que manda:** o Livro de decisões (ramo `obra-2026-10-26`), o
[PLANO-DEFINITIVO](../../docs/plano/PLANO-DEFINITIVO.md) e o plano-v2 (`relatorios/plano-windows-2026-11-18/plano-v2.md`,
ramo `plano-windows-2026-11-18`, esperando a aprovação). Ficha irmã: [atualizador.md](atualizador.md).

**O que é:** a caixinha "Deixar o Samuel fazer testes neste computador" (Configurações > Testes à distância). Ligada, o
programa instala o Servidor OpenSSH, abre a porta só para a rede do Tailscale, cria a conta escondida EditorTestes e
deixa o Samuel entrar de longe para testar e mandar atualizar. Junto vive a "primeira abertura" (o preparo: cria o
ajudante, tira o Editor antigo), que também pede a licença do Windows ("Deseja permitir...?").

## Situação (18/11/2026)

- **Não está pronta.** Na etapa 5 (18/11) funcionou: ligar no Windows (8 de 9 passos), entrar por SSH com senha só na
  conta de testes, a conta sem ver a pasta do Samuel nem ter administrador (no C:), a prioridade baixa, o teste rápido e
  a atualização de longe. **Falhou:** o "Não" ou a falha da pergunta viram "preparado"; a pergunta não aparece com o
  programa atrás; o programa não lê o relatório do próprio script; a tranca da pasta deixa os arquivos sem licença;
  "Desligado" sem desligar; o desfazer do desinstalar; o perfil preso.
- As 4 causas (revisão `revisao-distancia-2026-11-18`): a tela mostra o anotado, não o que o Windows tem; ligar não desfaz
  o meio; o programa não lê a resposta de quem trabalhou com licença; a tranca feita à mão.

- **27/11/2026 ([PARTE -47](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §4):** a vistoria achou, e a gerente conferiu no código (não rodado), que na 1.1.0
  do Kaique a caixinha e o botão "Testes à distância" das **Configurações** ainda ligam pelo pedido antigo de licença
  (`aplicar_no_windows`, o `runas` de 18/11), contra a D-825 ("nesta entrega a senha não liga nada", que só a janela da
  primeira abertura cumpre); e que nesse caminho o "Não" do Windows pode virar "Ligado" (`_rodar_elevado` lê
  `ctypes.get_last_error()` sem `use_last_error=True`). Na Lista de bugs; nada consertado (D-886).

## O que vale hoje

- **Ligar é tudo ou nada** (D-771, "A"): se um passo falhar, desfaz o que fez naquela vez e diz "Desligado" e o motivo.
- **A tela mostra o que o Windows tem de verdade**, nunca o que o programa anotou (CLAUDE.md §11.12 ponto 2; o Samuel:
  "então ele vai verificar no beck end realmente e não só olhar a tela?").
- **O Servidor OpenSSH vem do Windows Update** na hora de ligar, com aviso de internet e de até 15 minutos (D-772, "a" ·
  "mantenho, qual a proxima coisa"); levou 13 min no PC dele.
- **Duas trancas, sem a prova do celular** (D-780: "não quero fazer essa prova com o celular, eu quero que tu programa o
  negocio e ele funcione"): a do firewall e a de dentro do servidor; o programa confere as duas depois de ligar. A entrada
  vinda de fora fica "conferida por dentro" até o primeiro teste no notebook do Kaique.
- **A janela da senha:** dois campos e um botão de ver (D-781: "quero os dois campos e a possibilidade de apertar o botão
  para poder ver a senha enquanto digita"). O desenho vai a ele antes de construir.
- **Na pergunta do Windows aparece "Editor de Impressão"**, com a faixa amarela de "Editor desconhecido", e um aviso do
  programa antes (D-782: "ele não vai pensar isso" · "sim"). Se isso pedir arquivo com acento: ponto 3 da seção 6.3 do
  plano-v2, **esperando ele**.
- **O Samuel desliga o Controle Inteligente de Aplicativos** no notebook do Kaique ao instalar (D-783: "eu desligo quando
  for instalar."); desligado, não liga mais sem reinstalar o Windows.
- **O que roda à vista** (D-785): instalar, desinstalar, a pergunta do Windows, a primeira abertura, toda a atualização,
  ligar e desligar os testes, as tarefas, o que muda o Windows, publicar e as janelas do próprio Windows. Escondidos só os
  testes automáticos, os prints da Central, o `teste_botoes.py` e os de imagem. Na dúvida, à vista e perguntar.

## Mudou em

- 16-17/11/2026 — a frente do Kaique: OpenSSH e Tailscale (D-705 a D-722), senha só no instalado (D-728), desinstalar
  tira tudo (D-731), a pergunta volta até "Sim" (D-741). **Não cumpridas na etapa 5:** D-731 e (pelo defeito) D-741.
- 18/11/2026 — ligar "deixa o que deu certo" → tudo ou nada (D-771); a prova do celular → sem ela (D-780); um campo de
  senha → dois e o botão (D-781); "Windows PowerShell" na pergunta → "Editor de Impressão" (D-782).

## Tentado e descartado

- **Testar a pergunta do Windows numa área de trabalho escondida:** o Windows não deixa a pergunta aparecer (etapa 5).
- **Trancar a pasta com `icacls ... /inheritance:r` passando nos arquivos de dentro:** deixa a lista de licenças vazia
  (provado). O plano usa uma pasta segura de fábrica (Arquivos de Programas), sem tranca feita à mão.
- **Remendar cada defeito onde apareceu:** deixaria as 4 causas de pé.

## Comportamento real já provado (não redescobrir)

- `ctypes.get_last_error()` sem `use_last_error=True` dá sempre 0 (o Windows disse erro 2).
- A pergunta de administrador fica numa tela protegida: não dá print.
- Com o programa atrás de outra janela, só pisca um escudo na barra de tarefas, e o pedido cai sozinho.
- A pasta de `tempfile.mkdtemp` do Python 3.14 nasce só para o dono: o relatório do administrador fica ilegível.
- A senha mandada ao Windows pelo jeito de hoje perde os acentos ("maçã-Ação" → "maþÒ-AþÒo", com texto de exemplo).
- O perfil de uma conta apagada depois de entrar por SSH fica preso até reiniciar (`C:\Users\editortestes`).
- O D: dá Controle total a "Todos": a conta de testes lê e grava lá. No notebook do Kaique, conferir outros discos e
  pendrives na etapa 6.
- O estado de verdade (serviço, conta, regra do firewall, portas, tarefas) se lê sem administrador.

## De onde veio

- Pedido de 16/11: "vamos colocar uma api no programa para que eu possa fazer chamadas dentro do proprio pc do kaique
  para fazer testes de velocidade e outras coisas" ([PARTE -37](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §1).
- 18/11: os 7 defeitos da etapa 5 e "quero que faça as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros
  na hora de montar a estrutura do atualizador e testes a distancias" (D-767).
- Relatórios (fora do `fase-1`): etapa 5 (`etapa5-2026-11-17`), `revisao-distancia-2026-11-18`, `plano-windows-2026-11-18`.
