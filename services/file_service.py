"""
Servicios para el manejo de archivos.
Proporciona funciones para guardar y cargar archivos.
"""
import os
import logging
from datetime import datetime
from typing import Optional, TextIO

# Configurar logger
logger = logging.getLogger(__name__)

class FileService:
    """Clase para gestionar operaciones con archivos."""
    
    @staticmethod
    def save_analysis_to_file(analysis: str, output_dir: str = "outputs") -> str:
        """
        Guarda el análisis en un archivo de texto.
        
        Args:
            analysis: Texto del análisis a guardar
            output_dir: Directorio donde guardar el archivo
            
        Returns:
            Ruta completa al archivo guardado
        """
        # Crear directorio si no existe
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Directorio '{output_dir}' creado")
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analisis_sentimiento_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(analysis)
            logger.info(f"Análisis guardado en '{filepath}'")
            return filepath
        except Exception as e:
            logger.error(f"Error al guardar el análisis: {str(e)}")
            raise
    
    @staticmethod
    def get_file_handle(filepath: str) -> Optional[TextIO]:
        """
        Obtiene un handle para leer un archivo.
        
        Args:
            filepath: Ruta al archivo
            
        Returns:
            Handle de archivo abierto o None en caso de error
        """
        try:
            return open(filepath, "r", encoding="utf-8")
        except Exception as e:
            logger.error(f"Error al abrir el archivo '{filepath}': {str(e)}")
            return None

# Instancia global del servicio
file_service = FileService()