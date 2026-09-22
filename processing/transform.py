import polars as pl
from excel.writer import escrever_lote_excel, criar_contexto_excel, fechar_contexto_excel
import logging

import psutil
from monitoring.metrics import inicio_tempo, fase_log
from connection.conexao import conexao
from config.settings import QUERY_SQL, NOME_RELATORIO


def transformar_dados(df):
    ...
    return df

def registar_memoria(etapa: str):
    """Mede o consumo de memória RAM atual do processo."""
    processo = psutil.Process()
    ram_mb = processo.memory_info().rss / (1024 * 1024)
    logging.info(f"[{etapa}] Memória RAM em uso: {ram_mb:.2f} MB")

def ler_csv_em_lotes(csv_caminho: str, tamanho_lote: int = 100_000):
    """
    Função geradora que lê o CSV em lotes.
    Garante que nunca carregamos o ficheiro todo para a RAM.
    """
    inicio = inicio_tempo()

    leitor = pl.read_csv_batched(csv_caminho, batch_size=tamanho_lote)
    
    while True:
        lotes = leitor.next_batches(1)
        if not lotes:
            break
    
        yield lotes[0]  # Retorna 1 DataFrame do Polars por lote
    fase_log("leitura em lotes", inicio)



#__--------------------------------------------------------------------------------------------------------------------
def ler_query_sql(query_sql: str, tamanho_lote: int = 100_000):
    """
Executa uma query SQL e devolve o resultado em lotes.

Cada lote é entregue como um DataFrame Polars,
evitando concatenar todo o resultado em memória.
"""

    
    conn = conexao()
    
    logging.info("Iniciando a leitura SQL em lotes de %s registros", f"{tamanho_lote:,}",)
    inicio = inicio_tempo()

    leitor = pl.read_database(query=query_sql, connection=conn, iter_batches=True, batch_size=tamanho_lote)

    try:
        for lot in leitor:
            yield lot
    finally:
        conn.close()

        logging.info("Conexão com a BD fechada.")
        fase_log(
            "Leitura SQL em lotes",
            inicio,
        )
    

def executar_pipeline(
    nome_relatorio: str,
    query: str,
    excel_saida_caminho: str,
    tamanho_lote: int = 100_000,
):
    """
    Executa o pipeline completo:

    DB2 -> Polars -> Transformação -> Excel
    """

    inicio_total = inicio_tempo()

    logging.info(
        "=============================================="
    )
    logging.info(
        "Início do relatório: %s",
        nome_relatorio,
    )
    logging.info(
        "=============================================="
    )

    registar_memoria("Início")

    ctx_excel = criar_contexto_excel(
        excel_saida_caminho,
        max_linhas_sheet=500_000,
    )

    total_linhas = 0
    contagem_lotes = 0

    try:

        for df_lote in ler_query_sql(query_sql=query,
            tamanho_lote=tamanho_lote,
        ):

            contagem_lotes += 1

            qtd_linhas = df_lote.height

            total_linhas += qtd_linhas

            logging.info(
                "A processar lote %s | %s linhas",
                contagem_lotes,
                f"{qtd_linhas:,}",
            )

            # --------------------------------------------------
            # TRANSFORMAÇÃO
            # --------------------------------------------------

            inicio_transformacao = inicio_tempo()

            df_lote = transformar_dados(df_lote)

            fase_log(
                f"Transformação lote {contagem_lotes}",
                inicio_transformacao,
            )

            # --------------------------------------------------
            # ESCRITA EXCEL
            # --------------------------------------------------

            inicio_excel = inicio_tempo()

            escrever_lote_excel(
                ctx_excel,
                df_lote,
            )

            fase_log(
                f"Escrita Excel lote {contagem_lotes}",
                inicio_excel,
            )

            # --------------------------------------------------
            # MEMÓRIA
            # --------------------------------------------------

            registar_memoria(
                f"Lote {contagem_lotes} concluído"
            )

    except Exception:

        logging.exception(
            "Erro durante a execução do pipeline."
        )

        raise

    finally:

        fechar_contexto_excel(ctx_excel)

    fase_log(
        "Pipeline total",
        inicio_total,
    )

    logging.info(
        "Total de lotes processados: %s",
        f"{contagem_lotes:,}",
    )

    logging.info(
        "Total de linhas processadas: %s",
        f"{total_linhas:,}",
    )

    registar_memoria("Fim")