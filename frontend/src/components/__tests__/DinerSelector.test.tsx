import { render, screen, fireEvent } from '@testing-library/react';
import { describe, test, expect, vi } from 'vitest';
import DinerSelector from '../DinerSelector';

const mockDiners = [
  { name: 'Olivia', dislikes: ['pizza'], is_active: true },
  { name: 'Peyton', dislikes: ['mexican'], is_active: false }
];

describe('DinerSelector Component', () => {
  test('renders all diner names', () => {
    render(<DinerSelector diners={mockDiners} onToggleDiners={vi.fn()} />);
    expect(screen.getByText('Olivia')).toBeInTheDocument();
    expect(screen.getByText('Peyton')).toBeInTheDocument();
  });

  test('checkboxes have correct initial checked state', () => {
    render(<DinerSelector diners={mockDiners} onToggleDiners={vi.fn()} />);
    const oliviaCheckbox = screen.getByLabelText('Olivia') as HTMLInputElement;
    const peytonCheckbox = screen.getByLabelText('Peyton') as HTMLInputElement;
    
    expect(oliviaCheckbox.checked).toBe(true);
    expect(peytonCheckbox.checked).toBe(false);
  });

  test('toggling a checkbox fires the callback with the updated active list', () => {
    const handleToggle = vi.fn();
    render(<DinerSelector diners={mockDiners} onToggleDiners={handleToggle} />);
    
    const peytonCheckbox = screen.getByLabelText('Peyton');
    fireEvent.click(peytonCheckbox);
    
    // Peyton was inactive, toggling should make them active.
    // The callback should receive ["Olivia", "Peyton"]
    expect(handleToggle).toHaveBeenCalledWith(['Olivia', 'Peyton']);
  });
}); 