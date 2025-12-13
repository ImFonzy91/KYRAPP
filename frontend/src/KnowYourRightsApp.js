import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Price comparison messages for loading screens
const PRICE_COMPARISONS = [
  { competitor: "L*****Z***", their_price: "$299/year", our_price: "$10 one-time", savings: "96%" },
  { competitor: "R*****", their_price: "$39.99/month", our_price: "$2.99/bundle", savings: "92%" },
  { competitor: "Legal S**** Pro", their_price: "$149/consultation", our_price: "$3 for 5 AI consults", savings: "98%" },
  { competitor: "A*** L***** App", their_price: "$19.99/month", our_price: "$10 lifetime", savings: "95%" },
  { competitor: "Law F*** Online", their_price: "$79/document", our_price: "All rights included", savings: "100%" },
];

const LOADING_MESSAGES = [
  "🎵 You know every lyric to 50 songs. But do you know 3 of your rights?",
  "💭 You memorized entire albums. Time to memorize what actually matters.",
  "🚫 Stop being a mark. Start knowing your shit.",
  "💪 Not about being a dick. It's about not being a victim.",
  "🧠 Your brain memorized every Cardi B song. Now give it something useful.",
  "⚖️ Stand up for yourself. All it takes is a little knowledge.",
  "🎤 iTunes got your money. Now invest in yourself.",
  "🔥 They count on you not knowing. Prove them wrong.",
  "💰 Lawyers charge $300/hr because you don't know this. Change that.",
  "📚 Swap the order. Learn your rights like you learn lyrics.",
];

// Loading component with price comparison
const LoadingWithComparison = ({ message }) => {
  const [comparisonIndex] = useState(Math.floor(Math.random() * PRICE_COMPARISONS.length));
  const [messageIndex] = useState(Math.floor(Math.random() * LOADING_MESSAGES.length));
  const comparison = PRICE_COMPARISONS[comparisonIndex];
  
  return (
    <div className="loading-comparison">
      <div className="loading-spinner"></div>
      <p className="loading-message">{message || LOADING_MESSAGES[messageIndex]}</p>
      
      <div className="price-compare-box">
        <div className="competitor-price">
          <span className="blurred-name">{comparison.competitor}</span>
          <span className="their-price">{comparison.their_price}</span>
        </div>
        <span className="vs">VS</span>
        <div className="our-price-box">
          <span className="us-label">Know Your Rights</span>
          <span className="our-price">{comparison.our_price}</span>
        </div>
        <div className="savings-badge">Save {comparison.savings}!</div>
      </div>
      
      <p className="loading-disclaimer">* We believe legal education should be affordable for everyone</p>
    </div>
  );
};

// Video content for ALL 13 RIGHTS BUNDLES
const VIDEO_CONTENT = {
  traffic: {
    name: "Traffic & Police Stops",
    icon: "🚗",
    videos: [
      { id: "RvjF2VW73hY", title: "NEW Supreme Court Ruling - Your Traffic Stop Rights", channel: "Hampton Law" },
      { id: "7A-MTqLHRzY", title: "Exact Words to Say During a Traffic Stop", channel: "Hampton Law" },
      { id: "ZG7wPR3NFJo", title: "How Cops TRICK You During Traffic Stops", channel: "Hampton Law" },
    ]
  },
  arrest: {
    name: "Criminal Defense & Arrest",
    icon: "⚖️",
    videos: [
      { id: "uqo5RYOp4nQ", title: "Shut The F*** Up Friday - Your Right to Remain Silent", channel: "Pot Brothers at Law" },
      { id: "t9Gt5MbxCgk", title: "How to Handle Police Encounters", channel: "Hampton Law" },
      { id: "ibb2Kt9SbE4", title: "Your Rights During an Arrest", channel: "Hampton Law" },
    ]
  },
  tenant: {
    name: "Housing & Tenant Rights",
    icon: "🏠",
    videos: [
      { id: "yqMjMPlXzdA", title: "Know Your Rights - Police at Your Door", channel: "Flex Your Rights" },
      { id: "WwgoBr3FJ7k", title: "Can Police Enter Your Home Without a Warrant?", channel: "Hampton Law" },
      { id: "ek-siMIEoYE", title: "10 Things Your Landlord Doesn't Want You To Know", channel: "LegalEagle" },
    ]
  },
  workplace: {
    name: "Workplace & Employment",
    icon: "💼",
    videos: [
      { id: "xgrQPAb6nCE", title: "Employment Rights You Need to Know", channel: "Hampton Law" },
      { id: "cmZX0U8vEnI", title: "Can You Get Fired For That? Know Your Rights", channel: "LegalEagle" },
    ]
  },
  property: {
    name: "Property Rights",
    icon: "🏡",
    videos: [
      { id: "Spo-m2Atdwg", title: "Property Rights Explained - What Can You Actually Do?", channel: "LegalEagle" },
      { id: "WwgoBr3FJ7k", title: "Can Police Search Your Property?", channel: "Hampton Law" },
    ]
  },
  landmines: {
    name: "Legal Landmines",
    icon: "💣",
    videos: [
      { id: "d-7o9xYp7eE", title: "5 Legal Mistakes That Could Ruin Your Life", channel: "LegalEagle" },
      { id: "ZG7wPR3NFJo", title: "Cops Use These Tricks - Don't Fall For Them", channel: "Hampton Law" },
    ]
  },
  family: {
    name: "Family Law Rights",
    icon: "👨‍👩‍👧",
    videos: [
      { id: "0IbWampaEcM", title: "Child Custody Rights You NEED to Know", channel: "Command the Courtroom" },
      { id: "TJlfBqMBqzE", title: "Family Court - What to Expect", channel: "LegalEagle" },
    ]
  },
  divorce: {
    name: "Divorce Rights",
    icon: "💔",
    videos: [
      { id: "CG-eYS0OCWA", title: "Divorce Rights - Protect Yourself", channel: "LegalEagle" },
      { id: "MnME-8J_Y94", title: "What NOT to Do During a Divorce", channel: "Command the Courtroom" },
    ]
  },
  immigration: {
    name: "Immigration Rights",
    icon: "🌍",
    videos: [
      { id: "hqhW4GaZyx8", title: "Know Your Rights with ICE - ACLU Guide", channel: "ACLU" },
      { id: "yqMjMPlXzdA", title: "Can ICE Enter Your Home? Know Your Rights", channel: "Flex Your Rights" },
    ]
  },
  healthcare: {
    name: "Healthcare Rights",
    icon: "🏥",
    videos: [
      { id: "WrzCUn6MNRE", title: "Your Medical Rights - What Hospitals Can't Do", channel: "LegalEagle" },
      { id: "PPwGh0l4fvk", title: "Medical Billing Rights - Fight Unfair Bills", channel: "LegalEagle" },
    ]
  },
  student: {
    name: "Student Rights",
    icon: "🎓",
    videos: [
      { id: "xZzrhn4Z6Gg", title: "Student Rights - What Schools Can't Do", channel: "LegalEagle" },
      { id: "Q629R5pKMrk", title: "Can School Search Your Stuff? Know Your Rights", channel: "Pot Brothers at Law" },
    ]
  },
  digital: {
    name: "Digital & Privacy Rights",
    icon: "📱",
    videos: [
      { id: "3c9MKUaLIco", title: "Can Police Search Your Phone?", channel: "Hampton Law" },
      { id: "Spo-m2Atdwg", title: "Your Digital Privacy Rights Explained", channel: "LegalEagle" },
    ]
  },
  consumer: {
    name: "Consumer & Debt Rights",
    icon: "💳",
    videos: [
      { id: "tq0vjCKHkwM", title: "Debt Collector Calling? Know Your Rights", channel: "LegalEagle" },
      { id: "n0kz5aqJldA", title: "How to Fight Debt Collectors and WIN", channel: "The Credit Shifu" },
    ]
  }
};

// Quiz Questions Database - REAL legal knowledge
const QUIZ_DATA = {
  traffic: {
    name: "Traffic Stop Rights",
    icon: "🚗",
    quizzes: [
      {
        id: 1,
        questions: [
          { q: "Can police search your car without a warrant?", a: "Only with probable cause or your consent", wrong: ["Yes, anytime they want", "No, never under any circumstances", "Only on weekends"] },
          { q: "What should you say to refuse a search?", a: "I do not consent to any searches", wrong: ["Please don't search me", "I'd rather you didn't", "Maybe later"] },
          { q: "Which Amendment protects against unreasonable searches?", a: "4th Amendment", wrong: ["1st Amendment", "2nd Amendment", "5th Amendment"] },
          { q: "Do you have to answer questions during a traffic stop?", a: "No, you can remain silent", wrong: ["Yes, it's required by law", "Only if asked nicely", "Yes, or you'll be arrested"] },
          { q: "Can you record police during a traffic stop?", a: "Yes, it's protected by the 1st Amendment", wrong: ["No, it's illegal", "Only with their permission", "Only in some states"] },
        ]
      },
      {
        id: 2,
        questions: [
          { q: "What documents must you provide when driving?", a: "License, registration, and insurance", wrong: ["Just your license", "Your social security card", "Nothing at all"] },
          { q: "Can you refuse a breathalyzer test?", a: "Yes, but you may lose your license", wrong: ["No, it's mandatory", "Yes, with no consequences", "Only if you're sober"] },
          { q: "What's the best phrase to use when pulled over?", a: "Am I free to go?", wrong: ["What's your badge number?", "I know my rights!", "You can't do this!"] },
          { q: "Can police order you out of the car?", a: "Yes, for officer safety", wrong: ["No, you can stay inside", "Only with a warrant", "Only if you're under arrest"] },
          { q: "If arrested during a stop, what should you do?", a: "Stay silent and ask for a lawyer", wrong: ["Explain your side", "Try to talk your way out", "Run away"] },
        ]
      },
      {
        id: 3,
        questions: [
          { q: "Can police search your phone during a traffic stop?", a: "No, they need a warrant", wrong: ["Yes, it's allowed", "Only if it's unlocked", "Only iPhones are protected"] },
          { q: "What is 'probable cause'?", a: "Reasonable belief a crime occurred", wrong: ["Police suspicion", "Your nervous behavior", "Driving at night"] },
          { q: "Can passengers be searched during a traffic stop?", a: "Only with consent or probable cause", wrong: ["Yes, automatically", "No, never", "Only the driver"] },
          { q: "What happens if police search illegally?", a: "Evidence may be thrown out in court", wrong: ["Nothing happens", "You automatically win", "Police get fired"] },
          { q: "DUI checkpoint - can you turn around?", a: "Yes, if you can do so legally", wrong: ["No, you must go through", "Only in California", "It's a felony to avoid"] },
        ]
      }
    ]
  },
  arrest: {
    name: "Arrest & Miranda Rights",
    icon: "⚖️",
    quizzes: [
      {
        id: 1,
        questions: [
          { q: "What are Miranda Rights?", a: "Right to remain silent and have an attorney", wrong: ["Right to make one phone call", "Right to resist arrest", "Right to know charges immediately"] },
          { q: "When must police read Miranda Rights?", a: "Before custodial interrogation", wrong: ["Immediately upon arrest", "Only for felonies", "Never, it's optional"] },
          { q: "Which Amendment gives you the right to remain silent?", a: "5th Amendment", wrong: ["1st Amendment", "4th Amendment", "6th Amendment"] },
          { q: "What should you say when arrested?", a: "I invoke my right to remain silent. I want a lawyer.", wrong: ["I didn't do it!", "Let me explain", "This is a mistake"] },
          { q: "Can police question you after you ask for a lawyer?", a: "No, questioning must stop", wrong: ["Yes, if they really need to", "Only for serious crimes", "Yes, after 24 hours"] },
        ]
      },
      {
        id: 2,
        questions: [
          { q: "Which Amendment guarantees right to an attorney?", a: "6th Amendment", wrong: ["5th Amendment", "4th Amendment", "8th Amendment"] },
          { q: "What if you can't afford a lawyer?", a: "One will be provided free (public defender)", wrong: ["You must represent yourself", "You have to find the money", "You can't be tried"] },
          { q: "Can you be tried twice for the same crime?", a: "No, that's double jeopardy (5th Amendment)", wrong: ["Yes, if new evidence found", "Yes, in different courts", "Only for misdemeanors"] },
          { q: "What is 'due process'?", a: "Fair treatment through the legal system", wrong: ["Quick trial", "Police procedures", "Paying court fees"] },
          { q: "Should you talk to cellmates about your case?", a: "No, they could testify against you", wrong: ["Yes, get their advice", "Only if they're friendly", "Yes, practice your story"] },
        ]
      },
      {
        id: 3,
        questions: [
          { q: "What does 'presumption of innocence' mean?", a: "You're innocent until proven guilty", wrong: ["Police assume you're innocent", "Charges start at zero", "First offense is forgiven"] },
          { q: "Can you physically resist an unlawful arrest?", a: "No, fight it in court instead", wrong: ["Yes, if you're innocent", "Yes, it's your right", "Only with witnesses present"] },
          { q: "What's the 8th Amendment protect against?", a: "Excessive bail and cruel punishment", wrong: ["Unreasonable search", "Self-incrimination", "Speedy trial"] },
          { q: "How long can police hold you without charges?", a: "Usually 24-72 hours depending on state", wrong: ["Indefinitely", "Only 1 hour", "30 days"] },
          { q: "What should you NOT sign without a lawyer?", a: "Anything", wrong: ["Only confessions", "Only waivers", "Nothing, signing is fine"] },
        ]
      }
    ]
  },
  tenant: {
    name: "Tenant Rights",
    icon: "🏠",
    quizzes: [
      {
        id: 1,
        questions: [
          { q: "Can a landlord change locks to kick you out?", a: "No, that's illegal self-help eviction", wrong: ["Yes, it's their property", "Only with 24hr notice", "Yes, if you owe rent"] },
          { q: "How much notice must landlord give before entering?", a: "Usually 24-48 hours (varies by state)", wrong: ["None, it's their property", "1 week minimum", "Only if you're home"] },
          { q: "What law protects against housing discrimination?", a: "Fair Housing Act", wrong: ["Civil Rights Act only", "Housing Protection Act", "Tenant Security Act"] },
          { q: "Can landlord shut off utilities to force you out?", a: "No, that's illegal", wrong: ["Yes, if you owe rent", "Only electricity", "Yes, with court approval"] },
          { q: "What must landlord provide with security deposit deduction?", a: "Itemized list of damages", wrong: ["Nothing required", "Just the remaining amount", "A phone call explanation"] },
        ]
      },
      {
        id: 2,
        questions: [
          { q: "What is 'habitability'?", a: "Landlord must provide safe, livable conditions", wrong: ["Right to decorate", "Luxury amenities required", "Free repairs"] },
          { q: "Can you withhold rent for repairs?", a: "In some states, for serious issues", wrong: ["Yes, anytime", "No, never allowed", "Only for cosmetic issues"] },
          { q: "What's considered 'normal wear and tear'?", a: "Minor scuffs, faded paint, worn carpet", wrong: ["Holes in walls", "Broken windows", "Missing fixtures"] },
          { q: "Can landlord evict in retaliation for complaints?", a: "No, retaliation is illegal", wrong: ["Yes, it's their right", "Only in some states", "After 6 months they can"] },
          { q: "How long for security deposit return (typically)?", a: "15-60 days depending on state", wrong: ["Whenever they want", "1 year", "Only after you ask"] },
        ]
      },
      {
        id: 3,
        questions: [
          { q: "Can landlord refuse to rent based on race?", a: "No, violates Fair Housing Act", wrong: ["Yes, owner's choice", "Only for apartments", "If they have a reason"] },
          { q: "What's required for a legal eviction?", a: "Written notice and court order", wrong: ["Verbal warning only", "Just changing locks", "30 days notice only"] },
          { q: "Can landlord enter for 'emergencies' without notice?", a: "Yes, for true emergencies only", wrong: ["No, never without notice", "Yes, anytime they say emergency", "Only with police"] },
          { q: "Who enforces Fair Housing Act?", a: "HUD (Housing and Urban Development)", wrong: ["Local police", "FBI", "State governor"] },
          { q: "Can landlord raise rent during lease?", a: "Generally no, unless lease allows", wrong: ["Yes, with 30 days notice", "Yes, anytime", "Only 10% per year"] },
        ]
      }
    ]
  },
  workplace: {
    name: "Workplace Rights",
    icon: "💼",
    quizzes: [
      {
        id: 1,
        questions: [
          { q: "What law requires overtime pay?", a: "Fair Labor Standards Act (FLSA)", wrong: ["Worker Protection Act", "Employment Rights Act", "Overtime Pay Act"] },
          { q: "At what hours does overtime kick in?", a: "Over 40 hours per week", wrong: ["Over 8 hours per day", "Over 50 hours", "Any extra hours"] },
          { q: "Can your boss make you work off the clock?", a: "No, that's wage theft", wrong: ["Yes, if asked nicely", "Only for small tasks", "Yes, if you're salaried"] },
          { q: "What agency handles workplace safety?", a: "OSHA", wrong: ["FBI", "FDA", "SEC"] },
          { q: "Can you be fired for reporting safety violations?", a: "No, that's illegal retaliation", wrong: ["Yes, at-will employment", "Only in unions", "After 90 days yes"] },
        ]
      },
      {
        id: 2,
        questions: [
          { q: "What law protects against workplace discrimination?", a: "Title VII of Civil Rights Act", wrong: ["FLSA", "OSHA", "ADA only"] },
          { q: "What is sexual harassment?", a: "Unwelcome sexual conduct affecting work", wrong: ["Only physical contact", "Only from supervisors", "Only repeated behavior"] },
          { q: "What does ADA stand for?", a: "Americans with Disabilities Act", wrong: ["American Defense Act", "Anti-Discrimination Act", "American Disability Association"] },
          { q: "Can employer ask about your religion in interview?", a: "Generally no, it's discriminatory", wrong: ["Yes, for scheduling", "Yes, it's legal", "Only government jobs"] },
          { q: "What is FMLA?", a: "Family and Medical Leave Act - up to 12 weeks unpaid leave", wrong: ["Fair Medical Leave Act", "Federal Minimum Labor Act", "Family Money Loan Act"] },
        ]
      },
      {
        id: 3,
        questions: [
          { q: "Can you be fired for discussing wages with coworkers?", a: "No, that's protected (NLRA)", wrong: ["Yes, it's confidential", "Only if policy says so", "Yes, it causes drama"] },
          { q: "Federal minimum wage as of 2024?", a: "$7.25/hour (states may be higher)", wrong: ["$15/hour", "$10/hour", "$5/hour"] },
          { q: "What's 'at-will employment'?", a: "Either party can end job anytime for legal reasons", wrong: ["You must give 2 weeks", "Employer needs cause", "Only in some states"] },
          { q: "Who investigates workplace discrimination?", a: "EEOC", wrong: ["FBI", "State police", "OSHA"] },
          { q: "Can employer require unpaid training?", a: "Generally no if it benefits employer", wrong: ["Yes, always legal", "Only for first week", "Yes, if under 40 hours"] },
        ]
      }
    ]
  }
};

// Badge definitions - COD style progression
const BADGES = [
  // Starter badges (easy to get)
  { id: 'first_blood', name: 'First Blood', icon: '🩸', requirement: 'Answer your first question right', category: 'starter' },
  { id: 'rookie', name: 'Rights Rookie', icon: '🥉', requirement: 'Complete 1 quiz', category: 'progress' },
  { id: 'quick_draw', name: 'Quick Draw', icon: '⚡', requirement: 'Answer in under 3 seconds', category: 'speed' },
  
  // Streak badges
  { id: 'hot_streak', name: 'Hot Streak', icon: '🔥', requirement: '3 correct in a row', category: 'streak' },
  { id: 'on_fire', name: 'On Fire', icon: '💥', requirement: '5 correct in a row', category: 'streak' },
  { id: 'smoking_gun', name: 'Smoking Gun', icon: '🔫', requirement: 'Perfect quiz - no mistakes', category: 'streak' },
  { id: 'unstoppable', name: 'Unstoppable', icon: '💀', requirement: '10 correct in a row', category: 'streak' },
  
  // Progress badges
  { id: 'learner', name: 'Legal Learner', icon: '📚', requirement: 'Pass 3 quizzes', category: 'progress' },
  { id: 'scholar', name: 'Street Scholar', icon: '🎓', requirement: 'Pass 6 quizzes', category: 'progress' },
  { id: 'defender', name: 'Constitution Defender', icon: '🛡️', requirement: 'Pass all 12 quizzes', category: 'progress' },
  
  // Mastery badges
  { id: 'traffic_master', name: 'Road Warrior', icon: '🚗', requirement: 'Master all Traffic quizzes', category: 'mastery' },
  { id: 'arrest_master', name: 'Silent Assassin', icon: '🤐', requirement: 'Master all Arrest quizzes', category: 'mastery' },
  { id: 'tenant_master', name: 'Landlord Slayer', icon: '🏠', requirement: 'Master all Tenant quizzes', category: 'mastery' },
  { id: 'work_master', name: 'Boss Fighter', icon: '💼', requirement: 'Master all Workplace quizzes', category: 'mastery' },
  
  // Elite badges
  { id: 'speed_demon', name: 'Speed Demon', icon: '👹', requirement: 'Complete quiz with 5+ seconds left each', category: 'elite' },
  { id: 'fox', name: 'Sneaky Fox', icon: '🦊', requirement: '90%+ accuracy overall', category: 'elite' },
  { id: 'eagle', name: 'Legal Eagle', icon: '🦅', requirement: 'Perfect score on hard quiz', category: 'elite' },
  { id: 'legend', name: 'Rights Legend', icon: '👑', requirement: 'Earn all other badges', category: 'legend' },
  
  // Secret badges
  { id: 'comeback_kid', name: 'Comeback Kid', icon: '🔄', requirement: 'Miss 2 then get 3 right', category: 'secret' },
  { id: 'clutch', name: 'Clutch Master', icon: '🎯', requirement: 'Get last question right with <2 sec', category: 'secret' },
  { id: 'night_owl', name: 'Night Owl', icon: '🦉', requirement: 'Quiz after midnight', category: 'secret' },
];

// Difficulty levels
const DIFFICULTY_MULTIPLIER = {
  easy: { time: 12, label: 'Easy', color: '#4ecdc4' },
  medium: { time: 9, label: 'Medium', color: '#ffd700' },
  hard: { time: 6, label: 'Hard', color: '#ff6b6b' },
};

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
        <p>Stop being a mark. Start standing up for yourself.</p>
      </div>

      <div className="empowerment-message">
        <p>🎵 You memorized every song on your playlist.</p>
        <p>❓ But can you name 3 of your constitutional rights?</p>
        <p className="swap-message">💡 <strong>Swap the order.</strong> Learn what actually matters.</p>
      </div>

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
          </div>
        )}
      </div>

      <div className="auth-box">
        <div className="auth-tabs">
          <button className={isLogin ? 'active' : ''} onClick={() => setIsLogin(true)}>Login</button>
          <button className={!isLogin ? 'active' : ''} onClick={() => setIsLogin(false)}>Sign Up</button>
        </div>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <input type="text" placeholder="Your Name" value={name} onChange={(e) => setName(e.target.value)} required={!isLogin} />
          )}
          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Create Account')}
          </button>
        </form>
      </div>

      <div className="flash-sale-banner">
        <h3>🔥 48-HOUR FLASH SALE 🔥</h3>
        <p><strong>$10</strong> = ALL 13 Rights Bundles</p>
        <p><strong>$3</strong> = 5 AI Case Consultations</p>
      </div>
    </div>
  );
};

// Tab: Learn - All 13 Rights Bundles with Videos (LOCKED UNTIL PURCHASED)
const LearnTab = ({ user }) => {
  const [selectedBundle, setSelectedBundle] = useState(null);
  const [activeVideo, setActiveVideo] = useState(null);
  const [purchasedBundles, setPurchasedBundles] = useState([]);
  const [showStore, setShowStore] = useState(false);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchPurchasedBundles();
  }, []);

  const fetchPurchasedBundles = async () => {
    try {
      const response = await axios.get(`${API}/user/bundles`, { params: { user_id: user.id } });
      setPurchasedBundles(response.data.bundles?.map(b => b.id) || []);
    } catch (err) {
      console.error('Failed to fetch bundles:', err);
    }
  };

  const isUnlocked = (bundleId) => {
    return purchasedBundles.includes(bundleId) || purchasedBundles.includes('all');
  };

  const toggleCart = (bundleId) => {
    if (cart.includes(bundleId)) {
      setCart(cart.filter(id => id !== bundleId));
    } else {
      setCart([...cart, bundleId]);
    }
  };

  const getPrice = () => {
    if (cart.length === 0) return { price: 0, label: 'Select bundles' };
    return { price: cart.length * 2.99, label: `${cart.length} Bundle${cart.length > 1 ? 's' : ''}` };
  };

  const handlePremiumPurchase = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/purchase/cart`, {
        user_id: user.id,
        bundle_ids: ['premium'],
        origin_url: window.location.origin
      });
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (err) {
      alert('Checkout failed. Please try again.');
    }
    setLoading(false);
  };

  const handleCheckout = async () => {
    if (cart.length === 0) return;
    setLoading(true);
    try {
      const response = await axios.post(`${API}/purchase/cart`, {
        user_id: user.id,
        bundle_ids: cart.length >= 13 ? ['all'] : cart,
        origin_url: window.location.origin
      });
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (err) {
      alert('Checkout failed. Please try again.');
    }
    setLoading(false);
  };

  const buyAllBundles = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/purchase/cart`, {
        user_id: user.id,
        bundle_ids: ['all'],
        origin_url: window.location.origin
      });
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (err) {
      alert('Checkout failed. Please try again.');
    }
    setLoading(false);
  };

  // Viewing a purchased bundle
  if (selectedBundle && isUnlocked(selectedBundle)) {
    const bundle = VIDEO_CONTENT[selectedBundle];
    return (
      <div className="learn-bundle-view">
        <button className="back-btn" onClick={() => { setSelectedBundle(null); setActiveVideo(null); }}>← Back to All Rights</button>
        <h2>{bundle.icon} {bundle.name}</h2>
        
        {activeVideo ? (
          <div className="video-player">
            <div className="video-container">
              <iframe
                src={`https://www.youtube.com/embed/${activeVideo.id}?autoplay=1`}
                title={activeVideo.title}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            </div>
            <h3>{activeVideo.title}</h3>
            <p className="video-channel">📺 {activeVideo.channel}</p>
            <button className="close-video-btn" onClick={() => setActiveVideo(null)}>← Watch Another Video</button>
          </div>
        ) : (
          <div className="video-grid">
            {bundle.videos.map((video, i) => (
              <div key={i} className="video-card" onClick={() => setActiveVideo(video)}>
                <div className="video-thumbnail">
                  <img src={`https://img.youtube.com/vi/${video.id}/mqdefault.jpg`} alt={video.title} />
                  <div className="play-overlay">▶</div>
                </div>
                <h4>{video.title}</h4>
                <p className="video-channel">📺 {video.channel}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="learn-tab">
      <h2>🎬 Know Your Rights - 13 Bundles</h2>
      <p>Unlock the knowledge that could save you thousands</p>
      
      {/* Flash Sale Banner */}
      <div className="store-banner">
        <div className="premium-deal" onClick={() => handlePremiumPurchase()}>
          <span className="deal-badge">⚡ LIMITED TIME</span>
          <h3>PREMIUM UNLIMITED - $20</h3>
          <p>All 13 Bundles + Lifetime Updates Forever</p>
          <p className="limited-text">🔥 Offer ends Jan 31, 2025</p>
          <button disabled={loading}>{loading ? 'Processing...' : 'GET PREMIUM →'}</button>
        </div>
        <div className="other-deals">
          <div className="deal-item clickable" onClick={buyAllBundles}>
            <div>
              <span>📦 All 13 Bundles</span>
              <p className="deal-desc">One-time purchase</p>
            </div>
            <strong>$10</strong>
          </div>
          <div className="deal-item">
            <div>
              <span>📄 Single Bundle</span>
              <p className="deal-desc">Pick what you need</p>
            </div>
            <strong>$2.99</strong>
          </div>
        </div>
      </div>

      {/* Cart */}
      {cart.length > 0 && (
        <div className="shopping-cart">
          <div className="cart-info">
            <span>🛒 {cart.length} bundle{cart.length > 1 ? 's' : ''} selected</span>
            <strong>${getPrice().price.toFixed(2)}</strong>
          </div>
          <button className="checkout-btn" onClick={handleCheckout} disabled={loading}>
            {loading ? 'Processing...' : `Checkout - $${getPrice().price.toFixed(2)}`}
          </button>
        </div>
      )}

      {/* Bundle Grid */}
      <div className="bundles-grid-learn">
        {Object.entries(VIDEO_CONTENT).map(([key, bundle]) => {
          const unlocked = isUnlocked(key);
          const inCart = cart.includes(key);
          
          return (
            <div 
              key={key} 
              className={`bundle-learn-card ${unlocked ? 'unlocked' : 'locked'} ${inCart ? 'in-cart' : ''}`}
            >
              {!unlocked && <div className="lock-icon">🔒</div>}
              {unlocked && <div className="unlock-icon">✅</div>}
              {inCart && <div className="cart-check">🛒</div>}
              
              <span className="bundle-icon-large">{bundle.icon}</span>
              <h3>{bundle.name}</h3>
              <p className="video-count">{bundle.videos.length} Videos</p>
              
              {unlocked ? (
                <button className="watch-btn" onClick={() => setSelectedBundle(key)}>Watch Now →</button>
              ) : (
                <button 
                  className={`buy-btn ${inCart ? 'in-cart' : ''}`}
                  onClick={() => toggleCart(key)}
                >
                  {inCart ? '✓ In Cart - Click to Remove' : '$2.99 - Add to Cart'}
                </button>
              )}
            </div>
          );
        })}
      </div>

      <div className="purchase-note">
        <p>💡 <strong>Why pay?</strong> Lawyers charge $300/hr for this info. You're getting lifetime access for less than a coffee.</p>
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
      const response = await axios.get(`${API}/search/rights`, { params: { query } });
      setResults(response.data.results || []);
    } catch (err) {
      console.error('Search failed:', err);
    }
    setLoading(false);
  };

  if (loading) {
    return <LoadingWithComparison message="🔍 Finding your rights..." />;
  }

  if (selectedRight) {
    return (
      <div className="right-details">
        <button className="back-btn" onClick={() => setSelectedRight(null)}>← Back</button>
        <h2>{selectedRight.title}</h2>
        <p className="source"><strong>Source:</strong> {selectedRight.source}</p>
        
        {selectedRight.text && (
          <div className="legal-text">
            <h4>📜 Actual Legal Text:</h4>
            <blockquote>"{selectedRight.text}"</blockquote>
          </div>
        )}
        
        {selectedRight.what_it_means && (
          <div className="what-it-means">
            <h4>💡 What This Means For You:</h4>
            <ul>{selectedRight.what_it_means.map((item, i) => <li key={i}>{item}</li>)}</ul>
          </div>
        )}

        {selectedRight.what_to_do && (
          <div className="what-to-do">
            <h4>✅ What To Do:</h4>
            <ul>{selectedRight.what_to_do.map((item, i) => <li key={i}>{item}</li>)}</ul>
          </div>
        )}

        {selectedRight.magic_phrases && (
          <div className="magic-phrases">
            <h4>🗣️ Say These Exact Words:</h4>
            <ul>{selectedRight.magic_phrases.map((phrase, i) => <li key={i} className="magic-phrase">"{phrase}"</li>)}</ul>
          </div>
        )}

        {selectedRight.legal_requirements && (
          <div className="requirements">
            <h4>📋 What You Must Provide:</h4>
            <ul>{selectedRight.legal_requirements.must_provide?.map((item, i) => <li key={i}>✅ {item}</li>)}</ul>
            <h4>🚫 What You Do NOT Have To Do:</h4>
            <ul>{selectedRight.legal_requirements.not_required?.map((item, i) => <li key={i}>❌ {item}</li>)}</ul>
          </div>
        )}

        {/* Employment/Workplace Rights - Federal Laws with descriptions */}
        {selectedRight.federal_laws && (
          <div className="federal-laws-detail">
            <h4>📚 Federal Laws That Protect You:</h4>
            {Object.entries(selectedRight.federal_laws).map(([key, law]) => (
              <div key={key} className="law-card">
                <h5>{law.name}</h5>
                <p className="law-description">
                  {key === 'flsa' && "The FLSA sets minimum wage, overtime pay, recordkeeping, and child labor standards. If your employer isn't paying you fairly, this law protects you."}
                  {key === 'title_vii' && "Title VII makes it illegal for employers to discriminate against you based on race, color, religion, sex, or national origin. This includes hiring, firing, pay, and promotions."}
                  {key === 'ada' && "The ADA prohibits discrimination against people with disabilities and requires employers to provide reasonable accommodations so you can do your job."}
                  {key === 'osha' && "OSHA ensures you have a safe workplace. Your employer must provide a workplace free from serious hazards. You can report unsafe conditions without fear of retaliation."}
                  {key === 'fmla' && "FMLA allows eligible employees to take unpaid, job-protected leave for family and medical reasons. Your job must be waiting for you when you return."}
                </p>
                {law.rights && (
                  <ul>{law.rights.map((r, i) => <li key={i}>✓ {r}</li>)}</ul>
                )}
                {law.protects_against && (
                  <ul>{law.protects_against.map((r, i) => <li key={i}>🛡️ Protection from: {r}</li>)}</ul>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Criminal Defense - Core Rights with descriptions */}
        {selectedRight.core_rights && (
          <div className="core-rights-detail">
            <h4>⚖️ Your Core Rights When Facing Criminal Charges:</h4>
            {selectedRight.core_rights.map((right, i) => (
              <div key={i} className="core-right-card">
                <h5>{right.right}</h5>
                <p>{right.meaning}</p>
              </div>
            ))}
          </div>
        )}

        {selectedRight.what_to_say && (
          <div className="what-to-say">
            <h4>🗣️ If You're Arrested, Say ONLY These Words:</h4>
            <ul>{selectedRight.what_to_say.map((phrase, i) => <li key={i} className="magic-phrase">"{phrase}"</li>)}</ul>
            <p className="warning">⚠️ After saying these phrases, STOP TALKING. Do not explain, do not justify. Wait for your lawyer.</p>
          </div>
        )}

        {/* Tenant Rights */}
        {selectedRight.common_rights && (
          <div className="tenant-rights-detail">
            <h4>🏠 Your Rights as a Tenant:</h4>
            <ul>{selectedRight.common_rights.map((item, i) => <li key={i}>✓ {item}</li>)}</ul>
          </div>
        )}

        {selectedRight.illegal_landlord_actions && (
          <div className="illegal-actions">
            <h4>🚫 Things Your Landlord CANNOT Do:</h4>
            <ul>{selectedRight.illegal_landlord_actions.map((item, i) => <li key={i}>❌ {item}</li>)}</ul>
          </div>
        )}

        {/* Immigration Rights */}
        {selectedRight.all_persons_have && (
          <div className="immigration-rights-detail">
            <h4>🌍 Rights ALL Persons Have (Regardless of Status):</h4>
            <ul>{selectedRight.all_persons_have.map((item, i) => <li key={i}>✓ {item}</li>)}</ul>
          </div>
        )}

        {selectedRight.ice_encounters && (
          <div className="ice-encounters-detail">
            <h4>🏠 If ICE Comes to Your Home:</h4>
            <ul>{selectedRight.ice_encounters.at_home?.map((item, i) => <li key={i}>{item}</li>)}</ul>
            <h4>🚶 If Encountered in Public:</h4>
            <ul>{selectedRight.ice_encounters.in_public?.map((item, i) => <li key={i}>{item}</li>)}</ul>
          </div>
        )}

        {/* Consumer Rights */}
        {selectedRight.debt_collection && (
          <div className="debt-rights-detail">
            <h4>💰 {selectedRight.debt_collection.law}</h4>
            <p className="law-description">Debt collectors CANNOT harass you. You have rights when dealing with collection agencies.</p>
            <ul>{selectedRight.debt_collection.protections?.map((item, i) => <li key={i}>✓ {item}</li>)}</ul>
            {selectedRight.debt_collection.magic_letter && (
              <p className="tip"><strong>Pro Tip:</strong> {selectedRight.debt_collection.magic_letter}</p>
            )}
          </div>
        )}

        {selectedRight.credit_reporting && (
          <div className="credit-rights-detail">
            <h4>📊 {selectedRight.credit_reporting.law}</h4>
            <ul>{selectedRight.credit_reporting.rights?.map((item, i) => <li key={i}>✓ {item}</li>)}</ul>
          </div>
        )}

        {selectedRight.fallback_note && (
          <div className="fallback-note">
            <p>💡 {selectedRight.fallback_note}</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="smart-search-tab">
      <h2>🔍 Smart Search</h2>
      <p>Type your situation and find your rights</p>
      
      <form onSubmit={handleSearch} className="search-form">
        <input type="text" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="e.g., 'pulled over', 'landlord', 'arrested'" />
        <button type="submit" disabled={loading}>{loading ? 'Searching...' : 'Search Rights'}</button>
      </form>

      <div className="quick-searches">
        <p>Quick searches:</p>
        <div className="quick-btns">
          <button onClick={() => setQuery('pulled over')}>🚗 Pulled Over</button>
          <button onClick={() => setQuery('arrested')}>⚖️ Arrested</button>
          <button onClick={() => setQuery('landlord')}>🏠 Landlord</button>
          <button onClick={() => setQuery('work harassment')}>💼 Workplace</button>
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
    </div>
  );
};

// Tab 2: Quiz Mode - COD Style Progression
const QuizTab = ({ user, updateUser }) => {
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [currentQuiz, setCurrentQuiz] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(9);
  const [answered, setAnswered] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [quizComplete, setQuizComplete] = useState(false);
  const [shuffledAnswers, setShuffledAnswers] = useState([]);
  const [streak, setStreak] = useState(0);
  const [maxStreak, setMaxStreak] = useState(0);
  const [newBadges, setNewBadges] = useState([]);
  const [showBadgePopup, setShowBadgePopup] = useState(false);
  const [difficulty, setDifficulty] = useState('easy');
  const [fastAnswers, setFastAnswers] = useState(0);
  const [missedThenCorrect, setMissedThenCorrect] = useState({ missed: 0, correct: 0 });
  const [showVideos, setShowVideos] = useState(null);
  const [activeVideo, setActiveVideo] = useState(null);
  const [userProgress, setUserProgress] = useState(() => {
    const saved = localStorage.getItem('quizProgress');
    return saved ? JSON.parse(saved) : { 
      completedQuizzes: [], 
      badges: [], 
      totalCorrect: 0, 
      totalAnswered: 0,
      bestStreaks: {},
      level: 1,
      xp: 0
    };
  });

  // Anti-screenshot
  useEffect(() => {
    const handleContextMenu = (e) => e.preventDefault();
    const handleKeyDown = (e) => {
      if (e.key === 'PrintScreen' || (e.ctrlKey && e.key === 'p')) {
        e.preventDefault();
        alert('📵 Screenshots disabled! Learn it for real! 💪');
      }
    };
    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  // Timer with difficulty
  useEffect(() => {
    if (!currentQuiz || answered || quizComplete) return;
    if (timeLeft <= 0) { handleTimeout(); return; }
    const timer = setTimeout(() => setTimeLeft(t => t - 1), 1000);
    return () => clearTimeout(timer);
  }, [timeLeft, currentQuiz, answered, quizComplete]);

  // Shuffle answers
  useEffect(() => {
    if (currentQuiz && currentQuiz.questions[questionIndex]) {
      const q = currentQuiz.questions[questionIndex];
      const allAnswers = [q.a, ...q.wrong];
      setShuffledAnswers(allAnswers.sort(() => Math.random() - 0.5));
    }
  }, [currentQuiz, questionIndex]);

  const handleTimeout = () => {
    setAnswered(true);
    setSelectedAnswer('TIMEOUT');
    setStreak(0);
    setMissedThenCorrect(prev => ({ ...prev, missed: prev.missed + 1, correct: 0 }));
    setTimeout(nextQuestion, 1500);
  };

  const getDifficultyTime = () => DIFFICULTY_MULTIPLIER[difficulty]?.time || 9;

  const startQuiz = (topic, quizIndex, diff = 'easy') => {
    const quiz = QUIZ_DATA[topic].quizzes[quizIndex];
    setDifficulty(diff);
    setSelectedTopic(topic);
    setCurrentQuiz({ ...quiz, topic, quizIndex });
    setQuestionIndex(0);
    setScore(0);
    setStreak(0);
    setMaxStreak(0);
    setFastAnswers(0);
    setTimeLeft(DIFFICULTY_MULTIPLIER[diff].time);
    setAnswered(false);
    setQuizComplete(false);
    setNewBadges([]);
    setMissedThenCorrect({ missed: 0, correct: 0 });
  };

  const checkAndAwardBadge = (badgeId, progress) => {
    if (!progress.badges.includes(badgeId)) {
      progress.badges.push(badgeId);
      const badge = BADGES.find(b => b.id === badgeId);
      if (badge) {
        setNewBadges(prev => [...prev, badge]);
        setShowBadgePopup(true);
        setTimeout(() => setShowBadgePopup(false), 2000);
      }
    }
  };

  const handleAnswer = (answer) => {
    if (answered) return;
    setAnswered(true);
    setSelectedAnswer(answer);
    
    const correct = currentQuiz.questions[questionIndex].a;
    const isCorrect = answer === correct;
    const answerTime = getDifficultyTime() - timeLeft;
    
    const newProgress = { ...userProgress };
    newProgress.totalAnswered += 1;
    
    if (isCorrect) {
      setScore(s => s + 1);
      setStreak(s => s + 1);
      setMaxStreak(m => Math.max(m, streak + 1));
      newProgress.totalCorrect += 1;
      
      // Check for comeback
      if (missedThenCorrect.missed >= 2) {
        setMissedThenCorrect(prev => ({ ...prev, correct: prev.correct + 1 }));
        if (missedThenCorrect.correct + 1 >= 3) {
          checkAndAwardBadge('comeback_kid', newProgress);
        }
      }
      setMissedThenCorrect(prev => ({ ...prev, missed: 0 }));
      
      // First correct answer
      if (newProgress.totalCorrect === 1) {
        checkAndAwardBadge('first_blood', newProgress);
      }
      
      // Speed badges
      if (answerTime < 3) {
        setFastAnswers(f => f + 1);
        checkAndAwardBadge('quick_draw', newProgress);
      }
      
      // Streak badges
      if (streak + 1 >= 3) checkAndAwardBadge('hot_streak', newProgress);
      if (streak + 1 >= 5) checkAndAwardBadge('on_fire', newProgress);
      if (streak + 1 >= 10) checkAndAwardBadge('unstoppable', newProgress);
      
      // Clutch badge - last question with <2 sec
      if (questionIndex === currentQuiz.questions.length - 1 && timeLeft < 2) {
        checkAndAwardBadge('clutch', newProgress);
      }
    } else {
      setStreak(0);
      setMissedThenCorrect(prev => ({ ...prev, missed: prev.missed + 1, correct: 0 }));
    }
    
    // Night owl
    const hour = new Date().getHours();
    if (hour >= 0 && hour < 5) {
      checkAndAwardBadge('night_owl', newProgress);
    }
    
    // Add XP
    newProgress.xp += isCorrect ? (difficulty === 'hard' ? 30 : difficulty === 'medium' ? 20 : 10) : 2;
    newProgress.level = Math.floor(newProgress.xp / 100) + 1;
    
    setUserProgress(newProgress);
    setTimeout(nextQuestion, 1500);
  };

  const nextQuestion = () => {
    if (questionIndex + 1 >= currentQuiz.questions.length) {
      finishQuiz();
    } else {
      setQuestionIndex(i => i + 1);
      setTimeLeft(getDifficultyTime());
      setAnswered(false);
      setSelectedAnswer(null);
    }
  };

  const finishQuiz = () => {
    setQuizComplete(true);
    const quizId = `${currentQuiz.topic}_${currentQuiz.quizIndex}`;
    const percentage = (score / currentQuiz.questions.length) * 100;
    
    const newProgress = { ...userProgress };
    
    // Completed quiz
    if (!newProgress.completedQuizzes.includes(quizId) && percentage >= 70) {
      newProgress.completedQuizzes.push(quizId);
    }
    
    // Perfect score = Smoking Gun
    if (score === currentQuiz.questions.length) {
      checkAndAwardBadge('smoking_gun', newProgress);
      if (difficulty === 'hard') {
        checkAndAwardBadge('eagle', newProgress);
      }
    }
    
    // Speed demon - all answers with 5+ sec left
    if (fastAnswers === currentQuiz.questions.length) {
      checkAndAwardBadge('speed_demon', newProgress);
    }
    
    // Progress badges
    const completed = newProgress.completedQuizzes.length;
    if (completed >= 1) checkAndAwardBadge('rookie', newProgress);
    if (completed >= 3) checkAndAwardBadge('learner', newProgress);
    if (completed >= 6) checkAndAwardBadge('scholar', newProgress);
    if (completed >= 12) checkAndAwardBadge('defender', newProgress);
    
    // Topic mastery
    const topicQuizzes = QUIZ_DATA[currentQuiz.topic].quizzes.length;
    const topicCompleted = newProgress.completedQuizzes.filter(q => q.startsWith(currentQuiz.topic)).length;
    if (topicCompleted >= topicQuizzes) {
      const masteryBadge = `${currentQuiz.topic}_master`;
      checkAndAwardBadge(masteryBadge, newProgress);
    }
    
    // Accuracy badge
    const accuracy = (newProgress.totalCorrect / newProgress.totalAnswered) * 100;
    if (accuracy >= 90 && newProgress.totalAnswered >= 20) {
      checkAndAwardBadge('fox', newProgress);
    }
    
    // Legend badge - check if has all other badges
    const nonLegendBadges = BADGES.filter(b => b.id !== 'legend').length;
    if (newProgress.badges.length >= nonLegendBadges - 1) {
      checkAndAwardBadge('legend', newProgress);
    }
    
    setUserProgress(newProgress);
    localStorage.setItem('quizProgress', JSON.stringify(newProgress));
  };

  const shareToFacebook = () => {
    const text = `🔥 I'm Level ${userProgress.level} on Know Your Rights! Just scored ${score}/${currentQuiz.questions.length}! 💪⚖️ ${newBadges.length > 0 ? `Earned: ${newBadges.map(b => b.icon).join('')}` : ''}`;
    window.open(`https://www.facebook.com/sharer/sharer.php?quote=${encodeURIComponent(text)}`, '_blank');
  };

  // Video viewer
  if (showVideos && !currentQuiz) {
    const videoData = VIDEO_CONTENT[showVideos];
    return (
      <div className="video-section">
        <button className="back-btn" onClick={() => { setShowVideos(null); setActiveVideo(null); }}>← Back to Topics</button>
        <h2>🎬 {videoData.name}</h2>
        <p>Watch & learn before you quiz yourself!</p>
        
        {activeVideo ? (
          <div className="video-player">
            <div className="video-container">
              <iframe
                src={`https://www.youtube.com/embed/${activeVideo.id}?autoplay=1`}
                title={activeVideo.title}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            </div>
            <h3>{activeVideo.title}</h3>
            <p className="video-channel">📺 {activeVideo.channel}</p>
            <button className="close-video-btn" onClick={() => setActiveVideo(null)}>Watch Another Video</button>
          </div>
        ) : (
          <div className="video-grid">
            {videoData.videos.map((video, i) => (
              <div key={i} className="video-card" onClick={() => setActiveVideo(video)}>
                <div className="video-thumbnail">
                  <img src={`https://img.youtube.com/vi/${video.id}/mqdefault.jpg`} alt={video.title} />
                  <span className="video-duration">{video.duration}</span>
                  <div className="play-overlay">▶</div>
                </div>
                <h4>{video.title}</h4>
                <p className="video-channel">📺 {video.channel}</p>
              </div>
            ))}
          </div>
        )}
        
        <div className="ready-to-quiz">
          <p>Ready to test what you learned?</p>
          <button onClick={() => { setShowVideos(null); }}>Take the Quiz 🧠</button>
        </div>
      </div>
    );
  }

  // Quiz in progress
  if (currentQuiz && !quizComplete) {
    const question = currentQuiz.questions[questionIndex];
    const correct = question.a;
    const diffConfig = DIFFICULTY_MULTIPLIER[difficulty];
    
    return (
      <div className="quiz-active" style={{ userSelect: 'none' }}>
        {/* Badge popup */}
        {showBadgePopup && newBadges.length > 0 && (
          <div className="badge-popup">
            <div className="badge-earned">
              <span className="popup-icon">{newBadges[newBadges.length - 1].icon}</span>
              <span className="popup-text">BADGE UNLOCKED!</span>
              <span className="popup-name">{newBadges[newBadges.length - 1].name}</span>
            </div>
          </div>
        )}
        
        <div className="quiz-header">
          <span className="quiz-topic">{QUIZ_DATA[currentQuiz.topic].icon} {QUIZ_DATA[currentQuiz.topic].name}</span>
          <span className="difficulty-badge" style={{ background: diffConfig.color }}>{diffConfig.label}</span>
          <span className="quiz-progress">Q{questionIndex + 1}/{currentQuiz.questions.length}</span>
        </div>
        
        <div className="stats-bar">
          <span className="streak-counter">🔥 Streak: {streak}</span>
          <span className="level-display">⭐ Level {userProgress.level}</span>
          <span className="xp-display">XP: {userProgress.xp}</span>
        </div>
        
        <div className={`timer ${timeLeft <= 3 ? 'danger' : ''}`} style={{ borderColor: diffConfig.color }}>
          <span className="timer-num">{timeLeft}</span>
          <span className="timer-label">sec</span>
        </div>
        
        <div className="question-box">
          <h3>{question.q}</h3>
        </div>
        
        <div className="answers-grid">
          {shuffledAnswers.map((answer, i) => {
            let className = 'answer-btn';
            if (answered) {
              if (answer === correct) className += ' correct';
              else if (answer === selectedAnswer) className += ' wrong';
            }
            return (
              <button key={i} className={className} onClick={() => handleAnswer(answer)} disabled={answered}>
                {answer}
              </button>
            );
          })}
        </div>
        
        {answered && selectedAnswer === 'TIMEOUT' && (
          <div className="timeout-msg">⏰ Too slow! Answer: {correct}</div>
        )}
        
        <div className="score-display">Score: {score}/{questionIndex + (answered ? 1 : 0)}</div>
      </div>
    );
  }

  // Quiz complete
  if (quizComplete) {
    const percentage = Math.round((score / currentQuiz.questions.length) * 100);
    const passed = percentage >= 70;
    
    return (
      <div className="quiz-complete">
        <h2>{percentage === 100 ? '🔥 PERFECT!' : passed ? '✅ PASSED!' : '📚 Keep Training!'}</h2>
        
        <div className="score-circle" style={{ background: percentage === 100 ? 'linear-gradient(135deg, #ff6b6b, #ffd700)' : undefined }}>
          <span className="big-score">{score}/{currentQuiz.questions.length}</span>
          <span className="percentage">{percentage}%</span>
        </div>
        
        <div className="stats-summary">
          <div className="stat-item">
            <span className="stat-icon">🔥</span>
            <span className="stat-value">{maxStreak}</span>
            <span className="stat-label">Best Streak</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">⭐</span>
            <span className="stat-value">{userProgress.level}</span>
            <span className="stat-label">Level</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">🎯</span>
            <span className="stat-value">{Math.round((userProgress.totalCorrect / userProgress.totalAnswered) * 100) || 0}%</span>
            <span className="stat-label">Accuracy</span>
          </div>
        </div>
        
        {newBadges.length > 0 && (
          <div className="new-badges-section">
            <h3>🏆 BADGES EARNED!</h3>
            <div className="new-badges-row">
              {newBadges.map((badge, i) => (
                <div key={i} className="new-badge-item">
                  <span className="badge-icon-large">{badge.icon}</span>
                  <span className="badge-name-pop">{badge.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="next-difficulty">
          {difficulty !== 'hard' && passed && (
            <p className="challenge-text">
              Ready for {difficulty === 'easy' ? 'Medium' : 'Hard'} mode? ⚡
            </p>
          )}
        </div>
        
        <div className="quiz-actions">
          <button onClick={() => { setCurrentQuiz(null); setSelectedTopic(null); }}>Back</button>
          {passed && difficulty !== 'hard' && (
            <button 
              className="harder-btn"
              onClick={() => startQuiz(currentQuiz.topic, currentQuiz.quizIndex, difficulty === 'easy' ? 'medium' : 'hard')}
            >
              Try {difficulty === 'easy' ? 'Medium' : 'Hard'} 💀
            </button>
          )}
          <button onClick={shareToFacebook} className="share-btn">Share 📱</button>
        </div>
      </div>
    );
  }

  // Topic selection with level display
  return (
    <div className="quiz-tab">
      <div className="quiz-header-main">
        <h2>🧠 Quiz Mode</h2>
        <div className="player-stats">
          <span className="level-badge">⭐ Level {userProgress.level}</span>
          <span className="xp-bar">{userProgress.xp} XP</span>
        </div>
      </div>
      <p>9 seconds per question. Think FAST. 🔥</p>
      
      <div className="progress-summary">
        <span>✅ {userProgress.completedQuizzes.length}/12 Quizzes</span>
        <span>🏆 {userProgress.badges.length}/{BADGES.length} Badges</span>
        <span>🎯 {userProgress.totalAnswered > 0 ? Math.round((userProgress.totalCorrect / userProgress.totalAnswered) * 100) : 0}% Accuracy</span>
      </div>
      
      <div className="topics-grid">
        {Object.entries(QUIZ_DATA).map(([key, topic]) => (
          <div key={key} className="topic-card">
            <span className="topic-icon">{topic.icon}</span>
            <h3>{topic.name}</h3>
            
            {VIDEO_CONTENT[key] && (
              <button className="watch-videos-btn" onClick={() => setShowVideos(key)}>
                🎬 Watch Videos First
              </button>
            )}
            
            <div className="quiz-list">
              {topic.quizzes.map((quiz, i) => {
                const quizId = `${key}_${i}`;
                const completed = userProgress.completedQuizzes.includes(quizId);
                return (
                  <div key={i} className="quiz-row">
                    <button 
                      className={`quiz-btn ${completed ? 'completed' : ''}`}
                      onClick={() => startQuiz(key, i, 'easy')}
                    >
                      {completed ? '✅' : '▶️'} Quiz {i + 1}
                    </button>
                    {completed && (
                      <button 
                        className="hard-mode-btn"
                        onClick={() => startQuiz(key, i, 'hard')}
                        title="Hard Mode - 6 seconds!"
                      >
                        💀
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      
      <div className="badges-section">
        <h3>🏆 Your Badges ({userProgress.badges.length}/{BADGES.length})</h3>
        <div className="badges-grid">
          {BADGES.map(badge => (
            <div 
              key={badge.id} 
              className={`badge-item ${userProgress.badges.includes(badge.id) ? 'earned' : 'locked'}`}
              title={badge.requirement}
            >
              <span className="badge-icon">{badge.icon}</span>
              <span className="badge-name">{badge.name}</span>
              <span className="badge-req">{badge.requirement}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Tab 3: My Rights
const MyRightsTab = ({ user }) => {
  const [bundles, setBundles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPurchasedBundles();
  }, []);

  const fetchPurchasedBundles = async () => {
    try {
      const response = await axios.get(`${API}/user/bundles`, { params: { user_id: user.id } });
      setBundles(response.data.bundles || []);
    } catch (err) {
      console.error('Failed to fetch bundles:', err);
    }
    setLoading(false);
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="my-rights-tab">
      <h2>📚 My Rights</h2>
      <p>Your purchased rights bundles</p>

      {bundles.length === 0 ? (
        <div className="no-bundles">
          <h3>No bundles purchased yet</h3>
          <div className="promo-cards">
            <div className="promo-card flash">
              <h4>🔥 FLASH SALE</h4>
              <p className="price">$10</p>
              <p>All 13 Rights Bundles</p>
            </div>
            <div className="promo-card">
              <h4>Buy 3 Get 7 FREE</h4>
              <p className="price">$8.97</p>
              <p>10 Bundles Total</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bundles-grid">
          {bundles.map((bundle, i) => (
            <div key={i} className="bundle-card">
              <span className="bundle-icon">{bundle.icon}</span>
              <h4>{bundle.name}</h4>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Tab 4: Do I Have a Case?
const CaseAnalyzerTab = ({ user }) => {
  const [situation, setSituation] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [queriesLeft, setQueriesLeft] = useState(3);

  useEffect(() => {
    fetchQueriesLeft();
  }, []);

  const fetchQueriesLeft = async () => {
    try {
      const response = await axios.get(`${API}/case-analyzer/queries-left`, { params: { user_id: user.id } });
      setQueriesLeft(response.data.queries_left);
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
      alert(err.response?.data?.detail || 'Analysis failed');
    }
    setLoading(false);
  };

  if (loading) {
    return <LoadingWithComparison message="⚖️ AI analyzing your situation... Lawyers charge $300/hr for this." />;
  }

  return (
    <div className="case-analyzer-tab">
      <h2>⚖️ Do I Have a Case?</h2>
      <p>AI-powered legal situation analysis</p>

      <div className="queries-status">
        <span className={`queries-left ${queriesLeft <= 0 ? 'empty' : ''}`}>
          {queriesLeft} Free Queries Left
        </span>
      </div>

      <form onSubmit={handleAnalyze} className="analyzer-form">
        <textarea
          value={situation}
          onChange={(e) => setSituation(e.target.value)}
          placeholder="Describe your legal situation..."
          rows={5}
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
            <span className={`verdict-badge ${analysis.has_case ? 'yes' : 'maybe'}`}>
              {analysis.verdict}
            </span>
          </div>
          <div className="analysis-section">
            <h4>Summary</h4>
            <p>{analysis.summary}</p>
          </div>
          {analysis.relevant_laws?.length > 0 && (
            <div className="analysis-section">
              <h4>Relevant Laws</h4>
              <ul>{analysis.relevant_laws.map((law, i) => <li key={i}>{law}</li>)}</ul>
            </div>
          )}
          {analysis.next_steps?.length > 0 && (
            <div className="analysis-section">
              <h4>Next Steps</h4>
              <ol>{analysis.next_steps.map((step, i) => <li key={i}>{step}</li>)}</ol>
            </div>
          )}
          <div className="disclaimer-small">
            ⚠️ This is educational information, not legal advice.
          </div>
        </div>
      )}
    </div>
  );
};

// Main App
const KnowYourRightsApp = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('search');
  const [showDisclaimer, setShowDisclaimer] = useState(true);
  const [autoLogging, setAutoLogging] = useState(false);

  // Auto-login: Always keep user logged in for seamless experience
  useEffect(() => {
    const autoLogin = async () => {
      const savedUser = localStorage.getItem('user');
      if (savedUser) {
        setUser(JSON.parse(savedUser));
        return;
      }
      
      // No saved user - auto-login with demo account
      setAutoLogging(true);
      try {
        const response = await axios.post(`${API}/auth/login`, {
          email: 'demo@knowyourrights.com',
          password: 'demo123'
        });
        
        if (response.data.user) {
          localStorage.setItem('user', JSON.stringify(response.data.user));
          localStorage.setItem('token', response.data.token || 'demo-token');
          setUser(response.data.user);
        }
      } catch (err) {
        // If demo login fails, try to create the account first
        try {
          const signupResponse = await axios.post(`${API}/auth/signup`, {
            email: 'demo@knowyourrights.com',
            password: 'demo123',
            name: 'Demo User'
          });
          if (signupResponse.data.user) {
            localStorage.setItem('user', JSON.stringify(signupResponse.data.user));
            localStorage.setItem('token', signupResponse.data.token || 'demo-token');
            setUser(signupResponse.data.user);
          }
        } catch (signupErr) {
          console.log('Auto-login setup complete');
        }
      }
      setAutoLogging(false);
    };
    
    autoLogin();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    setUser(null);
  };

  if (!user) {
    return <AuthScreen onLogin={setUser} disclaimer={showDisclaimer} setShowDisclaimer={setShowDisclaimer} />;
  }

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
        <button className={activeTab === 'search' ? 'active' : ''} onClick={() => setActiveTab('search')}>🔍 Search</button>
        <button className={activeTab === 'learn' ? 'active' : ''} onClick={() => setActiveTab('learn')}>🎬 Learn</button>
        <button className={activeTab === 'quiz' ? 'active' : ''} onClick={() => setActiveTab('quiz')}>🧠 Quiz</button>
        <button className={activeTab === 'my-rights' ? 'active' : ''} onClick={() => setActiveTab('my-rights')}>📚 My Rights</button>
        <button className={activeTab === 'case' ? 'active' : ''} onClick={() => setActiveTab('case')}>⚖️ Case?</button>
      </nav>

      <main className="tab-content">
        {activeTab === 'search' && <SmartSearchTab user={user} />}
        {activeTab === 'learn' && <LearnTab user={user} />}
        {activeTab === 'quiz' && <QuizTab user={user} />}
        {activeTab === 'my-rights' && <MyRightsTab user={user} />}
        {activeTab === 'case' && <CaseAnalyzerTab user={user} />}
      </main>

      <footer className="app-footer">
        <p>© 2025 Know Your Rights • Real Legal Information from U.S. Constitution</p>
      </footer>
    </div>
  );
};

export default KnowYourRightsApp;
