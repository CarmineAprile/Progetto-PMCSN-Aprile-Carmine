import pickle
import numpy as np
import matplotlib.pyplot as plt
import os
import configurazione_sistema as config

BASE_DIR = "risultati_progetto"
DATA_DIR = os.path.join(BASE_DIR, "sim_results")


def load_data(filename):
    path = os.path.join(DATA_DIR, f"{filename}.pkl")
    if not os.path.exists(path): return None
    with open(path, 'rb') as f: return pickle.load(f)


def ensure_goal_dir(goal_name):
    path = os.path.join(BASE_DIR, goal_name)
    if not os.path.exists(path): os.makedirs(path)
    return path


def apply_style(title, xlabel, ylabel, soglia=None):
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)

    # OFFSET DAI BORDI: Aggiunge spazio tra (0,0) e gli assi per leggibilità
    plt.margins(x=0.05, y=0.05)

    if soglia: plt.axhline(y=soglia, color='red', linestyle='--', label=f'Soglia {soglia}s')
    plt.axvspan(0, config.WARMUP_DURATION, color='gray', alpha=0.1, label='Warmup')
    plt.legend()
    plt.tight_layout()


def plot_goal_1():
    target_dir = ensure_goal_dir("goal1")
    data = load_data('scenario_base')
    if not data: return

    time_axis = data[0]['samples']['time'].values
    # Calcolo della media d'insieme (Ensemble Average) tra le repliche
    avg_rt_e = np.mean([r['samples']['rt_e'].values for r in data], axis=0)
    avg_util_e = np.mean([r['samples']['util_e'].values for r in data], axis=0)
    avg_util_c = np.mean([r['samples']['util_c'].values for r in data], axis=0)
    avg_ni_e = np.mean([r['samples']['ni_e'].values for r in data], axis=0)
    avg_ni_c = np.mean([r['samples']['ni_c'].values for r in data], axis=0)

    plt.figure(figsize=(10, 6))
    plt.plot(time_axis, avg_rt_e, color='blue', label='RT Classe E')
    apply_style('Tempo di Risposta Job di Classe E', 'Tempo [s]', 'Tempo di Risposta [s]', 3.0)
    plt.savefig(os.path.join(target_dir, 'goal1_rt.png'))
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(time_axis, avg_util_e, label='Edge', color='green')
    plt.plot(time_axis, avg_util_c, label='Cloud', color='orange')
    apply_style('Utilizzazione Server', 'Tempo [s]', 'Utilizzazione')
    plt.savefig(os.path.join(target_dir, 'goal1_util.png'))
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(time_axis, avg_ni_e, label='Edge', color='purple')
    plt.plot(time_axis, avg_ni_c, label='Cloud', color='brown')
    apply_style('Numero di Utenti nel Sistema', 'Tempo [s]', 'N. Utenti')
    plt.savefig(os.path.join(target_dir, 'goal1_users.png'))
    plt.close()


def plot_goal_2():
    target_dir = ensure_goal_dir("goal2")
    data = load_data('scenario_base')
    if not data: return

    time_axis = data[0]['samples']['time'].values
    avg_rt_c = np.mean([r['samples']['rt_c'].values for r in data], axis=0)
    avg_util_e = np.mean([r['samples']['util_e'].values for r in data], axis=0)
    avg_util_c = np.mean([r['samples']['util_c'].values for r in data], axis=0)
    avg_ni_e = np.mean([r['samples']['ni_e'].values for r in data], axis=0)
    avg_ni_c = np.mean([r['samples']['ni_c'].values for r in data], axis=0)

    plt.figure(figsize=(10, 6))
    plt.plot(time_axis, avg_rt_c, color='cyan', label='RT Medio Classe C')
    apply_style('Tempo di Risposta Job di Classe C', 'Tempo [s]', 'Tempo di Risposta [s]', 5.0)
    plt.savefig(os.path.join(target_dir, 'goal2_rt_cloud.png'))
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(time_axis, avg_util_e, label='Edge', color='green')
    plt.plot(time_axis, avg_util_c, label='Cloud', color='orange')
    apply_style('Utilizzazione Server', 'Tempo [s]', 'Utilizzazione')
    plt.savefig(os.path.join(target_dir, 'goal2_util.png'))
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(time_axis, avg_ni_e, label='Edge', color='purple')
    plt.plot(time_axis, avg_ni_c, label='Cloud', color='brown')
    apply_style('Numero Utenti', 'Tempo [s]', 'N. Utenti')
    plt.savefig(os.path.join(target_dir, 'goal2_users.png'))
    plt.close()


def plot_goal_3():
    target_dir = ensure_goal_dir("goal3")
    sc_names = ["plus_0", "plus_10", "plus_20", "plus_30"]
    labels = ["Tasso degli Arrivi Nominale", "Tasso degli Arrivi +10%", "Tasso degli Arrivi +20%", "Tasso degli Arrivi +30%"]
    colors = ['blue', 'green', 'orange', 'red']

    # Dizionario per contenere i risultati medi di ogni scenario
    final_res = {l: {} for l in labels}
    time_axis = None

    for idx, sc in enumerate(sc_names):
        data = load_data(f'stress_test_{sc}')
        if not data: continue
        if time_axis is None: time_axis = data[0]['samples']['time'].values

        # Estrazione medie per ogni metrica dello scenario
        final_res[labels[idx]]['rt_e'] = np.mean([r['samples']['rt_e'].values for r in data], axis=0)
        final_res[labels[idx]]['rt_c'] = np.mean([r['samples']['rt_c'].values for r in data], axis=0)
        final_res[labels[idx]]['util_e'] = np.mean([r['samples']['util_e'].values for r in data], axis=0)
        final_res[labels[idx]]['util_c'] = np.mean([r['samples']['util_c'].values for r in data], axis=0)
        final_res[labels[idx]]['ni_e'] = np.mean([r['samples']['ni_e'].values for r in data], axis=0)
        final_res[labels[idx]]['ni_c'] = np.mean([r['samples']['ni_c'].values for r in data], axis=0)

    configs = [('rt_e', 'RT Classe E', 'Secondi', 'g3_rt_e.png', 3.0),
               ('rt_c', 'RT Classe C', 'Secondi', 'g3_rt_c.png', 5.0),
               ('util_e', 'Utilizzazione Server Edge', 'Utilizzazione', 'g3_util_e.png', None),
               ('util_c', 'Utilizzazione Server Cloud', 'Utilizzazione', 'g3_util_c.png', None),
               ('ni_e', 'Numero Utenti Server Edge', 'N. Utenti', 'g3_ni_e.png', None),
               ('ni_c', 'Numero Utenti Server Cloud', 'N. Utenti', 'g3_ni_c.png', None)]

    for key, title, ylabel, fname, soglia in configs:
        plt.figure(figsize=(10, 6))
        for idx, l in enumerate(labels):
            plt.plot(time_axis, final_res[l][key], color=colors[idx], label=l)
        apply_style(title, 'Tempo [s]', ylabel, soglia)
        plt.savefig(os.path.join(target_dir, fname))
        plt.close()


def plot_goal_4():
    target_dir = ensure_goal_dir("goal4")
    sc_names = ["up_0", "up_10", "up_20", "up_30"]
    labels = ["Server Edge Base", "Server Edge -10% TS", "Server Edge -20% TS", "Server Edge -30% TS"]
    colors = ['red', 'orange', 'green', 'blue']

    final_res = {l: {} for l in labels}
    time_axis = None

    for idx, sc in enumerate(sc_names):
        data = load_data(f'upgrade_{sc}')
        if not data: continue
        if time_axis is None: time_axis = data[0]['samples']['time'].values

        final_res[labels[idx]]['rt_e'] = np.mean([r['samples']['rt_e'].values for r in data], axis=0)
        final_res[labels[idx]]['rt_c'] = np.mean([r['samples']['rt_c'].values for r in data], axis=0)
        final_res[labels[idx]]['util_e'] = np.mean([r['samples']['util_e'].values for r in data], axis=0)
        final_res[labels[idx]]['util_c'] = np.mean([r['samples']['util_c'].values for r in data], axis=0)
        final_res[labels[idx]]['ni_e'] = np.mean([r['samples']['ni_e'].values for r in data], axis=0)
        final_res[labels[idx]]['ni_c'] = np.mean([r['samples']['ni_c'].values for r in data], axis=0)

    metrics = [('rt_e', 'Response Time Classe E', 'Secondi', 'g4_rt_edge.png', 3.0),
               ('rt_c', 'Response Time Classe C', 'Secondi', 'g4_rt_cloud.png', 5.0),
               ('util_e', 'Utilizzazione Server Edge', 'Utilizzazione', 'g4_util_edge.png', None),
               ('util_c', 'Utilizzazione Server Cloud', 'Utilizzazione', 'g4_util_cloud.png', None),
               ('ni_e', 'Numero Utenti Server Edge', 'N. Utenti', 'g4_ni_edge.png', None),
               ('ni_c', 'Numero Utenti Server Cloud', 'N. Utenti', 'g4_ni_cloud.png', None)]

    for key, title, ylabel, fname, soglia in metrics:
        plt.figure(figsize=(10, 6))
        for idx, l in enumerate(labels):
            plt.plot(time_axis, final_res[l][key], color=colors[idx], label=l)
        apply_style(f"{title} (Potenziamento Edge - Carico +30%)", 'Tempo [s]', ylabel, soglia)
        plt.savefig(os.path.join(target_dir, fname))
        plt.close()


if __name__ == "__main__":
    while True:
        print("\n" + "=" * 50)
        print(" PLOT MANAGER ")
        print("=" * 50)
        print("1. Genera Goal 1")
        print("2. Genera Goal 2")
        print("3. Genera Goal 3")
        print("4. Genera Goal 4")
        print("0. Esci")
        print("=" * 50)
        scelta = input("Seleziona un'opzione: ")
        if scelta == '1':
            plot_goal_1()
        elif scelta == '2':
            plot_goal_2()
        elif scelta == '3':
            plot_goal_3()
        elif scelta == '4':
            plot_goal_4()
        elif scelta == '0':
            break