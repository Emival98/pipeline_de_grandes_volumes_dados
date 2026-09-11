from sqlalchemy import create_engine, text
import urllib

import os
from dotenv import load_dotenv
import pandas as pd
import logging


load_dotenv()



def conectar_bd ():
    user = os.getenv("DB_USER")
    password = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    driver = os.getenv("DB_DRIVER")

    connection_string = f"mssql+pyodbc://{user}:{password}@{server}/{database}?driver={driver}"

    connection_string_win = (
        f"mssql+pyodbc://@{server}/{database}"
        f"drive={driver}&trusted_connection=yes"
    )

    try:
        logging.info("Criando a conexão com SQL Server")
        engine = create_engine(connection_string)

        with engine.connect() as conexao:
            resultado = text("""
                        SELECT c.id,c.nome,
                        COUNT(v.id) AS Numero_vendas,
                        SUM(p.valor) AS Valor_total,
                        SUM(p.valor) * 1.0 / COUNT(v.id) AS Ticket_medio
                        FROM clientes c
                        JOIN vendas v
                        ON v.id_cliente = c.id
                        JOIN pagamentos p
                        ON p.id_venda = v.id
                        GROUP BY c.id, c.nome
                """)
            
            df = pd.read_sql(resultado, conexao)
        #print(df.head())
            #print("Conexão bem sucedida")
            #print(f"Data/Hora no server: {row.data_atual}, {row.mes}")
            #print(f"Versão do SQL Server: {row.versao}")
    except Exception as e:
        logging.error("Erro ao conectar ao SQL Server")
        print(e)
    return df



