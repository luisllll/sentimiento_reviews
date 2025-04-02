"""
Páginas principales de la aplicación.
"""
import streamlit as st
import pandas as pd
import logging
from typing import Dict, List, Any, Optional

from ui.sidebar import render_sidebar
from ui.components import (
    upload_area, 
    display_example_dataframe, 
    display_instructions,
    progress_tracker,
    metrics_display,
    results_tabs,
    error_message
)
from utils.data_processing import (
    validate_and_prepare_dataframe,
    split_dataframe_into_chunks,
    calculate_total_tokens
)
from utils.metrics_extraction import extract_metrics_from_analysis, extract_key_sections
from utils.visualization import format_analysis_sections
from services.openai_service import openai_service
from services.file_service import file_service

# Configurar logger
logger = logging.getLogger(__name__)

def render_main_page() -> None:
    """Renderiza la página principal de la aplicación."""
    # Título y descripción
    st.title("📊 Análisis de Sentimiento de Comentarios")
    st.markdown("### Analiza comentarios de clientes usando modelos de razonamiento avanzado")
    
    # Cargar configuración desde la barra lateral
    config = render_sidebar()
    
    # Área para subir archivo
    uploaded_file = st.file_uploader(
        "Arrastra y suelta tu archivo CSV con comentarios", 
        type=["csv"], 
        help="El archivo debe contener una columna 'Cuerpo' con los comentarios"
    )
    
    if not uploaded_file:
        # Mostrar área de subida y ejemplo
        upload_area(help_text="El archivo debe contener una columna llamada 'Cuerpo' con los comentarios de los clientes")
        display_example_dataframe()
        display_instructions()
        return
    
    # Procesar archivo subido
    try:
        # Cargar DataFrame
        df = pd.read_csv(uploaded_file)
        
        # Validar y preparar datos
        success, message, df_cleaned = validate_and_prepare_dataframe(df, comment_column="Cuerpo")
        
        if not success:
            st.error(message)
            return
        
        # Mostrar vista previa
        total_comments = len(df_cleaned)
        st.markdown(f"### 📋 Vista previa ({total_comments} comentarios)")
        st.dataframe(df_cleaned.head(5), hide_index=True)
        
        # Botón para iniciar análisis
        if st.button("🔍 Analizar comentarios", type="primary"):
            if not config['api_key_status']:
                st.error("Por favor, configura tu API Key de OpenAI en el archivo .env o ingrésala en el panel lateral")
                return
            
            # Iniciar análisis
            with st.spinner("Preparando análisis..."):
                # Dividir en chunks
                chunks, total_comments = split_dataframe_into_chunks(
                    df_cleaned, 
                    comment_column="Cuerpo",
                    chunk_size=config['chunk_size'],
                    max_comments=config['max_comments']
                )
            
            # Crear sistema de seguimiento de progreso
            total_steps = len(chunks) + 1  # +1 para el análisis final
            progress_bar, progress_text, update_progress = progress_tracker(total_steps)
            
            # Procesar chunks
            chunk_analyses = []
            
            for i, chunk in enumerate(chunks):
                update_progress(i, f"Analizando grupo {i+1} de {len(chunks)} ({len(chunk)} comentarios)...")
                
                # Análisis del chunk
                chunk_result = openai_service.analyze_comments_chunk(
                    chunk,
                    system_prompt=config['system_prompt'],
                    model=config['model'],
                    reasoning_effort=config['reasoning_effort']
                )
                
                # Verificar si hubo errores
                if chunk_result.get("error", False):
                    st.error(f"Error al analizar grupo {i+1}: {chunk_result.get('analysis', 'Error desconocido')}")
                    continue
                
                chunk_analyses.append(chunk_result)
                
                # Actualizar barra de progreso
                update_progress(i + 1, f"Grupo {i+1} de {len(chunks)} completado")
            
            # Análisis final
            update_progress(len(chunks), "Generando análisis final...")
            
            with st.spinner("Generando análisis final..."):
                final_analysis = openai_service.generate_final_analysis(
                    chunk_analyses,
                    total_comments=total_comments,
                    chunks_count=len(chunks),
                    system_prompt=config['system_prompt'],
                    model=config['model'],
                    reasoning_effort=config['reasoning_effort']
                )
            
            # Actualizar progreso final
            update_progress(total_steps, "Análisis completado")
            
            # Verificar si el análisis final tuvo errores
            if final_analysis.get("error", False):
                st.error(f"Error en el análisis final: {final_analysis.get('analysis', 'Error desconocido')}")
                return
            
            # Mostrar mensaje de éxito
            st.success(f"✅ Análisis completado: {total_comments} comentarios procesados en {len(chunks)} grupos")
            
            # Calcular totales de tokens
            token_counts = calculate_total_tokens(chunk_analyses + [final_analysis])
            
            # Mostrar métricas generales
            metrics_display(
                total_comments=total_comments,
                tokens_reasoning=token_counts["tokens_reasoning"],
                total_tokens=token_counts["total_tokens"]
            )
            
            # Separador
            st.markdown("---")
            
            # Procesar y guardar resultados
            try:
                # Extraer métricas para visualización
                metrics = extract_metrics_from_analysis(final_analysis["analysis"])
                
                # Extraer secciones clave
                sections = extract_key_sections(final_analysis["analysis"])
                
                # Formatear secciones para mejor presentación
                formatted_sections = format_analysis_sections(sections)
                
                # Guardar análisis en archivo
                filename = file_service.save_analysis_to_file(final_analysis["analysis"])
                
                # Mostrar resultados en pestañas
                results_tabs(
                    analysis_text=final_analysis["analysis"],
                    metrics=metrics,
                    formatted_sections=formatted_sections,
                    filepath=filename
                )
                
                # Guardar resultados en estado de sesión para referencia futura
                st.session_state.analysis_results = {
                    "analysis_text": final_analysis["analysis"],
                    "metrics": metrics,
                    "token_counts": token_counts,
                    "total_comments": total_comments,
                    "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
            except Exception as processing_error:
                logger.error(f"Error al procesar resultados: {str(processing_error)}")
                st.error("Se completó el análisis, pero hubo un error al procesar los resultados para visualización")
                st.text_area("Análisis en texto plano:", final_analysis["analysis"], height=400)
    
    except Exception as e:
        logger.error(f"Error al procesar archivo: {str(e)}", exc_info=True)
        error_message(e)

def render_help_page() -> None:
    """Renderiza la página de ayuda."""
    st.title("📚 Ayuda y Documentación")
    
    st.markdown("""
    ## 🔍 Análisis de Sentimiento de Comentarios
    
    Esta aplicación te permite analizar comentarios de clientes para extraer insights valiosos
    que pueden ayudarte a mejorar tus productos y estrategias de marketing.
    
    ### 📊 Características principales
    
    - **Análisis de sentimiento**: Identifica la distribución de comentarios positivos, negativos y neutrales
    - **Extracción de temas**: Descubre los temas más mencionados por tus clientes
    - **Identificación de fortalezas**: Conoce qué aspectos de tu producto son valorados positivamente
    - **Detección de áreas de mejora**: Identifica oportunidades para mejorar tus productos
    - **Ideas de marketing**: Recibe sugerencias para campañas basadas en los comentarios
    - **Segmentación de clientes**: Identifica diferentes segmentos según sus preferencias
    - **Recomendaciones accionables**: Obtén acciones concretas para mejorar la satisfacción del cliente
    
    ### 📋 Requisitos del archivo CSV
    
    El archivo CSV debe contener al menos una columna llamada 'Cuerpo' (o el nombre que especifiques 
    en la configuración) que contenga los comentarios a analizar.
    
    ### ⚙️ Opciones de configuración
    
    - **Tamaño de chunk**: Define cuántos comentarios se procesan juntos (10-200)
    - **Máximo de comentarios**: Limita el número total de comentarios a analizar
    - **Modelo**: Selecciona el modelo de OpenAI a utilizar
    - **Esfuerzo de razonamiento**: Ajusta la profundidad del análisis
    - **Instrucciones personalizadas**: Modifica las instrucciones enviadas al modelo
    
    ### 🔐 Configuración de API Key
    
    Para usar esta aplicación, necesitas configurar tu API Key de OpenAI:
    
    1. Crea un archivo `.env` en el directorio principal
    2. Añade tu API Key: `OPENAI_API_KEY=tu_api_key_aquí`
    
    Alternativamente, puedes ingresar tu API Key en el panel lateral.
    """)
    
    st.markdown("---")
    
    with st.expander("❓ Preguntas frecuentes", expanded=False):
        st.markdown("""
        **P: ¿Cuántos comentarios puedo analizar a la vez?**
        
        R: No hay un límite estricto, pero para obtener mejores resultados y controlar 
        los costos, recomendamos analizar entre 100 y 1000 comentarios a la vez.
        
        **P: ¿Cómo afecta el tamaño de chunk al análisis?**
        
        R: Un tamaño de chunk mayor reduce el número de llamadas a la API pero puede
        hacer que el análisis sea menos detallado. Un tamaño menor permite un análisis
        más granular pero aumenta el número de llamadas y el costo total.
        
        **P: ¿Cómo puedo personalizar el análisis?**
        
        R: Puedes modificar las instrucciones en el panel lateral para enfocar el análisis
        en aspectos específicos o ajustar el tipo de insights que deseas obtener.
        
        **P: ¿Qué formatos de archivo son compatibles?**
        
        R: Actualmente solo se admiten archivos CSV. Asegúrate de que tu archivo tenga 
        una columna con los comentarios.
        """)

# Puedes añadir más funciones para renderizar páginas adicionales según sea necesario