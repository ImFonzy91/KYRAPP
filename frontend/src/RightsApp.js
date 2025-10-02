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
            placeholder="Search your rights... (e.g., 'pulled over', 'eviction')"
            className="search-input"
            data-testid="rights-search-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="search-button"
            data-testid="rights-search-button"
            disabled={loading || !query.trim()}
          >
            {loading ? '🔍 Searching...' : '🔍 Search Rights'}
          </button>
        </div>
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
    try {
      const response = await axios.get(`${API}/search`, { params: { query } });
      setSearchResults(response.data.results);
      setCurrentView('search-results');
    } catch (err) {
      setError('Search failed. Please try again.');
      console.error('Search error:', err);
    }
    setLoading(false);
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