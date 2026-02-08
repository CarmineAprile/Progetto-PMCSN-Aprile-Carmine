import pandas as pd
import os
import pickle
import configurazione_sistema as config
from src.utils import get_estimate

BASE_DIR = "risultati_progetto"
DATA_DIR = os.path.join(BASE_DIR, "sim_results")

METRICHE = [
    ("RT_Edge", "rt_e"), ("RT_Cloud", "rt_c"),
    ("Util_Edge", "util_e"), ("Util_Cloud", "util_c"),
    ("Utenti_Edge", "ni_e"), ("Utenti_Cloud", "ni_c")
]


def load_pkl(name):
    path = os.path.join(DATA_DIR, f"{name}.pkl")
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        return pickle.load(f)


def calcola_media_steady_state(df, colonna):
    # Calcola la media della metrica scartando il warmup
    df_steady = df[df['time'] >= config.WARMUP_DURATION]
    return df_steady[colonna].mean()


def genera_report_G1_G2():
    print(">>> Generazione Report Goal 1 & 2 (Scenario Base)...")
    report_list = []
    data = load_pkl('scenario_base')

    if data:
        for label, col in METRICHE:
            # Estrazione della media post-warmup di ogni replica
            values = [calcola_media_steady_state(r['samples'], col) for r in data]
            m, h = get_estimate(values)
            report_list.append({"Scenario": "Base", "Metrica": label, "Media": round(m, 4), "Errore_HW": round(h, 4)})

        df = pd.DataFrame(report_list)
        path = os.path.join(BASE_DIR, "report_G1_G2_Base.csv")
        df.to_csv(path, index=False, sep=';')
        print(f"[OK] Salvato in: {path}")


def genera_report_G3():
    print(">>> Generazione Report Goal 3 (Stress Test)...")
    report_list = []
    scenari = [("Nominale", "plus_0"), ("+10% Carico", "plus_10"), ("+20% Carico", "plus_20"),
               ("+30% Carico", "plus_30")]

    for label_sc, file_suffix in scenari:
        data = load_pkl(f'stress_test_{file_suffix}')
        if data:
            for label_m, col in METRICHE:
                values = [calcola_media_steady_state(r['samples'], col) for r in data]
                m, h = get_estimate(values)
                report_list.append(
                    {"Scenario": label_sc, "Metrica": label_m, "Media": round(m, 4), "Errore_HW": round(h, 4)})

    if report_list:
        df = pd.DataFrame(report_list)
        path = os.path.join(BASE_DIR, "report_G3_StressTest.csv")
        df.to_csv(path, index=False, sep=';')
        print(f"[OK] Salvato in: {path}")


def genera_report_G4():
    print(">>> Generazione Report Goal 4 (Hardware Upgrade)...")
    report_list = []
    # Nota: verificare che i nomi dei file corrispondano a quelli generati (up_0, up_10, etc)
    scenari = [("Upgrade 0%", "up_0"), ("Upgrade 10%", "up_10"), ("Upgrade 20%", "up_20"), ("Upgrade 30%", "up_30")]

    for label_sc, file_suffix in scenari:
        data = load_pkl(f'upgrade_{file_suffix}')
        if data:
            for label_m, col in METRICHE:
                values = [calcola_media_steady_state(r['samples'], col) for r in data]
                m, h = get_estimate(values)
                report_list.append(
                    {"Scenario": label_sc, "Metrica": label_m, "Media": round(m, 4), "Errore_HW": round(h, 4)})

    if report_list:
        df = pd.DataFrame(report_list)
        path = os.path.join(BASE_DIR, "report_G4_Upgrade.csv")
        df.to_csv(path, index=False, sep=';')
        print(f"[OK] Salvato in: {path}")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("   AVVIO GENERAZIONE REPORT STATISTICI")
    print("=" * 50)
    genera_report_G1_G2()
    genera_report_G3()
    genera_report_G4()
    print("=" * 50 + "\n")