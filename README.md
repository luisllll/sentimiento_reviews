# Analizador de Sentimiento de Comentarios

Esta aplicación analiza comentarios de clientes utilizando modelos de razonamiento avanzado para proporcionar insights accionables que ayuden a mejorar productos y estrategias de marketing.

## Características Principales

- **Análisis de sentimiento**: Identifica la distribución de comentarios positivos, neutrales y negativos
- **Extracción de temas principales**: Descubre los temas más mencionados por los clientes
- **Identificación de fortalezas y áreas de mejora**: Detecta oportunidades para perfeccionar los productos
- **Recomendaciones accionables**: Recibe sugerencias priorizadas para implementar mejoras
- **Visualización clara**: Gráficos intuitivos y resumen visual de los hallazgos más importantes
- **Informe completo detallado**: Acceso al análisis completo con formato optimizado

## Cómo Funciona

### 1. Subida de Datos
1. Sube un archivo CSV que contenga una columna llamada 'Cuerpo' con los comentarios de los clientes
2. La aplicación procesa automáticamente los datos y comienza el análisis

### 2. Análisis en Profundidad
1. Los comentarios se analizan por grupos (chunks) para un procesamiento eficiente
2. Se utiliza el modelo de razonamiento o1 de OpenAI con máximo esfuerzo de análisis
3. La aplicación muestra el progreso en tiempo real durante el procesamiento

### 3. Resultados Visuales
La aplicación presenta los resultados en dos pestañas:

#### 📊 Resumen Visual
- **Distribución de Sentimiento**: Gráfico circular que muestra el porcentaje de comentarios positivos, neutrales y negativos
- **Principales Hallazgos**: 
  - **Fortalezas**: Los 3 puntos fuertes más destacados del producto
  - **Áreas de Mejora**: Los 3 aspectos que más requieren atención
- **Recomendaciones Clave**: Las 5 acciones más importantes a implementar, organizadas por prioridad

#### 📄 Informe Completo
Muestra un análisis detallado con todas las secciones:
- Sentimiento general
- Temas principales
- Fortalezas del producto
- Áreas de mejora
- Oportunidades de marketing
- Segmentación de clientes
- Recomendaciones accionables

El informe se presenta con formato optimizado para facilitar su lectura, y puede descargarse como archivo de texto.

## Configuración

### Requisitos
- Python 3.8+
- OpenAI API Key
- Bibliotecas: streamlit, pandas, openai, plotly, python-dotenv

### Instalación
1. Clona el repositorio


2. Instala las dependencias:

pip install -r requirements.txt


3. Configura tu API Key de OpenAI:
   - Crea un archivo `.env` en el directorio principal
   - Añade: `OPENAI_API_KEY=tu_api_key_aquí`

### Ejecución

streamlit run app.py



## Estructura del Proyecto


sentiment-analysis-app/
│
├── app.py                     # Punto de entrada principal
│
├── config/                    # Configuraciones de la aplicación
│   ├── settings.py            # Parámetros globales
│   └── styles.py              # Estilos CSS
│
├── services/                  # Servicios externos
│   ├── openai_service.py      # Conexión con OpenAI
│   └── file_service.py        # Manejo de archivos
│
├── utils/                     # Utilidades
│   ├── data_processing.py     # Procesamiento de datos
│   ├── metrics_extraction.py  # Extracción de métricas
│   └── visualization.py       # Visualización y formato
│
└── ui/                        # Interfaz de usuario
├── components.py          # Componentes reutilizables
├── pages.py               # Páginas principales
└── sidebar.py             # Componentes de la barra lateral



## Opciones de Configuración

En el panel lateral puedes configurar:

- **Tamaño de chunk**: Define cuántos comentarios se procesan juntos (10-200)
- **Máximo de comentarios**: Limita el número total de comentarios a analizar
- **Instrucciones personalizadas**: Ajusta las directrices para el modelo de análisis

## Notas de Uso

- **Formato CSV**: Asegúrate de que tu archivo tenga una columna llamada 'Cuerpo' con los comentarios
- **Tiempo de procesamiento**: El análisis puede tomar varios minutos dependiendo del volumen de datos
- **Costos de API**: Ten en cuenta que el uso de modelos de razonamiento consume tokens de OpenAI, lo que puede generar costos

## Ejemplos de uso

Esta herramienta es ideal para:

- Equipos de producto que quieren entender la percepción de sus clientes
- Departamentos de marketing buscando nuevas oportunidades estratégicas
- Servicio al cliente para identificar puntos de fricción recurrentes
- Desarrolladores de producto analizando el feedback de usuarios

## Mantenimiento y Personalización

Para modificaciones en la aplicación:

- **Cambiar el formato visual**: Edita `utils/visualization.py`
- **Ajustar parámetros del modelo**: Modifica `config/settings.py`
- **Personalizar la extracción de métricas**: Actualiza `utils/metrics_extraction.py`
- **Modificar la interfaz de usuario**: Edita los archivos en la carpeta `ui/`