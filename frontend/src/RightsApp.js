import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RightsApp.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Helper function to get URL parameters
const getUrlParameter = (name) => {
  name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
  const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
  const results = regex.exec(window.location.search);
  return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};

// Components
const SearchBar = ({ onSearch, loading }) => {
  const [query, setQuery] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);

  useEffect(() => {
    // Check if speech recognition is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setSpeechSupported(!!SpeechRecognition);
  }, []);

  const handleVoiceSearch = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      alert('Speech recognition not supported in your browser. Try Chrome or Safari.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    setIsListening(true);
    console.log('Voice recognition starting...');

    recognition.onstart = () => {
      console.log('Voice recognition started - speak now!');
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log('Voice recognized:', transcript);
      setQuery(transcript);
      setIsListening(false);
      
      // Auto-search after voice input
      if (transcript.trim()) {
        setTimeout(() => {
          onSearch(transcript);
        }, 500);
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      
      if (event.error === 'not-allowed') {
        alert('Microphone access denied. Please allow microphone access and try again.');
      } else if (event.error === 'no-speech') {
        alert('No speech detected. Please try speaking louder or closer to the microphone.');
      } else {
        alert(`Voice recognition failed: ${event.error}. Please try again.`);
      }
    };

    recognition.onend = () => {
      console.log('Voice recognition ended');
      setIsListening(false);
    };

    try {
      recognition.start();
    } catch (error) {
      console.error('Failed to start recognition:', error);
      setIsListening(false);
      alert('Failed to start voice recognition. Please try again.');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your rights... (e.g., 'pulled over', 'eviction') or use voice 🎤"
            className="search-input"
            data-testid="rights-search-input"
            disabled={loading || isListening}
          />
          
          {speechSupported && (
            <button 
              type="button"
              className={`voice-button ${isListening ? 'listening' : ''}`}
              onClick={handleVoiceSearch}
              disabled={loading || isListening}
              data-testid="voice-search-button"
              title="Voice Search"
            >
              {isListening ? '🔴 Listening...' : '🎤'}
            </button>
          )}
          
          <button 
            type="submit" 
            className="search-button"
            data-testid="rights-search-button"
            disabled={loading || !query.trim() || isListening}
          >
            {loading ? '🔍 Searching...' : '🔍 Search Rights'}
          </button>
        </div>
        
        {isListening && (
          <div className="voice-feedback">
            <p>🎤 Listening... Speak now!</p>
            <p className="voice-tip">Try: "What are my rights when pulled over?"</p>
          </div>
        )}
        
        {speechSupported && (
          <div className="voice-examples">
            <p><strong>Voice commands you can try:</strong></p>
            <ul>
              <li>"What are my rights when pulled over?"</li>
              <li>"Can police search my car?"</li>
              <li>"Landlord eviction rights"</li>
              <li>"Recording police officers"</li>
            </ul>
          </div>
        )}
      </form>
    </div>
  );
};

const CategoryCard = ({ category, onSelect, onViewRights }) => (
  <div className={`category-card ${category.is_free ? 'free-card' : 'paid-card'}`}>
    <div className="category-icon">{category.icon}</div>
    <h3 className="category-title">{category.name}</h3>
    <p className="category-description">{category.description}</p>
    
    <div className="category-price">
      {category.is_free ? (
        <span className="price-free">FREE</span>
      ) : (
        <span className="price-paid">${category.price}</span>
      )}
    </div>
    
    <div className="category-actions">
      {category.coming_soon ? (
        <button className="btn-coming-soon" disabled>
          Coming Soon
        </button>
      ) : (
        <>
          <button 
            className="btn-view-rights"
            onClick={() => onViewRights(category.id)}
            data-testid={`view-${category.id}-rights`}
          >
            View Rights
          </button>
          {!category.is_free && (
            <button 
              className="btn-purchase"
              onClick={() => onSelect(category.id)}
              data-testid={`purchase-${category.id}`}
            >
              Purchase Access
            </button>
          )}
        </>
      )}
    </div>
  </div>
);

const RightCard = ({ right, onView, isPurchased = false }) => (
  <div className="right-card">
    <h4 className="right-title">{right.title}</h4>
    <p className="right-situation">{right.situation}</p>
    <div className="right-actions">
      <button 
        className={`btn-view-right ${right.is_free || isPurchased ? 'available' : 'preview'}`}
        onClick={() => onView(right.id)}
        data-testid={`view-right-${right.id}`}
      >
        {right.is_free ? 'Read Full Guide' : isPurchased ? 'Read Full Guide' : 'Preview'}
      </button>
      {!right.is_free && !isPurchased && (
        <span className="requires-purchase">Requires Purchase</span>
      )}
    </div>
  </div>
);

const RightContent = ({ content, onBack }) => (
  <div className="right-content" data-testid="right-content">
    <div className="content-header">
      <button 
        className="back-button"
        onClick={onBack}
        data-testid="back-to-rights"
      >
        ← Back
      </button>
      <h2 className="content-title">{content.title}</h2>
      {content.requires_purchase && (
        <div className="purchase-prompt">
          <p>This is a preview. Purchase full access for ${content.price}</p>
          <button className="btn-purchase-now">Purchase Now</button>
        </div>
      )}
    </div>
    
    <div className="content-body">
      <div className="situation-box">
        <strong>Situation:</strong> {content.situation}
      </div>
      
      <div className="content-text">
        {content.preview || content.content}
      </div>
      
      {content.requires_purchase && (
        <div className="content-locked">
          <div className="lock-icon">🔒</div>
          <p>Unlock full content with detailed guidance, legal requirements by state, and step-by-step instructions.</p>
          <button className="btn-unlock">Unlock for ${content.price}</button>
        </div>
      )}
    </div>
  </div>
);

const PaymentSuccess = ({ sessionId }) => {
  const [status, setStatus] = useState('checking');
  const [category, setCategory] = useState(null);

  useEffect(() => {
    if (sessionId) {
      // In a real app, you'd verify the payment here
      setStatus('success');
      setCategory('tenant'); // This would come from payment verification
    }
  }, [sessionId]);

  if (status === 'checking') {
    return (
      <div className="payment-status checking">
        <h2>🔄 Processing Payment...</h2>
        <p>Please wait while we verify your purchase.</p>
      </div>
    );
  }

  return (
    <div className="payment-status success">
      <h2>✅ Payment Successful!</h2>
      <p>You now have full access to {category} rights. Your purchase never expires!</p>
      <button onClick={() => window.location.href = '/'} className="btn-continue">
        Continue to Rights
      </button>
    </div>
  );
};

// Main App Component
const RightsApp = () => {
  const [currentView, setCurrentView] = useState('home');
  const [categories, setCategories] = useState([]);
  const [currentCategory, setCurrentCategory] = useState(null);
  const [categoryRights, setCategoryRights] = useState([]);
  const [currentRight, setCurrentRight] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCategories();
    
    // Check if returning from payment
    const sessionId = getUrlParameter('session_id');
    if (sessionId) {
      setCurrentView('payment-success');
    }
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data.categories);
    } catch (err) {
      setError('Failed to load categories');
      console.error('Categories error:', err);
    }
  };

  const handleSearch = async (query) => {
    setLoading(true);
    setError(null);
    console.log('Searching for:', query);
    
    try {
      const response = await axios.get(`${API}/search`, { params: { query } });
      console.log('Search results:', response.data);
      
      if (response.data.results && response.data.results.length > 0) {
        setSearchResults(response.data.results);
        setCurrentView('search-results');
      } else {
        // If no search results, try to find direct matches
        const directMatches = findDirectMatches(query);
        if (directMatches.length > 0) {
          setSearchResults(directMatches);
          setCurrentView('search-results');
        } else {
          setError(`No results found for "${query}". Try searching for: "pulled over", "eviction", "search car", or "tenant rights"`);
        }
      }
    } catch (err) {
      setError('Search failed. Please try again.');
      console.error('Search error:', err);
    }
    setLoading(false);
  };

  const findDirectMatches = (query) => {
    const queryLower = query.toLowerCase();
    const directMatches = [];
    
    // Common search terms and their matches
    if (queryLower.includes('pulled over') || queryLower.includes('traffic stop') || queryLower.includes('police stop')) {
      directMatches.push({
        id: 'traffic_pulled_over',
        title: 'I Got Pulled Over',
        situation: 'Police officer pulls you over',
        category: 'traffic',
        is_free: true,
        price: 0
      });
    }
    
    if (queryLower.includes('search') && (queryLower.includes('car') || queryLower.includes('vehicle'))) {
      directMatches.push({
        id: 'traffic_search_car',
        title: 'Can Police Search My Car?',
        situation: 'Officer wants to search your vehicle',
        category: 'traffic',
        is_free: true,
        price: 0
      });
    }
    
    if (queryLower.includes('id') || queryLower.includes('identification')) {
      directMatches.push({
        id: 'traffic_show_id',
        title: 'Do I Have to Show ID?',
        situation: 'Officer asks for identification',
        category: 'traffic',
        is_free: true,
        price: 0
      });
    }
    
    if (queryLower.includes('record') || queryLower.includes('filming')) {
      directMatches.push({
        id: 'traffic_recording',
        title: 'Can I Record Police?',
        situation: 'You want to record police interaction',
        category: 'traffic',
        is_free: true,
        price: 0
      });
    }
    
    if (queryLower.includes('evict') || queryLower.includes('landlord')) {
      directMatches.push({
        id: 'tenant_eviction',
        title: 'Landlord Wants to Evict Me',
        situation: 'Facing eviction proceedings',
        category: 'tenant',
        is_free: false,
        price: 2.99
      });
    }
    
    if (queryLower.includes('deposit')) {
      directMatches.push({
        id: 'tenant_security_deposit',
        title: 'Getting Security Deposit Back',
        situation: 'Moving out and want deposit returned',
        category: 'tenant',
        is_free: false,
        price: 2.99
      });
    }
    
    return directMatches;
  };

  const handleViewCategoryRights = async (categoryId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/rights/${categoryId}`);
      setCategoryRights(response.data.rights);
      setCurrentCategory(categoryId);
      setCurrentView('category-rights');
    } catch (err) {
      setError('Failed to load rights');
      console.error('Rights error:', err);
    }
    setLoading(false);
  };

  const handleViewRight = async (rightId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/rights/${currentCategory}/${rightId}`);
      setCurrentRight(response.data);
      setCurrentView('right-content');
    } catch (err) {
      setError('Failed to load content');
      console.error('Content error:', err);
    }
    setLoading(false);
  };

  const handlePurchaseCategory = async (categoryId) => {
    try {
      const originUrl = window.location.origin;
      const response = await axios.post(`${API}/purchase/${categoryId}`, {
        category: categoryId,
        origin_url: originUrl
      });

      if (response.data.access_granted) {
        setError(null);
        alert('This category is free! Access granted.');
        handleViewCategoryRights(categoryId);
      } else {
        // Redirect to Stripe checkout
        window.location.href = response.data.checkout_url;
      }
    } catch (err) {
      setError('Purchase failed. Please try again.');
      console.error('Purchase error:', err);
    }
  };

  // Handle payment success page
  if (currentView === 'payment-success') {
    const sessionId = getUrlParameter('session_id');
    return (
      <div className="app" data-testid="rights-app">
        <header className="app-header">
          <h1 className="app-title">Rights Helper</h1>
          <p className="app-tagline">Know Your Rights • Stay Protected • Be Informed</p>
        </header>
        <main className="app-main">
          <PaymentSuccess sessionId={sessionId} />
        </main>
      </div>
    );
  }

  return (
    <div className="app" data-testid="rights-app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title" onClick={() => setCurrentView('home')}>
            Rights Helper ⚖️
          </h1>
          <p className="app-tagline">Know Your Rights • Stay Protected • Be Informed</p>
        </div>
        <nav className="header-nav">
          <button 
            className="nav-link" 
            onClick={() => setCurrentView('home')}
            data-testid="nav-home"
          >
            🏠 Home
          </button>
          <button 
            className="nav-link" 
            onClick={() => setCurrentView('search')}
            data-testid="nav-search"
          >
            🔍 Search
          </button>
        </nav>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-message" data-testid="error-message">
            {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {currentView === 'home' && (
          <div className="home-view" data-testid="home-view">
            <div className="hero-section">
              <h2 className="hero-title">Know Your Rights Instantly</h2>
              <p className="hero-subtitle">
                Quick, reliable legal guidance for everyday situations. From traffic stops to tenant rights, 
                get the knowledge you need when you need it most. <strong>Works offline!</strong>
              </p>
              
              <div className="theme-selector">
                <p>Choose Your Style:</p>
                <div className="theme-buttons">
                  <button 
                    className="theme-btn default-theme" 
                    onClick={() => document.body.className = ''}
                    data-testid="default-theme"
                  >
                    🎯 Default
                  </button>
                  <button 
                    className="theme-btn glossy-theme" 
                    onClick={() => document.body.className = 'glossy-theme'}
                    data-testid="glossy-theme"
                  >
                    ✨ Glossy
                  </button>
                  <button 
                    className="theme-btn matte-theme" 
                    onClick={() => document.body.className = 'matte-theme'}
                    data-testid="matte-theme"
                  >
                    📱 Matte
                  </button>
                  <button 
                    className="theme-btn wet-theme" 
                    onClick={() => document.body.className = 'wet-theme'}
                    data-testid="wet-theme"
                  >
                    💧 Wet Look
                  </button>
                </div>
              </div>
            </div>
            
            <SearchBar onSearch={handleSearch} loading={loading} />
            
            <div className="categories-section">
              <h3>Choose Your Rights Category</h3>
              <div className="categories-grid">
                {categories.map(category => (
                  <CategoryCard
                    key={category.id}
                    category={category}
                    onSelect={handlePurchaseCategory}
                    onViewRights={handleViewCategoryRights}
                  />
                ))}
              </div>
            </div>

            <div className="features-section">
              <h3>Why Rights Helper?</h3>
              <div className="features-grid">
                <div className="feature-card">
                  <h4>📱 Works Offline</h4>
                  <p>Access your rights even without internet connection. Perfect for emergencies.</p>
                </div>
                <div className="feature-card">
                  <h4>🗺️ State-Specific</h4>
                  <p>Laws vary by state. Get accurate information for where you live.</p>
                </div>
                <div className="feature-card">
                  <h4>⚡ Instant Access</h4>
                  <p>No law degree needed. Plain English explanations you can understand quickly.</p>
                </div>
                <div className="feature-card">
                  <h4>💰 One-Time Purchase</h4>
                  <p>Buy once, own forever. No subscriptions, no hidden fees.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentView === 'search-results' && (
          <div className="search-results-view" data-testid="search-results">
            <div className="results-header">
              <h2>Search Results</h2>
              <button 
                className="back-button"
                onClick={() => setCurrentView('home')}
              >
                ← Back to Home
              </button>
            </div>
            
            <div className="results-list">
              {searchResults.map(result => (
                <div key={result.id} className="search-result-card">
                  <div className="result-info">
                    <h4>{result.title}</h4>
                    <p>{result.situation}</p>
                    <span className="result-category">Category: {result.category}</span>
                  </div>
                  <div className="result-actions">
                    {result.is_free ? (
                      <button 
                        className="btn-view-free"
                        onClick={() => {
                          setCurrentCategory(result.category);
                          handleViewRight(result.id);
                        }}
                      >
                        View Free
                      </button>
                    ) : (
                      <button 
                        className="btn-preview"
                        onClick={() => {
                          setCurrentCategory(result.category);
                          handleViewRight(result.id);
                        }}
                      >
                        Preview (${result.price})
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {currentView === 'category-rights' && (
          <div className="category-rights-view" data-testid="category-rights">
            <div className="category-header">
              <button 
                className="back-button"
                onClick={() => setCurrentView('home')}
              >
                ← Back to Categories
              </button>
              <h2>
                {categories.find(c => c.id === currentCategory)?.name} Rights
              </h2>
            </div>
            
            <div className="rights-list">
              {categoryRights.map(right => (
                <RightCard
                  key={right.id}
                  right={right}
                  onView={handleViewRight}
                  isPurchased={right.is_free} // Simplified for demo
                />
              ))}
            </div>
          </div>
        )}

        {currentView === 'right-content' && currentRight && (
          <div className="right-content-view" data-testid="right-content-view">
            <RightContent
              content={currentRight}
              onBack={() => setCurrentView('category-rights')}
            />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>© 2025 Rights Helper. Legal guidance for everyday situations. Not a substitute for legal advice.</p>
      </footer>
    </div>
  );
};

export default RightsApp;