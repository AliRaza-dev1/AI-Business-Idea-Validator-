import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import App from '../App';
import * as api from '../services/api';

// Mock the API calls
jest.mock('../services/api', () => ({
    analysis: {
        triggerAnalysis: jest.fn()
    },
    ideas: {
        create: jest.fn()
    }
}));

describe('App Component', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders header, main form, and footer', () => {
        render(<App />);

        // Header
        expect(screen.getByRole('heading', { level: 1, name: /AI Business Idea Validator/i })).toBeInTheDocument();

        // Form component should be present (looking for the form header)
        expect(screen.getByText('Submit Your Business Idea')).toBeInTheDocument();

        // Footer
        expect(screen.getByText(/All rights reserved/i)).toBeInTheDocument();
    });

    it('does not show AnalysisResults initially', () => {
        render(<App />);
        // Look for AnalysisResults header
        expect(screen.queryByRole('heading', { name: 'Analysis Results' })).not.toBeInTheDocument();
    });

    it('shows AnalysisResults and triggers analysis on idea submission', async () => {
        // Setup mock responses
        api.ideas.create.mockResolvedValueOnce({ data: { id: 123 } });
        api.analysis.triggerAnalysis.mockResolvedValueOnce({});

        render(<App />);

        // Fill required form fields to enable submit
        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText(/E.g., AI Email Manager/i), 'My Idea');
        await user.type(screen.getByPlaceholderText(/Detailed description of your idea/i), 'A brilliant idea');
        await user.type(screen.getByPlaceholderText(/What problem does this solve\?/i), 'Big problem');
        await user.type(screen.getByPlaceholderText(/Who is your target customer\?/i), 'Everyone');
        await user.type(screen.getByPlaceholderText(/How will you solve this problem\?/i), 'Do this');
        await user.type(screen.getByPlaceholderText(/What unique value do you provide\?/i), 'Saves time');
        await user.type(screen.getByPlaceholderText(/E.g., Freemium SaaS/i), 'SaaS');

        // Submit form
        await user.click(screen.getByRole('button', { name: /Submit Idea/i }));

        // Verify API calls
        await waitFor(() => {
            expect(api.ideas.create).toHaveBeenCalledTimes(1);
        });

        await waitFor(() => {
            expect(api.analysis.triggerAnalysis).toHaveBeenCalledWith(123);
        });

        expect(await screen.findByText(/Analysis not yet available/i)).toBeInTheDocument();
    });
});
