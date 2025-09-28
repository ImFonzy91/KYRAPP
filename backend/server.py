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
import json
from enum import Enum


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
    date: date
    status: CaseStatus
    status_description: str
    court: str
    county: str
    state: str

class PropertyRecord(BaseModel):
    address: str
    property_type: str
    estimated_value: Optional[int] = None
    ownership_date: Optional[date] = None
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
                    date=date(2023, 6, 15),
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
                    date=date(2023, 8, 20),
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
                    date=date(2023, 8, 20),
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
                    date=date(2021, 3, 10),
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
                    ownership_date=date(2020, 5, 15),
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
    return {"message": "PeopleCheck API - Background Checks Made Simple"}

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
    """Get a detailed background report"""
    
    # Generate mock report based on tier
    report = generate_mock_report("John Smith", tier)
    
    # Save report generation
    await db.reports.insert_one(report.dict())
    
    return report

@api_router.get("/pricing")
async def get_pricing():
    """Get current pricing information"""
    return {
        "free_tier": {
            "name": "Free Daily Check",
            "price": 0,
            "searches_per_day": 1,
            "features": [
                "Basic name and age",
                "Current city",
                "One criminal record preview",
                "Limited social media hints"
            ]
        },
        "pay_per_report": {
            "basic": {
                "name": "Basic Report",
                "price": 2.99,
                "features": [
                    "Full criminal history",
                    "Address history", 
                    "Phone numbers",
                    "2 social media profiles",
                    "Immediate family"
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
            "basic": {
                "name": "Basic Plan",
                "price": 14.99,
                "billing": "monthly",
                "reports": 10,
                "savings": "Save $15/month vs pay-per-report"
            },
            "professional": {
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
    
    return {
        "total_searches": total_searches,
        "total_reports": total_reports,
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