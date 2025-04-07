"""
Utilities for data and results visualization.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
import re
from typing import Dict, List, Any, Optional
from config.settings import SENTIMENT_COLORS

# Configure logger
logger = logging.getLogger(__name__)

def format_full_report(report_text: str) -> str:
    """
    Improves the formatting of the full report for better visualization in Streamlit.
    
    Args:
        report_text: The full report text
        
    Returns:
        Text with improved formatting for Streamlit
    """
    try:
        # Split the report into sections based on separators
        sections = re.split(r'─+\s*', report_text)
        
        # Remove empty sections
        sections = [s.strip() for s in sections if s.strip()]
        
        # Process each section
        formatted_report = ""
        
        for section in sections:
            # Detect if it's a numbered section
            match = re.match(r'(\d+\.\s*)?([A-ZÁ-ÚÑ\s]+)(?:\s*─+|\s*$)', section)
            if match:
                # Extract the section title
                section_title = match.group(2).strip()
                # Extract the content (everything after the title)
                content = section[match.end():].strip()
                
                # Add the formatted title
                formatted_report += f"### {section_title}\n\n"
                
                # Process the content
                # Format lists with bullet points
                content = re.sub(r'•\s*([^•\n]+)', r'* \1', content)
                content = re.sub(r'–\s*([^–\n]+)', r'  * \1', content)
                
                # Format percentages in bold
                content = re.sub(r'(\d+)%', r'**\1%**', content)
                
                # Format subsections in bold
                content = re.sub(r'([A-Za-z\sáéíóúÁÉÍÓÚñÑ"]+):(\s)', r'**\1:**\2', content)
                
                # Add the processed content
                formatted_report += content + "\n\n"
            else:
                # If it's not a standard section, add it as is
                formatted_report += section + "\n\n"
        
        return formatted_report
    
    except Exception as e:
        logger.error(f"Error formatting full report: {str(e)}")
        return report_text
    

def create_sentiment_pie_chart(sentiment_data: Dict[str, float], title: str = 'Sentiment Distribution') -> go.Figure:
    """
    Creates a pie chart for sentiment distribution.
    
    Args:
        sentiment_data: Dictionary with percentages for each sentiment
        title: Title of the chart
        
    Returns:
        Plotly figure with the chart
    """
    logger.info("Creating sentiment distribution chart")
    
    try:
        # Convert data to DataFrame
        df = pd.DataFrame({
            'Sentiment': list(sentiment_data.keys()),
            'Percentage': list(sentiment_data.values())
        })
        
        # Create simplified pie chart
        fig = px.pie(
            df, 
            values='Percentage', 
            names='Sentiment',
            color='Sentiment',
            color_discrete_map=SENTIMENT_COLORS,
            title=title
        )
        
        # Customize chart to make it simpler
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont=dict(size=16)
        )
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            title=dict(font=dict(size=24), x=0.5),
            height=400  # Fixed height for better visualization
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error creating sentiment chart: {str(e)}")
        # Create an error chart
        fig = go.Figure()
        fig.add_annotation(text="Error creating visualization", showarrow=False, font=dict(size=20, color="red"))
        return fig

def create_themes_bar_chart(themes_data: List[Dict[str, Any]], title: str = 'Main Themes Mentioned') -> Optional[go.Figure]:
    """
    Creates a bar chart for the main themes.
    
    Args:
        themes_data: List of dictionaries with the themes and their percentages
        title: Title of the chart
        
    Returns:
        Plotly figure with the chart or None if there is insufficient data
    """
    logger.info(f"Creating main themes chart with {len(themes_data)} themes")
    
    # Check if there is enough data
    if not themes_data or len(themes_data) < 2:
        logger.warning("Insufficient data to create themes chart")
        return None
    
    try:
        # Create DataFrame
        df = pd.DataFrame(themes_data)
        
        # Sort by percentage
        df = df.sort_values('percentage', ascending=False)
        
        # Limit to the top 10 themes
        if len(df) > 10:
            df = df.head(10)
        
        # Create horizontal bar chart
        fig = px.bar(
            df,
            y='name',
            x='percentage',
            orientation='h',
            title=title,
            labels={'name': 'Theme', 'percentage': 'Percentage (%)'},
            color='percentage',
            color_continuous_scale=px.colors.sequential.Blues
        )
        
        # Customize chart
        fig.update_layout(
            yaxis=dict(categoryorder='total ascending'),
            title=dict(font=dict(size=20)),
            xaxis_title='Percentage (%)',
            yaxis_title='Theme'
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error creating themes chart: {str(e)}")
        return None

def format_analysis_sections(sections: Dict[str, str]) -> Dict[str, str]:
    """
    Formats the analysis sections to improve presentation.
    
    Args:
        sections: Dictionary with extracted sections
        
    Returns:
        Dictionary with formatted sections
    """
    formatted = {}
    
    # Mapping of section names for presentation
    section_titles = {
        "sentiment": "🔍 GENERAL SENTIMENT",
        "themes": "📊 MAIN TOPICS",
        "strengths": "✅ PRODUCT STRENGTHS",
        "improvements": "⚠️ AREAS FOR IMPROVEMENT",
        "marketing": "📣 MARKETING OPPORTUNITIES",
        "segmentation": "👥 CUSTOMER SEGMENTATION",
        "recommendations": "🚀 ACTIONABLE RECOMMENDATIONS"
    }
    
    # Format each section
    for key, content in sections.items():
        if content:
            # Convert possible lists to more visual format
            formatted_content = content
            
            # Find numbered list patterns and add format
            formatted_content = re.sub(r'(\d+\.\s*)', r'**\1**', formatted_content)
            
            # Find hyphen list patterns and convert to more visual format
            formatted_content = re.sub(r'^\s*-\s*', r'• ', formatted_content, flags=re.MULTILINE)
            
            formatted[key] = f"### {section_titles.get(key, key)}\n\n{formatted_content}\n\n"
    
    return formatted
