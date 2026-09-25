from flask import Blueprint, request, jsonify
from Projeto_Restaurante_Banco_de_Dados import conexao_backend

rotas_itens_da_reserva = Blueprint('rotas_itens_da_reserva', __name__)

# ROTA PARA ADICIONAR ITEM À RESERVA

@rotas_itens_da_reserva.route('/reservas/<int:numero_da_reserva>/itens',methods=['POST'])
def adicionar_item_na_reserva(numero_da_reserva):

    """
Adiciona um item do cardápio a uma reserva.

O item só pode ser adicionado enquanto a reserva estiver com
status PENDENTE.

---

tags:
  - Itens da Reserva

consumes:
  - application/json

produces:
  - application/json

parameters:
  - name: numero_da_reserva
    in: path
    type: integer
    required: true
    description: Número da reserva que receberá o item.
    example: 1

  - in: body
    name: item
    required: true
    schema:
      type: object
      required:
        - numero_do_item
        - quantidade_de_itens
      properties:
        numero_do_item:
          type: integer
          example: 1
          description: Número do item existente no cardápio.

        quantidade_de_itens:
          type: integer
          example: 2
          description: Quantidade do item que será adicionada à reserva.

responses:
  201:
    description: Item adicionado à reserva com sucesso.
    schema:
      type: object
      properties:
        mensagem:
          type: string
          example: Item adicionado à reserva com sucesso

        item:
          type: object
          properties:
            id_itens_da_reserva:
              type: integer
              example: 1

            numero_da_reserva:
              type: integer
              example: 1

            numero_do_item:
              type: integer
              example: 1

            nome_do_item_na_reserva:
              type: string
              example: Prato Feito Tradicional

            categoria_do_item_na_reserva:
              type: string
              example: Refeição

            valor_do_item_na_reserva:
              type: number
              format: float
              example: 29.90

            quantidade_de_itens:
              type: integer
              example: 2

  400:
    description: Dados inválidos ou reserva não permite receber itens.
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Somente reservas PENDENTES podem receber itens

  404:
    description: Reserva ou item não encontrado.
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Reserva não encontrada

  409:
    description: Item já está adicionado à reserva.
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Este item já está adicionado à reserva

        quantidade_atual:
          type: integer
          example: 2

  500:
    description: Erro ao adicionar item à reserva.
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Erro ao adicionar item à reserva

        detalhes:
          type: string
          example: Erro interno do banco de dados
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
        "numero_do_item",
        "quantidade_de_itens"
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

    campos_obrigatorios = {
        "numero_do_item",
        "quantidade_de_itens"
    }


    campos_faltando = (
        campos_obrigatorios - campos_recebidos
    )

    if campos_faltando:

        return jsonify({

            "erro": "Campo(s) obrigatório(s) não informado(s)",

            "campos_não_informados":
                list(campos_faltando)

        }), 400

    numero_do_item = dados["numero_do_item"]
    quantidade_de_itens = dados["quantidade_de_itens"]

    if isinstance(numero_do_item, bool):

        return jsonify({
            "erro": "Número do item inválido"
        }), 400

    try:

        numero_do_item = int(numero_do_item)

    except (TypeError, ValueError):

        return jsonify({
            "erro": "Número do item inválido"
        }), 400


    if numero_do_item <= 0:

        return jsonify({
            "erro": "O número do item deve ser maior que zero"
        }), 400

    if isinstance(quantidade_de_itens, bool):

        return jsonify({
            "erro": "Quantidade de itens inválida"
        }), 400


    try:

        quantidade_de_itens = int(quantidade_de_itens)

    except (TypeError, ValueError):

        return jsonify({
            "erro": "Quantidade de itens inválida"
        }), 400


    if quantidade_de_itens <= 0:

        return jsonify({
            "erro": "A quantidade de itens deve ser maior que zero"
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

        if reserva["Status_da_Reserva"] != "PENDENTE":
             
             return jsonify({
              "erro":"Somente reservas PENDENTES podem receber itens"
             }), 400

        item = banco_de_dados.execute(
            '''
            SELECT
                Numero_do_Item,
                Nome_do_Item,
                Categoria_do_Item,
                Valor_do_Item

            FROM Cardapio

            WHERE Numero_do_Item = ?
            ''',
            (numero_do_item,)
        ).fetchone()

        if item is None:

            return jsonify({
                "erro": "Item não encontrado no cardápio"
            }), 404

        item_existente = banco_de_dados.execute(
            '''
            SELECT
                ID_Itens_da_Reserva,
                Quantidade_de_Itens

            FROM Itens_da_Reserva

            WHERE Numero_da_Reserva = ?

            AND Numero_do_Item = ?
            ''',
            (
                numero_da_reserva,
                numero_do_item
            )
        ).fetchone()

        if item_existente is not None:

            return jsonify({

                "erro":
                    "Este item já está adicionado à reserva",

                "quantidade_atual":
                    item_existente[
                        "Quantidade_de_Itens"
                    ]

            }), 409

        banco_de_dados.execute(
            '''
            INSERT INTO Itens_da_Reserva (
                Numero_da_Reserva,
                Numero_do_Item,
                Nome_do_Item_na_Reserva,
                Categoria_do_Item_na_Reserva,
                Valor_do_Item_na_Reserva,
                Quantidade_de_Itens
            )

            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                numero_da_reserva,
                item["Numero_do_Item"],
                item["Nome_do_Item"],
                item["Categoria_do_Item"],
                item["Valor_do_Item"],
                quantidade_de_itens
            )
        )

        banco_de_dados.commit()

        item_adicionado = banco_de_dados.execute(
            '''
            SELECT
                ID_Itens_da_Reserva,
                Numero_da_Reserva,
                Numero_do_Item,
                Nome_do_Item_na_Reserva,
                Categoria_do_Item_na_Reserva,
                Valor_do_Item_na_Reserva,
                Quantidade_de_Itens

            FROM Itens_da_Reserva

            WHERE Numero_da_Reserva = ?

            AND Numero_do_Item = ?
            ''',
            (
                numero_da_reserva,
                numero_do_item
            )
        ).fetchone()

        return jsonify({

            "mensagem":
                "Item adicionado à reserva com sucesso",

            "item": {

                "id_itens_da_reserva":
                    item_adicionado[
                        "ID_Itens_da_Reserva"
                    ],

                "numero_da_reserva":
                    item_adicionado[
                        "Numero_da_Reserva"
                    ],

                "numero_do_item":
                    item_adicionado[
                        "Numero_do_Item"
                    ],

                "nome_do_item_na_reserva":
                    item_adicionado[
                        "Nome_do_Item_na_Reserva"
                    ],

                "categoria_do_item_na_reserva":
                    item_adicionado[
                        "Categoria_do_Item_na_Reserva"
                    ],

                "valor_do_item_na_reserva":
                    item_adicionado[
                        "Valor_do_Item_na_Reserva"
                    ],

                "quantidade_de_itens":
                    item_adicionado[
                        "Quantidade_de_Itens"
                    ]
            }

        }), 201

    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({

            "erro": "Erro ao adicionar item à reserva",

            "detalhes": str(erro)

        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA CONSULTAR OS ITENS DA RESERVA

@rotas_itens_da_reserva.route('/reservas/<int:numero_da_reserva>/itens',methods=['GET'])
def consultar_itens_da_reserva(numero_da_reserva):

    """
    Consulta todos os itens adicionados a uma reserva.

    ---
    tags:
      - Itens da Reserva

    produces:
      - application/json

    parameters:

      - name: numero_da_reserva
        in: path
        type: integer
        required: true
        description: Número da reserva que será consultada.
        example: 1

    responses:

      200:
        description: Itens da reserva consultados com sucesso.
        schema:
          type: object
          properties:

            numero_da_reserva:
              type: integer
              example: 1

            status_da_reserva:
              type: string
              example: PENDENTE

            itens:
              type: array
              items:
                type: object
                properties:

                  id_itens_da_reserva:
                    type: integer
                    example: 1

                  numero_da_reserva:
                    type: integer
                    example: 1

                  numero_do_item:
                    type: integer
                    example: 1

                  nome_do_item_na_reserva:
                    type: string
                    example: Prato Feito Tradicional

                  categoria_do_item_na_reserva:
                    type: string
                    example: Refeição

                  valor_do_item_na_reserva:
                    type: number
                    format: float
                    example: 29.90

                  quantidade_de_itens:
                    type: integer
                    example: 2

                  subtotal:
                    type: number
                    format: float
                    example: 59.80

      400:
        description: Número da reserva inválido.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Número da reserva inválido

      404:
        description: Reserva não encontrada.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Reserva não encontrada

      500:
        description: Erro ao consultar os itens da reserva.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: Erro ao consultar os itens da reserva

            detalhes:
              type: string
              example: Erro interno do banco de dados
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

        itens = banco_de_dados.execute(
            '''
            SELECT
                ID_Itens_da_Reserva,
                Numero_da_Reserva,
                Numero_do_Item,
                Nome_do_Item_na_Reserva,
                Categoria_do_Item_na_Reserva,
                Valor_do_Item_na_Reserva,
                Quantidade_de_Itens
            FROM Itens_da_Reserva
            WHERE Numero_da_Reserva = ?
            ORDER BY ID_Itens_da_Reserva
            ''',
            (numero_da_reserva,)
        ).fetchall()

        lista_de_itens = []

        for item in itens:

            subtotal = (
                item["Valor_do_Item_na_Reserva"]
                *
                item["Quantidade_de_Itens"]
            )

            lista_de_itens.append({
                "id_itens_da_reserva":
                    item["ID_Itens_da_Reserva"],

                "numero_da_reserva":
                    item["Numero_da_Reserva"],

                "numero_do_item":
                    item["Numero_do_Item"],

                "nome_do_item_na_reserva":
                    item["Nome_do_Item_na_Reserva"],

                "categoria_do_item_na_reserva":
                    item["Categoria_do_Item_na_Reserva"],

                "valor_do_item_na_reserva":
                    item["Valor_do_Item_na_Reserva"],

                "quantidade_de_itens":
                    item["Quantidade_de_Itens"],

                "subtotal":
                    subtotal
            })

        return jsonify({
            "numero_da_reserva":
                numero_da_reserva,

            "status_da_reserva":
                reserva["Status_da_Reserva"],

            "itens":
                lista_de_itens
        }), 200

    except Exception as erro:

        return jsonify({
            "erro": "Erro ao consultar os itens da reserva",
            "detalhes": str(erro)
        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA ALTERAR A QUANTIDADE DE UM ITEM DA RESERVA

@rotas_itens_da_reserva.route('/reservas/<int:numero_da_reserva>/itens/<int:numero_do_item>',methods=['PUT'])
def atualizar_quantidade_item(numero_da_reserva,numero_do_item):

    """
Altera a quantidade de um item já adicionado a uma reserva.

A quantidade do item só pode ser alterada enquanto a reserva estiver
com status PENDENTE.

---

tags:
  - Itens da Reserva

consumes:
  - application/json

produces:
  - application/json

parameters:
  - name: numero_da_reserva
    in: path
    type: integer
    required: true
    description: Número da reserva que terá o item alterado.
    example: 1

  - name: numero_do_item
    in: path
    type: integer
    required: true
    description: Número do item do cardápio que será alterado.
    example: 1

  - in: body
    name: item
    required: true
    schema:
      type: object
      required:
        - quantidade_de_itens
      properties:
        quantidade_de_itens:
          type: integer
          example: 3
          description: Nova quantidade do item na reserva.

responses:
  200:
    description: Quantidade do item alterada com sucesso.
    schema:
      type: object
      properties:
        mensagem:
          type: string
          example: Quantidade do item alterada com sucesso

        item:
          type: object
          properties:
            id_itens_da_reserva:
              type: integer
              example: 1

            numero_da_reserva:
              type: integer
              example: 1

            numero_do_item:
              type: integer
              example: 1

            nome_do_item_na_reserva:
              type: string
              example: Prato Feito Tradicional

            categoria_do_item_na_reserva:
              type: string
              example: Refeição

            valor_do_item_na_reserva:
              type: number
              format: float
              example: 29.90

            quantidade_de_itens:
              type: integer
              example: 3

  400:
    description: Dados inválidos ou reserva não permite alteração dos itens.
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Somente reservas PENDENTES podem ter seus itens alterados

  404:
    description: Reserva ou item não encontrado.
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Item não encontrado na reserva

  500:
    description: Erro ao alterar item da reserva.
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Erro ao alterar item da reserva

        detalhes:
          type: string
          example: Erro interno do banco de dados
"""

    if numero_da_reserva <= 0:

        return jsonify({
            "erro": "Número da reserva inválido"
        }), 400

    if numero_do_item <= 0:

        return jsonify({
            "erro": "Número do item inválido"
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

    campos_permitidos = {"quantidade_de_itens"}

    campos_recebidos = set(dados.keys())

    campos_invalidos = (campos_recebidos - campos_permitidos)

    if campos_invalidos:

        return jsonify({
            "erro": "Campo(s) não permitido(s)",
            "campos_invalidos":
                list(campos_invalidos),
            "campos_permitidos":
                list(campos_permitidos)
        }), 400

    if "quantidade_de_itens" not in campos_recebidos:

        return jsonify({
            "erro":
                "Campo quantidade_de_itens não informado"
        }), 400

    quantidade_de_itens = dados["quantidade_de_itens"]

    if isinstance(quantidade_de_itens, bool):

        return jsonify({
            "erro": "Quantidade de itens inválida"
        }), 400

    try:

        quantidade_de_itens = int(quantidade_de_itens)

    except (TypeError, ValueError):

        return jsonify({
            "erro": "Quantidade de itens inválida"
        }), 400

    if quantidade_de_itens <= 0:

        return jsonify({
            "erro":
                "A quantidade de itens deve ser maior que zero"
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

        if reserva["Status_da_Reserva"] != "PENDENTE":

            return jsonify({
            "erro":"Somente reservas PENDENTES podem ter seus itens alterados"
             }), 400

        item = banco_de_dados.execute(
            '''
            SELECT
                ID_Itens_da_Reserva,
                Numero_da_Reserva,
                Numero_do_Item,
                Nome_do_Item_na_Reserva,
                Categoria_do_Item_na_Reserva,
                Valor_do_Item_na_Reserva,
                Quantidade_de_Itens
            FROM Itens_da_Reserva
            WHERE Numero_da_Reserva = ?
            AND Numero_do_Item = ?
            ''',
            (
                numero_da_reserva,
                numero_do_item
            )
        ).fetchone()

        if item is None:

            return jsonify({
                "erro":
                    "Item não encontrado na reserva"
            }), 404

        banco_de_dados.execute(
            '''
            UPDATE Itens_da_Reserva
            SET Quantidade_de_Itens = ?
            WHERE Numero_da_Reserva = ?
            AND Numero_do_Item = ?
            ''',
            (
                quantidade_de_itens,
                numero_da_reserva,
                numero_do_item
            )
        )

        banco_de_dados.commit()

        item_atualizado = banco_de_dados.execute(
            '''
            SELECT
                ID_Itens_da_Reserva,
                Numero_da_Reserva,
                Numero_do_Item,
                Nome_do_Item_na_Reserva,
                Categoria_do_Item_na_Reserva,
                Valor_do_Item_na_Reserva,
                Quantidade_de_Itens
            FROM Itens_da_Reserva
            WHERE Numero_da_Reserva = ?
            AND Numero_do_Item = ?
            ''',
            (
                numero_da_reserva,
                numero_do_item
            )
        ).fetchone()

        subtotal = (
            item_atualizado[
                "Valor_do_Item_na_Reserva"
            ]
            *
            item_atualizado[
                "Quantidade_de_Itens"
            ]
        )

        return jsonify({
            "mensagem":
                "Quantidade do item atualizada com sucesso",

            "item": {
                "id_itens_da_reserva":
                    item_atualizado[
                        "ID_Itens_da_Reserva"
                    ],

                "numero_da_reserva":
                    item_atualizado[
                        "Numero_da_Reserva"
                    ],

                "numero_do_item":
                    item_atualizado[
                        "Numero_do_Item"
                    ],

                "nome_do_item_na_reserva":
                    item_atualizado[
                        "Nome_do_Item_na_Reserva"
                    ],

                "categoria_do_item_na_reserva":
                    item_atualizado[
                        "Categoria_do_Item_na_Reserva"
                    ],

                "valor_do_item_na_reserva":
                    item_atualizado[
                        "Valor_do_Item_na_Reserva"
                    ],

                "quantidade_de_itens":
                    item_atualizado[
                        "Quantidade_de_Itens"
                    ],

                "subtotal":
                    subtotal
            }
        }), 200

    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({
            "erro":
                "Erro ao atualizar a quantidade do item",
            "detalhes":
                str(erro)
        }), 500

    finally:

        banco_de_dados.close()


# ROTA PARA REMOVER ITEM DA RESERVA

@rotas_itens_da_reserva.route('/reservas/<int:numero_da_reserva>/itens/<int:numero_do_item>',methods=['DELETE'])
def remover_item_da_reserva(numero_da_reserva,numero_do_item):

    """
Remove um item da reserva.

O item só pode ser removido enquanto a reserva estiver com status
PENDENTE.

---

tags:
  - Itens da Reserva

produces:
  - application/json

parameters:
  - name: numero_da_reserva
    in: path
    type: integer
    required: true
    description: Número da reserva da qual o item será removido.
    example: 1

  - name: numero_do_item
    in: path
    type: integer
    required: true
    description: Número do item do cardápio que será removido.
    example: 1

responses:
  200:
    description: Item removido da reserva com sucesso.
    schema:
      type: object
      properties:
        mensagem:
          type: string
          example: Item removido da reserva com sucesso

        item_removido:
          type: object
          properties:
            id_itens_da_reserva:
              type: integer
              example: 1

            numero_da_reserva:
              type: integer
              example: 1

            numero_do_item:
              type: integer
              example: 1

            nome_do_item_na_reserva:
              type: string
              example: Prato Feito Tradicional

            categoria_do_item_na_reserva:
              type: string
              example: Refeição

            valor_do_item_na_reserva:
              type: number
              format: float
              example: 29.90

            quantidade_de_itens:
              type: integer
              example: 2

  400:
    description: Reserva não permite a remoção do item.
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Somente reservas PENDENTES podem ter seus itens removidos

  404:
    description: Reserva ou item não encontrado.
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Item não encontrado na reserva

  500:
    description: Erro ao remover item da reserva.
    schema:
      type: object
      properties:
        erro:
          type: string
          example: Erro ao remover item da reserva

        detalhes:
          type: string
          example: Erro interno do banco de dados
"""

    if numero_da_reserva <= 0:
        return jsonify({
            "erro": "Número da reserva inválido"
        }), 400

    if numero_do_item <= 0:
        return jsonify({
            "erro": "Número do item inválido"
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

        if reserva["Status_da_Reserva"] != "PENDENTE":
            return jsonify({
             "erro": "Somente reservas PENDENTES podem ter seus itens removidos"
            }), 400

        item = banco_de_dados.execute(
            '''
            SELECT
                ID_Itens_da_Reserva,
                Numero_da_Reserva,
                Numero_do_Item,
                Nome_do_Item_na_Reserva,
                Categoria_do_Item_na_Reserva,
                Valor_do_Item_na_Reserva,
                Quantidade_de_Itens
            FROM Itens_da_Reserva
            WHERE Numero_da_Reserva = ?
            AND Numero_do_Item = ?
            ''',
            (
                numero_da_reserva,
                numero_do_item
            )
        ).fetchone()

        if item is None:

            return jsonify({
                "erro":
                    "Item não encontrado na reserva"
            }), 404

        banco_de_dados.execute(
            '''
            DELETE FROM Itens_da_Reserva
            WHERE Numero_da_Reserva = ?
            AND Numero_do_Item = ?
            ''',
            (
                numero_da_reserva,
                numero_do_item
            )
        )

        banco_de_dados.commit()

        subtotal = (
            item["Valor_do_Item_na_Reserva"]
            *
            item["Quantidade_de_Itens"]
        )

        return jsonify({
            "mensagem":
                "Item removido da reserva com sucesso",

            "item_removido": {
                "id_itens_da_reserva":
                    item["ID_Itens_da_Reserva"],

                "numero_da_reserva":
                    item["Numero_da_Reserva"],

                "numero_do_item":
                    item["Numero_do_Item"],

                "nome_do_item_na_reserva":
                    item["Nome_do_Item_na_Reserva"],

                "categoria_do_item_na_reserva":
                    item["Categoria_do_Item_na_Reserva"],

                "valor_do_item_na_reserva":
                    item["Valor_do_Item_na_Reserva"],

                "quantidade_de_itens":
                    item["Quantidade_de_Itens"],

                "subtotal":
                    subtotal
            }
        }), 200

    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({
            "erro":
                "Erro ao remover item da reserva",
            "detalhes":
                str(erro)
        }), 500

    finally:

        banco_de_dados.close()