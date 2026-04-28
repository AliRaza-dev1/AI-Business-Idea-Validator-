import React, { useState } from 'react';
import './styles/App.css';
import IdeaForm from './components/IdeaForm';
import AnalysisResults from './components/AnalysisResults';
import { analysis } from './services/api';

function App() {
  const [currentIdeaId, setCurrentIdeaId] = useState(null);
  const [showResults, setShowResults] = useState(false);

  const handleIdeaSubmit = async (idea) => {
    setCurrentIdeaId(idea.id);
    
    // Trigger analysis
    try {
      await analysis.triggerAnalysis(idea.id);
      console.log('Analysis triggered for idea:', idea.id);
    } catch (err) {
      console.error('Error triggering analysis:', err);
    }
    
    setShowResults(true);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🚀 AI Business Idea Validator</h1>
        <p>Validate your business ideas using artificial intelligence</p>
      </header>

      <main className="app-main">
        <section className="form-section">
          <IdeaForm onSubmitSuccess={handleIdeaSubmit} />
        </section>

        {showResults && currentIdeaId && (
          <section className="results-section">
            <AnalysisResults ideaId={currentIdeaId} />
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; 2026 AI Business Idea Validator. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
