# ============================================================
#    CONFIGURAZIONE SISTEMA VIDEOSORVERGLIANZA AEROPORTO
# ============================================================


# Parametro Base
LAMBDA_BASE = 1.40

# Scenari (Moltiplicatori)
LOAD_FACTORS = {
    "standard": 1.00,
    "intermedio": 1.05,
    "pesante": 1.10,
    "critico": 1.15
}

SCENARIO = "standard"
ARRIVAL_RATE = LAMBDA_BASE * LOAD_FACTORS[SCENARIO]

SIMULATION_DURATION = 100000    # Tempo totale della simulazione 80000
WARMUP_DURATION = 15000.0   # Tempo di warmup 15000
TS_STEP = 300   # Frequenza campionamento per i grafici 300

# Probabilita di Routing p_C
PC_PROBABILITY = 0.4
# Numero di Repliche delle simulazioni
NUM_REPLICAS = 128

SEED = 123456789


SERVICE_DEMANDS = {
    'Edge': {
        'E': 0.5,   # E[Se_analisi]
        'C': 0.1    # E[Sc_update]
    },
    'Cloud': {
        'C': 0.8    # E[Sc_analisi]
    }
}


ARRIVAL_STREAM = 0  # Stream per gli arrivi
ROUTING_STREAM = 1  # Stream per il routing

SERVICE_STREAMS = {
    'Edge_E': 2,  # Stream per fase Biometrica
    'Edge_C': 3,  # Stream per fase Update (Feedback)
    'Cloud': 4    # Stream per fase Cloud
}