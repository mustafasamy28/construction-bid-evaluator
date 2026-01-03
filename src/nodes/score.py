import logging
from langchain_core.prompts import ChatPromptTemplate
from src.state import BidEvalState
from src.schemas import BidScore, RedFlag, RedFlagType
from src.config import gpt4o_mini
from src.utils import calculate_dynamic_weights, detect_constraint_violations

logger = logging.getLogger(__name__)


def score_and_flag(state: BidEvalState) -> BidEvalState:
    """Score bids and detect red flags."""
    # Input validation
    if not state.get("bids") or not isinstance(state["bids"], list):
        raise ValueError("Missing or invalid 'bids' field")
    
    if len(state["bids"]) == 0:
        raise ValueError("No bids to score")
    
    if not state.get("requirements"):
        logger.warning("No requirements found in state, proceeding with empty requirements")
    
    bids = state["bids"]
    requirements = state["requirements"]
    contractor_profiles = {p.contractor_name: p for p in state.get("contractor_profiles", [])}
    
    # Calculate dynamic weights based on project priorities
    weights = calculate_dynamic_weights(requirements) if requirements else {
        "cost": 0.25,
        "timeline": 0.20,
        "scope": 0.25,
        "risk": 0.15,
        "reputation": 0.15,
    }
    logger.info(f"Scoring {len(bids)} bids with dynamic weights: Cost={weights['cost']:.0%}, Timeline={weights['timeline']:.0%}, Scope={weights['scope']:.0%}, Risk={weights['risk']:.0%}, Reputation={weights['reputation']:.0%}")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Score the bid across 5 dimensions (0-1 scale) using the contractor profile data from web research:

- cost_score: Cost competitiveness vs market benchmarks
- timeline_score: Timeline feasibility and realism. MUST consider recent_projects from contractor profile to assess if contractor has experience with similar timelines
- scope_score: Scope completeness vs requirements
- risk_score: Risk assessment (financial, technical, execution). MUST factor in red_flags_found from contractor profile and recent project history
- reputation_score: MUST use the reputation_score from the contractor profile (web research data). This is based on recent news, reviews, and credibility sources found online.

CRITICAL INSTRUCTIONS:
1. The contractor profile contains web research data from Serper API (recent news, reviews, projects)
2. reputation_score MUST match or closely align with the provided reputation_score from web research
3. Use recent_projects to inform timeline_score and risk_score - if contractor has similar projects, increase scores
4. If red_flags_found contains items, significantly reduce risk_score and reputation_score
5. Reference credibility_sources in your reasoning to show you're using the web research data
6. Provide detailed reasoning BEFORE assigning scores (chain-of-thought), explicitly mentioning how you used the contractor profile data"""),
        ("user", """Requirements: {requirements}
Bid: {bid}
Contractor Profile (from web research): {profile}

Score this bid. You MUST use the contractor profile data from web research in your scoring."""),
    ])
    
    chain = prompt | gpt4o_mini.with_structured_output(BidScore)
    
    scores = []
    red_flags = []
    
    for bid in bids:
        # Validate bid structure
        if not isinstance(bid, dict):
            logger.warning(f"Skipping invalid bid (not a dict): {bid}")
            continue
        
        contractor_name = bid.get("contractor_name", "")
        if not contractor_name:
            logger.warning(f"Skipping bid without contractor_name: {bid.get('id', 'unknown')}")
            continue
        
        bid_id = bid.get("id")
        if not bid_id:
            bid_id = f"bid_{len(scores)}"
            logger.warning(f"Bid missing 'id' field, generated ID: {bid_id}")
        
        profile = contractor_profiles.get(contractor_name)
        
        # Format profile data for better LLM understanding
        if profile:
            profile_data = {
                "contractor_name": profile.contractor_name,
                "reputation_score_from_web_research": profile.reputation_score,
                "recent_projects_found": profile.recent_projects,
                "red_flags_found_online": profile.red_flags_found,
                "credibility_sources": profile.credibility_sources,
                "note": "This data was retrieved from web search (Serper API) in the last 12 months"
            }
        else:
            profile_data = {
                "note": "No web research data available for this contractor"
            }
        
        try:
            result = chain.invoke({
                "requirements": requirements.model_dump_json() if requirements else "",
                "bid": bid,
                "profile": profile_data,
            })
        except Exception as e:
            logger.error(f"Error scoring bid {bid_id} for {contractor_name}: {str(e)}")
            continue
        
        if result:
            score = result
            score.bid_id = bid_id
            score.contractor_name = contractor_name
            
            # Check scope text for vagueness (heuristic check) - STRICTER
            scope_text = bid.get("scope", "").lower()
            vague_scope_keywords = ["construction", "building", "work", "renovation work"]
            is_vague_scope = len(scope_text.split()) < 10 or any(
                scope_text.strip() == keyword or scope_text.strip().startswith(keyword + " ")
                for keyword in vague_scope_keywords
            )
            
            # If scope is very vague, reduce scope_score more aggressively
            if is_vague_scope:
                if len(scope_text.split()) < 5:
                    # Extremely vague (e.g., "Building construction")
                    score.scope_score = min(score.scope_score, 0.50)
                elif len(scope_text.split()) < 10:
                    # Very vague
                    score.scope_score = min(score.scope_score, 0.65)
                else:
                    # Somewhat vague
                    score.scope_score = min(score.scope_score, 0.75)
                logger.info(f"Detected vague scope text for {contractor_name}, adjusted scope_score to {score.scope_score:.2f}")
            
            # Additional check: If scope mentions subcontracting critical work, reduce scope score
            if "subcontract" in scope_text or "subcontracted" in scope_text:
                if score.scope_score > 0.70:
                    # Reduce scope score if critical work is subcontracted without details
                    score.scope_score = max(0.60, score.scope_score - 0.10)
                    logger.info(f"Subcontracted work detected for {contractor_name}, reduced scope_score to {score.scope_score:.2f}")
            
            # ENFORCE: If Serper data exists, use it to adjust scores
            if profile and profile.reputation_score is not None:
                # Blend LLM's reputation_score with Serper's reputation_score (70% Serper, 30% LLM)
                # This ensures Serper data is actually used
                serper_reputation = profile.reputation_score
                llm_reputation = score.reputation_score
                score.reputation_score = (serper_reputation * 0.7) + (llm_reputation * 0.3)
                
                # Adjust risk_score based on Serper red flags
                if profile.red_flags_found:
                    # Reduce risk_score if red flags found online
                    risk_reduction = min(0.3, len(profile.red_flags_found) * 0.1)
                    score.risk_score = max(0.0, score.risk_score - risk_reduction)
                
                # Adjust timeline_score and risk_score based on recent projects
                if profile.recent_projects:
                    # Having recent projects increases confidence in timeline and reduces risk
                    project_bonus = min(0.15, len(profile.recent_projects) * 0.03)
                    score.timeline_score = min(1.0, score.timeline_score + project_bonus)
                    score.risk_score = min(1.0, score.risk_score + project_bonus * 0.5)
                elif not profile.recent_projects and profile.reputation_score < 0.7:
                    # No recent projects and low reputation = higher risk
                    score.risk_score = max(0.0, score.risk_score - 0.1)
            
            # Calculate weighted overall score using dynamic weights
            score.overall_score = (
                score.cost_score * weights["cost"] +
                score.timeline_score * weights["timeline"] +
                score.scope_score * weights["scope"] +
                score.risk_score * weights["risk"] +
                score.reputation_score * weights["reputation"]
            )
            # Round to 2 decimal places for consistency
            score.overall_score = round(score.overall_score, 2)
            
            scores.append(score)
            
            # Detect red flags - using both bid analysis and Serper web research data
            # Check for incomplete scope - stricter threshold for better detection
            scope_threshold = 0.75  # Stricter to catch more incomplete/vague scopes
            if score.scope_score < scope_threshold:
                # Determine severity based on how incomplete
                if score.scope_score < 0.5:
                    severity = "critical"
                elif score.scope_score < 0.6:
                    severity = "high"
                else:
                    severity = "medium"
                red_flags.append(RedFlag(
                    type=RedFlagType.INCOMPLETE_SCOPE,
                    severity=severity,
                    evidence=f"Scope score: {score.scope_score:.2f}. {score.reasoning}",
                    affected_bid=score.bid_id,
                ))
            
            # Check for suspiciously low cost - detect based on actual cost vs scope completeness
            # Method 1: High cost_score but low scope_score (LLM detected pattern)
            if (score.cost_score > 0.85 and score.scope_score < 0.75) or \
               (score.cost_score > 0.9 and score.scope_score < 0.8):
                red_flags.append(RedFlag(
                    type=RedFlagType.SUSPICIOUSLY_LOW_COST,
                    severity="medium",
                    evidence=f"Very competitive cost ({score.cost_score:.2f}) but incomplete/vague scope ({score.scope_score:.2f}). May indicate hidden costs or scope gaps.",
                    affected_bid=score.bid_id,
                ))
            
            # Method 2: Detect suspicious pattern based on scope vagueness + cost competitiveness
            # Pattern: Vague/incomplete scope + competitive cost = potential gaming attempt
            scope_text = bid.get("scope", "").strip().lower()
            is_vague_scope = (
                len(scope_text.split()) < 5 or 
                scope_text in ["renovation work", "building construction", "construction", "building"] or
                (len(scope_text.split()) < 10 and score.scope_score < 0.7)
            )
            
            # If scope is vague AND cost is competitive, flag as suspicious
            # This catches cases where the bidder offers good price but vague scope
            if is_vague_scope and score.scope_score < 0.7:
                if score.cost_score > 0.75:  # Competitive cost
                    red_flags.append(RedFlag(
                        type=RedFlagType.SUSPICIOUSLY_LOW_COST,
                        severity="medium",
                        evidence=f"Suspicious pattern detected: Competitive cost (score: {score.cost_score:.2f}) combined with vague/incomplete scope (score: {score.scope_score:.2f}, scope text: '{scope_text[:60]}'). This may indicate hidden costs or scope gaps.",
                        affected_bid=score.bid_id,
                    ))
            
            # Check for vague timeline
            if score.timeline_score < 0.6:
                red_flags.append(RedFlag(
                    type=RedFlagType.VAGUE_TIMELINE,
                    severity="medium",
                    evidence=f"Timeline score: {score.timeline_score:.2f}. Timeline may be unrealistic or vague.",
                    affected_bid=score.bid_id,
                ))
            
            # Detect constraint violations (subcontractor risk, operational disruption, etc.)
            if requirements:
                constraint_violations = detect_constraint_violations(bid, requirements, score.scope_score)
                for violation in constraint_violations:
                    red_flags.append(RedFlag(
                        type=RedFlagType[violation["type"]],
                        severity=violation["severity"],
                        evidence=violation["evidence"],
                        affected_bid=score.bid_id,
                    ))
            
            # Enhanced subcontractor risk detection
            scope_text_lower = bid.get("scope", "").lower()
            if "subcontract" in scope_text_lower or "subcontracted" in scope_text_lower:
                # Check if critical work is subcontracted
                critical_keywords = ["electrical", "power", "hvac", "structural", "foundation"]
                if any(keyword in scope_text_lower for keyword in critical_keywords):
                    # Check if scope score is low (indicates incomplete details)
                    if score.scope_score < 0.75:
                        red_flags.append(RedFlag(
                            type=RedFlagType.SUBCONTRACTOR_RISK,
                            severity="high",
                            evidence=f"Critical work ({', '.join([k for k in critical_keywords if k in scope_text_lower])}) is subcontracted with incomplete scope details (score: {score.scope_score:.2f}). Increases coordination risk and operational disruption potential.",
                            affected_bid=score.bid_id,
                        ))
            
            # ENFORCE: Use Serper web research data for red flags
            if profile:
                # Red flags from web research (Serper)
                if profile.red_flags_found:
                    severity = "critical" if len(profile.red_flags_found) >= 3 else "high"
                    red_flags.append(RedFlag(
                        type=RedFlagType.POOR_REPUTATION,
                        severity=severity,
                        evidence=f"Web research found reputation issues: {', '.join(profile.red_flags_found[:3])}. Sources: {', '.join(profile.credibility_sources[:2]) if profile.credibility_sources else 'N/A'}",
                        affected_bid=score.bid_id,
                    ))
                
                # If reputation score from Serper is very low, flag it
                if profile.reputation_score < 0.6:
                    red_flags.append(RedFlag(
                        type=RedFlagType.POOR_REPUTATION,
                        severity="high",
                        evidence=f"Low reputation score from web research: {profile.reputation_score:.2f}. Recent projects: {len(profile.recent_projects)} found.",
                        affected_bid=score.bid_id,
                    ))
                
                # If no recent projects found, flag as potential risk
                if not profile.recent_projects and profile.reputation_score < 0.7:
                    red_flags.append(RedFlag(
                        type=RedFlagType.REQUIRES_CLARIFICATION,
                        severity="medium",
                        evidence=f"Limited online presence: No recent projects found in web research. Reputation score: {profile.reputation_score:.2f}",
                        affected_bid=score.bid_id,
                    ))
    
    # Sort by overall score
    scores.sort(key=lambda x: x.overall_score, reverse=True)
    
    return {
        **state,
        "scores": scores,
        "red_flags": red_flags,
    }

