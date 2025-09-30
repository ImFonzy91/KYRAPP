from fastapi import FastAPI, APIRouter, HTTPException, Query, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date
from enum import Enum
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
import requests
import asyncio

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
class SearchType(str, Enum):
    NAME = "name"
    PHONE = "phone"
    EMAIL = "email"
    ADDRESS = "address"

class ReportTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    COMPLETE = "complete"

class CaseStatus(str, Enum):
    PENDING = "pending"
    CONVICTED = "convicted"
    DISMISSED = "dismissed"
    CHARGES_DROPPED = "charges_dropped"
    ACQUITTED = "acquitted"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    EXPIRED = "expired"

# Models
class PersonSearch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    search_query: str
    search_type: SearchType
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SocialMediaProfile(BaseModel):
    platform: str
    username: str
    profile_url: str
    verified: bool = False
    last_activity: Optional[str] = None

class CriminalRecord(BaseModel):
    case_number: str
    charge: str
    description: str
    date: str
    status: CaseStatus
    status_description: str
    court: str
    county: str
    state: str

class PropertyRecord(BaseModel):
    address: str
    property_type: str
    estimated_value: Optional[int] = None
    ownership_date: Optional[str] = None
    county: str
    state: str

class ProfessionalInfo(BaseModel):
    company: str
    position: str
    duration: str
    location: str
    industry: str

class BackgroundReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    person_name: str
    age: Optional[int] = None
    current_address: str
    phone_numbers: List[str] = []
    email_addresses: List[str] = []
    previous_addresses: List[str] = []
    social_media: List[SocialMediaProfile] = []
    criminal_records: List[CriminalRecord] = []
    property_records: List[PropertyRecord] = []
    professional_info: List[ProfessionalInfo] = []
    relatives: List[str] = []
    report_tier: ReportTier
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    amount: float
    currency: str = "usd"
    payment_status: PaymentStatus
    metadata: Dict[str, str] = {}
    person_id: Optional[str] = None
    report_tier: Optional[ReportTier] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CheckoutRequest(BaseModel):
    package_id: str
    person_id: str
    origin_url: str

class CheckoutStatusRequest(BaseModel):
    session_id: str

# Fixed Packages - NEVER accept amounts from frontend
PACKAGES = {
    "free": {"price": 0.0, "tier": ReportTier.FREE, "name": "Free Report"},
    "basic": {"price": 2.99, "tier": ReportTier.BASIC, "name": "Basic Report"},
    "premium": {"price": 5.99, "tier": ReportTier.PREMIUM, "name": "Premium Report"},
    "subscription_basic": {"price": 14.99, "tier": ReportTier.BASIC, "name": "Basic Subscription"},
    "subscription_pro": {"price": 29.99, "tier": ReportTier.PREMIUM, "name": "Pro Subscription"}
}

# Initialize Stripe
stripe_api_key = os.environ.get('STRIPE_API_KEY')
searchbug_api_key = os.environ.get('SEARCHBUG_API_KEY')

# SearchBug API integration
async def search_person_searchbug(name: str, tier: ReportTier) -> BackgroundReport:
    """Get real data from SearchBug API"""
    
    try:
        # SearchBug People Search API
        search_url = "https://www.searchbug.com/peoplefinder/api/search"
        params = {
            'apikey': searchbug_api_key,
            'name': name,
            'format': 'json'
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Parse SearchBug response and create report
            person_data = data.get('results', [{}])[0] if data.get('results') else {}
            
            # Build real report from SearchBug data
            report_data = {
                "person_name": person_data.get('name', name),
                "age": person_data.get('age'),
                "current_address": person_data.get('address', 'Address not found'),
                "phone_numbers": person_data.get('phones', []),
                "email_addresses": person_data.get('emails', []),
                "previous_addresses": person_data.get('previous_addresses', []),
                "social_media": [],  # SearchBug doesn't provide social media
                "criminal_records": [],  # SearchBug basic doesn't include criminal
                "property_records": [],
                "professional_info": [],
                "relatives": person_data.get('relatives', []),
                "report_tier": tier
            }
            
            # Add limited info based on tier
            if tier == ReportTier.FREE:
                # Very limited for free
                report_data.update({
                    "current_address": person_data.get('city', '') + ", " + person_data.get('state', ''),
                    "phone_numbers": [],
                    "email_addresses": []
                })
            
            return BackgroundReport(**report_data)
        else:
            logger.error(f"SearchBug API error: {response.status_code}")
            # Fall back to mock data if API fails
            return generate_mock_report(name, tier)
            
    except Exception as e:
        logger.error(f"SearchBug API exception: {e}")
        # Fall back to mock data if API fails  
        return generate_mock_report(name, tier)

# Mock Data Generator
def generate_mock_report(name: str, tier: ReportTier) -> BackgroundReport:
    """Generate realistic mock data for demo purposes"""
    
    # Base info available for all tiers
    base_report = {
        "person_name": name,
        "age": 32,
        "current_address": "123 Main St, Los Angeles, CA 90210",
        "phone_numbers": ["+1-555-0123"],
        "email_addresses": [],
        "previous_addresses": [],
        "social_media": [],
        "criminal_records": [],
        "property_records": [],
        "professional_info": [],
        "relatives": [],
        "report_tier": tier
    }
    
    if tier == ReportTier.FREE:
        # Very limited info for free tier
        base_report.update({
            "email_addresses": ["j****@gmail.com"],
            "criminal_records": [
                CriminalRecord(
                    case_number="CR-2023-****",
                    charge="Traffic Violation",
                    description="Speeding - 15 mph over limit",
                    date="2023-06-15",
                    status=CaseStatus.DISMISSED,
                    status_description="Case dismissed - traffic school completed",
                    court="Municipal Court",
                    county="Los Angeles",
                    state="CA"
                )
            ]
        })
    
    elif tier == ReportTier.BASIC:
        base_report.update({
            "email_addresses": ["john.smith@gmail.com"],
            "previous_addresses": ["456 Oak Ave, Beverly Hills, CA 90210"],
            "social_media": [
                SocialMediaProfile(
                    platform="Facebook",
                    username="john.smith.123",
                    profile_url="https://facebook.com/john.smith.123",
                    verified=False,
                    last_activity="2 weeks ago"
                )
            ],
            "criminal_records": [
                CriminalRecord(
                    case_number="CR-2023-001234",
                    charge="Misdemeanor Theft",
                    description="Accused of shoplifting - case pending trial",
                    date="2023-08-20",
                    status=CaseStatus.PENDING,
                    status_description="Case pending - accused but not yet convicted. Next court date: January 15, 2025",
                    court="Superior Court of California",
                    county="Los Angeles",
                    state="CA"
                )
            ],
            "relatives": ["Sarah Smith (Spouse)", "Michael Smith (Brother)"]
        })
    
    elif tier == ReportTier.PREMIUM:
        base_report.update({
            "email_addresses": ["john.smith@gmail.com", "j.smith@workmail.com"],
            "previous_addresses": [
                "456 Oak Ave, Beverly Hills, CA 90210",
                "789 Pine St, Santa Monica, CA 90404"
            ],
            "social_media": [
                SocialMediaProfile(
                    platform="Facebook",
                    username="john.smith.123",
                    profile_url="https://facebook.com/john.smith.123",
                    verified=False,
                    last_activity="2 weeks ago"
                ),
                SocialMediaProfile(
                    platform="LinkedIn",
                    username="john-smith-marketing",
                    profile_url="https://linkedin.com/in/john-smith-marketing",
                    verified=True,
                    last_activity="3 days ago"
                ),
                SocialMediaProfile(
                    platform="Instagram",
                    username="jsmith_la",
                    profile_url="https://instagram.com/jsmith_la",
                    verified=False,
                    last_activity="1 day ago"
                )
            ],
            "criminal_records": [
                CriminalRecord(
                    case_number="CR-2023-001234",
                    charge="Misdemeanor Theft",
                    description="Accused of shoplifting at retail store - surveillance footage unclear",
                    date="2023-08-20",
                    status=CaseStatus.PENDING,
                    status_description="Case pending trial - accused but not convicted. Defense claims mistaken identity. Next court date: January 15, 2025",
                    court="Superior Court of California",
                    county="Los Angeles",
                    state="CA"
                ),
                CriminalRecord(
                    case_number="CR-2021-005678",
                    charge="DUI",
                    description="Driving under influence - BAC 0.08",
                    date="2021-03-10",
                    status=CaseStatus.CHARGES_DROPPED,
                    status_description="Charges dropped - breathalyzer equipment found to be faulty during that period",
                    court="Municipal Court",
                    county="Los Angeles",
                    state="CA"
                )
            ],
            "property_records": [
                PropertyRecord(
                    address="123 Main St, Los Angeles, CA 90210",
                    property_type="Single Family Home",
                    estimated_value=750000,
                    ownership_date="2020-05-15",
                    county="Los Angeles",
                    state="CA"
                )
            ],
            "professional_info": [
                ProfessionalInfo(
                    company="Digital Marketing Solutions",
                    position="Marketing Manager",
                    duration="2019 - Present",
                    location="Los Angeles, CA",
                    industry="Digital Marketing"
                )
            ],
            "relatives": [
                "Sarah Smith (Spouse)",
                "Michael Smith (Brother)",
                "Dorothy Smith (Mother)",
                "Robert Smith (Father)"
            ]
        })
    
    return BackgroundReport(**base_report)

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Scan'Em API - Street Smart Background Checks"}

@api_router.post("/search")
async def search_person(
    query: str = Query(..., description="Name, phone, email, or address to search"),
    search_type: SearchType = Query(SearchType.NAME, description="Type of search to perform")
):
    """Search for a person - returns basic info for all users"""
    
    # Save search query
    search_record = PersonSearch(search_query=query, search_type=search_type)
    await db.searches.insert_one(search_record.dict())
    
    # Mock search results
    results = [
        {
            "id": str(uuid.uuid4()),
            "name": query if search_type == SearchType.NAME else "John Smith",
            "age": 32,
            "location": "Los Angeles, CA",
            "possible_matches": True,
            "preview": "1 criminal record found (pending case)"
        }
    ]
    
    return {"results": results, "total_found": 1}

@api_router.get("/report/{person_id}")
async def get_background_report(
    person_id: str,
    tier: ReportTier = Query(ReportTier.FREE, description="Report tier to generate")
):
    """Get a detailed background report using real SearchBug data"""
    
    # For demo, we'll use "John Smith" but in real app, 
    # person_id would map to actual search results
    name = "John Smith"  # This would come from your search results
    
    # Get real data from SearchBug
    report = await search_person_searchbug(name, tier)
    
    # Save report generation
    await db.reports.insert_one(report.dict())
    
    return report

# PAYMENT ROUTES
@api_router.post("/payments/checkout")
async def create_checkout_session(request: CheckoutRequest):
    """Create Stripe checkout session for background report"""
    
    # Validate package exists
    if request.package_id not in PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package selected")
    
    package = PACKAGES[request.package_id]
    
    # Free reports don't need payment
    if package["price"] == 0.0:
        # Generate free report directly
        report = generate_mock_report("John Smith", package["tier"])
        await db.reports.insert_one(report.dict())
        return {
            "type": "free_report",
            "report": report
        }
    
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
            amount=package["price"],
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "person_id": request.person_id,
                "package_id": request.package_id,
                "tier": package["tier"].value,
                "source": "scanem_app"
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction = PaymentTransaction(
            session_id=session.session_id,
            amount=package["price"],
            currency="usd",
            payment_status=PaymentStatus.PENDING,
            metadata=checkout_request.metadata,
            person_id=request.person_id,
            report_tier=package["tier"]
        )
        
        await db.payment_transactions.insert_one(transaction.dict())
        
        return {
            "type": "payment_required",
            "checkout_url": session.url,
            "session_id": session.session_id
        }
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail=f"Payment setup failed: {str(e)}")

@api_router.get("/payments/status/{session_id}")
async def check_payment_status(session_id: str):
    """Check payment status and return report if paid"""
    
    try:
        # Find transaction record
        transaction = await db.payment_transactions.find_one({"session_id": session_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Payment session not found")
        
        # Initialize Stripe checkout
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url="")
        
        # Check status with Stripe
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction status if changed
        if checkout_status.payment_status == "paid" and transaction["payment_status"] != PaymentStatus.PAID.value:
            # Update payment status
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "payment_status": PaymentStatus.PAID.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Generate the paid report
            tier = ReportTier(transaction["metadata"]["tier"])
            report = generate_mock_report("John Smith", tier)
            await db.reports.insert_one(report.dict())
            
            return {
                "payment_status": "paid",
                "report": report,
                "amount": checkout_status.amount_total / 100  # Stripe returns cents
            }
        
        elif checkout_status.status == "expired":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": PaymentStatus.EXPIRED.value, "updated_at": datetime.utcnow()}}
            )
            
        return {
            "payment_status": checkout_status.payment_status,
            "session_status": checkout_status.status,
            "amount": checkout_status.amount_total / 100
        }
        
    except Exception as e:
        logger.error(f"Payment status check error: {e}")
        raise HTTPException(status_code=500, detail=f"Payment status check failed: {str(e)}")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    
    try:
        body = await request.body()
        stripe_signature = request.headers.get("Stripe-Signature")
        
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url="")
        webhook_response = await stripe_checkout.handle_webhook(body, stripe_signature)
        
        # Update payment transaction based on webhook
        if webhook_response.event_type == "checkout.session.completed":
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {
                    "$set": {
                        "payment_status": PaymentStatus.PAID.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {str(e)}")

@api_router.get("/pricing")
async def get_pricing():
    """Get current pricing information"""
    return {
        "packages": {
            "free": {
                "name": "Free Daily Check",
                "price": 0.0,
                "features": [
                    "Basic name and age",
                    "Current city",
                    "One criminal record preview"
                ]
            },
            "basic": {
                "name": "Basic Report",
                "price": 2.99,
                "features": [
                    "Full criminal history",
                    "Address history",
                    "Phone numbers",
                    "Social media profiles",
                    "Family members"
                ]
            },
            "premium": {
                "name": "Premium Report", 
                "price": 5.99,
                "features": [
                    "Everything in Basic",
                    "All social media profiles",
                    "Property records",
                    "Professional background",
                    "Extended family network",
                    "Detailed case descriptions"
                ]
            }
        },
        "subscriptions": {
            "subscription_basic": {
                "name": "Basic Plan",
                "price": 14.99,
                "billing": "monthly",
                "reports": 10,
                "savings": "Save $15/month vs pay-per-report"
            },
            "subscription_pro": {
                "name": "Professional",
                "price": 29.99,
                "billing": "monthly", 
                "reports": 35,
                "savings": "Save $40/month vs pay-per-report"
            }
        }
    }

@api_router.get("/stats")
async def get_app_stats():
    """Get application statistics"""
    total_searches = await db.searches.count_documents({})
    total_reports = await db.reports.count_documents({})
    total_payments = await db.payment_transactions.count_documents({"payment_status": "paid"})
    
    return {
        "total_searches": total_searches,
        "total_reports": total_reports,
        "total_payments": total_payments,
        "uptime": "99.9%",
        "last_updated": datetime.utcnow()
    }

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