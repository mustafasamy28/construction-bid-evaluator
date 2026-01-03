from langgraph.graph import StateGraph, END
from src.state import BidEvalState
from src.nodes.parse import parse_and_enrich
from src.nodes.score import score_and_flag
from src.nodes.critique import critique_and_finalize


def create_graph():
    """Create and compile the bid evaluation graph."""
    workflow = StateGraph(BidEvalState)
    
    workflow.add_node("parse_and_enrich", parse_and_enrich)
    workflow.add_node("score_and_flag", score_and_flag)
    workflow.add_node("critique_and_finalize", critique_and_finalize)
    
    workflow.set_entry_point("parse_and_enrich")
    workflow.add_edge("parse_and_enrich", "score_and_flag")
    workflow.add_edge("score_and_flag", "critique_and_finalize")
    workflow.add_edge("critique_and_finalize", END)
    
    return workflow.compile()

