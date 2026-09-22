import { describe, it, vi, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';
import * as apiModule from './services/api';
import * as api from './services/api';
vi.mock('./services/api');

describe('App', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
  });

  it('renders the page title', async () => {
    render(<App />);
    expect(await screen.findByRole('heading', { name: 'Alumni Search' })).toBeInTheDocument();
  });

  it('renders search input and button', async () => {
    render(<App />);
    expect(await screen.findByPlaceholderText(/enter alumni name/i)).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: 'Search' })).toBeInTheDocument();
  });

  it('disables search button when input is empty', async () => {
    render(<App />);
    const searchButton = await screen.findByRole('button', { name: 'Search' });
    expect(searchButton).toBeDisabled();
  });

  it('enables search button when input has text', async () => {
    render(<App />);
    const input = await screen.findByPlaceholderText(/enter alumni name/i);
    const searchButton = await screen.findByRole('button', { name: 'Search' });
    fireEvent.change(input, { target: { value: 'Aman Sharma' } });
    expect(searchButton).not.toBeDisabled();
  });

  it('shows loading state during search', async () => {
    let resolveSearch;
    api.searchAlumni.mockImplementation(() => 
      new Promise((resolve) => { resolveSearch = resolve; })
    );

    render(<App />);
    const input = await screen.findByPlaceholderText(/enter alumni name/i);
    const searchButton = await screen.findByRole('button', { name: 'Search' });
    
    fireEvent.change(input, { target: { value: 'Aman Sharma' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(await screen.findByText('Searching...')).toBeInTheDocument();
    });
    expect(await screen.findByText('Searching alumni...')).toBeInTheDocument();

    resolveSearch([]);
    await waitFor(() => {
      expect(screen.queryByText('Searching...')).not.toBeInTheDocument();
    });
  });

  it('displays search results after successful search', async () => {
    const mockResults = [
      { name: 'Aman Sharma', title: 'Software Engineer', linkedin_url: 'https://linkedin.com/in/amansharma' },
      { name: 'Aman Sharma', title: 'Product Manager', linkedin_url: 'https://linkedin.com/in/amansharma2' }
    ];
    api.searchAlumni.mockResolvedValue(mockResults);

    render(<App />);
    const input = await screen.findByPlaceholderText(/enter alumni name/i);
    const searchButton = await screen.findByRole('button', { name: 'Search' });
    
    fireEvent.change(input, { target: { value: 'Aman Sharma' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(await screen.findByText('Search Results (2)')).toBeInTheDocument();
    });
    expect(await screen.findByText('Software Engineer')).toBeInTheDocument();
    expect(await screen.findByText('Product Manager')).toBeInTheDocument();
  });

  it('shows empty state when no results found', async () => {
    api.searchAlumni.mockResolvedValue([]);

    render(<App />);
    const input = await screen.findByPlaceholderText(/enter alumni name/i);
    const searchButton = await screen.findByRole('button', { name: 'Search' });
    
    fireEvent.change(input, { target: { value: 'Nonexistent Person' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(await screen.findByText(/no alumni found/i)).toBeInTheDocument();
    });
  });

  it('shows error state on search failure', async () => {
    api.searchAlumni.mockRejectedValue(new Error('External API Error'));

    render(<App />);
    const input = await screen.findByPlaceholderText(/enter alumni name/i);
    const searchButton = await screen.findByRole('button', { name: 'Search' });
    
    fireEvent.change(input, { target: { value: 'Test Name' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(await screen.findByRole('alert')).toHaveTextContent('External API Error');
    });
  });

  it('loads profile when result is clicked', async () => {
    const mockResults = [
      { name: 'Aman Sharma', title: 'Software Engineer', linkedin_url: 'https://linkedin.com/in/amansharma' }
    ];
    const mockProfile = {
      name: 'Aman Sharma',
      headline: 'Software Engineer at Tech Company',
      experience: [
        { role: 'Software Engineer', company: 'Tech Company' },
        { role: 'Junior Developer', company: 'Startup Inc' }
      ]
    };
    
    api.searchAlumni.mockResolvedValue(mockResults);
    api.getProfile.mockResolvedValue(mockProfile);

    render(<App />);
    const input = await screen.findByPlaceholderText(/enter alumni name/i);
    const searchButton = await screen.findByRole('button', { name: 'Search' });
    
    fireEvent.change(input, { target: { value: 'Aman Sharma' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(await screen.findByText('Software Engineer')).toBeInTheDocument();
    });

    const resultItem = await screen.findByText('Aman Sharma').closest('.result-item');
    fireEvent.click(resultItem);

    await waitFor(() => {
      expect(await screen.findByText('Loading profile...')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(await screen.findByText('Software Engineer at Tech Company')).toBeInTheDocument();
    });
    expect(await screen.findByText('Tech Company')).toBeInTheDocument();
    expect(await screen.findByText('Startup Inc')).toBeInTheDocument();
  });
});