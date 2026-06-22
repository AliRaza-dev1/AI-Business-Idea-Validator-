"""
Evaluation Runner — Loops over benchmark business ideas, collects agent validation metrics,
computes statistical consistency, runs LLM-as-judge scoring, and outputs structured reports.

LLM-as-Judge: Each analysis result is rated by GPT-4o on:
  - Relevance (1-5): Does the analysis address the actual business idea?
  - Accuracy (1-5): Are claims grounded in retrieved framework knowledge?
  - Actionability (1-5): Are recommendations specific and immediately useful?
"""
import os
import sys
import json
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional

# Setup path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.analysis_orchestrator import analysis_orchestrator
from app.services.knowledge_base import rag_service
from app.core.config import settings
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BENCHMARK_PATH = os.path.join(os.path.dirname(__file__), "benchmark_ideas.json")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "evaluation_report.md")


# ── LLM-as-Judge ─────────────────────────────────────────────────────────────

def llm_as_judge(idea_title: str, analysis_result: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """
    Uses GPT-4o as an automated judge to rate the quality of an analysis output.
    Scores each analysis on:
      - Relevance (1-5): Does the analysis correctly address the specific business idea?
      - Accuracy (1-5): Are the claims grounded in retrieved framework knowledge?
      - Actionability (1-5): Are the recommendations specific, concrete, and immediately useful?

    Returns a dict with scores and reasoning, or defaults of 3 if the call fails.
    """
    if dry_run:
        # Return deterministic mock scores in dry-run mode
        return {
            "relevance": 4,
            "accuracy": 4,
            "actionability": 3,
            "average_judge_score": 3.67,
            "judge_reasoning": "[DRY RUN] Mock judge scores — not a real GPT-4o evaluation."
        }

    try:
        openai_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
        if not openai_key or "sk-test" in openai_key:
            logger.warning("No valid API key for LLM judge — returning defaults.")
            return {"relevance": 3, "accuracy": 3, "actionability": 3, "average_judge_score": 3.0, "judge_reasoning": "Skipped — no API key."}

        client = OpenAI(api_key=openai_key)

        # Summarize the analysis for the judge (avoid token overflow)
        recommendation = analysis_result.get("recommendation", {})
        market = analysis_result.get("market_analysis", {})
        summary_for_judge = {
            "idea_title": idea_title,
            "overall_score": analysis_result.get("scores", {}).get("overall_score"),
            "viability_verdict": recommendation.get("viability_verdict"),
            "executive_summary": recommendation.get("executive_summary", "")[:500],
            "key_market_findings": market.get("key_findings", [])[:3],
            "action_plan_sample": recommendation.get("action_plan", [])[:2],
            "retrieved_sources": market.get("retrieved_knowledge_sources", [])
        }

        judge_prompt = f"""You are an expert business analyst evaluating the quality of an AI-generated business idea analysis.

Business Idea Title: {idea_title}

Analysis Output Summary:
{json.dumps(summary_for_judge, indent=2)}

Please rate this analysis on three dimensions (each 1-5 scale, where 5 is best):

1. RELEVANCE (1-5): Does the analysis correctly address the specific business idea provided? Is it tailored to this idea or generic?
2. ACCURACY (1-5): Are the market claims, risk assessments, and financial assumptions grounded in real business knowledge? Do the retrieved framework sources support the conclusions?
3. ACTIONABILITY (1-5): Are the recommendations specific, concrete, and immediately useful to a founder? Or are they vague platitudes?

Respond ONLY with a JSON object:
{{
  "relevance": <integer 1-5>,
  "accuracy": <integer 1-5>,
  "actionability": <integer 1-5>,
  "judge_reasoning": "<one sentence explaining your overall assessment>"
}}"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a strict, objective business analysis quality evaluator. Respond with raw JSON only."},
                {"role": "user", "content": judge_prompt}
            ],
            temperature=0.2,
            max_tokens=300
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:-1])

        scores = json.loads(raw)
        scores["average_judge_score"] = round(
            (scores.get("relevance", 3) + scores.get("accuracy", 3) + scores.get("actionability", 3)) / 3, 2
        )
        return scores

    except Exception as e:
        logger.error(f"LLM judge failed for '{idea_title}': {str(e)}")
        return {"relevance": 3, "accuracy": 3, "actionability": 3, "average_judge_score": 3.0, "judge_reasoning": f"Judge error: {str(e)}"}

async def run_evaluation(limit: int = 3, dry_run: bool = False):
    """Executes validation benchmarking over the dataset"""
    logger.info("Initializing RAG vector database indexing...")
    # Ensure frameworks are indexed
    try:
        rag_service.chunk_and_index_frameworks()
    except Exception as e:
        logger.error(f"Failed indexing RAG database: {str(e)}")

    if not os.path.exists(BENCHMARK_PATH):
        logger.error(f"Benchmark file not found at {BENCHMARK_PATH}")
        return

    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        ideas = json.load(f)

    selected_ideas = ideas[:limit]
    logger.info(f"Running evaluation benchmark on {len(selected_ideas)} ideas (Total dataset: {len(ideas)})")
    
    results = []
    total_start_time = time.time()
    
    for i, idea in enumerate(selected_ideas, 1):
        logger.info(f"[{i}/{len(selected_ideas)}] Evaluating: {idea['title']} ({idea['category']})")
        
        start_time = time.time()
        try:
            if dry_run:
                # In dry_run/mock mode, construct a mock response with deterministic metrics
                await asyncio.sleep(0.1) # Yield to event loop
                mock_score = 82 if "HR-Bot" in idea["title"] else 74
                actual_result = {
                    "overall_score": mock_score,
                    "scores": {
                        "market_score": 21,
                        "feasibility_score": 12,
                        "financial_score": 16,
                        "risk_score": 16,
                        "competitive_score": 17,
                        "overall_score": mock_score
                    },
                    "recommendation": {
                        "overall_confidence": 88,
                        "overall_confidence_reason": "High matching quality on dry run.",
                        "viability_verdict": "Viable" if mock_score < 80 else "Highly Viable"
                    },
                    "audit_trail": [{"processing_time": 0.05}]
                }
            else:
                actual_result = await analysis_orchestrator.run_full_analysis(
                    idea_title=idea["title"],
                    idea_description=idea["description"],
                    problem_statement=idea["problem_statement"],
                    target_market=idea["target_market"],
                    proposed_solution=idea["proposed_solution"],
                    value_proposition=idea["value_proposition"],
                    business_model=idea["business_model"]
                )
            
            elapsed = time.time() - start_time
            
            # Map score metrics
            score = actual_result.get("scores", {}).get("overall_score", 0.0)
            confidence = actual_result.get("recommendation", {}).get("overall_confidence", 0)
            verdict = actual_result.get("recommendation", {}).get("viability_verdict", "Unknown")
            
            # Evaluate consistency against expected range
            expected_range = idea.get("expected_viability_range", [50, 100])
            is_consistent = expected_range[0] <= score <= expected_range[1]
            
            # Risk checking consistency
            expected_risk = idea.get("expected_risk_level", "Medium")
            actual_risk_score = actual_result.get("scores", {}).get("risk_score", 10)
            # Map risk score to level (high risk = lower manageability score)
            if actual_risk_score <= 7:
                actual_risk = "High"
            elif actual_risk_score <= 14:
                actual_risk = "Medium"
            else:
                actual_risk = "Low"
                
            risk_consistent = (expected_risk == actual_risk)

            # ── LLM-as-Judge Scoring ──────────────────────────────────────
            judge_scores = llm_as_judge(idea["title"], actual_result, dry_run=dry_run)
            logger.info(f"  Judge scores → Relevance:{judge_scores['relevance']} Accuracy:{judge_scores['accuracy']} Actionability:{judge_scores['actionability']} Avg:{judge_scores['average_judge_score']}")

            results.append({
                "title": idea["title"],
                "category": idea["category"],
                "expected_viability_range": expected_range,
                "expected_risk_level": expected_risk,
                "actual_score": score,
                "actual_risk_level": actual_risk,
                "actual_risk_score": actual_risk_score,
                "confidence": confidence,
                "viability_verdict": verdict,
                "latency_sec": elapsed,
                "viability_consistent": is_consistent,
                "risk_consistent": risk_consistent,
                "judge_relevance": judge_scores.get("relevance", 3),
                "judge_accuracy": judge_scores.get("accuracy", 3),
                "judge_actionability": judge_scores.get("actionability", 3),
                "judge_avg": judge_scores.get("average_judge_score", 3.0),
                "judge_reasoning": judge_scores.get("judge_reasoning", ""),
                "status": "Success"
            })
            
            # Sleep brief moments to limit OpenAI rate thresholds if not dry run
            if not dry_run:
                await asyncio.sleep(2.0)
                
        except Exception as e:
            logger.error(f"Failed to evaluate {idea['title']}: {str(e)}")
            results.append({
                "title": idea["title"],
                "category": idea["category"],
                "status": "Failed",
                "error": str(e)
            })

    # ── Statistical Calculations ──────────────────────────────────────────────
    total_elapsed = time.time() - total_start_time
    successful_runs = [r for r in results if r["status"] == "Success"]
    failed_runs = [r for r in results if r["status"] == "Failed"]
    
    avg_viability = 0.0
    avg_confidence = 0.0
    avg_latency = 0.0
    viability_consistency_rate = 0.0
    risk_consistency_rate = 0.0
    
    avg_judge_relevance = 0.0
    avg_judge_accuracy = 0.0
    avg_judge_actionability = 0.0
    avg_judge_overall = 0.0

    if successful_runs:
        avg_viability = sum(r["actual_score"] for r in successful_runs) / len(successful_runs)
        avg_confidence = sum(r["confidence"] for r in successful_runs) / len(successful_runs)
        avg_latency = sum(r["latency_sec"] for r in successful_runs) / len(successful_runs)

        viability_consistent_count = sum(1 for r in successful_runs if r["viability_consistent"])
        viability_consistency_rate = (viability_consistent_count / len(successful_runs)) * 100

        risk_consistent_count = sum(1 for r in successful_runs if r["risk_consistent"])
        risk_consistency_rate = (risk_consistent_count / len(successful_runs)) * 100

        # LLM-as-judge aggregate stats
        avg_judge_relevance = sum(r.get("judge_relevance", 3) for r in successful_runs) / len(successful_runs)
        avg_judge_accuracy = sum(r.get("judge_accuracy", 3) for r in successful_runs) / len(successful_runs)
        avg_judge_actionability = sum(r.get("judge_actionability", 3) for r in successful_runs) / len(successful_runs)
        avg_judge_overall = sum(r.get("judge_avg", 3.0) for r in successful_runs) / len(successful_runs)

    # Build Markdown report
    report = f"""# AI Business Validator — Evaluation Benchmark Report

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Total ideas tested: {len(results)}
Dry Run Mode: {dry_run}

## Performance & Quality Metrics

| Metric | Result |
| :--- | :--- |
| **Average Viability Score** | {avg_viability:.2f} / 100 |
| **Average Agent Confidence** | {avg_confidence:.2f}% |
| **Average Request Latency** | {avg_latency:.2f} seconds |
| **Viability Score Consistency Rate** | {viability_consistency_rate:.1f}% |
| **Risk Assessment Consistency Rate** | {risk_consistency_rate:.1f}% |
| **Successful Iterations** | {len(successful_runs)} / {len(results)} |
| **Execution Failures** | {len(failed_runs)} |

## LLM-as-Judge Scores (GPT-4o Automated Quality Evaluation)

> Each analysis was rated by GPT-4o on Relevance, Accuracy, and Actionability (scale 1–5, higher is better).

| Dimension | Average Score | Interpretation |
| :--- | :--- | :--- |
| **Relevance** | {avg_judge_relevance:.2f} / 5 | Is the analysis tailored to the specific idea? |
| **Accuracy** | {avg_judge_accuracy:.2f} / 5 | Are claims grounded in retrieved framework knowledge? |
| **Actionability** | {avg_judge_actionability:.2f} / 5 | Are recommendations specific and immediately useful? |
| **Overall Judge Score** | {avg_judge_overall:.2f} / 5 | Combined average across all dimensions |

## Detailed Results Breakdown

| Idea Title | Sector | Expected Viability | Actual Score | Expected Risk | Actual Risk | Consistent? | Judge Score | Latency | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for r in results:
        if r["status"] == "Success":
            consistent_str = "✅" if r["viability_consistent"] else "❌"
            judge_str = f"{r.get('judge_avg', 'N/A')}/5"
            report += f"| {r['title']} | {r['category']} | {r['expected_viability_range'][0]}-{r['expected_viability_range'][1]} | {r['actual_score']} | {r['expected_risk_level']} | {r['actual_risk_level']} | {consistent_str} | {judge_str} | {r['latency_sec']:.2f}s | Success |\n"
        else:
            report += f"| {r['title']} | {r['category']} | N/A | N/A | N/A | N/A | ❌ | N/A | N/A | Failed ({r['error']}) |\n"

    # Identify Edge & Failure Cases
    report += "\n## Failure & Edge Case Log\n"
    if failed_runs:
        for f in failed_runs:
            report += f"- **{f['title']}**: Processing failure. Error: `{f['error']}`\n"
    else:
        report += "- Zero processing failures logged.\n"
        
    inconsistent_runs = [r for r in successful_runs if not r["viability_consistent"]]
    report += "\n## Inconsistent Score Cases (Out of Expected Range)\n"
    if inconsistent_runs:
        for ir in inconsistent_runs:
            report += f"- **{ir['title']}** ({ir['category']}): Expected range {ir['expected_viability_range']}, got `{ir['actual_score']}` viability rating.\n"
    else:
        report += "- Zero inconsistent cases logged.\n"

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
        
    try:
        print(report)
    except UnicodeEncodeError:
        try:
            print(report.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8'))
        except Exception:
            print("Evaluation report generated. (Unicode output suppressed on this terminal)")

if __name__ == "__main__":
    limit = 3
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
            
    dry_run = "--dry" in sys.argv or "--dry-run" in sys.argv
    asyncio.run(run_evaluation(limit=limit, dry_run=dry_run))
