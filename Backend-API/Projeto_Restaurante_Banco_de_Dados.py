import sqlite3

banco_de_dados = sqlite3.connect('Projeto_Restaurante.db')

banco_de_dados.execute("PRAGMA foreign_keys = ON")

tabelas = banco_de_dados.cursor()

def conexao_backend():
    banco_de_dados = sqlite3.connect('Projeto_Restaurante.db')
    banco_de_dados.row_factory = sqlite3.Row
    banco_de_dados.execute("PRAGMA foreign_keys = ON")
    return banco_de_dados

#CRIAÇÃO_DE_TABELAS

tabelas.execute('''CREATE TABLE IF NOT EXISTS Cardapio(
                 Numero_do_Item INTEGER PRIMARY KEY AUTOINCREMENT,
                 Nome_do_Item TEXT NOT NULL UNIQUE,
                 Categoria_do_Item TEXT NOT NULL,
                 Valor_do_Item REAL NOT NULL,
                 CHECK (Valor_do_Item > 0)
                 )
''')

tabelas.execute('''CREATE TABLE IF NOT EXISTS Clientes(
                 Numero_do_Cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                 Primeiro_Nome_do_Cliente TEXT NOT NULL,
                 Sobrenome_do_Cliente TEXT NOT NULL,
                 CPF TEXT NOT NULL UNIQUE,
                 Email_do_Cliente TEXT NOT NULL UNIQUE,
                 Telefone_do_cliente TEXT NOT NULL,
                 Senha_do_Cliente TEXT NOT NULL
                 )
''')

tabelas.execute('''CREATE TABLE IF NOT EXISTS Mesa(
                 Numero_da_Mesa INTEGER PRIMARY KEY,
                 Capacidade_da_Mesa INTEGER NOT NULL,
                 CHECK (Capacidade_da_Mesa > 0)
                 )
''')

tabelas.execute('''CREATE TABLE IF NOT EXISTS Reservas(
                 Numero_da_Reserva INTEGER PRIMARY KEY AUTOINCREMENT,
                 Data_do_Agendamento TEXT NOT NULL,
                 Horario_do_Agendamento TEXT NOT NULL,
                 Numero_do_Cliente INTEGER NOT NULL,
                 Quantidade_de_Pessoas_na_Mesa INTEGER NOT NULL,
                 Numero_da_Mesa INTEGER NOT NULL,
                 Capacidade_da_Mesa_na_Reserva INTEGER NOT NULL,
                 Data_da_Reserva TEXT NOT NULL,
                 Horario_da_Reserva TEXT NOT NULL,
                 Data_de_Termino_da_Reserva TEXT NOT NULL,
                 Horario_de_Termino_da_Reserva TEXT NOT NULL,
                 Duracao_da_Reserva INTEGER NOT NULL,
                 Status_da_Reserva TEXT NOT NULL,
                 CHECK (Quantidade_de_Pessoas_na_Mesa > 0),
                 CHECK (Capacidade_da_Mesa_na_Reserva > 0),
                 CHECK (Duracao_da_Reserva >= 60),
                 CHECK(
                     Status_da_Reserva IN(
                     'PENDENTE',
                     'CONFIRMADA',
                     'CANCELADA',
                     'CONCLUIDA'
                     )
                 ),

                 FOREIGN KEY (Numero_do_Cliente) 
                 REFERENCES Clientes(Numero_do_Cliente)

                 )
''')

tabelas.execute('''
    CREATE UNIQUE INDEX IF NOT EXISTS Liberar_Reserva_Apos_Cancelamento
    ON Reservas (
        Numero_da_Mesa,
        Data_da_Reserva,
        Horario_da_Reserva
    )
    WHERE Status_da_Reserva != 'CANCELADA'
''')

tabelas.execute('''CREATE TABLE IF NOT EXISTS Itens_da_Reserva(
                 ID_Itens_da_Reserva INTEGER PRIMARY KEY AUTOINCREMENT,
                 Numero_da_Reserva INTEGER NOT NULL,
                 Numero_do_Item INTEGER NOT NULL,
                 Nome_do_Item_na_Reserva TEXT NOT NULL,
                 Categoria_do_Item_na_Reserva TEXT NOT NULL,
                 Valor_do_Item_na_Reserva REAL NOT NULL,
                 Quantidade_de_Itens INTEGER NOT NULL,
                 UNIQUE (Numero_da_Reserva, Numero_do_Item),
                 CHECK (Quantidade_de_Itens > 0),
                 CHECK (Valor_do_Item_na_Reserva > 0),

                 FOREIGN KEY (Numero_da_Reserva)
                 REFERENCES Reservas(Numero_da_Reserva)
                 )
''')

tabelas.execute('''CREATE TABLE IF NOT EXISTS Pagamentos(
                 ID_Pagamentos INTEGER PRIMARY KEY AUTOINCREMENT,
                 Numero_da_Reserva INTEGER NOT NULL UNIQUE,
                 Valor_do_Pagamento REAL NOT NULL,
                 Forma_de_Pagamento TEXT NOT NULL,
                 Data_do_Pagamento TEXT NOT NULL,
                 Status_do_Pagamento TEXT NOT NULL,
                 CHECK (Valor_do_Pagamento > 0),

                 CHECK (
                     Forma_de_Pagamento IN (
                         'PIX',
                         'CARTAO_CREDITO',
                         'CARTAO_DEBITO',
                         'DINHEIRO'
                     )
                 ),

                 CHECK (
                     Status_do_Pagamento IN (
                         'PENDENTE',
                         'PAGO',
                         'CANCELADO'
                     )
                 ),

                 FOREIGN KEY (Numero_da_Reserva)
                 REFERENCES Reservas(Numero_da_Reserva) 
                 )
''')

# DADOS DA TABELA CARDÁPIO

itens_cardapio = [

    # REFEIÇÕES

    (
        'Prato Feito Tradicional (Arroz, Feijão, Bife, Salada e Ovo)',
        'Refeição',
        22.00
    ),

    (
        'Stroganoff de Frango com Arroz e Batata Palha',
        'Refeição',
        24.00
    ),

    (
        'Feijoada Completa (Individual)',
        'Refeição',
        28.00
    ),

    (
        'Parmegiana de Carne com Espaguete',
        'Refeição',
        26.00
    ),

    (
        'Omelete Recheado com Queijo e Presunto, Arroz e Salada',
        'Refeição',
        18.00
    ),

    # LANCHES

    (
        'Hambúrguer Tradicional (Pão, Carne 120g, Queijo e Salada)',
        'Lanche',
        16.00
    ),

    (
        'X-Bacon Especial (Pão, Carne 150g, Queijo, Bacon e Maionese)',
        'Lanche',
        21.00
    ),

    (
        'Smash Burger Duplo (Pão, 2x Carne 80g, Queijo Cheddar)',
        'Lanche',
        19.00
    ),

    (
        'Porção de Batata Frita Crocante (300g)',
        'Lanche',
        14.00
    ),

    # SOBREMESAS

    (
        'Pudim de Leite Condensado',
        'Sobremesa',
        8.00
    ),

    (
        'Mousse de Maracujá',
        'Sobremesa',
        7.00
    ),

    (
        'Bolo no Pote',
        'Sobremesa',
        9.00
    ),

    (
        'Petit Gâteau com Sorvete de Creme',
        'Sobremesa',
        14.00
    ),

    # BEBIDAS NÃO ALCOÓLICAS

    (
        'Suco Natural de Laranja (500ml)',
        'Bebida não alcoólica',
        8.00
    ),

    (
        'Suco Natural de Limão (500ml)',
        'Bebida não alcoólica',
        7.00
    ),

    (
        'Suco de Maracujá (Polpa 500ml)',
        'Bebida não alcoólica',
        8.50
    ),

    (
        'Suco de Acerola com Laranja (500ml)',
        'Bebida não alcoólica',
        9.00
    ),

    (
        'Suco de Abacaxi com Hortelã (500ml)',
        'Bebida não alcoólica',
        8.50
    ),

    (
        'Coca-Cola Lata (350ml)',
        'Bebida não alcoólica',
        6.00
    ),

    (
        'Guaraná Antarctica Lata (350ml)',
        'Bebida não alcoólica',
        5.50
    ),

    (
        'Fanta Laranja Lata (350ml)',
        'Bebida não alcoólica',
        5.50
    ),

    (
        'Fanta Uva Lata (350ml)',
        'Bebida não alcoólica',
        5.50
    ),

    (
        'Sprite Lata (350ml)',
        'Bebida não alcoólica',
        5.50
    ),

    # BEBIDAS ALCOÓLICAS

    (
        'Cerveja Heineken Long Neck (330ml)',
        'Bebida Alcoólica',
        11.00
    ),

    (
        'Cerveja Stella Artois Long Neck (330ml)',
        'Bebida Alcoólica',
        10.00
    ),

    (
        'Cerveja Amstel Lata (350ml)',
        'Bebida Alcoólica',
        7.00
    ),

    (
        'Cerveja Brahma Lata (350ml)',
        'Bebida Alcoólica',
        5.50
    ),

    (
        'Cerveja Antarctica Pilsen Lata (350ml)',
        'Bebida Alcoólica',
        5.50
    )

]

for item in itens_cardapio:

    tabelas.execute('''
        SELECT Numero_do_Item
        FROM Cardapio
        WHERE Nome_do_Item = ?
    ''', (item[0],))
    item_existente = tabelas.fetchone()

    if item_existente is None:

        tabelas.execute('''
            INSERT INTO Cardapio (
                Nome_do_Item,
                Categoria_do_Item,
                Valor_do_Item
            )

            VALUES (?, ?, ?)
        ''', item)

# DADOS DA TABELA MESAS

mesas = [
    (1, 4),
    (2, 10),
    (3, 8),
    (4, 2),
    (5, 8),
    (6, 4),
    (7, 8),
    (8, 8),
    (9, 4),
    (10, 8),
    (11, 4),
    (12, 8),
    (13, 10),
    (14, 2),
    (15, 8),
    (16, 4),
    (17, 10),
    (18, 6),
    (19, 10),
    (20, 8)
]

for mesa in mesas:

    tabelas.execute('''
        SELECT Numero_da_Mesa
        FROM Mesa
        WHERE Numero_da_Mesa = ?
    ''', (mesa[0],))

    mesa_existente = tabelas.fetchone()

    if mesa_existente is None:

        tabelas.execute('''
            INSERT INTO Mesa (
                Numero_da_Mesa,
                Capacidade_da_Mesa
            )
            VALUES (?, ?)
        ''', mesa)

banco_de_dados.commit()
banco_de_dados.close()