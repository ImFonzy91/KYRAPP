#!/usr/bin/env python3
"""
Scan'Em People Search App Backend Testing
Testing people search, background checks, and payment functionality
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        return "https://scanem-rights.preview.emergentagent.com"
    return "https://scanem-rights.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

class ScanEmAPITester:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results.append(result)
        print(result)
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def test_api_health(self):
        """Test basic API health endpoint"""
        try:
            response = requests.get(f"{API_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Health Check", True, f"API responding: {data.get('message', 'OK')}")
                return True
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_people_search_endpoints(self):
        """Test people search functionality"""
        # Test search by name
        search_tests = [
            ("/search/name", {"name": "John Smith"}),
            ("/search/phone", {"phone": "555-123-4567"}),
            ("/search/email", {"email": "john.smith@email.com"}),
            ("/search/address", {"address": "123 Main St, Anytown, CA"})
        ]
        
        for endpoint, params in search_tests:
            try:
                response = requests.get(f"{API_URL}{endpoint}", params=params, timeout=10)
                search_type = endpoint.split('/')[-1]
                
                if response.status_code == 200:
                    data = response.json()
                    if "results" in data:
                        self.log_test(f"People Search - {search_type.title()}", True, 
                                    f"Search endpoint working, returned {len(data.get('results', []))} results")
                    else:
                        self.log_test(f"People Search - {search_type.title()}", False, 
                                    "Response missing 'results' field")
                elif response.status_code == 404:
                    self.log_test(f"People Search - {search_type.title()}", False, 
                                "Search endpoint not found")
                else:
                    self.log_test(f"People Search - {search_type.title()}", False, 
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"People Search - {search_type.title()}", False, f"Error: {str(e)}")
    
    def test_background_report_generation(self):
        """Test background report generation"""
        try:
            # Test report generation endpoint
            response = requests.post(f"{API_URL}/report/generate", 
                                   json={"person_id": "test123", "report_type": "basic"}, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "report_id" in data:
                    self.log_test("Report Generation", True, "Report generation endpoint working")
                    
                    # Test report retrieval
                    report_id = data["report_id"]
                    report_response = requests.get(f"{API_URL}/report/{report_id}", timeout=10)
                    
                    if report_response.status_code == 200:
                        report_data = report_response.json()
                        expected_fields = ["criminal_history", "addresses", "relatives", "associates"]
                        has_expected_fields = any(field in report_data for field in expected_fields)
                        
                        if has_expected_fields:
                            self.log_test("Report Retrieval", True, "Report contains expected background data")
                        else:
                            self.log_test("Report Retrieval", False, "Report missing expected background fields")
                    else:
                        self.log_test("Report Retrieval", False, f"Status code: {report_response.status_code}")
                else:
                    self.log_test("Report Generation", False, "Response missing report_id")
            elif response.status_code == 404:
                self.log_test("Report Generation", False, "Report generation endpoint not found")
            else:
                self.log_test("Report Generation", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Report Generation", False, f"Error: {str(e)}")
    
    def test_pricing_structure(self):
        """Test pricing tiers and structure"""
        try:
            response = requests.get(f"{API_URL}/pricing", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "tiers" in data:
                    tiers = data["tiers"]
                    expected_tiers = ["free_preview", "pay_per_report", "subscription"]
                    
                    found_tiers = [tier.get("name", "") for tier in tiers]
                    has_expected_tiers = any(tier in str(found_tiers).lower() for tier in expected_tiers)
                    
                    if has_expected_tiers:
                        self.log_test("Pricing Structure", True, f"Found pricing tiers: {found_tiers}")
                    else:
                        self.log_test("Pricing Structure", False, f"Unexpected pricing structure: {found_tiers}")
                else:
                    self.log_test("Pricing Structure", False, "Response missing pricing tiers")
            elif response.status_code == 404:
                self.log_test("Pricing Structure", False, "Pricing endpoint not found")
            else:
                self.log_test("Pricing Structure", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Pricing Structure", False, f"Error: {str(e)}")
    
    def test_stripe_payment_integration(self):
        """Test Stripe checkout functionality"""
        try:
            # Test checkout session creation
            checkout_data = {
                "report_type": "basic",
                "person_id": "test123",
                "origin_url": BASE_URL
            }
            
            response = requests.post(f"{API_URL}/checkout/create", 
                                   json=checkout_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "checkout_url" in data and "session_id" in data:
                    self.log_test("Stripe Checkout Creation", True, "Checkout session created successfully")
                    
                    # Test checkout status check
                    session_id = data["session_id"]
                    status_response = requests.get(f"{API_URL}/checkout/status/{session_id}", timeout=10)
                    
                    if status_response.status_code == 200:
                        self.log_test("Stripe Checkout Status", True, "Checkout status endpoint working")
                    else:
                        self.log_test("Stripe Checkout Status", False, f"Status code: {status_response.status_code}")
                else:
                    self.log_test("Stripe Checkout Creation", False, "Response missing checkout_url or session_id")
            elif response.status_code == 404:
                self.log_test("Stripe Checkout Creation", False, "Checkout endpoint not found")
            else:
                self.log_test("Stripe Checkout Creation", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Stripe Checkout Creation", False, f"Error: {str(e)}")
    
    def test_sample_searches(self):
        """Test sample people searches with realistic data"""
        sample_searches = [
            ("John Smith", "name"),
            ("Jane Doe", "name"), 
            ("555-0123", "phone"),
            ("test@example.com", "email"),
            ("123 Main Street", "address")
        ]
        
        for search_term, search_type in sample_searches:
            try:
                if search_type == "name":
                    response = requests.get(f"{API_URL}/search", 
                                          params={"name": search_term}, timeout=10)
                elif search_type == "phone":
                    response = requests.get(f"{API_URL}/search", 
                                          params={"phone": search_term}, timeout=10)
                elif search_type == "email":
                    response = requests.get(f"{API_URL}/search", 
                                          params={"email": search_term}, timeout=10)
                elif search_type == "address":
                    response = requests.get(f"{API_URL}/search", 
                                          params={"address": search_term}, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if "results" in data:
                        result_count = len(data["results"])
                        self.log_test(f"Sample Search - {search_term}", True, 
                                    f"Search returned {result_count} results")
                    else:
                        self.log_test(f"Sample Search - {search_term}", False, 
                                    "Response missing results field")
                else:
                    self.log_test(f"Sample Search - {search_term}", False, 
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"Sample Search - {search_term}", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites for Scan'Em app"""
        print("=" * 60)
        print("SCAN'EM PEOPLE SEARCH APP - BACKEND API TESTING")
        print("=" * 60)
        print(f"Testing backend at: {BASE_URL}")
        print()
        
        # Test API connectivity first
        if not self.test_api_health():
            print("❌ CRITICAL: Cannot connect to API. Stopping tests.")
            return False
        
        print("\n🔍 Testing People Search Endpoints...")
        self.test_people_search_endpoints()
        
        print("\n📋 Testing Background Report Generation...")
        self.test_background_report_generation()
        
        print("\n💰 Testing Pricing Structure...")
        self.test_pricing_structure()
        
        print("\n💳 Testing Stripe Payment Integration...")
        self.test_stripe_payment_integration()
        
        print("\n🔍 Testing Sample Searches...")
        self.test_sample_searches()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        
        if self.passed_tests + self.failed_tests > 0:
            print(f"📊 Success Rate: {(self.passed_tests/(self.passed_tests + self.failed_tests)*100):.1f}%")
        
        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result:
                    print(f"  {result}")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = ScanEmAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Scan'Em backend is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {tester.failed_tests} tests failed. Check the issues above.")
        sys.exit(1)