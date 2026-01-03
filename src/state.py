from typing import TypedDict, Optional
from src.schemas import (
    ProjectRequirements,
    ContractorProfile,
    BidScore,
    RedFlag,
    FinalRecommendation,
)


class BidEvalState(TypedDict):
    project_description: str
    bids: list[dict]
    requirements: Optional[ProjectRequirements]
    contractor_profiles: list[ContractorProfile]
    scores: list[BidScore]
    red_flags: list[RedFlag]
    final_recommendation: Optional[FinalRecommendation]

