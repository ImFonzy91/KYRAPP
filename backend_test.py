#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Scan'Em People Search App
Tests all implemented people search and background check endpoints
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
    
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{API_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "Scan'Em API" in data.get("message", ""):
                    self.log_test("API Root Endpoint", True, "Scan'Em API is responding correctly")
                    return True
                else:
                    self.log_test("API Root Endpoint", False, f"Unexpected message: {data}")
                    return False
            else:
                self.log_test("API Root Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Connection error: {str(e)}")
            return False
    
    def test_pricing_structure(self):
        """Test pricing endpoint - should return 3 tiers"""
        try:
            response = requests.get(f"{API_URL}/pricing", timeout=10)
            if response.status_code == 200:
                data = response.json()
                pricing_tiers = data.get("pricing_tiers", {})
                
                # Expected tiers
                expected_tiers = ["basic", "premium", "comprehensive"]
                expected_prices = {"basic": 4.99, "premium": 19.99, "comprehensive": 39.99}
                
                if len(pricing_tiers) == 3:
                    self.log_test("Pricing Tiers Count", True, f"Found all 3 pricing tiers")
                else:
                    self.log_test("Pricing Tiers Count", False, f"Expected 3, got {len(pricing_tiers)}")
                
                # Check each expected tier exists with correct pricing
                for tier in expected_tiers:
                    if tier in pricing_tiers:
                        actual_price = pricing_tiers[tier].get("price")
                        expected_price = expected_prices[tier]
                        if actual_price == expected_price:
                            self.log_test(f"Pricing - {tier.title()}", True, f"${actual_price} correct")
                        else:
                            self.log_test(f"Pricing - {tier.title()}", False, f"Expected ${expected_price}, got ${actual_price}")
                    else:
                        self.log_test(f"Pricing - {tier.title()}", False, "Tier missing")
                
                # Check structure
                if pricing_tiers:
                    first_tier = list(pricing_tiers.values())[0]
                    required_fields = ["price", "name", "description", "includes"]
                    has_all_fields = all(field in first_tier for field in required_fields)
                    
                    if has_all_fields:
                        self.log_test("Pricing Structure", True, "Pricing tiers have correct structure")
                    else:
                        self.log_test("Pricing Structure", False, "Pricing tiers missing required fields")
                
                return True
            else:
                self.log_test("Pricing API", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Pricing API", False, f"Error: {str(e)}")
            return False
    
    def test_people_search(self):
        """Test people search functionality with various parameters"""
        search_tests = [
            # Name searches
            {"params": {"name": "John Smith"}, "expected_person": "person_001", "test_name": "Search by Name - John Smith"},
            {"params": {"name": "Sarah Johnson"}, "expected_person": "person_002", "test_name": "Search by Name - Sarah Johnson"},
            
            # Phone searches  
            {"params": {"phone": "555-123-4567"}, "expected_person": "person_001", "test_name": "Search by Phone - John Smith"},
            {"params": {"phone": "555-987-6543"}, "expected_person": "person_002", "test_name": "Search by Phone - Sarah Johnson"},
            
            # Email searches
            {"params": {"email": "john.smith@email.com"}, "expected_person": "person_001", "test_name": "Search by Email - John Smith"},
            {"params": {"email": "sarah.johnson@email.com"}, "expected_person": "person_002", "test_name": "Search by Email - Sarah Johnson"},
            
            # Address searches
            {"params": {"address": "123 Main St, Springfield, IL"}, "expected_person": "person_001", "test_name": "Search by Address - John Smith"},
        ]
        
        for test_case in search_tests:
            try:
                response = requests.get(f"{API_URL}/search", params=test_case["params"], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    if results and len(results) > 0:
                        found_person = results[0].get("person_id")
                        if found_person == test_case["expected_person"]:
                            self.log_test(test_case["test_name"], True, 
                                        f"Found {found_person} with confidence {results[0].get('confidence_score', 0)}")
                        else:
                            self.log_test(test_case["test_name"], False, 
                                        f"Expected {test_case['expected_person']}, got {found_person}")
                        
                        # Check result structure
                        first_result = results[0]
                        required_fields = ["person_id", "first_name", "last_name", "confidence_score"]
                        has_all_fields = all(field in first_result for field in required_fields)
                        
                        if has_all_fields:
                            self.log_test(f"Search Result Structure - {test_case['test_name']}", True, 
                                        "Results have correct structure")
                        else:
                            self.log_test(f"Search Result Structure - {test_case['test_name']}", False, 
                                        "Results missing required fields")
                    else:
                        self.log_test(test_case["test_name"], False, "No results returned")
                else:
                    self.log_test(test_case["test_name"], False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(test_case["test_name"], False, f"Error: {str(e)}")
    
    def test_person_preview(self):
        """Test person preview endpoint for detailed information"""
        test_persons = [
            {"person_id": "person_001", "name": "John Smith", "should_have_criminal": True},
            {"person_id": "person_002", "name": "Sarah Johnson", "should_have_criminal": False},
            {"person_id": "person_003", "name": "Michael Brown", "should_have_criminal": False},
            {"person_id": "person_004", "name": "Emily Davis", "should_have_criminal": False},
            {"person_id": "person_005", "name": "David Wilson", "should_have_criminal": True}
        ]
        
        for test_person in test_persons:
            try:
                response = requests.get(f"{API_URL}/person/{test_person['person_id']}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required fields
                    required_fields = ["person_id", "first_name", "last_name", "age", "current_city", 
                                     "state", "confidence_score", "preview_only", "available_reports"]
                    has_all_fields = all(field in data for field in required_fields)
                    
                    if has_all_fields:
                        self.log_test(f"Person Preview Structure - {test_person['name']}", True, 
                                    "Preview has all required fields")
                    else:
                        missing_fields = [field for field in required_fields if field not in data]
                        self.log_test(f"Person Preview Structure - {test_person['name']}", False, 
                                    f"Missing fields: {missing_fields}")
                    
                    # Check criminal history indication
                    criminal_records = data.get("criminal_records", 0)
                    if test_person["should_have_criminal"]:
                        if criminal_records > 0:
                            self.log_test(f"Criminal History - {test_person['name']}", True, 
                                        f"Has {criminal_records} criminal record(s) as expected")
                        else:
                            self.log_test(f"Criminal History - {test_person['name']}", False, 
                                        "Expected criminal history but none found")
                    else:
                        if criminal_records == 0:
                            self.log_test(f"Clean Record - {test_person['name']}", True, 
                                        "Clean record as expected")
                        else:
                            self.log_test(f"Clean Record - {test_person['name']}", False, 
                                        f"Expected clean record but found {criminal_records} record(s)")
                    
                    # Check available reports
                    available_reports = data.get("available_reports", [])
                    expected_reports = ["basic", "premium", "comprehensive"]
                    if set(available_reports) == set(expected_reports):
                        self.log_test(f"Available Reports - {test_person['name']}", True, 
                                    "All report types available")
                    else:
                        self.log_test(f"Available Reports - {test_person['name']}", False, 
                                    f"Expected {expected_reports}, got {available_reports}")
                        
                elif response.status_code == 404:
                    self.log_test(f"Person Preview - {test_person['name']}", False, "Person not found")
                else:
                    self.log_test(f"Person Preview - {test_person['name']}", False, 
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"Person Preview - {test_person['name']}", False, f"Error: {str(e)}")
    
    def test_stripe_integration(self):
        """Test Stripe payment integration endpoints"""
        try:
            # Test report purchase endpoint (should create checkout session)
            purchase_data = {
                "person_id": "person_001",
                "report_type": "premium",
                "origin_url": "https://scanem-rights.preview.emergentagent.com"
            }
            
            response = requests.post(f"{API_URL}/report/purchase", 
                                   json=purchase_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["checkout_url", "session_id"]
                has_all_fields = all(field in data for field in required_fields)
                
                if has_all_fields:
                    session_id = data["session_id"]
                    checkout_url = data["checkout_url"]
                    
                    # Verify checkout URL format
                    if "checkout.stripe.com" in checkout_url:
                        self.log_test("Stripe Checkout Creation", True, 
                                    f"Checkout session created: {session_id}")
                        
                        # Test payment status endpoint
                        status_response = requests.get(f"{API_URL}/payments/status/{session_id}", timeout=10)
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            if "payment_status" in status_data:
                                self.log_test("Payment Status Check", True, 
                                            f"Status: {status_data['payment_status']}")
                            else:
                                self.log_test("Payment Status Check", False, 
                                            "Payment status field missing")
                        else:
                            self.log_test("Payment Status Check", False, 
                                        f"Status code: {status_response.status_code}")
                    else:
                        self.log_test("Stripe Checkout Creation", False, 
                                    "Invalid checkout URL format")
                else:
                    self.log_test("Stripe Checkout Creation", False, 
                                "Missing required fields in response")
            else:
                self.log_test("Stripe Checkout Creation", False, 
                            f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Stripe Integration", False, f"Error: {str(e)}")
    
    def test_report_retrieval(self):
        """Test report retrieval endpoint (mock data)"""
        # Test with a mock session ID that should return sample report data
        mock_session_id = "cs_test_mock_session_123"
        
        try:
            response = requests.get(f"{API_URL}/report/{mock_session_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Check if it's a complete report structure
                required_fields = ["person_id", "report_type", "generated_at", "data"]
                has_all_fields = all(field in data for field in required_fields)
                
                if has_all_fields:
                    report_data = data.get("data", {})
                    
                    # Check report data structure based on type
                    if "basic_info" in report_data:
                        self.log_test("Report Retrieval - Structure", True, 
                                    "Report has correct data structure")
                        
                        # Check if comprehensive report has all sections
                        if data.get("report_type") == "comprehensive":
                            expected_sections = ["basic_info", "contact_info", "address_history", 
                                               "criminal_history", "relatives", "associates"]
                            has_all_sections = all(section in report_data for section in expected_sections)
                            
                            if has_all_sections:
                                self.log_test("Report Retrieval - Comprehensive Data", True, 
                                            "All report sections present")
                            else:
                                missing_sections = [s for s in expected_sections if s not in report_data]
                                self.log_test("Report Retrieval - Comprehensive Data", False, 
                                            f"Missing sections: {missing_sections}")
                        else:
                            self.log_test("Report Retrieval - Basic Data", True, 
                                        "Basic report data structure correct")
                    else:
                        self.log_test("Report Retrieval - Structure", False, 
                                    "Report missing basic_info section")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Report Retrieval - Structure", False, 
                                f"Missing fields: {missing_fields}")
                    
            elif response.status_code == 404:
                self.log_test("Report Retrieval - Not Found", True, 
                            "Correctly returns 404 for non-existent session")
            else:
                self.log_test("Report Retrieval", False, 
                            f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Report Retrieval", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 60)
        print("KNOW YOUR RIGHTS APP - BACKEND API TESTING")
        print("=" * 60)
        print(f"Testing backend at: {BASE_URL}")
        print()
        
        # Test API connectivity first
        if not self.test_api_root():
            print("❌ CRITICAL: Cannot connect to API. Stopping tests.")
            return False
        
        print("\n🔍 Testing Categories API...")
        self.test_categories_api()
        
        print("\n📋 Testing Rights by Category...")
        self.test_rights_by_category()
        
        print("\n📄 Testing Specific Content...")
        self.test_specific_content()
        
        print("\n🔍 Testing Search Functionality...")
        self.test_search_functionality()
        
        print("\n📦 Testing Bundle Completeness...")
        self.test_bundle_completeness()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📊 Success Rate: {(self.passed_tests/(self.passed_tests + self.failed_tests)*100):.1f}%")
        
        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result:
                    print(f"  {result}")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = KnowYourRightsAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Backend is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {tester.failed_tests} tests failed. Check the issues above.")
        sys.exit(1)