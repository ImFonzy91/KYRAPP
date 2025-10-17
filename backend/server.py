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
from rights_server import api_router as rights_router

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
    TENANT = "tenant"
    WORKPLACE = "workplace"
    CRIMINAL = "criminal"
    CONSTITUTIONAL = "constitutional"

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

    # PAID TENANT RIGHTS
    "tenant_eviction": RightsContent(
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
        category=RightsCategory.TENANT,
        is_free=False
    ),

    "tenant_security_deposit": RightsContent(
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
        category=RightsCategory.TENANT,
        is_free=False
    ),

    "tenant_landlord_entry": RightsContent(
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
        category=RightsCategory.TENANT,
        is_free=False
    )
}

# Pricing for categories
CATEGORY_PRICES = {
    RightsCategory.TRAFFIC: 0.0,  # Free
    RightsCategory.TENANT: 2.99,
    RightsCategory.WORKPLACE: 2.99,
    RightsCategory.CRIMINAL: 2.99,
    RightsCategory.CONSTITUTIONAL: 2.99
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

class CartCheckoutRequest(BaseModel):
    bundles: List[str]
    origin_url: str

@api_router.post("/purchase/cart")
async def purchase_cart(request: CartCheckoutRequest):
    """Purchase multiple bundles with discount pricing"""
    
    if not request.bundles or len(request.bundles) == 0:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate price with bundle discounts
    count = len(request.bundles)
    if count >= 13:
        total_price = 20.00  # All 13 bundles deal
        description = f"Complete Rights Package - All {count} Bundles"
    elif count >= 5:
        total_price = 12.99  # Any 5+ bundles deal
        description = f"Bundle Deal - {count} Rights Bundles"
    else:
        # Calculate individual prices - all $2.99 for launch
        bundle_prices = {
            "traffic": 2.99, "housing": 2.99, "property": 2.99, "landmines": 2.99,
            "criminal": 2.99, "workplace": 2.99, "family": 2.99, "divorce": 2.99,
            "immigration": 2.99, "healthcare": 2.99, "student": 2.99, 
            "digital": 2.99, "consumer": 2.99
        }
        total_price = sum(bundle_prices.get(b, 2.99) for b in request.bundles)
        description = f"{count} Rights Bundle{'s' if count > 1 else ''}"
    
    try:
        # Initialize Stripe checkout
        host_url = str(request.origin_url)
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        # Build success and cancel URLs
        success_url = f"{request.origin_url}/?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{request.origin_url}/?payment=cancelled"
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=total_price,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "bundles": ",".join(request.bundles),
                "bundle_count": str(count),
                "source": "rights_helper_cart"
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id,
            "amount": total_price
        }
        
    except Exception as e:
        logger.error(f"Cart checkout error: {e}")
        raise HTTPException(status_code=500, detail=f"Checkout failed: {str(e)}")

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

# Include the routers in the main app
app.include_router(api_router)
app.include_router(rights_router)

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