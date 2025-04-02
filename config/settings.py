"""
Configuraciones generales de la aplicación.
Contiene las configuraciones y constantes utilizadas en toda la aplicación.
"""
import os
import streamlit as st
import logging
from logging.handlers import RotatingFileHandler
from config.styles import CUSTOM_CSS

# Constantes de la aplicación
APP_TITLE = "Análisis de Sentimiento de Comentarios"
APP_ICON = "💬"
VERSION = "1.0.0"

# Configuración de OpenAI
DEFAULT_MODEL = "o1"
DEFAULT_REASONING_EFFORT = "high"
DEFAULT_MAX_TOKENS_CHUNK = 4000
DEFAULT_MAX_TOKENS_FINAL = 8000

# Configuraciones de procesamiento
DEFAULT_CHUNK_SIZE = 50
MIN_CHUNK_SIZE = 10
MAX_CHUNK_SIZE = 200

# Prompt por defecto para el sistema
DEFAULT_SYSTEM_PROMPT = """
Eres un modelo especializado en analizar el sentimiento de los comentarios de clientes a cerca de nuestros productos.
Tu objetivo es extraer insights generales de todos los comentarios, para poder mejorar los productos o realizar campañas de marketing.
Los archivos que se te proporcionan contienen las reseñas en la columna 'Cuerpo'.

Para el análisis general de comentarios, debes:
1. Identificar la distribución de sentimientos (% positivos, negativos, neutrales)
2. Extraer los temas principales mencionados y su frecuencia relativa
3. Identificar patrones comunes de quejas y elogios
4. Destacar oportunidades concretas de mejora de productos
5. Sugerir ideas específicas para campañas de marketing basadas en los comentarios
6. Identificar segmentos de clientes y sus preferencias específicas
7. Detectar tendencias emergentes o preocupaciones crecientes

Proporciona un análisis estructurado, detallado y accionable basado en todos los comentarios.
"""

# Colores para visualizaciones
SENTIMENT_COLORS = {
    'Positivo': '#4CAF50',  # Verde
    'Neutral': '#FFC107',   # Amarillo
    'Negativo': '#F44336'   # Rojo
}

def initialize_logging():
    """Configura el sistema de logging de la aplicación."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, "app.log")
    
    # Configurar logger root
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Formateo de logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def configure_app():
    """Configura la página de Streamlit y aplica estilos personalizados."""
    # Configuración de la página
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide"
    )
    
    # Aplicar estilos CSS personalizados
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Configurar estado de la sesión si no existe
    if 'is_initialized' not in st.session_state:
        st.session_state.is_initialized = True
        st.session_state.analysis_results = None