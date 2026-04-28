import React, { useState, useEffect, useCallback } from 'react';
import '../styles/AnalysisResults.css';
import { analysis } from '../services/api';

export default function AnalysisResults({ ideaId }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchResults = useCallback(async () => {
    try {
      setLoading(true);
      const response = await analysis.getAnalysis(ideaId);
      setResults(response.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching results');
    } finally {
      setLoading(false);
    }
  }, [ideaId]);

  useEffect(() => {
    if (ideaId) {
      fetchResults();
    }
  }, [ideaId, fetchResults]);

  if (loading) {
    return <div className="analysis-loading">Loading analysis results...</div>;
  }

  if (error) {
    return <div className="analysis-error">Analysis not yet available. Triggering analysis...</div>;
  }

  if (!results) {
    return <div className="analysis-empty">No analysis results available</div>;
  }

  return (
    <div className="analysis-results">
      <h2>Analysis Results</h2>

      <div className="scores-grid">
        <div className="score-card">
          <h3>Overall Score</h3>
          <div className="score-value">{results.overall_score?.toFixed(1) || 'N/A'}</div>
          <p>/10</p>
        </div>

        <div className="score-card">
          <h3>Market</h3>
          <div className="score-value">{results.market_score?.toFixed(1) || 'N/A'}</div>
          <p>/10</p>
        </div>

        <div className="score-card">
          <h3>Feasibility</h3>
          <div className="score-value">{results.feasibility_score?.toFixed(1) || 'N/A'}</div>
          <p>/10</p>
        </div>

        <div className="score-card">
          <h3>Financial</h3>
          <div className="score-value">{results.financial_score?.toFixed(1) || 'N/A'}</div>
          <p>/10</p>
        </div>

        <div className="score-card">
          <h3>Risk</h3>
          <div className="score-value">{results.risk_score?.toFixed(1) || 'N/A'}</div>
          <p>/10</p>
        </div>
      </div>

      <div className="analysis-section">
        <h3>Strengths</h3>
        <p>{results.strengths || 'No strengths identified'}</p>
      </div>

      <div className="analysis-section">
        <h3>Weaknesses</h3>
        <p>{results.weaknesses || 'No weaknesses identified'}</p>
      </div>

      <div className="analysis-section">
        <h3>Market Analysis</h3>
        <p>{JSON.stringify(results.market_analysis)?.substring(0, 200) || 'N/A'}...</p>
      </div>

      <button onClick={fetchResults} className="refresh-button">
        Refresh Results
      </button>
    </div>
  );
}
