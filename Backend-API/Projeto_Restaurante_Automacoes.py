import time
import threading

from datetime import datetime, timedelta
from Projeto_Restaurante_Banco_de_Dados import conexao_backend


# TEMPO MÁXIMO QUE UMA RESERVA PODE FICAR PENDENTE

TEMPO_MAXIMO_PENDENTE = timedelta(hours=2)

def atualizar_status_reservas():

    banco_de_dados = conexao_backend()

    try:

        agora = datetime.now()

        # CANCELA RESERVAS PENDENTES HÁ MAIS DE 2 HORAS

        reservas_pendentes = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Reserva,
                Data_do_Agendamento,
                Horario_do_Agendamento

            FROM Reservas

            WHERE Status_da_Reserva = 'PENDENTE'
            '''
        ).fetchall()

        for reserva in reservas_pendentes:

            data_agendamento = datetime.strptime(
                reserva["Data_do_Agendamento"],
                "%Y-%m-%d"
            ).date()

            horario_agendamento = datetime.strptime(
                reserva["Horario_do_Agendamento"],
                "%H:%M:%S"
            ).time()

            momento_agendamento = datetime.combine(
                data_agendamento,
                horario_agendamento
            )

            prazo_pagamento = momento_agendamento + TEMPO_MAXIMO_PENDENTE

            if agora >= prazo_pagamento:

                banco_de_dados.execute(
                    '''
                    UPDATE Reservas

                    SET Status_da_Reserva = 'CANCELADA'

                    WHERE Numero_da_Reserva = ?

                    AND Status_da_Reserva = 'PENDENTE'
                    ''',
                    (
                        reserva["Numero_da_Reserva"],
                    )
                )

        # CONCLUI RESERVAS CONFIRMADAS APÓS O HORÁRIO DE TÉRMINO
      
        reservas_confirmadas = banco_de_dados.execute(
            '''
            SELECT
                Numero_da_Reserva,
                Data_de_Termino_da_Reserva,
                Horario_de_Termino_da_Reserva

            FROM Reservas

            WHERE Status_da_Reserva = 'CONFIRMADA'
            '''
        ).fetchall()


        for reserva in reservas_confirmadas:

            data_termino = datetime.strptime(
                reserva["Data_de_Termino_da_Reserva"],
                "%Y-%m-%d"
            ).date()

            horario_termino = datetime.strptime(
                reserva["Horario_de_Termino_da_Reserva"],
                "%H:%M"
            ).time()


            momento_termino = datetime.combine(
                data_termino,
                horario_termino
            )


            if momento_termino <= agora:

                banco_de_dados.execute(
                    '''
                    UPDATE Reservas

                    SET Status_da_Reserva = 'CONCLUIDA'

                    WHERE Numero_da_Reserva = ?

                    AND Status_da_Reserva = 'CONFIRMADA'
                    ''',
                    (
                        reserva["Numero_da_Reserva"],
                    )
                )


        banco_de_dados.commit()


    except Exception:

        banco_de_dados.rollback()


    finally:

        banco_de_dados.close()


def iniciar_automacao_reservas():

    def executar_automaticamente():

        while True:

            atualizar_status_reservas()

            # Executa novamente após 1 minuto
            time.sleep(60)


    thread = threading.Thread(
        target=executar_automaticamente,
        daemon=True
    )

    thread.start()