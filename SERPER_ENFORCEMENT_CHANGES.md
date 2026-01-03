# Serper Data Enforcement - Changes Made

## Problem Identified

The Score and Flag node was **passing** Serper data to the LLM but **not enforcing** its use. The LLM could ignore the web research data and score bids based only on bid information.

## Changes Made

### 1. **Enhanced LLM Prompt** ✅
**File:** `src/nodes/score.py`

- Added explicit instructions to use contractor profile data from web research
- Required LLM to reference credibility_sources in reasoning
- Mandated that reputation_score must align with Serper's reputation_score
- Instructed to use recent_projects for timeline and risk assessment
- Required factoring in red_flags_found for risk scoring

### 2. **Improved Profile Data Formatting** ✅
**File:** `src/nodes/score.py` (lines 45-58)

Changed from passing raw JSON to a structured format that clearly labels:
- `reputation_score_from_web_research` - explicitly labeled as from Serper
- `recent_projects_found` - projects discovered via web search
- `red_flags_found_online` - reputation issues found online
- `credibility_sources` - URLs of sources
- Added note that data is from Serper API (last 12 months)

### 3. **Enforced Reputation Score Usage** ✅
**File:** `src/nodes/score.py` (lines 72-77)

**Before:** LLM could assign any reputation_score
**After:** Reputation score is **blended** (70% Serper, 30% LLM) to ensure Serper data dominates:
```python
score.reputation_score = (serper_reputation * 0.7) + (llm_reputation * 0.3)
```

### 4. **Automatic Score Adjustments Based on Serper Data** ✅
**File:** `src/nodes/score.py` (lines 79-93)

#### Risk Score Adjustments:
- **Red flags found:** Reduces risk_score by up to 0.3 points
- **Recent projects found:** Increases risk_score (reduces risk) by up to 0.15 points
- **No projects + low reputation:** Further reduces risk_score by 0.1 points

#### Timeline Score Adjustments:
- **Recent projects found:** Increases timeline_score by up to 0.15 points (more confidence in delivery)

### 5. **Enhanced Red Flag Detection Using Serper Data** ✅
**File:** `src/nodes/score.py` (lines 123-151)

Added three new red flag detection rules based on Serper data:

1. **Reputation Issues from Web Research:**
   - If `red_flags_found` contains items → Creates POOR_REPUTATION flag
   - Severity: "critical" if 3+ flags, "high" otherwise
   - Includes source URLs in evidence

2. **Low Reputation Score:**
   - If Serper reputation_score < 0.6 → Creates POOR_REPUTATION flag
   - Includes count of recent projects found

3. **Limited Online Presence:**
   - If no recent projects AND reputation < 0.7 → Creates REQUIRES_CLARIFICATION flag
   - Indicates contractor may be new or have limited track record

## How Serper Data is Now Used

| Serper Data Field | How It's Used |
|------------------|---------------|
| `reputation_score` | **70% weight** in final reputation_score calculation |
| `recent_projects` | Boosts timeline_score (+0.15 max) and risk_score (+0.075 max) |
| `red_flags_found` | Reduces risk_score (-0.3 max) and creates red flags |
| `credibility_sources` | Referenced in red flag evidence and LLM reasoning |

## Verification

To verify Serper data is being used:

1. **Check reasoning field:** LLM should mention "web research", "Serper", or "online sources"
2. **Check reputation_score:** Should closely match Serper's reputation_score (within 30%)
3. **Check red flags:** Should include flags from `red_flags_found` if any exist
4. **Check score adjustments:** Timeline and risk scores should reflect recent projects

## Example Flow

```
1. Parse node → Serper API → Contractor Profile:
   {
     reputation_score: 0.65,
     recent_projects: ["Project A", "Project B"],
     red_flags_found: ["Lawsuit in 2024"],
     credibility_sources: ["news.com/article"]
   }

2. Score node receives profile → LLM scores bid

3. Score node ENFORCES Serper data:
   - reputation_score = (0.65 * 0.7) + (LLM_score * 0.3)
   - risk_score reduced by 0.1 (red flag found)
   - timeline_score increased by 0.06 (2 projects found)
   - Red flag created: "Web research found reputation issues: Lawsuit in 2024"

4. Final scores reflect Serper data usage
```

## Impact

✅ **Before:** Serper data was optional - LLM could ignore it
✅ **After:** Serper data is **mandatory** - scores are adjusted programmatically to ensure usage

The system now **guarantees** that web research data influences the scoring, not just suggests it.

