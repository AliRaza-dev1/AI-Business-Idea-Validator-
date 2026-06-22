from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Idea, AnalysisResult
from app.services.report_generator import generate_pdf_report, generate_json_report
import logging

router = APIRouter(prefix="/api/v1/ideas", tags=["Reports"])
logger = logging.getLogger(__name__)

@router.get("/{idea_id}/report/pdf")
async def get_pdf_report(idea_id: int, db: Session = Depends(get_db)):
    """Generate and download PDF report for an idea"""
    
    # Get idea
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Get analysis
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.idea_id == idea_id
    ).first()
    
    if not analysis:
        logger.error(f"PDF report requested for idea {idea_id} but analysis does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis for this idea does not exist. Please run analysis first via /analyze endpoint."
        )
    
    analysis_data = {
        "overall_score": analysis.overall_score,
        "market_score": analysis.market_score,
        "feasibility_score": analysis.feasibility_score,
        "financial_score": analysis.financial_score,
        "risk_score": analysis.risk_score,
        "market_analysis": analysis.market_analysis,
        "feasibility_analysis": analysis.feasibility_analysis,
        "financial_analysis": analysis.financial_analysis,
        "risk_analysis": analysis.risk_analysis,
        "competitive_analysis": analysis.competitive_analysis,
        "strengths": analysis.strengths,
        "weaknesses": analysis.weaknesses,
        "recommendations": []
    }
    
    # Generate PDF
    try:
        pdf_bytes = generate_pdf_report(
            {
                "id": idea.id,
                "title": idea.title,
                "description": idea.description,
                "problem_statement": idea.problem_statement,
                "target_market": idea.target_market,
                "proposed_solution": idea.proposed_solution,
                "value_proposition": idea.value_proposition,
                "business_model": idea.business_model,
                "status": idea.status,
                "created_at": idea.created_at,
                "updated_at": idea.updated_at
            },
            analysis_data
        )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=idea_{idea_id}_report.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF report: {str(e)}"
        )


@router.get("/{idea_id}/report/json")
async def get_json_report(idea_id: int, db: Session = Depends(get_db)):
    """Generate JSON report for an idea"""
    
    # Get idea
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Get analysis
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.idea_id == idea_id
    ).first()
    
    if not analysis:
        logger.error(f"JSON report requested for idea {idea_id} but analysis does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis for this idea does not exist. Please run analysis first via /analyze endpoint."
        )
    
    analysis_data = {
        "overall_score": analysis.overall_score,
        "market_score": analysis.market_score,
        "feasibility_score": analysis.feasibility_score,
        "financial_score": analysis.financial_score,
        "risk_score": analysis.risk_score,
        "market_analysis": analysis.market_analysis,
        "feasibility_analysis": analysis.feasibility_analysis,
        "financial_analysis": analysis.financial_analysis,
        "risk_analysis": analysis.risk_analysis,
        "competitive_analysis": analysis.competitive_analysis,
        "strengths": analysis.strengths,
        "weaknesses": analysis.weaknesses,
        "recommendations": []
    }
    
    # Generate JSON
    try:
        report = generate_json_report(
            {
                "id": idea.id,
                "title": idea.title,
                "description": idea.description,
                "problem_statement": idea.problem_statement,
                "target_market": idea.target_market,
                "proposed_solution": idea.proposed_solution,
                "value_proposition": idea.value_proposition,
                "business_model": idea.business_model,
                "status": idea.status,
                "created_at": idea.created_at,
                "updated_at": idea.updated_at
            },
            analysis_data
        )
        
        import json
        return Response(
            content=json.dumps(report, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=idea_{idea_id}_report.json"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating JSON report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating JSON report: {str(e)}"
        )
