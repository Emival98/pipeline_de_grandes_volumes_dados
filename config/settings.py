import os 
from datetime import date

hoje_str = date.today().strftime("%Y%m%d")

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")


LOG_FILE = os.path.join(LOGS_DIR, "relatorio.log")

CSV_FILE = os.path.join(DATA_DIR, "play_by_play.csv")

PASTA_EXCEL = os.path.join(PROJECT_ROOT, "files")

EXCEL_SAIDA = os.path.join(PASTA_EXCEL, f"relatorio_final_{hoje_str}.xlsx")

