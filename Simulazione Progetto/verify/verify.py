import os
import pandas as pd
from tqdm.auto import tqdm
from lib.DES import rngs

import configurazione_sistema as config
from src.simulator import Simulator
from src.entities import Job
from src.utils import get_estimate

NUM_REPS = config.NUM_REPLICAS
DURATION = 3600.0 # 1 ora


def run_system_verification():

    rngs.selectStream(0)
    current_seed = config.SEED

    print("=" * 95)
    print(f"   AVVIO VERIFICA DEL SISTEMA: {NUM_REPS} REPLICHE DA {DURATION}s")
    print("=" * 95)

    obs_rates = []
    obs_pcs = []
    service_results = {'Edge_E': [], 'Edge_C': [], 'Cloud_C': []}

    for i in tqdm(range(NUM_REPS), desc="Esecuzione Repliche"):
        Job.reset_id()
        sim = Simulator(config.ARRIVAL_RATE,
                        config.PC_PROBABILITY,
                        DURATION, 0,
                        current_seed)
        sim.run()

        rngs.selectStream(0)
        current_seed = rngs.getSeed()

        obs_rates.append(sim.total_arrivals / DURATION)

        if sim.total_arrivals > 0:
            obs_pcs.append(sim.verify_sd_count['Cloud_C'] / sim.total_arrivals)
        else:
            obs_pcs.append(0)

        for key in service_results.keys():
            if sim.verify_sd_count[key] > 0:
                service_results[key].append(sim.verify_sd_sum[key] / sim.verify_sd_count[key])

    data = []

    # Test Tasso Arrivi
    m, h = get_estimate(obs_rates)
    status = "OK" if abs(m - config.ARRIVAL_RATE) <= h else "FAIL"
    data.append(["Tasso Arrivi (Lambda)", config.ARRIVAL_RATE, m, h, status])

    # Test Routing
    m, h = get_estimate(obs_pcs)
    status = "OK" if abs(m - config.PC_PROBABILITY) <= h else "FAIL"
    data.append(["Prob. Routing (p_c)", config.PC_PROBABILITY, m, h, status])

    # Test Service Demands
    targets = {
        'Edge_E': config.SERVICE_DEMANDS['Edge']['E'],
        'Edge_C': config.SERVICE_DEMANDS['Edge']['C'],
        'Cloud_C': config.SERVICE_DEMANDS['Cloud']['C']
    }

    for key, target in targets.items():
        if service_results[key]:
            m, h = get_estimate(service_results[key])
            status = "OK" if abs(m - target) <= h else "FAIL"
            data.append([f"Service Demand {key}", target, m, h, status])

    # Creazione DataFrame
    df = pd.DataFrame(data, columns=['Parametro', 'Target', 'Media Osservata', 'IC (+/-)', 'Esito'])

    # --- SALVATAGGIO CSV NELLO STESSO PERCORSO DEL FILE ---
    # Ottiene la cartella dove si trova questo script (verify/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "report_verifica.csv")

    # Salvataggio con separatore punto e virgola per Excel
    df.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig')

    print("\n" + "=" * 95)
    print(f"   REPORT FINALE SALVATO IN: {file_path}")
    print("=" * 95)
    print(df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("=" * 95)


if __name__ == "__main__":
    run_system_verification()