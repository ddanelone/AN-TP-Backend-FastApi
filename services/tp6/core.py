# services/tp6/core.py
import time

class TP6Processor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TP6Processor, cls).__new__(cls)
            # Inicializamos tiempos
            cls._instance.execution_times = {
                "A": 0.0, "B": 0.0, "C": 0.0, "D": 0.0, "E": 0.0
            }
        return cls._instance

    def record_time(self, inciso: str, duration: float):
        """
        Guarda la duración de la ejecución.
        duration: float (segundos). Ej: 12.5
        """
        # Guardamos siempre el último tiempo de ejecución válido
        if duration > 0:
             self.execution_times[inciso] = duration

    def get_times(self):
        return self.execution_times

processor = TP6Processor()