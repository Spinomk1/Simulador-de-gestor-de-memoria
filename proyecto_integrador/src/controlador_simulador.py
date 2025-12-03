"""
Controlador de Simulación Automática
Gestiona la creación, suspensión y terminación automática de procesos
"""
import threading
import time
import random
from generador_proceso import ProcessGenerator
from proceso import Process

class SimulationController:
    """
    Controla la simulación automática de creación y terminación de procesos
    Incluye suspensión de procesos y movimiento de páginas SWAP→RAM
    """

    def __init__(self, memory_manager, callback=None):
        """
        Inicializa el controlador de simulación
        """
        self.memory_manager = memory_manager
        self.callback = callback
        self.generator = ProcessGenerator(
            min_size=200,
            max_size=800,
            min_interval=1.5,
            max_interval=4.0
        )

        self.running = False
        self.paused = False
        self.thread = None
        self.speed = 1.0  # Velocidad de simulación

        # Tiempo de ejecución de procesos (más largos)
        self.min_exec_time = 15.0   # Segundos
        self.max_exec_time = 40.0   # Segundos

        # Probabilidades de acciones
        self.prob_create_process = 0.50     # 50% crear proceso
        self.prob_access_page = 0.25        # 25% acceder a página
        self.prob_suspend_process = 0.10    # 10% suspender proceso
        self.prob_bring_from_swap = 0.15    # 15% traer de SWAP a RAM

        # Configuración de suspensión
        self.min_suspend_time = 3.0   # Segundos mínimos suspendido
        self.max_suspend_time = 8.0   # Segundos máximos suspendido

        # Intervalo de actualización
        self.update_interval = 0.5  # Segundos entre ciclos

        # Tiempo de la última actualización
        self.last_update_time = 0

    def start(self):
        """
        Inicia la simulación
        """
        if not self.running:
            self.running = True
            self.paused = False
            self.last_update_time = time.time()
            self.thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self.thread.start()

    def pause(self):
        """
        Pausa la simulación
        """
        self.paused = True

    def resume(self):
        """
        Reanuda la simulación
        """
        self.paused = False
        self.last_update_time = time.time()

    def stop(self):
        """
        Detiene la simulación
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.generator.reset()

    def set_speed(self, speed):
        """
        Ajusta la velocidad de la simulación

        Args:
            speed (float): Velocidad (0.5 = lento, 1.0 = normal, 2.0 = rápido)
        """
        self.speed = max(0.1, min(5.0, speed))

    def _simulation_loop(self):
        """
        Bucle principal de la simulación
        """
        while self.running:
            if not self.paused:
                current_time = time.time()
                delta = (current_time - self.last_update_time) * self.speed
                self.last_update_time = current_time

                # 1. Actualizar tiempos de todos los procesos
                self._update_all_process_times(delta)

                # 2. Verificar procesos suspendidos que deben despertar
                self._wake_up_suspended_processes()

                # 3. Terminar procesos que completaron su ejecución
                self._terminate_finished_processes()

                # 4. Ejecutar acción aleatoria
                self._execute_random_action()

                # 5. Intentar traer páginas de SWAP a RAM si hay espacio
                if self.memory_manager.has_free_ram():
                    self._try_bring_pages_from_swap()

                # Notificar cambios a la GUI
                if self.callback:
                    self.callback()

                # Esperar antes del siguiente ciclo
                interval = self.update_interval / self.speed
                time.sleep(interval)
            else:
                time.sleep(0.1)

    def _update_all_process_times(self, delta):
        """
        Actualiza el tiempo en sistema de todos los procesos

        Args:
            delta (float): Tiempo transcurrido en segundos
        """
        for process in self.memory_manager.processes:
            process.update_time(delta)

    def _wake_up_suspended_processes(self):
        """
        Despierta procesos cuyo tiempo de suspensión ha terminado
        """
        for process in self.memory_manager.processes:
            if process.state == Process.SUSPENDED and process.is_suspension_over():
                # Verificar si tiene páginas en RAM
                pages_in_ram = process.page_table.get_pages_in_ram()

                if pages_in_ram:
                    process.set_state(Process.ACTIVE)
                    self.memory_manager._log_event(
                        f"{process} despertó de suspensión → ACTIVO", "INFO"
                    )
                else:
                    process.set_state(Process.SWAPPED)
                    self.memory_manager._log_event(
                        f"{process} despertó de suspensión → INTERCAMBIADO (sin páginas en RAM)", "WARNING"
                    )

    def _terminate_finished_processes(self):
        """
        Termina procesos que completaron su tiempo de ejecución
        """
        processes_to_terminate = []

        for process in self.memory_manager.processes:
            if process.is_finished():
                processes_to_terminate.append(process)

        for process in processes_to_terminate:
            # Liberar el nombre
            self.generator.release_name(process.name)

            # Terminar el proceso
            self.memory_manager.terminate_process(process.pid)

    def _execute_random_action(self):
        """
        Ejecuta una acción aleatoria según las probabilidades configuradas
        """
        rand = random.random()

        if rand < self.prob_create_process:
            # Crear nuevo proceso
            self._create_random_process()

        elif rand < self.prob_create_process + self.prob_access_page:
            # Acceder a página de proceso existente
            self._simulate_page_access()

        elif rand < self.prob_create_process + self.prob_access_page + self.prob_suspend_process:
            # Suspender un proceso aleatorio
            self._suspend_random_process()

        else:
            # Traer página de SWAP a RAM
            self._try_bring_pages_from_swap()

    def _create_random_process(self):
        """
        Crea un proceso con nombre, tamaño y tiempo de ejecución aleatorio
        """
        name = self.generator.generate_process_name()
        size = self.generator.generate_process_size()

        success, message, process = self.memory_manager.create_process(name, size)

        if success:
            # Asignar tiempo de ejecución aleatorio
            process.execution_time = random.uniform(
                self.min_exec_time / self.speed,
                self.max_exec_time / self.speed
            )
            process.time_in_system = 0.0
        else:
            # Si no se pudo crear, liberar el nombre
            self.generator.release_name(name)

    def _simulate_page_access(self):
        """
        Simula el acceso a una página de un proceso existente
        Solo procesos ACTIVOS pueden acceder a páginas
        """
        # Filtrar solo procesos activos
        active_processes = [p for p in self.memory_manager.processes
                          if p.state == Process.ACTIVE]

        if not active_processes:
            return

        process = random.choice(active_processes)

        if process.num_pages == 0:
            return

        page_num = random.randint(0, process.num_pages - 1)

        # Simular acceso
        self.memory_manager.simulate_page_access(process.pid, page_num)

    def _suspend_random_process(self):
        """
        Suspende un proceso activo aleatorio
        """
        # Filtrar solo procesos activos
        active_processes = [p for p in self.memory_manager.processes
                          if p.state == Process.ACTIVE]

        if not active_processes:
            return

        process = random.choice(active_processes)

        # Calcular tiempo de suspensión aleatorio
        suspend_duration = random.uniform(
            self.min_suspend_time / self.speed,
            self.max_suspend_time / self.speed
        )

        # Suspender el proceso
        process.suspend(suspend_duration)

        self.memory_manager._log_event(
            f"{process} SUSPENDIDO por {suspend_duration:.1f}s", "WARNING"
        )

    def _try_bring_pages_from_swap(self):
        """
        Intenta traer páginas de SWAP a RAM para procesos que las necesiten
        Esto genera FALLO DE PÁGINA pero NO SWAP
        """
        # Verificar si hay espacio libre en RAM
        if not self.memory_manager.has_free_ram():
            return

        # Buscar procesos con páginas en SWAP (priorizar INTERCAMBIADOS)
        swapped_processes = [p for p in self.memory_manager.processes
                           if p.state == Process.SWAPPED]

        # Si no hay intercambiados, buscar activos con páginas en SWAP
        if not swapped_processes:
            swapped_processes = [p for p in self.memory_manager.processes
                               if p.page_table and p.page_table.get_pages_in_swap()]

        if not swapped_processes:
            return

        # Seleccionar un proceso aleatorio
        process = random.choice(swapped_processes)

        # Obtener páginas en SWAP
        pages_in_swap = process.page_table.get_pages_in_swap()

        if not pages_in_swap:
            return

        # Traer una página aleatoria
        page_num = random.choice(pages_in_swap)

        success, msg = self.memory_manager.bring_page_from_swap_to_ram(process, page_num)

        if success:
            # Actualizar estado si era INTERCAMBIADO y ahora tiene página en RAM
            if process.state == Process.SWAPPED:
                process.set_state(Process.ACTIVE)
                self.memory_manager._log_event(
                    f"{process} cambió de INTERCAMBIADO a ACTIVO", "INFO"
                )

    #Obtiene el estado actual de la simulación
    def get_status(self):
        active = len([p for p in self.memory_manager.processes if p.state == Process.ACTIVE])
        suspended = len([p for p in self.memory_manager.processes if p.state == Process.SUSPENDED])
        swapped = len([p for p in self.memory_manager.processes if p.state == Process.SWAPPED])

        return {
            'running': self.running,
            'paused': self.paused,
            'speed': self.speed,
            'total_processes': len(self.memory_manager.processes),
            'active': active,
            'suspended': suspended,
            'swapped': swapped
        }