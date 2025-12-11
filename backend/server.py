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
from datetime import datetime, timezone
from enum import Enum
from emergentintegrations.llm.chat import LlmChat, UserMessage
from legal_data import search_rights, ALL_RIGHTS_DATA, CONSTITUTIONAL_RIGHTS, MIRANDA_RIGHTS, TRAFFIC_STOP_RIGHTS, TENANT_RIGHTS, EMPLOYMENT_RIGHTS, CRIMINAL_DEFENSE_RIGHTS, IMMIGRATION_RIGHTS, CONSUMER_RIGHTS

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Know Your Rights API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API keys
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Models
class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class CaseAnalysisRequest(BaseModel):
    user_id: str
    situation: str

class BuyQueriesRequest(BaseModel):
    user_id: str
    package: str
    origin_url: str

class CartPurchaseRequest(BaseModel):
    user_id: str
    bundle_ids: List[str]
    origin_url: str

# Bundle pricing
BUNDLE_PRICES = {
    "single": 4.99,
    "all13": 10.00,  # All 13 bundles
    "premium": 20.00  # Lifetime unlimited + all updates
}

BUNDLE_INFO = {
    "traffic": {"name": "Traffic & Police Stops", "icon": "🚗"},
    "criminal": {"name": "Criminal Defense & Arrest", "icon": "⚖️"},
    "housing": {"name": "Housing & Tenant Rights", "icon": "🏠"},
    "workplace": {"name": "Workplace & Employment", "icon": "💼"},
    "property": {"name": "Property Rights", "icon": "🏡"},
    "landmines": {"name": "Legal Landmines", "icon": "💣"},
    "family": {"name": "Family Law Rights", "icon": "👨‍👩‍👧"},
    "divorce": {"name": "Divorce Rights", "icon": "💔"},
    "immigration": {"name": "Immigration Rights", "icon": "🌍"},
    "healthcare": {"name": "Healthcare Rights", "icon": "🏥"},
    "student": {"name": "Student Rights", "icon": "🎓"},
    "digital": {"name": "Digital & Privacy Rights", "icon": "📱"},
    "consumer": {"name": "Consumer & Debt Rights", "icon": "💳"},
}

# Auth Routes
@api_router.post("/auth/signup")
async def signup(user_data: UserCreate):
    """Create a new user account"""
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "password": user_data.password,  # In production, hash this!
        "name": user_data.name or user_data.email.split('@')[0],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "free_queries": 3,  # 3 free "Do I Have a Case?" queries
        "purchased_bundles": []
    }
    
    await db.users.insert_one(user)
    
    # Remove password from response
    del user['password']
    if '_id' in user:
        del user['_id']
    
    return {"user": user, "token": f"token_{user_id}"}

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    """Login user"""
    user = await db.users.find_one({"email": credentials.email})
    
    if not user or user.get('password') != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Remove sensitive data
    user_response = {
        "id": user['id'],
        "email": user['email'],
        "name": user.get('name', user['email'].split('@')[0]),
        "free_queries": user.get('free_queries', 3),
        "purchased_bundles": user.get('purchased_bundles', [])
    }
    
    return {"user": user_response, "token": f"token_{user['id']}"}

# Search Routes - REAL LEGAL DATA
@api_router.get("/search/rights")
async def search_rights_endpoint(query: str = Query(..., description="Search query")):
    """Search through real legal rights data"""
    results = search_rights(query)
    
    # If no keyword match, do a broader text search
    if not results:
        query_lower = query.lower()
        # Check all categories
        all_categories = [
            ("constitutional", CONSTITUTIONAL_RIGHTS),
            ("miranda", {"miranda": MIRANDA_RIGHTS}),
            ("traffic", {"traffic": TRAFFIC_STOP_RIGHTS}),
            ("tenant", {"tenant": TENANT_RIGHTS}),
            ("employment", {"employment": EMPLOYMENT_RIGHTS}),
            ("criminal", {"criminal": CRIMINAL_DEFENSE_RIGHTS}),
            ("immigration", {"immigration": IMMIGRATION_RIGHTS}),
            ("consumer", {"consumer": CONSUMER_RIGHTS})
        ]
        
        for cat_type, cat_data in all_categories:
            if isinstance(cat_data, dict):
                for key, data in cat_data.items():
                    if isinstance(data, dict):
                        title = data.get('title', '')
                        if query_lower in title.lower():
                            results.append({
                                "type": cat_type,
                                "id": key,
                                "title": title,
                                "source": data.get('source', 'U.S. Law'),
                                **data
                            })
    
    return {"query": query, "results": results}

# Get all rights categories
@api_router.get("/rights/categories")
async def get_rights_categories():
    """Get all available rights categories"""
    return {
        "categories": [
            {"id": "constitutional", "name": "Constitutional Rights", "icon": "🇺🇸", "source": "U.S. Constitution"},
            {"id": "miranda", "name": "Miranda Rights", "icon": "⚖️", "source": "Supreme Court"},
            {"id": "traffic", "name": "Traffic Stop Rights", "icon": "🚗", "source": "4th/5th/6th Amendments"},
            {"id": "tenant", "name": "Tenant Rights", "icon": "🏠", "source": "Fair Housing Act + State Laws"},
            {"id": "employment", "name": "Employment Rights", "icon": "💼", "source": "FLSA, Title VII, OSHA"},
            {"id": "criminal", "name": "Criminal Defense", "icon": "🔒", "source": "Bill of Rights"},
            {"id": "immigration", "name": "Immigration Rights", "icon": "🌍", "source": "Constitution + Federal Law"},
            {"id": "consumer", "name": "Consumer Rights", "icon": "💳", "source": "FDCPA, FCRA"}
        ]
    }

# Get specific rights category
@api_router.get("/rights/{category}")
async def get_rights_by_category(category: str):
    """Get all rights for a specific category"""
    category_map = {
        "constitutional": CONSTITUTIONAL_RIGHTS,
        "traffic": TRAFFIC_STOP_RIGHTS,
        "tenant": TENANT_RIGHTS,
        "employment": EMPLOYMENT_RIGHTS,
        "criminal": CRIMINAL_DEFENSE_RIGHTS,
        "immigration": IMMIGRATION_RIGHTS,
        "consumer": CONSUMER_RIGHTS
    }
    
    if category == "miranda":
        return {"category": "miranda", "data": MIRANDA_RIGHTS}
    
    if category not in category_map:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"category": category, "data": category_map[category]}

# User Bundles
@api_router.get("/user/bundles")
async def get_user_bundles(user_id: str = Query(...)):
    """Get user's purchased bundles"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        return {"bundles": []}
    
    return {"bundles": user.get('purchased_bundles', [])}

# Case Analyzer Routes
@api_router.get("/case-analyzer/queries-left")
async def get_queries_left(user_id: str = Query(...)):
    """Get remaining free queries for user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        return {"queries_left": 3, "history": []}
    
    # Get analysis history
    history = await db.case_analyses.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    return {
        "queries_left": user.get('free_queries', 3),
        "history": history
    }

@api_router.post("/case-analyzer/analyze")
async def analyze_case(request: CaseAnalysisRequest):
    """AI-powered legal situation analysis"""
    # Check user's remaining queries
    user = await db.users.find_one({"id": request.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    queries_left = user.get('free_queries', 0)
    if queries_left <= 0:
        raise HTTPException(status_code=402, detail="No queries remaining. Purchase more to continue.")
    
    # Use AI to analyze the situation
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"case_analysis_{request.user_id}_{uuid.uuid4()}",
            system_message="""You are a legal information assistant. You provide educational information about legal rights and situations. 
            
IMPORTANT: You are NOT providing legal advice. You are providing educational information about general legal principles.

When analyzing a situation, provide:
1. A clear verdict: "Likely Yes", "Possibly", "Unlikely", or "Need More Information"
2. A summary of the legal situation
3. Relevant laws that may apply (cite actual law names like "Fair Housing Act", "4th Amendment", etc.)
4. The person's likely rights in this situation
5. Recommended next steps
6. Whether it's worth consulting a lawyer and why

Be helpful but always remind them this is educational information, not legal advice."""
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(
            text=f"Analyze this legal situation and help me understand if I might have a case:\n\n{request.situation}"
        )
        
        response = await chat.send_message(user_message)
        
        # Parse AI response into structured format
        analysis = parse_ai_response(response, request.situation)
        
        # Decrement user's queries
        new_queries = queries_left - 1
        await db.users.update_one(
            {"id": request.user_id},
            {"$set": {"free_queries": new_queries}}
        )
        
        # Save analysis to history
        analysis_record = {
            "id": str(uuid.uuid4()),
            "user_id": request.user_id,
            "situation": request.situation,
            "analysis": analysis,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.case_analyses.insert_one(analysis_record)
        
        return {
            **analysis,
            "queries_left": new_queries
        }
        
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def parse_ai_response(response: str, situation: str) -> dict:
    """Parse AI response into structured format"""
    # Default structure
    analysis = {
        "has_case": False,
        "verdict": "Need More Information",
        "summary": response[:500] if len(response) > 500 else response,
        "relevant_laws": [],
        "your_rights": [],
        "next_steps": [],
        "lawyer_recommendation": "Consider consulting with a licensed attorney for personalized advice."
    }
    
    response_lower = response.lower()
    
    # Determine verdict
    if "likely yes" in response_lower or "strong case" in response_lower or "good case" in response_lower:
        analysis["has_case"] = True
        analysis["verdict"] = "Likely Yes - You May Have a Case"
    elif "possibly" in response_lower or "might have" in response_lower or "could have" in response_lower:
        analysis["has_case"] = True
        analysis["verdict"] = "Possibly - Worth Investigating"
    elif "unlikely" in response_lower or "probably not" in response_lower:
        analysis["verdict"] = "Unlikely - But Consult a Lawyer to Be Sure"
    
    # Extract common laws mentioned
    common_laws = [
        "4th Amendment", "5th Amendment", "6th Amendment", "14th Amendment",
        "Fair Housing Act", "FLSA", "Fair Labor Standards Act", "Title VII",
        "ADA", "Americans with Disabilities Act", "OSHA", "FMLA",
        "Fair Debt Collection Practices Act", "FDCPA", "FCRA",
        "Miranda", "due process", "equal protection"
    ]
    
    for law in common_laws:
        if law.lower() in response_lower:
            if law not in analysis["relevant_laws"]:
                analysis["relevant_laws"].append(law)
    
    # Default rights based on situation keywords
    situation_lower = situation.lower()
    if "landlord" in situation_lower or "tenant" in situation_lower or "rent" in situation_lower:
        analysis["your_rights"].extend([
            "Right to habitable living conditions",
            "Right to proper notice before eviction",
            "Right to security deposit return with itemization",
            "Protection from retaliation"
        ])
        if "Fair Housing Act" not in analysis["relevant_laws"]:
            analysis["relevant_laws"].append("Fair Housing Act")
    
    if "police" in situation_lower or "arrest" in situation_lower:
        analysis["your_rights"].extend([
            "Right to remain silent (5th Amendment)",
            "Right to an attorney (6th Amendment)",
            "Right against unreasonable search (4th Amendment)"
        ])
    
    if "work" in situation_lower or "boss" in situation_lower or "job" in situation_lower:
        analysis["your_rights"].extend([
            "Right to fair wages and overtime (FLSA)",
            "Right to safe workplace (OSHA)",
            "Protection from discrimination (Title VII)"
        ])
    
    # Default next steps
    analysis["next_steps"] = [
        "Document everything - save emails, texts, photos, receipts",
        "Write down dates, times, and details while fresh",
        "Gather any witnesses who can support your account",
        "Research your state's specific laws on this matter",
        "Consider a free consultation with a local attorney"
    ]
    
    # Lawyer recommendation
    if analysis["has_case"]:
        analysis["lawyer_recommendation"] = "Based on your situation, it would be worth scheduling a consultation with a lawyer. Many offer free initial consultations. The potential value of your case likely justifies the time investment."
    else:
        analysis["lawyer_recommendation"] = "While this situation may not have strong legal grounds, a brief consultation with a lawyer could provide clarity. Many offer free consultations and can give you definitive guidance."
    
    return analysis

# Buy more queries
@api_router.post("/case-analyzer/buy-queries")
async def buy_queries(request: BuyQueriesRequest):
    """Purchase more AI case analysis queries"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    # $3 for 5 queries
    price = 3.00
    queries_to_add = 5
    
    try:
        host_url = str(request.origin_url)
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        success_url = f"{request.origin_url}/?payment=success&type=queries"
        cancel_url = f"{request.origin_url}/?payment=cancelled"
        
        checkout_request = CheckoutSessionRequest(
            amount=price,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": request.user_id,
                "type": "queries",
                "queries_count": str(queries_to_add)
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id
        }
        
    except Exception as e:
        logger.error(f"Purchase error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Cart Purchase - Buy bundles
@api_router.post("/purchase/cart")
async def purchase_cart(request: CartPurchaseRequest):
    """Purchase bundles via Stripe checkout"""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    bundle_ids = request.bundle_ids
    
    # Calculate price
    if 'premium' in bundle_ids:
        price = BUNDLE_PRICES['premium']
        description = "PREMIUM UNLIMITED - All 13 Bundles + Lifetime Updates"
        bundle_ids = ['premium']
    elif 'all' in bundle_ids or len(bundle_ids) >= 13:
        price = BUNDLE_PRICES['all13']
        description = "All 13 Rights Bundles"
        bundle_ids = ['all']
    else:
        price = len(bundle_ids) * BUNDLE_PRICES['single']
        description = f"{len(bundle_ids)} Rights Bundle{'s' if len(bundle_ids) > 1 else ''}"
    
    try:
        host_url = str(request.origin_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        success_url = f"{request.origin_url}/?payment=success&type=bundles"
        cancel_url = f"{request.origin_url}/?payment=cancelled"
        
        checkout_request = CheckoutSessionRequest(
            amount=price,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": request.user_id,
                "type": "bundles",
                "bundle_ids": ",".join(bundle_ids),
                "description": description
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # For demo purposes, also add bundles immediately (in production, do this in webhook)
        if 'premium' in bundle_ids or 'all' in bundle_ids:
            all_bundle_ids = list(BUNDLE_INFO.keys())
        else:
            all_bundle_ids = bundle_ids
            
        bundles_to_add = [{"id": bid, **BUNDLE_INFO.get(bid, {"name": bid, "icon": "📦"})} for bid in all_bundle_ids]
        
        await db.users.update_one(
            {"id": request.user_id},
            {"$addToSet": {"purchased_bundles": {"$each": bundles_to_add}}}
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id,
            "price": price
        }
        
    except Exception as e:
        logger.error(f"Purchase error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Know Your Rights API"}

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
