import data_generator as generator
import plot_results as plotter
import configurazione_sistema as config

def main():
    # Inizializziamo il seed una sola volta all'avvio del programma
    # Questo seed diventerà il "punto di partenza" globale
    current_global_seed = config.SEED

    while True:
        print("\n" + "=" * 50)
        print(" ---- SISTEMA DI VIDEOSORVEGLIANZA AEROPORTUALE BASATO SU SCANSIONI BIOMETRICHE ----")
        print("=" * 50)
        print(f" STATO SEED: {current_global_seed}")
        print("-" * 50)
        print("1. [SIMULA] Genera Dati")
        print("2. [ANALIZZA] Genera Grafici")
        print("0. ESCI")

        fase = input("\nSeleziona fase: ")

        if fase == '1':
            print("\n--- GENERAZIONE DATI ---")
            print("1. Scenario Base (Obiettivi 1 & 2)")
            print("2. Stress Test (Obiettivo 3)")
            print("3. Hardware Upgrade (Obiettivo 4)")
            print("0. Indietro")
            s = input("Scelta: ")

            # Aggiornando current_global_seed con il valore restituito dalle funzioni
            # la prossima simulazione inizierà dove questa è finita garantendo indipendenza
            if s == '1':
                current_global_seed = generator.run_base_scenario(current_global_seed)
            elif s == '2':
                current_global_seed = generator.run_stress_test(current_global_seed)
            elif s == '3':
                current_global_seed = generator.run_hardware_upgrade(current_global_seed)

        elif fase == '2':
            print("\n--- GENERAZIONE GRAFICI ---")
            print("1. Obiettivo 1 (Valutazione QoS RT(E))")
            print("2. Obiettivo 2 (Valutazione QoS RT(C))")
            print("3. Obiettivo 3 (Stress Test)")
            print("4. Obiettivo 4 (Effetti Potenziamento Hardware)")
            print("0. Indietro")
            s = input("Scelta: ")

            if s == '1':
                plotter.plot_goal_1()
            elif s == '2':
                plotter.plot_goal_2()
            elif s == '3':
                plotter.plot_goal_3()
            elif s == '4':
                plotter.plot_goal_4()

        elif fase == '0':
            print("Uscita in corso...")
            break
        else:
            print("Scelta non valida.")


if __name__ == "__main__":
    main()