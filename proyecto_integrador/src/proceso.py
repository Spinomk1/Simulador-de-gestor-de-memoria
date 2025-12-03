import random

class Process:
    """
    Representa un proceso en el sistema operativo simulado
    Módulo de Proceso
    Define la estructura y comportamiento de un proceso en el sistema
    """

    # Contador estático para IDs únicos
    _id_counter = 0

    # Estados posibles de un proceso
    ACTIVE = "Activo"
    SUSPENDED = "Suspendido"
    SWAPPED = "Intercambiado"

    #Inicializa un nuevo proceso
    def __init__(self, name, size, min_exec_time=10, max_exec_time=30):
        Process._id_counter += 1
        self.pid = Process._id_counter
        self.name = name
        self.size = size
        self.state = Process.ACTIVE
        self.page_table = None  # Se asignará después
        self.num_pages = 0      # Se calculará al asignar memoria
        self.page_faults = 0    # Contador de fallos de página

        # Tiempo de ejecución aleatorio
        self.execution_time = random.uniform(min_exec_time, max_exec_time)
        self.time_in_system = 0.0  # Tiempo que lleva en el sistema

        # Control de suspensión
        self.suspended_time = 0.0  # Tiempo que estará suspendido
        self.time_suspended = 0.0  # Tiempo que lleva suspendido

    #Calcula cuántas páginas necesita el proceso
    def calculate_pages(self, page_size):
        # Redondear hacia arriba si no es divisible exactamente
        self.num_pages = (self.size + page_size - 1) // page_size
        return self.num_pages

    #Cambia el estado del proceso
    def set_state(self, new_state):
        self.state = new_state

    #Suspende el proceso por un tiempo determinado
    def suspend(self, duration=5.0):
        self.state = Process.SUSPENDED
        self.suspended_time = duration
        self.time_suspended = 0.0

    #Verifica si el tiempo de suspensión terminó
    def is_suspension_over(self):
        return self.time_suspended >= self.suspended_time

    #Actualiza el tiempo del proceso
    def update_time(self, delta):
        self.time_in_system += delta

        if self.state == Process.SUSPENDED:
            self.time_suspended += delta

    #Verifica si el proceso terminó su ejecución
    def is_finished(self):
        return self.time_in_system >= self.execution_time

    #   Incrementa el contador de fallos de página
    def increment_page_fault(self):
        self.page_faults += 1

    #Representación en string del proceso
    def __str__(self):
        return f"P{self.pid}({self.name})"

    def __repr__(self):
        return self.__str__()

    #Obtiene información detallada del proceso
    def get_info(self):
        return {
            'PID': self.pid,
            'Nombre': self.name,
            'Tamaño': f"{self.size} KB",
            'Páginas': self.num_pages,
            'Estado': self.state,
            'Fallos de Página': self.page_faults,
            'Tiempo Ejecución': f"{self.execution_time:.1f}s",
            'Tiempo en Sistema': f"{self.time_in_system:.1f}s"
        }

    #Reinicia el contador de IDs
    @staticmethod
    def reset_counter():
        Process._id_counter = 0