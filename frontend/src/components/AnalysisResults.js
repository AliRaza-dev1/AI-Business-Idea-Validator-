import React, { useState, useEffect, useCallback } from 'react';
import '../styles/AnalysisResults.css';
import { analysis as analysisApi, reports, ideas as ideasApi } from '../services/api';

const safeJsonParse = (str, fallback = {}) => {
  if (!str) return fallback;
  if (typeof str === 'object') return str;
  try {
    return JSON.parse(str);
  } catch (e) {
    return { _legacyText: str };
  }
};

export default function AnalysisResults({ ideaId, initialError = '', onClearError = () => {} }) {
  const [results, setResults] = useState(null);
  const [idea, setIdea] = useState(null);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);
  const [currentStage, setCurrentStage] = useState(1);
  const [error, setError] = useState(initialError);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [downloadingJson, setDownloadingJson] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');

  const fetchResults = useCallback(async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      const response = await analysisApi.getAnalysis(ideaId);
      setResults(response.data);
      setPolling(false);
      setError('');
    } catch (err) {
      // If 404, the analysis is not created yet. Fetch idea status.
      try {
        const ideaRes = await ideasApi.getById(ideaId);
        const ideaData = ideaRes.data;
        setIdea(ideaData);
        
        if (ideaData.status === 'analyzing') {
          setPolling(true);
          setError('');
        } else if (ideaData.status === 'failed') {
          setError('✗ Analysis failed on the backend. Please check: 1) Is OpenAI API key configured in backend/.env? 2) Check backend logs for details.');
          setPolling(false);
        } else if (ideaData.status === 'pending') {
          // Status stuck at pending means the analysis trigger call failed
          setError('✗ Analysis failed to start. This usually means: 1) OpenAI API key not configured, 2) API key is invalid. Please configure OPENAI_API_KEY in backend/.env and restart.');
          setPolling(false);
        } else {
          setError('Unknown analysis status: ' + ideaData.status);
        }
      } catch (ideaErr) {
        setError('Error loading idea details: ' + (ideaErr.response?.data?.detail || ideaErr.message));
      }
    } finally {
      if (!silent) setLoading(false);
    }
  }, [ideaId]);

  useEffect(() => {
    if (ideaId) {
      fetchResults();
    }
  }, [ideaId, fetchResults]);

  // Polling logic for background agent execution
  useEffect(() => {
    let intervalId;
    let stageIntervalId;

    if (polling) {
      // Poll backend every 3 seconds
      intervalId = setInterval(() => {
        fetchResults(true);
      }, 3000);

      // Simulate sequential agent execution progress
      stageIntervalId = setInterval(() => {
        setCurrentStage((prev) => (prev < 7 ? prev + 1 : prev));
      }, 4000);
    } else {
      setCurrentStage(1);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
      if (stageIntervalId) clearInterval(stageIntervalId);
    };
  }, [polling, fetchResults]);

  const handleDownloadPdf = async () => {
    try {
      setDownloadingPdf(true);
      const response = await reports.getPdfReport(ideaId);
      // response.data is already a Blob when responseType is 'blob'
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `idea_${ideaId}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download PDF:', err);
      alert('Failed to download PDF report.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleDownloadJson = async () => {
    try {
      setDownloadingJson(true);
      const response = await reports.getJsonReport(ideaId);
      const jsonString = JSON.stringify(response.data, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `idea_${ideaId}_report.json`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download JSON:', err);
      alert('Failed to download JSON report.');
    } finally {
      setDownloadingJson(false);
    }
  };

  if (loading && !results && !polling) {
    return <div className="analysis-loading">Gathering intelligence parameters...</div>;
  }

  // Active analysis polling overlay
  if (polling) {
    const stages = [
      { id: 1, name: 'Market Intelligence Agent', desc: 'Estimating TAM/SAM/SOM & target demand...' },
      { id: 2, name: 'Competition Analysis Agent', desc: 'Mapping competitive landscape & positioning...' },
      { id: 3, name: 'Financial Feasibility Agent', desc: 'Projecting cost structure & breakeven path...' },
      { id: 4, name: 'Risk Assessment Agent', desc: 'Scanning startup failure patterns & legal hazards...' },
      { id: 5, name: 'Growth Potential Agent', desc: 'Evaluating scalability & investor readiness...' },
      { id: 6, name: 'Recommendation Synthesis Agent', desc: 'Compiling SWOT analysis & Business Model Canvas...' },
      { id: 7, name: 'Generating Report Artifacts', desc: 'Finalizing scores & storing details...' }
    ];

    return (
      <div className="agent-progress-container">
        <h3>🚀 Sequential Agent Pipeline Active</h3>
        <p>Our autonomous business agents are retrieving RAG framework context and verifying your business idea.</p>
        
        <div className="progress-steps">
          {stages.map((stage) => {
            let statusClass = 'pending';
            if (currentStage > stage.id) statusClass = 'completed';
            else if (currentStage === stage.id) statusClass = 'active';
            
            return (
              <div key={stage.id} className={`progress-step ${statusClass}`}>
                <div className="step-num">{stage.id}</div>
                <div className="step-details">
                  <h4>{stage.name}</h4>
                  <p>{stage.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
        <div className="pulse-loader"></div>
      </div>
    );
  }

  if (error) {
    return <div className="analysis-error">{error}</div>;
  }

  if (!results) {
    return <div className="analysis-empty">No validation results mapped.</div>;
  }

  // Deserialise rich json properties
  const market = safeJsonParse(results.market_analysis);
  const feasibility = safeJsonParse(results.feasibility_analysis);
  const financial = safeJsonParse(results.financial_analysis);
  const risk = safeJsonParse(results.risk_analysis);
  
  const compRaw = safeJsonParse(results.competitive_analysis);
  const competition = compRaw.competition || compRaw;
  const bmc = compRaw.bmc || {};
  
  const swot = safeJsonParse(results.strengths);
  const rec = safeJsonParse(results.weaknesses);

  const breakdown = rec.score_breakdown || {};
  const actionPlan = rec.action_plan || [];
  const nextSteps = rec.next_steps || [];

  return (
    <div className="analysis-results-panel">
      <div className="results-header">
        <div className="header-meta">
          <h2>AI Intelligence Output: {idea?.title || results.idea_title || 'Business Idea'}</h2>
          <span className={`verdict-tag verdict-${(rec.viability_verdict || 'Viable').replace(' ', '-').toLowerCase()}`}>
            {rec.viability_verdict || 'Viable'}
          </span>
        </div>
        <div className="report-actions">
          <button onClick={handleDownloadPdf} disabled={downloadingPdf} className="download-btn pdf-btn">
            {downloadingPdf ? 'Downloading PDF...' : '📄 Download PDF'}
          </button>
          <button onClick={handleDownloadJson} disabled={downloadingJson} className="download-btn json-btn">
            {downloadingJson ? 'Exporting JSON...' : '📊 Export JSON'}
          </button>
        </div>
      </div>

      {/* Main Score Overview Banner */}
      <div className="score-summary-banner">
        <div className="score-wheel-container">
          <div className="score-wheel">
            <span className="big-score">{rec.overall_score || results.overall_score || 0}</span>
            <span className="max-score">/100</span>
          </div>
          <div className="score-wheel-label">Viability Rating</div>
        </div>
        
        <div className="confidence-metric">
          <h4>Agent Confidence Index: {rec.overall_confidence || 80}%</h4>
          <p className="confidence-reason">"{rec.overall_confidence_reason || 'RAG frameworks aligned successfully.'}"</p>
        </div>
      </div>

      {/* Tab Menu Navigation */}
      <div className="tab-menu">
        <button className={activeTab === 'summary' ? 'active' : ''} onClick={() => setActiveTab('summary')}>Summary & SWOT</button>
        <button className={activeTab === 'score' ? 'active' : ''} onClick={() => setActiveTab('score')}>Category Explanations</button>
        <button className={activeTab === 'bmc' ? 'active' : ''} onClick={() => setActiveTab('bmc')}>Business Canvas</button>
        <button className={activeTab === 'agents' ? 'active' : ''} onClick={() => setActiveTab('agents')}>Agent Insights</button>
        <button className={activeTab === 'actions' ? 'active' : ''} onClick={() => setActiveTab('actions')}>Action Plan</button>
      </div>

      <div className="tab-content">
        {activeTab === 'summary' && (
          <div className="summary-tab">
            <div className="exe-summary-card">
              <h3>Executive Summary</h3>
              <p>{rec.executive_summary || 'No summary compiled.'}</p>
            </div>

            {/* SWOT Grid View */}
            <div className="swot-matrix-container">
              <h3>Derived SWOT Analysis</h3>
              <div className="swot-grid">
                <div className="swot-cell swot-s">
                  <h4>STRENGTHS</h4>
                  <ul>
                    {(swot.strengths || []).map((s, idx) => (
                      <li key={idx}>
                        {s.text} <span className="source-tag">{s.framework_source}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="swot-cell swot-w">
                  <h4>WEAKNESSES</h4>
                  <ul>
                    {(swot.weaknesses || []).map((w, idx) => (
                      <li key={idx}>
                        {w.text} <span className="source-tag">{w.framework_source}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="swot-cell swot-o">
                  <h4>OPPORTUNITIES</h4>
                  <ul>
                    {(swot.opportunities || []).map((o, idx) => (
                      <li key={idx}>
                        {o.text} <span className="source-tag">{o.framework_source}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="swot-cell swot-t">
                  <h4>THREATS</h4>
                  <ul>
                    {(swot.threats || []).map((t, idx) => (
                      <li key={idx}>
                        {t.text} <span className="source-tag">{t.framework_source}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'score' && (
          <div className="score-tab">
            <h3>Explainable Score Breakdown</h3>
            <div className="explainable-score-list">
              <div className="explain-score-item">
                <div className="score-row">
                  <span>Market Demand</span>
                  <strong>{breakdown.market_demand?.score || 0} / 25</strong>
                </div>
                <p className="explain-text">{breakdown.market_demand?.reasoning}</p>
              </div>
              <div className="explain-score-item">
                <div className="score-row">
                  <span>Competitive Density</span>
                  <strong>{breakdown.competition?.score || 0} / 20</strong>
                </div>
                <p className="explain-text">{breakdown.competition?.reasoning}</p>
              </div>
              <div className="explain-score-item">
                <div className="score-row">
                  <span>Revenue Potential</span>
                  <strong>{breakdown.revenue_potential?.score || 0} / 20</strong>
                </div>
                <p className="explain-text">{breakdown.revenue_potential?.reasoning}</p>
              </div>
              <div className="explain-score-item">
                <div className="score-row">
                  <span>Scalability Index</span>
                  <strong>{breakdown.scalability?.score || 0} / 15</strong>
                </div>
                <p className="explain-text">{breakdown.scalability?.reasoning}</p>
              </div>
              <div className="explain-score-item">
                <div className="score-row">
                  <span>Risk Resilience</span>
                  <strong>{breakdown.risk_management?.score || 0} / 20</strong>
                </div>
                <p className="explain-text">{breakdown.risk_management?.reasoning}</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'bmc' && (
          <div className="bmc-tab">
            <h3>Business Model Canvas Blocks</h3>
            <div className="bmc-canvas-grid">
              <div className="bmc-block bmc-partners">
                <h5>Key Partners</h5>
                <p>{bmc.key_partners?.details}</p>
                <div className="bmc-source">{bmc.key_partners?.framework_source}</div>
              </div>
              <div className="bmc-subgrid">
                <div className="bmc-block bmc-activities">
                  <h5>Key Activities</h5>
                  <p>{bmc.key_activities?.details}</p>
                  <div className="bmc-source">{bmc.key_activities?.framework_source}</div>
                </div>
                <div className="bmc-block bmc-resources">
                  <h5>Key Resources</h5>
                  <p>{bmc.key_resources?.details}</p>
                  <div className="bmc-source">{bmc.key_resources?.framework_source}</div>
                </div>
              </div>
              <div className="bmc-block bmc-props">
                <h5>Value Propositions</h5>
                <p>{bmc.value_proposition?.details}</p>
                <div className="bmc-source">{bmc.value_proposition?.framework_source}</div>
              </div>
              <div className="bmc-subgrid">
                <div className="bmc-block bmc-relationships">
                  <h5>Customer Relationships</h5>
                  <p>{bmc.customer_relationships?.details}</p>
                  <div className="bmc-source">{bmc.customer_relationships?.framework_source}</div>
                </div>
                <div className="bmc-block bmc-channels">
                  <h5>Channels</h5>
                  <p>{bmc.channels?.details}</p>
                  <div className="bmc-source">{bmc.channels?.framework_source}</div>
                </div>
              </div>
              <div className="bmc-block bmc-segments">
                <h5>Customer Segments</h5>
                <p>{bmc.customer_segments?.details}</p>
                <div className="bmc-source">{bmc.customer_segments?.framework_source}</div>
              </div>
            </div>
            
            <div className="bmc-bottom-row">
              <div className="bmc-block bmc-costs">
                <h5>Cost Structure</h5>
                <p>{bmc.cost_structure?.details}</p>
                <div className="bmc-source">{bmc.cost_structure?.framework_source}</div>
              </div>
              <div className="bmc-block bmc-revenues">
                <h5>Revenue Streams</h5>
                <p>{bmc.revenue_streams?.details}</p>
                <div className="bmc-source">{bmc.revenue_streams?.framework_source}</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="agents-tab">
            <div className="agent-detail-card">
              <h4>1. Market Intelligence Agent</h4>
              <p><strong>Subscore:</strong> {market.score}/25 | <strong>Confidence:</strong> {market.confidence}% ({market.confidence_reason})</p>
              <p><strong>TAM/SAM/SOM:</strong> TAM: {market.tam_sam_som?.tam} | SAM: {market.tam_sam_som?.sam} | SOM: {market.tam_sam_som?.som}</p>
              <p><strong>Target Customer Profile:</strong> {market.target_audience}</p>
              <p><strong>Agent Reasoning:</strong> {market.reasoning}</p>
            </div>

            <div className="agent-detail-card">
              <h4>2. Competition Analysis Agent</h4>
              <p><strong>Subscore:</strong> {competition.score}/20 | <strong>Confidence:</strong> {competition.confidence}% ({competition.confidence_reason})</p>
              <p><strong>Competitor Matrix:</strong> {competition.competitor_landscape}</p>
              <p><strong>Differentiation:</strong> {competition.differentiation}</p>
              <p><strong>Agent Reasoning:</strong> {competition.reasoning}</p>
            </div>

            <div className="agent-detail-card">
              <h4>3. Financial Feasibility Agent</h4>
              <p><strong>Subscore:</strong> {financial.score}/20 | <strong>Confidence:</strong> {financial.confidence}% ({financial.confidence_reason})</p>
              <p><strong>Breakeven Projection:</strong> {financial.breakeven_projection}</p>
              <p><strong>Agent Reasoning:</strong> {financial.reasoning}</p>
            </div>

            <div className="agent-detail-card">
              <h4>4. Risk Assessment Agent</h4>
              <p><strong>Subscore:</strong> {risk.score}/20 | <strong>Confidence:</strong> {risk.confidence}% ({risk.confidence_reason})</p>
              <p><strong>Mitigation Strategies:</strong> {(risk.mitigation_strategies || []).join('; ')}</p>
              <p><strong>Agent Reasoning:</strong> {risk.reasoning}</p>
            </div>

            <div className="agent-detail-card">
              <h4>5. Growth Potential & Investor Readiness</h4>
              <p><strong>Subscore:</strong> {feasibility.score}/15 | <strong>Confidence:</strong> {feasibility.confidence}% ({feasibility.confidence_reason})</p>
              <p><strong>Scalability Assessment:</strong> {feasibility.scalability_factors}</p>
              
              {feasibility.investor_readiness && (
                <div className="investor-subcard">
                  <h5>Investor Readiness Matrix</h5>
                  <p><strong>Readiness Score:</strong> {feasibility.investor_readiness.investor_score}/100</p>
                  <p><strong>Recommended Funding Stage:</strong> {feasibility.investor_readiness.funding_stage_recommendation}</p>
                  <p><strong>Strengths:</strong> {feasibility.investor_readiness.strengths?.join(', ')}</p>
                  <p><strong>Weaknesses:</strong> {feasibility.investor_readiness.weaknesses?.join(', ')}</p>
                  <p><strong>Investment Risks:</strong> {feasibility.investor_readiness.investment_risks?.join(', ')}</p>
                  <p><strong>Funding Stage Reasoning:</strong> {feasibility.investor_readiness.reasoning}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'actions' && (
          <div className="actions-tab">
            <h3>Action Plan Recommendations</h3>
            <div className="recommendations-list">
              {actionPlan.map((item, idx) => (
                <div key={idx} className={`rec-item priority-${(item.priority || 'medium').toLowerCase()}`}>
                  <div className="rec-badge-row">
                    <span className="rec-category">{item.category?.toUpperCase()}</span>
                    <span className="rec-priority">{item.priority?.toUpperCase()} PRIORITY</span>
                  </div>
                  <p className="rec-text">{item.recommendation}</p>
                  <div className="rec-attribution">
                    RAG Framework Influence: <strong>{item.framework_source || 'Lean Startup'}</strong>
                  </div>
                </div>
              ))}
            </div>

            <div className="next-steps-container">
              <h3>Recommended Next Steps</h3>
              <ol className="next-steps-list">
                {nextSteps.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
