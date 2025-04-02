"""
Utilidades para el procesamiento de datos.
"""
import pandas as pd
import logging
from typing import List, Tuple, Optional, Dict, Any

# Configurar logger
logger = logging.getLogger(__name__)

def validate_and_prepare_dataframe(df: pd.DataFrame, comment_column: str = 'Cuerpo') -> Tuple[bool, str, pd.DataFrame]:
    """
    Valida y prepara un DataFrame para el análisis.
    
    Args:
        df: DataFrame a validar y preparar
        comment_column: Nombre de la columna que contiene los comentarios
        
    Returns:
        Tupla con (éxito, mensaje, dataframe_procesado)
    """
    # Verificar que el DataFrame no es None
    if df is None:
        return False, "No se ha proporcionado un DataFrame válido", None
    
    # Verificar que la columna de comentarios existe
    if comment_column not in df.columns:
        return False, f"El archivo CSV debe contener una columna '{comment_column}'", None
    
    # Limpiar y preparar datos
    try:
        # Eliminar filas con comentarios vacíos o nulos
        df_cleaned = df.dropna(subset=[comment_column])
        df_cleaned = df_cleaned[df_cleaned[comment_column].str.strip() != '']
        
        # Verificar que quedan comentarios para analizar
        if len(df_cleaned) == 0:
            return False, f"No hay comentarios válidos en la columna '{comment_column}'", None
        
        logger.info(f"DataFrame preparado: {len(df_cleaned)} comentarios válidos")
        return True, f"DataFrame preparado con éxito: {len(df_cleaned)} comentarios válidos", df_cleaned
    
    except Exception as e:
        logger.error(f"Error al preparar DataFrame: {str(e)}")
        return False, f"Error al preparar los datos: {str(e)}", None

def split_dataframe_into_chunks(
    df: pd.DataFrame, 
    comment_column: str = 'Cuerpo', 
    chunk_size: int = 50,
    max_comments: int = 0
) -> Tuple[List[List[str]], int]:
    """
    Divide un DataFrame en chunks para su procesamiento.
    
    Args:
        df: DataFrame a dividir
        comment_column: Nombre de la columna que contiene los comentarios
        chunk_size: Tamaño de cada chunk
        max_comments: Máximo número de comentarios a procesar (0 para todos)
        
    Returns:
        Tupla con (lista_de_chunks, total_comentarios)
    """
    try:
        # Limitar número de comentarios si se especifica
        if max_comments > 0:
            df = df.head(max_comments)
        
        # Obtener lista de comentarios
        comments = df[comment_column].tolist()
        total_comments = len(comments)
        
        # Dividir en chunks
        chunks = [comments[i:i + chunk_size] for i in range(0, total_comments, chunk_size)]
        
        logger.info(f"Datos divididos en {len(chunks)} chunks (total: {total_comments} comentarios)")
        return chunks, total_comments
    
    except Exception as e:
        logger.error(f"Error al dividir DataFrame en chunks: {str(e)}")
        raise

def calculate_total_tokens(analyses: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calcula el total de tokens utilizados en el análisis.
    
    Args:
        analyses: Lista de resultados de análisis
        
    Returns:
        Diccionario con los totales de tokens
    """
    try:
        tokens_reasoning = sum(a.get("tokens_razonamiento", 0) for a in analyses if not a.get("error", False))
        total_tokens = sum(a.get("total_tokens", 0) for a in analyses if not a.get("error", False))
        
        return {
            "tokens_reasoning": tokens_reasoning,
            "total_tokens": total_tokens
        }
    except Exception as e:
        logger.error(f"Error al calcular tokens: {str(e)}")
        return {"tokens_reasoning": 0, "total_tokens": 0}