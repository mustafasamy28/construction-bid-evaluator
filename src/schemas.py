from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class ProjectRequirements(BaseModel):
    constraints: list[str] = Field(description="Technical and regulatory constraints")
    scope: str = Field(description="Project scope and deliverables")
    priorities: list[str] = Field(description="Key priorities (cost, timeline, quality, etc.)")


class ContractorProfile(BaseModel):
    contractor_name: str
    reputation_score: float = Field(ge=0, le=1, description="Reputation score 0-1")
    recent_projects: list[str] = Field(default_factory=list)
    red_flags_found: list[str] = Field(default_factory=list)
    credibility_sources: list[str] = Field(default_factory=list)


class BidScore(BaseModel):
    bid_id: str
    contractor_name: str
    cost_score: float = Field(ge=0, le=1, description="Cost competitiveness 0-1")
    timeline_score: float = Field(ge=0, le=1, description="Timeline feasibility 0-1")
    scope_score: float = Field(ge=0, le=1, description="Scope completeness 0-1")
    risk_score: float = Field(ge=0, le=1, description="Risk assessment 0-1")
    reputation_score: float = Field(ge=0, le=1, description="Reputation from research 0-1")
    overall_score: float = Field(ge=0, le=1, description="Weighted overall score")
    reasoning: str = Field(description="Chain-of-thought reasoning for scores")


class RedFlagType(str, Enum):
    INCOMPLETE_SCOPE = "INCOMPLETE_SCOPE"
    SUSPICIOUSLY_LOW_COST = "SUSPICIOUSLY_LOW_COST"
    VAGUE_TIMELINE = "VAGUE_TIMELINE"
    POOR_REPUTATION = "POOR_REPUTATION"
    REQUIRES_CLARIFICATION = "REQUIRES_CLARIFICATION"
    SUBCONTRACTOR_RISK = "SUBCONTRACTOR_RISK"
    CONSTRAINT_VIOLATION_RISK = "CONSTRAINT_VIOLATION_RISK"
    OPERATIONAL_DISRUPTION_RISK = "OPERATIONAL_DISRUPTION_RISK"
    OTHER = "OTHER"


class RedFlag(BaseModel):
    type: RedFlagType
    severity: Literal["low", "medium", "high", "critical"]
    evidence: str
    affected_bid: str


class RecommendationType(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT_ALL = "REJECT_ALL"
    REQUIRES_CLARIFICATION = "REQUIRES_CLARIFICATION"


class FinalRecommendation(BaseModel):
    recommendation_type: RecommendationType
    ranked_bids: list[str] = Field(description="Bid IDs ranked by score")
    confidence: float = Field(ge=0, le=1, description="Confidence in recommendation")
    rationale: str = Field(description="Explanation of recommendation")
    trade_offs: list[str] = Field(default_factory=list, description="Key trade-offs considered")

