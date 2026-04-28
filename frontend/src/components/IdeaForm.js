import React, { useState } from 'react';
import '../styles/IdeaForm.css';
import { ideas } from '../services/api';

export default function IdeaForm({ onSubmitSuccess }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    problem_statement: '',
    target_market: '',
    proposed_solution: '',
    value_proposition: '',
    business_model: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await ideas.create(formData);
      console.log('Idea created:', response.data);
      setFormData({
        title: '',
        description: '',
        problem_statement: '',
        target_market: '',
        proposed_solution: '',
        value_proposition: '',
        business_model: ''
      });
      if (onSubmitSuccess) {
        onSubmitSuccess(response.data);
      }
    } catch (err) {
      const errorDetail = err.response?.data?.detail;
      if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else if (Array.isArray(errorDetail)) {
        setError(errorDetail.map(e => e.msg).join(', '));
      } else {
        setError('Error creating idea. Please check all fields and try again.');
      }
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="idea-form">
      <h2>Submit Your Business Idea</h2>

      <div className="form-group">
        <label>Business Idea Title *</label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          required
          placeholder="E.g., AI Email Manager"
        />
      </div>

      <div className="form-group">
        <label>Description *</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          required
          placeholder="Detailed description of your idea"
          rows="4"
        />
      </div>

      <div className="form-group">
        <label>Problem Statement *</label>
        <textarea
          name="problem_statement"
          value={formData.problem_statement}
          onChange={handleChange}
          required
          placeholder="What problem does this solve?"
          rows="3"
        />
      </div>

      <div className="form-group">
        <label>Target Market *</label>
        <input
          type="text"
          name="target_market"
          value={formData.target_market}
          onChange={handleChange}
          required
          placeholder="Who is your target customer?"
        />
      </div>

      <div className="form-group">
        <label>Proposed Solution *</label>
        <textarea
          name="proposed_solution"
          value={formData.proposed_solution}
          onChange={handleChange}
          required
          placeholder="How will you solve this problem?"
          rows="3"
        />
      </div>

      <div className="form-group">
        <label>Value Proposition *</label>
        <input
          type="text"
          name="value_proposition"
          value={formData.value_proposition}
          onChange={handleChange}
          required
          placeholder="What unique value do you provide?"
        />
      </div>

      <div className="form-group">
        <label>Business Model *</label>
        <input
          type="text"
          name="business_model"
          value={formData.business_model}
          onChange={handleChange}
          required
          placeholder="E.g., Freemium SaaS, Subscription, Marketplace"
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      <button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'Submit Idea for Analysis'}
      </button>
    </form>
  );
}
