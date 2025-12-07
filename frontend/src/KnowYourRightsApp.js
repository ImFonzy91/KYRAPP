import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Login/Signup Component
const AuthScreen = ({ onLogin, disclaimer, setShowDisclaimer }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/signup';
      const payload = isLogin 
        ? { email, password }
        : { email, password, name };
      
      const response = await axios.post(`${API}${endpoint}`, payload);
      
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
        localStorage.setItem('token', response.data.token || 'demo-token');
        onLogin(response.data.user);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed');
    }
    setLoading(false);
  };

  return (
    <div className="auth-screen">
      <div className="auth-header">
        <h1>Know Your Rights</h1>
        <p>Real Legal Rights • Real Protection • Real Information</p>
      </div>

      {/* Collapsible Disclaimer */}
      <div className="disclaimer-container">
        <button 
          className="disclaimer-toggle"
          onClick={() => setShowDisclaimer(!disclaimer)}
        >
          ⚠️ Legal Disclaimer {disclaimer ? '▼' : '▶'}
        </button>
        {disclaimer && (
          <div className="disclaimer-content">
            <p><strong>This app provides educational legal information only and is NOT legal advice.</strong></p>
            <ul>
              <li>All rights shown are from the U.S. Constitution and federal/state laws</li>
              <li>Laws vary by state - always verify local laws</li>
              <li>No attorney-client relationship is created</li>
              <li>Consult a licensed attorney for specific legal situations</li>
            </ul>
            <p>By using this app, you acknowledge this is educational information, not legal advice.</p>
          </div>
        )}
      </div>

      <div className="auth-box">
        <div className="auth-tabs">
          <button 
            className={isLogin ? 'active' : ''}
            onClick={() => setIsLogin(true)}
          >
            Login
          </button>
          <button 
            className={!isLogin ? 'active' : ''}
            onClick={() => setIsLogin(false)}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <input
              type="text"
              placeholder="Your Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required={!isLogin}
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Create Account')}
          </button>
        </form>
      </div>

      {/* Flash Sale Banner */}
      <div className="flash-sale-banner">
        <h3>🔥 48-HOUR FLASH SALE 🔥</h3>
        <p><strong>$10</strong> = ALL 13 Rights Bundles (normally $38)</p>
        <p><strong>Buy 3</strong> = Get 7 FREE</p>
        <p><strong>$3</strong> = 5 AI Case Consultations</p>
      </div>
    </div>
  );
};

// Tab 1: Smart Search
const SmartSearchTab = ({ user }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedRight, setSelectedRight] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/search/rights`, {
        params: { query }
      });
      setResults(response.data.results || []);
    } catch (err) {
      console.error('Search failed:', err);
    }
    setLoading(false);
  };

  const renderRightDetails = (right) => {
    return (
      <div className="right-details">
        <button className="back-btn" onClick={() => setSelectedRight(null)}>← Back</button>
        <h2>{right.title}</h2>
        <p className="source"><strong>Source:</strong> {right.source}</p>
        
        {right.text && (
          <div className="legal-text">
            <h4>Actual Legal Text:</h4>
            <blockquote>"{right.text}"</blockquote>
          </div>
        )}
        
        {right.what_it_means && (
          <div className="what-it-means">
            <h4>What This Means For You:</h4>
            <ul>
              {right.what_it_means.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
        )}

        {right.what_to_do && (
          <div className="what-to-do">
            <h4>What To Do:</h4>
            <ul>
              {right.what_to_do.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
        )}

        {right.magic_phrases && (
          <div className="magic-phrases">
            <h4>Say These Exact Words:</h4>
            <ul>
              {right.magic_phrases.map((phrase, i) => (
                <li key={i} className="magic-phrase">"{phrase}"</li>
              ))}
            </ul>
          </div>
        )}

        {right.legal_requirements && (
          <div className="requirements">
            <h4>What You Must Provide:</h4>
            <ul>
              {right.legal_requirements.must_provide?.map((item, i) => <li key={i}>✅ {item}</li>)}
            </ul>
            <h4>What You Do NOT Have To Do:</h4>
            <ul>
              {right.legal_requirements.not_required?.map((item, i) => <li key={i}>❌ {item}</li>)}
            </ul>
          </div>
        )}

        {right.common_rights && (
          <div className="common-rights">
            <h4>Your Rights:</h4>
            <ul>
              {right.common_rights.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
        )}

        {right.illegal_landlord_actions && (
          <div className="illegal-actions">
            <h4>Illegal Landlord Actions:</h4>
            <ul>
              {right.illegal_landlord_actions.map((item, i) => <li key={i}>🚫 {item}</li>)}
            </ul>
          </div>
        )}

        {right.core_rights && (
          <div className="core-rights">
            <h4>Your Core Rights:</h4>
            {right.core_rights.map((r, i) => (
              <div key={i} className="core-right-item">
                <strong>{r.right}:</strong> {r.meaning}
              </div>
            ))}
          </div>
        )}

        {right.what_to_say && (
          <div className="what-to-say">
            <h4>What To Say When Arrested:</h4>
            <ul>
              {right.what_to_say.map((phrase, i) => (
                <li key={i} className="magic-phrase">"{phrase}"</li>
              ))}
            </ul>
            <p className="warning">⚠️ Then STOP TALKING. Wait for your lawyer.</p>
          </div>
        )}

        {right.federal_laws && (
          <div className="federal-laws">
            <h4>Federal Laws That Protect You:</h4>
            {Object.entries(right.federal_laws).map(([key, law]) => (
              <div key={key} className="law-item">
                <h5>{law.name}</h5>
                <ul>
                  {(law.rights || law.protects_against || []).map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}

        {right.ice_encounters && (
          <div className="ice-info">
            <h4>If ICE Comes to Your Home:</h4>
            <ul>
              {right.ice_encounters.at_home?.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
            <h4>If Encountered in Public:</h4>
            <ul>
              {right.ice_encounters.in_public?.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
        )}

        {right.debt_collection && (
          <div className="debt-info">
            <h4>{right.debt_collection.law}</h4>
            <ul>
              {right.debt_collection.protections?.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
            <p className="tip"><strong>Tip:</strong> {right.debt_collection.magic_letter}</p>
          </div>
        )}
      </div>
    );
  };

  if (selectedRight) {
    return renderRightDetails(selectedRight);
  }

  return (
    <div className="smart-search-tab">
      <h2>🔍 Smart Search</h2>
      <p>Type your situation and find your rights</p>
      
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., 'I got pulled over', 'landlord won't return deposit', 'boss harassment'"
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search Rights'}
        </button>
      </form>

      <div className="quick-searches">
        <p>Quick searches:</p>
        <div className="quick-btns">
          <button onClick={() => { setQuery('pulled over'); }}>🚗 Pulled Over</button>
          <button onClick={() => { setQuery('arrested'); }}>⚖️ Arrested</button>
          <button onClick={() => { setQuery('landlord'); }}>🏠 Landlord</button>
          <button onClick={() => { setQuery('work harassment'); }}>💼 Workplace</button>
          <button onClick={() => { setQuery('immigration'); }}>🌍 Immigration</button>
          <button onClick={() => { setQuery('debt collector'); }}>💳 Debt</button>
        </div>
      </div>

      {results.length > 0 && (
        <div className="search-results">
          <h3>Found {results.length} Relevant Right(s)</h3>
          {results.map((right, index) => (
            <div key={index} className="result-card" onClick={() => setSelectedRight(right)}>
              <h4>{right.title}</h4>
              <p className="source-tag">{right.source}</p>
              <button className="view-btn">View Full Details →</button>
            </div>
          ))}
        </div>
      )}

      {results.length === 0 && query && !loading && (
        <p className="no-results">No results found. Try different keywords like "police", "landlord", "work", etc.</p>
      )}
    </div>
  );
};

// Tab 2: My Rights (Purchased Bundles)
const MyRightsTab = ({ user, purchasedBundles }) => {
  const [bundles, setBundles] = useState([]);
  const [selectedBundle, setSelectedBundle] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPurchasedBundles();
  }, []);

  const fetchPurchasedBundles = async () => {
    try {
      const response = await axios.get(`${API}/user/bundles`, {
        params: { user_id: user.id }
      });
      setBundles(response.data.bundles || []);
    } catch (err) {
      console.error('Failed to fetch bundles:', err);
    }
    setLoading(false);
  };

  if (loading) {
    return <div className="loading">Loading your rights...</div>;
  }

  return (
    <div className="my-rights-tab">
      <h2>📚 My Rights</h2>
      <p>Your purchased rights bundles</p>

      {bundles.length === 0 ? (
        <div className="no-bundles">
          <h3>You haven't purchased any bundles yet</h3>
          <p>Check out our flash sale deals!</p>
          
          <div className="promo-cards">
            <div className="promo-card flash">
              <h4>🔥 FLASH SALE</h4>
              <p className="price">$10</p>
              <p>All 13 Rights Bundles</p>
              <span className="savings">Save $28!</span>
            </div>
            <div className="promo-card">
              <h4>Buy 3 Get 7 FREE</h4>
              <p className="price">$8.97</p>
              <p>Get 10 Bundles Total</p>
            </div>
            <div className="promo-card">
              <h4>AI Case Consult</h4>
              <p className="price">$3</p>
              <p>5 "Do I Have a Case?" Queries</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bundles-grid">
          {bundles.map((bundle, index) => (
            <div key={index} className="bundle-card" onClick={() => setSelectedBundle(bundle)}>
              <span className="bundle-icon">{bundle.icon}</span>
              <h4>{bundle.name}</h4>
              <p>{bundle.description}</p>
              <button>View Rights →</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Tab 3: Do I Have a Case?
const CaseAnalyzerTab = ({ user }) => {
  const [situation, setSituation] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [queriesLeft, setQueriesLeft] = useState(3);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchQueriesLeft();
  }, []);

  const fetchQueriesLeft = async () => {
    try {
      const response = await axios.get(`${API}/case-analyzer/queries-left`, {
        params: { user_id: user.id }
      });
      setQueriesLeft(response.data.queries_left);
      setHistory(response.data.history || []);
    } catch (err) {
      console.error('Failed to fetch queries:', err);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!situation.trim() || queriesLeft <= 0) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/case-analyzer/analyze`, {
        user_id: user.id,
        situation: situation
      });
      setAnalysis(response.data);
      setQueriesLeft(response.data.queries_left);
      setSituation('');
    } catch (err) {
      console.error('Analysis failed:', err);
      alert(err.response?.data?.detail || 'Analysis failed');
    }
    setLoading(false);
  };

  const buyMoreQueries = async () => {
    try {
      const response = await axios.post(`${API}/case-analyzer/buy-queries`, {
        user_id: user.id,
        package: '5_queries',
        origin_url: window.location.origin
      });
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (err) {
      console.error('Purchase failed:', err);
    }
  };

  return (
    <div className="case-analyzer-tab">
      <h2>⚖️ Do I Have a Case?</h2>
      <p>AI-powered legal situation analysis</p>

      <div className="queries-status">
        <span className={`queries-left ${queriesLeft <= 0 ? 'empty' : ''}`}>
          {queriesLeft} Free Queries Left
        </span>
        {queriesLeft <= 0 && (
          <button className="buy-more-btn" onClick={buyMoreQueries}>
            Get 5 More for $3
          </button>
        )}
      </div>

      <form onSubmit={handleAnalyze} className="analyzer-form">
        <textarea
          value={situation}
          onChange={(e) => setSituation(e.target.value)}
          placeholder="Describe your legal situation in detail...\n\nExample: 'My landlord hasn't returned my security deposit after 45 days. I left the apartment clean with photos. He's claiming damages that existed before I moved in.'"
          rows={6}
          disabled={queriesLeft <= 0}
        />
        <button type="submit" disabled={loading || queriesLeft <= 0 || !situation.trim()}>
          {loading ? 'Analyzing...' : 'Analyze My Situation'}
        </button>
      </form>

      {analysis && (
        <div className="analysis-result">
          <h3>Analysis Result</h3>
          
          <div className="verdict">
            <h4>Do You Have a Case?</h4>
            <span className={`verdict-badge ${analysis.has_case ? 'yes' : 'maybe'}`}>
              {analysis.verdict}
            </span>
          </div>

          <div className="analysis-section">
            <h4>📋 Summary</h4>
            <p>{analysis.summary}</p>
          </div>

          <div className="analysis-section">
            <h4>⚖️ Relevant Laws</h4>
            <ul>
              {analysis.relevant_laws?.map((law, i) => <li key={i}>{law}</li>)}
            </ul>
          </div>

          <div className="analysis-section">
            <h4>✅ Your Rights in This Situation</h4>
            <ul>
              {analysis.your_rights?.map((right, i) => <li key={i}>{right}</li>)}
            </ul>
          </div>

          <div className="analysis-section">
            <h4>📝 Recommended Next Steps</h4>
            <ol>
              {analysis.next_steps?.map((step, i) => <li key={i}>{step}</li>)}
            </ol>
          </div>

          <div className="analysis-section">
            <h4>💰 Is It Worth Seeing a Lawyer?</h4>
            <p>{analysis.lawyer_recommendation}</p>
          </div>

          <div className="disclaimer-small">
            ⚠️ This analysis is for educational purposes only and is not legal advice. 
            Consult a licensed attorney for your specific situation.
          </div>
        </div>
      )}

      {history.length > 0 && (
        <div className="analysis-history">
          <h3>Previous Analyses</h3>
          {history.map((item, i) => (
            <div key={i} className="history-item">
              <p className="situation-preview">{item.situation.substring(0, 100)}...</p>
              <span className="date">{new Date(item.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Main App Component
const KnowYourRightsApp = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('search');
  const [showDisclaimer, setShowDisclaimer] = useState(true);

  useEffect(() => {
    // Check for existing login
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }

    // Check for payment success
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('payment') === 'success') {
      alert('Payment successful! Your purchase has been added.');
      window.history.replaceState({}, '', '/');
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    setUser(null);
  };

  // Not logged in - show auth screen
  if (!user) {
    return (
      <AuthScreen 
        onLogin={setUser} 
        disclaimer={showDisclaimer}
        setShowDisclaimer={setShowDisclaimer}
      />
    );
  }

  // Logged in - show main app
  return (
    <div className="app-container">
      <header className="app-header">
        <h1 onClick={() => setActiveTab('search')}>Know Your Rights</h1>
        <div className="user-info">
          <span>Welcome, {user.name || user.email}</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <nav className="tab-nav">
        <button 
          className={activeTab === 'search' ? 'active' : ''}
          onClick={() => setActiveTab('search')}
        >
          🔍 Smart Search
        </button>
        <button 
          className={activeTab === 'my-rights' ? 'active' : ''}
          onClick={() => setActiveTab('my-rights')}
        >
          📚 My Rights
        </button>
        <button 
          className={activeTab === 'case-analyzer' ? 'active' : ''}
          onClick={() => setActiveTab('case-analyzer')}
        >
          ⚖️ Do I Have a Case?
        </button>
      </nav>

      <main className="tab-content">
        {activeTab === 'search' && <SmartSearchTab user={user} />}
        {activeTab === 'my-rights' && <MyRightsTab user={user} />}
        {activeTab === 'case-analyzer' && <CaseAnalyzerTab user={user} />}
      </main>

      <footer className="app-footer">
        <p>© 2025 Know Your Rights • Real Legal Information from U.S. Constitution & Federal Law</p>
        <p className="footer-disclaimer">Educational purposes only. Not legal advice.</p>
      </footer>
    </div>
  );
};

export default KnowYourRightsApp;
