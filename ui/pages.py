"""
Main pages of the application.
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

# Configure logger
logger = logging.getLogger(__name__)

def render_main_page() -> None:
    """Renders the main page of the application."""
    # Title and description
    st.title("📊 Comment Sentiment Analysis")
    st.markdown("### Analyze customer comments using advanced reasoning models")
    
    # Load configuration from the sidebar
    config = render_sidebar()
    
    # File upload area
    uploaded_file = st.file_uploader(
        "Drag and drop your CSV file with comments", 
        type=["csv"], 
        help="The file must contain a column 'Body' with the comments"
    )
    
    if not uploaded_file:
        # Show upload area and example
        upload_area(help_text="The file must contain a column named 'Body' with customer comments")
        display_example_dataframe()
        display_instructions()
        return
    
    # Process uploaded file
    try:
        # Load DataFrame
        df = pd.read_csv(uploaded_file)
        
        # Validate and prepare data
        success, message, df_cleaned = validate_and_prepare_dataframe(df, comment_column="Cuerpo")
        
        if not success:
            st.error(message)
            return
        
        # Show preview
        total_comments = len(df_cleaned)
        st.markdown(f"### 📋 Preview ({total_comments} comments)")
        st.dataframe(df_cleaned.head(5), hide_index=True)
        
        # Button to start analysis
        if st.button("🔍 Analyze Comments", type="primary"):
            if not config['api_key_status']:
                st.error("Please configure your OpenAI API Key in the .env file or enter it in the sidebar panel")
                return
            
            # Start analysis
            with st.spinner("Preparing analysis..."):
                # Split into chunks
                chunks, total_comments = split_dataframe_into_chunks(
                    df_cleaned, 
                    comment_column="Cuerpo",
                    chunk_size=config['chunk_size'],
                    max_comments=config['max_comments']
                )
            
            # Create progress tracking system
            total_steps = len(chunks) + 1  # +1 for the final analysis
            progress_bar, progress_text, update_progress = progress_tracker(total_steps)
            
            # Process chunks
            chunk_analyses = []
            
            for i, chunk in enumerate(chunks):
                update_progress(i, f"Analyzing group {i+1} of {len(chunks)} ({len(chunk)} comments)...")
                
                # Chunk analysis
                chunk_result = openai_service.analyze_comments_chunk(
                    chunk,
                    system_prompt=config['system_prompt'],
                    model=config['model'],
                    reasoning_effort=config['reasoning_effort']
                )
                
                # Check for errors
                if chunk_result.get("error", False):
                    st.error(f"Error analyzing group {i+1}: {chunk_result.get('analysis', 'Unknown error')}")
                    continue
                
                chunk_analyses.append(chunk_result)
                
                # Update progress bar
                update_progress(i + 1, f"Group {i+1} of {len(chunks)} completed")
            
            # Final analysis
            update_progress(len(chunks), "Generating final analysis...")
            
            with st.spinner("Generating final analysis..."):
                final_analysis = openai_service.generate_final_analysis(
                    chunk_analyses,
                    total_comments=total_comments,
                    chunks_count=len(chunks),
                    system_prompt=config['system_prompt'],
                    model=config['model'],
                    reasoning_effort=config['reasoning_effort']
                )
            
            # Update final progress
            update_progress(total_steps, "Analysis completed")
            
            # Check if the final analysis had errors
            if final_analysis.get("error", False):
                st.error(f"Error in final analysis: {final_analysis.get('analysis', 'Unknown error')}")
                return
            
            # Show success message
            st.success(f"✅ Analysis completed: {total_comments} comments processed in {len(chunks)} groups")
            
            # Calculate token totals
            token_counts = calculate_total_tokens(chunk_analyses + [final_analysis])
            
            # Display overall metrics
            metrics_display(
                total_comments=total_comments,
                tokens_reasoning=token_counts["tokens_reasoning"],
                total_tokens=token_counts["total_tokens"]
            )
            
            # Separator
            st.markdown("---")
            
            # Process and save results
            try:
                # Extract metrics for visualization
                metrics = extract_metrics_from_analysis(final_analysis["analysis"])
                
                # Extract key sections
                sections = extract_key_sections(final_analysis["analysis"])
                
                # Format sections for better presentation
                formatted_sections = format_analysis_sections(sections)
                
                # Save analysis to file
                filename = file_service.save_analysis_to_file(final_analysis["analysis"])
                
                # Display results in tabs
                results_tabs(
                    analysis_text=final_analysis["analysis"],
                    metrics=metrics,
                    formatted_sections=formatted_sections,
                    filepath=filename
                )
                
                # Save results in session state for future reference
                st.session_state.analysis_results = {
                    "analysis_text": final_analysis["analysis"],
                    "metrics": metrics,
                    "token_counts": token_counts,
                    "total_comments": total_comments,
                    "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
            except Exception as processing_error:
                logger.error(f"Error processing results: {str(processing_error)}")
                st.error("Analysis completed, but there was an error processing the results for display")
                st.text_area("Plain text analysis:", final_analysis["analysis"], height=400)
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        error_message(e)

def render_help_page() -> None:
    """Renders the help page."""
    st.title("📚 Help and Documentation")
    
    st.markdown("""
    ## 🔍 Comment Sentiment Analysis
    
    This application allows you to analyze customer comments to extract valuable insights 
    that can help you improve your products and marketing strategies.
    
    ### 📊 Main Features
    
    - **Sentiment Analysis**: Identifies the distribution of positive, negative, and neutral comments
    - **Topic Extraction**: Discovers the topics most mentioned by your customers
    - **Strength Identification**: Understands which aspects of your product are valued positively
    - **Detection of Areas for Improvement**: Identifies opportunities to improve your products
    - **Marketing Ideas**: Provides suggestions for campaigns based on customer comments
    - **Customer Segmentation**: Identifies different segments based on their preferences
    - **Actionable Recommendations**: Offers concrete actions to enhance customer satisfaction
    
    ### 📋 CSV File Requirements
    
    The CSV file must contain at least one column named 'Body' (or the name you specify 
    in the configuration) that contains the comments to analyze.
    
    ### ⚙️ Configuration Options
    
    - **Chunk Size**: Defines how many comments are processed together (10-200)
    - **Maximum Comments**: Limits the total number of comments to analyze
    - **Model**: Selects the OpenAI model to use
    - **Reasoning Effort**: Adjusts the depth of analysis
    - **Custom Instructions**: Modifies the instructions sent to the model
    
    ### 🔐 API Key Configuration
    
    To use this application, you need to configure your OpenAI API Key:
    
    1. Create a `.env` file in the main directory
    2. Add your API Key: `OPENAI_API_KEY=your_api_key_here`
    
    Alternatively, you can enter your API Key in the sidebar panel.
    """)
    
    st.markdown("---")
    
    with st.expander("❓ Frequently Asked Questions", expanded=False):
        st.markdown("""
        **Q: How many comments can I analyze at once?**
        
        A: There is no strict limit, but for best results and cost control, we recommend analyzing between 100 and 1000 comments at a time.
        
        **Q: How does the chunk size affect the analysis?**
        
        A: A larger chunk size reduces the number of API calls but may result in a less detailed analysis. A smaller chunk size allows for a more granular analysis but increases the number of calls and overall cost.
        
        **Q: How can I customize the analysis?**
        
        A: You can modify the instructions in the sidebar panel to focus the analysis on specific aspects or adjust the type of insights you want to obtain.
        
        **Q: What file formats are supported?**
        
        A: Currently, only CSV files are supported. Make sure your file has a column with the comments.
        """)
