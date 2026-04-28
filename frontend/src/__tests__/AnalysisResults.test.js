import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import AnalysisResults from '../components/AnalysisResults';
import { analysis } from '../services/api';

jest.mock('../services/api', () => ({
    analysis: {
        getAnalysis: jest.fn()
    }
}));

describe('AnalysisResults Component', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('displays empty state when no ideaId provided', () => {
        const { container } = render(<AnalysisResults ideaId={null} />);
        expect(container).toHaveTextContent('Loading analysis results...');
    });

    it('shows loading state initially', () => {
        // Delay resolution to catch loading state
        analysis.getAnalysis.mockImplementation(() => new Promise(() => { }));
        render(<AnalysisResults ideaId={1} />);

        expect(screen.getByText('Loading analysis results...')).toBeInTheDocument();
    });

    it('renders all scores and details when data is returned', async () => {
        const mockData = {
            overall_score: 8.5,
            market_score: 9.0,
            feasibility_score: 7.5,
            financial_score: 8.0,
            risk_score: 6.5,
            strengths: 'Good team',
            weaknesses: 'High costs',
            market_analysis: 'Growing TAM'
        };

        analysis.getAnalysis.mockResolvedValueOnce({ data: mockData });

        render(<AnalysisResults ideaId={1} />);

        // Wait for load to finish
        await waitFor(() => {
            expect(screen.queryByText('Loading analysis results...')).not.toBeInTheDocument();
        });

        // Check titles
        expect(screen.getByText('Analysis Results')).toBeInTheDocument();
        expect(screen.getByText('Overall Score')).toBeInTheDocument();

        // Check score values
        expect(screen.getByText('8.5')).toBeInTheDocument();
        expect(screen.getByText('9.0')).toBeInTheDocument();
        expect(screen.getByText('7.5')).toBeInTheDocument();

        // Check paragraphs
        expect(screen.getByText('Good team')).toBeInTheDocument();
        expect(screen.getByText('High costs')).toBeInTheDocument();

        // Market analysis converts object to string, then substrings
        expect(screen.getByText(/"Growing TAM"/i)).toBeInTheDocument();
    });

    it('refreshes results when refresh button clicked', async () => {
        const mockData1 = { overall_score: 7.0 };
        const mockData2 = { overall_score: 9.9 };

        analysis.getAnalysis
            .mockResolvedValueOnce({ data: mockData1 })
            .mockResolvedValueOnce({ data: mockData2 });

        render(<AnalysisResults ideaId={1} />);

        await screen.findByText('7.0');

        const refreshBtn = screen.getByRole('button', { name: 'Refresh Results' });
        const user = userEvent.setup();
        await user.click(refreshBtn);

        expect(analysis.getAnalysis).toHaveBeenCalledTimes(2);
        expect(await screen.findByText('9.9')).toBeInTheDocument();
    });

    it('handles error gracefully when API fails', async () => {
        analysis.getAnalysis.mockRejectedValueOnce({
            response: { data: { detail: 'Not found' } }
        });

        render(<AnalysisResults ideaId={1} />);

        await waitFor(() => {
            // Because error causes the "Analysis not yet available..." text:
            expect(screen.getByText(/Analysis not yet available/i)).toBeInTheDocument();
        });
    });
});
