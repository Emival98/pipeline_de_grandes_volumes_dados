import gc
import logging
import polars as pl
import xlsxwriter

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def criar_contexto_excel(
    saida_path: str, max_linhas_sheet: int = 500_000
) -> dict:
    """Cria e devolve a estrutura de estado do ficheiro Excel."""
    return {
        "saida_caminho": saida_path,
        "max_linhas_sheet": max_linhas_sheet,
        "folha_trabalho": xlsxwriter.Workbook(
            saida_path, {"constant_memory": True}
        ),
        "contagem_folhas": 1,
        "linhas_planilha_atual": 0,
        "folha_atual": None,
        "colunas": [],
    }


def _adicionar_nova_folha(ctx: dict):
    """Cria uma nova folha (Sheet) e escreve o cabeçalho."""
    nome_folha = f"Dados_Parte_{ctx['contagem_folhas']}"
    logging.info(f"A criar nova folha no Excel: {nome_folha}")

    ctx["folha_atual"] = ctx["folha_trabalho"].add_worksheet(nome_folha)
    ctx["contagem_folhas"] += 1

    # Se já conhecemos as colunas, escreve o cabeçalho de forma vetorizada
    if ctx["colunas"]:
        ctx["folha_atual"].write_row(0, 0, ctx["colunas"])
        ctx["linhas_planilha_atual"] = 1  # Linha 0 ocupada pelo cabeçalho
    else:
        ctx["linhas_planilha_atual"] = 0


def escrever_lote_excel(ctx: dict, df_lote: pl.DataFrame):
    """Escreve um lote (DataFrame) no ficheiro Excel gerindo o limite de linhas."""
    if df_lote.is_empty():
        return

    # Regista as colunas no primeiro lote
    if not ctx["colunas"]:
        ctx["colunas"] = df_lote.columns

    # Garante que existe uma folha ativa no arranque
    if ctx["folha_atual"] is None:
        _adicionar_nova_folha(ctx)

    total_linhas_lote = len(df_lote)
    linhas_processadas = 0

    while linhas_processadas < total_linhas_lote:
        # Espaço real disponível na folha (descontando o cabeçalho/linhas já escritas)
        espaco_restante = ctx["max_linhas_sheet"] - ctx["linhas_planilha_atual"]

        # Se a folha estiver cheia, cria uma nova
        if espaco_restante <= 0:
            _adicionar_nova_folha(ctx)
            espaco_restante = (
                ctx["max_linhas_sheet"] - ctx["linhas_planilha_atual"]
            )

        # Determina quantas linhas deste lote cabem no espaço restante
        linhas_para_escrever = min(
            total_linhas_lote - linhas_processadas, espaco_restante
        )
        sub_df = df_lote.slice(linhas_processadas, linhas_para_escrever)

        # Escreve a fatia no Excel usando write_row
        folha = ctx["folha_atual"]
        for valores_linha in sub_df.iter_rows():
            folha.write_row(ctx["linhas_planilha_atual"], 0, valores_linha)
            ctx["linhas_planilha_atual"] += 1

        linhas_processadas += linhas_para_escrever

        # Limpeza correta da fatia processada FORA do loop de linhas
        del sub_df

    # Liberta o DataFrame principal do lote e recolhe a memória
    del df_lote
    gc.collect()


def fechar_contexto_excel(ctx: dict):
    """Guarda e fecha o ficheiro Excel."""
    logging.info("A fechar e guardar o ficheiro Excel...")
    ctx["folha_trabalho"].close()
    logging.info(f"Ficheiro guardado com sucesso em: {ctx['saida_caminho']}")