import configparser
import os

class Config:
    """
    Módulo de Configuración del Simulador de Memoria
    Maneja la lectura y validación de parámetros del sistema
    Clase para gestionar la configuración del simulador
    Lee parámetros desde config.ini o usa valores por defecto
    Inicializa la configuración del sistema y ruta al archivo de configuración
    """
    
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        
        # Si no existe el archivo, crear uno por defecto
        if not os.path.exists(config_file):
            self._create_default_config(config_file)
        
        # Leer el archivo con codificación UTF-8 explícita para evitar errores en Windows
        self.config.read(config_file, encoding='utf-8')
        
        # Leer parámetros de memoria
        self.ram_size = int(self.config.get('Memory', 'ram_size', fallback=2048))
        self.swap_size = int(self.config.get('Memory', 'swap_size', fallback=4096))
        self.page_size = int(self.config.get('Memory', 'page_size', fallback=256))
        
        # Leer parámetros del sistema
        self.replacement_algorithm = self.config.get('System', 'replacement_algorithm', fallback='FIFO')
        
        # Calcular número de marcos disponibles
        self.ram_frames = self.ram_size // self.page_size
        self.swap_frames = self.swap_size // self.page_size
        
        # Validar configuración
        self._validate_config()

    """
    Si no existe crea un archivo de configuración por defecto
    Y la ruta donde crear el archivo
    """
    def _create_default_config(self, config_file):
        default_config = configparser.ConfigParser()
        
        default_config['Memory'] = {
            'ram_size': '2048',      # KB
            'swap_size': '4096',     # KB
            'page_size': '256'       # KB
        }
        
        default_config['System'] = {
            'replacement_algorithm': 'FIFO'  # FIFO o LRU
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            default_config.write(f)

    #Valida que los parámetros de configuración sean correctos
    def _validate_config(self):
        if self.ram_size <= 0:
            raise ValueError("El tamaño de RAM debe ser positivo")
        
        if self.swap_size <= 0:
            raise ValueError("El tamaño de SWAP debe ser positivo")
        
        if self.page_size <= 0:
            raise ValueError("El tamaño de página debe ser positivo")
        
        if self.page_size > self.ram_size:
            raise ValueError("El tamaño de página no puede ser mayor que la RAM")
        
        self.replacement_algorithm = 'FIFO'

    #Retorna un resumen de la configuración actual
    def get_summary(self):
        return {
            'RAM Total': f"{self.ram_size} KB",
            'SWAP Total': f"{self.swap_size} KB",
            'Tamaño de Página': f"{self.page_size} KB",
            'Marcos en RAM': self.ram_frames,
            'Marcos en SWAP': self.swap_frames,
            'Algoritmo de Reemplazo': self.replacement_algorithm
        }
