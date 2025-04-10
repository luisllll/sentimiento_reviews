"""
Reusable components for the user interface.
"""
import streamlit as st
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Callable
import time

from utils.visualization import create_sentiment_pie_chart, create_themes_bar_chart, format_full_report
from utils.metrics_extraction import format_key_points

# Configure logger
logger = logging.getLogger(__name__)

def upload_area(help_text: str = "The file must contain a 'Body' column with the comments") -> None:
    """
    Displays the drag-and-drop area for file uploads.
    
    Args:
        help_text: Help text to display
    """
    st.markdown("""
    <div class="upload-area">
        <h3>📁 Drag and drop your CSV file here</h3>
        <p>{}</p>
    </div>
    """.format(help_text), unsafe_allow_html=True)

def display_example_dataframe() -> None:
    """Displays an example DataFrame to illustrate the expected format."""
    st.markdown("### 🔍 Example of the expected CSV format:")
    
    example_df = pd.DataFrame({
        'ID': [1, 2, 3],
        'Body': [
            "I love this product, it works perfectly and the quality is excellent.",
            "The shipping was fast, but the product didn't meet my quality expectations.",
            "Price is high for the quality it offers, but it meets the basics."
        ],
        'Date': ['2023-01-15', '2023-01-20', '2023-01-25']
    })
    
    st.dataframe(example_df, hide_index=True)

def display_instructions() -> None:
    """Displays instructions on how to use the application."""
    st.markdown("""
    ### 🚀 How it works:
    1. Upload your CSV file with comments
    2. Set the analysis parameters in the sidebar
    3. Click on "Analyze Comments"
    4. Receive a detailed and actionable analysis
    
    ### 🧠 Technology:
    This tool uses advanced reasoning models to:
    - Analyze large volumes of comments
    - Detect patterns and trends
    - Extract actionable insights
    - Generate strategic recommendations
    """)

def progress_tracker(total_steps: int) -> tuple:
    """
    Creates a progress tracking system with a progress bar and text.
    
    Args:
        total_steps: Total number of steps
        
    Returns:
        Tuple with (progress_bar, progress_text, update_function)
    """
    st.markdown("### ⏳ Analysis Progress")
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    def update_progress(step: int, message: str) -> None:
        """Updates the progress bar and message."""
        progress = min(step / total_steps, 1.0)
        progress_bar.progress(progress)
        progress_text.text(message)
        # Small pause to visualize the update better
        time.sleep(0.1)
    
    return progress_bar, progress_text, update_progress

def metrics_display(
    total_comments: int, 
    tokens_reasoning: int, 
    total_tokens: int
) -> None:
    """
    Displays general metrics in three columns.
    
    Args:
        total_comments: Total number of comments analyzed
        tokens_reasoning: Number of reasoning tokens used
        total_tokens: Total number of tokens used
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Comments", f"{total_comments:,}")
    
    with col2:
        st.metric("Reasoning Tokens", f"{tokens_reasoning:,}")
    
    with col3:
        st.metric("Total Tokens", f"{total_tokens:,}")

def results_tabs(analysis_text: str, metrics: Dict[str, Any], formatted_sections: Dict[str, str], filepath: str) -> None:
    """
    Displays results in organized tabs (improved version).
    
    Args:
        analysis_text: Full analysis text
        metrics: Extracted metrics for visualization
        formatted_sections: Formatted sections of the analysis
        filepath: Path to the saved file for download
    """
    # Create simplified tabs
    tab1, tab2 = st.tabs(["📊 Visual Summary", "📄 Full Report"])
    
    with tab1:

        """
        # Sentiment chart
        st.plotly_chart(
            create_sentiment_pie_chart(metrics["sentiment_distribution"]), 
            use_container_width=True
        )
        """
        
        # Display only the most important sections
        st.markdown("### 🔍 Key Findings")
        
        # Show strengths and areas for improvement in columns
        col1, col2 = st.columns(2)
        
        with col1:
            if "strengths" in formatted_sections:
                st.markdown("#### ✅ Strengths")
                strengths_text = formatted_sections.get("strengths", "").replace("### ✅ PRODUCT STRENGTHS\n\n", "")
                
                # Format points as more readable bullet points
                points = format_key_points(strengths_text, max_points=3)
                if points:
                    for point in points.split("• "):
                        if point.strip():
                            st.markdown(f"• {point.strip()}")
        
        with col2:
            # Ensure the areas for improvement section is always shown
            st.markdown("#### ⚠️ Areas for Improvement")
            
            # Get text for areas for improvement or provide a default message
            improvements_text = formatted_sections.get("improvements", "").replace("### ⚠️ AREAS FOR IMPROVEMENT\n\n", "")
            if not improvements_text.strip():
                improvements_text = "No specific areas for improvement identified in the analyzed comments."
            
            # Format points as more readable bullet points
            points = format_key_points(improvements_text, max_points=3)
            if points:
                for point in points.split("• "):
                    if point.strip():
                        st.markdown(f"• {point.strip()}")
            else:
                st.markdown("No specific areas for improvement identified.")
        
        # Add recommendations in a separate section
        st.markdown("### 🚀 Key Recommendations")
        
        # Get text for recommendations or provide a default message
        recommendations_text = formatted_sections.get("recommendations", "").replace("### 🚀 ACTIONABLE RECOMMENDATIONS\n\n", "")
        if not recommendations_text.strip():
            recommendations_text = "Not enough data to generate specific recommendations."
        
        # Format points as numbered bullet points for better readability
        points = format_key_points(recommendations_text, max_points=5)
        if points:
            for i, point in enumerate(points.split("• ")[1:], 1):  # Start from 1, ignoring the first empty element
                if point.strip():
                    st.markdown(f"**{i}.** {point.strip()}")
    
    with tab2:
        st.markdown("## 📋 Full Report")
        
        # Apply improved formatting for Streamlit
        formatted_report = format_full_report(analysis_text)
        
        # Display the formatted report
        st.markdown(formatted_report)
        
        # Download button
        with open(filepath, "r", encoding="utf-8") as f:
            st.download_button(
                label="📥 Download Full Report",
                data=f,
                file_name="sentiment_analysis.txt",
                mime="text/plain"
            )

def error_message(error: Exception, show_details: bool = True) -> None:
    """
    Displays an error message with an option to view details.
    
    Args:
        error: Occurred exception
        show_details: Whether to show the button to view details
    """
    st.error(f"Error: {str(error)}")
    
    if show_details:
        if st.button("Show error details"):
            st.exception(error)
