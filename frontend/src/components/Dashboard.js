import React, { useState, useEffect } from 'react';
import { dashboard, ideas as ideasApi, analysis } from '../services/api';
import '../styles/Dashboard.css';
import { useAuth } from '../contexts/AuthContext';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [advancedStats, setAdvancedStats] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [ideasList, setIdeasList] = useState([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Comparison state variables
  const [compareA, setCompareA] = useState('');
  const [compareB, setCompareB] = useState('');
  const [comparisonResult, setComparisonResult] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState('');

  const { user } = useAuth();

  useEffect(() => {
    fetchData();
  }, [search, statusFilter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Use allSettled so one failure doesn't crash the whole dashboard
      const [statsRes, advStatsRes, recsRes, ideasRes] = await Promise.allSettled([
        dashboard.getStats(),
        dashboard.getAdvancedStats(),
        ideasApi.getRecommendations(),
        ideasApi.getAll(0, 100, search, statusFilter)
      ]);

      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value.data);
      } else {
        setError('Failed to load dashboard stats.');
      }

      if (advStatsRes.status === 'fulfilled') {
        setAdvancedStats(advStatsRes.value.data);
      }

      if (recsRes.status === 'fulfilled') {
        setRecommendations(recsRes.value.data.recommendations || []);
      }
      // Silently skip recommendations if unavailable (requires valid OpenAI key)

      if (ideasRes.status === 'fulfilled') {
        setIdeasList(ideasRes.value.data || []);
      }
    } catch (err) {
      setError('Failed to load dashboard data.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = async () => {
    if (!compareA || !compareB) {
      setCompareError('Please select two ideas to compare.');
      return;
    }
    if (compareA === compareB) {
      setCompareError('Please select two different ideas.');
      return;
    }

    try {
      setCompareLoading(true);
      setCompareError('');
      const res = await analysis.compareAnalyses(compareA, compareB);
      setComparisonResult(res.data);
    } catch (err) {
      console.error(err);
      setCompareError('Failed to compare ideas. Verify both are analyzed.');
    } finally {
      setCompareLoading(false);
    }
  };

  if (loading && !stats) return <div className="dashboard-loading">Loading dashboard...</div>;
  if (error) return <div className="dashboard-error">{error}</div>;
  if (!stats) return <div className="dashboard-empty">No data available</div>;

  const completedIdeas = ideasList.filter(idea => idea.status === 'completed');

  return (
    <div className="dashboard-container">
      <h2>Dashboard Analytics {user?.role === 'admin' ? '(Admin View)' : ''}</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_ideas}</div>
          <div className="stat-label">Total Ideas</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.total_analyzed}</div>
          <div className="stat-label">Total Analyzed</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.average_score}/100</div>
          <div className="stat-label">Average Viability Score</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.average_confidence}%</div>
          <div className="stat-label">Average Confidence</div>
        </div>
      </div>

      {/* Advanced AI Metrics Summary */}
      <div className="dashboard-ai-summary">
        <h3>AI Business Intelligence Insights</h3>
        <div className="stats-grid">
          <div className="stat-card highlight-rated">
            <div className="stat-label-large">🏆 Highest Rated Business Idea</div>
            <div className="stat-value-text">{stats.highest_rated_idea || 'N/A'}</div>
          </div>
          <div className="stat-card highlight-risky">
            <div className="stat-label-large">⚠️ Most Risky Business Idea</div>
            <div className="stat-value-text">{stats.most_risky_idea || 'N/A'}</div>
          </div>
        </div>
      </div>

      {/* RAG Comparison Workspace */}
      {completedIdeas.length >= 2 && (
        <div className="comparison-workspace">
          <h3>AI Business Idea Comparison Workspace</h3>
          <p>Compare two of your analyzed business ideas side-by-side to review score deltas and opportunities.</p>
          
          <div className="comparison-inputs">
            <div className="input-group">
              <label>Select Idea A (Base):</label>
              <select value={compareA} onChange={e => setCompareA(e.target.value)}>
                <option value="">-- Choose Idea A --</option>
                {completedIdeas.map(idea => (
                  <option key={idea.id} value={idea.id}>{idea.title}</option>
                ))}
              </select>
            </div>
            
            <div className="input-group">
              <label>Select Idea B (Target):</label>
              <select value={compareB} onChange={e => setCompareB(e.target.value)}>
                <option value="">-- Choose Idea B --</option>
                {completedIdeas.map(idea => (
                  <option key={idea.id} value={idea.id}>{idea.title}</option>
                ))}
              </select>
            </div>
            
            <button onClick={handleCompare} disabled={compareLoading} className="compare-action-btn">
              {compareLoading ? 'Comparing...' : '⚖️ Compare Ideas'}
            </button>
          </div>

          {compareError && <div className="compare-error-msg">{compareError}</div>}

          {comparisonResult && (
            <div className="comparison-results-panel">
              <h4>Comparison Report: {comparisonResult.idea_a.title} vs {comparisonResult.idea_b.title}</h4>
              
              <div className="compare-scores-row">
                <div className="compare-score-box">
                  <div className="label">{comparisonResult.idea_a.title}</div>
                  <div className="val">{comparisonResult.comparison.previous_score}/100</div>
                </div>
                <div className="compare-score-box">
                  <div className="label">{comparisonResult.idea_b.title}</div>
                  <div className="val">{comparisonResult.comparison.current_score}/100</div>
                </div>
                <div className="compare-score-box delta-box">
                  <div className="label">Score Difference</div>
                  <div className={`val delta-${comparisonResult.comparison.score_difference >= 0 ? 'positive' : 'negative'}`}>
                    {comparisonResult.comparison.score_difference >= 0 ? '+' : ''}{comparisonResult.comparison.score_difference}
                  </div>
                </div>
              </div>

              <div className="compare-details">
                <p><strong>Verdict Summary:</strong> {comparisonResult.comparison.key_changes}</p>
                
                <div className="compare-lists-grid">
                  <div className="compare-list-col">
                    <h5>New Opportunities in {comparisonResult.idea_b.title}</h5>
                    <ul>
                      {comparisonResult.comparison.new_opportunities.map((opp, i) => (
                        <li key={i}>{opp}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="compare-list-col">
                    <h5>New Risks in {comparisonResult.idea_b.title}</h5>
                    <ul>
                      {comparisonResult.comparison.new_risks.map((risk, i) => (
                        <li key={i}>{risk}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {advancedStats && (
        <div className="advanced-analytics">
          <h3>Viability Score Distributions</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{advancedStats.average_subscores.market}</div>
              <div className="stat-label">Avg Market Score (out of 25)</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{advancedStats.average_subscores.financial}</div>
              <div className="stat-label">Avg Financial Score (out of 20)</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{advancedStats.score_distribution?.['excellent (85-100)'] ?? 0}</div>
              <div className="stat-label">Highly Viable Ideas (≥85)</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{advancedStats.score_distribution?.['poor (<50)'] ?? 0}</div>
              <div className="stat-label">Challenging Ideas (&lt;50)</div>
            </div>
          </div>
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="recommendations-section">
          <h3>Advanced AI Recommendations (Based on your history)</h3>
          <div className="recs-grid" style={{display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))'}}>
            {recommendations.map((rec, index) => (
              <div key={index} className="rec-card" style={{padding: '1rem', border: '1px solid #ddd', borderRadius: '8px', background: '#f9f9f9'}}>
                <h4>{rec.title}</h4>
                <p><strong>Description:</strong> {rec.description}</p>
                <p><strong>Why:</strong> {rec.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="recent-activity" style={{marginTop: '2rem'}}>
        <h3>Your Ideas (Search & Filter)</h3>
        
        <div className="filters" style={{display: 'flex', gap: '1rem', marginBottom: '1rem'}}>
          <input 
            type="text" 
            placeholder="Search ideas..." 
            value={search} 
            onChange={e => setSearch(e.target.value)}
            style={{padding: '0.5rem', flex: 1}}
          />
          <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} style={{padding: '0.5rem'}}>
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="analyzing">Analyzing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        {ideasList.length > 0 ? (
          <ul className="activity-list">
            {ideasList.map(idea => (
              <li key={idea.id} className="activity-item">
                <div className="activity-title">{idea.title} - <small>{idea.description.substring(0, 70)}...</small></div>
                <div className="activity-meta">
                  <span className={`status-badge status-${idea.status}`}>
                    {idea.status}
                  </span>
                  <span className="activity-date">
                    {new Date(idea.created_at).toLocaleDateString()}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>No ideas found matching your search criteria.</p>
        )}
      </div>
    </div>
  );
}
