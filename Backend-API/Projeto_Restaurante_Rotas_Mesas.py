from flask import Blueprint, request, jsonify

from Projeto_Restaurante_Banco_de_Dados import conexao_backend

rotas_mesas = Blueprint('rotas_mesas', __name__)

# ROTA PARA ADICIONAR MESAS

@rotas_mesas.route('/mesas', methods=['POST'])
def cadastrar_mesa():

    """
    Cadastra uma nova mesa no restaurante.

    ---
    tags:
      - Mesas

    consumes:
      - application/json

    produces:
      - application/json

    parameters:

      - in: body
        name: mesa
        required: true
        schema:
          type: object
          required:
            - numero_da_mesa
            - capacidade_da_mesa
          properties:

            numero_da_mesa:
              type: integer
              example: 10
              description: Número da mesa.

            capacidade_da_mesa:
              type: integer
              example: 4
              description: Quantidade de pessoas que a mesa comporta.

    responses:

      201:
        description: Mesa cadastrada com sucesso.
        schema:
          type: object
          properties:

            mensagem:
              type: string
              example: Mesa cadastrada com sucesso

            mesa:
              type: object
              properties:

                numero_da_mesa:
                  type: integer
                  example: 10

                capacidade_da_mesa:
                  type: integer
                  example: 4

      400:
        description: Dados inválidos ou obrigatórios não informados.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: A capacidade da mesa deve ser maior que zero

            dados_faltantes:
              type: array
              items:
                type: string
              example:
                - numero_da_mesa

            dados_válidos:
              type: array
              items:
                type: string
              example:
                - numero_da_mesa
                - capacidade_da_mesa

      409:
        description: Já existe uma mesa cadastrada com esse número.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: Já existe uma mesa cadastrada com esse número

      500:
        description: Erro ao cadastrar mesa.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: Erro ao cadastrar mesa

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
        "numero_da_mesa",
        "capacidade_da_mesa"
    }

    campos_recebidos = set(dados.keys())

    campos_invalidos = campos_recebidos - campos_permitidos

    if campos_invalidos:
        return jsonify({
            "erro": "Foram enviados dados inválidos",
            "dados_válidos": list(campos_permitidos)
        }), 400

    campos_obrigatorios = [
        "numero_da_mesa",
        "capacidade_da_mesa"
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

    numero_da_mesa = dados["numero_da_mesa"]
    capacidade_da_mesa = dados["capacidade_da_mesa"]

    if isinstance(numero_da_mesa, bool):
     return jsonify({
        "erro": "Número da mesa inválido"
    }), 400

    try:
        numero_da_mesa = int(numero_da_mesa)

        if float(numero_da_mesa) != float(dados["numero_da_mesa"]):
             return jsonify({
               "erro": "Número da mesa inválido"
            }), 400

    except (TypeError, ValueError):
        return jsonify({
            "erro": "Número da mesa inválido"
        }), 400

    if numero_da_mesa <= 0:
        return jsonify({
            "erro": "O número da mesa deve ser maior que zero"
        }), 400

    if isinstance(capacidade_da_mesa, bool):
         return jsonify({
            "erro": "Capacidade da mesa inválida"
        }), 400
     
    try:
        capacidade_da_mesa = int(capacidade_da_mesa)

        if float(capacidade_da_mesa) != float(dados["capacidade_da_mesa"]):
             return jsonify({
              "erro": "Capacidade da mesa inválida"
            }), 400
    
    except (TypeError, ValueError):
        return jsonify({
            "erro": "Capacidade da mesa inválida"
        }), 400

    if capacidade_da_mesa <= 0:
        return jsonify({
            "erro": "A capacidade da mesa deve ser maior que zero"
        }), 400

    banco_de_dados = conexao_backend()

    try:

        mesa_existente = banco_de_dados.execute(
            """
            SELECT Numero_da_Mesa
            FROM Mesa
            WHERE Numero_da_Mesa = ?
            """,
            (numero_da_mesa,)
        ).fetchone()

        if mesa_existente:
            return jsonify({
                "erro": "Já existe uma mesa cadastrada com esse número"
            }), 409

        banco_de_dados.execute(
            """
            INSERT INTO Mesa (
                Numero_da_Mesa,
                Capacidade_da_Mesa
            )
            VALUES (?, ?)
            """,
            (
                numero_da_mesa,
                capacidade_da_mesa
            )
        )

        banco_de_dados.commit()

        return jsonify({
            "mensagem": "Mesa cadastrada com sucesso",
            "mesa": {
                "numero_da_mesa": numero_da_mesa,
                "capacidade_da_mesa": capacidade_da_mesa
            }
        }), 201

    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({
            "erro": "Erro ao cadastrar mesa",
            "detalhes": str(erro)
        }), 500

    finally:

        banco_de_dados.close()


# ROTA PARA CONSULTAR MESAS

@rotas_mesas.route('/mesas', methods=['GET'])
def consultar_mesas():

    """
    Consulta as mesas cadastradas no restaurante.

    Permite consultar todas as mesas ou utilizar filtros
    pelo número ou pela capacidade da mesa.

    ---
    tags:
      - Mesas

    produces:
      - application/json

    parameters:

      - name: numero_da_mesa
        in: query
        type: integer
        required: false
        description: Número da mesa que será pesquisada.
        example: 10

      - name: capacidade_da_mesa
        in: query
        type: integer
        required: false
        description: Capacidade da mesa que será pesquisada.
        example: 4

    responses:

      200:
        description: Mesas encontradas com sucesso.
        schema:
          type: array
          items:
            type: object
            properties:

              numero_da_mesa:
                type: integer
                example: 10

              capacidade_da_mesa:
                type: integer
                example: 4

      400:
        description: Parâmetros de pesquisa inválidos.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: Capacidade da mesa inválida

            Pesquisas Válidas:
              type: array
              items:
                type: string
              example:
                - numero_da_mesa
                - capacidade_da_mesa

      404:
        description: Nenhuma mesa encontrada.
        schema:
          type: object
          properties:

            mensagem:
              type: string
              example: Nenhuma mesa encontrada

      500:
        description: Erro ao consultar mesas.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: Erro ao consultar mesas

            detalhes:
              type: string
              example: Erro interno do banco de dados
    """

    pesquisa_permitida = {
        "numero_da_mesa",
        "capacidade_da_mesa"
    }

    pesquisa_recebida = set(request.args.keys())

    pesquisa_invalida = pesquisa_recebida - pesquisa_permitida

    if pesquisa_invalida:
        return jsonify({
            "erro": "Pesquisa inválida",
            "Pesquisas Válidas": list(pesquisa_permitida)
        }), 400

    numero_da_mesa = request.args.get('numero_da_mesa')
    capacidade_da_mesa = request.args.get('capacidade_da_mesa')

    filtros = []
    parametros = []

    if numero_da_mesa is not None:

        if not numero_da_mesa:
            return jsonify({
                "erro": "Informe o número da mesa"
            }), 400

        try:
            numero_da_mesa = int(numero_da_mesa)
        except ValueError:
            return jsonify({
                "erro": "Número da mesa inválido"
            }), 400

        filtros.append("Numero_da_Mesa = ?")
        parametros.append(numero_da_mesa)

    if capacidade_da_mesa is not None:

        if not capacidade_da_mesa:
            return jsonify({
                "erro": "Informe a capacidade da mesa"
            }), 400

        try:
            capacidade_da_mesa = int(capacidade_da_mesa)
        except ValueError:
            return jsonify({
                "erro": "Capacidade da mesa inválida"
            }), 400

        if capacidade_da_mesa <= 0:
            return jsonify({
                "erro": "A capacidade da mesa deve ser maior que zero"
            }), 400

        filtros.append("Capacidade_da_Mesa = ?")
        parametros.append(capacidade_da_mesa)

    banco_de_dados = conexao_backend()

    try:

        consulta = """
            SELECT
                Numero_da_Mesa,
                Capacidade_da_Mesa
            FROM Mesa
        """

        if filtros:
            consulta += " WHERE " + " AND ".join(filtros)

        consulta += " ORDER BY Numero_da_Mesa"

        mesas = banco_de_dados.execute(
            consulta,
            parametros
        ).fetchall()

        if not mesas:
            return jsonify({
                "mensagem": "Nenhuma mesa encontrada"
            }), 404

        resultado = []

        for mesa in mesas:
            resultado.append({
                "numero_da_mesa": mesa["Numero_da_Mesa"],
                "capacidade_da_mesa": mesa["Capacidade_da_Mesa"]
            })

        return jsonify(resultado), 200

    except Exception as erro:

        return jsonify({
            "erro": "Erro ao consultar mesas",
            "detalhes": str(erro)
        }), 500

    finally:

        banco_de_dados.close()

# ROTA PARA ATUALIZAR MESAS

@rotas_mesas.route('/mesas/<numero_da_mesa>', methods=['PUT'])
def atualizar_mesa(numero_da_mesa):

    """
    Atualiza os dados de uma mesa existente.

    Permite alterar o número da mesa, a capacidade da mesa
    ou ambos os dados.

    ---
    tags:
      - Mesas

    consumes:
      - application/json

    produces:
      - application/json

    parameters:

      - name: numero_da_mesa
        in: path
        type: string
        required: true
        description: Número atual da mesa que será atualizada.
        example: "10"

      - in: body
        name: mesa
        required: true
        schema:
          type: object
          properties:

            numero_da_mesa:
              type: integer
              example: 11
              description: Novo número da mesa.

            capacidade_da_mesa:
              type: integer
              example: 6
              description: Nova capacidade da mesa.

    responses:

      200:
        description: Mesa atualizada com sucesso.
        schema:
          type: object
          properties:

            mensagem:
              type: string
              example: Mesa atualizada com sucesso

            mesa:
              type: object
              properties:

                numero_da_mesa:
                  type: integer
                  example: 11

                capacidade_da_mesa:
                  type: integer
                  example: 6

      400:
        description: Dados inválidos ou nenhum dado informado.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: O número da mesa deve ser maior que zero

            dados_válidos:
              type: array
              items:
                type: string
              example:
                - numero_da_mesa
                - capacidade_da_mesa

      404:
        description: Mesa não encontrada.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: Mesa não encontrada

      409:
        description: Já existe outra mesa cadastrada com o número informado.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: Já existe uma mesa cadastrada com esse número

      500:
        description: Erro ao atualizar mesa.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: Erro ao atualizar mesa

            detalhes:
              type: string
              example: Erro interno do banco de dados
    """

    try:
        numero_convertido = int(numero_da_mesa)

        if str(numero_convertido) != numero_da_mesa:
            return jsonify({
                "erro": "Número da mesa inválido"
            }), 400

        numero_da_mesa = numero_convertido

    except (TypeError, ValueError):
        return jsonify({
            "erro": "Número da mesa inválido"
        }), 400

    if numero_da_mesa <= 0:
        return jsonify({
            "erro": "O número da mesa deve ser maior que zero"
        }), 400

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "erro": "Formato JSON inválido"
        }), 400

    campos_permitidos = {
        "numero_da_mesa",
        "capacidade_da_mesa"
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

    novo_numero_da_mesa = numero_da_mesa

    if "numero_da_mesa" in dados:

        novo_numero_da_mesa = dados["numero_da_mesa"]

        if isinstance(novo_numero_da_mesa, bool):
            return jsonify({
                "erro": "Número da mesa inválido"
            }), 400

        try:
            numero_convertido = int(novo_numero_da_mesa)

            if float(numero_convertido) != float(novo_numero_da_mesa):
                return jsonify({
                    "erro": "Número da mesa inválido"
                }), 400

            novo_numero_da_mesa = numero_convertido

        except (TypeError, ValueError):
            return jsonify({
                "erro": "Número da mesa inválido"
            }), 400

        if novo_numero_da_mesa <= 0:
            return jsonify({
                "erro": "O número da mesa deve ser maior que zero"
            }), 400

    capacidade_da_mesa = None

    if "capacidade_da_mesa" in dados:

        capacidade_da_mesa = dados["capacidade_da_mesa"]

        if isinstance(capacidade_da_mesa, bool):
            return jsonify({
                "erro": "Capacidade da mesa inválida"
            }), 400

        try:
            capacidade_convertida = int(capacidade_da_mesa)

            if float(capacidade_convertida) != float(capacidade_da_mesa):
                return jsonify({
                    "erro": "Capacidade da mesa inválida"
                }), 400

            capacidade_da_mesa = capacidade_convertida

        except (TypeError, ValueError):
            return jsonify({
                "erro": "Capacidade da mesa inválida"
            }), 400

        if capacidade_da_mesa <= 0:
            return jsonify({
                "erro": "A capacidade da mesa deve ser maior que zero"
            }), 400

    banco_de_dados = conexao_backend()

    try:

        mesa_existente = banco_de_dados.execute(
            """
            SELECT
                Numero_da_Mesa,
                Capacidade_da_Mesa
            FROM Mesa
            WHERE Numero_da_Mesa = ?
            """,
            (numero_da_mesa,)
        ).fetchone()

        if mesa_existente is None:
            return jsonify({
                "erro": "Mesa não encontrada"
            }), 404

        if capacidade_da_mesa is None:
            capacidade_da_mesa = mesa_existente["Capacidade_da_Mesa"]

        if novo_numero_da_mesa != numero_da_mesa:

            outra_mesa = banco_de_dados.execute(
                """
                SELECT Numero_da_Mesa
                FROM Mesa
                WHERE Numero_da_Mesa = ?
                """,
                (novo_numero_da_mesa,)
            ).fetchone()

            if outra_mesa is not None:
                return jsonify({
                    "erro": "Já existe uma mesa cadastrada com esse número"
                }), 409

        banco_de_dados.execute(
            """
            UPDATE Mesa
            SET
                Numero_da_Mesa = ?,
                Capacidade_da_Mesa = ?
            WHERE Numero_da_Mesa = ?
            """,
            (
                novo_numero_da_mesa,
                capacidade_da_mesa,
                numero_da_mesa
            )
        )

        banco_de_dados.commit()

        return jsonify({
            "mensagem": "Mesa atualizada com sucesso",
            "mesa": {
                "numero_da_mesa": novo_numero_da_mesa,
                "capacidade_da_mesa": capacidade_da_mesa
            }
        }), 200

    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({
            "erro": "Erro ao atualizar mesa",
            "detalhes": str(erro)
        }), 500

    finally:
        banco_de_dados.close()


# ROTA PARA EXCLUIR MESAS

@rotas_mesas.route('/mesas/<numero_da_mesa>', methods=['DELETE'])
def excluir_mesa(numero_da_mesa):

    """
    Exclui uma mesa cadastrada no restaurante.

    ---
    tags:
      - Mesas

    produces:
      - application/json

    parameters:

      - name: numero_da_mesa
        in: path
        type: string
        required: true
        description: Número da mesa que será excluída.
        example: "10"

    responses:

      200:
        description: Mesa excluída com sucesso.
        schema:
          type: object
          properties:

            mensagem:
              type: string
              example: Mesa excluída com sucesso

            mesa:
              type: object
              properties:

                numero_da_mesa:
                  type: integer
                  example: 10

                capacidade_da_mesa:
                  type: integer
                  example: 4

      400:
        description: Número da mesa inválido.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: O número da mesa deve ser maior que zero

      404:
        description: Mesa não encontrada.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: Mesa não encontrada

      500:
        description: Erro ao excluir mesa.
        schema:
          type: object
          properties:

            erro:
              type: string
              example: Erro ao excluir mesa

            detalhes:
              type: string
              example: Erro interno do banco de dados
    """

    try:
        numero_convertido = int(numero_da_mesa)

        if str(numero_convertido) != numero_da_mesa:
            return jsonify({
                "erro": "Número da mesa inválido"
            }), 400

        numero_da_mesa = numero_convertido

    except (TypeError, ValueError):
        return jsonify({
            "erro": "Número da mesa inválido"
        }), 400

    if numero_da_mesa <= 0:
        return jsonify({
            "erro": "O número da mesa deve ser maior que zero"
        }), 400

    banco_de_dados = conexao_backend()

    try:

        mesa_existente = banco_de_dados.execute(
            """
            SELECT
                Numero_da_Mesa,
                Capacidade_da_Mesa
            FROM Mesa
            WHERE Numero_da_Mesa = ?
            """,
            (numero_da_mesa,)
        ).fetchone()

        if mesa_existente is None:
            return jsonify({
                "erro": "Mesa não encontrada"
            }), 404

        banco_de_dados.execute(
            """
            DELETE FROM Mesa
            WHERE Numero_da_Mesa = ?
            """,
            (numero_da_mesa,)
        )

        banco_de_dados.commit()

        return jsonify({
            "mensagem": "Mesa excluída com sucesso",
            "mesa": {
                "numero_da_mesa": mesa_existente["Numero_da_Mesa"],
                "capacidade_da_mesa": mesa_existente["Capacidade_da_Mesa"]
            }
        }), 200

    except Exception as erro:

        banco_de_dados.rollback()

        return jsonify({
            "erro": "Erro ao excluir mesa",
            "detalhes": str(erro)
        }), 500

    finally:

        banco_de_dados.close()