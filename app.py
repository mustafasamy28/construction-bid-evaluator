import streamlit as st
import json
import asyncio
import nest_asyncio
import logging
from src.graph import create_graph
from src.state import BidEvalState

# Initialize logging
try:
    from src.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback if logging_config not available
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Fix asyncio event loop conflict with Streamlit
nest_asyncio.apply()

st.set_page_config(page_title="Bid Evaluation Agent", layout="wide")

st.title("🏗️ Construction Bid Evaluation Agent")

st.info("📋 **Upload a JSON file** containing both project description and bids. Use files from the `bids/` folder (e.g., `bids_project_1_commercial.json`).")

uploaded_file = st.file_uploader("Upload project and bids (JSON)", type=["json"], help="Select a JSON file from the bids/ folder. Each JSON file contains the project description and all bid information.")

if uploaded_file:
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)
        data = json.load(uploaded_file)
        project = data.get("project", {})
        bids = data.get("bids", [])
        
        if not project.get("description"):
            st.error("❌ Invalid JSON format: Missing 'project.description' field")
            st.json(data)
        elif not bids:
            st.error("❌ Invalid JSON format: Missing or empty 'bids' array")
            st.json(data)
        else:
            st.subheader("Project Description")
            st.write(project.get("description", ""))
            
            st.subheader(f"Bids Received: {len(bids)}")
            for bid in bids:
                with st.expander(f"Bid: {bid.get('contractor_name', 'Unknown')}"):
                    st.json(bid)
            
            st.divider()
            
            if st.button("🚀 Evaluate Bids", type="primary", use_container_width=True):
                with st.spinner("Evaluating bids..."):
                    graph = create_graph()
                    
                    initial_state: BidEvalState = {
                        "project_description": project.get("description", ""),
                        "bids": bids,
                        "requirements": None,
                        "contractor_profiles": [],
                        "scores": [],
                        "red_flags": [],
                        "final_recommendation": None,
                    }
                    
                    result = asyncio.run(graph.ainvoke(initial_state))
                    
                    # Display results
                    st.success("Evaluation Complete!")
                    
                    if result.get("final_recommendation"):
                        rec = result["final_recommendation"]
                        st.header("📊 Final Recommendation")
                        
                        rec_type_colors = {
                            "ACCEPT": "🟢",
                            "REJECT_ALL": "🔴",
                            "REQUIRES_CLARIFICATION": "🟡",
                        }
                        st.markdown(f"### {rec_type_colors.get(rec.recommendation_type.value, '⚪')} {rec.recommendation_type.value}")
                        st.metric("Confidence", f"{rec.confidence:.1%}")
                        st.write("**Rationale:**", rec.rationale)
                        
                        if rec.trade_offs:
                            st.write("**Trade-offs:**")
                            for tradeoff in rec.trade_offs:
                                st.write(f"- {tradeoff}")
                    
                    st.header("📈 Bid Scores")
                    scores = result.get("scores", [])
                    for score in scores:
                        with st.expander(f"{score.contractor_name} - Overall: {score.overall_score:.2f}"):
                            col1, col2, col3, col4, col5 = st.columns(5)
                            col1.metric("Cost", f"{score.cost_score:.2f}")
                            col2.metric("Timeline", f"{score.timeline_score:.2f}")
                            col3.metric("Scope", f"{score.scope_score:.2f}")
                            col4.metric("Risk", f"{score.risk_score:.2f}")
                            col5.metric("Reputation", f"{score.reputation_score:.2f}")
                            st.write("**Reasoning:**", score.reasoning)
                    
                    red_flags = result.get("red_flags", [])
                    if red_flags:
                        st.header("🚩 Red Flags")
                        for flag in red_flags:
                            severity_colors = {
                                "low": "🟡",
                                "medium": "🟠",
                                "high": "🔴",
                                "critical": "⛔",
                            }
                            st.warning(
                                f"{severity_colors.get(flag.severity, '⚪')} **{flag.type.value}** "
                                f"({flag.severity}) - {flag.evidence}"
                            )
                    
                    # LangSmith trace link
                    st.info("💡 Check LangSmith for detailed trace logs")
                
    except json.JSONDecodeError:
        st.error("Invalid JSON file")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)

