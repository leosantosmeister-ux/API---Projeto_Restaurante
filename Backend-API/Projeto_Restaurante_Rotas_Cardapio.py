from flask import Blueprint, request, jsonify

from Projeto_Restaurante_Banco_de_Dados import conexao_backend

rotas_cardapio = Blueprint('rotas_cardapio', __name__)

# ROTA PARA CADASTRAR ITEM NO CARDÁPIO

@rotas_cardapio.route('/cardapio', methods=['POST'])
def cadastrar_item_cardapio():

    """
    Cadastra um novo item no cardápio.

    ---
    tags:
      - Cardápio

    consumes:
      - application/json

    produces:
      - application/json

    parameters:
      - in: body
        name: item
        required: true
        schema:
          type: object
          required:
            - nome_do_item
            - categoria_do_item
            - valor_do_item
          properties:
            nome_do_item:
              type: string
              example: Prato Feito Tradicional
              description: Nome do item do cardápio.

            categoria_do_item:
              type: string
              example: Refeição
              description: Categoria do item.

            valor_do_item:
              type: number
              format: float
              example: 29.90
              description: Valor do item.

    responses:

      201:
        description: Item cadastrado com sucesso.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Item cadastrado com sucesso

            item:
              type: object
              properties:
                numero_do_item:
                  type: integer
                  example: 1

                nome_do_item:
                  type: string
                  example: Prato Feito Tradicional

                categoria_do_item:
                  type: string
                  example: Refeição

                valor_do_item:
                  type: number
                  format: float
                  example: 29.90

      400:
        description: Dados inválidos ou obrigatórios não informados.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: O valor do item deve ser maior que zero

            dados_faltantes:
              type: array
              items:
                type: string
              example:
                - nome_do_item

      409:
        description: Já existe um item cadastrado com o mesmo nome.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Já existe um item cadastrado com esse nome

      500:
        description: Erro ao cadastrar item.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao cadastrar item

            detalhes:
              type: string
              example: Erro interno do banco de dados
    """

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "erro": "Formato JSON inválido"
        }), 400

    campos_permitidos = {
        "nome_do_item",
        "categoria_do_item",
        "valor_do_item"
     }

    campos_recebidos = set(dados.keys())

    campos_invalidos = campos_recebidos - campos_permitidos

    if campos_invalidos:
        return jsonify({
            "erro": "Foram enviados dados inválidos",
         }), 400

    campos_obrigatorios = [
        "nome_do_item",
        "categoria_do_item",
        "valor_do_item"
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

    nome_do_item = dados["nome_do_item"]
    categoria_do_item = dados["categoria_do_item"]
    valor_do_item = dados["valor_do_item"]

    if not isinstance(nome_do_item, str) or not nome_do_item.strip():
        return jsonify({
            "erro": "O nome do item deve ser informado"
        }), 400

    nome_do_item = nome_do_item.strip()

    if not isinstance(categoria_do_item, str) or not categoria_do_item.strip():
        return jsonify({
            "erro": "A categoria do item deve ser informada"
        }), 400

    categoria_do_item = categoria_do_item.strip()

    try:
        valor_do_item = float(valor_do_item)
    except (TypeError, ValueError):
        return jsonify({
            "erro": "O valor do item deve ser numérico"
        }), 400

    if valor_do_item <= 0:
        return jsonify({
            "erro": "O valor do item deve ser maior que zero"
        }), 400

    banco_de_dados = conexao_backend()

    try:

        item_existente = banco_de_dados.execute(
            """
            SELECT Numero_do_Item
            FROM Cardapio
            WHERE Nome_do_Item = ?
            """,
            (nome_do_item,)
        ).fetchone()

        if item_existente:
            return jsonify({
                "erro": "Já existe um item cadastrado com esse nome"
            }), 409

        cursor = banco_de_dados.execute(
            """
            INSERT INTO Cardapio (
                Nome_do_Item,
                Categoria_do_Item,
                Valor_do_Item
            )
            VALUES (?, ?, ?)
            """,
            (
                nome_do_item,
                categoria_do_item,
                valor_do_item
            )
        )

        banco_de_dados.commit()

        numero_do_item = cursor.lastrowid

        return jsonify({
            "mensagem": "Item cadastrado com sucesso",
            "item": {
                "numero_do_item": numero_do_item,
                "nome_do_item": nome_do_item,
                "categoria_do_item": categoria_do_item,
                "valor_do_item": valor_do_item
            }
        }), 201

    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({
            "erro": "Erro ao cadastrar item",
            "detalhes": str(erro)
        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA CONSULTAR ITENS DO CARDÁPIO

@rotas_cardapio.route('/cardapio', methods=['GET'])
def consultar_cardapio():

    """
    Consulta os itens cadastrados no cardápio.

    Permite realizar a consulta sem filtros ou utilizando um ou mais
    parâmetros de pesquisa.

    ---
    tags:
      - Cardápio

    produces:
      - application/json

    parameters:

      - name: numero_do_item
        in: query
        type: integer
        required: false
        description: Número do item do cardápio.
        example: 1

      - name: nome_do_item
        in: query
        type: string
        required: false
        description: Nome ou parte do nome do item.
        example: Hambúrguer

      - name: categoria_do_item
        in: query
        type: string
        required: false
        description: Categoria do item.
        example: Refeição

      - name: valor_do_item
        in: query
        type: number
        format: float
        required: false
        description: Valor exato do item.
        example: 29.90

      - name: valor_minimo
        in: query
        type: number
        format: float
        required: false
        description: Valor mínimo dos itens.
        example: 20.00

      - name: valor_maximo
        in: query
        type: number
        format: float
        required: false
        description: Valor máximo dos itens.
        example: 50.00

    responses:

      200:
        description: Itens encontrados com sucesso.
        schema:
          type: array
          items:
            type: object
            properties:
              numero_do_item:
                type: integer
                example: 1

              nome_do_item:
                type: string
                example: Prato Feito Tradicional

              categoria_do_item:
                type: string
                example: Refeição

              valor_do_item:
                type: number
                format: float
                example: 29.90

      400:
        description: Parâmetros de pesquisa inválidos.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Valor mínimo não pode ser maior que o valor máximo

            Pesquisas Válidas:
              type: array
              items:
                type: string
              example:
                - numero_do_item
                - nome_do_item
                - categoria_do_item
                - valor_do_item
                - valor_minimo
                - valor_maximo

      404:
        description: Nenhum item encontrado ou categoria inexistente.
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Nenhum item encontrado

      500:
        description: Erro ao consultar cardápio.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao consultar cardápio

            detalhes:
              type: string
              example: Erro interno do banco de dados
    """

    pesquisa_permitida = {
        "numero_do_item",
        "nome_do_item",
        "categoria_do_item",
        "valor_do_item",
        "valor_minimo",
        "valor_maximo"
    }

    pesquisa_recebida = set(request.args.keys())

    pesquisa_invalida = pesquisa_recebida - pesquisa_permitida

    if pesquisa_invalida:
        return jsonify({
            "erro": "Pesquisa inválida",
            "Pesquisas Válidas": list(pesquisa_permitida)
        }), 400

    numero_do_item = request.args.get('numero_do_item')
    nome_do_item = request.args.get('nome_do_item')
    categoria_do_item = request.args.get('categoria_do_item')
    valor_do_item = request.args.get('valor_do_item')
    valor_minimo = request.args.get('valor_minimo')
    valor_maximo = request.args.get('valor_maximo')

    filtros = []
    parametros = []

    if numero_do_item is not None:

        if not numero_do_item:
                    return jsonify({
                        "erro": "O número do item não pode estar vazio"
                    }), 400

        try:
            numero_do_item = int(numero_do_item)
        except ValueError:
            return jsonify({
                "erro": "Número do item inválido"
            }), 400

        filtros.append("Numero_do_Item = ?")
        parametros.append(numero_do_item)

    if nome_do_item is not None:

        nome_do_item = nome_do_item.strip()

        if not nome_do_item:
            return jsonify({
                "erro": "O nome do item não pode estar vazio"
            }), 400

        filtros.append("Nome_do_Item LIKE ?")
        parametros.append(f"%{nome_do_item}%")

    if categoria_do_item is not None:

        categoria_do_item = categoria_do_item.strip()

        if not categoria_do_item:
            return jsonify({
                "erro": "A categoria do item não pode estar vazia"
            }), 400

        filtros.append("Categoria_do_Item = ?")
        parametros.append(categoria_do_item)

    if valor_do_item is not None:

        if not valor_do_item:
                    return jsonify({
                        "erro": "O valor do item não pode estar vazio"
                    }), 400

        try:
            valor_do_item = float(valor_do_item)
        except ValueError:
            return jsonify({
                "erro": "Valor do item inválido"
            }), 400

        if valor_do_item <= 0:
            return jsonify({
                "erro": "O valor do item deve ser maior que zero"
            }), 400

        filtros.append("Valor_do_Item = ?")
        parametros.append(valor_do_item)

    if valor_minimo is not None:

        try:
            valor_minimo = float(valor_minimo)
        except ValueError:
            return jsonify({
                "erro": "Valor mínimo inválido"
            }), 400

        if valor_minimo <= 0:
            return jsonify({
                "erro": "O valor mínimo deve ser maior que zero"
            }), 400

        filtros.append("Valor_do_Item >= ?")
        parametros.append(valor_minimo)

    if valor_maximo is not None:

        try:
            valor_maximo = float(valor_maximo)
        except ValueError:
            return jsonify({
                "erro": "Valor máximo inválido"
            }), 400

        if valor_maximo <= 0:
            return jsonify({
                "erro": "O valor máximo deve ser maior que zero"
            }), 400

        filtros.append("Valor_do_Item <= ?")
        parametros.append(valor_maximo)

    if valor_minimo is not None and valor_maximo is not None:

        if valor_minimo > valor_maximo:
            return jsonify({
                "erro": "O valor mínimo não pode ser maior que o valor máximo"
            }), 400

    banco_de_dados = conexao_backend()

    try:

        consulta = """
            SELECT
                Numero_do_Item,
                Nome_do_Item,
                Categoria_do_Item,
                Valor_do_Item
            FROM Cardapio
        """

        if filtros:
            consulta += " WHERE " + " AND ".join(filtros)

        consulta += " ORDER BY Numero_do_Item"

        itens = banco_de_dados.execute(
            consulta,
            parametros
        ).fetchall()

        if not itens:

            if categoria_do_item is not None:

                categoria_existente = banco_de_dados.execute(
                    """
                    SELECT 1
                    FROM Cardapio
                    WHERE Categoria_do_Item = ?
                    LIMIT 1
                    """,
                    (categoria_do_item,)
                ).fetchone()

                if categoria_existente is None:
                    return jsonify({
                        "mensagem": "Categoria inexistente"
                    }), 404
                
            return jsonify({
                "mensagem": "Nenhum item encontrado"
            }), 404

        resultado = []

        for item in itens:

            resultado.append({
                "numero_do_item": item["Numero_do_Item"],
                "nome_do_item": item["Nome_do_Item"],
                "categoria_do_item": item["Categoria_do_Item"],
                "valor_do_item": item["Valor_do_Item"]
            })

        return jsonify(resultado), 200

    except Exception as erro:

        return jsonify({
            "erro": "Erro ao consultar cardápio",
            "detalhes": str(erro)
        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA ATUALIZAR ITEM DO CARDÁPIO

@rotas_cardapio.route('/cardapio/<int:numero_do_item>', methods=['PUT'])
def atualizar_item_cardapio(numero_do_item):

    """
    Atualiza um item existente do cardápio.

    ---
    tags:
      - Cardápio

    consumes:
      - application/json

    produces:
      - application/json

    parameters:

      - name: numero_do_item
        in: path
        type: integer
        required: true
        description: Número do item que será atualizado.
        example: 1

      - in: body
        name: item
        required: true
        schema:
          type: object
          properties:

            nome_do_item:
              type: string
              example: Prato Feito Especial
              description: Novo nome do item.

            categoria_do_item:
              type: string
              example: Refeição
              description: Nova categoria do item.

            valor_do_item:
              type: number
              format: float
              example: 34.90
              description: Novo valor do item.

    responses:

      200:
        description: Item atualizado com sucesso.
        schema:
          type: object
          properties:

            mensagem:
              type: string
              example: Item atualizado com sucesso

            item:
              type: object
              properties:

                numero_do_item:
                  type: integer
                  example: 1

                nome_do_item:
                  type: string
                  example: Prato Feito Especial

                categoria_do_item:
                  type: string
                  example: Refeição

                valor_do_item:
                  type: number
                  format: float
                  example: 34.90

      400:
        description: Dados inválidos ou campos não permitidos.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: O valor do item deve ser maior que zero

            dados_válidos:
              type: array
              items:
                type: string
              example:
                - nome_do_item
                - categoria_do_item
                - valor_do_item

      404:
        description: Item não encontrado.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Item não encontrado

      409:
        description: Já existe outro item cadastrado com o mesmo nome.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Já existe outro item cadastrado com esse nome

      500:
        description: Erro ao atualizar item.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao atualizar item

            detalhes:
              type: string
              example: Erro interno do banco de dados
    """                        

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "erro": "Formato JSON inválido"
        }), 400

    campos_permitidos = {
        "nome_do_item",
        "categoria_do_item",
        "valor_do_item"
    }

    campos_recebidos = set(dados.keys())

    campos_invalidos = campos_recebidos - campos_permitidos

    if campos_invalidos:
        return jsonify({
            "erro": "Foram enviados dados inválidos",
            "dados_válidos": list(campos_permitidos)
        }), 400

    if not campos_recebidos:
        return jsonify({
            "erro": "Nenhum dado informado"
        }), 400

    banco_de_dados = conexao_backend()

    try:

        item_existente = banco_de_dados.execute(
            """
            SELECT
                Numero_do_Item,
                Nome_do_Item,
                Categoria_do_Item,
                Valor_do_Item
            FROM Cardapio
            WHERE Numero_do_Item = ?
            """,
            (numero_do_item,)
        ).fetchone()

        if item_existente is None:
            return jsonify({
                "erro": "Item não encontrado"
            }), 404

        nome_do_item = item_existente["Nome_do_Item"]
        categoria_do_item = item_existente["Categoria_do_Item"]
        valor_do_item = item_existente["Valor_do_Item"]

        if "nome_do_item" in dados:

            nome_do_item = dados["nome_do_item"]

            if not isinstance(nome_do_item, str) or not nome_do_item.strip():
                return jsonify({
                    "erro": "O nome do item deve ser informado"
                }), 400

            nome_do_item = nome_do_item.strip()

        if "categoria_do_item" in dados:

            categoria_do_item = dados["categoria_do_item"]

            if not isinstance(categoria_do_item, str) or not categoria_do_item.strip():
                return jsonify({
                    "erro": "A categoria do item deve ser informada"
                }), 400

            categoria_do_item = categoria_do_item.strip()

        if "valor_do_item" in dados:

            valor_recebido = dados["valor_do_item"]

            if isinstance(valor_recebido, str):
               valor_recebido = valor_recebido.strip()

            if valor_recebido == "":
                return jsonify({
                   "erro": "O valor do item deve ser preenchido"
                }), 400

            try:
                valor_do_item = float(valor_recebido)
            except (TypeError, ValueError):
                return jsonify({
                    "erro": "Valor do item inválido"
                }), 400

            if valor_do_item <= 0:
                return jsonify({
                    "erro": "O valor do item deve ser maior que zero"
                }), 400

        if nome_do_item != item_existente["Nome_do_Item"]:

            item_com_mesmo_nome = banco_de_dados.execute(
                """
                SELECT Numero_do_Item
                FROM Cardapio
                WHERE Nome_do_Item = ?
                AND Numero_do_Item != ?
                """,
                (
                    nome_do_item,
                    numero_do_item
                )
            ).fetchone()

            if item_com_mesmo_nome:
                return jsonify({
                    "erro": "Já existe outro item cadastrado com esse nome"
                }), 409

        banco_de_dados.execute(
            """
            UPDATE Cardapio
            SET
                Nome_do_Item = ?,
                Categoria_do_Item = ?,
                Valor_do_Item = ?
            WHERE Numero_do_Item = ?
            """,
            (
                nome_do_item,
                categoria_do_item,
                valor_do_item,
                numero_do_item
            )
        )

        banco_de_dados.commit()

        return jsonify({
            "mensagem": "Item atualizado com sucesso",
            "item": {
                "numero_do_item": numero_do_item,
                "nome_do_item": nome_do_item,
                "categoria_do_item": categoria_do_item,
                "valor_do_item": valor_do_item
            }
        }), 200

    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({
            "erro": "Erro ao atualizar item",
            "detalhes": str(erro)
        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA EXCLUIR ITEM DO CARDÁPIO

@rotas_cardapio.route('/cardapio/<int:numero_do_item>', methods=['DELETE'])
def excluir_item_cardapio(numero_do_item):

    """
    Exclui um item cadastrado no cardápio.

    ---
    tags:
      - Cardápio

    produces:
      - application/json

    parameters:

      - name: numero_do_item
        in: path
        type: integer
        required: true
        description: Número do item que será excluído.
        example: 1

    responses:

      200:
        description: Item excluído com sucesso.
        schema:
          type: object
          properties:

            mensagem:
              type: string
              example: Item excluído com sucesso

            item:
              type: object
              properties:

                numero_do_item:
                  type: integer
                  example: 1

                nome_do_item:
                  type: string
                  example: Prato Feito Tradicional

                categoria_do_item:
                  type: string
                  example: Refeição

                valor_do_item:
                  type: number
                  format: float
                  example: 29.90

      404:
        description: Item não encontrado.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Item não encontrado

      500:
        description: Erro ao excluir item.
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Erro ao excluir item

            detalhes:
              type: string
              example: Erro interno do banco de dados
    """

    banco_de_dados = conexao_backend()

    try:

        item_existente = banco_de_dados.execute(
            """
            SELECT
                Numero_do_Item,
                Nome_do_Item,
                Categoria_do_Item,
                Valor_do_Item
            FROM Cardapio
            WHERE Numero_do_Item = ?
            """,
            (numero_do_item,)
        ).fetchone()

        if item_existente is None:
            return jsonify({
                "erro": "Item não encontrado"
            }), 404

        banco_de_dados.execute(
            """
            DELETE FROM Cardapio
            WHERE Numero_do_Item = ?
            """,
            (numero_do_item,)
        )

        banco_de_dados.commit()

        return jsonify({
            "mensagem": "Item excluído com sucesso",
            "item": {
                "numero_do_item": item_existente["Numero_do_Item"],
                "nome_do_item": item_existente["Nome_do_Item"],
                "categoria_do_item": item_existente["Categoria_do_Item"],
                "valor_do_item": item_existente["Valor_do_Item"]
            }
        }), 200

    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({
            "erro": "Erro ao excluir item",
            "detalhes": str(erro)
        }), 500

    finally:

        banco_de_dados.close()