import { useState, useEffect } from 'react';
import Login from './components/Login';
import ProfileManager from './components/ProfileManager';
import DinerSelector from './components/DinerSelector';
import ChatAgent from './components/ChatAgent';

interface Diner {
  name: string;
  dislikes: string[];
  is_active: boolean;
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

const BACKEND_URL = 'http://127.0.0.1:8000';

function App() {
  const [user, setUser] = useState<UserSession | null>(null);
  const [diners, setDiners] = useState<Diner[]>([]);
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'agent', text: 'Hello! I am WeEat, your meal planner assistant. Who is eating today, and what can I suggest for you?' }
  ]);
  const [loading, setLoading] = useState(false);
  // Coordinates centered around Streamwood, IL
  const USER_LAT = 42.0234;
  const USER_LON = -88.1837;
  // 1. Fetch Diner Profiles when logged in
  useEffect(() => {
    if (!user) return;
    fetchDiners();
  }, [user]);
  const fetchDiners = async () => {
    if (!user) return;
    try {
      const res = await fetch(`${BACKEND_URL}/api/diners`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setDiners(data.map((d: any) => ({ ...d, is_active: true })));
      }
    } catch (err) {
      console.error('Failed to fetch diners:', err);
    }
  };
  // 2. Add Diner Profile
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
        fetchDiners();
      }
    } catch (err) {
      console.error('Failed to add diner:', err);
    }
  };
  // 3. Delete Diner Profile
  const handleDeleteDiner = async (name: string) => {
    if (!user) return;
    try {
      const res = await fetch(`${BACKEND_URL}/api/diners/${name}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${user.token}` }
      });
      if (res.ok) {
        fetchDiners();
      }
    } catch (err) {
      console.error('Failed to delete diner:', err);
    }
  };
  // 4. Toggle Active Diner
  const handleToggleDiners = (activeNames: string[]) => {
    setDiners(prev =>
      prev.map(d => ({ ...d, is_active: activeNames.includes(d.name) }))
    );
  };
  // 5. Send message to AI Agent
  const handleSendMessage = async (text: string) => {
    if (!user) return;
    
    // Append user message
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
      console.error('Failed to fetch recommendations:', err);
      setMessages(prev => [...prev, { sender: 'agent', text: 'Error connecting to the recommendation service.' }]);
    } finally {
      setLoading(false);
    }
  };
  // 6. Sign Out
  const handleSignOut = () => {
    setUser(null);
    setDiners([]);
    setMessages([
      { sender: 'agent', text: 'Hello! I am WeEat, your meal planner assistant. Who is eating today, and what can I suggest for you?' }
    ]);
  };
  if (!user) {
    return <Login onLoginSuccess={setUser} />;
  }
  return (
    <div className="app-layout">
      {/* Sidebar Controls */}
      <aside className="sidebar glass-panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: '0' }}>WeEat</h2>
          <button onClick={handleSignOut} className="demo-signin-btn" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
            Sign Out
          </button>
        </div>
        <hr style={{ border: '0', borderTop: '1px solid var(--card-border)', width: '100%', margin: '0' }} />
        
        <DinerSelector
          diners={diners}
          onToggleDiners={handleToggleDiners}
        />
        
        <hr style={{ border: '0', borderTop: '1px solid var(--card-border)', width: '100%', margin: '0' }} />
        
        <ProfileManager
          diners={diners}
          onAddDiner={handleAddDiner}
          onDeleteDiner={handleDeleteDiner}
        />
      </aside>
      {/* Main Dashboard Chat Console */}
      <main className="main-content">
        <ChatAgent
          messages={messages}
          onSendMessage={handleSendMessage}
          loading={loading}
        />
      </main>
    </div>
  );
}

export default App;