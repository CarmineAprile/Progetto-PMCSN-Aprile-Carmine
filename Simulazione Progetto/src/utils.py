import numpy as np
from lib.DES.rvms import idfStudent


def compute_snapshot(now, edge, cloud, sum_rt_e, count_e, sum_rt_c, count_c):
    # Funzione che scatta una "foto" dello stato del sistema in un dato istante
    if now <= 0: return None

    # Calcolo della media cumulata del Response Time dall'inizio della simulazione
    avg_rt_e = sum_rt_e / count_e if count_e > 0 else 0
    avg_rt_c = sum_rt_c / count_c if count_c > 0 else 0

    # Calcolo della media di sistema (pesata sul numero di job finiti per classe)
    total_count = count_e + count_c
    avg_rt_sys = (sum_rt_e + sum_rt_c) / total_count if total_count > 0 else 0

    return {
        'time': now,
        # Utilizzazione = Tempo Busy / Tempo Totale
        'util_e': edge.cumulative_busy_time / now,
        'util_c': cloud.cumulative_busy_time / now,
        # Numero Medio Utenti E[N] = Area Utenti / Tempo Totale
        'ni_e': edge.area_num_in_system / now,
        'ni_c': cloud.area_num_in_system / now,
        'ni': (edge.area_num_in_system + cloud.area_num_in_system) / now,
        'rt_e': avg_rt_e,
        'rt_c': avg_rt_c,
        'rt': avg_rt_sys
    }


def get_estimate(data, confidence=0.95):
    # Calcola l'Intervallo di Confidenza per una lista di campioni
    n = len(data)
    if n < 2: return np.mean(data), 0.0
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)

    u = 1.0 - 0.5 * (1.0 - confidence)
    t = idfStudent(n - 1, u)
    h = t * std_dev / np.sqrt(n)
    return mean, h