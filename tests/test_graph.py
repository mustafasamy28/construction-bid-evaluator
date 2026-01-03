"""Test runner for bid evaluation graph."""
import pytest
import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.graph import create_graph
from src.state import BidEvalState

# Get the test cases directory
TEST_CASES_DIR = Path(__file__).parent / "cases"


def load_test_case(filename: str) -> dict:
    """Load a test case JSON file."""
    filepath = TEST_CASES_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Test case not found: {filepath}")
    
    with open(filepath, 'r') as f:
        return json.load(f)


async def run_evaluation(test_case: dict) -> dict:
    """Run the evaluation graph on a test case."""
    graph = create_graph()
    
    initial_state: BidEvalState = {
        "project_description": test_case["project"]["description"],
        "bids": test_case["bids"],
        "requirements": None,
        "contractor_profiles": [],
        "scores": [],
        "red_flags": [],
        "final_recommendation": None,
    }
    
    result = await graph.ainvoke(initial_state)
    return result


def test_clear_winner():
    """Test case: One bid clearly superior."""
    test_case = load_test_case("clear_winner.json")
    result = asyncio.run(run_evaluation(test_case))
    
    # Assertions
    assert result.get("final_recommendation") is not None
    rec = result["final_recommendation"]
    
    # Check expected recommendation type
    expected = test_case.get("expected_recommendation", {})
    if expected.get("recommendation_type"):
        assert rec.recommendation_type.value == expected["recommendation_type"]
    
    # Check confidence threshold
    if "confidence" in expected:
        confidence_threshold = float(expected["confidence"].replace(">=", "").replace(" ", ""))
        assert rec.confidence >= confidence_threshold, f"Confidence {rec.confidence} below threshold {confidence_threshold}"
    
    # Check top bid
    if "top_bid" in expected:
        assert rec.ranked_bids[0] == expected["top_bid"]
    
    # Check expected flags
    expected_flags = test_case.get("expected_flags", [])
    if expected_flags:
        flag_types = [f.type.value for f in result.get("red_flags", [])]
        for expected_flag in expected_flags:
            assert expected_flag["type"] in flag_types, f"Expected flag type {expected_flag['type']} not found"


def test_all_bids_bad():
    """Test case: All bids have critical flaws."""
    test_case = load_test_case("all_bids_bad.json")
    result = asyncio.run(run_evaluation(test_case))
    
    rec = result.get("final_recommendation")
    assert rec is not None
    assert rec.recommendation_type.value == "REJECT_ALL"


def test_gaming_attempt():
    """Test case: Lowball cost + vague scope."""
    test_case = load_test_case("gaming_attempt.json")
    result = asyncio.run(run_evaluation(test_case))
    
    rec = result.get("final_recommendation")
    assert rec is not None
    
    # Should require clarification or reject
    assert rec.recommendation_type.value in ["REQUIRES_CLARIFICATION", "REJECT_ALL"]
    
    # Check for expected flags
    expected_flags = test_case.get("expected_flags", [])
    flag_types = [f.type.value for f in result.get("red_flags", [])]
    for expected_flag in expected_flags:
        assert expected_flag["type"] in flag_types


def test_incomplete_bid():
    """Test case: Missing mandatory scope."""
    test_case = load_test_case("incomplete_bid.json")
    result = asyncio.run(run_evaluation(test_case))
    
    rec = result.get("final_recommendation")
    assert rec is not None
    
    # Should flag incomplete scope but not necessarily reject
    red_flags = result.get("red_flags", [])
    incomplete_flags = [f for f in red_flags if f.type.value == "INCOMPLETE_SCOPE"]
    assert len(incomplete_flags) > 0, "Expected INCOMPLETE_SCOPE flag"


def test_close_call():
    """Test case: Two bids within 5% score."""
    test_case = load_test_case("close_call.json")
    result = asyncio.run(run_evaluation(test_case))
    
    rec = result.get("final_recommendation")
    assert rec is not None
    
    # Should have multiple bids recommended or trade-offs explained
    scores = result.get("scores", [])
    if len(scores) >= 2:
        score_diff = scores[0].overall_score - scores[1].overall_score
        if score_diff < 0.05:
            # Close scores should have trade-offs
            assert len(rec.trade_offs) > 0, "Close scores should have trade-offs explained"


def test_input_validation():
    """Test that input validation works."""
    graph = create_graph()
    
    # Test missing project description
    with pytest.raises(ValueError, match="project_description"):
        asyncio.run(graph.ainvoke({
            "project_description": "",
            "bids": [],
            "requirements": None,
            "contractor_profiles": [],
            "scores": [],
            "red_flags": [],
            "final_recommendation": None,
        }))
    
    # Test missing bids
    with pytest.raises(ValueError, match="bids"):
        asyncio.run(graph.ainvoke({
            "project_description": "Test project",
            "bids": [],
            "requirements": None,
            "contractor_profiles": [],
            "scores": [],
            "red_flags": [],
            "final_recommendation": None,
        }))


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

