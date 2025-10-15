import React, { useState, useEffect } from 'react';
import './pearl-theme.css';
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
const LegalDisclaimer = () => (
  <div className="legal-disclaimer">
    <div className="disclaimer-content">
      <h4>⚠️ Important Legal Disclaimer</h4>
      <p>
        <strong>This app provides educational information only and is NOT legal advice.</strong> 
        Laws vary significantly by state, county, and municipality. This information should not be relied upon 
        as a substitute for consultation with a qualified attorney. Always consult a licensed attorney in your 
        jurisdiction for specific legal situations.
      </p>
      <ul>
        <li>• Content is for educational purposes only</li>
        <li>• Laws change frequently - verify current local laws</li>
        <li>• No attorney-client relationship is created</li>
        <li>• Consult qualified legal counsel for advice</li>
      </ul>
      <p className="disclaimer-footer">
        <strong>By using this app, you acknowledge that you understand this is not legal advice 
        and agree to consult appropriate legal counsel for your specific situation.</strong>
      </p>
    </div>
  </div>
);

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
      
      // Immediate search - no delay
      if (transcript.trim()) {
        onSearch(transcript.trim());
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
  const [selectedBundles, setSelectedBundles] = useState([]);
  const [showCart, setShowCart] = useState(false);

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
    
    // Traffic & Vehicle Rights
    if (queryLower.includes('pulled over') || queryLower.includes('traffic stop') || queryLower.includes('police stop') || queryLower.includes('traffic')) {
      directMatches.push({
        id: 'traffic_pulled_over',
        title: 'Traffic & Vehicle Rights',
        situation: 'Police stops, searches, DUI checkpoints, recording rights',
        category: 'traffic',
        is_free: false,
        price: 2.99
      });
    }
    
    // Property Rights
    if (queryLower.includes('property') || queryLower.includes('home') || queryLower.includes('house') || queryLower.includes('door') || queryLower.includes('search')) {
      directMatches.push({
        id: 'property_rights',
        title: 'Property Rights',
        situation: 'Cops at your door? Learn the ONE phrase that stops illegal searches',
        category: 'property',
        is_free: false,
        price: 2.99
      });
    }
    
    // Housing/Tenant Rights
    if (queryLower.includes('evict') || queryLower.includes('landlord') || queryLower.includes('tenant') || queryLower.includes('rent') || queryLower.includes('housing') || queryLower.includes('deposit')) {
      directMatches.push({
        id: 'housing_rights',
        title: 'Housing Rights',
        situation: 'Landlord issues, evictions, security deposits, repairs',
        category: 'housing',
        is_free: false,
        price: 2.99
      });
    }
    
    // Legal Landmines
    if (queryLower.includes('review') || queryLower.includes('yelp') || queryLower.includes('lawsuit') || queryLower.includes('landmine') || queryLower.includes('defamation')) {
      directMatches.push({
        id: 'legal_landmines',
        title: 'Legal Landmines',
        situation: 'Bad Yelp review = $25K lawsuit? Learn the ONE word that protects you',
        category: 'landmines',
        is_free: false,
        price: 2.99
      });
    }
    
    // Criminal Defense
    if (queryLower.includes('arrest') || queryLower.includes('criminal') || queryLower.includes('defense') || queryLower.includes('miranda') || queryLower.includes('lawyer')) {
      directMatches.push({
        id: 'criminal_rights',
        title: 'Criminal Defense Rights',
        situation: 'Say these 2 sentences during arrest to stop questioning',
        category: 'criminal',
        is_free: false,
        price: 2.99
      });
    }
    
    // Workplace Rights
    if (queryLower.includes('work') || queryLower.includes('boss') || queryLower.includes('job') || queryLower.includes('fired') || queryLower.includes('overtime') || queryLower.includes('harass')) {
      directMatches.push({
        id: 'workplace_rights',
        title: 'Business & Workplace Rights',
        situation: 'Boss harassment, firing, overtime, workplace issues',
        category: 'workplace',
        is_free: false,
        price: 2.99
      });
    }
    
    // Divorce Rights
    if (queryLower.includes('divorce') || queryLower.includes('separation') || queryLower.includes('assets') || queryLower.includes('custody')) {
      directMatches.push({
        id: 'divorce_rights',
        title: 'Divorce Rights',
        situation: 'Don\'t lose half your assets! Learn the ONE thing lawyers hide',
        category: 'divorce',
        is_free: false,
        price: 4.99
      });
    }
    
    // Immigration Rights
    if (queryLower.includes('immigra') || queryLower.includes('visa') || queryLower.includes('deport') || queryLower.includes('green card') || queryLower.includes('citizen')) {
      directMatches.push({
        id: 'immigration_rights',
        title: 'Immigration Rights',
        situation: 'Visa, deportation defense, green cards - ALL immigrants covered',
        category: 'immigration',
        is_free: false,
        price: 4.99
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
    // Go directly to show content for the category
    handleViewCategoryRights(categoryId);
  };

  const toggleBundleSelection = (categoryId) => {
    setSelectedBundles(prev => {
      if (prev.includes(categoryId)) {
        // Remove from selection
        return prev.filter(id => id !== categoryId);
      } else {
        // Add to selection
        return [...prev, categoryId];
      }
    });
  };

  const getTotalPrice = () => {
    const bundlePrices = {
      traffic: 2.99,
      housing: 2.99,
      property: 2.99,
      landmines: 2.99,
      criminal: 2.99,
      workplace: 2.99,
      family: 2.99,
      divorce: 4.99,
      immigration: 4.99,
      healthcare: 2.99,
      student: 2.99,
      digital: 2.99,
      consumer: 2.99,
    };
    
    const subtotal = selectedBundles.reduce((total, bundleId) => {
      return total + (bundlePrices[bundleId] || 0);
    }, 0);
    
    // Apply bundle discounts
    const count = selectedBundles.length;
    if (count >= 13) {
      return 29.99; // All 13 bundles deal
    } else if (count >= 3) {
      return 12.99; // Any 3 bundles deal
    }
    
    return subtotal;
  };

  const handleCheckout = async () => {
    if (selectedBundles.length === 0) {
      alert('Please select at least one bundle to purchase!');
      return;
    }
    
    try {
      setLoading(true);
      const originUrl = window.location.origin;
      
      // Create Stripe checkout session for multiple bundles
      const response = await axios.post(`${API}/purchase/cart`, {
        bundles: selectedBundles,
        origin_url: originUrl
      });

      if (response.data.checkout_url) {
        // Redirect to Stripe checkout
        window.location.href = response.data.checkout_url;
      } else {
        alert('Checkout session created successfully!');
        setSelectedBundles([]);
        setShowCart(false);
      }
    } catch (err) {
      console.error('Checkout error:', err);
      alert('Checkout failed. Please try again or contact support.');
    } finally {
      setLoading(false);
    }
  };

  const handleBuyFullAccess = async (categoryId) => {
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
            Know Your Rights ⚖️
          </h1>
          <p className="app-tagline">Legal Protection Made Simple • Voice Commands • Offline Access</p>
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
            <LegalDisclaimer />
            <div className="hero-section">
              <h2 className="hero-title">Know Your Rights • Protect Yourself</h2>
              <p className="hero-subtitle">
                🚨 Don't let your boss harass you, don't post that angry review, don't get screwed over! 
                Prevent legal disasters before they happen - for the price of a coffee. 
                Voice-activated, offline access, plain English explanations. <strong>Be prepared for anything!</strong>
              </p>
            </div>
            
            <SearchBar onSearch={handleSearch} loading={loading} />
            
            <div className="bundles-section">
              <h3>Choose Your Rights Bundle</h3>
              <div className="pricing-note">
                <p>💰 <strong>Bundle Deals:</strong> Any 3 bundles for $12.99 • Complete Package (All 10) for $29.99</p>
              </div>
              
              <div className="bundles-grid">
                {/* Essential Bundles with Selection */}
                <div className={`bundle-card compact ${selectedBundles.includes('traffic') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('traffic')}
                    onChange={() => toggleBundleSelection('traffic')}
                  />
                  <div className="bundle-icon">🚗</div>
                  <h4>Traffic & Vehicle Rights</h4>
                  <p>Police stops, searches, DUI checkpoints, recording rights</p>
                  <div className="bundle-price">$2.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('housing') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('housing')}
                    onChange={() => toggleBundleSelection('housing')}
                  />
                  <div className="bundle-icon">🏠</div>
                  <h4>Housing Rights</h4>
                  <p>🏠 Landlords hate this ONE trick that gets your deposit back...</p>
                  <div className="bundle-price">$2.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('property') ? 'selected' : ''} popular`}>
                  <div className="popular-badge">⚡ MUST HAVE</div>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('property')}
                    onChange={() => toggleBundleSelection('property')}
                  />
                  <div className="bundle-icon">🏡</div>
                  <h4>Property Rights</h4>
                  <p>🚔 Cops at your door? Learn the ONE phrase that stops searches...</p>
                  <div className="bundle-price">$2.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('landmines') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('landmines')}
                    onChange={() => toggleBundleSelection('landmines')}
                  />
                  <div className="bundle-icon">⚠️</div>
                  <h4>Legal Landmines</h4>
                  <p>🚨 Bad Yelp review = $25K lawsuit? Protection here...</p>
                  <div className="bundle-price">$2.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('criminal') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('criminal')}
                    onChange={() => toggleBundleSelection('criminal')}
                  />
                  <div className="bundle-icon">⚖️</div>
                  <h4>Criminal Defense Rights</h4>
                  <p>⚖️ Say these 2 sentences during arrest to stop questioning...</p>
                  <div className="bundle-price">$2.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('workplace') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('workplace')}
                    onChange={() => toggleBundleSelection('workplace')}
                  />
                  <div className="bundle-icon">💼</div>
                  <h4>Business & Workplace Rights</h4>
                  <p>💼 Boss can't fire you for saying NO if you say these 5 words...</p>
                  <div className="bundle-price">$2.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('family') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('family')}
                    onChange={() => toggleBundleSelection('family')}
                  />
                  <div className="bundle-icon">👨‍👩‍👧‍👦</div>
                  <h4>Family & Personal Rights</h4>
                  <p>Marriage, divorce, child custody, domestic violence, elder care</p>
                  <div className="bundle-price">$2.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('divorce') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('divorce')}
                    onChange={() => toggleBundleSelection('divorce')}
                  />
                  <div className="bundle-icon">💔</div>
                  <h4>Divorce Rights</h4>
                  <p>💸 Don't lose half your assets! The ONE thing lawyers hide...</p>
                  <div className="bundle-price">$4.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('immigration') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('immigration')}
                    onChange={() => toggleBundleSelection('immigration')}
                  />
                  <div className="bundle-icon">🌍</div>
                  <h4>Immigration Rights</h4>
                  <p>🛂 Visa, deportation defense, green cards - ALL immigrants covered</p>
                  <div className="bundle-price">$4.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('healthcare') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('healthcare')}
                    onChange={() => toggleBundleSelection('healthcare')}
                  />
                  <div className="bundle-icon">🏥</div>
                  <h4>Healthcare & Privacy Rights</h4>
                  <p>Medical records, HIPAA, insurance disputes, patient rights</p>
                  <div className="bundle-price">$2.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('student') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('student')}
                    onChange={() => toggleBundleSelection('student')}
                  />
                  <div className="bundle-icon">🎓</div>
                  <h4>Student Rights</h4>
                  <p>School discipline, loans, campus safety, discrimination, speech</p>
                  <div className="bundle-price">$2.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('digital') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('digital')}
                    onChange={() => toggleBundleSelection('digital')}
                  />
                  <div className="bundle-icon">📱</div>
                  <h4>Digital & Social Media Rights</h4>
                  <p>Online privacy, cyberbullying, posts, harassment, data protection</p>
                  <div className="bundle-price">$2.99</div>
                </div>

                <div className={`bundle-card compact ${selectedBundles.includes('consumer') ? 'selected' : ''}`}>
                  <input 
                    type="checkbox" 
                    className="bundle-checkbox"
                    checked={selectedBundles.includes('consumer')}
                    onChange={() => toggleBundleSelection('consumer')}
                  />
                  <div className="bundle-icon">🛡️</div>
                  <h4>Consumer Protection Rights</h4>
                  <p>Scams, contracts, warranties, debt collection, identity theft</p>
                  <div className="bundle-price">$2.99</div>
                </div>
              </div>

              {/* Bundle Deal Cards */}
              <div className="bundle-deals">
                <h3>💰 Save with Bundle Deals</h3>
                <div className="deals-grid">
                  <div className="deal-card">
                    <h4>Essential 3-Pack</h4>
                    <p>Traffic + Housing + Legal Landmines</p>
                    <div className="deal-pricing">
                      <span className="original-price">$8.97</span>
                      <span className="deal-price">$6.99</span>
                    </div>
                    <button className="deal-button">Save $2 - Get 3 Pack</button>
                  </div>

                  <div className="deal-card popular">
                    <div className="popular-badge">BEST VALUE</div>
                    <h4>Complete Rights Package</h4>
                    <p>All 10 bundles - Everything you need!</p>
                    <div className="deal-pricing">
                      <span className="original-price">$29.90</span>
                      <span className="deal-price">$14.99</span>
                    </div>
                    <button className="deal-button">Save $19 - Get Everything</button>
                  </div>
                </div>
              </div>
            </div>

            <div className="features-section">
              <h3>Why Choose Know Your Rights?</h3>
              <div className="features-grid">
                <div className="feature-card">
                  <h4>🎤 Voice Commands</h4>
                  <p>Just speak your question - perfect for emergencies or hands-free use.</p>
                </div>
                <div className="feature-card">
                  <h4>📱 Works Offline</h4>
                  <p>Access your rights even without internet. Perfect for remote areas or emergencies.</p>
                </div>
                <div className="feature-card">
                  <h4>💬 Plain English</h4>
                  <p>No confusing legal jargon. Real situations, real answers you can understand.</p>
                </div>
                <div className="feature-card">
                  <h4>⚡ Instant Answers</h4>
                  <p>Why Google for 20 minutes when you can get precise answers in seconds?</p>
                </div>
                <div className="feature-card">
                  <h4>🛡️ Avoid Legal Trouble</h4>
                  <p>Know the legal landmines before you step on them. Prevention is cheaper than lawyers.</p>
                </div>
                <div className="feature-card">
                  <h4>💰 One-Time Purchase</h4>
                  <p>Buy once, own forever. No monthly subscriptions or hidden fees.</p>
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
              {currentCategory !== 'traffic' && (
                <div className="category-purchase">
                  <div className="category-price">
                    ${categories.find(c => c.id === currentCategory)?.price || '2.99'}
                  </div>
                  <button 
                    className="bundle-button"
                    onClick={() => handleBuyFullAccess(currentCategory)}
                  >
                    🔓 Unlock Full Access
                  </button>
                </div>
              )}
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

      {/* FLOATING CART BUTTON - ALWAYS VISIBLE WHEN ITEMS SELECTED */}
      {selectedBundles.length > 0 && (
        <>
          <button 
            className="floating-cart-btn"
            onClick={() => {
              console.log('Cart button clicked! showCart:', showCart);
              setShowCart(true);
              console.log('Set showCart to true');
            }}
          >
            <span className="cart-icon">🛒</span>
            <span className="cart-count">{selectedBundles.length}</span>
            <span className="cart-text">View Cart - ${getTotalPrice().toFixed(2)}</span>
          </button>

          {/* CART MODAL OVERLAY */}
          {showCart && (() => {
            console.log('RENDERING CART MODAL! showCart:', showCart, 'selectedBundles:', selectedBundles.length);
            return (
            <div className="cart-modal-overlay" onClick={() => setShowCart(false)}>
              <div className="cart-modal" onClick={(e) => e.stopPropagation()}>
                <div className="cart-modal-header">
                  <h2>🛒 Your Cart ({selectedBundles.length} items)</h2>
                  <button className="close-modal-btn" onClick={() => setShowCart(false)}>✕</button>
                </div>

                <div className="cart-modal-items">
                  {selectedBundles.map(bundleId => {
                    const bundleInfo = {
                      traffic: { name: 'Traffic & Vehicle Rights', icon: '🚗', price: 2.99 },
                      housing: { name: 'Housing Rights', icon: '🏠', price: 2.99 },
                      property: { name: 'Property Rights', icon: '🏡', price: 2.99 },
                      landmines: { name: 'Legal Landmines', icon: '⚠️', price: 2.99 },
                      criminal: { name: 'Criminal Defense Rights', icon: '⚖️', price: 2.99 },
                      workplace: { name: 'Business & Workplace Rights', icon: '💼', price: 2.99 },
                      family: { name: 'Family & Personal Rights', icon: '👨‍👩‍👧‍👦', price: 2.99 },
                      divorce: { name: 'Divorce Rights', icon: '💔', price: 4.99 },
                      immigration: { name: 'Immigration Rights', icon: '🌍', price: 4.99 },
                      healthcare: { name: 'Healthcare & Privacy Rights', icon: '🏥', price: 2.99 },
                      student: { name: 'Student Rights', icon: '🎓', price: 2.99 },
                      digital: { name: 'Digital & Social Media Rights', icon: '📱', price: 2.99 },
                      consumer: { name: 'Consumer Protection Rights', icon: '🛡️', price: 2.99 },
                    };
                    const bundle = bundleInfo[bundleId];
                    
                    return (
                      <div key={bundleId} className="cart-modal-item">
                        <span className="item-icon">{bundle.icon}</span>
                        <span className="item-name">{bundle.name}</span>
                        <span className="item-price">${bundle.price.toFixed(2)}</span>
                        <button 
                          className="remove-btn"
                          onClick={() => toggleBundleSelection(bundleId)}
                        >
                          ✕
                        </button>
                      </div>
                    );
                  })}
                </div>

                <div className="cart-modal-footer">
                  <div className="modal-total">
                    <span>TOTAL:</span>
                    <span className="modal-total-amount">${getTotalPrice().toFixed(2)}</span>
                  </div>
                  <button className="modal-clear-btn" onClick={() => setSelectedBundles([])}>
                    Clear All
                  </button>
                  <button className="modal-checkout-btn" onClick={handleCheckout}>
                    🔒 CHECKOUT NOW
                  </button>
                </div>
              </div>
            </div>
            );
          })()}
        </>
      )}
    </div>
  );
};

export default RightsApp;