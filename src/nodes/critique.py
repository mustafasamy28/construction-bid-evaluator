import logging
from langchain_core.prompts import ChatPromptTemplate
from src.state import BidEvalState
from src.schemas import FinalRecommendation, RecommendationType, RedFlagType
from src.config import gpt4o

logger = logging.getLogger(__name__)


def critique_and_finalize(state: BidEvalState) -> BidEvalState:
    """Self-critique analysis and finalize recommendation."""
    # Input validation
    if not state.get("scores") or not isinstance(state["scores"], list):
        logger.error("Missing or invalid 'scores' field in state")
        recommendation = FinalRecommendation(
            recommendation_type=RecommendationType.REJECT_ALL,
            ranked_bids=[],
            confidence=1.0,
            rationale="No scores available for evaluation.",
            trade_offs=[],
        )
        return {**state, "final_recommendation": recommendation}
    
    scores = state["scores"]
    red_flags = state.get("red_flags", [])
    requirements = state.get("requirements")
    
    logger.info(f"Critiquing {len(scores)} scored bids with {len(red_flags)} red flags")
    
    if not scores:
        recommendation = FinalRecommendation(
            recommendation_type=RecommendationType.REJECT_ALL,
            ranked_bids=[],
            confidence=1.0,
            rationale="No valid bids to evaluate.",
            trade_offs=[],
        )
        return {**state, "final_recommendation": recommendation}
    
    top_score = scores[0].overall_score
    
    # Decision logic - reject ALL if truly all bids are bad
    # Check if ALL bids have critical issues
    critical_red_flags = [f for f in red_flags if f.severity in ["high", "critical"]]
    top_bid_id = scores[0].bid_id if scores else None
    top_bid_critical_flags = [f for f in critical_red_flags if f.affected_bid == top_bid_id]
    
    # Count how many bids have critical issues
    bids_with_critical_issues = len(set(f.affected_bid for f in critical_red_flags))
    
    # Only reject all if:
    # 1. Top score is very low (< 0.60), OR
    # 2. Top score is low (< 0.65) AND top bid has critical flags, OR
    # 3. All bids have critical red flags (all bids affected)
    if top_score < 0.60 or \
       (top_score < 0.65 and len(top_bid_critical_flags) > 0) or \
       (bids_with_critical_issues >= len(scores) and len(scores) > 0 and top_score < 0.70):
        recommendation = FinalRecommendation(
            recommendation_type=RecommendationType.REJECT_ALL,
            ranked_bids=[s.bid_id for s in scores],
            confidence=0.85,
            rationale=f"Top bid score ({top_score:.2f}) below acceptable threshold. All bids have significant critical issues.",
            trade_offs=[],
        )
    else:
        # Enhanced self-review for missed issues
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are reviewing a bid evaluation analysis. Provide a final recommendation following these guidelines:

**DECISION RULES:**
1. **ACCEPT** if:
   - Top bid has overall_score >= 0.75 AND
   - No critical red flags (high/critical severity) on top bid AND
   - Top bid clearly superior to others (score difference > 0.05) OR confidence is high

2. **REQUIRES_CLARIFICATION** if:
   - Top bid has medium-severity issues that need clarification OR
   - Close scores between top bids (< 0.05 difference) OR
   - Some concerns but not critical enough to reject

3. **REJECT_ALL** if:
   - Top bid score < 0.65 OR
   - All bids have critical red flags OR
   - No acceptable bids found

**Your task:**
1. Review scores and red flags
2. Apply decision rules above strictly
3. Choose ACCEPT when appropriate - don't be overly conservative
4. Only use REQUIRES_CLARIFICATION when there are genuine concerns needing clarification
5. Provide well-calibrated confidence and comprehensive trade-offs"""),
            ("user", """Bid Scores (ranked by overall_score):
{scores}

Red Flags Detected:
{red_flags}

Project Requirements:
{requirements}

Perform self-critique and provide final recommendation. Be thorough in identifying any missed issues or inconsistencies."""),
        ])
        
        try:
            chain = prompt | gpt4o.with_structured_output(FinalRecommendation)
            
            recommendation = chain.invoke({
                "scores": [s.model_dump_json() for s in scores],
                "red_flags": [f.model_dump_json() for f in red_flags],
                "requirements": requirements.model_dump_json() if requirements else "",
            })
            
            # Ensure ranked_bids matches scores order
            recommendation.ranked_bids = [s.bid_id for s in scores]
            
            # Additional validation checks - but be less conservative
            # Only downgrade to REQUIRES_CLARIFICATION if there are critical issues with top bid
            top_bid_id = recommendation.ranked_bids[0] if recommendation.ranked_bids else None
            
            # Check for gaming attempts - only downgrade if top bid has this issue
            gaming_flags = [f for f in red_flags if f.type == RedFlagType.SUSPICIOUSLY_LOW_COST and f.affected_bid == top_bid_id]
            if gaming_flags and recommendation.recommendation_type == RecommendationType.ACCEPT:
                # Only require clarification if severity is high/critical
                if any(f.severity in ["high", "critical"] for f in gaming_flags):
                    recommendation.recommendation_type = RecommendationType.REQUIRES_CLARIFICATION
                    recommendation.trade_offs.append("Top bid has suspiciously low cost - requires clarification")
            
            # Check for incomplete bids - only downgrade if top bid has critical incomplete scope
            incomplete_flags_top = [f for f in red_flags 
                                  if f.type == RedFlagType.INCOMPLETE_SCOPE 
                                  and f.affected_bid == top_bid_id
                                  and f.severity in ["high", "critical"]]
            if incomplete_flags_top and recommendation.recommendation_type == RecommendationType.ACCEPT:
                # Only require clarification if it's a critical issue
                if any(f.severity == "critical" for f in incomplete_flags_top):
                    recommendation.recommendation_type = RecommendationType.REQUIRES_CLARIFICATION
                    recommendation.trade_offs.append("Top bid has critical incomplete scope - requires clarification")
                else:
                    # Just reduce confidence, don't downgrade
                    recommendation.confidence = max(0.6, recommendation.confidence - 0.15)
                    recommendation.trade_offs.append("Top bid has some scope gaps - review recommended")
            
            # Validate confidence is reasonable given score differences
            if len(scores) > 1:
                score_diff = scores[0].overall_score - scores[1].overall_score
                if score_diff < 0.05 and recommendation.confidence > 0.8:
                    recommendation.confidence = min(0.75, recommendation.confidence)
                    recommendation.trade_offs.append("Close scores between top bids - lower confidence")
            
            logger.info(f"Final recommendation: {recommendation.recommendation_type.value} with confidence {recommendation.confidence:.2f}")
            
        except Exception as e:
            logger.error(f"Error in critique step: {str(e)}")
            # Fallback recommendation
            recommendation = FinalRecommendation(
                recommendation_type=RecommendationType.REQUIRES_CLARIFICATION,
                ranked_bids=[s.bid_id for s in scores],
                confidence=0.6,
                rationale=f"Error during critique step: {str(e)}. Review scores manually.",
                trade_offs=["System error occurred - manual review recommended"],
            )
    
    return {
        **state,
        "final_recommendation": recommendation,
    }

