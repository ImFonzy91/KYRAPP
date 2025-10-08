import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Payment status polling function
const pollPaymentStatus = async (sessionId, onSuccess, onFailure, attempts = 0) => {
  const maxAttempts = 10;
  const pollInterval = 2000; // 2 seconds

  if (attempts >= maxAttempts) {
    onFailure('Payment status check timed out. Please contact support.');
    return;
  }

  try {
    const response = await axios.get(`${API}/payments/status/${sessionId}`);
    
    if (response.data.payment_status === 'paid') {
      onSuccess(response.data);
      return;
    } else if (response.data.session_status === 'expired') {
      onFailure('Payment session expired. Please try again.');
      return;
    }

    // Continue polling if still pending
    setTimeout(() => pollPaymentStatus(sessionId, onSuccess, onFailure, attempts + 1), pollInterval);
  } catch (error) {
    console.error('Error checking payment status:', error);
    onFailure('Error checking payment status. Please try again.');
  }
};

// Components
const SearchBar = ({ onSearch, loading }) => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('name');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query, searchType);
    }
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-group">
          <select 
            value={searchType} 
            onChange={(e) => setSearchType(e.target.value)}
            className="search-type-select"
            data-testid="search-type-select"
          >
            <option value="name">Name</option>
            <option value="phone">Phone</option>
            <option value="email">Email</option>
            <option value="address">Address</option>
          </select>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`Search by ${searchType}...`}
            className="search-input"
            data-testid="search-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="search-button"
            data-testid="search-button"
            disabled={loading || !query.trim()}
          >
            {loading ? 'Searching...' : 'Scan\'Em'}
          </button>
        </div>
      </form>
    </div>
  );
};

const PricingCard = ({ packageId, name, price, features, isPopular = false, onSelect }) => (
  <div className={`pricing-card ${isPopular ? 'popular' : ''}`}>
    {isPopular && <div className="popular-badge">Most Popular</div>}
    <h3 className="pricing-title">{name}</h3>
    <div className="pricing-price">
      ${price}
      {price > 0 && <span className="pricing-period">/report</span>}
    </div>
    <ul className="pricing-features">
      {features.map((feature, index) => (
        <li key={index} className="pricing-feature">✓ {feature}</li>
      ))}
    </ul>
    <button 
      className={`pricing-button ${isPopular ? 'popular-button' : ''}`}
      onClick={() => onSelect(packageId, price)}
      data-testid={`select-${packageId}-plan`}
    >
      {price === 0 ? 'Get Free Report' : `Pay $${price}`}
    </button>
  </div>
);

const ReportTab = ({ title, isActive, onClick, count = null }) => (
  <button
    className={`report-tab ${isActive ? 'active' : ''} ${title.toLowerCase().replace(' ', '-')}-tab`}
    onClick={onClick}
    data-testid={`tab-${title.toLowerCase().replace(' ', '-')}`}
  >
    {title}
    {count !== null && <span className="tab-count">({count})</span>}
  </button>
);

const CriminalRecord = ({ record }) => (
  <div className="criminal-record">
    <div className="record-header">
      <h4 className="record-charge">{record.charge}</h4>
      <span className={`record-status status-${record.status}`}>
        {record.status.replace('_', ' ').toUpperCase()}
      </span>
    </div>
    <div className="record-details">
      <p className="record-description">{record.description}</p>
      <div className="record-meta">
        <span>Case: {record.case_number}</span>
        <span>Date: {new Date(record.date).toLocaleDateString()}</span>
        <span>Court: {record.court}</span>
        <span>Location: {record.county}, {record.state}</span>
      </div>
      <p className="record-status-description">{record.status_description}</p>
    </div>
  </div>
);

const SocialMediaProfile = ({ profile }) => (
  <div className="social-profile">
    <div className="profile-header">
      <strong>{profile.platform}</strong>
      {profile.verified && <span className="verified-badge">✓</span>}
    </div>
    <p className="profile-username">@{profile.username}</p>
    <p className="profile-activity">Last activity: {profile.last_activity}</p>
    <a 
      href={profile.profile_url} 
      target="_blank" 
      rel="noopener noreferrer"
      className="profile-link"
    >
      View Profile →
    </a>
  </div>
);

const BackgroundReport = ({ report }) => {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', title: 'Overview', count: null },
    { id: 'criminal', title: 'Criminal Records', count: report.criminal_records?.length || 0 },
    { id: 'social', title: 'Social Media', count: report.social_media?.length || 0 },
    { id: 'property', title: 'Property', count: report.property_records?.length || 0 },
    { id: 'professional', title: 'Professional', count: report.professional_info?.length || 0 }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="overview-content" data-testid="overview-content">
            <h3>Personal Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <label>Name:</label>
                <span>{report.person_name}</span>
              </div>
              <div className="info-item">
                <label>Age:</label>
                <span>{report.age || 'Unknown'}</span>
              </div>
              <div className="info-item">
                <label>Current Address:</label>
                <span>{report.current_address}</span>
              </div>
              <div className="info-item">
                <label>Phone Numbers:</label>
                <span>{report.phone_numbers?.join(', ') || 'None found'}</span>
              </div>
              <div className="info-item">
                <label>Email Addresses:</label>
                <span>{report.email_addresses?.join(', ') || 'None found'}</span>
              </div>
            </div>
            
            {report.relatives?.length > 0 && (
              <div className="relatives-section">
                <h4>Known Relatives</h4>
                <ul className="relatives-list">
                  {report.relatives.map((relative, index) => (
                    <li key={index}>{relative}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );
      
      case 'criminal':
        return (
          <div className="criminal-content" data-testid="criminal-content">
            <h3>Criminal Records ({report.criminal_records?.length || 0})</h3>
            {report.criminal_records?.length > 0 ? (
              <div className="criminal-records">
                {report.criminal_records.map((record, index) => (
                  <CriminalRecord key={index} record={record} />
                ))}
              </div>
            ) : (
              <p className="no-records">No criminal records found.</p>
            )}
          </div>
        );
      
      case 'social':
        return (
          <div className="social-content" data-testid="social-content">
            <h3>Social Media Profiles ({report.social_media?.length || 0})</h3>
            {report.social_media?.length > 0 ? (
              <div className="social-profiles">
                {report.social_media.map((profile, index) => (
                  <SocialMediaProfile key={index} profile={profile} />
                ))}
              </div>
            ) : (
              <p className="no-records">No social media profiles found.</p>
            )}
          </div>
        );
      
      case 'property':
        return (
          <div className="property-content" data-testid="property-content">
            <h3>Property Records ({report.property_records?.length || 0})</h3>
            {report.property_records?.length > 0 ? (
              <div className="property-records">
                {report.property_records.map((property, index) => (
                  <div key={index} className="property-record">
                    <h4>{property.address}</h4>
                    <div className="property-details">
                      <span>Type: {property.property_type}</span>
                      <span>Value: ${property.estimated_value?.toLocaleString() || 'Unknown'}</span>
                      <span>Owned Since: {property.ownership_date ? new Date(property.ownership_date).toLocaleDateString() : 'Unknown'}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-records">No property records found.</p>
            )}
          </div>
        );
      
      case 'professional':
        return (
          <div className="professional-content" data-testid="professional-content">
            <h3>Professional Information ({report.professional_info?.length || 0})</h3>
            {report.professional_info?.length > 0 ? (
              <div className="professional-records">
                {report.professional_info.map((job, index) => (
                  <div key={index} className="professional-record">
                    <h4>{job.position}</h4>
                    <div className="job-details">
                      <span>Company: {job.company}</span>
                      <span>Duration: {job.duration}</span>
                      <span>Location: {job.location}</span>
                      <span>Industry: {job.industry}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-records">No professional information found.</p>
            )}
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="background-report" data-testid="background-report">
      <div className="report-header">
        <h2>Background Report - {report.person_name}</h2>
        <span className="report-tier">Report Type: {report.report_tier?.toUpperCase()}</span>
      </div>
      
      <div className="report-tabs">
        {tabs.map(tab => (
          <ReportTab
            key={tab.id}
            title={tab.title}
            isActive={activeTab === tab.id}
            onClick={() => setActiveTab(tab.id)}
            count={tab.count}
          />
        ))}
      </div>
      
      <div className={`report-content ${activeTab}-theme`}>
        {renderTabContent()}
      </div>
    </div>
  );
};

const PaymentSuccess = ({ sessionId }) => {
  const [status, setStatus] = useState('checking');
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (sessionId) {
      pollPaymentStatus(
        sessionId,
        (data) => {
          setStatus('success');
          setReport(data.report);
        },
        (error) => {
          setStatus('error');
          setError(error);
        }
      );
    }
  }, [sessionId]);

  if (status === 'checking') {
    return (
      <div className="payment-status checking" data-testid="payment-checking">
        <h2>Processing Your Payment...</h2>
        <p>Please wait while we verify your payment and generate your report.</p>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="payment-status error" data-testid="payment-error">
        <h2>Payment Error</h2>
        <p>{error}</p>
        <button onClick={() => window.location.href = '/'}>Try Again</button>
      </div>
    );
  }

  return (
    <div className="payment-status success" data-testid="payment-success">
      <h2>Payment Successful!</h2>
      <p>Your background report is ready. Here's what we found:</p>
      {report && <BackgroundReport report={report} />}
    </div>
  );
};

// Helper function to get URL parameters
const getUrlParameter = (name) => {
  name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
  const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
  const results = regex.exec(window.location.search);
  return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};

// Main App Component
const App = () => {
  const [currentView, setCurrentView] = useState('home');
  const [searchResults, setSearchResults] = useState([]);
  const [currentReport, setCurrentReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pricing, setPricing] = useState(null);

  useEffect(() => {
    fetchPricing();
    
    // Check if returning from payment
    const sessionId = getUrlParameter('session_id');
    if (sessionId) {
      setCurrentView('payment-success');
    }
  }, []);

  const fetchPricing = async () => {
    try {
      const response = await axios.get(`${API}/pricing`);
      setPricing(response.data);
    } catch (err) {
      console.error('Error fetching pricing:', err);
    }
  };

  const handleSearch = async (query, searchType) => {
    setLoading(true);
    setError(null);
    try {
      // Convert frontend searchType to backend parameter names
      const params = {};
      if (searchType === 'name') params.name = query;
      else if (searchType === 'phone') params.phone = query;
      else if (searchType === 'email') params.email = query;
      else if (searchType === 'address') params.address = query;
      else params.name = query; // default to name search
      
      const response = await axios.get(`${API}/search`, { params });
      setSearchResults(response.data.results);
      setCurrentView('results');
    } catch (err) {
      setError('Search failed. Please try again.');
      console.error('Search error:', err);
    }
    setLoading(false);
  };

  const handleGetReport = async (personId, packageId) => {
    setLoading(true);
    setError(null);
    
    try {
      const originUrl = window.location.origin;
      
      const response = await axios.post(`${API}/payments/checkout`, {
        package_id: packageId,
        person_id: personId,
        origin_url: originUrl
      });

      if (response.data.type === 'free_report') {
        // Free report - show immediately
        setCurrentReport(response.data.report);
        setCurrentView('report');
      } else {
        // Paid report - redirect to Stripe
        window.location.href = response.data.checkout_url;
      }
    } catch (err) {
      setError('Failed to process request. Please try again.');
      console.error('Report error:', err);
    }
    setLoading(false);
  };

  const handlePlanSelect = (packageId, price) => {
    if (searchResults.length > 0) {
      handleGetReport(searchResults[0].id, packageId);
    } else {
      setError('Please search for someone first');
    }
  };

  // Handle payment success page
  if (currentView === 'payment-success') {
    const sessionId = getUrlParameter('session_id');
    return (
      <div className="app" data-testid="scanem-app">
        <header className="app-header">
          <div className="header-content">
            <h1 className="app-title" onClick={() => setCurrentView('home')}>
              Scan'Em
            </h1>
            <p className="app-tagline">Street Smart Advice • Know Who You're Dealing With • Avoid The Drama</p>
          </div>
        </header>
        <main className="app-main">
          <PaymentSuccess sessionId={sessionId} />
        </main>
      </div>
    );
  }

  return (
    <div className="app" data-testid="scanem-app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title" onClick={() => setCurrentView('home')}>
            Scan'Em
          </h1>
          <p className="app-tagline">Street Smart Advice • Know Who You're Dealing With • Avoid The Drama</p>
        </div>
        <nav className="header-nav">
          <button 
            className="nav-link" 
            onClick={() => setCurrentView('home')}
            data-testid="nav-home"
          >
            Home
          </button>
          <button 
            className="nav-link" 
            onClick={() => setCurrentView('pricing')}
            data-testid="nav-pricing"
          >
            Pricing
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
              <h2 className="hero-title">Smart to Know Who's Around You</h2>
              <p className="hero-subtitle">
                Whether it's a new neighbor, coworker, or potential friend - a little background check never hurt. 
                See what kind of records they have, make better decisions, avoid unnecessary drama. 
                A few bucks for peace of mind. <strong>Just being smart about it.</strong>
              </p>
            </div>
            
            <SearchBar onSearch={handleSearch} loading={loading} />
            
            <div className="features-section">
              <h3>Make Smarter Decisions</h3>
              <div className="features-grid">
                <div className="feature-card">
                  <h4>🔍 See Their Background</h4>
                  <p>Court cases, arrests, what they've been up to. Better to know upfront than be surprised later.</p>
                </div>
                <div className="feature-card">
                  <h4>💰 Worth the Investment</h4>
                  <p>Small price for big peace of mind. Your safety and good judgment are worth more than a few dollars.</p>
                </div>
                <div className="feature-card">
                  <h4>⚡ Quick & Easy</h4>
                  <p>AI finds what you need in seconds. No waiting, no hassle - just the info you want.</p>
                </div>
                <div className="feature-card">
                  <h4>👥 Know Who's Around</h4>
                  <p>New neighbors, coworkers, potential friends - just check 'em out. Nothing creepy, just smart.</p>
                </div>
                <div className="feature-card">
                  <h4>🏘️ Stay Informed</h4>
                  <p>Service workers, people in your area - a little homework helps you make better decisions.</p>
                </div>
                <div className="feature-card">
                  <h4>⚖️ Clear Information</h4>
                  <p>Accused vs convicted vs dropped charges - we explain what it all means in plain English.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentView === 'results' && (
          <div className="results-view" data-testid="results-view">
            <div className="results-header">
              <h2>Search Results</h2>
              <button 
                className="back-button" 
                onClick={() => setCurrentView('home')}
                data-testid="back-to-search"
              >
                ← New Search
              </button>
            </div>
            
            {searchResults.map(result => (
              <div key={result.id} className="result-card">
                <div className="result-info">
                  <h3>{result.name}</h3>
                  <p>Age: {result.age} • Location: {result.location}</p>
                  <p className="result-preview">{result.preview}</p>
                </div>
                <div className="result-actions">
                  <button 
                    className="btn-free" 
                    onClick={() => handleGetReport(result.id, 'free')}
                    data-testid="get-free-report"
                  >
                    Free Report
                  </button>
                  <button 
                    className="btn-basic" 
                    onClick={() => handleGetReport(result.id, 'basic')}
                    data-testid="get-basic-report"
                  >
                    Basic ($2.99)
                  </button>
                  <button 
                    className="btn-premium" 
                    onClick={() => handleGetReport(result.id, 'premium')}
                    data-testid="get-premium-report"
                  >
                    Premium ($5.99)
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {currentView === 'pricing' && pricing && (
          <div className="pricing-view" data-testid="pricing-view">
            <h2 className="pricing-header">Simple, Transparent Pricing</h2>
            
            <div className="pricing-cards">
              <PricingCard
                packageId="free"
                name={pricing.packages.free.name}
                price={pricing.packages.free.price}
                features={pricing.packages.free.features}
                onSelect={handlePlanSelect}
              />
              
              <PricingCard
                packageId="basic"
                name={pricing.packages.basic.name}
                price={pricing.packages.basic.price}
                features={pricing.packages.basic.features}
                onSelect={handlePlanSelect}
              />
              
              <PricingCard
                packageId="premium"
                name={pricing.packages.premium.name}
                price={pricing.packages.premium.price}
                features={pricing.packages.premium.features}
                isPopular={true}
                onSelect={handlePlanSelect}
              />
            </div>
            
            <div className="subscription-section">
              <h3>Subscription Plans</h3>
              <div className="subscription-cards">
                <div className="subscription-card">
                  <h4>{pricing.subscriptions.subscription_basic.name}</h4>
                  <p className="sub-price">${pricing.subscriptions.subscription_basic.price}/month</p>
                  <p>{pricing.subscriptions.subscription_basic.reports} reports included</p>
                  <p className="sub-savings">{pricing.subscriptions.subscription_basic.savings}</p>
                </div>
                <div className="subscription-card">
                  <h4>{pricing.subscriptions.subscription_pro.name}</h4>
                  <p className="sub-price">${pricing.subscriptions.subscription_pro.price}/month</p>
                  <p>{pricing.subscriptions.subscription_pro.reports} reports included</p>
                  <p className="sub-savings">{pricing.subscriptions.subscription_pro.savings}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentView === 'report' && currentReport && (
          <div className="report-view" data-testid="report-view">
            <div className="report-navigation">
              <button 
                className="back-button" 
                onClick={() => setCurrentView('results')}
                data-testid="back-to-results"
              >
                ← Back to Results
              </button>
            </div>
            <BackgroundReport report={currentReport} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>© 2025 Scan'Em. Street smart advice. Better safe than sorry.</p>
      </footer>
    </div>
  );
};

export default App;