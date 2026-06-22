import { render, screen, fireEvent } from '@testing-library/react';
import { describe, test, expect, vi } from 'vitest';
import Login from '../Login';

// Mock Firebase functions
vi.mock('../../firebase', () => ({
    auth: {},
    googleProvider: {},
    signInWithPopup: vi.fn().mockResolvedValue({
        user: {
            uid: 'user123',
            email: 'user@example.com',
            displayName: 'Ryan B',
            getIdToken: () => Promise.resolve('mock-user123')
        }
    })
}));

describe('Login Component', () => {
    test('renders login buttons', () => {
        render(<Login onLoginSuccess={vi.fn()} />);
        expect(screen.getByRole('button', { name: /sign in with google/i})).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /demo sign in/i})).toBeInTheDocument();
    });

    test('clicking demo sign in triggers success callback with mock user', () => {
        const handleSuccess = vi.fn();
        render(<Login onLoginSuccess={handleSuccess} />);

        fireEvent.click(screen.getByRole('button', { name: /demo sign in/i }));

        expect(handleSuccess).toHaveBeenCalledWith({
            uid: 'user123',
            email: 'mock-user123@example.com',
            displayName: 'Mock User',
            token: 'mock-user123'
        });
    });

    test('clicking goot sign in triggers firebase authentication', async () => {
        const handleSuccess = vi.fn();
        render(<Login onLoginSuccess={handleSuccess} />);

        fireEvent.click(screen.getByRole('button', { name: /sign in with google/i }));

        // Wait for the promise to resolve
        await vi.waitFor(() => {
            expect(handleSuccess).toHaveBeenCalledWith({
                uid: 'user123',
                email: 'user@example.com',
                displayName: 'Ryan B',
                token: 'mock-user123'
            });
        });
    });

});