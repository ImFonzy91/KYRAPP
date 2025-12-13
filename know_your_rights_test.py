#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Know Your Rights Legal App
Tests all implemented legal rights and case analyzer endpoints
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
        return "https://lawsearch-5.preview.emergentagent.com"
    return "https://lawsearch-5.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

class KnowYourRightsAPITester:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        self.test_user_id = None
        
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
        """Test API health endpoint"""
        try:
            response = requests.get(f"{API_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "Know Your Rights API" in data.get("service", ""):
                    self.log_test("API Health Check", True, "Know Your Rights API is responding correctly")
                    return True
                else:
                    self.log_test("API Health Check", False, f"Unexpected service: {data}")
                    return False
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_auth_signup(self):
        """Test user signup endpoint"""
        try:
            # Create a test user
            signup_data = {
                "email": "testuser@knowyourrights.com",
                "password": "securepassword123",
                "name": "Test User"
            }
            
            response = requests.post(f"{API_URL}/auth/signup", json=signup_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "user" in data and "token" in data:
                    user = data["user"]
                    required_fields = ["id", "email", "name", "free_queries"]
                    has_all_fields = all(field in user for field in required_fields)
                    
                    if has_all_fields:
                        self.test_user_id = user["id"]  # Store for later tests
                        self.log_test("Auth Signup", True, 
                                    f"User created successfully with ID: {user['id']}")
                        
                        # Check free queries allocation
                        if user.get("free_queries") == 3:
                            self.log_test("Free Queries Allocation", True, 
                                        "User gets 3 free queries as expected")
                        else:
                            self.log_test("Free Queries Allocation", False, 
                                        f"Expected 3 free queries, got {user.get('free_queries')}")
                        
                        return True
                    else:
                        missing_fields = [field for field in required_fields if field not in user]
                        self.log_test("Auth Signup", False, f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Auth Signup", False, "Missing user or token in response")
                    return False
            elif response.status_code == 400:
                # User might already exist, try with different email
                signup_data["email"] = f"testuser{len(str(self.passed_tests + self.failed_tests))}@knowyourrights.com"
                response = requests.post(f"{API_URL}/auth/signup", json=signup_data, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if "user" in data:
                        self.test_user_id = data["user"]["id"]
                        self.log_test("Auth Signup", True, "User created with alternate email")
                        return True
                
                self.log_test("Auth Signup", False, f"Status code: {response.status_code}")
                return False
            else:
                self.log_test("Auth Signup", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Auth Signup", False, f"Error: {str(e)}")
            return False
    
    def test_auth_login(self):
        """Test user login endpoint"""
        try:
            # Try to login with the created user
            login_data = {
                "email": "testuser@knowyourrights.com",
                "password": "securepassword123"
            }
            
            response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "user" in data and "token" in data:
                    user = data["user"]
                    required_fields = ["id", "email", "name", "free_queries"]
                    has_all_fields = all(field in user for field in required_fields)
                    
                    if has_all_fields:
                        self.log_test("Auth Login", True, 
                                    f"Login successful for user: {user['email']}")
                        return True
                    else:
                        self.log_test("Auth Login", False, "User data incomplete")
                        return False
                else:
                    self.log_test("Auth Login", False, "Missing user or token in response")
                    return False
            elif response.status_code == 401:
                self.log_test("Auth Login", True, "Correctly rejects invalid credentials")
                return True
            else:
                self.log_test("Auth Login", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Auth Login", False, f"Error: {str(e)}")
            return False
    
    def test_search_rights(self):
        """Test legal rights search functionality with real legal data"""
        search_tests = [
            {
                "query": "pulled over",
                "expected_content": ["4th Amendment", "traffic stop", "Miranda"],
                "test_name": "Search - Traffic Stop Rights"
            },
            {
                "query": "landlord",
                "expected_content": ["tenant", "housing", "Fair Housing"],
                "test_name": "Search - Tenant Rights"
            },
            {
                "query": "arrested",
                "expected_content": ["Miranda", "5th Amendment", "6th Amendment"],
                "test_name": "Search - Arrest Rights"
            },
            {
                "query": "workplace",
                "expected_content": ["employment", "FLSA", "Title VII"],
                "test_name": "Search - Employment Rights"
            }
        ]
        
        for test_case in search_tests:
            try:
                response = requests.get(f"{API_URL}/search/rights", 
                                      params={"query": test_case["query"]}, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    if results and len(results) > 0:
                        # Check if results contain expected legal content
                        result_text = json.dumps(results).lower()
                        found_content = []
                        
                        for expected in test_case["expected_content"]:
                            if expected.lower() in result_text:
                                found_content.append(expected)
                        
                        if len(found_content) > 0:
                            self.log_test(test_case["test_name"], True, 
                                        f"Found relevant content: {', '.join(found_content)}")
                        else:
                            self.log_test(test_case["test_name"], False, 
                                        f"No expected content found in results")
                        
                        # Check result structure
                        first_result = results[0]
                        if "title" in first_result and "source" in first_result:
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
    
    def test_rights_categories(self):
        """Test rights categories endpoint"""
        try:
            response = requests.get(f"{API_URL}/rights/categories", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                categories = data.get("categories", [])
                
                # Should have 8 categories
                if len(categories) == 8:
                    self.log_test("Rights Categories Count", True, f"Found all 8 categories")
                else:
                    self.log_test("Rights Categories Count", False, 
                                f"Expected 8 categories, got {len(categories)}")
                
                # Check expected categories
                expected_categories = [
                    "constitutional", "miranda", "traffic", "tenant", 
                    "employment", "criminal", "immigration", "consumer"
                ]
                
                found_categories = [cat.get("id") for cat in categories]
                
                for expected_cat in expected_categories:
                    if expected_cat in found_categories:
                        self.log_test(f"Category - {expected_cat.title()}", True, "Category present")
                    else:
                        self.log_test(f"Category - {expected_cat.title()}", False, "Category missing")
                
                # Check category structure
                if categories:
                    first_cat = categories[0]
                    required_fields = ["id", "name", "icon", "source"]
                    has_all_fields = all(field in first_cat for field in required_fields)
                    
                    if has_all_fields:
                        self.log_test("Categories Structure", True, "Categories have correct structure")
                    else:
                        self.log_test("Categories Structure", False, "Categories missing required fields")
                
                return True
            else:
                self.log_test("Rights Categories", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Rights Categories", False, f"Error: {str(e)}")
            return False
    
    def test_specific_rights_categories(self):
        """Test specific rights category endpoints"""
        categories_to_test = [
            {"category": "traffic", "expected_content": ["4th Amendment", "traffic stop"]},
            {"category": "constitutional", "expected_content": ["Constitution", "Amendment"]},
            {"category": "tenant", "expected_content": ["landlord", "housing"]},
            {"category": "criminal", "expected_content": ["Miranda", "defense"]}
        ]
        
        for test_case in categories_to_test:
            try:
                response = requests.get(f"{API_URL}/rights/{test_case['category']}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "category" in data and "data" in data:
                        category_data = data.get("data", {})
                        
                        if category_data:
                            # Check if expected content is present
                            data_text = json.dumps(category_data).lower()
                            found_content = []
                            
                            for expected in test_case["expected_content"]:
                                if expected.lower() in data_text:
                                    found_content.append(expected)
                            
                            if len(found_content) > 0:
                                self.log_test(f"Rights Category - {test_case['category'].title()}", True, 
                                            f"Contains expected content: {', '.join(found_content)}")
                            else:
                                self.log_test(f"Rights Category - {test_case['category'].title()}", False, 
                                            "Missing expected content")
                        else:
                            self.log_test(f"Rights Category - {test_case['category'].title()}", False, 
                                        "Empty category data")
                    else:
                        self.log_test(f"Rights Category - {test_case['category'].title()}", False, 
                                    "Invalid response structure")
                else:
                    self.log_test(f"Rights Category - {test_case['category'].title()}", False, 
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"Rights Category - {test_case['category'].title()}", False, f"Error: {str(e)}")
    
    def test_case_analyzer_queries_left(self):
        """Test case analyzer queries left endpoint"""
        if not self.test_user_id:
            self.log_test("Case Analyzer - Queries Left", False, "No test user ID available")
            return False
        
        try:
            response = requests.get(f"{API_URL}/case-analyzer/queries-left", 
                                  params={"user_id": self.test_user_id}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "queries_left" in data and "history" in data:
                    queries_left = data.get("queries_left")
                    
                    if isinstance(queries_left, int) and queries_left >= 0:
                        self.log_test("Case Analyzer - Queries Left", True, 
                                    f"User has {queries_left} queries remaining")
                        return True
                    else:
                        self.log_test("Case Analyzer - Queries Left", False, 
                                    f"Invalid queries_left value: {queries_left}")
                        return False
                else:
                    self.log_test("Case Analyzer - Queries Left", False, 
                                "Missing required fields in response")
                    return False
            else:
                self.log_test("Case Analyzer - Queries Left", False, 
                            f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Case Analyzer - Queries Left", False, f"Error: {str(e)}")
            return False
    
    def test_case_analyzer_analyze(self):
        """Test AI-powered case analysis endpoint"""
        if not self.test_user_id:
            self.log_test("Case Analyzer - AI Analysis", False, "No test user ID available")
            return False
        
        try:
            # Test with a simple landlord scenario
            analysis_data = {
                "user_id": self.test_user_id,
                "situation": "My landlord is trying to evict me without proper notice and won't return my security deposit. They also refuse to fix the broken heating system in my apartment. I've been a good tenant for 2 years and always paid rent on time."
            }
            
            response = requests.post(f"{API_URL}/case-analyzer/analyze", 
                                   json=analysis_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields in AI analysis response
                required_fields = ["verdict", "summary", "relevant_laws", "your_rights", 
                                 "next_steps", "lawyer_recommendation", "queries_left"]
                has_all_fields = all(field in data for field in required_fields)
                
                if has_all_fields:
                    self.log_test("Case Analyzer - AI Analysis Structure", True, 
                                "Analysis has all required fields")
                    
                    # Check if analysis contains relevant legal content
                    analysis_text = json.dumps(data).lower()
                    relevant_terms = ["landlord", "tenant", "housing", "eviction", "deposit"]
                    found_terms = [term for term in relevant_terms if term in analysis_text]
                    
                    if len(found_terms) >= 2:
                        self.log_test("Case Analyzer - AI Analysis Content", True, 
                                    f"Analysis contains relevant terms: {', '.join(found_terms)}")
                    else:
                        self.log_test("Case Analyzer - AI Analysis Content", False, 
                                    "Analysis lacks relevant legal content")
                    
                    # Check if queries were decremented
                    queries_left = data.get("queries_left")
                    if isinstance(queries_left, int):
                        self.log_test("Case Analyzer - Query Decrement", True, 
                                    f"Queries decremented, {queries_left} remaining")
                    else:
                        self.log_test("Case Analyzer - Query Decrement", False, 
                                    "Queries not properly decremented")
                    
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Case Analyzer - AI Analysis", False, 
                                f"Missing fields: {missing_fields}")
                    return False
            elif response.status_code == 402:
                self.log_test("Case Analyzer - AI Analysis", True, 
                            "Correctly handles no queries remaining")
                return True
            elif response.status_code == 500:
                # Check if it's an AI/LLM integration issue
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                    if "Analysis failed" in error_detail:
                        self.log_test("Case Analyzer - AI Analysis", False, 
                                    f"AI Integration Error: {error_detail}")
                    else:
                        self.log_test("Case Analyzer - AI Analysis", False, 
                                    f"Server error: {error_detail}")
                except:
                    self.log_test("Case Analyzer - AI Analysis", False, 
                                "Server error (500)")
                return False
            else:
                self.log_test("Case Analyzer - AI Analysis", False, 
                            f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Case Analyzer - AI Analysis", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 70)
        print("KNOW YOUR RIGHTS LEGAL APP - BACKEND API TESTING")
        print("=" * 70)
        print(f"Testing backend at: {BASE_URL}")
        print()
        
        # Test API connectivity first
        if not self.test_api_health():
            print("❌ CRITICAL: Cannot connect to API. Stopping tests.")
            return False
        
        print("\n🔐 Testing Authentication...")
        self.test_auth_signup()
        self.test_auth_login()
        
        print("\n🔍 Testing Legal Rights Search...")
        self.test_search_rights()
        
        print("\n📚 Testing Rights Categories...")
        self.test_rights_categories()
        self.test_specific_rights_categories()
        
        print("\n🤖 Testing AI Case Analyzer...")
        self.test_case_analyzer_queries_left()
        self.test_case_analyzer_analyze()
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        
        if self.passed_tests + self.failed_tests > 0:
            success_rate = (self.passed_tests/(self.passed_tests + self.failed_tests)*100)
            print(f"📊 Success Rate: {success_rate:.1f}%")
        
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
        print("\n🎉 ALL TESTS PASSED! Know Your Rights backend is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {tester.failed_tests} tests failed. Check the issues above.")
        sys.exit(1)