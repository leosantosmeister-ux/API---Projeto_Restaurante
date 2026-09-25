import re
import sqlite3

from flask import Blueprint, request, jsonify
from Projeto_Restaurante_Banco_de_Dados import conexao_backend
from werkzeug.security import generate_password_hash, check_password_hash

rotas_clientes = Blueprint('rotas_clientes', __name__)

#VALIDAÇÃO_DO_CPF

def validar_cpf(cpf):

    if not re.fullmatch(r'\d{11}', cpf):
        return False

    if cpf == cpf[0] * 11:
        return False

    # Calcula o primeiro dígito verificador
    soma = 0

    for i in range(9):
        soma += int(cpf[i]) * (10 - i)

    resto = soma % 11

    if resto < 2:
        primeiro_digito = 0
    else:
        primeiro_digito = 11 - resto

    if primeiro_digito != int(cpf[9]):
        return False

    # Calcula o segundo dígito verificador
    soma = 0

    for i in range(10):
        soma += int(cpf[i]) * (11 - i)

    resto = soma % 11

    if resto < 2:
        segundo_digito = 0
    else:
        segundo_digito = 11 - resto

    if segundo_digito != int(cpf[10]):
        return False

    return True

#VALIDAÇÃO_DO_TELEFONE

def validar_telefone(telefone):

    telefone = re.sub(r'\D', '', telefone)

    if len(telefone) not in (10, 11):
        return False

    if len(telefone) == 11:

        if telefone[2] != '9':
            return False

    return True

#VALIDAÇÃO_DE_SENHA

def validar_senha(senha):

    if not isinstance(senha, str):
        return False

    if not re.search(r'[A-Z]', senha):
        return False

    if not re.search(r'[a-z]', senha):
        return False

    if not re.search(r'\d', senha):
        return False

    if not re.search(r'[^A-Za-z0-9]', senha):
        return False

    if len(senha) < 6:
        return False

    return True

#ROTA DE CADASTRO DO CLIENTE

@rotas_clientes.route('/cadastro_de_cliente', methods=['POST'])
def cadastro_de_cliente():

    """
    Cadastra um novo cliente.

    ---

    tags:
      - Clientes

    consumes:
      - application/json

    produces:
      - application/json

    parameters:
      - in: body
        name: cliente
        required: true
        schema:
          type: object
          required:
            - primeiro_nome
            - sobrenome
            - cpf
            - email
            - telefone
            - senha
          properties:
            primeiro_nome:
              type: string
              example: Leonardo
              description: Primeiro nome do cliente.

            sobrenome:
              type: string
              example: Santos
              description: Sobrenome do cliente.

            cpf:
              type: string
              example: "529.982.247-25"
              description: CPF do cliente.

            email:
              type: string
              format: email
              example: "leonardo.teste@email.com"
              description: E-mail do cliente.

            telefone:
              type: string
              example: "21999999999"
              description: Telefone do cliente.

            senha:
              type: string
              format: password
              example: "Abc@123"
              description: >
                Senha do cliente. Deve possuir no mínimo 6 caracteres,
                ao menos uma letra maiúscula, uma letra minúscula,
                um número e um caractere especial.

    responses:
      201:
        description: Cliente cadastrado com sucesso.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Cliente cadastrado com sucesso

            numero_do_cliente:
              type: integer
              example: 1

      400:
        description: Dados inválidos ou obrigatórios ausentes.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: CPF inválido.

      409:
        description: CPF ou e-mail já cadastrado.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: CPF já cadastrado

      500:
        description: Erro de banco de dados.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro de Banco de Dados
    """

    dados = request.get_json(silent=True)
    if dados is None:
     return jsonify({
        'erro': 'Dados Faltando ou Nenhum Dado Inserido'
     }), 400

    if not isinstance(dados, dict):
     return jsonify({
        'erro': 'Formato JSON inválido'
     }), 400

    if not dados:
     return jsonify({
        'erro': 'Dados Faltando ou Nenhum Dado Inserido'
     }), 400
    
    campos_obrigatorios = [
        'primeiro_nome',
        'sobrenome',
        'cpf',
        'email',
        'telefone',
        'senha'
    ]

    for campo in campos_obrigatorios:
     if campo not in dados or not dados[campo]:
      return jsonify({
        'erro': f'O campo "{campo}" é obrigatório'
     }), 400

    cpf = dados['cpf']

    if not isinstance(cpf, str):
      return jsonify({
        'erro': 'CPF inválido.'
     }), 400

    cpf = dados['cpf'].replace('.', '').replace('-', '')

    if not validar_cpf(cpf):
     return jsonify({
        'erro': 'CPF inválido.'
     }), 400

    email = dados['email']

    if not isinstance(email, str):
     return jsonify({
        'erro': 'E-mail inválido'
    }), 400

    email = email.strip()
 
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
     return jsonify({
        'erro': 'E-mail inválido'
     }), 400

    telefone = dados['telefone']

    if not isinstance(telefone, str):
     return jsonify({
        'erro': 'Telefone inválido'
     }), 400

    telefone = re.sub(r'\D', '', telefone)

    if not validar_telefone(telefone):
     return jsonify({
        'erro': 'Telefone inválido'
     }), 400

    senha = dados['senha']

    if not isinstance(senha, str):
     return jsonify({
        'erro': 'Senha inválida'
     }), 400

    if not validar_senha(senha):
     return jsonify({
        'erro': 'Senha inválida'
     }), 400
    
    senha_hash = generate_password_hash(senha)    

    banco_de_dados = conexao_backend()

    try:

     tabelas = banco_de_dados.cursor()

     tabelas.execute(
     'SELECT Numero_do_Cliente FROM Clientes WHERE CPF = ?',
     (cpf,))

     cpf_existente = tabelas.fetchone()

     if cpf_existente:
         return jsonify({
           'erro': 'CPF já cadastrado'
         }), 409

     tabelas.execute(
     'SELECT Numero_do_Cliente FROM Clientes WHERE Email_do_Cliente = ?',
     (email,))

     email_existente = tabelas.fetchone()

     if email_existente:
          return jsonify({
            'erro': 'E-mail já cadastrado'
         }), 409

     tabelas.execute('''
        INSERT INTO Clientes (
            Primeiro_Nome_do_Cliente,
            Sobrenome_do_Cliente,
            CPF,
            Email_do_Cliente,
            Telefone_do_cliente,
            Senha_do_Cliente
        )
        VALUES (?, ?, ?, ?, ?, ?)
     ''', (
        dados['primeiro_nome'],
        dados['sobrenome'],
        cpf,
        email,
        telefone,
        senha_hash
     ))

     banco_de_dados.commit()

     numero_do_cliente = tabelas.lastrowid

     return jsonify({
        'mensagem': 'Cliente cadastrado com sucesso',
        'numero_do_cliente': numero_do_cliente
    }), 201

    except sqlite3.Error: 
           banco_de_dados.rollback()
           return jsonify({
              'erro': 'Erro de Banco de Dados'
           }), 500
    
    finally:

     banco_de_dados.close()

# ROTA DE LOGIN DO CLIENTE

@rotas_clientes.route('/login', methods=['POST'])
def login_cliente():

    """
    Realiza o login do cliente.

    ---

    tags:
      - Clientes

    consumes:
      - application/json

    produces:
      - application/json

    parameters:
      - in: body
        name: login
        required: true
        schema:
          type: object
          required:
            - cpf
            - senha
          properties:
            cpf:
              type: string
              example: "529.982.247-25"
              description: CPF do cliente.

            senha:
              type: string
              format: password
              example: "Abc@123"
              description: Senha do cliente.

    responses:
      200:
        description: Login realizado com sucesso.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Login realizado com sucesso

            numero_do_cliente:
              type: integer
              example: 1

            primeiro_nome:
              type: string
              example: Leonardo

      400:
        description: Dados inválidos ou obrigatórios ausentes.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: CPF inválido

      401:
        description: CPF ou senha inválidos.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: CPF ou senha inválidos

      500:
        description: Erro ao realizar login.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao realizar login
    """

    dados = request.get_json(silent=True)

    if dados is None:
        return jsonify({
            'erro': 'Dados Faltando ou Nenhum Dado Inserido'
        }), 400

    if not isinstance(dados, dict):
        return jsonify({
            'erro': 'Formato JSON inválido'
        }), 400

    if not dados:
        return jsonify({
            'erro': 'Dados Faltando ou Nenhum Dado Inserido'
        }), 400

    if 'cpf' not in dados or not dados['cpf']:
        return jsonify({
            'erro': 'O campo "cpf" é obrigatório'
        }), 400

    if 'senha' not in dados or not dados['senha']:
        return jsonify({
            'erro': 'O campo "senha" é obrigatório'
        }), 400

    cpf = dados['cpf']

    if not isinstance(cpf, str):
        return jsonify({
            'erro': 'CPF inválido'
        }), 400

    cpf = cpf.replace('.', '').replace('-', '')

    if not validar_cpf(cpf):
        return jsonify({
            'erro': 'CPF inválido'
        }), 400

    senha = dados['senha']

    if not isinstance(senha, str):
        return jsonify({
            'erro': 'Senha inválida'
        }), 400

    banco_de_dados = conexao_backend()

    try:

        tabelas = banco_de_dados.cursor()

        tabelas.execute('''
            SELECT
                Numero_do_Cliente,
                Primeiro_Nome_do_Cliente,
                Senha_do_Cliente

            FROM Clientes

            WHERE CPF = ?
        ''', (cpf,))

        cliente = tabelas.fetchone()

        if cliente is None:

            return jsonify({
                'erro': 'CPF ou senha inválidos'
            }), 401

        senha_valida = check_password_hash(
            cliente['Senha_do_Cliente'],
            senha
        )

        if not senha_valida:

            return jsonify({
                'erro': 'CPF ou senha inválidos'
            }), 401

        return jsonify({
            'mensagem': 'Login realizado com sucesso',
            'numero_do_cliente': cliente['Numero_do_Cliente'],
            'primeiro_nome': cliente['Primeiro_Nome_do_Cliente']
        }), 200

    except sqlite3.Error:

        return jsonify({
            'erro': 'Erro ao realizar login'
        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA BUSCAR CLIENTES

@rotas_clientes.route('/clientes', methods=['GET'])

def buscar_clientes():
    
    """
    Busca clientes cadastrados.

    ---

    tags:
      - Clientes

    parameters:
      - name: numero_do_cliente
        in: query
        type: integer
        required: false
        description: Número do cliente para realizar a busca.
        example: 1

      - name: primeiro_nome
        in: query
        type: string
        required: false
        description: Primeiro nome do cliente.
        example: Leonardo

      - name: sobrenome
        in: query
        type: string
        required: false
        description: Sobrenome do cliente.
        example: Santos

      - name: cpf
        in: query
        type: string
        required: false
        description: CPF do cliente.
        example: "529.982.247-25"

      - name: email
        in: query
        type: string
        required: false
        description: E-mail do cliente.
        example: "leonardo.teste@email.com"

      - name: telefone
        in: query
        type: string
        required: false
        description: Telefone do cliente.
        example: "21999999999"

    responses:
      200:
        description: Cliente(s) encontrado(s) com sucesso.
        schema:
          type: array
          items:
            type: object
            properties:
              numero_do_cliente:
                type: integer
                example: 1

              primeiro_nome:
                type: string
                example: Leonardo

              sobrenome:
                type: string
                example: Santos

              cpf:
                type: string
                example: "52998224725"

              email:
                type: string
                example: "leonardo.teste@email.com"

              telefone:
                type: string
                example: "21999999999"

      404:
        description: Nenhum cliente encontrado.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Nenhum cliente encontrado

      500:
        description: Erro ao buscar clientes.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao buscar clientes
    """

    numero_do_cliente = request.args.get('numero_do_cliente')

    primeiro_nome = request.args.get('primeiro_nome')

    sobrenome = request.args.get('sobrenome')

    cpf = request.args.get('cpf')

    email = request.args.get('email')

    telefone = request.args.get('telefone')

    if cpf:
      cpf = cpf.replace('.', '').replace('-', '')

    if telefone:
      telefone = re.sub(r'\D', '', telefone)

    banco_de_dados = conexao_backend()

    try:

        tabelas = banco_de_dados.cursor()

        consulta = '''
            SELECT

                Numero_do_Cliente,

                Primeiro_Nome_do_Cliente,

                Sobrenome_do_Cliente,

                CPF,

                Email_do_Cliente,

                Telefone_do_cliente

            FROM Clientes
        '''

        valores = []

        filtros = []

        if numero_do_cliente:

            filtros.append('Numero_do_Cliente = ?')

            valores.append(numero_do_cliente)

        if primeiro_nome:

            filtros.append('Primeiro_Nome_do_Cliente = ?')

            valores.append(primeiro_nome)

        if sobrenome:

            filtros.append('Sobrenome_do_Cliente = ?')

            valores.append(sobrenome)

        if cpf:

            filtros.append('CPF = ?')

            valores.append(cpf)

        if email:

            filtros.append('Email_do_Cliente = ?')

            valores.append(email)

        if telefone:

            filtros.append('Telefone_do_cliente = ?')

            valores.append(telefone)

        if filtros:

            consulta += ' WHERE ' + ' AND '.join(filtros)

        tabelas.execute(consulta, valores)

        clientes = tabelas.fetchall()

        if not clientes:

            return jsonify({

                'erro': 'Nenhum cliente encontrado'

            }), 404

        lista_clientes = []

        for cliente in clientes:

            lista_clientes.append({

                'numero_do_cliente': cliente['Numero_do_Cliente'],

                'primeiro_nome': cliente['Primeiro_Nome_do_Cliente'],

                'sobrenome': cliente['Sobrenome_do_Cliente'],

                'cpf': cliente['CPF'],

                'email': cliente['Email_do_Cliente'],

                'telefone': cliente['Telefone_do_cliente']

            })

        return jsonify(lista_clientes), 200

    except sqlite3.Error:

        return jsonify({

            'erro': 'Erro ao buscar clientes'

        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA ALTERAR SENHA DO CLIENTE

@rotas_clientes.route('/clientes/<int:numero_do_cliente>/senha', methods=['PUT'])
def alterar_senha(numero_do_cliente):

    """
    Altera a senha de um cliente.

    ---

    tags:
      - Clientes

    consumes:
      - application/json

    produces:
      - application/json

    parameters:
      - name: numero_do_cliente
        in: path
        type: integer
        required: true
        description: Número do cliente.
        example: 1

      - in: body
        name: senha
        required: true
        schema:
          type: object
          required:
            - senha_atual
            - nova_senha
          properties:
            senha_atual:
              type: string
              format: password
              example: "Abc@123"
              description: Senha atual do cliente.

            nova_senha:
              type: string
              format: password
              example: "Nova@456"
              description: >
                Nova senha. Deve possuir no mínimo 6 caracteres,
                ao menos uma letra maiúscula, uma letra minúscula,
                um número e um caractere especial.

    responses:
      200:
        description: Senha alterada com sucesso.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Senha alterada com sucesso

            numero_do_cliente:
              type: integer
              example: 1

      400:
        description: Dados inválidos.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Senha inválida

      401:
        description: Senha atual incorreta.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Senha atual incorreta

      404:
        description: Cliente não encontrado.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Cliente não encontrado

      500:
        description: Erro ao alterar senha.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao alterar senha
    """

    if numero_do_cliente <= 0:
        return jsonify({
            'erro': 'Número do cliente inválido'
        }), 400

    dados = request.get_json(silent=True)

    if dados is None:
        return jsonify({
            'erro': 'Nenhum dado inserido'
        }), 400

    if not isinstance(dados, dict):
        return jsonify({
            'erro': 'Formato JSON inválido'
        }), 400

    if not dados:
        return jsonify({
            'erro': 'Nenhum dado inserido'
        }), 400

    if 'senha_atual' not in dados or not dados['senha_atual']:
        return jsonify({
            'erro': 'O campo "senha_atual" é obrigatório'
        }), 400

    if 'nova_senha' not in dados or not dados['nova_senha']:
        return jsonify({
            'erro': 'O campo "nova_senha" é obrigatório'
        }), 400

    senha_atual = dados['senha_atual']
    nova_senha = dados['nova_senha']

    if not isinstance(senha_atual, str):
        return jsonify({
            'erro': 'Senha atual inválida'
        }), 400

    if not isinstance(nova_senha, str):
        return jsonify({
            'erro': 'Nova senha inválida'
        }), 400

    if not validar_senha(nova_senha):
        return jsonify({
            'erro': 'Nova senha inválida. A senha deve possuir: '
            'no mínimo 6 caracteres, '
            'ao menos uma letra maiúscula, '
            'pelo menos uma letra minúscula, '
            'no mínimo um número, '
            'ao menos um caractere especial'
        }), 400

    if senha_atual == nova_senha:
        return jsonify({
            'erro': 'A nova senha deve ser diferente da senha atual'
        }), 400

    banco_de_dados = conexao_backend()

    try:

        tabelas = banco_de_dados.cursor()

        tabelas.execute('''
            SELECT
                Numero_do_Cliente,
                Senha_do_Cliente
            FROM Clientes
            WHERE Numero_do_Cliente = ?
        ''', (numero_do_cliente,))

        cliente = tabelas.fetchone()

        if cliente is None:
            return jsonify({
                'erro': 'Cliente não encontrado'
            }), 404

        senha_atual_valida = check_password_hash(
            cliente['Senha_do_Cliente'],
            senha_atual
        )

        if not senha_atual_valida:
            return jsonify({
                'erro': 'Senha atual incorreta'
            }), 401

        nova_senha_hash = generate_password_hash(nova_senha)

        tabelas.execute('''
            UPDATE Clientes
            SET Senha_do_Cliente = ?
            WHERE Numero_do_Cliente = ?
        ''', (
            nova_senha_hash,
            numero_do_cliente
        ))

        banco_de_dados.commit()

        return jsonify({
            'mensagem': 'Senha alterada com sucesso',
            'numero_do_cliente': numero_do_cliente
        }), 200

    except sqlite3.Error:

        banco_de_dados.rollback()

        return jsonify({
            'erro': 'Erro ao alterar senha'
        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA ATUALIZAR DADOS DO CLIENTE

@rotas_clientes.route('/clientes/<tipo_busca>/<valor_busca>', methods=['PUT'])

def atualizar_cliente(tipo_busca, valor_busca):

    """
    Atualiza os dados permitidos de um cliente.

    ---

    tags:
      - Clientes

    consumes:
      - application/json

    produces:
      - application/json

    parameters:
      - name: tipo_busca
        in: path
        type: string
        required: true
        description: Tipo de dado utilizado para localizar o cliente.
        enum:
          - numero
          - cpf
          - email
        example: numero

      - name: valor_busca
        in: path
        type: string
        required: true
        description: Valor correspondente ao tipo de busca utilizado.
        example: "1"

      - in: body
        name: cliente
        required: true
        schema:
          type: object
          properties:
            sobrenome:
              type: string
              example: Santos
              description: Novo sobrenome do cliente.

            email:
              type: string
              format: email
              example: "novo.email@email.com"
              description: Novo e-mail do cliente.

            telefone:
              type: string
              example: "21988888888"
              description: Novo telefone do cliente.

    responses:
      200:
        description: Dados do cliente atualizados com sucesso.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Dados do cliente atualizados com sucesso

            numero_do_cliente:
              type: integer
              example: 1

      400:
        description: Dados inválidos ou campo não permitido.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: E-mail inválido

            campos_permitidos:
              type: array
              items:
                type: string
              example:
                - sobrenome
                - email
                - telefone

      404:
        description: Cliente não encontrado.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Cliente não encontrado

      409:
        description: E-mail informado já cadastrado para outro cliente.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: O email informado já está cadastrado para outro cliente

      500:
        description: Erro ao atualizar os dados do cliente.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao atualizar dados do cliente
    """

    dados = request.get_json(silent=True)

    if dados is None:
        return jsonify({
            'erro': 'Nenhum dado inserido'
        }), 400

    if not isinstance(dados, dict):
        return jsonify({
            'erro': 'Formato JSON inválido'
        }), 400

    if not dados:
        return jsonify({
            'erro': 'Nenhum dado inserido'
        }), 400

    campos_permitidos_para_alteracao = {
        'sobrenome',
        'email',
        'telefone'
    }

    dados_invalidos = set(dados.keys()) - campos_permitidos_para_alteracao

    if dados_invalidos:
        return jsonify({
            'erro': 'Dado(s) não permitido(s) para alteração',
            'campos_permitidos': list(campos_permitidos_para_alteracao)
        }), 400

    campos_para_alterar = [
       campo
       for campo in dados.keys()
       if campo in campos_permitidos_para_alteracao
     ]

    if not campos_para_alterar:
        return jsonify({
            'erro': 'Nenhum dado foi informado',
            'campos_permitidos': list(campos_permitidos_para_alteracao)
        }), 400

    if tipo_busca not in ('numero', 'cpf', 'email'):
        return jsonify({
            'erro': 'Tipo de busca inválido. Utilize numero, cpf ou email'
        }), 400

    if tipo_busca == 'numero':

        try:
            numero_cliente = int(valor_busca)

        except ValueError:
            return jsonify({
                'erro': 'Número do cliente inválido'
            }), 400

        if numero_cliente <= 0:
            return jsonify({
                'erro': 'Número do cliente inválido'
            }), 400

    elif tipo_busca == 'cpf':

        cpf = valor_busca.replace('.', '').replace('-', '')

        if not validar_cpf(cpf):
            return jsonify({
                'erro': 'CPF inválido'
            }), 400


    elif tipo_busca == 'email':

        if not re.fullmatch(
            r'[^@\s]+@[^@\s]+\.[^@\s]+',
            valor_busca
        ):
            return jsonify({
                'erro': 'E-mail inválido'
            }), 400

    banco_de_dados = conexao_backend()

    try:

        tabelas = banco_de_dados.cursor()

        if tipo_busca == 'numero':

            tabelas.execute('''
                SELECT Numero_do_Cliente
                FROM Clientes
                WHERE Numero_do_Cliente = ?
            ''', (numero_cliente,))

        elif tipo_busca == 'cpf':

            tabelas.execute('''
                SELECT Numero_do_Cliente
                FROM Clientes
                WHERE CPF = ?
            ''', (cpf,))

        elif tipo_busca == 'email':

            tabelas.execute('''
                SELECT Numero_do_Cliente
                FROM Clientes
                WHERE Email_do_Cliente = ?
            ''', (valor_busca,))

        cliente = tabelas.fetchone()

        if cliente is None:
            return jsonify({
                'erro': 'Cliente não encontrado'
            }), 404

        numero_cliente = cliente[0]

        if 'sobrenome' in campos_para_alterar:

            sobrenome = dados['sobrenome']

            if not isinstance(sobrenome, str):
                return jsonify({
                    'erro': 'Sobrenome inválido'
                }), 400

            sobrenome = sobrenome.strip()

            if not sobrenome:
                return jsonify({
                    'erro': 'Sobrenome não pode ficar vazio'
                }), 400

            if not re.fullmatch(
                r'[A-Za-zÀ-ÖØ-öø-ÿ\s]+',
                sobrenome
            ):
                return jsonify({
                    'erro': 'Sobrenome deve conter apenas letras'
                }), 400

            dados['sobrenome'] = sobrenome

        if 'email' in campos_para_alterar:

            email = dados['email']

            if not isinstance(email, str):
                return jsonify({
                    'erro': 'E-mail inválido'
                }), 400

            email = email.strip()

            if not email:
                return jsonify({
                    'erro': 'E-mail não pode ficar vazio'
                }), 400

            if not re.fullmatch(
                r'[^@\s]+@[^@\s]+\.[^@\s]+',
                email
            ):
                return jsonify({
                    'erro': 'E-mail inválido'
                }), 400

            dados['email'] = email

            tabelas.execute('''
                SELECT Numero_do_Cliente
                FROM Clientes
                WHERE Email_do_Cliente = ?
                AND Numero_do_Cliente != ?
            ''', (email, numero_cliente))

            email_existente = tabelas.fetchone()

            if email_existente is not None:
                return jsonify({
                    'erro': 'O email informado já está cadastrado para outro cliente'
                }), 409

        if 'telefone' in campos_para_alterar:

            telefone = dados['telefone']

            if not isinstance(telefone, str):
                return jsonify({
                    'erro': 'Telefone inválido'
                }), 400

            telefone = telefone.strip()

            if not telefone:
                return jsonify({
                    'erro': 'Telefone não pode ficar vazio'
                }), 400

            telefone = re.sub(r'\D', '', telefone)

            if not validar_telefone(telefone):
                return jsonify({
                    'erro': 'Telefone inválido'
                }), 400

            dados['telefone'] = telefone

        dado_update = []
        dado_inserido_update = []


        for campo in campos_para_alterar:

            if campo == 'email':

                dado_update.append(
                    'Email_do_Cliente = ?'
                )

            elif campo == 'sobrenome':

                dado_update.append(
                    'Sobrenome_do_Cliente = ?'
                )

            elif campo == 'telefone':

                dado_update.append(
                    'Telefone_do_cliente = ?'
                )

            dado_inserido_update.append(
                dados[campo]
            )

        dado_inserido_update.append(numero_cliente)

        consulta_update = f'''
            UPDATE Clientes
            SET {', '.join(dado_update)}
            WHERE Numero_do_Cliente = ?
        '''

        tabelas.execute(
            consulta_update,
            dado_inserido_update
        )

        banco_de_dados.commit()

        return jsonify({
            'mensagem': 'Dados do cliente atualizados com sucesso',
            'numero_do_cliente': numero_cliente
        }), 200

    except sqlite3.Error:

        banco_de_dados.rollback()

        return jsonify({
            'erro': 'Erro ao atualizar dados do cliente'
        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA EXCLUIR CLIENTE

@rotas_clientes.route('/clientes/<tipo_busca>/<valor_busca>', methods=['DELETE'])
def excluir_cliente(tipo_busca, valor_busca):
    """
    Exclui um cliente cadastrado.

    ---

    tags:
      - Clientes

    produces:
      - application/json

    parameters:
      - name: tipo_busca
        in: path
        type: string
        required: true
        description: Tipo de dado utilizado para localizar o cliente.
        enum:
          - numero
          - cpf
          - email
        example: numero

      - name: valor_busca
        in: path
        type: string
        required: true
        description: Valor correspondente ao tipo de busca utilizado.
        example: "1"

    responses:
      200:
        description: Cliente excluído com sucesso.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Cliente excluído com sucesso

            numero_do_cliente:
              type: integer
              example: 1

      400:
        description: Tipo de busca, número, CPF ou e-mail inválido.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Tipo de busca inválido. Utilize numero, cpf ou email

      404:
        description: Cliente não encontrado.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Cliente não encontrado

      409:
        description: Cliente não pode ser excluído porque possui registros relacionados.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Não é possível excluir o cliente porque existem reservas relacionadas a ele

      500:
        description: Erro ao excluir cliente.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao excluir cliente
    """

    if tipo_busca not in ('numero', 'cpf', 'email'):
        return jsonify({
            'erro': 'Tipo de busca inválido. Utilize numero, cpf ou email'
        }), 400

    if tipo_busca == 'numero':
        try:
            numero_cliente = int(valor_busca)
        except ValueError:
            return jsonify({
                'erro': 'Número do cliente inválido'
            }), 400

        if numero_cliente <= 0:
            return jsonify({
                'erro': 'Número do cliente inválido'
            }), 400

    elif tipo_busca == 'cpf':
        cpf = valor_busca.replace('.', '').replace('-', '')

        if not validar_cpf(cpf):
            return jsonify({
                'erro': 'CPF inválido'
            }), 400

    elif tipo_busca == 'email':
        email = valor_busca.strip()

        if not re.fullmatch(
            r'[^@\s]+@[^@\s]+\.[^@\s]+',
            email
        ):
            return jsonify({
                'erro': 'E-mail inválido'
            }), 400

    banco_de_dados = conexao_backend()

    try:
        tabelas = banco_de_dados.cursor()

        if tipo_busca == 'numero':
            tabelas.execute('''
                SELECT Numero_do_Cliente
                FROM Clientes
                WHERE Numero_do_Cliente = ?
            ''', (numero_cliente,))

        elif tipo_busca == 'cpf':
            tabelas.execute('''
                SELECT Numero_do_Cliente
                FROM Clientes
                WHERE CPF = ?
            ''', (cpf,))

        elif tipo_busca == 'email':
            tabelas.execute('''
                SELECT Numero_do_Cliente
                FROM Clientes
                WHERE Email_do_Cliente = ?
            ''', (email,))

        cliente = tabelas.fetchone()

        if cliente is None:
            return jsonify({
                'erro': 'Cliente não encontrado'
            }), 404

        numero_cliente = cliente[0]

        tabelas.execute('''
            DELETE FROM Clientes
            WHERE Numero_do_Cliente = ?
        ''', (numero_cliente,))

        banco_de_dados.commit()

        return jsonify({
            'mensagem': 'Cliente excluído com sucesso',
            'numero_do_cliente': numero_cliente
        }), 200

    except sqlite3.IntegrityError:
       banco_de_dados.rollback()
       return jsonify({
          'erro': 'Não é possível excluir o cliente porque existem reservas relacionadas a ele'
        }), 409


    except sqlite3.Error:
       banco_de_dados.rollback()
       return jsonify({
          'erro': 'Erro ao excluir cliente'
        }), 500

    finally:
        banco_de_dados.close()