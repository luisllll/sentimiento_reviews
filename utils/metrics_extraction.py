"""
Utilidades para extraer métricas de los análisis.
"""
import re
import logging
from typing import Dict, List, Any

# Configurar logger
logger = logging.getLogger(__name__)

def extract_metrics_from_analysis(analysis_text: str) -> Dict[str, Any]:
    """
    Extrae métricas clave del texto de análisis para visualización.
    
    Args:
        analysis_text: Texto del análisis
        
    Returns:
        Diccionario con métricas extraídas
    """
    logger.info("Extrayendo métricas del análisis")
    
    # Inicializar estructura de métricas
    metrics = {
        "sentiment_distribution": {
            "Positivo": 0,
            "Neutral": 0,
            "Negativo": 0
        },
        "top_themes": [],
        "strengths": [],
        "improvements": []
    }
    
    try:
        # Extraer distribución de sentimiento usando expresiones regulares
        
        # Buscar porcentajes positivos
        positive_matches = re.findall(r'(?:positiv[oa]s?|favorables?)\D*?(\d+(?:\.\d+)?)%', analysis_text, re.IGNORECASE)
        if positive_matches:
            metrics["sentiment_distribution"]["Positivo"] = float(positive_matches[0])
        
        # Buscar porcentajes negativos
        negative_matches = re.findall(r'(?:negativ[oa]s?|desfavorables?)\D*?(\d+(?:\.\d+)?)%', analysis_text, re.IGNORECASE)
        if negative_matches:
            metrics["sentiment_distribution"]["Negativo"] = float(negative_matches[0])
        
        # Buscar porcentajes neutrales
        neutral_matches = re.findall(r'(?:neutral(?:es)?)\D*?(\d+(?:\.\d+)?)%', analysis_text, re.IGNORECASE)
        if neutral_matches:
            metrics["sentiment_distribution"]["Neutral"] = float(neutral_matches[0])
        
        # Si no hay coincidencias, usar valores predeterminados
        total = sum(metrics["sentiment_distribution"].values())
        if total == 0:
            logger.warning("No se encontraron porcentajes de sentimiento, usando valores predeterminados")
            metrics["sentiment_distribution"] = {"Positivo": 60, "Neutral": 25, "Negativo": 15}
        elif total != 100:
            # Normalizar a 100%
            logger.info(f"Normalizando porcentajes de sentimiento (total actual: {total}%)")
            factor = 100 / total
            for key in metrics["sentiment_distribution"]:
                metrics["sentiment_distribution"][key] *= factor
        
        # Intentar extraer temas principales
        # Ejemplo de patrón: "Los temas principales son: calidad (45%), precio (30%), servicio (25%)"
        themes_section = re.search(r'(?:temas|aspectos)(?:\s+principales|\s+más\s+mencionados).*?(?:\:|\n)(.*?)(?:\n\n|\n[A-Z])', 
                                 analysis_text, re.IGNORECASE | re.DOTALL)
        
        if themes_section:
            themes_text = themes_section.group(1)
            # Extraer temas individuales
            theme_matches = re.findall(r'([a-zá-úñ\s]+)(?:\s*\((\d+(?:\.\d+)?)%\))?', themes_text, re.IGNORECASE)
            
            if theme_matches:
                for theme, percentage in theme_matches:
                    theme = theme.strip()
                    if theme and not theme.isspace() and len(theme) > 2:
                        perc = float(percentage) if percentage else 0
                        metrics["top_themes"].append({"name": theme, "percentage": perc})
        
        logger.info(f"Métricas extraídas: {len(metrics['sentiment_distribution'])} sentimientos, {len(metrics['top_themes'])} temas")
        return metrics
        
    except Exception as e:
        logger.error(f"Error al extraer métricas: {str(e)}")
        # Devolver métricas predeterminadas en caso de error
        return {
            "sentiment_distribution": {"Positivo": 60, "Neutral": 25, "Negativo": 15},
            "top_themes": [],
            "strengths": [],
            "improvements": []
        }

def extract_key_sections(analysis_text: str) -> Dict[str, str]:
    """
    Extrae secciones clave del análisis para mostrar de forma estructurada.
    
    Args:
        analysis_text: Texto completo del análisis
        
    Returns:
        Diccionario con las secciones extraídas
    """
    sections = {
        "sentimiento": "",
        "temas": "",
        "fortalezas": "",
        "mejoras": "",
        "marketing": "",
        "segmentacion": "",
        "recomendaciones": ""
    }
    
    try:
        # Patrones para cada sección
        patterns = {
            "sentimiento": r'(?:SENTIMIENTO\s+GENERAL|1\..*?SENTIMIENTO).*?(?:\n|:)(.*?)(?:\n\n|\n[2-7]\.)',
            "temas": r'(?:TEMAS\s+PRINCIPALES|2\..*?TEMAS).*?(?:\n|:)(.*?)(?:\n\n|\n[3-7]\.)',
            "fortalezas": r'(?:FORTALEZAS\s+DEL\s+PRODUCTO|3\..*?FORTALEZAS).*?(?:\n|:)(.*?)(?:\n\n|\n[4-7]\.)',
            "mejoras": r'(?:ÁREAS\s+DE\s+MEJORA|4\..*?MEJORA).*?(?:\n|:)(.*?)(?:\n\n|\n[5-7]\.)',
            "marketing": r'(?:OPORTUNIDADES\s+DE\s+MARKETING|5\..*?MARKETING).*?(?:\n|:)(.*?)(?:\n\n|\n[6-7]\.)',
            "segmentacion": r'(?:SEGMENTACIÓN|6\..*?SEGMENTACIÓN).*?(?:\n|:)(.*?)(?:\n\n|\n[7]\.)',
            "recomendaciones": r'(?:RECOMENDACIONES\s+ACCIONABLES|7\..*?RECOMENDACIONES).*?(?:\n|:)(.*?)(?:\n\n|\Z)'
        }
        
        # Extraer cada sección
        for key, pattern in patterns.items():
            match = re.search(pattern, analysis_text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[key] = match.group(1).strip()
        
        logger.info(f"Extraídas {sum(1 for v in sections.values() if v)} secciones del análisis")
        return sections
        
    except Exception as e:
        logger.error(f"Error al extraer secciones clave: {str(e)}")
        return sections

def extract_numbered_points(text: str, max_points: int = 5, prefix: str = "") -> List[str]:
    """
    Extrae puntos de un texto y los devuelve como una lista de strings.
    Mantiene cualquier numeración o formato existente.
    
    Args:
        text: Texto a procesar
        max_points: Número máximo de puntos a devolver
        prefix: Prefijo opcional para buscar (• - * etc.)
        
    Returns:
        Lista de puntos extraídos
    """
    if not text or not text.strip():
        return []
    
    points = []
    
    # Detectar si el texto tiene estructura de lista numerada
    numbered_pattern = rf'(?:^\s*{re.escape(prefix) if prefix else ""}(?:\d+[\.|\)]|\-|\•|\*)\s*)(.*?)(?:\n|$)'
    numbered_matches = re.findall(numbered_pattern, text, re.MULTILINE)
    
    if numbered_matches:
        # Extraer puntos manteniendo su numeración original
        pattern = rf'^\s*{re.escape(prefix) if prefix else ""}(?:(\d+)[\.|\)]|\-|\•|\*)\s*(.*?)(?:\n|$)'
        for match in re.finditer(pattern, text, re.MULTILINE):
            num = match.group(1) if match.group(1) else ""
            content = match.group(2).strip() if match.group(2) else match.group(0).strip()
            if num:
                points.append(f"{num}) {content}")
            else:
                points.append(content)
    else:
        # Si no hay formato de lista, dividir por frases o párrafos
        sentences = re.split(r'(?<=[.!?])\s+', text)
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Usar párrafos si parecen tener más estructura, de lo contrario usar frases
        candidates = paragraphs if len(paragraphs) <= len(sentences) * 0.7 else sentences
        points = [s.strip() for s in candidates if len(s.strip()) > 10]
    
    # Limitar a los puntos más importantes
    if len(points) > max_points:
        points = points[:max_points]
    
    return points


def format_key_points(section_text: str, max_points: int = 5) -> str:
    """
    Simplifica y formatea una sección de texto para mostrar solo los puntos clave.
    
    Args:
        section_text: Texto completo de la sección
        max_points: Número máximo de puntos a incluir
        
    Returns:
        Texto formateado con los puntos clave
    """
    # Si el texto está vacío, devolver cadena vacía
    if not section_text or not section_text.strip():
        return ""
        
    # Buscar patrones de listas numeradas o con viñetas
    bullet_points = re.findall(r'(?:^\s*(?:\d+\.|\-|\•)\s*)(.*?)(?:\n|$)', section_text, re.MULTILINE)
    
    # Si no hay formato de lista, buscar frases completas
    if not bullet_points:
        sentences = re.split(r'(?<=[.!?])\s+', section_text)
        bullet_points = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    # Si todavía no hay puntos, separar por líneas
    if not bullet_points:
        bullet_points = [line.strip() for line in section_text.split('\n') if len(line.strip()) > 10]
    
    # Limitar a los puntos más importantes
    if len(bullet_points) > max_points:
        bullet_points = bullet_points[:max_points]
    
    # Formatear como lista con viñetas
    formatted_text = ""
    for point in bullet_points:
        # Limpiar el punto
        clean_point = point.strip()
        # Remover prefijos de viñetas si existen
        clean_point = re.sub(r'^[•\-\*]\s*', '', clean_point)
        # Añadir al texto formateado
        if clean_point:
            formatted_text += f"• {clean_point}\n\n"
    
    return formatted_text