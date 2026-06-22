import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '../components/Dashboard';
import { dashboard } from '../services/api';

// Mock the api
jest.mock('../services/api', () => ({
  dashboard: {
    getStats: jest.fn()
  }
}));

describe('Dashboard Component', () => {
  const mockStats = {
    total_ideas: 10,
    success_rate: 75.5,
    average_score: 8.2,
    total_analyzed: 8,
    total_users: 5,
    recent_activity: [
      {
        id: 1,
        title: 'Test Idea',
        status: 'completed',
        created_at: '2026-05-01T12:00:00Z'
      }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    dashboard.getStats.mockImplementation(() => new Promise(() => {}));
    render(<Dashboard />);
    expect(screen.getByText(/loading dashboard/i)).toBeInTheDocument();
  });

  test('renders error state on api failure', async () => {
    dashboard.getStats.mockRejectedValue(new Error('API Error'));
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/failed to load dashboard statistics/i)).toBeInTheDocument();
    });
  });

  test('renders dashboard statistics correctly', async () => {
    dashboard.getStats.mockResolvedValue({ data: mockStats });
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Dashboard Analytics')).toBeInTheDocument();
    });

    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('75.5%')).toBeInTheDocument();
    expect(screen.getByText('8.2')).toBeInTheDocument();
    expect(screen.getByText('Test Idea')).toBeInTheDocument();
    expect(screen.getByText('completed')).toBeInTheDocument();
  });
});
