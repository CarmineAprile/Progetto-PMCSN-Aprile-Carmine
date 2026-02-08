import pandas as pd
import pickle
import os
from tqdm import tqdm
import configurazione_sistema as config
from src.simulator import Simulator
from lib.DES import rngs

BASE_DIR = "risultati_progetto"
DATA_DIR = os.path.join(BASE_DIR, "sim_results")


def save_to_pickle(filename, data):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    path = os.path.join(DATA_DIR, f"{filename}.pkl")
    with open(path, 'wb') as f:
        pickle.dump(data, f)
    print(f"[OK] Dati salvati in: {path}")


def run_base_scenario(current_seed):
    print("\n>>> Scenario Base (Obiettivo 1 & 2)...")
    results = []

    for i in tqdm(range(config.NUM_REPLICAS), desc="Simulazione"):
        sim = Simulator(config.ARRIVAL_RATE,
                        config.PC_PROBABILITY,
                        config.SIMULATION_DURATION,
                        config.WARMUP_DURATION,
                        current_seed)

        # Restituisce le medie post-warmup
        rt_e_post, rt_c_post, _, _, samples, _ = sim.run()

        # Recuperiamo lo stato finale dello stream 0
        rngs.selectStream(0)
        current_seed = rngs.getSeed()

        df_s = pd.DataFrame(samples)

        if not df_s.empty and df_s.iloc[0]['time'] > 0:
            zeros = {col: [0.0] for col in df_s.columns}
            df_s = pd.concat([pd.DataFrame(zeros), df_s], ignore_index=True)

        results.append({
            'final_rt_e_val': rt_e_post,
            'final_rt_c_stat': rt_c_post,
            'samples': df_s
        })

    save_to_pickle('scenario_base', results)
    return current_seed


def run_stress_test(current_seed):
    print("\n>>> Stress Test (Obiettivo 3)...")
    increments, labels = [0.0, 0.10, 0.20, 0.30], ["plus_0", "plus_10", "plus_20", "plus_30"]

    for inc, label in zip(increments, labels):
        current_rate = config.ARRIVAL_RATE * (1 + inc)
        results = []
        for r in tqdm(range(config.NUM_REPLICAS), desc=f"Scenario {label}"):
            sim = Simulator(current_rate,
                            config.PC_PROBABILITY,
                            config.SIMULATION_DURATION,
                            config.WARMUP_DURATION,
                            current_seed)
            _, _, _, _, samples, _ = sim.run()

            rngs.selectStream(0)
            current_seed = rngs.getSeed()

            df_s = pd.DataFrame(samples)

            if not df_s.empty and df_s.iloc[0]['time'] > 0:
                zeros = {col: [0.0] for col in df_s.columns}
                df_s = pd.concat([pd.DataFrame(zeros), df_s], ignore_index=True)

            results.append({'samples': df_s})
        save_to_pickle(f'stress_test_{label}', results)
    return current_seed


def run_hardware_upgrade(current_seed):
    print("\n>>> Hardware Upgrade (Obiettivo 4)...")

    # Salviamo i valori originali per ripristinarli alla fine
    ORIG_E = config.SERVICE_DEMANDS['Edge']['E']
    ORIG_C_UP = config.SERVICE_DEMANDS['Edge']['C']

    # Usiamo il tasso dello stress test massimo (+30%)
    STRESS_RATE = config.ARRIVAL_RATE * 1.30
    upgrades, labels = [0.0, 0.10, 0.20, 0.30], ["up_0", "up_10", "up_20", "up_30"]

    for up_factor, label in zip(upgrades, labels):
        # Applichiamo il miglioramento hardware riducendo la demand
        config.SERVICE_DEMANDS['Edge']['E'] = ORIG_E * (1 - up_factor)
        config.SERVICE_DEMANDS['Edge']['C'] = ORIG_C_UP * (1 - up_factor)

        results = []
        for r in tqdm(range(config.NUM_REPLICAS), desc=f"Upgrade {label}"):
            sim = Simulator(STRESS_RATE,
                            config.PC_PROBABILITY,
                            config.SIMULATION_DURATION,
                            config.WARMUP_DURATION,
                            current_seed)
            _, _, _, _, samples, _ = sim.run()

            rngs.selectStream(0)
            current_seed = rngs.getSeed()

            df_s = pd.DataFrame(samples)

            if not df_s.empty and df_s.iloc[0]['time'] > 0:
                zeros = {col: [0.0] for col in df_s.columns}
                df_s = pd.concat([pd.DataFrame(zeros), df_s], ignore_index=True)

            results.append({'samples': df_s})
        save_to_pickle(f'upgrade_{label}', results)

    # Ripristino parametri originali
    config.SERVICE_DEMANDS['Edge']['E'] = ORIG_E
    config.SERVICE_DEMANDS['Edge']['C'] = ORIG_C_UP
    return current_seed


if __name__ == "__main__":
    rngs.selectStream(0)
    current_global_seed = config.SEED

    while True:
        print("\n" + "=" * 40)
        print("--- GENERATORE DATI SIMULAZIONE ---")
        print("=" * 40)
        print("1. Scenario Base (Obiettivi 1 & 2)")
        print("2. Stress Test +0/10/20/30% (Obiettivo 3)")
        print("3. Hardware Upgrade (Obiettivo 4)")
        print("0. Esci")

        scelta = input("\nSeleziona opzione: ")
        if scelta == '1':
            current_global_seed = run_base_scenario(current_global_seed)
        elif scelta == '2':
            current_global_seed = run_stress_test(current_global_seed)
        elif scelta == '3':
            current_global_seed = run_hardware_upgrade(current_global_seed)
        elif scelta == '0':
            break