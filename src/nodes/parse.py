import logging
from langchain_core.prompts import ChatPromptTemplate
from src.state import BidEvalState
from src.schemas import ProjectRequirements
from src.config import gpt4o_mini
from src.tools.serper import search_all_contractors

logger = logging.getLogger(__name__)


async def parse_and_enrich(state: BidEvalState) -> BidEvalState:
    """Extract requirements and enrich contractor profiles."""
    # Input validation
    if not state.get("project_description"):
        raise ValueError("Missing required field: project_description")
    
    if not state.get("bids") or not isinstance(state["bids"], list):
        raise ValueError("Missing or invalid 'bids' field. Expected a non-empty list.")
    
    if len(state["bids"]) == 0:
        raise ValueError("No bids provided in state")
    
    project_desc = state["project_description"]
    bids = state["bids"]
    
    logger.info(f"Parsing requirements for project with {len(bids)} bids")
    
    # Extract requirements
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract project requirements from the description. Be specific and comprehensive."),
            ("user", "Project description:\n{project_description}"),
        ])
        
        chain = prompt | gpt4o_mini.with_structured_output(ProjectRequirements)
        requirements = chain.invoke({"project_description": project_desc})
        logger.info("Successfully extracted project requirements")
    except Exception as e:
        logger.error(f"Error extracting requirements: {str(e)}")
        raise ValueError(f"Failed to extract project requirements: {str(e)}")
    
    # Get contractor names
    contractor_names = [bid.get("contractor_name", "") for bid in bids if bid.get("contractor_name")]
    
    # Handle empty contractor names list
    if not contractor_names:
        logger.warning("No contractor names found in bids, skipping Serper search")
        contractor_profiles = []
    else:
        logger.info(f"Searching for {len(contractor_names)} contractors via Serper")
        # Parallel Serper searches
        contractor_profiles = await search_all_contractors(contractor_names)
        logger.info(f"Retrieved profiles for {len(contractor_profiles)} contractors")
    
    return {
        **state,
        "requirements": requirements,
        "contractor_profiles": contractor_profiles,
    }

