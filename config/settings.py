import os 
from dotenv import load_dotenv
from datetime import date

load_dotenv()

hoje_str = date.today().strftime("%Y%m%d")

#Pastas
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

#________________Nome do Relatorio
NOME_RELATORIO = "Orders"

#________________________Ficheiros
LOG_FILE = os.path.join(LOGS_DIR, f"{NOME_RELATORIO}{hoje_str}.log")

CSV_FILE = os.path.join(DATA_DIR, "play_by_play.csv")

PASTA_EXCEL = os.path.join(PROJECT_ROOT, "files")

EXCEL_SAIDA = os.path.join(PASTA_EXCEL, f"{NOME_RELATORIO}_{hoje_str}.xlsx")

#________________________Query
QUERY_SQL = os.getenv("DB_QUERY")



#_________________________Email
MINHA_SENHA_GMAIL=os.getenv("MINHA_SENHA_GMAIL")
MEU_EMAIL = os.getenv("MEU_EMAIL")
DESTINATARIOS_LISTA = os.getenv("DESTINATARIOS")
DESTINATARIOS = [email.strip() for email in DESTINATARIOS_LISTA.split(",") if email.strip()]
ASSUNTO = "Teste email automatizado"
CORPO = f"""
<html>
    <body>
        <p style="text-align: justify; hyphens: auto;"> Estimados Prezados
        <br><br>O relatório foi gerado e guardado na pasta compartilhada e pronto pra extração
        <br><br>(<strong>Ref: Relatorio_{NOME_RELATORIO}</strong>)
        </p>
    </body>
</html>
"""



