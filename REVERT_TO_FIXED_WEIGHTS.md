# Reverted to Fixed Weights System

## Change Summary

**Reverted from**: Dynamic weight adjustment based on project priorities  
**Reverted to**: Fixed weights system (original approach)

## Fixed Weights (Restored)

| Dimension | Weight | Percentage |
|-----------|--------|------------|
| **Cost** | 0.25 | **25%** |
| **Timeline** | 0.20 | **20%** |
| **Scope** | 0.25 | **25%** |
| **Risk** | 0.15 | **15%** |
| **Reputation** | 0.15 | **15%** |
| **Total** | 1.00 | **100%** |

## Why Reverted?

The dynamic weight system was causing issues in production:
- ❌ Rejecting all projects
- ❌ Unrealistic weight adjustments
- ❌ Too aggressive weight changes based on keyword detection

## What Was Kept

✅ Enhanced red flag detection (subcontractor, constraint violations)  
✅ Improved scope scoring adjustments  
✅ Constraint violation detection  
✅ Better Serper data enforcement  
✅ All other improvements remain intact

## What Was Removed

❌ Dynamic weight calculation (`calculate_dynamic_weights()` call)  
❌ Automatic weight adjustment based on priorities  
❌ Risk-priority, timeline-critical, cost-de-prioritized weight sets

## Code Changes

**File**: `src/nodes/score.py`

**Before**:
```python
weights = calculate_dynamic_weights(requirements) if requirements else {
    "cost": 0.25,
    "timeline": 0.20,
    "scope": 0.25,
    "risk": 0.15,
    "reputation": 0.15,
}
```

**After**:
```python
weights = {
    "cost": 0.25,
    "timeline": 0.20,
    "scope": 0.25,
    "risk": 0.15,
    "reputation": 0.15,
}
```

## Testing

✅ All tests passing  
✅ Fixed weights sum to 1.0  
✅ Score calculations correct  
✅ No import errors

---

**The system now uses the original fixed-weight approach that was working correctly in production.**

