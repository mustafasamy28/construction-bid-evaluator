import httpx
import asyncio
import logging
from typing import List
from src.schemas import ContractorProfile
from src.config import SERPER_API_KEY

logger = logging.getLogger(__name__)


async def search_contractor(contractor_name: str) -> ContractorProfile:
    """Search for contractor information using Serper API."""
    if not contractor_name or not contractor_name.strip():
        logger.warning(f"Empty contractor name provided, returning default profile")
        return ContractorProfile(
            contractor_name=contractor_name or "Unknown",
            reputation_score=0.5,
            recent_projects=[],
            red_flags_found=[],
            credibility_sources=[],
        )
    
    if not SERPER_API_KEY:
        logger.warning(f"No SERPER_API_KEY configured, returning default profile for {contractor_name}")
        return ContractorProfile(
            contractor_name=contractor_name,
            reputation_score=0.5,
            recent_projects=[],
            red_flags_found=[],
            credibility_sources=[],
        )
    
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "q": f"{contractor_name} construction company reviews projects",
        "tbs": "qdr:y",  # Last 12 months
        "num": 10,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException:
        logger.error(f"Serper API timeout for {contractor_name}, returning default profile")
        return ContractorProfile(
            contractor_name=contractor_name,
            reputation_score=0.5,
            recent_projects=[],
            red_flags_found=[],
            credibility_sources=[],
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Serper API HTTP error for {contractor_name}: {e.response.status_code}, returning default profile")
        return ContractorProfile(
            contractor_name=contractor_name,
            reputation_score=0.5,
            recent_projects=[],
            red_flags_found=[],
            credibility_sources=[],
        )
    except Exception as e:
        logger.error(f"Unexpected error searching for {contractor_name}: {str(e)}, returning default profile")
        return ContractorProfile(
            contractor_name=contractor_name,
            reputation_score=0.5,
            recent_projects=[],
            red_flags_found=[],
            credibility_sources=[],
        )

    # Extract information
    organic_results = data.get("organic", [])
    news_results = data.get("news", [])
    
    # Weight news sources higher
    all_results = (news_results * 2) + organic_results
    
    recent_projects = []
    red_flags = []
    credibility_sources = []
    
    for result in all_results[:10]:
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        link = result.get("link", "")
        
        credibility_sources.append(link)
        
        # Simple keyword detection for projects and red flags
        text = f"{title} {snippet}".lower()
        if any(word in text for word in ["project", "completed", "construction", "building"]):
            recent_projects.append(f"{title}: {snippet[:100]}")
        
        if any(word in text for word in ["lawsuit", "complaint", "violation", "failed", "bankruptcy"]):
            red_flags.append(f"{title}: {snippet[:100]}")
    
    # Calculate reputation score (improved)
    # Base score starts at 0.7 (neutral-positive)
    base_score = 0.7
    
    # Positive signals boost score
    positive_keywords = ["award", "certified", "excellence", "success", "completed", "delivered"]
    positive_count = sum(1 for result in all_results[:10] 
                         if any(kw in result.get("title", "").lower() + result.get("snippet", "").lower() 
                               for kw in positive_keywords))
    positive_boost = min(0.2, positive_count * 0.05)
    
    # Negative signals reduce score
    negative_penalty = min(0.4, len(red_flags) * 0.1)
    
    # News sources indicate credibility (weighted higher)
    news_boost = min(0.1, len(news_results) * 0.02)
    
    reputation_score = max(0.3, min(1.0, base_score + positive_boost - negative_penalty + news_boost))
    
    return ContractorProfile(
        contractor_name=contractor_name,
        reputation_score=reputation_score,
        recent_projects=recent_projects[:5],
        red_flags_found=red_flags[:3],
        credibility_sources=credibility_sources[:5],
    )


async def search_all_contractors(contractor_names: List[str]) -> List[ContractorProfile]:
    """Parallel search for all contractors."""
    if not contractor_names:
        logger.warning("No contractor names provided for search")
        return []
    
    # Filter out empty names
    valid_names = [name for name in contractor_names if name and name.strip()]
    if not valid_names:
        logger.warning("No valid contractor names after filtering")
        return []
    
    tasks = [search_contractor(name) for name in valid_names]
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Handle any exceptions that occurred during gathering
        profiles = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error searching for {valid_names[i]}: {str(result)}")
                profiles.append(ContractorProfile(
                    contractor_name=valid_names[i],
                    reputation_score=0.5,
                    recent_projects=[],
                    red_flags_found=[],
                    credibility_sources=[],
                ))
            else:
                profiles.append(result)
        return profiles
    except Exception as e:
        logger.error(f"Error in parallel search: {str(e)}")
        return [ContractorProfile(
            contractor_name=name,
            reputation_score=0.5,
            recent_projects=[],
            red_flags_found=[],
            credibility_sources=[],
        ) for name in valid_names]

