import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import IdeaForm from '../components/IdeaForm';
import { ideas } from '../services/api';

// Mock the API Call
jest.mock('../services/api', () => ({
    ideas: {
        create: jest.fn()
    }
}));

describe('IdeaForm Component', () => {
    const mockOnSubmitSuccess = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    const fillForm = async (user) => {
        await user.type(screen.getByPlaceholderText(/E.g., AI Email Manager/i), 'Test Title');
        await user.type(screen.getByPlaceholderText(/Detailed description of your idea/i), 'Test Desc');
        await user.type(screen.getByPlaceholderText(/What problem does this solve\?/i), 'Test Prob');
        await user.type(screen.getByPlaceholderText(/Who is your target customer\?/i), 'Test Market');
        await user.type(screen.getByPlaceholderText(/How will you solve this problem\?/i), 'Test Solution');
        await user.type(screen.getByPlaceholderText(/What unique value do you provide\?/i), 'Test Value');
        await user.type(screen.getByPlaceholderText(/E.g., Freemium SaaS/i), 'Test Model');
    };

    it('renders all required form fields by checking placeholders', () => {
        render(<IdeaForm onSubmitSuccess={mockOnSubmitSuccess} />);

        expect(screen.getByPlaceholderText(/E.g., AI Email Manager/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Detailed description of your idea/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/What problem does this solve\?/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Who is your target customer\?/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/How will you solve this problem\?/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/What unique value do you provide\?/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/E.g., Freemium SaaS/i)).toBeInTheDocument();

        expect(screen.getByRole('button', { name: 'Submit Idea for Analysis' })).toBeInTheDocument();
    });

    it('submits form successfully and calls API and callback', async () => {
        const mockIdeaResponse = { id: 1, title: 'Test Title' };
        ideas.create.mockResolvedValueOnce({ data: mockIdeaResponse });

        render(<IdeaForm onSubmitSuccess={mockOnSubmitSuccess} />);
        const user = userEvent.setup();

        await fillForm(user);

        const submitBtn = screen.getByRole('button', { name: 'Submit Idea for Analysis' });
        await user.click(submitBtn);

        await waitFor(() => {
            expect(ideas.create).toHaveBeenCalledWith({
                title: 'Test Title',
                description: 'Test Desc',
                problem_statement: 'Test Prob',
                target_market: 'Test Market',
                proposed_solution: 'Test Solution',
                value_proposition: 'Test Value',
                business_model: 'Test Model'
            });
        });

        expect(mockOnSubmitSuccess).toHaveBeenCalledWith(mockIdeaResponse);
        expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });

    it('handles API string error properly', async () => {
        ideas.create.mockRejectedValueOnce({
            response: { data: { detail: 'Title already exists' } }
        });

        render(<IdeaForm onSubmitSuccess={mockOnSubmitSuccess} />);
        const user = userEvent.setup();
        await fillForm(user);

        await user.click(screen.getByRole('button', { name: 'Submit Idea for Analysis' }));

        expect(await screen.findByText('Title already exists')).toBeInTheDocument();
        expect(mockOnSubmitSuccess).not.toHaveBeenCalled();
    });

    it('handles API array error mapping properly', async () => {
        ideas.create.mockRejectedValueOnce({
            response: { data: { detail: [{ msg: 'Field required' }, { msg: 'Too short' }] } }
        });

        render(<IdeaForm onSubmitSuccess={mockOnSubmitSuccess} />);
        const user = userEvent.setup();
        await fillForm(user);

        await user.click(screen.getByRole('button', { name: 'Submit Idea for Analysis' }));

        expect(await screen.findByText('Field required, Too short')).toBeInTheDocument();
    });
});
