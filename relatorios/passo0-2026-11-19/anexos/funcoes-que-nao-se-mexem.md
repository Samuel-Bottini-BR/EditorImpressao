# Funções que guardam lugares de outros passos (ressalva do pacote dos passos 3 e 4, achado Q3)

Para a gerente pôr no texto do plano que vai no pacote de cada passo. A lista de exceções identifica cada lugar pela função e pelo texto da linha: se o agente de um passo renomear ou mover uma função que guarda lugar de OUTRO passo, aquele lugar vira erro novo e o ramo barra (nenhum item entra na lista por ramo de agente). O montador já escreve isto sozinho no pacote quando recebe o passo: `python -m regras_dos_agentes pacote ... --passo 3 <arquivos>`.

Tirado da lista de 19/11/2026 (176 lugares, proposta), com os arquivos que têm lugares de cada passo. Se o pedido do passo trouxer outros arquivos, vale o que o montador escrever no pacote.

## Passo 3 (arquivos: `atualizacao.py`)

Não renomeie nem mova estas funções no passo 3:

- `atualizacao.py`, função `ao_desinstalar` (lugares do passo 5)
- `atualizacao.py`, função `criar_as_tarefas` (lugares do passo 5)

## Passo 4 (arquivos: `core/_testes_a_distancia_windows.py`, `core/testes_a_distancia.py`)

Não renomeie nem mova estas funções no passo 4:

- `core/testes_a_distancia.py`, função `_comando_apagar_a_pasta_das_tarefas_se_vazia` (lugares do passo 5)
- `core/testes_a_distancia.py`, função `_comando_preparar_o_desfazer` (lugares do passo 5)
- `core/testes_a_distancia.py`, função `_passos_das_nossas_tarefas` (lugares do passo 5)
- `core/testes_a_distancia.py`, função `_passos_dos_testes_a_distancia` (lugares do passo 5)
- `core/testes_a_distancia.py`, função `xml_da_tarefa_do_desfazer` (lugares do passo 5)

## Passos 2 e 5

- Passo 2 (`empacotar.py`): nenhuma função de outro passo nesse arquivo.
- Passo 5 (`atualizacao.py`, `core/testes_a_distancia.py`): vem depois dos passos 3 e 4; o montador lista, no pacote dele, os lugares que ainda sobrarem desses passos.
