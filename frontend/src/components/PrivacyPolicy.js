import React from 'react';

const PrivacyPolicy = ({ onClose }) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="legal-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Privacy Policy</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        <div className="modal-content">
          <p><strong>Last Updated:</strong> {new Date().toLocaleDateString()}</p>
          
          <h3>Information We Collect</h3>
          <p>We collect minimal information to provide our services:</p>
          <ul>
            <li><strong>Payment Information:</strong> Processed securely through Stripe. We do NOT store your credit card details.</li>
            <li><strong>Purchase History:</strong> Records of bundles you've purchased to grant access.</li>
            <li><strong>Usage Data:</strong> Basic analytics about which bundles are accessed.</li>
          </ul>

          <h3>What We DON'T Collect</h3>
          <ul>
            <li>❌ Your personal legal situations or cases</li>
            <li>❌ Criminal history or background information</li>
            <li>❌ Social security numbers or sensitive personal data</li>
            <li>❌ Location tracking beyond basic IP-based analytics</li>
          </ul>

          <h3>How We Use Your Information</h3>
          <ul>
            <li>Process your payments securely</li>
            <li>Grant access to purchased content</li>
            <li>Send purchase confirmations</li>
            <li>Improve our service</li>
          </ul>

          <h3>Data Security</h3>
          <p>We use industry-standard security measures to protect your information. Payment processing is handled by Stripe, a PCI-compliant payment processor.</p>

          <h3>Third-Party Services</h3>
          <ul>
            <li><strong>Stripe:</strong> Payment processing (see Stripe's privacy policy)</li>
            <li><strong>MongoDB:</strong> Secure database storage</li>
          </ul>

          <h3>Your Rights</h3>
          <p>You have the right to:</p>
          <ul>
            <li>Access your data</li>
            <li>Request deletion of your data</li>
            <li>Opt out of marketing communications</li>
            <li>Request data correction</li>
          </ul>

          <h3>Data Retention</h3>
          <p>We retain purchase records for accounting purposes. You may request deletion at any time by contacting us.</p>

          <h3>Children's Privacy</h3>
          <p>This service is not intended for users under 13. We do not knowingly collect information from children.</p>

          <h3>Contact Us</h3>
          <p>For privacy questions or data requests, contact us at: [Your contact email]</p>

          <p><em>This app provides general legal information only and does not create an attorney-client relationship.</em></p>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;
