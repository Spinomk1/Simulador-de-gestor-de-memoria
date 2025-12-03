class PageTableEntry:
    """
    Entrada individual en la tabla de páginas
    Módulo de Tabla de Páginas
    Gestiona el mapeo entre páginas lógicas y marcos físicos
    Inicializa una entrada de la tabla de páginas
    """
    
    def __init__(self, page_number):
        self.page_number = page_number
        self.frame_number = None    # Marco físico asignado
        self.valid = False          # Bit de validación (presente en RAM)
        self.in_swap = False        # Está en área de intercambio
        self.modified = False       # Bit de modificación (dirty bit)
        self.referenced = False     # Bit de referencia
    
    def __str__(self):
        if self.valid:
            location = "RAM"
            frame = self.frame_number
        elif self.in_swap:
            location = "SWAP"
            frame = self.frame_number
        else:
            location = "No asignada"
            frame = "N/A"
        
        return f"Pág {self.page_number} -> Marco {frame} ({location})"


class PageTable:
    """
    Tabla de páginas completa de un proceso
    Mantiene el mapeo entre páginas lógicas y marcos físicos
    """

    #Inicializa la tabla de páginas para un proceso
    def __init__(self, process, num_pages):
        self.process = process
        self.num_pages = num_pages
        self.entries = []
        
        # Crear todas las entradas
        for i in range(num_pages):
            self.entries.append(PageTableEntry(i))

    #Marca una página como presente en RAM
    def set_page_in_ram(self, page_number, frame_number):
        entry = self.entries[page_number]
        entry.frame_number = frame_number
        entry.valid = True
        entry.in_swap = False
        entry.referenced = True

    #   Marca una página como presente en SWAP
    def set_page_in_swap(self, page_number, frame_number):
        entry = self.entries[page_number]
        entry.frame_number = frame_number
        entry.valid = False
        entry.in_swap = True

    #Invalida una página, la marca como no presente
    def invalidate_page(self, page_number):
        entry = self.entries[page_number]
        entry.valid = False
        entry.in_swap = False
        entry.frame_number = None

    #Obtiene el marco físico de una página
    def get_frame(self, page_number):
        entry = self.entries[page_number]
        return (entry.frame_number, entry.valid)

    #Verifica si una página está en RAM
    def is_page_in_ram(self, page_number):
        return self.entries[page_number].valid

    #Verifica si una página está en SWAP
    def is_page_in_swap(self, page_number):
        return self.entries[page_number].in_swap

    #Obtiene lista de páginas presentes en RAM
    def get_pages_in_ram(self):
        return [entry.page_number for entry in self.entries if entry.valid]

    #Obtiene lista de páginas en SWAP
    def get_pages_in_swap(self):
        return [entry.page_number for entry in self.entries if entry.in_swap]

    #Obtiene información completa de la tabla
    def get_table_info(self):
        return [str(entry) for entry in self.entries]

    #Representación en string de la tabla
    def __str__(self):
        info = f"\nTabla de páginas de {self.process}:\n"
        info += "\n".join(self.get_table_info())
        return info
