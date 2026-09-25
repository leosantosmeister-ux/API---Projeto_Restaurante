from flask import Blueprint, request, jsonify
from Projeto_Restaurante_Banco_de_Dados import conexao_backend

rotas_pagamentos = Blueprint('rotas_pagamentos', __name__)

# ROTA PARA REGISTRAR UM PAGAMENTO

@rotas_pagamentos.route('/reservas/<int:numero_da_reserva>/pagamento', methods=['POST'])
def registrar_pagamento(numero_da_reserva):

    """
    Registra um pagamento e confirma a reserva.

    O pagamento realizado pelo cliente é registrado como PAGO
    e a reserva PENDENTE é alterada para CONFIRMADA.

    ---
    tags:
      - Pagamentos

    consumes:
      - application/json

    produces:
      - application/json

    parameters:
      - name: numero_da_reserva
        in: path
        type: integer
        required: true
        description: Número da reserva que receberá o pagamento.
        example: 1

      - in: body
        name: pagamento
        required: true
        schema:
          type: object
          required:
            - forma_de_pagamento
          properties:
            forma_de_pagamento:
              type: string
              enum:
                - PIX
                - CARTAO_CREDITO
                - CARTAO_DEBITO
                - DINHEIRO
              description: Forma de pagamento escolhida.
              example: PIX

    responses:
      201:
        description: Pagamento registrado e reserva confirmada.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Pagamento realizado com sucesso
            pagamento:
              type: object
            reserva:
              type: object

      400:
        description: Dados inválidos ou reserva que não pode receber pagamento.

      404:
        description: Reserva não encontrada.

      500:
        description: Erro interno ao registrar o pagamento.
    """

    if numero_da_reserva <= 0:

        return jsonify({
            "erro": "Número da reserva inválido"
        }), 400

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):

        return jsonify({
            "erro": "Formato JSON inválido"
        }), 400

    campos_permitidos = {
        "forma_de_pagamento"
    }

    campos_recebidos = set(
        dados.keys()
    )

    campos_invalidos = (
        campos_recebidos -
        campos_permitidos
    )

    if campos_invalidos:

        return jsonify({
            "erro": "Campo(s) não permitido(s)",
            "campos_invalidos":
                list(campos_invalidos),
            "campos_permitidos":
                list(campos_permitidos)
        }), 400

    if "forma_de_pagamento" not in dados:

        return jsonify({
            "erro":
                "Campo forma_de_pagamento não informado"
        }), 400

    forma_de_pagamento = dados[
        "forma_de_pagamento"
    ]

    formas_de_pagamento_permitidas = {
        "PIX",
        "CARTAO_CREDITO",
        "CARTAO_DEBITO",
        "DINHEIRO"
    }

    if (
        forma_de_pagamento not in
        formas_de_pagamento_permitidas
    ):

        return jsonify({
            "erro":
                "Forma de pagamento inválida",
            "formas_de_pagamento_permitidas":
                list(formas_de_pagamento_permitidas)
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

        if (
            reserva["Status_da_Reserva"]
            !=
            "PENDENTE"
        ):

            return jsonify({
                "erro":
                    "Somente reservas PENDENTES podem receber pagamento",
                "status_atual":
                    reserva["Status_da_Reserva"]
            }), 400

        itens = banco_de_dados.execute(
            '''
            SELECT
                Valor_do_Item_na_Reserva,
                Quantidade_de_Itens
            FROM Itens_da_Reserva
            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchall()

        if not itens:

            return jsonify({
                "erro":
                    "A reserva não possui itens para pagamento"
            }), 400

        valor_total = 0

        for item in itens:

            valor_total += (
                item["Valor_do_Item_na_Reserva"]
                *
                item["Quantidade_de_Itens"]
            )

        pagamento_existente = banco_de_dados.execute(
            '''
            SELECT
                ID_Pagamentos,
                Status_do_Pagamento
            FROM Pagamentos
            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchone()

        from datetime import datetime

        data_do_pagamento = datetime.now().strftime(
            "%Y-%m-%d"
        )

        if pagamento_existente is None:

            cursor = banco_de_dados.execute(
                '''
                INSERT INTO Pagamentos (
                    Numero_da_Reserva,
                    Valor_do_Pagamento,
                    Forma_de_Pagamento,
                    Data_do_Pagamento,
                    Status_do_Pagamento
                )
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    numero_da_reserva,
                    valor_total,
                    forma_de_pagamento,
                    data_do_pagamento,
                    "PAGO"
                )
            )

            id_pagamento = cursor.lastrowid

        else:

            if (
                pagamento_existente[
                    "Status_do_Pagamento"
                ]
                ==
                "PAGO"
            ):

                return jsonify({
                    "erro":
                        "A reserva já possui um pagamento realizado"
                }), 409

            if (
                pagamento_existente[
                    "Status_do_Pagamento"
                ]
                ==
                "CANCELADO"
            ):

                return jsonify({
                    "erro":
                        "O pagamento anterior foi cancelado"
                }), 400

            id_pagamento = pagamento_existente[
                    "ID_Pagamentos"
                ]

            banco_de_dados.execute(
                '''
                UPDATE Pagamentos
                SET
                    Valor_do_Pagamento = ?,
                    Forma_de_Pagamento = ?,
                    Data_do_Pagamento = ?,
                    Status_do_Pagamento = ?
                WHERE ID_Pagamentos = ?
                ''',
                (
                    valor_total,
                    forma_de_pagamento,
                    data_do_pagamento,
                    "PAGO",
                    id_pagamento
                )
            )

        banco_de_dados.execute(
            '''
            UPDATE Reservas
            SET Status_da_Reserva = ?
            WHERE Numero_da_Reserva = ?
            AND Status_da_Reserva = 'PENDENTE'
            ''',
            (
                "CONFIRMADA",
                numero_da_reserva
            )
        )

        banco_de_dados.commit()

        pagamento = banco_de_dados.execute(
            '''
            SELECT
                ID_Pagamentos,
                Numero_da_Reserva,
                Valor_do_Pagamento,
                Forma_de_Pagamento,
                Data_do_Pagamento,
                Status_do_Pagamento
            FROM Pagamentos
            WHERE ID_Pagamentos = ?
            ''',
            (id_pagamento,)
        ).fetchone()

        reserva_atualizada = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Reserva,
                Status_da_Reserva
            FROM Reservas
            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchone()

        return jsonify({

            "mensagem":
                "Pagamento realizado com sucesso",

            "pagamento": {

                "id_pagamentos":
                    pagamento["ID_Pagamentos"],

                "numero_da_reserva":
                    pagamento["Numero_da_Reserva"],

                "valor_do_pagamento":
                    pagamento["Valor_do_Pagamento"],

                "forma_de_pagamento":
                    pagamento["Forma_de_Pagamento"],

                "data_do_pagamento":
                    pagamento["Data_do_Pagamento"],

                "status_do_pagamento":
                    pagamento["Status_do_Pagamento"]

            },

            "reserva": {

                "numero_da_reserva":
                    reserva_atualizada[
                        "Numero_da_Reserva"
                    ],

                "status_da_reserva":
                    reserva_atualizada[
                        "Status_da_Reserva"
                    ]

            }

        }), 201

    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({
            "erro":
                "Erro ao registrar pagamento",
            "detalhes":
                str(erro)
        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA CONSULTAR O PAGAMENTO DA RESERVA

@rotas_pagamentos.route('/reservas/<int:numero_da_reserva>/pagamento',methods=['GET'])
def consultar_pagamento(numero_da_reserva):

    """
    Consulta o pagamento de uma reserva.

    ---
    tags:
      - Pagamentos

    parameters:
      - name: numero_da_reserva
        in: path
        type: integer
        required: true
        description: Número da reserva cujo pagamento será consultado.
        example: 1

    responses:
      200:
        description: Pagamento consultado com sucesso.
        schema:
          type: object
          properties:
            numero_da_reserva:
              type: integer
              example: 1
            status_da_reserva:
              type: string
              example: CONFIRMADA
            pagamento:
              type: object
              properties:
                id_pagamentos:
                  type: integer
                  example: 1
                numero_da_reserva:
                  type: integer
                  example: 1
                valor_do_pagamento:
                  type: number
                  format: float
                  example: 150.0
                forma_de_pagamento:
                  type: string
                  example: PIX
                data_do_pagamento:
                  type: string
                  example: "2026-09-13"
                status_do_pagamento:
                  type: string
                  example: PAGO

      400:
        description: Número da reserva inválido.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Número da reserva inválido

      404:
        description: Reserva não encontrada ou reserva sem pagamento.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: A reserva não possui pagamento

      500:
        description: Erro interno ao consultar o pagamento.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao consultar pagamento
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

        pagamento = banco_de_dados.execute(
            '''
            SELECT
                ID_Pagamentos,
                Numero_da_Reserva,
                Valor_do_Pagamento,
                Forma_de_Pagamento,
                Data_do_Pagamento,
                Status_do_Pagamento
            FROM Pagamentos
            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchone()

        if pagamento is None:

            return jsonify({
                "erro":
                    "A reserva não possui pagamento"
            }), 404

        return jsonify({
            "numero_da_reserva":
                reserva["Numero_da_Reserva"],

            "status_da_reserva":
                reserva["Status_da_Reserva"],

            "pagamento": {
                "id_pagamentos":
                    pagamento["ID_Pagamentos"],

                "numero_da_reserva":
                    pagamento["Numero_da_Reserva"],

                "valor_do_pagamento":
                    pagamento["Valor_do_Pagamento"],

                "forma_de_pagamento":
                    pagamento["Forma_de_Pagamento"],

                "data_do_pagamento":
                    pagamento["Data_do_Pagamento"],

                "status_do_pagamento":
                    pagamento["Status_do_Pagamento"]
            }
        }), 200

    except Exception as erro:

        return jsonify({
            "erro":
                "Erro ao consultar pagamento",
            "detalhes":
                str(erro)
        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA ALTERAR O STATUS DO PAGAMENTO

@rotas_pagamentos.route('/reservas/<int:numero_da_reserva>/pagamento',methods=['PUT'])
def atualizar_status_pagamento(numero_da_reserva):

    """
    Atualiza o status de um pagamento pendente.

    A atualização do pagamento também pode alterar o status da reserva:
    PAGO altera uma reserva PENDENTE para CONFIRMADA.
    CANCELADO altera uma reserva PENDENTE para CANCELADA.

    ---
    tags:
      - Pagamentos

    parameters:
      - name: numero_da_reserva
        in: path
        type: integer
        required: true
        description: Número da reserva cujo pagamento terá o status alterado.
        example: 1

      - name: body
        in: body
        required: true
        description: Novo status do pagamento.
        schema:
          type: object
          required:
            - status_do_pagamento
          properties:
            status_do_pagamento:
              type: string
              enum:
                - PAGO
                - CANCELADO
              description: Novo status do pagamento.
              example: PAGO

    responses:
      200:
        description: Status do pagamento atualizado com sucesso.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Status do pagamento atualizado com sucesso
            pagamento:
              type: object
              properties:
                id_pagamentos:
                  type: integer
                  example: 1
                numero_da_reserva:
                  type: integer
                  example: 1
                valor_do_pagamento:
                  type: number
                  format: float
                  example: 150.0
                forma_de_pagamento:
                  type: string
                  example: PIX
                data_do_pagamento:
                  type: string
                  example: "2026-09-13"
                status_do_pagamento:
                  type: string
                  example: PAGO
            reserva:
              type: object
              properties:
                numero_da_reserva:
                  type: integer
                  example: 1
                status_da_reserva:
                  type: string
                  example: CONFIRMADA

      400:
        description: Dados inválidos ou pagamento que não pode ter o status alterado.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Somente pagamentos PENDENTES podem ter o status alterado
            status_atual:
              type: string
              example: PAGO

      404:
        description: Reserva não encontrada ou reserva sem pagamento.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: A reserva não possui pagamento

      500:
        description: Erro interno ao atualizar o status do pagamento.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao atualizar status do pagamento
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
            "erro": "Formato JSON inválido"
        }), 400

    if not isinstance(dados, dict):

        return jsonify({
            "erro": "Formato JSON inválido"
        }), 400

    campos_permitidos = {
        "status_do_pagamento"
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

    if "status_do_pagamento" not in campos_recebidos:

        return jsonify({
            "erro":
                "Campo status_do_pagamento não informado"
        }), 400

    status_novo = dados[
        "status_do_pagamento"
    ]

    status_permitidos = {
        "PAGO",
        "CANCELADO"
    }

    if status_novo not in status_permitidos:

        return jsonify({
            "erro":
                "Status de pagamento inválido",
            "status_permitidos":
                list(status_permitidos)
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

        pagamento = banco_de_dados.execute(
            '''
            SELECT
                ID_Pagamentos,
                Numero_da_Reserva,
                Valor_do_Pagamento,
                Forma_de_Pagamento,
                Data_do_Pagamento,
                Status_do_Pagamento
            FROM Pagamentos
            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchone()

        if pagamento is None:

            return jsonify({
                "erro":
                    "A reserva não possui pagamento"
            }), 404

        status_atual = pagamento[
            "Status_do_Pagamento"
        ]

        if status_atual != "PENDENTE":

            return jsonify({
                "erro":
                    "Somente pagamentos PENDENTES podem ter o status alterado",
                "status_atual":
                    status_atual
            }), 400

        if status_novo == "PAGO":

            banco_de_dados.execute(
                '''
                UPDATE Pagamentos
                SET Status_do_Pagamento = ?
                WHERE ID_Pagamentos = ?
                ''',
                (
                    "PAGO",
                    pagamento["ID_Pagamentos"]
                )
            )

            banco_de_dados.execute(
                '''
                UPDATE Reservas
                SET Status_da_Reserva = ?
                WHERE Numero_da_Reserva = ?
                AND Status_da_Reserva = 'PENDENTE'
                ''',
                (
                    "CONFIRMADA",
                    numero_da_reserva
                )
            )

        elif status_novo == "CANCELADO":


            banco_de_dados.execute(
                '''
                UPDATE Pagamentos
                SET Status_do_Pagamento = ?
                WHERE ID_Pagamentos = ?
                ''',
                (
                    "CANCELADO",
                    pagamento["ID_Pagamentos"]
                )
            )

            banco_de_dados.execute(
                '''
                UPDATE Reservas
                SET Status_da_Reserva = ?
                WHERE Numero_da_Reserva = ?
                AND Status_da_Reserva = 'PENDENTE'
                ''',
                (
                    "CANCELADA",
                    numero_da_reserva
                )
            )

        banco_de_dados.commit()

        pagamento_atualizado = banco_de_dados.execute(
            '''
            SELECT
                ID_Pagamentos,
                Numero_da_Reserva,
                Valor_do_Pagamento,
                Forma_de_Pagamento,
                Data_do_Pagamento,
                Status_do_Pagamento
            FROM Pagamentos
            WHERE ID_Pagamentos = ?
            ''',
            (
                pagamento["ID_Pagamentos"],
            )
        ).fetchone()

        reserva_atualizada = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Reserva,
                Status_da_Reserva
            FROM Reservas
            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchone()

        return jsonify({
            "mensagem":
                "Status do pagamento atualizado com sucesso",

            "pagamento": {
                "id_pagamentos":
                    pagamento_atualizado[
                        "ID_Pagamentos"
                    ],

                "numero_da_reserva":
                    pagamento_atualizado[
                        "Numero_da_Reserva"
                    ],

                "valor_do_pagamento":
                    pagamento_atualizado[
                        "Valor_do_Pagamento"
                    ],

                "forma_de_pagamento":
                    pagamento_atualizado[
                        "Forma_de_Pagamento"
                    ],

                "data_do_pagamento":
                    pagamento_atualizado[
                        "Data_do_Pagamento"
                    ],

                "status_do_pagamento":
                    pagamento_atualizado[
                        "Status_do_Pagamento"
                    ]
            },

            "reserva": {
                "numero_da_reserva":
                    reserva_atualizada[
                        "Numero_da_Reserva"
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
            "erro":
                "Erro ao atualizar status do pagamento",
            "detalhes":
                str(erro)
        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA CANCELAR O PAGAMENTO

@rotas_pagamentos.route('/reservas/<int:numero_da_reserva>/pagamento',methods=['DELETE'])
def cancelar_pagamento(numero_da_reserva):

    """
    Cancela um pagamento pendente.

    O cancelamento também altera uma reserva PENDENTE para CANCELADA.
    Pagamentos PAGO ou já CANCELADOS não podem ser cancelados.

    ---
    tags:
      - Pagamentos

    parameters:
      - name: numero_da_reserva
        in: path
        type: integer
        required: true
        description: Número da reserva cujo pagamento será cancelado.
        example: 1

    responses:
      200:
        description: Pagamento cancelado com sucesso.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Pagamento cancelado com sucesso
            pagamento:
              type: object
              properties:
                id_pagamentos:
                  type: integer
                  example: 1
                numero_da_reserva:
                  type: integer
                  example: 1
                valor_do_pagamento:
                  type: number
                  format: float
                  example: 150.0
                forma_de_pagamento:
                  type: string
                  example: PIX
                data_do_pagamento:
                  type: string
                  example: "2026-09-13"
                status_do_pagamento:
                  type: string
                  example: CANCELADO
            reserva:
              type: object
              properties:
                numero_da_reserva:
                  type: integer
                  example: 1
                status_da_reserva:
                  type: string
                  example: CANCELADA

      400:
        description: Pagamento já cancelado, pagamento já pago ou número da reserva inválido.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Pagamentos PAGO não podem ser cancelados

      404:
        description: Reserva não encontrada ou reserva sem pagamento.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: A reserva não possui pagamento

      500:
        description: Erro interno ao cancelar o pagamento.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao cancelar pagamento
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

        pagamento = banco_de_dados.execute(
            '''
            SELECT
                ID_Pagamentos,
                Numero_da_Reserva,
                Valor_do_Pagamento,
                Forma_de_Pagamento,
                Data_do_Pagamento,
                Status_do_Pagamento
            FROM Pagamentos
            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchone()

        if pagamento is None:

            return jsonify({
                "erro":
                    "A reserva não possui pagamento"
            }), 404

        status_atual = pagamento[
            "Status_do_Pagamento"
        ]

        if status_atual == "CANCELADO":

            return jsonify({
                "erro":
                    "O pagamento já está cancelado"
            }), 400

        if status_atual == "PAGO":

            return jsonify({
                "erro":
                    "Pagamentos PAGO não podem ser cancelados"
            }), 400

        banco_de_dados.execute(
            '''
            UPDATE Pagamentos
            SET Status_do_Pagamento = ?
            WHERE ID_Pagamentos = ?
            ''',
            (
                "CANCELADO",
                pagamento["ID_Pagamentos"]
            )
        )

        banco_de_dados.execute(
            '''
            UPDATE Reservas
            SET Status_da_Reserva = ?
            WHERE Numero_da_Reserva = ?
            AND Status_da_Reserva = 'PENDENTE'
            ''',
            (
                "CANCELADA",
                numero_da_reserva
            )
        )

        banco_de_dados.commit()

        pagamento_atualizado = banco_de_dados.execute(
            '''
            SELECT
                ID_Pagamentos,
                Numero_da_Reserva,
                Valor_do_Pagamento,
                Forma_de_Pagamento,
                Data_do_Pagamento,
                Status_do_Pagamento
            FROM Pagamentos
            WHERE ID_Pagamentos = ?
            ''',
            (
                pagamento["ID_Pagamentos"],
            )
        ).fetchone()

        reserva_atualizada = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Reserva,
                Status_da_Reserva
            FROM Reservas
            WHERE Numero_da_Reserva = ?
            ''',
            (numero_da_reserva,)
        ).fetchone()

        return jsonify({
            "mensagem":
                "Pagamento cancelado com sucesso",

            "pagamento": {
                "id_pagamentos":
                    pagamento_atualizado[
                        "ID_Pagamentos"
                    ],

                "numero_da_reserva":
                    pagamento_atualizado[
                        "Numero_da_Reserva"
                    ],

                "valor_do_pagamento":
                    pagamento_atualizado[
                        "Valor_do_Pagamento"
                    ],

                "forma_de_pagamento":
                    pagamento_atualizado[
                        "Forma_de_Pagamento"
                    ],

                "data_do_pagamento":
                    pagamento_atualizado[
                        "Data_do_Pagamento"
                    ],

                "status_do_pagamento":
                    pagamento_atualizado[
                        "Status_do_Pagamento"
                    ]
            },

            "reserva": {
                "numero_da_reserva":
                    reserva_atualizada[
                        "Numero_da_Reserva"
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
            "erro":
                "Erro ao cancelar pagamento",
            "detalhes":
                str(erro)
        }), 500

    finally:

        banco_de_dados.close()