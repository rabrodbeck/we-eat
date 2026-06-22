import React, { useState } from 'react';

interface Diner {
  name: string;
  dislikes: string[];
  is_active: boolean;
}

interface ProfileManagerProps {
  diners: Diner[];
  onAddDiner: (diner: Diner) => void;
  onDeleteDiner: (name: string) => void;
}

const ProfileManager: React.FC<ProfileManagerProps> = ({ diners, onAddDiner, onDeleteDiner }) => {
  const [name, setName] = useState('');
  const [dislikesInput, setDislikesInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    // Parse comma-separated dislikes list
    const dislikes = dislikesInput
      .split(',')
      .map(item => item.trim())
      .filter(item => item !== '');

    onAddDiner({
      name: name.trim(),
      dislikes,
      is_active: true
    });

    // Reset form inputs
    setName('');
    setDislikesInput('');
  };

  return (
    <div className="profile-manager-container">
      <h3>Family Profile Manager</h3>
      
      {/* List existing members */}
      <div className="member-list">
        {diners.map((diner) => (
          <div key={diner.name} className="member-card">
            <div className="member-info">
              <span className="member-name">{diner.name}</span>
              <span className="member-dislikes-list">
                {diner.dislikes.length > 0 ? diner.dislikes.join(', ') : 'None'}
              </span>
            </div>
            <button
              onClick={() => onDeleteDiner(diner.name)}
              className="delete-btn"
              aria-label={`Delete ${diner.name}`}
            >
              Delete
            </button>
          </div>
        ))}
      </div>

      {/* Add new member form */}
      <form onSubmit={handleSubmit} className="add-member-form">
        <h4>Add Family Member</h4>
        <div className="form-group">
          <input
            type="text"
            placeholder="Enter name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <input
            type="text"
            placeholder="Enter dislikes (comma separated)"
            value={dislikesInput}
            onChange={(e) => setDislikesInput(e.target.value)}
          />
        </div>
        <button type="submit" className="submit-btn">
          Add Member
        </button>
      </form>
    </div>
  );
};

export default ProfileManager;