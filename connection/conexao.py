import pyodbc
import polars as pl


import os
from dotenv import load_dotenv
import polars as pl
import logging


load_dotenv()

server = os.getenv("DB_SERVER")
porta = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")
driver = os.getenv("DB_DRIVER")


def conexao():
    try:
        logging.info("Conectando na BD")
        texto_conexao = pyodbc.connect(
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
                                    )
        return texto_conexao
    except pyodbc.OperationalError as e:
        logging.error(f"Erro ao conectar ao SQL Server\n{e}")
        return None

    
def testar_ligacao():
    texto_conexao = conexao()
    if not texto_conexao:
        return False
    
    try:
        logging.info("Criando a conexão com SQL Server")
        cursor = texto_conexao.cursor()
        cursor.execute("SELECT top 1000 * FROM EcommerceLab.[ecommerce].[Customers]")

        resultado = cursor.fetchone()
        print(f"Data de hoje: {resultado[0]}")

        

        
    except Exception as e:
        logging.error(f"Erro ao conectar ao SQL Server\n{e}")
        print(e)
        return False

    finally:
        texto_conexao.close()
