import heapq

class Scheduler:
    def __init__(self):
        # Lista che contiene tutti gli eventi futuri (arrivi e partenze)
        # già programmati ma non ancora avvenuti
        self.event_list = []

    def schedule(self, event):
        # Aggiunta di un evento nella lista degli eventi programmati
        heapq.heappush(self.event_list, event)

    def next_event(self):
        # Estrae l'evento (ArrivalEvent o DepartureEvent) con timestamp minore dalla lista
        return heapq.heappop(self.event_list) if self.event_list else None

    def is_empty(self):
        return len(self.event_list) == 0