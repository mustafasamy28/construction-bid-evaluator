"""Utility functions for bid evaluation."""
import logging
from typing import Dict
from src.schemas import ProjectRequirements

logger = logging.getLogger(__name__)


def calculate_dynamic_weights(requirements: ProjectRequirements) -> Dict[str, float]:
    """
    Calculate dynamic weights based on project priorities.
    
    Default weights:
    - Cost: 25%
    - Timeline: 20%
    - Scope: 25%
    - Risk: 15%
    - Reputation: 15%
    
    Adjusts based on priorities mentioned in requirements.
    """
    # Default weights
    weights = {
        "cost": 0.25,
        "timeline": 0.20,
        "scope": 0.25,
        "risk": 0.15,
        "reputation": 0.15,
    }
    
    if not requirements or not requirements.priorities:
        return weights
    
    # Analyze priorities text
    priorities_text = " ".join(requirements.priorities).lower()
    constraints_text = " ".join(requirements.constraints).lower()
    all_text = f"{priorities_text} {constraints_text}".lower()
    
    # Check for risk/operational disruption priority
    risk_keywords = ["risk", "operational disruption", "disruption", "safety", "reliability"]
    risk_priority = any(keyword in all_text for keyword in risk_keywords) and \
                   any(phrase in all_text for phrase in ["higher priority", "more important", "priority over cost"])
    
    # Check for cost de-prioritization
    cost_deprioritized = any(phrase in all_text for phrase in [
        "lower priority than", "less important than", "willing to accept higher cost",
        "cost less important", "cost not primary"
    ])
    
    # Check for timeline criticality
    timeline_critical = any(phrase in all_text for phrase in [
        "timeline critical", "schedule critical", "must complete by", "deadline"
    ])
    
    # Adjust weights based on detected priorities
    if risk_priority:
        # Increase risk weight, decrease cost weight
        weights["risk"] = 0.35  # Increase from 15% to 35%
        weights["scope"] = 0.25  # Keep high (operational disruption factor)
        weights["cost"] = 0.15  # Decrease from 25% to 15%
        weights["timeline"] = 0.15  # Decrease from 20% to 15%
        weights["reputation"] = 0.10  # Decrease from 15% to 10%
        logger.info("Dynamic weights: Risk-priority project detected - Risk: 35%, Cost: 15%")
    
    elif cost_deprioritized:
        # Moderate adjustment
        weights["risk"] = 0.25  # Increase from 15% to 25%
        weights["cost"] = 0.20  # Decrease from 25% to 20%
        weights["scope"] = 0.25  # Keep
        weights["timeline"] = 0.20  # Keep
        weights["reputation"] = 0.10  # Decrease
        logger.info("Dynamic weights: Cost de-prioritized - Risk: 25%, Cost: 20%")
    
    elif timeline_critical:
        # Increase timeline weight
        weights["timeline"] = 0.30  # Increase from 20% to 30%
        weights["cost"] = 0.20  # Decrease
        weights["risk"] = 0.20  # Increase
        weights["scope"] = 0.20  # Decrease
        weights["reputation"] = 0.10  # Decrease
        logger.info("Dynamic weights: Timeline-critical project - Timeline: 30%")
    
    # Normalize to ensure sum = 1.0
    total = sum(weights.values())
    if total != 1.0:
        weights = {k: v / total for k, v in weights.items()}
    
    return weights


def detect_constraint_violations(
    bid: dict,
    requirements: ProjectRequirements,
    scope_score: float
) -> list:
    """
    Detect if bid violates specific project constraints.
    Returns list of constraint violations.
    """
    violations = []
    
    if not requirements:
        return violations
    
    constraints_text = " ".join(requirements.constraints).lower()
    scope_text = bid.get("scope", "").lower()
    
    # Check for operational constraints
    if "occupied" in constraints_text or "operational" in constraints_text:
        # Check for subcontractor risk on critical work
        if "subcontract" in scope_text or "subcontracted" in scope_text:
            if "electrical" in scope_text or "power" in scope_text:
                violations.append({
                    "type": "SUBCONTRACTOR_RISK",
                    "severity": "high",
                    "evidence": "Critical electrical work is subcontracted, increasing operational disruption risk for occupied building"
                })
        
        # Check for phasing/disruption mitigation
        if "phasing" not in scope_text and "staged" not in scope_text and "phase" not in scope_text:
            if "occupied" in constraints_text:
                violations.append({
                    "type": "OPERATIONAL_DISRUPTION_RISK",
                    "severity": "medium",
                    "evidence": "No phasing plan mentioned for occupied building project"
                })
    
    # Check for power shutdown constraints
    if "no power shutdown" in constraints_text or "power shutdown" in constraints_text:
        if "electrical" in scope_text and ("subcontract" in scope_text or "partner" in scope_text):
            violations.append({
                "type": "CONSTRAINT_VIOLATION_RISK",
                "severity": "high",
                "evidence": "Electrical work subcontracted may violate 'no full-day power shutdowns' constraint"
            })
    
    # Check for noise restrictions
    if "noise" in constraints_text and "restricted" in constraints_text:
        if scope_score < 0.7:  # Vague scope
            violations.append({
                "type": "CONSTRAINT_VIOLATION_RISK",
                "severity": "medium",
                "evidence": "Vague scope may not address noise restriction requirements"
            })
    
    return violations

