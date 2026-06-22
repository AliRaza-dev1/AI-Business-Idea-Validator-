# SYSTEM FAILURE DIAGNOSTIC REPORT
**Date:** June 21, 2026  
**Status:** CRITICAL - APPLICATION CANNOT START

---

## ROOT CAUSE #1: AGGRESSIVE API KEY VALIDATION BLOCKS APP STARTUP

**File:** `backend/app/main.py` (lines 14-33)

**Problem:**
```python
if not settings.openai_api_key or \
   "replace-with-real-key" in settings.openai_api_key or \
   "sk-test" in settings.openai_api_key or \
   settings.openai_api_key.strip() == "":
    sys.exit(1)  # ← KILLS APP IMMEDIATELY
```

**Status:** `.env` contains `OPENAI_API_KEY=sk-test-key-replace-with-real-key`

**Impact:**
- Application calls `sys.exit(1)` on startup
- Backend never starts
- All endpoints unavailable (dashboard hangs, login fails, analysis fails)
- Frontend gets connection refused errors

**Severity:** CRITICAL - Blocks entire application

**Fix Required:** Change validation from `sys.exit(1)` to warning log only

---

## ROOT CAUSE #2: FALLBACK RESPONSE REMOVAL BREAKS DEV/TEST MODE

**Files:** All agent classes (market_agent.py, risk_agent.py, etc.)

**Problem:**
```python
def get_fallback_response(self, retrieved_sources):
    raise NotImplementedError(
        "Fallback responses are not supported..."
    )
```

**Impact:**
- If any agent fails (due to invalid key or API error), it raises exception
- Orchestrator has no error handler for these exceptions
- Analysis request crashes instead of gracefully failing

**Severity:** HIGH - Breaks error handling for legitimate API failures

**Fix Required:** Add proper exception handling in orchestrator

---

## ROOT CAUSE #3: RAG SERVICE INITIALIZATION MIGHT FAIL

**File:** `backend/app/services/knowledge_base.py` (lines 30-48)

**Problem:**
- RAG service is instantiated at module load time
- If API key is invalid, _get_embedding() throws exception
- This happens during import, not at request time

**Code Path:**
1. main.py imported
2. analysis.py imported (from routers)
3. analysis_orchestrator imported from analysis.py
4. AnalysisOrchestrator.__init__() creates MarketAnalysisService
5. MarketAnalysisService creates MarketAgent
6. MarketAgent inherits from BaseAgent
7. BaseAgent imports rag_service (knowledge_base.py)
8. RAGService is instantiated during module load
9. RAGService._init_db() runs
10. If anything fails, app startup fails

**Severity:** MEDIUM - Module initialization failure

---

## ROOT CAUSE #4: ORCHESTRATOR INSTANTIATION FAILS

**File:** `backend/app/services/analysis_orchestrator.py` (line 211)

```python
# Global instance created at module load time
analysis_orchestrator = AnalysisOrchestrator()
```

**Problem:**
- Created during module import, not lazily
- If any service initialization fails, entire app fails to start
- No try/except around initialization

**Severity:** MEDIUM - Import-time failure

---

## SYSTEM FAILURE CHAIN

```
1. Application startup
   ↓
2. main.py loads
   ├─ API key validation (line 14-33)
   │  └─ ISSUE: sys.exit(1) if key is placeholder → APP DIES
   │
3. If that passes, routers imported
   ├─ analysis.py imported
   │  └─ Imports analysis_orchestrator (causes global instantiation)
   │     └─ AnalysisOrchestrator.__init__() runs
   │        ├─ Instantiates MarketAnalysisService
   │        ├─ Instantiates FinancialAnalysisService
   │        ├─ Instantiates RiskAssessmentService
   │        ├─ Instantiates CompetitiveAnalysisService
   │        ├─ Instantiates FeasibilityAnalysisService
   │        ├─ Instantiates SWOTGenerator
   │        ├─ Instantiates BMCGenerator
   │        └─ Instantiates RecommendationAgent
   │           ↓
   │        All agents import BaseAgent
   │        ├─ BaseAgent imports RAGService
   │        │  ├─ RAGService.__init__()
   │        │  └─ RAGService._init_db() attempts SQLite init
   │        │     (might fail if DB is locked or corrupted)
   │        └─ If any of this fails → ImportError → App won't start
   │
4. If all imports succeed, FastAPI app initialized
   ├─ Route handlers registered
   ├─ Middleware applied
   └─ Ready to accept requests
```

**Current Status:** Stuck at step 2 (API key validation)

---

## FAILURE SYMPTOMS EXPLAINED

### Symptom 1: "Submitting a business idea does not return analysis results"
**Cause:** Backend not running (app died on startup due to API key validation)
**Evidence:** Frontend tries to connect to http://localhost:8000 → connection refused

### Symptom 2: "Dashboard remains in loading state indefinitely"
**Cause:** Dashboard tries to fetch `/api/v1/dashboard/stats` → backend connection refused → frontend waits forever
**Evidence:** Network tab shows request hanging/failing

### Symptom 3: "Creating a new account fails"
**Cause:** Backend not running → can't reach `/api/v1/auth/register` endpoint
**Evidence:** POST request to auth endpoint gets connection refused

---

## REQUIRED FIXES

### FIX #1: Change API Key Validation to Warning (Not Fatal)

**File:** `backend/app/main.py` (lines 14-33)

**Status:** URGENT - Blocks app startup

**Change:** Replace `sys.exit(1)` with warning log

```python
# BEFORE: (Blocks startup)
if not settings.openai_api_key or "replace-with-real-key" in settings.openai_api_key:
    logger.critical("...")
    sys.exit(1)

# AFTER: (Allow startup, warn user)
if not settings.openai_api_key or "replace-with-real-key" in settings.openai_api_key:
    logger.warning("...")
    # Allow app to start, but API calls will fail with helpful error
```

---

### FIX #2: Make RAG Service Graceful

**File:** `backend/app/services/knowledge_base.py`

**Status:** HIGH - Module import safety

**Change:** Wrap initialization in try/except

```python
# In _init_db():
try:
    conn = sqlite3.connect(DB_PATH)
    cursor.execute(...)
except Exception as e:
    logger.warning(f"RAG database init failed: {e}")
    # Don't fail startup, will try again on use
```

---

### FIX #3: Add Exception Handling in Orchestrator

**File:** `backend/app/services/analysis_orchestrator.py`

**Status:** HIGH - Error handling

**Change:** Wrap service initialization and add try/except in run_full_analysis

```python
try:
    market_result = await self.market_service.analyze_market(idea_context)
except Exception as e:
    logger.error(f"Market analysis failed: {e}")
    market_result = {"error": str(e), "score": 0}
    # Continue with other analyses instead of crashing
```

---

### FIX #4: Add Proper Error Response

**File:** `backend/app/api/routes/analysis.py`

**Status:** MEDIUM - Error messages

**Change:** Catch orchestrator failures and return helpful error

```python
try:
    analysis_result = await analysis_orchestrator.run_full_analysis(...)
except RuntimeError as e:
    if "OpenAI API key" in str(e):
        return {
            "error": "OpenAI API key not configured",
            "detail": "Analysis requires valid OpenAI API key in .env file"
        }
    raise
```

---

## IMMEDIATE ACTION REQUIRED

### Option A: Use Valid OpenAI API Key (RECOMMENDED)
1. Get API key from https://platform.openai.com/api-keys
2. Update `backend/.env`:
   ```
   OPENAI_API_KEY=sk-YOUR_REAL_KEY_HERE
   ```
3. Restart backend

### Option B: Temporarily Disable Validation (DEVELOPMENT ONLY)
1. Modify API key validation in main.py to warning only
2. System will start but API calls will fail
3. Useful for testing non-AI features

---

## VERIFICATION CHECKLIST

- [ ] Backend starts without fatal error
- [ ] `curl http://localhost:8000/health` returns 200
- [ ] Can submit a business idea
- [ ] Dashboard loads (shows stats)
- [ ] Can create account (if implemented)
- [ ] Analysis request doesn't hang indefinitely

