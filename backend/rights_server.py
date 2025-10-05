from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class RightsCategory(str, Enum):
    TRAFFIC = "traffic"
    HOUSING = "housing"
    LANDMINES = "landmines"
    CRIMINAL = "criminal"
    WORKPLACE = "workplace"
    FAMILY = "family"
    HEALTHCARE = "healthcare"
    STUDENT = "student"
    DIGITAL = "digital"
    CONSUMER = "consumer"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    EXPIRED = "expired"

# Models
class RightsContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    situation: str
    content: str
    category: RightsCategory
    state_specific: bool = False
    is_free: bool = False

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    amount: float
    currency: str = "usd"
    payment_status: PaymentStatus
    metadata: Dict[str, str] = {}
    category: Optional[RightsCategory] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CategoryAccess(BaseModel):
    user_id: str
    category: RightsCategory
    purchased_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

class CheckoutRequest(BaseModel):
    category: RightsCategory
    origin_url: str

# Initialize Stripe
stripe_api_key = os.environ.get('STRIPE_API_KEY')

# Rights Content Database
RIGHTS_CONTENT = {
    # FREE TRAFFIC RIGHTS
    "traffic_pulled_over": RightsContent(
        title="I Got Pulled Over",
        situation="Police officer pulls you over",
        content="""
**STAY CALM AND FOLLOW THESE STEPS:**

1. **Pull over safely** - Use turn signal, slow down, pull to safe location
2. **Turn off engine** - Keep hands visible on steering wheel
3. **Stay in vehicle** - Don't get out unless asked
4. **Be polite but brief** - "Good morning/evening officer"

**WHAT TO SAY:**
- "I'm exercising my right to remain silent"
- "I do not consent to searches"
- "Am I free to leave?"

**YOUR RIGHTS:**
✅ You have right to remain silent
✅ You can refuse vehicle searches (without warrant)
✅ You can ask if you're free to leave
✅ You can record the interaction

**WHAT NOT TO DO:**
❌ Don't argue or resist
❌ Don't consent to searches
❌ Don't answer questions beyond ID
❌ Don't make sudden movements

**ID REQUIREMENTS:**
Most states require driver's license, registration, insurance if driving.
        """,
        category=RightsCategory.TRAFFIC,
        is_free=True
    ),
    
    "traffic_search_car": RightsContent(
        title="Can Police Search My Car?",
        situation="Officer wants to search your vehicle",
        content="""
**YOU CAN SAY NO TO SEARCHES!**

**MAGIC WORDS:**
"Officer, I do not consent to any searches of my person or property."

**WHEN POLICE CAN SEARCH (Even without consent):**
- They have a valid warrant
- They see illegal items in plain view
- You're arrested (search incident to arrest)
- Vehicle impounded and inventoried

**WHEN THEY CANNOT SEARCH:**
- Just because they pulled you over
- Because they "smell something"
- If you refuse consent (unless above exceptions apply)

**WHAT TO DO:**
1. **Clearly state:** "I do not consent to searches"
2. **Don't physically resist** - Let lawyer fight it later
3. **Ask:** "Am I free to leave?"
4. **Stay silent** - Don't explain or justify

**REMEMBER:**
- Refusing search is NOT suspicious behavior
- It's your constitutional right
- Police may try to pressure you - stand firm
- Even if they search anyway, your refusal helps in court
        """,
        category=RightsCategory.TRAFFIC,
        is_free=True
    ),
    
    "traffic_show_id": RightsContent(
        title="Do I Have to Show ID?",
        situation="Officer asks for identification",
        content="""
**DEPENDS ON THE SITUATION:**

**DRIVING A VEHICLE - YES:**
- Driver's license REQUIRED
- Vehicle registration REQUIRED  
- Insurance proof REQUIRED

**WALKING/NOT DRIVING:**
**States that REQUIRE ID (Stop & Identify):**
Alabama, Arizona, Arkansas, Colorado, Delaware, Florida, Georgia, Illinois, Indiana, Kansas, Louisiana, Missouri, Montana, Nevada, New Hampshire, New Mexico, New York, North Dakota, Ohio, Rhode Island, Texas, Utah, Vermont, Wisconsin

**All Other States:**
You generally do NOT have to show ID unless:
- You're being arrested
- You're in a restricted area
- Officer has reasonable suspicion of crime

**WHAT TO SAY:**
"Am I being detained or arrested? If not, I'd like to exercise my right to leave."

**IF DETAINED:**
- Provide ID if in stop-and-identify state
- Otherwise, invoke right to remain silent
- Ask for lawyer if arrested

**REMEMBER:**
- Know your state's laws
- Being "suspicious" isn't enough in most states
- Police may lie about ID requirements
        """,
        category=RightsCategory.TRAFFIC,
        is_free=True
    ),
    
    "traffic_dui_checkpoint": RightsContent(
        title="DUI Checkpoints Rights",
        situation="Approaching sobriety checkpoint",
        content="""
**YOUR RIGHTS AT CHECKPOINTS:**

**LEGAL CHECKPOINTS MUST:**
✅ Be announced publicly in advance
✅ Follow systematic pattern (every 3rd car, etc.)
✅ Have proper signage and lighting
✅ Be supervised by high-ranking officer

**YOUR RIGHTS:**
✅ Remain silent beyond basic ID
✅ Refuse field sobriety tests (penalties vary by state)
✅ Refuse breathalyzer (but license may be suspended)
✅ Ask to speak to lawyer
✅ Turn around BEFORE checkpoint (if legal opportunity)

**WHAT TO DO:**
1. **Provide license/registration** when asked
2. **Be polite:** "Good evening officer"
3. **Minimal responses:** "I'm exercising my right to remain silent"
4. **Don't admit to drinking** - Even "just two beers" hurts you

**DON'T VOLUNTEER:**
❌ "I only had two drinks"
❌ "I'm coming from a bar/party"  
❌ Where you're going/been
❌ Answer questions about drinking

**FIELD SOBRIETY TESTS:**
- You can refuse (but may face license suspension)
- These tests are designed for failure
- Sober people fail 30% of the time
- Officer is looking for ANY reason to arrest
        """,
        category=RightsCategory.TRAFFIC,
        is_free=True
    ),

    "traffic_recording": RightsContent(
        title="Can I Record Police?",
        situation="You want to record police interaction",
        content="""
**YES - YOU CAN RECORD POLICE!**

**YOUR RIGHT TO RECORD:**
✅ First Amendment protects recording in public
✅ Applies to traffic stops, protests, arrests
✅ Police cannot delete your recordings
✅ You can stream live to cloud storage

**HOW TO RECORD SAFELY:**
1. **Stay at safe distance** - Don't interfere with police work
2. **Hold phone openly** - Don't be sneaky about it
3. **Announce you're recording** - "I'm recording for my safety"
4. **Keep hands visible** - Don't make sudden movements
5. **Stay calm and silent** - Let camera do the talking

**WHAT POLICE MIGHT SAY (These are WRONG):**
❌ "You can't record me" - FALSE
❌ "It's illegal to record" - FALSE  
❌ "Delete that video" - You don't have to
❌ "Give me your phone" - Only with warrant

**PROTECT YOUR RECORDING:**
- Use apps that auto-upload (ACLU Mobile Justice)
- Password protect your phone
- Know your passcode rights vary by state
- Don't unlock phone for police without warrant

**IF POLICE TAKE YOUR PHONE:**
- Don't physically resist
- Say "I do not consent to searches"
- Contact lawyer immediately
- Police need warrant to search phone contents
        """,
        category=RightsCategory.TRAFFIC,
        is_free=True
    ),

    "traffic_arrested": RightsContent(
        title="What If I Get Arrested?",
        situation="Police are arresting you during traffic stop",
        content="""
**MIRANDA RIGHTS APPLY:**

**THE MAGIC WORDS:**
"I invoke my right to remain silent and want a lawyer."

**WHAT HAPPENS DURING ARREST:**
1. **Handcuffs applied** - Don't resist physically
2. **You're read rights** - Listen carefully  
3. **Search incident to arrest** - They can search you and car
4. **Transported to jail** - Booking process begins

**YOUR CRITICAL RIGHTS:**
✅ Right to remain silent - USE IT
✅ Right to attorney - REQUEST IMMEDIATELY
✅ Right to phone call - Call lawyer or family
✅ Protection from unreasonable search (with exceptions)

**DO NOT:**
❌ Resist arrest physically (adds charges)
❌ Talk to police without lawyer
❌ Sign anything without lawyer
❌ Answer questions "just to clear this up"

**WHAT TO SAY:**
- "I'm invoking my right to remain silent"
- "I want a lawyer"  
- "I do not consent to searches"
- Then STOP TALKING

**AFTER ARREST:**
- Use phone call for lawyer, not to discuss case
- Don't talk to cellmates about your case
- Don't sign property receipts you can't read
- Contact family for bail/lawyer help

**REMEMBER:** 
Anything you say CAN and WILL be used against you. Police are trained interrogators. Wait for your lawyer.
        """,
        category=RightsCategory.TRAFFIC,
        is_free=True
    ),

    # HOUSING RIGHTS BUNDLE (Previously Tenant Rights)
    "housing_eviction": RightsContent(
        title="Landlord Wants to Evict Me",
        situation="Facing eviction proceedings",
        content="""
**EVICTION PROCESS - YOUR RIGHTS:**

**LANDLORD CANNOT:**
❌ Kick you out immediately
❌ Change locks while you live there
❌ Shut off utilities to force you out
❌ Remove your belongings without court order
❌ Evict for discriminatory reasons
❌ Evict in retaliation for complaints

**LEGAL EVICTION PROCESS:**
1. **Written Notice Required** (3-30 days depending on reason)
2. **Court Filing** - Landlord must sue you
3. **You Receive Court Summons** - Usually 5-10 days to respond
4. **Court Hearing** - You can defend yourself
5. **Court Order** - Only sheriff can remove you if you lose

**COMMON EVICTION DEFENSES:**
✅ Landlord didn't maintain property (habitability)
✅ Improper notice given
✅ Discrimination or retaliation
✅ Landlord accepted rent after violation
✅ Lease terms were illegal

**WHAT TO DO IMMEDIATELY:**
1. **Read notice carefully** - Check dates and reasons
2. **Document everything** - Photos, emails, repair requests
3. **Gather evidence** - Receipts, communications, witnesses
4. **Contact legal aid** - Many areas have free tenant lawyers
5. **Prepare for court** - Don't ignore court date

**EMERGENCY SITUATIONS:**
If landlord illegally locks you out or shuts off utilities:
- Call police (it's illegal "self-help" eviction)
- Document with photos/video
- Contact emergency tenant hotline
- File complaint with housing authority
        """,
        category=RightsCategory.HOUSING,
        is_free=False
    ),

    "housing_security_deposit": RightsContent(
        title="Getting Security Deposit Back",
        situation="Moving out and want deposit returned",
        content="""
**SECURITY DEPOSIT LAWS:**

**LANDLORD MUST:**
✅ Return deposit within 15-60 days (varies by state)
✅ Provide itemized list of deductions
✅ Return remainder with written explanation
✅ Only deduct for actual damages beyond normal wear
✅ Keep deposits in separate account (some states)

**NORMAL WEAR vs DAMAGE:**
**NORMAL WEAR (Can't charge you):**
- Faded paint after 2+ years
- Worn carpet in walkways
- Small nail holes from pictures
- Minor scuffs on walls
- Worn door handles/hinges

**DAMAGE (Can charge you):**
- Large holes in walls
- Broken windows/doors
- Stains on carpet from spills
- Missing fixtures you removed
- Excessive cleaning needed

**PROTECT YOUR DEPOSIT:**
**MOVE-IN:**
- Document existing damage with photos/video
- Get landlord to acknowledge condition in writing
- Keep copies of move-in inspection

**MOVE-OUT:**
- Clean thoroughly (hire professionals if needed)
- Fix any damage you caused
- Take photos/video of clean condition
- Do walk-through with landlord if possible

**IF LANDLORD WRONGFULLY KEEPS DEPOSIT:**
1. **Send demand letter** - Certified mail
2. **File in small claims court** - Usually no lawyer needed
3. **Gather evidence** - Photos, receipts, communications
4. **Know your state's penalties** - Some states double/triple damages for bad faith
        """,
        category=RightsCategory.HOUSING,
        is_free=False
    ),

    "housing_landlord_entry": RightsContent(
        title="Landlord Entering Without Notice",
        situation="Landlord entering your rental without permission",
        content="""
**YOUR RIGHT TO PRIVACY:**

**LANDLORD ENTRY RULES:**
Most states require 24-48 hour written notice except for:
- True emergencies (fire, flood, gas leak)
- Court orders or warrants
- Abandonment situations
- Tenant consent given

**VALID REASONS FOR ENTRY:**
✅ Make necessary repairs
✅ Show property to prospective tenants/buyers
✅ Inspect property (reasonable intervals)
✅ Emergency situations

**INVALID REASONS:**
❌ "Just checking up on things"
❌ Harassment or intimidation  
❌ Retaliation for complaints
❌ Showing property without proper notice

**WHAT TO DO IF ILLEGAL ENTRY:**
1. **Document everything** - Date, time, reason given
2. **Take photos/video** - Evidence of entry
3. **Send written complaint** - Certified mail to landlord
4. **Know your state's penalties** - Some allow rent reduction
5. **Contact housing authority** - File official complaint

**NOTICE REQUIREMENTS BY STATE:**
- **24 hours:** Most states including CA, TX, FL
- **48 hours:** Some states like WA, OR
- **Reasonable notice:** Some states don't specify exact time

**EMERGENCY ENTRY:**
Landlord can enter without notice for:
- Gas/water leaks
- Fire or smoke
- Broken pipes flooding
- Security breaches
- Medical emergencies

**PROTECT YOURSELF:**
- Change locks (if lease allows) and provide key
- Install security cameras (if legal in your area)
- Keep log of all landlord interactions
- Know your state's specific tenant laws
        """,
        category=RightsCategory.HOUSING,
        is_free=False
    ),

    "housing_repairs_habitability": RightsContent(
        title="Landlord Won't Make Repairs",
        situation="Living conditions are unsafe or unlivable",
        content="""
**WARRANTY OF HABITABILITY:**

**LANDLORD MUST PROVIDE:**
✅ Safe drinking water and plumbing
✅ Working heat and electricity
✅ Weatherproofing (roof, windows, doors)
✅ Pest-free environment
✅ Safe structure (no falling hazards)
✅ Working smoke/carbon monoxide detectors

**SERIOUS HABITABILITY ISSUES:**
- No heat in winter
- Raw sewage or backed-up drains
- Mold or significant water damage
- Electrical hazards (exposed wires, etc.)
- Broken locks or security issues
- Pest infestations

**STEPS TO TAKE:**
1. **Document everything** - Photos, videos, temperature readings
2. **Written notice to landlord** - Certified mail, demand repairs
3. **Give reasonable time** - Usually 14-30 days for repairs
4. **Contact local housing authority** - File complaints
5. **Know your remedies** - Rent withholding, repair and deduct

**YOUR LEGAL REMEDIES:**
**Rent Withholding:**
- Stop paying rent until repairs made (follow state procedures)
- Must continue paying into escrow account
- Court may order landlord to make repairs

**Repair and Deduct:**
- Pay for repairs yourself, deduct from rent
- Usually limited to 1-2 months rent
- Keep receipts and follow state laws

**EMERGENCY SITUATIONS:**
If immediate danger (gas leak, no heat in freezing weather):
- Call city building inspector immediately
- Document with photos/video
- May be able to break lease without penalty
- Local health department can condemn property

**PROTECT YOURSELF:**
- Always give written notice before withholding rent
- Know your state's specific habitability laws
- Keep records of all communications
- Never stop paying rent without legal grounds
        """,
        category=RightsCategory.HOUSING,
        is_free=False
    ),

    "housing_lease_breaking": RightsContent(
        title="Breaking a Lease Legally",
        situation="Need to move out before lease ends",
        content="""
**LEGAL REASONS TO BREAK LEASE:**

**AUTOMATIC LEASE TERMINATION:**
✅ Military deployment (SCRA protection)
✅ Domestic violence situations
✅ Landlord harassment or illegal entry
✅ Major habitability violations
✅ Property becomes uninhabitable

**CONSTRUCTIVE EVICTION:**
When landlord makes living conditions so bad you're forced to leave:
- Refusing to make essential repairs
- Shutting off utilities illegally
- Allowing dangerous conditions
- Harassment or privacy violations

**EARLY TERMINATION CLAUSES:**
Check your lease for:
- Job relocation clauses
- Medical emergency provisions
- Early termination fee options
- Military service provisions

**BREAKING LEASE - FINANCIAL CONSEQUENCES:**
**What You May Owe:**
- Remaining rent until new tenant found
- Advertising costs for re-renting
- Lost rent during vacancy period
- Early termination fees (if in lease)

**MINIMIZE DAMAGES:**
1. **Give maximum notice** - 30+ days if possible
2. **Help find replacement tenant** - Show unit, advertise
3. **Negotiate with landlord** - Offer to forfeit deposit
4. **Check state laws** - Many limit damages to 1-2 months rent

**STATE-SPECIFIC PROTECTIONS:**
- **California:** 30-day notice for domestic violence
- **Texas:** Military deployment, domestic violence
- **New York:** Senior citizens, disability accommodation
- **Check your state:** Laws vary significantly

**DOCUMENTATION NEEDED:**
- Military orders (for SCRA)
- Police reports (for domestic violence)
- Medical records (for health-related moves)
- Photos of habitability issues
- All communications with landlord

**BEFORE MOVING OUT:**
- Take photos of condition
- Return keys properly
- Provide forwarding address
- Keep copies of all documents
        """,
        category=RightsCategory.HOUSING,
        is_free=False
    ),

    "housing_discrimination": RightsContent(
        title="Housing Discrimination",
        situation="Being denied housing or facing unfair treatment",
        content="""
**FAIR HOUSING LAWS PROTECT YOU:**

**PROTECTED CLASSES (FEDERAL):**
✅ Race and color
✅ Religion
✅ National origin
✅ Sex/Gender
✅ Familial status (children under 18, pregnancy)
✅ Disability/handicap
✅ Age (in some contexts)

**ADDITIONAL STATE PROTECTIONS:**
Many states also protect:
- Sexual orientation and gender identity
- Source of income (Section 8, disability benefits)
- Marital status
- Military status

**ILLEGAL DISCRIMINATION:**
❌ Refusing to rent based on protected class
❌ Different terms/conditions for protected groups
❌ Steering (showing different neighborhoods)
❌ Discriminatory advertising language
❌ Refusing reasonable disability accommodations

**COMMON DISCRIMINATION EXAMPLES:**
- "No children" policies (usually illegal)
- Refusing Section 8 vouchers (illegal in many states)
- Different application requirements by race
- Asking about immigration status
- Refusing guide dogs/service animals

**REASONABLE ACCOMMODATIONS:**
Landlords must allow:
- Service animals (even with no-pets policy)
- Handicap-accessible modifications
- Reserved parking spaces for disabilities
- Communication aids for hearing impaired
- Caregiver access for disabled tenants

**WHAT TO DO IF DISCRIMINATED:**
1. **Document everything** - Save emails, texts, applications
2. **Test for discrimination** - Have others apply with same qualifications
3. **File complaints** - HUD, state fair housing agency, local commission
4. **Contact legal aid** - Many organizations help with housing discrimination
5. **Keep evidence** - Ads, application denials, witness statements

**WHERE TO FILE COMPLAINTS:**
- **HUD (Federal):** 1-800-669-9777
- **State fair housing agencies**
- **Local human rights commissions**
- **Private attorneys** (may take cases on contingency)

**REMEDIES AVAILABLE:**
- Monetary damages
- Forced rental/sale
- Policy changes
- Punitive damages
- Attorney fees
        """,
        category=RightsCategory.HOUSING,
        is_free=False
    ),

    # LEGAL LANDMINES BUNDLE - Avoid Costly Everyday Legal Mistakes
    "landmines_social_media": RightsContent(
        title="Social Media Legal Dangers",
        situation="Posting content that could get you sued or arrested",
        content="""
**SOCIAL MEDIA LEGAL LANDMINES:**

**POSTS THAT CAN GET YOU SUED:**
❌ Defamatory statements about people/businesses
❌ Posting photos of people without permission
❌ Copyright infringement (music, images, videos)
❌ Revenge posts about ex-partners
❌ False business reviews
❌ Sharing private information about others

**POSTS THAT CAN GET YOU ARRESTED:**
❌ Threats (even "joking" ones)
❌ Harassment or cyberbullying
❌ Posting illegal content
❌ Inciting violence or riots
❌ Identity theft or impersonation
❌ Child exploitation material

**EMPLOYMENT CONSEQUENCES:**
Employers can legally fire you for:
- Posts that violate company policy
- Discriminatory or offensive content
- Revealing confidential information
- Posts that damage company reputation

**PROTECT YOURSELF:**
1. **Think before posting** - Would you say this in court?
2. **Privacy settings** - Don't rely on them for legal protection
3. **Avoid naming people** - Especially in negative contexts
4. **No photos without permission** - Especially of minors
5. **Screenshot everything** - If someone threatens/harasses you

**DIVORCE/CUSTODY IMPLICATIONS:**
Social media is evidence in family court:
- Party photos during custody battle
- Dating posts during divorce proceedings
- Financial posts contradicting support claims
- Location check-ins during custody time

**IF YOU'RE BEING HARASSED:**
1. **Don't respond** - Document everything instead
2. **Block and report** - Use platform reporting tools
3. **Save evidence** - Screenshots with timestamps
4. **Contact police** - If threats of violence
5. **Consider restraining order** - For persistent harassment

**BUSINESS OWNERS BEWARE:**
- Fake positive reviews (FTC violations)
- Attacking competitors online
- Using copyrighted images
- Employee social media policies
- Customer privacy violations

**REMEMBER:**
Nothing online is truly private. Courts, employers, and investigators can access "deleted" content. When in doubt, don't post it.
        """,
        category=RightsCategory.LANDMINES,
        is_free=False
    ),

    "landmines_neighbor_disputes": RightsContent(
        title="Neighbor Disputes & Property Lines",
        situation="Conflicts with neighbors over noise, property, or boundaries",
        content="""
**COMMON NEIGHBOR LEGAL TRAPS:**

**PROPERTY LINE DISPUTES:**
❌ Building fences without surveys
❌ Assuming property lines based on existing structures
❌ Cutting neighbor's trees without permission
❌ Using neighbor's driveway/land without easement
❌ Blocking legal access routes

**NOISE COMPLAINTS:**
**LEGAL NOISE LIMITS:**
- Most cities: 55-65 decibels during day, 45-55 at night
- "Quiet hours" typically 10 PM - 7 AM
- Dogs barking persistently (usually after 10-20 minutes)
- Construction work restricted hours

**FENCE LAWS:**
- Check local setback requirements
- Good neighbor fence laws (shared costs)
- Height restrictions (usually 6 feet max)
- Cannot build spite fences
- May need permits for certain materials

**TREE DISPUTES:**
**YOU CAN LEGALLY:**
✅ Cut branches hanging over your property line
✅ Cut roots damaging your property
✅ Keep fruit from branches over your land

**YOU CANNOT:**
❌ Cut neighbor's tree on their property
❌ Poison or kill neighbor's tree
❌ Enter neighbor's property to trim

**WATER/DRAINAGE ISSUES:**
- Cannot divert water onto neighbor's property
- Natural drainage patterns must be maintained
- Gutters and downspouts placement matters
- Swimming pool overflow legal issues

**HOW TO HANDLE DISPUTES:**
1. **Talk first** - Many issues resolve with conversation
2. **Know local ordinances** - City codes vary significantly
3. **Document everything** - Photos, videos, measurements
4. **Mediation services** - Many cities offer free mediation
5. **Small claims court** - For damages under $5,000-$10,000

**WHEN TO CALL POLICE:**
- Threats or intimidation
- Property damage or trespassing
- Domestic violence situations
- Theft of property

**HOMEOWNERS ASSOCIATION (HOA):**
If you have an HOA:
- Follow complaint procedures first
- HOA rules override some local ordinances
- Architectural changes need approval
- Fines and liens possible for violations

**AVOID ESCALATION:**
❌ Retaliatory actions (making noise back)
❌ Trespassing to "teach a lesson"
❌ Threatening language or behavior
❌ Recording neighbors without consent (varies by state)
❌ Social media shaming campaigns

**PROTECT YOUR INVESTMENT:**
Good neighbor relations increase property values. Most disputes can be resolved without lawyers if handled respectfully and early.
        """,
        category=RightsCategory.LANDMINES,
        is_free=False
    ),

    "landmines_dating_relationships": RightsContent(
        title="Dating & Relationship Legal Traps",
        situation="Legal issues arising from romantic relationships",
        content="""
**DATING LEGAL LANDMINES:**

**CONSENT AND COMMUNICATION:**
- Consent can be withdrawn at any time
- "No" means no, regardless of relationship status
- Intoxicated people cannot give consent
- Document threatening behavior immediately

**REVENGE ACTIONS THAT ARE ILLEGAL:**
❌ Revenge porn (sharing intimate images)
❌ Posting private information online (doxxing)
❌ Accessing their social media accounts
❌ Stalking or following
❌ Damaging their property
❌ Contacting their employer to cause problems

**DOMESTIC VIOLENCE LAWS:**
Includes more than physical violence:
- Emotional/psychological abuse
- Financial control and manipulation  
- Isolation from friends and family
- Threats and intimidation
- Sexual coercion

**BREAKUP LEGAL ISSUES:**
**SHARED PROPERTY:**
- Gifts generally don't need to be returned
- Engagement rings: varies by state
- Shared lease/mortgage obligations continue
- Joint bank accounts: either party can empty
- Pet custody: pets are property, not like children

**RESTRAINING ORDERS:**
When you can get one:
- Threats of violence
- Stalking behavior
- Harassment after clear "no contact" request
- Fear for safety based on past behavior

**ONLINE DATING SAFETY:**
Legal protections are limited:
- Catfishing is usually not illegal (unless fraud involved)
- Age misrepresentation can be criminal
- Meeting strangers carries inherent risks
- Scam protection varies by platform

**WORKPLACE RELATIONSHIPS:**
- Check company policies before dating coworkers
- Supervisor/subordinate relationships often prohibited
- Sexual harassment laws still apply
- Document any retaliation for ending relationship

**COHABITATION RIGHTS:**
**Living Together Without Marriage:**
- No automatic property rights
- No spousal support if you break up
- Consider cohabitation agreements
- Emergency medical decision limitations

**DIGITAL PRIVACY:**
- Sharing passwords is risky legally
- Phone/computer searches may violate privacy
- Cloud storage access can be illegal
- Social media monitoring boundaries

**RED FLAGS - SEEK HELP:**
- Threats of violence or self-harm
- Extreme jealousy or controlling behavior
- Isolation from support systems
- Financial manipulation or control
- Any physical violence

**RESOURCES:**
- National Domestic Violence Hotline: 1-800-799-7233
- Local law enforcement for immediate danger
- Family court for protective orders
- Legal aid for low-income assistance
        """,
        category=RightsCategory.LANDMINES,
        is_free=False
    ),

    "landmines_contracts_agreements": RightsContent(
        title="Contracts & Agreements You Sign",
        situation="Understanding what you're legally agreeing to",
        content="""
**CONTRACT LEGAL TRAPS:**

**WHAT MAKES A CONTRACT BINDING:**
✅ Offer and acceptance
✅ Consideration (something of value exchanged)  
✅ Competent parties (adults, mentally capable)
✅ Legal purpose
✅ Written form (for certain contracts)

**CONTRACTS THAT MUST BE WRITTEN:**
- Real estate transactions
- Contracts over $500 in goods (UCC)
- Agreements lasting over 1 year
- Marriage contracts
- Debt assumption agreements

**DANGEROUS CLAUSES TO WATCH FOR:**
❌ **Arbitration clauses** - Give up right to sue in court
❌ **Liquidated damages** - Pre-set penalty amounts
❌ **Personal guarantees** - You're liable even if business fails  
❌ **Broad indemnification** - You pay their legal costs
❌ **Automatic renewal** - Contract extends without notice

**COMMON CONTRACT SCAMS:**
- Door-to-door sales (check cooling-off periods)
- Timeshare presentations with pressure tactics
- Auto extended warranties with fine print
- Home improvement contracts with upfront payments
- Multi-level marketing "business opportunities"

**YOUR RIGHT TO CANCEL:**
**3-Day Cooling-Off Period for:**
- Door-to-door sales over $25
- Home equity loans
- Timeshare purchases
- Some home improvement contracts

**UNCONSCIONABLE CONTRACTS:**
Courts may void contracts that are:
- Extremely one-sided
- Take advantage of someone's desperation
- Have hidden terms or deceptive language
- Violate public policy

**BEFORE SIGNING ANYTHING:**
1. **Read everything** - Including fine print
2. **Ask questions** - Get clarifications in writing
3. **Take time** - Don't sign under pressure
4. **Get copies** - Of everything you sign
5. **Understand penalties** - For breaking the agreement

**BREACH OF CONTRACT:**
**If You Break Contract:**
- May owe damages (actual losses caused)
- Specific performance (forced to complete)
- Liquidated damages (if clause exists)
- Legal fees (if contract requires)

**If They Break Contract:**
- You can sue for damages
- May get specific performance
- Might be able to cancel and get money back
- Legal fees recovery depends on contract terms

**EMPLOYMENT CONTRACTS:**
Watch for:
- Non-compete clauses (may not be enforceable)
- Non-disclosure agreements (NDAs)
- Intellectual property assignments
- At-will employment vs. contract terms

**DIGITAL AGREEMENTS:**
Terms of Service and Privacy Policies:
- Are legally binding contracts
- Can change without notice (usually)
- May include arbitration requirements
- Data collection and usage rights

**GET HELP BEFORE SIGNING:**
- Large purchases (homes, cars, business deals)
- Anything you don't understand
- Employment contracts with restrictions
- Any contract over $1,000
        """,
        category=RightsCategory.LANDMINES,
        is_free=False
    ),

    "landmines_family_disputes": RightsContent(
        title="Family Disputes & Legal Consequences",
        situation="Family conflicts that could become legal issues",
        content="""
**FAMILY LEGAL LANDMINES:**

**INHERITANCE DISPUTES:**
**COMMON TRIGGERS:**
- Dying without a will (intestate succession)
- Unequal distributions in wills
- Questions about mental capacity when will was made
- Second marriages and stepchildren issues
- Family members contesting wills

**PROTECT YOURSELF:**
- Document any promises about inheritance
- Keep records if you care for aging parents
- Don't assume verbal promises are binding
- Consider family meetings about estate plans

**ELDER ABUSE ALLEGATIONS:**
**WHAT CONSTITUTES ELDER ABUSE:**
- Physical abuse or neglect
- Financial exploitation
- Emotional or psychological abuse
- Sexual abuse
- Medical neglect or abandonment

**FINANCIAL EXPLOITATION WARNING SIGNS:**
- Sudden changes to wills or financial accounts
- Unexplained disappearance of funds or valuables
- Isolation from other family members
- New "best friends" or caregivers with financial access

**CHILD CUSTODY BATTLES:**
**WHAT HURTS YOUR CASE:**
❌ Badmouthing other parent to children
❌ Violating custody orders
❌ Substance abuse or criminal activity
❌ Dating multiple partners around children
❌ Moving far away without court permission

**WHAT HELPS YOUR CASE:**
✅ Following court orders exactly
✅ Documenting other parent's violations
✅ Staying involved in children's activities
✅ Maintaining stable home environment
✅ Avoiding conflict in front of children

**DIVORCE FINANCIAL LANDMINES:**
- Hiding assets (can backfire severely)
- Running up joint credit cards
- Emptying joint bank accounts
- Not disclosing retirement accounts
- Business valuation disputes

**GRANDPARENTS' RIGHTS:**
Limited but may include:
- Visitation rights in some circumstances
- Custody rights if parents are unfit
- Legal standing varies greatly by state
- Best interests of child standard applies

**FAMILY BUSINESS DISPUTES:**
**COMMON ISSUES:**
- Succession planning conflicts
- Unequal contributions vs. equal ownership
- Mixing family and business decisions
- Employment of family members
- Valuation for buyouts or divorce

**MENTAL HEALTH AND COMPETENCY:**
**Guardianship/Conservatorship Issues:**
- When family member can't make decisions
- Court process required for legal authority
- Alternatives: power of attorney, healthcare directives
- Family conflicts over what's "best" for person

**FAMILY LOANS AND MONEY:**
**DOCUMENT EVERYTHING:**
- Loans between family members
- Get written agreements for large amounts
- Consider gift vs. loan tax implications
- What happens if borrower dies?

**HOLIDAY AND TRADITION DISPUTES:**
While not typically legal issues, can escalate:
- Custody scheduling conflicts
- Religious differences in mixed families
- Cultural celebration disagreements
- Gift-giving expectations and financial strain

**PROTECTING FAMILY RELATIONSHIPS:**
1. **Communicate openly** about expectations
2. **Document financial arrangements**
3. **Consider family mediation** for major disputes
4. **Estate planning discussions** while everyone is healthy
5. **Professional help** for addiction or mental health issues

**WHEN TO SEEK LEGAL HELP:**
- Estate planning and will contests
- Child custody modifications
- Elder abuse allegations
- Family business partnership disputes
- Guardianship proceedings
        """,
        category=RightsCategory.LANDMINES,
        is_free=False
    ),

    "landmines_public_behavior": RightsContent(
        title="Public Behavior & Legal Consequences",
        situation="Actions in public that could lead to legal trouble",
        content="""
**PUBLIC BEHAVIOR LEGAL TRAPS:**

**WHAT'S LEGAL IN PUBLIC:**
✅ Taking photos/videos in public spaces
✅ Peaceful protests and free speech
✅ Recording police interactions
✅ Street photography and journalism
✅ Public performance (with permits if required)

**WHAT CAN GET YOU ARRESTED:**
❌ Public intoxication (varies by state)
❌ Disturbing the peace/disorderly conduct
❌ Public urination or indecent exposure
❌ Trespassing (staying after being asked to leave)
❌ Blocking pedestrian or vehicle traffic

**PROTEST AND FREE SPEECH RIGHTS:**
**PROTECTED ACTIVITIES:**
- Peaceful demonstrations on public property
- Distributing leaflets and petitions
- Wearing clothing with political messages
- Recording government officials in public

**RESTRICTIONS:**
- Time, place, and manner restrictions allowed
- Cannot block traffic without permits
- Private property owners can restrict speech
- Cannot incite violence or lawless action

**PHOTOGRAPHY/VIDEO LAWS:**
**YOU CAN RECORD:**
- Anyone in public spaces (no expectation of privacy)
- Police officers performing duties
- Public officials and government activities
- Accidents and newsworthy events

**YOU CANNOT RECORD:**
- Up-skirt or voyeuristic photography
- Private conversations (wiretapping laws)
- In bathrooms, changing rooms, private areas
- Children in some contexts (varies by state)

**BUSINESS AND PUBLIC PROPERTY:**
**PRIVATE BUSINESSES:**
- Can ask you to leave for any non-discriminatory reason
- Can prohibit recording on their property
- Cannot detain you without reasonable suspicion of theft
- Security guards have limited authority

**ALCOHOL-RELATED ISSUES:**
**OPEN CONTAINER LAWS:**
- Illegal to drink in public in most places
- Open alcohol containers in vehicles (even passengers)
- Beach/park alcohol restrictions vary by location
- Special event permits may allow exceptions

**PUBLIC INTOXICATION:**
- Being drunk in public is illegal in many states
- Can be arrested even without driving
- May face fines, jail time, and court costs
- Can affect employment and security clearances

**INTERACTIONS WITH SECURITY:**
**PRIVATE SECURITY GUARDS CANNOT:**
- Arrest you (unless citizen's arrest applies)
- Search you without consent
- Use excessive force
- Detain you indefinitely

**THEY CAN:**
- Ask you to leave private property
- Detain you briefly if they suspect theft
- Call police for assistance
- Use reasonable force to protect property

**CROWD CONTROL SITUATIONS:**
**POLICE ORDERS:**
- Must follow lawful police orders to disperse
- "Unlawful assembly" declarations require compliance
- Cannot resist even unlawful orders (fight in court later)
- Document police misconduct but don't interfere

**PETS IN PUBLIC:**
- Leash laws in most municipalities
- Service animals have special access rights
- Pet waste cleanup requirements
- Aggressive dog liability issues

**STREET PERFORMANCE/BUSKING:**
- Many cities require permits
- Cannot block pedestrian traffic
- Noise ordinances apply
- Donations generally legal, sales may need permits

**PROTECT YOURSELF:**
1. **Know local ordinances** - Laws vary by city/county
2. **Stay calm in confrontations** - Don't escalate situations
3. **ID requirements** - Know when you must provide identification
4. **Record interactions** - Protect yourself with documentation
5. **Avoid crowds during tensions** - Legal activities can become illegal in riots

**REMEMBER:**
What's legal in one place may be illegal in another. Tourist areas, government buildings, and private property often have special rules.
        """,
        category=RightsCategory.LANDMINES,
        is_free=False
    ),

    # CRIMINAL DEFENSE RIGHTS BUNDLE
    "criminal_arrest_rights": RightsContent(
        title="Your Rights When Arrested",
        situation="Being arrested and need to know your rights",
        content="""
**MIRANDA RIGHTS - WHAT THEY MEAN:**

**THE ACTUAL WORDS:**
"You have the right to remain silent. Anything you say can and will be used against you in a court of law. You have the right to an attorney. If you cannot afford an attorney, one will be provided for you."

**WHEN MIRANDA APPLIES:**
✅ Custodial interrogation (in custody + questioning)
✅ Not just when handcuffed - when not free to leave
✅ Must be read before questioning, not just arrest
✅ Applies to serious crimes and misdemeanors

**INVOKE YOUR RIGHTS CLEARLY:**
Say exactly: "I invoke my right to remain silent and want a lawyer."
- Don't say "maybe I should talk to a lawyer"
- Don't say "I think I want to remain silent"  
- Be clear and unambiguous

**WHAT HAPPENS DURING ARREST:**
1. **Handcuffs applied** - Don't resist
2. **Search incident to arrest** - They can search you
3. **Read rights** - Pay attention, ask if not read
4. **Transport to station** - Stay silent during ride
5. **Booking process** - Fingerprints, photos, paperwork

**SEARCH RIGHTS DURING ARREST:**
**POLICE CAN SEARCH:**
- Your person for weapons and evidence
- Area within your immediate reach
- Your vehicle if arrested during traffic stop
- Any containers that could hold weapons

**POLICE CANNOT SEARCH:**
- Your entire home without warrant (unless exigent circumstances)
- Locked containers in your car without probable cause
- Your phone without warrant (Riley v. California)
- Areas not within your immediate control

**THE BOOKING PROCESS:**
**WHAT TO EXPECT:**
- Personal property inventory
- Fingerprinting and photographs  
- Background checks and warrant searches
- Medical screening questions
- Assignment to holding cell

**YOUR RIGHTS AT BOOKING:**
- Right to phone call (usually within reasonable time)
- Right to medical attention if needed
- Right to remain silent during processing
- Right to refuse to answer questions beyond identification

**PHONE CALLS:**
- Usually get one or two calls
- Calls may be recorded (except attorney calls)
- Call a lawyer first, family second
- Don't discuss your case on recorded lines

**BAIL AND RELEASE:**
**TYPES OF RELEASE:**
- Released on own recognizance (OR)
- Cash bail
- Property bond  
- Bail bondsman (usually 10% fee)

**FACTORS AFFECTING BAIL:**
- Severity of charges
- Flight risk assessment
- Criminal history
- Ties to community
- Public safety concerns

**CRITICAL DON'TS:**
❌ Don't talk to police without lawyer
❌ Don't sign anything you don't understand
❌ Don't discuss case with other inmates
❌ Don't resist arrest (even if unlawful)
❌ Don't consent to searches
❌ Don't waive important rights

**REMEMBER:**
Police are trained interrogators. They can legally lie to you. They want you to talk. Exercise your right to remain silent and get a lawyer immediately.
        """,
        category=RightsCategory.CRIMINAL,
        is_free=False
    ),

    "criminal_court_procedures": RightsContent(
        title="Criminal Court Process",
        situation="Facing criminal charges and court proceedings",
        content="""
**CRIMINAL COURT PROCESS EXPLAINED:**

**FIRST COURT APPEARANCE - ARRAIGNMENT:**
**WHAT HAPPENS:**
- Charges formally read to you
- Asked to enter plea (guilty, not guilty, no contest)
- Bail/bond conditions set or reviewed
- Next court date scheduled
- Public defender appointed if needed

**PLEAS EXPLAINED:**
- **Guilty:** Admits you committed the crime
- **Not Guilty:** Forces prosecution to prove their case
- **No Contest (Nolo):** Not admitting guilt but not fighting charges

**ADVICE:** Usually plead "Not Guilty" at arraignment to preserve options.

**PRE-TRIAL PHASE:**
**DISCOVERY PROCESS:**
- Prosecutor must share evidence with defense
- Police reports, witness statements, lab results
- Video/audio evidence from arrests
- Expert witness information

**PRE-TRIAL MOTIONS:**
- Motion to suppress evidence (if illegally obtained)
- Motion to dismiss charges
- Motion for speedy trial
- Motion to exclude certain testimony

**PLEA BARGAINING:**
**COMMON PLEA DEALS:**
- Reduced charges (felony to misdemeanor)
- Reduced sentence recommendations
- Dismissal of some charges
- Alternative sentencing (probation, treatment)

**SHOULD YOU ACCEPT A PLEA?**
Consider:
- Strength of prosecution's evidence
- Consequences of going to trial
- Mandatory minimum sentences
- Collateral consequences (job, immigration, etc.)

**TRIAL RIGHTS:**
**YOUR CONSTITUTIONAL RIGHTS:**
✅ Right to jury trial (for crimes punishable by >6 months)
✅ Right to confront witnesses against you
✅ Right to present witnesses in your defense
✅ Right to testify or remain silent
✅ Presumption of innocence
✅ Burden on prosecution to prove guilt beyond reasonable doubt

**JURY SELECTION:**
- Questioning of potential jurors (voir dire)
- Challenges for cause (biased jurors)
- Peremptory challenges (limited number, no reason needed)
- Goal: Fair and impartial jury

**TRIAL PHASES:**
1. **Opening Statements** - Roadmap of each side's case
2. **Prosecution's Case** - Evidence and witnesses
3. **Defense Case** - Your evidence and witnesses (optional)
4. **Closing Arguments** - Final persuasion attempts
5. **Jury Instructions** - Judge explains the law
6. **Deliberation** - Jury decides verdict
7. **Verdict** - Guilty or not guilty

**SENTENCING:**
**IF FOUND GUILTY:**
- Pre-sentence investigation report
- Victim impact statements
- Character references for defendant
- Sentencing hearing
- Right to appeal conviction

**TYPES OF SENTENCES:**
- Fines and court costs
- Probation (supervised or unsupervised)
- Community service
- Jail/prison time
- Restitution to victims
- Treatment programs

**APPEALS PROCESS:**
**GROUNDS FOR APPEAL:**
- Legal errors during trial
- Ineffective assistance of counsel
- Prosecutorial misconduct
- Insufficient evidence
- Sentencing errors

**TIMELINE:**
- Usually 30 days to file notice of appeal
- Appellate brief due within 60-90 days
- Oral arguments (if requested)
- Written decision from appellate court

**WORKING WITH YOUR LAWYER:**
**BE HONEST:**
- Tell them everything, even bad facts
- Attorney-client privilege protects communications
- Lawyer needs full picture to defend you properly

**STAY INVOLVED:**
- Attend all court dates
- Follow all bail/bond conditions
- Keep lawyer updated on changes
- Ask questions if you don't understand
        """,
        category=RightsCategory.CRIMINAL,
        is_free=False
    ),

    "criminal_bail_bonds": RightsContent(
        title="Bail, Bonds & Getting Out of Jail",
        situation="Understanding bail system and getting released",
        content="""
**BAIL SYSTEM EXPLAINED:**

**PURPOSE OF BAIL:**
- Ensures appearance at future court dates
- Allows presumption of innocence until trial
- Not supposed to be punishment before conviction
- Courts cannot set excessive bail (8th Amendment)

**TYPES OF RELEASE:**
**Own Recognizance (OR):**
- Released on promise to appear
- No money required
- Based on ties to community, no flight risk

**CASH BAIL:**
- Full amount paid to court
- Money returned when case ends (minus fees)
- Can be paid by anyone
- Usually for less serious crimes or low amounts

**PROPERTY BOND:**
- Use real estate as collateral
- Property value must exceed bail amount
- Court puts lien on property
- Lose property if defendant doesn't appear

**BAIL BONDSMAN:**
- Pay 10-15% of total bail amount (non-refundable fee)
- Bondsman posts full amount with court
- Bondsman responsible if defendant flees
- May require collateral for large bonds

**FACTORS AFFECTING BAIL AMOUNT:**
**INCREASES BAIL:**
- Serious charges (especially violent crimes)
- Flight risk (no local ties, prior failures to appear)
- Extensive criminal history
- Danger to community
- Drug trafficking charges
- Immigration violations

**DECREASES BAIL:**
- Strong community ties (family, job, property)
- No prior criminal record
- Cooperation with law enforcement
- Non-violent charges
- Medical conditions requiring treatment

**BAIL CONDITIONS:**
**COMMON CONDITIONS:**
- Report to pretrial services regularly
- No contact with victims or witnesses
- No travel outside jurisdiction
- Surrender passport
- No alcohol or drug use (with testing)
- GPS monitoring
- Stay away from certain locations

**VIOLATING BAIL CONDITIONS:**
- Immediate arrest and return to jail
- Bail may be revoked entirely
- Additional charges possible
- Harder to get bail on future cases

**WORKING WITH BAIL BONDSMAN:**
**WHAT YOU NEED:**
- Valid identification
- Proof of employment/income
- Collateral information (property, vehicles)
- Co-signer with good credit (sometimes)

**BONDSMAN REQUIREMENTS:**
- Licensed by state
- Must explain all fees and conditions
- Cannot charge more than state-set rates
- Must return collateral when case ends

**ALTERNATIVES TO CASH BAIL:**
**PRETRIAL RELEASE PROGRAMS:**
- Electronic monitoring (ankle bracelet)
- Daily check-ins with pretrial services
- Drug/alcohol testing and treatment
- Mental health treatment requirements

**BAIL REDUCTION HEARINGS:**
**WHEN TO REQUEST:**
- Bail set too high for your financial situation
- Change in circumstances since initial setting
- New information about ties to community

**WHAT TO PRESENT:**
- Employment records and pay stubs
- Property ownership documents
- Family ties and support letters
- Community involvement proof
- Treatment program acceptance

**FAILURE TO APPEAR (FTA):**
**CONSEQUENCES:**
- Additional criminal charges
- Immediate arrest warrant issued
- Bail money forfeited
- Bondsman can arrest you
- Makes future bail much harder to get

**GETTING YOUR MONEY BACK:**
**CASH BAIL REFUND:**
- Returned when case ends (guilty or not guilty)
- May take 30-90 days to process
- Court fees may be deducted
- Keep all receipts and paperwork

**IMMIGRATION CONCERNS:**
- ICE holds can prevent release even with bail
- Notify lawyer immediately if you're not a citizen
- Some charges can trigger deportation proceedings
- Consider immigration consequences before pleading guilty

**TIPS FOR FAMILIES:**
- Don't use rent money or bill money for bail
- Understand you lose bondsman fee even if innocent
- Consider if person is likely to show up to court
- Get everything in writing from bondsman
- Ask about payment plans if available
        """,
        category=RightsCategory.CRIMINAL,
        is_free=False
    ),

    "criminal_lawyers": RightsContent(
        title="Getting a Lawyer & Legal Representation",
        situation="Need legal representation for criminal charges",
        content="""
**YOUR RIGHT TO A LAWYER:**

**WHEN YOU GET A LAWYER:**
✅ For any crime punishable by jail time
✅ During custodial interrogation
✅ At arraignment and all court proceedings
✅ During lineups after formal charges filed
✅ For appeals of convictions

**TYPES OF LAWYERS:**
**PUBLIC DEFENDER:**
- Free for those who qualify financially
- Experienced in criminal law
- Heavy caseloads (may have limited time)
- Appointed by court, you don't choose which one

**PRIVATE ATTORNEY:**
- You pay directly (or family pays)
- You choose which lawyer
- May have more time for your case
- Fees can be very expensive

**COURT-APPOINTED COUNSEL:**
- For those who don't qualify for public defender
- Private lawyer paid by court
- Rates set by court (lower than private rates)
- Quality varies significantly

**QUALIFYING FOR FREE LAWYER:**
**FINANCIAL ELIGIBILITY:**
- Income below federal poverty guidelines (usually)
- Vary by jurisdiction (some more generous)
- May consider assets, not just income
- Family help can disqualify you

**APPLICATION PROCESS:**
- Financial affidavit (sworn statement of income/assets)
- Pay stubs, bank statements, tax returns
- Court makes determination
- Can be reviewed if circumstances change

**CHOOSING A PRIVATE LAWYER:**
**WHAT TO LOOK FOR:**
- Criminal law experience (not just any lawyer)
- Experience with your type of charges
- Local court experience (knows judges/prosecutors)
- Good communication skills
- Reasonable fees and payment plans

**RED FLAGS:**
❌ Guarantees specific outcomes
❌ Asks for payment to "fix" charges before investigation
❌ Doesn't return phone calls promptly
❌ Has been disciplined by state bar
❌ Practices many different areas of law

**LEGAL FEES EXPLAINED:**
**RETAINER FEE:**
- Upfront payment held in trust account
- Lawyer bills time against this amount
- May need to replenish if case is complex
- Unused portion should be returned

**FLAT FEES:**
- One payment for entire case
- Usually for simple cases (DUI, misdemeanors)
- Doesn't change regardless of time spent
- Make sure you understand what's included

**HOURLY RATES:**
- Pay for actual time spent on case
- Rates vary widely ($200-$800+ per hour)
- Should get detailed time records
- Can become very expensive quickly

**WORKING WITH YOUR LAWYER:**
**YOUR RESPONSIBILITIES:**
- Be completely honest about all facts
- Follow all advice about court appearances
- Don't talk to police/prosecutors without lawyer present
- Keep lawyer updated on any developments
- Pay fees as agreed

**WHAT TO EXPECT FROM LAWYER:**
- Thorough investigation of case
- Regular communication about developments
- Honest assessment of strengths and weaknesses
- Zealous advocacy within bounds of law
- Confidentiality (attorney-client privilege)

**COMMUNICATION WITH LAWYER:**
**ATTORNEY-CLIENT PRIVILEGE:**
- Protects all communications between you and lawyer
- Cannot be forced to testify against you
- Extends to lawyer's staff and investigators
- Only exception: if you plan future crimes

**WHEN TO CALL YOUR LAWYER:**
- Any contact from police or prosecutors
- Violation of bail conditions
- New charges or arrests
- Questions about plea offers
- Before talking to anyone about your case

**FIRING YOUR LAWYER:**
**YOU CAN FIRE LAWYER IF:**
- Not communicating adequately
- Not prepared for court
- Conflicts of interest develop
- You lose confidence in representation

**CONSEQUENCES:**
- May delay court proceedings
- May lose money already paid
- New lawyer needs time to get up to speed
- Court may not grant continuances easily

**INEFFECTIVE ASSISTANCE OF COUNSEL:**
**GROUNDS FOR APPEAL:**
- Lawyer made serious errors
- Errors affected outcome of case
- Performance fell below professional standards
- Examples: failure to investigate, sleeping during trial, substance abuse

**LEGAL AID ORGANIZATIONS:**
- Help with appeals and post-conviction relief
- May assist with finding lawyers
- Some provide free consultations
- Law school legal clinics (supervised student practice)

**PAYMENT PLANS AND FINANCING:**
- Many lawyers offer payment plans
- Some accept credit cards
- Legal financing companies (high interest rates)
- Family/friend loans often cheaper than legal financing
        """,
        category=RightsCategory.CRIMINAL,
        is_free=False
    ),

    # BUSINESS & WORKPLACE RIGHTS BUNDLE
    "workplace_harassment": RightsContent(
        title="Workplace Harassment & Discrimination",
        situation="Experiencing harassment or discrimination at work",
        content="""
**WORKPLACE HARASSMENT LAWS:**

**PROTECTED CLASSES (FEDERAL):**
✅ Race, color, national origin
✅ Religion or religious beliefs
✅ Sex/gender (includes pregnancy)
✅ Age (40 and over)
✅ Disability
✅ Genetic information

**ADDITIONAL STATE PROTECTIONS:**
Many states also protect:
- Sexual orientation and gender identity
- Marital status
- Political affiliation
- Height and weight
- Criminal history (in some contexts)

**TYPES OF HARASSMENT:**
**QUID PRO QUO:**
- "This for that" - sexual favors for job benefits
- Supervisor demanding sexual activity for promotion
- Threats of firing for refusing advances

**HOSTILE WORK ENVIRONMENT:**
- Severe or pervasive harassment
- Interferes with work performance
- Creates intimidating workplace
- Based on protected characteristics

**EXAMPLES OF ILLEGAL HARASSMENT:**
❌ Racial slurs or ethnic jokes
❌ Sexual comments or advances
❌ Religious mockery or pressure
❌ Age-related insults ("old timer")
❌ Disability-related teasing
❌ Unwanted touching or sexual conduct

**WHAT TO DO IF HARASSED:**
1. **Document everything** - Dates, times, witnesses, what was said/done
2. **Report internally** - Follow company complaint procedures
3. **Keep copies** - Of all complaints and responses
4. **Report to EEOC** - File within 180-300 days (varies by state)
5. **Consult employment lawyer** - Know your options

**COMPANY OBLIGATIONS:**
**EMPLOYERS MUST:**
- Have anti-harassment policies
- Investigate complaints promptly and thoroughly
- Take corrective action to stop harassment
- Prevent retaliation against complainers
- Train supervisors on harassment laws

**RETALIATION IS ILLEGAL:**
**PROTECTED ACTIVITIES:**
- Filing harassment/discrimination complaints
- Participating in EEOC investigations
- Testifying in harassment cases
- Requesting reasonable accommodations

**EXAMPLES OF RETALIATION:**
❌ Firing, demoting, or disciplining complainant
❌ Cutting hours or changing job duties
❌ Hostile treatment after complaint
❌ Spreading rumors or blacklisting
❌ Denying promotions or benefits

**DISABILITY ACCOMMODATIONS:**
**REASONABLE ACCOMMODATIONS:**
- Modified work schedules
- Equipment modifications
- Workplace accessibility improvements
- Job duty adjustments
- Leave for medical treatment

**UNDUE HARDSHIP EXCEPTIONS:**
Employers don't have to provide accommodations that:
- Cost too much relative to company size
- Fundamentally alter business operations
- Create safety hazards

**PREGNANCY RIGHTS:**
**PREGNANCY DISCRIMINATION ACT:**
- Cannot fire or refuse to hire due to pregnancy
- Must treat pregnancy like any other medical condition
- Cannot force leave if able to work
- Must provide same benefits as other medical leaves

**RELIGIOUS ACCOMMODATIONS:**
**EMPLOYERS MUST ACCOMMODATE:**
- Religious dress and appearance
- Prayer schedules and religious holidays
- Dietary restrictions
- Religious practices that don't interfere with work

**AGE DISCRIMINATION:**
**PROTECTS WORKERS 40 AND OLDER:**
- Cannot use age in hiring/firing decisions
- Cannot force retirement (with limited exceptions)
- Benefits must be equal regardless of age
- Job ads cannot specify age preferences

**FILING COMPLAINTS:**
**EEOC PROCESS:**
1. **File charge** - Within 180-300 days of incident
2. **EEOC investigation** - Interview witnesses, review documents
3. **Mediation option** - Voluntary settlement discussions
4. **EEOC determination** - Cause found or no cause
5. **Right to sue letter** - If wanting to file lawsuit

**EMPLOYMENT LAWYERS:**
**WHEN TO CONSULT:**
- Severe or ongoing harassment
- Company fails to investigate properly
- Retaliation after complaining
- Wrongful termination
- Complex discrimination cases

**PROTECT YOURSELF:**
- Keep personal email account for documentation
- Save text messages and emails as evidence
- Get witness contact information
- Follow all company policies and procedures
- Don't quit without consulting lawyer (may affect claims)
        """,
        category=RightsCategory.WORKPLACE,
        is_free=False
    ),

    "workplace_firing_layoffs": RightsContent(
        title="Wrongful Termination & Layoffs",
        situation="Being fired or laid off and unsure of your rights",
        content="""
**EMPLOYMENT AT-WILL EXPLAINED:**

**AT-WILL EMPLOYMENT:**
- Employer can fire you for any reason or no reason
- You can quit for any reason or no reason
- No advance notice required (unless contract states otherwise)
- Applies in all states except Montana

**EXCEPTIONS TO AT-WILL:**
**ILLEGAL REASONS TO FIRE:**
❌ Discrimination based on protected class
❌ Retaliation for protected activities
❌ Violation of public policy
❌ Breach of employment contract
❌ Violation of implied contract

**PROTECTED ACTIVITIES:**
✅ Filing discrimination complaints
✅ Reporting safety violations (OSHA)
✅ Whistleblowing on illegal activities
✅ Taking legally protected leave (FMLA)
✅ Union organizing activities
✅ Refusing to break the law

**WRONGFUL TERMINATION SIGNS:**
**RED FLAGS:**
- Fired immediately after filing complaint
- Different reasons given for termination
- Inconsistent discipline compared to others
- Sudden negative performance reviews after complaint
- Fired during protected leave

**CONSTRUCTIVE DISCHARGE:**
When employer makes conditions so bad you're forced to quit:
- Impossible job assignments
- Harassment that company ignores
- Dangerous working conditions
- Significant pay/benefit cuts
- Demotion without cause

**SEVERANCE PAY:**
**NOT REQUIRED BY LAW:**
- Severance is voluntary (unless contract requires)
- Can negotiate amount and terms
- May include COBRA health insurance extension
- Often includes non-compete or non-disclosure agreements

**NEGOTIATING SEVERANCE:**
- Ask for more money or benefits
- Request positive reference letter
- Negotiate non-compete restrictions
- Get retraining or outplacement services

**UNEMPLOYMENT BENEFITS:**
**ELIGIBLE IF:**
- Lost job through no fault of your own
- Laid off due to business reasons
- Fired for poor performance (not misconduct)
- Meet work history and wage requirements

**DISQUALIFIED IF:**
- Fired for misconduct
- Quit without good cause
- Refuse suitable work offers
- Not available or actively seeking work

**COBRA HEALTH INSURANCE:**
**CONTINUATION COVERAGE:**
- Keep employer health insurance for 18-36 months
- Must pay full premium plus 2% administrative fee
- Must elect within 60 days of job loss
- Covers employee and eligible dependents

**FINAL PAYCHECK LAWS:**
**VARIES BY STATE:**
- Some require immediate payment upon termination
- Others allow until next regular payday
- Must include accrued vacation time (in most states)
- Cannot withhold pay for company property

**MASS LAYOFFS - WARN ACT:**
**60-DAY NOTICE REQUIRED FOR:**
- 100+ employees laid off at single site
- 50+ employees if they're 1/3 of workforce
- Plant closures affecting 50+ employees

**EXCEPTIONS:**
- Unforeseeable business circumstances
- Natural disasters
- Faltering companies seeking capital

**REFERENCES AND BACKGROUND CHECKS:**
**REFERENCE LAWS:**
- Most states protect truthful references
- Some limit references to dates of employment
- Cannot blacklist or give false information
- Former employees can sue for defamation

**NON-COMPETE AGREEMENTS:**
**ENFORCEABILITY VARIES:**
- Some states don't enforce them at all
- Must be reasonable in time, geography, scope
- Cannot prevent you from earning living
- May be void if fired without cause

**WHAT TO DO IF WRONGFULLY FIRED:**
1. **Document everything** - Save emails, performance reviews, witness info
2. **File for unemployment** - Do this immediately
3. **Preserve evidence** - Don't delete anything from personal devices
4. **Consult employment lawyer** - Many work on contingency
5. **File EEOC complaint** - If discrimination involved

**PROTECT YOURSELF:**
- Keep copies of important documents at home
- Maintain personal email for job-related communications
- Know your company's policies and procedures
- Document all incidents of harassment or discrimination
- Don't sign severance agreements without legal review
        """,
        category=RightsCategory.WORKPLACE,
        is_free=False
    ),

    "workplace_wages_hours": RightsContent(
        title="Wages, Hours & Overtime Pay",
        situation="Issues with pay, overtime, or work hours",
        content="""
**FAIR LABOR STANDARDS ACT (FLSA):**

**MINIMUM WAGE:**
- Federal minimum: $7.25/hour (as of 2024)
- States can set higher minimums
- Applies to most employees
- Tipped workers: $2.13/hour + tips (must equal minimum wage)

**OVERTIME PAY:**
**TIME AND A HALF REQUIRED:**
- After 40 hours in workweek
- Rate = regular hourly rate × 1.5
- Cannot average hours across multiple weeks
- Applies to non-exempt employees only

**EXEMPT vs NON-EXEMPT:**
**EXEMPT (NO OVERTIME):**
- Executive, administrative, professional roles
- Must be paid salary (not hourly)
- Must meet specific job duty tests
- Minimum salary: $684/week ($35,568/year)

**NON-EXEMPT (OVERTIME ELIGIBLE):**
- Most hourly workers
- Some salaried workers who don't meet exemption tests
- Blue-collar workers (regardless of pay level)
- First responders, paramedics

**COMMON WAGE VIOLATIONS:**
❌ Not paying for all hours worked
❌ Misclassifying employees as exempt
❌ Requiring off-the-clock work
❌ Not paying overtime rates
❌ Illegal payroll deductions
❌ Paying below minimum wage

**HOURS THAT MUST BE PAID:**
✅ Time spent working before/after shifts
✅ Short breaks (under 20 minutes)
✅ Training time (usually)
✅ Travel time between job sites
✅ On-call time (if restricted in activities)
✅ Time spent putting on/taking off safety equipment

**HOURS NOT REQUIRED TO BE PAID:**
- Meal breaks (30+ minutes, completely free from work)
- Commuting to/from regular workplace
- Time between shifts
- On-call time at home (if truly free)

**PAYROLL DEDUCTIONS:**
**LEGAL DEDUCTIONS:**
- Federal/state taxes and Social Security
- Court-ordered garnishments
- Voluntary deductions (insurance, 401k)
- Union dues (if authorized)

**ILLEGAL DEDUCTIONS (FOR NON-EXEMPT):**
- Business expenses (uniforms, tools)
- Cash register shortages
- Customer walkouts or bad checks
- Damage to company property (in most states)

**BREAK AND MEAL PERIOD LAWS:**
**FEDERAL LAW:**
- No required breaks or meal periods
- Short breaks (under 20 min) must be paid
- Meal breaks (30+ min) unpaid if completely free

**STATE LAWS VARY:**
- Some require meal breaks after certain hours
- Some mandate rest breaks
- Nursing mothers have break rights for pumping

**INDEPENDENT CONTRACTOR vs EMPLOYEE:**
**FACTORS FOR EMPLOYEE STATUS:**
- Company controls how work is done
- Work is integral to business
- Permanent or indefinite relationship
- Company provides tools/equipment
- Work done at company location

**MISCLASSIFICATION CONSEQUENCES:**
- Owe overtime and minimum wage
- Must pay employer portion of taxes
- Penalties and interest
- Department of Labor investigation

**STATE WAGE LAWS:**
**STATES OFTEN PROVIDE MORE:**
- Higher minimum wages
- Daily overtime (California: over 8 hours/day)
- Meal and break requirements
- Paid sick leave
- Final paycheck timing

**FILING WAGE COMPLAINTS:**
**DEPARTMENT OF LABOR:**
- Investigates FLSA violations
- Can recover back wages
- May assess penalties
- Protection from retaliation

**STATE LABOR DEPARTMENTS:**
- Handle state wage law violations
- Often faster than federal process
- May have different remedies available

**STATUTE OF LIMITATIONS:**
**FLSA CLAIMS:**
- 2 years for most violations
- 3 years for willful violations
- Back pay and "liquidated damages" (double damages)

**COLLECTIVE ACTION LAWSUITS:**
- Can join with other employees
- Share legal costs
- Class action for similar violations
- Court approval required

**PROTECT YOUR RIGHTS:**
1. **Keep time records** - Track all hours worked
2. **Save pay stubs** - Document wage payments
3. **Know your classification** - Exempt vs non-exempt
4. **Understand company policies** - But policies can't override law
5. **Report violations promptly** - Don't wait years to complain

**RETALIATION PROTECTION:**
- Cannot fire for filing wage complaints
- Cannot reduce hours or benefits
- Cannot demote or discipline
- Separate legal claim if retaliation occurs
        """,
        category=RightsCategory.WORKPLACE,
        is_free=False
    ),

    # FAMILY & PERSONAL RIGHTS BUNDLE
    "family_divorce_separation": RightsContent(
        title="Divorce & Legal Separation",
        situation="Going through divorce or considering separation",
        content="""
**DIVORCE BASICS:**

**GROUNDS FOR DIVORCE:**
**NO-FAULT DIVORCE (All States):**
- Irreconcilable differences
- Incompatibility  
- Irretrievable breakdown of marriage
- Living apart for specified time

**FAULT-BASED GROUNDS (Some States):**
- Adultery
- Abandonment
- Physical or mental cruelty
- Substance abuse
- Criminal conviction

**LEGAL SEPARATION vs DIVORCE:**
**LEGAL SEPARATION:**
- Still legally married
- Cannot remarry
- May keep insurance benefits
- Religious considerations
- Trial period before divorce

**DIVORCE:**
- Marriage completely dissolved
- Free to remarry
- All legal ties severed
- Final division of assets

**PROPERTY DIVISION:**
**COMMUNITY PROPERTY STATES (9 states):**
- All marital property split 50/50
- Separate property remains separate
- Includes: AZ, CA, ID, LA, NV, NM, TX, WA, WI

**EQUITABLE DISTRIBUTION (Other states):**
- Fair distribution (not necessarily equal)
- Court considers multiple factors
- Length of marriage, income, contributions

**MARITAL vs SEPARATE PROPERTY:**
**MARITAL PROPERTY:**
- Assets acquired during marriage
- Income earned during marriage
- Retirement benefits accrued during marriage
- Debt incurred during marriage

**SEPARATE PROPERTY:**
- Assets owned before marriage
- Inheritance received by one spouse
- Gifts to one spouse only
- Personal injury settlements

**SPOUSAL SUPPORT/ALIMONY:**
**FACTORS CONSIDERED:**
- Length of marriage
- Income disparity between spouses
- Age and health of parties
- Standard of living during marriage
- Contributions to marriage (including homemaking)

**TYPES OF ALIMONY:**
- Temporary (during divorce proceedings)
- Rehabilitative (short-term, for education/training)
- Permanent (ongoing, usually long marriages)
- Lump sum (one-time payment)

**DEBT DIVISION:**
**MARITAL DEBT:**
- Credit cards used for family expenses
- Mortgage on family home
- Car loans during marriage
- Business debts (if for family benefit)

**SEPARATE DEBT:**
- Debt from before marriage
- Credit cards for personal use only
- Gambling debts
- Student loans (sometimes separate)

**PROTECTING YOUR INTERESTS:**
**FINANCIAL PREPARATION:**
- Gather financial documents
- Open individual bank account
- Establish individual credit
- Document all assets and debts
- Take photos of valuable items

**CHILDREN CONSIDERATIONS:**
- Child custody and visitation
- Child support obligations
- Health insurance coverage
- Educational expenses
- Tax exemptions

**ALTERNATIVE DISPUTE RESOLUTION:**
**MEDIATION:**
- Neutral third party helps negotiate
- Less expensive than litigation
- Confidential process
- Parties control outcome

**COLLABORATIVE DIVORCE:**
- Each spouse has lawyer
- Team approach with financial experts
- Agreement not to go to court
- Focus on problem-solving

**RED FLAGS - GET HELP IMMEDIATELY:**
- Domestic violence or threats
- Hidden assets or financial deception
- Complex business interests
- Significant debt or financial problems
- International custody issues

**TEMPORARY ORDERS:**
During divorce proceedings, court can order:
- Temporary custody and support
- Who stays in marital home
- Payment of bills and expenses
- Restraining orders on assets
- Protection from harassment

**DIVORCE WITH CHILDREN:**
**BEST INTERESTS STANDARD:**
Court considers:
- Emotional ties with parents
- Parent's ability to provide care
- Child's adjustment to home/school/community
- Mental and physical health of all involved
- History of domestic violence

**DO NOT:**
❌ Hide assets or income
❌ Use children as messengers
❌ Violate temporary court orders
❌ Date openly during proceedings (affects some states)
❌ Make major financial decisions without approval
        """,
        category=RightsCategory.FAMILY,
        is_free=False
    ),

    "family_child_custody": RightsContent(
        title="Child Custody & Support",
        situation="Dealing with child custody or support issues",
        content="""
**CHILD CUSTODY TYPES:**

**LEGAL CUSTODY:**
- Right to make major decisions for child
- Education, healthcare, religion
- Can be joint or sole
- Different from physical custody

**PHYSICAL CUSTODY:**
- Where child lives day-to-day
- Can be joint (shared) or sole
- Determines visitation schedules
- Affects child support calculations

**CUSTODY ARRANGEMENTS:**
**JOINT CUSTODY:**
- Both parents share decision-making
- May or may not share physical time equally
- Requires good communication between parents
- Presumed best for children in many states

**SOLE CUSTODY:**
- One parent has primary responsibility
- Other parent may have visitation rights
- Used when joint custody not feasible
- Required if domestic violence history

**BEST INTERESTS OF CHILD STANDARD:**
**FACTORS COURTS CONSIDER:**
✅ Child's physical and emotional needs
✅ Parent's ability to care for child
✅ Child's relationship with each parent
✅ Stability of home environments
✅ Child's adjustment to current situation
✅ Any history of domestic violence
✅ Parent's mental and physical health

**WHAT HURTS YOUR CUSTODY CASE:**
❌ Domestic violence history
❌ Substance abuse problems
❌ Criminal record (especially violent crimes)
❌ Alienating child from other parent
❌ Unstable housing or employment
❌ Mental health issues (untreated)

**WHAT HELPS YOUR CUSTODY CASE:**
✅ Stable home and employment
✅ Active involvement in child's life
✅ Following court orders
✅ Encouraging relationship with other parent
✅ Good physical and mental health
✅ Strong support system

**CHILD SUPPORT CALCULATIONS:**
**INCOME SHARES MODEL (Most States):**
- Based on both parents' incomes
- Considers number of children
- Accounts for custody time
- Uses state guidelines/formulas

**FACTORS AFFECTING SUPPORT:**
- Gross income of both parents
- Number of overnight visits
- Health insurance costs
- Childcare expenses
- Other children's support obligations

**TYPES OF INCOME INCLUDED:**
- Wages and salary
- Overtime and bonuses
- Self-employment income
- Rental income
- Unemployment benefits
- Social Security benefits

**MODIFYING CUSTODY/SUPPORT:**
**SUBSTANTIAL CHANGE REQUIRED:**
- Significant change in income
- Relocation of parent
- Change in child's needs
- Remarriage affecting circumstances
- Parent's failure to exercise visitation

**COURT PROCESS:**
- File petition for modification
- Serve other parent with papers
- Attend mediation (if required)
- Present evidence at hearing
- Court issues new order

**ENFORCEMENT OF ORDERS:**
**IF PARENT DOESN'T PAY SUPPORT:**
- Wage garnishment
- Asset seizure
- Tax refund interception
- License suspension
- Contempt of court (possible jail)

**IF PARENT VIOLATES CUSTODY:**
- Document violations
- File contempt motion
- Request make-up time
- Possible custody modification
- Criminal charges (in extreme cases)

**RELOCATION WITH CHILDREN:**
**NOTICE REQUIREMENTS:**
- Must notify other parent (usually 30-60 days)
- May need court permission
- Consider impact on visitation
- Best interests standard applies

**FACTORS COURTS CONSIDER:**
- Reason for move
- Distance of relocation
- Impact on child's relationship with other parent
- Educational and social opportunities
- Economic benefits of move

**PARENTING PLANS:**
**SHOULD INCLUDE:**
- Detailed visitation schedule
- Holiday and vacation time
- Transportation arrangements
- Communication guidelines
- Decision-making procedures
- Dispute resolution process

**VISITATION RIGHTS:**
**REASONABLE VISITATION:**
- Parents work out schedule
- Flexible arrangements
- Requires good communication
- Court doesn't specify exact times

**FIXED VISITATION:**
- Court orders specific schedule
- Detailed dates and times
- Used when parents can't agree
- Provides certainty and structure

**SUPERVISED VISITATION:**
- Third party present during visits
- Court orders when safety concerns exist
- May be temporary or permanent
- Can be professional or family member

**PROTECTING YOUR CHILDREN:**
- Never use children as messengers
- Don't bad-mouth other parent to children
- Follow court orders exactly
- Document any safety concerns
- Put children's needs first
- Consider counseling if children struggle
        """,
        category=RightsCategory.FAMILY,
        is_free=False
    )
}

# Pricing for categories
CATEGORY_PRICES = {
    RightsCategory.TRAFFIC: 0.0,  # Free preview
    RightsCategory.HOUSING: 4.99,
    RightsCategory.LANDMINES: 4.99,
    RightsCategory.CRIMINAL: 4.99,
    RightsCategory.WORKPLACE: 4.99,
    RightsCategory.FAMILY: 4.99,
    RightsCategory.HEALTHCARE: 4.99,
    RightsCategory.STUDENT: 3.99,
    RightsCategory.DIGITAL: 4.99,
    RightsCategory.CONSUMER: 4.99
}

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Rights Helper API - Know Your Rights Instantly"}

@api_router.get("/categories")
async def get_categories():
    """Get all available rights categories"""
    return {
        "categories": [
            {
                "id": "traffic",
                "name": "Traffic Stops",
                "description": "Your rights during police traffic stops",
                "price": 0.0,
                "is_free": True,
                "icon": "🚗"
            },
            {
                "id": "tenant", 
                "name": "Tenant Rights",
                "description": "Protect yourself from landlord issues",
                "price": 2.99,
                "is_free": False,
                "icon": "🏠"
            },
            {
                "id": "workplace",
                "name": "Workplace Rights", 
                "description": "Employment law and worker protections",
                "price": 2.99,
                "is_free": False,
                "icon": "💼",
                "coming_soon": True
            },
            {
                "id": "criminal",
                "name": "Criminal Defense",
                "description": "Court procedures and arrest rights", 
                "price": 2.99,
                "is_free": False,
                "icon": "⚖️",
                "coming_soon": True
            }
        ]
    }

@api_router.get("/rights/{category}")
async def get_rights_by_category(category: RightsCategory):
    """Get all rights content for a specific category"""
    rights = [content for content in RIGHTS_CONTENT.values() 
             if content.category == category]
    
    return {
        "category": category.value,
        "rights": [
            {
                "id": key,
                "title": content.title,
                "situation": content.situation,
                "is_free": content.is_free
            }
            for key, content in RIGHTS_CONTENT.items()
            if content.category == category
        ]
    }

@api_router.get("/rights/{category}/{right_id}")
async def get_specific_right(category: RightsCategory, right_id: str, user_id: str = Query(None)):
    """Get specific rights content"""
    
    if right_id not in RIGHTS_CONTENT:
        raise HTTPException(status_code=404, detail="Rights content not found")
    
    content = RIGHTS_CONTENT[right_id]
    
    # Check if content is free or user has purchased access
    if content.is_free:
        return content
    
    # For paid content, check if user has access (simplified for demo)
    # In production, you'd check the database for user purchases
    if user_id:
        # Check if user purchased this category
        access = await db.category_access.find_one({
            "user_id": user_id,
            "category": category.value
        })
        if access:
            return content
    
    # Return preview for paid content
    return {
        "id": content.id,
        "title": content.title,
        "situation": content.situation,
        "category": content.category,
        "preview": content.content[:200] + "...",
        "is_free": False,
        "requires_purchase": True,
        "price": CATEGORY_PRICES[category]
    }

@api_router.post("/purchase/{category}")
async def purchase_category(category: RightsCategory, request: CheckoutRequest):
    """Purchase access to a rights category"""
    
    price = CATEGORY_PRICES.get(category, 2.99)
    
    if price == 0:
        return {"message": "This category is free", "access_granted": True}
    
    try:
        # Initialize Stripe checkout
        host_url = str(request.origin_url)
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        # Build success and cancel URLs
        success_url = f"{request.origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{request.origin_url}/payment-cancel"
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=price,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "category": category.value,
                "source": "rights_helper_app"
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction = PaymentTransaction(
            session_id=session.session_id,
            amount=price,
            currency="usd",
            payment_status=PaymentStatus.PENDING,
            metadata=checkout_request.metadata,
            category=category
        )
        
        await db.payment_transactions.insert_one(transaction.dict())
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id
        }
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Purchase error: {e}")
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")

@api_router.get("/search")
async def search_rights(query: str = Query(..., description="Search term")):
    """Search through all rights content"""
    
    results = []
    query_lower = query.lower()
    
    for key, content in RIGHTS_CONTENT.items():
        if (query_lower in content.title.lower() or 
            query_lower in content.situation.lower() or 
            query_lower in content.content.lower()):
            
            results.append({
                "id": key,
                "title": content.title,
                "situation": content.situation,
                "category": content.category.value,
                "is_free": content.is_free,
                "price": 0 if content.is_free else CATEGORY_PRICES[content.category]
            })
    
    return {"query": query, "results": results}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()