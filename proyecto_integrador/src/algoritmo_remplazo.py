class ReplacementAlgorithm:
    """
    Algoritmo de reemplazo de páginas FIFO
    Selecciona la página que llegó primero a memoria
    Implementa FIFO (First-In, First-Out)
    """

    #Inicializa el algoritmo FIFO
    def __init__(self, algorithm_type='FIFO'):
        self.algorithm_type = 'FIFO'

    #Selecciona una página víctima para reemplazar usando FIFO
    def select_victim(self, frames):
        # Filtrar solo marcos ocupados
        occupied_frames = [f for f in frames if not f.is_free]

        if not occupied_frames:
            return None

        # Encontrar el marco con menor tiempo de carga (más antiguo)
        victim = min(occupied_frames, key=lambda f: f.load_time)
        return victim

    #Retorna el nombre del algoritmo
    def get_algorithm_name(self):
        return self.algorithm_type

    def __str__(self):
        return "Algoritmo de Reemplazo: FIFO"