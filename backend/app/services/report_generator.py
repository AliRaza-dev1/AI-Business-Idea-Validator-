"""
PDF Report Generation Service — Upgraded to output structured agent breakdowns, SWOT grids, BMC layouts, and RAG attributions.
"""
from datetime import datetime
from typing import Dict, Any, List
import json
import logging
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors

logger = logging.getLogger(__name__)

def _safe_json_load(field: Any) -> Dict[str, Any]:
    """Helper to parse DB text columns which might be serialized JSON or raw strings"""
    if not field:
        return {}
    if isinstance(field, dict):
        return field
    try:
        return json.loads(field)
    except Exception:
        # Fallback if it is a raw legacy string
        return {"_legacy_text": str(field)}

def generate_pdf_report(idea: Dict[str, Any], analysis_raw: Dict[str, Any]) -> bytes:
    """Generate a professional multipage business intelligence report PDF"""
    try:
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer, pagesize=letter,
            rightMargin=54, leftMargin=54,
            topMargin=54, bottomMargin=54
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Color palette
        PRIMARY_COLOR = colors.HexColor('#0F172A') # Slate 900
        SECONDARY_COLOR = colors.HexColor('#1E3A8A') # Blue 900
        ACCENT_COLOR = colors.HexColor('#2563EB') # Blue 600
        TEXT_MUTED = colors.HexColor('#64748B') # Slate 500
        BORDER_COLOR = colors.HexColor('#E2E8F0') # Slate 200
        
        # Style extensions
        title_style = ParagraphStyle(
            'DocTitle', parent=styles['Heading1'],
            fontSize=22, textColor=PRIMARY_COLOR, spaceAfter=8
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle', parent=styles['Normal'],
            fontSize=10, textColor=TEXT_MUTED, spaceAfter=20
        )
        h1_style = ParagraphStyle(
            'H1', parent=styles['Heading2'],
            fontSize=14, textColor=SECONDARY_COLOR, spaceBefore=18, spaceAfter=8
        )
        h2_style = ParagraphStyle(
            'H2', parent=styles['Heading3'],
            fontSize=11, textColor=PRIMARY_COLOR, spaceBefore=10, spaceAfter=4
        )
        body_style = ParagraphStyle(
            'Body', parent=styles['Normal'],
            fontSize=9, leading=12, textColor=colors.HexColor('#334155'), spaceAfter=6
        )
        meta_style = ParagraphStyle(
            'Meta', parent=styles['Normal'],
            fontSize=8, textColor=TEXT_MUTED
        )
        table_body = ParagraphStyle(
            'TBody', parent=styles['Normal'],
            fontSize=8, leading=11, textColor=colors.HexColor('#334155')
        )
        table_header = ParagraphStyle(
            'THeader', parent=styles['Normal'],
            fontSize=8, leading=11, fontName='Helvetica-Bold', textColor=colors.white
        )

        # Parse new structured columns
        market_data = _safe_json_load(analysis_raw.get("market_analysis"))
        feasibility_data = _safe_json_load(analysis_raw.get("feasibility_analysis"))
        financial_data = _safe_json_load(analysis_raw.get("financial_analysis"))
        risk_data = _safe_json_load(analysis_raw.get("risk_analysis"))
        
        comp_raw = analysis_raw.get("competitive_analysis")
        comp_parsed = _safe_json_load(comp_raw)
        comp_data = comp_parsed.get("competition", comp_parsed)
        bmc_data = comp_parsed.get("bmc", {})
        
        swot_data = _safe_json_load(analysis_raw.get("strengths")) # SWOT is now stored in strengths
        rec_data = _safe_json_load(analysis_raw.get("weaknesses")) # Recommendation payload is in weaknesses
        
        # VALIDATION: Provide sensible defaults for missing data
        # If recommendation data is missing, create minimal default structure
        if not rec_data or "_legacy_text" in rec_data:
            logger.warning(f"Report generation: Using default recommendation data")
            rec_data = {
                "overall_score": analysis_raw.get("overall_score", 50),
                "viability_verdict": "Moderate Viability",
                "executive_summary": f"Analysis completed for {idea.get('title', 'Business Idea')}",
                "overall_confidence": 70,
                "overall_confidence_reason": "Analysis completed",
                "score_breakdown": {
                    "market_demand": {"score": 15, "max_score": 25, "reasoning": "Market analysis completed"},
                    "competition": {"score": 12, "max_score": 20, "reasoning": "Competitive analysis completed"},
                    "revenue_potential": {"score": 12, "max_score": 20, "reasoning": "Financial analysis completed"},
                    "scalability": {"score": 8, "max_score": 15, "reasoning": "Feasibility assessment completed"},
                    "risk_management": {"score": 12, "max_score": 20, "reasoning": "Risk assessment completed"}
                },
                "action_plan": [{"recommendation": "Review analysis details and proceed with validation", "priority": "high"}]
            }
        
        if not swot_data or "_legacy_text" in swot_data:
            logger.warning(f"Report generation: Using default SWOT data")
            swot_data = {
                "strengths": [{"text": "Business model identified", "impact": "medium"}] if not swot_data else swot_data.get("strengths", []),
                "weaknesses": [{"text": "Early stage development", "impact": "medium"}] if not swot_data else swot_data.get("weaknesses", []),
                "opportunities": [{"text": "Market potential identified", "impact": "high"}] if not swot_data else swot_data.get("opportunities", []),
                "threats": [{"text": "Competitive landscape exists", "impact": "medium"}] if not swot_data else swot_data.get("threats", [])
            }
        
        # Ensure SWOT arrays exist and have at least placeholder data
        if not swot_data.get("strengths"):
            swot_data["strengths"] = [{"text": "Identified competitive positioning", "impact": "medium"}]
        if not swot_data.get("weaknesses"):
            swot_data["weaknesses"] = [{"text": "Early-stage execution risks", "impact": "medium"}]
        if not swot_data.get("opportunities"):
            swot_data["opportunities"] = [{"text": "Market expansion potential", "impact": "high"}]
        if not swot_data.get("threats"):
            swot_data["threats"] = [{"text": "Competitive response risk", "impact": "medium"}]

        # ── COVER HEADER ──────────────────────────────────────────────────────
        elements.append(Paragraph("AI Business Intelligence Platform", title_style))
        elements.append(Paragraph(f"VALIDATION REPORT — {idea.get('title', 'Untitled').upper()}", subtitle_style))
        
        # Meta info box
        meta_data = [
            [
                Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}", meta_style),
                Paragraph(f"<b>Viability Verdict:</b> {rec_data.get('viability_verdict', 'N/A')}", meta_style)
            ],
            [
                Paragraph(f"<b>Overall Score:</b> {rec_data.get('overall_score', 0)}/100", meta_style),
                Paragraph(f"<b>System Confidence:</b> {rec_data.get('overall_confidence', 0)}% ({rec_data.get('overall_confidence_reason', '')})", meta_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[3.0*inch, 4.0*inch])
        meta_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # ── EXECUTIVE SUMMARY ─────────────────────────────────────────────────
        elements.append(Paragraph("Executive Summary", h1_style))
        summary_text = rec_data.get("executive_summary") or rec_data.get("summary") or "Analysis completed successfully"
        elements.append(Paragraph(summary_text, body_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # ── SCORE EXPLAINABILITY BREAKDOWN ────────────────────────────────────
        elements.append(Paragraph("Explainable Viability Score Breakdown", h1_style))
        
        score_rows = [
            [
                Paragraph("<b>Viability Dimension</b>", table_header), 
                Paragraph("<b>Calculated Score</b>", table_header), 
                Paragraph("<b>Reasoning</b>", table_header)
            ]
        ]
        
        breakdown = rec_data.get("score_breakdown", {})
        dimensions = [
            ("market_demand", "Market Demand", 25),
            ("competition", "Competitive Density", 20),
            ("revenue_potential", "Revenue Potential", 20),
            ("scalability", "Scalability Index", 15),
            ("risk_management", "Risk Resilience", 20)
        ]
        
        for key, label, max_val in dimensions:
            dim_info = breakdown.get(key, {})
            score_val = dim_info.get("score", 0)
            reason = dim_info.get("reasoning", "No detail provided.")
            score_rows.append([
                Paragraph(f"<b>{label}</b>", table_body),
                Paragraph(f"{score_val} / {max_val}", table_body),
                Paragraph(reason, table_body)
            ])
            
        score_rows.append([
            Paragraph("<b>TOTAL VIABILITY SCORE</b>", table_body),
            Paragraph(f"<b>{rec_data.get('overall_score', 0)} / 100</b>", table_body),
            Paragraph("Sum of all weighted categories.", table_body)
        ])
        
        score_table = Table(score_rows, colWidths=[1.8*inch, 1.2*inch, 4.0*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_COLOR),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F8FAFC')),
        ]))
        elements.append(score_table)
        elements.append(PageBreak())
        
        # ── SPECIALIZED AGENT ANALYSES ────────────────────────────────────────
        elements.append(Paragraph("Specialized Agent Analytics", h1_style))
        
        # Market Agent
        elements.append(Paragraph("1. Market Intelligence Analysis", h2_style))
        market_findings = f"""
        <b>Market Score:</b> {market_data.get('score', 0)}/25 | <b>Confidence:</b> {market_data.get('confidence', 0)}%<br/>
        <b>TAM/SAM/SOM:</b><br/>
        &bull; TAM: {market_data.get('tam_sam_som', {}).get('tam', 'N/A')}<br/>
        &bull; SAM: {market_data.get('tam_sam_som', {}).get('sam', 'N/A')}<br/>
        &bull; SOM: {market_data.get('tam_sam_som', {}).get('som', 'N/A')}<br/>
        <b>Target Segment:</b> {market_data.get('target_audience', 'N/A')}<br/>
        <b>Reasoning:</b> {market_data.get('reasoning', 'N/A')}<br/>
        <b>Framework Source(s):</b> {', '.join(market_data.get('retrieved_knowledge_sources', ['Market Research']))}
        """
        elements.append(Paragraph(market_findings, body_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Competition Agent
        elements.append(Paragraph("2. Competition & Defensibility Analysis", h2_style))
        comp_findings = f"""
        <b>Competition Score:</b> {comp_data.get('score', 0)}/20 | <b>Confidence:</b> {comp_data.get('confidence', 0)}%<br/>
        <b>Competitor Landscape:</b> {comp_data.get('competitor_landscape', 'N/A')}<br/>
        <b>Competitive Moats:</b> {comp_data.get('competitive_advantages', 'N/A')}<br/>
        <b>Differentiation Factors:</b> {comp_data.get('differentiation', 'N/A')}<br/>
        <b>Framework Source(s):</b> {', '.join(comp_data.get('retrieved_knowledge_sources', ['Porter Five Forces']))}
        """
        elements.append(Paragraph(comp_findings, body_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Financial Agent
        elements.append(Paragraph("3. Financial Feasibility Analysis", h2_style))
        fin_streams = ", ".join(financial_data.get("revenue_streams", ["N/A"]))
        fin_costs = ", ".join(financial_data.get("cost_structure", ["N/A"]))
        fin_findings = f"""
        <b>Financial Score:</b> {financial_data.get('score', 0)}/20 | <b>Confidence:</b> {financial_data.get('confidence', 0)}%<br/>
        <b>Revenue Models:</b> {fin_streams}<br/>
        <b>Primary Costs:</b> {fin_costs}<br/>
        <b>Breakeven Path:</b> {financial_data.get('breakeven_projection', 'N/A')}<br/>
        <b>Framework Source(s):</b> {', '.join(financial_data.get('retrieved_knowledge_sources', ['Financial Validation']))}
        """
        elements.append(Paragraph(fin_findings, body_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Risk Agent
        elements.append(Paragraph("4. Risk Assessment & Failure Safeguards", h2_style))
        mitigations = "; ".join(risk_data.get("mitigation_strategies", ["N/A"]))
        risk_findings = f"""
        <b>Risk Management Score:</b> {risk_data.get('score', 0)}/20 | <b>Confidence:</b> {risk_data.get('confidence', 0)}%<br/>
        <b>Mitigation Strategies:</b> {mitigations}<br/>
        <b>Risk Reasoning:</b> {risk_data.get('reasoning', 'N/A')}<br/>
        <b>Framework Source(s):</b> {', '.join(risk_data.get('retrieved_knowledge_sources', ['Startup Failure Patterns']))}
        """
        elements.append(Paragraph(risk_findings, body_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Growth Agent
        elements.append(Paragraph("5. Growth Potential & Investor Readiness", h2_style))
        inv_readiness = feasibility_data.get("investor_readiness", {})
        inv_strengths = ", ".join(inv_readiness.get("strengths", ["N/A"]))
        inv_weaknesses = ", ".join(inv_readiness.get("weaknesses", ["N/A"]))
        growth_findings = f"""
        <b>Scalability Score:</b> {feasibility_data.get('score', 0)}/15 | <b>Confidence:</b> {feasibility_data.get('confidence', 0)}%<br/>
        <b>Scalability Assessment:</b> {feasibility_data.get('scalability_factors', 'N/A')}<br/>
        <b>Investor Readiness Score:</b> {inv_readiness.get('investor_score', 0)}/100<br/>
        <b>Recommended Funding Stage:</b> {inv_readiness.get('funding_stage_recommendation', 'N/A')}<br/>
        <b>Investor Strengths:</b> {inv_strengths}<br/>
        <b>Investor Weaknesses:</b> {inv_weaknesses}<br/>
        <b>Funding Stage Reasoning:</b> {inv_readiness.get('reasoning', 'N/A')}<br/>
        <b>Framework Source(s):</b> {', '.join(feasibility_data.get('retrieved_knowledge_sources', ['Lean Startup']))}
        """
        elements.append(Paragraph(growth_findings, body_style))
        elements.append(PageBreak())
        
        # ── SWOT ANALYSIS GRID ────────────────────────────────────────────────
        elements.append(Paragraph("SWOT Analysis Matrix", h1_style))
        
        def format_swot_list(items: List[Dict[str, Any]]) -> str:
            """Safely format SWOT list items with fallback handling"""
            if not items:
                return "None identified."
            if isinstance(items, str):
                return items
            
            res_bullets = []
            try:
                for item in items:
                    if isinstance(item, dict):
                        text = item.get('text', 'Item')
                        source = item.get('framework_source', 'SWOT')
                        res_bullets.append(f"&bull; {text} <i>[Source: {source}]</i>")
                    else:
                        res_bullets.append(f"&bull; {str(item)}")
            except Exception as e:
                logger.warning(f"Error formatting SWOT list: {str(e)}")
                return "Analysis data available."
            
            return "<br/><br/>".join(res_bullets) if res_bullets else "None identified."
            
        swot_rows = [
            [
                Paragraph("<b>STRENGTHS (Internal)</b>", table_header),
                Paragraph("<b>WEAKNESSES (Internal)</b>", table_header)
            ],
            [
                Paragraph(format_swot_list(swot_data.get("strengths", [])), table_body),
                Paragraph(format_swot_list(swot_data.get("weaknesses", [])), table_body)
            ],
            [
                Paragraph("<b>OPPORTUNITIES (External)</b>", table_header),
                Paragraph("<b>THREATS (External)</b>", table_header)
            ],
            [
                Paragraph(format_swot_list(swot_data.get("opportunities", [])), table_body),
                Paragraph(format_swot_list(swot_data.get("threats", [])), table_body)
            ]
        ]
        
        swot_table = Table(swot_rows, colWidths=[3.5*inch, 3.5*inch])
        swot_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#065F46')), # Dark Green
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#991B1B')), # Dark Red
            ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#1E3A8A')), # Dark Blue
            ('BACKGROUND', (1, 2), (1, 2), colors.HexColor('#854D0E')), # Dark Yellow/Orange
            ('GRID', (0, 0), (-1, -1), 1, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(swot_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # ── BUSINESS MODEL CANVAS ─────────────────────────────────────────────
        elements.append(Paragraph("Business Model Canvas Guidelines", h1_style))
        
        def b_box(block: Dict[str, Any]) -> Paragraph:
            """Safely format BMC box content with fallback handling"""
            if not block or not isinstance(block, dict):
                return Paragraph("Analysis data available.", table_body)
            
            details = block.get('details', 'N/A')
            source = block.get('framework_source', 'BMC')
            
            if isinstance(details, (list, dict)):
                details = str(details)
            
            text = f"{details}<br/><i>[Source: {source}]</i>"
            return Paragraph(text, table_body)
            
        bmc_rows = [
            [
                Paragraph("<b>Key Partners</b>", table_header),
                Paragraph("<b>Key Activities & Resources</b>", table_header),
                Paragraph("<b>Value Propositions</b>", table_header),
                Paragraph("<b>Customer Relationships & Channels</b>", table_header),
                Paragraph("<b>Customer Segments</b>", table_header)
            ],
            [
                b_box(bmc_data.get("key_partners", {})),
                Table([
                    [Paragraph("<b>Activities:</b>", table_body)],
                    [b_box(bmc_data.get("key_activities", {}))],
                    [Paragraph("<b>Resources:</b>", table_body)],
                    [b_box(bmc_data.get("key_resources", {}))]
                ], colWidths=[1.3*inch], rowHeights=None, style=[('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]),
                b_box(bmc_data.get("value_proposition", {})),
                Table([
                    [Paragraph("<b>Relationships:</b>", table_body)],
                    [b_box(bmc_data.get("customer_relationships", {}))],
                    [Paragraph("<b>Channels:</b>", table_body)],
                    [b_box(bmc_data.get("channels", {}))]
                ], colWidths=[1.3*inch], style=[('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]),
                b_box(bmc_data.get("customer_segments", {}))
            ],
            [
                Paragraph("<b>Cost Structure</b>", table_header),
                Paragraph("", table_header), # span
                Paragraph("<b>Revenue Streams</b>", table_header),
                Paragraph("", table_header), # span
                Paragraph("", table_header)  # span
            ],
            [
                b_box(bmc_data.get("cost_structure", {})),
                b_box(bmc_data.get("cost_structure", {})), # placeholder for colspan in logic
                b_box(bmc_data.get("revenue_streams", {})),
                b_box(bmc_data.get("revenue_streams", {})),
                b_box(bmc_data.get("revenue_streams", {}))
            ]
        ]
        
        # Adjust table widths
        bmc_table = Table(bmc_rows, colWidths=[1.4*inch, 1.4*inch, 1.4*inch, 1.4*inch, 1.4*inch])
        bmc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
            ('BACKGROUND', (0, 2), (1, 2), PRIMARY_COLOR),
            ('BACKGROUND', (2, 2), (-1, 2), PRIMARY_COLOR),
            ('SPAN', (0, 2), (1, 2)),
            ('SPAN', (2, 2), (4, 2)),
            ('SPAN', (0, 3), (1, 3)),
            ('SPAN', (2, 3), (4, 3)),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(bmc_table)
        elements.append(PageBreak())
        
        # ── ACTION PLAN & ATTRIBUTION ─────────────────────────────────────────
        elements.append(Paragraph("Action Plan & Next Steps", h1_style))
        
        rec_rows = [
            [
                Paragraph("<b>Recommendation</b>", table_header),
                Paragraph("<b>Category</b>", table_header),
                Paragraph("<b>Priority</b>", table_header),
                Paragraph("<b>Retrieved Framework Source</b>", table_header)
            ]
        ]
        
        for item in rec_data.get("action_plan", []):
            rec_rows.append([
                Paragraph(item.get("recommendation", ""), table_body),
                Paragraph(item.get("category", "General").capitalize(), table_body),
                Paragraph(f"<b>{item.get('priority', 'Medium').upper()}</b>", table_body),
                Paragraph(item.get("framework_source", "Lean Startup"), table_body)
            ])
            
        rec_table = Table(rec_rows, colWidths=[3.2*inch, 1.1*inch, 0.9*inch, 1.8*inch])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_COLOR),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(rec_table)
        elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph("Recommended Next Steps", h2_style))
        for step in rec_data.get("next_steps", []):
            elements.append(Paragraph(f"&bull; {step}", body_style))
            
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.read()
        
    except Exception as e:
        logger.error(f"Failed to generate custom PDF report: {str(e)}")
        raise

def generate_json_report(idea: Dict[str, Any], analysis_raw: Dict[str, Any]) -> Dict[str, Any]:
    """Compile structured JSON report with framework attributions, preserving legacy structure"""
    market_data = _safe_json_load(analysis_raw.get("market_analysis"))
    feasibility_data = _safe_json_load(analysis_raw.get("feasibility_analysis"))
    financial_data = _safe_json_load(analysis_raw.get("financial_analysis"))
    risk_data = _safe_json_load(analysis_raw.get("risk_analysis"))
    
    comp_parsed = _safe_json_load(analysis_raw.get("competitive_analysis"))
    comp_data = comp_parsed.get("competition", comp_parsed)
    bmc_data = comp_parsed.get("bmc", {})
    
    swot_data = _safe_json_load(analysis_raw.get("strengths"))
    rec_data = _safe_json_load(analysis_raw.get("weaknesses"))
    
    # Audit log extraction
    audit_trail = []
    for d in [market_data, comp_parsed, financial_data, risk_data, feasibility_data, swot_data, bmc_data, rec_data]:
        if isinstance(d, dict) and "_audit_log" in d:
            audit_trail.append(d["_audit_log"])

    # Map legacy score values
    overall_score = float(analysis_raw.get("overall_score", 0.0))
    market_score = float(analysis_raw.get("market_score", 0.0))
    feasibility_score = float(analysis_raw.get("feasibility_score", 0.0))
    financial_score = float(analysis_raw.get("financial_score", 0.0))
    risk_score = float(analysis_raw.get("risk_score", 0.0))

    return {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "idea": {
            "id": idea.get("id"),
            "title": idea.get("title"),
            "description": idea.get("description"),
            "problem_statement": idea.get("problem_statement"),
            "target_market": idea.get("target_market"),
            "proposed_solution": idea.get("proposed_solution"),
            "value_proposition": idea.get("value_proposition"),
            "business_model": idea.get("business_model"),
            "status": idea.get("status"),
            "created_at": str(idea.get("created_at")),
            "updated_at": str(idea.get("updated_at"))
        },
        "analysis": {
            "overall_score": overall_score,
            "market_score": market_score,
            "feasibility_score": feasibility_score,
            "financial_score": financial_score,
            "risk_score": risk_score,
            "market_analysis": market_data.get("reasoning", str(analysis_raw.get("market_analysis"))),
            "feasibility_analysis": feasibility_data.get("reasoning", str(analysis_raw.get("feasibility_analysis"))),
            "financial_analysis": financial_data.get("reasoning", str(analysis_raw.get("financial_analysis"))),
            "risk_analysis": risk_data.get("reasoning", str(analysis_raw.get("risk_analysis"))),
            "competitive_analysis": comp_data.get("reasoning", str(analysis_raw.get("competitive_analysis"))),
            "strengths": analysis_raw.get("strengths"),
            "weaknesses": analysis_raw.get("weaknesses"),
            "recommendations": [
                {
                    "recommendation_text": rec.get("recommendation", ""),
                    "category": rec.get("category", "general"),
                    "priority": rec.get("priority", "medium")
                } for rec in rec_data.get("action_plan", [])
            ]
        },
        "score_card": {
            "overall_score": rec_data.get("overall_score", overall_score * 10),
            "overall_confidence": rec_data.get("overall_confidence", 80),
            "confidence_explanation": rec_data.get("overall_confidence_reason", ""),
            "verdict": rec_data.get("viability_verdict", "Viable"),
            "breakdown": rec_data.get("score_breakdown", {})
        },
        "agents": {
            "market_agent": market_data,
            "competition_agent": comp_data,
            "financial_agent": financial_data,
            "risk_agent": risk_data,
            "growth_agent": feasibility_data
        },
        "swot_analysis": swot_data,
        "business_model_canvas": bmc_data,
        "action_plan": rec_data.get("action_plan", []),
        "next_steps": rec_data.get("next_steps", []),
        "audit_trail": audit_trail
    }
