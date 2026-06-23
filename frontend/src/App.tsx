// MODIFY: frontend/src/App.tsx
import { useState, useEffect } from 'react';
import Login from './components/Login';
import ProfileManager from './components/ProfileManager';
import DinerSelector from './components/DinerSelector';
import ChatAgent from './components/ChatAgent';

interface Diner {
  id?: number;
  name: string;
  dislikes: string[];
  is_active: boolean;
  email?: string;
  invite_token?: string;
  invite_accepted?: boolean;
  role?: string;
}

interface Message {
  sender: 'user' | 'agent';
  text: string;
}

interface UserSession {
  uid: string;
  email: string | null;
  displayName: string | null;
  token: string;
}

interface Family {
  id: string;
  family_name: string;
  created_by: string;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

function App() {
  const [user, setUser] = useState<UserSession | null>(null);
  const [family, setFamily] = useState<Family | null>(null);
  const [diners, setDiners] = useState<Diner[]>([]);
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'agent', text: 'Hello! I am WeEat, your meal planner assistant. Who is eating today, and what can I suggest for you?' }
  ]);
  const [loading, setLoading] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [invitingDinerId, setInvitingDinerId] = useState<number | null>(null);
  const [generatedInviteLink, setGeneratedInviteLink] = useState<string | null>(null);

  const USER_LAT = 42.0234;
  const USER_LON = -88.1837;

  // 1. Check for invite token in URL query params on startup
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    if (token) {
      sessionStorage.setItem('invite_token', token);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  // 2. Fetch Family details and Diners on login
  useEffect(() => {
    if (!user) return;
    processLoginFlow();
  }, [user]);

  const processLoginFlow = async () => {
    if (!user) return;
    
    // Check if there's a pending invite token in session storage
    const pendingToken = sessionStorage.getItem('invite_token');
    if (pendingToken) {
      try {
        const acceptRes = await fetch(`${BACKEND_URL}/api/family/accept-invite`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${user.token}`
          },
          body: JSON.stringify({ invite_token: pendingToken })
        });
        if (acceptRes.ok) {
          sessionStorage.removeItem('invite_token');
          alert("Successfully joined the family!");
        }
      } catch (err) {
        console.error("Error accepting invite:", err);
      }
    }

    fetchFamilyAndDiners();
  };

  const fetchFamilyAndDiners = async () => {
    if (!user) return;
    try {
      const famRes = await fetch(`${BACKEND_URL}/api/family`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      if (famRes.ok) {
        const famData = await famRes.json();
        setFamily(famData);
      }

      const dinersRes = await fetch(`${BACKEND_URL}/api/diners`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      if (dinersRes.ok) {
        const dinersData = await dinersRes.json();
        setDiners(dinersData.map((d: any) => ({ ...d, is_active: true })));
      }
    } catch (err) {
      console.error('Failed to fetch data:', err);
    }
  };

  // Add Diner Profile
  const handleAddDiner = async (newDiner: Diner) => {
    if (!user) return;
    try {
      const res = await fetch(`${BACKEND_URL}/api/diners`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${user.token}`
        },
        body: JSON.stringify(newDiner)
      });
      if (res.ok) {
        fetchFamilyAndDiners();
      }
    } catch (err) {
      console.error('Failed to add diner:', err);
    }
  };

  // Delete Diner Profile
  const handleDeleteDiner = async (name: string) => {
    if (!user) return;
    try {
      const res = await fetch(`${BACKEND_URL}/api/diners/${name}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${user.token}` }
      });
      if (res.ok) {
        fetchFamilyAndDiners();
      }
    } catch (err) {
      console.error('Failed to delete diner:', err);
    }
  };

  // Toggle Active Diner
  const handleToggleDiners = (activeNames: string[]) => {
    setDiners(prev =>
      prev.map(d => ({ ...d, is_active: activeNames.includes(d.name) }))
    );
  };

  // Generate invite link for a diner profile
  const handleInviteDiner = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || invitingDinerId === null || !inviteEmail.trim()) return;
    try {
      const res = await fetch(`${BACKEND_URL}/api/family/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${user.token}`
        },
        body: JSON.stringify({ member_id: invitingDinerId, email: inviteEmail.trim() })
      });
      if (res.ok) {
        const data = await res.json();
        const fullInviteLink = `${window.location.origin}${data.invite_link}`;
        setGeneratedInviteLink(fullInviteLink);
        setInviteEmail('');
        fetchFamilyAndDiners();
      }
    } catch (err) {
      console.error('Failed to invite member:', err);
    }
  };

  // Send message to AI Agent
  const handleSendMessage = async (text: string) => {
    if (!user) return;
    setMessages(prev => [...prev, { sender: 'user', text }]);
    setLoading(true);
    try {
      const activeNames = diners.filter(d => d.is_active).map(d => d.name);
      const res = await fetch(`${BACKEND_URL}/api/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${user.token}`
        },
        body: JSON.stringify({
          query: text,
          active_diner_names: activeNames,
          user_lat: USER_LAT,
          user_lon: USER_LON,
          max_distance_miles: 15.0
        })
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, { sender: 'agent', text: data.recommendation }]);
      } else {
        setMessages(prev => [...prev, { sender: 'agent', text: 'Sorry, I ran into an error generating a suggestion.' }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'agent', text: 'Error connecting to the recommendation service.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = () => {
    setUser(null);
    setFamily(null);
    setDiners([]);
    setGeneratedInviteLink(null);
    setInvitingDinerId(null);
    setMessages([
      { sender: 'agent', text: 'Hello! I am WeEat, your meal planner assistant. Who is eating today, and what can I suggest for you?' }
    ]);
  };

  const isHead = family && user && family.created_by === user.uid;

  if (!user) {
    return <Login onLoginSuccess={setUser} />;
  }

  return (
    <div className="app-layout">
      {/* Sidebar Controls */}
      <aside className="sidebar glass-panel">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ margin: '0' }}>WeEat</h2>
            <button onClick={handleSignOut} className="demo-signin-btn" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
              Sign Out
            </button>
          </div>
          
          {family && (
            <div className="family-badge" style={{ fontSize: '0.9rem', padding: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '6px' }}>
              <div><strong>Family Dashboard:</strong> {family.family_name}</div>
              <div style={{ fontSize: '0.75rem', color: '#aaa', marginTop: '4px' }}>
                Role: {isHead ? 'Family Head' : 'Family Member'}
              </div>
            </div>
          )}

          {/* Allow Head of Family to invite diners */}
          {isHead && (
            <div style={{ marginTop: '10px', padding: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 'bold', marginBottom: '5px' }}>Invite a Member to Login:</div>
              <form onSubmit={handleInviteDiner} style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <select 
                  className="diner-input" 
                  style={{ fontSize: '0.8rem', padding: '4px' }}
                  onChange={(e) => setInvitingDinerId(Number(e.target.value) || null)}
                  value={invitingDinerId || ''}
                >
                  <option value="">Select diner profile...</option>
                  {diners.filter(d => !d.invite_accepted && d.role !== 'head').map(d => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
                <input 
                  type="email" 
                  placeholder="Invite Email" 
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  className="diner-input"
                  style={{ fontSize: '0.8rem', padding: '6px' }}
                />
                <button type="submit" className="add-diner-btn" style={{ padding: '6px', fontSize: '0.8rem' }}>
                  Generate Invite Link
                </button>
              </form>
              {generatedInviteLink && (
                <div style={{ marginTop: '8px', padding: '6px', background: 'rgba(255, 179, 0, 0.1)', borderRadius: '4px', fontSize: '0.75rem' }}>
                  <div><strong>Send this link:</strong></div>
                  <input 
                    type="text" 
                    readOnly 
                    value={generatedInviteLink} 
                    onClick={(e) => (e.target as HTMLInputElement).select()}
                    style={{ width: '100%', fontSize: '0.7rem', padding: '4px', background: '#000', border: 'none', color: '#fff', marginTop: '4px' }}
                  />
                </div>
              )}
            </div>
          )}
        </div>

        <hr style={{ borderColor: 'rgba(255,255,255,0.1)', margin: '20px 0' }} />

        <DinerSelector diners={diners} onToggleDiners={handleToggleDiners} />
        
        <hr style={{ borderColor: 'rgba(255,255,255,0.1)', margin: '20px 0' }} />
        
        <ProfileManager diners={diners} onAddDiner={handleAddDiner} onDeleteDiner={handleDeleteDiner} />
      </aside>

      {/* Chat Area */}
      <main className="chat-area">
        <ChatAgent messages={messages} onSendMessage={handleSendMessage} loading={loading} />
      </main>
    </div>
  );
}

export default App;