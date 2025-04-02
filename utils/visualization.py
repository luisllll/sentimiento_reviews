"""
Utilidades para visualización de datos y resultados.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
import re
from typing import Dict, List, Any, Optional
from config.settings import SENTIMENT_COLORS

# Configurar logger
logger = logging.getLogger(__name__)



def format_full_report(report_text: str) -> str:
    """
    Mejora el formato del informe completo para mejor visualización en Streamlit.
    
    Args:
        report_text: Texto completo del informe
        
    Returns:
        Texto con formato mejorado para Streamlit
    """
    try:
        # Dividir el informe en secciones basadas en los separadores
        sections = re.split(r'─+\s*', report_text)
        
        # Remover secciones vacías
        sections = [s.strip() for s in sections if s.strip()]
        
        # Procesar cada sección
        formatted_report = ""
        
        for section in sections:
            # Detectar si es una sección numerada
            match = re.match(r'(\d+\.\s*)?([A-ZÁ-ÚÑ\s]+)(?:\s*─+|\s*$)', section)
            if match:
                # Extraer el título de la sección
                section_title = match.group(2).strip()
                # Extraer el contenido (todo lo que viene después del título)
                content = section[match.end():].strip()
                
                # Añadir el título formateado
                formatted_report += f"### {section_title}\n\n"
                
                # Procesar el contenido
                # Formatear listas con viñetas
                content = re.sub(r'•\s*([^•\n]+)', r'* \1', content)
                content = re.sub(r'–\s*([^–\n]+)', r'  * \1', content)
                
                # Formatear porcentajes en negrita
                content = re.sub(r'(\d+)%', r'**\1%**', content)
                
                # Formatear subsecciones en negrita
                content = re.sub(r'([A-Za-z\sáéíóúÁÉÍÓÚñÑ"]+):(\s)', r'**\1:**\2', content)
                
                # Añadir el contenido procesado
                formatted_report += content + "\n\n"
            else:
                # Si no es una sección estándar, añadirla tal cual
                formatted_report += section + "\n\n"
        
        return formatted_report
    
    except Exception as e:
        logger.error(f"Error al formatear informe completo: {str(e)}")
        return report_text
    

def create_sentiment_pie_chart(sentiment_data: Dict[str, float], title: str = 'Distribución de Sentimientos') -> go.Figure:
    """
    Crea un gráfico de pastel para la distribución de sentimientos.
    
    Args:
        sentiment_data: Diccionario con los porcentajes de cada sentimiento
        title: Título del gráfico
        
    Returns:
        Figura de Plotly con el gráfico
    """
    logger.info("Creando gráfico de distribución de sentimientos")
    
    try:
        # Convertir datos a DataFrame
        df = pd.DataFrame({
            'Sentimiento': list(sentiment_data.keys()),
            'Porcentaje': list(sentiment_data.values())
        })
        
        # Crear gráfico de pastel simplificado
        fig = px.pie(
            df, 
            values='Porcentaje', 
            names='Sentimiento',
            color='Sentimiento',
            color_discrete_map=SENTIMENT_COLORS,
            title=title
        )
        
        # Personalizar gráfico para hacerlo más sencillo
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont=dict(size=16)
        )
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            title=dict(font=dict(size=24), x=0.5),
            height=400  # Altura fija para mejor visualización
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error al crear gráfico de sentimientos: {str(e)}")
        # Crear un gráfico de error
        fig = go.Figure()
        fig.add_annotation(text="Error al crear visualización", showarrow=False, font=dict(size=20, color="red"))
        return fig

def create_themes_bar_chart(themes_data: List[Dict[str, Any]], title: str = 'Temas Principales Mencionados') -> Optional[go.Figure]:
    """
    Crea un gráfico de barras para los temas principales.
    
    Args:
        themes_data: Lista de diccionarios con los temas y sus porcentajes
        title: Título del gráfico
        
    Returns:
        Figura de Plotly con el gráfico o None si no hay datos suficientes
    """
    logger.info(f"Creando gráfico de temas principales con {len(themes_data)} temas")
    
    # Verificar si hay suficientes datos
    if not themes_data or len(themes_data) < 2:
        logger.warning("Datos insuficientes para crear gráfico de temas")
        return None
    
    try:
        # Crear DataFrame
        df = pd.DataFrame(themes_data)
        
        # Ordenar por porcentaje
        df = df.sort_values('percentage', ascending=False)
        
        # Limitar a los 10 temas principales
        if len(df) > 10:
            df = df.head(10)
        
        # Crear gráfico de barras horizontales
        fig = px.bar(
            df,
            y='name',
            x='percentage',
            orientation='h',
            title=title,
            labels={'name': 'Tema', 'percentage': 'Porcentaje (%)'},
            color='percentage',
            color_continuous_scale=px.colors.sequential.Blues
        )
        
        # Personalizar gráfico
        fig.update_layout(
            yaxis=dict(categoryorder='total ascending'),
            title=dict(font=dict(size=20)),
            xaxis_title='Porcentaje (%)',
            yaxis_title='Tema'
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error al crear gráfico de temas: {str(e)}")
        return None

def format_analysis_sections(sections: Dict[str, str]) -> Dict[str, str]:
    """
    Formatea las secciones del análisis para mejorar la presentación.
    
    Args:
        sections: Diccionario con las secciones extraídas
        
    Returns:
        Diccionario con las secciones formateadas
    """
    formatted = {}
    
    # Mapeo de nombres de sección para presentación
    section_titles = {
        "sentimiento": "🔍 SENTIMIENTO GENERAL",
        "temas": "📊 TEMAS PRINCIPALES",
        "fortalezas": "✅ FORTALEZAS DEL PRODUCTO",
        "mejoras": "⚠️ ÁREAS DE MEJORA",
        "marketing": "📣 OPORTUNIDADES DE MARKETING",
        "segmentacion": "👥 SEGMENTACIÓN DE CLIENTES",
        "recomendaciones": "🚀 RECOMENDACIONES ACCIONABLES"
    }
    
    # Formatear cada sección
    for key, content in sections.items():
        if content:
            # Convertir posibles listas a formato más visual
            formatted_content = content
            
            # Buscar patrones de listas numéricas y añadir formato
            formatted_content = re.sub(r'(\d+\.\s*)', r'**\1**', formatted_content)
            
            # Buscar patrones de lista con guiones y convertir a formato más visual
            formatted_content = re.sub(r'^\s*-\s*', r'• ', formatted_content, flags=re.MULTILINE)
            
            formatted[key] = f"### {section_titles.get(key, key)}\n\n{formatted_content}\n\n"
    
    return formatted