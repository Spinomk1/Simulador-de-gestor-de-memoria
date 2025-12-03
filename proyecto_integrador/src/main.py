import tkinter as tk
from tkinter import ttk, scrolledtext
from config import Config
from administrador_memoria import MemoryManager
from controlador_simulador import SimulationController

class MemorySimulatorGUI:
    """
    Interfaz gráfica principal del simulador
    Muestra la simulación automática de gestión de memoria RAM y SWAP
    """
    
    # Colores para los diferentes procesos
    COLORS = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", 
        "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E2",
        "#F8B739", "#52B788", "#E76F51", "#2A9D8F",
        "#E9C46A", "#F4A261", "#E76F51", "#264653"
    ]
    #Inicializa la interfaz gráfica

    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Gestión de Memoria RAM y SWAP")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Inicializar componentes del simulador
        self.config = Config()
        self.memory_manager = MemoryManager(self.config)
        self.simulation = SimulationController(self.memory_manager, self.update_display)
        
        # Mapeo de procesos a colores
        self.process_colors = {}
        self.color_index = 0
        
        # Variable para controlar actualizaciones
        self.updating = False
        
        # Crear interfaz
        self.create_widgets()
        
        # Iniciar actualización automática
        self.auto_update()

    #Crea todos los widgets de la interfaz
    def create_widgets(self):

        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # - TÍTULO -
        title_frame = tk.Frame(main_frame, bg="#2C3E50", height=60)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="SIMULADOR DE GESTIÓN DE MEMORIA RAM Y SWAP",
            font=("Arial", 16, "bold"),
            bg="#2C3E50",
            fg="white"
        )
        title_label.pack(expand=True)
        
        # - PANEL DE CONTROL -
        control_frame = tk.LabelFrame(
            main_frame,
            text=" Control de Simulación ",
            font=("Arial", 10, "bold"),
            bg="white",
            relief=tk.RIDGE,
            borderwidth=2
        )
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame interno para botones
        buttons_frame = tk.Frame(control_frame, bg="white")
        buttons_frame.pack(pady=10, padx=10)
        
        self.btn_start = tk.Button(
            buttons_frame,
            text="▶ Iniciar",
            command=self.start_simulation,
            bg="#27AE60",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            height=2,
            cursor="hand2"
        )
        self.btn_start.grid(row=0, column=0, padx=5)
        
        self.btn_pause = tk.Button(
            buttons_frame,
            text="⏸ Pausar",
            command=self.pause_simulation,
            bg="#F39C12",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            height=2,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.btn_pause.grid(row=0, column=1, padx=5)
        
        self.btn_stop = tk.Button(
            buttons_frame,
            text="⏹ Detener",
            command=self.stop_simulation,
            bg="#E74C3C",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            height=2,
            cursor="hand2",
            state=tk.DISABLED
        )

        self.btn_stop.grid(row=0, column=2, padx=5)
        
        # Control de velocidad
        speed_frame = tk.Frame(control_frame, bg="white")
        speed_frame.pack(pady=(0, 10))
        
        tk.Label(speed_frame, text="Velocidad:", bg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = tk.Scale(
            speed_frame,
            from_=0.5,
            to=3.0,
            resolution=0.5,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self.change_speed,
            length=200,
            bg="white"
        )
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        
        self.speed_label = tk.Label(speed_frame, text="1.0x", bg="white", font=("Arial", 9, "bold"))
        self.speed_label.pack(side=tk.LEFT, padx=5)
        
        # - CONTENIDO PRINCIPAL -
        content_frame = tk.Frame(main_frame, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame izquierdo (Memoria)
        left_frame = tk.Frame(content_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # RAM
        self.ram_frame = tk.LabelFrame(
            left_frame,
            text=" MEMORIA RAM ",
            font=("Arial", 10, "bold"),
            bg="white",
            relief=tk.RIDGE,
            borderwidth=2
        )
        self.ram_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.ram_canvas = tk.Canvas(self.ram_frame, bg="white", highlightthickness=0)
        self.ram_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # SWAP
        self.swap_frame = tk.LabelFrame(
            left_frame,
            text=" ÁREA DE  INTERCAMBIO (SWAP) ",
            font=("Arial", 10, "bold"),
            bg="white",
            relief=tk.RIDGE,
            borderwidth=2
        )
        self.swap_frame.pack(fill=tk.BOTH, expand=True)
        
        self.swap_canvas = tk.Canvas(self.swap_frame, bg="white", highlightthickness=0)
        self.swap_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame derecho (Procesos y Log)
        right_frame = tk.Frame(content_frame, bg="#f0f0f0", width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # Estadísticas
        stats_frame = tk.LabelFrame(
            right_frame,
            text=" Estadísticas ",
            font=("Arial", 10, "bold"),
            bg="white",
            relief=tk.RIDGE,
            borderwidth=2
        )
        stats_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.stats_text = tk.Text(
            stats_frame,
            height=8,
            bg="white",
            font=("Courier", 9),
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.stats_text.pack(padx=10, pady=10, fill=tk.X)
        
        # Procesos activos
        process_frame = tk.LabelFrame(
            right_frame,
            text=" Procesos Activos ",
            font=("Arial", 10, "bold"),
            bg="white",
            relief=tk.RIDGE,
            borderwidth=2
        )
        process_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Treeview para procesos
        self.process_tree = ttk.Treeview(
            process_frame,
            columns=("PID", "Nombre", "Páginas", "Estado"),
            show="headings",
            height=8
        )
        self.process_tree.heading("PID", text="PID")
        self.process_tree.heading("Nombre", text="Nombre")
        self.process_tree.heading("Páginas", text="Pág")
        self.process_tree.heading("Estado", text="Estado")
        
        self.process_tree.column("PID", width=40)
        self.process_tree.column("Nombre", width=120)
        self.process_tree.column("Páginas", width=50)
        self.process_tree.column("Estado", width=80)
        
        process_scroll = ttk.Scrollbar(process_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=process_scroll.set)
        
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        process_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        # Log de eventos
        log_frame = tk.LabelFrame(
            right_frame,
            text=" Log de Eventos ",
            font=("Arial", 10, "bold"),
            bg="white",
            relief=tk.RIDGE,
            borderwidth=2
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            bg="white",
            font=("Courier", 8),
            wrap=tk.WORD
        )
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Tags para colores en el log
        self.log_text.tag_config("INFO", foreground="#2ECC71")
        self.log_text.tag_config("WARNING", foreground="#F39C12")
        self.log_text.tag_config("ERROR", foreground="#E74C3C")

    #Obtiene o asigna un color para un proceso
    def get_process_color(self, process):
        if process.pid not in self.process_colors:
            self.process_colors[process.pid] = self.COLORS[self.color_index % len(self.COLORS)]
            self.color_index += 1
        return self.process_colors[process.pid]

    #Dibuja la visualización de memoria
    def draw_memory(self, canvas, frames, title):
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Calcular disposición
        num_frames = len(frames)
        cols = max(1, int((width - 20) / 80))
        rows = (num_frames + cols - 1) // cols
        
        frame_width = min(70, (width - 20 - (cols - 1) * 10) // cols)
        frame_height = min(40, (height - 20 - (rows - 1) * 10) // rows)
        
        # Dibujar marcos
        for i, frame in enumerate(frames):
            row = i // cols
            col = i % cols
            
            x = 10 + col * (frame_width + 10)
            y = 10 + row * (frame_height + 10)
            
            # Color según estado
            if frame.is_free:
                color = "#E8E8E8"
                text_color = "#999999"
                text = f"Libre"
            else:
                color = self.get_process_color(frame.process)
                text_color = "white"
                text = f"{frame.process}\nPág {frame.page_number}"
            
            # Dibujar rectángulo
            canvas.create_rectangle(
                x, y, x + frame_width, y + frame_height,
                fill=color,
                outline="#333333",
                width=1
            )
            
            # Dibujar texto
            canvas.create_text(
                x + frame_width // 2,
                y + frame_height // 2,
                text=text,
                fill=text_color,
                font=("Arial", 8, "bold")
            )
    #Actualiza toda la visualización
    def update_display(self):
        if self.updating:
            return
        
        self.updating = True
        
        try:
            # Actualizar visualización de RAM
            self.draw_memory(self.ram_canvas, self.memory_manager.ram_frames, "RAM")
            
            # Actualizar visualización de SWAP
            self.draw_memory(self.swap_canvas, self.memory_manager.swap_frames, "SWAP")
            
            # Actualizar estadísticas
            stats = self.memory_manager.get_statistics()
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            
            stats_text = ""
            stats_text += f"RAM: {stats['Utilización RAM']}\n"
            stats_text += f"SWAP: {stats['Utilización SWAP']}\n"
            stats_text += f"Procesos: {stats['Procesos Activos']}\n"
            stats_text += f"Fallos Página: {stats['Total Fallos de Página']}\n"
            stats_text += f"Swaps: {stats['Total Intercambios (Swaps)']}\n"
            stats_text += f"Algoritmo: {stats['Algoritmo de Reemplazo']}\n"
            
            self.stats_text.insert(1.0, stats_text)
            self.stats_text.config(state=tk.DISABLED)
            
            # Actualizar lista de procesos
            self.process_tree.delete(*self.process_tree.get_children())
            for proc_info in self.memory_manager.get_process_list():
                self.process_tree.insert(
                    "",
                    tk.END,
                    values=(
                        proc_info['PID'],
                        proc_info['Nombre'],
                        proc_info['Páginas'],
                        proc_info['Estado']
                    )
                )
            
            # Actualizar log (solo los últimos 5 eventos)
            events = self.memory_manager.get_event_log(last_n=5)
            for event in events[-5:]:
                event_text = f"[{event['timestamp']}] {event['message']}\n"
                self.log_text.insert(tk.END, event_text, event['type'])
                self.log_text.see(tk.END)
        
        finally:
            self.updating = False

    #Actualización automática periódica cada 500 ms
    def auto_update(self):
        self.update_display()
        self.root.after(500, self.auto_update)

    #Inicia la simulación
    def start_simulation(self):
        self.simulation.start()
        self.btn_start.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.NORMAL, text="⏸ Pausar")
        self.btn_stop.config(state=tk.NORMAL)

    #Pausa o reanuda la simulación
    def pause_simulation(self):
        if self.simulation.paused:
            self.simulation.resume()
            self.btn_pause.config(text="⏸ Pausar")
        else:
            self.simulation.pause()
            self.btn_pause.config(text="▶ Reanudar")

    #Detiene la simulación
    def stop_simulation(self):
        self.simulation.stop()
        self.btn_start.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED, text="⏸ Pausar")
        self.btn_stop.config(state=tk.DISABLED)
        
        # Limpiar todos los procesos
        for process in list(self.memory_manager.processes):
            self.memory_manager.terminate_process(process.pid)
        
        self.process_colors.clear()
        self.color_index = 0
        self.update_display()

    #Cambia la velocidad de la simulación
    def change_speed(self, value):
        speed = float(value)
        self.simulation.set_speed(speed)
        self.speed_label.config(text=f"{speed:.1f}x")


def main():
    root = tk.Tk()
    app = MemorySimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
