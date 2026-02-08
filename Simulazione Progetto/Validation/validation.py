import pandas as pd
from src.simulator import Simulator
import configurazione_sistema as config
from src.utils import get_estimate
from tqdm import tqdm

def run_final_validation():
    print("=" * 105)
    print("   VALIDAZIONE   ")
    print("=" * 105)

    NUM_RUNS = config.NUM_REPLICAS
    T_DURATION = config.SIMULATION_DURATION
    T_WARMUP = config.WARMUP_DURATION
    T_OBSERVATION = T_DURATION - T_WARMUP

    run_results = []

    for i in tqdm(range(NUM_RUNS), desc="Esecuzione Repliche"):
        seed = config.SEED + (i * 123456789)
        sim = Simulator(
            arrival_rate=config.ARRIVAL_RATE,
            p_c=config.PC_PROBABILITY,
            duration=T_DURATION,
            warmup_time=T_WARMUP,
            seed=seed
        )

        rt_e_post, rt_c_post, edge, cloud, _, _ = sim.run()

        # Raccolta metriche osservate
        run_results.append({
            'Replica': i + 1,
            'Rho_E': edge.busy_time_post / T_OBSERVATION,
            'Rho_C': cloud.busy_time_post / T_OBSERVATION,
            'N_E': edge.area_ni_post / T_OBSERVATION,
            'N_C': cloud.area_ni_post / T_OBSERVATION,
            'R_E': rt_e_post,
            'R_C': rt_c_post,
            'R_tot': (rt_e_post * (1 - config.PC_PROBABILITY)) + (rt_c_post * config.PC_PROBABILITY)
        })

    # Creazione DataFrame Repliche
    df_repliche = pd.DataFrame(run_results)

    # --- CALCOLI VALORI TEORICI ---
    L = config.ARRIVAL_RATE
    pc = config.PC_PROBABILITY
    Se_e = config.SERVICE_DEMANDS['Edge']['E']
    Se_c = config.SERVICE_DEMANDS['Edge']['C']
    Sc_c = config.SERVICE_DEMANDS['Cloud']['C']

    rho_e_th = L * (Se_e + pc * Se_c)
    rho_c_th = L * (pc * Sc_c)

    R_phase_edge_E = Se_e / (1 - rho_e_th)
    R_phase_edge_C = Se_c / (1 - rho_e_th)
    R_phase_cloud = Sc_c / (1 - rho_c_th)

    th = {
        'Rho_E': rho_e_th, 'Rho_C': rho_c_th,
        'N_E': rho_e_th / (1 - rho_e_th), 'N_C': rho_c_th / (1 - rho_c_th),
        'R_E': R_phase_edge_E,
        'R_C': R_phase_edge_E + R_phase_cloud + R_phase_edge_C,
        'R_tot': (1 - pc) * R_phase_edge_E + pc * (R_phase_edge_E + R_phase_cloud + R_phase_edge_C)
    }

    # --- GENERAZIONE REPORT FINALE ---
    print("\n" + "-" * 105)
    print(f"{'METRICA':<25} | {'TEORICO':<15} | {'SIMULAZIONE (95% IC)':<30} | {'ESITO'}")
    print("-" * 105)

    metrics = [
        ('Rho_E', 'Utilizzazione Edge'), ('Rho_C', 'Utilizzazione Cloud'),
        ('N_E', 'Utenti Medi Edge'), ('N_C', 'Utenti Medi Cloud'),
        ('R_E', 'RT Classe E (Total)'), ('R_C', 'RT Classe C (Total)'), ('R_tot', 'RT Sistema')
    ]

    report_final_list = []

    for key, label in metrics:
        mean_s, h_w = get_estimate(df_repliche[key].values)
        t_val = th[key]
        status = "OK" if abs(t_val - mean_s) <= h_w else "FAIL"

        print(
            f"{label:<25} | {t_val:<15.4f} | {mean_s:>10.4f} +/- {h_w:<15.4f} | {'✅' if status == 'OK' else '❌'} {status}")

        report_final_list.append({
            'Metrica': label,
            'Valore_Teorico': round(t_val, 6),
            'Valore_Simulato': round(mean_s, 6),
            'Intervallo_Confidenza': round(h_w, 6),
            'Esito': status
        })

    # --- SALVATAGGIO FILE ---
    df_repliche.to_csv("validazione_repliche.csv", index=False, sep=';')
    pd.DataFrame(report_final_list).to_csv("validazione_report_finale.csv", index=False, sep=';')

    print("-" * 105)
    print(f"[SALVATAGGIO] Dati repliche salvati in: validazione_repliche.csv")
    print(f"[SALVATAGGIO] Report finale salvato in: validazione_report.csv")


if __name__ == "__main__":
    run_final_validation()