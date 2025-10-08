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
from datetime import datetime, date
from enum import Enum
import random
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
class SearchType(str, Enum):
    NAME = "name"
    PHONE = "phone"
    EMAIL = "email"
    ADDRESS = "address"

class ReportType(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    COMPREHENSIVE = "comprehensive"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    EXPIRED = "expired"

# Models
class PersonRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    age: Optional[int] = None
    current_address: Optional[str] = None
    phone_numbers: List[str] = []
    email_addresses: List[str] = []
    known_addresses: List[str] = []
    criminal_history: List[Dict[str, Any]] = []
    relatives: List[Dict[str, Any]] = []
    associates: List[Dict[str, Any]] = []
    social_media: List[Dict[str, Any]] = []
    confidence_score: float = 0.0

class SearchRequest(BaseModel):
    search_type: SearchType
    query: str
    state: Optional[str] = None
    city: Optional[str] = None

class ReportRequest(BaseModel):
    person_id: str
    report_type: ReportType
    origin_url: str

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    amount: float
    currency: str = "usd"
    payment_status: PaymentStatus
    report_type: ReportType
    person_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Initialize Stripe
stripe_api_key = os.environ.get('STRIPE_API_KEY')

# Mock Database - Realistic People Data
MOCK_PEOPLE_DATABASE = [
    PersonRecord(
        id="person_001",
        first_name="John",
        last_name="Smith", 
        age=34,
        current_address="1245 Oak Street, Springfield, IL 62701",
        phone_numbers=["555-123-4567", "555-987-6543"],
        email_addresses=["john.smith@email.com", "j.smith@company.com"],
        known_addresses=[
            "1245 Oak Street, Springfield, IL 62701",
            "892 Pine Avenue, Chicago, IL 60601",
            "567 Elm Street, Peoria, IL 61601"
        ],
        criminal_history=[
            {
                "date": "2018-03-15",
                "charge": "Speeding Violation",
                "disposition": "Paid Fine",
                "location": "Springfield, IL",
                "case_number": "TR-2018-001234"
            }
        ],
        relatives=[
            {"name": "Mary Smith", "relationship": "Spouse", "age": 32},
            {"name": "Robert Smith", "relationship": "Father", "age": 67},
            {"name": "Susan Johnson", "relationship": "Mother", "age": 64}
        ],
        associates=[
            {"name": "Michael Davis", "relationship": "Colleague"},
            {"name": "Jennifer Wilson", "relationship": "Neighbor"}
        ],
        social_media=[
            {"platform": "Facebook", "username": "john.smith.il", "verified": True},
            {"platform": "LinkedIn", "username": "johnsmith-professional", "verified": True}
        ],
        confidence_score=0.95
    ),
    PersonRecord(
        id="person_002", 
        first_name="Sarah",
        last_name="Johnson",
        age=28,
        current_address="789 Maple Drive, Austin, TX 73301",
        phone_numbers=["512-555-7890"],
        email_addresses=["sarah.johnson@gmail.com"],
        known_addresses=[
            "789 Maple Drive, Austin, TX 73301",
            "123 College Street, Austin, TX 78705"
        ],
        criminal_history=[],
        relatives=[
            {"name": "David Johnson", "relationship": "Father", "age": 55},
            {"name": "Lisa Johnson", "relationship": "Mother", "age": 53},
            {"name": "Kevin Johnson", "relationship": "Brother", "age": 25}
        ],
        associates=[
            {"name": "Amanda Rodriguez", "relationship": "Friend"},
            {"name": "Tyler Chen", "relationship": "Coworker"}
        ],
        social_media=[
            {"platform": "Instagram", "username": "sarahj_austin", "verified": False},
            {"platform": "Twitter", "username": "sjohnson_tx", "verified": False}
        ],
        confidence_score=0.88
    ),
    PersonRecord(
        id="person_003",
        first_name="Michael",
        last_name="Davis",
        age=41,
        current_address="456 Broadway, New York, NY 10013",
        phone_numbers=["212-555-0123", "917-555-4567"],
        email_addresses=["mdavis@company.com", "mike.davis.nyc@gmail.com"],
        known_addresses=[
            "456 Broadway, New York, NY 10013", 
            "789 West End Avenue, New York, NY 10025",
            "234 Main Street, Albany, NY 12203"
        ],
        criminal_history=[
            {
                "date": "2015-08-22",
                "charge": "Public Intoxication", 
                "disposition": "Community Service",
                "location": "New York, NY",
                "case_number": "CR-2015-005678"
            },
            {
                "date": "2020-12-10",
                "charge": "Parking Violations (Multiple)",
                "disposition": "Fines Paid",
                "location": "New York, NY", 
                "case_number": "TR-2020-009876"
            }
        ],
        relatives=[
            {"name": "Rachel Davis", "relationship": "Spouse", "age": 38},
            {"name": "Emma Davis", "relationship": "Daughter", "age": 12},
            {"name": "James Davis", "relationship": "Son", "age": 9}
        ],
        associates=[
            {"name": "John Smith", "relationship": "Business Partner"},
            {"name": "Carlos Rodriguez", "relationship": "Neighbor"}
        ],
        social_media=[
            {"platform": "LinkedIn", "username": "michael-davis-nyc", "verified": True},
            {"platform": "Facebook", "username": "mike.davis.ny", "verified": False}
        ],
        confidence_score=0.92
    ),
    PersonRecord(
        id="person_004",
        first_name="Jennifer",
        last_name="Wilson",
        age=35,
        current_address="321 Sunset Boulevard, Los Angeles, CA 90028",
        phone_numbers=["323-555-2468"],
        email_addresses=["jennifer.wilson@studio.com"],
        known_addresses=[
            "321 Sunset Boulevard, Los Angeles, CA 90028",
            "987 Hollywood Hills Drive, Los Angeles, CA 90069"
        ],
        criminal_history=[
            {
                "date": "2019-06-05",
                "charge": "Reckless Driving",
                "disposition": "License Suspended 6 months",
                "location": "Los Angeles, CA",
                "case_number": "TR-2019-112233"
            }
        ],
        relatives=[
            {"name": "Patricia Wilson", "relationship": "Mother", "age": 62},
            {"name": "Thomas Wilson", "relationship": "Father", "age": 65},
            {"name": "Ashley Wilson", "relationship": "Sister", "age": 32}
        ],
        associates=[
            {"name": "Maria Garcia", "relationship": "Colleague"},
            {"name": "Brandon Lee", "relationship": "Friend"}
        ],
        social_media=[
            {"platform": "Instagram", "username": "jenwilson_la", "verified": True},
            {"platform": "TikTok", "username": "jennywilsonofficial", "verified": False}
        ],
        confidence_score=0.87
    ),
    PersonRecord(
        id="person_005",
        first_name="David",
        last_name="Brown",
        age=52,
        current_address="654 Pine Street, Seattle, WA 98101",
        phone_numbers=["206-555-8901", "425-555-3456"],
        email_addresses=["david.brown@tech.com", "d.brown.seattle@yahoo.com"],
        known_addresses=[
            "654 Pine Street, Seattle, WA 98101",
            "111 Capitol Hill, Seattle, WA 98102",
            "222 Queen Anne Avenue, Seattle, WA 98109"
        ],
        criminal_history=[
            {
                "date": "2012-11-18",
                "charge": "DUI - First Offense",
                "disposition": "Fines, License Suspended 90 days",
                "location": "Seattle, WA",
                "case_number": "CR-2012-445566"
            },
            {
                "date": "2016-04-03", 
                "charge": "Failure to Appear",
                "disposition": "Warrant Cleared",
                "location": "Seattle, WA",
                "case_number": "CR-2016-778899"
            }
        ],
        relatives=[
            {"name": "Karen Brown", "relationship": "Ex-Spouse", "age": 48},
            {"name": "Nathan Brown", "relationship": "Son", "age": 22},
            {"name": "Melissa Brown", "relationship": "Daughter", "age": 19}
        ],
        associates=[
            {"name": "Steven Clark", "relationship": "Business Associate"},
            {"name": "Rebecca Martinez", "relationship": "Friend"}
        ],
        social_media=[
            {"platform": "LinkedIn", "username": "david-brown-seattle-tech", "verified": True},
            {"platform": "Facebook", "username": "dave.brown.wa", "verified": False}
        ],
        confidence_score=0.91
    )
]

# Pricing Structure
PRICING_TIERS = {
    ReportType.BASIC: {
        "price": 4.99,
        "name": "Basic Report",
        "description": "Name, age, current address, phone numbers",
        "includes": ["basic_info", "contact_info", "current_address"]
    },
    ReportType.PREMIUM: {
        "price": 19.99, 
        "name": "Premium Report",
        "description": "Everything in Basic + Criminal History + Previous Addresses",
        "includes": ["basic_info", "contact_info", "current_address", "criminal_history", "address_history"]
    },
    ReportType.COMPREHENSIVE: {
        "price": 39.99,
        "name": "Comprehensive Report", 
        "description": "Everything + Relatives + Associates + Social Media Profiles",
        "includes": ["basic_info", "contact_info", "current_address", "criminal_history", "address_history", "relatives", "associates", "social_media"]
    }
}

# Helper Functions
def search_people_by_name(query: str, limit: int = 10) -> List[PersonRecord]:
    """Search people by name"""
    query = query.lower().strip()
    results = []
    
    for person in MOCK_PEOPLE_DATABASE:
        full_name = f"{person.first_name} {person.last_name}".lower()
        if query in full_name or full_name.startswith(query):
            results.append(person)
    
    # Add some randomized results for demo purposes
    if len(results) < 3:
        additional_names = [
            ("James", "Miller"), ("Lisa", "Anderson"), ("Robert", "Taylor"),
            ("Maria", "Garcia"), ("Christopher", "Martinez"), ("Jessica", "Robinson")
        ]
        for first, last in additional_names[:3-len(results)]:
            if query.lower() in f"{first} {last}".lower():
                mock_person = PersonRecord(
                    first_name=first,
                    last_name=last,
                    age=random.randint(25, 65),
                    current_address=f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm'])} Street, {random.choice(['Springfield', 'Austin', 'Denver'])}, {random.choice(['IL', 'TX', 'CO'])} {random.randint(10000, 99999)}",
                    phone_numbers=[f"{random.randint(100, 999)}-555-{random.randint(1000, 9999)}"],
                    confidence_score=random.uniform(0.7, 0.95)
                )
                results.append(mock_person)
    
    return results[:limit]

def search_people_by_phone(query: str) -> List[PersonRecord]:
    """Search people by phone number"""
    results = []
    for person in MOCK_PEOPLE_DATABASE:
        for phone in person.phone_numbers:
            if query in phone.replace("-", "").replace("(", "").replace(")", "").replace(" ", ""):
                results.append(person)
                break
    return results

def search_people_by_email(query: str) -> List[PersonRecord]:
    """Search people by email"""
    results = []
    query = query.lower()
    for person in MOCK_PEOPLE_DATABASE:
        for email in person.email_addresses:
            if query in email.lower():
                results.append(person)
                break
    return results

def search_people_by_address(query: str) -> List[PersonRecord]:
    """Search people by address"""
    results = []
    query = query.lower()
    for person in MOCK_PEOPLE_DATABASE:
        # Check current address
        if query in person.current_address.lower():
            results.append(person)
        else:
            # Check known addresses
            for address in person.known_addresses:
                if query in address.lower():
                    results.append(person)
                    break
    return results

def filter_report_data(person: PersonRecord, report_type: ReportType) -> Dict[str, Any]:
    """Filter person data based on report type"""
    includes = PRICING_TIERS[report_type]["includes"]
    
    result = {
        "person_id": person.id,
        "report_type": report_type.value,
        "generated_at": datetime.utcnow().isoformat(),
    }
    
    if "basic_info" in includes:
        result.update({
            "first_name": person.first_name,
            "last_name": person.last_name,
            "age": person.age,
            "confidence_score": person.confidence_score
        })
    
    if "contact_info" in includes:
        result.update({
            "phone_numbers": person.phone_numbers,
            "email_addresses": person.email_addresses
        })
    
    if "current_address" in includes:
        result["current_address"] = person.current_address
    
    if "address_history" in includes:
        result["known_addresses"] = person.known_addresses
    
    if "criminal_history" in includes:
        result["criminal_history"] = person.criminal_history
    
    if "relatives" in includes:
        result["relatives"] = person.relatives
    
    if "associates" in includes:
        result["associates"] = person.associates
    
    if "social_media" in includes:
        result["social_media"] = person.social_media
    
    return result

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Scan'Em API - Smart Background Checks", "status": "active", "version": "1.0"}

@api_router.get("/search")
async def search_people(
    name: str = Query(None, description="Search by full name"),
    phone: str = Query(None, description="Search by phone number"),
    email: str = Query(None, description="Search by email address"),
    address: str = Query(None, description="Search by address"),
    limit: int = Query(10, description="Maximum number of results")
):
    """Search for people by various criteria"""
    
    if name:
        results = search_people_by_name(name, limit)
        search_type = "name"
        query = name
    elif phone:
        results = search_people_by_phone(phone)
        search_type = "phone"
        query = phone
    elif email:
        results = search_people_by_email(email)
        search_type = "email"
        query = email
    elif address:
        results = search_people_by_address(address)
        search_type = "address"
        query = address
    else:
        raise HTTPException(status_code=400, detail="Please provide at least one search parameter")
    
    # Return search preview (basic info only)
    search_results = []
    for person in results:
        search_results.append({
            "person_id": person.id,
            "first_name": person.first_name,
            "last_name": person.last_name,
            "age": person.age,
            "current_city": person.current_address.split(", ")[-2] if person.current_address else None,
            "state": person.current_address.split(", ")[-1].split(" ")[0] if person.current_address else None,
            "confidence_score": person.confidence_score,
            "has_criminal_history": len(person.criminal_history) > 0,
            "preview": True
        })
    
    return {
        "search_type": search_type,
        "query": query,
        "total_results": len(search_results),
        "results": search_results
    }

@api_router.get("/person/{person_id}")
async def get_person_preview(person_id: str):
    """Get basic person information (preview)"""
    
    person = None
    for p in MOCK_PEOPLE_DATABASE:
        if p.id == person_id:
            person = p
            break
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return {
        "person_id": person.id,
        "first_name": person.first_name,
        "last_name": person.last_name,
        "age": person.age,
        "current_city": person.current_address.split(", ")[-2] if person.current_address else None,
        "state": person.current_address.split(", ")[-1].split(" ")[0] if person.current_address else None,
        "phone_count": len(person.phone_numbers),
        "email_count": len(person.email_addresses), 
        "address_count": len(person.known_addresses),
        "criminal_records": len(person.criminal_history),
        "relatives_count": len(person.relatives),
        "associates_count": len(person.associates),
        "confidence_score": person.confidence_score,
        "preview_only": True,
        "available_reports": list(PRICING_TIERS.keys())
    }

@api_router.get("/pricing")
async def get_pricing():
    """Get pricing information for different report types"""
    return {
        "pricing_tiers": PRICING_TIERS,
        "currency": "USD",
        "free_preview": "Basic information preview available for all searches"
    }

@api_router.post("/report/purchase")
async def purchase_report(request: ReportRequest):
    """Purchase a background check report"""
    
    # Find the person
    person = None
    for p in MOCK_PEOPLE_DATABASE:
        if p.id == request.person_id:
            person = p
            break
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Get pricing info
    if request.report_type not in PRICING_TIERS:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    price_info = PRICING_TIERS[request.report_type]
    
    try:
        # Initialize Stripe checkout
        host_url = str(request.origin_url)
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        # Build success and cancel URLs  
        success_url = f"{request.origin_url}/report-success?session_id={{CHECKOUT_SESSION_ID}}&person_id={request.person_id}&report_type={request.report_type}"
        cancel_url = f"{request.origin_url}/search"
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=price_info["price"],
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "person_id": request.person_id,
                "report_type": request.report_type.value,
                "source": "scanem_app"
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction = PaymentTransaction(
            session_id=session.session_id,
            amount=price_info["price"],
            payment_status=PaymentStatus.PENDING,
            report_type=request.report_type,
            person_id=request.person_id
        )
        
        await db.scanem_transactions.insert_one(transaction.dict())
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id,
            "report_type": request.report_type,
            "person_name": f"{person.first_name} {person.last_name}",
            "amount": price_info["price"]
        }
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Purchase error: {e}")
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")

@api_router.get("/report/{session_id}")
async def get_report(session_id: str):
    """Get purchased report by session ID"""
    
    # Find transaction
    transaction = await db.scanem_transactions.find_one({"session_id": session_id})
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if transaction["payment_status"] != PaymentStatus.PAID.value:
        raise HTTPException(status_code=402, detail="Payment required")
    
    # Find the person
    person = None
    for p in MOCK_PEOPLE_DATABASE:
        if p.id == transaction["person_id"]:
            person = p
            break
    
    if not person:
        raise HTTPException(status_code=404, detail="Person data not found")
    
    # Generate filtered report based on purchased type
    report_type = ReportType(transaction["report_type"])
    report_data = filter_report_data(person, report_type)
    
    return {
        "session_id": session_id,
        "purchase_date": transaction["created_at"],
        "report_data": report_data,
        "pricing_tier": PRICING_TIERS[report_type]
    }

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str):
    """Check payment status"""
    
    transaction = await db.scanem_transactions.find_one({"session_id": session_id})
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # In a real app, you'd check with Stripe here
    # For demo, we'll simulate payment completion after 5 seconds
    
    return {
        "session_id": session_id,
        "payment_status": transaction["payment_status"],
        "report_type": transaction["report_type"],
        "person_id": transaction["person_id"],
        "amount": transaction["amount"]
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