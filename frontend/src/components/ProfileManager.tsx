import React, { useState } from 'react';
import TagInput from './TagInput';

interface Diner {
  id?: number;
  name: string;
  dislikes: string[];
  is_active: boolean;
  role?: string;
  invite_accepted?: boolean;
  user_id?: string;
}

interface ProfileManagerProps {
  diners: Diner[];
  onAddDiner: (diner: Diner) => void;
  onDeleteDiner: (id: number) => void;
  onUpdateDiner: (id: number, name: string, dislikes: string[]) => void;
  currentUserUid?: string;
  isHead: boolean;
}

const ProfileManager: React.FC<ProfileManagerProps> = ({ 
  diners, 
  onAddDiner, 
  onDeleteDiner, 
  onUpdateDiner,
  currentUserUid,
  isHead
}) => {
  const [name, setName] = useState('');
  const [dislikes, setDislikes] = useState<string[]>([]);
  
  // State to track which diner is being edited
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState('');
  const [editDislikes, setEditDislikes] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    onAddDiner({
      name: name.trim(),
      dislikes,
      is_active: true
    });

    // Reset form inputs
    setName('');
    setDislikes([]);
  };

  const startEdit = (diner: Diner) => {
    if (diner.id === undefined) return;
    setEditingId(diner.id);
    setEditName(diner.name);
    setEditDislikes(diner.dislikes);
  };

  const handleUpdateSubmit = (e: React.FormEvent, id: number) => {
    e.preventDefault();
    if (!editName.trim()) return;

    onUpdateDiner(id, editName.trim(), editDislikes);
    setEditingId(null);
  };

  return (
    <div className="profile-manager-container">
      <h3>Family Profile Manager</h3>
      
      {/* List existing members */}
      <div className="member-list">
        {diners.map((diner) => {
          const isCurrentUser = diner.user_id && diner.user_id === currentUserUid;
          const canEdit = isHead || isCurrentUser;
          const canDelete = isHead && diner.role !== 'head';
          const isEditing = editingId !== null && editingId === diner.id;

          if (isEditing && diner.id !== undefined) {
            return (
              <form 
                key={diner.id} 
                onSubmit={(e) => handleUpdateSubmit(e, diner.id!)}
                className="member-card editing-card"
                style={{ flexDirection: 'column', gap: '8px', alignItems: 'stretch' }}
              >
                <input 
                  type="text" 
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="diner-input"
                  style={{ fontSize: '0.85rem', padding: '6px' }}
                  required
                />
                <TagInput
                  tags={editDislikes}
                  onChange={setEditDislikes}
                  placeholder="Add a dislike..."
                />
                <div style={{ display: 'flex', gap: '5px', justifyContent: 'flex-end' }}>
                  <button type="submit" className="add-diner-btn" style={{ padding: '4px 8px', fontSize: '0.8rem' }}>Save</button>
                  <button 
                    type="button" 
                    className="demo-signin-btn" 
                    style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                    onClick={() => setEditingId(null)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            );
          }

          return (
            <div key={diner.id || diner.name} className="member-card">
              <div className="member-info" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <span className="member-name">
                  {diner.name} {isCurrentUser && <span style={{ fontSize: '0.75rem', color: '#ffb300' }}>(You)</span>}
                </span>
                <span className="member-dislikes-list" style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
                  Dislikes: {diner.dislikes.length > 0 ? diner.dislikes.join(', ') : 'None'}
                </span>
              </div>
              <div style={{ display: 'flex', gap: '5px', alignItems: 'center' }}>
                {canEdit && (
                  <button
                    onClick={() => startEdit(diner)}
                    className="demo-signin-btn"
                    style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                  >
                    Edit
                  </button>
                )}
                {canDelete && diner.id !== undefined && (
                  <button
                    onClick={() => onDeleteDiner(diner.id!)}
                    className="delete-btn"
                    aria-label={`Delete ${diner.name}`}
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Add new member form - only family head can add new members */}
      {isHead && (
        <form onSubmit={handleSubmit} className="add-member-form" style={{ marginTop: '15px' }}>
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
            <TagInput
              tags={dislikes}
              onChange={setDislikes}
              placeholder="Type a dislike and press Enter..."
            />
          </div>
          <button type="submit" className="submit-btn" style={{ marginTop: '5px' }}>
            Add Member
          </button>
        </form>
      )}
    </div>
  );
};

export default ProfileManager;