from src.components import Scheduler
from src.entities import ps_server
from src.events import ArrivalEvent, DepartureEvent
from src.utils import compute_snapshot
import configurazione_sistema as config
from lib.DES import rngs


class Simulator:
    def __init__(self, arrival_rate, p_c, duration, warmup_time, seed):
        # Inizializzazione parametri e contatori
        self.total_arrivals = 0
        self.arrival_rate = arrival_rate
        self.p_c = p_c
        self.duration = duration
        self.warmup_time = warmup_time

        # Impostazione del seed per la replicabilità statistica
        rngs.plantSeeds(seed)
        rngs.selectStream(config.ARRIVAL_STREAM)

        # Creazione dei componenti del sistema
        self.scheduler = Scheduler()
        self.edge = ps_server("Edge")
        self.cloud = ps_server("Cloud")
        self.current_time = 0.0

        # Liste usate per l'analisi del transitorio
        # Salviamo i singoli job completati per l'analisi job-by-job.
        self.completed_e = []
        self.completed_c = []

        # Accumulatori usati durante la verifica
        self.verify_sd_sum = {'Edge_E': 0.0, 'Edge_C': 0.0, 'Cloud_C': 0.0}
        self.verify_sd_count = {'Edge_E': 0, 'Edge_C': 0, 'Cloud_C': 0}

        # Accumulatori di statistiche
        self.sum_rt_e_all = 0.0
        self.count_e_all = 0
        self.sum_rt_c_all = 0.0
        self.count_c_all = 0

        self.sum_rt_e_post = 0.0
        self.count_e_post = 0
        self.sum_rt_c_post = 0.0
        self.count_c_post = 0

        self.samples = []

    def reschedule_departures(self):
        # Ricalcolo partenze per Processor Sharing
        next_e = self.edge.next_departure_time(self.current_time)
        if next_e: self.scheduler.schedule(DepartureEvent(next_e, self.edge, self.edge.version))

        next_c = self.cloud.next_departure_time(self.current_time)
        if next_c: self.scheduler.schedule(DepartureEvent(next_c, self.cloud, self.cloud.version))

    def record_completion(self, job):
        rt = job.finish - job.birth

        # Salvataggio nelle liste per l'analisi del transitorio
        if job.current_class == 'E':
            self.completed_e.append(job)
            self.sum_rt_e_all += rt
            self.count_e_all += 1
            if self.current_time > self.warmup_time:
                self.sum_rt_e_post += rt
                self.count_e_post += 1
        else:
            self.completed_c.append(job)
            self.sum_rt_c_all += rt
            self.count_c_all += 1
            if self.current_time > self.warmup_time:
                self.sum_rt_c_post += rt
                self.count_c_post += 1

    def run(self):
        self.scheduler.schedule(ArrivalEvent(0.0))
        next_snap = 0.0

        while not self.scheduler.is_empty() and self.current_time < self.duration:
            event = self.scheduler.next_event()
            if isinstance(event, ArrivalEvent):
                self.total_arrivals += 1

            self.edge.update_progress(event.time, self.warmup_time)
            self.cloud.update_progress(event.time, self.warmup_time)
            self.current_time = event.time

            if self.current_time >= next_snap:
                snap = compute_snapshot(self.current_time, self.edge, self.cloud,
                                        self.sum_rt_e_all, self.count_e_all,
                                        self.sum_rt_c_all, self.count_c_all)
                if snap: self.samples.append(snap)
                next_snap += config.TS_STEP

            event.process(self)

        # Calcolo medie post-warmup
        avg_rt_e_post = self.sum_rt_e_post / self.count_e_post if self.count_e_post > 0 else 0
        avg_rt_c_post = self.sum_rt_c_post / self.count_c_post if self.count_c_post > 0 else 0

        return avg_rt_e_post, avg_rt_c_post, self.edge, self.cloud, self.samples, self.total_arrivals