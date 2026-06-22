from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.db.database import get_db, SessionLocal
from app.models.models import Idea, AnalysisResult, Recommendation
from app.schemas.schemas import AnalysisResultResponse, ReportResponse
from app.services.analysis_orchestrator import analysis_orchestrator
from app.utils.security import sanitize_input_text, check_prompt_injection, validate_payload_sizes
from app.monitoring.monitoring_service import monitoring_service
from app.core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.get("/compare", tags=["Analysis"])
async def compare_analyses(idea_a: int, idea_b: int, db: Session = Depends(get_db)):
    """Compare Idea A vs Idea B and highlight changes, risks, and opportunities"""
    res_a = db.query(AnalysisResult).filter(AnalysisResult.idea_id == idea_a).first()
    res_b = db.query(AnalysisResult).filter(AnalysisResult.idea_id == idea_b).first()
    
    if not res_a or not res_b:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both analyses not found"
        )
        
    idea_obj_a = db.query(Idea).filter(Idea.id == idea_a).first()
    idea_obj_b = db.query(Idea).filter(Idea.id == idea_b).first()
    
    # Safely load JSON data
    try:
        payload_a = json.loads(res_a.weaknesses) if res_a.weaknesses.startswith("{") else {}
        payload_b = json.loads(res_b.weaknesses) if res_b.weaknesses.startswith("{") else {}
    except Exception:
        payload_a = {}
        payload_b = {}
        
    score_a = payload_a.get("overall_score", res_a.overall_score)
    score_b = payload_b.get("overall_score", res_b.overall_score)
    
    # Extract SWOT for opportunities & risks comparison
    try:
        swot_a = json.loads(res_a.strengths) if res_a.strengths.startswith("{") else {}
        swot_b = json.loads(res_b.strengths) if res_b.strengths.startswith("{") else {}
    except Exception:
        swot_a = {}
        swot_b = {}
        
    opps_a = [o.get("text", "") for o in swot_a.get("opportunities", [])]
    opps_b = [o.get("text", "") for o in swot_b.get("opportunities", [])]
    risks_a = [r.get("text", "") for r in swot_a.get("threats", [])]
    risks_b = [r.get("text", "") for r in swot_b.get("threats", [])]
    
    new_opps = list(set(opps_b) - set(opps_a))
    new_risks = list(set(risks_b) - set(risks_a))
    
    return {
        "idea_a": {
            "id": idea_a,
            "title": idea_obj_a.title if idea_obj_a else "Idea A",
            "score": score_a
        },
        "idea_b": {
            "id": idea_b,
            "title": idea_obj_b.title if idea_obj_b else "Idea B",
            "score": score_b
        },
        "comparison": {
            "previous_score": score_a,
            "current_score": score_b,
            "score_difference": round(score_b - score_a, 1),
            "key_changes": f"Viability score shifted from {score_a} to {score_b}.",
            "new_opportunities": new_opps if new_opps else ["Sustained growth options."],
            "new_risks": new_risks if new_risks else ["Similar risk profiles."]
        }
    }

@router.get("/monitoring/stats", tags=["Monitoring"])
async def get_monitoring_stats():
    """Retrieve operational RAG and agent processing trails"""
    return monitoring_service.get_stats()

@router.post("/{idea_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("50/minute")
async def analyze_idea(
    request: Request,
    idea_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger analysis of a business idea with security filters"""
    logger.info(f"[ANALYZE_REQUEST_RECEIVED] POST /analyze/{idea_id}")
    
    # Get the idea
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        logger.warning(f"[ANALYZE_ERROR] Idea {idea_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
        
    # Check if OpenAI API key is configured with a real key (ALWAYS CHECK - not just in production)
    is_dummy_key = (
        not settings.openai_api_key or
        "replace-with-real-key" in settings.openai_api_key or
        "sk-test" in settings.openai_api_key.lower() or
        "your_openai_api_key" in settings.openai_api_key or
        settings.openai_api_key.strip() == ""
    )
    
    if is_dummy_key:
        logger.warning(f"[ANALYSIS_MOCK_MODE] Running analysis in DEMO MODE with simulated responses")
        # Allow analysis to proceed in mock mode for testing/demo purposes

    # Security validations
    payload = {
        "title": idea.title,
        "description": idea.description,
        "problem_statement": idea.problem_statement,
        "target_market": idea.target_market,
        "proposed_solution": idea.proposed_solution,
        "value_proposition": idea.value_proposition,
        "business_model": idea.business_model
    }
    
    # 1. Size checking
    validate_payload_sizes(payload)
    
    # 2. Injection scanning
    for text in payload.values():
        if text:
            check_prompt_injection(text)
            
    # Check if analysis already exists
    existing_analysis = db.query(AnalysisResult).filter(
        AnalysisResult.idea_id == idea_id
    ).first()
    
    if existing_analysis:
        logger.info(f"[ANALYZE_CONFLICT] Analysis already exists for idea {idea_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis already exists for this idea"
        )
    
    # Update idea status
    idea.status = "analyzing"
    db.commit()
    logger.info(f"[ANALYZE_TRIGGER_START] Idea {idea_id} status updated to 'analyzing'")
    
    # Schedule background task with a fresh, dedicated DB session.
    background_tasks.add_task(
        analyze_idea_background,
        idea_id=idea_id
    )
    logger.info(f"[ANALYZE_TRIGGER_SUCCESS] Background task queued for idea {idea_id}")
    
    return {
        "message": "Analysis started",
        "idea_id": idea_id,
        "status": "analyzing"
    }

@router.post("/{idea_id}/trigger", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("50/minute")
async def trigger_idea_analysis(
    request: Request,
    idea_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger analysis of a business idea (alias for analyze)"""
    return await analyze_idea(request, idea_id, background_tasks, db)

import json

async def analyze_idea_background(idea_id: int):
    """Background task to perform sequential agent analysis"""
    db_session = SessionLocal()
    start_time = time.time()
    
    logger.info(f"{'='*80}")
    logger.info(f"[ANALYSIS_START] Idea ID: {idea_id}")
    logger.info(f"{'='*80}")
    
    try:
        idea = db_session.query(Idea).filter(Idea.id == idea_id).first()
        if not idea:
            logger.error(f"[ANALYSIS_ABORT] Idea {idea_id} not found in database")
            return
            
        logger.info(f"[ANALYSIS_INPUT] Title: {idea.title}")
        logger.info(f"[ANALYSIS_INPUT] Description: {idea.description[:200]}")
        logger.info(f"[ANALYSIS_INPUT] Problem Statement: {idea.problem_statement[:200] if idea.problem_statement else 'N/A'}")
        logger.info(f"[ANALYSIS_INPUT] Target Market: {idea.target_market[:200] if idea.target_market else 'N/A'}")
        logger.info(f"[ANALYSIS_INPUT] Proposed Solution: {idea.proposed_solution[:200] if idea.proposed_solution else 'N/A'}")
        logger.info(f"[ANALYSIS_INPUT] Value Proposition: {idea.value_proposition[:200] if idea.value_proposition else 'N/A'}")
        logger.info(f"[ANALYSIS_INPUT] Business Model: {idea.business_model[:200] if idea.business_model else 'N/A'}")
        
        logger.info(f"[ORCHESTRATOR_START] Calling run_full_analysis()...")
        analysis_result = await analysis_orchestrator.run_full_analysis(
            idea_title=idea.title,
            idea_description=idea.description,
            problem_statement=idea.problem_statement or "",
            target_market=idea.target_market or "",
            proposed_solution=idea.proposed_solution or "",
            value_proposition=idea.value_proposition or "",
            business_model=idea.business_model or ""
        )
        logger.info(f"[ORCHESTRATOR_SUCCESS] Analysis completed successfully")
        
        # Log scores
        logger.info(f"[SCORES] Market: {analysis_result['scores']['market_score']}")
        logger.info(f"[SCORES] Financial: {analysis_result['scores']['financial_score']}")
        logger.info(f"[SCORES] Feasibility: {analysis_result['scores']['feasibility_score']}")
        logger.info(f"[SCORES] Risk: {analysis_result['scores']['risk_score']}")
        logger.info(f"[SCORES] Overall: {analysis_result['scores']['overall_score']}")
        
        # Validate scores are not all zeros
        if analysis_result['scores']['overall_score'] == 0:
            logger.warning(f"[WARNING] Overall score is 0 - this may indicate analysis failed silently")
        
        # Log analysis payloads
        logger.info(f"[ANALYSIS_DATA] Market Analysis size: {len(str(analysis_result['market_analysis']))} chars")
        logger.info(f"[ANALYSIS_DATA] Financial Analysis size: {len(str(analysis_result['financial_analysis']))} chars")
        logger.info(f"[ANALYSIS_DATA] Risk Analysis size: {len(str(analysis_result['risk_analysis']))} chars")
        logger.info(f"[ANALYSIS_DATA] Competitive Analysis size: {len(str(analysis_result['competitive_analysis']))} chars")
        logger.info(f"[ANALYSIS_DATA] SWOT Analysis size: {len(str(analysis_result['swot']))} chars")
        
        # Serialize the rich structured responses into the Text fields
        market_str = json.dumps(analysis_result["market_analysis"])
        feasibility_str = json.dumps(analysis_result["feasibility_analysis"])
        financial_str = json.dumps(analysis_result["financial_analysis"])
        risk_str = json.dumps(analysis_result["risk_analysis"])
        competitive_str = json.dumps(analysis_result["competitive_analysis"])
        
        # SWOT grid payload is stored in strengths
        strengths_str = json.dumps(analysis_result["swot"])
        # Final recommendation response structure is stored in weaknesses
        weaknesses_str = json.dumps(analysis_result["recommendation"])
        
        logger.info(f"[DB_SAVE_START] Creating AnalysisResult record...")
        new_analysis = AnalysisResult(
            idea_id=idea_id,
            market_score=analysis_result["scores"]["market_score"],
            feasibility_score=analysis_result["scores"]["feasibility_score"],
            financial_score=analysis_result["scores"]["financial_score"],
            risk_score=analysis_result["scores"]["risk_score"],
            overall_score=analysis_result["scores"]["overall_score"],
            market_analysis=market_str,
            feasibility_analysis=feasibility_str,
            financial_analysis=financial_str,
            risk_analysis=risk_str,
            competitive_analysis=competitive_str,
            strengths=strengths_str,
            weaknesses=weaknesses_str
        )
        
        db_session.add(new_analysis)
        db_session.flush()
        logger.info(f"[DB_SAVE] AnalysisResult saved with ID: {new_analysis.id}")
        
        # Save recommendations
        rec_count = 0
        for rec in analysis_result["recommendations"]:
            new_rec = Recommendation(
                analysis_id=new_analysis.id,
                recommendation_text=rec.get("text", ""),
                category=rec.get("category", "general"),
                priority=rec.get("priority", "medium")
            )
            db_session.add(new_rec)
            rec_count += 1
        logger.info(f"[DB_SAVE] {rec_count} recommendations saved")
            
        # Update idea status
        idea.status = "completed"
        db_session.commit()
        logger.info(f"[DB_COMMIT] Transaction committed successfully")
        
        # Log to monitoring
        duration = time.time() - start_time
        monitoring_service.record_request(duration, success=True)
        for log in analysis_result.get("audit_trail", []):
            monitoring_service.record_agent_trail(log)
            
        # Email notifier
        try:
            from app.services.email_service import email_service
            user_email = idea.user.email if idea.user else "user@example.com"
            await email_service.send_analysis_completion_email(
                user_email=user_email,
                idea_title=idea.title,
                overall_score=analysis_result["scores"]["overall_score"]
            )
        except Exception as email_err:
            logger.error(f"Failed to email user: {str(email_err)}")
            
        logger.info(f"[ANALYSIS_SUCCESS] Analysis completed successfully")
        logger.info(f"[ANALYSIS_DURATION] {duration:.2f} seconds")
        logger.info(f"{'='*80}\n")
        
    except Exception as e:
        logger.error(f"{'='*80}")
        logger.error(f"[ANALYSIS_FAILED] Exception occurred for idea {idea_id}")
        logger.error(f"[ANALYSIS_ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"[ANALYSIS_TRACEBACK] {traceback.format_exc()}")
        
        try:
            idea = db_session.query(Idea).filter(Idea.id == idea_id).first()
            if idea:
                idea.status = "failed"
                db_session.commit()
                logger.info(f"[DB_UPDATE] Idea status marked as 'failed'")
        except Exception as db_err:
            logger.error(f"[DB_ERROR] Could not update idea status: {str(db_err)}")
        
        duration = time.time() - start_time
        monitoring_service.record_request(duration, success=False)
        monitoring_service.record_warning(f"Analysis failed for idea {idea_id}: {str(e)}")
        logger.error(f"[ANALYSIS_DURATION] {duration:.2f} seconds (failed)")
        logger.error(f"{'='*80}\n")
    finally:
        db_session.close()

@router.get("/{idea_id}", response_model=AnalysisResultResponse)
async def get_analysis(idea_id: int, db: Session = Depends(get_db)):
    """Get analysis results for an idea"""
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.idea_id == idea_id
    ).first()
    
    if not analysis:
        logger.error(f"Analysis requested for idea {idea_id} but analysis does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis for this idea does not exist. Please run analysis first via /analyze endpoint."
        )
    
    return analysis


@router.get("/{idea_id}/report", response_model=ReportResponse)
async def get_report(idea_id: int, db: Session = Depends(get_db)):
    """Get report containing idea and analysis results"""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
        
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.idea_id == idea_id
    ).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found for this idea"
        )
        
    return {
        "idea": idea,
        "analysis": analysis
    }
