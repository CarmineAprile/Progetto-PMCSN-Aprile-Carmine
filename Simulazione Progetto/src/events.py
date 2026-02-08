import configurazione_sistema as config
from lib.DES import rngs, rvgs


class Event:
    def __init__(self, time):
        self.time = time

    def __lt__(self, other):
        return self.time < other.time


class ArrivalEvent(Event):
    def process(self, sim):
        from src.entities import Job
        job = Job(self.time)
        job.current_class = 'E'

        # Programmazione del prossimo arrivo
        rngs.selectStream(config.ARRIVAL_STREAM)
        interarrival = rvgs.Exponential(1.0 / sim.arrival_rate)
        sim.scheduler.schedule(ArrivalEvent(self.time + interarrival))

        # Generazione tempo di servizio per la fase biometrica (Classe E)
        rngs.selectStream(config.SERVICE_STREAMS['Edge_E'])
        service_e = rvgs.Exponential(config.SERVICE_DEMANDS['Edge']['E'])

        sim.verify_sd_sum['Edge_E'] += service_e
        sim.verify_sd_count['Edge_E'] += 1

        # Inserimento del job nel server Edge
        sim.edge.process_arrival(job, service_e)
        sim.reschedule_departures()


class DepartureEvent(Event):
    def __init__(self, time, server, version):
        super().__init__(time)
        self.server = server
        self.version = version

    def process(self, sim):
        # Rimozione del job che ha terminato il servizio attuale
        job = self.server.process_completion(self.version)
        if job is None: return

        if self.server.name == "Edge":
            if job.current_class == 'E':
                # Il job ha finito la fase biometrica, decidiamo se va al Cloud o esce
                rngs.selectStream(config.ROUTING_STREAM)
                if rngs.random() < sim.p_c:
                    # Routing verso il Cloud (diventa classe C)
                    job.current_class = 'C'
                    rngs.selectStream(config.SERVICE_STREAMS['Cloud'])
                    s_cloud = rvgs.Exponential(config.SERVICE_DEMANDS['Cloud']['C'])

                    sim.verify_sd_sum['Cloud_C'] += s_cloud
                    sim.verify_sd_count['Cloud_C'] += 1

                    # Inserimento nel Cloud
                    sim.cloud.process_arrival(job, s_cloud)
                else:
                    # Il job esce dal sistema
                    job.finish = self.time
                    sim.record_completion(job)
            else:
                # Il job ha finito la fase di Update (Classe C) ed esce definitivamente
                job.finish = self.time
                sim.record_completion(job)

        elif self.server.name == "Cloud":
            # Il job ha finito il Cloud e torna all'Edge per l'Update (Feedback)
            rngs.selectStream(config.SERVICE_STREAMS['Edge_C'])
            s_upd = rvgs.Exponential(config.SERVICE_DEMANDS['Edge']['C'])

            sim.verify_sd_sum['Edge_C'] += s_upd
            sim.verify_sd_count['Edge_C'] += 1

            # Torna all'Edge in classe C
            sim.edge.process_arrival(job, s_upd)

        # Riprogrammazione delle partenze per entrambi i server PS
        sim.reschedule_departures()