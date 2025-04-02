"""
Componentes de la barra lateral para la interfaz de usuario.
"""
import os
import streamlit as st
import logging
from typing import Dict, Any, Tuple
from config.settings import (
    DEFAULT_CHUNK_SIZE, MIN_CHUNK_SIZE, MAX_CHUNK_SIZE, 
    DEFAULT_SYSTEM_PROMPT, DEFAULT_MODEL, DEFAULT_REASONING_EFFORT
)

# Configurar logger
logger = logging.getLogger(__name__)

def render_sidebar() -> Dict[str, Any]:
    """
    Renderiza la barra lateral con opciones de configuración.
    
    Returns:
        Diccionario con la configuración seleccionada
    """
    st.sidebar.header("⚙️ Configuración")
    
    # API Key status
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.sidebar.success("✅ API Key cargada desde archivo .env")
    else:
        st.sidebar.warning("⚠️ API Key no encontrada en archivo .env")
        api_key = st.sidebar.text_input("API Key de OpenAI (alternativa)", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            logger.info("API Key configurada manualmente")
    
    # Parámetros de procesamiento
    chunk_size = st.sidebar.slider(
        "Tamaño de cada chunk de comentarios", 
        min_value=MIN_CHUNK_SIZE, 
        max_value=MAX_CHUNK_SIZE, 
        value=DEFAULT_CHUNK_SIZE,
        help="Número de comentarios a procesar en cada grupo"
    )
    
    max_comments = st.sidebar.number_input(
        "Máximo de comentarios a analizar (0 = todos)", 
        min_value=0, 
        value=0,
        help="Limita el número total de comentarios a analizar (0 para analizar todos)"
    )
    
    # Sistema de instrucciones personalizado
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📝 Personalizar instrucciones")
    
    system_prompt = st.sidebar.text_area(
        "Instrucciones para el modelo",
        value=DEFAULT_SYSTEM_PROMPT,
        height=300
    )
    
    # Información de la aplicación
    st.sidebar.markdown("---")
    expander = st.sidebar.expander("ℹ️ Acerca de", expanded=False)
    with expander:
        st.markdown("""
        **Análisis de Sentimiento de Comentarios**
        
        Versión: 1.0.0
        
        Esta aplicación utiliza modelos de razonamiento avanzado para analizar comentarios 
        de clientes y extraer insights accionables.
        """)
    
    # Recopilar todas las opciones en un diccionario usando valores por defecto para opciones avanzadas
    config = {
        "api_key_status": bool(api_key),
        "chunk_size": chunk_size,
        "max_comments": max_comments,
        "model": DEFAULT_MODEL,
        "reasoning_effort": DEFAULT_REASONING_EFFORT,
        "column_name": "Cuerpo",  # Valor fijo
        "system_prompt": system_prompt,
        "output_format": "TXT"  # Valor fijo
    }
    
    logger.info(f"Configuración cargada: {', '.join(f'{k}={v}' for k, v in config.items() if k != 'system_prompt' and k != 'api_key_status')}")
    return config