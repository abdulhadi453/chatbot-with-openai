"""
Web search utility for fetching real-time information.
Uses DuckDuckGo search to provide current data without API keys.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, UTC
from ddgs import DDGS

logger = logging.getLogger(__name__)


async def search_web(query: str, max_results: int = 5) -> Dict:
    """
    Search the web for current information.

    Args:
        query: Search query
        max_results: Maximum number of results to return

    Returns:
        Dictionary containing search results and metadata
    """
    try:
        logger.info(f"Performing web search for: {query}")

        # Get current datetime for context
        current_time = datetime.now(UTC)

        # Perform search using DuckDuckGo
        results = []
        try:
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                results = list(search_results) if search_results else []
        except Exception as search_error:
            logger.error(f"DuckDuckGo search error: {search_error}")
            return {
                "success": False,
                "query": query,
                "error": str(search_error),
                "message": "Search failed - please try rephrasing the query",
                "timestamp": current_time.isoformat()
            }

        if not results:
            logger.warning(f"No search results found for query: {query}")
            return {
                "success": False,
                "query": query,
                "message": "No relevant information found. The topic may be too recent or specific.",
                "timestamp": current_time.isoformat()
            }

        # Format results with more detail for the AI
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append({
                "position": i,
                "title": result.get("title", "").strip(),
                "snippet": result.get("body", "").strip(),
                "url": result.get("href", "").strip(),
            })

        logger.info(f"Web search completed: {len(formatted_results)} results found")

        # Create a summary for the AI
        summary = f"Search completed for '{query}' - Found {len(formatted_results)} results:\n\n"
        for r in formatted_results:
            summary += f"{r['position']}. {r['title']}\n{r['snippet']}\nSource: {r['url']}\n\n"

        return {
            "success": True,
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results),
            "summary": summary,
            "timestamp": current_time.isoformat(),
            "current_date": current_time.strftime("%B %d, %Y"),
            "current_time_utc": current_time.strftime("%H:%M:%S UTC")
        }

    except Exception as e:
        logger.error(f"Web search error: {e}", exc_info=True)
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "message": "Search failed due to an unexpected error",
            "timestamp": datetime.now(UTC).isoformat()
        }


def get_current_datetime() -> Dict:
    """
    Get current date and time information.

    Returns:
        Dictionary with current date/time details
    """
    now = datetime.now(UTC)
    return {
        "iso": now.isoformat(),
        "date": now.strftime("%B %d, %Y"),
        "time_utc": now.strftime("%H:%M:%S UTC"),
        "day_of_week": now.strftime("%A"),
        "year": now.year,
        "month": now.month,
        "day": now.day
    }
