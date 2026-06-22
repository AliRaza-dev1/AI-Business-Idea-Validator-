# ROOT CAUSE ANALYSIS: AI Business Idea Validator
## Why All Ideas Produce Identical Generic Reports

**Date**: 2026-06-21  
**Status**: CRITICAL ISSUE IDENTIFIED  
**Severity**: P0 - All analysis broken  

---

## EXECUTIVE SUMMARY

The AI Business Idea Validator is generating identical generic validation reports for every submitted idea because:

1. **OpenAI API Key is a placeholder test key** (`sk-test-key-replace-with-real-key`)
2. **All AI agents fail silently** and return zero scores
3. **Zero scores trigger hardcoded fallback values** instead of real analysis
4. **Results with all zeros are saved to database** and reused for every idea
5. **PDF generation displays the same generic template** for all ideas

**Result**: Market Score = 0, Competition Score = 0, Financial Score = 0, Confidence = 0%, SWOT contains hardcoded generic values.

---

## PART 1: EXACT ROOT CAUSE

### Root Cause #1: Invalid OpenAI API Key

**File**: `backend/.env`  
**Line**: 2  
**Current Value**:
```
OPENAI_API_KEY=sk-test-key-replace-with-real-key
```

**Expected Value**:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Impact**: Every OpenAI API call fails with authentication error.

---

## PART 2: EVIDENCE FROM THE CODEBASE

### Execution Flow Chart

```
User Submits Idea
    ↓
POST /api/v1/ideas/{id}/analyze  [backend/app/api/routes/analysis.py:89-161]
    ↓
analyze_idea() - Request handler checks API key validity
    ↓
✗ FAILS: API key validation detects dummy key
    ↓
✓ Returns 503 Service Unavailable IF not in test mode
    OR
✓ Schedules analyze_idea_background() task
    ↓
analyze_idea_background() - Background execution  [backend/app/api/routes/analysis.py:180-296]
    ↓
orchestrator.run_full_analysis() [backend/app/services/analysis_orchestrator.py:24-243]
    ↓
6 Agent Calls (ALL FAIL):
  1. market_service.analyze_market()         → score=0 ✗
  2. competitive_service.analyze_competition() → score=0 ✗
  3. financial_service.analyze_financials()  → score=0 ✗
  4. risk_service.assess_risks()            → score=0 ✗
  5. feasibility_service.analyze_feasibility() → score=0 ✗
  6. swot_generator.generate_swot()         → empty ✗
    ↓
Orchestrator catches ALL exceptions silently [backend/app/services/analysis_orchestrator.py:53-100]
    ↓
Returns aggregated results with score=0
    ↓
Saved to database AnalysisResult table
    ↓
GET /api/v1/ideas/{id}/report/pdf  [backend/app/api/routes/reports.py:8-54]
    ↓
report_generator.generate_pdf_report()  [backend/app/services/report_generator.py:27-350]
    ↓
Detects score=0 (treated as "legacy" or missing)
    ↓
Triggers hardcoded fallback values:
  - "Legacy conversion" for all scores
  - "Experienced team, clear value prop" for strengths
  - "Limited budget, new market" for weaknesses
  - Generic SWOT and recommendations
    ↓
PDF returned with identical generic data for EVERY idea
```

---

## PART 3: WHERE HARDCODED DEFAULT VALUES ARE INJECTED

### Location #1: Report Generator - Fallback for Missing/Zero Analysis
**File**: `backend/app/services/report_generator.py`  
**Lines**: 99-117  
**Triggered When**: Analysis result is missing or legacy (all zeros)

```python
if not rec_data or "_legacy_text" in rec_data:
    rec_data = {
        "overall_score": analysis_raw.get("overall_score", 0) * 10,
        "overall_confidence": 80,
        "overall_confidence_reason": "Historical record baseline confidence.",
        "executive_summary": "Analysis records updated from legacy database.",
        "score_breakdown": {
            "market_demand": {
                "score": int(analysis_raw.get("market_score", 0)*2.5), 
                "max_score": 25, 
                "reasoning": "Legacy conversion."  # ← HARDCODED
            },
            "competition": {
                "score": int(analysis_raw.get("competitive_score", 0)*2), 
                "max_score": 20, 
                "reasoning": "Legacy conversion."  # ← HARDCODED
            },
            "revenue_potential": {
                "score": int(analysis_raw.get("financial_score", 0)*2), 
                "max_score": 20, 
                "reasoning": "Legacy conversion."  # ← HARDCODED
            },
            "scalability": {
                "score": int(analysis_raw.get("feasibility_score", 0)*1.5), 
                "max_score": 15, 
                "reasoning": "Legacy conversion."  # ← HARDCODED
            },
            "risk_management": {
                "score": int(analysis_raw.get("risk_score", 0)*2), 
                "max_score": 20, 
                "reasoning": "Legacy conversion."  # ← HARDCODED
            }
        },
        "action_plan": [
            {"recommendation": rec, "framework_source": "General Validation", "priority": "medium", "category": "general"}
            for rec in analysis_raw.get("recommendations", [])
        ],
        "next_steps": ["Review converted metrics."],  # ← HARDCODED
        "viability_verdict": "Viable"
    }
```

### Location #2: Report Generator - Fallback for Missing SWOT
**File**: `backend/app/services/report_generator.py`  
**Lines**: 118-126

```python
if not swot_data or "_legacy_text" in swot_data:
    swot_data = {
        "strengths": [{"text": analysis_raw.get("strengths", "N/A"), "framework_source": "SWOT Analysis"}],
        "weaknesses": [{"text": analysis_raw.get("weaknesses", "N/A"), "framework_source": "Startup Failure Patterns"}],
        "opportunities": [{"text": "Market expansion potential.", "framework_source": "Market Research"}],  # ← HARDCODED
        "threats": [{"text": "Competitor copycats.", "framework_source": "Porter Five Forces"}]  # ← HARDCODED
    }
```

### Location #3: Reports Route - Demo Data When Analysis Missing
**File**: `backend/app/api/routes/reports.py`  
**Lines**: 18-43 (PDF report) and 127-143 (JSON report)

```python
if not analysis:
    # Return demo data for now
    analysis_data = {
        "overall_score": 7.8,
        "market_score": 8.5,
        "feasibility_score": 7.8,
        "financial_score": 8.2,
        "risk_score": 6.5,
        "market_analysis": "Strong market potential",
        "feasibility_analysis": "Technically feasible",
        "financial_analysis": "Good financial prospects",
        "risk_analysis": "Moderate risk",
        "competitive_analysis": "Competitive but viable",
        "strengths": "Experienced team, clear value prop",  # ← HARDCODED
        "weaknesses": "Limited budget, new market",         # ← HARDCODED
        "recommendations": []
    }
```

---

## PART 4: WHY ALL AGENTS FAIL SILENTLY

### Agent Execution Failure - OpenAI API Key Invalid

**File**: `backend/app/agents/base_agent.py`  
**Lines**: 1-200

When any agent executes:
```python
async def execute(self, idea_context: str, query_text: str) -> Dict[str, Any]:
    # ... (logs and setup)
    
    # Line 103-109: OpenAI API Call
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[...],
        temperature=settings.openai_temperature,
        max_tokens=settings.openai_max_tokens
    )
```

**What Happens**:
1. `self.client` was initialized with invalid API key: `sk-test-key-replace-with-real-key`
2. OpenAI API rejects the request with authentication error
3. `base_agent.py` raises `RuntimeError` (line 147-149)
4. **BUT** - Orchestrator catches this exception silently (see next section)

### Silent Exception Catching in Orchestrator

**File**: `backend/app/services/analysis_orchestrator.py`  
**Lines**: 53-100

```python
# Step 1: Market Intelligence Agent (via market_service)
try:
    market_result = await self.market_service.analyze_market(idea_context)
    if "_audit_log" in market_result:
        audit_trail.append(market_result["_audit_log"])
except Exception as e:
    logger.error(f"Market analysis failed: {str(e)}")  # ← Only logs, doesn't re-raise
    market_result = {
        "score": 0,                                    # ← Returns zero
        "analysis": f"Market analysis failed: {str(e)[:100]}",
        "error": True
    }

# Step 2: Competition Analysis Agent
try:
    competition_result = await self.competitive_service.analyze_competition(idea_context)
    # ...
except Exception as e:
    logger.error(f"Competition analysis failed: {str(e)}")
    competition_result = {
        "score": 0,  # ← Returns zero
        "analysis": f"Competition analysis failed: {str(e)[:100]}",
        "error": True
    }

# Steps 3-5: Same pattern for Financial, Risk, Feasibility
# ALL catch exceptions and return score=0
```

**Result**: Even though agents fail, orchestrator continues and builds a complete report with all scores = 0.

### RAG Pipeline Never Gets Initialized

**File**: `backend/app/services/knowledge_base.py`  
**Lines**: 47-54

```python
def _get_embedding(self, text: str) -> List[float]:
    """Call OpenAI API to generate high-dimensional text embeddings"""
    if not self.openai_key:
        raise RuntimeError("FATAL: OpenAI API key not configured...")
    
    if "sk-test" in self.openai_key or "replace-with-real-key" in self.openai_key:
        raise RuntimeError(
            "FATAL: OpenAI API key is a placeholder (sk-test or 'replace-with-real-key'). "
            "Please update with a real API key from https://platform.openai.com/api-keys"
        )
```

**What Happens**:
1. RAG service checks for placeholder key (correct check)
2. Raises error when trying to generate embeddings
3. **BUT** - This is not called if vectors are already cached
4. **Result**: No embeddings generated → no retrieved context → agents produce generic responses

---

## PART 5: DATABASE PERSISTENCE ISSUE

### Scores Are Saved as Zero to Database

**File**: `backend/app/models/models.py`  
**Lines**: 46-72

```python
class AnalysisResult(Base):
    """Analysis results model"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False, unique=True, index=True)
    market_score = Column(Float, default=0.0)          # ← Defaults to 0
    feasibility_score = Column(Float, default=0.0)    # ← Defaults to 0
    financial_score = Column(Float, default=0.0)      # ← Defaults to 0
    risk_score = Column(Float, default=0.0)            # ← Defaults to 0
    overall_score = Column(Float, default=0.0)        # ← Defaults to 0
```

**What Happens**:
1. Orchestrator returns `{"score": 0, ...}` for each failed agent
2. Analysis route saves scores of 0 to database (lines in `analysis.py`)
3. When report is generated, it finds all zero scores
4. Treats this as "legacy" or missing data
5. Injects hardcoded fallback values

---

## PART 6: COMPLETE FILE ANALYSIS

### File 1: Core Configuration
**File**: `backend/app/core/config.py`

```python
class Settings(BaseSettings):
    # ...
    openai_api_key: str = ""              # Loaded from .env
    openai_model: str = "gpt-4"
    # ...
```

**Issue**: Loads placeholder key from .env file and doesn't validate it.

### File 2: Agent Initialization
**File**: `backend/app/agents/base_agent.py`

```python
def __init__(self, agent_name: str, prompt_filename: str):
    self.agent_name = agent_name
    self.prompt_filename = prompt_filename
    self.client = OpenAI(api_key=settings.openai_api_key)  # ← Uses invalid key
    self.model = settings.openai_model
```

**Issue**: Creates OpenAI client with placeholder key without validation.

### File 3: Orchestrator Error Handling
**File**: `backend/app/services/analysis_orchestrator.py`

All 6 agents wrapped in try/except blocks that catch and continue.

**Issue**: Errors are logged but not re-raised, allowing execution to continue with zero scores.

### File 4: Report Generator Fallbacks
**File**: `backend/app/services/report_generator.py`

Two fallback conditions (lines 99-117 and 118-126) that inject hardcoded values when data is empty.

**Issue**: Fallbacks are triggered for EVERY analysis due to zero scores.

### File 5: Routes with Demo Data
**File**: `backend/app/api/routes/reports.py`

Lines 18-43 and 127-143 show demo data being returned when analysis is missing.

**Issue**: Demo data has identical hardcoded SWOT values.

---

## PART 7: THE IDENTICAL REPORT PROBLEM

### Why Every Idea Gets the Same Report

1. **All ideas fail at the same point**: OpenAI API key validation
2. **All agents return score=0**: Same response for every idea
3. **Same zero scores saved to DB**: Identical database records
4. **Same fallback code path triggered**: Same hardcoded values used
5. **Same PDF generated**: Identical content for all ideas

### Example: Three Different Ideas, Identical Reports

**Idea 1**: "AI Resume Analyzer"  
**Idea 2**: "Grocery Delivery Platform"  
**Idea 3**: "Educational SaaS"

**All produce**:
- Market Score: 0
- Competition Score: 0
- Financial Score: 0
- Risk Score: 0
- Confidence: 0%
- Reasoning: "Legacy conversion"
- SWOT Strengths: "Experienced team, clear value prop"
- SWOT Weaknesses: "Limited budget, new market"
- SWOT Opportunities: "Market expansion potential"
- SWOT Threats: "Competitor copycats"

---

## PART 8: DETAILED FIXES

### FIX #1: Replace Invalid API Key (CRITICAL)

**File**: `backend/.env`

**Current**:
```
OPENAI_API_KEY=sk-test-key-replace-with-real-key
```

**Change To**:
```
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**How to Get Real Key**:
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy and paste into .env file
4. **NEVER commit real keys to version control**

### FIX #2: Add Fail-Fast Validation in Route

**File**: `backend/app/api/routes/analysis.py`

**Current Code (lines 110-121)**:
```python
# Check if OpenAI API key is configured with a real key and log warning if not
import sys
is_testing = "pytest" in sys.modules
is_dummy_key = (
    not settings.openai_api_key or
    "replace-with-real-key" in settings.openai_api_key or
    "your_openai_api_key" in settings.openai_api_key or
    settings.openai_api_key.strip() == ""
)
if is_dummy_key and not is_testing:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="OpenAI API key is not configured..."
    )
```

**Issue**: The `and not is_testing` condition allows execution during non-production.

**Fix**:
```python
# Check if OpenAI API key is configured with a real key - ALWAYS
is_dummy_key = (
    not settings.openai_api_key or
    "replace-with-real-key" in settings.openai_api_key or
    "sk-test" in settings.openai_api_key or
    "your_openai_api_key" in settings.openai_api_key or
    settings.openai_api_key.strip() == ""
)
if is_dummy_key:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="OpenAI API key is not configured. Analysis cannot be performed. "
               "Set OPENAI_API_KEY in .env with a real key from platform.openai.com"
    )
```

### FIX #3: Don't Silently Catch Agent Failures in Orchestrator

**File**: `backend/app/services/analysis_orchestrator.py`

**Current Code (lines 53-58)**:
```python
try:
    market_result = await self.market_service.analyze_market(idea_context)
    if "_audit_log" in market_result:
        audit_trail.append(market_result["_audit_log"])
except Exception as e:
    logger.error(f"Market analysis failed: {str(e)}")
    market_result = {
        "score": 0,
        "analysis": f"Market analysis failed: {str(e)[:100]}",
        "error": True
    }
```

**Issue**: Exception is caught and execution continues, leading to zero-score results.

**Fix - Approach A (Strict - Recommended)**:
```python
try:
    market_result = await self.market_service.analyze_market(idea_context)
    if "_audit_log" in market_result:
        audit_trail.append(market_result["_audit_log"])
except Exception as e:
    logger.error(f"Market analysis failed: {str(e)}")
    raise RuntimeError(
        f"Market analysis failed: {str(e)}. Analysis cannot complete. "
        f"Please verify OpenAI API key is valid and try again."
    ) from e
```

**Fix - Approach B (Graceful - Alternative)**:
```python
try:
    market_result = await self.market_service.analyze_market(idea_context)
    if "_audit_log" in market_result:
        audit_trail.append(market_result["_audit_log"])
except Exception as e:
    logger.error(f"Market analysis failed: {str(e)}")
    # Only retry with demo if explicitly requested, not silent
    raise RuntimeError(
        f"Market analysis failed and demo mode is disabled. "
        f"Error: {str(e)}"
    ) from e
```

**Apply same fix to all 6 agents**: Competition, Financial, Risk, Feasibility, SWOT, BMC

### FIX #4: Validate RAG Initialization Explicitly

**File**: `backend/app/agents/base_agent.py`

**Current Code (lines 54-65)**:
```python
# 1. RAG Search (Lazy initialized)
logger.info("Step 1: RAG Retrieval Starting...")
from app.services.knowledge_base import get_rag_service
rag_svc = get_rag_service()
search_results = rag_svc.search_similarity(query_text, top_k=2)
if search_results:
    # Use results
else:
    logger.warning("RAG: No matching frameworks retrieved - using general business principles")
    retrieved_content = "No matching frameworks retrieved..."
```

**Issue**: Silently continues even if RAG retrieval fails.

**Fix**:
```python
# 1. RAG Search (Lazy initialized) - MUST SUCCEED
logger.info("Step 1: RAG Retrieval Starting...")
from app.services.knowledge_base import get_rag_service
try:
    rag_svc = get_rag_service()
    search_results = rag_svc.search_similarity(query_text, top_k=2)
    if search_results:
        retrieved_sources = list(set(res["framework_name"] for res in search_results))
        retrieved_content = "\n\n".join(...)
    else:
        logger.warning("RAG: No matching frameworks retrieved")
        retrieved_content = "No matching frameworks retrieved..."
except Exception as e:
    logger.error(f"RAG initialization failed: {str(e)}")
    raise RuntimeError(
        f"Knowledge base retrieval failed: {str(e)}. "
        f"Ensure OpenAI API key is valid for embedding generation."
    ) from e
```

### FIX #5: Remove or Modify Fallback Logic in Report Generator

**File**: `backend/app/services/report_generator.py`

**Current Code (lines 99-117)**:
```python
# If legacy data parsed:
if not rec_data or "_legacy_text" in rec_data:
    rec_data = {
        # Hardcoded fallback values
    }
```

**Option A (Strict - Recommended)**:
```python
# If analysis data is missing, FAIL and inform user
if not rec_data or "_legacy_text" in rec_data:
    raise ValueError(
        "Analysis recommendation data is missing or invalid. "
        "The idea analysis appears incomplete. Please re-run analysis."
    )
```

**Option B (Enhanced - Better UX)**:
```python
# If analysis data is missing, return structured error response
if not rec_data or "_legacy_text" in rec_data:
    return {
        "error": True,
        "status": "incomplete",
        "message": "Analysis data is incomplete. This may indicate the analysis failed. "
                   "Please re-run analysis for complete results.",
        "pdf": None  # Return no PDF if analysis is incomplete
    }
```

### FIX #6: Add Logging to Track Analysis Pipeline

**File**: `backend/app/api/routes/analysis.py`

Add detailed logging in `analyze_idea_background()`:

```python
async def analyze_idea_background(idea_id: int):
    """Background task to perform sequential agent analysis"""
    db_session = SessionLocal()
    start_time = time.time()
    
    logger.info(f"[ANALYSIS START] Idea ID: {idea_id}")
    
    try:
        idea = db_session.query(Idea).filter(Idea.id == idea_id).first()
        if not idea:
            logger.error(f"[ANALYSIS ERROR] Idea {idea_id} not found")
            return
        
        logger.info(f"[ANALYSIS INPUT] Title: {idea.title}")
        logger.info(f"[ANALYSIS INPUT] Description: {idea.description[:100]}...")
        logger.info(f"[ANALYSIS INPUT] Problem: {idea.problem_statement[:100]}...")
        
        # Call orchestrator
        logger.info(f"[ORCHESTRATOR START]")
        analysis_result = await analysis_orchestrator.run_full_analysis(...)
        logger.info(f"[ORCHESTRATOR END]")
        
        # Log scores
        logger.info(f"[SCORES] Market: {analysis_result['scores']['market_score']}")
        logger.info(f"[SCORES] Financial: {analysis_result['scores']['financial_score']}")
        logger.info(f"[SCORES] Risk: {analysis_result['scores']['risk_score']}")
        logger.info(f"[SCORES] Overall: {analysis_result['scores']['overall_score']}")
        
        # Check for zero scores
        if analysis_result['scores']['overall_score'] == 0:
            logger.warning(f"[WARNING] Overall score is 0 - analysis may have failed")
        
        # Save to database
        logger.info(f"[DB SAVE START]")
        new_analysis = AnalysisResult(...)
        db_session.add(new_analysis)
        db_session.flush()
        logger.info(f"[DB SAVE] Analysis ID: {new_analysis.id}")
        
        # ...rest of function
        logger.info(f"[ANALYSIS SUCCESS] Duration: {time.time() - start_time:.2f}s")
        
    except Exception as e:
        logger.error(f"[ANALYSIS FAILED] {str(e)}")
        logger.error(f"[ANALYSIS FAILED] Traceback: {traceback.format_exc()}")
        # ...error handling
```

---

## PART 9: VERIFICATION STEPS

### After Applying Fixes

1. **Verify API Key is Valid**:
   ```bash
   # Test API key manually
   curl -X POST https://api.openai.com/v1/chat/completions \
     -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "gpt-4", "messages": [{"role": "user", "content": "test"}]}'
   ```

2. **Check Backend Logs for Errors**:
   ```bash
   # Look for "AGENT EXECUTION" logs
   # Should see: "AGENT EXECUTION SUCCESSFUL" (not "FAILED")
   # Should see scores > 0 (not 0)
   ```

3. **Test Analysis Endpoint**:
   ```bash
   # Submit new idea and check scores
   POST /api/v1/ideas/{idea_id}/analyze
   
   # Wait for analysis to complete
   GET /api/v1/ideas/{idea_id} 
   
   # Verify scores are NOT all zeros
   ```

4. **Inspect Database Records**:
   ```sql
   SELECT overall_score, market_score, financial_score, risk_score 
   FROM analysis_results 
   WHERE overall_score > 0;
   
   -- Should return non-zero scores after fix
   ```

5. **Generate PDF and Verify**:
   ```bash
   GET /api/v1/ideas/{idea_id}/report/pdf
   
   # PDF should contain actual analysis, not "Legacy conversion" messages
   ```

---

## PART 10: SUMMARY TABLE

| Issue | Location | Root Cause | Impact | Fix |
|-------|----------|-----------|--------|-----|
| Invalid API Key | `.env` line 2 | Placeholder test key | All API calls fail | Replace with real key |
| Silent Error Catching | `analysis_orchestrator.py` lines 53-100 | try/except returns score=0 | Zero scores saved to DB | Re-raise exceptions |
| No RAG Validation | `base_agent.py` lines 54-65 | Continues on RAG failure | No context for agents | Fail-fast on RAG errors |
| Hardcoded Fallbacks | `report_generator.py` lines 99-126 | Triggered by zero scores | Generic reports | Remove or replace with error |
| Demo Data in Routes | `reports.py` lines 18-43, 127-143 | Returns same data for missing analysis | Identical SWOT values | Fail or mark as incomplete |
| No Error Visibility | Various log points | Errors logged but not exposed | Users don't see what failed | Add structured error responses |

---

## PART 11: RECOMMENDED IMPLEMENTATION ORDER

### Phase 1 (Immediate - 15 minutes)
1. [ ] Replace API key in `.env` with real OpenAI key
2. [ ] Restart backend service
3. [ ] Test single idea analysis

### Phase 2 (Short-term - 1 hour)
4. [ ] Apply Fix #2 (fail-fast API key validation in route)
5. [ ] Apply Fix #3 (don't catch exceptions in orchestrator)
6. [ ] Test error handling with invalid key
7. [ ] Deploy and verify

### Phase 3 (Medium-term - 2 hours)
8. [ ] Apply Fix #4 (RAG validation)
9. [ ] Apply Fix #5 (remove fallback logic)
10. [ ] Apply Fix #6 (add detailed logging)
11. [ ] Test end-to-end
12. [ ] Deploy

### Phase 4 (Optional - 1 hour)
13. [ ] Add monitoring alerts for agent failures
14. [ ] Add dashboard indicators for analysis quality
15. [ ] Document deployment requirements

---

## CONCLUSION

The AI Business Idea Validator generates identical generic reports because the OpenAI API key in `.env` is a placeholder test key. When agents fail due to invalid authentication, the orchestrator catches exceptions silently and returns zero scores. The report generator then treats zero scores as "legacy" data and injects hardcoded fallback values, resulting in identical generic reports for every submitted idea.

**The fix is simple**: 
1. Replace the API key with a real key from OpenAI
2. Remove silent error catching in the orchestrator
3. Add fail-fast validation throughout the pipeline

After these fixes, each idea will produce a unique analysis based on actual AI evaluation.
