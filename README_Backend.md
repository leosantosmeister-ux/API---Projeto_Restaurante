# Backend - API de Reservas em Restaurantes

Este projeto faz parte do **MVP da disciplina Desenvolvimento Full Stack Básico**, desenvolvido como parte da **Pós-Graduação em Engenharia de Software da PUC-Rio**.

O objetivo da aplicação é disponibilizar uma API REST para gerenciamento de clientes, cardápio, mesas, reservas, itens das reservas e pagamentos.

## Tecnologias utilizadas

- Python
- Flask
- SQLite
- Flasgger / Swagger
- Werkzeug
- Threading

## Funcionalidades

### Clientes

- Cadastro de clientes
- Login
- Consulta de clientes
- Alteração de dados
- Alteração de senha
- Exclusão de clientes
- Validação de CPF, telefone, e-mail e senha
- Senhas armazenadas utilizando hash

### Cardápio

- Cadastro de itens
- Consulta de itens
- Filtros por nome, categoria e valor
- Alteração de itens
- Exclusão de itens

### Mesas

- Consulta e gerenciamento de mesas
- Controle da capacidade das mesas

### Reservas

- Criação de reservas
- Consulta de reservas
- Alteração de reservas
- Cancelamento de reservas
- Controle de conflitos de horários
- Validação da capacidade das mesas
- Controle da duração da reserva
- Controle do status da reserva

### Itens da Reserva

- Inclusão de itens do cardápio em uma reserva
- Consulta dos itens
- Alteração dos itens
- Exclusão dos itens

### Pagamentos

- Registro de pagamentos
- PIX
- Cartão de crédito
- Cartão de débito
- Dinheiro
- Controle do status do pagamento
- Confirmação da reserva após o pagamento

### Automação

O sistema possui uma rotina automática que verifica as reservas aproximadamente a cada 60 segundos.

- Reservas `PENDENTE` há mais de 2 horas são alteradas para `CANCELADA`.
- Reservas `CONFIRMADA` que atingiram o horário de término são alteradas para `CONCLUIDA`.

## Estrutura do projeto

- `Projeto_Restaurante_API.py` - Arquivo principal da aplicação Flask.
- `Projeto_Restaurante_Banco_de_Dados.py` - Criação e conexão com o banco de dados SQLite.
- `Projeto_Restaurante_Automacoes.py` - Rotinas automáticas para atualização dos status das reservas.
- `Projeto_Restaurante_Rotas_Cardapio.py` - Rotas relacionadas ao cardápio.
- `Projeto_Restaurante_Rotas_Clientes.py` - Rotas relacionadas aos clientes e autenticação.
- `Projeto_Restaurante_Rotas_Mesas.py` - Rotas relacionadas às mesas.
- `Projeto_Restaurante_Rotas_Reservas.py` - Rotas relacionadas às reservas.
- `Projeto_Restaurante_Rotas_Itens_da_Reserva.py` - Rotas relacionadas aos itens das reservas.
- `Projeto_Restaurante_Rotas_Pagamentos.py` - Rotas relacionadas aos pagamentos.
- `requirements.txt` - Dependências utilizadas no projeto.
- `README_Backend.md` - Documentação do projeto.

## Banco de dados

O projeto utiliza **SQLite** como banco de dados.

As principais tabelas são:

- `Cardapio`
- `Clientes`
- `Mesa`
- `Reservas`
- `Itens_da_Reserva`
- `Pagamentos`

O banco possui chaves estrangeiras, restrições de integridade e dados iniciais para o funcionamento do sistema.

São cadastradas inicialmente **20 mesas**, com capacidades de 2, 4, 6, 8 e 10 lugares.

O cardápio também possui dados iniciais distribuídos entre as categorias:

- Refeição
- Lanche
- Sobremesa
- Bebida não alcoólica
- Bebida alcoólica

## Regras de negócio das reservas

A criação e alteração das reservas possuem algumas regras de negócio.

- A reserva deve ser realizada com pelo menos 1 hora de antecedência.
- A duração mínima da reserva é de 60 minutos.
- A duração máxima da reserva é de 840 minutos.
- A reserva deve respeitar o horário de funcionamento do restaurante.
- Uma mesa não pode possuir duas reservas ativas no mesmo período.
- Reservas canceladas liberam as mesas reservadas para novos agendamentos.
- A capacidade da mesa deve ser compatível com a quantidade de pessoas.
- O cliente deve estar cadastrado para realizar uma reserva.
- A mesa selecionada deve existir no banco de dados.

## Capacidade das mesas

A capacidade necessária para a reserva é definida de acordo com a quantidade de pessoas:

- Até 2 pessoas: mesa para 2 pessoas.
- Até 4 pessoas: mesa para 4 pessoas.
- Até 6 pessoas: mesa para 6 pessoas.
- Até 8 pessoas: mesa para 8 pessoas.
- Mais de 8 pessoas: mesa para 10 pessoas.

## Status das reservas

As reservas podem possuir os seguintes status:

- `PENDENTE`
- `CONFIRMADA`
- `CANCELADA`
- `CONCLUIDA`

O fluxo principal da reserva é:

`PENDENTE` → pagamento realizado → `CONFIRMADA` → término da reserva → `CONCLUIDA`

Uma reserva também pode ser cancelada antes da sua conclusão.

## Pagamentos

Cada reserva pode possuir um pagamento associado.

As formas de pagamento disponíveis são:

- `PIX`
- `CARTAO_CREDITO`
- `CARTAO_DEBITO`
- `DINHEIRO`

Os pagamentos podem possuir os seguintes status:

- `PENDENTE`
- `PAGO`
- `CANCELADO`

Após o pagamento ser realizado, a reserva é confirmada.

## Automação das reservas

O sistema possui uma rotina automática executada em segundo plano.

Essa rotina verifica as reservas aproximadamente a cada 60 segundos.

### Cancelamento automático

Reservas que permanecerem com o status `PENDENTE` por mais de 2 horas são automaticamente alteradas para `CANCELADA`.

### Conclusão automática

Reservas com status `CONFIRMADA` são automaticamente alteradas para `CONCLUIDA` após o horário de término da reserva.

## Principais endpoints

### Clientes

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/cadastro_de_cliente` | Cadastrar cliente |
| POST | `/login` | Realizar login |
| GET | `/clientes` | Consultar clientes |
| PUT | `/clientes/<tipo_busca>/<valor_busca>` | Alterar dados do cliente |
| PUT | `/clientes/<numero_do_cliente>/senha` | Alterar senha |
| DELETE | `/clientes/<tipo_busca>/<valor_busca>` | Excluir cliente |

### Cardápio

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/cardapio` | Cadastrar item |
| GET | `/cardapio` | Consultar cardápio |
| PUT | `/cardapio/<numero_do_item>` | Alterar item |
| DELETE | `/cardapio/<numero_do_item>` | Excluir item |

### Reservas

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/reservas` | Criar reserva |
| GET | `/reservas` | Consultar reservas |
| PUT | `/reservas/<numero_da_reserva>` | Alterar reserva |
| DELETE | `/reservas/<numero_da_reserva>` | Cancelar reserva |

### Mesas

As rotas de mesas permitem consultar e gerenciar as mesas disponíveis no restaurante.

### Itens da Reserva

As rotas de itens da reserva permitem adicionar, consultar, alterar e excluir itens do cardápio associados a uma reserva.

### Pagamentos

As rotas de pagamentos permitem registrar o pagamento da reserva e controlar seu status.

As demais rotas e seus parâmetros podem ser consultados diretamente na documentação Swagger.

## Validações

A API possui validações para garantir a integridade dos dados recebidos.

Entre as principais validações estão:

- Campos obrigatórios.
- Campos não permitidos.
- CPF.
- E-mail.
- Telefone.
- Senha.
- Valores numéricos.
- Datas.
- Horários.
- Duração das reservas.
- Capacidade das mesas.
- Conflitos de horários.
- Existência do cliente.
- Existência da mesa.
- Existência dos itens do cardápio.
- Unicidade de CPF.
- Unicidade de e-mail.
- Integridade referencial do banco de dados.

## Segurança das senhas

As senhas dos clientes não são armazenadas em texto puro.

A aplicação utiliza o `Werkzeug` para gerar e verificar o hash das senhas.

A senha deve possuir:

- No mínimo 6 caracteres.
- Pelo menos uma letra maiúscula.
- Pelo menos uma letra minúscula.
- Pelo menos um número.
- Pelo menos um caractere especial.

## CORS

A API possui configuração de CORS para permitir requisições de diferentes origens.

Os métodos permitidos são:

- `GET`
- `POST`
- `PUT`
- `DELETE`
- `OPTIONS`

## Como executar

### 1. Criar um ambiente virtual

No terminal do VS Code, execute:

`python -m venv venv`

### 2. Ativar o ambiente virtual

No Windows:

`venv\Scripts\activate`

### 3. Instalar as dependências

Com o ambiente virtual ativado:

`pip install -r requirements.txt`

### 4. Executar a API

Execute:

`python Projeto_Restaurante_API.py`

A API será disponibilizada em:

`http://localhost:5000`

## Swagger

A documentação da API pode ser acessada através do Swagger:

`http://localhost:5000/apidocs/`

O Swagger permite visualizar e testar os endpoints diretamente pelo navegador.

## Testes

A API pode ser testada utilizando:

- Swagger
- Thunder Client
- Postman

## Códigos HTTP

A API utiliza os principais códigos HTTP:

- `200` - Operação realizada com sucesso.
- `201` - Recurso criado com sucesso.
- `400` - Dados inválidos ou requisição incorreta.
- `401` - Falha na autenticação.
- `404` - Recurso não encontrado.
- `409` - Conflito ou violação de regra de negócio.
- `500` - Erro interno do servidor.