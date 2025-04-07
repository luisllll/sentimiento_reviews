"""
Services to interact with the OpenAI API.
Provides functions to analyze comments using reasoning models.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
import streamlit as st
from config.settings import DEFAULT_MODEL, DEFAULT_REASONING_EFFORT, DEFAULT_MAX_TOKENS_CHUNK, DEFAULT_MAX_TOKENS_FINAL

# Configure logger
logger = logging.getLogger(__name__)

class OpenAIService:
    """Class to manage interactions with the OpenAI API."""
    
    def __init__(self):
        """Initializes the OpenAI service."""
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initializes the OpenAI client."""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OpenAI API Key not found in environment variables")
                return
            
            self._client = OpenAI()
            logger.info("OpenAI client successfully initialized")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            raise
    
    @property
    def client(self) -> OpenAI:
        """Returns the OpenAI client."""
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
        Analyzes a chunk of comments using the OpenAI model.
        
        Args:
            comments: List of comments to analyze
            system_prompt: System prompt for the model
            model: OpenAI model to use
            reasoning_effort: Reasoning effort level ('low', 'medium', 'high')
            max_tokens: Maximum number of tokens for the response
            
        Returns:
            Dict with the analysis results
        """
        logger.info(f"Analyzing chunk of {len(comments)} comments")
        
        comments_text = "\n\n".join([f"Comment {i+1}: {comment}" for i, comment in enumerate(comments)])
        
        chunk_prompt = f"""
        Analyze this set of {len(comments)} customer comments and provide preliminary insights on:
        
        1. Approximate sentiment distribution
        2. Main topics mentioned
        3. Patterns of complaints or praise identified
        
        Comments:
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
                "tokens_reasoning": response.usage.output_tokens_details.reasoning_tokens 
                                     if hasattr(response.usage.output_tokens_details, 'reasoning_tokens') else 0,
                "total_tokens": response.usage.total_tokens
            }
            
            logger.info(f"Analysis completed: {result['total_tokens']} tokens used")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing chunk: {str(e)}")
            return {
                "analysis": f"Error: {str(e)}",
                "tokens_reasoning": 0,
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
        Generates the final analysis based on the chunk analyses.
        
        Args:
            chunk_analyses: List of analysis results by chunks
            total_comments: Total number of comments analyzed
            chunks_count: Number of chunks processed
            system_prompt: System prompt for the model
            model: OpenAI model to use
            reasoning_effort: Reasoning effort level
            max_tokens: Maximum number of tokens for the response
            
        Returns:
            Dict with the final analysis results
        """
        logger.info(f"Generating final analysis for {total_comments} comments in {chunks_count} chunks")
        
        # Check if there are any errors in the chunks
        errors = [chunk for chunk in chunk_analyses if chunk.get("error", False)]
        if errors:
            logger.warning(f"Found {len(errors)} errors in chunk analyses")
        
        chunk_insights = "\n\n".join([
            f"--- INSIGHTS FROM GROUP {i+1} ({chunk_analyses.index(chunk)+1} of {chunks_count}) ---\n{chunk['analysis']}"
            for i, chunk in enumerate(chunk_analyses) if not chunk.get("error", False)
        ])
        
        final_prompt = f"""
        You have analyzed a total of {total_comments} customer comments in {chunks_count} groups.
        
        Based on the preliminary analyses from each group, provide a comprehensive executive report with:
        
        1. GENERAL SENTIMENT: Estimated sentiment distribution (% positive, negative, neutral) 
           and main trends
        
        2. MAIN TOPICS: The 5-7 most mentioned topics, their relative frequency, and their relationship with sentiment
        
        3. PRODUCT STRENGTHS: Main positive aspects mentioned by customers
        
        4. AREAS FOR IMPROVEMENT: Main complaints or suggestions for improvement, ranked by frequency and impact
        
        5. MARKETING OPPORTUNITIES: 3-5 concrete ideas for marketing campaigns based on the comments
        
        6. SEGMENTATION: Identification of different customer segments based on their preferences or concerns
        
        7. ACTIONABLE RECOMMENDATIONS: 5 concrete, prioritized recommendations to improve customer satisfaction
        
        Here are the preliminary insights from each group:
        
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
                "tokens_reasoning": response.usage.output_tokens_details.reasoning_tokens 
                                     if hasattr(response.usage.output_tokens_details, 'reasoning_tokens') else 0,
                "total_tokens": response.usage.total_tokens
            }
            
            logger.info(f"Final analysis completed: {result['total_tokens']} tokens used")
            return result
            
        except Exception as e:
            logger.error(f"Error in final analysis: {str(e)}")
            return {
                "analysis": f"Error: {str(e)}",
                "tokens_reasoning": 0,
                "total_tokens": 0,
                "error": True
            }

# Global instance of the service
openai_service = OpenAIService()
