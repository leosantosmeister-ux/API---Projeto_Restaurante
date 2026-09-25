import sqlite3

from flask import Blueprint, request, jsonify

from datetime import datetime, timedelta

from Projeto_Restaurante_Banco_de_Dados import conexao_backend


rotas_reservas = Blueprint('rotas_reservas', __name__)

# ROTA PARA CRIAR RESERVAS

@rotas_reservas.route('/reservas', methods=['POST'])
def cadastrar_reserva():

    """
    Cria uma nova reserva para um cliente.

    ---
    tags:
      - Reservas

    parameters:
      - name: body
        in: body
        required: true
        description: Dados necessários para criar uma reserva.
        schema:
          type: object
          required:
            - numero_do_cliente
            - quantidade_de_pessoas_na_mesa
            - numero_da_mesa
            - data_da_reserva
            - horario_da_reserva
            - duracao_da_reserva
          properties:
            numero_do_cliente:
              type: integer
              description: Número do cliente que realizará a reserva.
              example: 1
            quantidade_de_pessoas_na_mesa:
              type: integer
              description: Quantidade de pessoas que ocuparão a mesa.
              example: 2
            numero_da_mesa:
              type: integer
              description: Número da mesa desejada.
              example: 5
            data_da_reserva:
              type: string
              description: Data da reserva no formato DD-MM-AAAA.
              example: "20-09-2026"
            horario_da_reserva:
              type: string
              description: Horário de início da reserva no formato HH:MM.
              example: "19:00"
            duracao_da_reserva:
              type: integer
              description: Duração da reserva em minutos. O mínimo é 60 minutos.
              example: 120

    responses:
      201:
        description: Reserva criada com sucesso.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Reserva criada com sucesso
            reserva:
              type: object
              properties:
                numero_da_reserva:
                  type: integer
                  example: 1
                numero_do_cliente:
                  type: integer
                  example: 1
                quantidade_de_pessoas_na_mesa:
                  type: integer
                  example: 2
                numero_da_mesa:
                  type: integer
                  example: 5
                capacidade_da_mesa_na_reserva:
                  type: integer
                  example: 4
                data_da_reserva:
                  type: string
                  example: "20-09-2026"
                horario_da_reserva:
                  type: string
                  example: "19:00"
                data_de_termino_da_reserva:
                  type: string
                  example: "20-09-2026"
                horario_de_termino_da_reserva:
                  type: string
                  example: "21:00"
                duracao_da_reserva:
                  type: integer
                  example: 120
                status_da_reserva:
                  type: string
                  example: PENDENTE

      400:
        description: Dados inválidos, horário inválido, duração inválida, antecedência insuficiente ou regras da reserva não atendidas.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: A duração mínima da reserva é de 60 minutos
            capacidade_da_mesa:
              type: integer
              example: 4
            quantidade_de_pessoas:
              type: integer
              example: 6

      404:
        description: Cliente ou mesa não encontrada.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Cliente não encontrado

      409:
        description: A mesa já possui uma reserva no período informado.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: A mesa já possui uma reserva nesse período
            numero_da_reserva_conflitante:
              type: integer
              example: 3
    """

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):

        return jsonify({
            "erro": "Formato JSON inválido"
        }), 400

    campos_permitidos = {
        "numero_do_cliente",
        "quantidade_de_pessoas_na_mesa",
        "numero_da_mesa",
        "data_da_reserva",
        "horario_da_reserva",
        "duracao_da_reserva"
    }

    campos_recebidos = set(dados.keys())

    campos_invalidos = campos_recebidos - campos_permitidos

    if campos_invalidos:

        return jsonify({
            "erro": "Foram enviados dados inválidos",
            "dados_validos": list(campos_permitidos)
        }), 400

    campos_obrigatorios = [
        "numero_do_cliente",
        "quantidade_de_pessoas_na_mesa",
        "numero_da_mesa",
        "data_da_reserva",
        "horario_da_reserva",
        "duracao_da_reserva"
    ]

    campos_faltantes = [
        campo
        for campo in campos_obrigatorios
        if campo not in dados
    ]

    if campos_faltantes:

        return jsonify({
            "erro": "Dados obrigatórios não informados",
            "dados_faltantes": campos_faltantes
        }), 400

    numero_do_cliente = dados["numero_do_cliente"]

    quantidade_de_pessoas = dados["quantidade_de_pessoas_na_mesa"]

    numero_da_mesa = dados["numero_da_mesa"]

    data_da_reserva = dados["data_da_reserva"]

    horario_da_reserva = dados["horario_da_reserva"]

    duracao_da_reserva = dados["duracao_da_reserva"]

    if isinstance(numero_do_cliente, bool):

        return jsonify({
            "erro": "Número do cliente inválido"
        }), 400

    try:

        numero_do_cliente_convertido = int(numero_do_cliente)

        if float(numero_do_cliente_convertido) != float(
            numero_do_cliente
        ):

            return jsonify({
                "erro": "Número do cliente inválido"
            }), 400

        numero_do_cliente = numero_do_cliente_convertido

    except (TypeError, ValueError):

        return jsonify({
            "erro": "Número do cliente inválido"
        }), 400

    if numero_do_cliente <= 0:

        return jsonify({
            "erro": "O número do cliente deve ser maior que zero"
        }), 400

    if isinstance(quantidade_de_pessoas, bool):

        return jsonify({
            "erro": "Quantidade de pessoas inválida"
        }), 400

    try:

        quantidade_convertida = int(quantidade_de_pessoas)

        if float(quantidade_convertida) != float(
            quantidade_de_pessoas
        ):

            return jsonify({
                "erro": "Quantidade de pessoas inválida"
            }), 400

        quantidade_de_pessoas = quantidade_convertida

    except (TypeError, ValueError):

        return jsonify({
            "erro": "Quantidade de pessoas inválida"
        }), 400

    if quantidade_de_pessoas <= 0:

        return jsonify({
            "erro": "A quantidade de pessoas deve ser maior que zero"
        }), 400


    if isinstance(numero_da_mesa, bool):

        return jsonify({
            "erro": "Número da mesa inválido"
        }), 400

    try:

        numero_da_mesa_convertido = int(numero_da_mesa)

        if float(numero_da_mesa_convertido) != float(
            numero_da_mesa
        ):

            return jsonify({
                "erro": "Número da mesa inválido"
            }), 400

        numero_da_mesa = numero_da_mesa_convertido

    except (TypeError, ValueError):

        return jsonify({
            "erro": "Número da mesa inválido"
        }), 400

    if numero_da_mesa <= 0:

        return jsonify({
            "erro": "O número da mesa deve ser maior que zero"
        }), 400

    try:

        data_convertida = datetime.strptime(
            data_da_reserva,
            "%d-%m-%Y"
        ).date()

    except (TypeError, ValueError):

        return jsonify({
            "erro": "Data da reserva inválida. Use o formato DD-MM-AAAA"
        }), 400

    if data_convertida.strftime(
        "%d-%m-%Y"
    ) != data_da_reserva:

        return jsonify({
            "erro": "Data da reserva inválida. Use o formato DD-MM-AAAA"
        }), 400


    try:

        horario_convertido = datetime.strptime(
            horario_da_reserva,
            "%H:%M"
        ).time()

    except (TypeError, ValueError):

        return jsonify({
            "erro": "Horário da reserva inválido. Use o formato HH:MM"
        }), 400


    if horario_convertido.strftime(
        "%H:%M"
    ) != horario_da_reserva:

        return jsonify({
            "erro": "Horário da reserva inválido. Use o formato HH:MM"
        }), 400


    if isinstance(duracao_da_reserva, bool):

        return jsonify({
            "erro": "Duração da reserva inválida"
        }), 400

    try:

        duracao_convertida = int(duracao_da_reserva)

        if float(duracao_convertida) != float(
            duracao_da_reserva
        ):

            return jsonify({
                "erro": "Duração da reserva inválida"
            }), 400

        duracao_da_reserva = duracao_convertida

    except (TypeError, ValueError):

        return jsonify({
            "erro": "Duração da reserva inválida"
        }), 400

    if duracao_da_reserva < 60:

        return jsonify({
            "erro": "A duração mínima da reserva é de 60 minutos"
        }), 400

    if duracao_da_reserva > 840:

         return jsonify({
            "erro": "A duração máxima da reserva é de 14 horas"
        }), 400

    data_hora_inicio = datetime.combine(
        data_convertida,
        horario_convertido
    )

    data_hora_termino = (
        data_hora_inicio
        + timedelta(minutes=duracao_da_reserva)
    )

    abertura = datetime.combine(
        data_convertida,
        datetime.strptime(
            "10:00",
            "%H:%M"
        ).time()
    )

    fechamento = datetime.combine(
        data_convertida + timedelta(days=1),
        datetime.strptime(
            "00:00",
            "%H:%M"
        ).time()
    )

    if data_hora_inicio < abertura:

        return jsonify({
            "erro": "A reserva deve começar a partir das 10:00"
        }), 400

    if data_hora_termino > fechamento:

        return jsonify({
            "erro": "A reserva deve terminar até 00:00"
        }), 400

    agora = datetime.now()

    antecedencia = data_hora_inicio - agora

    if antecedencia < timedelta(hours=1):

        return jsonify({
            "erro": "A reserva deve ser realizada com pelo menos 1 hora de antecedência"
        }), 400

    banco_de_dados = conexao_backend()

    try:

        cliente = banco_de_dados.execute(
            '''
            SELECT Numero_do_Cliente
            FROM Clientes
            WHERE Numero_do_Cliente = ?
            ''',
            (numero_do_cliente,)
        ).fetchone()

        if cliente is None:

            return jsonify({
                "erro": "Cliente não encontrado"
            }), 404

        mesa = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Mesa,
                Capacidade_da_Mesa
            FROM Mesa
            WHERE Numero_da_Mesa = ?
            ''',
            (numero_da_mesa,)
        ).fetchone()

        if mesa is None:

            return jsonify({
                "erro": "Mesa não encontrada"
            }), 404


        capacidade_da_mesa = mesa["Capacidade_da_Mesa"]

        if quantidade_de_pessoas <= 2:

         capacidade_necessaria = 2

        elif quantidade_de_pessoas <= 4:

         capacidade_necessaria = 4

        elif quantidade_de_pessoas <= 6:

         capacidade_necessaria = 6

        elif quantidade_de_pessoas <= 8:

         capacidade_necessaria = 8

        else:

         capacidade_necessaria = 10

        if capacidade_da_mesa != capacidade_necessaria:

          return jsonify({
             "erro": "A capacidade da mesa não corresponde à quantidade de pessoas",
             "quantidade_de_pessoas": quantidade_de_pessoas,
             "capacidade_necessaria": capacidade_necessaria,
             "capacidade_da_mesa": capacidade_da_mesa
            }), 400

        reserva_conflitante = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Reserva,
                Data_da_Reserva,
                Horario_da_Reserva,
                Data_de_Termino_da_Reserva,
                Horario_de_Termino_da_Reserva

            FROM Reservas

            WHERE Numero_da_Mesa = ?

              AND Status_da_Reserva != 'CANCELADA'

              AND (
                    Data_da_Reserva
                    || ' '
                    || Horario_da_Reserva
                  ) < ?

              AND (
                    Data_de_Termino_da_Reserva
                    || ' '
                    || Horario_de_Termino_da_Reserva
                  ) > ?
            ''',
            (
                numero_da_mesa,

                data_hora_termino.strftime(
                    "%Y-%m-%d %H:%M"
                ),

                data_hora_inicio.strftime(
                    "%Y-%m-%d %H:%M"
                )
            )
        ).fetchone()

        if reserva_conflitante is not None:

            return jsonify({
                "erro": "A mesa já possui uma reserva nesse período",
                "numero_da_reserva_conflitante":
                    reserva_conflitante["Numero_da_Reserva"]
            }), 409

        data_reserva_banco = (
            data_hora_inicio.strftime("%Y-%m-%d")
        )

        horario_reserva_banco = (
            data_hora_inicio.strftime("%H:%M")
        )

        data_termino_banco = (
            data_hora_termino.strftime("%Y-%m-%d")
        )

        horario_termino_banco = (
            data_hora_termino.strftime("%H:%M")
        )

        data_hora_agendamento = datetime.now()

        data_do_agendamento = (
            data_hora_agendamento.strftime("%Y-%m-%d")
        )

        horario_do_agendamento = (
            data_hora_agendamento.strftime("%H:%M:%S")
        )

        status_da_reserva = "PENDENTE"

        cursor = banco_de_dados.execute(
            '''
            INSERT INTO Reservas (
                Data_do_Agendamento,
                Horario_do_Agendamento,
                Numero_do_Cliente,
                Quantidade_de_Pessoas_na_Mesa,
                Numero_da_Mesa,
                Capacidade_da_Mesa_na_Reserva,
                Data_da_Reserva,
                Horario_da_Reserva,
                Data_de_Termino_da_Reserva,
                Horario_de_Termino_da_Reserva,
                Duracao_da_Reserva,
                Status_da_Reserva
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                data_do_agendamento,
                horario_do_agendamento,
                numero_do_cliente,
                quantidade_de_pessoas,
                numero_da_mesa,
                capacidade_da_mesa,
                data_reserva_banco,
                horario_reserva_banco,
                data_termino_banco,
                horario_termino_banco,
                duracao_da_reserva,
                status_da_reserva
            )
        )

        numero_da_reserva = cursor.lastrowid

        banco_de_dados.commit()

        return jsonify({

            "mensagem": "Reserva criada com sucesso",

            "reserva": {

                "numero_da_reserva":
                    numero_da_reserva,

                "numero_do_cliente":
                    numero_do_cliente,

                "quantidade_de_pessoas_na_mesa":
                    quantidade_de_pessoas,

                "numero_da_mesa":
                    numero_da_mesa,

                "capacidade_da_mesa_na_reserva":
                    capacidade_da_mesa,

                "data_da_reserva":
                    data_hora_inicio.strftime("%d-%m-%Y"),

                "horario_da_reserva":
                    data_hora_inicio.strftime("%H:%M"),

                "data_de_termino_da_reserva":
                    data_hora_termino.strftime("%d-%m-%Y"),

                "horario_de_termino_da_reserva":
                    data_hora_termino.strftime("%H:%M"),

                "duracao_da_reserva":
                    duracao_da_reserva,

                "status_da_reserva":
                    status_da_reserva
            }

        }), 201

    
    except sqlite3.Error as erro:
        banco_de_dados.rollback()
        return jsonify({
            "erro": "Erro ao cadastrar reserva",
            "detalhes": str(erro)
        }), 500

    finally:

        banco_de_dados.close()


# ROTA PARA CONSULTAR RESERVAS

@rotas_reservas.route('/reservas', methods=['GET'])
def consultar_reservas():

    """
    Consulta reservas cadastradas.

    Permite realizar a pesquisa utilizando um ou mais parâmetros de filtro.

    ---
    tags:
      - Reservas

    parameters:
      - name: numero_da_reserva
        in: query
        type: integer
        required: false
        description: Número da reserva.
        example: 1

      - name: numero_do_cliente
        in: query
        type: integer
        required: false
        description: Número do cliente associado à reserva.
        example: 1

      - name: numero_da_mesa
        in: query
        type: integer
        required: false
        description: Número da mesa utilizada na reserva.
        example: 5

      - name: data_da_reserva
        in: query
        type: string
        required: false
        description: Data da reserva no formato DD-MM-AAAA.
        example: "20-09-2026"

      - name: status_da_reserva
        in: query
        type: string
        required: false
        description: Status atual da reserva.
        enum:
          - PENDENTE
          - CONFIRMADA
          - CANCELADA
          - CONCLUIDA
        example: PENDENTE

    responses:
      200:
        description: Reservas encontradas com sucesso.
        schema:
          type: array
          items:
            type: object
            properties:
              numero_da_reserva:
                type: integer
                example: 1
              data_do_agendamento:
                type: string
                example: "13-09-2026"
              horario_do_agendamento:
                type: string
                example: "18:30:00"
              numero_do_cliente:
                type: integer
                example: 1
              quantidade_de_pessoas_na_mesa:
                type: integer
                example: 2
              numero_da_mesa:
                type: integer
                example: 5
              capacidade_da_mesa_na_reserva:
                type: integer
                example: 4
              data_da_reserva:
                type: string
                example: "20-09-2026"
              horario_da_reserva:
                type: string
                example: "19:00"
              data_de_termino_da_reserva:
                type: string
                example: "20-09-2026"
              horario_de_termino_da_reserva:
                type: string
                example: "21:00"
              duracao_da_reserva:
                type: integer
                example: 120
              status_da_reserva:
                type: string
                example: PENDENTE

      400:
        description: Parâmetro de pesquisa inválido.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Data da reserva inválida. Use o formato DD-MM-AAAA
            parametros_invalidos:
              type: array
              items:
                type: string
              example:
                - parametro_invalido
            parametros_validos:
              type: array
              items:
                type: string
              example:
                - numero_da_reserva
                - numero_do_cliente
                - numero_da_mesa
                - data_da_reserva
                - status_da_reserva

      404:
        description: Nenhuma reserva encontrada.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Nenhuma reserva encontrada

      500:
        description: Erro interno ao consultar reservas.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao consultar reservas
            detalhes:
              type: string
              example: Erro interno no banco de dados
    """

    parametros_permitidos = {
        "numero_da_reserva",
        "numero_do_cliente",
        "numero_da_mesa",
        "data_da_reserva",
        "status_da_reserva"
    }

    parametros_recebidos = set(request.args.keys())

    parametros_invalidos = (
        parametros_recebidos - parametros_permitidos
    )

    if parametros_invalidos:

        return jsonify({

            "erro": "Parâmetro(s) de pesquisa inválido(s)",

            "parametros_invalidos":
                list(parametros_invalidos),

            "parametros_validos":
                list(parametros_permitidos)

        }), 400


    numero_da_reserva = request.args.get(
        "numero_da_reserva"
    )

    numero_do_cliente = request.args.get(
        "numero_do_cliente"
    )

    numero_da_mesa = request.args.get(
        "numero_da_mesa"
    )

    data_da_reserva = request.args.get(
        "data_da_reserva"
    )

    status_da_reserva = request.args.get(
        "status_da_reserva"
    )


    filtros = []

    valores = []

    if numero_da_reserva is not None:

        if not numero_da_reserva:

            return jsonify({
                "erro": "Informe o número da reserva"
            }), 400

        try:

            numero_da_reserva_convertido = int(
                numero_da_reserva
            )

            if str(numero_da_reserva_convertido) != (
                numero_da_reserva
            ):

                return jsonify({
                    "erro": "Número da reserva inválido"
                }), 400

        except ValueError:

            return jsonify({
                "erro": "Número da reserva inválido"
            }), 400


        if numero_da_reserva_convertido <= 0:

            return jsonify({
                "erro": "O número da reserva deve ser maior que zero"
            }), 400


        filtros.append(
            "Numero_da_Reserva = ?"
        )

        valores.append(
            numero_da_reserva_convertido
        )

    if numero_do_cliente is not None:

        if not numero_do_cliente:

            return jsonify({
                "erro": "Informe o número do cliente"
            }), 400

        try:

            numero_do_cliente_convertido = int(
                numero_do_cliente
            )

            if str(numero_do_cliente_convertido) != (
                numero_do_cliente
            ):

                return jsonify({
                    "erro": "Número do cliente inválido"
                }), 400

        except ValueError:

            return jsonify({
                "erro": "Número do cliente inválido"
            }), 400


        if numero_do_cliente_convertido <= 0:

            return jsonify({
                "erro": "O número do cliente deve ser maior que zero"
            }), 400


        filtros.append(
            "Numero_do_Cliente = ?"
        )

        valores.append(
            numero_do_cliente_convertido
        )

    if numero_da_mesa is not None:

        if not numero_da_mesa:

            return jsonify({
                "erro": "Informe o número da mesa"
            }), 400

        try:

            numero_da_mesa_convertido = int(
                numero_da_mesa
            )

            if str(numero_da_mesa_convertido) != (
                numero_da_mesa
            ):

                return jsonify({
                    "erro": "Número da mesa inválido"
                }), 400

        except ValueError:

            return jsonify({
                "erro": "Número da mesa inválido"
            }), 400


        if numero_da_mesa_convertido <= 0:

            return jsonify({
                "erro": "O número da mesa deve ser maior que zero"
            }), 400


        filtros.append(
            "Numero_da_Mesa = ?"
        )

        valores.append(
            numero_da_mesa_convertido
        )

    if data_da_reserva is not None:

        if not data_da_reserva:

            return jsonify({
                "erro": "Informe a data da reserva"
            }), 400


        try:

            data_convertida = datetime.strptime(
                data_da_reserva,
                "%d-%m-%Y"
            ).date()

        except (TypeError, ValueError):

            return jsonify({
                "erro": "Data da reserva inválida. Use o formato DD-MM-AAAA"
            }), 400


        if data_convertida.strftime(
            "%d-%m-%Y"
        ) != data_da_reserva:

            return jsonify({
                "erro": "Data da reserva inválida. Use o formato DD-MM-AAAA"
            }), 400


        data_banco = data_convertida.strftime(
            "%Y-%m-%d"
        )


        filtros.append(
            "Data_da_Reserva = ?"
        )

        valores.append(
            data_banco
        )

    if status_da_reserva is not None:

        if not status_da_reserva:

            return jsonify({
                "erro": "Informe o status da reserva"
            }), 400


        status_da_reserva = (
            status_da_reserva.upper()
        )


        status_permitidos = {
            "PENDENTE",
            "CONFIRMADA",
            "CANCELADA",
            "CONCLUIDA"
        }

        if status_da_reserva not in status_permitidos:

            return jsonify({

                "erro": "Status da reserva inválido",

                "status_permitidos":
                    list(status_permitidos)

            }), 400


        filtros.append(
            "Status_da_Reserva = ?"
        )

        valores.append(
            status_da_reserva
        )


    banco_de_dados = conexao_backend()

    try:

        consulta = '''

            SELECT

                Numero_da_Reserva,

                Data_do_Agendamento,

                Horario_do_Agendamento,

                Numero_do_Cliente,

                Quantidade_de_Pessoas_na_Mesa,

                Numero_da_Mesa,

                Capacidade_da_Mesa_na_Reserva,

                Data_da_Reserva,

                Horario_da_Reserva,

                Data_de_Termino_da_Reserva,

                Horario_de_Termino_da_Reserva,

                Duracao_da_Reserva,

                Status_da_Reserva

            FROM Reservas

        '''


        if filtros:

            consulta += (
                " WHERE "
                + " AND ".join(filtros)
            )


        consulta += '''
            ORDER BY
                Data_da_Reserva,
                Horario_da_Reserva,
                Numero_da_Reserva
        '''


        reservas = banco_de_dados.execute(
            consulta,
            valores
        ).fetchall()


        if not reservas:

            return jsonify({

                "mensagem":
                    "Nenhuma reserva encontrada"

            }), 404


        resultado = []


        for reserva in reservas:

            resultado.append({

                "numero_da_reserva":
                    reserva["Numero_da_Reserva"],

                "data_do_agendamento":
                    datetime.strptime(
                        reserva["Data_do_Agendamento"],
                        "%Y-%m-%d"
                    ).strftime("%d-%m-%Y"),

                "horario_do_agendamento":
                    reserva["Horario_do_Agendamento"],

                "numero_do_cliente":
                    reserva["Numero_do_Cliente"],

                "quantidade_de_pessoas_na_mesa":
                    reserva[
                        "Quantidade_de_Pessoas_na_Mesa"
                    ],

                "numero_da_mesa":
                    reserva["Numero_da_Mesa"],

                "capacidade_da_mesa_na_reserva":
                    reserva[
                        "Capacidade_da_Mesa_na_Reserva"
                    ],

                "data_da_reserva":
                    datetime.strptime(
                        reserva["Data_da_Reserva"],
                        "%Y-%m-%d"
                    ).strftime("%d-%m-%Y"),

                "horario_da_reserva":
                    reserva["Horario_da_Reserva"],

                "data_de_termino_da_reserva":
                    datetime.strptime(
                        reserva[
                            "Data_de_Termino_da_Reserva"
                        ],
                        "%Y-%m-%d"
                    ).strftime("%d-%m-%Y"),

                "horario_de_termino_da_reserva":
                    reserva[
                        "Horario_de_Termino_da_Reserva"
                    ],

                "duracao_da_reserva":
                    reserva["Duracao_da_Reserva"],

                "status_da_reserva":
                    reserva["Status_da_Reserva"]

            })


        return jsonify(resultado), 200


    except Exception as erro:

        return jsonify({

            "erro": "Erro ao consultar reservas",

            "detalhes": str(erro)

        }), 500


    finally:

        banco_de_dados.close()


# ROTA PARA ATUALIZAR RESERVA

@rotas_reservas.route('/reservas/<int:numero_da_reserva>',methods=['PUT'])
def atualizar_reserva(numero_da_reserva):

    """
    Atualiza uma reserva existente.

    Permite atualizar um ou mais dados da reserva. Reservas CANCELADA
    ou CONCLUIDA não podem ser alteradas.

    ---
    tags:
      - Reservas

    parameters:
      - name: numero_da_reserva
        in: path
        type: integer
        required: true
        description: Número da reserva que será atualizada.
        example: 1

      - name: body
        in: body
        required: true
        description: Campos da reserva que serão atualizados. Pelo menos um campo deve ser informado.
        schema:
          type: object
          properties:
            numero_do_cliente:
              type: integer
              description: Novo número do cliente.
              example: 1
            quantidade_de_pessoas_na_mesa:
              type: integer
              description: Nova quantidade de pessoas.
              example: 3
            numero_da_mesa:
              type: integer
              description: Novo número da mesa.
              example: 6
            data_da_reserva:
              type: string
              description: Nova data no formato DD-MM-AAAA.
              example: "21-09-2026"
            horario_da_reserva:
              type: string
              description: Novo horário no formato HH:MM.
              example: "20:00"
            duracao_da_reserva:
              type: integer
              description: Nova duração em minutos. O mínimo é 60 minutos.
              example: 120

    responses:
      200:
        description: Reserva atualizada com sucesso.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Reserva atualizada com sucesso
            reserva:
              type: object
              properties:
                numero_da_reserva:
                  type: integer
                  example: 1
                data_do_agendamento:
                  type: string
                  example: "13-09-2026"
                horario_do_agendamento:
                  type: string
                  example: "18:30:00"
                numero_do_cliente:
                  type: integer
                  example: 1
                quantidade_de_pessoas_na_mesa:
                  type: integer
                  example: 3
                numero_da_mesa:
                  type: integer
                  example: 6
                capacidade_da_mesa_na_reserva:
                  type: integer
                  example: 4
                data_da_reserva:
                  type: string
                  example: "21-09-2026"
                horario_da_reserva:
                  type: string
                  example: "20:00"
                data_de_termino_da_reserva:
                  type: string
                  example: "21-09-2026"
                horario_de_termino_da_reserva:
                  type: string
                  example: "22:00"
                duracao_da_reserva:
                  type: integer
                  example: 120
                status_da_reserva:
                  type: string
                  example: PENDENTE

      400:
        description: Dados inválidos ou reserva que não pode ser alterada.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Reservas CANCELADA ou CONCLUIDA não podem ser alteradas
            capacidade_da_mesa:
              type: integer
              example: 4

      404:
        description: Reserva, cliente ou mesa não encontrada.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Reserva não encontrada

      409:
        description: A mesa já possui outra reserva no período informado.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: A mesa já possui uma reserva nesse período
            numero_da_reserva_em_conflito:
              type: integer
              example: 3

      500:
        description: Erro interno ao atualizar a reserva.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao atualizar reserva
            detalhes:
              type: string
              example: Erro interno no banco de dados
    """

    if numero_da_reserva <= 0:

        return jsonify({
            "erro": "Número da reserva inválido"
        }), 400


    dados = request.get_json(silent=True)


    if dados is None:

        return jsonify({
            "erro": "O corpo da requisição deve ser um JSON"
        }), 400


    if not isinstance(dados, dict):

        return jsonify({
            "erro": "O corpo da requisição deve ser um objeto JSON"
        }), 400

    campos_permitidos = {
        "numero_do_cliente",
        "quantidade_de_pessoas_na_mesa",
        "numero_da_mesa",
        "data_da_reserva",
        "horario_da_reserva",
        "duracao_da_reserva"
    }


    campos_recebidos = set(dados.keys())


    campos_invalidos = (
        campos_recebidos - campos_permitidos
    )


    if campos_invalidos:

        return jsonify({

            "erro": "Campo(s) não permitido(s)",

            "campos_invalidos":
                list(campos_invalidos),

            "campos_permitidos":
                list(campos_permitidos)

        }), 400


    if not dados:

        return jsonify({
            "erro": "Informe pelo menos um campo para atualizar"
        }), 400


    banco_de_dados = conexao_backend()

    try:

        reserva = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Reserva,
                Numero_do_Cliente,
                Quantidade_de_Pessoas_na_Mesa,
                Numero_da_Mesa,
                Capacidade_da_Mesa_na_Reserva,
                Data_da_Reserva,
                Horario_da_Reserva,
                Duracao_da_Reserva,
                Status_da_Reserva
            FROM Reservas
            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchone()


        if reserva is None:

            return jsonify({
                "erro": "Reserva não encontrada"
            }), 404

        if reserva["Status_da_Reserva"] in (
            "CANCELADA",
            "CONCLUIDA"
        ):

            return jsonify({

                "erro":
                    "Reservas CANCELADA ou CONCLUIDA não podem ser alteradas"

            }), 400

        numero_do_cliente = (
            reserva["Numero_do_Cliente"]
        )

        quantidade_de_pessoas_na_mesa = (
            reserva["Quantidade_de_Pessoas_na_Mesa"]
        )

        numero_da_mesa = (
            reserva["Numero_da_Mesa"]
        )

        data_da_reserva = (
            reserva["Data_da_Reserva"]
        )

        horario_da_reserva = (
            reserva["Horario_da_Reserva"]
        )

        duracao_da_reserva = (
            reserva["Duracao_da_Reserva"]
        )

        if "numero_do_cliente" in dados:

            valor = dados["numero_do_cliente"]

            if isinstance(valor, bool):

                return jsonify({
                    "erro": "Número do cliente inválido"
                }), 400

            try:

                numero_do_cliente = int(valor)

            except (TypeError, ValueError):

                return jsonify({
                    "erro": "Número do cliente inválido"
                }), 400

            if numero_do_cliente <= 0:

                return jsonify({
                    "erro":
                        "O número do cliente deve ser maior que zero"
                }), 400


        if "quantidade_de_pessoas_na_mesa" in dados:

            valor = dados["quantidade_de_pessoas_na_mesa"]

            if isinstance(valor, bool):

                return jsonify({
                    "erro": "Quantidade de pessoas inválida"
                }), 400

            try:

                quantidade_de_pessoas_na_mesa = int(valor)

            except (TypeError, ValueError):

                return jsonify({
                    "erro": "Quantidade de pessoas inválida"
                }), 400

            if quantidade_de_pessoas_na_mesa <= 0:

                return jsonify({
                    "erro":
                        "A quantidade de pessoas deve ser maior que zero"
                }), 400

        if "numero_da_mesa" in dados:

            valor = dados["numero_da_mesa"]

            if isinstance(valor, bool):

                return jsonify({
                    "erro": "Número da mesa inválido"
                }), 400

            try:

                numero_da_mesa = int(valor)

            except (TypeError, ValueError):

                return jsonify({
                    "erro": "Número da mesa inválido"
                }), 400

            if numero_da_mesa <= 0:

                return jsonify({
                    "erro":
                        "O número da mesa deve ser maior que zero"
                }), 400

        if "data_da_reserva" in dados:

            valor = dados["data_da_reserva"]

            if not isinstance(valor, str):

                return jsonify({
                    "erro": "Data da reserva inválida"
                }), 400

            try:

                data_convertida = datetime.strptime(
                    valor,
                    "%d-%m-%Y"
                ).date()

            except ValueError:

                return jsonify({
                    "erro":
                        "Data da reserva inválida. Use o formato DD-MM-AAAA"
                }), 400


            if data_convertida.strftime(
                "%d-%m-%Y"
            ) != valor:

                return jsonify({
                    "erro":
                        "Data da reserva inválida. Use o formato DD-MM-AAAA"
                }), 400


            data_da_reserva = data_convertida.strftime(
                "%Y-%m-%d"
            )

        if "horario_da_reserva" in dados:

            valor = dados["horario_da_reserva"]

            if not isinstance(valor, str):

                return jsonify({
                    "erro": "Horário da reserva inválido"
                }), 400

            try:

                horario_convertido = datetime.strptime(
                    valor,
                    "%H:%M"
                ).time()

            except ValueError:

                return jsonify({
                    "erro":
                        "Horário da reserva inválido. Use o formato HH:MM"
                }), 400


            if horario_convertido.strftime(
                "%H:%M"
            ) != valor:

                return jsonify({
                    "erro":
                        "Horário da reserva inválido. Use o formato HH:MM"
                }), 400


            horario_da_reserva = valor

        if "duracao_da_reserva" in dados:

            valor = dados["duracao_da_reserva"]

            if isinstance(valor, bool):

                return jsonify({
                    "erro": "Duração da reserva inválida"
                }), 400

            try:

                duracao_da_reserva = int(valor)

            except (TypeError, ValueError):

                return jsonify({
                    "erro": "Duração da reserva inválida"
                }), 400

            if duracao_da_reserva < 60:

                return jsonify({
                    "erro":"A duração mínima da reserva é de 1 hora"
                }), 400

            if duracao_da_reserva > 840:

                 return jsonify({
                 "erro": "A duração máxima da reserva é de 14 horas"
                }), 400

        cliente = banco_de_dados.execute(
            '''
            SELECT Numero_do_Cliente
            FROM Clientes
            WHERE Numero_do_Cliente = ?
            ''',
            (numero_do_cliente,)
        ).fetchone()

        if cliente is None:

            return jsonify({
                "erro": "Cliente não encontrado"
            }), 404

        mesa = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Mesa,
                Capacidade_da_Mesa
            FROM Mesa
            WHERE Numero_da_Mesa = ?
            ''',
            (numero_da_mesa,)
        ).fetchone()

        if mesa is None:

            return jsonify({
                "erro": "Mesa não encontrada"
            }), 404


        capacidade_da_mesa = mesa["Capacidade_da_Mesa"]

                         
        if quantidade_de_pessoas_na_mesa <= 2:

         capacidade_necessaria = 2

        elif quantidade_de_pessoas_na_mesa <= 4:

         capacidade_necessaria = 4

        elif quantidade_de_pessoas_na_mesa <= 6:

         capacidade_necessaria = 6

        elif quantidade_de_pessoas_na_mesa <= 8:

         capacidade_necessaria = 8

        else:

         capacidade_necessaria = 10

        if capacidade_da_mesa != capacidade_necessaria:

          return jsonify({
             "erro": "A capacidade da mesa não corresponde à quantidade de pessoas",
             "quantidade_de_pessoas": quantidade_de_pessoas_na_mesa,
             "capacidade_necessaria": capacidade_necessaria,
             "capacidade_da_mesa": capacidade_da_mesa
            }), 400


        inicio = datetime.strptime(
            f"{data_da_reserva} {horario_da_reserva}",
            "%Y-%m-%d %H:%M"
        )

        termino = (
            inicio +
            timedelta(minutes=duracao_da_reserva)
        )

        abertura = inicio.replace(
            hour=10,
            minute=0,
            second=0
        )

        fechamento = inicio.replace(
            hour=0,
            minute=0,
            second=0
        ) + timedelta(days=1)


        if inicio < abertura or termino > fechamento:

            return jsonify({

                "erro":
                    "A reserva deve estar dentro do horário de funcionamento",

                "horario_funcionamento":
                    "10:00 às 00:00"

            }), 400

        agora = datetime.now()

        diferenca = inicio - agora


        if diferenca.total_seconds() < 3600:

            return jsonify({

                "erro":
                    "A reserva deve ser realizada com pelo menos 1 hora de antecedência"

            }), 400

        inicio_texto = inicio.strftime(
            "%Y-%m-%d %H:%M"
        )

        termino_texto = termino.strftime(
            "%Y-%m-%d %H:%M"
        )


        conflito = banco_de_dados.execute(
            '''
            SELECT Numero_da_Reserva
            FROM Reservas

            WHERE Numero_da_Mesa = ?

            AND Numero_da_Reserva != ?

            AND Status_da_Reserva != 'CANCELADA'

            AND (Data_da_Reserva || ' ' || Horario_da_Reserva) < ?

            AND (
                Data_de_Termino_da_Reserva
                || ' '
                || Horario_de_Termino_da_Reserva
            ) > ?

            LIMIT 1
            ''',
            (
                numero_da_mesa,
                numero_da_reserva,
                termino_texto,
                inicio_texto
            )
        ).fetchone()


        if conflito is not None:

            return jsonify({

                "erro":
                    "A mesa já possui uma reserva nesse período",

                "numero_da_reserva_em_conflito":
                    conflito["Numero_da_Reserva"]

            }), 409

        data_de_termino = termino.strftime(
            "%Y-%m-%d"
        )

        horario_de_termino = termino.strftime(
            "%H:%M"
        )

        banco_de_dados.execute(
            '''
            UPDATE Reservas

            SET
                Numero_do_Cliente = ?,
                Quantidade_de_Pessoas_na_Mesa = ?,
                Numero_da_Mesa = ?,
                Capacidade_da_Mesa_na_Reserva = ?,
                Data_da_Reserva = ?,
                Horario_da_Reserva = ?,
                Data_de_Termino_da_Reserva = ?,
                Horario_de_Termino_da_Reserva = ?,
                Duracao_da_Reserva = ?

            WHERE Numero_da_Reserva = ?
            ''',
            (
                numero_do_cliente,
                quantidade_de_pessoas_na_mesa,
                numero_da_mesa,
                capacidade_da_mesa,
                data_da_reserva,
                horario_da_reserva,
                data_de_termino,
                horario_de_termino,
                duracao_da_reserva,
                numero_da_reserva
            )
        )

        banco_de_dados.commit()

        reserva_atualizada = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Reserva,
                Data_do_Agendamento,
                Horario_do_Agendamento,
                Numero_do_Cliente,
                Quantidade_de_Pessoas_na_Mesa,
                Numero_da_Mesa,
                Capacidade_da_Mesa_na_Reserva,
                Data_da_Reserva,
                Horario_da_Reserva,
                Data_de_Termino_da_Reserva,
                Horario_de_Termino_da_Reserva,
                Duracao_da_Reserva,
                Status_da_Reserva

            FROM Reservas

            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchone()


        return jsonify({

            "mensagem":
                "Reserva atualizada com sucesso",

            "reserva": {

                "numero_da_reserva":
                    reserva_atualizada[
                        "Numero_da_Reserva"
                    ],

                "data_do_agendamento":
                    datetime.strptime(
                        reserva_atualizada[
                            "Data_do_Agendamento"
                        ],
                        "%Y-%m-%d"
                    ).strftime("%d-%m-%Y"),

                "horario_do_agendamento":
                    reserva_atualizada[
                        "Horario_do_Agendamento"
                    ],

                "numero_do_cliente":
                    reserva_atualizada[
                        "Numero_do_Cliente"
                    ],

                "quantidade_de_pessoas_na_mesa":
                    reserva_atualizada[
                        "Quantidade_de_Pessoas_na_Mesa"
                    ],

                "numero_da_mesa":
                    reserva_atualizada[
                        "Numero_da_Mesa"
                    ],

                "capacidade_da_mesa_na_reserva":
                    reserva_atualizada[
                        "Capacidade_da_Mesa_na_Reserva"
                    ],

                "data_da_reserva":
                    datetime.strptime(
                        reserva_atualizada[
                            "Data_da_Reserva"
                        ],
                        "%Y-%m-%d"
                    ).strftime("%d-%m-%Y"),

                "horario_da_reserva":
                    reserva_atualizada[
                        "Horario_da_Reserva"
                    ],

                "data_de_termino_da_reserva":
                    datetime.strptime(
                        reserva_atualizada[
                            "Data_de_Termino_da_Reserva"
                        ],
                        "%Y-%m-%d"
                    ).strftime("%d-%m-%Y"),

                "horario_de_termino_da_reserva":
                    reserva_atualizada[
                        "Horario_de_Termino_da_Reserva"
                    ],

                "duracao_da_reserva":
                    reserva_atualizada[
                        "Duracao_da_Reserva"
                    ],

                "status_da_reserva":
                    reserva_atualizada[
                        "Status_da_Reserva"
                    ]
            }

        }), 200


    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({

            "erro": "Erro ao atualizar reserva",

            "detalhes": str(erro)

        }), 500


    finally:

        banco_de_dados.close()


# ROTA PARA CANCELAR RESERVA

@rotas_reservas.route('/reservas/<int:numero_da_reserva>',methods=['DELETE'])
def cancelar_reserva(numero_da_reserva):

    """
    Cancela uma reserva existente.

    A reserva não é removida do banco de dados. Seu status é alterado
    para CANCELADA.

    Reservas já CANCELADAS ou CONCLUIDAS não podem ser canceladas.

    ---
    tags:
      - Reservas

    parameters:
      - name: numero_da_reserva
        in: path
        type: integer
        required: true
        description: Número da reserva que será cancelada.
        example: 1

    responses:
      200:
        description: Reserva cancelada com sucesso.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Reserva cancelada com sucesso
            reserva:
              type: object
              properties:
                numero_da_reserva:
                  type: integer
                  example: 1
                data_do_agendamento:
                  type: string
                  example: "13-09-2026"
                horario_do_agendamento:
                  type: string
                  example: "18:30:00"
                numero_do_cliente:
                  type: integer
                  example: 1
                quantidade_de_pessoas_na_mesa:
                  type: integer
                  example: 2
                numero_da_mesa:
                  type: integer
                  example: 5
                capacidade_da_mesa_na_reserva:
                  type: integer
                  example: 4
                data_da_reserva:
                  type: string
                  example: "20-09-2026"
                horario_da_reserva:
                  type: string
                  example: "19:00"
                data_de_termino_da_reserva:
                  type: string
                  example: "20-09-2026"
                horario_de_termino_da_reserva:
                  type: string
                  example: "21:00"
                duracao_da_reserva:
                  type: integer
                  example: 120
                status_da_reserva:
                  type: string
                  example: CANCELADA

      400:
        description: Número da reserva inválido ou reserva que não pode ser cancelada.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Uma reserva concluída não pode ser cancelada

      404:
        description: Reserva não encontrada.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Reserva não encontrada

      500:
        description: Erro interno ao cancelar a reserva.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao cancelar reserva
            detalhes:
              type: string
              example: Erro interno no banco de dados
    """

    if numero_da_reserva <= 0:

        return jsonify({
            "erro": "Número da reserva inválido"
        }), 400


    banco_de_dados = conexao_backend()

    try:

        reserva = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Reserva,
                Status_da_Reserva
            FROM Reservas
            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchone()


        if reserva is None:

            return jsonify({
                "erro": "Reserva não encontrada"
            }), 404

        status_atual = reserva["Status_da_Reserva"]

        if status_atual == "CANCELADA":

            return jsonify({
                "erro": "A reserva já está cancelada"
            }), 400

        if status_atual == "CONCLUIDA":

            return jsonify({
                "erro": "Uma reserva concluída não pode ser cancelada"
            }), 400

        banco_de_dados.execute(
            '''
            UPDATE Reservas

            SET Status_da_Reserva = 'CANCELADA'

            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        )

        banco_de_dados.commit()

        reserva_cancelada = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Reserva,
                Data_do_Agendamento,
                Horario_do_Agendamento,
                Numero_do_Cliente,
                Quantidade_de_Pessoas_na_Mesa,
                Numero_da_Mesa,
                Capacidade_da_Mesa_na_Reserva,
                Data_da_Reserva,
                Horario_da_Reserva,
                Data_de_Termino_da_Reserva,
                Horario_de_Termino_da_Reserva,
                Duracao_da_Reserva,
                Status_da_Reserva

            FROM Reservas

            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchone()


        return jsonify({

            "mensagem":
                "Reserva cancelada com sucesso",

            "reserva": {

                "numero_da_reserva":
                    reserva_cancelada[
                        "Numero_da_Reserva"
                    ],

                "data_do_agendamento":
                    datetime.strptime(
                        reserva_cancelada[
                            "Data_do_Agendamento"
                        ],
                        "%Y-%m-%d"
                    ).strftime("%d-%m-%Y"),

                "horario_do_agendamento":
                    reserva_cancelada[
                        "Horario_do_Agendamento"
                    ],

                "numero_do_cliente":
                    reserva_cancelada[
                        "Numero_do_Cliente"
                    ],

                "quantidade_de_pessoas_na_mesa":
                    reserva_cancelada[
                        "Quantidade_de_Pessoas_na_Mesa"
                    ],

                "numero_da_mesa":
                    reserva_cancelada[
                        "Numero_da_Mesa"
                    ],

                "capacidade_da_mesa_na_reserva":
                    reserva_cancelada[
                        "Capacidade_da_Mesa_na_Reserva"
                    ],

                "data_da_reserva":
                    datetime.strptime(
                        reserva_cancelada[
                            "Data_da_Reserva"
                        ],
                        "%Y-%m-%d"
                    ).strftime("%d-%m-%Y"),

                "horario_da_reserva":
                    reserva_cancelada[
                        "Horario_da_Reserva"
                    ],

                "data_de_termino_da_reserva":
                    datetime.strptime(
                        reserva_cancelada[
                            "Data_de_Termino_da_Reserva"
                        ],
                        "%Y-%m-%d"
                    ).strftime("%d-%m-%Y"),

                "horario_de_termino_da_reserva":
                    reserva_cancelada[
                        "Horario_de_Termino_da_Reserva"
                    ],

                "duracao_da_reserva":
                    reserva_cancelada[
                        "Duracao_da_Reserva"
                    ],

                "status_da_reserva":
                    reserva_cancelada[
                        "Status_da_Reserva"
                    ]
            }

        }), 200


    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({

            "erro": "Erro ao cancelar reserva",

            "detalhes": str(erro)

        }), 500


    finally:

        banco_de_dados.close()