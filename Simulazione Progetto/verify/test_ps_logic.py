from src.entities import ps_server, Job

def case1():
    # --------------------
    # CASO 1: Job singolo
    # --------------------
    print("\n>>> CASO 1: Job singolo (S=10s) -> Avanzamento di 6s")
    Job.reset_id()
    srv1 = ps_server("Edge")

    # arrivo di j1 all'istante 0
    j1 = Job(0.0)
    # aggiunta del job nel server
    srv1.process_arrival(j1, 10.0)

    # avanzamento di 6 secondi nell'esecuzione
    srv1.update_progress(6.0)
    # Atteso: 10 - 6 = 4
    print(f"  [J1] Residuo: {j1.remaining:.2f} | Atteso: 4.00")
    # all'istante 6 mancano 4s di servizio -> la partenza del Job è prevista a 10s
    print(f"  [Srv] Prossima Partenza: {srv1.next_departure_time(6.0):.2f} | Attesa: 10.00")

def case2():
    # -------------------------------------------------------
    # CASO 2: Due Job simultanei (Velocità 1/2 per ciascuno)
    # -------------------------------------------------------
    print("\n>>> CASO 2: Due Job simultanei (S=10s ciascuno) -> Avanzamento di 6s")
    Job.reset_id()
    srv2 = ps_server("Edge")

    # arrivo di due Job all'istante 0
    ja = Job(0.0)
    jb = Job(0.0)
    # aggiunta dei Job al server
    srv2.process_arrival(ja, 10.0)
    srv2.process_arrival(jb, 10.0)

    # avanzamento di 6s nell'esecuzione
    srv2.update_progress(6.0)

    # Atteso: Ogni job riceve 6s / 2 = 3s di servizio. Residuo: 10 - 3 = 7
    print(f"  [JA] Residuo: {ja.remaining:.2f} | Atteso: 7.00")
    print(f"  [JB] Residuo: {jb.remaining:.2f} | Atteso: 7.00")
    # Entrambi finirebbero dopo 20s totali (10s di lavoro a testa / 0.5 velocità)
    print(f"  [Srv] Prossima Partenza: {srv2.next_departure_time(6.0):.2f} | Attesa: 20.00")


def case3():
    # ------------------------------------------------------------------
    # CASO 3: Arrivi scaglionati (J1 a t=0, J2 a t=2) -> Controllo a t=6
    # ------------------------------------------------------------------
    print("\n>>> CASO 3: Arrivi asincroni (J1 t=0 S=10, J2 t=2 S=10) -> Controllo Stato di esecuzione a t=6")
    Job.reset_id()
    srv3 = ps_server("Edge")

    # t=0: J1 arriva
    j1_c3 = Job(0.0)
    # aggiunta del job al server
    srv3.process_arrival(j1_c3, 10.0)

    # Prima di aggiungere J2 al server avanziamo con l'esecuzione di J1
    srv3.update_progress(2.0)
    # t=2: arrivo del secondo Job
    j2_c3 = Job(2.0)
    # aggiunta di J2 al server
    srv3.process_arrival(j2_c3, 10.0)

    # t=6: avanziamo all'istante t=6s e verifichiamo cosa succede dopo i 4s di coesistenza all'interno del server
    srv3.update_progress(6.0)

    # Calcolo J1: (2s da solo * 1) + (4s in coppia * 0.5) = 4s ricevuti. Residuo Atteso: 10-4 = 6
    # Calcolo J2: (4s in coppia * 0.5) = 2s ricevuti. Residuo Atteso: 10-2 = 8
    print(f"  [J1] Residuo: {j1_c3.remaining:.2f} | Atteso: 6.00")
    print(f"  [J2] Residuo: {j2_c3.remaining:.2f} | Atteso: 8.00")

def case4():
    # ----------------------------------------------------------
    # TEST UNITARIO 4: Validazione del Meccanismo di Versioning
    # ----------------------------------------------------------
    print("\n[TEST 4] Verifica della protezione da Preemption (Versioning)")
    srv = ps_server("Edge")

    print(f"Initial Server Version: {srv.version}")
    # J1 (t=0s S=5s)
    print("t=0: Arrivo di J1 (S=5s)")
    srv.process_arrival(Job(0.0), 5.0)
    version_departure_J1 = srv.version
    print(f"New Server Version after J1 arrival: {srv.version}")
    print(
        f"Aggiungere alla lista degli Eventi -> Next Departure: {srv.next_departure_time(0.0)} - Version: {version_departure_J1}")

    # avanzamento fino all'arrivo di J2
    srv.update_progress(1.0)
    print("t=1: Arrivo di J2 (S=10s)")
    srv.process_arrival(Job(1.0), 10.0)
    actual_version = srv.version
    print(f"New Server Version after J2 arrival: {actual_version}")

    # A questo punto il tempo di conclusione di J1 è aumentato
    # Ma avevamo già aggiunto alla lista degli eventi futuri la sua departure all'istante t=5s

    srv.update_progress(5.0)
    # A questo punto viene processato il completamento della partenza di J1
    # che era stata precedentemente aggiunta alla Future Event List
    esito_departure = srv.process_completion(version_departure_J1)
    # Con l'arrivo di J2 è aumentato il tempo di partenza reale di J1 dunque
    # la departure precedentemente programmata deve essere scartata
    print(f"Esito Departure t=5.0s -> Atteso: Discarded | Osservato: {"Discarded" if esito_departure is None else "Confirmed"}")

def case5():
    # -----------------------------------------------------------
    # TEST UNITARIO 5: Ritorno a velocità piena dopo una partenza
    # -----------------------------------------------------------
    print("\n[TEST 5] Verifica accelerazione dopo partenza (n=2 -> n=1)")
    Job.reset_id()
    srv = ps_server("Edge")

    # t=0: Arrivano J1 (S=5) e J2 (S=1)
    j1 = Job(0.0)
    j2 = Job(0.0)
    print("Arrivo di J1 (t=0.0 S=5.0)")
    print("Arrivo di J2 (t=0.0 S=10.0)")
    srv.process_arrival(j1, 5.0)
    srv.process_arrival(j2, 10.0)
    version_departure_J1 = srv.version

    # Se lavorano insieme i tempi di esecuzione sono raddoppiati
    # Ne segue che Departure J1: 10s e Departure J2: 20s
    print("J1 viene completato all'istante t=10s")

    # Avanziamo fino alla partenza di J1
    srv.update_progress(10.0)
    srv.process_completion(version_departure_J1)

    # Essendo J2 da solo adesso riceve maggiore Servizio rispetto a prima e il suo
    # departure time diventa 15s
    print(f"Departure Time J2 dopo la partenza di J1 -> Valore Atteso: 15s | Valore osservato: {srv.next_departure_time(10.0)}")

if __name__ == "__main__":
    while True:
        print("\n" + "="*50 + "\n      Verifica Comportamento PS\n" + "="*50)
        print("1. Scenario: Job singolo\n"
              "2. Scenario: Job Simultanei Concorrenti\n"
              "3. Scenario: Job Asincroni Concorrenti\n"
              "4. Scenario: Validazione del Sistema di Versione del Server PS\n"
              "5. Scenario: Verifica della Riassegnazione della Capacità\n"
              "0. ESCI\n")
        fase = input("\nSeleziona Scenario Test: ")
        if fase == '1':
            case1()
        elif fase == '2':
            case2()
        elif fase == '3':
            case3()
        elif fase == '4':
            case4()
        elif fase == '5':
            case5()
        elif fase == '0': break