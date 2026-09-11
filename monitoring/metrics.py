import os 
import psutil
import time
import logging

def pegar_metricas_system():
    processamento = psutil.Process(os.getpid())

    memoria = processamento.memory_info().rss / (1024**2)
    cpu = processamento.cpu_percent(interval=0.1)

    return {
        "memoria_mb": round(memoria, 2),
        "cpu_percentagem": cpu
    }

def inicio_tempo():
    return time.perf_counter()


def pegar_tempo_execucao(tempo_inicial):
    return round(time.perf_counter() - tempo_inicial, 2)

def fase_log(nome_fase, tempo_inicial):

    decorrido = pegar_tempo_execucao(tempo_inicial)
    metrica = pegar_metricas_system()

    logging.info(
        f"ETAPA: {nome_fase} | "
        f"TEMPO: {decorrido}s | "
        f"RAM: {metrica['memoria_mb']} MB | "
        f"CPU: {metrica['cpu_percentagem']}%"
    )

    return decorrido