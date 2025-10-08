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
    
    def test_search_functionality(self):
        """Test search functionality with various queries"""
        search_queries = [
            ("pulled over", ["traffic_pulled_over"]),
            ("eviction", ["housing_eviction"]),
            ("harassment", ["workplace_harassment"]),
            ("divorce", ["family_divorce_separation"]),
            ("social media", ["landmines_social_media"]),
            ("arrest", ["criminal_arrest_rights", "traffic_arrested"]),
            ("landlord", ["housing_eviction", "housing_landlord_entry", "housing_repairs_habitability"])
        ]
        
        for query, expected_results in search_queries:
            try:
                response = requests.get(f"{API_URL}/search", params={"query": query}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    found_ids = [result["id"] for result in results]
                    
                    # Check if at least one expected result is found
                    found_expected = any(expected_id in found_ids for expected_id in expected_results)
                    
                    if found_expected and len(results) > 0:
                        self.log_test(f"Search - '{query}'", True, 
                                    f"Found {len(results)} results including expected content")
                    else:
                        self.log_test(f"Search - '{query}'", False, 
                                    f"Expected results not found. Got: {found_ids}")
                else:
                    self.log_test(f"Search - '{query}'", False, 
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"Search - '{query}'", False, f"Error: {str(e)}")
    
    def test_bundle_completeness(self):
        """Test that all promised bundles have content"""
        bundle_tests = {
            "Traffic & Vehicle Rights": {
                "category": "traffic",
                "expected_entries": 6,
                "sample_ids": ["traffic_pulled_over", "traffic_search_car", "traffic_recording"]
            },
            "Housing Rights": {
                "category": "housing", 
                "expected_entries": 6,
                "sample_ids": ["housing_eviction", "housing_security_deposit", "housing_landlord_entry"]
            },
            "Legal Landmines": {
                "category": "landmines",
                "expected_entries": 6, 
                "sample_ids": ["landmines_social_media", "landmines_neighbor_disputes", "landmines_dating_relationships"]
            },
            "Criminal Defense Rights": {
                "category": "criminal",
                "expected_entries": 4,
                "sample_ids": ["criminal_arrest_rights", "criminal_court_procedures", "criminal_bail_bonds"]
            },
            "Business & Workplace Rights": {
                "category": "workplace",
                "expected_entries": 3,
                "sample_ids": ["workplace_harassment", "workplace_firing_layoffs", "workplace_wages_hours"]
            },
            "Family & Personal Rights": {
                "category": "family",
                "expected_entries": 2,
                "sample_ids": ["family_divorce_separation", "family_child_custody"]
            }
        }
        
        for bundle_name, test_info in bundle_tests.items():
            category = test_info["category"]
            expected_count = test_info["expected_entries"]
            sample_ids = test_info["sample_ids"]
            
            # Test category has expected number of entries
            try:
                response = requests.get(f"{API_URL}/rights/{category}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    rights = data.get("rights", [])
                    
                    if len(rights) >= expected_count:
                        self.log_test(f"Bundle Completeness - {bundle_name}", True, 
                                    f"Has {len(rights)} entries (expected {expected_count})")
                    else:
                        self.log_test(f"Bundle Completeness - {bundle_name}", False, 
                                    f"Only {len(rights)} entries (expected {expected_count})")
                    
                    # Test sample content exists
                    found_ids = [right["id"] for right in rights]
                    missing_samples = [sid for sid in sample_ids if sid not in found_ids]
                    
                    if not missing_samples:
                        self.log_test(f"Sample Content - {bundle_name}", True, 
                                    "All sample content found")
                    else:
                        self.log_test(f"Sample Content - {bundle_name}", False, 
                                    f"Missing: {missing_samples}")
                else:
                    self.log_test(f"Bundle Access - {bundle_name}", False, 
                                f"Cannot access category: {response.status_code}")
            except Exception as e:
                self.log_test(f"Bundle Test - {bundle_name}", False, f"Error: {str(e)}")
    
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