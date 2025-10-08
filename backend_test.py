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
    
    def test_rights_by_category(self):
        """Test rights by category for implemented bundles"""
        implemented_categories = ["traffic", "housing", "landmines", "criminal", "workplace", "family"]
        
        for category in implemented_categories:
            try:
                response = requests.get(f"{API_URL}/rights/{category}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    rights = data.get("rights", [])
                    
                    # Expected counts based on implementation
                    expected_counts = {
                        "traffic": 6,
                        "housing": 6, 
                        "landmines": 6,
                        "criminal": 4,
                        "workplace": 3,
                        "family": 2
                    }
                    
                    expected_count = expected_counts.get(category, 0)
                    if len(rights) == expected_count:
                        self.log_test(f"Rights Count - {category.title()}", True, 
                                    f"Found {len(rights)} rights as expected")
                    else:
                        self.log_test(f"Rights Count - {category.title()}", False, 
                                    f"Expected {expected_count}, got {len(rights)}")
                    
                    # Check structure of rights
                    if rights:
                        first_right = rights[0]
                        required_fields = ["id", "title", "situation", "is_free"]
                        has_all_fields = all(field in first_right for field in required_fields)
                        
                        if has_all_fields:
                            self.log_test(f"Rights Structure - {category.title()}", True, 
                                        "Rights have correct structure")
                        else:
                            self.log_test(f"Rights Structure - {category.title()}", False, 
                                        "Rights missing required fields")
                else:
                    self.log_test(f"Rights API - {category.title()}", False, 
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"Rights API - {category.title()}", False, f"Error: {str(e)}")
    
    def test_specific_content(self):
        """Test specific content retrieval for sample entries"""
        test_cases = [
            # Traffic (free content)
            ("traffic", "traffic_pulled_over", True),
            ("traffic", "traffic_search_car", True),
            ("traffic", "traffic_dui_checkpoint", True),
            
            # Housing (paid content - should show preview)
            ("housing", "housing_eviction", False),
            ("housing", "housing_security_deposit", False),
            
            # Legal Landmines (paid content)
            ("landmines", "landmines_social_media", False),
            ("landmines", "landmines_neighbor_disputes", False),
            
            # Criminal Defense (paid content)
            ("criminal", "criminal_arrest_rights", False),
            ("criminal", "criminal_court_procedures", False),
            
            # Workplace (paid content)
            ("workplace", "workplace_harassment", False),
            ("workplace", "workplace_firing_layoffs", False),
            
            # Family (paid content)
            ("family", "family_divorce_separation", False),
            ("family", "family_child_custody", False)
        ]
        
        for category, right_id, is_free in test_cases:
            try:
                response = requests.get(f"{API_URL}/rights/{category}/{right_id}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    if is_free:
                        # Free content should have full content
                        if "content" in data and len(data["content"]) > 500:
                            self.log_test(f"Free Content - {right_id}", True, 
                                        "Full content available")
                        else:
                            self.log_test(f"Free Content - {right_id}", False, 
                                        "Content missing or too short")
                    else:
                        # Paid content should show preview
                        if "preview" in data and "requires_purchase" in data:
                            self.log_test(f"Paid Preview - {right_id}", True, 
                                        "Preview and purchase info shown")
                        else:
                            self.log_test(f"Paid Preview - {right_id}", False, 
                                        "Preview structure incorrect")
                elif response.status_code == 404:
                    self.log_test(f"Content - {right_id}", False, "Content not found")
                else:
                    self.log_test(f"Content - {right_id}", False, 
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"Content - {right_id}", False, f"Error: {str(e)}")
    
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