import React from 'react';

interface Diner {
  name: string;
  dislikes: string[];
  is_active: boolean;
}

interface DinerSelectorProps {
  diners: Diner[];
  onToggleDiners: (activeNames: string[]) => void;
}

const DinerSelector: React.FC<DinerSelectorProps> = ({ diners, onToggleDiners }) => {
  const handleCheckboxChange = (name: string, checked: boolean) => {
    const activeNames = diners
      .map((d) => {
        if (d.name === name) {
          return { ...d, is_active: checked };
        }
        return d;
      })
      .filter((d) => d.is_active)
      .map((d) => d.name);
      
    onToggleDiners(activeNames);
  };

  return (
    <div className="diner-selector-panel">
      <h3>Who is eating?</h3>
      <div className="diner-list">
        {diners.map((diner) => (
          <div key={diner.name} className="diner-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
            <label htmlFor={`checkbox-${diner.name}`} className="diner-label">
              <input
                id={`checkbox-${diner.name}`}
                type="checkbox"
                checked={diner.is_active}
                onChange={(e) => handleCheckboxChange(diner.name, e.target.checked)}
              />
              <span>{diner.name}</span>
            </label>
            <span className="diner-dislikes" style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
              {diner.dislikes.length > 0 ? `Dislikes: ${diner.dislikes.join(', ')}` : 'No dislikes'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DinerSelector;