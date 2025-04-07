"""
Utilities to extract metrics from the analysis.
"""
import re
import logging
from typing import Dict, List, Any

# Configure logger
logger = logging.getLogger(__name__)

def extract_metrics_from_analysis(analysis_text: str) -> Dict[str, Any]:
    """
    Extracts key metrics from the analysis text for visualization.
    
    Args:
        analysis_text: The analysis text
        
    Returns:
        Dictionary with extracted metrics
    """
    logger.info("Extracting metrics from the analysis")
    
    # Initialize metrics structure
    metrics = {
        "sentiment_distribution": {
            "Positive": 0,
            "Neutral": 0,
            "Negative": 0
        },
        "top_themes": [],
        "strengths": [],
        "improvements": []
    }
    
    try:
        # Extract sentiment distribution using regular expressions
        
        # Find positive percentages
        positive_matches = re.findall(r'(?:positiv[oa]s?|favorables?)\D*?(\d+(?:\.\d+)?)%', analysis_text, re.IGNORECASE)
        if positive_matches:
            metrics["sentiment_distribution"]["Positive"] = float(positive_matches[0])
        
        # Find negative percentages
        negative_matches = re.findall(r'(?:negativ[oa]s?|desfavorables?)\D*?(\d+(?:\.\d+)?)%', analysis_text, re.IGNORECASE)
        if negative_matches:
            metrics["sentiment_distribution"]["Negative"] = float(negative_matches[0])
        
        # Find neutral percentages
        neutral_matches = re.findall(r'(?:neutral(?:es)?)\D*?(\d+(?:\.\d+)?)%', analysis_text, re.IGNORECASE)
        if neutral_matches:
            metrics["sentiment_distribution"]["Neutral"] = float(neutral_matches[0])
        
        # If no matches are found, use default values
        total = sum(metrics["sentiment_distribution"].values())
        if total == 0:
            logger.warning("No sentiment percentages found, using default values")
            metrics["sentiment_distribution"] = {"Positive": 60, "Neutral": 25, "Negative": 15}
        elif total != 100:
            # Normalize to 100%
            logger.info(f"Normalizing sentiment percentages (current total: {total}%)")
            factor = 100 / total
            for key in metrics["sentiment_distribution"]:
                metrics["sentiment_distribution"][key] *= factor
        
        # Try to extract main themes
        # Example pattern: "The main themes are: quality (45%), price (30%), service (25%)"
        themes_section = re.search(r'(?:themes|aspects)(?:\s+main|\s+most\s+mentioned).*?(?:\:|\n)(.*?)(?:\n\n|\n[A-Z])', 
                                 analysis_text, re.IGNORECASE | re.DOTALL)
        
        if themes_section:
            themes_text = themes_section.group(1)
            # Extract individual themes
            theme_matches = re.findall(r'([a-zá-úñ\s]+)(?:\s*\((\d+(?:\.\d+)?)%\))?', themes_text, re.IGNORECASE)
            
            if theme_matches:
                for theme, percentage in theme_matches:
                    theme = theme.strip()
                    if theme and not theme.isspace() and len(theme) > 2:
                        perc = float(percentage) if percentage else 0
                        metrics["top_themes"].append({"name": theme, "percentage": perc})
        
        logger.info(f"Metrics extracted: {len(metrics['sentiment_distribution'])} sentiments, {len(metrics['top_themes'])} themes")
        return metrics
        
    except Exception as e:
        logger.error(f"Error extracting metrics: {str(e)}")
        # Return default metrics in case of error
        return {
            "sentiment_distribution": {"Positive": 60, "Neutral": 25, "Negative": 15},
            "top_themes": [],
            "strengths": [],
            "improvements": []
        }

def extract_key_sections(analysis_text: str) -> Dict[str, str]:
    """
    Extracts key sections from the analysis to display in a structured format.
    
    Args:
        analysis_text: The full analysis text
        
    Returns:
        Dictionary with extracted sections
    """
    sections = {
        "sentiment": "",
        "themes": "",
        "strengths": "",
        "improvements": "",
        "marketing": "",
        "segmentation": "",
        "recommendations": ""
    }
    
    try:
        # Patterns for each section
        patterns = {
            "sentiment": r'(?:GENERAL\s+SENTIMENT|1\..*?SENTIMENT).*?(?:\n|:)(.*?)(?:\n\n|\n[2-7]\.)',
            "themes": r'(?:MAIN\s+TOPICS|2\..*?TOPICS).*?(?:\n|:)(.*?)(?:\n\n|\n[3-7]\.)',
            "strengths": r'(?:PRODUCT\s+STRENGTHS|3\..*?STRENGTHS).*?(?:\n|:)(.*?)(?:\n\n|\n[4-7]\.)',
            "improvements": r'(?:AREAS\s+FOR\s+IMPROVEMENT|4\..*?IMPROVEMENTS).*?(?:\n|:)(.*?)(?:\n\n|\n[5-7]\.)',
            "marketing": r'(?:MARKETING\s+OPPORTUNITIES|5\..*?MARKETING).*?(?:\n|:)(.*?)(?:\n\n|\n[6-7]\.)',
            "segmentation": r'(?:SEGMENTATION|6\..*?SEGMENTATION).*?(?:\n|:)(.*?)(?:\n\n|\n[7]\.)',
            "recommendations": r'(?:ACTIONABLE\s+RECOMMENDATIONS|7\..*?RECOMMENDATIONS).*?(?:\n|:)(.*?)(?:\n\n|\Z)'
        }
        
        # Extract each section
        for key, pattern in patterns.items():
            match = re.search(pattern, analysis_text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[key] = match.group(1).strip()
        
        logger.info(f"Extracted {sum(1 for v in sections.values() if v)} sections from the analysis")
        return sections
        
    except Exception as e:
        logger.error(f"Error extracting key sections: {str(e)}")
        return sections

def extract_numbered_points(text: str, max_points: int = 5, prefix: str = "") -> List[str]:
    """
    Extracts points from a text and returns them as a list of strings.
    Maintains any numbering or existing formatting.
    
    Args:
        text: Text to process
        max_points: Maximum number of points to return
        prefix: Optional prefix to search for (• - * etc.)
        
    Returns:
        List of extracted points
    """
    if not text or not text.strip():
        return []
    
    points = []
    
    # Detect if the text has a numbered list structure
    numbered_pattern = rf'(?:^\s*{re.escape(prefix) if prefix else ""}(?:\d+[\.|\)]|\-|\•|\*)\s*)(.*?)(?:\n|$)'
    numbered_matches = re.findall(numbered_pattern, text, re.MULTILINE)
    
    if numbered_matches:
        # Extract points while keeping their original numbering
        pattern = rf'^\s*{re.escape(prefix) if prefix else ""}(?:(\d+)[\.|\)]|\-|\•|\*)\s*(.*?)(?:\n|$)'
        for match in re.finditer(pattern, text, re.MULTILINE):
            num = match.group(1) if match.group(1) else ""
            content = match.group(2).strip() if match.group(2) else match.group(0).strip()
            if num:
                points.append(f"{num}) {content}")
            else:
                points.append(content)
    else:
        # If no list format, split by sentences or paragraphs
        sentences = re.split(r'(?<=[.!?])\s+', text)
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Use paragraphs if they seem more structured, otherwise use sentences
        candidates = paragraphs if len(paragraphs) <= len(sentences) * 0.7 else sentences
        points = [s.strip() for s in candidates if len(s.strip()) > 10]
    
    # Limit to the most important points
    if len(points) > max_points:
        points = points[:max_points]
    
    return points


def format_key_points(section_text: str, max_points: int = 5) -> str:
    """
    Simplifies and formats a section of text to show only the key points.
    
    Args:
        section_text: The full text of the section
        max_points: Maximum number of points to include
        
    Returns:
        Formatted text with the key points
    """
    # If the text is empty, return an empty string
    if not section_text or not section_text.strip():
        return ""
        
    # Search for numbered or bulleted list patterns
    bullet_points = re.findall(r'(?:^\s*(?:\d+\.|\-|\•)\s*)(.*?)(?:\n|$)', section_text, re.MULTILINE)
    
    # If there are no list formats, look for complete sentences
    if not bullet_points:
        sentences = re.split(r'(?<=[.!?])\s+', section_text)
        bullet_points = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    # If still no points, split by lines
    if not bullet_points:
        bullet_points = [line.strip() for line in section_text.split('\n') if len(line.strip()) > 10]
    
    # Limit to the most important points
    if len(bullet_points) > max_points:
        bullet_points = bullet_points[:max_points]
    
    # Format as a list with bullets
    formatted_text = ""
    for point in bullet_points:
        # Clean the point
        clean_point = point.strip()
        # Remove bullet point prefixes if they exist
        clean_point = re.sub(r'^[•\-\*]\s*', '', clean_point)
        # Add to formatted text
        if clean_point:
            formatted_text += f"• {clean_point}\n\n"
    
    return formatted_text
