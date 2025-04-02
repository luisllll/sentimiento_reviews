"""
Servicios para interactuar con la API de OpenAI.
Proporciona funciones para analizar comentarios utilizando modelos de razonamiento.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
import streamlit as st
from config.settings import DEFAULT_MODEL, DEFAULT_REASONING_EFFORT, DEFAULT_MAX_TOKENS_CHUNK, DEFAULT_MAX_TOKENS_FINAL

# Configurar logger
logger = logging.getLogger(__name__)

class OpenAIService:
    """Clase para gestionar las interacciones con la API de OpenAI."""
    
    def __init__(self):
        """Inicializa el servicio de OpenAI."""
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Inicializa el cliente de OpenAI."""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("API Key de OpenAI no encontrada en variables de entorno")
                return
            
            self._client = OpenAI()
            logger.info("Cliente de OpenAI inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar el cliente de OpenAI: {str(e)}")
            raise
    
    @property
    def client(self) -> OpenAI:
        """Devuelve el cliente de OpenAI."""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def analyze_comments_chunk(
        self, 
        comments: List[str], 
        system_prompt: str, 
        model: str = DEFAULT_MODEL,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
        max_tokens: int = DEFAULT_MAX_TOKENS_CHUNK
    ) -> Dict[str, Any]:
        """
        Analiza un chunk de comentarios usando el modelo de OpenAI.
        
        Args:
            comments: Lista de comentarios para analizar
            system_prompt: Prompt del sistema para el modelo
            model: Modelo de OpenAI a utilizar
            reasoning_effort: Nivel de esfuerzo de razonamiento ('low', 'medium', 'high')
            max_tokens: Número máximo de tokens para la respuesta
            
        Returns:
            Dict con los resultados del análisis
        """
        logger.info(f"Analizando chunk de {len(comments)} comentarios")
        
        comments_text = "\n\n".join([f"Comentario {i+1}: {comment}" for i, comment in enumerate(comments)])
        
        chunk_prompt = f"""
        Analiza este conjunto de {len(comments)} comentarios de clientes y proporciona insights preliminares sobre:
        
        1. Distribución aproximada de sentimientos
        2. Temas principales mencionados
        3. Patrones de quejas o elogios identificados
        
        Comentarios:
        {comments_text}
        """
        
        try:
            response = self.client.responses.create(
                model=model,
                reasoning={"effort": reasoning_effort},
                input=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": chunk_prompt
                    }
                ],
                max_output_tokens=max_tokens
            )
            
            result = {
                "analysis": response.output_text,
                "tokens_razonamiento": response.usage.output_tokens_details.reasoning_tokens 
                                     if hasattr(response.usage.output_tokens_details, 'reasoning_tokens') else 0,
                "total_tokens": response.usage.total_tokens
            }
            
            logger.info(f"Análisis completado: {result['total_tokens']} tokens utilizados")
            return result
            
        except Exception as e:
            logger.error(f"Error al analizar chunk: {str(e)}")
            return {
                "analysis": f"Error: {str(e)}",
                "tokens_razonamiento": 0,
                "total_tokens": 0,
                "error": True
            }
    
    def generate_final_analysis(
        self,
        chunk_analyses: List[Dict[str, Any]],
        total_comments: int,
        chunks_count: int,
        system_prompt: str,
        model: str = DEFAULT_MODEL,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
        max_tokens: int = DEFAULT_MAX_TOKENS_FINAL
    ) -> Dict[str, Any]:
        """
        Genera el análisis final basado en los análisis de chunks.
        
        Args:
            chunk_analyses: Lista de resultados de análisis por chunks
            total_comments: Número total de comentarios analizados
            chunks_count: Número de chunks procesados
            system_prompt: Prompt del sistema para el modelo
            model: Modelo de OpenAI a utilizar
            reasoning_effort: Nivel de esfuerzo de razonamiento
            max_tokens: Número máximo de tokens para la respuesta
            
        Returns:
            Dict con los resultados del análisis final
        """
        logger.info(f"Generando análisis final para {total_comments} comentarios en {chunks_count} chunks")
        
        # Verificar si hay algún error en los chunks
        errors = [chunk for chunk in chunk_analyses if chunk.get("error", False)]
        if errors:
            logger.warning(f"Se encontraron {len(errors)} errores en los análisis por chunks")
        
        chunk_insights = "\n\n".join([
            f"--- INSIGHTS DEL GRUPO {i+1} ({chunk_analyses.index(chunk)+1} de {chunks_count}) ---\n{chunk['analysis']}"
            for i, chunk in enumerate(chunk_analyses) if not chunk.get("error", False)
        ])
        
        final_prompt = f"""
        Has analizado un total de {total_comments} comentarios de clientes en {chunks_count} grupos.
        
        Basándote en los análisis preliminares de cada grupo, proporciona un informe ejecutivo completo con:
        
        1. SENTIMIENTO GENERAL: Distribución estimada de sentimientos (% positivos, negativos, neutrales) 
           y tendencias principales
        
        2. TEMAS PRINCIPALES: Los 5-7 temas más mencionados, su frecuencia relativa y su relación con el sentimiento
        
        3. FORTALEZAS DEL PRODUCTO: Principales aspectos positivos mencionados por los clientes
        
        4. ÁREAS DE MEJORA: Principales quejas o sugerencias de mejora, ordenadas por frecuencia e impacto
        
        5. OPORTUNIDADES DE MARKETING: 3-5 ideas concretas para campañas de marketing basadas en los comentarios
        
        6. SEGMENTACIÓN: Identificación de diferentes segmentos de clientes según sus preferencias o preocupaciones
        
        7. RECOMENDACIONES ACCIONABLES: 5 recomendaciones concretas y priorizadas para mejorar la satisfacción del cliente
        
        Aquí están los insights preliminares de cada grupo:
        
        {chunk_insights}
        """
        
        try:
            response = self.client.responses.create(
                model=model,
                reasoning={"effort": reasoning_effort},
                input=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": final_prompt
                    }
                ],
                max_output_tokens=max_tokens
            )
            
            result = {
                "analysis": response.output_text,
                "tokens_razonamiento": response.usage.output_tokens_details.reasoning_tokens 
                                     if hasattr(response.usage.output_tokens_details, 'reasoning_tokens') else 0,
                "total_tokens": response.usage.total_tokens
            }
            
            logger.info(f"Análisis final completado: {result['total_tokens']} tokens utilizados")
            return result
            
        except Exception as e:
            logger.error(f"Error en análisis final: {str(e)}")
            return {
                "analysis": f"Error: {str(e)}",
                "tokens_razonamiento": 0,
                "total_tokens": 0,
                "error": True
            }

# Instancia global del servicio
openai_service = OpenAIService()