import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import './styles/App.css';
import IdeaForm from './components/IdeaForm';
import AnalysisResults from './components/AnalysisResults';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import { analysis } from './services/api';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  
  return children;
};

function MainApp() {
  const [currentIdeaId, setCurrentIdeaId] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const { user, logout } = useAuth();

  const handleIdeaSubmit = async (idea) => {
    setCurrentIdeaId(idea.id);
    setAnalysisError('');
    
    // Trigger analysis
    try {
      console.log('[FRONTEND] Triggering analysis for idea:', idea.id);
      const response = await analysis.triggerAnalysis(idea.id);
      console.log('[FRONTEND] Analysis triggered successfully:', response);
    } catch (err) {
      console.error('[FRONTEND] Error triggering analysis:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to trigger analysis';
      setAnalysisError(errorMsg);
      console.error('[FRONTEND] Analysis trigger error details:', errorMsg);
    }
    
    setShowResults(true);
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>🚀 AI Business Idea Validator</h1>
            <p>Validate your business ideas with a multi-agent AI pipeline powered by GPT-4o</p>
          </div>
          <div className="header-auth">
            {user ? (
              <div className="user-info">
                <nav className="header-nav">
                  <Link to="/" className="nav-link">Submit Idea</Link>
                  <Link to="/dashboard" className="nav-link">Dashboard</Link>
                </nav>
                <span className="user-email">{user.email}</span>
                <button onClick={logout} className="logout-btn">Logout</button>
              </div>
            ) : (
              <div className="auth-links">
                <Link to="/login" className="login-link">Login</Link>
                <Link to="/register" className="register-link">Register</Link>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/" element={
            <ProtectedRoute>
              <>
                <section className="form-section">
                  <IdeaForm onSubmitSuccess={handleIdeaSubmit} />
                </section>

                {showResults && currentIdeaId && (
                  <section className="results-section">
                    <AnalysisResults 
                      ideaId={currentIdeaId} 
                      initialError={analysisError}
                      onClearError={() => setAnalysisError('')}
                    />
                  </section>
                )}
              </>
            </ProtectedRoute>
          } />
        </Routes>
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <p>© 2026 AI Business Idea Validator. All rights reserved.</p>
          <p className="ai-disclosure">
            ⚡ <strong>Powered by GPT-4o AI</strong> — Analyses are AI-generated for informational purposes only and do not constitute professional financial, legal, or investment advice.
          </p>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <MainApp />
      </Router>
    </AuthProvider>
  );
}

export default App;
