import pandas as pd
import matplotlib.pyplot as plt
import configurazione_sistema as config
from src.simulator import Simulator
from lib.DES import rngs


def run_transient_cumulative():
    print("=" * 80)
    print("   STUDIO DEL TRANSITORIO: MEDIA CUMULATIVA RT SISTEMA")
    print("=" * 80)

    T_DURATION = 3600 * 10
    NUM_RUNS = 5

    # Inizializziamo il primo seed
    rngs.selectStream(0)
    current_seed = config.SEED

    plt.figure(figsize=(12, 7))

    for i in range(NUM_RUNS):
        run_seed = current_seed
        print(f"Esecuzione Replica {i + 1}/{NUM_RUNS} | Seed: {run_seed}")

        sim = Simulator(
            arrival_rate=config.ARRIVAL_RATE,
            p_c=config.PC_PROBABILITY,
            duration=T_DURATION,
            warmup_time=0.0,
            seed=run_seed
        )

        sim.run()

        # Recupero del seed per la prossima replica (logica di concatenazione)
        rngs.selectStream(0)
        current_seed = rngs.getSeed()

        # Elaborazione dati
        all_jobs = sim.completed_e + sim.completed_c
        data = []
        for j in all_jobs:
            if j.finish is not None:
                data.append((j.finish, j.finish - j.birth))

        data.sort()
        df = pd.DataFrame(data, columns=['finish_time', 'rt'])
        df['cumulative_avg'] = df['rt'].expanding().mean()

        # MODIFICA: Inserimento del seed nella label della legenda
        plt.plot(df['finish_time'], df['cumulative_avg'],
                 label=f'Run {i + 1} (Seed: {run_seed})', alpha=0.8)

    # Configurazione estetica plot
    plt.title('Studio del Transitorio: Media Cumulativa del Tempo di Risposta', fontweight='bold')
    plt.xlabel('Tempo di Simulazione [s]')
    plt.ylabel('Tempo di Risposta [s]')

    # Posizioniamo la legenda all'esterno o in un angolo pulito per non coprire le curve
    plt.legend(loc='upper right', fontsize='small', framealpha=0.8)
    plt.grid(True, alpha=0.3)

    plt.savefig('analisi_transitorio_tempo_di_risposta.png')
    print(f"\n[OK] Grafico generato e salvato correttamente.")
    plt.show()


if __name__ == "__main__":
    run_transient_cumulative()