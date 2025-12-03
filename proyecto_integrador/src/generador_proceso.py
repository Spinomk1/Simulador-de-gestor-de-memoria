import random

class ProcessGenerator:
    """
    Genera procesos automáticamente con nombres y tamaños aleatorios
    Crea procesos con nombres y tamaños aleatorios para la simulación
    """
    
    # Lista de nombres de procesos comunes
    PROCESS_NAMES = [
        "Chrome", "Firefox", "Edge", "Safari",
        "VSCode", "PyCharm", "Sublime", "Atom",
        "Word", "Excel", "PowerPoint", "Outlook",
        "Photoshop", "Illustrator", "Premiere",
        "Spotify", "Discord", "Slack", "Zoom",
        "Steam", "Epic Games", "Minecraft",
        "Terminal", "CMD", "PowerShell",
        "Explorer", "Finder", "Nautilus",
        "Docker", "VirtualBox", "VMware",
        "MySQL", "PostgreSQL", "MongoDB",
        "Apache", "Nginx", "Node.js",
        "Python", "Java", "GCC",
        "Calculator", "Notepad", "Paint",
        "MediaPlayer", "Acrobat", "WinRAR"
    ]

    #Inicializa el generador
    def __init__(self, min_size=200, max_size=1000, min_interval=1.0, max_interval=3.0):
        self.min_size = min_size
        self.max_size = max_size
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.used_names = []
        self.process_counter = 0

    #Genera un nombre de proceso único
    def generate_process_name(self):
        # Intentar usar nombres disponibles
        available_names = [name for name in self.PROCESS_NAMES if name not in self.used_names]
        
        if available_names:
            name = random.choice(available_names)
        else:
            # Si se acabaron los nombres, crear uno genérico
            self.process_counter += 1
            name = f"Process_{self.process_counter}"
        
        self.used_names.append(name)
        return name

    #Genera un tamaño aleatorio para el proceso
    def generate_process_size(self):
        # La mayoría de procesos son pequeños, algunos son grandes
        if random.random() < 0.7:  # 70% procesos pequeños
            return random.randint(self.min_size, self.min_size + 300)
        else:  # 30% procesos medianos/grandes
            return random.randint(self.min_size + 300, self.max_size)

    #Calcula el intervalo hasta el próximo proceso
    def get_next_interval(self):
        return random.uniform(self.min_interval, self.max_interval)

    #Libera un nombre para que pueda ser reutilizado
    def release_name(self, name):
        if name in self.used_names:
            self.used_names.remove(name)

    #Reinicia el generador
    def reset(self):
        self.used_names = []
        self.process_counter = 0