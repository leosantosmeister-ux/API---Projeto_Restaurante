from flask import Flask
from flasgger import Swagger

from Projeto_Restaurante_Rotas_Cardapio import rotas_cardapio
from Projeto_Restaurante_Rotas_Clientes import rotas_clientes
from Projeto_Restaurante_Rotas_Mesas import rotas_mesas
from Projeto_Restaurante_Rotas_Reservas import rotas_reservas
from Projeto_Restaurante_Rotas_Itens_da_Reserva import rotas_itens_da_reserva
from Projeto_Restaurante_Rotas_Pagamentos import rotas_pagamentos
from Projeto_Restaurante_Automacoes import iniciar_automacao_reservas

app = Flask(__name__)

app.json.sort_keys = False

@app.after_request
def aplicar_cors(resposta):
    resposta.headers["Access-Control-Allow-Origin"] = "*"
    resposta.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resposta.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

    return resposta

swagger = Swagger(app)

app.register_blueprint(rotas_cardapio)
app.register_blueprint(rotas_clientes)
app.register_blueprint(rotas_mesas)
app.register_blueprint(rotas_reservas)
app.register_blueprint(rotas_itens_da_reserva)
app.register_blueprint(rotas_pagamentos)

if __name__ == '__main__':
    iniciar_automacao_reservas()
    app.run(debug=True, use_reloader=False)