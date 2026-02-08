class Job:
    # Variabile di classe per generare ID univoci
    _id = 0

    def __init__(self, birth, class_id='E'):
        # Identificativo univoco del Job
        self.id = Job._id
        Job._id += 1
        # Istante di nascita (ingresso nel sistema)
        self.birth = birth
        # Istante di fine (uscita definitiva dal sistema)
        self.finish = None
        # Classe attuale del job ('E' o 'C')
        self.current_class = class_id
        # Tempo di servizio che il job deve ancora ricevere dal server attuale
        self.remaining = 0.0

    @staticmethod
    # Metodo per resettare il conteggio degli ID
    def reset_id():
        Job._id = 0


class ps_server:
    def __init__(self, name):
        # Nome identificativo del server (es. "Edge" o "Cloud")
        self.name = name
        # Lista dei job attualmente in fase di elaborazione
        self.jobs = []
        # Ultimo istante temporale in cui il server ha aggiornato il suo stato
        self.last_t = 0.0
        # Versione del server, incrementata a ogni arrivo/partenza per invalidare vecchi eventi programmati
        self.version = 0

        # --- Accumulatori GLOBALI (Includono il periodo di Warmup) ---
        # Tempo totale in cui il server è stato occupato da almeno un job
        self.cumulative_busy_time = 0.0
        # Integrale del numero di utenti nel tempo (Area sotto la curva N(t))
        self.area_num_in_system = 0.0

        # --- Accumulatori POST-WARMUP (Escludono il periodo di Warmup) ---
        # Tempo di occupazione registrato solo dopo la soglia di Warmup
        self.busy_time_post = 0.0
        # Area del numero di utenti registrata solo dopo la soglia di Warmup
        self.area_ni_post = 0.0

    def process_arrival(self, job, service_time):
        # Assegna al job il tempo di servizio richiesto per questa visita
        job.remaining = service_time
        # Aggiunge il job alla lista dei serviti
        self.jobs.append(job)
        # Incrementa la versione: la velocità di servizio per tutti cambia (Processor Sharing)
        self.version += 1

    def update_progress(self, now, warmup_time=0.0):
        # Calcola quanto tempo è passato dall'ultimo aggiornamento
        dt = now - self.last_t
        if dt <= 0:
            self.last_t = now
            return

        n = len(self.jobs)
        # Se ci sono job, ognuno avanza nel suo servizio in base alla capacità divisa per n
        if n > 0:
            per_job = dt / n
            for j in self.jobs:
                j.remaining -= per_job

            # Aggiornamento tempo busy globale
            self.cumulative_busy_time += dt
            # Aggiornamento tempo busy post-warmup (calcola solo la porzione di dt valida)
            if now > warmup_time:
                dt_post = now - max(self.last_t, warmup_time)
                if dt_post > 0: self.busy_time_post += dt_post

        # Aggiornamento area utenti globale (Area = n_utenti * intervallo_tempo)
        self.area_num_in_system += n * dt
        # Aggiornamento area utenti post-warmup
        if now > warmup_time:
            dt_post = now - max(self.last_t, warmup_time)
            if dt_post > 0: self.area_ni_post += n * dt_post

        # Aggiorna il timestamp dell'ultimo evento processato
        self.last_t = now

    def next_departure_time(self, now):
        # Se non ci sono job, non c'è nessuna partenza programmata
        if not self.jobs: return None
        # Trova il job a cui manca meno tempo di servizio
        min_remaining = min(j.remaining for j in self.jobs)
        # In PS, quel job finirà tra (tempo_rimanente * numero_job) secondi
        return now + (min_remaining * len(self.jobs))

    def process_completion(self, event_version):
        # Se la versione non coincide, l'evento è obsoleto e lo ignora (un arrivo ha cambiato la velocità)
        if event_version != self.version: return None
        if not self.jobs: return None
        # Estrae il job che ha effettivamente terminato
        job = min(self.jobs, key=lambda j: j.remaining)
        self.jobs.remove(job)
        # Incrementa la versione perché la velocità per i job restanti cambierà
        self.version += 1
        return job