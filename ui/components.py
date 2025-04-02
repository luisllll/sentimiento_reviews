"""
Componentes reutilizables para la interfaz de usuario.
"""
import streamlit as st
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Callable
import time

from utils.visualization import create_sentiment_pie_chart, create_themes_bar_chart,format_full_report
from utils.metrics_extraction import format_key_points

# Configurar logger
logger = logging.getLogger(__name__)

def upload_area(help_text: str = "El archivo debe contener una columna 'Cuerpo' con los comentarios") -> None:
    """
    Muestra el área de arrastrar y soltar para subir archivos.
    
    Args:
        help_text: Texto de ayuda para mostrar
    """
    st.markdown("""
    <div class="upload-area">
        <h3>📁 Arrastra y suelta tu archivo CSV aquí</h3>
        <p>{}</p>
    </div>
    """.format(help_text), unsafe_allow_html=True)

def display_example_dataframe() -> None:
    """Muestra un DataFrame de ejemplo para ilustrar el formato esperado."""
    st.markdown("### 🔍 Ejemplo de formato esperado del CSV:")
    
    example_df = pd.DataFrame({
        'ID': [1, 2, 3],
        'Cuerpo': [
            "Me encanta este producto, funciona perfectamente y la calidad es excelente.",
            "El envío fue rápido pero el producto no cumplió mis expectativas de calidad.",
            "Precio elevado para la calidad que ofrece, pero cumple con lo básico."
        ],
        'Fecha': ['2023-01-15', '2023-01-20', '2023-01-25']
    })
    
    st.dataframe(example_df, hide_index=True)

def display_instructions() -> None:
    """Muestra instrucciones sobre cómo usar la aplicación."""
    st.markdown("""
    ### 🚀 Cómo funciona:
    1. Sube tu archivo CSV con comentarios
    2. Configura los parámetros de análisis en el panel lateral
    3. Haz clic en "Analizar comentarios"
    4. Recibe un análisis detallado y accionable
    
    ### 🧠 Tecnología:
    Esta herramienta utiliza modelos de razonamiento avanzado para:
    - Analizar grandes volúmenes de comentarios
    - Detectar patrones y tendencias
    - Extraer insights accionables
    - Generar recomendaciones estratégicas
    """)

def progress_tracker(total_steps: int) -> tuple:
    """
    Crea un sistema de seguimiento de progreso con barra y texto.
    
    Args:
        total_steps: Número total de pasos
        
    Returns:
        Tupla con (barra_progreso, texto_progreso, función_actualizar)
    """
    st.markdown("### ⏳ Progreso del análisis")
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    def update_progress(step: int, message: str) -> None:
        """Actualiza la barra de progreso y el mensaje."""
        progress = min(step / total_steps, 1.0)
        progress_bar.progress(progress)
        progress_text.text(message)
        # Pequeña pausa para visualizar mejor la actualización
        time.sleep(0.1)
    
    return progress_bar, progress_text, update_progress

def metrics_display(
    total_comments: int, 
    tokens_reasoning: int, 
    total_tokens: int
) -> None:
    """
    Muestra métricas generales en tres columnas.
    
    Args:
        total_comments: Número total de comentarios analizados
        tokens_reasoning: Número de tokens de razonamiento utilizados
        total_tokens: Número total de tokens utilizados
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de comentarios", f"{total_comments:,}")
    
    with col2:
        st.metric("Tokens de razonamiento", f"{tokens_reasoning:,}")
    
    with col3:
        st.metric("Total de tokens", f"{total_tokens:,}")

def results_tabs(analysis_text: str, metrics: Dict[str, Any], formatted_sections: Dict[str, str], filepath: str) -> None:
    """
    Muestra los resultados en pestañas organizadas (versión mejorada).
    
    Args:
        analysis_text: Texto completo del análisis
        metrics: Métricas extraídas para visualización
        formatted_sections: Secciones del análisis formateadas
        filepath: Ruta al archivo guardado para descarga
    """
    # Crear pestañas simplificadas
    tab1, tab2 = st.tabs(["📊 Resumen Visual", "📄 Informe Completo"])
    
    with tab1:
        # Gráfico de sentimiento
        st.plotly_chart(
            create_sentiment_pie_chart(metrics["sentiment_distribution"]), 
            use_container_width=True
        )
        
        # Mostrar solo las secciones más importantes
        st.markdown("### 🔍 Principales Hallazgos")
        
        # Mostrar fortalezas y áreas de mejora en columnas
        col1, col2 = st.columns(2)
        
        with col1:
            if "fortalezas" in formatted_sections:
                st.markdown("#### ✅ Fortalezas")
                fortalezas_text = formatted_sections.get("fortalezas", "").replace("### ✅ FORTALEZAS DEL PRODUCTO\n\n", "")
                
                # Formatear puntos como viñetas más legibles
                points = format_key_points(fortalezas_text, max_points=3)
                if points:
                    for point in points.split("• "):
                        if point.strip():
                            st.markdown(f"• {point.strip()}")
        
        with col2:
            # Asegurar que siempre se muestre la sección de áreas de mejora
            st.markdown("#### ⚠️ Áreas de Mejora")
            
            # Obtener texto de áreas de mejora o proporcionar un mensaje predeterminado
            mejoras_text = formatted_sections.get("mejoras", "").replace("### ⚠️ ÁREAS DE MEJORA\n\n", "")
            if not mejoras_text.strip():
                mejoras_text = "No se identificaron áreas específicas de mejora en los comentarios analizados."
            
            # Formatear puntos como viñetas más legibles
            points = format_key_points(mejoras_text, max_points=3)
            if points:
                for point in points.split("• "):
                    if point.strip():
                        st.markdown(f"• {point.strip()}")
            else:
                st.markdown("No se identificaron áreas específicas de mejora.")
        
        # Añadir recomendaciones en una sección aparte
        st.markdown("### 🚀 Recomendaciones Clave")
        
        # Obtener texto de recomendaciones o proporcionar un mensaje predeterminado
        recom_text = formatted_sections.get("recomendaciones", "").replace("### 🚀 RECOMENDACIONES ACCIONABLES\n\n", "")
        if not recom_text.strip():
            recom_text = "No hay suficientes datos para generar recomendaciones específicas."
        
        # Formatear puntos como viñetas numeradas más legibles
        points = format_key_points(recom_text, max_points=5)
        if points:
            for i, point in enumerate(points.split("• ")[1:], 1):  # Empezar desde 1, ignorar el primer elemento vacío
                if point.strip():
                    st.markdown(f"**{i}.** {point.strip()}")
    
    with tab2:
        st.markdown("## 📋 Informe Completo")
        
        # Aplicar formato mejorado para Streamlit
        formatted_report = format_full_report(analysis_text)
        
        # Mostrar el informe formateado
        st.markdown(formatted_report)
        
        # Botón de descarga
        with open(filepath, "r", encoding="utf-8") as f:
            st.download_button(
                label="📥 Descargar informe completo",
                data=f,
                file_name="analisis_sentimiento.txt",
                mime="text/plain"
            )

def error_message(error: Exception, show_details: bool = True) -> None:
    """
    Muestra un mensaje de error con opción para ver detalles.
    
    Args:
        error: Excepción ocurrida
        show_details: Si se debe mostrar el botón para ver detalles
    """
    st.error(f"Error: {str(error)}")
    
    if show_details:
        if st.button("Mostrar detalles del error"):
            st.exception(error)