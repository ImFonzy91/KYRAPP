import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
    </div>
  );
};

const PricingCard = ({ tier, price, features, isPopular = false, onSelect }) => (
  <div className={`pricing-card ${isPopular ? 'popular' : ''}`}>
    {isPopular && <div className="popular-badge">Most Popular</div>}
    <h3 className="pricing-title">{tier}</h3>
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
      onClick={() => onSelect(tier.toLowerCase().replace(' ', '_'), price)}
      data-testid={`select-${tier.toLowerCase().replace(' ', '-')}-plan`}
    >
      {price === 0 ? 'Try Free' : 'Get Report'}
    </button>
  </div>
);

const ReportTab = ({ title, isActive, onClick, count = null }) => (
  <button
    className={`report-tab ${isActive ? 'active' : ''}`}
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
      
      <div className="report-content">
        {renderTabContent()}
      </div>
    </div>
  );
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
      const response = await axios.post(`${API}/search`, {}, {
        params: { query, search_type: searchType }
      });
      setSearchResults(response.data.results);
      setCurrentView('results');
    } catch (err) {
      setError('Search failed. Please try again.');
      console.error('Search error:', err);
    }
    setLoading(false);
  };

  const handleGetReport = async (personId, tier = 'free') => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API}/report/${personId}`, {
        params: { tier }
      });
      setCurrentReport(response.data);
      setCurrentView('report');
    } catch (err) {
      setError('Failed to generate report. Please try again.');
      console.error('Report error:', err);
    }
    setLoading(false);
  };

  const handlePlanSelect = (planType, price) => {
    if (price === 0) {
      // Free tier - generate free report
      if (searchResults.length > 0) {
        handleGetReport(searchResults[0].id, 'free');
      }
    } else {
      // Paid plans - would integrate with payment processor
      alert(`Payment integration would process $${price} for ${planType} plan`);
    }
  };

  return (
    <div className="app" data-testid="peoplecheck-app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title" onClick={() => setCurrentView('home')}>
            PeopleCheck AI
          </h1>
          <p className="app-tagline">AI-Powered Background Checks • Instant Results • Smart Analysis</p>
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
              <h2 className="hero-title">Find Anyone. Know Everything.</h2>
              <p className="hero-subtitle">
                Get comprehensive background checks with criminal records, social media profiles, 
                and more. Perfect for meeting new people, hiring decisions, or personal verification.
              </p>
            </div>
            
            <SearchBar onSearch={handleSearch} loading={loading} />
            
            <div className="features-section">
              <h3>Why Choose PeopleCheck?</h3>
              <div className="features-grid">
                <div className="feature-card">
                  <h4>📋 Comprehensive Reports</h4>
                  <p>Criminal records, social media, property, and professional information</p>
                </div>
                <div className="feature-card">
                  <h4>⚖️ Legal Clarity</h4>
                  <p>Clear case statuses - pending, dismissed, or convicted with full context</p>
                </div>
                <div className="feature-card">
                  <h4>🔒 Privacy Focused</h4>
                  <p>No spam emails, no hidden fees, legitimate use only</p>
                </div>
                <div className="feature-card">
                  <h4>💰 Affordable Pricing</h4>
                  <p>Starting free with competitive paid options</p>
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
                tier="Free Daily Check"
                price={0}
                features={pricing.free_tier.features}
                onSelect={handlePlanSelect}
              />
              
              <PricingCard
                tier="Basic Report"
                price={pricing.pay_per_report.basic.price}
                features={pricing.pay_per_report.basic.features}
                onSelect={handlePlanSelect}
              />
              
              <PricingCard
                tier="Premium Report"
                price={pricing.pay_per_report.premium.price}
                features={pricing.pay_per_report.premium.features}
                isPopular={true}
                onSelect={handlePlanSelect}
              />
            </div>
            
            <div className="subscription-section">
              <h3>Subscription Plans</h3>
              <div className="subscription-cards">
                <div className="subscription-card">
                  <h4>{pricing.subscriptions.basic.name}</h4>
                  <p className="sub-price">${pricing.subscriptions.basic.price}/month</p>
                  <p>{pricing.subscriptions.basic.reports} reports included</p>
                  <p className="sub-savings">{pricing.subscriptions.basic.savings}</p>
                </div>
                <div className="subscription-card">
                  <h4>{pricing.subscriptions.professional.name}</h4>
                  <p className="sub-price">${pricing.subscriptions.professional.price}/month</p>
                  <p>{pricing.subscriptions.professional.reports} reports included</p>
                  <p className="sub-savings">{pricing.subscriptions.professional.savings}</p>
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
        <p>© 2025 PeopleCheck. Legitimate use only. All data from public records.</p>
      </footer>
    </div>
  );
};

export default App;