"""
Utilities for data processing.
"""
import pandas as pd
import logging
from typing import List, Tuple, Optional, Dict, Any

# Configure logger
logger = logging.getLogger(__name__)

def validate_and_prepare_dataframe(df: pd.DataFrame, comment_column: str = 'Body') -> Tuple[bool, str, pd.DataFrame]:
    """
    Validates and prepares a DataFrame for analysis.
    
    Args:
        df: DataFrame to validate and prepare
        comment_column: Name of the column containing the comments
        
    Returns:
        Tuple with (success, message, processed_dataframe)
    """
    # Check if the DataFrame is None
    if df is None:
        return False, "No valid DataFrame provided", None
    
    # Check if the comment column exists
    if comment_column not in df.columns:
        return False, f"The CSV file must contain a column '{comment_column}'", None
    
    # Clean and prepare the data
    try:
        # Remove rows with empty or null comments
        df_cleaned = df.dropna(subset=[comment_column])
        df_cleaned = df_cleaned[df_cleaned[comment_column].str.strip() != '']
        
        # Check if there are comments left to analyze
        if len(df_cleaned) == 0:
            return False, f"No valid comments in the '{comment_column}' column", None
        
        logger.info(f"DataFrame prepared: {len(df_cleaned)} valid comments")
        return True, f"DataFrame successfully prepared: {len(df_cleaned)} valid comments", df_cleaned
    
    except Exception as e:
        logger.error(f"Error preparing DataFrame: {str(e)}")
        return False, f"Error preparing the data: {str(e)}", None

def split_dataframe_into_chunks(
    df: pd.DataFrame, 
    comment_column: str = 'Body', 
    chunk_size: int = 50,
    max_comments: int = 0
) -> Tuple[List[List[str]], int]:
    """
    Splits a DataFrame into chunks for processing.
    
    Args:
        df: DataFrame to split
        comment_column: Name of the column containing the comments
        chunk_size: Size of each chunk
        max_comments: Maximum number of comments to process (0 for all)
        
    Returns:
        Tuple with (list_of_chunks, total_comments)
    """
    try:
        # Limit the number of comments if specified
        if max_comments > 0:
            df = df.head(max_comments)
        
        # Get the list of comments
        comments = df[comment_column].tolist()
        total_comments = len(comments)
        
        # Split into chunks
        chunks = [comments[i:i + chunk_size] for i in range(0, total_comments, chunk_size)]
        
        logger.info(f"Data split into {len(chunks)} chunks (total: {total_comments} comments)")
        return chunks, total_comments
    
    except Exception as e:
        logger.error(f"Error splitting DataFrame into chunks: {str(e)}")
        raise

def calculate_total_tokens(analyses: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculates the total tokens used in the analysis.
    
    Args:
        analyses: List of analysis results
        
    Returns:
        Dictionary with token totals
    """
    try:
        tokens_reasoning = sum(a.get("tokens_reasoning", 0) for a in analyses if not a.get("error", False))
        total_tokens = sum(a.get("total_tokens", 0) for a in analyses if not a.get("error", False))
        
        return {
            "tokens_reasoning": tokens_reasoning,
            "total_tokens": total_tokens
        }
    except Exception as e:
        logger.error(f"Error calculating tokens: {str(e)}")
        return {"tokens_reasoning": 0, "total_tokens": 0}
