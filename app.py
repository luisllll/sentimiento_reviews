"""
Aplicación de Análisis de Sentimiento para Comentarios de Clientes
Punto de entrada principal de la aplicación.
"""
import streamlit as st
from dotenv import load_dotenv
import logging
from config.settings import configure_app, initialize_logging
from ui.pages import render_main_page

# Configurar logging
initialize_logging()
logger = logging.getLogger(__name__)

def main():
    """Función principal que inicializa y ejecuta la aplicación Streamlit."""
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Configurar la aplicación
        configure_app()
        
        # Renderizar la página principal
        render_main_page()
        
    except Exception as e:
        logger.error(f"Error en la aplicación: {str(e)}", exc_info=True)
        st.error("Ha ocurrido un error inesperado. Por favor, contacte al administrador.")
        if st.button("Mostrar detalles del error"):
            st.exception(e)

if __name__ == "__main__":
    main()