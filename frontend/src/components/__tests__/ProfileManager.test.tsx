import { render, screen, fireEvent } from '@testing-library/react';
import { describe, test, expect, vi } from 'vitest';
import ProfileManager from '../ProfileManager';

const mockDiners = [
  { name: 'Olivia', dislikes: ['pizza', 'sushi'], is_active: true },
  { name: 'Peyton', dislikes: ['mexican'], is_active: false }
];

describe('ProfileManager Component', () => {
  test('renders list of family members and their dislikes', () => {
    render(<ProfileManager diners={mockDiners} onAddDiner={vi.fn()} onDeleteDiner={vi.fn()} />);
    
    expect(screen.getByText('Olivia')).toBeInTheDocument();
    expect(screen.getByText('pizza, sushi')).toBeInTheDocument();
    
    expect(screen.getByText('Peyton')).toBeInTheDocument();
    expect(screen.getByText('mexican')).toBeInTheDocument();
  });

  test('submitting the form calls onAddDiner with input values', () => {
    const handleAdd = vi.fn();
    render(<ProfileManager diners={mockDiners} onAddDiner={handleAdd} onDeleteDiner={vi.fn()} />);
    
    // Fill in the form
    fireEvent.change(screen.getByPlaceholderText('Enter name'), { target: { value: 'Ryan' } });
    fireEvent.change(screen.getByPlaceholderText('Enter dislikes (comma separated)'), { target: { value: 'onions, mushrooms' } });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /add member/i }));
    
    expect(handleAdd).toHaveBeenCalledWith({
      name: 'Ryan',
      dislikes: ['onions', 'mushrooms'],
      is_active: true
    });
  });

  test('clicking delete calls onDeleteDiner with diner name', () => {
    const handleDelete = vi.fn();
    render(<ProfileManager diners={mockDiners} onAddDiner={vi.fn()} onDeleteDiner={handleDelete} />);
    
    // Click delete next to Olivia
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]); // First delete button is for Olivia
    
    expect(handleDelete).toHaveBeenCalledWith('Olivia');
  });
});