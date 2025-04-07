"""
Sidebar components for the user interface.
"""
import os
import streamlit as st
import logging
from typing import Dict, Any, Tuple
from config.settings import (
    DEFAULT_CHUNK_SIZE, MIN_CHUNK_SIZE, MAX_CHUNK_SIZE, 
    DEFAULT_SYSTEM_PROMPT, DEFAULT_MODEL, DEFAULT_REASONING_EFFORT
)

# Configure logger
logger = logging.getLogger(__name__)

def render_sidebar() -> Dict[str, Any]:
    """
    Renders the sidebar with configuration options.
    
    Returns:
        Dictionary with the selected configuration
    """
    st.sidebar.header("⚙️ Configuration")
    
    # API Key status
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.sidebar.success("✅ API Key loaded from .env file")
    else:
        st.sidebar.warning("⚠️ API Key not found in .env file")
        api_key = st.sidebar.text_input("OpenAI API Key (alternative)", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            logger.info("API Key configured manually")
    
    # Processing parameters
    chunk_size = st.sidebar.slider(
        "Size of each comment chunk", 
        min_value=MIN_CHUNK_SIZE, 
        max_value=MAX_CHUNK_SIZE, 
        value=DEFAULT_CHUNK_SIZE,
        help="Number of comments to process in each group"
    )
    
    max_comments = st.sidebar.number_input(
        "Maximum comments to analyze (0 = all)", 
        min_value=0, 
        value=0,
        help="Limits the total number of comments to analyze (0 to analyze all)"
    )
    
    # Custom instruction system
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📝 Customize Instructions")
    
    system_prompt = st.sidebar.text_area(
        "Instructions for the model",
        value=DEFAULT_SYSTEM_PROMPT,
        height=300
    )
    
    # Application information
    st.sidebar.markdown("---")
    expander = st.sidebar.expander("ℹ️ About", expanded=False)
    with expander:
        st.markdown(""" 
        **Comment Sentiment Analysis**
        
        Version: 1.0.0
        
        This application uses advanced reasoning models to analyze customer comments 
        and extract actionable insights.
        """)
    
    # Gather all options in a dictionary using default values for advanced options
    config = {
        "api_key_status": bool(api_key),
        "chunk_size": chunk_size,
        "max_comments": max_comments,
        "model": DEFAULT_MODEL,
        "reasoning_effort": DEFAULT_REASONING_EFFORT,
        "column_name": "Cuerpo",  # Fixed value
        "system_prompt": system_prompt,
        "output_format": "TXT"  # Fixed value
    }
    
    logger.info(f"Configuration loaded: {', '.join(f'{k}={v}' for k, v in config.items() if k != 'system_prompt' and k != 'api_key_status')}")
    return config
