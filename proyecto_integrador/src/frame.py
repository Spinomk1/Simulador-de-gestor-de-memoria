import time

class Frame:
    """
    Módulo de Marco de Memoria
    Define la estructura de un marco (frame) en RAM o SWAP
    Representa un marco de memoria física (RAM) o área de intercambio (SWAP).
    Inicializa un marco de memoria, Id unico del marco y ubicación.
    """
    def __init__(self, frame_id, location='RAM'):
        self.frame_id = frame_id
        self.location = location
        self.is_free = True
        self.process = None      # Proceso que ocupa este marco
        self.page_number = None  # Número de página lógica
        self.load_time = 0       # Timestamp de cuando se cargó (para FIFO)
        self.last_access = 0     # Timestamp de último acceso (para LRU)

    #Asigna el marco a un proceso específico, proceso que ocupará el marco y el número de páginas
    def allocate(self, process, page_number):
        self.is_free = False
        self.process = process
        self.page_number = page_number
        self.load_time = time.time()
        self.last_access = time.time()

    #Libera el marco, dejándolo disponible.
    def free(self):
        """

        """
        self.is_free = True
        self.process = None
        self.page_number = None
        self.load_time = 0
        self.last_access = 0

    #Registra un accesso al marco.
    def access(self):
        self.last_access = time.time()

    #Obtiene información del marco, devuelve la descripcion del contenido del marco.
    def get_info(self):
        if self.is_free:
            return f"[Marco {self.frame_id}: Libre]"
        else:
            return f"[Marco {self.frame_id}: {self.process}, Pág {self.page_number}]"
    
    def __str__(self):
        return self.get_info()
    
    def __repr__(self):
        return self.__str__()
