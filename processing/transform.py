import polars as pl
from excel.writer import escrever_lote_excel, criar_contexto_excel, fechar_contexto_excel
import logging

import psutil
from monitoring.metrics import inicio_tempo, fase_log

def transformar_dados(df):
    ...
    return df

def inspecionar_csv(file_path, num_linhas= 5):
    with open(file_path, "rb") as file:
        df = pl.read_csv(
            file_path,
            separator=',',
            n_rows=num_linhas

        )

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

def executar_pipeline(csv_caminho: str, excel_saida_caminho: str, tamanho_lote: int = 100_000):
    """Orquestra a leitura do CSV em lotes e a escrita no Excel."""
    inicio = inicio_tempo()
    logging.info(f"A iniciar processamento do ficheiro: {csv_caminho}")
    registar_memoria("Início")

    # Inicializa o estado do Excel com o teu dicionário ajustado
    ctx_excel = criar_contexto_excel(excel_saida_caminho, max_linhas_sheet=500_000)

    total_linhas = 0
    contagem_lotes = 0
    
    # Itera sobre os lotes do CSV produzidos pela função geradora
    for df_lote in ler_csv_em_lotes(csv_caminho, tamanho_lote=tamanho_lote):
        contagem_lotes += 1
        qtd_linhas = len(df_lote)
        total_linhas += qtd_linhas

        logging.info(f"A processar Lote {contagem_lotes} com {qtd_linhas} linhas...")
        
        # Escreve o lote no Excel
        escrever_lote_excel(ctx_excel, df_lote)
        
        registar_memoria(f"Lote {contagem_lotes} concluído")
    fase_log("Leitura dos dados", inicio)
    # Fecha e finaliza o ficheiro
    fechar_contexto_excel(ctx_excel)