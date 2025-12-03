# Simulador de Gestión de Memoria RAM y SWAP

## Integrantes

- Espinosa Vázquez Cristopher
- Polanco Tijerina Jose Luis
- Ponce Medina Jesus
- Barahona Romero Billy Antonio
- Gonzalez Gonzalez Oswaldo

## Descripción

Este proyecto es un simulador de gestión de memoria virtual mediante paginación. Implementa memoria RAM, área de intercambio (SWAP), tablas de páginas por proceso, y el algoritmo de reemplazo FIFO. Incluye una interfaz gráfica que permite visualizar en tiempo real la asignación de páginas, fallos de página, y operaciones de intercambio entre RAM y SWAP.

## Cómo Compilar y Ejecutar el Simulador

### Requisitos 

- Python 3.7 o superior
- Tkinter (incluido en instalaciones estándar de Python)

### Instalar Tkinter (si es necesario)

En Linux Ubuntu o Debian:
```
sudo apt-get install python3-tk
```

En Mac:
Tkinter viene incluido con Python.

En Windows:
Tkinter viene incluido con Python.

### Ejecutar el Simulador

**Opción 1: Desde la carpeta src**

En Windows:
```
cd src
python main.py
```

En Linux o Mac:
```
cd src
python3 main.py
```

**Opción 2: Desde la raíz del proyecto**

En Windows:
```
python src/main.py
```

En Linux o Mac:
```
python3 src/main.py
```

### Configuración Opcional

Antes de ejecutar, puedes modificar el archivo config.ini ubicado en la carpeta src:

- ram_size: Tamaño de la memoria RAM en KB (valor por defecto: 8192)
- swap_size: Tamaño del área de intercambio en KB (valor por defecto: 8192)
- page_size: Tamaño de cada página en KB (valor por defecto: 256)
- replacement_algorithm: Algoritmo de reemplazo (valor fijo: FIFO)

Para ver swapping frecuente, usar ram_size pequeño como 2048. Para menos swapping, usar ram_size grande como 16384.

## Diseño del Sistema

### Estructuras de Datos Utilizadas

#### 1. Tabla de Páginas

**Archivo:** tabla_paginas.py

**Descripción:**
Cada proceso tiene su propia tabla de páginas que mapea páginas lógicas a marcos físicos. La tabla se implementa como una lista de entradas, donde cada entrada representa una página del proceso.

**Estructura de cada entrada:**
- Número de página lógica
- Número de marco físico asignado (puede ser en RAM o SWAP)
- Bit de validación que indica si la página está presente en RAM
- Flag que indica si la página está en el área de intercambio (SWAP)
- Bit de modificación (dirty bit)
- Bit de referencia

**Implementación:**
Se utiliza una lista donde el índice representa el número de página lógica. Esto permite acceso directo en tiempo constante O(1) a cualquier página. Por ejemplo, para acceder a la página número 3, simplemente se consulta la posición 3 de la lista.

**Ventajas de usar lista:**
- Acceso inmediato a cualquier página por su número
- Iteración eficiente para listar todas las páginas
- Representación clara y directa del espacio de direcciones del proceso
- Fácil de mantener y actualizar

**Operaciones principales:**
- Asignar una página en RAM: marca la entrada como válida y guarda el número de marco
- Asignar una página en SWAP: marca la entrada como no válida pero en swap
- Consultar ubicación de una página: devuelve el marco y si está en RAM o SWAP
- Invalidar una página: limpia todos los campos de la entrada

#### 2. Marcos de Memoria

**Archivo:** frame.py

**Descripción:**
Un marco representa una porción de memoria física, ya sea en RAM o en el área de intercambio. Cada marco puede estar libre u ocupado por una página de algún proceso.

**Atributos de cada marco:**
- Identificador único del marco
- Ubicación (RAM o SWAP)
- Estado: libre u ocupado
- Proceso que ocupa el marco (si está ocupado)
- Número de página lógica almacenada
- Timestamp de carga (momento en que se asignó la página)
- Timestamp de último acceso

**Implementación en el sistema:**
La memoria del sistema se representa mediante dos listas separadas:
- Primera lista: contiene todos los marcos de la memoria RAM
- Segunda lista: contiene todos los marcos del área de intercambio (SWAP)

**Razones para usar dos listas separadas:**
- Separación clara entre memoria principal y secundaria
- Facilita el cálculo de estadísticas independientes para RAM y SWAP
- Búsqueda más eficiente de marcos libres en cada área
- Representación visual más clara en la interfaz gráfica

**Operaciones principales:**
- Asignar marco: marca el marco como ocupado, registra el proceso y página, guarda timestamp
- Liberar marco: marca el marco como libre, limpia información del proceso
- Actualizar último acceso: actualiza el timestamp cuando se accede a la página

#### 3. Administrador de Memoria

**Archivo:** administrador_memoria.py

**Descripción:**
Es el componente central que coordina todas las operaciones de gestión de memoria. Mantiene el estado completo del sistema.

**Componentes principales:**
- Lista de marcos de RAM
- Lista de marcos de SWAP  
- Diccionario de procesos activos
- Instancia del algoritmo de reemplazo
- Contadores de fallos de página
- Contadores de operaciones de intercambio

**Estructura para almacenar procesos:**
Se utiliza un diccionario donde la clave es el identificador del proceso (PID) y el valor es el objeto proceso completo. Por ejemplo: proceso con PID 1 se accede como diccionario[1].

**Ventajas del diccionario:**
- Búsqueda instantánea de un proceso por su PID en tiempo constante O(1)
- Verificación rápida de existencia de un proceso
- Iteración sencilla sobre todos los procesos activos
- Eliminación eficiente cuando un proceso termina
- Garantiza que no haya duplicados de PIDs

### Algoritmo de Reemplazo Implementado

**Archivo:** algoritmo_remplazo.py

#### FIFO (First-In, First-Out)

**Principio fundamental:**
El algoritmo FIFO reemplaza la página que llegó primero a la memoria, es decir, la página más antigua. Se basa en el concepto de cola: la primera página en entrar es la primera en salir.

**Funcionamiento:**

Cuando una página se carga en un marco de RAM, se registra el momento exacto de carga mediante un timestamp. Este timestamp identifica cuándo llegó la página a memoria.

Cuando la RAM está completamente llena y llega una nueva página que necesita espacio, el algoritmo:
1. Examina todos los marcos ocupados en RAM
2. Busca el marco cuyo timestamp de carga sea el más antiguo
3. Selecciona ese marco como víctima para ser reemplazado
4. Copia el contenido de ese marco al área de intercambio (SWAP)
5. Libera el marco en RAM
6. Carga la nueva página en el marco que acaba de quedar libre
7. Actualiza el timestamp del marco con el momento actual

**Ejemplo de funcionamiento:**

Supongamos una RAM con 4 marcos y la siguiente secuencia de accesos a páginas: 1, 2, 3, 4, 1, 2, 5

Paso 1: Se carga página 1. RAM tiene 1 marco ocupado de 4.
Paso 2: Se carga página 2. RAM tiene 2 marcos ocupados de 4.
Paso 3: Se carga página 3. RAM tiene 3 marcos ocupados de 4.
Paso 4: Se carga página 4. RAM tiene 4 marcos ocupados de 4. RAM completamente llena.
Paso 5: Se accede página 1. Ya está en RAM, no hay cambios.
Paso 6: Se accede página 2. Ya está en RAM, no hay cambios.
Paso 7: Se intenta cargar página 5. RAM está llena, se necesita reemplazo.
        FIFO examina los timestamps:
        - Página 1 tiene timestamp más antiguo (llegó primero)
        - Página 1 se selecciona como víctima
        - Página 1 se mueve a SWAP
        - Página 5 ocupa el marco liberado
        
Estado final: RAM contiene páginas 5, 2, 3, 4. SWAP contiene página 1.

**Complejidad computacional:**

Complejidad temporal: O(n) donde n es el número de marcos en RAM. Esto es porque el algoritmo debe examinar todos los marcos para encontrar el que tiene el timestamp más antiguo.

Complejidad espacial: O(n) porque se crea una lista temporal con los marcos ocupados.

**Ventajas del algoritmo FIFO:**
- Simplicidad: es el algoritmo más fácil de entender e implementar
- Predecibilidad: su comportamiento es completamente determinista
- Bajo overhead: solo requiere almacenar un timestamp por marco
- Justicia: todas las páginas tienen la misma oportunidad, no hay favorecidos

**Desventajas del algoritmo FIFO:**
- Anomalía de Belady: en algunos casos, aumentar el número de marcos puede provocar más fallos de página
- Ignora patrón de uso: no considera si una página se usa frecuentemente o no
- Puede reemplazar páginas activas: la página más antigua podría estar siendo usada constantemente

### Flujo de Asignación de Páginas

Cuando se crea un nuevo proceso:

1. El sistema calcula cuántas páginas necesita el proceso dividiendo su tamaño entre el tamaño de página. Por ejemplo, un proceso de 1024 KB con páginas de 256 KB necesita 4 páginas.

2. Se crea una tabla de páginas con el número de entradas calculado. Cada entrada inicialmente no tiene marco asignado.

3. Para cada página del proceso:
   - Si hay marcos libres en RAM, se asigna un marco libre directamente
   - Si no hay marcos libres en RAM, se ejecuta el algoritmo de reemplazo FIFO
   - FIFO selecciona una página víctima (la más antigua)
   - La página víctima se copia a un marco libre en SWAP
   - Se actualiza la tabla de páginas de la página víctima marcándola en SWAP
   - El marco liberado en RAM se asigna a la nueva página
   - Se actualiza la tabla de páginas de la nueva página marcándola en RAM
   - Se incrementan los contadores de fallos de página y operaciones de swap

4. Si no hay espacio ni en RAM ni en SWAP, la página se asigna directamente a SWAP si hay marcos disponibles allí.

5. Una vez asignadas todas las páginas, el proceso queda completamente creado con su tabla de páginas configurada.

## Características del Simulador

### Funcionalidades Principales

**Simulación Automática:**
El simulador puede crear y terminar procesos automáticamente de forma continua. La velocidad de simulación es ajustable entre 0.5x (más lento) hasta 3.0x (más rápido).

**Visualización de Memoria:**
La interfaz muestra dos mapas visuales: uno para la RAM y otro para SWAP. Cada marco se representa con un color que identifica al proceso que lo ocupa. Los marcos libres se muestran en color gris.

**Gestión de Procesos:**
Se pueden crear procesos manualmente especificando nombre y tamaño. También se pueden terminar procesos manualmente seleccionándolos de una lista. Cada proceso tiene su propia tabla de páginas que puede consultarse.

**Estadísticas en Tiempo Real:**
El simulador muestra continuamente:
- Número de procesos activos
- Porcentaje de utilización de RAM
- Porcentaje de utilización de SWAP
- Total de fallos de página ocurridos
- Total de operaciones de intercambio realizadas

**Log de Eventos:**
Todos los eventos se registran en un log cronológico con tres niveles:
- INFO: eventos normales como creación de procesos y asignación de páginas
- WARNING: eventos importantes como fallos de página y operaciones de swap
- ERROR: eventos de error en el sistema

**Controles de Simulación:**
- Iniciar: comienza la simulación automática
- Pausar: pausa y reanuda la simulación
- Detener: detiene completamente la simulación
- Crear Proceso: permite crear un proceso manualmente
- Terminar Proceso: permite eliminar un proceso existente
- Ver Tabla: muestra la tabla de páginas de un proceso seleccionado

## Estructura del Proyecto

El proyecto está organizado en las siguientes carpetas y archivos:

**Carpeta src:**
Contiene todos los archivos de código fuente:
- main.py: interfaz gráfica principal y punto de entrada del programa
- administrador_memoria.py: gestor principal de RAM y SWAP
- tabla_paginas.py: implementación de tabla de páginas
- frame.py: clase que representa un marco de memoria
- algoritmo_remplazo.py: implementación del algoritmo FIFO
- proceso.py: clase que representa un proceso
- generador_proceso.py: generador automático de procesos aleatorios
- controlador_simulador.py: controlador de la simulación automática
- config.py: gestor de configuración
- config.ini: archivo de configuración del sistema

**Carpeta docs:**
Destinada para documentación adicional. En especial el manual de
usuario y el manual tecnico.

**Carpeta test:**
Destinada para archivos de prueba.

**Archivo README.md:**
Este archivo con toda la documentación del proyecto.

## Solución de Problemas Comunes

**Problema: ModuleNotFoundError al ejecutar**
Solución: Instalar Tkinter según el sistema operativo como se indicó en la sección de instalación.

**Problema: No se encuentra el archivo config.ini**
Solución: Asegurarse de ejecutar el programa desde la carpeta src o usar la ruta completa python src/main.py

**Problema: La interfaz gráfica no responde o se congela**
Solución: Reducir la velocidad de simulación, pausar y reanudar, o reiniciar el programa.
