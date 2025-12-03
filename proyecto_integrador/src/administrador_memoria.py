from frame import Frame
from tabla_paginas import PageTable
from algoritmo_remplazo import ReplacementAlgorithm
from proceso import Process
import time

class MemoryManager:
    """
    Gestor principal de memoria del sistema
    Coordina RAM, SWAP, tablas de páginas y algoritmos de reemplazo
    Inicializa el gestor de memoria
    """
    
    def __init__(self, config):
        self.config = config
        
        # Crear marcos de RAM
        self.ram_frames = []
        for i in range(config.ram_frames):
            self.ram_frames.append(Frame(i, 'RAM'))
        
        # Crear marcos de SWAP
        self.swap_frames = []
        for i in range(config.swap_frames):
            self.swap_frames.append(Frame(i, 'SWAP'))
        
        # Lista de procesos activos
        self.processes = []
        
        # Algoritmo de reemplazo
        self.replacement_algorithm = ReplacementAlgorithm(config.replacement_algorithm)
        
        # Estadísticas
        self.total_page_faults = 0
        self.total_swaps = 0
        self.event_log = []
        
        self._log_event("Sistema inicializado", "INFO")

    #Registra un evento en el log
    def _log_event(self, message, event_type="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        event = {
            'timestamp': timestamp,
            'type': event_type,
            'message': message
        }
        self.event_log.append(event)

    #Crea y carga un nuevo proceso en memoria
    def create_process(self, name, size):
        # Crear el proceso
        process = Process(name, size)
        
        # Calcular páginas necesarias
        num_pages = process.calculate_pages(self.config.page_size)
        
        self._log_event(f"Creando proceso {process} ({size} KB, {num_pages} páginas)", "INFO")
        
        # Verificar si hay espacio total (RAM + SWAP)
        total_free_frames = self._count_free_frames(self.ram_frames) + \
                           self._count_free_frames(self.swap_frames)
        
        if num_pages > total_free_frames:
            error_msg = f"No hay suficiente espacio para {process}"
            self._log_event(error_msg, "ERROR")
            return (False, error_msg, None)
        
        # Crear tabla de páginas
        page_table = PageTable(process, num_pages)
        process.page_table = page_table
        
        # Intentar asignar páginas en RAM
        success = self._allocate_process(process)
        
        if success:
            self.processes.append(process)
            msg = f"Proceso {process} cargado exitosamente"
            self._log_event(msg, "INFO")
            return (True, msg, process)
        else:
            error_msg = f"Error al cargar {process}"
            self._log_event(error_msg, "ERROR")
            return (False, error_msg, None)

    #Asigna marcos de memoria a las páginas de un proceso
    def _allocate_process(self, process):
        page_table = process.page_table
        
        for page_num in range(process.num_pages):
            # Intentar asignar en RAM primero
            free_frame = self._find_free_frame(self.ram_frames)
            
            if free_frame:
                # Asignar en RAM directamente (no es fallo de página, es primera carga)
                free_frame.allocate(process, page_num)
                page_table.set_page_in_ram(page_num, free_frame.frame_id)
                self._log_event(f"Página {page_num} de {process} asignada a Marco RAM {free_frame.frame_id}", "INFO")
            else:
                # RAM llena, necesitamos hacer swapping (esto SÍ genera fallo de página)
                swap_success = self._swap_out_and_allocate(process, page_num)
                
                if not swap_success:
                    self._log_event(f"Error al hacer swap para {process}", "ERROR")
                    return False
        
        # Proceso creado exitosamente, está ACTIVO
        process.set_state(Process.ACTIVE)
        return True

    #Simula el acceso a una página de un proceso, puede generar fallo de página
    def simulate_page_access(self, pid, page_num):
        process = self._find_process_by_pid(pid)
        
        if not process:
            return (False, f"Proceso {pid} no encontrado")
        
        if page_num >= process.num_pages:
            return (False, f"Página {page_num} no existe en el proceso")
        
        # Verificar si la página está en RAM
        if process.page_table.is_page_in_ram(page_num):
            # Página en RAM, acceso exitoso sin fallo
            # Actualizar timestamp para LRU
            frame_num, _ = process.page_table.get_frame(page_num)
            self.ram_frames[frame_num].access()
            return (True, f"Acceso exitoso a página {page_num} en RAM")
        
        elif process.page_table.is_page_in_swap(page_num):
            # Página en SWAP, hay que traerla (FALLO DE PÁGINA)
            process.increment_page_fault()
            self.total_page_faults += 1
            
            # Buscar marco libre en RAM
            free_frame = self._find_free_frame(self.ram_frames)
            
            if free_frame:
                # Hay espacio libre, traer de SWAP sin necesidad de swap-out
                old_swap_frame_num, _ = process.page_table.get_frame(page_num)
                
                # Liberar del SWAP
                self.swap_frames[old_swap_frame_num].free()
                
                # Asignar en RAM
                free_frame.allocate(process, page_num)
                process.page_table.set_page_in_ram(page_num, free_frame.frame_id)
                
                msg = f"Fallo de página: Página {page_num} de {process} traída de SWAP a RAM (sin swap-out)"
                self._log_event(msg, "WARNING")
                
                return (True, msg)
            else:
                # No hay espacio, hacer swap-out primero
                # (esto genera fallo de página + swap)
                swap_success = self._swap_out_and_bring_in(process, page_num)
                
                if swap_success:
                    msg = f"Fallo de página: Página {page_num} de {process} traída de SWAP a RAM (con swap-out)"
                    return (True, msg)
                else:
                    return (False, "Error al hacer swap")
        else:
            # Página no asignada
            process.increment_page_fault()
            self.total_page_faults += 1
            return (False, f"Fallo de página: Página {page_num} no está asignada")

    #Hace swap-out de una página y trae otra del SWAP
    def _swap_out_and_bring_in(self, process, page_to_bring):
        # Seleccionar víctima
        victim_frame = self.replacement_algorithm.select_victim(self.ram_frames)
        
        if not victim_frame:
            return False
        
        victim_process = victim_frame.process
        victim_page = victim_frame.page_number
        
        # Obtener el marco en SWAP de la página que queremos traer
        swap_frame_num, _ = process.page_table.get_frame(page_to_bring)
        
        # Mover víctima a SWAP (reusar el marco que liberamos)
        self.swap_frames[swap_frame_num].allocate(victim_process, victim_page)
        victim_process.page_table.set_page_in_swap(victim_page, swap_frame_num)
        
        # Actualizar estado del proceso víctima
        self._update_process_state(victim_process)
        
        # Incrementar contador de swaps
        self.total_swaps += 1
        
        msg = f"Swap: Página {victim_page} de {victim_process} movida a SWAP"
        self._log_event(msg, "WARNING")
        
        # Traer la página deseada a RAM
        ram_frame_id = victim_frame.frame_id
        victim_frame.allocate(process, page_to_bring)
        process.page_table.set_page_in_ram(page_to_bring, ram_frame_id)
        
        # Actualizar estado del proceso
        self._update_process_state(process)
        
        msg = f"Página {page_to_bring} de {process} traída de SWAP a RAM"
        self._log_event(msg, "INFO")
        
        return True

    #Realiza swapping: saca una página de RAM y asigna el marco liberado
    def _swap_out_and_allocate(self, new_process, new_page_num):
        # Incrementar fallos de página (intentamos acceder a una página que no está en RAM)
        new_process.increment_page_fault()
        self.total_page_faults += 1
        
        # Seleccionar víctima usando el algoritmo de reemplazo
        victim_frame = self.replacement_algorithm.select_victim(self.ram_frames)
        
        if not victim_frame:
            self._log_event("No se encontró marco víctima", "ERROR")
            return False
        
        victim_process = victim_frame.process
        victim_page = victim_frame.page_number
        
        # Buscar espacio en SWAP
        swap_frame = self._find_free_frame(self.swap_frames)
        
        if not swap_frame:
            self._log_event("SWAP lleno, no se puede hacer intercambio", "ERROR")
            return False
        
        # Mover víctima a SWAP (esto es el SWAP, diferente al fallo de página)
        swap_frame.allocate(victim_process, victim_page)
        victim_process.page_table.set_page_in_swap(victim_page, swap_frame.frame_id)
        
        # Actualizar estadísticas de swap
        self.total_swaps += 1
        
        # Verificar si el proceso víctima tiene TODAS sus páginas en SWAP ahora
        self._update_process_state(victim_process)
        
        msg = f"Página {victim_page} de {victim_process} movida a SWAP (Marco {swap_frame.frame_id}) - Algoritmo: {self.replacement_algorithm.algorithm_type}"
        self._log_event(msg, "WARNING")
        
        # Liberar marco de RAM y asignar al nuevo proceso
        old_frame_id = victim_frame.frame_id
        victim_frame.allocate(new_process, new_page_num)
        new_process.page_table.set_page_in_ram(new_page_num, victim_frame.frame_id)
        
        # Asegurar que el nuevo proceso esté ACTIVO (tiene páginas en RAM)
        new_process.set_state(Process.ACTIVE)
        
        self._log_event(f"Página {new_page_num} de {new_process} asignada a Marco RAM {old_frame_id}", "INFO")
        
        return True

    #Actualiza el estado del proceso según dónde estén sus páginas
    def _update_process_state(self, process):
        pages_in_ram = process.page_table.get_pages_in_ram()
        pages_in_swap = process.page_table.get_pages_in_swap()
        
        if len(pages_in_ram) > 0:
            # Tiene al menos una página en RAM -> ACTIVO
            process.set_state(Process.ACTIVE)
        elif len(pages_in_swap) > 0:
            # Todas las páginas están en SWAP -> INTERCAMBIADO
            process.set_state(Process.SWAPPED)
        else:
            # No tiene páginas asignadas -> SUSPENDIDO
            process.set_state(Process.SUSPENDED)

    #Termina un proceso y libera su memoria
    def terminate_process(self, pid):
        # Buscar el proceso
        process = self._find_process_by_pid(pid)
        
        if not process:
            error_msg = f"Proceso con PID {pid} no encontrado"
            self._log_event(error_msg, "ERROR")
            return (False, error_msg)
        
        # Liberar marcos de RAM
        for frame in self.ram_frames:
            if not frame.is_free and frame.process.pid == pid:
                frame.free()
        
        # Liberar marcos de SWAP
        for frame in self.swap_frames:
            if not frame.is_free and frame.process.pid == pid:
                frame.free()
        
        # Eliminar proceso de la lista
        self.processes.remove(process)
        
        msg = f"Proceso {process} terminado y memoria liberada"
        self._log_event(msg, "INFO")
        
        return (True, msg)

    #Encuentra un marco libre en una lista de marcos
    def _find_free_frame(self, frames):
        for frame in frames:
            if frame.is_free:
                return frame
        return None

    #Cuenta cuántos marcos libres hay
    def _count_free_frames(self, frames):
        return sum(1 for frame in frames if frame.is_free)

    #Busca un proceso por su PID
    def _find_process_by_pid(self, pid):
        for process in self.processes:
            if process.pid == pid:
                return process
        return None

    #Obtiene el estado actual de la RAM
    def get_ram_status(self):
        return [frame.get_info() for frame in self.ram_frames]

    #Obtiene el estado actual del SWAP
    def get_swap_status(self):
        return [frame.get_info() for frame in self.swap_frames]

    #Obtiene lista de procesos activos
    def get_process_list(self):
        return [process.get_info() for process in self.processes]

    #Obtiene estadísticas del sistema
    def get_statistics(self):
        ram_used = sum(1 for f in self.ram_frames if not f.is_free)
        ram_free = len(self.ram_frames) - ram_used
        ram_utilization = (ram_used / len(self.ram_frames) * 100) if len(self.ram_frames) > 0 else 0
        
        swap_used = sum(1 for f in self.swap_frames if not f.is_free)
        swap_free = len(self.swap_frames) - swap_used
        swap_utilization = (swap_used / len(self.swap_frames) * 100) if len(self.swap_frames) > 0 else 0
        
        return {
            'Marcos RAM Usados': f"{ram_used}/{len(self.ram_frames)}",
            'Marcos RAM Libres': ram_free,
            'Utilización RAM': f"{ram_utilization:.2f}%",
            'Marcos SWAP Usados': f"{swap_used}/{len(self.swap_frames)}",
            'Marcos SWAP Libres': swap_free,
            'Utilización SWAP': f"{swap_utilization:.2f}%",
            'Procesos Activos': len(self.processes),
            'Total Fallos de Página': self.total_page_faults,
            'Total Intercambios (Swaps)': self.total_swaps,
            'Algoritmo de Reemplazo': self.replacement_algorithm.algorithm_type
        }

    #Obtiene la tabla de páginas de un proceso
    def get_page_table(self, pid):
        process = self._find_process_by_pid(pid)
        
        if not process:
            return f"Proceso con PID {pid} no encontrado"
        
        return str(process.page_table)

    #Obtiene los últimos eventos del log
    def get_event_log(self, last_n=10):
        return self.event_log[-last_n:] if last_n > 0 else self.event_log
    
    def clear_log(self):
        """
        Limpia el log de eventos
        """
        self.event_log = []
        self._log_event("Log limpiado", "INFO")

    #Trae una página de SWAP a RAM si hay espacio libre
    def bring_page_from_swap_to_ram(self, process, page_num):
        # Verificar que la página esté en SWAP
        if not process.page_table.is_page_in_swap(page_num):
            return (False, f"Página {page_num} no está en SWAP")

        # Buscar marco libre en RAM
        free_frame = self._find_free_frame(self.ram_frames)

        if not free_frame:
            return (False, "No hay espacio libre en RAM")

        # Registrar fallo de página (intentamos acceder a página que no estaba en RAM)
        process.increment_page_fault()
        self.total_page_faults += 1

        # Obtener el marco en SWAP
        swap_frame_num, _ = process.page_table.get_frame(page_num)

        # Liberar el marco en SWAP
        self.swap_frames[swap_frame_num].free()

        # Asignar el marco libre en RAM
        free_frame.allocate(process, page_num)
        process.page_table.set_page_in_ram(page_num, free_frame.frame_id)

        # Actualizar estado del proceso
        self._update_process_state(process)

        msg = f"Página {page_num} de {process} traída de SWAP a RAM (Marco {free_frame.frame_id}) - Sin swap-out"
        self._log_event(msg, "INFO")

        return (True, msg)

    """
        Intenta traer páginas de SWAP a RAM para procesos que las necesiten
        Se ejecuta cuando hay espacio libre en RAM
    """
    def try_bring_swapped_pages_to_ram(self):
        pages_brought = 0

        # Verificar si hay espacio libre en RAM
        free_frames = self._count_free_frames(self.ram_frames)

        if free_frames == 0:
            return 0

        # Buscar procesos con páginas en SWAP
        for process in self.processes:
            if process.state == Process.SWAPPED or process.page_table:
                pages_in_swap = process.page_table.get_pages_in_swap()

                for page_num in pages_in_swap:
                    # Verificar si aún hay espacio
                    if self._count_free_frames(self.ram_frames) == 0:
                        return pages_brought

                    # Traer la página
                    success, msg = self.bring_page_from_swap_to_ram(process, page_num)

                    if success:
                        pages_brought += 1

                        # Solo traer una página por proceso por ciclo
                        break

        return pages_brought

    #Obtiene lista de procesos que tienen páginas en SWAP
    def get_processes_in_swap(self):
        swapped_processes = []

        for process in self.processes:
            if process.page_table:
                pages_in_swap = process.page_table.get_pages_in_swap()
                if pages_in_swap:
                    swapped_processes.append({
                        'process': process,
                        'pages_in_swap': len(pages_in_swap),
                        'pages_in_ram': len(process.page_table.get_pages_in_ram())
                    })

        return swapped_processes

    #Verifica si hay marcos libres en RAM
    def has_free_ram(self):
        return self._count_free_frames(self.ram_frames) > 0