import logging
import os

from config.settings import LOGS_DIR, LOG_FILE, EXCEL_SAIDA, QUERY_SQL, NOME_RELATORIO, MEU_EMAIL, DESTINATARIOS, CORPO, ASSUNTO
#from monitoring.metrics import inicio_tempo, fase_log
from processing.transform import executar_pipeline
from email_service.email_server import send_email




def configure_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Formato padrão para ficheiro e consola
    log_format = "%(asctime)s | %(levelname)s | %(message)s"

    # Handler para gravar em ficheiro
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(log_format))

    # Handler para mostrar no terminal (consola)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
        force=True
    )

    


def main():

    configure_logging()

    logging.info("========================================")
    logging.info("Início da execução")

          
    
    
    
    executar_pipeline(
        nome_relatorio=NOME_RELATORIO,
        query=QUERY_SQL,
        excel_saida_caminho=EXCEL_SAIDA,
        tamanho_lote=100_000
    )

    send_email(fonte=MEU_EMAIL,
               destinatarios=DESTINATARIOS,
               assunto=ASSUNTO,
               mensagem=CORPO)


    
    logging.info("Fim da execução")


if __name__ == "__main__":
    main()