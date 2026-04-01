# Memoria Descriptiva - PDF Processing Technical Test

## Introducción y Objetivo

El objetivo principal de este proyecto fue procesar los datos raw del archivo [BUL_EM_TM_2024000007_001.json](/raw_data/BUL_EM_TM_2024000007_001.json) (extraídos previamente con la librería PDFPlumber) para aislar y estructurar los registros de marcas correspondientes única y exclusivamente a la **Sección B.1.**.

Como resultado, el script debía producir el archivo [BUL_EM_TM_2024000007_002.json](/process_data/BUL_EM_TM_2024000007_002.json) siguiendo un esquema de datos específico y jerárquico.

## Indice

- [Introducción y Objetivo](#introducción-y-objetivo)
- [Ejecución del script](#ejecución-del-script)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Análisis del Problema y Desafíos Resueltos](#análisis-del-problema-y-desafíos-resueltos)
- [Desafíos](#desafíos)
    - [Desafío 1: Filtro de Sección](#desafío-1-filtro-de-sección)
    - [Desafío 2: Reconstrucción de Columnas](#desafío-2-reconstrucción-de-columnas)
    - [Desafío 3: Identificación de Registros](#desafío-3-identificación-de-registros)
    - [Desafío 4: Manejo de Multilinealidad y Saltos de Página](#desafío-4-manejo-de-multilinealidad-y-saltos-de-página)
- [Estructura y Limpieza del Código](#estructura-y-limpieza-del-código)
- [Pseudo-código del Proceso Lógico](#pseudo-código-del-proceso-lógico)

## Ejecución del script

Requisitos: Python 3.10+

El siguiente proceso es para clonar el repositorio y ejecutar el script sin necesidad de instalar alguna librería o framework. Se puede realizar con WSL y Ubuntu

```bash
# Clonar el repositorio
git clone https://github.com/jab9814/pdf-data-extraction.git
cd pdf-data-extraction

# Ejecutar
python pipeline.py
```

El script está programado para realizar la extracción de la información para el documento [BUL_EM_TM_2024000007_001.json](/raw_data/BUL_EM_TM_2024000007_001.json) como `objetivo principal de la prueba`, pero es funcional para la extracción del documento [BUL_EM_TM_2024000001_001.json](/raw_data/BUL_EM_TM_2024000001_001.json).

Para realizar dicha extracción, es necesario modificar el modulo [constants](/constants.py):

``` python
# Descomentar para ejecutar la extraccion del archivo BUL_EM_TM_2024000001_001 
INPUT_FILE = "raw_data/BUL_EM_TM_2024000001_001.json"
OUTPUT_FILE = "process_data/BUL_EM_TM_2024000001_002.json"

# Comentar para no ejecutar la extraccion del archivo BUL_EM_TM_2024000007_001 
# INPUT_FILE = "raw_data/BUL_EM_TM_2024000007_001.json"
# OUTPUT_FILE = "process_data/BUL_EM_TM_2024000007_002.json"
```

## Estructura del proyecto

``` bash
pdf-data-extraction
├── constants.py    # Configuraciones para la ejecución de los archivos json con terminación 001.json
├── enums.py        
├── pipeline.py     # Lógica principal del proceso
├── utils.py        # Funciones de utilidad
├── README.md       # Memoria descriptiva de la prueba
├── raw_data        # Archivos de entrada
│   ├── BUL_EM_TM_2024000001_000.pdf
│   ├── BUL_EM_TM_2024000001_001.json
│   ├── BUL_EM_TM_2024000007_000.pdf
│   └── BUL_EM_TM_2024000007_001.json
└── process_data    # Archivos generados
      ├── BUL_EM_TM_2024000001_002.pdf
      └── BUL_EM_TM_2024000007_002.json
```

## Análisis del Problema y Desafíos Resueltos

El documento presenta la particularidad de no estar serializado en el orden natural de lectura de un ser humano. Al ser extraído por PDFPlumber, la data se recibe como cajas de texto independientes y desordenadas. Fue necesario reconstruir el sentido lógico y geométrico de las páginas aplicando un enfoque analítico.

## Desafíos

### Desafío 1: Filtro de Sección

El documento completo contiene múltiples secciones que no son requeridas (A.1, B.2, etc.).

- **Solución**: Se implementó una función lectora (`get_section_pages`) para analizar secuencialmente todas las páginas del archivo. El algoritmo detecta el inicio de la sección deseada iterando los bloques de texto hasta encontrar la cadena `"B.1"`, y a partir de ahí sigue guardando las páginas hasta toparse con la cadena `"B.2"`, momento en el cual detiene la extracción. Inicialmente, al buscar esto entre los encabezados, se omitieron 11 registros, por lo cual se depuró la lógica para que inspeccionara en la totalidad de la página asegurando que ninguna entidad se omita.

### Desafío 2: Reconstrucción de Columnas

Para evitar que la información de la columna izquierda se intercale erróneamente con la de la derecha (ya que el texto en una misma línea horizontal puede compartir coordenadas de altura similares), fue imperativo definir un flujo y ordenamiento geométrico.

- **Solución**: Mediante el módulo `split_columns`, en primer lugar se descartaron ruidos innecesarios como los encabezados (`top < 60`) y los pies de página (`top >= 810`). Seguidamente, se estableció un margen divisor central validado en `x0 = 300`. Todos los bloques con `x0 < 300` se acumularon en la columna izquierda y el resto en la derecha. Finalmente, ambos grupos se ordenaron de manera ascendente utilizando su coordenada vertical central (`top`), recuperando el flujo natural de lectura descendente.

### Desafío 3: Identificación de Registros

El archivo objeto y listado no provee llaves directas ni indicios explícitos sobre la separación de cada conjunto de datos, limitándose a enumerar bloques al azar.

- **Solución**: Ya que cada código INID y su valor comparten la misma altura dentro del documento o un margen vertical casi exacto, se elaboró la función `pair_inid_values`, cuya meta es agrupar dichos bloques de texto. Iterando desde arriba hacia abajo, se une el bloque de la izquierda (menor `x0`) que funge como código, con su respectivo valor a la derecha (mayor `x0`).

Cada vez que el script se topa con un código INID `"111"` (Número de Registro), la lógica infiere inteligentemente el comienzo de una nueva solicitud y procede a almacenar el registro anterior de considerarlo cerrado.

### Desafío 4: Manejo de Multilinealidad y Saltos de Página

A causa de limitaciones en espacio por márgenes y tabulaciones originadas en el diseño del PDF, varios registros están interrumpidos por la finalización de una columna o, de plano, un salto a otra página, y campos como el `"400"` se despliegan en múltiples líneas simultáneas.

- **Solución**: En el `pipeline` de construcción de datos, se usó un control de transición. Si el cursor se desplaza leyendo bloques y detecta un campo `151` ó `400` sin haber encontrado antes un inicio de código `111` explícito al principio de la página o de la columna nueva, el algoritmo deduce que dichos valores pertenecen al registro en progreso perteneciente a la iteración anterior, y lo acumula ahí. Los códigos `400` se programaron para ser agregados sistemáticamente (apendizados en listas) y la llave de paginación (`_PAGE`) siempre registra estrictamente en dónde se originó el par `"111"` inicial.

## Estructura y Limpieza del Código

Con la idea de dejar un programa simple, escalable y siguiendo directrices y convenciones (PEP 8 y principios SOLID), el proyecto se disgregó por jerarquías:

- **`constants.py` y `enums.py`**: Mantienen encapsuladas variables mágicas (Magic Numbers) como umbrales, enumeraciones de secciones y códigos de los INID (ej: `111`, `151`).

- **`utils.py`**: Aloja lógicas neutrales, puras, matemáticas y reutilizables sobre la redimensión geométrica y separación/apilamiento en la misma coordenada `y`.

- **`pipeline.py`**: El motor orquestador y nodo final del proyecto. Recopila las piezas y aplica el procesamiento en etapas continuas hasta exportar el `.json` resuelto.

## Pseudo-código del Proceso Lógico

A continuación se detalla en formato pseudo-código cómo el algoritmo transforma los datos, haciendo especial énfasis en cómo se anidan y cortan los ciclos (loops) para mantener viva la información sin duplicarla ni perderla:

```text
1. CARGAR json de PDFPlumber ("raw_data")
2. FILTRAR páginas que pertenecen solo a la Sección B.1

3. INICIO CICLO 1: PARA CADA "página" en páginas filtradas HACER:
      a. Descartar textos que sean Encabezados (top < 60) o Pies de página (top > 810).
      b. Dividir textos restantes en: "columna_izq" (x0 < 300) y "columna_der" (x0 >= 300).
      
      4. INICIO CICLO 2: PARA CADA "columna" en [columna_izq, columna_der] HACER:
            i. Ordenar todos los textos de la columna de arriba hacia abajo (según eje vertical 'top').
            ii. Agrupar la información emparejando el Código INID con su Valor respectivo.
            
            5. INICIO CICLO 3: PARA CADA "par" (Código, Valor) en esa columna HACER:
                  
                  SI el Código es "111":
                        - CERRAR y GUARDAR el registro anterior (si es que ya había uno abierto).
                        - CREAR un nuevo registro en blanco.
                        - GUARDAR el campo "111" y la página donde originó ("_PAGE").
                  
                  SINO SI el Código es "400":
                        - AÑADIR el valor a una lista dentro del registro que esté actualmente abierto.
                        
                  SINO:
                        - GUARDAR el valor en el registro actualmente abierto (ej. "151", "210").
                        
            FIN CICLO 3 (Cuando se evalúan todos los pares, se corta y sale de esta columna).
            
      FIN CICLO 2 (Cuando se evalúan las 2 columnas, se corta y sale de esta página).
      
FIN CICLO 1 (Cuando se procesan todas las páginas de la sección, se corta el bucle principal).

6. EXPORTAR los registros acumulados a un archivo final en "process_data".
```

*Nota sobre la persistencia en los cortes:* Como el ciclo 3 y 2 terminan, pero el algoritmo aún recuerda cuál era el *registro abierto*, si un bloque de datos se corta a la mitad de una columna, continuará agregándose sin problemas en el ciclo paralelo (la columna vecina, o incluso la página siguiente) ya que caerá dentro del `SINO` al no encontrar un nuevo `'111'`.
